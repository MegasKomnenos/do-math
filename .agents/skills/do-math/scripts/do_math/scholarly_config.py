"""Resolve the scholarly-MCP server from the nearest Codex configuration file (layer 2).

The shape rules are in ``scholarly``. ``codex_home`` is the entry point's
CODEX_HOME (or ``~/.codex``); a missing value falls back to the environment.
"""
from __future__ import annotations

from pathlib import Path
import tomllib
from typing import Any

from .migration_defaults import codex_home_or_default
from .scholarly import _pathlike, _validate, validate_scholarly_server


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


def resolve_scholarly_server(explicit: dict[str, Any] | None, *, start: Path, codex_home: Path | None = None) -> dict[str, Any] | None:
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
    code_home = codex_home_or_default(codex_home)
    candidate = code_home / "config.toml"
    if candidate.resolve(strict=False) not in checked and candidate.is_file():
        return _from_config(candidate)
    return None
