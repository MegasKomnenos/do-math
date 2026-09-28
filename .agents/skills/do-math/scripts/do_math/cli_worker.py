"""The request checks and the process skeleton every CLI worker shares.

Each provider worker (``codex_worker``, ``claude_worker``) is a direct Python
root inside its Windows Job. It checks its request with ``check_common_request``
plus its own fields, builds its provider's argv, and runs it with ``run_cli``.
"""
from __future__ import annotations

import hashlib
import math
import os
from pathlib import Path
import subprocess
from typing import Any, Mapping

try:  # A worker imports this module both as a package module and as a direct Job script.
    from do_math.scholarly import validate_scholarly_server
    from do_math.control_transport import ControlTransport
    from do_math.file_io import compact_json_bytes, validate_profile_ref, write_bytes_atomic
except ModuleNotFoundError:  # pragma: no cover - exercised by the direct-script regressions.
    from scholarly import validate_scholarly_server
    from control_transport import ControlTransport
    from file_io import compact_json_bytes, validate_profile_ref, write_bytes_atomic


# Request fields every worker binds to its status, and the collector compares.
STATUS_BINDING_KEYS = ("execution_id", "profile_ref")
COMMON_REQUIRED = frozenset({"prompt_path", "cwd", "model", "effort", "max_runtime_seconds",
                             "stdout_path", "stderr_path", "status_path"})
COMMON_OPTIONAL = frozenset({"output_schema_path", "scholarly_server", "execution_id", "profile_ref",
                             "control_binding", "resource_limits"})
# Environment names every CLI may keep; a provider adds its own login and configuration names.
ENV_ALLOWLIST = frozenset({"PATH", "SYSTEMROOT", "WINDIR", "COMSPEC", "PATHEXT", "TEMP", "TMP", "HOME",
                           "USERPROFILE", "APPDATA", "LOCALAPPDATA", "PROGRAMDATA", "PROGRAMFILES",
                           "PROGRAMFILES(X86)", "COMMONPROGRAMFILES", "OS", "HOMEDRIVE", "HOMEPATH"})


def allowed_environment(source: Mapping[str, str] | None, extra: frozenset[str]) -> dict[str, str]:
    """Keep the allowed names, and a provider's ``extra`` names, of ``source`` (default: this process)."""
    allowed = ENV_ALLOWLIST | extra
    return {key: value for key, value in (os.environ if source is None else source).items()
            if key.upper() in allowed}


def validate_execution_binding(request):
    fields = {"execution_id", "profile_ref", "control_binding", "resource_limits"}
    if not fields.intersection(request):
        return
    if not isinstance(request.get("execution_id"), str) or not request["execution_id"].strip():
        raise ValueError("worker execution binding requires exact execution_id and profile_ref")
    try:
        validate_profile_ref(request.get("profile_ref"))
    except ValueError:
        raise ValueError("worker execution binding requires exact execution_id and profile_ref") from None
    if "resource_limits" in request:
        try:
            from do_math.windows_job import validate_resource_limits
        except ModuleNotFoundError:
            from windows_job import validate_resource_limits
        if request["resource_limits"] is None:
            raise ValueError("explicit resource limits cannot be null")
        validate_resource_limits(request["resource_limits"])
    if "control_binding" in request:
        ControlTransport.validate_binding(request["control_binding"], execution_id=request["execution_id"],
                                          cwd=request.get("cwd"))


def validate_max_runtime(timeout: Any) -> None:
    """A CLI runtime limit is a positive finite number of seconds, or none."""
    if timeout is not None and (isinstance(timeout, bool) or not isinstance(timeout, (int, float))
            or not math.isfinite(timeout) or timeout <= 0):
        raise ValueError("max_runtime_seconds must be positive and finite or null")


def check_common_request(value: Any, *, required: frozenset, optional: frozenset) -> dict[str, Any]:
    """Check the request fields both workers share, then the provider's extra names."""
    if not isinstance(value, dict):
        raise ValueError("worker request must be an object")
    required, optional = COMMON_REQUIRED | required, COMMON_OPTIONAL | optional
    missing = sorted(required - set(value))
    if missing:
        raise ValueError("worker request misses " + ", ".join(missing))
    unknown = sorted(set(value) - required - optional)
    if unknown:
        raise ValueError("unknown worker request fields: " + ", ".join(unknown))
    validate_execution_binding(value)
    for key in (required - {"max_runtime_seconds"}) | ({"output_schema_path"} & set(value)):
        if not isinstance(value[key], str) or not value[key].strip() or "\0" in value[key]:
            raise ValueError(key + " must be a nonempty NUL-free string")
    validate_max_runtime(value["max_runtime_seconds"])
    if value.get("scholarly_server") is not None:
        value["scholarly_server"] = validate_scholarly_server(value["scholarly_server"])
    return value


def run_cli(request_path: Path, request: Mapping[str, Any], command: list[str],
            environment: dict[str, str]) -> int:
    """Run one CLI with its stdin prompt and record the status the collector checks."""
    prompt = Path(request["prompt_path"]).read_bytes()
    schema = Path(request["output_schema_path"]).read_bytes() if "output_schema_path" in request else None
    stdout_path, stderr_path = Path(request["stdout_path"]), Path(request["stderr_path"])
    for path in (stdout_path, stderr_path):
        path.parent.mkdir(parents=True, exist_ok=True)
    status: dict[str, Any] = {"argv_sha256": hashlib.sha256("\0".join(command).encode("utf-8")).hexdigest(),
                              "state": "starting", "cli_exit_code": None,
                              "request_sha256": hashlib.sha256(request_path.read_bytes()).hexdigest(),
                              "stdin_sha256": hashlib.sha256(prompt).hexdigest(),
                              "schema_sha256": None if schema is None else hashlib.sha256(schema).hexdigest()}
    status.update({key: request[key] for key in STATUS_BINDING_KEYS if key in request})
    temporary = Path(request["cwd"]) / ".scratch" / ".execution-temp"
    temporary.mkdir(parents=True, exist_ok=True)
    environment = {**environment, "TEMP": str(temporary.resolve()), "TMP": str(temporary.resolve())}
    try:
        with stdout_path.open("wb") as stdout, stderr_path.open("wb") as stderr:
            process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=stdout, stderr=stderr,
                                       cwd=request["cwd"], env=environment, shell=False,
                                       creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
            try:
                process.communicate(input=prompt, timeout=request["max_runtime_seconds"])
                status.update(state="exited", cli_exit_code=process.returncode)
            except subprocess.TimeoutExpired:
                process.kill()
                process.communicate()
                status.update(state="timeout", cli_exit_code=process.returncode, runner_stop_required=True)
    except Exception as exc:
        status.update(state="worker_error", error_type=type(exc).__name__, error=str(exc))
    write_bytes_atomic(Path(request["status_path"]), compact_json_bytes(status))
    return 0
