"""Windows Job ownership of child processes: held identity, nested Jobs and local control under load.

Disposable Windows children only; no research host, provider or schedule.
Held-handle identity is not natural PID recycling, and local busy-child
control is not provider latency.
"""
import os
from pathlib import Path
import sys
import tempfile
import threading
import time
import unittest

from do_math.control_transport import ControlTransport
from do_math.system_clock import SystemClock
from do_math.windows_job import WindowsJob
from test_categories import test_group as category

SCRIPTS = Path(__file__).resolve().parents[2]


def reached(predicate, timeout=10):
    """Poll ``predicate`` until it holds or ``timeout`` seconds pass; whether it held."""
    deadline = time.monotonic() + timeout
    pause = threading.Event()
    while time.monotonic() < deadline:
        if predicate():
            return True
        pause.wait(0.02)
    return predicate()


@category('resource')
@unittest.skipUnless(os.name == 'nt', 'requires Windows Job host')
class IsolatedHostTests(unittest.TestCase):
    def until(self, predicate, timeout=10):
        if not reached(predicate, timeout):
            self.fail('isolated child did not reach its boundary before timeout')

    def test_owned_process_identity_does_not_follow_a_changed_pid_field(self):
        with WindowsJob([sys.executable, '-c', 'import time; time.sleep(30)']) as first:
            with WindowsJob([sys.executable, '-c', 'import time; time.sleep(30)']) as other:
                original_pid, original_time = first.pid, first.creation_filetime
                self.assertGreater(original_time, 0)
                first.pid = other.pid  # synthetic recycled locator, not OS PID reuse
                self.assertEqual(first._process_creation_filetime(), original_time)
                first.terminate()
                self.assertTrue(first.wait(5))
                self.assertFalse(other.inspect().root_signaled)
                self.assertNotEqual(original_pid, other.pid)

    def test_nested_job_child_remains_owned_by_outer_job(self):
        with tempfile.TemporaryDirectory() as directory:
            marker = Path(directory) / 'inner-running'
            nested = ('import sys,time; from pathlib import Path; '
                      f'sys.path.insert(0,{str(SCRIPTS)!r}); '
                      'from do_math.windows_job import WindowsJob; '
                      'j=WindowsJob([sys.executable,"-c","import time; time.sleep(30)"]); '
                      f'j.resume(); Path({str(marker)!r}).write_text(str(j.pid)); time.sleep(30)')
            with WindowsJob([sys.executable, '-c', nested]) as outer:
                outer.resume()
                self.until(lambda: marker.is_file() and bool(marker.read_text()))
                inner_pid = int(marker.read_text())
                self.assertIn(inner_pid, outer.inspect().process_ids)
                outer.terminate()
                self.assertTrue(outer.wait(5))
                self.until(lambda: outer.inspect().active_processes == 0)

    @category('resource')
    def test_local_control_receipt_remains_responsive_during_child_cpu_load(self):
        with tempfile.TemporaryDirectory() as directory:
            marker = Path(directory) / 'busy'
            code = f'from pathlib import Path\nPath({str(marker)!r}).write_text("ready")\nwhile True: sum(range(10000))'
            with WindowsJob([sys.executable, '-c', code]) as job:
                job.resume()
                self.until(marker.exists)
                transport = ControlTransport(Path(directory) / 'control', clock=SystemClock())
                binding = transport.issue('EX-isolated', 'GR-fixture')
                start = time.monotonic()
                submitted = ControlTransport.worker_submit(binding, request_id='CT-stop', kind='safety_boundary',
                                                           payload={'inflight_calls': False})
                self.assertEqual(submitted['state'], 'submitted')
                receipts = transport.pump(lambda request: {'state': 'accepted', 'published': True, 'snapshot': 'fixture'})
                self.assertEqual(receipts[0]['state'], 'accepted')
                # A generous deadlock bound, not a latency or performance SLA.
                self.assertLess(time.monotonic() - start, 10)
                job.terminate()
                self.assertTrue(job.wait(5))
                self.until(lambda: job.inspect().active_processes == 0)


if __name__ == '__main__':
    unittest.main()
