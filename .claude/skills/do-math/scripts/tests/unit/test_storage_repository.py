"""Snapshot-facing repository operations (``repository``, layer 2) over the Git port's in-process fake.

Every repository is the real ``ResearchRepository`` on ``InProcessGit`` (설계
4.3); repository objects that must see each other's commits share one fake.
The legacy tests counted or forbade calls by patching the store, ``hashlib``,
``deepcopy`` and product functions with ``wraps`` or failing doubles. Here the
same calls are observed on the unchanged product: Python functions through
their code (``ObservedCalls``), the builtin ``hashlib.sha256`` through call
events (``storage_probes.BuiltinCalls``). "Another writer" commits are made
with the store's own ``publish``, past the repository's checks, as before.
"""
from copy import deepcopy
import base64
import hashlib
import json
from pathlib import Path
import re
import tempfile
import unittest
import uuid

from do_math import initialization, repository
from do_math.canonical import canonical_json
from do_math.payloads import json_safe
from do_math.git_store import GitStateStore, GitStateStoreConflict, GitStateStoreError
from do_math.repository import RepositoryCursorError
from do_math.state_checks import inspect_state
from do_math.state_contract import StateContract
from support.state_builders import current_state, installed_contract, with_validator
from support.fakes.clock import FakeClock
from support.fakes.git_backend import InProcessGit
from support.provider_probes import ObservedCalls
from support.storage_files import junction, remove_link
from support.storage_probes import BuiltinCalls
from support.storage_records import INSTANCE_ID, engine_on, fake_ports, record_store
from support.provider_native_inputs import EXTERNAL_JSON_VALUES

FLOAT_REFUSED = 'JSON floating-point numbers are not permitted'
STALE = 'expected head no longer matches the instance ref'
OUTSIDE_NAMESPACE = 'artifacts require full runtime/artifacts/<bundle>/<path> and bytes'


def exact(message):
    return '^' + re.escape(message) + '$'


def candidate_repository(test):
    """A repository over the installed contract in a new empty repository; candidate validation never reaches it."""
    return record_store(Path(test.enterContext(tempfile.TemporaryDirectory())))


class RepositoryCase(unittest.TestCase):
    """A repository at ``root/repository`` initialized with ``current_state({"title": "instance"})``."""

    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.repository_path = self.root / 'repository'
        self.backend, self.clock = InProcessGit(), FakeClock()
        self.repository = self.store()
        self.initial_head = self.repository.initialize(*current_state({'title': 'instance'}))

    def store(self, **options):
        """Another repository object on the same repository and Git objects."""
        return record_store(self.repository_path, backend=self.backend, clock=self.clock, **options)


class ResearchRepositoryTests(RepositoryCase):
    def test_checkpoint_evidence_cannot_escape_the_immutable_namespace(self):
        head, instance, runtime = self.repository.load()
        runtime['checkpoints'] = {'EX-evidence': {'evidence_files': [{'path': 'notes.txt',
            'artifact_ref': 'runtime/history/state.json', 'sha256': hashlib.sha256(b'notes').hexdigest(), 'bytes': 5}]}}
        before = deepcopy((instance, runtime))
        with self.assertRaisesRegex(ValueError, '^artifact evidence must use the immutable artifact namespace$'):
            self.repository.save_with_state(head, instance, runtime)
        self.assertEqual((instance, runtime), before)
        self.assertEqual(self.repository.load()[0], head)

    def test_artifact_cache_bounds_forget_facts_without_changing_their_bytes(self):
        """Exercise the real 1024-link and 64 MiB cache limits without publishing unrelated records."""
        git_dir = str(self.repository.git_dir)
        path = 'runtime/artifacts/AB-cache/large.bin'
        first = 'cache-head-0'
        repository._learn_artifact(git_dir, path, first, 5, b'first')
        self.assertEqual(repository._known_artifact(git_dir, path, first), [first, 5, b'first'])
        for index in range(1, repository._LINEAGE_LIMIT + 1):
            repository._learn_publication(git_dir, 'cache-head-' + str(index - 1), 'cache-head-' + str(index), {})
        # A bounded ancestry miss asks the store again; it never asserts absence.
        self.assertIsNone(repository._known_artifact(git_dir, path, 'cache-head-' + str(repository._LINEAGE_LIMIT)))
        self.assertEqual(repository._known_artifact(git_dir, path, first)[2], b'first')
        raw = b'x' * (repository._ARTIFACT_BYTES_LIMIT + 1)
        repository._learn_artifact(git_dir, path, first, len(raw), raw)
        self.assertEqual(repository._known_artifact(git_dir, path, first), [first, len(raw), None])
        self.assertEqual(raw[:3], b'xxx')
        self.assertLessEqual(repository._held_bytes, repository._ARTIFACT_BYTES_LIMIT)

    def test_export_reads_bounded_batches_and_preserves_binary_contents(self):
        """About 1 s, over the 0.2 s unit budget: 150 artifacts are published and exported file by file, the batching under test."""
        head, instance, runtime = self.repository.load()
        files = {f'runtime/artifacts/BA-export/{i}.bin': bytes([i % 256]) * 1024 for i in range(150)}
        head = self.repository.save_with_state(head, instance, runtime, artifacts=files)[0]
        with ObservedCalls(single=GitStateStore.read_bytes, batch=GitStateStore.read_many,
                           capture={'batch': lambda arguments: list(arguments['paths'])}) as calls:
            result = self.repository.export(self.root / 'batched', head, prefixes=('runtime/artifacts/',))
        self.assertEqual(calls.count('single'), 0)
        batches = calls.captured('batch')
        self.assertEqual(len(batches), 3)
        self.assertTrue(all(len(paths) <= 64 for paths in batches), [len(paths) for paths in batches])
        self.assertEqual(set(result['files']), set(files))
        for name, raw in files.items():
            self.assertEqual((self.root / 'batched' / name).read_bytes(), raw)

    def test_published_artifacts_are_not_read_again_at_later_heads_only(self):
        path, raw = 'runtime/artifacts/BA-known/input.txt', b'archived input\n'
        head, instance, runtime = self.repository.load()
        before = head
        written = self.repository.save_with_state(head, instance, runtime, artifacts={path: raw})[0]
        instance['title'] = 'later'
        later = self.repository.save_with_state(written, instance, runtime)[0]
        with ObservedCalls(single=GitStateStore.read_bytes, sizes=GitStateStore.blob_sizes,
                           capture={'sizes': lambda arguments: list(arguments['paths'])}) as calls:
            for snapshot in (written, later):
                self.assertEqual(self.repository.read(path, snapshot), raw)
                self.assertEqual(self.repository.blob_sizes([path], snapshot), {path: len(raw)})
        self.assertEqual(calls.count('single'), 0)
        self.assertEqual(calls.captured('sizes'), [[], []])
        # A head that precedes the artifact still asks Git, which reports it absent.
        self.assertEqual(self.repository.blob_sizes([path], before, missing='omit'), {})
        with self.assertRaisesRegex(GitStateStoreError, exact(f'git cat-file blob {before}:{path} failed: no blob at this path')):
            self.repository.read(path, before)

    def test_live_input_snapshots_stay_validated_beyond_the_read_bound(self):
        head, instance, runtime = self.repository.load()
        pinned = head
        repository.retain_reads(self.repository.git_dir, {pinned})
        try:
            for index in range(repository._VALIDATED_READ_LIMIT + 2):
                instance['title'] = f'title {index}'
                head = self.repository.save_with_state(head, instance, runtime)[0]
            self.assertIsNotNone(self.repository.published_state(pinned))
            repository.retain_reads(self.repository.git_dir, set())
            instance['title'] = 'released'
            self.repository.save_with_state(head, instance, runtime)
            self.assertIsNone(self.repository.published_state(pinned))
        finally:
            repository.retain_reads(self.repository.git_dir, set())

    def test_initialize_load_save_and_exact_old_snapshot_read(self):
        head, instance, runtime = self.repository.load()
        self.assertEqual(head, self.initial_head)
        self.assertEqual(instance['title'], 'instance')
        self.assertEqual(instance['object_format'], 'sha1')
        self.assertEqual(runtime['status'], 'initializing')
        later = self.repository.save_with_state(head, instance, {**runtime, 'status': 'running'})[0]
        self.assertEqual(self.repository.load(self.initial_head)[2]['status'], 'initializing')
        self.assertEqual(json.loads(self.repository.read('runtime/_state/metadata.json', later))['record']['status'],
                         'running')

    def test_stale_save_conflict_does_not_overwrite(self):
        second = self.store()
        winner = self.repository.save_with_state(self.initial_head,
                                                 *current_state({'title': 'instance'}, {'status': 'running'}))[0]
        with self.assertRaisesRegex(GitStateStoreConflict, exact(STALE)):
            second.save_with_state(self.initial_head, *current_state({'title': 'instance'}, {'status': 'paused'}))
        self.assertEqual(self.repository.load()[0], winner)
        self.assertEqual(self.repository.load(winner)[2]['status'], 'running')

    def test_new_artifact_bundle_is_saved_with_state_and_existing_bundle_is_immutable(self):
        first = self.repository.save_with_state(
            self.initial_head, *current_state({'title': 'instance'}, {'status': 'running'}),
            artifacts={'runtime/artifacts/AB-01/output.txt': b'sealed'})[0]
        with self.assertRaisesRegex(ValueError, exact('existing runtime artifact bundles are immutable')):
            self.repository.save_with_state(
                first, *current_state({'title': 'instance'}, {'status': 'running'}),
                artifacts={'runtime/artifacts/AB-01/other.txt': b'forbidden'})
        later = self.repository.save_with_state(
            first, *current_state({'title': 'instance'}, {'status': 'completed'}),
            artifacts={'runtime/artifacts/AB-02/output.txt': b'new bundle'})[0]
        self.assertEqual(self.repository.read('runtime/artifacts/AB-01/output.txt', later), b'sealed')

    def test_query_cursor_is_bound_to_snapshot_and_query_and_has_no_empty_page(self):
        head = self.repository._store.publish(self.initial_head, {
            'research/a.txt': b'needle alpha', 'research/b.txt': b'needle beta', 'research/c.txt': b'not here'}).head
        first = self.repository.query(snapshot=head, prefix='research/', text='needle', limit=1)
        self.assertEqual(first['total'], 2)
        self.assertEqual(len(first['items']), 1)
        self.assertTrue(first['truncated'])
        self.assertIsNotNone(first['next_cursor'])
        second = self.repository.query(snapshot=head, prefix='research/', text='needle', limit=1,
                                       cursor=first['next_cursor'])
        self.assertEqual(len(second['items']), 1)
        self.assertNotEqual(first['items'][0]['path'], second['items'][0]['path'])
        self.assertFalse(second['truncated'])
        with self.assertRaisesRegex(RepositoryCursorError, exact('cursor is bound to another snapshot or query')):
            self.repository.query(snapshot=head, prefix='research/', text='other', limit=1, cursor=first['next_cursor'])
        with self.assertRaisesRegex(RepositoryCursorError, exact('cursor is malformed')):
            self.repository.query(snapshot=head, prefix='research/', text='needle', limit=1,
                                  cursor=first['next_cursor'] + 'x')
        forged = base64.urlsafe_b64encode(canonical_json({
            'snapshot': head, 'prefix': 'research/', 'text': 'needle', 'last_path': 'research/aa.txt',
        })).decode('ascii').rstrip('=')
        with self.assertRaisesRegex(RepositoryCursorError, exact('cursor path is not present in this query result')):
            self.repository.query(snapshot=head, prefix='research/', text='needle', limit=1, cursor=forged)
        empty = self.repository.query(snapshot=head, prefix='research/', text='absent', limit=1)
        self.assertEqual(empty, {'snapshot': head, 'total': 0, 'items': [], 'next_cursor': None, 'truncated': False})

    def test_list_files_prefix_and_read_reject_implicit_missing_snapshot(self):
        self.assertIn('research/_state/metadata.json', self.repository.list_files('research/'))
        self.assertNotIn('research/instance.json', self.repository.list_files('research/'))
        self.assertIn('runtime/_state/metadata.json', self.repository.list_files('runtime/'))
        with self.assertRaisesRegex(ValueError, exact('prefix must remain below research/ or runtime/')):
            self.repository.list_files('../')

    def test_duplicate_json_keys_are_rejected_on_load(self):
        bad_head = self.repository._store.publish(self.initial_head, {
            'research/_state/metadata.json': b'{"name":"first","name":"second"}\n'}).head
        with self.assertRaisesRegex(ValueError, exact('stored document is not strict JSON')) as refused:
            self.repository.load(bad_head)
        self.assertEqual(str(refused.exception.__cause__), 'duplicate JSON key: name')

    def test_export_refuses_nonempty_or_reparse_destination_and_preserves_prefix(self):
        destination = self.root / 'export'
        result = self.repository.export(destination, prefixes=('research/',))
        self.assertEqual(result['snapshot'], self.initial_head)
        self.assertEqual(result['files'], self.repository.list_files('research/'))
        self.assertEqual((destination / 'research' / '_state' / 'metadata.json').read_bytes(),
                         self.repository.read('research/_state/metadata.json'))
        with self.assertRaisesRegex(ValueError, exact('export destination must be absent or an empty directory')):
            self.repository.export(destination, prefixes=('research/',))
        target = self.root / 'target'
        target.mkdir()
        link = junction(target, self.root / 'reparse-export')
        self.addCleanup(remove_link, link)
        with self.assertRaisesRegex(ValueError, exact('physical path crosses a reparse point or symlink: ' + str(link))):
            self.repository.export(link, prefixes=('research/',))
        self.assertEqual(list(target.iterdir()), [])

    def test_canonical_json_is_stable(self):
        self.assertEqual(canonical_json({'b': 1, 'a': [True, None]}), b'{\n  "a": [\n    true,\n    null\n  ],\n  "b": 1\n}\n')


class ValidatedReadReuseTests(unittest.TestCase):
    """Same-fact rechecks stay out of reads: own heads, shared heads, matched bytes."""

    def setUp(self):
        from support.entry import entry
        _entry = entry()
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.backend, self.clock = InProcessGit(), FakeClock()
        self.repository = self.store()
        # The large original input is stored as a sealed payload blob.
        instance, runtime = initialization.initialize_state(
            instance_id=INSTANCE_ID, goal='G', workspace=self.root / 'work', config={}, source_input='x' * 70000,
            clock=self.clock, host=_entry.ports.host)
        self.head = self.repository.initialize(instance, runtime)

    def store(self, **options):
        return record_store(self.root, backend=self.backend, clock=self.clock, **options)

    @staticmethod
    def counters():
        """Every snapshot decode and every contract validation while it is open."""
        return ObservedCalls(decode=repository._decode_families, validate=StateContract.validate)

    def outside_head(self, parent, bundle):
        """A head another writer published: same state plus one artifact bundle."""
        return self.repository._store.publish(parent, {f'runtime/artifacts/{bundle}/note.bin': bundle.encode()}).head

    def test_own_publication_is_not_revalidated_but_an_outside_head_is(self):
        head, instance, runtime = self.repository.load()
        runtime['cycles'] = 1
        with self.counters() as calls:
            new_head, saved_instance, saved_runtime = self.repository.save_with_state(head, instance, runtime)
            _, loaded_instance, loaded_runtime = self.repository.load(new_head)
            self.assertEqual(self.repository.view(new_head)[2]['cycles'], 1)
        self.assertEqual((calls.count('decode'), calls.count('validate')), (0, 1))  # the candidate check only
        self.assertEqual(loaded_runtime['cycles'], 1)
        saved_runtime['cycles'] = 99  # returned views are detached from the shared entry
        self.assertEqual(self.repository.load(new_head)[2]['cycles'], 1)
        rows = [row for row in self.repository.load_records(new_head)[3] if row['family'] == 'lifecycle']
        self.assertEqual(len(rows), 1)
        outside = self.outside_head(new_head, 'BA-outside')
        with self.counters() as calls:
            self.assertEqual(self.repository.load(outside)[2]['cycles'], 1)
        self.assertEqual((calls.count('decode'), calls.count('validate')), (1, 1))

    def test_one_head_is_validated_once_across_repository_objects(self):
        outside = self.outside_head(self.head, 'BA-shared')
        with self.counters() as calls:
            self.store().load(outside)
            self.store().load(outside)
            self.assertEqual(calls.count('decode'), 1)
            self.store(contract=installed_contract()).load(outside)
            self.assertEqual(calls.count('decode'), 2)  # another contract is another validation

    def test_payload_bytes_are_hashed_once_per_repository(self):
        payloads = {path: raw for path, raw in self.repository._read_documents(self.head)[3].items()
                    if path.startswith('runtime/artifacts/payload-')}
        self.assertEqual(len(payloads), 1)
        raw = next(iter(payloads.values()))
        outside = self.outside_head(self.head, 'BA-payload')
        with BuiltinCalls(hashlib.sha256) as sha256:
            hashlib.sha256(b'probe')  # the probe sees a hash of these bytes
            self.assertEqual(len(self.repository.load(outside)[1]['lifecycle']['immutable_input']['text']), 70000)
        self.assertEqual(sha256.arguments[0], b'probe')
        self.assertFalse(any(argument == raw for argument in sha256.arguments))

    def test_evidence_rows_are_read_once_and_new_rows_are_still_matched(self):
        path, raw = 'runtime/artifacts/BA-evidence/observation.json', b'{"observed": true}\n'
        head, instance, runtime = self.repository.load()
        head = self.repository.save_with_state(head, instance, runtime, artifacts={path: raw})[0]

        def rows(digest):
            return {'checkpoints': {'CP-1': {'evidence_files': [{'artifact_ref': path, 'sha256': digest, 'bytes': len(raw)}]}}}
        digest = hashlib.sha256(raw).hexdigest()
        outside = self.outside_head(head, 'BA-evidence-2')
        with ObservedCalls(reads=GitStateStore.read_many) as calls:
            self.repository._validate_artifact_evidence(rows(digest), head)
            self.repository._validate_artifact_evidence(rows(digest), outside)
        self.assertEqual(calls.count('reads'), 1)
        with self.assertRaisesRegex(ValueError, exact('artifact evidence missing or hash differs: ' + path)):
            self.repository._validate_artifact_evidence(rows('0' * 64), head)

    def test_unchanged_records_skip_record_local_and_immutable_hash_checks(self):
        from do_math import governance
        checked = []
        contract = installed_contract()
        installed = contract.family('research', 'governance_sources').validator

        def counted(record):
            checked.append(record['id'])
            installed(record)
        with_validator(contract, 'research', 'governance_sources', counted)
        store = self.store(contract=contract)
        head, instance, runtime = store.load()
        instance['governance_sources']['GS-1'] = governance.preserve_source('GS-1', 'first', origin='user')
        head, instance, runtime = store.save_with_state(head, instance, runtime)
        self.assertEqual(checked, ['GS-1'])
        instance['governance_sources']['GS-2'] = governance.preserve_source('GS-2', 'second', origin='user')
        runtime['cycles'] = 1
        with ObservedCalls(original=initialization.original_input_bytes) as calls:
            head, instance, runtime = store.save_with_state(head, instance, runtime)
        self.assertEqual(checked, ['GS-1', 'GS-2'])
        self.assertEqual(calls.count('original'), 0)
        instance['governance_sources']['GS-3'] = {**governance.preserve_source('GS-3', 'third', origin='user'),
                                                  'sha256': '0' * 64}
        with self.assertRaisesRegex(ValueError, exact('immutable source bytes or revision changed')):
            store.save_with_state(head, instance, runtime)


class SaveWithStateTests(RepositoryCase):
    def test_unchanged_state_is_noop_and_returns_normalized_reload_views(self):
        head, instance, runtime = self.repository.load()
        saved_head, saved_instance, saved_runtime = self.repository.save_with_state(head, instance, runtime)
        reloaded_head, reloaded_instance, reloaded_runtime = self.repository.load(saved_head)
        self.assertEqual(saved_head, head)
        self.assertEqual((saved_head, saved_instance, saved_runtime),
                         (reloaded_head, reloaded_instance, reloaded_runtime))

    def test_changed_state_writes_the_same_canonical_files_and_returns_reload_views(self):
        head, instance, runtime = self.repository.load()
        changed_runtime = {**runtime, 'status': 'running'}
        expected = self.repository.validate_candidate(instance, changed_runtime, head)
        saved_head, saved_instance, saved_runtime = self.repository.save_with_state(head, instance, changed_runtime)
        stored = self.repository._store.read_many(saved_head, sorted(expected['files']))
        self.assertNotEqual(saved_head, head)
        self.assertEqual(stored, expected['files'])
        self.assertEqual((saved_head, saved_instance, saved_runtime), self.repository.load(saved_head))

    def test_regular_save_still_rejects_invalid_input(self):
        head, instance, runtime = self.repository.load()
        with self.assertRaisesRegex(ValueError, exact(FLOAT_REFUSED)):
            self.repository.save_with_state(head, instance, {**runtime, 'status': float('nan')})
        self.assertEqual(self.repository.load()[0], head)

    def test_save_reads_parent_family_bytes_once_and_preserves_reload_equivalence(self):
        head, instance, runtime = self.repository.load()
        with ObservedCalls(reads=GitStateStore.read_many) as calls:
            saved = self.repository.save_with_state(head, instance, {**runtime, 'status': 'running'})
        self.assertEqual([call for call in calls.captured('reads') if call['commit'] == head], [])
        self.assertEqual(saved, self.repository.load(saved[0]))

    def test_save_rereads_only_new_artifact_evidence(self):
        head, instance, runtime = self.repository.load()
        ref, raw = 'runtime/artifacts/AB-evidence/notes.txt', b'checkpoint evidence'
        runtime['checkpoints'] = {'EX-evidence': {'evidence_files': [{'path': 'notes.txt',
            'artifact_ref': ref, 'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)}]}}
        head = self.repository.save_with_state(head, instance, runtime, artifacts={ref: raw})[0]
        head, instance, runtime = self.repository.load(head)
        with ObservedCalls(reads=GitStateStore.read_many,
                           capture={'reads': lambda arguments: list(arguments['paths'])}) as calls:
            saved = self.repository.save_with_state(head, instance, {**runtime, 'status': 'running'})
        self.assertFalse(any(ref in paths for paths in calls.captured('reads')), calls.captured('reads'))
        self.assertEqual(saved, self.repository.load(saved[0]))
        changed = deepcopy(saved[2])
        changed['checkpoints']['EX-evidence']['evidence_files'][0]['bytes'] += 1
        with self.assertRaisesRegex(ValueError, exact('artifact evidence missing or hash differs: ' + ref)):
            self.repository.save_with_state(saved[0], saved[1], changed)

    def test_reused_parent_bytes_still_reject_a_damaged_previous_snapshot(self):
        head, instance, runtime = self.repository.load()
        damaged = self.repository._store.publish(head, {'runtime/_state/metadata.json': b'{}\n'}).head
        with ObservedCalls(publish=GitStateStore.publish) as calls:
            with self.assertRaisesRegex(ValueError, exact('invalid record envelope fields')):
                self.repository.save_with_state(damaged, instance, runtime)
        self.assertEqual(calls.count('publish'), 0)
        self.assertEqual(self.repository._store.read_snapshot().head, damaged)

    def test_stale_head_is_rejected_before_artifact_shape(self):
        head, instance, runtime = self.repository.load()
        self.repository.save_with_state(head, instance, {**runtime, 'status': 'running'})
        with self.assertRaisesRegex(GitStateStoreConflict, exact(STALE)):
            self.repository.save_with_state(head, instance, runtime, artifacts={'outside-artifacts.txt': b'not allowed'})

    def test_artifact_bytes_and_namespace_are_checked_by_the_same_save_call(self):
        head, instance, runtime = self.repository.load()
        artifact_path, artifact_bytes = 'runtime/artifacts/AB-01/output.txt', b'sealed artifact bytes'
        saved_head, _, _ = self.repository.save_with_state(head, instance, runtime, artifacts={artifact_path: artifact_bytes})
        self.assertEqual(self.repository.read(artifact_path, saved_head), artifact_bytes)
        reloaded_head, reloaded_instance, reloaded_runtime = self.repository.load(saved_head)
        with self.assertRaisesRegex(ValueError, exact(OUTSIDE_NAMESPACE)):
            self.repository.save_with_state(reloaded_head, deepcopy(reloaded_instance), deepcopy(reloaded_runtime),
                                            artifacts={'outside-artifacts.txt': b'not allowed'})
        self.assertEqual(self.repository.load()[0], saved_head)


class CandidateCopyTests(unittest.TestCase):
    def test_candidate_numbers_events_without_a_second_whole_state_copy(self):
        instance, runtime = current_state({'title': 'fixture'}, {'events': [{'id': 'EV-1', 'kind': 'created'}]})
        before = deepcopy((instance, runtime))
        store = candidate_repository(self)
        with ObservedCalls(copy=deepcopy) as calls:
            candidate = store.validate_candidate(instance, runtime)
        # One copy of each root, made by the repository; event numbering works on that detached copy.
        self.assertEqual([id(call['x']) for call in calls.captured('copy', caller='do_math.repository')],
                         [id(instance), id(runtime)])
        self.assertEqual((instance, runtime), before)
        self.assertEqual(candidate['runtime']['events'][0]['event_seq'], 1)
        candidate['runtime']['events'][0]['kind'] = 'changed returned candidate'
        self.assertEqual((instance, runtime), before)

    def test_late_event_failure_never_numbers_the_callers_original(self):
        instance, runtime = current_state(runtime={'events': [
            {'id': 'EV-1', 'kind': 'created'},
            {'id': 'EV-2', 'kind': 'queued', 'event_seq': 99}]})
        before = deepcopy((instance, runtime))
        with self.assertRaisesRegex(ValueError, exact('new event sequence must be contiguous')):
            candidate_repository(self).validate_candidate(instance, runtime)
        self.assertEqual((instance, runtime), before)


class StorageValueTests(unittest.TestCase):
    def test_external_value_axes_have_exact_bytes_or_reject_without_publication(self):
        with tempfile.TemporaryDirectory() as directory:
            store = record_store(Path(directory))
            head = store.initialize(*current_state())
            _, instance, runtime = store.load(head)
            before = deepcopy((instance, runtime))
            for label, value, wire in EXTERNAL_JSON_VALUES:
                with self.subTest(label=label):
                    reason = ('JSON floating-point numbers are not permitted' if label == 'decimal' else
                              'JSON integers must be safe integers' if label.startswith('unsafe-') else None)
                    if reason:
                        proposed = {**runtime, 'provider_wake': {'value': value}}
                        original = deepcopy(proposed)
                        with self.assertRaisesRegex(ValueError, exact(reason)):
                            store.save_with_state(head, instance, proposed)
                        self.assertEqual(proposed, original)
                        self.assertEqual(store.load(head)[1:], before)
                        self.assertEqual(store.load()[0], head)
                    else:
                        self.assertEqual(canonical_json(value), wire + b'\n')
                        saved = store.save_with_state(head, instance, {**runtime, 'provider_wake': {'value': value}})
                        self.assertEqual(store.load(saved[0])[2]['provider_wake'], {'value': value})
                        head, instance, runtime = saved
                        before = deepcopy((instance, runtime))
            proposed = {**runtime, 'provider_wake': {'value': b'raw'}}
            original = deepcopy(proposed)
            with self.assertRaisesRegex(ValueError, exact('value is not JSON-serializable')):
                store.save_with_state(head, instance, proposed)
            self.assertEqual(proposed, original)
            self.assertEqual(store.load(), (head, *before))
            raw = b'\xff\x00'
            projected = {'sha256': hashlib.sha256(raw).hexdigest(), 'text': '\ufffd\x00', 'base64': '/wA='}
            self.assertEqual(json_safe(raw), projected)
            path = 'runtime/artifacts/BA-external-bytes/raw.bin'
            saved = store.save_with_state(head, instance, {**runtime, 'provider_wake': {'value': json_safe(raw)}},
                artifacts={path: raw})
            self.assertEqual(store.read(path, saved[0]), raw)
            self.assertEqual(store.load(saved[0])[2]['provider_wake'], {'value': projected})

    def test_value_validation_and_serialization_keep_the_same_domain(self):
        for value in (None, True, False, 0, -(2**53 - 1), 2**53 - 1,
                      {'e\N{COMBINING ACUTE ACCENT}': ['한글', '😀', 1], '\N{LATIN SMALL LETTER E WITH ACUTE}': None}):
            with self.subTest(value=value):
                self.assertIsNone(repository.validate_storage_value(value))
                self.assertIsInstance(repository.canonical_json(value), bytes)
        invalid = [0.0, float('nan'), float('inf'), float('-inf'), 2**53, -(2**53), '\ud800',
                   {1: 'non-string key'}, {'\udfff': 1}, b'raw', (1,), {'nested': [0.5]}]
        for value in invalid:
            with self.subTest(value=repr(value)):
                with self.assertRaises(ValueError) as checked:
                    repository.validate_storage_value(value)
                with self.assertRaises(ValueError) as encoded:
                    repository.canonical_json(value)
                self.assertEqual(str(checked.exception), str(encoded.exception))
        self.assertNotEqual(repository.canonical_json(True), repository.canonical_json(1))
        self.assertNotEqual(repository.canonical_json({'a': [2, 1]}), repository.canonical_json({'a': [1, 2]}))

    def test_inspection_builds_no_json_bytes_and_publication_checks_the_value_domain(self):
        instance, runtime = {'sources': []}, {'executions': {'EX-1': {'id': 'EX-1', 'output_files': []}}}
        with ObservedCalls(serialize=canonical_json) as calls:
            self.assertEqual(inspect_state(instance, runtime, requested_areas=['record_storage'])['status'], 'healthy')
        self.assertEqual(calls.count('serialize'), 0)
        # The storage value domain belongs to loading and publication: each
        # record serialized for a candidate passes the storage value check.
        instance, runtime = current_state(runtime={'provider_wake': {'measured': float('nan')}})
        with self.assertRaisesRegex(ValueError, exact(FLOAT_REFUSED)):
            candidate_repository(self).validate_candidate(instance, runtime)

    def test_a_float_equal_to_the_parent_integer_is_still_rejected(self):
        # 1.0 == 1, so the record equals its parent's and skips its schema check
        # and serialization; sealing the candidate rejects the float first.
        with tempfile.TemporaryDirectory() as directory:
            store = record_store(Path(directory))
            head = store.initialize(*current_state(runtime={'provider_wake': {'measured': 1}}))
            _, instance, runtime = store.load(head)
            runtime['provider_wake']['measured'] = 1.0
            with self.assertRaisesRegex(ValueError, exact(FLOAT_REFUSED)):
                store.save_with_state(head, instance, runtime)
            self.assertEqual(store.load()[0], head)


class SealedArtifactReadTests(unittest.TestCase):
    def test_a_sealed_row_is_hashed_once_and_matched_rows_are_not_reread(self):
        """The real engine on the port fakes over a repository holding the sealed artifact."""
        from support.entry import entry
        _entry = entry()
        from do_math.repository import ResearchRepository
        from do_math.engine import ResearchEngine
        raw = b'sealed bytes'
        digest = hashlib.sha256(raw).hexdigest()
        path = 'runtime/artifacts/BA-sealed/output.json'
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            clock, backend = FakeClock(), InProcessGit()
            store = record_store(root / 'repository', backend=backend, clock=clock)
            ports = fake_ports(clock, backend)
            instance, runtime = current_state({'id': INSTANCE_ID})
            _, head = engine_on(store, instance, runtime, workspace=root / 'work', ports=ports)
            _, instance, runtime = store.load(head)
            store.save_with_state(head, instance, runtime, artifacts={path: raw})
            # A new process's engine: this repository's rows are not yet matched.
            engine = ResearchEngine(store.repository, INSTANCE_ID, ports=ports, codex_home=_entry.codex_home, environment=_entry.environment, host_id=_entry.host_id)
            self.assertEqual(engine.store.git_dir, store.git_dir)
            # One observation over all four calls: the two that hash are the probes' positive control.
            with BuiltinCalls(hashlib.sha256) as sha256, \
                    ObservedCalls(read=ResearchRepository.read) as reads:
                with self.assertRaisesRegex(ValueError, exact('sealed artifact differs from its record: ' + path)):
                    engine._sealed_bytes(path, 'b' * 64, len(raw))
                self.assertEqual((sha256.arguments, reads.count('read')), ([raw], 1))
                self.assertEqual(engine._sealed_bytes(path, digest, len(raw)), raw)
                self.assertEqual((sha256.arguments, reads.count('read')), ([raw, raw], 2))
                # The matched row is read but not hashed again.
                self.assertEqual(engine._sealed_bytes(path, digest, len(raw)), raw)
                self.assertEqual((sha256.arguments, reads.count('read')), ([raw, raw], 3))
                # needed=False neither reads nor hashes.
                self.assertIsNone(engine._sealed_bytes(path, digest, len(raw), needed=False))
            self.assertEqual((sha256.arguments, reads.count('read')), ([raw, raw], 3), 'matched row rehashed or reread')


if __name__ == '__main__':
    unittest.main()
