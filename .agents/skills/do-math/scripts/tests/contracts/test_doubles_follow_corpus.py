"""The model and Lean doubles against recorded real output (설계 4.2, 4.5; 과정 결함 P7).

A double answers what its author knew; the corpus holds what the real tool
wrote. The product's own parsers judge both, and the judgments must agree, so
a double that drifts from the real output shape fails here before it hides a
receiving defect.
"""
import json
from pathlib import Path
import tempfile
import unittest

from do_math.codex_stream import parse_jsonl
from do_math.lean_evidence import check_file, parse_evidence
from support.lean import LeanDouble
from support.model import codex_stream_bytes

CORPUS = Path(__file__).resolve().parents[1] / 'corpus'
ENTRIES = {entry['id']: entry for entry in json.loads((CORPUS / 'manifest.json').read_text(encoding='utf-8'))['entries']}


class ModelDoubleStreamTests(unittest.TestCase):
    def test_the_codex_stream_is_judged_like_a_recorded_completed_stream(self):
        recorded = ENTRIES['codex-operational-review-completed']
        final = '{"summary": "fixture"}'
        parsed = parse_jsonl(codex_stream_bytes(final))
        self.assertEqual({'turn_completed': parsed['turn_completed'], 'parse_complete': parsed['parse_complete'],
                          'usage_fields': sorted(parsed['usage'][0]),
                          'unknown_events': [row['kind'] for row in parsed['unknown_events']]},
                         {key: recorded['verdict'][key] for key in
                          ('turn_completed', 'parse_complete', 'usage_fields', 'unknown_events')})
        self.assertEqual(parsed['final_text'], final)


class LeanDoubleOutputTests(unittest.TestCase):
    def run_check(self, lean, source, declarations, *, extract_evidence):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            check = root / 'proposal.lean'
            check.write_bytes(check_file(source.encode(), declarations, extract_evidence=extract_evidence))
            out, err = root / 'out', root / 'err'
            with open(out, 'wb') as stdout, open(err, 'wb') as stderr:
                with lean.spawn(['lean', str(check)], cwd=str(root), stdout=stdout, stderr=stderr) as process:
                    code = process.wait()
            return code, out.read_text(encoding='utf-8'), err.read_text(encoding='utf-8')

    def test_declared_facts_reproduce_the_recorded_signature_and_axiom_lines(self):
        recorded = ENTRIES['lean-nat-add-zero-beq']
        verdict = recorded['verdict']
        lean = LeanDouble()
        source = (CORPUS / recorded['source_path']).read_text(encoding='utf-8')
        lean.allow(source, recorded['declarations'], signatures=verdict['declaration_signatures'],
                   axioms=verdict['axioms'])
        code, stdout, _ = self.run_check(lean, source, recorded['declarations'], extract_evidence=False)
        self.assertEqual(code, 0)
        self.assertEqual(stdout, (CORPUS / recorded['path']).read_text(encoding='utf-8'))

    def test_only_the_default_producer_source_verifies_with_evidence_by_default(self):
        source = 'theorem t : True := by trivial'
        code, stdout, _ = self.run_check(LeanDouble(), source, ['t'], extract_evidence=True)
        self.assertEqual(code, 0)
        base = {'stdout': stdout, 'declaration_signatures': {}, 'axioms': {}, 'dependency_closure': {},
                'declaration_evidence': {}}
        result = parse_evidence(base, ['t'], [], extract_evidence=True)
        self.assertEqual((result['status'], result['declaration_signatures']), ('verified', {'t': 't : True'}))

    def test_a_declaration_the_source_does_not_define_fails_like_lean(self):
        code, _, stderr = self.run_check(LeanDouble(), 'theorem t : True := by trivial', ['missing'],
                                         extract_evidence=False)
        self.assertEqual(code, 1)
        self.assertIn('unregistered synthetic Lean source/declarations', stderr)

    def test_a_changed_body_or_declaration_set_has_no_implicit_success(self):
        for source, names in (
                ('theorem t : True := by invalid_proof', ['t']),
                ('theorem other : True := by trivial', ['other']),
                ('theorem t : True := by trivial\n', ['t']),
                ('theorem t : True := by trivial', ['t', 't'])):
            with self.subTest(source=source, declarations=names):
                lean = LeanDouble()
                code, stdout, stderr = self.run_check(lean, source, names, extract_evidence=True)
                self.assertEqual((code, stdout), (1, ''))
                self.assertIn('unregistered synthetic Lean source/declarations', stderr)
                self.assertEqual(lean.checks[-1]['registered'], False)

    def test_explicit_facts_still_pass_through_signature_and_forbidden_axiom_checks(self):
        source = 'axiom explicit : False'
        lean = LeanDouble().allow(source, ['explicit'], signatures={'explicit': 'explicit : False'},
                                  axioms={'explicit': ['sorryAx']})
        code, stdout, _ = self.run_check(lean, source, ['explicit'], extract_evidence=True)
        self.assertEqual(code, 0)
        result = parse_evidence({'stdout': stdout}, ['explicit'], ['sorryAx'], extract_evidence=True)
        self.assertEqual((result['status'], result['reason']), ('rejected', 'forbidden axiom'))
        code, _, error = self.run_check(lean, source + '\n-- changed', ['explicit'], extract_evidence=True)
        self.assertEqual(code, 1)
        self.assertIn('unregistered synthetic Lean source/declarations', error)


if __name__ == '__main__':
    unittest.main()
