"""Intent imports (``governance``, layer 2): sealing, the independent check, approval, owners and currentness.

A user's input enters governance as an import: an author execution seals
meaning units covering the exact original (``prepare_import``), an independent
checker compares them (``check_import``) and application needs a current premise
and, for a unit that changes authority, the user's approval of that exact change
(``apply_import``, ``apply_import_control``). The records are ``record_fixtures``'
(``governance_import``, ``checked_import``, ``applied_initial_intent``), built by
these same product functions; each rejection is pinned to its reason.
"""
from copy import deepcopy
import unittest

import jsonschema

from do_math import governance as gov, questions, submission
from do_math.canonical import exact_content_hash
from do_math.governance import interpretation_schema
from record_fixtures import checked_import, domain_governance, governance_import
from research_fixtures import charter

CHECKED = {"decision": "approved", "scope_complete": True, "unit_ids": ["U"], "question_ids": ["Q"], "findings": []}


def approved_check(bundle, **changes):
    return {"bundle_sha256": bundle["sha256"], **CHECKED, **changes}


class ImportSealTests(unittest.TestCase):
    def test_import_holes_and_self_check_are_rejected_and_questions_still_checked(self):
        i, rt, s, output = governance_import()
        bad = deepcopy(output); bad["import_units"][0]["source_range"]["end"] = 7
        with self.assertRaisesRegex(ValueError, "^incomplete source coverage$"):
            gov.prepare_import(i, rt, s, bad, execution_id="E1", input_ref="IN")
        bundle = gov.prepare_import(i, rt, s, output, execution_id="E1", input_ref="IN")
        rt["executions"]["E2"] = {"role": "intent_interpretation", "intent_import_sha256": bundle["sha256"]}
        check = approved_check(bundle)
        with self.assertRaisesRegex(ValueError, "^independent checker execution required$"):
            gov.check_import(i, rt, bundle["id"], check, execution_id="E1")
        gov.check_import(i, rt, bundle["id"], check, execution_id="E2")
        updated, updated_rt, outcome = gov.apply_import(i, rt, bundle["id"])
        self.assertEqual(outcome["status"], "applied")
        self.assertEqual(questions.user_waits({"role": "research_preparation"}, updated, updated_rt), [])

    def test_import_reauthor_requires_current_failed_parent_and_repair_coordinates(self):
        i, rt, s, out = governance_import()
        b = gov.prepare_import(i, rt, s, out, execution_id="E1", input_ref="IN")
        rt["executions"]["E2"] = {"role": "intent_interpretation", "intent_import_sha256": b["sha256"]}
        gov.check_import(i, rt, b["id"], approved_check(b, decision="revision_required",
                                                         findings=["Question incomplete"]), execution_id="E2")
        with self.assertRaisesRegex(ValueError, "^rework requires parent findings and exact changed coordinates$"):
            gov.prepare_import(i, rt, s, out, execution_id="E3", input_ref="IN", previous_id=b["id"])
        # Before any rework the failed check alone keeps the parent from applying.
        with self.assertRaisesRegex(ValueError, "^independent complete approval required$"):
            gov.apply_import(i, rt, b["id"])
        out["repair"] = {"previous_sha256": b["sha256"], "changed_unit_ids": ["U"], "actions": ["Add scope option"]}
        out["question_details"][0]["options"].append({"text": "Change scope", "effect": "Ask for a replacement charter"})
        newer = gov.prepare_import(i, rt, s, out, execution_id="E3", input_ref="IN", previous_id=b["id"])
        self.assertEqual(newer["previous_id"], b["id"])
        with self.assertRaisesRegex(ValueError, "^import is absent or superseded$"):
            gov.apply_import(i, rt, b["id"])

    def test_import_currentness_binds_actual_structured_task_contract(self):
        i, rt, source, output = governance_import()
        rt['tasks']['T'] = {'id': 'T', 'revision': 1, 'status': 'planned', 'question': 'Original task'}
        output['used_sources'] = ['T']
        bundle = gov.prepare_import(i, rt, source, output, execution_id='AUTHOR', input_ref="IN")
        rt['executions']['CHECK'] = {'role': 'intent_interpretation', 'intent_import_sha256': bundle['sha256']}
        rt['tasks']['T']['question'] = 'A different task under the same nominal revision'
        with self.assertRaisesRegex(ValueError, "^import authority or affected targets changed$"):
            gov.check_import(i, rt, bundle['id'], approved_check(bundle), execution_id='CHECK')

    def test_unapproved_or_stale_import_cannot_change_charter(self):
        i, rt, s, output = governance_import()
        replacement = charter("CH2", "Prove Q"); replacement["supersedes"] = ["CH1"]
        output.update(questions=[], question_details=[])
        unit = output["import_units"][0]
        unit.update(owner_ref="CH2", question_refs=[], payload={"kind": "charter", "record": replacement})
        b = gov.prepare_import(i, rt, s, output, execution_id="E1", input_ref="IN")
        rt["executions"]["E2"] = {"role": "intent_interpretation", "intent_import_sha256": b["sha256"]}
        gov.check_import(i, rt, b["id"], approved_check(b, question_ids=[]), execution_id="E2")
        with self.assertRaisesRegex(ValueError, "^semantic check is not user approval of the exact change$"):
            gov.apply_import(i, rt, b["id"])
        approvals = {"U": {"actor": "user", "source_ref": s["id"], "source_sha256": s["sha256"],
                           "change_sha256": exact_content_hash(unit["payload"])}}
        changed, state, event = gov.apply_import(i, rt, b["id"], approvals=approvals)
        self.assertEqual(gov.governance_view(changed)["goal"], "Prove Q")
        self.assertEqual(event["status"], "applied")
        _, repeated_state, repeated_event = gov.apply_import(changed, state, b["id"], approvals=approvals)
        self.assertEqual(repeated_event, event)
        self.assertEqual(repeated_state, state)
        stale = deepcopy(i); stale["decisions"]["D"]["source_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "^import authority or affected targets changed$"):
            gov.apply_import(stale, rt, b["id"], approvals=approvals)

    def test_import_check_must_resolve_a_real_execution_and_bound_input(self):
        i, rt, s, output = governance_import()
        bundle = gov.prepare_import(i, rt, s, output, execution_id="E1", input_ref="IN")
        with self.assertRaisesRegex(ValueError, "^independent checker execution required$"):
            gov.check_import(i, rt, bundle["id"], approved_check(bundle), execution_id="FAKE")
        # A real execution that did not receive this sealed import is not its checker either.
        rt["executions"]["E9"] = {"role": "intent_interpretation"}
        with self.assertRaisesRegex(ValueError, "^checker execution must bind exact preserved import input$"):
            gov.check_import(i, rt, bundle["id"], approved_check(bundle), execution_id="E9")

    def test_import_reapplication_is_idempotent(self):
        i, rt, s, output = governance_import()
        b = gov.prepare_import(i, rt, s, output, execution_id="E1", input_ref="IN")
        rt["executions"]["E2"] = {"role": "intent_interpretation", "intent_import_sha256": b["sha256"]}
        gov.check_import(i, rt, b["id"], approved_check(b), execution_id="E2")
        i, rt, first = gov.apply_import(i, rt, b["id"])
        _, second, result = gov.apply_import(i, rt, b["id"])
        self.assertEqual(first, result)
        self.assertEqual(len(rt["question_links"]), len(second["question_links"]))

    def test_import_repair_cannot_claim_unchanged_units_were_changed(self):
        i, rt, s, out = governance_import(); b = gov.prepare_import(i, rt, s, out, execution_id="E1", input_ref="IN")
        rt["executions"]["E2"] = {"role": "intent_interpretation", "intent_import_sha256": b["sha256"]}
        gov.check_import(i, rt, b["id"], approved_check(b, decision="revision_required",
                                                         findings=["Correct interpretation"]), execution_id="E2")
        out["repair"] = {"previous_sha256": b["sha256"], "changed_unit_ids": ["U"], "actions": ["Claim repaired"]}
        with self.assertRaisesRegex(ValueError, "^repair coordinates do not match actual changed units$"):
            gov.prepare_import(i, rt, s, out, execution_id="E3", input_ref="IN", previous_id=b["id"])

    def test_resumed_author_session_is_not_an_independent_import_check(self):
        i, rt, s, out = governance_import(); b = gov.prepare_import(i, rt, s, out, execution_id="E1", input_ref="IN")
        rt["executions"]["E2"] = {"role": "intent_interpretation", "intent_import_sha256": b["sha256"], "continuation_of": "E1"}
        with self.assertRaisesRegex(ValueError, "^checker resumes an author lineage$"):
            gov.check_import(i, rt, b["id"], approved_check(b), execution_id="E2")

    def test_intent_schema_covers_the_actual_check_and_repair_contract(self):
        i, rt, s, out = governance_import()
        out.update(summary="question", used_sources=["S"])
        jsonschema.validate(out, gov.interpretation_schema("interpret"))
        check = {"summary": "checked", "used_sources": ["S"], "questions": [], "bundle_sha256": "a" * 64,
                 "decision": "approved", "scope_complete": True, "unit_ids": ["U"], "question_ids": ["Q"], "findings": []}
        jsonschema.validate(check, gov.interpretation_schema("check"))
        with self.assertRaises(jsonschema.ValidationError) as caught:
            jsonschema.validate({**check, "decision": "match"}, gov.interpretation_schema("check"))
        self.assertEqual((list(caught.exception.absolute_path), caught.exception.validator), (["decision"], "enum"))

    def test_question_coordinates_must_reciprocate_unit_question_references(self):
        i, rt, s, out = governance_import()
        other = deepcopy(out["import_units"][0]); other.update(unit_id="V", source_range={"start": 4, "end": 8}, question_refs=[])
        out["import_units"][0]["source_range"]["end"] = 4; out["import_units"].append(other)
        out["question_details"][0]["source_unit_ids"] = ["V"]
        with self.assertRaisesRegex(ValueError, "^question coordinates contradict unit ownership$"):
            gov.prepare_import(i, rt, s, out, execution_id="E1", input_ref="IN")

    def test_advisory_question_does_not_leave_import_waiting_for_a_decision(self):
        i, rt, s, out = governance_import(); b = gov.prepare_import(i, rt, s, out, execution_id="E1", input_ref="IN")
        rt["executions"]["E2"] = {"role": "intent_interpretation", "intent_import_sha256": b["sha256"]}
        gov.check_import(i, rt, b["id"], approved_check(b), execution_id="E2")
        _, state, result = gov.apply_import(i, rt, b["id"])
        self.assertEqual(result["status"], "applied")
        self.assertEqual(state["question_links"][0]["status"], "open")
        i, rt, s, out = governance_import(); out["question_details"][0]["blocks"] = True
        b = gov.prepare_import(i, rt, s, out, execution_id="E1", input_ref="IN")
        rt["executions"]["E2"] = {"role": "intent_interpretation", "intent_import_sha256": b["sha256"]}
        gov.check_import(i, rt, b["id"], approved_check(b), execution_id="E2")
        _, state, result = gov.apply_import(i, rt, b["id"])
        self.assertEqual(result["status"], "awaiting_decision")
        waits = questions.user_waits({"role": "research_preparation"}, i, state)
        self.assertEqual([row["question_id"] for row in waits], [state["question_links"][0]["id"]])

    def test_import_unit_target_matches_each_governance_consumer(self):
        source = gov.preserve_source('GS-target', 'Use the named target.', origin='user')
        cases = [
            ('grant', 'GR-one', {'kind': 'grant', 'grant': {'id': 'GR-one'}}),
            ('delegation', 'DG-one', {'kind': 'delegation', 'delegation': {'id': 'DG-one'}}),
            ('revoke', 'GR-one', {'kind': 'revoke', 'grant_id': 'GR-one'}),
            ('task_scope', 'TK-one', {'kind': 'task_scope', 'task_id': 'TK-one'}),
            ('question_answer', 'QU-one', {'kind': 'question_answer', 'resolves_questions': ['QU-one', 'QU-two']}),
        ]
        for kind, target, payload in cases:
            with self.subTest(kind=kind):
                output = {'questions': [], 'question_details': [],
                    'import_units': [{'unit_id': 'U', 'source_range': {'start': 0, 'end': len(source['text'])},
                        'interpretation': 'Use the named target.', 'owner_kind': kind, 'owner_ref': target,
                        'payload': deepcopy(payload), 'decision_refs': [], 'question_refs': []}]}
                self.assertIsNone(gov.validate_import_units({'id': 'RI-test'}, {}, source, output))
                output['import_units'][0]['owner_ref'] = 'different-target'
                with self.assertRaisesRegex(ValueError, '^payload target differs from owner coordinate$'):
                    gov.validate_import_units({'id': 'RI-test'}, {}, source, output)
                output['import_units'][0]['payload'] = {}
                self.assertIsNone(gov.validate_import_units({'id': 'RI-test'}, {}, source, output))
        # A question answer's owner is any question it resolves, not only the first.
        output['import_units'][0].update(owner_ref='QU-two', payload=deepcopy(cases[-1][2]))
        self.assertIsNone(gov.validate_import_units({'id': 'RI-test'}, {}, source, output))

    def test_import_basis_tracks_replaced_grant_but_not_unrelated_grants(self):
        instance = {'id': 'RI-test', 'governance': {}, 'grants': {
            'GR-old': {'id': 'GR-old', 'kind': 'local', 'status': 'active', 'roles': ['maintenance']},
            'GR-other': {'id': 'GR-other', 'kind': 'local', 'status': 'active', 'roles': ['maintenance']}}}
        output = {'import_units': [{'owner_ref': 'GR-new', 'payload': {
            'kind': 'grant', 'grant': {'id': 'GR-new'}, 'replaces': ['GR-old']}}]}
        original = gov._import_basis(instance, {}, output)
        unrelated = deepcopy(instance)
        unrelated['grants']['GR-other']['roles'].append('research_work')
        self.assertEqual(gov._import_basis(unrelated, {}, output), original)
        changed = deepcopy(instance)
        changed['grants']['GR-old']['roles'].append('research_work')
        self.assertNotEqual(gov._import_basis(changed, {}, output), original)

    def test_original_literal_changes_are_not_equal_approval_hashes(self):
        self.assertNotEqual(exact_content_hash({'statement': 'e\u0301 has two codepoints'}),
                            exact_content_hash({'statement': '\u00e9 has two codepoints'}))

    def test_import_schema_requires_coordinate_covered_meaning_units(self):
        schema = interpretation_schema("interpret")
        self.assertIn("import_units", schema["properties"])
        unit = schema["properties"]["import_units"]["items"]["required"]
        self.assertEqual(unit, ["unit_id", "source_range", "interpretation", "owner_kind", "owner_ref", "payload",
                                "decision_refs", "question_refs"])


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
        with self.assertRaisesRegex(ValueError, '^approval does not name the exact sealed interpretation and check$'):
            gov.apply_import_control(i, rt, wrong)
        i['decisions']['D']['source_sha256'] = '0' * 64
        with self.assertRaisesRegex(ValueError, '^import authority or affected targets changed$'):
            gov.apply_import_control(i, rt, request)
        self.assertNotIn('LATER', i['governance_sources'])

    def test_import_application_receipt_binds_approval_and_rejects_tampering(self):
        i, rt, bundle, request = checked_import()
        i, rt, receipt = gov.apply_import_control(i, rt, request)
        self.assertEqual(receipt['approvals']['U']['source_ref'], 'LATER')
        self.assertEqual(receipt['check_sha256'], bundle['check']['sha256'])
        rt['intent_imports'][bundle['id']]['application']['applied_units'] = []
        with self.assertRaisesRegex(ValueError, '^sealed import application receipt changed$'):
            gov.apply_import_control(i, rt, request)

    def test_changed_premise_reopens_checked_import_without_fabricated_text_change(self):
        i, rt, bundle, request = checked_import()
        output = deepcopy(bundle['output'])
        output['repair'] = {'previous_sha256': bundle['sha256'], 'changed_unit_ids': [],
                            'actions': ['Re-evaluate the changed governing premise']}
        with self.assertRaisesRegex(ValueError, '^unchanged import resumes application; it does not need a new check$'):
            gov.prepare_import(i, rt, bundle['source'], output, execution_id='NEW', input_ref="IN", previous_id=bundle['id'])
        i['decisions']['D']['source_sha256'] = '0' * 64
        reopened = gov.prepare_import(i, rt, bundle['source'], output, execution_id='NEW', input_ref="IN", previous_id=bundle['id'])
        self.assertEqual(reopened['status'], 'checking')
        self.assertNotEqual(reopened['basis_sha256'], bundle['basis_sha256'])
        self.assertEqual(rt['intent_imports'][bundle['id']]['check'], bundle['check'])
        self.assertNotIn('check', reopened)

    def test_exact_draft_reaches_existing_consumer_without_mutating_source_state(self):
        instance, runtime, bundle, request = checked_import()
        before = deepcopy((instance, runtime))
        draft = gov.import_approval_draft(instance, runtime, bundle['id'])
        self.assertEqual(draft, request['config'])
        self.assertEqual((instance, runtime), before)
        updated, state, receipt = gov.apply_import_control(instance, runtime, {**request, 'config': draft})
        self.assertEqual(receipt['status'], 'applied')
        broken = deepcopy(runtime)
        broken['intent_imports'][bundle['id']]['check']['scope_complete'] = False
        with self.assertRaisesRegex(ValueError, '^approval draft requires a complete independently checked import$'):
            gov.import_approval_draft(instance, broken, bundle['id'])



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
        self.assertIsNone(validate_independent_execution(runtime, 'EX-check', ['EX-author']))
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
        installed = []

        def install(i, rt, unit, approval):
            installed.append(unit['unit_id'])
            i['config'] = {**i.get('config', {}), **unit['payload']['config']}; return i, rt
        gov.register_configuration_owner(handlers, apply=install)
        i, rt, source, output = governance_import()
        i['config'] = deepcopy(DEFAULT_CONFIG)
        output.update(questions=[], question_details=[])
        output['import_units'][0].update(owner_kind='configuration', owner_ref='I', question_refs=[],
            payload={'kind': 'configuration', 'config': {'call_timeout_seconds': 0}})
        with self.assertRaisesRegex(ValueError, '^config/call_timeout_seconds: 0 is less than the minimum of 1$'):
            gov.prepare_import(i, rt, source, output, execution_id='E1', input_ref="IN", owner_handlers=handlers)
        self.assertEqual(installed, [])

    def test_registered_owner_applies_existing_knowledge_consumer(self):
        from support.fakes.clock import FakeClock
        candidate = {'id': FakeClock().new_id('KN'), 'kind': 'observation', 'title': 'Observation', 'statement': 'P observed',
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
        with self.assertRaisesRegex(ValueError, '^import domain premises changed$'):
            gov.apply_import_control(i, rt, request, owner_handlers=handlers)


class IntentImportTests(unittest.TestCase):
    """The user's intent imported into governance: its input, owners, questions and grants."""

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
        output = {'questions': [], 'question_details': [],
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
        output.update(questions=['Optional presentation preference?'],
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
        with self.assertRaisesRegex(ValueError, '^import authority or affected targets changed$'):
            gov.apply_import_control(instance, runtime, request)

    def test_question_references_are_stable_ids_at_both_boundaries(self):
        instance = domain_governance()
        source = gov.preserve_source('SOURCE', 'Which domain?', origin='user')
        output = {'questions': ['Which domain?'],
            'question_details': [{'id': 'Q-domain', 'question_index': 0,
                'target_ids': [instance['id']], 'blocks': True, 'reason': 'Domain changes the goal',
                'source_unit_ids': ['U'], 'options': []}],
            'import_units': [{'unit_id': 'U', 'source_range': {'start': 0, 'end': len(source['text'])},
                'interpretation': 'The domain needs a user decision', 'owner_kind': 'charter',
                'owner_ref': 'CH1', 'payload': {}, 'decision_refs': [], 'question_refs': ['Q-domain']}]}
        self.assertIsNone(gov.validate_import_units(instance, {}, source, output))
        # The producer runs the same check over its fixed input.
        context = {'user_request': {'text': source['text']}, 'original_source': source, 'instance_id': instance['id']}
        self.assertEqual(submission._intent_import_issues(output, context), [])
        output['import_units'][0]['question_refs'] = ['output/questions/0']
        self.assertEqual([{key: row[key] for key in ('rule_id', 'path', 'message')}
                          for row in submission._intent_import_issues(output, context)],
                         [{'rule_id': 'intent.import_units', 'path': 'output/import_units',
                           'message': 'unit question does not resolve'}])

    def test_interpretation_binds_referenced_source_alias(self):
        instance, runtime, source, output = governance_import()
        instance['sources'] = [{'id': 'SO-table', 'name': 'table.txt', 'path': 'sources/table.txt', 'sha256': 'a' * 64}]
        output['used_sources'] = ['source:table.txt']
        bundle = gov.prepare_import(instance, runtime, source, output, execution_id='AUTHOR', input_ref='IN')
        self.assertEqual(gov.current_import(instance, runtime, bundle['id'])['id'], bundle['id'])
        instance['sources'][0]['sha256'] = 'b' * 64
        with self.assertRaisesRegex(ValueError, '^import authority or affected targets changed$'):
            gov.current_import(instance, runtime, bundle['id'])



if __name__ == "__main__":
    unittest.main()
