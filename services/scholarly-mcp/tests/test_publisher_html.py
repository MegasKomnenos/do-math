import sys,tempfile,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from scholarly import ArtifactStore,ServiceError

class PublisherHTMLContract(unittest.TestCase):
    def test_iop_body_preserves_tex_and_uses_actual_figure_instead_of_lazy_placeholder(self):
        import pymupdf
        from publisher_html import fetch_html
        raw=(ROOT/'tests/fixtures/iop-body-region.html').read_text('utf-8')
        with pymupdf.open() as document:
            document.new_page(width=20,height=10)
            png=document[0].get_pixmap().tobytes('png')
        with tempfile.TemporaryDirectory() as temp:
            store=ArtifactStore(temp)
            page=SimpleNamespace(url='https://iopscience.iop.org/article/10.1088/1367-2630/add557',content=lambda:raw)
            source=store.put(raw,'text/html','iop',page.url)
            adapter=SimpleNamespace(store=store,source='iop',profile=SimpleNamespace(download_hosts={'content-cld-iop-org.libproxy.knu.ac.kr'}),gateway=SimpleNamespace(context=None))
            gif=b'GIF89a\x01\x00\x01\x00\x00\x00\x00;'
            def downloaded(context,url,hosts,headers=None):
                return (gif,'image/gif',url) if url.endswith('.gif') else (png,'image/png',url)
            with patch('publisher_html.browser_download',side_effect=downloaded) as download:
                result=fetch_html(adapter,page,'10.1088/1367-2630/add557',source)
            self.assertEqual(result['status'],'available');self.assertEqual(len(result['figures']),1)
            self.assertEqual(result['math_images']['status'],'available')
            self.assertEqual(result['math_images']['requested'],5);self.assertEqual(result['math_images']['received'],5)
            self.assertEqual(result['math_images']['artifact']['media_type'],'image/gif')
            self.assertEqual(store.read(result['math_images']['artifact']['ref'])[1],gif)
            manifest=__import__('json').loads(store.read(result['math_images']['manifest']['ref'])[1])
            self.assertEqual(len(manifest),5);self.assertEqual([manifest[0]['number'],manifest[-1]['number']],[1,5])
            self.assertEqual(store.read(result['artifact']['ref'])[0]['equation_image_manifest_ref'],result['math_images']['manifest']['ref'])
            self.assertNotIn('equation_image_refs',store.read(result['artifact']['ref'])[0])
            self.assertEqual(download.call_count,6)
            html=store.read(result['artifact']['ref'])[1].decode()
            self.assertIn('math/tex',html);self.assertIn('\\textbf{s}',html)
            self.assertIn(result['figures'][0]['artifact']['ref'],html)
            self.assertIn(result['math_images']['artifact']['ref'],html)
            self.assertNotIn('data:image/png;base64',html)

    def test_iop_equation_failure_keeps_html_tex_and_other_images(self):
        import pymupdf
        from publisher_html import fetch_html
        raw=(ROOT/'tests/fixtures/iop-body-region.html').read_text('utf-8')
        with pymupdf.open() as document:
            document.new_page(width=20,height=10);png=document[0].get_pixmap().tobytes('png')
        gif=b'GIF89a\x01\x00\x01\x00\x00\x00\x00;';failed=[False]
        def downloaded(context,url,hosts,headers=None):
            if url.endswith('.jpg'):return png,'image/png',url
            if not failed[0]:failed[0]=True;raise ServiceError('timeout','Equation image timed out')
            return gif,'image/gif',url
        with tempfile.TemporaryDirectory() as temp:
            store=ArtifactStore(temp);page=SimpleNamespace(url='https://iopscience.iop.org/article/10.1088/1367-2630/add557',content=lambda:raw)
            source=store.put(raw,'text/html','iop',page.url)
            adapter=SimpleNamespace(store=store,source='iop',profile=SimpleNamespace(download_hosts={'content-cld-iop-org.libproxy.knu.ac.kr'}),gateway=SimpleNamespace(context=None))
            with patch('publisher_html.browser_download',side_effect=downloaded):result=fetch_html(adapter,page,'10.1088/1367-2630/add557',source)
            html=store.read(result['artifact']['ref'])[1].decode()
            manifest=__import__('json').loads(store.read(result['math_images']['manifest']['ref'])[1])
        self.assertEqual(result['status'],'partial');self.assertEqual(result['figures'][0]['status'],'available')
        self.assertEqual(result['math_images']['status'],'partial');self.assertEqual(result['math_images']['received'],4)
        self.assertEqual(manifest[0]['code'],'timeout')
        self.assertIn('math/tex',html);self.assertIn(result['figures'][0]['artifact']['ref'],html)

    def test_iop_equation_path_must_match_the_selected_article_assets(self):
        import pymupdf
        from publisher_html import fetch_html
        raw=(ROOT/'tests/fixtures/iop-body-region.html').read_text('utf-8').replace('/revision2/njpadd557ieqn1.gif','/other-revision/njpadd557ieqn1.gif')
        with pymupdf.open() as document:
            document.new_page(width=20,height=10);png=document[0].get_pixmap().tobytes('png')
        gif=b'GIF89a\x01\x00\x01\x00\x00\x00\x00;'
        def downloaded(context,url,hosts,headers=None):return (gif,'image/gif',url) if url.endswith('.gif') else (png,'image/png',url)
        with tempfile.TemporaryDirectory() as temp:
            store=ArtifactStore(temp);page=SimpleNamespace(url='https://iopscience.iop.org/article/10.1088/1367-2630/add557',content=lambda:raw)
            source=store.put(raw,'text/html','iop',page.url)
            adapter=SimpleNamespace(store=store,source='iop',profile=SimpleNamespace(download_hosts={'content-cld-iop-org.libproxy.knu.ac.kr'}),gateway=SimpleNamespace(context=None))
            with patch('publisher_html.browser_download',side_effect=downloaded) as download:result=fetch_html(adapter,page,'10.1088/1367-2630/add557',source)
            manifest=__import__('json').loads(store.read(result['math_images']['manifest']['ref'])[1])
        self.assertEqual(result['status'],'partial');self.assertEqual(manifest[0]['code'],'source_boundary')
        self.assertEqual(result['math_images']['received'],4);self.assertEqual(download.call_count,5)

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
        from publisher_html import nature_body,iop_body,springer_body
        with self.assertRaises(ServiceError):nature_body('<div class="c-article-body"><section>Abstract</section></div>')
        with self.assertRaises(ServiceError):iop_body('<div class="wd-jnl-art-abstract"><p>Abstract</p></div>')
        with self.assertRaises(ServiceError):springer_body('<div class="c-article-body"><div id="Abs1-section"><p>Abstract</p></div></div>')

    def test_springer_abstract_pdf_with_empty_native_body_reports_source_absence(self):
        from publisher_html import springer_body
        raw='''<meta name="citation_pdf_url" content="https://link.springer.com/content/pdf/10.1007/example.pdf">
        <div class="c-article-body">
          <section id="Abs1-section"><div class="c-article-section__content">Abstract text.</div></section>
          <section id="preview-section"><h2>Article PDF</h2></section>
          <div class="main-content"></div>
        </div>'''
        with self.assertRaises(ServiceError) as raised:springer_body(raw)
        self.assertEqual(raised.exception.result['status'],'not_found')
        self.assertEqual(raised.exception.result['code'],'html_fulltext_not_available')

    def test_springer_pdf_preview_does_not_prove_an_unrecognized_body_is_absent(self):
        from publisher_html import springer_body
        for content in ('<p>Article body in an unrecognized layout.</p>', '<img src="body.png">'):
            with self.subTest(content=content):
                raw='''<meta name="citation_pdf_url" content="https://link.springer.com/content/pdf/10.1007/example.pdf">
                <div class="c-article-body">
                  <section id="Abs1-section"><div class="c-article-section__content">Abstract text.</div></section>
                  <section id="preview-section"><h2>Article PDF</h2></section>
                  <div class="main-content">'''+content+'''</div>
                </div>'''
                with self.assertRaises(ServiceError) as raised:springer_body(raw)
                self.assertEqual(raised.exception.result['status'],'not_implemented')
                self.assertEqual(raised.exception.result['code'],'html_fulltext_not_identified')

    def test_iop_short_native_body_does_not_require_a_heading(self):
        from publisher_html import iop_body
        raw='<div class="wd-jnl-art-full-text"><div class="article-text"><p>Short native article body.</p></div></div>'
        self.assertEqual(iop_body(raw).get_text(' ',strip=True),'Short native article body.')

    def test_non_nature_springer_body_requires_substantive_native_sections(self):
        from publisher_html import springer_body
        raw=(ROOT/'tests/fixtures/springer-fulltext.html').read_text('utf-8')
        body=springer_body(raw)
        self.assertEqual([node.get('id') for node in body.select('[id^="Sec"][id$="-section"]')],['Sec1-section','Sec2-section'])

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
