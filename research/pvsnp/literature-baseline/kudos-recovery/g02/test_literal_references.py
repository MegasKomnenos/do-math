import json,unittest
from pathlib import Path
from literal_references import in_reference_section
BASE=Path(__file__).resolve().parents[2]
BODY=(BASE/'intake/kudos-recovery/g02/VER-2e1cb56054cbb371f2e02014/source-7d44d1ff0f4e5a23-9ab7d4039b5f444c.txt').read_text(encoding='utf-8')
class LiteralReferenceTests(unittest.TestCase):
 def test_actual_direct_reference_tasks_are_closed_by_integrated_pruner(self):
  from scope_prune import prune
  r=json.loads((BASE/'intake/kudos-recovery/g02/fixtures/literal-reference-tasks-d4c6d0f16a783a20.json').read_text(encoding='utf-8'))['record'];prune(r)
  self.assertTrue(all(t['status']=='not_needed' for t in r['work_state']['tasks']))
 def test_actual_collegeboard_and_keisler_urls_belong_to_references(self):
  for url in ['https://apcentral.collegeboard.org/pdf/ap-calculus-ab-and-bc-course-and-exam-description.pdf','https://people.math.wisc.edu/~hkeisler/foundations.pdf']:
   self.assertTrue(in_reference_section(BODY,url))
 def test_same_url_outside_reference_section_is_not_excluded(self):
  url='https://target.example/full-issue.pdf'
  self.assertFalse(in_reference_section(url+'\nReferences\nAn unrelated citation.\nAuthor information\n'+url,url))
 def test_no_reference_section_does_not_establish_reference_context(self):
  self.assertFalse(in_reference_section('Download book PDF\nhttps://target.example/book.pdf','https://target.example/book.pdf'))
if __name__=='__main__':unittest.main()
