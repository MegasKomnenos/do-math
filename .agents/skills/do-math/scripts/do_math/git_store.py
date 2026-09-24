"""Git plumbing storage for one immutable do-math instance state chain.

The store publishes bytes and Git object relationships only.  It does not
validate record schemas and does not activate a research instance; those
semantic decisions belong to callers above this storage primitive.
"""

from __future__ import annotations

from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from dataclasses import dataclass
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import stat
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


def oid_shape(oid: str) -> str:
    """Validate only OID syntax, not object existence or this instance's format."""
    if not isinstance(oid, str) or len(oid) not in {40, 64} or not _HEX.fullmatch(oid):
        raise ValueError("OID must be a lowercase 40/64-character hexadecimal string")
    return "sha1" if len(oid) == 40 else "sha256"


class GitStateStore:
    """Publish one parent-linked state chain at ``refs/heads/do-math/<id>``.

    ``publish`` uses Git's expected-old-OID ref update as its concurrency
    guarantee.  ``writer_lock`` is a separate, optional local OS lock for
    callers that need to serialize work before that final CAS.
    """

    def __init__(self, repository: str | os.PathLike[str], instance_id: str) -> None:
        if not isinstance(instance_id, str) or not _INSTANCE_ID.fullmatch(instance_id):
            raise ValueError("instance_id must be the registry RI-prefixed canonical ULID")
        self.repository = Path(repository).absolute()
        self._repository_boundary = PhysicalBoundary(self.repository)
        if not self.repository.is_dir():
            raise ValueError("repository must be an existing Git work tree or bare repository")
        self.instance_id = instance_id
        self.ref = f"refs/heads/do-math/{instance_id}"
        self._git_dir = Path(self._git_text("rev-parse", "--absolute-git-dir")).absolute()
        self._git_boundary = PhysicalBoundary(self._git_dir)
        self.object_format = self._git_text("rev-parse", "--show-object-format")
        if self.object_format not in {"sha1", "sha256"}:
            raise GitStateStoreError(f"unsupported Git object format: {self.object_format!r}")
        self.oid_length = 40 if self.object_format == "sha1" else 64
        self._listed: tuple[str, frozenset[str]] | None = None

    def read_snapshot(self) -> StateSnapshot:
        """Return the current state commit and its research/runtime tree OIDs."""
        head = self._ref_oid()
        if head is None:
            return StateSnapshot(None, None, None)
        names = ("research", "runtime")
        queries = "\n".join([head, *(f"{head}:{name}" for name in names)]) + "\n"
        result = self._git("cat-file", "--batch-check=%(objectname) %(objecttype)",
                           input=queries.encode("ascii"), check=False)
        rows = result.stdout.decode("ascii").splitlines()
        root = rows[0].split() if rows else []
        if not root or root == [head, "missing"]:
            detail = result.stderr.decode("utf-8", "replace").strip()
            raise GitStateStoreError(f"state ref points to an unreadable object: {detail}")
        if len(root) != 2 or root[0] != head:
            raise GitStateStoreError("invalid state commit metadata")
        if root[1] != "commit":
            raise GitStateStoreError("state ref must point to a commit")
        if result.returncode:
            detail = result.stderr.decode("utf-8", "replace").strip()
            raise GitStateStoreError(f"cannot read state subtree metadata: {detail}")
        trees = self._parse_subtree_oids(rows[1:], names)
        return StateSnapshot(head, trees["research"], trees["runtime"])

    def read_bytes(self, commit: str, path: str) -> bytes:
        """Read exact blob bytes from an explicit, format-valid state commit."""
        self._validate_oid(commit)
        self._validate_path(path)
        return self._git("cat-file", "blob", f"{commit}:{path}").stdout

    def read_many(self, commit: str, paths: list[str]) -> dict[str, bytes]:
        """Read a fixed snapshot in one process, using binary lengths, not lines."""
        self._validate_oid(commit)
        paths = list(dict.fromkeys(paths))
        for path in paths:
            self._validate_path(path)
        if not paths:
            return {}
        raw = self._git("cat-file", "--batch", input="".join(
            f"{commit}:{path}\n" for path in paths).encode("utf-8")).stdout
        result, offset = {}, 0
        for path in paths:
            end = raw.find(b"\n", offset)
            header = raw[offset:end].split() if end >= 0 else []
            if len(header) != 3 or header[1] != b"blob" or not header[2].isdigit():
                raise GitStateStoreError("batch read did not return a blob: " + path)
            self._validate_oid(header[0].decode("ascii"))
            size = int(header[2])
            start, offset = end + 1, end + 1 + size
            if raw[offset:offset + 1] != b"\n":
                raise GitStateStoreError("truncated batch blob: " + path)
            result[path] = raw[start:offset]
            offset += 1
        if offset != len(raw):
            raise GitStateStoreError("unexpected trailing batch output")
        return result

    def _write_blobs(self, changes: Mapping[str, bytes | None]) -> dict[str, str]:
        values = [(path, raw) for path, raw in changes.items() if raw is not None]
        if not values:
            return {}
        # Numbered private files avoid argv limits and quoting research paths.
        # --no-filters preserves exactly the bytes previously passed to --stdin.
        with tempfile.TemporaryDirectory(prefix="do-math-blobs-", dir=self._git_dir) as directory:
            filenames = []
            for number, (_, raw) in enumerate(values):
                file = Path(directory) / str(number)
                with self._git_boundary.open(file, "xb") as stream:
                    stream.write(raw)
                filenames.append(json.dumps(file.as_posix(), ensure_ascii=False))
            output = self._git("hash-object", "-w", "--no-filters", "--stdin-paths",
                               input=("\n".join(filenames) + "\n").encode("utf-8")).stdout
        oids = output.decode("ascii").splitlines()
        if len(oids) != len(values):
            raise GitStateStoreError("blob writer returned an incomplete object list")
        for oid in oids:
            self._validate_oid(oid)
        return {path: oid for (path, _), oid in zip(values, oids)}

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
        if expected_head is not None and not normalized_changes:
            # A no-op still compares the authoritative ref at the publication
            # boundary, but creates neither blobs nor an empty history commit.
            updated = self._git("update-ref", self.ref, expected_head, expected_head, check=False)
            if updated.returncode:
                raise GitStateStoreConflict("state ref changed before the no-op compare-and-swap")
            trees = self._subtree_oids(expected_head, ("research", "runtime"))
            return StateSnapshot(expected_head, trees["research"], trees["runtime"])
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
            blobs = self._write_blobs(normalized_changes)
            for path, contents in normalized_changes.items():
                if contents is None:
                    index_records.extend(f"0 {'0' * self.oid_length}\t{path}".encode("utf-8"))
                else:
                    blob = blobs[path]
                    index_records.extend(f"100644 {blob}\t{path}".encode("utf-8"))
                index_records.append(0)
            if index_records:
                self._git("update-index", "-z", "--index-info", input=bytes(index_records), env=index_environment)
            tree = self._git("write-tree", env=index_environment).stdout.decode("ascii").strip()
        self._validate_oid(tree)
        trees = self._subtree_oids(tree, ("research", "runtime"))
        research_tree, runtime_tree = trees["research"], trees["runtime"]

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
            self._git_boundary.verify_descriptor(descriptor, lock_path)
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

    def _ref_oid(self) -> str | None:
        """Resolve the ref and validate OID syntax; object kinds are checked by readers."""
        result = self._git("rev-parse", "--verify", "--quiet", self.ref, check=False)
        if result.returncode:
            if result.returncode == 1 and not result.stderr:
                return None
            detail = result.stderr.decode("utf-8", "replace").strip()
            raise GitStateStoreError(f"cannot resolve existing state ref: {detail}")
        oid = result.stdout.decode("ascii").strip()
        self._validate_oid(oid)
        return oid

    def _head(self) -> str | None:
        oid = self._ref_oid()
        if oid is None:
            return None
        object_type = self._git("cat-file", "-t", oid, check=False)
        if object_type.returncode:
            detail = object_type.stderr.decode("utf-8", "replace").strip()
            raise GitStateStoreError(f"state ref points to an unreadable object: {detail}")
        if object_type.stdout.decode("ascii").strip() != "commit":
            raise GitStateStoreError("state ref must point to a commit")
        return oid

    def _subtree_oids(self, commit_or_tree: str, names: tuple[str, ...]) -> dict[str, str]:
        """Resolve and type-check required trees in one immutable-object read."""
        self._validate_oid(commit_or_tree)
        if not names or any(name not in {"research", "runtime"} for name in names):
            raise ValueError("only research/runtime state subtrees can be resolved")
        queries = "".join(f"{commit_or_tree}:{name}\n" for name in names).encode("ascii")
        result = self._git("cat-file", "--batch-check=%(objectname) %(objecttype)", input=queries)
        rows = result.stdout.decode("ascii").splitlines()
        return self._parse_subtree_oids(rows, names)

    def _parse_subtree_oids(self, rows: list[str], names: tuple[str, ...]) -> dict[str, str]:
        if len(rows) != len(names):
            raise GitStateStoreError("incomplete state subtree metadata")
        trees = {}
        for name, row in zip(names, rows):
            fields = row.split()
            if len(fields) != 2 or fields[-1] == "missing":
                raise GitStateStoreError(f"state object lacks required {name!r} subtree")
            oid, object_type = fields
            self._validate_oid(oid)
            if object_type != "tree":
                raise GitStateStoreError(f"state {name!r} entry must be a tree")
            trees[name] = oid
        return trees

    def _tree_paths(self, commit: str) -> frozenset[str]:
        self._validate_oid(commit)
        self._repository_boundary.check()
        self._git_boundary.check()
        if self._listed is not None and self._listed[0] == commit:
            return self._listed[1]
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
        self._listed = (commit, frozenset(paths))
        return self._listed[1]

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
        if oid_shape(oid) != self.object_format:
            raise ValueError(f"OID must be a lowercase {self.object_format} object ID")

    @contextmanager
    def _private_index(self) -> Iterator[dict[str, str]]:
        descriptor, index_path = tempfile.mkstemp(prefix="do-math-index-", dir=self._git_dir)
        try:
            self._git_boundary.verify_descriptor(descriptor, index_path)
        finally:
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
        self._repository_boundary.check()
        if hasattr(self, "_git_boundary"):
            self._git_boundary.check()
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
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        if check and completed.returncode:
            detail = completed.stderr.decode("utf-8", "replace").strip()
            raise GitStateStoreError(f"git {' '.join(arguments)} failed: {detail}")
        return completed


def _no_reparse(path: Path) -> None:
    candidate = path.absolute()
    for part in (candidate, *candidate.parents):
        try:
            value = part.lstat()
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(value.st_mode) or getattr(value, "st_file_attributes", 0) & 0x400:
            raise ValueError("physical path crosses a reparse point or symlink: " + str(part))


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
    """Check actual open handles; does not assert an unspecified ACL policy."""
    def __init__(self, root):
        self.root = Path(root).absolute()
        _no_reparse(self.root)
        if not self.root.is_dir():
            raise ValueError("physical boundary root must be an existing directory")
        self.device = self.root.stat().st_dev
        self.check()

    def check(self):
        _no_reparse(self.root)
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

    def verify_descriptor(self, descriptor, path):
        path = Path(path).absolute()
        self.check()
        _no_reparse(path)
        if not path.is_relative_to(self.root) or os.fstat(descriptor).st_dev != self.device:
            raise ValueError("opened file is outside the physical root/volume")
        if os.name == "nt":
            import msvcrt
            final, volume = _windows_handle_facts(msvcrt.get_osfhandle(descriptor))
            if not final.is_relative_to(self.root) or volume != self.volume or os.path.normcase(str(final)) != os.path.normcase(str(path)):
                raise ValueError("opened handle final path is outside the physical boundary")
        else:
            if (os.fstat(descriptor).st_dev, os.fstat(descriptor).st_ino) != (path.stat().st_dev, path.stat().st_ino):
                raise ValueError("opened file identity changed")

    @contextmanager
    def open(self, path, mode):
        if mode not in {"rb", "xb"}:
            raise ValueError("physical boundary supports read or exclusive creation")
        path = Path(path).absolute()
        if not path.is_relative_to(self.root):
            raise ValueError("file path is outside the physical boundary")
        self.check()
        _no_reparse(path)
        with path.open(mode) as stream:
            self.verify_descriptor(stream.fileno(), path)
            yield stream
