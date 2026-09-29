"""Model-free supervision and engine-exclusive installation recovery.

Normal supervision keeps local evidence; failure-only repair uses the same Git
execution/reservation families while holding the repository writer lock.
"""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Any, Callable
import uuid
from copy import deepcopy

from .file_io import now
from .repository import ResearchRepository
from .model_runner import ModelRunner
from .model_policy import selection
from .provider_wait import epoch_seconds
from .session_slots import PROVIDER_WAIT
from .operation_trace import workspace_operation, child_environment


SCRIPTS = Path(__file__).resolve().parents[1]
SKILL_ROOT = SCRIPTS.parent
# Frozen bootstrap overrides this after importing the verified supervisor.
LIVE_INSTALLATION_ROOT = SKILL_ROOT
# The adapter finds operator_bootstrap.py beside itself. Its ValidateSet is the one
# action list: an unsupported action fails there and ``schedule`` raises its error.
SCHEDULE_SCRIPT = SCRIPTS / "operator_schedule.ps1"
# Supervision blockers in priority order; the first present one decides.
# ``held`` is the local HOLD file and ``disabled`` the operator setting.
SUPERVISION_BLOCKS = ('held', 'disabled', 'user_pause', 'maintenance', 'model_policy',
                      'paused', 'closed', 'completed', 'conversation_lost', 'installation_repair')

Runner = Callable[..., subprocess.CompletedProcess[str]]
OPERATOR_SCHEMA = {
    "type": "object", "additionalProperties": False,
    "properties": {
        "summary": {"type": "string"}, "observed_status": {"type": "string"},
        "actions": {"type": "array", "items": {"type": "string"}},
        "evidence_paths": {"type": "array", "items": {"type": "string"}},
        "user_questions": {"type": "array", "items": {"type": "string"}},
        "next_step": {"type": "string"},
    },
    "required": ["summary", "observed_status", "actions", "evidence_paths", "user_questions", "next_step"],
}


def repair_report_schema(*, diagnosed=False):
    """The CLI output schema of a repair run, in OPERATOR_SCHEMA's keywords only.

    No preserved run shows a provider accepting other keywords here. The prompt
    names the allowed values; collect_repair_verification judges them on receipt.
    """
    schema = deepcopy(OPERATOR_SCHEMA)
    if diagnosed:
        schema['properties'].update(repair_outcome={'type':'string'},
            verification_evidence={'type':'array','items':{'type':'string'}})
        schema['required'].extend(['repair_outcome','verification_evidence'])
    return schema


def collect_repair_verification(output, workspace):
    """Preserve actual regression evidence; a completed model call is insufficient."""
    if not output or output.get('repair_outcome') != 'repaired' or not output.get('verification_evidence'):
        raise ValueError('diagnosed repair requires repaired outcome and regression evidence files')
    rows = []
    workspace = Path(workspace).resolve()
    for name in output['verification_evidence']:
        path = (workspace / name).resolve()
        if not path.is_relative_to(workspace) or not path.is_file():
            raise ValueError('repair verification evidence must be a real file in its workspace')
        raw = path.read_bytes()
        if not raw:
            raise ValueError('repair verification evidence is empty')
        rows.append({'path': path.relative_to(workspace).as_posix(), 'sha256': hashlib.sha256(raw).hexdigest(),
                     'bytes': len(raw)})
    return rows


def _json(path: Path, value: dict[str, Any]) -> None:
    from .file_io import write_bytes_atomic
    from .values import bytes_evidence
    def evidence_default(item):
        if isinstance(item, bytes):
            return bytes_evidence(item)
        if isinstance(item, Path):
            return str(item)
        raise TypeError("unsupported supervisor evidence: " + type(item).__name__)
    write_bytes_atomic(path,(json.dumps(value,default=evidence_default,allow_nan=False,
                                        ensure_ascii=False,indent=2)+'\n').encode('utf-8'))


def _load_json(path: Path) -> dict[str, Any] | None:
    from .file_io import read_bytes_shared
    if not path.is_file():
        return None
    value = json.loads(read_bytes_shared(path).decode('utf-8'))
    return value if isinstance(value, dict) else None


def task_names(repository: Path, instance: str) -> dict[str, str]:
    """Return stable task names scoped to the exact repository and instance."""
    digest = hashlib.sha256((str(repository.resolve()) + "\0" + instance).encode("utf-8")).hexdigest()[:12]
    return {"operator": f"DoMath-Operator-{digest}", "engine": f"DoMath-Engine-{digest}", "wake": f"DoMath-Wake-{digest}"}


def schedule(
    action: str,
    *,
    repository: Path,
    instance: str,
    workspace: Path,
    interval_seconds: int | None = None,
    operator_timeout_seconds: int | None = None,
    wake_at: str | None = None,
    wake_key: str | None = None,
    runner: Runner = subprocess.run,
    scheduler=None,
) -> dict[str, Any]:
    """Call the narrow PowerShell scheduler adapter and decode its JSON result.

    Only ``install`` uses the configured interval and operator timeout;
    configuration validation already checked their ranges.
    """
    if action == "install" and (interval_seconds is None or operator_timeout_seconds is None):
        raise ValueError("install requires the configured operator interval and timeout")
    names = task_names(repository, instance)
    pythonw = Path(sys.executable).with_name("pythonw.exe")
    executable = str(pythonw) if pythonw.is_file() else sys.executable
    arguments = {"Repository": str(repository.resolve()), "Instance": instance, "Workspace": str(workspace.resolve()),
                 "Python": executable, "OperatorTask": names["operator"], "EngineTask": names["engine"],
                 "WakeTask": names["wake"]}
    if action == "install":
        arguments.update(IntervalSeconds=str(interval_seconds), OperatorTimeoutSeconds=str(operator_timeout_seconds))
    if action == "schedule-wake":
        if epoch_seconds(wake_at) is None or not wake_key:
            raise ValueError("wake requires a timezone-aware retry time and generation key")
        arguments.update(WakeAt=wake_at, WakeKey=wake_key)
    return (scheduler or PowerShellScheduler(runner)).run(action, arguments)


class PowerShellScheduler:
    """Real scheduler port: the PowerShell adapter ``operator_schedule.ps1``."""

    def __init__(self, runner: Runner = subprocess.run):
        self.runner = runner

    def run(self, action: str, arguments: dict) -> dict:
        powershell = shutil.which("powershell.exe") or shutil.which("powershell") or "powershell.exe"
        command = [powershell, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(SCHEDULE_SCRIPT),
                   "-Action", action]
        for name, value in arguments.items():
            command.extend(["-" + name, value])
        completed = self.runner(command, capture_output=True, text=True, encoding="utf-8", check=False,
                                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        if completed.returncode:
            raise RuntimeError(completed.stderr.strip() or completed.stdout.strip() or "scheduled-task operation failed")
        try:
            value = json.loads(completed.stdout)
        except json.JSONDecodeError as error:
            raise RuntimeError("scheduled-task adapter returned invalid JSON") from error
        if not isinstance(value, dict):
            raise RuntimeError("scheduled-task adapter result must be an object")
        return value


def cancel_wake(repository: Path, instance: str, workspace: Path) -> dict[str, Any]:
    """Remove the one-shot wake task and its local registration marker."""
    result = schedule("cancel-wake", repository=repository, instance=instance, workspace=workspace)
    (_operator_dir(workspace) / "wake-registration.json").unlink(missing_ok=True)
    return result


def hold_pause_reason(hold_id: str) -> str:
    """The user pause a HOLD requests; its release resumes only this exact pause."""
    return "User requested scheduled operator HOLD " + hold_id


def supervision_facts(instance: dict, runtime: dict) -> dict[str, Any]:
    """The persisted facts that decide whether supervision may start research or repair."""
    from .repair_execution import pending_installation_repair
    return {'status': runtime.get('status'), 'user_pause': deepcopy(runtime.get('user_pause')),
            'maintenance_fence': deepcopy(runtime.get('maintenance_fence')),
            'model_policy_violation': deepcopy(runtime.get('model_policy_violation')),
            'conversation_lost': (runtime.get('stop_requested') == 'conversation_lost'
                                  and instance.get('conversation_loss_policy') == 'pause'),
            'installation_repair': deepcopy(pending_installation_repair(runtime)),
            'operator_enabled': instance.get('config', {}).get('operator_enabled') is True}


def supervision_block(facts: dict[str, Any]) -> str | None:
    """The first supervision blocker present in ``facts``, or None.

    Facts without ``held`` or ``operator_enabled`` never report those blockers;
    a persisted-state view or an explicit engine start omits them.
    """
    present = {'held': facts.get('held'),
               'disabled': 'operator_enabled' in facts and not facts['operator_enabled'],
               'user_pause': facts.get('user_pause'), 'maintenance': facts.get('maintenance_fence'),
               'model_policy': facts.get('model_policy_violation'),
               'conversation_lost': facts.get('conversation_lost'),
               'installation_repair': facts.get('installation_repair'),
               **{state: facts.get('status') == state for state in ('paused', 'closed', 'completed')}}
    return next((code for code in SUPERVISION_BLOCKS if present[code]), None)


def _held(workspace: Path) -> bool:
    return (_operator_dir(workspace) / "HOLD.json").exists()


def resolve_workspace(repository: Path, instance: str) -> Path:
    _, state, _ = ResearchRepository(repository, instance).load()
    workspace = state.get("workspace")
    if not isinstance(workspace, str) or not workspace:
        raise ValueError("instance does not have a workspace")
    return Path(workspace).resolve()


def read_status(repository: Path, instance: str) -> dict[str, Any]:
    from .engine import ResearchEngine
    return ResearchEngine(repository, instance).status()


def _operator_dir(workspace: Path) -> Path:
    return workspace / "operator"


def hold(workspace: Path, *, reason: str) -> dict[str, Any]:
    """Set a local hold marker; intentionally does not send pause or resume."""
    value = {"id": uuid.uuid4().hex, "reason": reason, "started_at": now()}
    _json(_operator_dir(workspace) / "HOLD.json", value)
    return value


def release(workspace: Path) -> dict[str, Any]:
    """Release only this operator marker; research remains paused until resumed."""
    path = _operator_dir(workspace) / "HOLD.json"
    held = _load_json(path)
    if held is None:
        return {"released": None}
    path.unlink()
    result = {"released": held, "released_at": now()}
    _json(_operator_dir(workspace) / "release.json", result)
    return result


@workspace_operation('engine_launch')
def run_engine(repository: Path, instance: str, workspace: Path) -> dict[str, Any]:
    try:
        guard = engine_start_guard(repository, instance, workspace)
    except Exception as error:
        record = {"outcome": "engine_failed", "kind": "engine_unavailable",
                  "error_type": type(error).__name__, "error": str(error)}
        _json(_operator_dir(workspace) / "latest-engine.json", record)
        return record
    if guard["outcome"] != "startable":
        return guard
    status = guard["before"]
    run_directory = _operator_dir(workspace) / "engine" / (datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:8])
    run_directory.mkdir(parents=True)
    _json(run_directory / "before.json", status)
    command = [sys.executable, str(Path(LIVE_INSTALLATION_ROOT) / "scripts/do_math.py"),
               "run", "--repository", str(repository), "--instance", instance, "--watch"]
    record = {"outcome": "running", "before": status, "command": command, "run_directory": str(run_directory)}
    _json(run_directory / "result.json", record)
    try:
        completed = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", check=False,
            env=child_environment(), creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        (run_directory / "stdout.json").write_text(completed.stdout, encoding="utf-8")
        (run_directory / "stderr.txt").write_text(completed.stderr, encoding="utf-8")
        busy = completed.returncode != 0 and _retryable_tool_error(completed.stdout)
        record.update(outcome="completed" if completed.returncode == 0 else "engine_busy" if busy else "engine_failed",
                      exit_code=completed.returncode)
        record["after"] = read_status(repository, instance)
        if supervision_block({**record['after'], 'held': _held(workspace)}) == 'installation_repair':
            try:
                record['supervisor_request']=schedule('start-operator',repository=repository,
                    instance=instance,workspace=workspace)
            except (RuntimeError,OSError) as error:
                record['supervisor_request']={'status':'failed','error':str(error),
                    'next_owner':'scheduled_operator','fallback':'periodic supervision'}
    except Exception as error:
        record.update(outcome="engine_failed", error=f"{type(error).__name__}: {error}")
    _json(run_directory / "result.json", record)
    _json(_operator_dir(workspace) / "latest-engine.json", record)
    return record


def _retryable_tool_error(stdout: str) -> bool:
    """A busy writer lock or lost CAS is contention, not an installation failure."""
    try:
        envelope = json.loads(stdout)
    except json.JSONDecodeError:
        return False
    error = envelope.get("error") if isinstance(envelope, dict) else None
    return isinstance(error, dict) and error.get("kind") == "tool_error" and error.get("retryable") is True


def engine_start_guard(repository: Path, instance: str, workspace: Path, *, status=None) -> dict[str, Any]:
    """Read the conditions that must hold before either task starts an engine.

    An explicit engine start does not depend on automatic supervision being enabled.
    """
    if _held(workspace):
        return {"outcome": "held"}
    if status is None:
        status = read_status(repository, instance)
    block = supervision_block({key: value for key, value in status.items() if key != 'operator_enabled'})
    if block == 'maintenance':
        return {'outcome':'maintenance_waiting', 'before':status}
    if block == 'model_policy':
        return {"outcome": "model_policy_waiting", "before": status}
    if block in {'user_pause', 'paused'}:
        return {"outcome": "paused", "before": status}
    if block in {'closed', 'completed'}:
        return {"outcome": "not_started", "before": status}
    if block == 'conversation_lost':
        return {'outcome': 'user_paused', 'before': status}
    if block == 'installation_repair':
        return {'outcome': 'installation_repair_waiting', 'before': status}
    providers = status.get("provider_waits", {}).get("providers", {})
    # A queued request waits on a provider whose gate is open again.
    provider_open = any(row['wait'].get('kind') == PROVIDER_WAIT
                        and providers.get(row['wait'].get('provider'), {}).get('open')
                        for row in status.get("dispatch_waits", []))
    if status.get("status") == "waiting" and provider_open:
        return {"outcome": "startable", "before": status, "reason": "provider re-observation due"}
    if status.get("status") == "waiting" and status.get("research_wake_reasons"):
        return {"outcome": "startable", "before": status, "reason": "research reconsideration due",
                "research_wake_reasons": status["research_wake_reasons"]}
    if status.get("status") not in {"ready", "running", "capacity_waiting"}:
        return {"outcome": "not_started", "before": status}
    return {"outcome": "startable", "before": status}


def reconcile_wake(repository: Path, instance: str, workspace: Path, *, facts: dict, providers: dict,
                   scheduler=None) -> dict:
    """Repair a missing/stale one-shot reservation before invoking any model.

    ``facts`` are the caller's supervision facts and ``providers`` its provider
    snapshot, both from the state it already holds. A queried task status is
    returned as ``observed`` so the caller need not query it again.
    """
    marker = _operator_dir(workspace) / "wake-registration.json"
    previous = _load_json(marker)
    block = supervision_block({**facts, 'held': _held(workspace)})
    held = block not in {None, 'disabled', 'installation_repair'}
    waits = [row for row in providers.values() if row["state"] == "waiting"]
    if held or block == 'disabled' or not waits:
        if previous:
            cancel_wake(repository, instance, workspace)
        return {"status": "held" if held else "not_needed"}
    row = min(waits, key=lambda value: epoch_seconds(value["retry_at"]))
    key = row["provider"] + ":" + str(row["generation"])
    wanted = {"key": key, "retry_at": row["retry_at"]}
    observed = schedule("status", repository=repository, instance=instance, workspace=workspace, scheduler=scheduler)
    actual = observed.get("wake")
    future_trigger = actual and (epoch_seconds(actual.get("next_run")) or 0) > datetime.now(timezone.utc).timestamp()
    running = (observed.get("engine") or {}).get("state") == "Running" or (actual or {}).get("state") == "Running"
    if previous == wanted and actual and actual.get("description") == key and (future_trigger or running):
        return {"status": "scheduled", **wanted, "observed": observed}
    schedule("schedule-wake", repository=repository, instance=instance, workspace=workspace, scheduler=scheduler,
             wake_at=row["retry_at"], wake_key=key)
    _json(marker, wanted)
    return {"status": "scheduled", **wanted, "observed": observed}


def wake(repository: Path, instance: str, workspace: Path) -> dict:
    """No model ping: wake only the engine entry point with its usual guards."""
    guard = engine_start_guard(repository, instance, workspace)
    if guard["outcome"] != "startable":
        return guard
    scheduled = schedule("start-engine", repository=repository, instance=instance, workspace=workspace)
    return {"outcome": "engine_requested", "schedule": scheduled, "before": guard["before"]}


def check(repository: Path, instance: str, workspace: Path, *, probe: bool = False) -> dict[str, Any]:
    """Model-free supervision; preserved engine failure or accepted defect diagnosis opens recovery.

    Every judgment reads the one status snapshot; recovery rereads under its lock.
    """
    if _held(workspace):
        return {"outcome": "held"}
    try:
        status = read_status(repository, instance)
    except Exception as error:
        failure = {"outcome": "recovery_required", "kind": "engine_unavailable",
                   "error_type": type(error).__name__, "error": str(error),
                   "observed_at": now()}
        _json(_operator_dir(workspace) / "engine-failure.json", failure)
        if probe:
            return failure
        return recovery(repository, instance, workspace, failure=failure)
    block = supervision_block(status)
    if block == 'disabled':
        return {"outcome": "disabled"}
    if block in {'user_pause', 'paused', 'closed', 'completed'}:
        return {"outcome": status.get("status", "paused"), "status": status}
    if block == 'maintenance':
        return {"outcome": "maintenance_waiting", "status": status, "model_called": False}
    if block == 'model_policy':
        return {"outcome": "model_policy_waiting", "status": status}
    if block == 'conversation_lost':
        return {"outcome": "user_paused", "status": status}
    if block == 'installation_repair':
        if probe:
            from .repair_execution import installation_failure
            _, _, runtime = ResearchRepository(repository, instance).load(status["snapshot"])
            return {'outcome': 'installation_repair_pending', 'model_called': False,
                    'failure': installation_failure(runtime, status['installation_repair'])}
        return recovery(repository, instance, workspace)
    if probe:
        return {"outcome": "observed", "status": status, "model_called": False,
                "engine_start": engine_start_guard(repository, instance, workspace, status=status)}
    engine_failure = _load_json(_operator_dir(workspace) / "latest-engine.json")
    if engine_failure and engine_failure.get("outcome") == "engine_failed":
        return recovery(repository, instance, workspace, failure={
            "kind": "engine_unavailable", "error": engine_failure.get("error") or
                "engine process failed with exit code " + str(engine_failure.get("exit_code")),
            "evidence_path": str(_operator_dir(workspace) / "latest-engine.json"),
            "engine_run_directory": engine_failure.get("run_directory")})
    wake_status = reconcile_wake(repository, instance, workspace, facts=status,
                                 providers=status["provider_waits"]["providers"])
    observed = wake_status.pop("observed", None)
    guard = engine_start_guard(repository, instance, workspace, status=status)
    if guard["outcome"] != "startable":
        return {**guard, "provider_wake": wake_status, "model_called": False}
    if observed is None:
        observed = schedule("status", repository=repository, instance=instance, workspace=workspace)
    if (observed.get("engine") or {}).get("state") == "Running":
        return {"outcome": "engine_running", "model_called": False}
    started = schedule("start-engine", repository=repository, instance=instance, workspace=workspace)
    return {"outcome": "engine_requested", "schedule": started, "provider_wake": wake_status, "model_called": False}


def recovery(repository: Path, instance: str, workspace: Path, *, failure: dict | None = None) -> dict:
    """Failure-only installation repair under the engine's writer lock.

    Without ``failure``, repair the pending installation diagnosis read under
    the lock. Repair retains the already adopted operator authority.
    Instruction scope is explicit; it is not an OS sandbox. Research and user
    decisions are unchanged.
    """
    from .execution_profiles import (profile_ref, capability_evidence, prepare_prompt,
                                     prompt_seal, execution_observation)
    from .session_slots import SessionSlots
    from .file_io import os_lock
    from contextlib import ExitStack
    from .repository import new_id
    from .git_store import GitStateStoreLockError
    from .launch import mark_dispatched, mark_returned
    from .planning import instance_ended
    from .provider_engine import record_model_policy_violation
    from . import activities, execution_lifecycle
    if failure is not None and (failure.get("kind") not in {"engine_unavailable", "installation_defect"}
                                or not failure.get("error")):
        raise ValueError("recovery requires preserved engine failure evidence")
    if _held(workspace):
        return {"outcome": "held"}
    repo = ResearchRepository(repository, instance)
    try:
        with repo.writer_lock():
            head, state, runtime = repo.load()
            config = state["config"]
            block = supervision_block({**supervision_facts(state, runtime), 'held': _held(workspace)})
            if block == 'disabled':
                return {"outcome": "recovery_disabled", "failure": failure}
            if block not in {None, 'installation_repair'}:
                return {"outcome": "held"}
            from .repair_execution import (installation_failure, installation_sha256 as installed_skill_sha256,
                                           pending_installation_repair, resume_installation_repair)
            if failure is None:
                pending = pending_installation_repair(runtime)
                if pending is None:
                    return {"outcome": "recovery_waiting", "reason": "no installation repair is pending"}
                failure = installation_failure(runtime, pending)
            diagnosis = None
            if failure['kind'] == 'installation_defect':
                diagnosis = runtime.get('operational_dispositions', {}).get(failure.get('diagnosis_id'))
                if diagnosis is None or installation_failure(runtime, diagnosis) != failure:
                    raise ValueError('installation diagnosis is missing or differs from its published record')
            from .launch import termination_confirmed
            for execution in runtime.get("executions", {}).values():
                if execution.get("status") == "ended":
                    continue
                if not execution.get('launch_ticket') or not termination_confirmed(execution['launch_ticket'], recovering=True):
                    return {"outcome": "recovery_waiting", "reason": "existing execution termination is unconfirmed",
                            "execution_id": execution["id"]}
            maintenance = ExitStack()
            try:
                maintenance.enter_context(os_lock(repo.git_dir / "do-math-installation-maintenance.lock", blocking=False))
            except OSError:
                return {"outcome": "recovery_waiting", "reason": "installation maintenance is already active"}
            try:
                installation_sha256 = installed_skill_sha256(LIVE_INSTALLATION_ROOT)
                identity_fields = ('kind', 'diagnosis_id', 'error', 'repair_target', 'verification',
                    'target_execution_id', 'evidence_refs', 'installation_sha256', 'evidence_path', 'engine_run_directory')
                failure_identity = hashlib.sha256(json.dumps({key: failure[key] for key in identity_fields if key in failure},
                    ensure_ascii=False, sort_keys=True).encode('utf-8')).hexdigest()
                if diagnosis:
                    failure_identity = failure['failure_sha256']
                # One automatic repair per actual failure and installation edition. A call that judged
                # no repair does not count: the provider limit refused it, or a HOLD, pause or close
                # held it before its repair report was received. A held call with a received report
                # still counts. The provider gate and the supervision blocks pace a retry.
                def attempted(execution):
                    disposition = execution.get('result_disposition')
                    recovery = disposition.get('recovery') if isinstance(disposition, dict) else None
                    unjudged = (recovery == 'recovery_provider_limited'
                                or (recovery == 'recovery_held' and not execution.get('submission_receipt')))
                    return (execution.get('role') == 'recovery'
                            and execution.get('input_manifest', {}).get('repair_identity') == {
                                'failure_sha256': failure_identity, 'installation_sha256': installation_sha256}
                            and not unjudged)
                if any(attempted(e) for e in runtime.get('executions', {}).values()):
                    return {'outcome': 'recovery_waiting', 'reason': 'same failure and installation already attempted'}
                # The one role selection rule; it picks the adopted recovery edition.
                chosen = selection(config, {"role": "recovery"}, {}, {}, instance=state)
                profile = state["execution_profiles"][chosen["profile_ref"]["id"]]
                from .initialization import adapter_for, capability_requirements
                adapter = adapter_for(profile)
                reference = profile_ref(profile)
                checked_at = now()
                capability = capability_requirements(state, reference,
                    current_identity=adapter.capability_identity(), at=checked_at)
                if not capability["satisfied"]:
                    description = adapter.describe()  # CLI version/help only; never a model call.
                    description.setdefault("identity", adapter.capability_identity())
                    evidence = capability_evidence(profile, description, observed_at=checked_at)
                    state.setdefault("capability_evidence", {})[evidence["id"]] = evidence
                    head = repo.save_with_state(head, state, runtime)[0]
                    capability = capability_requirements(state, reference,
                        current_identity=adapter.capability_identity(), at=now())
                if not capability["satisfied"]:
                    return {"outcome": "recovery_waiting", "reason": "profile_capability_unavailable",
                            "capability": capability}
                eid = new_id("EX")
                # The activity of one failure is keyed like its attempts, so a later
                # observation of the same failure continues the same activity.
                owner = {"kind": "installation_recovery", "failure_sha256": failure_identity}
                activity = next((a for a in runtime.get("activities", {}).values()
                                 if a.get("owner_ref") == owner and a.get("status") != "finished"), None)
                at = now()
                if activity is None:
                    activity = activities.open_activity(runtime, activity_id=new_id("AY"), activity_kind="recovery",
                        owner_ref=owner, input_refs=[failure], opened_at=at)
                elif activity["status"] == "waiting":
                    activities.resume_activity(runtime, activity["id"], condition=activity["waiting"]["condition"], at=at)
                aid = activity["id"]
                run_directory = _operator_dir(workspace) / "recovery" / eid
                execution_workspace = run_directory / "workspace"
                execution_workspace.mkdir(parents=True)
                failure_inputs = []
                for index, artifact_ref in enumerate(failure.get('evidence_refs', [])):
                    raw = repo.read(artifact_ref, head)
                    local = execution_workspace / 'input' / f'failure-{index}.json'
                    local.parent.mkdir(exist_ok=True)
                    local.write_bytes(raw)
                    failure_inputs.append({'artifact_ref': artifact_ref, 'local_path': str(local),
                        'sha256': hashlib.sha256(raw).hexdigest()})
                prompt = (
                    ("Repair only the independently diagnosed do-math installation defect that blocks the preserved submission. "
                     if diagnosis else "Repair only the do-math installation defect that prevents this engine from starting. ")
                    + "Reproduce the recorded failure, make the smallest code repair, and run relevant checks. "
                    "Preserve failure evidence, verification commands and changed file paths in your report. "
                    "For a diagnosed submission defect, report repair_outcome=repaired only after reproducing and fixing it; "
                    "otherwise report unresolved. Write regression logs inside this workspace and list their relative paths in verification_evidence. "
                    "Do not change research records, goals, budgets, grants, user configuration or scheduled tasks. "
                    "Do not start the engine or wait for research: the launcher owns restart after releasing its lock. "
                    "Existing installation-repair approval applies; a new research or external-action authority does not.\n"
                    + json.dumps({"failure": failure, "failure_inputs": failure_inputs,
                                  "installation": str(LIVE_INSTALLATION_ROOT), "repository": str(repository),
                                  "instance": instance, "execution_id": eid, "profile_ref": reference}, ensure_ascii=False))
                prompt = prepare_prompt(prompt, profile)
                sealed_input = prompt_seal(prompt)
                if sealed_input["bytes"] > profile["input"]["max_input_bytes"]:
                    return {"outcome": "recovery_waiting", "reason": "input_overflow", "prompt": sealed_input}
                (run_directory / "input.txt").write_bytes(prompt.encode("utf-8"))
                execution = execution_lifecycle.create_execution(execution_id=eid, owner_activity_id=aid,
                    actor_kind="ai", input_manifest={"failure": failure, "prompt": sealed_input,
                        'repair_identity': {'failure_sha256': failure_identity, 'installation_sha256': installation_sha256},
                        "repair_authority": {"source": "adopted_operator_repair_scope", "boundary": "instructions"}},
                    profile_ref=reference, created_at=at,
                    context_origin=activity["assigned_execution_ids"][-1:])
                execution["role"] = "recovery"
                slots = SessionSlots(runtime, state)
                if not slots.acquire(eid, profile=profile, execution=execution):
                    return {"outcome": "recovery_waiting", "reason": slots.admission_reason,
                            "wait": deepcopy(slots.admission_wait)}
                activities.assign_execution(runtime, aid, execution)
                mark_dispatched(execution['launch_ticket'])
                head = repo.save_with_state(head, state, runtime)[0]
                def on_started(identity):
                    nonlocal head
                    slots.started(eid, identity, at=now())
                    head = repo.save_with_state(head, state, runtime)[0]
                result = None
                try:
                    result = ModelRunner().run(prompt=prompt, output_schema=repair_report_schema(diagnosed=diagnosis is not None),
                        workspace=execution_workspace, evidence_dir=run_directory / "evidence",
                        model=chosen["model"], effort=profile["ai"]["effort"],
                        timeout_seconds=profile["window"]["call_timeout_seconds"],
                        execution_id=eid, profile=profile, input_seal=sealed_input, on_started=on_started,
                        launch_ticket=deepcopy(runtime['executions'][eid]['launch_ticket']),
                        should_stop=lambda: (_operator_dir(workspace) / "HOLD.json").exists())
                    execution = runtime["executions"][eid]
                    _json(run_directory / "runner-result.json", result)
                    # Opaque provider decimals stay in transport JSON, never
                    # silently rounded into the integer-only state contract.
                    execution["runner"] = {"status": result["status"], "evidence_ref": str(run_directory / "runner-result.json")}
                    if result.get("output") is not None:
                        execution["output"] = result["output"]
                    execution["error"] = result.get("error")
                    slots.provider_result_from_run(eid, result, config)
                    observation = execution_observation(result)
                    if observation is not None:
                        execution["provider_observation"] = observation
                    if result.get("capability_evidence"):
                        evidence = result["capability_evidence"]
                        state.setdefault("capability_evidence", {})[evidence["id"]] = evidence
                    outcome = "repaired" if result.get("status") == "completed" else "recovery_failed"
                    if result.get("error_kind") == "provider_limit":
                        outcome = "recovery_provider_limited"
                    if result.get("error_kind") == "model_policy":
                        record_model_policy_violation(state, runtime, eid, chosen["model"], result)
                    if outcome == 'repaired' and diagnosis:
                        regression = collect_repair_verification(result.get('output'), execution_workspace)
                        _json(run_directory / 'regression-evidence.json', {'files': regression})
                    if outcome == "repaired":
                        execution["submission_receipt"] = {
                            "kind": execution_lifecycle.RECOVERY_REPORT_RECEIPT, "state": "accepted", "execution_id": eid,
                            "receiver": "recovery_launcher", "observed_at": now(),
                            "evidence_ref": str(run_directory / "evidence"),
                            "scope": "structured_recovery_report_not_research_integration"}
                        verified = subprocess.run([sys.executable, str(Path(LIVE_INSTALLATION_ROOT) / "scripts/probe_cli.py"), "--skill-only"],
                            capture_output=True, text=True, encoding="utf-8", check=False,
                            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
                        _json(run_directory / "verification.json", {"exit_code": verified.returncode,
                              "stdout": verified.stdout, "stderr": verified.stderr})
                        if verified.returncode != 0:
                            outcome = "recovery_verification_failed"
                    if ((_operator_dir(workspace) / 'HOLD.json').exists()
                            or runtime.get('user_pause') or runtime.get('status') == 'paused'
                            or instance_ended(state, runtime)):
                        outcome = 'recovery_held'
                except Exception as error:
                    outcome = "recovery_failed"
                    execution = runtime["executions"][eid]
                    execution["error"] = {"type": type(error).__name__, "message": str(error)}
                finally:
                    # save() may rebuild dictionary objects; always update the loaded view.
                    execution = runtime["executions"][eid]
                    mark_returned(execution['launch_ticket'], result)
                    ended_at = now()
                    released = execution_lifecycle.release_or_hold(execution, slots, at=ended_at)
                    if not released:
                        outcome = "recovery_termination_unknown"
                    else:
                        execution_lifecycle.transition_execution(execution, "stopping", at=ended_at, reason=outcome)
                        execution_lifecycle.transition_execution(execution, "ended", at=ended_at,
                            outcome="output_accepted" if execution.get("submission_receipt") else "execution_incomplete",
                            disposition={"recovery": outcome})
                        if outcome == "repaired":
                            activities.finish_activity(runtime, aid, result_refs=[eid], unresolved=[], followups=[], at=ended_at)
                        else:
                            activities.wait_for(runtime, aid, reason=outcome,
                                condition={"kind": "installation_repair_retry", "failure": owner},
                                next_owner="recovery", at=ended_at)
                        if diagnosis:
                            current_diagnosis = runtime['operational_dispositions'][diagnosis['id']]
                            if outcome == 'repaired':
                                resume_installation_repair(runtime, current_diagnosis, repaired_by=eid, at=ended_at)
                            else:
                                current_diagnosis['status'] = 'installation_repair_waiting'
                                current_diagnosis.setdefault('result', {})['installation_repair'].update(
                                    status=outcome, attempted_by=eid)
                    head = repo.save_with_state(head, state, runtime)[0]
                report = {"outcome": outcome, "execution_id": eid, "snapshot": head,
                          "run_directory": str(run_directory)}
                _json(run_directory / "result.json", report)
            finally:
                maintenance.close()
    except GitStateStoreLockError:
        return {"outcome": "engine_running", "model_called": False}
    if report["outcome"] == "repaired":
        # Restart only after both locks have been released; never wait holding capacity.
        _json(_operator_dir(workspace) / "latest-engine.json", {
            "outcome": "recovery_verified", "recovery_report": str(Path(report["run_directory"]) / "result.json")})
        report["restart"] = wake(repository, instance, workspace)
    return report


def main(argv=None):
    """Stable scheduling surface without importing engine through the CLI."""
    import argparse
    parser = argparse.ArgumentParser(description="Model-free do-math supervisor and failure-only recovery")
    parser.add_argument("action", choices=("check", "run-engine", "wake"))
    parser.add_argument("--repository", type=Path, required=True)
    parser.add_argument("--instance", required=True)
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--probe", action="store_true")
    args = parser.parse_args(argv)
    if args.action == "check":
        result = check(args.repository, args.instance, args.workspace, probe=args.probe)
    elif args.action == "wake":
        result = wake(args.repository, args.instance, args.workspace)
    else:
        result = run_engine(args.repository, args.instance, args.workspace)
    print(json.dumps(result, ensure_ascii=False))
    return 0
