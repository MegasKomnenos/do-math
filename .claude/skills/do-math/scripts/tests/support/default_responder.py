"""Canonical synthetic inputs and real producers; no engine or storage replacement."""
from __future__ import annotations

import json
from support.role_answers import assessment, candidate, contract_review, disposition, intent_response, planning_model_assessments, read_fixture_context
from support.observation_inputs import supply_observation_rules


def context_from(prompt: str, workspace=None) -> dict:
    if workspace is not None:
        return read_fixture_context(prompt, workspace)
    marker = "--- CANONICAL INPUT CONTEXT ---\n"
    return json.loads(prompt.split(marker, 1)[1].split("\n--- OUTPUT JSON SCHEMA ---", 1)[0])


def contract_checks(candidates: list[dict]) -> list[dict]:
    """The smallest self-check a fixture contract needs: it cites no sibling task."""
    return [{"task_title": item["title"], "sibling_boundaries": []} for item in candidates]


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


FORMAL_SOURCE = "theorem t : True := by trivial"


class DefaultResponder:
    def __init__(self, *, formal: bool = False, invalid_plan: str | None = None,
                 preparation_candidates=None, model_rating=None, plan_assessments=True):
        self.formal, self.invalid_plan = formal, invalid_plan
        self.plan_assessments = plan_assessments
        self.preparation_candidates = preparation_candidates
        self.explicit_model_rating = model_rating
        self.model_rating = model_rating or {"difficulty": "low", "importance": "medium", "reason": "Bounded explicit fixture argument"}

    def respond(self, role, ctx, workspace):
        """The role output, before binding and sealing, and the activity extensions it writes to ``workspace``."""
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
                "lean_code": FORMAL_SOURCE if self.formal else "",
                "declaration_names": ["t"] if self.formal else [], "dependencies": []}])
        elif role == "identity_review":
            stage = ctx["action"]["stage"]
            if stage == "scope":
                from support.role_answers import scope_response
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
                    from support.observation_inputs import prepared_rule_conditions
                    extensions['task_conditions'] = prepared_rule_conditions(ctx['action']['observation_rule_targets'])
            elif ctx.get("budget_unit") == "concurrent_sessions" and self.plan_assessments:
                extensions["model_assessments"] = planning_model_assessments(out, ctx)
                if self.explicit_model_rating is not None:
                    extensions["model_assessments"] = [{**row, **self.explicit_model_rating}
                        for row in extensions["model_assessments"]]
            if extensions:
                path.write_text(json.dumps(extensions), encoding="utf-8")
        return out


def rating(**identity):
    return {**identity, "difficulty": "low", "importance": "medium", "reason": "A bounded check of one supplied identity."}
