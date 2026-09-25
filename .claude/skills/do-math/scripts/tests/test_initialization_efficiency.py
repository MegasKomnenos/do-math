"""Cross-boundary checks for the current initialization implementation."""
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time
from types import SimpleNamespace
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math import payloads, maintenance_gate
from do_math.environment_checks import EnvironmentChecks, ObservationPending
from do_math.parallel import ModelCalls
from do_math.operation_trace import tracing, phase, phase_rows, progress
from do_math.repository import ResearchRepository, canonical_json, new_id
from research_fixtures import trust_fixture
from do_math.initialization import digest
from test_categories import test_group


@test_group('unit')
class EfficiencyUnits(unittest.TestCase):
    def test_telemetry_failure_identifies_operation_without_leaking_exception_text(self):
        from do_math.operation_trace import OperationTrace
        with tempfile.TemporaryDirectory() as directory:
            sink=OperationTrace(directory)
            with patch('do_math.operation_trace.atomic_replace',side_effect=PermissionError(13,'private request value')):
                with self.assertWarns(RuntimeWarning):
                    sink.emit({'event':'started','span_id':'span','phase':'unit'})
            observed=progress(directory)['telemetry_errors'][0]
            self.assertEqual(observed['operation'],'replace_live')
            self.assertEqual(observed['errno'],13)
            self.assertNotIn('private request value',json.dumps(observed))
            self.assertTrue(sink.path.is_file())

    def test_large_control_is_archived_before_reference_catalog_construction(self):
        from test_lifecycle_engine import FakeEngine, AdapterDouble
        from do_math.context_store import prepare_role_input
        with tempfile.TemporaryDirectory() as directory, patch('do_math.initialization.adapter_for', return_value=AdapterDouble()):
            root = Path(directory)
            owner = FakeEngine(root); owner.activate()
            request = {'id':'UC-large','action':'trust','origin':'user','config':{
                'files':[{'path':str(root/f'module-{i}'), 'sha256':'a'*64} for i in range(1000)]}}
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

    def test_launcher_trace_correlation_is_separate_from_child_authority(self):
        from do_math.operation_trace import workspace_operation, child_environment
        with tempfile.TemporaryDirectory() as directory:
            @workspace_operation('launcher')
            def launcher(workspace):
                return child_environment()['DO_MATH_PARENT_OPERATION_ID']
            parent = launcher(directory)
            with patch.dict('os.environ', {'DO_MATH_PARENT_OPERATION_ID':parent}):
                with tracing(directory), phase('child'):
                    pass
            child = next(row for row in phase_rows(directory) if row['phase']=='child')
            self.assertEqual(child['parent_operation_id'], parent)

    def test_payloads_are_exact_shared_and_immutable(self):
        text = '원문 코드포인트\n' * 20000
        value = payloads.seal_large({'title':text, 'source':{'text':text}})
        envelope={'contract_id':'test','family':'test','record':value}
        encoded, blobs=payloads.encode(envelope)
        self.assertEqual(len(blobs), 1)
        self.assertLess(len(canonical_json(encoded)), 1500)
        def read(path): return blobs[path]
        read.decoded={}
        restored=payloads.decode(encoded, read)
        self.assertEqual(restored, value)
        self.assertTrue(restored['title'] is restored['source']['text'], 'one immutable value should be shared')
        bad = deepcopy(encoded)
        bad['payloads'][0]['sha256']='0'*64
        with self.assertRaises(ValueError): payloads.decode(bad, read)
        manifest=payloads.seal_large({'manifest':{'foundation_profile':{},'files':[{'path':'x'*100} for _ in range(1000)]}})
        with self.assertRaises(TypeError): manifest['manifest']['files'].append({})

    def test_quiescence_does_not_release_unknown_execution_or_user_pause(self):
        runtime={'executions':{'EX-one':{'id':'EX-one','status':'starting'}},
                 'reservations':{},'user_pause':{'request_id':'UC-user'},'status':'paused'}
        request={'action':'quiesce','id':'UC-maint','origin':'operator','text':'install','created_at':'2026-09-25T00:00:00Z'}
        self.assertTrue(maintenance_gate.apply_control(runtime,request))
        maintenance_gate.settle(runtime)
        self.assertEqual(runtime['maintenance_fence']['state'],'blocked')
        release={**request,'action':'release_quiesce','id':'UC-release','config':{'fence_id':'UC-maint'}}
        with self.assertRaises(ValueError): maintenance_gate.apply_control(runtime,release)
        runtime['executions']['EX-one']['status']='ended'
        maintenance_gate.settle(runtime)
        maintenance_gate.apply_control(runtime,release)
        self.assertEqual(runtime['user_pause'],{'request_id':'UC-user'})
        self.assertEqual(runtime['status'],'paused')

    def test_publication_observation_is_deferred_and_not_reused_after_an_attempt(self):
        with tempfile.TemporaryDirectory() as directory:
            env=trust_fixture(Path(directory),['lean'])
            env.update(id='TE-test',status='active',source_ref='test',manifest_sha256=digest(env['manifest']))
            saved={}
            calls=ModelCalls()
            engine=SimpleNamespace(instance={'trust_environments':{'TE-test':env},'active_trust_environment':'TE-test'},
                runtime={'status':'running','executions':{'EX-one':{}},'waiting_actions':{}},
                _calls=calls,_save=lambda files:saved.update(files),_environment_attempt='attempt-1')
            checks=EnvironmentChecks(engine)
            try:
                with self.assertRaises(ObservationPending): checks.observe(env,'EX-one')
                deadline=time.monotonic()+5
                while calls.futures and time.monotonic()<deadline:
                    calls.collect(); time.sleep(.001)
                self.assertFalse(calls.futures)
                self.assertEqual(checks.observe(env,'EX-one')['status'],'verified')
                self.assertEqual(len(saved),1)
                engine._environment_attempt='attempt-2'
                with self.assertRaises(ObservationPending): checks.observe(env,'EX-one')
                while calls.futures and time.monotonic()<deadline:
                    calls.collect(); time.sleep(.001)
                self.assertEqual(len(saved),2)
                # Even an unconsumed result belongs to the executor that observed it.
                calls.close()
                calls = engine._calls = ModelCalls()
                with self.assertRaises(ObservationPending): checks.observe(env,'EX-one')
                while calls.futures and time.monotonic()<deadline:
                    calls.collect(); time.sleep(.001)
                self.assertEqual(checks.observe(env,'EX-one')['status'],'verified')
                self.assertEqual(len(saved),3)
                engine._environment_attempt = 'attempt-3'
                with patch('do_math.environment_checks.verify_environment_files', return_value={'status':'cancelled','errors':['fixture pause']}):
                    with self.assertRaises(ObservationPending) as pending: checks.observe(env,'EX-one')
                    while calls.futures and time.monotonic()<deadline:
                        calls.collect(); time.sleep(.001)
                self.assertTrue(checks.ready(pending.exception.request_id))
                with self.assertRaises(ObservationPending): checks.observe(env,'EX-one')
                while calls.futures and time.monotonic()<deadline:
                    calls.collect(); time.sleep(.001)
                self.assertEqual(checks.observe(env,'EX-one')['status'],'verified')
                self.assertEqual(len(saved),5)
                from do_math.lifecycle_engine import LifecycleEngineMixin
                engine._environment_checks = checks
                engine._environment_operation = 'EX-one'
                engine._calls = None
                with patch('do_math.trust_validation.verify_environment_files', side_effect=AssertionError('control path blocked')):
                    with self.assertRaises(ObservationPending): LifecycleEngineMixin._observe_environment(engine,env)
                    engine._calls = calls
                    engine._environment_operation = 'preview'
                    with self.assertRaises(ObservationPending): LifecycleEngineMixin._observe_environment(engine,env)
                self.assertFalse(calls.futures)
            finally:
                calls.close()

    def test_phase_timings_preserve_overlap_and_incomplete_work(self):
        with tempfile.TemporaryDirectory() as directory:
            with tracing(directory):
                with phase('parent'):
                    with phase('child') as counters:
                        counters.update(completed_files=2,read_bytes=20)
                    live = progress(directory)['rows']
                    self.assertEqual([r['phase'] for r in live[0]['active_spans']], ['parent'])
            rows=phase_rows(directory)
            self.assertEqual(len(rows),2)
            child=next(r for r in rows if r['phase']=='child')
            parent=next(r for r in rows if r['phase']=='parent')
            self.assertEqual(child['parent_span_id'],parent['span_id'])
            self.assertEqual(child['read_bytes'],20)
            self.assertGreaterEqual(parent['elapsed_ns'],child['elapsed_ns'])
            self.assertEqual(progress(directory)['rows'],[])
            (Path(directory)/'interrupted.jsonl').write_bytes(b'{"event": "started"}\n\xff')
            self.assertEqual(len(phase_rows(directory)), 2)


@test_group('integration')
class PayloadStorageTests(unittest.TestCase):
    def test_large_payload_storage_and_cached_parent_remain_exact(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            subprocess.run(['git','init','-q',str(root)],check=True)
            repo=ResearchRepository(root,new_id('RI'))
            repo.register_family('research','label',shape='metadata',schema={'type':'string'},identity=False)
            text='exact 원문\n'*20000
            head=repo.initialize({'feature_version':5,'title':text,'label':text},
                                 {'feature_version':5,'status':'initializing'})
            stored=json.loads(repo.read('research/_state/metadata.json',head))
            self.assertIsNone(stored['record']['title'])
            self.assertEqual(len({r['path'] for r in stored['payloads']}),1)
            _, instance, runtime=repo.load(head)
            self.assertEqual(instance['title'],text)
            self.assertTrue(instance['title'] is instance['label'], 'decoded values should share immutable bytes')
            with patch.object(repo._store,'read_many',wraps=repo._store.read_many) as reads:
                new_head, new_i, new_r=repo.save_with_state(head,instance,{**runtime,'status':'ready'})
            self.assertEqual(len([c for c in reads.call_args_list if c.args[0]==head]),0)
            self.assertEqual(repo.load(new_head),(new_head,new_i,new_r))
            instance['title']='caller mutation'
            self.assertEqual(repo.load(head)[1]['title'],text)
            self.assertEqual(repo.read(stored['payloads'][0]['path'],head),repo.read(stored['payloads'][0]['path'],new_head))

    def test_parent_cache_is_invalidated_when_a_family_validator_changes(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            subprocess.run(['git','init','-q',str(root)],check=True)
            repo=ResearchRepository(root,new_id('RI'))
            repo.initialize({'feature_version':5,'title':'original'}, {'feature_version':5,'status':'initializing'})
            repo.load()
            def reject(_): raise ValueError('new owner constraint')
            repo.register_family('research','title',shape='metadata',identity=False,validator=reject)
            with self.assertRaisesRegex(ValueError,'new owner constraint'): repo.load()


@test_group('integration')
class DeferredPublicationTests(unittest.TestCase):
    def test_public_maintenance_fence_survives_restart_and_preserves_user_pause(self):
        from test_input_recovery import InputRecoveryPublicTests
        from do_math.engine import ResearchEngine
        from do_math.scheduled_operator import engine_start_guard
        fixture = InputRecoveryPublicTests()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        args = fixture.instance_args(fixture.identifier)
        request = fixture.cli('quiesce', *args, '--origin', 'operator', '--reason', 'fixture installation maintenance')
        engine = ResearchEngine(fixture.repo, fixture.identifier)
        fence = engine.runtime['maintenance_fence']
        self.assertEqual(fence['state'], 'quiescent')
        self.assertEqual(fence['request_id'], request['request_id'])
        self.assertNotEqual(engine_start_guard(fixture.repo, fixture.identifier,
            Path(engine.instance['workspace']), status=engine.status())['outcome'], 'startable')
        fixture.cli('pause', *args, '--origin', 'user', '--reason', 'separate user pause')
        fixture.cli('release-quiesce', *args, '--origin', 'operator', '--fence', fence['request_id'], '--reason', 'fixture complete')
        restored = ResearchEngine(fixture.repo, fixture.identifier)
        self.assertNotIn('maintenance_fence', restored.runtime)
        self.assertEqual(restored.runtime['status'], 'paused')
        self.assertEqual(restored.runtime['user_pause']['reason'], 'separate user pause')

    def test_sealed_response_survives_deferred_domain_observation_and_git_publication(self):
        from test_submission_flow import CentralSubmissionHistoryTests
        fixture = CentralSubmissionHistoryTests()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        engine = fixture.engine
        raw = canonical_json(fixture.output)
        _, receipt = fixture.submit('CT-environment', raw)
        self.assertEqual(receipt['state'], 'accepted')
        execution = engine.runtime['executions']['EX-history']
        sealed_ref = execution['submission_intent']['output_ref']
        apply = engine._apply
        def observed_apply(*args, **kwargs):
            # Synthetic domain consumer, real observation/defer/receiver/Git path.
            engine._observe_environment(engine.instance['trust_environments'][engine.instance['active_trust_environment']])
            return apply(*args, **kwargs)
        calls = ModelCalls(on_returned=engine._local_call_returned)
        try:
            with patch.object(engine, '_apply', side_effect=observed_apply):
                first = engine._apply_submission_bundles(fixture.context['action'], fixture.output, {},
                    'EX-history', fixture.context, [])
                self.assertEqual(first['status'], 'partial')
                self.assertEqual(first['bundles'][0]['status'], 'returned')
                self.assertTrue(first['bundles'][0]['environment_request'])
                self.assertEqual(first['bundles'][0]['next_owner'], 'engine')
                self.assertFalse(calls.futures, 'a control-only owner must defer without scanning')
                engine._calls = calls
                pending = engine._apply_submission_bundles(fixture.context['action'], fixture.output, {},
                    'EX-history', fixture.context, [])
                self.assertEqual(pending['status'], 'partial')
                deadline = time.monotonic() + 10
                while calls.futures and time.monotonic() < deadline:
                    calls.collect(); time.sleep(.001)
                self.assertFalse(calls.futures)
                accepted = engine._apply_submission_bundles(fixture.context['action'], fixture.output, {},
                    'EX-history', fixture.context, [])
                self.assertEqual(accepted['status'], 'accepted', accepted)
            _, _, saved = ResearchRepository(fixture.repo, fixture.identifier).load()
            evidence = saved['executions']['EX-history']['environment_observations']
            self.assertEqual(len(evidence), 1)
            self.assertEqual(engine.store.read(sealed_ref), raw)
            observation = json.loads(engine.store.read(evidence[0]['artifact_ref']))
            self.assertEqual(observation['observation']['status'], 'verified')
            with patch('do_math.trust_validation._observe_file', side_effect=AssertionError('status read a trust file')):
                engine.status()
        finally:
            calls.close()
            engine._calls = None
