import json,sys,tempfile,unittest
from pathlib import Path
import httpx
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from api_adapters import SoftwareHeritage
from scholarly import ArtifactStore,ServiceError,extract_artifact
KEY='4d99d2d18326621ccdd70f5ea66c2e2ac236ad8b'
CORE='swh:1:cnt:'+KEY

class SoftwareHeritageContent(unittest.TestCase):
    def adapter(self,temp,*,alter=False,denied=False,metadata=None):
        data=(ROOT/'tests/fixtures/swh-simplefarm.ml').read_bytes()
        metadata=json.loads((ROOT/'tests/fixtures/swh-content.json').read_text('utf-8')) if metadata is None else metadata
        calls=[]
        def response(request):
            calls.append(str(request.url))
            if request.url.path.endswith('/raw/'):
                return httpx.Response(403) if denied else httpx.Response(200,content=data+(b'x' if alter else b''),headers={'content-type':'application/octet-stream'})
            return httpx.Response(200,json=metadata)
        return SoftwareHeritage(ArtifactStore(temp),httpx.Client(transport=httpx.MockTransport(response))),data,calls

    def test_qualified_lines_are_selected_after_checking_complete_content(self):
        with tempfile.TemporaryDirectory() as temp:
            adapter,data,calls=self.adapter(temp)
            result=adapter.fetch(CORE+';origin=https://example.org/repo;path=/simplefarm.ml;lines=9-15',parts=['metadata','fulltext'])
            content=result['components']['fulltext']
            self.assertEqual(result['status'],'ok')
            self.assertEqual(adapter.store.read(content['artifact']['ref'])[1],b''.join(data.splitlines(keepends=True)[8:15]))
            self.assertEqual(adapter.store.read(content['complete_content']['ref'])[1],data)
            self.assertEqual(extract_artifact(adapter.store,content['complete_content']['ref'],count=30)['total'],27)
            self.assertTrue(content['integrity']['verified'])
            self.assertEqual(result['qualifiers']['lines'],'9-15')
            self.assertFalse(result['context_verified'])
            self.assertTrue(all(url.startswith('https://archive.softwareheritage.org/') for url in calls))

    def test_corrupt_bytes_and_denied_content_keep_metadata(self):
        for kwargs,code in [({'alter':True},'content_integrity_mismatch'),({'denied':True},'access_restricted')]:
            with tempfile.TemporaryDirectory() as temp:
                adapter,_,_=self.adapter(temp,**kwargs)
                result=adapter.fetch(CORE,parts=['metadata','fulltext'])
                self.assertEqual(result['status'],'partial')
                self.assertEqual(result['components']['metadata']['status'],'available')
                self.assertEqual(result['components']['fulltext']['code'],code)

    def test_mismatched_metadata_is_rejected_before_raw_download(self):
        metadata=json.loads((ROOT/'tests/fixtures/swh-content.json').read_text('utf-8'))
        metadata['checksums']['sha1_git']='0'*40
        with tempfile.TemporaryDirectory() as temp:
            adapter,_,calls=self.adapter(temp,metadata=metadata)
            with self.assertRaises(ServiceError) as error:adapter.fetch(CORE,parts=['metadata','fulltext'])
            self.assertEqual(error.exception.result['code'],'identity_mismatch')
            self.assertEqual(len(calls),1)

    def test_invalid_or_duplicate_qualifiers_do_not_issue_a_request(self):
        for suffix in (';lines=15-9',';lines=0',';lines=1;lines=2',';unknown=value'):
            with tempfile.TemporaryDirectory() as temp:
                adapter,_,calls=self.adapter(temp)
                with self.assertRaises(ServiceError):adapter.fetch(CORE+suffix,parts=['metadata'])
                self.assertEqual(calls,[])

    def test_encoded_origin_is_sanitized_and_never_requested(self):
        with tempfile.TemporaryDirectory() as temp:
            adapter,_,calls=self.adapter(temp)
            result=adapter.fetch(CORE+';origin=https%3A%2F%2Fexample.org%2Frepo%3Faccess_token%3DSWH_SYNTHETIC_SECRET',parts=['metadata'])
            self.assertNotIn('SWH_SYNTHETIC_SECRET',str(result))
            self.assertEqual(len(calls),1)
            self.assertNotIn('example.org',calls[0])

    def test_out_of_range_fragment_retains_complete_verified_content(self):
        with tempfile.TemporaryDirectory() as temp:
            adapter,data,_=self.adapter(temp)
            result=adapter.fetch(CORE+';lines=25-40',parts=['metadata','fulltext'])
            selected=result['components']['fulltext']
            self.assertEqual(result['status'],'partial')
            self.assertEqual(selected['code'],'selection_out_of_range')
            self.assertNotIn('artifact',selected)
            self.assertEqual(adapter.store.read(selected['complete_content']['ref'])[1],data)

if __name__=='__main__':unittest.main()
