"""The launch ticket is bound to one execution (``launch``, layer 2).

The ticket's owner identity and Job name come from the Jobs and clock ports;
here their fakes, since validation reads only the ticket's fields.
"""
import unittest

from do_math.launch import ticket, validate
from support.fakes.clock import FakeClock
from support.fakes.jobs import FakeJobs

PROFILE = {'sha256': 'a' * 64, 'actor_kind': 'ai', 'role': 'research_work'}


class LaunchTicketTests(unittest.TestCase):
    def test_ticket_cannot_be_rebound_to_another_execution(self):
        t = ticket('EX-one', PROFILE, jobs=FakeJobs(), clock=FakeClock())
        self.assertIs(validate(t, execution_id='EX-one'), t)
        with self.assertRaisesRegex(ValueError, 'launch ticket execution differs'):
            validate(t, execution_id='EX-two')


if __name__ == '__main__':
    unittest.main()
