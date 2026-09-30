"""The runner places new-system tests in tiers by folder and selects them with --tier."""
from pathlib import Path
import sys
import unittest

SCRIPTS = Path(__file__).resolve().parents[2]
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))
import run_tests


def _case(module):
    """A test instance whose class claims to live in ``module``."""
    case = type('Case', (unittest.TestCase,), {'test_x': lambda self: None, '__module__': module})
    return case('test_x')


class TierTests(unittest.TestCase):
    def test_folder_package_decides_the_tier_group_and_legacy_modules_have_none(self):
        self.assertEqual(run_tests.folder_of(_case('structure.test_layers')), 'structure')
        self.assertEqual(run_tests.folder_of(_case('unit.test_runner_tiers')), 'unit')
        self.assertIsNone(run_tests.folder_of(_case('test_git_store')))

    def test_tier_selects_only_its_folders_and_never_legacy_modules(self):
        tests = [_case('structure.test_a'), _case('unit.test_b'), _case('sim.test_c'),
                 _case('contracts.test_d'), _case('boundary.test_e'), _case('smoke.test_f'),
                 _case('test_git_store')]
        chosen = lambda tier: sorted(run_tests.folder_of(t) for t in run_tests.select_tiers(tests, [tier]))
        self.assertEqual(chosen('T1'), ['contracts', 'structure', 'unit'])
        self.assertEqual(chosen('T2'), ['contracts', 'sim', 'structure', 'unit'])
        self.assertEqual(chosen('T4'), ['boundary'])
        self.assertEqual(chosen('T5'), ['smoke'])

    def test_discovery_reaches_the_folder_packages(self):
        discovered = run_tests.discover()
        self.assertIn('unit.test_runner_tiers.TierTests.test_discovery_reaches_the_folder_packages',
                      {test.id() for test in discovered})


class ReportTests(unittest.TestCase):
    def test_report_states_the_number_of_open_known_defects(self):
        """About 0.3 s, over the 0.2 s unit budget: it runs the runner's whole main, discovery included."""
        import json, tempfile
        from contextlib import redirect_stdout
        import io
        with tempfile.TemporaryDirectory() as directory:
            with redirect_stdout(io.StringIO()):
                code = run_tests.main(['unit.test_runner_tiers.TierTests.test_folder_package_decides_the_tier_group_and_legacy_modules_have_none',
                                       '--output', directory + '/out'])
            report = json.loads(open(directory + '/out/report.json', encoding='utf-8').read())
        self.assertEqual(code, 0)
        self.assertIn('open_known_defects', report)
        self.assertIsInstance(report['open_known_defects'], int)



class BudgetTests(unittest.TestCase):
    """Budgets are observed, not enforced per test (설계 5.2): the report lists what exceeds them."""

    BUDGETS = {'per_test_seconds': {'unit': 0.2, 'sim': 2.0}, 'tier_seconds': {'T1': 180, 'T2': 300}}

    def test_only_new_system_tests_over_their_folder_budget_are_listed(self):
        rows = [{'id': 'unit.test_a.T.test_fast', 'seconds': 0.1, 'outcome': 'passed'},
                {'id': 'unit.test_a.T.test_slow', 'seconds': 0.5, 'outcome': 'passed'},
                {'id': 'sim.test_b.T.test_slow', 'seconds': 7.0, 'outcome': 'failed'},
                {'id': 'test_legacy.T.test_slow', 'seconds': 90.0, 'outcome': 'passed'},
                {'id': 'sim.test_b.T.setUpClass', 'seconds': 9.0, 'outcome': 'passed', 'fixture': True}]
        report = run_tests.budget_report(rows, ['T2'], 400.0, self.BUDGETS)
        self.assertEqual([(row['id'], row['budget_seconds']) for row in report['over_budget']],
                         [('sim.test_b.T.test_slow', 2.0), ('unit.test_a.T.test_slow', 0.2)])
        self.assertEqual(report['tier'], {'tiers': ['T2'], 'budget_seconds': 300, 'seconds': 400.0, 'over': True})

    def test_a_run_without_a_tier_has_no_tier_budget(self):
        self.assertIsNone(run_tests.budget_report([], [], 10.0, self.BUDGETS)['tier'])
        combined = run_tests.budget_report([], ['T1', 'T2'], 250.0, self.BUDGETS)['tier']
        self.assertEqual((combined['budget_seconds'], combined['over']), (300, False))



class ParallelGroupTests(unittest.TestCase):
    def test_modules_go_longest_first_to_the_lightest_group(self):
        groups = run_tests.lpt_groups({'a': 10.0, 'b': 6.0, 'c': 5.0, 'd': 4.0, 'e': 1.0}, 2)
        self.assertEqual(groups, [['a', 'd'], ['b', 'c', 'e']])
        self.assertEqual(run_tests.lpt_groups({'a': 1.0}, 3), [['a']])
        self.assertEqual(run_tests.lpt_groups({}, 3), [])

    def test_a_module_without_a_recorded_time_is_estimated_from_its_test_count(self):
        counts = {'unit.test_x': 4, 'sim.test_y': 2}
        self.assertEqual(run_tests.module_seconds(counts, {'unit.test_x': 3.5}),
                         {'unit.test_x': 3.5, 'sim.test_y': 2 * run_tests.UNKNOWN_TEST_SECONDS})

if __name__ == '__main__':
    unittest.main()
