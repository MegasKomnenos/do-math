"""Run Claude print mode using local login and preserve its native event stream."""
from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys

try:
    from do_math.codex_worker import _ENV_ALLOWLIST, _pairs, _write_status, validate_execution_binding, ControlTransport
    from do_math.scholarly import validate_scholarly_server
    from do_math.claude_stream import parse_stream
except ModuleNotFoundError:  # Direct Python worker inside the Windows Job.
    from codex_worker import _ENV_ALLOWLIST, _pairs, _write_status, validate_execution_binding, ControlTransport
    from scholarly import validate_scholarly_server
    from claude_stream import parse_stream


def sanitized_environment(source=None):
    allowed = (_ENV_ALLOWLIST - {"CODEX_HOME"}) | {"CLAUDE_CONFIG_DIR", "CLAUDE_CODE_GIT_BASH_PATH"}
    return {k: v for k, v in (os.environ if source is None else source).items() if k.upper() in allowed}


def load_request(path: Path) -> dict:
    request = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_pairs)
    required = {"claude_path", "prompt_path", "cwd", "model", "effort",
                "max_runtime_seconds", "stdout_path", "stderr_path", "final_path", "status_path"}
    optional = {"output_schema_path", "scholarly_server", "claude_only_assigned_model", "execution_id", "profile_ref", "control_binding", "resource_limits"}
    if not isinstance(request, dict) or set(request) - required - optional or required - set(request):
        raise ValueError("Claude worker request fields differ from the execution contract")
    validate_execution_binding(request)
    if "output_schema_path" not in request and "control_binding" not in request:
        raise ValueError("an unbound Claude worker requires its structured final schema")
    strings = (required - {"max_runtime_seconds"}) | ({"output_schema_path"} & set(request))
    for key in strings:
        if not isinstance(request[key], str) or not request[key].strip() or "\0" in request[key]:
            raise ValueError(key + " must be a nonempty NUL-free string")
    if request["effort"] not in {"low", "medium", "high", "xhigh", "max"}:
        raise ValueError("Claude effort must be low, medium, high, xhigh or max")
    if not isinstance(request.get("claude_only_assigned_model", False), bool):
        raise ValueError("claude_only_assigned_model must be a boolean")
    if request.get("claude_only_assigned_model") and not request["model"].startswith("claude-"):
        raise ValueError("claude_only_assigned_model requires a full Claude model ID")
    timeout = request["max_runtime_seconds"]
    if timeout is not None and (isinstance(timeout, bool) or not isinstance(timeout, (int, float))
            or not math.isfinite(timeout) or timeout <= 0):
        raise ValueError("max_runtime_seconds must be positive and finite or null")
    if request.get("scholarly_server") is not None:
        request["scholarly_server"] = validate_scholarly_server(request["scholarly_server"])
    return request


def build_argv(request: dict) -> list[str]:
    validate_execution_binding(request)
    settings = {"disableAllHooks": True, "autoMemoryEnabled": False}
    if request.get("claude_only_assigned_model", False):
        model = request["model"]
        settings.update(availableModels=[model], fallbackModel=[], switchModelsOnFlag=False,
                        env={"ANTHROPIC_DEFAULT_HAIKU_MODEL": model,
                             "CLAUDE_CODE_SUBAGENT_MODEL": model,
                             "CLAUDE_CODE_SUBAGENT_MODEL_FORCE": "1"})
    servers = {}
    if "control_binding" in request:
        servers["execution_control"] = ControlTransport.mcp_server_config(request["control_binding"])
    if request.get("scholarly_server") is not None:
        server = validate_scholarly_server(request["scholarly_server"])
        servers["scholarly"] = {**server, "args": [*server["args"], "--data-dir",
                                                  str(Path(request["cwd"]).resolve() / "scholarly-data")]}
    # Keep subscription login; --bare deliberately disables OAuth login.
    argv = [request["claude_path"], "--print", "--output-format", "stream-json", "--verbose",
            "--model", request["model"], "--effort", request["effort"],
            "--no-session-persistence", "--setting-sources", "",
            "--settings", json.dumps(settings),
            "--disable-slash-commands", "--disallowedTools", "Agent,Task",
            "--strict-mcp-config", "--mcp-config", json.dumps({"mcpServers": servers}, ensure_ascii=False),
            "--permission-mode", "bypassPermissions"]
    if "output_schema_path" in request:
        schema = json.loads(Path(request["output_schema_path"]).read_text(encoding="utf-8"), object_pairs_hook=_pairs)
        if schema.get("$schema") == "https://json-schema.org/draft/2020-12/schema":
            schema.pop("$schema")
        schema.pop("x-contract-id", None)
        argv.extend(["--json-schema", json.dumps(schema, ensure_ascii=False)])
    return argv


def run(request_path: Path) -> int:
    request = load_request(request_path)
    prompt = Path(request["prompt_path"]).read_bytes()
    schema = Path(request["output_schema_path"]).read_bytes() if "output_schema_path" in request else None
    command = build_argv(request)
    status = {"state": "starting", "cli_exit_code": None,
              "argv_sha256": hashlib.sha256("\0".join(command).encode()).hexdigest(),
              "request_sha256": hashlib.sha256(request_path.read_bytes()).hexdigest(),
              "stdin_sha256": hashlib.sha256(prompt).hexdigest(),
              "schema_sha256": hashlib.sha256(schema).hexdigest() if schema is not None else None}
    status.update({key: request[key] for key in ("execution_id", "profile_ref") if key in request})
    environment = sanitized_environment()
    temporary = Path(request["cwd"]) / ".scratch" / ".execution-temp"
    temporary.mkdir(parents=True, exist_ok=True)
    environment.update(TEMP=str(temporary.resolve()), TMP=str(temporary.resolve()))
    stdout_path, stderr_path = Path(request["stdout_path"]), Path(request["stderr_path"])
    for path in (stdout_path, stderr_path):
        path.parent.mkdir(parents=True, exist_ok=True)
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
        if status["state"] == "exited" and status["cli_exit_code"] == 0:
            parsed = parse_stream(stdout_path.read_bytes(), require_structured_output=schema is not None)
            if parsed["parse_complete"] and parsed["turn_completed"]:
                final = (parsed["final_text"] if "final_text" in parsed else
                         json.dumps(parsed["structured_output"], ensure_ascii=False, allow_nan=False))
                Path(request["final_path"]).write_bytes(final.encode("utf-8"))
                status["selected_result"] = parsed["selected_result"]
    except Exception as exc:
        status.update(state="worker_error", error_type=type(exc).__name__, error=str(exc))
    _write_status(Path(request["status_path"]), status)
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: claude_worker.py REQUEST.json")
    raise SystemExit(run(Path(sys.argv[1])))
