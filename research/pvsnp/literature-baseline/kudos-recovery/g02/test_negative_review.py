import copy,json,unittest
from pathlib import Path
import resume
from negative_review import unavailable_abstract
BASE=Path(__file__).resolve().parents[2]
PID='VER-0050b48c4a1a304c1f05eafb'
P=next(json.loads(l) for l in (BASE/'catalog/abstract-format-partition/groups/02-needs-source-mathscinet-fields-json/members.jsonl').read_text(encoding='utf-8').splitlines() if PID in l)
def record():return json.loads((BASE/'kudos-recovery/g02/results'/f'{PID}.json').read_text(encoding='utf-8'))
class NegativeReviewTests(unittest.TestCase):
 def test_actual_no_resource_scope_is_not_independent_restriction_evidence(self):
  r=record();r['fulltext']={'status':'unresolved','reason':'Do not derive abstract status from fulltext status.'}
  result=unavailable_abstract(P,r)
  self.assertIsNone(result)
 def test_unvisited_source_stays_unresolved(self):
  r=record();resume.task(r,'source','https://example.org/unvisited');self.assertIsNone(unavailable_abstract(P,r))
 def test_unread_abstract_candidate_stays_unresolved(self):
  r=record();r['abstract_candidates']=[{'text':'A corresponding candidate still requires direct reading.','status':'needs_review'}];self.assertIsNone(unavailable_abstract(P,r))
 def test_found_abstract_is_preserved(self):
  r=record();r['abstract']={'status':'found','artifacts':[{'path':'fixture'}]};self.assertIsNone(unavailable_abstract(P,r))
if __name__=='__main__':unittest.main()
