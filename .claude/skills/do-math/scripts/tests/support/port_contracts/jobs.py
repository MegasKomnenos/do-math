"""Jobs port contract (설계 2.2, A12): an owned Job runs one program; the real Windows Job and the fake agree.

The program writes a marker file so both sides show that it ran exactly when
resumed. The fake resolves the same argv through its program table.
"""

import os

from pathlib import Path

import sys

import tempfile

import unittest

from run_tests import wait_for_worker

from do_math.windows_job import process_identity

from support.fakes.jobs import JobTerminated, job_turn

MARK = "import sys, pathlib; pathlib.Path(sys.argv[1]).write_text('ran'); raise SystemExit(0)"

def _write_mark(argv, cwd, env):
    Path(argv[-1]).write_text('ran')
    return 0

@unittest.skipUnless(os.name == 'nt', 'Windows port contract')
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
        self.addCleanup(self._cleanup_job, job)
        return job

    def _cleanup_job(self, job):
        # close releases handles and kills remaining processes; it does not
        # wait for their cwd to be released. Keep ownership until the root and
        # all Job processes have ended, before TemporaryDirectory's cleanup.
        try:
            job.terminate()
            self.assertTrue(job.wait(), 'owned Job root did not end')
            wait_for_worker(job)
        finally:
            job.close()

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

    # Owner queries (설계 A13 개정): who launched, and whether that owner or a named Job has ended.

    def test_the_owner_identity_names_this_process_stably(self):
        owner = self.jobs.owner_identity()
        self.assertEqual(set(owner), {'pid', 'creation_filetime', 'host', 'session'})
        self.assertGreater(owner['pid'], 0)
        self.assertTrue(owner['creation_filetime'].isdigit())
        self.assertEqual(self.jobs.owner_identity(), owner)

    def test_the_current_owner_has_not_ended(self):
        self.assertIs(self.jobs.owner_ended(self.jobs.owner_identity()), False)

    def test_the_same_pid_with_another_creation_time_has_ended(self):
        owner = self.jobs.owner_identity()
        reused = {**owner, 'creation_filetime': str(int(owner['creation_filetime']) + 1)}
        self.assertIs(self.jobs.owner_ended(reused), True)

    def test_an_owner_on_another_host_is_unknown(self):
        owner = self.jobs.owner_identity()
        self.assertIsNone(self.jobs.owner_ended({**owner, 'host': owner['host'] + '-elsewhere'}))

    def test_a_job_name_nobody_created_is_empty(self):
        self.assertIs(self.jobs.named_job_empty('Local\\DoMath-' + os.urandom(16).hex()), True)

    def test_a_named_job_is_not_empty_until_its_program_ends(self):
        job = self.launch()
        self.assertIs(self.jobs.named_job_empty(job.name), False)
        job.resume()
        job.wait(30)
        # Job accounting can lag the root's exit signal, so emptiness is polled for (as above).
        for _ in range(500):
            if self.jobs.named_job_empty(job.name):
                break
            job.wait(0.02)
        self.assertIs(self.jobs.named_job_empty(job.name), True)

def _two_steps(argv, cwd, env):
    """Write 'a', hand the runner a turn, write 'b'; on termination leave 'x' where it stopped."""
    mark = Path(argv[-1])
    mark.write_text('a')
    try:
        job_turn()
    except JobTerminated:
        mark.write_text(mark.read_text() + 'x')
        raise
    mark.write_text(mark.read_text() + 'b')
    return 0
