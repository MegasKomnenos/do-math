"""Pure specification checks; no process, network, Git or model authority."""
from __future__ import annotations

import copy
import hashlib
import json
import re
import unicodedata
from decimal import Decimal
from pathlib import PurePosixPath

import yaml


class ContractError(ValueError):
    pass


def duration_ms(value):
    match = re.fullmatch(r"PT(?=\d)(?:(\d+)H)?(?:(\d+)M)?(?:(\d+(?:\.\d{1,3})?)S)?", value)
    if not match:
        raise ContractError("duration: hours/minutes/seconds, at most millisecond precision")
    h, m, s = (Decimal(x or "0") for x in match.groups())
    result = (h * 3600 + m * 60 + s) * 1000
    if result <= 0 or result > 9007199254740991:
        raise ContractError("duration: positive safe millisecond integer required")
    return int(result)


def safe_path(value):
    if not isinstance(value, str) or not value or value.startswith("/") or "\\" in value:
        return False
    parts = value.split("/")
    devices = {"CON", "PRN", "AUX", "NUL", *("COM" + str(i) for i in range(1, 10)),
               *("LPT" + str(i) for i in range(1, 10))}
    for part in parts:
        if not part or part in (".", "..") or part[-1] in ". ":
            return False
        if any(ord(c) < 32 or c in '<>:"|?*' for c in part):
            return False
        if part.split(".")[0].upper() in devices:
            return False
    return True


def normalize(value):
    if value is None or type(value) is bool:
        return value
    if type(value) is int:
        if abs(value) > 9007199254740991:
            raise ContractError("large integer requires a typed string")
        return value
    if isinstance(value, str):
        if any(0xD800 <= ord(c) <= 0xDFFF for c in value):
            raise ContractError("surrogate code points are not Unicode scalar values")
        return unicodedata.normalize("NFC", value)
    if isinstance(value, list):
        return [normalize(x) for x in value]
    if isinstance(value, dict):
        result = {}
        for key, item in value.items():
            if not isinstance(key, str):
                raise ContractError("object keys must be strings")
            key = normalize(key)
            if key in result:
                raise ContractError("NFC key collision")
            result[key] = normalize(item)
        return result
    raise ContractError("floating point and non-JSON values are forbidden")


def unique_pairs(pairs):
    result, original = {}, set()
    for key, value in pairs:
        if key in original:
            raise ContractError("duplicate source key")
        original.add(key)
        nkey = normalize(key)
        if nkey in result:
            raise ContractError("NFC key collision")
        result[nkey] = value
    return result


def parse_json(data):
    if isinstance(data, bytes):
        if data.startswith(b"\xef\xbb\xbf"):
            raise ContractError("BOM forbidden")
        data = data.decode("utf-8", errors="strict")
    if data.startswith("\ufeff"):
        raise ContractError("BOM forbidden")
    def no_float(value):
        raise ContractError("floating point forbidden")
    return normalize(json.loads(data, object_pairs_hook=unique_pairs,
                                parse_float=no_float, parse_constant=no_float))


def canonical_json(value):
    return (json.dumps(normalize(value), ensure_ascii=False, allow_nan=False,
                       sort_keys=True, indent=2) + "\n").encode("utf-8")


class JsonScalarLoader(yaml.SafeLoader):
    pass


# YAML 1.2 JSON-compatible scalar resolution; disable YAML 1.1 implicit timestamps/bools.
JsonScalarLoader.yaml_implicit_resolvers = {}
JsonScalarLoader.add_implicit_resolver("tag:yaml.org,2002:bool", re.compile(r"^(?:true|false)$"), list("tf"))
JsonScalarLoader.add_implicit_resolver("tag:yaml.org,2002:null", re.compile(r"^null$"), ["n"])
JsonScalarLoader.add_implicit_resolver("tag:yaml.org,2002:int", re.compile(r"^-?(?:0|[1-9]\d*)$"), list("-0123456789"))
JsonScalarLoader.add_implicit_resolver("tag:yaml.org,2002:float",
    re.compile(r"^-?(?:0|[1-9]\d*)(?:\.\d+|[eE][+-]?\d+|\.\d+[eE][+-]?\d+)$"), list("-0123456789"))


def yaml_mapping(loader, node):
    if not isinstance(node, yaml.MappingNode):
        raise ContractError("mapping required")
    pairs = []
    for key, value in node.value:
        if key.value == "<<":
            raise ContractError("merge key forbidden")
        if key.tag != "tag:yaml.org,2002:str":
            raise ContractError("YAML keys must be strings")
        pairs.append((loader.construct_object(key, deep=True), loader.construct_object(value, deep=True)))
    return unique_pairs(pairs)


JsonScalarLoader.add_constructor("tag:yaml.org,2002:map", yaml_mapping)


def parse_knowledge(data):
    if isinstance(data, bytes):
        if data.startswith(b"\xef\xbb\xbf"):
            raise ContractError("BOM forbidden")
        data = data.decode("utf-8", errors="strict")
    if data.startswith("\ufeff"):
        raise ContractError("BOM forbidden")
    data = data.replace("\r\n", "\n").replace("\r", "\n")
    lines = data.split("\n")
    if not lines or lines[0] != "---":
        raise ContractError("frontmatter must begin at first line")
    try:
        end = lines.index("---", 1)
    except ValueError as error:
        raise ContractError("frontmatter delimiter missing") from error
    raw = "\n".join(lines[1:end])
    for token in yaml.scan(raw, Loader=JsonScalarLoader):
        if isinstance(token, (yaml.tokens.AliasToken, yaml.tokens.AnchorToken, yaml.tokens.TagToken,
                              yaml.tokens.DocumentStartToken, yaml.tokens.DocumentEndToken)):
            raise ContractError("tags, aliases, anchors and multiple YAML documents forbidden")
    front = yaml.load(raw, Loader=JsonScalarLoader)
    if not isinstance(front, dict):
        raise ContractError("frontmatter mapping required")
    front = normalize(front)
    # Schema, not the codec, determines whether any null value is permitted.
    body = "\n".join(lines[end + 1:])
    if body.startswith("\n"):
        body = body[1:]
    return front, body


def yaml_atom(value):
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False)
    if value is None:
        return "null"
    if type(value) is bool:
        return "true" if value else "false"
    if type(value) is int:
        return str(value)
    raise ContractError("not a scalar")


def yaml_lines(value, indent=0):
    pad = " " * indent
    if isinstance(value, dict):
        if not value:
            return [pad + "{}"]
        result = []
        for key in sorted(value):
            # Schema keys are conservative; arbitrary source keys are quoted.
            label = key if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_-]*", key) else yaml_atom(key)
            item = value[key]
            if isinstance(item, (dict, list)) and item:
                result.append(pad + label + ":")
                result.extend(yaml_lines(item, indent + 2))
            else:
                encoded = "{}" if item == {} else "[]" if item == [] else yaml_atom(item)
                result.append(pad + label + ": " + encoded)
        return result
    if isinstance(value, list):
        result = []
        for item in value:
            if isinstance(item, (dict, list)) and item:
                result.append(pad + "-")
                result.extend(yaml_lines(item, indent + 2))
            else:
                encoded = "{}" if item == {} else "[]" if item == [] else yaml_atom(item)
                result.append(pad + "- " + encoded)
        return result or [pad + "[]"]
    return [pad + yaml_atom(value)]


def canonical_knowledge(data):
    front, body = parse_knowledge(data)
    # Body content, including Unicode normalization, is never rewritten.
    output = "---\n" + "\n".join(yaml_lines(front)) + "\n---\n\n" + body.rstrip("\n") + "\n"
    return output.encode("utf-8")


def validate_budget(record):
    seen = set()
    for c in record["constraints"]:
        if c["id"] in seen:
            raise ContractError("duplicate constraint ID")
        seen.add(c["id"])
        if c["kind"] == "concurrency" and c["work_slots"] + c["operations_slots"] > c["total_slots"]:
            raise ContractError("work plus operations exceeds total")


def validate_reservation(record):
    if record["confirmed_consumed"] + record["returned"] > record["reserved"]:
        raise ContractError("reservation returned/consumed twice")
    if record["state"] in ("settled", "unrecoverable") and not record["evidence_refs"]:
        raise ContractError("settlement/loss requires evidence")
    if record["state"] == "settled" and record["confirmed_consumed"] + record["returned"] != record["reserved"]:
        raise ContractError("settled reservation still has unaccounted balance")


def review_execution_allocation(initial_count, *, organize_count=1, answer_count=None,
                                judge_count=None, objection_round_limit=3):
    """Mandatory stages for the resolved policy; None checks structure only."""
    if objection_round_limit is not None and (
            type(objection_round_limit) is not int or objection_round_limit < 1):
        raise ContractError("review round limit must be a positive integer")
    multiple_rounds = objection_round_limit is not None and objection_round_limit >= 2
    if answer_count is None:
        answer_count = initial_count if multiple_rounds else 0
    if judge_count is None:
        judge_count = 6 if multiple_rounds else 3
    counts = {"planning": 1, "initial": initial_count, "organize": organize_count,
              "answer": answer_count, "judge": judge_count}
    if any(type(count) is not int or count < 0 for count in counts.values()):
        raise ContractError("review allocation requires nonnegative integer counts")
    if initial_count < 3 or organize_count < 1 or judge_count < 3:
        raise ContractError("review allocation omits a mandatory stage")
    if multiple_rounds and (answer_count < initial_count or judge_count < 6):
        raise ContractError("review allocation omits the mandatory response round")
    if objection_round_limit == 1 and (answer_count != 0 or judge_count != 3):
        raise ContractError("single-round policy has no answer or second judging round")
    return counts


def review_execution_ids(activity_id, activities, executions):
    """Resolve the review's activity subtree from one complete snapshot."""
    if activity_id not in activities:
        raise ContractError("missing review activity")
    children = {}
    for key, activity in activities.items():
        owner = activity["owner_ref"]
        if owner["kind"] == "activity":
            children.setdefault(owner["id"], []).append(key)
    members, pending = set(), [activity_id]
    while pending:
        key = pending.pop()
        if key in members:
            raise ContractError("cyclic activity ownership")
        if activities[key]["id"] != key:
            raise ContractError("activity index differs from record ID")
        members.add(key)
        pending.extend(children.get(key, []))
    allocated, ai_ids = set(), set()
    for key in members:
        for execution_id in activities[key]["assigned_execution_ids"]:
            if execution_id in allocated or execution_id not in executions:
                raise ContractError("duplicate or missing assigned execution")
            execution = executions[execution_id]
            if execution["id"] != execution_id or execution["owner_activity_id"] != key:
                raise ContractError("assigned execution differs from its actual owner")
            allocated.add(execution_id)
            if execution["actor_kind"] == "ai":
                ai_ids.add(execution_id)
            elif execution["actor_kind"] != "machine":
                raise ContractError("unknown actor kind")
    if {key for key, execution in executions.items()
            if execution["owner_activity_id"] in members} != allocated:
        raise ContractError("owned execution missing from activity assignment")
    return ai_ids


def validate_review_reserve(record, *, activity_id=None, activities=None, executions=None):
    if any(value is not None for value in (activity_id, activities, executions)):
        if any(value is None for value in (activity_id, activities, executions)):
            raise ContractError("review accounting requires complete ownership inputs")
        actual = review_execution_ids(activity_id, activities, executions)
        if (record["executions_used"] != len(actual)
                or record["execution_limit"] != activities[activity_id]["execution_limit"]):
            raise ContractError("review count or limit differs from owning activities")
    fields = ("executions_used", "reserved_organize_executions",
              "reserved_answer_executions", "reserved_final_executions")
    if sum(record[field] for field in fields) > record["execution_limit"]:
        raise ContractError("review execution allocations exceed cap")


def check_review_output(execution, output):
    """Cross-record assignment check; input/proposal resolution remains external."""
    if execution["activity_kind"] != "identity_review" or execution["stage"] == "planning":
        raise ContractError("execution does not expect a review-result")
    for expected, actual in (("id", "execution_id"), ("owner_activity_id", "owner_activity_id"),
                             ("input_manifest_ref", "input_manifest_ref"),
                             ("output_phase", "phase"), ("role_slot_id", "role_slot_id")):
        if execution[expected] != output[actual]:
            raise ContractError("review output differs from assigned " + expected)
    return True


def check_relation_constraints(relation, definition, *, from_family, to_family):
    """Check a resolved kind/endpoint tuple, not the truth of mathematical evidence."""
    if (definition["family"] != "relation" or relation["type"] != "relation" or
            definition["token"] != relation["subkind"] or definition["lifecycle"] != "active"):
        raise ContractError("relation requires its active kind definition")
    constraints = definition["constraints"]
    if from_family not in constraints["from_families"] or to_family not in constraints["to_families"]:
        raise ContractError("relation endpoints do not match kind direction")
    if constraints["requires_evidence"] and not relation["evidence_refs"]:
        raise ContractError("relation lacks required evidence")
    if constraints["requires_assessment"] and (not relation.get("formal_result_refs") or
                                               not relation.get("assessment_refs")):
        raise ContractError("mathematical relation lacks formal/assessment references")
    return True


def slot_values(results, expected_slots, allowed):
    if (not isinstance(expected_slots, (list, tuple)) or
        len(expected_slots) != len(set(expected_slots)) or not expected_slots):
        return None
    if not all(isinstance(row, dict) and "slot_id" in row and "value" in row for row in results):
        return None
    ids = [row["slot_id"] for row in results]
    if len(ids) != len(set(ids)) or set(ids) != set(expected_slots):
        return None
    values = [row["value"] for row in results]
    return values if all(v in allowed for v in values) else None


def aggregate_identity(initial, final, scope_complete, open_issues, *,
                       expected_initial_slots=None, expected_judge_slots=None):
    first = slot_values(initial, expected_initial_slots, ("match", "mismatch", "unresolved"))
    if first is None or len(first) < 3:
        return "unresolved"
    if scope_complete and not open_issues and all(x == "match" for x in first) and not final:
        return "match"
    judges = slot_values(final, expected_judge_slots, ("match", "mismatch", "unresolved"))
    if not scope_complete or judges is None or len(judges) != 3:
        return "unresolved"
    if all(x == "match" for x in judges):
        return "unresolved" if open_issues else "match"
    if all(x == "mismatch" for x in judges):
        return "mismatch"
    return "unresolved"


def aggregate_objection(votes, round_number, limit, *, expected_slots=None):
    if limit < 1 or round_number < 1 or round_number > limit:
        raise ContractError("invalid objection round")
    values = slot_values(votes, expected_slots, ("approved", "rejected", "unresolved"))
    if values is None or len(values) != 3:
        return "execution_incomplete"
    if all(v == "approved" for v in values):
        return "approved"
    if round_number == limit:
        return "rejected" if all(v == "rejected" for v in values) else "unresolved"
    return "answer_required"


def pack_listings(candidates, canon, budget, permission=None):
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


def overflow_disposition(*, reducible_by_window, tool_accumulation, activity_kind, restored_fits=None,
                         prior_overflows=0, proposal_overflow=False, common_overflow=False):
    """Proposal overflow is measured without restored dialogue; common text has priority."""
    if (type(reducible_by_window) is not bool or type(tool_accumulation) is not bool
            or type(prior_overflows) is not int or prior_overflows < 0
            or type(proposal_overflow) is not bool or type(common_overflow) is not bool):
        raise ContractError("overflow facts must be confirmed values")
    if reducible_by_window:
        return "reduce_history"
    if common_overflow:
        return "escalate"
    if proposal_overflow:
        if activity_kind != "identity_review":
            raise ContractError("proposal-overflow closure only applies to mathematical review")
        return "close_unresolved_next_plan"
    if tool_accumulation:
        if prior_overflows >= 1:
            return "escalate"
        if activity_kind == "research_work":
            return "checkpoint_resume"
        if activity_kind == "identity_review":
            if type(restored_fits) is not bool:
                raise ContractError("reference restoration must be measured before deciding")
            return "reference_restore" if restored_fits else "escalate"
        return "restart_with_failure_input"
    return "escalate"


def check_truncation_permission(planning_input, permission):
    """Truncated listings must be exactly those the permission names, in the permission's order."""
    lists = set(permission["lists"])
    for name, key in (("candidates", "candidate_listing"), ("canon", "canon_listing")):
        listing = planning_input[key]
        if listing["truncated"]:
            if name not in lists:
                raise ContractError("listing truncated without permission")
            if listing["order"] != permission["order"]:
                raise ContractError("truncated listing order differs from permission")
    return True


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
        if (not compaction or compaction.get("disabled") is not True
                or compaction.get("overflow_behavior") != "fail_call"):
            raise ContractError("transcript restoration requires compaction disabled and fail-call overflow")
    return True


def transition(machines, machine, before, after, facts):
    table = machines[machine]
    if not any(a == before and b == after for a, b, _ in table["edges"]):
        raise ContractError("forbidden transition")
    def needed(*keys):
        if any(facts.get(key) is not True for key in keys):
            raise ContractError("unproved transition precondition: " + ",".join(keys))
    if machine == "execution":
        if after == "starting":
            needed("startup_reservations_complete", "authority_valid", "input_valid")
        if after == "running":
            needed("startup_reservations_complete", "authority_valid", "job_assigned")
        if after == "ended" and before != "queued":
            needed("local_processes_ended", "new_effect_paths_closed")
        if before == "queued" and after == "ended":
            needed("no_process_or_reservation")
    elif machine == "task":
        if after == "active":
            needed("new_research_request_committed", "contract_start_checks_valid")
            if before == "waiting":
                needed("waiting_condition_resolved")
        if after in ("waiting", "completed", "closed"):
            needed("owned_research_executions_ended")
        if after == "completed":
            needed("all_scope_fulfilled_or_authoritatively_waived", "completion_assessment_valid")
        if after == "closed":
            needed("remaining_scope_transferred_or_withdrawn")
    elif machine == "activity":
        if after in ("waiting", "finished"):
            needed("assigned_executions_ended", "next_owner_or_terminal_result_recorded")
        if before == "waiting" and after == "ready":
            needed("waiting_condition_resolved")
        if after == "working":
            needed("assigned_request_committed", "step_preconditions_valid")
    elif machine == "external-action":
        if after == "confirmed":
            needed("success_receipt")
        elif after == "failed":
            needed("failure_and_no_effect_proved")
        elif after == "cancelled":
            needed("not_invoked_proved")
        elif before == "unknown" and after == "prepared":
            needed("no_effect_proved", "authority_valid", "idempotent_retry_valid")
    elif machine == "assessment-use":
        if after == "active":
            needed("same_target_scope_inputs", "original_basis_current", "original_assessment_revalidated")
        if after == "withdrawn":
            needed("original_assessment_error_confirmed")
    elif machine == "lifecycle":
        if after == "paused" and facts.get("resume_lifecycle") != before:
            raise ContractError("pause must preserve prior lifecycle")
        if before == "paused":
            needed("recovery_valid", "permission_valid")
            if facts.get("resume_lifecycle") != after:
                raise ContractError("wrong resume lifecycle")
        if before == "initializing" and after == "active":
            needed("references_valid", "governance_approved", "operations_capacity_valid",
                   "active_trust_valid", "recovery_valid")
    return after


def request_fingerprint(request):
    return hashlib.sha256(canonical_json(request)).hexdigest()


def check_replay(original, incoming):
    if original["request_id"] != incoming["request_id"]:
        raise ContractError("not the same request")
    if request_fingerprint(original) != request_fingerprint(incoming):
        raise ContractError("request ID reused with different canonical request")
    return "return_recorded_result"


def check_request_response(request, response):
    if any(request[key] != response[key] for key in ("request_id", "command")):
        raise ContractError("response is not bound to request")
    if response["exit_code"] == 0 and request["command"] == "record":
        payload, result = request["payload"], response["result"]
        if any(payload[key] != result[key] for key in ("mode", "family")):
            raise ContractError("record response mode/family mismatch")
        if payload["mode"] == "allocate" and payload["family"] == "knowledge":
            if payload["knowledge_type"] != result["knowledge_type"]:
                raise ContractError("knowledge allocation family mismatch")
    return True


EXPOSED = {
    "frontier": {"/type", "/subkind", "/lifecycle", "/epistemic_status"},
    "evidence": {"/type", "/subkind", "/lifecycle"},
    "relation": {"/type", "/subkind", "/lifecycle"},
    "context": {"/type", "/lifecycle"}, "memory": {"/type", "/lifecycle", "/information_status"},
    "task": {"/state", "/contract/revision", "/contract/work_class"},
    "execution": {"/state", "/actor_kind", "/budget_kind"},
    "assessment": {"/kind", "/value", "/scope_complete"},
    "assessment-use": {"/state"}, "instance": {"/goal_status"},
    "governance": {"/kind", "/lifecycle"}, "trust-environment": {"/state"},
}


def resolve_exact(reference, records, artifacts, purpose="evidence"):
    kind = reference["ref_kind"]
    if kind == "tree":
        if purpose != "structural":
            raise ContractError("tree ref forbidden for frozen inputs")
        raise ContractError("structural resolution needs the containing space/tree")
    if kind == "record":
        key = (reference["space"], reference["commit"], reference["record_id"])
        data = records.get(key)
    elif kind == "artifact":
        data = artifacts.get((reference["bundle_id"], reference["path"]))
    else:
        raise ContractError("unknown reference kind")
    if data is None or hashlib.sha256(data).hexdigest() != reference["sha256"]:
        raise ContractError("missing or corrupt exact reference")
    return data


def evaluate_condition(node, snapshot):
    """Fixed synthetic snapshot, no IO. Invalid data is never treated as false."""
    try:
        op = node["op"]
        keys = {
            "always": {"op"}, "all": {"op", "args"}, "any": {"op", "args"}, "not": {"op", "arg"},
            "record_exists": {"op", "space", "record_id", "family"},
            "record_lifecycle_is": {"op", "space", "record_id", "value"},
            "record_field_equals": {"op", "space", "record_id", "pointer", "value"},
            "relation_exists": {"op", "subkind", "from_id", "to_id"},
            "task_disposition_is": {"op", "task_id", "value"},
            "decision_value_is": {"op", "decision_id", "value"},
            "artifact_valid": {"op", "artifact_ref"},
        }
        if op not in keys or set(node) != keys[op]:
            raise ContractError("invalid AST fields")
        if op == "always":
            return "true"
        if op in ("all", "any"):
            if not node["args"]:
                raise ContractError("empty boolean operator")
            values = [evaluate_condition(x, snapshot) for x in node["args"]]
            if "evaluation_error" in values:
                return "evaluation_error"
            return "true" if (all(v == "true" for v in values) if op == "all" else any(v == "true" for v in values)) else "false"
        if op == "not":
            value = evaluate_condition(node["arg"], snapshot)
            return {"true": "false", "false": "true", "evaluation_error": "evaluation_error"}[value]
        if op == "artifact_valid":
            resolve_exact(node["artifact_ref"], snapshot.get("exact_records", {}), snapshot.get("artifacts", {}))
            return "true"
        if op == "relation_exists":
            matches = []
            for relation in snapshot.get("relations", []):
                if (relation["subkind"], relation["from_id"], relation["to_id"]) == (node["subkind"], node["from_id"], node["to_id"]):
                    if not relation["well_formed"]:
                        raise ContractError("broken relation")
                    matches.append(relation["effective"])
            return "true" if any(matches) else "false"
        if op == "task_disposition_is":
            record = snapshot.get("runtime", {}).get(node["task_id"])
            if record is None:
                return "false"
            if record["family"] != "task" or not record["integrity"]:
                raise ContractError("wrong task record")
            return "true" if record["value"]["state"] == node["value"] else "false"
        if op == "decision_value_is":
            record = snapshot.get("research", {}).get(node["decision_id"])
            if record is None:
                return "false"
            if record["family"] != "decision" or not record["integrity"]:
                raise ContractError("wrong decision record")
            value = record["value"]["value"]
            return "true" if record["effective"] and type(value) is type(node["value"]) and value == node["value"] else "false"
        if op not in ("record_exists", "record_lifecycle_is", "record_field_equals"):
            raise ContractError("unknown operator")
        record = snapshot[node["space"]].get(node["record_id"])
        if record is None:
            return "false"
        if not record["integrity"]:
            raise ContractError("record integrity failure")
        if op == "record_exists":
            if record["family"] != node["family"]:
                raise ContractError("wrong record family")
            return "true"
        if op == "record_lifecycle_is":
            value = record["value"].get("lifecycle", record["value"].get("state"))
            if value is None:
                raise ContractError("no lifecycle field")
            allowed = {
                "frontier": {"active", "superseded", "withdrawn"},
                "evidence": {"active", "superseded", "withdrawn"},
                "relation": {"active", "superseded", "withdrawn"},
                "context": {"active", "superseded", "withdrawn"},
                "memory": {"active", "superseded", "withdrawn"},
                "governance": {"active", "superseded", "withdrawn"},
                "task": {"planned", "active", "waiting", "completed", "closed"},
                "assessment-use": {"active", "suspended", "withdrawn"},
                "trust-environment": {"staging", "active", "superseded", "invalidated"},
            }.get(record["family"])
            if allowed is None or node["value"] not in allowed or value not in allowed:
                raise ContractError("invalid lifecycle value")
            return "true" if value == node["value"] else "false"
        pointer = node["pointer"]
        if pointer not in EXPOSED.get(record["family"], set()):
            raise ContractError("pointer is not an exposed machine field")
        value = record["value"]
        for key in pointer.split("/")[1:]:
            value = value[key.replace("~1", "/").replace("~0", "~")]
        if type(value) not in (str, int, bool, type(None)):
            raise ContractError("scalar required")
        return "true" if type(value) is type(node["value"]) and value == node["value"] else "false"
    except (KeyError, TypeError, ValueError):
        return "evaluation_error"


def self_check_deadline_ms(due_ms, window_ms, *, tool_in_flight=False, provider_in_flight=False,
                           first_safe_boundary_ms=None):
    """Time deadline only; responding before the next research action is separate."""
    if type(due_ms) is not int or type(window_ms) is not int or window_ms <= 0:
        raise ContractError("self-check clock and positive window must be integer milliseconds")
    if type(tool_in_flight) is not bool or type(provider_in_flight) is not bool:
        raise ContractError("tool and provider states must be confirmed booleans")
    if not (tool_in_flight or provider_in_flight):
        return due_ms + window_ms
    if first_safe_boundary_ms is None:
        return None
    if type(first_safe_boundary_ms) is not int or first_safe_boundary_ms < due_ms:
        raise ContractError("first safe boundary must be at or after the due event")
    return first_safe_boundary_ms + window_ms


def update_self_check(state, event):
    result = copy.deepcopy(state)
    if event["id"] in result["seen"] or event["kind"] == "rules_only":
        return result
    if event["kind"] != "valid_response":
        raise ContractError("not a valid response")
    result["seen"].append(event["id"])
    result["anchor_ms"] = event["received_ms"]
    result["next_due_ms"] = event["received_ms"] + result["max_interval_ms"]
    if event["value"] == "progress":
        result["no_progress"] = 0
    elif event["value"] == "no_progress":
        result["no_progress"] += 1
    result["review_due"] = result["no_progress"] >= result["no_progress_limit"] or event["value"] == "contract_mismatch"
    return result
