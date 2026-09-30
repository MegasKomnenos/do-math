"""Control acceptance order and the operator's limited authority, through the public ``control`` and the owner.

Every test restores an active instance from the template (``Sim.activated()``)
and sends public controls; the owner applies them with ``process_controls``.
The acceptance tests give ``control`` a scripted clock port (``support.scheduling_clock``)
so that wall times and temporary identifiers are those the test names.
"""
from concurrent.futures import ThreadPoolExecutor
import unittest

from do_math.engine import control
from support.scheduling_clock import ScriptedClock, with_clock
from support.sim import Sim, warm_template

setUpModule = warm_template
REVERSED_IDS = ['UC-01M2KWMGGK0000000000000002', 'UC-01M2KWMGGK0000000000000001']
OPERATOR_LIMIT = 'operator controls are limited to configure, pause, quiesce, release_quiesce, request, resume, source'


def send(sim, action, clock, **options):
    return control(sim.repository, sim.instance_id, action, ports=with_clock(sim, clock), **options)


class AcceptanceOrderTests(unittest.TestCase):
    def setUp(self):
        self.sim = Sim.activated()

    def test_controls_with_identical_wall_time_preserve_acceptance_order(self):
        clock = ScriptedClock(['2026-09-16T01:00:00+00:00'] * 2, REVERSED_IDS)
        send(self.sim, 'conversation', clock, config={'operation': 'attach', 'id': 'C-user', 'generation': 1,
                                                     'disconnect_policy': 'pause', 'lease_seconds': 60})
        send(self.sim, 'conversation', clock, config={'operation': 'detach', 'id': 'C-user', 'generation': 1})
        pending = self.sim.engine._inbox()
        self.assertEqual([row['created_at'] for row in pending], ['2026-09-16T01:00:00+00:00'] * 2)
        self.assertEqual([row['config']['operation'] for row in pending], ['attach', 'detach'])
        self.sim.engine.process_controls()
        self.assertEqual(self.sim.runtime['status'], 'paused')

    def test_control_processing_uses_acceptance_time_not_random_id_order(self):
        clock = ScriptedClock(['2026-09-16T01:00:00.000001+00:00', '2026-09-16T01:00:00.000002+00:00'], REVERSED_IDS)
        send(self.sim, 'pause', clock, text='first')
        send(self.sim, 'resume', clock, text='second')
        pending = self.sim.engine._inbox()
        self.assertEqual([row['action'] for row in pending], ['pause', 'resume'])
        self.assertEqual(int(pending[1]['accepted_order']) - int(pending[0]['accepted_order']), 1)
        self.sim.engine.process_controls()
        self.assertEqual(self.sim.runtime['status'], 'ready')

    def test_controls_preserve_acceptance_order_when_wall_clock_moves_back(self):
        clock = ScriptedClock(['2026-09-16T01:00:01+00:00', '2026-09-16T01:00:00+00:00'])
        send(self.sim, 'pause', clock, text='first')
        send(self.sim, 'resume', clock, text='second')
        pending = self.sim.engine._inbox()
        self.assertEqual([row['created_at'] for row in pending], ['2026-09-16T01:00:01+00:00', '2026-09-16T01:00:00+00:00'])
        self.assertEqual([row['action'] for row in pending], ['pause', 'resume'])
        self.sim.engine.process_controls()
        self.assertEqual(self.sim.runtime['status'], 'ready')

    def test_concurrent_controls_receive_distinct_durable_order(self):
        """About 1 to 3.5 s, near the 2 s Sim budget: four public controls accepted on concurrent threads, the cost under test."""
        with ThreadPoolExecutor(max_workers=4) as pool:
            accepted = list(pool.map(lambda index: self.sim.control('pause', text=f'parallel {index}'), range(4)))
        identifiers = {row['request_id'] for row in accepted}
        pending = [row for row in self.sim.engine._inbox() if row['id'] in identifiers]
        orders = sorted(int(row['accepted_order']) for row in pending)
        self.assertEqual(len(identifiers), 4)
        self.assertEqual(orders, list(range(orders[0], orders[0] + 4)))


class OperatorAuthorityTests(unittest.TestCase):
    def setUp(self):
        self.sim = Sim.activated()

    def apply(self, action, **options):
        self.sim.control(action, **options)
        self.sim.engine.process_controls()

    def test_operator_resume_cannot_release_a_user_pause(self):
        self.apply('pause', text='Wait for my decision.')
        self.assertEqual(self.sim.engine.status()['user_pause']['reason'], 'Wait for my decision.')
        self.apply('resume', origin='operator', text='Automatic recovery.')
        self.assertEqual(self.sim.runtime['status'], 'paused')
        self.apply('resume', origin='user')
        self.assertEqual(self.sim.runtime['status'], 'ready')
        self.assertIsNone(self.sim.engine.status()['user_pause'])

    def test_operator_cannot_create_mathematical_or_external_controls(self):
        for action in ('decision', 'input', 'conversation', 'close', 'external', 'trust', 'knowledge'):
            with self.subTest(action=action), self.assertRaisesRegex(ValueError, OPERATOR_LIMIT):
                self.sim.control(action, origin='operator', text='operator request')

    def test_conditional_hold_release_preserves_a_different_user_pause(self):
        self.sim.control('pause', text='A newer independent user pause.')
        self.sim.control('resume', config={'expected_user_pause_reason': 'User requested scheduled operator HOLD old-hold'})
        self.sim.engine.process_controls()
        self.assertEqual(self.sim.runtime['status'], 'paused')
        self.assertEqual(self.sim.runtime['user_pause']['reason'], 'A newer independent user pause.')

    def test_conditional_hold_release_handles_a_pause_still_in_the_inbox(self):
        reason = 'User requested scheduled operator HOLD pending-hold'
        self.sim.control('pause', text=reason)
        self.sim.control('resume', config={'expected_user_pause_reason': reason})
        self.sim.engine.process_controls()
        self.assertEqual(self.sim.runtime['status'], 'ready')
        self.assertIsNone(self.sim.engine.status()['user_pause'])

    def test_operator_respects_explicit_pause_on_conversation_loss(self):
        self.sim.control('conversation', config={'operation': 'attach', 'id': 'C-user', 'generation': 1,
                                                 'disconnect_policy': 'pause', 'lease_seconds': 60})
        self.sim.control('conversation', config={'operation': 'detach', 'id': 'C-user', 'generation': 1})
        self.sim.engine.process_controls()
        self.assertEqual(self.sim.runtime['status'], 'paused')
        self.apply('resume', origin='operator')
        self.assertEqual(self.sim.runtime['status'], 'paused')


if __name__ == '__main__':
    unittest.main()
