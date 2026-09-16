"""Generic Windows scheduled operator for one do-math research instance.

The operator writes only local operational evidence.  Research state changes
remain commands through the CLI, which in turn uses the engine's writer lock.
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

from .repository import ResearchRepository
from .model_runner import CodexModelRunner


SCRIPTS = Path(__file__).resolve().parents[1]
SKILL_ROOT = SCRIPTS.parent
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


def _json(path: Path, value: dict[str, Any]) -> None:
    from .engine import json_safe
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(json_safe(value), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def _load_json(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    value = json.loads(path.read_text(encoding="utf-8"))
    return value if isinstance(value, dict) else None


def task_names(repository: Path, instance: str) -> dict[str, str]:
    """Return stable task names scoped to the exact repository and instance."""
    digest = hashlib.sha256((str(repository.resolve()) + "\0" + instance).encode("utf-8")).hexdigest()[:12]
    return {"operator": f"DoMath-Operator-{digest}", "engine": f"DoMath-Engine-{digest}"}


def schedule(
    action: str,
    *,
    repository: Path,
    instance: str,
    workspace: Path,
    interval_seconds: int = 7200,
    operator_timeout_seconds: int = 5400,
    engine_timeout_seconds: int = 7510,
    runner: Runner = subprocess.run,
) -> dict[str, Any]:
    """Call the narrow PowerShell scheduler adapter and decode its JSON result."""
    if action not in {"install", "uninstall", "status", "start-engine", "start-operator"}:
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
        "-IntervalSeconds", str(interval_seconds),
        "-OperatorTimeoutSeconds", str(operator_timeout_seconds),
        "-EngineTimeoutSeconds", str(engine_timeout_seconds),
    ]
    completed = runner(command, capture_output=True, text=True, encoding="utf-8", check=False)
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
    guard = engine_start_guard(repository, instance, workspace)
    if guard["outcome"] != "startable":
        return guard
    status = guard["before"]
    run_directory = _operator_dir(workspace) / "engine" / (datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:8])
    run_directory.mkdir(parents=True)
    _json(run_directory / "before.json", status)
    command = [sys.executable, str(ENTRYPOINT), "run", "--repository", str(repository), "--instance", instance]
    record = {"outcome": "running", "before": status, "command": command, "run_directory": str(run_directory)}
    _json(run_directory / "result.json", record)
    try:
        completed = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", check=False)
        (run_directory / "stdout.json").write_text(completed.stdout, encoding="utf-8")
        (run_directory / "stderr.txt").write_text(completed.stderr, encoding="utf-8")
        after = read_status(repository, instance)
        record.update(outcome="completed" if completed.returncode == 0 else "engine_failed", exit_code=completed.returncode, after=after)
    except OSError as error:
        record.update(outcome="engine_failed", error=f"{type(error).__name__}: {error}")
    _json(run_directory / "result.json", record)
    _json(_operator_dir(workspace) / "latest-engine.json", record)
    return record


def engine_start_guard(repository: Path, instance: str, workspace: Path) -> dict[str, Any]:
    """Read the conditions that must hold before either task starts an engine."""
    if (_operator_dir(workspace) / "HOLD.json").exists():
        return {"outcome": "held"}
    status = read_status(repository, instance)
    if status.get("user_pause") or status.get("status") == "paused":
        return {"outcome": "paused", "before": status}
    if status.get("status") not in {"ready", "running"}:
        return {"outcome": "not_started", "before": status}
    return {"outcome": "startable", "before": status}


def check(repository: Path, instance: str, workspace: Path, *, probe: bool = False) -> dict[str, Any]:
    """Run an independent Codex operator and preserve its evidence outside Git state."""
    status = read_status(repository, instance)
    if status.get("status") == "completed" and not probe:
        context = invocation_context(repository, instance, workspace, status)
        run_directory = Path(context["run_directory"])
        run_directory.mkdir(parents=True)
        _json(run_directory / "context.json", context)
        report = {"outcome": "completed", "status": status, "run_directory": str(run_directory),
                  "reason": "current CLI completed state is observed; no periodic operator model was started"}
        result_path = run_directory / "result.json"
        _json(result_path, report)
        _json(_operator_dir(workspace) / "latest-report.json", _latest_report(report, result_path))
        return report
    _, state, _ = ResearchRepository(repository, instance).load()
    from .engine import DEFAULT_CONFIG
    config = {**DEFAULT_CONFIG, **state["config"]}
    scholarly = config.get("scholarly_server") if config.get("scholarly_enabled", True) else None
    context = invocation_context(repository, instance, workspace, status, probe=probe, scholarly_configured=isinstance(scholarly, dict))
    run_directory = Path(context["run_directory"])
    run_directory.mkdir(parents=True)
    _json(run_directory / "context.json", context)
    if (_operator_dir(workspace) / "HOLD.json").exists():
        report = {"outcome": "held", "status": status, "run_directory": str(run_directory)}
        _json(run_directory / "result.json", report)
        _json(_operator_dir(workspace) / "latest-report.json", report)
        return report
    if status.get("user_pause") or status.get("status") == "closed":
        report = {"outcome": "user_paused" if status.get("user_pause") else "closed", "status": status,
                  "run_directory": str(run_directory)}
        _json(run_directory / "result.json", report)
        _json(_operator_dir(workspace) / "latest-report.json", report)
        return report
    if not PROMPT.is_file():
        raise RuntimeError("independent operator contract is missing")
    prompt = PROMPT.read_text(encoding="utf-8") + "\n\n## Invocation context\n\n" + json.dumps(context, ensure_ascii=False, indent=2)
    if probe:
        prompt += "\n\n## Probe restriction\n\nRead status and call scholarly list_sources only when configured. Do not create controls, start the engine, modify code, or change research state."
    (run_directory / "prompt.md").write_text(prompt, encoding="utf-8")
    report = {"outcome": "running", "probe": probe, "status_before": status, "run_directory": str(run_directory)}
    _json(run_directory / "result.json", report)
    last_status_check = 0.0
    stopped = False

    def should_stop() -> bool:
        nonlocal last_status_check, stopped
        if (_operator_dir(workspace) / "HOLD.json").exists():
            stopped = True
            return True
        import time
        if time.monotonic() - last_status_check < 1:
            return stopped
        last_status_check = time.monotonic()
        current = read_status(repository, instance)
        stopped = bool(current.get("user_pause") or current.get("status") == "closed")
        return stopped

    runner = CodexModelRunner()
    (run_directory / "workspace").mkdir()
    try:
        model_result = runner.run(prompt=prompt, output_schema=OPERATOR_SCHEMA, workspace=run_directory / "workspace",
                                  evidence_dir=run_directory / "evidence", model=config["operator_model"],
                                  effort=config["operator_effort"], timeout_seconds=config["operator_timeout_seconds"],
                                  scholarly_server=scholarly if isinstance(scholarly, dict) else None, should_stop=should_stop)
        report.update(outcome="completed" if model_result["status"] == "completed" else model_result["status"],
                      result=model_result, output=model_result.get("output"))
    except Exception as error:
        report.update(outcome="operator_failed", error=f"{type(error).__name__}: {error}")
    report["ended_at"] = datetime.now(timezone.utc).isoformat()
    result_path = run_directory / "result.json"
    _json(result_path, report)
    latest = _latest_report(report, result_path)
    _json(_operator_dir(workspace) / "latest-report.json", latest)
    return latest
