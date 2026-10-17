"""2-C의 일반 idle·실제 목표 완료·미확인 복구 반환. 종결 상태를 조립하지 않는다."""
from copy import deepcopy
import unittest

from do_math import scheduled_operator as operator
from support.engine_purpose import PurposeResponder, drive, purpose_sim
from support.operator_finish_scene import Scene
from support.scheduling_exit_contracts import assert_no_dispatch
from support.scheduling_return_observer import OwnerProbe, assert_settled
from support.scheduling_parallel import ready_work_sim
from support.sim import warm_template


setUpModule = warm_template


class RemainingExitTests(unittest.TestCase):
    def test_idle_with_missing_capability_returns_without_new_execution(self):
        sim = ready_work_sim(1)
        sim.ports.host.identity['edition'] = 'unobserved-cli-edition'
        before = deepcopy(sim.runtime['executions'])
        reservations = deepcopy(sim.runtime['reservations'])
        with OwnerProbe(sim) as probe:
            answer = sim.engine.run(max_steps=1)
        assert_no_dispatch(self, sim, answer, before, reservations, probe)
        self.assertEqual(answer['status'], 'waiting')
        self.assertEqual(answer['active_executions'], [])
        self.assertEqual([a['dispatch_wait']['kind'] for a in sim.runtime['queue']], ['capability_evidence'])
        self.assertGreater(probe.passes, 0)

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
        assert_no_dispatch(self, sim, answer, before, reservations, probe)
        self.assertEqual(answer['status'], 'completed')
        self.assertEqual(answer['active_executions'], [])
        self.assertEqual(len(sim.model.calls), count)

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
        before = deepcopy(sim.runtime['executions'])
        reservations = deepcopy(sim.runtime['reservations'])
        # 공개 재진입의 복구는 미확인 실행에 보존 처분만 기록한다.
        expected = deepcopy(before)
        expected[eid]['recovery_disposition'] = 'preserve_space_and_reservations'
        with OwnerProbe(sim) as probe:
            answer = sim.engine.run(max_steps=1)
        assert_no_dispatch(self, sim, answer, expected, reservations, probe)
        self.assertEqual(sim.runtime['executions'][eid]['capacity']['local_termination'], 'unknown')
        self.assertNotEqual(sim.runtime['executions'][eid]['status'], 'ended')
        self.assertTrue(sim.runtime['executions'][eid]['owner_activity_id'])
        self.assertEqual(len(scene.cli.calls), 1)

    def test_until_active_waits_for_live_limited_recovery_after_public_resume(self):
        from support.fakes.calls import DeterministicCalls
        from support.live_finish_model import execution, install
        from support.provider_probes import ObservedCalls
        from support.scheduling_recovery import limited_recovery_sim

        sim = limited_recovery_sim()
        self.assertEqual(sim.instance['lifecycle']['state'], 'paused')
        self.assertEqual(sim.runtime['resume_lifecycle'], 'active')
        before = set(sim.runtime['executions'])
        entered, resumed = [], []

        def hook(cli, context):
            entered.append((execution(sim, cli.workspace)['id'], context['action']['id'],
                            sim.instance['lifecycle']['state']))
            resumed.append(sim.control('resume', text='제한 복구 실행 중 연구를 재개한다'))
            cli.until(lambda: sim.instance['lifecycle']['state'] == 'active',
                      '공개 resume이 active로 복원되지 않음', limit=64)

        def waiting(arguments):
            calls = arguments['self']
            return (sim.instance['lifecycle']['state'],
                    tuple((f.execution_id, f.done()) for f in calls.futures))

        install(sim, hook)
        with OwnerProbe(sim) as probe, ObservedCalls(
                wait=DeterministicCalls.wait, capture={'wait': waiting}) as observed:
            # 단계 상한 없이 until_active 자체의 기다림/반환을 확인한다.
            answer = sim.engine.run(until_active=True)
        added = assert_settled(self, sim, before, probe)
        self.assertEqual(len(entered), 1)
        eid, action_id, state = entered[0]
        self.assertEqual((action_id, state), ('AC-limited', 'paused'))
        self.assertEqual(added, {eid})
        self.assertEqual(sim.runtime['executions'][eid]['outcome'], 'output_accepted')
        self.assertEqual(sim.runtime['executions'][eid]['submission_receipt']['state'], 'accepted')
        self.assertTrue(any(state == 'active' and (eid, False) in futures
                            for state, futures in observed.captured('wait', caller='do_math.scheduler')))
        self.assertIsInstance(answer, dict)
        self.assertEqual(answer['active_executions'], [])
        self.assertEqual(sim.instance['lifecycle']['state'], 'active')
        self.assertNotIn('resume_lifecycle', sim.runtime)
        self.assertEqual(len(resumed), 1)
        self.assertIn(resumed[0]['request_id'], sim.runtime['processed_controls'])
        self.assertEqual(len(sim.model.calls), 1)
        calls = sim.ports.calls.created[-1]
        self.assertEqual(calls.futures, {})
        self.assertEqual(calls.turns, [])
        self.assertTrue(calls.stopping)
        _, stored_instance, _ = sim.engine.store.load(sim.engine.head)
        self.assertEqual(stored_instance['lifecycle'], sim.instance['lifecycle'])
