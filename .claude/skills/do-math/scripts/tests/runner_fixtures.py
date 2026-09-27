"""Scripted model runners for engine drives, and the role outputs they write.

``ScriptedRunner`` answers every role with the smallest output the role's
contract accepts, built from its actual input: the preparation proposes one
candidate (``research_fixtures.candidate``) or the ``preparation_candidates``
given, the plan selects every ready task and assesses every returned one, the
work returns one theorem (formal when ``formal=True``), reviews match and the
goal audit is satisfied when eligible knowledge exists. Its output passes
through the producer path a real worker takes (``bind_candidates``,
``seal_response``, schema validation, ``submit_intent``) inside a real local
job (``local_job_runner``). ``invalid_plan`` and ``fail_role`` inject the two
failures tests ask for; ``prompts`` records every (role, prompt).

- ``common(role)``: the neutral fields every role output carries, plus the
  empty shape of that role's own fields.
- ``context_from(prompt, workspace=None)``: the canonical input context in a
  prompt, with its source references read from ``workspace`` when given.
- ``contract_checks(candidates)``: the smallest preparation self-check per candidate.
- ``rating(**identity)``: one model assessment row for ``identity``.
- ``formal_ok``: a compiler double that verifies the two fixture sources
  (``theorem t : True := by trivial`` and ``add_zero_fixture``) and nothing else.
"""
from __future__ import annotations

import json

import jsonschema

from research_fixtures import (assessment, bind_candidates, candidate, contract_review, disposition, intent_response,
                               local_job_runner, planning_model_assessments, read_fixture_context, seal_response,
                               submit_intent, supply_observation_rules)


def context_from(prompt: str, workspace=None) -> dict:
    if workspace is not None:
        return read_fixture_context(prompt, workspace)
    marker = "--- CANONICAL INPUT CONTEXT ---\n"
    return json.loads(prompt.split(marker, 1)[1].split("\n--- OUTPUT JSON SCHEMA ---", 1)[0])


def contract_checks(candidates: list[dict]) -> list[dict]:
    """The smallest self-check a fixture contract needs: no symbols, no cited sibling, two outcomes."""
    return [{"task_title": item["title"], "symbols": [], "sibling_boundaries": [], "outcome_branches": [
        {"outcome": "The fixture obligation is met", "completion": "Every criterion is judged from the report"},
        {"outcome": "The fixture obligation is not met", "completion": "The report records the unmet criterion"}]}
        for item in candidates]


def common(role: str) -> dict:
    """Neutral response fields only; judgments must come from the actual input."""
    base = {"summary": role, "used_sources": [], "questions": []}
    shapes = {
        "research_preparation": {"candidates": []},
        "research_plan": {"dispositions": [], "task_assessments": [], "preparation_requests": [], "goal_audit": False},
        "task_contract_review": {"item_reviews": []},
        "research_work": {"outcome": "no_result", "report": "", "knowledge": [], "relations": [], "remaining_work": [], "checkpoint": ""},
        "supplemental_research": {"outcome": "no_result", "report": "", "knowledge": [], "relations": [], "remaining_work": [], "checkpoint": ""},
        "maintenance": {"report": "", "remaining_work": []},
    }
    return {**base, **shapes.get(role, {})}


class ScriptedRunner:
    def __init__(self, *, formal: bool = False, invalid_plan: str | None = None, fail_role: str | None = None,
                 preparation_candidates=None, model_rating=None):
        self.formal, self.invalid_plan, self.fail_role = formal, invalid_plan, fail_role
        self.prompts: list[tuple[str, str]] = []
        self.preparation_candidates = preparation_candidates
        self.explicit_model_rating = model_rating
        self.model_rating = model_rating or {"difficulty": "low", "importance": "medium", "reason": "Bounded explicit fixture argument"}

    @local_job_runner
    def run(self, *, prompt, output_schema, workspace, evidence_dir, model, effort, timeout_seconds,
            should_stop, on_started, control_binding=None, launch_ticket=None, **kwargs):
        role = prompt.split("You are the do-math role: ", 1)[1].split(".", 1)[0]
        ctx = context_from(prompt, workspace)
        self.prompts.append((role, prompt))
        on_started()
        if role == self.fail_role:
            return {"status": "failed", "output": None, "usage": {}, "error": "interrupted"}
        out = common(role)
        if role == "intent_interpretation":
            out = intent_response(ctx)
        elif role == "research_preparation":
            from copy import deepcopy
            out["candidates"] = ([] if any(key in ctx['action'] for key in ('assessment_targets', 'observation_rule_targets')) else
                deepcopy(self.preparation_candidates) if self.preparation_candidates is not None else [candidate(formal=self.formal)])
        elif role == "task_contract_review":
            out.update(contract_review(ctx))
        elif role == "research_plan":
            from do_math.task_contracts import returned_task_ids
            tasks = {t["id"]: t for t in ctx["tasks"]}
            out.update(dispositions=[disposition(tid) for tid in ctx["ready_task_ids"]],
                task_assessments=[assessment(tasks[tid]) for tid in returned_task_ids(tasks)],
                goal_audit=bool(ctx["knowledge_catalog"]))
            if self.invalid_plan == "missing":
                out["dispositions"] = []
            if self.invalid_plan == "criterion":
                for row in out["task_assessments"]:
                    row["item_dispositions"] = []
        elif role == "research_work":
            out.update(outcome="submitted", report="The domain is Nat. Applying Nat.add_zero proves n + 0 = n.",
                checkpoint="Argument and domain recorded", knowledge=[{
                "kind": "theorem", "title": "T", "statement": "True", "explanation": "True holds by its constructor", "summary": "True holds",
                "lean_code": "theorem t : True := by trivial" if self.formal else "",
                "declaration_names": ["t"] if self.formal else [], "dependencies": []}])
        elif role == "identity_review":
            stage = ctx["action"]["stage"]
            if stage == "scope":
                from research_fixtures import scope_response
                out.update(scope_response(ctx))
            else:
                review = ctx["role_review"]
                out["proposal_digest"] = review["proposal_digest"]
                out["used_sources"] = ["proposal"]
                if stage == "initial": out.update(decision="match", findings=[], scope_complete=True)
                elif stage == "organize": out["issues"] = []
                elif stage == "answer": out.update(answers=[], new_findings=[])
                elif stage == "judge": out.update(decision="match", scope_complete=True, issue_verdicts=[], new_findings=[])
        elif role == "goal_audit":
            eligible = ctx.get("eligible_knowledge", [])
            out.update(decision="satisfied" if eligible else "not_satisfied",
                used_sources=[k["id"] for k in eligible], reason="Use only the supplied eligible formal records",
                scope_complete=True, additional_audits=[])
        elif role == "operational_review":
            out["disposition"] = {"kind": "user_decision", "basis_refs": [ctx["action"]["target"]],
                "next_owner": "user", "reason": "The fixture scenario has stopped after a preserved failure",
                "question": "Should the synthetic scenario continue?", "effect": "Choose the fixture continuation"}
        if role == "research_preparation" and ctx.get("budget_unit") == "concurrent_sessions":
            key = "task_id" if ctx["action"].get("assessment_targets") else "task_title"
            ids = list(ctx["action"].get("assessment_targets", {})) if key == "task_id" else [c["title"] for c in out["candidates"]]
            extensions = {"model_assessments": [{key: ident, **self.model_rating} for ident in ids]}
            if out["candidates"]: extensions["contract_checks"] = contract_checks(out["candidates"])
            (workspace / "activity-extensions.json").write_text(json.dumps(extensions), encoding="utf-8")
        if role in {"research_preparation", "research_plan"}:
            path = workspace / "activity-extensions.json"
            extensions = json.loads(path.read_bytes()) if path.exists() else {}
            if role == "research_preparation":
                supply_observation_rules(out.get("candidates", []), extensions)
                if ctx['action'].get('observation_rule_targets'):
                    from research_fixtures import prepared_rule_conditions
                    extensions['task_conditions'] = prepared_rule_conditions(ctx['action']['observation_rule_targets'])
            elif ctx.get("budget_unit") == "concurrent_sessions":
                extensions["model_assessments"] = planning_model_assessments(out, ctx)
                if self.explicit_model_rating is not None:
                    extensions["model_assessments"] = [{**row, **self.explicit_model_rating}
                        for row in extensions["model_assessments"]]
            if extensions:
                path.write_text(json.dumps(extensions), encoding="utf-8")
        bind_candidates(out, ctx)
        seal_response(out, ctx, workspace)
        jsonschema.validate(out, output_schema)
        submit_intent(control_binding, workspace, out)
        return {"status": "completed", "output": out, "usage": {"calls": 1}, "error": None}


def formal_ok(*, source, declarations, workspace, lean_command,
              allowed_axioms=(), should_stop=None, expected_toolchain=None, on_started=None, launch_ticket=None):
    if launch_ticket is not None:
        from do_math.launch import validate_start
        validate_start(launch_ticket)
    if source == "theorem t : True := by trivial" and declarations == ["t"]:
        signature, dependencies, value = "True", ["True", "True.intro"], "True.intro"
    elif (source == "theorem add_zero_fixture (n : Nat) : n + 0 = n := Nat.add_zero n"
          and declarations == ["add_zero_fixture"]):
        signature, dependencies, value = "(n : Nat) -> n + 0 = n", ["Nat", "Nat.add_zero"], "Nat.add_zero"
    else:
        raise AssertionError("No explicit compiler fixture covers this source and declaration set")
    from do_math.repository import exact_content_hash
    from knowledge_fixtures import formal_result
    signatures = {name: f"{name} : {signature}" for name in declarations}
    toolchain = expected_toolchain or {"executable": "test-lean", "sha256": "f" * 64,
        "version": "Lean test 4.32.0", "version_exit": 0, "configured_command": list(lean_command)}
    return formal_result(source, declarations, toolchain, closure=dependencies,
        dependency_evidence=["fixture-" + ref for ref in dependencies], declaration_evidence=(signature, value),
        launch_not_created=True, declaration_signatures=signatures, signature_hash=exact_content_hash(signatures),
        allowed_axioms=list(allowed_axioms))


def rating(**identity):
    return {**identity, "difficulty": "low", "importance": "medium", "reason": "A bounded check of one supplied identity."}
