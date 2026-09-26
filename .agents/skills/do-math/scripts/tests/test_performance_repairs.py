"""Focused performance contracts; no compiler, provider or child process.

Git transport and engine lifecycle prerequisites are synthetic where marked.
Artifact hashes, event numbering, submission validation and metadata parsing
use the installed implementations.
"""
from copy import deepcopy
import hashlib
from pathlib import Path
from types import SimpleNamespace
import sys
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from test_categories import test_group as category
from do_math import contracts, engine as engine_module, events, repository, submission
from do_math.context_store import prefetch_artifacts
from do_math.git_store import GitStateStore, GitStateStoreError, StateSnapshot
from do_math.state_checks import inspect_state
from do_math.state_contract import default_state_contract


def artifact(path, raw, **changes):
    return {"artifact_ref": path, "sha256": hashlib.sha256(raw).hexdigest(),
            "bytes": len(raw), **changes}


def storage_state(refs):
    return ({"feature_version": 5, "sources": []},
            {"feature_version": 5, "executions": {"EX-1": {"id": "EX-1", "output_files": refs}}})


@category('unit')
class BatchedInspectionTests(unittest.TestCase):
    def inspect(self, refs, single, batch=None):
        return inspect_state(*storage_state(refs), requested_areas=['record_storage'],
                             read_artifact=single, read_artifacts=batch)

    def test_batch_keeps_each_reference_check_and_binary_bytes(self):
        files = {'runtime/artifacts/BA-1/empty': b'',
                 'runtime/artifacts/BA-1/raw': b'\x00\xff\r\nblob missing\n'}
        refs = [artifact(path, raw) for path, raw in files.items()]
        refs.append(artifact(next(iter(files)), b'', sha256='0' * 64))
        expected = self.inspect(refs, files.__getitem__)
        single = Mock(side_effect=AssertionError('normal batch must not read files again'))
        batch = Mock(side_effect=lambda paths: {path: files[path] for path in paths})
        self.assertEqual(self.inspect(refs, single, batch), expected)
        self.assertEqual(expected['status'], 'blocked')
        batch.assert_called_once_with(list(files))
        single.assert_not_called()

    def test_failed_batch_preserves_individual_error_order_and_scope(self):
        files = {'runtime/artifacts/BA-1/bad': b'changed',
                 'runtime/artifacts/BA-1/good': b'good'}
        paths = [*files, 'runtime/artifacts/BA-1/missing']
        refs = [artifact(paths[0], b'original'), artifact(paths[1], b'good'), artifact(paths[2], b'')]

        def read(path):
            if path not in files:
                raise FileNotFoundError('missing fixture: ' + path)
            return files[path]

        expected = self.inspect(refs, read)
        single = Mock(side_effect=read)
        batch = Mock(side_effect=GitStateStoreError('one requested blob is missing'))
        self.assertEqual(self.inspect(refs, single, batch), expected)
        self.assertEqual([call.args[0] for call in single.call_args_list], paths)
        self.assertEqual([row['status'] for row in expected['findings']], ['blocked', 'incomplete'])

    def test_next_inspection_reads_fresh_bytes(self):
        path = 'runtime/artifacts/BA-1/raw'
        files = {path: b'original'}
        refs = [artifact(path, files[path])]
        batch = Mock(side_effect=lambda paths: {name: files[name] for name in paths})
        self.assertEqual(self.inspect(refs, files.__getitem__, batch)['status'], 'healthy')
        files[path] = b'changed'
        self.assertEqual(self.inspect(refs, files.__getitem__, batch)['status'], 'blocked')
        self.assertEqual(batch.call_count, 2)

    def test_empty_or_unavailable_batch_needs_no_new_reader_contract(self):
        single = Mock(return_value=b'single')
        batch = Mock(return_value={})
        self.assertIs(prefetch_artifacts([], single, batch), single)
        batch.assert_not_called()
        self.assertIs(prefetch_artifacts(['one'], single), single)
        read = prefetch_artifacts(['one'], single, batch)
        self.assertEqual(read('one'), b'single')
        self.assertEqual(read('another'), b'single')

    def test_engine_entry_checks_presence_and_length_while_check_compares_bytes(self):
        head = 'a' * 40
        output_path = 'runtime/artifacts/BA-output/result.bin'
        input_path = 'runtime/artifacts/BA-input/input.txt'
        files = {output_path: b'\x00\xff', input_path: b'exact prompt'}
        instance, runtime = storage_state([artifact(output_path, files[output_path])])
        runtime['executions']['EX-1'].update(input_bundle='BA-input',
            input_sha256=hashlib.sha256(files[input_path]).hexdigest())
        engine = engine_module.ResearchEngine.__new__(engine_module.ResearchEngine)
        engine.instance, engine.runtime, engine.head = instance, runtime, head
        engine.store = Mock()
        engine.store.load.return_value = (head, instance, runtime)
        engine.store.read.side_effect = AssertionError('normal inspection must use batch reads')

        def batch(paths, snapshot):
            self.assertEqual(snapshot, head)
            engine.head = 'b' * 40  # Later callbacks must retain the observed snapshot.
            return {path: files[path] for path in paths}

        def sizes(paths, snapshot):
            self.assertEqual(snapshot, head)
            missing = [path for path in paths if path not in files]
            if missing:
                raise GitStateStoreError('batch size did not return a blob: ' + missing[0])
            return {path: len(files[path]) for path in paths}

        engine.store.read_many.side_effect = batch
        engine.store.blob_sizes.side_effect = sizes
        # This fixture exercises artifact inspection, not lifecycle activation.
        with patch.object(engine_module, '_require_current_contract'),                 patch.object(engine_module, 'inspect_current_state', return_value={'valid': True}):
            engine._inspect_before_write()
            # Entry to run/controls reads no artifact bytes: same-length changes are check's.
            self.assertEqual(engine.store.read_many.call_count, 0)
            files[input_path] = b'exact prompX'
            engine._inspect_before_write()
            engine.head = head
            result = engine.check(requested_areas=['record_storage'])
            self.assertFalse(result['passed'])
            self.assertIn(input_path, result['errors'][0])
            del files[input_path]
            engine.head = head
            with self.assertRaisesRegex(ValueError, 'input artifact is missing'):
                engine._inspect_before_write()
            files[output_path] = b'\x00'
            with self.assertRaisesRegex(ValueError, 'repaired before publication'):
                engine._inspect_before_write()
        engine.store.read.assert_not_called()


@category('unit')
class ImpactReviewRetryTests(unittest.TestCase):
    def test_sealed_bytes_are_read_only_after_every_requested_review_ended(self):
        engine = engine_module.ResearchEngine.__new__(engine_module.ResearchEngine)
        engine.head = 'a' * 40
        request = {'integration_id': 'IN-1', 'payload_sha256': 'p' * 64}
        engine.runtime = {'status': 'ready', 'executions': {'EX-producer': {'id': 'EX-producer'}},
            'waiting_actions': {'A-1': {'action': {'id': 'A-1'}, 'kind': 'impact_review',
                'execution_id': 'EX-producer', 'review_requests': {'IN-1': request}}}}
        engine._hold_unreadable_impact_submission = Mock()
        engine.store = Mock(git_dir="fixture-git")
        with patch.object(engine_module.submission, 'read_sealed_submission',
                          side_effect=submission.SealedSubmissionError('unreadable fixture')) as read:
            # Control processing retries every waiting item; a pending review reads nothing.
            engine._retry_impact_reviews()
            read.assert_not_called()
            engine.runtime['executions']['EX-review'] = {'id': 'EX-review', 'status': 'ended',
                'outcome': 'output_accepted', 'action': {'stage': 'impact_review',
                                                         'input_basis': {'impact_review': request}}}
            engine._retry_impact_reviews()
            read.assert_called_once()
        engine._hold_unreadable_impact_submission.assert_called_once()


@category('unit')
class SealedArtifactTests(unittest.TestCase):
    def test_a_sealed_row_is_hashed_once_and_matched_rows_are_not_reread(self):
        import uuid
        raw = b'sealed bytes'
        digest = hashlib.sha256(raw).hexdigest()
        path = 'runtime/artifacts/BA-sealed/output.json'
        engine = engine_module.ResearchEngine.__new__(engine_module.ResearchEngine)
        engine.head = 'a' * 40
        engine.store = Mock(git_dir='git-' + uuid.uuid4().hex)
        engine.store.read.return_value = raw
        with self.assertRaisesRegex(ValueError, 'differs from its record'):
            engine._sealed_bytes(path, 'b' * 64, len(raw))
        self.assertEqual(engine._sealed_bytes(path, digest, len(raw)), raw)
        with patch.object(repository.hashlib, 'sha256', side_effect=AssertionError('matched row rehashed')):
            self.assertEqual(engine._sealed_bytes(path, digest, len(raw)), raw)
            engine.store.read.reset_mock()
            self.assertIsNone(engine._sealed_bytes(path, digest, len(raw), needed=False))
        engine.store.read.assert_not_called()

    def test_artifact_condition_reads_and_validates_a_sealed_artifact_once(self):
        import uuid
        from do_math import planning
        raw = b'{"result": true}'
        ref = {'snapshot': 'a' * 40, 'path': 'runtime/artifacts/BA-cond/result.json',
               'sha256': hashlib.sha256(raw).hexdigest()}
        read, validate = Mock(return_value=raw), Mock(return_value=True)
        context = {'snapshot': 'b' * 40, 'read_artifact': read, 'validate_artifact': validate,
                   'git_dir': 'git-' + uuid.uuid4().hex, 'now': '2026-09-26T00:00:00+00:00'}
        condition = {'op': 'artifact_valid', 'artifact_ref': ref}
        for _ in range(3):
            self.assertEqual(planning.evaluate_condition(condition, {}, {}, evaluation_context=context)['state'], 'ready')
        self.assertEqual((read.call_count, validate.call_count), (1, 1))


@category('unit')
class ToolDiscoveryTests(unittest.TestCase):
    def test_lean_is_rediscovered_at_most_once_per_second(self):
        engine = engine_module.ResearchEngine.__new__(engine_module.ResearchEngine)
        engine.instance = {'config': {'scholarly_enabled': False, 'scholarly_server': None},
                           'knowledge': {}, 'sources': []}
        engine.runtime = {'tasks': {}}
        clock = [100.0]
        with patch.object(engine_module, 'discover_lean', return_value=['lean']) as discover, \
                patch.object(engine_module.time, 'monotonic', side_effect=lambda: clock[0]):
            for _ in range(5):
                self.assertIn('tool:lean', engine._available_inputs())
            self.assertEqual(discover.call_count, 1)
            discover.return_value = None
            clock[0] += 1.0
            self.assertNotIn('tool:lean', engine._available_inputs())
            self.assertEqual(discover.call_count, 2)

    def test_periodic_installation_check_rehashes_no_unchanged_file(self):
        from do_math import file_io
        # Freshly edited files are not yet settled; age every fingerprint for this check.
        with patch.object(file_io, 'RACY_NS', 0):
            baseline = engine_module.ResearchEngine._installation_manifest()
            with patch.object(file_io, 'sha256_file', side_effect=AssertionError('unchanged file was rehashed')):
                self.assertEqual(engine_module.ResearchEngine._installation_manifest(), baseline)


@category('unit')
class CandidateCopyTests(unittest.TestCase):
    def repo(self):
        repo = repository.ResearchRepository.__new__(repository.ResearchRepository)
        repo._store = Mock(object_format='sha1')
        repo.contract = default_state_contract()
        return repo

    def test_candidate_numbers_events_without_a_second_whole_state_copy(self):
        instance = {'feature_version': 5, 'title': 'fixture'}
        runtime = {'feature_version': 5, 'events': [{'id': 'EV-1', 'kind': 'created'}]}
        before = deepcopy((instance, runtime))
        with patch.object(events, 'deepcopy', side_effect=AssertionError('candidate is already detached')):
            candidate = self.repo().validate_candidate(instance, runtime)
        self.assertEqual((instance, runtime), before)
        self.assertEqual(candidate['runtime']['events'][0]['event_seq'], 1)
        candidate['runtime']['events'][0]['kind'] = 'changed returned candidate'
        self.assertEqual((instance, runtime), before)

    def test_late_event_failure_never_numbers_the_callers_original(self):
        instance = {'feature_version': 5}
        runtime = {'feature_version': 5, 'events': [
            {'id': 'EV-1', 'kind': 'created'},
            {'id': 'EV-2', 'kind': 'queued', 'event_seq': 99}]}
        before = deepcopy((instance, runtime))
        with self.assertRaisesRegex(ValueError, 'contiguous'):
            self.repo().validate_candidate(instance, runtime)
        self.assertEqual((instance, runtime), before)

    def test_public_event_prepare_still_returns_detached_state_and_protects_failures(self):
        instance = {'nested': {'values': [1]}}
        runtime = {'events': [{'id': 'EV-1', 'kind': 'created'}]}
        copied_instance, copied_runtime = events.EventPublisher.prepare(instance, runtime)
        copied_instance['nested']['values'].append(2)
        copied_runtime['events'][0]['kind'] = 'changed'
        self.assertEqual(instance, {'nested': {'values': [1]}})
        self.assertEqual(runtime, {'events': [{'id': 'EV-1', 'kind': 'created'}]})
        runtime['events'].append({'id': 'EV-2', 'kind': 'queued', 'event_seq': 99})
        before = deepcopy(runtime)
        with self.assertRaisesRegex(ValueError, 'contiguous'):
            events.EventPublisher.prepare(instance, runtime)
        self.assertEqual(runtime, before)


@category('unit')
class StorageValueTests(unittest.TestCase):
    def test_value_validation_and_serialization_keep_the_same_domain(self):
        for value in (None, True, False, 0, -(2**53 - 1), 2**53 - 1,
                      {'e\u0301': ['한글', '😀', 1], 'é': None}):
            with self.subTest(value=value):
                self.assertIsNone(repository.validate_storage_value(value))
                self.assertIsInstance(repository.canonical_json(value), bytes)
        invalid = [0.0, float('nan'), float('inf'), 2**53, -(2**53), '\ud800',
                   {1: 'non-string key'}, {'\udfff': 1}, b'raw', (1,), {'nested': [0.5]}]
        for value in invalid:
            with self.subTest(value=repr(value)):
                with self.assertRaises(ValueError) as checked:
                    repository.validate_storage_value(value)
                with self.assertRaises(ValueError) as encoded:
                    repository.canonical_json(value)
                self.assertEqual(str(checked.exception), str(encoded.exception))
        self.assertNotEqual(repository.canonical_json(True), repository.canonical_json(1))

    def test_record_inspection_validates_without_building_unused_json_bytes(self):
        instance, runtime = storage_state([])
        with patch.object(repository, 'canonical_json', side_effect=AssertionError('unused serialization')):
            self.assertEqual(inspect_state(instance, runtime, requested_areas=['record_storage'])['status'], 'healthy')
            instance['unexpected_value'] = float('nan')
            rejected = inspect_state(instance, runtime, requested_areas=['record_storage'])
        self.assertEqual(rejected['status'], 'blocked')
        self.assertTrue(any('floating-point' in row['message'] for row in rejected['findings']))


@category('unit')
class SubmissionShapeWorkTests(unittest.TestCase):
    def fixture(self, *, explicit=True):
        context = {'action': {'role': 'maintenance'}, 'execution_id': 'EX-1',
                   'snapshot': 'fixed', 'kind_definitions': {}}
        output = {'summary': 'Inspect', 'used_sources': [], 'questions': [],
                  'report': 'Inspected', 'remaining_work': []}
        if explicit:
            output['integration_bundles'] = [{'integration_id': 'IN-1', 'members': ['output'],
                                              'impact_set': [], 'authority_refs': []}]
        return output, contracts.schema_for('maintenance'), context

    def test_unsplit_explicit_and_generated_bundles_check_shapes_once(self):
        for explicit in (True, False):
            output, schema, context = self.fixture(explicit=explicit)
            original = deepcopy(output)
            with self.subTest(explicit=explicit), \
                    patch.object(submission, '_schema_issues', wraps=submission._schema_issues) as checks:
                self.assertEqual(submission.payload_issues(output, schema, context, {}, Path('.')), [])
            self.assertEqual(checks.call_count, 2)  # Response and extensions, once each.
            self.assertIn('integration_bundles', checks.call_args_list[0].args[0])
            self.assertEqual(output, original)

    def test_inner_entry_still_rejects_unchecked_malformed_input(self):
        output, schema, context = self.fixture()
        output.pop('report')
        inner = submission._payload_issues(output, schema, context, {}, Path('.'))
        outer = submission.payload_issues(output, schema, context, {}, Path('.'))
        self.assertTrue(inner)
        self.assertEqual(outer, inner)
        self.assertTrue(all(row['rule_id'].startswith('schema.') for row in inner))

    def test_early_bundle_rejection_keeps_schema_errors_first(self):
        output, schema, context = self.fixture()
        output.pop('report')
        output['integration_bundles'][0]['members'] = ['unknown']
        expected = (submission._schema_issues(output, schema, 'output') +
            submission._schema_issues({}, submission.extension_schema(context['action']), 'activity-extensions.json') +
            submission.integration.inspect_bundles(output, {}, context))
        self.assertEqual(submission.payload_issues(output, schema, context, {}, Path('.')), expected)
        self.assertTrue(expected[0]['rule_id'].startswith('schema.'))

    def test_split_keeps_local_errors_and_checks_valid_siblings(self):
        from test_redesign_CONTRACTS import response, context
        output = response()
        output['knowledge'][0]['statement'] = ''  # Semantic defect in A.
        del output['knowledge'][1]['statement']  # Schema defect in B.
        with patch.object(submission, '_schema_issues', wraps=submission._schema_issues) as checks:
            issues = submission.payload_issues(output, contracts.schema_for('research_work'), context(), {}, Path('.'))
        self.assertEqual({row['integration_id'] for row in issues}, {'IN-A', 'IN-B'})
        self.assertEqual(checks.call_count, 6)  # Original and both distinct slices.

    def test_split_original_validation_is_not_replaced_by_generated_bundle(self):
        from test_redesign_CONTRACTS import response, context
        output = response()
        output.pop('integration_bundles')
        schema = contracts.schema_for('research_work')
        schema['required'].append('integration_bundles')
        supplied = {**context(), 'execution_id': 'EX-fixed'}
        issues = submission.payload_issues(output, schema, supplied, {}, Path('.'))
        self.assertTrue(any(row['rule_id'] == 'schema.required' and
                            row['path'] == 'output/integration_bundles' for row in issues))
        self.assertNotIn('integration_bundles', output)


@category('unit')
class SnapshotMetadataTests(unittest.TestCase):
    def store(self, *, length=40, root_type='commit', rows=None, returncode=0):
        store = GitStateStore.__new__(GitStateStore)
        store.ref = 'refs/heads/do-math/RI-fixture'
        store.object_format = 'sha1' if length == 40 else 'sha256'
        head, research, runtime = ('a' * length, 'b' * length, 'c' * length)
        values = rows if rows is not None else [head + ' ' + root_type, research + ' tree', runtime + ' tree']
        store._git = Mock(side_effect=[
            SimpleNamespace(returncode=0, stdout=(head + '\n').encode(), stderr=b''),
            SimpleNamespace(returncode=returncode, stdout=('\n'.join(values) + '\n').encode(), stderr=b'')])
        return store, head, research, runtime

    def test_two_calls_bind_all_metadata_to_the_resolved_oid(self):
        for length in (40, 64):
            with self.subTest(length=length):
                store, head, research, runtime = self.store(length=length)
                self.assertEqual(store.read_snapshot(), StateSnapshot(head, research, runtime))
                self.assertEqual(store._git.call_count, 2)
                request = store._git.call_args
                self.assertEqual(request.args, ('cat-file', '--batch-check=%(objectname) %(objecttype)'))
                self.assertEqual(request.kwargs['input'], f'{head}\n{head}:research\n{head}:runtime\n'.encode())
                self.assertNotIn(store.ref.encode(), request.kwargs['input'])

    def test_absent_ref_does_not_request_objects_but_corrupt_ref_is_rejected(self):
        store, *_ = self.store()
        store._git.side_effect = [SimpleNamespace(returncode=1, stdout=b'', stderr=b'')]
        self.assertEqual(store.read_snapshot(), StateSnapshot(None, None, None))
        self.assertEqual(store._git.call_count, 1)
        store._git.side_effect = [SimpleNamespace(returncode=1, stdout=b'', stderr=b'bad ref')]
        with self.assertRaisesRegex(GitStateStoreError, 'cannot resolve'):
            store.read_snapshot()

    def test_wrong_or_incomplete_metadata_never_returns_a_snapshot(self):
        head, tree = 'a' * 40, 'b' * 40
        cases = [([head + ' blob', head + ':research missing', head + ':runtime missing'], 'commit'),
                 ([head + ' missing'], 'unreadable'),
                 ([tree + ' commit', tree + ' tree', tree + ' tree'], 'invalid state commit'),
                 ([head + ' commit', head + ':research missing', tree + ' tree'], 'research'),
                 ([head + ' commit', tree + ' blob', tree + ' tree'], 'tree'),
                 ([head + ' commit', tree + ' tree'], 'incomplete'),
                 ([head + ' commit', tree + ' tree', tree + ' tree', tree + ' tree'], 'incomplete')]
        for rows, message in cases:
            with self.subTest(rows=rows):
                store, *_ = self.store(rows=rows)
                with self.assertRaisesRegex(GitStateStoreError, message):
                    store.read_snapshot()
        store, *_ = self.store(returncode=1)
        with self.assertRaises(GitStateStoreError):
            store.read_snapshot()


if __name__ == '__main__':
    unittest.main()
