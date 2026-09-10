import json,sys,tempfile,unittest
from pathlib import Path
import httpx
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from scholarly import ArtifactStore,ServiceError
from api_adapters import OpenAlex

class OpenAlexContract(unittest.TestCase):
    def test_canonical_merge_redirect_is_recorded_instead_of_a_false_mismatch(self):
        def response(req):
            if req.url.path.endswith('/W42'):return httpx.Response(301,headers={'Location':'https://api.openalex.org/works/W43'})
            return httpx.Response(200,json={'id':'https://openalex.org/W43','title':'Merged'})
        result=self.adapter(response).fetch('W42',parts=['metadata'])
        self.assertEqual(result['status'],'ok');self.assertTrue(result['identity']['canonical_redirect'])
        self.assertEqual(result['identity']['requested'],'W42')

    def test_later_page_failure_keeps_the_already_received_window(self):
        def response(req):
            if req.url.params['page']=='2':return httpx.Response(429)
            return httpx.Response(200,json={'meta':{'count':10,'page':1,'per_page':2},'results':[{'id':'W0'},{'id':'W1'}]})
        adapter=self.adapter(response);result=adapter.search('proofs',options={},start=1,limit=2)
        self.assertEqual(result['status'],'partial');self.assertEqual(result['received'],1)
        self.assertEqual(result['errors'][0]['code'],'rate_limited')
        self.assertEqual(json.loads(self.store.read(result['records']['ref'])[1]),[{'id':'W1'}])

    def adapter(self,handler):
        temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup);self.store=ArtifactStore(temp.name)
        self.calls=[]
        def serve(req):self.calls.append(req);return handler(req)
        client=httpx.Client(transport=httpx.MockTransport(serve));self.addCleanup(client.close)
        return OpenAlex(self.store,client)

    def test_group_counts_are_not_work_counts_and_cursor_is_preserved(self):
        raw=json.loads((ROOT/'tests/fixtures/openalex-groups.json').read_text('utf-8'))
        adapter=self.adapter(lambda r:httpx.Response(200,json=raw))
        result=adapter.search('natural proofs',options={'group_by':'publication_year'},limit=2)
        self.assertEqual(result['records_kind'],'groups');self.assertIsNone(result['total'])
        self.assertEqual(result['matched_work_count'],raw['meta']['count'])
        self.assertEqual(result['received'],2);self.assertEqual(self.calls[0].url.params['cursor'],'*')
        self.assertEqual(result['next'],{'cursor':raw['meta']['next_cursor']})

    def test_unaligned_window_combines_native_pages_without_losing_provenance(self):
        def response(req):
            size=int(req.url.params['per_page']);page=int(req.url.params['page']);start=(page-1)*size
            return httpx.Response(200,json={'meta':{'count':10,'page':page,'per_page':size},'results':[{'id':f'https://openalex.org/W{i}'} for i in range(start,start+size)]})
        adapter=self.adapter(response)
        result=adapter.search('proofs',options={},start=1,limit=2)
        rows=json.loads(self.store.read(result['records']['ref'])[1])
        self.assertEqual([row['id'] for row in rows],['https://openalex.org/W1','https://openalex.org/W2'])
        self.assertEqual(len(result['records']['evidence_refs']),2)
        self.assertEqual(result['next'],{'start':3})

    def test_cursor_end_does_not_use_a_total_as_an_offset(self):
        adapter=self.adapter(lambda r:httpx.Response(200,json={'meta':{'count':1000,'next_cursor':None},'results':[]}))
        result=adapter.search('proofs',options={},cursor='public-test-cursor',limit=2)
        self.assertFalse(result['has_more']);self.assertIsNone(result['next'])

    def test_abstract_reconstruction_preserves_positions_and_rejects_gaps(self):
        from openalex import abstract_text
        self.assertEqual(abstract_text({'a':[0,2],'proof':[1]}),'a proof a')
        for value in [{'a':[0,2]},{'a':[0],'b':[0]},{'a':[-1]},{'a':[True]}]:
            with self.assertRaises(ServiceError):abstract_text(value)

    def test_fetch_returns_reconstructed_abstract_and_native_relationships(self):
        raw=json.loads((ROOT/'tests/fixtures/openalex-abstract.json').read_text('utf-8'))
        adapter=self.adapter(lambda r:httpx.Response(200,json=raw))
        result=adapter.fetch('https://openalex.org/works/W2741809807',parts=['metadata','abstract','supplementary'])
        self.assertEqual(result['status'],'ok')
        index=raw['abstract_inverted_index'];tokens={p:w for w,ps in index.items() for p in ps}
        actual=self.store.read(result['components']['abstract']['artifact']['ref'])[1].decode()
        self.assertEqual(actual,' '.join(tokens[i] for i in range(len(tokens))))
        self.assertEqual(result['components']['supplementary']['reference_count'],len(raw['referenced_works']))

    def test_name_selection_wrong_id_and_missing_abstract(self):
        adapter=self.adapter(lambda r:httpx.Response(200,json={'meta':{'count':1},'results':[{'id':'https://openalex.org/W42','title':'Example'}]}))
        self.assertEqual(adapter.fetch('Example theorem',parts=['metadata'])['status'],'selection_required')
        raw=json.loads((ROOT/'tests/fixtures/openalex-natural-proofs.json').read_text('utf-8'))
        adapter=self.adapter(lambda r:httpx.Response(200,json=raw))
        result=adapter.fetch('W2912080987',parts=['metadata','abstract'])
        self.assertEqual(result['components']['abstract']['status'],'not_found')
        with self.assertRaises(ServiceError):adapter.fetch('W42',parts=['metadata'])
        raw['doi']=None
        with self.assertRaises(ServiceError) as cm:adapter.fetch('10.1006/jcss.1997.1494',parts=['metadata'])
        self.assertEqual(cm.exception.result['code'],'identity_mismatch')

if __name__=='__main__':unittest.main()
