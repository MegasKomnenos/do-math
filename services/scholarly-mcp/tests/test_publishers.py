import importlib
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class PublisherContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not (ROOT / "publishers.py").exists():
            raise AssertionError("Publisher document adapters are absent")
        cls.mod = importlib.import_module("publishers")

    def test_citation_metadata_keeps_repeated_authors_and_separate_dates(self):
        raw = '<meta name="citation_title" content="A theorem"><meta name="citation_author" content="One"><meta name="citation_author" content="Two"><meta name="citation_publication_date" content="2020"><meta name="citation_online_date" content="2019"><meta name="citation_doi" content="10.1007/example">'
        metadata = self.mod.publication_metadata(raw)
        self.assertEqual(metadata["citation_author"], ["One", "Two"])
        self.assertEqual(metadata["citation_publication_date"], ["2020"])
        self.assertEqual(metadata["citation_online_date"], ["2019"])

    def test_pdf_selection_uses_document_metadata_not_related_paper_links(self):
        raw = '<meta name="citation_pdf_url" content="/article/current.pdf"><a href="/references/other.pdf">PDF</a>'
        links = self.mod.primary_pdf_links(raw, "https://link.springer.com/article/current")
        self.assertEqual(links, ["https://link.springer.com/article/current.pdf"])

    def test_wiley_native_listing_preserves_publication_identity_and_range(self):
        raw = (ROOT / "tests/fixtures/wiley-search.html").read_text("utf-8")
        rows, total = self.mod.wiley_records(raw, "https://onlinelibrary.wiley.com")
        self.assertEqual(total, 684)
        self.assertEqual(len(rows), 20)
        self.assertEqual(rows[0]["title"], "Random Graphs")
        self.assertEqual(rows[1]["title"], "RANDOM GRAPHS")
        self.assertNotEqual(rows[0]["doi"], rows[1]["doi"])
        self.assertTrue(all(row["doi"].startswith("10.") for row in rows))
        empty = '<span class="result__current">0</span><div class="search-result__no-result">Your search did not return any results.</div>'
        self.assertEqual(self.mod.wiley_records(empty, 'https://onlinelibrary.wiley.com'), ([], 0))

    def test_springer_advanced_result_identifies_chapters_and_native_total(self):
        raw = (ROOT / "tests/fixtures/springer-search.html").read_text("utf-8")
        rows, total, first = self.mod.springer_records(raw, "https://link.springer.com")
        self.assertEqual((total, first, len(rows)), (6, 0, 6))
        self.assertEqual(rows[0]["doi"], "10.1007/978-3-642-39053-1_17")
        self.assertEqual(rows[0]["title"], "A Personal View of the P versus NP Problem")

    def test_oxford_listing_uses_chapter_link_and_rejects_unrendered_results(self):
        from silverchair import records
        raw = (ROOT / 'tests/fixtures/oxford-search.html').read_text('utf-8')
        rows, total, first = records(raw, 'https://academic.oup.com')
        self.assertEqual((total,first,len(rows)), (1,0,1))
        self.assertEqual(rows[0]['title'], 'The Prehistory of P versus NP')
        from urllib.parse import urlsplit
        self.assertTrue(urlsplit(rows[0]['url']).path.endswith('/chapter/180867790'))
        from scholarly import ServiceError
        with self.assertRaises(ServiceError):
            records('<div class="sr-statistics">1-20 of 47</div>No results found.', 'https://academic.oup.com')

    def test_aip_native_listing_keeps_its_twenty_records(self):
        from silverchair import records
        raw = (ROOT / 'tests/fixtures/aip-search.html').read_text('utf-8')
        rows,total,first = records(raw, 'https://pubs.aip.org')
        self.assertEqual((total,first,len(rows)),(367,0,20))
        self.assertEqual(rows[0]['title'],'Teaching decoherence by simulating quantum channels on quantum computers')

    def test_oxford_basic_search_and_advanced_empty_are_separate_observations(self):
        from silverchair import records
        raw = (ROOT / 'tests/fixtures/oxford-basic-search.html').read_text('utf-8')
        rows,total,first = records(raw,'https://academic.oup.com')
        self.assertEqual((len(rows),first),(20,0))
        self.assertGreaterEqual(total,20)
        empty = (ROOT / 'tests/fixtures/oxford-fulltext-search.html').read_text('utf-8')
        self.assertEqual(records(empty,'https://academic.oup.com'),([],0,0))

    def test_cambridge_preserves_chapter_identity_and_publication_listing(self):
        from cambridge import records
        raw=(ROOT / 'tests/fixtures/cambridge-search.html').read_text('utf-8')
        rows,total=records(raw,'https://www.cambridge.org')
        self.assertEqual((len(rows),total),(6,6))
        self.assertEqual(rows[0]['id'],'2ECDBEBD92A45AB706481F71189B3599')
        self.assertEqual(rows[0]['title'],'2 - The P versus NP Question')
        self.assertIn('2012',rows[0]['listing'])
        self.assertIn('2010',rows[0]['listing'])

    def test_oxford_journals_and_figures_are_not_dropped_from_mixed_results(self):
        from silverchair import records
        raw=(ROOT / 'tests/fixtures/oxford-mixed-search.html').read_text('utf-8')
        rows,total,first=records(raw,'https://academic.oup.com')
        self.assertEqual((len(rows),total,first),(20,75732,0))
        self.assertEqual(rows[0]['title'],'Journal of Complex Networks')


if __name__ == "__main__":
    unittest.main()
