"""T0 selection from the index and its safety rules (설계 5.3), judged on synthetic files, diffs and indexes."""
import unittest

from support.selection import (Paths, code_owners, importing_test_modules, region_anchors, select_with_index,
                               select_without_index, usable)

PREFIX = 'skill/scripts'
LAYERS = {'do_math/core.py': '2', 'do_math/wiring.py': '3', 'do_math/io.py': 'adapter'}
OLD = '''"""Module docstring."""
import os


def first(x):
    """Doc."""
    total = (x +
             1)
    if total:
        return total
    return 0


def second(y):
    # a comment
    return y * 2
'''
TESTS = ['unit.test_core.T.test_first', 'unit.test_core.T.test_second', 'sim.test_flow.F.test_all']
INDEX = {'format': 'do-math-selection-index/2', 'commit': 'c0', 'tests': TESTS, 'files': {
    f'{PREFIX}/do_math/core.py': {'blob': 'old', 'functions': {'first': [0, 2], 'second': [1]}},
    f'{PREFIX}/tests/unit/test_core.py': {'blob': 't1'},
    f'{PREFIX}/tests/support/helper.py': {'blob': 'h1', 'functions': {'help': [2]}},
    'skill/schemas/record.json': {'blob': 's1', 'readers': [1]},
    'skill/schemas/loaded.json': {'blob': 'l1', 'readers': []},
}}
NESTED = 'def f(c):\n    if c:\n        g()\n\n\ndef g():\n    pass\n'


def _select(current, texts, old_texts=None, graph=None):
    blobs = {**{path: entry['blob'] for path, entry in INDEX['files'].items()}, **current}
    blobs = {path: blob for path, blob in blobs.items() if blob is not None}
    old_texts = {'old': OLD, **(old_texts or {})}
    return select_with_index(INDEX, blobs, old_texts.get, texts.get, Paths(PREFIX, LAYERS),
                             lambda: graph or {})


class CodeLineTests(unittest.TestCase):
    def test_blank_comment_and_docstring_lines_are_not_code_and_a_continuation_belongs_to_its_statement(self):
        owners = code_owners(OLD)
        self.assertEqual(owners[8], 7)
        self.assertNotIn(1, owners)
        self.assertNotIn(6, owners)
        self.assertNotIn(15, owners)
        self.assertNotIn(4, owners)
        self.assertEqual(owners[16], 16)

    def test_a_comment_or_docstring_edit_has_no_code_region(self):
        self.assertEqual(region_anchors(OLD, OLD.replace('# a comment', '# another comment')), [])
        self.assertEqual(region_anchors(OLD, OLD.replace('"""Doc."""', '"""Other doc."""')), [])

    def test_a_replacement_is_anchored_at_its_old_statements_and_an_insertion_at_its_neighbours(self):
        [region] = region_anchors(OLD, OLD.replace('    return 0\n', '    return -1\n'))
        self.assertEqual(region['anchors'], [11])
        [region] = region_anchors(OLD, OLD.replace('             1)\n', '             1)\n    total += 0\n'))
        self.assertEqual(region['anchors'], [7, 9])


class IndexSelectionTests(unittest.TestCase):
    def test_a_changed_line_selects_the_tests_that_entered_its_function(self):
        new = OLD.replace('    return 0\n', '    return -1\n').replace('return y * 2', 'return y * 3')
        selection = _select({f'{PREFIX}/do_math/core.py': 'new'}, {f'{PREFIX}/do_math/core.py': new})
        self.assertEqual((selection.tests, selection.folders), (set(TESTS), set()))
        selection = _select({f'{PREFIX}/do_math/core.py': 'new'},
                            {f'{PREFIX}/do_math/core.py': OLD.replace('return y * 2', 'return y * 3')})
        self.assertEqual((selection.tests, selection.folders), ({TESTS[1]}, set()))

    def test_an_inserted_line_selects_the_tests_that_entered_its_function(self):
        new = OLD.replace('             1)\n', '             1)\n    total += 0\n')
        selection = _select({f'{PREFIX}/do_math/core.py': 'new'}, {f'{PREFIX}/do_math/core.py': new})
        self.assertEqual((selection.tests, selection.folders), ({TESTS[0], TESTS[2]}, set()))

    def test_a_line_added_after_a_nested_block_at_the_end_of_a_function_selects_every_test_that_entered_it(self):
        # Line level anchored this at the block's last statement and the next def: tests that skipped the block
        # reach the new line but ran neither neighbour.
        path = f'{PREFIX}/do_math/wiring.py'
        index = {**INDEX, 'files': {path: {'blob': 'n1', 'functions': {'f': [0, 1], 'g': [0]}}}}
        new = NESTED.replace('        g()\n', '        g()\n    raise RuntimeError\n')
        selection = select_with_index(index, {path: 'n2'}, {'n1': NESTED}.get, {path: new}.get, Paths(PREFIX, LAYERS),
                                      lambda: {})
        self.assertEqual((selection.tests, selection.folders), ({TESTS[0], TESTS[1]}, set()))

    def test_a_changed_definition_header_runs_at_import_and_takes_the_layer(self):
        new = OLD.replace('def second(y):', 'def second(y=1):')
        selection = _select({f'{PREFIX}/do_math/core.py': 'new'}, {f'{PREFIX}/do_math/core.py': new})
        self.assertEqual((selection.tests, selection.folders), (set(), {'unit', 'contracts'}))

    def test_a_changed_test_file_selects_that_whole_module(self):
        selection = _select({f'{PREFIX}/tests/unit/test_core.py': 't2'}, {})
        self.assertEqual((selection.modules, selection.tests), ({'unit.test_core'}, set()))
        self.assertTrue(selection.picks('unit.test_core.Other.test_x'))
        self.assertFalse(selection.picks('unit.test_other.T.test_x'))

    def test_a_new_product_file_or_a_line_the_index_does_not_know_selects_the_module_layer_tests(self):
        selection = _select({f'{PREFIX}/do_math/wiring.py': 'w1'}, {})
        self.assertEqual(selection.folders, {'sim'})
        new = OLD.replace('import os\n', 'import os\nLIMIT = 3\n')
        selection = _select({f'{PREFIX}/do_math/core.py': 'new'}, {f'{PREFIX}/do_math/core.py': new})
        self.assertEqual((selection.tests, selection.folders), (set(), {'unit', 'contracts'}))

    def test_a_changed_input_selects_its_readers(self):
        selection = _select({'skill/schemas/record.json': 's2'}, {})
        self.assertEqual(selection.tests, {TESTS[1]})

    def test_a_changed_input_with_no_test_to_credit_selects_every_selectable_folder(self):
        selection = _select({'skill/schemas/loaded.json': 'l2'}, {})
        self.assertEqual((selection.tests, selection.folders), (set(), {'unit', 'contracts', 'sim'}))

    def test_a_measured_text_git_no_longer_has_selects_every_test_of_the_file_and_the_layer(self):
        selection = _select({f'{PREFIX}/do_math/core.py': 'new'}, {f'{PREFIX}/do_math/core.py': OLD},
                            old_texts={'old': None})
        self.assertEqual((selection.tests, selection.folders), (set(TESTS), {'unit', 'contracts'}))

    def test_a_non_product_module_selects_the_test_modules_importing_it(self):
        graph = {'support.helper': {'os'}, 'support.sim': {'support.helper'}, 'sim.test_flow': {'support.sim'},
                 'unit.test_core': {'do_math.core'}}
        selection = _select({f'{PREFIX}/tests/support/helper.py': 'h2'},
                            {f'{PREFIX}/tests/support/helper.py': 'import os\n'}, old_texts={'h1': 'import os\n'},
                            graph=graph)
        self.assertEqual(selection.modules, set())
        selection = _select({f'{PREFIX}/tests/support/helper.py': 'h2'},
                            {f'{PREFIX}/tests/support/helper.py': 'import sys\n'}, old_texts={'h1': 'import os\n'},
                            graph=graph)
        self.assertEqual((selection.tests, selection.modules), (set(), {'sim.test_flow'}))
        selection = _select({f'{PREFIX}/tests/support/helper.py': 'h2'},
                            {f'{PREFIX}/tests/support/helper.py': 'def help():\n    return 2\n'},
                            old_texts={'h1': 'def help():\n    return 1\n'}, graph=graph)
        self.assertEqual((selection.tests, selection.modules), ({TESTS[2]}, set()))
        self.assertEqual(importing_test_modules(graph, 'support.helper'), {'sim.test_flow'})

    def test_an_unchanged_tree_selects_nothing(self):
        selection = _select({}, {})
        self.assertEqual((selection.tests, selection.modules, selection.folders), (set(), set(), set()))


class FallbackTests(unittest.TestCase):
    def test_a_missing_or_stale_index_falls_back_to_module_level_selection(self):
        self.assertEqual(usable(None, 'no selection index', lambda commit: True), (None, 'no selection index'))
        self.assertEqual(usable(INDEX, '', lambda commit: commit == 'c0'), (INDEX, ''))
        stale, reason = usable(INDEX, '', lambda commit: False)
        self.assertIsNone(stale)
        self.assertIn('not an ancestor of HEAD', reason)
        selection = select_without_index(
            {f'{PREFIX}/do_math/core.py', f'{PREFIX}/do_math/io.py', f'{PREFIX}/tests/sim/test_flow.py',
             'skill/references/guide.md', 'docs/plan.md', f'{PREFIX}/tests/test_legacy.py'},
            Paths(PREFIX, LAYERS), lambda: {}, 'no selection index')
        self.assertEqual(selection.mode, 'fallback')
        self.assertEqual(selection.modules, {'sim.test_flow'})
        self.assertEqual(selection.folders, {'unit', 'contracts', 'sim'})
        self.assertEqual({change['path'] for change in selection.reasons},
                         {f'{PREFIX}/do_math/core.py', f'{PREFIX}/do_math/io.py', f'{PREFIX}/tests/sim/test_flow.py',
                          'skill/references/guide.md'})


if __name__ == '__main__':
    unittest.main()
