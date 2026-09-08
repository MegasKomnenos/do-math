import json,unittest
from pathlib import Path
from pdf_review import book_match
BASE=Path(__file__).resolve().parents[2]
P={p['paper_id']:p for p in (json.loads(l) for l in (BASE/'catalog/abstract-format-partition/groups/02-needs-source-mathscinet-fields-json/members.jsonl').read_text(encoding='utf-8').splitlines())}
class PdfReviewTests(unittest.TestCase):
 def test_actual_complete_gradient_book_title_is_after_page_three(self):
  pid='VER-03d4f40f5e02f445ed375c27';path=BASE/'intake/kudos-recovery/g02'/pid/'fulltext-candidate-f9c35f3e50bf2881.pdf'
  self.assertTrue(book_match(P[pid],path))
 def test_actual_digraphs_front_and_back_matter_are_not_book(self):
  pid='VER-00108c1d6fee2df17ddd9c9d'
  for name in ['fulltext-candidate-ab6c06a129136d3b.pdf','fulltext-candidate-b4a820f8ee5ea709.pdf']:
   self.assertFalse(book_match(P[pid],BASE/'intake/kudos-recovery/g02'/pid/name))
 def test_wrong_edition_year_rejected(self):
  pid='VER-03d4f40f5e02f445ed375c27';p=dict(P[pid]);p['year']=2008
  self.assertFalse(book_match(p,BASE/'intake/kudos-recovery/g02'/pid/'fulltext-candidate-f9c35f3e50bf2881.pdf'))
if __name__=='__main__':unittest.main()
