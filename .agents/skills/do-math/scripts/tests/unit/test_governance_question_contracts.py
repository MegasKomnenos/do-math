"""질문 생산자의 경로 불변식과 부분 해결의 정확한 효과."""
from copy import deepcopy
import unittest

from do_math import questions
from support.fakes.clock import FakeClock


class GovernanceQuestionContractTests(unittest.TestCase):
    def setUp(self):
        self.clock = FakeClock()
        self.runtime = {}
        self.row = questions.link(self.runtime, execution_id='EX-question', field='questions/0',
            owner='user', targets=['A', 'B'], blocks=True, clock=self.clock)

    def test_invalid_owner_changes_nothing(self):
        before = deepcopy(self.runtime)
        with self.assertRaisesRegex(ValueError, '^question owner and blocking decision required$'):
            questions.link(self.runtime, execution_id='EX-next', field='questions/0', owner='unknown',
                           targets=['A'], blocks=True, clock=self.clock)
        self.assertEqual(self.runtime, before)

    def test_nonboolean_blocking_changes_nothing(self):
        before = deepcopy(self.runtime)
        with self.assertRaisesRegex(ValueError, '^question owner and blocking decision required$'):
            questions.link(self.runtime, execution_id='EX-next', field='questions/0', owner='user',
                           targets=['A'], blocks=1, clock=self.clock)
        self.assertEqual(self.runtime, before)

    def test_empty_blocking_targets_change_nothing(self):
        before = deepcopy(self.runtime)
        with self.assertRaisesRegex(ValueError, '^blocking questions require explicit affected targets$'):
            questions.link(self.runtime, execution_id='EX-next', field='questions/0', owner='user',
                           targets=[], blocks=True, clock=self.clock)
        self.assertEqual(self.runtime, before)

    def test_existing_source_cannot_change_owner(self):
        before = deepcopy(self.runtime)
        with self.assertRaisesRegex(ValueError, '^question source cannot be rerouted silently$'):
            questions.link(self.runtime, execution_id='EX-question', field='questions/0', owner='research',
                           targets=['A', 'B'], blocks=True, clock=self.clock)
        self.assertEqual(self.runtime, before)

    def test_duplicate_resolution_ids_change_nothing(self):
        before = deepcopy(self.runtime)
        with self.assertRaisesRegex(ValueError, '^resolves_questions must be distinct question IDs$'):
            questions.resolve_user(self.runtime, [self.row['id']] * 2, resolution_ref='DC-answer', affected_ids=['A'])
        self.assertEqual(self.runtime, before)

    def test_unknown_resolution_changes_nothing(self):
        before = deepcopy(self.runtime)
        with self.assertRaisesRegex(ValueError, '^user decision must name an open user question: missing$'):
            questions.resolve_user(self.runtime, ['missing'], resolution_ref='DC-answer', affected_ids=['A'])
        self.assertEqual(self.runtime, before)

    def test_unrelated_answer_changes_nothing(self):
        before = deepcopy(self.runtime)
        with self.assertRaisesRegex(ValueError, '^the applied decision does not affect the question target: QU-'):
            questions.resolve_user(self.runtime, [self.row['id']], resolution_ref='DC-answer', affected_ids=['C'])
        self.assertEqual(self.runtime, before)

    def test_partial_resolution_keeps_order_and_exact_history(self):
        identifier = self.row['id']
        questions.resolve_user(self.runtime, [identifier], resolution_ref='DC-first', affected_ids=['A'])
        self.assertEqual(questions.open_targets(self.row), ['B'])
        self.assertEqual((self.row['status'], self.row['resolution_ref']), ('open', None))
        self.assertEqual(self.row['resolution_history'], [
            {'kind': 'user_decision', 'resolution_ref': 'DC-first', 'affected_ids': ['A']}])
        questions.resolve_user(self.runtime, [identifier], resolution_ref='DC-last', affected_ids=['B'])
        self.assertEqual(questions.open_links(self.runtime), [])
        self.assertEqual(self.row['resolution_history'], [
            {'kind': 'user_decision', 'resolution_ref': 'DC-first', 'affected_ids': ['A']},
            {'kind': 'user_decision', 'resolution_ref': 'DC-last', 'affected_ids': ['B']}])
        self.assertEqual((self.row['status'], self.row['resolution_ref']), ('resolved', 'DC-last'))

    def test_operations_resolution_requires_operational_role(self):
        row = questions.link(self.runtime, execution_id='EX-operation', field='questions/0',
                             owner='operations', targets=['A'], clock=self.clock)
        before = deepcopy(self.runtime)
        self.assertEqual(questions.resolution_error(row, 'research_plan'),
                         'an operations question requires an operational role')
        self.assertIsNone(questions.resolution_error(row, 'maintenance'))
        self.assertEqual(self.runtime, before)

    def test_route_index_and_unknown_target_have_exact_diagnostics(self):
        output = {'questions': ['범위는?']}
        context = {'action': {'role': 'research_plan'}, 'available_input_refs': ['A']}
        route = {'question_index': 0, 'owner': 'user', 'target_ids': ['A']}
        self.assertEqual(questions.validate_extensions(output, {'question_routes': [route]}, context), [])
        duplicate = {'question_routes': [route, deepcopy(route)]}
        self.assertEqual(questions.validate_extensions(output, duplicate, context), [
            {'path': 'question_routes', 'message': 'route each supplied question index at most once'}])
        changed = deepcopy(route)
        changed['target_ids'] = ['missing']
        self.assertEqual(questions.validate_extensions(output, {'question_routes': [changed]}, context), [
            {'path': 'question_routes', 'message': 'route targets must be IDs this input supplies or '
             'lists in its record_index, and a user question needs at least one'}])

    def test_distinct_ai_resolution_is_valid_but_duplicate_is_rejected(self):
        row = questions.link(self.runtime, execution_id='EX-research', field='questions/0',
                             owner='research', targets=['A'], clock=self.clock)
        context = {'action': {'role': 'research_plan'}, 'question_links': [row]}
        resolution = {'question_id': row['id']}
        self.assertEqual(questions.validate_extensions({}, {'question_resolutions': [resolution]}, context), [])
        self.assertEqual(questions.validate_extensions({}, {'question_resolutions': [resolution, resolution]}, context), [
            {'path': 'question_resolutions', 'message':
             'only distinct open research or operations questions can be resolved by an AI extension'}])

    def test_pending_overflow_retry_exempts_only_its_question(self):
        second = questions.link(self.runtime, execution_id='EX-second', field='questions/0', owner='user',
                                targets=['A'], blocks=True, clock=self.clock)
        action = {'id': 'A', 'role': 'research_plan',
                  'input_overflow_retry': {'question_id': self.row['id'], 'state': 'pending'}}
        self.assertEqual(questions.user_waits(action, {'id': 'I'}, self.runtime), [
            {'kind': 'user_decision', 'question_id': second['id'], 'target_ids': ['A'], 'next_owner': 'user'}])
        self.assertEqual(questions.user_waits({'id': 'A', 'role': 'maintenance'}, {'id': 'I'}, self.runtime), [])
