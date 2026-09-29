"""Corpus kind completeness (설계 3.3, 4.5): every recorded entry is declared whole and the corpus stays small."""
import json
from pathlib import Path
import unittest

CORPUS = Path(__file__).resolve().parents[1] / 'corpus'
LIMIT_BYTES = 5 * 1024 * 1024  # it ships inside the skill and its Codex copy
FIELDS = {'id', 'kind', 'path', 'tool_version', 'recorded_at', 'command', 'role', 'source', 'verdict'}
FILE_FIELDS = ('path', 'final_path', 'source_path')


class CorpusCompletenessTests(unittest.TestCase):
    def test_every_entry_has_its_fields_and_files_and_no_file_is_undeclared(self):
        entries = json.loads((CORPUS / 'manifest.json').read_text(encoding='utf-8'))['entries']
        self.assertGreater(len(entries), 0)
        self.assertEqual(len({entry['id'] for entry in entries}), len(entries), 'entry IDs must be distinct')
        declared = set()
        for entry in entries:
            with self.subTest(entry=entry.get('id')):
                self.assertEqual(FIELDS - entry.keys(), set())
                for field in FILE_FIELDS:
                    if field in entry:
                        self.assertTrue((CORPUS / entry[field]).is_file(), entry[field])
                        declared.add(entry[field])
        present = {path.relative_to(CORPUS).as_posix() for path in CORPUS.rglob('*') if path.is_file()} - {'manifest.json'}
        self.assertEqual(present - declared, set(), 'corpus files the manifest does not declare')
        self.assertLessEqual(sum((CORPUS / path).stat().st_size for path in present), LIMIT_BYTES)


if __name__ == '__main__':
    unittest.main()
