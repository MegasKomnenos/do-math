from __future__ import annotations
from copy import deepcopy
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from do_math.governance import apply_decision,authorize,ensure_governance
class Tests(unittest.TestCase):
 def setUp(self):
  self.instance={'goal':'old','goal_kind':'mathematical','goal_status':'unresolved','policies':'p'};self.runtime={'status':'ready','tasks':{'old':{'id':'old','status':'planned','completion_criteria':[]},'done':{'id':'done','status':'completed','completion_criteria':[]}},'queue':[],'executions':{},'questions':[]}
 def test_goal_policy_and_idempotence(self):
  i,r,event=apply_decision(self.instance,self.runtime,{'kind':'goal','decision_id':'D','goal':'new','expected_revision':1},source_ref='user')
  self.assertEqual(i['goal_revision'],2);self.assertEqual(r['tasks']['old']['status'],'needs_revision');self.assertEqual(r['tasks']['done']['status'],'completed')
  i2,r2,same=apply_decision(i,r,{'kind':'goal','decision_id':'D','goal':'new','expected_revision':1},source_ref='user');self.assertEqual(same,event)
  with self.assertRaises(ValueError):apply_decision(i,r,{'kind':'policy','text':'x'},source_ref='user',actor='ai')
 def test_grant_expiry_revoke_and_operations_survive(self):
  i=ensure_governance(self.instance,'2026-01-01T00:00:00Z');work=next(g for g in i['grants'].values() if g['budget_kind']=='work');ops=next(g for g in i['grants'].values() if g['budget_kind']=='operations')
  self.assertTrue(authorize(i,{'role':'operational_review'},'2026-01-01T00:00:00Z')['allowed']);i['grants'][work['id']]['expires_at']='2020-01-01T00:00:00Z';self.assertFalse(authorize(i,{'role':'research_work'},'2026-01-01T00:00:00Z')['allowed']);self.assertTrue(authorize(i,{'role':'operational_review'},'2026-01-01T00:00:00Z')['allowed'])
  i,r,_=apply_decision(i,self.runtime,{'kind':'revoke','grant_id':ops['id'],'decision_id':'R'},source_ref='user');self.assertFalse(authorize(i,{'role':'operational_review'},'2026-01-01T00:00:00Z')['allowed'])
 def test_transfer_merges_criteria_revisions_and_rejects_live_execution(self):
  self.runtime['tasks']={'source':{'id':'source','status':'planned','revision':1,'completion_criteria':['source-proof'],'reviews':[]},'target':{'id':'target','status':'ready','revision':2,'completion_criteria':['target-proof'],'reviews':[{'decision':'approved'}],'assessment':{'decision':'completed'}}}
  i,r,_=apply_decision(self.instance,self.runtime,{'kind':'task_scope','decision_id':'X','task_id':'source','disposition':'transfer','target_task_id':'target','reason':'user transfer'},source_ref='user')
  target=r['tasks']['target'];self.assertEqual(target['completion_criteria'],['target-proof','source-proof']);self.assertEqual(target['revision'],3);self.assertEqual(target['reviews'],[]);self.assertNotIn('assessment',target);self.assertEqual(target['status'],'needs_revision');self.assertTrue(any(a['role']=='task_contract_review' and a['target']=='target' for a in r['queue']))
  live=deepcopy(self.runtime);live['executions']={'E':{'id':'E','status':'running','action':{'target':'target'}}};before=deepcopy(live['tasks']['target'])
  with self.assertRaises(ValueError):apply_decision(self.instance,live,{'kind':'task_scope','decision_id':'Y','task_id':'source','disposition':'transfer','target_task_id':'target','reason':'user transfer'},source_ref='user')
  self.assertEqual(live['tasks']['target'],before)
