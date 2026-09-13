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

    def test_explicit_output_download_url_follows_only_the_same_output_chain(self):
        data = self.pdf()
        output = 'https://api.core.ac.uk/v3/outputs/287883844/download'
        current = 'https://core.ac.uk/download/287883844.pdf'

        def handle(request):
            if request.url.host == 'api.core.ac.uk':
                return httpx.Response(302, headers={'location': current})
            if request.url.host == 'core.ac.uk':
                return httpx.Response(302, headers={'location': self.target})
            if request.url.host == 'fileserver-az.core.ac.uk':
                return httpx.Response(302, headers={'location': self.signed})
            return httpx.Response(200, content=data, headers={'content-type': 'application/pdf'})

        result = self.adapter(handle).fetch(output, parts=['fulltext'])
        self.assertEqual(result['components']['fulltext']['status'], 'available')
        self.assertEqual(self.calls, [output, current, self.target, self.signed])

        other = current.replace('287883844', '287883845')
        adapter = self.adapter(lambda request: httpx.Response(302, headers={'location': other}))
        with self.assertRaises(ServiceError) as error:
            adapter.fetch(output, parts=['fulltext'])
        self.assertEqual(error.exception.result['code'], 'source_boundary')
        self.assertEqual(self.calls, [output])

    def work_record(self, fulltext='Not available for public API users.'):
        return {'id': 42, 'title': 'A public CORE paper', 'abstract': 'Summary',
                'fullText': fulltext,
                'outputs': ['https://api.core.ac.uk/v3/outputs/287883844'],
                'downloadUrl': 'https://core.ac.uk/download/287883844.pdf',
                'links': [{'type': 'download', 'url': 'https://core.ac.uk/download/287883844.pdf'}]}

    def test_related_metadata_can_use_the_supported_output_api_download(self):
        data=self.pdf()
        output='https://api.core.ac.uk/v3/outputs/287883844/download'
        record=self.work_record();record.update(downloadUrl=output,links=[])
        def handle(request):
            if str(request.url)==output:return httpx.Response(302,headers={'location':self.target})
            if request.url.path=='/v3/works/42':return httpx.Response(200,json=record)
            return httpx.Response(200,content=data,headers={'content-type':'application/pdf'})
        result=self.adapter(handle).fetch('42',parts=['metadata','fulltext'])
        self.assertEqual(result['components']['fulltext']['status'],'available')
        self.assertIn(output,self.calls)

    def test_legacy_resolution_can_use_the_supported_same_output_api_download(self):
        data=self.pdf()
        legacy='https://files01.core.ac.uk/download/pdf/287883844.pdf'
        output='https://api.core.ac.uk/v3/outputs/287883844/download'
        def handle(request):
            if str(request.url)==legacy:return httpx.Response(404)
            if str(request.url)==output:return httpx.Response(302,headers={'location':self.target})
            if request.url.path=='/v3/outputs/287883844':
                return httpx.Response(200,json={'id':287883844,'fulltextStatus':'enabled','deleted':'ALLOWED','downloadUrl':output})
            return httpx.Response(200,content=data,headers={'content-type':'application/pdf'})
        result=self.adapter(handle).fetch(legacy,parts=['fulltext'])
        self.assertEqual(result['components']['fulltext']['status'],'available')
        self.assertIn(output,self.calls)

    def test_work_uses_only_its_related_output_file_and_preserves_partial_failure(self):
        data = self.pdf()
        def handle(request):
            if request.url.host == 'api.core.ac.uk':
                return httpx.Response(200, json=self.work_record())
            if request.url.host == 'core.ac.uk':
                return httpx.Response(302, headers={'location': self.target})
            if request.url.host == 'fileserver-az.core.ac.uk':
                return httpx.Response(302, headers={'location': self.signed})
            return httpx.Response(200, content=data, headers={'content-type': 'application/pdf'})
        result = self.adapter(handle).fetch('42', parts=['metadata', 'abstract', 'fulltext'])
        self.assertEqual(result['status'], 'ok')
        self.assertEqual(result['components']['fulltext']['content_kind'], 'core_pdf')
        self.assertEqual(result['components']['fulltext']['work_id'], 42)

        wrong = self.work_record();wrong['outputs']=['https://api.core.ac.uk/v3/outputs/287883845']
        adapter = self.adapter(lambda request: httpx.Response(200, json=wrong))
        result = adapter.fetch('42', parts=['metadata', 'fulltext'])
        self.assertEqual(result['components']['metadata']['status'], 'available')
        self.assertEqual(result['components']['fulltext']['code'], 'public_fulltext_restricted')
        self.assertEqual(len(self.calls), 1)

        def limited(request):
            if request.url.host == 'api.core.ac.uk':
                return httpx.Response(200, json=self.work_record(''))
            return httpx.Response(429, headers={'X-RateLimit-Retry-After': '2099-01-01T00:00:00+0000',
                                                'X-RateLimit-Limit': '10', 'X-RateLimit-Remaining': '0'})
        result = self.adapter(limited).fetch('42', parts=['metadata', 'abstract', 'fulltext'])
        self.assertEqual(result['status'], 'partial')
        self.assertEqual(result['components']['metadata']['status'], 'available')
        self.assertEqual(result['components']['fulltext']['code'], 'rate_limited')
        self.assertEqual(result['components']['fulltext']['rate_limit_remaining'], '0')

    def test_whitespace_fulltext_uses_a_verified_file_candidate(self):
        data = self.pdf()
        def handle(request):
            if request.url.host == 'api.core.ac.uk':
                return httpx.Response(200, json=self.work_record(' \r\n\t '))
            if request.url.host == 'core.ac.uk':
                return httpx.Response(302, headers={'location': self.target})
            if request.url.host == 'fileserver-az.core.ac.uk':
                return httpx.Response(302, headers={'location': self.signed})
            return httpx.Response(200, content=data, headers={'content-type': 'application/pdf'})
        result = self.adapter(handle).fetch('42', parts=['fulltext'])
        self.assertEqual(result['components']['fulltext']['status'], 'available')
        self.assertEqual(result['components']['fulltext']['content_kind'], 'core_pdf')

    def test_legacy_files01_404_uses_current_enabled_same_output_metadata(self):
        data = self.pdf()
        legacy = 'https://files01.core.ac.uk/download/pdf/287883844.pdf'
        current = 'https://core.ac.uk/download/287883844.pdf'
        def handle(request):
            if request.url.host == 'files01.core.ac.uk':
                return httpx.Response(404, content=b'missing')
            if request.url.host == 'api.core.ac.uk':
                return httpx.Response(200, json={'id': 287883844, 'fulltextStatus': 'enabled',
                                                 'deleted': 'ALLOWED', 'downloadUrl': current})
            if request.url.host == 'core.ac.uk':
                return httpx.Response(302, headers={'location': self.target})
            if request.url.host == 'fileserver-az.core.ac.uk':
                return httpx.Response(302, headers={'location': self.signed})
            return httpx.Response(200, content=data, headers={'content-type': 'application/pdf'})
        result = self.adapter(handle).fetch(legacy, parts=['fulltext'])
        self.assertEqual(result['components']['fulltext']['status'], 'available')
        self.assertIn('resolution_ref', result['components']['fulltext']['artifact'])

    def test_legacy_access_denial_gone_and_rate_limit_do_not_resolve(self):
        legacy = 'https://files01.core.ac.uk/download/pdf/287883844.pdf'
        cases = [(401, 'access_restricted'), (403, 'access_restricted'),
                 (410, 'not_found_at_source'), (429, 'rate_limited')]
        for status, code in cases:
            with self.subTest(status=status):
                headers = {'X-RateLimit-Retry-After': '2099-01-01T00:00:00+0000'} if status == 429 else {}
                adapter = self.adapter(lambda request, status=status, headers=headers:
                                       httpx.Response(status, headers=headers))
                with self.assertRaises(ServiceError) as error:
                    adapter.fetch(legacy, parts=['fulltext'])
                self.assertEqual(error.exception.result['code'], code)
                self.assertEqual(self.calls, [legacy])

    def test_disabled_or_removed_output_metadata_is_not_followed(self):
        legacy = 'https://files01.core.ac.uk/download/pdf/287883844.pdf'
        current = 'https://core.ac.uk/download/287883844.pdf'
        for state in ({'fulltextStatus': 'disabled', 'deleted': 'ALLOWED'},
                      {'fulltextStatus': 'enabled', 'deleted': 'REMOVED'}):
            with self.subTest(state=state):
                def handle(request):
                    if request.url.host == 'files01.core.ac.uk':
                        return httpx.Response(404)
                    if request.url.host == 'api.core.ac.uk':
                        return httpx.Response(200, json={'id': 287883844, 'downloadUrl': current, **state})
                    self.fail('Disabled or removed output URL was followed')
                adapter = self.adapter(handle)
                with self.assertRaises(ServiceError) as error:
                    adapter.fetch(legacy, parts=['fulltext'])
                self.assertEqual(error.exception.result['code'], 'not_found_at_source')
                self.assertEqual(error.exception.result['resolution_error_code'], 'fulltext_not_available')
                self.assertEqual(self.calls, [legacy, 'https://api.core.ac.uk/v3/outputs/287883844'])

    def test_failed_legacy_resolution_preserves_both_failure_stages(self):
        legacy = 'https://files01.core.ac.uk/download/pdf/287883844.pdf'
        def handle(request):
            if request.url.host == 'files01.core.ac.uk':
                return httpx.Response(404)
            return httpx.Response(503)
        adapter = self.adapter(handle)
        with self.assertRaises(ServiceError) as error:
            adapter.fetch(legacy, parts=['fulltext'])
        self.assertEqual(error.exception.result['code'], 'not_found_at_source')
        self.assertEqual(error.exception.result['http_status'], 404)
        self.assertEqual(error.exception.result['resolution_error_code'], 'provider_error')
        self.assertEqual(error.exception.result['resolution_http_status'], 503)

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
