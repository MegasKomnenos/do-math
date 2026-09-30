"""Relations expose the same references to impact analysis, submission and judgments (``relation_refs`` through
``knowledge.plan_impact``, ``submission.reported_references`` and ``task_scope.assessment_basis``; layer 2),
moved from ``test_relation_dependencies`` (``RelationEvidenceTests``).

The tests call the product's pure functions on plain records and the record
fixtures; nothing of the product is replaced.
"""
import unittest

from do_math import submission, task_scope


class RelationEvidenceTests(unittest.TestCase):
    def test_impact_analysis_does_not_turn_evidence_file_locators_into_record_dependencies(self):
        from do_math.knowledge import plan_impact
        instance = {'knowledge': {'KN-a': {'id': 'KN-a', 'dependencies': []}}, 'relations': [
            {'id': 'RL-a', 'source': 'KN-a', 'target': 'KN-a', 'evidence_refs': ['workspace:proof.md']}]}
        plan = plan_impact(instance, {}, ['KN-a'], ['RL-a'])
        self.assertEqual(plan['unresolved_refs'], [])
        self.assertFalse(plan['requires_independent_review'])

    def test_output_and_extension_relations_report_every_explicit_reference(self):
        relation = {'source': 'KN-source', 'target': 'KN-target', 'evidence_refs': ['SO-evidence'],
                    'formal_result_refs': ['FR-proof'], 'assessment_refs': ['IA-proof'],
                    'history': [{'source': 'KN-history'}], 'evidence': 'KN-prose'}
        expected = {'KN-source', 'KN-target', 'SO-evidence', 'FR-proof', 'IA-proof'}
        for output, extensions in (({'relations': [relation]}, {}), ({}, {'relations': [relation]})):
            self.assertEqual(set(submission.reported_references(output, extensions)), expected)

    def test_relation_judgment_edges_keep_formal_and_assessment_use_current(self):
        from record_fixtures import specialist_assessment
        for field in ('formal_result_refs', 'assessment_refs', 'evidence_refs'):
            with self.subTest(field=field):
                instance, runtime, _, kid, aid = specialist_assessment()
                task = runtime['tasks']['TK-1']
                formal_id = instance['knowledge'][kid]['formal_result_id']
                relation = {'id': 'RL-proof', 'kind': 'supports', 'source': kid, 'target': kid,
                            field: [aid if field == 'assessment_refs' else formal_id]}
                instance['relations'] = [relation]
                assessment = {'item_dispositions': [{'evidence_refs': ['RL-proof']}], 'unresolved': []}
                before = task_scope.assessment_basis(task, assessment, instance, runtime)
                if field == 'assessment_refs':
                    for use in instance['assessment_uses'].values():
                        use['status'] = 'suspended'
                else:
                    instance['formal_results'][formal_id]['formal_use'] = 'suspended'
                self.assertNotEqual(before, task_scope.assessment_basis(task, assessment, instance, runtime))

    def test_relation_endpoints_still_bind_submitted_content_not_later_review_bookkeeping(self):
        from record_fixtures import completed_with_knowledge
        instance, runtime = completed_with_knowledge()
        task = runtime['tasks']['TK-1']
        instance['relations'] = [{'id': 'RL-content', 'kind': 'supports', 'source': 'KN-proof', 'target': 'KN-proof'}]
        assessment = {'item_dispositions': [{'evidence_refs': ['RL-content']}], 'unresolved': []}
        before = task_scope.assessment_basis(task, assessment, instance, runtime)
        instance['knowledge']['KN-proof']['review_cycle_id'] = 'RC-new'
        instance['formal_results']['FR-proof'].update(formal_use='active', verification={'status': 'verified'})
        self.assertEqual(before, task_scope.assessment_basis(task, assessment, instance, runtime))
        instance['expositions']['XP-proof']['items'][0]['text'] = 'changed argument'
        self.assertNotEqual(before, task_scope.assessment_basis(task, assessment, instance, runtime))


if __name__ == '__main__':
    unittest.main()
