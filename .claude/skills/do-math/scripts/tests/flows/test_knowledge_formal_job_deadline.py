"""The Lean worker Job's termination check after a stop has a fixed deadline (``formal._job_run``, layer 3).

``_job_run`` waits for a terminated Job to empty until ``time.monotonic() + 2``
and sleeps between checks with ``time``; no clock port reaches it, so the
deadline passes in real time and the scenario itself lasts two seconds (longer
than a Sim test's budget, hence this folder).
"""
from pathlib import Path
import tempfile
import time
import unittest

from do_math import formal
from do_math.windows_job import JobInspection

LINGER_SECONDS = 10


class LingeringJob:
    """A Job whose process stays after ``terminate`` for ``LINGER_SECONDS`` of real time, then leaves.

    It empties eventually, so a termination loop without a deadline fails the
    assertion instead of hanging the suite.
    """

    name, pid, creation_filetime = 'worker', 17, 1

    def __init__(self):
        self.terminated_at = None
        self.terminate_calls = self.close_calls = 0

    def resume(self):
        pass

    def wait(self, timeout=None):
        return False

    def terminate(self, exit_code=1):
        self.terminate_calls += 1
        self.terminated_at = time.monotonic()

    def inspect(self):
        gone = self.terminated_at is not None and time.monotonic() >= self.terminated_at + LINGER_SECONDS
        return JobInspection(active_processes=0, process_ids=(), root_signaled=True) if gone else \
            JobInspection(active_processes=1, process_ids=(18,), root_signaled=True)

    def resource_usage(self):
        return {}

    def close(self):
        self.close_calls += 1


class OneJob:
    def __init__(self):
        self.job = LingeringJob()

    def launch(self, argv, *, cwd=None, env=None, name=None, resource_limits=None):
        return self.job


class TerminationDeadlineTests(unittest.TestCase):
    def test_job_termination_confirmation_has_a_fixed_deadline(self):
        """About 2 s: the product's termination deadline passes in real time."""
        jobs = OneJob()
        started = time.monotonic()
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(RuntimeError, 'formal Job termination could not be confirmed'):
                formal._job_run(['fixture'], Path(d), should_stop=lambda: True, jobs=jobs)
        self.assertLess(time.monotonic() - started, LINGER_SECONDS, 'the deadline, not the Job leaving, ended the wait')
        self.assertEqual((jobs.job.terminate_calls, jobs.job.close_calls), (1, 1))


if __name__ == '__main__':
    unittest.main()
