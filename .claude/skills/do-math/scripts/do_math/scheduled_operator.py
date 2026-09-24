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

if __package__ in {None, ""}:  # Direct launcher survives engine/CLI import failures.
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    __package__ = "do_math"

from .repository import ResearchRepository
from .model_runner import ModelRunner
from .model_policy import selection
from .provider_wait import timestamp


SCRIPTS = Path(__file__).resolve().parents[1]
SKILL_ROOT = SCRIPTS.parent
# Frozen bootstrap overrides this after importing the verified supervisor.
LIVE_INSTALLATION_ROOT = SKILL_ROOT
ENTRYPOINT = SCRIPTS / "do_math.py"
SCHEDULE_SCRIPT = SCRIPTS / "operator_schedule.ps1"
PROMPT = SKILL_ROOT / "계약" / "독립-운영.md"

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
    schema = deepcopy(OPERATOR_SCHEMA)
    if diagnosed:
        schema['properties'].update(repair_outcome={'enum':['repaired','unresolved']},
            verification_evidence={'type':'array','items':{'type':'string','minLength':1}})
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
    def evidence_default(item):
        if isinstance(item, bytes):
            import base64
            return {"sha256": hashlib.sha256(item).hexdigest(), "text": item.decode("utf-8", "replace"),
                    "base64": base64.b64encode(item).decode("ascii")}
        if isinstance(item, Path):
            return str(item)
        raise TypeError("unsupported supervisor evidence: " + type(item).__name__)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, default=evidence_default, allow_nan=False,
                                    ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def _load_json(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    value = json.loads(path.read_text(encoding="utf-8"))
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
    interval_seconds: int = 7200,
    operator_timeout_seconds: int = 5400,
    wake_at: str | None = None,
    wake_key: str | None = None,
    runner: Runner = subprocess.run,
) -> dict[str, Any]:
    """Call the narrow PowerShell scheduler adapter and decode its JSON result."""
    if action not in {"install", "uninstall", "status", "start-engine", "start-operator", "schedule-wake", "cancel-wake"}:
        raise ValueError("unsupported schedule action")
    if isinstance(interval_seconds, bool) or not isinstance(interval_seconds, int) or interval_seconds < 1:
        raise ValueError("operator interval must be a positive integer")
    names = task_names(repository, instance)
    pythonw = Path(sys.executable).with_name("pythonw.exe")
    executable = str(pythonw) if pythonw.is_file() else sys.executable
    powershell = shutil.which("powershell.exe") or shutil.which("powershell") or "powershell.exe"
    command = [
        powershell, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(SCHEDULE_SCRIPT),
        "-Action", action,
        "-Repository", str(repository.resolve()),
        "-Instance", instance,
        "-Workspace", str(workspace.resolve()),
        "-Python", executable,
        "-Entrypoint", str(ENTRYPOINT),
        "-OperatorTask", names["operator"],
        "-EngineTask", names["engine"],
        "-WakeTask", names["wake"],
        "-IntervalSeconds", str(interval_seconds),
        "-OperatorTimeoutSeconds", str(operator_timeout_seconds),
    ]
    if action == "schedule-wake":
        if timestamp(wake_at) is None or not wake_key:
            raise ValueError("wake requires a timezone-aware retry time and generation key")
        command.extend(["-WakeAt", wake_at, "-WakeKey", wake_key])
    completed = runner(command, capture_output=True, text=True, encoding="utf-8", check=False, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    if completed.returncode:
        raise RuntimeError(completed.stderr.strip() or completed.stdout.strip() or "scheduled-task operation failed")
    try:
        value = json.loads(completed.stdout)
    except json.JSONDecodeError as error:
        raise RuntimeError("scheduled-task adapter returned invalid JSON") from error
    if not isinstance(value, dict):
        raise RuntimeError("scheduled-task adapter result must be an object")
    return value


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


def _latest_report(report: dict[str, Any], result_path: Path) -> dict[str, Any]:
    result = report.get("result") if isinstance(report.get("result"), dict) else {}
    return {key: report[key] for key in ("outcome", "probe", "status_before", "run_directory", "output", "ended_at", "error") if key in report} | {
        "result_path": str(result_path), "evidence_dir": result.get("evidence_dir"), "usage": result.get("usage", {}),
    }


def hold(workspace: Path, *, reason: str) -> dict[str, Any]:
    """Set a local hold marker; intentionally does not send pause or resume."""
    value = {"id": uuid.uuid4().hex, "reason": reason, "started_at": datetime.now(timezone.utc).isoformat()}
    _json(_operator_dir(workspace) / "HOLD.json", value)
    return value


def release(workspace: Path) -> dict[str, Any]:
    """Release only this operator marker; research remains paused until resumed."""
    path = _operator_dir(workspace) / "HOLD.json"
    held = _load_json(path)
    if held is None:
        return {"released": None}
    path.unlink()
    result = {"released": held, "released_at": datetime.now(timezone.utc).isoformat()}
    _json(_operator_dir(workspace) / "release.json", result)
    return result


def invocation_context(repository: Path, instance: str, workspace: Path, status: dict[str, Any], skill_root: Path = SKILL_ROOT,
                       *, probe: bool = False, scholarly_configured: bool = False) -> dict[str, Any]:
    run_directory = _operator_dir(workspace) / "runs" / (datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:8])
    previous = _operator_dir(workspace) / "latest-report.json"
    return {
        "repository": str(repository.resolve()), "instance": instance, "workspace": str(workspace.resolve()),
        "skill_root": str(skill_root.resolve()), "run_directory": str(run_directory), "status": status,
        "probe": probe, "scholarly_configured": scholarly_configured,
        "previous_report": str(previous) if previous.is_file() else None,
        "control_policy": {
            "user_pause": "never resume", "hold": "never start engine while HOLD.json exists",
            "research_state": "use do-math CLI controls; never edit JSON or Git refs directly",
        },
    }


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
        completed = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", check=False, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        (run_directory / "stdout.json").write_text(completed.stdout, encoding="utf-8")
        (run_directory / "stderr.txt").write_text(completed.stderr, encoding="utf-8")
        record.update(outcome="completed" if completed.returncode == 0 else "engine_failed", exit_code=completed.returncode)
        record["after"] = read_status(repository, instance)
    except Exception as error:
        record.update(outcome="engine_failed", error=f"{type(error).__name__}: {error}")
    _json(run_directory / "result.json", record)
    _json(_operator_dir(workspace) / "latest-engine.json", record)
    return record


def engine_start_guard(repository: Path, instance: str, workspace: Path, *, status=None) -> dict[str, Any]:
    """Read the conditions that must hold before either task starts an engine."""
    if (_operator_dir(workspace) / "HOLD.json").exists():
        return {"outcome": "held"}
    if status is None:
        status = read_status(repository, instance)
    if status.get("model_policy_violation"):
        return {"outcome": "model_policy_waiting", "status": status, "reason": "Reported model violated the instance lock; no further operator model was called."}
    if status.get("user_pause") or status.get("status") == "paused":
        return {"outcome": "paused", "before": status}
    if status.get('conversation_lost'):
        return {'outcome': 'user_paused', 'before': status}
    if status.get('installation_repair'):
        return {'outcome': 'installation_repair_waiting', 'before': status}
    providers = status.get("provider_waits", {}).get("providers", {})
    provider_due = any(row.get("due") for row in providers.values())
    resumable = status.get("pending_actions") or any(row.get("failure_kind") == "provider_limit"
                      for row in status.get("waiting_actions", {}).values())
    if status.get("status") == "waiting" and provider_due and resumable:
        return {"outcome": "startable", "before": status, "reason": "provider re-observation due"}
    if status.get("status") == "waiting" and status.get("research_wake_reasons"):
        return {"outcome": "startable", "before": status, "reason": "research reconsideration due",
                "research_wake_reasons": status["research_wake_reasons"]}
    if status.get("status") not in {"ready", "running", "capacity_waiting"}:
        return {"outcome": "not_started", "before": status}
    return {"outcome": "startable", "before": status}


def reconcile_wake(repository: Path, instance: str, workspace: Path, *, config: dict, status: dict) -> dict:
    """Repair a missing/stale one-shot reservation before invoking any model."""
    marker = _operator_dir(workspace) / "wake-registration.json"
    previous = _load_json(marker)
    held = (_operator_dir(workspace) / "HOLD.json").exists() or status.get("user_pause") or status.get("status") in {"paused", "closed", "completed"}
    _, state, runtime = ResearchRepository(repository, instance).load()
    from .session_slots import SessionSlots
    providers = SessionSlots(runtime, state, observer=True).provider_snapshot()["providers"]
    waits = [row for row in providers.values() if row["state"] == "waiting"]
    if held or not config.get("operator_enabled", True) or not waits:
        if previous:
            schedule("cancel-wake", repository=repository, instance=instance, workspace=workspace)
            marker.unlink(missing_ok=True)
        return {"status": "held" if held else "not_needed"}
    row = min(waits, key=lambda value: timestamp(value["retry_at"]))
    key = row["provider"] + ":" + str(row["generation"])
    wanted = {"key": key, "retry_at": row["retry_at"]}
    observed = schedule("status", repository=repository, instance=instance, workspace=workspace)
    actual = observed.get("wake")
    future_trigger = actual and (timestamp(actual.get("next_run")) or 0) > datetime.now(timezone.utc).timestamp()
    running = (observed.get("engine") or {}).get("state") == "Running" or (actual or {}).get("state") == "Running"
    if previous == wanted and actual and actual.get("description") == key and (future_trigger or running):
        return {"status": "scheduled", **wanted}
    schedule("schedule-wake", repository=repository, instance=instance, workspace=workspace,
             wake_at=row["retry_at"], wake_key=key)
    _json(marker, wanted)
    return {"status": "scheduled", **wanted}


def wake(repository: Path, instance: str, workspace: Path) -> dict:
    """No model ping: wake only the engine entry point with its usual guards."""
    guard = engine_start_guard(repository, instance, workspace)
    if guard["outcome"] != "startable":
        return guard
    scheduled = schedule("start-engine", repository=repository, instance=instance, workspace=workspace)
    return {"outcome": "engine_requested", "schedule": scheduled, "before": guard["before"]}


def check(repository: Path, instance: str, workspace: Path, *, probe: bool = False) -> dict[str, Any]:
    """Model-free supervision; preserved engine failure or accepted defect diagnosis opens recovery."""
    if (_operator_dir(workspace) / "HOLD.json").exists():
        return {"outcome": "held"}
    try:
        status = read_status(repository, instance)
    except Exception as error:
        failure = {"outcome": "recovery_required", "kind": "engine_unavailable",
                   "error_type": type(error).__name__, "error": str(error),
                   "observed_at": datetime.now(timezone.utc).isoformat()}
        _json(_operator_dir(workspace) / "engine-failure.json", failure)
        if probe:
            return failure
        return recovery(repository, instance, workspace, failure=failure)
    _, state, runtime = ResearchRepository(repository, instance).load()
    config = state["config"]
    if not config.get("operator_enabled", True):
        return {"outcome": "disabled"}
    if status.get("user_pause") or status.get("status") in {"paused", "closed", "completed"}:
        return {"outcome": status.get("status", "paused"), "status": status}
    if status.get("model_policy_violation"):
        return {"outcome": "model_policy_waiting", "status": status}
    if runtime.get("stop_requested") == "conversation_lost" and state.get("conversation_loss_policy") == "pause":
        return {"outcome": "user_paused", "status": status}
    from .repair_execution import pending_installation_repair, installation_failure
    pending = pending_installation_repair(runtime)
    if pending:
        failure = installation_failure(runtime, pending)
        if probe:
            return {'outcome': 'installation_repair_pending', 'failure': failure, 'model_called': False}
        return recovery(repository, instance, workspace, failure=failure)
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
    wake_status = reconcile_wake(repository, instance, workspace, config=config, status=status)
    guard = engine_start_guard(repository, instance, workspace, status=status)
    if guard["outcome"] != "startable":
        return {**guard, "provider_wake": wake_status, "model_called": False}
    observed = schedule("status", repository=repository, instance=instance, workspace=workspace)
    if (observed.get("engine") or {}).get("state") == "Running":
        return {"outcome": "engine_running", "model_called": False}
    started = schedule("start-engine", repository=repository, instance=instance, workspace=workspace)
    return {"outcome": "engine_requested", "schedule": started, "provider_wake": wake_status, "model_called": False}


def recovery(repository: Path, instance: str, workspace: Path, *, failure: dict) -> dict:
    """Failure-only installation repair under the engine's writer lock.

    Repair retains the already adopted operator authority. Instruction scope is
    explicit; it is not an OS sandbox. Research and user decisions are unchanged.
    """
    from .execution_profiles import (select_profile, profile_ref, capability_evidence, prepare_prompt,
                                     prompt_seal, execution_observation)
    from .session_slots import SessionSlots, _lock, _unlock
    from .repository import new_id
    from .git_store import GitStateStoreLockError
    from . import activities, execution_lifecycle
    if failure.get("kind") not in {"engine_unavailable", "installation_defect"} or not failure.get("error"):
        raise ValueError("recovery requires preserved engine failure evidence")
    if (_operator_dir(workspace) / "HOLD.json").exists():
        return {"outcome": "held"}
    repo = ResearchRepository(repository, instance)
    register_profile_families(repo)
    try:
        with repo.writer_lock():
            head, state, runtime = repo.load()
            config = state["config"]
            if not config.get("operator_enabled", True):
                return {"outcome": "recovery_disabled", "failure": failure}
            if (runtime.get("user_pause") or runtime.get("status") in {"paused", "closed", "completed"}
                    or (_operator_dir(workspace) / "HOLD.json").exists()):
                return {"outcome": "held"}
            from .repair_execution import installation_failure, installation_fingerprint, resume_installation_repair
            diagnosis = None
            if failure['kind'] == 'installation_defect':
                diagnosis = runtime.get('operational_dispositions', {}).get(failure.get('diagnosis_id'))
                if diagnosis is None or installation_failure(runtime, diagnosis) != failure:
                    raise ValueError('installation diagnosis is missing or differs from its published record')
            from .windows_job import named_job_empty
            for execution in runtime.get("executions", {}).values():
                if execution.get("status") == "ended":
                    continue
                process = execution.get("capacity", {}).get("process") or execution.get("process")
                if not process or not process.get("job_name") or named_job_empty(process["job_name"]) is not True:
                    return {"outcome": "recovery_waiting", "reason": "existing execution termination is unconfirmed",
                            "execution_id": execution["id"]}
            maintenance = _lock(repo._store._git_dir / "do-math-installation-maintenance.lock")
            if maintenance is None:
                return {"outcome": "recovery_waiting", "reason": "installation maintenance is already active"}
            try:
                installation_sha256 = installation_fingerprint(LIVE_INSTALLATION_ROOT)
                identity_fields = ('kind', 'diagnosis_id', 'error', 'repair_target', 'verification',
                    'target_execution_id', 'evidence_refs', 'installation_sha256', 'evidence_path', 'engine_run_directory')
                failure_identity = hashlib.sha256(json.dumps({key: failure[key] for key in identity_fields if key in failure},
                    ensure_ascii=False, sort_keys=True).encode('utf-8')).hexdigest()
                if diagnosis:
                    failure_identity = failure['failure_sha256']
                # One automatic attempt per actual failure and installation edition.
                if any(e.get('role') == 'recovery'
                        and e.get('input_manifest', {}).get('repair_identity') == {
                            'failure_sha256': failure_identity, 'installation_sha256': installation_sha256}
                        for e in runtime.get('executions', {}).values()):
                    return {'outcome': 'recovery_waiting', 'reason': 'same failure and installation already attempted'}
                chosen = selection(config, {"role": "independent_operator"}, {}, {})
                profile = select_profile(state["execution_profiles"], {"role": "recovery"}, chosen,
                                         allowed_refs=state["role_profile_refs"]["recovery"])
                from .initialization import adapter_for, capability_requirements
                adapter = adapter_for(profile)
                reference = profile_ref(profile)
                checked_at = datetime.now(timezone.utc).isoformat()
                capability = capability_requirements(state, reference,
                    current_identity=adapter.capability_identity(), at=checked_at)
                if not capability["satisfied"]:
                    description = adapter.describe()  # CLI version/help only; never a model call.
                    description.setdefault("identity", adapter.capability_identity())
                    evidence = capability_evidence(profile, description, observed_at=checked_at)
                    state.setdefault("capability_evidence", {})[evidence["id"]] = evidence
                    head = repo.save_with_state(head, state, runtime)[0]
                    capability = capability_requirements(state, reference,
                        current_identity=adapter.capability_identity(), at=datetime.now(timezone.utc).isoformat())
                if not capability["satisfied"]:
                    return {"outcome": "recovery_waiting", "reason": "profile_capability_unavailable",
                            "capability": capability}
                eid = new_id("EX")
                owner = {"kind": "installation_recovery", "failure_sha256": hashlib.sha256(
                    json.dumps(failure, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()}
                activity = next((a for a in runtime.get("activities", {}).values()
                                 if a.get("owner_ref") == owner and a.get("status") != "finished"), None)
                at = datetime.now(timezone.utc).isoformat()
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
                for index, reference in enumerate(failure.get('evidence_refs', [])):
                    raw = repo.read(reference, head)
                    local = execution_workspace / 'input' / f'failure-{index}.json'
                    local.parent.mkdir(exist_ok=True)
                    local.write_bytes(raw)
                    failure_inputs.append({'artifact_ref': reference, 'local_path': str(local),
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
                                  "instance": instance, "execution_id": eid, "profile_ref": profile_ref(profile)}, ensure_ascii=False))
                prompt = prepare_prompt(prompt, profile)
                sealed_input = prompt_seal(prompt)
                if sealed_input["bytes"] > profile["input"]["max_input_bytes"]:
                    return {"outcome": "recovery_waiting", "reason": "input_overflow", "prompt": sealed_input}
                (run_directory / "input.txt").write_bytes(prompt.encode("utf-8"))
                execution = execution_lifecycle.create_execution(execution_id=eid, owner_activity_id=aid,
                    actor_kind="ai", input_manifest={"failure": failure, "prompt": sealed_input,
                        'repair_identity': {'failure_sha256': failure_identity, 'installation_sha256': installation_sha256},
                        "repair_authority": {"source": "adopted_operator_repair_scope", "boundary": "instructions"}},
                    profile_ref=profile_ref(profile), created_at=at,
                    context_origin=activity["assigned_execution_ids"][-1:])
                execution.update(role="recovery", budget_kind="operations")
                execution_lifecycle.transition_execution(execution, "starting", at=at)
                slots = SessionSlots(runtime, state)
                if not slots.acquire(eid, "operations", chosen["model"], profile=profile, execution=execution):
                    return {"outcome": "recovery_waiting", "reason": slots.admission_reason,
                            "wait": deepcopy(slots.admission_wait)}
                activities.assign_execution(runtime, aid, execution)
                head = repo.save_with_state(head, state, runtime)[0]
                def on_started(identity):
                    nonlocal head
                    slots.started(eid, identity)
                    execution_lifecycle.transition_execution(runtime["executions"][eid], "running",
                        at=datetime.now(timezone.utc).isoformat())
                    head = repo.save_with_state(head, state, runtime)[0]
                try:
                    result = ModelRunner().run(prompt=prompt, output_schema=repair_report_schema(diagnosed=diagnosis is not None),
                        workspace=execution_workspace, evidence_dir=run_directory / "evidence",
                        model=chosen["model"], effort=profile["ai"]["effort"],
                        timeout_seconds=profile["window"]["call_timeout_seconds"],
                        execution_id=eid, profile=profile, input_seal=sealed_input, on_started=on_started,
                        should_stop=lambda: (_operator_dir(workspace) / "HOLD.json").exists())
                    execution = runtime["executions"][eid]
                    _json(run_directory / "runner-result.json", result)
                    # Opaque provider decimals stay in transport JSON, never
                    # silently rounded into the integer-only state contract.
                    execution["runner"] = {"status": result["status"], "evidence_ref": str(run_directory / "runner-result.json")}
                    if result.get("output") is not None:
                        execution["output"] = result["output"]
                    execution["error"] = result.get("error")
                    observation = execution_observation(result)
                    if observation is not None:
                        execution["provider_observation"] = observation
                    if result.get("capability_evidence"):
                        evidence = result["capability_evidence"]
                        state.setdefault("capability_evidence", {})[evidence["id"]] = evidence
                    outcome = "repaired" if result.get("status") == "completed" else "recovery_failed"
                    if outcome == 'repaired' and diagnosis:
                        regression = collect_repair_verification(result.get('output'), execution_workspace)
                        _json(run_directory / 'regression-evidence.json', {'files': regression})
                    if outcome == "repaired":
                        execution["submission_receipt"] = {
                            "kind": "recovery_report", "state": "accepted", "execution_id": eid,
                            "receiver": "recovery_launcher", "observed_at": datetime.now(timezone.utc).isoformat(),
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
                            or runtime.get('user_pause') or runtime.get('status') in {'paused', 'closed', 'completed'}):
                        outcome = 'recovery_held'
                except Exception as error:
                    outcome = "recovery_failed"
                    execution = runtime["executions"][eid]
                    execution["error"] = {"type": type(error).__name__, "message": str(error)}
                finally:
                    # save() may rebuild dictionary objects; always update the loaded view.
                    execution = runtime["executions"][eid]
                    released = slots.release(eid)
                    if not released:
                        outcome = "recovery_termination_unknown"
                    ended_at = datetime.now(timezone.utc).isoformat()
                    execution_lifecycle.transition_execution(execution, "stopping", at=ended_at,
                        stop_phase="terminating", reason=outcome)
                    if released:
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
                _unlock(maintenance)
    except GitStateStoreLockError:
        return {"outcome": "engine_running", "model_called": False}
    if report["outcome"] == "repaired":
        # Restart only after both locks have been released; never wait holding capacity.
        _json(_operator_dir(workspace) / "latest-engine.json", {
            "outcome": "recovery_verified", "recovery_report": str(Path(report["run_directory"]) / "result.json")})
        report["restart"] = wake(repository, instance, workspace)
    return report


def register_profile_families(repository):
    from .execution_profiles import register_families
    register_families(repository.contract)


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


if __name__ == "__main__":
    raise SystemExit(main())
