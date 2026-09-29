"""Execute one ``codex exec`` request without a shell or API-key fallback.

This module is the direct Python root of a Codex call inside its Windows Job.
The request checks and process skeleton it shares with the Claude worker live
in ``cli_worker``.
"""
from __future__ import annotations

from pathlib import Path
import sys
from typing import Any, Mapping

try:  # This module is also the direct ``python codex_worker.py`` Job root.
    from do_math.values import strict_json_loads
    from do_math.cli_worker import allowed_environment, argv_inputs, run_cli
    from do_math.worker_request import check_codex_request, codex_argv
except ModuleNotFoundError:  # pragma: no cover - exercised by the direct-script regression.
    from values import strict_json_loads
    from cli_worker import allowed_environment, argv_inputs, run_cli
    from worker_request import check_codex_request, codex_argv


def sanitized_environment(source: Mapping[str, str] | None = None) -> dict[str, str]:
    """Keep ChatGPT login state while preventing a CLI API-key route."""
    return allowed_environment(source, frozenset({"CODEX_HOME"}))


def load_request(path: Path) -> dict[str, Any]:
    return check_codex_request(strict_json_loads(path.read_text(encoding="utf-8")))


def build_argv(request: Mapping[str, Any]) -> list[str]:
    """The Codex command for a request ``load_request`` has checked."""
    control, data_dir = argv_inputs(request)
    return codex_argv(request, control=control, data_dir=data_dir)


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
