"""The T3 branch-reach gate and the selection index, judged on synthetic coverage data (설계 5.3, 5.5)."""
import re
from pathlib import Path
import unittest
from unittest import mock

from support.branch_gate import (FORMAT, REASONED_EXCLUSION, FunctionRecorder, build_index, fixture_label,
                                 function_key, gate, module_label)

PREFIX = 'skill/scripts'
LAYERS = {'do_math/a.py': '1', 'do_math/b.py': '2', 'do_math/c.py': '3', 'do_math/io.py': 'adapter',
          'tool.py': '3'}


def _file(missing_branches=(), missing_lines=(), excluded=()):
    return {'missing_branches': [list(arc) for arc in missing_branches], 'missing_lines': list(missing_lines),
            'excluded_lines': list(excluded)}


class GateTests(unittest.TestCase):
    def test_every_gap_of_a_layer_one_to_three_module_fails_and_adapters_are_not_judged(self):
        files = {f'{PREFIX}/do_math/a.py': _file(excluded=[7, 8]),
                 f'{PREFIX}/do_math/b.py': _file(missing_branches=[(4, 6), (9, -1)]),
                 f'{PREFIX}/do_math/c.py': _file(missing_lines=[12]),
                 f'{PREFIX}/do_math/io.py': _file(missing_branches=[(1, 2)], missing_lines=[3])}
        result = gate(files, LAYERS, PREFIX)
        self.assertFalse(result['passed'])
        self.assertEqual(result['judged_modules'], 4)
        self.assertEqual(sorted(result['modules']), ['do_math/b.py', 'do_math/c.py', 'tool.py'])
        self.assertEqual(result['modules']['do_math/b.py']['missing_branches'], [[4, 6], [9, -1]])
        self.assertEqual((result['missing_branches'], result['missing_lines'], result['excluded_lines']), (2, 1, 2))
        self.assertEqual(result['unmeasured_modules'], ['tool.py'])

    def test_a_module_set_with_every_branch_and_line_reached_passes(self):
        files = {f'{PREFIX}/{module}': _file() for module in LAYERS}
        result = gate(files, LAYERS, PREFIX)
        self.assertEqual((result['passed'], result['modules_with_gaps'], result['modules']), (True, 0, {}))

    def test_only_an_exclusion_that_states_a_reason_excludes(self):
        pattern = re.compile(REASONED_EXCLUSION)
        self.assertIsNotNone(pattern.search('x = 1  # pragma: no cover - reached only by the direct script'))
        self.assertIsNotNone(pattern.search('x = 1  # pragma: no cover: Windows only'))
        self.assertIsNone(pattern.search('x = 1  # pragma: no cover'))
        self.assertIsNone(pattern.search('x = 1  # pragma: no cover -  '))


class IndexTests(unittest.TestCase):
    TESTS = ['unit.test_a.A.test_one', 'unit.test_a.A.test_two', 'sim.test_b.B.test_three']

    def test_functions_are_credited_to_their_test_to_every_test_of_a_fixture_module_and_never_to_imports(self):
        entered = {'': [['s/do_math/m.py', 'f']], 'unit.test_a.A.test_two': [['s/do_math/m.py', 'g']],
                   fixture_label('unit.test_a.A.test_two', 'sim.test_b.B.test_three'): [['s/do_math/m.py', 'h']],
                   'sim.test_b.B.test_three': [['s/do_math/m.py', 'g']]}
        index = build_index(entered, self.TESTS, {}, {}, {'s/do_math/m.py': 'b1', 's/do_math/n.py': 'b2'}, 'c0',
                            created='t', scripts_prefix='s', input_dependencies={})
        self.assertEqual(index['files']['s/do_math/m.py'], {'blob': 'b1', 'functions': {'g': [1, 2], 'h': [0, 1, 2]}})
        self.assertEqual(index['files']['s/do_math/n.py'], {'blob': 'b2', 'functions': {}})
        self.assertEqual((index['commit'], index['tests'], index['format']), ('c0', self.TESTS, FORMAT))

    def test_an_input_is_credited_to_its_openers_and_an_import_time_open_to_the_opener_module_tests(self):
        entered = {'sim.test_b.B.test_three': [['s/do_math/m.py', 'f']]}
        opens = {'unit.test_a.A.test_one': {'skill/schema.json'}}
        import_opens = {'skill/table.json': {'s/do_math/m.py'}, 'skill/corpus.json': {'s/tests/unit/test_a.py'},
                        'skill/unused.json': {'s/do_math/n.py'}}
        blobs = {'s/do_math/m.py': 'b1', 'skill/schema.json': 'b2', 'skill/table.json': 'b3',
                 'skill/corpus.json': 'b4', 'skill/unused.json': 'b5'}
        index = build_index(entered, self.TESTS, opens, import_opens, blobs, 'c0', scripts_prefix='s', input_dependencies={})
        self.assertEqual(index['files']['skill/schema.json'], {'blob': 'b2', 'readers': [0]})
        self.assertEqual(index['files']['skill/table.json'], {'blob': 'b3', 'readers': [2]})
        self.assertEqual(index['files']['skill/corpus.json'], {'blob': 'b4', 'readers': [0, 1]})
        self.assertEqual(index['files']['skill/unused.json'], {'blob': 'b5', 'readers': []})

    def test_the_fixture_label_names_the_modules_on_both_sides(self):
        self.assertEqual(fixture_label(None, 'unit.test_a.A.test_one'), 'fixture:unit.test_a')
        self.assertEqual(fixture_label('unit.test_a.A.test_one', 'sim.test_b.B.test_three'),
                         'fixture:sim.test_b,unit.test_a')

    def test_coverage_is_labelled_by_test_module_and_the_recorder_by_test(self):
        self.assertEqual(module_label('unit.test_a.A.test_one'), 'unit.test_a')
        self.assertEqual(module_label('fixture:sim.test_b,unit.test_a'), 'fixture:sim.test_b,unit.test_a')
        self.assertEqual(module_label(''), '')


class MergeTests(unittest.TestCase):
    def test_stopping_an_unstarted_merger_preserves_the_active_measurement(self):
        from support import branch_gate
        root = Path(__file__).resolve().parents[6]
        active = branch_gate.Measurement(root)
        merger = branch_gate.Measurement(root)
        with mock.patch.object(branch_gate, '_ACTIVE', active):
            merger.abandon()
            self.assertIs(branch_gate._ACTIVE, active)

    def test_a_worker_that_left_no_measurement_is_reported_missing_and_the_others_still_merge(self):
        """결함 D6: a worker that timed out never saved; combining must not end the whole run with no report."""
        import json
        from pathlib import Path
        import tempfile
        from coverage import CoverageData
        from support.branch_gate import DATA, ENTERED, OPENED, Measurement
        root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        saved, timed_out = root / 'parallel-0', root / 'parallel-1'
        saved.mkdir()
        timed_out.mkdir()
        data = CoverageData(basename=str(saved / DATA))
        data.set_context('unit.test_a')
        data.add_lines({str(root / 'm.py'): [1, 2]})
        data.write()
        (saved / OPENED).write_text(json.dumps({'opens': {'unit.test_a.A.test_x': ['in.json']}, 'import_opens': {},
                                                   'input_dependencies': {}}),
                                    encoding='utf-8')
        (saved / ENTERED).write_text(json.dumps({'unit.test_a.A.test_x': [['m.py', 'f']]}), encoding='utf-8')
        measurement = Measurement(root, data_file=root / 'coverage.data')
        self.assertEqual(measurement.merge([saved, timed_out]), [timed_out])
        self.assertEqual(dict(measurement.opens), {'unit.test_a.A.test_x': {'in.json'}})
        self.assertEqual(measurement.entered(), {'unit.test_a.A.test_x': [['m.py', 'f']]})
        self.assertEqual(measurement.input_dependencies(), {})
        self.assertEqual(sorted(measurement.coverage.get_data().lines(str(root / 'm.py'))), [1, 2])


class RecorderTests(unittest.TestCase):
    def test_a_lambda_or_generator_expression_is_credited_to_the_function_holding_it(self):
        self.assertEqual(function_key('f.<locals>.<lambda>'), 'f')
        self.assertEqual(function_key('C.m.<locals>.<genexpr>'), 'C.m')
        self.assertEqual(function_key('f.<locals>.inner'), 'f.<locals>.inner')
        self.assertEqual(function_key('<lambda>'), '')

    def test_each_label_keeps_the_functions_entered_under_it_once_however_often_they_ran(self):
        namespace = {}
        exec(compile('def f(n):\n    return [g(i) for i in range(n)]\n\n\ndef g(i):\n    return i\n\n\n'
                     'def unused():\n    return 0\n', __file__, 'exec'), namespace)
        recorder = FunctionRecorder(__file__, tool=4)
        recorder.start()
        try:
            recorder.switch('unit.test_a.A.test_one')
            namespace['f'](3)
            recorder.switch('unit.test_a.A.test_two')
            namespace['g'](1)
            recorder.switch('')
            namespace['f'](1)
        finally:
            recorder.stop()
        named = {label: sorted(code.co_qualname for code in codes) for label, codes in recorder.entered.items()}
        self.assertEqual(named, {'unit.test_a.A.test_one': ['f', 'g'], 'unit.test_a.A.test_two': ['g']})


class _NoCoverage:
    """Coverage that is not running: a measurement's context switches go nowhere."""

    def switch_context(self, label):
        pass


def _recording(prefix):
    """A measurement whose function recorder watches ``prefix`` on a spare tool id, coverage left off."""
    from support.branch_gate import Measurement
    measurement = Measurement(Path(__file__).resolve().parents[6])
    measurement.coverage = _NoCoverage()
    measurement.calls = FunctionRecorder(prefix, tool=4)
    return measurement


class ProcessCacheTests(unittest.TestCase):
    TESTS = ['unit.test_a.A.test_one', 'unit.test_a.A.test_two']

    def test_every_test_that_calls_a_cached_function_enters_it_and_what_it_calls(self):
        """결함 D2: a process cache ran its body in the first test only; each test must be credited."""
        namespace = {}
        exec(compile('import functools\n\n\n@functools.lru_cache(maxsize=None)\ndef table():\n    return helper()\n\n\n'
                     'def helper():\n    return 1\n', __file__, 'exec'), namespace)
        measurement = _recording(__file__)
        measurement.calls.start()
        try:
            measurement.begin(self.TESTS)
            for test in self.TESTS:
                measurement.test_started(test)
                namespace['table']()
                measurement.test_stopped(test)
        finally:
            measurement.calls.stop()
        named = {label: sorted(code.co_qualname for code in codes if code.co_qualname in ('table', 'helper'))
                 for label, codes in measurement.calls.entered.items()}
        self.assertEqual((named.get(self.TESTS[0]), named.get(self.TESTS[1])), (['helper', 'table'], ['helper', 'table']))

    def test_what_a_shared_template_build_ran_is_credited_to_every_test_that_restores_the_template(self):
        """결함 D2: a Sim template is built once per process; the tests that only restore it rely on its build too."""
        from pathlib import Path
        from unittest import mock
        from support import branch_gate
        root = Path(__file__).resolve().parents[6]
        source = branch_gate.TESTS / 'support' / 'shared_state_probe.py'  # a support path; the file need not exist
        namespace = {}
        exec(compile('def build():\n    return activate()\n\n\ndef activate():\n    return 1\n', str(source), 'exec'),
             namespace)
        measurement = _recording(str(source))
        self.enterContext(mock.patch.object(branch_gate, '_ACTIVE', measurement))
        measurement.calls.start()
        try:
            measurement.begin(self.TESTS)
            measurement.test_started(self.TESTS[0])
            with branch_gate.shared_state('probe'):
                namespace['build']()
            branch_gate.used_state('probe')
            measurement.test_stopped(self.TESTS[0])
            measurement.test_started(self.TESTS[1])
            branch_gate.used_state('probe')
            measurement.test_stopped(self.TESTS[1])
        finally:
            measurement.calls.stop()
        path = Path(source).relative_to(root).as_posix()
        prefix = branch_gate.SCRIPTS.relative_to(root).as_posix()
        index = build_index(measurement.entered(), self.TESTS, {}, {}, {path: 'b1'}, 'c0', scripts_prefix=prefix,
                            input_dependencies=measurement.input_dependencies())
        self.assertEqual(index['files'][path]['functions'], {'activate': [0, 1], 'build': [0, 1]})


class SharedDependencyTests(unittest.TestCase):
    def test_function_dependencies_follow_transitive_use_edges_without_rewriting_entries(self):
        from copy import deepcopy
        from support.branch_gate import credited_functions, shared_labels
        entered = {'unit.test_a.T.test_consume': [['<shared>', 'outer']],
                   'unit.test_b.T.test_passive': [],
                   'shared:outer': [['p.py', 'outer'], ['<shared>', 'inner'], ['<shared>', 'inner']],
                   'shared:inner': [['p.py', 'inner'], ['<shared>', 'outer']],
                   'shared:unused': [['p.py', 'unused']]}
        before = deepcopy(entered)
        self.assertEqual(shared_labels(entered, 'unit.test_a.T.test_consume'), {'shared:inner', 'shared:outer'})
        self.assertEqual(credited_functions(entered, 'unit.test_a.T.test_consume'),
                         {('p.py', 'outer'), ('p.py', 'inner')})
        self.assertEqual(credited_functions(entered, 'unit.test_b.T.test_passive'), set())
        self.assertEqual(entered, before)

    def test_paused_uses_and_failed_nested_builds_leave_no_consumer_edge_or_active_producer(self):
        from unittest import mock
        from support import branch_gate
        measurement = _recording(__file__)
        branch_gate._install_hook()
        self.enterContext(mock.patch.object(branch_gate, '_ACTIVE', measurement))
        measurement.calls.start()
        try:
            measurement.begin(['unit.test_a.T.test_passive'])
            measurement.test_started('unit.test_a.T.test_passive')
            with mock.patch.object(branch_gate, '_PAUSED', True):
                branch_gate.used_state('paused')
                with branch_gate.shared_state('paused'):
                    pass
            with self.assertRaisesRegex(ValueError, 'failed'):
                with branch_gate.shared_state('outer'):
                    with branch_gate.shared_state('inner'):
                        raise ValueError('failed')
            self.assertEqual(measurement.producers, [])
            self.assertEqual(dict(measurement.calls.users), {})
            self.assertEqual(measurement.input_dependencies(), {})
            self.assertEqual(measurement.context, 'unit.test_a.T.test_passive')
        finally:
            measurement.calls.stop()


if __name__ == '__main__':
    unittest.main()
