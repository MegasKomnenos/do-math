"""Installation registry and domain semantic checks for persisted families."""
from .schemas import (BOOL, EVIDENCE, NAT, PROFILE_REF, RECORDS, RESEARCH_FIELDS, RUNTIME_FIELDS, TEXT,
                      array, enum, nullable, obj)
from ..file_io import json_copy


def refs(*fields, lists=()):
    def extract(row):
        for field, family in fields:
            if row.get(field) is not None:
                yield row[field], family
        for field, family in lists:
            yield from ((value, family) for value in row.get(field, []))
    return extract


def _academic_references(row):
    yield row["rejection_id"], "external_rejections"
    yield row["execution_id"], "executions"
    for ref in row["evidence_refs"]:
        if not ref.startswith("runtime/artifacts/"):
            yield ref, "knowledge|formal_results|expositions|external_operations|executions"


REFERENCES = {
    "knowledge": refs(("formal_result_id", "formal_results"), ("exposition_id", "expositions"), lists=(("dependencies", "knowledge"),)),
    "formal_results": refs(("trust_environment_id", "trust_environments"), ("transition_id", "trust_transitions"), lists=(("dependencies", "knowledge"),)),
    "expositions": refs(("formal_result_id", "formal_results")),
    "identity_assessments": refs(("formal_result_id", "formal_results"), ("exposition_id", "expositions"),
        ("review_cycle_id", "review_cycles"), ("previous_assessment_id", "identity_assessments"),
        ("transition_id", "trust_transitions"), lists=(("execution_ids", "executions"),)),
    "assessment_uses": refs(("assessment_id", "identity_assessments")),
    "relations": refs(("source", "knowledge|formal_results"), ("target", "knowledge|formal_results"),
                      lists=(("formal_result_refs", "formal_results"), ("assessment_refs", "identity_assessments"))),
    "integrations": refs(("execution_id", "executions")),
    "activities": refs(lists=(("assigned_execution_ids", "executions"),)),
    "executions": refs(("owner_activity_id", "activities"), ("continuation_of", "executions"), ("operation_id", "external_operations"),
                       lists=(("context_origin", "executions"),)),
    "tasks": refs(("trust_environment_id", "trust_environments"), ("producer_execution", "executions"),
        lists=(("dependencies", "tasks|knowledge"), ("authority_refs", "grants|decisions|delegations"),
               ("author_execution_ids", "executions"), ("knowledge_revision_targets", "knowledge"))),
    "question_links": refs(("origin_execution_id", "executions"), ("resolution_ref", None)),
    "external_operations": refs(("grant_id", "grants"), ("execution_id", "executions"), ("continuation_of", "executions"),
                                lists=(("producer_executions", "executions"),)),
    "grants": refs(("source_ref", "governance_sources"), ("decision_id", "decisions"), ("replaced_by", "grants")),
    "delegations": refs(("original_decision_id", "decisions"), ("decision_id", "decisions")),
    "observation_facts": refs(("execution_id", "executions")),
    "self_check_obligations": refs(("execution_id", "executions")),
    "self_check_responses": refs(("execution_id", "executions")),
    "operational_dispositions": refs(("execution_id", "executions")),
    "control_receipts": refs(("execution_id", "executions")),
    "recoveries": refs(lists=(("execution_ids", "executions"),)),
    "reservations": refs(("constraint_id", "capacity_constraints"), ("owner_id", "executions")),
    "review_cycles": refs(("owner_activity_id", "activities"), ("knowledge_id", "knowledge"),
        ("assessment_id", "identity_assessments"), ("transition_id", "trust_transitions"), lists=(("assessment_use_ids", "assessment_uses"), ("producer_execution_ids", "executions"))),
    "goal_judgments": refs(("execution_id", "executions"), lists=(("formal_result_refs", "formal_results"),
        ("assessment_refs", "identity_assessments"), ("dependencies", "knowledge|tasks"))),
    "events": refs(("execution_id", "executions"), ("activity_id", "activities"), lists=(("record_refs", None),)),
    "governance": refs(("approval_ref", "decisions"), ("source_ref", "governance_sources"), ("superseded_by", "governance"), lists=(("supersedes", "governance"),)),
    "trust_transitions": refs(("from_environment", "trust_environments"), ("to_environment", "trust_environments")),
    "academic_resolution_records": _academic_references,
    "intent_imports": refs(("execution_id", "executions"), ("previous_id", "intent_imports"), ("superseded_by", "intent_imports"), ("input_ref", "inputs")),
    "delegation_applications": refs(("delegation_id", "delegations")),
    "governance_events": refs(("grant_id", "grants"), lists=(("affected", None),)),
}


def _role_profile_references(selection):
    for references in selection.values():
        yield from ((reference["id"], "execution_profiles") for reference in references)


def _lifecycle_references(row):
    if row.get("input_id"):
        yield row["input_id"], "inputs"
    check = row.get("intent_check", {})
    for field in ("interpretation_execution_id", "check_execution_id"):
        if check.get(field):
            yield check[field], "executions"
    adoption = row.get("adoption", {})
    for ref in adoption.get("profile_refs", []):
        yield ref["id"], "execution_profiles"
    if adoption.get("initial_profile_ref"):
        yield adoption["initial_profile_ref"]["id"], "execution_profiles"
    for field in ("initial_grant_ids", "research_grant_ids"):
        yield from ((identifier, "grants") for identifier in adoption.get(field, []))


def _event_queue_references(value):
    yield from ((identifier, "events") for identifier in value)


def _academic_assessment_references(value):
    for row in value:
        yield row["task_id"], "tasks"
        yield row["execution_id"], "executions"


def _host_capacity_reference(value):
    yield value, "capacity_constraints"


def _trust_binding_references(value):
    yield from ((identifier, "trust_environments") for identifier in value)


def install(contract):
    from ..execution_profiles import validate_profile
    from ..budget import validate_reservation
    from ..governance import validate_source
    from ..task_contracts import validate_contract_meaning
    validators = {"execution_profiles": validate_profile, "reservations": validate_reservation,
                  "tasks": validate_contract_meaning, "governance_sources": validate_source,
                  **RECORD_RULES}
    research = {"knowledge", "formal_results", "expositions", "identity_assessments", "assessment_uses",
                "relations", "sources", "kind_definitions", "grants", "decisions", "delegations",
                "trust_environments", "execution_profiles", "capacity_constraints", "capability_evidence", "goal_judgments", "governance", "governance_sources"}
    lists = {"relations", "sources", "question_links", "goal_judgments", "external_rejections", "academic_resolution_records", "inputs", "queue", "governance_events", "events"}
    metadata = {
        "research": {"id", "object_format", "title", "workspace", "created_at",
                     "goal_status", "active_trust_environment", "conversation_loss_policy", "host_capacity_ref"},
        "runtime": {"status", "cycles",
                    "updated_at", "recovery_checked", "last_observed_utc", "event_cursor", "availability",
                    "clock_guard", "resume_lifecycle", "user_pause", "stop_requested", "next_research_reconsider_at"}}
    for name, schema in RECORDS.items():
        contract.register_family("research" if name in research else "runtime", name,
            shape="list" if name in lists else "map",
            schema=schema, validator=validators.get(name), references=REFERENCES.get(name))
    for root, fields in (("research", RESEARCH_FIELDS), ("runtime", RUNTIME_FIELDS)):
        for name, schema in fields.items():
            if name == "role_profile_refs":
                from ..execution_profiles import PROFILE_ROLES
                choices = {**array(PROFILE_REF, True), "minItems": 1}
                selection_schema = obj({role: choices for role in sorted(PROFILE_ROLES)})
                contract.register_family(root, name, shape="singleton", schema=selection_schema,
                                         identity=False, references=_role_profile_references)
            else:
                reference = {("research", "lifecycle"): _lifecycle_references,
                    ("runtime", "pending_events"): _event_queue_references,
                    ("runtime", "academic_assessments"): _academic_assessment_references,
                    ("research", "host_capacity_ref"): _host_capacity_reference,
                    ("runtime", "trust_bindings"): _trust_binding_references}.get((root, name))
                contract.register_family(root, name, shape="metadata" if name in metadata[root] else "singleton",
                                         schema=schema, validator=validators.get(name), identity=False,
                                         references=reference)
    contract.register_family("research", "config", shape="singleton", schema=config_schema(), identity=False)


EFFORTS = ("minimal", "low", "medium", "high", "xhigh")
# Settings that must be adopted as positive integers; max_output_repairs may be zero.
POSITIVE_SETTINGS = tuple("call_timeout_seconds reviewers goal_auditors max_input_bytes review_rounds "
    "review_research_limit research_reconsider_seconds observation_interval_seconds plan_settle_seconds "
    "max_artifact_bytes operator_interval_seconds operator_timeout_seconds provider_retry_initial_seconds "
    "provider_retry_max_seconds finish_notice_seconds self_check_response_window_seconds tool_review_window_seconds "
    "contract_revision_limit exhaustion_empty_limit import_rework_limit proposal_version_limit "
    "selection_failure_limit no_progress_limit".split())


def config_schema():
    """The configuration section: the closed key vocabulary with each key's type and range.

    Stored configuration, the configure control shape and engine validation
    all derive from this one table. Cross-field rules (model policy, retry
    order, host binding, scholarly server) stay with their owners.
    """
    from ..execution_profiles import HOST_ROLES
    positive = {"type": "integer", "minimum": 1}
    config = {"effort": enum(*EFFORTS), "operator_effort": enum(*EFFORTS, "max", "ultra"),
              "observation_mode": enum("event_driven", "periodic"),
              **{k: positive for k in POSITIVE_SETTINGS}, "max_output_repairs": NAT,
              **{k: BOOL for k in ("operator_enabled", "scholarly_enabled", "claude_only_assigned_model")},
              **{k: {"type": "object", "additionalProperties": TEXT} for k in ("tier_models", "role_tiers")},
              "session_limits": obj({"work": {"type": "object", "additionalProperties": NAT}}, ("work",)),
              "lean_command": nullable({**array({"type": "string", "minLength": 1}), "minItems": 1}),
              "allowed_axioms": array({"type": "string", "minLength": 1}), "scholarly_server": nullable(EVIDENCE)}
    host_demands = obj({"jobs": {"const": 1}, "memory_bytes": {"type": "integer", "minimum": 1},
        "cpu_rate_basis_points": {"type": "integer", "minimum": 1, "maximum": 10000}},
        ("jobs", "memory_bytes", "cpu_rate_basis_points"))
    config["host_resources"] = nullable(obj({"constraint": RECORDS["capacity_constraints"],
        "demands_by_role": obj({role: host_demands for role in sorted(HOST_ROLES)})},
        ("constraint", "demands_by_role")))
    return json_copy(obj(config))


# Record-local rules: each reads one record and nothing else, so install
# registers it as its family's validator. StateContract.validate runs it for a
# record that differs from the parent's and skips it for an equal one, the one
# skip rule for these checks. Rules over several records stay in validate_semantics.

def _immutable_input_rules(lifecycle):
    from ..initialization import original_input_bytes
    original_input_bytes(lifecycle["immutable_input"])


def _execution_rules(row):
    if row["status"] == "ended" and (not row.get("ended_at") or not row.get("outcome")):
        raise ValueError("ended execution requires termination evidence")
    if (row["status"] == "stopping") != ("stop_phase" in row):
        raise ValueError("stop_phase belongs exactly to stopping executions")
    if row.get("outcome") == "output_accepted" and not row.get("submission_receipt"):
        raise ValueError("accepted output lacks submission receipt")
    if row.get("execution_window", {}).get("execution_id", row["id"]) != row["id"]:
        raise ValueError("execution window belongs to a different execution")
    if row.get("authority_revocation"):
        receipt = row.get("submission_receipt", {})
        if (not isinstance(row.get("submission_intent", {}).get("manifest"), list)
                or receipt.get("state") != "accepted" or receipt.get("kind") not in {"submit_intent", "native_final"}
                or receipt.get("execution_id") != row["id"]
                or row["authority_revocation"]["receipt_id"] != (receipt.get("id") or receipt.get("request_id"))):
            raise ValueError("submission authority revocation differs from its actual receipt")


def _external_operation_rules(row):
    from ..external import request_binding_current
    if not request_binding_current(row):
        raise ValueError("external operation request/key differs from sealed bytes")
    if row.get("retry_evidence"):
        proof = row["retry_evidence"]
        if proof["request_sha256"] != row["request_sha256"] or proof["idempotency_key"] != row["idempotency_key"]:
            raise ValueError("external retry evidence differs from the operation")
    evidence = row.get("reconciliation", {}).get("evidence", {})
    if row["status"] == "confirmed" and row.get("succeeded") is not True:
        raise ValueError("confirmed external operation requires success evidence")
    if row["status"] == "failed" and row.get("effect_absent") is not True:
        raise ValueError("failed external operation requires effect-absence evidence")
    if row["status"] == "unknown" and row.get("succeeded") is not None:
        raise ValueError("unknown external effect has a definitive success value")
    if row["status"] == "cancelled" and row.get("transmitted") is not False and evidence.get("fact") != "not_transmitted":
        raise ValueError("cancelled external effect was not confirmed untransmitted")
    if row.get("handling") == "reconciled" and not evidence.get("evidence_ref"):
        raise ValueError("reconciled handling lacks external effect evidence")


def _operational_disposition_rules(row):
    from ..operational_dispositions import validate_disposition
    validate_disposition(row["disposition"])


def _academic_seal_rules(row):
    from ..repository import exact_content_hash
    if (not row["evidence_refs"] or set(row["evidence_refs"]) != set(row["evidence_hashes"])
            or row["sha256"] != exact_content_hash({k: v for k, v in row.items() if k != "sha256"})):
        raise ValueError("academic resolution seal/evidence binding is invalid")


def _nonfinite(token):
    raise ValueError("nonfinite raw observation")


def _observation_fact_rules(row):
    import hashlib
    import json
    if "event_json" in row:
        json.loads(row["event_json"], parse_constant=_nonfinite)
        if hashlib.sha256(row["event_json"].encode()).hexdigest() != row["event_sha256"]:
            raise ValueError("observation event bytes hash mismatch")


def _capability_evidence_rules(row):
    from ..repository import exact_content_hash
    if row["id"] != "CE-" + exact_content_hash({k: v for k, v in row.items() if k != "id"}):
        raise ValueError("capability evidence ID differs from its content")


def _intent_import_rules(bundle):
    from ..governance import _import_payload, validate_source
    from ..repository import exact_content_hash
    validate_source(bundle["source"])
    if exact_content_hash(_import_payload(bundle)) != bundle["sha256"]:
        raise ValueError("sealed intent import hash mismatch")


def _delegation_application_rules(application):
    from ..delegations import case_basis_reference_ids
    from ..repository import exact_content_hash
    basis = application["basis"]
    if exact_content_hash(basis) != application["input_sha256"]:
        raise ValueError("delegation application basis hash mismatch")
    if set(basis["references"]) != set(case_basis_reference_ids(basis["case"])):
        raise ValueError("delegation frozen references differ from declared case basis")
    judgments = application["judgments"].values()
    if any(exact_content_hash(judgment["output"]) != judgment["sha256"] for judgment in judgments):
        raise ValueError("delegation judgment provenance mismatch")
    execution_ids = [judgment["execution_id"] for judgment in judgments]
    if len(execution_ids) != len(set(execution_ids)):
        raise ValueError("delegation judgments must use distinct executions")


RECORD_RULES = {"lifecycle": _immutable_input_rules, "executions": _execution_rules,
                "external_operations": _external_operation_rules,
                "operational_dispositions": _operational_disposition_rules,
                "academic_resolution_records": _academic_seal_rules, "observation_facts": _observation_fact_rules,
                "intent_imports": _intent_import_rules, "delegation_applications": _delegation_application_rules,
                "capability_evidence": _capability_evidence_rules}


def validate_lifecycle(instance, runtime):
    """The lifecycle rules of one whole state; the schema fixes the state values.

    A state has a lifecycle and a runtime status, a permanently closed
    instance only the closed status, and a persisted UTC high-water mark.
    """
    lifecycle, status = instance.get("lifecycle"), runtime.get("status")
    if lifecycle is None or status is None:
        raise ValueError("current lifecycle contract: the lifecycle and the runtime status are required")
    if lifecycle.get("permanently_closed") and status != "closed":
        raise ValueError("current lifecycle contract: a permanently closed instance cannot have a live projection")
    observed = runtime.get("last_observed_utc")
    from ..file_io import parse_utc
    try:
        if observed is None or not observed.endswith(("Z", "+00:00")):
            raise ValueError("UTC offset required")
        parse_utc(observed)
    except ValueError as error:
        raise ValueError("current lifecycle contract: the persisted UTC high-water is absent or invalid") from error


def validate_semantics(instance, runtime, identifiers, parent=None, *, contract):
    """Whole-state semantic rules of ``contract`` (the calling StateContract).

    ``parent`` is an (instance, runtime) pair already validated under the same
    contract. Record-local rules are family validators (RECORD_RULES), which
    StateContract.validate skips for records equal to the parent's. Rules here
    read several records and always run, with two exceptions that compare the
    records they read with the parent's: the active grant check and the
    transition hash of a finished staged review. Every validated state
    satisfies the lifecycle rules, so a loaded state never needs them again.
    """
    from ..activities import validate_activities
    from ..execution_profiles import match_profile_ref, validate_host_constraint
    from ..formal import compare_formal_results
    from ..governance import validate_governance_state, validate_grant_source
    from ..knowledge import _hash
    from ..knowledge_io import _BUILTINS, _RELATION_FIELDS, validate_relation
    from ..knowledge_records import _assessment_basis, validate_formal_evidence, validate_knowledge_records
    from ..launch import validate as validate_launch
    from ..observations import validate_rules
    from ..questions import open_targets
    from ..repository import exact_content_hash
    from ..review_cycle import (_check_proposal, identity_assessment, staged_review_candidate,
                                validate_resource_disposition)
    from ..review_policy import build_review_policy
    from ..task_contracts import available_input_refs, validate_item_dispositions
    from ..trust_validation import environment_errors
    parent_instance, parent_runtime = parent if parent is not None else ({}, {})
    validate_lifecycle(instance, runtime)
    if "governance" in instance:
        validate_governance_state(instance)
    sources, prior_sources = instance.get("governance_sources", {}), parent_instance.get("governance_sources", {})
    prior_grants, prior_decisions = parent_instance.get("grants", {}), parent_instance.get("decisions", {})
    for identifier, grant in instance.get("grants", {}).items():
        # The grant check reads only the grant, its source and its decision.
        if grant["status"] == "active" and (
                prior_grants.get(identifier) != grant
                or prior_sources.get(grant.get("source_ref")) != sources.get(grant.get("source_ref"))
                or prior_decisions.get(grant.get("decision_id")) != instance.get("decisions", {}).get(grant.get("decision_id"))):
            validate_grant_source(instance, grant)
    if instance.get("review_policy"):
        build_review_policy(instance["review_policy"])
    validate_knowledge_records(instance)
    errors = validate_activities(runtime)
    if errors:
        raise ValueError("; ".join(errors))
    for row in runtime.get("executions", {}).values():
        profile = match_profile_ref(instance.get("execution_profiles", {}), row["execution_profile_ref"])
        if row.get('capacity'):
            validate_launch(row.get('launch_ticket'), execution_id=row['id'], profile_sha256=profile['sha256'])
        if row.get("role", profile["role"]) != profile["role"] or row["actor_kind"] != profile["actor_kind"]:
            raise ValueError("execution/profile actor or role mismatch")
    for profile in instance.get("execution_profiles", {}).values():
        ids = profile.get("ai", {}).get("capacity_refs", []) + profile.get("host_capacity_refs", [])
        if set(ids) - set(instance.get("capacity_constraints", {})):
            raise ValueError("profile references unknown capacity constraint")
        host = profile.get("host_resources")
        if host:
            constraint = instance["capacity_constraints"][host["constraint_id"]]
            if constraint["kind"] != "host" or any(host[key] != constraint.get(key) for key in ("scope", "host_id")):
                raise ValueError("host profile differs from its referenced local constraint")
    for role, references in instance.get("role_profile_refs", {}).items():
        for reference in references:
            profile = match_profile_ref(instance.get("execution_profiles", {}), reference)
            if profile["role"] != role:
                raise ValueError("selected profile belongs to a different role")
    if instance.get("host_capacity_ref"):
        if instance["capacity_constraints"][instance["host_capacity_ref"]]["kind"] != "host":
            raise ValueError("adopted host capacity reference names another constraint kind")
    authored_host = instance.get("config", {}).get("host_resources")
    if authored_host:
        validate_host_constraint(authored_host["constraint"])
        if instance.get("capacity_constraints", {}).get(authored_host["constraint"]["id"]) != authored_host["constraint"]:
            raise ValueError("host authoring input differs from the registered constraint edition")
    for row in [*runtime.get("queue", []), *runtime.get("executions", {}).values(),
                *(wait["action"] for wait in runtime.get("waiting_actions", {}).values())]:
        selection = row.get("model_selection") or {}
        if selection.get("profile_ref"):
            profile = match_profile_ref(instance.get("execution_profiles", {}), selection["profile_ref"])
            if profile["role"] != row.get("role") or (profile["actor_kind"] == "ai" and profile["ai"]["model"] != selection["model"]):
                raise ValueError("model selection differs from the pinned role/model profile")
        action = row.get("action", row)
        if "cleanup_execution_ids" in action:
            requested = action["cleanup_execution_ids"]
            if set(requested) - set(runtime.get("executions", {})):
                raise ValueError("cleanup scope references missing executions")
            request = next((item["request"] for item in runtime.get("history", [])
                if item.get("kind") == "user_control" and
                item.get("request", {}).get("id") == action.get("requested_by")), None)
            if (action.get("role") != "maintenance" or not request
                    or request.get("origin", "user") != "user" or request.get("action") != "request"
                    or request.get("config", {}).get("role") != "maintenance"
                    or request["config"].get("cleanup_execution_ids") != requested):
                raise ValueError("cleanup scope differs from its preserved exact user request")
            # This validates the historical scope, not present permission to
            # delete. ENGINE rechecks current grants and retention closure.
        if action.get("stage") == "impact_review":
            request = action["input_basis"]["impact_review"]
            if request["producer_execution_id"] not in runtime.get("executions", {}):
                raise ValueError("impact review original execution is missing")
            for plan in request["plans"].values():
                if plan["digest"] != _hash({key: value for key, value in plan.items() if key != "digest"}):
                    raise ValueError("impact review frozen plan hash differs")
                if set(plan["basis"]) - set(identifiers) or not set(plan["roots"]) <= set(plan["basis"]):
                    raise ValueError("impact review frozen plan references do not resolve")
    for reservation in runtime.get("reservations", {}).values():
        for reference in reservation.get("authority_refs", []):
            identifier = reference.get("id") if isinstance(reference, dict) else reference
            if identifier not in instance.get("execution_profiles", {}) and identifier not in instance.get("grants", {}) and identifier not in instance.get("decisions", {}):
                raise ValueError("reservation authority reference does not resolve")
    for row in instance.get("capacity_constraints", {}).values():
        if row["kind"] == "host":
            validate_host_constraint(row)
            for reference in row["authority_refs"]:
                family = identifiers.get(reference, (None, None))[1]
                if family not in {"decisions", "governance_sources"}:
                    raise ValueError("host constraint authority reference does not resolve to a preserved user decision/source")
                if family == "governance_sources" and instance[family][reference].get("origin") != "user":
                    raise ValueError("host constraint authority source is not user-origin")
        if row["kind"] == "concurrency":
            if any(key not in row for key in ("model", "work_slots", "accounting_unit")):
                raise ValueError("concurrency constraint lacks its model or slot limit")
    for row in instance.get("capability_evidence", {}).values():
        match_profile_ref(instance.get("execution_profiles", {}), row["execution_profile_ref"])
    for task in runtime.get("tasks", {}).values():
        for reference in task.get("profile_refs", []):
            if identifiers.get(reference["id"], (None, None))[1] != "execution_profiles":
                raise ValueError("task profile reference does not identify an execution profile")
            match_profile_ref(instance.get("execution_profiles", {}), reference)
        if task.get("assessment"):
            validate_item_dispositions(task, task["assessment"], require_complete=task.get("status") == "completed")
    for row in runtime.get("self_check_responses", {}).values():
        if row["kind"] == "self_check_rejected":
            continue  # Invalid incoming IDs remain raw rejection evidence.
        obligation = runtime.get("self_check_obligations", {}).get(row["obligation_id"])
        if not obligation:
            raise ValueError("self-check response references unknown obligation")
        if obligation["execution_id"] != row["execution_id"]:
            raise ValueError("self-check response execution differs from obligation")
    for relation in instance.get("relations", []):
        if relation.get("status", "active") == "active":
            checked = validate_relation(instance, {k: v for k, v in relation.items() if k in _RELATION_FIELDS})
            if not checked["valid"]:
                raise ValueError("invalid relation semantics: " + ", ".join(checked["reasons"]))
    for rules in runtime.get("task_observation_rules", {}).values():
        validate_rules(rules, allow_empty=True)
    for formal in instance.get("formal_results", {}).values():
        evidence = formal["verification"]
        if formal["publication_state"] != "candidate" and not evidence:
            raise ValueError("published formal result requires verification evidence")
        if evidence:
            env = instance.get("trust_environments", {}).get(formal.get("trust_environment_id"))
            if env is None:
                raise ValueError("sealed formal result requires trust environment")
            validate_formal_evidence(formal, evidence, env)
            if (formal["publication_state"] == "accepted") != (evidence.get("status") == "verified"):
                raise ValueError("formal publication state contradicts verification")
    for assessment in instance.get("identity_assessments", {}).values():
        expected = _assessment_basis(instance["formal_results"][assessment["formal_result_id"]],
                                     instance["expositions"][assessment["exposition_id"]])
        if assessment["basis"] != expected:
            raise ValueError("identity assessment premise hash differs from immutable inputs")
        if assessment.get("previous_assessment_id"):
            previous = instance["identity_assessments"][assessment["previous_assessment_id"]]
            transition = runtime.get("trust_transitions", {}).get(assessment.get("transition_id"), {})
            targets = [t for t in transition.get("targets", [])
                       if t["formal_result_id"] == previous["formal_result_id"]
                       and t["exposition_id"] == previous["exposition_id"]]
            if len(targets) != 1 or transition.get("status") not in {"active", "activated"}:
                raise ValueError("identity continuity requires the actual activated transition")
            target = targets[0]
            comparison = compare_formal_results(target, transition.get("results", {}).get(target["id"], {}))
            formal = instance["formal_results"][assessment["formal_result_id"]]
            exposition = instance["expositions"][assessment["exposition_id"]]
            if (not comparison["equivalent"] or comparison != assessment.get("continuity_comparison")
                    or formal.get("supersedes") != previous["formal_result_id"]
                    or exposition.get("supersedes") != previous["exposition_id"]
                    or formal.get("trust_environment_id") != transition["to_environment"]
                    or any(assessment.get(k) != previous.get(k) for k in
                           ("decision", "review_cycle_id", "policy_ref", "execution_ids", "proposal_digest", "scope_complete"))):
                raise ValueError("identity continuity differs from its sealed source and transition")
        elif assessment.get("review_cycle_id"):
            cycle = runtime["review_cycles"][assessment["review_cycle_id"]]
            staged_transition = bool(assessment.get("transition_id") and assessment.get("reviewed_identity_basis"))
            reviewed_basis = (assessment.get("reviewed_identity_basis") if staged_transition
                              else assessment["basis"])
            if (cycle.get("decision") != assessment["decision"] or cycle.get("identity_basis") != reviewed_basis
                    or cycle.get("policy_ref") != assessment["policy_ref"]
                    or cycle.get("status") not in {"completed", "unresolved"}):
                raise ValueError("identity assessment differs from its sealed review")
            if staged_transition:
                transition = runtime.get("trust_transitions", {}).get(assessment["transition_id"], {})
                target = next((row for row in transition.get("targets", [])
                               if row["id"] == cycle.get("knowledge_id")), None)
                staged = cycle.get("staged_candidate", {})
                formal = instance["formal_results"][assessment["formal_result_id"]]
                exposition = instance["expositions"][assessment["exposition_id"]]
                verification = {key: value for key, value in transition.get("results", {}).get(cycle.get("knowledge_id"), {}).items()
                                if key not in {"id", "identity_review"}}
                if (transition.get("status") not in {"active", "activated"}
                        or cycle.get("transition_id") != assessment["transition_id"]
                        or target is None
                        or assessment.get("transition_basis") != staged.get("transition_basis")
                        or formal.get("transition_id") != assessment["transition_id"]
                        or formal.get("supersedes") != target["formal_result_id"]
                        or formal.get("trust_environment_id") != transition.get("to_environment")
                        or formal.get("verification") != verification
                        or exposition.get("supersedes") != cycle.get("proposal", {}).get("exposition_id")
                        or exposition.get("formal_result_id") != formal["id"]):
                    raise ValueError("staged identity assessment differs from its activated transition")
            source = identity_assessment(cycle, reason=assessment.get("summary", ""))
            if any(assessment.get(key) != value for key, value in source.items()):
                raise ValueError("identity assessment does not reproduce the sealed review result")
        elif assessment["decision"] == "match":
            raise ValueError("identity match requires a sealed review cycle")
    prior_cycles = parent_runtime.get("review_cycles", {})
    prior_transitions = parent_runtime.get("trust_transitions", {})
    for identifier, cycle in runtime.get("review_cycles", {}).items():
        _check_proposal(cycle)
        validate_resource_disposition(cycle, runtime, instance=instance)
        if cycle.get("staged_candidate") is not None or cycle.get("transition_id") is not None:
            staged = cycle.get("staged_candidate", {})
            transition = runtime.get("trust_transitions", {}).get(cycle.get("transition_id"), {})
            target = next((row for row in transition.get("targets", []) if row["id"] == cycle.get("knowledge_id")), None)
            environment = staged.get("target_environment", {})
            pending = transition.get("status") in {"checking", "ready"}
            # The transition hash reads only the cycle and its transition. A
            # finished review whose two records equal the parent's keeps the
            # parent's result; a pending one is reproduced below regardless.
            rehash = (pending or prior_cycles.get(identifier) != cycle
                      or prior_transitions.get(cycle.get("transition_id")) != transition)
            if (target is None or environment.get("id") != transition.get("to_environment")
                    or environment.get("id") not in instance.get("trust_environments", {})
                    or staged.get("proposal") != cycle["proposal"] or staged.get("identity_basis") != cycle.get("identity_basis")):
                raise ValueError("staged review does not bind its actual transition target/environment")
            if rehash:
                verification = {key: value for key, value in transition.get("results", {}).get(cycle.get("knowledge_id"), {}).items()
                                if key not in {"id", "identity_review"}}
                if staged.get("transition_basis") != exact_content_hash({"transition_id": transition["id"], "target": target,
                        "verification": verification, "target_environment": environment, "from_environment": transition["from_environment"]}):
                    raise ValueError("staged review does not bind its actual transition target/environment")
            # Pending reviews must reproduce the current producer. Historical
            # cycles retain their frozen candidate after atomic activation.
            if pending and staged_review_candidate(instance, runtime, transition["id"], cycle["knowledge_id"]) != staged:
                raise ValueError("staged review differs from current transition evidence")
        for reference in cycle.get("slot_profiles", {}).values():
            if reference is not None:
                match_profile_ref(instance.get("execution_profiles", {}), reference)
        for entry in cycle.get("results", {}).values():
            execution = runtime.get("executions", {}).get(entry.get("execution_id"))
            if not execution or execution.get("role") != "identity_review":
                raise ValueError("review result requires its actual identity-review execution")
        for eid, binding in cycle.get("input_bindings", {}).items():
            execution = runtime.get("executions", {}).get(eid)
            if not execution or binding["profile_ref"] != execution.get("execution_profile_ref"):
                raise ValueError("review input binding differs from its execution")
    if instance.get("active_trust_environment") is not None:
        env = instance.get("trust_environments", {}).get(instance["active_trust_environment"])
        if env is None or env.get("status") != "active":
            raise ValueError("active trust environment reference is not active")
        errors = environment_errors(env, runtime.get("trust_bindings", {}).get(instance["active_trust_environment"]))
        if errors:
            raise ValueError("active trust environment contract: " + "; ".join(errors))
    current_kinds = set()
    for definition in instance.get("kind_definitions", {}).values():
        if definition.get("builtin"):
            if not any(all(definition.get(k) == builtin[k] for k in ("family", "token", "meaning", "constraints")) for builtin in _BUILTINS):
                raise ValueError("builtin kind differs from installed definition")
        if definition["status"] != "withdrawn":
            key = (definition["family"], definition["token"])
            if key in current_kinds:
                raise ValueError("multiple current definitions of one kind")
            current_kinds.add(key)
        if not definition.get("builtin"):
            if definition["status"] in {"checked", "active"} and not definition.get("check_ref"):
                raise ValueError("checked kind lacks its check reference")
            if definition["status"] == "active" and not definition.get("approval_ref"):
                raise ValueError("active kind lacks approval reference")
        if definition["constraints"].get("mathematical_claim") and not all(
            definition["constraints"].get(k) for k in ("requires_formal_results", "requires_assessments")):
            raise ValueError("mathematical relation kind cannot waive formal evidence")
    for application in runtime.get("delegation_applications", {}).values():
        for identifier, record in application["basis"]["references"].items():
            if identifier not in identifiers or record.get("id") != identifier:
                raise ValueError("delegation frozen reference identity does not resolve")
            root, family_name = identifiers[identifier][:2]
            if family_name not in RECORDS:
                raise ValueError("delegation reference is not an independently typed record")
            contract.family(root, family_name).checker.validate(record)
        if any(judgment["execution_id"] not in runtime.get("executions", {})
               for judgment in application["judgments"].values()):
            raise ValueError("delegation judgment provenance mismatch")
    # Question scopes are not restricted to record IDs: the actual owner
    # also routes decisions to queued/deferred action coordinates or supplied
    # input aliases. These namespaces are explicit, not a scan for any 'id'.
    # They do not depend on the question, so build them once per validation.
    # Input references are derived, never stored; a stored target is valid whatever the host found.
    # They already carry every source alias (input_basis.aliases).
    question_targets = (set(identifiers) | set(runtime.get("waiting_actions", {}))
                        | set(available_input_refs(instance, runtime, lean_available=True)))
    for question in runtime.get("question_links", []):
        if question["origin_execution_id"] is None and not question.get("source_ref"):
            raise ValueError("nonexecution question requires a preserved source reference")
        # target_ids is immutable routing history. Only still-unresolved
        # coordinates must remain live after a queued/waiting action finishes.
        if set(open_targets(question)) - question_targets:
            raise ValueError("question target does not resolve in a declared namespace")
    for action_id, wait in runtime.get("waiting_actions", {}).items():
        if wait["action"]["id"] != action_id:
            raise ValueError("waiting action key differs from its preserved action")
        if wait.get("question_id") and wait["question_id"] not in identifiers:
            raise ValueError("waiting action question reference is missing")
        for field, family in (("execution_id", "executions"), ("import_id", "intent_imports")):
            if wait.get(field) is not None and identifiers.get(wait[field], (None, None))[1] != family:
                raise ValueError("waiting action reference does not resolve: " + field)
        if any(identifiers.get(task_id, (None, None))[1] != "tasks" for task_id in wait.get("delegated_targets", {}).values()):
            raise ValueError("waiting action reference does not resolve: delegated_targets")
        for identifier, request in wait.get("review_requests", {}).items():
            if identifier != request["integration_id"] or request["producer_execution_id"] not in runtime.get("executions", {}):
                raise ValueError("held impact request does not bind its original bundle/execution")
        for identifier, eid in wait.get("review_execution_ids", {}).items():
            execution = runtime.get("executions", {}).get(eid)
            if (identifier not in wait.get("review_requests", {}) or not execution
                    or execution.get("action", {}).get("input_basis", {}).get("impact_review") != wait["review_requests"][identifier]):
                raise ValueError("held impact review execution differs from its assigned request")
        recovery = wait.get("recovery", {})
        for field, family in (("owner_activity_id", "activities"), ("review_cycle_id", "review_cycles")):
            reference = recovery.get(field)
            if reference is not None and identifiers.get(reference, (None, None))[1] != family:
                raise ValueError("review recovery reference does not resolve: " + field)
