"""Snapshot-facing research repository operations built on :mod:`git_store`.

Family files are authoritative. Read and publication share the installed
schema/relationship contract; model selection and activation remain elsewhere.
"""

from __future__ import annotations

import base64
from collections import OrderedDict
from collections.abc import Mapping
from contextlib import AbstractContextManager
import hashlib
import json
from copy import deepcopy
from pathlib import Path
import re
import secrets
import threading
import time
from typing import Any

from .operation_trace import measured

from .events import EventPublisher, check_sequence, event_rows
from .file_io import is_sha256, reject_constant, unique_pairs
from .git_store import GitStateStore, PhysicalBoundary, ULID_ALPHABET, ULID_LENGTH, no_reparse
# payloads imports this module only inside its functions, so a module-level
# import is acyclic; canonical_json and its value check run on every node.
from .payloads import FrozenDict, FrozenText, decode, encode, seal_large
from .state_contract import STATE_CONTRACT_ID, StateContract, default_state_contract


# Immutable artifact rows whose stored bytes this process already matched,
# keyed by (git directory, artifact path, sha256). Existing artifact bundles
# never change (git_store bundle invariant), so one match holds for the process.
# The value is the matched byte length, so a row that declares a size is
# still compared against the actual length without reading the bytes again.
VERIFIED_ARTIFACTS: dict[tuple[str, str, str], int] = {}


def artifact_key(git_dir, path, sha256):
    """The key of one sealed row of one repository, shared by per-process memos."""
    return (str(git_dir), path, sha256)


def artifact_verified(git_dir, path, sha256, size=None):
    if git_dir is None:
        return False
    matched = VERIFIED_ARTIFACTS.get(artifact_key(git_dir, path, sha256))
    return matched is not None and (size is None or matched == size)


def mark_artifact_verified(git_dir, path, sha256, size):
    """Record a match the caller already established against stored bytes."""
    VERIFIED_ARTIFACTS[artifact_key(git_dir, path, sha256)] = size


def verify_artifact(git_dir, path, raw, sha256, size=None):
    """Raise unless ``raw`` matches the sealed row; remember the match in ``git_dir``."""
    if (not isinstance(raw, bytes) or hashlib.sha256(raw).hexdigest() != sha256
            or (size is not None and len(raw) != size)):
        raise ValueError("artifact evidence missing or hash differs: " + path)
    if git_dir is not None:
        mark_artifact_verified(git_dir, path, sha256, len(raw))


def sealed_bytes(git_dir, path, sha256, size, read, *, raw=None, needed=True, error=None):
    """Stored artifact bytes, matched against their sealed row once per process (contract S3).

    ``read()`` supplies the stored bytes when ``raw`` is not given. ``size`` is
    the declared length, or None when the row declares none. A row this process
    already matched is not hashed again; with ``needed=False`` it is not read
    either, and the result is ``raw`` (possibly None). Without ``git_dir`` the
    bytes are compared on every call and no match is remembered. A mismatch
    raises ``ValueError(error)`` when ``error`` is given, else verify_artifact's.
    """
    if artifact_verified(git_dir, path, sha256, size):
        if raw is None and needed:
            raw = read()
        return raw
    raw = read() if raw is None else raw
    try:
        verify_artifact(git_dir, path, raw, sha256, size)
    except ValueError as mismatch:
        if error is None:
            raise
        raise ValueError(error) from mismatch
    return raw


# Validated snapshot reads shared by every repository object in this process,
# keyed by (git directory, commit, contract key). A commit's bytes never
# change, so an entry stays valid for its contract; the bound limits memory.
# Entries come from a full read of a head, or from this process's own
# publication, whose candidate was validated before the ref moved.
_VALIDATED_READS: OrderedDict = OrderedDict()
_VALIDATED_READ_LIMIT = 4


def _contract_key(contract):
    """Contracts left as installed share entries; any other contract is its own key."""
    digest = contract.manifest()["sha256"]
    if contract.validation_generation == contract.installed_generation:
        return ("installed", digest)
    return (contract, digest, contract.validation_generation)


# Heads kept beyond the limit, per git directory: the input snapshots of live
# executions, which result acceptance reads again after later publications.
_RETAINED_READS: dict[str, frozenset] = {}


def retain_reads(git_dir, heads):
    """Keep the validated reads of ``heads`` outside the LRU bound until the next call."""
    _RETAINED_READS[str(git_dir)] = frozenset(heads)


def _remember_read(key, entry):
    _VALIDATED_READS[key] = entry
    _VALIDATED_READS.move_to_end(key)
    unretained = [k for k in _VALIDATED_READS if k[1] not in _RETAINED_READS.get(k[0], ())]
    for old in unretained[:max(0, len(unretained) - _VALIDATED_READ_LIMIT)]:
        del _VALIDATED_READS[old]


# Artifact facts this process wrote or read, keyed by (git directory, path):
# [head where the path was known to exist, length, bytes or None]. Existing
# artifact bundles never change and no publication removes them
# (git_store._validate_artifact_changes), so a fact known at a head holds at
# every later head this process published from it (_PUBLISHED_PARENTS).
# Bytes are held up to _ARTIFACT_BYTES_LIMIT; lengths stay while rows fit.
_ARTIFACT_FACTS: OrderedDict = OrderedDict()
_PUBLISHED_PARENTS: OrderedDict = OrderedDict()
_ARTIFACT_ROW_LIMIT = 4096
_ARTIFACT_BYTES_LIMIT = 64 << 20
_LINEAGE_LIMIT = 1024
_artifact_lock = threading.Lock()
_held_bytes = 0


def _descends(git_dir, snapshot, head):
    """True when ``snapshot`` is ``head`` or a later head this process published from it."""
    current = snapshot
    for _ in range(_LINEAGE_LIMIT):
        if current == head:
            return True
        current = _PUBLISHED_PARENTS.get((git_dir, current))
        if current is None:
            return False
    return False


def _known_artifact(git_dir, path, snapshot):
    """The [head, length, bytes] row for ``path`` when it holds at ``snapshot``, else None."""
    with _artifact_lock:
        row = _ARTIFACT_FACTS.get((git_dir, path))
        if row is None or not _descends(git_dir, snapshot, row[0]):
            return None
        _ARTIFACT_FACTS.move_to_end((git_dir, path))
        return row


def _learn_artifact(git_dir, path, head, size, raw=None):
    global _held_bytes
    with _artifact_lock:
        old = _ARTIFACT_FACTS.pop((git_dir, path), None)
        if old is not None and old[2] is not None:
            _held_bytes -= len(old[2])
            if raw is None and old[1] == size:
                raw = old[2]
        _ARTIFACT_FACTS[(git_dir, path)] = [head, size, raw]
        if raw is not None:
            _held_bytes += len(raw)
        for key in list(_ARTIFACT_FACTS):
            if len(_ARTIFACT_FACTS) <= _ARTIFACT_ROW_LIMIT and _held_bytes <= _ARTIFACT_BYTES_LIMIT:
                break
            if len(_ARTIFACT_FACTS) > _ARTIFACT_ROW_LIMIT:
                dropped = _ARTIFACT_FACTS.pop(key)
            else:
                dropped = _ARTIFACT_FACTS[key]
                _ARTIFACT_FACTS[key] = [dropped[0], dropped[1], None]
            if dropped[2] is not None:
                _held_bytes -= len(dropped[2])


def _learn_publication(git_dir, parent, head, artifacts):
    with _artifact_lock:
        if parent is not None and parent != head:  # a no-op publication keeps its head
            _PUBLISHED_PARENTS[(git_dir, head)] = parent
            while len(_PUBLISHED_PARENTS) > _LINEAGE_LIMIT:
                _PUBLISHED_PARENTS.popitem(last=False)
    for path, raw in artifacts.items():
        _learn_artifact(git_dir, path, head, len(raw), raw)


class RepositoryCursorError(ValueError):
    """A query cursor is malformed or bound to another snapshot/query."""


_PREFIX = re.compile(r"[A-Z][A-Z0-9]{0,7}\Z")
_SAFE_INTEGER = (1 << 53) - 1
_SURROGATE = re.compile(r"[\ud800-\udfff]")


def new_id(prefix: str) -> str:
    """Create a canonical uppercase ULID with the caller's registry prefix."""
    if not isinstance(prefix, str) or not _PREFIX.fullmatch(prefix):
        raise ValueError("prefix must be a canonical uppercase registry prefix")
    value = ((time.time_ns() // 1_000_000) << 80) | int.from_bytes(secrets.token_bytes(10), "big")
    encoded = ""
    for _ in range(ULID_LENGTH):
        encoded = ULID_ALPHABET[value & 31] + encoded
        value >>= 5
    return f"{prefix}-{encoded}"


def canonical_json(value: Any) -> bytes:
    """Encode a finite JSON value deterministically without changing Unicode."""
    if isinstance(value, (FrozenDict, FrozenText)) and hasattr(value, '_payload_bytes'):
        return value._payload_bytes
    validate_storage_value(value)
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n").encode("utf-8")


def exact_content_hash(value: Any) -> str:
    """Identity of an exact logical payload, not a file or semantic projection."""
    return hashlib.sha256(canonical_json(value)).hexdigest()


class ResearchRepository:
    """Read and publish version-five record-family files through one Git CAS."""

    def __init__(self, repository: Path, instance_id: str, *, contract: StateContract | None = None) -> None:
        self._store = GitStateStore(repository, instance_id)
        self.contract = contract or default_state_contract()

    @property
    def git_dir(self) -> Path:
        """Repository identity for process-wide caches such as VERIFIED_ARTIFACTS."""
        return self._store._git_dir

    def register_family(self, root: str, name: str, **kwargs: Any) -> None:
        """Register a family owner before that family is persisted."""
        if kwargs.get("schema") is not None:
            from .state_contract import check_schema
            check_schema(kwargs["schema"])
        self.contract.register_family(root, name, **kwargs)

    def initialize(self, instance, runtime):
        if self._store.read_snapshot().head is not None:
            raise ValueError("the instance ref already has an initial state")
        candidate = self.validate_candidate(instance, runtime)
        head = self._store.publish(None, candidate["files"]).head
        self._remember_published(head, candidate)
        return head

    def _read_key(self, head):
        return (str(self.git_dir), head, _contract_key(self.contract))

    def _descriptors(self, head):
        """The cached (instance, runtime, record descriptors) of ``head``, uncopied.

        A snapshot read validates records without describing them. The exact
        record rows are rebuilt from the retained bytes the first time a caller
        asks, and kept with the cache entry.
        """
        instance, runtime, descriptors, files = self._read_documents(head)
        if descriptors is None:
            records = {path: raw for path, raw in files.items() if not path.startswith("runtime/artifacts/")}
            descriptors = _decode_families(records, self.contract, self._store.object_format,
                                           read_payload=files.__getitem__, git_dir=self.git_dir,
                                           describe=True)[2]
            _remember_read(self._read_key(head), (instance, runtime, descriptors, files))
        return instance, runtime, descriptors

    @measured('snapshot_read_validation')
    def _read_documents(self, head):
        """Validate one snapshot and retain its exact non-artifact file bytes.

        The result is the shared cache entry. Callers that return or mutate
        state copy it; a publication parent is only compared, never copied.
        A head this process did not publish (startup, another writer after a
        CAS conflict) is validated in full the first time it is read.
        """
        from .operation_trace import phase
        key = self._read_key(head)
        cached = _VALIDATED_READS.get(key)
        if cached is not None:
            _VALIDATED_READS.move_to_end(key)
            return cached
        paths = self._store._tree_paths(head)
        # Sealed artifacts are not parsed or loaded just to reconstruct state.
        files = self._store.read_many(head, sorted(p for p in paths if not p.startswith("runtime/artifacts/")))
        payload_bytes = {}
        def read_payload(path):
            if path not in payload_bytes:
                payload_bytes[path] = self._store.read_bytes(head, path)
            return payload_bytes[path]
        read_payload.decoded = {}
        with phase('snapshot_decode', snapshot=head):
            instance, runtime, _ = _decode_families(files, self.contract, self._store.object_format,
                                                    read_payload=read_payload, git_dir=self.git_dir)
        self.contract.validate(instance, runtime)
        # Stored bytes are outside the trust boundary; the published numbering is checked on read.
        check_sequence(event_rows(runtime.get("events", [])), runtime.get("event_cursor"))
        self._validate_artifact_evidence(runtime, head)
        result = (instance, runtime, None, {**files, **payload_bytes})
        _remember_read(key, result)
        return result

    def _remember_published(self, head, candidate):
        """Enter a just-published candidate as its head's validated read.

        The candidate passed the same schema, relation, event and evidence
        checks as a read (event numbering is assigned contiguously during
        validation), and the head's files are exactly its encoded files, so
        reading the head back would re-prove the same facts. Its payload
        blobs are the canonical bytes whose digests name their paths.
        """
        files = candidate["files"]
        for path in files:
            if path.startswith("runtime/artifacts/payload-"):
                mark_artifact_verified(self.git_dir, path, path.split("/")[2].removeprefix("payload-"),
                                       len(files[path]))
        _remember_read(self._read_key(head), (candidate["instance"], candidate["runtime"], None, files))

    def load(self, snapshot=None):
        head = self._resolve_snapshot(snapshot)
        instance, runtime = deepcopy(self._read_documents(head)[:2])
        return head, instance, runtime

    def view(self, snapshot=None):
        """Like :meth:`load`, but return the shared validated state without copying it.

        The caller only reads the result; mutating it would corrupt the
        process-wide snapshot cache.
        """
        head = self._resolve_snapshot(snapshot)
        instance, runtime = self._read_documents(head)[:2]
        return head, instance, runtime

    def published_state(self, head):
        """The validated (instance, runtime) this process holds for ``head``, or None.

        A cache lookup only: nothing is read, validated or copied, and the
        caller only compares the result. None means the entry was evicted.
        """
        entry = _VALIDATED_READS.get(self._read_key(head))
        return None if entry is None else entry[:2]

    def validate_candidate(self, instance, runtime, expected_head=None, *, artifacts=None):
        """Pure candidate check, including parent event facts when supplied.

        The returned views are detached. Callers reload after publication to
        observe assigned events. No rejected/CAS-losing proposal mutates them.
        :meth:`save_validated` publishes the result without validating it again.
        """
        return self._validate_candidate(instance, runtime, expected_head, artifacts=artifacts)

    @measured('candidate_validation')
    def _validate_candidate(self, instance, runtime, expected_head=None, *, artifacts=None):
        if not isinstance(instance, dict) or not isinstance(runtime, dict):
            raise ValueError("instance and runtime must be objects")
        instance = deepcopy(instance)
        runtime = deepcopy(runtime)
        instance, runtime = seal_large(instance), seal_large(runtime)
        if instance.get("object_format", self._store.object_format) != self._store.object_format:
            raise ValueError("persisted object_format differs from Git")
        instance["object_format"] = self._store.object_format
        parent = None
        parent_instance, parent_runtime = {}, {}
        if expected_head is not None:
            parent_instance, parent_runtime, _, parent_files = self._read_documents(expected_head)
            parent = (parent_instance, parent_runtime, parent_files)
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
        # The parent was validated under this contract; records it already
        # holds unchanged skip record-local checks (StateContract.validate).
        self.contract.validate(instance, runtime, parent=parent[:2] if parent else None)
        # Encoding checks the storage value domain of each record it
        # serializes; a record equal to the parent's reuses the parent's bytes.
        files = _encode_families(instance, runtime, self.contract, self._store.object_format, parent=parent)
        supplied = self._snapshot_artifacts(artifacts) or {}
        for path in files.keys() & supplied.keys():
            if files[path] != supplied[path]:
                raise ValueError('immutable artifact differs from encoded state: ' + path)
        # Evidence validation and publication must see the same merged bytes.
        self._validate_artifact_evidence(runtime, expected_head, {**files, **supplied})
        self._store._validate_candidate_paths(set(files) | set(supplied))
        return {"instance": instance, "runtime": runtime, "files": files,
                "contract": self.contract.manifest(), "valid": True, "artifacts": supplied,
                "basis": {"head": expected_head, "validation_generation": self.contract.validation_generation}}

    def save_with_state(self, expected_head, instance, runtime, *, artifacts=None):
        """Validate and atomically publish once, returning the published normalized views."""
        self._precheck_head(expected_head)
        candidate = self._validate_candidate(instance, runtime, expected_head, artifacts=artifacts)
        return self._publish_candidate(expected_head, candidate)

    def save_validated(self, expected_head, candidate):
        """Publish a :meth:`validate_candidate` result without validating it again.

        The candidate must have been validated against ``expected_head`` under
        this contract's current validation generation. Any other candidate is
        validated in full first, as :meth:`save_with_state` would.
        """
        self._precheck_head(expected_head)
        if candidate.get("basis") != {"head": expected_head,
                                      "validation_generation": self.contract.validation_generation}:
            candidate = self._validate_candidate(candidate["instance"], candidate["runtime"], expected_head,
                                                 artifacts=candidate.get("artifacts") or None)
        return self._publish_candidate(expected_head, candidate)

    def _precheck_head(self, expected_head):
        self._store._validate_oid(expected_head)
        # Without the writer lock, a ref precheck avoids expensive validation
        # against an already stale head. Under it no other do-math writer can
        # move the ref; the final expected-old-OID update is the sole authority.
        if not self._store._holds_writer_lock and self._store.read_snapshot().head != expected_head:
            from .git_store import GitStateStoreConflict
            raise GitStateStoreConflict("expected head no longer matches the instance ref")

    def _publish_candidate(self, expected_head, candidate):
        old_files = self._read_documents(expected_head)[3]
        files = candidate["files"]
        # Unreferenced payloads remain immutable Git blobs. They are reusable
        # even when the parent decoder did not need to read them into old_files.
        missing = {p for p in files if p.startswith('runtime/artifacts/') and p not in old_files}
        if missing:
            existing = self._store.read_many(expected_head, sorted(missing & self._store._tree_paths(expected_head)))
            for path, raw in existing.items():
                if files[path] != raw:
                    raise ValueError('immutable artifact differs from encoded state: ' + path)
            old_files = {**old_files, **existing}
        changes = {p: None for p in old_files if p not in files and not p.startswith('runtime/artifacts/')}
        changes.update({p: raw for p, raw in files.items() if old_files.get(p) != raw})
        changes.update(candidate["artifacts"])
        published = self._store.publish(expected_head, changes)
        self._remember_published(published.head, candidate)
        _learn_publication(str(self.git_dir), expected_head, published.head, candidate["artifacts"])
        # The remembered candidate is the shared entry; callers mutate their views.
        return published.head, deepcopy(candidate["instance"]), deepcopy(candidate["runtime"])


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

    @staticmethod
    def _artifact_references(runtime):
        """Immutable byte evidence rows (ref, sha256, bytes or None) named by runtime."""
        references = [(ref, row["evidence_hashes"][ref], None)
            for row in runtime.get("academic_resolution_records", [])
            for ref in row["evidence_refs"] if ref.startswith("runtime/artifacts/")]
        for checkpoint in runtime.get("checkpoints", {}).values():
            for observation in (checkpoint, checkpoint.get("final_observation", {})):
                references.extend((row['artifact_ref'], row['sha256'], row['bytes'])
                                  for row in observation.get('evidence_files', []))
                if observation.get("observation_evidence_complete") is True and observation.get("observation_evidence_omitted"):
                    raise ValueError("complete observation evidence cannot contain omissions")
                references.extend((row["artifact_ref"], row["sha256"], row["bytes"])
                                  for row in observation.get("observation_sources", []))
        return references

    def _validate_artifact_evidence(self, runtime, head, artifacts=None):
        """Resolve immutable byte evidence separately from record identities.

        Existing artifact bundles are immutable, so a row this process already
        matched (VERIFIED_ARTIFACTS) is not read again; only new rows and rows
        whose bytes are supplied with this candidate are compared.
        """
        references = self._artifact_references(runtime)
        if not references:
            return
        supplied = artifacts or {}
        for ref, _, _ in references:
            if not ref.startswith("runtime/artifacts/"):
                raise ValueError("artifact evidence must use the immutable artifact namespace")
            self._store._validate_path(ref)
        pending = [row for row in references
                   if row[0] in supplied or not artifact_verified(self.git_dir, *row)]
        wanted = sorted({ref for ref, _, _ in pending if ref not in supplied})
        available = self._store._tree_paths(head) if head and wanted else set()
        stored = self._store.read_many(head, [ref for ref in wanted if ref in available]) if available else {}
        for ref, digest, size in pending:
            raw = supplied.get(ref)
            if raw is None:
                raw = stored.get(ref)
            verify_artifact(self.git_dir, ref, raw, digest, size)

    def load_records(self, snapshot=None):
        """Load one validated snapshot together with its exact persisted record rows."""
        head = self._resolve_snapshot(snapshot)
        instance, runtime, rows = deepcopy(self._descriptors(head))
        return head, instance, runtime, [{**row, "snapshot": head} for row in rows]

    def records(self, snapshot=None, *, family=None, root=None):
        """Enumerate exact persisted record bytes, including singleton authorities.

        Only the selected rows are copied.
        """
        head = self._resolve_snapshot(snapshot)
        return [{**deepcopy(row), "snapshot": head} for row in self._descriptors(head)[2]
                if (family is None or row["family"] == family) and (root is None or row["root"] == root)]

    def read_record(self, record_id, snapshot=None):
        head = self._resolve_snapshot(snapshot)
        matches = [row for row in self._descriptors(head)[2] if row["id"] == record_id]
        if len(matches) != 1:
            raise KeyError("record not found: " + str(record_id))
        return {**deepcopy(matches[0]), "snapshot": head}

    def read(self, path: str, snapshot: str | None = None) -> bytes:
        """Read bytes from an exact or current state snapshot.

        Artifact bytes this process wrote or read at this snapshot, or at an
        earlier head it published this snapshot from, are not read again.
        """
        head = self._resolve_snapshot(snapshot)
        if not isinstance(path, str) or not path.startswith("runtime/artifacts/"):
            return self._store.read_bytes(head, path)
        self._store._validate_path(path)
        git_dir = str(self.git_dir)
        row = _known_artifact(git_dir, path, head)
        if row is not None and row[2] is not None:
            return row[2]
        raw = self._store.read_bytes(head, path)
        _learn_artifact(git_dir, path, head, len(raw), raw)
        return raw

    def read_many(self, paths: list[str], snapshot: str | None = None, *, missing: str = "raise") -> dict[str, bytes]:
        """Read exact blobs together without changing their logical paths.

        ``missing="omit"`` leaves absent paths out instead of failing the batch.
        """
        return self._store.read_many(self._resolve_snapshot(snapshot), paths, missing=missing)

    def blob_sizes(self, paths: list[str], snapshot: str | None = None, *, missing: str = "raise") -> dict[str, int]:
        """Read stored lengths without blob bytes; ``missing`` is as for :meth:`read_many`.

        Artifact lengths this process already knows at this snapshot (see
        :meth:`read`) are not asked of Git again.
        """
        head = self._resolve_snapshot(snapshot)
        wanted = list(dict.fromkeys(paths))
        git_dir = str(self.git_dir)
        known = {}
        for path in wanted:
            if isinstance(path, str) and path.startswith("runtime/artifacts/"):
                row = _known_artifact(git_dir, path, head)
                if row is not None:
                    self._store._validate_path(path)
                    known[path] = row[1]
        rest = [path for path in wanted if path not in known]
        sizes = self._store.blob_sizes(head, rest, missing=missing)
        for path, size in sizes.items():
            if path.startswith("runtime/artifacts/"):
                _learn_artifact(git_dir, path, head, size)
        return {path: known[path] if path in known else sizes[path]
                for path in wanted if path in known or path in sizes}

    def list_files(self, prefix: str, snapshot: str | None = None) -> list[str]:
        """List files below one POSIX state prefix in stable lexical order."""
        head = self._resolve_snapshot(snapshot)
        normalized_prefix = _validate_prefix(prefix)
        return sorted(path for path in self._store._tree_paths(head) if path.startswith(normalized_prefix))

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
        paths = self.list_files(normalized_prefix, head)
        if text:
            # Content matching requires scanning the snapshot.
            for offset in range(0, len(paths), 16):
                batch = paths[offset:offset + 16]
                contents = self._store.read_many(head, batch)
                for path in batch:
                    content = contents[path]
                    if text not in path and needle not in content:
                        continue
                    matches.append({"path": path, "size": len(content), "sha256": hashlib.sha256(content).hexdigest()})
        else:
            matches = [{"path": path} for path in paths]
        total = len(matches)
        start = 0
        if last_path is not None:
            matching_indexes = [index for index, item in enumerate(matches) if item["path"] == last_path]
            if len(matching_indexes) != 1:
                raise RepositoryCursorError("cursor path is not present in this query result")
            start = matching_indexes[0] + 1
        items = matches[start:start + limit]
        if not text:
            hydrated = []
            for offset in range(0, len(items), 16):
                batch = [item["path"] for item in items[offset:offset + 16]]
                contents = self._store.read_many(head, batch)
                hydrated.extend({"path": path, "size": len(contents[path]),
                                 "sha256": hashlib.sha256(contents[path]).hexdigest()} for path in batch)
            items = hydrated
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
        no_reparse(destination)
        if destination.exists():
            if not destination.is_dir() or any(destination.iterdir()):
                raise ValueError("export destination must be absent or an empty directory")
        else:
            destination.mkdir(parents=True)
        # Proves the (possibly new) destination root once for every file below.
        boundary = PhysicalBoundary(destination)

        files = sorted({path for prefix in normalized_prefixes for path in self.list_files(prefix, head)})
        sizes = self._store.blob_sizes(head, files)
        cursor = 0
        while cursor < len(files):
            batch, size = [], 0
            while cursor < len(files) and len(batch) < 64:
                path = files[cursor]
                if batch and size + sizes[path] > 8 * 1024 * 1024:
                    break
                batch.append(path); size += sizes[path]; cursor += 1
            contents = self._store.read_many(head, batch)
            for path in batch:
                output = destination.joinpath(*path.split('/'))
                output.parent.mkdir(parents=True, exist_ok=True)
                with boundary.open(output, 'xb') as stream:
                    stream.write(contents[path])
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
        value = json.loads(data.decode("utf-8"), object_pairs_hook=unique_pairs, parse_constant=reject_constant)
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as error:
        raise ValueError("stored document is not strict JSON") from error
    if not isinstance(value, dict):
        raise ValueError("stored instance and runtime documents must be JSON objects")
    if canonical_json(value) != data:
        raise ValueError("stored document is not canonical JSON")
    return value


def validate_storage_value(value: Any) -> None:
    """Validate the exact storage value domain without constructing JSON bytes.

    Plain ``dict``, ``list`` and ``str`` values, nearly every node of a state,
    take a direct path with the same rules; string leaves are checked in
    place, and an ASCII string holds no surrogate. Other types (subclasses,
    sealed payloads) fall through to the general rules.
    """
    kind = type(value)
    if kind is dict:
        for key, item in value.items():
            if type(key) is not str:
                if not isinstance(key, str):
                    raise ValueError("JSON object keys must be strings")
                validate_storage_value(key)
            elif not key.isascii() and _SURROGATE.search(key):
                raise ValueError("JSON strings cannot contain surrogate code points")
            if type(item) is str:
                if not item.isascii() and _SURROGATE.search(item):
                    raise ValueError("JSON strings cannot contain surrogate code points")
            else:
                validate_storage_value(item)
        return
    if kind is list:
        for item in value:
            validate_storage_value(item)
        return
    if kind is str:
        if not value.isascii() and _SURROGATE.search(value):
            raise ValueError("JSON strings cannot contain surrogate code points")
        return
    if isinstance(value, (FrozenDict, FrozenText)) and hasattr(value, '_payload_bytes'):
        return  # Sealing validated exact bytes and these values cannot be edited.
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
    return base64.urlsafe_b64encode(canonical_json(dict(value))).decode("ascii").rstrip("=")


def _decode_cursor(cursor: str) -> dict[str, Any]:
    if not isinstance(cursor, str) or not cursor:
        raise RepositoryCursorError("cursor must be a non-empty string")
    try:
        encoded = cursor.encode("ascii")
        data = base64.b64decode(encoded + b"=" * (-len(encoded) % 4), altchars=b"-_", validate=True)
        value = json.loads(data.decode("utf-8"), object_pairs_hook=unique_pairs, parse_constant=reject_constant)
    except (UnicodeError, ValueError, json.JSONDecodeError) as error:
        raise RepositoryCursorError("cursor is malformed") from error
    if (not isinstance(value, dict) or set(value) != {"snapshot", "prefix", "text", "last_path"}
            or any(not isinstance(value[key], str) for key in ("snapshot", "prefix", "text", "last_path"))):
        raise RepositoryCursorError("cursor has an invalid shape")
    return value


def semantic_content_hash(value, projection=None):
    """Hash an explicitly selected semantic projection, distinct from file bytes."""
    if projection is not None:
        if not isinstance(value, Mapping) or any(key not in value for key in projection):
            raise ValueError("semantic projection fields must exist")
        value = {key: value[key] for key in projection}
    return exact_content_hash(value)


def _record_path(root, name, identifier):
    return f"{root}/{name}/{identifier}.json"


def _envelope(family, value):
    return {"contract_id": STATE_CONTRACT_ID, "family": family, "record": value}


_ABSENT = object()


@measured('state_encoding')
def _encode_families(instance, runtime, contract, object_format, *, parent=None):
    """Encode the record-family files of one state.

    ``parent`` is the publication parent's (instance, runtime, files). A record
    equal to the parent's record at the same family and ID keeps the parent's
    file bytes: canonical encoding is deterministic, and those bytes were
    produced by an earlier encoding or checked canonical when read. Only the
    records serialized here pass the storage value check of ``canonical_json``.
    """
    files = {}
    installed = contract.manifest()
    parent_files = parent[2] if parent is not None else {}
    for index, (root, state) in enumerate((("research", instance), ("runtime", runtime))):
        parent_state = parent[index] if parent is not None else {}
        containers, metadata = {}, {}
        for name, value in sorted(state.items()):
            family = contract.family(root, name)
            if family.shape == "metadata":
                containers[name] = {"shape": "metadata"}
                metadata[name] = value
                continue
            prior = parent_state.get(name, _ABSENT)
            if family.shape == "singleton":
                identifier = value["id"] if family.identity else "state"
                entries = [(identifier, value)]
                prior = {identifier: prior}
                descriptor = {"shape": "singleton", **({"id": identifier} if family.identity else {})}
            elif family.shape == "map":
                entries = sorted(value.items())
                descriptor = {"shape": "map", "ids": [k for k, _ in entries]}
            else:
                entries = [(r["id"], r) for r in value]
                descriptor = {"shape": "list", "ids": [k for k, _ in entries]}
                if isinstance(prior, list):
                    prior = {row["id"]: row for row in prior}
            containers[name] = descriptor
            for identifier, record in entries:
                path = _record_path(root, name, identifier)
                envelope, blobs = encode(_envelope(name, record))
                files.update(blobs)
                if path in parent_files and isinstance(prior, dict) and prior.get(identifier, _ABSENT) == record:
                    files[path] = parent_files[path]
                else:
                    files[path] = canonical_json(envelope)
        envelope, blobs = encode(_envelope('metadata', metadata))
        files.update(blobs)
        files[f"{root}/_state/metadata.json"] = canonical_json(envelope)
        # Each root describes only its own containers, preserving research OID
        # when only runtime families or event membership change.
        files[f"{root}/_state/manifest.json"] = canonical_json({
            "contract": installed, "object_format": object_format, "containers": containers})
    return files


def _decode_families(files, contract, object_format, *, read_payload=None, git_dir=None, describe=False):
    """Decode one snapshot's record files and check their family layout.

    Returns (research, runtime, descriptors). The descriptors, the exact
    persisted record rows, are built only with ``describe``; otherwise the
    third value is None.
    """
    if read_payload is None:
        def read_payload(path):
            raise ValueError('immutable payload reader required: ' + path)
    states, descriptors, expected = {}, [], set()
    installed = contract.manifest()
    for root in ("research", "runtime"):
        manifest_path = f"{root}/_state/manifest.json"
        if manifest_path not in files:
            raise ValueError("missing family manifest: " + root)
        manifest = _decode_object(files[manifest_path])
        declared = manifest.get("contract")
        if (set(manifest) != {"contract", "object_format", "containers"}
                or not isinstance(declared, dict) or set(declared) != set(installed)
                or declared.get("contract_id") != installed["contract_id"]
                or not is_sha256(declared.get("sha256"))):
            raise ValueError("unsupported stored contract/schema version or manifest")
        # The digest identifies the writer. Validate every layout and record
        # with the installed schema; loading never rewrites saved values.
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
        metadata = decode(envelope, read_payload, git_dir)
        if not isinstance(metadata, dict) or envelope.get('contract_id') != STATE_CONTRACT_ID or envelope.get('family') != 'metadata':
            raise ValueError("invalid root metadata envelope: " + root)
        declared_metadata = {name for name, descriptor in manifest["containers"].items()
                             if descriptor == {"shape": "metadata"}}
        if set(metadata) != declared_metadata:
            raise ValueError("metadata fields differ from declared membership: " + repr(sorted(set(metadata) ^ declared_metadata)))
        expected.add(metadata_path)
        if describe:
            descriptors.append({"root": root, "family": "metadata", "id": None, "path": metadata_path,
                "bytes": raw_metadata, "sha256": hashlib.sha256(raw_metadata).hexdigest(),
                "record": {}, "json_pointer": "/record", "payload_refs": envelope.get('payloads', [])})
            metadata_descriptor = descriptors[-1]
        for name, descriptor in manifest["containers"].items():
            family = contract.family(root, name)
            if family is None or not isinstance(descriptor, dict):
                raise ValueError("unregistered manifest family: " + name)
            shape = descriptor.get("shape")
            if shape != family.shape:
                raise ValueError("manifest shape differs from registered family: " + name)
            if shape == "metadata":
                if descriptor != {"shape": "metadata"}:
                    raise ValueError("invalid metadata descriptor: " + name)
                # The decoded metadata is this call's own value; no copy is needed.
                state[name] = metadata[name]
                if describe:
                    metadata_descriptor["record"][name] = state[name]
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
                row = decode(envelope, read_payload, git_dir)
                if envelope.get('contract_id') != STATE_CONTRACT_ID or envelope.get('family') != name:
                    raise ValueError("invalid record envelope: " + path)
                if family.identity and (not isinstance(row, dict) or row.get("id") != identifier):
                    raise ValueError("record path and id differ: " + path)
                rows.append(row)
                if describe:
                    descriptors.append({"root": root, "family": name,
                        "id": identifier if family.identity else None, "path": path,
                        "bytes": raw, "sha256": hashlib.sha256(raw).hexdigest(), "record": row,
                        "json_pointer": "/record", "payload_refs": envelope.get('payloads', [])})
            state[name] = rows[0] if shape == "singleton" else dict(zip(ids, rows)) if shape == "map" else rows
    if set(files) != expected:
        raise ValueError("undeclared state files: " + repr(sorted(set(files) - expected)))
    return states["research"], states["runtime"], descriptors if describe else None
