"""Recorded-output replay (의무 9-B, 설계 4.5): every corpus entry, parsed by the product's layer-1 parser, gives
the judgment recorded with it.

``READERS`` maps each corpus kind to how its entry is parsed and which part of
the result is the judgment. A new kind of recording adds one reader here and
its entries to ``tests/corpus/manifest.json``; an entry of a kind with no
reader fails the walk.
"""
import json
from pathlib import Path
import unittest

CORPUS = Path(__file__).resolve().parents[1] / 'corpus'


def _codex_stream(entry):
    from do_math.codex_stream import parse_jsonl
    parsed = parse_jsonl((CORPUS / entry['path']).read_bytes())
    judged = {'turn_completed': parsed['turn_completed'], 'parse_complete': parsed['parse_complete'],
              'usage_fields': sorted(parsed['usage'][0]) if parsed['usage'] else [],
              'unknown_events': [row['kind'] for row in parsed['unknown_events']]}
    if 'final_path' in entry:
        import hashlib
        final = (CORPUS / entry['final_path']).read_bytes()
        judged['final_sha256'] = hashlib.sha256(final).hexdigest()
        judged['final_is_selected_text'] = parsed.get('final_text', '').encode('utf-8') == final
    return judged


def _lean_output(entry):
    from do_math.lean_evidence import parse_evidence
    base = {'stdout': (CORPUS / entry['path']).read_text(encoding='utf-8'), 'declaration_signatures': {},
            'axioms': {}, 'dependency_closure': {}, 'declaration_evidence': {}}
    allowed = sorted({axiom for axioms in entry['verdict']['axioms'].values() for axiom in axioms})
    parsed = parse_evidence(base, entry['declarations'], allowed, extract_evidence=False)
    return {'status': parsed['status'], 'declaration_signatures': parsed['declaration_signatures'],
            'axioms': parsed['axioms']}


READERS = {'codex_stream': _codex_stream, 'lean_output': _lean_output}


class CorpusReplayTests(unittest.TestCase):
    def test_every_entry_parses_to_its_recorded_judgment(self):
        entries = json.loads((CORPUS / 'manifest.json').read_text(encoding='utf-8'))['entries']
        for entry in entries:
            with self.subTest(entry=entry['id']):
                self.assertIn(entry['kind'], READERS, 'a corpus kind needs a reader')
                self.assertEqual(READERS[entry['kind']](entry), entry['verdict'])


if __name__ == '__main__':
    unittest.main()
