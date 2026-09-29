"""Model-free supervision and engine-exclusive installation recovery.

Normal supervision keeps local evidence; failure-only repair uses the same Git
execution/reservation families while holding the repository writer lock.
"""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any
import uuid
from copy import deepcopy

from .system_clock import now
from .repository import ResearchRepository
from .model_runner import ModelRunner
from .model_policy import selection
from .provider_wait import epoch_seconds
from .operation_trace import workspace_operation, child_environment
from .migration_defaults import clock_or_system
from .powershell_scheduler import PowerShellScheduler, Runner
from .supervision import (OPERATOR_SCHEMA, SUPERVISION_BLOCKS, blocked_check_outcome, collect_repair_verification,
                          engine_failure_recovery, engine_run_outcome, hold_pause_reason, repair_report_schema,
                          start_guard, supervision_block,
                          supervision_facts, task_names, wake_is_current, wake_need)


SCRIPTS = Path(__file__).resolve().parents[1]
SKILL_ROOT = SCRIPTS.parent
# Frozen bootstrap overrides this after importing the verified supervisor.
LIVE_INSTALLATION_ROOT = SKILL_ROOT




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

def cancel_wake(repository: Path, instance: str, workspace: Path) -> dict[str, Any]:
    """Remove the one-shot wake task and its local registration marker."""
    result = schedule("cancel-wake", repository=repository, instance=instance, workspace=workspace)
    (_operator_dir(workspace) / "wake-registration.json").unlink(missing_ok=True)
    return result


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
        record.update(outcome=engine_run_outcome(completed.returncode, completed.stdout),
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




def engine_start_guard(repository: Path, instance: str, workspace: Path, *, status=None) -> dict[str, Any]:
    """Read the conditions that must hold before either task starts an engine.

    An explicit engine start does not depend on automatic supervision being enabled.
    """
    if _held(workspace):
        return {"outcome": "held"}
    if status is None:
        status = read_status(repository, instance)
    return start_guard(status)




def reconcile_wake(repository: Path, instance: str, workspace: Path, *, facts: dict, providers: dict,
                   scheduler=None, clock=None) -> dict:
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
            cancel_wake(repository, instance, workspace)
        return need
    wanted = need["wanted"]
    observed = schedule("status", repository=repository, instance=instance, workspace=workspace, scheduler=scheduler)
    if wake_is_current(previous, wanted, observed, now=clock_or_system(clock).wall().timestamp()):
        return {"status": "scheduled", **wanted, "observed": observed}
    schedule("schedule-wake", repository=repository, instance=instance, workspace=workspace, scheduler=scheduler,
             wake_at=wanted["retry_at"], wake_key=wanted["key"])
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
    blocked = blocked_check_outcome(block, status)
    if blocked is not None:
        return blocked
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
    failure = engine_failure_recovery(_load_json(_operator_dir(workspace) / "latest-engine.json"),
                                      evidence_path=_operator_dir(workspace) / "latest-engine.json")
    if failure is not None:
        return recovery(repository, instance, workspace, failure=failure)
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
    from .system_clock import new_id
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
    repo = ResearchRepository(repository, instance)
    try:
        with repo.writer_lock():
            head, state, runtime = repo.load()
            config = state["config"]
            block = supervision_block({**supervision_facts(state, runtime), 'held': _held(workspace)})
            blocked = recovery_block_outcome(block, failure)
            if blocked is not None:
                return blocked
            from .repair_execution import installation_sha256 as installed_skill_sha256
            failure = failure_to_repair(runtime, failure)
            if failure is None:
                return {"outcome": "recovery_waiting", "reason": "no installation repair is pending"}
            diagnosis = matching_diagnosis(runtime, failure)
            unconfirmed = unconfirmed_termination(runtime)
            if unconfirmed is not None:
                return {"outcome": "recovery_waiting", "reason": "existing execution termination is unconfirmed",
                        "execution_id": unconfirmed}
            maintenance = ExitStack()
            try:
                maintenance.enter_context(os_lock(repo.git_dir / "do-math-installation-maintenance.lock", blocking=False))
            except OSError:
                return {"outcome": "recovery_waiting", "reason": "installation maintenance is already active"}
            try:
                installation_sha256 = installed_skill_sha256(LIVE_INSTALLATION_ROOT)
                failure_sha256 = failure_identity(failure, diagnosis)
                if already_attempted(runtime, failure_sha256, installation_sha256):
                    return {'outcome': 'recovery_waiting', 'reason': 'same failure and installation already attempted'}
                # The one role selection rule; it picks the adopted recovery edition.
                chosen = selection(config, {"role": "recovery"}, {}, {}, instance=state)
                profile = state["execution_profiles"][chosen["profile_ref"]["id"]]
                from .initialization import capability_requirements
                from .local_host import LocalHost
                host = LocalHost()
                reference = profile_ref(profile)
                checked_at = now()
                capability = capability_requirements(state, reference,
                    current_identity=host.cli_identity(profile), at=checked_at)
                if not capability["satisfied"]:
                    description = host.cli_describe(profile)  # CLI version/help only; never a model call.
                    description.setdefault("identity", host.cli_identity(profile))
                    evidence = capability_evidence(profile, description, observed_at=checked_at)
                    state.setdefault("capability_evidence", {})[evidence["id"]] = evidence
                    head = repo.save_with_state(head, state, runtime)[0]
                    capability = capability_requirements(state, reference,
                        current_identity=host.cli_identity(profile), at=now())
                if not capability["satisfied"]:
                    return {"outcome": "recovery_waiting", "reason": "profile_capability_unavailable",
                            "capability": capability}
                eid = new_id("EX")
                # The activity of one failure is keyed like its attempts, so a later
                # observation of the same failure continues the same activity.
                owner = {"kind": "installation_recovery", "failure_sha256": failure_sha256}
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
                prompt = prepare_prompt(repair_prompt(failure, failure_inputs, diagnosed=bool(diagnosis),
                    installation=LIVE_INSTALLATION_ROOT, repository=repository, instance=instance,
                    execution_id=eid, reference=reference), profile)
                sealed_input = prompt_seal(prompt)
                if sealed_input["bytes"] > profile["input"]["max_input_bytes"]:
                    return {"outcome": "recovery_waiting", "reason": "input_overflow", "prompt": sealed_input}
                (run_directory / "input.txt").write_bytes(prompt.encode("utf-8"))
                execution = execution_lifecycle.create_execution(execution_id=eid, owner_activity_id=aid,
                    actor_kind="ai", input_manifest={"failure": failure, "prompt": sealed_input,
                        'repair_identity': {'failure_sha256': failure_sha256, 'installation_sha256': installation_sha256},
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
                    outcome = runner_outcome(result)
                    if result.get("error_kind") == "model_policy":
                        record_model_policy_violation(state, runtime, eid, chosen["model"], result)
                    if outcome == 'repaired' and diagnosis:
                        regression = collect_repair_verification(result.get('output'), execution_workspace)
                        _json(run_directory / 'regression-evidence.json', {'files': regression})
                    if outcome == "repaired":
                        execution["submission_receipt"] = recovery_report_receipt(
                            eid, evidence_ref=str(run_directory / "evidence"), observed_at=now())
                        verified = subprocess.run([sys.executable, str(Path(LIVE_INSTALLATION_ROOT) / "scripts/probe_cli.py"), "--skill-only"],
                            capture_output=True, text=True, encoding="utf-8", check=False,
                            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
                        _json(run_directory / "verification.json", {"exit_code": verified.returncode,
                              "stdout": verified.stdout, "stderr": verified.stderr})
                        if verified.returncode != 0:
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
                    ended_at = now()
                    released = execution_lifecycle.release_or_hold(execution, slots, at=ended_at)
                    if not released:
                        outcome = "recovery_termination_unknown"
                    else:
                        record_recovery_attempt(runtime, execution, activity_id=aid, owner=owner, outcome=outcome,
                                                diagnosis=diagnosis, execution_id=eid, at=ended_at)
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
