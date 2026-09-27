"""The producer's standalone compiler command gives feedback, never authority."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from provider_fixtures import actual_command
from test_categories import test_group as category
from do_math.submission import install_tools
from do_math.contracts import schema_for


class LeanPreviewTests(unittest.TestCase):
    def test_control_stop_is_consumed_before_any_compiler_start(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            context = {"action": {"role": "research_work"}, "snapshot": "fixed",
                "formal_verifier": {"command": ["definitely-missing-lean"], "allowed_axioms": []}}
            install_tools(workspace, context, schema_for('research_work'), 1000000)
            (workspace / 'draft.lean').write_text('theorem good : True := by trivial', encoding='utf-8')
            (workspace / '.control').mkdir()
            (workspace / '.control/stop-request.json').write_text('{}', encoding='utf-8')
            preview = context['formal_verifier']['preview']
            result = subprocess.run([*preview['command'], '--source', 'draft.lean', '--declaration', 'good'],
                cwd=workspace, capture_output=True, text=True, encoding='utf-8', timeout=30)
            self.assertEqual('stopped', json.loads(result.stdout)['status'])

    def test_preview_checker_loaded_from_the_support_archive_is_the_approved_checker(self):
        """The worker loads formal.py from a zip, so its path is never the approved path;
        the same bytes are the same checker and pass the identity gate."""
        from do_math import formal
        from do_math.file_io import sha256_file
        checker = Path(formal.__file__).resolve()
        python = Path(sys.executable).resolve()
        approved = {'executable': str(python), 'sha256': sha256_file(python), 'configured_command': [str(python)],
                    'version': 'fixture', 'version_exit': 0, 'verifier_sha256': sha256_file(checker),
                    'verifier_path': str(checker), 'executables': {}, 'project': None}
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            context = {"action": {"role": "research_work"}, "snapshot": "fixed",
                "formal_verifier": {"command": [str(python)], "allowed_axioms": [], "expected_toolchain": approved}}
            install_tools(workspace, context, schema_for('research_work'), 1000000)
            script = ('import json, sys; sys.path.insert(0, sys.argv[1]); from do_math import formal; '
                      'print(json.dumps({"file": formal.__file__, '
                      '"errors": formal.toolchain_identity_errors(json.loads(sys.argv[2]))}))')
            result = subprocess.run([sys.executable, '-B', '-c', script,
                                     str(workspace / 'input/tools/submission-support.zip'), json.dumps(approved)],
                                    capture_output=True, text=True, encoding='utf-8', timeout=60)
            observed = json.loads(result.stdout or 'null')
            self.assertIsNotNone(observed, result.stderr)
            self.assertIn('submission-support.zip', observed['file'])
            self.assertEqual(observed['errors'], [])

    @category('lean')
    def test_actual_standalone_preview_checks_code_axioms_and_stop(self):
        command = actual_command()
        self.assertIsNotNone(command, 'this integration test requires the real compiler')
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            context = {"action": {"role": "research_work"}, "snapshot": "fixed",
                "formal_verifier": {"command": command, "allowed_axioms": ["propext", "Classical.choice", "Quot.sound"]}}
            install_tools(workspace, context, schema_for('research_work'), 1000000)
            preview = context['formal_verifier'].get('preview')
            self.assertIsNotNone(preview, 'worker must receive the compiler preview command')
            for source, expected, name in [('theorem good : True := by trivial', 'verified', 'good'),
                                     ('theorem good : True := by\r\n  trivial\r\n', 'verified', 'good'),
                                     ('theorem good : False := by sorry', 'rejected', 'good'),
                                     ('theorem good : False := by trivial', 'failed', 'good'),
                                     ("theorem good' : True := by trivial", 'verified', "good'"),
                                     ('theorem \u212a (\u2126 : True) : True := \u2126\r\n-- e\u0301\n', 'verified', '\u212a')]:
                (workspace / 'draft.lean').write_bytes(source.encode('utf-8'))
                result = subprocess.run([*preview['command'], '--source', 'draft.lean', '--declaration', name],
                    cwd=workspace, capture_output=True, text=True, encoding='utf-8',
                    creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0), timeout=None)
                data = json.loads(result.stdout)
                self.assertEqual(data['status'], expected, result.stderr + str(data))
                self.assertEqual(data['source_sha256'], hashlib.sha256(source.encode()).hexdigest())
                self.assertFalse(data['authoritative'])
                self.assertEqual(data['toolchain']['configured_command'], command)
                self.assertEqual(data['input_snapshot'], 'fixed')
                if expected == 'verified':
                    self.assertIn(name, data['declaration_evidence'])
                    self.assertEqual(set(data['dependency_closure'][name]), set(data['dependency_evidence'][name]))
            self.assertFalse(any((workspace / family).exists() for family in
                ('formal_results', 'expositions', 'identity_assessments', 'assessment_uses')))
            (workspace / '.control').mkdir(exist_ok=True)
            (workspace / '.control/stop-request.json').write_text('{}')
            result = subprocess.run([*preview['command'], '--source', 'draft.lean', '--declaration', 'good'],
                cwd=workspace, capture_output=True, text=True, encoding='utf-8',
                creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0), timeout=30)
            self.assertEqual(json.loads(result.stdout)['status'], 'stopped')


if __name__ == '__main__':
    unittest.main()
