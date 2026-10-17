"""Remaining receiver and recovery questions on real engines and existing port fakes.

These tests use registered executions and the current repository contract. They
stop at the receiver or cleanup decision; no engine method is replaced.
"""
from copy import deepcopy
from pathlib import Path
import tempfile
import unittest

from support.sim import Sim, warm_template

setUpModule = warm_template


class TargetedCorePaths(unittest.TestCase):
    def test_bundle_rejects_changed_academic_requirements_at_the_same_charter_revision(self):
        """T3 56.2 s cold: the actual solved-goal task, work input and new review establish both editions."""
        from do_math import academic, governance, integration
        from support.academic_scenes import consumer_sim, MANUSCRIPT, user_source
        from support.state_builders import charter_change
        from support.engine_lifecycle import approve, queue_work
        sim = consumer_sim()
        engine = sim.engine
        sim.run_until(lambda s: any(a['role'] == 'task_contract_review' and a.get('target') in s.runtime['tasks']
                      for a in s.runtime['queue']), max_steps=8)
        task = next(t for t in sim.runtime['tasks'].values() if t.get('academic_requirement_id'))
        approve(engine, task)
        action = queue_work(engine, task['id'])
        engine._save()
        prepared = engine._prepare_call(action)
        self.assertIsInstance(prepared, dict)
        eid, action = prepared['execution_id'], prepared['action']
        context, _ = engine._issued_input(engine.runtime['executions'][eid])
        output = {'summary': 'Report on the issued academic contract', 'questions': [], 'used_sources': []}
        bundle, = integration.split_bundles(output, {}, context)
        prior_hash = engine.runtime['executions'][eid]['academic_requirements_sha256']
        current_revision = governance.governance_view(engine.instance)['charter']['revision']
        proposal = charter_change(engine, academic_requirements=[{**MANUSCRIPT, 'criteria': ['Publish the bounded argument']}])
        proposal['record']['revision'] = current_revision
        instance, runtime, _ = governance.apply_decision(engine.instance, engine.runtime, proposal,
            source_ref=user_source(engine), clock=sim.clock)
        self.assertEqual(governance.governance_view(instance)['charter']['revision'], current_revision)
        self.assertNotEqual(academic.current_requirements(instance)['sha256'], prior_hash)
        # A current independent review may already have re-approved this same
        # task revision. It does not replace the old worker's requirement hash.
        from support.engine_lifecycle import _ended_execution
        from support.role_answers import review_items
        original = engine.instance, engine.runtime
        try:
            engine.instance, engine.runtime = instance, runtime
            _ended_execution(engine, 'EX-current-academic-review', 'task_contract_review')
            engine._apply({'role': 'task_contract_review', 'target': task['id']}, review_items([task['id']]),
                'EX-current-academic-review', owns_response=False)
        finally:
            engine.instance, engine.runtime = original
        before = deepcopy((engine.head, engine.instance, engine.runtime))
        with self.assertRaisesRegex(ValueError, '^academic requirements changed during execution$'):
            engine._validate_bundle_current(instance, runtime, bundle, action=action, execution_id=eid, context=context)
        self.assertEqual((engine.head, engine.instance, engine.runtime), before)

    def test_feedback_delivery_failure_preserves_the_accepted_operational_response(self):
        """T3 6.1 s: one live target and a captured review are needed to attempt feedback delivery."""
        from support.core_remaining import operational_scene
        from support.engine_control import running_work
        from support.submission_receiver import receive
        sim = Sim.activated()
        with running_work(sim) as call:
            scene = operational_scene(sim, call.execution_id, {'kind': 'continue', 'basis_refs': [call.execution_id],
                'next_owner': 'research_work', 'reason': 'Continue the original bounded task', 'next_review': None})
            engine = sim.engine
            destination = call.workspace / '.control' / 'observation-feedback.json'
            destination.unlink(missing_ok=True)
            destination.mkdir()
            received = receive(scene)
            engine._save()
            self.assertEqual(received['status'], 'accepted', received)
            stored = engine.store.load()[2]
            self.assertEqual(stored['executions'][scene.execution_id]['outcome'], 'output_accepted')
            self.assertEqual(stored['executions'][call.execution_id]['status'], 'running')
            failure, = [h for h in stored['history'] if h.get('kind') == 'feedback_delivery_failed']
            self.assertEqual(failure['execution_id'], scene.execution_id)
            self.assertTrue(failure['error'])
            self.assertEqual(engine._publish_control_request(scene.request)['publication_id'], scene.receipt['publication_id'])

    def test_local_repair_publication_failure_keeps_the_accepted_response_and_engine_owner(self):
        """T3 5.5 s: real rejected artifacts and an accepted diagnosis establish the local repair boundary."""
        import sys
        from do_math.engine import ResearchEngine
        from do_math.ports.git_backend import GitBackendError
        from support.core_remaining import operational_scene
        from do_math.execution_lifecycle import transition_execution
        from support.engine_lifecycle import clear_work
        from support.submission_receiver import history, receive
        failed_scene = history()
        sim = failed_scene.sim
        engine = sim.engine
        clear_work(sim)
        transition_execution(engine.runtime['executions'][failed_scene.execution_id], 'stopping', at=sim.clock.now())
        returned = engine._receive_submission(failed_scene.action, {'output': failed_scene.output},
            failed_scene.execution_id, failed_scene.context, failed_scene.schema, failed_scene.workspace)
        self.assertNotEqual(returned['status'], 'accepted')
        engine._save()
        scene = operational_scene(sim, failed_scene.execution_id, {'kind': 'repair', 'basis_refs': [failed_scene.execution_id],
            'next_owner': 'installation_recovery', 'reason': 'Repair the installed receiver',
            'repair_target': 'installation:scripts/do_math/core_engine.py', 'meaning_preserving': True,
            'verification': 'Run the direct receiver regression'})
        backend, failed = sim.ports.git_backend, []
        original = backend.update_ref
        def unavailable(repository, ref, new, old):
            frame = sys._getframe(1)
            while frame is not None:
                if frame.f_code is ResearchEngine.request_installation_repair.__code__:
                    failed.append((new, old))
                    raise GitBackendError('local repair publication unavailable')
                frame = frame.f_back
            return original(repository, ref, new, old)
        backend.update_ref = unavailable
        try:
            received = receive(scene)
        finally:
            del backend.update_ref
        engine._save()
        self.assertEqual(received['status'], 'accepted', received)
        self.assertEqual(len(failed), 1)
        stored = engine.store.load()[2]
        self.assertEqual(stored['executions'][scene.execution_id]['outcome'], 'output_accepted')
        interruption, = [h for h in stored['history'] if h.get('kind') == 'operational_repair_interrupted']
        self.assertEqual((interruption['execution_id'], interruption['next_owner'], interruption['reason']),
                         (scene.execution_id, 'engine', 'local repair publication unavailable'))
        record, = [r for r in stored['operational_dispositions'].values() if r['execution_id'] == scene.execution_id]
        self.assertEqual(record['status'], 'repair_required')
        self.assertEqual(engine._publish_control_request(scene.request)['publication_id'], scene.receipt['publication_id'])
        engine._run_pending_operational_repairs()
        record = engine.runtime['operational_dispositions'][record['id']]
        self.assertEqual(record['status'], 'installation_repair_pending')
        history = deepcopy([h for h in engine.runtime['history'] if h.get('kind') == 'operational_repair_interrupted'])
        engine._run_pending_operational_repairs()
        self.assertEqual([h for h in engine.runtime['history'] if h.get('kind') == 'operational_repair_interrupted'], history)

    def test_bundle_keeps_required_source_currentness_separate_from_reported_references(self):
        """T3 2.8 s: two public source editions and the archived author input establish currentness."""
        from do_math import integration
        from do_math.input_basis import capture_sources, CurrentnessChanged
        from support.engine_lifecycle import applied
        from support.submission_receiver import history
        sim = Sim.activated()
        source = sim.root / 'required-input.txt'
        source.write_bytes(b'original input')
        applied(sim, 'source', config={'path': str(source)})
        scene = history(sim=sim)
        engine = scene.engine
        execution = engine.runtime['executions'][scene.execution_id]
        execution['source_basis'] = capture_sources(engine.instance, [source.name])
        engine._save()
        basis = deepcopy(execution['source_basis'])
        self.assertEqual(execution.get('decision_basis', {}).get('sources', []), [])
        bundle, = integration.split_bundles(scene.output, {}, scene.context)
        engine._validate_bundle_current(deepcopy(engine.instance), deepcopy(engine.runtime), bundle,
            action=scene.action, execution_id=scene.execution_id, context=scene.context)
        source.write_bytes(b'changed required input')
        applied(sim, 'source', config={'path': str(source)})
        before = deepcopy((engine.head, engine.instance, engine.runtime))
        with self.assertRaises(CurrentnessChanged) as caught:
            engine._validate_bundle_current(deepcopy(engine.instance), deepcopy(engine.runtime), bundle,
                action=scene.action, execution_id=scene.execution_id, context=scene.context)
        self.assertEqual(caught.exception.changes,
            [{'field': 'sources', 'reason': 'required source content changed'}])
        self.assertEqual(engine.runtime['executions'][scene.execution_id]['source_basis'], basis)
        self.assertEqual((engine.head, engine.instance, engine.runtime), before)

    def test_bundle_rechecks_an_additional_issued_grant_without_revoking_the_execution_grant(self):
        """T3 2.5 s: actual grant decisions separate immutable authority history from a revocable grant."""
        from do_math import integration
        from support.engine_lifecycle import applied, grant
        from support.submission_receiver import history
        sim = Sim.activated()
        grant(sim.engine, 'GR-additional-bundle')
        scene = history(sim=sim)
        engine = scene.engine
        context = deepcopy(scene.context)
        context['grants'].append(deepcopy(engine.instance['grants']['GR-additional-bundle']))
        decision = next(iter(engine.instance['decisions'].values()))
        context['decisions'] = [deepcopy(decision)]
        output = deepcopy(scene.output)
        output['integration_bundles'][0]['authority_refs'].extend([decision['id'], 'GR-additional-bundle'])
        self.assertEqual(integration.inspect_bundles(output, {}, context), [])
        bundle, = integration.split_bundles(output, {}, context)
        engine._validate_bundle_current(deepcopy(engine.instance), deepcopy(engine.runtime), bundle,
            action=scene.action, execution_id=scene.execution_id, context=context)
        applied(sim, 'decision', config={'change': {'kind': 'revoke', 'grant_id': 'GR-additional-bundle'}})
        before = deepcopy((engine.head, engine.instance, engine.runtime))
        with self.assertRaisesRegex(ValueError, '^bundle authority is no longer current: GR-additional-bundle$'):
            engine._validate_bundle_current(deepcopy(engine.instance), deepcopy(engine.runtime), bundle,
                action=scene.action, execution_id=scene.execution_id, context=context)
        self.assertEqual((engine.head, engine.instance, engine.runtime), before)

    def test_plan_rejects_external_issued_input_without_the_fixed_population(self):
        """T3 3.7 s: the issued artifact and two external rewrites exercise the real reader."""
        from support.engine_context import issue
        from support.engine_lifecycle import _ended_execution, clear_work
        from support.submission_receiver import history
        from do_math.canonical import canonical_json
        from support.storage_git import rewrite_commit
        scene = history()
        engine = scene.engine
        clear_work(scene.sim)
        _ended_execution(engine, 'EX-fixed-plan', 'research_plan')
        execution = engine.runtime['executions']['EX-fixed-plan']
        execution['input_snapshot'] = engine.head
        fixed = {'snapshot': execution['input_snapshot'], 'tasks': [], 'ready_task_ids': []}
        issue(engine, execution, fixed, 'BA-fixed-plan')
        engine._save()
        base = engine.head
        path = 'runtime/artifacts/BA-fixed-plan/input/submission/context.json'
        # A changed artifact is an external storage input. Product saves refuse
        # to rewrite sealed bundles, so the external writer owns this mutation.
        for damaged in ({**fixed, 'snapshot': base}, {k: v for k, v in fixed.items() if k != 'ready_task_ids'}):
            engine.head = rewrite_commit(engine.store, base, {path: canonical_json(damaged)})
            before = deepcopy((engine.head, engine.instance, engine.runtime))
            with self.subTest(input=damaged), self.assertRaisesRegex(ValueError,
                    '^planning input is missing its fixed candidate population$'):
                engine._apply_plan({}, execution['id'])
            self.assertEqual((engine.head, engine.instance, engine.runtime), before)
            base = engine.head

    def test_preparation_rejects_a_formal_candidate_without_its_authoring_environment(self):
        """T3 0.4 s: a newly initialized store supplies the genuine absent author environment."""
        from support.engine_lifecycle import _ended_execution
        from support.role_answers import candidate
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        sim = Sim(directory.name)
        engine = sim.engine
        _ended_execution(engine, 'EX-no-formal-environment', 'research_preparation')
        execution = engine.runtime['executions']['EX-no-formal-environment']
        execution['input_snapshot'] = engine.head
        self.assertIsNone(engine.store.view(engine.head)[1].get('active_trust_environment'))
        before = deepcopy((engine.head, engine.instance, engine.runtime))
        bundle = {'integration_id': 'IN-no-formal-environment', 'output': {'candidates': [candidate(formal=True)]},
                  'extensions': {}, 'owns_response': False}
        with self.assertRaisesRegex(ValueError, '^formal task requires the trust environment supplied to its author$'):
            engine._apply_bundle_candidate(deepcopy(engine.instance), deepcopy(engine.runtime), bundle,
                action=execution['action'], execution_id=execution['id'], extensions={})
        self.assertEqual((engine.head, engine.instance, engine.runtime), before)

    def test_unresolved_kind_preparation_returns_to_its_independent_checker(self):
        """T3 3.3 s: actual proposal, independent unresolved verdict and preparation produce the follow-up."""
        from do_math.canonical import exact_content_hash
        from support.storage_kind_checks import kind_scene, propose_kinds, kind_checker
        from support.engine_lifecycle import _ended_execution
        from support.planning_contract_inputs import issue_preparation
        sim = kind_scene()
        engine = sim.engine
        propose_kinds(engine)
        check_action = next(a for a in engine.runtime['queue'] if a.get('kind_definition_id'))
        checker, definition = kind_checker(engine, check_action, 'EX-unresolved-kind')
        engine._remove_action(check_action)
        engine._apply_kind_definition_check(check_action, {'definition_id': definition['id'],
            'definition_sha256': exact_content_hash(definition), 'decision': 'unresolved',
            'findings': ['Need evidence before this meaning can be adopted']}, checker['id'])
        action, = [a for a in engine.runtime['queue'] if a['role'] == 'research_preparation'
                   and a.get('kind_definition_id') == definition['id']]
        _ended_execution(engine, 'EX-kind-preparation', 'research_preparation')
        execution = engine.runtime['executions']['EX-kind-preparation']
        execution.update(input_snapshot=engine.head, extensions={})
        issue_preparation(sim, execution)
        engine._remove_action(action)
        engine._apply(action, {'candidates': []}, execution['id'], owns_response=False)
        followup, = [a for a in engine.runtime['queue'] if a['role'] == 'maintenance'
                     and a.get('kind_definition_id') == definition['id']]
        self.assertEqual(followup['kind_definition_sha256'], exact_content_hash(engine.instance['kind_definitions'][definition['id']]))
        self.assertEqual(engine.instance['kind_definitions'][definition['id']]['status'], 'candidate')
        engine._save()
        self.assertEqual(engine.store.load()[2]['queue'], engine.runtime['queue'])

    def test_research_extensions_publish_relations_and_reusable_observation_rules(self):
        from do_math import knowledge_io, submission
        from jsonschema import Draft202012Validator
        from support.observation_inputs import observation_rule
        from support.record_builders import observation_knowledge
        from support.submission_receiver import research
        scene = research()
        engine = scene.engine
        ids = []
        for title in ('Extension premise', 'Extension consequence'):
            engine.instance, engine.runtime, kid = knowledge_io.import_candidate(
                engine.instance, engine.runtime, observation_knowledge(title),
                source_ref=scene.execution_id, actor_ref=scene.execution_id, clock=scene.sim.clock)
            ids.append(kid)
        rules = [observation_rule(subject_kind='iteration', subject_id=scene.execution_id,
                                  operator='iteration_gte', threshold=2, required_evidence=[ids[0]])]
        extension = {'relations': [{'kind': 'supports', 'source': ids[0], 'target': ids[1],
                                    'evidence': 'The supplied observations support this connection'}],
                     'observation_rules': rules}
        Draft202012Validator(submission.extension_schema(scene.action)).validate(extension)
        engine.runtime['executions'][scene.execution_id]['extensions'] = deepcopy(extension)
        engine._apply_extensions(scene.action, scene.execution_id)
        relation, = engine.instance['relations']
        self.assertEqual((relation['source'], relation['target']), tuple(ids))
        stored_rules = engine.runtime['task_observation_rules'][scene.task['id']]
        self.assertEqual(stored_rules[0]['subject']['id'], '$execution')
        self.assertEqual(rules[0]['subject']['id'], scene.execution_id)
        engine._save()
        _, saved, runtime = engine.store.load()
        self.assertEqual(saved['relations'], [relation])
        self.assertEqual(runtime['task_observation_rules'][scene.task['id']], stored_rules)

    def test_cleanup_preserves_a_user_scoped_execution_that_is_still_running(self):
        from support.engine_lifecycle import applied, clear_work, _ended_execution
        sim = Sim.activated()
        engine = sim.engine
        clear_work(sim)
        target = engine._register_execution({'id': 'AC-live-cleanup', 'role': 'maintenance'},
            {'id': 'EX-live-cleanup', 'role': 'maintenance', 'status': 'running'})
        workspace = Path(engine.instance['workspace']) / 'runs' / target['id'] / 'workspace'
        workspace.mkdir(parents=True)
        marker = workspace / 'ongoing.txt'
        marker.write_bytes(b'work in progress')
        engine._save()
        request = applied(sim, 'request', config={'role': 'maintenance',
                                                'cleanup_execution_ids': [target['id']]})
        action, = [a for a in engine.runtime['queue'] if a.get('requested_by') == request['request_id']]
        _ended_execution(engine, 'EX-cleanup-review', 'maintenance')
        engine._save()
        result = engine._maintenance_cleanup(action, 'EX-cleanup-review')
        self.assertEqual(result['deleted'], [])
        self.assertEqual(marker.read_bytes(), b'work in progress')
        self.assertEqual(engine.runtime['executions'][target['id']]['status'], 'running')
        self.assertEqual(engine.store.load()[2]['history'][-1]['result'], result)

    def test_resolved_failure_retires_its_queued_nonlive_operational_review(self):
        from do_math.wait_rules import waiting_action
        from support.engine_lifecycle import _ended_execution
        engine = Sim.activated().engine
        _ended_execution(engine, 'EX-old-failure', 'maintenance')
        _ended_execution(engine, 'EX-resolution', 'maintenance')
        old = engine.runtime['executions']['EX-old-failure']['action']
        engine.runtime.setdefault('waiting_actions', {})[old['id']] = waiting_action({
            'action': deepcopy(old), 'execution_id': 'EX-old-failure',
            'kind': 'execution_failure', 'reason': 'Preserved unfinished action'})
        engine._resolve_failed_actions(old, 'EX-resolution')
        reason = engine._obsolete_action_reason({'role': 'operational_review', 'target': 'EX-old-failure'})
        self.assertEqual(reason,
            'The failed action has already been resolved; its execution remains historical evidence')
        self.assertIsNone(engine._obsolete_action_reason({'role': 'operational_review', 'target': 'EX-resolution'}))

    def test_held_insight_keeps_its_author_when_the_original_input_cannot_be_read(self):
        from support.review_scene import ReviewScene
        from support.engine_lifecycle import _ended_execution
        from support.storage_records import INSTANCE_ID
        with tempfile.TemporaryDirectory() as directory:
            scene = ReviewScene(directory)
            engine = scene.engine
            engine.instance['id'] = INSTANCE_ID
            _ended_execution(engine, 'author', 'research_work')
            engine._save()
            cycle = scene.start()
            _, _, first = scene.execute(registered=True)
            author = engine.runtime['executions'][first]
            insight = {'kind': 'question', 'title': 'Held evidence question',
                'statement': 'What does the original evidence imply?', 'summary': 'Keep the uncertainty',
                'evidence_ids': ['K1']}
            author['extensions'] = {'research_insights': [deepcopy(insight)]}
            engine._apply_extensions(author['action'], first)
            engine._save()
            _, _, last = scene.execute(registered=True)
            engine._save()
            import shutil
            from do_math.engine import ResearchEngine
            backend = engine.ports.git_backend
            original_repository = engine.store.repository
            copy = Path(directory) / 'reader-repository'
            shutil.copytree(original_repository, copy)
            backend.objects[str((copy / '.git').absolute())] = dict(
                backend.objects[str((original_repository / '.git').absolute())])
            engine = ResearchEngine(copy, INSTANCE_ID, ports=engine.ports,
                codex_home=engine.codex_home, environment=engine.environment, host_id=engine.host_id)
            # A Git read outage of the original snapshot is an external failure,
            # while this release's current snapshot remains readable.
            from do_math.ports.git_backend import GitBackendError
            read_objects = backend.read_objects
            origin = engine.runtime['executions'][first]['input_snapshot']
            failures = []
            def unavailable(repository, specs):
                if any(spec.startswith(origin + ':') for spec in specs):
                    failures.append(list(specs))
                    raise GitBackendError('original insight snapshot unavailable')
                return read_objects(repository, specs)
            backend.read_objects = unavailable
            try:
                engine._apply_extensions(engine.runtime['executions'][last]['action'], last)
            finally:
                del backend.read_objects
            self.assertTrue(failures)
            record, = [r for r in engine.instance['knowledge'].values() if r.get('title') == insight['title']]
            self.assertEqual(record['producer_execution'], first)
            self.assertTrue(record['use_suspended'])
            self.assertIn('origin input could not be established:', record['use_suspensions'][0]['reason'])
            self.assertNotIn(cycle, engine.runtime['private_insights'])
