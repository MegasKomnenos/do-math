import unittest,json
from pathlib import Path
import response_recovery as rr
class BatchTests(unittest.TestCase):
 def test_query_binds_both_ids(self):
  self.assertEqual(rr.batch_query([{'identifiers':{'doi':['10.1109/mcs.2008.931718']}},{'identifiers':{'doi':['10.1007/978-1-84800-998-1']}}]),'"10.1109/mcs.2008.931718" OR "10.1007/978-1-84800-998-1"')
 def test_isbn_fallback(self):
  self.assertEqual(rr.primary_identifier({'identifiers':{'doi':[],'isbn':['9781848009974']}}),'9781848009974')
 def test_truncated_batch_must_split(self):
  self.assertTrue(rr.batch_truncated({'record_count':80,'documents':[{}]*25}))
  self.assertFalse(rr.batch_truncated({'record_count':5,'documents':[{}]*5}))
if __name__=='__main__':unittest.main()
