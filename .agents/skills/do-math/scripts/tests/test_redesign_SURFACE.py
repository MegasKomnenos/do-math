from __future__ import annotations

import json
import hashlib
import os
from copy import deepcopy
from unittest.mock import patch
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))

from do_math.context_store import build_role_manifest, fit_context, prepare_role_input, validate_role_manifest, defer_input_overflow
from do_math.reporting import render_human_report, snapshot_report
from do_math.repository import new_id
from do_math.engine import _repository as ResearchRepository
from do_math.retention import cleanup, cleanup_candidates
from do_math.state_checks import inspect_state


def surface_state():
    from do_math import governance, execution_profiles, activities, execution_lifecycle
    from do_math.engine import DEFAULT_CONFIG
    record = {'id': 'CH-1', 'kind': 'charter', 'revision': 1, 'supersedes': [],
        'content': {'rationale': 'Research P', 'goal': 'Prove P', 'desired_result': 'A proof',
            'success_criteria': ['P proved'], 'partial_success_criteria': ['Cases settled'],
            'included_scope': ['P'], 'excluded_scope': [], 'priorities': ['P'], 'preferences': [],
            'evidence_boundary': 'Proof', 'academic_requirements': [], 'decision_authority': 'user', 'stop_conditions': []}}
    source = governance.preserve_source('GS-1', 'User approves P', origin='user', revision=1)
    approval = {'id': 'DC-1', 'actor': 'user', 'source_ref': source['id'], 'source_sha256': source['sha256'],
                'record_hashes': {record['id']: governance.digest(record)}}
    instance = governance.initialize_governance({'id': 'IN-1', 'feature_version': 5}, source, approval, [record])
    instance.update(config=deepcopy(DEFAULT_CONFIG), knowledge={}, formal_results={}, expositions={},
                    identity_assessments={}, assessment_uses={}, sources=[], trust_environments={})
    instance.update(execution_profiles.build_profiles(instance['config']))
    runtime = {'feature_version': 5, 'status': 'active', 'tasks': {}, 'activities': {}, 'executions': {},
               'queue': [], 'history': [], 'question_links': [], 'reservations': {}, 'waiting_actions': {}}
    activities.open_activity(runtime, activity_id='AC-1', activity_kind='research', owner_ref='IN-1',
                             input_refs=[], opened_at='2026-09-20T00:00:00Z')
    profile = next(p for p in instance['execution_profiles'].values() if p['role'] == 'research_work')
    execution = execution_lifecycle.create_execution(execution_id='EX-1', owner_activity_id='AC-1', actor_kind='ai',
        input_manifest=[], profile_ref=execution_profiles.profile_ref(profile), created_at='2026-09-20T00:00:00Z')
    execution['role'] = 'research_work'
    activities.assign_execution(runtime, 'AC-1', execution)
    return instance, runtime


def archived_run(root):
    run = root / 'runs/EX-1'
    run.mkdir(parents=True)
    (run / 'output.txt').write_bytes(b'preserved result')
    receipt = json.dumps({'execution_id': 'EX-1', 'local_terminated': True}).encode()
    snapshot = 'a' * 40
    archive = {'runtime/artifacts/EX-1/output.txt': b'preserved result',
               'runtime/artifacts/EX-1/termination.json': receipt}
    execution = {'id': 'EX-1', 'status': 'ended', 'termination': {
        'local_terminated': True, 'evidence_ref': 'runtime/artifacts/EX-1/termination.json',
        'snapshot': snapshot, 'sha256': hashlib.sha256(receipt).hexdigest(), 'bytes': len(receipt)},
        'collection': {'retention_manifest': [{'path': 'output.txt', 'artifact_ref': 'runtime/artifacts/EX-1/output.txt',
            'snapshot': snapshot, 'sha256': hashlib.sha256(b'preserved result').hexdigest(), 'bytes': 16}]}}
    state = {'executions': {'EX-1': execution}, 'protected_references': set(),
             'approved_execution_ids': {'EX-1'}, 'runtime': {}}
    def read(path, commit):
        if commit != snapshot:
            raise ValueError('not an archived snapshot')
        return archive[path]
    return run, state, archive, read


class SurfaceRedesignTests(unittest.TestCase):
    def test_cleanup_uses_current_recovery_completion_and_obligations(self):
        from do_math.record_schemas import RECORDS
        from jsonschema import Draft202012Validator
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _, state, _, reader = archived_run(root)
            recovery = {'id': 'RY-1', 'started_at': '2026-09-25T00:00:00Z',
                        'execution_ids': ['EX-1'], 'dispositions': []}
            state['runtime']['recoveries'] = {'RY-1': recovery}
            Draft202012Validator(RECORDS['recoveries']).validate(recovery)
            pending = cleanup_candidates(root, **state, read_artifact=reader)[0]
            self.assertIn('recovery_pending', pending['reasons'])
            recovery['finished_at'] = '2026-09-25T00:01:00Z'
            Draft202012Validator(RECORDS['recoveries']).validate(recovery)
            self.assertTrue(cleanup_candidates(root, **state, read_artifact=reader)[0]['eligible'])
            state['runtime']['waiting_actions'] = {'AC-1': {'execution_id': 'EX-1'}}
            waiting = cleanup_candidates(root, **state, read_artifact=reader)[0]
            self.assertIn('recovery_pending', waiting['reasons'])
            state['runtime']['waiting_actions'] = {}
            state['runtime']['reservations'] = {'RS-1': {'owner_id': 'EX-1', 'state': 'held'}}
            reserved = cleanup_candidates(root, **state, read_artifact=reader)[0]
            self.assertIn('unsettled_reservation', reserved['reasons'])
            self.assertFalse(reserved['eligible'])
    def test_checker_sees_canonical_catalog_beyond_direct_comparison(self):
        from test_redesign_TASKS import task, disposition
        from research_fixtures import assessment, candidate
        from test_contract_checks import checks
        from do_math.submission import contract_check_errors
        from do_math.planning import validate_plan_submission
        instance, runtime = surface_state()
        runtime['tasks'] = {identifier: {**task(), 'id': identifier, 'status': status, 'results': []}
            for identifier, status in [('TK-ready', 'planned'), ('TK-completed', 'completed'), ('TK-waiting', 'waiting')]}
        runtime['tasks']['TK-completed']['results'] = [{'execution_id': 'EX-old', 'report': 'preserved'}]
        readers = deepcopy(list(runtime['tasks'].values()))
        readers[1]['results'][0]['local_path'] = 'restored/output.txt'
        returned = {**task(), 'id': 'TK-returned', 'status': 'waiting',
                    'results': [{'execution_id': 'EX-returned', 'report': 'A returned proof sketch'}]}
        for obligation in returned['completion_obligations']:
            obligation['evidence_required'] = ['EX-returned']
        runtime['tasks']['TK-returned'] = returned
        readers.append(deepcopy(returned))
        for role in ('research_plan', 'research_preparation'):
            with self.subTest(role=role), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                profile = next(p for p in instance['execution_profiles'].values() if p['role'] == role)
                fitted = prepare_role_input({'instance_id': instance['id'], 'action': {'id': 'A', 'role': role},
                    'tasks': readers, 'resources': {}, 'knowledge_catalog': [], 'ready_task_ids': ['TK-ready'],
                    'ongoing_preparation': [], 'blocked_actions': []},
                    instance=instance, runtime=runtime, role=role, profile=profile,
                    snapshot='a'*40, workspace=root, activity_id='AC-1', install_submission_tools=True)
                context = json.loads((root/'input/submission/context.json').read_bytes())
                tasks = {t['id']: t for t in context['tasks']}
                self.assertEqual(tasks, runtime['tasks'])
                self.assertNotIn('TK-completed', [t['id'] for t in fitted['context']['tasks']])
                plan = {'dispositions': [disposition('TK-ready')], 'task_assessments': [assessment(returned)]}
                validate_plan_submission(plan, tasks, ['TK-ready'])
                with self.assertRaises(ValueError):
                    validate_plan_submission({**plan, 'task_assessments': []}, tasks, ['TK-ready'])
                proposal = candidate('new')
                entry = checks('new', sibling_boundaries=[{'task_id': 'TK-completed', 'revision': 1,
                    'boundary': 'Use the completed sibling boundary', 'independent_of_next_revision': True}])
                self.assertEqual(contract_check_errors(proposal, entry, [], tasks, set(), set()), [])
                entry['sibling_boundaries'][0]['revision'] = 2
                self.assertTrue(contract_check_errors(proposal, entry, [], tasks, set(), set()))
                for extra in ('TK-completed', 'TK-waiting'):
                    invalid = deepcopy(plan)
                    invalid['dispositions'][0]['parallel_task_ids'] = [extra]
                    with self.assertRaises(ValueError):
                        validate_plan_submission(invalid, tasks, ['TK-ready'])

    def test_plan_receives_returned_work_separately_from_ready_selection_population(self):
        instance, runtime = surface_state()
        runtime['tasks'] = {'TK-returned': {'id': 'TK-returned', 'status': 'waiting',
            'question': 'Assess the actual result',
            'results': [{'execution_id': 'EX-1', 'report': 'An actual supplied result'}]}}
        profile = next(p for p in instance['execution_profiles'].values() if p['role'] == 'research_plan')
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fitted = prepare_role_input({'instance_id': instance['id'], 'action': {'id': 'A', 'role': 'research_plan'},
                'tasks': deepcopy(list(runtime['tasks'].values())),
                'resources': {}, 'knowledge_catalog': [], 'ready_task_ids': [], 'ongoing_preparation': []}, instance=instance, runtime=runtime, role='research_plan', profile=profile,
                snapshot='a'*40, workspace=root, activity_id='AC-1', install_submission_tools=True)
            direct = fitted['context']
            self.assertEqual(direct['ready_task_ids'], [])
            self.assertEqual(direct['returned_task_ids'], ['TK-returned'])
            self.assertEqual(direct['candidate_order']['ids'], [])
            self.assertEqual([t['id'] for t in direct['tasks']], ['TK-returned'])
            self.assertEqual(direct['tasks'][0]['result_count'], 1)
            validation = json.loads((root/'input/submission/context.json').read_bytes())
            self.assertEqual(validation['tasks'][0]['results'], runtime['tasks']['TK-returned']['results'])

    def test_audit2_impact_review_evidence_is_required_direct_input(self):
        from do_math.execution_profiles import build_profiles
        instance,runtime=surface_state()
        instance['config']['max_input_bytes']=16000
        instance.update(build_profiles(instance['config']))
        profile=next(p for p in instance['execution_profiles'].values() if p['role']=='maintenance')
        action={'id':'AC-impact','role':'maintenance','stage':'impact_review',
                'input_basis':{'impact_review':{'producer_execution_id':'EX-producer','plans':{}}}}
        evidence={'request':action['input_basis']['impact_review'],
                  'output':{'explanation':'original evidence '*6000},'extensions':{},'records':{}}
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            fitted=prepare_role_input({'action':action,'impact_review_input':evidence},instance=instance,
                runtime=runtime,role='maintenance',profile=profile,snapshot='a'*40,workspace=root/'oversize',
                activity_id='AC-impact')
            self.assertIn('impact_review_input',fitted['manifest']['required_direct_keys'])
            self.assertEqual(fitted['context']['impact_review_input'],evidence)
            self.assertIsNotNone(fitted['overflow'])
            self.assertIn('impact_review_input',fitted['overflow']['required_direct_keys'])
            with self.assertRaisesRegex(ValueError,'impact_review_input'):
                prepare_role_input({'action':action},instance=instance,runtime=runtime,role='maintenance',
                    profile=profile,snapshot='a'*40,workspace=root/'missing',activity_id='AC-impact')

    def test_audit_engine_cleanup_failure_reaches_snapshot_reporting(self):
        from do_math.engine import ResearchEngine
        from unittest.mock import Mock
        instance,runtime=surface_state()
        runtime['executions']['EX-1'].update(status='ended',outcome='execution_incomplete')
        from research_fixtures import dispatched_launch
        ex = runtime['executions']['EX-1']
        ex['launch_ticket'] = {**dispatched_launch(ex['id'], instance['execution_profiles'][ex['execution_profile_ref']['id']]), 'phase':'finished'}
        ex['capacity']={'local_termination':'confirmed'}
        with tempfile.TemporaryDirectory() as directory:
            instance['workspace']=directory
            (Path(directory)/'runs/EX-1').mkdir(parents=True)
            engine=object.__new__(ResearchEngine)
            engine.instance,engine.runtime,engine.head=instance,runtime,'a'*40
            engine.store=Mock()
            state={'executions':runtime['executions'],'runtime':runtime,'approved_execution_ids':['EX-1'],
                   'protected_references':[],'reference_records':{}}
            with patch.object(engine,'_cleanup_scope',return_value=['EX-1']), \
                 patch.object(engine,'_retention_state',return_value=state), \
                 patch.object(engine,'_save'), \
                 patch('do_math.retention._inventory',side_effect=PermissionError('cannot inspect files')):
                result=engine._maintenance_cleanup({},'EX-maint')
            self.assertEqual(result['status'],'degraded')
            self.assertEqual(runtime['history'][-1]['kind'],'maintenance_cleanup')
            engine.store.load.return_value=('a'*40,instance,runtime)
            with patch('do_math.reporting._repository',return_value=engine.store):
                report=snapshot_report(Path(directory),'IN-1',requested_areas=['record_storage'])
            self.assertTrue(any(row['status']=='degraded' and 'cannot inspect files' in row['message']
                                for row in report['inspection']['findings']))
            self.assertEqual(report['cleanup_failures'][0]['next_owner'],'maintenance')
            self.assertIn('degraded',render_human_report(report))
            self.assertTrue((Path(directory)/'runs/EX-1').exists())

    def test_audit_compaction_preserves_producer_validation_inputs(self):
        from do_math import submission
        instance,runtime=surface_state()
        runtime['tasks']={'TK-1':{'id':'TK-1','status':'planned','question':'P',
            'results':[{'execution_id':'EX-preserved','report':'Detailed result'}],
            'reviews':[{'execution_id':'EX-review','decision':'revise'}]}}
        profile=next(p for p in instance['execution_profiles'].values() if p['role']=='research_preparation')
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            fitted=prepare_role_input({'instance_id':instance['id'],'action':{'id':'A','role':'research_preparation'},
                'tasks':deepcopy(list(runtime['tasks'].values())),
                'resources':{},'knowledge_catalog':[],'blocked_actions':[]},instance=instance,runtime=runtime,role='research_preparation',profile=profile,
                snapshot='a'*40,workspace=root,activity_id='AC-1',install_submission_tools=True,max_artifact_bytes=100000)
            preview=json.loads((root/'input/submission/context.json').read_bytes())
            self.assertIn('EX-preserved',submission._reference_ids(preview))
            self.assertIn('EX-review',submission._reference_ids(preview))
            self.assertEqual(preview['tasks'][0]['results'],runtime['tasks']['TK-1']['results'])
            self.assertNotIn('results',fitted['context']['tasks'][0])

    def test_audit_engine_context_restores_multihop_git_artifact(self):
        from do_math.engine import initialize, ResearchEngine
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory); repository=root/'repo'; repository.mkdir()
            subprocess.run(['git','-C',str(repository),'init','-q'],check=True)
            created=initialize(repository,goal='Preserve resume evidence',workspace=root/'work',
                               config={'operator_enabled':False,'scholarly_enabled':False,})
            engine=ResearchEngine(repository,created['instance_id'])
            raw=b'ancestral evidence'; ref='runtime/artifacts/EX-a/lemma.txt'
            newer=b'latest lemma'; latest_ref='runtime/artifacts/EX-b/lemma.txt'
            keep_ref='runtime/artifacts/EX-a/keep.txt'
            artifacts={ref:raw, latest_ref:newer, keep_ref:b'keep ancestor file',
                'runtime/artifacts/EX-a/result.json':b'{"stage":"EX-a"}',
                'runtime/artifacts/EX-b/result.json':b'{"stage":"EX-b"}'}
            with engine.store.writer_lock():
                engine.head=engine.store.save_with_state(engine.head,engine.instance,engine.runtime,artifacts=artifacts)[0]
            def entry(path, artifact_ref):
                data=artifacts[artifact_ref]
                return {'path':path,'artifact_ref':artifact_ref,'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)}
            engine.runtime['executions'].update({
                'EX-a':{'id':'EX-a','status':'ended','role':'maintenance','owner_activity_id':'AT-resume','action':{'role':'maintenance'},
                    'result_ref':'runtime/artifacts/EX-a/result.json',
                    'output_files':[entry('lemma.txt',ref),entry('keep.txt',keep_ref)]},
                'EX-b':{'id':'EX-b','status':'ended','role':'maintenance','owner_activity_id':'AT-resume','continuation_of':'EX-a',
                    'result_ref':'runtime/artifacts/EX-b/result.json',
                    'action':{'role':'maintenance','continuation_of':'EX-a'},'output_files':[entry('lemma.txt',latest_ref)]}})
            engine.runtime['checkpoints']={identifier:{'partial':identifier} for identifier in ('EX-a','EX-b')}
            workspace=root/'resume'
            context=engine._context({'id':'AC-c','role':'maintenance','continuation_of':'EX-b'},workspace,execution_id='EX-c')
            self.assertEqual([row['path'] for row in context['previous_output_files']],['keep.txt','lemma.txt'])
            self.assertEqual((workspace/'input/previous-output/lemma.txt').read_bytes(),newer)
            self.assertEqual((workspace/'input/previous-output/keep.txt').read_bytes(),artifacts[keep_ref])
            self.assertEqual([row['execution_id'] for row in context['continuation_history']],['EX-a','EX-b'])
            for stage in context['continuation_history']:
                source=stage['result_source']
                self.assertEqual(source['snapshot'],engine.head)
                self.assertEqual((workspace/source['local_path']).read_bytes(),artifacts[source['artifact_ref']])
                self.assertEqual(stage['checkpoint'],engine.runtime['checkpoints'][stage['execution_id']])

    def test_audit_cleanup_aborted_attempt_is_not_healthy(self):
        instance, runtime = surface_state()
        runtime['history'] = [{'kind':'maintenance_cleanup_failed','execution_id':'EX-maint',
                              'paths':['runs/EX-1'],'completed_paths':[],
                              'reason':'root inaccessible','next_owner':'maintenance'}]
        result=inspect_state(instance,runtime,requested_areas=['record_storage'])
        self.assertEqual(result['status'],'degraded')

    def test_audit_cleanup_history_is_the_degraded_source(self):
        instance, runtime = surface_state()
        runtime['history'].append({'kind': 'maintenance_cleanup', 'execution_id': 'EX-maint',
            'result': {'status': 'degraded', 'deleted': [], 'failures': [
                {'path': 'runs/EX-1', 'error': 'locked', 'next_owner': 'maintenance'}]}})
        result = inspect_state(instance, runtime, requested_areas=['record_storage'])
        self.assertEqual(result['status'], 'degraded')
        self.assertTrue(any('runs/EX-1' in str(row) for row in result['findings']))
        runtime['history'].append({'kind': 'maintenance_cleanup', 'execution_id': 'EX-maint-2',
            'result': {'status': 'healthy', 'deleted': ['runs/EX-1'], 'failures': []}})
        self.assertEqual(inspect_state(instance, runtime, requested_areas=['record_storage'])['status'], 'healthy')

    def test_audit_candidate_population_is_compact_profile_bound_and_reproducible(self):
        from do_math.context_store import read_source
        instance, runtime = surface_state()
        runtime['tasks'] = {identifier: {'id': identifier, 'status': 'planned', 'question': identifier,
            'revision': 1, 'scope': {'included': ['P'], 'excluded': []},
            'large_detail': 'x' * 100000} for identifier in ['TK-z', 'TK-a', 'TK-m']}
        profile = next(p for p in instance['execution_profiles'].values() if p['role'] == 'research_preparation')
        context = {'action': {'id': 'AC-prep', 'role': 'research_preparation'}, 'resources': {},
                   'tasks': deepcopy(list(runtime['tasks'].values())),
                   'blocked_actions': [], 'pending_revisions': [], 'knowledge_catalog': []}
        with tempfile.TemporaryDirectory() as directory:
            fitted = prepare_role_input(context, instance=instance, runtime=runtime, role='research_preparation',
                profile=profile, snapshot='a'*40, workspace=Path(directory)/'first', activity_id='AC-prep')
            actual = fitted['context']
            from do_math.execution_profiles import boundary_prompt
            self.assertTrue(fitted['prompt'].endswith(boundary_prompt(profile)))
            self.assertNotIn('config', actual)
            self.assertIn('profile_selection', actual)
            self.assertEqual(actual['execution_profile'], profile)
            self.assertEqual({row['id'] for row in actual['tasks']}, set(runtime['tasks']))
            self.assertNotIn('large_detail', actual['tasks'][0])
            for row in actual['tasks']:
                restored = read_source(Path(directory)/'first', row['source_ref'], limit=200000)
                self.assertEqual(json.loads(restored['bytes']), runtime['tasks'][row['id']])
            order = fitted['manifest']['candidate_order']
            self.assertEqual(order['ids'], [row['id'] for row in actual['tasks']])
            replay = prepare_role_input(context, instance=instance, runtime=runtime, role='research_preparation',
                profile=profile, snapshot='a'*40, workspace=Path(directory)/'replay', activity_id='AC-prep',
                candidate_order=order)
            self.assertEqual(replay['manifest']['candidate_order'], order)
            self.assertEqual(replay['prompt'], fitted['prompt'])

    def test_audit_multihop_restores_latest_file_and_stage_evidence(self):
        from do_math import context_store
        with tempfile.TemporaryDirectory() as directory:
            archive = {}
            def entry(name, body, generation):
                path = 'runtime/artifacts/' + generation + '/' + name
                archive[path] = body
                return {'path': name, 'artifact_ref': path, 'sha256': hashlib.sha256(body).hexdigest(), 'bytes': len(body)}
            runtime = {'executions': {
                'EX-a': {'id':'EX-a','status':'ended','role':'maintenance','owner_activity_id':'AT-resume','action': {'role':'maintenance'},
                         'output_files':[entry('lemma.txt',b'old','A'),entry('keep.txt',b'keep','A')]},
                'EX-b': {'id':'EX-b','status':'ended','role':'maintenance','owner_activity_id':'AT-resume',
                         'action': {'role':'maintenance','continuation_of':'EX-a'},
                         'output_files':[entry('lemma.txt',b'new','B')]}}, 'checkpoints':{}}
            for identifier in ('EX-a','EX-b'):
                ref='runtime/artifacts/'+identifier+'/result.json'
                archive[ref]=json.dumps({'stage':identifier}).encode('utf-8')
                runtime['executions'][identifier]['result_ref']=ref
                runtime['checkpoints'][identifier]={'partial':'checkpoint '+identifier}
            result = context_store.restore_continuation(runtime, {'role':'maintenance','continuation_of':'EX-b'},
                Path(directory), snapshot='a'*40, read_artifact=lambda path: archive[path])
            self.assertEqual([row['execution_id'] for row in result['continuation_history']], ['EX-a','EX-b'])
            for stage in result['continuation_history']:
                ref=stage['result_source']
                self.assertEqual((Path(directory)/ref['local_path']).read_bytes(),archive[ref['artifact_ref']])
                self.assertEqual(ref['sha256'],hashlib.sha256(archive[ref['artifact_ref']]).hexdigest())
                self.assertEqual(stage['checkpoint'],runtime['checkpoints'][stage['execution_id']])
            self.assertEqual((Path(directory)/'input/previous-output/lemma.txt').read_bytes(),b'new')
            self.assertEqual((Path(directory)/'input/previous-output/keep.txt').read_bytes(),b'keep')
            runtime['executions']['EX-a']['owner_activity_id']='AT-other'
            with self.assertRaisesRegex(ValueError,'activity'):
                context_store.restore_continuation(runtime, {'role':'maintenance','continuation_of':'EX-b'},
                    Path(directory)/'other',snapshot='a'*40,read_artifact=lambda path:archive[path])
            runtime['executions']['EX-a']['owner_activity_id']='AT-resume'
            runtime['executions']['EX-a']['action']['continuation_of']='EX-b'
            with self.assertRaisesRegex(ValueError,'cycle'):
                context_store.restore_continuation(runtime, {'role':'maintenance','continuation_of':'EX-b'},
                    Path(directory)/'cycle',snapshot='a'*40,read_artifact=lambda path: archive[path])

    def test_retention_preserves_unpinned_receipt_and_unreadable_inventory(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            run, state, archive, read = archived_run(root)
            state['executions']['EX-1']['termination']['snapshot'] = 'HEAD'
            permissive_reader = lambda path, snapshot: archive[path]
            result = cleanup_candidates(root, read_artifact=permissive_reader, **state)
            self.assertFalse(result[0]['eligible'])
            state['executions']['EX-1']['termination']['snapshot'] = 'a' * 40
            def inaccessible(*args, **kwargs):
                if kwargs.get('onerror'):
                    kwargs['onerror'](PermissionError('cannot list execution directory'))
                return iter(())
            state['executions']['EX-1']['collection']['retention_manifest'] = []
            with patch('do_math.retention.os.walk', side_effect=inaccessible):
                result = cleanup_candidates(root, read_artifact=read, **state)
            self.assertFalse(result[0]['eligible'])
            self.assertTrue(run.exists())

    def test_cleanup_archive_failure_is_local_degradation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            run, state, archive, read = archived_run(root)
            candidates = cleanup_candidates(root, read_artifact=read, **state)
            original = deepcopy(state)
            def failed_reader(path, snapshot):
                raise RuntimeError('archive store unavailable')
            result = cleanup(root, candidates, current_state=lambda: state, read_artifact=failed_reader)
            self.assertEqual(result['status'], 'degraded')
            self.assertEqual(state, original)
            self.assertTrue(run.exists())

    def test_invalid_execution_and_activity_are_actually_inspected(self):
        result = inspect_state({'feature_version': 5}, {'feature_version': 5, 'executions': {'EX-1': {'id': 'EX-1', 'status': 'teleporting'}}, 'activities': {}}, requested_areas=['tasks_activities_executions'])
        self.assertTrue(any('status' in f['message'] for f in result['findings']))
        self.assertTrue(any('activity' in f['message'] for f in result['findings']))

    def test_area_errors_are_not_copied_to_unrelated_areas(self):
        result = inspect_state({'feature_version': 5, 'sources': [{'sha256': 'bad'}]}, {'feature_version': 5, 'activities': {}, 'executions': {}, 'tasks': {}}, requested_areas=['record_storage', 'tasks_activities_executions'])
        self.assertFalse(any(f['area'] == 'tasks_activities_executions' and 'sha256' in f['message'] for f in result['findings']))

    def test_descendant_reference_blocks_cleanup(self):
        with tempfile.TemporaryDirectory() as d:
            result = cleanup_candidates(Path(d), {'EX-1': {'id': 'EX-1', 'status': 'ended', 'artifact_bundle': 'bundle'}}, protected_references={'runs/EX-1/needed.txt'})
            self.assertFalse(result[0]['eligible'])
            self.assertIn('protected_reference', result[0]['reasons'])

    def test_bundle_name_alone_never_proves_preservation(self):
        with tempfile.TemporaryDirectory() as d:
            result = cleanup_candidates(Path(d), {'EX-1': {'id': 'EX-1', 'status': 'ended', 'artifact_bundle': 'bundle'}}, protected_references=set())
            self.assertFalse(result[0]['eligible'])

    def test_required_direct_action_is_never_replaced_by_reference(self):
        with tempfile.TemporaryDirectory() as d:
            action = {'id': 'A', 'reason': 'essential ' * 1000}
            result = fit_context({'action': action}, max_bytes=500, workspace=Path(d), mandatory_keys=['action'])
            self.assertEqual(result['context']['action'], action)
            self.assertIsNotNone(result['overflow'])
    def test_requested_check_areas_distinguish_unchecked_from_healthy(self):
        instance = {"feature_version": 5, "sources": [], "knowledge": {}, "trust_environments": {}}
        runtime = {"feature_version": 5, "tasks": {}, "executions": {}, "queue": [], "status": "ready", "question_links": []}
        report = inspect_state(instance, runtime, requested_areas=["record_storage"])
        self.assertEqual(report["status"], "healthy")
        self.assertEqual(report["not_checked"], [])
        self.assertEqual(report["areas"][0]["name"], "record_storage")
        unknown = inspect_state(instance, runtime, requested_areas=["not_an_area"])
        self.assertEqual(unknown["status"], "incomplete")
        self.assertEqual(unknown["not_checked"], ["not_an_area"])
        self.assertEqual(unknown["areas"], [{"name": "not_an_area", "status": "incomplete", "checked": False, "findings": 1}])
        self.assertEqual(unknown["findings"][0]["next_owner"], "operator")

    def test_json_and_human_status_share_one_snapshot(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(["git", "-C", str(root), "init", "-q"], check=True)
            identifier = new_id("RI")
            store = ResearchRepository(root, identifier)
            head = store.initialize({"id": identifier, "feature_version": 5, "sources": [], "knowledge": {}, "trust_environments": {}},
                                    {"feature_version": 5, "tasks": {}, "executions": {}, "queue": [], "status": "ready", "question_links": []})
            report = snapshot_report(root, identifier, snapshot=head,
                                     host_observation={"budget": {"work": {"used": 0}}, "observed_at": "2026-09-20T00:00:00Z"})
            self.assertEqual(report["snapshot"], head)
            self.assertEqual(report["host_observation"]["observed_at"], "2026-09-20T00:00:00Z")
            human = render_human_report(report)
            self.assertIn(head, human)
            self.assertIn("inspection:", human)

    def test_file_query_and_read_include_resolved_snapshot_provenance(self):
        # CLI imports ENGINE, so keep this boundary test independent of any
        # concurrent engine/observation implementation work.
        from do_math.cli import build_parser, execute
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(["git", "-C", str(root), "init", "-q"], check=True)
            identifier = new_id("RI")
            store = ResearchRepository(root, identifier)
            head = store.initialize({"id": identifier, "feature_version": 5, "sources": [], "knowledge": {}, "trust_environments": {}},
                                    {"feature_version": 5, "tasks": {}, "executions": {}, "queue": [], "status": "ready", "question_links": []})
            parser = build_parser()
            query, code = execute(parser.parse_args(["query", "--repository", str(root), "--instance", identifier,
                                                      "--files", "--prefix", "research/", "--limit", "1"]))
            self.assertEqual(code, 0)
            self.assertEqual(query["provenance"]["snapshot"], head)
            self.assertEqual(query["provenance"]["filters"]["prefix"], "research/")
            path = store.list_files("research/", head)[0]
            read, code = execute(parser.parse_args(["read", "--repository", str(root), "--instance", identifier,
                                                     "--path", path]))
            self.assertEqual(code, 0)
            self.assertEqual(read["snapshot"], head)
            self.assertEqual(len(read["sha256"]), 64)

    def test_required_input_overflow_is_structured_and_lossless(self):
        with tempfile.TemporaryDirectory() as directory:
            result = fit_context({"goal": "x" * 1000, "action": {"id": "A"}}, max_bytes=100,
                                 workspace=Path(directory), mandatory_keys=["goal", "action"],
                                 role="research_work", profile_id="P1", activity_id="ACT-1")
        overflow = result["overflow"]
        self.assertEqual(overflow["kind"], "input_overflow")
        self.assertEqual(overflow["role"], "research_work")
        self.assertEqual(overflow["activity_id"], "ACT-1")
        self.assertGreater(overflow["actual_bytes"], overflow["limit_bytes"])
        self.assertEqual(result["context"]["goal"], "x" * 1000)

    def test_role_manifest_distinguishes_required_direct_views_from_references(self):
        context = {"goal": "prove it", "policies": "no external effect", "tasks": [{"id": "T1", "status": "ready"}]}
        with tempfile.TemporaryDirectory() as directory:
            manifest = build_role_manifest(context, workspace=Path(directory), role="research_plan",
                                           direct_keys=["goal", "policies"], reference_keys=["tasks"])
        self.assertEqual([row["key"] for row in manifest["direct"]], ["goal", "policies"])
        self.assertEqual(manifest["references"][0]["key"], "tasks")
        self.assertEqual(manifest["references"][0]["source_ref"]["path"], "input/catalog/tasks.json")
        with self.assertRaises(ValueError):
            build_role_manifest(context, workspace=Path(directory), role="research_plan",
                                direct_keys=["missing"], reference_keys=[])

    def test_retention_requires_ended_closed_preserved_unrecovered_execution(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            run, state, archive, reader = archived_run(root)
            candidates = cleanup_candidates(root, **state, read_artifact=reader)
            self.assertEqual(candidates[0]["eligible"], True)
            result = cleanup(root, candidates, current_state=lambda: state, read_artifact=reader)
            self.assertEqual(result["deleted"], ["runs/EX-1"])
            self.assertFalse(run.exists())
            run.mkdir(parents=True)
            blocked = cleanup_candidates(root, {"EX-1": {"id": "EX-1", "status": "ended", "artifact_bundle": "runtime/artifacts/EX-1", "recovery_pending": True}}, protected_references=set())
            self.assertFalse(blocked[0]["eligible"])
            self.assertIn("recovery_pending", blocked[0]["reasons"])

    def test_cleanup_rechecks_reference_files_and_archive_before_deletion(self):
        for mutation in ('reference', 'local', 'archive', 'termination', 'reservation', 'recovery'):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as d:
                root = Path(d); run, state, archive, reader = archived_run(root)
                candidates = cleanup_candidates(root, **state, read_artifact=reader)
                self.assertTrue(candidates[0]['eligible'])
                if mutation == 'reference': state['protected_references'].add('runs/EX-1/output.txt')
                elif mutation == 'local': (run / 'new.txt').write_bytes(b'not archived')
                elif mutation == 'archive': archive['runtime/artifacts/EX-1/output.txt'] = b'corrupt'
                elif mutation == 'termination': archive['runtime/artifacts/EX-1/termination.json'] = b'{}'
                elif mutation == 'reservation': state['runtime']['reservations'] = {'RS': {'owner_id': 'EX-1', 'state': 'held'}}
                else: state['runtime']['recoveries'] = {'RY-1': {'id': 'RY-1',
                    'started_at': '2026-09-25T00:00:00Z', 'execution_ids': ['EX-1'], 'dispositions': []}}
                original = deepcopy(state)
                result = cleanup(root, candidates, current_state=lambda: state, read_artifact=reader)
                self.assertEqual(result['status'], 'degraded')
                self.assertTrue(run.exists())
                self.assertEqual(state, original)

    def test_retention_resolves_real_git_archive_bytes_at_pinned_commit(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            subprocess.run(['git', '-C', str(root), 'init', '-q'], check=True)
            identifier = new_id('RI'); repository = ResearchRepository(root, identifier)
            instance = {'id': identifier, 'feature_version': 5}
            runtime = {'feature_version': 5, 'executions': {}, 'activities': {}}
            head = repository.initialize(instance, runtime)
            run, state, archive, _ = archived_run(root / 'work')
            archived = repository.save_with_state(head, instance, runtime, artifacts=archive)[0]
            execution = state['executions']['EX-1']
            execution['termination']['snapshot'] = archived
            for row in execution['collection']['retention_manifest']: row['snapshot'] = archived
            reader = lambda path, snapshot: repository.read(path, snapshot)
            candidate = cleanup_candidates(root / 'work', **state, read_artifact=reader)
            self.assertTrue(candidate[0]['eligible'], candidate)
            result = cleanup(root / 'work', candidate, current_state=lambda: state, read_artifact=reader)
            self.assertEqual(result['deleted'], ['runs/EX-1'])
            self.assertEqual(repository.read('runtime/artifacts/EX-1/output.txt', archived), b'preserved result')

    def test_reparse_root_is_rejected_before_resolution(self):
        from do_math import retention
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); run, state, archive, reader = archived_run(root)
            real_stat = Path.lstat
            def lstat(path):
                if path == root / 'runs':
                    class Reparse:
                        st_mode = 0
                        st_file_attributes = 0x400
                    return Reparse()
                return real_stat(path)
            with patch.object(Path, 'lstat', lstat):
                candidates = retention.cleanup_candidates(root, **state, read_artifact=reader)
            self.assertFalse(candidates[0]['eligible'])
            self.assertTrue(any('reparse' in r for r in candidates[0]['reasons']))

    @unittest.skipUnless(os.name == 'nt', 'Windows junction probe')
    def test_real_windows_runs_junction_is_not_a_new_trusted_root(self):
        with tempfile.TemporaryDirectory() as d, tempfile.TemporaryDirectory() as outside:
            root = Path(d); target = Path(outside)
            (target / 'EX-1').mkdir(); (target / 'EX-1/important').write_bytes(b'keep')
            junction = root / 'runs'
            script = "New-Item -ItemType Junction -Path '" + str(junction).replace("'", "''") + "' -Target '" + str(target).replace("'", "''") + "' | Out-Null"
            made = subprocess.run(['powershell', '-NoProfile', '-NonInteractive', '-Command', script], capture_output=True)
            self.assertEqual(made.returncode, 0, made.stderr)
            try:
                result = cleanup_candidates(root, {'EX-1': {'id': 'EX-1', 'status': 'ended'}}, protected_references=set())
                self.assertFalse(result[0]['eligible'])
                self.assertTrue(any('reparse' in reason for reason in result[0]['reasons']))
                self.assertEqual((target / 'EX-1/important').read_bytes(), b'keep')
            finally:
                os.rmdir(junction)  # Only the exact temporary junction, not its target.
            run, state, archive, reader = archived_run(root)
            alias = root / 'protected-alias'
            script = "New-Item -ItemType Junction -Path '" + str(alias).replace("'", "''") + "' -Target '" + str(run).replace("'", "''") + "' | Out-Null"
            self.assertEqual(subprocess.run(['powershell', '-NoProfile', '-NonInteractive', '-Command', script], capture_output=True).returncode, 0)
            try:
                state['protected_references'] = {str(alias / 'output.txt')}
                result = cleanup_candidates(root, **state, read_artifact=reader)
                self.assertFalse(result[0]['eligible'])
                self.assertTrue(run.exists())
            finally:
                os.rmdir(alias)

    def test_role_input_uses_current_schema_documents_and_private_resume_bytes(self):
        from do_math import execution_profiles, contracts
        instance, runtime = surface_state()
        profile = next(p for p in instance['execution_profiles'].values() if p['role'] == 'research_work')
        context = {'action': {'role': 'research_work'}, 'task': {'id': 'TK-1'},
                   'previous_execution': {'id': 'EX-old', 'failure': 'must not disappear'},
                   'resume_checkpoint': {'remaining_work': 'P'}, 'recent_history': ['x' * 1000]}
        with tempfile.TemporaryDirectory() as d:
            result = prepare_role_input(context, instance=instance, runtime=runtime, role='research_work',
                profile=profile, snapshot='a' * 40, workspace=Path(d), activity_id='AC-1', artifact_prefix='runtime/artifacts/EX-1')
            self.assertEqual(result['context']['resume_checkpoint'], context['resume_checkpoint'])
            self.assertTrue(validate_role_manifest(result['manifest']))
            self.assertEqual(result['manifest']['prompt']['sha256'], hashlib.sha256(result['prompt'].encode()).hexdigest())
            self.assertEqual(result['manifest']['output_contract']['id'], contracts.schema_for('research_work')['x-contract-id'])
            self.assertIn('previous_execution', result['manifest']['required_direct_keys'])
            broken = deepcopy(result['manifest']); broken['direct'] = [r for r in broken['direct'] if r['key'] != 'resume_checkpoint']
            with self.assertRaises(ValueError): validate_role_manifest(broken)
            from do_math.context_store import verify_manifest_artifacts
            self.assertEqual(verify_manifest_artifacts(result['manifest'], result['artifacts'].__getitem__), [])
            result['artifacts'][result['manifest']['prompt']['artifact_ref']] = b'changed'
            with self.assertRaises(ValueError): verify_manifest_artifacts(result['manifest'], result['artifacts'].__getitem__)

    def test_preparation_compares_full_population_and_only_effective_k_summaries(self):
        from test_static_review_repairs import context_engine
        from do_math import knowledge_records
        from test_redesign_TASKS import task
        instance, runtime = surface_state()
        value = task(); runtime['tasks'][value['id']] = value
        waiting = deepcopy(value); waiting.update(id='TK-2', status='waiting'); runtime['tasks']['TK-2'] = waiting
        instance, kid = knowledge_records.create_candidate(instance, {'title': 'Candidate', 'kind': 'conjecture',
            'statement': 'P', 'explanation': 'Unproved', 'summary': 'Do not call this verified',
            'lean_code': '', 'declaration_names': [], 'dependencies': []}, source_ref='SRC', actor_ref='EX-1')
        profile = next(p for p in instance['execution_profiles'].values() if p['role'] == 'research_preparation')
        with tempfile.TemporaryDirectory() as d:
            context = context_engine(instance, runtime)._context({'role': 'research_preparation'}, Path(d))
            result = prepare_role_input(context,
                instance=instance, runtime=runtime, role='research_preparation', profile=profile,
                snapshot='a'*40, workspace=Path(d), activity_id='AC-1')
        self.assertEqual([r['id'] for r in result['context']['tasks']], [value['id']])
        self.assertEqual(result['context']['knowledge_catalog'][0]['id'], kid)
        self.assertFalse(result['context']['knowledge_catalog'][0]['usable_as_k'])
        self.assertEqual(result['context']['knowledge_catalog'][0]['verified_summaries'], [])
        self.assertIn('knowledge_catalog', result['manifest']['required_direct_keys'])
        runtime['queue'] = [{'id': 'A-revise', 'role': 'research_preparation', 'revision_targets': {'TK-2': 1}}]
        with tempfile.TemporaryDirectory() as d:
            context = context_engine(instance, runtime)._context({'role': 'research_preparation'}, Path(d))
            revised = prepare_role_input(context, instance=instance, runtime=runtime,
                role='research_preparation', profile=profile, snapshot='b'*40, workspace=Path(d), activity_id='AC-1')
        self.assertEqual({row['id'] for row in revised['context']['tasks']}, {value['id'], 'TK-2'})
        self.assertEqual([row['id'] for row in revised['context']['tasks']], revised['manifest']['candidate_order']['ids'])

    def test_verified_summary_tracks_identity_use_withdrawal(self):
        from test_static_review_repairs import context_engine
        from test_redesign_KNOWLEDGE import KnowledgeRedesign
        from do_math.knowledge_records import set_assessment_use
        instance, runtime = surface_state()
        evidence, _, kid, assessment = KnowledgeRedesign().verified()
        instance.update(evidence)  # Synthetic formal receipts; this tests propagation, not Lean.
        profile = next(p for p in instance['execution_profiles'].values() if p['role'] == 'research_preparation')
        def prepare():
            with tempfile.TemporaryDirectory() as d:
                context = context_engine(instance, runtime)._context({'role': 'research_preparation'}, Path(d))
                return prepare_role_input(context, instance=instance, runtime=runtime,
                    role='research_preparation', profile=profile, snapshot='a'*40, workspace=Path(d), activity_id='AC-1')
        row = prepare()['context']['knowledge_catalog'][0]
        self.assertTrue(row['usable_as_k'])
        self.assertEqual(row['verified_summaries'][0]['text'], 'Truth')
        self.assertEqual(row['verified_summaries'][0]['basis']['assessment_id'], assessment)
        instance = set_assessment_use(instance, assessment, 'withdrawn', 'fixture withdrawal', 'user')
        row = prepare()['context']['knowledge_catalog'][0]
        self.assertFalse(row['usable_as_k'])
        self.assertEqual(row['verified_summaries'], [])

    def test_reference_closure_follows_records_and_preserves_unknown_origins(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); run, state, archive, reader = archived_run(root)
            state['protected_references'] = {'KN'}
            records = {'KN': {'dependencies': ['CP']}, 'CP': {'path': 'runs/EX-1/output.txt', 'references': ['KN']}}
            result = cleanup_candidates(root, **state, read_artifact=reader, reference_records=records)
            self.assertIn('protected_reference', result[0]['reasons'])
            result = cleanup_candidates(root, **state, read_artifact=reader)
            self.assertIn('unresolved_reference: KN', result[0]['reasons'])

    def test_review_input_matches_real_seat_view_and_rejects_peer_injection(self):
        from do_math.review_cycle import start_review, next_actions, context_for
        instance, runtime = surface_state()
        cycle = start_review({'revision': 1, 'statement': 'P'}, reviewers=2)
        runtime['review_cycles'] = {'RC-1': cycle}
        action = next_actions(cycle)[0]
        context = {'action': {**action, 'id': 'A-review', 'role': 'identity_review', 'review_cycle_id': 'RC-1',
                              'grant_id': 'GR-current-execution'},
                   'role_review': context_for(cycle, action)}
        profile = next(p for p in instance['execution_profiles'].values() if p['role'] == 'identity_review')
        with tempfile.TemporaryDirectory() as d:
            result = prepare_role_input(context, instance=instance, runtime=runtime, role='identity_review',
                profile=profile, snapshot='a'*40, workspace=Path(d), activity_id='AC-1')
            self.assertEqual(result['manifest']['private_scope']['slot'], action['slot'])
        context['role_review']['peer_private'] = {'unsealed': 'do not expose'}
        with tempfile.TemporaryDirectory() as d, self.assertRaisesRegex(ValueError, 'seat-scoped'):
            prepare_role_input(context, instance=instance, runtime=runtime, role='identity_review',
                profile=profile, snapshot='a'*40, workspace=Path(d), activity_id='AC-1')

    def test_engine_review_context_reaches_role_input_with_bound_identity_and_policy(self):
        from test_review_engine import FakeEngine
        instance, _ = surface_state()
        with tempfile.TemporaryDirectory() as d:
            workspace = Path(d)
            engine = FakeEngine(workspace)
            engine.instance = {**instance, **engine.instance,
                'config': {**instance['config'], **engine.instance['config']}}
            engine.head = 'a' * 40
            engine._start_identity_review('K1')
            action = {**engine.pending(), 'grant_id': 'GR-current-execution'}
            review = engine._build_review_context(action, workspace)
            profile = next(p for p in engine.instance['execution_profiles'].values() if p['role'] == 'identity_review')
            context = {'action': action, 'role_review': review}
            def prepare():
                return prepare_role_input(context, instance=engine.instance, runtime=engine.runtime,
                    role='identity_review', profile=profile, snapshot=engine.head,
                    workspace=workspace, activity_id='AC-1')
            result = prepare()
            self.assertEqual(result['context']['role_review']['identity_basis'], review['identity_basis'])
            self.assertEqual(result['context']['role_review']['policy_ref'], review['policy_ref'])
            for field in ('identity_basis', 'policy_ref'):
                with self.subTest(field=field):
                    context['role_review'] = {**review, field: 'forged'}
                    with self.assertRaisesRegex(ValueError, 'authorized seat view'):
                        prepare()

    def test_submission_context_is_installed_before_single_input_seal(self):
        instance, runtime = surface_state()
        profile = next(p for p in instance['execution_profiles'].values() if p['role'] == 'research_work')
        context = {'instance_id': instance['id'], 'action': {'id': 'A-work', 'role': 'research_work'},
                   'task': {'id': 'TK-1'}, 'formal_verifier': {'reference': 'tool:lean'}}
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            result = prepare_role_input(context, instance=instance, runtime=runtime, role='research_work',
                profile=profile, snapshot='a'*40, workspace=root, activity_id='AC-1',
                install_submission_tools=True, max_artifact_bytes=100000,
                artifact_prefix='runtime/artifacts/EX-1')
            preview = json.loads((root / 'input/submission/context.json').read_bytes())
            self.assertEqual(preview['formal_verifier'], result['context']['formal_verifier'])
            self.assertEqual(preview['governance'], result['context']['governance'])
            self.assertIn('submission_contract', result['manifest']['required_direct_keys'])

    def test_role_overflow_keeps_original_sizes_and_waits_on_activity(self):
        from do_math import execution_profiles, execution_lifecycle
        instance, runtime = surface_state()
        profile = next(p for p in instance['execution_profiles'].values() if p['role'] == 'research_work')
        body = {k: deepcopy(v) for k, v in profile.items() if k not in {'id', 'sha256'}}
        body['input']['max_input_bytes'] = 200
        profile = execution_profiles.seal_profile(body)
        with tempfile.TemporaryDirectory() as d:
            result = prepare_role_input({'action': {}, 'task': {'id': 'TK', 'evidence': 'x'*3000}},
                instance=instance, runtime=runtime, role='research_work', profile=profile,
                snapshot='a'*40, workspace=Path(d), activity_id='AC-1')
        overflow = result['overflow']
        self.assertGreater(overflow['original_bytes'], 3000)
        self.assertIn('resolution_question', overflow)
        self.assertEqual(defer_input_overflow(runtime, overflow, at='2026-09-20T00:00:01Z', question_ref='Q-1')['status'], 'working')
        execution_lifecycle.transition_execution(runtime['executions']['EX-1'], 'ended',
            at='2026-09-20T00:00:02Z', outcome='cancelled', reason='input overflow', disposition='question')
        self.assertEqual(defer_input_overflow(runtime, overflow, at='2026-09-20T00:00:03Z', question_ref='Q-1')['status'], 'waiting')
        self.assertEqual(runtime['activities']['AC-1']['status'], 'waiting')


if __name__ == "__main__":
    unittest.main(verbosity=2)
