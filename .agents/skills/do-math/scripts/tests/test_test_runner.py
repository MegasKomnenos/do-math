"""Runner regressions use synthetic tests/clocks, never a compiler or provider."""
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


if __name__ == '__main__':
    unittest.main()
