"""Every contract pair (설계 3.3; 의무 1-A, 1-C): each producer branch passes its receiving check, and the
receiver names no field that no producer branch writes. Branches a receiver rejects today are the known
defects below, each with its own reproduction."""
from copy import deepcopy
from pathlib import Path
import tempfile
import unittest

from contracts.pairs import (PAIRS, UNSTORABLE_RULE_IDS, accepted_condition, accepted_rule_ids, enumerated_pointers,
                             stored_rule_id_errors)
from support.known_defects import known_defect


class ContractPairTests(unittest.TestCase):
    def test_every_producer_branch_is_received_and_every_named_field_is_produced(self):
        self.assertGreater(len(PAIRS), 0)
        for pair in PAIRS:
            with self.subTest(pair=pair.name), tempfile.TemporaryDirectory() as directory:
                samples = pair.samples(Path(directory))
                self.assertGreater(len(samples), 0, 'a pair needs producer samples')
                rejected = []
                for branch, value in samples:
                    try:
                        pair.receive(deepcopy(value))
                    except ValueError as error:
                        rejected.append((branch, str(error)))
                self.assertEqual(rejected, [], 'producer branches the receiving check rejects')
                if pair.fields is not None:
                    written = set().union(*(pair.written(value) for _, value in samples))
                    self.assertEqual(sorted(pair.fields - written), [],
                                     'fields the receiving check names that no producer branch writes')


class KnownPairDefectTests(unittest.TestCase):
    @known_defect('KD-0007')
    def test_every_rule_id_the_tracker_accepts_is_storable(self):
        for rule_id, value in accepted_rule_ids(UNSTORABLE_RULE_IDS):
            with self.subTest(rule_id=rule_id):
                self.assertEqual(stored_rule_id_errors(value), [])

    @known_defect('KD-0008')
    def test_the_condition_grammar_rejects_values_outside_every_stored_enumeration(self):
        for family, space, pointer, enumeration in enumerated_pointers():
            with self.subTest(pointer=family + pointer):
                self.assertFalse(accepted_condition(space, family, pointer, 'not-a-stored-value'))


if __name__ == '__main__':
    unittest.main()
