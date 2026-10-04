"""과제 범위의 순수 경계는 실제 생산한 계약·사용자 원천에서 검사한다."""
from copy import deepcopy
import re
import unittest

from do_math import governance, planning, task_scope
from support.planning_contract_inputs import contract, fulfilled


class WithdrawalScopeTests(unittest.TestCase):
    def test_withdrawal_scope_covers_every_task_state_and_protection_combination(self):
        """3-C/D-02: exact common scope rejection for all finite protection axes."""
        from itertools import product
        from do_math.task_contracts import LIFECYCLE_STATES
        checked = 0
        for status, user_required, academic, inherited, proposed in product(
                sorted(LIFECYCLE_STATES), (False, True), (False, True), (False, True),
                (None, 'incomplete', 'completed', 'closed')):
            task = contract()
            task.update(status=status, user_required=user_required)
            if academic:
                task['academic_requirement_id'] = 'AR-protected'
            if inherited:
                task['transferred_obligations'] = [{'obligation_id': task['completion_obligations'][0]['id']}]
            assessment = None if proposed is None else {'decision': proposed}
            snapshot = deepcopy(task)
            before = deepcopy((task, assessment))
            reason = ('withdrawal requires an unfinished task' if status in ('completed', 'closed') else
                      'withdrawal cannot follow a terminal task assessment' if proposed not in (None, 'incomplete') else
                      'protected obligations require authoritative item dispositions' if user_required or academic or inherited else None)
            with self.subTest(status=status, user_required=user_required, academic=academic,
                              inherited=inherited, proposed=proposed):
                if reason is None:
                    self.assertIsNone(task_scope.validate_withdrawal_scope(task, snapshot, proposed_assessment=assessment))
                else:
                    with self.assertRaisesRegex(ValueError, '^' + re.escape(reason) + '$'):
                        task_scope.validate_withdrawal_scope(task, snapshot, proposed_assessment=assessment)
                self.assertEqual((task, assessment), before)
            checked += 1
        self.assertEqual(checked, len(LIFECYCLE_STATES) * 2 ** 3 * 4)


    def test_rejects_terminal_scope(self):
        task = contract()
        task_scope.validate_withdrawal_scope(task, deepcopy(task))
        task['status'] = 'completed'
        snapshot = deepcopy(task)
        before = deepcopy(task)
        with self.assertRaisesRegex(ValueError, '^' + re.escape('withdrawal requires an unfinished task') + '$'):
            task_scope.validate_withdrawal_scope(task, snapshot)
        self.assertEqual(task, before)

    def test_rejects_user_required_scope(self):
        task = contract()
        task_scope.validate_withdrawal_scope(task, deepcopy(task))
        task['user_required'] = True
        snapshot = deepcopy(task)
        before = deepcopy(task)
        with self.assertRaisesRegex(ValueError, '^' + re.escape('protected obligations require authoritative item dispositions') + '$'):
            task_scope.validate_withdrawal_scope(task, snapshot)
        self.assertEqual(task, before)

    def test_rejects_academic_scope(self):
        task = contract()
        task_scope.validate_withdrawal_scope(task, deepcopy(task))
        task['academic_requirement_id'] = 'AR-protected'
        snapshot = deepcopy(task)
        before = deepcopy(task)
        with self.assertRaisesRegex(ValueError, '^' + re.escape('protected obligations require authoritative item dispositions') + '$'):
            task_scope.validate_withdrawal_scope(task, snapshot)
        self.assertEqual(task, before)

    def test_rejects_inherited_scope(self):
        task = contract()
        task_scope.validate_withdrawal_scope(task, deepcopy(task))
        task['transferred_obligations'] = [{'obligation_id': 'OB-argument'}]
        snapshot = deepcopy(task)
        before = deepcopy(task)
        with self.assertRaisesRegex(ValueError, '^' + re.escape('protected obligations require authoritative item dispositions') + '$'):
            task_scope.validate_withdrawal_scope(task, snapshot)
        self.assertEqual(task, before)

    def test_terminal_proposed_assessment_cannot_authorize_withdrawal(self):
        task = contract()
        proposed = fulfilled(task)
        before = deepcopy((task, proposed))
        with self.assertRaisesRegex(ValueError, '^withdrawal cannot follow a terminal task assessment$'):
            task_scope.validate_withdrawal_scope(task, deepcopy(task), proposed_assessment=proposed)
        self.assertEqual((task, proposed), before)

    def test_result_ids_use_execution_only_when_result_identity_is_absent(self):
        task = contract()
        task['results'] = [{'id': 'EV-one', 'execution_id': 'EX-one'}, {'execution_id': 'EX-two'}, {}]
        before = deepcopy(task)
        self.assertEqual(task_scope.result_ids(task), {'EV-one', 'EX-two'})
        self.assertEqual(task, before)

    def test_evidence_requires_record_identity_not_a_file_locator(self):
        refs = ['EX-work', 'workspace:report.md']
        before = deepcopy(refs)
        with self.assertRaisesRegex(ValueError, re.escape(
                "completion evidence requires a supplied record ID; read the file and cite its producing execution or source record; invalid_evidence_refs=['workspace:report.md']")):
            task_scope.require_evidence_refs(refs, ['EX-work'])
        self.assertEqual(refs, before)
        self.assertIsNone(task_scope.require_evidence_refs(['EX-work'], ['EX-work']))


class DecisionCurrentnessTests(unittest.TestCase):
    def source_decision(self):
        source = governance.preserve_source('GS-planning', '의무를 면제한다.', origin='user')
        decision = {'id': 'DC-planning', 'actor': 'user', 'source_ref': source['id'],
                    'source_sha256': source['sha256'], 'change': {'kind': 'task_scope'}}
        return decision, {'governance_sources': {source['id']: source}, 'sources': []}

    def test_valid_preserved_source_is_current_without_mutation(self):
        decision, instance = self.source_decision()
        before = deepcopy((decision, instance))
        self.assertTrue(task_scope.decision_is_current(decision, instance, {}))
        self.assertEqual((decision, instance), before)

    def test_nonuser_is_not_current(self):
        decision, instance = self.source_decision()
        self.assertTrue(task_scope.decision_is_current(decision, instance, {}))
        decision['actor'] = 'ai'
        before = deepcopy((decision, instance))
        self.assertFalse(task_scope.decision_is_current(decision, instance, {}))
        self.assertEqual((decision, instance), before)

    def test_source_missing_is_not_current(self):
        decision, instance = self.source_decision()
        self.assertTrue(task_scope.decision_is_current(decision, instance, {}))
        decision['source_ref'] = 'GS-absent'
        before = deepcopy((decision, instance))
        self.assertFalse(task_scope.decision_is_current(decision, instance, {}))
        self.assertEqual((decision, instance), before)

    def test_change_not_object_is_not_current(self):
        decision, instance = self.source_decision()
        self.assertTrue(task_scope.decision_is_current(decision, instance, {}))
        decision['change'] = []
        before = deepcopy((decision, instance))
        self.assertFalse(task_scope.decision_is_current(decision, instance, {}))
        self.assertEqual((decision, instance), before)

    def test_digest_changed_is_not_current(self):
        decision, instance = self.source_decision()
        self.assertTrue(task_scope.decision_is_current(decision, instance, {}))
        decision['source_sha256'] = 'f'*64
        before = deepcopy((decision, instance))
        self.assertFalse(task_scope.decision_is_current(decision, instance, {}))
        self.assertEqual((decision, instance), before)

    def test_preserved_bytes_changed_is_not_current(self):
        decision, instance = self.source_decision()
        self.assertTrue(task_scope.decision_is_current(decision, instance, {}))
        instance['governance_sources'][decision['source_ref']]['text'] = '다른 지시'
        before = deepcopy((decision, instance))
        self.assertFalse(task_scope.decision_is_current(decision, instance, {}))
        self.assertEqual((decision, instance), before)

    def test_source_callback_requires_true_and_observes_exact_decision(self):
        decision, instance = self.source_decision()
        instance['governance_sources'] = {}
        calls = []

        def accept(value):
            calls.append(deepcopy(value))
            return True

        self.assertTrue(task_scope.decision_is_current(decision, instance, {},
            evaluation_context={'validate_decision_source': accept}))
        self.assertEqual(calls, [decision])
        for reply in (False, 1, 'true'):
            with self.subTest(reply=reply):
                self.assertFalse(task_scope.decision_is_current(decision, instance, {},
                    evaluation_context={'validate_decision_source': lambda value: reply}))
