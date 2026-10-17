"""Record identity rules the engine publishes by: exact evidence hashes and globally unique record IDs."""
import hashlib
import base64
from pathlib import Path
import tempfile
import unittest

from do_math.canonical import canonical_json, exact_content_hash
from do_math.engine import _record_evidence
from do_math.state_contract import default_state_contract
from support.state_builders import current_state


class QueryIdentity(unittest.TestCase):
    def test_cursor_rejects_json_values_without_a_query_snapshot_and_record_identity(self):
        from do_math.core_engine import query_records
        from support.fakes.clock import FakeClock
        from support.fakes.git_backend import InProcessGit
        from support.storage_records import INSTANCE_ID
        parameters = {'instance_id': INSTANCE_ID, 'kind': None, 'text': '',
                      'related_to': None, 'direction': 'both'}
        valid = {'parameters': parameters, 'snapshot': 'a' * 40, 'last': 'PF-one'}
        for value in (None, [], True, 1, 'text', {},
                {**valid, 'snapshot': []}, {**valid, 'last': None}):
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, '^invalid cursor$'):
                query_records(Path('unused'), INSTANCE_ID,
                    cursor=base64.urlsafe_b64encode(canonical_json(value)).decode('ascii'),
                    backend=InProcessGit(), clock=FakeClock())

    def test_public_query_pages_keep_the_snapshot_filters_relations_and_exact_evidence(self):
        from do_math.core_engine import query_records
        from support.storage_records import INSTANCE_ID, record_store, reference_fixture_instance
        from support.state_builders import current_state
        with tempfile.TemporaryDirectory() as directory:
            store = record_store(Path(directory))
            instance, runtime = current_state(reference_fixture_instance())
            instance['id'] = INSTANCE_ID
            head = store.initialize(instance, runtime)
            def query(**options):
                return query_records(store.repository, INSTANCE_ID, backend=store._store._backend,
                                     clock=store._store._clock, **options)
            all_rows = query(limit=1000)
            expected = [item['record'] for item in all_rows['items']]
            first = query(limit=1)
            self.assertTrue(first['truncated'])
            self.assertEqual(first['loaded'], 1)
            self.assertEqual(first['total'], len(expected))
            instance['title'] = 'later edition'
            later = store.save_with_state(head, instance, runtime)[0]
            rest = query(cursor=first['next_cursor'], limit=1000)
            self.assertEqual(rest['snapshot'], head)
            self.assertEqual([item['record'] for item in first['items'] + rest['items']], expected)
            self.assertFalse(rest['truncated'])
            self.assertIsNone(rest['next_cursor'])
            for item in rest['items']:
                self.assertEqual(item['sha256'], hashlib.sha256(store.read(item['path'], head)).hexdigest())
            with self.assertRaisesRegex(ValueError, '^cursor query or snapshot changed$'):
                query(cursor=first['next_cursor'], snapshot=later)
            with self.assertRaisesRegex(ValueError, '^cursor query or snapshot changed$'):
                query(cursor=first['next_cursor'], text='different')
            invalid = {'parameters': all_rows['query_basis']['parameters'], 'snapshot': head, 'last': 'absent'}
            with self.assertRaisesRegex(ValueError, '^cursor does not name a record in the fixed query$'):
                query(cursor=base64.urlsafe_b64encode(canonical_json(invalid)).decode('ascii'))
            with self.assertRaisesRegex(ValueError, '^invalid cursor$'):
                query(cursor='!')
            for limit in (0, 1001, True, '2'):
                with self.subTest(limit=limit), self.assertRaisesRegex(ValueError, '^limit must be between 1 and 1000$'):
                    query(limit=limit)
            with self.assertRaisesRegex(ValueError, '^direction must be incoming, outgoing or both$'):
                query(direction='sideways')
            # Source and grant are actual product records; matching is case insensitive.
            matched = query(text='AUTHORIZE THE FIXTURE RESEARCH.')
            self.assertEqual(matched['query_basis']['loaded_ids'], ['GS-reference'])
            self.assertEqual(store.load()[0], later)

    def test_related_query_distinguishes_incoming_outgoing_and_both_at_the_stored_head(self):
        from do_math.core_engine import query_records
        from do_math.knowledge_io import import_candidate, import_relation, ensure_ontology
        from support.storage_records import INSTANCE_ID, record_store
        from support.state_builders import current_state
        with tempfile.TemporaryDirectory() as directory:
            store = record_store(Path(directory))
            instance, runtime = current_state({'id': INSTANCE_ID})
            instance = ensure_ontology(instance)
            kids = []
            for title in ('One', 'Two'):
                instance, runtime, kid = import_candidate(instance, runtime,
                    {'kind': 'question', 'title': title, 'statement': title, 'summary': title,
                     'explanation': title, 'lean_code': '', 'declaration_names': [], 'dependencies': []},
                    source_ref=INSTANCE_ID, actor_ref=INSTANCE_ID, clock=store._store._clock)
                kids.append(kid)
            instance, relation = import_relation(instance,
                {'kind': 'supports', 'source': kids[0], 'target': kids[1], 'evidence': 'inspect questions'},
                source_ref=INSTANCE_ID, actor_ref=INSTANCE_ID, clock=store._store._clock)
            head = store.initialize(instance, runtime)
            for source, direction, expected in ((kids[0], 'outgoing', {kids[1], relation}),
                    (kids[1], 'incoming', {kids[0], relation}), (kids[0], 'incoming', set()),
                    (kids[1], 'outgoing', set()), (kids[0], 'both', {kids[1], relation})):
                with self.subTest(source=source, direction=direction):
                    found = query_records(store.repository, INSTANCE_ID, related_to=source, direction=direction,
                        backend=store._store._backend, clock=store._store._clock)
                    self.assertEqual(set(found['query_basis']['loaded_ids']), expected)
                    self.assertEqual(found['snapshot'], head)
                    self.assertEqual(found['total'], len(expected))
            self.assertEqual(store.load()[0], head)

    def test_exact_evidence_binds_persisted_bytes_and_code_points(self):
        record = {"id": "FR-one", "title": "e\u0301", "verification": {"\u212a": "e\u0301", "K": "\u00e9"}}

        def evidence(value):
            raw = canonical_json({"record": value})
            row = {"snapshot": "snapshot", "path": "research/formal_results/FR-one.json", "record": value,
                   "bytes": raw, "sha256": hashlib.sha256(raw).hexdigest(), "json_pointer": "/record"}
            return _record_evidence(row)
        first = evidence(record)
        self.assertEqual(first["json_pointer"], "/record")
        self.assertEqual(first["sha256"], hashlib.sha256(canonical_json({"record": record})).hexdigest())
        self.assertEqual(first["logical_sha256"], exact_content_hash(record))
        same_metadata = {**record, "title": "\u00e9"}
        self.assertNotEqual(first["logical_sha256"], evidence(same_metadata)["logical_sha256"])
        changed_payload = {**record, "verification": {"\u212a": "\u00e9", "K": "\u00e9"}}
        self.assertNotEqual(first["logical_sha256"], evidence(changed_payload)["logical_sha256"])

    def test_duplicate_id_is_rejected_across_families(self):
        # The state contract checks global record IDs of every bundle candidate
        # (_validate_bundle_candidate -> validate_candidate) before publication.
        instance, runtime = current_state(
            {"object_format": "sha1", "sources": [{"id": "DUP", "path": "input.txt", "sha256": "a" * 64}]},
            {"events": [{"id": "DUP", "kind": "created"}]})
        with self.assertRaisesRegex(ValueError, "record IDs must be globally unique: DUP"):
            default_state_contract().validate(instance, runtime)


if __name__ == "__main__":
    unittest.main()
