"""Behavioral boundaries of the September 23 repair plan; no model calls."""
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
import sys
import unittest
from unittest.mock import create_autospec, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math.repository import exact_content_hash
from do_math.engine import DEFAULT_CONFIG
from do_math.repository import ResearchRepository
from research_fixtures import bare_engine
from do_math import execution_profiles, reporting
from do_math.session_slots import SessionSlots


class GoalAuditFlowRepairTests(unittest.TestCase):
    def host(self):
        e = bare_engine({'id': 'IN-1', 'config': {'goal_auditors': 2}, 'goal_judgments': []},
                        {'executions': {}, 'queue': [], 'waiting_actions': {}, 'history': [],
                         'events': [], 'pending_events': [], 'tasks': {}, 'activities': {}, 'reservations': {}})
        e.runtime['last_observed_utc'] = e._lifecycle_now().isoformat()
        e._goal_basis_key = create_autospec(e._goal_basis_key, return_value='basis')
        return e

    def seal(self, e, slot=0, **changes):
        action = {'id': 'AC-original', 'role': 'goal_audit', 'basis': 'basis', 'required': 2, 'slot': slot}
        e.runtime['executions']['EX-original'] = {'id': 'EX-original', 'role': 'goal_audit',
            'action': action, 'status': 'ended', 'outcome': 'output_accepted'}
        j = {'id': 'GJ-one', 'basis': 'basis', 'required': 2, 'slot': slot,
             'execution_id': 'EX-original', 'current': True, **changes}
        e.instance['goal_judgments'].append(j)
        return action, j

    def test_only_missing_slots_are_enqueued_and_consumed_event_is_not_repended(self):
        e = self.host()
        _, j = self.seal(e)
        first = e._ensure_goal_audit_requests('basis', 'EX-plan')
        self.assertEqual([s['state'] for s in first['slots']], ['sealed', 'queued_new'])
        queued = deepcopy(e.runtime['queue'])
        second = e._ensure_goal_audit_requests('basis', 'EX-plan2')
        self.assertEqual([s['state'] for s in second['slots']], ['sealed', 'queued'])
        self.assertEqual(e.runtime['queue'], queued)
        event = e._record_goal_audit_followup('basis', [j])
        e.runtime['pending_events'].remove(event)
        self.assertEqual(e._record_goal_audit_followup('basis', [j]), event)
        self.assertEqual(e.runtime['pending_events'], [])
        j['current'] = False
        self.assertEqual(e._ensure_goal_audit_requests('basis', 'EX-plan3')['slots'][0]['state'], 'sealed_unusable')

    def test_owned_slot_wait_is_preserved(self):
        e = self.host()
        actions = [{'id': f'AC-{s}', 'role': 'goal_audit', 'basis': 'basis', 'slot': s, 'required': 2} for s in range(2)]
        e.runtime['executions']['EX-live'] = {'id': 'EX-live', 'status': 'running', 'action': actions[0]}
        e.runtime['waiting_actions']['AC-1'] = {'action': actions[1], 'kind': 'submission_failure', 'next_owner': 'engine'}
        self.assertEqual([r['state'] for r in e._ensure_goal_audit_requests('basis', 'EX-plan')['slots']], ['running', 'waiting'])
        self.assertEqual(e.runtime['queue'], [])

    def test_recovery_confirms_termination_before_using_original_seal_without_recollection(self):
        import hashlib
        from do_math.repository import canonical_json
        from do_math.contracts import schema_reference
        e = self.host()
        action, _ = self.seal(e)
        e.head = 'fixed'
        e.instance['workspace'] = str(Path('.').resolve())
        ex = e.runtime['executions']['EX-original']
        ex.update(status='stopping', stop_phase='terminating', actor_kind='ai',
            result_ref='original-result', input_bundle='original-input',
            capacity={'local_termination': 'confirmed', 'process': {'job_name': 'fixture-job'}}, submission_intent={})
        artifacts, refs = {}, []
        output, extensions = {'summary': 'original'}, {}
        schema_ref = schema_reference({'type': 'object'})
        ex['submission_intent']['schema_ref'] = schema_ref
        check = {'passed': True, 'capture_eligible': True, 'issues': [],
                 'mode': 'receiver', 'execution_id': ex['id'], 'schema_ref': schema_ref,
                 'input_hashes': {'output': exact_content_hash(output), 'extensions': exact_content_hash(extensions)}}
        for name, value in (('output', output), ('extensions', extensions), ('check', check)):
            if name == 'check':
                value['id'] = 'MC-' + exact_content_hash(value)[:24]
            raw = canonical_json(value)
            digest = hashlib.sha256(raw).hexdigest()
            artifacts[name] = raw
            refs.append({'path': name, 'bytes': len(raw), 'sha256': digest})
            ex['submission_intent'].update({name + '_ref': name, name + '_sha256': digest})
        ex['submission_receipt'] = {'state': 'accepted', 'execution_id': ex['id'],
                                    'payload': {'submission_check': {'artifacts': refs}}}
        e.runtime['integrations'] = {'IB-one': {'execution_id': ex['id'], 'members': ['output']}}
        e.store = create_autospec(ResearchRepository, instance=True)
        e.store.read.side_effect = lambda path, snapshot: artifacts[path]
        e.store.git_dir = "fixture-git"
        e._session_slots = create_autospec(e._session_slots, return_value=SessionSlots(e.runtime, e.instance))
        with patch.object(e, '_save'), patch('do_math.windows_job.named_job_empty', return_value=True), \
                patch('do_math.engine.collect_outputs', side_effect=AssertionError('must retain original files')):
            e._recover_disappeared()
        self.assertEqual(ex['status'], 'stopping')
        self.assertEqual(e.runtime['waiting_actions'], {})
        from research_fixtures import dispatched_launch
        ex['launch_ticket'] = dispatched_launch(ex['id'], {'sha256':'a'*64, 'actor_kind':'ai', 'role':'goal_audit'})
        with patch.object(e, '_save'), patch('do_math.windows_job.owner_ended', return_value=True), \
                patch('do_math.windows_job.named_job_empty', return_value=True), \
                patch('do_math.engine.collect_outputs', side_effect=AssertionError('must retain original files')):
            e._recover_disappeared()
        self.assertEqual(ex['status'], 'ended')
        self.assertEqual(ex['result_ref'], 'original-result')
        self.assertEqual(ex['input_bundle'], 'original-input')
        self.assertEqual(e.runtime['waiting_actions'][action['id']]['kind'], 'submission_publication')

    def test_original_publication_and_reservations_are_protected_from_duplicate_cleanup(self):
        e = self.host()
        action, j = self.seal(e)
        e.runtime['executions']['EX-original']['outcome'] = 'execution_incomplete'
        duplicate = {**action, 'id': 'AC-duplicate'}
        held = {**action, 'id': 'AC-held'}
        e.runtime['executions']['EX-held'] = {'id': 'EX-held', 'action': held, 'status': 'ended'}
        e.runtime['reservations']['RS-held'] = {'owner_id': 'EX-held', 'state': 'held'}
        e.runtime['queue'] = [action, duplicate, held]
        e.runtime['waiting_actions'] = {a['id']: {'action': a, 'kind': 'submission_publication',
            'execution_id': 'EX-original' if a is action else 'EX-duplicate'} for a in (action, duplicate)}
        self.assertTrue(e._retire_sealed_goal_audit_requests())
        self.assertEqual([a['id'] for a in e.runtime['queue']], ['AC-original', 'AC-held'])
        self.assertEqual(list(e.runtime['waiting_actions']), ['AC-original'])
        self.assertFalse(e._retire_sealed_goal_audit_requests())
        self.assertIsNone(e._obsolete_action_reason(action, execution_id='EX-original'))
        self.assertIn('sealed', e._obsolete_action_reason(action, execution_id='EX-other'))

    def test_committed_seal_requires_original_execution_and_output_receipt(self):
        e = self.host()
        _, j = self.seal(e)
        with self.assertRaisesRegex(ValueError, 'receipt'):
            e._committed_goal_audit('EX-original')
        e.runtime['integrations'] = {'IB-one': {'execution_id': 'EX-original', 'members': ['output']}}
        self.assertEqual(e._committed_goal_audit('EX-original'), j)
        e.runtime['executions']['EX-original']['action']['slot'] = 1
        with self.assertRaises(ValueError):
            e._committed_goal_audit('EX-original')

    def test_duplicate_retirement_preserves_evidence_and_other_activity_obligations(self):
        from do_math.activities import open_activity, assign_execution
        for other_obligation in (False, True):
            with self.subTest(other_obligation=other_obligation):
                e = self.host()
                original, judgment = self.seal(e, current=False)
                action = {**original, 'id': 'AC-duplicate', 'owner_activity_id': 'AT-duplicate'}
                activity = open_activity(e.runtime, activity_id='AT-duplicate', activity_kind='goal_audit',
                    owner_ref='IN-1', input_refs=[], opened_at='2026-09-23T00:00:00Z')
                assign_execution(e.runtime, activity['id'], {'id': 'EX-duplicate', 'role': 'goal_audit',
                    'owner_activity_id': activity['id'], 'action': action, 'status': 'ended',
                    'outcome': 'execution_incomplete'})
                activity.update(result_refs=['preserved-result'], unresolved=[{'action_id': action['id'], 'reason': 'failed'}])
                if other_obligation:
                    activity['followups'] = [{'reason': 'another outstanding obligation'}]
                before = deepcopy(activity)
                e.runtime['queue'] = [action]
                e._retire_sealed_goal_audit_requests()
                self.assertEqual(activity['result_refs'], before['result_refs'])
                self.assertEqual(e.runtime['executions']['EX-duplicate']['outcome'], 'execution_incomplete')
                if other_obligation:
                    self.assertEqual(activity, before)
                else:
                    self.assertEqual(activity['status'], 'finished')
                    self.assertIn(before['unresolved'][0], activity['unresolved'])
                    self.assertTrue(any(row.get('judgment_id') == judgment['id'] for row in activity['unresolved']))
    def test_last_slot_emits_one_event_and_invalid_slot_changes_nothing(self):
        from test_governance_engine import CentralGovernanceTests
        e, action, output = CentralGovernanceTests().audit_host()
        action['required'] = 2
        e.runtime['executions']['AUDITOR']['action'] = deepcopy(action)
        first = e._apply_governance_goal_audit(action, output, 'AUDITOR')
        self.assertEqual(e.runtime['events'], [])
        before = deepcopy(e.instance)
        for slot in (True, -1, 2):
            with self.assertRaises(ValueError):
                e._apply_governance_goal_audit({**action, 'slot': slot}, output, 'AUDITOR')
            self.assertEqual(e.instance, before)
        e.runtime['executions']['AUDITOR2'] = {**deepcopy(e.runtime['executions']['AUDITOR']), 'id': 'AUDITOR2'}
        second = e._apply_governance_goal_audit({**action, 'slot': 1}, output, 'AUDITOR2')
        self.assertEqual(len(e.instance['goal_judgments']), 2)
        self.assertEqual(e.runtime['events'][0]['judgment_ids'], sorted([first['id'], second['id']]))
        self.assertEqual(len(e.runtime['pending_events']), 1)


class DispatchResourceRepairTests(unittest.TestCase):
    def state(self, **changes):
        config = {**deepcopy(DEFAULT_CONFIG), **changes}
        instance = {**execution_profiles.build_profiles(config), 'config': config}
        runtime = {'executions': {}, 'reservations': {}, 'provider_waits': {}}
        profile = next(p for p in instance['execution_profiles'].values() if p['role'] == 'research_work')
        return instance, runtime, profile


    def test_zero_capacity_and_provider_probe_are_distinct_and_read_only(self):
        config = deepcopy(DEFAULT_CONFIG)
        for model in config['session_limits']['work']:
            config['session_limits']['work'][model] = 0
        instance, runtime, profile = self.state(**config)
        slots = SessionSlots(runtime, instance)
        wait = slots.admission_check(profile)['wait']
        self.assertEqual((wait['kind'], wait['next_owner']), ('capacity', 'user'))
        self.assertNotIn('retry_at', wait)
        provider = profile['ai']['provider']
        runtime['provider_waits']['PW-' + provider] = {'provider': provider, 'state': 'waiting',
            'retry_at': 100, 'probe_owner': None, 'probe_started_at': None}
        before = deepcopy(runtime)
        self.assertEqual(slots.admission_check(profile, current_time=90)['wait']['kind'], 'provider_limit')
        self.assertEqual(slots.admission_check(profile, current_time=110)['wait']['kind'], 'capacity')
        self.assertEqual(runtime, before)

    def test_non_task_wait_projection_is_detached_and_printable(self):
        runtime = {'executions': {}, 'queue': [{'id': 'AC-prep', 'role': 'research_preparation',
            'dispatch_wait': {'kind': 'capacity', 'constraint_id': 'BC-old', 'next_owner': 'user'}}]}
        rows = reporting.dispatch_waits(runtime)
        text = '\n'.join(reporting.render_dispatch_waits({'tasks': [], 'dispatch_waits': rows}))
        self.assertIn('AC-prep', text)
        self.assertIn('capacity', text)
        self.assertIn('BC-old', text)
        rows[0]['wait']['kind'] = 'changed'
        self.assertEqual(runtime['queue'][0]['dispatch_wait']['kind'], 'capacity')
        runtime['executions']['EX-live'] = {'status': 'running', 'action': {'id': 'AC-prep'}}
        self.assertEqual(reporting.dispatch_waits(runtime), [])

    def test_configure_wakes_only_changed_resource_waits_and_keeps_pinned_profile(self):
        from test_governance_engine import CentralGovernanceTests
        e, _, _ = CentralGovernanceTests().host()
        e.instance['workspace'] = str(Path('.').resolve())
        e.instance['config']['session_limits']['work'] = {m: 0 for m in e.instance['config']['tier_models'].values()}
        e.instance.update(execution_profiles.build_profiles(e.instance['config']))
        e.runtime.update(status='waiting', queue=[{'id': 'AC-wait', 'role': 'goal_audit',
            'profile_ref': deepcopy(e.instance['role_profile_refs']['goal_audit'][0]),
            'dispatch_wait': {'kind': 'capacity', 'next_owner': 'user'}}])
        original = deepcopy(e.runtime['queue'][0]['profile_ref'])
        request = {'origin': 'user', 'config': {'session_limits': deepcopy(DEFAULT_CONFIG['session_limits'])}}
        _, state = e._configure_candidate(e.instance, e.runtime, request)
        self.assertEqual(state['status'], 'ready')
        self.assertNotIn('dispatch_wait', state['queue'][0])
        self.assertEqual(state['queue'][0]['profile_ref'], original)
        self.assertEqual(e.runtime['status'], 'waiting')
        _, same = e._configure_candidate(e.instance, e.runtime, {'origin': 'user', 'config': {}})
        self.assertEqual(same['status'], 'waiting')
        e.runtime['status'] = 'capacity_waiting'
        _, same = e._configure_candidate(e.instance, e.runtime, {'origin': 'user', 'config': {}})
        self.assertEqual(same['status'], 'capacity_waiting')
        e.runtime['status'] = 'paused'
        _, paused = e._configure_candidate(e.instance, e.runtime, request)
        self.assertEqual(paused['status'], 'paused')


class ReadinessCopyRepairTests(unittest.TestCase):
    def test_historical_judgment_cannot_override_changed_governance_or_sources(self):
        from test_redesign_GOVERNANCE import DomainGovernanceTests
        from do_math import planning, task_scope
        instance = DomainGovernanceTests().initial()
        instance['sources'] = [{'name': 'source', 'path': 'source.txt', 'sha256': 'a'*64}]
        instance['knowledge'] = {'KN-one': {'id': 'KN-one', 'task_id': 'TK-one'}}
        judgment = {'id': 'GJ-one', 'decision': 'satisfied', 'scope_complete': True, 'current': True,
            'dependencies': ['KN-one'], 'record_basis': [], **planning.governance_revisions(instance),
            'source_basis': deepcopy(instance['sources'])}
        instance['goal_judgments'] = [judgment]
        def judge():
            return task_scope.designated_judgment({'id': 'TK-one'}, {'judges': ['goal_audit']},
                                                  {'evidence_refs': ['GJ-one']}, instance, {})
        with patch('do_math.knowledge_records.usable_links', return_value=[{'assessment_id': 'AS-one'}]):
            self.assertEqual(judge(), 'GJ-one')
            instance['sources'][0]['sha256'] = 'b'*64
            self.assertIsNone(judge())
            instance['sources'][0]['sha256'] = 'a'*64
            judgment['goal_revision'] = 'old-edition'
            self.assertIsNone(judge())

    def test_borrowed_inputs_and_copied_results_match_prior_evaluation(self):
        from test_redesign_TASKS import approved_fixture
        from do_math.planning import task_ready
        task, instance, runtime = approved_fixture()
        for scenario in ('ready', 'waiting', 'missing', 'invalid'):
            with self.subTest(scenario=scenario):
                value, state, working = deepcopy((task, instance, runtime))
                working['tasks'][value['id']] = value
                if scenario == 'waiting':
                    value['waiting'] = {'kind': 'external_event', 'next_owner': 'user', 'reason': 'wait'}
                elif scenario == 'missing':
                    value['inputs'].append('SO-missing')
                elif scenario == 'invalid':
                    value['occurrence_condition'] = {'op': 'unknown'}
                before = deepcopy((value, state, working))
                old = task_ready(deepcopy(value), deepcopy(state), deepcopy(working))
                result = deepcopy(task_ready(value, state, working))
                self.assertEqual(result, old)
                self.assertEqual((value, state, working), before)
                if scenario == 'waiting':
                    self.assertIn(value['waiting'], result['waits'])
                    result['waits'][0]['reason'] = 'changed by result consumer'
                    self.assertEqual(value['waiting']['reason'], 'wait')


if __name__ == '__main__':
    unittest.main()
