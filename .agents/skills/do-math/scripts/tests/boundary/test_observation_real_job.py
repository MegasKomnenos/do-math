"""A real Windows Job's stream reaches the owner after the Job ended (``model_runner``, ``core_engine._observe_running``).

The provider is a local Python child in a real ``WindowsJob`` that writes a
Codex stream, final and status file and exits; no model is called. The runner
is the product's ``ModelRunner``; its observation callback waits until the Job
has ended and then hands the batch to a Sim's real engine, which holds one
running execution (``support.provider_live``).
"""
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import threading
import time
import unittest

from do_math.record_schemas import RECORDS
from support.provider_live import running_execution
from support.sim import Sim, warm_template
from test_categories import test_group

setUpModule = warm_template


@test_group('resource')
@unittest.skipUnless(os.name == 'nt', 'Windows Jobs exist only on Windows')
class RealJobObservationTests(unittest.TestCase):
    def test_real_job_completion_is_observed_before_delayed_batch_application(self):
        from jsonschema import Draft202012Validator
        from do_math.codex_adapter import CLIExecution, CodexExecAdapter
        from do_math.model_runner import ModelRunner
        from do_math.observations import ObservationTracker
        from do_math.windows_job import WindowsJob

        class LocalStream(CodexExecAdapter):
            """A Codex collector whose process is a local Python child in a real Job, not the Codex CLI."""

            def start(self, request_path, *, cwd, env, **kwargs):
                request = json.loads(request_path.read_bytes())
                prompt = Path(request['prompt_path'])
                schema_bytes = Path(request['output_schema_path']).read_bytes()
                (cwd / 'schema.json').write_bytes(schema_bytes)
                schema_hash = hashlib.sha256(schema_bytes).hexdigest()
                status = {'state': 'exited', 'cli_exit_code': 0,
                    'request_sha256': hashlib.sha256(request_path.read_bytes()).hexdigest(),
                    'stdin_sha256': hashlib.sha256(prompt.read_bytes()).hexdigest(), 'schema_sha256': schema_hash}
                events = [{'type': 'thread.started', 'thread_id': 'local-test'}, {'type': 'turn.started'},
                    {'type': 'item.completed', 'item': {'id': 'final', 'type': 'agent_message', 'text': '{"ok":true}'}},
                    {'type': 'turn.completed', 'usage': {}}]
                payload = {request['stdout_path']: ''.join(json.dumps(e) + '\n' for e in events),
                    request['stderr_path']: '', request['final_path']: '{"ok":true}',
                    request['status_path']: json.dumps(status)}
                script = ('import json,sys; from pathlib import Path; '
                          '[(Path(p).write_bytes(v.encode())) for p,v in json.loads(sys.argv[1]).items()]')
                argv = (sys.executable, '-B', '-c', script, json.dumps(payload))
                job = WindowsJob(argv, cwd=cwd, env=os.environ)
                return CLIExecution(status['request_sha256'], status['stdin_sha256'], argv,
                    Path(request['stdout_path']), Path(request['stderr_path']), Path(request['final_path']),
                    Path(request['status_path']), job, schema_hash, request_path.read_bytes(), prompt.read_bytes())
        sim = Sim.activated()
        workspace = running_execution(sim, 'EX-real', 'research_work')
        tracker = ObservationTracker('EX-real', workspace, {'observation_mode': 'periodic',
                                                            'observation_interval_seconds': 1}, time_port=sim.ports.clock)
        tracker.last_review -= 600  # a periodic review would be long due if the stream were live

        def delayed(batch):
            # Apply the batch only after the Job has ended: poll the runner's own termination check, bounded.
            deadline = time.monotonic() + 10
            while not batch.is_terminated() and time.monotonic() < deadline:
                threading.Event().wait(.01)
            self.assertTrue(batch.is_terminated())
            sim.engine._observe_running('EX-real', tracker, batch)
        before = set(sim.runtime.get('observation_facts', {}))
        runner = ModelRunner(clock=sim.ports.clock, environment=sim.environment, host_id=sim.host_id, jobs=sim.ports.jobs)
        runner.adapters['codex'] = LocalStream('local-fixture', jobs=sim.ports.jobs, clock=sim.ports.clock)
        with tempfile.TemporaryDirectory() as directory:
            result = runner.run(prompt='Local stream fixture, no model.', output_schema={'type': 'object'},
                workspace=workspace, evidence_dir=Path(directory) / 'evidence', model='fixture', effort='low',
                timeout_seconds=15, on_observation=delayed)
        self.assertEqual(result['status'], 'completed', result.get('error'))
        self.assertEqual(result['output'], {'ok': True})
        self.assertTrue(result['execution']['collect']['termination_barrier']['confirmed'])
        self.assertFalse(any(a['role'] == 'operational_review' for a in sim.runtime['queue']))
        # Every fact the run wrote, of any execution: exactly four, all of this execution, all valid.
        facts = [fact for key, fact in sim.runtime['observation_facts'].items() if key not in before]
        self.assertEqual([fact['execution_id'] for fact in facts], ['EX-real'] * 4)
        for fact in facts:
            Draft202012Validator(RECORDS['observation_facts']).validate(fact)


if __name__ == '__main__':
    unittest.main()
