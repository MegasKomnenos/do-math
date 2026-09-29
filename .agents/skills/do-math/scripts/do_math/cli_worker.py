"""The process skeleton every CLI worker shares (layer 3).

Each provider worker (``codex_worker``, ``claude_worker``) is a direct Python
root inside its Windows Job. It checks its request with
``worker_request.check_common_request`` plus its own fields, builds its
provider's argv, and runs it with ``run_cli``.
"""
from __future__ import annotations

import hashlib
import os
from pathlib import Path
import subprocess
from typing import Any, Mapping

try:  # A worker imports this module both as a package module and as a direct Job script.
    from do_math.control_server import mcp_server_config
    from do_math.file_io import write_bytes_atomic
    from do_math.values import compact_json_bytes
    from do_math.worker_request import STATUS_BINDING_KEYS, allowed_names
except ModuleNotFoundError:  # pragma: no cover - exercised by the direct-script regressions.
    from control_server import mcp_server_config
    from file_io import write_bytes_atomic
    from values import compact_json_bytes
    from worker_request import STATUS_BINDING_KEYS, allowed_names


def allowed_environment(source: Mapping[str, str] | None, extra: frozenset[str]) -> dict[str, str]:
    """Keep the allowed names, and a provider's ``extra`` names, of ``source`` (default: this process)."""
    return allowed_names(os.environ if source is None else source, extra)


def argv_inputs(request: Mapping[str, Any]) -> tuple[dict | None, str | None]:
    """What a worker's argv takes from outside: the control server command and the scholarly data directory."""
    control = mcp_server_config(request["control_binding"]) if "control_binding" in request else None
    data_dir = (str(Path(request["cwd"]).resolve() / "scholarly-data")
                if request.get("scholarly_server") is not None else None)
    return control, data_dir


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
