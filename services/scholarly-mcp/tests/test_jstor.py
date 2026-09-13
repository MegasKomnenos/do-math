import json,sys,tempfile,unittest
from pathlib import Path
import httpx
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from scholarly import ArtifactStore,bibliography
from jstor import JSTOR,stable_id

class JSTORContract(unittest.TestCase):
    def test_missing_document_identity_is_a_retryable_load_timeout(self):
        from types import SimpleNamespace
        from unittest.mock import Mock
        from jstor import document_uuid
        from scholarly import ServiceError
        node=SimpleNamespace(wait_for=Mock(side_effect=TimeoutError('not attached')),count=lambda:0)
        page=SimpleNamespace(locator=lambda _:node,content=lambda:'<title>JSTOR</title>',wait_for_timeout=Mock())
        with self.assertRaises(ServiceError) as caught:document_uuid(page)
        self.assertEqual(caught.exception.result['code'],'document_load_timeout')
        self.assertTrue(caught.exception.result['retryable'])

    def test_ready_document_identity_is_not_confused_with_a_challenge_like_title(self):
        from types import SimpleNamespace
        from unittest.mock import Mock
        from jstor import document_uuid
        value='12345678-1234-1234-1234-123456789abc'
        node=SimpleNamespace(wait_for=Mock(),count=lambda:1,get_attribute=lambda _:value)
        page=SimpleNamespace(locator=lambda _:node,content=lambda:'<title>Client Challenge: a study</title>',wait_for_timeout=Mock())
        self.assertEqual(document_uuid(page),value)

    def test_document_identity_wait_classifies_a_challenge_that_renders_after_blank_shell(self):
        from jstor import document_uuid
        from scholarly import ServiceError

        class MissingIdentity:
            def wait_for(self, **_):
                raise TimeoutError("identity selector timed out")

            def count(self):
                return 0

        class DelayedChallengePage:
            def __init__(self):
                self.polls = 0

            def locator(self, _):
                return MissingIdentity()

            def content(self):
                return "" if self.polls == 0 else "<title>Client Challenge</title><input id='capInput'>"

            def wait_for_timeout(self, _):
                self.polls += 1

        with self.assertRaises(ServiceError) as caught:
            document_uuid(DelayedChallengePage())
        self.assertEqual(caught.exception.result["code"], "publisher_access_challenge")


    def test_document_parts_share_one_native_page_and_close_it_once(self):
        from unittest.mock import patch,Mock
        from publishers import Publisher,PROFILES
        data=(ROOT/'tests/fixtures/jstor.ris').read_bytes();page=Mock()
        def component(adapter,identifier,*,page=None):
            owned=page is None
            if owned:page=Publisher(adapter.store,adapter.gateway,next(p for p in PROFILES if p.source=='jstor')).document('https://www.jstor.org/stable/'+identifier)
            if owned:page.close()
            return {'status':'available'}
        with tempfile.TemporaryDirectory() as temp:
            adapter=self.adapter(temp,lambda request:httpx.Response(200,content=data));adapter.gateway=object()
            with patch('publishers.Publisher.document',return_value=page) as opened,patch('jstor.document_file',side_effect=component),patch('jstor.supplementary',side_effect=component):
                result=adapter.fetch('345683',parts=['fulltext','supplementary'])
            self.assertEqual(result['status'],'ok');self.assertEqual(opened.call_count,1);page.close.assert_called_once()

    def test_native_audio_header_and_disabled_download_are_distinct(self):
        from jstor import file_metadata,download_permission
        self.assertEqual(file_metadata((ROOT/'tests/fixtures/jstor-mp3-prefix.bin').read_bytes())['media_type'],'audio/mpeg')
        self.assertEqual(download_permission({'uuid':{'doi':'community.39197180','access':'disabled'}},'community.39197180','uuid')['access'],'disabled')

    def test_supplement_link_is_bound_to_its_native_parent_and_index(self):
        from jstor import supplement_links
        from scholarly import ServiceError
        raw=json.loads((ROOT/'tests/fixtures/jstor-supplement.json').read_text('utf-8'))
        rows=supplement_links(raw,'26581894','https://www.jstor.org')
        self.assertEqual(len(rows),1);self.assertEqual(rows[0]['filename'],'euclid.aos.1547197251_supp1.pdf')
        self.assertEqual(rows[0]['size'],863887)
        with self.assertRaises(ServiceError):supplement_links(raw,'999999','https://www.jstor.org')
        raw['content']['supplements'][0]['link']='/stable/get_asset/10.2307/999999?supp_index=0'
        self.assertTrue(supplement_links(raw,'26581894','https://www.jstor.org')[0]['invalid_link'])

    def test_native_image_download_url_identifies_the_selected_document(self):
        self.assertEqual(stable_id('https://www.jstor.org/stable/download-image/community.13581670?index=0'),'community.13581670')

    def test_native_download_permission_and_image_bytes_are_validated(self):
        from jstor import download_permission,file_metadata
        from scholarly import ServiceError
        for name,identifier,expected in [('jstor-image-download-params.json','community.13581670','download'),('jstor-restricted-download-params.json','community.39607963','restricted')]:
            raw=json.loads((ROOT/'tests/fixtures'/name).read_text('utf-8'));uuid=next(iter(raw))
            self.assertEqual(download_permission(raw,identifier,uuid)['access'],expected)
            with self.assertRaises(ServiceError):download_permission(raw,'community.999',uuid)
        meta=file_metadata((ROOT/'tests/fixtures/jstor-native-image.jpg').read_bytes())
        self.assertEqual(meta['media_type'],'image/jpeg');self.assertGreater(meta['width'],100);self.assertGreater(meta['height'],100)
        with self.assertRaises(ServiceError):file_metadata(b'<html>Access denied</html>')

    def test_name_fetch_returns_candidates_without_selecting_a_document(self):
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as temp:
            adapter=self.adapter(temp,lambda request:(_ for _ in ()).throw(AssertionError('Citation must not be selected')))
            with patch.object(adapter,'search',return_value={'status':'ok','received':2,'records':{'ref':'candidates'}}) as search:
                result=adapter.fetch('The Fundamental Theorem of Algebra',parts=['metadata'])
            self.assertEqual(result['status'],'selection_required');self.assertEqual(result['received'],2)
            search.assert_called_once()

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
