"""Regression cases for the five approved execution-boundary repairs."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math.engine import ResearchEngine, DEFAULT_CONFIG
from do_math import observations, execution_profiles, task_scope, planning
from test_categories import test_group


class WaitOwnershipTests(unittest.TestCase):
    def receive(self, kind, *, creates_wait=True):
        engine = object.__new__(ResearchEngine)
        action = {'id': 'AC-one', 'role': 'intent_interpretation', 'target': 'UI-one'}
        row = {'action': deepcopy(action), 'kind': kind, 'execution_id': 'EX-one', 'reason': 'pending'}
        output = {'summary': 'Checked original'}
        engine.head = 'fixed'
        engine.instance = {'lifecycle': {'state': 'initializing'}}
        engine.runtime = {'status': 'initializing', 'history': [], 'waiting_actions': {},
            'executions': {'EX-one': {'status': 'ended', 'submission_intent': {
                'output_ref': 'out', 'extensions_ref': 'ext', 'check_ref': 'check'}}}}
        engine.store = SimpleNamespace(read=lambda ref, head: json.dumps(
            {'out': output, 'ext': {}, 'check': {'issues': []}}[ref]).encode())
        def apply(*args):
            if creates_wait:
                engine.runtime['waiting_actions']['AC-one'] = deepcopy(row)
            return {'status': 'accepted', 'bundles': [], 'retry_bundle_ids': []}
        if not creates_wait:
            engine.runtime['waiting_actions']['AC-one'] = deepcopy(row)
        engine._apply_submission_bundles = apply
        engine._remove_action = lambda action: None
        engine._record_task_receipt = lambda *args, **kwargs: None
        # Sealing is covered separately; this fixture starts at a captured
        # submission so the wait ownership rule is the behavior under test.
        sealed = {'output': output, 'extensions': {}, 'check': {'issues': []}, 'output_ref': 'out'}
        with patch('do_math.engine.submission.read_sealed_submission', return_value=sealed):
            engine._receive_submission(action, {}, 'EX-one', {}, {}, Path('.'))
        return engine.runtime

    def test_new_user_wait_survives_successful_response(self):
        for kind in ('import_application_authority', 'import_user_decision'):
            with self.subTest(kind=kind):
                runtime = self.receive(kind)
                self.assertIn('AC-one', runtime['waiting_actions'])
                self.assertEqual(runtime['waiting_actions']['AC-one']['kind'], kind)

    def test_resolved_publication_and_impact_waits_are_removed(self):
        for kind in ('submission_publication', 'impact_review'):
            self.assertNotIn('AC-one', self.receive(kind, creates_wait=False)['waiting_actions'])


class ToolchainContractTests(unittest.TestCase):
    @test_group('lean')
    def test_inspection_matches_actual_formal_verifier(self):
        from do_math.formal import inspect_toolchain, toolchain_errors, verify_lean, portable_bin, toolchain_root
        command = [str(portable_bin(toolchain_root()) / 'lean.exe')]
        if not Path(command[0]).is_file():
            self.skipTest('portable Lean is not installed')
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            observed = inspect_toolchain(command, root)
            self.assertEqual(toolchain_errors(observed), [])
            result = verify_lean(source='theorem repair_probe : True := True.intro', declarations=['repair_probe'],
                workspace=root, lean_command=command, expected_toolchain=observed)
            self.assertEqual(result['status'], 'verified', result)
            self.assertEqual(result['toolchain'], observed)

    def test_registration_rejects_the_incomplete_document_toolchain(self):
        from do_math.initialization import trust_environment_errors, digest
        manifest = {'command': ['lean'], 'foundation_profile': {
            'allowed_axioms': ['Classical.choice', 'Quot.sound', 'propext'],
            'forbidden': ['sorryAx', 'Lean.trustCompiler', 'additional_axioms']},
            'files': [{'role': role, 'path': str(Path(tempfile.gettempdir()) / role), 'sha256': 'a'*64}
                      for role in ('lean_binary','lean_source','lake_binary','mathlib_source','mathlib_build','checker')],
            'build_kind': 'clean', 'validation': {'status': 'verified', 'evidence_refs': ['fixture']}}
        environment = {'source_ref': 'UC-adopt', 'allowed_axioms': ['Classical.choice','Quot.sound','propext'],
            'manifest': manifest, 'manifest_sha256': digest(manifest),
            'toolchain': {'executable': 'lean', 'sha256': 'a'*64, 'version': 'Lean', 'configured_command': ['lean']}}
        errors = trust_environment_errors(environment, verify_files=False)
        self.assertTrue(any('verifier_sha256' in error for error in errors), errors)


class RuleBindingTests(unittest.TestCase):
    def test_producer_reports_missing_initial_rules_before_contract_review(self):
        from test_contract_checks import ContractCheckTests, checks
        fixture = ContractCheckTests()
        fixture.setUp()
        try:
            from unittest.mock import patch
            with patch('research_fixtures.supply_observation_rules', lambda *args: None):
                issues = fixture.issues(checks())
            self.assertIn('initial_observation_rules', issues)
        finally:
            fixture.doCleanups()

    def test_foreign_execution_is_not_silently_rebound(self):
        rules = [{'id':'active', 'operator':'active_duration_gte',
            'subject':{'kind':'execution','id':'EX-foreign'}, 'basis':{'source':'adapter_active_intervals','unit':'milliseconds'},
            'threshold':1000, 'required_evidence':['input/contract.json']}]
        with self.assertRaises(ValueError): observations.bind_task_rules(rules, 'EX-new')
        with self.assertRaises(ValueError): observations.task_rules_from_execution(rules, 'EX-new')

    def test_one_task_rule_can_start_two_distinct_executions(self):
        profile = next(p for p in execution_profiles.build_profiles({**deepcopy(DEFAULT_CONFIG),
            'tool_review_window_seconds':60, 'self_check_response_window_seconds':5})['execution_profiles'].values()
                       if p['role'] == 'research_work')
        rules = [{'id':'checkpoints', 'operator':'checkpoint_count_gte',
            'subject': {'kind':'checkpoint', 'id':'$execution'},
            'basis': {'source':'checkpoint', 'unit':'count'}, 'threshold':2, 'required_evidence':['contract']}]
        binder = getattr(observations, 'bind_task_rules', None)
        self.assertTrue(callable(binder), 'task rules need an execution binding before tracker admission')
        with tempfile.TemporaryDirectory() as directory:
            for eid in ('EX-first', 'EX-second'):
                bound = binder(rules, eid)
                config = observations.tracker_config(profile, initial_self_check_rules=bound)
                tracker = observations.ObservationTracker(eid, Path(directory), config)
                self.assertEqual(tracker.rules[0]['subject']['id'], eid)
        self.assertEqual(rules[0]['subject']['id'], '$execution')


class PartialWithdrawalTests(unittest.TestCase):
    def test_current_unperformed_withdrawal_preserves_results_and_residual_scope(self):
        from test_task_scope import TaskScopeTests
        _, runtime, snapshot = TaskScopeTests().fixture()
        _, changed = TaskScopeTests().withdraw(runtime, snapshot)
        task = changed['tasks']['TK-AI']
        task_scope.validate_withdrawal_record(task)
        self.assertIsNone(task['scope_disposition']['assessment_sha256'])
        for key in ('results_sha256', 'remaining_obligation_ids'):
            with self.subTest(missing=key):
                broken = deepcopy(task)
                broken['scope_disposition'].pop(key)
                with self.assertRaises(ValueError):
                    task_scope.validate_withdrawal_record(broken)

    def fixture(self):
        from test_task_scope import TaskScopeTests
        instance, runtime, _ = TaskScopeTests().fixture()
        task = runtime['tasks']['TK-AI']
        task.update(status='waiting', results=[{'execution_id':'EX-work','outcome':'partial'}])
        assessment = {'decision':'incomplete', 'execution_id':'EX-plan',
            'item_dispositions':[{'obligation_id':o['id'],'kind':'open','evidence_refs':[]}
                                 for o in task['completion_obligations']], 'unresolved':[]}
        assessment.update(contract_sha256=planning.contract_hash(task), results_sha256=planning._hash(task['results']),
            current=True, basis=task_scope.assessment_basis(task, assessment, instance, runtime))
        task['assessment'] = assessment
        return instance, runtime, {task['id']:deepcopy(task)}

    def test_assessed_partial_work_closes_without_becoming_complete(self):
        instance, runtime, snapshot = self.fixture()
        _, changed = task_scope.apply_task_dispositions(instance, runtime,
            [{'task_id':'TK-AI','disposition':'withdraw','reason':'This optional approach is no longer useful'}],
            execution_id='EX-next-plan', input_tasks=snapshot)
        task = changed['tasks']['TK-AI']
        self.assertEqual(task['status'], 'closed')
        self.assertEqual(task['results'], snapshot['TK-AI']['results'])
        self.assertNotIn('assessment', task)
        self.assertEqual(task['assessment_history'][-1], snapshot['TK-AI']['assessment'])
        self.assertEqual(task['scope_disposition']['remaining_obligation_ids'], ['OB-1','OB-2'])
        task_scope.validate_withdrawal_record(task)
        task['scope_disposition']['remaining_obligation_ids'] = []
        with self.assertRaises(ValueError): task_scope.validate_withdrawal_record(task)

    def test_unassessed_new_results_and_protected_scope_are_not_withdrawable(self):
        for change in ('new_result','stale_assessment','user_required','transferred_obligations'):
            with self.subTest(change=change):
                instance, runtime, snapshot = self.fixture()
                task = runtime['tasks']['TK-AI']
                if change == 'new_result': task['results'].append({'execution_id':'EX-new'})
                elif change == 'stale_assessment': task['assessment']['current'] = False
                else: task[change] = True
                with self.assertRaises(ValueError):
                    task_scope.apply_task_dispositions(instance,runtime,
                        [{'task_id':'TK-AI','disposition':'withdraw','reason':'not authorized'}],
                        execution_id='EX-next', input_tasks=snapshot)


class NativeRepairTests(unittest.TestCase):
    def setUp(self):
        from test_native_final_submission import NativeFinalGitTests
        NativeFinalGitTests.setUp(self)

    def test_normal_malformed_final_routes_back_to_producer(self):
        from test_native_final_submission import native_result
        execution = self.engine.runtime['executions']['EX-history']
        raw = b'{"report":'
        result = native_result(execution, self.context, raw, self.workspace)
        received = self.engine._collect_submitted_result(execution, result, self.context, self.schema, self.workspace)
        self.assertEqual(received['error_kind'], 'output_validation')
        from do_math.execution_lifecycle import transition_execution
        transition_execution(self.engine.runtime['executions'][execution['id']], 'stopping',
                             at='2026-09-22T12:00:00+00:00', stop_phase='terminating')
        self.engine._receive_submission(self.context['action'], received, execution['id'], self.context, self.schema, self.workspace)
        retry = next(a for a in self.engine.runtime['queue'] if a.get('continuation_of') == execution['id'])
        self.assertEqual(retry['role'], self.context['action']['role'])
        self.assertEqual(retry['repair_attempt'], 1)
        self.assertEqual(self.engine.store.read(retry['repair']['raw_output_ref'], self.engine.head), raw)


class InitialDiagnosisTests(unittest.TestCase):
    def test_exhausted_initial_repairs_have_a_reachable_diagnostic_owner(self):
        from do_math.repair_execution import route_submission_return
        requests = []
        engine = SimpleNamespace(instance={'lifecycle':{'state':'initializing'}, 'config':{'max_output_repairs':1}},
            runtime={'queue':[], 'waiting_actions':{}}, _enqueue=lambda *a, **kw: requests.append((a,kw)))
        action = {'id':'AC-original','role':'intent_interpretation','target':'UI-original','repair_attempt':1}
        route_submission_return(engine,action,{'retry_bundle_ids':[],'bundles':[],'issues':[]},'EX-bad',None)
        self.assertEqual(requests[0][0], ('maintenance','EX-bad'))
        self.assertTrue(requests[0][1]['initial_submission_diagnosis'])

    def test_diagnosis_and_bound_rules_fit_the_persisted_contract(self):
        import jsonschema
        from do_math.record_schemas import RECORDS
        action = {'id':'AC-diagnose','role':'maintenance','target':'EX-bad', 'initial_submission_diagnosis':True}
        jsonschema.Draft202012Validator(RECORDS['queue']).validate(action)
        retry = {'id':'AC-original','role':'intent_interpretation','diagnosis_attempt':1}
        jsonschema.Draft202012Validator(RECORDS['queue']).validate(retry)
        self.assertIn('observation_rules', RECORDS['executions']['properties'])

    def test_diagnosis_retry_preserves_the_original_and_is_bounded(self):
        from do_math.repair_execution import apply_initial_diagnosis, continue_initial_retries, route_submission_return
        from test_static_review_repairs import initial_failure_engine
        with tempfile.TemporaryDirectory() as directory:
            engine, action, wait = initial_failure_engine(Path(directory), 'output_validation')
            engine._save = Mock()
            diagnostic = {'target': 'EX-bad', 'initial_submission_diagnosis': True}
            apply_initial_diagnosis(engine, diagnostic,
                {'initial_submission_diagnosis':{'decision':'retry','guidance':'Return the missing required field'}}, 'EX-diagnosis')
            self.assertEqual(engine.runtime['queue'], [])
            engine.runtime['executions']['EX-diagnosis'] = {'id': 'EX-diagnosis', 'role': 'maintenance',
                'status': 'ended', 'outcome': 'output_accepted', 'action': diagnostic}
            continue_initial_retries(engine)
            self.assertTrue(engine.runtime['queue'], engine.runtime['waiting_actions'])
            retry = engine.runtime['queue'].pop()
            self.assertEqual(retry['target'], 'UI-original')
            self.assertEqual(retry['owner_activity_id'], 'AY-original')
            self.assertEqual(retry['diagnosis_attempt'], 1)
            route_submission_return(engine,retry,{'retry_bundle_ids':[],'bundles':[],'issues':[]},'EX-again',None)
            self.assertEqual(engine.runtime['queue'], [])


class ResearchAdmissionTests(unittest.TestCase):
    def test_public_task_flow_keeps_observation_and_state_contracts_consistent(self):
        from test_input_recovery import InputRecoveryPublicTests
        from test_engine import ScriptedRunner
        InputRecoveryPublicTests.setUp(self)
        engine = ResearchEngine(self.repo, self.identifier, runner=ScriptedRunner())
        # This is a scheduler/storage integration test with scripted answers,
        # not a test of the AI's reading of role prose (checked separately).
        engine._documents = {role: [dict(document, content='Synthetic fixture: ' + document['path'],
            sha256=hashlib.sha256(('Synthetic fixture: ' + document['path']).encode()).hexdigest())
            for document in documents] for role, documents in engine._documents.items()}
        engine.instance, engine.runtime = engine._configure_candidate(engine.instance, engine.runtime,
            {'origin':'user', 'config':{'tool_review_window_seconds':60,
                'self_check_response_window_seconds':5, 'plan_settle_seconds':1}})
        from test_lifecycle_engine import AdapterDouble
        for profile in engine.instance['execution_profiles'].values():
            if profile['actor_kind'] == 'ai':
                evidence = execution_profiles.capability_evidence(profile, AdapterDouble().describe(),
                    observed_at=engine._lifecycle_now().isoformat())
                engine.instance.setdefault('capability_evidence', {})[evidence['id']] = evidence
        engine._enqueue('research_preparation', reason='Exercise task admission after the approved initial fixture')
        engine._save()
        admit = engine._provider_admit
        def checked_admission(*args, **kwargs):
            accepted = admit(*args, **kwargs)
            self.assertTrue(accepted, {'reason':engine._slots.admission_reason,
                'resources':engine._slots.snapshot(), 'reservations':engine.runtime.get('reservations'),
                'profile':kwargs['profile']})
            return accepted
        engine._provider_admit = checked_admission
        # Readiness events may open an extra plan; a step counts an action,
        # not one of the four conceptual research phases.
        engine.run(max_steps=8)
        work = [e for e in engine.runtime['executions'].values() if e['role']=='research_work']
        self.assertTrue(work, {'tasks':engine.runtime['tasks'], 'queue':engine.runtime['queue'],
                              'waits':engine.runtime.get('waiting_actions'), 'history':engine.runtime['history'][-5:]})
        self.assertTrue(work[0]['observation_rules'])
        report = engine.check()
        self.assertEqual(report['errors'], [])
        # This fixture supplies synthetic initial interpretations without input
        # manifests. Persisted-state inspection also cannot inspect live Lean.
        self.assertEqual(report['inspection']['status'], 'incomplete', report)
        self.assertEqual({row['message'] for row in report['inspection']['findings']}, {
            'live installed trust-environment files (persisted snapshot inspection only) not examined',
            'EX-check: role input manifest not examined', 'EX-interpret: role input manifest not examined'})


if __name__ == '__main__':
    unittest.main()
