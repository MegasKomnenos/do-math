"""Jobs port: start one program as the suspended root of an owned Job.

The returned Job has the ``windows_job.WindowsJob`` surface: ``name``, ``pid``,
``creation_filetime``, ``resume``, ``wait``, ``terminate``, ``inspect``,
``resource_usage``, ``close`` and use as a context manager. Worker programs
(provider CLI workers, the Lean worker) run inside such Jobs; the program a
worker starts in turn is its own seam (``cli_worker.run_cli``, ``formal._worker``).
The owner queries let a later process decide whether an earlier launch still runs.
"""
from typing import Protocol


class Jobs(Protocol):
    def launch(self, argv, *, cwd=None, env=None, name=None, resource_limits=None):
        """A Job whose suspended root runs ``argv``; nothing runs before ``resume``."""

    def owner_identity(self) -> dict:
        """This launching process: ``pid``, ``creation_filetime`` (decimal text), ``host``, ``session``."""

    def owner_ended(self, identity: dict) -> bool | None:
        """Whether that owner has ended; the same PID with another creation time has. Unknown is None."""

    def named_job_empty(self, name: str) -> bool | None:
        """Whether the named local Job has no live process; a Job nobody created is empty. Unknown is None."""
