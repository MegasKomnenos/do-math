"""The maintenance fence (``maintenance_gate``, layer 2): it drains execution without becoming a user pause.

The rules act on a runtime mapping; ``settle`` reads the time of its judgment
from the clock port, here the fake clock.
"""
import unittest
from copy import deepcopy

from do_math import maintenance_gate
from support.fakes.clock import FakeClock


class MaintenanceFenceTests(unittest.TestCase):
    def test_deferred_publication_ends_only_its_locally_terminated_stopping_execution(self):
        from do_math.execution_lifecycle import create_execution, transition_execution
        clock = FakeClock()
        def execution(identifier, stopped, confirmed):
            value = create_execution(execution_id=identifier, owner_activity_id='AY-one', actor_kind='ai',
                input_manifest={}, profile_ref={'id': 'PF-one'}, created_at=clock.now())
            transition_execution(value, 'starting', at=clock.now())
            transition_execution(value, 'running', at=clock.now())
            if stopped:
                transition_execution(value, 'stopping', at=clock.now())
            if confirmed:
                value['capacity'] = {'local_termination': 'confirmed'}
            return value
        runtime = {'executions': {identifier: execution(identifier, stopped, confirmed)
            for identifier, stopped, confirmed in [('EX-done', True, True),
                ('EX-unknown', True, False), ('EX-running', False, True), ('EX-other', True, True)]},
            'waiting_actions': {identifier: {'kind': 'submission_publication', 'execution_id': identifier}
                for identifier in ('EX-done', 'EX-unknown', 'EX-running', 'EX-absent')},
            'status': 'paused', 'user_pause': {'request_id': 'UC-user'}}
        maintenance_gate.apply_control(runtime, {'action': 'quiesce', 'id': 'UC-fence', 'origin': 'user',
            'text': 'defer publication', 'created_at': clock.now()})
        before = deepcopy(runtime)
        self.assertTrue(maintenance_gate.settle(runtime, clock=clock))
        done = runtime['executions']['EX-done']
        self.assertEqual((done['status'], done['outcome'], done['result_disposition']),
            ('ended', 'execution_incomplete', {'kind': 'deferred_publication'}))
        self.assertEqual(done['ended_at'], clock.now())
        for identifier in ('EX-unknown', 'EX-running', 'EX-other'):
            self.assertEqual(runtime['executions'][identifier], before['executions'][identifier])
        self.assertEqual(runtime['waiting_actions'], before['waiting_actions'])
        self.assertEqual(runtime['maintenance_fence']['state'], 'blocked')
        self.assertEqual(runtime['maintenance_fence']['pending_executions'], ['EX-unknown', 'EX-running', 'EX-other'])
        self.assertEqual(runtime['user_pause'], before['user_pause'])
        self.assertEqual(runtime['status'], 'paused')

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
