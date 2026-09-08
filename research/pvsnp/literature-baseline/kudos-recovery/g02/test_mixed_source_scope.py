import json,unittest
from pathlib import Path
from mixed_source_scope import restricted_fulltext_evidence
ROOT=Path(__file__).resolve().parent
class MixedScopeTests(unittest.TestCase):
 def record(self,pid):return json.loads((ROOT/'results'/f'{pid}.json').read_text(encoding='utf-8'))
 def test_actual_publisher_restriction_and_empty_resolvers_have_distinct_roles(self):
  r=self.record('VER-03e396105a7113c55bf29584');result=restricted_fulltext_evidence(r)
  self.assertTrue(result);self.assertTrue(result['restriction_evidence_paths']);self.assertTrue(result['no_resource_evidence_paths'])
 def test_actual_no_resource_only_does_not_establish_restriction(self):
  r=self.record('VER-0050b48c4a1a304c1f05eafb');self.assertIsNone(restricted_fulltext_evidence(r))
 def test_unvisited_uri_stays_open(self):
  r=self.record('VER-03e396105a7113c55bf29584');r['work_state']['tasks'].append({'kind':'source','target':'https://example.org/unvisited','status':'pending'});self.assertIsNone(restricted_fulltext_evidence(r))
 def test_unread_pdf_stays_open(self):
  r=self.record('VER-03e396105a7113c55bf29584');r['fulltext_candidates'][0]['status']='needs_review';self.assertIsNone(restricted_fulltext_evidence(r))
if __name__=='__main__':unittest.main()
