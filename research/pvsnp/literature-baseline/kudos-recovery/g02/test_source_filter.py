import json,unittest
from pathlib import Path
from resume import fulltext_links
ROOT=Path(__file__).resolve().parent
class SourceFilterTests(unittest.TestCase):
 def test_actual_cambridge_cited_by_export_is_not_fulltext(self):
  r=json.loads((ROOT/'results/VER-0113c4f0d3bbf906515157e1.json').read_text(encoding='utf-8'))
  url=next(t['target'] for t in r['work_state']['tasks'] if '/download/cited-by' in t['target'])
  self.assertEqual(fulltext_links([{'text':'Download','url':url}]),[])
 def test_article_navigation_is_a_source(self):
  self.assertEqual(len(fulltext_links([{'text':'Article','url':'https://example.org/item/1'}])),1)
 def test_review_article_title_is_not_review_pdf_metadata(self):
  self.assertEqual(len(fulltext_links([{'text':'A review of interval exchange maps','url':'https://example.org/article.pdf'}])),1)
if __name__=='__main__':unittest.main()
