import json,unittest
from pathlib import Path
from original_title import source_title,font_title
BASE=Path(__file__).resolve().parents[2]
PID='VER-31896676a216a41ed9fdb24f'
P=next(json.loads(line) for line in (BASE/'catalog/abstract-format-partition/groups/02-needs-source-mathscinet-fields-json/members.jsonl').read_text(encoding='utf-8').splitlines() if PID in line)
class OriginalTitleTests(unittest.TestCase):
 def test_actual_original_title_is_bound_to_assigned_record_hash(self):
  title=source_title(P,'MR3994384');self.assertIn('C',title);self.assertIn('^*',title)
  self.assertEqual(font_title(title),font_title(r'Axiomatic K-theory for {\rm C}^*-algebras.'))
 def test_math_star_is_not_erased(self):
  self.assertNotEqual(font_title(source_title(P,'MR3994384')),font_title(r'Axiomatic K-theory for {\rm C}-algebras.'))
 def test_fraction_arguments_are_not_flattened(self):
  self.assertIsNone(font_title(r'A title with $\frac{a}{bc}$'))
  self.assertNotEqual(font_title('A title with x^{ab}'),font_title('A title with x^ab'))
 def test_font_and_math_case_are_not_discarded(self):
  self.assertNotEqual(font_title(r'A title with $\mathbf{X}$'),font_title('A title with X'))
  self.assertNotEqual(font_title('A title with x^A'),font_title('A title with x^a'))
 def test_wrong_source_hash_is_rejected(self):
  import copy
  p=copy.deepcopy(P);p['source_records'][0]['record_sha256']='0'*64
  self.assertIsNone(source_title(p,'MR3994384'))
if __name__=='__main__':unittest.main()
