"""실제 생산·저장 상태에서 반환값과 부작용을 독립적으로 확인한다."""
from copy import deepcopy
import unittest

from do_math import delegations, governance as gov, input_basis
from do_math.canonical import exact_content_hash
from support.governance_cases import auditor_sim, audit_output, delegated_sim, planned_sim
from support.governance_sim import checked_sim, checked_bundle


class GovernanceEffectContractTests(unittest.TestCase):
    def test_approved_grant_interval_includes_start_and_excludes_expiry(self):
        from datetime import timedelta
        sim = delegated_sim()
        start = sim.clock.wall() + timedelta(seconds=1)
        end = start + timedelta(seconds=1)
        change = {'kind': 'grant', 'decision_id': 'DC-close-interval-boundary', 'grant': {
            'id': 'GR-close-interval-boundary', 'kind': 'local', 'roles': ['maintenance'],
            'reuse': 'reusable', 'valid_from': start.isoformat(), 'expires_at': end.isoformat()}}
        sim.engine.instance, sim.engine.runtime, _ = gov.apply_decision(
            sim.instance, sim.runtime, change, source_ref='GS-close-delegation', clock=sim.clock)
        sim.engine._save()
        grant = sim.instance['grants']['GR-close-interval-boundary']
        action = {'id': 'AC-close-boundary', 'role': 'maintenance'}
        before = deepcopy((sim.instance, sim.runtime))
        for at, reason in ((start - timedelta(microseconds=1), 'grant is not effective yet'),
                           (start, None), (end - timedelta(microseconds=1), None), (end, 'grant expired')):
            with self.subTest(at=at):
                self.assertEqual(gov.grant_scope_reason(grant, action, sim.runtime, at=at.isoformat()), reason)
        self.assertEqual((sim.instance, sim.runtime), before)

    def test_approved_grant_defaults_roundtrip_without_aliasing_the_proposal(self):
        sim = delegated_sim()
        change = {'kind': 'grant', 'decision_id': 'DC-close-defaults', 'grant': {
            'id': 'GR-close-defaults', 'kind': 'local', 'roles': ['maintenance']}}
        proposal = deepcopy(change)
        sim.engine.instance, sim.engine.runtime, event = gov.apply_decision(
            sim.instance, sim.runtime, change, source_ref='GS-close-delegation', clock=sim.clock)
        sim.engine._save()
        grant = sim.instance['grants']['GR-close-defaults']
        self.assertEqual(change, proposal)
        self.assertEqual(grant, {**proposal['grant'], 'status': 'active', 'expires_at': None,
            'created_at': event['created_at'], 'source_ref': event['source_ref'], 'decision_id': event['id'],
            'reuse': 'once', **{field: [] for field in gov.GRANT_LIST_FIELDS if field not in proposal['grant']}})
        self.assertIsNone(gov.validate_grant_source(sim.instance, grant))
        change['grant']['roles'].append('operational_review')
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1]['grants'][grant['id']], grant)
        self.assertEqual(grant['roles'], ['maintenance'])

    def test_delegation_authorization_returns_exact_identity_without_writing(self):
        sim = delegated_sim()
        app = next(row for row in sim.runtime['delegation_applications'].values() if row['delegation_id'] == 'DG-close')
        before = deepcopy((sim.instance, sim.runtime))
        self.assertEqual(delegations.authorize_delegated_case(sim.instance, 'DG-close',
            {'application_id': app['id']}, runtime=sim.runtime, now_iso=sim.clock.now()), {
                'allowed': True, 'delegation_id': 'DG-close', 'application_id': app['id'],
                'original_decision_id': 'DC-close-original'})
        blind = delegations.judgment_input(sim.runtime, app['id'])
        self.assertEqual(blind, {'basis': app['basis'], 'input_sha256': app['input_sha256']})
        self.assertNotIn('judgments', blind)
        blind['basis']['case']['effect']['operation'] = '변조'
        self.assertEqual((sim.instance, sim.runtime), before)

    def test_preparing_same_case_returns_detached_existing_application(self):
        sim = delegated_sim()
        app = next(row for row in sim.runtime['delegation_applications'].values() if row['delegation_id'] == 'DG-close')
        before = deepcopy(sim.runtime)
        actual = delegations.prepare_application(sim.instance, sim.runtime, 'DG-close', app['basis']['case'], now_iso=sim.clock.now())
        self.assertEqual(actual, app)
        actual['judgments'].clear()
        self.assertEqual(sim.runtime, before)

    def test_wrong_delegation_and_supplied_effect_return_exact_denials(self):
        sim = delegated_sim()
        app = next(row for row in sim.runtime['delegation_applications'].values() if row['delegation_id'] == 'DG-close')
        before = deepcopy((sim.instance, sim.runtime))
        self.assertEqual(delegations.authorize_delegated_case(sim.instance, 'other',
            {'application_id': app['id']}, runtime=sim.runtime, now_iso=sim.clock.now()),
            {'allowed': False, 'delegation_id': 'other', 'reason': 'wrong delegation'})
        case = {**deepcopy(app['basis']['case']), 'application_id': app['id']}
        case['effect']['operation'] = '다른 효과'
        self.assertEqual(delegations.authorize_delegated_case(sim.instance, 'DG-close', case,
            runtime=sim.runtime, now_iso=sim.clock.now()), {'allowed': False, 'delegation_id': 'DG-close',
                'reason': 'requested case differs from independently checked effect'})
        self.assertEqual((sim.instance, sim.runtime), before)

    def test_audit_mapping_and_goal_binding_are_exact_and_detached(self):
        sim = auditor_sim()
        output = audit_output(sim)
        before = deepcopy((sim.instance, sim.runtime))
        result = gov.evaluate_goal_audits(sim.instance, sim.runtime, 'EX-close-auditor', output['additional_audits'])
        expected = [{'audit_ref': 'AU-close', 'audit_sha256': exact_content_hash(sim.instance['governance']['AU-close']),
            'assessor': 'goal_audit', 'verdict': 'pass', 'decision': 'satisfied',
            'input_hashes': output['additional_audits'][0]['input_hashes'], 'execution_id': 'EX-close-auditor',
            'reason': '승인된 기준과 비교한 합성 판단'}]
        self.assertEqual(result, expected)
        self.assertIsNone(gov.validate_goal_additional_audits(sim.instance,
            [{'execution_id': 'EX-close-auditor', 'additional_audits': result}], runtime=sim.runtime))
        result[0]['input_hashes'].clear()
        self.assertEqual((sim.instance, sim.runtime), before)

    def test_partial_additional_audit_cannot_establish_goal(self):
        sim = auditor_sim()
        result = gov.evaluate_goal_audits(sim.instance, sim.runtime, 'EX-close-auditor', audit_output(sim, 'partial')['additional_audits'])
        before = deepcopy((sim.instance, sim.runtime))
        with self.assertRaisesRegex(ValueError, '^additional audit does not establish goal satisfaction$'):
            gov.validate_goal_additional_audits(sim.instance,
                [{'execution_id': 'EX-close-auditor', 'additional_audits': result}], runtime=sim.runtime)
        self.assertEqual((sim.instance, sim.runtime), before)

    def test_goal_judgment_mapping_cannot_change_execution_binding(self):
        sim = auditor_sim()
        result = gov.evaluate_goal_audits(sim.instance, sim.runtime, 'EX-close-auditor', audit_output(sim)['additional_audits'])
        result[0]['execution_id'] = 'other'
        before = deepcopy((sim.instance, sim.runtime))
        with self.assertRaisesRegex(ValueError, '^additional audit mapping or judgment binding changed$'):
            gov.validate_goal_additional_audits(sim.instance,
                [{'execution_id': 'EX-close-auditor', 'additional_audits': result}], runtime=sim.runtime)
        self.assertEqual((sim.instance, sim.runtime), before)

    def test_missing_additional_audit_never_counts_as_satisfaction(self):
        sim = auditor_sim()
        before = deepcopy((sim.instance, sim.runtime))
        with self.assertRaisesRegex(ValueError, '^goal judgment omits a current additional audit$'):
            gov.validate_goal_additional_audits(sim.instance,
                [{'execution_id': 'EX-close-auditor', 'additional_audits': []}], runtime=sim.runtime)
        self.assertEqual((sim.instance, sim.runtime), before)

    def test_first_audit_slot_seals_once_without_completion_event(self):
        sim = auditor_sim()
        e = sim.engine
        action = deepcopy(sim.runtime['executions']['EX-close-auditor']['action'])
        old_events = deepcopy(sim.runtime['events'])
        old_judgments = deepcopy(sim.instance['goal_judgments'])
        result = e._apply_governance_goal_audit(action, audit_output(sim), 'EX-close-auditor')
        self.assertEqual(sim.instance['goal_judgments'], old_judgments + [result])
        self.assertEqual((result['slot'], result['required'], result['basis'], result['execution_id']),
                         (0, 2, action['basis'], 'EX-close-auditor'))
        self.assertEqual(sim.runtime['events'], old_events)
        self.assertEqual(sim.instance['goal_status'], 'unsolved')
        before = deepcopy((sim.instance, sim.runtime))
        with self.assertRaisesRegex(ValueError, '^goal audit slot already sealed$'):
            e._apply_governance_goal_audit(action, audit_output(sim), 'EX-close-auditor')
        self.assertEqual((sim.instance, sim.runtime), before)
        e._save()
        self.assertEqual(e.store.load(e.head)[1]['goal_judgments'], old_judgments + [result])

    def test_missing_task_has_precise_existence_change(self):
        sim = planned_sim()
        tid = next(a['target'] for a in sim.runtime['queue'] if a['role'] == 'research_work')
        basis = input_basis.capture_decision_basis(sim.instance, sim.runtime, [tid])
        state = deepcopy(sim.runtime)
        del state['tasks'][tid]
        before = deepcopy((sim.instance, state))
        self.assertEqual(input_basis.decision_basis_changes(basis, sim.instance, state), [
            {'id': tid, 'field': 'existence', 'before': True, 'after': False, 'next': 'refresh_decision'}])
        self.assertEqual((sim.instance, state), before)

    def test_exact_approval_draft_is_read_only_and_application_roundtrips(self):
        sim = checked_sim()
        e = sim.engine
        bundle = checked_bundle(sim)
        before = deepcopy((sim.instance, sim.runtime))
        draft = gov.import_approval_draft(sim.instance, sim.runtime, bundle['id'],
            owner_handlers=e.governance_owner_handlers(), clock=sim.clock)
        self.assertEqual(draft, {'kind': 'import_approval', 'import_id': bundle['id'],
            'bundle_sha256': bundle['sha256'], 'check_sha256': bundle['check']['sha256'],
            'unit_hashes': {u['unit_id']: exact_content_hash(u['payload']) for u in bundle['output']['import_units'] if u['payload']}})
        self.assertEqual((sim.instance, sim.runtime), before)
        e.instance, e.runtime, receipt = gov.apply_import_control(sim.instance, sim.runtime,
            {'id': 'DC-close-approve', 'action': 'decision', 'origin': 'user', 'text': '이 변경을 승인한다.', 'config': draft},
            owner_handlers=e.governance_owner_handlers(), clock=sim.clock)
        self.assertEqual(receipt['status'], 'applied')
        self.assertEqual(gov.governance_view(sim.instance)['goal'], 'Prove Q')
        self.assertEqual(receipt['applied_units'], [u['unit_id'] for u in bundle['output']['import_units'] if u['payload']])
        e._save()
        saved = e.store.load(e.head)
        self.assertEqual(saved[2]['intent_imports'][bundle['id']]['application'], receipt)
        self.assertEqual(saved[1]['governance_sources']['DC-close-approve']['text'], '이 변경을 승인한다.')
