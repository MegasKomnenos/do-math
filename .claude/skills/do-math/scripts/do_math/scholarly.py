"""Closed scholarly-MCP configuration for isolated Codex executions."""
from __future__ import annotations

import os
from pathlib import Path
import tomllib
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


def _absolute_from_config(value: str, base: Path, *, label: str) -> str:
    candidate = Path(value)
    if candidate.is_absolute():
        return value
    resolved = (base / candidate).resolve(strict=False)
    if not resolved.is_file():
        raise ValueError(f"relative scholarly {label} does not name a file beside its configuration")
    return str(resolved)


def _from_config(path: Path) -> dict[str, Any] | None:
    try:
        with path.open("rb") as stream:
            parsed = tomllib.load(stream)
    except tomllib.TOMLDecodeError as error:
        raise ValueError(f"invalid Codex configuration at {path}") from error
    table = parsed.get("mcp_servers")
    entry = table.get("scholarly") if isinstance(table, dict) else None
    if entry is None:
        return None
    if not isinstance(entry, dict):
        raise ValueError("scholarly server configuration must be a table")
    # Codex's server table may also carry client timeout settings. They remain
    # owned by the parent configuration and are deliberately not inherited.
    server = _validate({key: entry.get(key) for key in ("command", "args")}, allow_relative_paths=True)
    if _pathlike(server["command"]) and not Path(server["command"]).is_absolute():
        server["command"] = _absolute_from_config(server["command"], path.parent, label="command")
    if server["args"] and _pathlike(server["args"][0]) and not Path(server["args"][0]).is_absolute():
        server["args"][0] = _absolute_from_config(server["args"][0], path.parent, label="server file")
    return validate_scholarly_server(server)


def resolve_scholarly_server(explicit: dict[str, Any] | None, *, start: Path) -> dict[str, Any] | None:
    """Resolve an explicit server or the nearest project/CODEX_HOME scholarly entry.

    This deliberately reads and returns only the ``mcp_servers.scholarly``
    command/args pair. Relative executable and first server-file arguments are
    resolved against their configuration file. Other arguments remain literals.
    """
    if explicit is not None:
        return validate_scholarly_server(explicit)
    anchor = start if start.is_dir() else start.parent
    checked: set[Path] = set()
    for directory in (anchor, *anchor.parents):
        candidate = directory / ".codex" / "config.toml"
        checked.add(candidate.resolve(strict=False))
        if candidate.is_file():
            resolved = _from_config(candidate)
            if resolved is not None:
                return resolved
    code_home = Path(os.environ["CODEX_HOME"]) if os.environ.get("CODEX_HOME") else Path.home() / ".codex"
    candidate = code_home / "config.toml"
    if candidate.resolve(strict=False) not in checked and candidate.is_file():
        return _from_config(candidate)
    return None
