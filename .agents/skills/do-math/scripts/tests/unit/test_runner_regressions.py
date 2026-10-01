"""Runner reporting, selection and deadlines use synthetic tests and injected clocks."""
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


class RunnerTests(unittest.TestCase):
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
        root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        for folder in run_tests.FOLDERS:
            (root / folder).mkdir()
            (root / folder / '__init__.py').write_text('', encoding='utf-8')
        self.enterContext(mock.patch.object(run_tests, 'TESTS', root))
        self.enterContext(mock.patch.object(sys, 'path', sys.path.copy()))
        self.enterContext(mock.patch.dict(sys.modules))
        for name in list(sys.modules):
            if name.split('.')[0] in run_tests.FOLDERS:
                del sys.modules[name]
        return root

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

    def test_timeout_terminates_the_owned_tree_and_identifies_the_running_test(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'progress.json'
            run_tests._write_json(path, {'sequence': 1, 'test_id': 'slow.compiler', 'phase': 'test'})
            clock = SimpleNamespace(value=0)
            def pause(seconds): clock.value += seconds
            class Job:
                ended = False
                def wait(self, seconds): return self.ended
                def terminate(self): self.ended = True
                def inspect(self): return SimpleNamespace(root_signaled=self.ended,
                    active_processes=0 if self.ended else 1, process_ids=() if self.ended else (123,))
            job = Job()
            result = run_tests.wait_for_worker(job, path, .2, clock=lambda: clock.value, pause=pause)
            self.assertEqual(result['test_id'], 'slow.compiler')
            self.assertTrue(result['termination_confirmed'])
            self.assertTrue(job.ended)

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

    def test_next_test_gets_its_own_deadline_without_restarting_class_fixtures(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'progress.json'
            run_tests._write_json(path, {'sequence': 1, 'test_id': 'first', 'phase': 'test'})
            clock = SimpleNamespace(value=0)
            def pause(seconds): clock.value += seconds
            class Job:
                updated = False
                def wait(self, seconds):
                    if clock.value >= .4 and not self.updated:
                        run_tests._write_json(path, {'sequence': 2, 'test_id': 'second', 'phase': 'test'})
                        self.updated = True
                    return clock.value >= .8
                def terminate(self): raise AssertionError('a progressing test group must not time out')
                def inspect(self): return SimpleNamespace(root_signaled=True, active_processes=0, process_ids=())
            self.assertIsNone(run_tests.wait_for_worker(Job(), path, .6,
                clock=lambda: clock.value, pause=pause))



if __name__ == '__main__':
    unittest.main()
