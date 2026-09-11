import json,sys,tempfile,unittest
from pathlib import Path
import httpx
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from scholarly import ArtifactStore,ServiceError

class IOPRSSContract(unittest.TestCase):
    def test_native_item_order_and_fields_are_preserved_when_sequence_is_empty(self):
        from iop_rss import feed_records
        rows=feed_records((ROOT/'tests/fixtures/iop-rss-twenty.xml').read_bytes())
        self.assertEqual(len(rows),20)
        self.assertEqual(rows[0]['doi'],'10.1088/1361-6528/ae9557')
        self.assertIn('Geometry controlled transition',rows[0]['title'])
        self.assertTrue(rows[0]['authors'])
        self.assertTrue(rows[0]['description_html'])
        self.assertIn('publicationName',rows[0]['xml'])
        self.assertIn('empty_rdf_sequence_used_item_order',rows[0]['parse_warnings'])

    def test_offset_window_crosses_api_pages_without_api_credentials(self):
        from iop_rss import IOPRSS
        first=(ROOT/'tests/fixtures/iop-rss-first.xml').read_bytes();second=(ROOT/'tests/fixtures/iop-rss-second.xml').read_bytes();calls=[]
        def response(request):
            calls.append(request)
            self.assertNotIn('authorization',request.headers);self.assertNotIn('api-key',request.headers)
            return httpx.Response(200,content=first if request.url.params['currentPage']=='1' else second,headers={'content-type':'application/xml'})
        with tempfile.TemporaryDirectory() as temp:
            adapter=IOPRSS(ArtifactStore(temp),httpx.Client(transport=httpx.MockTransport(response)))
            result=adapter.search('complexity',options={'page_size':10},start=9,limit=2)
            rows=json.loads(adapter.store.read(result['records']['ref'])[1])
            self.assertEqual([r['doi'] for r in rows],['10.1088/1748-605X/ae96f0','10.1088/1748-9326/ae9e24'])
            self.assertEqual([r.url.params['currentPage'] for r in calls],['1','2'])
            self.assertIsNone(result['total']);self.assertEqual(result['received'],2)

    def test_feed_order_is_not_relabelled_as_oldest_or_relevance(self):
        from iop_rss import IOPRSS
        with tempfile.TemporaryDirectory() as temp:
            adapter=IOPRSS(ArtifactStore(temp))
            with self.assertRaises(ServiceError):adapter.search('complexity',options={'sort':'oldest'})

if __name__=='__main__':unittest.main()
