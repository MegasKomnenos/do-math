"""Closed record shapes for the producers installed with this skill.

Each family's schema is defined once, in its final form. Open dictionaries
occur only in explicitly named raw evidence or domain payload fields. They are
never a fallback for unknown families or record fields. Lookup containers are
keyed by existing record identities, not newly allocated global IDs; their
values have closed schemas and are not a catch-all metadata family.
"""
from copy import deepcopy as _deepcopy

from ..activities import ACTIVITY_STATUSES as _ACTIVITY_STATUSES
from ..contracts import (PLAN_DISPOSITION as _PLAN_DISPOSITION, TEXT as _NONEMPTY_TEXT,
                         schema_for as _schema_for)
from ..execution_lifecycle import EXECUTION_STATUSES as _EXECUTION_STATUSES, OUTCOMES as _OUTCOMES
from ..execution_profiles import (OBSERVATION_KEYS as _OBSERVATION_KEYS, OBSERVATION_MODES as _OBSERVATION_MODES,
                                  PROFILE_ROLES as _PROFILE_ROLES, WINDOW_KEYS as _WINDOW_KEYS)
from ..external import OPERATION_STATUSES as _OPERATION_STATUSES
from ..values import SHA256_SCHEMA as HASH, json_copy
from ..governance import (GOVERNANCE_STATUSES as _GOVERNANCE_STATUSES, GRANT_STATUSES as _GRANT_STATUSES,
                          interpretation_schema as _interpretation_schema)
from ..input_basis import SOURCE_STATUSES as _SOURCE_STATUSES
from ..knowledge_io import KIND_STATUSES as _KIND_STATUSES
from ..knowledge_records import (ASSESSMENT_USE_STATUSES as _ASSESSMENT_USE_STATUSES,
                                 RECORD_LIFECYCLES as _RECORD_LIFECYCLES)
from ..model_policy import ASSESSMENT_SCHEMA as _ASSESSMENT_SCHEMA, TIERS as _TIERS
from ..observations import CHECKPOINT_SCHEMA as _CHECKPOINT_SCHEMA, RULE_ID_SCHEMA as _RULE_ID_SCHEMA
from ..questions import QUESTION_OWNERS as _QUESTION_OWNERS
from ..review_cycle import CYCLE_STATUSES as _CYCLE_STATUSES
from ..state_contract import RECORD_ID
from ..task_contracts import LIFECYCLE_STATES as _LIFECYCLE_STATES, REPEAT_LINEAGES as _REPEAT_LINEAGES
from ..trust_validation import (BINDING_SCHEMA as _BINDING_SCHEMA, ENVIRONMENT_PROPERTIES as _ENVIRONMENT_PROPERTIES,
                                ENVIRONMENT_REQUIRED as _ENVIRONMENT_REQUIRED)

TEXT = {"type": "string"}
ID = {"type": "string", "minLength": 1, "pattern": "^" + RECORD_ID + "$"}
INTEGER = {"type": "integer"}
NAT = {"type": "integer", "minimum": 0}
BOOL = {"type": "boolean"}
# Evidence payloads are preserved JSON; domain validators determine their use.
EVIDENCE = {"type": "object"}


def array(item=TEXT, unique=False):
    return json_copy({"type": "array", "items": item, **({"uniqueItems": True} if unique else {})})


def nullable(schema):
    return json_copy({"anyOf": [schema, {"type": "null"}]})


def enum(*values):
    return json_copy({"enum": list(values)})


def obj(properties, required=()):
    return json_copy({"type": "object", "properties": properties, "required": list(required), "additionalProperties": False})


def record(properties, required=()):
    return obj({"id": ID, **properties}, ("id", *required))


def mapping(value):
    return json_copy({"type": "object", "additionalProperties": value})


REFS = array(ID, True)
HISTORY = array(EVIDENCE)
PROFILE_REF = obj({"id": ID, "revision": {"type": "integer", "minimum": 1}, "sha256": HASH}, ("id", "revision", "sha256"))
LIFECYCLE = enum(*sorted(_RECORD_LIFECYCLES))
COMMON = {"family": TEXT, "producer_execution": TEXT, "origin_refs": array(TEXT), "created_at": TEXT,
          "updated_at": TEXT, "supersedes": nullable(ID), "history": HISTORY}

# Shapes shared by several families.
_SOLUTION_BASIS = obj({"goal_ref": TEXT, "records": array(obj({"id": ID, "sha256": HASH}, ("id", "sha256")))},
                      ("goal_ref", "records"))
_IDENTITY_BASIS = obj({"formal": HASH, "exposition": HASH}, ("formal", "exposition"))
_EXTERNAL_EFFECT = obj({"id": _NONEMPTY_TEXT, "scope": _NONEMPTY_TEXT, "grant_id": nullable(ID)}, ("id", "scope"))
_RECORD_TASK = obj({"record_id": ID, "task_id": ID}, ("record_id", "task_id"))
_HOST_AMOUNTS = obj({"jobs": NAT, "memory_bytes": NAT,
    "cpu_rate_basis_points": {"type": "integer", "minimum": 0, "maximum": 10000}},
    ("jobs", "memory_bytes", "cpu_rate_basis_points"))
_RULE = obj({"id": _RULE_ID_SCHEMA, "operator": TEXT, "subject": obj({"kind": TEXT, "id": TEXT}, ("kind", "id")),
    "basis": obj({"source": TEXT, "unit": TEXT}, ("source", "unit")),
    "threshold": {"type": ["integer", "string"]}, "repeat_interval": NAT,
    "required_evidence": array(TEXT, True)}, ("id", "operator", "subject", "basis", "threshold", "required_evidence"))
_MODEL_SELECTION = obj({"tier": nullable(enum(*_TIERS)), "model": TEXT,
    "assessment": nullable(_ASSESSMENT_SCHEMA), "reason": TEXT, "profile_ref": PROFILE_REF},
    ("tier", "model", "assessment", "reason"))
_METRICS = obj({"unit": enum("UTF-8_bytes"), "prompt_bytes": NAT, "context_bytes": NAT,
    "schema_bytes": NAT, "document_bytes": mapping(NAT), "context_component_value_bytes": mapping(NAT),
    "framing_bytes": INTEGER},
    ("unit", "prompt_bytes", "context_bytes", "schema_bytes", "document_bytes",
     "context_component_value_bytes", "framing_bytes"))
_OVERFLOW = obj({"kind": enum("input_overflow"), "reason": TEXT, "actual_bytes": NAT,
    "mandatory_bytes": NAT, "limit_bytes": NAT, "required_direct_keys": array(TEXT, True),
    "role": nullable(TEXT), "profile_id": nullable(ID), "activity_id": nullable(ID),
    "packed_bytes": NAT, "original_bytes": NAT, "context_budget_bytes": NAT, "unit": enum("utf8_bytes"),
    "component_bytes": mapping(NAT), "reductions": HISTORY, "prompt_metrics": _METRICS,
    "cause": enum("common_documents_or_governance", "required_role_input", "current_proposal_or_required_sources", "restored_dialogue"),
    "without_restored_dialogue_bytes": NAT, "allowed_profile_candidates": REFS,
    "suggested_disposition": enum("unresolved_to_review_plan", "plan_allowed_profile", "request_user_decision"),
    "resolution_question": obj({"kind": enum("input_capacity"), "activity_id": nullable(ID),
        "role": nullable(TEXT), "required_direct_keys": array(TEXT, True), "question": TEXT,
        "next_owner": enum("research_plan", "user")}, ("question", "next_owner"))},
    ("kind", "reason", "actual_bytes", "mandatory_bytes", "limit_bytes", "required_direct_keys",
     "role", "profile_id", "activity_id"))
_IMPACT_PLAN = obj({**{name: REFS for name in ("roots", "computed_impact", "declared_impact",
    "missing_declarations", "extra_declarations", "unresolved_refs")}, "sensitive": BOOL,
    "requires_independent_review": BOOL, "basis": mapping(HASH), "digest": HASH},
    ("roots", "computed_impact", "declared_impact", "missing_declarations", "extra_declarations",
     "unresolved_refs", "sensitive", "requires_independent_review", "basis", "digest"))
_IMPACT_REQUEST = obj({"integration_id": TEXT, "payload_sha256": HASH, "producer_execution_id": ID,
    "input_snapshot": TEXT, "plans": mapping(_IMPACT_PLAN)},
    ("integration_id", "payload_sha256", "producer_execution_id", "input_snapshot", "plans"))

# A queued action. An action embedded in an execution or wait is a historical
# input copy, not another live queue record/global identity.
_ACTION = record({"role": TEXT, "target": nullable(TEXT), "stage": TEXT, "slot": {"type": ["string", "integer"]},
    "round": NAT, "reason": TEXT, "grant_id": ID, "profile_ref": PROFILE_REF,
    "owner_activity_id": ID, "activity_id": ID, "execution_id": ID, "continuation_of": ID,
    "context_origin": REFS, "lineage_id": ID, "review_cycle_id": ID, "import_id": ID,
    "previous_import_id": ID, "transition_id": ID, "decision_id": ID, "rejection_id": ID,
    "created_at": TEXT, "live": BOOL, "initialization": BOOL, "required": {"anyOf": [BOOL, NAT]},
    "repair_attempt": NAT, "diagnosis_attempt": NAT, "initial_submission_diagnosis": BOOL,
    **{key: EVIDENCE for key in ("repair", "observation", "dispatch_wait", "revision_targets", "exhaustion_basis", "model_assessment", "input_basis", "assessment_targets", "input_overflow_retry")},
    **{key: array(TEXT, True) for key in ("event_refs", "receipt_refs", "obligation_ids", "observation_refs", "affected_ids", "evidence_refs")},
    "review_basis_key": TEXT, "settle_started_at": TEXT, "source_ref": TEXT,
    "observation_rule_targets": mapping(obj(
        {"revision": {"type": "integer", "minimum": 1}, "contract_sha256": HASH}, ("revision", "contract_sha256"))),
    "repetition_bases": obj({name: HASH for name in _REPEAT_LINEAGES}),
    "repetition_lineage": {"type": "array", "prefixItems": [enum(*_REPEAT_LINEAGES), TEXT], "items": False, "minItems": 2},
    "requested_by": ID, "requested_by_refs": REFS, "cleanup_execution_ids": REFS,
    "periodic_reconsideration": BOOL, "exhaustion_event_ref": ID,
    "opened_at": TEXT, "merged_action_ids": REFS, "selected_contract_sha256": HASH, "selection_execution_id": ID,
    "scope_decision_id": ID, "revision_request_action_id": ID,
    "basis": HASH, "kind_definition_id": ID, "kind_definition_sha256": HASH,
    "formal_target": ID,
    "model_selection": _MODEL_SELECTION,
    "contract_basis": obj({"revision": NAT, "contract_sha256": HASH, "goal_revision": NAT,
        "policy_revision": {"type": ["integer", "string"]}},
        ("revision", "contract_sha256", "goal_revision", "policy_revision")),
    "actor_kind": enum("ai", "machine"),
    "purpose": TEXT, "continuity_break_cause": TEXT, "continuity_broken": BOOL, "grant_sha256": HASH,
    "replacement_for": NAT, "owner_review_cycle_id": ID, "identity_review": EVIDENCE,
    "knowledge_id": ID,
    "input_overflow": _OVERFLOW, "overflow_activity_id": ID,
    "delegation_application_id": ID, "contract_review_execution": ID,
    "research_request_id": TEXT, "requesting_slot": TEXT,
    "revision_cycles": array(array(ID)), "revision_parent_ids": REFS, "unbound_request": BOOL,
    "reasons": array(TEXT), "superseded_revision_bases": HISTORY,
    "revision_followup": array(_RECORD_TASK),
    "intent_repair": obj({"import_id": ID, "previous_sha256": HASH, "check_execution_id": ID,
        "findings": array(TEXT)}, ("import_id", "previous_sha256", "check_execution_id", "findings")),
    "recovery": obj({"execution_id": ID, "disposition_id": ID, "reason": TEXT,
        "provider_generation": NAT}, ("execution_id", "reason")),
    "refresh": obj({"execution_id": ID,
        "changes": HISTORY, "attempt": NAT}, ("execution_id", "changes", "attempt"))}, ("role",))
_ACTION["allOf"] = [{"if": {"properties": {"stage": {"const": "impact_review"}}, "required": ["stage"]},
    "then": {"properties": {"role": {"const": "maintenance"},
        "input_basis": obj({"impact_review": _IMPACT_REQUEST}, ("impact_review",))}, "required": ["input_basis"]}}]

RECORDS = {}
# The one shape of an academic requirement; academic.requirement_record adds
# the rules across items (distinct requirement and effect IDs).
ACADEMIC_REQUIREMENT = obj({"id": _NONEMPTY_TEXT, "scope": _NONEMPTY_TEXT, "assessor": enum("research_plan"),
    "criteria": {**array(_NONEMPTY_TEXT, True), "minItems": 1}, "required_inputs": array(_NONEMPTY_TEXT, True),
    "external_effects": array(_EXTERNAL_EFFECT)},
    ("id", "scope", "assessor", "criteria"))
RECORDS["governance"] = record({"kind": enum("charter", "policy", "research_context", "additional_audit"),
    "revision": {"type": "integer", "minimum": 1}, "supersedes": REFS,
    "content": obj({**{k: TEXT for k in ("rationale", "goal", "desired_result", "evidence_boundary", "decision_authority", "rule_id", "text", "assessor")},
        **{k: array(TEXT, True) for k in ("success_criteria", "partial_success_criteria", "included_scope", "excluded_scope", "priorities", "preferences", "stop_conditions", "scope", "reason_refs", "audit_refs", "required_inputs")},
        "academic_requirements": array(ACADEMIC_REQUIREMENT), "verdict_mapping": mapping(enum("satisfied", "not_satisfied", "unresolved")),
        "terms": array(obj({"term": TEXT, "definition": TEXT, "boundary": TEXT, "avoid_synonyms": array(TEXT), "record_refs": REFS},
                           ("term", "definition", "boundary", "avoid_synonyms", "record_refs")))}),
    "document": obj({"ref": TEXT, "sha256": HASH}, ("ref", "sha256")), "status": enum(*sorted(_GOVERNANCE_STATUSES)),
    "approval_ref": ID, "source_ref": ID, "content_sha256": HASH, "superseded_by": ID},
    ("kind", "revision", "supersedes", "content", "status", "approval_ref", "source_ref", "content_sha256"))
RECORDS["governance_sources"] = record({"text": TEXT, "origin": TEXT, "revision": NAT, "sha256": HASH, "bytes": NAT},
    ("text", "origin", "revision", "sha256", "bytes"))
RECORDS["knowledge"] = record({**COMMON,
    "kind": TEXT, "title": TEXT, "lifecycle": LIFECYCLE, "formal_result_id": nullable(ID), "exposition_id": ID,
    "dependencies": REFS, "source_refs": array(TEXT), "source_basis": HISTORY, "confirmed_scope": TEXT,
    "epistemic_status": TEXT, "selection_relevance": TEXT, "uncertainty_assessment": {"type": ["string", "object"]},
    "relation_claim": EVIDENCE,
    "relation_endpoint_basis": array(obj({"id": ID, "sha256": HASH, "status": TEXT}, ("id", "sha256", "status"))),
    "revision": NAT,
    "review_cycle_id": ID, "previous_review_cycle_id": ID, "use_suspended": BOOL,
    "withdrawal_reason": TEXT, "withdrawn_by": TEXT,
    "kind_definition_id": ID, "kind_use_suspended": BOOL, "imported_at": TEXT, "imported_by": TEXT, "source_ref": TEXT,
    "revision_reason": TEXT, "use_suspensions": HISTORY, "use_suspension_reasons": array(TEXT), "actor_ref": TEXT,
    "task_id": ID}, ("lifecycle", "exposition_id", "formal_result_id"))
RECORDS["formal_results"] = record({**COMMON, "family": {"const": "formal_results"},
    "lean_code": TEXT, "declaration_names": array(TEXT, True),
    "dependencies": REFS, "publication_state": enum("candidate", "accepted", "rejected"),
    "formal_use": enum("active", "suspended", "withdrawn"), "verification": EVIDENCE,
    "trust_environment_id": ID, "transition_id": ID, "use_history": HISTORY},
    ("family", "lean_code", "declaration_names", "publication_state", "formal_use", "verification"))
RECORDS["expositions"] = record({**COMMON, "family": {"const": "expositions"},
    "formal_result_id": nullable(ID), "lifecycle": LIFECYCLE,
    "items": array(obj({"id": TEXT, "kind": enum("definitions", "assumptions", "statement", "explanation", "summary"),
                        "text": TEXT, "declaration_refs": array(TEXT)}, ("id", "kind", "text", "declaration_refs"))),
    "relation_claim": EVIDENCE}, ("family", "formal_result_id", "lifecycle", "items"))
RECORDS["identity_assessments"] = record({**COMMON, "family": {"const": "identity_assessments"},
    "formal_result_id": ID, "exposition_id": ID,
    "decision": enum("match", "mismatch", "unresolved"), "basis": _IDENTITY_BASIS,
    "policy_ref": TEXT, "scope_complete": BOOL, "execution_ids": REFS, "review_cycle_id": ID,
    "summary": TEXT, "findings": HISTORY, "relation_claim": EVIDENCE, "proposal_digest": HASH,
    "previous_assessment_id": ID, "source_ref": TEXT,
    "transition_id": ID, "transition_basis": HASH, "reviewed_identity_basis": EVIDENCE,
    "continuity_comparison": obj({"equivalent": BOOL, "missing": array(TEXT), "changed": array(TEXT),
        "requires_identity_review": BOOL}, ("equivalent", "missing", "changed", "requires_identity_review"))},
    ("family", "formal_result_id", "exposition_id", "decision", "basis", "policy_ref"))
RECORDS["assessment_uses"] = record({**COMMON, "family": {"const": "assessment_uses"}, "assessment_id": ID,
    "status": enum(*sorted(_ASSESSMENT_USE_STATUSES)),
    "environment_revalidation": obj({"environment_id": ID, "reason": TEXT}, ("environment_id", "reason")),
    "use_history": HISTORY}, ("family", "assessment_id", "status", "history"))
RECORDS["relations"] = record({"kind": TEXT, "source": ID, "target": ID,
    "evidence": TEXT, "evidence_refs": array(TEXT), "formal_result_refs": REFS, "assessment_refs": REFS,
    "confirmed_scope": TEXT, "status": TEXT, "lifecycle": LIFECYCLE, "created_at": TEXT,
    "source_ref": TEXT, "actor_ref": TEXT, "origin_refs": array(TEXT),
    "source_basis": HISTORY, "history": HISTORY,
    "kind_definition_id": ID, "authority": enum("mathematical_connection", "research_connection"),
    "revision": NAT, "imported_at": TEXT, "imported_by": TEXT, "use_history": HISTORY}, ("kind", "source", "target"))
RECORDS["sources"] = record({"name": TEXT, "path": TEXT, "sha256": HASH, "bytes": NAT,
    "status": enum(*sorted(_SOURCE_STATUSES)), "revision": NAT, "history": HISTORY, "created_at": TEXT, "source_ref": TEXT},
    ("path", "sha256"))
RECORDS["kind_definitions"] = record({"family": enum("knowledge", "relation"), "token": TEXT, "meaning": TEXT,
    "status": enum(*sorted(_KIND_STATUSES)), "builtin": BOOL,
    "constraints": obj({**{k: BOOL for k in ("mathematical_claim", "requires_evidence", "requires_formal_results", "requires_assessments")},
        "required_fields": array(TEXT, True), "allowed_epistemic_statuses": array(TEXT, True)}),
    "source_ref": TEXT, "actor_ref": TEXT, "created_at": TEXT, "history": HISTORY,
    "check": EVIDENCE, "checks": HISTORY, "activation": EVIDENCE,
    "supersedes": ID,
    **{key: TEXT for key in ("check_ref", "checked_by", "approval_ref", "activated_by", "withdrawn_reason", "withdrawn_by")}},
    ("family", "token", "meaning", "status", "constraints"))
RECORDS["events"] = record({"kind": TEXT, "event_seq": {"type": "integer", "minimum": 1},
    "at": TEXT, "created_at": TEXT, "actor_ref": TEXT, "record_refs": REFS,
    "execution_id": ID, "activity_id": ID, "reason": TEXT, "from": TEXT, "to": TEXT,
    "evidence_refs": array(TEXT),
    "opened_at": TEXT, "target": nullable(TEXT), "source_ref": nullable(TEXT),
    "generation": NAT, "previous_status": TEXT, "status": TEXT, "request_id": TEXT,
    "decision_id": ID, "affected_ids": REFS, "transition_id": ID, "environment_id": ID,
    "execution_ids": REFS, "task_ids": REFS, "revision": NAT, "detail": TEXT,
    "basis_sha256": HASH, "basis": EVIDENCE,
    "observed_at": TEXT, "regenerate_after": nullable(TEXT),
    "scope": TEXT, "next_owner": TEXT, "affected": REFS,
    "errors": array(TEXT), "request_sha256": HASH, "result": TEXT,
    "judgment_ids": REFS, "artifact_ref": TEXT, "outcome": TEXT, "evidence": EVIDENCE}, ("kind",))
RECORDS["integrations"] = record({"execution_id": ID, "payload_sha256": HASH,
    "members": {**array(TEXT, True), "minItems": 1}, "input_snapshot": nullable(TEXT), "response_sha256": HASH},
    ("execution_id", "payload_sha256", "members", "input_snapshot"))
RECORDS["activities"] = record({"activity_kind": TEXT, "owner_ref": {"type": ["string", "object"]},
    "opened_at": TEXT, "input_refs": array({"type": ["string", "object"]}),
    "status": enum(*sorted(_ACTIVITY_STATUSES)), "stage": nullable(TEXT),
    "execution_limit": nullable({"type": "integer", "minimum": 1}), "assigned_execution_ids": REFS,
    "result_refs": array({"type": ["string", "object"]}), "unresolved": array({"type": ["string", "object"]}),
    "followups": array({"type": ["string", "object"]}), "waiting": obj({"reason": TEXT,
        "condition": {"type": ["string", "object"]}, "next_owner": {"type": ["string", "object"]}, "at": TEXT},
        ("reason", "condition", "next_owner", "at")), "resumed_at": TEXT, "finished_at": TEXT},
    ("activity_kind", "owner_ref", "opened_at", "input_refs", "status", "assigned_execution_ids", "result_refs", "unresolved", "followups"))
# GOVERNANCE preserves the exact delivered audit and referenced record
# snapshots. Semantic checks bind those snapshots and mapped verdicts.
_AUDIT_INPUT = obj({"audit": RECORDS["governance"], "audit_sha256": HASH,
    "inputs": mapping(EVIDENCE), "input_hashes": mapping(HASH)},
    ("audit", "audit_sha256", "inputs", "input_hashes"))
_AUDIT_RESULT = obj({"audit_ref": ID, "audit_sha256": HASH, "assessor": TEXT, "verdict": TEXT,
    "decision": enum("satisfied", "not_satisfied", "unresolved"), "input_hashes": mapping(HASH),
    "execution_id": ID, "reason": {"type": "string", "minLength": 1}},
    ("audit_ref", "audit_sha256", "assessor", "verdict", "decision", "input_hashes", "execution_id", "reason"))
# The role input manifest (input_manifest) holds the prompt digest and the
# sealed input archive paths below runtime/artifacts/<input_bundle>.
RECORDS["executions"] = record({"owner_activity_id": ID, "actor_kind": enum("ai", "machine"),
    "launch_ticket": EVIDENCE,
    "input_manifest": {"type": ["object", "array", "string"]}, "execution_profile_ref": PROFILE_REF,
    "created_at": TEXT, "status": enum(*sorted(_EXECUTION_STATUSES)),
    "continuation_of": nullable(ID), "context_origin": REFS, "role": TEXT, "action": _ACTION,
    "transitions": HISTORY, "ended_at": TEXT, "outcome": enum(*sorted(_OUTCOMES)), "result_disposition": {"type": ["string", "object", "null"]},
    "submission_intent": EVIDENCE, "submission_receipt": EVIDENCE,
    "recovery_disposition": TEXT, "grant_id": ID,
    "model": TEXT, "effort": TEXT, "model_decisions": EVIDENCE,
    "input_snapshot": TEXT, "input_bundle": TEXT,
    "input_preparation_milliseconds": NAT, "artifact_bundle": TEXT, "result_ref": TEXT, "raw_result_ref": TEXT,
    "output_files": HISTORY, "output": EVIDENCE, "error": {"type": ["string", "object", "null"]},
    "usage": EVIDENCE, "provider_observation": EVIDENCE, "pid": NAT,
    "conversation_id": nullable(TEXT), "started_at": TEXT, "stop_requested": {"type": ["string", "boolean"]},
    "after_stop": EVIDENCE, "runner": EVIDENCE, "workspace": TEXT,
    "parent_execution_id": nullable(ID), "profile_ref": PROFILE_REF,
    "input_basis": EVIDENCE, "submission_check": EVIDENCE,
    "additional_audit_input": array(_AUDIT_INPUT), "source_ref": TEXT,
    "operation_id": ID, "request_sha256": HASH,
    "effect_status": enum(*sorted(_OPERATION_STATUSES)),
    "http_status": nullable(NAT), "succeeded": nullable(BOOL),
    # session_slots records the reservations, provider, process and local termination.
    "capacity": obj({"provider": nullable(TEXT), "reservation_ids": REFS,
        "process": nullable(EVIDENCE), "local_termination": enum("unknown", "confirmed")}),
    **{key: TEXT for key in ("submission_check_ref", "submitted_output_ref", "submitted_extensions_ref",
        "formal_status", "error_kind", "input_published_at", "finished_at", "started", "observed_at",
        "stop_observed_at", "preserved_reason")},
    **{key: HASH for key in ("intent_import_sha256", "contract_sha256", "academic_requirements_sha256", "delegation_input_sha256")},
    **{key: EVIDENCE for key in ("safe_boundary_report", "extensions", "integration_result", "control_transport",
        "decision_basis", "operational_continuation", "input_solution_basis",
        "termination", "collection", "currentness", "failure")},
    **{key: HISTORY for key in ("source_basis", "input_reductions", "currentness_changes")},
    "input_metrics": _METRICS,
    "validity_basis": array(obj({"id": ID, "sha256": HASH, "status": nullable(TEXT)}, ("id", "sha256", "status"))),
    "usage_segments": array(obj({"segment": NAT, "line": NAT, "usage": EVIDENCE},
                               ("segment", "line", "usage"))),
    "model_usage_reported": EVIDENCE,
    "usage_scope": obj({key: TEXT for key in ("usage", "model_usage_reported", "total_cost_usd")},
                       ("usage", "model_usage_reported", "total_cost_usd")),
    "reported_models": array(TEXT, True),
    "model_selection": nullable(_MODEL_SELECTION), "integration_id": ID, "goal_revision": NAT,
    "policy_revision": {"type": ["integer", "string"]}, "pending_operational_disposition": ID,
    "outputs_complete": BOOL,
    "stop_reason": {"type": ["string", "boolean"]},
    "authority_revocation": obj({"scope": enum("execution_research"), "reason": enum("submission_intent"),
        "at": TEXT, "receipt_id": ID}, ("scope", "reason", "at", "receipt_id")),
    "observation_stream": obj({'end_offset': NAT, 'received_at': TEXT, 'applied_at': TEXT,
                                'local_termination_confirmed': BOOL},
                               ('end_offset', 'received_at', 'applied_at', 'local_termination_confirmed')),
    "execution_window": obj({"execution_id": ID, "effective_deadline_at": nullable(TEXT),
        "remaining_ms_at_start": nullable(NAT), "deadline_source": TEXT, "finish_notice_at": nullable(TEXT),
        "effective_notice_ms": NAT}, ("execution_id", "effective_deadline_at", "remaining_ms_at_start",
                                      "deadline_source", "finish_notice_at", "effective_notice_ms")),
    "input_preparation": obj({"stage": {"type": "string", "minLength": 1}, "started_at": TEXT,
        "updated_at": TEXT, "finished_at": TEXT, "reason": {"type": "string", "minLength": 1}},
        ("stage", "started_at", "updated_at")),
    "observation_rules": array(_RULE)},
    ("owner_activity_id", "actor_kind", "input_manifest", "execution_profile_ref", "created_at", "status", "context_origin"))
# The stored task contract states its whole shape here: nonempty text and
# lists, a positive revision, exact profile references (PROFILE_REF, revision
# at least 1), distinct evidence and judged completion obligations.
# task_contracts.validate_contract_meaning keeps what this schema does not
# express (distinct criterion, obligation and profile IDs), and
# validate_task_contract applies both to tasks in memory.
_CRITERION_FIELDS = {"id": {"type": "string", "minLength": 1}, "claim": _NONEMPTY_TEXT,
    "evidence_required": array({"type": "string", "minLength": 1}, True),
    "evidence_requirements": array(_NONEMPTY_TEXT, True)}
_PROGRESS_CRITERION = obj({**_CRITERION_FIELDS, "judges": array(TEXT)}, ("id", "claim"))
_COMPLETION_OBLIGATION = obj({**_CRITERION_FIELDS, "judges": {**array(_NONEMPTY_TEXT), "minItems": 1}},
                             ("id", "claim", "judges"))
_SELECTION = _deepcopy(_PLAN_DISPOSITION)
_SELECTION["properties"].update({"execution_id": ID, "contract_sha256": HASH})
_SELECTION["required"] += ["execution_id", "contract_sha256"]
_ASSESSMENT = _deepcopy(_schema_for("research_plan")["properties"]["task_assessments"]["items"])
_ASSESSMENT["properties"].update({"execution_id": ID, "contract_sha256": HASH, "results_sha256": HASH,
                                  "current": BOOL, "basis": EVIDENCE, "invalidated_reason": TEXT,
                                  "specialist_support": mapping(ID)})
RECORDS["tasks"] = record({"question": _NONEMPTY_TEXT, "status": enum(*sorted(_LIFECYCLE_STATES)),
    "scope": obj({"included": array(_NONEMPTY_TEXT), "excluded": array(_NONEMPTY_TEXT)}, ("included", "excluded")),
    "expected": obj({"outputs": {**array(_NONEMPTY_TEXT), "minItems": 1}, "research_change": _NONEMPTY_TEXT},
                    ("outputs", "research_change")),
    "progress_criteria": {**array(_PROGRESS_CRITERION), "minItems": 1},
    "completion_obligations": {**array(_COMPLETION_OBLIGATION), "minItems": 1},
    # Input/basis locators include context:, tool:, source: and supplied paths.
    # Reused records, prerequisite tasks and authority remain record IDs.
    **{k: array({"type": "string", "minLength": 1}, True) for k in ("inputs", "basis_refs")},
    **{k: REFS for k in ("reuse", "dependencies", "authority_refs")},
    "profile_refs": array(PROFILE_REF, True),
    "title": TEXT, "work_class": TEXT, "revision": {"type": "integer", "minimum": 1}, "created_at": TEXT,
    "description": _NONEMPTY_TEXT,
    "results": HISTORY, "reviews": HISTORY, "assessment": _ASSESSMENT, "occurrence_condition": EVIDENCE,
    "waiting": EVIDENCE, "waiting_reason": EVIDENCE, "contract_review": EVIDENCE,
    "source_basis": HISTORY, "model_assessment": EVIDENCE,
    "revision_history": HISTORY, "revision_requested": EVIDENCE,
    "scope_disposition": EVIDENCE,
    "academic_requirement_id": _NONEMPTY_TEXT,
    "selected_by": ID, "deferred_reason": TEXT, "tools": array(TEXT),
    "progress": HISTORY, "proposal_version": NAT, "contract_revision": NAT,
    "initial_observation_rules": HISTORY,
    "newinput": ID, "solution_basis": _SOLUTION_BASIS,
    "requirements_sha256": HASH, "governance_revision_required": obj({"decision_ref": ID, "record_ref": ID}, ("decision_ref", "record_ref")),
    "trust_environment_id": ID,
    "producer_execution": ID, "author_execution_ids": REFS, "revision_request_action_id": ID,
    "knowledge_revision_targets": REFS, "selection_disposition": _SELECTION,
    "assessment_history": array(_ASSESSMENT),
    "required_external_effects": array(_EXTERNAL_EFFECT),
    "transferred_obligations": array(obj({"from_task": ID, "from_revision": {"type": "integer", "minimum": 1},
        "from_obligation_id": TEXT, "obligation_id": TEXT, "authority_ref": ID, "execution_id": ID},
        ("from_task", "from_revision", "from_obligation_id", "obligation_id", "authority_ref", "execution_id"))),
    "use_history": HISTORY, "input_current": BOOL,
    "remaining_work": array(TEXT),
    "observation_rule_history": HISTORY,
    "model_assessment_history": array(obj({"revision": NAT, "contract_sha256": HASH,
        "assessment": _ASSESSMENT_SCHEMA, "contract_review_execution": ID},
        ("revision", "contract_sha256", "assessment", "contract_review_execution")))},
    ("question", "scope", "expected", "progress_criteria", "completion_obligations", "revision"))
RECORDS["execution_profiles"] = record({"revision": NAT, "sha256": HASH,
    "role": TEXT, "actor_kind": enum("ai", "machine"),
    "boundary": obj({"mode": TEXT, "os_isolation": BOOL, "authenticated_caller": BOOL, "rules": array(TEXT)},
                    ("mode", "os_isolation", "authenticated_caller", "rules")),
    "host_capacity_refs": REFS, "host_capacity_status": TEXT,
    "observation": obj({"mode": enum(*_OBSERVATION_MODES),
        "settings": obj({key: NAT for key in _OBSERVATION_KEYS}),
        "rule_bindings": array(obj({"source": TEXT, "operator": TEXT, "subject_kind": TEXT, "unit": TEXT},
                                   ("source", "operator", "subject_kind", "unit")))},
        ("mode", "settings", "rule_bindings")),
    "window": obj({key: NAT for key in _WINDOW_KEYS}),
    "input": obj({"max_input_bytes": NAT, "unit": enum("utf8_bytes"), "provider_context_capacity": enum("unknown")},
                 ("max_input_bytes", "unit", "provider_context_capacity")),
    "required_capabilities": array(TEXT),
    "capability_evidence_refs": REFS,
    "ai": obj({"model": TEXT, "tier": nullable(TEXT), "provider": enum("codex", "claude"),
        "effort": TEXT, "capacity_refs": REFS, "provider_operations": TEXT,
        "remote_termination": TEXT, "maximum_output_enforced": BOOL, "claude_only_assigned_model": BOOL,
        "scholarly_server": nullable(EVIDENCE)}, ("model", "tier", "provider", "effort", "capacity_refs")),
    "host_resources": obj({"constraint_id": ID, "scope": enum("instance_on_host"), "host_id": TEXT,
        "demands": _HOST_AMOUNTS}, ("constraint_id", "scope", "host_id", "demands")),
    "machine": obj({"lean_command": nullable(array(TEXT))}, ("lean_command",))},
    ("revision", "sha256", "role", "actor_kind", "boundary", "observation", "window", "input"))
RECORDS["capacity_constraints"] = record({"kind": enum("concurrency", "host"),
    "model": TEXT, "accounting_unit": TEXT, "work_slots": NAT,
    "scope": TEXT, "max_jobs": NAT, "memory_bytes": NAT, "cpu_rate_basis_points": NAT,
    "host_id": TEXT, "control_reserve": _HOST_AMOUNTS,
    "authority_refs": REFS}, ("kind",))
RECORDS["reservations"] = record({"constraint_id": ID, "unit": TEXT,
    "authority_refs": array({"type": ["string", "object"]}), "owner_kind": enum("execution"),
    "owner_id": ID, "purpose": enum("normal"),
    "reserved": NAT, "confirmed_consumed": NAT, "returned": NAT, "state": enum("held", "settled"),
    "evidence_refs": array({"type": ["string", "object"]}), "reconcile_owner": TEXT, "reobserve": EVIDENCE},
    ("constraint_id", "unit", "owner_kind", "owner_id", "reserved", "confirmed_consumed", "returned", "state"))
RECORDS["capability_evidence"] = record({"execution_profile_ref": PROFILE_REF, "identity": EVIDENCE,
    "observed_at": TEXT, "capabilities": EVIDENCE, "version_sha256": nullable(HASH),
    "help_sha256": nullable(HASH), "boundary": TEXT}, ("execution_profile_ref", "identity", "observed_at", "capabilities"))
RECORDS["grants"] = record({"kind": enum("local", "http"), "status": enum(*sorted(_GRANT_STATUSES)),
    "roles": array(TEXT), "task_ids": REFS,
    "expires_at": nullable(TEXT), "valid_from": nullable(TEXT), "created_at": TEXT, "source_ref": TEXT,
    "decision_id": ID, "revoked_at": TEXT, "revoked_by": ID,
    "allowed_origins": array(TEXT), "allowed_methods": array(TEXT), "allowed_path_prefixes": array(TEXT),
    "credential_env": {"type": "object", "additionalProperties": TEXT},
    "included_targets": REFS, "excluded_targets": REFS, "reuse": TEXT, "initialization_only": BOOL,
    "replaced_by": ID, "academic_only": BOOL, "requires_academic": BOOL,
    "excluded_origins": array(TEXT, True), "excluded_path_prefixes": array(TEXT, True),
    **{key: array(TEXT, True) for key in ("execution_kinds", "purposes", "subjects")}}, ("kind", "status", "source_ref"))
# Initialization approval and later user decisions are two explicit variants.
RECORDS["decisions"] = {**record({"kind": TEXT, "change": EVIDENCE, "source_ref": TEXT, "actor": {"const": "user"},
    "created_at": TEXT, "affected": REFS,
    "grant_id": ID, "delegation_id": ID,
    "source_sha256": HASH, "record_hashes": mapping(HASH),
    "coverage": HISTORY, "intent_check": EVIDENCE,
    "input_source_ref": ID, "input_source_sha256": HASH,
    "author_execution_ids": REFS}, ("source_ref", "actor")),
    "anyOf": [{"required": ["record_hashes", "source_sha256"]}, {"required": ["kind", "change"]}]}
RECORDS["delegations"] = record({"status": enum("active", "revoked", "withdrawn"), "decision_kind": TEXT,
    "original_decision_id": ID, "included_targets": REFS, "excluded_targets": REFS, "external_effects": array(TEXT),
    "expires_at": nullable(TEXT), "source_ref": TEXT, "decision_id": ID, "created_at": TEXT,
    "resource_limits": mapping(NAT), "revoked_at": TEXT, "revoked_by": ID},
    ("status", "decision_kind", "original_decision_id", "included_targets", "excluded_targets", "external_effects", "expires_at"))
RECORDS["question_links"] = record({"origin_execution_id": nullable(ID), "origin_field": TEXT,
    "owner": enum(*sorted(_QUESTION_OWNERS)),
    "target_ids": REFS, "status": enum("open", "resolved", "superseded"), "resolution_ref": nullable(ID),
    "source_ref": TEXT, "routing_reason": TEXT,
    "unresolved_target_ids": REFS, "blocks": BOOL,
    "checked_by": nullable(ID), "resolution_history": HISTORY, "source_kind": TEXT, "source_id": ID,
    "question_kind": enum("grant")},
    ("origin_execution_id", "origin_field", "owner", "target_ids", "status", "resolution_ref", "unresolved_target_ids"))
RECORDS["external_operations"] = record({"request": obj({"method": TEXT, "url": TEXT, "body": TEXT}, ("method", "url", "body")),
    "request_sha256": HASH, "grant_id": ID, "source_ref": TEXT, "status": enum(*sorted(_OPERATION_STATUSES)),
    "idempotency_key": HASH, "attempts": HISTORY, "credential_env": nullable(array(TEXT)), "transmitted": BOOL,
    "transmission_phase": TEXT, "retry_authorized": BOOL, "succeeded": nullable(BOOL), "effect_absent": nullable(BOOL),
    "http_status": NAT, "body_base64": TEXT, "body_sha256": HASH, "error": TEXT, "waiting_reason": EVIDENCE,
    "reconciliation": EVIDENCE, "cancellation": EVIDENCE, "academic_effect_id": ID, "academic_basis": EVIDENCE,
    "target_id": ID, "purpose": TEXT, "subject": TEXT,
    "producer_executions": REFS, "actor_kind": enum("ai", "machine"),
    "execution_id": ID, "continuation_of": nullable(ID), "retried_from": TEXT, "history": HISTORY,
    "handling": enum("reconciliation_required", "reconciled"), "external_id": nullable(TEXT),
    "previous_outcome": enum("unknown", "failed"),
    "retry_evidence": obj({"kind": enum("effect_absent", "verified_idempotency"),
        "request_sha256": HASH, "idempotency_key": HASH, "evidence_ref": TEXT,
        "valid_until": TEXT, "source": enum("user", "adapter")},
        ("kind", "request_sha256", "idempotency_key", "evidence_ref", "source")),
    "academic_binding": obj({"task_id": ID, "requirement_id": TEXT, "effect_id": TEXT,
        "solution_basis": _SOLUTION_BASIS, "requirements_sha256": HASH},
        ("task_id", "requirement_id", "effect_id", "solution_basis", "requirements_sha256"))},
    ("request", "request_sha256", "grant_id", "source_ref", "status", "idempotency_key", "attempts"))
RECORDS["observation_facts"] = {**record({"kind": TEXT, "execution_id": ID, "event": EVIDENCE,
    "observed_at": TEXT,
    "elapsed_ms": NAT, "event_json": TEXT, "event_sha256": HASH, "monotonic_offset_ms": NAT,
    "source": obj({'stream': {'const': 'stdout.jsonl'}, 'start_offset': NAT, 'end_offset': NAT,
                   'received_at': TEXT, 'received_offset_ms': NAT},
                  ('stream', 'start_offset', 'end_offset', 'received_at', 'received_offset_ms'))},
    ("kind", "execution_id", "observed_at")),
    "oneOf": [{"required": ["event"]}, {"required": ["event_json", "event_sha256", "monotonic_offset_ms"]}]}
RECORDS["self_check_obligations"] = record({"kind": TEXT, "execution_id": ID, "rule_revision": NAT,
    "due": HISTORY, "opened_at": TEXT, "status": enum("open", "answered", "closed"),
    "response_ref": TEXT, "opened_offset_ms": NAT, "deadline_offset_ms": nullable(NAT),
    "observed_at": TEXT, "rules_sha256": HASH, "snapshot": EVIDENCE,
    "consumed_boundaries": mapping(NAT),
    "missed_reason": TEXT, "deadline_held_offset_ms": NAT,
    "delivered_source_offset": NAT, "delivered_at": TEXT, 'delivered_request_sha256': HASH,
    'acknowledged_source_offset': NAT, 'acknowledged_call_id': TEXT},
    ("kind", "execution_id", "rule_revision", "due", "opened_offset_ms", "deadline_offset_ms", "status", "observed_at"))
# The outcome of a response's rule_proposal (observations.ObservationTracker._replace_rules).
_RULE_UPDATE = obj({"kind": enum("observation_rules_accepted", "observation_rules_unchanged", "observation_rules_rejected"),
    "previous_rules_sha256": HASH, "rules": array(_RULE), "reason": TEXT, "previous_rules_preserved": BOOL,
    "execution_id": ID, "active_revision": NAT, "active_rules_sha256": HASH, "observed_at": TEXT,
    "worker_feedback": obj({"kind": TEXT, "reason": TEXT, "previous_rules_sha256": HASH,
        "previous_rules_preserved": BOOL, "execution_id": ID, "active_revision": NAT, "active_rules_sha256": HASH},
        ("kind", "execution_id", "active_revision", "active_rules_sha256"))},
    ("kind", "execution_id", "active_revision", "active_rules_sha256", "observed_at", "worker_feedback"))
RECORDS["self_check_responses"] = record({"kind": TEXT, "execution_id": ID, "obligation_id": nullable(TEXT),
    "response": nullable(EVIDENCE), "observed_at": TEXT, "reason": TEXT,
    "receipt_ref": nullable(TEXT),
    "response_json": TEXT, "received_offset_ms": NAT, "errors": array(TEXT),
    "followup": obj({"kind": TEXT, "next_owner": TEXT, "trigger": TEXT, "basis_refs": array(TEXT)}, ("kind", "next_owner")),
    "worker_feedback": obj({"kind": TEXT, "errors": array(TEXT), "obligation_id": nullable(TEXT), "next_owner": TEXT}),
    "next_self_check_offset_ms": nullable(NAT), "no_progress_count": NAT, "rule_update": _RULE_UPDATE},
    ("kind", "execution_id", "obligation_id", "observed_at", "response_json", "received_offset_ms"))
RECORDS["operational_dispositions"] = record({"execution_id": ID, "disposition": EVIDENCE,
    "created_at": TEXT, "status": TEXT, "target_execution_id": ID,
    "obligation_ids": REFS, "applied_at": TEXT, "result": EVIDENCE, "error": TEXT,
    "question_id": ID}, ("execution_id", "disposition"))
RECORDS["control_receipts"] = record({"request_id": ID, "execution_id": ID, "kind": TEXT, "state": TEXT,
    "payload": EVIDENCE, "received_at": TEXT, "grant_id": ID, "reason": TEXT,
    "request_sha256": HASH, "snapshot": TEXT, "publication_id": ID, "payload_sha256": HASH,
    "transport_id": TEXT, "request": EVIDENCE, "parent_snapshot": TEXT}, ("execution_id", "kind", "state"))
# trust_validation owns the environment record shape and its runtime binding.
RECORDS["trust_environments"] = record(_ENVIRONMENT_PROPERTIES, _ENVIRONMENT_REQUIRED)
_REVIEW_BINDING = obj({"role_slot_id": TEXT, "profile_ref": nullable(PROFILE_REF), "input_sha256": nullable(HASH),
    "input_snapshot": TEXT, "proposal_digest": HASH, "restored_messages": HISTORY,
    "request": EVIDENCE, "visible_execution_ids": REFS, "delegation_authority": EVIDENCE},
    ("role_slot_id", "profile_ref", "input_sha256", "input_snapshot", "proposal_digest", "restored_messages", "request", "visible_execution_ids"))
RECORDS["review_cycles"] = record({
    **{k: EVIDENCE for k in ("proposal", "review_policy", "execution_accounting", "results", "turns", "transcript_manifest", "issues", "findings", "deferred_actions", "research")},
    **{k: HISTORY for k in ("history", "previous_reviews", "followup", "recovery_events")},
    **{k: array(TEXT) for k in ("reviewer_slots", "requested_reviewer_slots", "retained_reviewer_slots", "judge_slots", "required_source_refs", "sealed")},
    **{k: NAT for k in ("revision", "max_rounds", "round", "activity_execution_limit")},
    "proposal_digest": HASH, "review_lineage_id": TEXT, "scope_assessment": nullable(EVIDENCE),
    "owner_activity_id": nullable(ID), "phase": TEXT, "status": enum(*sorted(_CYCLE_STATUSES)), "decision": nullable(TEXT),
    "knowledge_id": ID, "producer_execution": ID,
    "input_snapshot": TEXT, "producer_execution_ids": REFS,
    "transition_id": ID, "staged_candidate": obj({"proposal": EVIDENCE,
        "identity_basis": _IDENTITY_BASIS,
        "transition_basis": HASH, "target_environment": RECORDS["trust_environments"]},
        ("proposal", "identity_basis", "transition_basis", "target_environment")),
    "identity_basis": _IDENTITY_BASIS,
    "policy_ref": TEXT, "publication_premises": EVIDENCE, "review_input_basis": EVIDENCE,
    "slot_profiles": mapping(nullable(PROFILE_REF)), "input_bindings": mapping(_REVIEW_BINDING),
    "assessment_id": ID, "assessment_use_ids": REFS, "continuity_events": HISTORY,
    "blocked_actions": mapping(NAT), "replacement_actions": mapping(obj({"action": EVIDENCE,
        "recovery_event": NAT, "grant_id": ID, "grant_sha256": HASH, "authority_request": _ACTION,
        "authority": EVIDENCE, "delegation_id": nullable(ID), "case": nullable(EVIDENCE),
        "sealed_input_sha256": HASH, "omitted_indices": array(NAT)},
        ("action", "recovery_event", "grant_id", "grant_sha256", "authority_request", "authority", "delegation_id", "case", "sealed_input_sha256", "omitted_indices"))),
    "replacement_receipts": HISTORY, "transcript_replacements": HISTORY,
    "pending_findings": array(TEXT, True), "answer_requests": array(TEXT, True)},
    ("proposal", "proposal_digest", "revision", "phase", "status"))
RECORDS["goal_judgments"] = record({"execution_id": ID, "basis": TEXT, "decision": TEXT, "scope_complete": BOOL,
    "summary": TEXT, "findings": array(TEXT), "used_sources": array(TEXT), "questions": array(TEXT),
    "slot": {"type": ["integer", "string"]}, "required": NAT, "created_at": TEXT, "input_basis": EVIDENCE,
    "additional_audits": array(_AUDIT_RESULT),
    "formal_result_refs": REFS, "assessment_refs": REFS, "dependencies": REFS,
    "record_basis": array(obj({"id": ID, "sha256": HASH, "status": TEXT}, ("id", "sha256", "status"))),
    "basis_is_conservative": BOOL, "reason": TEXT, "goal_revision": NAT, "goal_basis_sha256": HASH,
    "policy_revision": HASH, "source_basis": HISTORY, "use_history": HISTORY, "current": BOOL,
    "invalidated_reason": TEXT},
    ("execution_id", "decision", "basis"))
RECORDS["conversations"] = record({"generation": {"type": "integer", "minimum": 1},
    "status": enum("connected", "lost"), "lease_seconds": {"type": "integer", "minimum": 1},
    "disconnect_policy": enum("pause", "continue_authorized"), "attached_at": TEXT, "last_heartbeat_at": TEXT,
    "lease_expires_at": TEXT, "source_ref": TEXT, "lost_at": TEXT, "loss_reason": TEXT},
    ("generation", "status", "lease_seconds", "disconnect_policy", "attached_at", "last_heartbeat_at", "lease_expires_at", "source_ref"))
RECORDS["trust_transitions"] = record({"from_environment": nullable(ID), "to_environment": ID,
    "targets": array(obj({"id": ID, "formal_result_id": ID, "exposition_id": ID, "source_sha256": HASH, "basis": EVIDENCE,
        "formal_basis": HASH, "exposition_basis": HASH, "declaration_evidence": nullable(EVIDENCE),
        "dependency_closure": nullable(mapping(array(TEXT))), "dependency_evidence": nullable(mapping(HASH)),
        "axioms": nullable(mapping(array(TEXT))), "previous_environment_ids": array(nullable(ID))},
        ("id", "formal_result_id", "exposition_id", "source_sha256", "basis", "formal_basis", "exposition_basis"))),
    "results": mapping(EVIDENCE), "status": enum("checking", "ready", "active", "activated", "failed", "withdrawn"),
    "source_ref": TEXT, "created_at": TEXT, "activated_at": TEXT, "history": HISTORY}, ("from_environment", "to_environment", "targets", "results", "status"))
# A rejection is immutable once received; its resolution lives in academic_resolution_records.
RECORDS["external_rejections"] = record({"actor": TEXT, "text": TEXT, "source_ref": TEXT,
    "created_at": TEXT, "solution_basis": _SOLUTION_BASIS}, ("actor", "text", "source_ref", "solution_basis"))
RECORDS["academic_resolution_records"] = record({"rejection_id": ID, "rejection_sha256": HASH,
    "solution_basis": _SOLUTION_BASIS, "requirements_sha256": nullable(HASH), "execution_id": ID,
    "decision": enum("resolved", "unresolved"), "evidence": TEXT, "evidence_refs": array(TEXT, True),
    "evidence_hashes": mapping(HASH), "sha256": HASH},
    ("rejection_id", "rejection_sha256", "solution_basis", "requirements_sha256", "execution_id", "decision", "evidence", "evidence_refs", "evidence_hashes", "sha256"))
RECORDS["intent_imports"] = record({"source": RECORDS["governance_sources"],
    "output": _interpretation_schema("interpret"), "execution_id": ID,
    "basis_sha256": HASH, "sha256": HASH,
    "previous_id": nullable(ID), "previous_findings": HISTORY, "status": TEXT,
    "superseded_by": ID, "check": EVIDENCE, "application": EVIDENCE, "owner_basis": mapping(EVIDENCE), "input_ref": ID},
    ("source", "output", "execution_id", "basis_sha256", "sha256", "previous_id", "previous_findings", "status",
     "input_ref"))
RECORDS["recoveries"] = record({"started_at": TEXT, "execution_ids": REFS,
    "dispositions": array(obj({"execution_id": ID, "fact": TEXT, "next_owner": TEXT,
        "local_termination_confirmed": BOOL, "remote_termination": enum("unknown"),
        "disposition": TEXT, "reason": TEXT}, ("execution_id",))),
    "finished_at": TEXT}, ("started_at", "execution_ids", "dispositions"))
RECORDS["provider_waits"] = record({"provider": enum("codex", "claude"), "generation": NAT,
    "state": enum("waiting", "checking", "available"), "retry_at": nullable(NAT), "attempts": NAT,
    "probe_owner": nullable(ID), "probe_started_at": nullable(NAT),
    "evidence": obj({"execution_id": ID, "kind": TEXT, "provider": TEXT,
        "evidence_ref": nullable(TEXT), "reported_fields_json": TEXT}, ("execution_id", "kind", "provider", "reported_fields_json"))},
    ("provider", "generation", "state", "retry_at", "attempts", "probe_owner", "probe_started_at", "evidence"))
RECORDS["delegation_applications"] = record({"delegation_id": ID,
    "basis": obj({"delegation": RECORDS["delegations"], "original_decision": RECORDS["decisions"],
        "approval": RECORDS["decisions"], "source": RECORDS["governance_sources"],
        "original_source": RECORDS["governance_sources"], "target": EVIDENCE, "references": mapping(EVIDENCE),
        "case": obj({"id": ID, "decision_kind": TEXT, "target_id": ID, "external_effects": array(TEXT),
            "resources": mapping(NAT), "effect": EVIDENCE, "basis_refs": array({"oneOf": [ID, obj({"id": ID}, ("id",))]})},
            ("id", "decision_kind", "target_id", "external_effects", "resources", "effect"))},
        ("delegation", "original_decision", "approval", "source", "original_source", "case", "target", "references")),
    "input_sha256": HASH, "judgments": obj({stage: obj({"execution_id": ID, "sha256": HASH,
        "output": obj({"input_sha256": HASH, "decision": enum("within_scope", "outside_scope", "unresolved"), "reason": TEXT},
                      ("input_sha256", "decision", "reason"))}, ("execution_id", "sha256", "output")) for stage in ("interpret", "check")}),
    "application": obj({"status": enum("applied"), "application_id": ID, "input_sha256": HASH,
        "original_decision_id": ID, "effect": EVIDENCE, "post_basis_sha256": HASH, "sha256": HASH},
        ("status", "application_id", "input_sha256", "original_decision_id", "effect", "post_basis_sha256", "sha256"))},
    ("delegation_id", "basis", "input_sha256", "judgments"))
RECORDS["inputs"] = record({"instance_id": ID, "action": TEXT, "text": TEXT, "config": EVIDENCE,
    "created_at": TEXT, "origin": TEXT, "accepted_order": TEXT, "sha256": HASH}, ("text", "config"))
RECORDS["queue"] = _ACTION

# Scalar and singleton state are enumerated explicitly; unknown top-level keys
# never acquire a storage location based on their run-time Python shape.
RESEARCH_FIELDS = {
    "id": ID,
    "object_format": enum("sha1", "sha256"), "title": TEXT,
    "workspace": TEXT, "created_at": TEXT, "goal_status": TEXT,
    "active_trust_environment": nullable(ID),
    "conversation_loss_policy": TEXT, "governance_approval": {"type": ["boolean", "object"]},
    "goal_assessment_basis": TEXT,
    # Each role that builds profiles (execution_profiles.PROFILE_ROLES) selects its stored editions.
    "role_profile_refs": obj({role: {**array(PROFILE_REF, True), "minItems": 1} for role in sorted(_PROFILE_ROLES)}),
    "lifecycle": obj({"state": enum("initializing", "active", "paused"),
        "immutable_input": obj({"text": TEXT, "sha256": HASH, "bytes": NAT},
        ("text", "sha256", "bytes")),
        "required_capabilities": array(TEXT),
        "activation": obj({"completed": array(TEXT), "missing": array(TEXT), "observation_errors": HISTORY}),
        "permanently_closed": BOOL, "history": HISTORY,
        "adoption": obj({"governance_sha256": HASH, "config_sha256": HASH, "review_policy_sha256": HASH,
            "external_policy": {"type": ["string", "object"]},
            "initial_profile_ref": PROFILE_REF, "research_grant_ids": REFS, "initial_grant_ids": REFS, "source_refs": array(TEXT)}),
        "intent_check": obj({"input_sha256": HASH, "interpretation_execution_id": ID, "check_execution_id": ID},
                            ("input_sha256", "interpretation_execution_id", "check_execution_id")),
        "input_id": ID, "activated_at": TEXT}, ("state", "immutable_input", "input_id")),
    "review_policy": obj({"id": ID,
        "required_perspectives": array(TEXT, True), "minimum_initial_slots": NAT, "judge_slots": array(TEXT, True),
        "round_limit": NAT, "activity_execution_limit": NAT, "overflow_disposition": enum("unresolved", "defer")},
        ("id", "required_perspectives", "minimum_initial_slots", "judge_slots", "round_limit", "activity_execution_limit", "overflow_disposition")),
    "host_capacity_ref": ID,
}
_CHECKPOINT = obj({"kind": TEXT, "status": TEXT, "checkpoint": _CHECKPOINT_SCHEMA, "value": _CHECKPOINT_SCHEMA,
    "sha256": HASH, "artifact_ref": TEXT, "execution_id": ID, "observed_at": TEXT,
    "checkpoint_status": TEXT, "messages": HISTORY, "workspace": TEXT, "limitation": TEXT,
    "reason": TEXT, "source": TEXT, "recovered": BOOL, "path": TEXT, "bytes": NAT,
    "observation_sources": array(obj({"artifact_ref": TEXT,
        "sha256": HASH, "bytes": NAT, "path": TEXT}, ("artifact_ref", "sha256", "bytes", "path"))),
    "observation_evidence_complete": BOOL,
    "observation_evidence_omitted": array(obj({"path": TEXT, "reason": TEXT, "required": BOOL,
        "error": TEXT, "error_type": TEXT, "bytes": NAT}, ("path", "reason"))),
    'evidence_files': array(obj({'path': TEXT, 'artifact_ref': TEXT, 'sha256': HASH, 'bytes': NAT},
                               ('path', 'artifact_ref', 'sha256', 'bytes'))),
    'evidence_omitted': array(obj({'path': TEXT, 'reason': TEXT}, ('path', 'reason')))})
_CHECKPOINT["properties"]["final_observation"] = _deepcopy(_CHECKPOINT)
_SUPPLIED_SOURCE = _deepcopy(RECORDS['sources'])
_SUPPLIED_SOURCE['properties']['local_path'] = TEXT
_OBSERVATION = obj({"kind": TEXT, "execution_id": ID, "observed_at": TEXT,
    "trigger": TEXT, "call_id": TEXT, "review_id": nullable(TEXT), "reason": nullable(TEXT),
    "basis_ref": nullable(TEXT), "basis": EVIDENCE, "observation_refs": REFS,
    "obligation_ids": REFS, "obligation_id": nullable(ID), "rule_ids": array(_RULE_ID_SCHEMA, True),
    "interval_ms": NAT, "review_window_ms": NAT, "window_ms": NAT, "at": TEXT,
    "followup": nullable(obj({"kind": TEXT, "trigger": TEXT, "next_owner": TEXT,
                              "basis_refs": REFS}, ("kind", "next_owner"))),
    "elapsed_ms": NAT, "next_owner": TEXT, "checkpoint_status": TEXT,
    "proposal_sha256": nullable(HASH), "previous_rules_sha256": HASH, "active_rules_sha256": HASH,
    "active_revision": NAT, "rules": array(_RULE), "rule_revision": NAT,
    "evidence_refs": array(TEXT)}, ("kind", "execution_id", "observed_at"))
RUNTIME_FIELDS = {"status": enum("initializing", "ready", "running", "paused", "waiting", "capacity_waiting",
                                  "completed", "closed"),
    "cycles": NAT, "updated_at": TEXT,
    "processed_controls": REFS, "questions": array(TEXT), "history": HISTORY,
    "recovery_checked": BOOL, "last_observed_utc": TEXT, "event_cursor": NAT,
    "availability": obj({"state": TEXT, "reason": TEXT, "next_owner": TEXT}, ("state",)),
    "clock_guard": obj({"state": TEXT, "observed_at": TEXT, "reason": TEXT,
        "usable": BOOL, "observed_utc": TEXT, "last_observed_utc": TEXT, "expected_at_least": TEXT}),
    "pending_events": REFS,
    "user_pause": {"type": ["boolean", "object"]}, "stop_requested": {"type": ["boolean", "string"]},
    "next_research_reconsider_at": nullable(TEXT),
    "model_policy_violation": EVIDENCE, "provider_wake": EVIDENCE,
    # Per trust environment: the toolchain-record baseline whose fingerprint was last accepted.
    "trust_bindings": mapping(_BINDING_SCHEMA),
    # These assessments have no producer ID. Their enclosing list is one typed
    # singleton until GOVERNANCE introduces independent assessment identities.
    "academic_assessments": array(obj({"requirement_id": TEXT, "solution_basis": _SOLUTION_BASIS, "requirements_sha256": HASH,
        "decision": enum("satisfied", "not_satisfied", "unresolved"), "evidence": array(obj({"criterion": TEXT, "satisfied": BOOL, "evidence": TEXT}, ("criterion", "satisfied", "evidence"))),
        "assessor": enum("research_plan"), "execution_id": ID, "task_id": ID, "external_effect_receipts": HISTORY,
        "task_assessment_sha256": HASH},
        ("requirement_id", "solution_basis", "requirements_sha256", "decision", "evidence", "assessor", "execution_id", "task_id"))),
    # Existing-ID keyed operational views: no duplicate record ID is manufactured.
    "checkpoints": mapping(_CHECKPOINT),
    "maintenance_fence": obj({'request_id':ID, 'origin':enum('user','operator'), 'reason':TEXT,
        'state':enum('draining','blocked','quiescent'), 'created_at':TEXT,
        'pending_executions':REFS,'held_reservations':REFS,'settled_at':TEXT},
        ('request_id','origin','reason','state','created_at')),
    "lost_conversation_generations": mapping(NAT), "resume_lifecycle": TEXT,
    "extended_controls": mapping(obj({"action": TEXT, "source_ref": TEXT, "status": TEXT,
        "request": EVIDENCE, "result": EVIDENCE, "processed_at": TEXT})),
    "review_inputs": mapping(obj({"proposal_digest": HASH, "proposal": EVIDENCE, "request": EVIDENCE,
        "slot": TEXT, "visible_execution_ids": REFS, "workspace": TEXT, "supplied_sources": array(_SUPPLIED_SOURCE),
        "source_snapshot": TEXT, "restored_messages": HISTORY},
        ("proposal_digest", "proposal", "request", "slot", "visible_execution_ids", "workspace", "supplied_sources", "source_snapshot"))),
    "waiting_actions": mapping(obj({"action": _ACTION, "reason": nullable(TEXT), "kind": TEXT,
        "execution_id": ID, "detail": EVIDENCE, "condition": EVIDENCE, "next_owner": TEXT,
        "waiting_reason": EVIDENCE,
        "question_id": ID,
        'diagnosis': obj({'execution_id': ID, 'decision': enum('retry', 'wait'), 'guidance': TEXT, 'retry_error': TEXT},
                         ('execution_id', 'decision', 'guidance')),
        "failure_kind": nullable(TEXT), "input_snapshot": TEXT,
        "changes": HISTORY, "import_id": ID, "question": TEXT, "owner": TEXT, "release_condition": TEXT,
        "observation_errors": HISTORY, "observation_rule_deferrals": HISTORY, "rule_input_version": EVIDENCE,
        "review_requests": mapping(_IMPACT_REQUEST), "review_execution_ids": mapping(ID),
        "delegated_targets": mapping(ID),
        "deferrals": mapping(obj({"execution_id": ID, "reason": TEXT}, ("execution_id", "reason"))),
        "delegation_history": array(_RECORD_TASK),
        "input_version": obj({"goal": NAT, "policy": {"type": ["integer", "string"]},
            "sources": array(obj({"name": TEXT, "sha256": HASH}, ("name", "sha256"))), "inputs": REFS},
            ("goal", "policy", "sources", "inputs")),
        "recovery": obj({"disposition": TEXT, "authority": EVIDENCE, "action": EVIDENCE, "review_cycle_id": ID,
            "next_owner": TEXT, "review_closure": TEXT, "recovery_event": EVIDENCE, "reason": TEXT,
            "event": EVIDENCE, "cycle": EVIDENCE, "retryable": BOOL,
            "owner_activity_id": nullable(ID), "review_status": TEXT})}, ("action", "reason"))),
    "private_insights": mapping(HISTORY),
    "task_observation_rules": mapping(array(_RULE)),
    "observations": mapping(_OBSERVATION),
    "pending_kind_checks": array(obj({"family": enum("knowledge", "relation"),
        "token": TEXT, "definition_id": ID, "source_ref": TEXT, "actor_ref": TEXT,
        "execution_id": ID}, ("family", "token"))),
    "revision_cycles": array(array(ID)),
    "input_overflows": array(obj({"action": _ACTION, "detail": _OVERFLOW,
        "source_catalog": EVIDENCE}, ("action", "detail", "source_catalog"))),
}
