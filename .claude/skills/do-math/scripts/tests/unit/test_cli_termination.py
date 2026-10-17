"""The local CLI Job barrier is true only after root and descendants end."""
import unittest

from do_math.cli_execution import termination_confirmed
from do_math.windows_job import JobInspection


class TerminationTests(unittest.TestCase):
    def test_barrier_requires_the_root_and_both_empty_process_observations(self):
        self.assertIs(termination_confirmed(JobInspection(0, (), True)), True)
        for state in (JobInspection(0, (), False), JobInspection(1, (), True),
                      JobInspection(0, (17,), True)):
            with self.subTest(state=state):
                self.assertIs(termination_confirmed(state), False)
