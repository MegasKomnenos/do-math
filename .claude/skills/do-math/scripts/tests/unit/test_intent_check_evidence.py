"""The shared input rule distinguishes missing check evidence from actual revision."""
import unittest

from do_math.governance import import_check_input_errors


class MissingCheckInputTests(unittest.TestCase):
    def test_normal_verdicts_need_no_missing_input_process_but_unresolved_has_actual_owners(self):
        for decision, complete in (('approved', True), ('revision_required', True), ('revision_required', False)):
            self.assertEqual(import_check_input_errors({'decision': decision, 'scope_complete': complete}, {}), [])
        output = {'decision': 'unresolved', 'scope_complete': True, 'questions': ['Recover the actual source']}
        route = {'question_index': 0, 'owner': 'operations', 'target_ids': ['RI-test'],
                 'reason': 'The original reference is required', 'obligation': {'kind': 'input_retrieval',
                     'subject_ref': 'RI-test', 'requirement_ref': 'original-reference'}}
        self.assertEqual(import_check_input_errors(output, {'question_routes': [route]}), [])
        for routes in ([], [route, route], [{**route, 'target_ids': []}]):
            with self.subTest(routes=routes):
                self.assertEqual(import_check_input_errors(output, {'question_routes': routes}),
                    ['unresolved import check requires explicitly routed missing-input questions'])
        self.assertEqual(import_check_input_errors({**output, 'decision': 'approved', 'scope_complete': False}, {}),
                         ['unresolved import check requires explicitly routed missing-input questions'])
