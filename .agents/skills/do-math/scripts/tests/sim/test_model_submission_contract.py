"""Explicit standalone answers through the actual ModelRunner and provider workers."""
import json
from pathlib import Path
import tempfile
import unittest

from support.fakes.clock import FakeClock
from support.model import ModelDouble, raw
from support.provider_claude_model import ClaudeModelDouble
from support.provider_runs import ProviderJobs, model_runner


class StandaloneWorkerTests(unittest.TestCase):
    def test_declared_standalone_output_uses_the_real_unbound_worker_protocol(self):
        for model_type, model_name in ((ModelDouble, 'test-model'), (ClaudeModelDouble, 'claude-opus-5')):
            with self.subTest(provider=model_name):
                root = Path(self.enterContext(tempfile.TemporaryDirectory()))
                clock = FakeClock()
                model = model_type(clock)
                output = {'summary': 'explicit standalone probe'}
                model.on('maintenance').reply(raw(output, mode='standalone', expected_receipt=None))
                jobs = ProviderJobs(model, clock=clock)
                runner = model_runner(root, jobs, clock)
                workspace = root / 'workspace'
                workspace.mkdir()
                prompt = ('You are the do-math role: maintenance.\n--- CANONICAL INPUT CONTEXT ---\n'
                          '{"action": {"role": "maintenance"}}\n--- OUTPUT JSON SCHEMA ---\n{}')
                result = runner.run(prompt=prompt, output_schema={'type': 'object'}, workspace=workspace,
                                    evidence_dir=root / 'evidence', model=model_name, effort='low', timeout_seconds=30)
                self.assertEqual((result['status'], result['output']), ('completed', output))
                self.assertEqual(model.receipts, [])
                self.assertEqual(len(model.calls), 1)
                job, = jobs.launched
                request = json.loads(Path(job.argv[2]).read_bytes())
                self.assertNotIn('control_binding', request)
                status = json.loads(Path(request['status_path']).read_bytes())
                self.assertEqual((status['state'], status['cli_exit_code']), ('exited', 0))
                self.assertTrue(job.done and job.closed)
                self.assertFalse((workspace / 'output.json').exists())
