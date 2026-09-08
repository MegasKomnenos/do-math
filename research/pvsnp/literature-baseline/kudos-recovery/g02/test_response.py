import unittest,json,copy
from pathlib import Path
import response_recovery as rr
BASE=Path(__file__).resolve().parents[2]
FX=BASE/'intake/kudos-recovery/g02/fixtures'
PAPERS=[json.loads(l) for l in (BASE/'catalog/abstract-format-partition/groups/02-needs-source-mathscinet-fields-json/members.jsonl').read_text(encoding='utf-8').splitlines()]
def load(n):return json.loads((FX/n).read_text(encoding='utf-8'))
class ResponseTests(unittest.TestCase):
 def test_actual_positive_boundary(self):
  rows=rr.select_documents(PAPERS[0],load('response-positive.json'),'10.1109/mcs.2008.931718')
  self.assertEqual(len(rows),1)
  expected=(BASE/'intake/kudos-recovery/g02/VER-00076a8018bfd0fedd6121ad/abstract.txt').read_text(encoding='utf-8')
  self.assertEqual(rows[0]['abstracts'][0]['abstract'],expected)
 def test_actual_wrong_doi_and_correct_rows(self):
  p=load('wrong-doi-candidate.json');rows=rr.select_documents(p,load('response-wrong-doi.json'),'10.1145/322217.322219')
  self.assertTrue(rows)
  self.assertTrue(all('Voronoi' in d['title'] and d['publication_years']==['1980'] for d in rows))
 def test_actual_zero(self):
  self.assertEqual(rr.select_documents(PAPERS[0],load('response-zero.json'),'g02nonexistentliteraturezzzz12345'),[])
 def test_stale_query_rejected(self):
  with self.assertRaises(ValueError):rr.select_documents(PAPERS[0],load('response-positive.json'),'another query')
 def test_wrong_scope_rejected(self):
  d=load('response-positive.json');d['query']['query_string']=d['query']['query_string'].replace('s.ho=f','s.ho=t')
  with self.assertRaises(ValueError):rr.select_documents(PAPERS[0],d,'10.1109/mcs.2008.931718')
 def test_actual_book_edition(self):
  rows=rr.select_documents(PAPERS[1],load('response-book.json'),'10.1007/978-1-84800-998-1')
  self.assertTrue(rows)
  self.assertTrue(all('2009' in d['publication_years'] for d in rows))
 def test_page_mismatch_rejected(self):
  d=load('response-positive.json');d['documents'][0]['start_pages']=['280'];d['documents'][0]['end_pages']=['930']
  self.assertEqual(rr.select_documents(PAPERS[0],d,'10.1109/mcs.2008.931718'),[])
if __name__=='__main__':unittest.main()
