"""The runner places tests in tiers by folder and selects them with --tier."""
import contextlib
import io
import hashlib
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
from support.runner_contracts import runner_tree


def _case(module):
    """A test instance whose class claims to live in ``module``."""
    case = type('Case', (unittest.TestCase,), {'test_x': lambda self: None, '__module__': module})
    return case('test_x')


class TierTests(unittest.TestCase):
    def test_folder_package_decides_the_tier_group(self):
        self.assertEqual(run_tests.folder_of(_case('structure.test_layers')), 'structure')
        self.assertEqual(run_tests.folder_of(_case('unit.test_runner_tiers')), 'unit')
        self.assertIsNone(run_tests.folder_of(_case('outside.test_invalid')))

    def test_tier_selects_only_its_folders(self):
        tests = [_case('structure.test_a'), _case('unit.test_b'), _case('sim.test_c'),
                 _case('contracts.test_d'), _case('boundary.test_e'), _case('smoke.test_f'),
                 _case('flows.test_g'), _case('outside.test_invalid')]
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
    def test_edition_hashes_actual_python_bytes_and_ignores_docs_and_pycache(self):
        root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        package = root / 'package'
        package.mkdir()
        source = package / 'source.py'
        raw = b'VALUE = 1\r\n'
        source.write_bytes(raw)
        notes = root / 'notes.md'
        notes.write_bytes(b'first documentation')
        cache = package / '__pycache__'
        cache.mkdir()
        (cache / 'not_source.py').write_bytes(b'ignored compiled-cache directory')
        with mock.patch.object(run_tests, 'SCRIPTS', root):
            expected = {'package/source.py': hashlib.sha256(raw).hexdigest()}
            self.assertEqual(run_tests._edition(), expected)
            notes.write_bytes(b'changed documentation')
            self.assertEqual(run_tests._edition(), expected)
            changed = b'VALUE = 2\r\n'
            source.write_bytes(changed)
            self.assertEqual(run_tests._edition(), {'package/source.py': hashlib.sha256(changed).hexdigest()})
            source.unlink()
            self.assertEqual(run_tests._edition(), {})

    def test_changed_source_rejects_pass_and_does_not_publish_timing_cache(self):
        root = runner_tree(self)
        (root.parent / 'source.py').write_bytes(b'VALUE = 1\r\n')
        (root.parent / 'removed.py').write_bytes(b'old source\n')
        (root / 'unit/test_source_probe.py').write_text(
            'import unittest\nfrom pathlib import Path\n'
            'class Case(unittest.TestCase):\n'
            '    def test_value(self):\n'
            '        scripts = Path(__file__).parents[2]\n'
            "        (scripts / 'source.py').write_bytes(b'VALUE = 2\\r\\n')\n"
            "        (scripts / 'removed.py').unlink()\n"
            "        (scripts / 'added.py').write_bytes(b'new source\\n')\n", encoding='utf-8')
        before = {p.relative_to(root.parent).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                  for p in root.parent.rglob('*.py')}
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            code = run_tests.main(['unit.test_source_probe', '--jobs', '1', '--output', str(root / 'out')])
        report = json.loads((root / 'out' / 'report.json').read_text(encoding='utf-8'))
        self.assertEqual(code, 1)
        self.assertTrue(report['complete'])
        self.assertFalse(report['successful'])
        self.assertEqual(report['source_sha256'], before)
        self.assertEqual(report['changed_during_run'], ['added.py', 'removed.py', 'source.py'])
        self.assertEqual(report['selected'], ['unit.test_source_probe.Case.test_value'])
        self.assertEqual(report['counts'], {'passed': 1})
        self.assertTrue(report['reports'][0]['successful'])
        self.assertEqual(set(report['module_total_seconds']), {'unit.test_source_probe'})
        self.assertFalse((root / '.timings.json').exists())

    def test_new_and_empty_outputs_run_again_and_existing_evidence_is_never_overwritten(self):
        root = runner_tree(self)
        (root / 'unit/test_output_probe.py').write_text(
            'import unittest\nfrom pathlib import Path\n'
            'class Case(unittest.TestCase):\n'
            '    def test_value(self):\n'
            "        with (Path(__file__).parents[2] / 'invocations.txt').open('a') as stream:\n"
            "            stream.write('ran\\n')\n", encoding='utf-8')
        new, empty = root / 'new', root / 'empty'
        empty.mkdir()
        reports = []
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()) as err:
            for output in (new, empty):
                self.assertEqual(run_tests.main(['unit.test_output_probe', '--jobs', '1',
                                                 '--output', str(output)]), 0)
                raw = (output / 'report.json').read_bytes()
                reports.append(json.loads(raw))
                with self.assertRaisesRegex(SystemExit, '^2$'):
                    run_tests.main(['unit.test_output_probe', '--jobs', '1', '--output', str(output)])
                self.assertEqual((output / 'report.json').read_bytes(), raw)
        self.assertIn('--output must be new or empty; previous evidence is never overwritten', err.getvalue())
        self.assertEqual((root.parent / 'invocations.txt').read_text(), 'ran\nran\n')
        for report in reports:
            self.assertTrue(report['complete'])
            self.assertTrue(report['successful'])
            self.assertEqual(report['selected'], ['unit.test_output_probe.Case.test_value'])
            self.assertEqual([r['id'] for g in report['reports'] for r in g['rows']], report['selected'])
            self.assertEqual(report['counts'], {'passed': 1})
            self.assertEqual(report['fixture_counts'], {})
            self.assertEqual(report['changed_during_run'], [])
        self.assertEqual(reports[0]['source_sha256'], reports[1]['source_sha256'])

    def test_setup_failures_and_skips_account_for_every_selected_id_in_the_final_report(self):
        for scope in ('setUpClass', 'setUpModule'):
            for skipped in (False, True):
                with self.subTest(scope=scope, skipped=skipped):
                    root = runner_tree(self)
                    failure = "unittest.SkipTest('fixture unavailable')" if skipped else "RuntimeError('fixture broken')"
                    fixture = (f'    @classmethod\n    def setUpClass(cls): raise {failure}\n' if scope == 'setUpClass'
                               else '')
                    (root / 'unit/test_setup_probe.py').write_text(
                        'import unittest\n'
                        + (f'def setUpModule(): raise {failure}\n' if scope == 'setUpModule' else '')
                        + 'class Case(unittest.TestCase):\n' + fixture
                        + "    def test_one(self): self.fail('must not start')\n"
                        + "    def test_two(self): self.fail('must not start')\n", encoding='utf-8')
                    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                        code = run_tests.main(['unit.test_setup_probe', '--jobs', '1', '--output', str(root / 'out')])
                    report = json.loads((root / 'out/report.json').read_bytes())
                    self.assertEqual(code, 0 if skipped else 1)
                    self.assertTrue(report['complete'])
                    self.assertEqual(report['successful'], skipped)
                    selected = ['unit.test_setup_probe.Case.test_one', 'unit.test_setup_probe.Case.test_two']
                    self.assertEqual(report['selected'], selected)
                    self.assertEqual(report['counts'], {'skipped' if skipped else 'not_run': 2})
                    self.assertEqual(report['fixture_counts'], {'skipped' if skipped else 'error': 1})
                    group = report['reports'][0]
                    self.assertEqual(group['tests_run'], 0)
                    rows = [r for r in group['rows'] if not r.get('fixture')]
                    self.assertEqual([r['id'] for r in rows], selected)
                    self.assertTrue(all(r['seconds'] == 0 for r in rows))
                    fixture_row, = [r for r in group['rows'] if r.get('fixture')]
                    expected_scope = 'unit.test_setup_probe.Case' if scope == 'setUpClass' else 'unit.test_setup_probe'
                    self.assertEqual(fixture_row['id'], f'{scope} ({expected_scope})')
                    self.assertIn('fixture unavailable' if skipped else 'fixture broken', fixture_row['details'][0])
                    self.assertTrue(all('fixture unavailable' in r['details'][0] if skipped else
                                        'A fixture failed before this test could run.' == r['details'][0] for r in rows))

    def test_report_states_the_number_of_open_known_defects(self):
        """About 0.3 s, over the 0.2 s unit budget: it runs the runner's whole main, discovery included."""
        import json, tempfile
        from contextlib import redirect_stdout
        import io
        with tempfile.TemporaryDirectory() as directory:
            with redirect_stdout(io.StringIO()):
                code = run_tests.main(['unit.test_runner_tiers.TierTests.test_folder_package_decides_the_tier_group',
                                       '--output', directory + '/out'])
            report = json.loads(open(directory + '/out/report.json', encoding='utf-8').read())
        self.assertEqual(code, 0)
        self.assertEqual(set(report) & {'shards', 'shard_seconds'}, set())
        self.assertTrue(all('shard' not in group for group in report['reports']))
        self.assertEqual(report['folders'], ['unit'])
        self.assertEqual(set(report['group_seconds']), {'unit'})
        self.assertEqual([group['group'] for group in report['reports']], ['unit'])
        self.assertEqual(report['counts'], {'passed': 1})
        self.assertEqual(report['module_total_seconds'], report['reports'][0]['module_total_seconds'])
        self.assertEqual(set(report['module_total_seconds']), {'unit.test_runner_tiers'})
        self.assertEqual(report['changed_during_run'], [])
        self.assertIn('open_known_defects', report)
        self.assertIsInstance(report['open_known_defects'], int)



class BudgetTests(unittest.TestCase):
    """Budgets are observed, not enforced per test (설계 5.2): the report lists what exceeds them."""

    BUDGETS = {'per_test_seconds': {'unit': 0.2, 'sim': 2.0}, 'tier_seconds': {'T1': 180, 'T2': 300}}

    def test_only_tests_over_their_folder_budget_are_listed(self):
        rows = [{'id': 'unit.test_a.T.test_fast', 'seconds': 0.1, 'outcome': 'passed'},
                {'id': 'unit.test_a.T.test_slow', 'seconds': 0.5, 'outcome': 'passed'},
                {'id': 'sim.test_b.T.test_slow', 'seconds': 7.0, 'outcome': 'failed'},
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


class ModuleCostTests(unittest.TestCase):
    def test_unmeasured_module_preparation_cost_reaches_cache_and_lpt(self):
        # Body-only costs would put a+c together (102 seconds) and b alone (8).
        # Actual fixture-inclusive costs put a alone (95), b+c together (15).
        clock = types.SimpleNamespace(value=0)
        def advance(seconds):
            clock.value += seconds
        root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.enterContext(mock.patch.object(run_tests, 'TIMINGS', root / 'times.json'))
        self.enterContext(mock.patch.object(run_tests, 'time', types.SimpleNamespace(monotonic=lambda: clock.value)))
        self.enterContext(mock.patch.dict(sys.modules))
        tests = []
        for name, prep, body in [('a', 90, 5), ('b', 0, 8), ('c', 0, 7)]:
            module = types.ModuleType('unit.test_cost_' + name)
            module.setUpModule = lambda prep=prep: advance(prep)
            sys.modules[module.__name__] = module
            case = type('Case', (unittest.TestCase,), {
                '__module__': module.__name__, 'test_x': lambda self, body=body: advance(body)})
            tests.append(case('test_x'))
        with contextlib.redirect_stderr(io.StringIO()):
            report = run_tests._run_suite(tests, root / 'run')
        row_costs = {row['id'].rsplit('.', 2)[0]: row['seconds'] for row in report['rows']}
        self.assertEqual(sum(row_costs.values()), 20)
        self.assertEqual(run_tests.lpt_groups(row_costs, 2),
                         [['unit.test_cost_b'], ['unit.test_cost_c', 'unit.test_cost_a']])
        totals = report['module_total_seconds']
        self.assertEqual(totals, {'unit.test_cost_a': 95, 'unit.test_cost_b': 8, 'unit.test_cost_c': 7})
        self.assertEqual(sum(totals.values()) - sum(row_costs.values()), 90)
        run_tests._record_timings(totals, measured=False)
        costs = run_tests.module_seconds(dict.fromkeys(totals, 1), run_tests.recorded_seconds(False))
        self.assertEqual(costs, totals)
        from support import mutation
        raw_cache = json.loads((root / 'times.json').read_text(encoding='utf-8'))
        self.assertEqual(mutation.expected_seconds({'tests': [], 'folders': ['unit']}, raw_cache), 110)
        self.assertEqual([test.id() for test in mutation.cheapest_first(tests, raw_cache)],
                         [tests[2].id(), tests[1].id(), tests[0].id()])
        self.assertEqual(run_tests.lpt_groups(costs, 2),
                         [['unit.test_cost_a'], ['unit.test_cost_b', 'unit.test_cost_c']])


class TimingRecordTests(unittest.TestCase):
    """Measured T3 times (2-3x, unevenly by module) stay out of the T2 balance record (결함 D11)."""

    def test_a_partial_public_selection_reports_its_cost_without_replacing_the_whole_module_cost(self):
        root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        clock = types.SimpleNamespace(value=0)
        def advance(seconds):
            clock.value += seconds
        module = types.ModuleType('unit.test_cost_scope_probe')
        module.setUpModule = lambda: advance(7)
        case = type('Case', (unittest.TestCase,), {
            '__module__': module.__name__,
            'test_short': lambda self: advance(1), 'test_long': lambda self: advance(9)})
        tests = [case('test_short'), case('test_long')]
        self.enterContext(mock.patch.dict(sys.modules, {module.__name__: module}))
        self.enterContext(mock.patch.object(run_tests, 'discover', return_value=tests))
        self.enterContext(mock.patch.object(run_tests, 'TIMINGS', root / 'times.json'))
        self.enterContext(mock.patch.object(run_tests, 'time', types.SimpleNamespace(monotonic=lambda: clock.value)))
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(run_tests.main([module.__name__, '--output', str(root / 'whole')]), 0)
            whole = json.loads((root / 'times.json').read_text(encoding='utf-8'))
            self.assertEqual(whole[module.__name__], 17)
            self.assertEqual(run_tests.main([tests[0].id(), '--output', str(root / 'partial')]), 0)
        partial = json.loads((root / 'partial/report.json').read_text(encoding='utf-8'))
        self.assertEqual(partial['counts'], {'passed': 1})
        self.assertEqual(partial['module_total_seconds'], {module.__name__: 8})
        self.assertEqual(json.loads((root / 'times.json').read_text(encoding='utf-8')), whole)

    def test_measured_and_unmeasured_module_totals_have_separate_cost_populations(self):
        root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.enterContext(mock.patch.object(run_tests, 'TIMINGS', root / 't2.json'))
        self.enterContext(mock.patch.object(run_tests, 'TIMINGS_T3', root / 't3.json'))
        run_tests._record_timings({'sim.test_a': 3.0, 'unit.test_b': 1.0}, measured=False)
        run_tests._record_timings({'sim.test_a': 9.0}, measured=True)
        self.assertEqual(run_tests.recorded_seconds(True), {'sim.test_a': 9.0})
        self.assertEqual(run_tests.recorded_seconds(False), {'sim.test_a': 3.0, 'unit.test_b': 1.0})
        self.assertEqual(run_tests.module_seconds({'unit.test_b': 2}, run_tests.recorded_seconds(True)),
                         {'unit.test_b': 2 * run_tests.UNKNOWN_TEST_SECONDS})
        run_tests._record_timings({'sim.test_a': 4.0}, measured=False)
        self.assertEqual(run_tests.recorded_seconds(False), {'sim.test_a': 4.0, 'unit.test_b': 1.0})
        self.assertEqual(json.loads((root / 't2.json').read_text(encoding='utf-8')),
                         {'_cost_basis': 'module_total_seconds', 'sim.test_a': 4.0, 'unit.test_b': 1.0})

    def test_body_only_cache_is_invalidated_without_inventing_module_totals(self):
        root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        path = root / 'times.json'
        path.write_text('{"sim.test_old": 123}', encoding='utf-8')
        self.enterContext(mock.patch.object(run_tests, 'TIMINGS', path))
        self.assertEqual(run_tests.recorded_seconds(False), {})
        run_tests._record_timings({'unit.test_new': 5.0})
        self.assertEqual(run_tests.recorded_seconds(False), {'unit.test_new': 5.0})


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
    def test_both_modes_preserve_order_fixture_counts_and_complete_module_costs(self):
        from support.branch_gate import FunctionRecorder, Measurement
        for measured in (False, True):
            with self.subTest(measured=measured), mock.patch.dict(sys.modules):
                events, tests = [], []
                clock = types.SimpleNamespace(value=0)
                def event(label, cost):
                    events.append(label)
                    clock.value += cost
                expected = []
                classes = {}
                for name in ('unit.test_cost_a', 'unit.test_cost_b'):
                    module = types.ModuleType(name)
                    module.setUpModule = lambda name=name: event(name + ':module setup', 2)
                    module.tearDownModule = lambda name=name: event(name + ':module teardown', 11)
                    sys.modules[name] = module
                    expected.append(name + ':module setup')
                    for label in ('A', 'B'):
                        prefix = name + ':' + label
                        case = type(label, (unittest.TestCase,), {
                            '__module__': name,
                            'setUpClass': classmethod(lambda cls, p=prefix: event(p + ':setup', 3)),
                            'tearDownClass': classmethod(lambda cls, p=prefix: event(p + ':teardown', 7)),
                            'test_x': lambda self, p=prefix: event(p + ':x', 5),
                            'test_y': lambda self, p=prefix: event(p + ':y', 5)})
                        classes[name, label] = case
                        tests.extend([case('test_x'), case('test_y')])
                        expected.extend(prefix + ':' + phase for phase in ('setup', 'x', 'y', 'teardown'))
                    expected.append(name + ':module teardown')
                # Noncontiguous recurrence preserves order and repeats fixtures, as unittest does.
                tests.append(classes['unit.test_cost_a', 'A']('test_x'))
                expected.extend(['unit.test_cost_a:module setup', 'unit.test_cost_a:A:setup',
                                 'unit.test_cost_a:A:x', 'unit.test_cost_a:A:teardown',
                                 'unit.test_cost_a:module teardown'])
                measurement = None
                if measured:
                    measurement = Measurement(Path(__file__).resolve().parents[6])
                    measurement.coverage = _NoCoverage()
                    measurement.calls = FunctionRecorder(str(Path(tempfile.gettempdir()) / 'no-such-prefix'), tool=4)
                    measurement.calls.start()
                    measurement.begin([test.id() for test in tests])
                try:
                    with tempfile.TemporaryDirectory() as root, contextlib.redirect_stderr(io.StringIO()), \
                            mock.patch.object(run_tests, 'time', types.SimpleNamespace(monotonic=lambda: clock.value)):
                        report = run_tests._run_suite(tests, Path(root), checkpoint=True, measurement=measurement)
                        self.assertEqual(report['module_total_seconds'], {'unit.test_cost_a': 81, 'unit.test_cost_b': 53})
                        self.assertEqual(report['tests_run'], 9)
                        self.assertTrue(report['successful'])
                        progress = [json.loads(path.read_text(encoding='utf-8')) for path in sorted(Path(root).glob('progress-*.json'))]
                        self.assertEqual([r['phase'] for r in progress], ['test', 'fixture_or_shutdown'] * 9)
                        self.assertEqual([r['sequence'] for r in progress], list(range(1, 19)))
                finally:
                    if measured:
                        measurement.calls.stop()
                self.assertEqual(events, expected)

    def test_fixture_errors_and_skips_keep_their_outcomes_and_observed_cost(self):
        for scope in ('setUpModule', 'setUpClass', 'tearDownClass', 'tearDownModule'):
            for skipped in (False, True):
                with self.subTest(scope=scope, skipped=skipped), mock.patch.dict(sys.modules):
                    clock = types.SimpleNamespace(value=0)
                    module = types.ModuleType('unit.test_cost_failure')
                    def fail(*args):
                        clock.value += 13
                        raise unittest.SkipTest('fixture skip') if skipped else RuntimeError('fixture error')
                    case = type('Case', (unittest.TestCase,), {'__module__': module.__name__, 'test_x': lambda self: None})
                    if 'Class' in scope:
                        setattr(case, scope, classmethod(fail))
                    else:
                        setattr(module, scope, fail)
                    sys.modules[module.__name__] = module
                    with tempfile.TemporaryDirectory() as root, contextlib.redirect_stderr(io.StringIO()), \
                            mock.patch.object(run_tests, 'time', types.SimpleNamespace(monotonic=lambda: clock.value)):
                        report = run_tests._run_suite([case('test_x')], Path(root))
                        fixtures = [r for r in report['rows'] if r.get('fixture')]
                        rows = [r for r in report['rows'] if not r.get('fixture')]
                        self.assertEqual([r['outcome'] for r in fixtures], ['skipped' if skipped else 'error'])
                        self.assertEqual([r['outcome'] for r in rows],
                                         ['skipped' if skipped else 'not_run'] if scope.startswith('setUp') else ['passed'])
                        self.assertEqual(report['module_total_seconds'], {module.__name__: 13})
                        self.assertEqual(report['tests_run'], 0 if scope.startswith('setUp') else 1)
                        if not skipped:
                            evidence = list((Path(root) / 'failures').glob('*.json'))
                            self.assertEqual(len(evidence), 1)
                            self.assertEqual(json.loads(evidence[0].read_text(encoding='utf-8'))['test']['outcome'], 'error')

    def test_stopped_or_interrupted_modules_are_not_filled_from_rows(self):
        for interrupted in (False, True):
            with self.subTest(interrupted=interrupted), tempfile.TemporaryDirectory() as root:
                clock = types.SimpleNamespace(value=0)
                def body(case):
                    clock.value += 17
                    if interrupted:
                        raise KeyboardInterrupt()
                    case._outcome.result.stop()
                first = type('First', (unittest.TestCase,), {'__module__': 'unit.test_started', 'test_x': body})
                later = type('Later', (unittest.TestCase,), {'__module__': 'unit.test_absent', 'test_x': lambda case: case.fail()})
                with contextlib.redirect_stderr(io.StringIO()), \
                        mock.patch.object(run_tests, 'time', types.SimpleNamespace(monotonic=lambda: clock.value)):
                    if interrupted:
                        with self.assertRaisesRegex(KeyboardInterrupt, '^$'):
                            run_tests._run_suite([first('test_x'), later('test_x')], Path(root), checkpoint=True)
                        report = json.loads((Path(root) / 'result.json').read_text(encoding='utf-8'))
                        self.assertEqual(report['module_total_seconds'], {})
                    else:
                        report = run_tests._run_suite([first('test_x'), later('test_x')], Path(root), checkpoint=True)
                        self.assertEqual(report['module_total_seconds'], {'unit.test_started': 17})
                        self.assertEqual([r['outcome'] for r in report['rows']], ['passed', 'not_run'])

    def test_a_measured_run_sets_up_and_tears_down_each_module_under_its_own_fixture_label(self):
        """A29: a module's fixtures belong to that module alone, so its reused measurement keeps them."""
        import types
        from support.branch_gate import FunctionRecorder, Measurement
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
        measurement = Measurement(Path(__file__).resolve().parents[6])
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
    def test_branch_success_cannot_hide_missing_mutation_measurement(self):
        from support import branch_gate, mutation, selection
        gate = {'passed': True, 'judged_modules': 1, 'modules_with_gaps': 0,
                'missing_branches': 0, 'missing_lines': 0, 'excluded_lines': 0, 'unmeasured_modules': []}
        self.enterContext(mock.patch.object(branch_gate, 'gate', lambda *args: gate))
        self.enterContext(mock.patch.object(selection, 'read_index', lambda: (None, 'missing')))
        self.enterContext(mock.patch.object(selection, 'is_ancestor_of_head', lambda root: lambda commit: True))
        directory = Path(self.enterContext(tempfile.TemporaryDirectory()))
        args = mock.Mock(tests=['unit.test_ids'], match=[], mutation_base='HEAD')
        for status in ('execution_error', 'mutation_error', 'not_executed', 'baseline_failing'):
            with self.subTest(status=status):
                report = {'base': 'HEAD', 'every': True, 'functions': 1, 'counts': {status: 1},
                          'unreasoned_entries': 0, 'baseline_failing': [], 'seconds': 0.0, 'survived': []}
                with mock.patch.object(mutation, 'run', lambda *args, **options: report):
                    result = run_tests._finish_t3(_FinishedMeasurement(Path(__file__).resolve().parents[6]),
                                                  directory, [], args, False)
                self.assertTrue(result['branch_gate']['passed'])
                self.assertFalse(result['passed'])
                self.assertEqual(result['mutation']['counts'], {status: 1})

    def test_a_run_that_writes_no_index_still_mutates_on_the_usable_index(self):
        """A partial T3 with --mutation-base hands mutation the fresh index it finds, not none (결함 D13)."""
        from support import branch_gate, mutation, selection
        index = {'format': selection.FORMAT, 'commit': 'c0', 'tests': [], 'files': {}}
        seen = {}

        def run(base, given, layers, root, directory, **options):
            seen['index'] = given
            return {'base': base, 'every': False, 'functions': 0, 'counts': {}, 'unreasoned_entries': 0,
                    'seconds': 0.0, 'survived': [], 'baseline_failing': []}
        self.enterContext(mock.patch.object(selection, 'read_index', lambda: (index, '')))
        self.enterContext(mock.patch.object(selection, 'is_ancestor_of_head', lambda root: lambda commit: True))
        self.enterContext(mock.patch.object(mutation, 'run', run))
        directory = Path(self.enterContext(tempfile.TemporaryDirectory()))
        args = mock.Mock(tests=['unit.test_ids'], match=[], mutation_base='HEAD')
        result = run_tests._finish_t3(_FinishedMeasurement(Path(__file__).resolve().parents[6]), directory, [], args, False)
        self.assertIsNone(result['selection_index'])
        self.assertIs(seen['index'], index)

if __name__ == '__main__':
    unittest.main()
