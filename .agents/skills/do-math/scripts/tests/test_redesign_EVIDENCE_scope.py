"""Scope-source/artifact binding tests; synthetic files are not product evidence."""
import hashlib
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import check_coverage


class ScopeArtifactTests(unittest.TestCase):
    def test_scope_artifacts_bind_source_bytes_and_never_supply_a_test_pass(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / 'adopted.txt'
            source.write_bytes(b'Exact counter if available; otherwise documented bytes.')
            trace = {'scope_artifacts': {'U31': {'path': 'adopted.txt',
                'sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
                'scope': 'Fixture for adopted measurement units',
                'boundary': 'Source binding only; not an execution result'}},
                'vectors': {'V214': {'adopted_scope': {'source_refs': ['U31'],
                    'retained_effects': 'Measure the actual final input.',
                    'changed_or_conditional': 'Token counter is conditional.'}}}}
            self.assertEqual(check_coverage.scope_artifact_errors(trace, root), [])
            source.write_bytes(b'A different contract')
            self.assertTrue(any('scope artifact bytes differ' in e
                for e in check_coverage.scope_artifact_errors(trace, root)))
            source.write_bytes(b'Exact counter if available; otherwise documented bytes.')
            trace['vectors']['V214']['adopted_scope']['source_refs'] = ['absent']
            self.assertTrue(any('unknown scope source' in e
                for e in check_coverage.scope_artifact_errors(trace, root)))
            trace['vectors']['V214']['adopted_scope']['source_refs'] = ['U31']
            trace['scope_artifacts']['U31']['path'] = '../outside'
            self.assertTrue(any('scope artifact unavailable' in e
                for e in check_coverage.scope_artifact_errors(trace, root)))


if __name__ == '__main__':
    unittest.main(verbosity=2)
