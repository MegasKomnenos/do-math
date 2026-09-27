"""Real local ownership observations across the pre-publication launch gap."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math.launch import ticket, termination_confirmed, validate
from do_math.windows_job import WindowsJob, owner_identity, owner_ended


@unittest.skipUnless(os.name == 'nt', 'Windows launch contract')
class LaunchRecoveryTests(unittest.TestCase):
    def test_current_owner_and_foreign_session_are_not_dead(self):
        identity = owner_identity()
        self.assertFalse(owner_ended(identity))
        self.assertIsNone(owner_ended({**identity, 'session':identity['session']+1}))
        t = ticket('EX-test', {'sha256':'a'*64,'actor_kind':'ai','role':'research_work'})
        self.assertFalse(termination_confirmed(t, recovering=True))
        t['phase']='dispatched'
        self.assertFalse(termination_confirmed(t))

    def test_crash_before_and_after_suspended_root_creation_is_recoverable(self):
        for stage in ('before_create', 'suspended', 'running', 'completed'):
            with self.subTest(stage=stage), tempfile.TemporaryDirectory() as directory:
                root=Path(directory)
                program = '''import json,sys,time
from pathlib import Path
sys.path.insert(0,sys.argv[1])
from do_math.launch import ticket
from do_math.windows_job import WindowsJob
root=Path(sys.argv[2])
t=ticket('EX-crash',{'sha256':'a'*64,'actor_kind':'ai','role':'research_work'})
t['phase']='dispatched'
(root/'ticket.json').write_text(json.dumps(t))
if sys.argv[3]!='before_create':
 command="from pathlib import Path; import time; Path(r'%s').write_text('resumed'); time.sleep(%s)" % (root/'resumed',30 if sys.argv[3]=='running' else 0)
 job=WindowsJob([sys.executable,'-c',command],name=t['job_name'])
 if sys.argv[3] in {'running','completed'}:
  job.resume()
  while not (root/'resumed').exists(): time.sleep(.01)
  if sys.argv[3]=='completed':
   while not job.inspect().root_signaled: time.sleep(.01)
(root/'ready').write_text('ready')
time.sleep(30)
'''
                child=subprocess.Popen([sys.executable,'-c',program,str(Path(__file__).resolve().parents[1]),str(root),stage],
                    creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
                try:
                    deadline=time.monotonic()+10
                    while not (root/'ready').exists() and time.monotonic()<deadline:
                        if child.poll() is not None: self.fail('owner exited before test boundary')
                        time.sleep(.02)
                    self.assertTrue((root/'ready').exists())
                    t=json.loads((root/'ticket.json').read_text())
                    self.assertFalse(termination_confirmed(t,recovering=True))
                    child.kill(); child.wait(5)
                    deadline=time.monotonic()+5
                    while not termination_confirmed(t,recovering=True) and time.monotonic()<deadline:
                        time.sleep(.02)
                    self.assertTrue(termination_confirmed(t,recovering=True))
                    self.assertEqual((root/'resumed').exists(), stage in {'running','completed'})
                finally:
                    if child.poll() is None: child.kill(); child.wait(5)

    def test_job_name_collision_cannot_attach_or_kill_the_original(self):
        t=ticket('EX-collision',{'sha256':'a'*64,'actor_kind':'ai','role':'research_work'})
        with WindowsJob([sys.executable,'-c','pass'],name=t['job_name']) as first:
            with self.assertRaises(FileExistsError):
                WindowsJob([sys.executable,'-c','pass'],name=t['job_name'])
            self.assertFalse(first.inspect().root_signaled)

    def test_ticket_cannot_be_rebound_to_another_execution(self):
        t=ticket('EX-one',{'sha256':'a'*64,'actor_kind':'ai','role':'research_work'})
        with self.assertRaises(ValueError): validate(t,execution_id='EX-two')
