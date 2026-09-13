import json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import httpx
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from scholarly import ArtifactStore,ServiceError
from api_adapters import DBLP
from registry import SOURCES

class DBLPAccessContract(unittest.TestCase):
    def test_documented_thousand_hit_limit_is_not_reduced_by_the_common_default(self):
        raw=json.loads((ROOT/'tests/fixtures/dblp-search.json').read_text('utf-8'))
        raw['result']['hits']['@total']=raw['result']['hits']['@sent']
        seen=[]
        def response(request):
            seen.append(int(request.url.params['h']))
            return httpx.Response(200,json=raw)
        with tempfile.TemporaryDirectory() as temp:
            a=DBLP(ArtifactStore(temp),httpx.Client(transport=httpx.MockTransport(response)))
            a.min_interval=0
            for limit in (101,1000):
                with self.subTest(limit=limit):a.search('algebra',options={},limit=limit)
            with self.assertRaises(ServiceError):a.search('algebra',options={},limit=1001)
        self.assertEqual(seen,[101,1000])

    def test_short_native_pages_fill_the_requested_window_and_preserve_native_exports(self):
        seen=[]
        def response(request):
            start=int(request.url.params['f']);limit=int(request.url.params['h']);seen.append((start,limit))
            rows=[{'info':{'key':f'conf/example/{i}','title':f'Paper {i}'}} for i in range(start,min(start+min(limit,2),8))]
            return httpx.Response(200,json={'result':{'hits':{'@first':str(start),'@sent':str(len(rows)),'@total':'8','hit':rows}}})
        with tempfile.TemporaryDirectory() as temp:
            a=DBLP(ArtifactStore(temp),httpx.Client(transport=httpx.MockTransport(response)));a.min_interval=0
            result=a.search('algebra',options={},start=1,limit=5,export='native')
            records=json.loads(a.store.read(result['records']['ref'])[1])
        self.assertEqual(result['received'],5)
        self.assertEqual([r['key'] for r in records],[f'conf/example/{i}' for i in range(1,6)])
        self.assertEqual(seen,[(1,5),(3,3),(5,1)])
        self.assertEqual(result['next'],{'start':6})
        self.assertEqual(len(result['native_pages']),3)
        self.assertEqual(len(result['export']['artifacts']),3)

    def test_later_native_failure_keeps_the_verified_prefix(self):
        def response(request):
            start=int(request.url.params['f'])
            if start:return httpx.Response(429,headers={'Retry-After':'60'})
            return httpx.Response(200,json={'result':{'hits':{'@first':'0','@sent':'2','@total':'8','hit':[
                {'info':{'key':'conf/example/0','title':'Paper 0'}},{'info':{'key':'conf/example/1','title':'Paper 1'}}]}}})
        with tempfile.TemporaryDirectory() as temp:
            a=DBLP(ArtifactStore(temp),httpx.Client(transport=httpx.MockTransport(response)));a.min_interval=0
            result=a.search('algebra',options={},limit=5)
        self.assertEqual(result['status'],'partial')
        self.assertEqual(result['received'],2)
        self.assertEqual(result['next'],{'start':2})
        self.assertEqual(result['errors'][0]['code'],'rate_limited')
        self.assertEqual(result['errors'][0]['retry_after'],'60')

    def test_source_guide_explains_internal_request_pacing(self):
        self.assertIn('6.1초',SOURCES['dblp'].usage['limits'])

    def test_consecutive_dblp_requests_are_spaced_for_the_public_api(self):
        raw=json.loads((ROOT/'tests/fixtures/dblp-search.json').read_text('utf-8'))
        with tempfile.TemporaryDirectory() as temp:
            a=DBLP(ArtifactStore(temp),httpx.Client(transport=httpx.MockTransport(lambda request:httpx.Response(200,json=raw))))
            with patch('api_adapters.time.monotonic',side_effect=(100.0,100.0,101.0,106.1)),patch('api_adapters.time.sleep') as sleep:
                a.search('algebra',options={},limit=2)
                a.search('algebra',options={},limit=2)
            sleep.assert_called_once_with(5.1)

    def test_search_percent_encodes_spaces_without_losing_literal_plus(self):
        raw=json.loads((ROOT/'tests/fixtures/dblp-search.json').read_text('utf-8'))
        seen=[]
        def response(request):
            seen.append(request.url.query.decode())
            return httpx.Response(200,json=raw)
        with tempfile.TemporaryDirectory() as temp:
            a=DBLP(ArtifactStore(temp),httpx.Client(transport=httpx.MockTransport(response)))
            a.min_interval=0
            a.search('P versus C++',options={},limit=2)
        self.assertIn('q=P%20versus%20C%2B%2B',seen[0])
        self.assertNotIn('P+versus',seen[0])

    def test_native_meta_and_header_refresh_reach_json_without_exposing_challenge(self):
        html=(ROOT/'tests/fixtures/dblp-metarefresh.html').read_text('utf-8');raw=json.loads((ROOT/'tests/fixtures/dblp-search.json').read_text('utf-8'))
        for mode in ('meta','header'):
            calls=[]
            def response(request):
                calls.append(request)
                if 'pass-challenge' in request.url.path:
                    return httpx.Response(302,headers={'Location':request.url.params['redir'],'Set-Cookie':'verified=yes; Path=/; Secure'})
                if 'verified=yes' in request.headers.get('cookie',''):return httpx.Response(200,json=raw)
                soup=BeautifulSoup(html,'html.parser');meta=soup.select_one('meta[http-equiv="refresh"]');headers={'Content-Type':'text/html'}
                if mode=='header':headers['Refresh']=meta['content'];meta.decompose()
                return httpx.Response(200,text=str(soup),headers=headers)
            with self.subTest(mode=mode),tempfile.TemporaryDirectory() as temp:
                a=DBLP(ArtifactStore(temp),httpx.Client(transport=httpx.MockTransport(response)))
                with patch('time.sleep'):
                    result=a.search('algebra',options={},limit=2)
                self.assertEqual((result['status'],result['received']),('ok',2))
                self.assertEqual(len(calls),3)
                for p in Path(temp).rglob('*'):
                    if p.is_file():self.assertNotIn(b'synthetic-refresh-challenge',p.read_bytes())

    def test_foreign_refresh_and_changed_query_do_not_send_the_challenge(self):
        html=(ROOT/'tests/fixtures/dblp-metarefresh.html').read_text('utf-8')
        for altered in (html.replace('/.within.website/','https://example.org/.within.website/'),html.replace('q%3Dalgebra','q%3Ddifferent')):
            calls=[]
            def response(request):calls.append(request);return httpx.Response(200,text=altered,headers={'Content-Type':'text/html'})
            with tempfile.TemporaryDirectory() as temp:
                a=DBLP(ArtifactStore(temp),httpx.Client(transport=httpx.MockTransport(response)))
                with patch('time.sleep'),self.assertRaises(ServiceError):a.search('algebra',options={},limit=2)
                self.assertEqual(len(calls),1)

if __name__=='__main__':unittest.main()
