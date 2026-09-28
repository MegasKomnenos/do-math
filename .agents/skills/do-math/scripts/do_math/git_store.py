"""Git plumbing storage for one immutable do-math instance state chain.

The store publishes bytes and Git object relationships only.  It does not
validate record schemas and does not activate a research instance; those
semantic decisions belong to callers above this storage primitive.
"""

from __future__ import annotations
from .operation_trace import measured


from collections.abc import Iterator, Mapping
from contextlib import ExitStack, contextmanager
from dataclasses import dataclass
import hashlib
import os
from pathlib import Path
import re
import tempfile
import stat
import time
from typing import Final
import zlib

from .file_io import check_path_segment, no_reparse, os_lock


class GitStateStoreError(RuntimeError):
    """A Git storage operation could not establish the requested state."""


class GitStateStoreConflict(GitStateStoreError):
    """The expected state head was no longer the authoritative ref value."""


class GitStateStoreLockError(GitStateStoreError):
    """Another local writer currently owns this instance's advisory lock."""


@dataclass(frozen=True, slots=True)
class StateSnapshot:
    """The authoritative state commit, or None before the initial publication."""

    head: str | None


@dataclass(frozen=True, slots=True)
class _Tree:
    """One state commit's tree: ``name -> (mode, oid)`` per directory (``""`` is the root).

    ``paths`` are its file paths. A publication shares every untouched
    directory's entries with its parent's ``_Tree``; neither is mutated.
    """

    commit: str
    directories: Mapping[str, Mapping[str, tuple[str, str]]]
    paths: frozenset[str]


_FILE_MODE: Final = "100644"
_TREE_MODE: Final = "40000"

# ULID in Crockford base32: 26 digits, the first at most 7 (48-bit time + 80 random bits).
from .ids import ULID_ALPHABET, ULID_LENGTH, ULID_PATTERN  # noqa: F401  (re-exported)
_HEX = re.compile(r"[0-9a-f]+\Z")
# Archived artifacts live under this prefix; an existing bundle there never changes.
ARTIFACT_ROOT: Final = "runtime/artifacts/"


def is_new_id(prefix: str, value) -> bool:
    """True for ``<prefix>-<ULID>``, the form ``repository.new_id`` creates."""
    return isinstance(value, str) and re.fullmatch(re.escape(prefix) + "-" + ULID_PATTERN, value) is not None


def oid_shape(oid: str) -> str:
    """Validate only OID syntax, not object existence or this instance's format."""
    if not isinstance(oid, str) or len(oid) not in {40, 64} or not _HEX.fullmatch(oid):
        raise ValueError("OID must be a lowercase 40/64-character hexadecimal string")
    return "sha1" if len(oid) == 40 else "sha256"


class GitStateStore:
    """Publish one parent-linked state chain at ``refs/heads/do-math/<id>``.

    ``publish`` uses Git's expected-old-OID ref update as its concurrency
    guarantee.  ``writer_lock`` is a separate, optional local OS lock for
    callers that need to serialize work before that final CAS; while a caller
    holds it, no other do-math writer can move the ref.

    Physical boundaries (no reparse ancestor, local fixed NTFS volume, final
    path) are established when the store is opened and re-established when
    Git reports an error, which is how a move or remount surfaces. They are
    not re-proved before every Git process: racing a path swap is deliberate
    tampering, outside the accidental-change threat model.
    """

    def __init__(self, repository: str | os.PathLike[str], instance_id: str, *, backend=None) -> None:
        if not isinstance(instance_id, str) or not is_new_id("RI", instance_id):
            raise ValueError("instance_id must be the registry RI-prefixed canonical ULID")
        self.repository = Path(repository).absolute()
        self._repository_boundary = PhysicalBoundary(self.repository)
        if not self.repository.is_dir():
            raise ValueError("repository must be an existing Git work tree or bare repository")
        self.instance_id = instance_id
        self.ref = f"refs/heads/do-math/{instance_id}"
        if backend is None:
            from .git_process import GitProcess
            backend = GitProcess()
        self._backend = backend
        # Until Git reports its directory, the work tree stands in for it when
        # a failure re-proves the boundaries.
        self.git_dir = self.repository
        self._git_boundary = self._repository_boundary
        facts = self._call("describe")
        self.git_dir = Path(facts[0]).absolute()
        self._git_boundary = PhysicalBoundary(self.git_dir)
        self.object_format = facts[1].strip()
        if self.object_format not in {"sha1", "sha256"}:
            raise GitStateStoreError(f"unsupported Git object format: {self.object_format!r}")
        self.oid_length = 40 if self.object_format == "sha1" else 64
        # --git-path is relative to the work tree unless Git reports it absolute
        # (a linked worktree's common directory, GIT_OBJECT_DIRECTORY).
        self._objects = self.repository / facts[2].strip()
        # The trees this store last published and last read (see _tree).
        self._published: _Tree | None = None
        self._read: _Tree | None = None
        # Set only while this store holds the writer lock and its own CAS moved the ref.
        self._held_head: str | None = None
        self.holds_writer_lock = False

    def read_snapshot(self) -> StateSnapshot:
        """Return the current state commit, checking that it holds research/runtime trees.

        One batch query resolves the ref, its object type and both subtrees.
        Only when the ref line is missing does ``rev-parse`` separate an absent
        ref from a ref that names a missing object. Under the writer lock, after
        this store's own compare-and-swap, no do-math writer can have moved the
        ref from the commit that CAS installed, so that head is returned unread.
        """
        if self._held_head is not None:
            return StateSnapshot(self._held_head)
        names = ("research", "runtime")
        specs = [self.ref, *(f"{self.ref}:{name}" for name in names)]
        info = self._call("object_info", specs)
        rows = [f"{spec} missing" if found is None else f"{found[0]} {found[1]}" for spec, found in zip(specs, info)]
        if info[0] is None:
            if self._ref_oid() is None:
                return StateSnapshot(None)
            raise GitStateStoreError("state ref points to an unreadable object")
        head, object_type = info[0][0], info[0][1]
        self.validate_oid(head)
        if object_type != "commit":
            raise GitStateStoreError("state ref must point to a commit")
        self._check_subtrees(rows[1:], names)
        return StateSnapshot(head)

    def read_bytes(self, commit: str, path: str) -> bytes:
        """Read exact blob bytes from an explicit, format-valid state commit."""
        self.validate_oid(commit)
        self.validate_path(path)
        found = self._call("read_objects", [f"{commit}:{path}"])[0]
        if found is None or found[0] != "blob":
            # Git refuses this read; as with any Git refusal, a moved repository
            # is reported before the missing blob.
            self._repository_boundary.check()
            self._git_boundary.check()
            raise GitStateStoreError(f"git cat-file blob {commit}:{path} failed: no blob at this path")
        return found[1]

    def read_many(self, commit: str, paths: list[str], *, missing: str = "raise") -> dict[str, bytes]:
        """Read a fixed snapshot in one process, using binary lengths, not lines.

        With ``missing="omit"`` a path absent from the snapshot is left out of
        the result; with ``"raise"`` it fails the whole batch.
        """
        self.validate_oid(commit)
        self._check_missing_mode(missing)
        paths = list(dict.fromkeys(paths))
        for path in paths:
            self.validate_path(path)
        if not paths:
            return {}
        found = self._call("read_objects", [f"{commit}:{path}" for path in paths])
        result = {}
        for path, item in zip(paths, found):
            if item is None and missing == "omit":
                continue
            if item is None or item[0] != "blob":
                raise GitStateStoreError("batch read did not return a blob: " + path)
            result[path] = item[1]
        return result

    def blob_sizes(self, commit: str, paths: list[str], *, missing: str = "raise") -> dict[str, int]:
        """Read object lengths once so callers can bound batch-read memory.

        ``missing`` has the meaning it has for :meth:`read_many`.
        """
        self.validate_oid(commit)
        self._check_missing_mode(missing)
        for path in paths:
            self.validate_path(path)
        if not paths:
            return {}
        info = self._call("object_info", [f'{commit}:{path}' for path in paths])
        result = {}
        for path, found in zip(paths, info):
            if found is None and missing == "omit":
                continue
            if found is None or found[1] != 'blob':
                raise GitStateStoreError('batch size did not return a blob: ' + path)
            result[path] = found[2]
        return result

    @staticmethod
    def _check_missing_mode(missing: str) -> None:
        if missing not in {"raise", "omit"}:
            raise ValueError('missing must be "raise" or "omit"')

    def _write_object(self, kind: bytes, body: bytes) -> str:
        """Store one loose object as installed Git does by default, returning its OID.

        The OID hashes ``"<kind> <size>\\0"`` and the exact body, so writing is
        idempotent: an existing loose object is kept, and a concurrent writer of
        the same object only loses the final rename. Like Git for Windows
        (``core.fsyncObjectFiles=true`` by default) each new object is flushed
        before its final name appears; the directory is not, as Git does not.
        """
        data = b"%s %d\0" % (kind, len(body)) + body
        oid = hashlib.new(self.object_format, data).hexdigest()
        target = self._objects / oid[:2] / oid[2:]
        if target.exists():
            return oid
        target.parent.mkdir(exist_ok=True)
        # Git's prefix, so ``git prune`` removes a temporary a crash leaves behind.
        descriptor, temporary = tempfile.mkstemp(prefix="tmp_obj_", dir=target.parent)
        try:
            with os.fdopen(descriptor, "wb") as stream:
                stream.write(zlib.compress(data, 1))  # core.looseCompression default
                stream.flush()
                os.fsync(stream.fileno())
            os.chmod(temporary, 0o444)  # Git's mode for loose objects (read-only on Windows)
            try:
                os.rename(temporary, target)
            except FileExistsError:
                pass  # Windows: another writer stored the identical object first
        finally:
            if os.path.lexists(temporary):
                os.chmod(temporary, stat.S_IREAD | stat.S_IWRITE)
                os.unlink(temporary)
        return oid

    def _write_tree(self, parent: Mapping[str, Mapping[str, tuple[str, str]]],
                    changes: Mapping[str, bytes | None]) -> tuple[str, dict[str, dict[str, tuple[str, str]]]]:
        """Write each changed blob and the trees above it; other subtrees keep their OIDs.

        Returns the root tree OID and the new directory map. A directory left
        empty disappears from its parent, as it does from Git's index.
        """
        directories = dict(parent)
        touched: set[str] = set()

        def own(directory: str) -> dict[str, tuple[str, str]]:
            if directory not in touched:
                touched.add(directory)
                directories[directory] = dict(directories.get(directory, {}))
            return directories[directory]

        for path, contents in changes.items():
            directory, _, name = path.rpartition("/")
            entries = own(directory)
            if contents is not None:
                entries[name] = (_FILE_MODE, self._write_object(b"blob", contents))
            elif entries.get(name, ("",))[0] != _TREE_MODE:
                # As in Git's index, deleting a directory's own path removes nothing.
                entries.pop(name, None)
            while directory:
                directory = directory.rpartition("/")[0]
                own(directory)
        # Deepest first, so each parent sees its children already rewritten or emptied.
        for directory in sorted(touched - {""}, key=lambda path: path.count("/"), reverse=True):
            above, _, name = directory.rpartition("/")
            if directories[directory]:
                directories[above][name] = (_TREE_MODE, self._write_tree_object(directories[directory]))
            else:
                del directories[directory]
                if directories[above].get(name, ("",))[0] == _TREE_MODE:
                    del directories[above][name]
        return self._write_tree_object(directories[""]), directories

    def _write_tree_object(self, entries: Mapping[str, tuple[str, str]]) -> str:
        # Git orders entries by name bytes, a subtree's name as if it ended in "/".
        rows = sorted((name.encode("utf-8") + (b"/" if mode == _TREE_MODE else b""), name, mode, oid)
                      for name, (mode, oid) in entries.items())
        return self._write_object(b"tree", b"".join(
            f"{mode} {name}\0".encode("utf-8") + bytes.fromhex(oid) for _, name, mode, oid in rows))

    def _write_commit(self, tree: str, parent: str | None) -> str:
        """The commit ``git commit-tree`` wrote for do-math: fixed identity, now, local offset."""
        seconds = int(time.time())
        minutes = time.localtime(seconds).tm_gmtoff // 60
        signature = "do-math <do-math@invalid> %d %s%02d%02d" % (
            seconds, "-" if minutes < 0 else "+", abs(minutes) // 60, abs(minutes) % 60)
        parents = f"parent {parent}\n" if parent is not None else ""
        return self._write_object(b"commit", (
            f"tree {tree}\n{parents}author {signature}\ncommitter {signature}\n\ndo-math state\n").encode("ascii"))

    def _compare_and_swap(self, new: str, old: str | None, operation: str) -> None:
        """Move the ref by Git's expected-old-OID update, the only ref move."""
        if not self._backend.update_ref(self.repository, self.ref, new, old):
            # A moved or remounted repository surfaces as a failed update; report
            # the changed boundary rather than only a conflict.
            self._repository_boundary.check()
            self._git_boundary.check()
            self._held_head = None
            raise GitStateStoreConflict(f"state ref changed before the {operation} compare-and-swap")
        self._held_head = new if self.holds_writer_lock else None

    @measured('git_publication')
    def publish(self, expected_head: str | None, changes: Mapping[str, bytes | None]) -> StateSnapshot:
        """Create and atomically publish one complete state commit.

        ``expected_head`` is ``None`` only for the parentless initial commit.
        Every later commit has exactly that expected commit as its only parent.
        A failed expected-old-OID check raises :class:`GitStateStoreConflict`
        and leaves the authoritative ref unchanged. The final update-ref CAS is
        the only ref comparison here; callers that want to avoid work against a
        stale head compare it first (``ResearchRepository`` does).
        """
        if expected_head is not None:
            self.validate_oid(expected_head)
        normalized_changes = self._validate_changes(changes)

        parent = self._tree(expected_head) if expected_head is not None else None
        existing_paths = parent.paths if parent is not None else frozenset()
        self._validate_artifact_changes(existing_paths, normalized_changes)
        candidate_paths = set(existing_paths)
        for path, contents in normalized_changes.items():
            if contents is None:
                candidate_paths.discard(path)
            else:
                candidate_paths.add(path)
        self.validate_candidate_paths(candidate_paths)
        if expected_head is not None and not normalized_changes:
            # A no-op still compares the authoritative ref at the publication
            # boundary, but creates neither blobs nor an empty history commit.
            self._compare_and_swap(expected_head, expected_head, "no-op")
            return StateSnapshot(expected_head)
        # The candidate path list decides both subtrees without reading the written tree.
        if not any(path.startswith("research/") for path in candidate_paths):
            raise ValueError("the state must contain a research subtree")
        if not any(path.startswith("runtime/") for path in candidate_paths):
            raise ValueError("the state must contain a runtime subtree")

        # Objects are written in this process; only the ref move below runs Git.
        tree, directories = self._write_tree(parent.directories if parent is not None else {"": {}},
                                             normalized_changes)
        commit = self._write_commit(tree, expected_head)
        self._compare_and_swap(commit, expected_head, "publish")
        # The new tree is known entry by entry, so it is never enumerated (ls-tree).
        self._published = _Tree(commit, directories, frozenset(candidate_paths))
        return StateSnapshot(commit)

    @contextmanager
    def writer_lock(self) -> Iterator[None]:
        """Acquire a non-stale, same-instance advisory OS lock in the Git dir."""
        with ExitStack() as held:
            try:
                held.enter_context(os_lock(self.git_dir / f"do-math-{self.instance_id}.lock", blocking=False))
            except OSError as error:
                raise GitStateStoreLockError("another local writer owns this instance lock") from error
            self.holds_writer_lock = True
            try:
                yield
            finally:
                self.holds_writer_lock = False
                self._held_head = None

    def _ref_oid(self) -> str | None:
        """Resolve the ref and validate OID syntax; object kinds are checked by readers."""
        oid = self._call("ref_oid", self.ref)
        if oid is None:
            return None
        self.validate_oid(oid)
        return oid

    def _check_subtrees(self, rows: list[str], names: tuple[str, ...]) -> None:
        if len(rows) != len(names):
            raise GitStateStoreError("incomplete state subtree metadata")
        for name, row in zip(names, rows):
            fields = row.split()
            if len(fields) != 2 or fields[-1] == "missing":
                raise GitStateStoreError(f"state object lacks required {name!r} subtree")
            oid, object_type = fields
            self.validate_oid(oid)
            if object_type != "tree":
                raise GitStateStoreError(f"state {name!r} entry must be a tree")

    def tree_paths(self, commit: str) -> frozenset[str]:
        return self._tree(commit).paths

    def _tree(self, commit: str) -> _Tree:
        """The tree of ``commit``: kept from this store's last publication or read, else one ls-tree.

        Two slots keep reading an older snapshot from displacing the head the
        next publication builds on.
        """
        self.validate_oid(commit)
        for known in (self._published, self._read):
            if known is not None and known.commit == commit:
                return known
        directories: dict[str, dict[str, tuple[str, str]]] = {"": {}}
        paths: set[str] = set()
        for mode, kind, oid, raw_path in self._call("list_tree", commit):
            try:
                path = raw_path.decode("utf-8")
            except UnicodeDecodeError as error:
                raise GitStateStoreError("existing state contains a non-UTF-8 path") from error
            if kind == "tree":
                directories.setdefault(path, {})
            else:
                self.validate_path(path)
                paths.add(path)
            above, _, name = path.rpartition("/")
            # ls-tree prints a subtree's mode zero-padded (040000); the tree object stores 40000.
            directories.setdefault(above, {})[name] = (mode.lstrip("0"), oid)
        self._read = _Tree(commit, directories, frozenset(paths))
        return self._read

    def _validate_changes(self, changes: Mapping[str, bytes | None]) -> dict[str, bytes | None]:
        if not isinstance(changes, Mapping):
            raise TypeError("changes must be a mapping of paths to bytes or None")
        normalized: dict[str, bytes | None] = {}
        folded: dict[str, str] = {}
        for path, contents in changes.items():
            self.validate_path(path)
            folded_path = path.casefold()
            prior = folded.get(folded_path)
            if prior is not None and prior != path:
                raise ValueError(f"Windows case-colliding paths: {prior!r} and {path!r}")
            folded[folded_path] = path
            if contents is not None and not isinstance(contents, bytes):
                raise TypeError("change contents must be bytes or None")
            normalized[path] = contents
        return normalized

    def validate_candidate_paths(self, paths: set[str]) -> None:
        folded_prefixes: dict[str, str] = {}
        directories: set[str] = set()
        for path in paths:
            self.validate_path(path)
            parts = path.split("/")
            for position in range(1, len(parts) + 1):
                original = "/".join(parts[:position])
                key = original.casefold()
                prior = folded_prefixes.get(key)
                if prior is not None and prior != original:
                    raise ValueError(f"Windows case-colliding path segments: {prior!r} and {original!r}")
                folded_prefixes[key] = original
                if position < len(parts):
                    directories.add(original)
        # The tree writer would let the subtree replace the file entry of the same name, silently dropping the file.
        conflicts = directories.intersection(paths)
        if conflicts:
            raise ValueError("state path is both a file and a directory: " + min(conflicts))

    def _validate_artifact_changes(self, existing_paths: set[str], changes: Mapping[str, bytes | None]) -> None:
        existing_bundles = {
            path.split("/")[2]
            for path in existing_paths
            if path.startswith(ARTIFACT_ROOT) and len(path.split("/")) >= 4
        }
        for path in changes:
            parts = path.split("/")
            if parts[:2] == ["runtime", "artifacts"] and parts[2] in existing_bundles:
                raise ValueError("existing runtime artifact bundles are immutable")

    def validate_path(self, path: str) -> None:
        if not isinstance(path, str) or not path:
            raise ValueError("path must be a non-empty POSIX relative path")
        if path.startswith("/") or "\\" in path or "\x00" in path:
            raise ValueError("path must be a POSIX relative path")
        parts = path.split("/")
        if len(parts) < 2 or parts[0] not in {"research", "runtime"}:
            raise ValueError("state paths must be files below research/ or runtime/")
        for part in parts:
            check_path_segment(part)
        if parts[:2] == ["runtime", "artifacts"] and len(parts) < 4:
            raise ValueError("artifact paths must name a bundle and a file")

    def validate_oid(self, oid: str) -> None:
        if oid_shape(oid) != self.object_format:
            raise ValueError(f"OID must be a lowercase {self.object_format} object ID")

    def first_descendant(self, parent: str, head: str) -> str | None:
        """The commit on ``head``'s first-parent line whose parent is ``parent``, if any."""
        self.validate_oid(parent)
        commits = self._call("first_parent_line", parent, head)
        return commits[0] if commits else None

    def _call(self, operation: str, *arguments):
        """One Git backend operation; a Git failure re-proves both boundaries first."""
        from .ports.git_backend import GitBackendError
        try:
            return getattr(self._backend, operation)(self.repository, *arguments)
        except GitBackendError as error:
            # A moved or remounted repository surfaces as a Git error; report
            # the changed boundary rather than only the Git symptom.
            self._repository_boundary.check()
            self._git_boundary.check()
            raise GitStateStoreError(str(error)) from error


def _windows_handle_facts(handle):
    import ctypes
    from ctypes import wintypes
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    final = kernel.GetFinalPathNameByHandleW
    final.argtypes = [wintypes.HANDLE, wintypes.LPWSTR, wintypes.DWORD, wintypes.DWORD]
    final.restype = wintypes.DWORD
    buffer = ctypes.create_unicode_buffer(32768)
    count = final(handle, buffer, len(buffer), 0)
    if not count or count >= len(buffer):
        raise ctypes.WinError(ctypes.get_last_error())
    path = buffer.value
    if path.startswith("\\\\?\\UNC\\"):
        raise ValueError("storage requires a local fixed NTFS volume")
    path = path.removeprefix("\\\\?\\")
    volume = ctypes.create_unicode_buffer(32768)
    volume_path = kernel.GetVolumePathNameW
    volume_path.argtypes = [wintypes.LPCWSTR, wintypes.LPWSTR, wintypes.DWORD]
    if not volume_path(path, volume, len(volume)):
        raise ctypes.WinError(ctypes.get_last_error())
    drive_type = kernel.GetDriveTypeW
    drive_type.argtypes = [wintypes.LPCWSTR]
    if drive_type(volume.value) != 3:
        raise ValueError("storage requires a local fixed volume")
    serial = wintypes.DWORD()
    fs = ctypes.create_unicode_buffer(256)
    info = kernel.GetVolumeInformationW
    info.argtypes = [wintypes.LPCWSTR, wintypes.LPWSTR, wintypes.DWORD, ctypes.POINTER(wintypes.DWORD),
                     ctypes.POINTER(wintypes.DWORD), ctypes.POINTER(wintypes.DWORD), wintypes.LPWSTR, wintypes.DWORD]
    if not info(volume.value, None, 0, ctypes.byref(serial), None, None, fs, len(fs)):
        raise ctypes.WinError(ctypes.get_last_error())
    if fs.value.upper() != "NTFS":
        raise ValueError("storage requires NTFS")
    return Path(path), (volume.value.casefold(), serial.value)


class PhysicalBoundary:
    """A root proved physical once, when the boundary is opened.

    ``check`` proves the root: no reparse ancestor, the same local fixed NTFS
    volume, and a directory handle whose final path is the lexical root.
    Opening a file below the root only rejects reparse points between the root
    and the file. Handles are not re-verified after opening: swapping a path
    between check and use is deliberate tampering, not an accidental change.
    Does not assert an unspecified ACL policy.
    """
    def __init__(self, root):
        self.root = Path(os.path.abspath(root))
        no_reparse(self.root)
        if not self.root.is_dir():
            raise ValueError("physical boundary root must be an existing directory")
        self.device = self.root.stat().st_dev
        self.check()

    def check(self):
        no_reparse(self.root)
        if self.root.stat().st_dev != self.device:
            raise ValueError("physical root volume changed")
        if os.name == "nt":
            import ctypes
            from ctypes import wintypes
            kernel = ctypes.WinDLL("kernel32", use_last_error=True)
            create = kernel.CreateFileW
            create.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, ctypes.c_void_p,
                               wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE]
            create.restype = wintypes.HANDLE
            close = kernel.CloseHandle
            close.argtypes = [wintypes.HANDLE]
            handle = create(str(self.root), 0, 3, None, 3, 0x02000000 | 0x00200000, None)
            if handle == wintypes.HANDLE(-1).value:
                raise ctypes.WinError(ctypes.get_last_error())
            try:
                final, volume = _windows_handle_facts(handle)
                if os.path.normcase(str(final)) != os.path.normcase(str(self.root)):
                    raise ValueError("physical directory handle resolves elsewhere")
                if hasattr(self, "volume") and volume != self.volume:
                    raise ValueError("physical volume identity changed")
                self.volume = volume
            finally:
                close(handle)

    @contextmanager
    def open(self, path, mode):
        if mode not in {"rb", "xb"}:
            raise ValueError("physical boundary supports read or exclusive creation")
        path = Path(os.path.abspath(path))
        if not path.is_relative_to(self.root):
            raise ValueError("file path is outside the physical boundary")
        # The root and its ancestors were proved when this boundary opened.
        no_reparse(path, below=self.root)
        with path.open(mode) as stream:
            yield stream
