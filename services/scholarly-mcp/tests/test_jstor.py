import json,sys,tempfile,unittest
from pathlib import Path
import httpx
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from scholarly import ArtifactStore,bibliography
from jstor import JSTOR,stable_id

class JSTORContract(unittest.TestCase):
    def adapter(self,temp,handler):
        adapter=JSTOR(ArtifactStore(temp),httpx.Client(transport=httpx.MockTransport(handler)))
        adapter.min_interval=0
        return adapter

    def test_current_book_identifiers_and_metadata_are_supported(self):
        for value in ('jj.8306294','10.2307/jj.8306294','https://www.jstor.org/stable/jj.8306294'):
            self.assertEqual(stable_id(value),'jj.8306294')
        data=(ROOT/'tests/fixtures/jstor-book.ris').read_bytes()
        with tempfile.TemporaryDirectory() as temp:
            adapter=self.adapter(temp,lambda request:httpx.Response(200,content=data,headers={'content-type':'application/x-research-info-systems'}))
            result=adapter.fetch('jj.8306294',parts=['metadata'])
            row=json.loads(adapter.store.read(result['records']['ref'])[1])[0]
            self.assertEqual(result['status'],'ok')
            self.assertEqual(row['fields']['ty'],['BOOK'])
            self.assertIn('Bibliography and Footnotes',row['title'])

    def test_export_preserves_both_native_formats_without_requiring_a_bibtex_doi_field(self):
        ris=(ROOT/'tests/fixtures/jstor.ris').read_bytes()
        bib=(ROOT/'tests/fixtures/jstor.bib').read_bytes();calls=[]
        def response(request):
            calls.append(request.url.path)
            return httpx.Response(200,content=bib if '/text/' in request.url.path else ris,headers={'content-type':'text/plain' if '/text/' in request.url.path else 'application/x-research-info-systems'})
        with tempfile.TemporaryDirectory() as temp:
            adapter=self.adapter(temp,response);result=adapter.fetch('345683',parts=['metadata','export'])
            exports=result['components']['export']['artifacts']
            self.assertEqual(result['status'],'ok')
            self.assertEqual([x['format'] for x in exports],['ris','bibtex'])
            self.assertEqual(adapter.store.read(exports[1]['artifact']['ref'])[1],bib)
            self.assertIsNone(bibliography(bib,'application/x-bibtex')[0].get('doi'))
            self.assertEqual(calls,['/citation/ris/345683','/citation/text/345683'])

    def test_failed_second_export_keeps_ris_and_metadata(self):
        data=(ROOT/'tests/fixtures/jstor.ris').read_bytes()
        def response(request):
            return httpx.Response(403) if '/text/' in request.url.path else httpx.Response(200,content=data,headers={'content-type':'application/x-research-info-systems'})
        with tempfile.TemporaryDirectory() as temp:
            result=self.adapter(temp,response).fetch('345683',parts=['metadata','export'])
            self.assertEqual(result['status'],'partial')
            self.assertEqual(result['components']['metadata']['status'],'available')
            self.assertEqual(result['components']['export']['errors'][0]['status'],'restricted')
            self.assertEqual(len(result['components']['export']['artifacts']),1)

    def test_other_document_bibtex_is_rejected_but_original_file_is_preserved(self):
        ris=(ROOT/'tests/fixtures/jstor.ris').read_bytes()
        wrong=(ROOT/'tests/fixtures/jstor.bib').read_bytes().replace(b'/stable/345683',b'/stable/999999')
        def response(request):
            return httpx.Response(200,content=wrong if '/text/' in request.url.path else ris,
                headers={'content-type':'text/plain' if '/text/' in request.url.path else 'application/x-research-info-systems'})
        with tempfile.TemporaryDirectory() as temp:
            adapter=self.adapter(temp,response);result=adapter.fetch('345683',parts=['metadata','export'])
            error=result['components']['export']['errors'][0]
            self.assertEqual(result['status'],'partial')
            self.assertEqual(error['code'],'identity_mismatch')
            self.assertEqual(adapter.store.read(error['source_export']['ref'])[1],wrong)

if __name__=='__main__':unittest.main()
