"""The T3 branch-reach gate and the selection index, judged on synthetic coverage data (설계 5.3, 5.5)."""
import re
import unittest

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
                            created='t', scripts_prefix='s')
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
        index = build_index(entered, self.TESTS, opens, import_opens, blobs, 'c0', scripts_prefix='s')
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
        (saved / OPENED).write_text(json.dumps({'opens': {'unit.test_a.A.test_x': ['in.json']}, 'import_opens': {}}),
                                    encoding='utf-8')
        (saved / ENTERED).write_text(json.dumps({'unit.test_a.A.test_x': [['m.py', 'f']]}), encoding='utf-8')
        measurement = Measurement(root, data_file=root / 'coverage.data')
        self.assertEqual(measurement.merge([saved, timed_out]), [timed_out])
        self.assertEqual(dict(measurement.opens), {'unit.test_a.A.test_x': {'in.json'}})
        self.assertEqual(measurement.entered(), {'unit.test_a.A.test_x': [['m.py', 'f']]})
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


if __name__ == '__main__':
    unittest.main()
