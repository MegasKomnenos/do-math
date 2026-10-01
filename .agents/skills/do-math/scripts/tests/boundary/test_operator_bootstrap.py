"""The operator's bootstrap entry point as a real child Python (``operator_bootstrap.py``).

The bootstrap is the scheduled tasks' entry point: it must start, and report,
even when the engine package it supervises cannot be imported. Each test runs
a copy of the installed skill as a real process, so the copy's damage stays in
a temporary folder.
"""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from test_categories import test_group


SKILL = Path(__file__).resolve().parents[3]
INSTANCE = 'RI-00000000000000000000000000'
NO_WINDOW = getattr(subprocess, 'CREATE_NO_WINDOW', 0)


def copy_skill(destination):
    shutil.copytree(SKILL, destination, ignore=shutil.ignore_patterns('__pycache__', '*.pyc', '.lake'))
    return destination


@test_group('resource')
class BootstrapTests(unittest.TestCase):
    def test_supervisor_starts_when_engine_cannot_be_imported(self):
        with tempfile.TemporaryDirectory() as directory:
            scripts = copy_skill(Path(directory) / 'skill') / 'scripts'
            (scripts / 'do_math/engine.py').write_text('broken engine syntax !!!\n', encoding='utf-8')
            broken = subprocess.run([sys.executable, str(scripts / 'do_math.py'), '--help'], cwd=directory,
                                    capture_output=True, text=True, encoding='utf-8', creationflags=NO_WINDOW)
            self.assertNotEqual(broken.returncode, 0)
            self.assertIn('SyntaxError', broken.stderr)
            supervisor = subprocess.run([sys.executable, str(scripts / 'operator_bootstrap.py'), '--help'],
                                        cwd=directory, capture_output=True, text=True, encoding='utf-8',
                                        creationflags=NO_WINDOW)
            self.assertEqual(supervisor.returncode, 0, supervisor.stderr)
            self.assertIn('run-engine', supervisor.stdout)

    def test_frozen_supervisor_survives_damage_to_live_shared_modules(self):
        """About 6 s: two freezes of a whole skill copy and three child interpreters."""
        with tempfile.TemporaryDirectory() as directory:
            live = copy_skill(Path(directory) / 'installation')
            bootstrap = live / 'scripts/operator_bootstrap.py'
            command = [sys.executable, str(bootstrap), '--freeze', '--installation-root', str(live),
                       '--workspace', str(Path(directory) / 'workspace')]
            first = subprocess.run(command, capture_output=True, text=True, check=True, creationflags=NO_WINDOW)
            frozen = json.loads(first.stdout)
            second = subprocess.run(command, capture_output=True, text=True, check=True, creationflags=NO_WINDOW)
            self.assertEqual(frozen, json.loads(second.stdout))
            (live / 'scripts/do_math/repository.py').write_text('damaged shared module !!!\n', encoding='utf-8')
            result = subprocess.run([sys.executable, frozen['entrypoint'], '--help'], cwd=directory,
                                    capture_output=True, text=True, creationflags=NO_WINDOW)
            self.assertEqual(result.returncode, 0, result.stderr)
            info = subprocess.run([sys.executable, frozen['entrypoint'], '--bootstrap-info'], cwd=directory,
                                  capture_output=True, text=True, check=True, creationflags=NO_WINDOW)
            self.assertEqual(json.loads(info.stdout)['manifest']['installation_root'], str(live.resolve()))

    def test_changed_frozen_code_is_rejected_before_import(self):
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run([sys.executable, str(SKILL / 'scripts/operator_bootstrap.py'),
                                     '--freeze', '--installation-root', str(SKILL), '--workspace', directory],
                                    capture_output=True, text=True, check=True, creationflags=NO_WINDOW)
            frozen = json.loads(result.stdout)
            module = Path(frozen['entrypoint']).parent / 'do_math/repository.py'
            module.write_text("raise RuntimeError('unverified code executed')\n", encoding='utf-8')
            rejected = subprocess.run([sys.executable, frozen['entrypoint'], '--help'],
                                      capture_output=True, text=True, creationflags=NO_WINDOW)
            self.assertNotEqual(rejected.returncode, 0)
            self.assertIn('bootstrap file hash mismatch', rejected.stderr)
            self.assertNotIn('RuntimeError: unverified code executed', rejected.stderr)


@test_group('resource')
class BrokenEngineProbeTests(unittest.TestCase):
    def test_real_probe_persists_failure_when_engine_has_syntax_error(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repository, workspace = root / 'repository', root / 'workspace'
            repository.mkdir()
            workspace.mkdir()
            isolated = copy_skill(root / 'isolated-skill')
            (isolated / 'scripts/do_math/engine.py').write_text('broken engine syntax !!!\n', encoding='utf-8')
            result = subprocess.run([sys.executable, str(isolated / 'scripts/operator_bootstrap.py'), 'check',
                                     '--repository', str(repository), '--instance', INSTANCE,
                                     '--workspace', str(workspace), '--probe'],
                                    capture_output=True, text=True, encoding='utf-8', timeout=30,
                                    creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
            self.assertEqual(result.returncode, 0, result.stderr)
            failure = json.loads(result.stdout)
            self.assertEqual(failure['error_type'], 'SyntaxError')
            self.assertEqual(failure['outcome'], 'recovery_required')
            self.assertEqual(json.loads((workspace / 'operator/engine-failure.json').read_text(encoding='utf-8')),
                             failure)


if __name__ == '__main__':
    unittest.main()
