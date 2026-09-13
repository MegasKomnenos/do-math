"""Failure reporting checks which never call a model."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


class ProbeTests(unittest.TestCase):
    def test_missing_cli_preserves_failed_report_and_runs_no_cases(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            script = Path(__file__).resolve().parents[1] / "probe_codex.py"
            report_dir = root / "evidence"
            result = subprocess.run([sys.executable, str(script), "--codex", str(root / "missing.exe"),
                                     "--model", "must-not-run", "--output-dir", str(report_dir)],
                                    capture_output=True, timeout=20)
            self.assertEqual(result.returncode, 1, result.stderr)
            report = json.loads((report_dir / "report.json").read_bytes())
            self.assertFalse(report["passed"])
            self.assertEqual(report["cases"], [])
            self.assertEqual(report["not_run"], ["text", "structured", "cancel"])
            self.assertEqual(report["failure"], "cli_description_unavailable_or_incompatible")


if __name__ == "__main__":
    unittest.main()
