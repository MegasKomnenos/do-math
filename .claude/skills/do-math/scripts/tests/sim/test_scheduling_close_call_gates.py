"""실제 엔진의 호출 준비·배정 음성 경로. 가짜 엔진이나 반환값 주입은 쓰지 않는다."""
from copy import deepcopy
from datetime import datetime, timedelta
import unittest

from support.engine_lifecycle import applied
from support.scheduling_parallel import ready_work_sim
from support.sim import Sim, warm_template


def setUpModule():
    warm_template()
    ready_work_sim(1)


class CallGateTests(unittest.TestCase):
    def test_prepare_rechecks_clock_before_creating_execution(self):
        sim = ready_work_sim(1)
        action = deepcopy(sim.runtime['queue'][0])
        before = deepcopy(sim.runtime['executions'])
        persisted = datetime.fromisoformat(sim.runtime['last_observed_utc'])
        sim.clock.set_wall(persisted - timedelta(seconds=5))
        self.assertIs(sim.engine._prepare_call(action), False)
        self.assertEqual(sim.runtime['executions'], before)
        self.assertEqual(sim.runtime['availability'], {
            'state': 'blocked', 'reason': 'clock_regression', 'next_owner': 'operator'})
        _, _, stored = sim.engine.store.load(sim.engine.head)
        self.assertEqual(stored['availability'], sim.runtime['availability'])

    def test_dispatch_missing_task_records_exact_readiness_wait(self):
        sim = ready_work_sim(1)
        action = deepcopy(sim.runtime['queue'][0])
        action['target'] = 'TK-absent'
        before = deepcopy(sim.runtime['executions'])
        self.assertFalse(sim.engine._dispatchable(action))
        self.assertEqual(action['dispatch_wait'], {
            'kind': 'task_readiness', 'state': 'not_ready', 'errors': ['task is absent'], 'basis': []})
        self.assertEqual(sim.runtime['executions'], before)

    def test_return_without_execution_id_preserves_every_record(self):
        sim = Sim.activated()
        before = deepcopy(sim.runtime)
        self.assertIsNone(sim.engine._local_call_returned(None, {'status': 'failed'}))
        self.assertEqual(sim.runtime, before)

    def test_pause_idle_status_and_reconsideration_do_not_override_user(self):
        sim = Sim.activated()
        applied(sim, 'pause', text='사용자 상태 우선순위')
        before = deepcopy(sim.runtime)
        sim.engine._idle_wait_status()
        self.assertEqual(sim.runtime, before)
        self.assertIsNone(sim.engine._schedule_reconsideration(sim.clock.now()))
        self.assertEqual(sim.runtime, before)
