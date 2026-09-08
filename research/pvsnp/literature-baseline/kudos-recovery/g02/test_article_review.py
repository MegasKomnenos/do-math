import json,unittest,copy
from pathlib import Path
from article_review import inspect_article
BASE=Path(__file__).resolve().parents[2]
PID='VER-01747868e78783cb0861b2c8'
P=next(json.loads(l) for l in (BASE/'catalog/abstract-format-partition/groups/02-needs-source-mathscinet-fields-json/members.jsonl').read_text(encoding='utf-8').splitlines() if PID in l)
PDF=BASE/'intake/kudos-recovery/g02'/PID/'fulltext-candidate-4b3b1ebfd62b66c1.pdf'
class ArticleReviewTests(unittest.TestCase):
 def test_actual_viana_identity_extent_and_abstract_boundary(self):
  value=inspect_article(P,PDF)
  self.assertEqual(value['page_count'],94);self.assertEqual(value['page_range'],[7,100]);self.assertTrue(value['abstract_text'].startswith('A uni'))
  self.assertNotIn('Key words',value['abstract_text']);self.assertEqual(len(value['abstract_bbox']),4)
 def test_received2005_is_not_publication_year(self):
  p=copy.deepcopy(P);p['year']=2005;self.assertIsNone(inspect_article(p,PDF))
 def test_wrong_doi_or_page_range_rejected(self):
  p=copy.deepcopy(P);p['identifiers']['doi']=['10.1000/different'];self.assertIsNone(inspect_article(p,PDF))
  p=copy.deepcopy(P);p['publication']['pages']=['7 99'];self.assertIsNone(inspect_article(p,PDF))
if __name__=='__main__':unittest.main()
