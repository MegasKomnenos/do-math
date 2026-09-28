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


if __name__ == '__main__':
    unittest.main()
