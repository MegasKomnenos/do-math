"""Exact subprocess invocation and return/exception contract, without launching Git."""
from pathlib import Path
import subprocess
from types import SimpleNamespace
import unittest

from do_math.git_process import GitProcess
from do_math.ports.git_backend import GitBackendError


class GitInitProcessTests(unittest.TestCase):
    def test_git_init_existence_does_not_adopt_describe_output_or_error_contract(self):
        for code, stdout, error_type, message in (
                (1, b'', GitBackendError, 'git rev-parse .* failed: unavailable'),
                (0, b'', GitBackendError, 'did not report the Git directory'),
                (0, b'\xff', UnicodeDecodeError, 'invalid start byte')):
            def run(*args, **kwargs):
                return SimpleNamespace(returncode=code, stdout=stdout, stderr=b'unavailable')
            backend = GitProcess(environment={}, run=run)
            self.assertIs(backend.repository_exists(Path('repository')), not code)
            with self.assertRaisesRegex(error_type, message):
                backend.describe(Path('repository'))

    def test_git_init_preserves_exit_only_result_and_ambient_invocation(self):
        repository = Path('relative-repository')
        for operation, arguments in (('initialize_repository', ['init', '-q']),
                                     ('repository_exists', ['rev-parse', '--git-dir'])):
            for code in (0, 1, 128, -1):
                for output in (b'', b'.git\n', b'\xff'):
                    calls = []
                    def run(*args, **kwargs):
                        calls.append((args, kwargs))
                        return SimpleNamespace(returncode=code, stdout=output, stderr=b'\xff')
                    backend = GitProcess(environment={'SHOULD_NOT_BE_PASSED': '1'}, run=run)
                    self.assertIs(getattr(backend, operation)(repository), not code)
                    self.assertEqual(calls, [((['git', '-C', str(repository), *arguments],), {
                        'check': False, 'capture_output': True,
                        'creationflags': getattr(subprocess, 'CREATE_NO_WINDOW', 0)})])

    def test_git_init_os_and_subprocess_errors_propagate_unchanged(self):
        for operation in ('initialize_repository', 'repository_exists'):
            for error in (FileNotFoundError('git missing'), PermissionError('git denied'),
                          subprocess.SubprocessError('spawn failed')):
                def run(*args, **kwargs):
                    raise error
                backend = GitProcess(environment={}, run=run)
                with self.assertRaises(type(error)) as caught:
                    getattr(backend, operation)(Path('repository'))
                self.assertIs(caught.exception, error)
