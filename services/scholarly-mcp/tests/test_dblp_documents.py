import json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import httpx
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from api_adapters import DBLP
from scholarly import ArtifactStore,extract_artifact,ServiceError

class DBLPDocumentContract(unittest.TestCase):
    def test_all_native_formats_preserve_the_selected_record(self):
        def response(request):
            ext=request.url.path.rsplit('.',1)[-1]
            return httpx.Response(200,content=(ROOT/'tests/fixtures'/('dblp-cook.'+ext)).read_bytes(),headers={'Content-Type':'application/octet-stream'})
        with tempfile.TemporaryDirectory() as temp:
            a=DBLP(ArtifactStore(temp),httpx.Client(transport=httpx.MockTransport(response)))
            result=a.fetch('conf/stoc/Cook71',parts=['metadata','export'])
            formats=result['components']['export']['artifacts']
            self.assertEqual(result['status'],'ok')
            self.assertEqual({x['format'] for x in formats},{'xml','bibtex','ris','ntriples','turtle','rdf','plain'})
            for entry in formats:
                selected=extract_artifact(a.store,entry['artifact']['ref'],count=1)
                self.assertEqual(selected['status'],'ok')

    def test_name_is_a_candidate_search_and_wrong_xml_identity_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            a=DBLP(ArtifactStore(temp),httpx.Client(transport=httpx.MockTransport(lambda req:httpx.Response(200,content=(ROOT/'tests/fixtures/dblp-cook.xml').read_bytes()))))
            with patch.object(a,'search',return_value={'status':'ok','received':1,'preview':[{'title':'A paper'}]}):
                self.assertEqual(a.fetch('The Complexity of Theorem-Proving Procedures',parts=['metadata'])['status'],'selection_required')
            with self.assertRaises(ServiceError):a.fetch('conf/stoc/Wrong71',parts=['metadata'])

    def test_bad_native_export_keeps_metadata_and_other_exports(self):
        def response(request):
            ext=request.url.path.rsplit('.',1)[-1];data=(ROOT/'tests/fixtures'/('dblp-cook.'+ext)).read_bytes()
            if ext=='bib':data=data.replace(b'DBLP:conf/stoc/Cook71',b'DBLP:conf/stoc/Wrong71')
            return httpx.Response(200,content=data)
        with tempfile.TemporaryDirectory() as temp:
            a=DBLP(ArtifactStore(temp),httpx.Client(transport=httpx.MockTransport(response)))
            result=a.fetch('conf/stoc/Cook71',parts=['metadata','export'])
            self.assertEqual(result['status'],'partial')
            self.assertEqual(result['components']['metadata']['status'],'available')
            self.assertEqual(len(result['components']['export']['artifacts']),6)
            self.assertEqual(result['components']['export']['errors'][0]['code'],'identity_mismatch')

if __name__=='__main__':unittest.main()
