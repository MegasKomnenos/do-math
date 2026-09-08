import json,unittest,copy
from pathlib import Path
from mr_review import inspect_mr
BASE=Path(__file__).resolve().parents[2]
P={p['paper_id']:p for p in (json.loads(l) for l in (BASE/'catalog/abstract-format-partition/groups/02-needs-source-mathscinet-fields-json/members.jsonl').read_text(encoding='utf-8').splitlines())}
class MrReviewTests(unittest.TestCase):
 def test_actual_tsay_substantive_publisher_summary_excludes_editorial_note(self):
  pid='VER-04473799966c247455ae8aeb';body=(BASE/'intake/kudos-recovery/g02'/pid/'mathscinet-resume.txt').read_text(encoding='utf-8');v=inspect_mr(P[pid],body)
  self.assertTrue(v['abstract']);self.assertIn('realized volatility',v['abstract']);self.assertIn('ideal book for introductory courses',v['abstract']);self.assertNotIn('{For the second edition',v['abstract']);self.assertEqual(v['wording_source'],'publisher description');self.assertIn('MR2162112',v['editorial_note'])
 def test_actual_audience_only_publisher_description_stays_additional(self):
  pid='VER-01272400003b4a8ff07d9210';body=(BASE/'intake/kudos-recovery/g02'/pid/'mathscinet.txt').read_text(encoding='utf-8');v=inspect_mr(P[pid],body)
  self.assertIsNone(v['abstract']);self.assertIn('graduate students',v['additional_description'])
 def test_actual_stefan_complete_quoted_summary(self):
  pid='VER-00f0581b5f0c24dcfcc0d5b4';text=(BASE/'intake/kudos-recovery/g02'/pid/'mathscinet.txt').read_text(encoding='utf-8');v=inspect_mr(P[pid],text)
  self.assertTrue(v['identity']);self.assertTrue(v['abstract'].startswith('We present a bibliography'));self.assertIn('2528 titles',v['abstract'])
 def test_grouped_volume_identity_does_not_promote_shared_review(self):
  pid='VER-003c46a9dfd6ece2b0ecef3c';text=(BASE/'intake/kudos-recovery/g02'/pid/'mathscinet.txt').read_text(encoding='utf-8');v=inspect_mr(P[pid],text)
  self.assertTrue(v['identity']);self.assertIsNone(v['abstract']);p=copy.deepcopy(P[pid]);p['title']=p['title'].replace('vol v','vol iv');self.assertIsNone(inspect_mr(p,text))
if __name__=='__main__':unittest.main()
