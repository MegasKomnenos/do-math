"""Actual authority/ontology writes against all installed receiving fields."""
from copy import deepcopy
import hashlib
import re
from pathlib import Path
import tempfile
import unittest

from contracts.pairs import assert_pair
from support.storage_authority_pairs import authority_samples, family_pair, ontology_samples
from support.storage_records import record_store


class AuthorityFieldPairs(unittest.TestCase):
    def test_named_fields_handles_boolean_schemas_and_closed_tuple_members(self):
        from do_math.record_schemas.schemas import _ACTION, obj, nullable
        from support.storage_authority_pairs import _named_fields
        # The real failing input has repetition_lineage.items=False.
        self.assertIn('repetition_lineage', _named_fields(_ACTION))
        self.assertEqual(_named_fields(True), set())
        self.assertEqual(_named_fields(False), set())
        schema = obj({'tuple': {'type': 'array', 'prefixItems': [True,
            obj({'required': True, 'optional': False})], 'items': False},
            'nullable': nullable(obj({'nested': True})),
            'map': {'type': 'object', 'additionalProperties': obj({'member': True})}})
        self.assertEqual(_named_fields(schema), {'tuple', 'tuple[1]/required',
            'tuple[1]/optional', 'nullable', 'nullable/nested', 'map', 'map/{}/member'})
        values = [{'tuple': [0, {'required': 'actual'}], 'nullable': None, 'map': {}}]
        self.assertEqual(_named_fields(schema, values), {'tuple', 'tuple[1]/required', 'nullable', 'map'})
        conditional = {'allOf': [{'if': {'properties': {'kind': {'const': 'closed'}}, 'required': ['kind']},
            'then': {'properties': {'payload': obj({'must': True, 'optional': True})}},
            'else': {'properties': {'fallback': True}}}]}
        self.assertEqual(_named_fields(conditional), {'payload', 'payload/must', 'payload/optional', 'fallback'})
        self.assertEqual(_named_fields(conditional, [{'kind': 'open', 'payload': {'must': 1}, 'fallback': 0}]),
                         {'fallback'})

    def test_authority_fields_are_produced_approved_and_stored(self):
        """About 1.5 s: real initial approval, decisions and repository history on port fakes."""
        from do_math.canonical import exact_content_hash
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            samples = authority_samples(root)
            store = record_store(root / 'receiver')
            for family in ('decisions', 'delegations', 'governance', 'governance_approval', 'governance_sources', 'grants'):
                with self.subTest(family=family):
                    assert_pair(self, family_pair(store, family, samples), samples)
            before, approved = samples[0][1][0], samples[1][1][0]
            self.assertNotIn('governance_approval', before)
            self.assertEqual(before['governance'], {})
            self.assertEqual(before['grants'], {})
            approval = approved['governance_approval']
            original = approved['governance_sources'][approval['source_ref']]
            self.assertEqual(approval, {'decision_ref': next(iter(approved['decisions'])),
                'source_ref': original['id'], 'source_sha256': hashlib.sha256(original['text'].encode()).hexdigest()})
            final = samples[-2][1][0]
            preserved = final['governance_sources']['GS-authority-pair']
            raw = '승인 e\u0301\r\n권한의 범위는 이 원문 그대로다.\n'.encode()
            self.assertEqual((preserved['text'].encode(), preserved['bytes'], preserved['sha256'], preserved['revision']),
                             (raw, len(raw), hashlib.sha256(raw).hexdigest(), 2))
            for state in (approved, final):
                for record in state['governance'].values():
                    decision = state['decisions'][record['approval_ref']]
                    proposal = decision.get('change', {}).get('record')
                    expected = exact_content_hash(proposal) if proposal else decision['record_hashes'][record['id']]
                    self.assertEqual(record['content_sha256'], expected)
                    self.assertEqual(decision['source_sha256'], state['governance_sources'][decision['source_ref']]['sha256'])
            predecessor = next(row for row in final['governance'].values() if row['status'] == 'superseded')
            self.assertEqual(predecessor['superseded_by'], 'CH-authority-pair')
            self.assertEqual(final['governance']['CH-authority-pair']['supersedes'], [predecessor['id']])
            self.assertEqual(final['grants']['GR-authority-local']['replaced_by'], 'GR-authority-replacement')
            self.assertEqual(final['grants']['GR-authority-local']['status'], 'revoked')
            self.assertEqual(final['grants']['GR-authority-http']['status'], 'revoked')
            delegation = final['delegations']['DG-authority-pair']
            self.assertEqual((delegation['status'], delegation['resource_limits'], delegation['external_effects']),
                             ('revoked', {'steps': 2}, ['bounded-read']))
            decision = final['decisions'][delegation['decision_id']]
            self.assertEqual(decision['original_decision_sha256'], exact_content_hash(final['decisions'][delegation['original_decision_id']]))
            self.assert_removed_fields_rejected(root / 'rejected', samples[-2][1], 'decisions',
                                               ('coverage', 'intent_check', 'author_execution_ids'))

    def test_ontology_fields_reach_the_actual_map_and_list_receivers(self):
        """Actual imports, sealed relation review and a core kind verdict through storage."""
        from do_math.canonical import exact_content_hash
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            samples = ontology_samples(root)
            store = record_store(root / 'receiver')
            for family in ('kind_definitions', 'relations'):
                with self.subTest(family=family):
                    assert_pair(self, family_pair(store, family, samples), samples)
            by_name = dict(samples)
            proposed, _ = by_name['core kind proposals']
            checked, checked_runtime = by_name['core unresolved kind check']
            definition, = [row for row in proposed['kind_definitions'].values() if row['token'] == 'pending_fact']
            self.assertNotIn('check', definition)
            installed = checked['kind_definitions'][definition['id']]
            self.assertEqual(installed['check'], {
                'definition_id': definition['id'], 'definition_sha256': exact_content_hash(definition),
                'decision': 'unresolved', 'findings': ['정확한 미해결 근거 e\u0301\r\n추가 증거 필요'],
                'execution_id': 'EX-ontology-kind-reader'})
            checker = checked_runtime['executions']['EX-ontology-kind-reader']
            self.assertEqual((checker['role'], checker['status']), ('maintenance', 'ended'))
            self.assertNotEqual(checker['id'], definition['actor_ref'])
            self.assertEqual(checker['input_basis']['kind_definition'],
                             {'id': definition['id'], 'sha256': exact_content_hash(definition)})
            self.assertEqual(installed['status'], 'candidate')
            self.assertFalse(by_name['builtins and zero relations'][0].get('relations', []))
            relation, = by_name['one relation'][0]['relations']
            self.assertNotEqual(relation['source'], relation['target'])
            self.assertEqual(relation['authority'], 'research_connection')
            self.assertEqual(relation['evidence'].encode(), 'Exact e\u0301\r\nconnection'.encode())
            revised, = by_name['same relation new revision'][0]['relations']
            self.assertEqual((revised['revision'], revised['history']), (2, [relation]))
            self.assertEqual(revised['imported_by'], 'reviser')
            self.assertEqual(len(by_name['several research relations'][0]['relations']), 2)
            suspended = by_name['withdraw relation kind and suspend relation'][0]['relations'][0]
            self.assertEqual(suspended['status'], 'suspended')
            impacted = by_name['endpoint withdrawal propagates to relations'][0]['relations'][0]
            self.assertEqual(impacted['use_history'][-1]['reason'], 'Endpoint withdrawn')
            mathematical = by_name['mathematical relation with sealed evidence'][0]['relations'][-1]
            self.assertEqual(mathematical['authority'], 'mathematical_connection')
            self.assertEqual(len(mathematical['formal_result_refs']), 1)
            self.assertEqual(len(mathematical['assessment_refs']), 1)
            from do_math.knowledge_io import lookup_definition
            final = samples[-1][1][0]
            renewed = lookup_definition(final, 'knowledge', 'bounded_fact')
            old = final['kind_definitions'][renewed['supersedes']]
            self.assertEqual((renewed['status'], old['status'], old['withdrawn_reason']),
                             ('candidate', 'withdrawn', 'Refine the meaning'))
            self.assert_removed_fields_rejected(root / 'rejected-kinds', samples[-1][1], 'kind_definitions',
                                               ('history', 'checks', 'activation'))
            self.assert_removed_fields_rejected(root / 'rejected-relations', samples[-1][1], 'relations',
                                               ('lifecycle', 'created_at', 'actor_ref', 'origin_refs', 'source_basis'))

    def test_unproduced_optional_drift_fails_the_same_reverse_walk(self):
        """About 1 s: the real producer states also expose optional receiving-schema drift."""
        from do_math.state_contract import StateContract, default_state_contract
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            samples = authority_samples(root)
            store = record_store(root / 'receiver')
            definition = default_state_contract().family('research', 'grants')
            schema = deepcopy(definition.schema)
            schema['properties']['unproduced_optional'] = {'type': 'string'}
            contract = StateContract()
            contract.register_family('research', 'grants', schema=schema, shape=definition.shape)
            with self.assertRaisesRegex(AssertionError, 'unproduced_optional'):
                assert_pair(self, family_pair(store, 'grants', samples, contract=contract), samples)

    def assert_removed_fields_rejected(self, root, state, family, fields):
        store = record_store(root)
        head = store.initialize(*state)
        old = store.load(head)
        for field in fields:
            changed, runtime = deepcopy(state)
            records = changed[family]
            record = next(iter(records.values())) if isinstance(records, dict) else records[0]
            record[field] = []
            reason = "Additional properties are not allowed ('" + field + "' was unexpected)"
            with self.subTest(rejected=family + '.' + field), self.assertRaisesRegex(ValueError, re.escape(reason)):
                store.save_with_state(head, changed, runtime)
            self.assertEqual(store.load(), old)
