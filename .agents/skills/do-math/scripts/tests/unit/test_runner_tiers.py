"""The runner places new-system tests in tiers by folder and selects them with --tier."""
import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest import mock

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
                 _case('flows.test_g'), _case('test_git_store')]
        chosen = lambda tier: sorted(run_tests.folder_of(t) for t in run_tests.select_tiers(tests, [tier]))
        self.assertEqual(chosen('T1'), ['contracts', 'structure', 'unit'])
        self.assertEqual(chosen('T2'), ['contracts', 'sim', 'structure', 'unit'])
        # Flows (Sim scenarios longer than the Sim budget, 설계 6.1) run at T3 and in the default whole run.
        self.assertEqual(chosen('T3'), ['contracts', 'flows', 'sim', 'structure', 'unit'])
        self.assertIn('flows', run_tests.DEFAULT_FOLDERS)
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

    def test_a_t3_that_measured_everything_is_held_to_the_full_measurement_budget(self):
        """설계 A29: the daily incremental T3 keeps its budget; a run measuring every module has its own."""
        full = types.SimpleNamespace(mode='full')
        incremental = types.SimpleNamespace(mode='incremental')
        self.assertEqual(run_tests.budget_tiers(['T3'], {'plan': full}), ['T3_full'])
        self.assertEqual(run_tests.budget_tiers(['T3'], {'plan': incremental}), ['T3'])
        self.assertEqual(run_tests.budget_tiers(['T1', 'T2'], None), ['T1', 'T2'])
        budgets = json.loads((SCRIPTS / 'tests' / 'budgets.json').read_text(encoding='utf-8'))['tier_seconds']
        self.assertGreater(budgets['T3_full'], budgets['T3'])



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


class TimingRecordTests(unittest.TestCase):
    """Measured T3 times (2-3x, unevenly by module) stay out of the T2 balance record (결함 D11)."""

    def test_a_measured_run_keeps_its_times_apart_and_balances_by_them_with_t2_as_fallback(self):
        rows = [{'id': 'sim.test_a.T.test_x', 'seconds': 9.0, 'outcome': 'passed'}]
        root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        t2, t3 = root / 't2.json', root / 't3.json'
        t2.write_text('{"sim.test_a": 3.0, "unit.test_b": 1.0}', encoding='utf-8')
        self.enterContext(mock.patch.object(run_tests, 'TIMINGS', t2))
        self.enterContext(mock.patch.object(run_tests, 'TIMINGS_T3', t3))
        run_tests._record_timings(rows, measured=True)
        self.assertEqual(json.loads(t2.read_text(encoding='utf-8')), {'sim.test_a': 3.0, 'unit.test_b': 1.0})
        self.assertEqual(json.loads(t3.read_text(encoding='utf-8')), {'sim.test_a': 9.0})
        self.assertEqual(run_tests.recorded_seconds(measured=True), {'sim.test_a': 9.0, 'unit.test_b': 1.0})
        self.assertEqual(run_tests.recorded_seconds(measured=False), {'sim.test_a': 3.0, 'unit.test_b': 1.0})
        run_tests._record_timings(rows, measured=False)
        self.assertEqual(json.loads(t2.read_text(encoding='utf-8')), {'sim.test_a': 9.0, 'unit.test_b': 1.0})


class StoredModuleTests(unittest.TestCase):
    def test_a_module_with_a_test_that_did_not_pass_is_not_stored_so_the_next_run_measures_it_again(self):
        """A reused module does not run: a stored failure would vanish from T3 while its reach still counted."""
        chosen = {'unit.test_a': ['unit.test_a.T.test_1'], 'unit.test_b': ['unit.test_b.T.test_1', 'unit.test_b.T.test_2'],
                  'unit.test_c': ['unit.test_c.T.test_1'], 'unit.test_d': ['unit.test_d.T.test_1'],
                  'unit.test_e': ['unit.test_e.T.test_1']}
        store = {'chosen': chosen, 'partial': {'unit.test_c'},
                 'plan': types.SimpleNamespace(measure={'unit.test_a', 'unit.test_b', 'unit.test_c', 'unit.test_d'})}
        rows = [{'id': 'unit.test_a.T.test_1', 'outcome': 'passed'},
                {'id': 'unit.test_b.T.test_1', 'outcome': 'expected_failure'},
                {'id': 'unit.test_b.T.test_2', 'outcome': 'failed'},
                {'id': 'unit.test_c.T.test_1', 'outcome': 'passed'},
                {'id': 'unit.test_d.T.test_1', 'outcome': 'not_run'},
                {'id': 'setUpModule (unit.test_a)', 'outcome': 'passed', 'fixture': True}]
        self.assertEqual(run_tests.storable_modules(store, rows), {'unit.test_a': ['unit.test_a.T.test_1']})


class _NoCoverage:
    def switch_context(self, label):
        pass


class ModuleFixtureTests(unittest.TestCase):
    def test_a_measured_run_sets_up_and_tears_down_each_module_under_its_own_fixture_label(self):
        """A29: a module's fixtures belong to that module alone, so its reused measurement keeps them."""
        import types
        from support.branch_gate import FunctionRecorder, Measurement, repository_root
        seen = []
        self.enterContext(mock.patch.dict(sys.modules))
        tests = []
        for name in ('unit.test_fixture_probe_a', 'unit.test_fixture_probe_b'):
            module = types.ModuleType(name)
            module.setUpModule = lambda name=name: seen.append(('setUp ' + name, measurement.context))
            module.tearDownModule = lambda name=name: seen.append(('tearDown ' + name, measurement.context))
            sys.modules[name] = module
            case = type('Case', (unittest.TestCase,), {'test_x': lambda self: None, '__module__': name})
            tests.append(case('test_x'))
        measurement = Measurement(repository_root())
        measurement.coverage = _NoCoverage()
        measurement.calls = FunctionRecorder(str(Path(tempfile.gettempdir()) / 'no-such-prefix'), tool=4)
        measurement.calls.start()
        try:
            measurement.begin([test.id() for test in tests])
            with contextlib.redirect_stderr(io.StringIO()):
                run_tests._run_suite(tests, Path(self.enterContext(tempfile.TemporaryDirectory())) / 'run',
                                     measurement=measurement)
        finally:
            measurement.calls.stop()
        self.assertEqual(seen, [('setUp unit.test_fixture_probe_a', 'fixture:unit.test_fixture_probe_a'),
                                ('tearDown unit.test_fixture_probe_a', 'fixture:unit.test_fixture_probe_a'),
                                ('setUp unit.test_fixture_probe_b', 'fixture:unit.test_fixture_probe_b'),
                                ('tearDown unit.test_fixture_probe_b', 'fixture:unit.test_fixture_probe_b')])


class _FinishedMeasurement:
    """A measurement that has already run: ``finish`` hands back an empty coverage report."""

    def __init__(self, root):
        self.root = root

    def finish(self, directory, before_report=None):
        return {'files': {}}


class MutationIndexTests(unittest.TestCase):
    def test_a_run_that_writes_no_index_still_mutates_on_the_usable_index(self):
        """A partial T3 with --mutation-base hands mutation the fresh index it finds, not none (결함 D13)."""
        from support import branch_gate, mutation, selection
        index = {'format': selection.FORMAT, 'commit': 'c0', 'tests': [], 'files': {}}
        seen = {}

        def run(base, given, layers, root, directory, **options):
            seen['index'] = given
            return {'base': base, 'every': False, 'functions': 0, 'counts': {}, 'unreasoned_entries': 0,
                    'seconds': 0.0, 'survived': []}
        self.enterContext(mock.patch.object(selection, 'read_index', lambda: (index, '')))
        self.enterContext(mock.patch.object(selection, 'is_ancestor_of_head', lambda root: lambda commit: True))
        self.enterContext(mock.patch.object(mutation, 'run', run))
        directory = Path(self.enterContext(tempfile.TemporaryDirectory()))
        args = mock.Mock(tests=['unit.test_ids'], match=[], mutation_base='HEAD', timeout=5.0)
        result = run_tests._finish_t3(_FinishedMeasurement(branch_gate.repository_root()), directory, [], args, False)
        self.assertIsNone(result['selection_index'])
        self.assertIs(seen['index'], index)

if __name__ == '__main__':
    unittest.main()
