# -*- coding: utf-8 -*-
"""적대 검토 AR-06, AR-07, AR-12, AR-13, AR-15, AR-19, AR-20과 8.3절 개정을 v9 묶음에 반영한다."""
import sys
from pathlib import Path

V9 = Path(r"C:/math/docs/do-math/통합-설계-명세-v9")
PATCHES = {"build_spec.py": [], "verify_spec.py": [], "spec_checks.py": []}


def add(name, old, new, count=1):
    PATCHES[name].append((old, new, count))


B, V, S = "build_spec.py", "verify_spec.py", "spec_checks.py"

# AR-20: 어댑터의 초과 시 동작
add(B, '''                 "compaction": obj({"disabled": BOOL, "evidence_ref": ARTIFACT})})''',
    '''                 "compaction": obj({"disabled": BOOL, "evidence_ref": ARTIFACT,
                                    "overflow_behavior": {"const": "fail_call"},
                                    "overflow_evidence_ref": ARTIFACT})})''')
# AR-12: 참조 항목의 인자
add(B, '''                        "reference": obj({"call": S, "size_bytes": N})}, "reference")''',
    '''                        "reference": obj({"call": S, "arguments_ref": ARTIFACT, "size_bytes": N})}, "reference")''')
# AR-15: runtime 보류 기록의 종류
add(B, '''    "threshold_holds": array(obj({"kind": enum("import_rework", "selection_failure",
                                               "exhaustion_empty", "proposal_version"),''',
    '''    "threshold_holds": array(obj({"kind": enum("import_rework", "selection_failure",
                                               "exhaustion_empty", "proposal_version",
                                               "context_overflow", "output_truncation"),''')
# AR-06: 잘림 허가의 닫힌 필드
add(B, '''    "permission": obj({"subjects": IDS, "actions": STRINGS, "scope": S, "excluded_scope": S,
                      "resource_limits": array(obj({"constraint_id": S, "maximum": common("limit")})),
                      "valid_from": TIME, "expires_at": TIME, "stop_conditions": STRINGS,
                      "external_effects": STRINGS, "replay_allowed": BOOL,
                      "reuse": common("reuse_permission"), "user_decision_ref": EXACT}),''',
    '''    "permission": optional({"subjects": IDS, "actions": STRINGS, "scope": S, "excluded_scope": S,
                      "resource_limits": array(obj({"constraint_id": S, "maximum": common("limit")})),
                      "valid_from": TIME, "expires_at": TIME, "stop_conditions": STRINGS,
                      "external_effects": STRINGS, "replay_allowed": BOOL,
                      "reuse": common("reuse_permission"), "user_decision_ref": EXACT,
                      "truncation": common("truncation_permission")}, "truncation"),''')
add(B, '''common_defs["limit"] = {"oneOf": [obj({"kind": {"const": "bounded"}, "value": N}),
                                  obj({"kind": {"const": "unlimited"}})]}''',
    '''common_defs["limit"] = {"oneOf": [obj({"kind": {"const": "bounded"}, "value": N}),
                                  obj({"kind": {"const": "unlimited"}})]}
common_defs["truncation_permission"] = obj({
    "lists": array(enum("candidates", "canon"), 1, True), "order": enum("id", "sealed_random"),
    "activity_kinds": array(enum("research_preparation", "research_plan"), 1, True)})''')
# AR-07: 계획의 사용자 결정 요청과 identity_review 활동 결과
add(B, '''    "preparation_requests": REFS, "completion_assessments": REFS,''',
    '''    "preparation_requests": REFS, "completion_assessments": REFS,
    "user_decision_requests": array(obj({"question_ref": ARTIFACT, "basis_refs": NONEMPTY_REFS})),''')
add(B, '''    "research_plan": obj({"plan_ref": ARTIFACT, "bound_contracts": array(obj({''',
    '''    "identity_review": obj({"outcome": {"const": "input_overflow"}, "proposal_ref": ARTIFACT,
        "measurement_ref": ARTIFACT}),
    "research_plan": obj({"plan_ref": ARTIFACT, "bound_contracts": array(obj({''')
add(B, '''            "planning": "Allocate expertise, slots and execution counts for a proposal that fits in full; return restructuring when it does not; no identity approval.",''',
    '''            "planning": "Allocate expertise, slots and execution counts for a proposal that fits in full; when it does not fit the engine closes the activity unresolved with the measurement and the next research plan owns restructuring or profile requests; no identity approval.",''')
# AR-13: provided_order의 닫힌 이름
add(B, '''    "read_scope": array(common("query_scope")), "provided_order": STRINGS,''',
    '''    "read_scope": array(common("query_scope")),
    "provided_order": array(enum("common_documents", "role_documents", "governance", "transcript",
                                 "canon_listing", "candidate_listing", "ongoing", "required_failures",
                                 "recent_history", "preparation_history", "required_inputs", "question"), unique=True),''')
# 규칙 문면과 벡터 (AR-19 포함)
add(B, '''    ("R16", "8.3", "Same review slot receives its own messages in full and, uniformly, every tool-result body and prior proposal version as exact reference entries inside its read scope; overflow is classified into information-preserving reduction, self-repair or user escalation; a records-based replacement requires a user decision or general permission and records its cause.", ["V144", "V145", "V146", "V166", "V201", "V202", "V208", "V209"], "input"),''',
    '''    ("R16", "8.3", "Same review slot receives its own messages in full and, uniformly, every tool-result body and prior proposal version as exact reference entries inside its read scope; overflow is classified into information-preserving reduction, self-repair, proposal-overflow closure or user escalation; non-restoring AI activities restart once with the failure measurement as input; a second accumulation overflow or a residual overflow after reference restoration escalates; a user hold closes the activity with its current result; a records-based replacement requires a user decision or general permission and records its cause.", ["V144", "V145", "V146", "V166", "V201", "V202", "V208", "V209", "V210", "V211", "V212", "V214"], "input"),''')
add(B, '''    ("R17", "8.5", "Both listings are supplied in full when they fit; history windows shrink first; if the listings still overflow the engine escalates to the user without truncating; truncation happens only under a recorded permission naming the list and order, with snapshot population/counts and retrievable omissions.", ["V118", "V119", "V127", "V141", "V160", "V178", "V206", "V207"], "listing"),''',
    '''    ("R17", "8.5", "Both listings are supplied in full when they fit; history windows shrink first; if the listings still overflow the engine escalates to the user without truncating; truncation happens only under a recorded permission whose closed truncation fields name the lists, order and activity kinds, with snapshot population/counts and retrievable omissions.", ["V18", "V118", "V119", "V127", "V141", "V160", "V178", "V206", "V207", "V213"], "listing"),''')

# ---------------- spec_checks.py ----------------
add(S, '''def overflow_disposition(*, reducible_by_window, tool_accumulation, activity_kind, restored_fits=None):
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
    return "escalate"''',
    '''def overflow_disposition(*, reducible_by_window, tool_accumulation, activity_kind, restored_fits=None,
                         prior_overflows=0, proposal_overflow=False):
    """8.3 overflow classification: reduction, self-repair, proposal-overflow closure, or user escalation."""
    if (type(reducible_by_window) is not bool or type(tool_accumulation) is not bool
            or type(prior_overflows) is not int or type(proposal_overflow) is not bool):
        raise ContractError("overflow facts must be confirmed values")
    if reducible_by_window:
        return "reduce_history"
    if proposal_overflow:
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
    return True''')
add(S, '''def check_restoration_profile(profile, activity_kind):
    if activity_kind == "identity_review":
        compaction = profile.get("ai", {}).get("compaction")
        if not compaction or compaction.get("disabled") is not True:
            raise ContractError("transcript restoration requires an adapter with compaction disabled")
    return True''',
    '''def check_restoration_profile(profile, activity_kind):
    if activity_kind == "identity_review":
        compaction = profile.get("ai", {}).get("compaction")
        if (not compaction or compaction.get("disabled") is not True
                or compaction.get("overflow_behavior") != "fail_call"):
            raise ContractError("transcript restoration requires compaction disabled and fail-call overflow")
    return True''')

# ---------------- verify_spec.py ----------------
add(V, '''        for entry in value.get("transcript", []):
            if entry["restore_form"] == "reference" and entry["content_ref"] not in value["reference_read_refs"]:
                raise checks.ContractError("reference-form transcript entry outside read scope")''',
    '''        for entry in value.get("transcript", []):
            if entry["restore_form"] == "reference" and entry["content_ref"] not in value["reference_read_refs"]:
                raise checks.ContractError("reference-form transcript entry outside read scope")
        order = value["provided_order"]
        stable = [c for c in order if c in ("common_documents", "role_documents", "governance", "transcript", "canon_listing")]
        volatile = [c for c in order if c in ("candidate_listing", "recent_history", "preparation_history", "question")]
        if stable and volatile and max(order.index(c) for c in stable) > min(order.index(c) for c in volatile):
            raise checks.ContractError("stable components must precede per-round components")''')
add(V, '''        with self.assertRaises(checks.ContractError):
            checks.overflow_disposition(reducible_by_window=False, tool_accumulation=True, activity_kind="identity_review")''',
    '''        with self.assertRaises(checks.ContractError):
            checks.overflow_disposition(reducible_by_window=False, tool_accumulation=True, activity_kind="identity_review")
        self.assertEqual(checks.overflow_disposition(reducible_by_window=False, tool_accumulation=True,
                                                     activity_kind="research_plan"), "restart_with_failure_input")
        self.assertEqual(checks.overflow_disposition(reducible_by_window=False, tool_accumulation=True,
                                                     activity_kind="research_plan", prior_overflows=1), "escalate")
        self.assertEqual(checks.overflow_disposition(reducible_by_window=False, tool_accumulation=True,
                                                     activity_kind="identity_review", restored_fits=True, prior_overflows=1), "escalate")
        self.assertEqual(checks.overflow_disposition(reducible_by_window=False, tool_accumulation=False,
                                                     activity_kind="identity_review", proposal_overflow=True), "close_unresolved_next_plan")''')
add(V, '''        self.assertTrue(checks.check_restoration_profile(read_example("execution-profile"), "research_work"))''',
    '''        self.assertTrue(checks.check_restoration_profile(read_example("execution-profile"), "research_work"))

    def test_truncation_permission_alignment(self):
        manifest = read_example("input-manifest")
        planning = manifest["planning_input"]
        permission = {"lists": ["candidates"], "order": "sealed_random", "activity_kinds": ["research_plan"]}
        self.assertTrue(checks.check_truncation_permission(planning, permission))
        planning["candidate_listing"].update(total_count=5, truncated=True)
        self.assertTrue(checks.check_truncation_permission(planning, permission))
        with self.assertRaises(checks.ContractError):
            checks.check_truncation_permission(planning, {"lists": ["canon"], "order": "sealed_random"})
        with self.assertRaises(checks.ContractError):
            checks.check_truncation_permission(planning, {"lists": ["candidates"], "order": "id"})
        governance = read_example("governance")
        governance.update(kind="permission", payload=sample(SCHEMAS["governance"]["allOf"][3]["then"]["properties"]["payload"]))
        governance["payload"]["truncation"] = permission
        validate("governance", governance)
        governance["payload"]["truncation"] = {"lists": ["history"], "order": "id", "activity_kinds": ["research_plan"]}
        with self.assertRaises(checks.ContractError):
            validate("governance", governance)

    def test_provided_order_stable_components_first(self):
        manifest = read_example("input-manifest")
        manifest["provided_order"] = ["common_documents", "role_documents", "governance", "canon_listing",
                                      "candidate_listing", "recent_history", "question"]
        validate("input-manifest", manifest)
        manifest["provided_order"] = ["candidate_listing", "canon_listing"]
        with self.assertRaises(checks.ContractError):
            validate("input-manifest", manifest)
        manifest["provided_order"] = ["listing"]
        with self.assertRaises(checks.ContractError):
            validate("input-manifest", manifest)''')
add(V, '''        self.assertEqual(set(ids), {"V" + str(i).zfill(2) for i in range(1, 210)})
        self.assertEqual(len(ids), 209)''',
    '''        self.assertEqual(set(ids), {"V" + str(i).zfill(2) for i in range(1, 215)})
        self.assertEqual(len(ids), 214)''')
add(V, '''        self.assertEqual({q["id"] for q in mapping["quality_contracts"]}, {"Q" + str(i).zfill(2) for i in range(1, 22)})''',
    '''        self.assertEqual({q["id"] for q in mapping["quality_contracts"]}, {"Q" + str(i).zfill(2) for i in range(1, 23)})''')


def main():
    texts, failures = {}, []
    for name, pairs in PATCHES.items():
        text = (V9 / name).read_text(encoding="utf-8")
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


if __name__ == "__main__":
    main()
