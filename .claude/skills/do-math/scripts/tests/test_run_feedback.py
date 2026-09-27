"""Scheduling changes derived from the 2026-09-19 parking research run.

Each test fixes one trigger rule that produced executions without a decision to make.
Model responses are fixtures; the engine's own enqueue, lifecycle and dispatch code runs.
"""
from copy import deepcopy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math.model_policy import LIMITS
from do_math.execution_profiles import WORK_ROLES
from test_engine import common, ScriptedRunner
from test_model_assessment_flow import candidate
from test_purpose_engine import ActivatedPurposeHarness


class PlanAfterPreparationTests(ActivatedPurposeHarness):
    def prepare(self, candidates, *, ready_candidate=False):
        # The validated active state has no queued action and no pending event,
        # so nothing but the tested preparation can open a plan. (Public activation
        # leaves reconsideration events that a plan would first have to consume.)
        engine, _ = self.make_active(**self.fixture_config(
            scholarly_enabled=False, operator_enabled=False, session_limits=deepcopy(LIMITS)))
        self.assertEqual(engine.runtime["queue"], [])
        self.assertFalse(engine.runtime.get("pending_events"))
        if ready_candidate:
            engine.runner = ScriptedRunner(preparation_candidates=[candidate("deferred")])
            engine._enqueue("research_preparation", reason="Prepare a task that will await a decision")
            engine._save()
            engine.run(max_steps=2)
            self.assertTrue(any(row["state"] == "ready" for row in engine._task_readiness.values()))
        # Isolate the preparation trigger from previously queued plans. The task
        # and its approval remain actual receiver-created records.
        engine.runtime["queue"] = []
        engine._enqueue("research_preparation", reason="Explicit regression preparation")
        engine.runner = ScriptedRunner(preparation_candidates=candidates)
        engine._save()
        engine.run(max_steps=1)
        return engine

    def plans(self, engine):
        return [a for a in engine.runtime["queue"] if a["role"] == "research_plan"]

    def test_new_contracts_awaiting_review_do_not_open_a_plan_with_nothing_to_decide(self):
        engine = self.prepare([candidate("one")])
        self.assertTrue(any(a["role"] == "task_contract_review" for a in engine.runtime["queue"]))
        self.assertEqual(self.plans(engine), [])

    def test_preparation_still_opens_a_plan_when_a_ready_task_awaits_a_decision(self):
        engine = self.prepare([candidate("one")], ready_candidate=True)
        self.assertEqual(len(self.plans(engine)), 1)

    def test_preparation_without_any_pending_review_still_opens_a_plan(self):
        engine = self.prepare([])
        self.assertEqual(len(self.plans(engine)), 1, self.plans(engine))


class DuplicateContractReviewTests(ActivatedPurposeHarness):
    def test_a_running_review_of_the_same_contract_is_not_doubled_when_its_outside_premises_move(self):
        engine, _ = self.make_active(**self.fixture_config(
            scholarly_enabled=False, operator_enabled=False, session_limits=deepcopy(LIMITS)))
        engine.runner = ScriptedRunner(preparation_candidates=[candidate("window")])
        engine._enqueue("research_preparation", reason="Prepare the contract under review")
        engine._save()
        engine.run(max_steps=1)
        running = next(a for a in engine.runtime["queue"] if a["role"] == "task_contract_review")
        from do_math.repository import new_id
        from do_math.engine import now
        execution = engine._register_execution(running, {"id": new_id("EX"),
            "role": "task_contract_review", "status": "running", "created_at": now(), "input_snapshot": engine.head})
        before_id = running["id"]
        engine._refresh_readiness()
        reviews = [a for a in engine.runtime["queue"] if a["role"] == "task_contract_review"]
        self.assertEqual([a["id"] for a in reviews], [before_id],
                         "the finished review's own currentness check decides whether another review is needed")


class PlanSettleTests(ActivatedPurposeHarness):
    def setUp(self):
        super().setUp()
        self.engine, _ = self.make_active(scholarly_enabled=False, operator_enabled=False, session_limits=deepcopy(LIMITS))
        self.engine.runtime["queue"] = []

    def queue(self, plan, review=True):
        self.engine.runtime["queue"] = [plan, *([{"id": "AC-review", "role": "task_contract_review", "target": "TK-x"}] if review else [])]
        return plan

    def test_a_plan_waits_for_pending_contract_reviews_so_nearby_approvals_share_one_decision(self):
        plan = self.queue({"id": "AC-plan", "role": "research_plan"})
        self.assertFalse(self.engine._dispatchable(plan))
        self.assertEqual(plan["dispatch_wait"]["kind"], "plan_settle")
        self.queue(plan, review=False)
        self.assertTrue(self.engine._dispatchable(plan))

    def test_the_settle_wait_ends_at_its_configured_limit(self):
        from datetime import datetime, timedelta, timezone
        self.assertEqual(self.engine.instance["config"]["plan_settle_seconds"], 300)
        started = (datetime.now(timezone.utc) - timedelta(seconds=301)).isoformat()
        plan = self.queue({"id": "AC-plan", "role": "research_plan", "settle_started_at": started})
        self.assertTrue(self.engine._dispatchable(plan), "a slow review must not hold the first ready task for long")

    def test_an_explicitly_requested_plan_does_not_settle(self):
        plan = self.queue({"id": "AC-plan", "role": "research_plan", "requested_by": "UC-user"})
        self.assertTrue(self.engine._dispatchable(plan))


class RunWithoutDeadlineTests(ActivatedPurposeHarness):
    def test_elapsed_legacy_run_limit_does_not_block_the_next_execution(self):
        from unittest.mock import patch
        from types import SimpleNamespace
        import time
        import do_math.engine as engine_module
        import do_math.scheduler as scheduler
        engine, _ = self.make_active(scholarly_enabled=False, operator_enabled=False,
            session_limits=deepcopy(LIMITS))
        engine.runtime['queue'] = []
        engine._enqueue('research_preparation', reason='Prepare a contract for the deadline regression')
        engine._save()
        scripted = ScriptedRunner(preparation_candidates=[candidate('deadline regression')])
        clock = [0.0]
        calls = []
        class Runner:
            def run(self, **arguments):
                calls.append(arguments)
                result = scripted.run(**arguments)
                clock[0] += 10000
                return result
        engine.runner = Runner()
        observed_clock = SimpleNamespace(monotonic=lambda: time.monotonic() + clock[0], sleep=time.sleep)
        with patch.object(scheduler, 'time', observed_clock), patch.object(engine_module, 'time', observed_clock):
            engine.run(max_steps=2)
        self.assertEqual(len(calls), 2)
        for call in calls:
            if call['profile']['role'] in WORK_ROLES:
                self.assertIsNone(call['timeout_seconds'])
            else:
                self.assertGreater(call['timeout_seconds'], 0)
                self.assertLessEqual(call['timeout_seconds'], call['profile']['window']['call_timeout_seconds'])
        self.assertNotEqual(engine.runtime['status'], 'paused')


if __name__ == "__main__":
    unittest.main()
