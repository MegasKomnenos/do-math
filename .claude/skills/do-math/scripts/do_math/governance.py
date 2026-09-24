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

from .repository import canonical_json, exact_content_hash, new_id
from .academic import requirement_record

WORK_ROLES = {"research_work", "supplemental_research", "task_contract_review", "identity_review", "goal_audit", "formal_check"}
OPERATING_ROLES = {"research_preparation", "research_plan", "operational_review", "intent_interpretation", "maintenance",
                   "trust_check", "trust_activate"}

GOVERNANCE_KINDS = {"charter", "policy", "research_context", "additional_audit"}


def digest(value: Any) -> str:
    # User wording can explicitly concern literal Unicode/codepoint identity.
    # Canonical storage syntax and lossless authority payloads are distinct.
    return exact_content_hash(value)


def preserve_source(identifier: str, text: str, *, origin: str, revision: int = 1) -> dict:
    """Preserve exact input, not a normalized or interpreted substitute."""
    _require_text(identifier, "source id"); _require_text(text, "source text"); _require_text(origin, "origin")
    if type(revision) is not int or revision < 1:
        raise ValueError("source revision must be positive")
    raw = text.encode("utf-8")
    return {"id": identifier, "text": text, "origin": origin, "revision": revision,
            "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)}


def validate_source(source: dict) -> None:
    if not isinstance(source, dict): raise ValueError("immutable source required")
    expected = preserve_source(source.get("id"), source.get("text"), origin=source.get("origin"), revision=source.get("revision"))
    if any(source.get(key) != expected[key] for key in expected):
        raise ValueError("immutable source bytes or revision changed")


def _strings(value, label, *, nonempty=False):
    if not isinstance(value, list) or any(not isinstance(v, str) or not v.strip() for v in value) or len(set(value)) != len(value) or (nonempty and not value):
        raise ValueError(label + " requires distinct nonempty strings")
    return value


def validate_governance_record(record: dict) -> None:
    if not isinstance(record, dict) or record.get("kind") not in GOVERNANCE_KINDS:
        raise ValueError("unsupported governance record kind")
    _require_text(record.get("id"), "record id")
    if type(record.get("revision")) is not int or record["revision"] < 1:
        raise ValueError("governance revision must be positive")
    _strings(record.get("supersedes"), "supersedes")
    if record["id"] in record["supersedes"]: raise ValueError("self supersession")
    c = record.get("content")
    if not isinstance(c, dict): raise ValueError("governance content required")
    kind = record["kind"]
    if kind == "charter":
        for key in ("rationale", "goal", "desired_result", "evidence_boundary", "decision_authority"):
            _require_text(c.get(key), key)
        if c["decision_authority"] != "user": raise ValueError("charter authority cannot create a new decision owner")
        for key in ("success_criteria", "partial_success_criteria", "included_scope", "excluded_scope", "priorities", "preferences", "stop_conditions"):
            _strings(c.get(key), key, nonempty=key in {"success_criteria", "included_scope"})
        requirement_record(c.get("academic_requirements"))
    elif kind == "policy":
        _require_text(c.get("rule_id"), "rule id"); _require_text(c.get("text"), "rule text")
        _strings(c.get("scope"), "rule scope", nonempty=True)
        _strings(c.get("reason_refs"), "rule reasons", nonempty=True)
        _strings(c.get("audit_refs"), "rule audits")
    elif kind == "research_context":
        terms = c.get("terms")
        if not isinstance(terms, list) or not terms: raise ValueError("context terms required")
        seen = set()
        for term in terms:
            if not isinstance(term, dict): raise ValueError("context term must be an object")
            for key in ("term", "definition", "boundary"): _require_text(term.get(key), key)
            if term["term"] in seen: raise ValueError("duplicate context term")
            seen.add(term["term"])
            _strings(term.get("avoid_synonyms"), "avoided synonyms")
            _strings(term.get("record_refs"), "definition references")
    else:
        _strings(c.get("scope"), "audit scope", nonempty=True)
        _strings(c.get("required_inputs"), "audit inputs", nonempty=True)
        _require_text(c.get("assessor"), "audit assessor")
        mapping = c.get("verdict_mapping")
        if not isinstance(mapping, dict) or not mapping or any(not k or v not in {"satisfied", "not_satisfied", "unresolved"} for k, v in mapping.items()):
            raise ValueError("audit needs explicit universal verdict mapping")
    if "document" in record:
        document = record["document"]
        if not isinstance(document, dict): raise ValueError("document reference required")
        _require_text(document.get("ref"), "document ref")
        if len(document.get("sha256", "")) != 64: raise ValueError("document bytes hash required")


def _install_record(instance, record, approval_ref, source_ref):
    validate_governance_record(record)
    records = instance.setdefault("governance", {})
    identifier, kind = record["id"], record["kind"]
    if identifier in records: raise ValueError("governance ID is immutable")
    for old_id in record["supersedes"]:
        old = records.get(old_id)
        if not old or old["kind"] != kind or old["status"] != "active": raise ValueError("supersession must name an active same-kind record")
    if kind == "charter" and any(r["kind"] == kind and r["status"] == "active" and r["id"] not in record["supersedes"] for r in records.values()):
        raise ValueError("one active charter must own the goal")
    if kind == "policy" and any(r["kind"] == kind and r["status"] == "active" and r["content"]["rule_id"] == record["content"]["rule_id"] and r["id"] not in record["supersedes"] for r in records.values()):
        raise ValueError("same rule requires explicit supersession")
    for old_id in record["supersedes"]: records[old_id].update(status="superseded", superseded_by=identifier)
    records[identifier] = {**deepcopy(record), "status": "active", "approval_ref": approval_ref, "source_ref": source_ref,
                           "content_sha256": digest(record)}


def initialize_governance(instance, source, approval, records, *, approval_source=None):
    """Install an exactly approved first charter; no grant is inferred from defaults."""
    validate_source(source)
    immutable = instance.get("lifecycle", {}).get("immutable_input")
    if immutable and any(immutable.get(k) != source[k] for k in ("text", "sha256", "bytes")):
        raise ValueError("initial charter source differs from initialization immutable input")
    if instance.get("governance"): raise ValueError("governance is already initialized")
    approval_source = source if approval_source is None else approval_source
    validate_source(approval_source)
    if not isinstance(approval, dict) or approval.get("actor") != "user" or approval.get("source_ref") != approval_source["id"] or approval.get("source_sha256") != approval_source["sha256"]:
        raise ValueError("initialization requires actual user approval of the immutable input")
    if approval.get("input_source_ref", approval["source_ref"]) != source["id"] or approval.get("input_source_sha256",approval["source_sha256"]) != source["sha256"]:
        raise ValueError("approval does not bind the original initialization input")
    _require_text(approval.get("id"), "approval id")
    if not records or len({r["id"] for r in records}) != len(records) or approval.get("record_hashes") != {r["id"]: digest(r) for r in records}:
        raise ValueError("approval must bind the exact proposed records")
    result = deepcopy(instance)
    if source["id"] in result.get("governance_sources", {}) and result["governance_sources"][source["id"]] != source:
        raise ValueError("source ID already bound")
    if approval["id"] in result.get("decisions", {}): raise ValueError("initial approval ID already exists")
    result.setdefault("governance_sources", {})[source["id"]] = deepcopy(source)
    if approval_source["id"] in result["governance_sources"] and result["governance_sources"][approval_source["id"]] != approval_source:
        raise ValueError("approval original source ID already bound")
    result["governance_sources"][approval_source["id"]] = deepcopy(approval_source)
    result.setdefault("decisions", {})[approval["id"]] = deepcopy(approval)
    result.setdefault("grants", {})
    for record in records: _install_record(result, record, approval["id"], source["id"])
    if sum(r["kind"] == "charter" for r in records) != 1: raise ValueError("initialization needs exactly one approved charter")
    result["governance_approval"] = {"decision_ref": approval["id"], "source_ref": source["id"], "source_sha256": source["sha256"]}
    result["goal_status"] = "unsolved"
    validate_governance_state(result)
    return result


def governance_view(instance):
    """Derive the current research view from approved governance records."""
    active = [deepcopy(r) for r in instance.get("governance", {}).values() if r["status"] == "active"]
    charters = [r for r in active if r["kind"] == "charter"]
    if len(charters) != 1: raise ValueError("no unique approved charter")
    charter = charters[0]; policies = sorted((r for r in active if r["kind"] == "policy"), key=lambda r: r["id"])
    return {"charter": charter, "goal": charter["content"]["goal"], "goal_revision": charter["revision"],
            "policies": "\n\n".join(r["content"]["text"] for r in policies), "policy_revision": digest(policies), "policy_records": policies,
            "research_context": [r for r in active if r["kind"] == "research_context"],
            "additional_audits": [r for r in active if r["kind"] == "additional_audit"],
            "academic_requirements": requirement_record(charter["content"]["academic_requirements"])}


def validate_governance_state(instance):
    """Domain validation callable before publication, independent of file layout."""
    if any(k in instance for k in ("goal", "policies", "goal_revision", "policy_revision", "academic_requirements")):
        raise ValueError("parallel governance authority in feature 5")
    if instance.get("goal_status", "unsolved") not in {"unsolved", "mathematically_solved"}: raise ValueError("unsupported final goal assurance")
    known = set(instance.get("governance", {})) | set(instance.get("decisions", {}))
    for family in ("knowledge", "formal_results", "expositions", "research_records"):
        known.update(instance.get(family, {}))
    for record in instance.get("governance", {}).values():
        validate_governance_record(record)
        if record.get("approval_ref") not in instance.get("decisions", {}): raise ValueError("governance approval missing")
        source = instance.get("governance_sources", {}).get(record.get("source_ref")); validate_source(source)
        proposal = {k: deepcopy(v) for k, v in record.items() if k not in {"status", "approval_ref", "source_ref", "content_sha256", "superseded_by"}}
        approval = instance["decisions"][record["approval_ref"]]
        approved_hash = approval.get("record_hashes", {}).get(record["id"])
        if approved_hash is None and approval.get("change", {}).get("record") is not None:
            approved_hash = digest(approval["change"]["record"])
        approval_source = instance.get("governance_sources", {}).get(approval.get("source_ref"))
        validate_source(approval_source)
        if (approval.get("actor") != "user" or approval.get("revoked")
                or approval.get("input_source_ref",approval.get("source_ref")) != source["id"]
                or approval.get("input_source_sha256",approval.get("source_sha256")) != source["sha256"]
                or approval.get("source_sha256") != approval_source["sha256"]):
            raise ValueError("record lacks actual source-bound user approval")
        if digest(proposal) != record.get("content_sha256") or approved_hash != digest(proposal):
            raise ValueError("governance content differs from approved proposal")
        if record.get("status") not in {"active", "superseded"}: raise ValueError("invalid governance lifecycle")
        if record["status"] == "superseded":
            successor = instance["governance"].get(record.get("superseded_by"), {})
            if record["id"] not in successor.get("supersedes", []) or successor.get("kind") != record["kind"]:
                raise ValueError("broken governance supersession")
        c = record["content"]; refs = c.get("reason_refs", []) + c.get("audit_refs", []) + c.get("required_inputs", [])
        refs += [ref for term in c.get("terms", []) for ref in term["record_refs"]]
        if set(refs) - known: raise ValueError("governance reference does not resolve")
    if instance.get("governance"): governance_view(instance)


def evaluate_additional_audit(instance, audit_id, verdict, *, assessor, input_hashes, runtime=None):
    """Map the approved audit's verdict; this is not a final goal assurance."""
    validate_governance_state(instance)
    audit = instance.get("governance", {}).get(audit_id, {})
    if audit.get("kind") != "additional_audit" or audit.get("status") != "active": raise ValueError("audit is not current")
    content = audit["content"]
    if assessor != content["assessor"] or verdict not in content["verdict_mapping"]: raise ValueError("audit assessor or verdict differs from approval")
    from .planning import _records
    records = _records(instance, runtime or {})
    if set(input_hashes) != set(content["required_inputs"]): raise ValueError("audit inputs differ from the approved required set")
    for ref in content["required_inputs"]:
        record = records.get(ref, (None, None))[1]
        if record is None or input_hashes.get(ref) != digest(record): raise ValueError("audit required input is absent or stale")
    return {"audit_ref": audit_id, "audit_sha256": digest(audit), "assessor": assessor, "verdict": verdict,
            "decision": content["verdict_mapping"][verdict], "input_hashes": deepcopy(input_hashes)}


def additional_audit_input(instance, runtime=None):
    """Fixed contracts and exact required records delivered to a goal auditor.

    Every active additional audit is required at the final goal gate. Its scope
    tells the assessor what to compare, not permission to silently omit it.
    """
    from .planning import _records
    records = _records(instance, runtime or {})
    result = []
    for audit in sorted(instance.get("governance", {}).values(), key=lambda row: row["id"]):
        if audit.get("kind") != "additional_audit" or audit.get("status") != "active": continue
        inputs = {}
        for ref in audit["content"]["required_inputs"]:
            record = records.get(ref, (None, None))[1]
            if record is None: raise ValueError("additional audit required input is unavailable: " + ref)
            inputs[ref] = deepcopy(record)
        result.append({"audit": deepcopy(audit), "audit_sha256": digest(audit), "inputs": inputs,
                       "input_hashes": {ref: digest(record) for ref, record in inputs.items()}})
    return result


def additional_audit_schema(instance):
    """Producer schema for output.additional_audits; receiver also checks identity."""
    options = []
    for audit in instance.get("governance", {}).values():
        if audit.get("kind") != "additional_audit" or audit.get("status") != "active": continue
        content = audit["content"]
        fields = {"audit_ref": {"const": audit["id"]}, "assessor": {"const": content["assessor"]},
                  "verdict": {"enum": list(content["verdict_mapping"])}, "reason": {"type": "string", "minLength": 1},
                  "input_hashes": {"type": "object", "additionalProperties": False,
                     "properties": {ref: {"type": "string", "pattern": "^[0-9a-f]{64}$"} for ref in content["required_inputs"]},
                     "required": list(content["required_inputs"])}}
        options.append({"type": "object", "additionalProperties": False, "properties": fields, "required": list(fields)})
    return {"type": "array", "items": {"oneOf": options} if options else False,
            "minItems": len(options), "maxItems": len(options)}


def evaluate_goal_audits(instance, runtime, execution_id, results):
    """Map actual producer verdicts on the exact delivered, still-current input."""
    execution = runtime.get("executions", {}).get(execution_id, {})
    current = additional_audit_input(instance, runtime)
    if execution.get("role") != "goal_audit" or execution.get("additional_audit_input") != current:
        raise ValueError("goal auditor did not receive these current additional-audit inputs")
    if not isinstance(results, list) or len(results) != len(current): raise ValueError("all additional audits require actual verdicts")
    expected = {row["audit"]["id"] for row in current}
    if any(not isinstance(row, dict) for row in results) or {row.get("audit_ref") for row in results} != expected:
        raise ValueError("additional audit result identity differs")
    mapped = []
    for row in results:
        _require_text(row.get("reason"), "audit reason")
        evaluation = evaluate_additional_audit(instance, row["audit_ref"], row.get("verdict"),
            assessor=row.get("assessor"), input_hashes=row.get("input_hashes", {}), runtime=runtime)
        mapped.append({**evaluation, "execution_id": execution_id, "reason": row["reason"]})
    return mapped


def validate_goal_additional_audits(instance, judgments, *, runtime=None):
    """A generic satisfied verdict cannot bypass a required project audit."""
    expected = {row["audit"]["id"] for row in additional_audit_input(instance, runtime)}
    for judgment in judgments:
        results = judgment.get("additional_audits", [])
        if not isinstance(results, list) or len(results) != len(expected) or {row.get("audit_ref") for row in results} != expected:
            raise ValueError("goal judgment omits a current additional audit")
        for row in results:
            actual = evaluate_additional_audit(instance, row["audit_ref"], row.get("verdict"),
                assessor=row.get("assessor"), input_hashes=row.get("input_hashes", {}), runtime=runtime)
            if any(row.get(key) != value for key, value in actual.items()) or row.get("execution_id") != judgment.get("execution_id"):
                raise ValueError("additional audit mapping or judgment binding changed")
            _require_text(row.get("reason"), "audit reason")
            if actual["decision"] != "satisfied": raise ValueError("additional audit does not establish goal satisfaction")


def _apply_domain_decision(instance, runtime, change, source_ref, actor, at):
    if actor != "user": raise ValueError("preserved user decision required")
    validate_source(instance.get("governance_sources", {}).get(source_ref))
    result, state = deepcopy(instance), deepcopy(runtime)
    decision_id = change.get("decision_id") or new_id("DC")
    old = result.setdefault("decisions", {}).get(decision_id)
    if old:
        if old.get("change") != change or old.get("source_ref") != source_ref: raise ValueError("decision ID reused")
        return result, state, old
    record = change.get("record")
    if not isinstance(record, dict): raise ValueError("governance decision requires a structured governance record")
    if record.get("kind") != change["kind"]: raise ValueError("record owner differs from decision kind")
    previous_charter = governance_view(instance)["charter"]
    academic_only = (record["kind"] == "charter"
                     and {k: v for k, v in previous_charter["content"].items() if k != "academic_requirements"}
                     == {k: v for k, v in record.get("content", {}).items() if k != "academic_requirements"}
                     and previous_charter.get("document") == record.get("document"))
    event = {"id": decision_id, "kind": change["kind"], "actor": "user", "change": deepcopy(change), "source_ref": source_ref,
             "source_sha256": result["governance_sources"][source_ref]["sha256"], "created_at": timestamp(at).isoformat(), "affected": []}
    result["decisions"][decision_id] = event
    _install_record(result, record, decision_id, source_ref)
    validate_governance_state(result)
    if record["kind"] == "charter" and not academic_only: result["goal_status"] = "unsolved"
    for task in state.get("tasks", {}).values():
        if task.get("status") in {"completed", "closed"}: continue
        if academic_only and not task.get("academic_requirement_id"): continue
        event["affected"].append(task["id"])
        task["governance_revision_required"] = {"decision_ref": decision_id, "record_ref": record["id"]}
        if isinstance(task.get("assessment"), dict): task["assessment"]["current"] = False
    for execution in state.get("executions", {}).values():
        if (execution.get("status") != "ended" and record["kind"] in {"charter", "policy"}
                and (not academic_only or state.get("tasks", {}).get(execution.get("action", {}).get("target"), {}).get("academic_requirement_id"))
                and execution.get("role") in WORK_ROLES | {"research_preparation", "research_plan"}
                and not execution.get("action", {}).get("review_cycle_id")):
            execution["stop_requested"] = "governance_changed"
            event["affected"].append(execution["id"])
    _queue(state, "research_plan" if academic_only else "research_preparation", "approved governance changed",
           decision_id=decision_id, affected_ids=event["affected"])
    if change.get("resolves_questions"):
        from .questions import resolve_user
        resolve_user(state, change["resolves_questions"], resolution_ref=decision_id, affected_ids=[result["id"], record["id"], *event["affected"]])
    state.setdefault("history", []).append({"kind": "governance_decision", "decision_id": decision_id})
    return result, state, event


def timestamp(value: str | None = None) -> datetime:
    result = datetime.fromisoformat(value.replace("Z", "+00:00")) if value else datetime.now(timezone.utc)
    if result.tzinfo is None:
        raise ValueError("a timezone is required")
    return result.astimezone(timezone.utc)


def ensure_governance(instance: dict) -> dict:
    result = deepcopy(instance)
    result.setdefault("governance", {})
    result.setdefault("governance_sources", {})
    result.setdefault("decisions", {})
    result.setdefault("grants", {})
    return result


def grant_case_id(action, runtime):
    """Logical case identity from the operation ledger, never a supplied case_id.

    An HTTP operation owns all of its local execution attempts. AC-OP is only
    an action name; its external role and stored operation target establish the
    relationship. Other actions retain their own identity.
    """
    identifier = action.get("id")
    operations = (runtime or {}).get("external_operations", {})
    if action.get("role") == "external_operation":
        matches = [o for o in operations.values() if identifier in {o.get("id"), o.get("action_id")}]
    elif action.get("role") == "external_action":
        matches = [o for o in operations.values() if action.get("target") == o.get("id")]
    else:
        matches = []
    if len(matches) > 1: raise ValueError("ambiguous external case identity")
    if matches:
        operation = matches[0]
        if action.get("grant_id") and operation.get("grant_id") != action["grant_id"]:
            raise ValueError("external case grant differs")
        return ("external_operation", operation["id"])
    return ("action", identifier)


def grant_scope_reason(grant, action, runtime, *, at=None):
    """Check explicit authority; execution/operation ledgers own consumption."""
    now = timestamp(at)
    if grant.get("status") != "active": return "grant is not active"
    if grant.get("expires_at") and timestamp(grant["expires_at"]) <= now: return "grant expired"
    if grant.get("valid_from") and timestamp(grant["valid_from"]) > now: return "grant is not effective yet"
    target = action.get("target")
    if target in grant.get("excluded_targets", []): return "target excluded"
    for field in ("included_targets", "task_ids"):
        if grant.get(field) and target not in grant[field]: return "target outside grant"
    if grant.get("subjects") and action.get("subject", action.get("role")) not in grant["subjects"]: return "subject outside grant"
    if grant.get("budget_kind") and action.get("budget_kind") != grant["budget_kind"]: return "resource pool outside grant"
    if grant.get("execution_kinds") and action.get("actor_kind") not in grant["execution_kinds"]: return "execution kind outside grant"
    if grant.get("purposes") and action.get("purpose") not in grant["purposes"]: return "purpose outside grant"
    if grant.get("resource_limits"):
        # Enforcement belongs to the reservation/profile owner, never a caller's boolean claim.
        return "resource-limited grant requires reservation-owner enforcement"
    if grant.get("reuse", "once") == "once":
        if runtime is None or not action.get("id"): return "one-case authority requires action identity and current ledger"
        try:
            wanted = grant_case_id({**action, "grant_id": grant["id"]}, runtime)
            used = [grant_case_id({**e.get("action", {"id": e.get("action_id", e.get("id"))}), "grant_id": e["grant_id"]}, runtime)
                    for e in runtime.get("executions", {}).values() if e.get("grant_id") == grant["id"]]
            used += [("external_operation", o["id"]) for o in runtime.get("external_operations", {}).values()
                     if o.get("grant_id") == grant["id"]]
        except ValueError as error:
            return str(error)
        if any(case != wanted for case in used):
            return "one-case grant already reserved or consumed"
    elif grant.get("reuse") != "reusable": return "unknown grant reuse contract"
    return None


def authorize(instance: dict, action: dict, at: str | None = None, *, runtime: dict | None = None) -> dict:
    now = timestamp(at)
    role, target = action["role"], action.get("target")
    accepted = []
    rejected = []
    requested_grant = action.get("grant_id")
    for grant in instance.get("grants", {}).values():
        if requested_grant is not None and grant.get("id") != requested_grant:
            continue
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
        if reason is None:
            reason = grant_scope_reason(grant, action, runtime, at=at)
        if reason:
            rejected.append({"grant_id": grant["id"], "reason": reason})
        else:
            accepted.append(grant)
    if not accepted:
        return {"allowed": False, "grant_id": None, "reason": "no current grant permits this action", "rejected": rejected}
    if len(accepted) != 1:
        return {"allowed": False, "grant_id": None, "reason": "ambiguous current grants", "rejected": rejected}
    grant = accepted[0]
    return {"allowed": True, "grant_id": grant["id"],
            "grant_sha256": hashlib.sha256(canonical_json(grant)).hexdigest(),
            "expires_at": grant.get("expires_at"), "checkpoint_allowed": grant.get("checkpoint_allowed", False)}


def _require_text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be nonempty text")
    return value


def validate_grant_source(instance, grant):
    """Resolve the exact preserved approval, not an origin label or caller claim."""
    source = instance.get("governance_sources", {}).get(grant.get("source_ref"))
    validate_source(source)
    decision = instance.get("decisions", {}).get(grant.get("decision_id"), {})
    if (decision.get("actor") != "user" or decision.get("kind") != "grant" or decision.get("revoked")
            or decision.get("status", "active") != "active" or decision.get("source_ref") != source["id"]
            or decision.get("source_sha256", source["sha256"]) != source["sha256"]):
        raise ValueError("grant lacks current source-bound user approval")
    approved = deepcopy(decision.get("change", {}).get("grant", {}))
    approved.update(id=grant["id"], status="active", expires_at=approved.get("expires_at"),
                    created_at=decision["created_at"], source_ref=source["id"], decision_id=decision["id"])
    approved.setdefault("reuse", "once")
    for field in ("included_targets", "excluded_targets", "subjects", "execution_kinds", "purposes"):
        approved.setdefault(field, [])
    if approved != grant: raise ValueError("grant differs from the actual approved scope")


def authorize_review_replacement(instance, runtime, action, *, delegation_id=None, case=None, at=None):
    """Check authority only; REVIEWS owns the failed slot and continuity transition."""
    try:
        if action.get("role") != "identity_review" or action.get("purpose") != "record_replacement":
            raise ValueError("replacement must identify its role and purpose")
        fields = ("review_cycle_id", "stage", "slot", "round", "replacement_for", "continuity_break_cause")
        if any(field not in action for field in fields): raise ValueError("replacement needs the exact failed slot and cause")
        authority = authorize(instance, action, at, runtime=runtime)
        if not authority["allowed"]: return authority
        validate_grant_source(instance, instance["grants"][authority["grant_id"]])
        if delegation_id is None:
            if case is not None: raise ValueError("case reuse must identify its delegation")
            return {**authority, "authority_mode": "machine_grant"}
        from .delegations import case_basis_reference_ids, authorize_delegated_case
        if (not isinstance(case, dict) or case.get("target_id") != action.get("target")
                or case.get("effect") != {field: action[field] for field in fields}
                or action["review_cycle_id"] not in case_basis_reference_ids(case)):
            raise ValueError("delegated replacement differs from the checked target, slot or cycle basis")
        delegated = authorize_delegated_case(instance, delegation_id, case, runtime=runtime, now_iso=at)
        if not delegated["allowed"]: return delegated
        return {**authority, "authority_mode": "checked_case", "delegation": delegated}
    except (ValueError, KeyError, TypeError) as error:
        return {"allowed": False, "grant_id": action.get("grant_id"), "reason": str(error)}


def _queue(runtime: dict, role: str, reason: str, **fields: Any) -> None:
    action = {"id": new_id("AC"), "role": role, "reason": reason, **fields}
    action.setdefault("lineage_id", action["id"])
    runtime.setdefault("queue", []).append(action)


def _dispose_grant_consumers(runtime, gid, event, reason):
    for eid, execution in runtime.get("executions", {}).items():
        if execution.get("grant_id") == gid and execution.get("status") != "ended":
            execution["stop_requested"] = reason
            event["affected"].append(eid)
    # Pinned requests cannot fall through to another overlapping authority.
    runtime["queue"] = [a for a in runtime.get("queue", []) if a.get("grant_id") != gid]
    for operation in runtime.get("external_operations", {}).values():
        if operation.get("grant_id") == gid and operation.get("status") == "prepared":
            if not operation.get("transmitted") and operation.get("transmission_phase") != "recorded":
                operation.update(status="cancelled", transmitted=False, cancellation={"authority_event_ref":event["id"],"reason":reason})
            else:
                operation.update(status="unknown", handling="reconciliation_required")
            event["affected"].append(operation["id"])


def expire_grants(instance, runtime, *, at):
    """Mechanical deadline effects; no new approval, grant, or research decision."""
    result, state = deepcopy(instance), deepcopy(runtime)
    events = []
    for gid, grant in result.get("grants", {}).items():
        if grant.get("status") != "active" or not grant.get("expires_at") or timestamp(grant["expires_at"]) > timestamp(at): continue
        event = {"id":new_id("GX"),"kind":"grant_expiry","grant_id":gid,"at":at,"affected":[]}
        grant.update(status="expired",expired_at=at,expiry_event_ref=event["id"])
        _dispose_grant_consumers(state,gid,event,"grant_expired")
        state.setdefault("governance_events",[]).append(event)
        events.append(event)
    return result,state,events


def apply_decision(instance: dict, runtime: dict, change: dict, *, source_ref: str,
                   actor: str = "user", at: str | None = None) -> tuple[dict, dict, dict]:
    """Apply one explicit decision atomically to copies of the two roots."""
    if actor != "user" or not source_ref:
        raise ValueError("a preserved user decision is required")
    if change.get("kind") in GOVERNANCE_KINDS:
        return _apply_domain_decision(instance, runtime, change, source_ref, actor, at)
    instance, runtime = ensure_governance(instance), deepcopy(runtime)
    validate_source(instance.get("governance_sources", {}).get(source_ref, {}))
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
    source = instance.get("governance_sources", {}).get(source_ref)
    validate_source(source)
    event["source_sha256"] = source["sha256"]
    if kind == "grant":
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
        spec.setdefault("reuse", "once")
        if spec["reuse"] not in {"once", "reusable"}: raise ValueError("grant reuse must be explicit once or reusable")
        for field in ("included_targets", "excluded_targets", "subjects", "execution_kinds", "purposes"):
            _strings(spec.setdefault(field, []), field)
        if spec.get("resource_limits"):
            raise ValueError("resource limits require an enforcing reservation contract; unsupported limits cannot be granted")
        if spec.get("valid_from"): timestamp(spec["valid_from"])
        if spec.get("valid_from") and expires and timestamp(spec["valid_from"]) >= timestamp(expires):
            raise ValueError("grant has an empty effective interval")
        instance["grants"][gid] = spec
        replaces = change.get("replaces", [])
        _strings(replaces, "replaced grants")
        for old_id in replaces:
            previous = instance["grants"].get(old_id)
            if previous is None or old_id == gid or previous["status"] != "active": raise ValueError("replacement requires distinct active grants")
            previous.update(status="revoked", revoked_at=when, revoked_by=decision_id, replaced_by=gid)
            _dispose_grant_consumers(runtime,old_id,event,"grant_revoked")
        event["grant_id"] = gid
        lifecycle = instance.get("lifecycle", {}).get("state")
        initializing = lifecycle == "initializing" or (
            lifecycle == "paused" and runtime.get("resume_lifecycle") == "initializing")
        if not initializing:
            # The decision is a reason to reconsider, not the permission for
            # that planning execution. Activation opens the first research work.
            _queue(runtime, "research_plan", "new execution authority", decision_id=decision_id)
    elif kind == "revoke":
        gid = change.get("grant_id")
        if gid not in instance["grants"]:
            raise ValueError("grant not found")
        instance["grants"][gid].update(status="revoked", revoked_at=when, revoked_by=decision_id)
        event["grant_id"] = gid
        _dispose_grant_consumers(runtime,gid,event,"grant_revoked")
    elif kind == "delegation":
        from .delegations import validate_delegation
        delegation = deepcopy(change.get("delegation"))
        if not isinstance(delegation, dict):
            raise ValueError("delegation decision requires a delegation record")
        delegation.update(source_ref=source_ref, decision_id=decision_id, created_at=when)
        delegation = validate_delegation(delegation, now_iso=when)
        original = instance["decisions"].get(delegation["original_decision_id"], {})
        if original.get("actor") != "user" or original.get("kind") != delegation["decision_kind"] or original.get("revoked"):
            raise ValueError("delegation must bind an actual current user decision of the same kind")
        instance.setdefault("delegations", {})
        if delegation["id"] in instance["delegations"]:
            raise ValueError("delegation ID already exists")
        instance["delegations"][delegation["id"]] = delegation
        event["delegation_id"] = delegation["id"]
    elif kind == "revoke_delegation":
        delegation = instance.get("delegations", {}).get(change.get("delegation_id"))
        if delegation is None: raise ValueError("delegation not found")
        delegation.update(status="revoked", revoked_by=decision_id, revoked_at=when)
        event["delegation_id"] = delegation["id"]
    elif kind == 'repetition_continue':
        from .revisions import continue_repetition
        instance['decisions'][decision_id] = event
        continue_repetition(instance, runtime, change, event)
    elif kind == "question_answer":
        _require_text(change.get("text"), "answer text")
        identifiers = change.get("resolves_questions", [])
        if not identifiers:
            raise ValueError("a question answer must identify its questions")
        by_id = {row["id"]: row for row in runtime.get("question_links", [])}
        targets = change.get("target_ids")
        _strings(targets, "answer affected targets", nonempty=True)
        for identifier in identifiers:
            if identifier not in by_id:
                raise ValueError("unknown question: " + str(identifier))
            relevant = by_id[identifier].get("unresolved_target_ids", by_id[identifier]["target_ids"])
            if targets is not None and set(targets) - set(relevant): raise ValueError("answer names unrelated or already resolved targets")
            event["affected"].extend(targets if targets is not None else relevant)
    elif kind == "task_scope":
        from .planning import contract_hash
        from .task_contracts import validate_task_contract
        tid = change.get("task_id")
        task = runtime["tasks"].get(tid)
        if task is None or task["status"] in {"completed", "closed"}:
            raise ValueError("task scope decision requires an unfinished task")
        validate_task_contract(task)
        if change.get("revision") != task["revision"] or change.get("contract_sha256") != contract_hash(task):
            raise ValueError("scope approval must bind the exact task contract edition")
        disposition = change.get("disposition")
        if disposition not in {"revise", "waive", "transfer"}:
            raise ValueError("v5 scope approval requires revise, waive or transfer of named obligations")
        reason = _require_text(change.get("reason"), "scope reason")
        if disposition in {"waive", "transfer"}:
            ids = _strings(change.get("obligation_ids"), "approved obligations", nonempty=True)
            if set(ids) - {row["id"] for row in task["completion_obligations"]}:
                raise ValueError("scope approval names an unknown obligation")
            if disposition == "transfer":
                recipient = runtime["tasks"].get(change.get("target_task_id"))
                if not recipient or recipient["id"] == tid or recipient["status"] in {"completed", "closed"}:
                    raise ValueError("scope transfer requires a distinct unfinished recipient")
                validate_task_contract(recipient)
            # This is authority, not a second application of TASKS' lifecycle.
            _queue(runtime, "research_plan", reason, scope_decision_id=decision_id)
        else:
            task["revision_requested"] = {"source": decision_id, "revision": task["revision"], "reason": reason}
            from .revisions import capture_targets
            _queue(runtime, "research_preparation", reason, target=tid,
                   revision_targets=capture_targets(instance, runtime, [tid], required=True, source_ref=decision_id))
        event["affected"].append(tid)
    else:
        raise ValueError(f"unsupported governance decision: {kind}")
    if change.get("resolves_questions"):
        from .questions import resolve_user
        affected = set(event["affected"])
        if kind == "grant":
            granted = instance["grants"][event["grant_id"]]
            affected.update(granted.get("task_ids") or [instance["id"]])
            affected.add(event["grant_id"])
        resolve_user(runtime, change["resolves_questions"], resolution_ref=decision_id, affected_ids=affected)
    instance["decisions"][decision_id] = event
    runtime.setdefault("history", []).append({"kind": "governance_decision", "decision_id": decision_id, "source_ref": source_ref})
    return instance, runtime, event


def _import_basis(instance, runtime, output):
    """Bind the governance and records actually referenced by this interpretation."""
    from .planning import contract_hash
    from .planning import _records
    reference_fields = {'owner_ref', 'decision_refs', 'used_sources', 'source_refs', 'supersedes',
        'target_ids', 'task_ids', 'resolves_questions', 'grant_id', 'replaces',
        'original_decision_id', 'task_id', 'target_task_id', 'included_targets', 'excluded_targets',
        'record_refs', 'dependencies', 'basis_refs', 'authority_refs', 'formal_result_ref', 'input_refs'}
    references = set()
    def collect(value):
        if isinstance(value, dict):
            for key, child in value.items():
                if key in reference_fields:
                    references.update(x for x in (child if isinstance(child, list) else [child]) if isinstance(x, str))
                collect(child)
        elif isinstance(value, list):
            for child in value:
                collect(child)
    collect(output)
    # Current research governance constrains every interpretation. Unrelated
    # task progress, decisions and grants are not part of that premise.
    governance = {key: row for key, row in instance.get('governance', {}).items() if row.get('status') == 'active'}
    records = {key: row for key, (_, row) in _records(instance, runtime).items()}
    if instance.get('id'):
        # An owner coordinate naming the instance is not a dependency on
        # every nested record. Domain handlers capture their own settings.
        records[instance['id']] = {'id': instance['id']}
    records.update(instance.get('governance_sources', {}))
    from .input_basis import aliases
    for source in instance.get('sources', []):
        for alias in aliases(source):
            records.setdefault(alias, source)
    records.update({row['id']: row for row in runtime.get('question_links', [])})
    for row in governance.values():
        references.update(row[key] for key in ('approval_ref', 'source_ref') if row.get(key))
    pending = list(references)
    while pending:
        row = records.get(pending.pop(), {})
        for key in ('source_ref', 'decision_id'):
            ref = row.get(key)
            if isinstance(ref, str) and ref not in references:
                references.add(ref)
                pending.append(ref)
    return digest({'governance': governance,
        'references': {ref: deepcopy(records.get(ref)) for ref in sorted(references)}})


def register_import_owner(handlers, kind, *, apply, validate, basis, contract=None):
    """Register trusted domain code, not model-submitted functions or authority.

    validate(i,r,unit) checks the owner's actual candidate contract;
    basis(i,r,unit) returns only premises whose changes invalidate interpretation;
    apply(i,r,unit,approval) returns the two roots using that same owner contract.
    ENGINE supplies configuration's existing configure consumer through this API.
    """
    _require_text(kind, "import owner kind")
    if kind in GOVERNANCE_KINDS or kind in {"grant", "revoke", "delegation", "question_answer", "task_scope"}:
        raise ValueError("cannot replace a governance authority owner")
    if kind in handlers: raise ValueError("import owner already registered")
    if not all(callable(fn) for fn in (apply, validate, basis)): raise ValueError("owner needs apply, validate and currentness functions")
    handlers[kind] = {"apply": apply, "validate": validate, "basis": basis}
    if contract is not None:
        if not isinstance(contract, dict) or not contract:
            raise ValueError('import owner contract must be a nonempty object')
        handlers[kind]['contract'] = deepcopy(contract)
    return handlers


def import_consumer_catalog(handlers=None):
    """Publish the actual registered kinds and their producer-facing contracts."""
    owners = _owner_handlers(handlers)
    builtins = GOVERNANCE_KINDS | {'grant', 'revoke', 'delegation', 'question_answer', 'task_scope',
                                  'configuration', 'research_record', 'evidence'}
    kinds = GOVERNANCE_KINDS | {'grant', 'revoke', 'delegation', 'question_answer', 'task_scope'} | set(owners)
    rows = []
    for kind in sorted(kinds):
        contract = owners.get(kind, {}).get('contract')
        if kind in builtins:
            contract = {'document': 'references/입력-소비자.md', 'section': kind}
        if not contract:
            raise ValueError('registered import owner has no producer contract: ' + kind)
        rows.append({'owner_kind': kind, 'payload_contract': deepcopy(contract)})
    return rows


def _knowledge_import(instance, runtime, unit, approval):
    from .knowledge_io import import_candidate
    result, state, _ = import_candidate(instance, runtime, unit["payload"]["record"],
        source_ref=approval["source_ref"], actor_ref=approval.get("execution_id", approval["source_ref"]))
    return result, state


def _validate_knowledge_import(instance, runtime, unit):
    from .knowledge_io import import_candidate
    if not unit["payload"]: return
    candidate = unit["payload"].get("record")
    if not isinstance(candidate, dict) or candidate.get("id") != unit["owner_ref"]:
        raise ValueError("knowledge import must name its exact candidate ID")
    # Pure owner API on copies; no publication, execution or verification occurs.
    import_candidate(instance, runtime, candidate, source_ref="import-validation", actor_ref="import-validation")


def _knowledge_import_basis(instance, runtime, unit):
    from .planning import _records
    from .knowledge_io import _lookup_definition, ensure_ontology
    from .input_basis import capture_sources
    candidate = unit["payload"].get("record", {})
    records = _records(instance, runtime)
    refs = {unit["owner_ref"], *candidate.get("dependencies", [])}
    if candidate.get("formal_result_ref"): refs.add(candidate["formal_result_ref"])
    return {"records": {ref: deepcopy(records.get(ref, (None, None))[1]) for ref in sorted(refs)},
            "kind_definition": deepcopy(_lookup_definition(ensure_ontology(instance), "knowledge", candidate.get("kind", ""))),
            "source_basis": capture_sources(instance, candidate.get("source_refs", []))}


def import_owner_handlers():
    """Built-in research candidates/evidence; extension tokens are not a closed list.

    These owners use the ordinary knowledge candidate contract. Evidence here
    means a research candidate (e.g. an observation), never automatic proof or
    arbitrary bytes promoted to verified evidence. Raw artifacts keep their
    existing artifact/source owner and can register that owner's adapter.
    """
    handlers = {}
    for kind in ("research_record", "evidence"):
        register_import_owner(handlers, kind, apply=_knowledge_import,
                              validate=_validate_knowledge_import, basis=_knowledge_import_basis)
    return handlers


def register_configuration_owner(handlers, *, apply):
    """Reuse ENGINE's actual config validation and its live-ledger apply callback.

    The callback must consume the approved patch through the same configure
    transition as public controls (profiles, stopped-mode check, reservations,
    pending selections). It must not dispatch external effects during staging.
    """
    def validate(instance, runtime, unit):
        from .engine import validate_config
        patch = unit["payload"].get("config")
        if unit["owner_ref"] != instance["id"] or not isinstance(patch, dict):
            raise ValueError("configuration import must bind this instance and an explicit config patch")
        validate_config({**instance.get("config", {}), **patch})
    def basis(instance, runtime, unit):
        return deepcopy(instance.get("config", {}))
    return register_import_owner(handlers, "configuration", apply=apply, validate=validate, basis=basis)


def _owner_handlers(handlers):
    result = import_owner_handlers()
    for kind, adapter in (handlers or {}).items():
        if kind in result and adapter == result[kind]: continue
        if not isinstance(adapter, dict): raise ValueError("owner registration needs apply/validate/basis")
        register_import_owner(result, kind, **adapter)
    return result


def _owner_basis(instance, runtime, output, handlers):
    return {unit["unit_id"]: deepcopy(handlers[unit["owner_kind"]]["basis"](instance, runtime, unit))
            for unit in output["import_units"] if unit["owner_kind"] in handlers}


def validate_import_units(instance, runtime, source, output, *, owner_handlers=None):
    """Check exact character coverage and ownership; semantic preservation is checked separately."""
    validate_source(source)
    units = output.get("import_units")
    if not isinstance(units, list) or not units: raise ValueError("import units required")
    owner_handlers = _owner_handlers(owner_handlers)
    known_owners = GOVERNANCE_KINDS | {"grant", "revoke", "delegation", "question_answer", "task_scope"} | set(owner_handlers)
    decisions = instance.get("decisions", {})
    details = output.get("question_details", [])
    if not isinstance(details, list): raise ValueError("question details required")
    qids = [q.get("id") for q in details]
    if any(not isinstance(q, str) or not q for q in qids) or len(set(qids)) != len(qids): raise ValueError("duplicate question identity")
    cursor = 0; seen = set(); referenced_questions = set()
    for unit in units:
        if not isinstance(unit, dict): raise ValueError("import unit must be an object")
        identifier = _require_text(unit.get("unit_id"), "unit id")
        if identifier in seen: raise ValueError("duplicate meaning unit")
        seen.add(identifier)
        span = unit.get("source_range", {})
        start, end = span.get("start"), span.get("end")
        if type(start) is not int or type(end) is not int or start != cursor or end <= start or end > len(source["text"]):
            raise ValueError("source coverage gap, overlap, or invalid coordinate")
        cursor = end
        _require_text(unit.get("interpretation"), "interpretation")
        _require_text(unit.get("owner_ref"), "owner ref")
        if unit.get("owner_kind") not in known_owners: raise ValueError("owner has no registered domain handler")
        if not isinstance(unit.get("payload"), dict): raise ValueError("unit payload must be an object")
        _strings(unit.get("decision_refs"), "decision references")
        _strings(unit.get("question_refs"), "question references")
        if set(unit["decision_refs"]) - set(decisions): raise ValueError("existing decision does not resolve")
        if set(unit["question_refs"]) - set(qids): raise ValueError("unit question does not resolve")
        referenced_questions.update(unit["question_refs"])
        payload = unit["payload"]
        if payload:
            if payload.get("kind") != unit["owner_kind"]: raise ValueError("payload and unit have different owners")
            if payload.get("record", {}).get("id", unit["owner_ref"]) != unit["owner_ref"]: raise ValueError("payload target differs from owner coordinate")
            kind = unit["owner_kind"]
            if kind in {"grant", "delegation"}:
                target = payload.get(kind)
                if not isinstance(target, dict) or target.get("id") != unit["owner_ref"]:
                    raise ValueError("payload target differs from owner coordinate")
            elif kind in {"revoke", "task_scope"}:
                field = "grant_id" if kind == "revoke" else "task_id"
                if payload.get(field) != unit["owner_ref"]:
                    raise ValueError("payload target differs from owner coordinate")
            elif kind == "question_answer":
                targets = payload.get("resolves_questions")
                if not isinstance(targets, list) or unit["owner_ref"] not in targets:
                    raise ValueError("payload target differs from owner coordinate")
            if kind in owner_handlers:
                owner_handlers[kind]["validate"](instance, runtime, unit)
    if cursor != len(source["text"]): raise ValueError("incomplete source coverage")
    if referenced_questions != set(qids): raise ValueError("question lacks a source meaning unit")
    indices = set()
    known_targets = {instance.get("id"), *runtime.get("tasks", {}), *instance.get("governance", {}), *instance.get("grants", {})}
    for q in details:
        index = q.get("question_index")
        if type(index) is not int or not 0 <= index < len(output.get("questions", [])) or index in indices: raise ValueError("invalid question coordinate")
        indices.add(index)
        if type(q.get("blocks")) is not bool: raise ValueError("question must state whether the decision blocks work")
        _strings(q.get("target_ids"), "question targets", nonempty=q["blocks"])
        if set(q["target_ids"]) - known_targets: raise ValueError("question affects an unknown target")
        _require_text(q.get("reason"), "decision need")
        _strings(q.get("source_unit_ids"), "question source units", nonempty=True)
        if set(q["source_unit_ids"]) - seen: raise ValueError("question source unit missing")
        actual_units = {unit["unit_id"] for unit in units if q["id"] in unit["question_refs"]}
        if set(q["source_unit_ids"]) != actual_units: raise ValueError("question coordinates contradict unit ownership")
        if not isinstance(q.get("options"), list): raise ValueError("question options and effects must be explicit")
        for option in q["options"]:
            _require_text(option.get("text"), "option"); _require_text(option.get("effect"), "option effect")
    if indices != set(range(len(output.get("questions", [])))): raise ValueError("all questions require source and impact details")
    if bool(details) != output.get("needs_clarification"): raise ValueError("clarification and question records disagree")


def _import_payload(bundle):
    return {k: v for k, v in bundle.items() if k not in {"sha256", "check", "status", "superseded_by", "application"}}


def import_input_source(instance, runtime, input_id):
    """Resolve a public input to a distinct, stable exact-source record identity."""
    request = next((row for row in runtime.get('inputs', []) if row['id'] == input_id), None)
    if request is None: raise ValueError('intent input reference does not resolve')
    text = request['text']
    lifecycle = instance.get('lifecycle', {})
    if input_id == lifecycle.get('input_id') and lifecycle.get('immutable_input'):
        from .initialization import original_input_bytes
        text = original_input_bytes(lifecycle['immutable_input']).decode('utf-8')
    identifier = 'GS-' + digest({'input_ref': input_id})
    return preserve_source(identifier, text, origin=request.get('origin', 'user'))


def prepare_import(instance, runtime, source, output, *, execution_id, previous_id=None, owner_handlers=None, input_ref=None):
    _require_text(execution_id, "author execution")
    if input_ref is not None and import_input_source(instance, runtime, input_ref) != source:
        raise ValueError('source differs from the exact public input')
    validate_import_units(instance, runtime, source, output, owner_handlers=owner_handlers)
    previous = runtime.get("intent_imports", {}).get(previous_id) if previous_id else None
    if previous_id:
        if not previous or previous.get("superseded_by") or previous.get("status") not in {"revision_required", "unresolved", "approved"}:
            raise ValueError("rework must follow a sealed failed or changed import")
        if previous["sha256"] != digest(_import_payload(previous)): raise ValueError("rework parent seal changed")
        repair = output.get("repair", {})
        if repair.get("previous_sha256") != previous["sha256"] or not repair.get("actions") or not isinstance(repair.get("changed_unit_ids"), list):
            raise ValueError("rework requires parent findings and exact changed coordinates")
        if previous["source"]["id"] != source["id"] or previous["source"]["sha256"] != source["sha256"]: raise ValueError("a new original requires a new import lineage")
        if set(repair["changed_unit_ids"]) - {u["unit_id"] for u in output["import_units"]}: raise ValueError("repair unit missing")
        def unit_basis(value, unit):
            return {"unit":unit,"questions":[q for q in value.get("question_details",[]) if q["id"] in unit["question_refs"]],
                    "question_texts":[value["questions"][q["question_index"]] for q in value.get("question_details",[]) if q["id"] in unit["question_refs"]]}
        old_units = {u["unit_id"]:unit_basis(previous["output"],u) for u in previous["output"]["import_units"]}
        changed = {u["unit_id"] for u in output["import_units"] if old_units.get(u["unit_id"]) != unit_basis(output,u)}
        if set(repair["changed_unit_ids"]) != changed: raise ValueError("repair coordinates do not match actual changed units")
        premise_changed = (previous.get("application", {}).get("post_basis_sha256", previous["basis_sha256"]) != _import_basis(instance, runtime, previous["output"])
            or previous.get("application", {}).get("post_owner_basis", previous.get("owner_basis", {})) !=
               _owner_basis(instance, runtime, previous["output"], _owner_handlers(owner_handlers)))
        if not changed and not premise_changed: raise ValueError("unchanged import resumes application; it does not need a new check")
    known = instance.get("governance_sources", {}).get(source["id"])
    if known and known != source: raise ValueError("source identity reused with different bytes")
    identifier = new_id("IM")
    bundle = {"id": identifier, "source": deepcopy(source), "output": deepcopy(output), "execution_id": execution_id,
              "coordinate_unit": "unicode_codepoint", "basis_scope": "referenced-v1",
              "basis_sha256": _import_basis(instance, runtime, output),
              "owner_basis": _owner_basis(instance, runtime, output, _owner_handlers(owner_handlers)),
              "previous_id": previous_id, "previous_findings": deepcopy(previous.get("check", {}).get("findings", [])) if previous else [],
              "status": "checking"}
    if input_ref is not None: bundle['input_ref'] = input_ref
    bundle["sha256"] = digest(_import_payload(bundle))
    if previous: previous["superseded_by"] = identifier
    runtime.setdefault("intent_imports", {})[identifier] = bundle
    return deepcopy(bundle)


def _current_import(instance, runtime, import_id, *, owner_handlers=None):
    bundle = runtime.get("intent_imports", {}).get(import_id)
    if not bundle or bundle.get("superseded_by"): raise ValueError("import is absent or superseded")
    validate_source(bundle["source"])
    if bundle.get('input_ref') is not None and import_input_source(instance, runtime, bundle['input_ref']) != bundle['source']:
        raise ValueError('original public input changed')
    if bundle["sha256"] != digest(_import_payload(bundle)): raise ValueError("sealed import changed")
    source = instance.get("governance_sources", {}).get(bundle["source"]["id"])
    if source is not None and source != bundle["source"]: raise ValueError("original version changed")
    receipt = bundle.get("application")
    if receipt and receipt.get("sha256") != digest({k: v for k, v in receipt.items() if k != "sha256"}):
        raise ValueError("sealed import application receipt changed")
    expected_basis = bundle.get("application", {}).get("post_basis_sha256", bundle["basis_sha256"])
    if expected_basis != _import_basis(instance, runtime, bundle["output"]): raise ValueError("import authority or affected targets changed")
    expected_owners = bundle.get("application", {}).get("post_owner_basis", bundle.get("owner_basis", {}))
    handlers = _owner_handlers(owner_handlers)
    if any(u["owner_kind"] not in GOVERNANCE_KINDS | {"grant", "revoke", "delegation", "question_answer", "task_scope"} | set(handlers)
           for u in bundle["output"]["import_units"]): raise ValueError("import domain owner is no longer registered")
    if expected_owners != _owner_basis(instance, runtime, bundle["output"], handlers):
        raise ValueError("import domain premises changed")
    return bundle


def check_import(instance, runtime, import_id, output, *, execution_id, owner_handlers=None):
    bundle = _current_import(instance, runtime, import_id, owner_handlers=owner_handlers)
    if bundle.get("check"): raise ValueError("check is sealed; reauthor instead")
    _require_text(execution_id, "checker execution")
    validate_independent_execution(runtime,execution_id,[bundle["execution_id"]])
    execution = runtime.get("executions", {}).get(execution_id, {})
    if execution.get("role") != "intent_interpretation" or execution.get("intent_import_sha256") != bundle["sha256"]:
        raise ValueError("checker execution must bind exact preserved import input")
    if output.get("bundle_sha256") != bundle["sha256"]: raise ValueError("check read a different import")
    if output.get("decision") not in {"approved", "revision_required", "unresolved"}: raise ValueError("invalid semantic verdict")
    if type(output.get("scope_complete")) is not bool: raise ValueError("scope completeness required")
    for field, expected in (("unit_ids", [u["unit_id"] for u in bundle["output"]["import_units"]]),
                            ("question_ids", [q["id"] for q in bundle["output"].get("question_details", [])])):
        _strings(output.get(field), field)
        if output["scope_complete"] and set(output[field]) != set(expected): raise ValueError("check must cover all meaning units and questions")
    _strings(output.get("findings"), "check findings")
    if output["decision"] == "revision_required" and not output["findings"]: raise ValueError("failed check needs repair findings")
    check = {**deepcopy(output), "execution_id": execution_id}
    check["sha256"] = digest(check)
    bundle["check"] = check
    bundle["status"] = output["decision"] if output["scope_complete"] else "unresolved"
    return deepcopy(bundle)


def validate_independent_execution(runtime, execution_id, author_ids):
    """Logical execution independence, not OS isolation or same-user authentication."""
    execution=runtime.get("executions",{}).get(execution_id,{})
    if not execution or execution_id in author_ids: raise ValueError("independent checker execution required")
    cursor=execution;seen=set()
    while cursor.get("continuation_of"):
        predecessor=cursor["continuation_of"]
        if predecessor in author_ids or predecessor in seen: raise ValueError("checker resumes an author lineage")
        seen.add(predecessor);cursor=runtime.get("executions",{}).get(predecessor,{})
        if not cursor: raise ValueError("checker continuation lineage does not resolve")
    for author_id in author_ids:
        author=runtime.get("executions",{}).get(author_id,{})
        for field in ("provider_session_id","conversation_id"):
            if execution.get(field) and execution[field] == author.get(field): raise ValueError("checker shares author conversation")


def apply_import(instance, runtime, import_id, *, approvals=None, owner_handlers=None):
    owner_handlers = _owner_handlers(owner_handlers)
    bundle = _current_import(instance, runtime, import_id, owner_handlers=owner_handlers)
    if bundle.get("application", {}).get("status") == "applied": return deepcopy(instance), deepcopy(runtime), deepcopy(bundle["application"])
    if bundle["status"] != "approved": raise ValueError("independent complete approval required")
    check = bundle["check"]
    validate_independent_execution(runtime,check["execution_id"],[bundle["execution_id"]])
    if check["sha256"] != digest({k: v for k, v in check.items() if k != "sha256"}): raise ValueError("sealed check changed")
    if runtime.get("executions", {}).get(check["execution_id"], {}).get("intent_import_sha256") != bundle["sha256"]:
        raise ValueError("checker input evidence no longer resolves")
    result, state = deepcopy(instance), deepcopy(runtime)
    validate_import_units(result, state, bundle["source"], bundle["output"], owner_handlers=owner_handlers)
    result.setdefault("governance_sources", {})[bundle["source"]["id"]] = deepcopy(bundle["source"])
    from .questions import link
    for q in bundle["output"].get("question_details", []):
        row = link(state, execution_id=bundle["execution_id"], field=f"output/questions/{q['question_index']}", owner="user",
                   targets=q["target_ids"], blocks=q["blocks"], reason=q["reason"], checked_by=check["execution_id"])
        row.update(source_kind="intent_import", source_id=import_id)
    if any(q["blocks"] for q in bundle["output"].get("question_details", [])):
        outcome = {"status": "awaiting_decision", "import_id": import_id, "applied_units": []}
    else:
        applied = []
        for unit in bundle["output"]["import_units"]:
            change = unit["payload"]
            if not change: continue
            approval = (approvals or {}).get(unit["unit_id"])
            if not approval or approval.get("actor") != "user" or approval.get("change_sha256") != digest(change): raise ValueError("semantic check is not user approval of the exact change")
            source_ref = approval.get("source_ref")
            source = result["governance_sources"].get(source_ref)
            if not source or approval.get("source_sha256") != source["sha256"]: raise ValueError("change approval original is unavailable")
            if unit["owner_kind"] in owner_handlers:
                result, state = owner_handlers[unit["owner_kind"]]["apply"](result, state, deepcopy(unit),
                    {**deepcopy(approval), "execution_id": bundle["execution_id"]})
            else:
                result, state, _ = apply_decision(result, state, change, source_ref=source_ref)
            applied.append(unit["unit_id"])
        outcome = {"status": "applied", "import_id": import_id, "applied_units": applied}
    outcome["post_basis_sha256"] = _import_basis(result, state, bundle["output"])
    outcome["post_owner_basis"] = _owner_basis(result, state, bundle["output"], owner_handlers)
    outcome["bundle_sha256"] = bundle["sha256"]
    outcome["check_sha256"] = check["sha256"]
    outcome["approvals"] = deepcopy(approvals or {})
    outcome["sha256"] = digest(outcome)
    state["intent_imports"][import_id]["application"] = deepcopy(outcome)
    return result, state, outcome


def apply_import_control(instance, runtime, request, *, owner_handlers=None):
    """Apply-only resume from the public user's exact sealed-import approval.

    ENGINE routes decision/config.kind=import_approval here, preserving request
    id/text/origin. This function never opens a new interpretation or check.
    Changed premises are rejected, so ENGINE can reauthor on the new basis.
    """
    spec = request.get("config", {})
    if request.get("action") != "decision" or request.get("origin", "user") != "user" or spec.get("kind") != "import_approval":
        raise ValueError("import approval requires an explicit user decision control")
    bundle = _current_import(instance, runtime, spec.get("import_id"), owner_handlers=owner_handlers)
    if spec.get("bundle_sha256") != bundle["sha256"] or spec.get("check_sha256") != bundle.get("check", {}).get("sha256"):
        raise ValueError("approval does not name the exact sealed interpretation and check")
    required = {u["unit_id"]: digest(u["payload"]) for u in bundle["output"]["import_units"] if u["payload"]}
    if spec.get("unit_hashes") != required: raise ValueError("approval must bind every exact proposed change")
    source = preserve_source(request["id"], request.get("text", ""), origin="user")
    _require_text(source["text"], "approval original")
    result = deepcopy(instance)
    existing = result.setdefault("governance_sources", {}).get(source["id"])
    if existing is not None and existing != source: raise ValueError("approval source identity reused")
    result["governance_sources"][source["id"]] = source
    approvals = {uid: {"actor": "user", "source_ref": source["id"], "source_sha256": source["sha256"],
                      "change_sha256": value} for uid, value in required.items()}
    result, state, receipt = apply_import(result, runtime, bundle["id"], approvals=approvals, owner_handlers=owner_handlers)
    if receipt["status"] == "applied":
        state["waiting_actions"] = {key: row for key, row in state.get("waiting_actions", {}).items()
            if not (row.get("kind") == "import_application_authority" and row.get("import_id") == bundle["id"])}
    return result, state, receipt


def interpretation_schema(stage: str) -> dict:
    string = {"type": "string"}
    fields = {"summary": string, "used_sources": {"type": "array", "items": string},
              "questions": {"type": "array", "items": string}}
    source_range = {"type": "object", "additionalProperties": False,
                    "properties": {"start": {"type": "integer", "minimum": 0}, "end": {"type": "integer", "minimum": 1}},
                    "required": ["start", "end"]}
    unit = {"type": "object", "additionalProperties": False,
            "properties": {"unit_id": string, "source_range": source_range, "interpretation": string,
                           "owner_kind": string, "owner_ref": string, "payload": {"type": "object"},
                           "decision_refs": {"type": "array", "items": string, "uniqueItems": True},
                           "question_refs": {"type": "array", "items": string, "uniqueItems": True}},
            "required": ["unit_id", "source_range", "interpretation", "owner_kind", "owner_ref", "payload", "decision_refs", "question_refs"]}
    if stage == "interpret":
        question_fields = {"id":string,"question_index":{"type":"integer","minimum":0},
                           "target_ids":{"type":"array","items":string,"uniqueItems":True}, "blocks":{"type":"boolean"}, "reason":string,
                           "source_unit_ids":{"type":"array","items":string,"minItems":1,"uniqueItems":True},
                           "options":{"type":"array","items":{"type":"object","additionalProperties":False,
                               "properties":{"text":string,"effect":string},"required":["text","effect"]}}}
        fields.update(import_units={"type": "array", "items": unit, "minItems": 1}, needs_clarification={"type": "boolean"},
                      question_details={"type":"array","items":{"type":"object","additionalProperties":False,"properties":question_fields,"required":list(question_fields)}})
    elif stage == "check":
        fields.update(decision={"type": "string", "enum": ["approved", "revision_required", "unresolved"]},
                      findings={"type": "array", "items": string}, scope_complete={"type": "boolean"}, bundle_sha256=string,
                      unit_ids={"type":"array","items":string,"uniqueItems":True},question_ids={"type":"array","items":string,"uniqueItems":True})
    else:
        raise ValueError("unknown interpretation stage")
    required = list(fields)
    if stage == "interpret":
        repair_fields = {"previous_sha256":string,"changed_unit_ids":{"type":"array","items":string,"uniqueItems":True},
                         "actions":{"type":"array","items":string,"minItems":1}}
        fields["repair"] = {"type":"object","additionalProperties":False,"properties":repair_fields,"required":list(repair_fields)}
    return {"type": "object", "additionalProperties": False, "properties": fields, "required": required}
