import json,unittest
from pathlib import Path
import pymupdf
from copyright_notice import matches_year
BASE=Path(__file__).resolve().parents[2]
class CopyrightNoticeTests(unittest.TestCase):
 def test_actual_publisher_named_copyright_notice(self):
  p=BASE/'intake/kudos-recovery/g02/VER-3191c2b73c67e60ee329b845/fulltext-candidate-9ea62d26f5ee89c7.pdf'
  with pymupdf.open(p) as d:front='\n'.join(d[i].get_text() for i in range(10))
  self.assertTrue(matches_year(front,2018));self.assertFalse(matches_year(front,2017))
 def test_actual_original_simple_notice_remains_valid(self):
  p=BASE/'intake/kudos-recovery/g02/VER-03d4f40f5e02f445ed375c27/fulltext-candidate-f9c35f3e50bf2881.pdf'
  with pymupdf.open(p) as d:front='\n'.join(d[i].get_text() for i in range(10))
  self.assertTrue(matches_year(front,2005));self.assertFalse(matches_year(front,2008))
 def test_unclear_multi_year_notice_is_not_automatic(self):
  self.assertFalse(matches_year('© Publisher 2010, 2018',2018))
  self.assertFalse(matches_year('© Publisher 2010\n© Publisher 2018',2018))
 def test_actual_complete_book_passes_current_integrated_rule(self):
  from pdf_review import book_match
  pid='VER-3191c2b73c67e60ee329b845';root=Path(__file__).resolve().parent;assignment=json.loads((root/'assignment.json').read_text(encoding='utf-8-sig'));p=next(json.loads(line) for line in (BASE/assignment['members_path']).read_text(encoding='utf-8').splitlines() if pid in line)
  path=BASE/'intake/kudos-recovery/g02'/pid/'fulltext-candidate-9ea62d26f5ee89c7.pdf'
  self.assertIsNotNone(book_match(p,path))
 def test_non_copyright_year_does_not_supply_copyright_proof(self):
  self.assertFalse(matches_year('Library of Congress Control Number: 2018933462\nReferences\nA source (2018).',2018))
if __name__=='__main__':unittest.main()
