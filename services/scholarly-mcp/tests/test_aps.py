import importlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
import httpx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scholarly import ArtifactStore


class APSContract(unittest.TestCase):
    def search_adapter(self,rows,*,fail_page=None):
        mod=importlib.import_module('aps');calls=[]
        def serve(request):
            calls.append(request)
            page=int(request.url.params['page']);size=int(request.url.params['per_page']);offset=(page-1)*size
            if page==fail_page:return httpx.Response(503)
            batch=rows[offset:offset+size];headers={}
            if offset+len(batch)<len(rows):
                headers['Link']=f'<https://harvest.aps.org/v2/journals/articles?page={page+1}&per_page={size}>; rel="next"'
            return httpx.Response(200,json={'data':batch},headers=headers)
        temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup)
        client=httpx.Client(transport=httpx.MockTransport(serve));self.addCleanup(client.close)
        return mod.APS(ArtifactStore(temp.name),client=client),calls

    def test_arbitrary_window_selects_exact_rows_and_preserves_native_pages(self):
        rows=[{'id':f'10.1103/example.{i}','title':str(i),'authors':[]} for i in range(4)]
        base,_=self.search_adapter(rows);whole=base.search('',options={},start=0,limit=4)
        adapter,calls=self.search_adapter(rows);result=adapter.search('',options={},start=1,limit=2,export='native')
        selected=json.loads(adapter.store.read(result['records']['ref'])[1])
        expected=json.loads(base.store.read(whole['records']['ref'])[1])[1:3]
        self.assertEqual(selected,expected);self.assertEqual(len(calls),2)
        self.assertEqual([p['native_start'] for p in result['native_pages']],[0,2])
        self.assertEqual(len(result['export']['artifacts']),2)
        self.assertEqual(result['next'],{'start':3})

    def test_end_window_stops_without_inventing_a_total_or_next(self):
        rows=[{'id':f'10.1103/example.{i}','title':str(i),'authors':[]} for i in range(4)]
        adapter,calls=self.search_adapter(rows);result=adapter.search('',options={},start=3,limit=2)
        selected=json.loads(adapter.store.read(result['records']['ref'])[1])
        self.assertEqual([r['id'] for r in selected],['10.1103/example.3'])
        self.assertIsNone(result['total']);self.assertFalse(result['has_more']);self.assertIsNone(result['next'])
        self.assertEqual(len(calls),1)

    def test_later_page_failure_preserves_the_selected_prefix(self):
        rows=[{'id':f'10.1103/example.{i}','title':str(i),'authors':[]} for i in range(5)]
        adapter,calls=self.search_adapter(rows,fail_page=2);result=adapter.search('',options={},start=1,limit=2)
        selected=json.loads(adapter.store.read(result['records']['ref'])[1])
        self.assertEqual([r['id'] for r in selected],['10.1103/example.1'])
        self.assertEqual(result['status'],'partial');self.assertEqual(result['next'],{'start':2})
        self.assertEqual(result['errors'][0]['http_status'],503);self.assertEqual(len(calls),2)

    def test_repeated_article_across_pages_is_partial_not_an_exact_window(self):
        rows=[{'id':f'10.1103/example.{i}','title':str(i),'authors':[]} for i in (0,1,1,3)]
        adapter,calls=self.search_adapter(rows);result=adapter.search('',options={},start=1,limit=2)
        selected=json.loads(adapter.store.read(result['records']['ref'])[1])
        self.assertEqual(result['status'],'partial')
        self.assertEqual([r['id'] for r in selected],['10.1103/example.1'])
        self.assertEqual(result['errors'][0]['code'],'inconsistent_pagination')
        self.assertEqual(result['next'],{'start':2})

    def test_keyless_metadata_keeps_full_authorship_without_large_preview(self):
        self.assertTrue((ROOT / "aps.py").exists(), "APS public adapter is absent")
        mod = importlib.import_module("aps")
        fixture = (ROOT / "tests/fixtures/aps-article.json").read_bytes()
        def serve(request):
            self.assertNotIn("authorization", request.headers)
            self.assertNotIn("x-api-key", request.headers)
            return httpx.Response(200, content=fixture, headers={"Content-Type": "application/json"})
        with tempfile.TemporaryDirectory() as folder, httpx.Client(transport=httpx.MockTransport(serve)) as client:
            store = ArtifactStore(folder)
            result = mod.APS(store, client=client).fetch("10.1103/PhysRevLett.116.061102", parts=["metadata", "abstract"])
            self.assertEqual(result["status"], "ok")
            self.assertLess(len(json.dumps(result)), 12000)
            data = json.loads(store.read(result["records"]["ref"])[1])
            self.assertGreater(len(data[0]["authors"]), 100)


if __name__ == "__main__":
    unittest.main()
