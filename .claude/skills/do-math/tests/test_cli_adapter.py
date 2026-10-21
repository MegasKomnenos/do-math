"""Small synthetic records derived from CLI implementations, not live limits."""

from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import sys
import tempfile
import tomllib
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from cli_adapter import build_command, detect_usage_limit, provider_for_model


KST = timezone(timedelta(hours=9))
NOW = datetime(2026, 10, 21, 18, 0, tzinfo=KST).timestamp()


def refusal(info=None):
    return {"type": "assistant", "is_api_error_message": True,
            "api_error": "usage_limit_reached",
            "api_error_params": {"rate_limit_info": info}}


class AdapterTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.out = self.root / "stdout.jsonl"
        self.err = self.root / "stderr.log"

    def detect(self, provider, rows, *, stderr=b"", **kwargs):
        self.out.write_bytes("\n".join(
            row if isinstance(row, str) else json.dumps(row) for row in rows
        ).encode("utf-8"))
        self.err.write_bytes(stderr)
        return detect_usage_limit(provider, self.out, self.err, now=NOW,
                                  fallback_seconds=600, local_timezone=KST, **kwargs)

    def test_commands_preserve_paths_and_explicit_selection(self):
        workdir = self.root / "연구 세션"
        codex = build_command(self.root / "program files" / "codex.exe",
                              "codex/gpt-6.1-sol", "high", workdir)
        self.assertEqual(codex.provider, "codex")
        self.assertEqual(codex.argv[0], str(self.root / "program files" / "codex.exe"))
        self.assertEqual(codex.argv[codex.argv.index("--cd") + 1], str(workdir.resolve()))
        self.assertEqual(codex.argv[-1], "-")
        configs = [codex.argv[i + 1] for i, arg in enumerate(codex.argv) if arg == "-c"]
        self.assertEqual(tomllib.loads("\n".join(configs)),
                         {"model_reasoning_effort": "high", "approval_policy": "never"})
        self.assertEqual(codex.argv[codex.argv.index("--model") + 1], "gpt-6.1-sol")
        claude = build_command("claude.exe", "claude/sonnet", "max", workdir)
        self.assertEqual(claude.provider, "claude")
        self.assertEqual(claude.cwd, workdir.resolve())
        self.assertEqual(claude.argv[claude.argv.index("--effort") + 1], "max")
        self.assertIn("--verbose", claude.argv)
        self.assertNotIn("--bare", claude.argv)
        self.assertEqual(claude.argv[claude.argv.index("--model") + 1], "sonnet")
        for model in ("claude/opus", "claude/fable", "claude/claude-sonnet-example"):
            self.assertEqual(provider_for_model(model), "claude")
        for model in ("unmapped-model", "gpt-6.1-sol", "sonnet", "codex/", "claude/ "):
            with self.assertRaises(ValueError):
                provider_for_model(model)
        custom = build_command("codex.exe", "codex/vendor/model", "high", workdir)
        self.assertEqual(custom.argv[custom.argv.index("--model") + 1], "vendor/model")
        with self.assertRaises(ValueError):
            build_command("claude.exe", "claude/sonnet", "ultra", workdir)

    def test_codex_explicit_date_and_stderr(self):
        message = "You’ve hit your usage limit. Try again at Oct 22nd, 2026 7:11 PM."
        limit = self.detect("codex", [], stderr=json.dumps(
            {"type": "turn.failed", "error": {"message": message}}
        ).encode())
        self.assertEqual(limit.retry_at, datetime(2026, 10, 22, 19, 11, tzinfo=KST).timestamp())
        self.assertEqual(limit.source, "provider")

    def test_codex_time_only_requires_same_date_session(self):
        rows = [{"type": "error", "message":
                 "You've hit your usage limit for GPT. Switch models, or try again at 7:11 PM."}]
        known = self.detect("codex", rows, session_started_at=NOW - 60)
        self.assertEqual(known.retry_at, NOW + 71 * 60)
        for started in (None, NOW - 24 * 3600):
            with self.subTest(started=started):
                limit = self.detect("codex", rows, session_started_at=started)
                self.assertEqual((limit.retry_at, limit.source), (NOW + 600, "fallback"))

    def test_codex_unknown_and_expired_times_keep_signal(self):
        for message in (
            "Your workspace is out of credits. Add credits to continue.",
            "You hit your spend cap set in your workspace. Increase your spend cap to continue.",
            "You’ve hit your usage limit. Try again later.",
            "You’ve hit your usage limit. Try again at Oct 20th, 2026 7:11 PM.",
            "You’ve hit your usage limit. Try again at Oct 32nd, 2026 7:11 PM.",
        ):
            with self.subTest(message=message):
                limit = self.detect("codex", [{"type": "error", "message": message}])
                self.assertEqual((limit.retry_at, limit.source), (NOW + 600, "fallback"))

    def test_claude_windows_and_ordinary_overage(self):
        info = {"status": "rejected", "rateLimitType": "five_hour",
                "resetsAt": NOW + 3600, "isUsingOverage": False,
                "unifiedWindows": {"seven_day": {"resetsAt": NOW + 86400}}}
        limit = self.detect("claude", [refusal(info)])
        self.assertEqual((limit.retry_at, limit.source), (NOW + 3600, "provider"))
        info.update(overageStatus="rejected", overageResetsAt=NOW + 1800)
        self.assertEqual(self.detect("claude", [refusal(info)]).retry_at, NOW + 1800)
        for change in ({"limitScope": "group_pool"},
                       {"overageDisabledReason": "org_level_disabled_until"},
                       {"overageResetsAt": NOW - 1}, {"isUsingOverage": True}):
            with self.subTest(change=change):
                limit = self.detect("claude", [refusal(info | change)])
                self.assertEqual((limit.retry_at, limit.source), (NOW + 600, "fallback"))

    def test_claude_bad_or_missing_info_does_not_erase_refusal(self):
        for info in (None, [], {"status": []},
                     {"status": "rejected", "rateLimitType": []},
                     *({"status": "rejected", "rateLimitType": "five_hour", "resetsAt": value}
                       for value in (None, "tomorrow", [], {}, True, float("inf"), NOW - 1, 10**400))):
            with self.subTest(info=info):
                limit = self.detect("claude", [refusal(info)])
                self.assertEqual((limit.retry_at, limit.source), (NOW + 600, "fallback"))

    def test_quotes_warnings_generic_429_and_partial_logs_are_not_limits(self):
        quote = "You've hit your usage limit. Try again at 7:11 PM."
        rows = ["plain diagnostic", "{incomplete", "[]", "null", "42",
                {"type": "item.completed", "item": {"text": quote}},
                {"type": "assistant", "message": {"content": quote}},
                {"type": "user", "message": {"content": json.dumps(refusal())}},
                {"type": "error", "message": "429 rate_limit_reached"},
                {"type": "turn.failed", "error": []},
                {"type": "assistant", "error": "rate_limit", "is_api_error_message": True},
                {"type": "assistant", "is_api_error_message": False,
                 "api_error": "usage_limit_reached"},
                *({"type": "rate_limit_event", "rate_limit_info": {"status": status,
                    "isUsingOverage": True, "overageStatus": "allowed"}}
                  for status in ("allowed", "allowed_warning", "rejected"))]
        for provider in ("codex", "claude"):
            self.assertIsNone(self.detect(provider, rows, stderr=b"\xff\nERROR: quoted text\n"))
        # Unknown and duplicate keys follow ordinary json.loads semantics.
        rows.append('{"unknown":1,"unknown":2,"type":"error",'
                    '"message":"Your workspace is out of credits."}')
        self.assertEqual(self.detect("codex", rows).source, "fallback")
        rows.append(refusal())
        self.assertEqual(self.detect("claude", rows).source, "fallback")

    def test_multiple_refusals_and_io_errors(self):
        rows = [refusal({"status": "rejected", "rateLimitType": "five_hour",
                         "resetsAt": NOW + offset}) for offset in (3600, 1800)]
        self.assertEqual(self.detect("claude", rows).retry_at, NOW + 3600)
        with self.assertRaises(FileNotFoundError):
            detect_usage_limit("claude", self.root / "missing", self.err,
                               now=NOW, fallback_seconds=600)


if __name__ == "__main__":
    unittest.main()
