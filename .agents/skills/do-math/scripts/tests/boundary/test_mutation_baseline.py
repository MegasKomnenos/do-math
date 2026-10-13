"""Mutation baseline bookkeeping against actual Git blobs and HEAD."""
from pathlib import Path
import json
import os
import tempfile
import types
import unittest
from unittest import mock

from support import mutation
from test_categories import test_group


@test_group("resource")
class ActualBaselineTests(unittest.TestCase):
    def _run_fixture(self, baseline_body, *, preamble='', via='run', next_test=False):
        from support.branch_gate import git_blobs, repository_root
        repository = repository_root()
        root = Path(tempfile.mkdtemp(prefix='mutation-baseline-'))
        scripts = root / 'scripts'
        scripts.mkdir()
        module = 'mutation_fixture_subject.py'
        source = 'def value():\n    return 2\n'
        (scripts / module).write_text(source, encoding='utf-8')
        (scripts / 'mutation_fixture_tests.py').write_text(
            'import os\nimport unittest\nfrom mutation_fixture_subject import value\n'
            + preamble + '\n'
            'class Case(unittest.TestCase):\n'
            '    def test_value(self):\n'
            + baseline_body + '\n'
            '        self.assertEqual(value(), 2)\n'
            + ('    def test_z(self):\n        self.assertEqual(value(), 2)\n' if next_test else ''), encoding='utf-8')
        test = 'mutation_fixture_tests.Case.test_value'
        tests = [test] + (['mutation_fixture_tests.Case.test_z'] if next_test else [])
        path = scripts.relative_to(repository).as_posix() + '/' + module
        index = {'tests': tests, 'files': {path: {
            'blob': git_blobs(repository, [path])[path], 'functions': {'value': list(range(len(tests)))}}}}
        self.enterContext(mock.patch.object(mutation, 'SCRIPTS', scripts))
        self.enterContext(mock.patch.dict(os.environ, {'PYTHONPATH': str(scripts)}))
        if via == 'run':
            report = mutation.run('HEAD', index, {module: '1'}, repository, root / 'mutation', every=True,
                                  listing_path=root / 'pseudo.json')
        else:
            import run_tests
            from support import branch_gate, selection
            actual_run = mutation.run

            def run(base, given, layers, repo, directory, **options):
                # Supply the tiny population, then execute the actual parent and real children.
                return actual_run(base, given, {module: '1'}, repo, directory, every=True,
                                  listing_path=root / 'pseudo.json')

            index.update(format=selection.FORMAT, commit='fixture')
            self.enterContext(mock.patch.object(mutation, 'run', run))
            self.enterContext(mock.patch.object(selection, 'read_index', lambda: (index, '')))
            self.enterContext(mock.patch.object(selection, 'is_ancestor_of_head', lambda repo: lambda commit: True))
            if via == 'cli':
                exit_code = mutation.main(['--base', 'HEAD', '--every', '--output', str(root / 'mutation')])
                report = json.loads((root / 'mutation/mutation.json').read_text(encoding='utf-8'))
                observed = exit_code == 0
            else:
                self.enterContext(mock.patch.object(branch_gate, 'gate', lambda *args: {
                    'passed': True, 'judged_modules': 1, 'modules_with_gaps': 0,
                    'missing_branches': 0, 'missing_lines': 0, 'excluded_lines': 0, 'unmeasured_modules': []}))
                measured = types.SimpleNamespace(root=repository, finish=lambda *args, **kwargs: {'files': {}})
                args = types.SimpleNamespace(tests=[test], match=[], mutation_base='HEAD')
                result = run_tests._finish_t3(measured, root, [], args, False)
                (root / 't3.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
                report, observed = result['mutation'], result['passed']
                self.assertTrue(result['branch_gate']['passed'])
            (root / 'consumer.json').write_text(json.dumps({'via': via, 'passed': observed}), encoding='utf-8')
            self.assertEqual(observed, mutation.passed(report))
        (root / 'report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
        print('Actual mutation fixture: ' + str(root))
        self.assertEqual((scripts / module).read_text(encoding='utf-8'), source)
        return report, root

    def test_missing_normal_child_result_never_certifies_a_kill(self):
        report, root = self._run_fixture('        if value() == 2:\n            os._exit(17)')
        self.assertNotEqual(report['outcomes'][0]['status'], 'killed')
        self.assertFalse(mutation.passed(report))
        baseline = report['baselines'][0]
        self.assertEqual(baseline['status'], 'evidence_error')
        self.assertEqual(baseline['attempt']['exit_code'], 17)
        self.assertIsNone(baseline['attempt']['result'])
        self.assertIn('FileNotFoundError', baseline['detail'])
        self.assertEqual(report['outcomes'][0]['attempts'][0]['baselines'], [baseline['id']])

    def test_actual_normal_pass_certifies_the_mutant_failure(self):
        for body in ('', '        with self.subTest(axis=1):\n            self.assertEqual(value(), 2)'):
            with self.subTest(body=body):
                report, root = self._run_fixture(body)
                self.assertEqual(report['outcomes'][0]['status'], 'killed')
                self.assertTrue(mutation.passed(report))
                self.assertEqual(report['baselines'][0]['attempt']['result']['rows'][0]['outcome'], 'passed')

    def test_real_load_failure_is_a_kill_only_when_the_normal_batch_passes(self):
        for condition, status in (('value() is None', 'killed'), ('True', 'execution_error')):
            with self.subTest(condition=condition):
                report, root = self._run_fixture('', preamble=f'if {condition}:\n    raise ImportError("specimen load")')
                self.assertEqual(report['counts'], {status: 1})
                self.assertEqual(mutation.passed(report), status == 'killed')
                attempt = report['outcomes'][0]['attempts'][0]['execution']
                self.assertEqual(attempt['exit_code'], 0)
                self.assertEqual(attempt['result']['tests_run'], 0)
                self.assertIn('specimen load', attempt['result']['load_error']['details'][0])
                self.assertEqual(report['baselines'][0]['status'],
                                 'passed' if status == 'killed' else 'evidence_error')

    def test_normal_skip_and_fixture_events_are_evidence_errors(self):
        cases = [('        if value() == 2:\n            self.skipTest("normal skip")', '', 'skipped', False),
                 ('        if value() == 2:\n            with self.subTest(axis=1):\n                self.skipTest("subtest skip")',
                  '', 'skipped', False),
                 ('', 'def setUpModule():\n    if value() == 2:\n        raise unittest.SkipTest("fixture skip")',
                  'skipped', True),
                 ('', 'def setUpModule():\n    if value() == 2:\n        raise RuntimeError("fixture error")',
                  'error', True)]
        for body, preamble, outcome, fixture in cases:
            with self.subTest(outcome=outcome, fixture=fixture):
                report, root = self._run_fixture(body, preamble=preamble)
                self.assertEqual(report['counts'], {'execution_error': 1})
                self.assertFalse(mutation.passed(report))
                result = report['baselines'][0]['attempt']['result']
                self.assertEqual((result['rows'][0]['outcome'], result['rows'][0]['fixture']), (outcome, fixture))
                self.assertEqual(result['tests_run'], 0 if fixture else 1)

    def test_a_written_passing_result_cannot_hide_an_abnormal_normal_exit(self):
        report, root = self._run_fixture('', preamble=
            'import atexit\nif value() == 2:\n    atexit.register(lambda: os._exit(23))')
        self.assertEqual(report['counts'], {'execution_error': 1})
        self.assertFalse(mutation.passed(report))
        normal = report['baselines'][0]['attempt']
        self.assertEqual(normal['exit_code'], 23)
        self.assertEqual(normal['result']['rows'][0]['outcome'], 'passed')

    def test_actual_normal_failure_is_retained_while_the_next_witness_kills(self):
        report, root = self._run_fixture('        self.fail("normal failure")', next_test=True)
        self.assertEqual(report['counts'], {'killed': 1})
        self.assertFalse(mutation.passed(report))
        self.assertEqual(report['baseline_failing'], ['mutation_fixture_tests.Case.test_value'])
        self.assertEqual([item['status'] for item in report['baselines']], ['failing', 'passed'])
        outcome = report['outcomes'][0]
        self.assertEqual(outcome['killed_by'], ['mutation_fixture_tests.Case.test_z'])
        self.assertEqual([a['baselines'] for a in outcome['attempts']], [[0], [1]])
        results = [Path(a['execution']['directory']) / 'result.json' for a in outcome['attempts']]
        self.assertNotEqual(results[0], results[1])
        self.assertEqual([json.loads(path.read_text(encoding='utf-8'))['rows'][0]['id'] for path in results],
                         ['mutation_fixture_tests.Case.test_value', 'mutation_fixture_tests.Case.test_z'])

    def test_actual_mutant_exit_or_expected_failure_is_not_a_pass(self):
        for body, preamble in [('        if value() is None:\n            os._exit(19)', ''),
                               ('', '@unittest.expectedFailure')]:
            with self.subTest(body=body):
                report, root = self._run_fixture(body, preamble=preamble)
                self.assertEqual(report['counts'], {'execution_error': 1})
                self.assertFalse(mutation.passed(report))
                self.assertEqual(report['baselines'], [])
                attempt = report['outcomes'][0]['attempts'][0]['execution']
                if body:
                    self.assertEqual(attempt['exit_code'], 19)
                    self.assertIsNone(attempt['result'])
                else:
                    self.assertEqual(attempt['exit_code'], 0)
                    self.assertEqual(attempt['result']['rows'][0]['outcome'], 'expected_failure')

    def test_cli_and_t3_consume_actual_normal_evidence_with_the_same_verdict(self):
        for via in ('cli', 't3'):
            for body, passed in (('', True), ('        if value() == 2:\n            os._exit(17)', False)):
                with self.subTest(via=via, passed=passed):
                    # Restore routing between populations while retaining each independent attempt directory.
                    with mock.patch.object(mutation, 'run', mutation.run), mock.patch.object(mutation, 'SCRIPTS', mutation.SCRIPTS):
                        report, root = self._run_fixture(body, via=via)
                    consumer = json.loads((root / 'consumer.json').read_text(encoding='utf-8'))
                    self.assertEqual(consumer['passed'], passed)
                    self.assertEqual(report['counts'], {'killed' if passed else 'execution_error': 1})


@test_group("resource")
class LazyBaselineTests(unittest.TestCase):
    def test_only_a_test_that_failed_a_mutant_is_rechecked_unmutated_and_one_failing_unmutated_is_set_aside(self):
        """No union baseline: a mutant's failing test counts only if it passes unmutated (D9)."""
        from support.branch_gate import git_blobs, repository_root
        root = repository_root()
        module = 'do_math/http_request.py'
        path = f'{mutation.SCRIPTS.relative_to(root).as_posix()}/{module}'
        index = {'tests': ['t0', 't1', 't2'],
                 'files': {path: {'blob': git_blobs(root, [path])[path],
                                  'functions': {'check_url': [1], 'check_body': [0, 2]}}}}
        calls = []

        def child(spec, directory):
            tests = spec['tests']
            calls.append((spec['mutant'] is not None, tests))
            failing = ({'t0'} & set(tests)) if spec['mutant'] is None else \
                ({'t1'} if 't1' in tests else {'t0'} if 't0' in tests else set())
            result = mutation._new_result(spec)
            result['collected'] = tests
            result['rows'] = [{'id': test, 'outcome': 'failed' if test in failing else 'passed', 'fixture': False}
                              for test in (sorted(failing) if failing else tests)]
            result['tests_run'] = len(result['rows'])
            mutation.validate_result(result, spec)
            return {'result': result, 'error': None, 'seconds': 0.1, 'directory': str(directory)}
        self.enterContext(mock.patch.object(mutation, '_child_run', child))
        directory = Path(self.enterContext(tempfile.TemporaryDirectory()))
        report = mutation.run('HEAD', index, {module: '1'}, root, directory, only=[module], every=True,
                              listing_path=directory / 'pseudo_tested.json')
        self.assertEqual({o['function']: o['status'] for o in report['outcomes']},
                         {'check_url': 'killed', 'check_body': 'survived'})
        self.assertEqual([tests for mutated, tests in calls if not mutated], [['t1'], ['t0']])
        self.assertEqual(report['baseline_failing'], ['t0'])
