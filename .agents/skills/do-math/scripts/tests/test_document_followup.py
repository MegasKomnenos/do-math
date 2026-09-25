"""Research contracts must deliver the evidence their next reader needs."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math import planning
from do_math.repository import canonical_json
from test_purpose_engine import ActiveStateHarness, candidate, common


class FollowupDocumentTests(ActiveStateHarness):
    def test_planning_roles_receive_the_complete_current_settings(self):
        engine, _ = self.make(observation_interval_seconds=417, review_research_limit=4)
        for role in ("research_preparation", "research_plan"):
            context = engine._context({"role": role}, self.root / role)
            self.assertEqual(context.get("config"), engine.instance["config"])

    def test_prepared_observation_rule_reaches_contract_review(self):
        engine, _ = self.make()
        from do_math.execution_profiles import profile_ref
        def proposal(title, **kwargs):
            value=candidate(title, **kwargs)
            value['profile_refs']=[profile_ref(p) for p in engine.instance['execution_profiles'].values()
                                   if p['role']=='research_work']
            return value
        rule = {"id": "branches", "operator": "counter_gte", "threshold": 3,
                "subject": {"kind": "counter", "id": "branches"},
                "basis": {"source": "execution_events", "unit": "count"},
                "repeat_interval": 3, "required_evidence": ["EV-branch"]}
        engine.runtime["executions"]["EX-preparation"] = {"status": "ended", "input_snapshot": engine.head, "extensions": {"task_conditions": [
            {"task_title": "Bounded branch investigation", "observation_rules": [rule]}]}}
        engine._apply({"role": "research_preparation"},
                      {**common("Prepare an observable investigation"), "candidates": [proposal("Bounded branch investigation")]},
                      "EX-preparation")
        task = next(iter(engine.runtime["tasks"].values()))
        self.assertEqual(task.get("initial_observation_rules"), [rule])
        review = next(a for a in engine.runtime["queue"] if a["role"] == "task_contract_review")
        context = engine._context(review, self.root / "review-input")
        self.assertEqual(context["task"]["initial_observation_rules"], [rule])
        changed = deepcopy(task)
        changed["initial_observation_rules"][0]["threshold"] = 30
        self.assertNotEqual(planning.contract_hash(task), planning.contract_hash(changed))

        engine.runtime["task_observation_rules"] = {task["id"]: [rule]}
        revised_rule = {**rule, "threshold": 5}
        engine.runtime["executions"]["EX-revision"] = {"status": "ended", "input_snapshot": engine.head, "extensions": {"task_conditions": [
            {"task_title": task["title"], "observation_rules": [revised_rule]}]}}
        engine._apply({"role": "research_preparation"},
                      {**common("Revise the observation boundary"), "candidates": [proposal(task["title"], revises=task["id"])]},
                      "EX-revision")
        self.assertEqual(engine.runtime["tasks"][task["id"]]["initial_observation_rules"], [revised_rule])
        self.assertNotIn(task["id"], engine.runtime["task_observation_rules"],
                         "rules from an earlier contract must not override the new reviewed initial rules")

    def test_old_rejected_preparation_remains_readable_after_recent_history_moves(self):
        engine, _ = self.make()
        output = {**common("Investigated the earlier approach"), "candidates": [candidate("Earlier proposal")]}
        result = canonical_json({"status": "completed", "output": output, "error": None})
        reference = "runtime/artifacts/BA-old/result.json"
        from do_math.execution_lifecycle import transition_execution
        action = {"id": "AC-old", "role": "research_preparation"}
        engine._action_lifecycle_gate(action)
        old = engine._register_execution(action, {"id": "EX-old", "role": "research_preparation", "status": "running"})
        # Synthetic historical result, with actual actor/activity record shape.
        old.update(artifact_bundle="BA-old", result_ref=reference,
                   error="output validation: earlier proposal omitted its required source")
        at = engine._lifecycle_now().isoformat()
        transition_execution(old, "stopping", at=at, stop_phase="terminating")
        transition_execution(old, "ended", at=at, outcome="execution_incomplete")
        engine.runtime["history"] = [{"role": "maintenance", "summary": "Unrelated later event"} for _ in range(20)]
        engine._save({reference: result})
        workspace = self.root / "later-preparation"
        context = engine._context({"role": "research_preparation"}, workspace)
        self.assertIn("preparation_history", list(context))
        earlier = next(row for row in context["preparation_history"] if row["execution_id"] == "EX-old")
        self.assertEqual(earlier["outcome"], "execution_incomplete")
        self.assertIn("required source", earlier["error"])
        raw = (workspace / earlier["local_path"]).read_bytes()
        self.assertEqual(raw, result)
        self.assertEqual(earlier["sha256"], hashlib.sha256(raw).hexdigest())
        self.assertEqual(json.loads(raw)["output"], output)
