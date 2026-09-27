"""Governance records: the charter and policies, the imported user intent, grants, approvals and registered owners.

These tests specify facts and authority boundaries, not provider capabilities.
"""
from __future__ import annotations

from pathlib import Path
import json
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math.repository import exact_content_hash

from do_math.governance import apply_decision, authorize, interpretation_schema
from do_math import governance as gov, questions, submission
from copy import deepcopy
from unittest.mock import create_autospec

from research_fixtures import charter, governance_start
from record_fixtures import checked_import, domain_governance, governance_import


class DomainGovernanceTests(unittest.TestCase):
    def test_initialized_charter_is_single_authority_and_binds_approved_original(self):
        i = domain_governance()
        self.assertNotIn("goal", i)
        self.assertNotIn("policies", i)
        self.assertEqual(gov.governance_view(i)["goal"], "Prove P")
        self.assertEqual(i["governance"]["CH1"]["approval_ref"], "D")
        changed = deepcopy(i["governance_sources"]["S"]); changed["text"] += "!"
        with self.assertRaises(ValueError):
            gov.initialize_governance(governance_start({"id": "I"}), changed, i["decisions"]["D"], [charter()])

    def test_policy_coexists_and_only_explicit_supersession_retires_old_rule(self):
        i = domain_governance(); runtime = {"tasks": {}, "executions": {}, "queue": [], "status": "ready"}
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
        i = domain_governance(); rt = {"tasks": {}, "executions": {}, "queue": [], "status": "ready"}
        context = {"id": "CX", "kind": "research_context", "revision": 1, "supersedes": [],
                   "content": {"terms": [{"term": "P", "definition": "the target", "boundary": "this problem",
                                          "avoid_synonyms": [], "record_refs": []}]}}
        i, rt, _ = gov.apply_decision(i, rt, {"kind": "research_context", "record": context}, source_ref="S")
        audit = {"id": "AU", "kind": "additional_audit", "revision": 1, "supersedes": [],
                 "content": {"scope": ["P"], "required_inputs": ["CH1"], "assessor": "goal_audit",
                             "verdict_mapping": {"pass": "satisfied", "fail": "not_satisfied", "unknown": "unresolved"}}}
        i, rt, _ = gov.apply_decision(i, rt, {"kind": "additional_audit", "record": audit}, source_ref="S")
        self.assertEqual(gov.governance_view(i)["additional_audits"][0]["id"], "AU")
        audit["id"] = "AU2"; audit["content"]["verdict_mapping"]["pass"] = "unsupported_assurance"
        with self.assertRaises(ValueError):
            gov.apply_decision(i, rt, {"kind": "additional_audit", "record": audit}, source_ref="S")

    def test_import_holes_and_self_check_are_rejected_and_questions_still_checked(self):
        i, rt, s, output = governance_import()
        bad = deepcopy(output); bad["import_units"][0]["source_range"]["end"] = 7
        with self.assertRaises(ValueError): gov.prepare_import(i, rt, s, bad, execution_id="E1", input_ref="IN")
        bundle = gov.prepare_import(i, rt, s, output, execution_id="E1", input_ref="IN")
        rt["executions"]["E2"] = {"role":"intent_interpretation", "intent_import_sha256":bundle["sha256"]}
        check = {"bundle_sha256": bundle["sha256"], "decision": "approved", "scope_complete": True,
                 "unit_ids": ["U"], "question_ids": ["Q"], "findings": []}
        with self.assertRaises(ValueError): gov.check_import(i, rt, bundle["id"], check, execution_id="E1")
        gov.check_import(i, rt, bundle["id"], check, execution_id="E2")
        updated, updated_rt, outcome = gov.apply_import(i, rt, bundle["id"])
        self.assertEqual(outcome["status"], "applied")
        self.assertFalse(questions.user_waits({"role": "research_preparation"}, updated, updated_rt))

    def test_import_reauthor_requires_current_failed_parent_and_repair_coordinates(self):
        i, rt, s, out = governance_import()
        b = gov.prepare_import(i, rt, s, out, execution_id="E1", input_ref="IN")
        rt["executions"]["E2"] = {"role":"intent_interpretation", "intent_import_sha256":b["sha256"]}
        gov.check_import(i, rt, b["id"], {"bundle_sha256": b["sha256"], "decision": "revision_required",
            "scope_complete": True, "unit_ids": ["U"], "question_ids": ["Q"], "findings": ["Question incomplete"]}, execution_id="E2")
        with self.assertRaises(ValueError): gov.prepare_import(i, rt, s, out, execution_id="E3", input_ref="IN", previous_id=b["id"])
        out["repair"] = {"previous_sha256": b["sha256"], "changed_unit_ids": ["U"], "actions": ["Add scope option"]}
        out["question_details"][0]["options"].append({"text":"Change scope", "effect":"Ask for a replacement charter"})
        newer = gov.prepare_import(i, rt, s, out, execution_id="E3", input_ref="IN", previous_id=b["id"])
        self.assertEqual(newer["previous_id"], b["id"])
        with self.assertRaises(ValueError): gov.apply_import(i, rt, b["id"])

    def test_import_currentness_binds_actual_structured_task_contract(self):
        i, rt, source, output = governance_import()
        rt['tasks']['T'] = {'id': 'T', 'revision': 1, 'status': 'planned', 'question': 'Original task'}
        output['used_sources'] = ['T']
        bundle = gov.prepare_import(i, rt, source, output, execution_id='AUTHOR', input_ref="IN")
        rt['executions']['CHECK'] = {'role': 'intent_interpretation', 'intent_import_sha256': bundle['sha256']}
        rt['tasks']['T']['question'] = 'A different task under the same nominal revision'
        with self.assertRaises(ValueError):
            gov.check_import(i, rt, bundle['id'], {'bundle_sha256': bundle['sha256'], 'decision': 'approved',
                'scope_complete': True, 'unit_ids': ['U'], 'question_ids': ['Q'], 'findings': []}, execution_id='CHECK')

    def test_unapproved_or_stale_import_cannot_change_charter(self):
        i, rt, s, output = governance_import()
        replacement = charter("CH2", "Prove Q"); replacement["supersedes"] = ["CH1"]
        output.update(questions=[], question_details=[], needs_clarification=False)
        unit = output["import_units"][0]; unit.update(owner_ref="CH2", question_refs=[], payload={"kind": "charter", "record": replacement})
        b = gov.prepare_import(i, rt, s, output, execution_id="E1", input_ref="IN")
        rt["executions"]["E2"] = {"role":"intent_interpretation", "intent_import_sha256":b["sha256"]}
        gov.check_import(i, rt, b["id"], {"bundle_sha256": b["sha256"], "decision": "approved", "scope_complete": True,
                                      "unit_ids": ["U"], "question_ids": [], "findings": []}, execution_id="E2")
        with self.assertRaises(ValueError): gov.apply_import(i, rt, b["id"])
        approvals = {"U": {"actor": "user", "source_ref": s["id"], "source_sha256": s["sha256"], "change_sha256": exact_content_hash(unit["payload"])}}
        changed, state, event = gov.apply_import(i, rt, b["id"], approvals=approvals)
        self.assertEqual(gov.governance_view(changed)["goal"], "Prove Q")
        self.assertEqual(event["status"], "applied")
        _, repeated_state, repeated_event = gov.apply_import(changed, state, b["id"], approvals=approvals)
        self.assertEqual(repeated_event, event)
        self.assertEqual(repeated_state, state)
        stale = deepcopy(i); stale["decisions"]["D"]["source_sha256"] = "0" * 64
        with self.assertRaises(ValueError): gov.apply_import(stale, rt, b["id"], approvals=approvals)

    def test_explicit_once_grant_and_exclusions_use_existing_execution_ledger(self):
        i = {"grants": {"G": {"id": "G", "kind": "local", "status": "active",
             "roles": ["research_work"], "task_ids": [], "excluded_targets": ["B"], "reuse": "once",
             "source_ref": "S", "subjects": ["research_work"], "resource_limits": {}}}}
        rt = {"executions": {"E": {"id": "E", "grant_id": "G", "action": {"id": "A1"}}}}
        self.assertFalse(gov.authorize(i, {"id": "A2", "role": "research_work", "target": "A"}, runtime=rt)["allowed"])
        self.assertFalse(gov.authorize(i, {"id": "A1", "role": "research_work", "target": "B"}, runtime={})["allowed"])

    def test_initialization_cannot_rebind_another_immutable_original(self):
        source = gov.preserve_source("S", "P", origin="user")
        records = [charter()]
        approval = {"id":"D", "actor":"user", "source_ref":"S", "source_sha256":source["sha256"], "record_hashes":{"CH1":exact_content_hash(records[0])}}
        with self.assertRaises(ValueError):
            gov.initialize_governance(governance_start({"lifecycle":{"immutable_input":{"text":"Q", "sha256":"different", "bytes":1}}}), source, approval, records)

    def test_stored_governance_content_must_still_match_approved_proposal(self):
        i = domain_governance(); i["governance"]["CH1"]["content"]["goal"] = "Unapproved Q"
        with self.assertRaises(ValueError): gov.validate_governance_state(i)

    def test_import_check_must_resolve_a_real_execution_and_bound_input(self):
        i, rt, s, output = governance_import()
        bundle = gov.prepare_import(i, rt, s, output, execution_id="E1", input_ref="IN")
        with self.assertRaises(ValueError):
            gov.check_import(i, rt, bundle["id"], {"bundle_sha256":bundle["sha256"], "decision":"approved", "scope_complete":True,
                            "unit_ids":["U"], "question_ids":["Q"], "findings":[]}, execution_id="FAKE")

    def test_import_reapplication_is_idempotent(self):
        i, rt, s, output = governance_import()
        b = gov.prepare_import(i, rt, s, output, execution_id="E1", input_ref="IN")
        rt["executions"]["E2"] = {"role":"intent_interpretation", "intent_import_sha256":b["sha256"]}
        gov.check_import(i, rt, b["id"], {"bundle_sha256":b["sha256"], "decision":"approved", "scope_complete":True,
                         "unit_ids":["U"], "question_ids":["Q"], "findings":[]}, execution_id="E2")
        i, rt, first = gov.apply_import(i, rt, b["id"])
        _, second, result = gov.apply_import(i, rt, b["id"])
        self.assertEqual(first, result)
        self.assertEqual(len(rt["question_links"]),len(second["question_links"]))

    def test_additional_audit_consumes_exact_required_inputs_and_mapping(self):
        i = domain_governance(); rt = {"tasks":{},"executions":{},"queue":[]}
        r = {"id":"AU", "kind":"additional_audit", "revision":1,"supersedes":[],
             "content":{"scope":["P"],"required_inputs":["CH1"],"assessor":"goal_audit","verdict_mapping":{"pass":"satisfied","fail":"not_satisfied","unknown":"unresolved"}}}
        i, _, _ = gov.apply_decision(i,rt,{"kind":"additional_audit","record":r},source_ref="S")
        with self.assertRaises(ValueError): gov.evaluate_additional_audit(i,"AU","pass",assessor="goal_audit",input_hashes={})
        verdict = gov.evaluate_additional_audit(i,"AU","pass",assessor="goal_audit",input_hashes={"CH1":exact_content_hash(i["governance"]["CH1"])})
        self.assertEqual(verdict["decision"],"satisfied")
        self.assertEqual(i["goal_status"],"unsolved")

    def test_grant_replacement_is_atomic_and_expiry_disposes_current_consumers(self):
        i=domain_governance();rt={"tasks":{},"executions":{},"queue":[]}
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

    def test_local_execution_kind_is_not_ignored(self):
        i={"grants":{"G":{"id":"G","kind":"local","status":"active","roles":["research_work"],
            "reuse":"reusable","execution_kinds":["machine"]}}}
        self.assertFalse(gov.authorize(i,{"role":"research_work","actor_kind":"ai"},runtime={})["allowed"])

    def test_import_repair_cannot_claim_unchanged_units_were_changed(self):
        i,rt,s,out=governance_import();b=gov.prepare_import(i,rt,s,out,execution_id="E1", input_ref="IN")
        rt["executions"]["E2"]={"role":"intent_interpretation","intent_import_sha256":b["sha256"]}
        gov.check_import(i,rt,b["id"],{"bundle_sha256":b["sha256"],"decision":"revision_required","scope_complete":True,"unit_ids":["U"],"question_ids":["Q"],"findings":["Correct interpretation"]},execution_id="E2")
        out["repair"]={"previous_sha256":b["sha256"],"changed_unit_ids":["U"],"actions":["Claim repaired"]}
        with self.assertRaises(ValueError):gov.prepare_import(i,rt,s,out,execution_id="E3", input_ref="IN",previous_id=b["id"])

    def test_initial_original_and_later_explicit_approval_remain_distinct(self):
        source=gov.preserve_source("ORIG","Research P",origin="user")
        approval_source=gov.preserve_source("APPROVAL","Approve this exact charter",origin="user")
        record=charter();approval={"id":"D","actor":"user","source_ref":"APPROVAL","source_sha256":approval_source["sha256"],
            "input_source_ref":"ORIG","input_source_sha256":source["sha256"],"record_hashes":{"CH1":exact_content_hash(record)}}
        i=gov.initialize_governance(governance_start({"id":"I","lifecycle":{"immutable_input":{k:source[k] for k in ("text","sha256","bytes")}}}),source,approval,[record],approval_source=approval_source)
        self.assertEqual(i["governance"]["CH1"]["source_ref"],"ORIG")
        self.assertEqual(i["decisions"]["D"]["source_ref"],"APPROVAL")
        gov.validate_governance_state(i)

    def test_resumed_author_session_is_not_an_independent_import_check(self):
        i,rt,s,out=governance_import();b=gov.prepare_import(i,rt,s,out,execution_id="E1", input_ref="IN")
        rt["executions"]["E2"]={"role":"intent_interpretation","intent_import_sha256":b["sha256"],"continuation_of":"E1"}
        with self.assertRaises(ValueError):gov.check_import(i,rt,b["id"],{"bundle_sha256":b["sha256"],"decision":"approved","scope_complete":True,
                              "unit_ids":["U"],"question_ids":["Q"],"findings":[]},execution_id="E2")

    def test_intent_schema_covers_the_actual_check_and_repair_contract(self):
        import jsonschema
        i,rt,s,out=governance_import()
        out.update(summary="question",used_sources=["S"])
        jsonschema.validate(out,gov.interpretation_schema("interpret"))
        check={"summary":"checked","used_sources":["S"],"questions":[],"bundle_sha256":"a"*64,"decision":"approved",
               "scope_complete":True,"unit_ids":["U"],"question_ids":["Q"],"findings":[]}
        jsonschema.validate(check,gov.interpretation_schema("check"))
        with self.assertRaises(jsonschema.ValidationError):jsonschema.validate({**check,"decision":"match"},gov.interpretation_schema("check"))

    def test_question_coordinates_must_reciprocate_unit_question_references(self):
        i,rt,s,out=governance_import()
        other=deepcopy(out["import_units"][0]);other.update(unit_id="V",source_range={"start":4,"end":8},question_refs=[])
        out["import_units"][0]["source_range"]["end"]=4;out["import_units"].append(other)
        out["question_details"][0]["source_unit_ids"]=["V"]
        with self.assertRaises(ValueError):gov.prepare_import(i,rt,s,out,execution_id="E1", input_ref="IN")

    def test_advisory_question_does_not_leave_import_waiting_for_a_decision(self):
        i,rt,s,out=governance_import();b=gov.prepare_import(i,rt,s,out,execution_id="E1", input_ref="IN")
        rt["executions"]["E2"]={"role":"intent_interpretation","intent_import_sha256":b["sha256"]}
        gov.check_import(i,rt,b["id"],{"bundle_sha256":b["sha256"],"decision":"approved","scope_complete":True,
                         "unit_ids":["U"],"question_ids":["Q"],"findings":[]},execution_id="E2")
        _,state,result=gov.apply_import(i,rt,b["id"])
        self.assertEqual(result["status"],"applied")
        self.assertEqual(state["question_links"][0]["status"],"open")
        i,rt,s,out=governance_import();out["question_details"][0]["blocks"]=True
        b=gov.prepare_import(i,rt,s,out,execution_id="E1", input_ref="IN")
        rt["executions"]["E2"]={"role":"intent_interpretation","intent_import_sha256":b["sha256"]}
        gov.check_import(i,rt,b["id"],{"bundle_sha256":b["sha256"],"decision":"approved","scope_complete":True,
                         "unit_ids":["U"],"question_ids":["Q"],"findings":[]},execution_id="E2")
        _,state,result=gov.apply_import(i,rt,b["id"])
        self.assertEqual(result["status"],"awaiting_decision")
        self.assertTrue(questions.user_waits({"role":"research_preparation"},i,state))

    def test_overlapping_grants_are_not_selected_by_identifier_order(self):
        instance = governance_start({'id': 'I', 'governance_sources': {'user': gov.preserve_source(
            'user', 'Authorize two reusable work grants.', origin='user')}})
        runtime = {'tasks': {}, 'executions': {}, 'queue': []}
        for identifier in ('A', 'B'):
            instance, runtime, _ = apply_decision(instance, runtime, {'kind': 'grant', 'grant': {
                'id': identifier, 'kind': 'local', 'reuse': 'reusable', 'roles': ['research_work']}},
                source_ref='user')
        decision = authorize(instance, {'id': 'AC', 'role': 'research_work', 'actor_kind': 'ai'}, runtime=runtime)
        self.assertFalse(decision["allowed"])
        self.assertEqual(decision["reason"], "ambiguous current grants")

    def test_import_schema_requires_coordinate_covered_meaning_units(self):
        schema = interpretation_schema("interpret")
        self.assertIn("import_units", schema["properties"])
        unit = schema["properties"]["import_units"]["items"]["required"]
        self.assertEqual(unit, ["unit_id", "source_range", "interpretation", "owner_kind", "owner_ref", "payload", "decision_refs", "question_refs"])

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


class ImportApprovalTests(unittest.TestCase):
    def test_later_exact_approval_resumes_apply_without_rechecking(self):
        i, rt, bundle, request = checked_import()
        before = deepcopy(rt['intent_imports'][bundle['id']]['check'])
        i, rt, result = gov.apply_import_control(i, rt, request)
        self.assertEqual(gov.governance_view(i)['goal'], 'Prove Q')
        self.assertEqual(result['status'], 'applied')
        self.assertEqual(rt['intent_imports'][bundle['id']]['check'], before)
        self.assertNotIn('CHECK', rt['waiting_actions'])
        repeated_i, repeated_rt, repeated = gov.apply_import_control(i, rt, request)
        self.assertEqual((repeated_i, repeated_rt, repeated), (i, rt, result))

    def test_later_approval_rejects_changed_seal_and_changed_premise(self):
        i, rt, bundle, request = checked_import()
        wrong = deepcopy(request); wrong['config']['check_sha256'] = 'wrong'
        with self.assertRaises(ValueError): gov.apply_import_control(i, rt, wrong)
        i['decisions']['D']['source_sha256'] = '0' * 64
        with self.assertRaises(ValueError): gov.apply_import_control(i, rt, request)
        self.assertNotIn('LATER', i['governance_sources'])

    def test_import_application_receipt_binds_approval_and_rejects_tampering(self):
        i, rt, bundle, request = checked_import()
        i, rt, receipt = gov.apply_import_control(i, rt, request)
        self.assertEqual(receipt['approvals']['U']['source_ref'], 'LATER')
        self.assertEqual(receipt['check_sha256'], bundle['check']['sha256'])
        rt['intent_imports'][bundle['id']]['application']['applied_units'] = []
        with self.assertRaises(ValueError): gov.apply_import_control(i, rt, request)

    def test_changed_premise_reopens_checked_import_without_fabricated_text_change(self):
        i, rt, bundle, request = checked_import()
        output = deepcopy(bundle['output'])
        output['repair'] = {'previous_sha256': bundle['sha256'], 'changed_unit_ids': [],
                            'actions': ['Re-evaluate the changed governing premise']}
        with self.assertRaises(ValueError):
            gov.prepare_import(i, rt, bundle['source'], output, execution_id='NEW', input_ref="IN", previous_id=bundle['id'])
        i['decisions']['D']['source_sha256'] = '0' * 64
        reopened = gov.prepare_import(i, rt, bundle['source'], output, execution_id='NEW', input_ref="IN", previous_id=bundle['id'])
        self.assertEqual(reopened['status'], 'checking')
        self.assertNotEqual(reopened['basis_sha256'], bundle['basis_sha256'])
        self.assertEqual(rt['intent_imports'][bundle['id']]['check'], bundle['check'])
        self.assertNotIn('check', reopened)


class ExecutionLineageTests(unittest.TestCase):
    def test_one_lineage_walk_keeps_each_consumers_judgment(self):
        from do_math.governance import execution_lineage, validate_independent_execution
        from do_math.review_cycle import validate_review_independence
        runtime = {'executions': {
            'EX-author': {'id': 'EX-author'},
            'EX-context': {'id': 'EX-context', 'context_origin': ['EX-author']},
            'EX-check': {'id': 'EX-check', 'continuation_of': 'EX-context'},
            'EX-loop-a': {'id': 'EX-loop-a', 'continuation_of': 'EX-loop-b'},
            'EX-loop-b': {'id': 'EX-loop-b', 'continuation_of': 'EX-loop-a'},
            'EX-lost': {'id': 'EX-lost', 'continuation_of': 'EX-missing'},
            'EX-orphan': {'id': 'EX-orphan', 'context_origin': ['EX-missing']}}}
        self.assertEqual([identifier for identifier, _ in execution_lineage(runtime, 'EX-check')],
                         ['EX-check', 'EX-context', 'EX-author'])
        self.assertEqual(list(execution_lineage(runtime, 'EX-lost'))[-1], ('EX-missing', None))
        # Checker independence follows continuations only; a review also follows context origins.
        validate_independent_execution(runtime, 'EX-check', ['EX-author'])
        with self.assertRaisesRegex(ValueError, 'original author context'):
            validate_review_independence({'id': 'RC', 'proposal': {'producer_execution_ids': ['EX-author']}},
                                         runtime, 'EX-check', {})
        with self.assertRaisesRegex(ValueError, 'resumes an author lineage'):
            validate_independent_execution(runtime, 'EX-loop-a', ['EX-author'])
        with self.assertRaisesRegex(ValueError, 'continuation lineage does not resolve'):
            validate_independent_execution(runtime, 'EX-lost', ['EX-author'])
        with self.assertRaisesRegex(ValueError, 'review context lineage does not resolve'):
            validate_review_independence({'id': 'RC', 'proposal': {}}, runtime, 'EX-orphan', {})


class RegisteredOwnerTests(unittest.TestCase):
    """Governance changes applied through the owner registered for each record kind."""

    def test_configuration_adapter_uses_actual_config_validator(self):
        from do_math.configuration import DEFAULT_CONFIG
        handlers = gov.import_owner_handlers()
        def install(i, rt, unit, approval):
            i['config'] = {**i.get('config', {}), **unit['payload']['config']}; return i, rt
        gov.register_configuration_owner(handlers, apply=install)
        i, rt, source, output = governance_import()
        i['config'] = deepcopy(DEFAULT_CONFIG)
        output.update(questions=[], question_details=[], needs_clarification=False)
        output['import_units'][0].update(owner_kind='configuration', owner_ref='I', question_refs=[],
            payload={'kind': 'configuration', 'config': {'call_timeout_seconds': 0}})
        with self.assertRaises(ValueError): gov.prepare_import(i, rt, source, output, execution_id='E1', input_ref="IN", owner_handlers=handlers)

    def test_registered_owner_applies_existing_knowledge_consumer(self):
        from do_math.repository import new_id
        candidate = {'id': new_id('KN'), 'kind': 'observation', 'title': 'Observation', 'statement': 'P observed',
                     'explanation': 'Limited observation', 'summary': 'Not a proof', 'lean_code': ''}
        for owner in ('research_record', 'evidence'):
            with self.subTest(owner=owner):
                i, rt, bundle, request = checked_import(kind=owner, payload={'kind': owner, 'record': candidate})
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
        i, rt, bundle, request = checked_import(kind='configuration', handlers=handlers,
            payload={'kind': 'configuration', 'config': {'model': 'approved'}})
        changed, _, _ = gov.apply_import_control(i, rt, request, owner_handlers=handlers)
        self.assertEqual(changed['config']['model'], 'approved')
        i['config'] = {'model': 'changed during review'}
        with self.assertRaises(ValueError): gov.apply_import_control(i, rt, request, owner_handlers=handlers)


class IntentImportTests(unittest.TestCase):
    """The user's intent imported into governance: its input, owners, questions and grants."""

    def test_intent_input_exposes_actual_consumers_and_exact_source(self):
        from engine_fixtures import governance_host
        host, _, _ = governance_host()
        host.runtime['inputs'] = [{'id': 'UI-exact', 'text': 'e\u0301 has two code points', 'config': {}}]
        context = host._governance_context({'role': 'intent_interpretation', 'target': 'UI-exact'}, {})
        self.assertEqual(context['user_request']['text'], context['original_source']['text'])
        kinds = {row['owner_kind'] for row in context['import_consumers']}
        self.assertEqual(kinds, gov.GOVERNANCE_KINDS | {'grant', 'revoke', 'delegation', 'question_answer',
            'task_scope'} | set(host.governance_owner_handlers()))
        self.assertEqual(context['governance_records'], list(host.instance['governance'].values()))
        for row in context['import_consumers']:
            document = Path(__file__).resolve().parents[2] / row['payload_contract']['document']
            self.assertIn(row['owner_kind'], document.read_text(encoding='utf-8'))

    def test_initial_configuration_keeps_its_owner_through_completion(self):
        from record_fixtures import applied_initial_intent
        from do_math.initialization import initial_intent_evidence
        from do_math.configuration import DEFAULT_CONFIG
        instance, runtime, _ = applied_initial_intent('Use this exact configuration')
        instance['config'] = {**deepcopy(DEFAULT_CONFIG), 'scholarly_enabled': False}
        source = gov.import_input_source(instance, runtime, instance['lifecycle']['input_id'])
        def configure(i, r, unit, approval):
            changed = deepcopy(i)
            changed['config'].update(unit['payload']['config'])
            return changed, deepcopy(r)
        handlers = gov.register_configuration_owner(gov.import_owner_handlers(), apply=configure)
        payload = {'kind': 'configuration', 'config': {'effort': 'high'}}
        output = {'questions': [], 'question_details': [], 'needs_clarification': False,
            'import_units': [{'unit_id': 'U', 'source_range': {'start': 0, 'end': len(source['text'])},
                'interpretation': 'Use the approved effort', 'owner_kind': 'configuration',
                'owner_ref': instance['id'], 'payload': payload, 'decision_refs': [], 'question_refs': []}]}
        runtime['executions']['EX-config-author'] = {'id': 'EX-config-author', 'role': 'intent_interpretation'}
        bundle = gov.prepare_import(instance, runtime, source, output, execution_id='EX-config-author',
            input_ref=instance['lifecycle']['input_id'], owner_handlers=handlers)
        runtime['executions']['EX-config-check'] = {'id': 'EX-config-check', 'role': 'intent_interpretation',
            'intent_import_sha256': bundle['sha256']}
        bundle = gov.check_import(instance, runtime, bundle['id'], {'bundle_sha256': bundle['sha256'],
            'decision': 'approved', 'scope_complete': True, 'unit_ids': ['U'], 'question_ids': [], 'findings': []},
            execution_id='EX-config-check', owner_handlers=handlers)
        instance, runtime, _ = gov.apply_import_control(instance, runtime, {'id': 'APPROVAL-config',
            'action': 'decision', 'origin': 'user', 'text': 'Approve this exact effort', 'config': {
                'kind': 'import_approval', 'import_id': bundle['id'], 'bundle_sha256': bundle['sha256'],
                'check_sha256': bundle['check']['sha256'], 'unit_hashes': {'U': exact_content_hash(payload)}}},
            owner_handlers=handlers)
        self.assertEqual(instance['config']['effort'], 'high')
        receipt = initial_intent_evidence(instance, runtime, owner_handlers=handlers)
        self.assertEqual(receipt['interpretation_execution_id'], 'EX-config-author')

    def test_initial_advisory_question_does_not_become_a_blocking_gate(self):
        from record_fixtures import applied_initial_intent
        from do_math.initialization import initial_intent_evidence
        instance, runtime, original_id = applied_initial_intent('Prove the stated goal')
        original = runtime['intent_imports'][original_id]
        output = deepcopy(original['output'])
        uid = output['import_units'][0]['unit_id']
        output.update(questions=['Optional presentation preference?'], needs_clarification=True,
            question_details=[{'id': 'Q-advice', 'question_index': 0, 'target_ids': [instance['id']],
                'blocks': False, 'reason': 'Presentation preference is optional', 'source_unit_ids': [uid], 'options': []}])
        output['import_units'][0]['question_refs'] = ['Q-advice']
        runtime['executions']['EX-advice'] = {'role': 'intent_interpretation'}
        bundle = gov.prepare_import(instance, runtime, original['source'], output, execution_id='EX-advice',
            input_ref=instance['lifecycle']['input_id'])
        runtime['executions']['EX-advice-check'] = {'role': 'intent_interpretation', 'intent_import_sha256': bundle['sha256']}
        gov.check_import(instance, runtime, bundle['id'], {'decision': 'approved', 'scope_complete': True,
            'bundle_sha256': bundle['sha256'], 'unit_ids': [uid], 'question_ids': ['Q-advice'], 'findings': []},
            execution_id='EX-advice-check')
        instance, runtime, receipt = gov.apply_import(instance, runtime, bundle['id'])
        self.assertEqual(receipt['status'], 'applied')
        self.assertEqual(initial_intent_evidence(instance, runtime)['interpretation_execution_id'], 'EX-advice')
        self.assertEqual(runtime['question_links'][-1]['status'], 'open')

    def test_unrelated_progress_preserves_checked_import_but_relevant_changes_do_not(self):
        instance, runtime, bundle, request = checked_import()
        runtime['tasks']['TK-other'] = {'id': 'TK-other', 'revision': 2, 'status': 'active', 'question': 'Unrelated'}
        instance['decisions']['DC-other'] = {'id': 'DC-other', 'change': {'note': 'Unrelated'}}
        changed, _, receipt = gov.apply_import_control(instance, runtime, request)
        self.assertEqual(receipt['status'], 'applied')
        self.assertEqual(gov.governance_view(changed)['goal'], 'Prove Q')
        instance['decisions']['D']['source_sha256'] = '0' * 64
        with self.assertRaises(ValueError):
            gov.apply_import_control(instance, runtime, request)

    def test_initial_blocking_question_waits_and_answer_reopens_original_once(self):
        from datetime import datetime, timezone
        from unittest.mock import patch
        from engine_fixtures import governance_host
        from do_math.initialization_engine import InitializationEngineMixin
        host, _, _ = governance_host()
        text = 'Which domain?'
        source = gov.preserve_source('UNUSED', text, origin='user')
        host.instance['lifecycle'] = {'state': 'initializing', 'input_id': 'UI-original',
            'immutable_input': {k: source[k] for k in ('text', 'sha256', 'bytes')},
            'adoption': {'initial_profile_ref': {'id': 'P'}, 'initial_grant_ids': ['GR-initial']}}
        host.instance['grants']['GR-initial'] = {'roles': ['intent_interpretation']}
        host.runtime['inputs'] = [{'id': 'UI-original', 'text': text, 'config': {}}]
        host.runtime['queue'] = []
        host.runtime['waiting_actions'] = {}
        action = {'id': 'AC-interpret', 'role': 'intent_interpretation', 'target': 'UI-original', 'stage': 'interpret'}
        host.runtime['executions']['AUTHOR'] = {'id': 'AUTHOR', 'role': 'intent_interpretation', 'status': 'ended', 'action': action}
        output = {'questions': [text], 'needs_clarification': True, 'question_details': [{'id': 'Q-domain',
            'question_index': 0, 'target_ids': [host.instance['id']], 'blocks': True, 'reason': 'Domain is needed',
            'source_unit_ids': ['U'], 'options': []}], 'import_units': [{'unit_id': 'U',
            'source_range': {'start': 0, 'end': len(text)}, 'interpretation': 'Ask the domain',
            'owner_kind': 'charter', 'owner_ref': 'CH1', 'payload': {}, 'decision_refs': [], 'question_refs': ['Q-domain']}]}
        bundle = host._apply_governance_intent(action, output, 'AUTHOR')
        check = host.runtime['queue'].pop()
        host.runtime['executions']['CHECK'] = {'id': 'CHECK', 'role': 'intent_interpretation', 'status': 'ended',
            'intent_import_sha256': bundle['sha256'], 'action': check}
        host._apply_governance_intent(check, {'bundle_sha256': bundle['sha256'], 'decision': 'approved',
            'scope_complete': True, 'unit_ids': ['U'], 'question_ids': ['Q-domain'], 'findings': []}, 'CHECK')
        self.assertEqual(len(host.runtime['waiting_actions']), 1)
        host._capability_requirements = create_autospec(host._capability_requirements, return_value={'satisfied': True})
        host._lifecycle_now = create_autospec(host._lifecycle_now, side_effect=lambda: datetime.now(timezone.utc))
        with patch('do_math.initialization.grant_current', return_value=True):
            for _ in range(3):
                InitializationEngineMixin._queue_initial_intent(host)
        self.assertEqual(host.runtime['queue'], [])
        question = host.runtime['question_links'][-1]
        host.instance, host.runtime, _ = gov.apply_decision(host.instance, host.runtime,
            {'kind': 'question_answer', 'text': 'Natural numbers', 'target_ids': [host.instance['id']],
             'resolves_questions': [question['id']]}, source_ref='S')
        host._resume_import_question_waits()
        host._resume_import_question_waits()
        self.assertEqual(len(host.runtime['queue']), 1)
        self.assertEqual(host.runtime['queue'][0]['previous_import_id'], bundle['id'])
        self.assertEqual(host.runtime['queue'][0]['target'], 'UI-original')
        self.assertEqual(host.runtime['waiting_actions'], {})

    def test_question_references_are_stable_ids_at_both_boundaries(self):
        instance = domain_governance()
        source = gov.preserve_source('SOURCE', 'Which domain?', origin='user')
        output = {'questions': ['Which domain?'], 'needs_clarification': True,
            'question_details': [{'id': 'Q-domain', 'question_index': 0,
                'target_ids': [instance['id']], 'blocks': True, 'reason': 'Domain changes the goal',
                'source_unit_ids': ['U'], 'options': []}],
            'import_units': [{'unit_id': 'U', 'source_range': {'start': 0, 'end': len(source['text'])},
                'interpretation': 'The domain needs a user decision', 'owner_kind': 'charter',
                'owner_ref': 'CH1', 'payload': {}, 'decision_refs': [], 'question_refs': ['Q-domain']}]}
        gov.validate_import_units(instance, {}, source, output)
        # The producer runs the same check over its fixed input.
        context = {'user_request': {'text': source['text']}, 'original_source': source, 'instance_id': instance['id']}
        self.assertEqual(submission._intent_import_issues(output, context), [])
        output['import_units'][0]['question_refs'] = ['output/questions/0']
        self.assertTrue(submission._intent_import_issues(output, context))

    def test_interpretation_binds_referenced_source_alias(self):
        instance, runtime, source, output = governance_import()
        instance['sources'] = [{'id': 'SO-table', 'name': 'table.txt', 'path': 'sources/table.txt', 'sha256': 'a'*64}]
        output['used_sources'] = ['source:table.txt']
        bundle = gov.prepare_import(instance, runtime, source, output, execution_id='AUTHOR', input_ref='IN')
        instance['sources'][0]['sha256'] = 'b'*64
        with self.assertRaisesRegex(ValueError, 'targets changed'):
            gov.current_import(instance, runtime, bundle['id'])

    def test_documented_research_grant_permits_formal_check(self):
        path = Path(__file__).resolve().parents[2] / 'references' / '초기화-운전.md'
        blocks = path.read_text(encoding='utf-8').split('```json\n')[1:]
        grant = next(json.loads(block.split('```')[0])['grant'] for block in blocks
                     if '"id": "GR-research-01"' in block.split('```')[0])
        # The document's expiry is a placeholder the operator replaces with the approved period.
        self.assertTrue(grant['expires_at'].startswith('<'), grant['expires_at'])
        grant.update(status='active', expires_at='2026-09-23T00:00:00+00:00')
        self.assertTrue(gov.authorize({'grants': {grant['id']: grant}}, {'role': 'formal_check'},
            at='2026-09-22T00:00:00+00:00')['allowed'])


if __name__ == "__main__":
    unittest.main(verbosity=2)
