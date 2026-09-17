"""Snapshot-facing research repository operations built on :mod:`git_store`.

This is a byte and JSON access layer.  It does not validate instance/runtime
schemas, select a model, or activate a research instance.
"""

from __future__ import annotations

import base64
from collections.abc import Mapping
from contextlib import AbstractContextManager
import hashlib
import json
import math
import os
from pathlib import Path
import re
import secrets
import time
from typing import Any

from .git_store import GitStateStore


class RepositoryCursorError(ValueError):
    """A query cursor is malformed or bound to another snapshot/query."""


_PREFIX = re.compile(r"[A-Z][A-Z0-9]{0,7}\Z")
_CROCKFORD = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
_SAFE_INTEGER = (1 << 53) - 1
_REPARSE_POINT = 0x00000400


def new_id(prefix: str) -> str:
    """Create a canonical uppercase ULID with the caller's registry prefix."""
    if not isinstance(prefix, str) or not _PREFIX.fullmatch(prefix):
        raise ValueError("prefix must be a canonical uppercase registry prefix")
    value = ((time.time_ns() // 1_000_000) << 80) | int.from_bytes(secrets.token_bytes(10), "big")
    encoded = ""
    for _ in range(26):
        encoded = _CROCKFORD[value & 31] + encoded
        value >>= 5
    return f"{prefix}-{encoded}"


def canonical_json(value: Any) -> bytes:
    """Encode a finite JSON value deterministically, with one terminal LF."""
    _validate_json(value)
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n").encode("utf-8")


class ResearchRepository:
    """Read and publish the two JSON roots of one GitStateStore instance."""

    def __init__(self, repository: Path, instance_id: str) -> None:
        self._store = GitStateStore(repository, instance_id)

    def initialize(self, instance: dict[str, Any], runtime: dict[str, Any]) -> str:
        """Publish the parentless state whose roots are instance and runtime JSON."""
        if self._store.read_snapshot().head is not None:
            raise ValueError("the instance ref already has an initial state")
        snapshot = self._store.publish(None, {
            "research/instance.json": _canonical_object(instance),
            "runtime/state.json": _canonical_object(runtime),
        })
        return snapshot.head

    def load(self, snapshot: str | None = None) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Load both root documents from one explicit or current snapshot."""
        head = self._resolve_snapshot(snapshot)
        roots = self._store.read_many(head, ["research/instance.json", "runtime/state.json"])
        return (
            head,
            _decode_object(roots["research/instance.json"]),
            _decode_object(roots["runtime/state.json"]),
        )

    def save(
        self,
        expected_head: str,
        instance: dict[str, Any],
        runtime: dict[str, Any],
        *,
        artifacts: dict[str, bytes] | None = None,
    ) -> str:
        """CAS-publish both roots and optional new immutable artifact bundles."""
        self._store._validate_oid(expected_head)
        changes: dict[str, bytes] = {
            "research/instance.json": _canonical_object(instance),
            "runtime/state.json": _canonical_object(runtime),
        }
        if artifacts is not None:
            if not isinstance(artifacts, Mapping):
                raise TypeError("artifacts must map full artifact paths to bytes")
            for path, contents in artifacts.items():
                if not isinstance(path, str) or not path.startswith("runtime/artifacts/"):
                    raise ValueError("artifact keys must be full runtime/artifacts/<bundle>/<path> paths")
                if not isinstance(contents, bytes):
                    raise TypeError("artifact values must be bytes")
                changes[path] = contents
        return self._store.publish(expected_head, changes).head

    def read(self, path: str, snapshot: str | None = None) -> bytes:
        """Read bytes from an exact or current state snapshot."""
        return self._store.read_bytes(self._resolve_snapshot(snapshot), path)

    def read_many(self, paths: list[str], snapshot: str | None = None) -> dict[str, bytes]:
        """Read exact blobs together without changing their logical paths."""
        return self._store.read_many(self._resolve_snapshot(snapshot), paths)

    def list_files(self, prefix: str, snapshot: str | None = None) -> list[str]:
        """List files below one POSIX state prefix in stable lexical order."""
        head = self._resolve_snapshot(snapshot)
        normalized_prefix = _validate_prefix(prefix)
        raw = self._git("ls-tree", "-r", "-z", "--name-only", head).stdout.split(b"\0")
        paths: list[str] = []
        for raw_path in raw:
            if not raw_path:
                continue
            path = raw_path.decode("utf-8")
            self._store._validate_path(path)
            if path.startswith(normalized_prefix):
                paths.append(path)
        return sorted(paths)

    def query(
        self,
        *,
        snapshot: str | None = None,
        prefix: str = "research/",
        text: str = "",
        limit: int = 50,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """Return a page bound to one immutable snapshot and textual query.

        Matching includes the POSIX path and UTF-8 query bytes in file contents.
        A fixed-window-like guarantee is not inferred from the current head: a
        cursor always carries the exact commit it was created from.
        """
        normalized_prefix = _validate_prefix(prefix)
        if not isinstance(text, str) or not isinstance(limit, int) or isinstance(limit, bool) or limit <= 0:
            raise ValueError("text must be a string and limit a positive integer")
        last_path: str | None = None
        if cursor is not None:
            payload = _decode_cursor(cursor)
            cursor_snapshot = payload["snapshot"]
            if snapshot is not None and snapshot != cursor_snapshot:
                raise RepositoryCursorError("cursor is bound to another snapshot or query")
            if payload["prefix"] != normalized_prefix or payload["text"] != text:
                raise RepositoryCursorError("cursor is bound to another snapshot or query")
            snapshot = cursor_snapshot
            last_path = payload["last_path"]
        head = self._resolve_snapshot(snapshot)

        needle = text.encode("utf-8")
        matches: list[dict[str, Any]] = []
        for path in self.list_files(normalized_prefix, head):
            content = self._store.read_bytes(head, path)
            if text and text not in path and needle not in content:
                continue
            matches.append({"path": path, "size": len(content), "sha256": hashlib.sha256(content).hexdigest()})
        total = len(matches)
        start = 0
        if last_path is not None:
            matching_indexes = [index for index, item in enumerate(matches) if item["path"] == last_path]
            if len(matching_indexes) != 1:
                raise RepositoryCursorError("cursor path is not present in this query result")
            start = matching_indexes[0] + 1
        items = matches[start:start + limit]
        next_cursor = None
        if start + len(items) < total:
            next_cursor = _encode_cursor({
                "snapshot": head,
                "prefix": normalized_prefix,
                "text": text,
                "last_path": items[-1]["path"],
            })
        return {
            "snapshot": head,
            "total": total,
            "items": items,
            "next_cursor": next_cursor,
            "truncated": next_cursor is not None,
        }

    def export(
        self,
        destination: Path,
        snapshot: str | None = None,
        prefixes: tuple[str, ...] = ("research/",),
    ) -> dict[str, Any]:
        """Copy selected snapshot files into a new or empty non-reparse directory."""
        head = self._resolve_snapshot(snapshot)
        if not isinstance(prefixes, tuple) or not prefixes:
            raise ValueError("prefixes must be a non-empty tuple")
        normalized_prefixes = tuple(_validate_prefix(prefix) for prefix in prefixes)
        destination = Path(destination)
        _assert_no_reparse_ancestor(destination)
        if destination.exists():
            if not destination.is_dir() or any(destination.iterdir()):
                raise ValueError("export destination must be absent or an empty directory")
        else:
            destination.mkdir(parents=True)
        _assert_no_reparse_ancestor(destination)

        files = sorted({path for prefix in normalized_prefixes for path in self.list_files(prefix, head)})
        for path in files:
            output = destination.joinpath(*path.split("/"))
            _assert_no_reparse_ancestor(output.parent)
            output.parent.mkdir(parents=True, exist_ok=True)
            _assert_no_reparse_ancestor(output.parent)
            with output.open("xb") as stream:
                stream.write(self._store.read_bytes(head, path))
        return {"snapshot": head, "files": files}

    def writer_lock(self) -> AbstractContextManager[None]:
        """Delegate the same-instance OS lock to GitStateStore."""
        return self._store.writer_lock()

    def _resolve_snapshot(self, snapshot: str | None) -> str:
        if snapshot is None:
            snapshot = self._store.read_snapshot().head
        if snapshot is None:
            raise ValueError("repository has no authoritative snapshot")
        self._store._validate_oid(snapshot)
        return snapshot

    def _git(self, *arguments: str):
        return self._store._git(*arguments)


def _canonical_object(value: Any) -> bytes:
    if not isinstance(value, dict):
        raise TypeError("instance and runtime values must be JSON objects")
    return canonical_json(value)


def _decode_object(data: bytes) -> dict[str, Any]:
    try:
        value = json.loads(data.decode("utf-8"), object_pairs_hook=_unique_pairs, parse_constant=_reject_constant)
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as error:
        raise ValueError("stored document is not strict JSON") from error
    if not isinstance(value, dict):
        raise ValueError("stored instance and runtime documents must be JSON objects")
    if canonical_json(value) != data:
        raise ValueError("stored document is not canonical JSON")
    return value


def _unique_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise ValueError(f"non-finite JSON constant: {value}")


def _validate_json(value: Any) -> None:
    if value is None or isinstance(value, (bool, str)):
        if isinstance(value, str) and any(0xD800 <= ord(character) <= 0xDFFF for character in value):
            raise ValueError("JSON strings cannot contain surrogate code points")
        return
    if isinstance(value, int) and not isinstance(value, bool):
        if abs(value) > _SAFE_INTEGER:
            raise ValueError("JSON integers must be safe integers")
        return
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("JSON numbers must be finite")
        return
    if isinstance(value, list):
        for item in value:
            _validate_json(item)
        return
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                raise ValueError("JSON object keys must be strings")
            _validate_json(key)
            _validate_json(item)
        return
    raise ValueError("value is not JSON-serializable")


def _validate_prefix(prefix: str) -> str:
    if not isinstance(prefix, str) or not prefix.endswith("/"):
        raise ValueError("prefix must be a slash-terminated POSIX state path")
    base = prefix[:-1]
    if not base:
        raise ValueError("prefix may not be the state root")
    parts = base.split("/")
    if parts[0] not in {"research", "runtime"} or any(not part or part in {".", ".."} or "\\" in part for part in parts):
        raise ValueError("prefix must remain below research/ or runtime/")
    return prefix


def _encode_cursor(value: Mapping[str, str]) -> str:
    return base64.urlsafe_b64encode(canonical_json(dict(value))).decode("ascii").rstrip("=")


def _decode_cursor(cursor: str) -> dict[str, Any]:
    if not isinstance(cursor, str) or not cursor:
        raise RepositoryCursorError("cursor must be a non-empty string")
    try:
        encoded = cursor.encode("ascii")
        data = base64.b64decode(encoded + b"=" * (-len(encoded) % 4), altchars=b"-_", validate=True)
        value = json.loads(data.decode("utf-8"), object_pairs_hook=_unique_pairs, parse_constant=_reject_constant)
    except (UnicodeError, ValueError, json.JSONDecodeError) as error:
        raise RepositoryCursorError("cursor is malformed") from error
    if (not isinstance(value, dict) or set(value) != {"snapshot", "prefix", "text", "last_path"}
            or any(not isinstance(value[key], str) for key in ("snapshot", "prefix", "text", "last_path"))):
        raise RepositoryCursorError("cursor has an invalid shape")
    return value


def _assert_no_reparse_ancestor(path: Path) -> None:
    candidate = path.absolute()
    while True:
        if candidate.exists() and _is_reparse(candidate):
            raise ValueError(f"export path crosses a reparse point: {candidate}")
        parent = candidate.parent
        if parent == candidate:
            return
        candidate = parent


def _is_reparse(path: Path) -> bool:
    if path.is_symlink():
        return True
    attributes = getattr(os.stat(path, follow_symlinks=False), "st_file_attributes", 0)
    return bool(attributes & _REPARSE_POINT)
