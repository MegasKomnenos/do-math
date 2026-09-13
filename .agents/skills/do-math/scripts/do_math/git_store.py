"""Git plumbing storage for one immutable do-math instance state chain.

The store publishes bytes and Git object relationships only.  It does not
validate record schemas and does not activate a research instance; those
semantic decisions belong to callers above this storage primitive.
"""

from __future__ import annotations

from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from dataclasses import dataclass
import os
from pathlib import Path
import re
import subprocess
import tempfile
from typing import Final


class GitStateStoreError(RuntimeError):
    """A Git storage operation could not establish the requested state."""


class GitStateStoreConflict(GitStateStoreError):
    """The expected state head was no longer the authoritative ref value."""


class GitStateStoreLockError(GitStateStoreError):
    """Another local writer currently owns this instance's advisory lock."""


@dataclass(frozen=True, slots=True)
class StateSnapshot:
    """The authoritative commit and its two required top-level subtrees."""

    head: str | None
    research_tree: str | None
    runtime_tree: str | None


_INSTANCE_ID = re.compile(r"RI-[0-7][0-9A-HJKMNP-TV-Z]{25}\Z")
_HEX = re.compile(r"[0-9a-f]+\Z")
_WINDOWS_RESERVED: Final = {
    "CON", "PRN", "AUX", "NUL",
    *(f"COM{number}" for number in range(1, 10)),
    *(f"LPT{number}" for number in range(1, 10)),
}


class GitStateStore:
    """Publish one parent-linked state chain at ``refs/heads/do-math/<id>``.

    ``publish`` uses Git's expected-old-OID ref update as its concurrency
    guarantee.  ``writer_lock`` is a separate, optional local OS lock for
    callers that need to serialize work before that final CAS.
    """

    def __init__(self, repository: str | os.PathLike[str], instance_id: str) -> None:
        if not isinstance(instance_id, str) or not _INSTANCE_ID.fullmatch(instance_id):
            raise ValueError("instance_id must be the registry RI-prefixed canonical ULID")
        self.repository = Path(repository).resolve()
        if not self.repository.is_dir():
            raise ValueError("repository must be an existing Git work tree or bare repository")
        self.instance_id = instance_id
        self.ref = f"refs/heads/do-math/{instance_id}"
        self._git_dir = Path(self._git_text("rev-parse", "--absolute-git-dir")).resolve()
        self.object_format = self._git_text("rev-parse", "--show-object-format")
        if self.object_format not in {"sha1", "sha256"}:
            raise GitStateStoreError(f"unsupported Git object format: {self.object_format!r}")
        self.oid_length = 40 if self.object_format == "sha1" else 64

    def read_snapshot(self) -> StateSnapshot:
        """Return the current state commit and its research/runtime tree OIDs."""
        head = self._head()
        if head is None:
            return StateSnapshot(None, None, None)
        return StateSnapshot(head, self._subtree_oid(head, "research"), self._subtree_oid(head, "runtime"))

    def read_bytes(self, commit: str, path: str) -> bytes:
        """Read exact blob bytes from an explicit, format-valid state commit."""
        self._validate_oid(commit)
        self._validate_path(path)
        return self._git("cat-file", "blob", f"{commit}:{path}").stdout

    def publish(self, expected_head: str | None, changes: Mapping[str, bytes | None]) -> StateSnapshot:
        """Create and atomically publish one complete state commit.

        ``expected_head`` is ``None`` only for the parentless initial commit.
        Every later commit has exactly that expected commit as its only parent.
        A failed expected-old-OID check raises :class:`GitStateStoreConflict`
        and leaves the authoritative ref unchanged.
        """
        if expected_head is not None:
            self._validate_oid(expected_head)
        normalized_changes = self._validate_changes(changes)
        current = self._head()
        if current != expected_head:
            raise GitStateStoreConflict("expected head no longer matches the instance ref")

        existing_paths = self._tree_paths(expected_head) if expected_head is not None else set()
        self._validate_artifact_changes(existing_paths, normalized_changes)
        candidate_paths = set(existing_paths)
        for path, contents in normalized_changes.items():
            if contents is None:
                candidate_paths.discard(path)
            else:
                candidate_paths.add(path)
        self._validate_candidate_paths(candidate_paths)
        if expected_head is None:
            if not any(path.startswith("research/") for path in candidate_paths):
                raise ValueError("the initial state must contain a research subtree")
            if not any(path.startswith("runtime/") for path in candidate_paths):
                raise ValueError("the initial state must contain a runtime subtree")

        with self._private_index() as index_environment:
            if expected_head is None:
                self._git("read-tree", "--empty", env=index_environment)
            else:
                self._git("read-tree", f"{expected_head}^{{tree}}", env=index_environment)
            index_records = bytearray()
            for path, contents in normalized_changes.items():
                if contents is None:
                    index_records.extend(f"0 {'0' * self.oid_length}\t{path}".encode("utf-8"))
                else:
                    blob = self._git("hash-object", "-w", "--stdin", input=contents).stdout.decode("ascii").strip()
                    self._validate_oid(blob)
                    index_records.extend(f"100644 {blob}\t{path}".encode("utf-8"))
                index_records.append(0)
            if index_records:
                self._git("update-index", "-z", "--index-info", input=bytes(index_records), env=index_environment)
            tree = self._git("write-tree", env=index_environment).stdout.decode("ascii").strip()
        self._validate_oid(tree)
        research_tree = self._subtree_oid(tree, "research")
        runtime_tree = self._subtree_oid(tree, "runtime")

        command = ["commit-tree", tree]
        if expected_head is not None:
            command.extend(["-p", expected_head])
        commit = self._git(*command, input=b"do-math state\n").stdout.decode("ascii").strip()
        self._validate_oid(commit)

        old = expected_head if expected_head is not None else "0" * self.oid_length
        updated = self._git("update-ref", self.ref, commit, old, check=False)
        if updated.returncode:
            raise GitStateStoreConflict("state ref changed before the publish compare-and-swap")
        return StateSnapshot(commit, research_tree, runtime_tree)

    @contextmanager
    def writer_lock(self) -> Iterator[None]:
        """Acquire a non-stale, same-instance advisory OS lock in the Git dir."""
        lock_path = self._git_dir / f"do-math-{self.instance_id}.lock"
        descriptor = os.open(lock_path, os.O_RDWR | os.O_CREAT, 0o600)
        try:
            if os.fstat(descriptor).st_size == 0:
                os.write(descriptor, b"\0")
            os.lseek(descriptor, 0, os.SEEK_SET)
            try:
                if os.name == "nt":
                    import msvcrt

                    msvcrt.locking(descriptor, msvcrt.LK_NBLCK, 1)
                else:
                    import fcntl

                    fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except OSError as error:
                raise GitStateStoreLockError("another local writer owns this instance lock") from error
            try:
                yield
            finally:
                os.lseek(descriptor, 0, os.SEEK_SET)
                if os.name == "nt":
                    msvcrt.locking(descriptor, msvcrt.LK_UNLCK, 1)
                else:
                    fcntl.flock(descriptor, fcntl.LOCK_UN)
        finally:
            os.close(descriptor)

    def _head(self) -> str | None:
        result = self._git("rev-parse", "--verify", "--quiet", self.ref, check=False)
        if result.returncode:
            if result.returncode == 1 and not result.stderr:
                return None
            detail = result.stderr.decode("utf-8", "replace").strip()
            raise GitStateStoreError(f"cannot resolve existing state ref: {detail}")
        oid = result.stdout.decode("ascii").strip()
        self._validate_oid(oid)
        object_type = self._git("cat-file", "-t", oid, check=False)
        if object_type.returncode:
            detail = object_type.stderr.decode("utf-8", "replace").strip()
            raise GitStateStoreError(f"state ref points to an unreadable object: {detail}")
        if object_type.stdout.decode("ascii").strip() != "commit":
            raise GitStateStoreError("state ref must point to a commit")
        return oid

    def _subtree_oid(self, commit_or_tree: str, name: str) -> str:
        result = self._git("rev-parse", "--verify", f"{commit_or_tree}:{name}", check=False)
        if result.returncode:
            raise GitStateStoreError(f"state object lacks required {name!r} subtree")
        oid = result.stdout.decode("ascii").strip()
        self._validate_oid(oid)
        object_type = self._git("cat-file", "-t", oid).stdout.decode("ascii").strip()
        if object_type != "tree":
            raise GitStateStoreError(f"state {name!r} entry must be a tree")
        return oid

    def _tree_paths(self, commit: str) -> set[str]:
        raw_paths = self._git("ls-tree", "-r", "-z", "--name-only", commit).stdout.split(b"\0")
        paths: set[str] = set()
        for raw_path in raw_paths:
            if not raw_path:
                continue
            try:
                path = raw_path.decode("utf-8")
            except UnicodeDecodeError as error:
                raise GitStateStoreError("existing state contains a non-UTF-8 path") from error
            self._validate_path(path)
            paths.add(path)
        return paths

    def _validate_changes(self, changes: Mapping[str, bytes | None]) -> dict[str, bytes | None]:
        if not isinstance(changes, Mapping):
            raise TypeError("changes must be a mapping of paths to bytes or None")
        normalized: dict[str, bytes | None] = {}
        folded: dict[str, str] = {}
        for path, contents in changes.items():
            self._validate_path(path)
            folded_path = path.casefold()
            prior = folded.get(folded_path)
            if prior is not None and prior != path:
                raise ValueError(f"Windows case-colliding paths: {prior!r} and {path!r}")
            folded[folded_path] = path
            if contents is not None and not isinstance(contents, bytes):
                raise TypeError("change contents must be bytes or None")
            normalized[path] = contents
        return normalized

    def _validate_candidate_paths(self, paths: set[str]) -> None:
        folded_prefixes: dict[str, str] = {}
        for path in paths:
            self._validate_path(path)
            parts = path.split("/")
            for position in range(1, len(parts) + 1):
                original = "/".join(parts[:position])
                key = original.casefold()
                prior = folded_prefixes.get(key)
                if prior is not None and prior != original:
                    raise ValueError(f"Windows case-colliding path segments: {prior!r} and {original!r}")
                folded_prefixes[key] = original

    def _validate_artifact_changes(self, existing_paths: set[str], changes: Mapping[str, bytes | None]) -> None:
        existing_bundles = {
            path.split("/")[2]
            for path in existing_paths
            if path.startswith("runtime/artifacts/") and len(path.split("/")) >= 4
        }
        for path in changes:
            parts = path.split("/")
            if parts[:2] == ["runtime", "artifacts"] and parts[2] in existing_bundles:
                raise ValueError("existing runtime artifact bundles are immutable")

    def _validate_path(self, path: str) -> None:
        if not isinstance(path, str) or not path:
            raise ValueError("path must be a non-empty POSIX relative path")
        if path.startswith("/") or "\\" in path or "\x00" in path:
            raise ValueError("path must be a POSIX relative path")
        parts = path.split("/")
        if len(parts) < 2 or parts[0] not in {"research", "runtime"}:
            raise ValueError("state paths must be files below research/ or runtime/")
        for part in parts:
            if not part or part in {".", ".."} or part[-1] in {".", " "}:
                raise ValueError("path contains an invalid segment")
            if any(character in '<>:"|?*' or ord(character) < 32 for character in part):
                raise ValueError("path contains a Windows-invalid segment")
            device_name = part.rstrip(". ").split(".", 1)[0].upper()
            if device_name in _WINDOWS_RESERVED:
                raise ValueError("path contains a reserved Windows device name")
        if parts[:2] == ["runtime", "artifacts"] and len(parts) < 4:
            raise ValueError("artifact paths must name a bundle and a file")

    def _validate_oid(self, oid: str) -> None:
        if not isinstance(oid, str) or len(oid) != self.oid_length or not _HEX.fullmatch(oid):
            raise ValueError(f"OID must be a lowercase {self.object_format} object ID")

    @contextmanager
    def _private_index(self) -> Iterator[dict[str, str]]:
        descriptor, index_path = tempfile.mkstemp(prefix="do-math-index-", dir=self._git_dir)
        os.close(descriptor)
        environment = {"GIT_INDEX_FILE": index_path}
        try:
            yield environment
        finally:
            Path(index_path).unlink(missing_ok=True)
            Path(f"{index_path}.lock").unlink(missing_ok=True)

    def _git_text(self, *arguments: str) -> str:
        return self._git(*arguments).stdout.decode("utf-8").strip()

    def _git(
        self,
        *arguments: str,
        input: bytes | None = None,
        env: Mapping[str, str] | None = None,
        check: bool = True,
    ) -> subprocess.CompletedProcess[bytes]:
        disabled_hooks = getattr(self, "_git_dir", self.repository) / "do-math-disabled-hooks"
        environment = os.environ.copy()
        environment.update({
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_OPTIONAL_LOCKS": "0",
        })
        if env is not None:
            environment.update(env)
        completed = subprocess.run(
            [
                "git", "-C", str(self.repository),
                "-c", "user.name=do-math",
                "-c", "user.email=do-math@invalid",
                "-c", "commit.gpgSign=false",
                "-c", f"core.hooksPath={disabled_hooks}",
                *arguments,
            ],
            input=input,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=environment,
            check=False,
        )
        if check and completed.returncode:
            detail = completed.stderr.decode("utf-8", "replace").strip()
            raise GitStateStoreError(f"git {' '.join(arguments)} failed: {detail}")
        return completed
