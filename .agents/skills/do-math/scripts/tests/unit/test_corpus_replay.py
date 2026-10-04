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
    if 'turn_failed' in entry['verdict']:
        judged['turn_failed'] = parsed['turn_failed']
    if 'final_path' in entry:
        import hashlib
        final = (CORPUS / entry['final_path']).read_bytes()
        judged['final_sha256'] = hashlib.sha256(final).hexdigest()
        judged['final_is_selected_text'] = parsed.get('final_text', '').encode('utf-8') == final
    return judged


def _claude_stream(entry):
    from do_math.claude_stream import parse_stream
    parsed = parse_stream((CORPUS / entry['path']).read_bytes())
    return {'turn_completed': parsed['turn_completed'], 'turn_failed': parsed['turn_failed'],
            'parse_complete': parsed['parse_complete'], 'unknown_events': parsed['unknown_events'],
            'structured_output': parsed.get('structured_output'), 'reported_models': parsed['reported_models'],
            'result_segments': len(parsed['result_segments']), 'usage_segments': len(parsed['usage_segments']),
            'rate_limit_statuses': [row['info'].get('status') for row in parsed['rate_limits']],
            'background_event_types': [row['event']['subtype'] for row in parsed['background_events']],
            'post_result_event_types': [row['event']['subtype'] for row in parsed['post_result_events']]}


def _lean_output(entry):
    from do_math.lean_evidence import parse_evidence
    base = {'stdout': (CORPUS / entry['path']).read_text(encoding='utf-8'), 'declaration_signatures': {},
            'axioms': {}, 'dependency_closure': {}, 'declaration_evidence': {}}
    allowed = sorted({axiom for axioms in entry['verdict']['axioms'].values() for axiom in axioms})
    parsed = parse_evidence(base, entry['declarations'], allowed, extract_evidence=False)
    return {'status': parsed['status'], 'declaration_signatures': parsed['declaration_signatures'],
            'axioms': parsed['axioms']}


READERS = {'codex_stream': _codex_stream, 'claude_stream': _claude_stream, 'lean_output': _lean_output}


class CorpusReplayTests(unittest.TestCase):
    def test_every_entry_parses_to_its_recorded_judgment(self):
        entries = json.loads((CORPUS / 'manifest.json').read_text(encoding='utf-8'))['entries']
        for entry in entries:
            with self.subTest(entry=entry['id']):
                self.assertIn(entry['kind'], READERS, 'a corpus kind needs a reader')
                self.assertEqual(READERS[entry['kind']](entry), entry['verdict'])


if __name__ == '__main__':
    unittest.main()
