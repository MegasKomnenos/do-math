from __future__ import annotations
import sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import do_math.model_runner as runner

class Job:
 pid=7; creation_filetime=9
 def terminate(self): self.terminated=True
 def close(self): self.closed=True
class Execution:
    job=Job(); request_sha256="a"
class Adapter:
    def __init__(self, result): self.result=result; self.done=False; self.stopped=False
    def start(self,*a,**k):
     import json
     self.request=json.loads(a[0].read_text(encoding='utf-8'))
     return Execution()
    def resume(self,*a): self.resumed=True
    def wait_for_termination(self,*a): self.done=True; return True
    def stop(self,*a): self.stopped=True
    def collect(self,*a): return self.result

class Tests(unittest.TestCase):
 def run_with(self, collected):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d); ws=root/'ws'; ws.mkdir(); ev=root/'e'; r=runner.CodexModelRunner('fake'); r._adapter=Adapter(collected)
   return r.run(prompt='x',output_schema={'type':'object','required':['x']},workspace=ws,evidence_dir=ev,model='m',effort='low',timeout_seconds=1)
 def test_completed_only_after_schema(self):
  x=self.run_with({'result':'output_collected','final':{'raw':b'{"x":1}'},'jsonl':{'usage':{'input_tokens':1}}})
  self.assertEqual(x['status'],'completed')
 def test_invalid_output_fails(self):
  x=self.run_with({'result':'output_collected','final':{'raw':b'{}'},'jsonl':{'usage':{}}})
  self.assertEqual(x['status'],'failed')
 def test_invalid_output_keeps_parsed_value_and_actionable_schema_error(self):
  x=self.run_with({'result':'output_collected','final':{'raw':b'{}'},'jsonl':{'usage':{}}})
  self.assertEqual(x.get('error_kind'),'output_validation')
  self.assertEqual(x['output'],{})
  self.assertIn('x',x['error'])
 def test_incomplete_fails(self):
  x=self.run_with({'result':'incomplete','reasons':['tail'],'jsonl':{}})
  self.assertEqual(x['status'],'failed')
 def test_callback_failure_does_not_resume(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d); ws=root/'ws'; ws.mkdir(); ev=root/'e'; r=runner.CodexModelRunner('fake'); a=Adapter({}); r._adapter=a
   with self.assertRaises(RuntimeError): r.run(prompt='x',output_schema={},workspace=ws,evidence_dir=ev,model='m',effort='low',timeout_seconds=1,on_started=lambda _:(_ for _ in ()).throw(RuntimeError()))
   self.assertTrue(a.stopped)
   self.assertFalse(getattr(a,'resumed',False), 'a failed start record must not resume the root')
 def test_pre_start_stop_does_not_resume(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d); ws=root/'ws'; ws.mkdir(); ev=root/'e'; r=runner.CodexModelRunner('fake'); a=Adapter({'result':'incomplete','jsonl':{}}); r._adapter=a
   x=r.run(prompt='x',output_schema={},workspace=ws,evidence_dir=ev,model='m',effort='low',timeout_seconds=1,should_stop=lambda:True)
   self.assertEqual(x['status'],'stopped'); self.assertTrue(a.stopped); self.assertFalse(getattr(a,'resumed',False))
 def test_scholarly_server_is_written_to_the_immutable_worker_request(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d); ws=root/'ws'; ws.mkdir(); ev=root/'e'; r=runner.CodexModelRunner('fake'); a=Adapter({'result':'output_collected','final':{'raw':b'{}'},'jsonl':{'usage':{}}}); r._adapter=a
   r.run(prompt='x',output_schema={'type':'object'},workspace=ws,evidence_dir=ev,model='m',effort='low',timeout_seconds=1,scholarly_server={'command':'python','args':['C:/server.py']})
   self.assertEqual(a.request['scholarly_server'],{'command':'python','args':['C:/server.py']})
class WithoutDeadlineTests(unittest.TestCase):
    def run_observed(self, *, timeout=None, stop=False):
        from unittest.mock import patch
        clock = [0.0]
        class LiveAdapter(Adapter):
            polls = 0
            def wait_for_termination(self, *args):
                self.polls += 1
                clock[0] += 10000
                return self.stopped or self.polls >= 9
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            worker = runner.CodexModelRunner('fake')
            adapter = LiveAdapter({'result': 'output_collected', 'final': {'raw': b'{}'}, 'jsonl': {}})
            worker._adapter = adapter
            with patch.object(runner.time, 'monotonic', side_effect=lambda: clock[0]), patch.object(runner.time, 'sleep'):
                result = worker.run(prompt='x', output_schema={}, workspace=root, evidence_dir=root / 'evidence',
                    model='m', effort='low', timeout_seconds=timeout,
                    should_stop=lambda: stop and adapter.polls >= 4)
            return result, adapter

    def test_long_running_work_keeps_running_until_its_normal_return(self):
        result, adapter = self.run_observed()
        self.assertEqual(result['status'], 'completed')
        self.assertFalse(adapter.stopped)
        self.assertIsNone(adapter.request['max_runtime_seconds'])

    def test_work_without_a_deadline_still_obeys_stop(self):
        result, adapter = self.run_observed(stop=True)
        self.assertEqual(result['status'], 'stopped')
        self.assertTrue(adapter.stopped)

    def test_a_finite_call_deadline_still_stops_the_runner(self):
        result, adapter = self.run_observed(timeout=1)
        self.assertEqual(result['status'], 'stopped')
        self.assertTrue(adapter.stopped)


if __name__=='__main__': unittest.main()
