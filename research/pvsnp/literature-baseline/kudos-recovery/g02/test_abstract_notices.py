import json,unittest
from pathlib import Path
from abstract_kind import classify
ROOT=Path(__file__).resolve().parent
ROWS={r['id']:r for r in json.loads((ROOT/'short-abstract-audit.json').read_text(encoding='utf-8'))}
class AbstractNoticeTests(unittest.TestCase):
 def test_actual_description_unavailable_is_placeholder(self):
  for pid in ['VER-28118f372822326d214b3bc8','VER-2a6b483f6759df2066e2d36e','VER-2b1befeee2ab850cad9d3803','VER-2e7910511dd428f5c539675e']:
   self.assertEqual(classify(ROWS[pid]['text']),'placeholder')
 def test_actual_license_only_is_not_summary(self):self.assertEqual(classify(ROWS['VER-138da0ab4751283bc036828b']['text']),'rights_notice')
 def test_actual_contributor_only_is_not_summary(self):self.assertEqual(classify(ROWS['VER-2f1e11be0e153d6c6436d9bd']['text']),'bibliographic_note')
 def test_rights_notice_appended_to_complete_summary_is_preserved(self):
  summary=ROWS['VER-0e3d2cb0861d1d48b2a79893']['text'];rights=ROWS['VER-138da0ab4751283bc036828b']['text']
  self.assertEqual(classify(summary+'\n'+rights),'database_indexing_abstract')
  self.assertEqual(classify(rights+' '+summary),'database_indexing_abstract')
 def test_actual_short_complete_summaries_are_preserved(self):
  for pid in ['VER-0b8833e7d0ecd8989c973df4','VER-0e3d2cb0861d1d48b2a79893','VER-17abcde2f0819fe3afcd984f','VER-216e7a446b03523628584349','VER-21a50dd9a1b700cea41507fa','VER-23a648e54edbf09c6d51ac26']:
   self.assertEqual(classify(ROWS[pid]['text']),'database_indexing_abstract')
 def test_directly_read_other_short_values_require_correct_disposition(self):
  expected={'VER-14a1af1b0e513554e09c472a':'table_of_contents','VER-1c64bd0484bf25d1781ed829':'review_excerpt','VER-259ba20e4b3e9571448abe6d':'bibliographic_note','VER-0eb1eebb0b265001954f6541':'unverified_formula','VER-18e7c75c197610201a71058c':'unverified_excerpt'}
  for pid,kind in expected.items():self.assertEqual(classify(ROWS[pid]['text']),kind)
if __name__=='__main__':unittest.main()
