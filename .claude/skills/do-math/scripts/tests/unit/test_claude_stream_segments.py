"""Native Claude invocation segments (``claude_stream``, layer 1): boundaries, continuations, usage and quota evidence.

The parser reads a Claude ``stream-json`` stdout as segments that open with
``system/init`` and close with ``result``; only a same-session
task-notification continues a finished segment. The inputs are JSONL bytes
(``provider_fixtures.claude_stream``). A stream the parser does not complete
names its reason in ``unknown_events``; the negative tests fix that reason.
"""
from copy import deepcopy
import json
import unittest

from jsonschema import Draft202012Validator, ValidationError

from do_math.claude_adapter import ClaudePrintAdapter
from do_math.claude_stream import parse_stream, provider_limit
from do_math.payloads import json_safe
from do_math.record_schemas import RECORDS
from provider_fixtures import claude_stream as stream

INIT = {"type": "system", "subtype": "init", "session_id": "one"}
RESULT = {"type": "result", "subtype": "success", "is_error": False, "session_id": "one",
          "num_turns": 2, "usage": {"input_tokens": 3, "output_tokens": 7},
          "modelUsage": {"claude-opus-5": {"outputTokens": 7}}, "total_cost_usd": .1,
          "structured_output": {"summary": "computation pending"}}
METADATA = ('usage_segments', 'model_usage_reported', 'usage_scope', 'reported_models')


def notification(**changes):
    """A result that continues the session as a task notification (the only supported continuation)."""
    return {**deepcopy(RESULT), "origin": {"kind": "task-notification"}, **changes}


def noop():
    """A continuation that did no work: zero turns, zero usage and no submission."""
    result = notification(num_turns=0, usage={"input_tokens": 0, "output_tokens": 0})
    result.pop("structured_output")
    return result


class UsageStorageTests(unittest.TestCase):
    def test_native_usage_metadata_fits_the_execution_storage_contract(self):
        from record_fixtures import surface_state
        parsed = parse_stream(stream(INIT, RESULT))
        self.assertTrue(parsed['turn_completed'])
        _, runtime = surface_state()
        execution = runtime['executions']['EX-1']
        metadata = json_safe({key: parsed[key] for key in METADATA})
        execution.update(metadata)
        validator = Draft202012Validator(RECORDS['executions'])
        validator.validate(execution)
        restored = json.loads(json.dumps(execution))
        self.assertEqual({key: restored[key] for key in metadata}, metadata)
        with self.assertRaisesRegex(ValidationError, r"Additional properties are not allowed "
                                                     r"\('unregistered_provider_field' was unexpected\)"):
            validator.validate({**execution, 'unregistered_provider_field': {}})
        for key, invalid, message in (('usage_segments', {}, r"\{\} is not of type 'array'"),
                                      ('model_usage_reported', [], r"\[\] is not of type 'object'"),
                                      ('usage_scope', 'unknown', r"'unknown' is not of type 'object'"),
                                      ('reported_models', {}, r"\{\} is not of type 'array'")):
            with self.subTest(key=key), self.assertRaisesRegex(ValidationError, message) as refused:
                validator.validate({**execution, key: invalid})
            self.assertEqual(list(refused.exception.path), [key])


class SegmentTests(unittest.TestCase):
    def test_three_segments_choose_correction_and_separate_usage_scopes(self):
        corrected = notification(structured_output={"summary": "computation failed; not rerun"},
                                 modelUsage={"claude-opus-5": {"outputTokens": 14}}, total_cost_usd=.2)
        parsed = parse_stream(stream(INIT, RESULT, INIT, noop(), INIT,
                                     {"type": "assistant", "session_id": "one"}, corrected))
        self.assertTrue(parsed["turn_completed"], parsed)
        self.assertEqual(parsed["structured_output"], corrected["structured_output"])
        self.assertEqual(parsed["selected_result"]["result_line"], 7)
        self.assertEqual(len(parsed["superseded_results"]), 1)
        self.assertEqual(parsed["superseded_results"][0]["segment"], 0)
        # Segment counters add up (3+0+3, 7+0+7); the cumulative modelUsage is not added.
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
                worked = parse_stream(stream(INIT, RESULT, INIT, extra, noop()))
                self.assertFalse(worked["turn_completed"])
                self.assertEqual(worked["unknown_events"], ["segment_submission_missing"])
        changed = noop()
        changed["usage"]["output_tokens"] = 1
        counted = parse_stream(stream(INIT, RESULT, INIT, changed))
        self.assertFalse(counted["turn_completed"])
        self.assertEqual(counted["unknown_events"], ["segment_submission_missing"])

    def test_later_failure_or_truncation_cannot_fall_back_to_old_success(self):
        bad = notification(subtype="error_during_execution", is_error=True)
        cases = (("later failure", stream(INIT, RESULT, INIT, bad), []),
                 ("unfinished last segment", stream(INIT, RESULT, INIT), ["terminal_missing"]),
                 ("truncated last row", stream(INIT, RESULT, INIT, notification())[:-1],
                  ["incomplete_jsonl_line", "terminal_missing"]),
                 ("truncated tail", stream(INIT, RESULT) + b'{"type":', ["incomplete_jsonl_line"]),
                 ("second terminal without init", stream(INIT, RESULT, RESULT), ["event_after_terminal_without_init"]),
                 ("continuation without origin", stream(INIT, RESULT, INIT, RESULT), ["unsupported_continuation"]),
                 ("other session", stream(INIT, RESULT, {**INIT, "session_id": "other"}, notification()),
                  ["session_mismatch"]))
        for name, raw, errors in cases:
            with self.subTest(case=name):
                parsed = parse_stream(raw)
                self.assertFalse(parsed["turn_completed"])
                self.assertNotIn("structured_output", parsed)
                self.assertEqual(parsed["unknown_events"], errors)
                if not errors:
                    # A failed later segment is a failure mark, not a parse error.
                    self.assertTrue(parsed["turn_failed"])

    def test_duplicate_keys_nonfinite_and_overflow_are_invalid(self):
        for raw in (b'{"type":"result","type":"system"}\n',
                    b'{"type":"result","usage":NaN}\n',
                    b'{"type":"result","usage":1e999}\n'):
            with self.subTest(raw=raw):
                parsed = parse_stream(stream(INIT) + raw)
                self.assertFalse(parsed["parse_complete"])
                self.assertEqual(parsed["unknown_events"], ["invalid_jsonl", "terminal_missing"])

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
        self.assertEqual(parsed["structured_output"], RESULT["structured_output"])
        self.assertEqual(len(parsed["post_result_events"]), 3)
        for status in ("failed", "completed"):
            with self.subTest(status=status):
                other = parse_stream(stream(INIT, RESULT, {**events[-1], "status": status}))
                self.assertFalse(other["turn_completed"])
                self.assertEqual(other["unknown_events"], ["event_after_terminal_without_init"])


class ProviderLimitTests(unittest.TestCase):
    def test_only_native_admission_rejection_is_provider_failure(self):
        failure = {**RESULT, "subtype": "error_during_execution", "is_error": True}
        for status in ("allowed", "allowed_warning", "rejected"):
            rate = {"type": "rate_limit_event", "rate_limit_info": {"status": status,
                    "overageStatus": "rejected", "resetsAt": 1789705200, "rateLimitType": "five_hour",
                    "unifiedWindows": {"seven_day": {"utilization": 1.0, "resetsAt": 1789729200}}}}
            with self.subTest(status=status):
                limit = provider_limit(parse_stream(stream(rate, INIT, failure)))
                if status == "rejected":
                    # The later of the two windows (seven days, utilization 1.0) sets the retry time.
                    self.assertEqual(limit["retry_at"], "2026-09-18T11:00:00+00:00")
                    self.assertEqual(limit["evidence_line"], 1)
                else:
                    self.assertIsNone(limit)
        tool = {"type": "user", "message": {"content": [{"type": "tool_result", "content": "429 rejected"}]}}
        self.assertIsNone(provider_limit(parse_stream(stream(INIT, tool, failure))))
        # ``rate`` is the rejected admission event; a completed turn is still not a provider failure.
        self.assertIsNone(provider_limit(parse_stream(stream(rate, INIT, RESULT))))


if __name__ == "__main__":
    unittest.main()
