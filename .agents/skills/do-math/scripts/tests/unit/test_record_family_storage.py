"""State stored as record-family files (``repository``, ``git_store``, ``events``; layers 1-2).

Records survive storage typed and closed, loading rejects what the contract
does not register, published events keep their numbers, and a lost
compare-and-swap leaves both the ref and the caller unchanged. The store is
the real ``ResearchRepository`` on the in-process Git fake (``RecordingGit``,
which also lists the objects a publication writes). A lost race is a real one:
another writer holds the instance ref's lock (``held_ref_lock``), as a
concurrent Git ref transaction does. Writing a damaged record past the
contract goes through the store's own ``_store.publish``.
"""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from do_math.canonical import canonical_json
from do_math.events import EventPublisher, check_sequence
from do_math.git_store import GitStateStoreConflict
from support.state_builders import current_state, installed_contract, with_validator
from support.fakes.clock import FakeClock
from support.storage_records import INSTANCE_ID, OTHER_INSTANCE_ID, RecordingGit, held_ref_lock, record_store

LOST_RACE = '^state ref changed before the publish compare-and-swap$'


class StoreCase(unittest.TestCase):
    """A new repository per test and the store of ``INSTANCE_ID`` on it."""

    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.repository_path = self.root / 'repository'
        self.clock, self.backend = FakeClock(), RecordingGit()
        self.repository = self.store()

    def store(self, **options):
        """Another store on this test's repository, Git fake and clock."""
        return record_store(options.pop('path', self.repository_path), backend=self.backend, clock=self.clock, **options)


class FamilyRecordStorageTests(StoreCase):
    def test_state_persists_as_family_files_and_reconstructs_views(self):
        instance, runtime = current_state(
            {'sources': [{'id': 'SO-01', 'path': 'runtime/artifacts/input/source.txt', 'sha256': 'a' * 64}]},
            {'events': [{'id': 'EV-01', 'kind': 'created'}]})
        head = self.repository.initialize(instance, runtime)
        loaded = self.repository.load(head)
        self.assertEqual(loaded[1]['sources'], instance['sources'])
        self.assertEqual(loaded[2]['events'][0]['event_seq'], 1)
        files = self.repository.list_files('research/', head) + self.repository.list_files('runtime/', head)
        self.assertIn('research/sources/SO-01.json', files)
        self.assertIn('runtime/events/EV-01.json', files)
        self.assertNotIn('research/instance.json', files)
        self.assertNotIn('runtime/state.json', files)

    def test_scalar_metadata_is_one_closed_record_per_root(self):
        instance, runtime = current_state({'id': INSTANCE_ID, 'title': 'Title', 'created_at': '2026-09-20T00:00:00Z'},
                                          {'status': 'ready', 'cycles': 0})
        head = self.repository.initialize(instance, runtime)
        self.assertIn('research/_state/metadata.json', self.repository.list_files('research/', head))
        self.assertNotIn('research/title/state.json', self.repository.list_files('research/', head))
        self.assertEqual(self.repository.load(head)[1]['title'], 'Title')
        rows = [row for row in self.repository.load_records(head)[3] if row['family'] == 'metadata']
        self.assertEqual(len(rows), 2)
        self.assertTrue(all(row['sha256'] == hashlib.sha256(row['bytes']).hexdigest() for row in rows))

    def test_final_goal_assessment_keeps_its_recorded_group_key_in_git(self):
        basis = 'a' * 64
        head = self.repository.initialize(*current_state({'goal_assessment_basis': basis}))
        self.assertEqual(self.repository.load(head)[1]['goal_assessment_basis'], basis)

    def test_save_rejects_global_identifier_collision_and_missing_reference(self):
        instance, runtime = current_state({'sources': [{'id': 'SO-01', 'path': 'input.txt', 'sha256': 'a' * 64}]})
        head = self.repository.initialize(instance, runtime)
        collision = {**runtime, 'events': [{'id': 'SO-01', 'kind': 'created'}]}
        with self.assertRaisesRegex(ValueError, 'globally unique'):
            self.repository.save_with_state(head, instance, collision)
        contract = installed_contract()
        contract.register_family(
            'runtime', 'links',
            schema={'type': 'object', 'properties': {'id': {'type': 'string'}, 'target_id': {'type': 'string'}},
                    'required': ['id', 'target_id'], 'additionalProperties': False},
            references=lambda record: [record['target_id']])
        repository = self.store(instance_id=OTHER_INSTANCE_ID, contract=contract)
        with self.assertRaisesRegex(ValueError, 'unknown record'):
            repository.initialize(*current_state(runtime={'links': {'LK-01': {'id': 'LK-01', 'target_id': 'missing'}}}))

    def test_unknown_family_and_malformed_map_do_not_become_singletons(self):
        # The malformed map's record also lacks required fields, which are checked first.
        from support.entry import entry
        _entry = entry()
        for state, reason in (({'unregistered_records': {}}, '^unregistered family: research/unregistered_records$'),
                              ({'knowledge': {'KN-1': {'id': 'KN-2'}}},
                               "^research/knowledge/KN-1/: 'lifecycle' is a required property$")):
            with self.subTest(state=state), self.assertRaisesRegex(ValueError, reason):
                self.repository.initialize(*current_state(state))
        # A complete record under another key is refused by the map rule itself.
        from do_math.knowledge_io import ensure_ontology
        from do_math.knowledge_records import create_candidate
        instance, kid = create_candidate(ensure_ontology(current_state()[0]), {
            'kind': 'observation', 'statement': 'prior', 'dependencies': []}, source_ref='input', actor_ref='user', clock=_entry.ports.clock)
        instance['knowledge']['KN-other'] = instance['knowledge'].pop(kid)
        with self.assertRaisesRegex(ValueError, '^knowledge map key and id differ$'):
            self.repository.initialize(instance, current_state()[1])

    def test_list_record_validation_cannot_be_bypassed(self):
        with self.assertRaisesRegex(ValueError, '^relations references unknown record: absent$'):
            self.repository.initialize(*current_state({'relations': [
                {'id': 'RL-1', 'kind': 'supports', 'source': 'absent', 'target': 'absent'}]}))

    def test_pure_validation_rejects_duplicate_list_ids_and_unknown_record_fields(self):
        row = {'id': 'SO-1', 'path': 'input.txt', 'sha256': 'a' * 64}
        for rows, reason in (([row, row], '^record IDs must be globally unique: SO-1$'),
                             ([{**row, 'mystery': True}],
                              r"Additional properties are not allowed \('mystery' was unexpected\)$")):
            with self.subTest(rows=rows), self.assertRaisesRegex(ValueError, reason):
                self.repository.validate_candidate(*current_state({'sources': rows}))
        self.assertIsNone(self.repository._store.read_snapshot().head)
        self.assertEqual(self.backend.writes, [])

    def test_current_lifecycle_empty_families_are_registered(self):
        names = ('trust_transitions', 'conversations', 'checkpoints', 'observations', 'extended_controls')
        checked = self.repository.validate_candidate(*current_state(runtime={name: {} for name in names}))
        self.assertEqual({name: checked['runtime'][name] for name in names}, {name: {} for name in names})

    def test_empty_family_and_list_order_round_trip_and_runtime_oid(self):
        instance, runtime = current_state({'knowledge': {}, 'sources': []}, {'events': []})
        head = self.repository.initialize(instance, runtime)
        runtime['events'] = [{'id': 'EV-Z', 'kind': 'first'}, {'id': 'EV-A', 'kind': 'second'}]
        next_head = self.repository.save_with_state(head, instance, runtime)[0]

        def research_tree(commit):
            return self.backend.object_info(self.repository_path, [commit + ':research'])[0][0]
        self.assertEqual(research_tree(next_head), research_tree(head))
        _, loaded, state = self.repository.load(next_head)
        self.assertEqual(loaded['knowledge'], {})
        self.assertEqual(loaded['sources'], [])
        self.assertEqual([r['id'] for r in state['events']], ['EV-Z', 'EV-A'])

    def test_unchanged_many_record_save_does_not_rewrite_blobs(self):
        instance, runtime = current_state({'sources': [{'id': 'SO-' + str(i), 'path': 'runtime/artifacts/B/file' + str(i),
                                                        'sha256': 'a' * 64} for i in range(64)]})
        head = self.repository.initialize(instance, runtime)
        _, instance, runtime = self.repository.load(head)
        # Every blob a publication writes is one of the changes handed to it.
        self.backend.writes.clear()
        same = self.repository.save_with_state(head, instance, runtime)[0]
        self.assertEqual(same, head)
        self.assertEqual(self.backend.writes, [])
        runtime['status'] = 'ready'
        changed = self.repository.save_with_state(head, instance, runtime)[0]
        self.assertNotEqual(changed, head)
        self.assertLessEqual(len([oid for kind, oid in self.backend.writes if kind == 'blob']), 2)

        def blobs(commit):
            return {path: oid for _, kind, oid, path in self.backend.list_tree(self.repository_path, commit) if kind == 'blob'}
        before, after = blobs(head), blobs(changed)
        self.assertLessEqual(len({path for path in before.keys() | after.keys() if before.get(path) != after.get(path)}), 2)

    def test_family_round_trip_on_sha256_repository(self):
        repository = self.store(path=self.root / 'sha256', object_format='sha256')
        head = repository.initialize(*current_state())
        self.assertEqual(len(head), 64)
        self.assertEqual(repository.load(head)[1]['object_format'], 'sha256')

    def test_identity_bearing_singleton_and_nonexecution_question(self):
        contract = installed_contract()
        contract.register_family('research', 'singleton_proof', shape='singleton', schema={
            'type': 'object', 'additionalProperties': False,
            'properties': {'id': {'type': 'string'}, 'claim': {'type': 'string'}}, 'required': ['id', 'claim']})
        repository = self.store(instance_id=OTHER_INSTANCE_ID, contract=contract)
        question = {'id': 'QU-1', 'origin_execution_id': None, 'origin_field': 'input_overflow/AC-1',
                    'source_ref': 'runtime/artifacts/BA-1/overflow.json', 'owner': 'user', 'target_ids': ['SP-1'],
                    'unresolved_target_ids': ['SP-1'], 'status': 'open', 'resolution_ref': None}
        head = repository.initialize(*current_state({'singleton_proof': {'id': 'SP-1', 'claim': 'P'}},
                                                    {'question_links': [question]}))
        self.assertEqual(repository.read_record('SP-1', head)['path'], 'research/singleton_proof/SP-1.json')
        self.assertIsNone(repository.load(head)[2]['question_links'][0]['origin_execution_id'])

    def test_question_target_can_be_a_preserved_waiting_action_coordinate(self):
        instance, runtime = current_state(runtime={'waiting_actions': {'AC-1': {
            'action': {'id': 'AC-1', 'role': 'research_plan'}, 'reason': 'input_overflow', 'question_id': 'QU-1'}},
            'question_links': [{'id': 'QU-1', 'origin_execution_id': None, 'origin_field': 'input_overflow/AC-1',
                                'source_ref': 'archived-overflow', 'owner': 'user', 'target_ids': ['AC-1'],
                                'unresolved_target_ids': ['AC-1'], 'status': 'open', 'resolution_ref': None}]})
        self.repository.validate_candidate(instance, runtime)
        runtime['question_links'][0].update(target_ids=['AC-absent'], unresolved_target_ids=['AC-absent'])
        with self.assertRaisesRegex(ValueError, 'question target'):
            self.repository.validate_candidate(instance, runtime)

    def test_resolved_question_preserves_a_historical_action_coordinate(self):
        instance, runtime = current_state(runtime={'waiting_actions': {},
            'question_links': [{'id': 'QU-1', 'origin_execution_id': None,
                                'origin_field': 'resolution_question/question', 'source_ref': 'archived-overflow',
                                'owner': 'user', 'target_ids': ['AC-finished'], 'unresolved_target_ids': [],
                                'blocks': True, 'status': 'resolved', 'resolution_ref': None}]})
        checked = self.repository.validate_candidate(instance, runtime)
        self.assertEqual(checked['runtime']['question_links'][0]['target_ids'], ['AC-finished'])


class ExactRecordTests(StoreCase):
    """Exact bytes: registered payloads, singleton roots, preserved text and the query cursor."""

    def test_lossless_query_cursor_retains_exact_search_text(self):
        from do_math.repository import _decode_cursor, _encode_cursor
        cursor = {'snapshot': 'a' * 40, 'prefix': 'research/', 'text': 'e\u0301', 'last_path': 'research/a.json'}
        self.assertEqual(_decode_cursor(_encode_cursor(cursor)), cursor)

    def test_plain_exact_json_rejects_invalid_stored_records_on_git_read(self):
        schema = {'type': 'object', 'additionalProperties': False,
                  'properties': {'id': {'type': 'string'}, 'payload': {'type': 'object', 'additionalProperties': False,
                                 'properties': {'text': {'type': 'string'}}, 'required': ['text']}},
                  'required': ['id', 'payload']}
        contract = installed_contract()
        contract.register_family('research', 'exact_negative', schema=schema)
        self.repository = self.store(contract=contract)
        head = self.repository.initialize(*current_state({'exact_negative': {
            'EN-1': {'id': 'EN-1', 'payload': {'text': 'e\u0301'}}}}))
        descriptor = self.repository.read_record('EN-1', head)
        stored = json.loads(descriptor['bytes'])
        for payload, reason in (({'text': 'valid string', 'unknown': 'forbidden'},
                                 r"^research/exact_negative/EN-1/payload: Additional properties are not allowed "
                                 r"\('unknown' was unexpected\)$"),
                                ({'text': 3}, "^research/exact_negative/EN-1/payload/text: 3 is not of type 'string'$")):
            with self.subTest(payload=payload):
                broken = deepcopy(stored)
                broken['record']['payload'] = payload
                head = self.repository._store.publish(head, {descriptor['path']: canonical_json(broken)}).head
                with self.assertRaisesRegex(ValueError, reason):
                    self.repository.load(head)

    def test_exact_singleton_root_is_typed_without_wrapper_autodetection(self):
        schema = {'type': 'array', 'items': {'type': 'object', 'additionalProperties': False,
                  'properties': {'value': {'type': 'string'}}, 'required': ['value']}}
        contract = installed_contract()
        contract.register_family('runtime', 'exact_history', shape='singleton', schema=schema, identity=False)
        self.repository = self.store(contract=contract)
        history = [{'value': 'e\u0301\r\n'}]
        head = self.repository.initialize(*current_state(runtime={'exact_history': history}))
        _, instance, runtime = self.repository.load(head)
        self.assertEqual(runtime['exact_history'], history)
        descriptor = next(row for row in self.repository.load_records(head)[3] if row['family'] == 'exact_history')
        self.assertEqual(descriptor['json_pointer'], '/record')

    def test_registered_exact_payload_keeps_closed_logical_validation_and_file_coordinates(self):
        schema = {'type': 'object', 'additionalProperties': False,
                  'properties': {'id': {'type': 'string'}, 'machine': {'type': 'string'},
                                 'payload': {'type': 'object', 'additionalProperties': {'type': 'string'}}},
                  'required': ['id', 'machine', 'payload']}
        contract = installed_contract()
        contract.register_family('research', 'exact_fixture', schema=schema)
        self.repository = self.store(contract=contract)
        record = {'id': 'EF-1', 'machine': 'e\u0301', 'payload': {'\u212a': 'e\u0301\r\n', 'K': 'é'}}
        instance, runtime = current_state({'exact_fixture': {record['id']: record}})
        checked = self.repository.validate_candidate(instance, runtime)
        self.assertEqual(record['machine'], 'e\u0301')  # pure candidate
        self.assertEqual(checked['instance']['exact_fixture']['EF-1']['machine'], 'e\u0301')
        head = self.repository.initialize(instance, runtime)
        _, state, run = self.repository.load(head)
        self.assertEqual(state['exact_fixture']['EF-1']['payload'], record['payload'])
        descriptor = self.repository.read_record('EF-1', head)
        stored = json.loads(self.repository.read(descriptor['path'], head))
        self.assertEqual(stored['record']['payload'], record['payload'])
        self.assertEqual(descriptor['sha256'], hashlib.sha256(descriptor['bytes']).hexdigest())
        self.assertEqual(descriptor['json_pointer'], '/record')
        self.assertEqual(descriptor['record'], state['exact_fixture']['EF-1'])
        self.assertEqual(self.repository.save_with_state(head, state, run)[0], head)
        state['exact_fixture']['EF-1']['payload']['K'] = 7
        with self.assertRaisesRegex(ValueError, "^research/exact_fixture/EF-1/payload/K: 7 is not of type 'string'$"):
            self.repository.validate_candidate(state, run)

    def test_governance_original_text_survives_lossless_git_and_immutable_check(self):
        from do_math.governance import preserve_source
        text = 'Prove that "e\u0301" contains two Unicode code points.\r\n'
        source = preserve_source('GS-exact', text, origin='user')
        instance, runtime = current_state({'governance_sources': {source['id']: source}})
        head = self.repository.initialize(instance, runtime)
        _, state, runtime = self.repository.load(head)
        self.assertEqual(state['governance_sources'][source['id']], source)
        state['governance_sources'][source['id']] = preserve_source('GS-exact', text.replace('e\u0301', 'é'),
                                                                    origin='user')
        with self.assertRaisesRegex(ValueError, 'immutable'):
            self.repository.save_with_state(head, state, runtime)

    def test_exact_record_evidence_and_corrupt_record_rejected_on_load(self):
        head = self.repository.initialize(*current_state({'sources': [{'id': 'SO-1', 'path': 'input.txt', 'sha256': 'a' * 64}]}))
        descriptor = self.repository.read_record('SO-1', head)
        raw = self.repository.read(descriptor['path'], head)
        self.assertEqual(raw, descriptor['bytes'])
        self.assertEqual(hashlib.sha256(raw).hexdigest(), descriptor['sha256'])
        tampered = json.loads(raw)
        tampered['record']['unknown_authority'] = True
        bad = self.repository._store.publish(head, {descriptor['path']: canonical_json(tampered)}).head
        with self.assertRaisesRegex(ValueError, 'Additional properties'):
            self.repository.load(bad)


class ContractEditionTests(StoreCase):
    """The installed contract: registration, object format, edition, manifest and lifecycle gate."""

    def test_registration_requires_closed_schema_once_and_runs_the_owner_checker(self):
        contract = installed_contract()
        for schema, reason in ((None, '^explicit record schema is required: unknown$'),
                               ({'type': 'object'}, '^record schema must reject unknown fields: unknown$')):
            with self.subTest(schema=schema), self.assertRaisesRegex(ValueError, reason):
                contract.register_family('runtime', 'unknown', schema=schema)
        with self.assertRaisesRegex(ValueError, 'already registered'):
            contract.register_family('research', 'sources', shape='list', validator=lambda record: None)

        def reject(_):
            raise ValueError('owner checker invoked')
        with_validator(contract, 'research', 'sources', reject)
        repository = self.store(instance_id=OTHER_INSTANCE_ID, contract=contract)
        with self.assertRaisesRegex(ValueError, 'owner checker invoked'):
            repository.validate_candidate(*current_state({'sources': [{'id': 'SO-1', 'path': 'x', 'sha256': 'a' * 64}]}))

    def test_storage_object_format_and_contract_versions_are_enforced(self):
        head = self.repository.initialize(*current_state())
        _, instance, runtime = self.repository.load(head)
        instance['object_format'] = 'sha256'
        with self.assertRaisesRegex(ValueError, 'object_format'):
            self.repository.save_with_state(head, instance, runtime)
        path = 'research/_state/manifest.json'
        manifest = json.loads(self.repository.read(path, head))
        manifest['contract']['sha256'] = '0' * 64
        bad = self.repository._store.publish(head, {path: canonical_json(manifest)}).head
        # Same edition is checked against current values and layout.
        self.assertEqual(self.repository.load(bad)[0], bad)
        manifest['contract']['contract_id'] = 'unsupported'
        incompatible = self.repository._store.publish(bad, {path: canonical_json(manifest)}).head
        with self.assertRaisesRegex(ValueError, 'contract/schema'):
            self.repository.load(incompatible)

    def test_load_rejects_removed_required_contract_field(self):
        head = self.repository.initialize(*current_state())
        path = 'runtime/_state/manifest.json'
        manifest = json.loads(self.repository.read(path, head))
        del manifest['containers']['status']
        bad = self.repository._store.publish(head, {path: canonical_json(manifest)}).head
        with self.assertRaisesRegex(ValueError, 'status'):
            self.repository.load(bad)

    def test_complete_lifecycle_candidate_uses_installed_current_state_gate(self):
        from support.entry import entry
        _entry = entry()
        from do_math.initialization import initialize_state
        instance, runtime = initialize_state(instance_id=INSTANCE_ID, goal='P', workspace=self.repository_path, config={},
                                             source_input='P', clock=_entry.ports.clock, host=_entry.ports.host)
        self.repository.validate_candidate(instance, runtime)
        runtime['status'] = 'invented_status'
        with self.assertRaisesRegex(ValueError, 'runtime/status'):
            self.repository.validate_candidate(instance, runtime)

    def test_original_input_bytes_are_the_exact_working_text(self):
        from support.entry import entry
        _entry = entry()
        from do_math.initialization import initialize_state, original_input_bytes
        source = 'e\u0301 original input'
        instance, runtime = initialize_state(instance_id=INSTANCE_ID, goal='P', workspace=self.repository_path, config={},
                                             source_input=source, clock=_entry.ports.clock, host=_entry.ports.host)
        original = instance['lifecycle']['immutable_input']
        self.assertEqual(original_input_bytes(original), source.encode('utf-8'))
        self.assertEqual(original, {'text': source, 'sha256': hashlib.sha256(source.encode('utf-8')).hexdigest(),
                                    'bytes': len(source.encode('utf-8'))})
        original['sha256'] = '0' * 64
        with self.assertRaisesRegex(ValueError, '^immutable input bytes or hash differs$'):
            self.repository.validate_candidate(instance, runtime)

    def test_initial_input_and_loaded_pending_event_references_are_checked(self):
        from support.entry import entry
        _entry = entry()
        from do_math.initialization import initialize_state
        instance, runtime = initialize_state(instance_id=INSTANCE_ID, goal='P', workspace=self.repository_path, config={},
                                             source_input='P', clock=_entry.ports.clock, host=_entry.ports.host)
        runtime['inputs'] = []
        with self.assertRaisesRegex(ValueError, 'unknown record'):
            self.repository.validate_candidate(instance, runtime)
        head = self.repository.initialize(*current_state(runtime={
            'events': [{'id': 'EV-1', 'kind': 'first'}], 'pending_events': ['EV-1']}))
        path = 'runtime/pending_events/state.json'
        value = json.loads(self.repository.read(path, head))
        value['record'] = ['EV-unknown']
        bad = self.repository._store.publish(head, {path: canonical_json(value)}).head
        with self.assertRaisesRegex(ValueError, 'unknown record'):
            self.repository.load(bad)


class PublishedEventTests(StoreCase):
    """Published events on the store: numbering at publication, immutability, and lost races."""

    def test_public_events_receive_contiguous_sequence_at_publish_boundary(self):
        rows = [{'id': 'EV-01', 'kind': 'created'}, {'id': 'EV-02', 'kind': 'queued'}]
        runtime = self.repository.validate_candidate(*current_state(runtime={'events': rows}))['runtime']
        self.assertEqual([row['event_seq'] for row in runtime['events']], [1, 2])
        self.assertEqual(runtime['event_cursor'], 2)
        # Events are one record list; a map of events is refused.
        with self.assertRaisesRegex(ValueError, 'record list'):
            self.repository.validate_candidate(*current_state(runtime={'events': {row['id']: row for row in rows}}))

    def test_pending_event_references_remain_unconsumed_after_publication(self):
        instance, runtime = current_state(runtime={'events': [{'id': 'EV-1', 'kind': 'created'}], 'pending_events': ['EV-1']})
        head = self.repository.initialize(instance, runtime)
        _, instance, runtime = self.repository.load(head)
        self.assertEqual(runtime['pending_events'], ['EV-1'])
        runtime['pending_events'] = ['EV-missing']
        with self.assertRaisesRegex(ValueError, '^pending_events references unknown event$'):
            self.repository.save_with_state(head, instance, runtime)

    def test_published_event_content_is_immutable_and_retry_uses_parent(self):
        instance, runtime = current_state(runtime={'events': [{'id': 'EV-1', 'kind': 'created'}]})
        head = self.repository.initialize(instance, runtime)
        _, instance, runtime = self.repository.load(head)
        runtime['events'][0]['kind'] = 'rewritten'
        with self.assertRaisesRegex(ValueError, 'content cannot be rewritten'):
            self.repository.save_with_state(head, instance, runtime)

    def test_save_and_cas_failure_do_not_mutate_caller(self):
        instance, runtime = current_state(runtime={'events': [{'id': 'EV-1', 'kind': 'created'}]})
        original = deepcopy((instance, runtime))
        with held_ref_lock(self.repository), self.assertRaisesRegex(GitStateStoreConflict, LOST_RACE):
            self.repository.initialize(instance, runtime)
        self.assertEqual((instance, runtime), original)
        self.assertIsNone(self.repository._store.read_snapshot().head)

    def test_real_event_storage_retry_removal_and_order(self):
        instance, runtime = current_state(runtime={'events': [{'id': 'EV-1', 'kind': 'created'}]})
        head = self.repository.initialize(instance, runtime)
        _, instance, runtime = self.repository.load(head)
        runtime['events'].append({'id': 'EV-2', 'kind': 'queued'})
        before = deepcopy((instance, runtime))
        with held_ref_lock(self.repository), self.assertRaisesRegex(GitStateStoreConflict, LOST_RACE):
            self.repository.save_with_state(head, instance, runtime)
        self.assertEqual((instance, runtime), before)
        self.assertEqual(self.repository._store.read_snapshot().head, head)
        next_head = self.repository.save_with_state(head, instance, runtime)[0]
        _, instance, runtime = self.repository.load(next_head)
        self.assertEqual([e['event_seq'] for e in runtime['events']], [1, 2])
        retry = self.repository.save_with_state(next_head, instance, runtime)[0]
        self.assertEqual(self.repository.load(retry)[2]['events'], runtime['events'])
        runtime['events'].reverse()
        with self.assertRaisesRegex(ValueError, 'published event sequence is not contiguous'):
            self.repository.save_with_state(retry, instance, runtime)
        runtime['events'].clear()
        with self.assertRaisesRegex(ValueError, 'removed'):
            self.repository.save_with_state(retry, instance, runtime)

    def test_real_stale_cas_retry_keeps_pending_obligations_and_caller(self):
        head = self.repository.initialize(*current_state(runtime={'events': [{'id': 'EV-1', 'kind': 'first'}],
                                                                  'pending_events': ['EV-1']}))
        _, instance, winner = self.repository.load(head)
        loser = deepcopy(winner)
        winner['events'].append({'id': 'EV-2', 'kind': 'winner'})
        accepted = self.repository.save_with_state(head, instance, winner)[0]
        loser['events'].append({'id': 'EV-3', 'kind': 'retry'})
        before = deepcopy((instance, loser))
        with self.assertRaisesRegex(GitStateStoreConflict, '^expected head no longer matches the instance ref$'):
            self.repository.save_with_state(head, instance, loser)
        self.assertEqual((instance, loser), before)
        _, instance, retry = self.repository.load(accepted)
        retry['events'].append(loser['events'][-1])
        final = self.repository.save_with_state(accepted, instance, retry)[0]
        saved = self.repository.load(final)[2]
        self.assertEqual([r['event_seq'] for r in saved['events']], [1, 2, 3])
        self.assertEqual(saved['pending_events'], ['EV-1'])


class EventSequenceRuleTests(unittest.TestCase):
    """The public event numbering rules (``events``, layer 1), without a store."""

    def test_republication_keeps_prior_event_sequence_and_only_numbers_new_events(self):
        previous = {'EV-01': {'id': 'EV-01', 'event_seq': 1, 'kind': 'created'}}
        runtime = {'events': [dict(previous['EV-01']), {'id': 'EV-02', 'kind': 'queued'}]}
        EventPublisher.assign_sequences_in_place(runtime, published_events=previous)
        self.assertEqual([row['event_seq'] for row in runtime['events']], [1, 2])

    def test_published_event_numbers_require_exact_integers_in_every_position(self):
        # check_sequence is the published numbering rule; reading a snapshot applies it.
        for bad in (True, 1.0, None, '1', 0, -1):
            with self.subTest(number=bad):
                rows = [{'id': 'EV-01', 'event_seq': bad, 'kind': 'created'},
                        {'id': 'EV-02', 'event_seq': 2, 'kind': 'queued'}]
                with self.assertRaisesRegex(ValueError, 'published event sequence is not contiguous'):
                    check_sequence(rows)

    def test_current_event_numbers_require_exact_integers(self):
        for bad in (True, 1.0, None, '1', 0, -1):
            for previous in ({}, {'EV-01': {'id': 'EV-01', 'event_seq': 1, 'kind': 'created'}}):
                with self.subTest(number=bad, published=bool(previous)):
                    with self.assertRaisesRegex(ValueError, 'invalid event sequence'):
                        EventPublisher.assign_sequences_in_place({'events': [
                            {'id': 'EV-01', 'event_seq': bad, 'kind': 'created'}]}, published_events=previous)

    def test_event_publication_preserves_history_and_rejects_unbacked_sequence(self):
        previous = {'EV-01': {'id': 'EV-01', 'event_seq': 1, 'kind': 'created'}}
        for rows, message in (([], 'cannot be removed'),
                              ([{**previous['EV-01'], 'kind': 'rewritten'}], 'content cannot be rewritten'),
                              ([{**previous['EV-01'], 'event_seq': 2}], 'sequence cannot be rewritten')):
            with self.subTest(message=message), self.assertRaisesRegex(ValueError, message):
                EventPublisher.assign_sequences_in_place({'events': rows}, published_events=previous)
        with self.assertRaisesRegex(ValueError, 'contiguous'):
            EventPublisher.assign_sequences_in_place({'events': [{'id': 'EV-unbacked', 'event_seq': 8}]})


if __name__ == '__main__':
    unittest.main()
