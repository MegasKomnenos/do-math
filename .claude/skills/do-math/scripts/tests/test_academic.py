from __future__ import annotations
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from do_math.academic import *
class Tests(unittest.TestCase):
 def setUp(self):
  self.i={'goal_status':'mathematically_solved'};self.i=set_requirements(self.i,[{'id':'paper','scope':'solution','criteria':['draft'],'assessor':'research_plan'}]);self.b=solution_basis('goal',[{'id':'K','v':1}]);self.r={'tasks':{},'academic_assessments':[],'external_rejections':[]}
 def test_pending_completed_and_requirement_change(self):
  self.assertEqual(academic_status(self.i,self.r,self.b)['status'],'pending');self.r['academic_assessments']=[assess('paper',self.b,self.i['academic_requirements'],'satisfied',[{'criterion':'draft','satisfied':True,'evidence':'e'}])];self.assertEqual(academic_status(self.i,self.r,self.b)['status'],'completed')
  changed=set_requirements(self.i,[{'id':'paper','scope':'solution','criteria':['publish'],'assessor':'research_plan'}]);self.assertTrue(requirements_changed(self.i,changed));self.assertEqual(academic_status(changed,self.r,self.b)['status'],'pending')
 def test_rejection_and_resolution(self):
  self.r['external_rejections']=[{'id':'RJ','solution_basis':self.b,'resolved':False,'source_ref':'planner-evidence'}]
  self.assertEqual(academic_status(self.i,self.r,self.b)['status'],'externally_rejected')
  self.r['external_rejections'][0].update(resolved=True,resolution_evidence=['planner-assessment'])
  self.assertEqual(academic_status(self.i,self.r,self.b)['status'],'externally_rejected')
  self.r['executions']={'E':{'role':'research_plan','input_solution_basis':self.b}}
  self.r['artifacts']={'EV':{'text':'Planner evidence'}}
  record_resolution(self.i,self.r,self.b,{'id':'RJ','decision':'resolved','evidence':'Addresses objection','evidence_refs':['EV']},execution_id='E')
  self.assertEqual(academic_status(self.i,self.r,self.b)['status'],'pending')
 def test_invalid_requirement_shape_is_rejected(self):
  with self.assertRaises(ValueError):set_requirements({},[{'id':'x'}])
  with self.assertRaises(ValueError):set_requirements({},[{'id':'x','scope':'s','criteria':[],'assessor':'other'}])
 def test_unsolved_not_applicable(self):
  self.i['goal_status']='unresolved';self.assertEqual(academic_status(self.i,self.r,self.b)['status'],'not_applicable')
 def test_normalizes_inputs_effects_and_rechecks_actual_confirmed_receipt(self):
  self.i=set_requirements({'goal_status':'mathematically_solved'},[{'id':'publish','scope':'solution','criteria':['send'],
   'assessor':'research_plan','required_inputs':['context:goal'],'external_effects':[{'id':'submit','scope':'send manuscript','grant_id':'G'}]}])
  req=self.i['academic_requirements']['items'][0]
  self.assertEqual(req['required_inputs'],['context:goal']);self.assertEqual(req['external_effects'],[{'id':'submit','scope':'send manuscript','grant_id':'G'}])
  assessment=assess('publish',self.b,self.i['academic_requirements'],'satisfied',[{'criterion':'send','satisfied':True,'evidence':'receipt'}]);assessment['task_id']='T';self.r['academic_assessments']=[assessment]
  self.assertEqual(academic_status(self.i,self.r,self.b)['status'],'pending')
  binding={'task_id':'T','requirement_id':'publish','requirements_sha256':self.i['academic_requirements']['sha256'],'solution_basis':self.b,'effect_id':'submit'}
  self.r['external_operations']={'OP':{'id':'OP','status':'confirmed','succeeded':True,'grant_id':'G','request_sha256':'r','academic_binding':binding}}
  self.assertEqual(academic_status(self.i,self.r,self.b)['status'],'completed')
  self.r['external_operations']['OP']['succeeded']=False;self.assertEqual(academic_status(self.i,self.r,self.b)['status'],'pending')
 def test_bad_effect_or_input_shape_is_rejected(self):
  with self.assertRaises(ValueError):set_requirements({},[{'id':'x','scope':'s','criteria':['c'],'assessor':'research_plan','required_inputs':['x','x']}])
  with self.assertRaises(ValueError):set_requirements({},[{'id':'x','scope':'s','criteria':['c'],'assessor':'research_plan','external_effects':[{'id':'e','scope':'x'},{'id':'e','scope':'y'}]}])
if __name__=='__main__':unittest.main()
