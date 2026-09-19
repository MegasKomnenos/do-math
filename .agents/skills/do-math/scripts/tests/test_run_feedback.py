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
from test_engine import common
from test_model_assessment_flow import candidate
from test_purpose_engine import PurposeHarness


class PlanAfterPreparationTests(PurposeHarness):
    def engine_with_running_work(self):
        engine, _ = self.make(scholarly_enabled=False, operator_enabled=False, session_limits=deepcopy(LIMITS))
        engine.runtime["queue"] = []
        engine.runtime["executions"]["EX-prep"] = {"id": "EX-prep", "role": "research_preparation", "status": "running",
                                                   "action": {"id": "AC-prep", "role": "research_preparation"}, "extensions": {}}
        return engine

    def plans(self, engine):
        return [a for a in engine.runtime["queue"] if a["role"] == "research_plan"]

    def prepare(self, engine, candidates):
        engine._apply({"id": "AC-prep", "role": "research_preparation"},
                      {**common("research_preparation"), "candidates": candidates}, "EX-prep")

    def test_new_contracts_awaiting_review_do_not_open_a_plan_with_nothing_to_decide(self):
        engine = self.engine_with_running_work()
        self.prepare(engine, [candidate("one")])
        self.assertTrue(any(a["role"] == "task_contract_review" for a in engine.runtime["queue"]))
        self.assertEqual(self.plans(engine), [], "the approval event opens the plan that can actually select the task")

    def test_preparation_still_opens_a_plan_when_a_ready_task_awaits_a_decision(self):
        engine = self.engine_with_running_work()
        engine.runtime["tasks"]["TK-ready"] = {**candidate("deferred"), "id": "TK-ready", "revision": 1, "status": "ready",
                                                "results": [], "reviews": [], "dependencies": []}
        self.prepare(engine, [candidate("one")])
        self.assertEqual(len(self.plans(engine)), 1)

    def test_preparation_without_any_pending_review_still_opens_a_plan(self):
        engine = self.engine_with_running_work()
        self.prepare(engine, [])
        self.assertEqual(len(self.plans(engine)), 1, "nothing else would reconsider the research")


class DuplicateContractReviewTests(PurposeHarness):
    def test_a_running_review_of_the_same_contract_is_not_doubled_when_its_outside_premises_move(self):
        from do_math.planning import contract_hash
        from test_model_assessment_flow import rating
        engine, _ = self.make(scholarly_enabled=False, operator_enabled=False, session_limits=deepcopy(LIMITS))
        task = {**candidate("window"), "id": "TK-window", "revision": 1, "status": "planned", "feature_version": 2,
                "producer_execution": "EX-prep", "results": [], "reviews": [], "dependencies": [],
                "occurrence_condition": {"op": "always"}, "initial_observation_rules": [], "model_assessment": rating()}
        engine.runtime["tasks"] = {"TK-window": task}
        basis = {"revision": 1, "contract_sha256": contract_hash(task),
                 "goal_revision": engine.instance["goal_revision"], "policy_revision": engine.instance["policy_revision"]}
        running = {"id": "AC-review", "role": "task_contract_review", "target": "TK-window",
                   "contract_basis": basis, "review_basis_key": "key-before-a-sibling-was-approved"}
        engine.runtime["queue"] = [running]
        engine.runtime["executions"]["EX-review"] = {"id": "EX-review", "role": "task_contract_review",
                                                     "status": "running", "action": deepcopy(running)}
        engine._refresh_readiness()
        reviews = [a for a in engine.runtime["queue"] if a["role"] == "task_contract_review"]
        self.assertEqual([a["id"] for a in reviews], ["AC-review"],
                         "the finished review's own currentness check decides whether another review is needed")


class PlanSettleTests(PurposeHarness):
    def setUp(self):
        super().setUp()
        from do_math.model_policy import MODELS
        self.engine, _ = self.make(scholarly_enabled=False, operator_enabled=False, session_limits=deepcopy(LIMITS))
        self.engine.runtime["queue"] = []
        self.resources = {pool: {model: {"available": 3} for model in MODELS.values()} for pool in ("work", "operations")}

    def queue(self, plan, review=True):
        self.engine.runtime["queue"] = [plan, *([{"id": "AC-review", "role": "task_contract_review", "target": "TK-x"}] if review else [])]
        return plan

    def test_a_plan_waits_for_pending_contract_reviews_so_nearby_approvals_share_one_decision(self):
        plan = self.queue({"id": "AC-plan", "role": "research_plan"})
        self.assertFalse(self.engine._dispatchable(plan, self.resources))
        self.assertEqual(plan["dispatch_wait"]["kind"], "plan_settle")
        self.queue(plan, review=False)
        self.assertTrue(self.engine._dispatchable(plan, self.resources))

    def test_the_settle_wait_ends_at_its_configured_limit(self):
        from datetime import datetime, timedelta, timezone
        self.assertEqual(self.engine.instance["config"]["plan_settle_seconds"], 300)
        started = (datetime.now(timezone.utc) - timedelta(seconds=301)).isoformat()
        plan = self.queue({"id": "AC-plan", "role": "research_plan", "settle_started_at": started})
        self.assertTrue(self.engine._dispatchable(plan, self.resources), "a slow review must not hold the first ready task for long")

    def test_an_explicitly_requested_plan_does_not_settle(self):
        plan = self.queue({"id": "AC-plan", "role": "research_plan", "requested_by": "UC-user"})
        self.assertTrue(self.engine._dispatchable(plan, self.resources))


class DispatchReserveTests(unittest.TestCase):
    def test_reserve_follows_the_notice_idiom_and_never_exceeds_a_tenth_of_the_run(self):
        from do_math.execution_window import dispatch_reserve_seconds
        self.assertEqual(dispatch_reserve_seconds({"run_timeout_seconds": 7200}), 300)
        self.assertEqual(dispatch_reserve_seconds({"run_timeout_seconds": 7200, "dispatch_reserve_seconds": 120}), 120)
        self.assertEqual(dispatch_reserve_seconds({"run_timeout_seconds": 100}), 10)


class DispatchReserveRunTests(PurposeHarness):
    def test_no_ordinary_execution_starts_inside_the_reserve_before_the_run_deadline(self):
        from unittest.mock import patch
        import do_math.scheduler as scheduler
        engine, runner = self.make(scholarly_enabled=False, operator_enabled=False, session_limits=deepcopy(LIMITS))
        with patch.object(scheduler, "dispatch_reserve_seconds", lambda config: config["run_timeout_seconds"] + 1):
            engine.run(max_steps=1)
        self.assertEqual(engine.runtime["executions"], {}, "a run that cannot finish before the deadline is left for the next engine run")


if __name__ == "__main__":
    unittest.main()
