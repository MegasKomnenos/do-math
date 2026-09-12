import json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import httpx
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from scholarly import ArtifactStore,ServiceError
from api_adapters import DBLP

class DBLPAccessContract(unittest.TestCase):
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
