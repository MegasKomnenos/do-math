from pathlib import Path
import hashlib
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from do_math import governance as gov
from do_math.initialization import initial_intent_evidence
from research_fixtures import git_init
from record_fixtures import applied_initial_intent


class InitialIntentConnectionTests(unittest.TestCase):
    def test_public_initialization_stores_exact_text_and_source_filename(self):
        from do_math.repository import ResearchRepository
        from research_fixtures import new_instance
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary)
            text='e\u0301 and \u212a are exact source text'
            source=root/'e\u0301.txt'
            source.write_bytes(text.encode())
            instance_id=new_instance(root/'repo',goal=text,workspace=root/'work',sources=[source],
                config={'scholarly_enabled':False,'operator_enabled':False})
            store=ResearchRepository(root/'repo',instance_id)
            head,instance,_=store.load()
            self.assertEqual(instance['lifecycle']['immutable_input']['text'],text)
            preserved=instance['sources'][0]
            self.assertEqual(preserved['name'],source.name)
            self.assertIn(source.name,preserved['path'])
            self.assertEqual(store.read(preserved['path'],head),source.read_bytes())

    def test_applied_import_uses_original_input_reference_and_exact_bytes(self):
        for text in ['A mathematical goal','e\u0301 and \u212a are exact source text']:
            with self.subTest(text=text):
                instance,runtime,_=applied_initial_intent(text)
                evidence=initial_intent_evidence(instance,runtime)
                self.assertEqual(evidence,{'input_sha256':hashlib.sha256(text.encode()).hexdigest(),
                    'interpretation_execution_id':'EX-author','check_execution_id':'EX-check'})

    def test_changed_input_or_unapplied_result_cannot_complete_initialization(self):
        instance,runtime,bid=applied_initial_intent('A mathematical goal')
        runtime['intent_imports'][bid].pop('application')
        with self.assertRaises(ValueError): initial_intent_evidence(instance,runtime)
        instance,runtime,bid=applied_initial_intent('A mathematical goal')
        runtime['intent_imports'][bid]['input_ref']='UI-other'
        with self.assertRaises(ValueError): initial_intent_evidence(instance,runtime)

    def test_initial_grants_wait_for_activation_to_open_research(self):
        instance,runtime,_=applied_initial_intent('A mathematical goal')
        instance,runtime,_=gov.apply_decision(instance,runtime,{'kind':'grant','grant':{
            'id':'GR-work','kind':'local','roles':['research_work'],'reuse':'reusable'}},source_ref='GS-adoption')
        self.assertEqual(runtime['queue'],[])
        self.assertEqual(instance['grants']['GR-work']['status'],'active')

    def test_grant_change_is_plan_basis_and_not_the_plan_execution_authority(self):
        instance,runtime,_=applied_initial_intent('A mathematical goal')
        instance['lifecycle']['state']='active'
        instance,runtime,_=gov.apply_decision(instance,runtime,{'kind':'grant','grant':{
            'id':'GR-plan','kind':'local','roles':['research_plan'],'reuse':'reusable'}},source_ref='GS-adoption')
        runtime['queue']=[]
        instance,runtime,event=gov.apply_decision(instance,runtime,{'kind':'grant','grant':{
            'id':'GR-work','kind':'local','roles':['research_work'],'reuse':'reusable'}},source_ref='GS-adoption')
        self.assertEqual(len(runtime['queue']),1)
        action=runtime['queue'][0]
        authorization=gov.authorize(instance,action,runtime=runtime)
        self.assertTrue(authorization['allowed'],authorization)
        self.assertEqual(authorization['grant_id'],'GR-plan')
        self.assertEqual(action['decision_id'],event['id'])


class InitialFailureRetryTests(unittest.TestCase):
    def test_public_retry_preserves_original_input_and_ended_predecessor(self):
        from copy import deepcopy
        import json
        from unittest.mock import patch
        from do_math.engine import ResearchEngine, control
        from do_math.repository import ResearchRepository, new_id
        from do_math import execution_profiles as profiles
        from engine_fixtures import FakeEngine, PublicInitializationRunner
        from research_fixtures import charter_record, install_adapter_fixture
        install_adapter_fixture(self)
        from do_math.initialization import adapter_for
        class FailingRunner:
            def run(self, **arguments):
                raise ValueError('synthetic pre-start binding failure')
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory); workspace=root/'work'; workspace.mkdir()
            repo=root/'repo'; git_init(repo)
            seed=FakeEngine(workspace, {'scholarly_enabled':False, 'operator_enabled':False,
                'tool_review_window_seconds':60, 'self_check_response_window_seconds':5,
                })
            seed.grant('GR-init',True); seed.grant('GR-research')
            seed.control('decision',{'change':{'kind':'initialization','operation':'governance',
                'records':[charter_record(seed.instance['lifecycle']['immutable_input']['text'])]}})
            for profile in seed.instance['execution_profiles'].values():
                if profile['actor_kind']=='ai':
                    evidence=profiles.capability_evidence(profile,adapter_for(profile).describe(),
                        observed_at=seed.current_time.isoformat())
                    seed.instance.setdefault('capability_evidence',{})[evidence['id']]=evidence
            from do_math.model_policy import selection
            initial=selection(seed.instance['config'],{'role':'intent_interpretation'}, {},{},
                instance=seed.instance)['profile_ref']
            seed.control('decision',{'change':{'kind':'initialization','adopt_current_config':True,
                'adopt_current_governance':True,'conversation_loss_policy':'continue_authorized',
                'external_policy':'disabled','adopt_default_review_policy':True,
                'profile_refs':[profiles.profile_ref(p) for p in seed.instance['execution_profiles'].values()],
                'initial_profile_ref':initial,'initial_grant_ids':['GR-init'],'research_grant_ids':['GR-research']}})
            seed.runtime.update(processed_controls=[],reservations={},provider_waits={},
                updated_at=seed.runtime['last_observed_utc'])
            identifier=new_id('RI')
            instance=json.loads(json.dumps(seed.instance).replace('RI-test',identifier))
            runtime=json.loads(json.dumps(seed.runtime).replace('RI-test',identifier))
            ResearchRepository(repo,identifier).initialize(instance,runtime)
            engine=ResearchEngine(repo,identifier,runner=FailingRunner())
            original=deepcopy(engine.instance['lifecycle']['immutable_input'])
            engine.run(max_steps=1)
            self.assertTrue(any(h['kind']=='execution_failure' for h in engine.runtime['waiting_actions'].values()),
                {k:engine.runtime.get(k) for k in ('status','queue','waiting_actions','history','executions')})
            aid,held=next((a,h) for a,h in engine.runtime['waiting_actions'].items()
                          if h['kind']=='execution_failure')
            predecessor=deepcopy(engine.runtime['executions'][held['execution_id']])
            self.assertEqual(predecessor['status'],'ended')
            self.assertIsNone(predecessor.get('started_at'))
            failure_state=deepcopy(engine.runtime)
            for change in ('live','source','grant','termination'):
                with self.subTest(rejected=change):
                    engine.runtime=deepcopy(failure_state)
                    saved_instance=deepcopy(engine.instance)
                    if change=='live':
                        engine.runtime['executions'][predecessor['id']]['status']='running'
                    elif change=='source':
                        engine.runtime['waiting_actions'][aid]['action']['target']='UI-other'
                    elif change=='grant':
                        engine.instance['grants']['GR-init']['status']='revoked'
                    else:
                        # Only SessionSlots.release confirms local termination, and it settles the
                        # execution's reservations first; unconfirmed termination still holds them.
                        engine.runtime['executions'][predecessor['id']]['capacity']['local_termination']='unknown'
                    with self.assertRaises(ValueError):
                        engine._retry_input_overflow_action({'id':'UC-negative','config':{'retry_action':aid}})
                    self.assertIn(aid,engine.runtime['waiting_actions'])
                    engine.instance=saved_instance
            engine.runtime=deepcopy(failure_state)
            request=control(repo,identifier,'request',config={'retry_action':aid},request_id='UC-initial-retry')
            self.assertTrue(request['accepted'])
            restarted=ResearchEngine(repo,identifier,runner=PublicInitializationRunner())
            restarted.process_controls()
            self.assertNotIn(aid,restarted.runtime['waiting_actions'],restarted.runtime['history'][-3:])
            retry=next(a for a in restarted.runtime['queue'] if a['id']==aid)
            self.assertEqual(retry['continuation_of'],predecessor['id'])
            self.assertEqual(restarted.runtime['executions'][predecessor['id']],predecessor)
            self.assertFalse(any(a['role']=='operational_review' and a.get('target')==predecessor['id']
                                 for a in restarted.runtime['queue']))
            with patch('do_math.windows_job.named_job_empty',return_value=True):
                restarted.run(max_steps=1)
            successor=next(e for e in restarted.runtime['executions'].values()
                           if e.get('continuation_of')==predecessor['id'])
            self.assertEqual(successor['outcome'],'output_accepted',successor)
            self.assertEqual(successor['owner_activity_id'],predecessor['owner_activity_id'])
            self.assertTrue(restarted.runtime['intent_imports'])
            self.assertEqual(restarted.instance['lifecycle']['immutable_input'],original)

if __name__=='__main__': unittest.main()
