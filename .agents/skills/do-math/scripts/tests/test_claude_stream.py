"""Invocation boundaries, continuation failures, and native quota evidence."""
from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math.claude_stream import parse_stream, provider_limit
from do_math.claude_adapter import ClaudePrintAdapter


INIT = {"type": "system", "subtype": "init", "session_id": "one"}
RESULT = {"type": "result", "subtype": "success", "is_error": False, "session_id": "one",
          "num_turns": 2, "usage": {"input_tokens": 3, "output_tokens": 7},
          "modelUsage": {"claude-opus-5": {"outputTokens": 7}}, "total_cost_usd": .1,
          "structured_output": {"summary": "computation pending"}}


def stream(*events):
    return b"".join(json.dumps(e).encode() + b"\n" for e in events)


def notification(**changes):
    return {**deepcopy(RESULT), "origin": {"kind": "task-notification"}, **changes}


def noop():
    result = notification(num_turns=0, usage={"input_tokens": 0, "output_tokens": 0})
    result.pop("structured_output")
    return result


class StreamTests(unittest.TestCase):
    def test_native_usage_metadata_fits_the_execution_storage_contract(self):
        from jsonschema import Draft202012Validator, ValidationError
        from do_math.engine import json_safe
        from do_math.record_schemas import RECORDS
        from test_redesign_SURFACE import surface_state
        parsed = parse_stream(stream(INIT, RESULT))
        self.assertTrue(parsed['turn_completed'])
        _, runtime = surface_state()
        execution = runtime['executions']['EX-1']
        metadata = json_safe({key: parsed[key] for key in
            ('usage_segments', 'model_usage_reported', 'usage_scope', 'reported_models')})
        execution.update(metadata)
        validator = Draft202012Validator(RECORDS['executions'])
        validator.validate(execution)
        restored = json.loads(json.dumps(execution))
        self.assertEqual({key: restored[key] for key in metadata}, metadata)
        with self.assertRaises(ValidationError):
            validator.validate({**execution, 'unregistered_provider_field': {}})
        for key, invalid in (('usage_segments', {}), ('model_usage_reported', []),
                             ('usage_scope', 'unknown'), ('reported_models', {})):
            with self.subTest(key=key), self.assertRaises(ValidationError):
                validator.validate({**execution, key: invalid})

    def test_three_segments_choose_correction_and_separate_usage_scopes(self):
        corrected = notification(structured_output={"summary": "computation failed; not rerun"},
            modelUsage={"claude-opus-5": {"outputTokens": 14}}, total_cost_usd=.2)
        parsed = parse_stream(stream(INIT, RESULT, INIT, noop(), INIT,
            {"type": "assistant", "session_id": "one"}, corrected))
        self.assertTrue(parsed["turn_completed"], parsed)
        self.assertEqual(parsed["structured_output"], corrected["structured_output"])
        self.assertEqual(parsed["selected_result"]["result_line"], 7)
        self.assertEqual(len(parsed["superseded_results"]), 1)
        self.assertEqual(parsed["usage_total"], {"input_tokens": 6, "output_tokens": 14})
        self.assertEqual(parsed["model_usage_reported"], corrected["modelUsage"])
        self.assertEqual(parsed["total_cost_usd"], .2)
        adapter = ClaudePrintAdapter("unused")
        self.assertEqual(adapter.validate_final(parsed, json.dumps(corrected["structured_output"]).encode()), [])
        self.assertTrue(adapter.validate_final(parsed, json.dumps(RESULT["structured_output"]).encode()))

    def test_trailing_noop_retains_submission_but_new_work_requires_submission(self):
        parsed = parse_stream(stream(INIT, RESULT, INIT, noop()))
        self.assertTrue(parsed["turn_completed"])
        self.assertEqual(parsed["selected_result"]["segment"], 0)
        for extra in ({"type": "assistant"}, {"type": "user"}, {"type": "stream_event"}):
            with self.subTest(extra=extra):
                self.assertFalse(parse_stream(stream(INIT, RESULT, INIT, extra, noop()))["turn_completed"])
        changed = noop()
        changed["usage"]["output_tokens"] = 1
        self.assertFalse(parse_stream(stream(INIT, RESULT, INIT, changed))["turn_completed"])

    def test_later_failure_or_truncation_cannot_fall_back_to_old_success(self):
        bad = notification(subtype="error_during_execution", is_error=True)
        cases = (stream(INIT, RESULT, INIT, bad), stream(INIT, RESULT, INIT),
                 stream(INIT, RESULT, INIT, notification())[:-1],
                 stream(INIT, RESULT) + b'{"type":',
                 stream(INIT, RESULT, RESULT),
                 stream(INIT, RESULT, INIT, RESULT),
                 stream(INIT, RESULT, {**INIT, "session_id": "other"}, notification()))
        for raw in cases:
            with self.subTest(raw=raw):
                parsed = parse_stream(raw)
                self.assertFalse(parsed["turn_completed"])
                self.assertNotIn("structured_output", parsed)

    def test_duplicate_keys_nonfinite_and_overflow_are_invalid(self):
        for raw in (b'{"type":"result","type":"system"}\n',
                    b'{"type":"result","usage":NaN}\n',
                    b'{"type":"result","usage":1e999}\n'):
            self.assertFalse(parse_stream(stream(INIT) + raw)["parse_complete"])

    def test_only_native_admission_rejection_is_provider_failure(self):
        failure = {**RESULT, "subtype": "error_during_execution", "is_error": True}
        for status in ("allowed", "allowed_warning", "rejected"):
            rate = {"type": "rate_limit_event", "rate_limit_info": {"status": status,
                "overageStatus": "rejected", "resetsAt": 1789705200, "rateLimitType": "five_hour",
                "unifiedWindows": {"seven_day": {"utilization": 1.0, "resetsAt": 1789729200}}}}
            limit = provider_limit(parse_stream(stream(rate, INIT, failure)))
            if status == "rejected":
                self.assertEqual(limit["retry_at"], "2026-09-18T11:00:00+00:00")
                self.assertEqual(limit["evidence_line"], 1)
            else:
                self.assertIsNone(limit)
        tool = {"type": "user", "message": {"content": [{"type": "tool_result", "content": "429 rejected"}]}}
        self.assertIsNone(provider_limit(parse_stream(stream(INIT, tool, failure))))
        self.assertIsNone(provider_limit(parse_stream(stream(rate, INIT, RESULT))))

    def test_all_reported_models_survive_last_segment_overwrite(self):
        first = {**RESULT, "modelUsage": {"other-model": {"outputTokens": 1}}}
        parsed = parse_stream(stream(INIT, first, INIT, notification()))
        self.assertEqual(parsed["reported_models"], ["claude-opus-5", "other-model"])

    def test_native_terminal_cleanup_preserves_partial_submission_and_stop_evidence(self):
        events = [{"type": "system", "subtype": "background_tasks_changed", "tasks": []},
                  {"type": "system", "subtype": "task_updated", "task_id": "job", "patch": {"status": "killed"}},
                  {"type": "system", "subtype": "task_notification", "task_id": "job", "status": "stopped"}]
        parsed = parse_stream(stream(INIT, RESULT, *events))
        self.assertTrue(parsed["turn_completed"])
        self.assertEqual(len(parsed["post_result_events"]), 3)
        for status in ("failed", "completed"):
            self.assertFalse(parse_stream(stream(INIT, RESULT, {**events[-1], "status": status}))["turn_completed"])


if __name__ == "__main__":
    unittest.main()
