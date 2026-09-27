"""Goal audit and final goal assurance: audit slots and their seals, the mapping of audit results, and what a final goal record may rely on. No model calls."""
from copy import deepcopy
from pathlib import Path
import sys
import unittest
import uuid
from unittest.mock import create_autospec, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math.repository import exact_content_hash
from do_math.repository import ResearchRepository
from research_fixtures import bare_engine
from do_math import governance as gov
from do_math.session_slots import SessionSlots
from record_fixtures import audited_governance, domain_governance


class GoalAuditSlotTests(unittest.TestCase):
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
        e.store.git_dir = 'git-' + uuid.uuid4().hex
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
        from engine_fixtures import goal_audit_host, governance_host
        e, action, output = goal_audit_host()
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


class GoalAssuranceTests(unittest.TestCase):
    def test_nonformal_task_does_not_establish_final_goal_assurance(self):
        from do_math.academic import apply_goal_assurance
        i=domain_governance()
        with self.assertRaises(ValueError):apply_goal_assurance(i,decision="unsupported_assurance",basis="B",judgments=[{"decision":"satisfied"}])

    def test_final_goal_record_cannot_rely_on_unresolved_formal_references(self):
        from do_math.academic import apply_goal_assurance
        i=domain_governance()
        with self.assertRaises(ValueError):apply_goal_assurance(i,decision="mathematically_solved",basis="B",
            judgments=[{"decision":"satisfied","current":True,"formal_result_refs":["MISSING"]}])

    def test_goal_audit_maps_actual_results_and_rejects_missing_or_stale_input(self):
        import jsonschema
        i, rt = audited_governance()
        basis = gov.additional_audit_input(i, rt)
        rt['executions']['AUDIT'] = {'role': 'goal_audit', 'additional_audit_input': basis}
        row = {'audit_ref': 'AU', 'assessor': 'goal_audit', 'verdict': 'partial', 'reason': 'Only partial',
               'input_hashes': {'CH1': exact_content_hash(i['governance']['CH1'])}}
        jsonschema.Draft202012Validator(gov.additional_audit_schema(i)).validate([row])
        mapped = gov.evaluate_goal_audits(i, rt, 'AUDIT', [row])
        self.assertEqual(mapped[0]['decision'], 'not_satisfied')
        with self.assertRaises(ValueError): gov.validate_goal_additional_audits(i, [{'execution_id': 'AUDIT', 'additional_audits': mapped}])
        with self.assertRaises(ValueError): gov.evaluate_goal_audits(i, rt, 'AUDIT', [])
        row['verdict'] = 'pass'
        mapped = gov.evaluate_goal_audits(i, rt, 'AUDIT', [row])
        gov.validate_goal_additional_audits(i, [{'execution_id': 'AUDIT', 'additional_audits': mapped}])
        i['governance']['CH1']['content']['goal'] += ' changed'
        with self.assertRaises(ValueError): gov.evaluate_goal_audits(i, rt, 'AUDIT', [row])

    def test_audit_assessor_must_resolve_to_actual_execution_not_producer_claim(self):
        i, rt = audited_governance()
        rt['executions']['AUDIT'] = {'role': 'goal_audit', 'additional_audit_input': gov.additional_audit_input(i, rt)}
        with self.assertRaises(ValueError): gov.evaluate_goal_audits(i, rt, 'AUDIT', [{
            'audit_ref': 'AU', 'verdict': 'pass', 'assessor': 'someone-else', 'reason': 'Claimed authority',
            'input_hashes': {'CH1': exact_content_hash(i['governance']['CH1'])}}])

    def test_goal_assurance_cannot_omit_active_additional_audit(self):
        from unittest.mock import patch
        from do_math.academic import apply_goal_assurance
        i, rt = audited_governance()
        judgment = {'id': 'J', 'execution_id': 'AUDIT', 'slot': 0, 'basis': 'B', 'required': 1,
                    'decision': 'satisfied', 'scope_complete': True, 'current': True, 'formal_result_refs': ['FR']}
        i['goal_judgments'] = [judgment]; i['formal_results'] = {'FR': {'id': 'FR'}}
        with patch('do_math.knowledge_records.formal_usable', return_value=True):
            with self.assertRaises(ValueError): apply_goal_assurance(i, decision='mathematically_solved', basis='B', judgments=[judgment])


if __name__ == '__main__':
    unittest.main()
