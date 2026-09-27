"""Role inputs: what the context producer packages for each role, and the checks at that boundary.

Model answers are fixtures. The context producer, input manifests, restored
sources and submission checks are the product's.
"""
import hashlib
import json
import sys
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path
from unittest.mock import create_autospec, Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math import (contracts, execution_profiles, integration, knowledge_io, knowledge_records, planning,
                     submission)
from do_math.configuration import DEFAULT_CONFIG
from do_math.context_store import fit_context, prepare_role_input
from do_math.repository import canonical_json, ResearchRepository
from engine_fixtures import context_engine, package, routing_engine
from knowledge_fixtures import verified_knowledge
from purpose_fixtures import ActivatedPurposeHarness, candidate, common as purpose_common
from record_fixtures import approve_task, approved_task, surface_state, task_disposition
from research_fixtures import governance_start, seal_response
from review_fixtures import defer_review_for_research, ReviewFakeEngine
from runner_fixtures import common


class OperationalInputTests(unittest.TestCase):
    def fixture(self):
        engine = context_engine()
        engine._documents['operational_review'] = contracts.prompt_documents('operational_review')
        target = {'id': 'EX-work', 'role': 'research_work', 'status': 'running',
                  'action': {'role': 'research_work', 'target': 'TK-work'}}
        engine.runtime['executions'][target['id']] = target
        value = {'current_claim': 'The exact source passed the preview.', 'evidence_paths': ['proof.lean'],
                 'attempts': ['checked'], 'remaining_work': ['central verification'],
                 'next_step': 'submit', 'progress_state': 'ready_to_submit'}
        raw = (json.dumps(value) + '\n').encode()
        checkpoint = {'kind': 'worker_checkpoint', 'execution_id': target['id'], 'status': 'valid',
            'value': value, 'artifact_ref': 'runtime/artifacts/BA-check/checkpoint.json',
            'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)}
        engine.runtime['checkpoints'] = {target['id']: checkpoint}
        engine.store.read.return_value = raw
        action = {'id': 'AC-review', 'role': 'operational_review', 'target': target['id'],
                  'live': True, 'observation_refs': ['OF-one'], 'obligation_ids': ['SC-one']}
        return engine, action, checkpoint, raw

    def test_live_review_receives_the_already_sealed_target_checkpoint(self):
        engine, action, checkpoint, raw = self.fixture()
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            context = engine._context(action, workspace, execution_id='EX-review')
            evidence = context.get('operational_evidence', {})
            self.assertEqual(evidence.get('checkpoint'), {k: v for k, v in checkpoint.items() if k != 'value'})
            source = evidence['checkpoint_source']
            self.assertEqual((workspace / source['local_path']).read_bytes(), raw)
            self.assertEqual(source['sha256'], checkpoint['sha256'])

    def test_large_checkpoint_stays_readable_without_becoming_mandatory_prompt_text(self):
        from do_math.context_store import prepare_role_input
        engine, action, checkpoint, _ = self.fixture()
        checkpoint['value']['current_claim'] = 'Evidence retained. ' * 40000
        raw = json.dumps(checkpoint['value']).encode()
        checkpoint.update(sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw))
        engine.store.read.return_value = raw
        profile = next(p for p in engine.instance['execution_profiles'].values() if p['role'] == 'operational_review')
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            context = engine._context(action, root, execution_id='EX-review')
            fitted = prepare_role_input(context, instance=engine.instance, runtime=engine.runtime,
                role='operational_review', profile=profile, snapshot=engine.head, workspace=root,
                activity_id='AY-review', install_submission_tools=True)
            self.assertIsNone(fitted['overflow'], 'Checkpoint text is available through its exact file reference')
            source = fitted['context']['operational_evidence']['checkpoint_source']
            self.assertEqual((root / source['local_path']).read_bytes(), raw)

    def test_review_gets_the_same_canonical_basis_set_as_application(self):
        engine, action, checkpoint, raw = self.fixture()
        with tempfile.TemporaryDirectory() as directory:
            context = engine._context(action, Path(directory), execution_id='EX-review')
            self.assertEqual(set(context.get('admissible_basis_refs', [])),
                             {'EX-work', 'OF-one', 'SC-one', checkpoint['artifact_ref']})

    def test_live_review_receives_exact_checkpoint_evidence_files(self):
        engine, action, checkpoint, raw = self.fixture()
        proof = b'theorem proof (n : Nat) : n + 0 = n := rfl\n'
        source = {'path': 'proof.lean', 'artifact_ref': 'runtime/artifacts/BA-check/proof.lean',
                  'sha256': hashlib.sha256(proof).hexdigest(), 'bytes': len(proof)}
        checkpoint['evidence_files'] = [source]
        engine.store.read.side_effect = lambda path, snapshot: proof if path == source['artifact_ref'] else raw
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            context = engine._context(action, root, execution_id='EX-review')
            files = context['operational_evidence'].get('checkpoint_files', [])
            self.assertEqual(len(files), 1)
            self.assertEqual((root / files[0]['local_path']).read_bytes(), proof)

    def test_assigned_role_uses_exact_registry_references_even_below_input_limit(self):
        from do_math.context_store import fit_context, read_source
        engine, _, _, _ = self.fixture()
        profiles = list(engine.instance['execution_profiles'].values())
        context = {'action': {'role': 'research_work'}, 'task': {'id': 'TK-one', 'question': 'Fixed'},
                   'execution_profiles': profiles, 'role_profile_refs': engine.instance['role_profile_refs'],
                   'tasks': [{'id': 'TK-one', 'question': 'Fixed'}] * 10}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result = fit_context(context, max_bytes=10_000_000, workspace=root,
                                 mandatory_keys=['task'], role='research_work')
            self.assertIsInstance(result['context']['execution_profiles'], dict,
                                  'The already assigned role need not repeatedly inline the full registry')
            ref = result['context']['execution_profiles']['source_ref']
            self.assertEqual(json.loads(read_source(root, ref)['bytes']), profiles)
            self.assertEqual(result['context']['task'], context['task'])
            self.assertLess(result['actual_bytes'], result['original_bytes'])

    def test_packaged_operational_submission_checks_the_advertised_basis(self):
        from do_math.context_store import prepare_role_input
        from do_math.submission import payload_issues
        engine, action, _, _ = self.fixture()
        profile = next(p for p in engine.instance['execution_profiles'].values() if p['role'] == 'operational_review')
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            context = engine._context(action, root, execution_id='EX-review')
            fitted = prepare_role_input(context, instance=engine.instance, runtime=engine.runtime,
                role='operational_review', profile=profile, snapshot=engine.head, workspace=root,
                activity_id='AY-review', install_submission_tools=True)
            fixed = fitted['validation_context']
            output = {'summary': 'Review', 'used_sources': ['EX-work'], 'questions': [],
                'disposition': {'kind': 'continue', 'basis_refs': ['EX-work'], 'next_owner': 'engine',
                                'reason': 'The preserved checkpoint is available.', 'next_review': None}}
            schema = contracts.schema_for('operational_review')
            self.assertEqual(payload_issues(output, schema, fixed, {}, root), [])
            output['disposition']['basis_refs'].append('input/catalog/observation.json')
            issues = payload_issues(output, schema, fixed, {}, root)
            self.assertTrue(any('invalid_basis_refs' in row['message'] for row in issues), issues)

    def test_changed_checkpoint_file_bytes_are_rejected_before_review(self):
        engine, action, _, _ = self.fixture()
        engine.store.read.return_value = b'changed bytes'
        with tempfile.TemporaryDirectory() as directory, self.assertRaisesRegex(ValueError, 'checkpoint hash'):
            engine._context(action, Path(directory), execution_id='EX-review')


class InputConnections(unittest.TestCase):
    def test_fixed_question_is_packaged_and_answer_returns_to_its_seat(self):
        engine = ReviewFakeEngine(self.enterContext(tempfile.TemporaryDirectory()))
        cid = defer_review_for_research(engine)
        action = next(a for a in engine.runtime['queue'] if a['role'] == 'supplemental_research')
        root = engine.root / 'packaged-investigation'
        context = {'action': deepcopy(action), **engine._review_research_context(action, root)}
        instance, _ = surface_state()
        # The fake engine starts from governance_start's families; the adopted charter
        # comes from surface_state, so each family keeps the records of both.
        instance.update({**engine.instance, **{family: {**instance[family], **engine.instance[family]}
                                                for family in governance_start()}})
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
        execution = {'id': 'INV-answer', 'role': 'supplemental_research', 'status': 'running', 'action': action,
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


class RoleInputBoundaryTests(unittest.TestCase):
    def test_large_task_catalog_moves_to_fixed_source_without_shrinking_selection(self):
        catalog = [{'id': 'TK-past', 'title': 'Earlier result', 'report': 'failure' * 1000}]
        context = {'tasks': [{'id': 'TK-ready'}], 'ready_task_ids': ['TK-ready'],
                   'ongoing_work': [{'execution_id': 'EX-active', 'reason': 'still checking'}],
                   'task_catalog': catalog}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fitted = fit_context(context, max_bytes=1000, workspace=root,
                                 mandatory_keys=['tasks', 'ready_task_ids', 'ongoing_work'],
                                 role='research_plan')
            self.assertIsNone(fitted['overflow'])
            self.assertEqual(fitted['context']['ready_task_ids'], ['TK-ready'])
            self.assertEqual(fitted['context']['ongoing_work'], context['ongoing_work'])
            ref = fitted['context']['task_catalog']['source_ref']
            raw = (root / ref['path']).read_bytes()
            self.assertEqual(submission.load_json(raw), catalog)
            self.assertEqual((ref['sha256'], ref['bytes']), (hashlib.sha256(raw).hexdigest(), len(raw)))

    def test_planning_keeps_completed_report_and_active_work_as_readable_context(self):
        selected, instance, runtime = approved_task()
        finished = deepcopy(selected)
        finished.update(id='TK-finished-context', title='Earlier failed approach', status='completed',
                        results=[{'execution_id': 'EX-finished-context',
                                  'report': 'The previous approach fails at the boundary case.',
                                  'output_files': []}])
        active = deepcopy(selected)
        active.update(id='TK-active-context', title='Current investigation', status='active', results=[])
        runtime['tasks'][finished['id']] = finished
        runtime['tasks'][active['id']] = active
        runtime['executions']['EX-active-context'] = {
            'id': 'EX-active-context', 'role': 'research_work', 'status': 'running',
            'action': {'id': 'AC-active-context', 'role': 'research_work', 'target': active['id'],
                       'reason': 'Investigate the open case'}, 'input_snapshot': 'a' * 40,
            'private_draft': 'unpublished judgment'}
        engine = context_engine(instance, runtime)
        source = b'fixture source for task context\n'
        engine.instance['sources'][0]['sha256'] = hashlib.sha256(source).hexdigest()
        engine.store.read.return_value = source
        approve_task(selected, engine.instance, engine.runtime)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fitted, fixed = package(engine, root)
            self.assertEqual(fixed['ready_task_ids'], [selected['id']])
            self.assertEqual({row['id'] for row in fixed['tasks']},
                             {selected['id'], finished['id'], active['id']})
            catalog = {row['id']: row for row in fixed['task_catalog']}
            self.assertEqual(set(catalog), {selected['id'], finished['id'], active['id']})
            report = submission.load_json((root / catalog[finished['id']]['source_ref']['path']).read_bytes())
            self.assertEqual(report['results'][0]['report'], finished['results'][0]['report'])
            self.assertTrue(any(row.get('execution_id') == 'EX-active-context' and
                                row.get('target') == active['id'] for row in fixed['ongoing_work']))
            self.assertNotIn('unpublished judgment', json.dumps(fixed['ongoing_work']))
            submission.validate_reference(finished['id'], fixed, root)
            self.assertEqual(fitted['manifest']['candidate_order']['ids'], [selected['id']])

    def test_manifest_batch_read_keeps_exact_validation_and_missing_bindings(self):
        from do_math.context_store import verify_manifest_artifacts
        engine = context_engine()
        with tempfile.TemporaryDirectory() as directory:
            fitted, _ = package(engine, Path(directory))
            manifest, artifacts = fitted['manifest'], fitted['artifacts']
            batch = Mock(side_effect=lambda paths: {path: artifacts[path] for path in paths})
            single = Mock(side_effect=AssertionError('batch must not fall back to per-file processes'))
            expected = verify_manifest_artifacts(manifest, artifacts.__getitem__)
            self.assertEqual(verify_manifest_artifacts(manifest, single, read_artifacts=batch), expected)
            batch.assert_called_once()
            single.assert_not_called()
            unbound = deepcopy(manifest); unbound['direct'][0].pop('artifact_ref')
            self.assertEqual(verify_manifest_artifacts(unbound, single, read_artifacts=batch),
                             verify_manifest_artifacts(unbound, artifacts.__getitem__))
            artifacts[manifest['prompt']['artifact_ref']] = b'corrupt'
            for reader in ({}, {'read_artifacts': batch}):
                with self.assertRaisesRegex(ValueError, 'input artifact bytes differ'):
                    verify_manifest_artifacts(manifest, artifacts.__getitem__, **reader)

    def test_catalog_keeps_aliases_identity_and_only_effective_summaries(self):
        evidence, _, kid, aid = verified_knowledge()
        # Two effective assessments for the same item must not repeat its text.
        evidence, _ = knowledge_records.record_identity_assessment(evidence, kid,
            {'decision': 'match', 'basis': knowledge_records.identity_basis(evidence, kid)}, 'policy:2', runtime={})
        engine = context_engine(evidence)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _, fixed = package(engine, root)
            row = fixed['knowledge_catalog'][0]
            self.assertIn(aid, row['identity_assessment_ids'])
            self.assertEqual(row['path'], 'input/knowledge/' + kid + '.json')
            self.assertEqual(len(row['verified_summaries']), 1)
            self.assertEqual(row['verified_summaries'][0]['text'], row['summary'])
            submission.validate_reference(aid, fixed, root)
            self.assertEqual(submission.reported_references({'used_sources': [row['path']]}, {}, fixed), [kid])
            from do_math.input_basis import capture_decision_basis, decision_basis_changes
            refs = submission.reported_references({'used_sources': [row['path']]}, {}, fixed)
            basis = capture_decision_basis(engine.instance, engine.runtime, refs)
            changed = deepcopy(engine.instance)
            changed['expositions'][row['exposition_id']]['items'][0]['text'] += ' changed'
            self.assertTrue(decision_basis_changes(basis, changed, engine.runtime))
            for use in engine.instance['assessment_uses'].values():
                use['status'] = 'withdrawn'
            _, withdrawn = package(engine, root / 'withdrawn')
            changed = withdrawn['knowledge_catalog'][0]
            self.assertEqual(changed['verified_summaries'], [])
            self.assertFalse(changed['usable_as_k'])
            self.assertEqual(changed['summary'], row['summary'])
            self.assertEqual(changed['path'], row['path'])

    def artifact_engine(self):
        task, instance, runtime = approved_task()
        raw = b'valid evidence\n'
        instance['sources'][0]['sha256'] = hashlib.sha256(raw).hexdigest()
        task['occurrence_condition'] = {'op': 'artifact_valid', 'artifact_ref': {
            'snapshot': 'a' * 40, 'path': 'runtime/artifacts/BA-evidence/proof.txt',
            'sha256': hashlib.sha256(raw).hexdigest()}}
        approve_task(task, instance, runtime)
        engine = context_engine(instance, runtime)
        engine.store.read.return_value = raw
        return engine, task

    def test_artifact_candidate_survives_packaging_and_population_stays_fixed(self):
        engine, task = self.artifact_engine()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fitted, fixed = package(engine, root)
            self.assertEqual(fixed['ready_task_ids'], [task['id']])
            self.assertEqual(fixed['observed_at'], fixed['submission_contract']['basis_time'])
            self.assertEqual(fitted['manifest']['candidate_order']['ids'], [task['id']])
            output = {**common('research_plan'), 'dispositions': [task_disposition(task['id'])]}
            (root / 'activity-extensions.json').write_bytes(canonical_json({'model_assessments': [{
                'task_id': task['id'], 'difficulty': 'low', 'importance': 'low',
                'reason': 'The selected fixture task has bounded evidence and scope.'}]}))
            seal_response(output, fixed, root)
            draft = root / 'draft.json'; draft.write_bytes(canonical_json(output))
            check = submission.producer_check(root, draft)
            self.assertTrue(check['passed'], check['issues'])
            original = deepcopy(engine.runtime)
            engine.store.load.return_value = (engine.head, deepcopy(engine.instance), original)
            engine.store.view.return_value = engine.store.load.return_value
            frozen = canonical_json(fixed)
            evidence = engine.store.read.return_value
            task_sources = {row['source_ref']['artifact_ref']: (root / row['source_ref']['path']).read_bytes()
                            for row in fixed['task_catalog']}
            engine.store.read.side_effect = lambda path, head: (
                frozen if path.endswith('/context.json') else task_sources.get(path, evidence))
            engine.runtime['executions']['EX-plan'] = {'id': 'EX-plan', 'role': 'research_plan', 'status': 'ended',
                'action': fixed['action'], 'input_snapshot': engine.head, 'input_bundle': 'BA-plan'}
            extra = deepcopy(task); extra['id'] = 'TK-later'; engine.runtime['tasks'][extra['id']] = extra
            engine.instance['grants']['GR-later'] = {**deepcopy(engine.instance['grants']['GR-1']),
                                                     'id': 'GR-later', 'task_ids': [extra['id']]}
            extra['authority_refs'] = ['GR-later']
            approve_task(extra, engine.instance, engine.runtime)
            engine._apply_plan(output, 'EX-plan')
            self.assertEqual([a['target'] for a in engine.runtime['queue']], [task['id']])

    def test_selected_candidate_still_requires_current_authority(self):
        engine, task = self.artifact_engine()
        with tempfile.TemporaryDirectory() as directory:
            _, fixed = package(engine, Path(directory))
            output = {**common('research_plan'), 'dispositions': [task_disposition(task['id'])]}
            engine.store.load.return_value = (engine.head, deepcopy(engine.instance), deepcopy(engine.runtime))
            engine.instance['grants']['GR-1']['status'] = 'revoked'
            execution = {'input_snapshot': engine.head, 'extensions': {}, 'goal_revision': 1, 'policy_revision': 1}
            with self.assertRaisesRegex(ValueError, 'changed|current'):
                engine._validate_decision_acceptance(fixed['action'], output, execution, fixed,
                                                     evaluation_context=engine._evaluation_context())

    def test_missing_population_is_input_error(self):
        engine = context_engine()
        profile = next(p for p in engine.instance['execution_profiles'].values() if p['role'] == 'research_plan')
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError, 'fixed ready_task_ids'):
                prepare_role_input({'action': {'role': 'research_plan'}, 'resources': {}, 'knowledge_catalog': []},
                    instance=engine.instance, runtime=engine.runtime, role='research_plan', profile=profile,
                    snapshot=engine.head, workspace=Path(directory), activity_id='AC-1')

    def test_delivered_identity_receipt_can_complete_only_its_current_task(self):
        from record_fixtures import specialist_assessment
        for mutation in (None, 'foreign', 'withdrawn'):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as directory:
                state, runtime, assessment, kid, aid = specialist_assessment()
                # These source bytes are irrelevant to this specialist obligation.
                state['sources'] = []
                engine = context_engine(state, runtime)
                root = Path(directory)
                _, fixed = package(engine, root)
                output = {**common('research_plan'), 'task_assessments': [assessment]}
                seal_response(output, fixed, root)
                draft = root / 'draft.json'; draft.write_bytes(canonical_json(output))
                check = submission.producer_check(root, draft)
                self.assertTrue(check['passed'], check['issues'])
                engine.store.load.return_value = (engine.head, deepcopy(engine.instance), deepcopy(engine.runtime))
                engine.store.view.return_value = engine.store.load.return_value
                task_sources = {row['source_ref']['artifact_ref']: (root / row['source_ref']['path']).read_bytes()
                                for row in fixed['task_catalog']}
                engine.store.read.side_effect = lambda path, head: task_sources.get(path, canonical_json(fixed))
                engine.runtime['executions']['EX-plan'].update(input_snapshot=engine.head, input_bundle='BA-plan')
                if mutation == 'foreign':
                    engine.instance['knowledge'][kid]['task_id'] = 'TK-other'
                elif mutation == 'withdrawn':
                    engine.instance = knowledge_records.set_assessment_use(engine.instance, aid, 'withdrawn', 'recheck', 'reviewer')
                if mutation:
                    with self.assertRaises(ValueError):
                        engine._apply_plan(output, 'EX-plan')
                else:
                    engine._apply_plan(output, 'EX-plan')
                    self.assertEqual(engine.runtime['tasks']['TK-1']['status'], 'completed')

    def relation_engine(self):
        state, _, kid, aid = verified_knowledge()
        template = next(t for t in knowledge_io.relation_templates() if t['token'] == 'formally_implies')
        state, token = knowledge_io.register_kind_definition(state, template, source_ref='fixture', actor_ref='author')
        state = knowledge_io.check_kind_definition(state, 'relation', token, check_ref='check', actor_ref='checker')
        state = knowledge_io.activate_kind_definition(state, 'relation', token, approval_ref='review', actor_ref='reviewer')
        fid = state['knowledge'][kid]['formal_result_id']
        claim = {'kind': token, 'source': kid, 'target': kid, 'confirmed_scope': 'reflexive'}
        state['identity_assessments'][aid]['relation_claim'] = claim
        relation = {**claim, 'formal_result_refs': [fid], 'assessment_refs': [aid], 'evidence_refs': [kid], 'evidence': kid}
        return context_engine(state), relation, aid

    def test_relation_uses_sealed_domain_records_at_local_and_central_check(self):
        engine, relation, aid = self.relation_engine()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fitted, fixed = package(engine, root, 'research_work')
            output = {**common('research_work'), 'outcome': 'submitted', 'report': 'Reflexive relation'}
            extensions = {'relations': [relation]}
            (root / 'activity-extensions.json').write_bytes(canonical_json(extensions))
            seal_response(output, fixed, root)
            draft = root / 'draft.json'; draft.write_bytes(canonical_json(output))
            check = submission.producer_check(root, draft)
            self.assertTrue(check['passed'], check['issues'])
            sealed = submission.seal_submission(root, 'draft.json', execution_id='EX-plan',
                context=fixed, schema=contracts.schema_for('research_work'), max_artifact_bytes=2000000)
            self.assertTrue(sealed['passed'], sealed['check']['issues'])
            artifacts = engine._input_artifacts('BA-plan', contracts.schema_for('research_work'), fitted, root)
            self.assertIn('runtime/artifacts/BA-plan/input/submission/relation-state.json', artifacts)
            stopped = knowledge_records.set_assessment_use(engine.instance, aid, 'withdrawn', 'recheck', 'reviewer')
            with self.assertRaisesRegex(ValueError, 'invalid relation'):
                knowledge_io.import_relation(stopped, relation, source_ref='submission', actor_ref='EX-plan')
            for key, wrong in [('target', 'KN-absent'), ('confirmed_scope', 'different')]:
                bad = deepcopy(extensions); bad['relations'][0][key] = wrong
                self.assertTrue(submission.payload_issues(output, contracts.schema_for('research_work'), fixed, bad, root))
            (root / fixed['relation_validation_source']['path']).write_bytes(b'{}')
            issues = submission.payload_issues(output, contracts.schema_for('research_work'), fixed, extensions, root)
            self.assertTrue(any('input is missing or corrupt' in row['message'] for row in issues), issues)


class InputManifestConnections(unittest.TestCase):
    def test_delivered_previous_hashes_pass_the_actual_live_impact_gate(self):
        from record_fixtures import surface_state
        from research_fixtures import candidate
        from do_math import contracts, knowledge_io, knowledge
        engine = routing_engine(); engine.instance, engine.runtime = surface_state()
        engine.instance.update(relations=[], goal_status="unresolved")
        engine.runtime.update(inputs=[], questions=[])
        engine.instance, engine.runtime, kid = knowledge_io.import_candidate(engine.instance, engine.runtime,
            {"kind": "observation", "title": "Record", "statement": "A bounded observation", "summary": "Observed",
                "explanation": "Exact e\u0301 source", "lean_code": "", "declaration_names": [], "dependencies": []},
            source_ref="EX-author", actor_ref="EX-author")
        task = contracts.task_candidate_record(candidate("bounded work"), task_id="TA-one")
        task.update(status="candidate", results=[])
        engine.runtime["tasks"][task["id"]] = task
        engine.head = "fixed-input"; engine.store = create_autospec(ResearchRepository, instance=True); engine.store.read_many.return_value = {}
        engine._documents = {"maintenance": contracts.prompt_documents("maintenance")}
        engine._preparation_checkpoint = create_autospec(engine._preparation_checkpoint); engine._academic_status = create_autospec(engine._academic_status, return_value={"status": "not_evaluated"})
        with tempfile.TemporaryDirectory() as temporary:
            engine.instance["workspace"] = temporary
            context = engine._context({"id": "AC-reader", "role": "maintenance"}, Path(temporary) / "reader")
        rows = {row["id"]: row for field in ("knowledge_catalog", "tasks") for row in context[field]}
        for identifier, record in ((kid, engine.instance["knowledge"][kid]), (task["id"], task)):
            self.assertEqual(rows[identifier]["content_sha256"], knowledge.content_hash(record))
        engine.runtime["executions"]["EX-producer"] = {"id": "EX-producer", "input_snapshot": engine.head}
        bundle = {"integration_id": "IN-edit", "payload_sha256": "a" * 64, "members": ["activity-extensions.json/knowledge_changes/0"],
            "previous_hashes": {kid: rows[kid]["content_sha256"]}, "impact_set": [], "output": {},
            "extensions": {"knowledge_changes": [{"id": kid, "changes": {"summary": "Refined observation"}, "impact_set": []}]}}
        request = integration.bundle_impact_request(engine.instance, engine.runtime, bundle,
            producer_execution_id="EX-producer", input_snapshot=engine.head)
        self.assertIn("bundle", request["plans"])

    def test_input_artifacts_preserve_the_exact_role_manifest_and_catalog(self):
        from record_fixtures import surface_state
        from do_math import contracts
        from do_math.context_store import prepare_role_input
        engine = routing_engine()
        engine.instance, engine.runtime = surface_state()
        profile = next(row for row in engine.instance["execution_profiles"].values() if row["role"] == "maintenance")
        engine._documents = {"maintenance": contracts.prompt_documents("maintenance")}
        schema = contracts.schema_for("maintenance")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            context = {"action": {"role": "maintenance"}, "execution_id": "EX-maintenance"}
            # The engine archives each role input once, below its input bundle.
            fitted = prepare_role_input(context, instance=engine.instance, runtime=engine.runtime,
                role="maintenance", profile=profile, snapshot="a" * 40, workspace=root,
                activity_id="AC-1", output_schema=schema, documents=engine._documents["maintenance"],
                artifact_prefix="runtime/artifacts/BA-input")
            artifacts = engine._input_artifacts("BA-input", schema, fitted, root)
            self.assertEqual(json.loads(artifacts["runtime/artifacts/BA-input/manifest.json"]), fitted["manifest"])
            self.assertEqual(artifacts["runtime/artifacts/BA-input/input.txt"], fitted["prompt"].encode("utf-8"))
            for entry in fitted["manifest"]["catalog"]:
                raw = artifacts["runtime/artifacts/BA-input/" + entry["path"]]
                self.assertEqual(hashlib.sha256(raw).hexdigest(), entry["sha256"])


class PreparedInputTests(unittest.TestCase):
    def test_continuation_preserves_older_files_and_latest_replacements(self):
        from do_math.context_store import restore_continuation
        raw = {"old": b"old proof", "new": b"new proof", "notes": b"old notes", "result-first": b"first", "result-second": b"second"}
        def entry(path, ref): return {"path": path, "artifact_ref": ref, "sha256": hashlib.sha256(raw[ref]).hexdigest(), "bytes": len(raw[ref])}
        runtime = {"executions": {
            "EX-first": {"id": "EX-first", "role": "research_work", "status": "ended", "owner_activity_id": "AY-one", "continuation_of": None,
                "result_ref": "result-first", "output_files": [entry("proof.lean", "old"), entry("notes.txt", "notes")]},
            "EX-second": {"id": "EX-second", "role": "research_work", "status": "ended", "owner_activity_id": "AY-one", "continuation_of": "EX-first",
                "result_ref": "result-second", "output_files": [entry("proof.lean", "new")]}}}
        action = {"role": "research_work", "continuation_of": "EX-second"}
        with tempfile.TemporaryDirectory() as temporary:
            context = restore_continuation(runtime, action, Path(temporary), snapshot="fixed", read_artifact=raw.__getitem__)
            self.assertEqual({row["path"]: row["artifact_ref"] for row in context["previous_output_files"]}, {"proof.lean": "new", "notes.txt": "notes"})
            self.assertEqual([row["execution_id"] for row in context["continuation_history"]], ["EX-first", "EX-second"])
            self.assertEqual((Path(temporary) / "input/previous-output/proof.lean").read_bytes(), b"new proof")
            runtime["executions"]["EX-first"]["continuation_of"] = "EX-second"
            with self.assertRaisesRegex(ValueError, "cycle"):
                restore_continuation(runtime, action, Path(temporary), snapshot="fixed", read_artifact=raw.__getitem__)

    def test_discard_records_cancelled_preparation_and_explicit_continuation(self):
        from do_math import execution_lifecycle
        engine = routing_engine()
        with tempfile.TemporaryDirectory() as temporary:
            engine.instance["workspace"] = temporary
            engine.instance["config"] = deepcopy(DEFAULT_CONFIG)
            engine.instance.update(execution_profiles.build_profiles(DEFAULT_CONFIG))
            action = {"id": "AC-one", "role": "research_preparation"}
            engine.runtime["queue"] = [action]
            execution = engine._register_execution(action, {"id": "EX-one", "role": action["role"], "status": "queued"})
            execution_lifecycle.begin_preparation(execution, at="2026-09-20T00:00:00+00:00")
            base = Path(temporary) / "runs/EX-one"
            base.mkdir(parents=True)
            (base / "partial").write_text("incomplete private input")
            engine._save = create_autospec(engine._save)
            engine._discard_prepared_input(base, "EX-one")
            ended = engine.runtime["executions"]["EX-one"]
            self.assertEqual(ended["outcome"], "cancelled")
            self.assertEqual(engine.runtime["queue"][0]["continuation_of"], "EX-one")
            self.assertEqual(engine.runtime["queue"][0]["owner_activity_id"], ended["owner_activity_id"])
            self.assertFalse(base.exists())
            engine._save.assert_called()

    def test_runner_takes_its_tools_only_from_the_pinned_profile(self):
        from provider_fixtures import Adapter, runner_with
        from research_fixtures import dispatched_launch
        profile = next(p for p in execution_profiles.build_profiles(DEFAULT_CONFIG)["execution_profiles"].values()
                       if p["role"] == "research_work")
        tools = execution_profiles.runner_tools(profile)
        prompt = execution_profiles.prepare_prompt("fixture", profile)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            adapter = Adapter({"result": "output_collected", "final": {"raw": b"{}"}, "jsonl": {}})
            runner = runner_with(adapter)
            options = dict(prompt=prompt, input_seal=execution_profiles.prompt_seal(prompt), output_schema={},
                workspace=root, model=profile["ai"]["model"].removeprefix("claude:"), effort=profile["ai"]["effort"],
                timeout_seconds=1, execution_id="EX-tools", profile=profile,
                launch_ticket=dispatched_launch("EX-tools", profile))
            runner.run(**options, evidence_dir=root / "evidence")
            self.assertEqual(adapter.request.get("scholarly_server"), tools["scholarly_server"])
            for name, value in (("scholarly_server", {"command": "changed", "args": []}),
                                ("claude_only_assigned_model", False)):
                with self.subTest(name=name), self.assertRaisesRegex(ValueError, "pinned profile supplies"):
                    runner.run(**options, evidence_dir=root / name, **{name: value})


class ArchivedControlInputTests(unittest.TestCase):
    def test_large_control_is_archived_before_reference_catalog_construction(self):
        from engine_fixtures import FakeEngine
        from research_fixtures import FixtureAdapter
        from do_math.context_store import prepare_role_input
        with tempfile.TemporaryDirectory() as directory, patch('do_math.initialization.adapter_for', return_value=FixtureAdapter()):
            root = Path(directory)
            owner = FakeEngine(root); owner.activate()
            import base64
            request = {'id':'UC-large','action':'source','origin':'user','config':{
                'name':'large-notes.txt','body_base64':base64.b64encode(b'notes ' * 20000).decode('ascii')}}
            context = {'action':{'id':'AC-test','role':'maintenance'},'execution_id':'EX-test',
                       'recent_history':[{'kind':'user_control','request':request}]}
            profile = next(p for p in owner.instance['execution_profiles'].values() if p['role']=='maintenance')
            result = prepare_role_input(context, instance=owner.instance, runtime=owner.runtime, role='maintenance',
                profile=profile, snapshot='a'*40, workspace=root/'input-case', activity_id='AY-test',
                install_submission_tools=True, max_artifact_bytes=1000000)
            validation = result['validation_context']
            ref = validation['recent_history'][0]['request_source_ref']
            self.assertEqual(json.loads((root/'input-case'/ref['path']).read_bytes()), request)
            self.assertLess(len(canonical_json(validation['recent_history'])), 1000)
            self.assertLess(len(validation['reference_catalog']), 20)


class FollowupDocumentTests(ActivatedPurposeHarness):
    def test_planning_roles_receive_the_complete_current_settings(self):
        from do_math.context_store import prepare_role_input
        engine, _ = self.make_active(observation_interval_seconds=417, review_research_limit=4)
        for role in ("research_preparation", "research_plan"):
            workspace = self.root / role
            context = engine._context({"role": role}, workspace)
            # The engine projects no raw configuration; the role input preserves it from state.
            self.assertNotIn("config", context)
            profile = next(p for p in engine.instance["execution_profiles"].values() if p["role"] == role)
            fitted = prepare_role_input(context, instance=engine.instance, runtime=engine.runtime, role=role,
                profile=profile, snapshot=engine.head, workspace=workspace, activity_id="AC-" + role)
            source = fitted["context"]["configuration_source"]
            self.assertEqual(json.loads((workspace / source["path"]).read_bytes()), engine.instance["config"])

    def test_prepared_observation_rule_reaches_contract_review(self):
        engine, _ = self.make_active()
        from unittest.mock import create_autospec
        from do_math.execution_profiles import profile_ref
        # The preparations' issued inputs fix which task inputs they could name; these name none.
        engine._issued_input = create_autospec(engine._issued_input, return_value=(
            {"available_input_refs": [], "supplied_record_ids": []}, None))
        def proposal(title, **kwargs):
            value=candidate(title, **kwargs)
            value['profile_refs']=[profile_ref(p) for p in engine.instance['execution_profiles'].values()
                                   if p['role']=='research_work']
            return value
        rule = {"id": "branches", "operator": "counter_gte", "threshold": 3,
                "subject": {"kind": "counter", "id": "branches"},
                "basis": {"source": "checkpoint", "unit": "count"},
                "repeat_interval": 3, "required_evidence": ["EV-branch"]}
        engine.runtime["executions"]["EX-preparation"] = {"status": "ended", "input_snapshot": engine.head, "extensions": {"task_conditions": [
            {"task_title": "Bounded branch investigation", "observation_rules": [rule]}]}}
        engine._apply({"role": "research_preparation"},
                      {**purpose_common("Prepare an observable investigation"), "candidates": [proposal("Bounded branch investigation")]},
                      "EX-preparation")
        task = next(iter(engine.runtime["tasks"].values()))
        self.assertEqual(task.get("initial_observation_rules"), [rule])
        review = next(a for a in engine.runtime["queue"] if a["role"] == "task_contract_review")
        context = engine._context(review, self.root / "review-input")
        self.assertEqual(context["task"]["initial_observation_rules"], [rule])
        changed = deepcopy(task)
        changed["initial_observation_rules"][0]["threshold"] = 30
        self.assertNotEqual(planning.contract_hash(task), planning.contract_hash(changed))

        engine.runtime["task_observation_rules"] = {task["id"]: [rule]}
        revised_rule = {**rule, "threshold": 5}
        engine.runtime["executions"]["EX-revision"] = {"status": "ended", "input_snapshot": engine.head, "extensions": {"task_conditions": [
            {"task_title": task["title"], "observation_rules": [revised_rule]}]}}
        engine._apply({"role": "research_preparation"},
                      {**purpose_common("Revise the observation boundary"), "candidates": [proposal(task["title"], revises=task["id"])]},
                      "EX-revision")
        self.assertEqual(engine.runtime["tasks"][task["id"]]["initial_observation_rules"], [revised_rule])
        self.assertNotIn(task["id"], engine.runtime["task_observation_rules"],
                         "rules from an earlier contract must not override the new reviewed initial rules")

    def test_old_rejected_preparation_remains_readable_after_recent_history_moves(self):
        engine, _ = self.make_active()
        output = {**purpose_common("Investigated the earlier approach"), "candidates": [candidate("Earlier proposal")]}
        result = canonical_json({"status": "completed", "output": output, "error": None})
        reference = "runtime/artifacts/BA-old/result.json"
        from do_math.execution_lifecycle import transition_execution
        action = {"id": "AC-old", "role": "research_preparation"}
        engine._action_lifecycle_gate(action)
        old = engine._register_execution(action, {"id": "EX-old", "role": "research_preparation", "status": "running"})
        # Synthetic historical result, with actual actor/activity record shape.
        old.update(artifact_bundle="BA-old", result_ref=reference,
                   error="output validation: earlier proposal omitted its required source")
        at = engine._lifecycle_now().isoformat()
        transition_execution(old, "stopping", at=at)
        transition_execution(old, "ended", at=at, outcome="execution_incomplete")
        engine.runtime["history"] = [{"role": "maintenance", "summary": "Unrelated later event"} for _ in range(20)]
        engine._save({reference: result})
        workspace = self.root / "later-preparation"
        context = engine._context({"role": "research_preparation"}, workspace)
        self.assertIn("preparation_history", list(context))
        earlier = next(row for row in context["preparation_history"] if row["execution_id"] == "EX-old")
        self.assertEqual(earlier["outcome"], "execution_incomplete")
        self.assertIn("required source", earlier["error"])
        raw = (workspace / earlier["local_path"]).read_bytes()
        self.assertEqual(raw, result)
        self.assertEqual(earlier["sha256"], hashlib.sha256(raw).hexdigest())
        self.assertEqual(json.loads(raw)["output"], output)


if __name__ == "__main__":
    unittest.main()
