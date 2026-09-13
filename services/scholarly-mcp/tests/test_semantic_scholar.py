import json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
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
            return httpx.Response(200,json=[row])
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
        row=self.record();adapter=self.adapter(lambda r:httpx.Response(200,json=[row]))
        result=adapter.fetch(row['url'],parts=['metadata','abstract'])
        self.assertEqual(result['status'],'ok')
        fields=self.calls[0].url.params['fields'].split(',')
        self.assertNotIn('references',fields);self.assertNotIn('citations',fields)
        self.assertEqual(result['identity']['paper_id'],row['paperId'])

    def test_fetch_uses_documented_one_id_batch_route(self):
        row=self.record()
        def response(req):
            if req.url.path.endswith('/paper/batch'):
                self.assertEqual(req.method,'POST')
                self.assertEqual(json.loads(req.content),{'ids':[row['paperId']]})
                return httpx.Response(200,json=[row])
            return httpx.Response(429)
        adapter=self.adapter(response)
        result=adapter.fetch(row['paperId'],parts=['metadata','abstract'])
        self.assertEqual(result['status'],'ok')
        self.assertTrue(self.calls[0].url.path.endswith('/paper/batch'))
        self.assertEqual(result['identity']['paper_id'],row['paperId'])

    def test_export_only_batch_requests_only_identity_and_citation_fields(self):
        row=self.record();row['citationStyles']={'bibtex':'@article{sample, title={'+row['title']+'}, year={2026}}'}
        adapter=self.adapter(lambda req:httpx.Response(200,json=[row]))
        with patch('semantic_scholar.bibliography',return_value=[{'id':'sample','title':row['title']}]):
            result=adapter.fetch(row['paperId'],parts=['export'])
        fields=set(self.calls[0].url.params['fields'].split(','))
        self.assertEqual(fields,{'title','externalIds','corpusId','citationStyles'})
        self.assertEqual(result['status'],'ok')
        self.assertEqual(result['components']['export']['media_type'],'application/x-bibtex')

    def test_native_bibtex_without_doi_must_match_the_paper_title(self):
        row=self.record();row['citationStyles']={'bibtex':'@article{sample, title={Another Paper}, year={2026}}'}
        adapter=self.adapter(lambda req:httpx.Response(200,json=[row]))
        with patch('semantic_scholar.bibliography',return_value=[{'id':'sample','title':'Another Paper'}]):
            result=adapter.fetch(row['paperId'],parts=['export'])
        self.assertEqual(result['status'],'partial')
        self.assertEqual(result['components']['export']['errors'][0]['code'],'identity_mismatch')
        self.assertEqual(self.store.read(result['components']['export']['errors'][0]['source_export']['ref'])[1],row['citationStyles']['bibtex'].encode())

    def test_name_lookup_uses_documented_title_match_route(self):
        row=self.record();row['matchScore']=232.7
        def response(req):
            if req.url.path.endswith('/paper/search/match'):
                self.assertEqual(set(req.url.params['fields'].split(',')),
                    {'title','authors','year','externalIds','url','corpusId'})
                return httpx.Response(200,json={'data':[row]})
            return httpx.Response(429)
        adapter=self.adapter(response)
        result=adapter.fetch(row['title'],parts=['metadata'])
        self.assertEqual(result['status'],'selection_required')
        self.assertTrue(self.calls[0].url.path.endswith('/paper/search/match'))
        self.assertEqual(json.loads(self.store.read(result['records']['ref'])[1]),[row])
        self.assertEqual(result['requested_target'],row['title'])

    def test_bulk_search_uses_native_token_and_keeps_distinct_semantics(self):
        row=self.record();next_row={**row,'paperId':'b'*40,'title':'Next result'}
        def response(req):
            self.assertTrue(req.url.path.endswith('/paper/search/bulk'))
            self.assertEqual(req.url.params['query'],'quantum natural proofs')
            self.assertEqual(req.url.params['sort'],'citationCount:desc')
            if req.url.params.get('token'):
                self.assertEqual(req.url.params['token'],'next-page')
                return httpx.Response(200,json={'total':2,'data':[next_row]})
            self.assertNotIn('offset',req.url.params)
            return httpx.Response(200,json={'total':2,'token':'next-page','data':[row]})
        adapter=self.adapter(response)
        first=adapter.search('quantum natural proofs',options={'kind':'bulk','sort':'citationCount:desc'},limit=1000)
        self.assertEqual(first['records_kind'],'bulk')
        self.assertTrue(first['next']['cursor'].startswith('scholarly://artifact/'))
        second=adapter.search('quantum natural proofs',options={'kind':'bulk','sort':'citationCount:desc'},limit=1,cursor=first['next']['cursor'])
        self.assertFalse(second['has_more'])
        self.assertEqual(len(self.calls),2)

    def test_bulk_caller_window_preserves_the_unreturned_native_page(self):
        first=self.record();second={**first,'paperId':'b'*40,'title':'Second result'}
        adapter=self.adapter(lambda req:httpx.Response(200,json={'total':1,'data':[first,second]}))
        page1=adapter.search('natural AND proofs',options={'kind':'bulk'},limit=1)
        self.assertNotIn('limit',self.calls[0].url.params)
        self.assertEqual(json.loads(self.store.read(page1['records']['ref'])[1]),[first])
        self.assertTrue(page1['total_is_estimate'])
        page2=adapter.search('natural AND proofs',options={'kind':'bulk'},limit=1,cursor=page1['next']['cursor'])
        self.assertEqual(json.loads(self.store.read(page2['records']['ref'])[1]),[second])
        self.assertFalse(page2['has_more'])
        self.assertEqual(len(self.calls),1)

    def test_bulk_finishes_local_remainder_before_requesting_next_native_token(self):
        rows=[{**self.record(),'paperId':letter*40,'title':'Result '+letter} for letter in ('a','b','c')]
        def response(req):
            self.assertNotIn('limit',req.url.params)
            if req.url.params.get('token'):
                self.assertEqual(req.url.params['token'],'native-next')
                return httpx.Response(200,json={'total':3,'data':[rows[2]]})
            return httpx.Response(200,json={'total':3,'token':'native-next','data':rows[:2]})
        adapter=self.adapter(response)
        page1=adapter.search('natural AND proofs',options={'kind':'bulk'},limit=1)
        page2=adapter.search('natural AND proofs',options={'kind':'bulk'},limit=1,cursor=page1['next']['cursor'])
        self.assertEqual(len(self.calls),1)
        page3=adapter.search('natural AND proofs',options={'kind':'bulk'},limit=1,cursor=page2['next']['cursor'])
        observed=[json.loads(self.store.read(page['records']['ref'])[1])[0]['paperId'] for page in (page1,page2,page3)]
        self.assertEqual(observed,[row['paperId'] for row in rows])
        self.assertEqual(len(self.calls),2)
        self.assertFalse(page3['has_more'])

    def test_bulk_cursor_is_bound_to_query_options_and_export(self):
        rows=[self.record(),{**self.record(),'paperId':'b'*40}]
        adapter=self.adapter(lambda req:httpx.Response(200,json={'total':2,'data':rows}))
        first=adapter.search('natural AND proofs',options={'kind':'bulk','sort':'paperId:asc'},limit=1)
        cursor=first['next']['cursor']
        for query,options,export in [
            ('another query',{'kind':'bulk','sort':'paperId:asc'},None),
            ('natural AND proofs',{'kind':'bulk','sort':'paperId:desc'},None),
            ('natural AND proofs',{'kind':'bulk','sort':'paperId:asc','fields':'title'},None),
            ('natural AND proofs',{'kind':'bulk','sort':'paperId:asc'},'bibtex'),
        ]:
            with self.assertRaises(ServiceError) as raised:
                adapter.search(query,options=options,limit=1,cursor=cursor,export=export)
            self.assertEqual(raised.exception.result['code'],'invalid_cursor')
        foreign=self.store.put(b'{}','application/json','dblp','https://dblp.org/',role='provider_response')['ref']
        for invalid in [foreign,'scholarly://artifact/not-a-valid-reference','unbound-native-token']:
            with self.subTest(cursor=invalid), self.assertRaises(ServiceError) as raised:
                adapter.search('natural AND proofs',options={'kind':'bulk','sort':'paperId:asc'},limit=1,cursor=invalid)
            self.assertEqual(raised.exception.result['code'],'invalid_cursor')
        with self.assertRaises(ServiceError) as raised:
            adapter.search('natural AND proofs',options={'kind':'bulk','sort':'paperId:asc'},start=1,limit=1,cursor=cursor)
        self.assertEqual(raised.exception.result['code'],'invalid_range')
        self.assertEqual(len(self.calls),1)

    def test_bulk_rejects_a_repeated_native_page(self):
        row=self.record()
        def response(req):
            return httpx.Response(200,json={'total':2,'token':'second' if req.url.params.get('token') else 'first','data':[row]})
        adapter=self.adapter(response)
        first=adapter.search('natural AND proofs',options={'kind':'bulk'},limit=1)
        with self.assertRaises(ServiceError) as raised:
            adapter.search('natural AND proofs',options={'kind':'bulk'},limit=1,cursor=first['next']['cursor'])
        self.assertEqual(raised.exception.result['code'],'inconsistent_pagination')

    def test_bulk_requires_a_valid_paper_id_and_rejects_page_duplicates(self):
        valid=self.record()
        for rows in [
            [{**valid,'paperId':None}],
            [{**valid,'paperId':'not-a-paper-id'}],
            [valid,{**valid}],
        ]:
            with self.subTest(rows=rows):
                adapter=self.adapter(lambda req,rows=rows:httpx.Response(200,json={'total':len(rows),'data':rows}))
                with self.assertRaises(ServiceError) as raised:
                    adapter.search('natural AND proofs',options={'kind':'bulk'},limit=1000)
                self.assertIn(raised.exception.result['code'],('invalid_response','inconsistent_pagination'))

    def test_bulk_rejects_a_partial_id_overlap_between_native_pages(self):
        rows=[{**self.record(),'paperId':letter*40,'title':'Result '+letter} for letter in ('a','b','c')]
        def response(req):
            page=rows[1:] if req.url.params.get('token') else rows[:2]
            return httpx.Response(200,json={'total':3,**({} if req.url.params.get('token') else {'token':'next'}),'data':page})
        adapter=self.adapter(response)
        first=adapter.search('natural AND proofs',options={'kind':'bulk'},limit=2)
        with self.assertRaises(ServiceError) as raised:
            adapter.search('natural AND proofs',options={'kind':'bulk'},limit=2,cursor=first['next']['cursor'])
        self.assertEqual(raised.exception.result['code'],'inconsistent_pagination')

    def test_bulk_local_windows_share_one_page_history_without_copying_ids_into_cursors(self):
        rows=[{**self.record(),'paperId':f'{index:040x}','title':f'Result {index}'} for index in range(1000)]
        adapter=self.adapter(lambda req:httpx.Response(200,json={'total':2000,'token':'next','data':rows}))
        cursors=[]
        for limit in (1,998,1):
            page=adapter.search('natural AND proofs',options={'kind':'bulk'},limit=limit,
                **({'cursor':cursors[-1]} if cursors else {}))
            cursors.append(page['next']['cursor'])
        states=[json.loads(self.store.read(cursor)[1]) for cursor in cursors]
        self.assertEqual(len({state['history_ref'] for state in states}),1)
        self.assertTrue(all('paper_ids' not in state for state in states))
        history=json.loads(self.store.read(states[0]['history_ref'])[1])
        self.assertEqual(len(history['paper_ids']),1000)
        self.assertIsNone(history['parent'])
        self.assertEqual(len(self.calls),1)

    def test_bulk_history_cache_makes_sequential_page_processing_linear(self):
        from semantic_scholar import _read_bulk_history
        rows=[{**self.record(),'paperId':letter*40,'title':'Result '+letter} for letter in ('a','b','c')]
        def response(req):
            token=req.url.params.get('token')
            if token=='second':return httpx.Response(200,json={'total':3,'data':[rows[2]]})
            if token=='first':return httpx.Response(200,json={'total':3,'token':'second','data':[rows[1]]})
            return httpx.Response(200,json={'total':3,'token':'first','data':[rows[0]]})
        adapter=self.adapter(response)
        with patch('semantic_scholar._read_bulk_history',wraps=_read_bulk_history) as read_history:
            page=adapter.search('natural AND proofs',options={'kind':'bulk'},limit=1)
            page=adapter.search('natural AND proofs',options={'kind':'bulk'},limit=1,cursor=page['next']['cursor'])
            page=adapter.search('natural AND proofs',options={'kind':'bulk'},limit=1,cursor=page['next']['cursor'])
        self.assertEqual(read_history.call_count,0)
        self.assertFalse(page['has_more'])
        self.assertFalse(hasattr(adapter,'_bulk_history_cache'))

    def test_bulk_history_cache_rebuilds_for_resume_and_branch_without_error_pollution(self):
        from semantic_scholar import _read_bulk_history
        rows=[{**self.record(),'paperId':letter*40,'title':'Result '+letter} for letter in ('a','b','c')]
        overlap=False
        def response(req):
            token=req.url.params.get('token')
            if token=='second':return httpx.Response(200,json={'total':3,'data':[rows[2]]})
            if token=='first':return httpx.Response(200,json={'total':3,'token':'second','data':[rows[0] if overlap else rows[1]]})
            return httpx.Response(200,json={'total':3,'token':'first','data':[rows[0]]})
        adapter=self.adapter(response)
        page1=adapter.search('natural AND proofs',options={'kind':'bulk'},limit=1)
        page2=adapter.search('natural AND proofs',options={'kind':'bulk'},limit=1,cursor=page1['next']['cursor'])
        self.assertIsNotNone(getattr(adapter,'_bulk_history_cache',None))

        resumed=SemanticScholar(self.store,httpx.Client(transport=httpx.MockTransport(response)));resumed.min_interval=0
        self.addCleanup(resumed.client.close)
        with patch('semantic_scholar._read_bulk_history',wraps=_read_bulk_history) as read_history:
            final=resumed.search('natural AND proofs',options={'kind':'bulk'},limit=1,cursor=page2['next']['cursor'])
        self.assertEqual(read_history.call_count,1)
        self.assertFalse(final['has_more'])

        with patch('semantic_scholar._read_bulk_history',wraps=_read_bulk_history) as read_history:
            branch=adapter.search('natural AND proofs',options={'kind':'bulk'},limit=1,cursor=page1['next']['cursor'])
        self.assertEqual(read_history.call_count,1)
        self.assertTrue(branch['has_more'])
        cached_before=getattr(adapter,'_bulk_history_cache',None)
        overlap=True
        with self.assertRaises(ServiceError), patch('semantic_scholar._read_bulk_history',wraps=_read_bulk_history) as read_history:
            adapter.search('natural AND proofs',options={'kind':'bulk'},limit=1,cursor=page1['next']['cursor'])
        self.assertEqual(read_history.call_count,1)
        self.assertEqual(getattr(adapter,'_bulk_history_cache',None),cached_before)
        overlap=False
        retry=adapter.search('natural AND proofs',options={'kind':'bulk'},limit=1,cursor=page1['next']['cursor'])
        self.assertTrue(retry['has_more'])

    def test_bulk_rejects_an_empty_intermediate_native_page(self):
        row=self.record()
        def response(req):
            if req.url.params.get('token'):
                return httpx.Response(200,json={'total':2,'token':'again','data':[]})
            return httpx.Response(200,json={'total':2,'token':'next','data':[row]})
        adapter=self.adapter(response)
        first=adapter.search('natural AND proofs',options={'kind':'bulk'},limit=1)
        with self.assertRaises(ServiceError) as raised:
            adapter.search('natural AND proofs',options={'kind':'bulk'},limit=1,cursor=first['next']['cursor'])
        self.assertEqual(raised.exception.result['code'],'incomplete_response')

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
        row=self.record();adapter=self.adapter(lambda r:httpx.Response(200,json=[row]))
        with self.assertRaises(ServiceError):adapter.fetch('a'*40,parts=['metadata'])
        adapter=self.adapter(lambda r:httpx.Response(200,json={'offset':0,'data':[]}))
        with self.assertRaises(ServiceError):adapter.search('a'*40,options={'kind':'citations'},start=3,limit=1)

    def test_native_bibtex_is_preserved_and_name_lookup_returns_candidates(self):
        row=self.record();row['citationStyles']={'bibtex':'@article{sample, title={'+row['title']+'}, year={2026}}'}
        adapter=self.adapter(lambda r:httpx.Response(200,json={'offset':0,'total':1,'data':[row]}))
        found=adapter.search('proofs',options={},limit=1,export='bibtex')
        self.assertEqual(found['export']['media_type'],'application/x-bibtex')
        self.assertEqual(self.store.read(found['export']['ref'])[1],row['citationStyles']['bibtex'].encode())
        self.assertEqual(adapter.fetch('Example theorem',parts=['metadata'])['status'],'selection_required')

    def test_reference_failure_keeps_metadata_and_reported_counts(self):
        row=self.record();row['referenceCount']=12;row['citationCount']=3
        def response(req):
            if req.url.path.endswith('/references'):return httpx.Response(429)
            return httpx.Response(200,json=[row])
        adapter=self.adapter(response);result=adapter.fetch(row['paperId'],parts=['metadata','supplementary'])
        self.assertEqual(result['components']['metadata']['status'],'available')
        self.assertEqual(result['components']['supplementary']['status'],'partial')
        self.assertEqual(result['components']['supplementary']['reported_reference_count'],12)
        self.assertEqual(result['components']['supplementary']['errors'][0]['code'],'rate_limited')
        self.assertEqual(len(self.calls),2)

if __name__=='__main__':unittest.main()
