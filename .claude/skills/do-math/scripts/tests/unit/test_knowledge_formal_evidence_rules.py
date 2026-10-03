"""Lean evidence rules (``lean_evidence``, layer 1) and the trust-registration contract on a recorded toolchain
(``trust_validation``, layer 2)."""
from pathlib import Path
from copy import deepcopy
from io import BytesIO
import json
import tempfile
import unittest

from do_math.lean_evidence import check_file, compare_formal_results, is_lean_identifier, parse_evidence
from support.lean import LeanDouble
from do_math.trust_validation import environment_errors, register_request_errors
from support.trust_inputs import trust_environment, trust_fixture


class LeanEvidenceRuleTests(unittest.TestCase):
    def test_declaration_value_must_follow_the_compiler_string_or_null_contract(self):
        source, name = 'theorem evidence_shape : True := True.intro', 'evidence_shape'
        lean = LeanDouble().allow(source, [name], signatures={name: name + ' : True'},
            dependencies={name: {'True': {'type': 'Prop', 'value': None}}})
        with tempfile.TemporaryDirectory() as directory:
            check = Path(directory) / 'proposal.lean'
            check.write_bytes(check_file(source.encode(), [name], extract_evidence=True))
            stdout, stderr = BytesIO(), BytesIO()
            with lean.spawn(['synthetic-lean', str(check)], stdout=stdout, stderr=stderr) as process:
                self.assertEqual(process.wait(), 0)
            self.assertEqual(stderr.getvalue(), b'')
        output = stdout.getvalue().decode('utf-8')
        prefix = '__DO_MATH_DEPENDENCIES__'
        lines = output.splitlines(keepends=True)
        index = next(i for i, line in enumerate(lines) if line.startswith(prefix))
        declaration = json.loads(lines[index][len(prefix):])
        for value in (None, 'True.intro', [], {}, True, 1):
            with self.subTest(value=value):
                row = deepcopy(declaration)
                row['evidence']['value'] = value
                changed = list(lines)
                changed[index] = prefix + json.dumps(row) + '\n'
                base = {'stdout': ''.join(changed), 'stderr': '',
                        'dependency_closure': {}, 'declaration_evidence': {}}
                result = parse_evidence(base, [name], [])
                if value is None or isinstance(value, str):
                    self.assertEqual((result['status'], result['reason']), ('verified', None))
                    self.assertEqual(result['declaration_evidence'], {name: {'type': 'True', 'value': value}})
                else:
                    self.assertEqual((result['status'], result['reason']),
                                     ('failed', 'malformed dependency evidence'))

    def test_results_without_dependencies_compare_as_equivalent(self):
        result = {'axioms': {'x': []}, 'dependency_closure': {'x': []}, 'dependency_evidence': {},
                  'declaration_evidence': {'x': {'type': 'Prop', 'value': None}}}
        self.assertTrue(compare_formal_results(result, dict(result))['equivalent'])

    def test_prime_names_keep_the_existing_identifier_boundary(self):
        for value in ("sumTo_succ'", "N.foo''", "α'", "N'.foo'"):
            self.assertTrue(is_lean_identifier(value), value)
        for value in ("'", "N.'", "x'; #eval 1", "x' y", "x\ny", "x'y", 'x"', "x()", ".x", "x."):
            self.assertFalse(is_lean_identifier(value), value)


class ToolchainRegistrationTests(unittest.TestCase):
    def test_registration_rejects_the_incomplete_document_toolchain(self):
        with tempfile.TemporaryDirectory() as directory:
            request = trust_fixture(Path(directory), ['test-lean'])
            environment, binding = trust_environment(request, source_ref='UC-adopt')
            self.assertEqual(environment_errors(environment, binding), [])
            del environment['toolchain']['verifier_sha256']
            del request['toolchain']['verifier_sha256']
            errors = environment_errors(environment, binding)
            self.assertIn('toolchain.verifier_sha256 is missing', register_request_errors(request))
        self.assertTrue(any('verifier_sha256' in error for error in errors), errors)


if __name__ == '__main__':
    unittest.main()
