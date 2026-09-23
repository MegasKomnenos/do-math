"""Feature-five condition and planning regressions; no persisted-ready fixtures."""
from copy import deepcopy
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from do_math import planning
from test_redesign_TASKS import approved_fixture, approve


class PlanningTests(unittest.TestCase):
    def setUp(self):
        self.task,self.instance,self.runtime=approved_fixture()
        self.instance['knowledge']={'K':{'id':'K','lifecycle':'active','value':1}}

    def condition(self,op='record_exists',**changes):
        return dict(op=op,space='research',family='knowledge',record_id='K',**changes)

    def test_conditions_and_errors_preserve_basis(self):
        condition={'op':'all','args':[self.condition(),self.condition('record_field_equals',pointer='/value',value=1)]}
        before=deepcopy(self.instance)
        result=planning.evaluate_condition(condition,self.instance,self.runtime)
        self.assertEqual(result['state'],'ready');self.assertEqual(len(result['basis']),2)
        self.assertEqual(before,self.instance)
        self.instance['knowledge']['K']['value']=True
        self.assertEqual(planning.evaluate_condition(condition,self.instance,self.runtime)['state'],'not_ready')
        changed=planning.evaluate_condition(self.condition(),self.instance,self.runtime)
        self.assertNotEqual(changed['basis'][0]['sha256'],result['basis'][0]['sha256'])
        for invalid in [{'op':'unknown'},self.condition('record_field_equals',pointer='/question',value=1),
                        {'op':'any','args':[{'op':'always'},{'op':'unknown'}]}]:
            self.assertEqual(planning.evaluate_condition(invalid,self.instance,self.runtime)['state'],'evaluation_error')
        self.instance['knowledge'].clear()
        result=planning.evaluate_condition(self.condition(),self.instance,self.runtime)
        self.assertEqual(result['state'],'not_ready');self.assertIn('absencequery',result['basis'][0])

    def test_task_ready_rechecks_reviews_inputs_and_conditions(self):
        self.assertEqual(planning.task_ready(self.task,self.instance,self.runtime)['state'],'ready')
        self.task['reviews'][0]['revision']=2
        self.assertEqual(planning.task_ready(self.task,self.instance,self.runtime)['state'],'not_ready')
        self.task['occurrence_condition']=self.condition('record_lifecycle_is',value='withdrawn')
        approve(self.task,self.instance,self.runtime)
        self.assertEqual(planning.task_ready(self.task,self.instance,self.runtime)['state'],'not_ready')

    def test_contract_hash_only_changes_for_contract_fields(self):
        baseline=planning.contract_hash(self.task)
        self.task.update(status='waiting',waiting={'kind':'external_event'},history=['bookkeeping'])
        self.assertEqual(planning.contract_hash(self.task),baseline)
        self.task['question']='changed'
        self.assertNotEqual(planning.contract_hash(self.task),baseline)

    def test_due_events_are_unique_and_paused_preserves_pending(self):
        self.runtime['next_research_reconsider_at']='2026-01-01T00:00:00Z'
        self.task.update(wake_at='2026-01-01T00:00:00Z',due_conditions=[{'op':'always'}],newinput=True)
        events=planning.collect_due_events(self.instance,self.runtime,'2026-01-02T00:00:00Z')
        self.assertEqual(sorted(e['kind'] for e in events),['research_reconsider_due','task_condition_due','task_new_input','task_wake_due'])
        self.assertEqual(len(events),len({e['id'] for e in events}))
        self.runtime['status']='paused'
        result=planning.apply_event_schedule(self.instance,self.runtime,'2026-01-02T00:00:00Z')
        self.assertTrue(result['runtime']['pending_events'])
        self.assertFalse(planning.apply_event_schedule(result['instance'],result['runtime'],'2026-01-02T00:00:00Z')['events'])

    def test_source_arrival_and_trust_transition_are_machine_conditions(self):
        condition={'op':'all','args':[
            {'op':'record_exists','space':'research','family':'source','record_id':'SO-new'},
            {'op':'record_lifecycle_is','space':'research','family':'trust-environment','record_id':'TE-1','value':'active'}]}
        self.assertEqual(planning.evaluate_condition(condition,self.instance,self.runtime)['state'],'not_ready')
        self.instance['sources'].append({'id':'SO-new','sha256':'a'*64})
        self.instance['trust_environments']={'TE-1':{'id':'TE-1','status':'active'}}
        self.assertEqual(planning.evaluate_condition(condition,self.instance,self.runtime)['state'],'ready')
        self.instance['trust_environments']['TE-1']['status']='invalid'
        self.assertEqual(planning.evaluate_condition(condition,self.instance,self.runtime)['state'],'not_ready')

    def test_relation_condition_rechecks_its_proof_after_import(self):
        from do_math import knowledge_io
        from test_redesign_KNOWLEDGE import KnowledgeRedesign
        from do_math import knowledge_records as kr
        i,r,kid,aid=KnowledgeRedesign().verified()
        template=next(t for t in knowledge_io.relation_templates() if t['token']=='formally_implies')
        i,_=knowledge_io.register_kind_definition(i,template,source_ref='source',actor_ref='producer')
        i=knowledge_io.check_kind_definition(i,'relation','formally_implies',check_ref='check',actor_ref='reviewer')
        i=knowledge_io.activate_kind_definition(i,'relation','formally_implies',approval_ref='approved',actor_ref='reviewer')
        fid=i['knowledge'][kid]['formal_result_id'];xid=i['knowledge'][kid]['exposition_id']
        claim={'kind':'formally_implies','source':kid,'target':kid,'confirmed_scope':'True implies True'}
        i['expositions'][xid]['relation_claim']=claim
        i,aid=kr.record_identity_assessment(i,kid,{'decision':'match','basis':kr.identity_basis(i,kid),'cycle_id':'RC-relation'},'policy:1',runtime=r)
        relation={'id':'RL-1','kind':'formally_implies','source':kid,'target':kid,
            'confirmed_scope':'True implies True','evidence':'reflexivity',
            'formal_result_refs':[fid],'assessment_refs':[aid]}
        i['relations']=[relation]
        condition={'op':'relation_exists','subkind':'formally_implies','from_id':kid,'to_id':kid}
        actual=planning.evaluate_condition(condition,i,r)
        self.assertEqual(actual['state'],'ready',actual)
        i['formal_results'][fid]['formal_use']='suspended'
        self.assertNotEqual(planning.evaluate_condition(condition,i,r)['state'],'ready')

    def test_cited_task_basis_ignores_lifecycle_and_appended_results_but_not_contract_rewrites(self):
        t=self.task;t['results']=[{'execution_id':'EX-1','summary':'first'}]
        basis=[planning.task_reference_basis(t)];tasks={t['id']:deepcopy(t)}
        tasks[t['id']].update(status='active',selected_by='EX-2',reviews=[])
        tasks[t['id']]['results'].append({'execution_id':'EX-3','summary':'later'})
        self.assertEqual(planning.task_reference_changes(basis,tasks),[])
        tasks[t['id']]['scope']['included'].append('new');tasks[t['id']]['results'][0]['summary']='rewritten'
        self.assertEqual(planning.task_reference_changes(basis,tasks),['contract_changed:TK-1','results_changed:TK-1'])
        self.assertEqual(planning.task_reference_changes(basis,{}),['missing:TK-1'])


if __name__=='__main__':unittest.main(verbosity=2)
