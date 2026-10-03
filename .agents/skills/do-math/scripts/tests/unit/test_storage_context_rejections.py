"""문서·catalog·role manifest의 외곽을 유지한 입력 거부와 실제 파일 결과."""
import hashlib
from pathlib import Path
import re
import tempfile
import unittest

from do_math.context_store import (build_role_manifest, collect_outputs, fit_context,
                                   materialize_inputs, read_source, safe_path, write_source_catalog,
                                   readable_snapshot_path, read_refusal, read_content)
from do_math.canonical import canonical_json
from do_math.payloads import encode, seal_large, LIMIT
from do_math.file_io import PhysicalBoundary


class ContextRejections(unittest.TestCase):
    def test_read_authority_checks_blocked_families_before_index_and_ledger(self):
        path = 'runtime/tasks/TK-one.json'
        context = {'record_index': {'runtime/tasks': ['TK-one']},
                   'record_map': {'ledger': 'readable', 'blocked_keys': ['runtime/tasks']}}
        self.assertFalse(readable_snapshot_path(context, path))
        for invalid in (None, '', 'outside/file', 'runtime'):
            self.assertFalse(readable_snapshot_path(context, invalid))
        del context['record_map']['blocked_keys']
        self.assertTrue(readable_snapshot_path(context, path))
        self.assertTrue(readable_snapshot_path(context, 'runtime/other/row.json'))
        context['record_map']['ledger'] = 'restricted'
        self.assertFalse(readable_snapshot_path(context, 'runtime/other/row.json'))
        self.assertTrue(readable_snapshot_path(context, 'research/questions/Q-one.json'))
        context['result'] = {'artifact_ref': 'runtime/artifacts/BA-one/result.txt'}
        self.assertTrue(readable_snapshot_path(context, context['result']['artifact_ref']))
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.assertIsNone(read_refusal(context, root, path, 'out.txt'))
            self.assertEqual(read_refusal(context, root, path, 'input/out.txt'),
                             '--output must not write into the fixed input/')
            self.assertTrue(read_refusal(context, root, path, '../out.txt').startswith(
                '--output needs a workspace-relative path: '))
            self.assertEqual(read_refusal(context, root, None, None),
                             'outside the record map of this input (record_index and record_map.ledger)')

    def test_read_content_decodes_payload_record_text_and_binary_separately(self):
        record = {'text': 'A' * LIMIT}
        envelope, blobs = encode({'contract_id': 'test', 'family': 'test',
                                  'record': seal_large(record.copy())})
        self.assertEqual(read_content('research/test/R-one.json', canonical_json(envelope), blobs.__getitem__),
                         {'record': record})
        for path in ('research/_state/manifest.json', 'runtime/artifacts/BA-one/raw'):
            self.assertEqual(read_content(path, b'{}\n', blobs.__getitem__), {'text': '{}\n'})
            self.assertEqual(read_content(path, b'\xff', blobs.__getitem__), {'base64': '/w=='})

    def test_materialization_validates_all_inputs_before_any_file_write(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with self.assertRaisesRegex(TypeError, '^documents must be a path-to-bytes object$'):
                materialize_inputs(root, [])
            with self.assertRaisesRegex(TypeError, '^document must be bytes: z.txt$'):
                materialize_inputs(root, {'a.txt': b'valid', 'z.txt': 'not bytes'})
            self.assertEqual(list(root.iterdir()), [])
            result = materialize_inputs(root, {'a.txt': b'abc'})
            self.assertEqual(result, {'input_root': 'input', 'manifest': [
                {'path': 'input/a.txt', 'sha256': hashlib.sha256(b'abc').hexdigest(), 'bytes': 3}]})
            with self.assertRaisesRegex(FileExistsError, '^input path already exists: input/a.txt$'):
                materialize_inputs(root, {'a.txt': b'changed'})
            self.assertEqual((root / 'input/a.txt').read_bytes(), b'abc')
            with self.assertRaisesRegex(ValueError, '^source reference must stay below input/$'):
                safe_path(root, 'outside.txt', require_input=True)

    def test_capture_validation_and_missing_workspace_results_are_exact(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for kwargs, kind, reason in (
                    ({'max_bytes': True}, ValueError, 'max_bytes must be a nonnegative integer'),
                    ({'required_paths': ()}, TypeError, 'required_paths must be a list'),
                    ({'captured_files': []}, TypeError, 'captured_files must be a path-to-bytes object'),
                    ({'captured_files': {'input/a': b'a'}}, ValueError, 'captured research file is excluded: input/a'),
                    ({'captured_files': {'a': 'text'}}, TypeError, 'captured research file must be bytes: a')):
                with self.subTest(kwargs=kwargs), self.assertRaisesRegex(kind, '^' + re.escape(reason) + '$'):
                    collect_outputs(root, **kwargs)
            self.assertEqual(collect_outputs(root / 'absent', required_paths=['a']),
                {'files': {}, 'manifest': [], 'omitted': [{'path': 'a', 'reason': 'workspace_missing'}], 'complete': False})

    def test_manifest_field_validation_and_missing_catalog_entry(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            base = {'workspace': root, 'role': 'research_work', 'direct_keys': ['a'], 'reference_keys': ['b']}
            for changes, kind, reason in (
                    ({'role': ''}, ValueError, 'role must be a non-empty string'),
                    ({'direct_keys': ['a', 'a']}, ValueError, 'direct_keys must contain distinct string keys'),
                    ({'reference_keys': ['a']}, ValueError, 'a role input cannot be both direct and referenced: a'),
                    ({'reference_keys': ['missing']}, ValueError, 'role manifest keys are missing: missing')):
                with self.subTest(changes=changes), self.assertRaisesRegex(kind, '^' + re.escape(reason) + '$'):
                    build_role_manifest({'a': 1, 'b': 2}, **{**base, **changes})
            catalog = write_source_catalog({'a': 1, 'b': 2}, root)
            del catalog['entries']['b']
            with self.assertRaisesRegex(ValueError, '^reference key has no exact catalog entry: b$'):
                build_role_manifest({'a': 1, 'b': 2}, **base, catalog=catalog)

    def test_fit_limits_and_physical_boundary_modes_are_explicit(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for changes, kind, reason in (
                    ({'context': []}, TypeError, 'context must be an object'),
                    ({'max_bytes': True}, ValueError, 'max_bytes must be a positive integer'),
                    ({'mandatory_keys': ['a', 'a']}, ValueError, 'mandatory_keys must contain distinct string keys'),
                    ({'mandatory_keys': ['missing']}, ValueError, 'mandatory context keys are missing: missing')):
                options = {'context': {'a': 1}, 'workspace': root, 'max_bytes': 1000, 'mandatory_keys': []}
                with self.subTest(changes=changes), self.assertRaisesRegex(kind, '^' + reason + '$'):
                    fit_context(**{**options, **changes})
            with self.assertRaisesRegex(ValueError, '^limit must be a positive integer$'):
                read_source(root, {'path': 'input/a'}, limit=0)
            boundary = PhysicalBoundary(root)
            with self.assertRaisesRegex(ValueError, '^physical boundary supports read or exclusive creation$'):
                with boundary.open(root / 'a', 'wb'):
                    self.fail('쓰기 모드가 허용됨')
            with self.assertRaisesRegex(ValueError, '^file path is outside the physical boundary$'):
                with boundary.open(root.parent / 'outside', 'rb'):
                    self.fail('외부 경로가 허용됨')
            with self.assertRaisesRegex(ValueError, '^physical boundary root must be an existing directory$'):
                PhysicalBoundary(root / 'missing')

    def test_catalog_ingress_rejects_nonobjects_and_unsafe_keys_without_writing(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for call in (
                    lambda: write_source_catalog([], root),
                    lambda: build_role_manifest([], workspace=root, role='research_work',
                                                direct_keys=[], reference_keys=[])):
                with self.subTest(call=call), self.assertRaises(TypeError) as rejected:
                    call()
                self.assertIs(type(rejected.exception), TypeError)
                self.assertEqual(str(rejected.exception), 'context must be an object')
                self.assertEqual(list(root.iterdir()), [])
            for key in ('', '../outside', 'space key', 'x/y'):
                with self.subTest(key=key), self.assertRaises(ValueError) as rejected:
                    write_source_catalog({key: []}, root)
                self.assertIs(type(rejected.exception), ValueError)
                self.assertEqual(str(rejected.exception), 'context key cannot be a catalog filename: ' + key)
                self.assertEqual(list(root.iterdir()), [])

    def test_source_ref_rejection_keeps_the_materialized_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            raw = b'\xff\x00exact\r\n'
            ref = materialize_inputs(root, {'source.bin': raw})['manifest'][0]
            before = (root / ref['path']).read_bytes()
            for malformed, reason in (
                    ([], 'source ref must contain a path'),
                    ({**ref, 'path': None}, 'source ref must contain a path'),
                    ({**ref, 'bytes': len(raw) + 1}, 'source size differs from reference')):
                with self.subTest(reference=malformed):
                    result = read_source(root, malformed)
                    self.assertEqual(result, {
                        'status': 'error', 'path': malformed.get('path') if isinstance(malformed, dict) else None,
                        'bytes': b'', 'sha256': None, 'range': None,
                        'truncated': False, 'reason': reason, 'error_type': 'ValueError'})
                    self.assertIs(type(result['bytes']), bytes)
                    self.assertIs(type(result['truncated']), bool)
                    self.assertEqual((root / ref['path']).read_bytes(), before)
            self.assertEqual(read_source(root, ref)['bytes'], raw)


if __name__ == '__main__':
    unittest.main()
