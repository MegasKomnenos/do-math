import json
import sys
import tempfile
import unittest
from pathlib import Path

import httpx
import pymupdf

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from api_adapters import CORE
from scholarly import ArtifactStore, Sanitizer, ServiceError


class COREFileContract(unittest.TestCase):
    target = 'https://fileserver-az.core.ac.uk/download/287883844.pdf'
    signed = 'https://pdf.core.ac.uk/storage/pdf/shard/287883844.pdf?sp=r&sig=private-test-signature&sr=b&rsct=application%2Fpdf'

    def adapter(self, handler):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.store = ArtifactStore(directory.name)
        self.calls = []

        def observe(request):
            self.calls.append(str(request.url))
            return handler(request)

        client = httpx.Client(transport=httpx.MockTransport(observe))
        self.addCleanup(client.close)
        adapter = CORE(self.store, client)
        adapter.min_interval = 0
        return adapter

    def pdf(self):
        with pymupdf.open() as document:
            document.new_page().insert_text((72, 72), 'A public CORE paper')
            document.new_page().insert_text((72, 72), 'Second page')
            document.set_metadata({'title': 'A public CORE paper', 'author': 'Example Author'})
            return document.tobytes()

    def test_native_file_redirect_preserves_bytes_metadata_and_output_identity(self):
        data = self.pdf()
        adapter = self.adapter(lambda request: httpx.Response(302, headers={'location': self.signed})
                               if request.url.host == 'fileserver-az.core.ac.uk'
                               else httpx.Response(200, content=data, headers={'content-type': 'application/pdf'}))
        result = adapter.fetch(self.target, parts=['metadata', 'fulltext', 'export'])
        self.assertEqual(result['status'], 'ok')
        self.assertEqual(self.calls, [self.target, self.signed])
        artifact = result['components']['fulltext']['artifact']
        self.assertEqual(self.store.read(artifact['ref'])[1], data)
        self.assertEqual(artifact['pages'], 2)
        rows = json.loads(self.store.read(result['records']['ref'])[1])
        self.assertEqual(rows[0]['core_output_id'], 287883844)
        self.assertEqual(rows[0]['id'], self.target)
        self.assertEqual(rows[0]['title'], 'A public CORE paper')
        self.assertNotIn('private-test-signature', json.dumps(result))
        for manifest in (self.store.root / 'manifests').iterdir():
            self.assertNotIn('private-test-signature', manifest.read_text('utf-8'))

    def test_other_ids_api_routes_and_external_redirects_stop_before_following(self):
        targets = [self.signed.replace('287883844.pdf', '287883845.pdf'),
                   self.target.replace('287883844.pdf', '287883845.pdf'),
                   'https://api.core.ac.uk/v3/works/42',
                   'https://pdf.core.ac.uk.evil.example/storage/287883844.pdf',
                   self.signed.replace('https://pdf.', 'https://user:password@pdf.'),
                   self.signed.replace('https://', 'http://')]
        for target in targets:
            with self.subTest(target=target):
                adapter = self.adapter(lambda request: httpx.Response(302, headers={'location': target}))
                with self.assertRaises(ServiceError) as error:
                    adapter.fetch(self.target, parts=['fulltext'])
                self.assertEqual(error.exception.result['code'], 'source_boundary')
                self.assertEqual(self.calls, [self.target])

    def test_direct_file_and_missing_abstract_keep_verified_pdf(self):
        data = self.pdf()
        adapter = self.adapter(lambda request: httpx.Response(200, content=data, headers={'content-type': 'application/octet-stream'}))
        result = adapter.fetch('https://files01.core.ac.uk/download/pdf/287883844.pdf', parts=['metadata', 'abstract', 'fulltext'])
        self.assertEqual(result['status'], 'partial')
        self.assertEqual(result['components']['abstract']['status'], 'not_offered')
        self.assertEqual(result['components']['fulltext']['status'], 'available')
        self.assertEqual(result['components']['fulltext']['artifact']['media_type'], 'application/pdf')

    def test_native_ui_download_url_follows_the_observed_same_output_chain(self):
        data = self.pdf()
        target = 'https://core.ac.uk/download/287883844.pdf'

        def handle(request):
            if request.url.host == 'core.ac.uk':
                return httpx.Response(302, headers={'location': self.target})
            if request.url.host == 'fileserver-az.core.ac.uk':
                return httpx.Response(302, headers={'location': self.signed})
            return httpx.Response(200, content=data, headers={'content-type': 'application/pdf'})

        result = self.adapter(handle).fetch(target, parts=['fulltext'])
        self.assertEqual(result['status'], 'ok')
        self.assertEqual(self.calls, [target, self.target, self.signed])
        self.assertEqual(result['components']['fulltext']['artifact']['core_output_id'], 287883844)

    def test_html_and_damaged_pdf_are_not_reported_as_fulltext(self):
        for data, media, expected in [(b'<html><title>Just a moment</title></html>', 'text/html', 'access_challenge'),
                                       (b'%PDF-1.7\nnot a PDF', 'application/pdf', 'invalid_pdf'),
                                       (b'Not a PDF', 'application/octet-stream', 'invalid_pdf')]:
            with self.subTest(media=media, expected=expected):
                adapter = self.adapter(lambda request: httpx.Response(200, content=data, headers={'content-type': media}))
                with self.assertRaises(ServiceError) as error:
                    adapter.fetch(self.target, parts=['fulltext'])
                self.assertEqual(error.exception.result['code'], expected)
                if expected == 'invalid_pdf':
                    self.assertIn('evidence', error.exception.result)

    def test_invalid_parts_make_no_request(self):
        adapter = self.adapter(lambda request: self.fail('Unexpected network request'))
        with self.assertRaises(ServiceError) as error:
            adapter.fetch(self.target, parts=['invented'])
        self.assertEqual(error.exception.result['code'], 'invalid_parts')
        self.assertEqual(self.calls, [])

    def test_pdf_core_sas_signature_is_removed_but_public_sig_elsewhere_is_preserved(self):
        sanitizer = Sanitizer()
        self.assertNotIn('private-test-signature', sanitizer.url(self.signed))
        self.assertEqual(sanitizer.url('https://example.org/search?sig=public-label'), 'https://example.org/search?sig=public-label')


if __name__ == '__main__':
    unittest.main()
