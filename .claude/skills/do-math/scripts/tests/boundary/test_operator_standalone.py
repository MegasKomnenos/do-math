"""The installed skill works on its own, as real child processes (``probe_cli.py``, ``setup_lean.py``).

A copied skill must check itself without its author's repository documents.
Lean preparation must drop the ready marker when a step fails. The second test
copies ``setup_lean.py`` and the ``do_math`` package under a temporary
repository root, so the product's own ``toolchain_root()`` names a temporary
toolchain folder; its ``lake.exe`` is a real program that exits non-zero
(Windows ``where.exe`` finding nothing), so ``lake update`` fails for real and
no download or compiler runs.
"""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from do_math.lean_evidence import LEAN_VERSION, READY_MARKER, mathlib_project, portable_bin


SKILL = Path(__file__).resolve().parents[3]
SCRIPTS = SKILL / 'scripts'
NO_WINDOW = getattr(subprocess, 'CREATE_NO_WINDOW', 0)
WHERE = Path(os.environ.get('SystemRoot', r'C:\Windows')) / 'System32' / 'where.exe'


class StandaloneTests(unittest.TestCase):
    def test_copied_skill_checks_itself_without_repository_documents(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            skill = root / 'do-math'
            shutil.copytree(SKILL, skill, ignore=shutil.ignore_patterns('__pycache__'))
            result = subprocess.run([sys.executable, str(skill / 'scripts/probe_cli.py'), '--skill-only'],
                                    cwd=root, capture_output=True, timeout=30, creationflags=NO_WINDOW)
            self.assertEqual(result.returncode, 0, result.stderr.decode(errors='replace'))
            report = json.loads(result.stdout)
            self.assertEqual(report['status'], 'verified')
            self.assertEqual(report['scope'], 'installed_skill_structure')
            self.assertFalse((root / 'docs').exists())

    @unittest.skipUnless(WHERE.is_file(), 'Windows where.exe stands in for a failing lake.exe')
    def test_failed_lean_preparation_invalidates_the_previous_ready_marker(self):
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            scripts = home / '.claude/skills/do-math/scripts'
            shutil.copytree(SCRIPTS / 'do_math', scripts / 'do_math', ignore=shutil.ignore_patterns('__pycache__'))
            shutil.copy2(SCRIPTS / 'setup_lean.py', scripts / 'setup_lean.py')
            root = home / '.skill-workspace/do-math-toolchains'
            binary = portable_bin(root) / 'lean.exe'
            binary.parent.mkdir(parents=True)
            binary.write_bytes(b'fixture: no compiler is started')
            lake = portable_bin(root) / 'lake.exe'
            shutil.copy2(WHERE, lake)
            project = mathlib_project(root)
            project.mkdir(parents=True)
            marker = project / READY_MARKER
            marker.write_text(LEAN_VERSION, encoding='utf-8')
            result = subprocess.run([sys.executable, str(scripts / 'setup_lean.py')], cwd=home,
                                    env={**os.environ, 'PATH': str(binary.parent)}, capture_output=True,
                                    text=True, encoding='utf-8', timeout=60, creationflags=NO_WINDOW)
            # An execution error is exit code 2 with a JSON status, and never leaves a ready marker.
            self.assertEqual(result.returncode, 2, result.stderr)
            outcome = json.loads(result.stdout)
            self.assertEqual(outcome['status'], 'error')
            self.assertTrue(outcome['error'].startswith('CalledProcessError: '), outcome['error'])
            self.assertIn('+ ' + str(lake) + ' update', result.stderr)
            self.assertFalse(marker.exists())


if __name__ == '__main__':
    unittest.main()
