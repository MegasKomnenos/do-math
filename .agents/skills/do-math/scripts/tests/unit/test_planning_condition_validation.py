"""조건 문법과 해석기의 거부 경계: 결과·근거·입력 보존을 함께 확인한다."""
from copy import deepcopy
import re
import unittest

from do_math import planning
from do_math.canonical import exact_content_hash
from support.planning_contract_inputs import contract


def task_condition():
    return {'op': 'record_field_equals', 'space': 'runtime', 'family': 'task',
            'record_id': 'TK-planning', 'pointer': '/revision', 'value': 1}


class ConditionGrammarTests(unittest.TestCase):

    def test_rejects_extra_field_with_exact_reason(self):
        condition = {'op': 'always'}
        planning.validate_condition(condition)
        condition['args'] = []
        before = deepcopy(condition)
        with self.assertRaisesRegex(ValueError, '^' + re.escape('condition fields do not match always') + '$'):
            planning.validate_condition(condition)
        self.assertEqual(planning.evaluate_condition(condition, {}, {}),
                         {'state': 'evaluation_error', 'basis': [], 'errors': ['condition fields do not match always']})
        self.assertEqual(condition, before)

    def test_rejects_all_empty_with_exact_reason(self):
        condition = {'op': 'all', 'args': [{'op': 'always'}]}
        planning.validate_condition(condition)
        condition['args'] = []
        before = deepcopy(condition)
        with self.assertRaisesRegex(ValueError, '^' + re.escape('all requires nonempty args') + '$'):
            planning.validate_condition(condition)
        self.assertEqual(planning.evaluate_condition(condition, {}, {}),
                         {'state': 'evaluation_error', 'basis': [], 'errors': ['all requires nonempty args']})
        self.assertEqual(condition, before)

    def test_rejects_any_not_list_with_exact_reason(self):
        condition = {'op': 'any', 'args': [{'op': 'always'}]}
        planning.validate_condition(condition)
        condition['args'] = {}
        before = deepcopy(condition)
        with self.assertRaisesRegex(ValueError, '^' + re.escape('any requires nonempty args') + '$'):
            planning.validate_condition(condition)
        self.assertEqual(planning.evaluate_condition(condition, {}, {}),
                         {'state': 'evaluation_error', 'basis': [], 'errors': ['any requires nonempty args']})
        self.assertEqual(condition, before)

    def test_rejects_artifact_shape_with_exact_reason(self):
        condition = {'op': 'artifact_valid', 'artifact_ref': {'snapshot': 'a'*40, 'path': 'runtime/artifacts/BA-planning/proof.txt', 'sha256': 'b'*64}}
        planning.validate_condition(condition)
        del condition['artifact_ref']['snapshot']
        before = deepcopy(condition)
        with self.assertRaisesRegex(ValueError, '^' + re.escape('artifact_ref requires snapshot, path, sha256') + '$'):
            planning.validate_condition(condition)
        self.assertEqual(planning.evaluate_condition(condition, {}, {}),
                         {'state': 'evaluation_error', 'basis': [], 'errors': ['artifact_ref requires snapshot, path, sha256']})
        self.assertEqual(condition, before)

    def test_rejects_artifact_nontext_with_exact_reason(self):
        condition = {'op': 'artifact_valid', 'artifact_ref': {'snapshot': 'a'*40, 'path': 'runtime/artifacts/BA-planning/proof.txt', 'sha256': 'b'*64}}
        planning.validate_condition(condition)
        condition['artifact_ref']['snapshot'] = 1
        before = deepcopy(condition)
        with self.assertRaisesRegex(ValueError, '^' + re.escape('artifact reference values must be text') + '$'):
            planning.validate_condition(condition)
        self.assertEqual(planning.evaluate_condition(condition, {}, {}),
                         {'state': 'evaluation_error', 'basis': [], 'errors': ['artifact reference values must be text']})
        self.assertEqual(condition, before)

    def test_rejects_artifact_hash_with_exact_reason(self):
        condition = {'op': 'artifact_valid', 'artifact_ref': {'snapshot': 'a'*40, 'path': 'runtime/artifacts/BA-planning/proof.txt', 'sha256': 'b'*64}}
        planning.validate_condition(condition)
        condition['artifact_ref']['sha256'] = 'B'*64
        before = deepcopy(condition)
        with self.assertRaisesRegex(ValueError, '^' + re.escape('artifact hash must be lowercase SHA256') + '$'):
            planning.validate_condition(condition)
        self.assertEqual(planning.evaluate_condition(condition, {}, {}),
                         {'state': 'evaluation_error', 'basis': [], 'errors': ['artifact hash must be lowercase SHA256']})
        self.assertEqual(condition, before)

    def test_rejects_record_blank_with_exact_reason(self):
        condition = task_condition()
        planning.validate_condition(condition)
        condition['record_id'] = ' '
        before = deepcopy(condition)
        with self.assertRaisesRegex(ValueError, '^' + re.escape('condition record_id must be nonempty text') + '$'):
            planning.validate_condition(condition)
        self.assertEqual(planning.evaluate_condition(condition, {}, {}),
                         {'state': 'evaluation_error', 'basis': [], 'errors': ['condition record_id must be nonempty text']})
        self.assertEqual(condition, before)

    def test_rejects_terminal_value_with_exact_reason(self):
        condition = {'op': 'task_disposition_is', 'task_id': 'TK-planning', 'value': 'completed'}
        planning.validate_condition(condition)
        condition['value'] = 'waiting'
        before = deepcopy(condition)
        with self.assertRaisesRegex(ValueError, '^' + re.escape('task disposition must be completed or closed') + '$'):
            planning.validate_condition(condition)
        self.assertEqual(planning.evaluate_condition(condition, {}, {}),
                         {'state': 'evaluation_error', 'basis': [], 'errors': ['task disposition must be completed or closed']})
        self.assertEqual(condition, before)

    def test_rejects_pointer_prefix_with_exact_reason(self):
        condition = task_condition()
        planning.validate_condition(condition)
        condition['pointer'] = 'revision'
        before = deepcopy(condition)
        with self.assertRaisesRegex(ValueError, '^' + re.escape('record comparison needs a pointer and scalar value') + '$'):
            planning.validate_condition(condition)
        self.assertEqual(planning.evaluate_condition(condition, {}, {}),
                         {'state': 'evaluation_error', 'basis': [], 'errors': ['record comparison needs a pointer and scalar value']})
        self.assertEqual(condition, before)

    def test_rejects_comparison_nonscalar_with_exact_reason(self):
        condition = task_condition()
        planning.validate_condition(condition)
        condition['value'] = []
        before = deepcopy(condition)
        with self.assertRaisesRegex(ValueError, '^' + re.escape('record comparison needs a pointer and scalar value') + '$'):
            planning.validate_condition(condition)
        self.assertEqual(planning.evaluate_condition(condition, {}, {}),
                         {'state': 'evaluation_error', 'basis': [], 'errors': ['record comparison needs a pointer and scalar value']})
        self.assertEqual(condition, before)

    def test_rejects_unknown_space_with_exact_reason(self):
        condition = task_condition()
        planning.validate_condition(condition)
        condition['space'] = 'workspace'
        before = deepcopy(condition)
        with self.assertRaisesRegex(ValueError, '^' + re.escape('unknown condition space') + '$'):
            planning.validate_condition(condition)
        self.assertEqual(planning.evaluate_condition(condition, {}, {}),
                         {'state': 'evaluation_error', 'basis': [], 'errors': ['unknown condition space']})
        self.assertEqual(condition, before)

    def test_rejects_unknown_family_with_exact_reason(self):
        condition = task_condition()
        planning.validate_condition(condition)
        condition['family'] = 'unknown'
        before = deepcopy(condition)
        with self.assertRaisesRegex(ValueError, '^' + re.escape('unknown condition family') + '$'):
            planning.validate_condition(condition)
        self.assertEqual(planning.evaluate_condition(condition, {}, {}),
                         {'state': 'evaluation_error', 'basis': [], 'errors': ['unknown condition family']})
        self.assertEqual(condition, before)

    def test_rejects_family_space_with_exact_reason(self):
        condition = task_condition()
        planning.validate_condition(condition)
        condition['space'] = 'research'
        before = deepcopy(condition)
        with self.assertRaisesRegex(ValueError, '^' + re.escape('condition family is outside the requested space') + '$'):
            planning.validate_condition(condition)
        self.assertEqual(planning.evaluate_condition(condition, {}, {}),
                         {'state': 'evaluation_error', 'basis': [], 'errors': ['condition family is outside the requested space']})
        self.assertEqual(condition, before)

    def test_rejects_lifecycle_value_with_exact_reason(self):
        condition = {'op': 'record_lifecycle_is', 'space': 'runtime', 'family': 'task', 'record_id': 'TK-planning', 'value': 'planned'}
        planning.validate_condition(condition)
        condition['value'] = 'unknown'
        before = deepcopy(condition)
        with self.assertRaisesRegex(ValueError, '^' + re.escape('value is not a lifecycle value of this family') + '$'):
            planning.validate_condition(condition)
        self.assertEqual(planning.evaluate_condition(condition, {}, {}),
                         {'state': 'evaluation_error', 'basis': [], 'errors': ['value is not a lifecycle value of this family']})
        self.assertEqual(condition, before)

    def test_rejects_status_value_with_exact_reason(self):
        condition = {**task_condition(), 'pointer': '/status', 'value': 'planned'}
        planning.validate_condition(condition)
        condition['value'] = 'unknown'
        before = deepcopy(condition)
        with self.assertRaisesRegex(ValueError, '^' + re.escape('value is not a lifecycle value of this family') + '$'):
            planning.validate_condition(condition)
        self.assertEqual(planning.evaluate_condition(condition, {}, {}),
                         {'state': 'evaluation_error', 'basis': [], 'errors': ['value is not a lifecycle value of this family']})
        self.assertEqual(condition, before)

    def test_rejects_hidden_pointer_with_exact_reason(self):
        condition = task_condition()
        planning.validate_condition(condition)
        condition['pointer'] = '/question'
        before = deepcopy(condition)
        with self.assertRaisesRegex(ValueError, '^' + re.escape('pointer is not an exposed machine field') + '$'):
            planning.validate_condition(condition)
        self.assertEqual(planning.evaluate_condition(condition, {}, {}),
                         {'state': 'evaluation_error', 'basis': [], 'errors': ['pointer is not an exposed machine field']})
        self.assertEqual(condition, before)


class ConditionEvaluationTests(unittest.TestCase):
    def test_compounds_propagate_runtime_error_even_with_ready_child(self):
        task = contract()
        bad = {**task_condition(), 'family': 'knowledge', 'space': 'research', 'pointer': '/kind', 'value': 'theorem'}
        expected = 'existing record belongs to another family: ' + task['id']
        for condition in ({'op': 'any', 'args': [{'op': 'always'}, bad]},
                          {'op': 'all', 'args': [{'op': 'always'}, bad]}, {'op': 'not', 'arg': bad}):
            with self.subTest(condition=condition):
                before = deepcopy((condition, task))
                self.assertEqual(planning.evaluate_condition(condition, {}, {'tasks': {task['id']: task}}),
                                 {'state': 'evaluation_error', 'basis': [], 'errors': [expected]})
                self.assertEqual((condition, task), before)

    def test_absent_decision_has_an_exact_absence_basis(self):
        condition = {'op': 'decision_value_is', 'decision_id': 'DC-absent', 'value': True}
        self.assertEqual(planning.evaluate_condition(condition, {}, {}), {
            'state': 'not_ready', 'basis': [{'absencequery': {'op': 'decision_value_is', 'decision_id': 'DC-absent'}}], 'errors': []})

    def test_absent_lifecycle_record_is_not_ready(self):
        condition = {'op': 'record_lifecycle_is', 'space': 'runtime', 'family': 'task',
                     'record_id': 'TK-absent', 'value': 'completed'}
        self.assertEqual(planning.evaluate_condition(condition, {}, {}), {
            'state': 'not_ready', 'basis': [{'absencequery': {'op': 'record_lifecycle_is', 'record_id': 'TK-absent'}}], 'errors': []})

    def test_not_of_absence_is_ready_and_keeps_absence_basis(self):
        child = {'op': 'task_disposition_is', 'task_id': 'TK-absent', 'value': 'closed'}
        self.assertEqual(planning.evaluate_condition({'op': 'not', 'arg': child}, {}, {}), {
            'state': 'ready', 'basis': [{'absencequery': {'op': 'task_disposition_is', 'task_id': 'TK-absent'}}], 'errors': []})

    def test_revision_comparison_keeps_type_and_record_hash(self):
        task = contract()
        runtime = {'tasks': {task['id']: task}}
        basis = [{'id': task['id'], 'sha256': exact_content_hash(task), 'status': 'planned'}]
        before = deepcopy(runtime)
        for value, state in ((1, 'ready'), (True, 'not_ready'), (1.0, 'not_ready'), (2, 'not_ready')):
            with self.subTest(value=value):
                self.assertEqual(planning.evaluate_condition({**task_condition(), 'value': value}, {}, runtime),
                                 {'state': state, 'basis': basis, 'errors': []})
        self.assertEqual(runtime, before)

    def test_duplicate_question_link_cannot_shadow_a_task(self):
        task = contract()
        runtime = {'tasks': {task['id']: task}, 'question_links': [{'id': task['id']} ]}
        before = deepcopy(runtime)
        with self.assertRaisesRegex(ValueError, '^globally duplicate record ID: TK-planning$'):
            planning.record_index({}, runtime, question_links=True)
        self.assertEqual(runtime, before)

    def test_shared_index_failure_is_reported_by_each_evaluation(self):
        task = contract()
        runtime = {'tasks': {task['id']: task, 'duplicate': deepcopy(task)}}
        self.assertIsNone(planning._shared_index({}, runtime))
        self.assertEqual(planning.evaluate_condition({'op': 'always'}, {}, runtime), {
            'state': 'evaluation_error', 'basis': [], 'errors': ['globally duplicate record ID: TK-planning']})

    def test_pointer_decodes_tokens_and_preserves_scalar_types(self):
        value = {'a/b': {'~name': False}, 'integer': 7, 'float': 7.0, 'text': 'seven'}
        before = deepcopy(value)
        self.assertIs(planning._pointer(value, '/a~1b/~0name'), False)
        self.assertEqual(planning._pointer(value, '/integer'), 7)
        self.assertEqual(planning._pointer(value, '/float'), 7.0)
        self.assertEqual(planning._pointer(value, '/text'), 'seven')
        self.assertEqual(value, before)

    def test_pointer_rejects_missing_and_nonscalar_values(self):
        with self.assertRaisesRegex(KeyError, '/absent'):
            planning._pointer({'present': 1}, '/absent')
        for value in ({}, [], None, 1.5):
            with self.subTest(value=value):
                before = deepcopy(value)
                with self.assertRaisesRegex(ValueError, '^pointer must name a scalar machine field$'):
                    planning._pointer({'field': value}, '/field')
                self.assertEqual(value, before)

    def test_artifact_requires_both_fixed_reader_and_validator(self):
        condition = {'op': 'artifact_valid', 'artifact_ref': {'snapshot': 'a'*40,
            'path': 'runtime/artifacts/BA-planning/proof.txt', 'sha256': 'b'*64}}
        self.assertEqual(planning.evaluate_condition(condition, {}, {}), {
            'state': 'evaluation_error', 'basis': [],
            'errors': ['artifact requires a fixed-snapshot reader and format validator']})

    def test_condition_refs_traverse_all_operators_without_turning_prose_into_edges(self):
        condition = {'op': 'all', 'args': [task_condition(), {'op': 'not', 'arg': {
            'op': 'decision_value_is', 'decision_id': 'DC-one', 'value': 'TK-prose'}}]}
        before = deepcopy(condition)
        self.assertEqual(planning.condition_refs(condition), {'TK-planning', 'DC-one'})
        self.assertEqual(condition, before)

    def test_record_index_includes_only_requested_families(self):
        task = contract()
        runtime = {'tasks': {task['id']: task}}
        self.assertEqual(planning.record_index({}, runtime, families=['task']), {task['id']: ('task', task)})
        self.assertEqual(planning.record_index({}, runtime, families=[]), {})

    def test_task_reference_basis_excludes_open_status_but_binds_terminal_and_results(self):
        task = contract()
        expected = {'id': task['id'], 'contract_sha256': planning.contract_hash(task), 'result_count': 0,
                    'results_sha256': exact_content_hash([]), 'terminal': False}
        self.assertEqual(planning.task_reference_basis(task), expected)
        task['status'] = 'waiting'
        self.assertEqual(planning.task_reference_basis(task), expected)
        task['status'] = 'closed'
        self.assertEqual(planning.task_reference_basis(task), {**expected, 'terminal': True})

    def test_assigned_events_include_waiting_and_running_but_not_ended(self):
        runtime = {'queue': [{'event_refs': ['EV-queue']}],
            'waiting_actions': {'AC-wait': {'action': {'event_refs': ['EV-wait']}}, 'AC-empty': {}},
            'executions': {'EX-run': {'status': 'running', 'action': {'event_refs': ['EV-run']}},
                           'EX-end': {'status': 'ended', 'action': {'event_refs': ['EV-end']}}}}
        before = deepcopy(runtime)
        self.assertEqual(planning.assigned_event_refs(runtime), {'EV-queue', 'EV-wait', 'EV-run'})
        self.assertEqual(runtime, before)


class ClosedConditionPrefixTests(unittest.TestCase):
    def test_unknown_operator_is_rejected_before_evaluator_dispatch(self):
        import ast
        import inspect
        import textwrap
        from support.planning_paths import ExecutedLines
        source, first = inspect.getsourcelines(planning.evaluate_condition)
        function = ast.parse(textwrap.dedent(''.join(source))).body[0]
        guard = next(node for node in function.body if isinstance(node, ast.Try))
        rejected = next(node for node in guard.handlers[0].body if isinstance(node, ast.Return))
        visitor = next(node for node in function.body if isinstance(node, ast.FunctionDef) and node.name == 'visit')
        condition = {'op': 'planning_unknown_operator'}
        with ExecutedLines(planning.evaluate_condition) as reached:
            result = planning.evaluate_condition(condition, {}, {})
        self.assertEqual(result, {'state': 'evaluation_error', 'basis': [],
            'errors': ['unsupported condition op']})
        self.assertIn(first + rejected.lineno - 1, reached.lines)
        self.assertNotIn(first + visitor.lineno - 1, reached.lines)
