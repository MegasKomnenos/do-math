"""정비 울타리는 발행 주체와 종결 장벽을 보존하고 사용자 정지를 대체하지 않는다."""
from copy import deepcopy
import unittest

from do_math import maintenance_gate
from support.fakes.clock import FakeClock


def request(action='quiesce', origin='user', **changes):
    return dict(id='UC-fence', action=action, origin=origin, text='정비 사유',
                created_at='2090-01-01T00:00:00+00:00', config={}, **changes)


class MaintenanceGuardTests(unittest.TestCase):
    def test_unrelated_control_and_absent_fence_have_no_effect(self):
        runtime = {'status': 'paused'}
        self.assertFalse(maintenance_gate.apply_control(runtime, request('pause')))
        self.assertFalse(maintenance_gate.settle(runtime, clock=FakeClock()))
        self.assertEqual(runtime, {'status': 'paused'})

    def test_unknown_origin_duplicate_and_wrong_release_are_rejected(self):
        for origin in (None, 'worker'):
            with self.subTest(origin=origin):
                runtime = {}
                with self.assertRaisesRegex(ValueError, '^maintenance control requires a known origin$'):
                    maintenance_gate.apply_control(runtime, request(origin=origin))
                self.assertEqual(runtime, {})
        runtime = {'status': 'paused'}
        maintenance_gate.apply_control(runtime, request())
        before = deepcopy(runtime)
        with self.assertRaisesRegex(ValueError, '^an existing maintenance fence must be released explicitly$'):
            maintenance_gate.apply_control(runtime, request())
        with self.assertRaisesRegex(ValueError, '^release must name the current maintenance fence$'):
            maintenance_gate.apply_control(runtime, request('release_quiesce'))
        self.assertEqual(runtime, before)

    def test_operator_cannot_release_user_fence_and_user_must_wait_for_barrier(self):
        runtime = {'status': 'paused'}
        maintenance_gate.apply_control(runtime, request())
        release = {**request('release_quiesce', 'operator'), 'config': {'fence_id': 'UC-fence'}}
        with self.assertRaisesRegex(ValueError, '^operator cannot release a user maintenance fence$'):
            maintenance_gate.apply_control(runtime, release)
        release['origin'] = 'user'
        with self.assertRaisesRegex(ValueError, '^maintenance has not reached its termination barrier$'):
            maintenance_gate.apply_control(runtime, release)
        clock = FakeClock()
        clock.advance(7)
        self.assertTrue(maintenance_gate.settle(runtime, clock=clock))
        fence = deepcopy(runtime['maintenance_fence'])
        self.assertEqual((fence['state'], fence['settled_at']), ('quiescent', clock.now()))
        self.assertTrue(maintenance_gate.apply_control(runtime, release))
        self.assertEqual(runtime, {'status': 'paused', 'history': [
            {'kind': 'maintenance_released', 'fence': fence, 'request_id': 'UC-fence'}]})
