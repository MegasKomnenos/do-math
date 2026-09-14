import sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from do_math.formal import verify_lean
class T(unittest.TestCase):
 def test_invalid_declaration_rejected(self):
  with tempfile.TemporaryDirectory() as d:self.assertEqual(verify_lean(source='',declarations=['bad;'],workspace=Path(d))['status'],'rejected')
 def test_missing_lean_unavailable(self):
  with tempfile.TemporaryDirectory() as d:self.assertEqual(verify_lean(source='',declarations=['X'],workspace=Path(d),lean_command=['no-such-lean'])['status'],'unavailable')
 def test_fake_lean_rejects_real_sorry_even_when_source_prints_allowed_text(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d); fake=root/'fake.py'; fake.write_text("import sys\nif '--version' in sys.argv: print('Lean fake')\nelse: print(\"'X' depends on axioms: [Classical.choice]\"); print(\"'X' depends on axioms: [sorryAx]\")",encoding='utf8')
   r=verify_lean(source='#eval \"X depends on axioms: [Classical.choice]\"',declarations=['X'],workspace=root,lean_command=[sys.executable,str(fake)])
   self.assertEqual(r['status'],'rejected'); self.assertIn('sorryAx',r['axioms']['X'])
 def test_missing_axiom_output_fails(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d); fake=root/'fake.py'; fake.write_text("import sys\nif '--version' in sys.argv: print('v')",encoding='utf8')
   self.assertEqual(verify_lean(source='',declarations=['X'],workspace=root,lean_command=[sys.executable,str(fake)])['status'],'failed')
if __name__=='__main__':unittest.main()
