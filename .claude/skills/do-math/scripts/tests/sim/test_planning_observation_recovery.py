"""관찰 설정 대기는 실제 호출 준비자가 만들고 계획 수신자가 해제한다."""
from copy import deepcopy
import unittest

from do_math.execution_profiles import apply_editions, build_profiles
from support.engine_lifecycle import _ended_execution, approve
from support.planning_owner import enqueue
from support.planning_contract_inputs import prepared_sim, warm_prepared, only_task

setUpModule = warm_prepared


class ObservationRecoveryTests(unittest.TestCase):
    def setUp(self):
        self.sim = prepared_sim()
        self.engine = self.sim.engine

    def held(self, role='task_contract_review'):
        """관찰 창 한 필드를 비운 설정을 정본 프로필 생산자와 호출 준비자에 넘긴다."""
        normal = deepcopy(self.sim.instance['config'])
        invalid = deepcopy(normal)
        del invalid['tool_review_window_seconds']
        editions = build_profiles(invalid, host=self.sim.ports.host)
        apply_editions(self.sim.instance, editions)
        task = only_task(self.sim)
        if role == 'research_work':
            task['profile_refs'] = deepcopy(editions['role_profile_refs']['research_work'])
            approve(self.engine, task)
        action = enqueue(self.engine, role, task['id'])
        result = self.engine._prepare_call(action)
        self.assertIs(result, True)
        entry = self.sim.runtime['waiting_actions'][action['id']]
        self.assertEqual(entry['kind'], 'observation_configuration')
        self.assertEqual([r['field'] for r in entry['observation_errors']], ['tool_review_window_seconds'])
        return action['id'], normal

    def restore_configuration(self, normal):
        self.sim.instance['config'] = normal
        editions = build_profiles(normal, host=self.sim.ports.host)
        apply_editions(self.sim.instance, editions)

    def test_unchanged_invalid_configuration_keeps_exact_wait(self):
        aid, _ = self.held()
        before = deepcopy((self.sim.instance, self.sim.runtime))
        self.engine._retry_observation_configuration()
        self.assertEqual((self.sim.instance, self.sim.runtime), before)
        self.assertEqual(self.sim.runtime['waiting_actions'][aid]['kind'], 'observation_configuration')

    def test_recovered_review_rebinds_and_removes_exact_previous_wait(self):
        aid, normal = self.held()
        previous = deepcopy(self.sim.runtime['waiting_actions'][aid])
        self.restore_configuration(normal)
        history = deepcopy(self.sim.runtime['history'])
        queue = deepcopy(self.sim.runtime['queue'])
        self.engine._retry_observation_configuration()
        added = self.sim.runtime['queue'][len(queue):]
        self.assertEqual(len(added), 1)
        self.assertEqual(self.sim.runtime['queue'][:len(queue)], queue)
        action = added[0]
        self.assertEqual(action['id'], aid)
        self.assertNotEqual(action['profile_ref'], previous['action']['profile_ref'])
        self.assertIn(action['profile_ref'], self.sim.instance['role_profile_refs']['task_contract_review'])
        self.assertNotIn(aid, self.sim.runtime['waiting_actions'])
        self.assertEqual(self.sim.runtime['history'], [*history, {
            'kind': 'observation_configuration_reprepared', 'action_id': aid,
            'previous': previous, 'profile_ref': action['profile_ref']}])
        self.engine._save()
        self.sim.restart()
        self.assertEqual(self.sim.runtime['queue'], queue + added)

    def test_no_adopted_review_profile_keeps_wait_instead_of_raising(self):
        aid, normal = self.held()
        self.restore_configuration(normal)
        self.sim.instance['role_profile_refs']['task_contract_review'] = []
        before = deepcopy((self.sim.instance, self.sim.runtime))
        self.engine._retry_observation_configuration()
        self.assertEqual((self.sim.instance, self.sim.runtime), before)
        self.assertIn(aid, self.sim.runtime['waiting_actions'])

    def test_unrepaired_work_profiles_do_not_create_repreparation(self):
        aid, _ = self.held('research_work')
        before = deepcopy((self.sim.instance, self.sim.runtime))
        self.engine._retry_observation_configuration()
        self.assertEqual((self.sim.instance, self.sim.runtime), before)
        self.assertEqual(self.sim.runtime['waiting_actions'][aid]['kind'], 'observation_configuration')

    def test_resolved_wait_finishes_its_activity_and_preserves_exact_history(self):
        aid, normal = self.held('research_work')
        self.restore_configuration(normal)
        _ended_execution(self.engine, 'EX-rules', 'research_preparation')
        previous = deepcopy(self.sim.runtime['waiting_actions'][aid])
        activity_id = previous['action']['owner_activity_id']
        history = deepcopy(self.sim.runtime['history'])
        self.engine._resolve_task_observation_waits(only_task(self.sim)['id'], 'EX-rules')
        self.assertNotIn(aid, self.sim.runtime['waiting_actions'])
        self.assertEqual(self.sim.runtime['activities'][activity_id]['status'], 'finished')
        self.assertEqual(self.sim.runtime['history'], [*history, {
            'kind': 'observation_configuration_resolved', 'action_id': aid,
            'failed_execution_id': None, 'resolved_by': 'EX-rules', 'previous': previous}])
        self.engine._save()

    def test_other_pending_activity_action_prevents_premature_finish(self):
        aid, normal = self.held('research_work')
        self.restore_configuration(normal)
        previous = deepcopy(self.sim.runtime['waiting_actions'][aid])
        activity_id = previous['action']['owner_activity_id']
        enqueue(self.engine, 'research_plan', owner_activity_id=activity_id)
        _ended_execution(self.engine, 'EX-rules', 'research_preparation')
        activity = deepcopy(self.sim.runtime['activities'][activity_id])
        self.engine._resolve_task_observation_waits(only_task(self.sim)['id'], 'EX-rules')
        self.assertNotIn(aid, self.sim.runtime['waiting_actions'])
        self.assertEqual(self.sim.runtime['activities'][activity_id], activity)
        self.engine._save()
