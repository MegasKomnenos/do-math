"""정상 계획 상태에 호스트 설정 변경을 적용할 때의 큐·과제 경계."""
from copy import deepcopy
import unittest

from support.governance_cases import planned_sim
from support.scheduling_hosts import host_configuration


class GovernanceHostTransitionInputTests(unittest.TestCase):
    def test_settled_review_scope_keeps_its_pinned_profile(self):
        from support.governance_cases import review_question_sim
        sim = review_question_sim()
        execution = next(e for e in sim.runtime['executions'].values()
                         if e['role'] == 'identity_review' and e['action'].get('stage') == 'initial')
        action = deepcopy(execution['action'])
        action['id'] += '-close'
        sim.engine._enqueue(**action)
        before = deepcopy((sim.instance, sim.runtime))
        result, state = sim.engine._configure_candidate(sim.instance, sim.runtime,
            {'config': {'host_resources': host_configuration()['host_resources']}})
        pending = next(a for a in state['queue'] if a['id'] == action['id'])
        self.assertEqual(pending['profile_ref'], action['profile_ref'])
        self.assertEqual((sim.instance, sim.runtime), before)
        self.assertIn('host_capacity_ref', result)

    def test_different_effort_has_no_host_only_profile_replacement(self):
        sim = planned_sim()
        profile = deepcopy(sim.instance['role_profile_refs']['maintenance'][0])
        sim.engine._enqueue('maintenance', id='AC-close-profile', profile_ref=profile)
        effort = 'high' if sim.instance['config']['effort'] != 'high' else 'medium'
        before = deepcopy((sim.instance, sim.runtime))
        result, state = sim.engine._configure_candidate(sim.instance, sim.runtime, {'config': {
            'host_resources': host_configuration()['host_resources'], 'effort': effort}})
        pending = next(a for a in state['queue'] if a['id'] == 'AC-close-profile')
        self.assertEqual(pending['profile_ref'], profile)
        self.assertEqual(result['config']['effort'], effort)
        self.assertEqual((sim.instance, sim.runtime), before)

    def test_resource_change_preserves_queue_without_resource_wait(self):
        sim = planned_sim()
        i, r = deepcopy((sim.instance, sim.runtime))
        r['status'] = 'waiting'
        settings = deepcopy(i['config']['session_limits'])
        settings['work'][next(iter(settings['work']))] += 1
        before = deepcopy((i, r))
        result, state = sim.engine._configure_candidate(i, r, {'config': {'session_limits': settings}})
        expected = deepcopy(r['queue'])
        for action in expected:
            action.pop('model_selection', None)
        self.assertEqual(state['queue'], expected)
        self.assertEqual(state['status'], 'ready')
        self.assertEqual((i, r), before)
        self.assertEqual(result['config']['session_limits'], settings)

    def test_task_bound_pending_action_keeps_contract_profile_and_requests_preparation(self):
        sim = planned_sim()
        before = deepcopy((sim.instance, sim.runtime))
        action = next(a for a in sim.runtime['queue'] if a['role'] == 'research_work')
        tid = action['target']
        result, state = sim.engine._configure_candidate(sim.instance, sim.runtime,
            {'config': {'host_resources': host_configuration()['host_resources']}})
        self.assertEqual((sim.instance, sim.runtime), before)
        self.assertEqual(state['tasks'][tid]['profile_refs'], sim.runtime['tasks'][tid]['profile_refs'])
        self.assertEqual(state['queue'][0]['role'], 'research_preparation')
        self.assertEqual(set(state['queue'][0]['revision_targets']), {tid})
        pending = next(a for a in state['queue'] if a['id'] == action['id'])
        self.assertNotIn('model_selection', pending)
        self.assertIn('host_capacity_ref', result)
        sim.engine.instance, sim.engine.runtime = result, state
        sim.engine._save()
        self.assertEqual(sim.engine.store.load(sim.engine.head)[2]['queue'], state['queue'])

    def test_terminal_task_does_not_receive_host_repreparation(self):
        sim = planned_sim()
        i, r = deepcopy((sim.instance, sim.runtime))
        tid = next(a['target'] for a in r['queue'] if a['role'] == 'research_work')
        r['tasks'][tid]['status'] = 'completed'
        before = deepcopy((i, r))
        result, state = sim.engine._configure_candidate(i, r,
            {'config': {'host_resources': host_configuration()['host_resources']}})
        self.assertEqual((i, r), before)
        self.assertEqual([a['id'] for a in state['queue']], [a['id'] for a in r['queue']])
        self.assertEqual(state['tasks'][tid], r['tasks'][tid])
        self.assertIn('host_capacity_ref', result)

    def test_waiting_without_queued_action_does_not_become_ready(self):
        sim = planned_sim()
        i, r = deepcopy((sim.instance, sim.runtime))
        r['queue'] = []
        r['status'] = 'waiting'
        settings = deepcopy(i['config']['session_limits'])
        settings['work'][next(iter(settings['work']))] += 1
        before = deepcopy((i, r))
        result, state = sim.engine._configure_candidate(i, r, {'config': {'session_limits': settings}})
        self.assertEqual((i, r), before)
        self.assertEqual((state['status'], state['queue']), ('waiting', []))
        self.assertEqual(result['config']['session_limits'], settings)

    def test_same_host_settings_do_not_reprepare_again(self):
        sim = planned_sim()
        patch = {'host_resources': host_configuration()['host_resources']}
        first_i, first_r = sim.engine._configure_candidate(sim.instance, sim.runtime, {'config': patch})
        second_i, second_r = sim.engine._configure_candidate(first_i, first_r, {'config': {}})
        self.assertEqual(second_r['queue'], first_r['queue'])
        self.assertEqual(second_i['host_capacity_ref'], first_i['host_capacity_ref'])
