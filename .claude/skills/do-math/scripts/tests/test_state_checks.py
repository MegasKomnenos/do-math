"""Persisted v5 checks use actual domain producers and adversarial mutations.

These replace the v4 FakeEngine academic end-to-end fixture: the checker tests
record invariants, not the retired nonformal final-assurance workflow.
"""
from copy import deepcopy
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from do_math import knowledge_records, external, execution_lifecycle
from do_math.state_checks import inspect_state, state_errors
from test_redesign_SURFACE import surface_state


class StateCheckTests(unittest.TestCase):
    def test_valid_rule_payload_is_not_an_error_list(self):
        from v5_fixtures import supply_observation_rules
        instance, runtime = surface_state()
        extensions = {}
        supply_observation_rules([{'title': 'fixture'}], extensions)
        rules = extensions['task_conditions'][0]['observation_rules']
        runtime['executions']['EX-1']['observation_rules'] = deepcopy(rules)
        runtime['task_observation_rules'] = {'TK-fixture': deepcopy(rules)}
        self.assertEqual(self.area(instance, runtime, 'self_check_stop')['status'], 'healthy')
        runtime['executions']['EX-1']['observation_rules'][0]['threshold'] = 0
        self.assertError(instance, runtime, 'positive integer', 'self_check_stop')

    def area(self, instance, runtime, name):
        return inspect_state(instance, runtime, requested_areas=[name])

    def assertError(self, instance, runtime, text, area):
        errors = self.area(instance, runtime, area)['findings']
        self.assertTrue(any(text in row['message'] for row in errors), errors)

    def test_domain_created_activity_execution_profiles_are_clean(self):
        instance, runtime = surface_state()
        report = self.area(instance, runtime, 'tasks_activities_executions')
        self.assertEqual(report['status'], 'healthy', report)
        self.assertIn('activity ownership and continuation', report['areas'][0]['checked_invariants'])
        before = deepcopy(runtime)
        self.area(instance, runtime, 'tasks_activities_executions')
        self.assertEqual(runtime, before)

    def test_execution_state_lineage_profile_and_activity_mutations(self):
        for field, value, message in (
            ('status', 'teleporting', 'status'),
            ('owner_activity_id', 'absent', 'activity'),
            ('continuation_of', 'EX-missing', 'continuation'),
            ('execution_profile_ref', {'id': 'missing'}, 'profile'),
        ):
            with self.subTest(field=field):
                instance, runtime = surface_state()
                runtime['executions']['EX-1'][field] = value
                self.assertError(instance, runtime, message, 'tasks_activities_executions')
        instance, runtime = surface_state()
        profile = next(iter(instance['execution_profiles'].values()))
        profile['role'] = 'changed'
        self.assertEqual(self.area(instance, runtime, 'tasks_activities_executions')['status'], 'blocked')

    def test_separated_knowledge_and_source_mutations(self):
        instance, runtime = surface_state()
        candidate = {'kind': 'theorem', 'title': 'P', 'statement': 'P', 'explanation': 'Argument',
                     'summary': 'P follows', 'lean_code': 'theorem p : True := True.intro',
                     'declaration_names': ['p'], 'dependencies': []}
        instance, kid = knowledge_records.create_candidate(instance, candidate, source_ref='SRC', actor_ref='EX-1')
        self.assertEqual(self.area(instance, runtime, 'mathematical_effect')['status'], 'healthy')
        formal = instance['formal_results'][instance['knowledge'][kid]['formal_result_id']]
        formal.update(publication_state='accepted', formal_use='active')
        self.assertError(instance, runtime, 'stale verification', 'mathematical_effect')
        instance['knowledge'][kid]['exposition_id'] = 'missing'
        self.assertEqual(self.area(instance, runtime, 'mathematical_effect')['status'], 'blocked')
        instance['sources'] = [{'name': 'broken', 'path': 'runtime/broken', 'sha256': 'bad', 'bytes': -1}]
        self.assertError(instance, runtime, 'invalid sha256', 'record_storage')
        self.assertError(instance, runtime, 'invalid byte count', 'record_storage')

    def test_completion_requires_all_obligations_and_authoritative_waiver(self):
        from test_redesign_TASKS import task
        instance, runtime = surface_state()
        value = task()
        value['status'] = 'completed'
        from do_math.execution_profiles import profile_ref
        value['profile_refs'] = [profile_ref(next(p for p in instance['execution_profiles'].values() if p['role']=='research_work'))]
        value['assessment'] = {'task_id':value['id'],'decision':'completed','reason':'Obligations assessed', 'item_dispositions': [
            {'obligation_id': 'OB-1', 'kind': 'fulfilled', 'evidence_refs': ['EV-1']}], 'unresolved': []}
        runtime['tasks'][value['id']] = value
        self.assertError(instance, runtime, 'every obligation', 'tasks_activities_executions')
        value['assessment']['item_dispositions'].append(
            {'obligation_id': 'OB-2', 'kind': 'waived', 'authority_ref': 'missing', 'evidence_refs': []})
        self.assertError(instance, runtime, 'authority', 'tasks_activities_executions')

    def test_solved_goal_requires_current_complete_audits(self):
        instance, runtime = surface_state()
        instance.update(goal_status='mathematically_solved', goal_assessment_basis='GB')
        instance['goal_judgments'] = [{'id': 'GJ-1', 'execution_id': 'EX-1', 'basis': 'GB', 'required': 1, 'slot': 'one',
                                     'decision': 'satisfied', 'scope_complete': True}]
        self.assertEqual(self.area(instance, runtime, 'mathematical_effect')['status'], 'healthy')
        instance['goal_judgments'][0]['current'] = False
        self.assertError(instance, runtime, 'current agreeing audits', 'mathematical_effect')

    def test_supplement_request_must_match_pending_review_owner(self):
        instance, runtime = surface_state()
        runtime['review_cycles'] = {'RC': {'id': 'RC', 'status': 'working', 'knowledge_id': 'KN',
            'research': {'RQ': {'status': 'pending', 'action': {'slot': 'initial-0'}}}}}
        runtime['queue'] = [{'role': 'supplemental_research', 'target': 'KN',
            'review_cycle_id': 'RC', 'research_request_id': 'RQ', 'requesting_slot': 'wrong'}]
        self.assertError(instance, runtime, 'queued investigation is not linked', 'preparation_selection')

    def test_external_error_http_remains_unknown_and_reconciliation_is_distinct(self):
        instance, runtime = surface_state()
        operation = external.prepare_operation({'method': 'POST', 'url': 'https://example.test/', 'body': ''}, 'GR', 'SRC', 'OP')
        operation['producer_executions'] = ['EX-1']
        import jsonschema
        from do_math.record_schemas import RECORDS, REFERENCES
        jsonschema.validate(operation, RECORDS['external_operations'])
        self.assertIn(('EX-1', 'executions'), list(REFERENCES['external_operations'](operation)))
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate({**operation, 'producer_executions': [1]}, RECORDS['external_operations'])
        # An actual domain transport response, not a fabricated successful receipt.
        grant = {'id': 'GR', 'status': 'active', 'allowed_origins': ['https://example.test'],
                 'allowed_methods': ['POST'], 'allowed_path_prefixes': ['/'], 'credential_env': {}}
        operation = external.execute_operation(operation, grant,
            transport=lambda *_: {'http_status': 500, 'body': b'uncertain'}, persist=lambda row: row)
        runtime['external_operations'] = {'OP': operation}
        self.assertEqual(operation['status'], 'unknown')
        self.assertEqual(self.area(instance, runtime, 'tasks_activities_executions')['status'], 'healthy')
        operation['succeeded'] = False
        self.assertError(instance, runtime, 'definitive success', 'tasks_activities_executions')
        operation['succeeded'] = None
        operation['handling'] = 'reconciled'
        self.assertError(instance, runtime, 'reconciled handling', 'tasks_activities_executions')

    def test_reservation_requires_balanced_settlement_and_existing_owner(self):
        instance, runtime = surface_state()
        runtime['reservations']['R'] = {'id': 'R', 'constraint_id': 'missing', 'unit': 'session',
            'budget_kind': 'work', 'state': 'settled', 'reserved': 1, 'confirmed_consumed': 0,
            'returned': 0, 'owner_kind': 'execution', 'owner_id': 'missing', 'evidence_refs': []}
        self.assertError(instance, runtime, 'reservation', 'tasks_activities_executions')

    def test_requested_area_never_reuses_other_domain_findings(self):
        instance, runtime = surface_state()
        runtime['executions']['EX-1']['status'] = 'teleporting'
        self.assertEqual(self.area(instance, runtime, 'governance_trust')['status'], 'healthy')
        report = self.area(instance, runtime, 'start_import_input')
        self.assertEqual(report['status'], 'incomplete')
        self.assertTrue(report['areas'][0]['not_checked'])

    def test_unknown_version_and_old_state_are_not_new_contract_success(self):
        instance, runtime = surface_state()
        instance['feature_version'] = 99
        self.assertError(instance, runtime, 'feature_version 5', 'record_storage')
        instance['feature_version'] = runtime['feature_version'] = 99
        self.assertIn('state: unsupported feature version', state_errors(instance, runtime))


if __name__ == '__main__':
    unittest.main(verbosity=2)
