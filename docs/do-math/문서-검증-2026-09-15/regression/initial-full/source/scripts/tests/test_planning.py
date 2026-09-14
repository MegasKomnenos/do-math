from __future__ import annotations
import copy,sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from do_math.planning import apply_event_schedule, collect_due_events, contract_hash, evaluate_condition, task_ready

class PlanningTests(unittest.TestCase):
 def setUp(self):
  self.instance={'knowledge':{'K':{'id':'K','status':'active','value':1}},'relations':[{'id':'R','kind':'supports','source':'K','target':'F'}],'sources':[{'name':'src','path':'p'}],'goal_status':'unresolved'}
  self.runtime={'tasks':{'T':{'id':'T','status':'planned','revision':1,'reviews':[{'id':'RV','revision':1,'decision':'approved'}],'inputs':['K','src'],'dependencies':[]}},'activities':{},'executions':{},'events':[],'next_research_reconsider_at':'2026-01-01T00:00:00Z'}
 def test_conditions_and_errors_preserve_basis(self):
  x=evaluate_condition({'op':'all','args':[{'op':'record_exists','record_id':'K','family':'knowledge'},{'op':'record_field_equals','record_id':'K','pointer':'/value','value':1}]},self.instance,self.runtime); self.assertEqual(x['state'],'ready'); self.assertEqual(len(x['basis']),2)
  old=x['basis'][0]['sha256']; self.instance['knowledge']['K']['value']=2; changed=evaluate_condition({'op':'record_exists','record_id':'K','family':'knowledge'},self.instance,self.runtime); self.assertNotEqual(old,changed['basis'][0]['sha256']); self.instance['knowledge']['K']['value']=1
  self.assertEqual(evaluate_condition({'op':'unknown','record_id':'none'},self.instance,self.runtime)['state'],'evaluation_error')
  self.assertEqual(evaluate_condition({'op':'record_field_equals','record_id':'K','pointer':'/question','value':1},self.instance,self.runtime)['state'],'evaluation_error')
  self.instance['knowledge']['K']['value']=True; self.assertEqual(evaluate_condition({'op':'record_field_equals','record_id':'K','pointer':'/value','value':1},self.instance,self.runtime)['state'],'not_ready'); self.instance['knowledge']['K']['value']=1
  self.assertEqual(evaluate_condition({'op':'record_exists','record_id':'none','family':'knowledge'},self.instance,self.runtime)['state'],'not_ready')
  before=copy.deepcopy(self.instance);evaluate_condition({'op':'record_field_equals','record_id':'K','pointer':'/value','value':1},self.instance,self.runtime);self.assertEqual(self.instance,before)
 def test_task_ready_rechecks_reviews_inputs_and_conditions(self):
  self.assertEqual(task_ready(self.runtime['tasks']['T'],self.instance,self.runtime)['state'],'ready')
  self.runtime['tasks']['T']['reviews'][0]['revision']=2; self.assertEqual(task_ready(self.runtime['tasks']['T'],self.instance,self.runtime)['state'],'not_ready')
  self.runtime['tasks']['T']['reviews'][0]['revision']=1; self.runtime['tasks']['T']['occurrence_condition']={'op':'record_lifecycle_is','record_id':'K','value':'withdrawn'}; self.assertEqual(task_ready(self.runtime['tasks']['T'],self.instance,self.runtime)['state'],'not_ready')
 def test_contract_hash_only_changes_for_contract_fields(self):
  task={'id':'T','revision':1,'title':'t','question':'q','scope':'s','expected_result':'r','completion_criteria':['c'],'inputs':['i'],'reuse':[],'dependencies':[],'occurrence_condition':{'op':'always'},'work_class':'nonformal','profile_refs':['p'],'status':'ready','reviews':[],'history':['x']}
  baseline=contract_hash(task);task['status']='waiting';task['history'].append('y');task['readiness']={'state':'ready'};self.assertEqual(contract_hash(task),baseline)
  task['question']='changed';self.assertNotEqual(contract_hash(task),baseline)
 def test_due_events_are_unique_and_paused_preserves_pending(self):
  self.runtime['tasks']['T'].update(wake_at='2026-01-01T00:00:00Z',due_conditions=[{'op':'always'}],newinput=True)
  events=collect_due_events(self.instance,self.runtime,'2026-01-02T00:00:00Z'); self.assertGreaterEqual(len(events),3)
  self.runtime['status']='paused'; applied=apply_event_schedule(self.instance,self.runtime,'2026-01-02T00:00:00Z'); self.assertTrue(applied['runtime'].get('pending_events',[]))
  again=apply_event_schedule(applied['instance'],applied['runtime'],'2026-01-02T00:00:00Z'); self.assertEqual(again['events'],[])
 def test_source_arrival_and_trust_transition_are_machine_conditions(self):
  condition={'op':'all','args':[{'op':'record_exists','record_id':'SO-1','family':'source'},{'op':'record_lifecycle_is','record_id':'TE-1','value':'active'}]}
  self.assertEqual(evaluate_condition(condition,self.instance,self.runtime)['state'],'not_ready')
  self.instance['sources'].append({'id':'SO-1','name':'new','path':'artifact','sha256':'a'*64,'status':'active'})
  self.instance['trust_environments']={'TE-1':{'id':'TE-1','status':'active'}}
  self.assertEqual(evaluate_condition(condition,self.instance,self.runtime)['state'],'ready')
  self.instance['trust_environments']['TE-1']['status']='invalid'
  self.assertEqual(evaluate_condition(condition,self.instance,self.runtime)['state'],'not_ready')
if __name__=='__main__': unittest.main()
