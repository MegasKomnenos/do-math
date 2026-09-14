"""Generate v9 schemas and contracts from owned declarations and the draft."""
from __future__ import annotations

import copy
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DOC = ROOT.parent / "통합-설계.md"
BASE = "https://do-math.invalid/schemas/draft/9/"
VERSION = 9
SCHEMAS: dict[str, dict] = {}


def text(minimum=1):
    return {"type": "string", "minLength": minimum}


def enum(*values):
    return {"type": "string", "enum": list(values)}


def integer(minimum=0):
    return {"type": "integer", "minimum": minimum, "maximum": 9007199254740991}


def array(item, minimum=0, unique=False):
    result = {"type": "array", "items": item, "minItems": minimum}
    if unique:
        result["uniqueItems"] = True
    return result


def obj(properties, required=None):
    return {"type": "object", "properties": properties,
            "required": list(properties) if required is None else required,
            "additionalProperties": False}


def optional(properties, *names):
    return obj(properties, [key for key in properties if key not in names])


def common(name):
    return {"$ref": BASE + "common#/$defs/" + name}


def ref(family):
    return {"$ref": BASE + family}


def variant(key, choices):
    return {"oneOf": [obj({key: {"const": name}, **fields}, required)
                      for name, (fields, required) in choices.items()]}


S = text()
STRINGS = array(S, unique=True)
BOOL = {"type": "boolean"}
N = integer()
POS = integer(1)
ID = common("id")
IDS = array(ID, unique=True)
HASH = common("sha256")
OID = common("oid")
TIME = common("instant")
DURATION = common("duration")
PATH = common("path")
RECORD = common("record_ref")
ARTIFACT = common("artifact_ref")
EXACT = common("exact_ref")
LINK = common("link_ref")
REFS = array(EXACT, unique=True)
NONEMPTY_REFS = array(EXACT, 1, True)
LIFECYCLE = enum("active", "superseded", "withdrawn")
ASSESSMENT = enum("match", "mismatch", "unresolved")
APPROVAL = enum("approved", "revision_required", "unresolved")
USE = enum("active", "suspended", "withdrawn")
CAUSE = obj({"code": S, "message": S, "evidence_refs": REFS})
FILE = obj({"path": PATH, "sha256": HASH, "media_type": S, "size_bytes": N})
SUBJECT = obj({"kind": enum("instance", "task", "activity"), "id": ID})
WAIT = obj({"wait_kind": enum("user_decision", "research_input", "validation",
                             "external_event", "execution_repair"),
            "target_refs": NONEMPTY_REFS, "next_owner": SUBJECT,
            "wake": common("wake")})
FOLLOWUP = obj({"kind": S, "owner": SUBJECT, "input_refs": REFS,
                "wake": common("wake"), "reason": S})
FOLLOWUPS = array(FOLLOWUP)
BASIS = obj({"record_refs": REFS, "absence_queries": array(common("query_scope")),
             "required_effects": array(obj({"record_ref": EXACT, "effect": S}))})
RANGE = obj({"id": S, "description": S, "evidence_refs": REFS})
RANGES = array(RANGE)
FIELD_RESULT = obj({"item_id": S, "verdict": APPROVAL, "reason": S,
                    "evidence_refs": REFS})
EXECUTION_KINDS = ("research_preparation", "research_plan", "research_work",
                   "task_contract_review", "identity_review", "goal_audit",
                   "operational_review", "intent_interpretation",
                   "supplemental_research", "maintenance")

common_defs = {
    "id": {"type": "string", "pattern": r"^[A-Z][A-Z0-9]{0,7}-[0-7][0-9A-HJKMNP-TV-Z]{25}$"},
    "sha256": {"type": "string", "pattern": r"^[0-9a-f]{64}$"},
    "oid": {"type": "string", "pattern": r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$",
            "$comment": "Object-format length is checked against the instance, not guessed."},
    "instant": {"type": "string", "format": "date-time",
                "pattern": r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$"},
    "duration": {"type": "string", "format": "do-math-duration",
                 "pattern": r"^PT(?=\d)(?:\d+H)?(?:\d+M)?(?:\d+(?:\.\d{1,3})?S)?$"},
    "path": {"type": "string", "format": "do-math-path", "minLength": 1},
    "record_ref": obj({"ref_kind": {"const": "record"}, "space": enum("research", "runtime"),
                       "commit": OID, "record_id": ID, "sha256": HASH}),
    "artifact_ref": obj({"ref_kind": {"const": "artifact"}, "bundle_id": ID,
                         "path": PATH, "sha256": HASH}),
    "tree_record_ref": obj({"ref_kind": {"const": "tree"}, "record_id": ID}),
    "exact_ref": {"oneOf": [common("record_ref"), common("artifact_ref")]},
    "link_ref": {"oneOf": [common("record_ref"), common("artifact_ref"),
                           common("tree_record_ref")]},
    "wake": {"oneOf": [obj({"kind": {"const": "time"}, "at": TIME}),
                       obj({"kind": {"const": "event"}, "event_kind": S, "target_id": ID})]},
    "query_scope": obj({"space": enum("research", "runtime"), "family": S,
                        "record_ids": IDS}),
    "file": FILE,
    "scalar": {"type": ["string", "integer", "boolean", "null"]},
    "source": optional({"resource": S, "id": S, "title": S, "author": S,
                        "last_modified": TIME}, "id", "title", "author", "last_modified"),
    "observation_rule": obj({
        "id": S, "op": enum("event_recorded", "counter_gte", "iteration_gte",
                           "checkpoint_count_gte", "active_duration_gte",
                           "wall_time_reached", "tool_call_completed",
                           "safe_boundary_recorded"),
        "target_ref": EXACT, "unit": S, "baseline": common("scalar"),
        "threshold": common("scalar"), "required_evidence": STRINGS}),
    "occurrence_condition": {"oneOf": [
        obj({"op": {"const": "always"}}),
        obj({"op": enum("all", "any"), "args": array(common("occurrence_condition"), 1)}),
        obj({"op": {"const": "not"}, "arg": common("occurrence_condition")}),
        obj({"op": {"const": "record_exists"}, "space": enum("research", "runtime"),
             "record_id": ID, "family": S}),
        obj({"op": {"const": "record_lifecycle_is"}, "space": enum("research", "runtime"),
             "record_id": ID, "value": S}),
        obj({"op": {"const": "record_field_equals"}, "space": enum("research", "runtime"),
             "record_id": ID, "pointer": {"type": "string", "pattern": r"^(?:/(?:[^~/]|~[01])*)*$"},
             "value": common("scalar")}),
        obj({"op": {"const": "relation_exists"}, "subkind": S, "from_id": ID, "to_id": ID}),
        obj({"op": {"const": "task_disposition_is"}, "task_id": ID,
             "value": enum("completed", "closed")}),
        obj({"op": {"const": "decision_value_is"}, "decision_id": ID, "value": common("scalar")}),
        obj({"op": {"const": "artifact_valid"}, "artifact_ref": ARTIFACT}),
    ]},
}


def register(name, section, storage, properties, required=None, constraints=None, prefix=None):
    schema = {"$schema": "https://json-schema.org/draft/2020-12/schema",
              "$id": BASE + name, "title": name,
              "x-contract-id": f"do-math-draft/{name}/9",
              "x-owner-section": section, "x-storage": storage}
    props = {"schema_version": {"const": f"do-math-draft/{name}/9"}, **properties}
    schema.update(obj(props, None if required is None else ["schema_version", *required]))
    if constraints:
        schema["allOf"] = constraints
    if prefix:
        schema["x-id-prefix"] = prefix
        schema["properties"]["id"] = {"allOf": [ID, {"pattern": "^" + prefix + "-"}]}
    SCHEMAS[name] = schema
    return schema


def condition(field, value, then):
    return {"if": {"properties": {field: {"const": value}}, "required": [field]},
            "then": then}


def forbid(*fields):
    return {"not": {"anyOf": [{"required": [field]} for field in fields]}}


def require(*fields):
    return {"required": list(fields)}


register("instance", "1.4,14.1,19.2", "research/instance.json", {
    "id": ID, "name": S, "object_format": enum("sha1", "sha256"),
    "lifecycle": enum("initializing", "active", "paused"),
    "goal_status": enum("unsolved", "mathematically_solved"), "goal_reason": CAUSE,
    "active_charter_ref": EXACT, "active_policy_refs": REFS, "active_context_refs": REFS,
    "active_settings_ref": EXACT, "active_permission_refs": NONEMPTY_REFS,
    "active_trust_ref": EXACT, "implementation_ref": EXACT,
    "conversation_loss_policy": enum("continue_authorized", "pause"),
}, ["id", "name", "object_format", "lifecycle", "goal_status", "goal_reason",
    "active_policy_refs", "active_context_refs", "active_permission_refs",
    "implementation_ref", "conversation_loss_policy"],
    [condition("lifecycle", "active",
               require("active_charter_ref", "active_settings_ref", "active_trust_ref"))], "RI")

register("runtime", "3.1,9.1,13.5,14.2,19.2", "runtime/state.json", {
    "id": ID, "engine_id": ID, "lifecycle": enum("initializing", "active", "paused"),
    "resume_lifecycle": enum("initializing", "active"),
    "recovery_status": enum("checking", "ready", "blocked"),
    "recovery_evidence_refs": REFS, "event_cursor": N,
    "preparation_cursor": N, "selection_cursor": N,
    "next_research_reconsider_at": TIME, "pending_event_ids": IDS,
    "open_preparation_id": ID, "open_plan_id": ID,
    "threshold_holds": array(obj({"kind": enum("import_rework", "selection_failure",
                                               "exhaustion_empty", "proposal_version",
                                               "context_overflow", "output_truncation"),
                                  "owner": SUBJECT, "basis_refs": NONEMPTY_REFS,
                                  "decision_question_ref": ARTIFACT})),
}, ["id", "engine_id", "lifecycle", "recovery_status", "recovery_evidence_refs",
    "event_cursor", "preparation_cursor", "selection_cursor", "pending_event_ids", "threshold_holds"],
    [condition("lifecycle", "paused", require("resume_lifecycle")),
     {"if": {"properties": {"lifecycle": {"enum": ["initializing", "active"]}}},
      "then": forbid("resume_lifecycle")}], "RT")

governance_branches = {
    "charter": obj({"document_ref": ARTIFACT, "goal_refs": NONEMPTY_REFS,
                   "academic_requirements": array(obj({"id": S, "scope": S,
                        "completion_criteria": S, "assessor_kind": enum("research_plan"),
                        "external_effects": STRINGS, "authority_refs": REFS}))}),
    "policy": obj({"rule_id": S, "scope": S, "normative_text_ref": ARTIFACT,
                  "basis_refs": NONEMPTY_REFS, "overrides_policy_ids": IDS,
                  "audit_contracts": array(obj({"rule_id": S, "revision": POS,
                    "scope": S, "required_inputs": NONEMPTY_REFS,
                    "outcomes": array(obj({"value": S, "universal_result": enum("satisfied", "not_satisfied", "unresolved"),
                        "blocks_integration": BOOL, "blocks_external_action": BOOL,
                        "mathematical_defect_reason": S}), 1)}))}),
    "settings": obj({"budget_ref": EXACT, "execution_profile_refs": NONEMPTY_REFS,
                     "review_policy_ref": EXACT, "research_reconsider_interval": DURATION,
                     "history_window": N, "import_rework_limit": POS,
                     "selection_failure_limit": POS, "exhaustion_empty_limit": POS,
                     "proposal_version_limit": POS, "contract_revision_limit": POS, "report_policy_ref": ARTIFACT,
                     "retention_policy_ref": ARTIFACT}),
    "permission": optional({"subjects": IDS, "actions": STRINGS, "scope": S, "excluded_scope": S,
                      "resource_limits": array(obj({"constraint_id": S, "maximum": common("limit")})),
                      "valid_from": TIME, "expires_at": TIME, "stop_conditions": STRINGS,
                      "external_effects": STRINGS, "replay_allowed": BOOL,
                      "reuse": common("reuse_permission"), "user_decision_ref": EXACT,
                      "truncation": common("truncation_permission")}, "truncation"),
}
common_defs["limit"] = {"oneOf": [obj({"kind": {"const": "bounded"}, "value": N}),
                                  obj({"kind": {"const": "unlimited"}})]}
common_defs["truncation_permission"] = obj({
    "lists": array(enum("candidates", "canon"), 1, True), "order": enum("id", "sealed_random"),
    "activity_kinds": array(enum("research_preparation", "research_plan"), 1, True)})
common_defs["reuse_permission"] = {"oneOf": [
    obj({"kind": {"const": "case_only"}}),
    obj({"kind": {"const": "general"}, "conditions_ref": ARTIFACT}),
    obj({"kind": {"const": "case_delegation"}, "decision_kinds": STRINGS,
         "scope": S, "excluded_scope": S, "source_decision_refs": NONEMPTY_REFS})]}
register("governance", "1.4,13.1,13.2,19.3", "research/governance/{id}.json", {
    "id": ID, "kind": enum(*governance_branches), "lifecycle": LIFECYCLE,
    "approval_ref": EXACT, "origin_refs": NONEMPTY_REFS, "payload": {},
}, prefix="GV")["allOf"] = [
    condition("kind", kind, {"properties": {"payload": schema}})
    for kind, schema in governance_branches.items()]

ai_config = obj({"model": S, "effort": S, "provider": S, "tokenizer": S,
                 "context_tokens": POS, "output_reserve_tokens": POS, "safety_margin_tokens": N,
                 "capacity_refs": array(S, 1, True), "usage_constraint_ids": STRINGS,
                 "remote_recovery": obj({"retention": DURATION, "supported_gap": DURATION,
                                         "inspection_method": S, "evidence_ref": ARTIFACT}),
                 "compaction": obj({"disabled": BOOL, "evidence_ref": ARTIFACT,
                                    "overflow_behavior": {"const": "fail_call"},
                                    "overflow_evidence_ref": ARTIFACT})})
stop_policy = {"oneOf": [
    obj({"kind": {"const": "disabled"}}),
    obj({"kind": {"const": "bounded"}, "window": DURATION, "allowed_tools": STRINGS,
         "allowed_paths": array(PATH, 1, True),
         "max_usage": array(obj({"constraint_id": S, "amount": POS}), 1)})]}
observation = obj({"operational_review_mode": enum("event_driven", "periodic"),
                   "max_interval": DURATION, "self_check_response_window": DURATION,
                   "tool_review_window": DURATION, "allowed_operators": STRINGS,
                   "allowed_target_refs": REFS, "periodic_interval": DURATION})
register("execution-profile", "6.1,6.4.1,12.1,16.1,16.2,19.4",
         "research/governance/profiles/{id}.json", {
    "id": ID, "revision": POS, "actor_kind": enum("ai", "machine"),
    "adapter_ref": EXACT, "implementation_ref": EXACT, "tool_manifest_ref": ARTIFACT,
    "role_documents": array(FILE, 1), "host_capacity_refs": array(S, 1, True),
    "isolation_evidence_ref": ARTIFACT, "io_contract_ref": EXACT,
    "shutdown_grace": DURATION, "execution_window": DURATION,
    "ai": ai_config, "stop_checkpoint": stop_policy, "observation": observation,
    "evaluation_refs": REFS,
}, ["id", "revision", "actor_kind", "adapter_ref", "implementation_ref", "tool_manifest_ref",
    "role_documents", "host_capacity_refs", "isolation_evidence_ref", "io_contract_ref",
    "shutdown_grace", "evaluation_refs"],
    [condition("actor_kind", "ai", require("ai", "stop_checkpoint")),
     condition("actor_kind", "machine", {"allOf": [forbid("ai", "stop_checkpoint", "observation"),
                                                  require("execution_window")]})], "EP")

constraint = {"oneOf": [
    obj({"id": S, "kind": {"const": "concurrency"},
         "accounting_unit": enum("execution", "provider_operation"),
         "work_slots": N, "operations_slots": N, "total_slots": N,
         "source": enum("local_budget", "provider_verified"), "source_ref": EXACT}),
    obj({"id": S, "kind": enum("cumulative", "window"),
         "unit": enum("tokens", "requests", "currency_minor", "tool_milliseconds", "bytes"),
         "limit": common("limit"), "window": common("window"),
         "source_ref": EXACT, "authority_refs": NONEMPTY_REFS}),
    obj({"id": S, "kind": {"const": "host"}, "max_jobs": POS,
         "memory_bytes": POS, "cpu_rate_basis_points": {"type": "integer", "minimum": 1, "maximum": 10000},
         "control_headroom_evidence_ref": ARTIFACT})]}
common_defs["window"] = {"oneOf": [obj({"kind": {"const": "none"}}),
    obj({"kind": {"const": "fixed"}, "duration": DURATION, "reset_at": TIME, "basis_ref": EXACT})]}
register("budget", "4,19.4", "research/governance/budgets/{id}.json", {
    "id": ID, "constraints": array(constraint, 1), "approval_refs": NONEMPTY_REFS,
    "activation_evidence_refs": NONEMPTY_REFS}, prefix="BG")

register("resource-reservation", "4.2,4.5,19.4", "runtime/reservations/{id}.json", {
    "id": ID, "constraint_id": S, "unit": S, "authority_refs": NONEMPTY_REFS,
    "owner_kind": enum("execution", "provider_operation"), "owner_id": ID,
    "budget_kind": enum("work", "operations"), "purpose": enum("normal", "stop_checkpoint"),
    "reserved": N, "confirmed_consumed": N, "returned": N,
    "state": enum("held", "settled", "unrecoverable"), "evidence_refs": REFS,
    "reconcile_owner": {"const": "engine"}, "reobserve": common("wake"),
}, ["id", "constraint_id", "unit", "authority_refs", "owner_kind", "owner_id", "purpose",
    "reserved", "confirmed_consumed", "returned", "state", "evidence_refs", "reconcile_owner"],
    [condition("state", "held", require("reobserve")),
     condition("state", "settled", {"properties": {"evidence_refs": NONEMPTY_REFS}}),
     condition("state", "unrecoverable", {"properties": {"evidence_refs": NONEMPTY_REFS}})], "RR")

register("provider-operation", "4.2,6.1,13.3,19.4", "runtime/provider-operations/{id}/record.json", {
    "id": ID, "execution_id": ID, "request_ref": ARTIFACT, "profile_ref": EXACT,
    "action_id": ID, "provider_identifier": S, "reservation_ids": array(ID, 1, True),
    "observation": enum("not_sent", "running", "ended", "unknown", "unrecoverable"),
    "evidence_refs": REFS, "observed_at": TIME, "next_observation": common("wake"),
}, ["id", "execution_id", "request_ref", "profile_ref", "action_id", "reservation_ids",
    "observation", "evidence_refs", "observed_at"], prefix="PO")

register("conversation-state", "3.3,19.4", "runtime/conversations/{id}.json", {
    "id": ID, "connection_generation": POS, "policy": enum("pause", "continue_authorized"),
    "state": enum("connected", "disconnected", "lost"), "observed_at": TIME,
    "heartbeat_interval": DURATION, "loss_grace": DURATION, "last_heartbeat_at": TIME,
    "event_ids": IDS, "evidence_refs": REFS,
}, ["id", "connection_generation", "policy", "state", "observed_at", "event_ids", "evidence_refs"],
    [condition("policy", "pause", require("heartbeat_interval", "loss_grace"))], "CV")

progress = obj({"expected_changes": array(RANGE, 1),
    "initial_self_check_rules": array(common("observation_rule"), 1),
    "observation_bounds": obj({"allowed_operators": STRINGS, "allowed_target_refs": REFS,
                               "max_wall_interval": DURATION}),
    "no_progress_limit": integer(2), "reconsider_conditions": STRINGS})
scope_disposition = obj({"scope_id": S, "value": enum("fulfilled", "waived", "transferred", "open"),
    "evidence_refs": REFS, "successor_task_ids": IDS})
common_defs["paused_maintenance_authorization"] = obj({
    "procedure_ref": EXACT, "approval_ref": EXACT, "target_refs": NONEMPTY_REFS,
    "scope": RANGES, "authority_refs": NONEMPTY_REFS})
contract_fields = {
    "revision": POS, "title": S, "description": {"type": "string", "minLength": 1, "pattern": r"^[^\r\n]+$"},
    "question": S, "work_class": enum("research_production", "academic_validation"),
    "academic_validation": obj({"requirement_refs": NONEMPTY_REFS,
                               "solution_basis": common("solution_basis")}),
    "scope": array(RANGE, 1), "excluded_scope": RANGES,
    "required_inputs": REFS, "occurrence_condition": common("occurrence_condition"),
    "expected_outputs": array(obj({"kind": S, "scope": S}), 1),
    "expected_research_change": S, "progress_criteria": progress,
    "completion_criteria": array(obj({"id": S, "condition": S,
          "assessor_kind": enum("maintenance", "research_plan", "identity_review", "goal_audit", "user_decision"),
          "required_inputs": REFS}), 1),
    "authority_refs": NONEMPTY_REFS, "execution_profile_refs": NONEMPTY_REFS, "basis_refs": NONEMPTY_REFS,
    "author_execution_ids": array(ID, 1, True), "author_proposal_ref": ARTIFACT}
task_contract = optional(contract_fields, "description", "academic_validation")
task_contract["allOf"] = [
    condition("work_class", "academic_validation", require("academic_validation")),
    condition("work_class", "research_production", forbid("academic_validation"))]
common_defs["task_contract"] = task_contract
common_defs["solution_basis"] = obj({"goal_ref": EXACT, "result_refs": NONEMPTY_REFS,
                                    "explanation_refs": NONEMPTY_REFS,
                                    "identity_assessment_refs": NONEMPTY_REFS,
                                    "goal_audit_refs": NONEMPTY_REFS})
register("task", "5,9.4,19.5", "runtime/tasks/{id}/record.json", {
    "id": ID, "contract": common("task_contract"), "state": enum("planned", "active", "waiting", "completed", "closed"),
    "research_execution_ids": IDS, "scope_dispositions": array(scope_disposition),
    "remaining_scope_ids": STRINGS, "waiting": WAIT, "completion_ref": EXACT,
    "closure_ref": EXACT, "followups": FOLLOWUPS,
}, ["id", "contract", "state", "research_execution_ids", "scope_dispositions", "remaining_scope_ids", "followups"],
    [condition("state", "waiting", require("waiting")),
     condition("state", "completed", require("completion_ref")),
     condition("state", "closed", require("closure_ref")),
     {"if": {"properties": {"state": {"enum": ["planned", "active", "completed", "closed"]}}},
      "then": forbid("waiting")}], "T")

register("activity", "3.2.1,19.5", "runtime/activities/{id}/record.json", {
    "id": ID, "activity_kind": enum(*EXECUTION_KINDS), "owner_ref": SUBJECT,
    "opened_at": TIME, "input_refs": REFS, "state": enum("ready", "working", "waiting", "finished"),
    "stage": enum("drafting", "selecting", "performing", "assessing", "planning", "reviewing",
                  "clarifying", "judging", "diagnosing", "checking_recovery", "interpreting",
                  "checking", "investigating", "initializing", "integrating", "transitioning", "migrating"),
    "assigned_execution_ids": IDS, "result_refs": REFS, "unresolved_refs": REFS,
    "waiting": WAIT, "followups": FOLLOWUPS, "execution_limit": POS, "review_lineage_id": ID,
}, ["id", "activity_kind", "owner_ref", "opened_at", "input_refs", "state", "stage",
    "assigned_execution_ids", "result_refs", "unresolved_refs", "followups"],
    [condition("state", "waiting", require("waiting")),
     condition("activity_kind", "identity_review", require("execution_limit", "review_lineage_id"))], "AC")

result_payloads = {
    "research_preparation": obj({"frontier_proposals": REFS, "task_proposals": REFS,
        "refinement_proposals": REFS, "exploration_consideration": S,
        "exploitation_consideration": S, "attempts_ref": ARTIFACT, "open_questions": STRINGS,
        "regenerate_after": TIME, "receiver_check_refs": REFS}),
    "task_contract_review": obj({"task_id": ID, "revision": POS,
        "items": array(FIELD_RESULT, 1), "verdict": APPROVAL, "validity_basis": BASIS}),
    "intent_interpretation": obj({"stage": enum("interpreting", "checking"),
        "purpose": enum("import", "delegation"), "verdict": APPROVAL,
        "unit_map": array(obj({"unit_id": S, "source_ref": EXACT, "anchor": S,
            "owner": S, "target_ref": LINK, "interpretation_ref": ARTIFACT})),
        "questions": REFS, "authority_refs": REFS, "validity_basis": BASIS,
        "repair_actions": array(obj({"finding_id": S, "action": S, "changed_refs": REFS}))}),
    "identity_review": obj({"outcome": {"const": "input_overflow"}, "proposal_ref": ARTIFACT,
        "measurement_ref": ARTIFACT}),
    "research_plan": obj({"plan_ref": ARTIFACT, "bound_contracts": array(obj({
        "task_id": ID, "revision": POS, "contract_ref": EXACT}))}),
    "research_work": obj({"bundle_refs": REFS, "scope_report": array(scope_disposition),
        "remaining_scope_ids": STRINGS, "wait_request": common("optional_wait")}),
    "supplemental_research": obj({"question_id": S, "answer_ref": ARTIFACT,
        "actual_scope": RANGES, "evidence_refs": REFS, "uncertainties": STRINGS}),
    "maintenance": obj({"operation": enum("initialization", "integration", "trust_transition", "migration"),
        "check_refs": REFS, "judgment_requests": REFS, "remaining_items": STRINGS}),
}
common_defs["optional_wait"] = {"oneOf": [obj({"kind": {"const": "none"}}),
    obj({"kind": {"const": "waiting"}, "wait": WAIT})]}
register("activity-result", "3.2.1,5.4,9.2.1,13.1,19.5", "runtime/artifacts/{bundle_id}/{path}", {
    "id": ID, "owner_activity_id": ID, "execution_id": ID, "kind": enum(*result_payloads),
    "input_manifest_ref": EXACT, "actual_scope": RANGES, "incidental_insights": REFS,
    "followups": FOLLOWUPS, "payload": {},
}, prefix="AR")["allOf"] = [
    condition("kind", kind, {"properties": {"payload": schema}})
    for kind, schema in result_payloads.items()]

process = obj({"pid": POS, "creation_filetime": {"type": "string", "pattern": r"^[0-9]+$"},
               "image_path": S, "job_id": ID, "handle_observation_ref": ARTIFACT})
end = optional({"kind": enum("output_accepted", "execution_incomplete", "cancelled", "start_failed"),
           "at": TIME, "cause": CAUSE, "actual_scope": RANGES, "remaining_scope": RANGES,
           "artifact_refs": REFS, "barrier_evidence_refs": REFS,
           "outstanding_reservation_ids": IDS, "next_owner": SUBJECT,
           "stop_reasons": array(obj({"provider_operation_id": ID,
               "stop_reason": enum("end_turn", "max_output", "context_overflow", "cancelled", "error")})),
           "overflow": obj({"component_tokens": array(obj({"component": S, "tokens": N}), 1), "limit": POS})},
           "overflow")
end["allOf"] = [{"if": {"properties": {"cause": {"properties": {"code": {"const": "context_overflow"}},
                                                  "required": ["code"]}}, "required": ["cause"]},
                 "then": require("overflow")}]
self_check = obj({"event_ids": array(ID, 1, True), "rule_revision": N,
    "value": enum("progress", "no_progress", "contract_mismatch"),
    "results": RANGES, "evidence_refs": REFS, "attempts_ref": ARTIFACT,
    "next_method": S, "method_difference": S, "submitted_at": TIME})
register("execution", "6,12,19.4", "runtime/executions/{id}/record.json", {
    "id": ID, "owner_activity_id": ID, "activity_kind": enum(*EXECUTION_KINDS),
    "stage": S, "actor_kind": enum("ai", "machine"), "profile_ref": EXACT,
    "input_manifest_ref": EXACT, "output_schema_id": S, "authority_refs": NONEMPTY_REFS,
    "output_phase": enum("initial", "judge", "answer", "organize"), "role_slot_id": S,
    "workspace": PATH, "state": enum("queued", "starting", "running", "stopping", "ended"),
    "paused_maintenance_authorization": common("paused_maintenance_authorization"),
    "created_at": TIME, "budget_kind": enum("work", "operations"),
    "operational_review_mode": enum("event_driven", "periodic"),
    "execution_deadline": TIME, "next_operational_review_at": TIME,
    "explicit_review_basis_ref": EXACT, "continuation_of": ID,
    "context_origin": obj({"kind": enum("fresh", "continued", "restored", "replacement"),
                            "execution_ids": IDS, "transcript_ref": ARTIFACT}),
    "task_id": ID, "task_revision": POS, "process": process,
    "provider_operation_ids": IDS, "reservation_ids": IDS, "checkpoint_refs": REFS,
    "stop_phase": enum("checkpointing", "terminating"), "stop_requested_at": TIME,
    "stop_checkpoint_deadline": TIME, "stop_cause": CAUSE,
    "self_check_revision": N, "self_check_rules": array(common("observation_rule"), 1),
    "observation_clock_anchor": TIME, "next_self_check_at": TIME,
    "self_checks": array(self_check), "end": end,
}, ["id", "owner_activity_id", "activity_kind", "stage", "actor_kind", "profile_ref",
    "input_manifest_ref", "output_schema_id", "authority_refs", "workspace", "state",
    "created_at", "provider_operation_ids", "reservation_ids", "checkpoint_refs"],
    [condition("actor_kind", "ai", require("budget_kind", "context_origin")),
     condition("actor_kind", "machine", {"allOf": [require("execution_deadline"),
             forbid("budget_kind", "context_origin", "operational_review_mode", "next_operational_review_at")]}),
     condition("budget_kind", "operations", {"allOf": [require("execution_deadline"),
             forbid("next_operational_review_at", "operational_review_mode")]}),
     condition("budget_kind", "work", {"allOf": [require("operational_review_mode"), forbid("execution_deadline")]}),
     condition("operational_review_mode", "periodic", require("next_operational_review_at")),
     condition("state", "stopping", require("stop_phase", "stop_requested_at", "stop_cause")),
     {"if": {"properties": {"state": {"enum": ["queued", "starting", "running", "ended"]}}},
      "then": forbid("stop_phase", "stop_checkpoint_deadline")},
     condition("stop_phase", "checkpointing", require("stop_checkpoint_deadline")),
     condition("state", "ended", require("end")),
     {"if": {"properties": {"state": {"enum": ["queued", "starting", "running", "stopping"]}}},
      "then": forbid("end")},
     condition("activity_kind", "research_work", require("task_id", "task_revision"))], "E")

register("artifact", "6.5,7.1,19.2", "runtime/artifacts/{id}/manifest.json", {
    "id": ID, "kind": enum("input", "output", "checkpoint", "evidence", "transcript"),
    "created_at": TIME, "producer_execution_id": ID, "files": array(FILE, 1),
    "origin_refs": REFS, "sealed": {"const": True}}, ["id", "kind", "created_at", "files", "origin_refs", "sealed"],
    prefix="AB")

listing_item = obj({"id": ID, "record_ref": EXACT, "title": S,
                    "description": {"type": "string", "pattern": r"^[^\r\n]*$"},
                    "detail_refs": REFS})
listing = optional({"snapshot_commit": OID, "scope": common("query_scope"),
    "total_count": N, "loaded_count": N, "truncated": BOOL, "items": array(listing_item),
    "order": enum("id", "sealed_random"),
    "shuffle_seed": HASH, "algorithm": {"const": "hmac-sort-v1"},
    "omitted_query": common("query_scope")}, "shuffle_seed", "algorithm")
listing["allOf"] = [condition("order", "sealed_random", require("shuffle_seed", "algorithm")),
                    condition("order", "id", forbid("shuffle_seed", "algorithm"))]
transcript_entry = optional({"sequence": N, "role": enum("system", "user", "assistant", "tool"),
                        "content_ref": ARTIFACT, "execution_id": ID,
                        "restore_form": enum("full", "reference"),
                        "reference": obj({"call": S, "arguments_ref": ARTIFACT, "size_bytes": N})}, "reference")
transcript_entry["allOf"] = [
    condition("role", "system", {"properties": {"restore_form": {"const": "full"}}}),
    condition("role", "assistant", {"properties": {"restore_form": {"const": "full"}}}),
    condition("role", "tool", {"properties": {"restore_form": {"const": "reference"}}}),
    condition("restore_form", "reference", require("reference")),
    condition("restore_form", "full", forbid("reference"))]
planning_input = optional({"candidate_listing": listing, "canon_listing": listing,
    "ongoing_refs": REFS, "recent_history": REFS, "preparation_history": REFS,
    "required_failure_refs": REFS, "configured_history_window": N, "actual_history_window": N,
    "truncation_permission_ref": EXACT,
    "component_tokens": array(obj({"component": S, "tokens": N}))}, "truncation_permission_ref")
register("input-manifest", "8,13.1,16.5,19.5", "runtime/artifacts/{bundle_id}/input-manifest.json", {
    "id": ID, "snapshot_commit": OID, "question": S, "scope": RANGES,
    "output_schema_id": S, "profile_ref": EXACT, "authority_refs": NONEMPTY_REFS,
    "common_documents": array(FILE, 2), "role_documents": array(FILE, 1),
    "governance_refs": REFS, "required_refs": REFS, "failure_refs": REFS,
    "read_scope": array(common("query_scope")),
    "provided_order": array(enum("common_documents", "role_documents", "governance", "transcript",
                                 "canon_listing", "candidate_listing", "ongoing", "required_failures",
                                 "recent_history", "preparation_history", "required_inputs", "question"), unique=True),
    "planning_input": planning_input, "transcript": array(transcript_entry),
    "transcript_complete": BOOL, "continuity_broken": BOOL,
    "continuity_break_cause": enum("permanent_loss", "context_overflow", "profile_replaced"),
    "continuity_failure_refs": REFS, "reference_read_refs": REFS,
    "token_count": N, "max_input_tokens": POS,
}, ["id", "snapshot_commit", "question", "scope", "output_schema_id", "profile_ref",
    "authority_refs", "common_documents", "role_documents", "governance_refs", "required_refs",
    "failure_refs", "read_scope", "provided_order", "reference_read_refs", "token_count", "max_input_tokens"], prefix="IM")

knowledge_base = {"id": ID, "type": enum("frontier", "evidence", "relation", "context", "memory", "kind_definition"),
    "title": S, "description": {"type": "string", "minLength": 1, "pattern": r"^[^\r\n]+$"},
    "lifecycle": LIFECYCLE, "origin_refs": NONEMPTY_REFS,
    "generated": obj({"by": {"type": "string", "pattern": r"^(?:human:|process:|execution:).+$"}, "at": TIME}),
    "sources": array(common("source")), "uncertainty_assessment": obj({
        "assessment": enum("unassessed", "assessed"), "items": STRINGS}),
    "subkind": S, "epistemic_status": enum("open", "supported", "challenged", "resolved", "refuted", "inactive"),
    "confirmed_scope": S, "evidence_refs": REFS, "selection_relevance": S,
    "source_refs": REFS, "related_refs": array(LINK), "from_ref": LINK, "to_ref": LINK,
    "assessment_refs": REFS, "formal_result_refs": REFS,
    "avoid_terms": STRINGS, "information_status": enum("fact", "inference", "heuristic", "hypothesis"),
    "scope": S, "excluded_scope": S, "family": enum("frontier", "relation"),
    "token": S, "meaning": S, "constraints": common("kind_constraints"),
    "external_rejection": optional({"actor": S, "at": TIME, "solution_basis": common("solution_basis"),
                                     "resolution_ref": EXACT}, "resolution_ref"),
    "replacement_refs": REFS, "withdrawal_reason_ref": EXACT}
common_defs["kind_constraints"] = optional({
    "allowed_epistemic_status": array(enum("open", "supported", "challenged", "resolved", "refuted", "inactive"), 1, True),
    "required_fields": STRINGS, "from_families": array(S, 1, True), "to_families": array(S, 1, True),
    "requires_evidence": BOOL, "requires_assessment": BOOL},
    "allowed_epistemic_status", "required_fields", "from_families", "to_families", "requires_evidence", "requires_assessment")
knowledge_common = ["id", "type", "title", "lifecycle", "origin_refs", "generated"]
knowledge_specific = {
    "frontier": ["subkind", "epistemic_status", "confirmed_scope", "evidence_refs", "selection_relevance"],
    "evidence": ["subkind", "source_refs", "confirmed_scope", "related_refs"],
    "relation": ["subkind", "from_ref", "to_ref", "evidence_refs"],
    "context": ["avoid_terms", "related_refs"],
    "memory": ["information_status", "scope", "excluded_scope", "source_refs"],
    "kind_definition": ["family", "token", "meaning", "constraints"],
}
register("knowledge", "7.3,19.3", "research/knowledge/{path}.md#frontmatter",
    knowledge_base, knowledge_common, [
        condition("type", kind, require(*fields)) for kind, fields in knowledge_specific.items()
    ] + [
        condition("type", "evidence", {"properties": {"subkind": enum("source", "observation", "computation", "argument", "hypothesis", "failure")}}),
        {"if": {"required": ["external_rejection"]}, "then": {"properties": {"type": {"const": "evidence"}, "subkind": {"const": "source"}}}},
        {"if": {"properties": {"type": {"const": "relation"},
                               "subkind": {"enum": ["solves", "refutes", "partially_addresses", "narrows_scope"]}},
                 "required": ["subkind"]},
         "then": {"required": ["assessment_refs", "formal_result_refs"],
                  "properties": {"assessment_refs": NONEMPTY_REFS, "formal_result_refs": NONEMPTY_REFS}}},
        {"if": {"required": ["uncertainty_assessment"], "properties": {"uncertainty_assessment": {
                    "properties": {"assessment": {"const": "unassessed"}}}}},
         "then": {"properties": {"uncertainty_assessment": {"properties": {"items": {"maxItems": 0}}}}}},
    ])

register("kind-definition", "7.3,19.3", "research/knowledge/{path}.md#frontmatter", {
    "id": ID, "type": {"const": "kind_definition"}, "title": S, "lifecycle": LIFECYCLE,
    "origin_refs": NONEMPTY_REFS, "generated": knowledge_base["generated"],
    "family": enum("frontier", "relation"), "token": S, "meaning": S,
    "constraints": common("kind_constraints")}, prefix="KD")

register("plan", "9,19.5", "runtime/artifacts/{bundle_id}/plan.json", {
    "id": ID, "activity_id": ID, "execution_id": ID, "input_manifest_ref": EXACT,
    "snapshot_commit": OID, "candidate_dispositions": array(obj({
        "task_id": ID, "revision": POS, "value": enum("selected", "not_selected", "not_assessable"),
        "reason": S, "information_status": enum("evidence", "inference", "hypothesis", "intuition", "random"),
        "uncertainty": S, "read_scope_refs": REFS})),
    "execution_requests": array(obj({"task_id": ID, "revision": POS, "execution_profile_id": ID,
                                      "reason": S})),
    "dispatch_order": IDS, "parallel_relations": array(obj({"task_ids": array(ID, 2, True), "reason": S})),
    "queued_cancellations": array(obj({"execution_id": ID, "reason": S})),
    "preparation_requests": REFS, "completion_assessments": REFS,
    "user_decision_requests": array(obj({"question_ref": ARTIFACT, "basis_refs": NONEMPTY_REFS})),
    "expectation_actual_comparison_ref": ARTIFACT, "exploration_consideration": S,
    "next_reconsideration": common("wake"), "consumed_event_ids": IDS}, prefix="PN")

register("integration", "10,19.6", "research/integrations/{id}.json", {
    "id": ID, "base_snapshot_commit": OID, "author_execution_ids": array(ID, 1, True),
    "changes": array(obj({"operation": enum("create", "revise", "withdraw", "delete"),
        "record_id": ID, "prior": common("prior_hash"), "candidate_ref": ARTIFACT}), 1),
    "authority_refs": NONEMPTY_REFS, "assessment_refs": REFS, "check_refs": NONEMPTY_REFS,
    "impact": array(obj({"target_ref": EXACT, "reason": S, "disposition": S,
                         "requires_independent_review": BOOL, "approval_refs": REFS})),
    "followups": FOLLOWUPS}, prefix="IN")
common_defs["prior_hash"] = {"oneOf": [obj({"kind": {"const": "absent"}}),
    obj({"kind": {"const": "present"}, "sha256": HASH})]}

declaration = obj({"name": S, "kind": enum("definition", "theorem", "proof", "relation"),
                   "type_sha256": HASH, "body_sha256": HASH, "source_ref": ARTIFACT, "anchor": S})
register("formal-result", "1.2,11.1,11.6,15,19.6", "research/formal/results/{id}.json", {
    "id": ID, "declarations": array(declaration, 1), "dependency_refs": REFS,
    "trust_environment_ref": EXACT, "source_manifest_ref": ARTIFACT,
    "kernel_check_ref": EXACT, "axiom_check_ref": EXACT,
    "formal_use": enum("active", "suspended", "historical"), "basis_refs": NONEMPTY_REFS}, prefix="K")

math_item = obj({"id": ID, "kind": enum("summary", "definition", "assumption", "statement", "quantification", "proof_step", "scope", "conclusion"),
    "anchor": S, "dependency_ids": IDS,
    "lean_coordinates": array(obj({"declaration": S, "coordinate_kind": enum("declaration", "binder", "subexpression", "lemma", "obligation"), "anchor": S}), 1),
    "quantifiers": array(obj({"id": S, "kind": enum("forall", "exists", "exists_unique"),
        "variable_anchor": S, "domain_item_id": ID, "depends_on": STRINGS,
        "declaration": S, "lean_anchor": S}))})
register("explanation", "11.1,19.6", "research/formal/explanations/{id}.json", {
    "id": ID, "revision": POS, "document_ref": ARTIFACT, "formal_result_refs": NONEMPTY_REFS,
    "math_items": array(math_item, 1), "summary_item_id": ID, "non_mathematical_anchors": STRINGS,
    "evidence": array(obj({"source_id": S, "artifact_ref": ARTIFACT, "anchors": STRINGS,
                          "purpose": enum("literature_transcription", "factual_support")})),
    "required_domains": STRINGS, "origin_refs": NONEMPTY_REFS}, prefix="EX")

role_slot = obj({"id": S, "perspective": S, "profile_ref": EXACT,
                 "scope_item_ids": IDS, "producer_execution_ids": IDS,
                 "context_origin_refs": REFS, "transcript_refs": REFS})
register("review-policy", "11.3,19.6", "research/governance/review-policies/{id}.json", {
    "id": ID, "revision": POS, "required_perspectives": array(obj({"name": S, "count": POS}), 3),
    "final_judges": {"type": "array", "items": role_slot, "minItems": 3, "maxItems": 3},
    "execution_limit": POS, "objection_round_limit": POS, "scope_rule_ref": ARTIFACT,
    "required_evidence": STRINGS, "independence_rules_ref": ARTIFACT,
    "approval_ref": EXACT}, prefix="RP")

issue = obj({"id": ID, "revision": POS, "lineage_id": ID, "round": POS,
    "author_slot_id": S, "answer_role_slot_id": S, "source_result_ref": EXACT,
    "claim_ref": ARTIFACT, "coordinates": STRINGS,
    "evidence_refs": REFS, "parent_issue_ids": IDS, "answer_refs": REFS,
    "judge_results": array(obj({"slot_id": S, "value": enum("approved", "rejected", "unresolved"),
                               "reason_ref": ARTIFACT}), 0),
    "state": enum("open", "approved", "rejected", "withdrawn", "unresolved"),
    "establishment_basis": enum("unanimous_approval", "none")})
register("issue-state", "8.3,11.3,11.4,19.6", "runtime/activities/{activity_id}/issues/{id}.json", {
    "id": ID, "review_lineage_id": ID, "proposal_ref": ARTIFACT, "proposal_revision": POS,
    "previous_proposal_ref": ARTIFACT, "repair_map_ref": ARTIFACT,
    "role_slots": array(role_slot, 1), "issues": array(issue),
    "executions_used": N, "execution_limit": POS, "reserved_organize_executions": N,
    "reserved_answer_executions": N,
    "reserved_final_executions": N, "scope_manifest_ref": ARTIFACT,
    "continuity_broken": BOOL, "continuity_break_cause": enum("permanent_loss", "context_overflow", "profile_replaced"),
    "continuity_evidence_refs": REFS,
}, ["id", "review_lineage_id", "proposal_ref", "proposal_revision", "role_slots", "issues",
    "executions_used", "execution_limit", "reserved_organize_executions",
    "reserved_answer_executions", "reserved_final_executions",
    "scope_manifest_ref", "continuity_broken", "continuity_evidence_refs"], prefix="IS")

register("assessment", "5.4,9.4,11,19.6", "research/formal/assessments/{id}.json", {
    "id": ID, "kind": enum("identity", "goal", "academic", "task_completion", "project_audit"),
    "target_refs": NONEMPTY_REFS, "policy_ref": EXACT, "input_manifest_ref": EXACT,
    "value": enum("match", "mismatch", "unresolved", "satisfied", "not_satisfied"),
    "project_value": S, "route": enum("initial_unanimous", "disputed", "direct"),
    "actual_scope": RANGES, "scope_complete": BOOL, "evidence_refs": NONEMPTY_REFS,
    "execution_ids": array(ID, 1, True), "disputed_findings": REFS, "remaining_questions": STRINGS,
    "effects": obj({"goal_solved": BOOL, "blocks_integration": BOOL, "blocks_external_action": BOOL}),
}, ["id", "kind", "target_refs", "policy_ref", "input_manifest_ref", "value", "route",
    "actual_scope", "scope_complete", "evidence_refs", "execution_ids", "disputed_findings",
    "remaining_questions", "effects"],
    [condition("kind", "identity", {"properties": {"value": ASSESSMENT}}),
     {"if": {"properties": {"kind": {"enum": ["goal", "academic", "task_completion", "project_audit"]}}},
      "then": {"properties": {"value": enum("satisfied", "not_satisfied", "unresolved")}}},
     condition("value", "match", {"properties": {"scope_complete": {"const": True}}})], "AS")

register("assessment-use", "11.8,19.6", "research/formal/uses/{id}.json", {
    "id": ID, "assessment_ref": EXACT, "state": USE, "changed_at": TIME,
    "reason_refs": NONEMPTY_REFS, "previous_use_ref": EXACT,
    "reassessment_ref": EXACT, "affected_refs": REFS,
}, ["id", "assessment_ref", "state", "changed_at", "reason_refs", "affected_refs"], prefix="AU")

register("operational-review", "12,19.4", "runtime/activities/{activity_id}/reviews/{id}.json", {
    "id": ID, "activity_id": ID, "execution_id": ID, "stage": enum("diagnosing", "checking_recovery"),
    "trigger_event_ids": array(ID, 1, True), "observation_refs": NONEMPTY_REFS,
    "diagnosis_ref": ARTIFACT, "actual_scope": RANGES, "uncertainties": STRINGS,
    "disposition": enum("continue", "repair", "resume_checkpoint", "restart", "revise_task", "close_task", "ask_user", "no_action"),
    "basis": BASIS, "next_review_at": {**TIME, "description": "For continue, required by the target execution's periodic mode. In event_driven mode, absence means no further reservation for the reviewed duty; a supplied time requires remaining uncertainty and diagnosis evidence. Check against the bound target execution."}, "recovery_approval_ref": EXACT,
    "checkpoint_ref": ARTIFACT, "followups": FOLLOWUPS,
    "recovery": obj({"path": enum("deterministic", "meaning_review"), "prior_execution_ref": EXACT,
        "input_manifest_ref": EXACT, "profile_ref": EXACT, "authority_refs": NONEMPTY_REFS,
        "external_action_refs": REFS, "scope": RANGES, "diagnosing_execution_id": ID}),
}, ["id", "activity_id", "execution_id", "stage", "trigger_event_ids", "observation_refs",
    "diagnosis_ref", "actual_scope", "uncertainties", "disposition", "basis", "followups"],
    prefix="OR")

register("decision", "13.1,19.3", "research/governance/decisions/{id}.json", {
    "id": ID, "question_ref": ARTIFACT, "answer_ref": ARTIFACT,
    "conversation_refs": REFS, "structured_value_schema_ref": EXACT,
    "structured_value_ref": ARTIFACT, "targets": NONEMPTY_REFS, "scope": S,
    "effective_at": TIME, "expires_at": TIME, "supersedes": REFS, "withdraws": REFS,
    "affected_refs": REFS, "import_check_refs": NONEMPTY_REFS,
    "lifecycle": LIFECYCLE,
}, ["id", "question_ref", "answer_ref", "conversation_refs", "structured_value_schema_ref",
    "structured_value_ref", "targets", "scope", "effective_at", "supersedes", "withdraws",
    "affected_refs", "import_check_refs", "lifecycle"], prefix="DC")

register("external-action", "13.3,19.4", "runtime/actions/{id}.json", {
    "id": ID, "execution_id": ID, "authority_refs": NONEMPTY_REFS,
    "request_ref": ARTIFACT, "request_sha256": HASH, "idempotency_key": S,
    "external_identifier": S, "state": enum("prepared", "confirmed", "failed", "unknown", "cancelled"),
    "attempts": array(obj({"attempt": POS, "prepared_at": TIME, "evidence_refs": REFS})),
    "evidence_refs": REFS, "retry_rule_ref": EXACT, "next_owner": SUBJECT,
    "reobserve": common("wake"),
}, ["id", "execution_id", "authority_refs", "request_ref", "request_sha256", "state",
    "attempts", "evidence_refs", "retry_rule_ref", "next_owner"], prefix="EA")

register("action-result", "3.2.1,10.3,13.2,16.3,19.7", "runtime/actions/results/{id}.json", {
    "id": ID, "request_id": ID, "input_sha256": HASH, "command": S,
    "state": enum("prepared", "applied", "rejected", "blocked", "failed"),
    "result_refs": REFS, "reason": CAUSE, "followups": FOLLOWUPS,
    "delegation": obj({"permission_ref": EXACT, "source_decision_ref": EXACT,
                       "case_ref": EXACT, "effect_ref": ARTIFACT,
                       "interpretation_ref": EXACT, "checking_ref": EXACT, "basis": BASIS}),
}, ["id", "request_id", "input_sha256", "command", "state", "result_refs", "reason", "followups"], prefix="AX")

register("runtime-event", "3.2.1,9.1,12.1.1,13.1.1,19.4", "runtime/events/{id}.json", {
    "id": ID, "event_seq": N, "kind": enum("activity_opened", "activity_finished", "execution_started",
        "execution_ended", "self_check_due", "self_check_received", "self_check_missed",
        "rules_changed", "rules_rejected", "tool_review_due", "permission_expired",
        "conversation_lost", "preparation_due", "exhaustion", "threshold_opened",
        "threshold_continued", "checkpointing_started", "checkpoint_received",
        "checkpoint_missed", "external_action_changed", "reservation_reconciled", "integration_applied"),
    "at": TIME, "owner": SUBJECT, "execution_id": ID, "basis_refs": REFS,
    "trigger_key": S, "consumed_by": IDS, "payload_ref": ARTIFACT,
}, ["id", "event_seq", "kind", "at", "owner", "basis_refs", "trigger_key", "consumed_by", "payload_ref"], prefix="EVT")

register("trust-environment", "15,19.6", "research/trust/{id}.json", {
    "id": ID, "state": enum("staging", "active", "superseded", "invalidated"),
    "allowed_axioms": array(enum("propext", "Quot.sound", "Classical.choice"), 3, True),
    "lean_source_ref": ARTIFACT, "lean_binary_ref": ARTIFACT,
    "toolchain_ref": ARTIFACT, "mathlib_source_ref": ARTIFACT, "mathlib_build_ref": ARTIFACT,
    "check_tool_refs": NONEMPTY_REFS, "reproduction_ref": ARTIFACT,
    "base_acceptance_ref": EXACT, "result_refs": REFS, "previous_environment_ref": EXACT,
    "transition_approval_ref": EXACT, "impact_refs": REFS,
}, ["id", "state", "allowed_axioms", "lean_source_ref", "lean_binary_ref", "toolchain_ref",
    "mathlib_source_ref", "mathlib_build_ref", "check_tool_refs", "reproduction_ref",
    "base_acceptance_ref", "result_refs", "transition_approval_ref", "impact_refs"], prefix="TE")

finding = obj({"rule_id": S, "path": S, "message": S})
register("machine-check", "16.3,19.8", "runtime/artifacts/{bundle_id}/checks/{path}.json", {
    "id": ID, "tool": S, "mode": S, "version": S, "sequence": N,
    "inputs": array(FILE), "actual_scope": STRINGS, "uninspected_scope": STRINGS,
    "verdict": enum("pass", "fail", "incomplete"), "failures": array(finding),
    "repairs": array(obj({"rule_id": S, "before_sha256": HASH, "after_sha256": HASH, "path": PATH})),
    "resolved": array(finding), "previous_check_ref": EXACT,
    "evidence_refs": REFS, "next_owner": SUBJECT,
}, ["id", "tool", "mode", "version", "sequence", "inputs", "actual_scope", "uninspected_scope",
    "verdict", "failures", "repairs", "evidence_refs", "next_owner"],
    [condition("verdict", "pass", {"properties": {"failures": {"maxItems": 0}, "uninspected_scope": {"maxItems": 0}}}),
     {"dependentRequired": {"resolved": ["previous_check_ref"], "previous_check_ref": ["resolved"]}}], "MC")

register("status", "9.4,16.6,19.8", "derived/status.json", {
    "id": ID, "snapshot_commit": OID, "generated_at": TIME,
    "health": enum("healthy", "degraded", "blocked", "incomplete"), "check_refs": NONEMPTY_REFS,
    "goal_status": enum("unsolved", "mathematically_solved"), "goal_reason": CAUSE,
    "academic_validation_status": enum("not_applicable", "externally_rejected", "completed", "active", "pending"),
    "academic_basis_refs": REFS, "work_refs": REFS, "waiting_refs": REFS,
    "resource_refs": REFS, "unsettled_reservation_refs": REFS, "decision_refs": REFS,
    "planning_input_refs": REFS, "observation_refs": REFS, "continuity_break_refs": REFS,
    "stop_checkpoint_refs": REFS, "resolved_counts": array(obj({"rule_id": S, "count": N})),
    "strongest_result_refs": REFS, "limitations": STRINGS, "next_actions": FOLLOWUPS}, prefix="ST")

register("migration", "14.5,19.8", "research/integrations/migrations/{id}.json", {
    "id": ID, "old_contract_ref": EXACT, "new_contract_ref": EXACT,
    "source_snapshot": OID, "source_manifest_ref": ARTIFACT, "transform_ref": ARTIFACT,
    "dry_run_check_refs": NONEMPTY_REFS, "meaning_changes_ref": ARTIFACT,
    "approval_ref": EXACT, "state": enum("proposed", "checked", "applied", "failed"),
    "corrects_migration_ref": EXACT, "remaining_items": STRINGS,
}, ["id", "old_contract_ref", "new_contract_ref", "source_snapshot", "source_manifest_ref",
    "transform_ref", "dry_run_check_refs", "meaning_changes_ref", "approval_ref", "state", "remaining_items"], prefix="MG")

RECORD_FAMILIES = tuple(SCHEMAS)
COMMANDS = {
    "init": ("user", "14.1", obj({"name": S, "storage_location": S,
        "source_files": array(obj({"source_path": S, "sha256": HASH}), 1),
        "initial_permission_ref": EXACT, "profile_ref": EXACT, "budget_ref": EXACT,
        "conversation_loss_policy": enum("pause", "continue_authorized")}),
        "bootstrap_only", "initializing_with_import_activity"),
    "run": ("user", "3.1,14.2", obj({"instance_id": ID, "permission_ref": EXACT}),
        "exclusive_lock_and_recovery", "engine_running"),
    "pause": ("user_or_stop_policy", "13.5", obj({"instance_id": ID, "cause_ref": EXACT,
        "immediate_all_actions": BOOL}), "stop_authority", "paused_and_stopping"),
    "resume": ("user_or_resume_permission", "13.5,14.2", obj({"instance_id": ID,
        "permission_ref": EXACT}), "recovery_and_resume_permission", "resume_lifecycle"),
    "status": ("user_or_authorized_execution", "16.6", obj({"snapshot_commit": OID}),
        "read_scope", "derived_status"),
    "query": ("authorized_execution", "8.2,8.4", optional({"snapshot_commit": OID,
        "space": enum("research", "runtime"), "family": enum(*RECORD_FAMILIES),
        "ids": IDS, "text_query": text(0), "relation_neighbors": IDS,
        "source_refs": REFS, "page_size": integer(1), "cursor": common("cursor")}, "cursor"),
        "fixed_snapshot_and_read_scope", "bounded_page"),
    "read": ("authorized_execution", "7.2,8.2", optional({"target": EXACT,
        "byte_range": obj({"start": N, "length": POS})}, "byte_range"),
        "reference_integrity_and_read_scope", "exact_bytes_or_explicit_range"),
    "record": ("producer", "7.3.1", {"oneOf": [
        obj({"mode": {"const": "allocate"}, "family": enum(*RECORD_FAMILIES)}),
        obj({"mode": {"const": "normalize"}, "family": enum(*RECORD_FAMILIES), "input_ref": ARTIFACT})]},
        "authorized_staging", "id_or_normalized_candidate"),
    "check": ("producer_or_engine", "16.3", obj({"mode": enum("schema", "codec", "reference",
        "state", "readiness", "observation", "identity", "integration_preview", "contract"),
        "input_refs": NONEMPTY_REFS, "snapshot_commit": OID}),
        "declared_check_scope", "machine_check_only"),
    "checkpoint": ("running_or_checkpointing_producer", "6.4.1,6.5", optional({
        "execution_id": ID, "files": array(FILE, 1), "progress_ref": ARTIFACT,
        "self_check": self_check, "next_rules": array(common("observation_rule"), 1)}, "self_check", "next_rules"),
        "running_or_bounded_write_scope", "immutable_checkpoint"),
    "submit": ("running_producer", "6.5", obj({"execution_id": ID, "files": array(FILE),
        "result_ref": ARTIFACT, "wait_request": common("optional_wait")}),
        "running_and_manifest_binding", "stopping_acknowledgement"),
    "decide": ("conversation_adapter", "13.1", obj({"question_ref": ARTIFACT,
        "answer_ref": ARTIFACT, "conversation_refs": NONEMPTY_REFS}),
        "authenticated_user_answer", "decision_or_interpretation_activity"),
    "apply": ("engine", "10.3", obj({"integration_ref": EXACT, "expected_snapshot": OID}),
        "current_basis_and_required_judgments", "atomic_state_publication"),
    "trust": ("engine", "15", obj({"operation": enum("prepare", "check", "transition", "invalidate"),
        "environment_ref": EXACT, "basis_refs": NONEMPTY_REFS}),
        "operation_specific_trust_evidence", "trust_activity_or_atomic_transition"),
    "recover": ("engine", "14.2", obj({"instance_id": ID, "profile_refs": NONEMPTY_REFS}),
        "exclusive_lock_and_readonly_integrity", "recovery_report_and_followups"),
    "migrate": ("engine", "14.5", obj({"migration_ref": EXACT, "dry_run": BOOL}),
        "paused_and_checked_conversion", "candidate_or_approved_transition"),
}
common_defs["cursor"] = obj({"snapshot_commit": OID, "query_sha256": HASH,
                             "last_record_id": ID})
caller = {"oneOf": [
    obj({"kind": {"const": "user"}, "conversation_id": ID}),
    obj({"kind": {"const": "execution"}, "execution_id": ID}),
    obj({"kind": {"const": "engine"}, "engine_id": ID})]}
register("command-request", "16.3,19.7", "transport", {
    "request_id": ID, "command": enum(*COMMANDS), "caller": caller, "payload": {},
})["allOf"] = [condition("command", name, {"properties": {"payload": values[2]}})
              for name, values in COMMANDS.items()]

response_results = {
    "init": obj({"instance_id": ID, "snapshot_commit": OID, "activity_ids": IDS}),
    "run": obj({"engine_id": ID, "snapshot_commit": OID, "recovery_ref": EXACT}),
    "pause": obj({"snapshot_commit": OID, "stopping_execution_ids": IDS,
                   "unsettled_reservation_ids": IDS}),
    "resume": obj({"snapshot_commit": OID, "lifecycle": enum("initializing", "active")}),
    "status": ref("status"),
    "query": optional({"snapshot_commit": OID, "total_count": N, "loaded_count": N,
                      "items": REFS, "next_cursor": common("cursor")}, "next_cursor"),
    "read": obj({"target": EXACT, "encoding": enum("utf8", "base64"), "content": text(0),
                 "content_sha256": HASH, "total_bytes": N, "start_byte": N, "returned_bytes": N}),
    "record": optional({"id": ID, "candidate_ref": ARTIFACT, "check_ref": EXACT}, "candidate_ref", "check_ref"),
    "check": ref("machine-check"),
    "checkpoint": obj({"checkpoint_ref": ARTIFACT, "snapshot_commit": OID,
                        "self_check_disposition": enum("received", "missed", "not_submitted"),
                        "rule_disposition": enum("accepted", "rejected", "not_submitted", "not_activated")}),
    "submit": obj({"acknowledged": {"const": True}, "state": {"const": "stopping"},
                    "snapshot_commit": OID}),
    "decide": {"oneOf": [obj({"kind": {"const": "decision"}, "decision_ref": EXACT}),
                          obj({"kind": {"const": "interpretation"}, "activity_id": ID})]},
    "apply": obj({"integration_id": ID, "snapshot_commit": OID}),
    "trust": optional({"activity_id": ID, "snapshot_commit": OID}, "activity_id"),
    "recover": obj({"report_ref": ARTIFACT, "snapshot_commit": OID,
                    "ready_for_dispatch": BOOL, "followup_activity_ids": IDS}),
    "migrate": obj({"dry_run": BOOL, "report_ref": ARTIFACT, "snapshot_commit": OID}),
}
error = obj({"code": enum("invalid_input", "basis_changed", "permission_missing", "capacity_unavailable",
        "context_overflow", "credential_unavailable", "integrity_failure", "unsupported",
        "tool_failure", "execution_incomplete"), "message": S, "findings": array(finding),
        "actual_scope": STRINGS, "uninspected_scope": STRINGS, "next_owner": SUBJECT})
register("command-response", "16.3,19.7", "transport", {
    "request_id": ID, "command": enum(*COMMANDS), "exit_code": {"enum": [0, 2, 3, 4, 5]},
    "result": {}, "error": error,
}, ["request_id", "command", "exit_code"], [
    condition("exit_code", 0, {"allOf": [require("result"), forbid("error")]}),
    {"if": {"properties": {"exit_code": {"enum": [2, 3, 4, 5]}}},
     "then": {"allOf": [require("error"), forbid("result")]}},
    *[{"if": {"properties": {"command": {"const": name}, "exit_code": {"const": 0}}},
       "then": {"properties": {"result": shape}}} for name, shape in response_results.items()],
])

# Single ownership: runtime owns operational lifecycle; instance owns goal facts.
inst = SCHEMAS["instance"]
del inst["properties"]["lifecycle"]
inst["required"].remove("lifecycle")
inst.pop("allOf")
# Knowledge is the five content families; kind-definition is its own composed family.
SCHEMAS["knowledge"]["properties"]["type"] = enum("frontier", "evidence", "relation", "context", "memory")
# A machine profile does not receive model-facing documents.
profile = SCHEMAS["execution-profile"]
profile["required"].remove("role_documents")
profile["allOf"][0]["then"]["required"].append("role_documents")
profile["allOf"][1]["then"]["allOf"][0]["not"]["anyOf"].append({"required": ["role_documents"]})
# Preparation's regeneration timestamp is conditional on no accepted contract.
prep = result_payloads["research_preparation"]
prep["required"].remove("regenerate_after")
# Observation periodic settings are absent in event-driven mode.
observation["required"].remove("periodic_interval")
observation["allOf"] = [condition("operational_review_mode", "periodic", require("periodic_interval")),
                       condition("operational_review_mode", "event_driven", forbid("periodic_interval"))]
# Staging trust environments may not have build receipts yet.
trust = SCHEMAS["trust-environment"]
for key in ("base_acceptance_ref", "kernel_check_ref"):
    if key in trust["required"]:
        trust["required"].remove(key)
trust["allOf"] = [
    {"if": {"properties": {"state": {"enum": ["active", "superseded"]}}},
     "then": require("base_acceptance_ref")}]

# Close the operator-specific observation language rather than accepting scalar bags.
observation_branches = []
for operation, fields in {
    "event_recorded": {"event_kind": S, "target_id": ID},
    "safe_boundary_recorded": {"event_kind": S, "target_id": ID},
    "counter_gte": {"counter_id": S, "source_ref": EXACT, "baseline": N, "threshold": POS},
    "iteration_gte": {"counter_id": S, "source_ref": EXACT, "baseline": N, "threshold": POS},
    "checkpoint_count_gte": {"execution_id": ID, "baseline": N, "threshold": POS},
    "active_duration_gte": {"execution_id": ID, "baseline_milliseconds": N, "threshold_milliseconds": POS},
    "wall_time_reached": {"at": TIME},
    "tool_call_completed": {"call_id": ID},
}.items():
    repeat = {"repeat_interval": POS} if operation in {
        "counter_gte", "iteration_gte", "checkpoint_count_gte", "active_duration_gte"} else {}
    observation_branches.append(optional({"id": S, "op": {"const": operation},
                                          "required_evidence": STRINGS, **fields, **repeat},
                                         "repeat_interval") if repeat else
                                obj({"id": S, "op": {"const": operation},
                                     "required_evidence": STRINGS, **fields}))
common_defs["observation_rule"] = {"oneOf": observation_branches}
SCHEMAS["execution"]["properties"]["context_origin"] = {"oneOf": [
    obj({"kind": {"const": "fresh"}}),
    obj({"kind": enum("continued", "restored", "replacement"),
         "execution_ids": array(ID, 1, True), "transcript_ref": ARTIFACT})]}
SCHEMAS["execution"]["allOf"].extend([
    condition("state", "queued", {"allOf": [forbid("process"),
        {"properties": {"provider_operation_ids": {"maxItems": 0}, "reservation_ids": {"maxItems": 0}}}]}),
    condition("state", "running", require("process")),
    {"if": {"properties": {"activity_kind": {"const": "research_work"}, "state": {"const": "running"}}},
     "then": require("self_check_revision", "self_check_rules", "observation_clock_anchor", "next_self_check_at")},
    {"if": {"properties": {"operational_review_mode": {"const": "event_driven"}},
            "required": ["next_operational_review_at", "operational_review_mode"]},
     "then": require("explicit_review_basis_ref")},
])
SCHEMAS["operational-review"]["allOf"] = [
    {"if": {"properties": {"disposition": {"enum": ["resume_checkpoint", "restart"]}}},
     "then": require("recovery")},
    condition("stage", "checking_recovery", {"allOf": [require("recovery"),
        {"properties": {"recovery": {"properties": {"path": {"const": "meaning_review"}}}}}]}),
]
knowledge_optional = ["description", "sources", "uncertainty_assessment", "replacement_refs", "withdrawal_reason_ref"]
extra_by_kind = {"frontier": [], "evidence": ["external_rejection"],
                 "relation": ["assessment_refs", "formal_result_refs"], "context": [], "memory": []}
for kind in extra_by_kind:
    allowed = set(knowledge_common + knowledge_optional + knowledge_specific[kind] + extra_by_kind[kind] + ["schema_version"])
    disallowed = set(SCHEMAS["knowledge"]["properties"]) - allowed
    SCHEMAS["knowledge"]["allOf"].append(condition("type", kind, forbid(*sorted(disallowed))))
SCHEMAS["knowledge"]["allOf"].append(condition("type", "memory", {"properties": {"source_refs": NONEMPTY_REFS}}))
for schema in [SCHEMAS["kind-definition"]]:
    schema["allOf"] = [
        condition("family", "frontier", {"properties": {"constraints": {
            "allOf": [require("allowed_epistemic_status", "required_fields"),
                      forbid("from_families", "to_families", "requires_evidence", "requires_assessment")]}}}),
        condition("family", "relation", {"properties": {"constraints": {
            "allOf": [require("from_families", "to_families", "requires_evidence", "requires_assessment"),
                      forbid("allowed_epistemic_status", "required_fields")]}}}),
    ]
SCHEMAS["activity"]["allOf"].append({
    "if": {"properties": {"state": {"enum": ["ready", "working", "finished"]}}},
    "then": forbid("waiting")})
STAGES = {
    "research_preparation": ["drafting"], "research_plan": ["selecting"],
    "research_work": ["performing"], "task_contract_review": ["assessing"],
    "identity_review": ["planning", "reviewing", "clarifying", "judging"],
    "goal_audit": ["assessing"], "operational_review": ["diagnosing", "checking_recovery"],
    "intent_interpretation": ["interpreting", "checking"],
    "supplemental_research": ["investigating"],
    "maintenance": ["initializing", "integrating", "transitioning", "migrating"],
}
for kind, stages in STAGES.items():
    for family in ("activity", "execution"):
        SCHEMAS[family]["allOf"].append(condition("activity_kind", kind, {"properties": {"stage": enum(*stages)}}))
SCHEMAS["explanation"]["properties"]["math_items"]["items"]["allOf"] = [
    condition("kind", "quantification", {"properties": {"quantifiers": {"minItems": 1}}}),
    {"if": {"properties": {"kind": {"enum": ["definition", "assumption", "statement", "proof_step", "scope", "conclusion"]}}},
     "then": {"properties": {"quantifiers": {"maxItems": 0}}}},
]
SCHEMAS["machine-check"]["allOf"].extend([
    condition("verdict", "fail", {"properties": {"failures": {"minItems": 1}}}),
    condition("verdict", "incomplete", {"properties": {"uninspected_scope": {"minItems": 1}}}),
])
type_prefixes = {"frontier": "F", "evidence": "EV", "relation": "R", "context": "CX", "memory": "MM"}
SCHEMAS["knowledge"]["x-type-prefixes"] = type_prefixes
for kind, prefix in type_prefixes.items():
    SCHEMAS["knowledge"]["allOf"].append(condition("type", kind,
        {"properties": {"id": {"pattern": "^" + prefix + "-"}}}))
allocation = COMMANDS["record"][2]["oneOf"][0]
allocation["properties"]["knowledge_type"] = enum(*type_prefixes)
allocation["allOf"] = [condition("family", "knowledge", require("knowledge_type")),
    {"if": {"properties": {"family": {"not": {"const": "knowledge"}}}},
     "then": forbid("knowledge_type")}]
formal = SCHEMAS["formal-result"]
formal["properties"]["publication_state"] = enum("candidate", "accepted")
formal["required"].append("publication_state")
for field in ("kernel_check_ref", "axiom_check_ref", "formal_use"):
    formal["required"].remove(field)
formal["allOf"] = [
    condition("publication_state", "accepted", require("kernel_check_ref", "axiom_check_ref", "formal_use")),
    condition("publication_state", "candidate", forbid("formal_use"))]
trust_required_active = list(SCHEMAS["trust-environment"]["properties"])
trust = SCHEMAS["trust-environment"]
trust["required"] = ["schema_version", "id", "state", "allowed_axioms", "lean_source_ref",
                     "toolchain_ref", "mathlib_source_ref", "transition_approval_ref", "impact_refs", "result_refs"]
trust["allOf"] = [{"if": {"properties": {"state": {"enum": ["active", "superseded"]}}},
                   "then": require(*[p for p in trust_required_active if p != "previous_environment_ref"])}]

register("proposal", "11.1,11.4,19.6", "runtime/artifacts/{bundle_id}/proposal.json", {
    "id": ID, "revision": POS, "author_execution_ids": array(ID, 1, True),
    "base_snapshot_commit": OID, "trust_environment_ref": EXACT,
    "formal_subject_refs": NONEMPTY_REFS, "explanation_ref": ARTIFACT,
    "source_manifest": array(FILE), "dependency_refs": REFS,
    "previous_proposal_ref": ARTIFACT, "repair_map_ref": ARTIFACT,
    "review_lineage_id": ID, "required_domains": STRINGS,
    "goal_claim_refs": REFS, "preflight_check_refs": REFS,
}, ["id", "revision", "author_execution_ids", "base_snapshot_commit", "trust_environment_ref",
    "formal_subject_refs", "explanation_ref", "source_manifest", "dependency_refs",
    "required_domains", "goal_claim_refs", "preflight_check_refs"],
    [{"if": {"properties": {"revision": {"minimum": 2}}},
      "then": require("previous_proposal_ref", "repair_map_ref", "review_lineage_id")}], "PR")
register("review-plan", "11.3,19.6", "runtime/artifacts/{bundle_id}/review-plan.json", {
    "id": ID, "proposal_ref": ARTIFACT, "review_lineage_id": ID,
    "planner_execution_id": ID, "policy_ref": EXACT,
    "role_slots": array(role_slot, 3),
    "required_domains": STRINGS, "domain_reasons_ref": ARTIFACT,
    "transcript_refs": REFS, "execution_limit": POS, "initial_execution_count": POS,
    "reserved_organize_executions": POS, "reserved_answer_executions": N,
    "reserved_final_executions": {"type": "integer", "minimum": 3},
    "input_measurement_ref": ARTIFACT,
}, ["id", "proposal_ref", "review_lineage_id", "planner_execution_id", "policy_ref",
    "role_slots", "required_domains", "domain_reasons_ref", "transcript_refs",
    "execution_limit", "initial_execution_count", "reserved_organize_executions", "reserved_answer_executions",
    "reserved_final_executions", "input_measurement_ref"], prefix="VP")
register("implementation-manifest", "14.5,16.5,19.1", "installed/implementation-manifest.json", {
    "id": ID, "implementation_commit": OID, "schema_registry_sha256": HASH,
    "tool_manifest_ref": ARTIFACT, "skill_documents": array(FILE, 2),
    "codec_profile": {"const": "do-math-codec/9"},
    "dependencies": array(obj({"name": S, "version": S}), 1),
    "okf_profile": obj({"version": {"const": "0.2"}, "spec_sha256": HASH,
                         "subset_ref": ARTIFACT}),
    "capability_evidence_refs": REFS}, prefix="IC")
# New auxiliary families are part of the same registry and record/query contract.
for command in ("record",):
    for branch in COMMANDS[command][2]["oneOf"]:
        branch["properties"]["family"] = enum(*[name for name, schema in SCHEMAS.items()
            if "id" in schema.get("properties", {}) and not schema["x-storage"].startswith("derived/")])
COMMANDS["query"][2]["properties"]["family"] = enum(*[name for name, schema in SCHEMAS.items()
    if "id" in schema.get("properties", {})])

RULES = [
    ("R01", "4.1", "sum(work_slots, operations_slots) <= total_slots; local execution constraints and every provider call constraint are reserved atomically.", ["V01", "V37", "V72"], "budget"),
    ("R02", "4.2", "ended releases only proved local resources; unknown provider reservations survive execution termination.", ["V10", "V76", "V77"], "reservation"),
    ("R03", "4.5", "confirmed_consumed + returned <= reserved; settlement requires evidence; hard limits require enforceable upper bounds.", ["V56", "V57", "V58"], "reservation"),
    ("R04", "5.3", "At most one non-ended research_work request per task, including queued; completed/closed require all owned research executions ended.", ["V45", "V46"], "task"),
    ("R05", "5.5,12.4", "A contract revision applies only after previous research executions ended and independent approval exists; remaining_scope cannot waive contract obligations. Termination without changing the contract preserves its revision and requires the designated completion or closure basis, scope disposition and ended research executions; operational review does not replace these judgments with contract rewriting.", ["V55", "V69", "V70", "V224"], "task"),
    ("R06", "5.7", "Evaluate all AST branches at one snapshot; errors dominate true/false; missing dynamic records are false, broken declared artifact refs are errors.", ["V163", "V164", "V165"], "occurrence"),
    ("R07", "6.2", "Only documented execution transitions; stopping phases only checkpointing -> terminating; ended is immutable.", ["V07", "V11", "V39"], "execution"),
    ("R08", "6.3", "No substantive action before running authority; all startup reservations including bounded finishing usage are present.", ["V08", "V09", "V13", "V167"], "execution"),
    ("R09", "6.4.1", "Stopping checkpoint authority is bounded in time/tools/paths/usage; immediate stop, expiry or integrity loss skips it.", ["V155", "V156", "V157", "V158", "V185"], "execution"),
    ("R10", "6.5", "Submission acknowledgement is not output acceptance; bytes are collected after the termination barrier and compared to the announced manifest.", ["V43", "V11"], "execution"),
    ("R11", "7.1", "The initial state commit has no parent; every later state commit has exactly its preceding state as parent and contains research/runtime; runtime-only changes preserve research tree; artifacts cannot change or disappear.", ["V14", "V15", "V42", "V65", "V67", "V197"], "state"),
    ("R12", "7.2", "Exact refs resolve to preserved bytes at the named snapshot/bundle; tree refs are same-space structural only and never judgment/permission inputs.", ["V41", "V54"], "reference"),
    ("R13", "7.2.1", "Clock rollback or restart never grants a fresh deadline; expired events are merged once and permissions rechecked.", ["V66", "V79"], "time"),
    ("R14", "7.3,7.3.2", "Record family/subkind/endpoint constraints and assessment dependencies are checked together; body mentions create no authority relation. Installed relation templates have no active instance identity; mathematical kinds require formal-result and assessment evidence.", ["V82", "V85", "V86", "V87", "V179", "V193"], "knowledge"),
    ("R15", "8.1", "Mandatory common/role/governance text, pending failures and issues are present before judgment; required exact inputs cannot be replaced by summaries; stable components precede per-round components; governance or common text that cannot fit escalates to the user.", ["V48", "V103", "V129", "V161", "V180", "V204"], "input"),
    ('R16', '8.3', 'Same review slot receives every preserved public assistant response in full, including the final response not retransmitted to a model; retransmission of one conversation entry is not a new entry. Tool-result bodies and prior proposals uniformly become exact references. After permitted reduction, common-document overflow escalates first; proposal overflow excludes restored dialogue and closes unresolved; residual restoration overflow escalates. Accumulation permits one recovery before escalation; replacement requires recorded user authority.', ['V144', 'V145', 'V146', 'V166', 'V201', 'V202', 'V208', 'V209', 'V210', 'V211', 'V212', 'V214', 'V218', 'V222'], 'input'),
    ("R17", "8.5", "Both listings are supplied in full when they fit; history windows shrink first; if the listings still overflow the engine escalates to the user without truncating; truncation happens only under a recorded permission whose closed truncation fields name the lists, order and activity kinds, with snapshot population/counts and retrievable omissions.", ["V18", "V118", "V119", "V127", "V141", "V160", "V178", "V206", "V207", "V213"], "listing"),
    ("R18", "9.1", "Preparation/selection have one open activity each; opened_at anchors recurrence; only consumed input events advance cursors.", ["V78", "V79", "V130", "V131", "V172", "V173"], "activity"),
    ("R19", "9.2.1", "Selector is not in candidate author_execution_ids and does not resume/fork author context; prepared tasks do not wait for unrelated reviews.", ["V123", "V125"], "independence"),
    ("R20", "9.3", "Exactly one disposition per supplied candidate; dispositions name a listed task_id/revision and the engine binds exact refs in the activity result without editing plan bytes; a plan cut at max output is a receipt failure that escalates without retry and is not a selection failure; sum requests per shared execution constraint respects its cap.", ["V120", "V183", "V205"], "plan"),
    ("R21", "9.4", "Academic state uses exact current solution/requirements and unresolved external rejection; old completed work never silently carries to changed bases.", ["V97", "V98", "V99", "V100"], "academic"),
    ("R22", "10.3", "Apply only declared changes to latest research and latest runtime; semantic merge is AI-owned; long checks rerun if their input closure changes.", ["V42", "V67", "V181"], "integration"),
    ('R23', '11.3', 'Three basic perspectives plus required domains and source fidelity; every reviewer reads the full proposal. Only the proposal-overflow branch defined in 8.3 closes unresolved for restructuring; restored dialogue is never omitted from actual review input. Restructure an ongoing same obligation by contract revision, or create a new task after a completed/closed author task. Planners never split proposals.', ['V19', 'V44', 'V47', 'V90', 'V177', 'V219', 'V222'], 'review'),
    ("R24", "11.4", "New proposal versions receive all new semantic judgments; same version/scope/input may retain other completed slots.", ["V62", "V139", "V142", "V143"], "review"),
    ("R25", "11.4.1", "Unanimous approved establishes an objection; final split/unresolved stays unresolved; last unanimous rejected closes without new response.", ["V136", "V147", "V149", "V170"], "review"),
    ('R26', '11.3.1,11.4', 'Count each AI execution owned by the review or its descendant activities once, including ended supplements, queued requests, failed starts, cancellations and retries; exclude machine executions. Check ownership completeness and cycles against one snapshot. Publish child assignment, parent count and consumed mandatory reserve atomically. Resolve the exact policy: one judging round reserves no answers and three judges; two or more reserve at least N answers and six judges. Protect the remaining mandatory allocations.', ['V20', 'V63', 'V137', 'V148', 'V190', 'V191', 'V216', 'V217'], 'review'),
    ("R27", "11.5", "All completed match => match; disputed path unanimous mismatch => mismatch; disagreement or incomplete scope => unresolved with findings retained.", ["V21", "V64", "V91", "V92"], "review"),
    ("R28", "11.8", "Only actual assessment dependencies suspend. Revalidate the original assessment's kind, value, basis and effects to restore use; confirmed error in that assessment withdraws it. New positive/negative values alone imply neither outcome. Unresolved meta-review remains suspended; independent explanations and formally valid results remain.", ["V22", "V23", "V27", "V198", "V199"], "assessment"),
    ("R29", "12.1.1", "Valid self-check resets maximum interval anchor; retransmission/rule-only change does not; old obligations and no-progress history survive rule changes.", ["V134", "V152", "V153", "V154", "V169", "V175", "V176", "V187"], "observation"),
    ('R30', '12.1.1', 'The self-check deadline is due time plus window only when both tool and provider calls are absent; otherwise it is the first confirmed safe boundary plus window, or unset before that boundary. Response must also precede the next research action. Independent call review and machine stop still apply.', ['V135', 'V168', 'V200'], 'observation'),
    ("R31", "12.1,12.2,12.3,12.4", "One open operational review per execution; valid progress does not cancel explicitly scheduled review or periodic duty. Bind a continue result to the actual target execution: periodic requires the next review time; event_driven reserves a further review only for remaining uncertainty with diagnosis evidence. If the reviewed duty is complete and no further review is needed, clear that reservation while preserving unprocessed duties and checking current premises.", ["V133", "V150", "V151", "V223"], "observation"),
    ("R32", "13.1", "Exact user approval requires no universal second confirmation; newly interpreted scope requires checking and user decision.", ["V28", "V101"], "decision"),
    ('R33', '13.1.1', 'Repeated-work holds follow lineage and explicit continue decisions. Proposal and contract revision thresholds count current revision minus the revision bound by the latest explicit continue decision, or zero as the initial baseline; immutable revision numbers never reset. Existing holds and total limits remain. Proposal and contract continuation cannot use case delegation; overflow escalations and capacity shortages are not selection failures.', ['V174', 'V184', 'V205', 'V220'], 'threshold'),
    ("R34", "13.2", "Case approval is not future delegation; independent blinded checking and current original authority are required for semantic reuse.", ["V29", "V113", "V114", "V115", "V116", "V117"], "decision"),
    ("R35", "13.3", "Persist preparation before external action; unknown cannot be blindly resent; cancelled requires proof not invoked; partial effects are unknown.", ["V30", "V52", "V53", "V71", "V108"], "external"),
    ("R36", "13.5", "Pause preserves resume_lifecycle including initializing; queued ends without reservation and stopping remains visible until barrier.", ["V04", "V32", "V39", "V40"], "lifecycle"),
    ("R37", "14.2", "Read-only integrity check precedes new engine_id; reconcile actual local/remote effects without new model inference.", ["V49", "V57", "V75"], "recovery"),
    ("R38", "15", "One active trust environment; transition freezes new K, validates full target set, and preserves old valid environment on failure.", ["V34", "V110"], "trust"),
    ('R39', '16.1,16.1.1', 'Actual capability evidence is mandatory; fixture success is not proof of input injection, isolation or remote termination. Transcript-restoring adapters must disable and report compaction and preserve outputs. A Windows root is suspended and already a Job member at creation, before identity persistence; engine loss in that gap must still terminate it. Authority precedes resume and termination is observed. Unsupported creation paths cannot activate.', ['V33', 'V61', 'V106', 'V140', 'V194', 'V203'], 'adapter'),
    ("R40", "16.3", "Same request ID and canonical input => previous result; different input => rejection; identical checker/input disagreement is tool failure. Repair aggregation selects the latest history_window sealed role outputs by event_seq, breaking same-event ties by bundle ID and path bytes, and deduplicates their check records regardless of integration success. A zero window does not suppress mandatory current failures.", ["V12", "V104", "V182", "V221"], "command"),
    ("R41", "14.1", "initializing -> active requires complete activation evidence: approved governance, valid references, operations capacity, active trust and recovery.", ["V08", "V49"], "lifecycle"),
    ("R42", "3.2.1,5.3", "waiting may resume only after its recorded wake condition resolves; a task additionally requires a committed new research request.", ["V04", "V45", "V112"], "waiting"),
    ("R43", "11.3.2,16.5", "The assigned execution fixes review-result phase and role slot; validate the output against that exact assignment as well as its schema. Organize/answer never authorize a semantic verdict.", ["V192"], "review"),
    ("R44", "11.1,11.7,17.3.1", "Quantifier order and witness dependencies are semantic obligations. A false formal statement without a valid proof stops at the preliminary gate and is not evidence of identity-review detection. Test the identity gate with a valid formal proof paired with both a faithful explanation and a quantifier-mismatched explanation. A counterexample must meet every hypothesis and violate the conclusion; goal satisfaction follows the charter, not merely a proof of excluded middle.", ["V195", "V196", "V225"], "mathematics"),
    ("R45", "8.3,16.2", "A profile used for transcript restoration has compaction disabled with evidence; an overflowing call fails without compaction and the execution ends execution_incomplete with cause context_overflow and measured components; reference-form transcript entries lie within the execution's read scope.", ["V201", "V203", "V208"], "input"),
    ('R46', '5.5,13.1.1', 'Contract revision numbers increase from 1. Threshold usage subtracts the revision named by the last explicit continuation decision, with zero before any such decision. With limit 3, continuation at revision 3 allows revisions 4 through 6 and holds authoring of 7. Existing holds, lineage and total limits survive; other tasks continue.', ['V215', 'V220'], 'threshold'),
    ('R47', '5.2,9.3,19.5', 'A task contract fixes a nonempty allowed profile set; a research request selects exactly one listed profile. Current applicability is checked for the selected profile without invalidating independent listed profiles. A plan names selected profile IDs, dispatch order and queued cancellation reasons; the engine binds exact refs without rewriting plan meaning.', ['V68', 'V183', 'V231', 'V232', 'V236'], 'plan'),
    ('R48', '11.1,11.3.2,11.4.1,19.5,19.6', 'An explanation summary names one stable explanation item and canon listing returns that verified summary with exact links. Judge new findings are distinct from verdicts; each issue preserves its source result and names an eligible answer role slot.', ['V226', 'V227', 'V229', 'V237'], 'review'),
    ('R49', '12.1.1,19.4', 'Only numeric observation operators may carry a positive repeat interval. Each event records the consumed threshold or range; retransmission and rule replacement do not consume it again.', ['V175', 'V176', 'V228'], 'observation'),
    ('R50', '12.4,13.5.1,14.5,19.4', 'A paused instance permits only an approved maintenance procedure with bound target, scope and authority. Deterministic recovery applies directly; unresolved recovery meaning goes to a separate checking_recovery execution, and a renewed stop preserves the latest state.', ['V235', 'V238', 'V239', 'V240', 'V241', 'V242'], 'recovery'),
    ('R51', '16.3,19.5', 'Generators bind only determined execution metadata and expand an explicit remainder disposition over the fixed candidate population. They reject ambiguous targets, omissions, duplicates and out-of-population entries; machine checks preserve generator inputs, outputs, hashes and rules.', ['V181', 'V182', 'V221', 'V234'], 'command'),
    ('R52', '1.5,7.3.1,8.4,10.1,10.4,19.3,19.5', 'Knowledge records preserve source, scope, information status, relation direction and current assessment use. Preparation, selection, partial results, import, recovery and migration preserve the actual reused basis and next owner; links alone do not establish mathematical implication or research efficacy.', ['V243', 'V244', 'V245', 'V246', 'V247', 'V248', 'V249', 'V250', 'V251', 'V252', 'V253', 'V254'], 'knowledge'),
]
RULES = [(rid, section, statement + (" Settled requires confirmed_consumed + returned == reserved." if rid == "R03" else ""),
          vectors, domain) for rid, section, statement, vectors, domain in RULES]

TRANSITIONS = {
    "execution": {"initial": "queued", "terminal": ["ended"], "edges": [
        ["queued", "starting", "R08"], ["queued", "ended", "R07"],
        ["starting", "running", "R08"], ["starting", "stopping", "R07"],
        ["running", "stopping", "R09"], ["stopping", "ended", "R02"]]},
    "activity": {"initial": "ready", "terminal": ["finished"], "edges": [
        ["ready", "working", "R18"], ["working", "working", "R18"],
        ["ready", "waiting", "R04"], ["working", "waiting", "R04"],
        ["waiting", "ready", "R42"], ["ready", "finished", "R04"],
        ["working", "finished", "R04"], ["waiting", "finished", "R04"]]},
    "task": {"initial": "planned", "terminal": ["completed", "closed"], "edges": [
        ["planned", "active", "R04"], ["planned", "waiting", "R04"],
        ["active", "waiting", "R04"], ["waiting", "active", "R42"],
        *[[state, target, "R05"] for state in ["planned", "active", "waiting"]
          for target in ["completed", "closed"]]]},
    "external-action": {"initial": "prepared", "terminal": ["confirmed", "failed", "cancelled"], "edges": [
        ["prepared", "confirmed", "R35"], ["unknown", "confirmed", "R35"],
        ["prepared", "failed", "R35"], ["unknown", "failed", "R35"],
        ["prepared", "cancelled", "R35"], ["unknown", "cancelled", "R35"],
        ["prepared", "unknown", "R35"], ["unknown", "prepared", "R35"]]},
    "assessment-use": {"initial": "active", "terminal": ["withdrawn"], "edges": [
        ["active", "suspended", "R28"], ["suspended", "active", "R28"],
        ["suspended", "withdrawn", "R28"]]},
    "lifecycle": {"initial": "initializing", "terminal": [], "edges": [
        ["initializing", "active", "R41"], ["initializing", "paused", "R36"],
        ["active", "paused", "R36"], ["paused", "active", "R36"],
        ["paused", "initializing", "R36"]]},
}

# Corrections justified by the independent review and author counterexamples.
SCHEMAS["assessment"]["allOf"].append(condition("value", "satisfied",
    {"properties": {"scope_complete": {"const": True}}}))
SCHEMAS["task"]["allOf"].extend([
    condition("state", "completed", forbid("closure_ref")),
    condition("state", "closed", forbid("completion_ref")),
    {"if": {"properties": {"state": {"enum": ["planned", "active", "waiting"]}}},
     "then": forbid("completion_ref", "closure_ref")},
])
SCHEMAS["activity"]["allOf"].extend([
    condition("state", "working", {"properties": {"assigned_execution_ids": {"minItems": 1}}}),
    condition("state", "finished", {"properties": {"result_refs": {"minItems": 1}}}),
])
prep = result_payloads["research_preparation"]
prep["properties"]["observed_at"] = TIME
prep["required"].extend(["observed_at", "regenerate_after"])
prep["$comment"] = "Producer supplies a fallback future timestamp; only the receiver's actual empty outcome activates the exhaustion guard."
planning_input["allOf"] = [
    {"if": {"anyOf": [{"properties": {"candidate_listing": {"properties": {"truncated": {"const": True}}}}},
                      {"properties": {"canon_listing": {"properties": {"truncated": {"const": True}}}}}]},
     "then": require("truncation_permission_ref")},
]
candidate_view = optional({
    "revision": POS, "title": S,
    "description": {"type": "string", "minLength": 1, "pattern": r"^[^\r\n]+$"},
    "question": S, "scope": array(RANGE, 1), "excluded_scope": RANGES,
    "expected_research_change": S,
    "work_class": enum("research_production", "academic_validation"),
    "basis_ids": IDS, "review_status": enum("absent", "approved", "revision_required", "unresolved"),
    "profile_availability": array(obj({"profile_id": ID, "currently_usable": BOOL}), 1),
}, "description")
candidate_refs = optional({"record_ref": EXACT, "basis_refs": NONEMPTY_REFS, "review_ref": EXACT,
                           "profile_refs": NONEMPTY_REFS, "author_execution_ids": array(ID, 1, True)}, "review_ref")
candidate_item = obj({"id": ID, "view": candidate_view, "refs": candidate_refs})
candidate_item["allOf"] = [
    {"if": {"properties": {"view": {"properties": {"review_status": {"const": "absent"}}, "required": ["review_status"]}}},
     "then": {"properties": {"refs": forbid("review_ref")}}},
    {"if": {"properties": {"view": {"properties": {"review_status": {"enum": ["approved", "revision_required", "unresolved"]}}, "required": ["review_status"]}}},
     "then": {"properties": {"refs": require("review_ref")}}}]
canon_view = obj({
    "declaration_kind": enum("definition", "theorem", "proof", "relation"),
    "declaration_names": array(S, 1, True),
    "explanation_states": array(obj({"assessment_value": ASSESSMENT, "use_state": USE})),
    "valid_explanation_available": BOOL, "summary": S, "recently_changed": BOOL,
})
canon_refs = obj({
    "record_ref": EXACT,
    "explanation_links": array(obj({"explanation_ref": EXACT, "assessment_ref": EXACT,
        "use_ref": EXACT, "summary_item_id": ID, "use_state": USE, "assessment_value": ASSESSMENT})),
    "change_refs": REFS,
})
canon_item = obj({"id": ID, "view": canon_view, "refs": canon_refs})
candidate_listing = copy.deepcopy(listing)
candidate_listing["properties"]["items"] = array(candidate_item)
canon_listing = copy.deepcopy(listing)
canon_listing["properties"]["items"] = array(canon_item)
planning_input["properties"]["candidate_listing"] = candidate_listing
planning_input["properties"]["canon_listing"] = canon_listing
planning_input["properties"]["actual_preparation_history_window"] = N
SCHEMAS["input-manifest"]["properties"]["activity_kind"] = enum(*EXECUTION_KINDS)
SCHEMAS["input-manifest"]["required"].append("activity_kind")
SCHEMAS["input-manifest"]["allOf"] = [
    {"if": {"properties": {"activity_kind": {"enum": ["research_preparation", "research_plan"]}}},
     "then": require("planning_input")},
    condition("activity_kind", "research_preparation",
        {"properties": {"planning_input": require("actual_preparation_history_window")}}),
    {"if": {"properties": {"activity_kind": {"not": {"enum": ["research_preparation", "research_plan"]}}}},
     "then": forbid("planning_input")},
    condition("continuity_broken", True, require("continuity_break_cause")),
    condition("continuity_broken", False, forbid("continuity_break_cause")),
]
SCHEMAS["input-manifest"]["properties"]["common_documents"]["allOf"] = [
    {"contains": {"properties": {"path": {"pattern": r"(?:^|/)SKILL\.md$"}}, "required": ["path"]},
     "minContains": 1, "maxContains": 1},
    {"contains": {"properties": {"path": {"pattern": r"(?:^|/)GLOSSARY\.md$"}}, "required": ["path"]},
     "minContains": 1, "maxContains": 1},
]
review_plan = SCHEMAS["review-plan"]
review_plan["properties"]["proposal_item_ids"] = array(ID, 1, True)
review_plan["properties"]["conclusion_dependencies"] = array(obj({"conclusion_id": ID, "dependency_item_ids": IDS}))
review_plan["properties"]["final_judge_slot_ids"] = {"type": "array", "items": S, "minItems": 3, "maxItems": 3, "uniqueItems": True}
review_plan["required"].extend(["proposal_item_ids", "conclusion_dependencies", "final_judge_slot_ids"])
policy_judges = SCHEMAS["review-policy"]["properties"]["final_judges"]
policy_judges["items"] = obj({"id": S, "perspective": enum("objection_establishment", "objection_rebuttal", "context_comparison"),
                              "profile_ref": EXACT, "qualification_ref": ARTIFACT})
issue_schema = SCHEMAS["issue-state"]
issue_schema["properties"]["judge_slot_ids"] = {"type": "array", "items": S, "minItems": 3, "maxItems": 3, "uniqueItems": True}
issue_schema["properties"]["review_plan_ref"] = EXACT
issue_schema["required"].extend(["judge_slot_ids", "review_plan_ref"])
issue_schema["allOf"] = [condition("continuity_broken", True, require("continuity_break_cause")),
                         condition("continuity_broken", False, forbid("continuity_break_cause"))]
record_families = COMMANDS["record"][2]["oneOf"][0]["properties"]["family"]
record_results = []
for mode in ("allocate", "normalize"):
    fields = {"mode": {"const": mode}, "family": record_families, "id": ID, "knowledge_type": enum(*type_prefixes)}
    if mode == "normalize":
        fields.update(candidate_ref=ARTIFACT, check_ref=EXACT)
    shape = optional(fields, "knowledge_type")
    shape["allOf"] = [condition("family", "knowledge", require("knowledge_type")),
        {"if": {"properties": {"family": {"not": {"const": "knowledge"}}}},
         "then": forbid("knowledge_type")}]
    for family, schema in SCHEMAS.items():
        if schema.get("x-id-prefix"):
            shape["allOf"].append(condition("family", family, {"properties": {
                "id": {"pattern": "^" + schema["x-id-prefix"] + "-"}}}))
    for kind, prefix in type_prefixes.items():
        shape["allOf"].append(condition("knowledge_type", kind, {"properties": {"id": {"pattern": "^" + prefix + "-"}}}))
    record_results.append(shape)
response_results["record"] = {"oneOf": record_results}
for clause in SCHEMAS["command-response"]["allOf"]:
    if clause.get("if", {}).get("properties", {}).get("command", {}).get("const") == "record":
        clause["then"]["properties"]["result"] = response_results["record"]

objection_proposal = obj({"id": ID, "revision": POS, "lineage_id": ID, "author_slot_id": S,
    "claim_ref": ARTIFACT, "coordinates": array(S, 1), "evidence_refs": NONEMPTY_REFS,
    "parent_issue_ids": IDS})
register("review-result", "11.3,11.4,11.4.1,19.6", "runtime/artifacts/{bundle_id}/review-result.json", {
    "id": ID, "owner_activity_id": ID, "execution_id": ID, "review_lineage_id": ID,
    "proposal_ref": ARTIFACT, "role_slot_id": S, "input_manifest_ref": EXACT,
    "phase": enum("initial", "judge", "answer", "organize"),
    "actual_item_ids": IDS, "scope_complete": BOOL, "evidence_refs": REFS,
    "remaining_questions": STRINGS, "verdict": ASSESSMENT,
    "objections": array(objection_proposal),
    "new_findings": array(objection_proposal),
    "objection_verdicts": array(obj({"objection_id": ID, "revision": POS,
        "value": enum("approved", "rejected", "unresolved"), "reason_ref": ARTIFACT,
        "evidence_refs": NONEMPTY_REFS})),
    "answers": array(obj({"objection_id": ID, "revision": POS,
        "action": enum("strengthen", "narrow", "split", "add", "withdraw"),
        "statement_ref": ARTIFACT, "successor_objection_ids": IDS, "evidence_refs": REFS})),
    "organization": obj({"issue_refs": REFS, "answer_requests": REFS, "supplement_requests": REFS}),
}, ["id", "owner_activity_id", "execution_id", "review_lineage_id", "proposal_ref",
    "role_slot_id", "input_manifest_ref", "phase", "actual_item_ids", "scope_complete",
    "evidence_refs", "remaining_questions"], [
        condition("phase", "initial", {"allOf": [require("verdict", "objections"), forbid("objection_verdicts", "answers", "organization")]}),
        condition("phase", "judge", {"allOf": [require("verdict", "objection_verdicts", "new_findings"), forbid("objections", "answers", "organization")]}),
        {"if": {"properties": {"phase": {"not": {"const": "judge"}}}}, "then": forbid("new_findings")},
        condition("phase", "answer", {"allOf": [require("answers"), forbid("verdict", "objections", "objection_verdicts", "organization")]}),
        condition("phase", "organize", {"allOf": [require("organization"), forbid("verdict", "objections", "objection_verdicts", "answers")]}),
        condition("verdict", "match", {"properties": {"scope_complete": {"const": True}, "remaining_questions": {"maxItems": 0}, "objections": {"maxItems": 0}}}),
        {"if": {"properties": {"phase": {"const": "initial"}, "verdict": {"const": "mismatch"}}, "required": ["verdict"]},
         "then": {"properties": {"objections": {"minItems": 1}}}},
    ], "RV")
for shape in [*(b["properties"]["family"] for b in COMMANDS["record"][2]["oneOf"]),
              COMMANDS["query"][2]["properties"]["family"]]:
    if "review-result" not in shape["enum"]:
        shape["enum"].append("review-result")
for shape in record_results:
    shape["allOf"].append(condition("family", "review-result", {"properties": {"id": {"pattern": "^RV-"}}}))

RELATION_TEMPLATES = []
research_families = ["frontier", "evidence", "context", "memory", "formal-result", "explanation"]
for token, title, meaning, mathematical in [
    ("derived_from", "도출 계보", "출발 기록이 도착 기록에서 유래한 연구 계보다. 수학적 함의를 자동 주장하지 않는다.", False),
    ("cites", "인용", "출발 기록이 도착 기록을 인용한다. 인용한 주장 자체의 타당성을 부여하지 않는다.", False),
    ("refines", "연구상 구체화", "출발 기록이 도착 기록을 어떤 범위에서 구체화하는지 근거를 기록한다. 논리적 함의와 구별한다.", False),
    ("supersedes", "대체", "출발 기록이 도착 기록을 대체한다. 실제 효력 변경은 대상 기록의 기존 권한·전이 계약을 따른다.", False),
    ("splits_from", "분할 계보", "출발 기록이 도착 기록에서 분할돼 나온 범위와 계보다. 잔여 의무의 처분은 작업 계약을 따른다.", False),
    ("formally_implies", "형식 함의", "출발 명제에서 도착 명제가 도출됨을 명시한 가정·적용 범위에서 증명한다.", True),
    ("formally_equivalent", "형식 동치", "출발·도착 대상의 명시한 의미가 양방향으로 대응함을 증명한다. 역방향 관계 기록을 자동 생성하지 않는다.", True),
    ("formally_reduces_to", "형식 환원", "문제 A에서 B로의 환원이다. B의 허용 해답에서 A의 요구 해답을 얻는 변환·가정·범위·보존 성질을 증명한다.", True),
    ("formally_encodes", "형식 부호화", "출발 대상을 도착 표현으로 부호화하는 사상과 필요한 복원·구별·성질 보존의 범위를 명시하고 증명한다.", True),
    ("formally_simulates", "형식 시뮬레이션", "도착 체계가 출발 체계의 지정한 행동을 모사한다. 상태·전이 대응과 보존 성질·가정을 명시하고 증명한다.", True),
]:
    families = ["frontier", "formal-result"] if mathematical else research_families
    RELATION_TEMPLATES.append({"family": "relation", "token": token, "title": title,
        "meaning": meaning, "constraints": {"from_families": families, "to_families": families,
            "requires_evidence": True, "requires_assessment": mathematical}})


REVIEW_PHASES = {"reviewing": ["initial"], "clarifying": ["organize", "answer"], "judging": ["judge"]}
SCHEMAS["execution"]["allOf"].append({
    "if": {"properties": {"activity_kind": {"const": "identity_review"},
                           "stage": {"enum": list(REVIEW_PHASES)}},
           "required": ["activity_kind", "stage"]},
    "then": {"allOf": [require("output_phase", "role_slot_id"),
        *[condition("stage", stage, {"properties": {"output_phase": enum(*phases)}})
          for stage, phases in REVIEW_PHASES.items()]]},
    "else": forbid("output_phase", "role_slot_id"),
})

ROLE_OUTPUTS = {
    "research_preparation": "activity-result", "research_plan": "plan",
    "research_work": "activity-result", "task_contract_review": "activity-result",
    "goal_audit": "assessment", "operational_review": "operational-review",
    "intent_interpretation": "activity-result", "supplemental_research": "activity-result",
    "maintenance": "activity-result",
}
ROLE_CONTRACTS = [{"actor_kind": "ai", "activity_kind": kind, "stage": stage,
    "output_family": ("review-plan" if stage == "planning" else "review-result") if kind == "identity_review" else ROLE_OUTPUTS[kind],
    "mandatory_input": "Exact activity assignment, common and role documents, applicable governance, required evidence, prior failures and permitted transcript.",
    "authority": "Submit an immutable role output; the engine owns state publication and applies all domain gates.",
    "incomplete": "Return actual scope and partial bytes through execution_incomplete; do not fabricate a role verdict."}
    for kind, stages in STAGES.items() for stage in stages]
ROLE_CONTRACTS += [{"actor_kind": "machine", "activity_kind": "maintenance", "stage": stage,
    "output_family": "machine-check", "mandatory_input": "Exact tool manifest, artifact inputs, host reservations and permission.",
    "authority": "Perform only the assigned deterministic operation; no AI budget or model-facing documents.",
    "incomplete": "Preserve actual checks, failures and uninspected scope; no semantic verdict."}
    for stage in STAGES["maintenance"]]
for row in ROLE_CONTRACTS:
    if row["activity_kind"] == "identity_review":
        if row["stage"] in REVIEW_PHASES:
            row["output_phases"] = REVIEW_PHASES[row["stage"]]
        row["owner_section"] = "11.3.2"
        row["mandatory_input"] = {
            "planning": "Exact proposal, policy, sources, domains, measured input fit, own restored transcript and execution capacity; calculate every mandatory stage allocation; apply 8.3 overflow precedence; proposal-fit measurement excludes restored dialogue only for classification.",
            "reviewing": "Exact full proposal, sources, preflight, perspective and own restored transcript with tool-result bodies and prior versions as reference entries; no current peer verdicts.",
            "clarifying": "Exact output_phase and role_slot_id. organize receives all published issues and missing-scope evidence; answer receives the original objection, all judge replies and its author's own restored transcript.",
            "judging": "Exact proposal, all initial findings, objections, supplements, prior answers and own restored transcript; no current peer judge verdicts.",
        }[row["stage"]]
        row["authority"] = {
            "planning": "Allocate expertise, slots and execution counts for a proposal that fits in full; only the 8.3 proposal-overflow branch closes unresolved for the next plan; common-text or residual restoration overflow escalates; no identity approval.",
            "reviewing": "Assess the assigned scope and submit explicit objections/remaining questions; do not edit the proposal.",
            "clarifying": "Submit only the assigned organize or answer phase; do not issue a semantic verdict or overwrite issue-state.",
            "judging": "Judge objections and whole-proposal identity separately; send new material disputes through the answer route; no proposal edits.",
        }[row["stage"]]

TYPED_IDS = {
    "instance_id": "RI", "engine_id": "EN", "task_id": "T", "owner_activity_id": "AC",
    "activity_id": "AC", "execution_id": "E", "producer_execution_id": "E",
    "planner_execution_id": "E", "request_id": "RQ", "bundle_id": "AB",
    "decision_id": "DC", "conversation_id": "CV", "integration_id": "IN",
    "review_lineage_id": "AC", "continuation_of": "E", "action_id": "EA",
}
TYPED_ARRAYS = {
    "author_execution_ids": "E", "producer_execution_ids": "E", "execution_ids": "E",
    "assigned_execution_ids": "E", "research_execution_ids": "E",
    "provider_operation_ids": "PO", "reservation_ids": "RR", "outstanding_reservation_ids": "RR",
    "unsettled_reservation_ids": "RR", "stopping_execution_ids": "E", "successor_task_ids": "T",
    "dispatch_order": "T", "task_ids": "T", "activity_ids": "AC", "followup_activity_ids": "AC",
    "pending_event_ids": "EVT", "event_ids": "EVT", "trigger_event_ids": "EVT", "consumed_event_ids": "EVT",
}
for prefix in set(TYPED_IDS.values()) | set(TYPED_ARRAYS.values()) | set(type_prefixes.values()) | {"K"}:
    common_defs["id_" + prefix] = {"type": "string", "pattern": "^" + prefix + r"-[0-7][0-9A-HJKMNP-TV-Z]{25}$"}
candidate_item["properties"]["id"] = common("id_T")
canon_item["properties"]["id"] = common("id_K")
visited = set()
def type_named_ids(node):
    if not isinstance(node, (dict, list)) or id(node) in visited:
        return
    visited.add(id(node))
    if isinstance(node, dict):
        for name, shape in node.get("properties", {}).items():
            if name in TYPED_IDS:
                node["properties"][name] = common("id_" + TYPED_IDS[name])
            elif name in TYPED_ARRAYS and shape.get("type") == "array":
                typed_shape = copy.deepcopy(shape)
                typed_shape["items"] = common("id_" + TYPED_ARRAYS[name])
                node["properties"][name] = typed_shape
        for child in node.values():
            type_named_ids(child)
    else:
        for child in node:
            type_named_ids(child)
for schema in [*SCHEMAS.values(), common_defs]:
    type_named_ids(schema)


def schema_documents():
    result = copy.deepcopy(SCHEMAS)
    result["common"] = {"$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": BASE + "common", "title": "common", "$defs": copy.deepcopy(common_defs),
        "x-contract-id": "do-math-draft/common/9", "x-owner-section": "19.2",
        "x-storage": "schema_only"}
    return result

def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2,
                               allow_nan=False) + "\n", encoding="utf-8", newline="\n")


TABLE_START = "<!-- schema-family-table:start -->"
TABLE_END = "<!-- schema-family-table:end -->"


def schema_family_table(schemas):
    rows = ["| 가족 | 소유 절 | 저장 위치 |", "|---|---|---|"]
    rows.extend(f"| `{name}` | {schema['x-owner-section']} | `{schema['x-storage']}` |"
                for name, schema in sorted(schemas.items()))
    return "\n".join(rows)


def generate():
    SCHEMAS.update(schema_documents())
    source = DOC.read_text(encoding="utf-8-sig")
    if source.count(TABLE_START) != 1 or source.count(TABLE_END) != 1:
        raise ValueError("draft must have exactly one managed schema-family table")
    before, rest = source.split(TABLE_START)
    _, after = rest.split(TABLE_END)
    updated = before + TABLE_START + "\n" + schema_family_table(SCHEMAS) + "\n" + TABLE_END + after
    if updated != source:
        DOC.write_text(updated, encoding="utf-8", newline="\n")
    for family, schema in SCHEMAS.items():
        dump(ROOT / "schemas" / (family + ".schema.json"), schema)
    dump(ROOT / "schema-registry.json", {
        "version": 9, "uri_resolution": "offline_exact_registry_only",
        "identifier_prefixes": {**TYPED_IDS, **TYPED_ARRAYS},
        "families": [{"family": family, "schema_id": schema["$id"],
                      "contract_id": schema["x-contract-id"], "owner_section": schema["x-owner-section"],
                      "storage": schema["x-storage"], "path": "schemas/" + family + ".schema.json",
                      "sha256": hashlib.sha256((ROOT / "schemas" / (family + ".schema.json")).read_bytes()).hexdigest(),
                      "id_prefix": schema.get("x-id-prefix")}
                     for family, schema in sorted(SCHEMAS.items())]})
    dump(ROOT / "command-contracts.json", {"version": 9, "authentication": "Actual caller identity is supplied by the authenticated adapter; caller JSON is never authority.",
        "commands": [{"command": name, "caller": v[0], "owner_section": v[1],
                      "precondition": v[3], "postcondition": v[4],
                      "request_schema": BASE + "command-request",
                      "response_schema": BASE + "command-response",
                      "retry": "Same request_id and the SHA-256 of the entire canonical request (schema_version, request_id, command, caller, payload) return the recorded result; changed input is rejected. External action replay additionally requires R35."}
                     for name, v in COMMANDS.items()],
        "exit_codes": {"0": "request_processed_not_semantic_approval", "2": "input_defect",
                       "3": "basis_changed", "4": "correctly_blocked", "5": "tool_or_environment_failure"}})
    dump(ROOT / "semantic-rules.json", {"version": 9, "rules": [
        {"id": rid, "owner_section": section, "contract": statement,
         "source_vectors": vectors, "domain": domain,
         "enforcement": "Runtime/AI/evidence validation as described in the owner section; schema validity alone is insufficient."}
        for rid, section, statement, vectors, domain in RULES]})
    dump(ROOT / "transitions.json", {"version": 9, "machines": TRANSITIONS,
        "interpretation": "Edges are necessary but not sufficient: referenced semantic preconditions and evidence must also hold. Non-transition record updates remain subject to immutability and authority."})
    dump(ROOT / "role-contracts.json", {"version": 9, "roles": ROLE_CONTRACTS,
        "binding": "The execution output_schema_id must equal the assigned role output family URI. Review-result outputs must also match the assigned output_phase, role_slot_id, execution, activity and input manifest. Exact proposal/revision bindings are checked against the referenced assignment."})
    dump(ROOT / "relation-templates.json", {"version": 9, "owner_section": "7.3.2",
        "activation": "Author and validate an instance kind-definition before use; templates alone have no ID, lifecycle or authority.",
        "templates": RELATION_TEMPLATES})
    source_lines = DOC.read_text(encoding="utf-8-sig").splitlines()
    vectors, quality = [], []
    for number, line in enumerate(source_lines, 1):
        match = re.match(r"\| (V\d+) \| (.*?) \| (.*?) \|$", line)
        if match:
            vid, given, expected = match.groups()
            vectors.append({"id": vid, "source_line": number, "input": given, "expected": expected,
                "owner_section": "17.2",
                "source_row_sha256": hashlib.sha256(line.encode("utf-8")).hexdigest(),
                "rule_ids": [r[0] for r in RULES if vid in r[3]], "execution_status": "not_run",
                "evidence_scope": "source_contract_only"})
        match = re.match(r"\| (Q\d+) \| (.*?) \| (.*?) \| (.*?) \|$", line)
        if match:
            qid, guarantee, owner, linked = match.groups()
            quality.append({"id": qid, "guarantee": guarantee, "owner": owner,
                            "source_vectors": re.findall(r"V\d+", linked), "source_line": number,
                            "source_row_sha256": hashlib.sha256(line.encode("utf-8")).hexdigest()})
    dump(ROOT / "source-vector-map.json", {"version": 9, "source": DOC.name,
        "source_sha256": hashlib.sha256(DOC.read_bytes()).hexdigest(),
        "vectors": vectors, "quality_contracts": quality})
    rows = ["# v9 규범 명세 묶음", "",
        "이 묶음은 통합-설계.md의 구현 전 명세다. 설치된 실행기나 검증된 어댑터를 뜻하지 않는다.",
        "기계 형식은 schemas가, 행동의 의미와 원자성은 설계 본문의 소유 절이 정한다.",
        "build_spec.py는 이 묶음의 선언에서 스키마·레지스트리·계약·템플릿과 설계 본문 §16.4의 지정 표를 생성하고, 본문의 벡터 대응을 고정한다.",
        "verify_spec.py는 스키마·codec·명세 검사와 합성 반례를 실행한다. 실제 모델·OS·Lean 시험은 수행하지 않는다.",
        "", "실행 명령:", "", "    python build_spec.py", "    python verify_spec.py", "",
        "위 명령은 이 디렉터리 기준이며 저장소 루트에서는 파일의 전체 상대 경로를 사용한다.",
        "", "| 파일 | 소유 내용 |", "|---|---|",
        "| schemas/ | JSON Schema Draft 2020-12의 닫힌 자료 형식 |",
        "| schema-registry.json | 생성한 스키마 ID·저장 위치·소유 절·해시 |",
        "| command-contracts.json | 명령별 호출자·선행조건·효과·오류·재시도 |",
        "| role-contracts.json | 활동·단계·AI/기계별 필수 입력·출력 가족·권한·미완료 반환 |",
        "| relation-templates.json | 인스턴스에 자동 활성화되지 않는 표준 관계 저작 템플릿 |",
        "| toolchain-lock.json | 실제 명세 검증에 사용한 Python·파서·스키마 검사기 판본 |",
        "| semantic-rules.json | 스키마만으로 판정할 수 없는 관계적·의미적 의무 |",
        "| transitions.json | 허용 전이와 추가 전제 규칙 |",
        f"| source-vector-map.json | 본문의 V 벡터 {len(vectors)}개·Q 계약 {len(quality)}개 원문 대응. 실제 실행 상태는 별도 |",
        "| fixtures/ | 합성 입력과 독립 반례 |",
        "| validation-report.json | 실제 수행한 명세 검사의 범위·결과 |",
        "| review/ | 각 검토가 고정한 판본의 독립 적대 검토와 작성자 판단. 이전 판본의 통과를 현행 통과로 승계하지 않음 |", "",
        "스키마 URI의 do-math.invalid는 오프라인 식별자다. 네트워크로 해석하지 않는다.",
        "예제 참조·영수증은 합성 자료다. 스키마 통과를 실제 대상 실재·권한·종료·수학 판정의 증거로 사용하지 않는다.",
        "", "| 가족 | 계약 ID | 소유 절 | 저장 위치 |", "|---|---|---|---|"]
    rows += [f"| {name} | {s['x-contract-id']} | {s['x-owner-section']} | {s['x-storage']} |"
             for name, s in sorted(SCHEMAS.items())]
    (ROOT / "README.md").write_text("\n".join(rows) + "\n", encoding="utf-8", newline="\n")
    return SCHEMAS


if __name__ == "__main__":
    generate()
