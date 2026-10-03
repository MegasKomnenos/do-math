"""기존 준비 생산물과 실제 엔진으로 중복 배정·실패 정산의 빈 분기를 검사한다."""
from copy import deepcopy
import unittest

from support.engine_lifecycle import clear_work
from support.engine_lifecycle import applied
from do_math.model_policy import MODELS
from support.scheduling_parallel import ready_work_sim
from support.sim import Sim, warm_template


def setUpModule():
    warm_template()
    ready_work_sim(1)


class DispatchBranchTests(unittest.TestCase):
    def test_prepare_rechecks_zero_capacity_and_preserves_closed_transport(self):
        sim = ready_work_sim(1)
        action = deepcopy(sim.runtime['queue'][0])
        applied(sim, 'configure', config={'session_limits': {'work': {model: 0 for model in MODELS.values()}}})
        before = set(sim.runtime['executions'])
        self.assertIs(sim.engine._prepare_call(action), False)
        added = set(sim.runtime['executions']) - before
        self.assertEqual(len(added), 1)
        eid, = added
        row = sim.runtime['executions'][eid]
        self.assertEqual((row['status'], row['outcome']), ('ended', 'start_failed'))
        self.assertNotIn(eid, sim.engine._transport_bindings)
        queued = next(a for a in sim.runtime['queue'] if a['id'] == action['id'])
        self.assertEqual(queued['dispatch_wait']['kind'], 'capacity')
        self.assertEqual(queued['dispatch_wait']['next_owner'], 'user')
        self.assertEqual(sim.engine.store.load(sim.engine.head)[2]['executions'][eid], row)

    def test_interrupted_missing_and_ended_calls_leave_every_record_unchanged(self):
        sim = Sim.activated()
        ended = next(e for e in sim.runtime['executions'].values() if e['status'] == 'ended')
        before = deepcopy(sim.runtime)
        self.assertEqual(sim.engine._record_interrupted_calls([
            ('EX-absent', b'{}', 'absent.json', {}), (ended['id'], b'{}', 'ended.json', {})]), {})
        self.assertEqual(sim.runtime, before)

    def test_failed_live_review_stops_only_its_live_parent_and_persists_reason(self):
        sim = Sim.activated()
        parent = sim.engine._register_execution({'id': 'AC-parent', 'role': 'maintenance'},
            {'id': 'EX-parent', 'role': 'maintenance', 'status': 'running'})
        self.assertIsNotNone(parent)
        before = deepcopy(sim.runtime)
        for action in ({'target': 'EX-parent'}, {'live': True, 'target': 'EX-absent'}):
            sim.engine._failed_live_review(action, '진단 호출 실패')
            self.assertEqual(sim.runtime, before)
        sim.engine._failed_live_review({'live': True, 'target': 'EX-parent'}, '진단 호출 실패')
        expected = deepcopy(before)
        expected['executions']['EX-parent'].update(stop_requested='operating_review_unavailable',
            after_stop={'decision': 'wait', 'reason': '진단 호출 실패'})
        self.assertEqual(sim.runtime, expected)
        sim.engine._save()
        self.assertEqual(sim.engine.store.load(sim.engine.head)[2]['executions'], expected['executions'])

    def test_duplicate_action_and_different_identity_same_task_are_not_dispatched(self):
        for identical in (True, False):
            with self.subTest(identical=identical):
                sim = ready_work_sim(1)
                action = deepcopy(sim.runtime['queue'][0])
                self.assertTrue(sim.engine._dispatchable(action))
                live_action = deepcopy(action)
                if not identical:
                    live_action.update(id='AC-other', stage='separate-stage')
                row = sim.engine._register_execution(live_action,
                    {'id': 'EX-occupied', 'role': action['role'], 'status': 'running'})
                self.assertIsNotNone(row)
                before = deepcopy(sim.runtime['executions'])
                self.assertFalse(sim.engine._dispatchable(action))
                self.assertEqual(sim.runtime['executions'], before)
                if identical:
                    self.assertNotIn('dispatch_wait', action)
                else:
                    self.assertEqual(action['dispatch_wait'], {
                        'kind': 'task_readiness', 'state': 'not_ready', 'basis': [],
                        'errors': ['task is occupied or has an unresolved wait'],
                        'waits': [], 'dispatch_occupied': True})

    def test_planning_role_is_singleton_even_when_action_identity_differs(self):
        sim = Sim.activated()
        clear_work(sim)
        sim.engine._enqueue('research_plan', reason='중복 계획 준비')
        action = deepcopy(sim.runtime['queue'][0])
        self.assertTrue(sim.engine._dispatchable(action))
        occupied = {**action, 'id': 'AC-other-plan', 'stage': 'different'}
        self.assertIsNotNone(sim.engine._register_execution(occupied,
            {'id': 'EX-plan', 'role': 'research_plan', 'status': 'running'}))
        before = deepcopy(sim.runtime['executions'])
        self.assertFalse(sim.engine._dispatchable(action))
        self.assertEqual(sim.runtime['executions'], before)

    def test_prepare_obsolete_action_removes_only_its_own_queue_record(self):
        sim = ready_work_sim(1)
        action = deepcopy(sim.runtime['queue'][0])
        action['selected_contract_sha256'] = '0' * 64
        before = deepcopy(sim.runtime['executions'])
        self.assertIs(sim.engine._prepare_call(action), True)
        self.assertEqual(sim.runtime['executions'], before)
        self.assertNotIn(action['id'], [a['id'] for a in sim.runtime['queue']])

    def test_continuation_requires_an_ended_predecessor_and_its_unfinished_activity(self):
        from support.engine_control import running_work
        sim = Sim.activated()
        ended = next(row for row in sim.runtime['executions'].values()
                     if row['status'] == 'ended'
                     and sim.runtime['activities'][row['owner_activity_id']]['status'] == 'finished')
        with running_work(sim) as call:
            before = deepcopy(sim.runtime)
            cases = [
                ({**deepcopy(call.execution['action']), 'continuation_of': call.execution_id},
                 'continuation requires an ended, explicitly referenced execution'),
                ({**deepcopy(call.execution['action']), 'continuation_of': ended['id']},
                 'continuation cannot change its activity'),
                ({**deepcopy(ended['action']), 'continuation_of': ended['id']},
                 'finished activity cannot be continued'),
            ]
            for action, reason in cases:
                with self.subTest(reason=reason), self.assertRaisesRegex(ValueError, '^' + reason + '$'):
                    sim.engine._activity_for_action(action)
                self.assertEqual(sim.runtime, before)
            self.assertEqual(sim.engine.store.load(sim.engine.head)[2], sim.runtime)

    def test_machine_start_callback_rejects_an_actual_running_ai_job(self):
        from do_math.windows_job import process_identity
        from support.engine_control import running_work
        sim = Sim.activated()
        with running_work(sim) as call:
            before = deepcopy((sim.engine.head, sim.runtime))
            job = sim.jobs.launched[-1]
            with self.assertRaisesRegex(ValueError, '^machine process callback requires a machine execution$'):
                sim.engine._machine_started(call.execution_id,
                    {**process_identity(job), 'job_name': job.name})
            self.assertEqual((sim.engine.head, sim.runtime), before)

    def test_dispatch_rejects_a_selection_bound_to_another_produced_contract(self):
        from do_math.planning import contract_hash
        sim = ready_work_sim(2)
        action, other = [deepcopy(row) for row in sim.runtime['queue']]
        current = contract_hash(sim.runtime['tasks'][action['target']])
        foreign = contract_hash(sim.runtime['tasks'][other['target']])
        self.assertNotEqual(current, foreign)
        # Corrupt only this reference; both source contracts and approvals are real producers.
        action['selected_contract_sha256'] = foreign
        before = deepcopy(sim.runtime['executions'])
        self.assertFalse(sim.engine._dispatchable(action))
        self.assertEqual(sim.runtime['executions'], before)
        self.assertNotIn(action['id'], [a['id'] for a in sim.runtime['queue']])
        self.assertIn(other['id'], [a['id'] for a in sim.runtime['queue']])
        self.assertEqual(sim.runtime['tasks'][action['target']]['status'], 'waiting')
        obsolete, = [row for row in sim.runtime['history']
                     if row.get('kind') == 'obsolete_selection' and row['action']['id'] == action['id']]
        self.assertEqual(obsolete['action']['selected_contract_sha256'], foreign)
        self.assertEqual(obsolete['reason'], 'selected contract or its approval is no longer current')
        self.assertEqual(len([a for a in sim.runtime['queue'] if a['role'] == 'research_plan']), 1)
        sim.engine._save()
        self.assertEqual(sim.engine.store.load(sim.engine.head)[2]['queue'], sim.runtime['queue'])
        self.assertEqual(sim.model.calls, [])
