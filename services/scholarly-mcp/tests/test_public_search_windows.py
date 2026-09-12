"""Public page APIs must retain arbitrary requested record windows."""
import json,sys,tempfile,unittest
from pathlib import Path
import httpx
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from api_adapters import GitHub,Zenodo
from scholarly import ArtifactStore

class PublicSearchWindows(unittest.TestCase):
    def run_search(self,kind,start=1,limit=2,total=6,fail_second=False,duplicate=False,incomplete=False):
        folder=tempfile.TemporaryDirectory();self.addCleanup(folder.cleanup)
        store=ArtifactStore(folder.name);calls=[]
        def serve(request):
            calls.append(request)
            self.assertNotIn('authorization',request.headers)
            if fail_second and len(calls)==2:return httpx.Response(503)
            page=int(request.url.params['page']);size=int(request.url.params['per_page' if kind=='github' else 'size'])
            offset=(page-1)*size
            native=[{'id':i,'metadata':{'title':str(i)}} for i in range(offset,min(offset+size,total,1000 if kind=='github' else total))]
            if duplicate and len(calls)==2:native[0]['id']=1
            value={'items':native,'total_count':total,'incomplete_results':incomplete} if kind=='github' else {'hits':{'hits':native,'total':{'value':total,'relation':'eq'}}}
            return httpx.Response(200,json=value)
        client=httpx.Client(transport=httpx.MockTransport(serve));self.addCleanup(client.close)
        adapter=(GitHub if kind=='github' else Zenodo)(store,client)
        result=adapter.search('query',options={},start=start,limit=limit,export='native')
        return result,json.loads(store.read(result['records']['ref'])[1]),calls

    def test_arbitrary_offset_selects_exact_records_and_retains_native_pages(self):
        for kind in ('github','zenodo'):
            with self.subTest(kind=kind):
                result,rows,calls=self.run_search(kind)
                self.assertEqual([r['id'] for r in rows],[1,2])
                self.assertEqual(result['next'],{'start':3})
                self.assertEqual(len(result['export']['artifacts']),2)
                self.assertEqual(len(calls),2)

    def test_final_incomplete_window_stops_at_source_total(self):
        for kind in ('github','zenodo'):
            result,rows,calls=self.run_search(kind,start=5)
            self.assertEqual([r['id'] for r in rows],[5])
            self.assertFalse(result['has_more'])
            self.assertEqual(len(calls),1)

    def test_later_error_preserves_earlier_records(self):
        for kind in ('github','zenodo'):
            result,rows,calls=self.run_search(kind,fail_second=True)
            self.assertEqual(result['status'],'partial')
            self.assertEqual([r['id'] for r in rows],[1])
            self.assertEqual(result['next'],{'start':2})

    def test_repeated_page_does_not_silently_duplicate_records(self):
        for kind in ('github','zenodo'):
            result,rows,calls=self.run_search(kind,duplicate=True)
            self.assertEqual(result['status'],'partial')
            self.assertEqual([r['id'] for r in rows],[1])
            self.assertEqual(result['errors'][0]['code'],'inconsistent_pagination')

    def test_github_source_ceiling_and_incomplete_flag_are_preserved(self):
        result,rows,calls=self.run_search('github',start=999,total=1200,incomplete=True)
        self.assertEqual([r['id'] for r in rows],[999])
        self.assertEqual(result['requested'],2)
        self.assertTrue(result['has_more']);self.assertIsNone(result['next'])
        self.assertTrue(result['continuation_limited']);self.assertTrue(result['incomplete_results'])
        self.assertEqual(len(calls),1)

if __name__=='__main__':unittest.main()
