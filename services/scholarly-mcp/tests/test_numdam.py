"""Native Numdam result structure and document-boundary regression cases."""
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scholarly import ArtifactStore, ServiceError, extract_artifact
from numdam import Numdam, search_records


class NumdamContract(unittest.TestCase):
    def test_native_endnote_can_be_extracted_without_losing_repeated_authors(self):
        raw = (ROOT / 'tests/fixtures/numdam.enw').read_bytes()
        with tempfile.TemporaryDirectory() as temp:
            store = ArtifactStore(temp)
            artifact = store.put(raw, 'application/x-endnote-refer', 'numdam', 'https://www.numdam.org/')
            result = extract_artifact(store, artifact['ref'])
            self.assertEqual(result['returned'], 1)
            self.assertEqual(result['items'][0]['fields']['T'], ['Three complexity functions'])
            self.assertEqual(result['items'][0]['fields']['R'], ['10.1051/ita/2011126'])
            self.assertEqual(len(result['items'][0]['fields']['A']), 2)
            self.assertEqual(result['items'][0]['fields']['F'], ['ITA_2012__46_1_67_0'])

    def test_recorded_search_retains_order_title_and_both_file_formats(self):
        raw = (ROOT / 'tests/fixtures/numdam-search.html').read_text('utf-8')
        rows, total = search_records(raw, 'https://www.numdam.org/search?complexity-q')
        self.assertEqual(total, 4804)
        self.assertEqual(len(rows), 20)
        self.assertEqual(rows[0]['title'], 'Three complexity functions')
        self.assertEqual(rows[0]['url'], 'https://www.numdam.org/articles/10.1051/ita/2011126/')
        self.assertEqual({x['format'] for x in rows[0]['links']}, {'pdf', 'djvu'})
        self.assertEqual(len({r['url'] for r in rows}), 20)

    def test_zero_results_and_missing_results_are_distinct(self):
        self.assertEqual(search_records('<main>No results</main>', 'https://www.numdam.org/'), ([], 0))
        for html in ('<div class="results-header">20 results</div>', '<main>Loading</main>'):
            with self.assertRaises(ServiceError) as cm:
                search_records(html, 'https://www.numdam.org/')
            self.assertEqual(cm.exception.result['code'], 'search_parse_failed')

    def test_native_id_and_foreign_url_before_browser_or_network(self):
        with tempfile.TemporaryDirectory() as temp:
            adapter = Numdam(ArtifactStore(temp), None)
            self.assertEqual(adapter.document('oai:numdam.org:AIF_1956__6__1_0'), ('AIF_1956__6__1_0', None, None))
            self.assertEqual(adapter.document('https://www.numdam.org/item/AIF_1956__6__1_0.pdf')[0], 'AIF_1956__6__1_0')
            for target in ('https://example.org/item/AIF_1956__6__1_0', 'https://user:secret@www.numdam.org/item/AIF_1956__6__1_0'):
                with self.assertRaises(ServiceError) as cm:
                    adapter.document(target)
                self.assertEqual(cm.exception.result['code'], 'source_boundary')

    def test_options_are_rejected_without_ignoring_conditions(self):
        with tempfile.TemporaryDirectory() as temp:
            adapter = Numdam(ArtifactStore(temp), None)
            for options in ({'terms': 'wrong'}, {'terms': [{'field': 'date'}]}, {'field': 'invented'}, {'sort': 'title'}):
                with self.assertRaises(ServiceError):
                    adapter.search('complexity', options=options)


if __name__ == '__main__':
    unittest.main()
