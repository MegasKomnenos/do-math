# -*- coding: utf-8 -*-
"""v8 명세 묶음을 v9로 복사하고 9차 초안의 결정을 선언·검사·시험에 반영한다.
각 원문이 지정 횟수만큼 정확히 있을 때만 파일별로 전부 적용한다."""
import importlib.metadata
import json
import platform
import shutil
import sys
from pathlib import Path

DOCS = Path(r"C:/math/docs/do-math")
V8 = DOCS / "통합-설계-명세-v8"
V9 = DOCS / "통합-설계-명세-v9"

if not V9.exists():
    shutil.copytree(V8, V9, ignore=shutil.ignore_patterns("__pycache__", "review"))
    (V9 / "review").mkdir()

PATCHES = {"build_spec.py": [], "verify_spec.py": [], "spec_checks.py": []}


def add(name, old, new, count=1):
    PATCHES[name].append((old, new, count))


B, V, S = "build_spec.py", "verify_spec.py", "spec_checks.py"

# ---------------- build_spec.py ----------------
add(B, '"""Generate v8 schemas and contracts from owned declarations and the draft."""',
    '"""Generate v9 schemas and contracts from owned declarations and the draft."""')
add(B, 'BASE = "https://do-math.invalid/schemas/draft/8/"\nVERSION = 8',
    'BASE = "https://do-math.invalid/schemas/draft/9/"\nVERSION = 9')
add(B, '              "x-contract-id": f"do-math-draft/{name}/8",',
    '              "x-contract-id": f"do-math-draft/{name}/9",')
add(B, '    props = {"schema_version": {"const": f"do-math-draft/{name}/8"}, **properties}',
    '    props = {"schema_version": {"const": f"do-math-draft/{name}/9"}, **properties}')
add(B, '''                 "remote_recovery": obj({"retention": DURATION, "supported_gap": DURATION,
                                         "inspection_method": S, "evidence_ref": ARTIFACT})})''',
    '''                 "remote_recovery": obj({"retention": DURATION, "supported_gap": DURATION,
                                         "inspection_method": S, "evidence_ref": ARTIFACT}),
                 "compaction": obj({"disabled": BOOL, "evidence_ref": ARTIFACT})})''')
add(B, '''end = obj({"kind": enum("output_accepted", "execution_incomplete", "cancelled", "start_failed"),
           "at": TIME, "cause": CAUSE, "actual_scope": RANGES, "remaining_scope": RANGES,
           "artifact_refs": REFS, "barrier_evidence_refs": REFS,
           "outstanding_reservation_ids": IDS, "next_owner": SUBJECT})''',
    '''end = optional({"kind": enum("output_accepted", "execution_incomplete", "cancelled", "start_failed"),
           "at": TIME, "cause": CAUSE, "actual_scope": RANGES, "remaining_scope": RANGES,
           "artifact_refs": REFS, "barrier_evidence_refs": REFS,
           "outstanding_reservation_ids": IDS, "next_owner": SUBJECT,
           "stop_reasons": array(obj({"provider_operation_id": ID,
               "stop_reason": enum("end_turn", "max_output", "context_overflow", "cancelled", "error")})),
           "overflow": obj({"component_tokens": array(obj({"component": S, "tokens": N}), 1), "limit": POS})},
           "overflow")
end["allOf"] = [{"if": {"properties": {"cause": {"properties": {"code": {"const": "context_overflow"}},
                                                  "required": ["code"]}}, "required": ["cause"]},
                 "then": require("overflow")}]''')
add(B, '''listing = obj({"snapshot_commit": OID, "scope": common("query_scope"),
    "total_count": N, "loaded_count": N, "truncated": BOOL, "items": array(listing_item),
    "shuffle_seed": HASH, "algorithm": {"const": "hmac-sort-v1"},
    "omitted_query": common("query_scope")})
transcript_entry = obj({"sequence": N, "role": enum("system", "user", "assistant", "tool"),
                        "content_ref": ARTIFACT, "execution_id": ID})
planning_input = obj({"candidate_listing": listing, "canon_listing": listing,
    "ongoing_refs": REFS, "recent_history": REFS, "preparation_history": REFS,
    "required_failure_refs": REFS, "configured_history_window": N, "actual_history_window": N,
    "canon_exposure": enum("full", "partial"), "full_canon_tokens": N,
    "partial_reason": S, "component_tokens": array(obj({"component": S, "tokens": N}))})''',
    '''listing = optional({"snapshot_commit": OID, "scope": common("query_scope"),
    "total_count": N, "loaded_count": N, "truncated": BOOL, "items": array(listing_item),
    "order": enum("id", "sealed_random"),
    "shuffle_seed": HASH, "algorithm": {"const": "hmac-sort-v1"},
    "omitted_query": common("query_scope")}, "shuffle_seed", "algorithm")
listing["allOf"] = [condition("order", "sealed_random", require("shuffle_seed", "algorithm")),
                    condition("order", "id", forbid("shuffle_seed", "algorithm"))]
transcript_entry = optional({"sequence": N, "role": enum("system", "user", "assistant", "tool"),
                        "content_ref": ARTIFACT, "execution_id": ID,
                        "restore_form": enum("full", "reference"),
                        "reference": obj({"call": S, "size_bytes": N})}, "reference")
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
    "component_tokens": array(obj({"component": S, "tokens": N}))}, "truncation_permission_ref")''')
add(B, '''    "planning_input": planning_input, "transcript": array(transcript_entry),
    "transcript_complete": BOOL, "continuity_broken": BOOL,
    "continuity_failure_refs": REFS, "token_count": N, "max_input_tokens": POS,
}, ["id", "snapshot_commit", "question", "scope", "output_schema_id", "profile_ref",
    "authority_refs", "common_documents", "role_documents", "governance_refs", "required_refs",
    "failure_refs", "read_scope", "provided_order", "token_count", "max_input_tokens"], prefix="IM")''',
    '''    "planning_input": planning_input, "transcript": array(transcript_entry),
    "transcript_complete": BOOL, "continuity_broken": BOOL,
    "continuity_break_cause": enum("permanent_loss", "context_overflow"),
    "continuity_failure_refs": REFS, "reference_read_refs": REFS,
    "token_count": N, "max_input_tokens": POS,
}, ["id", "snapshot_commit", "question", "scope", "output_schema_id", "profile_ref",
    "authority_refs", "common_documents", "role_documents", "governance_refs", "required_refs",
    "failure_refs", "read_scope", "provided_order", "reference_read_refs", "token_count", "max_input_tokens"], prefix="IM")''')
add(B, '''    "research_work": obj({"bundle_refs": REFS, "scope_report": array(scope_disposition),
        "remaining_scope_ids": STRINGS, "wait_request": common("optional_wait")}),''',
    '''    "research_plan": obj({"plan_ref": ARTIFACT, "bound_contracts": array(obj({
        "task_id": ID, "revision": POS, "contract_ref": EXACT}))}),
    "research_work": obj({"bundle_refs": REFS, "scope_report": array(scope_disposition),
        "remaining_scope_ids": STRINGS, "wait_request": common("optional_wait")}),''')
add(B, '''    "reserved_final_executions": N, "scope_manifest_ref": ARTIFACT,
    "continuity_broken": BOOL, "continuity_evidence_refs": REFS,
}, ["id", "review_lineage_id", "proposal_ref", "proposal_revision", "role_slots", "issues",''',
    '''    "reserved_final_executions": N, "scope_manifest_ref": ARTIFACT,
    "continuity_broken": BOOL, "continuity_break_cause": enum("permanent_loss", "context_overflow"),
    "continuity_evidence_refs": REFS,
}, ["id", "review_lineage_id", "proposal_ref", "proposal_revision", "role_slots", "issues",''')
add(B, '''register("review-plan", "11.3,19.6", "runtime/artifacts/{bundle_id}/review-plan.json", {
    "id": ID, "proposal_ref": ARTIFACT, "review_lineage_id": ID,
    "planner_execution_id": ID, "policy_ref": EXACT,
    "role_slots": array(role_slot, 3), "scope_allocations": array(obj({
        "slot_id": S, "item_ids": IDS, "conclusion_closures": array(obj({
            "conclusion_id": ID, "dependency_item_ids": IDS})),
        "checks_global_connections": BOOL, "required_inputs": NONEMPTY_REFS}), 3),
    "required_domains": STRINGS, "domain_reasons_ref": ARTIFACT,
    "transcript_refs": REFS, "execution_limit": POS, "initial_execution_count": POS,
    "reserved_organize_executions": POS, "reserved_answer_executions": N,
    "reserved_final_executions": {"type": "integer", "minimum": 6},
    "full_proposal_fits": BOOL, "scope_reconstruction_ref": ARTIFACT,
}, ["id", "proposal_ref", "review_lineage_id", "planner_execution_id", "policy_ref",
    "role_slots", "scope_allocations", "required_domains", "domain_reasons_ref", "transcript_refs",
    "execution_limit", "initial_execution_count", "reserved_organize_executions", "reserved_answer_executions",
    "reserved_final_executions", "full_proposal_fits"], prefix="VP")''',
    '''register("review-plan", "11.3,19.6", "runtime/artifacts/{bundle_id}/review-plan.json", {
    "id": ID, "proposal_ref": ARTIFACT, "review_lineage_id": ID,
    "planner_execution_id": ID, "policy_ref": EXACT,
    "role_slots": array(role_slot, 3),
    "required_domains": STRINGS, "domain_reasons_ref": ARTIFACT,
    "transcript_refs": REFS, "execution_limit": POS, "initial_execution_count": POS,
    "reserved_organize_executions": POS, "reserved_answer_executions": N,
    "reserved_final_executions": {"type": "integer", "minimum": 6},
    "input_measurement_ref": ARTIFACT,
}, ["id", "proposal_ref", "review_lineage_id", "planner_execution_id", "policy_ref",
    "role_slots", "required_domains", "domain_reasons_ref", "transcript_refs",
    "execution_limit", "initial_execution_count", "reserved_organize_executions", "reserved_answer_executions",
    "reserved_final_executions", "input_measurement_ref"], prefix="VP")''')
add(B, '    "codec_profile": {"const": "do-math-codec/8"},', '    "codec_profile": {"const": "do-math-codec/9"},')
add(B, '''    ("R15", "8.1", "Mandatory common/role/governance text, pending failures and issues are present before judgment; required exact inputs cannot be replaced by summaries.", ["V19", "V48", "V103", "V129", "V161", "V180"], "input"),''',
    '''    ("R15", "8.1", "Mandatory common/role/governance text, pending failures and issues are present before judgment; required exact inputs cannot be replaced by summaries; stable components precede per-round components; governance or common text that cannot fit escalates to the user.", ["V48", "V103", "V129", "V161", "V180", "V204"], "input"),''')
add(B, '''    ("R16", "8.3", "Same review slot receives complete ordered model-visible transcript; overflow is not loss; permanent loss requires recorded continuity break.", ["V144", "V145", "V146", "V166"], "input"),''',
    '''    ("R16", "8.3", "Same review slot receives its own messages in full and, uniformly, every tool-result body and prior proposal version as exact reference entries inside its read scope; overflow is classified into information-preserving reduction, self-repair or user escalation; a records-based replacement requires a user decision or general permission and records its cause.", ["V144", "V145", "V146", "V166", "V201", "V202", "V208", "V209"], "input"),''')
add(B, '''    ("R17", "8.5", "Full K is preferred if it fits with a minimum candidate; partial requires measured impossibility, snapshot population/counts and retrievable omissions.", ["V118", "V119", "V127", "V141", "V159", "V160", "V178", "V189"], "listing"),''',
    '''    ("R17", "8.5", "Both listings are supplied in full when they fit; history windows shrink first; if the listings still overflow the engine escalates to the user without truncating; truncation happens only under a recorded permission naming the list and order, with snapshot population/counts and retrievable omissions.", ["V118", "V119", "V127", "V141", "V160", "V178", "V206", "V207"], "listing"),''')
add(B, '''    ("R20", "9.3", "Exactly one disposition per supplied candidate; selected tasks belong to listing; sum requests per shared execution constraint respects its cap.", ["V120", "V183"], "plan"),''',
    '''    ("R20", "9.3", "Exactly one disposition per supplied candidate; dispositions name a listed task_id/revision and the engine binds exact refs in the activity result without editing plan bytes; a plan cut at max output is a receipt failure that escalates without retry and is not a selection failure; sum requests per shared execution constraint respects its cap.", ["V120", "V183", "V205"], "plan"),''')
add(B, '''    ("R23", "11.3", "Three basic perspectives plus every required domain and source fidelity; full proposal if it fits, otherwise each conclusion closure plus global links.", ["V44", "V47", "V90", "V162", "V177"], "review"),''',
    '''    ("R23", "11.3", "Three basic perspectives plus every required domain and source fidelity; every reviewer reads the full proposal; if it does not fit no review plan is made, the activity closes unresolved and the next plan returns restructuring to the author or asks the user for a larger profile; planners never split proposals.", ["V19", "V44", "V47", "V90", "V162", "V177"], "review"),''')
add(B, '''    ("R33", "13.1.1", "Repeated-work holds follow lineage and explicit continue decisions, not new IDs; proposal-limit decisions cannot be delegated.", ["V174", "V184"], "threshold"),''',
    '''    ("R33", "13.1.1", "Repeated-work holds follow lineage and explicit continue decisions, not new IDs; proposal-limit decisions cannot be delegated; overflow escalations from 8.3/9.3 and capacity shortages are not selection failures.", ["V174", "V184", "V205"], "threshold"),''')
add(B, '''    ("R39", "16.1,16.1.1", "Actual capability receipts are mandatory for support; fixture success is not proof of input injection, isolation or remote termination. The Windows adapter implements the documented non-inherited Job handle, suspended startup, authority-before-resume and observed termination conditions.", ["V33", "V61", "V106", "V140", "V194"], "adapter"),''',
    '''    ("R39", "16.1,16.1.1", "Actual capability receipts are mandatory for support; fixture success is not proof of input injection, isolation or remote termination. Adapters that cannot disable or report conversation compaction, return per-call stop reasons and per-result artifacts are not used for transcript-restoring activities. The Windows adapter implements the documented non-inherited Job handle, suspended startup, authority-before-resume and observed termination conditions.", ["V33", "V61", "V106", "V140", "V194", "V203"], "adapter"),''')
add(B, '''    ("R44", "11.1,11.7,17.3.1", "Quantifier order and witness dependencies are semantic obligations. A counterexample must meet every hypothesis and violate the conclusion; goal satisfaction follows the charter, not merely a proof of excluded middle.", ["V195", "V196"], "mathematics"),''',
    '''    ("R44", "11.1,11.7,17.3.1", "Quantifier order and witness dependencies are semantic obligations. A counterexample must meet every hypothesis and violate the conclusion; goal satisfaction follows the charter, not merely a proof of excluded middle.", ["V195", "V196"], "mathematics"),
    ("R45", "8.3,16.2", "A profile used for transcript restoration has compaction disabled with evidence; an overflowing call fails without compaction and the execution ends execution_incomplete with cause context_overflow and measured components; reference-form transcript entries lie within the execution's read scope.", ["V201", "V203", "V208"], "input"),''')
add(B, '''planning_input["required"].remove("partial_reason")
planning_input["allOf"] = [
    condition("canon_exposure", "partial", require("partial_reason")),
    condition("canon_exposure", "full", forbid("partial_reason")),
]''',
    '''planning_input["allOf"] = [
    {"if": {"anyOf": [{"properties": {"candidate_listing": {"properties": {"truncated": {"const": True}}}}},
                      {"properties": {"canon_listing": {"properties": {"truncated": {"const": True}}}}}]},
     "then": require("truncation_permission_ref")},
]''')
add(B, '''candidate_item = optional({
    "id": ID, "record_ref": EXACT, "revision": POS, "title": S,
    "description": {"type": "string", "minLength": 1, "pattern": r"^[^\\r\\n]+$"},
    "work_class": enum("research_production", "academic_validation"),
    "basis_refs": NONEMPTY_REFS, "review_status": enum("absent", "approved", "revision_required", "unresolved"),
    "review_ref": EXACT, "author_execution_ids": array(ID, 1, True),
}, "description", "review_ref")
candidate_item["allOf"] = [
    condition("review_status", "absent", forbid("review_ref")),
    {"if": {"properties": {"review_status": {"enum": ["approved", "revision_required", "unresolved"]}}},
     "then": require("review_ref")}]
canon_item = obj({
    "id": ID, "record_ref": EXACT,
    "declaration_kind": enum("definition", "theorem", "proof", "relation"),
    "declaration_names": array(S, 1, True),
    "explanation_links": array(obj({"explanation_ref": EXACT, "assessment_ref": EXACT,
        "use_ref": EXACT, "use_state": USE, "assessment_value": ASSESSMENT})),
    "valid_explanation_available": BOOL, "change_refs": REFS,
})''',
    '''candidate_view = optional({
    "revision": POS, "title": S,
    "description": {"type": "string", "minLength": 1, "pattern": r"^[^\\r\\n]+$"},
    "question": S, "scope": array(RANGE, 1), "excluded_scope": RANGES,
    "expected_research_change": S,
    "work_class": enum("research_production", "academic_validation"),
    "basis_ids": IDS, "review_status": enum("absent", "approved", "revision_required", "unresolved"),
}, "description")
candidate_refs = optional({"record_ref": EXACT, "basis_refs": NONEMPTY_REFS, "review_ref": EXACT,
                           "author_execution_ids": array(ID, 1, True)}, "review_ref")
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
    "valid_explanation_available": BOOL, "recently_changed": BOOL,
})
canon_refs = obj({
    "record_ref": EXACT,
    "explanation_links": array(obj({"explanation_ref": EXACT, "assessment_ref": EXACT,
        "use_ref": EXACT, "use_state": USE, "assessment_value": ASSESSMENT})),
    "change_refs": REFS,
})
canon_item = obj({"id": ID, "view": canon_view, "refs": canon_refs})''')
add(B, '''    {"if": {"properties": {"activity_kind": {"not": {"enum": ["research_preparation", "research_plan"]}}}},
     "then": forbid("planning_input")},
]''',
    '''    {"if": {"properties": {"activity_kind": {"not": {"enum": ["research_preparation", "research_plan"]}}}},
     "then": forbid("planning_input")},
    condition("continuity_broken", True, require("continuity_break_cause")),
    condition("continuity_broken", False, forbid("continuity_break_cause")),
]''')
add(B, '''review_plan["allOf"] = [condition("full_proposal_fits", False, require("scope_reconstruction_ref"))]
''', '')
add(B, '''issue_schema["required"].extend(["judge_slot_ids", "review_plan_ref"])''',
    '''issue_schema["required"].extend(["judge_slot_ids", "review_plan_ref"])
issue_schema["allOf"] = [condition("continuity_broken", True, require("continuity_break_cause")),
                         condition("continuity_broken", False, forbid("continuity_break_cause"))]''')
add(B, '''            "planning": "Exact proposal, policy, sources, domains, preserved planner transcript and execution capacity; calculate every mandatory stage allocation.",
            "reviewing": "Exact assigned scope and conclusion closure, proposal/sources/preflight, perspective and permitted slot transcript; no current peer verdicts.",
            "clarifying": "Exact output_phase and role_slot_id. organize receives all published issues and missing-scope evidence; answer receives the original objection, all judge replies and its author's preserved transcript.",
            "judging": "Exact proposal, all initial findings, objections, supplements, prior answers and own transcript; no current peer judge verdicts.",''',
    '''            "planning": "Exact proposal, policy, sources, domains, measured input fit, own restored transcript and execution capacity; calculate every mandatory stage allocation; no plan when the full proposal does not fit.",
            "reviewing": "Exact full proposal, sources, preflight, perspective and own restored transcript with tool-result bodies and prior versions as reference entries; no current peer verdicts.",
            "clarifying": "Exact output_phase and role_slot_id. organize receives all published issues and missing-scope evidence; answer receives the original objection, all judge replies and its author's own restored transcript.",
            "judging": "Exact proposal, all initial findings, objections, supplements, prior answers and own restored transcript; no current peer judge verdicts.",''')
add(B, '''            "planning": "Allocate scope, expertise, slots and execution counts; no identity approval.",''',
    '''            "planning": "Allocate expertise, slots and execution counts for a proposal that fits in full; return restructuring when it does not; no identity approval.",''')
add(B, '"version": 8,', '"version": 9,', 7)
add(B, '    rows = ["# v8 규범 명세 묶음", "",', '    rows = ["# v9 규범 명세 묶음", "",')
add(B, '        "x-contract-id": "do-math-draft/common/8", "x-owner-section": "19.2",',
    '        "x-contract-id": "do-math-draft/common/9", "x-owner-section": "19.2",')

# ---------------- verify_spec.py ----------------
add(V, 'BASE = "https://do-math.invalid/schemas/draft/8/"', 'BASE = "https://do-math.invalid/schemas/draft/9/"')
add(V, '''    elif family == "review-plan":
        slots = value["role_slots"]
        ids = [s["id"] for s in slots]
        allocation_ids = [a["slot_id"] for a in value["scope_allocations"]]
        if len(ids) != len(set(ids)) or len(allocation_ids) != len(set(allocation_ids)) or set(ids) != set(allocation_ids):
            raise checks.ContractError("review slot/allocation mismatch or duplicate")
        expected_views = {"argument_reconstruction", "adversarial_scope", "semantic_identity",
                          *("domain_expertise:" + d for d in value["required_domains"])}
        if not expected_views <= {s["perspective"] for s in slots}:
            raise checks.ContractError("missing required review perspective")
        n = value["initial_execution_count"]
        allocation = checks.review_execution_allocation(n,
            organize_count=value["reserved_organize_executions"],
            answer_count=value["reserved_answer_executions"], judge_count=value["reserved_final_executions"])
        if n != len(slots) or sum(allocation.values()) > value["execution_limit"]:
            raise checks.ContractError("review plan cannot fund mandatory allocation")
        universe = set(value["proposal_item_ids"])
        by_slot = {s["id"]: s for s in slots}
        for allocation in value["scope_allocations"]:
            covered = set(allocation["item_ids"])
            if not covered <= universe or set(by_slot[allocation["slot_id"]]["scope_item_ids"]) != covered:
                raise checks.ContractError("invalid scope allocation")
            if value["full_proposal_fits"] and covered != universe:
                raise checks.ContractError("full proposal must be read by every reviewer")
        if not all(any(a["checks_global_connections"] and by_slot[a["slot_id"]]["perspective"] == view
                       for a in value["scope_allocations"]) for view in expected_views):
            raise checks.ContractError("missing whole-proposal connection review")
        for conclusion in value["conclusion_dependencies"]:
            closure = {conclusion["conclusion_id"], *conclusion["dependency_item_ids"]}
            if not closure <= universe:
                raise checks.ContractError("conclusion references unknown item")
            for view in expected_views:
                if not any(closure <= set(a["item_ids"]) and by_slot[a["slot_id"]]["perspective"] == view
                           for a in value["scope_allocations"]):
                    raise checks.ContractError("conclusion closure split across reviewer assignments")''',
    '''    elif family == "review-plan":
        slots = value["role_slots"]
        ids = [s["id"] for s in slots]
        if len(ids) != len(set(ids)):
            raise checks.ContractError("duplicate review slot")
        expected_views = {"argument_reconstruction", "adversarial_scope", "semantic_identity",
                          *("domain_expertise:" + d for d in value["required_domains"])}
        if not expected_views <= {s["perspective"] for s in slots}:
            raise checks.ContractError("missing required review perspective")
        n = value["initial_execution_count"]
        allocation = checks.review_execution_allocation(n,
            organize_count=value["reserved_organize_executions"],
            answer_count=value["reserved_answer_executions"], judge_count=value["reserved_final_executions"])
        if n != len(slots) or sum(allocation.values()) > value["execution_limit"]:
            raise checks.ContractError("review plan cannot fund mandatory allocation")
        universe = set(value["proposal_item_ids"])
        for slot in slots:
            if set(slot["scope_item_ids"]) != universe:
                raise checks.ContractError("every reviewer must be assigned the full proposal")
        for conclusion in value["conclusion_dependencies"]:
            closure = {conclusion["conclusion_id"], *conclusion["dependency_item_ids"]}
            if not closure <= universe:
                raise checks.ContractError("conclusion references unknown item")''')
add(V, '''    elif family == "input-manifest":
        if value["token_count"] > value["max_input_tokens"]:
            raise checks.ContractError("context_overflow")
        planning = value.get("planning_input")
        if planning:
            for key in ("candidate_listing", "canon_listing"):
                listing = planning[key]
                ids = [item["id"] for item in listing["items"]]
                if (len(ids) != len(set(ids)) or listing["loaded_count"] != len(ids)
                    or listing["total_count"] < len(ids)
                    or listing["truncated"] != (len(ids) < listing["total_count"])):
                    raise checks.ContractError("listing population/count/truncation mismatch")
            if planning["canon_exposure"] == "full" and planning["canon_listing"]["truncated"]:
                raise checks.ContractError("full canon exposure cannot be truncated")
            for item in planning["canon_listing"]["items"]:
                valid_link = any(link["use_state"] == "active" and link["assessment_value"] == "match"
                                 for link in item["explanation_links"])
                if item["valid_explanation_available"] != valid_link:
                    raise checks.ContractError("canon explanation availability is incorrect")''',
    '''    elif family == "input-manifest":
        if value["token_count"] > value["max_input_tokens"]:
            raise checks.ContractError("context_overflow")
        for entry in value.get("transcript", []):
            if entry["restore_form"] == "reference" and entry["content_ref"] not in value["reference_read_refs"]:
                raise checks.ContractError("reference-form transcript entry outside read scope")
        planning = value.get("planning_input")
        if planning:
            for key in ("candidate_listing", "canon_listing"):
                listing = planning[key]
                ids = [item["id"] for item in listing["items"]]
                if (len(ids) != len(set(ids)) or listing["loaded_count"] != len(ids)
                    or listing["total_count"] < len(ids)
                    or listing["truncated"] != (len(ids) < listing["total_count"])):
                    raise checks.ContractError("listing population/count/truncation mismatch")
            if planning["candidate_listing"]["order"] != "sealed_random":
                raise checks.ContractError("candidate listing must use the sealed random order")
            if planning["canon_listing"]["order"] != "id" and not planning["canon_listing"]["truncated"]:
                raise checks.ContractError("full canon listing must be in ID order")
            for item in planning["canon_listing"]["items"]:
                links = item["refs"]["explanation_links"]
                states = [{"assessment_value": link["assessment_value"], "use_state": link["use_state"]} for link in links]
                valid_link = any(link["use_state"] == "active" and link["assessment_value"] == "match" for link in links)
                view = item["view"]
                if (view["explanation_states"] != states or view["valid_explanation_available"] != valid_link
                        or view["recently_changed"] != bool(item["refs"]["change_refs"])):
                    raise checks.ContractError("canon view does not match its references")''')
add(V, '''            value["max_input_tokens"] = 100
            value["planning_input"]["actual_preparation_history_window"] = 0''',
    '''            value["max_input_tokens"] = 100
            value["planning_input"]["actual_preparation_history_window"] = 0
            value["planning_input"]["candidate_listing"].update(order="sealed_random", shuffle_seed="1" * 64, algorithm="hmac-sort-v1")
            value["planning_input"]["canon_listing"].update(order="id")
            value["planning_input"]["canon_listing"].pop("shuffle_seed", None)
            value["planning_input"]["canon_listing"].pop("algorithm", None)''')
add(V, '''        if family == "review-plan":
            value.update(initial_execution_count=3, execution_limit=14, reserved_organize_executions=1, reserved_answer_executions=3,
                         reserved_final_executions=6, full_proposal_fits=True, required_domains=[],
                         final_judge_slot_ids=["judge-1", "judge-2", "judge-3"])
            value.pop("scope_reconstruction_ref", None)
            item = "MATH-" + "0" * 25 + "1"
            value["proposal_item_ids"] = [item]
            value["conclusion_dependencies"] = [{"conclusion_id": item, "dependency_item_ids": []}]
            for i, (slot, assignment) in enumerate(zip(value["role_slots"], value["scope_allocations"])):
                slot.update(id="reviewer-" + str(i + 1), perspective=["argument_reconstruction", "adversarial_scope", "semantic_identity"][i],
                            scope_item_ids=[item])
                assignment.update(slot_id=slot["id"], item_ids=[item], checks_global_connections=True,
                                  conclusion_closures=[{"conclusion_id": item, "dependency_item_ids": []}])''',
    '''        if family == "review-plan":
            value.update(initial_execution_count=3, execution_limit=14, reserved_organize_executions=1, reserved_answer_executions=3,
                         reserved_final_executions=6, required_domains=[],
                         final_judge_slot_ids=["judge-1", "judge-2", "judge-3"])
            item = "MATH-" + "0" * 25 + "1"
            value["proposal_item_ids"] = [item]
            value["conclusion_dependencies"] = [{"conclusion_id": item, "dependency_item_ids": []}]
            for i, slot in enumerate(value["role_slots"]):
                slot.update(id="reviewer-" + str(i + 1), perspective=["argument_reconstruction", "adversarial_scope", "semantic_identity"][i],
                            scope_item_ids=[item])''')
add(V, '        self.assertEqual(lock["codec_profile"], "do-math-codec/8")',
    '        self.assertEqual(lock["codec_profile"], "do-math-codec/9")')
add(V, '''    def test_full_canon_priority_and_skip_large_candidate(self):
        result = checks.pack_listings([9, 3, 2], [4, 3], 10)
        self.assertEqual(result, {"mode": "full", "candidates": [1], "canon": [0, 1], "remaining": 0})

    def test_partial_minimum_pair_search(self):
        result = checks.pack_listings([9, 3], [7, 7], 10)
        self.assertEqual(result["mode"], "partial")
        self.assertEqual(result["candidates"], [1])
        self.assertEqual(result["canon"], [0])
        with self.assertRaises(checks.ContractError):
            checks.pack_listings([8], [8], 10)''',
    '''    def test_listings_fit_or_escalate_without_permission(self):
        result = checks.pack_listings([3, 2], [4, 1], 10)
        self.assertEqual(result, {"mode": "full", "candidates": [0, 1], "canon": [0, 1], "remaining": 0})
        with self.assertRaises(checks.ContractError):
            checks.pack_listings([9, 3, 2], [4, 3], 10)

    def test_truncation_only_under_named_permission(self):
        result = checks.pack_listings([9, 3, 2], [4, 3], 10, permission={"lists": ["candidates"]})
        self.assertEqual(result["mode"], "truncated")
        self.assertEqual((result["candidates"], result["canon"]), ([1], [0, 1]))
        with self.assertRaises(checks.ContractError):
            checks.pack_listings([2], [7, 7], 10, permission={"lists": ["candidates"]})
        result = checks.pack_listings([2], [7, 7], 10, permission={"lists": ["canon"]})
        self.assertEqual((result["candidates"], result["canon"]), ([0], [0]))
        with self.assertRaises(checks.ContractError):
            checks.pack_listings([2], [7, 7], 10, permission={"lists": ["history"]})

    def test_overflow_disposition_and_restore_forms(self):
        self.assertEqual(checks.overflow_disposition(reducible_by_window=True, tool_accumulation=False,
                                                     activity_kind="research_plan"), "reduce_history")
        self.assertEqual(checks.overflow_disposition(reducible_by_window=False, tool_accumulation=True,
                                                     activity_kind="research_work"), "checkpoint_resume")
        self.assertEqual(checks.overflow_disposition(reducible_by_window=False, tool_accumulation=True,
                                                     activity_kind="identity_review", restored_fits=True), "reference_restore")
        self.assertEqual(checks.overflow_disposition(reducible_by_window=False, tool_accumulation=True,
                                                     activity_kind="identity_review", restored_fits=False), "escalate")
        self.assertEqual(checks.overflow_disposition(reducible_by_window=False, tool_accumulation=False,
                                                     activity_kind="research_plan"), "escalate")
        with self.assertRaises(checks.ContractError):
            checks.overflow_disposition(reducible_by_window=False, tool_accumulation=True, activity_kind="identity_review")
        entries = [{"role": "system"}, {"role": "user"}, {"role": "assistant"}, {"role": "tool"},
                   {"role": "user", "prior_version": True}, {"role": "assistant"}]
        self.assertEqual(checks.restore_forms(entries), ["full", "full", "full", "reference", "reference", "full"])
        with self.assertRaises(checks.ContractError):
            checks.restore_forms([{"role": "tool", "relevance_hint": "needed"}])

    def test_plan_binding_and_output_truncation(self):
        manifest = read_example("input-manifest")
        item = sample(SCHEMAS["input-manifest"]["properties"]["planning_input"]["properties"]["candidate_listing"]["properties"]["items"]["items"])
        item["id"] = "T-" + "0" * 25 + "1"
        item["view"]["revision"] = 2
        manifest["planning_input"]["candidate_listing"].update(items=[item], total_count=1, loaded_count=1)
        validate("input-manifest", manifest)
        plan = read_example("plan")
        plan["candidate_dispositions"] = [{"task_id": item["id"], "revision": 2, "value": "not_selected", "reason": "held",
                                           "information_status": "evidence", "uncertainty": "none", "read_scope_refs": []}]
        plan["dispatch_order"] = []
        validate("plan", plan)
        bound = checks.check_plan_binding(plan, manifest)
        self.assertEqual(bound[(item["id"], 2)], item["refs"]["record_ref"])
        plan["candidate_dispositions"][0]["task_id"] = "T-" + "0" * 25 + "2"
        with self.assertRaises(checks.ContractError):
            checks.check_plan_binding(plan, manifest)
        self.assertEqual(checks.plan_receipt_disposition("max_output"), "escalate_user_decision")
        self.assertEqual(checks.plan_receipt_disposition("end_turn"), "receive")

    def test_restoration_profile_requires_compaction_control(self):
        profile = read_example("execution-profile")
        with self.assertRaises(checks.ContractError):
            checks.check_restoration_profile(profile, "identity_review")
        profile["ai"]["compaction"]["disabled"] = True
        self.assertTrue(checks.check_restoration_profile(profile, "identity_review"))
        self.assertTrue(checks.check_restoration_profile(read_example("execution-profile"), "research_work"))''')
add(V, '''        self.assertEqual(set(ids), {"V" + str(i).zfill(2) for i in range(1, 201)})
        self.assertEqual(len(ids), 200)''',
    '''        self.assertEqual(set(ids), {"V" + str(i).zfill(2) for i in range(1, 210)})
        self.assertEqual(len(ids), 209)
        retired = {v["id"] for v in mapping["vectors"] if v["expected"] == "번호 미재사용"}
        self.assertEqual(retired, {"V159", "V189"})
        rules = checks.parse_json((ROOT / "semantic-rules.json").read_bytes())["rules"]
        for rule in rules:
            self.assertFalse(retired & set(rule["source_vectors"]), rule["id"])
        for q in mapping["quality_contracts"]:
            self.assertFalse(retired & set(q["source_vectors"]), q["id"])''')
add(V, '''        value = read_example("review-plan")
        value["full_proposal_fits"] = False
        with self.assertRaises(checks.ContractError):
            validate("review-plan", value)''',
    '''        value = read_example("review-plan")
        value["role_slots"][2]["scope_item_ids"] = []
        with self.assertRaises(checks.ContractError):
            validate("review-plan", value)''')
add(V, '''    def test_regression_full_has_no_partial_reason(self):
        value = read_example("input-manifest")
        validate("input-manifest", value)
        value["planning_input"]["partial_reason"] = "invented"
        with self.assertRaises(checks.ContractError):
            validate("input-manifest", value)
        value["planning_input"].update(canon_exposure="partial")
        validate("input-manifest", value)''',
    '''    def test_regression_truncation_requires_recorded_permission(self):
        value = read_example("input-manifest")
        validate("input-manifest", value)
        value["planning_input"]["candidate_listing"].update(total_count=5, truncated=True)
        with self.assertRaises(checks.ContractError):
            validate("input-manifest", value)
        value["planning_input"]["truncation_permission_ref"] = value["profile_ref"]
        validate("input-manifest", value)
        value["planning_input"]["canon_listing"].update(order="sealed_random", shuffle_seed="1" * 64, algorithm="hmac-sort-v1")
        with self.assertRaises(checks.ContractError):
            validate("input-manifest", value)
        value["continuity_broken"] = True
        with self.assertRaises(checks.ContractError):
            validate("input-manifest", value)''')
add(V, '''        candidate_shape = props["candidate_listing"]["properties"]["items"]["items"]
        item = sample(candidate_shape)
        self.assertNotIn("description", item)
        validator(candidate_shape).validate(item)
        for key in ("revision", "work_class", "basis_refs", "author_execution_ids"):
            changed = copy.deepcopy(item)
            changed.pop(key)
            self.assertFalse(validator(candidate_shape).is_valid(changed), key)
        canon_shape = props["canon_listing"]["properties"]["items"]["items"]
        item = sample(canon_shape)
        for key in ("declaration_kind", "declaration_names", "explanation_links", "valid_explanation_available"):
            changed = copy.deepcopy(item)
            changed.pop(key)
            self.assertFalse(validator(canon_shape).is_valid(changed), key)''',
    '''        candidate_shape = props["candidate_listing"]["properties"]["items"]["items"]
        item = sample(candidate_shape)
        self.assertNotIn("description", item["view"])
        validator(candidate_shape).validate(item)
        for key in ("revision", "question", "scope", "expected_research_change", "work_class", "basis_ids", "review_status"):
            changed = copy.deepcopy(item)
            changed["view"].pop(key)
            self.assertFalse(validator(candidate_shape).is_valid(changed), key)
        for key in ("record_ref", "basis_refs", "author_execution_ids"):
            changed = copy.deepcopy(item)
            changed["refs"].pop(key)
            self.assertFalse(validator(candidate_shape).is_valid(changed), key)
        canon_shape = props["canon_listing"]["properties"]["items"]["items"]
        item = sample(canon_shape)
        for key in ("declaration_kind", "declaration_names", "explanation_states", "valid_explanation_available", "recently_changed"):
            changed = copy.deepcopy(item)
            changed["view"].pop(key)
            self.assertFalse(validator(canon_shape).is_valid(changed), key)
        for key in ("record_ref", "explanation_links", "change_refs"):
            changed = copy.deepcopy(item)
            changed["refs"].pop(key)
            self.assertFalse(validator(canon_shape).is_valid(changed), key)''')
add(V, '''        "source_vectors": {"total": 200, "runtime_execution": "not_run"},''',
    '''        "source_vectors": {"total": len(checks.parse_json((ROOT / "source-vector-map.json").read_bytes())["vectors"]),
                           "retired": ["V159", "V189"], "runtime_execution": "not_run"},''')
add(V, '''        "not_verified": ["actual_adapter", "OS_isolation", "remote_termination", "provider_limits",''',
    '''        "not_verified": ["actual_adapter", "adapter_compaction_control", "OS_isolation", "remote_termination", "provider_limits",''')

# ---------------- spec_checks.py ----------------
add(S, '''def pack_listings(candidates, canon, budget):
    """Costs are measured caller inputs; this does not implement a tokenizer."""
    if type(budget) is not int or budget < 0 or any(type(x) is not int or x <= 0 for x in candidates + canon):
        raise ContractError("invalid measured token costs")
    total_k = sum(canon)
    if total_k <= budget and (not candidates or any(x + total_k <= budget for x in candidates)):
        selected_c, remaining = [], budget - total_k
        for i, cost in enumerate(candidates):
            if cost <= remaining:
                selected_c.append(i)
                remaining -= cost
        return {"mode": "full", "candidates": selected_c, "canon": list(range(len(canon))), "remaining": remaining}
    selected_c, selected_k, remaining = [], [], budget
    if candidates and canon:
        found = next(((i, j) for i, c in enumerate(candidates) for j, k in enumerate(canon)
                      if c + k <= budget), None)
        if found is None:
            raise ContractError("context_overflow")
        i, j = found
        selected_c, selected_k = [i], [j]
        remaining -= candidates[i] + canon[j]
    for i in range(max(len(candidates), len(canon), 1)):
        if i < len(candidates) and i not in selected_c and candidates[i] <= remaining:
            selected_c.append(i)
            remaining -= candidates[i]
        if i < len(canon) and i not in selected_k and canon[i] <= remaining:
            selected_k.append(i)
            remaining -= canon[i]
    if candidates and not selected_c or canon and not selected_k:
        raise ContractError("context_overflow")
    return {"mode": "partial", "candidates": selected_c, "canon": selected_k, "remaining": remaining}''',
    '''def pack_listings(candidates, canon, budget, permission=None):
    """Costs are measured caller inputs in their sealed order; this does not implement a tokenizer.

    Without a recorded truncation permission an overflow escalates to the user instead of cutting."""
    if type(budget) is not int or budget < 0 or any(type(x) is not int or x <= 0 for x in candidates + canon):
        raise ContractError("invalid measured token costs")
    if sum(candidates) + sum(canon) <= budget:
        return {"mode": "full", "candidates": list(range(len(candidates))),
                "canon": list(range(len(canon))), "remaining": budget - sum(candidates) - sum(canon)}
    if permission is None:
        raise ContractError("context_overflow_escalate")
    allowed = set(permission.get("lists", []))
    if not allowed or not allowed <= {"candidates", "canon"}:
        raise ContractError("truncation permission must name candidates and/or canon")
    remaining = budget

    def greedy(costs):
        nonlocal remaining
        chosen = []
        for index, cost in enumerate(costs):
            if cost <= remaining:
                chosen.append(index)
                remaining -= cost
        return chosen

    if "canon" in allowed:
        selected_k = greedy(canon)
    else:
        if sum(canon) > remaining:
            raise ContractError("context_overflow_escalate")
        selected_k, remaining = list(range(len(canon))), remaining - sum(canon)
    if "candidates" in allowed:
        selected_c = greedy(candidates)
    else:
        if sum(candidates) > remaining:
            raise ContractError("context_overflow_escalate")
        selected_c, remaining = list(range(len(candidates))), remaining - sum(candidates)
    return {"mode": "truncated", "candidates": selected_c, "canon": selected_k,
            "remaining": remaining, "permission": permission}


def overflow_disposition(*, reducible_by_window, tool_accumulation, activity_kind, restored_fits=None):
    """8.3 overflow classification: information-preserving reduction, self-repair, or user escalation."""
    if type(reducible_by_window) is not bool or type(tool_accumulation) is not bool:
        raise ContractError("overflow facts must be confirmed booleans")
    if reducible_by_window:
        return "reduce_history"
    if tool_accumulation:
        if activity_kind == "research_work":
            return "checkpoint_resume"
        if activity_kind == "identity_review":
            if type(restored_fits) is not bool:
                raise ContractError("reference restoration must be measured before deciding")
            return "reference_restore" if restored_fits else "escalate"
    return "escalate"


def restore_forms(entries):
    """Uniform restore form per role; relevance-based selection is never allowed."""
    forms = []
    for entry in entries:
        if "relevance_hint" in entry:
            raise ContractError("relevance-based transcript selection forbidden")
        role = entry["role"]
        if role == "tool":
            forms.append("reference")
        elif role in ("system", "assistant"):
            forms.append("full")
        elif role == "user":
            forms.append("reference" if entry.get("prior_version") else "full")
        else:
            raise ContractError("unknown transcript role")
    return forms


def check_plan_binding(plan, manifest):
    """Dispositions name listed task_id/revision pairs; the engine binds exact refs, never the plan bytes."""
    listed = {}
    for item in manifest["planning_input"]["candidate_listing"]["items"]:
        listed[(item["id"], item["view"]["revision"])] = item["refs"]["record_ref"]
    given = [(row["task_id"], row["revision"]) for row in plan["candidate_dispositions"]]
    if len(given) != len(set(given)) or set(given) != set(listed):
        raise ContractError("dispositions must cover exactly the listed candidates")
    return {key: listed[key] for key in given}


def plan_receipt_disposition(stop_reason):
    if stop_reason == "max_output":
        return "escalate_user_decision"
    if stop_reason == "end_turn":
        return "receive"
    raise ContractError("plan receipt needs a terminal stop reason")


def check_restoration_profile(profile, activity_kind):
    if activity_kind == "identity_review":
        compaction = profile.get("ai", {}).get("compaction")
        if not compaction or compaction.get("disabled") is not True:
            raise ContractError("transcript restoration requires an adapter with compaction disabled")
    return True''')


def main():
    failures = []
    texts = {}
    for name, pairs in PATCHES.items():
        path = V9 / name
        text = path.read_text(encoding="utf-8")
        for i, (old, new, count) in enumerate(pairs, 1):
            c = text.count(old)
            if c != count:
                failures.append((name, i, c, count, old[:70].replace("\n", "\\n")))
        texts[name] = text
    if failures:
        for f in failures:
            print("FAIL", f)
        sys.exit(1)
    for name, pairs in PATCHES.items():
        text = texts[name]
        for old, new, count in pairs:
            text = text.replace(old, new)
        (V9 / name).write_text(text, encoding="utf-8", newline="\n")
        print("patched", name, len(pairs))
    lock = {"codec_profile": "do-math-codec/9", "implementation": platform.python_implementation(),
            "packages": {p: importlib.metadata.version(p) for p in ("PyYAML", "jsonschema", "referencing")},
            "python": platform.python_version()}
    (V9 / "toolchain-lock.json").write_text(json.dumps(lock, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                                            encoding="utf-8", newline="\n")
    print("lock", lock)


if __name__ == "__main__":
    main()
