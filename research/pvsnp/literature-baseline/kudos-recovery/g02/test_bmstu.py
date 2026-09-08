import unittest
from pathlib import Path
from bmstu import abstract_field
ROOT=Path(__file__).resolve().parents[2]/'intake/kudos-recovery/g02/VER-0050890c5c715f7ad7e98d97'
class BmstuTests(unittest.TestCase):
 def test_actual1973_annotation_boundary(self):
  result=abstract_field((ROOT/'bmstu-1973-ui.txt').read_text(encoding='utf-8'),1973,207)
  self.assertTrue(result.startswith('В книге излагаются числовые ряды'))
  self.assertTrue(result.endswith('работе над предметом.'));self.assertNotIn('УДК',result)
 def test_2002_record_mentioning1973_in_related_editions_is_rejected(self):
  self.assertIsNone(abstract_field((ROOT/'bmstu-ui.txt').read_text(encoding='utf-8'),1973,207))
if __name__=='__main__':unittest.main()
