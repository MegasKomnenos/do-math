"""현재 없어진 과제·프로필과 후속 실행을 복구 선택으로 다시 광고하지 않는다."""
from copy import deepcopy
import unittest

from do_math import input_recovery, operational_dispositions
from do_math.task_contracts import TERMINAL_TASK_STATUSES
from support.record_builders import approved_task


class RecoveryChoiceTests(unittest.TestCase):
    def test_absent_and_terminal_tasks_never_become_overflow_choices(self):
        task, instance, runtime = approved_task()
        runtime['waiting_actions'] = {'AC-size': {'kind': 'input_overflow', 'next_owner': 'research_plan',
            'action': {'role': 'research_work', 'target': task['id']}, 'question_id': 'QU-size',
            'detail': {'allowed_profile_candidates': []}}}
        for status in [None, *sorted(TERMINAL_TASK_STATUSES)]:
            with self.subTest(status=status):
                state = deepcopy(runtime)
                if status is None:
                    state['tasks'] = {}
                else:
                    state['tasks'][task['id']]['status'] = status
                before = deepcopy(state)
                self.assertEqual(input_recovery.overflow_requests(instance, state), [])
                self.assertEqual(state, before)

    def test_removed_profile_is_not_offered_and_wait_detail_is_detached(self):
        task, instance, runtime = approved_task()
        task['profile_refs'] = [{'id': 'PF-removed', 'revision': 1, 'sha256': 'b' * 64}]
        runtime['waiting_actions'] = {'AC-size': {'kind': 'input_overflow', 'next_owner': 'research_plan',
            'action': {'role': 'research_work', 'target': task['id'], 'owner_activity_id': 'AY-one',
                       'selected_contract_sha256': 'c' * 64}, 'question_id': 'QU-size',
            'detail': {'allowed_profile_candidates': ['PF-removed']}}}
        rows = input_recovery.overflow_requests(instance, runtime)
        self.assertEqual(rows, [{'action_id': 'AC-size', 'owner_activity_id': 'AY-one', 'task_id': task['id'],
            'contract_revision': task['revision'], 'contract_sha256': 'c' * 64, 'question_id': 'QU-size',
            'detail': {'allowed_profile_candidates': ['PF-removed']},
            'model_assessment': task.get('model_assessment'), 'allowed_profile_refs': []}])
        rows[0]['detail']['allowed_profile_candidates'].clear()
        self.assertEqual(runtime['waiting_actions']['AC-size']['detail']['allowed_profile_candidates'], ['PF-removed'])

    def test_unsupported_disposition_and_missing_execution_have_precise_reasons(self):
        for value in (None, [], {}, {'kind': 'made-up'}):
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, '^operational disposition kind is unsupported$'):
                    operational_dispositions.validate_disposition(value)
        with self.assertRaisesRegex(ValueError, '^operational disposition has no execution target$'):
            operational_dispositions.admissible_basis_refs({}, {'executions': {}}, {'target': 'EX-missing'})

    def test_successor_evidence_and_superseded_receipt_are_exact(self):
        runtime = {'executions': {
            'EX-old': {'id': 'EX-old', 'owner_activity_id': 'AY-one', 'status': 'ended',
                       'action': {}, 'result_ref': 'old-result', 'pending_operational_disposition': 'OD-one'},
            'EX-new': {'id': 'EX-new', 'owner_activity_id': 'AY-one', 'status': 'ended',
                       'continuation_of': 'EX-old', 'result_ref': 'new-result'}},
            'queue': [], 'checkpoints': {'EX-old': {'artifact_ref': 'checkpoint'}}}
        refs = operational_dispositions.admissible_basis_refs({}, runtime, {'target': 'EX-old',
            'observation_refs': ['OF-one'], 'obligation_ids': ['OB-one']})
        self.assertEqual(refs, sorted(['EX-old', 'EX-new', 'old-result', 'new-result', 'checkpoint', 'OF-one', 'OB-one']))
        record = {'id': 'OD-one', 'status': 'proposed', 'target_execution_id': 'EX-old', 'disposition': {'kind': 'retry'}}
        self.assertTrue(operational_dispositions.reconcile_recovery(runtime, record))
        self.assertEqual(record['result'], {'successor': {'state': 'continued', 'execution_ids': ['EX-new'],
                          'live_execution_ids': [], 'action_ids': []}})
        self.assertNotIn('pending_operational_disposition', runtime['executions']['EX-old'])
        before = deepcopy((runtime, record))
        self.assertTrue(operational_dispositions.reconcile_recovery(runtime, record))
        self.assertEqual((runtime, record), before)
