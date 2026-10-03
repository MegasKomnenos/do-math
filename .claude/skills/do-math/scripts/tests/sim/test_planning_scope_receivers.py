"""실제 수신·저장 상태 위에서 평가와 양도의 원자성 및 잔여 의무를 확인한다."""
from copy import deepcopy
import re
import unittest

from do_math import planning, task_scope
from do_math.canonical import exact_content_hash
from support.engine_lifecycle import _ended_execution
from support.planning_contract_inputs import (prepared_sim, only_task, returned, transfer_sim,
                                             transfer_input, warm_prepared, warm_transfer)


def setUpModule():
    warm_prepared()
    warm_transfer()


class AssessmentReceiverTests(unittest.TestCase):
    def setUp(self):
        self.sim = prepared_sim()
        self.assessment = returned(self.sim)
        self.engine = self.sim.engine
        self.task = only_task(self.sim)
        self.snapshot = deepcopy(self.sim.runtime['tasks'])

    def apply(self):
        return task_scope.apply_task_assessments(self.sim.instance, self.sim.runtime, [self.assessment],
            execution_id='EX-planning-plan', input_tasks=self.snapshot, clock=self.sim.ports.clock)

    def test_completed_assessment_survives_real_storage_and_restart(self):
        before = deepcopy((self.sim.instance, self.sim.runtime))
        instance, runtime = self.apply()
        identifier = self.task['id']
        assessed = runtime['tasks'][identifier]
        self.assertEqual(assessed['status'], 'completed')
        self.assertEqual(assessed['assessment'], {**self.assessment, 'execution_id': 'EX-planning-plan',
            'contract_sha256': planning.contract_hash(self.task),
            'results_sha256': exact_content_hash(self.task['results']), 'current': True,
            'basis': task_scope.assessment_basis(self.task, self.assessment, instance, runtime), 'specialist_support': {}})
        self.assertEqual((self.sim.instance, self.sim.runtime), before)
        self.engine.instance, self.engine.runtime = instance, runtime
        self.engine._save()
        expected = deepcopy(self.sim.runtime['tasks'][identifier])
        self.sim.restart()
        self.assertEqual(self.sim.runtime['tasks'][identifier], expected)
        self.assertTrue(task_scope.assessment_current(expected, self.sim.instance, self.sim.runtime))

    def test_rejects_assessor_role_without_publication_or_input_mutation(self):
        self.apply()
        self.sim.runtime['executions']['EX-planning-plan']['role'] = 'research_work'
        before = deepcopy((self.sim.instance, self.sim.runtime, self.assessment, self.snapshot))
        head = self.engine.head
        with self.assertRaisesRegex(ValueError, '^' + re.escape('completion requires a designated independent assessor execution') + '$'):
            self.apply()
        self.assertEqual((self.sim.instance, self.sim.runtime, self.assessment, self.snapshot), before)
        self.assertEqual(self.engine.head, head)

    def test_rejects_changed_snapshot_without_publication_or_input_mutation(self):
        self.apply()
        self.snapshot[self.task['id']]['question'] = '이전 질문'
        before = deepcopy((self.sim.instance, self.sim.runtime, self.assessment, self.snapshot))
        head = self.engine.head
        with self.assertRaisesRegex(ValueError, '^' + re.escape('assessment contract or returned work changed') + '$'):
            self.apply()
        self.assertEqual((self.sim.instance, self.sim.runtime, self.assessment, self.snapshot), before)
        self.assertEqual(self.engine.head, head)

    def test_rejects_terminal_task_without_publication_or_input_mutation(self):
        self.apply()
        self.task['status'] = 'completed'
        before = deepcopy((self.sim.instance, self.sim.runtime, self.assessment, self.snapshot))
        head = self.engine.head
        with self.assertRaisesRegex(ValueError, '^' + re.escape('assessment requires unfinished returned work') + '$'):
            self.apply()
        self.assertEqual((self.sim.instance, self.sim.runtime, self.assessment, self.snapshot), before)
        self.assertEqual(self.engine.head, head)

    def test_rejects_empty_results_without_publication_or_input_mutation(self):
        self.apply()
        self.task['results'] = []
        self.snapshot = deepcopy(self.sim.runtime['tasks'])
        before = deepcopy((self.sim.instance, self.sim.runtime, self.assessment, self.snapshot))
        head = self.engine.head
        with self.assertRaisesRegex(ValueError, '^' + re.escape('assessment requires unfinished returned work') + '$'):
            self.apply()
        self.assertEqual((self.sim.instance, self.sim.runtime, self.assessment, self.snapshot), before)
        self.assertEqual(self.engine.head, head)

    def test_rejects_author_assesses_without_publication_or_input_mutation(self):
        self.apply()
        self.task['author_execution_ids'] = ['EX-planning-plan']
        before = deepcopy((self.sim.instance, self.sim.runtime, self.assessment, self.snapshot))
        head = self.engine.head
        with self.assertRaisesRegex(ValueError, '^' + re.escape('contract author cannot assess its own obligations') + '$'):
            self.apply()
        self.assertEqual((self.sim.instance, self.sim.runtime, self.assessment, self.snapshot), before)
        self.assertEqual(self.engine.head, head)

    def test_rejects_live_work_without_publication_or_input_mutation(self):
        self.apply()
        self.engine._register_execution({'id': 'AC-live', 'role': 'research_work', 'target': self.task['id']},
            {'id': 'EX-live', 'role': 'research_work', 'status': 'running'})
        before = deepcopy((self.sim.instance, self.sim.runtime, self.assessment, self.snapshot))
        head = self.engine.head
        with self.assertRaisesRegex(ValueError, '^' + re.escape('work execution must end before completion assessment') + '$'):
            self.apply()
        self.assertEqual((self.sim.instance, self.sim.runtime, self.assessment, self.snapshot), before)
        self.assertEqual(self.engine.head, head)

    def test_rejects_unknown_evidence_without_publication_or_input_mutation(self):
        self.apply()
        self.assessment['item_dispositions'][0]['evidence_refs'] = ['workspace:report.md']
        before = deepcopy((self.sim.instance, self.sim.runtime, self.assessment, self.snapshot))
        head = self.engine.head
        with self.assertRaisesRegex(ValueError, '^' + re.escape("completion evidence requires a supplied record ID; read the file and cite its producing execution or source record; invalid_evidence_refs=['workspace:report.md']") + '$'):
            self.apply()
        self.assertEqual((self.sim.instance, self.sim.runtime, self.assessment, self.snapshot), before)
        self.assertEqual(self.engine.head, head)

    def test_incomplete_open_assessment_keeps_one_continuation_and_prior_history(self):
        self.assessment['decision'] = 'incomplete'
        self.assessment['item_dispositions'][0]['kind'] = 'open'
        instance, runtime = self.apply()
        identifier = self.task['id']
        self.assertEqual(runtime['tasks'][identifier]['waiting'], {
            'kind': 'research_followup', 'target_refs': [], 'next_owner': 'research_plan', 'basis_ref': 'EX-planning-plan'})
        first = deepcopy(runtime['tasks'][identifier]['assessment'])
        queue = deepcopy(runtime['queue'])
        self.engine.instance, self.engine.runtime = instance, runtime
        self.engine._save()
        self.snapshot = deepcopy(self.sim.runtime['tasks'])
        instance, runtime = self.apply()
        self.assertEqual(runtime['queue'], queue)
        self.assertEqual(runtime['tasks'][identifier]['assessment_history'], [first])
        self.engine.instance, self.engine.runtime = instance, runtime
        self.engine._save()
        self.sim.restart()
        self.assertEqual(self.sim.runtime['tasks'][identifier]['assessment_history'], [first])

    def test_current_assessment_rejects_changed_contract_and_refresh_is_idempotent(self):
        instance, runtime = self.apply()
        identifier = self.task['id']
        task = runtime['tasks'][identifier]
        self.assertTrue(task_scope.assessment_current(task, instance, runtime))
        task['question'] = '바뀐 계약 질문'
        self.assertFalse(task_scope.assessment_current(task, instance, runtime))
        self.assertEqual(task_scope.refresh_task_assessments(instance, runtime), [identifier])
        self.assertEqual(task['assessment']['invalidated_reason'],
                         'Completion contract, results, scope authority or designated judgment is no longer current')
        before = deepcopy(runtime)
        self.assertEqual(task_scope.refresh_task_assessments(instance, runtime), [])
        self.assertEqual(runtime, before)

    def test_currentness_rejects_invalid_disposition_even_with_unchanged_evidence_basis(self):
        instance, runtime = self.apply()
        task = runtime['tasks'][self.task['id']]
        self.assertTrue(task_scope.assessment_current(task, instance, runtime))
        task['assessment']['item_dispositions'][0]['kind'] = 'unknown'
        before = deepcopy((instance, runtime))
        self.assertFalse(task_scope.assessment_current(task, instance, runtime))
        self.assertEqual((instance, runtime), before)

    def test_assessment_basis_of_another_task_uses_contract_and_its_review_references(self):
        from support.planning_contract_inputs import produce_task
        other = produce_task(self.sim, '판정에 인용된 과제')
        task = only_task(self.sim)
        self.assessment['item_dispositions'][0]['evidence_refs'] = [other]
        value = self.sim.runtime['tasks'][other]
        before = deepcopy((self.sim.instance, self.sim.runtime))
        basis = task_scope.assessment_basis(task, self.assessment, self.sim.instance, self.sim.runtime)
        self.assertEqual(basis[other], exact_content_hash(planning.task_reference_basis(value)))
        for ref in value['reviews'][-1]['decision_basis']['records']:
            self.assertIn(ref['id'], basis)
        self.assertEqual((self.sim.instance, self.sim.runtime), before)


class TransferReceiverTests(unittest.TestCase):
    def setUp(self):
        self.sim = transfer_sim()
        self.engine = self.sim.engine
        self.assessment = transfer_input(self.sim)
        self.task = only_task(self.sim)
        self.row = self.assessment['item_dispositions'][0]
        self.recipient = self.sim.runtime['tasks'][self.row['target_task_id']]
        self.authority = self.sim.instance['decisions'][self.row['authority_ref']]
        self.snapshot = deepcopy(self.sim.runtime['tasks'])

    def apply(self):
        return task_scope.apply_task_assessments(self.sim.instance, self.sim.runtime, [self.assessment],
            execution_id='EX-planning-plan', input_tasks=self.snapshot, clock=self.sim.ports.clock)

    def test_transfer_preserves_obligation_and_requires_new_recipient_approval(self):
        source_id, target_id = self.task['id'], self.recipient['id']
        original = deepcopy(self.task['completion_obligations'][0])
        before = deepcopy((self.sim.instance, self.sim.runtime))
        instance, runtime = self.apply()
        target = runtime['tasks'][target_id]
        self.assertEqual(runtime['tasks'][source_id]['status'], 'closed')
        self.assertEqual(target['revision'], self.recipient['revision'] + 1)
        self.assertEqual(target['reviews'], [])
        self.assertEqual(target['completion_obligations'], [*self.recipient['completion_obligations'], {**original, 'id': 'OB-inherited'}])
        self.assertEqual(target['transferred_obligations'], [{'from_task': source_id, 'from_revision': self.task['revision'],
            'from_obligation_id': original['id'], 'obligation_id': 'OB-inherited',
            'authority_ref': self.authority['id'], 'execution_id': 'EX-planning-plan'}])
        self.assertEqual([(a['role'], a.get('target')) for a in runtime['queue']], [('task_contract_review', target_id)])
        self.assertEqual((self.sim.instance, self.sim.runtime), before)
        self.engine.instance, self.engine.runtime = instance, runtime
        self.engine._save()
        expected = deepcopy(self.sim.runtime['tasks'])
        self.sim.restart()
        self.assertEqual(self.sim.runtime['tasks'], expected)
        self.assertTrue(task_scope.assessment_current(expected[source_id], self.sim.instance, self.sim.runtime))

    def test_rejects_authority_source_atomically(self):
        self.apply()
        self.authority['source_sha256'] = 'f'*64
        before = deepcopy((self.sim.instance, self.sim.runtime, self.assessment, self.snapshot))
        head = self.engine.head
        with self.assertRaisesRegex(ValueError, '^' + re.escape('scope disposition requires a current source-bound user decision') + '$'):
            self.apply()
        self.assertEqual((self.sim.instance, self.sim.runtime, self.assessment, self.snapshot), before)
        self.assertEqual(self.engine.head, head)

    def test_rejects_authority_task_atomically(self):
        self.apply()
        self.authority['change']['task_id'] = self.recipient['id']
        before = deepcopy((self.sim.instance, self.sim.runtime, self.assessment, self.snapshot))
        head = self.engine.head
        with self.assertRaisesRegex(ValueError, '^' + re.escape('scope authority does not cover this task and disposition') + '$'):
            self.apply()
        self.assertEqual((self.sim.instance, self.sim.runtime, self.assessment, self.snapshot), before)
        self.assertEqual(self.engine.head, head)

    def test_rejects_authority_edition_atomically(self):
        self.apply()
        self.authority['change']['revision'] += 1
        before = deepcopy((self.sim.instance, self.sim.runtime, self.assessment, self.snapshot))
        head = self.engine.head
        with self.assertRaisesRegex(ValueError, '^' + re.escape('scope authority applies to a different contract edition') + '$'):
            self.apply()
        self.assertEqual((self.sim.instance, self.sim.runtime, self.assessment, self.snapshot), before)
        self.assertEqual(self.engine.head, head)

    def test_rejects_authority_obligation_atomically(self):
        self.apply()
        self.authority['change']['obligation_ids'] = []
        before = deepcopy((self.sim.instance, self.sim.runtime, self.assessment, self.snapshot))
        head = self.engine.head
        with self.assertRaisesRegex(ValueError, '^' + re.escape('scope authority does not cover this obligation') + '$'):
            self.apply()
        self.assertEqual((self.sim.instance, self.sim.runtime, self.assessment, self.snapshot), before)
        self.assertEqual(self.engine.head, head)

    def test_rejects_authority_recipient_atomically(self):
        self.apply()
        self.authority['change']['target_task_id'] = self.task['id']
        before = deepcopy((self.sim.instance, self.sim.runtime, self.assessment, self.snapshot))
        head = self.engine.head
        with self.assertRaisesRegex(ValueError, '^' + re.escape('transfer authority names a different recipient') + '$'):
            self.apply()
        self.assertEqual((self.sim.instance, self.sim.runtime, self.assessment, self.snapshot), before)
        self.assertEqual(self.engine.head, head)

    def test_rejects_terminal_recipient_atomically(self):
        self.apply()
        self.recipient['status'] = 'completed'
        before = deepcopy((self.sim.instance, self.sim.runtime, self.assessment, self.snapshot))
        head = self.engine.head
        with self.assertRaisesRegex(ValueError, '^' + re.escape('transfer requires a distinct unfinished recipient outside this assessment set') + '$'):
            self.apply()
        self.assertEqual((self.sim.instance, self.sim.runtime, self.assessment, self.snapshot), before)
        self.assertEqual(self.engine.head, head)

    def test_rejects_unbound_recipient_atomically(self):
        self.apply()
        del self.snapshot[self.recipient['id']]
        before = deepcopy((self.sim.instance, self.sim.runtime, self.assessment, self.snapshot))
        head = self.engine.head
        with self.assertRaisesRegex(ValueError, '^' + re.escape('transfer recipient must be bound to the current input') + '$'):
            self.apply()
        self.assertEqual((self.sim.instance, self.sim.runtime, self.assessment, self.snapshot), before)
        self.assertEqual(self.engine.head, head)

    def test_rejects_live_recipient_atomically(self):
        self.apply()
        self.engine._register_execution({'id': 'AC-live', 'role': 'research_work', 'target': self.recipient['id']},
            {'id': 'EX-live', 'role': 'research_work', 'status': 'running'})
        before = deepcopy((self.sim.instance, self.sim.runtime, self.assessment, self.snapshot))
        head = self.engine.head
        with self.assertRaisesRegex(ValueError, '^' + re.escape('transfer recipient has a live execution') + '$'):
            self.apply()
        self.assertEqual((self.sim.instance, self.sim.runtime, self.assessment, self.snapshot), before)
        self.assertEqual(self.engine.head, head)

    def test_rejects_existing_obligation_atomically(self):
        self.apply()
        self.row['target_obligation_id'] = 'OB-argument'
        before = deepcopy((self.sim.instance, self.sim.runtime, self.assessment, self.snapshot))
        head = self.engine.head
        with self.assertRaisesRegex(ValueError, '^' + re.escape('transfer cannot overwrite an existing recipient obligation') + '$'):
            self.apply()
        self.assertEqual((self.sim.instance, self.sim.runtime, self.assessment, self.snapshot), before)
        self.assertEqual(self.engine.head, head)

    def test_removed_inherited_obligation_invalidates_original_assessment(self):
        instance, runtime = self.apply()
        task = runtime['tasks'][self.task['id']]
        self.assertTrue(task_scope.assessment_current(task, instance, runtime))
        runtime['tasks'][self.recipient['id']]['completion_obligations'].pop()
        before = deepcopy((instance, runtime))
        self.assertFalse(task_scope.assessment_current(task, instance, runtime))
        self.assertEqual((instance, runtime), before)

    def test_invalidated_scope_source_invalidates_original_assessment(self):
        instance, runtime = self.apply()
        task = runtime['tasks'][self.task['id']]
        self.assertTrue(task_scope.assessment_current(task, instance, runtime))
        instance['decisions'][self.authority['id']]['source_sha256'] = 'f'*64
        before = deepcopy((instance, runtime))
        self.assertFalse(task_scope.assessment_current(task, instance, runtime))
        self.assertEqual((instance, runtime), before)

    def test_scope_decision_condition_only_applies_to_its_own_task(self):
        condition = {'op': 'decision_value_is', 'decision_id': self.authority['id'],
                     'value': deepcopy(self.authority['change'])}
        basis = [{'id': self.authority['id'], 'sha256': exact_content_hash(self.authority), 'status': None}]
        before = deepcopy((self.sim.instance, self.sim.runtime, condition))
        self.assertEqual(planning.evaluate_condition(condition, self.sim.instance, self.sim.runtime,
            evaluation_context={'task_id': self.task['id']}), {'state': 'ready', 'basis': basis, 'errors': []})
        self.assertEqual(planning.evaluate_condition(condition, self.sim.instance, self.sim.runtime,
            evaluation_context={'task_id': self.recipient['id']}), {'state': 'not_ready', 'basis': basis, 'errors': []})
        self.assertEqual((self.sim.instance, self.sim.runtime, condition), before)

    def multiple_transfer(self):
        from support.engine_lifecycle import applied, clear_work
        from support.planning_contract_inputs import produce_task
        original = deepcopy(self.task['completion_obligations'][0])
        produce_task(self.sim, revises=self.task['id'], obligations=[original, {
            **deepcopy(original), 'id': 'OB-domain', 'claim': '적용 범위도 설명한다.'}])
        self.task = only_task(self.sim)
        applied(self.sim, 'decision', config={'change': {'kind': 'task_scope', 'decision_id': 'DC-multi-transfer',
            'task_id': self.task['id'], 'disposition': 'transfer', 'revision': self.task['revision'],
            'contract_sha256': planning.contract_hash(self.task), 'obligation_ids': ['OB-argument', 'OB-domain'],
            'target_task_id': self.recipient['id'], 'reason': '서로 다른 두 의무를 같은 수신 과제에 옮긴다.'}})
        clear_work(self.sim)
        self.task = only_task(self.sim)
        self.recipient = self.sim.runtime['tasks'][self.recipient['id']]
        self.assessment = {'task_id': self.task['id'], 'decision': 'closed', 'reason': '사용자가 정한 두 의무의 양도',
            'item_dispositions': [{'obligation_id': obligation, 'kind': 'transferred', 'evidence_refs': [],
                'authority_ref': 'DC-multi-transfer', 'target_task_id': self.recipient['id'], 'target_obligation_id': target}
                for obligation, target in [('OB-argument', 'OB-inherited'), ('OB-domain', 'OB-inherited-domain')]],
            'unresolved': []}
        self.snapshot = deepcopy(self.sim.runtime['tasks'])

    def test_two_transfers_increment_recipient_once_and_preserve_both_obligations(self):
        self.multiple_transfer()
        instance, runtime = self.apply()
        target = runtime['tasks'][self.recipient['id']]
        self.assertEqual(target['revision'], self.recipient['revision'] + 1)
        self.assertEqual([row['id'] for row in target['completion_obligations']],
                         ['OB-argument', 'OB-inherited', 'OB-inherited-domain'])
        self.assertEqual([row['from_obligation_id'] for row in target['transferred_obligations']],
                         ['OB-argument', 'OB-domain'])
        self.assertEqual([(a['role'], a.get('target')) for a in runtime['queue']],
                         [('task_contract_review', target['id'])])
        self.engine.instance, self.engine.runtime = instance, runtime
        self.engine._save()
        self.sim.restart()
        self.assertEqual(self.sim.runtime['tasks'][target['id']]['completion_obligations'], target['completion_obligations'])

    def test_two_transfers_cannot_create_the_same_recipient_obligation(self):
        self.multiple_transfer()
        self.apply()
        self.assessment['item_dispositions'][1]['target_obligation_id'] = 'OB-inherited'
        before = deepcopy((self.sim.instance, self.sim.runtime, self.assessment))
        head = self.engine.head
        with self.assertRaisesRegex(ValueError, '^duplicate transferred obligation ID$'):
            self.apply()
        self.assertEqual((self.sim.instance, self.sim.runtime, self.assessment), before)
        self.assertEqual(self.engine.head, head)


class WithdrawalRecordTests(unittest.TestCase):
    def setUp(self):
        self.sim = prepared_sim()
        self.engine = self.sim.engine
        self.task = only_task(self.sim)
        _ended_execution(self.engine, 'EX-planning-plan', 'research_plan')
        self.engine._save()
        self.task = only_task(self.sim)
        self.snapshot = deepcopy(self.sim.runtime['tasks'])
        self.dispositions = [{'task_id': self.task['id'], 'disposition': 'withdraw', 'reason': '중복 의무 철회'}]

    def apply(self):
        return task_scope.apply_task_dispositions(self.sim.instance, self.sim.runtime, self.dispositions,
            execution_id='EX-planning-plan', input_tasks=self.snapshot, clock=self.sim.ports.clock)

    def test_unperformed_withdrawal_keeps_exact_residual_scope_after_restart(self):
        before = deepcopy((self.sim.instance, self.sim.runtime))
        instance, runtime = self.apply()
        identifier = self.task['id']
        task = runtime['tasks'][identifier]
        self.assertEqual(task['status'], 'closed')
        self.assertEqual(task['scope_disposition']['remaining_obligation_ids'], ['OB-argument'])
        self.assertEqual(task['scope_disposition']['previous_contract_sha256'], planning.contract_hash(self.task))
        self.assertEqual(task['scope_disposition']['cancelled_queue_actions'], [])
        self.assertEqual(task['scope_disposition']['cancelled_waiting_actions'], [])
        self.assertEqual((self.sim.instance, self.sim.runtime), before)
        self.engine.instance, self.engine.runtime = instance, runtime
        self.engine._save()
        expected = deepcopy(self.sim.runtime['tasks'][identifier])
        self.sim.restart()
        self.assertEqual(self.sim.runtime['tasks'][identifier], expected)
        self.assertIsNone(task_scope.validate_withdrawal_record(expected))

    def test_withdrawal_rejects_changed_status(self):
        instance, runtime = self.apply()
        task = runtime['tasks'][self.task['id']]
        task_scope.validate_withdrawal_record(task)
        task['status'] = 'planned'
        before = deepcopy(task)
        with self.assertRaisesRegex(ValueError, '^' + re.escape('withdrawal contract or status differs') + '$'):
            task_scope.validate_withdrawal_record(task)
        self.assertEqual(task, before)

    def test_withdrawal_rejects_changed_contract(self):
        instance, runtime = self.apply()
        task = runtime['tasks'][self.task['id']]
        task_scope.validate_withdrawal_record(task)
        task['question'] = '바뀐 질문'
        before = deepcopy(task)
        with self.assertRaisesRegex(ValueError, '^' + re.escape('withdrawal contract or status differs') + '$'):
            task_scope.validate_withdrawal_record(task)
        self.assertEqual(task, before)

    def test_withdrawal_rejects_changed_results(self):
        instance, runtime = self.apply()
        task = runtime['tasks'][self.task['id']]
        task_scope.validate_withdrawal_record(task)
        task['scope_disposition']['results_sha256'] = 'f'*64
        before = deepcopy(task)
        with self.assertRaisesRegex(ValueError, '^' + re.escape('withdrawal results changed') + '$'):
            task_scope.validate_withdrawal_record(task)
        self.assertEqual(task, before)

    def test_withdrawal_rejects_changed_residual(self):
        instance, runtime = self.apply()
        task = runtime['tasks'][self.task['id']]
        task_scope.validate_withdrawal_record(task)
        task['scope_disposition']['remaining_obligation_ids'] = []
        before = deepcopy(task)
        with self.assertRaisesRegex(ValueError, '^' + re.escape('withdrawal residual scope differs') + '$'):
            task_scope.validate_withdrawal_record(task)
        self.assertEqual(task, before)

    def test_withdrawal_rejects_producer_without_changing_state(self):
        self.task['producer_execution'] = 'EX-planning-plan'
        before = deepcopy((self.sim.instance, self.sim.runtime, self.snapshot))
        with self.assertRaisesRegex(ValueError, '^' + re.escape('task is not attributable to a research preparation execution: ' + self.task['id']) + '$'):
            self.apply()
        self.assertEqual((self.sim.instance, self.sim.runtime, self.snapshot), before)

    def test_withdrawal_rejects_snapshot_without_changing_state(self):
        self.snapshot[self.task['id']]['question'] = '이전 질문'
        before = deepcopy((self.sim.instance, self.sim.runtime, self.snapshot))
        with self.assertRaisesRegex(ValueError, '^' + re.escape('task contract changed since the execution input snapshot: ' + self.task['id']) + '$'):
            self.apply()
        self.assertEqual((self.sim.instance, self.sim.runtime, self.snapshot), before)

    def test_withdrawal_rejects_unknown_task_without_changing_state(self):
        self.dispositions[0]['task_id'] = 'TK-absent'
        before = deepcopy((self.sim.instance, self.sim.runtime, self.snapshot))
        with self.assertRaisesRegex(ValueError, '^' + re.escape('unknown task: TK-absent') + '$'):
            self.apply()
        self.assertEqual((self.sim.instance, self.sim.runtime, self.snapshot), before)

    def test_invalid_disposition_argument_shapes_do_not_change_state(self):
        before = deepcopy((self.sim.instance, self.sim.runtime))
        for execution, rows, snapshots, message in (
            ('', self.dispositions, self.snapshot, 'task dispositions need an execution ID'),
            ('EX-planning-plan', {}, self.snapshot, 'task dispositions and input tasks must be collections'),
            ('EX-planning-plan', self.dispositions, [], 'task dispositions and input tasks must be collections')):
            with self.subTest(message=message):
                with self.assertRaisesRegex(ValueError, '^' + message + '$'):
                    task_scope.apply_task_dispositions(self.sim.instance, self.sim.runtime, rows,
                        execution_id=execution, input_tasks=snapshots, clock=self.sim.ports.clock)
                self.assertEqual((self.sim.instance, self.sim.runtime), before)

    def test_performed_withdrawal_keeps_its_incomplete_assessment(self):
        assessment = returned(self.sim)
        assessment['decision'] = 'incomplete'
        assessment['item_dispositions'][0]['kind'] = 'open'
        self.engine.instance, self.engine.runtime = task_scope.apply_task_assessments(
            self.sim.instance, self.sim.runtime, [assessment], execution_id='EX-planning-plan',
            input_tasks=deepcopy(self.sim.runtime['tasks']), clock=self.sim.ports.clock)
        self.engine._save()
        self.task = only_task(self.sim)
        self.snapshot = deepcopy(self.sim.runtime['tasks'])
        prior = deepcopy(self.task['assessment'])
        instance, runtime = self.apply()
        task = runtime['tasks'][self.task['id']]
        self.assertEqual(task['assessment_history'], [prior])
        self.assertNotIn('assessment', task)
        self.assertEqual(task['scope_disposition']['assessment_sha256'], exact_content_hash(prior))
        self.assertEqual(task['scope_disposition']['remaining_obligation_ids'], ['OB-argument'])
        self.engine.instance, self.engine.runtime = instance, runtime
        self.engine._save()
        self.sim.restart()
        task = only_task(self.sim)
        self.assertIsNone(task_scope.validate_withdrawal_record(task))
        task['assessment_history'] = []
        with self.assertRaisesRegex(ValueError, '^withdrawal lacks its preserved incomplete assessment$'):
            task_scope.validate_withdrawal_record(task)

    def incomplete(self):
        assessment = returned(self.sim)
        assessment['decision'] = 'incomplete'
        assessment['item_dispositions'][0]['kind'] = 'open'
        self.engine.instance, self.engine.runtime = task_scope.apply_task_assessments(
            self.sim.instance, self.sim.runtime, [assessment], execution_id='EX-planning-plan',
            input_tasks=deepcopy(self.sim.runtime['tasks']), clock=self.sim.ports.clock)
        self.engine._save()
        self.task = only_task(self.sim)
        self.snapshot = deepcopy(self.sim.runtime['tasks'])

    def test_changed_evidence_blocks_withdrawal_even_when_contract_and_results_match(self):
        self.incomplete()
        self.sim.runtime['executions']['EX-planning-work']['error'] = '뒤늦게 보존된 실행 진단'
        before = deepcopy((self.sim.instance, self.sim.runtime))
        with self.assertRaisesRegex(ValueError, '^performed obligations need current item dispositions for all returned work$'):
            self.apply()
        self.assertEqual((self.sim.instance, self.sim.runtime), before)

    def test_changed_assessment_seal_blocks_withdrawal_before_scope_is_removed(self):
        self.incomplete()
        self.task['assessment']['contract_sha256'] = 'f'*64
        before = deepcopy((self.sim.instance, self.sim.runtime))
        with self.assertRaisesRegex(ValueError, '^item dispositions do not cover the current contract and results$'):
            self.apply()
        self.assertEqual((self.sim.instance, self.sim.runtime), before)
