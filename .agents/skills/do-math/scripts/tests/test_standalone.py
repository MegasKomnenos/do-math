"""The installed skill must work without its author's repository documents."""
from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math import formal


class StandaloneTests(unittest.TestCase):
    def test_shallow_installation_without_lean_reports_unavailable(self):
        shallow = Path(Path.cwd().anchor) / "do-math/scripts/do_math/formal.py"
        with patch.object(formal, "__file__", str(shallow)), patch.object(formal.shutil, "which", return_value=None):
            self.assertIsNone(formal.discover_lean())

    def test_copied_skill_checks_itself_without_repository_documents(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            skill = root / "do-math"
            shutil.copytree(Path(__file__).resolve().parents[2], skill,
                            ignore=shutil.ignore_patterns("__pycache__"))
            result = subprocess.run(
                [sys.executable, str(skill / "scripts/probe_cli.py"), "--skill-only"],
                cwd=root, capture_output=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stderr.decode(errors="replace"))
            report = json.loads(result.stdout)
            self.assertEqual(report["status"], "verified")
            self.assertEqual(report["scope"], "installed_skill_structure")
            self.assertFalse((root / "docs").exists())

    def test_failed_lean_preparation_invalidates_the_previous_ready_marker(self):
        import setup_lean
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            binary = setup_lean.portable_bin(root) / 'lean.exe'
            binary.parent.mkdir(parents=True)
            binary.write_bytes(b'fixture: no compiler is started')
            project = setup_lean.mathlib_project(root)
            project.mkdir(parents=True)
            marker = project / setup_lean.READY_MARKER
            marker.write_text(setup_lean.LEAN_VERSION, encoding='utf-8')
            with patch.object(sys, 'argv', ['setup_lean.py']), \
                    patch.object(setup_lean, 'toolchain_root', return_value=root), \
                    patch.object(setup_lean, 'run', side_effect=subprocess.CalledProcessError(1, ['lake', 'update'])), \
                    redirect_stdout(io.StringIO()) as output:
                with self.assertRaises(SystemExit) as stopped:
                    setup_lean.main()
            # An execution error is exit code 2 with a JSON status, and never leaves a ready marker.
            self.assertEqual(stopped.exception.code, 2)
            self.assertEqual(json.loads(output.getvalue())['status'], 'error')
            self.assertFalse(marker.exists())


if __name__ == "__main__":
    unittest.main()
