"""The provider gate must change engine recovery, not only report a timestamp."""
from pathlib import Path
import json
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math.engine import ResearchEngine, initialize, control
from do_math import scheduled_operator
from test_engine import common, context_from


class QuotaRunner:
    def __init__(self):
        self.calls = []

    def run(self, **arguments):
        context = context_from(arguments["prompt"])
        self.calls.append(context)
        arguments["on_started"]({"pid": 1})
        if len(self.calls) == 1:
            (arguments["workspace"] / "partial.txt").write_text("retained evidence", encoding="utf-8")
            return {"status": "failed", "error": "native quota", "error_kind": "provider_limit",
                "failure": {"kind": "provider_limit", "provider": "claude", "retry_at": None,
                            "limit_windows": [], "evidence_ref": "stdout.jsonl"}, "usage": {}, "output": None}
        return {"status": "completed", "output": common(context["action"]["role"]), "usage": {}}


class RecoveryTests(unittest.TestCase):
    def test_quota_preserves_original_action_without_diagnostic_calls_then_restores_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repository = root / "repository"
            repository.mkdir()
            subprocess.run(["git", "-C", str(repository), "init", "-q"], check=True)
            instance = initialize(repository, goal="provider recovery", workspace=root / "workspace",
                config={"model": "claude-opus-5", "scholarly_enabled": False, "operator_enabled": False,
                        "run_timeout_seconds": 120, "max_cycles": 1})
            runner = QuotaRunner()
            engine = ResearchEngine(repository, instance["instance_id"], runner=runner)
            engine.run(max_steps=2)
            self.assertEqual(len(runner.calls), 1)
            self.assertFalse(any(e["role"] == "operational_review" for e in engine.runtime["executions"].values()))
            waiting = list(engine.runtime["waiting_actions"].values())
            self.assertEqual([row["failure_kind"] for row in waiting], ["provider_limit"])
            self.assertFalse(engine.runtime["questions"])
            current = time.time()
            with patch("do_math.session_slots.time.time", return_value=current + 301):
                engine.run(max_steps=1)
            self.assertEqual(len(runner.calls), 2)
            self.assertTrue(any(row["path"] == "partial.txt" for row in runner.calls[1]["previous_output_files"]))
            self.assertNotIn(waiting[0]["action"]["id"], engine.runtime["waiting_actions"])

    def test_wake_keeps_hold_and_user_pause_and_only_requests_engine(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            status = {"status": "waiting", "pending_actions": 1,
                      "provider_waits": {"providers": {"claude": {"due": True}}}}
            with patch.object(scheduled_operator, "read_status", return_value=status), \
                 patch.object(scheduled_operator, "schedule", return_value={}) as schedule:
                self.assertEqual(scheduled_operator.wake(root, "I", root)["outcome"], "engine_requested")
                schedule.assert_called_once_with("start-engine", repository=root, instance="I", workspace=root)
                schedule.reset_mock()
                status["user_pause"] = {"reason": "stop"}
                self.assertEqual(scheduled_operator.wake(root, "I", root)["outcome"], "paused")
                schedule.assert_not_called()
                scheduled_operator.hold(root, reason="keep stopped")
                self.assertEqual(scheduled_operator.wake(root, "I", root)["outcome"], "held")
                schedule.assert_not_called()


if __name__ == "__main__":
    unittest.main()
