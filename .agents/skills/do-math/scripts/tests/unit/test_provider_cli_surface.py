"""The CLI command-surface verdict (``cli_execution.surface_report``, layer 2) for the Codex adapter's help commands.

``LocalCLIAdapter.describe`` runs ``--version`` and each help command of its
provider and hands the results here; ``boundary.test_provider_cli_surface``
runs ``describe`` itself against a CLI executable.
"""
import subprocess
from copy import deepcopy
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

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
    def test_unknown_final_provider_is_rejected_before_any_semantic_translation(self):
        from do_math.provider_final import output_contract, semantic_output
        for call in (lambda: output_contract('unregistered', {}),
                     lambda: semantic_output('unregistered', b'{}')):
            with self.subTest(call=call), self.assertRaises(ValueError) as caught:
                call()
            self.assertEqual(str(caught.exception), 'unsupported final-response provider: unregistered')

    def test_host_observations_use_the_selected_provider_and_exact_cli_surface(self):
        """About 0.2 s: both providers' identities hash their actual modules; only the OS command boundary is controlled."""
        import hashlib
        from do_math.claude_adapter import ADAPTERS
        from do_math.local_host import LocalHost
        from support.fakes.clock import FakeClock
        from support.fakes.jobs import FakeJobs
        root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        host = LocalHost(jobs=FakeJobs(), clock=FakeClock(), environment={}, git_backend=None)
        executables = {}
        for provider in ADAPTERS:
            executable = root / (provider + '.exe')
            executable.write_bytes(provider.encode())
            executables[provider] = str(executable)
        executables['lean'] = str(root / 'lean.exe')
        with patch('shutil.which', side_effect=executables.get):
            self.assertEqual(host.discover_lean(), [executables['lean']])
            for provider, adapter_type in ADAPTERS.items():
                calls = []
                outputs = {arguments: b' '.join(flags) for arguments, flags in adapter_type.help_commands}

                def run(command, **options):
                    calls.append((command, options))
                    raw = b'fixture-version' if command[1:] == ['--version'] else outputs[tuple(command[1:])]
                    return subprocess.CompletedProcess(command, 0, raw, b'')

                profile = {'ai': {'provider': provider}}
                identity = host.cli_identity(profile)
                key = host.cli_observation_key(profile)
                with self.subTest(provider=provider), patch('subprocess.run', run):
                    description = host.cli_describe(profile)
                self.assertEqual(identity['cli_path'], executables[provider])
                self.assertEqual(identity['cli_sha256'], hashlib.sha256(provider.encode()).hexdigest())
                self.assertEqual(description['identity'], identity)
                self.assertTrue(description['verified'], description)
                self.assertEqual(key[2], executables[provider])
                self.assertEqual([call[0] for call in calls], [[executables[provider], '--version'],
                    *[[executables[provider], *arguments] for arguments, _ in adapter_type.help_commands]])
                self.assertTrue(all(options['shell'] is False and options['capture_output'] is True
                                    for _, options in calls))

    def test_start_paths_accept_path_lookup_and_reject_a_different_executable(self):
        from do_math.cli_execution import checked_start_paths
        from do_math.model_call import worker_request_fields
        from support.fakes.clock import FakeClock
        from support.provider_runs import ProviderJobs
        from do_math.claude_adapter import ADAPTERS
        for provider, adapter_type in ADAPTERS.items():
            with self.subTest(provider=provider):
                root = Path(self.enterContext(tempfile.TemporaryDirectory()))
                executable = root/'identity-probe.exe'
                executable.write_bytes(b'fixture executable identity; not launched')
                evidence = root/'evidence'
                workspace = root/'workspace'
                adapter = adapter_type(executable.name, jobs=ProviderJobs(), clock=FakeClock())
                seed = worker_request_fields(adapter.worker_options(evidence),
                    prompt_path=evidence/'input.txt', workspace=workspace, evidence_dir=evidence,
                    cli_model='test-model', effort='high', timeout_seconds=10,
                    schema_path=evidence/'schema.json', execution_id=None, reference=None,
                    resource_limits=None, control_binding=None, scholarly_server=None,
                    claude_only_assigned_model=False)
                before = deepcopy(seed)
                with patch.dict(os.environ, {'PATH': str(root), 'PATHEXT': '.EXE'}):
                    expected = executable.resolve(strict=True)
                    result = checked_start_paths(seed, root/'request.json',
                        cli_path=str(expected), executable_key=adapter.executable_key)
                    self.assertEqual(result[-1], workspace.resolve())
                    with self.assertRaisesRegex(ValueError, '^request CLI executable differs from adapter executable$'):
                        checked_start_paths(seed, root/'request.json',
                            cli_path=str(root/'different.exe'), executable_key=adapter.executable_key)
                    from do_math.file_io import executable_identity
                    self.assertEqual(executable_identity(executable.name, strict=True), expected)
                    if os.name == 'nt':
                        self.assertEqual(executable_identity(executable.stem.upper(), strict=True), expected)
                    self.assertEqual(executable_identity(root/'.'/executable.name), expected)
                    self.assertEqual(adapter.capability_identity()['cli_path'], str(expected))
                    self.assertEqual(adapter.observation_key()[2], str(expected))
                    missing = root/'missing-identity.exe'
                    self.assertEqual(executable_identity(missing), missing.resolve())
                    with self.assertRaisesRegex(FileNotFoundError, r'missing-identity\.exe'):
                        executable_identity(missing, strict=True)
                self.assertEqual(seed, before)

    def test_surface_requires_the_flags_used_by_the_worker(self):
        for missing in (None, b"--strict-config", b"--color", b"--cd"):
            with self.subTest(missing=missing):
                description = report(b" ".join(flag for flag in WORKER_FLAGS if flag != missing))
                self.assertEqual(description["verified"], missing is None)
                self.assertEqual(description["supported"]["jsonl"], missing is None)


if __name__ == "__main__":
    unittest.main()
