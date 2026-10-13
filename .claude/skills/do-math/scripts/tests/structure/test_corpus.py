"""Corpus kind completeness (설계 3.3, 4.5): every recorded entry is declared whole and the corpus stays small."""
import json
import hashlib
from pathlib import Path
import unittest

CORPUS = Path(__file__).resolve().parents[1] / 'corpus'
LIMIT_BYTES = 5 * 1024 * 1024  # it ships inside the skill and its Codex copy
FIELDS = {'id', 'kind', 'path', 'tool_version', 'recorded_at', 'command', 'role', 'source', 'verdict'}
FILE_FIELDS = ('path', 'final_path', 'source_path', 'compiled_path')


class CorpusCompletenessTests(unittest.TestCase):
    def test_each_provider_has_a_versioned_real_stream(self):
        from do_math.claude_adapter import ADAPTERS
        manifest = json.loads((CORPUS / 'manifest.json').read_text(encoding='utf-8'))
        versions = manifest['supported_stream_versions']
        self.assertEqual(set(versions), set(ADAPTERS))
        for provider, version in versions.items():
            with self.subTest(provider=provider):
                self.assertTrue(version.strip())
                entries = [entry for entry in manifest['entries']
                           if entry['kind'] == provider + '_stream' and entry['tool_version'] == version]
                self.assertTrue(entries, 'each current provider version needs a real recording')
                for entry in entries:
                    self.assertEqual(hashlib.sha256((CORPUS / entry['path']).read_bytes()).hexdigest(),
                                     entry['source_sha256'], 'recorded bytes must match their source')

    def test_every_entry_has_its_fields_and_files_and_no_file_is_undeclared(self):
        entries = json.loads((CORPUS / 'manifest.json').read_text(encoding='utf-8'))['entries']
        self.assertGreater(len(entries), 0)
        self.assertTrue({'lean_output', 'scholarly_config', 'scheduler_json', 'cli_surface'}
                        <= {entry['kind'] for entry in entries},
                        'the recorded non-provider boundaries must not disappear from the manifest')
        self.assertEqual(len({entry['id'] for entry in entries}), len(entries), 'entry IDs must be distinct')
        declared = set()
        for entry in entries:
            with self.subTest(entry=entry.get('id')):
                self.assertEqual(FIELDS - entry.keys(), set())
                for field in FILE_FIELDS:
                    if field in entry:
                        self.assertTrue((CORPUS / entry[field]).is_file(), entry[field])
                        declared.add(entry[field])
                if 'source_sha256' in entry:
                    self.assertEqual(hashlib.sha256((CORPUS / entry['path']).read_bytes()).hexdigest(),
                                     entry['source_sha256'], 'historical and current source bytes must be preserved')
                for recording in entry.get('recordings', []):
                    path = CORPUS / recording['path']
                    self.assertTrue(path.is_file(), recording['path'])
                    self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), recording['sha256'])
                    declared.add(recording['path'])
                if entry['role'] == 'maintenance':
                    self.assertIn(entry['schema_path'], declared)
                    self.assertEqual(hashlib.sha256((CORPUS / entry['schema_path']).read_bytes()).hexdigest(),
                                     entry['schema_sha256'])
                    self.assertIsInstance(entry['live_passed'], bool)
                    if 'transport_schema_path' in entry:
                        self.assertIn(entry['transport_schema_path'], declared)
                        self.assertIn(entry['worker_status_path'], declared)
                        self.assertEqual(hashlib.sha256((CORPUS / entry['transport_schema_path']).read_bytes()).hexdigest(),
                                         entry['transport_schema_sha256'])
        present = {path.relative_to(CORPUS).as_posix() for path in CORPUS.rglob('*') if path.is_file()} - {'manifest.json', '.gitattributes'}
        self.assertEqual(present - declared, set(), 'corpus files the manifest does not declare')
        self.assertLessEqual(sum((CORPUS / path).stat().st_size for path in present), LIMIT_BYTES)


if __name__ == '__main__':
    unittest.main()
