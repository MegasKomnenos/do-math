import json,sys,unittest,tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from scholarly import ArtifactStore,ServiceError,bibliography
from browser_adapters import MathSciNet

class MathSciNetCitations(unittest.TestCase):
    def test_name_returns_candidates_without_requiring_an_mr_number(self):
        from unittest.mock import Mock
        adapter=MathSciNet(None,None)
        adapter.search=Mock(return_value={'status':'ok','received':1,'total':1,'records':{'ref':'candidate'}})
        result=adapter.fetch('P versus NP',parts=['metadata'])
        self.assertEqual(result['status'],'selection_required')
        self.assertEqual(adapter.search.call_args.args[0],'ti:("P versus NP")')

    def test_doi_lookup_checks_native_citation_before_following_the_mr_record(self):
        from unittest.mock import Mock
        payload=json.loads((ROOT/'tests/fixtures/mathscinet-formats.json').read_text('utf-8'))
        with tempfile.TemporaryDirectory() as temp:
            store=ArtifactStore(temp);adapter=MathSciNet(store,None)
            records=store.put('[{"mrnumber":2733384}]','application/json','mathscinet','https://mathscinet.ams.org/')
            bib=store.put(payload[0]['bib'],'application/x-bibtex','mathscinet','https://mathscinet.ams.org/')
            adapter.search=Mock(return_value={'status':'ok','received':1,'total':1,'records':records,'export':bib})
            adapter.fetch=Mock(return_value={'status':'ok','target':'MR2733384'})
            result=MathSciNet.fetch(adapter,'10.1016/j.jsc.2010.06.015',parts=['metadata'])
            self.assertEqual(result['status'],'ok')
            adapter.fetch.assert_called_once_with('MR2733384',parts=['metadata'])
            adapter.fetch.reset_mock()
            mismatch=MathSciNet.fetch(adapter,'10.1234/different',parts=['metadata'])
            self.assertEqual(mismatch['status'],'selection_required')
            adapter.fetch.assert_not_called()

    def test_invalid_selected_id_is_not_silently_dropped(self):
        payload=(ROOT/'tests/fixtures/mathscinet-formats.json').read_bytes()
        with tempfile.TemporaryDirectory() as temp:
            adapter=MathSciNet(ArtifactStore(temp),SimpleNamespace(context=None))
            page=SimpleNamespace(url='https://mathscinet-ams-org.libproxy.knu.ac.kr/mathscinet/article?mr=2733384')
            with patch.object(adapter,'page',return_value=page),patch('browser_adapters.browser_download',return_value=(payload,'application/json',page.url)) as download:
                with self.assertRaises(ServiceError):adapter.citation_exports(['2733384','invalid'],['bibtex'])
                download.assert_not_called()

    def test_source_formatted_fields_work_without_the_result_list(self):
        payload=(ROOT/'tests/fixtures/mathscinet-formats.json').read_bytes()
        with tempfile.TemporaryDirectory() as temp:
            store=ArtifactStore(temp);adapter=MathSciNet(store,SimpleNamespace(context=None))
            page=SimpleNamespace(url='https://mathscinet-ams-org.libproxy.knu.ac.kr/mathscinet/article?mr=2733384')
            with patch.object(adapter,'page',return_value=page),patch('browser_adapters.browser_download',return_value=(payload,'application/json',page.url)):
                result=adapter.citation_exports(['2733384'],['bibtex','endnote','amsref','tex'])
            self.assertEqual([x['format'] for x in result],['bibtex','endnote','amsref','tex'])
            for item in result:
                self.assertEqual(item['artifact']['mr_order'],['2733384'])
                self.assertGreater(item['artifact']['bytes'],0)
            bib=bibliography(store.read(result[0]['artifact']['ref'])[1],'application/x-bibtex')
            self.assertEqual(bib[0]['id'],'MR2733384')

    def test_wrong_or_duplicate_publication_ids_are_rejected(self):
        payload=json.loads((ROOT/'tests/fixtures/mathscinet-formats.json').read_text('utf-8'))
        with tempfile.TemporaryDirectory() as temp:
            adapter=MathSciNet(ArtifactStore(temp),SimpleNamespace(context=None))
            page=SimpleNamespace(url='https://mathscinet-ams-org.libproxy.knu.ac.kr/mathscinet/article?mr=2733384')
            for value in ([{**payload[0],'paperId':'1'}],payload+payload):
                with patch.object(adapter,'page',return_value=page),patch('browser_adapters.browser_download',return_value=(json.dumps(value).encode(),'application/json',page.url)):
                    with self.assertRaises(ServiceError) as error:adapter.citation_exports(['2733384'],['bibtex'])
                    self.assertEqual(error.exception.result['code'],'citation_identity_mismatch')

    def test_formatted_bibtex_must_match_its_publication_wrapper(self):
        payload=json.loads((ROOT/'tests/fixtures/mathscinet-formats.json').read_text('utf-8'))
        payload[0]['bib']=payload[0]['bib'].replace('2733384','999999')
        with tempfile.TemporaryDirectory() as temp:
            adapter=MathSciNet(ArtifactStore(temp),SimpleNamespace(context=None))
            page=SimpleNamespace(url='https://mathscinet-ams-org.libproxy.knu.ac.kr/')
            with patch.object(adapter,'page',return_value=page),patch('browser_adapters.browser_download',return_value=(json.dumps(payload).encode(),'application/json',page.url)):
                with self.assertRaises(ServiceError) as error:adapter.citation_exports(['2733384'],['bibtex'])
                self.assertEqual(error.exception.result['code'],'citation_identity_mismatch')

if __name__=='__main__':unittest.main()
