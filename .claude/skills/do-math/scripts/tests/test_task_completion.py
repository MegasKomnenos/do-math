"""Task completion, transfer and withdrawal (``do_math.task_scope``).

Which submitted evidence keeps a completion assessment current, how an
assessment transfers obligations, and what a withdrawal preserves. Pure
functions over record fixtures.
"""
import sys
import unittest
from copy import deepcopy
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math import planning, task_scope
from do_math.repository import exact_content_hash
from record_fixtures import apply_assessment, completed_with_knowledge, specialist_assessment


class PartialWithdrawalTests(unittest.TestCase):
    def test_current_unperformed_withdrawal_preserves_results_and_residual_scope(self):
        from record_fixtures import withdraw_prepared, withdrawable_task
        _, runtime, snapshot = withdrawable_task()
        _, changed = withdraw_prepared(runtime, snapshot)
        task = changed['tasks']['TK-AI']
        task_scope.validate_withdrawal_record(task)
        self.assertIsNone(task['scope_disposition']['assessment_sha256'])
        for key in ('results_sha256', 'remaining_obligation_ids'):
            with self.subTest(missing=key):
                broken = deepcopy(task)
                broken['scope_disposition'].pop(key)
                with self.assertRaises(ValueError):
                    task_scope.validate_withdrawal_record(broken)

    def fixture(self):
        from record_fixtures import withdrawable_task
        instance, runtime, _ = withdrawable_task()
        task = runtime['tasks']['TK-AI']
        task.update(status='waiting', results=[{'execution_id':'EX-work','outcome':'partial'}])
        # A stored assessment is the planner's task assessment plus receiver fields (apply_task_assessments).
        assessment = {'task_id':task['id'], 'decision':'incomplete', 'reason':'The partial result leaves every obligation open',
            'execution_id':'EX-plan',
            'item_dispositions':[{'obligation_id':o['id'],'kind':'open','evidence_refs':[]}
                                 for o in task['completion_obligations']], 'unresolved':[]}
        assessment.update(contract_sha256=planning.contract_hash(task), results_sha256=exact_content_hash(task['results']),
            current=True, basis=task_scope.assessment_basis(task, assessment, instance, runtime))
        task['assessment'] = assessment
        return instance, runtime, {task['id']:deepcopy(task)}

    def test_assessed_partial_work_closes_without_becoming_complete(self):
        instance, runtime, snapshot = self.fixture()
        _, changed = task_scope.apply_task_dispositions(instance, runtime,
            [{'task_id':'TK-AI','disposition':'withdraw','reason':'This optional approach is no longer useful'}],
            execution_id='EX-next-plan', input_tasks=snapshot)
        task = changed['tasks']['TK-AI']
        self.assertEqual(task['status'], 'closed')
        self.assertEqual(task['results'], snapshot['TK-AI']['results'])
        self.assertNotIn('assessment', task)
        self.assertEqual(task['assessment_history'][-1], snapshot['TK-AI']['assessment'])
        self.assertEqual(task['scope_disposition']['remaining_obligation_ids'], ['OB-1','OB-2'])
        task_scope.validate_withdrawal_record(task)
        task['scope_disposition']['remaining_obligation_ids'] = []
        with self.assertRaises(ValueError): task_scope.validate_withdrawal_record(task)

    def test_unassessed_new_results_and_protected_scope_are_not_withdrawable(self):
        # Each change is rejected by its own withdrawal rule, not by the stored-record schema.
        reasons = {'new_result': 'current item dispositions', 'stale_assessment': 'current item dispositions',
                   'user_required': 'protected obligations', 'transferred_obligations': 'protected obligations'}
        for change, reason in reasons.items():
            with self.subTest(change=change):
                instance, runtime, snapshot = self.fixture()
                task = runtime['tasks']['TK-AI']
                if change == 'new_result': task['results'].append({'execution_id':'EX-new'})
                elif change == 'stale_assessment': task['assessment']['current'] = False
                else: task[change] = True
                with self.assertRaisesRegex(ValueError, reason):
                    task_scope.apply_task_dispositions(instance,runtime,
                        [{'task_id':'TK-AI','disposition':'withdraw','reason':'not authorized'}],
                        execution_id='EX-next', input_tasks=snapshot)


class CompletionBasisTests(unittest.TestCase):
    def test_submission_completion_survives_later_formal_verification_and_review_id(self):
        instance, runtime = completed_with_knowledge()
        task = runtime['tasks']['TK-1']
        self.assertTrue(task_scope.assessment_current(task, instance, runtime))
        instance['formal_results']['FR-proof'].update(publication_state='accepted', formal_use='active',
                                                    verification={'status': 'verified'})
        instance['knowledge']['KN-proof']['review_cycle_id'] = 'RC-new'
        self.assertTrue(task_scope.assessment_current(task, instance, runtime),
                        'Post-submission bookkeeping must not invalidate unchanged submitted evidence')

    def test_actual_submitted_source_change_still_invalidates_completion(self):
        instance, runtime = completed_with_knowledge()
        instance['formal_results']['FR-proof']['lean_code'] = 'different source'
        self.assertFalse(task_scope.assessment_current(runtime['tasks']['TK-1'], instance, runtime))

    def test_relation_endpoint_contents_remain_part_of_completion_evidence(self):
        instance, runtime = completed_with_knowledge()
        task = runtime['tasks']['TK-1']
        instance['knowledge']['KN-proof']['relation_claim'] = {'source': 'KN-source', 'target': 'KN-target'}
        for name in ('source', 'target'):
            instance['knowledge']['KN-' + name] = {'id': 'KN-' + name, 'lifecycle': 'active',
                'exposition_id': 'XP-' + name, 'formal_result_id': None, 'dependencies': []}
            instance['expositions']['XP-' + name] = {'id': 'XP-' + name, 'items': [{'text': name}]}
        task['assessment']['basis'] = task_scope.assessment_basis(task, task['assessment'], instance, runtime)
        instance['expositions']['XP-source']['items'][0]['text'] = 'different endpoint'
        self.assertFalse(task_scope.assessment_current(task, instance, runtime))

    def test_new_identity_assessment_does_not_change_submission_content_basis(self):
        instance, runtime = completed_with_knowledge()
        instance['identity_assessments']['IA-later'] = {'id': 'IA-later', 'formal_result_id': 'FR-proof',
            'exposition_id': 'XP-proof', 'decision': 'match'}
        self.assertTrue(task_scope.assessment_current(runtime['tasks']['TK-1'], instance, runtime))

    def test_specialist_support_still_requires_its_current_trust_and_use(self):
        for judge in ('formal_check', 'identity_review'):
            with self.subTest(judge=judge):
                instance, runtime, assessment, _, _ = specialist_assessment(judge)
                instance, runtime = apply_assessment(instance, runtime, assessment)
                task = runtime['tasks']['TK-1']
                self.assertTrue(task_scope.assessment_current(task, instance, runtime))
                if judge == 'formal_check':
                    instance['active_trust_environment'] = 'TE-other'
                else:
                    for use in instance['assessment_uses'].values():
                        use['status'] = 'suspended'
                self.assertFalse(task_scope.assessment_current(task, instance, runtime))

    def test_specialist_dependency_use_is_not_reduced_to_submission_content(self):
        instance, runtime, assessment, kid, _ = specialist_assessment('formal_check')
        formal = instance['formal_results'][instance['knowledge'][kid]['formal_result_id']]
        formal['dependencies'] = ['KN-dependency']
        instance['knowledge']['KN-dependency'] = {'id': 'KN-dependency', 'lifecycle': 'active',
            'formal_result_id': 'FR-dependency', 'dependencies': []}
        instance['formal_results']['FR-dependency'] = {'id': 'FR-dependency', 'lean_code': 'dependency',
            'declaration_names': ['dependency'], 'formal_use': 'active', 'dependencies': []}
        instance, runtime = apply_assessment(instance, runtime, assessment)
        instance['formal_results']['FR-dependency']['formal_use'] = 'suspended'
        self.assertFalse(task_scope.assessment_current(runtime['tasks']['TK-1'], instance, runtime))


class TransferReferenceTests(unittest.TestCase):
    def test_nonready_recipient_uses_separate_fixed_reference_population(self):
        from record_fixtures import transfer_assessment, apply_assessment
        from do_math.task_scope import apply_task_assessments
        instance, runtime, assessment = transfer_assessment()
        selected_population = {'TK-1': deepcopy(runtime['tasks']['TK-1'])}
        original = deepcopy(runtime['tasks'])
        _, changed = apply_task_assessments(instance, runtime, [assessment], execution_id='EX-plan',
            input_tasks=selected_population, reference_tasks=original)
        self.assertEqual(changed['tasks']['TK-2']['completion_obligations'][-1]['id'], 'OB-inherited')
        self.assertEqual(set(selected_population), {'TK-1'})
        for mutate in (lambda r: r['tasks']['TK-2'].update(revision=2),
                       lambda r: r['tasks']['TK-2'].update(status='closed'),
                       lambda r: r['executions'].update({'EX-peer': {'status': 'running', 'action': {'target': 'TK-2'}}})):
            candidate = deepcopy(runtime)
            mutate(candidate)
            with self.assertRaises(ValueError):
                apply_task_assessments(instance, candidate, [assessment], execution_id='EX-plan',
                    input_tasks=selected_population, reference_tasks=original)
        with self.assertRaisesRegex(ValueError, 'recipient'):
            apply_task_assessments(instance, runtime, [assessment], execution_id='EX-plan',
                input_tasks=selected_population, reference_tasks=selected_population)


if __name__ == "__main__":
    unittest.main()
