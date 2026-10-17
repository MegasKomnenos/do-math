"""Each provider worker is the direct Python root of its Job: a fresh interpreter imports it as a script.

Inside its Job a worker runs as ``python <worker>.py REQUEST.json`` outside the
``do_math`` package, so its imports fall back to the modules beside it. The
subject is interpreter start-up and ``sys.path``, which only a child process
shows (조사 K-24).
"""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from do_math import claude_worker, codex_worker
from test_categories import test_group


@test_group('resource')
class WorkerRootTests(unittest.TestCase):
    def run_root(self, module):
        return subprocess.run([sys.executable, str(Path(module.__file__))], capture_output=True, timeout=10,
                              creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))

    def test_worker_remains_importable_as_its_direct_job_root(self):
        result = self.run_root(codex_worker)
        self.assertNotIn(b"No module named", result.stderr)
        self.assertIn(b"usage: codex_worker.py REQUEST.json", result.stderr)

    def test_claude_worker_remains_importable_as_its_direct_job_root(self):
        result = self.run_root(claude_worker)
        self.assertNotIn(b"No module named", result.stderr)
        self.assertIn(b"usage: claude_worker.py REQUEST.json", result.stderr)

    def assert_checked_request(self, module, provider):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            prompt = root / 'prompt.txt'
            prompt.write_bytes('local request 경계\n'.encode('utf-8'))
            schema = root / 'schema.json'
            schema.write_bytes(b'{"type":"object"}\n')
            request = {provider + '_path': sys.executable, 'prompt_path': str(prompt), 'cwd': str(root),
                       'model': 'local-boundary', 'effort': 'low', 'max_runtime_seconds': None,
                       'stdout_path': str(root / 'stdout'), 'stderr_path': str(root / 'stderr'),
                       'status_path': str(root / 'status.json'), 'execution_id': 'EX-direct',
                       'profile_ref': {'id': 'EP-direct', 'revision': 1, 'sha256': 'a' * 64}}
            request['output_schema_path'] = str(schema)
            if provider == 'codex':
                request.update(sandbox='read-only', approval_policy='never', final_path=str(root / 'final'))
            path = root / 'request.json'
            path.write_text(json.dumps(request), encoding='utf-8')
            # Python is a real failing CLI at the external executable boundary:
            # it refuses provider flags, so no provider or paid call is involved.
            result = subprocess.run([sys.executable, str(Path(module.__file__)), str(path)], cwd=root,
                env={key: value for key, value in os.environ.items() if key != 'PYTHONPATH'},
                capture_output=True, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
            self.assertEqual((result.returncode, result.stdout, result.stderr), (0, b'', b''))
            status = json.loads((root / 'status.json').read_bytes())
            self.assertEqual((status['state'], status['cli_exit_code']), ('exited', 2))
            self.assertEqual(status['request_sha256'], hashlib.sha256(path.read_bytes()).hexdigest())
            self.assertEqual(status['stdin_sha256'], hashlib.sha256(prompt.read_bytes()).hexdigest())
            self.assertEqual(status['schema_sha256'], hashlib.sha256(schema.read_bytes()).hexdigest())
            command = module.build_argv(request)
            self.assertEqual(status['argv_sha256'], hashlib.sha256('\0'.join(command).encode()).hexdigest())
            self.assertEqual((status['execution_id'], status['profile_ref']),
                             (request['execution_id'], request['profile_ref']))
            self.assertEqual((root / 'stdout').read_bytes(), b'')
            option = b'--ask-for-approval' if provider == 'codex' else b'--print'
            self.assertEqual((root / 'stderr').read_bytes().splitlines()[0], b'unknown option ' + option)

    def test_codex_direct_root_records_the_checked_request_and_cli_failure(self):
        self.assert_checked_request(codex_worker, 'codex')

    def test_claude_direct_root_records_the_checked_request_and_cli_failure(self):
        self.assert_checked_request(claude_worker, 'claude')


if __name__ == '__main__':
    unittest.main()
