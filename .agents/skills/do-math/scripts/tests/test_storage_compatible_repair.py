from pathlib import Path
from copy import deepcopy
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math.repository import ResearchRepository, new_id
from do_math.state_contract import StateContract


class CompatibleCheckerRepairTests(unittest.TestCase):
    @staticmethod
    def fixture_contract(*, optional=False, shape='map'):
        schema = {'type': 'object', 'additionalProperties': False,
                  'properties': {'id': {'type': 'string'}, 'text': {'type': 'string'}},
                  'required': ['id', 'text']}
        if optional:
            schema['properties']['annotation'] = {'type': 'string'}
        contract = StateContract.default()
        contract.register_family('research', 'format_fixture', shape=shape, schema=schema)
        return contract

    def test_compatible_schema_extension_validates_existing_records_and_new_values(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            subprocess.run(['git', 'init', '--quiet', str(root)], check=True, capture_output=True)
            identifier = new_id('RI')
            before = ResearchRepository(root, identifier, contract=self.fixture_contract())
            head = before.initialize({'feature_version': 5, 'format_fixture': {
                'FF-one': {'id': 'FF-one', 'text': 'e\u0301 K K'}}}, {'feature_version': 5})
            after = ResearchRepository(root, identifier, contract=self.fixture_contract(optional=True))
            loaded, instance, runtime = after.load(head)
            self.assertEqual(loaded, head)
            original = deepcopy(instance)
            instance['format_fixture']['FF-one']['annotation'] = 'new optional field'
            current = after.save(head, instance, runtime)
            self.assertEqual(after.load(current)[1], instance)
            self.assertEqual(after.load(head)[1], original)
            broken = deepcopy(instance)
            broken['format_fixture']['FF-one']['annotation'] = 3
            with self.assertRaises(ValueError):
                after.save(current, broken, runtime)
            with self.assertRaises(ValueError):
                before.load(current)

    def test_compatible_checker_repair_reads_snapshot_and_enforces_current_rules(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            subprocess.run(['git', 'init', '--quiet', str(root)], check=True, capture_output=True)
            identifier = new_id('RI')
            before = ResearchRepository(root, identifier)
            head = before.initialize({'feature_version': 5, 'sources': [
                {'id': 'SO-input', 'path': 'original.txt', 'sha256': 'a' * 64}]}, {'feature_version': 5})

            contract = StateContract.default()
            def check_source(record):
                if record['path'] != 'original.txt':
                    raise ValueError('repaired source rule')
            contract.register_family('research', 'sources', shape='list', validator=check_source)
            after = ResearchRepository(root, identifier, contract=contract)
            loaded, instance, runtime = after.load(head)
            self.assertEqual(loaded, head)
            instance['sources'][0]['path'] = 'unexpected.txt'
            with self.assertRaisesRegex(ValueError, 'repaired source rule'):
                after.save(head, instance, runtime)
            self.assertEqual(after.load()[1]['sources'][0]['path'], 'original.txt')

    def test_different_representation_still_rejects_old_snapshot(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            subprocess.run(['git', 'init', '--quiet', str(root)], check=True, capture_output=True)
            identifier = new_id('RI')
            repository = ResearchRepository(root, identifier, contract=self.fixture_contract())
            head = repository.initialize({'feature_version': 5, 'format_fixture': {
                'FF-one': {'id': 'FF-one', 'text': 'original'}}}, {'feature_version': 5})
            changed = self.fixture_contract(shape='list')
            with self.assertRaisesRegex(ValueError, 'contract/schema|shape'):
                ResearchRepository(root, identifier, contract=changed).load(head)


if __name__ == '__main__':
    unittest.main()
