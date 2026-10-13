"""A formal Job run through the calls manager on a real Windows Job (``formal._job_run``, ``parallel.ModelCalls``).

``_job_run`` publishes the Job's identity through ``on_started`` before the
suspended root resumes, and terminates the Job when its stop flag is set; the
calls manager runs the start callback and the stop judgment on the owner
thread. The Jobs port here is the real one.
"""
import os
from pathlib import Path
import sys
import tempfile
import threading
import time
import unittest

from do_math.formal import _job_run
from do_math.parallel import ModelCalls
from do_math.windows_job import WindowsJobs
from test_categories import test_group


class CallJobTests(unittest.TestCase):
    @test_group('resource')
    @unittest.skipUnless(os.name == 'nt', 'Windows Job required')
    def test_failed_start_publication_never_resumes_the_real_job(self):
        from support.entry import entry
        _entry = entry()
        from do_math.wiring import real_ports
        _entry.ports = real_ports(environment=_entry.environment)
        with tempfile.TemporaryDirectory() as root:
            marker = Path(root) / 'must-not-run'

            def reject(identity):
                self.assertFalse(marker.exists())
                raise OSError('simulated publication failure')
            with self.assertRaisesRegex(OSError, 'publication'):
                _job_run([sys.executable, '-c', f'from pathlib import Path; Path({str(marker)!r}).touch()'],
                         Path(root), on_started=reject, jobs=WindowsJobs(), clock=_entry.ports.clock, environment=_entry.environment)
            self.assertFalse(marker.exists())

    @test_group('resource')
    @unittest.skipUnless(os.name == 'nt', 'Windows Job required')
    def test_real_job_cancellation_uses_owner_judgment_and_collects_once(self):
        from support.entry import entry
        from do_math.wiring import real_ports
        _entry = entry()
        _entry.ports = real_ports(environment=_entry.environment)
        jobs = _entry.ports.jobs
        owner = threading.get_ident()
        calls = ModelCalls()
        started, returned = [], []

        def on_started(identity):
            self.assertEqual(threading.get_ident(), owner)
            started.append(identity)

        def should_stop():
            self.assertEqual(threading.get_ident(), owner)
            return bool(started)

        def continuation():
            returned.append((yield))
        generator = continuation()
        next(generator)
        with tempfile.TemporaryDirectory() as root:
            calls.start_call(generator, _job_run, {'command': [sys.executable, '-c', 'import time; time.sleep(30)'],
                             'cwd': Path(root), 'on_started': on_started, 'should_stop': should_stop,
                             'jobs': jobs, 'clock': _entry.ports.clock,
                             'environment': _entry.environment}, execution_id='EX-real')
            deadline = time.monotonic() + 15
            collected = 0
            try:
                while calls.futures and time.monotonic() < deadline:
                    collected += calls.collect()
                    calls.judge()
                    calls.wait(0.01)
                self.assertFalse(calls.futures)
                self.assertEqual(collected, 1)
                self.assertEqual(len(started), 1)
                self.assertEqual(len(returned), 1)
                self.assertIsInstance(returned[0], tuple, returned[0])
                self.assertEqual(returned[0], (None, '', '', True))
                self.assertTrue(jobs.named_job_empty(started[0]['job_name']))
                self.assertEqual(calls.collect(), 0)
            finally:
                calls.close()


if __name__ == '__main__':
    unittest.main()
