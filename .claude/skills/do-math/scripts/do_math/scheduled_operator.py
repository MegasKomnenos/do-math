"""Model-free supervision and engine-exclusive installation recovery.

Normal supervision keeps local evidence; failure-only repair uses the same Git
execution/reservation families while holding the repository writer lock.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any
from copy import deepcopy

from .repository import ResearchRepository
from .model_runner import ModelRunner
from .model_policy import selection
from .provider_wait import epoch_seconds
from .operation_trace import workspace_operation, child_environment
from .supervision import (OPERATOR_SCHEMA, SUPERVISION_BLOCKS, blocked_check_outcome, check_repair_version, collect_repair_verification,
                          engine_failure_recovery, engine_run_outcome, hold_pause_reason, repair_report_schema,
                          start_guard, supervision_block,
                          supervision_facts, task_names, wake_is_current, wake_need)


SCRIPTS = Path(__file__).resolve().parents[1]
SKILL_ROOT = SCRIPTS.parent




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
    scheduler,
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
    return scheduler.run(action, arguments)

def cancel_wake(repository: Path, instance: str, workspace: Path, *, scheduler) -> dict[str, Any]:
    """Remove the one-shot wake task and its local registration marker."""
    result = schedule("cancel-wake", repository=repository, instance=instance, workspace=workspace, scheduler=scheduler)
    (_operator_dir(workspace) / "wake-registration.json").unlink(missing_ok=True)
    return result


def _held(workspace: Path) -> bool:
    return (_operator_dir(workspace) / "HOLD.json").exists()


def resolve_workspace(repository: Path, instance: str, *, ports) -> Path:
    _, state, _ = ResearchRepository(repository, instance, backend=ports.git_backend, clock=ports.clock).load()
    workspace = state.get("workspace")
    if not isinstance(workspace, str) or not workspace:
        raise ValueError("instance does not have a workspace")
    return Path(workspace).resolve()


def read_status(repository: Path, instance: str, *, ports, codex_home, environment, host_id) -> dict[str, Any]:
    from .engine import ResearchEngine
    return ResearchEngine(repository, instance, ports=ports, codex_home=codex_home, environment=environment, host_id=host_id).status()


def _operator_dir(workspace: Path) -> Path:
    return workspace / "operator"


def hold(workspace: Path, *, reason: str, clock) -> dict[str, Any]:
    """Set a local hold marker; intentionally does not send pause or resume."""
    value = {"id": clock.random_hex(16), "reason": reason, "started_at": clock.now()}
    _json(_operator_dir(workspace) / "HOLD.json", value)
    return value


def release(workspace: Path, *, clock) -> dict[str, Any]:
    """Release only this operator marker; research remains paused until resumed."""
    path = _operator_dir(workspace) / "HOLD.json"
    held = _load_json(path)
    if held is None:
        return {"released": None}
    path.unlink()
    result = {"released": held, "released_at": clock.now()}
    _json(_operator_dir(workspace) / "release.json", result)
    return result


@workspace_operation('engine_launch')
def run_engine(repository: Path, instance: str, workspace: Path, *, ports, installation_root: Path = SKILL_ROOT, environment, codex_home, host_id,
               installation_manifest: Path | None = None) -> dict[str, Any]:
    """Start the live engine with the caller's explicit frozen manifest, if any.

    Only operator_bootstrap discovers a manifest beside its independent entrypoint.
    Package callers without one start live, regardless of this module's location.
    """
    try:
        guard = engine_start_guard(repository, instance, workspace, ports=ports, codex_home=codex_home, environment=environment, host_id=host_id)
    except Exception as error:
        record = {"outcome": "engine_failed", "kind": "engine_unavailable",
                  "error_type": type(error).__name__, "error": str(error)}
        _json(_operator_dir(workspace) / "latest-engine.json", record)
        return record
    if guard["outcome"] != "startable":
        return guard
    status = guard["before"]
    run_directory = _operator_dir(workspace) / "engine" / (ports.clock.wall().strftime("%Y%m%dT%H%M%SZ") + "-" + ports.clock.random_hex(4))
    run_directory.mkdir(parents=True)
    _json(run_directory / "before.json", status)
    command = [sys.executable, str(Path(installation_root) / "scripts/do_math.py"),
               "run", "--repository", str(repository), "--instance", instance, "--watch"]
    import operator_bootstrap as bootstrap
    if installation_manifest is not None:
        manifest = bootstrap.verify_snapshot(Path(installation_manifest))
        if Path(manifest['installation_root']).resolve() != Path(installation_root).resolve():
            raise ValueError('startup manifest identifies a different installation root')
        command.extend(['--installation-manifest', str(Path(installation_manifest).resolve())])
    record = {"outcome": "running", "before": status, "command": command, "run_directory": str(run_directory)}
    _json(run_directory / "result.json", record)
    try:
        from .formal import _job_run
        code, stdout, stderr, _ = _job_run(command, Path.cwd(), jobs=ports.jobs,
                                         clock=ports.clock, env=child_environment(environment),
                                         evidence_dir=run_directory, decode_errors="strict", environment=environment, preserve_os_error=True)
        (run_directory / "stdout.json").write_text(stdout, encoding="utf-8")
        (run_directory / "stderr.txt").write_text(stderr, encoding="utf-8")
        record.update(outcome=engine_run_outcome(code, stdout), exit_code=code)
        record["after"] = read_status(repository, instance, ports=ports, codex_home=codex_home, environment=environment, host_id=host_id)
        if supervision_block({**record['after'], 'held': _held(workspace)}) == 'installation_repair':
            try:
                record['supervisor_request']=schedule('start-operator',repository=repository,
                    instance=instance,workspace=workspace,scheduler=ports.scheduler)
            except (RuntimeError,OSError) as error:
                record['supervisor_request']={'status':'failed','error':str(error),
                    'next_owner':'scheduled_operator','fallback':'periodic supervision'}
    except Exception as error:
        record.update(outcome="engine_failed", error=f"{type(error).__name__}: {error}")
    _json(run_directory / "result.json", record)
    _json(_operator_dir(workspace) / "latest-engine.json", record)
    return record




def engine_start_guard(repository: Path, instance: str, workspace: Path, *, status=None, ports, codex_home, environment, host_id) -> dict[str, Any]:
    """Read the conditions that must hold before either task starts an engine.

    An explicit engine start does not depend on automatic supervision being enabled.
    """
    if _held(workspace):
        return {"outcome": "held"}
    if status is None:
        status = read_status(repository, instance, ports=ports, codex_home=codex_home, environment=environment, host_id=host_id)
    return start_guard(status)




def reconcile_wake(repository: Path, instance: str, workspace: Path, *, facts: dict, providers: dict,
                   scheduler, clock) -> dict:
    """Repair a missing/stale one-shot reservation before invoking any model.

    ``facts`` are the caller's supervision facts and ``providers`` its provider
    snapshot, both from the state it already holds. A queried task status is
    returned as ``observed`` so the caller need not query it again.
    """
    marker = _operator_dir(workspace) / "wake-registration.json"
    previous = _load_json(marker)
    need = wake_need(facts, providers, held=_held(workspace))
    if "wanted" not in need:
        if previous:
            cancel_wake(repository, instance, workspace, scheduler=scheduler)
        return need
    wanted = need["wanted"]
    observed = schedule("status", repository=repository, instance=instance, workspace=workspace, scheduler=scheduler)
    if wake_is_current(previous, wanted, observed, now=clock.wall().timestamp()):
        return {"status": "scheduled", **wanted, "observed": observed}
    schedule("schedule-wake", repository=repository, instance=instance, workspace=workspace, scheduler=scheduler,
             wake_at=wanted["retry_at"], wake_key=wanted["key"])
    _json(marker, wanted)
    return {"status": "scheduled", **wanted, "observed": observed}


def wake(repository: Path, instance: str, workspace: Path, *, ports, codex_home, environment, host_id) -> dict:
    """No model ping: wake only the engine entry point with its usual guards."""
    guard = engine_start_guard(repository, instance, workspace, ports=ports, codex_home=codex_home, environment=environment, host_id=host_id)
    if guard["outcome"] != "startable":
        return guard
    scheduled = schedule("start-engine", repository=repository, instance=instance, workspace=workspace, scheduler=ports.scheduler)
    return {"outcome": "engine_requested", "schedule": scheduled, "before": guard["before"]}


def check(repository: Path, instance: str, workspace: Path, *, ports, probe: bool = False, installation_root: Path = SKILL_ROOT, codex_home, environment, host_id) -> dict[str, Any]:
    """Model-free supervision; preserved engine failure or accepted defect diagnosis opens recovery.

    Every judgment reads the one status snapshot; recovery rereads under its lock.
    """
    if _held(workspace):
        return {"outcome": "held"}
    try:
        status = read_status(repository, instance, ports=ports, codex_home=codex_home, environment=environment, host_id=host_id)
    except Exception as error:
        failure = {"outcome": "recovery_required", "kind": "engine_unavailable",
                   "error_type": type(error).__name__, "error": str(error),
                   "observed_at": ports.clock.now()}
        _json(_operator_dir(workspace) / "engine-failure.json", failure)
        if probe:
            return failure
        return recovery(repository, instance, workspace, failure=failure, ports=ports, installation_root=installation_root, environment=environment, host_id=host_id, codex_home=codex_home)
    block = supervision_block(status)
    blocked = blocked_check_outcome(block, status)
    if blocked is not None:
        return blocked
    if block == 'installation_repair':
        if probe:
            from .repair_execution import installation_failure
            _, _, runtime = ResearchRepository(repository, instance, backend=ports.git_backend, clock=ports.clock).load(status["snapshot"])
            return {'outcome': 'installation_repair_pending', 'model_called': False,
                    'failure': installation_failure(runtime, status['installation_repair'])}
        return recovery(repository, instance, workspace, ports=ports, installation_root=installation_root, environment=environment, host_id=host_id, codex_home=codex_home)
    if probe:
        return {"outcome": "observed", "status": status, "model_called": False,
                "engine_start": engine_start_guard(repository, instance, workspace, status=status, ports=ports, codex_home=codex_home, environment=environment, host_id=host_id)}
    failure = engine_failure_recovery(_load_json(_operator_dir(workspace) / "latest-engine.json"),
                                      evidence_path=_operator_dir(workspace) / "latest-engine.json")
    if failure is not None:
        return recovery(repository, instance, workspace, failure=failure, ports=ports, installation_root=installation_root, environment=environment, host_id=host_id, codex_home=codex_home)
    wake_status = reconcile_wake(repository, instance, workspace, facts=status,
                                 providers=status["provider_waits"]["providers"], scheduler=ports.scheduler, clock=ports.clock)
    observed = wake_status.pop("observed", None)
    guard = engine_start_guard(repository, instance, workspace, status=status, ports=ports, codex_home=codex_home, environment=environment, host_id=host_id)
    if guard["outcome"] != "startable":
        return {**guard, "provider_wake": wake_status, "model_called": False}
    if observed is None:
        observed = schedule("status", repository=repository, instance=instance, workspace=workspace, scheduler=ports.scheduler)
    if (observed.get("engine") or {}).get("state") == "Running":
        return {"outcome": "engine_running", "model_called": False}
    started = schedule("start-engine", repository=repository, instance=instance, workspace=workspace, scheduler=ports.scheduler)
    return {"outcome": "engine_requested", "schedule": started, "provider_wake": wake_status, "model_called": False}


def recovery(repository: Path, instance: str, workspace: Path, *, ports, failure: dict | None = None, installation_root: Path = SKILL_ROOT, environment, host_id, codex_home) -> dict:
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
    from .git_store import GitStateStoreLockError
    from .launch import mark_dispatched, mark_returned
    from .provider_engine import record_model_policy_violation
    from . import activities, execution_lifecycle
    from .repair_execution import (already_attempted, check_recovery_failure, failure_identity, failure_to_repair,
                                   matching_diagnosis, record_recovery_attempt, recovery_block_outcome,
                                   recovery_held, recovery_report_receipt, repair_prompt, runner_outcome,
                                   unconfirmed_termination)
    check_recovery_failure(failure)
    if _held(workspace):
        return {"outcome": "held"}
    repo = ResearchRepository(repository, instance, backend=ports.git_backend, clock=ports.clock)
    try:
        with repo.writer_lock():
            head, state, runtime = repo.load()
            config = state["config"]
            block = supervision_block({**supervision_facts(state, runtime), 'held': _held(workspace)})
            blocked = recovery_block_outcome(block, failure)
            if blocked is not None:
                return blocked
            from .repair_execution import installation_evidence
            failure = failure_to_repair(runtime, failure)
            if failure is None:
                return {"outcome": "recovery_waiting", "reason": "no installation repair is pending"}
            diagnosis = matching_diagnosis(runtime, failure)
            unconfirmed = unconfirmed_termination(runtime, jobs=ports.jobs)
            if unconfirmed is not None:
                return {"outcome": "recovery_waiting", "reason": "existing execution termination is unconfirmed",
                        "execution_id": unconfirmed}
            maintenance = ExitStack()
            try:
                maintenance.enter_context(os_lock(repo.git_dir / "do-math-installation-maintenance.lock", blocking=False))
            except OSError:
                return {"outcome": "recovery_waiting", "reason": "installation maintenance is already active"}
            try:
                before_installation = installation_evidence(installation_root, backend=ports.git_backend)
                installation_sha256 = before_installation['installation_version']
                if installation_sha256 is None:
                    raise ValueError('cannot identify repair installation: ' + before_installation['installation_error'])
                failure_sha256 = failure_identity(failure, diagnosis)
                if already_attempted(runtime, failure_sha256, installation_sha256):
                    return {'outcome': 'recovery_waiting', 'reason': 'same failure and installation already attempted'}
                # The one role selection rule; it picks the adopted recovery edition.
                chosen = selection(config, {"role": "recovery"}, {}, {}, instance=state)
                profile = state["execution_profiles"][chosen["profile_ref"]["id"]]
                from .initialization import capability_requirements
                host = ports.host
                reference = profile_ref(profile)
                checked_at = ports.clock.now()
                capability = capability_requirements(state, reference,
                    current_identity=host.cli_identity(profile), at=checked_at, host=ports.host)
                if not capability["satisfied"]:
                    description = host.cli_describe(profile)  # CLI version/help only; never a model call.
                    description.setdefault("identity", host.cli_identity(profile))
                    evidence = capability_evidence(profile, description, observed_at=checked_at)
                    state.setdefault("capability_evidence", {})[evidence["id"]] = evidence
                    head = repo.save_with_state(head, state, runtime)[0]
                    capability = capability_requirements(state, reference,
                        current_identity=host.cli_identity(profile), at=ports.clock.now(), host=ports.host)
                if not capability["satisfied"]:
                    return {"outcome": "recovery_waiting", "reason": "profile_capability_unavailable",
                            "capability": capability}
                eid = ports.clock.new_id("EX")
                # The activity of one failure is keyed like its attempts, so a later
                # observation of the same failure continues the same activity.
                owner = {"kind": "installation_recovery", "failure_sha256": failure_sha256}
                activity = next((a for a in runtime.get("activities", {}).values()
                                 if a.get("owner_ref") == owner and a.get("status") != "finished"), None)
                at = ports.clock.now()
                if activity is None:
                    activity = activities.open_activity(runtime, activity_id=ports.clock.new_id("AY"), activity_kind="recovery",
                        owner_ref=owner, input_refs=[failure], opened_at=at)
                elif activity["status"] == "waiting":
                    activities.resume_activity(runtime, activity["id"], condition=activity["waiting"]["condition"], at=at)
                aid = activity["id"]
                run_directory = _operator_dir(workspace) / "recovery" / eid
                execution_workspace = run_directory / "workspace"
                execution_workspace.mkdir(parents=True)
                _json(execution_workspace / 'input/installation-before.json', before_installation)
                failure_inputs = []
                for index, artifact_ref in enumerate(failure.get('evidence_refs', [])):
                    raw = repo.read(artifact_ref, head)
                    local = execution_workspace / 'input' / f'failure-{index}.json'
                    local.parent.mkdir(exist_ok=True)
                    local.write_bytes(raw)
                    failure_inputs.append({'artifact_ref': artifact_ref, 'local_path': str(local),
                        'sha256': hashlib.sha256(raw).hexdigest()})
                prompt = prepare_prompt(repair_prompt(failure, failure_inputs, diagnosed=bool(diagnosis),
                    installation=installation_root, repository=repository, instance=instance,
                    execution_id=eid, reference=reference), profile)
                sealed_input = prompt_seal(prompt)
                if sealed_input["bytes"] > profile["input"]["max_input_bytes"]:
                    return {"outcome": "recovery_waiting", "reason": "input_overflow", "prompt": sealed_input}
                (run_directory / "input.txt").write_bytes(prompt.encode("utf-8"))
                execution = execution_lifecycle.create_execution(execution_id=eid, owner_activity_id=aid,
                    actor_kind="ai", input_manifest={"failure": failure, "prompt": sealed_input,
                        'installation_before': before_installation,
                        'repair_identity': {'failure_sha256': failure_sha256, 'installation_sha256': installation_sha256},
                        "repair_authority": {"source": "adopted_operator_repair_scope", "boundary": "instructions"}},
                    profile_ref=reference, created_at=at,
                    context_origin=activity["assigned_execution_ids"][-1:])
                execution["role"] = "recovery"
                slots = SessionSlots(runtime, state, clock=ports.clock, jobs=ports.jobs, host_id=host_id)
                if not slots.acquire(eid, profile=profile, execution=execution):
                    return {"outcome": "recovery_waiting", "reason": slots.admission_reason,
                            "wait": deepcopy(slots.admission_wait)}
                activities.assign_execution(runtime, aid, execution)
                mark_dispatched(execution['launch_ticket'])
                head = repo.save_with_state(head, state, runtime)[0]
                def on_started(identity):
                    nonlocal head
                    slots.started(eid, identity, at=ports.clock.now())
                    head = repo.save_with_state(head, state, runtime)[0]
                result = None
                after_installation = None
                try:
                    result = ModelRunner(jobs=ports.jobs, clock=ports.clock, environment=environment, host_id=host_id).run(prompt=prompt, output_schema=repair_report_schema(diagnosed=diagnosis is not None),
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
                    outcome = runner_outcome(result)
                    if result.get("error_kind") == "model_policy":
                        record_model_policy_violation(state, runtime, eid, chosen["model"], result)
                    after_installation = installation_evidence(installation_root, backend=ports.git_backend)
                    _json(run_directory / 'installation-after.json', after_installation)
                    if outcome == 'repaired':
                        check_repair_version(result['output'], after_installation)
                    if outcome == 'repaired' and diagnosis:
                        regression = collect_repair_verification(result.get('output'), execution_workspace)
                        _json(run_directory / 'regression-evidence.json', {'files': regression})
                    if outcome == "repaired":
                        execution["submission_receipt"] = recovery_report_receipt(
                            eid, evidence_ref=str(run_directory / "evidence"), observed_at=ports.clock.now())
                        from .formal import _job_run
                        code, stdout, stderr, _ = _job_run(
                            [sys.executable, str(Path(installation_root) / "scripts/probe_cli.py"), "--skill-only"],
                            Path.cwd(), jobs=ports.jobs, clock=ports.clock, env=environment,
                            evidence_dir=run_directory, decode_errors="strict", environment=environment, preserve_os_error=True)
                        _json(run_directory / "verification.json", {"exit_code": code,
                              "stdout": stdout, "stderr": stderr})
                        if code != 0:
                            outcome = "recovery_verification_failed"
                    if recovery_held((_operator_dir(workspace) / 'HOLD.json').exists(), state, runtime):
                        outcome = 'recovery_held'
                except Exception as error:
                    outcome = "recovery_failed"
                    execution = runtime["executions"][eid]
                    execution["error"] = {"type": type(error).__name__, "message": str(error)}
                finally:
                    # save() may rebuild dictionary objects; always update the loaded view.
                    execution = runtime["executions"][eid]
                    mark_returned(execution['launch_ticket'], result)
                    ended_at = ports.clock.now()
                    released = execution_lifecycle.release_or_hold(execution, slots, at=ended_at)
                    if not released:
                        outcome = "recovery_termination_unknown"
                    else:
                        record_recovery_attempt(runtime, execution, activity_id=aid, owner=owner, outcome=outcome,
                                                diagnosis=diagnosis, execution_id=eid, at=ended_at)
                    head = repo.save_with_state(head, state, runtime)[0]
                report = {"outcome": outcome, "execution_id": eid, "snapshot": head,
                          "run_directory": str(run_directory),
                          'installation_before': before_installation, 'installation_after': after_installation}
                _json(run_directory / "result.json", report)
            finally:
                maintenance.close()
    except GitStateStoreLockError:
        return {"outcome": "engine_running", "model_called": False}
    if report["outcome"] == "repaired":
        # Restart only after both locks have been released; never wait holding capacity.
        _json(_operator_dir(workspace) / "latest-engine.json", {
            "outcome": "recovery_verified", "recovery_report": str(Path(report["run_directory"]) / "result.json")})
        report["restart"] = wake(repository, instance, workspace, ports=ports, codex_home=codex_home, environment=environment, host_id=host_id)
    return report


def execute(action, repository, instance, workspace, *, ports, environment, host_id, codex_home,
            installation_root: Path = SKILL_ROOT, installation_manifest: Path | None = None, probe=False):
    """Publish startup evidence and pass the same explicit manifest to the engine.

    The bootstrap verifies before importing this package; here the manifest also
    supplies the live comparison. No caller-supplied comparison or path discovery
    can silently select a different startup basis for the child.
    """
    import operator_bootstrap as bootstrap
    from .repair_execution import installation_evidence
    manifest = bootstrap.verify_snapshot(Path(installation_manifest)) if installation_manifest is not None else None
    startup = {'bootstrap': bootstrap.startup_evidence(manifest),
               'installation': installation_evidence(installation_root, backend=ports.git_backend),
               'runtime_root': str(SKILL_ROOT), 'observed_at': ports.clock.now()}
    _json(_operator_dir(workspace) / 'startup.json', startup)
    if action == 'check':
        result = check(repository, instance, workspace, probe=probe, ports=ports,
                       installation_root=installation_root, codex_home=codex_home, environment=environment, host_id=host_id)
    elif action == 'wake':
        result = wake(repository, instance, workspace, ports=ports, codex_home=codex_home, environment=environment, host_id=host_id)
    else:  # run-engine: main's choices and cli.execute's fixed dispatch close this set.
        result = run_engine(repository, instance, workspace, ports=ports, installation_root=installation_root,
                            environment=environment, codex_home=codex_home, host_id=host_id,
                            installation_manifest=installation_manifest)
    return {**result, 'startup': startup}


def main(argv=None, *, ports=None, environment=None, host_id=None, codex_home=None, installation_root: Path = SKILL_ROOT,
         installation_manifest: Path | None = None):
    """Stable scheduling surface without importing engine through the CLI."""
    import os
    import platform
    from .wiring import real_ports
    environment = dict(os.environ) if environment is None else environment
    host_id = platform.node() if host_id is None else host_id
    codex_home = (Path(environment["CODEX_HOME"]) if environment.get("CODEX_HOME") else Path.home() / ".codex") if codex_home is None else codex_home
    ports = real_ports(environment=environment) if ports is None else ports
    import argparse
    parser = argparse.ArgumentParser(description="Model-free do-math supervisor and failure-only recovery")
    parser.add_argument("action", choices=("check", "run-engine", "wake"))
    parser.add_argument("--repository", type=Path, required=True)
    parser.add_argument("--instance", required=True)
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--probe", action="store_true")
    args = parser.parse_args(argv)
    result = execute(args.action, args.repository, args.instance, args.workspace, ports=ports,
                     installation_root=installation_root, codex_home=codex_home, environment=environment,
                     host_id=host_id, installation_manifest=installation_manifest, probe=args.probe)
    print(json.dumps(result, ensure_ascii=False))
    return 0
