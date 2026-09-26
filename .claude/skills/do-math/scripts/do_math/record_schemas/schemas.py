"""Closed record shapes for the feature-5 producers installed with this skill.

Open dictionaries occur only in explicitly named raw evidence or domain payload
fields. They are never a fallback for unknown families or record fields.
"""
from copy import deepcopy
from ..state_contract import STATE_FORMAT_VERSION, STATE_CONTRACT_ID

TEXT = {"type": "string"}
ID = {"type": "string", "minLength": 1, "pattern": r"^[A-Za-z0-9][A-Za-z0-9_.-]*$"}
INTEGER = {"type": "integer"}
NAT = {"type": "integer", "minimum": 0}
BOOL = {"type": "boolean"}
HASH = {"type": "string", "pattern": "^[0-9a-f]{64}$"}
# Evidence payloads are preserved JSON; domain validators determine their use.
EVIDENCE = {"type": "object"}


def array(item=TEXT, unique=False):
    return {"type": "array", "items": item, **({"uniqueItems": True} if unique else {})}


def nullable(schema):
    return {"anyOf": [schema, {"type": "null"}]}


def enum(*values):
    return {"enum": list(values)}


def obj(properties, required=()):
    return {"type": "object", "properties": properties, "required": list(required), "additionalProperties": False}


def record(properties, required=()):
    return obj({"id": ID, **properties}, ("id", *required))


REFS = array(ID, True)
HISTORY = array(EVIDENCE)
PROFILE_REF = obj({"id": ID, "revision": NAT, "sha256": HASH}, ("id", "revision", "sha256"))
LIFECYCLE = enum("active", "superseded", "withdrawn")
COMMON = {"family": TEXT, "producer_execution": TEXT, "origin_refs": array(TEXT), "created_at": TEXT,
          "updated_at": TEXT, "supersedes": nullable(ID), "history": HISTORY}

RECORDS = {}
RECORDS["knowledge"] = record({**COMMON,
    "kind": TEXT, "title": TEXT, "lifecycle": LIFECYCLE, "formal_result_id": nullable(ID), "exposition_id": ID,
    "dependencies": REFS, "source_refs": array(TEXT), "source_basis": HISTORY, "confirmed_scope": TEXT,
    "epistemic_status": TEXT, "selection_relevance": TEXT, "uncertainty_assessment": {"type": ["string", "object"]},
    "relation_claim": EVIDENCE,
    "relation_endpoint_basis": array(obj({"id": ID, "sha256": HASH, "status": TEXT}, ("id", "sha256", "status"))),
    "revision": NAT,
    "review_cycle_id": ID, "previous_review_cycle_id": ID, "use_suspended": BOOL,
    "change_reasons": HISTORY, "impact_plan": EVIDENCE,
    "withdrawal_reason": TEXT, "withdrawn_by": TEXT}, ("lifecycle", "exposition_id", "formal_result_id"))
RECORDS["formal_results"] = record({**COMMON, "lean_code": TEXT, "declaration_names": array(TEXT, True),
    "dependencies": REFS, "publication_state": enum("candidate", "accepted", "rejected"),
    "formal_use": enum("active", "suspended", "withdrawn"), "verification": EVIDENCE,
    "trust_environment_id": ID}, ("lean_code", "declaration_names", "publication_state", "formal_use", "verification"))
RECORDS["expositions"] = record({**COMMON, "formal_result_id": nullable(ID), "lifecycle": LIFECYCLE,
    "items": array(obj({"id": TEXT, "kind": enum("definitions", "assumptions", "statement", "explanation", "summary"),
                        "text": TEXT, "declaration_refs": array(TEXT)}, ("id", "kind", "text", "declaration_refs"))),
    "relation_claim": EVIDENCE}, ("formal_result_id", "lifecycle", "items"))
RECORDS["identity_assessments"] = record({**COMMON, "formal_result_id": ID, "exposition_id": ID,
    "decision": enum("match", "mismatch", "unresolved"), "basis": obj({"formal": HASH, "exposition": HASH}, ("formal", "exposition")),
    "policy_ref": TEXT, "scope_complete": BOOL, "execution_ids": REFS, "review_cycle_id": ID,
    "summary": TEXT, "findings": HISTORY, "relation_claim": EVIDENCE, "proposal_digest": HASH,
    "previous_assessment_id": ID, "source_ref": TEXT}, ("formal_result_id", "exposition_id", "decision", "basis", "policy_ref"))
RECORDS["assessment_uses"] = record({**COMMON, "assessment_id": ID,
    "status": enum("active", "suspended", "withdrawn")}, ("assessment_id", "status", "history"))
RECORDS["relations"] = record({"kind": TEXT, "source": ID, "target": ID,
    "evidence": TEXT, "evidence_refs": array(TEXT), "formal_result_refs": REFS, "assessment_refs": REFS,
    "confirmed_scope": TEXT, "status": TEXT, "lifecycle": LIFECYCLE, "created_at": TEXT,
    "source_ref": TEXT, "actor_ref": TEXT, "origin_refs": array(TEXT), "endpoint_basis": EVIDENCE,
    "source_basis": HISTORY, "history": HISTORY}, ("kind", "source", "target"))
RECORDS["sources"] = record({"name": TEXT, "path": TEXT, "sha256": HASH, "bytes": NAT,
    "status": TEXT, "revision": NAT, "history": HISTORY, "created_at": TEXT, "source_ref": TEXT,
    "replaced_by": ID, "revoked_at": TEXT}, ("path", "sha256"))
RECORDS["kind_definitions"] = record({"family": enum("knowledge", "relation"), "token": TEXT, "meaning": TEXT,
    "status": enum("candidate", "checked", "active", "withdrawn"), "builtin": BOOL,
    "constraints": obj({k: BOOL for k in ("mathematical_claim", "requires_evidence", "requires_formal_results", "requires_assessments")}),
    "source_ref": TEXT, "actor_ref": TEXT, "created_at": TEXT, "history": HISTORY,
    "check": EVIDENCE, "checks": HISTORY, "activation": EVIDENCE, "withdrawal": EVIDENCE}, ("family", "token", "meaning", "status", "constraints"))
RECORDS["events"] = record({"kind": TEXT, "event_seq": {"type": "integer", "minimum": 1},
    "at": TEXT, "created_at": TEXT, "actor_ref": TEXT, "subject_ref": ID, "record_refs": REFS,
    "execution_id": ID, "activity_id": ID, "reason": TEXT, "from": TEXT, "to": TEXT,
    "evidence_refs": array(TEXT)}, ("kind",))
RECORDS["integrations"] = record({"execution_id": ID, "payload_sha256": HASH,
    "members": {**array(TEXT, True), "minItems": 1}, "input_snapshot": nullable(TEXT)},
    ("execution_id", "payload_sha256", "members", "input_snapshot"))
RECORDS["activities"] = record({"activity_kind": TEXT, "owner_ref": {"type": ["string", "object"]},
    "opened_at": TEXT, "input_refs": array({"type": ["string", "object"]}),
    "status": enum("ready", "working", "waiting", "finished"), "stage": nullable(TEXT),
    "execution_limit": nullable({"type": "integer", "minimum": 1}), "assigned_execution_ids": REFS,
    "result_refs": array({"type": ["string", "object"]}), "unresolved": array({"type": ["string", "object"]}),
    "followups": array({"type": ["string", "object"]}), "waiting": obj({"reason": TEXT,
        "condition": {"type": ["string", "object"]}, "next_owner": {"type": ["string", "object"]}, "at": TEXT},
        ("reason", "condition", "next_owner", "at")), "resumed_at": TEXT, "finished_at": TEXT},
    ("activity_kind", "owner_ref", "opened_at", "input_refs", "status", "assigned_execution_ids", "result_refs", "unresolved", "followups"))
RECORDS["executions"] = record({"owner_activity_id": ID, "actor_kind": enum("ai", "machine"),
    "launch_ticket": EVIDENCE,
    "input_manifest": {"type": ["object", "array", "string"]}, "execution_profile_ref": PROFILE_REF,
    "created_at": TEXT, "status": enum("queued", "starting", "running", "stopping", "ended"),
    "continuation_of": nullable(ID), "context_origin": REFS, "role": TEXT, "action": EVIDENCE,
    "transitions": HISTORY, "ended_at": TEXT, "outcome": TEXT, "result_disposition": {"type": ["string", "object", "null"]},
    "stop_phase": enum("checkpointing", "terminating"), "submission_intent": EVIDENCE, "submission_receipt": EVIDENCE,
    "recovery": HISTORY, "recovery_disposition": TEXT, "grant_id": ID, "engine_sha256": HASH,
    "model": TEXT, "effort": TEXT, "budget_kind": TEXT, "model_decisions": EVIDENCE,
    "input_snapshot": TEXT, "input_bundle": TEXT, "input_sha256": HASH, "input_bytes": NAT,
    "input_preparation_milliseconds": NAT, "artifact_bundle": TEXT, "result_ref": TEXT, "raw_result_ref": TEXT,
    "output_files": HISTORY, "output": EVIDENCE, "error": {"type": ["string", "object", "null"]},
    "usage": EVIDENCE, "provider_observation": EVIDENCE, "pid": NAT, "process": EVIDENCE,
    "conversation_id": nullable(TEXT), "started_at": TEXT, "stop_requested": {"type": ["string", "boolean"]},
    "after_stop": EVIDENCE, "runner": EVIDENCE, "workspace": TEXT, "reservation_ids": REFS,
    "parent_execution_id": nullable(ID), "resume_from": nullable(ID), "profile_ref": PROFILE_REF,
    "initialization_id": TEXT, "input_basis": EVIDENCE, "submission_check": EVIDENCE},
    ("owner_activity_id", "actor_kind", "input_manifest", "execution_profile_ref", "created_at", "status", "context_origin"))
OBLIGATION = obj({"id": TEXT, "claim": TEXT, "evidence_required": array(TEXT),
    "evidence_requirements": array(TEXT), "judges": array(TEXT)}, ("id", "claim"))
RECORDS["tasks"] = record({"question": TEXT, "status": enum("planned", "active", "waiting", "completed", "closed"),
    "scope": obj({"included": array(TEXT), "excluded": array(TEXT)}, ("included", "excluded")),
    "expected": obj({"outputs": array(TEXT), "research_change": TEXT}, ("outputs", "research_change")),
    "progress_criteria": array(OBLIGATION), "completion_obligations": array(OBLIGATION),
    # Input/basis locators include context:, tool:, source: and supplied paths.
    # Reused records, prerequisite tasks and authority remain record IDs.
    **{k: array({"type": "string", "minLength": 1}, True) for k in ("inputs", "basis_refs")},
    **{k: REFS for k in ("reuse", "dependencies", "authority_refs")},
    "profile_refs": array(PROFILE_REF, True),
    "title": TEXT, "work_class": TEXT, "revision": NAT, "created_at": TEXT, "created_by": TEXT,
    "description": {"type": "string", "minLength": 1, "pattern": r"\S"},
    "results": HISTORY, "reviews": HISTORY, "assessment": EVIDENCE, "occurrence_condition": EVIDENCE,
    "waiting": EVIDENCE, "waiting_reason": EVIDENCE, "contract_review": EVIDENCE,
    "source_basis": HISTORY, "knowledge_basis": EVIDENCE, "model_assessment": EVIDENCE,
    "revision_history": HISTORY, "revision_requested": EVIDENCE, "change_reasons": HISTORY,
    "scope_disposition": EVIDENCE, "pending_withdrawal": EVIDENCE,
    "academic_requirement_id": {"type": "string", "minLength": 1, "pattern": r"\S"},
    "selected_by": ID, "deferred_reason": TEXT, "tools": array(TEXT), "stages": HISTORY,
    "progress": HISTORY, "proposal_version": NAT, "contract_revision": NAT},
    ("question", "scope", "expected", "progress_criteria", "completion_obligations"))
RECORDS["execution_profiles"] = record({"revision": NAT, "feature_version": {"const": STATE_FORMAT_VERSION}, "sha256": HASH,
    "role": TEXT, "actor_kind": enum("ai", "machine"), "budget_kind": enum("work", "operations"),
    "boundary": obj({"mode": TEXT, "os_isolation": BOOL, "authenticated_caller": BOOL, "rules": array(TEXT)},
                    ("mode", "os_isolation", "authenticated_caller", "rules")),
    "host_capacity_refs": REFS, "host_capacity_status": TEXT, "observation": EVIDENCE,
    "window": EVIDENCE, "input": EVIDENCE, "required_capabilities": array(TEXT),
    "capability_evidence_refs": REFS, "ai": EVIDENCE},
    ("revision", "feature_version", "sha256", "role", "actor_kind", "budget_kind", "boundary", "observation", "window", "input"))
RECORDS["capacity_constraints"] = record({"kind": enum("concurrency", "host"),
    "model": TEXT, "accounting_unit": TEXT, "work_slots": NAT, "operations_slots": NAT, "total_slots": NAT,
    "scope": TEXT, "max_jobs": NAT, "memory_bytes": NAT, "cpu_rate_basis_points": NAT}, ("kind",))
RECORDS["reservations"] = record({"schema_version": {"const": STATE_FORMAT_VERSION}, "constraint_id": ID, "unit": TEXT,
    "authority_refs": array({"type": ["string", "object"]}), "owner_kind": enum("execution"),
    "owner_id": ID, "purpose": enum("normal"), "budget_kind": enum("work", "operations"),
    "reserved": NAT, "confirmed_consumed": NAT, "returned": NAT, "state": enum("held", "settled"),
    "evidence_refs": array({"type": ["string", "object"]}), "reconcile_owner": TEXT, "reobserve": EVIDENCE},
    ("constraint_id", "unit", "owner_kind", "owner_id", "budget_kind", "reserved", "confirmed_consumed", "returned", "state"))
RECORDS["capability_evidence"] = record({"execution_profile_ref": PROFILE_REF, "identity": EVIDENCE,
    "observed_at": TEXT, "capabilities": EVIDENCE, "version_sha256": nullable(HASH),
    "help_sha256": nullable(HASH), "boundary": TEXT}, ("execution_profile_ref", "identity", "observed_at", "capabilities"))
RECORDS["grants"] = record({"kind": enum("local", "http"), "status": enum("active", "revoked", "withdrawn"),
    "budget_kind": enum("work", "operations"), "roles": array(TEXT), "task_ids": REFS,
    "expires_at": nullable(TEXT), "valid_from": nullable(TEXT), "created_at": TEXT, "source_ref": TEXT,
    "checkpoint_allowed": BOOL, "decision_id": ID, "revoked_at": TEXT, "revoked_by": ID,
    "allowed_origins": array(TEXT), "allowed_methods": array(TEXT), "allowed_path_prefixes": array(TEXT),
    "credential_env": {"type": "object", "additionalProperties": TEXT},
    "included_targets": REFS, "excluded_targets": REFS, "reuse": TEXT}, ("kind", "status", "source_ref"))
RECORDS["decisions"] = record({"kind": TEXT, "change": EVIDENCE, "source_ref": TEXT, "actor": {"const": "user"},
    "created_at": TEXT, "affected": REFS, "initial_registration": BOOL,
    "grant_id": ID, "delegation_id": ID}, ("kind", "change", "source_ref", "actor", "affected"))
RECORDS["delegations"] = record({"status": enum("active", "revoked", "withdrawn"), "decision_kind": TEXT,
    "original_decision_id": ID, "included_targets": REFS, "excluded_targets": REFS, "external_effects": array(TEXT),
    "expires_at": nullable(TEXT), "source_ref": TEXT, "decision_id": ID, "created_at": TEXT},
    ("status", "decision_kind", "original_decision_id", "included_targets", "excluded_targets", "external_effects", "expires_at"))
RECORDS["question_links"] = record({"origin_execution_id": ID, "origin_field": TEXT, "owner": TEXT,
    "target_ids": REFS, "status": enum("open", "resolved", "superseded"), "resolution_ref": nullable(ID),
    "source_ref": TEXT, "routing_reason": TEXT}, ("origin_execution_id", "origin_field", "owner", "target_ids", "status", "resolution_ref"))
RECORDS["external_operations"] = record({"request": obj({"method": TEXT, "url": TEXT, "body": TEXT}, ("method", "url", "body")),
    "request_sha256": HASH, "grant_id": ID, "source_ref": TEXT, "status": enum("prepared", "confirmed", "failed", "unknown", "cancelled"),
    "idempotency_key": HASH, "attempts": HISTORY, "credential_env": nullable(array(TEXT)), "transmitted": BOOL,
    "transmission_phase": TEXT, "retry_authorized": BOOL, "succeeded": nullable(BOOL), "effect_absent": nullable(BOOL),
    "http_status": NAT, "body_base64": TEXT, "body_sha256": HASH, "error": TEXT, "waiting_reason": EVIDENCE,
    "reconciliation": EVIDENCE, "cancellation": EVIDENCE, "academic_effect_id": ID, "academic_basis": EVIDENCE},
    ("request", "request_sha256", "grant_id", "source_ref", "status", "idempotency_key", "attempts"))
RECORDS["observation_facts"] = record({"kind": TEXT, "execution_id": ID, "event": EVIDENCE,
    "observed_at": TEXT, "monotonic_seconds": {"type": "string", "pattern": r"^-?\d+(\.\d+)?$"},
    "elapsed_ms": NAT}, ("kind", "execution_id", "event", "observed_at"))
RECORDS["self_check_obligations"] = record({"kind": TEXT, "execution_id": ID, "rule_revision": NAT,
    "due": HISTORY, "opened_at": TEXT, "deadline_monotonic": nullable(TEXT), "status": enum("open", "answered", "closed"),
    "response_ref": TEXT}, ("execution_id", "rule_revision", "due", "opened_at", "status"))
RECORDS["self_check_responses"] = record({"kind": TEXT, "execution_id": ID, "obligation_id": ID,
    "response": nullable(EVIDENCE), "observed_at": TEXT, "reason": TEXT}, ("kind", "execution_id", "obligation_id", "observed_at"))
RECORDS["operational_dispositions"] = record({"execution_id": ID, "disposition": EVIDENCE,
    "source_execution_id": ID, "created_at": TEXT, "status": TEXT}, ("execution_id", "disposition"))
RECORDS["control_receipts"] = record({"request_id": ID, "execution_id": ID, "kind": TEXT, "state": TEXT,
    "payload": EVIDENCE, "received_at": TEXT, "grant_id": ID, "reason": TEXT}, ("execution_id", "kind", "state"))
# The identity copied from one shared toolchain record and that record's file.
# The accepted baseline is the runtime trust binding, outside this record.
RECORDS["trust_environments"] = record({"status": enum("registered", "active", "superseded", "invalid"),
    "toolchain": EVIDENCE, "allowed_axioms": array(TEXT), "source_ref": TEXT,
    "toolchain_record": obj({"path": TEXT, "id": TEXT}, ("path", "id")),
    "validation_receipt": EVIDENCE, "invalidated_reason": TEXT},
    ("status", "toolchain", "allowed_axioms", "source_ref", "toolchain_record"))
RECORDS["review_cycles"] = record({
    **{k: EVIDENCE for k in ("proposal", "review_policy", "execution_accounting", "results", "turns", "transcript_manifest", "issues", "findings", "deferred_actions", "research")},
    **{k: HISTORY for k in ("history", "previous_reviews", "followup", "pending_findings", "answer_requests", "recovery_events")},
    **{k: array(TEXT) for k in ("reviewer_slots", "requested_reviewer_slots", "retained_reviewer_slots", "judge_slots", "required_source_refs", "sealed")},
    **{k: NAT for k in ("revision", "reviewers", "judges", "max_rounds", "round", "activity_execution_limit")},
    "proposal_digest": HASH, "review_lineage_id": TEXT, "scope_assessment": nullable(EVIDENCE),
    "owner_activity_id": nullable(ID), "phase": TEXT, "status": TEXT, "decision": nullable(TEXT),
    "knowledge_id": ID, "producer_execution": ID}, ("proposal", "proposal_digest", "revision", "phase", "status"))
RECORDS["goal_judgments"] = record({"execution_id": ID, "basis": TEXT, "decision": TEXT, "scope_complete": BOOL,
    "summary": TEXT, "findings": array(TEXT), "used_sources": array(TEXT), "questions": array(TEXT),
    "slot": {"type": ["integer", "string"]}, "required": NAT, "created_at": TEXT, "input_basis": EVIDENCE}, ("execution_id", "decision", "basis"))

# Scalar and singleton state are enumerated explicitly; unknown top-level keys
# never acquire a storage location based on their run-time Python shape.
RESEARCH_FIELDS = {
    "id": ID, "feature_version": {"const": STATE_FORMAT_VERSION}, "contract_id": {"const": STATE_CONTRACT_ID},
    "object_format": enum("sha1", "sha256"), "title": TEXT,
    "workspace": TEXT, "created_at": TEXT, "goal_status": TEXT,
    "active_trust_environment": nullable(ID),
    "conversation_loss_policy": TEXT, "governance_approval": {"type": ["boolean", "object"]},
    "goal_assessment_basis": TEXT,
    "role_profile_refs": {"type": "object", "additionalProperties": array(PROFILE_REF)},
    "lifecycle": obj({"state": TEXT, "immutable_input": obj({"text": TEXT, "sha256": HASH, "bytes": NAT},
        ("text", "sha256", "bytes")),
        "initial_profile_id": nullable(ID), "required_capabilities": array(TEXT), "requires_initial_profile": BOOL,
        "activation": obj({"completed": array(TEXT), "missing": array(TEXT), "observation_errors": HISTORY}), "resume_state": TEXT,
        "permanently_closed": BOOL, "history": HISTORY}, ("state", "immutable_input")),
}
RUNTIME_FIELDS = {"feature_version": {"const": STATE_FORMAT_VERSION}, "contract_id": {"const": STATE_CONTRACT_ID}, "status": TEXT,
    "cycles": NAT, "active_execution": nullable(ID), "active_executions": REFS, "updated_at": TEXT,
    "processed_controls": REFS, "questions": array(TEXT), "history": HISTORY,
    "recovery_checked": BOOL, "last_observed_utc": TEXT, "event_cursor": NAT,
    "availability": obj({"state": TEXT, "reason": TEXT, "next_owner": TEXT}, ("state",)),
    "clock_guard": obj({"state": TEXT, "observed_at": TEXT, "reason": TEXT, "high_water": TEXT}),
    "pending_events": REFS,
    "user_pause": {"type": ["boolean", "object"]}, "stop_requested": {"type": ["boolean", "string"]},
    "next_research_reconsider_at": nullable(TEXT), "installation": EVIDENCE,
    "interpretation_history": HISTORY, "implementation_history": HISTORY,
    "model_policy_violation": EVIDENCE, "provider_wake": EVIDENCE,
    "pending_knowledge_impacts": HISTORY, "permission_requests": HISTORY,
    # Per trust environment: the toolchain-record baseline whose fingerprint was last accepted.
    "trust_bindings": {"type": "object", "additionalProperties": obj({"baseline": NAT,
        "fingerprint_sha256": HASH, "content_sha256": HASH, "validation_sha256": HASH},
        ("baseline", "fingerprint_sha256", "content_sha256", "validation_sha256"))},
}
