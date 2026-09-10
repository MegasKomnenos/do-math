import sys,tempfile,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from scholarly import ArtifactStore,ServiceError

class PublisherHTMLContract(unittest.TestCase):
    def test_nature_body_preserves_tex_and_downloads_its_figure(self):
        import pymupdf
        from publisher_html import fetch_html
        raw=(ROOT/'tests/fixtures/nature-body-region.html').read_text('utf-8')
        with pymupdf.open() as document:
            document.new_page(width=20,height=10)
            png=document[0].get_pixmap().tobytes('png')
        with tempfile.TemporaryDirectory() as temp:
            store=ArtifactStore(temp)
            page=SimpleNamespace(url='https://www.nature.com/articles/s41467-023-41217-6',content=lambda:raw)
            source=store.put(raw,'text/html','springer',page.url)
            adapter=SimpleNamespace(store=store,source='springer',profile=SimpleNamespace(download_hosts={'media.springernature.com'}),gateway=SimpleNamespace(context=None))
            with patch('publisher_html.browser_download',return_value=(png,'image/png','https://media.springernature.com/figure.png')) as download:
                result=fetch_html(adapter,page,'10.1038/s41467-023-41217-6',source)
            self.assertEqual(result['status'],'available');self.assertEqual(len(result['figures']),1)
            self.assertEqual(download.call_count,1)
            html=store.read(result['artifact']['ref'])[1].decode()
            self.assertIn('\\mathsf{NISQ}',html)
            self.assertNotIn('Unrelated recommendations',html)
            self.assertIn(result['figures'][0]['artifact']['ref'],html)
            self.assertEqual(result['figures'][0]['artifact']['media_type'],'image/png')

    def test_abstract_only_page_is_not_fulltext_html(self):
        from publisher_html import nature_body
        with self.assertRaises(ServiceError):nature_body('<div class="c-article-body"><section>Abstract</section></div>')

    def test_figure_failure_preserves_the_html_and_its_error(self):
        from publisher_html import fetch_html
        raw=(ROOT/'tests/fixtures/nature-body-region.html').read_text('utf-8')
        with tempfile.TemporaryDirectory() as temp:
            store=ArtifactStore(temp)
            page=SimpleNamespace(url='https://www.nature.com/articles/s41467-023-41217-6',content=lambda:raw)
            source=store.put(raw,'text/html','springer',page.url)
            adapter=SimpleNamespace(store=store,source='springer',profile=SimpleNamespace(download_hosts={'media.springernature.com'}),gateway=SimpleNamespace(context=None))
            with patch('publisher_html.browser_download',side_effect=ServiceError('timeout','Source timeout')):
                result=fetch_html(adapter,page,'10.1038/s41467-023-41217-6',source)
            self.assertEqual(result['status'],'partial')
            self.assertEqual(result['figures'][0]['code'],'timeout')
            html=store.read(result['artifact']['ref'])[1].decode()
            self.assertIn('\\mathsf{NISQ}',html)
            self.assertNotIn('<img src="https:',html)

if __name__=='__main__':unittest.main()
