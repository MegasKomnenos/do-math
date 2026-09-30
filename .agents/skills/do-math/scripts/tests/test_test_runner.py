"""Runner regressions use synthetic tests/clocks, never a compiler or provider."""
from contextlib import redirect_stderr, redirect_stdout
import io
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import run_tests
from test_categories import isolation_for, test_group as category, unregistered_modules


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
            def test_compiler(self): pass
            @category('resource')
            def test_job(self): pass
        class Child(Base): pass
        class Plain(unittest.TestCase):
            def test_rule(self): pass
            @category('resource')
            def test_process(self): pass
        self.assertEqual(isolation_for(Child('test_compiler')), 'lean')
        self.assertEqual(isolation_for(Child('test_job')), 'resource')
        self.assertIsNone(isolation_for(Plain('test_rule')))
        self.assertEqual(isolation_for(Plain('test_process')), 'resource')
        with self.assertRaises(ValueError):
            category('unit')

    def test_every_test_module_is_in_exactly_one_shard_and_absent_modules_are_reported(self):
        self.assertEqual(unregistered_modules(Path(run_tests.TESTS)), ([], []))
        with tempfile.TemporaryDirectory() as directory:
            (Path(directory) / 'test_new_module.py').write_text('', encoding='utf-8')
            missing, stale = unregistered_modules(directory)
        self.assertEqual(missing, ['test_new_module'])
        self.assertIn('test_test_runner', stale)

    def test_positional_ids_select_a_module_class_or_method_without_prefix_collisions(self):
        with redirect_stdout(io.StringIO()) as out, redirect_stderr(io.StringIO()):
            self.assertEqual(run_tests.main(['--list', 'test_test_runner.RunnerTests']), 0)
        rows = out.getvalue().splitlines()
        self.assertTrue(rows)
        self.assertTrue(all(row.split('\t')[1].startswith('test_test_runner.RunnerTests.') for row in rows))
        self.assertTrue(all(row.split('\t')[0] == 'foundation' for row in rows))
        with redirect_stdout(io.StringIO()) as out, redirect_stderr(io.StringIO()):
            run_tests.main(['--list', 'boundary.test_engine_cli'])
        # boundary.test_engine_cli_advanced and ..._control_shapes share the name as a prefix. The
        # example is a new-system module, which 1f does not delete (the old test_knowledge was).
        rows = out.getvalue().splitlines()
        self.assertTrue(rows)
        self.assertTrue(all(row.split('\t')[1].rsplit('.', 2)[0] == 'boundary.test_engine_cli' for row in rows))

    def test_an_id_that_matches_no_test_refuses_the_whole_selection(self):
        # A mistyped ID beside valid ones must not drop out and leave the rest to read as a pass.
        with redirect_stdout(io.StringIO()) as out, redirect_stderr(io.StringIO()) as err:
            self.assertEqual(run_tests.main(['--list', 'test_test_runner', 'test_no_such_module']), 2)
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

    def test_native_worker_failure_cannot_be_hidden_by_a_successful_json_report(self):
        class Case(unittest.TestCase):
            def test_one(self): pass
        test = Case('test_one')
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / 'worker'
            class Job:
                def __init__(self, *args, **kwargs): pass
                def __enter__(self): return self
                def __exit__(self, *args): pass
                def resume(self):
                    run_tests._write_json(destination / 'result.json', {'complete': True, 'successful': True,
                        'rows': [{'id': test.id(), 'outcome': 'passed', 'seconds': .1, 'details': []}]})
            with patch('do_math.windows_job.WindowsJob', Job), \
                    patch.object(run_tests, 'wait_for_worker', return_value=None), \
                    patch.object(run_tests, '_exit_code', return_value=7):
                report = run_tests._isolated([test], destination, 1)
            self.assertFalse(report['successful'])
            self.assertEqual(report['returncode'], 7)


if __name__ == '__main__':
    unittest.main()
