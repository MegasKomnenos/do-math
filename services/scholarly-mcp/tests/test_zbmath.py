import json,sys,tempfile,unittest
from pathlib import Path
import httpx
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scholarly import ArtifactStore,ServiceError
from api_adapters import ZBMath

class ZBMathContract(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.store=ArtifactStore(self.temp.name)
        self.record=json.loads((ROOT/'tests/fixtures/zbmath-natural-proofs.json').read_text('utf-8'))

    def adapter(self,handler):
        client=httpx.Client(transport=httpx.MockTransport(handler))
        self.addCleanup(client.close)
        return ZBMath(self.store,client)

    def test_license_notice_is_not_an_available_abstract(self):
        adapter=self.adapter(lambda request:httpx.Response(200,json={'result':self.record}))
        result=adapter.fetch('1079979',parts=['metadata','abstract','supplementary'])
        self.assertEqual(result['status'],'partial')
        self.assertEqual(result['components']['abstract']['status'],'restricted')
        self.assertEqual(result['components']['abstract']['code'],'content_license_restriction')
        self.assertEqual(result['components']['supplementary']['reference_count'],40)

    def test_review_text_keeps_its_type_and_missing_content_is_distinct(self):
        self.record['editorial_contributions']=[{'contribution_type':'review','text':'Synthetic review text','reviewer':None}]
        adapter=self.adapter(lambda request:httpx.Response(200,json={'result':self.record}))
        result=adapter.fetch('1079979',parts=['abstract'])
        self.assertEqual(result['components']['abstract']['status'],'source_page')
        self.assertEqual(result['components']['abstract']['entries'][0]['type'],'review')
        self.record['editorial_contributions']=[]
        result=adapter.fetch('1079979',parts=['abstract'])
        self.assertEqual(result['components']['abstract']['status'],'not_found')

    def test_arbitrary_window_spans_native_pages_without_dropping_rows(self):
        rows=[{'id':number,'title':{'title':str(number)}} for number in (10,11,12)]
        def respond(request):
            page=int(request.url.params['page'])
            return httpx.Response(200,json={'result':rows[page*2:page*2+2],'status':{'nr_total_results':3}})
        result=self.adapter(respond).search('test',options={},start=1,limit=2,export='native')
        selected=json.loads(self.store.read(result['records']['ref'])[1])
        self.assertEqual([row['id'] for row in selected],[11,12])
        self.assertEqual(len(result['export']['artifacts']),2)

    def test_a_different_document_response_is_not_accepted(self):
        adapter=self.adapter(lambda request:httpx.Response(200,json={'result':self.record}))
        with self.assertRaises(ServiceError) as caught:
            adapter.fetch('1079980',parts=['metadata'])
        self.assertEqual(caught.exception.result['code'],'identity_mismatch')

    def test_doi_name_and_query_style_links_resolve_without_api_knowledge(self):
        def respond(request):
            if request.url.path.endswith('_structured_search'):
                return httpx.Response(200,json={'result':[self.record],'status':{'nr_total_results':1}})
            return httpx.Response(200,json={'result':self.record})
        adapter=self.adapter(respond)
        found=adapter.fetch('10.1006/jcss.1997.1494',parts=['metadata'])
        self.assertEqual(found['identity']['zbmath_id'],1079979)
        candidates=adapter.fetch('Natural proofs',parts=['metadata'])
        self.assertEqual(candidates['status'],'selection_required')
        linked=adapter.fetch('https://zbmath.org/?q=an:0884.68055',parts=['metadata'])
        self.assertEqual(linked['status'],'ok')
        self.record['identifier']='10.68055'
        self.assertEqual(adapter.fetch('10.68055',parts=['metadata'])['status'],'ok')

if __name__=='__main__':
    unittest.main()
