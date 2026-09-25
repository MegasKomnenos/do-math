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
    def test_large_manifest_rechecks_every_file_and_keeps_ordered_findings(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            request = trust_fixture(root, ['lean'])
            environment = {key: value for key, value in request.items() if key != 'operation'}
            files = environment['manifest']['files']
            for i in range(40):
                path = root / f'module-{i}'
                path.write_bytes(b'original')
                files.append({'role':'mathlib_build', 'path':str(path.resolve()),
                              'sha256':hashlib.sha256(b'original').hexdigest()})
            environment.update(source_ref='test', manifest_sha256=digest(environment['manifest']))
            self.assertEqual(trust_environment_errors(environment), [])
            changed, missing = files[-2]['path'], files[-1]['path']
            Path(changed).write_bytes(b'changed')
            Path(missing).unlink()
            files.append(dict(files[0]))
            files.append({'role':'checker','path':'relative','sha256':'0'*64})
            environment['manifest_sha256'] = digest(environment['manifest'])
            # A malformed manifest fails before any live observation.
            self.assertEqual(trust_environment_errors(environment), [
                'duplicate manifest path', 'manifest file must have an absolute path'])
            self.assertEqual(trust_environment_errors(environment, verify_files=False), [
                'duplicate manifest path', 'manifest file must have an absolute path'])
            del files[-2:]
            environment['manifest_sha256'] = digest(environment['manifest'])
            self.assertEqual(trust_environment_errors(environment), [
                'trust file changed: ' + changed, 'trust file unavailable: ' + missing])

    def test_structure_never_resolves_host_paths_and_live_hashing_streams(self):
        from do_math.trust_validation import verify_environment_files
        with tempfile.TemporaryDirectory() as directory:
            request = trust_fixture(Path(directory), ['lean'])
            environment = {key:value for key,value in request.items() if key != 'operation'}
            environment.update(source_ref='test', manifest_sha256=digest(request['manifest']))
            with patch.object(Path, 'resolve', side_effect=AssertionError('host access')):
                self.assertEqual(trust_environment_errors(environment, verify_files=False), [])
            with patch.object(Path, 'read_bytes', side_effect=AssertionError('whole file read')):
                result = verify_environment_files(environment, workers=2)
            self.assertEqual(result['status'], 'verified')
            self.assertLessEqual(result['peak_pending'], 4)
            self.assertEqual(result['completed_files'], 6)
            stopped = verify_environment_files(environment, should_stop=lambda:True)
            self.assertEqual(stopped['status'], 'cancelled')
            self.assertEqual(stopped['read_bytes'], 0)

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
