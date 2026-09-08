import copy, json, unittest, tempfile
from pathlib import Path
from unittest.mock import patch
import run, response_recovery as rr
from test_response import PAPERS, load

class RestartTests(unittest.TestCase):
 def test_exact_bibliography_without_identifiers(self):
  p=copy.deepcopy(PAPERS[0]); d=copy.deepcopy(load('response-positive.json')['documents'][0])
  p['identifiers']={};d['dois']=[];d['isbn']=None;d['isbns']=[];d['eisbns']=[]
  self.assertTrue(rr.document_matches(p,d))
  d['publication_years']=['1900'];self.assertFalse(rr.document_matches(p,d))
 def test_stage_does_not_skip_unresolved_real_record(self):
  p=PAPERS[0]
  record=json.loads((run.ROOT/'results'/f"{p['paper_id']}.json").read_text(encoding='utf-8'));record['fulltext']={'status':'unresolved','reason':'Historical missing fulltext state reproduced.'}
  with tempfile.TemporaryDirectory() as directory:
   root=Path(directory);(root/'results').mkdir();(root/'results'/f"{p['paper_id']}.json").write_text(json.dumps(record),encoding='utf-8')
   with patch.object(run,'ROOT',root),patch.object(run,'search_ui',return_value=load('response-positive.json')),patch.object(run,'progress'),patch.object(run,'capture',return_value={}):
    rows=list(run.iter_batches(type('Page',(),{'url':'https://knu.summon.serialssolutions.com/'})(),[p]))
  self.assertEqual(len(rows),1)
 def test_batch_error_preserves_candidate_for_individual_retry(self):
  with patch.object(Path,'exists',return_value=False),patch.object(run,'search_ui',side_effect=RuntimeError('Observed UI search HTTP status 500')),patch.object(run,'progress'),patch.object(run,'store_json'):
   rows=list(run.iter_batches(None,[PAPERS[0]]))
  self.assertEqual(rows,[(PAPERS[0],None,None,None)])

if __name__=='__main__':unittest.main()
