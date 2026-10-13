"""The model and Lean doubles against recorded real output (설계 4.2, 4.5; 과정 결함 P7).

A double answers what its author knew; the corpus holds what the real tool
wrote. The product's own parsers judge both, and the judgments must agree, so
a double that drifts from the real output shape fails here before it hides a
receiving defect.
"""
import json
import io
from pathlib import Path
import tempfile
import unittest

from do_math.codex_stream import parse_jsonl
from do_math.canonical import exact_content_hash
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

    def test_current_maintenance_outputs_match_the_provider_doubles_at_the_real_parser(self):
        from do_math.claude_stream import parse_stream
        from do_math.provider_final import final_bytes, semantic_output
        from support.model import raw, ModelDouble
        from support.provider_claude_model import ClaudeModelDouble
        recordings = [entry for entry in ENTRIES.values() if entry['role'] == 'maintenance']
        self.assertTrue(recordings)
        for entry in recordings:
            with self.subTest(entry=entry['id']):
                parser = parse_jsonl if entry['kind'] == 'codex_stream' else parse_stream
                recorded = parser((CORPUS / entry['path']).read_bytes())
                if recorded['turn_failed']:
                    # The normal double must not make an admission rejection look successful.
                    self.assertFalse(entry['live_passed'])
                    self.assertIsNone(final_bytes(recorded))
                    self.assertNotEqual(recorded['turn_completed'], parse_jsonl(codex_stream_bytes('{}'))['turn_completed'])
                    continue
                provider = entry['kind'].removesuffix('_stream')
                output = semantic_output(provider, final_bytes(recorded))
                if entry['kind'] == 'codex_stream':
                    stdout = io.BytesIO()
                    with tempfile.TemporaryDirectory() as directory:
                        model = ModelDouble(clock=None)
                        cli = model.spawn(['codex', '--output-schema', str(CORPUS / entry['transport_schema_path']),
                            '--output-last-message', str(Path(directory) / 'final.txt')], stdout=stdout, cwd=directory)
                        cli.finish(output, raw(output, mode='standalone', expected_receipt=None))
                        doubled = parse_jsonl(stdout.getvalue())
                        self.assertEqual(final_bytes(doubled), (Path(directory) / 'final.txt').read_bytes())
                else:
                    stdout = io.BytesIO()
                    model = ClaudeModelDouble(clock=None)
                    cli = model.spawn(['claude', '--print', '--json-schema', '{}'], stdout=stdout, cwd=CORPUS)
                    cli.finish(output, raw(output, mode='standalone', expected_receipt=None))
                    doubled = parse_stream(stdout.getvalue())
                self.assertEqual({key: doubled[key] for key in ('turn_completed', 'turn_failed', 'parse_complete')},
                                 {key: recorded[key] for key in ('turn_completed', 'turn_failed', 'parse_complete')})
                self.assertEqual(semantic_output(provider, final_bytes(doubled)), output)


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
                   axioms=verdict['axioms'], declaration_evidence=None, dependencies=None)
        code, stdout, _ = self.run_check(lean, source, recorded['declarations'], extract_evidence=False)
        self.assertEqual(code, 0)
        self.assertEqual(stdout, (CORPUS / recorded['path']).read_text(encoding='utf-8'))
        code, _, stderr = self.run_check(lean, source, recorded['declarations'], extract_evidence=True)
        self.assertEqual(code, 1)
        self.assertIn('unregistered synthetic Lean source/declarations', stderr)

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
                                  axioms={'explicit': ['sorryAx']}, dependencies={'explicit': {}},
                                  declaration_evidence={'explicit': {'type': 'False', 'value': None}})
        code, stdout, _ = self.run_check(lean, source, ['explicit'], extract_evidence=True)
        self.assertEqual(code, 0)
        result = parse_evidence({'stdout': stdout}, ['explicit'], ['sorryAx'], extract_evidence=True)
        self.assertEqual((result['status'], result['reason']), ('rejected', 'forbidden axiom'))
        code, _, error = self.run_check(lean, source + '\n-- changed', ['explicit'], extract_evidence=True)
        self.assertEqual(code, 1)
        self.assertIn('unregistered synthetic Lean source/declarations', error)

    def test_explicit_binder_type_value_and_shared_bodies_survive_the_parser(self):
        # Deliberately synthetic facts, independently supplied: no source/binder parser.
        source, names = '-- explicitly registered compiler output', ['first', 'second']
        signatures = {name: name + ' (n : Nat) : n = n' for name in names}
        evidence = {name: {'type': '(n : Nat) -> n = n', 'value': 'fun n => Eq.refl n'} for name in names}
        dependencies = {name: {'Nat': {'type': 'Type', 'value': None},
                               'Eq.refl': {'type': 'synthetic dependent type', 'value': None}} for name in names}
        lean = LeanDouble().allow(source, names, signatures=signatures, declaration_evidence=evidence,
                                  axioms={name: [] for name in names}, dependencies=dependencies)
        evidence['first']['value'] = 'caller mutation must not change the registration'
        code, stdout, _ = self.run_check(lean, source, names, extract_evidence=True)
        self.assertEqual(code, 0)
        self.assertEqual(stdout.count('__DO_MATH_DEPENDENCY__'), 2)
        result = parse_evidence({'stdout': stdout, 'dependency_closure': {}, 'declaration_evidence': {}}, names, [])
        self.assertEqual(result['status'], 'verified')
        self.assertEqual(result['declaration_evidence'],
                         {name: {'type': '(n : Nat) -> n = n', 'value': 'fun n => Eq.refl n'} for name in names})
        self.assertEqual(result['declaration_signatures'], signatures)
        self.assertEqual(result['signature_hash'], exact_content_hash(signatures))
        self.assertEqual(result['dependency_closure'], {name: ['Eq.refl', 'Nat'] for name in names})
        self.assertEqual(result['dependency_evidence'],
                         {name: exact_content_hash(body) for name, body in dependencies['first'].items()})

    def test_missing_or_conflicting_facts_are_not_silently_filled(self):
        source, names = '-- explicit', ['one', 'two']
        facts = dict(signatures={name: name + ' : True' for name in names},
                     declaration_evidence={name: {'type': 'True', 'value': 'True.intro'} for name in names},
                     axioms={name: [] for name in names}, dependencies={name: {} for name in names})
        for field in facts:
            missing = {key: value for key, value in facts.items() if key != field}
            with self.subTest(field=field), self.assertRaisesRegex(
                    TypeError, "^LeanDouble.allow\\(\\) missing 1 required keyword-only argument: '" + field + "'$" ):
                LeanDouble().allow(source, names, **missing)
            with self.subTest(incomplete=field), self.assertRaisesRegex(ValueError, 'cover exactly'):
                LeanDouble().allow(source, names, **{**facts, field: {}})
        conflicting = {'one': {'True': {'type': 'Prop', 'value': None}},
                       'two': {'True': {'type': 'different', 'value': None}}}
        with self.assertRaisesRegex(ValueError, 'conflicting dependency evidence: True'):
            LeanDouble().allow(source, names, **{**facts, 'dependencies': conflicting})

    def test_preview_registration_removes_previous_extraction_permission(self):
        source = 'theorem t : True := by trivial'
        lean = LeanDouble().allow(source, ['t'], signatures={'t': 't : True'}, axioms={'t': []},
                                  declaration_evidence=None, dependencies=None)
        self.assertEqual(self.run_check(lean, source, ['t'], extract_evidence=False)[0], 0)
        self.assertEqual(self.run_check(lean, source, ['t'], extract_evidence=True)[0], 1)


if __name__ == '__main__':
    unittest.main()
