from pathlib import Path
import json
import shutil
import subprocess
import sys
import tempfile
import unittest


class OperatorBootstrapTests(unittest.TestCase):
    def test_supervisor_starts_when_engine_cannot_be_imported(self):
        skill_root = Path(__file__).resolve().parents[2]
        with tempfile.TemporaryDirectory() as directory:
            isolated = Path(directory) / "skill"
            shutil.copytree(skill_root, isolated,
                            ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".lake"))
            scripts = isolated / "scripts"
            (scripts / "do_math/engine.py").write_text("broken engine syntax !!!\n", encoding="utf-8")
            broken = subprocess.run([sys.executable, str(scripts / "do_math.py"), "--help"],
                                    cwd=directory, capture_output=True, text=True, encoding="utf-8")
            self.assertNotEqual(broken.returncode, 0)
            self.assertIn("SyntaxError", broken.stderr)
            supervisor = subprocess.run([sys.executable, str(scripts / "operator_bootstrap.py"), "--help"],
                                        cwd=directory, capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(supervisor.returncode, 0, supervisor.stderr)
            self.assertIn("run-engine", supervisor.stdout)

    def test_frozen_supervisor_survives_damage_to_live_shared_modules(self):
        skill_root = Path(__file__).resolve().parents[2]
        with tempfile.TemporaryDirectory() as directory:
            live = Path(directory) / "installation"
            shutil.copytree(skill_root, live,
                            ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".lake"))
            bootstrap = live / "scripts/operator_bootstrap.py"
            command = [sys.executable, str(bootstrap), "--freeze", "--installation-root", str(live),
                       "--workspace", str(Path(directory) / "workspace")]
            first = subprocess.run(command, capture_output=True, text=True, check=True)
            frozen = json.loads(first.stdout)
            second = subprocess.run(command, capture_output=True, text=True, check=True)
            self.assertEqual(frozen, json.loads(second.stdout))
            (live / "scripts/do_math/repository.py").write_text("damaged shared module !!!\n", encoding="utf-8")
            result = subprocess.run([sys.executable, frozen["entrypoint"], "--help"], cwd=directory,
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            info = subprocess.run([sys.executable, frozen["entrypoint"], "--bootstrap-info"], cwd=directory,
                                  capture_output=True, text=True, check=True)
            self.assertEqual(json.loads(info.stdout)["manifest"]["installation_root"], str(live.resolve()))

    def test_changed_frozen_code_is_rejected_before_import(self):
        skill_root = Path(__file__).resolve().parents[2]
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run([sys.executable, str(skill_root / "scripts/operator_bootstrap.py"),
                "--freeze", "--installation-root", str(skill_root), "--workspace", directory],
                capture_output=True, text=True, check=True)
            frozen = json.loads(result.stdout)
            module = Path(frozen["entrypoint"]).parent / "do_math/repository.py"
            module.write_text("raise RuntimeError('unverified code executed')\n", encoding="utf-8")
            rejected = subprocess.run([sys.executable, frozen["entrypoint"], "--help"],
                                      capture_output=True, text=True)
            self.assertNotEqual(rejected.returncode, 0)
            self.assertIn("bootstrap file hash mismatch", rejected.stderr)
            self.assertNotIn("RuntimeError: unverified code executed", rejected.stderr)

    def test_verified_frozen_files_are_rehashed_only_after_their_fingerprint_changes(self):
        from unittest.mock import patch
        scripts = Path(__file__).resolve().parents[1]
        sys.path.insert(0, str(scripts))
        import operator_bootstrap as bootstrap
        from do_math import file_io
        with tempfile.TemporaryDirectory() as directory:
            manifest = Path(bootstrap.freeze(scripts.parent, Path(directory))["manifest"])
            # Fresh copies cannot age their birth time; treat any past fingerprint as settled.
            with patch.object(file_io, "RACY_NS", 0):
                bootstrap.verify_snapshot(manifest)
                self.assertTrue((manifest.parent / bootstrap.MARKS).is_file())
                with patch.object(file_io, "sha256_file", side_effect=AssertionError("unchanged frozen file was rehashed")):
                    bootstrap.verify_snapshot(manifest)
                (manifest.parent / "scripts/do_math/repository.py").write_text("changed\n", encoding="utf-8")
                with self.assertRaisesRegex(ValueError, "bootstrap file hash mismatch"):
                    bootstrap.verify_snapshot(manifest)


if __name__ == "__main__":
    unittest.main()
