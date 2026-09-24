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
    def test_claude_lock_in_pinned_profile_keeps_codex_request_valid(self):
        from do_math import codex_worker, execution_profiles
        from test_model_runner import Adapter
        config = {**DEFAULT_CONFIG, "claude_only_assigned_model": True,
                  "scholarly_enabled": False}
        profile = next(p for p in execution_profiles.build_profiles(config)["execution_profiles"].values()
                       if p["role"] == "maintenance")
        self.assertTrue(profile["ai"]["claude_only_assigned_model"])
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            workspace = root / "workspace"
            workspace.mkdir()
            runner = model_runner.ModelRunner(codex_path="fixture-cli")
            runner.codex._adapter = Adapter({"result": "output_collected",
                                            "final": {"raw": b"{}"}, "jsonl": {}})
            prompt = execution_profiles.prepare_prompt("fixture", profile)
            result = runner.run(model=profile["ai"]["model"], effort=profile["ai"]["effort"],
                prompt=prompt, output_schema={}, workspace=workspace, evidence_dir=root / "evidence",
                timeout_seconds=1, execution_id="EX-codex-lock", profile=profile,
                input_seal=execution_profiles.prompt_seal(prompt), claude_only_assigned_model=True)
            request = codex_worker.load_request(root / "evidence/request.json")
            self.assertNotIn("claude_only_assigned_model", request)
            self.assertEqual(request["profile_ref"], execution_profiles.profile_ref(profile))
            self.assertEqual(result["status"], "completed")

    def test_model_lock_is_opt_in_and_reaches_only_claude(self):
        from do_math.engine import ResearchEngine
        from types import SimpleNamespace
        from do_math.execution_profiles import build_profiles
        pinned = {**DEFAULT_CONFIG, "claude_only_assigned_model": True, "scholarly_enabled": False}
        profile = next(p for p in build_profiles(pinned)["execution_profiles"].values() if p["role"] == "maintenance")
        arguments = {"profile": profile}
        runner_context = SimpleNamespace(runner=Mock(), instance={"config": {
            **DEFAULT_CONFIG, "claude_only_assigned_model": False, "scholarly_enabled": True}})
        ResearchEngine._runner_tools(runner_context, arguments)
        self.assertTrue(arguments["claude_only_assigned_model"])
        self.assertFalse(DEFAULT_CONFIG["claude_only_assigned_model"])
        with self.assertRaises(ValueError):
            validate_config({"claude_only_assigned_model": "true"})
        runner = model_runner.ModelRunner()
        runner.claude = Mock()
        runner.codex = Mock()
        runner.run(model="claude-opus-5", claude_only_assigned_model=True)
        runner.claude.run.assert_called_once_with(model="claude-opus-5", claude_only_assigned_model=True)
        runner.run(model="gpt-5.6-sol", claude_only_assigned_model=True)
        runner.codex.run.assert_called_once_with(model="gpt-5.6-sol")
        worker = self.module("claude_worker")
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "schema.json"
            path.write_text('{"type":"object"}', encoding="utf-8")
            request = {"claude_path": "claude.exe", "model": "claude-opus-5", "effort": "high",
                       "cwd": d, "output_schema_path": str(path)}
            argv = worker.build_argv(request)
            settings = json.loads(argv[argv.index("--settings") + 1])
            self.assertNotIn("availableModels", settings)
            request["claude_only_assigned_model"] = True
            argv = worker.build_argv(request)
            settings = json.loads(argv[argv.index("--settings") + 1])
            self.assertEqual(settings["availableModels"], ["claude-opus-5"])
            self.assertEqual(settings["fallbackModel"], [])
            self.assertFalse(settings["switchModelsOnFlag"])
            self.assertEqual(settings["env"]["CLAUDE_CODE_SUBAGENT_MODEL"], "claude-opus-5")
            self.assertEqual(settings["env"]["CLAUDE_CODE_SUBAGENT_MODEL_FORCE"], "1")
            self.assertEqual(settings["env"]["ANTHROPIC_DEFAULT_HAIKU_MODEL"], "claude-opus-5")

    def test_role_schemas_reach_claude_without_unsupported_meta_schema(self):
        from do_math.contracts import ROLES, schema_for
        from jsonschema import Draft7Validator
        worker = self.module("claude_worker")
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "schema.json"
            for role in ROLES:
                with self.subTest(role=role):
                    original = schema_for(role)
                    raw = json.dumps(original)
                    path.write_text(raw, encoding="utf-8")
                    args = worker.build_argv({"claude_path": "claude.exe", "model": "claude-opus-5",
                        "effort": "high", "cwd": d, "output_schema_path": str(path)})
                    sent = json.loads(args[args.index("--json-schema") + 1])
                    self.assertEqual(sent, {k: v for k, v in original.items() if k not in {"$schema", "x-contract-id"}})
                    Draft7Validator.check_schema(sent)
                    self.assertFalse(Draft7Validator(sent).is_valid({}))
                    self.assertEqual(path.read_text(encoding="utf-8"), raw)

    def test_claude_tools_and_messages_feed_progress_observation(self):
        with tempfile.TemporaryDirectory() as d:
            tracker = ObservationTracker("one", Path(d), {"observation_mode": "periodic", "research_self_checks": False})
            facts = tracker.observe({"type": "assistant", "message": {"content": [
                {"type": "text", "text": "Checking the computation."},
                {"type": "tool_use", "id": "tool-one", "name": "Bash", "input": {"command": "python proof.py"}}]}})
            self.assertIn("tool-one", tracker.pending_tools)
            tracker.observe({"type": "user", "message": {"content": [
                {"type": "tool_result", "tool_use_id": "tool-one", "content": "verified"}]}})
            self.assertEqual(tracker.completed_call_ids, {"tool-one"})
            self.assertFalse(tracker.pending_tools)
            fact = next(row for row in facts if row["kind"] == "observation_fact")
            self.assertIn("Checking the computation.", json.dumps(fact))

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
        from do_math.execution_profiles import build_profiles
        state = {**build_profiles(config), "config": config}
        runtime = {"executions": {}, "reservations": {}}
        with tempfile.TemporaryDirectory() as d:
            slots = SessionSlots( runtime=runtime, instance=state)
            def acquire(eid, pool, model):
                role = "research_work" if pool == "work" else "research_plan"
                profile = next(p for p in state["execution_profiles"].values()
                               if p["role"] == role and p.get("ai", {}).get("model") == model)
                return slots.acquire(eid, pool, model, profile=profile, execution={"id": eid, "role": role})
            self.assertTrue(acquire("one", "work", "claude:opus"))
            self.assertFalse(acquire("two", "work", "claude:opus"))
            self.assertTrue(acquire("three", "operations", "claude:opus"))
            self.assertTrue(acquire("four", "work", "gpt-5.6-sol"))
            self.assertTrue(slots.release("one"))
            self.assertTrue(acquire("two", "work", "claude:opus"))
            slots.close()


if __name__ == "__main__":
    unittest.main()
