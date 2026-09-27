"""The provider gate must change engine recovery, not only report a timestamp."""
import sys
import tempfile
import time
import unittest
from copy import deepcopy
from pathlib import Path
from unittest.mock import create_autospec, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math import scheduled_operator
from do_math.engine import ResearchEngine
from research_fixtures import install_adapter_fixture, local_job_runner, producer_result, restore_template
from runner_fixtures import common, context_from, ScriptedRunner
from state_fixtures import active_instance


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


class ProviderConnections(unittest.TestCase):
    def test_result_observation_has_no_prepublication_schedule_effect(self):
        from provider_fixtures import PROVIDER_LIMIT_FAILURE, admit, provider_repository
        from research_fixtures import bare_engine, git_init
        root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        engine = bare_engine(store=provider_repository(git_init(root)))
        engine.head, engine.instance, engine.runtime = engine.store.load()
        self.assertTrue(admit(engine._session_slots(), engine.instance, engine.runtime, 'EX-limit'))
        engine._schedule_provider_wake = create_autospec(engine._schedule_provider_wake)
        engine._provider_outcome('EX-limit', {'status': 'failed', 'error_kind': 'provider_limit', 'failure': PROVIDER_LIMIT_FAILURE})
        engine._schedule_provider_wake.assert_not_called()

    def test_saved_wait_drives_wake_and_schedule_failure_is_recoverable(self):
        from provider_fixtures import PROVIDER_LIMIT_FAILURE, admit, finish, provider_repository, report
        from research_fixtures import bare_engine, git_init
        from do_math import scheduled_operator
        from do_math.session_slots import SessionSlots
        from unittest.mock import patch
        import time
        root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        engine = bare_engine(store=provider_repository(git_init(root)))
        engine.head, engine.instance, engine.runtime = engine.store.load()
        engine.instance['config']['operator_enabled'] = True
        engine.runtime['tasks'] = {}  # The product save reads the task table this minimal provider state omits.
        slots = engine._session_slots()
        self.assertTrue(admit(slots, engine.instance, engine.runtime, 'EX-limit', current=time.time()))
        # Observation is separate from publication; the external effect reads Git.
        gate = report(slots, engine.instance, 'EX-limit', time.time(), PROVIDER_LIMIT_FAILURE)
        finish(slots, engine.runtime, 'EX-limit', time.time(), close_activity=False)
        action = {'id': 'AC-held', 'role': 'research_work',
                  'profile_ref': deepcopy(engine.instance['role_profile_refs']['research_work'][-1])}
        engine.runtime['queue'] = [action]
        engine._requeue_provider_action(action, 'EX-limit', gate)
        self.assertEqual(engine.runtime['queue'][-1]['dispatch_wait']['kind'], 'provider_limit')
        def saved_status():
            _, instance, persisted = engine.store.load()
            return {**scheduled_operator.supervision_facts(instance, persisted),
                    'provider_waits': SessionSlots(persisted, instance, observer=True).provider_snapshot()}
        calls = []
        actual = {}
        def schedule(command, **kwargs):
            calls.append((command, kwargs))
            _, _, persisted = engine.store.load()
            from do_math.provider_wait import epoch_seconds
            self.assertEqual(persisted['provider_waits']['PW-claude']['retry_at'], epoch_seconds(gate['retry_at']))
            self.assertIn('AC-held', [queued['id'] for queued in persisted['queue']])
            if command == 'status':
                return {'wake': actual.get('wake')}
            if command == 'schedule-wake':
                actual['wake'] = {'description': kwargs['wake_key'], 'next_run': kwargs['wake_at'], 'state': 'Ready'}
            return {}
        with patch.object(scheduled_operator, 'schedule', side_effect=OSError('scheduler unavailable')):
            engine._publish_provider_result()
        _, _, persisted = engine.store.load()
        self.assertEqual(persisted['provider_wake']['status'], 'failed')
        from do_math.provider_wait import epoch_seconds
        self.assertEqual(persisted['provider_waits']['PW-claude']['retry_at'], epoch_seconds(gate['retry_at']))
        with patch.object(scheduled_operator, 'schedule', side_effect=schedule):
            with patch.object(scheduled_operator, 'read_status', return_value=saved_status()), patch.object(
                    scheduled_operator, 'engine_start_guard', return_value={'outcome': 'provider_waiting'}):
                observed = scheduled_operator.check(root, engine.instance['id'], root)
                self.assertEqual(observed['provider_wake']['status'], 'scheduled')
            engine._publish_provider_result()
        self.assertEqual(sum(command == 'schedule-wake' for command, _ in calls), 1)
        scheduled = next(kwargs for command, kwargs in calls if command == 'schedule-wake')
        self.assertEqual(scheduled['wake_at'], gate['retry_at'])
        self.assertEqual(scheduled['wake_key'], 'claude:' + str(gate['generation']))
        with patch.object(engine, '_save', side_effect=OSError('Git failed')), patch.object(
                scheduled_operator, 'schedule') as scheduling:
            with self.assertRaisesRegex(OSError, 'Git failed'):
                engine._publish_provider_result()
            scheduling.assert_not_called()
        with patch.object(scheduled_operator, 'schedule', side_effect=schedule):
            scheduled_operator.hold(root, reason='Synthetic HOLD')
            calls_before = len(calls)
            self.assertEqual(scheduled_operator.check(root, engine.instance['id'], root)['outcome'], 'held')
            self.assertEqual(len(calls), calls_before)
            self.assertEqual(scheduled_operator.reconcile_wake(root, engine.instance['id'], root,
                facts={'status': 'ready'}, providers=engine._provider_status()['providers'])['status'], 'held')
            self.assertEqual(calls[-1][0], 'cancel-wake')


if __name__ == "__main__":
    unittest.main()
