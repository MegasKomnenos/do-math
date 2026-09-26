"""Run Claude print mode using local login and preserve its native event stream.

The collector derives the final response from the preserved stream; this
worker only runs the CLI and records its status.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import sys

try:
    from do_math.codex_worker import _ENV_ALLOWLIST, check_common_request, run_cli, validate_execution_binding
    from do_math.control_transport import CONTROL_SERVER, ControlTransport
    from do_math.file_io import unique_pairs
    from do_math.scholarly import validate_scholarly_server
except ModuleNotFoundError:  # Direct Python worker inside the Windows Job.
    from codex_worker import _ENV_ALLOWLIST, check_common_request, run_cli, validate_execution_binding
    from control_transport import CONTROL_SERVER, ControlTransport
    from file_io import unique_pairs
    from scholarly import validate_scholarly_server


def sanitized_environment(source=None):
    allowed = (_ENV_ALLOWLIST - {"CODEX_HOME"}) | {"CLAUDE_CONFIG_DIR", "CLAUDE_CODE_GIT_BASH_PATH"}
    return {k: v for k, v in (os.environ if source is None else source).items() if k.upper() in allowed}


def load_request(path: Path) -> dict:
    request = check_common_request(json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_pairs),
                                   required=frozenset({"claude_path"}),
                                   optional=frozenset({"claude_only_assigned_model"}))
    if "output_schema_path" not in request and "control_binding" not in request:
        raise ValueError("an unbound Claude worker requires its structured final schema")
    if request["effort"] not in {"low", "medium", "high", "xhigh", "max"}:
        raise ValueError("Claude effort must be low, medium, high, xhigh or max")
    if not isinstance(request.get("claude_only_assigned_model", False), bool):
        raise ValueError("claude_only_assigned_model must be a boolean")
    if request.get("claude_only_assigned_model") and not request["model"].startswith("claude-"):
        raise ValueError("claude_only_assigned_model requires a full Claude model ID")
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
        servers[CONTROL_SERVER] = ControlTransport.mcp_server_config(request["control_binding"])
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
        schema = json.loads(Path(request["output_schema_path"]).read_text(encoding="utf-8"), object_pairs_hook=unique_pairs)
        if schema.get("$schema") == "https://json-schema.org/draft/2020-12/schema":
            schema.pop("$schema")
        schema.pop("x-contract-id", None)
        argv.extend(["--json-schema", json.dumps(schema, ensure_ascii=False)])
    return argv


def run(request_path: Path) -> int:
    request = load_request(request_path)
    return run_cli(request_path, request, build_argv(request), sanitized_environment())


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: claude_worker.py REQUEST.json")
    raise SystemExit(run(Path(sys.argv[1])))
