"""Cross-boundary checks for the current initialization implementation."""
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math import payloads, maintenance_gate
from do_math.operation_trace import tracing, phase, phase_rows, progress
from do_math.repository import ResearchRepository, canonical_json, new_id
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
            identifier=new_id('RI')
            repo=ResearchRepository(root,identifier)
            repo.register_family('research','label',shape='metadata',schema={'type':'string'},identity=False)
            text='exact 원문\n'*20000
            head=repo.initialize({'feature_version':5,'title':text,'label':text},
                                 {'feature_version':5,'status':'initializing'})
            stored=json.loads(repo.read('research/_state/metadata.json',head))
            self.assertIsNone(stored['record']['title'])
            self.assertEqual(len({r['path'] for r in stored['payloads']}),1)
            _, instance, runtime=repo.load(head)
            self.assertEqual(instance['title'],text)
            # Decoding (a head this repository object did not publish) shares one value per payload.
            reader=ResearchRepository(root,identifier)
            reader.register_family('research','label',shape='metadata',schema={'type':'string'},identity=False)
            decoded=reader.load(head)[1]
            self.assertTrue(decoded['title'] is decoded['label'], 'decoded values should share immutable bytes')
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

    def test_sealed_response_waits_for_a_record_change_after_a_failed_identity_check(self):
        import setup_lean
        from test_submission_flow import CentralSubmissionHistoryTests
        from research_fixtures import fixture_setup_lean
        from do_math.trust_validation import require_active_environment
        fixture = CentralSubmissionHistoryTests()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        engine = fixture.engine
        raw = canonical_json(fixture.output)
        _, receipt = fixture.submit('CT-environment', raw)
        self.assertEqual(receipt['state'], 'accepted')
        sealed_ref = engine.runtime['executions']['EX-history']['submission_intent']['output_ref']
        environment = engine.instance['trust_environments'][engine.instance['active_trust_environment']]
        lake = Path(environment['toolchain']['executable']).with_name('lake.exe')
        original = lake.read_bytes()
        apply = engine._apply
        def gated_apply(*args, **kwargs):
            # Synthetic domain consumer; the publication gate and wait are the real ones.
            require_active_environment(engine.instance, engine.runtime, current_identity=True)
            return apply(*args, **kwargs)
        with patch.object(engine, '_apply', side_effect=gated_apply):
            lake.write_bytes(b'accidentally replaced launcher')
            engine._receive_submission(fixture.context['action'], {}, 'EX-history', fixture.context, fixture.schema,
                                       fixture.workspace, preserved=True)
            waiting = engine.runtime['waiting_actions'][fixture.context['action']['id']]
            self.assertEqual((waiting['kind'], waiting['next_owner']), ('submission_publication', 'engine'))
            self.assertEqual(waiting['detail']['environment_id'], environment['id'])
            lake.write_bytes(original)
            with patch.object(engine, '_receive_submission', side_effect=AssertionError('retried before a change')):
                engine._retry_submission_publications()
            # A user re-records after restoring the files; the record change releases the wait.
            record_path = Path(environment['toolchain_record']['path'])
            with fixture_setup_lean(environment['toolchain'], record_path.parent / 'smoke.lean'):
                setup_lean.rerecord(['unused'], record_path.parent, record_path.parent / 'evidence', None)
            engine._retry_submission_publications()
        self.assertNotIn(fixture.context['action']['id'], engine.runtime['waiting_actions'])
        self.assertEqual(engine.runtime['executions']['EX-history']['outcome'], 'output_accepted')
        self.assertEqual(engine.store.read(sealed_ref), raw)
        with patch('do_math.formal.toolchain_identity_errors', side_effect=AssertionError('status checked identity')), \
             patch('do_math.trust_inventory.observe_fingerprint', side_effect=AssertionError('status scanned files')):
            engine.status()
