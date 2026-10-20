"""User authority, goal/policy revisions and bounded action authorization.

These functions interpret structured decisions already attributed to a user.
AI proposals are not decisions until their interpretation has been checked
against the preserved original request by a separate execution.
"""
from __future__ import annotations

from copy import deepcopy
from functools import partial
from datetime import datetime, timezone
import hashlib
from typing import Any

from .values import SHA256_SCHEMA, distinct_texts, is_sha256, json_copy, parse_utc, require_text
from .canonical import exact_content_hash
from .academic import requirement_record
from .execution_profiles import PLANNING_ROLES, WORK_ROLES as _SLOT_WORK_ROLES, task_research
from .external import recover_operation
from .task_contracts import TERMINAL_TASK_STATUSES

# Roles that carry out or judge task work: the slot-reserving work roles and
# the machine formal check. A governance change stops their unended executions.
TASK_WORK_ROLES = _SLOT_WORK_ROLES | {"formal_check"}
OPERATING_ROLES = {"research_preparation", "research_plan", "operational_review", "intent_interpretation", "maintenance",
                   "trust_check", "trust_activate"}

GOVERNANCE_KINDS = {"charter", "policy", "research_context", "additional_audit"}
# Decision kinds owned by this module; import owners cannot replace them.
DECISION_OWNER_KINDS = GOVERNANCE_KINDS | {"grant", "revoke", "delegation", "question_answer", "task_scope"}
# Verdicts of the independent interpretation check (schema enum and receiver check).
INTERPRETATION_DECISIONS = ("approved", "revision_required", "unresolved")
GRANT_LIST_FIELDS = ("included_targets", "excluded_targets", "subjects", "execution_kinds", "purposes")
# The states of one grant: created active, then revoked by a decision. Expiry is not a
# state: every authority check compares the clock with expires_at (grant_time_reason).
GRANT_STATUSES = frozenset({"active", "revoked"})
# The states of one governance record edition.
GOVERNANCE_STATUSES = frozenset({"active", "superseded"})


def source_record(text: str) -> dict:
    """The exact-original record ``{text, sha256, bytes}`` of ``text``'s UTF-8 bytes."""
    raw = text.encode("utf-8")
    return {"text": text, "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)}


def preserve_source(identifier: str, text: str, *, origin: str, revision: int = 1) -> dict:
    """Preserve exact input, not a normalized or interpreted substitute."""
    require_text(identifier, "source id"); require_text(text, "source text"); require_text(origin, "origin")
    if type(revision) is not int or revision < 1:
        raise ValueError("source revision must be positive")
    record = source_record(text)
    return {"id": identifier, "text": text, "origin": origin, "revision": revision,
            "sha256": record["sha256"], "bytes": record["bytes"]}


def validate_source(source: dict) -> None:
    if not isinstance(source, dict): raise ValueError("immutable source required")
    expected = preserve_source(source.get("id"), source.get("text"), origin=source.get("origin"), revision=source.get("revision"))
    if any(source.get(key) != expected[key] for key in expected):
        raise ValueError("immutable source bytes or revision changed")


def validate_governance_record(record: dict) -> None:
    if not isinstance(record, dict) or record.get("kind") not in GOVERNANCE_KINDS:
        raise ValueError("unsupported governance record kind")
    require_text(record.get("id"), "record id")
    if type(record.get("revision")) is not int or record["revision"] < 1:
        raise ValueError("governance revision must be positive")
    distinct_texts(record.get("supersedes"), "supersedes")
    if record["id"] in record["supersedes"]: raise ValueError("self supersession")
    c = record.get("content")
    if not isinstance(c, dict): raise ValueError("governance content required")
    kind = record["kind"]
    if kind == "charter":
        for key in ("rationale", "goal", "desired_result", "evidence_boundary", "decision_authority"):
            require_text(c.get(key), key)
        if c["decision_authority"] != "user": raise ValueError("charter authority cannot create a new decision owner")
        for key in ("success_criteria", "partial_success_criteria", "included_scope", "excluded_scope", "priorities", "preferences", "stop_conditions"):
            distinct_texts(c.get(key), key, nonempty=key in {"success_criteria", "included_scope"})
        requirement_record(c.get("academic_requirements"))
    elif kind == "policy":
        require_text(c.get("rule_id"), "rule id"); require_text(c.get("text"), "rule text")
        distinct_texts(c.get("scope"), "rule scope", nonempty=True)
        distinct_texts(c.get("reason_refs"), "rule reasons", nonempty=True)
        distinct_texts(c.get("audit_refs"), "rule audits")
    elif kind == "research_context":
        terms = c.get("terms")
        if not isinstance(terms, list) or not terms: raise ValueError("context terms required")
        seen = set()
        for term in terms:
            if not isinstance(term, dict): raise ValueError("context term must be an object")
            for key in ("term", "definition", "boundary"): require_text(term.get(key), key)
            if term["term"] in seen: raise ValueError("duplicate context term")
            seen.add(term["term"])
            distinct_texts(term.get("avoid_synonyms"), "avoided synonyms")
            distinct_texts(term.get("record_refs"), "definition references")
    else:
        distinct_texts(c.get("scope"), "audit scope", nonempty=True)
        distinct_texts(c.get("required_inputs"), "audit inputs", nonempty=True)
        require_text(c.get("assessor"), "audit assessor")
        mapping = c.get("verdict_mapping")
        if not isinstance(mapping, dict) or not mapping or any(not k or v not in {"satisfied", "not_satisfied", "unresolved"} for k, v in mapping.items()):
            raise ValueError("audit needs explicit universal verdict mapping")
    if "document" in record:
        document = record["document"]
        if not isinstance(document, dict): raise ValueError("document reference required")
        require_text(document.get("ref"), "document ref")
        if not is_sha256(document.get("sha256")): raise ValueError("document bytes hash required")


def _install_record(instance, record, approval_ref, source_ref):
    validate_governance_record(record)
    records = instance["governance"]
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
                           "content_sha256": exact_content_hash(record)}


def initialize_governance(instance, source, approval, records, *, approval_source=None):
    """Install an exactly approved first charter; no grant is inferred from defaults."""
    validate_source(source)
    immutable = instance.get("lifecycle", {}).get("immutable_input")
    if immutable and any(immutable.get(k) != source[k] for k in ("text", "sha256", "bytes")):
        raise ValueError("initial charter source differs from initialization immutable input")
    if instance["governance"]: raise ValueError("governance is already initialized")
    approval_source = source if approval_source is None else approval_source
    validate_source(approval_source)
    if not isinstance(approval, dict) or approval.get("actor") != "user" or approval.get("source_ref") != approval_source["id"] or approval.get("source_sha256") != approval_source["sha256"]:
        raise ValueError("initialization requires actual user approval of the immutable input")
    if approval.get("input_source_ref", approval["source_ref"]) != source["id"] or approval.get("input_source_sha256",approval["source_sha256"]) != source["sha256"]:
        raise ValueError("approval does not bind the original initialization input")
    require_text(approval.get("id"), "approval id")
    if not records or len({r["id"] for r in records}) != len(records) or approval.get("record_hashes") != {r["id"]: exact_content_hash(r) for r in records}:
        raise ValueError("approval must bind the exact proposed records")
    result = deepcopy(instance)
    if source["id"] in result["governance_sources"] and result["governance_sources"][source["id"]] != source:
        raise ValueError("source ID already bound")
    if approval["id"] in result["decisions"]: raise ValueError("initial approval ID already exists")
    result["governance_sources"][source["id"]] = deepcopy(source)
    if approval_source["id"] in result["governance_sources"] and result["governance_sources"][approval_source["id"]] != approval_source:
        raise ValueError("approval original source ID already bound")
    result["governance_sources"][approval_source["id"]] = deepcopy(approval_source)
    result["decisions"][approval["id"]] = deepcopy(approval)
    for record in records: _install_record(result, record, approval["id"], source["id"])
    if sum(r["kind"] == "charter" for r in records) != 1: raise ValueError("initialization needs exactly one approved charter")
    result["governance_approval"] = {"decision_ref": approval["id"], "source_ref": source["id"], "source_sha256": source["sha256"]}
    result["goal_status"] = "unsolved"
    validate_governance_state(result)
    return result


def mathematical_goal_basis(charter):
    """The approved mathematical premises; academic requirements bind separately."""
    return exact_content_hash({'content': {key: value for key, value in charter['content'].items()
                                          if key != 'academic_requirements'},
                               'document': charter.get('document')})


def governance_view(instance):
    """Derive the current research view from approved governance records."""
    active = [deepcopy(r) for r in instance.get("governance", {}).values() if r["status"] == "active"]
    charters = [r for r in active if r["kind"] == "charter"]
    if len(charters) != 1: raise ValueError("no unique approved charter")
    charter = charters[0]; policies = sorted((r for r in active if r["kind"] == "policy"), key=lambda r: r["id"])
    return {"charter": charter, "goal": charter["content"]["goal"], "goal_revision": charter["revision"],
            "policies": "\n\n".join(r["content"]["text"] for r in policies), "policy_revision": exact_content_hash(policies), "policy_records": policies,
            "research_context": [r for r in active if r["kind"] == "research_context"],
            "additional_audits": [r for r in active if r["kind"] == "additional_audit"],
            "academic_requirements": requirement_record(charter["content"]["academic_requirements"])}


def validate_governance_state(instance):
    """Domain validation callable before publication, independent of file layout."""
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
            approved_hash = exact_content_hash(approval["change"]["record"])
        approval_source = instance.get("governance_sources", {}).get(approval.get("source_ref"))
        validate_source(approval_source)
        if (approval.get("actor") != "user"
                or approval.get("input_source_ref",approval.get("source_ref")) != source["id"]
                or approval.get("input_source_sha256",approval.get("source_sha256")) != source["sha256"]
                or approval.get("source_sha256") != approval_source["sha256"]):
            raise ValueError("record lacks actual source-bound user approval")
        if exact_content_hash(proposal) != record.get("content_sha256") or approved_hash != exact_content_hash(proposal):
            raise ValueError("governance content differs from approved proposal")
        if record.get("status") not in GOVERNANCE_STATUSES: raise ValueError("invalid governance lifecycle")
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
    from .planning import record_index
    records = record_index(instance, runtime or {})
    if set(input_hashes) != set(content["required_inputs"]): raise ValueError("audit inputs differ from the approved required set")
    for ref in content["required_inputs"]:
        record = records.get(ref, (None, None))[1]
        if record is None or input_hashes.get(ref) != exact_content_hash(record): raise ValueError("audit required input is absent or stale")
    return {"audit_ref": audit_id, "audit_sha256": exact_content_hash(audit), "assessor": assessor, "verdict": verdict,
            "decision": content["verdict_mapping"][verdict], "input_hashes": deepcopy(input_hashes)}


def additional_audit_input(instance, runtime=None):
    """Fixed contracts and exact required records delivered to a goal auditor.

    Every active additional audit is required at the final goal gate. Its scope
    tells the assessor what to compare, not permission to silently omit it.
    """
    from .planning import record_index
    records = record_index(instance, runtime or {})
    result = []
    for audit in sorted(instance.get("governance", {}).values(), key=lambda row: row["id"]):
        if audit.get("kind") != "additional_audit" or audit.get("status") != "active": continue
        inputs = {}
        for ref in audit["content"]["required_inputs"]:
            record = records.get(ref, (None, None))[1]
            if record is None: raise ValueError("additional audit required input is unavailable: " + ref)
            inputs[ref] = deepcopy(record)
        result.append({"audit": deepcopy(audit), "audit_sha256": exact_content_hash(audit), "inputs": inputs,
                       "input_hashes": {ref: exact_content_hash(record) for ref, record in inputs.items()}})
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
                     "properties": {ref: json_copy(SHA256_SCHEMA) for ref in content["required_inputs"]},
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
        require_text(row.get("reason"), "audit reason")
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
            require_text(row.get("reason"), "audit reason")
            if actual["decision"] != "satisfied": raise ValueError("additional audit does not establish goal satisfaction")


def _apply_domain_decision(instance, runtime, change, source_ref, actor, at, *, clock):
    if actor != "user": raise ValueError("preserved user decision required")
    validate_source(instance.get("governance_sources", {}).get(source_ref))
    result, state = deepcopy(instance), deepcopy(runtime)
    decision_id = change.get("decision_id") or clock.new_id("DC")
    old = result["decisions"].get(decision_id)
    if old:
        if old.get("change") != change or old.get("source_ref") != source_ref: raise ValueError("decision ID reused")
        return result, state, old
    record = change.get("record")
    if not isinstance(record, dict): raise ValueError("governance decision requires a structured governance record")
    if record.get("kind") != change["kind"]: raise ValueError("record owner differs from decision kind")
    validate_governance_record(record)
    previous_charter = governance_view(instance)["charter"]
    academic_only = (record["kind"] == "charter"
                     and mathematical_goal_basis(previous_charter) == mathematical_goal_basis(record))
    event = {"id": decision_id, "kind": change["kind"], "actor": "user", "change": deepcopy(change), "source_ref": source_ref,
             "source_sha256": result["governance_sources"][source_ref]["sha256"], "created_at": timestamp(clock.now() if at is None else at).isoformat(), "affected": []}
    result["decisions"][decision_id] = event
    _install_record(result, record, decision_id, source_ref)
    validate_governance_state(result)
    if record["kind"] == "charter" and not academic_only: result["goal_status"] = "unsolved"
    for task in state.get("tasks", {}).values():
        if task.get("status") in TERMINAL_TASK_STATUSES: continue
        if academic_only and not task.get("academic_requirement_id"): continue
        event["affected"].append(task["id"])
        task["governance_revision_required"] = {"decision_ref": decision_id, "record_ref": record["id"]}
        if isinstance(task.get("assessment"), dict): task["assessment"]["current"] = False
    for execution in state.get("executions", {}).values():
        if (execution.get("status") != "ended" and record["kind"] in {"charter", "policy"}
                and (not academic_only or state.get("tasks", {}).get(execution.get("action", {}).get("target"), {}).get("academic_requirement_id"))
                and execution.get("role") in TASK_WORK_ROLES | PLANNING_ROLES
                and not execution.get("action", {}).get("review_cycle_id")):
            execution["stop_requested"] = "governance_changed"
            event["affected"].append(execution["id"])
    _queue(state, "research_plan" if academic_only else "research_preparation", "approved governance changed",
           decision_id=decision_id, affected_ids=event["affected"], clock=clock)
    if change.get("resolves_questions"):
        from .questions import resolve_user
        resolve_user(state, change["resolves_questions"], resolution_ref=decision_id, affected_ids=[result["id"], record["id"], *event["affected"]])
    state.setdefault("history", []).append({"kind": "governance_decision", "decision_id": decision_id})
    return result, state, event


def timestamp(value: str) -> datetime:
    """A stored zoned time as UTC."""
    return parse_utc(value)


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


def grant_scope_reason(grant, action, runtime, *, at):
    """Check explicit authority; execution/operation ledgers own consumption."""
    return _grant_scope_reason(grant, action, runtime, now=timestamp(at))


def grant_time_reason(grant, now):
    """The one effective-interval rule of a grant: [valid_from, expires_at)."""
    if grant.get("expires_at") and timestamp(grant["expires_at"]) <= now: return "grant expired"
    if grant.get("valid_from") and timestamp(grant["valid_from"]) > now: return "grant is not effective yet"
    return None


def normalized_grant(spec, *, gid, created_at, source_ref, decision_id):
    """Stored form of one approved grant; the producer and the source check both build it here."""
    grant = deepcopy(spec)
    grant.update(id=gid, status="active", expires_at=spec.get("expires_at"), created_at=created_at,
                 source_ref=source_ref, decision_id=decision_id)
    grant.setdefault("reuse", "once")
    for field in GRANT_LIST_FIELDS:
        grant.setdefault(field, [])
    return grant


def _grant_scope_reason(grant, action, runtime, *, now):
    if grant.get("status") != "active": return "grant is not active"
    time_reason = grant_time_reason(grant, now)
    if time_reason: return time_reason
    target = action.get("target")
    if target in grant.get("excluded_targets", []): return "target excluded"
    for field in ("included_targets", "task_ids"):
        if grant.get(field) and target not in grant[field]: return "target outside grant"
    if grant.get("subjects") and action.get("subject", action.get("role")) not in grant["subjects"]: return "subject outside grant"
    if grant.get("execution_kinds") and action.get("actor_kind") not in grant["execution_kinds"]: return "execution kind outside grant"
    if grant.get("purposes") and action.get("purpose") not in grant["purposes"]: return "purpose outside grant"
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


def authorize(instance: dict, action: dict, at: str | None, *, runtime: dict | None = None) -> dict:
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
        reason = _grant_scope_reason(grant, action, runtime, now=now)
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
            "grant_sha256": exact_content_hash(grant),
            "expires_at": grant.get("expires_at")}


def validate_grant_source(instance, grant):
    """Resolve the exact preserved approval, not an origin label or caller claim."""
    source = instance.get("governance_sources", {}).get(grant.get("source_ref"))
    validate_source(source)
    decision = instance.get("decisions", {}).get(grant.get("decision_id"), {})
    if (decision.get("actor") != "user" or decision.get("kind") != "grant"
            or decision.get("source_ref") != source["id"]
            or decision["source_sha256"] != source["sha256"]):
        raise ValueError("grant lacks current source-bound user approval")
    approved = normalized_grant(decision.get("change", {}).get("grant", {}), gid=grant["id"],
                                created_at=decision["created_at"], source_ref=source["id"], decision_id=decision["id"])
    if approved != grant: raise ValueError("grant differs from the actual approved scope")


def authorize_review_replacement(instance, runtime, action, *, delegation_id=None, case=None, at):
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


def _queue(runtime: dict, role: str, reason: str, clock, **fields: Any) -> None:
    action = {"id": clock.new_id("AC"), "role": role, "reason": reason, **fields}
    action.setdefault("lineage_id", action["id"])
    runtime.setdefault("queue", []).append(action)


def _dispose_grant_consumers(runtime, gid, event, reason):
    for eid, execution in runtime.get("executions", {}).items():
        if execution.get("grant_id") == gid and execution.get("status") != "ended":
            execution["stop_requested"] = reason
            event["affected"].append(eid)
    # Pinned requests cannot fall through to another overlapping authority.
    removed = [a for a in runtime.get("queue", []) if a.get("grant_id") == gid]
    runtime["queue"] = [a for a in runtime.get("queue", []) if a.get("grant_id") != gid]
    live_targets = {row.get("action", {}).get("target") for row in runtime.get("executions", {}).values()
                    if row.get("status") != "ended"}
    for action in removed:
        # Removing a request withdraws that attempt, not the task obligation: a selected
        # task without live work returns to planning, as a cancelled selection does.
        task = runtime.get("tasks", {}).get(action.get("target"))
        if (task is not None and task_research(action) and task.get("status") == "active"
                and task["id"] not in live_targets):
            task.update(status="planned", deferred_reason=reason)
            event["affected"].append(task["id"])
    for operation in runtime.get("external_operations", {}).values():
        if operation.get("grant_id") == gid and operation.get("status") == "prepared":
            if not operation.get("transmitted") and operation.get("transmission_phase") != "recorded":
                operation.update(status="cancelled", transmitted=False, cancellation={"authority_event_ref":event["id"],"reason":reason})
            else:
                operation.update(recover_operation(operation))
            event["affected"].append(operation["id"])


def apply_decision(instance: dict, runtime: dict, change: dict, *, source_ref: str,
                   actor: str = "user", at: str | None = None, clock) -> tuple[dict, dict, dict]:
    """Apply one explicit decision atomically to copies of the two roots."""
    from .control_contracts import validate_decision_shape
    validate_decision_shape(change)
    if actor != "user" or not source_ref:
        raise ValueError("a preserved user decision is required")
    if change.get("kind") in GOVERNANCE_KINDS:
        return _apply_domain_decision(instance, runtime, change, source_ref, actor, at, clock=clock)
    instance, runtime = deepcopy(instance), deepcopy(runtime)
    validate_source(instance.get("governance_sources", {}).get(source_ref, {}))
    when = timestamp(clock.now() if at is None else at).isoformat()
    kind = change.get("kind")
    decision_id = change.get("decision_id") or clock.new_id("DC")
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
            if not isinstance(roles, list) or not roles or set(roles) - TASK_WORK_ROLES - OPERATING_ROLES:
                raise ValueError("local grant requires supported roles")
        else:
            if not spec.get("allowed_origins") or not spec.get("allowed_methods"):
                raise ValueError("HTTP grant must specify origins and methods")
        gid = spec.get("id") or clock.new_id("GR")
        if gid in instance["grants"]:
            raise ValueError("grant ID already exists; revoke it before replacing authority")
        spec = normalized_grant(spec, gid=gid, created_at=when, source_ref=source_ref, decision_id=decision_id)
        if spec["reuse"] not in {"once", "reusable"}: raise ValueError("grant reuse must be explicit once or reusable")
        for field in GRANT_LIST_FIELDS:
            distinct_texts(spec[field], field)
        if spec.get("valid_from"): timestamp(spec["valid_from"])
        if spec.get("valid_from") and expires and timestamp(spec["valid_from"]) >= timestamp(expires):
            raise ValueError("grant has an empty effective interval")
        instance["grants"][gid] = spec
        replaces = change.get("replaces", [])
        distinct_texts(replaces, "replaced grants")
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
            _queue(runtime, "research_plan", "new execution authority", decision_id=decision_id, clock=clock)
    elif kind == "revoke":
        gid = change.get("grant_id")
        if gid not in instance["grants"]:
            raise ValueError("grant not found")
        instance["grants"][gid].update(status="revoked", revoked_at=when, revoked_by=decision_id)
        event["grant_id"] = gid
        _dispose_grant_consumers(runtime,gid,event,"grant_revoked")
    elif kind == "review_replacement":
        from .review_cycle import authorize_record_replacement
        action = change.get("allowed_action", {})
        cycle = runtime.get("review_cycles", {}).get(action.get("review_cycle_id"))
        if (action.get("role") != "identity_review" or cycle is None
                or cycle.get("knowledge_id") != action.get("target")):
            raise ValueError("review replacement decision requires the exact current review action")
        from .review_cycle import slot_key
        if slot_key(action) in cycle.get("results", {}):
            raise ValueError("review replacement decision requires an unsealed review slot")
        outcome = authorize_record_replacement(cycle, action, instance, runtime=runtime,
            grant_id=change.get("grant_id"), at=when, clock=clock)
        if outcome["disposition"] != "replacement_ready":
            raise ValueError("review replacement decision is not authorized: " +
                             str(outcome.get("reason", outcome["disposition"])))
        event["effect"] = {"review_cycle_id": action["review_cycle_id"], **{
            key: outcome["action"][key] for key in (
                "stage", "slot", "round", "replacement_for", "continuity_break_cause")}}
        event["grant_id"] = outcome["authority"]["grant_id"]
        event["affected"].append(action["target"])
    elif kind == "delegation":
        from .delegations import validate_delegation
        delegation = deepcopy(change.get("delegation"))
        if not isinstance(delegation, dict):
            raise ValueError("delegation decision requires a delegation record")
        delegation.update(source_ref=source_ref, decision_id=decision_id, created_at=when)
        delegation = validate_delegation(delegation, now_iso=when)
        original = instance["decisions"].get(delegation["original_decision_id"], {})
        if original.get("actor") != "user" or original.get("kind") != delegation["decision_kind"]:
            raise ValueError("delegation must bind an actual current user decision of the same kind")
        original_source = instance["governance_sources"].get(original.get("source_ref"))
        validate_source(original_source)
        if original.get("source_sha256") != original_source["sha256"]:
            raise ValueError("original decision source differs from its preserved approval")
        event["original_decision_sha256"] = exact_content_hash(original)
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
        continue_repetition(instance, runtime, change, event, clock=clock)
    elif kind == "question_answer":
        require_text(change.get("text"), "answer text")
        identifiers = change.get("resolves_questions", [])
        if not identifiers:
            raise ValueError("a question answer must identify its questions")
        by_id = {row["id"]: row for row in runtime.get("question_links", [])}
        targets = change.get("target_ids")
        distinct_texts(targets, "answer affected targets", nonempty=True)
        from .questions import open_targets
        for identifier in identifiers:
            if identifier not in by_id:
                raise ValueError("unknown question: " + str(identifier))
            if set(targets) - set(open_targets(by_id[identifier])):
                raise ValueError("answer names unrelated or already resolved targets")
        event["affected"].extend(targets)
    elif kind == "task_scope":
        from .planning import contract_hash
        from .task_contracts import validate_task_contract
        tid = change.get("task_id")
        task = runtime["tasks"].get(tid)
        if task is None or task["status"] in TERMINAL_TASK_STATUSES:
            raise ValueError("task scope decision requires an unfinished task")
        validate_task_contract(task)
        if change.get("revision") != task["revision"] or change.get("contract_sha256") != contract_hash(task):
            raise ValueError("scope approval must bind the exact task contract edition")
        disposition = change.get("disposition")
        if disposition not in {"revise", "waive", "transfer"}:
            raise ValueError("scope approval requires revise, waive or transfer of named obligations")
        reason = require_text(change.get("reason"), "scope reason")
        if disposition in {"waive", "transfer"}:
            ids = distinct_texts(change.get("obligation_ids"), "approved obligations", nonempty=True)
            if set(ids) - {row["id"] for row in task["completion_obligations"]}:
                raise ValueError("scope approval names an unknown obligation")
            if disposition == "transfer":
                recipient = runtime["tasks"].get(change.get("target_task_id"))
                if not recipient or recipient["id"] == tid or recipient["status"] in TERMINAL_TASK_STATUSES:
                    raise ValueError("scope transfer requires a distinct unfinished recipient")
                validate_task_contract(recipient)
            # This is authority, not a second application of TASKS' lifecycle.
            _queue(runtime, "research_plan", reason, scope_decision_id=decision_id, clock=clock)
        else:
            task["revision_requested"] = {"source": decision_id, "revision": task["revision"], "reason": reason}
            from .revisions import capture_targets
            _queue(runtime, "research_preparation", reason, target=tid,
                   revision_targets=capture_targets(instance, runtime, [tid], required=True, source_ref=decision_id), clock=clock)
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
    from .planning import record_index
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
    records = {key: row for key, (_, row) in
               record_index(instance, runtime, source_aliases=True, question_links=True).items()}
    if instance.get('id'):
        # An owner coordinate naming the instance is not a dependency on
        # every nested record. Domain handlers capture their own settings.
        records[instance['id']] = {'id': instance['id']}
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
    return exact_content_hash({'governance': governance,
        'references': {ref: deepcopy(records.get(ref)) for ref in sorted(references)}})


def register_import_owner(handlers, kind, *, apply, validate, basis, contract=None):
    """Register trusted domain code, not model-submitted functions or authority.

    validate(i,r,unit) checks the owner's actual candidate contract;
    basis(i,r,unit) returns only premises whose changes invalidate interpretation;
    apply(i,r,unit,approval) returns the two roots using that same owner contract.
    ENGINE supplies configuration's existing configure consumer through this API.
    """
    require_text(kind, "import owner kind")
    if kind in DECISION_OWNER_KINDS:
        raise ValueError("cannot replace a governance authority owner")
    if kind in handlers: raise ValueError("import owner already registered")
    if not all(callable(fn) for fn in (apply, validate, basis)): raise ValueError("owner needs apply, validate and currentness functions")
    owner = {"apply": apply, "validate": validate, "basis": basis}
    if contract is not None:
        if not isinstance(contract, dict) or not contract:
            raise ValueError('import owner contract must be a nonempty object')
        owner['contract'] = deepcopy(contract)
    handlers[kind] = owner
    return handlers


def import_consumer_catalog(handlers=None, *, clock):
    """Publish the actual registered kinds and their producer-facing contracts."""
    owners = _owner_handlers(handlers, clock=clock)
    builtins = DECISION_OWNER_KINDS | {'configuration', 'research_record', 'evidence'}
    kinds = DECISION_OWNER_KINDS | set(owners)
    rows = []
    for kind in sorted(kinds):
        contract = owners.get(kind, {}).get('contract')
        if kind in builtins:
            contract = {'document': 'references/입력-소비자.md', 'section': kind}
        if not contract:
            raise ValueError('registered import owner has no producer contract: ' + kind)
        rows.append({'owner_kind': kind, 'payload_contract': deepcopy(contract)})
    return rows


def _knowledge_import(instance, runtime, unit, approval, *, clock):
    from .knowledge_io import import_candidate
    result, state, _ = import_candidate(instance, runtime, unit["payload"]["record"],
        source_ref=approval["source_ref"], actor_ref=approval.get("execution_id", approval["source_ref"]), clock=clock)
    return result, state


def _validate_knowledge_import(instance, runtime, unit, *, clock):
    from .knowledge_io import import_candidate
    if not unit["payload"]: return
    candidate = unit["payload"].get("record")
    if not isinstance(candidate, dict) or candidate.get("id") != unit["owner_ref"]:
        raise ValueError("knowledge import must name its exact candidate ID")
    # Pure owner API on copies; no publication, execution or verification occurs.
    import_candidate(instance, runtime, candidate, source_ref="import-validation", actor_ref="import-validation", clock=clock)


def _knowledge_import_basis(instance, runtime, unit):
    from .planning import record_index
    from .knowledge_io import lookup_definition, ensure_ontology
    from .input_basis import capture_sources
    candidate = unit["payload"].get("record", {})
    records = record_index(instance, runtime)
    refs = {unit["owner_ref"], *candidate.get("dependencies", [])}
    if candidate.get("formal_result_ref"): refs.add(candidate["formal_result_ref"])
    return {"records": {ref: deepcopy(records.get(ref, (None, None))[1]) for ref in sorted(refs)},
            "kind_definition": deepcopy(lookup_definition(ensure_ontology(instance), "knowledge", candidate.get("kind", ""))),
            "source_basis": capture_sources(instance, candidate.get("source_refs", []))}


def import_owner_handlers(*, clock):
    """Built-in research candidates/evidence; extension tokens are not a closed list.

    These owners use the ordinary knowledge candidate contract. Evidence here
    means a research candidate (e.g. an observation), never automatic proof or
    arbitrary bytes promoted to verified evidence. Raw artifacts keep their
    existing artifact/source owner and can register that owner's adapter.
    """
    handlers = {}
    for kind in ("research_record", "evidence"):
        register_import_owner(handlers, kind, apply=partial(_knowledge_import, clock=clock),
                              validate=partial(_validate_knowledge_import, clock=clock), basis=_knowledge_import_basis)
    return handlers


def register_configuration_owner(handlers, *, apply, host_id):
    """Reuse ENGINE's actual config validation and its live-ledger apply callback.

    The callback must consume the approved patch through the same configure
    transition as public controls (profiles, stopped-mode check, reservations,
    pending selections). It must not dispatch external effects during staging.
    """
    def validate(instance, runtime, unit):
        from .configuration import validate_config
        patch = unit["payload"].get("config")
        if unit["owner_ref"] != instance["id"] or not isinstance(patch, dict):
            raise ValueError("configuration import must bind this instance and an explicit config patch")
        validate_config({**instance.get("config", {}), **patch}, host_id=host_id)
    def basis(instance, runtime, unit):
        return deepcopy(instance.get("config", {}))
    return register_import_owner(handlers, "configuration", apply=apply, validate=validate, basis=basis)


def _unbound(adapter):
    """An owner adapter with its clock binding removed, to recognize the built-in owners."""
    return {key: getattr(value, "func", value) for key, value in adapter.items()} if isinstance(adapter, dict) else adapter


def _owner_handlers(handlers, *, clock):
    result = import_owner_handlers(clock=clock)
    for kind, adapter in (handlers or {}).items():
        if kind in result and _unbound(adapter) == _unbound(result[kind]):
            result[kind] = adapter  # the same owner, bound to the caller's clock
            continue
        if not isinstance(adapter, dict): raise ValueError("owner registration needs apply/validate/basis")
        register_import_owner(result, kind, **adapter)
    return result


def _owner_basis(instance, runtime, output, handlers):
    return {unit["unit_id"]: deepcopy(handlers[unit["owner_kind"]]["basis"](instance, runtime, unit))
            for unit in output["import_units"] if unit["owner_kind"] in handlers}


def validate_import_units(instance, runtime, source, output, *, owner_handlers=None, owner_kinds=None, clock):
    """Check exact character coverage and ownership; semantic preservation is checked separately.

    The interpreting producer runs this same check on its fixed input
    (submission._intent_import_issues). It passes the published owner_kinds of
    import_consumers instead of handlers, so owner checks of live state stay here.
    """
    validate_source(source)
    units = output.get("import_units")
    if not isinstance(units, list) or not units: raise ValueError("import units required")
    owner_handlers = {} if owner_kinds is not None else _owner_handlers(owner_handlers, clock=clock)
    known_owners = DECISION_OWNER_KINDS | set(owner_handlers if owner_kinds is None else owner_kinds)
    decisions = instance.get("decisions", {})
    details = output.get("question_details", [])
    if not isinstance(details, list): raise ValueError("question details required")
    qids = [q.get("id") for q in details]
    if any(not isinstance(q, str) or not q for q in qids) or len(set(qids)) != len(qids): raise ValueError("duplicate question identity")
    cursor = 0; seen = set(); referenced_questions = set()
    for unit in units:
        if not isinstance(unit, dict): raise ValueError("import unit must be an object")
        identifier = require_text(unit.get("unit_id"), "unit id")
        if identifier in seen: raise ValueError("duplicate meaning unit")
        seen.add(identifier)
        span = unit.get("source_range", {})
        start, end = span.get("start"), span.get("end")
        if type(start) is not int or type(end) is not int or start != cursor or end <= start or end > len(source["text"]):
            raise ValueError("source coverage gap, overlap, or invalid coordinate")
        cursor = end
        require_text(unit.get("interpretation"), "interpretation")
        require_text(unit.get("owner_ref"), "owner ref")
        if unit.get("owner_kind") not in known_owners: raise ValueError("owner has no registered domain handler")
        if not isinstance(unit.get("payload"), dict): raise ValueError("unit payload must be an object")
        distinct_texts(unit.get("decision_refs"), "decision references")
        distinct_texts(unit.get("question_refs"), "question references")
        if set(unit["decision_refs"]) - set(decisions): raise ValueError("existing decision does not resolve")
        if set(unit["question_refs"]) - set(qids): raise ValueError("unit question does not resolve")
        referenced_questions.update(unit["question_refs"])
        payload = unit["payload"]
        if payload:
            from .control_contracts import validate_decision_shape
            validate_decision_shape(payload)
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
        distinct_texts(q.get("target_ids"), "question targets", nonempty=q["blocks"])
        if set(q["target_ids"]) - known_targets: raise ValueError("question affects an unknown target")
        require_text(q.get("reason"), "decision need")
        distinct_texts(q.get("source_unit_ids"), "question source units", nonempty=True)
        if set(q["source_unit_ids"]) - seen: raise ValueError("question source unit missing")
        actual_units = {unit["unit_id"] for unit in units if q["id"] in unit["question_refs"]}
        if set(q["source_unit_ids"]) != actual_units: raise ValueError("question coordinates contradict unit ownership")
        if not isinstance(q.get("options"), list): raise ValueError("question options and effects must be explicit")
        for option in q["options"]:
            require_text(option.get("text"), "option"); require_text(option.get("effect"), "option effect")
    if indices != set(range(len(output.get("questions", [])))): raise ValueError("all questions require source and impact details")


def import_seal(bundle):
    """The seal digest of an intent import: every field but the seal, its check, status, supersession and application."""
    return exact_content_hash({k: v for k, v in bundle.items() if k not in {"sha256", "check", "status", "superseded_by", "application"}})


def import_input_source(instance, runtime, input_id):
    """Resolve a public input to a distinct, stable exact-source record identity."""
    request = next((row for row in runtime.get('inputs', []) if row['id'] == input_id), None)
    if request is None: raise ValueError('intent input reference does not resolve')
    text = request['text']
    lifecycle = instance.get('lifecycle', {})
    if input_id == lifecycle.get('input_id') and lifecycle.get('immutable_input'):
        from .initialization import original_input_bytes
        text = original_input_bytes(lifecycle['immutable_input']).decode('utf-8')
    identifier = 'GS-' + exact_content_hash({'input_ref': input_id})
    return preserve_source(identifier, text, origin=request.get('origin', 'user'))


def prepare_import(instance, runtime, source, output, *, execution_id, input_ref, previous_id=None, owner_handlers=None, clock):
    """Seal an interpretation of the public input ``input_ref``, whose exact source is ``source``."""
    require_text(execution_id, "author execution")
    if import_input_source(instance, runtime, input_ref) != source:
        raise ValueError('source differs from the exact public input')
    validate_import_units(instance, runtime, source, output, owner_handlers=owner_handlers, clock=clock)
    previous = runtime.get("intent_imports", {}).get(previous_id) if previous_id else None
    if previous_id:
        if not previous or previous.get("superseded_by") or previous.get("status") not in INTERPRETATION_DECISIONS:
            raise ValueError("rework must follow a sealed failed or changed import")
        if previous["sha256"] != import_seal(previous): raise ValueError("rework parent seal changed")
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
               _owner_basis(instance, runtime, previous["output"], _owner_handlers(owner_handlers, clock=clock)))
        if not changed and not premise_changed: raise ValueError("unchanged import resumes application; it does not need a new check")
    known = instance.get("governance_sources", {}).get(source["id"])
    if known and known != source: raise ValueError("source identity reused with different bytes")
    identifier = clock.new_id("IM")
    bundle = {"id": identifier, "source": deepcopy(source), "output": deepcopy(output), "execution_id": execution_id,
              "basis_sha256": _import_basis(instance, runtime, output),
              "owner_basis": _owner_basis(instance, runtime, output, _owner_handlers(owner_handlers, clock=clock)),
              "previous_id": previous_id, "previous_findings": deepcopy(previous.get("check", {}).get("findings", [])) if previous else [],
              "status": "checking"}
    bundle['input_ref'] = input_ref
    bundle["sha256"] = import_seal(bundle)
    if previous: previous["superseded_by"] = identifier
    runtime.setdefault("intent_imports", {})[identifier] = bundle
    return deepcopy(bundle)


def current_import(instance, runtime, import_id, *, owner_handlers=None, clock):
    bundle = runtime.get("intent_imports", {}).get(import_id)
    if not bundle or bundle.get("superseded_by"): raise ValueError("import is absent or superseded")
    validate_source(bundle["source"])
    if import_input_source(instance, runtime, bundle['input_ref']) != bundle['source']:
        raise ValueError('original public input changed')
    if bundle["sha256"] != import_seal(bundle): raise ValueError("sealed import changed")
    source = instance.get("governance_sources", {}).get(bundle["source"]["id"])
    if source is not None and source != bundle["source"]: raise ValueError("original version changed")
    receipt = bundle.get("application")
    if receipt and receipt.get("sha256") != exact_content_hash({k: v for k, v in receipt.items() if k != "sha256"}):
        raise ValueError("sealed import application receipt changed")
    expected_basis = bundle.get("application", {}).get("post_basis_sha256", bundle["basis_sha256"])
    if expected_basis != _import_basis(instance, runtime, bundle["output"]): raise ValueError("import authority or affected targets changed")
    expected_owners = bundle.get("application", {}).get("post_owner_basis", bundle.get("owner_basis", {}))
    handlers = _owner_handlers(owner_handlers, clock=clock)
    if any(u["owner_kind"] not in DECISION_OWNER_KINDS | set(handlers)
           for u in bundle["output"]["import_units"]): raise ValueError("import domain owner is no longer registered")
    if expected_owners != _owner_basis(instance, runtime, bundle["output"], handlers):
        raise ValueError("import domain premises changed")
    return bundle


def check_import(instance, runtime, import_id, output, *, execution_id, owner_handlers=None, clock):
    bundle = current_import(instance, runtime, import_id, owner_handlers=owner_handlers, clock=clock)
    if bundle.get("check"): raise ValueError("check is sealed; reauthor instead")
    require_text(execution_id, "checker execution")
    validate_independent_execution(runtime,execution_id,[bundle["execution_id"]])
    execution = runtime.get("executions", {}).get(execution_id, {})
    if execution.get("role") != "intent_interpretation" or execution.get("intent_import_sha256") != bundle["sha256"]:
        raise ValueError("checker execution must bind exact preserved import input")
    if output.get("bundle_sha256") != bundle["sha256"]: raise ValueError("check read a different import")
    if output.get("decision") not in INTERPRETATION_DECISIONS: raise ValueError("invalid semantic verdict")
    if type(output.get("scope_complete")) is not bool: raise ValueError("scope completeness required")
    for field, expected in (("unit_ids", [u["unit_id"] for u in bundle["output"]["import_units"]]),
                            ("question_ids", [q["id"] for q in bundle["output"].get("question_details", [])])):
        distinct_texts(output.get(field), field)
        if output["scope_complete"] and set(output[field]) != set(expected): raise ValueError("check must cover all meaning units and questions")
    distinct_texts(output.get("findings"), "check findings")
    if output["decision"] == "revision_required" and not output["findings"]: raise ValueError("failed check needs repair findings")
    check = {**deepcopy(output), "execution_id": execution_id}
    check["sha256"] = exact_content_hash(check)
    bundle["check"] = check
    bundle["status"] = output["decision"] if output["scope_complete"] else "unresolved"
    return deepcopy(bundle)


def execution_lineage(runtime, execution_id, fields=("continuation_of", "context_origin"), *, revisit_error=None):
    """Yield (ID, execution) for execution_id and each execution its ``fields`` reach, depth first.

    Each ID is yielded once. The execution is None for an ID with no record, and its
    links are not followed; the caller decides whether that rejects or ends its
    judgment. With ``revisit_error``, reaching an ID again raises ValueError with it.
    """
    executions = runtime.get("executions", {})
    pending, seen = [execution_id], set()
    while pending:
        identifier = pending.pop()
        if identifier in seen:
            if revisit_error:
                raise ValueError(revisit_error)
            continue
        seen.add(identifier)
        row = executions.get(identifier)
        yield identifier, row
        for field in fields if row is not None else ():
            values = row.get(field) or []
            pending.extend([values] if isinstance(values, str) else values)


def validate_independent_execution(runtime, execution_id, author_ids):
    """Logical execution independence, not OS isolation or same-user authentication.

    Each provider invocation starts a fresh CLI conversation (worker_request's
    ephemeral Codex exec / nonpersistent Claude print). A continuation is an
    explicit logical reuse; context_origin names supplied records, not a resumed
    provider session. Native thread IDs remain in the captured provider stream,
    rather than unproduced execution-level session aliases.
    """
    execution=runtime.get("executions",{}).get(execution_id,{})
    if not execution or execution_id in author_ids: raise ValueError("independent checker execution required")
    for predecessor, row in execution_lineage(runtime, execution_id, ("continuation_of",),
                                              revisit_error="checker resumes an author lineage"):
        if predecessor == execution_id: continue
        if predecessor in author_ids: raise ValueError("checker resumes an author lineage")
        if not row: raise ValueError("checker continuation lineage does not resolve")


def import_approval_draft(instance, runtime, import_id, *, owner_handlers=None, clock):
    """Derive exact approval coordinates without approving or applying a change."""
    bundle = current_import(instance, runtime, import_id, owner_handlers=owner_handlers, clock=clock)
    check = bundle.get('check', {})
    if (bundle.get('status') != 'approved' or check.get('decision') != 'approved'
            or check.get('scope_complete') is not True
            or check.get('bundle_sha256') != bundle['sha256']
            or check.get('sha256') != exact_content_hash({k:v for k,v in check.items() if k != 'sha256'})):
        raise ValueError('approval draft requires a complete independently checked import')
    validate_independent_execution(runtime, check['execution_id'], [bundle['execution_id']])
    return {'kind':'import_approval', 'import_id':bundle['id'], 'bundle_sha256':bundle['sha256'],
            'check_sha256':check['sha256'],
            'unit_hashes':{u['unit_id']:exact_content_hash(u['payload']) for u in bundle['output']['import_units'] if u['payload']}}


def apply_import(instance, runtime, import_id, *, approvals=None, owner_handlers=None, clock):
    from .control_contracts import validate_import_approvals
    approvals = {} if approvals is None else approvals
    validate_import_approvals(approvals)
    owner_handlers = _owner_handlers(owner_handlers, clock=clock)
    bundle = current_import(instance, runtime, import_id, owner_handlers=owner_handlers, clock=clock)
    if bundle.get("application", {}).get("status") == "applied": return deepcopy(instance), deepcopy(runtime), deepcopy(bundle["application"])
    if bundle["status"] != "approved": raise ValueError("independent complete approval required")
    check = bundle["check"]
    validate_independent_execution(runtime,check["execution_id"],[bundle["execution_id"]])
    if check["sha256"] != exact_content_hash({k: v for k, v in check.items() if k != "sha256"}): raise ValueError("sealed check changed")
    if runtime.get("executions", {}).get(check["execution_id"], {}).get("intent_import_sha256") != bundle["sha256"]:
        raise ValueError("checker input evidence no longer resolves")
    result, state = deepcopy(instance), deepcopy(runtime)
    validate_import_units(result, state, bundle["source"], bundle["output"], owner_handlers=owner_handlers, clock=clock)
    result["governance_sources"][bundle["source"]["id"]] = deepcopy(bundle["source"])
    from .questions import link
    for q in bundle["output"].get("question_details", []):
        row = link(state, execution_id=bundle["execution_id"], field=f"output/questions/{q['question_index']}", owner="user",
                   targets=q["target_ids"], blocks=q["blocks"], reason=q["reason"], checked_by=check["execution_id"], clock=clock)
        row.update(source_kind="intent_import", source_id=import_id)
    if any(q["blocks"] for q in bundle["output"].get("question_details", [])):
        outcome = {"status": "awaiting_decision", "import_id": import_id, "applied_units": []}
    else:
        applied = []
        for unit in bundle["output"]["import_units"]:
            change = unit["payload"]
            if not change: continue
            approval = approvals.get(unit["unit_id"])
            if not approval or approval.get("actor") != "user" or approval.get("change_sha256") != exact_content_hash(change): raise ValueError("semantic check is not user approval of the exact change")
            source_ref = approval.get("source_ref")
            source = result["governance_sources"].get(source_ref)
            if not source or approval.get("source_sha256") != source["sha256"]: raise ValueError("change approval original is unavailable")
            if unit["owner_kind"] in owner_handlers:
                result, state = owner_handlers[unit["owner_kind"]]["apply"](result, state, deepcopy(unit),
                    {**deepcopy(approval), "execution_id": bundle["execution_id"]})
            else:
                result, state, _ = apply_decision(result, state, change, source_ref=source_ref, clock=clock)
            applied.append(unit["unit_id"])
        outcome = {"status": "applied", "import_id": import_id, "applied_units": applied}
    outcome["post_basis_sha256"] = _import_basis(result, state, bundle["output"])
    outcome["post_owner_basis"] = _owner_basis(result, state, bundle["output"], owner_handlers)
    outcome["bundle_sha256"] = bundle["sha256"]
    outcome["check_sha256"] = check["sha256"]
    outcome["approvals"] = deepcopy(approvals)
    outcome["sha256"] = exact_content_hash(outcome)
    state["intent_imports"][import_id]["application"] = deepcopy(outcome)
    return result, state, outcome


def apply_import_control(instance, runtime, request, *, owner_handlers=None, clock):
    """Apply-only resume from the public user's exact sealed-import approval.

    ENGINE routes decision/config.kind=import_approval here, preserving request
    id/text/origin. This function never opens a new interpretation or check.
    Changed premises are rejected, so ENGINE can reauthor on the new basis.
    """
    spec = request.get("config", {})
    if request.get("action") != "decision" or request.get("origin", "user") != "user" or spec.get("kind") != "import_approval":
        raise ValueError("import approval requires an explicit user decision control")
    # apply_import checks that the bundle is current; here only its sealed coordinates are compared.
    bundle = runtime.get("intent_imports", {}).get(spec.get("import_id"))
    if not bundle: raise ValueError("import is absent")
    if spec.get("bundle_sha256") != bundle["sha256"] or spec.get("check_sha256") != bundle.get("check", {}).get("sha256"):
        raise ValueError("approval does not name the exact sealed interpretation and check")
    required = {u["unit_id"]: exact_content_hash(u["payload"]) for u in bundle["output"]["import_units"] if u["payload"]}
    if spec.get("unit_hashes") != required: raise ValueError("approval must bind every exact proposed change")
    source = preserve_source(request["id"], request.get("text", ""), origin="user")
    require_text(source["text"], "approval original")
    result = deepcopy(instance)
    existing = result["governance_sources"].get(source["id"])
    if existing is not None and existing != source: raise ValueError("approval source identity reused")
    result["governance_sources"][source["id"]] = source
    approvals = {uid: {"actor": "user", "source_ref": source["id"], "source_sha256": source["sha256"],
                      "change_sha256": value} for uid, value in required.items()}
    result, state, receipt = apply_import(result, runtime, bundle["id"], approvals=approvals, owner_handlers=owner_handlers, clock=clock)
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
        fields.update(import_units={"type": "array", "items": unit, "minItems": 1},
                      question_details={"type":"array","items":{"type":"object","additionalProperties":False,"properties":question_fields,"required":list(question_fields)}})
    elif stage == "check":
        fields.update(decision={"type": "string", "enum": list(INTERPRETATION_DECISIONS)},
                      findings={"type": "array", "items": string}, scope_complete={"type": "boolean"}, bundle_sha256=string,
                      unit_ids={"type":"array","items":string,"uniqueItems":True},question_ids={"type":"array","items":string,"uniqueItems":True})
    else:
        raise ValueError("unknown interpretation stage")
    required = list(fields)
    if stage == "interpret":
        repair_fields = {"previous_sha256":string,"changed_unit_ids":{"type":"array","items":string,"uniqueItems":True},
                         "actions":{"type":"array","items":string,"minItems":1}}
        fields["repair"] = {"type":"object","additionalProperties":False,"properties":repair_fields,"required":list(repair_fields)}
    return json_copy({"type": "object", "additionalProperties": False, "properties": fields, "required": required})
