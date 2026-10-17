"""Persistent research workflow using observable provider CLI executions (Codex, Claude).

The persisted contract is ``state_contract.STATE_CONTRACT_ID``. Mathematical,
semantic, goal, authority and execution judgments remain distinct. Session
boundaries are instructions and do not claim OS isolation.
"""
from __future__ import annotations

from copy import deepcopy
from functools import cached_property, partial
from pathlib import Path
from typing import Any
from .contracts import all_prompt_documents
from .formal import verify_lean
from .operation_trace import engine_operation, tracing
from .review_engine import ReviewEngineMixin
from .lifecycle_engine import LifecycleEngineMixin
from .initialization_engine import InitializationEngineMixin
from .knowledge_engine import KnowledgeEngineMixin
from .external_engine import ExternalEngineMixin
from .formal_engine import FormalEngineMixin
from .planning_engine import PlanningEngineMixin
from .academic_engine import AcademicEngineMixin
from .governance_engine import GovernanceEngineMixin
from .repair_execution import RepairExecutionMixin
from .model_runner import ModelRunner
from .repository import ResearchRepository
from .scheduler import SchedulerMixin
from .dispatch_engine import DispatchEngineMixin
from .provider_engine import ProviderEngineMixin
from .decision_engine import DecisionEngineMixin
from .revision_engine import RevisionEngineMixin
from .question_engine import QuestionEngineMixin
from . import execution_window
from .control_transport import ControlTransport
from .call_engine import CallEngineMixin
from .core_engine import (CoreEngineMixin, _query_record, _record_evidence, initialize_instance, query_records, read_record, submit_control)


def initialize(repository: Path, *, goal: str, workspace: Path, config: dict | None = None,
               title: str = "",
               instance_id: str | None = None, sources: list[Path] | None = None,
               source_input: str | None = None, ports, codex_home, host_id) -> dict:
    """Create a research instance: the public entry point chooses the ports, the working directory and tracing.

    """
    return initialize_instance(repository, goal=goal, workspace=workspace, config=config, title=title,
                               instance_id=instance_id, sources=sources, source_input=source_input,
                               clock=ports.clock, cwd=Path.cwd, trace=tracing, host=ports.host,
                               git_backend=ports.git_backend, codex_home=codex_home, host_id=host_id)


def control(repository: Path, instance_id: str, action: str, *, text: str = "", config: dict | None = None,
            origin: str = "user", request_id: str | None = None, idempotency_key: str | None = None,
            ports, host_id) -> dict:
    """Queue user commands; only the owning engine publishes authority changes.

    """
    return submit_control(repository, instance_id, action, text=text, config=config, origin=origin,
                          request_id=request_id, idempotency_key=idempotency_key, clock=ports.clock,
                          lean_available=lambda: ports.host.discover_lean() is not None,
                          git_backend=ports.git_backend, host_id=host_id)


class ResearchEngine(CallEngineMixin, CoreEngineMixin, QuestionEngineMixin, RevisionEngineMixin, DecisionEngineMixin, ProviderEngineMixin, DispatchEngineMixin, SchedulerMixin, PlanningEngineMixin, ReviewEngineMixin, LifecycleEngineMixin, InitializationEngineMixin, KnowledgeEngineMixin, ExternalEngineMixin, FormalEngineMixin, AcademicEngineMixin, GovernanceEngineMixin, RepairExecutionMixin):
    def __init__(self, repository: Path, instance_id: str, *, ports, installation_root: Path | None = None, codex_home, environment, host_id):
        self.ports = ports
        self.host_id, self.environment, self.codex_home = host_id, environment, codex_home
        # This selects installation files, not a different edition of loaded Python code.
        self.installation_root = (Path(installation_root) if installation_root is not None
                                  else Path(__file__).resolve().parents[2]).resolve()
        self.store = ResearchRepository(repository, instance_id, backend=ports.git_backend, clock=ports.clock)
        self.runner = ModelRunner(jobs=ports.jobs, clock=ports.clock, environment=environment, host_id=host_id)
        self.formal_verifier = partial(verify_lean, jobs=ports.jobs, clock=ports.clock, environment=environment, git_backend=ports.git_backend)
        self.head, self.instance, self.runtime = self.store.load()
        self._init_process_state(
            transport=ControlTransport(Path(self.instance["workspace"]) / "execution-control" / instance_id,
                                       clock=ports.clock))

    def _init_process_state(self, *, transport=None):
        """Process-local owner state that no repository holds.

        Called by the constructor after the installation and store are set.
        """
        self._task_readiness = {}
        self._live_execution_ids = set()
        self._executor_running = False
        self._calls = None
        self._next_installation_check = 0.0
        self._preparing_input = False
        self._transport = transport
        self._transport_bindings = {}
        self._trackers = {}
        self._stop_deadlines, self._stop_clock = {}, None
        self._clock_anchor = None
        self._clock_failure = None  # a retained clock regression (LifecycleEngineMixin._clock_guard)
        self._feedback_delivered = set()  # control receipts whose worker feedback this process delivered
        self._retrying_publication = False
        self._next_lean_discovery, self._lean_found = 0.0, False
        self._goal_audit_contract = None  # hash of the goal audit input contract of the loaded role documents
        self._goal_basis_memo = None  # (head, goal basis key) of the stop judgments
        self._scan_head, self._scan_at = None, 0.0  # head and time of the owner's last readiness/dispatch judgment

    @cached_property
    def _documents(self):
        """Role documents, read once by the first command that renders a prompt."""
        return all_prompt_documents(skill_root=self.installation_root)

    @cached_property
    def _installation(self):
        """The installed edition this engine loaded, hashed on first use by ``run``."""
        return self._installation_manifest()

    def _record_installation_startup(self, manifest_path):
        """Record full installation provenance separately from the polling edition."""
        import operator_bootstrap as bootstrap
        from .repair_execution import installation_evidence
        from .canonical import canonical_json
        from .file_io import write_bytes_atomic
        manifest = bootstrap.verify_snapshot(Path(manifest_path)) if manifest_path is not None else None
        if manifest is not None and Path(manifest['installation_root']).resolve() != self.installation_root.resolve():
            raise ValueError('startup manifest identifies a different installation root')
        startup = {'bootstrap': bootstrap.startup_evidence(manifest),
                   'manifest_path': str(Path(manifest_path).resolve()) if manifest_path is not None else None,
                   'installation': installation_evidence(self.installation_root, backend=self.ports.git_backend),
                   'runtime_root': str(Path(__file__).resolve().parents[2]),
                   'polling_edition': self._installation,
                   'observed_at': self.ports.clock.now()}
        write_bytes_atomic(Path(self.instance['workspace']) / 'execution-control' / self.instance['id'] / 'startup.json',
                           canonical_json(startup))
        return startup

    def _controls(self) -> None:
        """One owner pass over controls: apply the inbox, then the periodic upkeep."""
        self._apply_inbox()
        self._upkeep()

    @engine_operation('controls')
    def process_controls(self) -> None:
        """Apply queued user controls under the sole writer lock, without AI."""
        with self.store.writer_lock():
            self._reload()
            self._inspect_before_write()
            self._apply_inbox()
            # Only an executor can recover predecessors before judging a live due target.
            self._upkeep(schedule_reviews=False)
            self._save()
    @engine_operation('run')
    def run(self, *, max_steps: int | None = None, watch: bool = False, until_active: bool = False,
            installation_manifest: Path | None = None) -> dict:
        # A host resource change is valid only while no executor loop can dispatch.
        self._executor_running = True
        try:
            return self._run_executor(max_steps=max_steps, watch=watch, until_active=until_active,
                                      installation_manifest=installation_manifest)
        finally:
            self._executor_running = False

    def _run_executor(self, *, max_steps: int | None = None, watch: bool = False, until_active: bool = False,
                      installation_manifest: Path | None = None) -> dict:
        if max_steps is not None and max_steps < 1:
            raise ValueError("max_steps must be positive")
        with self.store.writer_lock():
            self._reload()
            self._inspect_before_write()
            self._installation  # the edition later checks compare against, fixed at run start
            startup = self._record_installation_startup(installation_manifest)
            if startup['bootstrap']['comparison'] in {'different', 'unavailable'}:
                if not self._instance_closed():
                    self._pause_lifecycle('installation_startup_mismatch')
                self._save()
                return {**self.status(), 'startup': startup}
            self._apply_inbox()
            self._recover_disappeared()
            # A predecessor's running row is not a live target of this owner.
            self._upkeep()
            if not self._prepare_executor_pass():
                return {**self.status(), 'startup': startup}
            self._run_parallel(max_steps=max_steps, watch=watch, until_active=until_active)
        return {**self.status(), 'startup': startup}

    def _call_steps(self, action: dict):
        """Prepare and run one AI action as a generator that yields the runner arguments.

        The scheduler starts it in the same owner pass in which ``_dispatchable``
        passed the action's lifecycle gate; that gate is its last before start.
        The generator only wires the runner, clock and tracker: ``_prepare_call``
        judges and prepares, ``_call_started`` and ``_call_stop_requested`` answer
        the runner's callbacks, and ``_receive_call`` handles the returned result.
        """
        prepared = self._prepare_call(action)
        if not isinstance(prepared, dict):
            return prepared
        base = prepared['base']
        binding = prepared['binding']
        call_deadline = prepared['call_deadline']
        config = prepared['config']
        execution = prepared['execution']
        execution_id = prepared['execution_id']
        fitted = prepared['fitted']
        profile = prepared['profile']
        prompt = prepared['prompt']
        schema = prepared['schema']
        tracker = prepared['tracker']
        workspace = prepared['workspace']
        def started(identity):
            self._call_started(prepared, identity)
        def should_stop():
            return self._call_stop_requested(prepared)
        arguments = dict(prompt=prompt, output_schema=schema, workspace=workspace, evidence_dir=base/"evidence",
                         model=execution["model"], effort=execution["effort"],
                         execution_id=execution_id, profile=profile,
                         launch_ticket=deepcopy(execution['launch_ticket']),
                         control_binding=binding,
                         input_seal=deepcopy(fitted["manifest"]["prompt"]),
                         timeout_seconds=None if call_deadline is None else max(.1, call_deadline-self.ports.clock.monotonic()),
                         should_stop=should_stop, on_started=started,
                         on_observation=lambda event: self._observe_running(execution_id, tracker, event))
        deadlines = self._stop_deadlines
        if call_deadline is not None:
            # The owner loop compares these instants with the clock; the judgment runs when one passes.
            deadlines[execution_id] = (call_deadline - execution_window.notice_seconds(config), call_deadline)
        result = yield arguments
        deadlines.pop(execution_id, None)
        return self._receive_call(prepared, result)
