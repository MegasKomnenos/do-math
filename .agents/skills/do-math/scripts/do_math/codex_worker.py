"""Execute one ``codex exec`` request without a shell or API-key fallback.

This module is the direct Python root of a Codex call inside its Windows Job.
The request checks and process skeleton it shares with the Claude worker live
in ``cli_worker``.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any, Mapping

try:  # This module is also the direct ``python codex_worker.py`` Job root.
    from do_math.control_transport import CONTROL_SERVER, ControlTransport
    from do_math.values import strict_json_loads
    from do_math.cli_worker import allowed_environment, check_common_request, run_cli
except ModuleNotFoundError:  # pragma: no cover - exercised by the direct-script regression.
    from control_transport import CONTROL_SERVER, ControlTransport
    from values import strict_json_loads
    from cli_worker import allowed_environment, check_common_request, run_cli


_EFFORTS = frozenset({"minimal", "low", "medium", "high", "xhigh", "max", "ultra"})
_SANDBOXES = frozenset({"read-only", "workspace-write", "danger-full-access"})
_WINDOWS_SANDBOXES = frozenset({"unelevated", "elevated"})


def sanitized_environment(source: Mapping[str, str] | None = None) -> dict[str, str]:
    """Keep ChatGPT login state while preventing a CLI API-key route."""
    return allowed_environment(source, frozenset({"CODEX_HOME"}))


def load_request(path: Path) -> dict[str, Any]:
    value = check_common_request(strict_json_loads(path.read_text(encoding="utf-8")),
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
    """Use only documented non-interactive flags and a stdin prompt sentinel; ``load_request`` checked the request."""
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
    server = request.get("scholarly_server")
    if server is not None:
        data_dir = str((Path(request["cwd"]).resolve() / "scholarly-data"))
        args = [*server["args"], "--data-dir", data_dir]
        argv.extend(["--config", "mcp_servers.scholarly.command=" + json.dumps(server["command"], ensure_ascii=False),
                     "--config", "mcp_servers.scholarly.args=" + json.dumps(args, ensure_ascii=False)])
    argv.extend(["--sandbox", request["sandbox"]])
    return [*argv, "-"]


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
