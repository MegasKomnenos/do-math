"""Mutation baseline bookkeeping against actual Git blobs and HEAD."""
from pathlib import Path
import json
import os
import subprocess
import tempfile
import time
import types
import unittest
from unittest import mock

from support import mutation
from test_categories import test_group


@test_group('resource')
class ParallelMutationTests(unittest.TestCase):
    """Small real children prove overlap, shared normal evidence and owned interruption."""

    def fixture(self, body):
        from support.branch_gate import git_blobs
        root = Path(tempfile.mkdtemp(prefix='mutation-parallel-'))
        subprocess.run(['git', 'init', '--template=', str(root)], capture_output=True, check=True)
        subprocess.run(['git', '-C', str(root), '-c', 'user.name=Mutation fixture',
                        '-c', 'user.email=fixture@invalid', '-c', 'core.hooksPath=',
                        '-c', 'commit.gpgsign=false', 'commit', '--allow-empty', '--no-verify',
                        '-m', 'Empty baseline'], capture_output=True, check=True)
        scripts = root / 'scripts'
        scripts.mkdir()
        module = 'parallel_subject.py'
        source = ''.join(f'def f{i}():\n    return 2\n' for i in range(3)) + 'def same():\n    return None\n'
        (scripts / module).write_text(source, encoding='utf-8')
        (scripts / 'parallel_tests.py').write_text(
            'import unittest, time, os, json, subprocess, sys, threading\nfrom pathlib import Path\n'
            'from parallel_subject import f0, f1, f2, same\n'
            'class Case(unittest.TestCase):\n    def test_values(self):\n' + body + '\n'
            '        self.assertEqual([f0(), f1(), f2(), same()], [2, 2, 2, None])\n', encoding='utf-8')
        path = 'scripts/' + module
        index = {'tests': ['parallel_tests.Case.test_values'], 'files': {path: {
            'blob': git_blobs(root, [path])[path], 'functions': {name: [0] for name in ('f0', 'f1', 'f2', 'same')}}}}
        self.enterContext(mock.patch.object(mutation, 'SCRIPTS', scripts))
        self.enterContext(mock.patch.dict(os.environ, {'PYTHONPATH': str(scripts)}))
        print('Parallel mutation fixture: ' + str(root))
        return root, module, source, index

    def run_fixture(self, root, module, index, jobs, name):
        listing = root / (name + '-pseudo.json')
        listing.write_text(json.dumps({'entries': [
            {'module': module, 'function': 'same', 'rule': 'pass', 'base': 'old', 'reason': 'None is its behaviour'},
            {'module': 'unrelated.py', 'function': 'kept', 'reason': 'existing unrelated reason'},
            {'module': module, 'function': 'f0', 'reason': 'obsolete entry'}]}), encoding='utf-8')
        report = mutation.run('HEAD', index, {module: '1'}, root, root / name, every=True,
                              only=[module], listing_path=listing, jobs=jobs)
        (root / (name + '.json')).write_text(json.dumps(report, indent=1), encoding='utf-8')
        return report, listing

    def test_exact_nested_function_runs_only_its_plan_and_keeps_other_list_entries(self):
        from support.branch_gate import git_blobs
        root, module, _, index = self.fixture('        pass')
        source = ('def outer():\n    def inner():\n        return 2\n    return inner()\n'
                  'def neighbour():\n    return 7\n')
        (root / 'scripts' / module).write_text(source, encoding='utf-8')
        (root / 'scripts/parallel_tests.py').write_text(
            'import unittest\nfrom parallel_subject import outer, neighbour\n'
            'class Case(unittest.TestCase):\n    def test_values(self):\n'
            '        self.assertEqual(neighbour(), 7)\n        self.assertEqual(outer(), 2)\n', encoding='utf-8')
        entry = index['files']['scripts/' + module]
        entry['blob'] = git_blobs(root, ['scripts/' + module])['scripts/' + module]
        entry['functions'] = {'outer.<locals>.inner': [0], 'outer': [0], 'neighbour': [0]}
        listing = root / 'exact-pseudo.json'
        listing.write_text(json.dumps({'entries': [
            {'module': module, 'function': 'outer.<locals>.inner', 'reason': ''},
            {'module': module, 'function': 'neighbour', 'reason': 'kept outside selection'}]}), encoding='utf-8')
        selector = module + ':outer.<locals>.inner'
        report = mutation.run('HEAD', index, {module: '1'}, root, root / 'exact', every=True,
                              only=[module], listing_path=listing, jobs=1,
                              function_selectors=[selector, selector])
        self.assertEqual(report['function_selectors'], [selector])
        self.assertEqual([(o['function'], o['status']) for o in report['outcomes']],
                         [('outer.<locals>.inner', 'killed')])
        self.assertEqual(report['outcomes'][0]['selection']['indexed_ordinals'], [0])
        self.assertEqual(report['baselines'][0]['status'], 'passed')
        self.assertEqual([e['function'] for e in mutation.read_list(listing)['entries']], ['neighbour'])
        self.assertEqual(len(list((root / 'exact').glob('mutant-*'))), 1)
        self.assertEqual((root / 'scripts' / module).read_text(encoding='utf-8'), source)
        with mock.patch.object(mutation, '_child_run', side_effect=AssertionError('launched child')):
            with self.assertRaisesRegex(ValueError, 'unresolved function selectors'):
                mutation.run('HEAD', index, {module: '1'}, root, root / 'typo', every=True,
                             only=[module], listing_path=listing, function_selectors=[module + ':outer.<locals>.typo'])

    def test_real_parallel_children_match_serial_results_and_share_one_baseline(self):
        from datetime import datetime
        root, module, source, index = self.fixture(
            '        started = time.time_ns()\n'
            '        os.write(1, b"native stdout marker\\n")\n'
            '        os.write(2, b"native stderr marker\\n")\n'
            '        time.sleep(.25)\n'
            '        Path(os.environ["TEMP"], "execution.json").write_text(json.dumps(\n'
            '            {"pid": os.getpid(), "started": started, "finished": time.time_ns()}))')
        reports = []
        for jobs, name in ((1, 'serial'), (3, 'parallel')):
            report, listing = self.run_fixture(root, module, index, jobs, name)
            reports.append(report)
            self.assertEqual(report['counts'], {'killed': 3, 'survived': 1})
            self.assertTrue(mutation.passed(report))
            self.assertEqual(len(report['baselines']), 1)
            self.assertEqual(report['baselines'][0]['status'], 'passed')
            self.assertEqual([(o['function'], o['status']) for o in report['outcomes']],
                             [('f0', 'killed'), ('f1', 'killed'), ('f2', 'killed'), ('same', 'survived')])
            self.assertEqual([(e['function'], e['reason']) for e in mutation.read_list(listing)['entries']],
                             [('same', 'None is its behaviour'), ('kept', 'existing unrelated reason')])
            attempts = [a['execution'] for o in report['outcomes'] for a in o['attempts']]
            attempts += [b['attempt'] for b in report['baselines']]
            self.assertEqual(len({a['directory'] for a in attempts}), 5)
            events = []
            executions = []
            for attempt in attempts:
                directory = Path(attempt['directory'])
                self.assertTrue(all((directory / file).exists()
                                    for file in ('spec.json', 'result.json', 'attempt.json', 'output.txt', 'scratch')))
                self.assertEqual(attempt['exit_code'], 0)
                output = (directory / 'output.txt').read_text(encoding='utf-8')
                self.assertIn('native stdout marker', output)
                self.assertIn('native stderr marker', output)
                execution = json.loads((directory / 'scratch/execution.json').read_text(encoding='utf-8'))
                self.assertEqual(execution['pid'], attempt['pid'])
                executions.extend([(execution['started'], 1), (execution['finished'], -1)])
                events.extend([(datetime.fromisoformat(attempt['started']), 1),
                               (datetime.fromisoformat(attempt['finished']), -1)])
            live = peak = 0
            for _, delta in sorted(events):
                live += delta
                peak = max(peak, live)
            self.assertEqual(peak, jobs)
            active = execution_peak = 0
            for _, delta in sorted(executions):
                active += delta
                execution_peak = max(execution_peak, active)
            self.assertEqual(execution_peak, jobs)
            (root / (name + '-overlap.json')).write_text(json.dumps({'peak': peak, 'seconds': report['seconds'],
                'execution_peak': execution_peak, 'child_seconds': sum(a['seconds'] for a in attempts)}), encoding='utf-8')
            self.assertEqual((root / 'scripts' / module).read_text(encoding='utf-8'), source)
        self.assertEqual([o['selection'] for o in reports[0]['outcomes']],
                         [o['selection'] for o in reports[1]['outcomes']])
        with self.assertRaisesRegex(ValueError, 'new or empty'):
            mutation.run('HEAD', index, {module: '1'}, root, root / 'parallel', jobs=3)

    def test_interrupt_joins_all_active_child_trees_and_preserves_listing_and_attempts(self):
        import run_tests
        from concurrent.futures import wait as wait_futures, FIRST_COMPLETED
        root, module, _, index = self.fixture(
            '        process = subprocess.Popen([sys.executable, "-c", "import threading; threading.Event().wait()"], '
            'creationflags=subprocess.CREATE_NO_WINDOW)\n'
            '        Path(os.environ["TEMP"], "ready.json").write_text(json.dumps({"pid": process.pid}))\n'
            '        threading.Event().wait()')
        ended = []
        original_wait = run_tests.wait_for_worker

        def wait(job, **options):
            original_wait(job, **options)
            if options.get('cancelled') is None:
                state = job.inspect()
                ended.append({'root_signaled': state.root_signaled, 'active_processes': state.active_processes,
                              'process_ids': state.process_ids})

        def interrupt(futures):
            deadline = time.monotonic() + 15  # observation only; explicit interrupt below owns termination
            while len(list((root / 'interrupt').glob('mutant-*/attempt-*/scratch/ready.json'))) != 3:
                if time.monotonic() > deadline:
                    self.fail('three mutant children did not reach their explicit interruption point')
                finished, _ = wait_futures(futures, timeout=.01, return_when=FIRST_COMPLETED)
                if finished:
                    self.fail('mutation children ended before their explicit interruption point')
            raise KeyboardInterrupt('explicit fixture interruption')

        with mock.patch.object(mutation, 'as_completed', interrupt), mock.patch.object(run_tests, 'wait_for_worker', wait):
            report, listing = self.run_fixture(root, module, index, 3, 'interrupt')
        self.assertTrue(report['interrupted'])
        self.assertFalse(mutation.passed(report))
        self.assertEqual(report['counts'], {'execution_error': 4})
        self.assertEqual(report['baselines'], [])
        self.assertEqual(len(ended), 3)
        self.assertTrue(all(s == {'root_signaled': True, 'active_processes': 0, 'process_ids': ()} for s in ended))
        self.assertEqual(len(mutation.read_list(listing)['entries']), 3)
        attempts = list((root / 'interrupt').glob('mutant-*/attempt-*/attempt.json'))
        self.assertEqual(len(attempts), 3)
        self.assertTrue(all('CancelledError' in json.loads(p.read_text(encoding='utf-8'))['error'] for p in attempts))
        (root / 'terminated.json').write_text(json.dumps(ended), encoding='utf-8')


@test_group("resource")
class ActualBaselineTests(unittest.TestCase):
    def _run_fixture(self, baseline_body, *, preamble='', via='run', next_test=False, explicit=False,
                     missing_method=False):
        from support.branch_gate import git_blobs
        root = Path(tempfile.mkdtemp(prefix='mutation-baseline-'))
        repository = root
        # The specimen lives in external scratch, independently of the runner's
        # checkout. Its real empty HEAD keeps the subject absent from the base.
        subprocess.run(['git', 'init', '--template=', str(repository)],
                       capture_output=True, check=True)
        subprocess.run(['git', '-C', str(repository), '-c', 'user.name=Mutation fixture',
                        '-c', 'user.email=fixture@invalid', '-c', 'core.hooksPath=',
                        '-c', 'commit.gpgsign=false', 'commit', '--allow-empty',
                        '--no-verify', '-m', 'Empty mutation fixture baseline'],
                       capture_output=True, check=True)
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
        if missing_method:
            test = 'mutation_fixture_tests.Case.test_missing'
        tests = [test] + (['mutation_fixture_tests.Case.test_z'] if next_test else [])
        path = scripts.relative_to(repository).as_posix() + '/' + module
        index = {'tests': tests, 'files': {path: {
            'blob': git_blobs(repository, [path])[path],
            'functions': {} if explicit else {'value': list(range(len(tests)))}}}}
        self.enterContext(mock.patch.object(mutation, 'SCRIPTS', scripts))
        self.enterContext(mock.patch.dict(os.environ, {'PYTHONPATH': str(scripts)}))
        if via == 'run':
            report = mutation.run('HEAD', index, {module: '1'}, repository, root / 'mutation', every=True,
                                  listing_path=root / 'pseudo.json', only=[module],
                                  explicit_tests=tests if explicit else ())
        else:
            import run_tests
            from support import branch_gate, selection
            actual_run = mutation.run

            def run(base, given, layers, repo, directory, **options):
                # Supply the tiny population, then execute the actual parent and real children.
                return actual_run(base, given, {module: '1'}, repo, directory, every=True,
                                  listing_path=root / 'pseudo.json', only=options.get('only', ()),
                                  explicit_tests=options.get('explicit_tests', ()), jobs=options['jobs'])

            index.update(format=selection.FORMAT, commit='fixture')
            self.enterContext(mock.patch.object(mutation, 'run', run))
            self.enterContext(mock.patch.object(selection, 'read_index', lambda: (index, '')))
            self.enterContext(mock.patch.object(selection, 'is_ancestor_of_head', lambda repo: lambda commit: True))
            if via == 'cli':
                with mock.patch.object(branch_gate, 'repository_root', lambda: repository):
                    exit_code = mutation.main(['--base', 'HEAD', '--every', '--output', str(root / 'mutation')]
                        + (['--only', module, '--test', test, '--jobs', '3'] if explicit else []))
                report = json.loads((root / 'mutation/mutation.json').read_text(encoding='utf-8'))
                observed = exit_code == 0
            else:
                self.enterContext(mock.patch.object(branch_gate, 'gate', lambda *args: {
                    'passed': True, 'judged_modules': 1, 'modules_with_gaps': 0,
                    'missing_branches': 0, 'missing_lines': 0, 'excluded_lines': 0, 'unmeasured_modules': []}))
                measured = types.SimpleNamespace(root=repository, finish=lambda *args, **kwargs: {'files': {}})
                args = types.SimpleNamespace(tests=[test], match=[], mutation_base='HEAD', jobs=1)
                with mock.patch.object(run_tests, 'SCRIPTS', scripts):
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

    def test_explicit_cli_selection_reaches_real_children_and_requires_normal_pass(self):
        for body, status in (('', 'killed'), ('        if value() == 2:\n            os._exit(17)', 'execution_error')):
            with self.subTest(status=status):
                with mock.patch.object(mutation, 'run', mutation.run), mock.patch.object(mutation, 'SCRIPTS', mutation.SCRIPTS):
                    report, root = self._run_fixture(body, via='cli', explicit=True)
                self.assertEqual(report['counts'], {status: 1})
                self.assertEqual(report['jobs'], 3)
                selection = report['outcomes'][0]['selection']
                self.assertEqual(selection['indexed_ordinals'], [])
                self.assertEqual(selection['tests'], ['mutation_fixture_tests.Case.test_value'])
                self.assertEqual(report['baselines'][0]['status'],
                                 'passed' if status == 'killed' else 'evidence_error')

    def test_a_missing_explicit_method_cannot_turn_a_load_error_into_a_kill(self):
        report, root = self._run_fixture('', explicit=True, missing_method=True)
        self.assertEqual(report['counts'], {'execution_error': 1})
        self.assertFalse(mutation.passed(report))
        self.assertEqual(report['baselines'][0]['status'], 'evidence_error')
        self.assertEqual(report['baselines'][0]['attempt']['result']['tests_run'], 0)
        self.assertIsNotNone(report['baselines'][0]['attempt']['result']['load_error'])

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

        def child(spec, directory, **options):
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
