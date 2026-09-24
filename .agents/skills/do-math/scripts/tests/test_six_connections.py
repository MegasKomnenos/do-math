"""Regression cases for role handoffs; external model verdicts are fixtures."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math.context_store import prepare_role_input
from do_math import planning
from test_static_review_repairs import context_engine, package
from test_redesign_SURFACE import surface_state
import test_review_research


class InputConnections(unittest.TestCase):
    def test_fixed_question_is_packaged_and_answer_returns_to_its_seat(self):
        fixture = test_review_research.SplitReviewResearchTests()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        engine = fixture.engine
        cid = fixture.defer()
        action = next(a for a in engine.runtime['queue'] if a['role'] == 'supplemental_research')
        root = engine.root / 'packaged-investigation'
        context = {'action': deepcopy(action), **engine._review_research_context(action, root)}
        instance, _ = surface_state()
        instance.update(engine.instance)
        profile = next(p for p in instance['execution_profiles'].values() if p['role'] == 'supplemental_research')
        from do_math.contracts import with_integration_schema
        fitted = prepare_role_input(context, instance=instance, runtime=engine.runtime,
            role='supplemental_research', profile=profile, snapshot='a'*40,
            workspace=root, activity_id=action['owner_activity_id'], install_submission_tools=True,
            output_schema=with_integration_schema(engine._review_research_schema(action)))
        self.assertIsNone(fitted['overflow'])
        self.assertIsNone(fitted['manifest']['private_scope'])
        self.assertIn('review_research', fitted['manifest']['required_direct_keys'])
        self.assertNotIn('task', fitted['manifest']['required_direct_keys'])
        self.assertNotIn('role_review', fitted['context'])
        self.assertEqual(fitted['context']['review_research']['id'], action['research_request_id'])
        self.assertEqual(engine.runtime['review_cycles'][cid]['research'][action['research_request_id']]['status'], 'pending')
        engine.execute({'summary': 'PRIVATE-INITIAL-PEER'})
        research = fitted['context']['review_research']
        execution = {'id': 'INV-answer', 'role': 'supplemental_research', 'action': action,
            'execution_profile_ref': deepcopy(engine.research_profile), 'actor_kind': 'ai',
            'owner_activity_id': action['owner_activity_id']}
        self.assertEqual(engine._admit_review_execution(action, execution)['disposition'], 'admitted')
        engine.runtime['executions']['INV-answer'] = execution
        engine._apply_review_research(action, {'summary': 'Fixed source comparison',
            'used_sources': [research['sources'][0]['ref']], 'questions': [], 'research_request_id': research['id'],
            'request_digest': research['request_digest'], 'outcome': 'answered', 'answer': 'The map is complete.',
            'scope_complete': True, 'evidence_refs': [research['sources'][0]['ref']]}, 'INV-answer')
        execution.update(status='ended', outcome='output_accepted')
        resumed, _, _ = engine.execute()
        self.assertTrue(resumed['supplemental_results'])
        self.assertNotIn('PRIVATE-INITIAL-PEER', json.dumps(resumed))
        self.assertEqual(engine.assessment()['review_cycle_id'], cid)

    def test_task_result_paths_survive_packaging_without_entering_validation_hashes(self):
        raw = b'\xff exact result bytes\n'
        result = {'execution_id': 'EX-work', 'report': 'Returned evidence', 'output_files': [
            {'path': 'proof.bin', 'artifact_ref': 'runtime/artifacts/BA-work/proof.bin',
             'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)}]}
        task = {'id': 'TK-result', 'revision': 1, 'status': 'waiting', 'results': [result]}
        engine = context_engine(runtime={'tasks': {task['id']: task}})
        engine.store.read.return_value = raw
        original = deepcopy(task)
        for role in ('research_plan', 'research_preparation'):
            for _ in range(2):
                with tempfile.TemporaryDirectory() as directory:
                    root = Path(directory)
                    fitted, fixed = package(engine, root, role, target=task['id'])
                    ref = fitted['context']['tasks'][0]['source_ref']
                    detail = json.loads((root / ref['path']).read_bytes())
                    file = detail['results'][0]['output_files'][0]
                    self.assertEqual((root / file['local_path']).read_bytes(), raw)
                    self.assertEqual(fixed['tasks'][0], original)
                    self.assertEqual(engine.runtime['tasks'][task['id']], original)

    def test_missing_reader_task_is_an_input_error(self):
        instance, runtime = surface_state()
        runtime['tasks'] = {'TK': {'id': 'TK', 'status': 'waiting', 'results': [{'report': 'evidence'}]}}
        profile = next(p for p in instance['execution_profiles'].values() if p['role'] == 'research_plan')
        with tempfile.TemporaryDirectory() as directory, self.assertRaisesRegex(ValueError, 'preserve every current task'):
            prepare_role_input({'action': {'role': 'research_plan'}, 'ready_task_ids': [],
                'tasks': [], 'resources': {}, 'knowledge_catalog': []}, instance=instance,
                runtime=runtime, role='research_plan', profile=profile, snapshot='a'*40,
                workspace=Path(directory), activity_id='AY')


class PlanningConnections(unittest.TestCase):
    def test_plan_assessment_reaches_assignment_without_changing_contract(self):
        from do_math import execution_profiles, model_policy
        from test_redesign_TASKS import approved_fixture, approve, disposition
        task, instance, runtime = approved_fixture()
        engine = context_engine(instance, runtime)
        config = engine.instance['config']
        config['session_limits'] = deepcopy(model_policy.LIMITS)
        config['session_limits']['work'][config['tier_models']['high']] = 0
        config['role_tiers']['research_work'] = 'low'
        engine.instance.update(execution_profiles.build_profiles(config))
        task = engine.runtime['tasks'][task['id']]
        task['profile_refs'] = deepcopy(engine.instance['role_profile_refs']['research_work'])
        task['model_assessment'] = {'difficulty': 'low', 'importance': 'low', 'reason': 'Initial bounded work'}
        approve(task, engine.instance, engine.runtime)
        before = deepcopy(task)
        high = {'difficulty': 'high', 'importance': 'high', 'reason': 'New plan needs stronger reasoning'}
        engine.runtime['executions']['EX-plan'] = {'id': 'EX-plan', 'role': 'research_plan', 'status': 'ended',
            'model_decisions': {task['id']: high}}
        engine._apply_task_plan({'dispositions': [disposition(task['id'])], 'task_assessments': []},
            'EX-plan', deepcopy(engine.runtime['tasks']), [task['id']])
        action = next(a for a in engine.runtime['queue'] if a['role'] == 'research_work')
        selected = engine._select_model(action)
        self.assertEqual(selected['tier'], 'high')
        self.assertEqual(selected['model'], config['tier_models']['high'])
        self.assertEqual(action['model_assessment'], high)
        self.assertEqual(planning.contract_hash(engine.runtime['tasks'][task['id']]), planning.contract_hash(before))
        self.assertEqual(engine.runtime['tasks'][task['id']]['reviews'], before['reviews'])
        high['reason'] = 'Mutation of the source must not change the request'
        self.assertNotEqual(action['model_assessment'], high)
        from do_math.session_slots import SessionSlots
        from do_math.execution_lifecycle import create_execution, transition_execution
        profile = execution_profiles.resolve_profile(engine.instance['execution_profiles'], selected['profile_ref'])
        execution = create_execution(execution_id='EX-no-slot', owner_activity_id='AY-work', actor_kind='ai',
            input_manifest={}, profile_ref=selected['profile_ref'], created_at='2026-09-23T00:00:00+00:00')
        transition_execution(execution, 'starting', at='2026-09-23T00:00:00+00:00')
        slots = SessionSlots(engine.runtime, engine.instance)
        self.assertFalse(slots.acquire('EX-no-slot', 'work', selected['model'], profile=profile,
                                      execution=execution))
        self.assertEqual(engine._select_model(action)['tier'], 'high')

    def assessment_engine(self, directory):
        from test_lifecycle_engine import FakeEngine
        from test_redesign_TASKS import AssessmentApplicationTests
        from do_math.engine import ResearchEngine
        from do_math import task_contracts
        fixture = AssessmentApplicationTests()
        instance, runtime, assessment = fixture.fixture()
        assessment.update(decision='incomplete', item_dispositions=assessment['item_dispositions'][1:],
            unresolved=[{'obligation_id': 'OB-1', 'missing_inputs': ['SO-new'], 'next_owner': 'research_work'}])
        instance, runtime = fixture.apply(instance, runtime, assessment)
        engine = FakeEngine(directory)
        engine.instance['lifecycle']['state'] = 'active'
        engine.instance.update({key: value for key, value in instance.items() if key not in {'lifecycle', 'config'}})
        engine.runtime.update(runtime)
        engine.runtime['queue'] = [{'id': 'AC-other', 'role': 'research_preparation'}]
        engine._enqueue = ResearchEngine._enqueue.__get__(engine)
        return engine

    def test_readiness_refresh_requests_reassessment_while_other_work_remains(self):
        from do_math import task_contracts
        with tempfile.TemporaryDirectory() as directory:
            engine = self.assessment_engine(directory)
            engine.instance['sources'].append({'id': 'SO-new', 'name': 'new', 'path': 'new.txt', 'sha256': 'b'*64})
            original_results = deepcopy(engine.runtime['tasks']['TK-1']['results'])
            engine._refresh_readiness()
            self.assertFalse(engine.runtime['tasks']['TK-1']['assessment']['current'])
            plans = [a for a in engine.runtime['queue'] if a['role'] == 'research_plan']
            self.assertEqual(len(plans), 1)
            self.assertIn('TK-1', plans[0]['reason'])
            self.assertEqual(task_contracts.returned_task_ids(engine.runtime['tasks']), ['TK-1'])
            engine._refresh_readiness()
            self.assertEqual(len([a for a in engine.runtime['queue'] if a['role'] == 'research_plan']), 1)
            self.assertEqual(engine.runtime['tasks']['TK-1']['results'], original_results)

    def test_live_work_defers_reassessment_until_end_and_unrelated_changes_do_not_reopen(self):
        with tempfile.TemporaryDirectory() as directory:
            engine = self.assessment_engine(directory)
            engine.instance['sources'].append({'id': 'SO-other', 'name': 'other', 'path': 'other.txt', 'sha256': 'c'*64})
            engine._refresh_readiness()
            self.assertTrue(engine.runtime['tasks']['TK-1']['assessment']['current'])
            engine.runtime['executions']['EX-live'] = {'id': 'EX-live', 'status': 'running',
                'role': 'research_work', 'action': {'id': 'AC-live', 'role': 'research_work', 'target': 'TK-1'}}
            engine.instance['sources'].append({'id': 'SO-new', 'name': 'new', 'path': 'new.txt', 'sha256': 'b'*64})
            engine._refresh_readiness()
            self.assertFalse(any(a['role'] == 'research_plan' for a in engine.runtime['queue']))
            engine.runtime['executions']['EX-live']['status'] = 'ended'
            engine._refresh_readiness()
            self.assertFalse(engine.runtime['tasks']['TK-1']['assessment']['current'])
            self.assertEqual(len([a for a in engine.runtime['queue'] if a['role'] == 'research_plan']), 1)

    def test_terminal_history_remains_closed_when_assessment_evidence_changes(self):
        with tempfile.TemporaryDirectory() as directory:
            engine = self.assessment_engine(directory)
            task = engine.runtime['tasks']['TK-1']
            task['status'] = 'closed'
            original = deepcopy(task['results'])
            engine.instance['sources'].append({'id': 'SO-new', 'name': 'new', 'path': 'new.txt', 'sha256': 'b'*64})
            engine._refresh_readiness()
            self.assertEqual(engine.runtime['tasks']['TK-1']['status'], 'closed')
            self.assertEqual(engine.runtime['tasks']['TK-1']['results'], original)
            self.assertFalse(engine.runtime['tasks']['TK-1']['assessment']['current'])
            self.assertFalse(any(a['role'] == 'research_plan' for a in engine.runtime['queue']))


class OverflowConnections(unittest.TestCase):
    def fixture(self):
        from do_math import activities, execution_profiles
        from do_math.engine import ResearchEngine
        from test_redesign_TASKS import approved_fixture, approve
        task, instance, runtime = approved_fixture()
        engine = context_engine(instance, runtime)
        config = engine.instance['config']
        profiles = execution_profiles.build_profiles(config)
        engine.store.read.return_value = b'source'
        engine.instance['sources'][0]['sha256'] = hashlib.sha256(b'source').hexdigest()
        engine.instance.update(profiles)
        small = execution_profiles.resolve_profile(profiles['execution_profiles'], profiles['role_profile_refs']['research_work'][0])
        large = deepcopy(small)
        large['input']['max_input_bytes'] *= 2
        large = execution_profiles.seal_profile(large)
        engine.instance['execution_profiles'][large['id']] = large
        task['profile_refs'] = [execution_profiles.profile_ref(small), execution_profiles.profile_ref(large)]
        task['status'] = 'active'
        engine.runtime['tasks'][task['id']] = task
        approve(task, engine.instance, engine.runtime)
        action = {'id': 'AC-held', 'role': 'research_work', 'target': task['id'],
            'owner_activity_id': 'AY-held', 'grant_id': 'GR-1',
            'selected_contract_sha256': planning.contract_hash(task), 'profile_ref': execution_profiles.profile_ref(small),
            'model_assessment': {'difficulty': 'low', 'importance': 'low', 'reason': 'Bounded work'}}
        activities.open_activity(engine.runtime, activity_id='AY-held', activity_kind='research_work',
            owner_ref='AC-held', input_refs=[task['id']], opened_at='2026-09-23T00:00:00+00:00')
        activities.wait_for(engine.runtime, 'AY-held', reason='input_overflow',
            condition={'action_ids': ['AC-held']}, next_owner='research_plan', at='2026-09-23T00:00:00+00:00')
        engine.runtime['waiting_actions'] = {'AC-held': {'kind': 'input_overflow', 'action': action,
            'question_id': 'QU-held', 'next_owner': 'research_plan', 'detail': {
                'allowed_profile_candidates': [large['id']], 'cause': 'required_role_input',
                'packed_bytes': small['input']['max_input_bytes'] + 10}}}
        engine.instance['conversation_loss_policy'] = 'continue_authorized'
        engine._require_action_clock = lambda: '2026-09-23T00:00:00+00:00'
        engine._execution_profile = ResearchEngine._execution_profile.__get__(engine)
        return engine, execution_profiles.profile_ref(large)

    def test_overflow_choices_are_supplied_without_changing_ready_population(self):
        engine, reference = self.fixture()
        with tempfile.TemporaryDirectory() as directory:
            fitted, fixed = package(engine, Path(directory))
        self.assertEqual(fixed['ready_task_ids'], [])
        item = fitted['context']['input_overflow_requests'][0]
        self.assertEqual(item['action_id'], 'AC-held')
        self.assertEqual(item['owner_activity_id'], 'AY-held')
        self.assertEqual(item['allowed_profile_refs'], [reference])

    def test_planner_extension_accepts_exact_choice_and_requeues_same_obligation(self):
        from do_math import submission
        import jsonschema
        engine, reference = self.fixture()
        choice = {'action_id': 'AC-held', 'profile_ref': reference, 'reason': 'Required evidence fits'}
        extension = {'input_overflow_resolutions': [choice]}
        jsonschema.validate(extension, submission.extension_schema({'role': 'research_plan'}))
        with tempfile.TemporaryDirectory() as directory:
            _, fixed = package(engine, Path(directory))
        engine._apply_input_overflow_resolutions([choice], fixed, 'EX-plan')
        action = next(a for a in engine.runtime['queue'] if a['id'] == 'AC-held')
        self.assertEqual(action['owner_activity_id'], 'AY-held')
        self.assertEqual(action['profile_ref'], reference)
        self.assertEqual(action['model_assessment']['difficulty'], 'low')
        self.assertEqual(action['input_overflow_retry']['request_id'], 'EX-plan')
        self.assertEqual(action['input_overflow_retry']['state'], 'pending')
        self.assertNotIn('AC-held', engine.runtime['waiting_actions'])

    def test_stale_contract_or_unoffered_profile_cannot_release_wait(self):
        for mutation in ('contract', 'profile', 'question', 'review'):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as directory:
                engine, reference = self.fixture()
                _, fixed = package(engine, Path(directory))
                choice = {'action_id': 'AC-held', 'profile_ref': reference, 'reason': 'Fits'}
                if mutation == 'contract':
                    engine.runtime['tasks']['TK-1']['revision'] += 1
                elif mutation == 'profile':
                    choice['profile_ref'] = engine.instance['role_profile_refs']['research_plan'][0]
                elif mutation == 'question':
                    engine.runtime['waiting_actions']['AC-held']['question_id'] = 'QU-new-failure'
                else:
                    engine.runtime['waiting_actions']['AC-held']['action']['role'] = 'identity_review'
                with self.assertRaises(ValueError):
                    engine._apply_input_overflow_resolutions([choice], fixed, 'EX-plan')
                self.assertIn('AC-held', engine.runtime['waiting_actions'])

    def test_shared_submission_check_rejects_duplicate_and_unoffered_choices(self):
        from do_math import contracts, submission
        from do_math.repository import canonical_json
        from test_engine import common
        from research_fixtures import seal_response
        engine, reference = self.fixture()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _, fixed = package(engine, root)
            choice = {'action_id': 'AC-held', 'profile_ref': reference, 'reason': 'Fits required evidence'}
            for mode in ('valid', 'duplicate', 'profile', 'unknown'):
                row = deepcopy(choice)
                if mode == 'profile': row['profile_ref'] = engine.instance['role_profile_refs']['research_plan'][0]
                if mode == 'unknown': row['action_id'] = 'AC-unknown'
                extensions = {'input_overflow_resolutions': [row, row] if mode == 'duplicate' else [row]}
                (root / 'activity-extensions.json').write_bytes(canonical_json(extensions))
                output = common('research_plan')
                seal_response(output, fixed, root)
                issues = submission.payload_issues(output, contracts.schema_for('research_plan'), fixed, extensions, root)
                self.assertEqual(bool(issues), mode != 'valid', (mode, issues))

    def test_same_integration_receipt_prevents_duplicate_retry(self):
        from do_math import integration
        from test_engine import common
        engine, reference = self.fixture()
        with tempfile.TemporaryDirectory() as directory:
            _, fixed = package(engine, Path(directory))
        extension = {'input_overflow_resolutions': [{'action_id': 'AC-held', 'profile_ref': reference, 'reason': 'Fits'}]}
        calls = []
        def apply(instance, runtime, bundle):
            calls.append(bundle['integration_id'])
            engine.instance, engine.runtime = instance, runtime
            engine._apply_input_overflow_resolutions(bundle['extensions']['input_overflow_resolutions'], fixed, 'EX-plan')
        callbacks = {'apply_bundle': apply, 'validate_candidate': lambda *args: None,
                     'validate_current': lambda *args: None, 'publish': lambda *args: None}
        first = integration.apply_bundles(engine.instance, engine.runtime, common('research_plan'), extension, fixed,
                                         execution_id='EX-plan', **callbacks)
        self.assertEqual(first['status'], 'accepted', first['issues'])
        second = integration.apply_bundles(first['instance'], first['runtime'], common('research_plan'), extension, fixed,
                                          execution_id='EX-plan', **callbacks)
        self.assertEqual(second['bundles'][0]['status'], 'already_accepted', second['issues'])
        self.assertEqual(len(calls), 1)
        self.assertEqual(len([a for a in second['runtime']['queue'] if a['id'] == 'AC-held']), 1)


class ProviderConnections(unittest.TestCase):
    def test_result_observation_has_no_prepublication_schedule_effect(self):
        from test_provider_wait import ProviderTests, admit, MODEL, FAILURE
        from do_math.engine import ResearchEngine
        from unittest.mock import Mock
        fixture = ProviderTests()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        engine = object.__new__(ResearchEngine)
        engine.store = fixture.repository
        engine.head, engine.instance, engine.runtime = engine.store.load()
        engine._slots = None
        self.assertTrue(admit(engine._provider_slots(), engine.instance, engine.runtime, 'EX-limit'))
        engine._schedule_provider_wake = Mock()
        engine._provider_outcome('EX-limit', MODEL, {'status': 'failed', 'error_kind': 'provider_limit', 'failure': FAILURE})
        engine._schedule_provider_wake.assert_not_called()

    def test_saved_wait_drives_wake_and_schedule_failure_is_recoverable(self):
        from test_provider_wait import ProviderTests, admit, finish, MODEL, FAILURE
        from do_math.engine import ResearchEngine
        from do_math import scheduled_operator
        from unittest.mock import patch
        import time
        fixture = ProviderTests()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        engine = object.__new__(ResearchEngine)
        engine.store = fixture.repository
        engine.head, engine.instance, engine.runtime = engine.store.load()
        engine.instance['config']['operator_enabled'] = True
        engine._slots = None
        slots = engine._provider_slots()
        self.assertTrue(admit(slots, engine.instance, engine.runtime, 'EX-limit', current=time.time()))
        # Observation is separate from publication; the external effect reads Git.
        gate = slots.provider_result('EX-limit', 'claude', failure=FAILURE)
        finish(slots, engine.runtime, 'EX-limit', time.time())
        engine.runtime['waiting_actions'] = {'AC-held': {'action': {'id': 'AC-held', 'role': 'research_work'},
            'kind': 'execution_failure', 'failure_kind': 'provider_limit', 'execution_id': 'EX-limit',
            'reason': 'Synthetic provider limit'}}
        calls = []
        actual = {}
        def schedule(command, **kwargs):
            calls.append((command, kwargs))
            _, _, persisted = engine.store.load()
            from do_math.provider_wait import timestamp
            self.assertEqual(persisted['provider_waits']['PW-claude']['retry_at'], timestamp(gate['retry_at']))
            self.assertIn('AC-held', persisted['waiting_actions'])
            if command == 'status':
                return {'wake': actual.get('wake')}
            if command == 'schedule-wake':
                actual['wake'] = {'description': kwargs['wake_key'], 'next_run': kwargs['wake_at'], 'state': 'Ready'}
            return {}
        def save(artifacts=None):
            engine.head = engine.store.save_with_state(engine.head, engine.instance, engine.runtime, artifacts=artifacts or {})[0]
        engine._save = save
        with patch.object(scheduled_operator, 'schedule', side_effect=OSError('scheduler unavailable')):
            engine._publish_provider_result()
        _, _, persisted = engine.store.load()
        self.assertEqual(persisted['provider_wake']['status'], 'failed')
        from do_math.provider_wait import timestamp
        self.assertEqual(persisted['provider_waits']['PW-claude']['retry_at'], timestamp(gate['retry_at']))
        with patch.object(scheduled_operator, 'schedule', side_effect=schedule):
            with patch.object(scheduled_operator, 'read_status', return_value={'status': 'ready'}), patch.object(
                    scheduled_operator, 'engine_start_guard', return_value={'outcome': 'provider_waiting'}):
                observed = scheduled_operator.check(fixture.root, engine.instance['id'], fixture.root)
                self.assertEqual(observed['provider_wake']['status'], 'scheduled')
            engine._publish_provider_result()
        self.assertEqual(sum(command == 'schedule-wake' for command, _ in calls), 1)
        scheduled = next(kwargs for command, kwargs in calls if command == 'schedule-wake')
        self.assertEqual(scheduled['wake_at'], gate['retry_at'])
        self.assertEqual(scheduled['wake_key'], 'claude:' + str(gate['generation']))
        with patch.object(engine, '_save', side_effect=OSError('Git failed')), patch.object(
                scheduled_operator, 'schedule') as scheduling:
            with self.assertRaisesRegex(OSError, 'Git failed'):
                engine._publish_provider_result()
            scheduling.assert_not_called()
        with patch.object(scheduled_operator, 'schedule', side_effect=schedule):
            scheduled_operator.hold(fixture.root, reason='Synthetic HOLD')
            calls_before = len(calls)
            self.assertEqual(scheduled_operator.check(fixture.root, engine.instance['id'], fixture.root)['outcome'], 'held')
            self.assertEqual(len(calls), calls_before)
            self.assertEqual(scheduled_operator.reconcile_wake(fixture.root, engine.instance['id'], fixture.root,
                config=engine.instance['config'], status={'status': 'ready'})['status'], 'held')
            self.assertEqual(calls[-1][0], 'cancel-wake')


class OverflowGitConnection(unittest.TestCase):
    def test_plan_choice_repackages_original_work_and_reaches_runner(self):
        from test_input_recovery import InputRecoveryPublicTests
        from do_math.engine import ResearchEngine
        from do_math import execution_profiles
        from do_math.repository import canonical_json
        from test_redesign_TASKS import task as task_fixture, approve
        from test_engine import common, context_from
        from research_fixtures import local_job_runner, producer_result
        fixture = InputRecoveryPublicTests()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        calls = []
        class Runner:
            @local_job_runner
            def run(self, **arguments):
                context = context_from(arguments['prompt'])
                calls.append(deepcopy(context['action']))
                role = context['action']['role']
                output = common(role)
                if role == 'research_plan':
                    row = context['input_overflow_requests'][0]
                    extension = {'input_overflow_resolutions': [{'action_id': row['action_id'],
                        'profile_ref': row['allowed_profile_refs'][0], 'reason': 'The complete input fits this allowed profile'}]}
                    (arguments['workspace'] / 'activity-extensions.json').write_bytes(canonical_json(extension))
                elif role == 'research_work':
                    output.update(outcome='submitted', report='Read the complete assigned input and preserved the result.')
                else:
                    raise AssertionError('Unexpected role: ' + role)
                arguments['on_started']({'fixture': 'overflow response'})
                return producer_result({'status': 'completed', 'output': output, 'usage': {}}, arguments)
        engine = ResearchEngine(fixture.repo, fixture.identifier, runner=Runner())
        reference = engine.instance['role_profile_refs']['research_work'][-1]
        large = execution_profiles.resolve_profile(engine.instance['execution_profiles'], reference)
        large['input']['max_input_bytes'] = 2000000
        large['observation']['settings'].update(tool_review_window_seconds=60, self_check_response_window_seconds=5)
        large = execution_profiles.seal_profile(large)
        reference = execution_profiles.profile_ref(large)
        engine.instance['execution_profiles'][large['id']] = large
        small = deepcopy(large)
        small['input']['max_input_bytes'] = 500000
        small = execution_profiles.seal_profile(small)
        engine.instance['execution_profiles'][small['id']] = small
        from test_lifecycle_engine import AdapterDouble
        for profile in (small, large):
            evidence = execution_profiles.capability_evidence(profile, AdapterDouble().describe(),
                observed_at=engine.runtime['last_observed_utc'])
            engine.instance.setdefault('capability_evidence', {})[evidence['id']] = evidence
        task = task_fixture()
        task.update(title='Fixed input recovery', status='active', work_class='nonformal', inputs=[], reuse=[], dependencies=[], basis_refs=[],
            authority_refs=['GR-research'], profile_refs=[execution_profiles.profile_ref(small), reference],
            model_assessment={'difficulty': 'high', 'importance': 'high', 'reason': 'Preserve the assigned requirement'},
            question='Inspect the following fixed evidence: ' + 'required evidence ' * 40000, results=[])
        from research_fixtures import supply_observation_rules
        extensions = {}
        supply_observation_rules([task], extensions)
        task['initial_observation_rules'] = extensions['task_conditions'][0]['observation_rules']
        engine.runtime['tasks'] = {task['id']: task}
        approve(task, engine.instance, engine.runtime)
        action = {'id': 'AC-overflow-work', 'role': 'research_work', 'target': task['id'],
            'profile_ref': execution_profiles.profile_ref(small), 'grant_id': 'GR-research',
            'selected_contract_sha256': planning.contract_hash(task), 'model_assessment': deepcopy(task['model_assessment'])}
        engine.runtime['queue'] = [action]
        engine._save()
        engine.run(max_steps=1)
        self.assertEqual(calls, [])
        held = engine.runtime['waiting_actions'][action['id']]
        self.assertEqual(held['next_owner'], 'research_plan', held)
        owner, question = held['action']['owner_activity_id'], held['question_id']
        engine.run(max_steps=1)
        self.assertEqual([row['role'] for row in calls], ['research_plan'])
        retry = next(row for row in engine.runtime['queue'] if row['id'] == action['id'])
        self.assertEqual(retry['profile_ref'], reference)
        self.assertEqual(retry['owner_activity_id'], owner)
        self.assertEqual(next(q for q in engine.runtime['question_links'] if q['id'] == question)['status'], 'open')
        engine.run(max_steps=1)
        self.assertEqual([row['role'] for row in calls], ['research_plan', 'research_work'])
        self.assertEqual(calls[-1]['profile_ref'], reference)
        self.assertEqual(calls[-1]['owner_activity_id'], owner)
        self.assertEqual(next(q for q in engine.runtime['question_links'] if q['id'] == question)['status'], 'resolved')
        attempts = [e for e in engine.runtime['executions'].values() if e.get('action', {}).get('id') == action['id']]
        self.assertEqual(len(attempts), 2)
        self.assertEqual(len({e['id'] for e in attempts}), 2)
        self.assertTrue(any(e.get('outcome') == 'output_accepted' for e in attempts))


if __name__ == '__main__':
    unittest.main(verbosity=2)
