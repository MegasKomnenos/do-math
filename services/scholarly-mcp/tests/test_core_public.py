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

    def test_real_indexed_text_and_missing_abstract_are_distinct(self):
        adapter=self.adapter(lambda r:httpx.Response(200,json={'id':42,'fullText':'A theorem.\nIts proof.','abstract':None}))
        result=adapter.fetch('https://core.ac.uk/works/42',parts=['metadata','abstract','fulltext'])
        self.assertEqual(result['components']['abstract']['status'],'not_found')
        file=result['components']['fulltext']['artifact']
        self.assertEqual(file['media_type'],'text/plain')
        self.assertEqual(self.store.read(file['ref'])[1],b'A theorem.\nIts proof.')

    def test_title_fetch_requires_selection_and_wrong_record_is_rejected(self):
        adapter=self.adapter(lambda r:httpx.Response(200,json={'results':[{'id':42,'title':'Example'}],'totalHits':1}))
        self.assertEqual(adapter.fetch('Example theorem',parts=['metadata'])['status'],'selection_required')
        adapter=self.adapter(lambda r:httpx.Response(200,json={'id':43}))
        with self.assertRaises(ServiceError) as cm:adapter.fetch('42',parts=['metadata'])
        self.assertEqual(cm.exception.result['code'],'identity_mismatch')
        with self.assertRaises(ServiceError):adapter.fetch('https://other.example/42',parts=['metadata'])

if __name__=='__main__':unittest.main()
