from pathlib import Path
from copy import deepcopy
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math.repository import ResearchRepository, new_id
from do_math.state_contract import StateContract
from research_fixtures import current_state


class RegisteredValidatorTests(unittest.TestCase):


    def test_registered_validator_enforces_current_rules(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            subprocess.run(['git', 'init', '--quiet', str(root)], check=True, capture_output=True)
            identifier = new_id('RI')
            before = ResearchRepository(root, identifier)
            head = before.initialize(*current_state({'sources': [
                {'id': 'SO-input', 'path': 'original.txt', 'sha256': 'a' * 64}]}))

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
                after.save_with_state(head, instance, runtime)[0]
            self.assertEqual(after.load()[1]['sources'][0]['path'], 'original.txt')


if __name__ == '__main__':
    unittest.main()
