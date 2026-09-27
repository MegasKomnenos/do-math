"""CLI bookkeeping must not become a research artifact."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math import claude_worker, cli_worker, codex_worker
from do_math.context_store import collect_outputs


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
                events = [{'type': 'system', 'subtype': 'init', 'session_id': 'fixture'},
                          {'type': 'result', 'subtype': 'success', 'is_error': False,
                           'session_id': 'fixture', 'structured_output': {}, 'num_turns': 1, 'usage': {}}]

                timeouts = []
                class Provider:
                    returncode = 0
                    def __init__(self, argv, **options):
                        temporary = Path(options['env']['TEMP'])
                        (temporary / 'runtime.tmp').write_bytes(b'CLI internal bookkeeping')
                        options['stdout'].write(b''.join(json.dumps(row).encode() + b'\n' for row in events))
                    def communicate(self, **options):
                        timeouts.append(options['timeout'])
                        return None, None

                # Both workers launch their CLI through the shared cli_worker.run_cli.
                with patch.object(cli_worker.subprocess, 'Popen', Provider):
                    self.assertEqual(worker.run(path), 0)
                self.assertEqual(json.loads((root / 'status.json').read_text())['state'], 'exited')
                self.assertEqual(timeouts, [None], 'a work request must reach subprocess without a time limit')
                collected = collect_outputs(workspace)
                self.assertTrue(collected['complete'])
                self.assertEqual(collected['files'], {'result.txt': b'research result'})


if __name__ == '__main__':
    unittest.main()
