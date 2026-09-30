"""The maintenance fence (``maintenance_gate``, layer 2): it drains execution without becoming a user pause.

The rules act on a runtime mapping; ``settle`` reads the time of its judgment
from the clock port, here the fake clock.
"""
import unittest

from do_math import maintenance_gate
from support.fakes.clock import FakeClock


class MaintenanceFenceTests(unittest.TestCase):
    def test_quiescence_does_not_release_unknown_execution_or_user_pause(self):
        clock = FakeClock()
        runtime = {'executions': {'EX-one': {'id': 'EX-one', 'status': 'starting'}},
                   'reservations': {}, 'user_pause': {'request_id': 'UC-user'}, 'status': 'paused'}
        request = {'action': 'quiesce', 'id': 'UC-maint', 'origin': 'operator', 'text': 'install',
                   'created_at': '2026-09-25T00:00:00Z'}
        self.assertTrue(maintenance_gate.apply_control(runtime, request))
        maintenance_gate.settle(runtime, clock=clock)
        self.assertEqual(runtime['maintenance_fence']['state'], 'blocked')
        release = {**request, 'action': 'release_quiesce', 'id': 'UC-release', 'config': {'fence_id': 'UC-maint'}}
        with self.assertRaisesRegex(ValueError, '^maintenance has not reached its termination barrier$'):
            maintenance_gate.apply_control(runtime, release)
        self.assertEqual(runtime['maintenance_fence']['state'], 'blocked')
        runtime['executions']['EX-one']['status'] = 'ended'
        maintenance_gate.settle(runtime, clock=clock)
        self.assertTrue(maintenance_gate.apply_control(runtime, release))
        self.assertNotIn('maintenance_fence', runtime)
        self.assertEqual(runtime['user_pause'], {'request_id': 'UC-user'})
        self.assertEqual(runtime['status'], 'paused')


if __name__ == '__main__':
    unittest.main()
