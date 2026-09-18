"""The producer's standalone compiler command gives feedback, never authority."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math.formal import discover_lean
from do_math.submission import install_tools
from do_math.contracts import schema_for


class LeanPreviewTests(unittest.TestCase):
    def test_actual_standalone_preview_checks_code_axioms_and_stop(self):
        command = discover_lean()
        self.assertIsNotNone(command, 'this integration test requires the real compiler')
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            context = {"action": {"role": "research_work"}, "snapshot": "fixed",
                "formal_verifier": {"command": command, "allowed_axioms": ["propext", "Classical.choice", "Quot.sound"],
                                    "timeout_seconds": 30}}
            install_tools(workspace, context, schema_for('research_work'), 1000000)
            preview = context['formal_verifier'].get('preview')
            self.assertIsNotNone(preview, 'worker must receive the compiler preview command')
            for source, expected, name in [('theorem good : True := by trivial', 'verified', 'good'),
                                     ('theorem good : True := by\r\n  trivial\r\n', 'verified', 'good'),
                                     ('theorem good : False := by sorry', 'rejected', 'good'),
                                     ('theorem good : False := by trivial', 'failed', 'good'),
                                     ("theorem good' : True := by trivial", 'verified', "good'")]:
                (workspace / 'draft.lean').write_bytes(source.encode('utf-8'))
                result = subprocess.run([*preview['command'], '--source', 'draft.lean', '--declaration', name],
                    cwd=workspace, capture_output=True, text=True, encoding='utf-8',
                    creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0), timeout=60)
                data = json.loads(result.stdout)
                self.assertEqual(data['status'], expected, result.stderr + str(data))
                self.assertEqual(data['source_sha256'], hashlib.sha256(source.encode()).hexdigest())
                self.assertFalse(data['authoritative'])
                self.assertEqual(data['toolchain']['configured_command'], command)
            (workspace / 'stop-request.json').write_text('{}')
            result = subprocess.run([*preview['command'], '--source', 'draft.lean', '--declaration', 'good'],
                cwd=workspace, capture_output=True, text=True, encoding='utf-8',
                creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0), timeout=30)
            self.assertEqual(json.loads(result.stdout)['status'], 'stopped')


if __name__ == '__main__':
    unittest.main()
