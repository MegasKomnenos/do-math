import sys,tempfile,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock,patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from scholarly import ArtifactStore,ServiceError,bibliography
DOI='10.1088/0022-3727/34/10/311'

class IOPCitationContract(unittest.TestCase):
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
