"""Read-only counterexamples for the v8 specification adversarial review."""
from __future__ import annotations

import copy
import hashlib
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import spec_checks as checks  # noqa: E402
import verify_spec as verify  # noqa: E402


def accepted(family: str, value: dict) -> bool:
    try:
        return verify.validate(family, value)
    except checks.ContractError:
        return False


def exact_ref_from(value: dict) -> dict:
    return copy.deepcopy(value["authority_refs"][0])


def unittest_accepts(test_name: str, replacement: dict) -> bool:
    case = verify.SpecificationTests(test_name)
    result = unittest.TestResult()
    with patch.object(verify.checks, "parse_json", return_value=replacement):
        case.run(result)
    return result.wasSuccessful()


def main() -> None:
    machines = checks.parse_json((ROOT / "transitions.json").read_bytes())["machines"]
    results: dict[str, object] = {}

    reservation = verify.read_example("resource-reservation")
    reservation.update(reserved=10, confirmed_consumed=3, returned=2, state="settled")
    reservation["evidence_refs"] = [exact_ref_from(reservation)]
    results["settled_with_unaccounted_balance_accepted"] = accepted(
        "resource-reservation", reservation
    )

    assessment = verify.read_example("assessment")
    assessment.update(kind="goal", value="satisfied", scope_complete=False)
    results["satisfied_with_incomplete_scope_accepted"] = accepted(
        "assessment", assessment
    )

    results["identity_open_issue_all_final_match"] = checks.aggregate_identity(
        ["mismatch"], ["match", "match", "match"], True, True
    )
    results["identity_one_initial_match"] = checks.aggregate_identity(
        ["match"], [], True, False
    )

    issue_state = verify.read_example("issue-state")
    issue = verify.sample(verify.SCHEMAS["issue-state"]["properties"]["issues"]["items"])
    issue["judge_results"] = [
        {
            "slot_id": "same-slot",
            "value": "approved",
            "reason_ref": issue_state["scope_manifest_ref"],
        }
    ] * 3
    issue.update(state="approved", establishment_basis="unanimous_approval")
    issue_state["issues"] = [issue]
    results["duplicate_judge_slots_accepted"] = accepted("issue-state", issue_state)
    results["duplicate_judge_votes_aggregate"] = checks.aggregate_objection(
        [item["value"] for item in issue["judge_results"]], 1, 3
    )

    runtime = verify.read_example("runtime")
    runtime.update(lifecycle="paused", resume_lifecycle="active")
    results["paused_wrong_resume_schema_accepted"] = accepted("runtime", runtime)
    results["initializing_to_paused_without_resume_fact"] = checks.transition(
        machines, "lifecycle", "initializing", "paused", {}
    )
    results["initializing_to_active_without_activation_facts"] = checks.transition(
        machines, "lifecycle", "initializing", "active", {}
    )
    results["task_waiting_to_active_without_wake"] = checks.transition(
        machines, "task", "waiting", "active", {}
    )
    results["activity_waiting_to_ready_without_wake"] = checks.transition(
        machines, "activity", "waiting", "ready", {}
    )

    task = verify.read_example("task")
    reference = task["contract"]["execution_profile_ref"]
    task.update(state="completed", completion_ref=reference, closure_ref=reference)
    task["scope_dispositions"] = [
        {
            "scope_id": item["id"],
            "value": "fulfilled",
            "evidence_refs": [reference],
            "successor_task_ids": [],
        }
        for item in task["contract"]["scope"]
    ]
    task["remaining_scope_ids"] = []
    results["completed_with_closure_ref_accepted"] = accepted("task", task)
    task["state"] = "closed"
    results["closed_with_completion_ref_accepted"] = accepted("task", task)

    manifest = verify.read_example("input-manifest")
    planning = verify.sample(
        verify.SCHEMAS["input-manifest"]["properties"]["planning_input"]
    )
    planning["canon_exposure"] = "full"
    planning.pop("partial_reason", None)
    manifest["planning_input"] = planning
    results["full_without_partial_reason_accepted"] = accepted("input-manifest", manifest)
    planning["partial_reason"] = "fabricated-for-full"
    results["full_with_irrelevant_partial_reason_accepted"] = accepted(
        "input-manifest", manifest
    )

    preparation = verify.read_example("activity-result")
    results["empty_preparation_without_regenerate_after_accepted"] = accepted(
        "activity-result", preparation
    )
    results["empty_preparation_has_regenerate_after"] = (
        "regenerate_after" in preparation["payload"]
    )

    review_plan = verify.read_example("review-plan")
    results["impossible_review_plan_fixture_accepted"] = accepted(
        "review-plan", review_plan
    )
    results["review_plan_allocation"] = {
        "execution_limit": review_plan["execution_limit"],
        "local_minimum": 1
        + review_plan["initial_execution_count"]
        + review_plan["reserved_answer_executions"]
        + review_plan["reserved_final_executions"],
        "role_slot_ids": [item["id"] for item in review_plan["role_slots"]],
        "perspectives": [item["perspective"] for item in review_plan["role_slots"]],
    }

    init_response = checks.parse_json(
        (ROOT / "fixtures" / "commands" / "init.response.json").read_bytes()
    )
    results["wrong_prefix_init_response_accepted"] = accepted(
        "command-response", init_response
    )
    results["wrong_prefix_instance_id"] = init_response["result"]["instance_id"]

    record_response = verify.read_example("command-response")
    record_response.update(
        command="record",
        exit_code=0,
        result={"id": "F-" + "0" * 25 + "1"},
    )
    record_response.pop("error", None)
    results["record_success_id_only_accepted"] = accepted(
        "command-response", record_response
    )

    run_request = checks.parse_json(
        (ROOT / "fixtures" / "commands" / "run.request.json").read_bytes()
    )
    resume_request = copy.deepcopy(run_request)
    resume_request["command"] = "resume"
    results["same_id_same_payload_different_command"] = {
        "run_valid": accepted("command-request", run_request),
        "resume_valid": accepted("command-request", resume_request),
        "same_request_id": run_request["request_id"] == resume_request["request_id"],
        "same_canonical_payload": checks.canonical_json(run_request["payload"])
        == checks.canonical_json(resume_request["payload"]),
        "same_canonical_request": checks.canonical_json(run_request)
        == checks.canonical_json(resume_request),
        "run_request_sha256": hashlib.sha256(checks.canonical_json(run_request)).hexdigest(),
        "resume_request_sha256": hashlib.sha256(
            checks.canonical_json(resume_request)
        ).hexdigest(),
    }

    source_map = checks.parse_json((ROOT / "source-vector-map.json").read_bytes())
    source_map["vectors"][0].update(input="CORRUPTED", expected="CORRUPTED", source_line=1)
    source_map["quality_contracts"][0].update(
        guarantee="CORRUPTED", owner="CORRUPTED", source_vectors=[]
    )
    results["corrupted_source_map_unittest_accepts"] = unittest_accepts(
        "test_source_vectors_and_quality_bijection", source_map
    )

    registry = checks.parse_json((ROOT / "schema-registry.json").read_bytes())
    registry["families"][0].update(
        contract_id="CORRUPTED",
        owner_section="CORRUPTED",
        storage="CORRUPTED",
        id_prefix="CORRUPTED",
    )
    results["corrupted_registry_metadata_unittest_accepts"] = unittest_accepts(
        "test_registry_exact_bijection_and_hash", registry
    )

    print(json.dumps(results, ensure_ascii=False, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
