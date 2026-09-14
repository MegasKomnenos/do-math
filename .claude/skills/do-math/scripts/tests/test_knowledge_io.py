from __future__ import annotations
import sys, unittest
from pathlib import Path
SCRIPTS=Path(__file__).resolve().parents[1];sys.path.insert(0,str(SCRIPTS))
from do_math.knowledge_io import (catalog_definitions, import_candidate, import_relation,
    register_kind_definition, validate_relation)
from do_math.knowledge import capture_basis

def roots():
 return {'config':{'reviewers':2},'knowledge':{},'relations':[],'sources':[{'id':'SO-1','name':'source.txt','sha256':'a'}]}, {'queue':[],'history':[]}
def candidate(kind='theorem',identity=None):
 value={'kind':kind,'title':'T','statement':'P','explanation':'Explanation','summary':'Summary','lean_code':'theorem t : True := by trivial','declaration_names':['t'],'dependencies':[],'origin_refs':['SO-1']}
 if identity:value['id']=identity
 return value

class KnowledgeIoTests(unittest.TestCase):
 def test_candidate_import_is_not_usable_and_queues_full_verification(self):
  ins,run=roots();new,nrun,kid=import_candidate(ins,run,candidate(),source_ref='SO-1',actor_ref='user:1');record=new['knowledge'][kid]
  self.assertEqual(record['status'],'candidate');self.assertEqual(record['formal'],{});self.assertEqual(record['reviews'],[]);self.assertIn('SO-1',record['origin_refs']);self.assertEqual(nrun['queue'][-1]['role'],'formal_check');self.assertEqual(ins['knowledge'],{})
 def test_same_id_revision_preserves_history_and_resets_verification(self):
  ins,run=roots();ins,run,kid=import_candidate(ins,run,candidate('theorem','KN-X'),source_ref='SO-1',actor_ref='user:1');old=ins['knowledge'][kid];old['status']='verified';old['formal']={'status':'verified'};old['reviews']=[{'decision':'match'}]
  revised,_,same=import_candidate(ins,run,{**candidate('theorem','KN-X'),'statement':'Q'},source_ref='SO-2',actor_ref='user:2');self.assertEqual(same,'KN-X');self.assertEqual(revised['knowledge'][same]['revision'],2);self.assertEqual(revised['knowledge'][same]['history'][-1]['statement'],'P');self.assertEqual(revised['knowledge'][same]['status'],'candidate');self.assertEqual(revised['knowledge'][same]['formal'],{})
 def test_unknown_kind_requires_explicit_definition(self):
  ins,run=roots()
  with self.assertRaises(ValueError):import_candidate(ins,run,candidate('computational_lemma'),source_ref='SO-1',actor_ref='user')
  definition={'family':'knowledge','token':'computational_lemma','meaning':'A bounded computational lemma.','constraints':{'requires_evidence':True}}
  ins,token=register_kind_definition(ins,definition,source_ref='SO-1',actor_ref='user');self.assertEqual(token,'computational_lemma');ins,_,kid=import_candidate(ins,run,candidate(token),source_ref='SO-1',actor_ref='user');self.assertEqual(ins['knowledge'][kid]['kind'],token)
 def test_missing_dependency_is_rejected(self):
  ins,run=roots();value=candidate();value['dependencies']=['KN-MISSING']
  with self.assertRaises(ValueError):import_candidate(ins,run,value,source_ref='SO-1',actor_ref='user')
 def test_research_analogy_is_distinct_from_formal_relation(self):
  ins,run=roots();ins,run,a=import_candidate(ins,run,candidate(identity='KN-A'),source_ref='SO-1',actor_ref='u');ins,run,b=import_candidate(ins,run,{**candidate(identity='KN-B'),'title':'B'},source_ref='SO-1',actor_ref='u')
  analogy={'kind':'analogous_to','source':a,'target':b,'evidence':'same recurrence shape'};check=validate_relation(ins,analogy);self.assertTrue(check['valid']);self.assertFalse(check['definition']['constraints']['mathematical_claim']);ins,rid=import_relation(ins,analogy,source_ref='SO-1',actor_ref='u');self.assertEqual(ins['relations'][-1]['authority'],'research_connection')
  formal={'kind':'formally_implies','source':a,'target':b,'evidence':'proof'};self.assertFalse(validate_relation(ins,formal)['valid'])
 def test_mathematical_relation_requires_usable_formal_and_assessment_refs(self):
  ins,run=roots();ins,run,a=import_candidate(ins,run,candidate(identity='KN-A'),source_ref='SO-1',actor_ref='u');ins,run,b=import_candidate(ins,run,{**candidate(identity='KN-B'),'title':'B'},source_ref='SO-1',actor_ref='u');ins['knowledge'][a].update(status='verified',formal={'status':'verified'},identity_assessment={'effective':True,'cycle_id':'review:A'});ins['knowledge'][b].update(status='verified',formal={'status':'verified'})
  relation={'kind':'formally_implies','source':a,'target':b,'confirmed_scope':'P implies Q','evidence':'proof','formal_result_refs':[a],'assessment_refs':['review:A']}
  self.assertFalse(validate_relation(ins,relation)['valid'], 'an unrelated approved theorem cannot establish this edge')
  ins,run,p=import_candidate(ins,run,{**candidate(identity='KN-P'),'relation_claim':{key:relation[key] for key in ('kind','source','target','confirmed_scope')}},source_ref='SO-1',actor_ref='u')
  ins['knowledge'][p].update(status='verified',formal={'status':'verified'},identity_assessment={'effective':True,'cycle_id':'review:P'})
  relation.update(formal_result_refs=[p],assessment_refs=['review:P'])
  self.assertTrue(validate_relation(ins,relation)['valid']);new,rid=import_relation(ins,relation,source_ref='SO-1',actor_ref='u');self.assertEqual(new['relations'][-1]['authority'],'mathematical_connection')
  relation['assessment_refs']=['review:A'];self.assertFalse(validate_relation(ins,relation)['valid']);relation['assessment_refs']=['review:P']
  ins['knowledge'][b]['statement']='changed endpoint';self.assertFalse(validate_relation(ins,relation)['valid'])
 def test_relation_revision_keeps_same_id_and_history(self):
  ins,run=roots();ins,run,a=import_candidate(ins,run,candidate(identity='KN-A'),source_ref='SO-1',actor_ref='u');ins,run,b=import_candidate(ins,run,{**candidate(identity='KN-B'),'title':'B'},source_ref='SO-1',actor_ref='u');first={'id':'RL-X','kind':'supports','source':a,'target':b,'evidence':'e1'};ins,rid=import_relation(ins,first,source_ref='SO-1',actor_ref='u');ins,rid2=import_relation(ins,{**first,'evidence':'e2'},source_ref='SO-2',actor_ref='u');self.assertEqual(rid2,rid);self.assertEqual(ins['relations'][-1]['revision'],2);self.assertEqual(ins['relations'][-1]['history'][-1]['evidence'],'e1')
 def test_catalog_contains_builtin_and_custom_definitions(self):
  ins,_=roots();ins,_=register_kind_definition(ins,{'family':'relation','token':'translates_to','meaning':'An explicitly scoped translation.','constraints':{'requires_evidence':True}},source_ref='SO-1',actor_ref='u');catalog=catalog_definitions(ins);self.assertTrue(any(x['token']=='theorem' for x in catalog['knowledge']));self.assertTrue(any(x['token']=='translates_to' for x in catalog['relations']))
if __name__=='__main__':unittest.main(verbosity=2)
