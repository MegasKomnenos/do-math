import sys,tempfile,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock,patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from scholarly import ArtifactStore,ServiceError,bibliography
DOI='10.1088/0022-3727/34/10/311'

class IOPCitationContract(unittest.TestCase):
    def test_supplement_page_with_a_different_doi_is_not_downloaded(self):
        from iop import supplementary
        selected='10.1088/1367-2630/add557'
        raw='<a class="wd-btn-supp-data" href="/article/'+selected+'/data">Supplementary data</a>'
        viewer=SimpleNamespace(url='https://iopscience.iop.org/article/'+selected+'/data',content=lambda:'<meta name="citation_doi" content="10.1088/other">',close=Mock())
        page=SimpleNamespace(url='https://iopscience.iop.org/article/'+selected,content=lambda:raw)
        with tempfile.TemporaryDirectory() as temp:
            store=ArtifactStore(temp);proof=store.put(raw,'text/html','iop',page.url)
            adapter=SimpleNamespace(store=store,source='iop',gateway=SimpleNamespace(context=SimpleNamespace(new_page=lambda:viewer)),profile=SimpleNamespace(hosts=('iopscience.iop.org',)))
            with patch('browser_adapters.goto_source'),patch('supplements.fetch_supplementary') as files:
                result=supplementary(adapter,page,selected,proof)
            self.assertEqual(result['code'],'identity_mismatch');files.assert_not_called();viewer.close.assert_called_once()

    def test_native_spaced_key_is_preserved_with_an_extraction_warning(self):
        data=(ROOT/'tests/fixtures/iop.bib').read_bytes()
        rows=bibliography(data,'application/x-bibtex')
        self.assertEqual(len(rows),1);self.assertEqual(rows[0]['id'],'J Batina_2001')
        self.assertEqual(rows[0]['doi'],DOI)
        self.assertIn('citation_key_contains_whitespace',rows[0]['parse_warnings'])

    def test_failed_parsing_retains_the_received_native_file(self):
        from iop import citation
        data=b'@article{broken, title={unclosed'
        control=SimpleNamespace(first=SimpleNamespace(wait_for=Mock(),get_attribute=lambda name:'/export?doi='+DOI))
        page=SimpleNamespace(url='https://iopscience.iop.org/article/'+DOI+'/meta',locator=lambda selector:control)
        with tempfile.TemporaryDirectory() as temp:
            adapter=SimpleNamespace(store=ArtifactStore(temp),source='iop',gateway=SimpleNamespace(context=None),profile=SimpleNamespace(download_hosts=('iopscience.iop.org',)))
            with patch('iop.browser_download',return_value=(data,'application/x-bibtex','https://iopscience.iop.org/export?doi='+DOI)),self.assertRaises(ServiceError) as error:
                citation(adapter,page,DOI)
            self.assertEqual(adapter.store.read(error.exception.result['source_export']['ref'])[1],data)

if __name__=='__main__':unittest.main()
