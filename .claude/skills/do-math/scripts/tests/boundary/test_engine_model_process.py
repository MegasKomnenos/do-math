"""The real Windows Job behaviour the engine region's Sim tests take from the Jobs fake.

``sim.test_engine_queue`` ends a call's model process and ``flows.test_engine_flow``
recovers a crashed launch whose Job has emptied; both use Jobs-fake Jobs. The
legacy tests also checked these on real Jobs, so they stay here: a model process
ended while running or before it was resumed is gone within ten seconds and
leaves no process, a launch owner whose process has exited is judged ended, and
the Codex collector's termination barrier sees an ended Job empty.
"""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
from types import SimpleNamespace
import unittest

from do_math.codex_adapter import CodexExecAdapter
from do_math.windows_job import WindowsJob, WindowsJobs

SCRIPTS = Path(__file__).resolve().parents[2]


def job_name():
    return 'Local\\DoMath-test-' + os.urandom(8).hex()


class ModelProcessJobTests(unittest.TestCase):
    def test_a_running_model_process_is_ended_within_ten_seconds_and_leaves_no_process(self):
        with tempfile.TemporaryDirectory() as directory:
            job = WindowsJob([sys.executable, '-c', 'import time; time.sleep(600)'], cwd=directory, name=job_name())
            try:
                job.resume()
                self.assertEqual(job.inspect().active_processes, 1)
                job.terminate()
                self.assertTrue(job.wait(10))
                self.assertEqual(job.inspect().active_processes, 0)
            finally:
                job.close()

    def test_a_model_process_ended_before_resume_leaves_no_process_within_ten_seconds(self):
        with tempfile.TemporaryDirectory() as directory:
            job = WindowsJob([sys.executable, '-c', 'import time; time.sleep(600)'], cwd=directory, name=job_name())
            try:
                job.terminate()
                self.assertTrue(job.wait(10))
                # The Job's active count can trail the root signal; poll it for up to ten seconds.
                pause = threading.Event()
                for _ in range(500):
                    if job.inspect().active_processes == 0:
                        break
                    pause.wait(0.02)
                self.assertEqual(job.inspect().active_processes, 0)
            finally:
                job.close()

    def test_an_exited_owner_process_has_ended(self):
        # A separate exited process supplies a real dead launch owner; this process stays alive.
        program = ('import json, sys; sys.path.insert(0, sys.argv[1]); '
                   'from do_math.windows_job import owner_identity; print(json.dumps(owner_identity()))')
        identity = json.loads(subprocess.check_output([sys.executable, '-c', program, str(SCRIPTS)], timeout=60))
        self.assertNotEqual(identity['pid'], os.getpid())
        self.assertIs(WindowsJobs().owner_ended(identity), True)
        self.assertIs(WindowsJobs().owner_ended(WindowsJobs().owner_identity()), False)

    def test_the_collector_barrier_sees_an_ended_job_empty(self):
        with tempfile.TemporaryDirectory() as directory:
            job = WindowsJob([sys.executable, '-c', 'pass'], cwd=directory, name=job_name())
            try:
                job.resume()
                # Root signal alone can precede the Job's active-count update; the collector's barrier waits for both.
                self.assertTrue(CodexExecAdapter('fixture-cli').wait_for_termination(SimpleNamespace(job=job), 10))
                self.assertEqual(job.inspect().active_processes, 0)
            finally:
                job.close()


if __name__ == '__main__':
    unittest.main()
