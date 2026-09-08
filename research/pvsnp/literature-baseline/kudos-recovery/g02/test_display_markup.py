import unittest,json,copy
from pathlib import Path
import response_recovery as rr
B=Path(__file__).resolve().parents[2]
P={p['paper_id']:p for p in [json.loads(l) for l in (B/'catalog/abstract-format-partition/groups/02-needs-source-mathscinet-fields-json/members.jsonl').read_text(encoding='utf-8').splitlines()]}
class DisplayMarkupTests(unittest.TestCase):
 def test_actual_title_query_highlighting_and_isbn_binding(self):
  pid='VER-03cd01813498df81ef6faff8';d=json.loads((B/'intake/kudos-recovery/g02'/pid/'summon-response-2.json').read_text(encoding='utf-8'))
  matches=rr.select_documents(P[pid],d,d['query']['original_query'])
  self.assertTrue(matches)
  self.assertTrue(any('<mark>' in x['title'] for x in matches),'Original displayed markup remains preserved')
 def test_actual_compound_spacing(self):
  pid='VER-03ef232d85c695710c9e3ea7';d=json.loads((B/'intake/kudos-recovery/g02'/pid/'summon-response-1.json').read_text(encoding='utf-8'))
  matches=rr.select_documents(P[pid],d,d['query']['original_query'])
  self.assertTrue(matches)
  self.assertTrue(all('1981' in x['publication_years'] for x in matches))
 def test_conflicting_doi_is_not_treated_as_missing(self):
  pid='VER-03cd01813498df81ef6faff8';d=json.loads((B/'intake/kudos-recovery/g02'/pid/'summon-response-2.json').read_text(encoding='utf-8'))
  for x in d['documents']:x['dois']=['10.1000/different']
  self.assertEqual(rr.select_documents(P[pid],d,d['query']['original_query']),[])
 def test_mathml_operator_difference_is_not_erased(self):
  d=json.loads((B/'intake/kudos-recovery/g02/fixtures/mathml-response-document.json').read_text(encoding='utf-8'))
  p={'title':d['full_title'],'authors':[a['fullname'] for a in d['authors']],'year':int(d['publication_years'][0]),'record_type':'article','identifiers':{'doi':d['dois'],'isbn':[]},'publication':{}}
  changed=copy.deepcopy(d);changed['full_title']=changed['full_title'].replace('O</mml:mi>','O+</mml:mi>')
  self.assertNotEqual(changed['full_title'],d['full_title'])
  self.assertFalse(rr.document_matches(p,changed))
  captured=rr.selected_payload({'query':{},'record_count':1,'documents':[d]})
  self.assertEqual(captured['documents'][0]['full_title'],d['full_title'])
if __name__=='__main__':unittest.main()
