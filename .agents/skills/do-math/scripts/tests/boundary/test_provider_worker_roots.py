"""Each provider worker is the direct Python root of its Job: a fresh interpreter imports it as a script.

Inside its Job a worker runs as ``python <worker>.py REQUEST.json`` outside the
``do_math`` package, so its imports fall back to the modules beside it. The
subject is interpreter start-up and ``sys.path``, which only a child process
shows (조사 K-24).
"""
from pathlib import Path
import subprocess
import sys
import unittest

from do_math import claude_worker, codex_worker


class WorkerRootTests(unittest.TestCase):
    def run_root(self, module):
        return subprocess.run([sys.executable, str(Path(module.__file__))], capture_output=True, timeout=10,
                              creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))

    def test_worker_remains_importable_as_its_direct_job_root(self):
        result = self.run_root(codex_worker)
        self.assertNotIn(b"No module named", result.stderr)
        self.assertIn(b"usage: codex_worker.py REQUEST.json", result.stderr)

    def test_claude_worker_remains_importable_as_its_direct_job_root(self):
        result = self.run_root(claude_worker)
        self.assertNotIn(b"No module named", result.stderr)
        self.assertIn(b"usage: claude_worker.py REQUEST.json", result.stderr)


if __name__ == '__main__':
    unittest.main()
