"""The installed skill must work without its author's repository documents."""
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
import probe_native_isolation


class StandaloneTests(unittest.TestCase):
    def test_shallow_installation_without_lean_reports_unavailable(self):
        shallow = Path(Path.cwd().anchor) / "do-math/scripts/do_math/formal.py"
        with patch.object(formal, "__file__", str(shallow)), patch.object(formal.shutil, "which", return_value=None):
            self.assertIsNone(formal.discover_lean())

    def test_native_probe_help_does_not_require_repository_ancestors(self):
        shallow = Path(Path.cwd().anchor) / "do-math/scripts/probe_native_isolation.py"
        with patch.object(probe_native_isolation, "__file__", str(shallow)), patch.object(sys, "argv", ["probe", "--help"]):
            with self.assertRaises(SystemExit) as result:
                probe_native_isolation.main()
            self.assertEqual(result.exception.code, 0)

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


if __name__ == "__main__":
    unittest.main()
