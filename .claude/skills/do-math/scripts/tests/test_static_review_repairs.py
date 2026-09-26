"""Actual input packaging/checker boundaries; no provider or scheduler launches.

Formal and identity receipts are synthetic evidence, not a Lean verification.
"""
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import Mock, create_autospec, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math import contracts, integration, knowledge_io, knowledge_records, planning, repair_execution, submission
from do_math.question_engine import QuestionEngineMixin
from do_math.context_store import fit_context, prepare_role_input
from do_math.engine import ResearchEngine, control
from do_math.repository import ResearchRepository, canonical_json
from test_redesign_SURFACE import surface_state
import test_redesign_KNOWLEDGE as knowledge_fixtures
from test_redesign_TASKS import approved_fixture, approve, disposition
from test_engine import common
from research_fixtures import bare_engine, new_instance, seal_response

AT = '2026-09-22T00:00:00+00:00'


def context_engine(instance=None, runtime=None):
    """Keep the real context producer; replace unrelated host observations."""
    base, running = surface_state()
    base.update(relations=[], goal_status='unresolved', lifecycle={'state': 'active'})
    running.update(inputs=[], questions=[])
    running['executions'] = {}
    if instance:
        profiles = {**base['execution_profiles'], **instance.get('execution_profiles', {})}
        base.update(instance)
        base['execution_profiles'] = profiles
    if runtime:
        running.update(runtime)
    engine = bare_engine(base, running, head='a' * 40, store=create_autospec(ResearchRepository, instance=True))
    engine.store.read_many.side_effect = lambda paths, snapshot: {p: engine.store.read(p, snapshot) for p in paths}
    engine._documents = {role: contracts.prompt_documents(role) for role in ('research_preparation', 'research_plan', 'research_work')}
    engine._preparation_checkpoint = create_autospec(engine._preparation_checkpoint, side_effect=lambda: None)
    engine._session_slots = create_autospec(engine._session_slots)
    engine._academic_status = create_autospec(engine._academic_status, side_effect=lambda: {})
    engine._planning_history = create_autospec(engine._planning_history, side_effect=lambda *args: [])
    engine._execution_profile = create_autospec(engine._execution_profile,
                                                side_effect=ValueError('no compiler launched in input test'))
    engine._ensure_academic_followup = create_autospec(engine._ensure_academic_followup, side_effect=lambda: None)
    engine._record_academic_assessment = create_autospec(engine._record_academic_assessment, side_effect=lambda *args: None)
    return engine


def package(engine, root, role='research_plan', target=None):
    action = {'id': 'AC-plan', 'role': role}
    if target:
        action['target'] = target
    context = engine._context(action, root, execution_id='EX-plan')
    profile = next(p for p in engine.instance['execution_profiles'].values() if p['role'] == role)
    result = prepare_role_input(context, instance=engine.instance, runtime=engine.runtime, role=role,
        profile=profile, snapshot=engine.head, workspace=root, activity_id='AC-1',
        install_submission_tools=True, artifact_prefix='runtime/artifacts/BA-plan')
    fixed = submission.load_json((root / 'input/submission/context.json').read_bytes())
    return result, fixed


def initial_failure_engine(root, kind='execution_failure', stage='interpret'):
    from do_math import activities, execution_lifecycle, execution_profiles
    from test_lifecycle_engine import FakeEngine
    seed = FakeEngine(root)
    seed.grant('GR-init', True)
    seed.instance['grants']['GR-init']['roles'].append('maintenance')
    lifecycle = seed.instance['lifecycle']
    from do_math.model_policy import selection
    selected = selection(seed.instance['config'], {'role': 'intent_interpretation'}, {}, {},
                         instance=seed.instance)['profile_ref']
    profile = execution_profiles.resolve_profile(seed.instance['execution_profiles'], selected)
    lifecycle.update(input_id='UI-original', adoption={'initial_grant_ids': ['GR-init'],
        'initial_profile_ref': execution_profiles.profile_ref(profile)})
    seed.runtime['inputs'] = [{'id': 'UI-original', 'config': {}, **lifecycle['immutable_input']}]
    engine = bare_engine(seed.instance, seed.runtime, head='a' * 40, store=create_autospec(ResearchRepository, instance=True))
    engine.lifecycle_clock = seed.lifecycle_clock
    engine.lifecycle_monotonic = seed.lifecycle_monotonic
    action = {'id': 'AC-original', 'role': 'intent_interpretation', 'target': 'UI-original',
              'stage': stage, 'owner_activity_id': 'AY-original'}
    activities.open_activity(engine.runtime, activity_id='AY-original', activity_kind='intent_interpretation',
        owner_ref='engine', input_refs=['UI-original'], opened_at=AT)
    failed = execution_lifecycle.create_execution(execution_id='EX-bad', owner_activity_id='AY-original',
        actor_kind='ai', input_manifest={}, profile_ref=execution_profiles.profile_ref(profile), created_at=AT)
    from research_fixtures import dispatched_launch
    failed['launch_ticket'] = {**dispatched_launch(failed['id'], profile), 'phase':'finished'}
    failed.update(role=action['role'], action=deepcopy(action), capacity={'local_termination': 'confirmed'})
    activities.assign_execution(engine.runtime, 'AY-original', failed)
    execution_lifecycle.transition_execution(failed, 'starting', at=AT)
    execution_lifecycle.transition_execution(failed, 'stopping', at=AT, stop_phase='terminating')
    execution_lifecycle.transition_execution(failed, 'ended', at=AT, outcome='execution_incomplete')
    activities.wait_for(engine.runtime, 'AY-original', reason=kind, condition={'action_ids': [action['id']]},
                        next_owner='maintenance', at=AT)
    wait = {'kind': kind, 'action': action, 'execution_id': 'EX-bad', 'reason': 'synthetic failure'}
    if kind == 'output_validation':
        action.update(repair_attempt=2, repair={'execution_id': 'EX-bad', 'issues': [], 'retry_bundle_ids': ['IN-pending']})
    engine.runtime.update(queue=[], waiting_actions={action['id']: wait})
    return engine, action, wait


class InputBoundaryRepairs(unittest.TestCase):
    def test_accepted_maintenance_question_reads_its_single_sealed_source(self):
        engine = context_engine()
        action = {'id': 'AC-sealed-question', 'role': 'maintenance'}
        ref = 'runtime/artifacts/BA-sealed/submission/output.json'
        engine.runtime['executions']['EX-sealed-question'] = {
            'id': 'EX-sealed-question', 'role': 'maintenance', 'status': 'ended',
            'action': action, 'submission_intent': {'output_ref': ref}}
        output = {**common('maintenance'), 'questions': ['Which result should be used?']}
        engine._record_output_questions(action, output, 'EX-sealed-question')
        engine._record_output_questions(action, output, 'EX-sealed-question')
        self.assertEqual(len(engine.runtime['question_links']), 1)
        self.assertEqual(engine.runtime['question_links'][0]['source_ref'], ref)
        engine.store.read_many.side_effect = lambda paths, snapshot: {ref: canonical_json(output)}
        self.assertEqual(engine._question_view()[0]['text'], 'Which result should be used?')

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

    def test_running_maintenance_question_preview_uses_captured_candidate_only(self):
        engine = context_engine()
        action = {'id': 'AC-preview-question', 'role': 'maintenance'}
        execution_id = 'EX-preview-question'
        engine.runtime['executions'][execution_id] = {
            'id': execution_id, 'role': 'maintenance', 'status': 'running', 'action': action}
        output = {**common('maintenance'), 'questions': ['Which condition needs a decision?']}
        context = {'action': action, 'snapshot': engine.head, 'execution_id': execution_id}
        ref = 'runtime/artifacts/preview/' + execution_id + '/output.json'
        artifacts = {ref: canonical_json(output)}
        before = canonical_json(engine.runtime)
        preview = integration.preview_bundles(engine.instance, engine.runtime, output, {}, context,
            execution_id=execution_id,
            apply_bundle=lambda instance, runtime, bundle: engine._apply_bundle_candidate(
                instance, runtime, bundle, action=action, execution_id=execution_id,
                extensions={}, question_source_ref=ref),
            validate_current=lambda *_: None,
            validate_candidate=lambda instance, runtime, bundle: engine._validate_bundle_candidate(
                instance, runtime, bundle, artifacts=artifacts))
        self.assertEqual(preview['status'], 'accepted', preview['issues'])
        self.assertEqual(canonical_json(engine.runtime), before)
        self.assertEqual(engine.store.validate_candidate.call_count, 1)
        self.assertEqual(preview['runtime']['question_links'][0]['source_ref'], ref)
        self.assertNotIn('artifact_bundle', engine.runtime['executions'][execution_id])

    def test_profile_query_document_reads_cli_result_envelope(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repo = root / 'repo'
            instance_id = new_instance(repo, goal='Check profile query', workspace=root / 'work')
            engine = ResearchEngine(repo, instance_id)
            allowed = next(iter(engine.instance['role_profile_refs'].values()))[0]
            selected = engine.instance['execution_profiles'][allowed['id']]
            document = Path(__file__).resolve().parents[2] / 'references' / '초기화-운전.md'
            lines = document.read_text(encoding='utf-8').splitlines()
            first = next(index for index, line in enumerate(lines) if line.startswith('$dmPage = (python $dmCli query '))
            last = next(index for index in range(first, len(lines))
                        if lines[index].startswith('$dmProfileRecords | Select-Object'))
            query = lines[first:last + 1]
            selection_index = next(index for index, line in enumerate(lines)
                                   if line.startswith('$dmSelectedProfiles = @('))
            refs_index = next(index for index in range(selection_index, len(lines))
                              if lines[index].startswith('$dmProfileRefs = @('))
            selection = lines[selection_index:refs_index]
            environment = {**os.environ, 'DM_CLI': str(Path(__file__).resolve().parents[1] / 'do_math.py'),
                           'DM_REPO': str(repo), 'DM_INSTANCE': instance_id,
                           'DM_CHOSEN': selected['id']}
            self.assertGreater(len(engine.instance['execution_profiles']), 10)
            for page_size in (1000, 10):
                with self.subTest(page_size=page_size):
                    page_query = [line.replace('--limit 1000', '--limit ' + str(page_size)) for line in query]
                    script = '\n'.join(['$dmCli = $env:DM_CLI', '$dmRepository = $env:DM_REPO',
                                        '$dmInstance = $env:DM_INSTANCE', *page_query,
                                        '$dmChosenIds = @($env:DM_CHOSEN)', *selection,
                                        '@($dmSelectedProfiles | Select-Object id, revision, sha256) | ConvertTo-Json -Compress -Depth 5'])
                    result = subprocess.run(['pwsh', '-NoProfile', '-NonInteractive', '-Command', script],
                                            env=environment, capture_output=True, text=True, encoding='utf-8')
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(json.loads(result.stdout.strip().splitlines()[-1]),
                                     {'id': selected['id'], 'revision': selected['revision'], 'sha256': selected['sha256']})
                    if page_size == 1000:
                        wrong = selection[:1] + ["$dmSelectedProfiles[0].sha256 = '0' * 64"] + selection[1:]
                        invalid = '\n'.join(['$dmCli = $env:DM_CLI', '$dmRepository = $env:DM_REPO',
                                             '$dmInstance = $env:DM_INSTANCE', *page_query,
                                             '$dmChosenIds = @($env:DM_CHOSEN)', *wrong])
                        rejected = subprocess.run(['pwsh', '-NoProfile', '-NonInteractive', '-Command', invalid],
                                                  env=environment, capture_output=True, text=True, encoding='utf-8')
                        self.assertNotEqual(rejected.returncode, 0)
                        self.assertIn('허용 참조', rejected.stderr)

    def test_unchanged_source_control_publishes_one_replayable_receipt(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repo = root / 'repo'
            source = root / 'source.txt'
            source.write_text('fixed source\n', encoding='utf-8')
            instance_id = new_instance(repo, goal='Check source receipts', workspace=root / 'work', sources=[source])
            engine = ResearchEngine(repo, instance_id)
            before = deepcopy(engine.instance['sources'][0])
            sent = control(repo, instance_id, 'source', config={'path': str(source)},
                           request_id='UC-unchanged-source')
            self.assertEqual(sent['effect'], 'pending engine processing')
            engine._controls(pump=False)
            receipt = engine.control_result('UC-unchanged-source')
            self.assertEqual(receipt['effect'], 'applied')
            self.assertEqual(receipt['reason'], 'source content unchanged')
            self.assertEqual(engine.instance['sources'][0], before)
            replay = control(repo, instance_id, 'source', config={'path': str(source)},
                             request_id='UC-unchanged-source')
            self.assertEqual(replay['snapshot'], receipt['snapshot'])
            self.assertEqual(len([row for row in engine.runtime['history']
                if row.get('request', {}).get('id') == 'UC-unchanged-source']), 1)
            source.write_text('updated source\n', encoding='utf-8')
            control(repo, instance_id, 'source', config={'path': str(source)},
                    request_id='UC-changed-source')
            engine._controls(pump=False)
            self.assertEqual(engine.instance['sources'][0]['revision'], 2)
            self.assertEqual(engine.store.read(engine.instance['sources'][0]['path'], engine.head),
                             source.read_bytes())

    def test_operational_question_uses_exact_execution_or_sealed_source_coordinate(self):
        engine = bare_engine()
        engine.instance = {'decisions': {}}
        engine.head = 'fixed'
        engine.store = create_autospec(ResearchRepository, instance=True)
        engine.store.read_many.return_value = {'sealed-output.json': canonical_json({
            'disposition': {'question': 'Question from the sealed response'}})}
        engine.runtime = {'executions': {
            'EX-current': {'id': 'EX-current', 'role': 'operational_review',
                           'output': {'disposition': {'question': 'Choose the next action'}}},
            'EX-missing': {'id': 'EX-missing', 'role': 'operational_review', 'output': {}}},
            'question_links': [
                {'id': 'QU-current', 'origin_execution_id': 'EX-current',
                 'origin_field': 'output/disposition/question', 'owner': 'user', 'status': 'open'},
                {'id': 'QU-wrong', 'origin_execution_id': 'EX-current',
                 'origin_field': 'disposition/question', 'owner': 'user', 'status': 'open'},
                {'id': 'QU-missing', 'origin_execution_id': 'EX-missing',
                 'origin_field': 'output/disposition/question', 'owner': 'user', 'status': 'open'},
                {'id': 'QU-sealed', 'origin_execution_id': 'EX-current', 'source_ref': 'sealed-output.json',
                 'origin_field': 'disposition/question', 'owner': 'user', 'status': 'open'}]}
        view = {row['id']: row for row in QuestionEngineMixin._question_view(engine)}
        self.assertEqual(view['QU-current']['text'], 'Choose the next action')
        self.assertEqual(view['QU-sealed']['text'], 'Question from the sealed response')
        for identifier in ('QU-wrong', 'QU-missing'):
            self.assertIsNone(view[identifier]['text'])
            self.assertEqual(view[identifier]['source_status'], 'unavailable')
        self.assertEqual(QuestionEngineMixin._user_questions(engine),
                         ['Choose the next action', 'Question from the sealed response'])

    def test_planning_keeps_completed_report_and_active_work_as_readable_context(self):
        selected, instance, runtime = approved_fixture()
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
        approve(selected, engine.instance, engine.runtime)
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
        evidence, _, kid, aid = knowledge_fixtures.KnowledgeRedesign().verified()
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
        task, instance, runtime = approved_fixture()
        raw = b'valid evidence\n'
        instance['sources'][0]['sha256'] = hashlib.sha256(raw).hexdigest()
        task['occurrence_condition'] = {'op': 'artifact_valid', 'artifact_ref': {
            'snapshot': 'a' * 40, 'path': 'runtime/artifacts/BA-evidence/proof.txt',
            'sha256': hashlib.sha256(raw).hexdigest()}}
        approve(task, instance, runtime)
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
            output = {**common('research_plan'), 'dispositions': [disposition(task['id'])]}
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
            approve(extra, engine.instance, engine.runtime)
            engine._apply_plan(output, 'EX-plan')
            self.assertEqual([a['target'] for a in engine.runtime['queue']], [task['id']])

    def test_selected_candidate_still_requires_current_authority(self):
        engine, task = self.artifact_engine()
        with tempfile.TemporaryDirectory() as directory:
            _, fixed = package(engine, Path(directory))
            output = {**common('research_plan'), 'dispositions': [disposition(task['id'])]}
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
        from test_walkthrough_contract_repairs import WalkthroughRepairs
        for mutation in (None, 'foreign', 'withdrawn'):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as directory:
                state, runtime, assessment, kid, aid = WalkthroughRepairs().specialist_fixture()
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
        state, _, kid, aid = knowledge_fixtures.KnowledgeRedesign().verified()
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


class WakeRepairs(unittest.TestCase):
    def test_supervisor_requests_once_and_probe_reports_the_same_reason(self):
        from do_math import scheduled_operator as operator
        # Supervision judges from this one engine status; it loads no repository state.
        status = {'status': 'waiting', 'research_wake_reasons': [{'kind': 'research_reconsider_due'}],
                  'operator_enabled': True, 'provider_waits': {'providers': {}}}
        running = False
        def schedule(kind, **kwargs):
            nonlocal running
            if kind == 'start-engine':
                running = True
                return {'started': True}
            return {'engine': {'state': 'Running' if running else 'Ready'}}
        with tempfile.TemporaryDirectory() as directory, \
                patch.object(operator, 'read_status', return_value=status), \
                patch.object(operator, 'reconcile_wake', return_value={'status': 'not_needed'}), \
                patch.object(operator, 'schedule', side_effect=schedule) as start:
            root = Path(directory)
            observed = operator.check(root, 'RI-test', root, probe=True)
            self.assertEqual(observed['engine_start']['reason'], 'research reconsideration due')
            start.assert_not_called()
            self.assertEqual(operator.check(root, 'RI-test', root)['outcome'], 'engine_requested')
            self.assertEqual(operator.check(root, 'RI-test', root)['outcome'], 'engine_running')
            self.assertEqual(sum(call.args == ('start-engine',) for call in start.call_args_list), 1)

    def test_stopped_waiting_engine_wakes_on_due_research_without_mutating_state(self):
        from do_math import scheduled_operator
        instance = {'lifecycle': {'state': 'active'}, 'goal_status': 'unresolved'}
        runtime = {'status': 'waiting', 'tasks': {}, 'executions': {},
            'queue': [{'role': 'research_preparation'}], 'next_research_reconsider_at': AT}
        before = deepcopy(runtime)
        self.assertEqual(planning.research_wake_reasons(instance, runtime, now='2026-09-21T00:00:00Z'), [])
        reasons = planning.research_wake_reasons(instance, runtime, now=AT)
        self.assertEqual(reasons[0]['kind'], 'research_reconsider_due')
        self.assertEqual(runtime, before)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            status = {'status': 'waiting', 'research_wake_reasons': reasons}
            with patch.object(scheduled_operator, 'read_status', return_value=status):
                self.assertEqual(scheduled_operator.engine_start_guard(root, 'RI-test', root)['outcome'], 'startable')
                status['user_pause'] = {'reason': 'user'}
                self.assertEqual(scheduled_operator.engine_start_guard(root, 'RI-test', root)['outcome'], 'paused')
                scheduled_operator.hold(root, reason='test')
                self.assertEqual(scheduled_operator.engine_start_guard(root, 'RI-test', root)['outcome'], 'held')

    def test_regeneration_and_task_timers_are_read_only_and_not_duplicated(self):
        instance = {'lifecycle': {'state': 'active'}, 'goal_status': 'unresolved'}
        runtime = {'status': 'waiting', 'tasks': {'TK-wait': {'id': 'TK-wait', 'wake_at': AT}},
                   'queue': [{'role': 'research_work'}], 'executions': {}}
        due = planning.collect_due_events(instance, runtime, AT)
        self.assertEqual(planning.research_wake_reasons(instance, runtime, now=AT)[0]['kind'], 'task_wake_due')
        runtime['events'] = due
        self.assertEqual(planning.research_wake_reasons(instance, runtime, now=AT), [])
        runtime.update(tasks={}, queue=[], history=[{'kind': 'task_repetition', 'lineage': 'exhaustion_empty',
            'lineage_id': 'empty', 'outcome': 'empty', 'regenerate_after': AT}])
        with patch('do_math.revisions.repetition_hold', return_value=False):
            self.assertEqual(planning.research_wake_reasons(instance, runtime, now='2026-09-21T00:00:00Z'), [])
            self.assertEqual(planning.research_wake_reasons(instance, runtime, now=AT), [{'kind': 'research_regeneration_due'}])
        instance['id'] = 'RI-wait'
        runtime['question_links'] = [{'id': 'QU-user', 'status': 'open', 'owner': 'user',
                                     'blocks': True, 'target_ids': ['RI-wait'], 'unresolved_target_ids': ['RI-wait']}]
        with patch('do_math.revisions.repetition_hold', return_value=False):
            self.assertEqual(planning.research_wake_reasons(instance, runtime, now=AT), [])


class RecoveryBoundaryRepairs(unittest.TestCase):
    def test_restart_finishes_an_accepted_retry_after_target_termination_once(self):
        from test_repair_execution import RepairExecutionTests
        fixture = RepairExecutionTests('test_installation_repair_handoff_preserves_failure_and_is_idempotent')
        fixture.setUp(); self.addCleanup(fixture.doCleanups)
        host = fixture.host
        target = host.runtime['executions']['EX-target']
        target.pop('input_bundle')
        target['pending_operational_disposition'] = 'OD-repair'
        record = host.runtime['operational_dispositions']['OD-repair']
        record.update(status='awaiting_termination', disposition={'kind': 'retry', 'reason': 'Restart after ended target',
            'scope': 'Same unfinished activity', 'replay_safety': 'No external effects',
            'basis_refs': ['EX-target'], 'next_owner': 'engine'})
        host.runtime['status'] = 'paused'
        host._save()  # Reloaded state models interruption after the target ended.
        host._complete_operational_disposition = lambda row: ResearchEngine._complete_operational_disposition(host, row)
        ResearchEngine._run_pending_operational_repairs(host)
        self.assertEqual(host.runtime['queue'], [])
        host.runtime['status'] = 'ready'; host._save()
        ResearchEngine._run_pending_operational_repairs(host)
        ResearchEngine._run_pending_operational_repairs(host)
        _, _, saved = host.store.load()
        self.assertEqual(len(saved['queue']), 1)
        self.assertEqual(saved['operational_dispositions']['OD-repair']['status'], 'applied')
        self.assertNotIn('pending_operational_disposition', saved['executions']['EX-target'])

    def test_initial_diagnosis_receives_the_original_role_contract_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            engine, action, wait = initial_failure_engine(root)
            adopted, _ = surface_state()
            engine.instance.update({key: adopted[key] for key in ('governance', 'governance_sources')})
            engine.runtime['executions']['EX-bad']['input_bundle'] = 'BA-original'
            prefix = 'runtime/artifacts/BA-original'
            originals = {prefix + '/input.txt': b'Original role contract and fixed prompt',
                prefix + '/schema.json': b'{"type":"object"}',
                prefix + '/input/submission/context.json': b'{"fixed":"original input"}'}
            # The role input manifest names the archived prompt.
            prompt = originals[prefix + '/input.txt']
            engine.runtime['executions']['EX-bad']['input_manifest'] = {'prompt': {
                'artifact_ref': prefix + '/input.txt', 'sha256': hashlib.sha256(prompt).hexdigest(), 'bytes': len(prompt)}}
            engine.store.read.side_effect = lambda ref, head: originals[ref]
            engine.store.read_many.side_effect = lambda refs, head: {ref: originals[ref] for ref in refs}
            engine._documents = {'maintenance': contracts.prompt_documents('maintenance')}
            engine._preparation_checkpoint = create_autospec(engine._preparation_checkpoint, side_effect=lambda: None)
            engine._session_slots = create_autospec(engine._session_slots)
            engine._academic_status = create_autospec(engine._academic_status, side_effect=lambda: {})
            workspace = root / 'diagnosis'
            context = engine._context({'id': 'AC-diagnosis', 'role': 'maintenance', 'target': 'EX-bad',
                                       'initial_submission_diagnosis': True}, workspace)
            materials = context['initial_submission_diagnosis']['materials']
            self.assertEqual({row['artifact_ref'] for row in materials}, set(originals))
            for row in materials:
                raw = (workspace / row['local_path']).read_bytes()
                self.assertEqual(raw, originals[row['artifact_ref']])
                self.assertEqual(hashlib.sha256(raw).hexdigest(), row['sha256'])

    def test_retry_queue_and_disposition_publish_together_and_replay_is_noop(self):
        from test_repair_execution import RepairExecutionTests
        fixture = RepairExecutionTests('test_installation_repair_handoff_preserves_failure_and_is_idempotent')
        fixture.setUp(); self.addCleanup(fixture.doCleanups)
        host = fixture.host
        target = host.runtime['executions']['EX-target']
        target.pop('input_bundle')  # This case isolates queue/CAS publication.
        record = host.runtime['operational_dispositions']['OD-repair']
        record.update(status='pending', disposition={'kind': 'retry', 'reason': 'Use fresh input',
            'scope': 'Same unfinished activity', 'replay_safety': 'No external effects',
            'basis_refs': ['EX-target'], 'next_owner': 'engine'})
        host._save()
        before = host.head
        record = host.runtime['operational_dispositions']['OD-repair']
        ResearchEngine._complete_operational_disposition(host, record)
        self.assertEqual(host.store.load()[2]['queue'], [])
        host._save()
        after, _, saved = host.store.load()
        self.assertNotEqual(after, before)
        self.assertEqual(saved['operational_dispositions']['OD-repair']['status'], 'applied')
        self.assertEqual(saved['operational_dispositions']['OD-repair']['result']['continuation_action_id'], saved['queue'][0]['id'])
        ResearchEngine._complete_operational_disposition(host, host.runtime['operational_dispositions']['OD-repair'])
        self.assertEqual(len(host.runtime['queue']), 1)
        self.assertEqual(fixture.destination.read_bytes(), b'damaged')

    def test_initial_failure_kinds_and_stages_reach_one_authorized_followup(self):
        for kind in ('output_validation', 'execution_failure', 'submission_failure'):
            for stage in ('interpret', 'check'):
                with self.subTest(kind=kind, stage=stage), tempfile.TemporaryDirectory() as directory:
                    engine, action, wait = initial_failure_engine(Path(directory), kind, stage)
                    original = deepcopy(engine.instance['lifecycle']['immutable_input'])
                    repair_execution.route_failed_action(engine, action, 'EX-bad', reason='Diagnose actual failure')
                    diagnostic = engine.runtime['queue'].pop()
                    self.assertEqual(diagnostic['role'], 'maintenance')
                    engine._action_lifecycle_gate(diagnostic)
                    engine.runtime['executions']['EX-diagnosis'] = {'id': 'EX-diagnosis', 'role': 'maintenance',
                        'status': 'running', 'action': diagnostic}
                    repair_execution.apply_initial_diagnosis(engine, diagnostic,
                        {'initial_submission_diagnosis': {'decision': 'retry', 'guidance': 'Use the preserved contract'}}, 'EX-diagnosis')
                    self.assertEqual(engine.runtime['queue'], [], 'candidate application cannot publish a native recovery')
                    engine._save = create_autospec(engine._save)
                    engine.runtime['executions']['EX-diagnosis'] = {'id': 'EX-diagnosis', 'role': 'maintenance',
                        'status': 'ended', 'outcome': 'output_accepted', 'action': diagnostic}
                    repair_execution.continue_initial_retries(engine)
                    self.assertTrue(engine.runtime['queue'], engine.runtime['waiting_actions'])
                    retry = engine.runtime['queue'].pop()
                    self.assertEqual(retry['stage'], stage)
                    self.assertEqual(retry['owner_activity_id'], 'AY-original')
                    self.assertEqual(retry['continuation_of'], 'EX-bad')
                    self.assertEqual(retry['diagnosis_attempt'], 1)
                    self.assertEqual(engine.instance['lifecycle']['immutable_input'], original)
                    if kind == 'output_validation':
                        self.assertEqual(retry['repair']['retry_bundle_ids'], ['IN-pending'])
                    repair_execution.route_submission_return(engine, retry,
                        {'retry_bundle_ids': [], 'bundles': [], 'issues': []}, 'EX-again', None)
                    self.assertEqual(engine.runtime['queue'], [])

    def test_failed_diagnosed_retry_is_recorded_once_and_remains_storable(self):
        from do_math.record_schemas import RUNTIME_FIELDS
        from jsonschema import Draft202012Validator
        with tempfile.TemporaryDirectory() as directory:
            engine, action, wait = initial_failure_engine(Path(directory))
            diagnostic = {'id': 'AC-diagnosis', 'role': 'maintenance', 'target': 'EX-bad', 'initial_submission_diagnosis': True}
            repair_execution.apply_initial_diagnosis(engine, diagnostic,
                {'initial_submission_diagnosis': {'decision': 'retry', 'guidance': 'Retry original input'}}, 'EX-diagnosis')
            engine.runtime['executions']['EX-diagnosis'] = {'id': 'EX-diagnosis', 'role': 'maintenance',
                'status': 'ended', 'outcome': 'output_accepted', 'action': diagnostic}
            engine.instance['grants']['GR-init']['status'] = 'revoked'
            engine._save = create_autospec(engine._save)
            repair_execution.continue_initial_retries(engine)
            repair_execution.continue_initial_retries(engine)
            self.assertIn('retry_error', wait['diagnosis'])
            self.assertEqual(engine.runtime['queue'], [])
            engine._save.assert_called_once()
            Draft202012Validator(RUNTIME_FIELDS['waiting_actions']).validate(engine.runtime['waiting_actions'])

    def test_initial_diagnosis_does_not_bypass_termination_source_or_authority(self):
        for changed in ('termination', 'source', 'grant'):
            with self.subTest(changed=changed), tempfile.TemporaryDirectory() as directory:
                engine, action, wait = initial_failure_engine(Path(directory))
                if changed == 'termination':
                    engine.runtime['executions']['EX-bad']['capacity']['local_termination'] = 'unknown'
                elif changed == 'source':
                    engine.runtime['inputs'][0]['text'] = 'changed'
                else:
                    engine.instance['grants']['GR-init']['status'] = 'revoked'
                with self.assertRaises(ValueError):
                    engine._continue_initial_execution(wait, request_id='EX-diagnosis',
                        diagnosis={'decision': 'retry', 'guidance': 'Retry'})
                self.assertEqual(engine.runtime['queue'], [])


    def test_retry_keeps_pending_bundles_and_never_restores_old_input(self):
        from do_math import activities, execution_lifecycle, execution_profiles
        engine = context_engine()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fitted, fixed = package(engine, root, 'research_work')
            artifacts = engine._input_artifacts('BA-plan', contracts.schema_for('research_work'), fitted, root)
            engine.store.read.side_effect = lambda path, head: artifacts[path]
            profile = next(p for p in engine.instance['execution_profiles'].values() if p['role'] == 'research_work')
            activities.open_activity(engine.runtime, activity_id='AY-work', activity_kind='research_work',
                                    owner_ref='engine', input_refs=[], opened_at=AT)
            target = execution_lifecycle.create_execution(execution_id='EX-work', owner_activity_id='AY-work',
                actor_kind='ai', input_manifest=fitted['manifest'], profile_ref=execution_profiles.profile_ref(profile), created_at=AT)
            target.update(role='research_work', input_bundle='BA-plan', action={'id': 'AC-work',
                'role': 'research_work', 'owner_activity_id': 'AY-work'})
            activities.assign_execution(engine.runtime, 'AY-work', target)
            execution_lifecycle.transition_execution(target, 'starting', at=AT)
            execution_lifecycle.transition_execution(target, 'stopping', at=AT, stop_phase='terminating')
            execution_lifecycle.transition_execution(target, 'ended', at=AT, outcome='execution_incomplete')
            activities.wait_for(engine.runtime, 'AY-work', reason='returned', condition={'action_ids': ['AC-work']},
                                next_owner='operations', at=AT)
            engine.runtime['waiting_actions']['AC-work'] = {'execution_id': 'EX-work',
                'action': {**target['action'], 'repair': {'execution_id': 'EX-work', 'retry_bundle_ids': ['IN-left'],
                    'previous_output': {}, 'bundle_results': [], 'issues': []}}}
            record = {'id': 'OD-retry', 'target_execution_id': 'EX-work', 'status': 'pending',
                'disposition': {'kind': 'retry', 'reason': 'Fresh input copy', 'scope': 'Remaining bundles',
                    'replay_safety': 'Applied bundles stay recorded', 'next_owner': 'engine', 'basis_refs': ['EX-work']}}
            engine.runtime['operational_dispositions'] = {record['id']: record}
            damaged = root / 'input/submission/context.json'; damaged.write_bytes(b'damaged')
            engine._complete_operational_disposition(record)
            engine._complete_operational_disposition(record)
            self.assertEqual(damaged.read_bytes(), b'damaged')
            self.assertEqual(len(engine.runtime['queue']), 1)
            retry = engine.runtime['queue'][0]
            self.assertEqual(retry['repair']['retry_bundle_ids'], ['IN-left'])
            self.assertEqual(record['result']['continuation_action_id'], retry['id'])
            self.assertNotIn('AC-work', engine.runtime['waiting_actions'])
            fresh = root / 'next'
            context = engine._context(retry, fresh, execution_id='EX-next')
            self.assertEqual(context['previous_execution']['id'], 'EX-work')
            self.assertTrue((fresh / 'input/implementation/SKILL.md').is_file())
            self.assertEqual(damaged.read_bytes(), b'damaged')


if __name__ == '__main__':
    unittest.main()
