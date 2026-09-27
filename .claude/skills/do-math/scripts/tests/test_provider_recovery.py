"""The provider gate must change engine recovery, not only report a timestamp."""
from pathlib import Path
import sys
import time
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from research_fixtures import local_job_runner
from do_math.engine import ResearchEngine, control
from do_math import scheduled_operator
from research_fixtures import producer_result, install_adapter_fixture, restore_template
from state_fixtures import active_instance
from test_engine import common, context_from, ScriptedRunner


class QuotaRunner:
    def __init__(self):
        self.calls = []

    @local_job_runner
    def run(self, **arguments):
        context = context_from(arguments["prompt"])
        self.calls.append(context)
        call_number = len(self.calls)
        arguments["on_started"]({"fixture": "quota model"})
        if call_number == 1:
            (arguments["workspace"] / "partial.txt").write_text("retained evidence", encoding="utf-8")
            return producer_result({"status": "failed", "error": "native quota", "error_kind": "provider_limit",
                "failure": {"kind": "provider_limit", "provider": "claude", "retry_at": None,
                            "limit_windows": [], "evidence_ref": "stdout.jsonl"}, "usage": {}, "output": None}, arguments)
        return producer_result({"status": "completed", "output": common(context["action"]["role"]), "usage": {}}, arguments)


class RecoveryTests(unittest.TestCase):
    def setUp(self):
        install_adapter_fixture(self)

    def test_quota_preserves_original_action_without_diagnostic_calls_then_restores_files(self):
        # The subject begins at the runner's provider failure; activation is not
        # examined. One queued AI action keeps other plans off the provider probe.
        root, instance_id = restore_template(active_instance, config={
            "tier_models": {tier: "claude-opus-5" for tier in ("high", "medium", "low")},
            "scholarly_enabled": False, "operator_enabled": False,
            "tool_review_window_seconds": 60, "self_check_response_window_seconds": 5,
            "plan_settle_seconds": 1,
            "session_limits": {"work": {"claude-opus-5": 1}}, "lean_command": ["test-lean"]})
        runner = QuotaRunner()
        engine = ResearchEngine(root / "repository", instance_id, runner=runner)
        engine._enqueue("research_preparation", reason="Prepare work for the provider recovery fixture")
        engine._save()
        engine.run(max_steps=2)
        self.assertEqual(len(runner.calls), 1)
        self.assertFalse(any(e["role"] == "operational_review" for e in engine.runtime["executions"].values()))
        # The limited request returns to the queue with its gate wait, not to waiting_actions.
        retried = [row for row in engine.runtime["queue"]
                   if row.get("recovery", {}).get("reason") == "provider admission retry"]
        self.assertEqual(len(retried), 1)
        self.assertEqual(retried[0]["dispatch_wait"]["kind"], "provider_limit")
        self.assertEqual(retried[0]["dispatch_wait"]["provider"], "claude")
        self.assertNotIn(retried[0]["id"], engine.runtime.get("waiting_actions", {}))
        self.assertFalse(engine.runtime["questions"])
        current = time.time()
        original_action = retried[0]["id"]
        # An already queued independent plan may consume the successful
        # provider probe. Follow the preserved action, not a call ordinal.
        with patch("do_math.session_slots.time.time", return_value=current + 301):
            for _ in range(3):
                engine.run(max_steps=1)
                resumed = [ctx for ctx in runner.calls[1:] if ctx["action"]["id"] == original_action]
                if resumed:
                    break
        self.assertEqual(len(resumed), 1)
        self.assertTrue(any(row["path"] == "partial.txt" for row in resumed[0]["previous_output_files"]))
        self.assertFalse(any(e["role"] == "operational_review" for e in engine.runtime["executions"].values()))
        self.assertFalse([row for row in engine.runtime["queue"] if row["id"] == original_action
                          and row.get("dispatch_wait", {}).get("kind") == "provider_limit"])

    def test_wake_keeps_hold_and_user_pause_and_only_requests_engine(self):
        from research_fixtures import send_control
        root, instance_id = restore_template(active_instance, config={
            'operator_enabled': False, 'scholarly_enabled': False, 'lean_command': ['test-lean'],
            'tool_review_window_seconds': 60, 'self_check_response_window_seconds': 5})
        repo = root / 'repository'
        engine = ResearchEngine(repo, instance_id, runner=ScriptedRunner())
        workspace = Path(engine.instance['workspace'])
        with patch.object(scheduled_operator, 'schedule', return_value={}) as schedule:
            self.assertEqual(scheduled_operator.wake(repo, engine.instance['id'], workspace)['outcome'], 'engine_requested')
            schedule.assert_called_once_with('start-engine', repository=repo,
                instance=engine.instance['id'], workspace=workspace)
            schedule.reset_mock()
            send_control(engine, 'pause', text='Keep this synthetic instance paused')
            self.assertEqual(scheduled_operator.wake(repo, engine.instance['id'], workspace)['outcome'], 'paused')
            schedule.assert_not_called()
            scheduled_operator.hold(workspace, reason='Explicit temporary HOLD fixture')
            self.assertEqual(scheduled_operator.wake(repo, engine.instance['id'], workspace)['outcome'], 'held')
            schedule.assert_not_called()


if __name__ == "__main__":
    unittest.main()
