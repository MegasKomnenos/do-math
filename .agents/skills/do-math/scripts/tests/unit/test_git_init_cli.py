"""CLI eligibility and exact error envelopes; stop before engine initialization."""
from dataclasses import replace
from pathlib import Path
import subprocess
import tempfile
import unittest

from support.entry import entry
from support.git_init_cli import git_init_main
from support.git_init_faults import GitInitFaults


class GitInitCliRejectionTests(unittest.TestCase):
    def invoke(self, root, backend, *, create):
        values = entry()
        values.ports = replace(values.ports, git_backend=backend)
        argv = ['init', '--repository', str(root / 'repository'), '--workspace', str(root / 'work'),
                '--goal', 'Git prerequisite']
        if create:
            argv.append('--create-repository')
        return git_init_main(argv, values)

    def assert_error(self, response, code, kind, message):
        actual, envelope = response
        self.assertEqual(actual, code)
        self.assertEqual(envelope['error'], {'kind': kind, 'message': message,
            'next_owner': 'user' if kind == 'input_error' else 'operator', 'retryable': False})

    def test_git_init_create_rejects_file_and_nonempty_before_port(self):
        for kind in ('file', 'nonempty', 'repository'):
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                repository = root / 'repository'
                backend = GitInitFaults()
                if kind == 'file':
                    repository.write_bytes(b'keep')
                else:
                    repository.mkdir()
                    if kind == 'repository':
                        backend.initialize_repository(repository)
                        backend.observed.clear()
                    else:
                        (repository / 'keep').write_bytes(b'keep')
                self.assert_error(self.invoke(root, backend, create=True), 2, 'input_error',
                    '--create-repository accepts only a missing or empty directory')
                self.assertEqual(backend.observed, [])
                self.assertFalse((root / 'work').exists())

    def test_git_init_no_create_missing_or_empty_never_initializes(self):
        for empty in (False, True):
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                if empty:
                    (root / 'repository').mkdir()
                backend = GitInitFaults()
                self.assert_error(self.invoke(root, backend, create=False), 2, 'input_error',
                    '--repository must name an existing Git repository; use init --create-repository explicitly')
                self.assertEqual(backend.observed, [('exists', empty)])
                self.assertEqual((root / 'repository').exists(), empty)

    def test_git_init_mkdir_precedes_init_failure_and_existence_is_not_attempted(self):
        for empty in (False, True):
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory) / 'nested'
                if empty:
                    (root / 'repository').mkdir(parents=True)
                backend = GitInitFaults(init_failure=True)
                self.assert_error(self.invoke(root, backend, create=True), 5, 'tool_error', 'git init failed')
                self.assertEqual(backend.observed, [('initialize', True, ())])
                self.assertTrue((root / 'repository').is_dir())

    def test_git_init_success_then_failed_check_keeps_created_repository(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            backend = GitInitFaults(inspect_failure=True)
            self.assert_error(self.invoke(root, backend, create=True), 2, 'input_error',
                '--repository must name an existing Git repository; use init --create-repository explicitly')
            self.assertEqual(backend.observed, [('initialize', True, ()), ('exists', True)])
            self.assertTrue((root / 'repository/.git/HEAD').is_file())

    def test_git_init_boundary_exceptions_are_tool_errors_at_either_step(self):
        for step in ('init_failure', 'inspect_failure'):
            for error in (FileNotFoundError('missing git'), PermissionError('denied git'),
                          subprocess.SubprocessError('spawn failed')):
                with tempfile.TemporaryDirectory() as directory:
                    root = Path(directory)
                    backend = GitInitFaults(**{step: error})
                    self.assert_error(self.invoke(root, backend, create=True), 5, 'tool_error', str(error))
                    self.assertEqual(len(backend.observed), 1 if step == 'init_failure' else 2)
