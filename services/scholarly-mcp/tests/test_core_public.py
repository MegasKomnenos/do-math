import json,sys,tempfile,unittest
from pathlib import Path
import httpx
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from scholarly import ArtifactStore,ServiceError
from api_adapters import CORE

class COREPublicContract(unittest.TestCase):
    def adapter(self,handler):
        temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup)
        self.store=ArtifactStore(temp.name)
        client=httpx.Client(transport=httpx.MockTransport(handler));self.addCleanup(client.close)
        adapter=CORE(self.store,client);adapter.min_interval=0;return adapter

    def test_public_access_notice_is_not_full_text(self):
        row=json.loads((ROOT/'tests/fixtures/core-public-record.json').read_text('utf-8'))
        adapter=self.adapter(lambda r:httpx.Response(200,json=row))
        result=adapter.fetch(str(row['id']),parts=['metadata','abstract','fulltext'])
        self.assertEqual(result['components']['fulltext']['status'],'restricted')
        self.assertEqual(result['components']['fulltext']['code'],'public_fulltext_restricted')
        self.assertEqual(result['components']['metadata']['status'],'available')

    def test_search_uses_the_documented_trailing_slash(self):
        seen=[]
        def handle(request):
            seen.append(request.url.path)
            return httpx.Response(200,json={'results':[],'totalHits':0})
        result=self.adapter(handle).search('proof',options={},limit=1)
        self.assertEqual(result['total'],0)
        self.assertEqual(seen,['/v3/search/works/'])

    def test_custom_rate_header_is_actionable_only_on_429(self):
        custom='2026-09-13T08:23:48+0000'
        adapter=self.adapter(lambda r:httpx.Response(429,headers={
            'Retry-After':'120','X-RateLimit-Retry-After':custom,
            'X-RateLimit-Limit':'10','X-RateLimit-Remaining':'0'}))
        with self.assertRaises(ServiceError) as error:
            adapter.request('https://api.core.ac.uk/v3/works/42')
        self.assertEqual(error.exception.result['retry_after'],'120')
        self.assertEqual(error.exception.result['retry_after_header'],'retry-after')
        self.assertEqual(error.exception.result['rate_limit_retry_after'],custom)
        self.assertEqual(error.exception.result['rate_limit_remaining'],'0')

        adapter=self.adapter(lambda r:httpx.Response(200,json={'id':42},headers={
            'X-RateLimit-Retry-After':custom,'X-RateLimit-Limit':'10','X-RateLimit-Remaining':'9'}))
        _,evidence=adapter.request('https://api.core.ac.uk/v3/works/42')
        self.assertNotIn('retry_after',evidence)
        self.assertEqual(evidence['rate_limit_retry_after'],custom)
        self.assertEqual(evidence['rate_limit_remaining'],'9')

    def test_real_indexed_text_and_missing_abstract_are_distinct(self):
        adapter=self.adapter(lambda r:httpx.Response(200,json={'id':42,'fullText':'A theorem.\nIts proof.','abstract':None}))
        result=adapter.fetch('https://core.ac.uk/works/42',parts=['metadata','abstract','fulltext'])
        self.assertEqual(result['components']['abstract']['status'],'not_found')
        file=result['components']['fulltext']['artifact']
        self.assertEqual(file['media_type'],'text/plain')
        self.assertEqual(self.store.read(file['ref'])[1],b'A theorem.\nIts proof.')

    def test_whitespace_only_fulltext_is_missing(self):
        adapter=self.adapter(lambda r:httpx.Response(200,json={'id':42,'fullText':' \r\n\t '}))
        result=adapter.fetch('42',parts=['fulltext'])
        self.assertEqual(result['components']['fulltext']['status'],'not_found')
        self.assertNotIn('artifact',result['components']['fulltext'])

    def test_source_guide_exposes_recovery_and_rate_boundaries(self):
        from registry import SOURCES
        usage=SOURCES['core'].usage
        self.assertIn('/v3/search/works/',usage['search'])
        for phrase in ('output API download URL','429·401·403·410','disabled·removed','다른 저장소'):
            self.assertIn(phrase,usage['fetch'])
        self.assertIn('성공 응답의 custom timestamp는 rate metadata',usage['limits'])

    def test_title_fetch_requires_selection_and_wrong_record_is_rejected(self):
        adapter=self.adapter(lambda r:httpx.Response(200,json={'results':[{'id':42,'title':'Example'}],'totalHits':1}))
        self.assertEqual(adapter.fetch('Example theorem',parts=['metadata'])['status'],'selection_required')
        adapter=self.adapter(lambda r:httpx.Response(200,json={'id':43}))
        with self.assertRaises(ServiceError) as cm:adapter.fetch('42',parts=['metadata'])
        self.assertEqual(cm.exception.result['code'],'identity_mismatch')
        with self.assertRaises(ServiceError):adapter.fetch('https://other.example/42',parts=['metadata'])

if __name__=='__main__':unittest.main()
