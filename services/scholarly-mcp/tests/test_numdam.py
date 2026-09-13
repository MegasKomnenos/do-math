"""Native Numdam result structure and document-boundary regression cases."""
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scholarly import ArtifactStore, ServiceError, extract_artifact
from numdam import Numdam, search_records


class NumdamContract(unittest.TestCase):
    def test_numbered_page_link_supports_text_and_date_search_pages(self):
        from numdam import numbered_page_link
        self.assertEqual(numbered_page_link('?algebra-2-qt', 49), '?algebra-49-qt')
        self.assertEqual(numbered_page_link('?*-[2012 TO 2012]-2-qdt', 49),
                         '?*-[2012 TO 2012]-49-qdt')
        self.assertIsNone(numbered_page_link('?unrecognized-page=2', 49))

    def test_blank_query_with_only_date_terms_uses_the_native_match_all_query(self):
        class Submitted(Exception):
            pass

        class Navigation:
            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

        class Locator:
            def __init__(self, page, selector):
                self.page = page
                self.selector = selector

            def count(self):
                return 1

            def filter(self, **kwargs):
                return self

            def locator(self, selector):
                return Locator(self.page, selector)

            def click(self):
                if self.selector == 'button[type=submit]':
                    raise Submitted

            def fill(self, value):
                self.page.fills[self.selector] = value

            def check(self):
                self.page.checked.add(self.selector)

        class Page:
            def __init__(self):
                self.fills = {}
                self.checked = set()

            def locator(self, selector):
                return Locator(self, selector)

            def expect_navigation(self, **kwargs):
                return Navigation()

        class Gateway:
            def __init__(self, page):
                self.page = page

            def public_page(self, source):
                return self.page

        page = Page()
        with tempfile.TemporaryDirectory() as temp:
            adapter = Numdam(ArtifactStore(temp), Gateway(page))
            options = {'terms': [{'field': 'date', 'from': '2012', 'until': '2012'}]}
            with patch('numdam.goto_source'), self.assertRaises(Submitted):
                adapter.search('', options=options)
        self.assertEqual(page.fills['input[name="q0"]'], '*')
        self.assertEqual(page.fills['input[name="q-f-1"]'], '2012')
        self.assertEqual(page.fills['input[name="q-l-1"]'], '2012')

        for bound, expected in (
            ({'from': '2012'}, {'q-f-1': '2012', 'q-l-1': '*'}),
            ({'until': '2012'}, {'q-f-1': '*', 'q-l-1': '2012'}),
        ):
            one_sided = Page()
            with tempfile.TemporaryDirectory() as temp:
                adapter = Numdam(ArtifactStore(temp), Gateway(one_sided))
                options = {'terms': [{'field': 'date', **bound}]}
                with patch('numdam.goto_source'), self.assertRaises(Submitted):
                    adapter.search('', options=options)
            self.assertEqual(one_sided.fills['input[name="q0"]'], '*')
            self.assertEqual(one_sided.fills['input[name="q-f-1"]'], expected['q-f-1'])
            self.assertEqual(one_sided.fills['input[name="q-l-1"]'], expected['q-l-1'])

        with tempfile.TemporaryDirectory() as temp:
            adapter = Numdam(ArtifactStore(temp), Gateway(Page()))
            with patch('numdam.goto_source'), self.assertRaises(ServiceError) as caught:
                adapter.search('', options={'terms': [{'field': 'date', 'from': 0, 'until': '2012'}]})
        self.assertEqual(caught.exception.result['code'], 'invalid_options')

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

    def test_result_rows_wrapped_by_source_formatting_are_not_dropped_or_duplicated(self):
        from bs4 import BeautifulSoup
        soup=BeautifulSoup((ROOT/'tests/fixtures/numdam-search.html').read_text('utf-8'),'html.parser')
        container=soup.select_one('.search-results');cards=container.select(':scope > .row');wrapper=soup.new_tag('i')
        cards[-2].insert_before(wrapper);wrapper.append(cards[-2].extract());wrapper.append(cards[-1].extract())
        rows,total=search_records(str(soup),'https://www.numdam.org/search?complexity-q')
        self.assertEqual(total,4804);self.assertEqual(len(rows),20);self.assertEqual(len({row['url'] for row in rows}),20)

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
