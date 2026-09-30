"""``LocalCLIAdapter.describe`` against a CLI executable: real ``--version`` and help processes.

The executable is a batch file that prints its help texts, so the adapter's
own process calls, their order and the verdict's inputs are the product's.
``unit.test_provider_cli_surface`` checks the verdict function alone.
"""
import os
from pathlib import Path
import tempfile
import unittest

from do_math.codex_adapter import CodexExecAdapter

WORKER_FLAGS = [b"--json", b"--output-last-message", b"--model", b"--sandbox", b"--ephemeral",
                b"--ignore-user-config", b"--ignore-rules", b"--skip-git-repo-check", b"--output-schema",
                b"--config", b"--strict-config", b"--color", b"--cd"]

# ``codex --version``, ``codex --help`` and ``codex exec --help`` print the files beside the script.
SCRIPT = (b'@echo off\r\n'
          b'if "%~1"=="--version" (echo fixture-version& exit /b 0)\r\n'
          b'if "%~1"=="exec" (type "%~dp0exec-help.txt"& exit /b 0)\r\n'
          b'type "%~dp0help.txt"\r\n')


@unittest.skipUnless(os.name == 'nt', 'the fixture CLI is a Windows batch file')
class DescribeTests(unittest.TestCase):
    def test_surface_requires_the_flags_used_by_the_worker(self):
        for missing in (None, b"--strict-config", b"--color", b"--cd"):
            with self.subTest(missing=missing), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                (root / 'help.txt').write_bytes(b'--ask-for-approval\r\n')
                (root / 'exec-help.txt').write_bytes(b' '.join(flag for flag in WORKER_FLAGS if flag != missing))
                cli = root / 'codex.cmd'
                cli.write_bytes(SCRIPT)
                description = CodexExecAdapter(str(cli)).describe()
                self.assertEqual(description["verified"], missing is None)
                self.assertEqual(description["version_bytes"].strip(), b"fixture-version")
                self.assertEqual(description["identity"]["cli_path"], str(cli.resolve()))


if __name__ == '__main__':
    unittest.main()
