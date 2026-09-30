"""The CLI command-surface verdict (``cli_execution.surface_report``, layer 2) for the Codex adapter's help commands.

``LocalCLIAdapter.describe`` runs ``--version`` and each help command of its
provider and hands the results here; ``boundary.test_provider_cli_surface``
runs ``describe`` itself against a CLI executable.
"""
import subprocess
import unittest

from do_math.cli_execution import surface_report
from do_math.codex_adapter import CodexExecAdapter

# Every flag the Codex worker's command uses, written out rather than read from the adapter.
WORKER_FLAGS = [b"--json", b"--output-last-message", b"--model", b"--sandbox", b"--ephemeral",
                b"--ignore-user-config", b"--ignore-rules", b"--skip-git-repo-check", b"--output-schema",
                b"--config", b"--strict-config", b"--color", b"--cd"]


def report(exec_help):
    adapter = CodexExecAdapter
    outputs = [b"--ask-for-approval", exec_help]
    helps = [(subprocess.CompletedProcess(list(arguments), 0, output), flags)
             for (arguments, flags), output in zip(adapter.help_commands, outputs, strict=True)]
    return surface_report(subprocess.CompletedProcess(["--version"], 0, b"fixture-version"), helps,
                          identity={"fixture": True}, provider=adapter.provider, cli_path="fixture-cli",
                          surface=adapter.surface_capabilities, unknown=adapter.unknown_capabilities)


class SurfaceTests(unittest.TestCase):
    def test_surface_requires_the_flags_used_by_the_worker(self):
        for missing in (None, b"--strict-config", b"--color", b"--cd"):
            with self.subTest(missing=missing):
                description = report(b" ".join(flag for flag in WORKER_FLAGS if flag != missing))
                self.assertEqual(description["verified"], missing is None)
                self.assertEqual(description["supported"]["jsonl"], missing is None)


if __name__ == "__main__":
    unittest.main()
