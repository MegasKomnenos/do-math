"""2-C의 일반 idle·실제 목표 완료·미확인 복구 반환. 종결 상태를 조립하지 않는다."""
from copy import deepcopy
import unittest

from do_math import scheduled_operator as operator
from support.engine_lifecycle import clear_work
from support.engine_purpose import PurposeResponder, drive, purpose_sim
from support.operator_finish_scene import Scene
from support.scheduling_return_observer import OwnerProbe
from support.scheduling_parallel import ready_work_sim
from support.sim import Sim, warm_template


setUpModule = warm_template


class RemainingExitTests(unittest.TestCase):
    def test_idle_with_missing_capability_returns_without_new_execution(self):
        sim = ready_work_sim(1)
        sim.ports.host.identity['edition'] = 'unobserved-cli-edition'
        before = deepcopy(sim.runtime['executions'])
        reservations = deepcopy(sim.runtime['reservations'])
        with OwnerProbe(sim) as probe:
            answer = sim.engine.run(max_steps=1)
        self.assertEqual(answer['status'], 'waiting')
        self.assertEqual(answer['active_executions'], [])
        self.assertEqual(sim.runtime['executions'], before)
        self.assertEqual(sim.runtime['reservations'], reservations)
        self.assertEqual([a['dispatch_wait']['kind'] for a in sim.runtime['queue']], ['capability_evidence'])
        self.assertGreater(probe.passes, 0)
        self.assertIsNone(sim.engine._calls)

    def test_completed_goal_returns_without_repeating_any_role(self):
        sim = purpose_sim()
        sim.model.responder = PurposeResponder()
        drive(self, sim)
        self.assertEqual(sim.runtime['status'], 'completed')
        before = deepcopy(sim.runtime['executions'])
        reservations = deepcopy(sim.runtime['reservations'])
        count = len(sim.model.calls)
        with OwnerProbe(sim) as probe:
            answer = sim.engine.run(max_steps=1)
        self.assertEqual(answer['status'], 'completed')
        self.assertEqual(answer['active_executions'], [])
        self.assertEqual(sim.runtime['executions'], before)
        self.assertEqual(sim.runtime['reservations'], reservations)
        self.assertEqual(len(sim.model.calls), count)
        self.assertEqual(probe.failures, [])

    def test_unconfirmed_recovery_blocks_dispatch_without_releasing_its_ownership(self):
        scene = Scene()
        scene.answer()
        def unknown(call):
            scene.jobs.empty[scene.jobs.launched[-1].name] = None
        scene.cli.on_input = unknown
        result = scene.call(operator.recovery, failure={'kind': 'engine_unavailable',
                                                       'error': '합성 설치 실행 실패'})
        self.assertEqual(result['outcome'], 'recovery_termination_unknown')
        sim = scene.sim
        sim.ports = sim.engine.ports = scene.ports
        sim.engine._reload()
        eid = result['execution_id']
        before = set(sim.runtime['executions'])
        reservations = deepcopy(sim.runtime['reservations'])
        with OwnerProbe(sim) as probe:
            answer = sim.engine.run(max_steps=1)
        self.assertIsInstance(answer, dict)
        self.assertEqual(set(sim.runtime['executions']), before)
        self.assertEqual(sim.runtime['executions'][eid]['capacity']['local_termination'], 'unknown')
        self.assertNotEqual(sim.runtime['executions'][eid]['status'], 'ended')
        self.assertTrue(sim.runtime['executions'][eid]['owner_activity_id'])
        self.assertEqual(sim.runtime['reservations'], reservations)
        self.assertEqual(len(scene.cli.calls), 1)
        self.assertEqual(probe.failures, [])
