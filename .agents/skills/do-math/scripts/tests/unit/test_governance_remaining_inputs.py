"""앞선 검사와 구분되는 원천·위임·답변의 추가 입력 축."""
from copy import deepcopy
import unittest

from do_math import delegations, governance as gov
from support.governance_cases import delegated_sim, question_sim, question_bundle, records_sim, proposed_record


class GovernanceRemainingInputTests(unittest.TestCase):
    def test_missing_delegation_key_is_rejected_without_changing_the_roots(self):
        """선택 키 생략은 shape 검사를 통과하지만 위임 결정의 필수 기록은 도메인이 거부한다."""
        sim = records_sim()
        change = {'kind': 'delegation'}
        before = deepcopy((sim.instance, sim.runtime, change))
        with self.assertRaisesRegex(ValueError, '^delegation decision requires a delegation record$'):
            gov.apply_decision(sim.instance, sim.runtime, change, source_ref='GS-close', clock=sim.clock)
        self.assertEqual((sim.instance, sim.runtime, change), before)
        self.assertEqual(sim.engine.store.load()[1:3], (sim.instance, sim.runtime))

    def test_approval_of_blocking_import_preserves_user_wait(self):
        sim = question_sim()
        bundle = question_bundle(sim)
        before = deepcopy((sim.instance, sim.runtime))
        draft = gov.import_approval_draft(sim.instance, sim.runtime, bundle['id'],
            owner_handlers=sim.engine.governance_owner_handlers(), clock=sim.clock)
        i, r, receipt = gov.apply_import_control(sim.instance, sim.runtime,
            {'id': 'DC-close-blocked-approval', 'action': 'decision', 'origin': 'user',
             'text': '해석은 승인하지만 질문의 답은 아직 없다.', 'config': draft},
            owner_handlers=sim.engine.governance_owner_handlers(), clock=sim.clock)
        self.assertEqual(receipt['status'], 'awaiting_decision')
        self.assertEqual(r['waiting_actions'], sim.runtime['waiting_actions'])
        self.assertEqual((sim.instance, sim.runtime), before)
        self.assertEqual(i['governance'], sim.instance['governance'])
        sim.engine.instance, sim.engine.runtime = i, r
        sim.engine._save()
        self.assertEqual(sim.engine.store.load(sim.engine.head)[2]['intent_imports'][bundle['id']]['application'], receipt)

    def test_nonobject_delegation_is_rejected(self):
        sim = delegated_sim()
        before = deepcopy((sim.instance, sim.runtime))
        with self.assertRaisesRegex(ValueError, '^delegation record required$'):
            delegations.validate_delegation([], now_iso=sim.clock.now())
        self.assertEqual((sim.instance, sim.runtime), before)

    def test_previously_included_instance_target_must_still_resolve(self):
        sim = delegated_sim()
        i, r = deepcopy((sim.instance, sim.runtime))
        app = next(row for row in r['delegation_applications'].values() if row['delegation_id'] == 'DG-close')
        i['id'] = 'RI-other'
        before = deepcopy((i, r))
        with self.assertRaisesRegex(ValueError, '^case target does not resolve$'):
            delegations.prepare_application(i, r, 'DG-close', app['basis']['case'], now_iso=sim.clock.now())
        self.assertEqual((i, r), before)

    def test_required_audit_record_must_resolve_before_delivery(self):
        sim = records_sim()
        i = deepcopy(sim.instance)
        ref = i['governance']['AU-close']['content']['required_inputs'][0]
        del i['governance'][ref]
        before = deepcopy(i)
        with self.assertRaisesRegex(ValueError, '^additional audit required input is unavailable: '):
            gov.additional_audit_input(i, sim.runtime)
        self.assertEqual(i, before)

    def test_domain_owner_rejects_nonuser_actor(self):
        sim = records_sim()
        change = {'kind': 'policy', 'record': proposed_record(sim.instance, 'PO-close')}
        before = deepcopy((sim.instance, sim.runtime, change))
        with self.assertRaisesRegex(ValueError, '^preserved user decision required$'):
            gov._apply_domain_decision(sim.instance, sim.runtime, change, 'GS-close', 'ai', None, clock=sim.clock)
        self.assertEqual((sim.instance, sim.runtime, change), before)

    def test_domain_owner_rejects_record_of_another_kind(self):
        sim = records_sim()
        change = {'kind': 'policy', 'record': proposed_record(sim.instance, 'CX-close')}
        before = deepcopy((sim.instance, sim.runtime, change))
        with self.assertRaisesRegex(ValueError, '^record owner differs from decision kind$'):
            gov.apply_decision(sim.instance, sim.runtime, change, source_ref='GS-close', clock=sim.clock)
        self.assertEqual((sim.instance, sim.runtime, change), before)

    def test_empty_grant_interval_is_not_an_expired_grant(self):
        sim = delegated_sim()
        change = deepcopy(sim.instance['decisions']['DC-close-original']['change'])
        change['decision_id'] = 'DC-close-interval'
        change['grant']['id'] = 'GR-close-interval'
        change['grant']['expires_at'] = '2099-01-01T00:00:00Z'
        change['grant']['valid_from'] = '2099-01-01T00:00:00Z'
        before = deepcopy((sim.instance, sim.runtime, change))
        with self.assertRaisesRegex(ValueError, '^grant has an empty effective interval$'):
            gov.apply_decision(sim.instance, sim.runtime, change, source_ref='GS-close-delegation', clock=sim.clock)
        self.assertEqual((sim.instance, sim.runtime, change), before)

    def test_answer_must_name_a_question(self):
        sim = question_sim()
        bundle = question_bundle(sim)
        change = {'kind': 'question_answer', 'text': '자연수다.', 'target_ids': [sim.instance['id']], 'resolves_questions': []}
        before = deepcopy((sim.instance, sim.runtime, change))
        with self.assertRaisesRegex(ValueError, '^a question answer must identify its questions$'):
            gov.apply_decision(sim.instance, sim.runtime, change, source_ref=bundle['source']['id'], clock=sim.clock)
        self.assertEqual((sim.instance, sim.runtime, change), before)

    def test_answer_cannot_name_missing_question(self):
        sim = question_sim()
        bundle = question_bundle(sim)
        change = {'kind': 'question_answer', 'text': '자연수다.', 'target_ids': [sim.instance['id']], 'resolves_questions': ['missing']}
        before = deepcopy((sim.instance, sim.runtime, change))
        with self.assertRaisesRegex(ValueError, '^unknown question: missing$'):
            gov.apply_decision(sim.instance, sim.runtime, change, source_ref=bundle['source']['id'], clock=sim.clock)
        self.assertEqual((sim.instance, sim.runtime, change), before)

    def test_answer_cannot_affect_unrelated_target(self):
        sim = question_sim()
        bundle = question_bundle(sim)
        row = next(q for q in sim.runtime['question_links'] if q.get('source_id') == bundle['id'])
        change = {'kind': 'question_answer', 'text': '자연수다.', 'target_ids': ['other'], 'resolves_questions': [row['id']]}
        before = deepcopy((sim.instance, sim.runtime, change))
        with self.assertRaisesRegex(ValueError, '^answer names unrelated or already resolved targets$'):
            gov.apply_decision(sim.instance, sim.runtime, change, source_ref=bundle['source']['id'], clock=sim.clock)
        self.assertEqual((sim.instance, sim.runtime, change), before)

    def test_grant_answer_closes_exact_instance_question(self):
        sim = question_sim()
        bundle = question_bundle(sim)
        row = next(q for q in sim.runtime['question_links'] if q.get('source_id') == bundle['id'])
        change = {'kind': 'grant', 'decision_id': 'DC-close-answer', 'grant': {
            'id': 'GR-close-answer', 'kind': 'local', 'roles': ['maintenance'], 'reuse': 'reusable'},
            'resolves_questions': [row['id']]}
        before = deepcopy((sim.instance, sim.runtime))
        i, r, event = gov.apply_decision(sim.instance, sim.runtime, change, source_ref=bundle['source']['id'], clock=sim.clock)
        resolved = next(q for q in r['question_links'] if q['id'] == row['id'])
        self.assertEqual((resolved['status'], resolved['resolution_ref'], resolved['unresolved_target_ids']),
                         ('resolved', 'DC-close-answer', []))
        self.assertEqual(resolved['resolution_history'], [{'kind': 'user_decision',
            'resolution_ref': 'DC-close-answer', 'affected_ids': [sim.instance['id']]}])
        self.assertEqual(event['grant_id'], 'GR-close-answer')
        self.assertEqual((sim.instance, sim.runtime), before)
        sim.engine.instance, sim.engine.runtime = i, r
        sim.engine._save()
        self.assertEqual(sim.engine.store.load(sim.engine.head)[2]['question_links'], r['question_links'])

    def test_knowledge_import_rejects_mismatched_candidate_identity(self):
        sim = records_sim()
        unit = {'owner_ref': 'KN-close', 'payload': {'record': {'id': 'KN-other'}}}
        before = deepcopy((sim.instance, sim.runtime, unit))
        with self.assertRaisesRegex(ValueError, '^knowledge import must name its exact candidate ID$'):
            gov._validate_knowledge_import(sim.instance, sim.runtime, unit, clock=sim.clock)
        self.assertEqual((sim.instance, sim.runtime, unit), before)

    def test_empty_knowledge_payload_is_nonapplying(self):
        sim = question_sim()
        unit = deepcopy(question_bundle(sim)['output']['import_units'][0])
        self.assertEqual(unit['payload'], {})
        before = deepcopy((sim.instance, sim.runtime, unit))
        self.assertIsNone(gov._validate_knowledge_import(sim.instance, sim.runtime, unit, clock=sim.clock))
        self.assertEqual((sim.instance, sim.runtime, unit), before)
