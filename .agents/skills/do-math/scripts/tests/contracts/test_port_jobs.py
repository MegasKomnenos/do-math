"""Jobs port contract (설계 2.2, A12): an owned Job runs one program; the real Windows Job and the fake agree.

The program writes a marker file so both sides show that it ran exactly when
resumed. The fake resolves the same argv through its program table.
"""
import os
from pathlib import Path
import sys
import tempfile
import unittest

from do_math.windows_job import process_identity
from support.fakes.jobs import make_fake

MARK = "import sys, pathlib; pathlib.Path(sys.argv[1]).write_text('ran'); raise SystemExit(0)"


def _write_mark(argv, cwd, env):
    Path(argv[-1]).write_text('ran')
    return 0


@unittest.skipUnless(os.name == 'nt', 'Windows Jobs exist only on Windows')
class JobsContract:
    def make(self):
        raise NotImplementedError

    def setUp(self):
        self.directory = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.mark = self.directory / 'mark.txt'
        self.jobs = self.make()

    def launch(self):
        job = self.jobs.launch([sys.executable, '-c', MARK, str(self.mark)], cwd=self.directory,
                               env=dict(os.environ), name='Local\\DoMath-contract-' + os.urandom(8).hex())
        self.addCleanup(job.close)
        return job

    def test_a_launched_job_is_suspended_until_resumed(self):
        job = self.launch()
        observed = job.inspect()
        self.assertFalse(observed.root_signaled)
        self.assertFalse(self.mark.exists())

    def test_a_resumed_program_runs_and_the_termination_barrier_is_observed(self):
        job = self.launch()
        job.resume()
        self.assertTrue(job.wait(30))
        # The root's signal can precede the Job accounting's release of its last
        # process, so the barrier is polled for, as the product does.
        barrier = None
        for _ in range(500):
            observed = job.inspect()
            barrier = (observed.root_signaled, observed.active_processes, observed.process_ids)
            if barrier == (True, 0, ()):
                break
            job.wait(0.02)
        self.assertEqual(barrier, (True, 0, ()))
        self.assertEqual(self.mark.read_text(), 'ran')

    def test_termination_before_resume_means_the_program_never_runs(self):
        job = self.launch()
        job.terminate()
        self.assertTrue(job.wait(30))
        self.assertTrue(job.inspect().root_signaled)
        self.assertFalse(self.mark.exists())

    def test_identity_and_resource_usage_have_the_product_shape(self):
        job = self.launch()
        identity = process_identity(job)
        self.assertIsInstance(identity['pid'], int)
        self.assertTrue(identity['creation_filetime'].isdigit())
        job.resume()
        job.wait(30)
        usage = job.resource_usage()
        self.assertEqual(set(usage), {'limits', 'peak_job_memory_bytes', 'cpu_time_100ns', 'scope'})
        self.assertEqual(set(usage['limits']), {'memory_bytes', 'cpu_rate_basis_points'})

    def test_a_job_resumes_only_once(self):
        job = self.launch()
        job.resume()
        with self.assertRaisesRegex(RuntimeError, 'already been resumed'):
            job.resume()


class FakeJobsContract(JobsContract, unittest.TestCase):
    def make(self):
        return make_fake(programs=[(lambda argv: argv[1:3] == ['-c', MARK], _write_mark)])


if __name__ == '__main__':
    unittest.main()
