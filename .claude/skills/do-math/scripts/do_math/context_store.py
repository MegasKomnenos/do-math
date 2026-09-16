"""Lossless input catalogs, bounded prompt contexts, and workspace collection."""
from __future__ import annotations

from copy import deepcopy
import hashlib
import os
from pathlib import Path, PurePosixPath
import stat
from typing import Any

from .repository import canonical_json


_REPARSE_POINT = 0x400
_CATALOG_KEYS = (
    "recent_history", "tasks", "knowledge_catalog", "eligible_knowledge",
    "relations", "sources", "user_inputs", "open_questions", "goal_judgments", "preparation_history", "blocked_actions",
)


class _ChangedDuringRead(OSError):
    pass


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _relative(name: str) -> PurePosixPath:
    if not isinstance(name, str) or not name or "\\" in name or ":" in name:
        raise ValueError("path must be a nonempty relative POSIX path")
    path = PurePosixPath(name)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        raise ValueError(f"unsafe relative path: {name}")
    return path


def _is_reparse(path: Path) -> bool:
    try:
        info = path.lstat()
    except FileNotFoundError:
        return False
    return stat.S_ISLNK(info.st_mode) or bool(getattr(info, "st_file_attributes", 0) & _REPARSE_POINT)


def _safe_path(root: Path, name: str, *, require_input: bool = False) -> Path:
    relative = _relative(name)
    if require_input and (not relative.parts or relative.parts[0] != "input"):
        raise ValueError("source reference must stay below input/")
    root = root.resolve()
    candidate = root.joinpath(*relative.parts)
    cursor = root
    if _is_reparse(cursor):
        raise ValueError(f"root is a reparse point: {root}")
    for part in relative.parts:
        cursor /= part
        if cursor.exists() and _is_reparse(cursor):
            raise ValueError(f"path crosses a reparse point: {cursor}")
    resolved = candidate.resolve(strict=False)
    if not resolved.is_relative_to(root):
        raise ValueError(f"path leaves workspace: {name}")
    return candidate


def _read_stable(path: Path) -> bytes:
    before = path.stat()
    data = path.read_bytes()
    after = path.stat()
    signature = lambda value: (value.st_size, value.st_mtime_ns, getattr(value, "st_ino", None))
    if signature(before) != signature(after) or len(data) != after.st_size:
        raise _ChangedDuringRead(f"file changed while being read: {path}")
    return data


def materialize_inputs(workspace: Path, documents: dict[str, bytes]) -> dict:
    if not isinstance(documents, dict):
        raise TypeError("documents must be a path-to-bytes object")
    workspace = workspace.resolve()
    workspace.mkdir(parents=True, exist_ok=True)
    if _is_reparse(workspace):
        raise ValueError("workspace must not be a reparse point")
    planned: list[tuple[str, Path, bytes]] = []
    for name, data in documents.items():
        relative = _relative(name)
        if not isinstance(data, bytes):
            raise TypeError(f"document must be bytes: {name}")
        logical = PurePosixPath("input") / relative
        target = _safe_path(workspace, logical.as_posix(), require_input=True)
        if target.exists():
            raise FileExistsError(f"input path already exists: {logical.as_posix()}")
        planned.append((logical.as_posix(), target, data))
    manifest = []
    for logical, target, data in sorted(planned):
        target.parent.mkdir(parents=True, exist_ok=True)
        _safe_path(workspace, logical, require_input=True)
        with target.open("xb") as stream:
            stream.write(data)
        observed = _read_stable(target)
        if observed != data:
            raise OSError(f"materialized input bytes differ: {logical}")
        manifest.append({"path": logical, "sha256": _sha256(observed), "bytes": len(observed)})
    return {"input_root": "input", "manifest": manifest}


def _excluded(relative: PurePosixPath) -> bool:
    return bool(relative.parts and (relative.parts[0] in {"input", ".git"} or "__pycache__" in relative.parts))


def collect_outputs(workspace: Path, *, required_paths: list[str] = [],
                    max_bytes: int = 268435456) -> dict:
    if isinstance(max_bytes, bool) or not isinstance(max_bytes, int) or max_bytes < 0:
        raise ValueError("max_bytes must be a nonnegative integer")
    if not isinstance(required_paths, list):
        raise TypeError("required_paths must be a list")
    required = {_relative(name).as_posix() for name in required_paths}
    workspace = workspace.resolve()
    files: dict[str, bytes] = {}
    manifest: list[dict] = []
    omitted: list[dict] = []
    seen: set[str] = set()
    if not workspace.is_dir():
        return {"files": files, "manifest": manifest,
                "omitted": [{"path": name, "reason": "workspace_missing"} for name in sorted(required)],
                "complete": False}
    for directory, dirnames, filenames in os.walk(workspace, topdown=True, followlinks=False):
        base = Path(directory)
        kept = []
        for dirname in sorted(dirnames):
            path = base / dirname
            relative = PurePosixPath(path.relative_to(workspace).as_posix())
            if _excluded(relative):
                continue
            if _is_reparse(path):
                reason = "outside_symlink" if not path.resolve(strict=False).is_relative_to(workspace) else "reparse_directory"
                omitted.append({"path": relative.as_posix(), "reason": reason})
                continue
            kept.append(dirname)
        dirnames[:] = kept
        for filename in sorted(filenames):
            path = base / filename
            relative = PurePosixPath(path.relative_to(workspace).as_posix())
            name = relative.as_posix()
            if _excluded(relative):
                continue
            seen.add(name)
            if _is_reparse(path):
                reason = "outside_symlink" if not path.resolve(strict=False).is_relative_to(workspace) else "reparse_file"
                omitted.append({"path": name, "reason": reason, "required": name in required})
                continue
            try:
                data = _read_stable(path)
            except FileNotFoundError:
                omitted.append({"path": name, "reason": "disappeared", "required": name in required})
                continue
            except _ChangedDuringRead as error:
                omitted.append({"path": name, "reason": "changed_during_read", "error": str(error), "required": name in required})
                continue
            except OSError as error:
                omitted.append({"path": name, "reason": "read_error", "error_type": type(error).__name__,
                                "error": str(error), "required": name in required})
                continue
            if sum(row["bytes"] for row in manifest) + len(data) > max_bytes:
                omitted.append({"path": name, "reason": "max_bytes_exceeded", "bytes": len(data), "required": name in required})
                continue
            files[name] = data
            manifest.append({"path": name, "sha256": _sha256(data), "bytes": len(data)})
    for name in sorted(required - set(files)):
        if not any(row["path"] == name for row in omitted):
            omitted.append({"path": name, "reason": "required_missing" if name not in seen else "required_not_collected", "required": True})
    complete = not omitted and required <= set(files)
    return {"files": files, "manifest": sorted(manifest, key=lambda row: row["path"]),
            "omitted": sorted(omitted, key=lambda row: (row["path"], row["reason"])), "complete": complete}


def _catalog_name(key: str) -> str:
    if not isinstance(key, str) or not key or any(not (character.isalnum() or character in "_-") for character in key):
        raise ValueError(f"context key cannot be a catalog filename: {key}")
    return key + ".json"


def write_source_catalog(context: dict, workspace: Path) -> dict:
    if not isinstance(context, dict):
        raise TypeError("context must be an object")
    workspace = workspace.resolve()
    workspace.mkdir(parents=True, exist_ok=True)
    if _is_reparse(workspace):
        raise ValueError("workspace must not be a reparse point")
    entries: dict[str, dict] = {}
    manifest: list[dict] = []
    for key in _CATALOG_KEYS:
        if key not in context:
            continue
        logical = "input/catalog/" + _catalog_name(key)
        target = _safe_path(workspace, logical, require_input=True)
        data = canonical_json(context[key])
        if target.exists():
            observed = _read_stable(target)
            if observed != data:
                raise FileExistsError(f"catalog path contains different bytes: {logical}")
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open("xb") as stream:
                stream.write(data)
            observed = _read_stable(target)
        ref = {"path": logical, "sha256": _sha256(observed), "bytes": len(observed),
               "format": "canonical-json"}
        entries[key] = ref
        manifest.append({"key": key, **ref})
    return {"entries": entries, "manifest": manifest, "total": len(manifest)}


def _encoded_size(value: dict) -> int:
    return len(canonical_json(value))


def _ready_projection(tasks: Any) -> tuple[list[str], list[dict]]:
    if not isinstance(tasks, list):
        return [], []
    ready = [task for task in tasks if isinstance(task, dict) and task.get("status") == "ready"]
    identifiers = [task["id"] for task in ready if isinstance(task.get("id"), str)]
    fields = ("id", "title", "question", "status", "completion_criteria")
    return identifiers, [{key: deepcopy(task[key]) for key in fields if key in task} for task in ready]


def fit_context(context: dict, *, max_bytes: int, workspace: Path,
                mandatory_keys: list[str]) -> dict:
    if not isinstance(context, dict):
        raise TypeError("context must be an object")
    if isinstance(max_bytes, bool) or not isinstance(max_bytes, int) or max_bytes < 1:
        raise ValueError("max_bytes must be a positive integer")
    if not isinstance(mandatory_keys, list) or len(mandatory_keys) != len(set(mandatory_keys)):
        raise ValueError("mandatory_keys must contain distinct keys")
    missing = [key for key in mandatory_keys if key not in context]
    if missing:
        raise ValueError("mandatory context keys are missing: " + ", ".join(missing))
    catalog = write_source_catalog(context, workspace)
    fitted = deepcopy(context)
    reductions: list[dict] = []
    mandatory_context = {key: deepcopy(context[key]) for key in mandatory_keys}
    mandatory_bytes = _encoded_size(mandatory_context)
    if mandatory_bytes > max_bytes:
        actual = _encoded_size(fitted)
        return {"context": fitted, "manifest": catalog["manifest"], "actual_bytes": actual,
                "reductions": reductions, "overflow": {"reason": "mandatory_context_exceeds_limit",
                "actual_bytes": actual, "mandatory_bytes": mandatory_bytes, "max_bytes": max_bytes}}
    if _encoded_size(fitted) <= max_bytes:
        return {"context": fitted, "manifest": catalog["manifest"],
                "actual_bytes": _encoded_size(fitted), "reductions": reductions, "overflow": None}

    if "recent_history" in fitted and "recent_history" not in mandatory_keys and isinstance(fitted["recent_history"], list):
        original = fitted["recent_history"]
        ref = catalog["entries"]["recent_history"]
        keep = min(8, len(original))
        while True:
            fitted["recent_history"] = {"recent": deepcopy(original[-keep:]) if keep else [],
                                        "total": len(original), "source_ref": ref}
            if _encoded_size(fitted) <= max_bytes or keep == 0:
                break
            keep //= 2
        reductions.append({"key": "recent_history", "kind": "recent_window",
                           "original_items": len(original), "kept_items": keep, "source_ref": ref})

    candidates = [key for key in _CATALOG_KEYS if key in fitted and key not in mandatory_keys and key != "recent_history"]
    candidates.sort(key=lambda key: len(canonical_json(context[key])), reverse=True)
    for key in candidates:
        if _encoded_size(fitted) <= max_bytes:
            break
        ref = catalog["entries"][key]
        if key == "tasks":
            universe, listing = _ready_projection(context[key])
            fitted[key] = {"total": len(context[key]) if isinstance(context[key], list) else None,
                           "ready_universe_ids": universe, "ready_listing": listing, "source_ref": ref}
            if _encoded_size(fitted) > max_bytes:
                fitted[key]["ready_listing"] = []
            reductions.append({"key": key, "kind": "ready_catalog", "source_ref": ref,
                               "ready_universe_ids": universe})
        else:
            count = len(context[key]) if isinstance(context[key], (list, dict)) else None
            fitted[key] = {"source_ref": ref, "total": count}
            reductions.append({"key": key, "kind": "source_reference", "source_ref": ref})

    actual = _encoded_size(fitted)
    overflow = None if actual <= max_bytes else {"reason": "context_cannot_fit_without_losing_required_index",
        "actual_bytes": actual, "mandatory_bytes": mandatory_bytes, "max_bytes": max_bytes}
    return {"context": fitted, "manifest": catalog["manifest"], "actual_bytes": actual,
            "reductions": reductions, "overflow": overflow}


def read_source(workspace: Path, ref: dict, offset: int = 0,
                limit: int = 1048576) -> dict:
    if isinstance(offset, bool) or not isinstance(offset, int) or offset < 0:
        raise ValueError("offset must be a nonnegative integer")
    if isinstance(limit, bool) or not isinstance(limit, int) or limit < 1:
        raise ValueError("limit must be a positive integer")
    try:
        if not isinstance(ref, dict) or not isinstance(ref.get("path"), str):
            raise ValueError("source ref must contain a path")
        path = _safe_path(workspace.resolve(), ref["path"], require_input=True)
        if not path.exists():
            return {"status": "missing", "path": ref["path"], "bytes": b"",
                    "sha256": None, "range": {"start": offset, "end": offset, "total": 0},
                    "truncated": False, "reason": "source_missing"}
        data = _read_stable(path)
        digest = _sha256(data)
        if "sha256" in ref and ref["sha256"] != digest:
            raise ValueError("source hash differs from reference")
        if "bytes" in ref and ref["bytes"] != len(data):
            raise ValueError("source size differs from reference")
        start = min(offset, len(data)); end = min(start + limit, len(data))
        return {"status": "ok", "path": ref["path"], "bytes": data[start:end],
                "sha256": digest, "range": {"start": start, "end": end, "total": len(data)},
                "truncated": end < len(data)}
    except (OSError, ValueError) as error:
        return {"status": "error", "path": ref.get("path") if isinstance(ref, dict) else None,
                "bytes": b"", "sha256": None, "range": None, "truncated": False,
                "reason": str(error), "error_type": type(error).__name__}
