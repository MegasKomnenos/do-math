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
from test_categories import group_for, test_group as category


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

    def test_expensive_class_label_is_inherited_and_method_can_override_it(self):
        @category('lean')
        class Base(unittest.TestCase):
            def test_compiler(self): pass
            @category('unit')
            def test_parser(self): pass
        class Child(Base): pass
        self.assertEqual(group_for(Child('test_compiler')), 'lean')
        self.assertEqual(group_for(Child('test_parser')), 'unit')
        class Unknown(unittest.TestCase):
            def test_rule(self): pass
        Unknown.__module__ = 'new_unclassified_tests'
        self.assertEqual(group_for(Unknown('test_rule')), 'integration')

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

    def test_a_pass_on_the_same_inputs_is_reported_from_the_cache_not_rerun(self):
        target = 'test_file_io.FingerprintTests.test_recent_fingerprint_is_not_cached'
        with tempfile.TemporaryDirectory() as directory, \
             patch.object(run_tests, 'CACHE', Path(directory) / 'cache'), \
             patch.object(run_tests, '_input_key', return_value='k' * 64), \
             redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            def run(name, *extra):
                self.assertEqual(run_tests.main(['--group', 'unit', '--match', target, '--output',
                                                 str(Path(directory) / name), *extra]), 0)
                return json.loads((Path(directory) / name / 'report.json').read_bytes())
            first, second, forced = run('first'), run('second'), run('forced', '--no-cache')
        self.assertEqual((first['cached'], first['counts']), (0, {'passed': 1}))
        self.assertEqual((second['cached'], second['counts']), (1, {'passed': 1}))
        self.assertEqual(second['reports'][0]['rows'][0]['cached_from'],
                         str(Path(directory) / 'first' / 'report.json'))
        self.assertEqual(forced['cached'], 0)

    def test_editing_a_test_module_invalidates_it_and_its_importers_only(self):
        with tempfile.TemporaryDirectory() as directory:
            tests = Path(directory)
            (tests / 'test_base.py').write_text('HELPER = 1\n', encoding='utf-8')
            (tests / 'test_user.py').write_text('from test_base import HELPER\n', encoding='utf-8')
            (tests / 'test_other.py').write_text('X = 1\n', encoding='utf-8')
            with patch.object(run_tests, 'TESTS', tests):
                before = run_tests._module_keys()
                (tests / 'test_base.py').write_text('HELPER = 2\n', encoding='utf-8')
                shared = run_tests._module_keys()
                (tests / 'test_user.py').write_text('from test_base import HELPER\nY = 1\n', encoding='utf-8')
                own = run_tests._module_keys()
        self.assertNotEqual(shared['test_base'], before['test_base'])
        self.assertNotEqual(shared['test_user'], before['test_user'], 'an importer reads the edited module')
        self.assertEqual(shared['test_other'], before['test_other'])
        self.assertEqual(own['test_base'], shared['test_base'], 'an importer edit does not reach the imported module')
        self.assertNotEqual(own['test_user'], shared['test_user'])

    def test_a_fixture_module_is_keyed_with_the_test_modules_it_imports(self):
        with tempfile.TemporaryDirectory() as directory:
            tests = Path(directory)
            (tests / 'test_base.py').write_text('HELPER = 1\n', encoding='utf-8')
            (tests / 'shared_fixture.py').write_text('from test_base import HELPER\n', encoding='utf-8')
            (tests / 'test_user.py').write_text('import shared_fixture\n', encoding='utf-8')
            (tests / 'test_other.py').write_text('X = 1\n', encoding='utf-8')
            with patch.object(run_tests, 'TESTS', tests):
                before = run_tests._module_keys()
                (tests / 'test_base.py').write_text('HELPER = 2\n', encoding='utf-8')
                through = run_tests._module_keys()
                (tests / 'shared_fixture.py').write_text('from test_base import HELPER\nY = 1\n', encoding='utf-8')
                fixture = run_tests._module_keys()
                self.assertFalse(run_tests._is_test_source(tests.parent / 'shared_fixture.py'))
                self.assertTrue(run_tests._is_test_source(tests / 'shared_fixture.py'))
        self.assertNotEqual(through['test_user'], before['test_user'], 'a test module read through a fixture is tracked')
        self.assertNotEqual(fixture['test_user'], through['test_user'], 'a fixture edit reaches its importers')
        self.assertEqual(fixture['test_other'], before['test_other'], 'a fixture edit reaches only its importers')


if __name__ == '__main__':
    unittest.main()
