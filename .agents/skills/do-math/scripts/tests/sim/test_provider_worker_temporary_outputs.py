"""CLI bookkeeping must not become a research artifact: the provider workers (``codex_worker``, ``claude_worker``,
layer 3, through the shared ``cli_worker.run_cli``) and the research collector (``context_store.collect_outputs``),
moved from ``test_worker_temporary_outputs``.

A worker points its CLI's ``TEMP`` and ``TMP`` at the workspace's
``.scratch/.execution-temp``, so the CLI's own temporary files land where the
collector leaves them out. The CLI is the double at the worker's ``spawn``
seam: it writes a temporary file into the ``TEMP`` it was given and a
completed stream, and records the time limit its wait received.
"""
import json
from pathlib import Path
import tempfile
import unittest

from do_math import claude_worker, codex_worker
from do_math.context_store import collect_outputs

EVENTS = [{'type': 'system', 'subtype': 'init', 'session_id': 'fixture'},
          {'type': 'result', 'subtype': 'success', 'is_error': False,
           'session_id': 'fixture', 'structured_output': {}, 'num_turns': 1, 'usage': {}}]


class BookkeepingCLI:
    """The spawn double: each start writes ``runtime.tmp`` into its ``TEMP`` and the stream into its stdout."""

    def __init__(self):
        self.environments, self.timeouts = [], []

    def spawn(self, command, **options):
        environment = dict(options['env'])
        self.environments.append(environment)
        (Path(environment['TEMP']) / 'runtime.tmp').write_bytes(b'CLI internal bookkeeping')
        options['stdout'].write(b''.join(json.dumps(row).encode() + b'\n' for row in EVENTS))
        return _Process(self)


class _Process:
    returncode = 0

    def __init__(self, cli):
        self.cli = cli

    def communicate(self, **options):
        self.cli.timeouts.append(options['timeout'])
        return None, None


class WorkerTemporaryOutputTests(unittest.TestCase):
    def test_actual_worker_temp_creation_is_excluded_by_the_research_collector(self):
        for worker, executable in ((codex_worker, 'codex_path'), (claude_worker, 'claude_path')):
            with self.subTest(worker=worker.__name__), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                workspace = root / 'workspace'; workspace.mkdir()
                (workspace / 'result.txt').write_bytes(b'research result')
                prompt = root / 'input.txt'; prompt.write_text('fixture', encoding='utf-8')
                schema = root / 'schema.json'; schema.write_text('{"type":"object"}', encoding='utf-8')
                request = {executable: 'fixture-cli', 'prompt_path': str(prompt), 'cwd': str(workspace),
                    'model': 'fixture', 'effort': 'low', 'max_runtime_seconds': None,
                    'output_schema_path': str(schema),
                    **{key: str(root / name) for key, name in [('stdout_path', 'stdout.jsonl'),
                        ('stderr_path', 'stderr.txt'), ('status_path', 'status.json')]}}
                if worker is codex_worker:
                    # Only Codex writes a final message file; Claude's final comes from its stream.
                    request.update(approval_policy='never', sandbox='danger-full-access',
                                   final_path=str(root / 'final.txt'))
                path = root / 'request.json'; path.write_text(json.dumps(request), encoding='utf-8')
                cli = BookkeepingCLI()
                self.assertEqual(worker.run(path, spawn=cli.spawn), 0)
                self.assertEqual(json.loads((root / 'status.json').read_text())['state'], 'exited')
                self.assertEqual(cli.timeouts, [None], 'a work request must reach subprocess without a time limit')
                # The CLI's temporary directory is inside the workspace, so the exclusion below is the collector's.
                temporary = str((workspace / '.scratch' / '.execution-temp').resolve())
                environment, = cli.environments
                self.assertEqual((environment['TEMP'], environment['TMP']), (temporary, temporary))
                self.assertEqual((Path(temporary) / 'runtime.tmp').read_bytes(), b'CLI internal bookkeeping')
                collected = collect_outputs(workspace)
                self.assertTrue(collected['complete'])
                self.assertEqual(collected['files'], {'result.txt': b'research result'})


if __name__ == '__main__':
    unittest.main()
