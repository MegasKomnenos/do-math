"""The state inspection's role input area (``state_checks.inspect_state``, ``start_import_input``; layer 2).

An AI execution without a role input manifest (no ``direct`` part) cannot have
its input bytes examined: the inspection reports it and is incomplete. The
legacy scheduler flow met this branch through synthetic initial interpretations
``EX-check`` and ``EX-interpret`` that had no manifest; the executions here are
the same two, one without the field and one with a manifest lacking ``direct``.
"""
import unittest

from do_math.state_checks import inspect_state


class RoleInputInspectionTests(unittest.TestCase):
    def test_ai_executions_without_a_role_input_manifest_leave_the_inspection_incomplete(self):
        runtime = {'executions': {'EX-check': {'id': 'EX-check', 'actor_kind': 'ai', 'status': 'ended'},
                                  'EX-interpret': {'id': 'EX-interpret', 'actor_kind': 'ai', 'status': 'ended',
                                                   'input_manifest': {'prompt': {}}}}}
        report = inspect_state({}, runtime, requested_areas=['start_import_input'])
        self.assertEqual(report['status'], 'incomplete')
        self.assertEqual(report['not_checked'], ['start_import_input'])
        self.assertEqual({row['message'] for row in report['findings']},
                         {'EX-check: role input manifest not examined', 'EX-interpret: role input manifest not examined'})
        self.assertEqual({row['status'] for row in report['findings']}, {'incomplete'})


if __name__ == '__main__':
    unittest.main()
