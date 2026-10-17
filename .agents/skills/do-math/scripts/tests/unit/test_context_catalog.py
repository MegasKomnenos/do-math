"""The context store's file layer (``context_store``, layer 2): input materialization, source catalogs, bounded context, workspace collection.

The file system is not a port (설계 2.2), so these tests run on real temporary
folders. What a test cannot write with ordinary file calls it arranges with the
Windows API (``support.storage_files``): a directory that cannot be listed, and
audit events that show which files were opened and how often the physical
root was proved.
"""
import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest
import re

import do_math.context_store as store
from do_math.canonical import canonical_json
from do_math.file_io import PhysicalBoundary
from support.storage_files import audit_events, unlistable
from support.storage_role_inputs import catalog_opens
from support.engine_context import assert_result_documents


class ChangingMetadata:
    """Observe the real descriptor; only the OS-reported mtime differs (1 then 2 ns)."""
    def __init__(self, *, size=None):
        self.descriptors = []
        self.size = size

    def __call__(self, fd):
        from types import SimpleNamespace
        real = os.fstat(fd)
        self.descriptors.append(fd)
        return SimpleNamespace(st_size=real.st_size if self.size is None else self.size,
                               st_mtime_ns=len(self.descriptors), st_ctime_ns=real.st_ctime_ns,
                               st_birthtime_ns=getattr(real, 'st_birthtime_ns', real.st_ctime_ns))


class StableReadTests(unittest.TestCase):
    def test_metadata_change_during_one_read_is_not_one_version(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'x'
            path.write_bytes(b'bytes')
            self.assertEqual(store.read_stable(path), b'bytes')
            fstat = ChangingMetadata()
            with self.assertRaisesRegex(store._ChangedDuringRead, 'file changed while being read'):
                store.read_stable(path, fstat=fstat)
            self.assertEqual(len(fstat.descriptors), 2)
            self.assertEqual(fstat.descriptors[0], fstat.descriptors[1])

    def test_changed_during_read_is_not_success(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'x').write_bytes(b'x')
            fstat = ChangingMetadata()
            got = store.collect_outputs(root, required_paths=['x'], fstat=fstat)
            self.assertFalse(got['complete'])
            self.assertEqual(got['omitted'][0]['reason'], 'changed_during_read')
            self.assertTrue(got['omitted'][0]['required'])
            self.assertEqual(got['files'], {})
            self.assertEqual(len(fstat.descriptors), 2)
            self.assertEqual(fstat.descriptors[0], fstat.descriptors[1])

    def test_one_boundary_proves_its_root_once_for_many_reads(self):
        """A root proof (``PhysicalBoundary.check``) loads kernel32 through ctypes; collecting three files loads it as often as one proof does."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / 'sub').mkdir()
            for i in range(3):
                (root / 'sub' / f'{i}.txt').write_bytes(b'%d' % i)
            with audit_events('ctypes.dlopen') as proof:
                PhysicalBoundary(root)
            with audit_events('ctypes.dlopen') as collected:
                got = store.collect_outputs(root)
            self.assertEqual(len(got['files']), 3)
            self.assertTrue(proof)
            self.assertEqual(len(collected), len(proof))


class ContextStoreTests(unittest.TestCase):
    def test_directory_read_failure_is_an_omission_even_without_required_paths(self):
        for required in ([], ['blocked/proof.txt']):
            with self.subTest(required=required), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                (root / 'blocked').mkdir()
                (root / 'visible.txt').write_bytes(b'preserved sibling')
                # Listing the held directory fails with a sharing violation, as os.walk sees it.
                with unlistable(root / 'blocked'):
                    with self.assertRaises(PermissionError) as refused:
                        os.scandir(root / 'blocked')
                    result = store.collect_outputs(root, required_paths=required)
                self.assertEqual(result['files'], {'visible.txt': b'preserved sibling'})
                self.assertFalse(result['complete'])
                omission = next(row for row in result['omitted'] if row['path'] == 'blocked')
                self.assertEqual(omission['reason'], 'read_error')
                self.assertEqual(omission['error_type'], 'PermissionError')
                self.assertEqual(omission['required'], bool(required))
                self.assertEqual(omission['error'], str(refused.exception))

    def test_large_ongoing_preparation_is_recoverable_without_prompt_overflow(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            entries = [{'execution_id': 'E', 'status': 'running', 'reason': 'assigned obligation ' * 1000}]
            result = store.fit_context({'goal': 'g', 'ongoing_preparation': entries}, max_bytes=1200, workspace=root,
                                       mandatory_keys=['goal'])
            self.assertIsNone(result['overflow'])
            ref = result['context']['ongoing_preparation']['source_ref']
            self.assertEqual(json.loads(store.read_source(root, ref, limit=100000)['bytes']), entries)

    def test_new_catalog_is_hashed_from_the_bytes_it_wrote(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            context = {'goal': 'g', 'tasks': [{'id': 'T-1'}]}
            with audit_events('open') as opened:
                catalog = store.write_source_catalog(context, root)
            # A new catalog file is created once and never read back.
            self.assertEqual(catalog_opens(opened, root), [('goal.json', 'x'), ('tasks.json', 'x')])
            for key, value in context.items():
                logical = 'input/catalog/' + key + '.json'
                data = canonical_json(value)
                self.assertEqual(catalog['files'][logical], data)
                self.assertEqual(catalog['entries'][key]['sha256'], hashlib.sha256(data).hexdigest())
                self.assertEqual((root / logical).read_bytes(), data)
                ref = catalog['entries'][key]
                self.assertEqual(ref['path'], logical)
                assert_result_documents(self, ref, root, owner='source_ref', expected=value)
                from support.doc_code import result_field_issues
                self.assertEqual(result_field_issues('`source_ref.passed`', 'source_ref', ref),
                                 [('actual field', 'source_ref.passed')])
                for fault in ('path', 'sha256', 'bytes'):
                    changed = dict(ref)
                    if fault == 'path':
                        changed['path'] = catalog['entries']['tasks' if key == 'goal' else 'goal']['path']
                    elif fault == 'sha256':
                        changed['sha256'] = '0' * 64
                    else:
                        changed['bytes'] += 1
                    reason = (f"{len(data)} != {changed['bytes']}" if fault == 'bytes' else
                              hashlib.sha256((root / changed['path']).read_bytes()).hexdigest())
                    with self.subTest(key=key, fault=fault), self.assertRaisesRegex(AssertionError, re.escape(reason)):
                        assert_result_documents(self, changed, root, owner='source_ref', expected=value)
            self.assertEqual(catalog['total'], len(context))
            # Existing catalog files are still compared before reuse.
            (root / 'input/catalog/goal.json').write_bytes(b'"other"')
            with self.assertRaisesRegex(FileExistsError, 'catalog path contains different bytes: input/catalog/goal.json'):
                store.write_source_catalog(context, root)

    def test_materialize_and_invalid_utf8_round_trip(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            data = b'\xff\x00abc'
            result = store.materialize_inputs(root, {'sources/raw.bin': data})
            ref = result['manifest'][0]
            self.assertEqual((root / ref['path']).read_bytes(), data)
            read = store.read_source(root, {**ref, 'format': 'bytes'}, limit=99)
            self.assertEqual(read['status'], 'ok')
            self.assertEqual(read['bytes'], data)
            self.assertFalse(read['truncated'])

    def test_traversal_and_absolute_paths_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            for name, message in (('../x', 'unsafe relative path: ../x'),
                                  ('/absolute', 'unsafe relative path: /absolute'),
                                  ('C:/absolute', 'path must be a nonempty relative POSIX path'),
                                  ('a\\b', 'path must be a nonempty relative POSIX path')):
                with self.subTest(name=name), self.assertRaisesRegex(ValueError, message):
                    store.materialize_inputs(Path(d), {name: b'x'})
            self.assertFalse((Path(d) / 'input').exists() and any((Path(d) / 'input').iterdir()))

    def test_collect_preserves_outputs_and_excludes_noise(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            for folder, name, raw in (('input', 'x', b'in'), ('.git', 'x', b'g'), ('__pycache__', 'x', b'p'),
                                      ('src', 'main.lean', b'lean')):
                (root / folder).mkdir()
                (root / folder / name).write_bytes(raw)
            (root / 'checkpoint.bin').write_bytes(b'\xffcp')
            got = store.collect_outputs(root, required_paths=['src/main.lean', 'checkpoint.bin'])
            self.assertTrue(got['complete'])
            self.assertEqual(got['files']['checkpoint.bin'], b'\xffcp')
            self.assertEqual(set(got['files']), {'src/main.lean', 'checkpoint.bin'})

    def test_required_missing_and_limit_are_incomplete(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / 'large').write_bytes(b'x' * 20)
            got = store.collect_outputs(root, required_paths=['missing', 'large'], max_bytes=5)
            self.assertFalse(got['complete'])
            self.assertEqual({x['reason'] for x in got['omitted']}, {'required_missing', 'max_bytes_exceeded'})

    def test_invalid_empty_capture_does_not_disappear(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(TypeError, 'captured_files must be'):
                store.collect_outputs(Path(d), captured_files=[])

    @unittest.skipUnless(hasattr(os, 'symlink'), 'symlink unavailable')
    def test_outside_symlink_is_reported_when_supported(self):
        with tempfile.TemporaryDirectory() as d, tempfile.TemporaryDirectory() as outside:
            root = Path(d)
            target = Path(outside) / 'secret'
            target.write_bytes(b's')
            try:
                (root / 'link').symlink_to(target)
            except OSError as error:
                self.skipTest(str(error))
            got = store.collect_outputs(root, required_paths=['link'])
            self.assertFalse(got['complete'])
            self.assertEqual(got['omitted'][0]['reason'], 'outside_symlink')

    def test_catalog_and_overflow_history_preserve_exact_values(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / 'new-workspace'
            context = {'goal': 'g', 'action': {'role': 'plan'},
                       'recent_history': [{'n': i, 'text': 'x' * 100} for i in range(40)],
                       'tasks': [{'id': 'T1', 'title': 't', 'question': 'q', 'status': 'ready',
                                  'completion_criteria': ['c'], 'detail': 'y' * 1000},
                                 {'id': 'T2', 'status': 'completed'}],
                       'knowledge_catalog': [{'id': 'K', 'detail': 'z' * 2000}]}
            fitted = store.fit_context(context, max_bytes=1200, workspace=root, mandatory_keys=['goal', 'action'])
            self.assertIsNone(fitted['overflow'])
            self.assertLessEqual(fitted['actual_bytes'], 1200)
            self.assertTrue(fitted['reductions'])
            task_reduction = next(x for x in fitted['reductions'] if x['key'] == 'tasks')
            self.assertEqual(json.loads(store.read_source(root, task_reduction['source_ref'], limit=10 ** 7)['bytes']),
                             context['tasks'])
            ref = next(x for x in fitted['manifest'] if x['key'] == 'recent_history')
            raw = store.read_source(root, ref, limit=10 ** 7)
            self.assertEqual(json.loads(raw['bytes']), context['recent_history'])
            for key in ('tasks', 'knowledge_catalog', 'recent_history'):
                projected = fitted['context'][key]
                if isinstance(projected, dict) and 'source_ref' in projected:
                    assert_result_documents(self, projected['source_ref'], root, owner='source_ref',
                                            expected=context[key], total=projected['total'])

    def test_packed_sizes_equal_the_canonical_bytes_of_the_packed_context(self):
        nested = {'deep': [{'a': [1, [2, {}], []], 'b': '\u00e9\u2028'}], 'empty': {}}
        contexts = [{'goal': 'g', 'empty_list': [], 'empty_map': {}, 'text': 'line\none', 'nested': nested,
                     'numbers': list(range(30))},
                    {'goal': 'g'}, {'goal': 'x' * 1000, 'recent_history': [1, 2, 3], 'tasks': [{'id': 'T', 'detail': 'y' * 500}]}]
        for index, context in enumerate(contexts):
            for limit in (10, 300, 10 ** 6):
                with self.subTest(context=index, limit=limit), tempfile.TemporaryDirectory() as d:
                    got = store.fit_context(context, max_bytes=limit, workspace=Path(d), mandatory_keys=['goal'])
                    self.assertEqual(got['actual_bytes'], len(canonical_json(got['context'])))
                    self.assertEqual(got['original_bytes'], len(canonical_json(context)))
                    if got['overflow']:
                        self.assertEqual(got['overflow']['mandatory_bytes'], len(canonical_json({'goal': context['goal']})))

    def test_mandatory_overflow_reports_size_without_reduction(self):
        with tempfile.TemporaryDirectory() as d:
            context = {'goal': 'x' * 1000, 'recent_history': [1, 2, 3]}
            got = store.fit_context(context, max_bytes=100, workspace=Path(d), mandatory_keys=['goal'])
            self.assertEqual(got['overflow']['reason'], 'mandatory_context_exceeds_limit')
            self.assertEqual(got['context']['goal'], context['goal'])

    def test_read_source_range_missing_and_hash_error(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mat = store.materialize_inputs(root, {'x.bin': b'abcdef'})
            ref = mat['manifest'][0]
            part = store.read_source(root, ref, limit=2)
            self.assertEqual(part['bytes'], b'ab')
            self.assertTrue(part['truncated'])
            self.assertEqual(part['range'], {'start': 0, 'end': 2, 'total': 6})
            self.assertEqual(store.read_source(root, {'path': 'input/nope', 'sha256': '0', 'bytes': 1})['status'], 'missing')
            for fault, expected in (('sha256', 'source hash differs from reference'),
                                    ('bytes', 'source size differs from reference')):
                changed = {**ref, fault: '0' * 64 if fault == 'sha256' else ref['bytes'] + 1}
                error = store.read_source(root, changed)
                self.assertEqual((error['status'], error['error_type'], error['reason']),
                                 ('error', 'ValueError', expected))
                self.assertEqual(error['bytes'], b'')
                self.assertIsNone(error['range'])


if __name__ == '__main__':
    unittest.main()
