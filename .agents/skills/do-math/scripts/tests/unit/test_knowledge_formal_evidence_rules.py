"""Lean evidence rules (``lean_evidence``, layer 1) and the trust-registration contract on a recorded toolchain
(``trust_validation``, layer 2)."""
from pathlib import Path
import tempfile
import unittest

from do_math.lean_evidence import compare_formal_results, is_lean_identifier
from do_math.trust_validation import environment_errors, register_request_errors
from research_fixtures import trust_environment, trust_fixture


class LeanEvidenceRuleTests(unittest.TestCase):
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
