"""Native Claude events: the collector's stream parse (``claude_stream``, layer 1) and progress observation.

A Claude print stream proves its own completion: one session, a start before
any work, exactly one terminal result, and nothing unreadable after it. The
events inside a call also feed the progress tracker (``observations``, layer
2) as tools pending and completed and as observed facts.
"""
import json
from pathlib import Path
import tempfile
import unittest

from do_math.claude_stream import parse_stream
from do_math.observations import ObservationTracker
from support.provider_inputs import CLAUDE_INIT, CLAUDE_RESULT, claude_stream
from support.observation_inputs import observe


class StreamTests(unittest.TestCase):
    def test_native_success_extracts_structured_output_and_usage(self):
        parsed = parse_stream(claude_stream(CLAUDE_INIT, {"type": "rate_limit_event"}, CLAUDE_RESULT))
        self.assertTrue(parsed["parse_complete"])
        self.assertTrue(parsed["turn_completed"])
        self.assertEqual(parsed["structured_output"], {"ok": True})
        self.assertEqual(parsed["usage"], [CLAUDE_RESULT["usage"]])

    def test_rate_notification_can_precede_init_but_work_cannot(self):
        # Observed with Claude 2.1.274 while connecting scholarly MCP.
        notification = {"type": "rate_limit_event", "session_id": "session-one"}
        self.assertTrue(parse_stream(claude_stream(notification, CLAUDE_INIT, CLAUDE_RESULT))["parse_complete"])
        for events, error in ((({"type": "assistant"}, CLAUDE_INIT, CLAUDE_RESULT), "work_before_session_start"),
                              (({**notification, "session_id": "other"}, CLAUDE_INIT, CLAUDE_RESULT), "session_mismatch"),
                              (({**CLAUDE_INIT, "session_id": 7}, {**CLAUDE_RESULT, "session_id": 7}),
                               "invalid_session_start")):
            with self.subTest(events=events):
                parsed = parse_stream(claude_stream(*events))
                self.assertFalse(parsed["parse_complete"])
                self.assertIn(error, parsed["unknown_events"])

    def test_error_truncation_duplicate_terminal_and_session_mismatch_fail(self):
        for raw in (claude_stream(CLAUDE_INIT), claude_stream(CLAUDE_INIT, CLAUDE_RESULT, CLAUDE_RESULT),
                    claude_stream(CLAUDE_INIT, CLAUDE_RESULT) + b'{"type":',
                    claude_stream(CLAUDE_INIT, {**CLAUDE_RESULT, "session_id": "another"}),
                    claude_stream(CLAUDE_RESULT), claude_stream(CLAUDE_INIT, CLAUDE_RESULT, {"type": "assistant"})):
            with self.subTest(raw=raw):
                self.assertFalse(parse_stream(raw)["parse_complete"])
        parsed = parse_stream(claude_stream(CLAUDE_INIT, {**CLAUDE_RESULT, "subtype": "error_max_turns", "is_error": True}))
        self.assertTrue(parsed["turn_failed"])
        self.assertFalse(parsed["turn_completed"])


class ProgressTests(unittest.TestCase):
    def test_claude_tools_and_messages_feed_progress_observation(self):
        from support.entry import entry
        _entry = entry()
        with tempfile.TemporaryDirectory() as d:
            tracker = ObservationTracker("one", Path(d), {"observation_mode": "periodic", "research_self_checks": False}, time_port=_entry.ports.clock)
            facts = observe(tracker, {"type": "assistant", "message": {"content": [
                {"type": "text", "text": "Checking the computation."},
                {"type": "tool_use", "id": "tool-one", "name": "Bash", "input": {"command": "python proof.py"}}]}})
            self.assertIn("tool-one", tracker.pending_tools)
            observe(tracker, {"type": "user", "message": {"content": [
                {"type": "tool_result", "tool_use_id": "tool-one", "content": "verified"}]}})
            self.assertEqual(tracker.completed_call_ids, {"tool-one"})
            self.assertFalse(tracker.pending_tools)
            fact = next(row for row in facts if row["kind"] == "observation_fact")
            self.assertIn("Checking the computation.", json.dumps(fact))


if __name__ == "__main__":
    unittest.main()
