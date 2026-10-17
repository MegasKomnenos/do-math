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



class PhysicalCollectionTests(unittest.TestCase):
    def test_captured_limit_and_excluded_nested_files_keep_exact_omissions(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'src' / '__pycache__').mkdir(parents=True)
            (root / 'src' / '__pycache__' / 'skip.pyc').write_bytes(b'noise')
            (root / 'input').write_bytes(b'excluded root file')
            captured = {'large': b'1234', 'small': b'x'}
            got = collect_outputs(root, captured_files=captured, required_paths=['large', 'small'], max_bytes=2)
            self.assertEqual(got['files'], {'small': b'x'})
            self.assertEqual(got['omitted'], [{'path': 'large', 'reason': 'max_bytes_exceeded', 'bytes': 4, 'required': True}])
            self.assertFalse(got['complete'])

    def test_directory_junction_is_omitted_and_cannot_be_read_as_evidence(self):
        from support.provider_probes import junction
        from do_math.context_store import read_stable
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'real').mkdir()
            (root / 'real' / 'data').write_bytes(b'keep')
            link = root / 'junction'
            junction(link, root / 'real')
            try:
                got = collect_outputs(root)
                self.assertEqual(got['files'], {'real/data': b'keep'})
                self.assertEqual(got['omitted'], [{'path': 'junction', 'reason': 'reparse_directory'}])
                self.assertFalse(got['complete'])
                with self.assertRaisesRegex(ValueError, '^physical boundary rejected read: physical path crosses'):
                    read_stable(link / 'data')
            finally:
                link.rmdir()

    def test_collection_records_disappearance_and_permission_at_open(self):
        import errno
        import os
        from support.engine_control import on_audit
        for fault, reason in [('missing', 'disappeared'), ('denied', 'read_error')]:
            with self.subTest(fault=fault), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                nested = root / 'nested'; nested.mkdir()
                target = nested / 'value'; target.write_bytes(b'original')
                seen = []
                def at_open(arguments):
                    if os.path.normcase(os.path.abspath(arguments[0])) != os.path.normcase(str(target)) or seen:
                        return
                    seen.append(str(arguments[0]))
                    if fault == 'missing': target.unlink()
                    else: raise PermissionError(errno.EACCES, 'fixture denied', str(target))
                with on_audit('open', at_open):
                    got = collect_outputs(root, required_paths=['nested/value'])
                self.assertEqual(got['files'], {})
                self.assertEqual([(x['path'], x['reason'], x['required']) for x in got['omitted']],
                                 [('nested/value', reason, True)])
                self.assertFalse(got['complete'])
                if fault == 'denied':
                    self.assertEqual(got['omitted'][0]['error_type'], 'PermissionError')

class RoleInputBoundaryTests(unittest.TestCase):
    def test_role_profile_snapshot_governance_and_archive_rejections_are_exact(self):
        from copy import deepcopy
        from do_math.context_store import prepare_role_input
        from support.record_builders import surface_state
        from support.fakes.clock import FakeClock
        instance, runtime = surface_state()
        profile = next(p for p in instance['execution_profiles'].values() if p['role'] == 'maintenance')
        for fault, message in [
            ('profile', 'selected profile does not match the input role'),
            ('snapshot', 'input snapshot must be a fixed Git commit'),
            ('governance', 'role requires adopted governance'),
            ('archive', 'role input archive must stay in runtime/artifacts/')]:
            with self.subTest(fault=fault), tempfile.TemporaryDirectory() as directory:
                options = dict(context={'action': {'id': 'AC-boundary', 'role': 'maintenance'}},
                    instance=deepcopy(instance), runtime=runtime, role='maintenance', profile=profile,
                    snapshot='a'*40, workspace=Path(directory), activity_id='AC-boundary', clock=FakeClock())
                if fault == 'profile': options['role'] = 'research_work'
                elif fault == 'snapshot': options['snapshot'] = 'HEAD'
                elif fault == 'governance': options['instance'].pop('governance', None)
                else: options['artifact_prefix'] = 'outside/archive'
                with self.assertRaises(ValueError) as caught: prepare_role_input(**options)
                self.assertEqual(str(caught.exception), message)

    def test_resume_lineage_rejects_wrong_action_and_absent_owner_without_writing(self):
        from do_math.context_store import restore_continuation
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            action = {'role': 'research_work', 'target': 'TK-one', 'continuation_of': 'EX-prior'}
            valid = {'id': 'EX-prior', 'status': 'ended', 'role': 'research_work',
                     'action': {'target': 'TK-one'}, 'owner_activity_id': 'AC-one'}
            for execution, reason in [({**valid, 'action': {'target': 'TK-other'}}, "resume lineage does not identify this action's ended execution"),
                                       ({**valid, 'status': 'running'}, "resume lineage does not identify this action's ended execution"),
                                       ({**valid, 'owner_activity_id': None}, 'resume lineage requires an owner activity')]:
                with self.subTest(reason=reason), self.assertRaises(ValueError) as caught:
                    restore_continuation({'executions': {'EX-prior': execution}}, action, root,
                        snapshot='a'*40, read_artifact=lambda path: self.fail('must not read artifacts'))
                self.assertEqual(str(caught.exception), reason)
                self.assertEqual(list(root.iterdir()), [])

    def test_manifest_rejects_mutable_snapshot_before_reading_components(self):
        from do_math.context_store import validate_role_manifest
        with self.assertRaisesRegex(ValueError, '^input manifest requires fixed snapshot$'):
            validate_role_manifest({'role': 'maintenance', 'snapshot': 'HEAD'})



class ReviewInputBoundaryTests(unittest.TestCase):
    def test_review_input_rejects_missing_cycle_seat_and_unverified_transcript(self):
        from copy import deepcopy
        from do_math import review_cycle
        from do_math.context_store import prepare_role_input
        from support.record_builders import surface_state
        from support.fakes.clock import FakeClock
        instance, runtime = surface_state()
        profile = next(p for p in instance['execution_profiles'].values() if p['role'] == 'identity_review')
        cycle = review_cycle.start_review({'id': 'KN-one', 'revision': 1}, reviewers=1)
        seat, = review_cycle.next_actions(cycle)
        expected = review_cycle.context_for(cycle, seat)
        for fault, message in [('cycle', 'review input has no current cycle'),
                ('seat', 'review requires seat-scoped role_review input'),
                ('private', 'another review seat transcript is private'),
                ('bytes', 'review transcript source bytes could not be verified')]:
            with self.subTest(fault=fault), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                ref = materialize_inputs(root, {'transcript.txt': b'original transcript'})['manifest'][0]
                supplied = deepcopy(expected)
                if fault == 'seat': supplied = None
                elif fault in {'private', 'bytes'}:
                    supplied['source_refs'] = [{**ref, 'local_path': ref['path'],
                        'sha256': '0'*64 if fault == 'bytes' else ref['sha256'],
                        'slot': 'another' if fault == 'private' else seat['slot']}]
                running = {**runtime, 'review_cycles': {} if fault == 'cycle' else {'RC-one': cycle}}
                context = {'action': {'id': 'AC-review', 'role': 'identity_review', 'review_cycle_id': 'RC-one', **seat},
                           'role_review': supplied}
                with self.assertRaises(ValueError) as caught:
                    prepare_role_input(context, instance=instance, runtime=running, role='identity_review',
                        profile=profile, snapshot='a'*40, workspace=root, activity_id='AC-review', clock=FakeClock())
                self.assertEqual(str(caught.exception), message)
                self.assertEqual((root / ref['path']).read_bytes(), b'original transcript')

    def test_repeated_live_overflow_keeps_one_unresolved_condition(self):
        from do_math.context_store import defer_input_overflow
        from support.record_builders import surface_state
        _, runtime = surface_state()
        overflow = {'activity_id': 'AC-1', 'kind': 'input_overflow', 'limit_bytes': 1}
        first = defer_input_overflow(runtime, overflow, at='2026-09-20T00:00:01Z', question_ref='Q-one')
        second = defer_input_overflow(runtime, overflow, at='2026-09-20T00:00:02Z', question_ref='Q-one')
        self.assertEqual(first, second)
        self.assertEqual(first['status'], 'working')
        self.assertEqual(runtime['activities']['AC-1']['unresolved'], [first['condition']])
        self.assertEqual(runtime['activities']['AC-1']['status'], 'working')

    def test_collection_preserves_physical_refusal_after_directory_becomes_junction(self):
        import os
        from support.engine_control import on_audit
        from support.provider_probes import junction
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            nested, displaced = root / 'nested', root / 'displaced'
            nested.mkdir(); (nested / 'proof').write_bytes(b'exact')
            seen = []
            def replace_at_traversal(arguments):
                if os.path.abspath(arguments[0]) == str(nested) and not seen:
                    seen.append(True)
                    nested.rename(displaced)
                    junction(nested, displaced)
            try:
                with on_audit('os.scandir', replace_at_traversal):
                    got = collect_outputs(root, required_paths=['nested/proof'])
                self.assertEqual(seen, [True])
                self.assertFalse(got['complete'])
                row, = [row for row in got['omitted'] if row['path'] == 'nested/proof']
                self.assertEqual((row['reason'], row['error_type'], row['required']),
                                 ('physical_boundary', '_PhysicalBoundaryError', True))
                self.assertIn('physical boundary rejected read: physical path crosses a reparse point', row['error'])
            finally:
                if nested.is_junction(): nested.rmdir()


class OverflowProfileBoundaryTests(unittest.TestCase):
    """Full role prompt/catalog rendering costs about 0.5 s for the three actual profile choices."""
    def test_overflow_offers_only_a_current_distinct_profile_that_fits_the_actual_input(self):
        from copy import deepcopy
        from do_math import contracts, execution_profiles
        from do_math.context_store import prepare_role_input
        from support.record_builders import surface_state
        from support.fakes.clock import FakeClock
        instance, runtime = surface_state()
        original = next(p for p in instance['execution_profiles'].values()
                        if p['role'] == 'research_work' and p['ai']['tier'] == 'high')
        fixed = len(execution_profiles.prepare_prompt(contracts.render_prompt('research_work', {}), original).encode('utf-8'))
        body = deepcopy(original)
        body['input']['max_input_bytes'] = fixed + 50000
        profile = execution_profiles.seal_profile(body)
        instance['execution_profiles'][profile['id']] = profile
        reference = execution_profiles.profile_ref(profile)
        alternate_body = deepcopy(profile)
        alternate_body['input']['max_input_bytes'] += 1000
        alternate = execution_profiles.seal_profile(alternate_body)
        instance['execution_profiles'][alternate['id']] = alternate
        for fault in ['same', 'stale', 'insufficient']:
            with self.subTest(fault=fault), tempfile.TemporaryDirectory() as directory:
                offered = reference if fault == 'same' else {**reference, 'sha256': '0'*64}
                offers = [reference, execution_profiles.profile_ref(alternate)] if fault == 'insufficient' else [offered]
                task = {'id': 'TK-overflow', 'profile_refs': offers, 'evidence': 'x'*70000}
                runtime['tasks'] = {task['id']: task}
                context = {'action': {'id': 'AC-overflow', 'role': 'research_work', 'target': task['id']}, 'task': task}
                result = prepare_role_input(context, instance=instance, runtime=runtime, role='research_work',
                    profile=profile, snapshot='a'*40, workspace=Path(directory), activity_id='AC-1', clock=FakeClock())
                overflow = result['overflow']
                self.assertEqual(overflow['cause'], 'required_role_input')
                self.assertEqual(overflow['allowed_profile_candidates'], [])
                self.assertEqual(overflow['resolution_question']['next_owner'], 'user')
                self.assertEqual(result['validation_context']['task'], task)

if __name__ == '__main__':
    unittest.main()
