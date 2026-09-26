"""Execute one ``codex exec`` request without a shell or API-key fallback.

Both CLI workers are direct Python roots inside their Windows Job and share
this module: the common request checks and the process skeleton live here.
"""
from __future__ import annotations

import json
import hashlib
import math
import os
from pathlib import Path
import subprocess
import sys
from typing import Any, Mapping

try:  # This module is also the direct ``python codex_worker.py`` Job root.
    from do_math.scholarly import validate_scholarly_server
    from do_math.control_transport import CONTROL_SERVER, ControlTransport
    from do_math.file_io import compact_json_bytes, is_sha256, unique_pairs, write_bytes_atomic
except ModuleNotFoundError:  # pragma: no cover - exercised by the direct-script regression.
    from scholarly import validate_scholarly_server
    from control_transport import CONTROL_SERVER, ControlTransport
    from file_io import compact_json_bytes, is_sha256, unique_pairs, write_bytes_atomic


# Request fields every worker binds to its status, and the collector compares.
STATUS_BINDING_KEYS = ("execution_id", "profile_ref")
COMMON_REQUIRED = frozenset({"prompt_path", "cwd", "model", "effort", "max_runtime_seconds",
                             "stdout_path", "stderr_path", "status_path"})
COMMON_OPTIONAL = frozenset({"output_schema_path", "scholarly_server", "execution_id", "profile_ref",
                             "control_binding", "resource_limits"})
_EFFORTS = frozenset({"minimal", "low", "medium", "high", "xhigh", "max", "ultra"})
_SANDBOXES = frozenset({"read-only", "workspace-write", "danger-full-access"})
_WINDOWS_SANDBOXES = frozenset({"unelevated", "elevated"})
_ENV_ALLOWLIST = frozenset({"PATH", "SYSTEMROOT", "WINDIR", "COMSPEC", "PATHEXT", "TEMP", "TMP", "HOME",
                            "USERPROFILE", "APPDATA", "LOCALAPPDATA", "PROGRAMDATA", "PROGRAMFILES",
                            "PROGRAMFILES(X86)", "COMMONPROGRAMFILES", "CODEX_HOME", "OS", "HOMEDRIVE", "HOMEPATH"})


def sanitized_environment(source: Mapping[str, str] | None = None) -> dict[str, str]:
    """Keep ChatGPT login state while preventing a CLI API-key route."""
    return {key: value for key, value in (os.environ if source is None else source).items()
            if key.upper() in _ENV_ALLOWLIST}


def validate_execution_binding(request):
    fields = {"execution_id", "profile_ref", "control_binding", "resource_limits"}
    if not fields.intersection(request):
        return
    ref = request.get("profile_ref")
    if (not isinstance(request.get("execution_id"), str) or not request["execution_id"].strip()
            or not isinstance(ref, dict) or set(ref) != {"id", "revision", "sha256"}
            or not isinstance(ref["id"], str) or not ref["id"]
            or type(ref["revision"]) is not int or ref["revision"] < 1
            or not is_sha256(ref["sha256"])):
        raise ValueError("worker execution binding requires exact execution_id and profile_ref")
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


def load_request(path: Path) -> dict[str, Any]:
    value = check_common_request(json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_pairs),
                                 required=frozenset({"codex_path", "approval_policy", "sandbox", "final_path"}),
                                 optional=frozenset({"windows_sandbox"}))
    if value["effort"] not in _EFFORTS or value["approval_policy"] != "never":
        raise ValueError("unsupported effort or approval policy")
    if value["sandbox"] not in _SANDBOXES:
        raise ValueError("a supported sandbox is required")
    if "windows_sandbox" in value and value["windows_sandbox"] not in _WINDOWS_SANDBOXES:
        raise ValueError("windows_sandbox must be elevated or unelevated when present")
    return value


def build_argv(request: Mapping[str, Any]) -> list[str]:
    """Use only documented non-interactive flags and a stdin prompt sentinel."""
    validate_execution_binding(request)
    argv = [request["codex_path"], "--ask-for-approval", request["approval_policy"], "exec",
            "--json", "--color", "never", "--output-last-message", request["final_path"],
            "--model", request["model"], "--cd", request["cwd"],
            "--strict-config", "--config", 'model_reasoning_effort="' + request["effort"] + '"',
            "--config", "project_doc_max_bytes=0",
            "--ephemeral", "--ignore-user-config", "--ignore-rules", "--skip-git-repo-check"]
    if "output_schema_path" in request:
        argv.extend(["--output-schema", request["output_schema_path"]])
    if "windows_sandbox" in request:
        argv.extend(["--config", 'windows.sandbox="' + request["windows_sandbox"] + '"'])
    if "control_binding" in request:
        control = ControlTransport.mcp_server_config(request["control_binding"])
        argv.extend(["--config", f"mcp_servers.{CONTROL_SERVER}.command=" + json.dumps(control["command"], ensure_ascii=False),
                     "--config", f"mcp_servers.{CONTROL_SERVER}.args=" + json.dumps(control["args"], ensure_ascii=False)])
    scholarly = request.get("scholarly_server")
    if scholarly is not None:
        server = validate_scholarly_server(scholarly)
        data_dir = str((Path(request["cwd"]).resolve() / "scholarly-data"))
        args = [*server["args"], "--data-dir", data_dir]
        argv.extend(["--config", "mcp_servers.scholarly.command=" + json.dumps(server["command"], ensure_ascii=False),
                     "--config", "mcp_servers.scholarly.args=" + json.dumps(args, ensure_ascii=False)])
    argv.extend(["--sandbox", request["sandbox"]])
    return [*argv, "-"]


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


def run(request_path: Path) -> int:
    request = load_request(request_path)
    return run_cli(request_path, request, build_argv(request), sanitized_environment())


def main(argv: list[str] | None = None) -> int:
    arguments = sys.argv[1:] if argv is None else argv
    if len(arguments) != 1:
        raise SystemExit("usage: codex_worker.py REQUEST.json")
    return run(Path(arguments[0]))


if __name__ == "__main__":
    raise SystemExit(main())
