"""Additional installed producers and typed, non-record lookup containers.

Lookup keys are existing record identities, not newly allocated global IDs.
Their values have closed schemas; they are not a catch-all metadata family.
"""
from .schemas import *


def mapping(value):
    return {"type": "object", "additionalProperties": value}


def extend():
    requirement = obj({"id": TEXT, "scope": TEXT, "assessor": enum("research_plan"),
        "criteria": array(TEXT, True), "required_inputs": array(TEXT, True),
        "external_effects": array(obj({"id": TEXT, "scope": TEXT, "grant_id": nullable(ID)}, ("id", "scope")))},
        ("id", "scope", "assessor", "criteria"))
    content = obj({**{k: TEXT for k in ("rationale", "goal", "desired_result", "evidence_boundary", "decision_authority", "rule_id", "text", "assessor")},
        **{k: array(TEXT, True) for k in ("success_criteria", "partial_success_criteria", "included_scope", "excluded_scope", "priorities", "preferences", "stop_conditions", "scope", "reason_refs", "audit_refs", "required_inputs")},
        "academic_requirements": array(requirement), "verdict_mapping": mapping(enum("satisfied", "not_satisfied", "unresolved")),
        "terms": array(obj({"term": TEXT, "definition": TEXT, "boundary": TEXT, "avoid_synonyms": array(TEXT), "record_refs": REFS},
                           ("term", "definition", "boundary", "avoid_synonyms", "record_refs")))})
    RECORDS["governance"] = record({"kind": enum("charter", "policy", "research_context", "additional_audit"),
        "revision": {"type": "integer", "minimum": 1}, "supersedes": REFS, "content": content,
        "document": obj({"ref": TEXT, "sha256": HASH}, ("ref", "sha256")), "status": enum("active", "superseded"),
        "approval_ref": ID, "source_ref": ID, "content_sha256": HASH, "superseded_by": ID},
        ("kind", "revision", "supersedes", "content", "status", "approval_ref", "source_ref", "content_sha256"))
    RECORDS["governance_sources"] = record({"text": TEXT, "origin": TEXT, "revision": NAT, "sha256": HASH, "bytes": NAT},
        ("text", "origin", "revision", "sha256", "bytes"))
    # GOVERNANCE preserves the exact delivered audit and referenced record
    # snapshots. Semantic checks below bind those snapshots and mapped verdicts.
    audit_input = obj({"audit": RECORDS["governance"], "audit_sha256": HASH,
        "inputs": mapping(EVIDENCE), "input_hashes": mapping(HASH)},
        ("audit", "audit_sha256", "inputs", "input_hashes"))
    audit_result = obj({"audit_ref": ID, "audit_sha256": HASH, "assessor": TEXT, "verdict": TEXT,
        "decision": enum("satisfied", "not_satisfied", "unresolved"), "input_hashes": mapping(HASH),
        "execution_id": ID, "reason": {"type": "string", "minLength": 1}},
        ("audit_ref", "audit_sha256", "assessor", "verdict", "decision", "input_hashes", "execution_id", "reason"))
    RECORDS["executions"]["properties"]["additional_audit_input"] = array(audit_input)
    RECORDS["goal_judgments"]["properties"].update({"additional_audits": array(audit_result),
        "formal_result_refs": REFS, "assessment_refs": REFS, "dependencies": REFS,
        "record_basis": array(obj({"id": ID, "sha256": HASH, "status": TEXT}, ("id", "sha256", "status"))),
        "basis_is_conservative": BOOL, "reason": TEXT, "goal_revision": NAT,
        "policy_revision": HASH, "source_basis": HISTORY})
    # Initialization approval and later user decisions are two explicit variants.
    decisions = RECORDS["decisions"]
    decisions["properties"].update({"source_sha256": HASH, "record_hashes": mapping(HASH), "revoked": BOOL,
        "coverage": HISTORY, "intent_check_ref": ID, "intent_check": EVIDENCE})
    decisions["required"] = ["id", "source_ref", "actor"]
    decisions["anyOf"] = [{"required": ["record_hashes", "source_sha256"]}, {"required": ["kind", "change", "affected"]}]
    RECORDS["conversations"] = record({"generation": {"type": "integer", "minimum": 1},
        "status": enum("connected", "lost"), "lease_seconds": {"type": "integer", "minimum": 1},
        "disconnect_policy": enum("pause", "continue_authorized"), "attached_at": TEXT, "last_heartbeat_at": TEXT,
        "lease_expires_at": TEXT, "source_ref": TEXT, "lost_at": TEXT, "loss_reason": TEXT},
        ("generation", "status", "lease_seconds", "disconnect_policy", "attached_at", "last_heartbeat_at", "lease_expires_at", "source_ref"))
    RECORDS["trust_transitions"] = record({"from_environment": nullable(ID), "to_environment": ID,
        "targets": array(obj({"id": ID, "formal_result_id": ID, "exposition_id": ID, "source_sha256": HASH, "basis": EVIDENCE,
            "formal_basis": HASH, "exposition_basis": HASH, "declaration_evidence": nullable(EVIDENCE),
            "dependency_closure": nullable(mapping(array(TEXT))), "dependency_evidence": nullable(EVIDENCE),
            "axioms": nullable(mapping(array(TEXT))), "previous_environment_ids": array(nullable(ID))},
            ("id", "formal_result_id", "exposition_id", "source_sha256", "basis", "formal_basis", "exposition_basis"))),
        "results": mapping(EVIDENCE), "status": enum("checking", "ready", "active", "activated", "failed", "withdrawn"),
        "source_ref": TEXT, "created_at": TEXT, "activated_at": TEXT, "semantic_pending": REFS,
        "semantic_results": mapping(EVIDENCE), "history": HISTORY}, ("from_environment", "to_environment", "targets", "results", "status"))
    RECORDS["identity_assessments"]["properties"].update({"transition_id": ID, "transition_basis": HASH,
        "reviewed_identity_basis": EVIDENCE,
        "continuity_comparison": obj({"equivalent": BOOL, "missing": array(TEXT), "changed": array(TEXT),
            "requires_identity_review": BOOL}, ("equivalent", "missing", "changed", "requires_identity_review"))})
    RECORDS["formal_results"]["properties"]["transition_id"] = ID
    RECORDS["executions"]["properties"]["source_ref"] = TEXT
    basis = obj({"goal_ref": TEXT, "records": array(obj({"id": ID, "sha256": HASH}, ("id", "sha256")))}, ("goal_ref", "records"))
    RECORDS["external_rejections"] = record({"actor": TEXT, "text": TEXT, "source_ref": TEXT,
        "created_at": TEXT, "solution_basis": basis, "resolved": BOOL}, ("actor", "text", "source_ref", "solution_basis", "resolved"))
    RECORDS["academic_resolution_records"] = record({"rejection_id": ID, "rejection_sha256": HASH,
        "solution_basis": basis, "requirements_sha256": nullable(HASH), "execution_id": ID,
        "decision": enum("resolved", "unresolved"), "evidence": TEXT, "evidence_refs": array(TEXT, True),
        "evidence_hashes": mapping(HASH), "sha256": HASH},
        ("rejection_id", "rejection_sha256", "solution_basis", "requirements_sha256", "execution_id", "decision", "evidence", "evidence_refs", "evidence_hashes", "sha256"))
    academic_assessment = obj({"requirement_id": TEXT, "solution_basis": basis, "requirements_sha256": HASH,
        "decision": enum("satisfied", "not_satisfied", "unresolved"), "evidence": array(obj({"criterion": TEXT, "satisfied": BOOL, "evidence": TEXT}, ("criterion", "satisfied", "evidence"))),
        "assessor": enum("research_plan"), "execution_id": ID, "task_id": ID, "external_effect_receipts": HISTORY,
        "task_assessment_sha256": HASH},
        ("requirement_id", "solution_basis", "requirements_sha256", "decision", "evidence", "assessor", "execution_id", "task_id"))
    # These assessments have no producer ID. Their enclosing list is one typed
    # singleton until GOVERNANCE introduces independent assessment identities.
    RUNTIME_FIELDS["academic_assessments"] = array(academic_assessment)
    life = RESEARCH_FIELDS["lifecycle"]["properties"]
    life.update({"adoption": obj({"governance_sha256": HASH, "config_sha256": HASH, "review_policy_sha256": HASH,
        "external_policy": {"type": ["string", "object"]}, "profile_refs": array(PROFILE_REF),
        "initial_profile_ref": PROFILE_REF, "research_grant_ids": REFS, "initial_grant_ids": REFS, "source_refs": array(TEXT)}),
        "intent_check": obj({"input_sha256": HASH, "interpretation_execution_id": ID, "check_execution_id": ID},
                            ("input_sha256", "interpretation_execution_id", "check_execution_id")),
        "input_id": ID, "activated_at": TEXT, "closed_at": TEXT})
    RESEARCH_FIELDS["review_policy"] = obj({"id": ID, "version": {"const": STATE_FORMAT_VERSION},
        "required_perspectives": array(TEXT, True), "minimum_initial_slots": NAT, "judge_slots": array(TEXT, True),
        "round_limit": NAT, "activity_execution_limit": NAT, "overflow_disposition": enum("unresolved", "defer")},
        ("id", "version", "required_perspectives", "minimum_initial_slots", "judge_slots", "round_limit", "activity_execution_limit", "overflow_disposition"))
    from ..observations import CHECKPOINT_SCHEMA
    checkpoint = obj({"kind": TEXT, "status": TEXT, "checkpoint": CHECKPOINT_SCHEMA, "value": CHECKPOINT_SCHEMA,
        "sha256": HASH, "artifact_ref": TEXT, "execution_id": ID, "observed_at": TEXT,
        "checkpoint_status": TEXT, "messages": HISTORY, "workspace": TEXT, "limitation": TEXT,
        "reason": TEXT, "source": TEXT, "recovered": BOOL, "path": TEXT, "bytes": NAT})
    checkpoint["properties"].update({"observation_sources": array(obj({"artifact_ref": TEXT,
        "sha256": HASH, "bytes": NAT, "path": TEXT}, ("artifact_ref", "sha256", "bytes", "path"))),
        "observation_evidence_complete": BOOL,
        "observation_evidence_omitted": array(obj({"path": TEXT, "reason": TEXT, "required": BOOL,
            "error": TEXT, "error_type": TEXT, "bytes": NAT}, ("path", "reason")))})
    checkpoint['properties'].update({
        'evidence_files': array(obj({'path': TEXT, 'artifact_ref': TEXT, 'sha256': HASH, 'bytes': NAT},
                                   ('path', 'artifact_ref', 'sha256', 'bytes'))),
        'evidence_omitted': array(obj({'path': TEXT, 'reason': TEXT}, ('path', 'reason')))})
    from copy import deepcopy
    checkpoint["properties"]["final_observation"] = deepcopy(checkpoint)
    supplied_source = deepcopy(RECORDS['sources'])
    supplied_source['properties']['local_path'] = TEXT
    # Existing-ID keyed operational views: no duplicate record ID is manufactured.
    RUNTIME_FIELDS.update({"checkpoints": mapping(checkpoint),
        "maintenance_fence": obj({'request_id':ID, 'origin':enum('user','operator'), 'reason':TEXT,
            'state':enum('draining','blocked','quiescent'), 'created_at':TEXT,
            'pending_executions':REFS,'held_reservations':REFS,'settled_at':TEXT},
            ('request_id','origin','reason','state','created_at')),
        "condition_states": mapping(enum("ready", "not_ready", "evaluation_error")),
        "lost_conversation_generations": mapping(NAT), "resume_lifecycle": TEXT,
        "extended_controls": mapping(obj({"action": TEXT, "source_ref": TEXT, "status": TEXT,
            "request": EVIDENCE, "result": EVIDENCE, "processed_at": TEXT})),
        "review_inputs": mapping(obj({"proposal_digest": HASH, "proposal": EVIDENCE, "request": EVIDENCE,
            "slot": TEXT, "visible_execution_ids": REFS, "workspace": TEXT, "supplied_sources": array(supplied_source),
            "source_snapshot": TEXT}, ("proposal_digest", "proposal", "request", "slot", "visible_execution_ids", "workspace", "supplied_sources", "source_snapshot"))),
        "waiting_actions": mapping(obj({"action": EVIDENCE, "reason": TEXT, "kind": TEXT,
            "execution_id": ID, "detail": EVIDENCE, "condition": EVIDENCE, "next_owner": TEXT,
            "retry_at": TEXT, "waiting_reason": EVIDENCE, "waiting_since": TEXT}, ("action", "reason"))),
        "private_insights": mapping(HISTORY)})
    RUNTIME_FIELDS["clock_guard"]["properties"].update({"usable": BOOL, "observed_utc": TEXT,
        "last_observed_utc": TEXT, "expected_at_least": TEXT})
    RUNTIME_FIELDS["waiting_actions"]["additionalProperties"]["properties"]["question_id"] = ID
    event = RECORDS["events"]["properties"]
    event.update({"opened_at": TEXT, "target": nullable(TEXT), "source_ref": nullable(TEXT),
        "generation": NAT, "previous_status": TEXT, "status": TEXT, "request_id": TEXT,
        "decision_id": ID, "affected_ids": REFS, "transition_id": ID, "environment_id": ID,
        "execution_ids": REFS, "task_ids": REFS, "revision": NAT, "detail": TEXT})
    RECORDS["tasks"]["properties"].update({"initial_observation_rules": HISTORY,
        "newinput": {"anyOf": [BOOL, ID]}, "wake_at": TEXT, "due_conditions": HISTORY, "solution_basis": basis,
        "requirements_sha256": HASH, "governance_revision_required": obj({"decision_ref": ID, "record_ref": ID}, ("decision_ref", "record_ref"))})
    from copy import deepcopy
    from ..contracts import PLAN_DISPOSITION, schema_for
    selection = deepcopy(PLAN_DISPOSITION)
    selection["properties"].update({"execution_id": ID, "contract_sha256": HASH})
    selection["required"] += ["execution_id", "contract_sha256"]
    assessment = deepcopy(schema_for("research_plan")["properties"]["task_assessments"]["items"])
    assessment["properties"].update({"execution_id": ID, "contract_sha256": HASH, "results_sha256": HASH,
                                      "current": BOOL, "basis": EVIDENCE, "invalidated_reason": TEXT,
                                      "specialist_support": mapping(ID)})
    RECORDS["tasks"]["properties"].update({
        "feature_version": {"const": STATE_FORMAT_VERSION}, "trust_environment_id": ID,
        "profile_refs": array(PROFILE_REF, True),
        "producer_execution": ID, "author_execution_ids": REFS, "revision_request_action_id": ID,
        "knowledge_revision_targets": REFS, "selection_disposition": selection,
        "assessment_history": array(assessment), "assessment": assessment,
        "required_external_effects": array(obj({"id": TEXT, "scope": TEXT, "grant_id": nullable(ID)}, ("id", "scope"))),
        "transferred_obligations": array(obj({"from_task": ID, "from_revision": {"type": "integer", "minimum": 1},
            "from_obligation_id": TEXT, "obligation_id": TEXT, "authority_ref": ID, "execution_id": ID},
            ("from_task", "from_revision", "from_obligation_id", "obligation_id", "authority_ref", "execution_id")))})
    RECORDS["external_operations"]["properties"].update({"target_id": ID, "purpose": TEXT, "subject": TEXT,
        "producer_executions": REFS,
        "budget_kind": enum("work", "operations"), "actor_kind": enum("ai", "machine"),
        "execution_id": ID, "continuation_of": nullable(ID), "retried_from": TEXT, "history": HISTORY,
        "handling": enum("reconciliation_required", "reconciled"), "external_id": nullable(TEXT),
        "previous_outcome": enum("unknown", "failed"),
        "retry_evidence": obj({"kind": enum("effect_absent", "verified_idempotency"),
            "request_sha256": HASH, "idempotency_key": HASH, "evidence_ref": TEXT,
            "valid_until": TEXT, "source": enum("user", "adapter")},
            ("kind", "request_sha256", "idempotency_key", "evidence_ref", "source")),
        "academic_binding": obj({"task_id": ID, "requirement_id": TEXT, "effect_id": TEXT,
            "solution_basis": basis, "requirements_sha256": HASH},
            ("task_id", "requirement_id", "effect_id", "solution_basis", "requirements_sha256"))})
    RECORDS["executions"]["properties"].update({"operation_id": ID, "request_sha256": HASH,
        "effect_status": enum("prepared", "confirmed", "failed", "unknown", "cancelled"),
        "http_status": nullable(NAT), "succeeded": nullable(BOOL)})
    RECORDS["integrations"]["properties"]["response_sha256"] = HASH
    RECORDS["question_links"]["properties"].update({"unresolved_target_ids": REFS, "blocks": BOOL,
        "checked_by": nullable(ID), "resolution_history": HISTORY, "source_kind": TEXT, "source_id": ID,
        "origin_execution_id": nullable(ID), "resolution_evidence": array(TEXT), "resolution_reason": TEXT})
    from ..governance import interpretation_schema
    RECORDS["intent_imports"] = record({"source": RECORDS["governance_sources"],
        "output": interpretation_schema("interpret"), "execution_id": ID,
        "coordinate_unit": enum("unicode_codepoint"), "basis_sha256": HASH, "basis_scope": enum("referenced-v1"), "sha256": HASH,
        "previous_id": nullable(ID), "previous_findings": HISTORY, "status": TEXT,
        "superseded_by": ID, "check": EVIDENCE, "application": EVIDENCE, "owner_basis": mapping(EVIDENCE), "input_ref": ID},
        ("source", "output", "execution_id", "coordinate_unit", "basis_sha256", "sha256", "previous_id", "previous_findings", "status"))
    subject = obj({"kind": TEXT, "id": TEXT}, ("kind", "id"))
    rule = obj({"id": TEXT, "operator": TEXT, "subject": subject,
        "basis": obj({"source": TEXT, "unit": TEXT}, ("source", "unit")),
        "threshold": {"type": ["integer", "string"]}, "repeat_interval": NAT,
        "required_evidence": array(TEXT, True)}, ("id", "operator", "subject", "basis", "threshold", "required_evidence"))
    RUNTIME_FIELDS["task_observation_rules"] = mapping(array(rule))
    observation = obj({"kind": TEXT, "execution_id": ID, "observed_at": TEXT,
        "trigger": TEXT, "call_id": TEXT, "review_id": nullable(TEXT), "reason": nullable(TEXT),
        "basis_ref": nullable(TEXT), "basis": EVIDENCE, "observation_refs": REFS,
        "obligation_ids": REFS, "obligation_id": nullable(ID), "rule_ids": REFS,
        "interval_ms": NAT, "review_window_ms": NAT, "window_ms": NAT, "at": TEXT,
        "followup": nullable(obj({"kind": TEXT, "trigger": TEXT, "next_owner": TEXT,
                                  "basis_refs": REFS}, ("kind", "next_owner"))),
        "elapsed_ms": NAT, "next_owner": TEXT, "checkpoint_status": TEXT,
        "proposal_sha256": nullable(HASH), "previous_rules_sha256": HASH, "active_rules_sha256": HASH,
        "active_revision": NAT, "rules": array(rule), "rule_revision": NAT,
        "started_offset_ms": NAT, "due_offset_ms": NAT, "evidence_refs": array(TEXT)}, ("kind", "execution_id", "observed_at"))
    RUNTIME_FIELDS["observations"] = mapping(observation)
    fact = RECORDS["observation_facts"]
    fact["properties"].update({"event_json": TEXT, "event_sha256": HASH, "monotonic_offset_ms": NAT,
        "source": obj({'stream': {'const': 'stdout.jsonl'}, 'start_offset': NAT, 'end_offset': NAT,
                       'received_at': TEXT, 'received_offset_ms': NAT},
                      ('stream', 'start_offset', 'end_offset', 'received_at', 'received_offset_ms'))})
    fact["required"] = ["id", "kind", "execution_id", "observed_at"]
    fact["oneOf"] = [{"required": ["event"]}, {"required": ["event_json", "event_sha256", "monotonic_offset_ms"]}]
    obligation = RECORDS["self_check_obligations"]
    obligation["properties"].update({"opened_offset_ms": NAT, "deadline_offset_ms": nullable(NAT),
        "observed_at": TEXT, "rules_sha256": HASH, "snapshot": EVIDENCE,
        "consumed_boundaries": mapping(NAT), "response_availability": enum("available", "awaiting_safe_boundary"),
        "missed_reason": TEXT, "safe_boundary_ref": TEXT, "closed_at": TEXT, "close_reason": TEXT,
        "delivered_source_offset": NAT, "delivered_at": TEXT, 'delivered_request_sha256': HASH,
        'acknowledged_source_offset': NAT, 'acknowledged_call_id': TEXT})
    obligation["required"] = ["id", "kind", "execution_id", "rule_revision", "due", "opened_offset_ms", "deadline_offset_ms", "status", "observed_at"]
    response = RECORDS["self_check_responses"]
    response["properties"].update({"obligation_id": nullable(TEXT), "receipt_ref": nullable(TEXT),
        "response_json": TEXT, "received_offset_ms": NAT, "errors": array(TEXT),
        "followup": obj({"kind": TEXT, "next_owner": TEXT, "trigger": TEXT, "basis_refs": array(TEXT)}, ("kind", "next_owner")),
        "worker_feedback": obj({"kind": TEXT, "errors": array(TEXT), "obligation_id": nullable(TEXT), "next_owner": TEXT}),
        "next_self_check_offset_ms": nullable(NAT), "no_progress_count": NAT})
    response["required"] = ["id", "kind", "execution_id", "obligation_id", "observed_at", "response_json", "received_offset_ms"]
    RECORDS["recoveries"] = record({"started_at": TEXT, "execution_ids": REFS,
        "dispositions": array(obj({"execution_id": ID, "fact": TEXT, "next_owner": TEXT,
            "local_termination_confirmed": BOOL, "remote_termination": enum("unknown"),
            "reservation_reconciled": BOOL, "disposition": TEXT,
            "process_alive": BOOL, "workspace_preserved": BOOL, "reason": TEXT}, ("execution_id",))),
        "finished_at": TEXT}, ("started_at", "execution_ids", "dispositions"))
    RECORDS["operational_dispositions"]["properties"].update({"target_execution_id": ID,
        "obligation_ids": REFS, "applied_at": TEXT, "result": EVIDENCE, "error": TEXT})
    RESEARCH_FIELDS["available_input_refs"] = array(TEXT, True)
    RUNTIME_FIELDS["pending_kind_checks"] = array(obj({"family": enum("knowledge", "relation"),
        "token": TEXT, "definition_id": ID, "source_ref": TEXT, "actor_ref": TEXT,
        "execution_id": ID}, ("family", "token")))
    RECORDS["grants"]["properties"]["initialization_only"] = BOOL
    RECORDS["knowledge"]["properties"].update({"kind_definition_id": ID, "kind_use_suspended": BOOL,
        "imported_at": TEXT, "imported_by": TEXT, "source_ref": TEXT})
    RECORDS["relations"]["properties"].update({"kind_definition_id": ID, "authority": enum("mathematical_connection", "research_connection"),
        "revision": NAT, "imported_at": TEXT, "imported_by": TEXT})
    RECORDS["kind_definitions"]["properties"]["constraints"]["properties"].update({
        "required_fields": array(TEXT, True), "allowed_epistemic_statuses": array(TEXT, True)})
    RECORDS["decisions"]["anyOf"][1]["required"] = ["kind", "change"]
    RECORDS["capacity_constraints"]["properties"]["budget_kind"] = enum("work", "operations")
    host_amounts = obj({"jobs": NAT, "memory_bytes": NAT,
        "cpu_rate_basis_points": {"type": "integer", "minimum": 0, "maximum": 10000}},
        ("jobs", "memory_bytes", "cpu_rate_basis_points"))
    RECORDS["capacity_constraints"]["properties"].update({"host_id": TEXT,
        "control_reserve": host_amounts, "authority_refs": REFS})
    RECORDS["execution_profiles"]["properties"]["host_resources"] = obj({
        "constraint_id": ID, "scope": enum("instance_on_host"), "host_id": TEXT, "demands": host_amounts},
        ("constraint_id", "scope", "host_id", "demands"))
    RESEARCH_FIELDS["host_capacity_ref"] = ID
    RECORDS["control_receipts"]["properties"].update({"request_sha256": HASH, "snapshot": TEXT,
        "publication_id": ID, "payload_sha256": HASH, "transport_id": TEXT, "request": EVIDENCE, "parent_snapshot": TEXT})
    RECORDS["provider_waits"] = record({"provider": enum("codex", "claude"), "generation": NAT,
        "state": enum("waiting", "checking", "available"), "retry_at": nullable(NAT), "attempts": NAT,
        "probe_owner": nullable(ID), "probe_started_at": nullable(NAT),
        "evidence": obj({"execution_id": ID, "kind": TEXT, "provider": TEXT,
            "evidence_ref": nullable(TEXT), "reported_fields_json": TEXT}, ("execution_id", "kind", "provider", "reported_fields_json"))},
        ("provider", "generation", "state", "retry_at", "attempts", "probe_owner", "probe_started_at", "evidence"))
    RECORDS["executions"]["properties"]["capacity"] = obj({"provider": nullable(TEXT), "acquired_at": NAT,
        "released_at": NAT, "reservation_ids": REFS, "profile_ref": PROFILE_REF, "model": TEXT,
        "budget_kind": TEXT, "release_evidence": EVIDENCE, "state": TEXT,
        "process": nullable(EVIDENCE), "local_termination": enum("unknown", "confirmed")})
    RECORDS["kind_definitions"]["properties"]["supersedes"] = ID
    RECORDS["kind_definitions"]["properties"].update({key: TEXT for key in
        ("check_ref", "checked_by", "approval_ref", "activated_by", "withdrawn_reason", "withdrawn_by")})
    RECORDS["assessment_uses"]["properties"]["environment_revalidation"] = obj({"environment_id": ID, "reason": TEXT}, ("environment_id", "reason"))
    for name in ("formal_results", "assessment_uses", "relations", "tasks", "goal_judgments"):
        RECORDS[name]["properties"]["use_history"] = HISTORY
    RECORDS["tasks"]["properties"]["input_current"] = BOOL
    RECORDS["goal_judgments"]["properties"]["current"] = BOOL
    RECORDS["knowledge"]["properties"].update({"revision_reason": TEXT, "use_suspensions": HISTORY,
        "use_suspension_reasons": array(TEXT), "actor_ref": TEXT, "task_id": ID})
    RECORDS["decisions"]["properties"].update({"input_source_ref": ID, "input_source_sha256": HASH,
        "author_execution_ids": REFS, "status": TEXT, "revoked_at": TEXT})
    RECORDS["grants"]["properties"].update({"status": enum("active", "revoked", "withdrawn", "expired"),
        "expired_at": TEXT, "expiry_event_ref": ID, "used_by": REFS, "uses": HISTORY,
        "replaced_by": ID, "academic_only": BOOL, "requires_academic": BOOL,
        "excluded_origins": array(TEXT, True), "excluded_path_prefixes": array(TEXT, True),
        **{key: array(TEXT, True) for key in ("execution_kinds", "purposes", "subjects")}})
    RECORDS["delegations"]["properties"]["resource_limits"] = mapping(NAT)
    case_basis_reference = {"oneOf": [ID, obj({"id": ID}, ("id",))]}
    RECORDS["delegation_applications"] = record({"delegation_id": ID,
        "basis": obj({"delegation": RECORDS["delegations"], "original_decision": RECORDS["decisions"],
            "approval": RECORDS["decisions"], "source": RECORDS["governance_sources"],
            "original_source": RECORDS["governance_sources"], "target": EVIDENCE, "references": mapping(EVIDENCE),
            "case": obj({"id": ID, "decision_kind": TEXT, "target_id": ID, "external_effects": array(TEXT),
                "resources": mapping(NAT), "effect": EVIDENCE, "basis_refs": array(case_basis_reference)}, ("id", "decision_kind", "target_id", "external_effects", "resources", "effect"))},
            ("delegation", "original_decision", "approval", "source", "original_source", "case", "target", "references")),
        "input_sha256": HASH, "judgments": obj({stage: obj({"execution_id": ID, "sha256": HASH,
            "output": obj({"input_sha256": HASH, "decision": enum("within_scope", "outside_scope", "unresolved"), "reason": TEXT},
                          ("input_sha256", "decision", "reason"))}, ("execution_id", "sha256", "output")) for stage in ("interpret", "check")}),
        "application": obj({"status": enum("applied"), "application_id": ID, "input_sha256": HASH,
            "original_decision_id": ID, "effect": EVIDENCE, "post_basis_sha256": HASH, "sha256": HASH},
            ("status", "application_id", "input_sha256", "original_decision_id", "effect", "post_basis_sha256", "sha256"))},
        ("delegation_id", "basis", "input_sha256", "judgments"))
    RECORDS["governance_events"] = record({"kind": TEXT, "grant_id": ID, "at": TEXT, "affected": REFS},
                                         ("kind", "grant_id", "at", "affected"))
    from ..execution_profiles import OBSERVATION_KEYS, WINDOW_KEYS
    profile = RECORDS["execution_profiles"]["properties"]
    profile['machine'] = obj({"lean_command": nullable(array(TEXT))}, ("lean_command",))
    observation_binding = obj({"source": TEXT, "operator": TEXT, "subject_kind": TEXT, "unit": TEXT},
                              ("source", "operator", "subject_kind", "unit"))
    profile["observation"] = obj({"mode": enum("event_driven", "periodic", "deadline_only"),
        "settings": obj({key: NAT for key in OBSERVATION_KEYS}), "rule_bindings": array(observation_binding)},
        ("mode", "settings", "rule_bindings"))
    profile["window"] = obj({key: NAT for key in WINDOW_KEYS})
    profile["input"] = obj({"max_input_bytes": NAT, "unit": enum("utf8_bytes"), "provider_context_capacity": enum("unknown")},
                            ("max_input_bytes", "unit", "provider_context_capacity"))
    profile["ai"] = obj({"model": TEXT, "tier": nullable(TEXT), "provider": enum("codex", "claude"),
        "effort": TEXT, "capacity_refs": REFS, "provider_operations": TEXT,
        "remote_termination": TEXT, "maximum_output_enforced": BOOL, "claude_only_assigned_model": BOOL,
        "scholarly_server": nullable(EVIDENCE)}, ("model", "tier", "provider", "effort", "capacity_refs"))
    RECORDS["events"]["properties"].update({"basis_sha256": HASH, "basis": EVIDENCE,
        "observed_at": TEXT, "regenerate_after": nullable(TEXT),
        "scope": TEXT, "next_owner": TEXT, "affected": REFS,
        "errors": array(TEXT), "request_sha256": HASH, "result": TEXT,
        "judgment_ids": REFS, "artifact_ref": TEXT, "outcome": TEXT, "evidence": EVIDENCE})
    execution = RECORDS["executions"]["properties"]
    execution.update({**{key: TEXT for key in ("submission_check_ref", "submitted_output_ref", "submitted_extensions_ref",
        "formal_status", "error_kind", "input_published_at", "finished_at", "started", "return_reason", "observed_at",
        "stop_observed_at", "preserved_reason")},
        **{key: HASH for key in ("intent_import_sha256", "contract_sha256", "academic_requirements_sha256", "delegation_input_sha256")},
        **{key: EVIDENCE for key in ("safe_boundary_report", "extensions", "integration_result", "control_transport",
            "input_metrics", "decision_basis", "validity_basis", "operational_continuation", "input_solution_basis",
            "termination", "collection", "currentness", "provider_execution", "failure", "protocol")},
        **{key: HISTORY for key in ("source_basis", "input_reductions", "currentness_changes")},
        "usage_segments": array(obj({"segment": NAT, "line": NAT, "usage": EVIDENCE},
                                   ("segment", "line", "usage"))),
        "model_usage_reported": EVIDENCE,
        "usage_scope": obj({key: TEXT for key in ("usage", "model_usage_reported", "total_cost_usd")},
                           ("usage", "model_usage_reported", "total_cost_usd")),
        "reported_models": array(TEXT, True),
        "model_selection": nullable(EVIDENCE), "integration_id": ID, "goal_revision": NAT,
        "policy_revision": {"type": ["integer", "string"]}, "pending_operational_disposition": ID,
        "return_code": nullable(INTEGER), "elapsed_milliseconds": NAT, "outputs_complete": BOOL,
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
            ("stage", "started_at", "updated_at"))})
    execution["validity_basis"] = array(obj({"id": ID, "sha256": HASH, "status": nullable(TEXT)},
                                            ("id", "sha256", "status")))
    RECORDS["inputs"] = record({"instance_id": ID, "action": TEXT, "text": TEXT, "config": EVIDENCE,
        "created_at": TEXT, "origin": TEXT, "accepted_order": TEXT, "sha256": HASH}, ("text", "config"))
    action = record({"role": TEXT, "target": nullable(TEXT), "stage": TEXT, "slot": {"type": ["string", "integer"]},
        "round": NAT, "reason": TEXT, "grant_id": ID, "profile_ref": PROFILE_REF,
        "owner_activity_id": ID, "activity_id": ID, "execution_id": ID, "continuation_of": ID,
        "context_origin": REFS, "lineage_id": ID, "review_cycle_id": ID, "import_id": ID,
        "previous_import_id": ID, "transition_id": ID, "decision_id": ID, "rejection_id": ID,
        "created_at": TEXT, "live": BOOL, "initialization": BOOL, "required": {"anyOf": [BOOL, NAT]},
        "repair_attempt": NAT, "diagnosis_attempt": NAT, "initial_submission_diagnosis": BOOL,
        "output_repairs": NAT, "attempts": NAT, "max_rounds": NAT,
        **{key: EVIDENCE for key in ("repair", "observation", "dispatch_wait", "revision_targets", "exhaustion_basis", "selection", "model_assessment", "input_basis", "assessment_targets", "observation_rule_targets", "waiting", "research_request", "revision_request", "input_overflow_retry")},
        **{key: array(TEXT, True) for key in ("event_refs", "receipt_refs", "obligation_ids", "observation_refs", "affected_ids", "evidence_refs", "required_source_refs")},
        "review_basis_key": TEXT, "investigation_id": ID, "task_title": TEXT, "not_before": TEXT,
        "retry_at": TEXT, "settle_started_at": TEXT, "source_ref": TEXT, "scope": TEXT}, ("role",))
    RECORDS["queue"] = action
    action['properties']['observation_rule_targets'] = mapping(obj(
        {'revision': {'type': 'integer', 'minimum': 1}, 'contract_sha256': HASH}, ('revision', 'contract_sha256')))
    execution['observation_rules'] = array(rule)
    from ..task_contracts import REPEAT_LINEAGES
    from ..model_policy import ASSESSMENT_SCHEMA, TIERS
    RECORDS["tasks"]["properties"].update({"remaining_work": array(TEXT),
        "observation_rule_history": HISTORY,
        "model_assessment_history": array(obj({"revision": NAT, "contract_sha256": HASH,
            "assessment": ASSESSMENT_SCHEMA, "contract_review_execution": ID},
            ("revision", "contract_sha256", "assessment", "contract_review_execution")))})
    model_selection = obj({"tier": nullable(enum(*TIERS)), "model": TEXT,
        "assessment": nullable(ASSESSMENT_SCHEMA), "reason": TEXT, "profile_ref": PROFILE_REF},
        ("tier", "model", "assessment", "reason"))
    RECORDS["executions"]["properties"]["model_selection"] = nullable(model_selection)
    action["properties"].update({"repetition_bases": obj({name: HASH for name in REPEAT_LINEAGES}),
        "repetition_lineage": {"type": "array", "prefixItems": [enum(*REPEAT_LINEAGES), TEXT], "items": False, "minItems": 2},
        "requested_by": ID, "requested_by_refs": REFS, "cleanup_execution_ids": REFS,
        "periodic_reconsideration": BOOL, "exhaustion_event_ref": ID,
        "opened_at": TEXT, "merged_action_ids": REFS, "selected_contract_sha256": HASH, "selection_execution_id": ID,
        "scope_decision_id": ID, "revision_request_action_id": ID,
        "basis": HASH, "kind_definition_id": ID, "kind_definition_sha256": HASH,
        "formal_target": ID,
        "model_selection": model_selection,
        "contract_basis": obj({"revision": NAT, "contract_sha256": HASH, "goal_revision": NAT,
            "policy_revision": {"type": ["integer", "string"]}},
            ("revision", "contract_sha256", "goal_revision", "policy_revision"))})
    action["properties"].update({"actor_kind": enum("ai", "machine"), "budget_kind": enum("work", "operations"),
        "purpose": TEXT, "continuity_break_cause": TEXT, "continuity_broken": BOOL, "grant_sha256": HASH,
        "replacement_for": NAT, "owner_review_cycle_id": ID, "identity_review": EVIDENCE,
        "knowledge_id": ID, "source_basis": HISTORY})
    metrics = obj({"unit": enum("UTF-8_bytes"), "prompt_bytes": NAT, "context_bytes": NAT,
        "schema_bytes": NAT, "document_bytes": mapping(NAT), "context_component_value_bytes": mapping(NAT),
        "framing_bytes": INTEGER},
        ("unit", "prompt_bytes", "context_bytes", "schema_bytes", "document_bytes",
         "context_component_value_bytes", "framing_bytes"))
    overflow = obj({"kind": enum("input_overflow"), "reason": TEXT, "actual_bytes": NAT,
        "mandatory_bytes": NAT, "limit_bytes": NAT, "required_direct_keys": array(TEXT, True),
        "role": nullable(TEXT), "profile_id": nullable(ID), "activity_id": nullable(ID),
        "packed_bytes": NAT, "original_bytes": NAT, "unit": enum("utf8_bytes"),
        "component_bytes": mapping(NAT), "reductions": HISTORY, "prompt_metrics": metrics,
        "cause": enum("common_documents_or_governance", "required_role_input", "current_proposal_or_required_sources", "restored_dialogue"),
        "without_restored_dialogue_bytes": NAT, "allowed_profile_candidates": REFS,
        "suggested_disposition": enum("unresolved_to_review_plan", "plan_allowed_profile", "request_user_decision"),
        "resolution_question": obj({"kind": enum("input_capacity"), "activity_id": nullable(ID),
            "role": nullable(TEXT), "required_direct_keys": array(TEXT, True), "question": TEXT,
            "next_owner": enum("research_plan", "user")}, ("question", "next_owner"))},
        ("kind", "reason", "actual_bytes", "mandatory_bytes", "limit_bytes", "required_direct_keys",
         "role", "profile_id", "activity_id"))
    action["properties"].update({"input_overflow": overflow, "overflow_activity_id": ID,
        "delegation_application_id": ID, "contract_review_execution": ID,
        "operational_disposition_id": ID, "research_request_id": TEXT, "requesting_slot": TEXT,
        "revision_cycles": array(array(ID)), "revision_parent_ids": REFS, "unbound_request": BOOL,
        "reasons": array(TEXT), "superseded_revision_bases": HISTORY,
        "revision_followup": array(obj({"record_id": ID, "task_id": ID}, ("record_id", "task_id"))),
        "intent_repair": obj({"import_id": ID, "previous_sha256": HASH, "check_execution_id": ID,
            "findings": array(TEXT)}, ("import_id", "previous_sha256", "check_execution_id", "findings")),
    })
    RUNTIME_FIELDS["revision_cycles"] = array(array(ID))
    impact_plan = obj({**{name: REFS for name in ("roots", "computed_impact", "declared_impact",
        "missing_declarations", "extra_declarations", "unresolved_refs")}, "sensitive": BOOL,
        "requires_independent_review": BOOL, "basis": mapping(HASH), "digest": HASH},
        ("roots", "computed_impact", "declared_impact", "missing_declarations", "extra_declarations",
         "unresolved_refs", "sensitive", "requires_independent_review", "basis", "digest"))
    impact_request = obj({"integration_id": TEXT, "payload_sha256": HASH, "producer_execution_id": ID,
        "input_snapshot": TEXT, "plans": mapping(impact_plan)},
        ("integration_id", "payload_sha256", "producer_execution_id", "input_snapshot", "plans"))
    action["properties"].update({"recovery": obj({"execution_id": ID, "disposition_id": ID, "reason": TEXT,
        "provider_generation": NAT}, ("execution_id", "reason")),
        "recovery_attempt": NAT, "refresh": obj({"execution_id": ID,
        "changes": HISTORY, "attempt": NAT}, ("execution_id", "changes", "attempt"))})
    RUNTIME_FIELDS["waiting_actions"]["additionalProperties"]["properties"].update({
        'diagnosis': obj({'execution_id': ID, 'decision': enum('retry', 'wait'), 'guidance': TEXT, 'retry_error': TEXT},
                         ('execution_id', 'decision', 'guidance')),
        "reason": nullable(TEXT), "failure_kind": nullable(TEXT), "input_snapshot": TEXT,
        "changes": HISTORY, "import_id": ID, "question": TEXT, "owner": TEXT, "release_condition": TEXT,
        "observation_errors": HISTORY, "observation_rule_deferrals": HISTORY, "rule_input_version": EVIDENCE,
        "review_requests": mapping(impact_request), "review_execution_ids": mapping(ID),
        "revision_targets": EVIDENCE, "delegated_targets": mapping(ID), "delegated_to_task_id": nullable(ID),
        "delegation_history": array(obj({"record_id": ID, "task_id": ID}, ("record_id", "task_id"))),
        "input_version": obj({"goal": NAT, "policy": {"type": ["integer", "string"]},
            "sources": array(obj({"name": TEXT, "sha256": HASH}, ("name", "sha256"))), "inputs": REFS},
            ("goal", "policy", "sources", "inputs")),
        "provider": enum("codex", "claude"), "generation": NAT,
        "retry_at": nullable({"anyOf": [TEXT, NAT]}),
        "activity_wait": obj({"kind": enum("provider_admission"), "provider": enum("codex", "claude"),
            "state": enum("waiting"), "retry_at": nullable(TEXT), "retry_at_timestamp": NAT, "attempt": NAT},
            ("kind", "provider", "state", "retry_at", "attempt"))})
    action["allOf"] = [{"if": {"properties": {"stage": {"const": "impact_review"}}, "required": ["stage"]},
        "then": {"properties": {"role": {"const": "maintenance"},
            "input_basis": obj({"impact_review": impact_request}, ("impact_review",))}, "required": ["input_basis"]}}]
    execution["input_metrics"] = metrics
    RUNTIME_FIELDS["input_overflows"] = array(obj({"action": action, "detail": overflow,
        "source_catalog": EVIDENCE}, ("action", "detail", "source_catalog")))
    binding = obj({"role_slot_id": TEXT, "profile_ref": nullable(PROFILE_REF), "input_sha256": nullable(HASH),
        "input_snapshot": TEXT, "proposal_digest": HASH, "restored_messages": HISTORY,
        "request": EVIDENCE, "visible_execution_ids": REFS, "delegation_authority": EVIDENCE},
        ("role_slot_id", "profile_ref", "input_sha256", "input_snapshot", "proposal_digest", "restored_messages", "request", "visible_execution_ids"))
    RECORDS["review_cycles"]["properties"].update({"input_snapshot": TEXT, "producer_execution_ids": REFS,
        "transition_id": ID, "staged_candidate": obj({"proposal": EVIDENCE,
            "identity_basis": obj({"formal": HASH, "exposition": HASH}, ("formal", "exposition")),
            "transition_basis": HASH, "target_environment": RECORDS["trust_environments"]},
            ("proposal", "identity_basis", "transition_basis", "target_environment")),
        "identity_basis": obj({"formal": HASH, "exposition": HASH}, ("formal", "exposition")),
        "policy_ref": TEXT, "publication_premises": EVIDENCE, "review_input_basis": EVIDENCE,
        "slot_profiles": mapping(nullable(PROFILE_REF)), "input_bindings": mapping(binding),
        "assessment_id": ID, "assessment_use_ids": REFS, "continuity_events": HISTORY,
        "blocked_actions": mapping(NAT), "replacement_actions": mapping(obj({"action": EVIDENCE,
            "recovery_event": NAT, "grant_id": ID, "grant_sha256": HASH, "authority_request": action,
            "authority": EVIDENCE, "delegation_id": nullable(ID), "case": nullable(EVIDENCE),
            "sealed_input_sha256": HASH, "omitted_indices": array(NAT)},
            ("action", "recovery_event", "grant_id", "grant_sha256", "authority_request", "authority", "delegation_id", "case", "sealed_input_sha256", "omitted_indices"))),
        "replacement_receipts": HISTORY, "transcript_replacements": HISTORY,
        "pending_findings": array(TEXT, True), "answer_requests": array(TEXT, True)})
    RUNTIME_FIELDS["review_inputs"]["additionalProperties"]["properties"]["restored_messages"] = HISTORY
    RUNTIME_FIELDS["waiting_actions"]["additionalProperties"]["properties"]["recovery"] = obj({
        "disposition": TEXT, "authority": EVIDENCE, "action": EVIDENCE, "review_cycle_id": ID,
        "next_owner": TEXT, "review_closure": TEXT, "recovery_event": EVIDENCE, "reason": TEXT,
        "event": EVIDENCE, "cycle": EVIDENCE, "retryable": BOOL,
        "owner_activity_id": nullable(ID), "review_status": TEXT})
    # An action embedded in an execution or wait is a historical input copy,
    # not another live queue record/global identity.
    RECORDS["executions"]["properties"]["action"] = action
    RUNTIME_FIELDS["waiting_actions"]["additionalProperties"]["properties"]["action"] = action


extend()
