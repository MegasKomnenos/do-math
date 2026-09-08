import hashlib,json,unittest
from pathlib import Path
from response_recovery import document_matches
from abstract_kind import classify

PATH=Path(__file__).resolve().parents[2]/'intake/kudos-recovery/g02/fixtures/book-review-mismatch-93fbac29fb63b565.json'

class BookReviewIdentityTests(unittest.TestCase):
 def setUp(self):
  data=PATH.read_bytes();self.assertTrue(hashlib.sha256(data).hexdigest().startswith('93fbac29fb63b565'));self.fixture=json.loads(data)
 def test_actual_book_review_does_not_identify_reviewed_book(self):
  self.assertFalse(document_matches(self.fixture['paper'],self.fixture['document']))
 def test_actual_review_notice_is_not_book_summary(self):
  text=self.fixture['document']['abstracts'][0]['abstract']
  self.assertEqual(classify(text),'review_excerpt')
 def test_mixed_book_review_and_book_tags_still_describe_review(self):
  d=self.fixture['document'];d['content_types'].append('Book')
  self.assertFalse(document_matches(self.fixture['paper'],d))
 def test_actual_book_ebook_and_chapter_types_remain_eligible(self):
  data=PATH.with_name('book-types-positive-958b6064e61edcf3.json').read_bytes()
  self.assertTrue(hashlib.sha256(data).hexdigest().startswith('958b6064e61edcf3'))
  for kind,row in json.loads(data).items():
   with self.subTest(kind=kind):self.assertTrue(document_matches(row['paper'],row['document']))
 def test_review_research_verb_does_not_disqualify_summary(self):
  self.assertEqual(classify('This paper reviews stochastic processes and derives a unified convergence theorem.'),'database_indexing_abstract')

if __name__=='__main__':unittest.main()
