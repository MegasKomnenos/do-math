"""Doubles for the engine region's research flows on a Sim.

- ``record_submissions(sim, responder=None)``: the Sim's model double, and for each
  bound call it keeps in ``submissions`` the role, the checker context's control
  binding, the transport's delivery state and the final receipt state of the
  submission the model made with the workspace tool.
- ``BoundedObservationResponder``: the answers of the legacy
  ``test_engine.PublicGitFlow`` runner. Research preparation proposes one bounded
  observation task (with its contract checks, an observation rule and a model
  assessment) while no task exists; the plan selects every ready task and assesses
  every returned one; research work submits one observation. Any other role is an
  error, so the flow cannot pass through an unexpected role.
"""
from __future__ import annotations

import json
from pathlib import Path

from do_math.canonical import canonical_json
from support.model import FakeCLI, ModelDouble


class BoundedObservationResponder:
    def respond(self, role, ctx, workspace):
        from do_math import execution_profiles, task_contracts
        from support.role_answers import assessment, candidate, contract_review, intent_response, planning_model_assessments
        from support.default_responder import contract_checks
        output = {"summary": role, "used_sources": [], "questions": []}
        if role == "intent_interpretation":
            output = intent_response(ctx)
        elif role == "research_preparation":
            row = candidate("bounded observation")
            row["profile_refs"] = [execution_profiles.profile_ref(p) for p in ctx["execution_profiles"]
                                   if p["role"] == "research_work"]
            output["candidates"] = [row] if not ctx["tasks"] else []
            from do_math.contracts import schema_for
            if "observed_at" in schema_for(role)["properties"]:
                output["observed_at"] = ctx["observed_at"]
            if output["candidates"]:
                rules = [{"id": "rule-attempt", "operator": "counter_gte", "subject": {"kind": "counter", "id": "attempts"},
                          "basis": {"source": "checkpoint", "unit": "count"}, "threshold": 10,
                          "required_evidence": ["checkpoint.json"]}]
                (Path(workspace) / "activity-extensions.json").write_bytes(canonical_json({
                    "contract_checks": contract_checks(output["candidates"]),
                    "task_conditions": [{"task_title": row["title"], "occurrence_condition": {"op": "always"},
                                         "dependencies": [], "knowledge_revision_targets": [], "observation_rules": rules}],
                    "model_assessments": [{"task_title": row["title"], "difficulty": "low",
                                           "importance": "low", "reason": "Bounded synthetic task"}]}))
        elif role == "task_contract_review":
            output.update(contract_review(ctx))
        elif role == "research_plan":
            tasks = {task["id"]: task for task in ctx["tasks"]}
            output.update(dispositions=[{"task_id": tid, "kind": "selected", "reason": "Perform approved bounded work",
                "uncertainty": "Outcome is unconfirmed before execution", "parallel_task_ids": [],
                "expected_research_change": "Preserve an explicit observation", "revisit": {"at": None, "event_refs": []},
                "missing_inputs": [], "next_owner": "research_work"} for tid in ctx["ready_task_ids"]],
                task_assessments=[assessment(tasks[tid]) for tid in task_contracts.returned_task_ids(tasks)],
                preparation_requests=[], goal_audit=False)
            (Path(workspace) / "activity-extensions.json").write_bytes(canonical_json({
                "model_assessments": planning_model_assessments(output, ctx)}))
        elif role == "research_work":
            output.update(outcome="submitted", report="The observation is bounded to this synthetic execution and its stated domain.",
                checkpoint="Observation preserved", remaining_work=[], relations=[], knowledge=[{
                    "kind": "observation", "title": "Bounded observation", "statement": "The synthetic runner returned an observation.",
                    "explanation": "Evidence is this explicit synthetic execution", "summary": "A bounded observation",
                    "lean_code": "", "declaration_names": [], "dependencies": []}])
        else:
            raise AssertionError("Unexpected role in minimum actual Git flow: " + role)
        return output


def record_submissions(sim, responder=None):
    """Give ``sim`` a model double that records each tool submission; returns it."""

    class RecordingCLI(FakeCLI):
        def receipt_received(self, context, delivery, receipt):
            super().receipt_received(context, delivery, receipt)
            self.model.submissions.append({"role": context["action"]["role"],
                "binding": context["control_binding"], "delivery": delivery["state"], "receipt": receipt["state"],
                "schema_bytes": (self.workspace / 'input/submission/schema.json').read_bytes()})

    class RecordingModel(ModelDouble):
        def __init__(self, clock, responder=None):
            super().__init__(clock, responder)
            self.submissions = []

        def spawn(self, command, *, stdin=None, stdout=None, stderr=None, cwd=None, env=None, shell=False,
                  creationflags=0):
            return RecordingCLI(self, list(command), stdout, stderr, Path(cwd))
    sim.model = RecordingModel(sim.clock, responder)
    return sim.model


def worker_bindings(sim):
    """``{execution ID: control binding}`` of every worker request the Jobs fake ran (the runner's argument)."""
    rows = {}
    for job in sim.jobs.launched:
        if len(job.argv) > 2 and Path(job.argv[1]).name in ('codex_worker.py', 'claude_worker.py'):
            request = json.loads(Path(job.argv[2]).read_text(encoding='utf-8'))
            if 'control_binding' in request:
                rows[request['execution_id']] = request['control_binding']
    return rows
