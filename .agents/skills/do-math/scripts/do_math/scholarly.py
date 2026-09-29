"""The closed scholarly-MCP server shape for isolated Codex executions (layer 1).

Workers load this module without the package inside their Windows Job; the
configuration-file resolution is in ``scholarly_config``.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any


def _pathlike(value: str) -> bool:
    return "/" in value or "\\" in value or bool(Path(value).suffix)


def _validate(value: dict[str, Any], *, allow_relative_paths: bool) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != {"command", "args"}:
        raise ValueError("scholarly server must contain exactly command and args")
    command, args = value["command"], value["args"]
    if not isinstance(command, str) or not command or "\x00" in command:
        raise ValueError("scholarly command must be a nonempty NUL-free string")
    if not isinstance(args, list) or any(not isinstance(arg, str) or "\x00" in arg for arg in args):
        raise ValueError("scholarly args must be NUL-free strings")
    if any(arg == "--data-dir" or arg.startswith("--data-dir=") for arg in args):
        raise ValueError("scholarly args must not override the execution data directory")
    if not allow_relative_paths:
        if _pathlike(command) and not Path(command).is_absolute():
            raise ValueError("relative scholarly command needs a configuration-file base")
        if args and _pathlike(args[0]) and not Path(args[0]).is_absolute():
            raise ValueError("relative scholarly server file needs a configuration-file base")
    return {"command": command, "args": list(args)}


def validate_scholarly_server(value: dict[str, Any]) -> dict[str, Any]:
    """Validate a command/args pair that has no configuration-file base."""
    return _validate(value, allow_relative_paths=False)
