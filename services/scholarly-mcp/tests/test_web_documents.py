from pathlib import Path
import socket
import sys
import unittest
from unittest.mock import MagicMock,patch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scholarly import ServiceError
from web_documents import public_document_hosts,rendered_document_identity

class PublicDocumentContract(unittest.TestCase):
    def test_public_target_rejects_local_private_and_credential_urls(self):
        for address in ('127.0.0.1','10.0.0.1','169.254.169.254','::1'):
            with patch('socket.getaddrinfo',return_value=[(socket.AF_INET,socket.SOCK_STREAM,6,'',(address,443))]):
                with self.assertRaises(ServiceError) as error:
                    public_document_hosts('https://author.example/paper.pdf')
                self.assertEqual(error.exception.result['code'],'source_boundary')
        for target in ('file:///C:/math/.credentials/kudos.md','https://user:password@author.example/paper.pdf'):
            with self.assertRaises(ServiceError):
                public_document_hosts(target)

    def test_rendered_short_page_and_multiple_headings_are_valid(self):
        raw='<html><head><meta name="citation_title" content="A short public note"></head><body><main><h1>A short public note</h1><h2>Files</h2><a href="note.pdf">PDF</a></main></body></html>'
        self.assertEqual(rendered_document_identity(raw,['A short public note','Files'],'A short public note\nFiles\nPDF'),'A short public note')
        untitled='<html><body><main><p>Three public sentences. Second sentence. Third sentence.</p></main></body></html>'
        self.assertEqual(rendered_document_identity(untitled,[],'Three public sentences. Second sentence. Third sentence.'),'')
        article_about_challenges='<html><head><title>A research challenge</title></head><body><section id="challenge">A concise public research challenge.</section></body></html>'
        self.assertEqual(rendered_document_identity(article_about_challenges,[],'A concise public research challenge.'),'A research challenge')
        platform_title='<html><head><title>OSF</title></head><body><main><h1>Actual preprint title</h1><h2>Files</h2></main></body></html>'
        self.assertEqual(rendered_document_identity(platform_title,['Actual preprint title','Files'],'Actual preprint title Files'),'Actual preprint title')

    def test_rendered_empty_loading_and_access_states_are_rejected(self):
        for raw,headings,text,code in (
            ('<html><body><main></main></body></html>',[], '', 'dynamic_document_not_ready'),
            ('<html><head><title>Loading...</title></head><body><main>Loading...</main></body></html>',[], 'Loading...', 'dynamic_document_not_ready'),
            ('<html><head><title>Sign in</title></head><body><form><input type="password"></form></body></html>',[], 'Sign in', 'access_restricted')):
            with self.subTest(code=code),self.assertRaises(ServiceError) as error:
                rendered_document_identity(raw,headings,text)
            self.assertEqual(error.exception.result['code'],code)

    def test_script_only_response_uses_an_isolated_rendered_public_page(self):
        import json,tempfile
        from scholarly import ArtifactStore
        from web_documents import WebDocuments
        rendered='<html><head><title>A dynamic preprint</title></head><body><main><h1>A dynamic preprint</h1><p>Short public note.</p></main></body></html>'
        body=MagicMock();body.first.inner_text.return_value='A dynamic preprint\nShort public note.'
        page=MagicMock();page.url='https://dynamic.example/paper';page.content.return_value=rendered
        page.locator.return_value=body
        context=MagicMock();context.new_page.return_value=page
        gateway=MagicMock();gateway.browser.new_context.return_value=context
        with tempfile.TemporaryDirectory() as temp,patch('web_documents.public_document_hosts',return_value={'dynamic.example'}), \
                patch('web_documents.browser_download',return_value=(b'<html><body><script src="app.js"></script></body></html>','text/html','https://dynamic.example/paper')):
            store=ArtifactStore(temp);result=WebDocuments(store,gateway,'author-repository').fetch('https://dynamic.example/paper',parts=['metadata'])
            rows=json.loads(store.read(result['records']['ref'])[1]);manifest=store.read(result['source_document']['ref'])[0]
        self.assertEqual(rows[0]['title'],'A dynamic preprint')
        self.assertTrue(manifest['rendered_public_browser'])
        self.assertEqual(result['components']['metadata']['status'],'available')
        context.new_page.assert_called_once();page.close.assert_called_once()

    def test_unsettled_rendered_shell_is_preserved_as_a_clean_source_page(self):
        import tempfile
        from scholarly import ArtifactStore
        from web_documents import WebDocuments
        shell=b'<html><head><title>Loading...</title></head><body><main>Loading...</main><script>secret()</script></body></html>'
        page=MagicMock();page.url='https://dynamic.example/paper';page.content.return_value=shell.decode()
        body=MagicMock();body.first.inner_text.return_value='Loading...';body.all_inner_texts.return_value=[]
        page.locator.return_value=body
        context=MagicMock();context.new_page.return_value=page
        gateway=MagicMock();gateway.browser.new_context.return_value=context
        with tempfile.TemporaryDirectory() as temp,patch('web_documents.public_document_hosts',return_value={'dynamic.example'}), \
                patch('web_documents.browser_download',return_value=(shell,'text/html','https://dynamic.example/paper')):
            store=ArtifactStore(temp)
            with self.assertRaises(ServiceError) as error:
                WebDocuments(store,gateway,'author-repository').fetch('https://dynamic.example/paper',parts=['metadata'])
            preserved=store.read(error.exception.result['source_page']['ref'])[1]
        self.assertEqual(error.exception.result['code'],'dynamic_document_not_ready')
        self.assertIn(b'Loading...',preserved);self.assertNotIn(b'<script',preserved)
        page.close.assert_called_once()

if __name__=='__main__':
    unittest.main()
