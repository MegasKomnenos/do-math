"""Windows Job ownership of child processes: suspended start, held identity, nested jobs and control under load.

Disposable Windows children only; no research host, provider, or schedule.

Held-handle identity and injected resume failure are not natural PID recycling
or a full ENGINE crash test. Local busy-child control is not provider latency.
"""
import os
from pathlib import Path
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math import windows_job as jobs


@unittest.skipUnless(os.name == 'nt', 'requires Windows Job host')
class IsolatedHostTests(unittest.TestCase):
    def until(self, predicate, timeout=10):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if predicate(): return
            time.sleep(.02)
        self.fail('isolated child did not reach its boundary before timeout')

    def test_resume_failure_never_runs_the_suspended_child(self):
        with tempfile.TemporaryDirectory() as directory:
            marker = Path(directory) / 'substantive-action'
            code = f'from pathlib import Path; Path({str(marker)!r}).write_text("ran")'
            with jobs.WindowsJob([sys.executable, '-c', code]) as job:
                with patch.object(jobs._kernel32, 'ResumeThread', return_value=jobs._WAIT_FAILED):
                    with self.assertRaises(OSError): job.resume()
                self.assertFalse(marker.exists())
                job.terminate()
                self.assertTrue(job.wait(5))
                self.until(lambda: job.inspect().active_processes == 0)


if __name__ == '__main__': unittest.main(verbosity=2)
