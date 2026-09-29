"""Live observation of running executions: collected events, self-check obligations and observation rules.

Provider streams and model answers are fixtures. The observation tracker,
its transport, the owner that applies observations and their publication are
the product's.
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import create_autospec

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from engine_fixtures import routing_engine


class ReviewDialogueObservationTests(unittest.TestCase):
    def test_review_public_dialogue_keeps_raw_row_order_and_retries_after_failed_cas(self):
        from do_math.observations import ObservationTracker
        from do_math.observation_transport import ObservationBatch
        engine = routing_engine()
        engine._controls = create_autospec(engine._controls); engine._check_conversations = create_autospec(engine._check_conversations, return_value=False)
        engine._record_review_observation = create_autospec(engine._record_review_observation)
        engine.runtime["executions"]["EX-review"] = {"id": "EX-review", "action": {"role": "identity_review", "review_cycle_id": "RC-one"}}
        with tempfile.TemporaryDirectory() as temporary:
            engine.instance["workspace"] = temporary
            path = Path(temporary) / "runs/EX-review/evidence/stdout.jsonl"
            path.parent.mkdir(parents=True)
            event = {"type": "item.completed", "item": {"type": "agent_message", "text": "Visible independent judgment"}}
            row = json.dumps(event).encode() + b"\n"
            tail = {"type": "item.completed", "item": {"type": "agent_message", "text": "Final unterminated public message"}}
            tail_row = json.dumps(tail).encode()
            path.write_bytes(b"\n" + row + tail_row)

            def batch(event, start, raw, first_row):
                # The runner's batch carries the exact row bytes and their stream row number.
                return ObservationBatch([event], [(start, start + len(raw))], [raw], first_row,
                    "2026-09-25T00:00:00Z", 1.0, start + len(raw), path, lambda: False)
            tracker = ObservationTracker("EX-review", Path(temporary), {"observation_mode": "deadline_only", "research_self_checks": False})
            engine._save = create_autospec(engine._save, side_effect=ValueError("CAS failed"))
            with self.assertRaisesRegex(ValueError, "CAS"):
                engine._observe_running("EX-review", tracker, batch(event, 1, row, 0))
            engine._save.side_effect = None
            engine._observe_running("EX-review", tracker, batch(event, 1, row, 0))
            call = engine._record_review_observation.call_args
            self.assertEqual(call.args, ("EX-review", event))
            self.assertEqual(call.kwargs["event_index"], 0)
            self.assertEqual(engine._save.call_args.args[0][call.kwargs["artifact_ref"]], row)
            # After the Job ends the runner delivers the unterminated last row with the next number.
            engine._observe_running("EX-review", tracker, batch(tail, 1 + len(row), tail_row, 1))
            call = engine._record_review_observation.call_args
            self.assertEqual(call.args, ("EX-review", tail))
            self.assertEqual(call.kwargs["event_index"], 1)
            self.assertEqual(engine._save.call_args.args[0][call.kwargs["artifact_ref"]], tail_row)


if __name__ == "__main__":
    unittest.main()
