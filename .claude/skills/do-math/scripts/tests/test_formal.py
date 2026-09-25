import os,subprocess,sys,tempfile,unittest
import hashlib
from unittest.mock import patch, Mock
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from test_categories import test_group as category
from do_math.formal import project_fingerprint, verify_lean, _ident, portable_bin, toolchain_root, compare_formal_results
from do_math import formal

def actual_command():
 # Explicit portable compiler coverage; Mathlib readiness is checked separately.
 return [os.environ.get('DO_MATH_KNOWLEDGE_TEST_LEAN', str(portable_bin(toolchain_root())/'lean.exe'))]
class T(unittest.TestCase):
 def test_project_preparation_honors_stop_before_starting_git(self):
  with tempfile.TemporaryDirectory() as d, patch('do_math.formal.subprocess.Popen',side_effect=AssertionError('must stop before Git')):
   with self.assertRaisesRegex(RuntimeError,'stopped'):
    project_fingerprint(Path(d),should_stop=lambda:True)


 def test_nested_stop_preserves_flushed_child_output(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);ready=root/'ready'
   child="import time; from pathlib import Path; print('child started',flush=True); Path("+repr(str(ready))+").touch(); time.sleep(10)"
   parent='import subprocess,sys,time; subprocess.Popen([sys.executable,"-c",'+repr(child)+']); time.sleep(10)'
   result=formal._job_run([sys.executable,'-c',parent],root,should_stop=ready.exists)
  self.assertTrue(result[3])
  self.assertIn('child started',result[1])

 def test_compiler_crash_preserves_native_exit_code(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);fake=root/'compiler.py'
   fake.write_text("import sys,ctypes\nif '--version' in sys.argv: print('synthetic compiler')\nelse: ctypes.windll.kernel32.ExitProcess(0xC0000005)\n",encoding='utf8')
   result=verify_lean(source='theorem good : True := True.intro',declarations=['good'],
    workspace=root,lean_command=[sys.executable,str(fake)])
  self.assertEqual(result['status'],'failed')
  self.assertEqual(result.get('exit_code'),0xC0000005)
  self.assertEqual(result['reason'],'compiler crashed')

 def test_job_start_failure_is_not_reported_as_timeout(self):
  with tempfile.TemporaryDirectory() as d:
   with self.assertRaisesRegex(RuntimeError, 'FileNotFoundError'):
    formal._job_run([str(Path(d)/'missing-compiler.exe')], Path(d))

 def test_job_missing_completion_is_not_reported_as_timeout(self):
  job=Mock(name='worker'); job.name='worker'; job.pid=17; job.creation_filetime=1
  job.wait.return_value=True
  job.inspect.return_value=type('Inspection',(),{'root_signaled':True,'active_processes':0,'process_ids':()})()
  with tempfile.TemporaryDirectory() as d, patch('do_math.formal.WindowsJob',return_value=job):
   with self.assertRaisesRegex(RuntimeError, 'completion status'):
    formal._job_run(['fixture'],Path(d))
  job.close.assert_called_once()

 def test_job_termination_confirmation_has_a_fixed_deadline(self):
  job=Mock(name='worker'); job.name='worker'; job.pid=17; job.creation_filetime=1
  job.wait.return_value=True
  pending=type('Inspection',(),{'root_signaled':True,'active_processes':1,'process_ids':(18,)})()
  empty=type('Inspection',(),{'root_signaled':True,'active_processes':0,'process_ids':()})()
  # Eventually empty so the old unbounded loop fails the assertion rather than hanging the suite.
  job.inspect.side_effect=[pending]*20+[empty]
  with tempfile.TemporaryDirectory() as d, patch('do_math.formal.WindowsJob',return_value=job), \
    patch('do_math.formal.time.monotonic',side_effect=range(100)), patch('do_math.formal.time.sleep'):
   with self.assertRaisesRegex(RuntimeError, 'termination'):
    formal._job_run(['fixture'],Path(d),should_stop=lambda:True)
  job.terminate.assert_called_once()
  job.close.assert_called_once()


 def test_actual_job_stop_without_completion_is_still_stopped(self):
  with tempfile.TemporaryDirectory() as d:
   result=formal._job_run([sys.executable,'-c','import time; time.sleep(10)'],Path(d),should_stop=lambda:True)
  self.assertTrue(result[3])

 def test_verifier_reports_worker_failure_without_raising_or_claiming_timeout(self):
  with tempfile.TemporaryDirectory() as d, patch('do_math.formal.inspect_toolchain',return_value={}), \
    patch('do_math.formal._job_run',side_effect=RuntimeError('worker completion status missing')):
   result=verify_lean(source='theorem good : True := True.intro',declarations=['good'],
    workspace=Path(d),lean_command=[sys.executable])
  self.assertEqual(result['status'],'failed')
  self.assertIn('worker completion status missing',result['reason'])
  self.assertNotEqual(result['reason'],'timeout')

 def test_pinned_project_change_is_rejected_before_process_start(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d); project=root/'project'; project.mkdir()
   subprocess.run(['git','-C',str(root),'init','-q'],check=True)
   manifest=project/'lakefile.toml'; manifest.write_bytes(b'name = "approved"\n')
   executable=root/'lake.exe'; executable.write_bytes(b'not executed')
   command=[str(executable),'--dir',str(project),'env','lean']
   digest=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
   expected={'configured_command':command,'executable':str(executable),'sha256':digest(executable),
    'verifier_sha256':digest(Path(formal.__file__)), 'verifier_path':str(Path(formal.__file__).resolve()),
    'executables':{str(executable):digest(executable)},
    'version':'fixture','version_exit':0,'project':{'manifest_hashes':{'lakefile.toml':digest(manifest)},
     'fingerprint':project_fingerprint(project),'search_paths':[]}}
   manifest.write_bytes(b'name = "changed"\n')
   run_job=formal._job_run
   def only_git(command,*args,**kwargs):
    self.assertEqual(command[0],'git','changed project must not start the compiler')
    return run_job(command,*args,**kwargs)
   with patch('do_math.formal._job_run',side_effect=only_git):
    result=verify_lean(source='theorem x : True := True.intro',declarations=['x'],
     workspace=root,lean_command=command,expected_toolchain=expected)
   self.assertEqual(result['status'],'rejected')
   self.assertEqual(result['reason'],'approved project inputs changed before execution')

 @category('lean')
 def test_actual_exact_unicode_names_and_expressions_are_not_normalized(self):
  names=['\u212a','K']
  source='theorem \u212a (\u2126 : True) : True := \u2126\r\ntheorem K : True := True.intro\n-- e\u0301\n'
  with tempfile.TemporaryDirectory() as d:
   result=verify_lean(source=source,declarations=names,workspace=Path(d),lean_command=actual_command())
  self.assertEqual(result['status'],'verified',{k:result.get(k) for k in ('status','reason','stderr')})
  self.assertEqual(result['source_sha256'],hashlib.sha256(source.encode()).hexdigest())
  self.assertEqual(result['declarations'],names)
  self.assertEqual(set(result['declaration_evidence']),set(names))
  self.assertEqual(set(result['declaration_signatures']),set(names))
  self.assertIn('\u2126',result['declaration_signatures'][names[0]])

 def test_changed_approved_executable_is_rejected_before_version_execution(self):
  with tempfile.TemporaryDirectory() as d, patch('do_math.formal._job_run', return_value=(0,'fixture version','',False)) as run:
   executable=Path(d)/'synthetic-lean.exe'
   executable.write_bytes(b'approved fixture executable')
   command=[str(executable)]
   approved=formal.inspect_toolchain(command,Path(d))
   run.reset_mock()
   executable.write_bytes(b'changed fixture executable')
   result=verify_lean(source='theorem x : True := True.intro',declarations=['x'],workspace=Path(d),
    lean_command=command,expected_toolchain=approved)
   self.assertEqual(result['status'],'rejected',result)
   run.assert_not_called()
 def test_approved_executable_change_during_run_is_rejected_before_evidence_parsing(self):
  with tempfile.TemporaryDirectory() as d:
   executable=Path(d)/'synthetic-lean.exe';executable.write_bytes(b'approved fixture executable')
   command=[str(executable)]
   with patch('do_math.formal._job_run',return_value=(0,'fixture version','',False)):
    expected=formal.inspect_toolchain(command,Path(d))
   def run(args,*unused,**kwargs):
    if args[-1]=='--version': return 0,'fixture version','',False
    executable.write_bytes(b'changed during simulated compiler run')
    return 0,'','',False
   with patch('do_math.formal._job_run',side_effect=run):
    result=verify_lean(source='theorem x : True := True.intro',declarations=['x'],workspace=Path(d),
     lean_command=command,expected_toolchain=expected)
   self.assertEqual(result['status'],'rejected',result)
   self.assertEqual(result['reason'],'approved toolchain changed during verification')
 def test_path_lookup_spelling_matches_the_inspected_executable(self):
  if os.name!='nt': self.skipTest('Windows PATHEXT lookup keeps the spelling of its argument')
  with tempfile.TemporaryDirectory() as d, patch('do_math.formal._job_run',return_value=(0,'fixture version','',False)):
   root=Path(d).resolve();(root/'synthetic-lean.exe').write_bytes(b'approved fixture executable')
   command=[str(root/'SYNTHETIC-LEAN.EXE')]
   observed=formal.inspect_toolchain(command,root)
   self.assertEqual(observed['executable'],str(root/'synthetic-lean.exe'))
   result=verify_lean(source='theorem x : True := True.intro',declarations=['x'],workspace=root,
    lean_command=command,expected_toolchain=observed)
  self.assertEqual((result['status'],result['reason']),('failed','signature output missing'),result)
 def test_prime_names_keep_the_existing_identifier_boundary(self):
  for value in ("sumTo_succ'", "N.foo''", "α'", "N'.foo'"):
   self.assertTrue(_ident(value), value)
  for value in ("'", "N.'", "x'; #eval 1", "x' y", "x\ny", "x'y", 'x"', "x()", ".x", "x."):
   self.assertFalse(_ident(value), value)
 @category('lean')
 def test_actual_prime_declarations_have_signatures_and_axioms(self):
  with tempfile.TemporaryDirectory() as d:
   names=["sumTo_succ'", "N.foo''", "α'"]
   source="theorem sumTo_succ' (n : Nat) : n = n := rfl\nnamespace N\ntheorem foo'' : True := by trivial\nend N\ntheorem α' : True := by trivial"
   result=verify_lean(source=source,declarations=names,workspace=Path(d),lean_command=actual_command())
   self.assertEqual(result['status'],'verified',result)
   self.assertEqual(set(result['declaration_signatures']),set(names))
   self.assertEqual(set(result['axioms']),set(names))
   self.assertEqual(set(result['declaration_evidence']),set(names))
   for name in names:
    self.assertEqual(set(result['dependency_evidence'][name]),set(result['dependency_closure'][name]))
 def test_invalid_declaration_rejected(self):
  with tempfile.TemporaryDirectory() as d:self.assertEqual(verify_lean(source='',declarations=['bad;'],workspace=Path(d))['status'],'rejected')
 def test_empty_declaration_list_is_rejected(self):
  with tempfile.TemporaryDirectory() as d:self.assertEqual(verify_lean(source='theorem foo : False := sorry',declarations=[],workspace=Path(d))['status'],'rejected')
 def test_missing_lean_unavailable(self):
  with tempfile.TemporaryDirectory() as d:self.assertEqual(verify_lean(source='',declarations=['X'],workspace=Path(d),lean_command=['no-such-lean'])['status'],'unavailable')
 def test_fake_lean_rejects_real_sorry_even_when_source_prints_allowed_text(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d); fake=root/'fake.py'; fake.write_text("import sys\nif '--version' in sys.argv: print('Lean fake')\nelse: print('\"__DO_MATH_SIGNATURE_BEGIN_X__\"'); print('X : True'); print('\"__DO_MATH_SIGNATURE_END_X__\"'); print(\"'X' depends on axioms: [Classical.choice]\"); print(\"'X' depends on axioms: [sorryAx]\")",encoding='utf8')
   r=verify_lean(source='#eval \"X depends on axioms: [Classical.choice]\"',declarations=['X'],workspace=root,lean_command=[sys.executable,str(fake)])
   self.assertEqual(r['status'],'rejected'); self.assertIn('sorryAx',r['axioms']['X'])
 def test_missing_axiom_output_fails(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d); fake=root/'fake.py'; fake.write_text("import sys\nif '--version' in sys.argv: print('v')",encoding='utf8')
   self.assertEqual(verify_lean(source='',declarations=['X'],workspace=root,lean_command=[sys.executable,str(fake)])['status'],'failed')
 @category('lean')
 def test_actual_signatures_preserve_binders_and_unicode(self):
  with tempfile.TemporaryDirectory() as d:
   r=verify_lean(source='theorem good (n : Nat) : n = n := rfl\ndef unicodeGood : ∀ α : Type, α → α := fun _ x => x',declarations=['good','unicodeGood'],workspace=Path(d),lean_command=actual_command())
   self.assertEqual(r['status'],'verified');self.assertIn('(n : Nat)',r['declaration_signatures']['good']);self.assertIn('α',r['declaration_signatures']['unicodeGood'])
 @category('lean')
 def test_actual_changed_transitive_body_requires_identity_reassessment(self):
  results=[]
  with tempfile.TemporaryDirectory() as d:
   for value in (1,2):
    result=verify_lean(source=f'def base : Nat := {value}\ndef mid : Nat := base\ntheorem leaf : mid = mid := rfl',
     declarations=['leaf'],workspace=Path(d),lean_command=actual_command())
    self.assertEqual(result['status'],'verified',result)
    self.assertIn('base',result['dependency_closure']['leaf'])
    results.append(result)
  comparison=compare_formal_results(*results)
  self.assertTrue(comparison['requires_identity_review'])
  self.assertIn('dependency_evidence',comparison['changed'])
  self.assertFalse(compare_formal_results(results[0],results[0])['requires_identity_review'])
 def test_project_fingerprint_excludes_unrelated_and_tracks_project_changes(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);project=root/'project';project.mkdir();(project/'Main.lean').write_text('def x := 1',encoding='utf8');(root/'unrelated').mkdir();(root/'unrelated'/'x').write_text('a',encoding='utf8')
   subprocess.run(['git','-C',str(root),'init','-q'],check=True);subprocess.run(['git','-C',str(root),'add','.'],check=True);subprocess.run(['git','-C',str(root),'-c','user.name=t','-c','user.email=t@x','commit','-qm','base'],check=True)
   before=project_fingerprint(project);(project/'.lake'/'packages'/'dep').mkdir(parents=True);(project/'.lake'/'packages'/'dep'/'Dep.lean').write_text('def y := 1',encoding='utf8');self.assertEqual(before,project_fingerprint(project))
   (root/'unrelated'/'x').write_text('b',encoding='utf8');subprocess.run(['git','-C',str(root),'add','unrelated/x'],check=True);subprocess.run(['git','-C',str(root),'-c','user.name=t','-c','user.email=t@x','commit','-qm','unrelated'],check=True);self.assertEqual(before,project_fingerprint(project))
   (project/'Main.lean').write_text('def x := 2',encoding='utf8');self.assertNotEqual(before,project_fingerprint(project))
 def test_stop_is_not_a_math_failure(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d); fake=root/'fake.py';fake.write_text("import sys,time\nif '--version' in sys.argv: print('v')\nelse: time.sleep(10)",encoding='utf8')
   self.assertEqual(verify_lean(source='',declarations=['X'],workspace=root,lean_command=[sys.executable,str(fake)],should_stop=lambda:True)['status'],'stopped')
 def test_untracked_project_does_not_report_unresolved_git_expression_as_hash(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);project=root/'untracked';project.mkdir()
   (root/'tracked.txt').write_text('fixture',encoding='utf8')
   (project/'lakefile.toml').write_text('name = "fixture"',encoding='utf8')
   subprocess.run(['git','-C',str(root),'init','-q'],check=True)
   subprocess.run(['git','-C',str(root),'add','tracked.txt'],check=True)
   subprocess.run(['git','-C',str(root),'-c','user.name=t','-c','user.email=t@x','commit','-qm','fixture'],check=True)
   fingerprint=project_fingerprint(project)
   self.assertIsNone(fingerprint['git_tree'])
   self.assertEqual(fingerprint['untracked_file_count'],1)
   self.assertRegex(fingerprint['untracked_sha256'],r'^[0-9a-f]{64}$')
if __name__=='__main__':unittest.main()
