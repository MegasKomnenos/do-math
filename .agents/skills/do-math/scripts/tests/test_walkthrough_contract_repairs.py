"""Regression cases from the operator/producer/consumer walkthrough.

No provider calls, production instances, or scheduler registrations are made.
Compiler and identity records are explicit synthetic fixture evidence.
"""
from copy import deepcopy
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from do_math import cli, contracts, submission, task_contracts, task_scope
import test_redesign_TASKS as task_fixtures
import test_redesign_KNOWLEDGE as knowledge_fixtures
from research_fixtures import candidate, trust_fixture


class WalkthroughRepairs(unittest.TestCase):
    def test_removed_goal_kind_option_has_no_repository_or_workspace_effect(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with patch.object(cli, '_require_git') as git:
                with self.assertRaisesRegex(ValueError, 'unrecognized'):
                    cli.build_parser().parse_args(['init', '--repository', str(root/'repo'),
                        '--workspace', str(root/'work'), '--goal', 'Compare methods', '--goal-kind', 'research'])
                git.assert_not_called()
            self.assertEqual(list(root.iterdir()), [])
            request = {'schema_version':5, 'command':'init', 'payload':{'repository':str(root/'repo'),
                'workspace':str(root/'work'), 'goal':'Compare methods', 'goal_kind':'research'}}
            with patch.object(cli, '_require_git') as git:
                with self.assertRaisesRegex(ValueError, 'unknown|unrecognized|unexpected'):
                    cli._json_arguments(cli.build_parser(), request)
                git.assert_not_called()

    def test_independent_operation_does_not_require_a_conversation_lease(self):
        from do_math.engine import ResearchEngine
        engine = object.__new__(ResearchEngine)
        engine.instance = {'conversation_loss_policy':'continue_authorized'}
        engine.runtime = {'conversations':{}}
        self.assertTrue(engine._conversation_live())

    def test_governance_and_split_evidence_are_visible_but_arbitrary_nested_ids_are_not(self):
        context = {'governance': {'charter': {'id': 'CH-adopted'},
            'policy_records': [{'id': 'PO-adopted'}], 'research_context': [{'id': 'CX-adopted'}],
            'additional_audits': [{'id': 'AA-adopted'}], 'example': {'id': 'CH-example'}},
            'knowledge_catalog': [{'id': 'KN-result', 'formal_result_id': 'FR-result',
                                   'identity_assessment_ids': ['IA-result']}],
            'goal_judgments': [{'id': 'GJ-result'}]}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for identifier in ('CH-adopted','PO-adopted','CX-adopted','AA-adopted','FR-result','IA-result','GJ-result'):
                submission.validate_reference(identifier, context, root)
            context['reference_catalog'] = [{'value': 'invented'}]
            for identifier in ('CH-example', 'invented', 'CH-not-delivered'):
                with self.assertRaises(ValueError):
                    submission.validate_reference(identifier, context, root)

    def test_prose_requirement_does_not_require_a_future_id_equal_to_the_description(self):
        wire = candidate()
        wire['completion_obligations'][0]['evidence_requirements'] = ['Code and exact output for the full stated range']
        task = contracts.task_candidate_record(wire, task_id='TK-new')
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

    def specialist_fixture(self, judge='identity_review'):
        instance, runtime, assessment = task_fixtures.AssessmentApplicationTests().fixture()
        state, _, kid, aid = knowledge_fixtures.KnowledgeRedesign().verified()
        instance.update(state)
        instance['knowledge'][kid]['task_id'] = 'TK-1'
        task = runtime['tasks']['TK-1']
        task['completion_obligations'] = [{'id':'OB-certification', 'claim':'The returned proposal is certified',
            'judges':[judge], 'evidence_required':[]}]
        ref = aid if judge == 'identity_review' else instance['knowledge'][kid]['formal_result_id']
        assessment.update(decision='completed', item_dispositions=[{'obligation_id':'OB-certification',
            'kind':'fulfilled', 'evidence_refs':[ref]}], unresolved=[])
        return instance, runtime, assessment, kid, aid

    def test_planner_can_aggregate_the_tasks_current_specialist_receipt(self):
        for judge in ('identity_review', 'formal_check'):
            with self.subTest(judge=judge):
                instance, runtime, assessment, _, _ = self.specialist_fixture(judge)
                _, changed = task_fixtures.AssessmentApplicationTests().apply(instance, runtime, assessment)
                self.assertEqual(changed['tasks']['TK-1']['status'], 'completed')

    def test_foreign_stale_or_cycle_only_receipt_does_not_authorize_completion(self):
        for mutation in ('foreign', 'suspended', 'cycle', 'changed_exposition'):
            with self.subTest(mutation=mutation):
                instance, runtime, assessment, kid, aid = self.specialist_fixture()
                if mutation == 'foreign': instance['knowledge'][kid]['task_id'] = 'TK-other'
                elif mutation == 'suspended':
                    for row in instance['assessment_uses'].values(): row['status'] = 'suspended'
                elif mutation == 'cycle': assessment['item_dispositions'][0]['evidence_refs'] = ['RC-fixture']
                else: instance['expositions'][instance['knowledge'][kid]['exposition_id']]['items'][0]['text'] += ' changed'
                with self.assertRaises(ValueError):
                    task_fixtures.AssessmentApplicationTests().apply(instance, runtime, assessment)

    def test_unresolved_has_one_owner_and_can_be_reassessed_after_evidence_arrives(self):
        instance, runtime, assessment, kid, aid = self.specialist_fixture()
        waiting = deepcopy(assessment)
        waiting.update(decision='incomplete', item_dispositions=[], unresolved=[{
            'obligation_id':'OB-certification','missing_inputs':['IA-needed'], 'next_owner':'identity_review'}])
        _, changed = task_fixtures.AssessmentApplicationTests().apply(instance, runtime, waiting)
        self.assertEqual(changed['tasks']['TK-1']['waiting']['kind'], 'assessment_input')
        duplicate = deepcopy(waiting)
        duplicate['item_dispositions'] = [{'obligation_id':'OB-certification','kind':'open','evidence_refs':[]}]
        with self.assertRaisesRegex(ValueError, 'undisposed'):
            task_fixtures.AssessmentApplicationTests().apply(instance, runtime, duplicate)
        _, completed = task_fixtures.AssessmentApplicationTests().apply(instance, changed, assessment)
        self.assertEqual(completed['tasks']['TK-1']['status'], 'completed')

    def test_knowledge_input_exposes_exact_formal_and_identity_records(self):
        from do_math.knowledge_records import reader_view
        instance, _, kid, aid = knowledge_fixtures.KnowledgeRedesign().verified()
        view = reader_view(instance, kid)
        self.assertEqual(view['formal_result']['id'], view['formal_result_id'])
        self.assertEqual(view['identity_assessments'][0]['id'], aid)
        self.assertEqual(view['assessment_uses'][0]['assessment_id'], aid)

    def test_goal_judgment_must_cover_this_tasks_result_and_remain_current(self):
        from do_math.knowledge import capture_basis
        from do_math.planning import governance_revisions
        instance, runtime, assessment, kid, _ = self.specialist_fixture('goal_audit')
        judgment = {'id':'GJ-proof','decision':'satisfied','scope_complete':True,'current':True,
            'dependencies':[kid], 'record_basis':capture_basis(instance,runtime,[kid]),
            **governance_revisions(instance)}
        instance['goal_judgments'] = [judgment]
        assessment['item_dispositions'][0]['evidence_refs'] = ['GJ-proof']
        _, completed = task_fixtures.AssessmentApplicationTests().apply(instance, runtime, assessment)
        self.assertEqual(completed['tasks']['TK-1']['status'],'completed')
        judgment['current'] = False
        with self.assertRaises(ValueError):
            task_fixtures.AssessmentApplicationTests().apply(instance, runtime, assessment)

    def test_changed_installed_trust_bytes_block_match_publication(self):
        from do_math.engine import ResearchEngine
        from do_math.initialization import digest
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            request = trust_fixture(root, ['synthetic-lean'])
            request.pop('operation')
            environment = {**request, 'id':'TE-test', 'status':'active', 'source_ref':'approved-test',
                           'manifest_sha256':digest(request['manifest'])}
            engine = object.__new__(ResearchEngine)
            engine.instance = {'active_trust_environment':'TE-test', 'trust_environments':{'TE-test':environment}}
            from datetime import datetime, timezone
            engine.runtime = {'trust_transitions':{}, 'last_observed_utc':datetime.now(timezone.utc).isoformat()}
            engine._review_publication_premises = lambda _: {'fixed':'same stored environment'}
            engine._identity_assessment = lambda *a, **k: {'decision':'match'}
            updated = {'id':'RC-test','proposal':{},'decision':'match','identity_basis':{},'policy_ref':'policy',
                       'publication_premises':{'fixed':'same stored environment'}}
            with patch('do_math.review_engine.kr.record_identity_assessment', side_effect=RuntimeError('publication reached')):
                with self.assertRaisesRegex(RuntimeError, 'publication reached'):
                    engine._publish_identity_review_result({'target':'KN-test'}, updated, 'EX-review')
                Path(environment['manifest']['files'][0]['path']).write_bytes(b'changed compiler')
                with self.assertRaisesRegex(ValueError, 'trust'):
                    engine._publish_identity_review_result({'target':'KN-test'}, updated, 'EX-review')

    def test_repeated_submission_return_stops_producer_and_opens_one_diagnosis(self):
        from types import SimpleNamespace
        from do_math.repair_execution import route_submission_return
        opened = []
        engine = SimpleNamespace(instance={'config':{'max_output_repairs':1}}, runtime={'queue':[], 'waiting_actions':{}},
                                 _enqueue=lambda *a, **k: opened.append((a, k)))
        action = {'id':'AC-producer','role':'research_plan'}
        received = {'retry_bundle_ids':['IN-failed'], 'bundles':[], 'issues':[{'rule_id':'application'}]}
        route_submission_return(engine, action, received, 'EX-first', {'summary':'preserved'})
        retry = engine.runtime['queue'].pop()
        self.assertEqual(retry['repair_attempt'], 1)
        route_submission_return(engine, retry, received, 'EX-second', {'summary':'preserved'})
        self.assertEqual(engine.runtime['queue'], [])
        self.assertEqual(opened[0][0], ('operational_review','EX-second'))
        wait = engine.runtime['waiting_actions']['AC-producer']
        self.assertEqual(wait['action']['repair']['execution_id'], 'EX-second')
        self.assertEqual(wait['detail']['issues'], received['issues'])
        # Failed diagnostic output itself cannot open recursive diagnostics forever.
        route_submission_return(engine, {**retry,'role':'operational_review'}, received, 'EX-op', {})
        self.assertEqual(len(opened), 1)
        engine.instance['config']['max_output_repairs'] = 0
        route_submission_return(engine, {'id':'AC-zero','role':'research_plan'}, received, 'EX-zero', {})
        self.assertEqual(engine.runtime['queue'], [])
        self.assertIn('AC-zero', engine.runtime['waiting_actions'])

    def installation_fixture(self):
        from do_math import activities
        at = '2026-09-22T00:00:00+00:00'
        runtime = {'queue':[], 'executions':{}, 'activities':{}, 'waiting_actions':{}, 'status':'ready'}
        activities.open_activity(runtime, activity_id='AY-work', activity_kind='research_plan',
                                 owner_ref='AC-work', input_refs=[], opened_at=at)
        target = {'id':'EX-failed','role':'research_plan','status':'ended','error':'receiver contract conflict',
            'action':{'id':'AC-work','role':'research_plan','owner_activity_id':'AY-work'},
            'owner_activity_id':'AY-work', 'result_ref':'runtime/artifacts/failure/result.json'}
        runtime['executions']['EX-failed'] = target
        runtime['activities']['AY-work'].update(assigned_execution_ids=['EX-failed'],status='waiting',
            waiting={'condition':{'error':'receiver'},'reason':'receiver','next_owner':'operations','at':at})
        runtime['executions']['EX-diagnosis'] = {'id':'EX-diagnosis','role':'operational_review',
            'status':'ended','outcome':'output_accepted','action':{'target':'EX-failed'}}
        record = {'id':'OD-repair','execution_id':'EX-diagnosis','target_execution_id':'EX-failed',
            'status':'installation_repair_pending','disposition':{'kind':'repair',
                'repair_target':'installation:scripts/do_math/task_scope.py','meaning_preserving':True,
                'verification':'Reproduce the receiver conflict and verify completion without weakening evidence',
                'basis_refs':['EX-failed'],'reason':'Receiver contradicts the granted contract','next_owner':'installation_recovery'},
            'result':{'installation_repair':{'installation_sha256':'a'*64,
                'evidence_refs':['runtime/artifacts/failure/result.json']}}}
        runtime['operational_dispositions'] = {record['id']:record}
        runtime['waiting_actions']['AC-work'] = {'action':{**target['action'],'repair_attempt':2,
            'repair':{'execution_id':'EX-failed','issues':[{'message':'actual error'}]}},
            'execution_id':'EX-failed','kind':'output_validation','reason':'failed again'}
        return runtime, record

    def test_installation_request_requires_accepted_diagnosis_and_keeps_stable_identity(self):
        from do_math.repair_execution import installation_failure
        runtime, record = self.installation_fixture()
        before = installation_failure(runtime, record)
        record['result']['installation_repair'].update(status='failed', attempted_by='EX-repair')
        record['status'] = 'installation_repair_waiting'
        self.assertEqual(installation_failure(runtime, record), before)
        runtime['executions']['EX-failed']['contract_sha256'] = 'changed-contract'
        self.assertNotEqual(installation_failure(runtime, record)['failure_sha256'], before['failure_sha256'])
        runtime['executions']['EX-diagnosis']['outcome'] = 'execution_incomplete'
        with self.assertRaises(ValueError): installation_failure(runtime, record)

    def test_unattempted_installation_diagnosis_is_not_starved_by_an_old_wait(self):
        from do_math.repair_execution import pending_installation_repair
        runtime, record = self.installation_fixture()
        record['status'] = 'installation_repair_waiting'
        fresh = {**deepcopy(record),'id':'OD-fresh','status':'installation_repair_pending'}
        runtime['operational_dispositions'][fresh['id']] = fresh
        self.assertEqual(pending_installation_repair(runtime)['id'], 'OD-fresh')

    def test_pending_installation_repair_prevents_a_redundant_engine_start(self):
        from do_math import scheduled_operator as operator
        with tempfile.TemporaryDirectory() as directory, patch.object(operator,'read_status',return_value={
                'status':'ready','installation_repair':{'id':'OD-pending'}}):
            result = operator.engine_start_guard(Path(directory)/'repo','RI-test',Path(directory)/'work')
            self.assertEqual(result['outcome'],'installation_repair_waiting')

    def test_scheduler_drains_existing_calls_without_dispatching_new_work_during_installation_repair(self):
        from do_math.scheduler import SchedulerMixin
        from types import SimpleNamespace
        runtime, _ = self.installation_fixture()
        runtime['queue'] = [{'id':'AC-independent','role':'research_work'}]
        class Calls:
            def __init__(self): self.futures = {'existing':object()}; self.collected = 0; self.closed = False
            def collect(self):
                self.collected += 1
                if self.collected == 2: self.futures.clear()
            def close(self): self.closed = True
        calls = Calls()
        class Host(SchedulerMixin):
            def _controls(self): pass
            def _check_installation(self): pass
            def _save(self): pass
            def _dispatchable(self, *args): raise AssertionError('new work must not be dispatched')
        host = Host()
        host.instance = {'workspace':'.','id':'RI-test','config':{}}
        host.runtime = runtime
        with patch('do_math.scheduler.SessionSlots',return_value=SimpleNamespace(close=lambda:None)), \
                patch('do_math.scheduler.ModelCalls',return_value=calls), patch('do_math.scheduler.time.sleep'):
            host._run_parallel()
        self.assertEqual(calls.collected,2)
        self.assertTrue(calls.closed)
        self.assertEqual(runtime['status'],'waiting')
        self.assertEqual(runtime['queue'],[{'id':'AC-independent','role':'research_work'}])

    def test_supervisor_routes_diagnosed_live_engine_defect_and_probe_stays_read_only(self):
        from do_math import scheduled_operator as operator
        from types import SimpleNamespace
        runtime, record = self.installation_fixture()
        repository = SimpleNamespace(load=lambda: ('head',{'config':{'operator_enabled':True}},runtime))
        with tempfile.TemporaryDirectory() as directory, \
                patch.object(operator,'read_status',return_value={'status':'ready'}), \
                patch.object(operator,'ResearchRepository',return_value=repository), \
                patch.object(operator,'recovery',return_value={'outcome':'routed'}) as recover, \
                patch.object(operator,'schedule') as schedule:
            args = (Path(directory)/'repo', 'RI-test', Path(directory)/'work')
            self.assertEqual(operator.check(*args,probe=True)['outcome'],'installation_repair_pending')
            recover.assert_not_called(); schedule.assert_not_called()
            self.assertEqual(operator.check(*args)['outcome'],'routed')
            self.assertEqual(recover.call_args.kwargs['failure']['diagnosis_id'],record['id'])
            operator.hold(args[2],reason='user hold')
            recover.reset_mock()
            self.assertEqual(operator.check(*args)['outcome'],'held')
            recover.assert_not_called()

    def test_installation_repair_continues_latest_rejected_bundles_without_resetting_count(self):
        from do_math.repair_execution import resume_installation_repair
        runtime, record = self.installation_fixture()
        action = resume_installation_repair(runtime, record, repaired_by='EX-repair', at='2026-09-22T01:00:00Z')
        self.assertEqual(action['repair']['execution_id'],'EX-failed')
        self.assertEqual(action['repair_attempt'],2)
        self.assertEqual(action['continuation_of'],'EX-failed')
        self.assertEqual(runtime['waiting_actions'],{})
        self.assertEqual(record['status'],'applied')
        self.assertEqual(runtime['activities']['AY-work']['status'],'waiting')
        self.assertEqual(runtime['queue'],[action])


if __name__ == '__main__':
    unittest.main()
