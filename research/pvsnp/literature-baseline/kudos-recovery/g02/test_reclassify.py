import unittest,json
from pathlib import Path
from abstract_reclassify import candidate_abstract
B=Path(__file__).resolve().parents[2]
class ExistingAbstractTests(unittest.TestCase):
 def test_existing_book_field_can_be_bound_and_promoted(self):
  papers=[json.loads(l) for l in (B/'catalog/abstract-format-partition/groups/02-needs-source-mathscinet-fields-json/members.jsonl').read_text(encoding='utf-8').splitlines()]
  p=papers[1];r=json.loads((B/'kudos-recovery/g02/results'/f"{p['paper_id']}.json").read_text(encoding='utf-8'))
  a=candidate_abstract(r,p)
  self.assertIsNotNone(a)
  self.assertEqual(a['source_kind'],'database_indexing_abstract')
  self.assertEqual(a['status'],'found')
  self.assertEqual(a['wording_author_status'],'not_verified')
  other=dict(p);other['title']='A wholly unrelated book'
  self.assertIsNone(candidate_abstract(r,other))
if __name__=='__main__':unittest.main()
