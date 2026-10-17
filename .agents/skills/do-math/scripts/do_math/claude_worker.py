"""Run Claude print mode using local login and preserve its native event stream.

The collector derives the final response from the preserved stream; this
worker only runs the CLI and records its status.
"""
from __future__ import annotations

from pathlib import Path
import subprocess
import sys

try:
    from do_math.cli_worker import allowed_environment, argv_inputs, run_cli
    from do_math.worker_request import check_claude_request, claude_argv
    from do_math.values import strict_json_loads
except ModuleNotFoundError:  # pragma: no cover - T4 boundary.test_provider_worker_roots owns bare imports in LocalCLIAdapter's direct Python root.
    from cli_worker import allowed_environment, argv_inputs, run_cli
    from worker_request import check_claude_request, claude_argv
    from values import strict_json_loads


def sanitized_environment(source=None):
    return allowed_environment(source, frozenset({"CLAUDE_CONFIG_DIR", "CLAUDE_CODE_GIT_BASH_PATH"}))


def load_request(path: Path) -> dict:
    return check_claude_request(strict_json_loads(path.read_text(encoding="utf-8")))


def build_argv(request: dict) -> list[str]:
    """The Claude print command for a request ``load_request`` has checked."""
    control, data_dir = argv_inputs(request)
    schema = (strict_json_loads(Path(request["output_schema_path"]).read_text(encoding="utf-8"))
              if "output_schema_path" in request else None)
    return claude_argv(request, control=control, data_dir=data_dir, schema=schema)


def run(request_path: Path, *, spawn=subprocess.Popen) -> int:
    """Run the checked request's Claude command; ``spawn`` starts it (``subprocess.Popen``'s shape)."""
    request = load_request(request_path)
    return run_cli(request_path, request, build_argv(request), sanitized_environment(), spawn=spawn)


if __name__ == "__main__":  # pragma: no cover - T4 boundary.test_provider_worker_roots checks usage and REQUEST dispatch in a fresh interpreter.
    if len(sys.argv) != 2:
        raise SystemExit("usage: claude_worker.py REQUEST.json")
    raise SystemExit(run(Path(sys.argv[1])))
