"""The two default fixture sources retain the current installed Lean's complete evidence."""
from pathlib import Path
import tempfile
import unittest

from do_math import lean_evidence
from do_math.canonical import exact_content_hash
from do_math.formal import _job_run
from do_math.wiring import real_ports
from support.entry import entry
from support.lean_preservation import recorded_defaults
from support.provider_inputs import actual_command
from test_categories import test_group


class LeanDefaultFactsTests(unittest.TestCase):
    @test_group('lean')
    def test_default_registration_matches_current_compiler_evidence(self):
        owner = entry()
        ports = real_ports(environment=owner.environment)
        for name, facts in recorded_defaults().items():
            with self.subTest(declaration=name), tempfile.TemporaryDirectory() as directory:
                workspace = Path(directory)
                check = workspace / 'proposal.lean'
                check.write_bytes(lean_evidence.check_file(facts['source'].encode(), [name], extract_evidence=True))
                code, stdout, stderr, stopped = _job_run([*actual_command(), str(check)], workspace,
                    jobs=ports.jobs, clock=ports.clock, environment=owner.environment)
                self.assertEqual((code, stderr, stopped), (0, '', False))
                result = lean_evidence.parse_evidence({'stdout': stdout, 'dependency_closure': {},
                    'declaration_evidence': {}}, [name], [])
                self.assertEqual((result['status'], result['reason']), ('verified', None))
                self.assertEqual(result['declaration_signatures'], facts['signatures'])
                self.assertEqual(result['declaration_evidence'], facts['declaration_evidence'])
                self.assertEqual(result['axioms'], facts['axioms'])
                dependencies = facts['dependencies'][name]
                self.assertEqual(result['dependency_closure'], {name: sorted(dependencies)})
                self.assertEqual(result['dependency_evidence'],
                    {key: exact_content_hash(value) for key, value in dependencies.items()})
