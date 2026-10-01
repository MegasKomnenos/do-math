"""Jobs port contract (설계 2.2, A12): an owned Job runs one program; the real Windows Job and the fake agree.

The program writes a marker file so both sides show that it ran exactly when
resumed. The fake resolves the same argv through its program table.
"""
from pathlib import Path
import tempfile
import unittest

from support.fakes.jobs import job_turn, make_fake


from support.port_contracts.jobs import MARK, _write_mark, JobsContract, _two_steps

class FakeJobsContract(JobsContract, unittest.TestCase):
    def make(self):
        return make_fake(programs=[(lambda argv: argv[1:3] == ['-c', MARK], _write_mark)])


class LiveFakeJobTests(unittest.TestCase):
    """The fake's live mode (이음매 장부 18): the program runs beside its runner, one step per barrier probe.

    Without it a resumed program has always ended before the runner's poll loop
    first looks, so no observation is live and no stop reaches a running program.
    """

    def setUp(self):
        self.mark = Path(self.enterContext(tempfile.TemporaryDirectory())) / 'mark.txt'
        self.jobs = make_fake(programs=[(lambda argv: argv[1] == 'two-steps', _two_steps)])
        self.jobs.live = True
        self.job = self.jobs.launch(['python', 'two-steps', str(self.mark)], name='Local\\DoMath-live')
        self.addCleanup(self.job.close)

    def test_a_resumed_program_is_still_running_at_its_first_turn(self):
        self.job.resume()
        self.assertEqual(self.mark.read_text(), 'a')
        self.assertIs(self.jobs.named_job_empty('Local\\DoMath-live'), False)

    def test_each_barrier_probe_runs_the_program_to_its_next_turn(self):
        self.job.resume()
        observed = self.job.inspect()
        self.assertEqual((observed.root_signaled, observed.active_processes, observed.process_ids), (True, 0, ()))
        self.assertEqual((self.mark.read_text(), self.job.exit_code), ('ab', 0))

    def test_a_runner_polling_with_wait_also_runs_the_program_on(self):
        """``formal._job_run`` polls ``wait(0)`` rather than ``inspect``; both are the runner's probe."""
        self.job.resume()
        self.assertIs(self.job.wait(0), True)
        self.assertEqual((self.mark.read_text(), self.job.exit_code), ('ab', 0))

    def test_termination_ends_the_program_at_its_turn(self):
        self.job.resume()
        self.job.terminate(7)
        observed = self.job.inspect()
        self.assertEqual((observed.root_signaled, observed.active_processes), (True, 0))
        self.assertEqual((self.mark.read_text(), self.job.exit_code), ('ax', 7))

    def test_a_turn_outside_a_live_program_does_nothing(self):
        self.assertIsNone(job_turn())


if __name__ == '__main__':
    unittest.main()
