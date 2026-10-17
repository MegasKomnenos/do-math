"""The actual split-record producers against the complete installed receiving fields."""
from copy import deepcopy
from pathlib import Path
import tempfile
import unittest

from contracts.pairs import assert_pair
from support.storage_knowledge_pairs import (engine_knowledge_samples, family_pair, identity_samples,
                                             knowledge_samples, replacement_samples, trust_samples)
from support.storage_records import record_store


class KnowledgeFieldPairs(unittest.TestCase):
    def test_trust_record_scalar_and_singleton_fields_reach_the_actual_receiver(self):
        """A few seconds: two file-backed toolchains through actual trust mixins and storage."""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            samples = trust_samples(root)
            store = record_store(root / 'receiver')
            for owner, family in (('research', 'active_trust_environment'), ('research', 'trust_environments'),
                                  ('runtime', 'trust_bindings'), ('runtime', 'trust_transitions')):
                with self.subTest(family=family):
                    assert_pair(self, family_pair(store, owner, family, samples), samples)

    def test_split_record_fields_are_written_and_received_with_their_actual_state(self):
        """About 8 s: actual domain/owner branches, complete state reception and optional drift."""
        from do_math.state_contract import StateContract, default_state_contract
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            samples = (knowledge_samples(root) + identity_samples(root) +
                       engine_knowledge_samples(root) + replacement_samples(root))
            store = record_store(root / 'receiver')
            for owner, family in (('research', 'formal_results'), ('research', 'expositions'),
                    ('research', 'assessment_uses'), ('research', 'identity_assessments'),
                    ('research', 'knowledge'), ('runtime', 'review_cycles'), ('runtime', 'review_inputs')):
                with self.subTest(family=family):
                    pair = family_pair(store, owner, family, samples)
                    assert_pair(self, pair, samples)
                    # Optional schema drift passes forward and fails in the
                    # very same reverse walk; it is not a required-field test.
                    definition = default_state_contract().family(owner, family)
                    schema = deepcopy(definition.schema)
                    fields = schema if definition.shape == 'map' else schema['additionalProperties']
                    fields['properties']['unproduced_optional'] = {'type': 'string'}
                    changed_contract = StateContract()
                    changed_contract.register_family(owner, family, schema=schema, shape=definition.shape,
                                                     identity=definition.identity)
                    changed = family_pair(store, owner, family, samples, contract=changed_contract)
                    with self.assertRaisesRegex(AssertionError, 'unproduced_optional'):
                        assert_pair(self, changed, samples)

