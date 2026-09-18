"""Claude stream validation and routing at the same local execution boundary."""
from __future__ import annotations

import importlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import Mock
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math import model_runner
from do_math.engine import DEFAULT_CONFIG, validate_config
from do_math.model_policy import selection
from do_math.session_slots import SessionSlots
from do_math.observations import ObservationTracker


def stream(*events):
    return b"".join(json.dumps(event).encode() + b"\n" for event in events)


INIT = {"type": "system", "subtype": "init", "session_id": "session-one"}
RESULT = {"type": "result", "subtype": "success", "is_error": False,
          "session_id": "session-one", "structured_output": {"ok": True},
          "usage": {"input_tokens": 7, "output_tokens": 3}}


class ClaudeTests(unittest.TestCase):
    def test_claude_tools_and_messages_feed_progress_observation(self):
        with tempfile.TemporaryDirectory() as d:
            tracker = ObservationTracker("one", Path(d), {})
            tracker.observe({"type": "assistant", "message": {"content": [
                {"type": "text", "text": "Checking the computation."},
                {"type": "tool_use", "id": "tool-one", "name": "Bash", "input": {"command": "python proof.py"}}]}})
            self.assertIn("tool-one", tracker.pending_tools)
            tracker.observe({"type": "user", "message": {"content": [
                {"type": "tool_result", "tool_use_id": "tool-one", "content": "verified"}]}})
            self.assertEqual(tracker.tool_results, 1)
            self.assertFalse(tracker.pending_tools)
            self.assertEqual(tracker.messages[-1]["text"], "Checking the computation.")

    def test_profile_accepts_claude_provider(self):
        from do_math.cli import build_parser, CliInputError
        try:
            args = build_parser().parse_args(["profile", "--provider", "claude"])
        except CliInputError as error:
            self.fail(str(error))
        self.assertEqual(args.provider, "claude")

    def module(self, name):
        name = "do_math." + name
        self.assertIsNotNone(importlib.util.find_spec(name), "Claude CLI support is missing")
        return importlib.import_module(name)

    def test_native_success_extracts_structured_output_and_usage(self):
        adapter = self.module("claude_adapter")
        parsed = adapter.parse_jsonl(stream(INIT, {"type": "rate_limit_event"}, RESULT))
        self.assertTrue(parsed["parse_complete"])
        self.assertTrue(parsed["turn_completed"])
        self.assertEqual(parsed["structured_output"], {"ok": True})
        self.assertEqual(parsed["usage"], [RESULT["usage"]])

    def test_rate_notification_can_precede_init_but_work_cannot(self):
        adapter = self.module("claude_adapter")
        # Observed with Claude 2.1.274 while connecting scholarly MCP.
        notification = {"type": "rate_limit_event", "session_id": "session-one"}
        self.assertTrue(adapter.parse_jsonl(stream(notification, INIT, RESULT))["parse_complete"])
        for events in (({"type": "assistant"}, INIT, RESULT),
                       ({**notification, "session_id": "other"}, INIT, RESULT),
                       ({**INIT, "session_id": 7}, {**RESULT, "session_id": 7})):
            with self.subTest(events=events):
                self.assertFalse(adapter.parse_jsonl(stream(*events))["parse_complete"])

    def test_final_output_comparison_preserves_json_types_and_rejects_duplicates(self):
        adapter = self.module("claude_adapter").ClaudePrintAdapter("unused")
        parsed = {"structured_output": {"ok": True}}
        self.assertEqual(adapter.validate_final(parsed, b'{"ok":true}'), [])
        for final in (b'{"ok":1}', b'{"ok":false,"ok":true}'):
            with self.subTest(final=final):
                self.assertTrue(adapter.validate_final(parsed, final))

    def test_error_truncation_duplicate_terminal_and_session_mismatch_fail(self):
        adapter = self.module("claude_adapter")
        for raw in (stream(INIT), stream(INIT, RESULT, RESULT),
                    stream(INIT, RESULT) + b'{"type":',
                    stream(INIT, {**RESULT, "session_id": "another"}),
                    stream(RESULT), stream(INIT, RESULT, {"type": "assistant"})):
            with self.subTest(raw=raw):
                self.assertFalse(adapter.parse_jsonl(raw)["parse_complete"])
        parsed = adapter.parse_jsonl(stream(INIT, {**RESULT, "subtype": "error_max_turns", "is_error": True}))
        self.assertTrue(parsed["turn_failed"])
        self.assertFalse(parsed["turn_completed"])

    def test_worker_uses_login_stdin_schema_and_only_configured_mcp(self):
        worker = self.module("claude_worker")
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            schema = root / "schema.json"
            schema.write_text('{"type":"object"}', encoding="utf-8")
            request = {"claude_path": "claude.exe", "model": "haiku", "effort": "low",
                       "cwd": str(root), "output_schema_path": str(schema),
                       "scholarly_server": {"command": "python", "args": [str(root / "server.py")]}}
            args = worker.build_argv(request)
            self.assertEqual(args[:2], ["claude.exe", "--print"])
            self.assertIn("stream-json", args)
            self.assertNotIn("--bare", args)
            self.assertIn("--no-session-persistence", args)
            self.assertIn("--strict-mcp-config", args)
            mcp = json.loads(args[args.index("--mcp-config") + 1])
            self.assertEqual(set(mcp["mcpServers"]), {"scholarly"})
            self.assertEqual(mcp["mcpServers"]["scholarly"]["args"][-2:], ["--data-dir", str(root / "scholarly-data")])
        env = worker.sanitized_environment({"PATH": "ok", "USERPROFILE": "login", "CLAUDE_CONFIG_DIR": "config",
              "ANTHROPIC_API_KEY": "secret", "ANTHROPIC_AUTH_TOKEN": "secret", "CLAUDECODE": "1",
              "ANTHROPIC_BASE_URL": "https://elsewhere", "CLAUDE_CODE_USE_BEDROCK": "1"})
        self.assertEqual(env, {"PATH": "ok", "USERPROFILE": "login", "CLAUDE_CONFIG_DIR": "config"})

    def test_router_dispatches_claude_and_codex_without_mutating_shared_runner(self):
        self.assertTrue(hasattr(model_runner, "ModelRunner"), "provider routing is missing")
        runner = model_runner.ModelRunner()
        runner.codex = Mock()
        runner.claude = Mock()
        runner.run(model="claude:haiku", prompt="one")
        runner.run(model="gpt-5.6-sol", prompt="two")
        runner.run(model="claude-haiku-4-5-20251001", prompt="three")
        self.assertEqual(runner.claude.run.call_args_list[0].kwargs["model"], "haiku")
        self.assertEqual(runner.claude.run.call_args_list[1].kwargs["model"], "claude-haiku-4-5-20251001")
        runner.codex.run.assert_called_once_with(model="gpt-5.6-sol", prompt="two")

    def test_mixed_models_use_existing_selection_and_separate_slot_pools(self):
        config = {**DEFAULT_CONFIG, "tier_models": {"high": "claude:opus", "medium": "gpt-5.6-sol", "low": "claude:haiku"},
                  "session_limits": {pool: {"claude:opus": 1, "gpt-5.6-sol": 1, "claude:haiku": 1}
                                     for pool in ("work", "operations")}}
        validate_config(config)
        self.assertEqual(selection(config, {"role": "research_plan"}, {}, {})["model"], "claude:opus")
        self.assertEqual(selection(config, {"role": "task_contract_review"}, {}, {})["model"], "gpt-5.6-sol")
        with tempfile.TemporaryDirectory() as d:
            slots = SessionSlots(Path(d), "mixed")
            try:
                slots.configure(config["session_limits"])
                self.assertTrue(slots.acquire("one", "work", "claude:opus"))
                self.assertFalse(slots.acquire("two", "work", "claude:opus"))
                self.assertTrue(slots.acquire("three", "operations", "claude:opus"))
                self.assertTrue(slots.acquire("four", "work", "gpt-5.6-sol"))
                self.assertTrue(slots.release("one"))
                self.assertTrue(slots.acquire("two", "work", "claude:opus"))
            finally:
                slots.close()


if __name__ == "__main__":
    unittest.main()
