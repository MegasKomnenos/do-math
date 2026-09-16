from __future__ import annotations
import json,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from do_math.observations import ObservationTracker,read_checkpoint,request_checkpoint
class Clock:
 def __init__(self):self.x=0
 def __call__(self):return self.x
class Tests(unittest.TestCase):
 def setUp(self):self.temp=tempfile.TemporaryDirectory();self.ws=Path(self.temp.name);self.clock=Clock();self.t=ObservationTracker('E',self.ws,{'observation_idle_seconds':5,'observation_interval_seconds':3,'max_observation_reviews':2},clock=self.clock)
 def tearDown(self):self.temp.cleanup()
 def write(self,state='working',extra=''):(self.ws/'checkpoint.json').write_text(json.dumps({'current_claim':'c','evidence_paths':[],'attempts':[],'remaining_work':[],'next_step':'n','progress_state':state})+extra,encoding='utf-8')
 def test_checkpoint_requires_available_preserved_evidence_paths(self):
  value={'current_claim':'c','evidence_paths':['proof.txt'],'attempts':[],'remaining_work':[],'next_step':'n','progress_state':'working'}
  (self.ws/'checkpoint.json').write_text(json.dumps(value),encoding='utf-8')
  self.assertEqual(read_checkpoint(self.ws)['status'],'invalid')
  (self.ws/'proof.txt').write_text('actual evidence',encoding='utf-8')
  self.assertEqual(read_checkpoint(self.ws)['status'],'valid')
  (self.ws/'.scratch').mkdir();(self.ws/'.scratch/proof.txt').write_text('disposable',encoding='utf-8')
  value['evidence_paths']=['.scratch/proof.txt'];(self.ws/'checkpoint.json').write_text(json.dumps(value),encoding='utf-8')
  self.assertEqual(read_checkpoint(self.ws)['status'],'invalid')
 def test_idle_is_due_not_math_failure_and_hash_change_only(self):
  self.clock.x=6;due=self.t.observe({'type':'tick'});self.assertEqual(due[-1]['reason'],'no_visible_activity');self.assertEqual(self.t.observe({'type':'tick'}),[])
  self.write();self.assertEqual([x['kind'] for x in self.t.observe({'type':'tick'})],['checkpoint']);self.assertEqual(self.t.observe({'type':'tick'}),[])
 def test_blocked_periodic_and_invalid_checkpoint(self):
  self.write('blocked');self.assertTrue(any(x.get('reason')=='worker_reported_obstacle' for x in self.t.observe({'type':'tick'})))
  self.t.config['observation_mode']='periodic';self.clock.x=10;self.write('working');due=[x for x in self.t.observe({'type':'tick'}) if x['kind']=='operational_review_due'];self.assertEqual([x['reason'] for x in due],['periodic_review']);self.assertEqual(self.t.review_count,2)
  self.clock.x=20;self.write('working',' ');self.assertEqual([x for x in self.t.observe({'type':'tick'}) if x['kind']=='operational_review_due'],[]);self.assertEqual(self.t.review_count,2)
  (self.ws/'checkpoint.json').write_bytes(b'\xff');self.assertEqual(read_checkpoint(self.ws)['status'],'invalid')
  (self.ws/'checkpoint.json').unlink();self.assertEqual(read_checkpoint(self.ws)['status'],'missing')
  (self.ws/'checkpoint.json').write_text('{"current_claim":"partial"}',encoding='utf-8');self.assertEqual(read_checkpoint(self.ws)['status'],'invalid')
  request=request_checkpoint(self.ws,'stop',immediate=True,deadline='2026-01-01T00:00:00Z');self.assertIn('Do not start new research',request['instruction'])
