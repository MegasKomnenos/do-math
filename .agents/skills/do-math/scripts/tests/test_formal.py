import subprocess,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from do_math.formal import project_fingerprint, verify_lean, _ident
class T(unittest.TestCase):
 def test_prime_names_keep_the_existing_identifier_boundary(self):
  for value in ("sumTo_succ'", "N.foo''", "α'", "N'.foo'"):
   self.assertTrue(_ident(value), value)
  for value in ("'", "N.'", "x'; #eval 1", "x' y", "x\ny", "x'y", 'x"', "x()", ".x", "x."):
   self.assertFalse(_ident(value), value)
 def test_actual_prime_declarations_have_signatures_and_axioms(self):
  with tempfile.TemporaryDirectory() as d:
   names=["sumTo_succ'", "N.foo''", "α'"]
   source="theorem sumTo_succ' (n : Nat) : n = n := rfl\nnamespace N\ntheorem foo'' : True := by trivial\nend N\ntheorem α' : True := by trivial"
   result=verify_lean(source=source,declarations=names,workspace=Path(d))
   self.assertEqual(result['status'],'verified',result)
   self.assertEqual(set(result['declaration_signatures']),set(names))
   self.assertEqual(set(result['axioms']),set(names))
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
 def test_actual_signatures_preserve_binders_and_unicode(self):
  with tempfile.TemporaryDirectory() as d:
   r=verify_lean(source='theorem good (n : Nat) : n = n := rfl\ndef unicodeGood : ∀ α : Type, α → α := fun _ x => x',declarations=['good','unicodeGood'],workspace=Path(d))
   self.assertEqual(r['status'],'verified');self.assertIn('(n : Nat)',r['declaration_signatures']['good']);self.assertIn('α',r['declaration_signatures']['unicodeGood'])
 def test_project_fingerprint_excludes_unrelated_and_tracks_project_changes(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);project=root/'project';project.mkdir();(project/'Main.lean').write_text('def x := 1',encoding='utf8');(root/'unrelated').mkdir();(root/'unrelated'/'x').write_text('a',encoding='utf8')
   subprocess.run(['git','-C',str(root),'init','-q'],check=True);subprocess.run(['git','-C',str(root),'add','.'],check=True);subprocess.run(['git','-C',str(root),'-c','user.name=t','-c','user.email=t@x','commit','-qm','base'],check=True)
   before=project_fingerprint(project);(root/'unrelated'/'x').write_text('b',encoding='utf8');subprocess.run(['git','-C',str(root),'add','unrelated/x'],check=True);subprocess.run(['git','-C',str(root),'-c','user.name=t','-c','user.email=t@x','commit','-qm','unrelated'],check=True);self.assertEqual(before,project_fingerprint(project))
   (project/'Main.lean').write_text('def x := 2',encoding='utf8');self.assertNotEqual(before,project_fingerprint(project))
 def test_stop_is_not_a_math_failure(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d); fake=root/'fake.py';fake.write_text("import sys,time\nif '--version' in sys.argv: print('v')\nelse: time.sleep(10)",encoding='utf8')
   self.assertEqual(verify_lean(source='',declarations=['X'],workspace=root,lean_command=[sys.executable,str(fake)],should_stop=lambda:True)['status'],'stopped')
if __name__=='__main__':unittest.main()
