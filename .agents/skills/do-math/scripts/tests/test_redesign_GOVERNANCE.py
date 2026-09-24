"""Feature-version-5 governance contracts.

These tests specify facts and authority boundaries, not provider capabilities.
"""
from __future__ import annotations

from pathlib import Path
import os
import json
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from do_math.external import execute_operation, prepare_operation
from do_math.governance import apply_decision, authorize, interpretation_schema
from do_math.academic import academic_status, solution_basis
from do_math import governance as gov, questions
from copy import deepcopy


def charter(identifier="CH1", goal="Prove P"):
    return {"id": identifier, "kind": "charter", "revision": 1, "supersedes": [],
            "content": {"rationale": "Research P", "goal": goal, "desired_result": "A proof",
                        "success_criteria": ["P proved"], "partial_success_criteria": ["Cases settled"],
                        "included_scope": ["P"], "excluded_scope": [], "priorities": ["P"],
                        "preferences": [], "evidence_boundary": "Proof, not preference",
                        "academic_requirements": [], "decision_authority": "user", "stop_conditions": []}}


class DomainGovernanceTests(unittest.TestCase):
    def initial(self):
        source = gov.preserve_source("S", "User approves P", origin="user", revision=1)
        records = [charter()]
        approval = {"id": "D", "actor": "user", "source_ref": "S", "source_sha256": source["sha256"],
                    "record_hashes": {r["id"]: gov.digest(r) for r in records}}
        return gov.initialize_governance({"id": "I", "feature_version": 5}, source, approval, records)

    def test_initialized_charter_is_single_authority_and_binds_approved_original(self):
        i = self.initial()
        self.assertNotIn("goal", i)
        self.assertNotIn("policies", i)
        self.assertEqual(gov.governance_view(i)["goal"], "Prove P")
        self.assertEqual(i["governance"]["CH1"]["approval_ref"], "D")
        changed = deepcopy(i["governance_sources"]["S"]); changed["text"] += "!"
        with self.assertRaises(ValueError):
            gov.initialize_governance({"id": "I", "feature_version": 5}, changed, i["decisions"]["D"], [charter()])

    def test_policy_coexists_and_only_explicit_supersession_retires_old_rule(self):
        i = self.initial(); runtime = {"tasks": {}, "executions": {}, "queue": [], "status": "ready"}
        for identifier, replaces in (("P1", []), ("P2", []), ("P3", ["P1"])):
            record = {"id": identifier, "kind": "policy", "revision": 1, "supersedes": replaces,
                      "content": {"rule_id": identifier, "scope": ["P"], "text": identifier,
                                  "reason_refs": ["D"], "audit_refs": []}}
            change = {"kind": "policy", "record": record, "decision_id": "D" + identifier}
            i, runtime, _ = gov.apply_decision(i, runtime, change, source_ref="S")
        self.assertEqual({r["id"] for r in gov.governance_view(i)["policy_records"]}, {"P2", "P3"})
        self.assertEqual(i["governance"]["P1"]["status"], "superseded")
        with self.assertRaises(ValueError):
            gov.apply_decision(i, runtime, {"kind": "policy", "text": "replace all"}, source_ref="S")

    def test_context_and_audit_require_owned_meaning_and_exact_verdict_mapping(self):
        i = self.initial(); rt = {"tasks": {}, "executions": {}, "queue": [], "status": "ready"}
        context = {"id": "CX", "kind": "research_context", "revision": 1, "supersedes": [],
                   "content": {"terms": [{"term": "P", "definition": "the target", "boundary": "this problem",
                                          "avoid_synonyms": [], "record_refs": []}]}}
        i, rt, _ = gov.apply_decision(i, rt, {"kind": "research_context", "record": context}, source_ref="S")
        audit = {"id": "AU", "kind": "additional_audit", "revision": 1, "supersedes": [],
                 "content": {"scope": ["P"], "required_inputs": ["CH1"], "assessor": "goal_audit",
                             "verdict_mapping": {"pass": "satisfied", "fail": "not_satisfied", "unknown": "unresolved"}}}
        i, rt, _ = gov.apply_decision(i, rt, {"kind": "additional_audit", "record": audit}, source_ref="S")
        self.assertEqual(gov.governance_view(i)["additional_audits"][0]["id"], "AU")
        audit["id"] = "AU2"; audit["content"]["verdict_mapping"]["pass"] = "research_goal_satisfied"
        with self.assertRaises(ValueError):
            gov.apply_decision(i, rt, {"kind": "additional_audit", "record": audit}, source_ref="S")

    def import_fixture(self):
        i = self.initial(); rt = {"tasks": {}, "executions": {}, "queue": [], "status": "ready"}
        s = gov.preserve_source("IN", "A choice", origin="user", revision=1)
        unit = {"unit_id": "U", "source_range": {"start": 0, "end": 8}, "interpretation": "Ask a choice",
                "owner_kind": "charter", "owner_ref": "CH1", "payload": {}, "decision_refs": ["D"], "question_refs": ["Q"]}
        output = {"import_units": [unit], "questions": ["Which scope?"], "needs_clarification": True,
                  "question_details": [{"id": "Q", "question_index": 0, "target_ids": ["I"], "blocks": False,
                                        "reason": "Optional direction", "options": [{"text": "Keep", "effect": "No change"}],
                                        "source_unit_ids": ["U"]}]}
        return i, rt, s, output

    def test_import_holes_and_self_check_are_rejected_and_questions_still_checked(self):
        i, rt, s, output = self.import_fixture()
        bad = deepcopy(output); bad["import_units"][0]["source_range"]["end"] = 7
        with self.assertRaises(ValueError): gov.prepare_import(i, rt, s, bad, execution_id="E1")
        bundle = gov.prepare_import(i, rt, s, output, execution_id="E1")
        rt["executions"]["E2"] = {"role":"intent_interpretation", "intent_import_sha256":bundle["sha256"]}
        check = {"bundle_sha256": bundle["sha256"], "decision": "approved", "scope_complete": True,
                 "unit_ids": ["U"], "question_ids": ["Q"], "findings": []}
        with self.assertRaises(ValueError): gov.check_import(i, rt, bundle["id"], check, execution_id="E1")
        gov.check_import(i, rt, bundle["id"], check, execution_id="E2")
        updated, updated_rt, outcome = gov.apply_import(i, rt, bundle["id"])
        self.assertEqual(outcome["status"], "applied")
        self.assertFalse(questions.user_waits({"role": "research_preparation"}, updated, updated_rt))

    def test_import_reauthor_requires_current_failed_parent_and_repair_coordinates(self):
        i, rt, s, out = self.import_fixture()
        b = gov.prepare_import(i, rt, s, out, execution_id="E1")
        rt["executions"]["E2"] = {"role":"intent_interpretation", "intent_import_sha256":b["sha256"]}
        gov.check_import(i, rt, b["id"], {"bundle_sha256": b["sha256"], "decision": "revision_required",
            "scope_complete": True, "unit_ids": ["U"], "question_ids": ["Q"], "findings": ["Question incomplete"]}, execution_id="E2")
        with self.assertRaises(ValueError): gov.prepare_import(i, rt, s, out, execution_id="E3", previous_id=b["id"])
        out["repair"] = {"previous_sha256": b["sha256"], "changed_unit_ids": ["U"], "actions": ["Add scope option"]}
        out["question_details"][0]["options"].append({"text":"Change scope", "effect":"Ask for a replacement charter"})
        newer = gov.prepare_import(i, rt, s, out, execution_id="E3", previous_id=b["id"])
        self.assertEqual(newer["previous_id"], b["id"])
        with self.assertRaises(ValueError): gov.apply_import(i, rt, b["id"])

    def test_import_currentness_binds_actual_structured_task_contract(self):
        i, rt, source, output = self.import_fixture()
        rt['tasks']['T'] = {'id': 'T', 'revision': 1, 'status': 'planned', 'question': 'Original task'}
        output['used_sources'] = ['T']
        bundle = gov.prepare_import(i, rt, source, output, execution_id='AUTHOR')
        rt['executions']['CHECK'] = {'role': 'intent_interpretation', 'intent_import_sha256': bundle['sha256']}
        rt['tasks']['T']['question'] = 'A different task under the same nominal revision'
        with self.assertRaises(ValueError):
            gov.check_import(i, rt, bundle['id'], {'bundle_sha256': bundle['sha256'], 'decision': 'approved',
                'scope_complete': True, 'unit_ids': ['U'], 'question_ids': ['Q'], 'findings': []}, execution_id='CHECK')

    def test_question_advice_does_not_block_and_partial_target_answer_does_not_erase_wait(self):
        rt = {}; row = questions.link(rt, execution_id="E", field="questions/0", owner="user", targets=["I"], blocks=False)
        self.assertEqual(questions.user_waits({"role": "research_preparation"}, {"id": "I"}, rt), [])
        blocking = questions.link(rt, execution_id="E", field="questions/1", owner="user", targets=["A", "B"], blocks=True)
        questions.resolve_user(rt, [blocking["id"]], resolution_ref="D", affected_ids=["A"])
        self.assertEqual(blocking["status"], "open")
        self.assertEqual(blocking["unresolved_target_ids"], ["B"])

    def test_unapproved_or_stale_import_cannot_change_charter(self):
        i, rt, s, output = self.import_fixture()
        replacement = charter("CH2", "Prove Q"); replacement["supersedes"] = ["CH1"]
        output.update(questions=[], question_details=[], needs_clarification=False)
        unit = output["import_units"][0]; unit.update(owner_ref="CH2", question_refs=[], payload={"kind": "charter", "record": replacement})
        b = gov.prepare_import(i, rt, s, output, execution_id="E1")
        rt["executions"]["E2"] = {"role":"intent_interpretation", "intent_import_sha256":b["sha256"]}
        gov.check_import(i, rt, b["id"], {"bundle_sha256": b["sha256"], "decision": "approved", "scope_complete": True,
                                      "unit_ids": ["U"], "question_ids": [], "findings": []}, execution_id="E2")
        with self.assertRaises(ValueError): gov.apply_import(i, rt, b["id"])
        approvals = {"U": {"actor": "user", "source_ref": "IN", "source_sha256": s["sha256"], "change_sha256": gov.digest(unit["payload"])}}
        changed, state, event = gov.apply_import(i, rt, b["id"], approvals=approvals)
        self.assertEqual(gov.governance_view(changed)["goal"], "Prove Q")
        self.assertEqual(event["status"], "applied")
        _, repeated_state, repeated_event = gov.apply_import(changed, state, b["id"], approvals=approvals)
        self.assertEqual(repeated_event, event)
        self.assertEqual(repeated_state, state)
        stale = deepcopy(i); stale["decisions"]["D"]["revoked"] = True
        with self.assertRaises(ValueError): gov.apply_import(stale, rt, b["id"], approvals=approvals)

    def test_explicit_once_grant_and_exclusions_use_existing_execution_ledger(self):
        i = {"feature_version": 5, "grants": {"G": {"id": "G", "kind": "local", "status": "active",
             "roles": ["research_work"], "task_ids": [], "excluded_targets": ["B"], "reuse": "once",
             "source_ref": "S", "subjects": ["research_work"], "resource_limits": {}}}}
        rt = {"executions": {"E": {"id": "E", "grant_id": "G", "action": {"id": "A1"}}}}
        self.assertFalse(gov.authorize(i, {"id": "A2", "role": "research_work", "target": "A"}, runtime=rt)["allowed"])
        self.assertFalse(gov.authorize(i, {"id": "A1", "role": "research_work", "target": "B"}, runtime={})["allowed"])

    def test_delegation_requires_two_real_judgments_on_same_current_case(self):
        from do_math import delegations as d
        i = self.initial()
        i["decisions"]["ORIGINAL"] = {"id": "ORIGINAL", "actor": "user", "source_ref": "S", "kind": "review_replacement", "status": "active"}
        i["delegations"] = {"DG": {"id": "DG", "status": "active", "decision_kind": "review_replacement",
              "original_decision_id": "ORIGINAL", "included_targets": ["T"], "excluded_targets": [],
              "external_effects": [], "resource_limits": {}, "expires_at": None, "source_ref": "S", "decision_id": "D"}}
        i["delegations"]["DG"]["decision_id"] = "DD"
        i["decisions"]["DD"] = {"id":"DD", "kind":"delegation", "actor":"user", "source_ref":"S",
            "change":{"delegation":{k:deepcopy(v) for k,v in i["delegations"]["DG"].items() if k not in {"source_ref","decision_id","created_at"}}}}
        rt = {"executions": {}, "tasks": {"T": {"id": "T", "status": "waiting"}}}
        case = {"id": "CASE", "target_id": "T", "decision_kind": "review_replacement", "external_effects": [], "resources": {}, "effect": {"replace_slot": "R"}}
        app = d.prepare_application(i, rt, "DG", case)
        for eid, stage in (("E1", "interpret"), ("E2", "check")):
            rt["executions"][eid] = {"id": eid, "role": "intent_interpretation", "input_sha256": app["input_sha256"], "status": "ended"}
            d.record_judgment(rt, app["id"], {"decision": "within_scope", "reason": "same approved recovery", "input_sha256": app["input_sha256"]}, execution_id=eid, stage=stage)
        def effect(a,b,value):
            b["tasks"]["T"]["status"]="ready";b["replacement"]=value
            return a,b
        result, state, record = d.apply_application(i, rt, app["id"], apply_effect=effect)
        self.assertEqual(state["replacement"], {"replace_slot": "R"})
        self.assertNotIn(app["id"], result["decisions"])
        _, repeated, _ = d.apply_application(result,state,app["id"],apply_effect=lambda *_:self.fail("already applied"))
        self.assertEqual(repeated,state)
        i["delegations"]["DG"]["status"] = "revoked"
        with self.assertRaises(ValueError): d.apply_application(i, rt, app["id"], apply_effect=lambda a,b,e:(a,b))

    def test_unknown_with_sent_marker_cannot_silently_retransmit(self):
        from do_math.external import prepare_operation, execute_operation
        op = prepare_operation({"method": "POST", "url": "https://example.test/p"}, "G", "S")
        op.update(transmitted=True, transmission_phase="recorded")
        grant = {"id": "G", "status": "active", "allowed_origins": ["https://example.test"], "allowed_methods": ["POST"], "allowed_path_prefixes": ["/"]}
        calls = []
        with self.assertRaises(ValueError): execute_operation(op, grant, persist=lambda _:True, transport=lambda *_: calls.append(1) or {"http_status":200,"body":b"ok"})
        self.assertEqual(calls, [])

    def test_resolution_is_current_only_while_its_real_evidence_is_unchanged(self):
        from do_math import academic
        i = self.initial(); i["goal_status"] = "mathematically_solved"
        basis = solution_basis("CH1", [{"id": "K"}])
        rt = {"external_rejections": [{"id": "RJ", "solution_basis": basis, "text": "Missing argument"}],
              "executions": {"E": {"role": "research_plan", "input_solution_basis": basis}},
              "artifacts": {"EV": {"id": "EV", "text": "Full response"}}}
        academic.record_resolution(i, rt, basis, {"id": "RJ", "decision": "resolved", "evidence": "Response addresses objection", "evidence_refs": ["EV"]}, execution_id="E")
        self.assertEqual(academic.unresolved_rejections(i, rt, basis), [])
        rt["artifacts"]["EV"]["text"] = "changed"
        self.assertEqual(len(academic.unresolved_rejections(i, rt, basis)), 1)

    def test_initialization_cannot_rebind_another_immutable_original(self):
        source = gov.preserve_source("S", "P", origin="user")
        records = [charter()]
        approval = {"id":"D", "actor":"user", "source_ref":"S", "source_sha256":source["sha256"], "record_hashes":{"CH1":gov.digest(records[0])}}
        with self.assertRaises(ValueError):
            gov.initialize_governance({"feature_version":5, "lifecycle":{"immutable_input":{"text":"Q", "sha256":"different", "bytes":1}}}, source, approval, records)

    def test_stored_governance_content_must_still_match_approved_proposal(self):
        i = self.initial(); i["governance"]["CH1"]["content"]["goal"] = "Unapproved Q"
        with self.assertRaises(ValueError): gov.validate_governance_state(i)

    def test_import_check_must_resolve_a_real_execution_and_bound_input(self):
        i, rt, s, output = self.import_fixture()
        bundle = gov.prepare_import(i, rt, s, output, execution_id="E1")
        with self.assertRaises(ValueError):
            gov.check_import(i, rt, bundle["id"], {"bundle_sha256":bundle["sha256"], "decision":"approved", "scope_complete":True,
                            "unit_ids":["U"], "question_ids":["Q"], "findings":[]}, execution_id="FAKE")

    def test_import_reapplication_is_idempotent(self):
        i, rt, s, output = self.import_fixture()
        b = gov.prepare_import(i, rt, s, output, execution_id="E1")
        rt["executions"]["E2"] = {"role":"intent_interpretation", "intent_import_sha256":b["sha256"]}
        gov.check_import(i, rt, b["id"], {"bundle_sha256":b["sha256"], "decision":"approved", "scope_complete":True,
                         "unit_ids":["U"], "question_ids":["Q"], "findings":[]}, execution_id="E2")
        i, rt, first = gov.apply_import(i, rt, b["id"])
        _, second, result = gov.apply_import(i, rt, b["id"])
        self.assertEqual(first, result)
        self.assertEqual(len(rt["question_links"]),len(second["question_links"]))

    def test_additional_audit_consumes_exact_required_inputs_and_mapping(self):
        i = self.initial(); rt = {"tasks":{},"executions":{},"queue":[]}
        r = {"id":"AU", "kind":"additional_audit", "revision":1,"supersedes":[],
             "content":{"scope":["P"],"required_inputs":["CH1"],"assessor":"goal_audit","verdict_mapping":{"pass":"satisfied","fail":"not_satisfied","unknown":"unresolved"}}}
        i, _, _ = gov.apply_decision(i,rt,{"kind":"additional_audit","record":r},source_ref="S")
        with self.assertRaises(ValueError): gov.evaluate_additional_audit(i,"AU","pass",assessor="goal_audit",input_hashes={})
        verdict = gov.evaluate_additional_audit(i,"AU","pass",assessor="goal_audit",input_hashes={"CH1":gov.digest(i["governance"]["CH1"])})
        self.assertEqual(verdict["decision"],"satisfied")
        self.assertEqual(i["goal_status"],"unsolved")


    def test_question_mixin_publishes_advice_without_global_wait_and_resolves_atomically(self):
        from do_math.question_engine import QuestionEngineMixin
        class Host(QuestionEngineMixin): pass
        h=Host();h.instance={"id":"I","feature_version":5}
        h.runtime={"executions":{"E":{"id":"E","role":"research_plan","artifact_bundle":"B", "extensions":{"question_routes":[{"question_index":0,"owner":"user","target_ids":["I"],"blocks":False,"reason":"optional"}]}}}}
        h._record_output_questions({"role":"research_plan"},{"questions":["Optional priority?"]},"E")
        self.assertEqual(questions.user_waits({"role":"research_plan"}, h.instance, h.runtime), [])
        one=questions.link(h.runtime,execution_id="A",field="questions/0",owner="research",targets=["I"])
        h.runtime["executions"]["E"]["extensions"]={"question_resolutions":[
            {"question_id":one["id"],"disposition":"resolved","evidence_refs":["EV"],"reason":"answered"},
            {"question_id":"missing","disposition":"resolved","evidence_refs":["EV"],"reason":"bad"}]}
        h.runtime["artifacts"]={"EV":{"id":"EV","answer":"evidence"}}
        with self.assertRaises(ValueError):h._apply_question_resolutions("E")
        self.assertEqual(one["status"],"open")

    def test_question_wait_uses_activity_lifecycle_and_resumes_only_after_all_answers(self):
        from do_math.activities import open_activity
        rt={"executions":{}}
        open_activity(rt,activity_id="A",activity_kind="research",owner_ref="T",input_refs=[],opened_at="2026-09-20T00:00:00Z")
        one=questions.link(rt,execution_id="E",field="q/0",owner="user",targets=["T"],blocks=True)
        questions.sync_activity_wait(rt,"A",[one["id"]],at="2026-09-20T00:00:00Z")
        self.assertEqual(rt["activities"]["A"]["status"],"waiting")
        questions.resolve_user(rt,[one["id"]],resolution_ref="D",affected_ids=["T"])
        questions.sync_activity_wait(rt,"A",[one["id"]],at="2026-09-20T00:01:00Z")
        self.assertEqual(rt["activities"]["A"]["status"],"ready")

    def test_reconciliation_cannot_assert_success_from_unbound_text(self):
        from do_math.external import reconcile_operation
        op=prepare_operation({"method":"POST","url":"https://example.test/p"},"G","S");op["status"]="unknown"
        with self.assertRaises(ValueError): reconcile_operation(op,"a receipt","confirmed",source="user",succeeded=True)

    def test_delegation_approval_must_bind_the_actual_delegation(self):
        from do_math import delegations as d
        i=self.initial();i["decisions"]["ORIG"]={"id":"ORIG","kind":"custom_case","actor":"user","source_ref":"S"}
        i["delegations"]={"DG":{"id":"DG","status":"active","decision_kind":"custom_case","original_decision_id":"ORIG",
             "included_targets":["T"],"excluded_targets":[],"external_effects":[],"resource_limits":{},"source_ref":"S","decision_id":"D"}}
        case={"id":"C","target_id":"T","decision_kind":"custom_case","external_effects":[],"resources":{},"effect":{}}
        with self.assertRaises(ValueError):d.prepare_application(i,{"tasks":{"T":{"id":"T"}}},"DG",case)

    def test_grant_replacement_is_atomic_and_expiry_disposes_current_consumers(self):
        i=self.initial();rt={"tasks":{},"executions":{},"queue":[]}
        spec={"id":"G","kind":"local","roles":["research_work"],"reuse":"reusable","expires_at":"2099-01-01T00:00:00Z"}
        i,rt,_=gov.apply_decision(i,rt,{"kind":"grant","grant":spec},source_ref="S")
        rt["executions"]["E"]={"id":"E","status":"running","grant_id":"G"}
        replacement={**spec,"id":"G2","expires_at":"2099-01-02T00:00:00Z"}
        i,rt,event=gov.apply_decision(i,rt,{"kind":"grant","grant":replacement,"replaces":["G"]},source_ref="S")
        self.assertEqual(i["grants"]["G"]["status"],"revoked")
        self.assertEqual(i["grants"]["G"]["revoked_by"],event["id"])
        self.assertEqual(rt["executions"]["E"]["stop_requested"],"grant_revoked")
        i,rt,events=gov.expire_grants(i,rt,at="2099-01-03T00:00:00Z")
        self.assertEqual(i["grants"]["G2"]["status"],"expired")
        self.assertEqual(events[0]["grant_id"],"G2")

    def test_local_capability_pool_and_execution_kind_are_not_ignored(self):
        i={"feature_version":5,"grants":{"G":{"id":"G","kind":"local","status":"active","roles":["research_work"],
            "reuse":"reusable","budget_kind":"operations","execution_kinds":["machine"]}}}
        self.assertFalse(gov.authorize(i,{"role":"research_work","actor_kind":"ai","budget_kind":"work"},runtime={})["allowed"])

    def test_generic_academic_request_must_bind_the_solution_it_relied_on(self):
        from do_math import academic
        i=self.initial();i["goal_status"]="mathematically_solved"
        basis=solution_basis("CH1",[{"id":"K"}]);rt={}
        grant={"id":"G","academic_only":True}
        operation=prepare_operation({"method":"POST","url":"https://example.test/p"},"G","S")
        self.assertFalse(academic.external_prerequisite(i,rt,basis,operation,grant))
        operation=academic.bind_external_prerequisite(i,rt,basis,operation)
        self.assertTrue(academic.external_prerequisite(i,rt,basis,operation,grant))
        self.assertFalse(academic.external_prerequisite(i,rt,solution_basis("CH2",[{"id":"K"}]),operation,grant))

    def test_nonformal_task_does_not_establish_final_goal_assurance(self):
        from do_math.academic import apply_goal_assurance
        i=self.initial()
        with self.assertRaises(ValueError):apply_goal_assurance(i,decision="research_goal_satisfied",basis="B",judgments=[{"decision":"satisfied"}])

    def test_import_repair_cannot_claim_unchanged_units_were_changed(self):
        i,rt,s,out=self.import_fixture();b=gov.prepare_import(i,rt,s,out,execution_id="E1")
        rt["executions"]["E2"]={"role":"intent_interpretation","intent_import_sha256":b["sha256"]}
        gov.check_import(i,rt,b["id"],{"bundle_sha256":b["sha256"],"decision":"revision_required","scope_complete":True,"unit_ids":["U"],"question_ids":["Q"],"findings":["Correct interpretation"]},execution_id="E2")
        out["repair"]={"previous_sha256":b["sha256"],"changed_unit_ids":["U"],"actions":["Claim repaired"]}
        with self.assertRaises(ValueError):gov.prepare_import(i,rt,s,out,execution_id="E3",previous_id=b["id"])

    def test_academic_file_evidence_is_resolved_at_snapshot_not_from_its_name(self):
        from do_math import academic
        i=self.initial();basis=solution_basis("CH1",[{"id":"K"}])
        rt={"external_rejections":[{"id":"RJ","solution_basis":basis}],"executions":{"E":{"role":"research_plan","input_solution_basis":basis}}}
        value={"id":"RJ","decision":"resolved","evidence":"response","evidence_refs":["runtime/artifacts/E/response.md"]}
        with self.assertRaises(ValueError):academic.record_resolution(i,rt,basis,value,execution_id="E")
        academic.record_resolution(i,rt,basis,value,execution_id="E",resolve_evidence=lambda _:b"actual text")
        self.assertEqual(academic.unresolved_rejections(i,rt,basis,resolve_evidence=lambda _:b"actual text"),[])
        self.assertTrue(academic.unresolved_rejections(i,rt,basis,resolve_evidence=lambda _:b"changed"))

    def test_actual_answer_preserves_other_affected_targets(self):
        i=self.initial();rt={"tasks":{"A":{"id":"A"},"B":{"id":"B"}},"executions":{},"queue":[]}
        q=questions.link(rt,execution_id="E",field="q/0",owner="user",targets=["A","B"],blocks=True)
        _,updated,_=gov.apply_decision(i,rt,{"kind":"question_answer","text":"Answer A", "target_ids":["A"],"resolves_questions":[q["id"]]},source_ref="S")
        self.assertEqual(updated["question_links"][0]["unresolved_target_ids"],["B"])

    def test_academic_basis_rejects_a_stale_judgment_dependency(self):
        from do_math.academic_engine import AcademicEngineMixin
        from do_math.knowledge import capture_basis
        class Host(AcademicEngineMixin):pass
        h=Host();h.instance={"goal_status":"mathematically_solved","goal_revision":1,"knowledge":{"K":{"id":"K","text":"new"}},"goal_assessment_basis":"B"};h.runtime={}
        h.instance["goal_judgments"]=[{"execution_id":"E","basis":"B","current":True,"dependencies":["K"],"record_basis":capture_basis({"knowledge":{"K":{"id":"K","text":"old"}}},{},["K"])}]
        self.assertIsNone(h._solution_basis())

    def test_initial_original_and_later_explicit_approval_remain_distinct(self):
        source=gov.preserve_source("ORIG","Research P",origin="user")
        approval_source=gov.preserve_source("APPROVAL","Approve this exact charter",origin="user")
        record=charter();approval={"id":"D","actor":"user","source_ref":"APPROVAL","source_sha256":approval_source["sha256"],
            "input_source_ref":"ORIG","input_source_sha256":source["sha256"],"record_hashes":{"CH1":gov.digest(record)}}
        i=gov.initialize_governance({"id":"I","feature_version":5,"lifecycle":{"immutable_input":{k:source[k] for k in ("text","sha256","bytes")}}},source,approval,[record],approval_source=approval_source)
        self.assertEqual(i["governance"]["CH1"]["source_ref"],"ORIG")
        self.assertEqual(i["decisions"]["D"]["source_ref"],"APPROVAL")
        gov.validate_governance_state(i)

    def test_resumed_author_session_is_not_an_independent_import_check(self):
        i,rt,s,out=self.import_fixture();b=gov.prepare_import(i,rt,s,out,execution_id="E1")
        rt["executions"]["E2"]={"role":"intent_interpretation","intent_import_sha256":b["sha256"],"continuation_of":"E1"}
        with self.assertRaises(ValueError):gov.check_import(i,rt,b["id"],{"bundle_sha256":b["sha256"],"decision":"approved","scope_complete":True,
                              "unit_ids":["U"],"question_ids":["Q"],"findings":[]},execution_id="E2")

    def test_intent_schema_covers_the_actual_check_and_repair_contract(self):
        import jsonschema
        i,rt,s,out=self.import_fixture()
        out.update(summary="question",used_sources=["S"])
        jsonschema.validate(out,gov.interpretation_schema("interpret"))
        check={"summary":"checked","used_sources":["S"],"questions":[],"bundle_sha256":"a"*64,"decision":"approved",
               "scope_complete":True,"unit_ids":["U"],"question_ids":["Q"],"findings":[]}
        jsonschema.validate(check,gov.interpretation_schema("check"))
        with self.assertRaises(jsonschema.ValidationError):jsonschema.validate({**check,"decision":"match"},gov.interpretation_schema("check"))

    def test_question_coordinates_must_reciprocate_unit_question_references(self):
        i,rt,s,out=self.import_fixture()
        other=deepcopy(out["import_units"][0]);other.update(unit_id="V",source_range={"start":4,"end":8},question_refs=[])
        out["import_units"][0]["source_range"]["end"]=4;out["import_units"].append(other)
        out["question_details"][0]["source_unit_ids"]=["V"]
        with self.assertRaises(ValueError):gov.prepare_import(i,rt,s,out,execution_id="E1")

    def test_final_goal_record_cannot_rely_on_unresolved_formal_references(self):
        from do_math.academic import apply_goal_assurance
        i=self.initial()
        with self.assertRaises(ValueError):apply_goal_assurance(i,decision="mathematically_solved",basis="B",
            judgments=[{"decision":"satisfied","current":True,"formal_result_refs":["MISSING"]}])

    def test_advisory_question_does_not_leave_import_waiting_for_a_decision(self):
        i,rt,s,out=self.import_fixture();b=gov.prepare_import(i,rt,s,out,execution_id="E1")
        rt["executions"]["E2"]={"role":"intent_interpretation","intent_import_sha256":b["sha256"]}
        gov.check_import(i,rt,b["id"],{"bundle_sha256":b["sha256"],"decision":"approved","scope_complete":True,
                         "unit_ids":["U"],"question_ids":["Q"],"findings":[]},execution_id="E2")
        _,state,result=gov.apply_import(i,rt,b["id"])
        self.assertEqual(result["status"],"applied")
        self.assertEqual(state["question_links"][0]["status"],"open")
        i,rt,s,out=self.import_fixture();out["question_details"][0]["blocks"]=True
        b=gov.prepare_import(i,rt,s,out,execution_id="E1")
        rt["executions"]["E2"]={"role":"intent_interpretation","intent_import_sha256":b["sha256"]}
        gov.check_import(i,rt,b["id"],{"bundle_sha256":b["sha256"],"decision":"approved","scope_complete":True,
                         "unit_ids":["U"],"question_ids":["Q"],"findings":[]},execution_id="E2")
        _,state,result=gov.apply_import(i,rt,b["id"])
        self.assertEqual(result["status"],"awaiting_decision")
        self.assertTrue(questions.user_waits({"role":"research_preparation"},i,state))


class GovernanceRedesignTests(unittest.TestCase):
    def _grant(self, **extra):
        value = {
            "id": "G", "status": "active", "expires_at": None,
            "allowed_origins": ["https://example.test"],
            "allowed_methods": ["POST"], "allowed_path_prefixes": ["/submit"],
            "credential_env": {},
        }
        value.update(extra)
        return value

    def _operation(self):
        return prepare_operation(
            {"method": "POST", "url": "https://example.test/submit", "body": "proof"},
            "G", "source",
        )

    def test_non_2xx_is_failed_only_when_effect_absence_is_evidenced(self):
        operation = self._operation()
        result = execute_operation(
            operation, self._grant(), persist=lambda _: True,
            transport=lambda *_: {"http_status": 409, "body": b"rejected", "effect_absent": True},
        )
        self.assertEqual(result["status"], "failed")
        self.assertIs(result["succeeded"], False)
        self.assertTrue(result["effect_absent"])

    def test_missing_credential_preserves_prepared_operation_and_wait_reason(self):
        operation = self._operation()
        previous = os.environ.pop("DO_MATH_TEST_MISSING_SECRET", None)
        self.addCleanup(lambda: os.environ.__setitem__("DO_MATH_TEST_MISSING_SECRET", previous) if previous else None)
        result = execute_operation(
            operation, self._grant(credential_env={"Authorization": "DO_MATH_TEST_MISSING_SECRET"}),
            persist=lambda _: True,
        )
        self.assertEqual(result["status"], "prepared")
        self.assertFalse(result["transmitted"])
        self.assertEqual(result["waiting_reason"]["kind"], "credential_unavailable")

    def test_revocation_cancels_only_untransmitted_prepared_effects(self):
        instance = {'id': 'I', 'governance_sources': {'user': gov.preserve_source(
            'user', 'Authorize the HTTP grant, then revoke it.', origin='user')}}
        instance, _, _ = apply_decision(instance, {}, {'kind': 'grant', 'grant': {
            'id': 'G', 'kind': 'http', 'reuse': 'reusable', 'allowed_origins': ['https://example.test'],
            'allowed_methods': ['POST'], 'allowed_path_prefixes': ['/submit'], 'credential_env': {}}}, source_ref='user')
        operation = self._operation()
        runtime = {"status": "ready", "tasks": {}, "queue": [], "executions": {}, "external_operations": {operation["id"]: operation}}
        _, updated, _ = apply_decision(instance, runtime, {"kind": "revoke", "grant_id": "G", "decision_id": "D"}, source_ref="user")
        self.assertEqual(updated["external_operations"][operation["id"]]["status"], "cancelled")
        self.assertFalse(updated["external_operations"][operation["id"]]["transmitted"])

    def test_overlapping_grants_are_not_selected_by_identifier_order(self):
        instance = {'id': 'I', 'governance_sources': {'user': gov.preserve_source(
            'user', 'Authorize two reusable work grants.', origin='user')}}
        runtime = {'tasks': {}, 'executions': {}, 'queue': []}
        for identifier in ('A', 'B'):
            instance, runtime, _ = apply_decision(instance, runtime, {'kind': 'grant', 'grant': {
                'id': identifier, 'kind': 'local', 'reuse': 'reusable', 'roles': ['research_work'],
                'budget_kind': 'work'}}, source_ref='user')
        decision = authorize(instance, {'id': 'AC', 'role': 'research_work', 'budget_kind': 'work',
                                        'actor_kind': 'ai'}, runtime=runtime)
        self.assertFalse(decision["allowed"])
        self.assertEqual(decision["reason"], "ambiguous current grants")

    def test_import_schema_requires_coordinate_covered_meaning_units(self):
        schema = interpretation_schema("interpret")
        self.assertIn("import_units", schema["properties"])
        unit = schema["properties"]["import_units"]["items"]["required"]
        self.assertEqual(unit, ["unit_id", "source_range", "interpretation", "owner_kind", "owner_ref", "payload", "decision_refs", "question_refs"])

    def test_case_delegation_requires_explicit_scope_and_independent_check(self):
        from do_math.delegations import authorize_delegated_case

        delegation = {
            "id": "DG", "status": "active", "decision_kind": "task_scope",
            "original_decision_id": "DC", "included_targets": ["T"], "excluded_targets": [],
            "external_effects": [], "expires_at": None,
        }
        allowed = authorize_delegated_case(
            {"delegations": {"DG": delegation}}, "DG",
            {"decision_kind": "task_scope", "target_id": "T", "check": {"decision": "match", "scope_complete": True, "independent": True}},
        )
        # A caller's independent=True flag does not resolve either real execution.
        self.assertFalse(allowed["allowed"])
        denied = authorize_delegated_case(
            {"delegations": {"DG": delegation}}, "DG",
            {"decision_kind": "task_scope", "target_id": "T", "check": {"decision": "match", "scope_complete": True, "independent": False}},
        )
        self.assertFalse(denied["allowed"])


    def test_external_rejection_resolution_requires_a_current_structured_record(self):
        instance = {"goal_status": "mathematically_solved", "governance": {"CH": {
            "id": "CH", "kind": "charter", "status": "active", "revision": 1,
            "content": {"goal": "P", "academic_requirements": [{
                "id": "R", "scope": "s", "criteria": ["c"], "assessor": "research_plan"}]}}}}
        basis = solution_basis("goal", [{"id": "K"}])
        runtime = {
            "tasks": {}, "academic_assessments": [],
            "external_rejections": [{"id": "RJ", "solution_basis": basis, "resolved": True, "resolution_evidence": "old text"}],
            "academic_resolution_records": [],
        }
        self.assertEqual(academic_status(instance, runtime, basis)["status"], "externally_rejected")
        runtime["academic_resolution_records"].append({
            "rejection_id": "RJ", "solution_basis": basis, "decision": "resolved", "execution_id": "E",
            "evidence_refs": ["artifact:response"], "current": True,
        })
        self.assertEqual(academic_status(instance, runtime, basis)["status"], "externally_rejected")


class AcademicConsumerTests(unittest.TestCase):
    """Actual academic producer and TASKS consumers; mathematical evidence is synthetic."""

    def host(self):
        from do_math.academic_engine import AcademicEngineMixin
        from do_math.decision_engine import DecisionEngineMixin
        from do_math.scheduler import SchedulerMixin
        from do_math.revision_engine import RevisionEngineMixin
        from do_math.execution_profiles import seal_profile, profile_ref, BOUNDARY
        class Host(AcademicEngineMixin, DecisionEngineMixin, SchedulerMixin, RevisionEngineMixin):
            def _solution_basis(self): return deepcopy(self.basis)
            def _academic_evidence(self, ref): return None
            def _lifecycle_now(self):
                from do_math.governance import timestamp
                return timestamp('2026-09-20T00:00:00Z')
            def _remove_action(self, action):
                self.runtime['queue'][:] = [a for a in self.runtime['queue'] if a['id'] != action['id']]
            def _apply_input_overflow_resolutions(self, choices, fixed, execution_id):
                from do_math.engine import ResearchEngine
                return ResearchEngine._apply_input_overflow_resolutions(self, choices, fixed, execution_id)
            def _enqueue(self, role, target=None, **fields):
                self.runtime['queue'].append({'id': 'A' + str(len(self.runtime['queue'])),
                                             'role': role, 'target': target, **fields})
        h = Host()
        source = gov.preserve_source('S', 'Synthetic approval of a manuscript requirement', origin='user')
        record = charter()
        record['content']['academic_requirements'] = [{'id': 'AR', 'scope': 'Prepare a manuscript',
            'assessor': 'research_plan', 'criteria': ['Explain the proof', 'Discuss the limitations']}]
        h.instance = gov.initialize_governance({'id': 'I', 'feature_version': 5}, source,
            {'id': 'D', 'actor': 'user', 'source_ref': 'S', 'source_sha256': source['sha256'],
             'record_hashes': {'CH1': gov.digest(record)}}, [record])
        from do_math.execution_profiles import build_profiles
        from do_math.engine import DEFAULT_CONFIG
        config = {**deepcopy(DEFAULT_CONFIG),
                  'tool_review_window_seconds': 60, 'self_check_response_window_seconds': 5}
        profile = next(p for p in build_profiles(config)['execution_profiles'].values()
                       if p['role'] == 'research_work')
        h.instance.update(goal_status='mathematically_solved', knowledge={}, sources=[], config=config,
            execution_profiles={profile['id']: profile}, role_profile_refs={'research_work': [profile_ref(profile)]},
            grants={'G': {'id': 'G', 'kind': 'local', 'status': 'active', 'roles': ['research_work'],
                          'source_ref': 'S', 'reuse': 'reusable', 'resource_limits': {}}})
        h.runtime = {'status': 'ready', 'tasks': {}, 'executions': {}, 'queue': [], 'inputs': [],
                     'waiting_actions': {}, 'history': [], 'questions': []}
        h.basis = solution_basis('synthetic-current-goal', [h.instance['governance_sources']['S']])
        return h

    def generated(self):
        h = self.host(); h._ensure_academic_followup()
        return h, next(iter(h.runtime['tasks'].values()))

    def reviewed(self):
        from do_math import planning, contracts
        h, task = self.generated()
        from research_fixtures import prepared_rule_conditions
        action = next(a for a in h.runtime['queue'] if a.get('observation_rule_targets'))
        h.runtime['executions']['PREP'] = {'id': 'PREP', 'role': 'research_preparation', 'status': 'ended',
            'action': action, 'extensions': {'task_conditions': prepared_rule_conditions([task['id']])}}
        h._finish_assessment_preparation(action, 'PREP')
        h._remove_action(action)
        output = {'item_reviews': [{'item_id': key, 'decision': 'approved', 'evidence_refs': [task['id']],
            'findings': [], 'missing_inputs': [], 'next_owner': 'research_preparation'}
            for key in contracts.CONTRACT_REVIEW_ITEMS]}
        task['reviews'].append(planning.seal_contract_review(task, output, h.instance, h.runtime, execution_id='REVIEW'))
        return h, task

    def assessed(self, *, kind='fulfilled', decision='completed'):
        from do_math.task_scope import apply_task_assessments
        h, task = self.reviewed()
        tid = task['id']
        task['results'] = [{'execution_id': 'WORK', 'report': 'Synthetic returned manuscript'}]
        h.runtime['executions'].update(WORK={'id': 'WORK', 'role': 'research_work', 'status': 'ended', 'action': {'target': tid}},
            PLAN={'id': 'PLAN', 'role': 'research_plan', 'status': 'ended', 'input_solution_basis': deepcopy(h.basis)})
        assessment = {'task_id': tid, 'decision': decision, 'item_dispositions': [
            {'obligation_id': o['id'], 'kind': kind, 'evidence_refs': ['WORK']} for o in task['completion_obligations']]}
        h.instance, h.runtime = apply_task_assessments(h.instance, h.runtime, [assessment],
            execution_id='PLAN', input_tasks=deepcopy(h.runtime['tasks']))
        return h, h.runtime['tasks'][tid], assessment

    def test_actual_constructor_review_and_ready_population_use_v5_contract(self):
        from do_math import planning, task_contracts
        h, task = self.reviewed()
        task_contracts.validate_task_contract(task)
        self.assertEqual(task['feature_version'], 5)
        self.assertEqual([o['claim'] for o in task['completion_obligations']],
                         ['Explain the proof', 'Discuss the limitations'])
        self.assertEqual(task['profile_refs'], h.instance['role_profile_refs']['research_work'])
        self.assertEqual(task['authority_refs'], ['G'])
        self.assertTrue({row['id'] for row in h.basis['records']}.issubset(task['inputs']))
        self.assertNotIn('completion_criteria', task)
        self.assertEqual(planning.task_ready(task, h.instance, h.runtime)['state'], 'ready')
        self.assertEqual(planning.ready_task_ids(h.runtime, h.instance), [task['id']])
        h._ensure_academic_followup()
        self.assertEqual(len(h.runtime['tasks']), 1)

    def test_actual_assessment_consumer_uses_item_dispositions_and_current_evidence(self):
        h, task, assessment = self.assessed()
        h._record_academic_assessment(task, assessment, 'PLAN')
        self.assertEqual(h._academic_status()['status'], 'completed')
        h._record_academic_assessment(task, assessment, 'PLAN')
        self.assertEqual(len(h.runtime['academic_assessments']), 1)
        h.runtime['executions']['WORK']['changed_evidence'] = True
        self.assertNotEqual(h._academic_status()['status'], 'completed')
        with self.assertRaises(ValueError): h._record_academic_assessment(task, assessment, 'PLAN')

    def test_open_disposition_keeps_followup_in_same_task_contract(self):
        h, task, assessment = self.assessed(kind='open', decision='incomplete')
        h._record_academic_assessment(task, assessment, 'PLAN')
        self.assertEqual(task['status'], 'waiting')
        self.assertEqual(h.runtime['academic_assessments'][0]['decision'], 'not_satisfied')
        h._ensure_academic_followup()
        self.assertEqual(len(h.runtime['tasks']), 1)

    def test_engine_plan_dispatch_consumes_generated_contract_and_applied_assessment(self):
        from do_math.engine import ResearchEngine
        from types import SimpleNamespace
        h, task = self.reviewed()
        tid = task['id']
        h.runtime['executions']['SELECT'] = {'id': 'SELECT', 'role': 'research_plan', 'status': 'ended', 'input_snapshot': 'before-work', 'input_bundle': 'BA-select'}
        first = deepcopy((h.instance, h.runtime))
        h.store = SimpleNamespace(load=lambda snapshot: (snapshot, *deepcopy(first)),
            read=lambda path, snapshot: json.dumps({'snapshot': 'before-work', 'tasks': list(first[1]['tasks'].values()), 'ready_task_ids': [tid]}).encode())
        h.head = 'before-work'
        h._evaluation_context = lambda snapshot=None: {'snapshot': snapshot}
        ResearchEngine._apply_plan(h, {'dispositions': [{'task_id': tid, 'kind': 'selected', 'reason': 'Current academic work',
            'next_owner': 'research_work', 'expected_research_change': 'Complete the manuscript'}],
            'task_assessments': [], 'goal_audit': False}, 'SELECT')
        task = h.runtime['tasks'][tid]
        self.assertEqual(task['status'], 'active')
        self.assertTrue(any(a['role'] == 'research_work' and a.get('target') == tid for a in h.runtime['queue']))
        task['results'] = [{'execution_id': 'WORK', 'report': 'Synthetic manuscript'}]
        h.runtime['executions'].update(WORK={'id': 'WORK', 'role': 'research_work', 'status': 'ended', 'action': {'target': tid}},
            PLAN={'id': 'PLAN', 'role': 'research_plan', 'status': 'ended', 'input_snapshot': 'after-work', 'input_bundle': 'BA-returned', 'input_solution_basis': h.basis})
        returned = deepcopy((h.instance, h.runtime))
        h.store = SimpleNamespace(load=lambda snapshot: (snapshot, *deepcopy(returned)),
            read=lambda path, snapshot: json.dumps({'snapshot': 'after-work', 'tasks': list(returned[1]['tasks'].values()), 'ready_task_ids': []}).encode())
        h.head = 'after-work'
        assessment = {'task_id': tid, 'decision': 'completed', 'item_dispositions': [
            {'obligation_id': o['id'], 'kind': 'fulfilled', 'evidence_refs': ['WORK']} for o in task['completion_obligations']]}
        ResearchEngine._apply_plan(h, {'dispositions': [], 'task_assessments': [assessment], 'goal_audit': False}, 'PLAN')
        self.assertEqual(h.runtime['tasks'][tid]['status'], 'completed')
        self.assertEqual(h._academic_status()['status'], 'completed')
        self.assertEqual(h.runtime['status'], 'completed')

    def test_unapplied_or_different_assessment_cannot_certify_academic_success(self):
        h, task, assessment = self.assessed()
        forged = deepcopy(assessment); forged['item_dispositions'][0]['evidence_refs'] = ['not-in-input']
        with self.assertRaises(ValueError): h._record_academic_assessment(task, forged, 'PLAN')
        task.pop('assessment')
        with self.assertRaises(ValueError): h._record_academic_assessment(task, assessment, 'PLAN')

    def test_v5_scope_waiver_records_authority_without_applying_a_second_task_lifecycle(self):
        from do_math.planning import contract_hash
        from do_math.task_scope import apply_task_assessments
        h, task = self.generated()
        task['results'] = [{'execution_id': 'WORK', 'report': 'Cannot satisfy the requirement'}]
        change = {'kind': 'task_scope', 'decision_id': 'WAIVER', 'task_id': task['id'],
            'disposition': 'waive', 'revision': task['revision'], 'contract_sha256': contract_hash(task),
            'obligation_ids': [row['id'] for row in task['completion_obligations']], 'reason': 'Synthetic explicit waiver'}
        before = deepcopy(task)
        h.instance, h.runtime, decision = gov.apply_decision(h.instance, h.runtime, change, source_ref='S')
        self.assertEqual(h.runtime['tasks'][task['id']], before)
        h.runtime['executions']['PLAN'] = {'id': 'PLAN', 'role': 'research_plan', 'status': 'ended', 'input_solution_basis': h.basis}
        assessment = {'task_id': task['id'], 'decision': 'closed', 'item_dispositions': [
            {'obligation_id': row['id'], 'kind': 'waived', 'authority_ref': decision['id'], 'evidence_refs': ['WORK']}
            for row in task['completion_obligations']]}
        h.instance, h.runtime = apply_task_assessments(h.instance, h.runtime, [assessment],
            execution_id='PLAN', input_tasks=deepcopy(h.runtime['tasks']))
        h._record_academic_assessment(h.runtime['tasks'][task['id']], assessment, 'PLAN')
        self.assertNotEqual(h._academic_status()['status'], 'completed')

    def test_v5_transfer_approval_does_not_copy_legacy_criteria_or_close_source(self):
        from do_math.planning import contract_hash
        h, task = self.generated()
        h.runtime['tasks']['RECIPIENT'] = {**deepcopy(task), 'id': 'RECIPIENT'}
        change = {'kind': 'task_scope', 'task_id': task['id'], 'disposition': 'transfer',
            'target_task_id': 'RECIPIENT', 'revision': task['revision'], 'contract_sha256': contract_hash(task),
            'obligation_ids': [task['completion_obligations'][0]['id']], 'reason': 'Transfer only the first obligation'}
        i, rt, _ = gov.apply_decision(h.instance, h.runtime, change, source_ref='S')
        self.assertEqual(rt['tasks'], h.runtime['tasks'])
        change['contract_sha256'] = 'stale'
        with self.assertRaises(ValueError): gov.apply_decision(h.instance, h.runtime, change, source_ref='S')

    def test_academic_only_charter_change_preserves_math_fact_and_replaces_requirement_task(self):
        h, task = self.generated()
        record = charter('CH2'); record['supersedes'] = ['CH1']
        record['content']['academic_requirements'] = [{'id': 'AR', 'scope': 'Prepare a manuscript',
            'assessor': 'research_plan', 'criteria': ['Revised manuscript']}]
        h.instance, h.runtime, _ = gov.apply_decision(h.instance, h.runtime,
            {'kind': 'charter', 'record': record}, source_ref='S')
        self.assertEqual(h.instance['goal_status'], 'mathematically_solved')
        h._ensure_academic_followup()
        self.assertEqual(h.runtime['tasks'][task['id']]['status'], 'closed')
        current = [t for t in h.runtime['tasks'].values() if t['status'] != 'closed']
        self.assertEqual(len(current), 1)
        self.assertEqual(current[0]['completion_obligations'][0]['claim'], 'Revised manuscript')
        changed = charter('CH3', 'Prove Q'); changed['supersedes'] = ['CH2']
        h.instance, h.runtime, _ = gov.apply_decision(h.instance, h.runtime,
            {'kind': 'charter', 'record': changed}, source_ref='S')
        self.assertEqual(h.instance['goal_status'], 'unsolved')


class ReplacementAuthorityTests(unittest.TestCase):
    def fixture(self):
        from do_math import delegations as d
        i = DomainGovernanceTests().initial()
        rt = {'tasks': {}, 'executions': {}, 'queue': [], 'status': 'ready',
              'review_cycles': {'RC': {'id': 'RC', 'knowledge_id': 'K', 'revision': 1}},
              'activities': {}}
        i['knowledge'] = {'K': {'id': 'K', 'revision': 1}}
        action = {'id': 'ACTION', 'role': 'identity_review', 'target': 'K', 'budget_kind': 'work',
                  'actor_kind': 'ai', 'purpose': 'record_replacement', 'review_cycle_id': 'RC',
                  'stage': 'initial', 'slot': 'R1', 'round': 0, 'replacement_for': 0,
                  'continuity_break_cause': 'permanent_loss'}
        i, rt, _ = gov.apply_decision(i, rt, {'kind': 'grant', 'decision_id': 'GRANT-DECISION',
            'grant': {'id': 'G', 'kind': 'local', 'roles': ['identity_review'], 'reuse': 'reusable',
                      'included_targets': ['K'], 'budget_kind': 'work', 'purposes': ['record_replacement']}}, source_ref='S')
        i['decisions']['ORIGINAL'] = {'id': 'ORIGINAL', 'actor': 'user', 'kind': 'review_replacement', 'source_ref': 'S'}
        i, rt, _ = gov.apply_decision(i, rt, {'kind': 'delegation', 'decision_id': 'DD', 'delegation': {
            'id': 'DG', 'status': 'active', 'decision_kind': 'review_replacement', 'original_decision_id': 'ORIGINAL',
            'included_targets': ['K'], 'excluded_targets': [], 'external_effects': [], 'resource_limits': {},
            'expires_at': '2099-01-01T00:00:00Z'}}, source_ref='S')
        effect = {key: action[key] for key in ('review_cycle_id', 'stage', 'slot', 'round', 'replacement_for', 'continuity_break_cause')}
        case = {'id': 'CASE', 'decision_kind': 'review_replacement', 'target_id': 'K',
                'external_effects': [], 'resources': {}, 'effect': effect, 'basis_refs': ['RC']}
        return i, rt, action, case

    def checked(self):
        from do_math import delegations as d
        i, rt, action, case = self.fixture()
        app = d.prepare_application(i, rt, 'DG', case)
        for eid, stage in [('INTERPRET', 'interpret'), ('CHECK', 'check')]:
            rt['executions'][eid] = {'id': eid, 'role': 'intent_interpretation', 'input_sha256': app['input_sha256']}
            d.record_judgment(rt, app['id'], {'input_sha256': app['input_sha256'], 'decision': 'within_scope',
                                           'reason': 'Synthetic matching case'}, execution_id=eid, stage=stage)
        return i, rt, action, {**case, 'application_id': app['id']}

    def test_general_machine_grant_does_not_require_new_semantic_delegation(self):
        i, rt, action, case = self.fixture()
        self.assertTrue(gov.authorize_review_replacement(i, rt, action)['allowed'])
        changed = deepcopy(i); changed['governance_sources']['S']['text'] += '!'
        self.assertFalse(gov.authorize_review_replacement(changed, rt, action)['allowed'])
        i['grants']['G']['expires_at'] = '2000-01-01T00:00:00Z'
        self.assertFalse(gov.authorize_review_replacement(i, rt, action)['allowed'])

    def test_real_checked_case_resolves_knowledge_and_rechecks_cycle_and_exact_effect(self):
        from do_math import delegations as d
        i, rt, action, case = self.checked()
        self.assertTrue(gov.authorize_review_replacement(i, rt, action, delegation_id='DG', case=case)['allowed'])
        forged = deepcopy(case); forged['effect']['slot'] = 'OTHER'
        self.assertFalse(d.authorize_delegated_case(i, 'DG', forged, runtime=rt)['allowed'])
        rt['review_cycles']['RC']['revision'] = 2
        self.assertFalse(gov.authorize_review_replacement(i, rt, action, delegation_id='DG', case=case)['allowed'])

    def test_expired_or_missing_independent_check_denies_semantic_reuse(self):
        i, rt, action, case = self.checked()
        self.assertFalse(gov.authorize_review_replacement(i, rt, action, delegation_id='DG', case=case,
                                                        at='2100-01-01T00:00:00Z')['allowed'])
        rt['delegation_applications'][case['application_id']]['judgments'].pop('check')
        self.assertFalse(gov.authorize_review_replacement(i, rt, action, delegation_id='DG', case=case)['allowed'])


class AuditRepairTests(unittest.TestCase):
    def checked_import(self, kind='charter', handlers=None, payload=None):
        i, rt, source, output = DomainGovernanceTests().import_fixture()
        replacement = charter('CH2', 'Prove Q'); replacement['supersedes'] = ['CH1']
        payload = payload or {'kind': kind, 'record': replacement}
        output.update(questions=[], question_details=[], needs_clarification=False)
        output['import_units'][0].update(owner_kind=kind, owner_ref=payload.get('record', {}).get('id', 'I'),
                                        payload=payload, question_refs=[])
        bundle = gov.prepare_import(i, rt, source, output, execution_id='E1', owner_handlers=handlers)
        rt['executions']['E2'] = {'role': 'intent_interpretation', 'intent_import_sha256': bundle['sha256']}
        bundle = gov.check_import(i, rt, bundle['id'], {'bundle_sha256': bundle['sha256'], 'decision': 'approved',
            'scope_complete': True, 'unit_ids': ['U'], 'question_ids': [], 'findings': []}, execution_id='E2',
            owner_handlers=handlers)
        request = {'id': 'LATER', 'action': 'decision', 'origin': 'user', 'text': 'Approve this exact checked change',
            'config': {'kind': 'import_approval', 'import_id': bundle['id'], 'bundle_sha256': bundle['sha256'],
                       'check_sha256': bundle['check']['sha256'], 'unit_hashes': {'U': gov.digest(payload)}}}
        rt['waiting_actions'] = {'CHECK': {'kind': 'import_application_authority', 'import_id': bundle['id'],
                                         'action': {'id': 'CHECK', 'role': 'intent_interpretation', 'stage': 'check'}}}
        return i, rt, bundle, request

    def test_later_exact_approval_resumes_apply_without_rechecking(self):
        i, rt, bundle, request = self.checked_import()
        before = deepcopy(rt['intent_imports'][bundle['id']]['check'])
        i, rt, result = gov.apply_import_control(i, rt, request)
        self.assertEqual(gov.governance_view(i)['goal'], 'Prove Q')
        self.assertEqual(result['status'], 'applied')
        self.assertEqual(rt['intent_imports'][bundle['id']]['check'], before)
        self.assertNotIn('CHECK', rt['waiting_actions'])
        repeated_i, repeated_rt, repeated = gov.apply_import_control(i, rt, request)
        self.assertEqual((repeated_i, repeated_rt, repeated), (i, rt, result))

    def test_later_approval_rejects_changed_seal_and_changed_premise(self):
        i, rt, bundle, request = self.checked_import()
        wrong = deepcopy(request); wrong['config']['check_sha256'] = 'wrong'
        with self.assertRaises(ValueError): gov.apply_import_control(i, rt, wrong)
        i['decisions']['D']['revoked'] = True
        with self.assertRaises(ValueError): gov.apply_import_control(i, rt, request)
        self.assertNotIn('LATER', i['governance_sources'])

    def test_import_application_receipt_binds_approval_and_rejects_tampering(self):
        i, rt, bundle, request = self.checked_import()
        i, rt, receipt = gov.apply_import_control(i, rt, request)
        self.assertEqual(receipt['approvals']['U']['source_ref'], 'LATER')
        self.assertEqual(receipt['check_sha256'], bundle['check']['sha256'])
        rt['intent_imports'][bundle['id']]['application']['applied_units'] = []
        with self.assertRaises(ValueError): gov.apply_import_control(i, rt, request)

    def test_changed_premise_reopens_checked_import_without_fabricated_text_change(self):
        i, rt, bundle, request = self.checked_import()
        output = deepcopy(bundle['output'])
        output['repair'] = {'previous_sha256': bundle['sha256'], 'changed_unit_ids': [],
                            'actions': ['Re-evaluate the changed governing premise']}
        with self.assertRaises(ValueError):
            gov.prepare_import(i, rt, bundle['source'], output, execution_id='NEW', previous_id=bundle['id'])
        i['decisions']['D']['revoked'] = True
        reopened = gov.prepare_import(i, rt, bundle['source'], output, execution_id='NEW', previous_id=bundle['id'])
        self.assertEqual(reopened['status'], 'checking')
        self.assertNotEqual(reopened['basis_sha256'], bundle['basis_sha256'])
        self.assertEqual(rt['intent_imports'][bundle['id']]['check'], bundle['check'])
        self.assertNotIn('check', reopened)

    def test_configuration_adapter_uses_actual_config_validator(self):
        from do_math.engine import DEFAULT_CONFIG
        handlers = gov.import_owner_handlers()
        def install(i, rt, unit, approval):
            i['config'] = {**i.get('config', {}), **unit['payload']['config']}; return i, rt
        gov.register_configuration_owner(handlers, apply=install)
        i, rt, source, output = DomainGovernanceTests().import_fixture()
        i['config'] = deepcopy(DEFAULT_CONFIG)
        output.update(questions=[], question_details=[], needs_clarification=False)
        output['import_units'][0].update(owner_kind='configuration', owner_ref='I', question_refs=[],
            payload={'kind': 'configuration', 'config': {'call_timeout_seconds': 0}})
        with self.assertRaises(ValueError): gov.prepare_import(i, rt, source, output, execution_id='E1', owner_handlers=handlers)

    def test_once_http_operation_and_its_execution_share_logical_case(self):
        grant = {'id': 'G', 'status': 'active', 'reuse': 'once'}
        operation = {'id': 'OP', 'grant_id': 'G', 'request_sha256': 'request'}
        action = {'id': 'AC-OP', 'role': 'external_action', 'target': 'OP', 'grant_id': 'G'}
        rt = {'external_operations': {'OP': operation}, 'executions': {
            'EX': {'id': 'EX', 'role': 'external_action', 'grant_id': 'G', 'action': action}}}
        self.assertIsNone(gov.grant_scope_reason(grant, action, rt))
        self.assertIsNone(gov.grant_scope_reason(grant, {'id': 'OP', 'role': 'external_operation'}, rt))
        self.assertIsNotNone(gov.grant_scope_reason(grant, {'id': 'OTHER', 'case_id': 'OP'}, rt))
        rt['external_operations']['SECOND'] = {'id': 'SECOND', 'grant_id': 'G'}
        self.assertIsNotNone(gov.grant_scope_reason(grant, action, rt))

    def test_registered_owner_applies_existing_knowledge_consumer(self):
        from do_math.repository import new_id
        candidate = {'id': new_id('KN'), 'kind': 'observation', 'title': 'Observation', 'statement': 'P observed',
                     'explanation': 'Limited observation', 'summary': 'Not a proof', 'lean_code': ''}
        for owner in ('research_record', 'evidence'):
            with self.subTest(owner=owner):
                i, rt, bundle, request = self.checked_import(kind=owner, payload={'kind': owner, 'record': candidate})
                i, rt, receipt = gov.apply_import_control(i, rt, request)
                self.assertIn(candidate['id'], i['knowledge'])
                self.assertTrue(any(a['role'] == 'research_plan' for a in rt['queue']))
                self.assertEqual(receipt['applied_units'], ['U'])
                self.assertIsNone(i['knowledge'][candidate['id']]['formal_result_id'])

    def test_registered_configuration_reuses_owner_callback_and_currentness(self):
        def install(i, rt, unit, approval):
            i['config'] = deepcopy(unit['payload']['config']); return i, rt
        handlers = gov.import_owner_handlers()
        gov.register_import_owner(handlers, 'configuration', apply=install,
            validate=lambda i, rt, unit: None, basis=lambda i, rt, unit: i.get('config'))
        i, rt, bundle, request = self.checked_import(kind='configuration', handlers=handlers,
            payload={'kind': 'configuration', 'config': {'model': 'approved'}})
        changed, _, _ = gov.apply_import_control(i, rt, request, owner_handlers=handlers)
        self.assertEqual(changed['config']['model'], 'approved')
        i['config'] = {'model': 'changed during review'}
        with self.assertRaises(ValueError): gov.apply_import_control(i, rt, request, owner_handlers=handlers)

    def audited(self):
        i = DomainGovernanceTests().initial(); rt = {'tasks': {}, 'executions': {}, 'queue': [], 'status': 'ready'}
        audit = {'id': 'AU', 'kind': 'additional_audit', 'revision': 1, 'supersedes': [], 'content': {
            'scope': ['P'], 'required_inputs': ['CH1'], 'assessor': 'goal_audit',
            'verdict_mapping': {'pass': 'satisfied', 'partial': 'not_satisfied', 'unknown': 'unresolved'}}}
        i, rt, _ = gov.apply_decision(i, rt, {'kind': 'additional_audit', 'record': audit}, source_ref='S')
        return i, rt

    def test_goal_audit_maps_actual_results_and_rejects_missing_or_stale_input(self):
        import jsonschema
        i, rt = self.audited()
        basis = gov.additional_audit_input(i, rt)
        rt['executions']['AUDIT'] = {'role': 'goal_audit', 'additional_audit_input': basis}
        row = {'audit_ref': 'AU', 'assessor': 'goal_audit', 'verdict': 'partial', 'reason': 'Only partial',
               'input_hashes': {'CH1': gov.digest(i['governance']['CH1'])}}
        jsonschema.Draft202012Validator(gov.additional_audit_schema(i)).validate([row])
        mapped = gov.evaluate_goal_audits(i, rt, 'AUDIT', [row])
        self.assertEqual(mapped[0]['decision'], 'not_satisfied')
        with self.assertRaises(ValueError): gov.validate_goal_additional_audits(i, [{'execution_id': 'AUDIT', 'additional_audits': mapped}])
        with self.assertRaises(ValueError): gov.evaluate_goal_audits(i, rt, 'AUDIT', [])
        row['verdict'] = 'pass'
        mapped = gov.evaluate_goal_audits(i, rt, 'AUDIT', [row])
        gov.validate_goal_additional_audits(i, [{'execution_id': 'AUDIT', 'additional_audits': mapped}])
        i['governance']['CH1']['content']['goal'] += ' changed'
        with self.assertRaises(ValueError): gov.evaluate_goal_audits(i, rt, 'AUDIT', [row])

    def test_audit_assessor_must_resolve_to_actual_execution_not_producer_claim(self):
        i, rt = self.audited()
        rt['executions']['AUDIT'] = {'role': 'goal_audit', 'additional_audit_input': gov.additional_audit_input(i, rt)}
        with self.assertRaises(ValueError): gov.evaluate_goal_audits(i, rt, 'AUDIT', [{
            'audit_ref': 'AU', 'verdict': 'pass', 'assessor': 'someone-else', 'reason': 'Claimed authority',
            'input_hashes': {'CH1': gov.digest(i['governance']['CH1'])}}])

    def test_goal_assurance_cannot_omit_active_additional_audit(self):
        from unittest.mock import patch
        from do_math.academic import apply_goal_assurance
        i, rt = self.audited()
        judgment = {'id': 'J', 'execution_id': 'AUDIT', 'slot': 0, 'basis': 'B', 'required': 1,
                    'decision': 'satisfied', 'scope_complete': True, 'current': True, 'formal_result_refs': ['FR']}
        i['goal_judgments'] = [judgment]; i['formal_results'] = {'FR': {'id': 'FR'}}
        with patch('do_math.knowledge_records.formal_usable', return_value=True):
            with self.assertRaises(ValueError): apply_goal_assurance(i, decision='mathematically_solved', basis='B', judgments=[judgment])

    def test_delegation_uses_case_hash_not_full_context_hash(self):
        from do_math import delegations as d
        i, rt, action, case = ReplacementAuthorityTests().fixture()
        app = d.prepare_application(i, rt, 'DG', case)
        for eid, stage in [('AUTHOR', 'interpret'), ('CHECKER', 'check')]:
            rt['executions'][eid] = {'id': eid, 'role': 'intent_interpretation', 'input_sha256': 'whole-context-' + eid,
                                     'delegation_input_sha256': app['input_sha256']}
            d.record_judgment(rt, app['id'], {'input_sha256': app['input_sha256'], 'decision': 'within_scope',
                'reason': 'Within exact delegated case'}, execution_id=eid, stage=stage)
        def effect(i, rt, change):
            rt['review_cycles']['RC']['installed_effect'] = deepcopy(change); return i, rt
        updated, state, receipt = d.apply_application(i, rt, app['id'], apply_effect=effect)
        self.assertEqual(receipt['effect'], case['effect'])
        self.assertEqual(updated['grants'], i['grants'])
        self.assertEqual(d.apply_application(updated, state, app['id'], apply_effect=effect)[2], receipt)
        rt['executions']['CHECKER']['role'] = 'research_work'
        self.assertFalse(d.authorize_delegated_case(i, 'DG', {'application_id': app['id']}, runtime=rt)['allowed'])

    def test_delegated_effect_cannot_rewrite_preserved_authority_source(self):
        from do_math import delegations as d
        i, rt, action, case = ReplacementAuthorityTests().checked()
        def bad_effect(i, rt, change):
            i['governance_sources']['NEW'] = gov.preserve_source('NEW', 'Forged authority', origin='user'); return i, rt
        with self.assertRaises(ValueError): d.apply_application(i, rt, case['application_id'], apply_effect=bad_effect)

    def test_actual_engine_delegation_control_to_independent_judgments_effect_and_receipt(self):
        import tempfile
        from do_math.engine import ResearchEngine
        from do_math import delegations as d
        from test_review_engine import FakeEngine, grant_replacement
        with tempfile.TemporaryDirectory() as root:
            engine = FakeEngine(root)
            grant_replacement(engine)
            cid = engine._start_identity_review('K1')
            action = deepcopy(engine.pending())
            engine._record_review_recovery(action, ValueError('permanent_loss'), retryable=False)
            engine.instance['decisions']['ORIGINAL'] = {'id': 'ORIGINAL', 'actor': 'user',
                'kind': 'review_replacement', 'source_ref': 'SOURCE-review'}
            engine.instance, engine.runtime, _ = gov.apply_decision(engine.instance, engine.runtime,
                {'kind': 'delegation', 'decision_id': 'DD', 'delegation': {'id': 'DG', 'status': 'active',
                 'decision_kind': 'review_replacement', 'original_decision_id': 'ORIGINAL',
                 'included_targets': ['K1'], 'excluded_targets': [], 'external_effects': [],
                 'resource_limits': {}, 'expires_at': None}}, source_ref='SOURCE-review')
            effect = {**{key: action[key] for key in ('review_cycle_id', 'stage', 'slot', 'round')},
                      'replacement_for': 0, 'continuity_break_cause': 'permanent_loss'}
            case = {'id': 'CASE', 'decision_kind': 'review_replacement', 'target_id': 'K1',
                    'external_effects': [], 'resources': {}, 'effect': effect, 'basis_refs': [cid]}
            request = {'id': 'REQUEST', 'action': 'request', 'config': {'role': 'maintenance', 'review_replacement': {
                'action': action, 'grant_id': 'GR-review', 'delegation_id': 'DG', 'case': case}}}
            engine.runtime.setdefault('history', []).append({'kind': 'user_control', 'request': request})
            self.assertTrue(ResearchEngine._review_recovery_control(engine, request))
            stages = [a for a in engine.runtime['queue'] if a.get('delegation_application_id')]
            self.assertEqual(len(stages), 2)
            app_id = stages[0]['delegation_application_id']
            shared = d.judgment_input(engine.runtime, app_id)
            before_authority = deepcopy({key: engine.instance.get(key) for key in ('decisions', 'grants', 'delegations')})
            for index, stage in enumerate(stages):
                self.assertEqual(d.judgment_input(engine.runtime, app_id), shared)
                eid = 'DG-' + str(index)
                engine.runtime['executions'][eid] = {'id': eid, 'role': 'intent_interpretation',
                    'input_sha256': 'full-context-' + eid, 'delegation_input_sha256': shared['input_sha256']}
                ResearchEngine._apply_delegation_judgment(engine, stage, {'delegation_judgment': {
                    'input_sha256': shared['input_sha256'], 'decision': 'within_scope',
                    'reason': 'Exact case is covered by original authority'}}, eid)
            app = engine.runtime['delegation_applications'][app_id]
            self.assertEqual(set(app['judgments']), {'interpret', 'check'})
            self.assertEqual(app['application']['effect'], effect)
            self.assertEqual({key: engine.instance.get(key) for key in before_authority}, before_authority)
            replacement = next(a for a in engine.runtime['queue'] if a.get('replacement_for') is not None)
            engine.runtime['queue'].remove(replacement); engine.runtime['queue'].insert(0, replacement)
            engine.execute(record_first=True)
            engine.execute()
            self.assertTrue(engine.usable())
            self.assertTrue(engine.runtime['review_cycles'][cid]['replacement_receipts'])


class ExternalScopeConsumerTests(unittest.TestCase):
    def test_external_scope_metadata_is_checked_in_actual_send_and_once_ledger(self):
        from do_math.external import prepare_operation, execute_operation
        grant = {'id': 'G', 'kind': 'http', 'status': 'active', 'reuse': 'once',
            'included_targets': ['T'], 'purposes': ['publish'], 'subjects': ['external_operation'],
            'budget_kind': 'operations', 'execution_kinds': ['machine'],
            'allowed_origins': ['https://example.test'], 'allowed_methods': ['POST'], 'allowed_path_prefixes': ['/']}
        op = prepare_operation({'method': 'POST', 'url': 'https://example.test/p'}, 'G', 'S',
            target_id='T', purpose='publish', subject='external_operation', budget_kind='operations', actor_kind='machine')
        calls = []
        transport = lambda *args: calls.append(args) or {'http_status': 200, 'body': b'ok'}
        result = execute_operation(op, grant, persist=lambda row: True, transport=transport, runtime={})
        self.assertEqual(result['status'], 'confirmed')
        bad = deepcopy(op); bad['purpose'] = 'unapproved'
        with self.assertRaises(ValueError): execute_operation(bad, grant, persist=lambda row: True, transport=transport, runtime={})
        with self.assertRaises(ValueError): execute_operation(op, grant, persist=lambda row: True, transport=transport,
            runtime={'external_operations': {'USED': {**result, 'id': 'USED'}}})
        self.assertEqual(len(calls), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
