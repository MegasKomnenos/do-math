"""How observations reach the owner (``parallel.ModelCalls``, ``model_runner.ModelRunner``; layer 3), without an engine.

The calls object is the product's ``ModelCalls`` on real threads; the test
waits on events the calculation sets, never a fixed time. The runner is the
product's ``ModelRunner`` on the fake clock port, so its polling waits advance
virtual time. The real adapter, worker and collector use the Jobs and CLI
doubles in ``support.provider_runs``.
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
    def test_empty_stream_delivers_a_tick_before_collection_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            clock = FakeClock()
            jobs = ProviderJobs(ScriptedCLI(stdout=b'', final=b'{"output_json":"{}"}'),
                                clock=clock, polls=2)
            delivered = []
            result = model_runner(root, jobs, clock).run(
                prompt='fixture', output_schema={}, workspace=root / 'work',
                evidence_dir=root / 'evidence', model='fixture', effort='low',
                timeout_seconds=None, on_observation=delivered.append)
            self.assertEqual(result['status'], 'failed', result)
            self.assertEqual(len(delivered), 1)
            tick, = delivered
            self.assertEqual((tick.events, tick.rows, tick.first_row, tick.end_offset),
                             ([], [], 0, 0))
            self.assertTrue(tick.ends_read)
            self.assertTrue(tick.is_terminated())

    def test_native_read_parts_keep_receipt_time_and_coordinates_during_delayed_replay(self):
        from do_math.model_runner import OBSERVATION_BATCH_ROWS
        from do_math.observations import ObservationTracker
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
            self.assertEqual(len(delivered), (len(rows) + OBSERVATION_BATCH_ROWS - 1) // OBSERVATION_BATCH_ROWS)
            self.assertEqual([event for part in delivered for event in part.events], events)
            self.assertEqual([row for part in delivered for row in part.rows], rows)
            received_at, received_monotonic = clock.now(), clock.monotonic()
            self.assertEqual({part.received_at for part in delivered}, {received_at})
            self.assertEqual({part.received_monotonic for part in delivered}, {received_monotonic})
            self.assertEqual([part.ends_read for part in delivered], [False] * (len(delivered) - 1) + [True])
            self.assertEqual([part.caught_up() for part in delivered], [False] * (len(delivered) - 1) + [True])
            tracker = ObservationTracker('EX-replay', root / 'work', {
                'observation_mode': 'event_driven', 'research_self_checks': False,
                'tool_review_window_seconds': 1, 'observation_interval_seconds': 1}, time_port=clock)
            tracker.set_execution_status('ended')
            clock.advance(1000)
            position, row_number = 0, 0
            facts = []
            for part in delivered:
                self.assertTrue(part.is_terminated())
                self.assertLessEqual(len(part.events), OBSERVATION_BATCH_ROWS)
                self.assertEqual(part.first_row, row_number)
                row_number += len(part.events)
                for event, raw, (start, end) in zip(part.events, part.rows, part.offsets):
                    self.assertEqual((start, end), (position, position + len(raw)))
                    position = end
                    source = part.source(end, start_offset=start)
                    facts.extend(tracker.observe(event, source=source, live=False))
                if part.caught_up():
                    self.assertEqual(tracker.observe({'type': 'tick'}, live=False,
                        source=part.source(part.end_offset, start_offset=part.end_offset)), [])
            self.assertEqual(position, sum(map(len, rows)))
            self.assertEqual([json.loads(fact['event_json']) for fact in facts], events)
            self.assertEqual({fact['observed_at'] for fact in facts}, {clock.now()})
            self.assertEqual({fact['source']['received_at'] for fact in facts}, {received_at})
            self.assertEqual({fact['source']['received_offset_ms'] for fact in facts}, {0})
            self.assertFalse(tracker.obligations)


if __name__ == '__main__':
    unittest.main()
