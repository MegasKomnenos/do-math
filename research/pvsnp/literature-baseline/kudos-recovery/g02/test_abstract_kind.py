import unittest,json
from pathlib import Path
from abstract_kind import classify
FX=Path(__file__).resolve().parents[2]/'intake/kudos-recovery/g02/fixtures'
class AbstractKindTests(unittest.TestCase):
 def test_audience_only_is_not_an_abstract_but_content_with_audience_is(self):
  self.assertEqual(classify('This book is of interest to graduate students and researchers interested in turbulent dynamical systems.'),'audience_only')
  self.assertEqual(classify('This book presents spectral methods for partial differential equations. It is of interest to graduate students.'),'database_indexing_abstract')
 def test_actual_endorsement_is_not_database_abstract(self):
  payload=json.loads((FX.parent/'_batches/resume-7c8e13b0a45e5278.json').read_text(encoding='utf-8'))
  d=next(d for d in payload['documents'] if d['title']=='Computational Fluid Mechanics and Heat Transfer')
  self.assertEqual(classify(d['abstracts'][0]['abstract']),'review_excerpt')
  self.assertEqual(classify(d['abstracts'][2]['abstract']),'database_indexing_abstract')
 def test_actual_gradient_flows_corrupted_glyphs_require_review(self):
  path=FX.parent/'VER-03d4f40f5e02f445ed375c27/database-abstract.txt'
  self.assertEqual(classify(path.read_text(encoding='utf-8')),'damaged_text')
 def test_complete_database_book_abstract(self):
  d=json.loads((FX/'response-book.json').read_text(encoding='utf-8'))['documents'][0]
  self.assertEqual(classify(d['abstracts'][0]['abstract']),'database_indexing_abstract')
 def test_actual_other_paper_citation(self):
  self.assertEqual(classify((FX/'citation-in-abstract-field.txt').read_text(encoding='utf-8')),'bibliographic_citation')
 def test_actual_book_review_excerpt(self):
  self.assertEqual(classify((FX/'book-review-excerpt.txt').read_text(encoding='utf-8')),'review_excerpt')
 def test_visible_snippet_is_incomplete(self):
  lines=(FX/'summon-first.txt').read_text(encoding='utf-8').splitlines()
  text=next(s for s in lines if s.startswith('Robust stability') and s.endswith('...'))
  self.assertEqual(classify(text),'truncated_snippet')
 def test_actual_contents_field(self):
  self.assertEqual(classify((FX/'contents-in-abstract-field.txt').read_text(encoding='utf-8')),'table_of_contents')
 def test_placeholder(self):
  self.assertEqual(classify('No abstract available'),'placeholder')
if __name__=='__main__':unittest.main()
