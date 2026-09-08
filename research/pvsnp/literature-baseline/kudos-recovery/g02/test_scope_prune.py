import json,unittest
from pathlib import Path
from scope_prune import prune
ROOT=Path(__file__).resolve().parent
class PruneTests(unittest.TestCase):
 def test_cpe_recheck_does_not_read_excluded_branch_evidence(self):
  import resume
  from unittest.mock import patch
  r=json.loads((ROOT/'results/VER-2f57a70bf9fdaa234cee4a31.json').read_text(encoding='utf-8'));r['work_state']['tasks']=[t for t in r['work_state']['tasks'] if t.get('scope_relation')=='unrelated']
  with patch.object(resume,'valid_bytes',side_effect=AssertionError('Unrelated evidence must not be reread')):resume.reopen_cpe_routes(r)
 def test_reapplying_scope_repair_does_not_treat_parent_proof_as_child_output(self):
  import copy
  r=json.loads((ROOT/'results/VER-2f57a70bf9fdaa234cee4a31.json').read_text(encoding='utf-8'));child=copy.deepcopy(next(t for t in r['work_state']['tasks'] if '10511970.2015.1047545' in t['target']));origin=child['discovered_from'];child['evidence_paths']=[p for p in child.get('evidence_paths',[]) if p!=origin];child.pop('scope_relation',None);child['status']='done'
  legitimate={'key':'pdf:fixture-legitimate-control','kind':'pdf','target':'https://target.example/observed.pdf','status':'pending','discovered_from':origin}
  r['work_state']['tasks']=[child,legitimate];r['fulltext_candidates']=[];r['abstract_candidates']=[]
  prune(r);self.assertEqual(legitimate['status'],'pending');prune(r);self.assertEqual(legitimate['status'],'pending')
 def test_actual_wiley_reference_linkouts_close_without_losing_book_chapters(self):
  r=json.loads((ROOT/'results/VER-04473799966c247455ae8aeb.json').read_text(encoding='utf-8'));prune(r)
  refs=[t for t in r['work_state']['tasks'] if 'linkLocation=Reference' in t['target']];self.assertTrue(refs);self.assertTrue(all(t['status']=='not_needed' for t in refs))
  own=[t for t in r['work_state']['tasks'] if '.ch12' in t['target'] and 'linkLocation' not in t['target'] and t['kind']=='pdf'];self.assertTrue(own);self.assertTrue(all(t.get('scope_relation')!='unrelated' for t in own))
 def test_resume_inventory_applies_scope_repair(self):
  import resume
  pid='VER-2f57a70bf9fdaa234cee4a31';r=json.loads((ROOT/'results'/f'{pid}.json').read_text(encoding='utf-8'));p=next(json.loads(line) for line in (resume.BASE/resume.ASSIGN['members_path']).read_text(encoding='utf-8').splitlines() if pid in line)
  resume.inventory(p,r)
  self.assertTrue(all(t['status']=='not_needed' for t in r['work_state']['tasks'] if 'europepmc.org/ftp/' in t['target']))
 def test_actual_ftp_descendants_close_but_assigned_sources_remain(self):
  r=json.loads((ROOT/'results/VER-2f57a70bf9fdaa234cee4a31.json').read_text(encoding='utf-8'));prune(r)
  ftp=[t for t in r['work_state']['tasks'] if 'europepmc.org/ftp/' in t['target']]
  self.assertTrue(ftp);self.assertTrue(all(t['status']=='not_needed' for t in ftp))
  target=next(t for t in r['work_state']['tasks'] if t['target']=='https://doi.org/10.1007/978-3-031-81217-0_5');self.assertNotEqual(target.get('scope_relation'),'unrelated')
 def test_actual_perlego_related_products_close_but_input_book_remains(self):
  r=json.loads((ROOT/'results/VER-2f0b8d4978e9dd62408de031.json').read_text(encoding='utf-8'));prune(r)
  related=next(t for t in r['work_state']['tasks'] if '/book/112829/' in t['target']);self.assertEqual(related['status'],'not_needed')
  target=next(t for t in r['work_state']['tasks'] if t['kind']=='source' and '/book/737286/' in t['target']);self.assertNotEqual(target.get('scope_relation'),'unrelated')
if __name__=='__main__':unittest.main()
