"""8-B: 실제 실행 전·중·반환 뒤 정산. 여러 공개 역할 호출이어서 flows에 둔다."""
from copy import deepcopy
import unittest

from do_math.execution_profiles import LEAN_ROLES
from support.engine_lifecycle import warm_lifecycle
from support.live_finish_model import execution, install
from support.scheduling_return_observer import OwnerProbe, assert_settled
from support.scheduling_return_ports import defer_first_calculation
from support.scheduling_machine import formal_scene, trust_scene, hold_lean
from support.scheduling_parallel import ready_work_sim, round_robin
from support.sim import warm_template


def setUpModule():
    warm_template()
    warm_lifecycle()
    ready_work_sim(1)
    ready_work_sim(2)


class ReturnSettlementTests(unittest.TestCase):

    def test_ai_running_stop_and_fence_drain_every_execution(self):
        for action in ('pause', 'quiesce', 'close'):
            with self.subTest(action=action):
                sim = ready_work_sim(2)
                sim.ports.calls.choose = round_robin()
                before = set(sim.runtime['executions'])
                entered = []

                def hook(cli, context):
                    entered.append(execution(sim, cli.workspace)['id'])
                    if len(entered) == 2:
                        sim.control(action, text='진행 중 실행의 반환 정산')
                    cli.until(lambda: False, '종료 제어가 실행을 정지시키지 않음', limit=64)

                install(sim, hook)
                with OwnerProbe(sim) as probe:
                    answer = sim.engine.run(max_steps=2)
                added = assert_settled(self, sim, before, probe)
                self.assertEqual(len(entered), 2)
                self.assertEqual(added, set(entered))
                self.assertEqual(answer['active_executions'], [])
                if action == 'quiesce':
                    self.assertEqual(sim.runtime['maintenance_fence']['state'], 'quiescent')
                else:
                    self.assertEqual(answer['status'], 'paused' if action == 'pause' else 'closed')
                settled = deepcopy(sim.runtime['reservations'])
                sim.restart()
                sim.engine.run(max_steps=1)
                self.assertEqual(sim.runtime['reservations'], settled)
                self.assertEqual(set(sim.runtime['executions']) - before, added)

    def test_step_cap_applies_sealed_ai_completion_before_return(self):
        sim = ready_work_sim(1)
        before = set(sim.runtime['executions'])
        with OwnerProbe(sim) as probe:
            sim.engine.run(max_steps=1)
        added = assert_settled(self, sim, before, probe)
        self.assertEqual(len(added), 1)
        eid, = added
        row = sim.runtime['executions'][eid]
        self.assertEqual(row['outcome'], 'output_accepted')
        receipts = [r for r in sim.runtime['control_receipts'].values()
                    if r['execution_id'] == eid and r['kind'] == 'submit_intent']
        self.assertEqual(len(receipts), 1)
        self.assertEqual(receipts[0]['state'], 'accepted')
        self.assertEqual([r for r in sim.runtime.get('waiting_actions', {}).values()
                          if r.get('execution_id') == eid and r.get('kind') == 'submission_publication'], [])
        # 같은 완료를 재적용하거나 예약을 두 번 반환하지 않는 별도 공개 재진입.
        before_receipts = deepcopy(sim.runtime['control_receipts'])
        before_reservations = deepcopy(sim.runtime['reservations'])
        sim.engine.run(max_steps=1, until_active=True)
        self.assertEqual(sim.runtime['control_receipts'], before_receipts)
        self.assertEqual(sim.runtime['reservations'], before_reservations)
        self.assertEqual(set(sim.runtime['executions']) - before, added)

    def test_machine_first_turn_stop_has_confirmed_termination(self):
        builders = {'formal_check': formal_scene, 'trust_check': trust_scene}
        self.assertEqual(set(builders), set(LEAN_ROLES))
        for role in LEAN_ROLES:
            with self.subTest(role=role):
                sim, action, _ = builders[role]()
                sim.engine.runtime['queue'][:] = [action]
                sim.engine._save()
                before = set(sim.runtime['executions'])
                checks = len(sim.lean.checks)
                defer_first_calculation(sim, lambda: sim.control('pause', text='검증 계산 시작 전 정지'))
                with OwnerProbe(sim) as probe:
                    sim.engine.run(max_steps=1)
                added = assert_settled(self, sim, before, probe)
                self.assertEqual(len(added), 1)
                eid, = added
                self.assertEqual(sim.runtime['executions'][eid]['role'], role)
                self.assertEqual(sim.runtime['executions'][eid]['outcome'], 'execution_incomplete')
                self.assertEqual(len(sim.lean.checks), checks)

    def test_machine_running_pause_is_applied_within_one_owner_pass(self):
        for builder in (formal_scene, trust_scene):
            with self.subTest(builder=builder.__name__):
                sim, action, _ = builder()
                sim.engine.runtime['queue'][:] = [action]
                sim.engine._save()
                before = set(sim.runtime['executions'])
                seen = []
                probe = OwnerProbe(sim)

                def hold():
                    from support.fakes.calls import owner_turn
                    requested = probe.passes
                    sim.control('pause', text='실행 중 검증을 정지')
                    owner_turn()
                    seen.append((requested, probe.passes, sim.runtime['status']))

                hold_lean(sim, hold)
                with probe:
                    sim.engine.run(max_steps=1)
                added = assert_settled(self, sim, before, probe)
                self.assertEqual(len(added), 1)
                self.assertEqual(len(seen), 1)
                requested, applied_at, status = seen[0]
                self.assertEqual(status, 'paused')
                self.assertEqual(applied_at - requested, 1)
