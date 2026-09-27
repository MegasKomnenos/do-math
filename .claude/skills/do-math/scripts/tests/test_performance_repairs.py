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
from unittest.mock import Mock, create_autospec, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math import contracts, engine as engine_module, repository, submission
from do_math.context_store import prefetch_artifacts
from do_math.git_store import GitStateStore, GitStateStoreError, StateSnapshot
from do_math.state_checks import inspect_state
from do_math.state_contract import default_state_contract
from research_fixtures import bare_engine, current_state


def artifact(path, raw, **changes):
    return {"artifact_ref": path, "sha256": hashlib.sha256(raw).hexdigest(),
            "bytes": len(raw), **changes}


def storage_state(refs):
    return ({"feature_version": 5, "sources": []},
            {"feature_version": 5, "executions": {"EX-1": {"id": "EX-1", "output_files": refs}}})


def archived_role_input(bundle, snapshot, files):
    """The manifest of a maintenance role input archived once below ``runtime/artifacts/<bundle>``.

    Each row names its archived bytes (prompt at ``input.txt``); ``files``
    receives those bytes.
    """
    prefix = 'runtime/artifacts/' + bundle + '/'

    # A document row carries its own ``path`` field, so the archive location has another name.
    def row(archived, raw, **fields):
        files[prefix + archived] = raw
        return {**fields, **artifact(prefix + archived, raw)}
    return {'feature_version': 5, 'role': 'maintenance', 'snapshot': snapshot,
            'output_contract': {'id': 'do-math-cli/5'}, 'prompt': row('input.txt', b'exact prompt'),
            'direct': [row('input/catalog/' + key + '.json', b'{}\n', key=key)
                       for key in ('snapshot', 'governance', 'execution_profile', 'action')],
            'documents': [row('input/implementation/' + path, path.encode() + b'\n', path=path)
                          for path in ('SKILL.md', 'GLOSSARY.md')],
            'references': []}


def candidate_repository():
    """A repository over the installed contract; candidate validation never reaches its Git store."""
    repo = repository.ResearchRepository.__new__(repository.ResearchRepository)
    repo._store = Mock(object_format='sha1')
    repo.contract = default_state_contract()
    return repo


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
        # The batch omits a requested path absent from the snapshot.
        with self.assertRaisesRegex(ValueError, 'artifact is missing: one'):
            read('one')
        self.assertEqual(read('another'), b'single')

    def test_engine_entry_checks_presence_and_length_while_check_compares_bytes(self):
        head = 'a' * 40
        output_path = 'runtime/artifacts/BA-output/result.bin'
        input_path = 'runtime/artifacts/BA-input/input.txt'
        files = {output_path: b'\x00\xff'}
        instance, runtime = storage_state([artifact(output_path, files[output_path])])
        runtime['executions']['EX-1'].update(input_bundle='BA-input',
            input_manifest=archived_role_input('BA-input', head, files))
        engine = bare_engine(instance, runtime, head=head, store=create_autospec(repository.ResearchRepository, instance=True))
        engine.store.load.return_value = (head, instance, runtime)
        engine.store.read.side_effect = AssertionError('normal inspection must use batch reads')

        # Both batch readers leave paths absent from the snapshot out of their result.
        def batch(paths, snapshot, *, missing='raise'):
            self.assertEqual((snapshot, missing), (head, 'omit'))
            engine.head = 'b' * 40  # Later callbacks must retain the observed snapshot.
            return {path: files[path] for path in paths if path in files}

        def sizes(paths, snapshot, *, missing='raise'):
            self.assertEqual((snapshot, missing), (head, 'omit'))
            return {path: len(files[path]) for path in paths if path in files}

        engine.store.read_many.side_effect = batch
        engine.store.blob_sizes.side_effect = sizes
        engine._inspect_before_write()
        # Entry to run/controls reads no artifact bytes: same-length changes are check's.
        self.assertEqual(engine.store.read_many.call_count, 0)
        self.assertTrue(engine.check(requested_areas=['start_import_input'])['passed'])
        engine.head = head
        files[input_path] = b'exact prompX'
        engine._inspect_before_write()
        # The start_import_input area compares each archived role input, prompt included.
        result = engine.check(requested_areas=['start_import_input'])
        self.assertFalse(result['passed'])
        self.assertIn('EX-1: input artifact bytes differ: prompt',
                      [row['message'] for row in result['inspection']['findings']])
        del files[input_path]
        engine.head = head
        with self.assertRaisesRegex(ValueError, 'current input artifact is missing: EX-1'):
            engine._inspect_before_write()
        files[output_path] = b'\x00'
        with self.assertRaisesRegex(ValueError, 'repaired before publication'):
            engine._inspect_before_write()
        engine.store.read.assert_not_called()


class ImpactReviewRetryTests(unittest.TestCase):
    def test_sealed_bytes_are_read_only_after_every_requested_review_ended(self):
        engine = bare_engine(head='a' * 40)
        request = {'integration_id': 'IN-1', 'payload_sha256': 'p' * 64}
        engine.runtime = {'status': 'ready', 'executions': {'EX-producer': {'id': 'EX-producer'}},
            'waiting_actions': {'A-1': {'action': {'id': 'A-1'}, 'kind': 'impact_review',
                'execution_id': 'EX-producer', 'review_requests': {'IN-1': request}}}}
        engine._hold_unreadable_impact_submission = create_autospec(engine._hold_unreadable_impact_submission)
        engine.store = create_autospec(repository.ResearchRepository, instance=True)
        engine.store.git_dir = "fixture-git"
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


class SealedArtifactTests(unittest.TestCase):
    def test_a_sealed_row_is_hashed_once_and_matched_rows_are_not_reread(self):
        import uuid
        raw = b'sealed bytes'
        digest = hashlib.sha256(raw).hexdigest()
        path = 'runtime/artifacts/BA-sealed/output.json'
        engine = bare_engine(head='a' * 40, store=create_autospec(repository.ResearchRepository, instance=True))
        engine.store.git_dir = 'git-' + uuid.uuid4().hex
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


class ToolDiscoveryTests(unittest.TestCase):
    def test_lean_is_rediscovered_at_most_once_per_second(self):
        engine = bare_engine()
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
            # Forget the hashed edition so the full walk runs, not the listing shortcut.
            with patch.object(engine_module, '_HASHED_INSTALLATION', None), \
                    patch.object(file_io, 'sha256_file', side_effect=AssertionError('unchanged file was rehashed')):
                self.assertEqual(engine_module.ResearchEngine._installation_manifest(), baseline)

    def test_control_reuses_one_reader_per_repository_and_instance(self):
        with patch.object(engine_module, '_CONTROL_READERS', type(engine_module._CONTROL_READERS)()), \
                patch.object(engine_module, '_repository', side_effect=lambda *args: object()) as create:
            first = engine_module._control_reader(Path('repo'), 'RI-1')
            self.assertIs(engine_module._control_reader(Path('repo').absolute(), 'RI-1'), first)
            self.assertIsNot(engine_module._control_reader(Path('repo'), 'RI-2'), first)
            self.assertEqual(create.call_count, 2)
            for index in range(engine_module._CONTROL_READER_LIMIT):
                engine_module._control_reader(Path('other'), f'RI-{index + 3}')
            self.assertIsNot(engine_module._control_reader(Path('repo'), 'RI-1'), first)

    def test_unchanged_installation_listing_reuses_the_hashed_edition(self):
        from do_math import file_io
        with patch.object(file_io, 'RACY_NS', 0), patch.object(engine_module, '_HASHED_INSTALLATION', None):
            baseline = engine_module.ResearchEngine._installation_manifest()
            with patch.object(engine_module, 'reading_map', side_effect=AssertionError('role map reread')):
                self.assertIs(engine_module.ResearchEngine._installation_manifest(), baseline)
            listing = engine_module._HASHED_INSTALLATION[1]
            changed = {**listing, 'scripts/do_math/added.py': (1, 1, 1)}
            with patch.object(engine_module, '_installation_listing', side_effect=[changed, listing]), \
                    patch.object(engine_module, 'reading_map', wraps=engine_module.reading_map) as rebuilt:
                self.assertEqual(engine_module.ResearchEngine._installation_manifest(), baseline)
            self.assertEqual(rebuilt.call_count, 1)

    def test_installation_listing_reports_added_removed_and_rewritten_files(self):
        import os, tempfile
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            package = root / 'scripts' / 'do_math'
            (package / 'sub').mkdir(parents=True)
            (root / 'docs').mkdir()
            for path in (package / 'a.py', package / 'sub' / 'b.py', root / 'docs' / 'x.md', root / 'SKILL.md'):
                path.write_text('v1', encoding='utf-8')
            documents = ('SKILL.md', 'docs/x.md')
            listing = lambda: engine_module._installation_listing(root, documents)
            before = listing()
            self.assertEqual(set(before), {'scripts/do_math/a.py', 'scripts/do_math/sub/b.py', 'SKILL.md', 'docs/x.md'})
            # Files the manifest never hashes do not move the listing.
            (package / '__pycache__').mkdir()
            (package / '__pycache__' / 'a.cpython-312.pyc').write_bytes(b'cache')
            (root / 'docs' / 'unlisted.md').write_text('other', encoding='utf-8')
            self.assertEqual(listing(), before)
            (package / 'new').mkdir()
            (package / 'new' / 'c.py').write_text('v1', encoding='utf-8')
            self.assertEqual(set(listing()) - set(before), {'scripts/do_math/new/c.py'})
            (package / 'new' / 'c.py').unlink()
            (package / 'sub' / 'b.py').unlink()
            self.assertEqual(set(before) - set(listing()), {'scripts/do_math/sub/b.py'})
            for relative in ('docs/x.md', 'scripts/do_math/a.py'):
                path = root / relative
                old = listing()[relative]
                path.write_text('v2', encoding='utf-8')  # same size: only the time moves
                os.utime(path, ns=(old[1] + 10**9, old[1] + 10**9))
                self.assertNotEqual(listing()[relative], old, relative)


class CandidateCopyTests(unittest.TestCase):
    def test_candidate_numbers_events_without_a_second_whole_state_copy(self):
        instance, runtime = current_state({'title': 'fixture'}, {'events': [{'id': 'EV-1', 'kind': 'created'}]})
        before = deepcopy((instance, runtime))
        with patch.object(repository, 'deepcopy', wraps=deepcopy) as copies:
            candidate = candidate_repository().validate_candidate(instance, runtime)
        # One copy of each root; event numbering works on that detached copy.
        self.assertEqual([call.args[0] for call in copies.call_args_list], [instance, runtime])
        self.assertEqual((instance, runtime), before)
        self.assertEqual(candidate['runtime']['events'][0]['event_seq'], 1)
        candidate['runtime']['events'][0]['kind'] = 'changed returned candidate'
        self.assertEqual((instance, runtime), before)

    def test_late_event_failure_never_numbers_the_callers_original(self):
        instance, runtime = current_state(runtime={'events': [
            {'id': 'EV-1', 'kind': 'created'},
            {'id': 'EV-2', 'kind': 'queued', 'event_seq': 99}]})
        before = deepcopy((instance, runtime))
        with self.assertRaisesRegex(ValueError, 'contiguous'):
            candidate_repository().validate_candidate(instance, runtime)
        self.assertEqual((instance, runtime), before)


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

    def test_inspection_builds_no_json_bytes_and_publication_checks_the_value_domain(self):
        instance, runtime = storage_state([])
        with patch.object(repository, 'canonical_json', side_effect=AssertionError('unused serialization')):
            self.assertEqual(inspect_state(instance, runtime, requested_areas=['record_storage'])['status'], 'healthy')
        # The storage value domain belongs to loading and publication: each
        # record serialized for a candidate passes the storage value check.
        instance, runtime = current_state(runtime={'installation': {'measured': float('nan')}})
        with self.assertRaisesRegex(ValueError, 'floating-point'):
            candidate_repository().validate_candidate(instance, runtime)


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


class SnapshotMetadataTests(unittest.TestCase):
    REF = 'refs/heads/do-math/RI-fixture'

    def store(self, *, length=40, root_type='commit', rows=None, returncode=0, resolved=None):
        store = GitStateStore.__new__(GitStateStore)
        store.ref = self.REF
        store._held_head = None
        store.object_format = 'sha1' if length == 40 else 'sha256'
        head, research, runtime = ('a' * length, 'b' * length, 'c' * length)
        values = rows if rows is not None else [head + ' ' + root_type, research + ' tree', runtime + ' tree']
        if resolved is None:
            resolved = SimpleNamespace(returncode=0, stdout=(head + '\n').encode(), stderr=b'')
        # One batch query; rev-parse (``resolved``) runs only when the ref line is missing.
        store._git = Mock(side_effect=[
            SimpleNamespace(returncode=returncode, stdout=('\n'.join(values) + '\n').encode(), stderr=b''),
            resolved])
        return store, head

    def test_one_batch_reads_the_ref_and_both_subtrees(self):
        for length in (40, 64):
            with self.subTest(length=length):
                store, head = self.store(length=length)
                self.assertEqual(store.read_snapshot(), StateSnapshot(head))
                self.assertEqual(store._git.call_count, 1)
                request = store._git.call_args
                self.assertEqual(request.args, ('cat-file', '--batch-check=%(objectname) %(objecttype)'))
                self.assertEqual(request.kwargs['input'],
                                 f'{self.REF}\n{self.REF}:research\n{self.REF}:runtime\n'.encode())

    def test_absent_ref_is_none_but_corrupt_ref_is_rejected(self):
        missing = [self.REF + suffix + ' missing' for suffix in ('', ':research', ':runtime')]
        store, _ = self.store(rows=missing, resolved=SimpleNamespace(returncode=1, stdout=b'', stderr=b''))
        self.assertEqual(store.read_snapshot(), StateSnapshot(None))
        self.assertEqual([call.args[0] for call in store._git.call_args_list], ['cat-file', 'rev-parse'])
        store, _ = self.store(rows=missing, resolved=SimpleNamespace(returncode=1, stdout=b'', stderr=b'bad ref'))
        with self.assertRaisesRegex(GitStateStoreError, 'cannot resolve'):
            store.read_snapshot()

    def test_wrong_or_incomplete_metadata_never_returns_a_snapshot(self):
        head, tree, ref = 'a' * 40, 'b' * 40, self.REF
        cases = [([head + ' blob', ref + ':research missing', ref + ':runtime missing'], 'commit'),
                 ([ref + ' missing'], 'unreadable'),
                 ([head + ' commit extra', tree + ' tree', tree + ' tree'], 'invalid state commit'),
                 ([head + ' commit', ref + ':research missing', tree + ' tree'], 'research'),
                 ([head + ' commit', tree + ' blob', tree + ' tree'], 'tree'),
                 ([head + ' commit', tree + ' tree'], 'incomplete'),
                 ([head + ' commit', tree + ' tree', tree + ' tree', tree + ' tree'], 'incomplete')]
        for rows, message in cases:
            with self.subTest(rows=rows):
                store, _ = self.store(rows=rows)
                with self.assertRaisesRegex(GitStateStoreError, message):
                    store.read_snapshot()
        store, _ = self.store(returncode=1)
        with self.assertRaises(GitStateStoreError):
            store.read_snapshot()


if __name__ == '__main__':
    unittest.main()
