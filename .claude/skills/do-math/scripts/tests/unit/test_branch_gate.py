"""The T3 branch-reach gate and the selection index, judged on synthetic coverage data (설계 5.3, 5.5)."""
import re
import unittest

from support.branch_gate import REASONED_EXCLUSION, build_index, fixture_label, gate

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

    def test_lines_are_credited_to_their_test_to_every_test_of_a_fixture_module_and_never_to_imports(self):
        files = {'s/do_math/m.py': {'contexts': {
            '3': [''], '5': ['unit.test_a.A.test_two'], '7': [fixture_label('unit.test_a.A.test_two', 'sim.test_b.B.test_three')],
            '9': ['', 'sim.test_b.B.test_three']}}}
        index = build_index(files, self.TESTS, {}, {}, {'s/do_math/m.py': 'b1'}, 'c0', created='t')
        entry = index['files']['s/do_math/m.py']
        self.assertEqual(entry, {'blob': 'b1', 'lines': {'5': [1], '7': [0, 1, 2], '9': [2]}})
        self.assertEqual((index['commit'], index['tests']), ('c0', self.TESTS))

    def test_an_input_is_credited_to_its_openers_and_an_import_time_open_to_the_opener_module_tests(self):
        files = {'s/do_math/m.py': {'contexts': {'4': ['sim.test_b.B.test_three']}}}
        opens = {'unit.test_a.A.test_one': {'skill/schema.json'}}
        index = build_index(files, self.TESTS, opens, {'skill/table.json': {'s/do_math/m.py'}},
                            {'s/do_math/m.py': 'b1', 'skill/schema.json': 'b2', 'skill/table.json': 'b3'}, 'c0')
        self.assertEqual(index['files']['skill/schema.json'], {'blob': 'b2', 'readers': [0]})
        self.assertEqual(index['files']['skill/table.json'], {'blob': 'b3', 'readers': [2]})

    def test_the_fixture_label_names_the_modules_on_both_sides(self):
        self.assertEqual(fixture_label(None, 'unit.test_a.A.test_one'), 'fixture:unit.test_a')
        self.assertEqual(fixture_label('unit.test_a.A.test_one', 'sim.test_b.B.test_three'),
                         'fixture:sim.test_b,unit.test_a')


if __name__ == '__main__':
    unittest.main()
