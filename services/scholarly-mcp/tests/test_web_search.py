from pathlib import Path
import sys,json,tempfile,unittest
import httpx
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scholarly import ArtifactStore,ServiceError
from web_search import GeneralWeb,candidate_rows

class WebSearchContract(unittest.TestCase):
    def test_public_results_keep_styled_source_without_inventing_a_global_total(self):
        raw=(ROOT/'tests/fixtures/mwmbl.json').read_bytes()
        calls=[]
        def respond(request):
            calls.append(request)
            return httpx.Response(200,content=raw,headers={'Content-Type':'application/json'})
        with tempfile.TemporaryDirectory() as temp,httpx.Client(transport=httpx.MockTransport(respond)) as client:
            adapter=GeneralWeb(ArtifactStore(temp),client)
            result=adapter.search('natural proofs',options={},start=1,limit=1)
            self.assertEqual(calls[0].url.params['s'],'natural proofs')
            self.assertIsNone(result['total'])
            self.assertEqual(result['received'],1)
            self.assertEqual(result['returned_set_size'],len(json.loads(raw)))
            row=json.loads(adapter.store.read(result['records']['ref'])[1])[0]
            self.assertEqual(row['native'],json.loads(raw)[1])
            self.assertIn('natural',row['title'].lower())

    def test_empty_result_is_distinct_from_malformed_provider_content(self):
        self.assertEqual(candidate_rows([]),[])
        for raw in ({'error':'bad'},[{'url':'javascript:bad','title':[]}],[{'url':'https://example.org','title':[{'value':None}]}]):
            with self.assertRaises(ServiceError):
                candidate_rows(raw)

if __name__=='__main__':
    unittest.main()
