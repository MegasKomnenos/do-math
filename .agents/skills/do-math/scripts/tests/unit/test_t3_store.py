"""The T3 store's invalidation (설계 A29): which test modules an incremental T3 measures again and which it reuses."""
from pathlib import Path
import tempfile
import unittest

from support.t3_store import FORMAT, code_digests, module_records, path_mapper, plan, records, reused_data

SOURCE = '''"""A module."""
import os

LIMIT = 3


def first(x):
    """Doc."""
    if x:
        return x
    return 0


class Box:
    def put(self, value):
        return value


def second(y):
    return y * 2
'''


class DigestTests(unittest.TestCase):
    def test_a_body_edit_changes_only_that_function_and_no_module_level_code(self):
        old, new = code_digests(SOURCE), code_digests(SOURCE.replace('return 0', 'return -1'))
        self.assertEqual(old['top'], new['top'])
        self.assertEqual({key for key in old['functions'] if old['functions'][key] != new['functions'].get(key)},
                         {'first'})

    def test_a_line_added_above_moves_and_so_changes_every_function_below(self):
        """Stored arcs are line numbers: a function that only moved cannot reuse them."""
        old = code_digests(SOURCE)
        new = code_digests(SOURCE.replace('        return x\n', '        x += 1\n        return x\n'))
        self.assertEqual(old['top'], new['top'])
        self.assertEqual({key for key in old['functions'] if old['functions'][key] != new['functions'].get(key)},
                         {'first', 'Box', 'Box.put', 'second', '<module>'})

    def test_module_and_class_level_code_changes_the_top(self):
        old = code_digests(SOURCE)['top']
        for edit in (SOURCE.replace('LIMIT = 3', 'LIMIT = 4'), SOURCE.replace('def second(y):', 'def second(y=1):'),
                     SOURCE + '\n\ndef third():\n    return 3\n',
                     SOURCE.replace('class Box:\n', 'class Box:\n    size = 1\n\n')):
            self.assertNotEqual(code_digests(edit)['top'], old, edit)

    def test_a_docstring_or_comment_edit_that_keeps_the_lines_changes_nothing(self):
        edited = SOURCE.replace('"""Doc."""', '"""Other."""').replace('return y * 2', 'return y * 2  # twice')
        self.assertEqual(code_digests(edited), code_digests(SOURCE))


class _Tree:
    """The current tree: blobs and code digests by repository path; a missing path is absent."""

    def __init__(self, blobs, texts):
        self._blobs, self._texts = blobs, texts

    def blobs(self, paths):
        return {path: self._blobs.get(path) for path in paths}

    def digests(self, path):
        return code_digests(self._texts[path]) if path in self._texts else None

    def source(self, path):
        return self._texts.get(path)


P = 's/do_math/core.py'
SUPPORT = 's/tests/support/helper.py'


def _records():
    digests = code_digests(SOURCE)
    return {'format': FORMAT, 'coverage': 'v', 'root': 'r',
            'tops': {P: digests['top'], SUPPORT: code_digests('def help():\n    return 1\n')['top']},
            'runner': {'s/run_tests.py': 'r1'}, 'import_inputs': {'s/schema.json': 'i1'},
            'modules': {
                'unit.test_a': {'tests': ['unit.test_a.T.test_1'], 'blob': 'a1',
                                'functions': {P: {'first': digests['functions']['first']}}, 'inputs': {}},
                'unit.test_b': {'tests': ['unit.test_b.T.test_1'], 'blob': 'b1',
                                'functions': {P: {'second': digests['functions']['second']}},
                                'inputs': {'s/role.md': 'd1'}},
                'unit.test_gone': {'tests': ['unit.test_gone.T.test_1'], 'blob': 'g1', 'functions': {}, 'inputs': {}}}}


def _plan(texts=None, blobs=None, universe=('unit.test_a', 'unit.test_b', 'unit.test_new'), full=False, records=None):
    current = {'s/tests/unit/test_a.py': 'a1', 's/tests/unit/test_b.py': 'b1', 's/tests/unit/test_new.py': 'n1',
               's/run_tests.py': 'r1', 's/schema.json': 'i1', 's/role.md': 'd1', **(blobs or {})}
    tree = _Tree(current, {P: SOURCE, SUPPORT: 'def help():\n    return 1\n', **(texts or {})})
    return plan(_records() if records is None else records, set(universe), set(universe), tree, 's',
                coverage_version='v', full=full)


class PlanTests(unittest.TestCase):
    def test_an_unchanged_tree_reuses_every_stored_module_measures_new_ones_and_drops_gone_ones(self):
        result = _plan()
        self.assertEqual((result.mode, result.measure, result.reuse, result.drop),
                         ('incremental', {'unit.test_new'}, {'unit.test_a', 'unit.test_b'}, {'unit.test_gone'}))

    def test_a_changed_test_module_or_a_changed_function_it_entered_is_measured_again(self):
        result = _plan(blobs={'s/tests/unit/test_a.py': 'a2'})
        self.assertEqual((result.measure, result.reuse), ({'unit.test_a', 'unit.test_new'}, {'unit.test_b'}))
        result = _plan(texts={P: SOURCE.replace('return y * 2', 'return y * 3')})
        self.assertEqual((result.measure, result.reuse), ({'unit.test_b', 'unit.test_new'}, {'unit.test_a'}))

    def test_a_changed_input_measures_the_modules_that_opened_it(self):
        result = _plan(blobs={'s/role.md': 'd2'})
        self.assertEqual((result.measure, result.reuse), ({'unit.test_b', 'unit.test_new'}, {'unit.test_a'}))

    def test_module_level_code_the_runner_or_an_input_read_at_import_measures_everything_again(self):
        for changes in ({'texts': {P: SOURCE.replace('LIMIT = 3', 'LIMIT = 4')}},
                        {'texts': {SUPPORT: 'X = 1\n\n\ndef help():\n    return 1\n'}},
                        {'blobs': {'s/run_tests.py': 'r2'}}, {'blobs': {'s/schema.json': 'i2'}}):
            result = _plan(**changes)
            self.assertEqual((result.mode, result.reuse), ('full', set()), changes)
            self.assertEqual(result.measure, {'unit.test_a', 'unit.test_b', 'unit.test_new'})

    def test_every_categories_change_invalidates_the_runner_measurement(self):
        stored = _records()
        stored['runner']['s/test_categories.py'] = 'categories-blob'
        self.assertEqual(_plan(blobs={'s/test_categories.py': 'categories-blob'}, records=stored).mode, 'incremental')
        for blob in ('changed-labels', 'changed-isolation-body', 'changed-comment', None):
            with self.subTest(blob=blob):
                result = _plan(blobs={'s/test_categories.py': blob}, records=stored)
                self.assertEqual((result.mode, result.reason, result.reuse), ('full', 'the runner changed', set()))
                self.assertEqual(result.measure, {'unit.test_a', 'unit.test_b', 'unit.test_new'})

    def test_no_store_another_coverage_or_a_forced_full_run_measures_everything(self):
        self.assertEqual(_plan(records={}).mode, 'full')
        self.assertEqual(_plan(full=True).mode, 'full')
        other = {**_records(), 'coverage': 'w'}
        self.assertEqual(_plan(records=other).mode, 'full')


class ModuleRecordTests(unittest.TestCase):
    def test_a_module_relies_on_what_its_tests_fixtures_and_restored_shared_builds_entered_and_opened(self):
        entered = {'unit.test_a.T.test_1': [[P, 'first'], ['<shared>', 'sim:activated']],
                   'fixture:unit.test_a': [[P, 'second']],
                   'shared:sim:activated': [[P, 'Box.put']],
                   'unit.test_b.T.test_1': [[P, 'second']]}
        opens = {'unit.test_a.T.test_1': ['s/role.md'], 'unit.test_b.T.test_1': ['s/other.md']}
        tree = _Tree({'s/tests/unit/test_a.py': 'a1', 's/role.md': 'd1'}, {P: SOURCE})
        records = module_records({'unit.test_a': ['unit.test_a.T.test_1']}, entered, opens, tree, 's')
        digests = code_digests(SOURCE)['functions']
        self.assertEqual(records, {'unit.test_a': {
            'tests': ['unit.test_a.T.test_1'], 'blob': 'a1', 'inputs': {'s/role.md': 'd1'},
            'functions': {P: {name: digests[name] for name in ('Box.put', 'first', 'second')}}}})
        stored = {**_records(), 'modules': records}
        moved = SOURCE.replace('        return value\n', '        value += 0\n        return value\n')
        result = plan(stored, {'unit.test_a'}, {'unit.test_a'},
                      _Tree({**{p: b for p, b in _records()['runner'].items()}, 's/tests/unit/test_a.py': 'a1',
                             's/role.md': 'd1', 's/schema.json': 'i1'}, {P: moved, SUPPORT: 'def help():\n    return 1\n'}),
                      's', coverage_version='v')
        self.assertEqual((result.measure, result.why['unit.test_a']), ({'unit.test_a'}, f'entered {P}:Box.put changed'))


class RecordTests(unittest.TestCase):
    def test_module_level_digests_cover_product_support_and_fixture_code_but_no_test_module_or_runner_file(self):
        """Legacy tests/test_*.py modules come and go through stage 1f; they must not measure everything again."""
        root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        texts = {'s/do_math/core.py': 'X = 1\n', 's/tests/support/helper.py': 'def h():\n    return 1\n',
                 's/tests/research_fixtures.py': 'Y = 2\n', 's/tests/unit/test_a.py': 'import unittest\n',
                 's/tests/test_legacy.py': 'import unittest\n', 's/run_tests.py': 'Z = 3\n'}
        for path, text in texts.items():
            (root / path).parent.mkdir(parents=True, exist_ok=True)
            (root / path).write_text(text, encoding='utf-8')
        record = records(root, root / 's', {}, {}, {}, {}, _Tree({}, texts), 'v')
        self.assertEqual(sorted(record['tops']),
                         ['s/do_math/core.py', 's/tests/research_fixtures.py', 's/tests/support/helper.py'])


class ReusedDataTests(unittest.TestCase):
    def test_only_the_reused_modules_contexts_are_kept_and_moved_to_this_tree(self):
        from coverage import CoverageData
        root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        old, new = root / 'old', root / 'new'
        (root / 'store').mkdir()
        stored = CoverageData(basename=str(root / 'store' / 'coverage.data'))
        for context, arcs in (('unit.test_a', [(-1, 2), (2, 3)]), ('fixture:unit.test_a', [(-1, 5)]),
                              ('unit.test_b', [(3, 4)]), ('', [(-1, 1)])):
            stored.set_context(context)
            stored.add_arcs({str(old / 'm.py'): arcs})
        stored.write()
        kept = reused_data(root / 'store', {'unit.test_a'}, root / 'kept.data')
        target = CoverageData(basename=str(root / 'target.data'))
        target.set_context('unit.test_c')
        target.add_arcs({str(new / 'm.py'): [(7, 8)]})
        target.update(CoverageData(basename=str(kept)), map_path=path_mapper(str(old), str(new)))
        self.assertEqual(sorted(target.arcs(str(new / 'm.py'))), [(-1, 2), (-1, 5), (2, 3), (7, 8)])
        self.assertEqual(target.measured_files(), {str(new / 'm.py')})


if __name__ == '__main__':
    unittest.main()
