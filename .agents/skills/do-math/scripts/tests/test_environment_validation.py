"""Cached environments need real validation evidence, not a build-method label."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import setup_lean
from do_math.initialization import digest, trust_environment_errors
from research_fixtures import trust_fixture
from test_categories import test_group


@test_group('unit')
class EnvironmentValidationTests(unittest.TestCase):
    def test_cached_environment_requires_evidence_and_unchanged_files(self):
        with tempfile.TemporaryDirectory() as directory:
            request = trust_fixture(Path(directory), ['lean'])
            environment = {key: value for key, value in request.items() if key != 'operation'}
            environment.update(source_ref='explicit-test-adoption', manifest_sha256=digest(request['manifest']))
            self.assertEqual(trust_environment_errors(environment), [])
            entry = environment['manifest']['files'][-1]
            Path(entry['path']).write_bytes(b'changed checker')
            self.assertTrue(any('trust file changed' in error for error in trust_environment_errors(environment)))
            environment['manifest']['validation']['evidence_refs'] = []
            environment['manifest_sha256'] = digest(environment['manifest'])
            self.assertIn('trust validation evidence absent', trust_environment_errors(environment))

    def test_unknown_manifest_field_is_not_silently_ignored(self):
        with tempfile.TemporaryDirectory() as directory:
            request = trust_fixture(Path(directory), ['lean'])
            environment = {key: value for key, value in request.items() if key != 'operation'}
            environment['manifest']['unrecognized'] = True
            environment.update(source_ref='test', manifest_sha256=digest(environment['manifest']))
            self.assertIn('trust manifest fields differ from the current contract', trust_environment_errors(environment))

    def test_validation_preserves_source_output_and_exact_toolchain(self):
        with tempfile.TemporaryDirectory() as directory:
            chain = {'identity': 'synthetic test environment'}
            with patch.object(setup_lean, 'inspect_toolchain', return_value=chain), \
                    patch.object(setup_lean.subprocess, 'run', return_value=subprocess.CompletedProcess([], 0, 'ok', '')) as run:
                result = setup_lean.verify_environment(['test-lean'], Path(directory))
            self.assertEqual(result['status'], 'verified')
            record = json.loads(Path(result['validation']['evidence_refs'][0]).read_text(encoding='utf-8'))
            self.assertEqual(record['scope'], 'mathlib_import_and_representative_proofs')
            self.assertEqual(record['command'], run.call_args.args[0])
            self.assertEqual(record['stdout'], 'ok')
            self.assertEqual(record['toolchain_after'], chain)
            self.assertEqual(record['source_sha256'], hashlib.sha256(Path(record['source']).read_bytes()).hexdigest())

    def test_failure_and_toolchain_change_never_produce_verified_evidence(self):
        for exit_code, after in [(1, 'before'), (0, 'changed')]:
            with self.subTest(exit_code=exit_code, after=after), tempfile.TemporaryDirectory() as directory:
                with patch.object(setup_lean, 'inspect_toolchain', side_effect=['before', after]), \
                        patch.object(setup_lean.subprocess, 'run', return_value=subprocess.CompletedProcess([], exit_code, '', 'diagnostic')):
                    result = setup_lean.verify_environment(['test-lean'], Path(directory))
                self.assertEqual(result['status'], 'failed')
                record = json.loads(Path(result['validation']['evidence_refs'][0]).read_text(encoding='utf-8'))
                self.assertEqual(record['stderr'], 'diagnostic')
