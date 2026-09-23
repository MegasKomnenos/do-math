"""Snapshot-facing research repository operations built on :mod:`git_store`.

Family files are authoritative. Read and publication share the installed
schema/relationship contract; model selection and activation remain elsewhere.
"""

from __future__ import annotations

import base64
from collections.abc import Mapping
from contextlib import AbstractContextManager
import hashlib
import json
import math
from copy import deepcopy
import os
from pathlib import Path
import re
import secrets
import time
from typing import Any

from .events import EventPublisher
from .git_store import GitStateStore, PhysicalBoundary
from .state_contract import STATE_FORMAT_VERSION, STATE_CONTRACT_ID, SCHEMA_VERSION, StateContract, default_state_contract


class RepositoryCursorError(ValueError):
    """A query cursor is malformed or bound to another snapshot/query."""


_PREFIX = re.compile(r"[A-Z][A-Z0-9]{0,7}\Z")
_CROCKFORD = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
_SAFE_INTEGER = (1 << 53) - 1
_REPARSE_POINT = 0x00000400
_SURROGATE = re.compile(r"[\ud800-\udfff]")


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
    """Encode a finite JSON value deterministically without changing Unicode."""
    validate_storage_value(value)
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n").encode("utf-8")


def lossless_json(value: Any) -> bytes:
    """Compatibility name for the exact canonical JSON representation."""
    return canonical_json(value)


def exact_content_hash(value: Any) -> str:
    """Identity of an exact logical payload, not a file or semantic projection."""
    return hashlib.sha256(lossless_json(value)).hexdigest()


class ResearchRepository:
    """Read and publish version-five record-family files through one Git CAS."""

    def __init__(self, repository: Path, instance_id: str, *, contract: StateContract | None = None) -> None:
        self._store = GitStateStore(repository, instance_id)
        self.contract = contract or default_state_contract()

    def register_family(self, root: str, name: str, **kwargs: Any) -> None:
        """Register a family owner before that family is persisted."""
        self.contract.register_family(root, name, **kwargs)

    def initialize(self, instance, runtime):
        if self._store.read_snapshot().head is not None:
            raise ValueError("the instance ref already has an initial state")
        candidate = self.validate_candidate(instance, runtime)
        return self._store.publish(None, candidate["files"]).head

    def _documents(self, head):
        return self._read_documents(head)[:3]

    def _read_documents(self, head):
        """Validate one snapshot and retain its exact non-artifact file bytes."""
        paths = self._store._tree_paths(head)
        if {"research/instance.json", "runtime/state.json"} & paths:
            raise ValueError("legacy two-root state is not a version-five snapshot")
        # Sealed artifacts are not parsed or loaded just to reconstruct state.
        files = self._store.read_many(head, sorted(p for p in paths if not p.startswith("runtime/artifacts/")))
        instance, runtime, descriptors = _decode_families(files, self.contract, self._store.object_format)
        self.contract.validate(instance, runtime)
        _validate_published_events(runtime)
        self._validate_artifact_evidence(runtime, head)
        return instance, runtime, descriptors, files

    def load(self, snapshot=None):
        head = self._resolve_snapshot(snapshot)
        instance, runtime, _ = self._documents(head)
        return head, instance, runtime

    def validate_candidate(self, instance, runtime, expected_head=None, *, artifacts=None):
        """Pure candidate check, including parent event facts when supplied.

        The returned views are detached. Callers reload after publication to
        observe assigned events. No rejected/CAS-losing proposal mutates them.
        """
        return self._validate_candidate(instance, runtime, expected_head, artifacts=artifacts)

    def _validate_candidate(self, instance, runtime, expected_head=None, *, artifacts=None, parent_state=None):
        # parent_state is private and supplied only by this save's validated read.
        if not isinstance(instance, dict) or not isinstance(runtime, dict):
            raise ValueError("instance and runtime must be objects")
        instance = deepcopy(instance)
        runtime = deepcopy(runtime)
        validate_storage_value(instance)
        validate_storage_value(runtime)
        for state in (instance, runtime):
            if state.get("feature_version") != STATE_FORMAT_VERSION:
                raise ValueError("storage requires feature_version 5")
            if state.get("contract_id", STATE_CONTRACT_ID) != STATE_CONTRACT_ID:
                raise ValueError("unsupported persisted state contract")
            state["contract_id"] = STATE_CONTRACT_ID
        if instance.get("object_format", self._store.object_format) != self._store.object_format:
            raise ValueError("persisted object_format differs from Git")
        instance["object_format"] = self._store.object_format
        parent_instance, parent_runtime = {}, {}
        if expected_head is not None:
            if parent_state is None:
                _, parent_instance, parent_runtime = self.load(expected_head)
            else:
                parent_instance, parent_runtime = parent_state
        from .events import event_rows
        previous = {row["id"]: row for row in event_rows(parent_runtime.get("events", []))}
        EventPublisher.assign_sequences_in_place(runtime, published_events=previous)
        # Immutable judgments/profile editions cannot be rewritten under one ID.
        for family in ("identity_assessments", "execution_profiles", "governance_sources"):
            for identifier, row in parent_instance.get(family, {}).items():
                if instance.get(family, {}).get(identifier) != row:
                    raise ValueError("immutable record changed or removed: " + identifier)
        if parent_instance.get("lifecycle", {}).get("immutable_input") is not None:
            if instance.get("lifecycle", {}).get("immutable_input") != parent_instance["lifecycle"]["immutable_input"]:
                raise ValueError("immutable original input changed")
        for identifier, row in parent_instance.get("formal_results", {}).items():
            if row.get("verification"):
                current = instance.get("formal_results", {}).get(identifier)
                if current is None or any(current.get(k) != v for k, v in row.items() if k not in {"formal_use", "history", "use_history"}):
                    raise ValueError("sealed formal result changed: " + identifier)
        # Only explicitly derived views are refreshed; authoritative caller
        # records are neither repaired nor silently discarded.
        for family in self.contract.families():
            state = instance if family.root == "research" else runtime
            if family.shape == "derived" and family.name in state:
                state[family.name] = family.derived(instance, runtime)
        self.contract.validate(instance, runtime)
        self._validate_artifact_evidence(runtime, expected_head, artifacts)
        files = _encode_families(instance, runtime, self.contract, self._store.object_format)
        self._store._validate_candidate_paths(set(files))
        return {"instance": instance, "runtime": runtime, "files": files,
                "contract": self.contract.manifest(), "valid": True}

    def save_with_state(self, expected_head, instance, runtime, *, artifacts=None):
        """Validate and atomically publish once, returning the published normalized views."""
        self._store._validate_oid(expected_head)
        # Ref precheck avoids expensive validation against an already stale head;
        # final expected-old-OID update remains the sole authority.
        if self._store.read_snapshot().head != expected_head:
            from .git_store import GitStateStoreConflict
            raise GitStateStoreConflict("expected head no longer matches the instance ref")
        artifact_snapshot = self._snapshot_artifacts(artifacts)
        parent_instance, parent_runtime, _, old_files = self._read_documents(expected_head)
        candidate = self._validate_candidate(instance, runtime, expected_head, artifacts=artifact_snapshot,
                                             parent_state=(parent_instance, parent_runtime))
        files = candidate["files"]
        changes = {p: None for p in old_files if p not in files}
        changes.update({p: raw for p, raw in files.items() if old_files.get(p) != raw})
        if artifact_snapshot is not None:
            for path, raw in artifact_snapshot.items():
                changes[path] = raw
        published = self._store.publish(expected_head, changes)
        return published.head, candidate["instance"], candidate["runtime"]

    def save(self, expected_head, instance, runtime, *, artifacts=None):
        """Publish a valid state and retain the historical head-only interface."""
        return self.save_with_state(expected_head, instance, runtime, artifacts=artifacts)[0]

    @staticmethod
    def _snapshot_artifacts(artifacts):
        if artifacts is None:
            return None
        if not isinstance(artifacts, Mapping):
            raise TypeError("artifacts must map full artifact paths to bytes")
        snapshot = {}
        for path, raw in artifacts.items():
            if not isinstance(path, str) or not path.startswith("runtime/artifacts/") or not isinstance(raw, bytes):
                raise ValueError("artifacts require full runtime/artifacts/<bundle>/<path> and bytes")
            snapshot[path] = raw
        return snapshot

    def _validate_artifact_evidence(self, runtime, head, artifacts=None):
        """Resolve immutable byte evidence separately from record identities."""
        references = [(ref, row["evidence_hashes"][ref], None)
            for row in runtime.get("academic_resolution_records", [])
            for ref in row["evidence_refs"] if ref.startswith("runtime/artifacts/")]
        for checkpoint in runtime.get("checkpoints", {}).values():
            for observation in (checkpoint, checkpoint.get("final_observation", {})):
                if observation.get("observation_evidence_complete") is True and observation.get("observation_evidence_omitted"):
                    raise ValueError("complete observation evidence cannot contain omissions")
                references.extend((row["artifact_ref"], row["sha256"], row["bytes"])
                                  for row in observation.get("observation_sources", []))
        if not references:
            return
        available = self._store._tree_paths(head) if head else set()
        supplied = artifacts or {}
        for ref, _, _ in references:
            if not ref.startswith("runtime/artifacts/"):
                raise ValueError("artifact evidence must use the immutable artifact namespace")
            self._store._validate_path(ref)
        stored = self._store.read_many(head, sorted({ref for ref, _, _ in references
            if supplied.get(ref) is None and ref in available})) if head else {}
        for ref, digest, size in references:
            raw = supplied.get(ref)
            if raw is None:
                raw = stored.get(ref)
            if (not isinstance(raw, bytes) or hashlib.sha256(raw).hexdigest() != digest
                    or (size is not None and len(raw) != size)):
                raise ValueError("artifact evidence missing or hash differs: " + ref)

    def records(self, snapshot=None, *, family=None, root=None):
        """Enumerate exact persisted record bytes, including singleton authorities."""
        head = self._resolve_snapshot(snapshot)
        _, _, rows = self._documents(head)
        return [{**row, "snapshot": head} for row in rows
                if (family is None or row["family"] == family) and (root is None or row["root"] == root)]

    def read_record(self, record_id, snapshot=None):
        matches = [row for row in self.records(snapshot) if row["id"] == record_id]
        if len(matches) != 1:
            raise KeyError("record not found: " + str(record_id))
        return matches[0]

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

        boundary = PhysicalBoundary(destination)

        files = sorted({path for prefix in normalized_prefixes for path in self.list_files(prefix, head)})
        for path in files:
            output = destination.joinpath(*path.split("/"))
            _assert_no_reparse_ancestor(output.parent)
            output.parent.mkdir(parents=True, exist_ok=True)
            _assert_no_reparse_ancestor(output.parent)
            with boundary.open(output, "xb") as stream:
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


def validate_storage_value(value: Any) -> None:
    """Validate the exact storage value domain without constructing JSON bytes."""
    if value is None or isinstance(value, (bool, str)):
        if isinstance(value, str) and _SURROGATE.search(value):
            raise ValueError("JSON strings cannot contain surrogate code points")
        return
    if isinstance(value, int) and not isinstance(value, bool):
        if abs(value) > _SAFE_INTEGER:
            raise ValueError("JSON integers must be safe integers")
        return
    if isinstance(value, float):
        raise ValueError("JSON floating-point numbers are not permitted")
    if isinstance(value, list):
        for item in value:
            validate_storage_value(item)
        return
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                raise ValueError("JSON object keys must be strings")
            validate_storage_value(key)
            validate_storage_value(item)
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
    return base64.urlsafe_b64encode(lossless_json(dict(value))).decode("ascii").rstrip("=")


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


def transport_json(value):
    """JSON transport for measured finite decimals; not canonical storage bytes."""
    def check(item):
        if isinstance(item, float):
            if not math.isfinite(item):
                raise ValueError("transport numbers must be finite")
        elif isinstance(item, dict):
            for key, child in item.items():
                validate_storage_value(key)
                check(child)
        elif isinstance(item, list):
            for child in item:
                check(child)
        else:
            validate_storage_value(item)
    check(value)
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n").encode("utf-8")


def semantic_content_hash(value, projection=None):
    """Hash an explicitly selected semantic projection, distinct from file bytes."""
    if projection is not None:
        if not isinstance(value, Mapping) or any(key not in value for key in projection):
            raise ValueError("semantic projection fields must exist")
        value = {key: value[key] for key in projection}
    return hashlib.sha256(canonical_json(value)).hexdigest()


def _record_path(root, name, identifier):
    return f"{root}/{name}/{identifier}.json"


def _envelope(family, value):
    return {"contract_id": STATE_CONTRACT_ID, "schema_version": SCHEMA_VERSION,
            "family": family, "record": value}


def _encode_families(instance, runtime, contract, object_format):
    files = {}
    installed = contract.manifest()
    for root, state in (("research", instance), ("runtime", runtime)):
        containers, metadata = {}, {}
        for name, value in sorted(state.items()):
            family = contract.family(root, name)
            if family.shape == "metadata":
                containers[name] = {"shape": "metadata"}
                metadata[name] = deepcopy(value)
                continue
            if family.shape == "derived":
                containers[name] = {"shape": "derived"}
                continue
            if family.shape == "singleton":
                identifier = value["id"] if family.identity else "state"
                entries = [(identifier, value)]
                descriptor = {"shape": "singleton", **({"id": identifier} if family.identity else {})}
            elif family.shape == "map" or family.shape == "events" and isinstance(value, dict):
                entries = sorted(value.items()) if family.shape != "events" else list(value.items())
                descriptor = {"shape": "map", "ids": [k for k, _ in entries]}
            else:
                entries = [(r["id"], r) for r in value]
                descriptor = {"shape": "list", "ids": [k for k, _ in entries]}
            containers[name] = descriptor
            for identifier, record in entries:
                files[_record_path(root, name, identifier)] = canonical_json(_envelope(name, record))
        files[f"{root}/_state/metadata.json"] = canonical_json(_envelope("metadata", metadata))
        # Each root describes only its own containers, preserving research OID
        # when only runtime families or event membership change.
        files[f"{root}/_state/manifest.json"] = canonical_json({
            "contract": installed, "object_format": object_format, "containers": containers})
    return files


def _decode_families(files, contract, object_format):
    states, descriptors, expected = {}, [], set()
    installed = contract.manifest()
    derived = []
    for root in ("research", "runtime"):
        manifest_path = f"{root}/_state/manifest.json"
        if manifest_path not in files:
            raise ValueError("missing family manifest: " + root)
        manifest = _decode_object(files[manifest_path])
        declared = manifest.get("contract")
        if (set(manifest) != {"contract", "object_format", "containers"}
                or not isinstance(declared, dict) or set(declared) != set(installed)
                or declared.get("contract_id") != installed["contract_id"]
                or declared.get("schema_version") != installed["schema_version"]
                or not isinstance(declared.get("sha256"), str)
                or not re.fullmatch(r"[0-9a-f]{64}", declared["sha256"])):
            raise ValueError("unsupported stored contract/schema version or manifest")
        # The writer's schema digest identifies its declarations. An optional
        # field added later does not change existing records' representation.
        # Check every stored layout and record against the installed contract
        # below; never infer compatibility by rewriting or dropping fields.
        if manifest["object_format"] != object_format:
            raise ValueError("snapshot object_format differs from Git")
        if not isinstance(manifest["containers"], dict):
            raise ValueError("invalid family manifest containers")
        expected.add(manifest_path)
        state = states[root] = {}
        metadata_path = f"{root}/_state/metadata.json"
        if metadata_path not in files:
            raise ValueError("missing root metadata record: " + root)
        raw_metadata = files[metadata_path]
        envelope = _decode_object(raw_metadata)
        metadata = envelope.get("record")
        if not isinstance(metadata, dict) or envelope != _envelope("metadata", metadata):
            raise ValueError("invalid root metadata envelope: " + root)
        declared_metadata = {name for name, descriptor in manifest["containers"].items()
                             if descriptor == {"shape": "metadata"}}
        if set(metadata) != declared_metadata:
            raise ValueError("metadata fields differ from declared membership: " + repr(sorted(set(metadata) ^ declared_metadata)))
        expected.add(metadata_path)
        descriptors.append({"root": root, "family": "metadata", "id": None, "path": metadata_path,
            "bytes": raw_metadata, "sha256": hashlib.sha256(raw_metadata).hexdigest(),
            "record": {}, "json_pointer": "/record"})
        metadata_descriptor = descriptors[-1]
        for name, descriptor in manifest["containers"].items():
            family = contract.family(root, name)
            if family is None or not isinstance(descriptor, dict):
                raise ValueError("unregistered manifest family: " + name)
            shape = descriptor.get("shape")
            allowed = {"map", "list"} if family.shape == "events" else {family.shape}
            if shape not in allowed:
                raise ValueError("manifest shape differs from registered family: " + name)
            if shape == "metadata":
                if descriptor != {"shape": "metadata"}:
                    raise ValueError("invalid metadata descriptor: " + name)
                state[name] = deepcopy(metadata[name])
                metadata_descriptor["record"][name] = deepcopy(state[name])
                continue
            if shape == "derived":
                if descriptor != {"shape": "derived"}:
                    raise ValueError("invalid derived descriptor")
                derived.append(family)
                continue
            ids = [descriptor.get("id") if family.identity else "state"] if shape == "singleton" else descriptor.get("ids")
            descriptor_keys = ({"shape", "id"} if family.identity else {"shape"}) if shape == "singleton" else {"shape", "ids"}
            if (not isinstance(ids, list) or any(not isinstance(i, str) for i in ids)
                    or len(ids) != len(set(ids))
                    or set(descriptor) != descriptor_keys):
                raise ValueError("invalid family membership: " + name)
            rows = []
            for identifier in ids:
                path = _record_path(root, name, identifier)
                if path not in files:
                    raise ValueError("missing registered record file: " + path)
                expected.add(path)
                raw = files[path]
                envelope = _decode_object(raw)
                if set(envelope) != {"contract_id", "schema_version", "family", "record"} or envelope != _envelope(name, envelope["record"]):
                    raise ValueError("invalid record envelope: " + path)
                row = envelope["record"]
                if family.identity and (not isinstance(row, dict) or row.get("id") != identifier):
                    raise ValueError("record path and id differ: " + path)
                rows.append(row)
                descriptors.append({"root": root, "family": name,
                    "id": identifier if family.identity else None, "path": path,
                    "bytes": raw, "sha256": hashlib.sha256(raw).hexdigest(), "record": deepcopy(row),
                    "json_pointer": "/record"})
            state[name] = rows[0] if shape == "singleton" else dict(zip(ids, rows)) if shape == "map" else rows
    if set(files) != expected:
        raise ValueError("undeclared state files: " + repr(sorted(set(files) - expected)))
    for family in derived:
        states[family.root][family.name] = family.derived(states["research"], states["runtime"])
    return states["research"], states["runtime"], descriptors


def _validate_published_events(runtime):
    from .events import event_rows
    rows = event_rows(runtime.get("events", []))
    numbers = [r.get("event_seq") for r in rows]
    if any(type(n) is not int for n in numbers) or numbers != list(range(1, len(rows) + 1)):
        raise ValueError("published event sequence is not contiguous")
    if "event_cursor" in runtime and runtime["event_cursor"] != len(rows):
        raise ValueError("event cursor differs from published events")
