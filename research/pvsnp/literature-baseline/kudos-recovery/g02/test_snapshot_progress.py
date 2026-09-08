import unittest
from snapshot_progress import summarize
class SnapshotTests(unittest.TestCase):
 def record(self,pid):return {'paper_id':pid,'identity':{'status':'confirmed'},'abstract':{'status':'unresolved'},'fulltext':{'status':'unresolved'}}
 def test_duplicate_observation_of_same_result_counts_once(self):
  r=self.record('a');s=summarize([r,r],{'a','b','c'})
  self.assertEqual(s['processed'],1);self.assertEqual(s['unprocessed'],2);self.assertEqual(s['saved_with_remaining_work'],1);self.assertEqual(s['total_remaining_papers'],3)
 def test_conflicting_same_id_does_not_silently_overwrite(self):
  a=self.record('a');b=self.record('a');b['abstract']['status']='found'
  with self.assertRaises(ValueError):summarize([a,b],{'a'})
 def test_other_assignment_id_is_rejected(self):
  with self.assertRaises(ValueError):summarize([self.record('other')],{'a'})
if __name__=='__main__':unittest.main()
