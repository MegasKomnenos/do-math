import importlib
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class IEEEContract(unittest.TestCase):
    def test_failed_export_retains_selected_search_records(self):
        import tempfile
        from unittest.mock import Mock,patch
        from types import SimpleNamespace
        from ieee import IEEE
        from scholarly import ArtifactStore,ServiceError
        raw=json.loads((ROOT/'tests/fixtures/ieee-search.json').read_text('utf-8'))
        page=Mock();page.url='https://ieeexplore.ieee.org/search/searchresult.jsp'
        pending=SimpleNamespace(value=SimpleNamespace(status=200,json=lambda:raw,url='https://ieeexplore.ieee.org/rest/search'))
        manager=Mock();manager.__enter__=Mock(return_value=pending);manager.__exit__=Mock(return_value=False)
        page.expect_response.return_value=manager
        with tempfile.TemporaryDirectory() as temp:
            adapter=IEEE(ArtifactStore(temp),None)
            with patch.object(adapter,'page',return_value=page),patch('ieee.goto_source'),patch('ieee.dismiss_cookies'),patch.object(adapter,'citation',side_effect=ServiceError('export_format_mismatch','Wrong native format')):
                result=adapter.search('"Article Number":10488889',options={},limit=1,export='csv')
            self.assertEqual(result['status'],'partial')
            self.assertEqual(result['received'],1)
            self.assertEqual(result['export']['errors'][0]['code'],'export_format_mismatch')
            self.assertEqual(json.loads(adapter.store.read(result['records']['ref'])[1])[0]['articleNumber'],'10488889')

    def test_native_citation_formats_and_selected_count_are_checked(self):
        from ieee import validate_citation_file
        from scholarly import ServiceError
        for format,suffix in [('bibtex','bib'),('ris','ris'),('csv','csv')]:
            data=(ROOT/'tests/fixtures'/('ieee.'+suffix)).read_bytes()
            validate_citation_file(data,format,1)
            with self.assertRaises(ServiceError):validate_citation_file(data,format,2)
        with self.assertRaises(ServiceError) as error:
            validate_citation_file(b'D. Drusinsky, "From P Versus NP", 2024.\nkeywords: {Privacy}\n','csv',1)
        self.assertEqual(error.exception.result['code'],'export_format_mismatch')

    def test_source_document_range_and_abstract_are_preserved(self):
        self.assertTrue((ROOT / "ieee.py").exists(), "IEEE adapter is absent")
        mod = importlib.import_module("ieee")
        raw = json.loads((ROOT / "tests/fixtures/ieee-search.json").read_text("utf-8"))
        rows, total, offset = mod.ieee_records(raw)
        self.assertEqual((len(rows), total, offset), (1, 1, 0))
        self.assertEqual(rows[0]["articleNumber"], "10488889")
        self.assertIn("zero knowledge", rows[0]["abstract"])


if __name__ == "__main__":
    unittest.main()
