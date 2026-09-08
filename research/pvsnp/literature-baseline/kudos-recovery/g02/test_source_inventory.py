import copy,json,unittest
from pathlib import Path
import resume
from source_kind import assess
from negative_review import unavailable_abstract
BASE=Path(__file__).resolve().parents[2]
PID='VER-2a20cc1ccaddd97f89693ecf'
P=next(json.loads(l) for l in (BASE/'catalog/abstract-format-partition/groups/02-needs-source-mathscinet-fields-json/members.jsonl').read_text(encoding='utf-8').splitlines() if PID in l)
def record():return json.loads((BASE/'kudos-recovery/g02/results'/f'{PID}.json').read_text(encoding='utf-8'))
class SourceInventoryTests(unittest.TestCase):
 def test_actual_no_electronic_resource_is_not_restriction(self):
  for name in ('source-ff1824e59f14ff1b.txt','source-54508d5cd5a5e973.txt'):
   body=(BASE/'intake/kudos-recovery/g02'/PID/name).read_text(encoding='utf-8')
   self.assertEqual(assess(body,200),'no_resource')
 def test_no_resource_cannot_establish_unavailable(self):
  r=record();r['abstract']={'status':'unresolved'};r['fulltext']={'status':'unresolved'}
  self.assertIsNone(unavailable_abstract(P,r))
  resume.close_restricted_fulltext(r)
  self.assertEqual(r['fulltext']['status'],'unresolved')
 def test_preserved_matching_cinii_uri_is_inventoried(self):
  r=record();resume.inventory(P,r)
  self.assertTrue(any(t['kind']=='source' and t['target']=='https://cir.nii.ac.jp/crid/1971430859789970822' for t in r['work_state']['tasks']))
 def test_content_links_include_lists_but_not_thumbnails(self):
  self.assertEqual(resume.document_links({'uris':['https://a.test/record'],'open_access_link':'https://b.test/paper','thumbnail_small':'https://c.test/image'}),['https://a.test/record','https://b.test/paper'])
 def test_completed_initialization_shell_is_reopened_from_preserved_evidence(self):
  import hashlib
  pid='VER-010fc459824818ec8e6bf762';p=next(json.loads(l) for l in (BASE/resume.ASSIGN['members_path']).read_text(encoding='utf-8').splitlines() if pid in l);r=resume.new_result(p)
  path='intake/kudos-recovery/g02/'+pid+'/source-2b06cf9bd926dc42-41341e76469061ea.txt';url='https://www.degruyterbrill.com/document/doi/10.1515/9783110278606.1/html'
  r['evidence']=[{'path':path,'sha256':hashlib.sha256((BASE/path).read_bytes()).hexdigest(),'url':url,'kind':'provider-page','media_type':'text/plain'}]
  t=resume.task(r,'source',url,'done',evidence_paths=[path]);resume.inventory(p,r)
  self.assertEqual(t['status'],'retry')
if __name__=='__main__':unittest.main()
