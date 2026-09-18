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
    from do_math.codex_worker import _ENV_ALLOWLIST, _pairs, _write_status
    from do_math.scholarly import validate_scholarly_server
except ModuleNotFoundError:  # Direct Python worker inside the Windows Job.
    from codex_worker import _ENV_ALLOWLIST, _pairs, _write_status
    from scholarly import validate_scholarly_server


def sanitized_environment(source=None):
    allowed = (_ENV_ALLOWLIST - {"CODEX_HOME"}) | {"CLAUDE_CONFIG_DIR", "CLAUDE_CODE_GIT_BASH_PATH"}
    return {k: v for k, v in (os.environ if source is None else source).items() if k.upper() in allowed}


def load_request(path: Path) -> dict:
    request = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_pairs)
    required = {"claude_path", "prompt_path", "cwd", "model", "effort", "output_schema_path",
                "max_runtime_seconds", "stdout_path", "stderr_path", "final_path", "status_path"}
    if not isinstance(request, dict) or set(request) - required - {"scholarly_server", "claude_only_assigned_model"} or required - set(request):
        raise ValueError("Claude worker request fields differ from the execution contract")
    for key in required - {"max_runtime_seconds"}:
        if not isinstance(request[key], str) or not request[key].strip() or "\0" in request[key]:
            raise ValueError(key + " must be a nonempty NUL-free string")
    if request["effort"] not in {"low", "medium", "high", "xhigh", "max"}:
        raise ValueError("Claude effort must be low, medium, high, xhigh or max")
    if not isinstance(request.get("claude_only_assigned_model", False), bool):
        raise ValueError("claude_only_assigned_model must be a boolean")
    if request.get("claude_only_assigned_model") and not request["model"].startswith("claude-"):
        raise ValueError("claude_only_assigned_model requires a full Claude model ID")
    timeout = request["max_runtime_seconds"]
    if isinstance(timeout, bool) or not isinstance(timeout, (int, float)) or not math.isfinite(timeout) or timeout <= 0:
        raise ValueError("max_runtime_seconds must be positive and finite")
    if request.get("scholarly_server") is not None:
        request["scholarly_server"] = validate_scholarly_server(request["scholarly_server"])
    return request


def build_argv(request: dict) -> list[str]:
    schema = json.loads(Path(request["output_schema_path"]).read_text(encoding="utf-8"), object_pairs_hook=_pairs)
    # Claude CLI does not register the 2020-12 meta-schema or x-contract-id. Our role schemas
    # use the shared keyword subset; keep every constraint and retain the
    # original schema file for the authoritative submission validation.
    if schema.get("$schema") == "https://json-schema.org/draft/2020-12/schema":
        schema.pop("$schema")
    schema.pop("x-contract-id", None)
    settings = {"disableAllHooks": True, "autoMemoryEnabled": False}
    if request.get("claude_only_assigned_model", False):
        model = request["model"]
        settings.update(availableModels=[model], fallbackModel=[], switchModelsOnFlag=False,
                        env={"ANTHROPIC_DEFAULT_HAIKU_MODEL": model,
                             "CLAUDE_CODE_SUBAGENT_MODEL": model,
                             "CLAUDE_CODE_SUBAGENT_MODEL_FORCE": "1"})
    servers = {}
    if request.get("scholarly_server") is not None:
        server = validate_scholarly_server(request["scholarly_server"])
        servers["scholarly"] = {**server, "args": [*server["args"], "--data-dir",
                                                  str(Path(request["cwd"]).resolve() / "scholarly-data")]}
    # Keep subscription login; --bare deliberately disables OAuth login.
    return [request["claude_path"], "--print", "--output-format", "stream-json", "--verbose",
            "--model", request["model"], "--effort", request["effort"],
            "--no-session-persistence", "--setting-sources", "",
            "--settings", json.dumps(settings),
            "--disable-slash-commands", "--disallowedTools", "Agent,Task",
            "--strict-mcp-config", "--mcp-config", json.dumps({"mcpServers": servers}, ensure_ascii=False),
            "--permission-mode", "bypassPermissions",
            "--json-schema", json.dumps(schema, ensure_ascii=False)]


def run(request_path: Path) -> int:
    request = load_request(request_path)
    prompt = Path(request["prompt_path"]).read_bytes()
    schema = Path(request["output_schema_path"]).read_bytes()
    command = build_argv(request)
    status = {"state": "starting", "cli_exit_code": None,
              "argv_sha256": hashlib.sha256("\0".join(command).encode()).hexdigest(),
              "request_sha256": hashlib.sha256(request_path.read_bytes()).hexdigest(),
              "stdin_sha256": hashlib.sha256(prompt).hexdigest(), "schema_sha256": hashlib.sha256(schema).hexdigest()}
    stdout_path, stderr_path = Path(request["stdout_path"]), Path(request["stderr_path"])
    for path in (stdout_path, stderr_path):
        path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with stdout_path.open("wb") as stdout, stderr_path.open("wb") as stderr:
            process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=stdout, stderr=stderr,
                                       cwd=request["cwd"], env=sanitized_environment(), shell=False,
                                       creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
            try:
                process.communicate(input=prompt, timeout=request["max_runtime_seconds"])
                status.update(state="exited", cli_exit_code=process.returncode)
            except subprocess.TimeoutExpired:
                process.kill()
                process.communicate()
                status.update(state="timeout", cli_exit_code=process.returncode, runner_stop_required=True)
        # The collector separately validates stream order, completion and schema.
        if status["state"] == "exited" and status["cli_exit_code"] == 0:
            events = [json.loads(line) for line in stdout_path.read_bytes().splitlines() if line.strip()]
            if events and isinstance(events[-1], dict) and "structured_output" in events[-1]:
                Path(request["final_path"]).write_text(json.dumps(events[-1]["structured_output"], ensure_ascii=False), encoding="utf-8")
    except Exception as exc:
        status.update(state="worker_error", error_type=type(exc).__name__, error=str(exc))
    _write_status(Path(request["status_path"]), status)
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: claude_worker.py REQUEST.json")
    raise SystemExit(run(Path(sys.argv[1])))
