"""Connection regressions: real owner transitions, with explicit model/Lean doubles."""
from copy import deepcopy
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math import execution_profiles, review_cycle, review_policy, submission
from do_math.engine import ResearchEngine
from test_lifecycle_engine import FakeEngine, AdapterDouble


class FormalEngine(FakeEngine):
    _formal = ResearchEngine._formal
    _formal_steps = ResearchEngine._formal_steps
    _settle_activity = ResearchEngine._settle_activity
    _remove_action = ResearchEngine._remove_action


class FormalContinuationTests(unittest.TestCase):
    def make(self):
        adapter = patch('do_math.initialization.adapter_for', return_value=AdapterDouble())
        adapter.start()
        self.addCleanup(adapter.stop)
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        engine = FormalEngine(Path(directory.name))
        engine.activate()
        from do_math import knowledge_records
        engine.instance, _ = knowledge_records.create_candidate(engine.instance,
            {'id': 'K1', 'kind': 'lemma', 'statement': 'One equals one', 'summary': 'Reflexivity',
             'lean_code': 'theorem k1 : 1 = 1 := rfl', 'declaration_names': ['k1'], 'dependencies': []},
            source_ref='UI-source', actor_ref='EX-author')
        environment = engine._formal_environment()
        editions = execution_profiles.build_profiles({**engine.instance['config'],
            'lean_command': environment['toolchain']['configured_command']})
        engine.instance['execution_profiles'].update(editions['execution_profiles'])
        engine.instance['role_profile_refs']['formal_check'] = editions['role_profile_refs']['formal_check']
        action = {'id': 'AC-formal', 'role': 'formal_check', 'target': 'K1'}
        engine.runtime['queue'] = [action]
        return engine, action

    def test_pause_resume_retains_one_action_and_reaches_identity_review(self):
        engine, action = self.make()
        def pause(arguments):
            engine.control('pause', {})
            self.assertTrue(arguments['should_stop']())
            return {'status': 'stopped'}
        engine.formal_behavior = pause
        engine._formal(action)
        first = next(e for e in engine.runtime['executions'].values() if e['role'] == 'formal_check')
        self.assertEqual(first['status'], 'ended')
        pending = next(a for a in engine.runtime['queue'] if a['id'] == action['id'])
        self.assertEqual(pending['continuation_of'], first['id'])
        self.assertNotEqual(engine.runtime['activities'][first['owner_activity_id']]['status'], 'finished')
        engine.control('resume', {})
        engine.control('resume', {})
        self.assertEqual(sum(a.get('id') == action['id'] for a in engine.runtime['queue']), 1)
        engine.formal_behavior = None
        engine._formal(pending)
        attempts = [e for e in engine.runtime['executions'].values() if e['role'] == 'formal_check']
        self.assertEqual(len(attempts), 2)
        self.assertEqual(attempts[-1]['continuation_of'], first['id'])
        self.assertEqual(attempts[-1]['formal_status'], 'verified')
        self.assertTrue(any(a['role'] == 'identity_review' for a in engine.runtime['queue']))

    def test_close_preserves_the_ended_check_without_continuation(self):
        engine, action = self.make()
        def close(arguments):
            engine.control('close', {})
            return {'status': 'stopped'}
        engine.formal_behavior = close
        engine._formal(action)
        self.assertFalse(any(a.get('id') == action['id'] for a in engine.runtime['queue']))
        self.assertFalse(engine.runtime['waiting_actions'])

    def test_resume_rechecks_source_trust_and_authority_before_another_call(self):
        for changed in ('source', 'trust', 'authority'):
            with self.subTest(changed=changed):
                engine, action = self.make()
                def pause(arguments):
                    engine.control('pause', {})
                    return {'status': 'stopped'}
                engine.formal_behavior = pause
                engine._formal(action)
                engine.control('resume', {})
                continuation = next(a for a in engine.runtime['queue'] if a.get('id') == action['id'])
                if changed == 'source':
                    fid = engine.instance['knowledge']['K1']['formal_result_id']
                    engine.instance['formal_results'][fid]['lean_code'] += '\n-- changed candidate'
                elif changed == 'trust':
                    engine.instance['trust_environments'][engine.instance['active_trust_environment']]['status'] = 'inactive'
                else:
                    engine.instance['grants']['GR-research']['status'] = 'revoked'
                engine.formal_behavior = None
                engine._formal(continuation)
                self.assertEqual(len(engine.formal_calls), 1)


class ReviewScopeBudgetTests(unittest.TestCase):
    def test_exhaustion_drains_only_owned_attempts_before_publishing_followup(self):
        from do_math import execution_lifecycle
        case = FormalContinuationTests()
        engine, _ = case.make()
        self.addCleanup(case.doCleanups)
        engine.knowledge('K2')
        policy = engine._adopted_review_policy()
        limit = review_policy.minimum_scope_executions(2, policy['round_limit'])
        policy['activity_execution_limit'] = limit
        engine._adopted_review_policy = lambda: deepcopy(policy)
        engine.instance['knowledge']['K2']['scope_assessment'] = review_policy.default_scope_assessment(policy, ['one','two'])
        cid = engine._start_identity_review('K2')
        action = next(a for a in engine.runtime['queue'] if a.get('review_cycle_id') == cid)
        stamp = engine.current_time.isoformat()
        for number in range(limit):
            execution = engine._register_execution(action,
                {'id': f'EX-attempt-{number}', 'role': 'identity_review', 'status': 'queued'})
            if number < limit-1:
                execution_lifecycle.end_preparation(execution, at=stamp, stage='context', reason='fixture interrupted attempt', cancelled=True)
        last = execution['id']
        execution_lifecycle.transition_execution(execution, 'starting', at=stamp)
        execution_lifecycle.transition_execution(execution, 'running', at=stamp)
        unrelated = engine._register_execution({'id': 'AC-unrelated', 'role': 'maintenance'},
            {'id':'EX-unrelated','role':'maintenance','status':'running'})
        self.assertIsNone(engine._register_execution(action, {'id':'EX-denied','role':'identity_review','status':'queued'}))
        cycle = engine.runtime['review_cycles'][cid]
        self.assertEqual(review_cycle.resource_disposition(cycle)['state'], 'draining')
        self.assertEqual(engine.runtime['executions'][last]['stop_requested'], 'review_resource_disposition')
        self.assertNotIn('stop_requested', unrelated)
        self.assertFalse(any(a['role']=='research_plan' for a in engine.runtime['queue']))
        execution_lifecycle.transition_execution(execution, 'stopping', at=stamp, stop_phase='terminating')
        execution_lifecycle.transition_execution(execution, 'ended', at=stamp, outcome='execution_incomplete', disposition='fixture return')
        engine._settle_activity(last)
        self.assertEqual(cycle['status'], 'unresolved')
        self.assertEqual(engine.runtime['activities'][cycle['owner_activity_id']]['status'], 'finished')
        self.assertEqual(unrelated['status'], 'running')
        self.assertEqual(sum(a['role']=='research_plan' for a in engine.runtime['queue']), 1)
        self.assertEqual(review_cycle.validate_sealed_review(cycle, engine.runtime)['decision'], 'unresolved')

    def test_completed_legacy_review_replays_without_a_retroactive_admission_floor(self):
        import do_math.review_engine as owner
        from test_review_engine import FakeEngine as ReviewFixture
        with tempfile.TemporaryDirectory() as directory:
            engine = ReviewFixture(directory)
            engine.instance['review_policy']['activity_execution_limit'] = 2
            engine.instance['config']['review_scope_assessment']['activity_execution_limit'] = 2
            start = review_cycle.start_review
            with patch.object(owner, 'start_review', side_effect=lambda *a, **kw:
                    start(*a, **kw, enforce_execution_minimum=False)):
                cid = engine._start_identity_review('K1')
            engine.execute()
            engine.execute()
            replay = review_cycle.validate_sealed_review(engine.runtime['review_cycles'][cid],
                engine.runtime, instance=engine.instance)
            self.assertEqual(replay['decision'], 'match')

    def test_floor_counts_scope_and_mandatory_followup(self):
        for rounds, required in [(1, 8), (2, 14), (4, 14)]:
            with self.subTest(rounds=rounds):
                policy = review_policy.build_review_policy(None, reviewer_count=3, max_rounds=rounds)
                scope = review_policy.default_scope_assessment(policy, ['one', 'two', 'three'])
                scope['activity_execution_limit'] = required - 1
                with self.assertRaisesRegex(ValueError, 'at least'):
                    review_policy.validate_scope_assessment(scope, policy, executions_used=1)
                scope['activity_execution_limit'] = required
                self.assertEqual(review_policy.validate_scope_assessment(scope, policy,
                    executions_used=1)['activity_execution_limit'], required)

    def test_scope_context_exposes_actual_attempt_usage(self):
        cycle = review_cycle.start_review({'revision': 1}, 2)
        cycle['execution_accounting']['executions_used'] = ['EX-first', 'EX-retry']
        visible = review_cycle.context_for(cycle, review_cycle.next_actions(cycle)[0])
        self.assertEqual(visible['scope_executions_used'], 2)
        self.assertEqual(visible['minimum_scope_execution_limit'], 13)

    def test_unaffordable_scope_returns_to_plan_without_fabricating_a_judgment(self):
        for disposition in ('unresolved', 'defer'):
            with self.subTest(disposition=disposition):
                case = FormalContinuationTests()
                engine, _ = case.make()
                self.addCleanup(case.doCleanups)
                engine.knowledge('K2')
                policy = engine._adopted_review_policy()
                policy.update(activity_execution_limit=1, overflow_disposition=disposition)
                engine._adopted_review_policy = lambda: deepcopy(policy)
                cid = engine._start_identity_review('K2')
                action = next(a for a in engine.runtime['queue'] if a.get('review_cycle_id') == cid)
                before = deepcopy(engine.instance['identity_assessments'])
                result = engine._register_execution(action, {'id': 'EX-unstarted', 'role': 'identity_review', 'status': 'queued'})
                self.assertIsNone(result)
                self.assertNotIn('EX-unstarted', engine.runtime['executions'])
                cycle = engine.runtime['review_cycles'][cid]
                record = review_cycle.validate_resource_disposition(cycle, engine.runtime)
                self.assertEqual(record['state'], 'ended' if disposition == 'unresolved' else 'deferred')
                self.assertEqual(engine.instance['identity_assessments'], before)
                plans = [a for a in engine.runtime['queue'] if a['role'] == 'research_plan']
                self.assertEqual(len(plans), 1)
                self.assertIn(cid, plans[0]['evidence_refs'])
                self.assertEqual(review_cycle.next_actions(cycle), [])
                engine._settle_review_resource_dispositions()
                self.assertEqual(len([a for a in engine.runtime['queue'] if a['role'] == 'research_plan']), 1)
                if disposition == 'unresolved':
                    self.assertEqual(review_cycle.validate_sealed_review(cycle, engine.runtime)['decision'], 'unresolved')


class TransferReferenceTests(unittest.TestCase):
    def test_nonready_recipient_uses_separate_fixed_reference_population(self):
        from test_redesign_TASKS import AssessmentApplicationTests
        from do_math.task_scope import apply_task_assessments
        instance, runtime, assessment = AssessmentApplicationTests().fixture()
        selected_population = {'TK-1': deepcopy(runtime['tasks']['TK-1'])}
        original = deepcopy(runtime['tasks'])
        _, changed = apply_task_assessments(instance, runtime, [assessment], execution_id='EX-plan',
            input_tasks=selected_population, reference_tasks=original)
        self.assertEqual(changed['tasks']['TK-2']['completion_obligations'][-1]['id'], 'OB-inherited')
        self.assertEqual(set(selected_population), {'TK-1'})
        for mutate in (lambda r: r['tasks']['TK-2'].update(revision=2),
                       lambda r: r['tasks']['TK-2'].update(status='closed'),
                       lambda r: r['executions'].update({'EX-peer': {'status': 'running', 'action': {'target': 'TK-2'}}})):
            candidate = deepcopy(runtime)
            mutate(candidate)
            with self.assertRaises(ValueError):
                apply_task_assessments(instance, candidate, [assessment], execution_id='EX-plan',
                    input_tasks=selected_population, reference_tasks=original)
        with self.assertRaisesRegex(ValueError, 'recipient'):
            apply_task_assessments(instance, runtime, [assessment], execution_id='EX-plan',
                input_tasks=selected_population, reference_tasks=selected_population)


class FixedResearchReferenceTests(unittest.TestCase):
    def test_fixed_sources_and_collectable_workspace_paths(self):
        self.assertIsNone(submission.fixed_research_reference_path('proposal', {'proposal'}))
        self.assertEqual(submission.fixed_research_reference_path('workspace:result.txt', {'proposal'}), 'result.txt')
        for reference in ['KN-unassigned', 'workspace:../escape', 'workspace:input/source.txt',
                          'workspace:C:/escape', 'workspace:.scratch/discarded.txt']:
            with self.subTest(reference=reference), self.assertRaises(ValueError):
                submission.fixed_research_reference_path(reference, {'proposal'})


class HostConfigurationTests(unittest.TestCase):
    def test_uncapped_lean_demands_can_be_omitted(self):
        from do_math.engine import validate_config
        config = self.configuration()
        for role in ('formal_check', 'trust_check', 'trust_activate'):
            config['host_resources']['demands_by_role'].pop(role)
        validate_config(config)
        profiles = execution_profiles.build_profiles(config)['execution_profiles']
        self.assertTrue(all('host_resources' not in p for p in profiles.values()
            if p['role'] in {'formal_check','trust_check','trust_activate'}))
        config['host_resources']['demands_by_role'].pop('research_work')
        with self.assertRaisesRegex(ValueError, 'capped role'):
            validate_config(config)

    def test_unstarted_role_defaults_refresh_while_task_profiles_require_preparation(self):
        from do_math.engine import DEFAULT_CONFIG
        from do_math.initialization import initialize_state
        from do_math.governance_engine import GovernanceEngineMixin
        from do_math.contracts import task_candidate_record
        from v5_fixtures import candidate
        with tempfile.TemporaryDirectory() as directory:
            config = {**deepcopy(DEFAULT_CONFIG), 'scholarly_enabled': False}
            instance, runtime = initialize_state(instance_id='RI-host-change', goal='Test profiles', goal_kind='research',
                workspace=Path(directory), config=config, source_input='Test profiles', created_at='2026-09-23T00:00:00Z')
            instance.update(execution_profiles.build_profiles(config))
            old = deepcopy(instance['role_profile_refs']['maintenance'][0])
            wire = candidate()
            wire['profile_refs'] = [deepcopy(instance['role_profile_refs']['research_work'][0])]
            task = task_candidate_record(wire, task_id='TK-pinned')
            task.update(status='planned', results=[], reviews=[])
            runtime['tasks'][task['id']] = task
            runtime['queue'] = [{'id':'AC-default','role':'maintenance','profile_ref':old}]
            changed, state = GovernanceEngineMixin()._configure_candidate(instance, runtime,
                {'config':{'host_resources':self.configuration()['host_resources']}})
            pending = next(a for a in state['queue'] if a['id']=='AC-default')
            self.assertNotEqual(pending['profile_ref'], old)
            self.assertEqual(state['tasks'][task['id']]['profile_refs'], task['profile_refs'])
            self.assertTrue(any(task['id'] in a.get('revision_targets', {}) for a in state['queue']))

    def configuration(self):
        import platform
        from do_math.engine import DEFAULT_CONFIG
        settings = {**deepcopy(DEFAULT_CONFIG), 'scholarly_enabled': False}
        roles = execution_profiles.build_profiles(settings)['role_profile_refs']
        host = execution_profiles.host_constraint(host_id=platform.node(),
            limits={'jobs': 4, 'memory_bytes': 536870912, 'cpu_rate_basis_points': 8000},
            control_reserve={'jobs': 1, 'memory_bytes': 134217728, 'cpu_rate_basis_points': 2000},
            authority_refs=['configuration:request'])
        settings['host_resources'] = {'constraint': host, 'demands_by_role': {role:
            {'jobs': 1, 'memory_bytes': 134217728, 'cpu_rate_basis_points': 2000} for role in roles}}
        return settings

    def test_public_init_configure_and_removal_in_both_budget_modes(self):
        import subprocess
        from do_math.engine import initialize
        from do_math.governance_engine import GovernanceEngineMixin
        from do_math.repository import ResearchRepository
        for sessions in (True, False):
            with self.subTest(sessions=sessions), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                subprocess.run(['git', '-C', str(root), 'init', '-q'], check=True)
                settings = self.configuration()
                if not sessions: settings['session_limits'] = None
                else:
                    settings.pop('model')
                    settings.pop('operator_model')
                created = initialize(root, goal='Temporary configuration test', workspace=root/'workspace', config=settings)
                store = ResearchRepository(root, created['instance_id'])
                head, instance, runtime = store.load()
                host_id = instance['host_capacity_ref']
                approval = instance['capacity_constraints'][host_id]['authority_refs'][0]
                self.assertEqual(instance['governance_sources'][approval]['origin'], 'user')
                self.assertNotEqual(approval, 'configuration:request')
                host = GovernanceEngineMixin()
                same, state = host._configure_candidate(instance, runtime, {'config': {'host_resources': settings['host_resources']}})
                self.assertEqual(same['host_capacity_ref'], host_id)
                with self.assertRaisesRegex(ValueError, 'user'):
                    host._configure_candidate(instance, runtime, {'origin': 'operator', 'config': {'host_resources': None}})
                held = deepcopy(runtime)
                held['executions']['EX-live'] = {'status': 'queued'}
                with self.assertRaisesRegex(ValueError, 'stopped'):
                    host._configure_candidate(instance, held, {'config': {'host_resources': None}})
                removed, state = host._configure_candidate(instance, runtime, {'config': {'host_resources': None}})
                self.assertNotIn('host_capacity_ref', removed)
                self.assertIn(host_id, removed['capacity_constraints'])
                saved = store.save(head, removed, state)
                self.assertIsNone(store.load(saved)[1]['config']['host_resources'])
                for profile in same['execution_profiles'].values():
                    if profile['role'] in {'formal_check', 'trust_check', 'trust_activate'}:
                        self.assertNotIn('host_resources', profile)


class PartialCaptureTests(unittest.TestCase):
    def test_only_independent_local_errors_can_be_captured(self):
        from do_math import contracts
        from test_redesign_CONTRACTS import response, context
        from do_math.repository import canonical_json
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            visible = {**context(), 'execution_id': 'EX-partial'}
            schema = contracts.action_schema(visible['action'], visible['kind_definitions'])
            submission.install_tools(workspace, visible, schema, None)
            output = response()
            output['knowledge'][1]['dependencies'] = ['KN-not-supplied']
            def seal(value):
                return submission.seal_submission(workspace, execution_id='EX-partial', context=visible,
                    schema=schema, max_artifact_bytes=1024*1024, raw_output=canonical_json(value))
            sealed = seal(output)
            self.assertFalse(sealed['passed'])
            self.assertTrue(sealed['capture_eligible'], sealed['check']['issues'])
            self.assertEqual(sealed['artifacts']['output.json'], canonical_json(output))
            all_bad = deepcopy(output)
            all_bad['knowledge'][0]['dependencies'] = ['KN-not-supplied']
            self.assertFalse(seal(all_bad)['capture_eligible'])
            connected = deepcopy(output)
            connected['knowledge'][1]['dependencies'] = ['A']
            self.assertFalse(seal(connected)['capture_eligible'])
            malformed = deepcopy(output)
            malformed.pop('report')
            self.assertFalse(seal(malformed)['capture_eligible'])


class PartialCaptureGitTests(unittest.TestCase):
    def setUp(self):
        from test_submission_flow import CentralSubmissionHistoryTests
        from do_math import contracts, knowledge_io, planning
        from do_math.input_basis import capture_decision_basis
        from do_math.repository import canonical_json
        from test_redesign_CONTRACTS import response
        CentralSubmissionHistoryTests.setUp(self)
        action = {'id': 'AC-partial', 'role': 'research_work'}
        self.engine._action_lifecycle_gate(action)
        execution = self.engine._register_execution(action, {'id': 'EX-partial', 'role': 'research_work', 'status': 'running'})
        from v5_fixtures import candidate
        from types import SimpleNamespace
        wire = candidate()
        wire['profile_refs'] = [execution['execution_profile_ref']]
        wire['authority_refs'] = [action['grant_id']]
        task = contracts.task_candidate_record(wire, task_id='TK-partial')
        task.pop('revises_task_id', None)
        task.update(status='planned', results=[], reviews=[], occurrence_condition={'op': 'always'})
        self.engine.runtime['tasks'][task['id']] = task
        reviewer = {'id': 'AC-review', 'role': 'task_contract_review', 'target': task['id']}
        self.engine._register_execution(reviewer, {'id': 'EX-review', 'role': 'task_contract_review', 'status': 'running'})
        FakeEngine.approve(SimpleNamespace(instance=self.engine.instance, runtime=self.engine.runtime), task)
        action['target'] = task['id']
        execution['action']['target'] = task['id']
        execution['contract_sha256'] = planning.contract_hash(task)
        self.engine._save()
        execution = self.engine.runtime['executions']['EX-partial']
        execution.update(grant_id=action['grant_id'], input_bundle='BA-partial-input', input_snapshot=self.engine.head,
            decision_basis=capture_decision_basis(self.engine.instance, self.engine.runtime, []),
            **planning.governance_revisions(self.engine.instance))
        self.workspace = Path(self.engine.instance['workspace'])/'runs/EX-partial/workspace'
        self.workspace.mkdir(parents=True)
        self.context = {'action': action, 'execution_id': 'EX-partial', 'snapshot': self.engine.head,
            'tasks': [deepcopy(task)], 'sources': [], 'knowledge_catalog': [],
            'kind_definitions': knowledge_io.catalog_definitions(self.engine.instance),
            'grants': [deepcopy(self.engine.instance['grants'][action['grant_id']])]}
        self.schema = contracts.action_schema(action, self.context['kind_definitions'])
        submission.install_tools(self.workspace, self.context, self.schema, None)
        self.engine._save({'runtime/artifacts/BA-partial-input/input/submission/context.json': canonical_json(self.context),
                           'runtime/artifacts/BA-partial-input/schema.json': canonical_json(self.schema)})
        self.binding = self.transport.issue('EX-partial', action['grant_id'], workspace=self.workspace)
        self.output = response()
        # The independent A record can be imported without the returned report's
        # task disposition; this fixture intentionally tests the capture seam.
        self.output['integration_bundles'][0]['members'].remove('output')
        self.output['integration_bundles'][1]['members'].append('output')
        self.output['knowledge'][1]['dependencies'] = ['KN-not-supplied']

    def test_early_submission_preview_reload_and_partial_application(self):
        from do_math.repository import canonical_json
        execution = self.engine.runtime['executions']['EX-partial']
        raw = canonical_json(self.output)
        (self.workspace/'draft.json').write_bytes(raw)
        head = self.engine.head
        preview = self.engine._preview_submission(execution, {'draft_path': 'draft.json'})
        self.assertEqual(self.engine.head, head)
        self.assertEqual([row['status'] for row in preview['bundles']], ['preview_passed', 'returned'], preview)
        request = {**self.binding, 'request_id': 'CT-partial', 'kind': 'submit_intent', 'payload': {'draft_path': 'draft.json'}}
        receipt = self.transport.receive(request, publish=self.engine._publish_control_request)
        self.assertEqual(receipt['state'], 'accepted', receipt)
        self.engine = ResearchEngine(self.repo, self.identifier)
        execution = self.engine.runtime['executions']['EX-partial']
        sealed = submission.read_sealed_submission(execution, self.engine.head, lambda s,p: self.engine.store.read(p,s))
        self.assertFalse(sealed['check']['passed'])
        self.assertEqual(self.engine._submission_check_summary(self.engine.head, self.engine.runtime)['status'], 'verified')
        applied = self.engine._apply_submission_bundles(execution['action'], sealed['output'], sealed['extensions'],
            execution['id'], self.context, sealed['check']['issues'])
        self.assertEqual([row['status'] for row in applied['bundles']], ['accepted', 'returned'], applied['issues'])
        repeated = self.engine._apply_submission_bundles(execution['action'], sealed['output'], sealed['extensions'],
            execution['id'], self.context, sealed['check']['issues'])
        self.assertEqual(repeated['bundles'][0]['status'], 'already_accepted')

    def test_native_final_reaches_the_same_partial_candidate(self):
        from test_native_final_submission import native_result
        from do_math.repository import canonical_json
        execution = self.engine.runtime['executions']['EX-partial']
        result = native_result(execution, self.context, canonical_json(self.output), self.workspace)
        captured = self.engine._collect_submitted_result(execution, result, self.context, self.schema, self.workspace)
        self.assertEqual(captured['collection'], 'sealed_submission', captured)
        self.assertNotIn('rejected_submission', captured)
        received = self.engine._receive_submission(execution['action'], captured, execution['id'], self.context,
                                                   self.schema, self.workspace, preserved=True)
        self.assertEqual([row['status'] for row in received['bundles']], ['accepted', 'returned'], received['issues'])


class ReviewOverflowGitTests(unittest.TestCase):
    def setUp(self):
        from test_input_recovery import InputRecoveryPublicTests
        InputRecoveryPublicTests.setUp(self)

    def test_actual_proposal_overflow_ends_preparation_and_reaches_plan_input(self):
        import json
        from do_math import knowledge_records, context_store
        engine = ResearchEngine(self.repo, self.identifier)
        source = 'theorem overflow : 1 = 1 := rfl'
        engine.instance, _ = knowledge_records.create_candidate(engine.instance, {
            'id': 'KN-overflow', 'kind': 'lemma', 'title': 'Overflow fixture', 'statement': 'One equals one', 'summary': 'Large explanation',
            'explanation': 'This is preserved explanation evidence. ' * 35000,
            'lean_code': source, 'declaration_names': ['overflow'], 'dependencies': []},
            source_ref=engine.instance['lifecycle']['input_id'], actor_ref=next(iter(engine.runtime['executions'])))
        environment = engine._formal_environment()
        result = FakeEngine.verification(engine, source, ['overflow'], environment['toolchain'])
        engine.instance = knowledge_records.record_formal_result(engine.instance, 'KN-overflow', result,
            environment['id'], runtime=engine.runtime)
        engine._save()
        cid = engine._start_identity_review('KN-overflow')
        action = next(a for a in engine.runtime['queue'] if a.get('review_cycle_id') == cid)
        with self.assertRaises(StopIteration):
            next(engine._call_steps(action))
        cycle = engine.runtime['review_cycles'][cid]
        event = review_cycle.resource_disposition(cycle)
        self.assertIsNotNone(event)
        self.assertEqual(event['reason'], 'review_input_overflow')
        execution = engine.runtime['executions'][event['detail']['execution_id']]
        self.assertEqual((execution['status'], execution['input_preparation']['stage']), ('ended', 'packing'))
        self.assertNotIn('process', execution)
        for entry in execution['input_manifest']['direct']:
            self.assertTrue(engine.store.read(entry['artifact_ref'], engine.head))
        self.assertFalse(any(q.get('blocks') for q in engine.runtime.get('question_links', [])))
        plan = next(a for a in engine.runtime['queue'] if a['role'] == 'research_plan')
        workspace = Path(engine.instance['workspace'])/'plan-input'
        workspace.mkdir()
        context = engine._context(plan, workspace, execution_id='EX-plan-input')
        profile = engine._execution_profile(plan)
        fitted = context_store.prepare_role_input(context, instance=engine.instance, runtime=engine.runtime,
            role='research_plan', profile=profile, snapshot=engine.head, workspace=workspace,
            activity_id='AY-plan-input', artifact_prefix='runtime/artifacts/BA-plan-input')
        followup = fitted['validation_context']['review_followups'][0]
        self.assertEqual(followup['id'], cid)
        restored = json.loads((workspace/followup['source_ref']['path']).read_bytes())
        self.assertEqual(restored['proposal_digest'], cycle['proposal_digest'])
        self.assertEqual(restored['history'], cycle['history'])
        self.assertIn(cid, submission.assessment_reference_ids(fitted['validation_context']))
        restarted = ResearchEngine(self.repo, self.identifier)
        self.assertEqual(restarted.runtime['review_cycles'][cid]['status'], 'unresolved')

    def test_public_pause_restart_resume_preserves_formal_attempt_lineage(self):
        from do_math import knowledge_records
        from v5_fixtures import send_control
        engine = ResearchEngine(self.repo, self.identifier)
        environment = engine._formal_environment()
        engine.instance['config']['lean_command'] = environment['toolchain']['configured_command']
        editions = execution_profiles.build_profiles(engine.instance['config'])
        engine.instance['execution_profiles'].update(editions['execution_profiles'])
        engine.instance['role_profile_refs']['formal_check'] = editions['role_profile_refs']['formal_check']
        engine.instance, _ = knowledge_records.create_candidate(engine.instance, {
            'id': 'KN-formal-resume', 'kind': 'lemma', 'title': 'Resume fixture',
            'statement': 'One equals one', 'summary': 'Reflexivity',
            'lean_code': 'theorem resume_fixture : 1 = 1 := rfl', 'declaration_names': ['resume_fixture'],
            'dependencies': []}, source_ref=engine.instance['lifecycle']['input_id'],
            actor_ref=next(iter(engine.runtime['executions'])))
        engine._enqueue('formal_check', 'KN-formal-resume')
        engine._save()
        def pause(**arguments):
            send_control(engine, 'pause', config={})
            self.assertTrue(arguments['should_stop']())
            return {'status': 'stopped', 'reason': 'Explicit test pause; no Lean process'}
        engine.formal_verifier = pause
        engine._formal(next(a for a in engine.runtime['queue'] if a['role'] == 'formal_check'))
        first = next(e for e in engine.runtime['executions'].values() if e['role'] == 'formal_check')
        self.assertEqual(first['status'], 'ended')
        restarted = ResearchEngine(self.repo, self.identifier)
        send_control(restarted, 'resume', config={})
        action = next(a for a in restarted.runtime['queue'] if a['role'] == 'formal_check')
        self.assertEqual(action['continuation_of'], first['id'])
        restarted.formal_verifier = lambda **kw: FakeEngine.verification(restarted,
            kw['source'], kw['declarations'], kw['expected_toolchain'])
        restarted._formal(action)
        final = ResearchEngine(self.repo, self.identifier)
        attempts = [e for e in final.runtime['executions'].values() if e['role'] == 'formal_check']
        self.assertEqual(len(attempts), 2)
        self.assertTrue(any(e.get('continuation_of') == first['id'] and e['formal_status'] == 'verified' for e in attempts))
        self.assertTrue(any(a['role'] == 'identity_review' for a in final.runtime['queue']))


if __name__ == '__main__':
    unittest.main()
