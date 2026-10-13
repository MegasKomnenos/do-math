"""Extreme mutation rules and bookkeeping (설계 6.3), judged on small synthetic modules."""
import ast
import contextlib
import inspect
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

from support import mutation
from support.mutation import (changed_functions, functions, mutate, rule_of, tests_for, unreasoned,
                               update_list)

SOURCE = '''class Store:
    def put(self, key, value):
        """Keep a value."""
        self.items[key] = value

    def get(self, key):
        return self.items.get(key, '기본값')


def pairs(items):
    for item in items:
        yield item, item


def total(values): return sum(values)


def explicit_none(flag):
    if flag:
        return None
    return


def outer(x):
    def inner():
        return x
    inner()


def stub():
    ...
'''


def _node(source, key):
    return dict(functions(ast.parse(source)))[key]


def _run(source):
    namespace = {}
    exec(compile(source, '<mutant>', 'exec'), namespace)
    return namespace


class RuleTests(unittest.TestCase):
    def test_the_rule_follows_the_body_shape_of_the_function_itself(self):
        rules = {key: rule_of(node) for key, node in functions(ast.parse(SOURCE))}
        self.assertEqual(rules, {'Store.put': 'pass', 'Store.get': 'return_none', 'pairs': 'return_first',
                                 'total': 'return_none', 'explicit_none': 'pass', 'outer': 'pass',
                                 'outer.<locals>.inner': 'return_none', 'stub': 'pass'})


class MutantTests(unittest.TestCase):
    def test_a_value_returning_function_returns_none_and_keeps_its_docstring_and_neighbours(self):
        rule, mutant = mutate(SOURCE, _node(SOURCE, 'Store.get'))
        namespace = _run(mutant)
        store = namespace['Store']()
        store.items = {'k': 1}
        self.assertEqual(rule, 'return_none')
        self.assertIsNone(store.get('k'))
        self.assertEqual(namespace['total']([1, 2]), 3)
        self.assertEqual(ast.get_docstring(_node(mutant, 'Store.put')), 'Keep a value.')

    def test_a_state_changing_function_does_nothing(self):
        rule, mutant = mutate(SOURCE, _node(SOURCE, 'Store.put'))
        store = _run(mutant)['Store']()
        store.items = {}
        store.put('k', 1)
        self.assertEqual((rule, store.items), ('pass', {}))
        self.assertEqual(ast.get_docstring(_node(mutant, 'Store.put')), 'Keep a value.')

    def test_a_generator_stays_a_generator_and_yields_nothing(self):
        rule, mutant = mutate(SOURCE, _node(SOURCE, 'pairs'))
        pairs = _run(mutant)['pairs']
        self.assertEqual(rule, 'return_first')
        self.assertTrue(inspect.isgeneratorfunction(pairs))
        self.assertEqual(list(pairs([1, 2])), [])

    def test_a_one_line_body_is_replaced_in_place(self):
        rule, mutant = mutate(SOURCE, _node(SOURCE, 'total'))
        self.assertIsNone(_run(mutant)['total']([1, 2]))
        one_line_generator = 'def g(): yield 1\n'
        rule, mutant = mutate(one_line_generator, _node(one_line_generator, 'g'))
        self.assertEqual((rule, list(_run(mutant)['g']())), ('return_first', []))

    def test_a_body_of_only_pass_or_ellipsis_has_no_mutant(self):
        self.assertEqual(mutate(SOURCE, _node(SOURCE, 'stub')), ('pass', None))


class ChangeTests(unittest.TestCase):
    def test_a_changed_or_new_body_is_a_target_and_a_docstring_or_neighbour_edit_is_not(self):
        base = SOURCE
        edited = SOURCE.replace('"""Keep a value."""', '"""Keep the value."""') \
            .replace("'기본값'", "'다른 값'") + '\n\ndef added():\n    return 1\n'
        self.assertEqual([key for key, _ in changed_functions(base, edited)], ['Store.get', 'added'])
        self.assertEqual(len(changed_functions('', SOURCE)), 8)

    def test_repeated_names_are_keyed_in_order(self):
        source = 'def f():\n    return 1\n\n\ndef f():\n    return 2\n'
        self.assertEqual([key for key, _ in functions(ast.parse(source))], ['f', 'f#2'])


class SelectionTests(unittest.TestCase):
    ENTRY = {'blob': 'b1', 'functions': {'f': [0, 1, 2], 'C.m': [1]}}

    def test_the_tests_that_entered_the_function_are_chosen_whatever_moved(self):
        self.assertEqual(tests_for(self.ENTRY, 'b1', 'f', '2'), ({0, 1, 2}, ()))
        self.assertEqual(tests_for(self.ENTRY, 'b2', 'f', '2'), ({0, 1, 2}, ()))
        self.assertEqual(tests_for(self.ENTRY, 'b1', 'C.m#2', '2'), ({1}, ()))

    def test_an_unknown_function_of_a_changed_file_or_a_missing_index_adds_the_layer_folders(self):
        self.assertEqual(tests_for(self.ENTRY, 'b1', 'g', '3'), (set(), ()))
        self.assertEqual(tests_for(self.ENTRY, 'b2', 'g', '3'), (set(), ('sim',)))
        self.assertEqual(tests_for(None, 'b1', 'f', '1'), (set(), ('unit', 'contracts')))


class ListTests(unittest.TestCase):
    def test_survivors_enter_without_a_reason_and_killed_functions_leave(self):
        listing = {'note': 'n', 'entries': [
            {'module': 'do_math/a.py', 'function': 'kept', 'rule': 'pass', 'base': 'b0', 'reason': 'None is its behaviour'},
            {'module': 'do_math/a.py', 'function': 'fixed', 'rule': 'pass', 'base': 'b0', 'reason': ''}]}
        outcomes = [{'module': 'do_math/a.py', 'function': 'fixed', 'rule': 'pass', 'status': 'killed'},
                    {'module': 'do_math/a.py', 'function': 'kept', 'rule': 'pass', 'status': 'survived'},
                    {'module': 'do_math/b.py', 'function': 'new', 'rule': 'return_none', 'status': 'survived'},
                    {'module': 'do_math/b.py', 'function': 'unrun', 'rule': 'pass', 'status': 'not_executed'}]
        self.assertTrue(update_list(listing, outcomes, 'b1'))
        self.assertEqual([(e['function'], e['reason'], e['base']) for e in listing['entries']],
                         [('kept', 'None is its behaviour', 'b0'), ('new', '', 'b1')])
        self.assertEqual(unreasoned(listing), 1)
        self.assertFalse(update_list(listing, outcomes, 'b1'))





PROBE = '''import unittest
from pathlib import Path
MARK = Path(__file__).with_suffix('.ran')


class T(unittest.TestCase):
    def test_1_fails(self):
        self.fail('first failure')

    def test_2_runs(self):
        MARK.write_text('ran', encoding='utf-8')
'''


class ChildRunTests(unittest.TestCase):
    """A mutant needs one failing test to die, so its child stops at the first and tries the cheapest first (D9)."""

    def _child(self, root, tests, seconds):
        self.enterContext(mock.patch.object(sys, 'path', [str(root), *sys.path]))
        self.enterContext(mock.patch.object(sys, 'dont_write_bytecode', True))
        self.enterContext(mock.patch.dict(sys.modules))
        timings = root / 'timings.json'
        timings.write_text(json.dumps(seconds), encoding='utf-8')
        self.enterContext(mock.patch.object(mutation, 'TIMINGS', timings, create=True))
        spec = root / 'spec.json'
        spec.write_text(json.dumps({'tests': tests, 'folders': [], 'target': None, 'mutant': None}), encoding='utf-8')
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            mutation._child(spec)
        return json.loads((root / 'result.json').read_text(encoding='utf-8'))

    def test_a_mutant_child_stops_at_the_first_failing_test(self):
        root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        (root / 'mutation_probe_one.py').write_text(PROBE, encoding='utf-8')
        failing = self._child(root, ['mutation_probe_one.T.test_1_fails', 'mutation_probe_one.T.test_2_runs'], {})
        self.assertEqual(failing['rows'], [{'id': 'mutation_probe_one.T.test_1_fails',
                                           'outcome': 'failed', 'fixture': False}])
        self.assertEqual(failing['tests_run'], 1)
        self.assertEqual(len(failing['collected']), 2)
        self.assertFalse((root / 'mutation_probe_one.ran').exists())

    def test_the_tests_of_the_module_with_the_cheapest_recorded_tests_run_first(self):
        root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        for name in ('mutation_probe_slow', 'mutation_probe_cheap'):
            code = PROBE
            if name == 'mutation_probe_slow':
                code += "\nPath(__file__).with_suffix('.imported').write_text('imported', encoding='utf-8')\n"
            (root / f'{name}.py').write_text(code, encoding='utf-8')
        failing = self._child(root, ['mutation_probe_slow.T.test_1_fails', 'mutation_probe_cheap.T.test_1_fails'],
                              {'mutation_probe_slow': 50.0, 'mutation_probe_cheap': 1.0})
        self.assertEqual([row['id'] for row in failing['rows']], ['mutation_probe_cheap.T.test_1_fails'])
        self.assertEqual(failing['rows'][0]['outcome'], 'failed')
        self.assertFalse((root / 'mutation_probe_slow.imported').exists(),
                         'a confirmed cheap witness must stop before loading the later module')

    def test_a_surviving_cheap_module_does_not_skip_a_later_killer(self):
        root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        for name in ('mutation_probe_surviving', 'mutation_probe_later'):
            (root / f'{name}.py').write_text(PROBE, encoding='utf-8')
        failing = self._child(root,
            ['mutation_probe_surviving.T.test_2_runs', 'mutation_probe_later.T.test_1_fails'],
            {'mutation_probe_surviving': 1.0, 'mutation_probe_later': 50.0})
        self.assertEqual([(row['id'], row['outcome']) for row in failing['rows']],
                         [('mutation_probe_surviving.T.test_2_runs', 'passed'),
                          ('mutation_probe_later.T.test_1_fails', 'failed')])
        self.assertEqual((root / 'mutation_probe_surviving.ran').read_text(encoding='utf-8'), 'ran')

    def test_module_load_exception_is_reported_as_load_failure(self):
        root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        (root / 'mutation_probe_load_error.py').write_text(
            "raise TypeError('mutation import specimen')\n", encoding='utf-8')
        failing = self._child(root, ['mutation_probe_load_error.T.test_one'], {})
        self.assertEqual(failing['rows'], [])
        self.assertEqual(failing['tests_run'], 0)
        self.assertEqual(failing['load_error']['details'], ['TypeError: mutation import specimen'])
        self.assertEqual(failing['load_error']['selection']['tests'], ['mutation_probe_load_error.T.test_one'])


class MutationEvidenceTests(unittest.TestCase):
    TEST = 'unit.probe.Case.test_value'

    def _result(self, spec, outcome='passed'):
        result = mutation._new_result(spec)
        result['collected'] = list(spec['tests']) or [self.TEST]
        result['rows'] = [{'id': name, 'outcome': outcome, 'fixture': False}
                          for name in result['collected']]
        result['tests_run'] = len(result['rows'])
        return result

    def _run_with_payload(self, payload, *, source='def value():\n    return 2\n',
                          selected=None, functions=None, fallback=False):
        """Only the child process/file boundary is doubled; parent parsing and classification are real."""
        from subprocess import CompletedProcess
        from support import branch_gate
        root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        scripts = root / 'scripts'
        module = scripts / 'do_math/sample.py'
        module.parent.mkdir(parents=True)
        module.write_text(source, encoding='utf-8')
        selected = selected or [self.TEST]
        index = {'tests': selected, 'files': {'scripts/do_math/sample.py': {
            'blob': 'blob', 'functions': functions if functions is not None else {'value': list(range(len(selected)))}}}}
        self.calls = []

        def spawn(command, **options):
            spec_path = Path(command[-1])
            spec = json.loads(spec_path.read_text(encoding='utf-8'))
            self.calls.append((spec, spec_path.parent))
            result, exit_code = payload(spec)
            if result is not None:
                raw = result if isinstance(result, bytes) else json.dumps(result).encode('utf-8')
                (spec_path.parent / 'result.json').write_bytes(raw)
            options['stdout'].write('process boundary specimen\n')
            return mock.Mock(pid=123, wait=mock.Mock(return_value=exit_code), poll=mock.Mock(return_value=exit_code))

        self.enterContext(mock.patch.object(mutation, 'SCRIPTS', scripts))
        self.enterContext(mock.patch.object(mutation, '_git', lambda root, *args: CompletedProcess(
            args, 0, stdout=(b'b' * 40 if args[0] == 'rev-parse' else b''))))
        self.enterContext(mock.patch.object(branch_gate, 'git_blobs', lambda root, paths: {p: 'blob' for p in paths}))
        self.enterContext(mock.patch.object(mutation.subprocess, 'Popen', spawn))
        return mutation.run('HEAD', None if fallback else index, {'do_math/sample.py': '1'}, root, root / 'mutants',
                            listing_path=root / 'pseudo.json')

    def test_missing_corrupt_or_inconsistent_evidence_blocks_both_sides_of_a_kill(self):
        """About 0.8s: both sides of 15 evidence faults retain actual spec/result/attempt files."""
        for side in ('normal', 'mutant'):
            for fault in ('missing', 'json', 'utf8', 'list', 'legacy', 'selection', 'row', 'count', 'exit',
                          'zero', 'not_run', 'skipped', 'expected_failure', 'fixture_error', 'fixture_skip'):
                with self.subTest(side=side, fault=fault):
                    def payload(spec):
                        result = self._result(spec, 'failed' if spec['target'] else 'passed')
                        if bool(spec['target']) != (side == 'mutant'):
                            return result, 0
                        if fault == 'missing':
                            return None, 0
                        if fault == 'json':
                            return b'{', 0
                        if fault == 'utf8':
                            return b'\xff', 0
                        if fault == 'list':
                            return [], 0
                        if fault == 'legacy':
                            return {'failing': []}, 0
                        if fault == 'selection':
                            result['selection']['tests'] = ['wrong.selection.Case.test_other']
                        elif fault == 'row':
                            result['rows'][0]['id'] = 'uncollected'
                        elif fault == 'count':
                            result['tests_run'] = 2
                        elif fault == 'exit':
                            return result, 17
                        elif fault in {'zero', 'not_run'}:
                            result['rows'] = []
                            result['tests_run'] = 0
                            if fault == 'zero':
                                result['collected'] = []
                        elif fault.startswith('fixture_'):
                            result['rows'] = [{'id': 'setUpClass (unit.probe.Case)',
                                               'outcome': 'error' if fault == 'fixture_error' else 'skipped',
                                               'fixture': True}]
                            result['tests_run'] = 0
                        else:
                            result['rows'][0]['outcome'] = fault
                        return result, 0
                    report = self._run_with_payload(payload)
                    self.assertEqual(report['counts'], {'execution_error': 1})
                    self.assertFalse(mutation.passed(report))
                    self.assertEqual(report['baseline_failing'], [])
                    self.assertIn('detail', report['outcomes'][0])
                    self.assertEqual(len(report['baselines']), int(side == 'normal'))
                    for _, directory in self.calls:
                        self.assertTrue((directory / 'spec.json').is_file())
                        self.assertTrue((directory / 'output.txt').is_file())
                        self.assertTrue((directory / 'attempt.json').is_file())

    def test_elapsed_time_alone_does_not_kill_a_mutant(self):
        import itertools
        self.enterContext(mock.patch.object(mutation.time, 'monotonic', side_effect=itertools.count(0, 10000)))
        report = self._run_with_payload(lambda spec: (self._result(spec), 0))
        self.assertEqual(report['counts'], {'survived': 1})
        self.assertEqual(report['baselines'], [])
        self.assertGreaterEqual(report['outcomes'][0]['seconds'], 10000)

    def test_only_actual_normal_pass_confirms_failure_error_or_unexpected_success(self):
        """About 0.3s for the 3 mutant outcomes x 4 normal outcomes through actual file parsing."""
        for outcome in sorted(mutation.FAILURES):
            for normal in ('passed', 'failed', 'error', 'unexpected_success'):
                with self.subTest(mutant=outcome, normal=normal):
                    report = self._run_with_payload(lambda spec: (
                        self._result(spec, outcome if spec['target'] else normal), 0))
                    self.assertEqual(report['counts'], {'killed' if normal == 'passed' else 'baseline_failing': 1})
                    self.assertEqual(mutation.passed(report), normal == 'passed')
                    self.assertEqual(report['baseline_failing'], [] if normal == 'passed' else [self.TEST])

    def test_a_partial_successful_selection_cannot_be_reported_as_surviving(self):
        other = 'unit.probe.Case.test_other'
        def payload(spec):
            result = self._result(spec)
            result['rows'] = [row for row in result['rows'] if row['id'] == self.TEST]
            result['tests_run'] = 1
            return result, 0
        report = self._run_with_payload(payload, selected=[self.TEST, other])
        self.assertEqual(report['counts'], {'execution_error': 1})
        self.assertFalse(mutation.passed(report))
        self.assertIn(other, report['outcomes'][0]['detail'])
        self.assertEqual(report['baselines'], [])

    def test_load_error_requires_the_identical_normal_selection_to_actually_pass(self):
        for normal in ('passed', 'load_error', 'failed'):
            with self.subTest(normal=normal):
                def payload(spec):
                    if not spec['target'] and normal != 'load_error':
                        return self._result(spec, normal), 0
                    result = mutation._new_result(spec)
                    result['load_error'] = {'selection': mutation._selection(spec),
                                            'details': ['ImportError: specimen']}
                    return result, 0
                report = self._run_with_payload(payload)
                self.assertEqual(report['counts'], {'killed' if normal == 'passed' else 'execution_error': 1})
                self.assertEqual(mutation.passed(report), normal == 'passed')
                self.assertEqual(report['baselines'][0]['selection']['tests'], [self.TEST])
                if normal == 'passed':
                    self.assertEqual(report['outcomes'][0]['killed_by'], [self.TEST])

    def test_normal_failure_is_excluded_and_attempts_and_cached_baselines_remain_traceable(self):
        bad, good = 'unit.probe.Case.test_bad', self.TEST
        def payload(spec):
            result = self._result(spec)
            first = spec['tests'][0]
            result['rows'] = [{'id': first, 'outcome': 'failed' if spec['target'] or first == bad else 'passed',
                              'fixture': False}]
            result['tests_run'] = 1
            return result, 0
        report = self._run_with_payload(payload, selected=[bad, good],
            source='def value():\n    return 2\ndef another():\n    return 3\n',
            functions={'value': [0, 1], 'another': [0, 1]})
        self.assertEqual(report['counts'], {'killed': 2})
        self.assertEqual(report['baseline_failing'], [bad])
        self.assertFalse(mutation.passed(report))
        self.assertEqual([spec['tests'] for spec, _ in self.calls if spec['target'] is None], [[bad], [good]])
        self.assertEqual([item['status'] for item in report['baselines']], ['failing', 'passed'])
        for outcome in report['outcomes']:
            self.assertEqual([attempt['baselines'] for attempt in outcome['attempts']], [[0], [1]])
            directories = [Path(attempt['execution']['directory']) for attempt in outcome['attempts']]
            self.assertEqual(len(set(directories)), 2)
            self.assertEqual(json.loads((directories[0] / 'spec.json').read_text())['exclude'], [])
            self.assertEqual(json.loads((directories[1] / 'spec.json').read_text())['exclude'], [bad])
            self.assertEqual(json.loads((directories[0] / 'result.json').read_text())['rows'][0]['id'], bad)

    def test_fallback_keeps_layer_folders_and_unentered_and_trivial_functions_need_no_child(self):
        report = self._run_with_payload(lambda spec: (self._result(spec), 0), fallback=True)
        self.assertEqual(self.calls[0][0]['folders'], ['unit', 'contracts'])
        self.assertEqual(report['counts'], {'survived': 1})
        report = self._run_with_payload(lambda spec: self.fail('unentered function started a child'),
            source='def value():\n    return 2\ndef stub():\n    pass\n', functions={})
        self.assertEqual(report['counts'], {'not_executed': 1, 'trivial': 1})
        self.assertEqual(self.calls, [])
        self.assertFalse(mutation.passed(report))

    def test_closing_requires_measured_mutants_and_a_passing_unmutated_baseline(self):
        good = {'counts': {'killed': 3, 'trivial': 1}, 'unreasoned_entries': 0, 'baseline_failing': []}
        self.assertTrue(mutation.passed(good))
        for status in ('execution_error', 'mutation_error', 'not_executed'):
            with self.subTest(status=status):
                self.assertFalse(mutation.passed({**good, 'counts': {**good['counts'], status: 1}}))
        self.assertFalse(mutation.passed({**good, 'baseline_failing': ['unit.probe.Case.test_value']}))
        self.assertFalse(mutation.passed({**good, 'unreasoned_entries': 1}))




if __name__ == '__main__':
    unittest.main()
