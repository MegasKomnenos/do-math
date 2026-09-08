import json,unittest,copy
from pathlib import Path
import resume
ROOT=Path(__file__).resolve().parent
P={p['paper_id']:p for p in (json.loads(l) for l in (resume.BASE/resume.ASSIGN['members_path']).read_text(encoding='utf-8').splitlines())}
class ReassessTests(unittest.TestCase):
 def test_completed_actual_result_selected_only_when_explicit(self):
  r=json.loads((ROOT/'results/VER-01747868e78783cb0861b2c8.json').read_text(encoding='utf-8'))
  self.assertFalse(resume.should_process(r,False));self.assertTrue(resume.should_process(r,True))
 def test_actual_pdf_and_region_rechecked_without_losing_files(self):
  pid='VER-01747868e78783cb0861b2c8';r=json.loads((ROOT/'results'/f'{pid}.json').read_text(encoding='utf-8'));before=[a['sha256'] for c in ('abstract','fulltext') for a in r[c]['artifacts']]
  resume.reassess_saved(P[pid],r)
  self.assertEqual(before,[a['sha256'] for c in ('abstract','fulltext') for a in r[c]['artifacts']]);self.assertFalse(resume.pending_work(r))
 def test_actual_cpe_route_reopens_for_firefox(self):
  pid='VER-00c50f5444a98ca8ad72ac74';r=json.loads((ROOT/'results'/f'{pid}.json').read_text(encoding='utf-8'));r['fulltext']={'status':'unavailable','reason':'Former CPE-only scope.'}
  original='intake/kudos-recovery/g02/'+pid+'/source-bf6692403aab0a5c.txt'
  t=next(t for t in r['work_state']['tasks'] if any('source-bf6692403aab0a5c' in v for v in t.get('evidence_paths',[])))
  t.update(status='done',last_browser='chromium',evidence_paths=[original])
  resume.reopen_cpe_routes(r)
  self.assertEqual(r['fulltext']['status'],'unresolved');self.assertTrue(any(t.get('preferred_browser')=='firefox' and t['status']=='retry' for t in r['work_state']['tasks']))
if __name__=='__main__':unittest.main()
