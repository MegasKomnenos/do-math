"""Task contracts: obligations and dispositions, derived readiness, dependencies, assessments and repetition lineages."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from do_math import contracts, governance as gov, submission, task_contracts
from do_math import planning
from copy import deepcopy
from unittest.mock import create_autospec

from research_fixtures import bare_engine, candidate, git_init, review_items
from record_fixtures import (apply_assessment, approve_task, approved_task, domain_governance, task_contract,
                             task_disposition, transfer_assessment)
from record_fixtures import specialist_assessment


class TaskContractReviewTests(unittest.TestCase):
    def test_wire_profile_reference_remains_identical_in_stored_contract(self):
        from do_math import contracts
        from do_math.execution_profiles import profile_ref
        from jsonschema import Draft202012Validator
        from research_fixtures import candidate
        _, instance, _ = approved_task()
        wire = candidate()
        wire['profile_refs'] = [profile_ref(next(iter(instance['execution_profiles'].values())))]
        Draft202012Validator(contracts.TASK_CANDIDATE).validate(wire)
        # Allocation belongs to the engine, not the wire producer.
        stored = {k: deepcopy(v) for k, v in wire.items() if k != 'revises_task_id'}
        stored.update(id='TK-wire', revision=1)
        task_contracts.validate_task_contract(stored)
        self.assertEqual(stored['profile_refs'], wire['profile_refs'])
        for illegal in ({**wire, 'id':'TK-wire'}, {**wire, 'revision':1}):
            self.assertTrue(list(Draft202012Validator(contracts.TASK_CANDIDATE).iter_errors(illegal)))
        with self.assertRaises(ValueError):
            task_contracts.validate_task_contract(wire)

    def test_raw_governance_review_is_current_in_raw_and_projected_consumers(self):
        from do_math.governance import governance_view
        value, instance, runtime = approved_task()
        approve_task(value, instance, runtime)
        review = value['reviews'][-1]
        expected = governance_view(instance)
        self.assertEqual(review['goal_revision'], expected['goal_revision'])
        self.assertEqual(review['policy_revision'], expected['policy_revision'])
        for view in (instance, {**instance, **expected}):
            self.assertTrue(planning.contract_review_current(review, value, view, runtime)['valid'])
            self.assertEqual(planning.task_ready(value, view, runtime)['state'], 'ready')
        self.assertNotIn('goal_revision', instance)

    def test_transfer_cannot_complete_original_obligations(self):
        instance, runtime, assessment = transfer_assessment()
        assessment['decision'] = 'completed'
        before = deepcopy((instance, runtime))
        with self.assertRaisesRegex(ValueError, 'completed.*transferred'):
            apply_assessment(instance, runtime, assessment)
        self.assertEqual((instance, runtime), before)
        with self.assertRaisesRegex(ValueError, 'completed.*transferred'):
            planning.validate_plan_submission({'dispositions':[], 'task_assessments':[assessment]}, runtime['tasks'], [])

    def test_review_ignores_flat_projection_and_rejects_real_governance_changes(self):
        from do_math import governance
        value, instance, runtime = approved_task()
        review = deepcopy(value['reviews'][-1])
        stale_projection = {**instance, 'goal_revision':999, 'policy_revision':'fake'}
        self.assertTrue(planning.contract_review_current(review, value, stale_projection, runtime)['valid'])
        before = planning.review_basis_key(value, instance, runtime)
        policy = {'id':'POL-new', 'kind':'policy', 'revision':1, 'supersedes':[],
            'content':{'rule_id':'rule-new', 'scope':['P'], 'text':'Require an explicit domain', 'reason_refs':['D'], 'audit_refs':[]}}
        updated, runtime, _ = governance.apply_decision(instance, runtime,
            {'kind':'policy', 'record':policy}, source_ref='S')
        self.assertFalse(planning.contract_review_current(review, value, updated, runtime)['valid'])
        self.assertNotEqual(planning.review_basis_key(value, updated, runtime), before)

    def test_actual_charter_replacement_invalidates_review_without_top_level_fields(self):
        from do_math import governance
        from research_fixtures import charter
        value, instance, runtime = approved_task()
        review = deepcopy(value['reviews'][-1])
        replacement = charter('CH2', 'Prove the stronger Q')
        replacement.update(revision=2, supersedes=['CH1'])
        updated, runtime, _ = governance.apply_decision(instance, runtime,
            {'kind':'charter', 'record':replacement}, source_ref='S')
        self.assertNotIn('goal_revision', updated)
        self.assertFalse(planning.contract_review_current(review, value, updated, runtime)['valid'])
        self.assertEqual(planning.task_ready(value, updated, runtime)['state'], 'not_ready')

    def test_closed_transfer_never_satisfies_a_completion_dependency(self):
        instance, runtime, assessment = transfer_assessment()
        instance, runtime = apply_assessment(instance, runtime, assessment)
        source = runtime['tasks']['TK-1']
        consumer = deepcopy(runtime['tasks']['TK-2'])
        consumer.update(id='TK-consumer', dependencies=[source['id']], results=[], reviews=[])
        runtime['tasks'][consumer['id']] = consumer
        instance['grants']['GR-1']['task_ids'].append(consumer['id'])
        approve_task(consumer, instance, runtime)
        state = planning.task_ready(consumer, instance, runtime)
        self.assertEqual(state['state'], 'not_ready')
        self.assertIn('blocked dependencies', state['errors'][0])

    def test_terminal_disposition_consistency_is_checked_by_shared_validator(self):
        from do_math.task_scope import assessment_current
        instance, runtime, assessment = transfer_assessment()
        task = runtime['tasks']['TK-1']
        opened = deepcopy(assessment)
        opened['item_dispositions'][0]['kind'] = 'open'
        with self.assertRaisesRegex(ValueError, 'open obligations'):
            task_contracts.validate_item_dispositions(task, opened)
        _, runtime = apply_assessment(instance, runtime, assessment)
        runtime['tasks']['TK-1']['status'] = 'completed'
        self.assertFalse(assessment_current(runtime['tasks']['TK-1'], instance, runtime))

    def test_profile_ref_shape_and_exact_resolution_are_both_required(self):
        value, instance, runtime = approved_task()
        for replacement in (value['profile_refs'][0]['id'],
                {**value['profile_refs'][0], 'revision':True},
                {**value['profile_refs'][0], 'sha256':'invalid'}):
            bad = deepcopy(value); bad['profile_refs'] = [replacement]
            with self.assertRaises(ValueError): task_contracts.validate_task_contract(bad)
        bad = deepcopy(value); bad['profile_refs'] *= 2
        with self.assertRaises(ValueError): task_contracts.validate_task_contract(bad)
        for field, invalid in (('revision', 2), ('sha256', 'b'*64)):
            stale = deepcopy(value); stale['profile_refs'][0][field] = invalid
            runtime['tasks'][stale['id']] = stale
            approve_task(stale, instance, runtime)
            self.assertEqual(planning.task_ready(stale, instance, runtime)['state'], 'not_ready')

    def test_repetition_basis_changes_with_actual_policy_not_flat_projection(self):
        from do_math import governance, revisions
        _, instance, runtime = approved_task()
        action = {'role':'research_preparation'}
        revisions.bind_repetition_bases(instance, runtime, action)
        policy = {'id':'POL-new', 'kind':'policy', 'revision':1, 'supersedes':[],
            'content':{'rule_id':'new', 'scope':['P'], 'text':'A new requirement', 'reason_refs':['D'], 'audit_refs':[]}}
        changed, runtime, _ = governance.apply_decision(instance, runtime, {'kind':'policy', 'record':policy}, source_ref='S')
        next_action = {'role':'research_preparation'}
        revisions.bind_repetition_bases(changed, runtime, next_action)
        self.assertNotEqual(action['repetition_bases'], next_action['repetition_bases'])

    def test_common_reference_closure_does_not_split_grant_reuse_string(self):
        value, instance, runtime = approved_task()
        basis = planning.capture_task_basis(value, instance, runtime)
        self.assertNotIn('r', basis['common'])
        self.assertIn(value['profile_refs'][0]['id'], planning.action_read_ids({'target':value['id']}, instance, runtime))


class TaskContractStorageTests(unittest.TestCase):
    """Real installed schemas and Git; synthetic user decisions and AI judgments."""
    def setUp(self):
        import tempfile
        from do_math.repository import ResearchRepository
        from do_math.configuration import DEFAULT_CONFIG
        from do_math.execution_profiles import build_profiles
        self.temporary = tempfile.TemporaryDirectory(prefix='tasks-audit1-')
        self.addCleanup(self.temporary.cleanup)
        root = Path(self.temporary.name)
        git_init(root)
        from research_fixtures import current_state
        self.store = ResearchRepository(root, 'RI-01ARZ3NDEKTSV4RRFFQ69G5FAV')
        # Stored states pass the current lifecycle gate; these tasks belong to an active instance.
        self.instance, self.runtime = current_state(
            {**domain_governance(), 'config':deepcopy(DEFAULT_CONFIG), **build_profiles(DEFAULT_CONFIG)},
            {'status':'ready', 'tasks':{}, 'executions':{}, 'queue':[], 'history':[]})
        self.instance['lifecycle']['state'] = 'active'

    def execution(self, identifier, role):
        from do_math.activities import open_activity, assign_execution
        from do_math.execution_lifecycle import create_execution, transition_execution
        from do_math.execution_profiles import profile_ref
        profile = next(p for p in self.instance['execution_profiles'].values() if p['role']==role)
        activity_id = 'AT-' + identifier
        when = '2026-09-20T00:00:00Z'
        open_activity(self.runtime, activity_id=activity_id, activity_kind=role, owner_ref='engine', input_refs=[], opened_at=when)
        execution = create_execution(execution_id=identifier, owner_activity_id=activity_id,
            actor_kind=profile['actor_kind'], input_manifest={}, profile_ref=profile_ref(profile), created_at=when)
        execution['role'] = role
        assign_execution(self.runtime, activity_id, execution)
        transition_execution(execution, 'starting', at=when)
        transition_execution(execution, 'running', at=when)
        return execution

    def candidate(self, identifier):
        from do_math.contracts import task_candidate_record
        from do_math.execution_profiles import profile_ref
        from research_fixtures import candidate
        wire = candidate()
        profile = next(p for p in self.instance['execution_profiles'].values()
                       if p['role']=='research_work' and p['ai']['tier']=='high')
        wire['profile_refs'] = [profile_ref(profile)]
        wire['authority_refs'] = ['GR-audit']
        task = task_candidate_record(wire, task_id=identifier)
        task.pop('revises_task_id')  # Transport target, not stored contract authority.
        task.update(status='planned', results=[], reviews=[])
        self.runtime['tasks'][identifier] = task
        return task, wire

    def grant(self):
        from do_math.governance import apply_decision
        self.instance, self.runtime, _ = apply_decision(self.instance, self.runtime,
            {'kind':'grant', 'grant':{'id':'GR-audit','kind':'local','roles':['research_work'], 'reuse':'reusable'}}, source_ref='S')

    def review(self, identifier):
        eid = 'EX-review-' + identifier
        self.execution(eid, 'task_contract_review')
        task = self.runtime['tasks'][identifier]
        output = review_items(['S'])
        task['reviews'] = [planning.seal_contract_review(task, output, self.instance, self.runtime, execution_id=eid)]

    def test_candidate_review_profile_selection_and_governance_survive_git_reload(self):
        from do_math import governance
        from do_math.execution_profiles import resolve_profile, select_profile, profile_ref
        self.grant()
        task, wire = self.candidate('TK-stored')
        self.review(task['id'])
        head = self.store.initialize(self.instance, self.runtime)
        _, instance, runtime = self.store.load(head)
        saved = runtime['tasks'][task['id']]
        self.assertEqual(saved['profile_refs'], wire['profile_refs'])
        self.assertNotIn('goal_revision', instance)
        self.assertNotIn('policy_revision', instance)
        self.assertEqual(saved['reviews'][0]['goal_revision'], governance.governance_view(instance)['goal_revision'])
        self.assertEqual(saved['reviews'][0]['policy_revision'], governance.governance_view(instance)['policy_revision'])
        selected = resolve_profile(instance['execution_profiles'], saved['profile_refs'][0])
        action = {'id':'AC-dispatch','role':'research_work','target':saved['id'], 'profile_ref':profile_ref(selected)}
        self.assertEqual(select_profile(instance['execution_profiles'], action, selected['ai'], saved['profile_refs'])['id'], selected['id'])
        self.assertEqual(planning.task_ready(saved, instance, runtime, action=action, include_scheduling_waits=False)['state'], 'ready')
        bad = deepcopy(runtime)
        bad['tasks'][saved['id']]['profile_refs'][0]['revision'] += 1
        with self.assertRaises(ValueError):
            self.store.save_with_state(head, instance, bad)[0]
        self.assertEqual(self.store.load()[0], head)
        # Receipt currentness reads the same persisted governance as review/dispatch.
        from do_math.input_basis import CurrentnessChanged
        receiver = bare_engine(instance, runtime, store=self.store)
        receipt = {'input_snapshot':head, 'contract_sha256':planning.contract_hash(saved),
                   **planning.governance_revisions(instance)}
        review_action = {'role':'task_contract_review', 'target':saved['id']}
        output = {'item_reviews':deepcopy(saved['reviews'][0]['item_reviews'])}
        receiver._validate_decision_acceptance(review_action, output, receipt, {})
        policy = {'id':'POL-persisted', 'kind':'policy', 'revision':1, 'supersedes':[],
            'content':{'rule_id':'persisted', 'scope':['P'], 'text':'Require an explicit domain', 'reason_refs':['D'], 'audit_refs':[]}}
        receiver.instance, receiver.runtime, _ = governance.apply_decision(instance, runtime,
            {'kind':'policy', 'record':policy}, source_ref='S')
        changed_head = self.store.save_with_state(head, receiver.instance, receiver.runtime)[0]
        _, receiver.instance, receiver.runtime = self.store.load(changed_head)
        with self.assertRaises(CurrentnessChanged):
            receiver._validate_decision_acceptance(review_action, output, receipt, {})
        self.assertFalse(planning.contract_review_current(saved['reviews'][0], saved, receiver.instance, receiver.runtime)['valid'])

    def test_transfer_closes_without_completion_and_recipient_obligation_survives_reload(self):
        from do_math import governance, task_scope
        self.grant()
        source, _ = self.candidate('TK-source')
        target, _ = self.candidate('TK-target')
        self.execution('EX-plan', 'research_plan')
        source.update(status='waiting', results=[{'id':'EV-work', 'report':'remaining work identified'}])
        self.instance, self.runtime, decision = governance.apply_decision(self.instance, self.runtime,
            {'kind':'task_scope', 'task_id':source['id'], 'revision':source['revision'],
             'contract_sha256':planning.contract_hash(source), 'disposition':'transfer', 'reason':'move the exact remaining obligation',
             'obligation_ids':[source['completion_obligations'][0]['id']], 'target_task_id':target['id']}, source_ref='S')
        head = self.store.initialize(self.instance, self.runtime)
        _, instance, runtime = self.store.load(head)
        assessment = {'task_id':source['id'], 'decision':'closed', 'reason':'authorized transfer, not fulfillment',
            'item_dispositions':[{'obligation_id':source['completion_obligations'][0]['id'], 'kind':'transferred',
                'authority_ref':decision['id'], 'target_task_id':target['id'], 'target_obligation_id':'OB-inherited', 'evidence_refs':[]}], 'unresolved':[]}
        instance, runtime = task_scope.apply_task_assessments(instance, runtime, [assessment], execution_id='EX-plan', input_tasks=deepcopy(runtime['tasks']))
        saved_head = self.store.save_with_state(head, instance, runtime)[0]
        _, instance, runtime = self.store.load(saved_head)
        original, recipient = runtime['tasks'][source['id']], runtime['tasks'][target['id']]
        self.assertEqual(original['status'], 'closed')
        self.assertEqual(recipient['revision'], 2)
        self.assertTrue(task_scope.assessment_current(original, instance, runtime))
        self.assertEqual(recipient['completion_obligations'][-1]['id'], 'OB-inherited')
        # Neither persisted state nor the completion consumer may relabel transfer as fulfillment.
        bad = deepcopy(runtime)
        bad['tasks'][source['id']]['status'] = 'completed'
        bad['tasks'][source['id']]['assessment']['decision'] = 'completed'
        with self.assertRaisesRegex(ValueError, 'completed.*transferred'):
            self.store.save_with_state(saved_head, instance, bad)[0]
        self.assertFalse(task_scope.assessment_current(bad['tasks'][source['id']], instance, bad))
        self.assertEqual(self.store.load()[0], saved_head)
        omitted = {'task_id':target['id'], 'decision':'completed', 'item_dispositions':[
            {'obligation_id':recipient['completion_obligations'][0]['id'], 'kind':'fulfilled', 'evidence_refs':[]}], 'unresolved':[]}
        with self.assertRaisesRegex(ValueError, 'every obligation'):
            task_contracts.validate_item_dispositions(recipient, omitted, require_complete=True)

    def test_actual_engine_candidate_and_review_receiver_round_trip(self):
        from do_math.contracts import TASK_CANDIDATE
        from do_math.execution_profiles import profile_ref
        from jsonschema import Draft202012Validator
        from research_fixtures import candidate
        self.grant()
        self.instance.update(knowledge={}, sources=[])
        self.runtime.update(cycles=0, waiting_actions={})
        self.execution('EX-author', 'research_preparation')
        self.execution('EX-review', 'task_contract_review')
        engine = bare_engine(self.instance, self.runtime, store=self.store)
        engine.head = self.store.initialize(engine.instance, engine.runtime)
        wire = candidate()
        profile = next(p for p in self.instance['execution_profiles'].values()
                       if p['role']=='research_work' and p['ai']['tier']=='high')
        wire['profile_refs'] = [profile_ref(profile)]
        wire['authority_refs'] = ['GR-audit']
        Draft202012Validator(TASK_CANDIDATE).validate(wire)
        # No ID/revision or approval basis is patched into this actual receiver input.
        # The author's issued input fixes which task inputs it could name.
        from unittest.mock import create_autospec
        engine._issued_input = create_autospec(engine._issued_input, return_value=(
            {'available_input_refs': [], 'supplied_record_ids': []}, None))
        engine._apply({'role':'research_preparation'}, {'candidates':[wire]}, 'EX-author', owns_response=False)
        task = next(iter(engine.runtime['tasks'].values()))
        self.assertEqual(task['revision'], 1)
        self.assertEqual(task['profile_refs'], wire['profile_refs'])
        output = review_items(['S'])
        engine._apply({'role':'task_contract_review', 'target':task['id']}, output, 'EX-review', owns_response=False)
        saved_head = self.store.save_with_state(engine.head, engine.instance, engine.runtime)[0]
        _, instance, runtime = self.store.load(saved_head)
        task = runtime['tasks'][task['id']]
        self.assertTrue(planning.contract_review_current(task['reviews'][-1], task, instance, runtime)['valid'])
        self.assertEqual(planning.task_ready(task, instance, runtime)['state'], 'ready')


class TransferredContractRevisionTests(unittest.TestCase):
    def test_replacement_preserves_inherited_obligation_and_machine_provenance(self):
        from do_math.contracts import task_candidate_record
        from do_math.task_scope import validate_withdrawal_scope
        from research_fixtures import candidate
        instance, runtime, assessment = transfer_assessment()
        instance, runtime = apply_assessment(instance, runtime, assessment)
        recipient = runtime['tasks']['TK-2']
        proposal = candidate('Revised recipient', revises=recipient['id'])
        proposal['completion_obligations'] = deepcopy(recipient['completion_obligations'])
        proposal['completion_obligations'][0]['claim'] = 'Refine the independently authored obligation'
        revised = task_candidate_record(proposal, task_id=recipient['id'], previous=recipient)
        self.assertEqual(revised['transferred_obligations'], recipient['transferred_obligations'])
        self.assertIsNot(revised['transferred_obligations'], recipient['transferred_obligations'])
        self.assertEqual(revised['completion_obligations'][-1], recipient['completion_obligations'][-1])
        with self.assertRaisesRegex(ValueError, 'protected obligations'):
            validate_withdrawal_scope({**revised, 'status': 'planned'}, revised)
        for field in ('remove', 'id', 'claim', 'judges', 'evidence_required'):
            with self.subTest(field=field):
                bad = deepcopy(proposal)
                if field == 'remove':
                    bad['completion_obligations'].pop()
                else:
                    bad['completion_obligations'][-1][field] = (
                        ['changed'] if field in {'judges', 'evidence_required'} else 'changed')
                before = deepcopy(recipient)
                with self.assertRaisesRegex(ValueError, 'preserve transferred obligations'):
                    task_candidate_record(bad, task_id=recipient['id'], previous=recipient)
                self.assertEqual(recipient, before)


class TaskContractsTest(unittest.TestCase):
    def test_contract_has_stable_obligations_and_completion_requires_every_disposition(self):
        value = task_contract()
        task_contracts.validate_task_contract(value)
        assessment = {"item_dispositions": [
            {"obligation_id": "OB-1", "kind": "fulfilled", "evidence_refs": ["EV-1"]},
            {"obligation_id": "OB-2", "kind": "transferred", "evidence_refs": [], "target_task_id": "TK-2", "target_obligation_id": "OB-9", "authority_ref": "GR-1"},
        ]}
        task_contracts.validate_item_dispositions(value, assessment)
        self.assertEqual(task_contracts.remaining_obligations(value, assessment), [])

    def test_unresolved_inspection_is_not_a_false_or_open_disposition(self):
        value = task_contract()
        assessment = {"unresolved": [{"obligation_id": "OB-1", "missing_inputs": ["EV-1"], "next_owner": "AC-recover"}],
                      "item_dispositions": [{"obligation_id": "OB-2", "kind": "fulfilled", "evidence_refs": []}]}
        with self.assertRaisesRegex(ValueError, "unresolved"):
            task_contracts.validate_item_dispositions(value, assessment, require_complete=True)
        self.assertEqual(task_contracts.remaining_obligations(value, assessment), ["OB-1"])

    def test_waiver_and_transfer_need_authoritative_links(self):
        value = task_contract()
        for row in (
            {"obligation_id": "OB-1", "kind": "waived", "evidence_refs": ["EV-1"]},
            {"obligation_id": "OB-1", "kind": "transferred", "target_task_id": "TK-2", "authority_ref": "GR-1"},
        ):
            with self.subTest(row=row):
                with self.assertRaises(ValueError):
                    task_contracts.validate_item_dispositions(value, {"item_dispositions": [row]})
        with self.assertRaises(ValueError):
            task_contracts.validate_item_dispositions(value, {"item_dispositions": [{
                "obligation_id": "OB-1", "kind": "waived", "evidence_refs": ["EV-1"], "authority_ref": "GR-unrelated",
            }]})

    def test_readiness_is_derived_not_a_saved_task_state(self):
        value, instance, runtime = approved_task()
        before = deepcopy(runtime)
        result = planning.task_ready(value, instance, runtime)
        self.assertEqual(result["state"], "ready")
        self.assertEqual(runtime, before)

    def test_repetition_lineages_keep_ai_repair_distinct_from_user_authority(self):
        runtime = {'history':[{'kind':'task_repetition','lineage':name,'lineage_id':'TK-1',
            'outcome':'revised','owner':'ai'} for name in task_contracts.REPEAT_LINEAGES]}
        lineages = task_contracts.repetition_lineages(runtime, "TK-1")
        self.assertEqual(set(lineages), {"import_rework", "selection_failure", "exhaustion_empty", "proposal_version", "contract_revision"})
        self.assertTrue(all(row["owner"] == "ai" for row in lineages.values()))
        self.assertTrue(all(row['count']==1 for row in lineages.values()))

    def test_planning_routes_tasks_to_derived_readiness_and_item_plan_checks(self):
        value, instance, runtime = approved_task()
        self.assertEqual(planning.task_ready(value, instance, runtime)["state"], "ready")
        self.assertEqual(planning.ready_task_ids(runtime, instance), ["TK-1"])
        plan = {'dispositions':[task_disposition('TK-1','not_selected')], 'task_assessments':[]}
        planning.validate_plan_submission(plan, {"TK-1": value}, ["TK-1"])
        invalid = {'dispositions': [task_disposition('TK-absent'), task_disposition('TK-absent')], 'task_assessments': []}
        with self.assertRaises(ValueError) as rejected:
            planning.validate_plan_submission(invalid, {'TK-1': value}, ['TK-1'])
        for detail in ("missing=['TK-1']", "unexpected=['TK-absent']", "duplicate=['TK-absent']"):
            self.assertIn(detail, str(rejected.exception))

    def test_family_qualified_condition_does_not_read_a_same_id_from_another_family(self):
        instance = {"knowledge": {"X": {"id": "X", "status": "verified"}}}
        runtime = {"tasks": {"X": {"id": "X", "status": "completed"}}}
        result = planning.evaluate_condition({"op": "record_lifecycle_is", "space":"research", "family": "knowledge", "record_id": "X", "value": "active"}, instance, runtime)
        self.assertEqual(result["state"], "evaluation_error")
        self.assertIn('duplicate',result['errors'][0])

    def test_decision_and_artifact_conditions_preserve_effect_and_validity(self):
        _, instance, runtime = approved_task()
        instance['decisions']={'DC-1':{'id':'DC-1','actor':'user','source_ref':'SO-1',
            'source_sha256':'a'*64,'change':{'value':'continue'}}}
        self.assertEqual(planning.evaluate_condition({"op": "decision_value_is", "decision_id": "DC-1", "value": "continue"}, instance, {})["state"], "ready")
        instance['decisions']['DC-1']['source_sha256']='b'*64
        self.assertEqual(planning.evaluate_condition({'op':'decision_value_is','decision_id':'DC-1','value':'continue'},instance,runtime)['state'],'not_ready')
        import hashlib
        data=b'valid proof output'
        condition={'op':'artifact_valid','artifact_ref':{'snapshot':'SN-1','path':'runtime/artifacts/BA-1/proof.txt','sha256':hashlib.sha256(data).hexdigest()}}
        context={'snapshot':'SN-1','read_artifact':lambda p,s:data,'validate_artifact':lambda r,b:b==data}
        self.assertEqual(planning.evaluate_condition(condition,instance,runtime,evaluation_context=context)['state'],'ready')
        context['snapshot']='SN-later-evaluation'
        self.assertEqual(planning.evaluate_condition(condition,instance,runtime,evaluation_context=context)['state'],'ready')
        context['read_artifact']=lambda p,s:b'corrupt'
        self.assertEqual(planning.evaluate_condition(condition,instance,runtime,evaluation_context=context)['state'],'evaluation_error')

    def test_prose_requirement_does_not_require_a_future_id_equal_to_the_description(self):
        wire = candidate()
        wire['completion_obligations'][0]['evidence_requirements'] = ['Code and exact output for the full stated range']
        task = contracts.task_candidate_record(wire, task_id='TK-new')
        # The engine stores the contract without the wire-only revision pointer.
        del task['revises_task_id']
        assessment = {'decision':'completed', 'item_dispositions':[
            {'obligation_id':'OB-argument','kind':'fulfilled','evidence_refs':['EX-newly-created']}], 'unresolved':[]}
        task_contracts.validate_item_dispositions(task, assessment)
        task['completion_obligations'][0]['evidence_required'] = ['KN-required-existing']
        with self.assertRaisesRegex(ValueError, 'required evidence'):
            task_contracts.validate_item_dispositions(task, assessment)
        assessment['item_dispositions'][0]['evidence_refs'].append('KN-required-existing')
        task_contracts.validate_item_dispositions(task, assessment)
        fields = list(submission._explicit_reference_fields(wire))
        self.assertFalse(any('evidence_requirements' in path for path, _ in fields))


class TaskReadinessTests(unittest.TestCase):
    def test_review_cannot_be_replaced_by_an_unsubstantiated_summary(self):
        value,i,r=approved_task();value['reviews'][0]['item_reviews']=[]
        self.assertNotEqual(planning.task_ready(value,i,r)['state'],'ready')

    def test_each_actual_premise_change_blocks_an_otherwise_ready_task(self):
        mutations=[lambda t,i,r:t['reviews'][0].update(inputs_current=False),
            lambda t,i,r:i['sources'].clear(),
            lambda t,i,r:i['sources'][0].update(sha256='b'*64),
            lambda t,i,r:i['grants']['GR-1'].update(status='revoked'),
            lambda t,i,r:i['execution_profiles'].clear(),
            lambda t,i,r:t.update(revision_requested={'revision':1,'source':'EX-repair'}),
            lambda t,i,r:r['question_links'].append({'id':'Q-1','owner':'user','status':'open','blocks':True,'target_ids':['TK-1'],'unresolved_target_ids':['TK-1']}),
            lambda t,i,r:r['queue'].append({'id':'AC-revise','role':'research_preparation','revision_targets':{'TK-1':{}}})]
        for mutate in mutations:
            with self.subTest(mutate=mutate):
                t,i,r=approved_task();self.assertEqual(planning.task_ready(t,i,r)['state'],'ready')
                mutate(t,i,r);self.assertEqual(planning.task_ready(t,i,r)['state'],'not_ready')

    def test_missing_input_cannot_be_approved_into_existence(self):
        t,i,r=approved_task();t['inputs'].append('SO-absent');approve_task(t,i,r)
        self.assertIn('missing inputs',planning.task_ready(t,i,r)['errors'][0])

    def test_profile_edition_and_fixed_trust_must_still_apply(self):
        from do_math.execution_profiles import profile_ref
        t,i,r=approved_task();t.update(work_class='formal',trust_environment_id='TE-1')
        i.update(active_trust_environment='TE-1',trust_environments={'TE-1':{'id':'TE-1','status':'active'}});approve_task(t,i,r)
        action={'id':'AC-work','role':'research_work','target':t['id'],'profile_ref':profile_ref(next(iter(i['execution_profiles'].values())))}
        self.assertEqual(planning.task_ready(t,i,r,action=action)['state'],'ready')
        action['profile_ref']['revision']+=1
        self.assertEqual(planning.task_ready(t,i,r,action=action)['state'],'not_ready')
        i['active_trust_environment']='TE-2'
        self.assertEqual(planning.task_ready(t,i,r)['state'],'not_ready')

    def test_split_knowledge_evidence_is_part_of_review_currentness(self):
        t,i,r=approved_task()
        i['knowledge']={'KN-1':{'id':'KN-1','exposition_id':'XP-1','formal_result_id':'FR-1'}}
        i['expositions']={'XP-1':{'id':'XP-1','items':['old']}}
        i['formal_results']={'FR-1':{'id':'FR-1','verification':{'status':'verified'}}}
        t['inputs'].append('KN-1');approve_task(t,i,r)
        self.assertEqual(planning.task_ready(t,i,r)['state'],'ready')
        i['expositions']['XP-1']['items']=['changed']
        self.assertEqual(planning.task_ready(t,i,r)['state'],'not_ready')

    def test_external_wait_and_formal_work_are_not_research_exhaustion(self):
        t,i,r=approved_task();t['waiting']={'kind':'external_event','next_owner':'external_action'};t['status']='waiting'
        self.assertFalse(planning.exhaustion_state(i,r)['exhausted'])
        r['tasks']={};r['queue']=[{'id':'AC-formal','role':'formal_check','target':'FR-1'}]
        self.assertFalse(planning.exhaustion_state(i,r)['exhausted'])

    def test_empty_queue_is_not_exhaustion_when_work_is_running(self):
        runtime={'status':'active','tasks':{},'queue':[], 'executions':{'EX-live':{'id':'EX-live','role':'research_work','status':'running','action':{'target':'TK'}}}}
        self.assertFalse(planning.exhaustion_state({'goal_status':'unresolved'}, runtime)['exhausted'])

    def test_stale_approval_and_absent_input(self):
        value = task_contract()
        value['inputs'] = ['missing-input']
        value['reviews'] = [{'revision': 1, 'decision': 'approved', 'inputs_current': False}]
        result = planning.task_ready(value, {}, {'tasks': {value['id']: value}})
        self.assertNotEqual(result['state'], 'ready')

    def test_missing_returned_work_cannot_be_silently_omitted(self):
        value = task_contract(); value.update(status='waiting', results=[{'id': 'EV-return'}])
        with self.assertRaises(ValueError):
            planning.validate_plan_submission({'dispositions': [], 'task_assessments': []}, {value['id']: value}, [])

    def test_open_obligation_does_not_require_evidence_of_fulfilment(self):
        value = task_contract()
        task_contracts.validate_item_dispositions(value, {'item_dispositions': [
            {'obligation_id': 'OB-1', 'kind': 'open', 'evidence_refs': []},
            {'obligation_id': 'OB-2', 'kind': 'open', 'evidence_refs': []}]})

    def test_new_contract_fields_are_in_approval_digest(self):
        from copy import deepcopy
        value = task_contract(); changed = deepcopy(value)
        changed['completion_obligations'][0]['claim'] = 'A different requirement'
        self.assertNotEqual(planning.contract_hash(value), planning.contract_hash(changed))

    def test_artifact_metadata_is_not_evidence_of_readable_bytes(self):
        result = planning.evaluate_condition({'op':'artifact_valid', 'artifact_ref':'AR-1'},
            {'artifacts': {'AR-1': {'id':'AR-1','valid':True,'sha256':'a'*64}}}, {})
        self.assertEqual(result['state'], 'evaluation_error')


class AssessmentApplicationTests(unittest.TestCase):
    def test_transfer_binds_receiving_contract_and_blocks_incomplete_recipient_completion(self):
        i,r,a=transfer_assessment();previous=deepcopy(r)
        _,changed=apply_assessment(i,r,a)
        self.assertEqual(r,previous)
        self.assertEqual(changed['tasks']['TK-1']['status'],'closed')
        recipient=changed['tasks']['TK-2']
        self.assertEqual(recipient['revision'],2)
        self.assertEqual(recipient['reviews'],[])
        self.assertEqual(recipient['completion_obligations'][-1]['id'],'OB-inherited')
        self.assertEqual(recipient['completion_obligations'][-1]['claim'],r['tasks']['TK-1']['completion_obligations'][1]['claim'])
        recipient['results']=[{'id':'EV-1'}]
        incomplete={'task_id':'TK-2','decision':'completed','item_dispositions':[
            {'obligation_id':'OB-1','kind':'fulfilled','evidence_refs':['EV-1']},
            {'obligation_id':'OB-2','kind':'fulfilled','evidence_refs':[]}], 'unresolved':[]}
        with self.assertRaisesRegex(ValueError,'every obligation'):
            apply_assessment(i,changed,incomplete)

    def test_bare_unrelated_or_changed_authority_cannot_transfer(self):
        mutations=[lambda i,r,a:i['decisions'].clear(),
            lambda i,r,a:i['decisions']['DC-1']['change'].update(target_task_id='TK-other'),
            lambda i,r,a:i['decisions']['DC-1']['change'].update(revision=2),
            lambda i,r,a:i['decisions']['DC-1'].update(source_sha256='b'*64),
            lambda i,r,a:a['item_dispositions'][1].update(authority_ref='GR-1')]
        for mutation in mutations:
            with self.subTest(mutation=mutation):
                i,r,a=transfer_assessment();mutation(i,r,a);before=deepcopy((i,r))
                with self.assertRaises(ValueError):apply_assessment(i,r,a)
                self.assertEqual((i,r),before)

    def test_changed_decision_source_invalidates_scope_assessment_and_decision_condition(self):
        from do_math.task_scope import assessment_current
        instance, runtime, assessment = transfer_assessment()
        instance['decisions']['DC-1']['change']['value'] = 'continue'
        instance, runtime = apply_assessment(instance, runtime, assessment)
        source = runtime['tasks']['TK-1']
        condition = {'op': 'decision_value_is', 'decision_id': 'DC-1', 'value': 'continue'}
        context = {'task_id': source['id']}
        self.assertTrue(assessment_current(source, instance, runtime))
        self.assertEqual(planning.evaluate_condition(condition, instance, runtime,
            evaluation_context=context)['state'], 'ready')
        instance['decisions']['DC-1']['source_sha256'] = 'b' * 64
        self.assertFalse(assessment_current(source, instance, runtime))
        self.assertEqual(planning.evaluate_condition(condition, instance, runtime,
            evaluation_context=context)['state'], 'not_ready')
        self.assertEqual(source['status'], 'closed')

    def test_waiver_is_a_scope_decision_not_missing_evidence(self):
        i,r,a=transfer_assessment();a['item_dispositions'][1]={'obligation_id':'OB-2','kind':'waived','evidence_refs':[],'authority_ref':'DC-1'}
        a['decision']='completed'
        i['decisions']['DC-1']['change']['disposition']='waive'
        _,changed=apply_assessment(i,r,a)
        self.assertEqual(changed['tasks']['TK-1']['status'],'completed')
        self.assertEqual(changed['tasks']['TK-2']['revision'],1)

    def test_unresolved_inspection_preserves_missing_input_and_owner(self):
        i,r,a=transfer_assessment();a.update(decision='incomplete')
        a['item_dispositions']=a['item_dispositions'][1:]
        a['unresolved']=[{'obligation_id':'OB-1','missing_inputs':['EV-1'],'next_owner':'research_work'}]
        _,changed=apply_assessment(i,r,a)
        self.assertEqual(changed['tasks']['TK-1']['waiting']['target_refs'],['EV-1'])
        self.assertEqual(changed['tasks']['TK-1']['waiting']['next_owner'],'research_work')
        self.assertEqual(task_contracts.returned_task_ids(changed['tasks']),[])

    def test_missing_assessment_input_arrival_reopens_assessment_without_new_work(self):
        from do_math.task_scope import refresh_task_assessments
        for reference in ('SO-new', 'new.txt', 'source:new.txt', 'sources/new.txt'):
            with self.subTest(reference=reference):
                i,r,a=transfer_assessment();a.update(decision='incomplete')
                a['item_dispositions']=a['item_dispositions'][1:]
                a['unresolved']=[{'obligation_id':'OB-1','missing_inputs':[reference],'next_owner':'research_work'}]
                i,r=apply_assessment(i,r,a)
                results = deepcopy(r['tasks']['TK-1']['results'])
                self.assertFalse(task_contracts.returned_task_ids(r['tasks']))
                i['sources'].append({'id':'SO-other','name':'other.txt',
                    'path':'sources/other.txt','sha256':'c'*64})
                self.assertEqual(refresh_task_assessments(i,r), [])
                self.assertTrue(r['tasks']['TK-1']['assessment']['current'])
                i['sources'].append({'id':'SO-new','name':'new.txt',
                    'path':'sources/new.txt','sha256':'b'*64})
                self.assertEqual(refresh_task_assessments(i,r),['TK-1'])
                self.assertEqual(task_contracts.returned_task_ids(r['tasks']),['TK-1'])
                self.assertEqual(r['tasks']['TK-1']['results'], results)

    def test_plan_covers_every_ready_and_returned_task_and_rejects_double_disposition(self):
        i,r,a=transfer_assessment()
        plan={'dispositions':[],'task_assessments':[a]}
        planning.validate_plan_submission(plan,r['tasks'],[])
        for plan,ready in [({'dispositions':[],'task_assessments':[]},[]),
                           ({'dispositions':[],'task_assessments':[a]},['TK-2']),
                           ({'dispositions':[task_disposition('TK-2')]*2,'task_assessments':[a]},['TK-2']),
                           ({'dispositions':[task_disposition('TK-1')],'task_assessments':[a]},['TK-1'])]:
            with self.assertRaises(ValueError):planning.validate_plan_submission(plan,r['tasks'],ready)

    def test_incomplete_open_work_is_available_for_a_later_continuation_plan(self):
        i,r,a=transfer_assessment();t=r['tasks']['TK-1']
        t['waiting']={'kind':'assessment','next_owner':'research_plan'};approve_task(t,i,r)
        a.update(decision='incomplete',item_dispositions=[{'obligation_id':'OB-1','kind':'open','evidence_refs':[]},
                                                        {'obligation_id':'OB-2','kind':'open','evidence_refs':[]}])
        i,r=apply_assessment(i,r,a)
        self.assertEqual(planning.task_ready(r['tasks']['TK-1'],i,r)['state'],'ready')
        self.assertTrue(any(q['role']=='research_plan' for q in r['queue']))

    def test_nonselection_revisit_is_an_actual_machine_event(self):
        t,i,r=approved_task();t['selection_disposition']={**task_disposition(t['id'],'not_selected'),
            'execution_id':'EX-plan','revisit':{'at':'2026-09-20T00:00:00Z','event_refs':[]}}
        events=planning.collect_due_events(i,r,'2026-09-20T00:00:01Z')
        self.assertTrue(any(e['kind']=='task_revisit_due' and e['target']==t['id'] for e in events))

    def test_planner_can_aggregate_the_tasks_current_specialist_receipt(self):
        for judge in ('identity_review', 'formal_check'):
            with self.subTest(judge=judge):
                instance, runtime, assessment, _, _ = specialist_assessment(judge)
                _, changed = apply_assessment(instance, runtime, assessment)
                self.assertEqual(changed['tasks']['TK-1']['status'], 'completed')

    def test_foreign_stale_or_cycle_only_receipt_does_not_authorize_completion(self):
        for mutation in ('foreign', 'suspended', 'cycle', 'changed_exposition'):
            with self.subTest(mutation=mutation):
                instance, runtime, assessment, kid, aid = specialist_assessment()
                if mutation == 'foreign': instance['knowledge'][kid]['task_id'] = 'TK-other'
                elif mutation == 'suspended':
                    for row in instance['assessment_uses'].values(): row['status'] = 'suspended'
                elif mutation == 'cycle': assessment['item_dispositions'][0]['evidence_refs'] = ['RC-fixture']
                else: instance['expositions'][instance['knowledge'][kid]['exposition_id']]['items'][0]['text'] += ' changed'
                with self.assertRaises(ValueError):
                    apply_assessment(instance, runtime, assessment)

    def test_unresolved_has_one_owner_and_can_be_reassessed_after_evidence_arrives(self):
        instance, runtime, assessment, kid, aid = specialist_assessment()
        waiting = deepcopy(assessment)
        waiting.update(decision='incomplete', item_dispositions=[], unresolved=[{
            'obligation_id':'OB-certification','missing_inputs':['IA-needed'], 'next_owner':'identity_review'}])
        _, changed = apply_assessment(instance, runtime, waiting)
        self.assertEqual(changed['tasks']['TK-1']['waiting']['kind'], 'assessment_input')
        duplicate = deepcopy(waiting)
        duplicate['item_dispositions'] = [{'obligation_id':'OB-certification','kind':'open','evidence_refs':[]}]
        with self.assertRaisesRegex(ValueError, 'undisposed'):
            apply_assessment(instance, runtime, duplicate)
        _, completed = apply_assessment(instance, changed, assessment)
        self.assertEqual(completed['tasks']['TK-1']['status'], 'completed')

    def test_goal_judgment_must_cover_this_tasks_result_and_remain_current(self):
        from do_math.knowledge import capture_basis
        from do_math.planning import governance_revisions
        instance, runtime, assessment, kid, _ = specialist_assessment('goal_audit')
        judgment = {'id':'GJ-proof','decision':'satisfied','scope_complete':True,'current':True,
            'dependencies':[kid], 'record_basis':capture_basis(instance,runtime,[kid]),
            **governance_revisions(instance)}
        instance['goal_judgments'] = [judgment]
        assessment['item_dispositions'][0]['evidence_refs'] = ['GJ-proof']
        _, completed = apply_assessment(instance, runtime, assessment)
        self.assertEqual(completed['tasks']['TK-1']['status'],'completed')
        judgment['current'] = False
        with self.assertRaises(ValueError):
            apply_assessment(instance, runtime, assessment)


class RepetitionLineageTests(unittest.TestCase):
    def test_real_receipts_produce_all_five_lineages_and_initial_versions(self):
        from do_math import revisions
        t,i,r=approved_task();t['producer_execution']='EX-prep'
        i['knowledge']={'KN-first':{'id':'KN-first','producer_execution':'EX-work'},
                        'KN-next':{'id':'KN-next','producer_execution':'EX-revise','supersedes':'KN-first'}}
        for identifier,action,output,accepted in [
            ('EX-prep',{'role':'research_preparation'},{'summary':'preserved one contract'},True),
            ('EX-plan',{'role':'research_plan'},{'summary':'semantic rejection'},False),
            ('EX-import',{'role':'intent_interpretation','stage':'interpret','previous_import_id':'IM-1','target':'UI-original'}, {'summary':'reauthor interpretation'},True),
            ('EX-work',{'role':'research_work'},{'summary':'first proposal'},True),
            ('EX-revise',{'role':'research_work'},{'summary':'replacement proposal'},True)]:
            r['executions'][identifier]={'id':identifier,'role':action['role'],'status':'ended'}
            revisions.bind_repetition_bases(i,r,action)
            revisions.record_import_rework(i,r,action,identifier)
            revisions.record_execution_outcome(i,r,action,output,identifier,accepted=accepted)
        counts=task_contracts.repetition_lineages(r)
        self.assertTrue(all(row['events'] for row in counts.values()))
        self.assertEqual(counts['proposal_version']['by_lineage'],{'KN-first':2})
        self.assertEqual(counts['contract_revision']['count'],1)
        self.assertEqual(counts['exhaustion_empty']['count'],0)

    def test_a_technical_retry_does_not_reset_the_configured_user_limit(self):
        from do_math import revisions
        i={'config':{'selection_failure_limit':1}};r={'history':[],'queue':[],'executions':{}}
        revisions.record_repetition(i,r,lineage='selection_failure',lineage_id='population',event_ref='EX-bad',outcome='rejected',owner='ai',reason='missing dispositions')
        action={'id':'AC-retry','role':'research_plan','continuation_of':'EX-bad','repetition_bases':{'selection_failure':'population'}}
        r['executions']['EX-bad']={'id':'EX-bad','role':'research_plan','action':{'id':'AC-retry'},'status':'ended'}
        self.assertTrue(revisions.action_repetition_waits(i,r,action))
        r['executions']['EX-op']={'id':'EX-op','role':'operational_review','status':'ended','outcome':'output_accepted'}
        r['operational_dispositions']={'OD-1':{'id':'OD-1','execution_id':'EX-op','target_execution_id':'EX-bad','status':'applied',
            'disposition':{'kind':'retry','basis_refs':['EX-bad'],'next_owner':'research_plan','reason':'fixed input manifest',
                           'scope':'repeat only the held plan','replay_safety':'no external effects'}}}
        self.assertTrue(revisions.action_repetition_waits(i,r,action))
        self.assertEqual(task_contracts.repetition_lineages(r)['selection_failure']['count'],1)
        self.assertEqual(revisions.repetition_hold(r,'selection_failure','population')['owner'],'user')

    def test_new_request_ids_do_not_reset_semantic_lineage(self):
        from do_math import revisions
        t,i,r=approved_task()
        a={'id':'AC-1','role':'research_plan'};b={'id':'AC-2','role':'research_plan'}
        revisions.bind_repetition_bases(i,r,a);revisions.bind_repetition_bases(i,r,b)
        self.assertEqual(a['repetition_bases'],b['repetition_bases'])
        i['sources'][0]['sha256']='b'*64
        c={'id':'AC-3','role':'research_plan'};revisions.bind_repetition_bases(i,r,c)
        self.assertNotEqual(a['repetition_bases'],c['repetition_bases'])

    def test_one_case_grant_is_available_before_reservation_but_not_after_other_use(self):
        t,i,r=approved_task();i['grants']['GR-1']['reuse']='once';approve_task(t,i,r)
        self.assertEqual(planning.task_ready(t,i,r)['state'],'ready')
        r['executions']['EX-used']={'id':'EX-used','grant_id':'GR-1','role':'research_work','status':'ended','action':{'id':'AC-other'}}
        self.assertEqual(planning.task_ready(t,i,r)['state'],'not_ready')

    def test_one_regeneration_diagnosis_waits_for_a_new_basis_after_its_attempt(self):
        for outcome in ('output_accepted', 'execution_incomplete'):
            with self.subTest(outcome=outcome):
                instance={'id':'IN-one','goal_status':'unresolved','sources':[]}
                runtime={'status':'active','tasks':{},'queue':[],'executions':{},'events':[],'pending_events':[],'history':[
                    {'kind':'task_repetition','lineage':'exhaustion_empty','lineage_id':'basis-one',
                     'outcome':'empty','event_ref':'EX-prepare','reason':'No candidate available'}]}
                planning.schedule_reconsideration(instance,runtime,now='2026-09-20T00:00:00Z')
                action=deepcopy(runtime['queue'].pop())
                self.assertEqual(action['role'],'research_plan')
                runtime['executions']['EX-plan']={'id':'EX-plan','role':'research_plan','status':'ended',
                    'outcome':outcome,'action':action}
                planning.schedule_reconsideration(instance,runtime,now='2026-09-20T00:00:01Z')
                self.assertEqual(runtime['queue'],[])
                instance['sources'].append({'id':'SO-new','sha256':'a'*64})
                planning.schedule_reconsideration(instance,runtime,now='2026-09-20T00:00:02Z')
                self.assertEqual(len(runtime['queue']),1)
                self.assertNotEqual(runtime['queue'][0]['exhaustion_event_ref'],action['exhaustion_event_ref'])

    def test_empty_regeneration_cannot_immediately_repeat_and_periodic_is_independent(self):
        from do_math import revisions
        from do_math.configuration import DEFAULT_CONFIG
        i={'id':'IN-1','goal_status':'unresolved','config':deepcopy(DEFAULT_CONFIG)}
        r={'status':'active','tasks':{},'queue':[],'executions':{},'events':[],'pending_events':[],'history':[]}
        planning.schedule_reconsideration(i,r,now='2026-09-20T00:00:00Z')
        exhausted=next(e for e in r['events'] if e['kind']=='research_exhausted')
        self.assertEqual(exhausted['observed_at'],'2026-09-20T00:00:00Z')
        self.assertIsNone(exhausted['regenerate_after'])
        from do_math.state_contract import default_state_contract
        import jsonschema
        jsonschema.validate(exhausted,default_state_contract().family('runtime','events').schema)
        r['queue']=[]
        revisions.record_repetition(i,r,lineage='exhaustion_empty',lineage_id='basis-1',event_ref='EX-empty',
            outcome='empty',owner='ai',reason='no candidate')
        planning.schedule_reconsideration(i,r,now='2026-09-20T00:00:01Z')
        self.assertFalse(any(a['role']=='research_preparation' for a in r['queue']))
        r['next_research_reconsider_at']='2026-09-20T00:00:02Z'
        planning.record_due_events(i,r,'2026-09-20T00:00:03Z')
        planning.schedule_reconsideration(i,r,now='2026-09-20T00:00:03Z')
        self.assertTrue(any(a['role']=='research_preparation' for a in r['queue']))

    def test_repetition_threshold_counts_validation_failures_once_per_execution(self):
        from do_math import revisions
        instance = {'id': 'IN-1', 'config': {'selection_failure_limit': 2}}
        runtime = {'history': [], 'queue': [], 'executions': {}}
        action = {'role': 'research_plan', 'repetition_bases': {'selection_failure': 'population-1'}}
        for number, failure in enumerate(('output_validation', 'output_schema')):
            identifier = 'EX-' + str(number)
            runtime['executions'][identifier] = {'role': 'research_plan', 'error_kind': failure}
            for _ in range(2):
                revisions.record_execution_outcome(instance, runtime, action, {}, identifier, accepted=False)
            count = task_contracts.repetition_lineages(runtime)['selection_failure']['count']
            self.assertEqual(count, number + 1)
        self.assertTrue(revisions.repetition_hold(runtime, 'selection_failure', 'population-1'))
        self.assertFalse(revisions.repetition_hold(runtime, 'selection_failure', 'population-2'))

    def test_technical_plan_failures_do_not_count_and_acceptance_ends_the_sequence(self):
        from do_math import revisions
        instance = {'id': 'IN-1'}
        runtime = {'history': [], 'queue': [], 'executions': {}}
        action = {'role': 'research_plan', 'repetition_bases': {'selection_failure': 'population-1'}}
        failures = ('currentness_changed', 'publication_failure', 'input_failure')
        for number, failure in enumerate(failures):
            identifier = 'EX-technical-' + str(number)
            runtime['executions'][identifier] = {'role': 'research_plan', 'error_kind': failure}
            revisions.record_execution_outcome(instance, runtime, action, {}, identifier, accepted=False)
        self.assertEqual(task_contracts.repetition_lineages(runtime)['selection_failure']['count'], 0)
        runtime['executions']['EX-invalid'] = {'role': 'research_plan', 'error_kind': 'output_validation'}
        revisions.record_execution_outcome(instance, runtime, action, {}, 'EX-invalid', accepted=False)
        self.assertEqual(task_contracts.repetition_lineages(runtime)['selection_failure']['count'], 1)
        runtime['executions']['EX-accepted'] = {'role': 'research_plan'}
        revisions.record_execution_outcome(instance, runtime, action, {}, 'EX-accepted', accepted=True)
        self.assertEqual(task_contracts.repetition_lineages(runtime)['selection_failure']['count'], 0)

    def test_repetition_receipt_produces_followup_once(self):
        from do_math import revisions
        runtime={'history':[], 'queue':[], 'question_links':[]}
        for _ in range(2):
            revisions.record_repetition({},runtime,lineage='selection_failure',lineage_id='IN-1',event_ref='EX-failed',outcome='rejected',owner='ai',reason='schema repair')
        self.assertEqual(len(runtime['history']),1)
        self.assertEqual(len(runtime['queue']),1)
        self.assertEqual(runtime['queue'][0]['role'],'operational_review')
        self.assertFalse(runtime['question_links'])

class PreparationReceiptClassificationTests(unittest.TestCase):
    def test_rejected_preparation_does_not_count_as_an_empty_research_result(self):
        from do_math import revisions
        for failure in ('output_validation', 'currentness_changed', 'output_contract'):
            with self.subTest(failure=failure):
                instance = {'id': 'I', 'config': {'exhaustion_empty_limit': 1}}
                action = {'role': 'research_preparation',
                          'repetition_bases': {'exhaustion_empty': 'same-input'}}
                runtime = {'tasks': {}, 'queue': [], 'history': [], 'executions': {
                    'EX-failed': {'id': 'EX-failed', 'role': 'research_preparation',
                                  'error_kind': failure, 'observed_at': '2026-09-20T00:00:00Z'}}}
                revisions.record_execution_outcome(instance, runtime, action,
                    {'regenerate_after': '2026-09-21T00:00:00Z'}, 'EX-failed', accepted=False)
                self.assertEqual(runtime['history'], [])
                self.assertEqual(runtime['queue'], [])
                self.assertFalse(revisions.action_repetition_waits(instance, runtime, action))
                runtime['executions']['EX-empty'] = {'id': 'EX-empty', 'role': 'research_preparation'}
                revisions.record_execution_outcome(instance, runtime, action, {}, 'EX-empty', accepted=True)
                self.assertEqual(task_contracts.repetition_lineages(runtime)['exhaustion_empty']['count'], 1)
                self.assertTrue(revisions.repetition_hold(runtime, 'exhaustion_empty', 'same-input'))

    def test_partially_accepted_contract_still_records_its_real_production(self):
        from do_math import revisions
        value, instance, runtime = approved_task()
        value['producer_execution'] = 'EX-partial'
        runtime['executions']['EX-partial'] = {'id': 'EX-partial', 'role': 'research_preparation'}
        action = {'role': 'research_preparation', 'repetition_bases': {'exhaustion_empty': 'same-input'}}
        revisions.record_execution_outcome(instance, runtime, action, {}, 'EX-partial', accepted=False)
        receipts = [r for r in runtime['history'] if r.get('lineage') == 'exhaustion_empty']
        self.assertEqual([r['outcome'] for r in receipts], ['contracts_preserved'])
        self.assertEqual(task_contracts.repetition_lineages(runtime)['contract_revision']['count'], 1)


class TaskDependencyTests(unittest.TestCase):
    def test_primary_and_extension_dependencies_are_preserved(self):
        candidate = {'dependencies': ['TK-existing']}
        self.assertEqual(task_contracts.prepared_dependencies(candidate, {'observation_rules': []}), ['TK-existing'])
        self.assertEqual(task_contracts.prepared_dependencies(candidate,
            {'dependencies': ['new task', 'TK-existing']}, {'new task': 'TK-new'}), ['TK-existing', 'TK-new'])

    def test_engine_preserves_primary_dependency_when_extension_only_sets_condition(self):
        from do_math.engine import ResearchEngine
        from record_fixtures import approved_task
        from research_fixtures import candidate
        prior, instance, runtime = approved_task()
        proposal = candidate('Followup')
        # The author binds a permitted work profile it was given (research_fixtures.bind_candidates).
        proposal['profile_refs'] = deepcopy(prior['profile_refs'])
        proposal['dependencies'] = [prior['id']]
        runtime.update(cycles=0, executions={'EX-prepare': {'status': 'ended', 'extensions': {
            'task_conditions': [{'task_title': 'Followup', 'occurrence_condition': {'op': 'always'}}]}}})
        host = bare_engine(instance, runtime)
        host._record_output_questions = create_autospec(host._record_output_questions, return_value=None)
        host._evaluation_context = create_autospec(host._evaluation_context, return_value={})
        host._issued_input = create_autospec(host._issued_input, return_value=({}, None))
        host._governance = create_autospec(host._governance, side_effect=lambda: gov.governance_view(instance))
        ResearchEngine._apply(host, {'role': 'research_preparation'}, {'candidates': [proposal]}, 'EX-prepare')
        applied = next(t for t in runtime['tasks'].values() if t.get('title') == 'Followup')
        self.assertEqual(applied['dependencies'], [prior['id']])
        self.assertEqual(applied['occurrence_condition']['args'][1]['task_id'], prior['id'])


if __name__ == "__main__":
    unittest.main(verbosity=2)
