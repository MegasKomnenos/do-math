"""Jobs port: start one program as the suspended root of an owned Job.

The returned Job has the ``windows_job.WindowsJob`` surface: ``name``, ``pid``,
``creation_filetime``, ``resume``, ``wait``, ``terminate``, ``inspect``,
``resource_usage``, ``close`` and use as a context manager. Worker programs
(provider CLI workers, the Lean worker) run inside such Jobs; the program a
worker starts in turn is its own seam (``cli_worker.run_cli``, ``formal._worker``).
"""
from typing import Protocol


class Jobs(Protocol):
    def launch(self, argv, *, cwd=None, env=None, name=None, resource_limits=None):
        """A Job whose suspended root runs ``argv``; nothing runs before ``resume``."""
