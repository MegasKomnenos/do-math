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
 def test_transport_and_tool_wait_are_bounded_without_becoming_math_progress(self):
  self.t.config.update(observation_idle_seconds=5,observation_interval_seconds=20,observation_unbounded_wait_seconds=20)
  self.clock.x=4;self.assertEqual(self.t.observe({'type':'transport_bytes_received','bytes':100}),[])
  self.clock.x=7;self.assertEqual(self.t.observe({'type':'transport_bytes_received','bytes':50}),[])
  self.assertEqual(self.t.last_activity,0)
  self.clock.x=21;due=self.t.observe({'type':'transport_bytes_received','bytes':10})[-1]
  self.assertEqual(due['reason'],'output_streaming_review');self.assertEqual(due['sample']['transport_bytes'],160)
  self.assertEqual(due['sample']['tool_results'],0)
  self.clock.x=22;self.t.observe({'type':'assistant','message':{'content':[{'type':'tool_use','id':'tool','name':'Bash','input':{'timeout':10000}}]}})
  self.clock.x=28;self.assertEqual(self.t.observe({'type':'tick'}),[])
  self.clock.x=33;due=self.t.observe({'type':'tick'})[-1]
  self.assertEqual(due['reason'],'tool_timeout_observed')
 def tool(self,timeout=None):
  value={'timeout':timeout} if timeout else {}
  return {'type':'assistant','message':{'content':[{'type':'tool_use','id':'tool','name':'Bash','input':value}]}}
 def due(self,event):return [x['reason'] for x in self.t.observe(event) if x['kind']=='operational_review_due']
 def test_event_driven_wait_inside_a_declared_tool_timeout_is_not_reviewed_by_elapsed_time(self):
  self.t.config.update(observation_unbounded_wait_seconds=20)
  self.clock.x=1;self.t.observe(self.tool(100000))
  for self.clock.x in (4,10,19,50,99):self.assertEqual(self.due({'type':'tick'}),[])
  self.clock.x=102;self.assertEqual(self.due({'type':'tick'}),['tool_timeout_observed'])
 def test_event_driven_wait_on_a_tool_without_timeout_is_reviewed_once_per_unbounded_wait(self):
  self.t.config.update(observation_unbounded_wait_seconds=20,max_observation_reviews=3)
  self.clock.x=1;self.t.observe(self.tool())
  self.clock.x=10;self.assertEqual(self.due({'type':'tick'}),[])
  self.clock.x=21;self.assertEqual(self.due({'type':'tick'}),['untimed_tool_wait_review'])
  self.clock.x=30;self.assertEqual(self.due({'type':'tick'}),[])
  self.clock.x=41;self.assertEqual(self.due({'type':'tick'}),['untimed_tool_wait_review'])
 def test_event_driven_streaming_with_work_events_is_not_reviewed_by_elapsed_time(self):
  self.t.config.update(observation_unbounded_wait_seconds=20)
  for self.clock.x in range(2,60,2):
   self.assertEqual(self.due({'type':'transport_bytes_received','bytes':1}),[])
   self.t.observe({'type':'assistant','message':{'content':[{'type':'text','text':'working'}]}})
 def test_periodic_mode_still_reviews_waiting_states_each_interval(self):
  self.t.config.update(observation_mode='periodic',observation_unbounded_wait_seconds=600)
  self.clock.x=1;self.t.observe(self.tool(100000))
  self.clock.x=4;self.assertEqual(self.due({'type':'tick'}),['tool_wait_review'])
 def test_missing_checkpoint_reminder_is_emitted_once_for_checkpointing_roles_only(self):
  kinds=lambda t:[x['kind'] for x in t.observe({'type':'assistant','message':{'content':[]}}) if x['kind']=='checkpoint_reminder_due']
  self.clock.x=2;self.assertEqual(kinds(self.t),[])
  self.clock.x=4;self.assertEqual(kinds(self.t),[])
  expected=ObservationTracker('W',self.ws,{**self.t.config,'checkpoint_expected':True},clock=self.clock)
  expected.started=0
  self.assertEqual(kinds(expected),['checkpoint_reminder_due']);self.clock.x=9;self.assertEqual(kinds(expected),[])
  written=ObservationTracker('V',self.ws,{**self.t.config,'checkpoint_expected':True},clock=self.clock)
  written.started=0;self.write();self.assertEqual(kinds(written),[])
 def test_ping_does_not_hide_idle(self):
  self.clock.x=6;due=self.t.observe({'type':'ping'})[-1]
  self.assertEqual(due['reason'],'no_visible_activity')
 def test_blocked_periodic_and_invalid_checkpoint(self):
  self.write('blocked');self.assertTrue(any(x.get('reason')=='worker_reported_obstacle' for x in self.t.observe({'type':'tick'})))
  self.t.config['observation_mode']='periodic';self.clock.x=10;self.write('working');due=[x for x in self.t.observe({'type':'tick'}) if x['kind']=='operational_review_due'];self.assertEqual([x['reason'] for x in due],['periodic_review']);self.assertEqual(self.t.review_count,2)
  self.clock.x=20;self.write('working',' ');self.assertEqual([x for x in self.t.observe({'type':'tick'}) if x['kind']=='operational_review_due'],[]);self.assertEqual(self.t.review_count,2)
  (self.ws/'checkpoint.json').write_bytes(b'\xff');self.assertEqual(read_checkpoint(self.ws)['status'],'invalid')
  (self.ws/'checkpoint.json').unlink();self.assertEqual(read_checkpoint(self.ws)['status'],'missing')
  (self.ws/'checkpoint.json').write_text('{"current_claim":"partial"}',encoding='utf-8');self.assertEqual(read_checkpoint(self.ws)['status'],'invalid')
  request=request_checkpoint(self.ws,'stop',immediate=True,deadline='2026-01-01T00:00:00Z');self.assertIn('Do not start new research',request['instruction'])
class ReminderTests(unittest.TestCase):
 def test_executor_reminder_is_written_once_and_never_replaces_existing_feedback(self):
  from do_math.observations import write_checkpoint_reminder
  with tempfile.TemporaryDirectory() as temp:
   ws=Path(temp);self.assertTrue(write_checkpoint_reminder(ws))
   value=json.loads((ws/'observation-feedback.json').read_text(encoding='utf-8'))
   self.assertEqual((value['source'],value['decision']),('executor','checkpoint'));self.assertIn('current_claim',value['reason'])
   (ws/'observation-feedback.json').write_text('{"decision":"checkpoint","reason":"reviewer"}',encoding='utf-8')
   self.assertFalse(write_checkpoint_reminder(ws));self.assertIn('reviewer',(ws/'observation-feedback.json').read_text(encoding='utf-8'))
 def test_engine_answers_the_reminder_without_opening_a_model_review(self):
  from types import SimpleNamespace
  from do_math.engine import ResearchEngine
  with tempfile.TemporaryDirectory() as temp:
   ws=Path(temp)/'runs'/'E'/'workspace';ws.mkdir(parents=True)
   queued=[]
   fake=SimpleNamespace(_controls=lambda:None,_check_conversations=lambda:False,_save=lambda *a:None,_inline_reviewing=False,
    instance={'workspace':temp},runtime={'status':'running'},_run_inline_review=lambda *a:queued.append(a))
   tracker=SimpleNamespace(observe=lambda event:[{'kind':'checkpoint_reminder_due','execution_id':'E'}])
   ResearchEngine._observe_running(fake,'E',tracker,{'type':'tick'},0)
   self.assertTrue((ws/'observation-feedback.json').exists());self.assertEqual(queued,[])
if __name__=='__main__':unittest.main()
