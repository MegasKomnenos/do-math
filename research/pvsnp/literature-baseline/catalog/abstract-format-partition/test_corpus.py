"""Exhaustive cross-check against source fields and the pre-existing availability inventory."""
import csv
from functools import lru_cache
import hashlib
import io
import json
from pathlib import Path
import unittest

import partition as p

FOLDER = Path(__file__).resolve().parent
BASE = p.BASE


@lru_cache(maxsize=None)
def original_export(relative, provider):
    text = (BASE / relative).read_text(encoding='utf-8-sig')
    if provider == 'scopus':
        csv.field_size_limit(max(len(text), csv.field_size_limit()))
        return [{'id': r['EID'], 'fields': {k.lower(): [v] for k, v in r.items()}}
                for r in csv.DictReader(io.StringIO(text, newline=''))]
    if provider in {'wos', 'pqdt'}:
        rows = p.export_parser.parse_ris(text, source_name=relative)
        return [{'id': p.export_parser._ris_occurrence(r, provider)['source_record_id'], 'fields': r['fields']} for r in rows]
    rows = p.export_parser.parse_bibtex_tolerant(text, source_name=relative)
    return [{'id': p.export_parser._bib_occurrence(r, provider)['source_record_id'], 'fields': r['fields']} for r in rows]


class CorpusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.input = p.read_jsonl(FOLDER / 'input.jsonl')
        cls.iterations = p.read_jsonl(FOLDER / 'iterations.jsonl')
        cls.abstracts = [r for step in cls.iterations
                         for r in p.read_jsonl(FOLDER / step['group'] / 'abstracts.jsonl')]

    def test_original_candidate_file_is_unchanged(self):
        self.assertEqual((BASE / 'catalog/paper-summary-candidates.jsonl').read_bytes(),
                         (FOLDER / 'input.jsonl').read_bytes())

    def test_availability_agrees_with_existing_independent_inventory(self):
        reference = p.read_jsonl(BASE / 'catalog/abstract-inventory.jsonl')
        self.assertEqual({r['paper_id'] for r in reference}, {r['paper_id'] for r in self.input})
        expected = {r['paper_id'] for r in reference if r['status'] == 'found'}
        actual = {r['paper_id'] for r in self.abstracts}
        self.assertEqual(actual, expected)

    def test_every_abstract_equals_its_identified_original_field(self):
        for abstract in self.abstracts:
            with self.subTest(paper_id=abstract['paper_id']):
                source = abstract['source']
                locator = source['locator']
                family = source['family']
                if family in {'scopus-csv', 'bibtex', 'ris', 'mathscinet-bibtex'}:
                    rows = original_export(locator['path'], locator['source_id'])
                    row = rows[locator['rank'] - 1]
                    self.assertEqual(row['id'].casefold(), source['source_record_id'].casefold())
                    self.assertIn(abstract['text'], [v.strip() for v in row['fields'][abstract['field']]])
                elif family == 'crossref-json':
                    envelope = json.loads((BASE / locator['path']).read_text(encoding='utf-8-sig'))
                    payload = json.loads(envelope['response_text']) if 'response_text' in envelope else envelope
                    message = payload.get('message', payload)
                    self.assertEqual(message['DOI'].lower(), source['source_record_id'].lower())
                    self.assertEqual(message['abstract'].strip(), abstract['text'])
                elif family == 'captured-page':
                    envelope = json.loads((BASE / locator['path']).read_text(encoding='utf-8-sig'))
                    self.assertEqual(envelope['paper_id'], abstract['paper_id'])
                    self.assertEqual(envelope['abstract'], abstract['text'])
                else:
                    self.fail('Unreviewed output family: ' + family)
                self.assertEqual(hashlib.sha256(abstract['text'].encode()).hexdigest(), abstract['text_sha256'])

    def test_all_original_records_are_preserved_once(self):
        members = [r for step in self.iterations for r in p.read_jsonl(FOLDER / step['group'] / 'members.jsonl')]
        self.assertEqual(len(members), len(self.input))
        self.assertEqual(len({r['paper_id'] for r in members}), len(self.input))
        self.assertEqual(sorted(members, key=lambda r: r['paper_id']), sorted(self.input, key=lambda r: r['paper_id']))
        self.assertEqual((FOLDER / 'remaining.jsonl').read_bytes(), b'')

    def test_all_candidates_were_observed_and_group_recognition_has_no_errors(self):
        observations = p.read_jsonl(FOLDER / 'observations.jsonl')
        self.assertEqual({r['paper_id'] for r in observations}, {r['paper_id'] for r in self.input})
        report = p.verify_partition(FOLDER)
        self.assertTrue(report['passed'], report)


if __name__ == '__main__':
    unittest.main()
