"""Feature-five lifecycle integration; CLI/Lean probes are explicit test doubles."""
import hashlib
import sys
import tempfile
import unittest
from copy import deepcopy
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import create_autospec, Mock, patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from do_math import execution_profiles as profiles
from do_math.configuration import DEFAULT_CONFIG
from do_math.engine import read_record, ResearchEngine
from do_math.initialization import initialize_state
from do_math.repository import ResearchRepository
from engine_fixtures import FakeEngine, initialized, initialized_instance, PublicInitializationRunner
from research_fixtures import FixtureAdapter, IDENTITY
from state_fixtures import owner_calls


def run_machine(engine,role):
    """Process one queued machine action and finish its calculation, as the owner loop does."""
    with owner_calls(engine):
        return engine.machine(role)


class PublicLifecycleTests(unittest.TestCase):
    def initializing(self):
        """A copy of one publicly initialized instance: ``(repository, instance ID)``."""
        from research_fixtures import restore_template
        root, instance_id = restore_template(initialized_instance, goal='Preserve this original input',
                                             config={'scholarly_enabled':False})
        return root/'repository', instance_id

    def test_public_utc_watermark_is_published_only_with_normal_change(self):
        root, instance_id = self.initializing()
        engine = ResearchEngine(root,instance_id)
        engine._save()  # Establish any ordinary derived runtime fields first.
        head = engine.head
        initial = datetime.fromisoformat(engine.runtime['last_observed_utc'])
        observed = initial + timedelta(hours=2)
        engine.lifecycle_clock = lambda: observed.isoformat()
        engine.lifecycle_monotonic = lambda: 0.
        engine._require_action_clock()
        engine._save()
        self.assertEqual(engine.head,head,'clock observation alone created a commit')
        engine.instance['title'] = 'Ordinary state update'
        engine._save()
        self.assertEqual(engine.runtime['last_observed_utc'],observed.isoformat())
        restarted = ResearchEngine(root,instance_id)
        restarted.lifecycle_clock = lambda: (observed-timedelta(microseconds=1)).isoformat()
        restarted.lifecycle_monotonic = lambda: 0.
        self.assertEqual(restarted._clock_guard()['reason'],'persisted_utc_regression')
        # A later rejected sample does not revoke the prior trusted sample.
        engine.lifecycle_clock = lambda: (observed+timedelta(hours=1)).isoformat()
        trusted = engine._require_action_clock()
        engine.lifecycle_clock = lambda: (observed+timedelta(minutes=30)).isoformat()
        self.assertFalse(engine._clock_guard()['usable'])
        engine._pause_lifecycle('clock_regression')
        engine._save()
        self.assertEqual(engine.store.load()[2]['last_observed_utc'],trusted)

    def test_public_unicode_original_survives_restart(self):
        from do_math.initialization import original_input_bytes
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); source = 'Cafe\u0301'
            instance_id = initialized(root,goal=source,config={'scholarly_enabled':False})
            restarted = ResearchEngine(root,instance_id)
            self.assertEqual(original_input_bytes(restarted.instance['lifecycle']['immutable_input']),source.encode())

    def test_public_initializing_pause_resume_preserves_source_and_missing(self):
        from research_fixtures import send_control
        root, instance_id = self.initializing()
        engine=ResearchEngine(root,instance_id)
        source=deepcopy(engine.runtime['inputs'])
        send_control(engine,'pause',config={})
        self.assertEqual(engine.runtime['resume_lifecycle'],'initializing')
        send_control(engine,'resume',config={})
        resumed=ResearchEngine(root,instance_id)
        self.assertEqual(resumed.instance['lifecycle']['state'],'initializing')
        self.assertEqual(resumed.runtime['inputs'],source)
        self.assertIn('independent_intent',resumed.instance['lifecycle']['activation']['missing'])
        self.assertNotIn('missing',resumed.runtime['availability'])
        send_control(resumed,'close',config={})
        self.assertTrue(resumed.instance['lifecycle']['permanently_closed'])
        from do_math.engine import control
        for action in ('pause','resume'):
            # After the resume, the same pause is a new request; a closed instance rejects both.
            request=control(root,instance_id,action,config={})
            resumed.process_controls()
            self.assertEqual(resumed.control_result(request['request_id'])['effect'],'rejected',action)
        terminal=ResearchEngine(root,instance_id)
        self.assertEqual(terminal.runtime['status'],'closed')
        self.assertTrue(terminal.instance['lifecycle']['permanently_closed'])

    def test_public_call_mode_init_activate_pause_resume_and_persistence(self):
        # The public initialization and activation through PublicInitializationRunner
        # are this test's subject, so it keeps the public path.
        from research_fixtures import activate, install_adapter_fixture, send_control
        install_adapter_fixture(self)
        with tempfile.TemporaryDirectory() as directory, patch('do_math.windows_job.named_job_empty',return_value=True):
            root = Path(directory)
            instance_id = initialized(root,goal='Prove n + 0 = n',config={
                'scholarly_enabled':False,
                'lean_command':['synthetic-lean'],})
            engine = ResearchEngine(root,instance_id,runner=PublicInitializationRunner())
            activate(engine,root,initialization_runner=engine.runner)
            self.assertEqual(engine.instance['lifecycle']['state'],'active')
            self.assertEqual(len(engine.runtime['intent_imports']),1)
            self.assertTrue(engine.instance['active_trust_environment'])
            queued=deepcopy(engine.runtime['queue'])
            attempts=set(engine.runtime['executions'])
            engine.run(until_active=True)
            self.assertEqual(set(engine.runtime['executions']),attempts)
            self.assertEqual(engine.runtime['queue'],queued)
            send_control(engine,'pause',config={})
            self.assertEqual(engine.runtime['resume_lifecycle'],'active')
            send_control(engine,'resume',config={})
            self.assertEqual(engine.instance['lifecycle']['state'],'active')
            resumed = ResearchEngine(root,instance_id)
            self.assertEqual(resumed.instance['lifecycle']['state'],'active')
            self.assertNotIn('task_readiness',resumed.runtime)
            self.assertNotIn('initial_request',resumed.instance['lifecycle'])

    def test_public_external_once_credential_resume_persists_attempts(self):
        # The subject is how public controls and Git reloads record the two
        # attempts, not activation: start from the validated active state.
        import os, threading
        from http.server import HTTPServer
        from research_fixtures import install_adapter_fixture, restore_template, send_control
        from state_fixtures import active_instance
        from provider_fixtures import HTTPFixtureHandler
        class Handler(HTTPFixtureHandler):
            count=0
            def do_POST(self):
                Handler.count+=1
                super().do_POST()
        install_adapter_fixture(self)
        server=HTTPServer(('127.0.0.1',0),Handler)
        threading.Thread(target=server.serve_forever,daemon=True).start()
        self.addCleanup(server.server_close); self.addCleanup(server.shutdown)
        origin=f'http://127.0.0.1:{server.server_port}'
        root, instance_id = restore_template(active_instance, config={'scholarly_enabled':False,
                                                                      'lean_command':['synthetic-lean']})
        repository = root/'repository'
        engine=ResearchEngine(repository,instance_id)
        send_control(engine,'decision',config={'change':{'kind':'grant','grant':{
            'id':'GR-public-http','kind':'http','reuse':'once','allowed_origins':[origin],
            'allowed_methods':['POST'],'allowed_path_prefixes':['/effect'],
            'credential_env':{'X-Test':'LIFECYCLE_AUDIT_TEST_TOKEN'}}}})
        config={'operation':'prepare','id':'OP-public','grant_id':'GR-public-http',
            'request':{'method':'POST','url':origin+'/effect','body':'synthetic local request'}}
        send_control(engine,'external',config=config)
        action=next(a for a in engine.runtime['queue'] if a['role']=='external_action')
        with patch.dict(os.environ):
            os.environ.pop('LIFECYCLE_AUDIT_TEST_TOKEN',None)
            engine._process_machine_action(action)
        before=deepcopy(engine.runtime['external_operations']['OP-public'])
        first=deepcopy(engine.runtime['executions'][before['execution_id']])
        self.assertEqual(first['status'],'ended'); self.assertEqual(Handler.count,0)
        resumed=ResearchEngine(repository,instance_id)
        send_control(resumed,'external',config=config,request_id='UC-public-external-credential-resume')
        action=next(a for a in resumed.runtime['queue'] if a['role']=='external_action')
        with patch.dict(os.environ,{'LIFECYCLE_AUDIT_TEST_TOKEN':'synthetic-local-token'}):
            resumed._process_machine_action(action)
        saved=ResearchEngine(repository,instance_id)
        op=saved.runtime['external_operations']['OP-public']
        current=saved.runtime['executions'][op['execution_id']]
        self.assertEqual(Handler.count,1); self.assertEqual(op['status'],'confirmed')
        self.assertNotIn('waiting_reason',op)
        for key in ('id','request_sha256','idempotency_key'):
            self.assertEqual(op[key],before[key])
        self.assertEqual(saved.runtime['executions'][first['id']],first)
        self.assertEqual(current['continuation_of'],first['id'])
        self.assertEqual(current['owner_activity_id'],first['owner_activity_id'])
        self.assertEqual(current['submission_receipt']['kind'],'machine_output')
        self.assertEqual(current['outcome'],'output_accepted')
        for execution in (first,current):
            times=[datetime.fromisoformat(row['at']) for row in execution['transitions']]
            self.assertEqual(times,sorted(times))


class LifecycleTests(unittest.TestCase):
    def setUp(self):
        temp=tempfile.TemporaryDirectory(); self.addCleanup(temp.cleanup)
        mock=patch('do_math.initialization.adapter_for',return_value=FixtureAdapter())
        mock.start(); self.addCleanup(mock.stop)
        self.engine=FakeEngine(temp.name); self.engine.activate()
    def test_controls_reach_active_and_separate_initial_authority(self):
        e=self.engine; self.assertEqual(e.instance['lifecycle']['state'],'active')
        self.assertEqual(set(e.instance['grants']),{'GR-init','GR-research'})
        with self.assertRaises(ValueError): e._action_lifecycle_gate({'role':'intent_interpretation','grant_id':'GR-init'})
        chosen=e.instance['lifecycle']['adoption']['initial_profile_ref']
        actual=ResearchEngine._execution_profile(e,{'role':'intent_interpretation','profile_ref':chosen})
        self.assertEqual(profiles.profile_ref(actual),chosen)
    def test_review_currentness_and_no_persisted_readiness(self):
        e=self.engine; t=e.task(approved=False); e._refresh_readiness(); e._refresh_readiness()
        self.assertEqual(len([a for a in e.runtime['queue'] if a['role']=='task_contract_review']),1)
        e.approve(e.runtime['tasks'][t['id']]); e.runtime['queue'].clear(); e._refresh_readiness()
        self.assertEqual(e._task_readiness[t['id']]['state'],'ready')
        from jsonschema import Draft202012Validator
        from do_math.record_schemas import RECORDS
        readiness_event = next(row for row in e.runtime['events'] if row['kind'] == 'task_became_ready')
        Draft202012Validator(RECORDS['events']).validate(readiness_event)
        self.assertEqual(readiness_event['basis']['records'], e._task_readiness[t['id']]['basis'])
        self.assertEqual(e.runtime['tasks'][t['id']]['status'],'planned'); self.assertNotIn('task_readiness',e.runtime)
        e.control('decision',{'change':{'kind':'policy','record':{'id':'PO-new','kind':'policy','revision':1,'supersedes':[],
            'content':{'rule_id':'new','text':'New evidence requirement','scope':['Target'],
                'reason_refs':['CH-test'],'audit_refs':[]}}}})
        e._refresh_readiness()
        self.assertEqual(e._task_readiness[t['id']]['state'],'not_ready')
        for event in e.runtime['events']:
            Draft202012Validator(RECORDS['events']).validate(event)
    def test_rejected_current_review_not_repeated(self):
        e=self.engine; t=e.task(approved=False); e.approve(t,'rejected'); e._refresh_readiness()
        self.assertFalse(any(a['role']=='task_contract_review' for a in e.runtime['queue']))
    def test_missing_input_and_bad_condition_distinct(self):
        e=self.engine; a=e.task(inputs=['absent']); b=e.task('T2',condition={'op':'unsupported'}); e._refresh_readiness()
        self.assertEqual(e._task_readiness[a['id']]['state'],'not_ready')
        self.assertEqual(e._task_readiness[b['id']]['state'],'evaluation_error')
    def test_completed_removes_readiness_projection(self):
        e=self.engine; t=e.task(); e._refresh_readiness(); e.runtime['tasks'][t['id']]['status']='completed'
        e._refresh_readiness(); self.assertNotIn(t['id'],e._task_readiness)
    def test_pause_returns_to_original_phase_and_preserves_events(self):
        e=self.engine; ev=e._lifecycle_event('user_input_available')
        e.control('pause',{}); e._refresh_readiness(); self.assertIn(ev['id'],e.runtime['pending_events'])
        e.control('pause',{},'UI-again'); e.control('resume',{})
        self.assertEqual(e.instance['lifecycle']['state'],'active')
    def test_published_event_is_not_mutated_when_assigned(self):
        e=self.engine
        event=e._lifecycle_event('user_input_available'); event['event_seq']=1
        original=deepcopy(event)
        e._refresh_readiness()
        self.assertEqual(next(row for row in e.runtime['events'] if row['id']==event['id']),original)
        self.assertIn(event['id'],e.runtime['pending_events'])
        self.assertTrue(any(event['id'] in a.get('event_refs',[]) for a in e.runtime['queue']))
        other=e._lifecycle_event('user_input_available')
        ResearchEngine._consume_action_events(e,{'event_refs':[event['id']]},'EX-accepted-plan')
        self.assertNotIn(event['id'],e.runtime['pending_events'])
        self.assertIn(other['id'],e.runtime['pending_events'])
        self.assertEqual(next(row for row in e.runtime['events'] if row['id']==event['id']),original)
    def test_one_input_request_is_one_event_and_its_consumption_keeps_a_later_request(self):
        e=self.engine; tid=e.task()['id']; task=lambda: e.runtime['tasks'][tid]
        task()['newinput']='RQ-one'
        e._refresh_readiness(); e.current_time+=timedelta(seconds=5); e._refresh_readiness()
        inputs=[row for row in e.runtime['events'] if row['kind']=='task_new_input']
        self.assertEqual([row['request_id'] for row in inputs],['RQ-one'])
        self.assertEqual(e.runtime['pending_events'].count(inputs[0]['id']),1)
        task()['newinput']='RQ-two'
        ResearchEngine._consume_action_events(e,{'event_refs':[inputs[0]['id']]},'EX-accepted-plan')
        self.assertEqual(task()['newinput'],'RQ-two')
        e._refresh_readiness()
        later=next(row for row in e.runtime['events'] if row.get('request_id')=='RQ-two')
        ResearchEngine._consume_action_events(e,{'event_refs':[later['id']]},'EX-accepted-plan')
        self.assertNotIn('newinput',task())
    def test_empty_queue_prepares_from_goal_exhaustion_regardless_of_cycle_count(self):
        e=self.engine; e.runtime['cycles']=1000
        e._refresh_readiness()
        preparation=next((a for a in e.runtime['queue'] if a['role']=='research_preparation'),None)
        self.assertIsNotNone(preparation)
        self.assertIn('exhaustion_basis',preparation)
        self.assertTrue(preparation['exhaustion_basis']['exhausted'])
    def test_conversation_requires_new_live_generation(self):
        e=self.engine; e.control('conversation',{'operation':'attach','id':'chat','generation':1,'lease_seconds':10,'disconnect_policy':'pause'})
        e.current_time+=timedelta(seconds=11); e._check_conversations()
        with self.assertRaises(ValueError): e.control('resume',{})
        with self.assertRaises(ValueError): e.control('conversation',{'operation':'heartbeat','id':'chat','generation':1})
        e.control('conversation',{'operation':'attach','id':'chat','generation':2,'lease_seconds':10})
        e.control('resume',{}); self.assertEqual(e.instance['lifecycle']['state'],'active')
    def test_continue_alias_is_rejected_without_changing_conversation(self):
        e = self.engine
        before = deepcopy((e.instance, e.runtime))
        with self.assertRaisesRegex(ValueError, 'conversation loss policy'):
            e.control('conversation', {'operation': 'attach', 'id': 'chat',
                'generation': 1, 'lease_seconds': 60, 'disconnect_policy': 'continue'})
        self.assertEqual((e.instance, e.runtime), before)

    def test_continue_policy_does_not_pause(self):
        e=self.engine; e.control('conversation',{'operation':'attach','id':'chat','generation':1,'lease_seconds':1,'disconnect_policy':'continue_authorized'})
        e.current_time+=timedelta(seconds=2); e._check_conversations()
        self.assertEqual(e.runtime['conversations']['chat']['status'],'lost')
        self.assertEqual(e.instance['lifecycle']['state'],'active')
    def test_control_replay_and_atomic_rejection(self):
        e=self.engine; q={'operation':'attach','id':'chat','generation':1,'lease_seconds':60,'disconnect_policy':'continue_authorized'}
        e.control('conversation',q,'UI-fixed'); before=deepcopy((e.instance,e.runtime))
        e.control('conversation',q,'UI-fixed'); self.assertEqual((e.instance,e.runtime),before)
        with self.assertRaises(ValueError): e.control('conversation',{**q,'generation':2},'UI-fixed')
        self.assertEqual((e.instance,e.runtime),before)
    def test_empty_trust_activation_records_profile_bound_machine_execution(self):
        e=self.engine; environment=e.environment('empty-transition')
        e.control('trust',{'operation':'transition','env_id':environment})
        run_machine(e,'trust_activate')
        attempts=[row for row in e.runtime['executions'].values() if row['role']=='trust_activate']
        self.assertEqual(len(attempts),1)
        self.assertEqual(attempts[0]['status'],'ended')
        self.assertEqual(attempts[0]['outcome'],'output_accepted')
        self.assertEqual(attempts[0]['submission_receipt']['kind'],'machine_output')
        self.assertIn('execution_profile_ref',attempts[0])
        self.assertEqual(e.runtime['activities'][attempts[0]['owner_activity_id']]['status'],'finished')

    def test_trust_transition_uses_current_storage_contract(self):
        import jsonschema
        from do_math.record_schemas import RECORDS
        e=self.engine; environment=e.environment('schema-transition')
        e.control('trust',{'operation':'transition','env_id':environment})
        transition=next(reversed(e.runtime['trust_transitions'].values()))
        jsonschema.validate(transition,RECORDS['trust_transitions'])


    def test_initial_grant_does_not_queue_research_before_activation(self):
        with tempfile.TemporaryDirectory() as root:
            e=FakeEngine(root)
            e.grant('GR-initial',True)
            self.assertIn('GR-initial', e.instance['grants'])
            self.assertEqual(e.runtime['queue'], [])

    def test_initial_intent_receipt_cannot_replace_import_evidence(self):
        e=self.engine; original=deepcopy(e.runtime['intent_imports'])
        for field in ('check','application','source'):
            with self.subTest(field=field):
                e.runtime['intent_imports']=deepcopy(original)
                bundle=next(iter(e.runtime['intent_imports'].values()))
                if field=='check': bundle['check']['bundle_sha256']='0'*64
                elif field=='application': bundle['application']['status']='awaiting_decision'
                else: bundle['source']['text']='different original'
                with self.assertRaises(ValueError):
                    e._complete_initial_intent(e.instance['lifecycle']['input_id'])

    def test_formal_requires_preapproved_environment(self):
        e=self.engine; env=e._formal_environment()
        self.assertEqual(env['id'],e.instance['active_trust_environment'])
        e.instance['active_trust_environment']=None
        with self.assertRaises(ValueError): e._formal_environment()
    def transition(self):
        e=self.engine; old=e.instance['active_trust_environment']; e.knowledge('K1'); e.knowledge('K2')
        new=e.environment('next'); e.control('trust',{'operation':'transition','env_id':new})
        return old,new,next(reversed(e.runtime['trust_transitions']))
    def test_full_transition_preserves_old_formal_records_and_full_command(self):
        e=self.engine; old,new,tid=self.transition(); prior=deepcopy(e.instance['formal_results'])
        with self.assertRaises(ValueError): e._formal_environment()
        run_machine(e,'trust_check'); self.assertEqual(e.instance['active_trust_environment'],old)
        run_machine(e,'trust_check'); run_machine(e,'trust_activate'); self.assertEqual(e.instance['active_trust_environment'],new)
        for fid,row in prior.items(): self.assertEqual(e.instance['formal_results'][fid],row)
        for args in e.formal_calls: self.assertEqual(args['lean_command'],args['expected_toolchain']['configured_command'])
        for row in e.runtime['executions'].values():
            self.assertIn('execution_profile_ref',row); self.assertIn('owner_activity_id',row)
            if row['role']=='trust_check':
                self.assertEqual(row['outcome'],'output_accepted')
                self.assertEqual(row['submission_receipt']['kind'],'machine_output')
    def test_partial_failure_cannot_activate(self):
        e=self.engine; old,new,tid=self.transition()
        e.formal_behavior=lambda args:{'status':'failed','reason':'fixture'}
        run_machine(e,'trust_check'); run_machine(e,'trust_check')
        run_machine(e,'trust_activate')
        self.assertEqual(e.instance['active_trust_environment'],old); self.assertEqual(e.runtime['trust_transitions'][tid]['status'],'failed')
    def test_wrong_compiler_is_rejected(self):
        e=self.engine; old,new,tid=self.transition()
        e.formal_behavior=lambda a:{**e.verification(a['source'],a['declarations'],a['expected_toolchain']),'toolchain':{'sha256':'wrong'}}
        run_machine(e,'trust_check'); self.assertEqual(e.runtime['trust_transitions'][tid]['results']['K1']['status'],'rejected')
    def test_changed_semantics_requires_independent_review(self):
        e=self.engine; old,new,tid=self.transition()
        def changed(a):
            r=e.verification(a['source'],a['declarations'],a['expected_toolchain'])
            r['declaration_evidence']={d:{'type':'changed'} for d in a['declarations']}; return r
        e.formal_behavior=changed; run_machine(e,'trust_check'); run_machine(e,'trust_check')
        run_machine(e,'trust_activate')
        self.assertEqual(e.instance['active_trust_environment'],old)
        self.assertEqual(e.runtime['trust_transitions'][tid]['status'],'ready')
        self.assertEqual(len([c for c in e.runtime['review_cycles'].values() if c.get('transition_id')==tid]),2)
    def test_completed_target_not_repeated_on_recovery(self):
        e=self.engine; old,new,tid=self.transition(); a=run_machine(e,'trust_check')
        calls=len(e.formal_calls); e._run_trust_check(a); self.assertEqual(len(e.formal_calls),calls)
        run_machine(e,'trust_check'); run_machine(e,'trust_activate'); self.assertEqual(e.instance['active_trust_environment'],new)
    def olean(self,environment_id):
        return Path(self.engine.instance['trust_environments'][environment_id]['toolchain']['executable']).parents[1]/'lib/lean/Init/Prelude.olean'
    def test_changed_olean_blocks_trust_check_before_compiling(self):
        e=self.engine; old,new,tid=self.transition()
        self.olean(new).write_bytes(b'changed module bytes')
        run_machine(e,'trust_check')
        result=e.runtime['trust_transitions'][tid]['results']['K1']
        self.assertEqual(result['status'],'failed')
        self.assertEqual(result['error_kind'],'trust_environment')
        self.assertIn('olean fingerprint differs',result['reason'])
        self.assertEqual(result['environment_check']['changed_files'],['toolchain/lib/lean/Init/Prelude.olean'])
        self.assertEqual(e.formal_calls,[])
    def test_registration_reads_the_shared_record_without_scanning_files(self):
        from research_fixtures import trust_fixture
        e=self.engine; request=trust_fixture(self.engine.root/'shared',['synthetic-lean','shared'])
        with patch('do_math.trust_inventory.observe_fingerprint',side_effect=AssertionError('registration scanned files')), \
             patch('do_math.trust_inventory.content_hashes',side_effect=AssertionError('registration hashed files')):
            e._trust_control(request,'UI-shared-one'); e._trust_control(request,'UI-shared-two')
        shared=[eid for eid,row in e.instance['trust_environments'].items() if row['toolchain']==request['toolchain']]
        self.assertEqual(len(shared),2)
        for eid in shared:
            self.assertEqual(e.instance['trust_environments'][eid]['toolchain_record'],request['toolchain_record'])
            self.assertEqual(e.runtime['trust_bindings'][eid],request['binding'])
        changed={**request,'binding':{**request['binding'],'fingerprint_sha256':'0'*64}}
        with self.assertRaisesRegex(ValueError,'differs from its toolchain record'): e._trust_control(changed,'UI-shared-bad')
        registered=dict(e.instance['trust_environments'])
        duplicated={**request,'allowed_axioms':[*request['allowed_axioms'],request['allowed_axioms'][0]]}
        with self.assertRaisesRegex(ValueError,'foundation axiom profile differs'): e._trust_control(duplicated,'UI-shared-dup')
        self.assertEqual(e.instance['trust_environments'],registered)
    def test_rerecorded_baseline_is_followed_once_with_an_event(self):
        import os, setup_lean
        from research_fixtures import fixture_setup_lean
        e=self.engine; old,new,tid=self.transition()
        environment=e.instance['trust_environments'][new]; before=deepcopy(e.runtime['trust_bindings'][new])
        path=self.olean(new); info=os.stat(path); os.utime(path,ns=(info.st_atime_ns,info.st_mtime_ns+10**9))
        record_path=Path(environment['toolchain_record']['path'])
        with fixture_setup_lean(environment['toolchain'],self.engine.root/'smoke.lean'):
            recorded=setup_lean.rerecord(['unused'],record_path.parent,self.engine.root/'evidence',None)
        run_machine(e,'trust_check'); run_machine(e,'trust_check'); run_machine(e,'trust_activate')
        self.assertEqual(e.instance['active_trust_environment'],new)
        self.assertEqual(e.runtime['trust_bindings'][new],recorded['binding'])
        events=[row for row in e.runtime['events'] if row['kind']=='trust_environment_rebound']
        self.assertEqual(len(events),1)
        self.assertEqual((events[0]['previous'],events[0]['current']),(before,recorded['binding']))
        # Rebinding changed only the runtime binding; activation adds its status and receipt.
        activated=e.instance['trust_environments'][new]
        self.assertEqual(environment,{**{k:v for k,v in activated.items() if k!='validation_receipt'},'status':'registered'})
        self.assertEqual(activated['validation_receipt']['binding'],recorded['binding'])
    def test_clock_regression_precedes_authority(self):
        e=self.engine; e.runtime['last_observed_utc']=(e.current_time+timedelta(seconds=1)).isoformat()
        before=deepcopy(e.instance['grants'])
        with self.assertRaisesRegex(ValueError,'clock'): e.grant('GR-bad')
        self.assertEqual(e.instance['grants'],before)
        with self.assertRaisesRegex(ValueError,'clock'): e._action_lifecycle_gate({'role':'external_action'})

    def test_dispatch_uses_current_task_predicate(self):
        e=self.engine; t=e.task(); a={'id':'AC-work','role':'research_work','target':t['id']}
        e.runtime['queue']=[a]
        with patch.object(e,'_revision_dispatch_waits',autospec=True,return_value=[]), patch.object(e,'_selected_action_current',autospec=True,return_value=True), patch.object(e,'_provider_status',autospec=True,return_value={'providers':{}}):
            self.assertTrue(e._dispatchable(a))
            e.runtime['tasks'][t['id']]['inputs'].append('absent')
            self.assertFalse(e._dispatchable(a))
            e.runtime['tasks'][t['id']]['inputs']=[]
            e.runtime['tasks'][t['id']]['status']='ready'
            e.runtime['task_readiness']={t['id']:{'state':'ready'}}
            self.assertFalse(e._dispatchable(a))
            self.assertEqual(a['dispatch_wait']['kind'],'task_readiness')

    def test_task_artifact_context_reaches_refresh_and_dispatch(self):
        from do_math.repository import ResearchRepository
        e=self.engine; raw=b'{"valid":true}'
        path='runtime/artifacts/EX-evidence/result.json'
        e.store=create_autospec(ResearchRepository,instance=True)
        e.store.read.return_value=raw; e.store.git_dir=None
        condition={'op':'artifact_valid','artifact_ref':{'snapshot':'sealed-evidence',
            'path':path,'sha256':hashlib.sha256(raw).hexdigest()}}
        t=e.task(condition=condition); e.approve(t)
        e._refresh_readiness()
        self.assertEqual(e._task_readiness[t['id']]['state'],'ready')
        a={'id':'AC-artifact','role':'research_work','target':t['id']}
        e.runtime['queue']=[a]
        with patch.object(e,'_revision_dispatch_waits',autospec=True,return_value=[]), patch.object(e,'_selected_action_current',autospec=True,return_value=True) as selected, patch.object(e,'_provider_status',autospec=True,return_value={'providers':{}}):
            self.assertTrue(e._dispatchable(a))
            context=selected.call_args.kwargs['evaluation_context']
            self.assertTrue(callable(context['validate_artifact']))
            self.assertEqual(context['read_artifact'](path,'sealed-evidence'),raw)
        self.assertTrue(all(call.args==(path,'sealed-evidence') for call in e.store.read.call_args_list))

    def test_stop_and_resume_trust_check_preserves_attempt_lineage(self):
        e=self.engine; old,new,tid=self.transition()
        def stop(args):
            e._pause_lifecycle('test_pause'); return {'status':'stopped'}
        e.formal_behavior=stop; run_machine(e,'trust_check')
        first=next(row for row in e.runtime['executions'].values() if row['role']=='trust_check')
        self.assertEqual(first['status'],'ended'); self.assertNotIn('K1',e.runtime['trust_transitions'][tid]['results'])
        e.formal_behavior=None; e.control('resume',{}); run_machine(e,'trust_check')
        attempts=[row for row in e.runtime['executions'].values() if row['role']=='trust_check']
        self.assertEqual(attempts[1]['owner_activity_id'],first['owner_activity_id'])
        self.assertEqual(attempts[1]['continuation_of'],first['id'])

    def test_assigned_events_survive_and_live_input_is_not_changed(self):
        e=self.engine; first=e._lifecycle_event('user_input_available'); e._refresh_readiness()
        a=next(a for a in e.runtime['queue'] if a['role']=='research_plan'); original=deepcopy(a)
        e.runtime['executions']['EX-live']={'id':'EX-live','role':'research_plan','status':'running','action':deepcopy(a)}
        second=e._lifecycle_event('user_input_available'); e._refresh_readiness()
        self.assertEqual(next(a for a in e.runtime['queue'] if a.get('id')==original['id']),original)
        self.assertTrue({first['id'],second['id']} <= set(e.runtime['pending_events']))

    def http(self,url):
        from urllib.parse import urlsplit
        e=self.engine; parsed=urlsplit(url)
        e.grant('GR-http',http={'kind':'http','allowed_origins':[parsed.scheme+'://'+parsed.netloc],
            'allowed_methods':['POST'],'allowed_path_prefixes':['/'],'reuse':'reusable'})
        e.control('external',{'operation':'prepare','id':'EO-test','grant_id':'GR-http',
            'request':{'method':'POST','url':url,'body':'test'}})
        return e.runtime['external_operations']['EO-test']

    def test_real_loopback_unknown_reconcile_and_retry_share_activity(self):
        from http.server import BaseHTTPRequestHandler,HTTPServer
        import threading
        class Handler(BaseHTTPRequestHandler):
            count=0
            def do_POST(self):
                self.rfile.read(int(self.headers.get('Content-Length','0')))
                type(self).count+=1; self.send_response(503); self.end_headers(); self.wfile.write(b'uncertain')
            def log_message(self,*args): pass
        server=HTTPServer(('127.0.0.1',0),Handler)
        thread=threading.Thread(target=server.serve_forever,daemon=True); thread.start()
        self.addCleanup(server.server_close); self.addCleanup(server.shutdown)
        e=self.engine; op=self.http('http://127.0.0.1:'+str(server.server_port)+'/effect')
        e.machine('external_action'); op=e.runtime['external_operations'][op['id']]
        self.assertEqual(op['http_status'],503)
        self.assertEqual(op['status'],'unknown'); self.assertIsNone(op['succeeded'])
        with self.assertRaises(ValueError): e.control('external',{'operation':'retry','id':op['id'],'grant_id':'GR-http'})
        with self.assertRaises(ValueError): e.control('external',{'operation':'reconcile','id':op['id'],'result':'failed','evidence':'string'})
        e.control('external',{'operation':'reconcile','id':op['id'],'result':'failed','evidence':{
            'evidence_ref':'remote-admin-log','operation_id':op['id'],'request_sha256':op['request_sha256'],
            'idempotency_key':op['idempotency_key'],'fact':'effect_absent','observed_at':e.current_time.isoformat()}})
        e.control('external',{'operation':'retry','id':op['id'],'grant_id':'GR-http'})
        # The new attempt is not the reconciled one: its handling goes with its reconciliation.
        retried=e.runtime['external_operations'][op['id']]
        self.assertEqual(retried['status'],'prepared')
        self.assertNotIn('handling',retried); self.assertNotIn('reconciliation',retried)
        from do_math.record_schemas import RECORD_RULES
        RECORD_RULES['external_operations'](retried)  # the storage rules of one operation record
        e.machine('external_action'); self.assertEqual(Handler.count,2)
        attempts=[row for row in e.runtime['executions'].values() if row['role']=='external_action']
        self.assertEqual(attempts[0]['owner_activity_id'],attempts[1]['owner_activity_id'])
        self.assertEqual(attempts[1]['continuation_of'],attempts[0]['id'])

    def test_revocation_before_transport_cancels(self):
        e=self.engine; op=self.http('http://127.0.0.1:1/effect')
        e.control('decision',{'change':{'kind':'revoke','grant_id':'GR-http'}})
        self.assertEqual(e.runtime['external_operations'][op['id']]['status'],'cancelled')
        with patch('do_math.external._http') as transport:
            e._run_external_action({'role':'external_action','target':op['id'],'grant_id':'GR-http'})
            transport.assert_not_called()

    def test_prepare_replay_preserves_unknown_ledger(self):
        e=self.engine; op=self.http('http://127.0.0.1:1/effect')
        e.runtime['external_operations'][op['id']].update(status='unknown',transmitted=True)
        before=deepcopy(e.runtime['external_operations'][op['id']])
        e.control('external',{'operation':'prepare','id':op['id'],'grant_id':'GR-http','request':op['request']})
        self.assertEqual(e.runtime['external_operations'][op['id']],before)

    def test_capability_evidence_rejects_changed_host_or_forged_record(self):
        e=self.engine; ref=e.instance['role_profile_refs']['intent_interpretation'][0]
        self.assertTrue(e._capability_requirements(ref)['satisfied'])
        with patch.object(FixtureAdapter,'capability_identity',return_value={'host':'different'}):
            self.assertFalse(e._capability_requirements(ref)['satisfied'])
        for row in e.instance['capability_evidence'].values(): row['identity']={'forged':True}
        self.assertFalse(e._capability_requirements(ref)['satisfied'])

    def test_changed_fixed_source_never_activates_transition(self):
        e=self.engine; old,new,tid=self.transition()
        formal=e.instance['formal_results'][e.instance['knowledge']['K1']['formal_result_id']]
        formal['lean_code']+='\n-- changed'
        run_machine(e,'trust_check'); run_machine(e,'trust_check')
        self.assertEqual(e.instance['active_trust_environment'],old)

    def test_http_success_finishes_activity_without_changing_effect_fact(self):
        e=self.engine; op=self.http('http://127.0.0.1:1/effect')
        with patch('do_math.external._http',return_value={'http_status':201,'body':b'created'}):
            e.machine('external_action')
        op=e.runtime['external_operations'][op['id']]
        self.assertEqual(op['status'],'confirmed'); self.assertIs(op['succeeded'],True)
        ex=e.runtime['executions'][op['execution_id']]
        self.assertEqual(e.runtime['activities'][ex['owner_activity_id']]['status'],'finished')
        self.assertEqual(ex['outcome'],'output_accepted')
        self.assertEqual(ex['submission_receipt']['kind'],'machine_output')

    def test_authority_revoked_at_send_gate_prevents_transport(self):
        e=self.engine; op=self.http('http://127.0.0.1:1/effect'); count=[0]
        def controls(*, pump=True):
            count[0]+=1
            if count[0]==4: e.instance['grants']['GR-http']['status']='revoked'
        # The external stop judgment applies the inbox (a revoking control) before each send step.
        e._apply_inbox=create_autospec(e._apply_inbox,side_effect=controls)
        with patch('do_math.external._http') as transport:
            e.machine('external_action'); transport.assert_not_called()
        self.assertEqual(e.runtime['external_operations'][op['id']]['status'],'cancelled')

    def test_failure_before_any_send_step_is_an_untransmitted_cancellation(self):
        e=self.engine; op=self.http('http://127.0.0.1:1/effect')
        with patch('do_math.external_engine.execute_operation',side_effect=ValueError('grant is inactive')):
            e.machine('external_action')
        op=e.store.load()[2]['external_operations'][op['id']]
        self.assertEqual((op['status'],op['transmitted'],op['succeeded']),('cancelled',False,False))
        from do_math.record_schemas import RECORD_RULES
        RECORD_RULES['external_operations'](op)  # the storage rules of one operation record

    def test_session_capacity_reads_git_reservations_not_sqlite(self):
        e=self.engine; resources=e._session_resources()
        self.assertTrue(resources)
        for row in resources.values(): self.assertEqual(set(row),{'limit','used','execution_ids','available'})
        self.assertFalse((e.root/'session-slots').exists())

    def test_invalidated_split_knowledge_invalidates_dependent_goal(self):
        from do_math.knowledge import plan_impact, capture_basis
        e=self.engine; e.knowledge('K1')
        e.instance['goal_status']='mathematically_solved'
        e.instance['goal_judgments']=[{'id':'G1','dependencies':['K1'],'current':True,
            'record_basis':capture_basis(e.instance,e.runtime,['K1'])}]
        impact=plan_impact(e.instance,e.runtime,['K1'],[])
        e.control('knowledge',{'operation':'invalidate','id':'K1','reason':'User withdrew this result',
            'declared_impact':impact['computed_impact']})
        self.assertEqual(e.instance['goal_status'],'unsolved')
        self.assertFalse(e.instance['goal_judgments'][0]['current'])

class LifecycleBoundaryTests(unittest.TestCase):
    """Clock, trust, limited-recovery and close boundaries of the lifecycle, on in-memory engines."""

    def test_event_uses_the_clock_sample_that_passed_the_guard(self):
        with tempfile.TemporaryDirectory() as root:
            e = FakeEngine(root)
            approved = e.current_time+timedelta(seconds=2)
            samples = iter([approved.isoformat(),(approved-timedelta(seconds=1)).isoformat()])
            e.lifecycle_clock = lambda:next(samples)
            event=e._lifecycle_event('test_clock_observation',schedule=False)
            self.assertEqual(event['at'],approved.isoformat())
            self.assertEqual(e.runtime['last_observed_utc'],approved.isoformat())

    def test_scheduler_scopes_maintenance_dispatch_with_executor_double(self):
        with tempfile.TemporaryDirectory() as root, patch('do_math.initialization.adapter_for', return_value=FixtureAdapter()):
            e = FakeEngine(root); e.activate(); e._pause_lifecycle('user_pause')
            e.grant('GR-repair',http={'kind':'local','roles':['maintenance'],
                'reuse':'once','included_targets':['RI-test']})
            e.runtime['queue'] = [{'id':'AC-repair','role':'maintenance','target':'RI-test'},
                                  {'id':'AC-general','role':'research_preparation'}]
            action = e.runtime['queue'][0]
            e.control('decision',{'change':{'kind':'limited_recovery','action_id':'AC-repair',
                'grant_id':'GR-repair','profile_ref':e._select_model(action)['profile_ref'],
                'purpose':'inspect the exact recovery target','procedure':'Inspect this target only; do not resume research',
                'expires_at':(e.current_time+timedelta(minutes=5)).isoformat()}})
            dispatched=[]
            def executor_double(action):
                e._action_lifecycle_gate(action)
                execution=e._register_execution(action,{'id':'EX-repair','role':action['role'],'status':'running'})
                dispatched.append(deepcopy(execution))
                e._end_machine_execution(execution,outcome='execution_incomplete',disposition={'kind':'executor_double'})
                e.runtime['queue'][:]=[row for row in e.runtime['queue'] if row['id']!=action['id']]
                if False: yield
            e._call_steps=create_autospec(e._call_steps,side_effect=executor_double)
            e._check_installation=create_autospec(e._check_installation)
            e._provider_status=create_autospec(e._provider_status,return_value={'providers':{}})
            e._selected_action_current=create_autospec(e._selected_action_current,return_value=True)
            e._revision_dispatch_waits=create_autospec(e._revision_dispatch_waits,return_value=[])
            e._run_parallel(max_steps=1)
            self.assertEqual([row['role'] for row in dispatched],['maintenance'])
            self.assertEqual(e.runtime['status'],'paused')
            self.assertEqual(e.runtime['queue'][0]['id'],'AC-general')

    def test_wrong_pinned_trust_command_ends_attempt_without_verifier(self):
        with tempfile.TemporaryDirectory() as root, patch('do_math.initialization.adapter_for', return_value=FixtureAdapter()):
            e = FakeEngine(root); e.activate(); e.knowledge('K1')
            old_ref = profiles.profile_ref(e._execution_profile({'role':'trust_check'}))
            env = e.environment('next')
            e.control('trust', {'operation':'transition','env_id':env})
            action = next(a for a in e.runtime['queue'] if a['role']=='trust_check')
            action['profile_ref'] = old_ref
            with owner_calls(e):
                e._process_machine_action(action)
            self.assertEqual(e.formal_calls,[])
            execution = next(x for x in e.runtime['executions'].values() if x['role']=='trust_check')
            self.assertEqual(execution['status'],'ended')
            self.assertEqual(execution['outcome'],'execution_incomplete')
            self.assertEqual([x['id'] for x in e.runtime['executions'].values() if x['status']!='ended'],[])

    def test_terminal_marker_cannot_have_live_projection(self):
        from do_math.record_schemas import validate_lifecycle
        with tempfile.TemporaryDirectory() as root:
            e = FakeEngine(root)
            e.instance['lifecycle']['permanently_closed'] = True
            with self.assertRaisesRegex(ValueError, 'permanently closed'):
                validate_lifecycle(e.instance,e.runtime)
            e.runtime['status'] = 'closed'
            validate_lifecycle(e.instance,e.runtime)

    def test_scheduler_runs_only_approved_machine_recovery_and_stays_paused(self):
        with tempfile.TemporaryDirectory() as root, patch('do_math.initialization.adapter_for', return_value=FixtureAdapter()):
            e = FakeEngine(root); e.activate()
            env = e.environment('repair')
            e.control('trust', {'operation':'transition','env_id':env})
            e._pause_lifecycle('user_pause')
            e.grant('GR-repair',http={'kind':'local','roles':['trust_activate'],
                'reuse':'once','purposes':['activate empty verified environment']})
            action = next(a for a in e.runtime['queue'] if a['role']=='trust_activate')
            e.control('decision',{'change':{'kind':'limited_recovery','action_id':action['id'],
                'grant_id':'GR-repair','profile_ref':profiles.profile_ref(e._execution_profile(action)),
                'purpose':'activate empty verified environment','procedure':'Activate this empty target transition only',
                'expires_at':(e.current_time+timedelta(minutes=5)).isoformat()}})
            e.runtime['queue'].insert(0,{'id':'AC-general','role':'research_preparation'})
            e._check_installation=create_autospec(e._check_installation)
            e._selected_action_current=create_autospec(e._selected_action_current,return_value=True)
            e._revision_dispatch_waits=create_autospec(e._revision_dispatch_waits,return_value=[])
            e._run_parallel(max_steps=1)
            self.assertEqual(e.instance['active_trust_environment'],env)
            self.assertEqual(e.runtime['status'],'paused')
            self.assertEqual(e.instance['lifecycle']['state'],'paused')
            self.assertTrue(any(a['id']=='AC-general' for a in e.runtime['queue']))
            repair = [x for x in e.runtime['executions'].values() if x['role']=='trust_activate'][-1]
            self.assertEqual(repair['status'],'ended')
            self.assertEqual(repair['submission_receipt']['state'],'accepted')

    def test_changed_transition_opens_real_review_without_live_publication(self):
        with tempfile.TemporaryDirectory() as root, patch('do_math.initialization.adapter_for', return_value=FixtureAdapter()):
            e = FakeEngine(root); e.activate(); e.knowledge('K1')
            new = e.environment('next')
            before = deepcopy(e.instance)
            e.control('trust', {'operation':'transition','env_id':new})
            def changed(args):
                result = e.verification(args['source'],args['declarations'],args['expected_toolchain'])
                result['declaration_evidence'] = {d:{'type':'Changed proposition'} for d in args['declarations']}
                return result
            e.formal_behavior = changed
            run_machine(e,'trust_check')
            run_machine(e,'trust_activate')
            transition = next(reversed(e.runtime['trust_transitions'].values()))
            self.assertEqual(transition['status'],'ready')
            cycles = [r for r in e.runtime['review_cycles'].values() if r.get('transition_id')==transition['id']]
            self.assertEqual(len(cycles),1)
            self.assertTrue(any(a.get('review_cycle_id')==cycles[0]['id'] for a in e.runtime['queue']))
            for family in ('knowledge','formal_results','identity_assessments','assessment_uses'):
                self.assertEqual(e.instance.get(family), before.get(family))

    def test_trust_verifier_uses_registered_command_without_deadline(self):
        with tempfile.TemporaryDirectory() as root, patch('do_math.initialization.adapter_for', return_value=FixtureAdapter()):
            e = FakeEngine(root); e.activate(); e.knowledge('K1')
            new = e.environment('next')
            command = e.instance['trust_environments'][new]['toolchain']['configured_command']
            fixed = profiles.build_profiles({**e.instance['config'], 'lean_command':command, })
            p = next(p for p in fixed['execution_profiles'].values() if p['role']=='trust_check')
            e.instance['execution_profiles'][p['id']] = p
            e.instance['role_profile_refs']['trust_check'] = [profiles.profile_ref(p)]
            e.control('trust', {'operation':'transition','env_id':new})
            run_machine(e,'trust_check')
            self.assertEqual(len(e.formal_calls),1)
            self.assertNotIn("timeout_seconds", e.formal_calls[0])
            self.assertEqual(e.formal_calls[0]['lean_command'],command)

    def test_paused_recovery_is_exact_authorized_and_revocable(self):
        with tempfile.TemporaryDirectory() as root, patch('do_math.initialization.adapter_for', return_value=FixtureAdapter()):
            e = FakeEngine(root); e.activate(); e._pause_lifecycle('user_pause')
            e.grant('GR-repair', http={'kind':'local','roles':['maintenance'],'included_targets':['RI-test'],
                'purposes':['restore sealed input'],'reuse':'once'})
            action = {'id':'AC-repair','role':'maintenance','target':'RI-test','purpose':'restore sealed input'}
            e.runtime['queue'].append(action)
            ref = e._select_model(action)['profile_ref']
            e.control('decision', {'change': {'kind':'limited_recovery','action_id':'AC-repair',
                'grant_id':'GR-repair','profile_ref':ref,'purpose':'restore sealed input',
                'procedure':'Restore the specified sealed input and verify its digest',
                'expires_at':(e.current_time+timedelta(minutes=5)).isoformat()}})
            action = next(a for a in e.runtime['queue'] if a['id'] == 'AC-repair')
            e._check_limited_recovery(action)
            e._action_lifecycle_gate(action)
            self.assertTrue(e._limited_recovery_allowed(action))
            self.assertFalse(e._execution_stop_requested(action))
            self.assertEqual(e.runtime['status'],'paused')
            prior_stop = e.runtime['stop_requested']
            e.runtime['stop_requested'] = 'new_emergency_stop'
            self.assertFalse(e._limited_recovery_allowed(action))
            e.runtime['stop_requested'] = prior_stop
            with self.assertRaises(ValueError): e._action_lifecycle_gate({**action,'target':'RI-other'})
            with self.assertRaises(ValueError): e._action_lifecycle_gate({'role':'research_preparation'})
            e._pause_lifecycle('new_pause')
            self.assertFalse(e._limited_recovery_allowed(action))
            self.assertTrue(e._execution_stop_requested(action))

    def test_limited_recovery_refuses_unbound_requests_and_surfaces_check_defects(self):
        with tempfile.TemporaryDirectory() as root:
            e = FakeEngine(root)
            with patch.object(e, '_check_limited_recovery', side_effect=AssertionError('unbound request checked')):
                self.assertFalse(e._limited_recovery_allowed({'id': 'AC-plain', 'role': 'maintenance'}))
            bound = {'id': 'AC-bound', 'role': 'maintenance', 'repair': {'limited_recovery': {'source_ref': 'UC-one'}}}
            with patch.object(e, '_check_limited_recovery', side_effect=KeyError('defect')):
                with self.assertRaises(KeyError):
                    e._limited_recovery_allowed(bound)

    def test_closed_pause_cannot_reopen(self):
        with tempfile.TemporaryDirectory() as root:
            e = FakeEngine(root)
            e.runtime['status'] = 'closed'
            before = deepcopy((e.instance, e.runtime))
            with self.assertRaises(ValueError):
                e._pause_lifecycle('user_pause')
            self.assertEqual((e.instance, e.runtime), before)
            with self.assertRaises(ValueError):
                e._resume_lifecycle({'origin': 'user'})

    def test_close_control_seals_terminal_marker(self):
        with tempfile.TemporaryDirectory() as root:
            e = FakeEngine(root)
            self.assertTrue(e.control('close', {}))
            self.assertTrue(e.instance['lifecycle']['permanently_closed'])
            self.assertEqual(e.runtime['status'], 'closed')
            self.assertEqual(e.runtime['queue'], [])
            with self.assertRaises(ValueError): e.control('pause', {})
            with self.assertRaises(ValueError): e.control('resume', {})

    def test_original_unicode_bytes_survive_canonical_roundtrip(self):
        import json
        from do_math.repository import canonical_json
        from do_math.initialization import original_input_bytes
        with tempfile.TemporaryDirectory() as root:
            source = 'Cafe\u0301'
            instance, runtime = initialize_state(instance_id='RI-unicode', goal=source,
                workspace=root, config=DEFAULT_CONFIG, source_input=source)
            restored = json.loads(canonical_json(instance))
            original = restored['lifecycle']['immutable_input']
            self.assertEqual(original_input_bytes(original), source.encode())
            self.assertEqual(original['text'], source)
            self.assertEqual(runtime['inputs'][0]['sha256'], original['sha256'])
            original['text'] = 'wrong'
            with self.assertRaises(ValueError): original_input_bytes(original)

    def test_negative_job_is_not_cleared_by_later_help_probe(self):
        from do_math.initialization import capability_requirements
        with tempfile.TemporaryDirectory() as root:
            e = FakeEngine(root)
            p = e._execution_profile({'role': 'maintenance'})
            negative = profiles.structural_failure_evidence(p, IDENTITY,
                observed_at=e.current_time.isoformat(), execution_id='EX-failed', evidence_ref='failure.json')
            positive = profiles.capability_evidence(p, FixtureAdapter().describe(),
                observed_at=(e.current_time + timedelta(seconds=1)).isoformat())
            e.instance['capability_evidence'] = {r['id']: r for r in (negative, positive)}
            outcome = capability_requirements(e.instance, profiles.profile_ref(p), current_identity=IDENTITY,
                at=(e.current_time + timedelta(seconds=2)).isoformat())
            self.assertFalse(outcome['satisfied'])
            self.assertIn('atomic_local_job', outcome['missing'])

class GrantAndExternalEffectTests(unittest.TestCase):
    """Grant adoption and selection, initial queueing, and external HTTP effects and their controls."""

    setUp = LifecycleTests.setUp

    def test_machine_records_use_registered_schema_and_existing_source_provenance(self):
        import jsonschema
        from do_math.record_schemas import RECORDS
        e=self.engine
        config=self.prepare_http()
        e.control('external',config)
        op=e.runtime['external_operations'][config['id']]
        validate=lambda record,family: self.assertEqual(
            [error.message for error in jsonschema.Draft202012Validator(RECORDS[family]).iter_errors(record)],[])
        validate(op,'external_operations')
        event=next(row for row in e.runtime['events']
                   if row['kind']=='external_operation_prepared' and row['target']==op['id'])
        self.assertIn(event['source_ref'],e.instance['governance_sources'])
        with patch('do_math.external._http',return_value={'http_status':201,'body':b'ok'}):
            e.machine('external_action')
        validate(e.runtime['external_operations'][op['id']],'external_operations')
        environment=e.environment('audit-schema')
        e.control('trust',{'operation':'transition','env_id':environment})
        run_machine(e,'trust_activate')
        LifecycleTests.transition(self)
        run_machine(e,'trust_check'); run_machine(e,'trust_check')
        for execution in e.runtime['executions'].values():
            if execution['role'] in {'external_action','trust_activate','trust_check'}:
                validate(execution,'executions')
                self.assertTrue(execution['action']['source_ref'])
                if execution['role'].startswith('trust_'):
                    self.assertEqual(execution['result_ref'],execution['submission_receipt']['evidence_ref'])

    def test_ambiguous_adopted_grants_are_not_selected_by_order(self):
        e=self.engine; e.grant('GR-other')
        e.instance['lifecycle']['adoption']['research_grant_ids']=['GR-other','GR-research']
        action={'id':'AC-ambiguous','role':'research_preparation'}
        with self.assertRaisesRegex(ValueError,'ambiguous'):
            e._action_lifecycle_gate(action)
        self.assertNotIn('grant_id',action)
        selected={**action,'grant_id':'GR-research'}
        e._action_lifecycle_gate(selected)
        self.assertEqual(selected['grant_id'],'GR-research')

    def test_initial_queue_does_not_manufacture_explicit_grant_choice(self):
        e=self.engine; e.grant('GR-init-other',True)
        lifecycle=e.instance['lifecycle']
        lifecycle.update(state='initializing'); lifecycle.pop('intent_check',None)
        lifecycle['adoption']['initial_grant_ids']=['GR-init-other','GR-init']
        e.runtime['queue'].clear()
        e._queue_initial_intent()
        action=next(a for a in e.runtime['queue'] if a['role']=='intent_interpretation')
        self.assertNotIn('grant_id',action)
        with self.assertRaisesRegex(ValueError,'ambiguous'):
            e._action_lifecycle_gate(action)
        lifecycle['adoption']['initial_grant_ids']=['GR-init']
        e._action_lifecycle_gate(action)
        self.assertEqual(action['grant_id'],'GR-init')

    def test_initial_queue_treats_held_input_overflow_as_the_same_request(self):
        e=self.engine
        lifecycle=e.instance['lifecycle']
        lifecycle.update(state='initializing'); lifecycle.pop('intent_check',None)
        input_id=lifecycle['input_id']
        held={'id':'AC-held-overflow','role':'intent_interpretation','target':input_id,
              'stage':'interpret','initialization':True}
        e.runtime['queue'].clear()
        e.runtime['waiting_actions']={held['id']:{'action':held,'kind':'input_overflow',
            'reason':'input_overflow','next_owner':'user'}}
        e._queue_initial_intent()
        self.assertEqual(e.runtime['queue'],[],
            'a held initial request must not be regenerated under a new action ID')

    def test_retry_reuses_the_exact_held_action_and_current_authority(self):
        from do_math import activities, questions
        e=self.engine
        action={'id':'AC-held-overflow','role':'research_preparation'}
        e._action_lifecycle_gate(action)
        activity=e._activity_for_action(action)
        condition={'kind':'input_overflow','action_ids':[action['id']]}
        activities.wait_for(e.runtime,activity['id'],reason='input_overflow',
                            condition=condition,next_owner='user',at=e.current_time.isoformat())
        question=questions.link(e.runtime,execution_id='EX-overflow',
            field='resolution_question/question',owner='user',targets=[action['id']],blocks=True)
        e.runtime['queue'].clear()
        e.runtime['waiting_actions'][action['id']]={'action':deepcopy(action),'kind':'input_overflow',
            'reason':'input_overflow','question_id':question['id'],'next_owner':'user'}
        prior_profile=deepcopy(action['profile_ref'])
        retried=ResearchEngine._retry_input_overflow_action(e,{'id':'UC-retry','config':{
            'retry_action':action['id']}})
        self.assertEqual(retried['id'],action['id'])
        self.assertEqual(retried['owner_activity_id'],activity['id'])
        self.assertEqual(retried['profile_ref'],prior_profile)
        self.assertEqual(e.runtime['activities'][activity['id']]['status'],'ready')
        self.assertNotIn(action['id'],e.runtime['waiting_actions'])
        self.assertEqual(question['status'],'open','a request does not prove that packing now fits')
        e.runtime['status']='closed'
        with self.assertRaisesRegex(ValueError,'closed/completed'):
            ResearchEngine._retry_input_overflow_action(e,{'id':'UC-closed','config':{
                'retry_action':action['id']}})

    def test_adoption_preserves_approved_grants_and_disjoint_initial_scope(self):
        from do_math.governance import validate_grant_source
        e=self.engine
        for grant in e.instance['grants'].values():
            approved=e.instance['decisions'][grant['decision_id']]['change']['grant']
            self.assertEqual(grant.get('initialization_only'),approved.get('initialization_only'))
            validate_grant_source(e.instance,grant)
        with self.assertRaises(ValueError):
            e._action_lifecycle_gate({'role':'intent_interpretation','grant_id':'GR-init'})
        with tempfile.TemporaryDirectory() as root:
            initial=FakeEngine(root); initial.grant('GR-narrow',True)
            before=deepcopy(initial.instance['grants'])
            with self.assertRaisesRegex(ValueError,'distinct grants'):
                initial.control('decision',{'change':{'kind':'initialization','operation':'adopt',
                    'initial_grant_ids':['GR-narrow'],'research_grant_ids':['GR-narrow']}})
            self.assertEqual(initial.instance['grants'],before)

    def test_unique_eligible_grant_within_adoption_and_explicit_denial(self):
        e=self.engine; e.grant('GR-other')
        e.instance['grants']['GR-other']['included_targets']=['different']
        e.instance['lifecycle']['adoption']['research_grant_ids']=['GR-other','GR-research']
        action={'id':'AC-unique','role':'research_preparation'}
        e._action_lifecycle_gate(action)
        self.assertEqual(action['grant_id'],'GR-research')
        with self.assertRaises(ValueError):
            e._action_lifecycle_gate({**action,'grant_id':'GR-other'})

    def prepare_http(self, *, once=False, credentials=False, scope=None, origin='http://127.0.0.1:1'):
        e=self.engine
        grant={'id':'GR-http-audit','kind':'http','reuse':'once' if once else 'reusable',
            'allowed_origins':[origin],'allowed_methods':['POST'],'allowed_path_prefixes':['/effect']}
        if credentials: grant['credential_env']={'X-Test':'LIFECYCLE_AUDIT_TEST_TOKEN'}
        if scope: grant.update(scope)
        e.control('decision',{'change':{'kind':'grant','grant':grant}})
        config={'operation':'prepare','id':'OP-audit','grant_id':grant['id'],
                'request':{'method':'POST','url':origin+'/effect','body':'test'}}
        return config

    def test_scoped_http_control_preserves_exact_envelope(self):
        e=self.engine
        scope={'included_targets':['TARGET'],'purposes':['publish'],'subjects':['publisher'],
               'execution_kinds':['machine']}
        config=self.prepare_http(scope=scope)
        fields={'target_id':'TARGET','purpose':'publish','subject':'publisher',
                'actor_kind':'machine'}
        e.control('external',{**config,**fields})
        op=e.runtime['external_operations'][config['id']]
        self.assertEqual({k:op[k] for k in fields},fields)
        with patch('do_math.external._http',return_value={'http_status':201,'body':b'ok'}) as send:
            e.machine('external_action'); self.assertEqual(send.call_count,1)
        with self.assertRaises(ValueError):
            e.control('external',{**config,**fields,'purpose':'different'})

    def test_once_http_first_send_and_distinct_request(self):
        e=self.engine; config=self.prepare_http(once=True)
        e.control('external',config)
        with patch('do_math.external._http',return_value={'http_status':201,'body':b'ok'}) as send:
            e.machine('external_action'); self.assertEqual(send.call_count,1)
        self.assertEqual(e.runtime['external_operations'][config['id']]['status'],'confirmed')
        with self.assertRaises(ValueError): e.control('external',{**config,'id':'OP-other'})

    def test_once_unknown_send_cannot_be_replayed_without_evidence(self):
        e=self.engine; config=self.prepare_http(once=True)
        e.control('external',config)
        action=next(a for a in e.runtime['queue'] if a['role']=='external_action')
        with patch('do_math.external._http',side_effect=TimeoutError) as send:
            e.machine('external_action'); self.assertEqual(send.call_count,1)
        before=deepcopy(e.runtime['external_operations'][config['id']])
        self.assertEqual(before['status'],'unknown')
        with self.assertRaises(ValueError):
            e.control('external',{'operation':'retry','id':config['id'],'grant_id':config['grant_id']})
        with patch('do_math.external._http') as send:
            e._run_external_action(action); send.assert_not_called()
        self.assertEqual(e.runtime['external_operations'][config['id']]['execution_id'],before['execution_id'])

    def test_academic_control_binds_current_real_prerequisite(self):
        from do_math.academic import current_requirements, solution_basis
        e=self.engine; config=self.prepare_http(scope={'requires_academic':True})
        e._solution_basis=create_autospec(e._solution_basis,side_effect=lambda: solution_basis('synthetic-goal-evidence',
            list(e.instance['formal_results'].values())) if e.instance['goal_status']=='mathematically_solved' else None)
        with self.assertRaises(ValueError): e.control('external',config)
        # Synthetic upstream proof result; actual binding and academic prerequisite consumers.
        e.knowledge('K-academic')
        e.instance['goal_status']='mathematically_solved'
        basis=e._solution_basis(); self.assertIsNotNone(basis)
        e.control('external',config)
        op=e.runtime['external_operations'][config['id']]
        self.assertEqual(op['academic_basis'],{'solution_basis':basis,
            'requirements_sha256':current_requirements(e.instance)['sha256']})
        e.instance['goal_status']='unsolved'
        with patch('do_math.external._http') as send:
            e.machine('external_action'); send.assert_not_called()
        self.assertEqual(e.runtime['external_operations'][config['id']]['status'],'cancelled')

    def test_credential_resume_has_new_attempt_receipt_and_cleared_wait(self):
        import os,time,threading
        from http.server import HTTPServer
        from provider_fixtures import HTTPFixtureHandler
        class Handler(HTTPFixtureHandler):
            count=0
            def do_POST(self):
                Handler.count+=1
                super().do_POST()
        server=HTTPServer(('127.0.0.1',0),Handler)
        threading.Thread(target=server.serve_forever,daemon=True).start()
        self.addCleanup(server.server_close); self.addCleanup(server.shutdown)
        e=self.engine; config=self.prepare_http(credentials=True,origin=f'http://127.0.0.1:{server.server_port}')
        # Real host clock on both registration and completion; no frozen fixture time.
        e.lifecycle_clock=None; e.lifecycle_monotonic=time.monotonic
        e._clock_anchor=None
        e.control('external',config)
        with patch.dict(os.environ), patch('do_math.external._http') as send:
            os.environ.pop('LIFECYCLE_AUDIT_TEST_TOKEN',None)
            e.machine('external_action'); send.assert_not_called()
        before=deepcopy(e.runtime['external_operations'][config['id']])
        first=deepcopy(e.runtime['executions'][before['execution_id']])
        self.assertEqual(first['status'],'ended')
        e.control('external',config)
        with patch.dict(os.environ,{'LIFECYCLE_AUDIT_TEST_TOKEN':'synthetic-local-token'}):
            e.machine('external_action')
        self.assertEqual(Handler.count,1)
        op=e.runtime['external_operations'][config['id']]
        self.assertNotEqual(op['execution_id'],first['id'])
        self.assertEqual(e.runtime['executions'][first['id']],first)
        current=e.runtime['executions'][op['execution_id']]
        self.assertEqual(current['continuation_of'],first['id'])
        self.assertEqual(current['owner_activity_id'],first['owner_activity_id'])
        self.assertEqual(current['outcome'],'output_accepted')
        self.assertEqual(current['submission_receipt']['kind'],'machine_output')
        self.assertNotIn('waiting_reason',op)
        for key in ('id','request_sha256','idempotency_key'):
            self.assertEqual(op[key],before[key])
        for execution in (first,current):
            transitions = execution['transitions']
            # Wall-clock registration and guarded lifecycle samples are diagnostic.
            # The preserved transition sequence records causal state order.
            self.assertEqual(transitions[0]['from'], 'queued')
            self.assertEqual(transitions[-1]['to'], 'ended')
            for previous, following in zip(transitions, transitions[1:]):
                self.assertEqual(previous['to'], following['from'])
            self.assertTrue(all(datetime.fromisoformat(row['at']).utcoffset() == timedelta(0)
                                for row in transitions))
            self.assertEqual(execution['ended_at'], transitions[-1]['at'])


class PersistedConnections(unittest.TestCase):
    def test_new_instance_is_v5_initializing_without_implicit_authority(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            identifier = initialized(root / "repo", goal="Prove the stated goal", workspace=root / "work",
                config={"scholarly_enabled": False, "operator_enabled": False})
            head, instance, runtime = ResearchRepository(root / "repo", identifier).load()
            self.assertEqual(runtime["status"], "initializing")
            self.assertEqual(runtime["queue"], [])
            self.assertEqual(instance["grants"], {})
            profile_id = next(iter(instance["execution_profiles"]))
            found = read_record(root / "repo", instance["id"], profile_id, snapshot=head)
            raw = ResearchRepository(root / "repo", instance["id"]).read(found["path"], head)
            self.assertEqual(found["sha256"], hashlib.sha256(raw).hexdigest())
            self.assertEqual(found["bytes"], len(raw))
            self.assertEqual(found["snapshot"], head)
            engine = ResearchEngine(root / "repo", instance["id"], runner=Mock())
            status = engine.run(max_steps=1)
            self.assertEqual(status["status"], "initializing")
            engine.runner.run.assert_not_called()


if __name__=='__main__': unittest.main()
