"""The engine's context producer (``_context``) and input archive on a Sim's engine and store.

Every engine method runs: the legacy tests replaced the store with an autospec
double and stubbed seven engine methods (``engine_fixtures.context_engine``);
here the store is the Sim's ``ResearchRepository`` and artifact bytes are
published into it (``support.engine_context``). Where a test needs a synthetic
state, the engine holds the legacy records in memory as the input of the
layer-2 call; the Followup tests start from the Sim's public activation.
"""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock

from do_math import contracts, execution_lifecycle, execution_profiles, integration, knowledge_io, knowledge_records, \
    planning, submission
from do_math.canonical import canonical_json
from do_math.context_store import prepare_role_input
from support.knowledge_builders import verified_knowledge
from support.record_builders import approve_task, approved_task, surface_state
from support.default_responder import common
from support.role_answers import seal_response
from support.engine_context import JUDGED, central_check_knowledge, context_engine, issue, package
from support.sim import Sim, warm_template

setUpModule = warm_template

CHECKPOINT = 'runtime/artifacts/BA-check/checkpoint.json'


def use_state(engine, instance, runtime):
    """Give the engine the legacy ``context_engine`` state over ``instance`` and ``runtime``, keeping its workspace."""
    from support.engine_context import context_state
    workspace = engine.instance['workspace']
    engine.instance, engine.runtime = context_state(instance, runtime)
    engine.instance.setdefault('workspace', workspace)
    return engine


class OperationalInputTests(unittest.TestCase):
    def fixture(self, *, claim=None, stored=None, files=None):
        """``(engine, action, checkpoint, raw)``: a live review of running work whose checkpoint is published.

        ``claim`` replaces the checkpoint's claim, ``stored`` is published at the
        checkpoint path instead of its bytes, and ``files`` are published with it.
        """
        value = {'current_claim': 'The exact source passed the preview.', 'evidence_paths': ['proof.lean'],
                 'attempts': ['checked'], 'remaining_work': ['central verification'],
                 'next_step': 'submit', 'progress_state': 'ready_to_submit'}
        raw = (json.dumps(value) + '\n').encode()
        if claim is not None:
            value['current_claim'] = claim
            raw = json.dumps(value).encode()
        engine = context_engine(files={CHECKPOINT: raw if stored is None else stored, **(files or {})})
        target = {'id': 'EX-work', 'role': 'research_work', 'status': 'running',
                  'action': {'role': 'research_work', 'target': 'TK-work'}}
        engine.runtime['executions'][target['id']] = target
        checkpoint = {'kind': 'worker_checkpoint', 'execution_id': target['id'], 'status': 'valid',
            'value': value, 'artifact_ref': CHECKPOINT, 'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)}
        engine.runtime['checkpoints'] = {target['id']: checkpoint}
        action = {'id': 'AC-review', 'role': 'operational_review', 'target': target['id'],
                  'live': True, 'observation_refs': ['OF-one'], 'obligation_ids': ['SC-one']}
        return engine, action, checkpoint, raw

    def packaged(self, engine, action, root):
        from support.entry import entry
        _entry = entry()
        profile = next(p for p in engine.instance['execution_profiles'].values() if p['role'] == 'operational_review')
        context = engine._context(action, root, execution_id='EX-review')
        fitted = prepare_role_input(context, instance=engine.instance, runtime=engine.runtime,
            role='operational_review', profile=profile, snapshot=engine.head, workspace=root,
            activity_id='AY-review', install_submission_tools=True, clock=_entry.ports.clock)
        from support.role_input_requirements import assert_judgment_inputs
        assert_judgment_inputs(self, 'operational_review', fitted, root, producer_context=context)
        return context, fitted

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
        engine, action, _, raw = self.fixture(claim='Evidence retained. ' * 40000)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _, fitted = self.packaged(engine, action, root)
            self.assertIsNone(fitted['overflow'], 'Checkpoint text is available through its exact file reference')
            source = fitted['context']['operational_evidence']['checkpoint_source']
            self.assertEqual((root / source['local_path']).read_bytes(), raw)

    def test_review_gets_the_same_canonical_basis_set_as_application(self):
        engine, action, checkpoint, _ = self.fixture()
        with tempfile.TemporaryDirectory() as directory:
            context = engine._context(action, Path(directory), execution_id='EX-review')
            self.assertEqual(set(context.get('admissible_basis_refs', [])),
                             {'EX-work', 'OF-one', 'SC-one', checkpoint['artifact_ref']})

    def test_live_review_receives_exact_checkpoint_evidence_files(self):
        proof = b'theorem proof (n : Nat) : n + 0 = n := rfl\n'
        source = {'path': 'proof.lean', 'artifact_ref': 'runtime/artifacts/BA-check/proof.lean',
                  'sha256': hashlib.sha256(proof).hexdigest(), 'bytes': len(proof)}
        engine, action, checkpoint, _ = self.fixture(files={source['artifact_ref']: proof})
        checkpoint['evidence_files'] = [source]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            context = engine._context(action, root, execution_id='EX-review')
            files = context['operational_evidence'].get('checkpoint_files', [])
            self.assertEqual(len(files), 1)
            self.assertEqual((root / files[0]['local_path']).read_bytes(), proof)

    def test_packaged_operational_submission_checks_the_advertised_basis(self):
        from support.entry import entry
        _entry = entry()
        engine, action, _, _ = self.fixture()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _, fitted = self.packaged(engine, action, root)
            fixed = fitted['validation_context']
            output = {'summary': 'Review', 'used_sources': ['EX-work'], 'questions': [],
                'disposition': {'kind': 'continue', 'basis_refs': ['EX-work'], 'next_owner': 'engine',
                                'reason': 'The preserved checkpoint is available.', 'next_review': None}}
            schema = contracts.schema_for('operational_review')
            self.assertEqual(submission.payload_issues(output, schema, fixed, {}, root, clock=_entry.ports.clock), [])
            output['disposition']['basis_refs'].append('input/catalog/observation.json')
            issues = submission.payload_issues(output, schema, fixed, {}, root, clock=_entry.ports.clock)
            self.assertTrue(any('invalid_basis_refs' in row['message'] for row in issues), issues)

    def test_every_advertised_basis_ref_passes_the_submission_check(self):
        from support.entry import entry
        _entry = entry()
        engine, action, _, _ = self.fixture()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _, fitted = self.packaged(engine, action, root)
            fixed = fitted['validation_context']
            advertised = fixed['admissible_basis_refs']
            self.assertTrue({'OF-one', 'SC-one'} <= set(advertised), advertised)
            output = {'summary': 'Review', 'used_sources': list(advertised), 'questions': [],
                'disposition': {'kind': 'continue', 'basis_refs': list(advertised), 'next_owner': 'engine',
                                'reason': 'The observation opened a review of a progressing run.', 'next_review': None}}
            self.assertEqual(submission.payload_issues(output, contracts.schema_for('operational_review'), fixed, {}, root, clock=_entry.ports.clock), [])
            catalog = {row['value'] for row in fitted['context']['reference_catalog']}
            self.assertLessEqual(set(advertised), catalog, 'The producer-visible catalog projects the same checker')

    def test_next_review_of_the_same_target_can_resolve_an_exhausted_review(self):
        from support.entry import entry
        _entry = entry()
        engine, action, _, _ = self.fixture()
        exhausted = {'id': 'AC-earlier-review', 'role': 'operational_review', 'target': 'EX-work', 'live': True}
        engine.runtime['waiting_actions'] = {exhausted['id']: {'action': exhausted, 'kind': 'output_validation',
            'execution_id': 'EX-earlier-review', 'next_owner': 'operational_review',
            'reason': 'Producer repair was rejected again; diagnose the preserved contract and receiver errors'}}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            context, fitted = self.packaged(engine, action, root)
            self.assertEqual([row['action_id'] for row in context['blocked_actions']], [exhausted['id']])
            output = {'summary': 'Review', 'used_sources': ['EX-work'], 'questions': [],
                'disposition': {'kind': 'continue', 'basis_refs': ['EX-work'], 'next_owner': 'engine',
                                'reason': 'The target still progresses.', 'next_review': None}}
            extensions = {'action_resolutions': [{'action_id': exhausted['id'], 'evidence_execution_id': 'current',
                'reason': 'This accepted review settles the same observed target.'}]}
            self.assertEqual(submission.payload_issues(output, contracts.schema_for('operational_review'),
                                                       fitted['validation_context'], extensions, root, clock=_entry.ports.clock), [])

    def test_changed_checkpoint_file_bytes_are_rejected_before_review(self):
        engine, action, _, _ = self.fixture(stored=b'changed bytes')
        with tempfile.TemporaryDirectory() as directory, self.assertRaisesRegex(ValueError, 'checkpoint hash'):
            engine._context(action, Path(directory), execution_id='EX-review')

class ManifestIngressTests(unittest.TestCase):
    def test_produced_manifest_rejects_shape_damage_before_reading_artifacts(self):
        from do_math.context_store import verify_manifest_artifacts
        engine = Sim.activated().engine
        with tempfile.TemporaryDirectory() as directory:
            fitted, _ = package(engine, Path(directory))
            manifest = fitted['manifest']
            head = engine.store.save_with_state(engine.head, engine.instance, engine.runtime,
                                               artifacts=fitted['artifacts'])[0]
            self.assertEqual(verify_manifest_artifacts(
                manifest, lambda path: engine.store.read(path, head)), [])
            before = canonical_json(manifest)
            for fault, reason in (
                    ('role', 'invalid role input manifest role'),
                    ('contract', 'input does not bind the current response contract'),
                    ('documents', 'common documents must each occur exactly once'),
                    ('hash', 'input component requires exact byte hash'),
                    ('boolean_length', 'input component requires measured byte length'),
                    ('negative_length', 'input component requires measured byte length'),
                    ('order', 'candidate input requires a sealed population order'),
                    ('seed', 'candidate order requires a 256-bit seed'),
                    ('replay', 'candidate order replay differs from population or input basis')):
                changed = deepcopy(manifest)
                if fault == 'role':
                    changed['role'] = 'unknown-role'
                elif fault == 'contract':
                    changed['output_contract']['id'] = 'invalid-contract'
                elif fault == 'documents':
                    changed['documents'] = [row for row in changed['documents'] if row['path'] != 'GLOSSARY.md']
                elif fault == 'hash':
                    changed['prompt']['sha256'] = 'not-a-hash'
                elif fault.endswith('length'):
                    changed['prompt']['bytes'] = True if fault == 'boolean_length' else -1
                elif fault == 'order':
                    changed['candidate_order']['ids'] = ['duplicate', 'duplicate']
                elif fault == 'seed':
                    changed['candidate_order']['seed'] = 'not-a-seed'
                else:
                    changed['candidate_order']['basis']['snapshot'] = '0' * len(manifest['snapshot'])
                reads = []
                def read(path):
                    reads.append(path)
                    return engine.store.read(path, head)
                with self.subTest(fault=fault), self.assertRaises(ValueError) as rejected:
                    verify_manifest_artifacts(changed, read)
                self.assertIs(type(rejected.exception), ValueError)
                self.assertEqual(str(rejected.exception), reason)
                self.assertEqual(reads, [])
                self.assertEqual(canonical_json(manifest), before)
            self.assertEqual(engine.store.load()[0], head)
            self.assertEqual(engine.store.read(manifest['prompt']['artifact_ref'], head),
                             fitted['prompt'].encode('utf-8'))

    def test_repository_lengths_distinguish_unbound_absent_and_wrong_size_components(self):
        from do_math.context_store import verify_manifest_artifacts
        engine = Sim.activated().engine
        with tempfile.TemporaryDirectory() as directory:
            fitted, _ = package(engine, Path(directory))
            manifest = fitted['manifest']
            head = engine.store.save_with_state(engine.head, engine.instance, engine.runtime,
                                               artifacts=fitted['artifacts'])[0]
            def sizes(paths):
                return engine.store.blob_sizes(paths, head, missing='omit')
            self.assertEqual(verify_manifest_artifacts(manifest, None, artifact_sizes=sizes), [])
            raw = engine.store.read(manifest['prompt']['artifact_ref'], head)
            self.assertIs(type(raw), bytes)
            self.assertEqual(raw, fitted['prompt'].encode('utf-8'))
            self.assertEqual(len(raw), manifest['prompt']['bytes'])
            unbound = deepcopy(manifest)
            del unbound['prompt']['artifact_ref']
            self.assertEqual(verify_manifest_artifacts(unbound, None, artifact_sizes=sizes), ['prompt'])
            for fault, reason in (
                    ('missing', 'input artifact is missing: prompt'),
                    ('size', 'input artifact size differs: prompt')):
                changed = deepcopy(manifest)
                if fault == 'missing':
                    changed['prompt']['artifact_ref'] += '.absent'
                else:
                    changed['prompt']['bytes'] += 1
                with self.subTest(fault=fault), self.assertRaises(ValueError) as rejected:
                    verify_manifest_artifacts(changed, None, artifact_sizes=sizes)
                self.assertIs(type(rejected.exception), ValueError)
                self.assertEqual(str(rejected.exception), reason)
            self.assertEqual(engine.store.read(manifest['prompt']['artifact_ref'], head), raw)
            self.assertEqual(engine.store.load()[0], head)


    def test_loaded_input_with_one_unbound_component_names_the_missing_prompt(self):
        from do_math.activities import open_activity, assign_execution
        from do_math.state_checks import inspect_state, inspection_exit_code
        engine = Sim.activated().engine
        with tempfile.TemporaryDirectory() as directory:
            fitted, _ = package(engine, Path(directory))
            running = deepcopy(engine.runtime)
            activity_id = engine.ports.clock.new_id('AT')
            open_activity(running, activity_id=activity_id, activity_kind='research_plan',
                          owner_ref='engine', input_refs=[], opened_at=engine.ports.clock.now())
            execution = execution_lifecycle.create_execution(execution_id='EX-plan',
                owner_activity_id=activity_id, actor_kind='ai', input_manifest=fitted['manifest'],
                profile_ref=fitted['manifest']['execution_profile_ref'], created_at=engine.ports.clock.now())
            execution['role'] = fitted['manifest']['role']
            assign_execution(running, activity_id, execution)
            head = engine.store.save_with_state(engine.head, engine.instance, running,
                                               artifacts=fitted['artifacts'])[0]
            def inspect(snapshot):
                _, instance, runtime = engine.store.load(snapshot)
                before = canonical_json([instance, runtime])
                result = inspect_state(instance, runtime, requested_areas=['start_import_input'],
                    snapshot=snapshot, read_artifact=lambda path: engine.store.read(path, snapshot),
                    artifact_sizes=lambda paths: engine.store.blob_sizes(paths, snapshot, missing='omit'))
                self.assertEqual(canonical_json([instance, runtime]), before)
                return result
            baseline = inspect(head)
            _, instance, runtime = engine.store.load(head)
            del runtime['executions'][execution['id']]['input_manifest']['prompt']['artifact_ref']
            damaged = engine.store.save_with_state(head, instance, runtime)[0]
            result = inspect(damaged)
            message = execution['id'] + ': actual input bytes for prompt not examined'
            finding = {'area': 'start_import_input', 'status': 'incomplete', 'message': message,
                       'blocked_scope': [], 'evidence': ['state'], 'next_owner': 'maintenance'}
            self.assertEqual([row for row in result['findings'] if row['message'] == message], [finding])
            self.assertEqual([row for row in result['findings'] if row['message'] != message],
                             baseline['findings'])
            self.assertIn('start_import_input', result['not_checked'])
            self.assertEqual(inspection_exit_code(result), 1)
            self.assertEqual(engine.store.load()[0], damaged)
            self.assertEqual(engine.store.read(fitted['manifest']['prompt']['artifact_ref'], damaged),
                             fitted['prompt'].encode('utf-8'))

    def test_packaged_response_rejects_manifest_shape_and_unprovided_authority(self):
        from support.default_responder import DefaultResponder
        engine = Sim.activated().engine
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _, context = package(engine, root, 'maintenance')
            authored = DefaultResponder().respond('maintenance', context, root)
            output = integration.protocol_output(authored, {}, context)
            self.assertEqual(integration.inspect_bundles(output, {}, context), [])
            before = canonical_json([output, context])
            for fault, expected in (
                    ('shape', [('integration.manifest', 'output/integration_bundles/0/authority_refs',
                                "'not-an-array' is not of type 'array'", None)]),
                    ('authority', [('integration.authority_reference', 'output/integration_bundles',
                                    'authority is not in the fixed visible input: GR-unprovided',
                                    output['integration_bundles'][0]['integration_id'])])):
                changed = deepcopy(output)
                changed['integration_bundles'][0]['authority_refs'] = (
                    'not-an-array' if fault == 'shape' else ['GR-unprovided'])
                with self.subTest(fault=fault):
                    issues = integration.inspect_bundles(changed, {}, context)
                    self.assertEqual([(row['rule_id'], row['path'], row['message'], row['integration_id'])
                                      for row in issues], expected)
                    self.assertEqual(canonical_json([output, context]), before)



class PackagedInputTests(unittest.TestCase):
    def test_task_result_paths_survive_packaging_without_entering_validation_hashes(self):
        raw = b'\xff exact result bytes\n'
        result = {'execution_id': 'EX-work', 'report': 'Returned evidence', 'output_files': [
            {'path': 'proof.bin', 'artifact_ref': 'runtime/artifacts/BA-work/proof.bin',
             'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)}]}
        task = {'id': 'TK-result', 'revision': 1, 'status': 'waiting', 'results': [result]}
        engine = context_engine(runtime={'tasks': {task['id']: task}}, files={'runtime/artifacts/BA-work/proof.bin': raw})
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
        # The legacy source path (source.txt) named no store path; its bytes live below the artifacts here.
        source = b'fixture source for task context\n'
        instance['sources'][0].update(path='runtime/artifacts/BA-source/source.txt',
                                      sha256=hashlib.sha256(source).hexdigest())
        engine = context_engine(instance, runtime, files={instance['sources'][0]['path']: source})
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
            unbound = deepcopy(manifest)
            unbound['direct'][0].pop('artifact_ref')
            self.assertEqual(verify_manifest_artifacts(unbound, single, read_artifacts=batch),
                             verify_manifest_artifacts(unbound, artifacts.__getitem__))
            artifacts[manifest['prompt']['artifact_ref']] = b'corrupt'
            for reader in ({}, {'read_artifacts': batch}):
                with self.assertRaisesRegex(ValueError, 'input artifact bytes differ'):
                    verify_manifest_artifacts(manifest, artifacts.__getitem__, **reader)

    def test_catalog_keeps_aliases_identity_and_only_effective_summaries(self):
        from support.entry import entry
        _entry = entry()
        evidence, _, kid, aid = verified_knowledge()
        # Two effective assessments for the same item must not repeat its text.
        evidence, _ = knowledge_records.record_identity_assessment(evidence, kid,
            {'decision': 'match', 'basis': knowledge_records.identity_basis(evidence, kid)}, 'policy:2', runtime={}, clock=_entry.ports.clock)
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

    def test_relation_uses_sealed_domain_records_at_local_and_central_check(self):
        from support.entry import entry
        _entry = entry()
        state, _, kid, aid = verified_knowledge()
        fid = state['knowledge'][kid]['formal_result_id']
        claim = {'kind': 'formally_implies', 'source': kid, 'target': kid, 'confirmed_scope': 'reflexive'}
        state['identity_assessments'][aid]['relation_claim'] = claim
        relation = {**claim, 'formal_result_refs': [fid], 'assessment_refs': [aid], 'evidence_refs': [kid], 'evidence': kid}
        engine = context_engine(state)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fitted, fixed = package(engine, root, 'research_work')
            output = {**common('research_work'), 'outcome': 'submitted', 'report': 'Reflexive relation'}
            extensions = {'relations': [relation]}
            (root / 'activity-extensions.json').write_bytes(canonical_json(extensions))
            seal_response(output, fixed, root)
            draft = root / 'draft.json'
            draft.write_bytes(canonical_json(output))
            check = submission.producer_check(root, draft, clock=_entry.ports.clock)
            self.assertTrue(check['passed'], check['issues'])
            sealed = submission.seal_submission(root, 'draft.json', execution_id='EX-plan',
                context=fixed, schema=contracts.schema_for('research_work'), max_artifact_bytes=2000000, clock=_entry.ports.clock)
            self.assertTrue(sealed['passed'], sealed['check']['issues'])
            artifacts = engine._input_artifacts('BA-plan', contracts.schema_for('research_work'), fitted, root)
            self.assertIn('runtime/artifacts/BA-plan/input/submission/relation-state.json', artifacts)
            stopped = knowledge_records.set_assessment_use(engine.instance, aid, 'withdrawn', 'recheck', 'reviewer')
            with self.assertRaisesRegex(ValueError, 'invalid relation'):
                knowledge_io.import_relation(stopped, relation, source_ref='submission', actor_ref='EX-plan', clock=_entry.ports.clock)
            for key, wrong in [('target', 'KN-absent'), ('confirmed_scope', 'different')]:
                bad = deepcopy(extensions)
                bad['relations'][0][key] = wrong
                self.assertTrue(submission.payload_issues(output, contracts.schema_for('research_work'), fixed, bad, root, clock=_entry.ports.clock))
            (root / fixed['relation_validation_source']['path']).write_bytes(b'{}')
            issues = submission.payload_issues(output, contracts.schema_for('research_work'), fixed, extensions, root, clock=_entry.ports.clock)
            self.assertTrue(any('input is missing or corrupt' in row['message'] for row in issues), issues)


class InputManifestConnections(unittest.TestCase):
    def maintenance_engine(self):
        """The legacy ``routing_engine`` state: ``surface_state`` with the context additions it made."""
        engine = context_engine()
        workspace = engine.instance['workspace']
        engine.instance, engine.runtime = surface_state()
        engine.instance.update(relations=[], goal_status='unresolved', workspace=workspace)
        engine.runtime.update(inputs=[], questions=[])
        return engine

    def test_delivered_previous_hashes_pass_the_actual_live_impact_gate(self):
        from support.entry import entry
        _entry = entry()
        from do_math import knowledge
        from support.role_answers import candidate
        engine = self.maintenance_engine()
        engine.instance, engine.runtime, kid = knowledge_io.import_candidate(engine.instance, engine.runtime,
            {"kind": "observation", "title": "Record", "statement": "A bounded observation", "summary": "Observed",
                "explanation": "Exact e\u0301 source", "lean_code": "", "declaration_names": [], "dependencies": []},
            source_ref="EX-author", actor_ref="EX-author", clock=_entry.ports.clock)
        task = contracts.task_candidate_record(candidate("bounded work"), task_id="TA-one")
        task.update(status="candidate", results=[])
        engine.runtime["tasks"][task["id"]] = task
        with tempfile.TemporaryDirectory() as temporary:
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
        from support.entry import entry
        _entry = entry()
        engine = self.maintenance_engine()
        profile = next(row for row in engine.instance["execution_profiles"].values() if row["role"] == "maintenance")
        schema = contracts.schema_for("maintenance")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            context = {"action": {"role": "maintenance"}, "execution_id": "EX-maintenance"}
            # The engine archives each role input once, below its input bundle.
            fitted = prepare_role_input(context, instance=engine.instance, runtime=engine.runtime,
                role="maintenance", profile=profile, snapshot="a" * 40, workspace=root,
                activity_id="AC-1", output_schema=schema, documents=engine._documents["maintenance"],
                artifact_prefix="runtime/artifacts/BA-input", clock=_entry.ports.clock)
            artifacts = engine._input_artifacts("BA-input", schema, fitted, root)
            self.assertEqual(json.loads(artifacts["runtime/artifacts/BA-input/manifest.json"]), fitted["manifest"])
            self.assertEqual(artifacts["runtime/artifacts/BA-input/input.txt"], fitted["prompt"].encode("utf-8"))
            for entry in fitted["manifest"]["catalog"]:
                raw = artifacts["runtime/artifacts/BA-input/" + entry["path"]]
                self.assertEqual(hashlib.sha256(raw).hexdigest(), entry["sha256"])


class PreparedInputTests(unittest.TestCase):
    def test_discard_records_cancelled_preparation_and_explicit_continuation(self):
        engine = Sim.activated().engine
        action = {"id": "AC-one", "role": "research_preparation"}
        engine.runtime["queue"] = [action]
        execution = engine._register_execution(action, {"id": "EX-one", "role": action["role"], "status": "queued"})
        execution_lifecycle.begin_preparation(execution, at=engine.ports.clock.now())
        base = Path(engine.instance["workspace"]) / "runs/EX-one"
        base.mkdir(parents=True)
        (base / "partial").write_text("incomplete private input")
        before = engine.head
        engine._discard_prepared_input(base, "EX-one")
        ended = engine.runtime["executions"]["EX-one"]
        self.assertEqual(ended["outcome"], "cancelled")
        self.assertEqual(engine.runtime["queue"][0]["continuation_of"], "EX-one")
        self.assertEqual(engine.runtime["queue"][0]["owner_activity_id"], ended["owner_activity_id"])
        self.assertFalse(base.exists())
        # The discard is saved: the published state holds the cancelled execution and its continuation.
        self.assertNotEqual(engine.head, before)
        _, _, published = engine.store.load()
        self.assertEqual(published["executions"]["EX-one"]["outcome"], "cancelled")
        self.assertEqual(published["queue"][0]["continuation_of"], "EX-one")

    def test_runner_takes_its_tools_only_from_the_pinned_profile(self):
        """The real runner and Codex adapter start the worker; the Jobs fake's worker program records its request."""
        from support.entry import entry
        _entry = entry()
        from do_math.launch import ticket
        from do_math.model_runner import ModelRunner
        from do_math.configuration import DEFAULT_CONFIG
        from support.fakes.clock import FakeClock
        from support.fakes.jobs import FakeJobs
        requests = []

        def worker(argv, cwd, env):
            requests.append(json.loads(Path(argv[2]).read_text(encoding='utf-8')))
            return 1
        jobs = FakeJobs([(lambda argv: Path(argv[1]).name == 'codex_worker.py', worker)])
        clock = FakeClock()
        profile = next(p for p in execution_profiles.build_profiles(DEFAULT_CONFIG, host=_entry.ports.host)["execution_profiles"].values()
                       if p["role"] == "research_work")
        tools = execution_profiles.runner_tools(profile)
        prompt = execution_profiles.prepare_prompt("fixture", profile)
        runner = ModelRunner(jobs=jobs, clock=clock, environment=_entry.environment, host_id=_entry.host_id)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            launch = {**ticket("EX-tools", profile, jobs=jobs, clock=clock), 'phase': 'dispatched'}
            (root / "workspace").mkdir()
            options = dict(prompt=prompt, input_seal=execution_profiles.prompt_seal(prompt), output_schema={},
                workspace=root / "workspace", model=profile["ai"]["model"].removeprefix("claude:"), effort=profile["ai"]["effort"],
                timeout_seconds=1, execution_id="EX-tools", profile=profile, launch_ticket=launch)
            runner.run(**options, evidence_dir=root / "evidence")
            self.assertEqual(len(requests), 1)
            self.assertEqual(requests[0].get("scholarly_server"), tools["scholarly_server"])
            for name, value in (("scholarly_server", {"command": "changed", "args": []}),
                                ("claude_only_assigned_model", False)):
                with self.subTest(name=name), self.assertRaisesRegex(ValueError, "pinned profile supplies"):
                    runner.run(**options, evidence_dir=root / name, **{name: value})
            self.assertEqual(len(requests), 1, 'a refused override starts no worker')


class ArchivedControlInputTests(unittest.TestCase):
    def test_large_control_is_archived_before_reference_catalog_construction(self):
        from support.entry import entry
        _entry = entry()
        import base64
        engine = Sim.activated().engine
        request = {'id': 'UC-large', 'action': 'source', 'origin': 'user', 'config': {
            'name': 'large-notes.txt', 'body_base64': base64.b64encode(b'notes ' * 20000).decode('ascii')}}
        context = {'action': {'id': 'AC-test', 'role': 'maintenance'}, 'execution_id': 'EX-test',
                   'recent_history': [{'kind': 'user_control', 'request': request}]}
        profile = next(p for p in engine.instance['execution_profiles'].values() if p['role'] == 'maintenance')
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result = prepare_role_input(context, instance=engine.instance, runtime=engine.runtime, role='maintenance',
                profile=profile, snapshot=engine.head, workspace=root / 'input-case', activity_id='AY-test',
                install_submission_tools=True, max_artifact_bytes=1000000, clock=_entry.ports.clock)
            validation = result['validation_context']
            ref = validation['recent_history'][0]['request_source_ref']
            self.assertEqual(json.loads((root / 'input-case' / ref['path']).read_bytes()), request)
            self.assertLess(len(canonical_json(validation['recent_history'])), 1000)
            self.assertLess(len(validation['reference_catalog']), 20)


class FormalJudgmentInputTests(unittest.TestCase):
    def assert_judged(self, view, verification):
        self.assertEqual(view, {name: verification[name] for name in JUDGED})

    def assert_environment(self, formal):
        # verified_knowledge's trust environment TE-test allows no axiom.
        self.assertEqual((formal.pop('trust_environment_id'), formal.pop('allowed_axioms')), ('TE-test', []))

    def test_goal_audit_receives_the_judged_formal_result(self):
        instance, runtime, kid, verification = central_check_knowledge()
        engine = context_engine(instance, runtime)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            context = engine._context({'role': 'goal_audit'}, root)
            from support.entry import entry
            from support.role_input_requirements import assert_judgment_inputs
            profile = next(p for p in engine.instance['execution_profiles'].values() if p['role'] == 'goal_audit')
            fitted = prepare_role_input(context, instance=engine.instance, runtime=engine.runtime,
                role='goal_audit', profile=profile, snapshot=engine.head, workspace=root,
                activity_id='AY-audit', clock=entry().ports.clock)
            assert_judgment_inputs(self, 'goal_audit', fitted, root, producer_context=context)
            item, = context['eligible_knowledge']
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


class RoleScopeContextTests(unittest.TestCase):
    def test_self_check_evidence_follows_the_submission_citation_rule(self):
        # Records of the input snapshot and the execution's preserved workspace files are citable.
        engine = context_engine()
        execution = {'id': 'EX-1'}
        issue(engine, execution, {'reference_catalog': [], 'record_index': {'runtime/activities': ['AC-1']}}, 'BA-issued')
        cited = ['AC-1', 'checkpoint.json', 'workspace:checkpoint.json', '.scratch/note.txt', 'absent.txt']
        response = {'obligation_id': 'SC-1', 'execution_id': 'EX-1', 'rule_revision': 0, 'progress': 'progress',
                    'attempts': ['read the checkpoint'], 'next_method': 'continue',
                    'rule_results': [{'rule_id': 'R-1', 'status': 'normal', 'evidence_refs': cited,
                                      'missing_evidence_refs': [], 'reason': 'compared the checkpoint'}]}
        workspace = Path(engine.instance['workspace']) / 'runs/EX-1/workspace'
        (workspace / '.scratch').mkdir(parents=True)
        (workspace / 'checkpoint.json').write_text('{}', encoding='utf-8')
        (workspace / '.scratch/note.txt').write_text('scratch', encoding='utf-8')
        self.assertEqual(engine._control_evidence_refs(execution, response),
                         {'AC-1', 'checkpoint.json', 'workspace:checkpoint.json'})

    def test_task_readiness_reaches_its_readers_in_their_scope(self):
        # 후보-준비.md 61 checks which tasks wait for external input; 연구-수행.md 17 reads its own task's basis.
        from support.record_builders import task_contract
        instance, runtime = surface_state()
        runtime['tasks'] = {identifier: {**task_contract(), 'id': identifier} for identifier in ('TK-1', 'TK-2')}
        engine = context_engine(instance, runtime)
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
        for role, expected in (('goal_audit', True), ('research_preparation', False)):
            with self.subTest(role=role), tempfile.TemporaryDirectory() as directory:
                row, = engine._context({'role': role}, Path(directory))['knowledge_catalog']
                self.assertEqual('review_cycle_source' in row, expected)
                self.assertEqual((Path(directory) / 'input' / 'review-cycles').exists(), expected)


class ReviewSeatInputTests(unittest.TestCase):
    def test_identity_review_maps_what_it_does_not_inline_and_never_receives_its_private_keys(self):
        """About 11 s, over the 2 s Sim budget: formal work runs to its first queued identity review seat."""
        # 계약/동일성-검토.md 47 and GLOSSARY 「검토 자리」: no author or peer execution context.
        from do_math import governance
        from support.default_responder import DefaultResponder
        from support.engine_context import is_map_entry, prepare
        sim = Sim.activated()
        sim.model.responder = DefaultResponder(formal=True)
        engine = sim.engine

        def seat():
            return next((a for a in engine.runtime['queue'] if a['role'] == 'identity_review'
                         and a.get('review_cycle_id') and a.get('stage') == 'initial'), None)
        for _ in range(40):
            if seat():
                break
            engine.run(max_steps=1)
        action = seat()
        self.assertIsNotNone(action, 'formal work did not reach an initial identity review seat')
        action = {**deepcopy(action), 'grant_id': governance.authorize(
            engine.instance, action, runtime=engine.runtime, at=sim.clock.now())['grant_id']}
        with tempfile.TemporaryDirectory() as directory:
            review = engine._prepare_review_context(action, Path(directory) / 'seat')['context']
            fitted = prepare(action, {'role_review': review}, instance=engine.instance, runtime=engine.runtime,
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


class RoleContractInputTests(unittest.TestCase):
    def test_every_role_preserves_its_declared_judgment_inputs_or_exact_sources(self):
        """All ten real context producers and packagers; no model call per role.

        The review scene's one shared public build includes the actual formal
        worker. Stage/recovery variants have separate existing owner cases;
        this sweep checks the entire role population at its normal entry.
        """
        from do_math.role_input_requirements import ROLE_INPUT_REQUIREMENTS
        from support.engine_lifecycle import applied, clear_work, task
        from support.review_sim import opened_sim
        from support.role_input_requirements import assert_judgment_inputs
        self.assertEqual(set(ROLE_INPUT_REQUIREMENTS), set(contracts.ROLES))
        for role in contracts.ROLES:
            with self.subTest(role=role), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                sim = opened_sim() if role == 'identity_review' else Sim.activated()
                engine = sim.engine
                if role == 'identity_review':
                    action = deepcopy(next(a for a in sim.runtime['queue'] if a['role'] == role))
                else:
                    clear_work(sim)
                    action = {'id': 'AC-input-requirement', 'role': role}
                    if role in {'research_preparation', 'research_plan', 'research_work',
                                'task_contract_review', 'supplemental_research', 'operational_review'}:
                        row = task(engine, approved=False)
                        if role == 'operational_review':
                            action['target'] = row['producer_execution']
                        elif role in {'research_work', 'task_contract_review', 'supplemental_research'}:
                            action['target'] = row['id']
                        engine._save()
                    if role == 'intent_interpretation':
                        applied(sim, 'input', text='Keep the exact supplied source and its current constraints.')
                        action = deepcopy(next(a for a in sim.runtime['queue'] if a['role'] == role))
                context = engine._context(action, root)
                profile = execution_profiles.resolve_profile(engine.instance['execution_profiles'],
                    engine.instance['role_profile_refs'][role][0])
                fitted = prepare_role_input(context, instance=engine.instance, runtime=engine.runtime,
                    role=role, profile=profile, snapshot=engine.head, workspace=root,
                    activity_id='AY-input-requirement', install_submission_tools=True,
                    clock=sim.clock)
                self.assertIsNone(fitted['overflow'])
                assert_judgment_inputs(self, role, fitted, root, producer_context=context)
                from support.role_input_requirements import assert_missing_judgment_inputs_rejected
                assert_missing_judgment_inputs_rejected(self, role, fitted, root, producer_context=context)
                from support.role_input_requirements import assert_unreadable_requirement_rejected
                assert_unreadable_requirement_rejected(self, role, fitted, root, producer_context=context)


class FollowupDocumentTests(unittest.TestCase):
    """From the Sim's public activation; the legacy tests restored the synthetic active template."""

    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.sim = Sim.activated()
        self.engine = self.sim.engine

    def proposal(self, title, **kwargs):
        from support.purpose_answers import candidate
        value = candidate(title, **kwargs)
        # The adopted research work editions (the registry also keeps the editions activation replaced).
        value['profile_refs'] = deepcopy(self.engine.instance['role_profile_refs']['research_work'])
        return value

    def test_planning_roles_receive_the_complete_current_settings(self):
        from support.entry import entry
        _entry = entry()
        self.sim.control('configure', config={'observation_interval_seconds': 417, 'review_research_limit': 4})
        self.engine.process_controls()
        engine = self.engine
        self.assertEqual((engine.instance['config']['observation_interval_seconds'],
                          engine.instance['config']['review_research_limit']), (417, 4))
        for role in ("research_preparation", "research_plan"):
            workspace = self.root / role
            context = engine._context({"role": role}, workspace)
            # The engine projects no raw configuration; the role input preserves it from state.
            self.assertNotIn("config", context)
            profile = next(p for p in engine.instance["execution_profiles"].values() if p["role"] == role)
            fitted = prepare_role_input(context, instance=engine.instance, runtime=engine.runtime, role=role,
                profile=profile, snapshot=engine.head, workspace=workspace, activity_id="AC-" + role, clock=_entry.ports.clock)
            from support.role_input_requirements import assert_judgment_inputs
            assert_judgment_inputs(self, role, fitted, workspace, producer_context=context)
            source = fitted["context"]["configuration_source"]
            self.assertEqual(json.loads((workspace / source["path"]).read_bytes()), engine.instance["config"])

    def test_prepared_observation_rule_reaches_contract_review(self):
        from support.purpose_answers import common as purpose_common
        engine = self.engine
        # The preparations' issued inputs fix which task inputs they could name; these name none.
        issued = {"available_input_refs": [], "supplied_record_ids": []}
        rule = {"id": "branches", "operator": "counter_gte", "threshold": 3,
                "subject": {"kind": "counter", "id": "branches"},
                "basis": {"source": "checkpoint", "unit": "count"},
                "repeat_interval": 3, "required_evidence": ["EV-branch"]}
        engine.runtime["executions"]["EX-preparation"] = issue(engine, {"status": "ended", "input_snapshot": engine.head,
            "extensions": {"task_conditions": [{"task_title": "Bounded branch investigation", "observation_rules": [rule]}]}},
            issued, 'BA-preparation')
        engine._apply({"role": "research_preparation"},
                      {**purpose_common("Prepare an observable investigation"), "candidates": [self.proposal("Bounded branch investigation")]},
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
        engine.runtime["executions"]["EX-revision"] = issue(engine, {"status": "ended", "input_snapshot": engine.head,
            "extensions": {"task_conditions": [{"task_title": task["title"], "observation_rules": [revised_rule]}]}},
            issued, 'BA-revision')
        engine._apply({"role": "research_preparation"},
                      {**purpose_common("Revise the observation boundary"), "candidates": [self.proposal(task["title"], revises=task["id"])]},
                      "EX-revision")
        self.assertEqual(engine.runtime["tasks"][task["id"]]["initial_observation_rules"], [revised_rule])
        self.assertNotIn(task["id"], engine.runtime["task_observation_rules"],
                         "rules from an earlier contract must not override the new reviewed initial rules")

    def test_old_rejected_preparation_remains_readable_after_recent_history_moves(self):
        from support.purpose_answers import candidate, common as purpose_common
        from do_math.execution_lifecycle import transition_execution
        engine = self.engine
        output = {**purpose_common("Investigated the earlier approach"), "candidates": [candidate("Earlier proposal")]}
        result = canonical_json({"status": "completed", "output": output, "error": None})
        reference = "runtime/artifacts/BA-old/result.json"
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


if __name__ == '__main__':
    unittest.main()
