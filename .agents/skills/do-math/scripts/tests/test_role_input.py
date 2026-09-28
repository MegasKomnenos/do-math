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
        from do_math.context_store import fit_context, input_class, read_source
        engine, _, _, _ = self.fixture()
        profiles = list(engine.instance['execution_profiles'].values())
        context = {'action': {'role': 'research_work'}, 'task': {'id': 'TK-one', 'question': 'Fixed'},
                   'execution_profiles': profiles, 'role_profile_refs': engine.instance['role_profile_refs'],
                   'tasks': [{'id': 'TK-one', 'question': 'Fixed'}] * 10}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result = fit_context(context, max_bytes=10_000_000, workspace=root, mandatory_keys=['task'],
                                 role='research_work', map_keys=[key for key in context
                                                                 if input_class('research_work', key) == 'map'])
            self.assertEqual(set(result['context']['tasks']), {'source_ref', 'total'})
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

    def test_every_advertised_basis_ref_passes_the_submission_check(self):
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
            advertised = fixed['admissible_basis_refs']
            self.assertTrue({'OF-one', 'SC-one'} <= set(advertised), advertised)
            output = {'summary': 'Review', 'used_sources': list(advertised), 'questions': [],
                'disposition': {'kind': 'continue', 'basis_refs': list(advertised), 'next_owner': 'engine',
                                'reason': 'The observation opened a review of a progressing run.', 'next_review': None}}
            self.assertEqual(payload_issues(output, contracts.schema_for('operational_review'), fixed, {}, root), [])
            catalog = {row['value'] for row in fitted['context']['reference_catalog']}
            self.assertLessEqual(set(advertised), catalog, 'The producer-visible catalog projects the same checker')

    def test_next_review_of_the_same_target_can_resolve_an_exhausted_review(self):
        from do_math.submission import payload_issues
        engine, action, _, _ = self.fixture()
        exhausted = {'id': 'AC-earlier-review', 'role': 'operational_review', 'target': 'EX-work', 'live': True}
        engine.runtime['waiting_actions'] = {exhausted['id']: {'action': exhausted, 'kind': 'output_validation',
            'execution_id': 'EX-earlier-review', 'next_owner': 'operational_review',
            'reason': 'Producer repair was rejected again; diagnose the preserved contract and receiver errors'}}
        profile = next(p for p in engine.instance['execution_profiles'].values() if p['role'] == 'operational_review')
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            context = engine._context(action, root, execution_id='EX-review')
            self.assertEqual([row['action_id'] for row in context['blocked_actions']], [exhausted['id']])
            fitted = prepare_role_input(context, instance=engine.instance, runtime=engine.runtime,
                role='operational_review', profile=profile, snapshot=engine.head, workspace=root,
                activity_id='AY-review', install_submission_tools=True)
            output = {'summary': 'Review', 'used_sources': ['EX-work'], 'questions': [],
                'disposition': {'kind': 'continue', 'basis_refs': ['EX-work'], 'next_owner': 'engine',
                                'reason': 'The target still progresses.', 'next_review': None}}
            extensions = {'action_resolutions': [{'action_id': exhausted['id'], 'evidence_execution_id': 'current',
                'reason': 'This accepted review settles the same observed target.'}]}
            self.assertEqual(payload_issues(output, contracts.schema_for('operational_review'),
                                            fitted['validation_context'], extensions, root), [])

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


# Fields of a stored central check beyond knowledge_fixtures.formal_result: the compiler's
# raw output and invocation, signatures and the check reference.
CENTRAL_CHECK = {'stdout': 'raw Lean output', 'stderr': 'raw Lean warnings', 'command': ['lake', 'env', 'lean', 'Check.lean'],
                 'exit_code': 0, 'declaration_signatures': {'truth': 'True'},
                 'signature_hash': 's' * 64, 'execution_id': 'EX-formal', 'artifact_ref': 'runtime/artifacts/BA-formal/formal.json'}
# What identity review and goal audit compare (계약/동일성-검토.md, 계약/목표-감사.md).
JUDGED = {'status', 'source_sha256', 'declarations', 'axioms', 'declaration_signatures', 'signature_hash',
          'toolchain', 'execution_id', 'artifact_ref'}


def central_check_knowledge():
    """``(instance, runtime, kid, stored verification)``: one K record whose check stored raw output and evidence."""
    instance, runtime = surface_state()
    evidence, _, kid, _ = verified_knowledge(check=CENTRAL_CHECK)
    instance.update(evidence)
    verification = instance['formal_results'][instance['knowledge'][kid]['formal_result_id']]['verification']
    return instance, runtime, kid, verification


class FormalJudgmentInputTests(unittest.TestCase):
    def assert_judged(self, view, verification):
        self.assertEqual(view, {name: verification[name] for name in JUDGED})

    def assert_environment(self, formal):
        # verified_knowledge's trust environment TE-test allows no axiom.
        self.assertEqual((formal.pop('trust_environment_id'), formal.pop('allowed_axioms')), ('TE-test', []))

    def test_identity_review_proposal_carries_only_the_judged_formal_fields(self):
        from do_math.review_cycle import review_proposal
        instance, _, kid, verification = central_check_knowledge()
        formal = review_proposal(instance, kid)['formal']
        self.assert_environment(formal)
        self.assert_judged(formal, verification)

    def test_judged_formal_view_states_its_environment_allowed_axioms(self):
        # A central check stores no allowed axioms; the judgment compares axioms with its environment's.
        environment = {'id': 'TE-test', 'status': 'active', 'toolchain': {'version': 'test-fixture'},
                       'allowed_axioms': ['propext']}
        instance, _, kid, _ = verified_knowledge(environment)
        verification = instance['formal_results'][instance['knowledge'][kid]['formal_result_id']]['verification']
        self.assertNotIn('allowed_axioms', verification)
        self.assertEqual(knowledge_records.proposal_view(instance, kid)['formal']['allowed_axioms'], ['propext'])

    def test_goal_audit_receives_the_judged_formal_result(self):
        instance, runtime, kid, verification = central_check_knowledge()
        engine = context_engine(instance, runtime)
        engine._documents['goal_audit'] = contracts.prompt_documents('goal_audit')
        with tempfile.TemporaryDirectory() as directory:
            item, = engine._context({'role': 'goal_audit'}, Path(directory))['eligible_knowledge']
        self.assert_environment(item['proposal']['formal'])
        self.assert_judged(item['proposal']['formal'], verification)
        self.assert_judged(item['formal_result']['verification'], verification)
        self.assertEqual(item['formal_result']['trust_environment_id'], 'TE-test')

    def test_knowledge_files_carry_the_judged_formal_result(self):
        instance, runtime, kid, verification = central_check_knowledge()
        with tempfile.TemporaryDirectory() as directory:
            context = context_engine(instance, runtime)._context({'role': 'research_preparation'}, Path(directory))
            row, = context['knowledge_catalog']
            record = json.loads((Path(directory) / row['path']).read_bytes())
        self.assert_environment(record['formal'])
        self.assert_judged(record['formal'], verification)
        self.assert_judged(record['formal_result']['verification'], verification)

    def test_reviewed_proposal_fixes_the_sources_it_used(self):
        # 계약/동일성-검토.md 39: transcriptions are compared with the originals actually used.
        from do_math.review_cycle import review_proposal
        instance, _, kid, _ = central_check_knowledge()
        record = instance['knowledge'][kid]
        record.update(source_refs=['paper.pdf'], source_basis=[{'name': 'paper.pdf', 'sha256': 'e' * 64}])
        proposal = review_proposal(instance, kid)
        self.assertEqual((proposal['source_refs'], proposal['source_basis']),
                         (record['source_refs'], record['source_basis']))


# Context keys the engine builds for many roles; each reaches only the roles whose contract
# or checks read it. The expectations below are those roles, from the role contracts.
SCOPED_KEYS = ('model_policy', 'resources', 'budget_unit', 'academic_requirements', 'academic_phase',
               'academic_validation', 'repetition_holds', 'goal', 'policies', 'goal_revision', 'policy_revision',
               'events', 'external_operations', 'external_rejections', 'user_inputs', 'open_questions',
               'recent_history', 'relations', 'formal_verifier', 'execution_profiles', 'role_profile_refs',
               'decisions', 'pending_revisions', 'revision_cycles', 'blocked_actions')


def is_map_entry(value):
    """A context key given as a map entry: its exact catalog source and item count, not its content."""
    return isinstance(value, dict) and set(value) == {'source_ref', 'total'}


# Derived machine files the input builds only for the scopes that inline them; elsewhere the
# records they are derived from stay readable through the record map.
DERIVED_KEYS = {'configuration_source', 'relation_validation_source'}
PLANNING_DIRECT = {'tasks': [], 'resources': {}, 'knowledge_catalog': [], 'ready_task_ids': [], 'blocked_actions': []}
INTENT_DIRECT = {'user_request': {'id': 'UI-1'}, 'interpretation_to_check': None}
OPERATIONAL_DIRECT = {'execution_to_review': {'id': 'EX-work'}, 'observation': {}, 'operational_evidence': {},
                      'admissible_basis_refs': []}


class RoleInputClassTests(unittest.TestCase):
    def prepare(self, action, direct=None, *, instance=None, runtime=None, extra=None, root=None,
                snapshot='a' * 40, install=False):
        """One role input whose engine context held every scoped key.

        Returns the packaged context, or with ``root`` the whole prepared input in that workspace.
        ``install`` also installs the submission and read tools, as the engine does.
        """
        if instance is None:
            instance, runtime = surface_state()
        profile = next(p for p in instance['execution_profiles'].values() if p['role'] == action['role'])
        context = {key: [] for key in SCOPED_KEYS}
        context.update(action={'id': 'AC-scope', **action}, **(direct or {}), **(extra or {}))
        def run(workspace):
            return prepare_role_input(context, instance=instance, runtime=runtime, role=action['role'],
                profile=profile, snapshot=snapshot, workspace=workspace, activity_id='AC-1',
                install_submission_tools=install, max_artifact_bytes=100000 if install else None)
        if root is not None:
            return run(root)
        with tempfile.TemporaryDirectory() as directory:
            return run(Path(directory))['context']

    def test_role_input_maps_context_its_scope_does_not_inline(self):
        planning, intent, operational = PLANNING_DIRECT, INTENT_DIRECT, OPERATIONAL_DIRECT
        cases = [  # (action, direct inputs, keys it inlines, keys it receives only as map entries)
            ({'role': 'research_work'}, {'task': {'id': 'TK-1'}},
             {'formal_verifier', 'relations', 'user_inputs', 'external_operations', 'external_rejections', 'open_questions',
              'goal', 'policies', 'decisions', 'relation_validation_source'},
             {'model_policy', 'resources', 'budget_unit', 'academic_requirements', 'academic_phase', 'academic_validation',
              'repetition_holds', 'goal_revision', 'policy_revision', 'events', 'recent_history', 'execution_profiles',
              'role_profile_refs', 'pending_revisions', 'revision_cycles', 'blocked_actions'}),
            ({'role': 'supplemental_research'}, {'task': {'id': 'TK-1'}},
             {'relation_validation_source', 'goal', 'user_inputs', 'external_operations', 'formal_verifier'},
             {'model_policy', 'events', 'recent_history', 'execution_profiles'}),
            ({'role': 'supplemental_research', 'review_cycle_id': 'RC-1'},
             {'review_research': {'sources': []}, 'proposal': {'revision': 1}},
             {'formal_verifier', 'relations', 'decisions'},
             {'relation_validation_source', 'goal', 'policies', 'user_inputs', 'external_operations', 'external_rejections',
              'model_policy', 'execution_profiles'}),
            ({'role': 'operational_review'}, operational,
             {'repetition_holds', 'events', 'recent_history', 'goal_revision', 'policy_revision', 'decisions',
              'user_inputs', 'external_operations', 'blocked_actions'},
             {'model_policy', 'resources', 'budget_unit', 'formal_verifier', 'external_rejections', 'academic_requirements',
              'academic_phase', 'academic_validation', 'pending_revisions', 'revision_cycles', 'execution_profiles',
              'role_profile_refs'}),
            ({'role': 'goal_audit'}, {'eligible_knowledge': []},
             {'academic_requirements', 'academic_phase', 'academic_validation', 'decisions', 'relations', 'goal',
              'policies', 'goal_revision', 'policy_revision', 'external_rejections', 'open_questions'},
             {'formal_verifier', 'model_policy', 'resources', 'execution_profiles', 'role_profile_refs', 'events',
              'user_inputs', 'external_operations', 'repetition_holds'}),
            ({'role': 'task_contract_review'}, {'task': {'id': 'TK-1'}},
             {'model_policy', 'resources', 'budget_unit', 'formal_verifier', 'academic_requirements',
              'academic_phase', 'recent_history', 'external_operations', 'external_rejections', 'open_questions'},
             {'execution_profiles', 'role_profile_refs', 'events', 'academic_validation', 'goal_revision',
              'policy_revision', 'repetition_holds', 'user_inputs'}),
            ({'role': 'intent_interpretation', 'stage': 'interpret'}, intent,
             {'formal_verifier', 'academic_requirements', 'configuration_source', 'goal_revision'},
             {'recent_history', 'user_inputs', 'open_questions', 'events', 'model_policy', 'academic_phase',
              'execution_profiles', 'role_profile_refs'}),
            ({'role': 'intent_interpretation', 'stage': 'check'}, intent,
             {'academic_requirements', 'goal_revision', 'goal', 'relations', 'decisions', 'configuration_source'},
             {'formal_verifier', 'recent_history', 'user_inputs', 'open_questions', 'events', 'model_policy', 'resources',
              'external_operations', 'external_rejections', 'repetition_holds', 'academic_phase', 'academic_validation',
              'execution_profiles', 'role_profile_refs'}),
            ({'role': 'intent_interpretation', 'stage': 'delegation_check', 'delegation_application_id': 'DA-1'}, intent,
             {'decisions'},
             {'configuration_source', 'goal', 'policies', 'goal_revision', 'policy_revision', 'relations',
              'formal_verifier', 'execution_profiles', 'role_profile_refs', 'academic_requirements'}),
            ({'role': 'maintenance'}, {},
             {'resources', 'budget_unit', 'formal_verifier', 'pending_revisions', 'revision_cycles', 'blocked_actions',
              'recent_history', 'user_inputs', 'external_operations', 'external_rejections', 'goal', 'relations', 'decisions'},
             {'model_policy', 'academic_requirements', 'academic_phase', 'academic_validation', 'repetition_holds',
              'goal_revision', 'policy_revision', 'events', 'open_questions', 'execution_profiles', 'role_profile_refs'}),
            ({'role': 'maintenance', 'kind_definition_id': 'KD-1'}, {},
             {'decisions'},
             {'goal', 'policies', 'relations', 'formal_verifier', 'resources', 'budget_unit', 'pending_revisions',
              'revision_cycles', 'blocked_actions', 'user_inputs', 'recent_history', 'external_operations',
              'external_rejections'}),
            ({'role': 'maintenance', 'stage': 'impact_review'}, {'impact_review_input': {}},
             {'goal', 'relations', 'formal_verifier'},
             {'resources', 'pending_revisions', 'blocked_actions', 'user_inputs', 'recent_history', 'external_operations'}),
            ({'role': 'research_plan'}, planning,
             {'model_policy', 'resources', 'academic_validation', 'repetition_holds', 'events', 'goal_revision',
              'pending_revisions', 'revision_cycles', 'blocked_actions', 'external_rejections'},
             {'user_inputs', 'execution_profiles', 'role_profile_refs'}),
            ({'role': 'research_preparation'}, planning,
             {'model_policy', 'resources', 'academic_phase', 'repetition_holds', 'events', 'user_inputs',
              'external_operations'},
             {'academic_validation', 'execution_profiles', 'role_profile_refs'}),
        ]
        for action, direct, inlined, mapped in cases:
            with self.subTest(action=action), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                context = self.prepare(action, direct, root=root)['context']
                self.assertEqual(inlined - context.keys(), set())
                self.assertEqual({key for key in inlined if is_map_entry(context[key])}, set())
                self.assertEqual(mapped & DERIVED_KEYS & context.keys(), set())
                for key in mapped - DERIVED_KEYS:
                    self.assertTrue(is_map_entry(context.get(key)), key)
                    self.assertEqual((root / context[key]['source_ref']['path']).read_bytes(), canonical_json([]))

    def test_independent_judgment_never_receives_its_blocked_context(self):
        # 계약/보충-조사.md 23, 공통-실행.md 69 (review lineage); 계약/목표-감사.md 13; 계약/의도-해석.md 69.
        instance, runtime = surface_state()
        runtime['executions']['EX-seat'] = {'id': 'EX-seat', 'role': 'identity_review', 'status': 'ended',
                                            'action': {'role': 'identity_review', 'review_cycle_id': 'RC-1'}}
        private = {'tasks': [{'id': 'TK-private'}], 'recent_history': [], 'open_questions': [], 'question_links': [],
                   'user_inputs': []}
        review_lineage = {'tasks', 'recent_history', 'open_questions', 'question_links'}
        cases = [
            ({'role': 'supplemental_research', 'review_cycle_id': 'RC-1'},
             {'review_research': {'sources': []}, 'proposal': {'revision': 1}}, review_lineage),
            ({'role': 'operational_review', 'target': 'EX-seat'}, OPERATIONAL_DIRECT, review_lineage),
            ({'role': 'goal_audit'}, {'eligible_knowledge': []}, {'recent_history'}),
            ({'role': 'intent_interpretation', 'stage': 'delegation_check', 'delegation_application_id': 'DA-1'},
             INTENT_DIRECT, {'recent_history', 'user_inputs', 'open_questions', 'question_links'}),
        ]
        for action, direct, blocked in cases:
            with self.subTest(action=action), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                fitted = self.prepare(action, direct, instance=instance, runtime=runtime, extra=private, root=root)
                self.assertEqual(blocked & fitted['context'].keys(), set())
                self.assertEqual(blocked & fitted['validation_context'].keys(), set())
                self.assertEqual({key for key in blocked if (root / 'input/catalog' / (key + '.json')).exists()}, set())
                if 'tasks' in blocked:
                    self.assertNotIn('TK-private', canonical_json(fitted['validation_context']).decode())

    def test_goal_auditor_cannot_reach_another_auditors_judgment(self):
        # 계약/목표-감사.md 13: each audit slot seals its judgment in research/goal_judgments while
        # the other slots of the same round may still be unjudged; they must not read or cite it.
        from do_math.git_store import GitStateStore
        from do_math.state_contract import STATE_CONTRACT_ID
        from research_fixtures import git_init, role_reach
        secret = 'PRIVATE-PEER-AUDIT'
        judgment = {'id': 'GJ-peer', 'basis': 'BASIS', 'slot': 0, 'required': 2, 'decision': 'satisfied',
                    'summary': secret}
        instance, runtime = surface_state()
        instance['goal_judgments'] = [judgment]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repository, workspace = root / 'repository', root / 'workspace'
            repository.mkdir()
            workspace.mkdir()
            git_init(repository)
            store = {'repository': str(repository), 'instance_id': SnapshotReadToolTests.INSTANCE}
            def envelope(family, record):
                return canonical_json({'contract_id': STATE_CONTRACT_ID, 'family': family, 'record': record})
            snapshot = GitStateStore(repository, store['instance_id']).publish(None, {
                'research/goal_judgments/GJ-peer.json': envelope('goal_judgments', judgment),
                'runtime/executions/EX-1.json': envelope('executions', {'id': 'EX-1', 'role': 'research_work'})}).head
            fitted = self.prepare({'role': 'goal_audit', 'basis': 'BASIS', 'slot': 1, 'required': 2},
                                  {'eligible_knowledge': []}, instance=instance, runtime=runtime,
                                  extra={'record_store': store, 'formal_verifier': {'reference': 'tool:lean'}},
                                  root=workspace, snapshot=snapshot, install=True)
            reached, held = role_reach(fitted['prompt'], workspace, secret)
            try:
                submission.validate_reference('GJ-peer', fitted['validation_context'], workspace)
                cited = True
            except ValueError:
                cited = False
        self.assertEqual(held, ['research/goal_judgments/GJ-peer.json'])
        self.assertEqual((reached, cited), ([], False))

    def test_operational_review_of_an_audit_slot_cannot_reach_another_slots_judgment(self):
        # 계약/목표-감사.md 13: a live operational review of a running audit slot publishes its
        # disposition reason to that slot (engine: publish_worker_feedback), so the reviewer must
        # not see the round's other judgments either: inline, in the history or in the snapshot.
        from do_math import operational_dispositions
        from do_math.git_store import GitStateStore
        from do_math.state_contract import STATE_CONTRACT_ID
        from research_fixtures import git_init, role_reach
        secret = 'PRIVATE-PEER-AUDIT'
        judgment = {'id': 'GJ-peer', 'basis': 'BASIS', 'slot': 0, 'required': 2, 'decision': 'satisfied',
                    'summary': secret}
        audit = {'id': 'EX-audit', 'role': 'goal_audit', 'status': 'running',
                 'action': {'role': 'goal_audit', 'basis': 'BASIS', 'slot': 1, 'required': 2}}
        instance, runtime = surface_state()
        instance['goal_judgments'] = [judgment]
        runtime['executions']['EX-audit'] = audit
        action = {'role': 'operational_review', 'target': 'EX-audit', 'live': True}
        direct = {'execution_to_review': deepcopy(audit), 'observation': {}, 'operational_evidence': {},
                  'admissible_basis_refs': operational_dispositions.admissible_basis_refs(instance, runtime, action)}
        # The engine gives an operational review the goal judgments and the recent history.
        extra = {'goal_judgments': [judgment],
                 'recent_history': [{'role': 'goal_audit', 'execution_id': 'EX-peer', 'summary': secret}]}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repository, workspace = root / 'repository', root / 'workspace'
            repository.mkdir()
            workspace.mkdir()
            git_init(repository)
            store = {'repository': str(repository), 'instance_id': SnapshotReadToolTests.INSTANCE}
            def envelope(family, record):
                return canonical_json({'contract_id': STATE_CONTRACT_ID, 'family': family, 'record': record})
            snapshot = GitStateStore(repository, store['instance_id']).publish(None, {
                'research/goal_judgments/GJ-peer.json': envelope('goal_judgments', judgment),
                'runtime/executions/EX-audit.json': envelope('executions', audit)}).head
            fitted = self.prepare(action, direct, instance=instance, runtime=runtime,
                                  extra={**extra, 'record_store': store, 'formal_verifier': {'reference': 'tool:lean'}},
                                  root=workspace, snapshot=snapshot, install=True)
            reached, held = role_reach(fitted['prompt'], workspace, secret)
            try:
                submission.validate_reference('GJ-peer', fitted['validation_context'], workspace)
                cited = True
            except ValueError:
                cited = False
        self.assertEqual(held, ['research/goal_judgments/GJ-peer.json'])
        self.assertEqual((reached, cited), ([], False))

    def test_independent_judgment_cannot_reach_unpublished_work_of_the_execution_ledger(self):
        """Over 10 s: each of three scopes runs the installed read tool in a child process on a real Git snapshot."""
        # Scopes whose ledger reach was judged only from the code: a delegation judge and the
        # executions it stays independent of (계약/의도-해석.md 69, delegations.record_judgment),
        # the interpreter's unfixed checkpoint (계약/의도-해석.md 50) and the unsealed lineage record
        # behind a review seat's operational review (공통-실행.md 「질문의 소유자와 영향을 받는 대상을
        # 밝힌다」). Each secret lives only in the execution ledger, and each input is built as the
        # engine builds it, so a supplied reference that names a ledger record is really supplied.
        from do_math import delegations, operational_dispositions
        from do_math.git_store import GitStateStore
        from do_math.state_contract import STATE_CONTRACT_ID
        from research_fixtures import git_init, role_reach
        secret = 'PRIVATE-UNPUBLISHED-WORK'
        def envelope(family, record):
            return canonical_json({'contract_id': STATE_CONTRACT_ID, 'family': family, 'record': record})
        instance, runtime = surface_state()
        seat = {'id': 'EX-seat', 'role': 'identity_review', 'status': 'running',
                'action': {'role': 'identity_review', 'review_cycle_id': 'RC-1'}}
        author = {'id': 'EX-author', 'role': 'intent_interpretation', 'status': 'ended'}
        runtime['executions'].update({'EX-seat': seat, 'EX-author': author})
        runtime['review_cycles'] = {'RC-1': {'id': 'RC-1'}}
        # The case names its original decision's author, whose execution the judge stays independent of.
        runtime['delegation_applications'] = {'DA-1': {'id': 'DA-1', 'input_sha256': 'c' * 64, 'judgments': {},
            'basis': {'original_decision': {'id': 'DC-1', 'actor': 'user', 'author_execution_ids': ['EX-author']},
                      'case': {'id': 'CASE-1', 'basis_refs': []}}}}
        delegation_case = delegations.judgment_input(runtime, 'DA-1')
        review_target = {'role': 'operational_review', 'target': 'EX-seat'}
        # A published canon record: every snapshot holds a research subtree.
        canon = {'research/decisions/DC-1.json': envelope('decisions', {'id': 'DC-1', 'actor': 'user'})}
        cases = [  # (action, direct inputs, snapshot files that hold the secret, other snapshot files)
            ({'role': 'intent_interpretation', 'stage': 'delegation_check', 'delegation_application_id': 'DA-1'},
             {'user_request': {'request': {'id': 'UI-1'}, 'delegation_case': deepcopy(delegation_case)},
              'delegation_case': deepcopy(delegation_case), 'interpretation_to_check': None},
             {'runtime/delegation_applications/DA-1.json': envelope('delegation_applications', {
                  'id': 'DA-1', 'judgments': {'interpret': {'execution_id': 'EX-peer', 'output': {'reason': secret}}}}),
              'runtime/executions/EX-author.json': envelope('executions', {**author, 'summary': secret})}, {}),
            ({'role': 'intent_interpretation', 'stage': 'check'}, INTENT_DIRECT,
             {'runtime/artifacts/BA-interpreter/checkpoint.json': secret.encode('utf-8')}, {}),
            (review_target, {'execution_to_review': deepcopy(seat), 'observation': {}, 'operational_evidence': {},
                             'admissible_basis_refs': operational_dispositions.admissible_basis_refs(
                                 instance, runtime, review_target)},
             {'runtime/review_cycles/RC-1.json': envelope('review_cycles', {'id': 'RC-1', 'summary': secret})},
             {'runtime/executions/EX-seat.json': envelope('executions', seat)}),
        ]
        for action, direct, unpublished, published in cases:
            with self.subTest(action=action), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                repository, workspace = root / 'repository', root / 'workspace'
                repository.mkdir()
                workspace.mkdir()
                git_init(repository)
                store = {'repository': str(repository), 'instance_id': SnapshotReadToolTests.INSTANCE}
                snapshot = GitStateStore(repository, store['instance_id']).publish(
                    None, {**canon, **unpublished, **published}).head
                fitted = self.prepare(action, direct, instance=instance, runtime=runtime,
                                      extra={'record_store': store, 'formal_verifier': {'reference': 'tool:lean'}},
                                      root=workspace, snapshot=snapshot, install=True)
                self.assertEqual(fitted['context']['record_map']['ledger'], 'supplied_only')
                reached, held = role_reach(fitted['prompt'], workspace, secret)
                self.assertEqual(held, sorted(unpublished))
                self.assertEqual(reached, [])
                if action is review_target:
                    # The seat's target is supplied and readable; only the lineage record it names is not.
                    self.assertIn('EX-seat', fitted['validation_context']['record_index']['runtime/executions'])

    def test_record_index_lists_the_snapshot_records_the_role_may_read(self):
        from record_fixtures import task_contract
        instance, runtime = surface_state()
        runtime['tasks'] = {'TK-1': task_contract()}
        governance_sources = sorted(instance['governance_sources'])
        with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
            readable = self.prepare({'role': 'maintenance'}, instance=instance, runtime=runtime, root=Path(first))
            judged = self.prepare({'role': 'task_contract_review', 'target': 'TK-1'}, {'task': task_contract()},
                                  instance=instance, runtime=runtime, root=Path(second))
        index = readable['validation_context']['record_index']
        self.assertEqual((index['runtime/executions'], index['runtime/activities'], index['runtime/tasks']),
                         (['EX-1'], ['AC-1'], ['TK-1']))
        self.assertEqual(index['research/governance_sources'], governance_sources)
        # An independent judgment reads the research canon and only the supplied part of the execution ledger.
        index = judged['validation_context']['record_index']
        self.assertEqual({family for family in index if family.startswith('runtime/')}, {'runtime/tasks'})
        self.assertEqual(index['research/governance_sources'], governance_sources)
        for fitted, ledger in ((readable, 'readable'), (judged, 'supplied_only')):
            record_map = fitted['context']['record_map']
            self.assertEqual(record_map['ledger'], ledger)
            self.assertEqual(record_map['families'], {family: len(ids) for family, ids in
                                                      fitted['validation_context']['record_index'].items()})
            self.assertTrue(is_map_entry(fitted['context']['record_index']))

    def test_snapshot_record_outside_the_prompt_passes_the_shared_reference_check(self):
        # A record of the input snapshot is citable although no inline key shows it (R5).
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fitted = self.prepare({'role': 'maintenance'}, extra={'execution_id': 'EX-check'}, root=root)
            fixed = fitted['validation_context']
            self.assertNotIn('AC-1', canonical_json(fitted['context']).decode())
            output = {'summary': 'Inspect', 'used_sources': ['AC-1'], 'questions': [],
                      'report': 'Inspected the activity record', 'remaining_work': []}
            schema = contracts.schema_for('maintenance')
            self.assertEqual(submission.payload_issues(output, schema, fixed, {}, root), [])
            output['used_sources'] = ['AC-absent']
            self.assertEqual([row['path'] for row in submission.payload_issues(output, schema, fixed, {}, root)],
                             ['output/used_sources/0'])

    def test_independent_judgment_cites_the_research_canon_but_not_an_unsupplied_ledger_record(self):
        from record_fixtures import task_contract
        instance, runtime = surface_state()
        runtime['tasks'] = {'TK-1': task_contract()}
        # A published exposition that no key of this input shows.
        instance['expositions'] = {'EP-1': {'id': 'EP-1'}}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fixed = self.prepare({'role': 'task_contract_review', 'target': 'TK-1'}, {'task': task_contract()},
                                 instance=instance, runtime=runtime, root=root)['validation_context']
            submission.validate_reference('EP-1', fixed, root)
            submission.validate_reference('TK-1', fixed, root)
            with self.assertRaises(ValueError):
                submission.validate_reference('EX-1', fixed, root)

    def test_review_seat_operational_review_reads_the_evidence_its_input_supplies(self):
        # 공통-실행.md 「독립 판단의 차단」: an independent judgment reads the ledger records and
        # files its input supplies; an operational review supplies them as admissible_basis_refs.
        from do_math.context_store import readable_snapshot_path
        instance, runtime = surface_state()
        runtime['executions']['EX-seat'] = {'id': 'EX-seat', 'role': 'identity_review', 'status': 'ended',
                                            'action': {'role': 'identity_review', 'review_cycle_id': 'RC-1'}}
        runtime['observation_facts'] = {identifier: {'id': identifier} for identifier in ('OF-seat', 'OF-other')}
        runtime['self_check_obligations'] = {'SC-seat': {'id': 'SC-seat', 'execution_id': 'EX-seat'}}
        result = 'runtime/artifacts/BA-seat/result.json'
        direct = {**OPERATIONAL_DIRECT, 'execution_to_review': {'id': 'EX-seat'},
                  'admissible_basis_refs': ['EX-seat', 'OF-seat', 'SC-seat', result]}
        with tempfile.TemporaryDirectory() as directory:
            fixed = self.prepare({'role': 'operational_review', 'target': 'EX-seat'}, direct, instance=instance,
                                 runtime=runtime, root=Path(directory))['validation_context']
        self.assertEqual(fixed['record_map']['ledger'], 'supplied_only')
        index = fixed['record_index']
        self.assertEqual((index.get('runtime/observation_facts'), index.get('runtime/self_check_obligations')),
                         (['OF-seat'], ['SC-seat']))
        self.assertTrue(readable_snapshot_path(fixed, result))
        self.assertFalse(readable_snapshot_path(fixed, 'runtime/artifacts/BA-other/result.json'))

    def test_citable_records_cover_every_readable_work_record(self):
        # Task inputs and completion evidence may name any record the role can read (공통-실행.md 41).
        for action, direct in (({'role': 'research_preparation'}, PLANNING_DIRECT),
                               ({'role': 'operational_review', 'target': 'EX-1'}, OPERATIONAL_DIRECT)):
            with self.subTest(action=action), tempfile.TemporaryDirectory() as directory:
                fixed = self.prepare(action, direct, root=Path(directory))['validation_context']
                self.assertTrue({'EX-1', 'AC-1'} <= set(fixed['supplied_record_ids']), fixed['supplied_record_ids'])

    def test_self_check_evidence_follows_the_submission_citation_rule(self):
        # Records of the input snapshot and the execution's preserved workspace files are citable.
        engine = context_engine()
        engine._issued_input = create_autospec(engine._issued_input, return_value=(
            {'reference_catalog': [], 'record_index': {'runtime/activities': ['AC-1']}}, None))
        cited = ['AC-1', 'checkpoint.json', 'workspace:checkpoint.json', '.scratch/note.txt', 'absent.txt']
        response = {'obligation_id': 'SC-1', 'execution_id': 'EX-1', 'rule_revision': 0, 'progress': 'progress',
                    'attempts': ['read the checkpoint'], 'next_method': 'continue',
                    'rule_results': [{'rule_id': 'R-1', 'status': 'normal', 'evidence_refs': cited,
                                      'missing_evidence_refs': [], 'reason': 'compared the checkpoint'}]}
        with tempfile.TemporaryDirectory() as directory:
            engine.instance['workspace'] = directory
            workspace = Path(directory) / 'runs/EX-1/workspace'
            (workspace / '.scratch').mkdir(parents=True)
            (workspace / 'checkpoint.json').write_text('{}', encoding='utf-8')
            (workspace / '.scratch/note.txt').write_text('scratch', encoding='utf-8')
            self.assertEqual(engine._control_evidence_refs({'id': 'EX-1'}, response),
                             {'AC-1', 'checkpoint.json', 'workspace:checkpoint.json'})

    def test_scope_follows_the_role_the_input_is_prepared_for(self):
        # prepare_role_input vouches for its role (the selected profile's role), not for action fields.
        planning = {'tasks': [], 'resources': {}, 'knowledge_catalog': [], 'ready_task_ids': [], 'blocked_actions': []}
        instance, runtime = surface_state()
        profile = next(p for p in instance['execution_profiles'].values() if p['role'] == 'research_plan')
        with tempfile.TemporaryDirectory() as directory:
            context = prepare_role_input({'action': {'id': 'AC-plan'}, 'model_policy': {}, **planning},
                instance=instance, runtime=runtime, role='research_plan', profile=profile, snapshot='a' * 40,
                workspace=Path(directory), activity_id='AC-1')['context']
        self.assertEqual({'model_policy', 'configuration_source'} - context.keys(), set())

    def test_identity_review_maps_what_it_does_not_inline_and_never_receives_its_private_keys(self):
        # 계약/동일성-검토.md 47 and GLOSSARY 「검토 자리」: no author or peer execution context.
        instance, _ = surface_state()
        with tempfile.TemporaryDirectory() as directory:
            engine = ReviewFakeEngine(Path(directory))
            engine.instance = {**instance, **engine.instance,
                'config': {**instance['config'], **engine.instance['config']},
                **{family: {**instance[family], **engine.instance[family]} for family in governance_start()}}
            engine.head = 'a' * 40
            engine.start('K1')
            action = {**engine.pending(), 'grant_id': 'GR-current-execution'}
            review = engine._prepare_review_context(action, Path(directory) / 'seat')['context']
            fitted = self.prepare(action, {'role_review': review}, instance=engine.instance, runtime=engine.runtime,
                                  extra={'tasks': [{'id': 'TK-private'}], 'question_links': []},
                                  root=Path(directory) / 'input-case')
        context = fitted['context']
        self.assertEqual(action['stage'], 'initial')
        for key in ('model_policy', 'formal_verifier', 'decisions', 'relations', 'goal', 'policies',
                    'execution_profiles', 'role_profile_refs', 'events', 'user_inputs'):
            self.assertTrue(is_map_entry(context.get(key)), key)
        self.assertEqual({'tasks', 'recent_history', 'open_questions', 'question_links'}
                         & fitted['validation_context'].keys(), set())
        self.assertEqual(context['record_map']['ledger'], 'supplied_only')

    def test_control_binding_reaches_the_checker_context_but_not_the_prompt(self):
        instance, runtime = surface_state()
        profile = next(p for p in instance['execution_profiles'].values() if p['role'] == 'research_work')
        binding = {'execution_id': 'EX-work', 'grant_id': 'GR-1', 'capability': 'secret-capability'}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fitted = prepare_role_input({'action': {'id': 'AC-work', 'role': 'research_work'}, 'task': {'id': 'TK-1'},
                'control_binding': binding}, instance=instance, runtime=runtime, role='research_work', profile=profile,
                snapshot='a' * 40, workspace=root, activity_id='AC-1', install_submission_tools=True,
                max_artifact_bytes=100000)
            checker = json.loads((root / 'input/submission/context.json').read_bytes())
        self.assertEqual(checker['control_binding'], binding)
        self.assertNotIn('control_binding', fitted['context'])
        self.assertNotIn('secret-capability', fitted['prompt'])

    def test_task_readiness_reaches_its_readers_in_their_scope(self):
        # 후보-준비.md 61 checks which tasks wait for external input; 연구-수행.md 17 reads its own task's basis.
        from record_fixtures import task_contract
        instance, runtime = surface_state()
        runtime['tasks'] = {identifier: {**task_contract(), 'id': identifier} for identifier in ('TK-1', 'TK-2')}
        engine = context_engine(instance, runtime)
        engine._documents['supplemental_research'] = contracts.prompt_documents('supplemental_research')
        readiness = {}
        for role in ('research_preparation', 'research_work', 'supplemental_research'):
            with tempfile.TemporaryDirectory() as directory:
                readiness[role] = engine._context({'role': role, 'target': 'TK-1'}, Path(directory)).get('task_readiness')
        self.assertEqual(set(readiness['research_preparation']), {'TK-1', 'TK-2'})
        self.assertEqual(set(readiness['research_work']), {'TK-1'})
        self.assertIsNone(readiness['supplemental_research'])

    def test_completed_review_record_reaches_only_the_goal_audit(self):
        # 계약/목표-감사.md 21 reads it; no other role contract does.
        instance, runtime, kid, _ = central_check_knowledge()
        instance['knowledge'][kid]['review_cycle_id'] = 'RC-done'
        runtime['review_cycles'] = {'RC-done': {'id': 'RC-done', 'status': 'completed', 'turns': {}}}
        engine = context_engine(instance, runtime)
        engine._documents['goal_audit'] = contracts.prompt_documents('goal_audit')
        for role, expected in (('goal_audit', True), ('research_preparation', False)):
            with self.subTest(role=role), tempfile.TemporaryDirectory() as directory:
                row, = engine._context({'role': role}, Path(directory))['knowledge_catalog']
                self.assertEqual('review_cycle_source' in row, expected)
                self.assertEqual((Path(directory) / 'input' / 'review-cycles').exists(), expected)


class SnapshotReadToolTests(unittest.TestCase):
    """The installed read tool reads the fixed input snapshot within the record map and logs each read."""
    INSTANCE = 'RI-01ARZ3NDEKTSV4RRFFQ69G5FAV'

    def setUp(self):
        from do_math.git_store import GitStateStore
        from do_math.state_contract import STATE_CONTRACT_ID
        from research_fixtures import git_init
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.repository = self.root / 'repo'
        self.repository.mkdir()
        git_init(self.repository)
        def envelope(family, record):
            return canonical_json({'contract_id': STATE_CONTRACT_ID, 'family': family, 'record': record})
        self.decision = {'id': 'DC-1', 'kind': 'approval', 'actor': 'user'}
        self.result = b'{"report": "earlier run"}'
        self.snapshot = GitStateStore(self.repository, self.INSTANCE).publish(None, {
            'research/decisions/DC-1.json': envelope('decisions', self.decision),
            'runtime/executions/EX-1.json': envelope('executions', {'id': 'EX-1', 'role': 'research_work'}),
            'runtime/artifacts/BA-1/result.json': self.result}).head

    def install(self, ledger):
        workspace = self.root / ledger
        workspace.mkdir()
        index = {'research/decisions': ['DC-1'], **({'runtime/executions': ['EX-1']} if ledger == 'readable' else {})}
        context = {'action': {'id': 'AC-read', 'role': 'maintenance'}, 'execution_id': 'EX-read',
                   'snapshot': self.snapshot, 'tasks': [], 'knowledge_catalog': [], 'sources': [],
                   'kind_definitions': {}, 'record_index': index,
                   'record_map': {'snapshot': self.snapshot, 'ledger': ledger,
                                  'families': {family: len(ids) for family, ids in index.items()}},
                   'record_store': {'repository': str(self.repository), 'instance_id': self.INSTANCE}}
        submission.install_tools(workspace, context, contracts.schema_for('maintenance'), None)
        return workspace

    def read(self, workspace, *arguments):
        import subprocess
        result = subprocess.run([sys.executable, '-B', 'input/tools/read_input.py', *arguments], cwd=workspace,
                                text=True, capture_output=True, timeout=60)
        log = (workspace / 'checks/reads.jsonl').read_text(encoding='utf-8').splitlines()
        return result.returncode, json.loads(result.stdout), [json.loads(line) for line in log]

    def test_indexed_record_is_read_from_the_input_snapshot_and_logged(self):
        code, output, log = self.read(self.install('readable'), '--id', 'DC-1')
        self.assertEqual(code, 0, output)
        row, = output['records']
        self.assertEqual((row['status'], row['path'], row['record']), ('ok', 'research/decisions/DC-1.json', self.decision))
        self.assertEqual([(entry['request'], entry['status'], entry['snapshot']) for entry in log],
                         [('DC-1', 'ok', self.snapshot)])

    def test_record_outside_the_index_is_refused_and_logged(self):
        code, output, log = self.read(self.install('supplied_only'), '--id', 'EX-1')
        self.assertEqual(code, 1)
        self.assertEqual(output['records'][0]['status'], 'refused')
        self.assertNotIn('record', output['records'][0])
        self.assertEqual([(entry['request'], entry['status']) for entry in log], [('EX-1', 'refused')])

    def test_ledger_artifact_is_readable_only_where_the_ledger_is(self):
        path = 'runtime/artifacts/BA-1/result.json'
        code, output, _ = self.read(self.install('readable'), '--path', path)
        self.assertEqual((code, output['records'][0]['text']), (0, self.result.decode()))
        code, output, _ = self.read(self.install('supplied_only'), '--path', path)
        self.assertEqual((code, output['records'][0]['status']), (1, 'refused'))

    def test_family_listing_summarizes_its_indexed_records(self):
        code, output, log = self.read(self.install('readable'), '--list', '--family', 'research/decisions')
        self.assertEqual(code, 0, output)
        self.assertEqual([(row['id'], row['kind']) for row in output['records']], [('DC-1', 'approval')])
        self.assertEqual(log[-1]['status'], 'ok')

    def test_invalid_output_path_is_refused_in_the_json_result(self):
        # 공통-실행.md 「읽기 도구로 읽는다」: the result is one JSON value and every request is logged.
        code, output, log = self.read(self.install('readable'), '--path', 'runtime/artifacts/BA-1/result.json',
                                      '--output', '../outside.json')
        self.assertEqual((code, output['records'][0]['status']), (1, 'refused'))
        self.assertEqual(log[-1]['status'], 'refused')


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
