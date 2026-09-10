import json,sys,tempfile,unittest
from pathlib import Path
import httpx
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from scholarly import ArtifactStore,ServiceError
from api_adapters import SemanticScholar

class SemanticScholarContract(unittest.TestCase):
    def test_name_hyphens_are_adapted_but_explicit_queries_stay_literal(self):
        row=self.record()
        adapter=self.adapter(lambda r:httpx.Response(200,json={'offset':0,'total':1,'data':[row]}))
        result=adapter.fetch('Fine-Grained theorem',parts=['metadata'])
        self.assertEqual(self.calls[-1].url.params['query'],'Fine Grained theorem')
        self.assertEqual(result['requested_target'],'Fine-Grained theorem')
        adapter.search('Fine-Grained theorem',options={},limit=1)
        self.assertEqual(self.calls[-1].url.params['query'],'Fine-Grained theorem')

    def test_invalid_native_bibtex_is_preserved_as_an_error_not_rewritten(self):
        row=self.record();row['citationStyles']={'bibtex':"@['JournalArticle', 'Conference']{key, title={Example}}"}
        adapter=self.adapter(lambda r:httpx.Response(200,json={'offset':0,'total':1,'data':[row]}))
        result=adapter.search('proofs',options={},limit=1,export='bibtex')
        self.assertEqual(result['status'],'partial')
        self.assertEqual(len(result['export']['errors']),1)
        artifact=result['export']['errors'][0]['source_export']
        self.assertEqual(self.store.read(artifact['ref'])[1],row['citationStyles']['bibtex'].encode())

    def test_references_cross_pages_and_keep_the_reported_count(self):
        row=self.record();row['referenceCount']=2
        def response(req):
            if req.url.path.endswith('/references'):
                offset=int(req.url.params['offset'])
                return httpx.Response(200,json={'offset':offset,**({'next':1} if offset==0 else {}),'data':[{'citedPaper':{'paperId':None,'title':'Reference '+str(offset)}}]})
            return httpx.Response(200,json=row)
        result=self.adapter(response).fetch(row['paperId'],parts=['supplementary'])
        self.assertEqual(result['status'],'ok')
        self.assertEqual(result['components']['supplementary']['reference_count'],2)
        self.assertTrue(result['components']['supplementary']['complete'])

    def adapter(self,handler):
        temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup);self.store=ArtifactStore(temp.name);self.calls=[]
        def serve(req):self.calls.append(req);return handler(req)
        client=httpx.Client(transport=httpx.MockTransport(serve));self.addCleanup(client.close)
        adapter=SemanticScholar(self.store,client);adapter.min_interval=0;return adapter

    def record(self):return json.loads((ROOT/'tests/fixtures/semantic-scholar-public-record.json').read_text('utf-8'))

    def test_public_paper_url_and_metadata_do_not_fetch_unrequested_graphs(self):
        row=self.record();adapter=self.adapter(lambda r:httpx.Response(200,json=row))
        result=adapter.fetch(row['url'],parts=['metadata','abstract'])
        self.assertEqual(result['status'],'ok')
        fields=self.calls[0].url.params['fields'].split(',')
        self.assertNotIn('references',fields);self.assertNotIn('citations',fields)
        self.assertEqual(result['identity']['paper_id'],row['paperId'])

    def test_flag_filter_does_not_turn_false_into_a_presence_filter(self):
        row=self.record()
        for value in [False,True]:
            adapter=self.adapter(lambda r:httpx.Response(200,json={'offset':0,'total':1,'data':[row]}))
            adapter.search('proofs',options={'openAccessPdf':value},limit=1)
            self.assertEqual('openAccessPdf' in self.calls[0].url.params,value)
            if value:self.assertEqual(self.calls[0].url.params['openAccessPdf'],'')

    def test_relation_search_uses_native_offset_next_and_missing_paper_ids(self):
        row={'citedPaper':{'paperId':None,'title':'Unmatched citation'},'contexts':['Context'],'intents':['background']}
        adapter=self.adapter(lambda r:httpx.Response(200,json={'offset':3,'next':4,'data':[row]}))
        result=adapter.search('a'*40,options={'kind':'references'},start=3,limit=1)
        self.assertEqual(result['records_kind'],'references');self.assertEqual(result['next'],{'start':4})
        self.assertEqual(json.loads(self.store.read(result['records']['ref'])[1]),[row])
        self.assertTrue(self.calls[0].url.path.endswith('/references'))

    def test_wrong_identity_and_offset_are_rejected(self):
        row=self.record();adapter=self.adapter(lambda r:httpx.Response(200,json=row))
        with self.assertRaises(ServiceError):adapter.fetch('a'*40,parts=['metadata'])
        adapter=self.adapter(lambda r:httpx.Response(200,json={'offset':0,'data':[]}))
        with self.assertRaises(ServiceError):adapter.search('a'*40,options={'kind':'citations'},start=3,limit=1)

    def test_native_bibtex_is_preserved_and_name_lookup_returns_candidates(self):
        row=self.record();row['citationStyles']={'bibtex':'@article{sample, title={Example}, year={2026}}'}
        adapter=self.adapter(lambda r:httpx.Response(200,json={'offset':0,'total':1,'data':[row]}))
        found=adapter.search('proofs',options={},limit=1,export='bibtex')
        self.assertEqual(found['export']['media_type'],'application/x-bibtex')
        self.assertEqual(self.store.read(found['export']['ref'])[1],row['citationStyles']['bibtex'].encode())
        self.assertEqual(adapter.fetch('Example theorem',parts=['metadata'])['status'],'selection_required')

    def test_reference_failure_keeps_metadata_and_reported_counts(self):
        row=self.record();row['referenceCount']=12;row['citationCount']=3
        def response(req):
            if req.url.path.endswith('/references'):return httpx.Response(429)
            return httpx.Response(200,json=row)
        adapter=self.adapter(response);result=adapter.fetch(row['paperId'],parts=['metadata','supplementary'])
        self.assertEqual(result['components']['metadata']['status'],'available')
        self.assertEqual(result['components']['supplementary']['status'],'partial')
        self.assertEqual(result['components']['supplementary']['reported_reference_count'],12)
        self.assertEqual(result['components']['supplementary']['errors'][0]['code'],'rate_limited')
        self.assertEqual(len(self.calls),2)

if __name__=='__main__':unittest.main()
