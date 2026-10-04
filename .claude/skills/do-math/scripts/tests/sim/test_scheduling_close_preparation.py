"""호출 준비의 폐기·권한·관찰 설정 분기를 실제 생산물과 저장으로 검사한다."""
from copy import deepcopy
from datetime import timedelta
import json
import unittest

from do_math.execution_profiles import seal_profile, profile_ref
from do_math.observations import OPERATORS, validate_task_rules
from support.engine_lifecycle import applied, clear_work, control_at_inbox_check
from support.scheduling_parallel import ready_work_sim
from support.sim import Sim, warm_template
from support.observation_inputs import observation_rule


def setUpModule():
    warm_template()
    ready_work_sim(1)


class PreparationBranchTests(unittest.TestCase):

    def test_a_new_grant_does_not_replace_a_revoked_pinned_authority(self):
        sim = Sim.activated()
        gid = sim.instance['lifecycle']['adoption']['research_grant_ids'][0]
        applied(sim, 'decision', config={'change': {'kind': 'revoke', 'grant_id': gid}})
        clear_work(sim)
        sim.engine._enqueue('maintenance', grant_id=gid, reason='고정 권한을 보존')
        action = deepcopy(sim.runtime['queue'][0])
        sim.engine._prepare_call(action)
        wait = deepcopy(sim.runtime['waiting_actions'][action['id']])
        applied(sim, 'decision', config={'change': {'kind': 'grant', 'grant': {
            'id': 'GR-different-maintenance', 'kind': 'local', 'roles': ['maintenance'],
            'reuse': 'reusable', 'expires_at': (sim.ports.clock.wall() + timedelta(days=1)).isoformat()}}})
        self.assertEqual(sim.runtime['waiting_actions'][action['id']], wait)
        self.assertEqual(wait['action']['grant_id'], gid)
        self.assertFalse(any(row['id'] == action['id'] for row in sim.runtime['queue']))
        before = deepcopy((sim.instance, sim.runtime))
        sim.engine._resume_action_authority_waits()
        self.assertEqual((sim.instance, sim.runtime), before)
        self.assertEqual(sim.model.calls, [])
        self.assertEqual(sim.engine.store.load()[2]['waiting_actions'][action['id']], wait)

    def test_ambiguous_grants_wait_until_one_public_revocation_leaves_one_authority(self):
        sim = Sim.activated()
        gid = sim.instance['lifecycle']['adoption']['research_grant_ids'][0]
        applied(sim, 'decision', config={'change': {'kind': 'revoke', 'grant_id': gid}})
        for identifier in ('GR-maintenance-one', 'GR-maintenance-two'):
            applied(sim, 'decision', config={'change': {'kind': 'grant', 'grant': {
                'id': identifier, 'kind': 'local', 'roles': ['maintenance'], 'reuse': 'reusable',
                'expires_at': (sim.ports.clock.wall() + timedelta(days=1)).isoformat()}}})
        clear_work(sim)
        sim.engine._enqueue('maintenance', reason='모호한 허가의 공개 해소')
        action = deepcopy(sim.runtime['queue'][0])
        sim.engine._prepare_call(action)
        wait = deepcopy(sim.runtime['waiting_actions'][action['id']])
        self.assertEqual(wait['reason'], 'ambiguous current grants')
        held = deepcopy((sim.instance, sim.runtime))
        sim.engine._resume_action_authority_waits()
        self.assertEqual((sim.instance, sim.runtime), held)
        applied(sim, 'decision', config={'change': {'kind': 'revoke', 'grant_id': 'GR-maintenance-two'}})
        self.assertNotIn(action['id'], sim.runtime.get('waiting_actions', {}))
        self.assertEqual(sum(row['id'] == action['id'] for row in sim.runtime['queue']), 1)
        resolutions = [row for row in sim.runtime['history']
                       if row.get('kind') == 'action_authority_resolved' and row['action_id'] == action['id']]
        self.assertEqual(len(resolutions), 1)
        self.assertEqual(resolutions[0]['authority']['grant_id'], 'GR-maintenance-one')
        self.assertEqual(resolutions[0]['previous'], wait)
        self.assertEqual(sim.model.calls, [])
        self.assertEqual(sim.engine.store.load()[2]['queue'], sim.runtime['queue'])

    def test_rule_bound_to_previous_execution_waits_for_research_preparation(self):
        sim = ready_work_sim(1)
        action = deepcopy(sim.runtime['queue'][0])
        rule = observation_rule('iteration_gte', OPERATORS['iteration_gte']['subject_kind'], '$execution')
        self.assertEqual(validate_task_rules([rule]), [rule])
        rule['subject']['id'] = 'EX-previous'
        sim.runtime.setdefault('task_observation_rules', {})[action['target']] = [rule]
        sim.engine._save()
        before = deepcopy(sim.runtime['executions'])
        self.assertIs(sim.engine._prepare_call(action), True)
        self.assertEqual(sim.runtime['executions'], before)
        wait = sim.runtime['waiting_actions'][action['id']]
        self.assertEqual((wait['kind'], wait['next_owner'], wait['reason']),
            ('observation_rules', 'research_preparation', 'task rule execution-bound subject must be $execution'))
        self.assertNotIn('observation_errors', wait)
        self.assertEqual([a['role'] for a in sim.runtime['queue']], ['research_preparation'])
        self.assertEqual(sim.engine.store.load(sim.engine.head)[2]['waiting_actions'][action['id']], wait)

    def test_public_request_during_input_discards_the_old_prepared_snapshot(self):
        sim = ready_work_sim(1)
        action = deepcopy(sim.runtime['queue'][0])
        before = set(sim.runtime['executions'])
        with control_at_inbox_check(sim, 1, 'request', config={'role': 'maintenance'}) as arrived:
            self.assertIs(sim.engine._prepare_call(action), True)
        self.assertIsNotNone(arrived['request'])
        self.assertEqual(sim.engine.control_result(arrived['request']['request_id'])['effect'], 'applied')
        added = set(sim.runtime['executions']) - before
        self.assertEqual(len(added), 1)
        eid, = added
        row = sim.runtime['executions'][eid]
        self.assertEqual(row['status'], 'ended')
        self.assertEqual(row['outcome'], 'cancelled')
        self.assertNotIn(eid, sim.engine._live_execution_ids)
        self.assertNotIn(eid, sim.engine._transport_bindings)
        self.assertIn(action['id'], [a['id'] for a in sim.runtime['queue']])
        self.assertEqual(sim.engine.store.load(sim.engine.head)[2]['executions'][eid], row)

    def test_ended_live_review_is_removed_with_exact_obsolete_reason(self):
        sim = Sim.activated()
        ended = next(e for e in sim.runtime['executions'].values() if e['status'] == 'ended')
        sim.engine._enqueue('operational_review', ended['id'], live=True)
        action = next(a for a in sim.runtime['queue'] if a.get('live'))
        before = deepcopy(sim.runtime['executions'])
        self.assertIs(sim.engine._prepare_call(action), True)
        self.assertEqual(sim.runtime['executions'], before)
        self.assertNotIn(action['id'], [a['id'] for a in sim.runtime['queue']])
        row = sim.runtime['history'][-1]
        self.assertEqual((row['kind'], row['action']['id'], row['reason']),
                         ('obsolete_action', action['id'], 'The live observation target has ended'))
        self.assertEqual(sim.engine.store.load(sim.engine.head)[2]['history'][-1], row)

    def test_revoked_maintenance_authority_is_parked_before_execution_creation(self):
        sim = Sim.activated()
        gid = sim.instance['lifecycle']['adoption']['research_grant_ids'][0]
        applied(sim, 'decision', config={'change': {'kind': 'revoke', 'grant_id': gid}})
        clear_work(sim)
        sim.engine._enqueue('maintenance', reason='권한 재검사')
        action = sim.runtime['queue'][0]
        before = deepcopy(sim.runtime['executions'])
        self.assertIs(sim.engine._prepare_call(action), False)
        self.assertEqual(sim.runtime['executions'], before)
        self.assertEqual(sim.runtime['queue'], [])
        self.assertEqual(sim.runtime['waiting_actions'][action['id']]['reason'],
                         'no current grant permits this action')
        self.assertEqual(sim.runtime['status'], 'waiting')
        self.assertEqual(sim.engine.store.load(sim.engine.head)[2]['waiting_actions'], sim.runtime['waiting_actions'])

    def test_sealed_profile_missing_one_required_duration_waits_for_profile_owner(self):
        sim = ready_work_sim(1)
        task_id = next(iter(sim.runtime['tasks']))
        clear_work(sim)
        sim.engine._enqueue('task_contract_review', task_id)
        action = sim.runtime['queue'][0]
        original = sim.engine._execution_profile(action)
        body = deepcopy(original)
        del body['observation']['settings']['tool_review_window_seconds']
        profile = seal_profile(body)
        ref = profile_ref(profile)
        sim.instance['execution_profiles'][profile['id']] = profile
        sim.instance['role_profile_refs']['task_contract_review'].append(ref)
        action['profile_ref'] = ref
        action['model_selection']['profile_ref'] = ref
        sim.engine._save()
        before = deepcopy(sim.runtime['executions'])
        self.assertIs(sim.engine._prepare_call(action), True)
        self.assertEqual(sim.runtime['executions'], before)
        wait = sim.runtime['waiting_actions'][action['id']]
        expected = [{'role': 'task_contract_review', 'profile_id': profile['id'],
            'field': 'tool_review_window_seconds',
            'reason': 'tool_review_window_seconds must be a positive millisecond-exact duration'}]
        self.assertEqual((wait['kind'], wait['next_owner']), ('observation_configuration', 'execution_profile'))
        self.assertEqual(wait['observation_errors'], expected)
        self.assertEqual(json.loads(wait['reason']), expected)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[2]['waiting_actions'][action['id']], wait)

    def test_control_after_input_packing_discards_only_the_unpublished_attempt(self):
        from pathlib import Path
        from do_math.context_store import prepare_role_input
        from support.scheduling_return_matrix import AfterReturn
        sim = ready_work_sim(1)
        action = deepcopy(sim.runtime['queue'][0])
        before = set(sim.runtime['executions'])
        requests = []
        def arrive():
            requests.append(sim.control('request', config={'role': 'maintenance'},
                                        text='control after packing, before admission'))
        with AfterReturn(prepare_role_input, arrive) as packed:
            result = sim.engine._prepare_call(action)
        self.assertIs(result, True)
        self.assertEqual(len(packed.values), 1)
        self.assertEqual(len(requests), 1)
        self.assertEqual(sim.engine.control_result(requests[0]['request_id'])['effect'], 'applied')
        added = set(sim.runtime['executions']) - before
        self.assertEqual(len(added), 1)
        eid, = added
        row = sim.runtime['executions'][eid]
        self.assertEqual((row['status'], row['outcome']), ('ended', 'cancelled'))
        self.assertNotIn('input_bundle', row)
        self.assertNotIn(eid, sim.engine._transport_bindings)
        self.assertNotIn(eid, sim.engine._live_execution_ids)
        self.assertFalse((Path(sim.instance['workspace']) / 'runs' / eid).exists())
        continuation, = [a for a in sim.runtime['queue'] if a['id'] == action['id']]
        self.assertEqual(continuation['continuation_of'], eid)
        self.assertEqual(continuation['owner_activity_id'], row['owner_activity_id'])
        self.assertEqual(sim.model.calls, [])
        self.assertEqual(sim.engine.store.load(sim.engine.head)[2]['executions'][eid], row)

    def test_revoked_targeted_maintenance_parks_the_real_task_without_a_call(self):
        sim = ready_work_sim(1)
        target = next(iter(sim.runtime['tasks']))
        request = sim.control('request', config={'role': 'maintenance', 'target': target})
        sim.engine.process_controls()
        self.assertEqual(sim.engine.control_result(request['request_id'])['effect'], 'applied')
        action = deepcopy(next(a for a in sim.runtime['queue']
                               if a.get('requested_by') == request['request_id']))
        for gid in list(sim.instance['lifecycle']['adoption']['research_grant_ids']):
            applied(sim, 'decision', config={'change': {'kind': 'revoke', 'grant_id': gid}})
        before = deepcopy(sim.runtime['executions'])
        sim.engine._prepare_call(action)
        self.assertEqual(sim.runtime['executions'], before)
        self.assertEqual(sim.runtime['tasks'][target]['status'], 'waiting')
        self.assertNotIn(action['id'], [a['id'] for a in sim.runtime['queue']])
        wait = sim.runtime['waiting_actions'][action['id']]
        self.assertEqual(wait['reason'], 'no current grant permits this action')
        self.assertEqual(wait['action']['target'], target)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[2]['waiting_actions'][action['id']], wait)
        self.assertEqual(sim.model.calls, [])
