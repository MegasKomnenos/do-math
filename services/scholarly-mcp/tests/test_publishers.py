import importlib
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class PublisherContract(unittest.TestCase):
    def test_explicit_pdf_accepts_owned_native_download_without_page_download_event(self):
        import tempfile,pymupdf
        from types import SimpleNamespace
        from unittest.mock import Mock,patch
        from playwright.sync_api import Error
        from scholarly import ArtifactStore
        url='https://epubs.siam.org/doi/pdf/10.1137/example?download=1'
        with pymupdf.open() as pdf:
            pdf.new_page().insert_text((72,72),'Selected front matter')
            data=pdf.tobytes()
        page=SimpleNamespace(on=Mock(),remove_listener=Mock(),is_closed=lambda:False,close=Mock())
        gateway=SimpleNamespace(start=Mock(),pages={},context=SimpleNamespace(on=Mock(),remove_listener=Mock()),
            public_page=Mock(return_value=page),native_download=Mock(return_value=(data,'file.pdf',url)))
        with tempfile.TemporaryDirectory() as temp:
            adapter=self.mod.Publisher(ArtifactStore(temp),gateway,next(p for p in self.mod.PROFILES if p.source=='siam'))
            with patch.object(adapter,'document',side_effect=Error('Download is starting')):
                result=adapter.explicit_pdf(url,['metadata','fulltext'])
            self.assertEqual(result['status'],'ok')
            self.assertEqual(result['components']['fulltext']['artifact']['pages'],1)
            self.assertEqual(gateway.native_download.call_args.kwargs['query'],'download=1')

    def test_book_uses_publication_doi_and_document_heading_without_brand_suffix(self):
        import json,tempfile
        from types import SimpleNamespace
        from unittest.mock import Mock,patch
        from scholarly import ArtifactStore,ServiceError
        identifier='10.1137/1.9780898717976'
        title='Numerical Polynomial Algebra'
        raw='<meta name="publication_doi" content="'+identifier+'"><meta property="og:title" content="'+title+' | SIAM Publications Library"><h1 class="banner-widget__heading">'+title+'</h1>'
        url='https://epubs.siam.org/doi/book/'+identifier
        page=SimpleNamespace(url=url,content=Mock(return_value=raw),wait_for_function=Mock(),
            locator=Mock(return_value=SimpleNamespace(inner_text=lambda:title)),title=lambda:title,close=Mock())
        with tempfile.TemporaryDirectory() as temp:
            store=ArtifactStore(temp)
            adapter=self.mod.Publisher(store,None,next(p for p in self.mod.PROFILES if p.source=='siam'))
            with patch.object(adapter,'document',return_value=page):
                result=adapter.fetch(url,parts=['metadata'])
                record=json.loads(store.read(result['records']['ref'])[1])[0]
                self.assertEqual((record['title'],record['doi']),(title,identifier))
                self.assertEqual(record['metadata']['og:title'],[title+' | SIAM Publications Library'])
                page.content.return_value=raw.replace('publication_doi','unrelated_field')
                with self.assertRaises(ServiceError) as rejected:
                    adapter.fetch(url,parts=['metadata'])
                self.assertEqual(rejected.exception.result['code'],'metadata_not_identified')

    def test_translated_challenge_has_restricted_status_in_document_fetch(self):
        import tempfile
        from types import SimpleNamespace
        from unittest.mock import Mock,patch
        from scholarly import ArtifactStore,ServiceError
        raw=(ROOT/'tests/fixtures/ams-challenge-ko.html').read_text('utf-8')
        page=SimpleNamespace(wait_for_function=Mock(side_effect=TimeoutError),content=lambda:raw,close=Mock())
        with tempfile.TemporaryDirectory() as temp:
            adapter=self.mod.Publisher(ArtifactStore(temp),None,next(p for p in self.mod.PROFILES if p.source=='ams'))
            with patch.object(adapter,'document',return_value=page),self.assertRaises(ServiceError) as error:
                adapter.fetch('https://pubs.ams.org/view?ProductCode=MPRIZE',parts=['metadata'])
            self.assertEqual(error.exception.result['status'],'restricted')
            self.assertEqual(error.exception.result['code'],'publisher_access_restricted')

    def test_url_fetch_preserves_requested_and_observed_doi_distinction(self):
        import json,tempfile
        from types import SimpleNamespace
        from unittest.mock import Mock,patch
        from scholarly import ArtifactStore
        raw=(ROOT/'tests/fixtures/taylor-dublin-core.html').read_text('utf-8')
        url='https://www.tandfonline.com/doi/abs/10.1080/10618600.2017.1349663'
        page=SimpleNamespace(url=url,content=Mock(return_value=raw),wait_for_function=Mock(),
            locator=Mock(return_value=SimpleNamespace(inner_text=lambda:'Paper')),title=lambda:'Paper',close=Mock())
        with tempfile.TemporaryDirectory() as temp:
            store=ArtifactStore(temp)
            adapter=self.mod.Publisher(store,None,next(p for p in self.mod.PROFILES if p.source=='taylor-francis'))
            with patch.object(adapter,'document',return_value=page):result=adapter.fetch(url,parts=['metadata'])
            self.assertIsNone(result['identity']['requested_doi'])
            self.assertEqual(json.loads(store.read(result['records']['ref'])[1])[0]['doi'],'10.1080/10618600.2017.1349663')

    def test_dublin_core_doi_is_distinct_from_the_native_numeric_identifier(self):
        raw=(ROOT/'tests/fixtures/taylor-dublin-core.html').read_text('utf-8')
        metadata=self.mod.publication_metadata(raw)
        self.assertEqual(self.mod.publication_dois(metadata),['10.1080/10618600.2017.1349663'])
        self.assertEqual(metadata['dc.identifier'],['1349663','10.1080/10618600.2017.1349663'])
        self.assertIn('publication_doi',metadata)

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
        raw='<a class="show-pdf" href="/doi/epdf/10.1080/current">View PDF</a><a class="show-pdf" href="/doi/pdf/10.1080/current">Download PDF</a><a class="show-pdf" href="/doi/pdf/10.1080/related">Other</a>'
        self.assertEqual(self.mod.primary_pdf_links(raw,'https://www.tandfonline.com/doi/abs/10.1080/current',identifier='10.1080/current'),['https://www.tandfonline.com/doi/pdf/10.1080/current'])

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

    def test_taylor_listing_and_export_have_the_same_publication_identities(self):
        from taylor import records
        from scholarly import bibliography
        raw=(ROOT / 'tests/fixtures/taylor-search.html').read_text('utf-8')
        rows,total,first=records(raw,'https://www.tandfonline.com')
        self.assertEqual((len(rows),total,first),(20,40675,0))
        exported=bibliography((ROOT / 'tests/fixtures/taylor.bib').read_bytes(),'application/x-bibtex')
        self.assertEqual([r['doi'] for r in rows[:2]],[r['doi'] for r in exported])

    def test_degruyter_keeps_native_document_types_and_doi_identity(self):
        from degruyter import records
        raw=(ROOT / 'tests/fixtures/degruyter-search.html').read_text('utf-8')
        rows,total=records(raw,'https://www.degruyterbrill.com')
        self.assertEqual(len(rows),10)
        self.assertGreaterEqual(total,10)
        self.assertEqual(rows[0]['doi'],'10.1515/joc-2026-0248')
        self.assertEqual(rows[0]['type'],'Article')

    def test_jstor_ris_retains_its_provider_preamble(self):
        from scholarly import bibliography
        raw=(ROOT / 'tests/fixtures/jstor.ris').read_bytes()
        rows=bibliography(raw,'application/x-research-info-systems')
        self.assertEqual(len(rows),1)
        self.assertIn('Provider: JSTOR',rows[0]['source_preamble'])
        self.assertIn('345683',' '.join(rows[0]['fields']['ur']))


if __name__ == "__main__":
    unittest.main()
