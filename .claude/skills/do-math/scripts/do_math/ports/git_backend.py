"""Git backend port: CLI prerequisites, project facts, and state storage operations.

The port writes and reads the objects of the state commits and moves the state
ref. For storage, a missing object or path answers None and an unexpected Git
failure raises ``GitBackendError``. CLI prerequisites instead answer exit-status
success; project reads have their separately documented failure contracts.
"""
from pathlib import Path
from dataclasses import dataclass
from typing import Protocol


class GitBackendError(RuntimeError):
    """Git failed in a way the port does not answer with a value."""


@dataclass(frozen=True)
class ProjectSnapshot:
    repository_root: Path | None
    tree_oid: str | None
    raw_diff: bytes
    tracked_paths: frozenset[str]


class GitBackend(Protocol):
    def initialize_repository(self, repository: Path) -> bool:
        """Initialize Git in an existing empty directory; answer only exit-status success.

        The CLI owns missing/empty eligibility and mkdir. Inherit the live process
        environment (including Git's default object format), not the backend's
        storage environment. Ignore stdout/stderr, even empty or non-UTF bytes;
        OS/subprocess exceptions propagate. No storage isolation options apply.
        """

    def repository_exists(self, repository: Path) -> bool:
        """Can Git resolve --git-dir here? Exit status alone, no output parsing.

        Includes enclosing repositories, bare repositories and linked worktrees.
        Same ambient environment and exception contract as initialize_repository.
        Unlike describe, False is a normal answer and no object format is read.
        """

    def project_repository_root(self, project_root: Path, *, should_stop=None) -> Path | None:
        """Find the enclosing worktree; empty stdout means None, irrespective of exit status.

        UTF-8 decoding and OS errors propagate. Honour stop before/after the read.
        """

    def project_snapshot(self, project_root: Path, repository_root: Path | None, *, should_stop=None) -> ProjectSnapshot:
        """Read HEAD subtree, raw worktree diff and index paths for this project.

        None root means no Git facts. Missing HEAD/subtree gives tree_oid=None;
        diff stdout is kept even on failure. Index failure raises RuntimeError.
        Paths decode strict UTF-8. An outside project raises ValueError. Stop is
        checked before/after each of the three local reads, not only the batch.
        """

    def describe(self, repository: Path) -> tuple:
        """(absolute Git directory, object format 'sha1'|'sha256', objects directory as Git names it)."""

    def write_object(self, repository: Path, kind: str, body: bytes) -> str:
        """Store one object (``kind``: blob, tree or commit) and return its OID; an existing object is kept."""

    def object_info(self, repository: Path, specs: list) -> list:
        """For each ``ref``, ``oid`` or ``rev:path``: (oid, type, size), or None when absent."""

    def read_objects(self, repository: Path, specs: list) -> list:
        """For each spec: (object type, exact bytes), or None when absent."""

    def ref_oid(self, repository: Path, ref: str) -> str | None:
        """The object ID the ref names, or None when the ref does not exist."""

    def update_ref(self, repository: Path, ref: str, new: str, old: str | None) -> bool:
        """Move ``ref`` to ``new`` only if it names ``old`` (None: only if absent); False otherwise."""

    def list_tree(self, repository: Path, commit: str) -> list:
        """Every entry of the commit's tree, subtrees included: (mode, kind, oid, path bytes)."""

    def first_parent_line(self, repository: Path, parent: str, head: str) -> list:
        """Commits on ``head``'s first-parent line after ``parent``, oldest first."""
