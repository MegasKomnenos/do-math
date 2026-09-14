from __future__ import annotations
import hashlib, sys, unittest
from pathlib import Path
SCRIPTS=Path(__file__).resolve().parents[1];sys.path.insert(0,str(SCRIPTS))
from do_math.knowledge import (activate_transition, assess_use, begin_transition, capture_basis,
    invalidate_environment, invalidate_knowledge, record_transition_result, register_environment,
    revise_knowledge, validate_basis)

def item(i,status='verified',deps=None,env='TE-old'):
 return {'id':i,'kind':'theorem','title':i,'statement':'old','explanation':'e','summary':'s','lean_code':'theorem x : True := by trivial','declaration_names':['x'],'dependencies':deps or [],'status':status,'reviews':[{'decision':'match'}],'formal':{'status':'verified','source_sha256':'x','trust_environment_id':env}}
def fixture():
 a=item('KN-A');b=item('KN-B',deps=['KN-A']);c=item('KN-C')
 instance={'knowledge':{'KN-A':a,'KN-B':b,'KN-C':c},'relations':[{'id':'RL-1','source':'KN-A','target':'KN-C','kind':'mentions','evidence':'e','authority':'research'}],
  'goal_judgments':[{'id':'GJ-1','decision':'satisfied','used_sources':['KN-B'],'current':True}],
  'trust_environments':{'TE-old':{'id':'TE-old','status':'active'}},'active_trust_environment':'TE-old'}
 runtime={'tasks':{'TK-1':{'id':'TK-1','status':'completed','inputs':['KN-B'],'reuse':[],'results':[],'assessment':{'decision':'completed','current':True}},'TK-2':{'id':'TK-2','status':'completed','inputs':['KN-C'],'reuse':[],'results':[]}},'queue':[],'history':[]}
 return instance,runtime

class KnowledgeTests(unittest.TestCase):
 def test_revision_preserves_history_and_propagates_only_actual_dependencies(self):
  ins,run=fixture();new,nrun=revise_knowledge(ins,run,'KN-A',{'statement':'new'},reason='correction',actor_ref='human:x')
  self.assertEqual(new['knowledge']['KN-A']['revision'],2);self.assertEqual(new['knowledge']['KN-A']['status'],'candidate');self.assertEqual(new['knowledge']['KN-A']['formal'],{});self.assertEqual(new['knowledge']['KN-A']['reviews'],[])
  self.assertEqual(new['knowledge']['KN-A']['history'][-1]['previous']['statement'],'old');self.assertTrue(new['knowledge']['KN-B']['use_suspended']);self.assertNotIn('use_suspended',new['knowledge']['KN-C'])
  self.assertEqual(nrun['tasks']['TK-1']['status'],'waiting');self.assertEqual(nrun['tasks']['TK-2']['status'],'completed');self.assertFalse(nrun['tasks']['TK-1']['assessment']['current']);self.assertFalse(new['goal_judgments'][0]['current']);self.assertTrue(nrun['queue'])
  self.assertEqual(ins['knowledge']['KN-A']['statement'],'old')
 def test_task_dependencies_are_strong_reassessment_edges(self):
  ins,run=fixture();run['tasks']['TK-3']={'id':'TK-3','status':'completed','dependencies':['KN-B'],'inputs':[],'reuse':[],'results':[],'assessment':{'decision':'completed','current':True}}
  new,nrun=revise_knowledge(ins,run,'KN-A',{'statement':'new'},reason='dependency changed',actor_ref='human:x')
  self.assertTrue(new['knowledge']['KN-B']['use_suspended']);self.assertEqual(nrun['tasks']['TK-3']['status'],'waiting');self.assertFalse(nrun['tasks']['TK-3']['assessment']['current'])
 def test_invalidation_withdraws_without_deleting_and_relation_neighbor_is_preserved(self):
  ins,run=fixture();new,nrun=invalidate_knowledge(ins,run,'KN-A',reason='false',actor_ref='review:1')
  self.assertIn('KN-A',new['knowledge']);self.assertEqual(new['knowledge']['KN-A']['status'],'withdrawn');self.assertEqual(new['knowledge']['KN-C']['status'],'verified');self.assertEqual(nrun['tasks']['TK-2']['status'],'completed')
 def test_basis_hash_detects_change_and_assess_use(self):
  ins,run=fixture();basis=capture_basis(ins,run,['KN-A','TK-1']);self.assertTrue(validate_basis(basis,ins,run)['valid'])
  ins['knowledge']['KN-A']['summary']='changed';result=validate_basis(basis,ins,run);self.assertFalse(result['valid']);self.assertIn('hash_changed:KN-A',result['reasons'])
  self.assertTrue(assess_use(fixture()[0]['knowledge']['KN-B'],fixture()[0])['valid'])
 def test_source_coordinates_are_not_missing_knowledge_but_real_ids_are(self):
  ins,_=fixture();review={'status':'verified','used_sources':['proposal:1','input/knowledge/KN-X.json',{'path':'input/catalog/sources.json','sha256':'0','bytes':1}]}
  self.assertTrue(assess_use(review,ins)['valid'])
  review['used_sources'].append('KN-MISSING');result=assess_use(review,ins);self.assertFalse(result['valid']);self.assertIn('missing_dependency:KN-MISSING',result['reasons'])
  self.assertFalse(assess_use({'status':'verified','dependencies':['not-present']},ins)['valid'])
 def test_known_used_source_propagates_but_source_locator_does_not(self):
  ins,run=fixture();ins['knowledge']['KN-B']['dependencies']=[];ins['knowledge']['KN-B']['reviews']=[{'used_sources':['proposal:1','input/knowledge/KN-X.json','KN-A']}]
  new,_=revise_knowledge(ins,run,'KN-A',{'summary':'changed'},reason='r',actor_ref='a');self.assertTrue(new['knowledge']['KN-B']['use_suspended']);self.assertNotIn('use_suspended',new['knowledge']['KN-C'])
 def test_transition_partial_failure_keeps_old_environment(self):
  ins,_=fixture();ins,new_id=register_environment(ins,{'executable':'lean-new','sha256':'a'},['propext']);tr=begin_transition(ins,new_id)
  first=tr['targets'][0];tr=record_transition_result(ins,tr,{'id':first['id'],'status':'failed','source_sha256':first['source_sha256']})
  with self.assertRaises(ValueError):activate_transition(ins,tr)
  self.assertEqual(ins['active_trust_environment'],'TE-old')
 def test_unknown_environment_rejected(self):
  ins,run=fixture()
  with self.assertRaises(ValueError):begin_transition(ins,'TE-missing')
  with self.assertRaises(ValueError):invalidate_environment(ins,run,'TE-missing','bad')
 def test_complete_transition_requires_all_and_updates_environment(self):
  ins,_=fixture();ins,new_id=register_environment(ins,{'executable':'lean-new','sha256':'a'},['propext']);tr=begin_transition(ins,new_id)
  for index,target in enumerate(tr['targets']):
   result={'status':'verified','source_sha256':target['source_sha256'],'axioms':[]}
   tr=record_transition_result(ins,tr,{target['id']:result} if index==0 else {'id':target['id'],**result})
  activated=activate_transition(ins,tr);self.assertEqual(activated['active_trust_environment'],new_id);self.assertEqual(activated['trust_environments']['TE-old']['status'],'superseded')
  self.assertTrue(all(x['formal']['trust_environment_id']==new_id for x in activated['knowledge'].values()))
 def test_environment_invalidation_propagates_only_affected_records(self):
  ins,run=fixture();ins['knowledge']['KN-C']['formal']['trust_environment_id']='TE-other';ins['trust_environments']['TE-other']={'id':'TE-other','status':'registered'}
  new,nrun=invalidate_environment(ins,run,'TE-old','toolchain defect');self.assertTrue(new['knowledge']['KN-A']['use_suspended']);self.assertTrue(new['knowledge']['KN-B']['use_suspended']);self.assertNotIn('use_suspended',new['knowledge']['KN-C']);self.assertEqual(nrun['tasks']['TK-2']['status'],'completed')
 def test_invalidated_active_environment_can_transition_and_recover_all_verified_k(self):
  ins,run=fixture();stopped,_=invalidate_environment(ins,run,'TE-old','kernel defect');self.assertIsNone(stopped['active_trust_environment'])
  stopped,new_id=register_environment(stopped,{'executable':'lean-fixed','sha256':'b'},['propext']);tr=begin_transition(stopped,new_id)
  self.assertEqual({x['id'] for x in tr['targets']},{'KN-A','KN-B','KN-C'});self.assertTrue(all(x['previous_environment_ids']==['TE-old'] for x in tr['targets']))
  first=tr['targets'][0];partial=record_transition_result(stopped,tr,{'id':first['id'],'status':'failed','source_sha256':first['source_sha256']})
  with self.assertRaises(ValueError):activate_transition(stopped,partial)
  self.assertIsNone(stopped['active_trust_environment']);self.assertTrue(all(x['use_suspended'] for x in stopped['knowledge'].values()))
  for target in tr['targets']:
   tr=record_transition_result(stopped,tr,{'id':target['id'],'status':'verified','source_sha256':target['source_sha256'],'axioms':[]})
  recovered=activate_transition(stopped,tr);self.assertEqual(recovered['active_trust_environment'],new_id);self.assertEqual(recovered['trust_environments']['TE-old']['status'],'invalid')
  for record in recovered['knowledge'].values():
   self.assertFalse(record['use_suspended']);self.assertEqual(record['formal']['previous_environment_ids'],['TE-old']);self.assertTrue(record['use_history'][-1]['reasons'])
 def test_recovery_transition_does_not_promote_candidate_or_withdrawn(self):
  ins,run=fixture();stopped,_=invalidate_environment(ins,run,'TE-old','bad');stopped['knowledge']['KN-B']['status']='candidate';stopped['knowledge']['KN-C']['status']='withdrawn'
  stopped,new_id=register_environment(stopped,{'executable':'lean-fixed'},[]);tr=begin_transition(stopped,new_id);self.assertEqual([x['id'] for x in tr['targets']],['KN-A'])
  target=tr['targets'][0];tr=record_transition_result(stopped,tr,{'id':'KN-A','status':'verified','source_sha256':target['source_sha256']});recovered=activate_transition(stopped,tr)
  self.assertEqual(recovered['knowledge']['KN-B']['status'],'candidate');self.assertTrue(recovered['knowledge']['KN-B']['use_suspended']);self.assertEqual(recovered['knowledge']['KN-C']['status'],'withdrawn')
 def test_environment_recovery_preserves_independent_semantic_suspension(self):
  ins,run=fixture();stopped,_=invalidate_environment(ins,run,'TE-old','environment bad');record=stopped['knowledge']['KN-A'];record['use_suspensions'].append({'kind':'semantic','root_ids':['KN-A'],'reason':'meaning challenged'});record['use_suspension_reasons'].append('meaning challenged')
  stopped,new_id=register_environment(stopped,{'executable':'fixed'},[]);tr=begin_transition(stopped,new_id)
  for target in tr['targets']:tr=record_transition_result(stopped,tr,{'id':target['id'],'status':'verified','source_sha256':target['source_sha256']})
  recovered=activate_transition(stopped,tr);self.assertTrue(recovered['knowledge']['KN-A']['use_suspended']);self.assertEqual(recovered['knowledge']['KN-A']['use_suspensions'],[{'kind':'semantic','root_ids':['KN-A'],'reason':'meaning challenged'}]);self.assertFalse(recovered['knowledge']['KN-C']['use_suspended'])
 def test_environment_recovery_preserves_dependency_on_invalid_knowledge(self):
  ins,run=fixture();withdrawn,run=invalidate_knowledge(ins,run,'KN-A',reason='false theorem',actor_ref='review')
  stopped,_=invalidate_environment(withdrawn,run,'TE-old','environment bad');self.assertEqual({x['kind'] for x in stopped['knowledge']['KN-B']['use_suspensions']},{'dependency','environment'})
  stopped,new_id=register_environment(stopped,{'executable':'fixed'},[]);tr=begin_transition(stopped,new_id)
  for target in tr['targets']:tr=record_transition_result(stopped,tr,{'id':target['id'],'status':'verified','source_sha256':target['source_sha256']})
  recovered=activate_transition(stopped,tr);self.assertTrue(recovered['knowledge']['KN-B']['use_suspended']);self.assertEqual(recovered['knowledge']['KN-B']['use_suspensions'][0]['kind'],'dependency');self.assertEqual(recovered['knowledge']['KN-A']['status'],'withdrawn')
if __name__=='__main__':unittest.main(verbosity=2)
