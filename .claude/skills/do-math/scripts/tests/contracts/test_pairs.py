"""Every contract pair (설계 3.3; 의무 1-A, 1-C): each producer branch passes its receiving check, and the
receiver names no field that no producer branch writes. Branches a receiver rejects today are the known
defects below, each with its own reproduction."""
from copy import deepcopy
from pathlib import Path
import tempfile
import unittest

from contracts.pairs import (PAIRS, TEXT_RULE_ID_SAMPLES, accepted_condition, accepted_rule_ids, enumerated_pointers,
                             stored_rule_id_errors)


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


    def test_worker_samples_preserve_both_assigned_model_flags_for_each_legal_assignment(self):
        from do_math.claude_adapter import ADAPTERS
        prefix = 'worker request ('
        pairs = {pair.name[len(prefix):-1]: pair for pair in PAIRS if pair.name.startswith(prefix)}
        self.assertEqual(set(pairs), set(ADAPTERS))
        for provider, pair in pairs.items():
            with self.subTest(provider=provider), tempfile.TemporaryDirectory() as directory:
                assignments = {}
                for label, request in pair.samples(Path(directory)):
                    flags = label.split(',') if label != 'bare' else []
                    only = 'claude_only' in flags
                    key = tuple(flag for flag in flags if flag != 'claude_only')
                    choices = assignments.setdefault(key, {})
                    self.assertNotIn(only, choices, (provider, label))
                    choices[only] = request
                self.assertTrue(assignments, 'no worker assignments were examined')
                for assignment, choices in assignments.items():
                    with self.subTest(assignment=assignment):
                        self.assertEqual(set(choices), {False, True})
                        expected = deepcopy(choices[False])
                        if provider == 'claude':
                            expected['claude_only_assigned_model'] = True
                        self.assertEqual(choices[True], expected)


class KnownPairDefectTests(unittest.TestCase):
    def test_every_rule_id_the_tracker_accepts_is_storable(self):
        for rule_id, value in accepted_rule_ids(TEXT_RULE_ID_SAMPLES):
            with self.subTest(rule_id=rule_id):
                self.assertEqual(stored_rule_id_errors(value), [])

    def test_the_condition_grammar_rejects_values_outside_every_stored_enumeration(self):
        for family, space, pointer, enumeration in enumerated_pointers():
            with self.subTest(pointer=family + pointer):
                self.assertFalse(accepted_condition(space, family, pointer, 'not-a-stored-value'))


if __name__ == '__main__':
    unittest.main()
