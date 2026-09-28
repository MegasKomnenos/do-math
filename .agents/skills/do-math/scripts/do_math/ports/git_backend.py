"""Git backend port: the repository operations GitStateStore needs, in meaning-sized steps.

Objects are written by GitStateStore itself; this port reads them back and
moves the state ref. A missing object or path answers None; an unexpected Git
failure raises ``GitBackendError``.
"""
from pathlib import Path
from typing import Protocol


class GitBackendError(RuntimeError):
    """Git failed in a way the port does not answer with a value."""


class GitBackend(Protocol):
    def describe(self, repository: Path) -> tuple:
        """(absolute Git directory, object format 'sha1'|'sha256', objects directory as Git names it)."""

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
