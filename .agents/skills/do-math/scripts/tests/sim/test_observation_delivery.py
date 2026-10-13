"""How observations reach the owner (``parallel.ModelCalls``, ``model_runner.ModelRunner``; layer 3), without an engine.

The calls object is the product's ``ModelCalls`` on real threads; the test
waits on events the calculation sets, never a fixed time. The runner is the
product's ``ModelRunner`` on the fake clock port, so its polling waits advance
virtual time; its provider collector is ``provider_fixtures.Adapter``.
"""
import json
from pathlib import Path
import tempfile
import threading
import unittest

from do_math.model_runner import ModelRunner
from do_math.parallel import ModelCalls
from support.provider_runs import ProviderJobs, ScriptedCLI, model_runner
from support.fakes.clock import FakeClock


class CollectionOrderTests(unittest.TestCase):
    def test_returned_result_is_collected_before_unrelated_observation_callbacks(self):
        calls = ModelCalls()
        order = []

        def continuation():
            yield
            order.append('result')
        ready = continuation()
        next(ready)
        calls.start_call(ready, lambda: {'status': 'completed'}, {}, execution_id='EX-ready').result(timeout=5)
        observed, release = threading.Event(), threading.Event()

        def observe_then_wait(on_observation):
            on_observation()
            observed.set()
            release.wait(5)
            return {'status': 'completed'}
        live = continuation()
        next(live)
        future = calls.start_call(live, observe_then_wait, {'on_observation': lambda: order.append('observation')},
                                  execution_id='EX-live')
        try:
            self.assertTrue(observed.wait(5), 'the live call did not deliver its observation')
            self.assertTrue(future.observations)
            self.assertEqual(calls.collect(), 1)
            self.assertEqual(order, ['result', 'observation'])
        finally:
            release.set()
            calls.close()


class StreamChunkTests(unittest.TestCase):
    def test_one_native_chunk_is_one_owner_transaction(self):
        from support.entry import entry
        _entry = entry()
        events = [{'type': 'item.completed', 'item': {'id': str(i), 'type': 'agent_message', 'text': str(i)}}
                  for i in range(20)]

        from support.model import codex_stream_bytes
        final = b'{"output_json":"{}"}'
        framing = [json.loads(row) for row in codex_stream_bytes(final.decode('utf-8')).splitlines()]
        # Preserve the twenty observations, with the real collector's required
        # provider start/completion and exact final-message framing in one write.
        events = framing[:2] + events + framing[2:]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            rows = [json.dumps(e).encode() + b'\n' for e in events]
            cli = ScriptedCLI(stdout=b''.join(rows), final=final)
            clock = FakeClock()
            jobs = ProviderJobs(cli, clock=clock, polls=2)
            runner = model_runner(root, jobs, clock)
            delivered = []
            result = runner.run(prompt='fixture', output_schema={}, workspace=root / 'work',
                evidence_dir=root / 'evidence', model='fixture', effort='low',
                timeout_seconds=None, on_observation=delivered.append)
            self.assertEqual(result['status'], 'completed', result)
            self.assertEqual(result['output'], {})
            self.assertEqual(len(delivered), 1, 'One buffered stream chunk must not require 20 state transactions')
            self.assertEqual(delivered[0].events, events)
            self.assertEqual(list(delivered[0].rows), rows)


if __name__ == '__main__':
    unittest.main()
