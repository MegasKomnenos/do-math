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
    def start(self,*a,**k): return Execution()
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
if __name__=='__main__': unittest.main()
