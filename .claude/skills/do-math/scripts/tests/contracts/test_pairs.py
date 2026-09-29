"""Every contract pair (설계 3.3; 의무 1-A, 1-C): each producer branch passes its receiving check, and the
receiver names no field that no producer branch writes."""
from copy import deepcopy
from pathlib import Path
import tempfile
import unittest

from contracts.pairs import PAIRS


class ContractPairTests(unittest.TestCase):
    def test_every_producer_branch_is_received_and_every_named_field_is_produced(self):
        self.assertGreater(len(PAIRS), 0)
        for pair in PAIRS:
            with self.subTest(pair=pair.name), tempfile.TemporaryDirectory() as directory:
                samples = pair.samples(Path(directory))
                self.assertGreater(len(samples), 0, 'a pair needs producer samples')
                self.assertGreater(len(pair.fields), 0, 'a pair names the receiver fields')
                rejected = []
                for branch, value in samples:
                    try:
                        pair.receive(deepcopy(value))
                    except ValueError as error:
                        rejected.append((branch, str(error)))
                self.assertEqual(rejected, [], 'producer branches the receiving check rejects')
                written = set().union(*(pair.written(value) for _, value in samples))
                self.assertEqual(sorted(pair.fields - written), [],
                                 'fields the receiving check names that no producer branch writes')


if __name__ == '__main__':
    unittest.main()
