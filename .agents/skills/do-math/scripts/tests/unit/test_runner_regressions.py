"""Runner reporting, selection and ownership decisions using small synthetic inputs."""
from contextlib import redirect_stderr, redirect_stdout
import io
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import run_tests
from test_categories import isolation_for, test_group as category
from support.runner_contracts import runner_tree


class RunnerTests(unittest.TestCase):
    def test_worker_preserves_checkpoint_publication_traceback_without_completing_report(self):
        class Specimen(unittest.TestCase):
            def test_value(self): self.assertEqual(2 + 2, 4)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            specimen = Specimen('test_value')
            run_tests._write_json(root / 'requested.json', [specimen.id()])
            failure = OSError(13, 'injected checkpoint publication failure', str(root / 'result.json'))
            write_json = run_tests._write_json
            def publish(path, value):
                if path.name == 'result.json' and value['rows'][-1]['outcome'] == 'passed':
                    raise failure
                return write_json(path, value)
            with mock.patch.object(sys, 'path', sys.path.copy()), \
                    mock.patch.object(unittest.TestLoader, 'loadTestsFromNames',
                                      return_value=unittest.TestSuite([specimen])), \
                    mock.patch.object(run_tests, '_write_json', side_effect=publish):
                with self.assertRaises(OSError) as caught:
                    run_tests._worker(root)
            self.assertIs(caught.exception, failure)
            report = run_tests._read_json(root / 'result.json')
            self.assertFalse(report['complete'])
            self.assertFalse(report['successful'])
            self.assertEqual(report['rows'][-1]['outcome'], 'running')
            self.assertFalse((root / 'progress-000002.json').exists())
            retained = (root / 'stderr.txt').read_text(encoding='utf-8')
            self.assertIn('... ok', retained)
            self.assertIn('Traceback (most recent call last):', retained)
            self.assertIn(str(failure), retained)
            self.assertIn('stopTest', retained)

    def test_worker_keeps_completed_success_and_test_failure_exit_contracts(self):
        class Specimen(unittest.TestCase):
            def test_pass(self): self.assertEqual(2 + 2, 4)
            def test_fail(self): self.fail('ordinary test failure')
        for method, code, outcome in [('test_pass', 0, 'passed'), ('test_fail', 1, 'failed')]:
            with self.subTest(outcome=outcome), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                specimen = Specimen(method)
                run_tests._write_json(root / 'requested.json', [specimen.id()])
                with mock.patch.object(sys, 'path', sys.path.copy()), \
                        mock.patch.object(unittest.TestLoader, 'loadTestsFromNames',
                                          return_value=unittest.TestSuite([specimen])):
                    self.assertEqual(run_tests._worker(root), code)
                report = run_tests._read_json(root / 'result.json')
                self.assertTrue(report['complete'])
                self.assertEqual(report['successful'], code == 0)
                self.assertEqual(report['rows'][0]['outcome'], outcome)

    def test_failure_is_readable_while_the_next_test_runs_before_group_completion(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            observations = []
            class Failed(unittest.TestCase):
                def test_first(self): self.fail('preserve this exact failure')
            class Following(unittest.TestCase):
                def test_next(self):
                    records = list((root / 'failures').glob('*.json'))
                    self.assertEqual(len(records), 1)
                    row = json.loads(records[0].read_bytes())
                    self.assertFalse(row['complete'])
                    self.assertEqual(row['test']['id'], first.id())
                    self.assertEqual(row['test']['outcome'], 'failed')
                    self.assertIn('preserve this exact failure', row['test']['details'][0])
                    self.assertFalse((root / 'result.json').exists())
                    observations.append(row)
            first = Failed('test_first')
            result = unittest.TextTestRunner(stream=io.StringIO(), resultclass=lambda *a, **k:
                run_tests.TimedResult(*a, directory=root, **k)).run(unittest.TestSuite([
                    first, Following('test_next')]))
            self.assertEqual(len(observations), 1)
            self.assertEqual(len(result.failures), 1)
            self.assertFalse(result.wasSuccessful())

    def test_isolation_label_is_inherited_and_a_method_label_overrides_its_class(self):
        @category('lean')
        class Base(unittest.TestCase):
            def test_compiler(self): self.fail('label specimen must not run')
            @category('resource')
            def test_job(self): self.fail('label specimen must not run')
        class Child(Base): pass
        class Plain(unittest.TestCase):
            def test_rule(self): self.fail('label specimen must not run')
            @category('resource')
            def test_process(self): self.fail('label specimen must not run')
        self.assertEqual(isolation_for(Child('test_compiler')), 'lean')
        self.assertEqual(isolation_for(Child('test_job')), 'resource')
        self.assertIsNone(isolation_for(Plain('test_rule')))
        self.assertEqual(isolation_for(Plain('test_process')), 'resource')
        with self.assertRaisesRegex(ValueError, '^unknown test label: unit$'):
            category('unit')

    def test_every_disk_module_is_discovered_with_its_qualified_folder_name(self):
        """Real population check, not a comparison with a second registration list (K-02/K-68)."""
        expected = {'.'.join(path.relative_to(run_tests.TESTS).with_suffix('').parts)
                    for path in run_tests.TESTS.rglob('test_*.py')}
        discovered = run_tests.discover()
        self.assertEqual({run_tests.module_of(test) for test in discovered}, expected)
        self.assertEqual(len({test.id() for test in discovered}), len(discovered))
        self.assertTrue(all(run_tests.folder_of(test) in run_tests.FOLDERS for test in discovered))

    def _tree(self):
        return runner_tree(self)

    def _module(self, root, name):
        path = root / name
        path.write_text('import unittest\nclass Case(unittest.TestCase):\n'
                        '    def test_value(self): self.assertEqual(2 + 2, 4)\n', encoding='utf-8')
        return path

    def _listing(self, arguments):
        with redirect_stdout(io.StringIO()) as out, redirect_stderr(io.StringIO()) as err:
            code = run_tests.main(['--list', *arguments])
        return code, out.getvalue(), err.getvalue()

    def test_folder_selection_keeps_same_named_modules_distinct_and_has_no_short_alias(self):
        root = self._tree()
        for folder in ('unit', 'sim', 'boundary'):
            self._module(root, folder + '/test_same.py')
        code, out, err = self._listing(['unit', 'sim.test_same.Case.test_value'])
        self.assertEqual((code, err), (0, ''))
        self.assertEqual(out.splitlines(), ['sim\tsim.test_same.Case.test_value',
                                           'unit\tunit.test_same.Case.test_value'])
        code, out, err = self._listing(['test_same'])
        self.assertEqual((code, out), (2, ''))
        self.assertIn('No test matches: test_same', err)
        code, out, err = self._listing([])
        self.assertEqual((code, err), (0, ''))
        self.assertNotIn('boundary', out)
        self.assertEqual(len(out.splitlines()), 2)
        code, out, err = self._listing(['--tier', 'T4'])
        self.assertEqual((code, out, err), (0, 'boundary\tboundary.test_same.Case.test_value\n', ''))
        code, out, err = self._listing(['unit.test_same.Case.test_value', '--tier', 'T1',
                                       '--tier', 'T2', '--match', '*test_value', '--match', '*absent'])
        self.assertEqual((code, out, err), (0, 'unit\tunit.test_same.Case.test_value\n', ''))
        code, out, err = self._listing(['sim', '--tier', 'T1'])
        self.assertEqual((code, out), (2, ''))
        self.assertIn('No tests selected; no pass was established.', err)

    def test_missing_folder_package_or_nested_package_refuses_even_a_valid_selection(self):
        root = self._tree()
        self._module(root, 'unit/test_present.py')
        marker = root / 'sim' / '__init__.py'
        marker.unlink()
        code, out, err = self._listing(['unit'])
        self.assertEqual((code, out), (2, ''))
        self.assertIn('Missing test folder/package: sim', err)
        (root / 'sim').rmdir()
        code, out, err = self._listing(['unit'])
        self.assertEqual((code, out), (2, ''))
        self.assertIn('Missing test folder/package: sim', err)
        marker.parent.mkdir()
        marker.write_text('', encoding='utf-8')
        (root / 'unit' / 'nested').mkdir()
        self._module(root, 'unit/nested/test_lost.py')
        code, out, err = self._listing(['unit.test_present'])
        self.assertEqual((code, out), (2, ''))
        self.assertIn('Missing test package: unit/nested', err)

    def test_folderless_or_unclassified_test_file_refuses_the_selection(self):
        root = self._tree()
        self._module(root, 'unit/test_present.py')
        for relative in ('test_stray.py', 'other/test_stray.py'):
            with self.subTest(path=relative):
                (root / relative).parent.mkdir(exist_ok=True)
                path = self._module(root, relative)
                code, out, err = self._listing(['unit'])
                self.assertEqual((code, out), (2, ''))
                self.assertIn('Test outside tier folders: ' + relative, err)
                path.unlink()

    def test_a_module_omitted_by_discovery_cannot_silently_shrink_the_population(self):
        root = self._tree()
        self._module(root, 'unit/test_present.py')
        path = self._module(root, 'sim/test_omitted.py')
        with path.open('a', encoding='utf-8') as stream:
            stream.write('def load_tests(loader, tests, pattern): return unittest.TestSuite()\n')
        code, out, err = self._listing(['unit'])
        self.assertEqual((code, out), (2, ''))
        self.assertIn('Test population mismatch. Missing: sim.test_omitted', err)

    def test_a_ghost_module_returned_by_load_tests_refuses_even_a_valid_selection(self):
        root = self._tree()
        self._module(root, 'unit/test_present.py')
        path = self._module(root, 'sim/test_extra.py')
        with path.open('a', encoding='utf-8') as stream:
            stream.write("Ghost = type('Ghost', (Case,), {'__module__': 'sim.test_ghost'})\n"
                         'def load_tests(loader, tests, pattern):\n'
                         "    tests.addTest(Ghost('test_value'))\n"
                         '    return tests\n')
        code, out, err = self._listing(['unit.test_present'])
        self.assertEqual((code, out), (2, ''))
        self.assertIn('Test population mismatch. Missing: ; unexpected: sim.test_ghost', err)

    def test_duplicate_ids_and_import_failures_refuse_selection(self):
        root = self._tree()
        path = self._module(root, 'unit/test_duplicate.py')
        with path.open('a', encoding='utf-8') as stream:
            stream.write('Alias = Case\n')
        code, out, err = self._listing(['unit'])
        self.assertEqual((code, out), (2, ''))
        self.assertIn('Duplicate test IDs: unit.test_duplicate.Case.test_value', err)
        self._module(root, 'sim/test_broken.py').write_text('raise ImportError("broken specimen")', encoding='utf-8')
        code, out, err = self._listing(['unit'])
        self.assertEqual((code, out), (2, ''))
        self.assertIn('broken specimen', err)

    def test_removed_shard_option_and_empty_selection_are_rejected(self):
        with redirect_stderr(io.StringIO()) as err, self.assertRaisesRegex(SystemExit, '^2$'):
            run_tests.main(['--shard', 'unit'])
        self.assertIn('unrecognized arguments: --shard', err.getvalue())
        root = self._tree()
        self._module(root, 'unit/test_present.py')
        code, out, err = self._listing(['unit', '--match', '*no_such_test'])
        self.assertEqual((code, out), (2, ''))
        self.assertIn('No tests selected; no pass was established.', err)

    def test_positional_ids_select_a_module_class_or_method_without_prefix_collisions(self):
        """About 0.8 s: two real discoveries test selection without substituting the runner."""
        with redirect_stdout(io.StringIO()) as out, redirect_stderr(io.StringIO()):
            self.assertEqual(run_tests.main(['--list', 'unit.test_runner_regressions.RunnerTests']), 0)
        rows = out.getvalue().splitlines()
        self.assertTrue(rows)
        self.assertTrue(all(row.split('\t')[1].startswith('unit.test_runner_regressions.RunnerTests.') for row in rows))
        self.assertTrue(all(row.split('\t')[0] == 'unit' for row in rows))
        with redirect_stdout(io.StringIO()) as out, redirect_stderr(io.StringIO()):
            run_tests.main(['--list', 'boundary.test_engine_cli'])
        # boundary.test_engine_cli_advanced and ..._control_shapes share the name as a prefix. The
        # example is a new-system module, which 1f does not delete (the old test_knowledge was).
        rows = out.getvalue().splitlines()
        self.assertTrue(rows)
        self.assertTrue(all(row.split('\t')[1].rsplit('.', 2)[0] == 'boundary.test_engine_cli' for row in rows))

    def test_an_id_that_matches_no_test_refuses_the_whole_selection(self):
        """About 0.4 s: real discovery must refuse the valid and unknown ID together."""
        # A mistyped ID beside valid ones must not drop out and leave the rest to read as a pass.
        with redirect_stdout(io.StringIO()) as out, redirect_stderr(io.StringIO()) as err:
            self.assertEqual(run_tests.main(['--list', 'unit.test_runner_regressions', 'test_no_such_module']), 2)
        self.assertEqual(out.getvalue(), '')
        self.assertIn('test_no_such_module', err.getvalue())

    def test_failing_subtest_remains_a_failure_in_the_machine_report(self):
        class Specimen(unittest.TestCase):
            def test_cases(self):
                with self.subTest(value='failure'):
                    self.assertEqual(1, 2)
                with self.subTest(value='success'):
                    self.assertEqual(1, 1)
        with tempfile.TemporaryDirectory() as directory:
            result = unittest.TextTestRunner(stream=io.StringIO(), resultclass=lambda *a, **k:
                run_tests.TimedResult(*a, directory=Path(directory), **k)).run(unittest.TestSuite([
                    Specimen('test_cases')]))
            report = result.preserve(complete=True)
        self.assertFalse(report['successful'])
        self.assertEqual(report['rows'][0]['outcome'], 'failed')
        self.assertIn('failure', report['rows'][0]['details'][0])

    def test_worker_wait_has_no_elapsed_deadline(self):
        elapsed = SimpleNamespace(value=0)
        def pause(seconds): elapsed.value += 100
        class Job:
            def wait(self, seconds): return elapsed.value >= 1000
            def terminate(self): raise AssertionError('elapsed time cannot terminate a test')
            def inspect(self): return SimpleNamespace(root_signaled=elapsed.value >= 1000,
                active_processes=0 if elapsed.value >= 1000 else 1, process_ids=())
        self.assertIsNone(run_tests.wait_for_worker(Job(), pause=pause))
        self.assertEqual(elapsed.value, 1000)

    def test_skipped_subtest_is_not_reported_as_a_running_or_passed_parent(self):
        class Specimen(unittest.TestCase):
            def test_cases(self):
                with self.subTest(value='unavailable'):
                    self.skipTest('fixture unavailable')
                with self.subTest(value='checked'):
                    self.assertTrue(True)
        with tempfile.TemporaryDirectory() as directory:
            result = unittest.TextTestRunner(stream=io.StringIO(), resultclass=lambda *a, **k:
                run_tests.TimedResult(*a, directory=Path(directory), **k)).run(unittest.TestSuite([
                    Specimen('test_cases')]))
            report = result.preserve(complete=True)
        self.assertTrue(report['successful'])
        self.assertEqual(report['rows'][0]['outcome'], 'skipped')
        self.assertEqual(report['rows'][0]['skipped_subtests'][0]['reason'], 'fixture unavailable')

    def test_class_setup_skip_accounts_for_each_selected_test(self):
        from contextlib import redirect_stderr
        class Specimen(unittest.TestCase):
            @classmethod
            def setUpClass(cls): raise unittest.SkipTest('compiler unavailable')
            def test_one(self): self.fail('skipped class must not run')
            def test_two(self): self.fail('skipped class must not run')
        with tempfile.TemporaryDirectory() as directory, redirect_stderr(io.StringIO()):
            report = run_tests._run_suite([Specimen('test_one'), Specimen('test_two')], Path(directory))
        tests = [row for row in report['rows'] if not row.get('fixture')]
        self.assertTrue(report['successful'])
        self.assertEqual([row['outcome'] for row in tests], ['skipped', 'skipped'])

    def test_worker_wait_preserves_owned_children_after_the_root_exits(self):
        observed = SimpleNamespace(checks=0)
        def pause(seconds): observed.checks += 1
        class Job:
            def wait(self, seconds): return True
            def terminate(self): raise AssertionError('live children must not be killed by elapsed time')
            def inspect(self): return SimpleNamespace(root_signaled=True,
                active_processes=1 if observed.checks < 3 else 0, process_ids=())
        self.assertIsNone(run_tests.wait_for_worker(Job(), pause=pause))
        self.assertEqual(observed.checks, 3)

    def test_empty_requires_root_signal_zero_active_count_and_empty_pid_list(self):
        for signaled, active, pids, empty in [
                (False, 0, (), False), (True, 1, (), False),
                (True, 0, (123,), False), (True, 0, (), True)]:
            with self.subTest(signaled=signaled, active=active, pids=pids):
                job = SimpleNamespace(inspect=lambda: SimpleNamespace(
                    root_signaled=signaled, active_processes=active, process_ids=pids))
                self.assertEqual(run_tests._empty(job), empty)

    def test_main_groups_marked_methods_by_class_and_keeps_the_last_row(self):
        root = self._tree()
        (root / 'unit' / 'test_labels.py').write_text(
            'import unittest\nfrom test_categories import test_group\n'
            '@test_group("lean")\nclass Marked(unittest.TestCase):\n'
            '    def test_one(self): self.assertTrue(True)\n'
            '    @test_group("resource")\n'
            '    def test_two(self): self.assertTrue(True)\n'
            'class Plain(unittest.TestCase):\n'
            '    def test_plain(self): self.assertTrue(True)\n'
            '    @test_group("resource")\n'
            '    def test_process(self): self.assertTrue(True)\n', encoding='utf-8')
        calls = []
        def isolate(tests, directory, **kwargs):
            calls.append([test.id() for test in tests])
            return run_tests._run_suite(tests, directory)
        destination = root.parent / 'output'
        with mock.patch.object(run_tests, '_isolated', side_effect=isolate), \
                redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            self.assertEqual(run_tests.main(['unit', '--jobs', '1', '--output', str(destination)]), 0)
        self.assertEqual(calls, [['unit.test_labels.Marked.test_one', 'unit.test_labels.Marked.test_two'],
                                 ['unit.test_labels.Plain.test_process']])
        report = json.loads((destination / 'report.json').read_bytes())
        self.assertEqual(report['counts'], {'passed': 4})
        self.assertEqual({row['id'] for group in report['reports'] for row in group['rows']}, set(report['selected']))

    def test_main_stops_after_an_interrupted_worker_and_accounts_for_later_groups(self):
        root = self._tree()
        (root / 'unit' / 'test_interrupt.py').write_text(
            'import unittest\nfrom test_categories import test_group\n'
            '@test_group("resource")\nclass Case(unittest.TestCase):\n'
            '    def test_one(self): self.fail("must not run")\n'
            '    def test_two(self): self.fail("must not run")\n', encoding='utf-8')
        self._module(root, 'sim/test_later.py')
        def interrupted(tests, directory, **kwargs):
            return {'complete': False, 'successful': False, 'interrupted': True,
                    'module_total_seconds': {}, 'rows': [
                        {'id': test.id(), 'outcome': 'not_run', 'seconds': 0, 'details': ['interrupt specimen']}
                        for test in tests]}
        destination = root.parent / 'output'
        with mock.patch.object(run_tests, '_isolated', side_effect=interrupted) as isolated, \
                redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            self.assertEqual(run_tests.main(['unit', 'sim', '--jobs', '1', '--output', str(destination)]), 1)
        isolated.assert_called_once()
        report = json.loads((destination / 'report.json').read_bytes())
        self.assertFalse(report['complete'])
        self.assertFalse(report['successful'])
        self.assertEqual(report['counts'], {'not_run': 3})
        rows = [row for group in report['reports'] for row in group['rows']]
        self.assertEqual({row['id'] for row in rows}, set(report['selected']))
        self.assertEqual(len(rows), len(report['selected']))
        self.assertFalse((destination / 'sim').exists())



if __name__ == '__main__':
    unittest.main()
