"""User authority, goal/policy revisions and bounded action authorization.

These functions interpret structured decisions already attributed to a user.
AI proposals are not decisions until their interpretation has been checked
against the preserved original request by a separate execution.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import hashlib
from typing import Any

from .repository import canonical_json, new_id
from .academic import set_requirements

WORK_ROLES = {"research_work", "supplemental_research", "task_contract_review", "identity_review", "goal_audit", "formal_check"}
OPERATING_ROLES = {"research_preparation", "research_plan", "operational_review", "intent_interpretation", "maintenance"}


def timestamp(value: str | None = None) -> datetime:
    result = datetime.fromisoformat(value.replace("Z", "+00:00")) if value else datetime.now(timezone.utc)
    if result.tzinfo is None:
        raise ValueError("a timezone is required")
    return result.astimezone(timezone.utc)


def ensure_governance(instance: dict, at: str | None = None) -> dict:
    result = deepcopy(instance)
    when = timestamp(at).isoformat()
    result.setdefault("goal_revision", 1)
    result.setdefault("policy_revision", 1)
    result.setdefault("governance_history", [])
    result.setdefault("decisions", {})
    if "grants" not in result:
        result["grants"] = {}
        for pool, roles in (("work", WORK_ROLES), ("operations", OPERATING_ROLES)):
            gid = new_id("GR")
            result["grants"][gid] = {
                "id": gid, "kind": "local", "status": "active", "budget_kind": pool,
                "roles": sorted(roles), "task_ids": [], "expires_at": None,
                "created_at": when, "source_ref": "instance-init", "checkpoint_allowed": True,
            }
    return result


def authorize(instance: dict, action: dict, at: str | None = None) -> dict:
    now = timestamp(at)
    role, target = action["role"], action.get("target")
    accepted = []
    rejected = []
    for grant in instance.get("grants", {}).values():
        if grant.get("kind") != "local" or role not in grant.get("roles", []):
            continue
        if grant.get("task_ids") and target not in grant["task_ids"]:
            continue
        reason = None
        if grant.get("status") != "active":
            reason = "grant is not active"
        elif grant.get("expires_at") and timestamp(grant["expires_at"]) <= now:
            reason = "grant expired"
        elif grant.get("valid_from") and timestamp(grant["valid_from"]) > now:
            reason = "grant is not effective yet"
        if reason:
            rejected.append({"grant_id": grant["id"], "reason": reason})
        else:
            accepted.append(grant)
    if not accepted:
        return {"allowed": False, "grant_id": None, "reason": "no current grant permits this action", "rejected": rejected}
    grant = sorted(accepted, key=lambda g: g["id"])[0]
    return {"allowed": True, "grant_id": grant["id"],
            "grant_sha256": hashlib.sha256(canonical_json(grant)).hexdigest(),
            "expires_at": grant.get("expires_at"), "checkpoint_allowed": grant.get("checkpoint_allowed", False)}


def _require_text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be nonempty text")
    return value


def _queue(runtime: dict, role: str, reason: str, **fields: Any) -> None:
    action = {"role": role, "reason": reason, **fields}
    runtime.setdefault("queue", []).append(action)


def apply_decision(instance: dict, runtime: dict, change: dict, *, source_ref: str,
                   actor: str = "user", at: str | None = None) -> tuple[dict, dict, dict]:
    """Apply one explicit decision atomically to copies of the two roots."""
    if actor != "user" or not source_ref:
        raise ValueError("a preserved user decision is required")
    instance, runtime = ensure_governance(instance, at), deepcopy(runtime)
    when = timestamp(at).isoformat()
    kind = change.get("kind")
    decision_id = change.get("decision_id") or new_id("DC")
    if decision_id in instance["decisions"]:
        old = instance["decisions"][decision_id]
        if old["change"] != change or old["source_ref"] != source_ref:
            raise ValueError("decision ID reused with different content")
        return instance, runtime, old
    event = {"id": decision_id, "kind": kind, "change": deepcopy(change), "source_ref": source_ref,
             "actor": actor, "created_at": when, "affected": []}
    if kind == "goal":
        goal = _require_text(change.get("goal"), "goal")
        if change.get("expected_revision", instance["goal_revision"]) != instance["goal_revision"]:
            raise ValueError("goal revision changed")
        if change.get("goal_kind", instance["goal_kind"]) not in {"mathematical", "research"}:
            raise ValueError("invalid goal kind")
        instance["governance_history"].append({"kind": "goal", "revision": instance["goal_revision"],
            "goal": instance["goal"], "goal_kind": instance["goal_kind"], "goal_status": instance["goal_status"], "replaced_by": decision_id})
        instance.update(goal=goal, goal_kind=change.get("goal_kind", instance["goal_kind"]),
                        goal_revision=instance["goal_revision"] + 1, goal_status="unresolved")
        for task in runtime["tasks"].values():
            if task["status"] not in {"completed", "closed"}:
                task["status"] = "needs_revision"
                task.setdefault("change_reasons", []).append({"decision_id": decision_id, "reason": "goal changed"})
                event["affected"].append(task["id"])
        goal_dependent = {"research_preparation", "research_plan", "goal_audit", "task_contract_review", "research_work", "supplemental_research"}
        # Only actions that consume the replaced goal are cancelled; machine transitions, identity review
        # slots (including their fixed-question research), intent checks and recovery actions continue.
        runtime["queue"] = [a for a in runtime["queue"] if a["role"] not in goal_dependent or a.get("review_cycle_id")]
        _queue(runtime, "research_preparation", "goal changed", decision_id=decision_id)
        runtime["questions"] = []
        if runtime["status"] in {"waiting", "completed", "budget_exhausted"}:
            runtime["status"] = "ready"
    elif kind == "policy":
        text = _require_text(change.get("text"), "policy text")
        if change.get("expected_revision", instance["policy_revision"]) != instance["policy_revision"]:
            raise ValueError("policy revision changed")
        instance["governance_history"].append({"kind": "policy", "revision": instance["policy_revision"],
                                               "text": instance["policies"], "replaced_by": decision_id})
        instance["policies"] = text
        instance["policy_revision"] += 1
        for task in runtime["tasks"].values():
            if task["status"] not in {"completed", "closed"}:
                task["status"] = "planned"
                event["affected"].append(task["id"])
                _queue(runtime, "task_contract_review", "policy changed", target=task["id"])
        _queue(runtime, "research_plan", "policy changed")
    elif kind == "academic_requirements":
        requirements = change.get("requirements")
        instance = set_requirements(instance, requirements)
        event["requirements_revision"] = instance["academic_requirements"]["revision"]
        for task in runtime["tasks"].values():
            if task.get("academic_requirement_id") and task["status"] not in {"completed", "closed"}:
                task["status"] = "planned"
                event["affected"].append(task["id"])
        initial = (not runtime.get("executions") and not runtime["tasks"]
                   and not instance.get("knowledge") and any(
                       a["role"] == "research_preparation" for a in runtime["queue"]))
        event["initial_registration"] = initial
        fields = {}
        if initial:
            fields["initial_preparation_wait"] = {
                "goal_revision": instance["goal_revision"],
                "policy_revision": instance["policy_revision"],
                "requirements_sha256": instance["academic_requirements"]["sha256"]}
        pending = next((a for a in runtime["queue"] if initial and
                        a.get("initial_preparation_wait") and a["role"] == "research_plan"), None)
        if pending is not None:
            pending.update(fields)
        else:
            _queue(runtime, "research_plan", "academic requirements changed", **fields)
    elif kind == "grant":
        spec = deepcopy(change.get("grant"))
        if not isinstance(spec, dict) or spec.get("kind") not in {"local", "http"}:
            raise ValueError("grant kind must be local or http")
        expires = spec.get("expires_at")
        if expires and timestamp(expires) <= timestamp(when):
            raise ValueError("new grant has already expired")
        if spec["kind"] == "local":
            roles = spec.get("roles")
            if not isinstance(roles, list) or not roles or set(roles) - WORK_ROLES - OPERATING_ROLES:
                raise ValueError("local grant requires supported roles")
            if not isinstance(spec.get("task_ids", []), list):
                raise ValueError("task_ids must be a list")
        else:
            if not spec.get("allowed_origins") or not spec.get("allowed_methods"):
                raise ValueError("HTTP grant must specify origins and methods")
            if not isinstance(spec.get("credential_env", {}), dict):
                raise ValueError("credential_env contains names, not credential values")
        gid = spec.get("id") or new_id("GR")
        if gid in instance["grants"]:
            raise ValueError("grant ID already exists; revoke it before replacing authority")
        spec.update(id=gid, status="active", expires_at=expires, created_at=when,
                    source_ref=source_ref, decision_id=decision_id)
        instance["grants"][gid] = spec
        event["grant_id"] = gid
        _queue(runtime, "research_plan", "new execution authority", grant_id=gid)
    elif kind == "revoke":
        gid = change.get("grant_id")
        if gid not in instance["grants"]:
            raise ValueError("grant not found")
        instance["grants"][gid].update(status="revoked", revoked_at=when, revoked_by=decision_id)
        event["grant_id"] = gid
        for eid, execution in runtime["executions"].items():
            if execution.get("grant_id") == gid and execution["status"] != "ended":
                execution["stop_requested"] = "grant_revoked"
                event["affected"].append(eid)
        runtime["queue"] = [a for a in runtime["queue"] if a.get("grant_id") != gid]
    elif kind == "task_scope":
        tid = change.get("task_id")
        task = runtime["tasks"].get(tid)
        if task is None or task["status"] in {"completed", "closed"}:
            raise ValueError("task scope change requires an unfinished task")
        disposition = change.get("disposition")
        if disposition not in {"revise", "transfer", "withdraw"}:
            raise ValueError("scope disposition must be revise, transfer or withdraw")
        reason = _require_text(change.get("reason"), "scope disposition reason")
        if disposition == "transfer":
            target = runtime["tasks"].get(change.get("target_task_id"))
            if target is None or target["id"] == tid or target["status"] in {"completed", "closed"}:
                raise ValueError("scope transfer requires a distinct unfinished receiving task")
            live = [execution['id'] for execution in runtime.get('executions', {}).values()
                    if execution.get('status') != 'ended' and execution.get('action', {}).get('target') in {tid, target['id']}]
            if live: raise ValueError('scope transfer requires source and target executions to end first: ' + ','.join(live))
            previous = {'revision': target.get('revision', 1), 'completion_criteria': deepcopy(target.get('completion_criteria', [])),
                        'reviews': deepcopy(target.get('reviews', [])), 'assessment': deepcopy(target.get('assessment'))}
            inherited = list(dict.fromkeys([*target.get('completion_criteria', []), *task.get('completion_criteria', [])]))
            target.setdefault('revision_history', []).append({'decision_id': decision_id, 'reason': reason, 'previous': previous,
                                                                'inherited_from': tid, 'criteria': deepcopy(task.get('completion_criteria', []))})
            target['completion_criteria'] = inherited
            target['revision'] = target.get('revision', 1) + 1
            target['reviews'] = []
            target.pop('assessment', None)
            target['status'] = 'needs_revision'
            target.setdefault("transferred_obligations", []).append({"from_task": tid, "criteria": task["completion_criteria"], "decision_id": decision_id})
            _queue(runtime, "task_contract_review", "transferred obligations require review", target=target['id'])
        task["scope_disposition"] = {"kind": disposition, "reason": reason, "decision_id": decision_id, "target_task_id": change.get("target_task_id")}
        task.pop("pending_withdrawal", None)
        live_work = [execution for execution in runtime.get("executions", {}).values()
                     if execution.get("status") != "ended"
                     and execution.get("role") in {"research_work", "supplemental_research"}
                     and execution.get("action", {}).get("target") == tid
                     and not execution.get("action", {}).get("review_cycle_id")]
        if disposition == "withdraw" and live_work:
            task["pending_withdrawal"] = deepcopy(task["scope_disposition"])
            for execution in live_work:
                execution["stop_requested"] = "task_withdrawn"
                execution["after_stop"] = {"decision": "wait", "reason": reason}
        else:
            task["status"] = "needs_revision" if disposition == "revise" else "closed"
        if disposition == "revise":
            # The current contract revision may not be scheduled again until preparation authors a new revision.
            task["revision_requested"] = {"source": decision_id, "revision": task.get("revision"), "reason": reason}
        event["affected"].append(tid)
        runtime["queue"] = [a for a in runtime["queue"] if a.get("target") != tid]
        if disposition == "revise":
            _queue(runtime, "research_preparation", reason, target=tid)
    else:
        raise ValueError(f"unsupported governance decision: {kind}")
    instance["decisions"][decision_id] = event
    runtime.setdefault("history", []).append({"kind": "governance_decision", "decision_id": decision_id, "source_ref": source_ref})
    return instance, runtime, event


def interpretation_schema(stage: str) -> dict:
    string = {"type": "string"}
    changes = {"type": "array", "items": {"type": "object", "additionalProperties": False,
        "properties": {"kind": {"type": "string", "enum": ["goal", "policy", "none"]},
                       "text": string, "reason": string}, "required": ["kind", "text", "reason"]}}
    fields = {"summary": string, "used_sources": {"type": "array", "items": string},
              "questions": {"type": "array", "items": string}}
    if stage == "interpret":
        fields.update(interpretation=string, proposed_changes=changes, needs_clarification={"type": "boolean"})
    elif stage == "check":
        fields.update(decision={"type": "string", "enum": ["match", "mismatch", "unresolved"]},
                      findings={"type": "array", "items": string}, scope_complete={"type": "boolean"})
    else:
        raise ValueError("unknown interpretation stage")
    return {"type": "object", "additionalProperties": False, "properties": fields, "required": list(fields)}
