import importlib
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scholarly import Sanitizer, ServiceError


class BrowserContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not (ROOT / "browser_adapters.py").exists():
            raise AssertionError("The KUDOS gateway and browser adapter are absent")
        cls.mod = importlib.import_module("browser_adapters")

    def test_record_identity_is_taken_from_the_result_record_not_linked_references(self):
        raw = (ROOT / "tests/fixtures/mathscinet-article.html").read_text("utf-8")
        row = self.mod.mathscinet_record(raw, "https://mathscinet-ams-org.libproxy.knu.ac.kr/mathscinet/publications-search", Sanitizer())
        self.assertEqual(row["id"], "MR4048204")
        self.assertEqual(row["title"], "From classical proof theory to P versus NP: a guide to bounded theories")
        self.assertIn("Tzameret", row["text"])
        self.assertTrue(row["url"].endswith("article?mr=4048204"))

    def test_html_retains_original_math_but_excludes_session_inputs_and_active_scripts(self):
        raw = '<main><p>A<script type="math/tex">x^{2}</script></p><script>session="SECRET"</script><input type="hidden" value="SECRET"><a href="https://example.org/a?token=SECRET&q=NP">link</a></main>'
        cleaned = self.mod.clean_html(raw, Sanitizer(["SECRET"]))
        self.assertIn("x^{2}", cleaned)
        self.assertNotIn("SECRET", cleaned)
        self.assertNotIn("<input", cleaned)
        self.assertNotIn('session=', cleaned)
        self.assertIn("q=NP", cleaned)

    def test_html_form_wrapper_does_not_delete_publication_results(self):
        raw = '<main><form><input type="checkbox" name="10.1145/example"><article><h5>The complexity of theorem-proving procedures</h5><p>1971</p></article></form></main>'
        cleaned = self.mod.clean_html(raw, Sanitizer())
        self.assertIn("The complexity of theorem-proving procedures", cleaned)
        self.assertIn("1971", cleaned)
        self.assertNotIn("<form", cleaned)

    def test_relative_export_links_are_sanitized_in_preserved_html(self):
        cleaned = self.mod.clean_html('<a href="/export?_csrf=PRIVATE-CSRF&amp;format=RIS">Export</a>', Sanitizer())
        self.assertNotIn("PRIVATE-CSRF", cleaned)
        self.assertIn("format=RIS", cleaned)

    def test_cached_login_still_registers_credentials_for_output_redaction(self):
        import tempfile
        with tempfile.TemporaryDirectory() as folder:
            Path(folder, "kudos.md").write_text("ID: private-test-user\nPW: private-test-password\n", "utf-8")
            sanitizer = Sanitizer()
            self.mod.KudosGateway(folder, sanitizer)
            self.assertEqual(sanitizer.text("private-test-user private-test-password"), "[REDACTED] [REDACTED]")

    def test_browser_document_redirect_outside_named_source_is_rejected(self):
        from types import SimpleNamespace
        self.assertTrue(hasattr(self.mod, "goto_source"), "Browser document boundary helper is absent")
        page = SimpleNamespace(url="https://source.example/article")
        def navigate(url, **kwargs):
            page.url = "https://another-publisher.example/article"
        page.goto = navigate
        with self.assertRaises(ServiceError) as raised:
            self.mod.goto_source(page, "https://source.example/article", {"source.example"})
        self.assertEqual(raised.exception.result["code"], "source_boundary")

    def test_browser_download_timeout_has_a_safe_typed_result(self):
        from types import SimpleNamespace
        from playwright.sync_api import TimeoutError as BrowserTimeout
        def get(*args, **kwargs):
            raise BrowserTimeout("signed URL must not enter the error result")
        context = SimpleNamespace(request=SimpleNamespace(get=get))
        with self.assertRaises(ServiceError) as raised:
            self.mod.browser_download(context, "https://source.example/file.pdf", {"source.example"})
        self.assertEqual(raised.exception.result["code"], "timeout")
        self.assertNotIn("signed URL", str(raised.exception.result))

    def test_browser_download_does_not_request_an_external_redirect(self):
        from types import SimpleNamespace
        calls = []
        def get(url, **kwargs):
            calls.append(url)
            return SimpleNamespace(status=302, headers={"location": "https://other.example/file.pdf?token=PRIVATE"}, url=url)
        context = SimpleNamespace(request=SimpleNamespace(get=get))
        with self.assertRaises(ServiceError) as raised:
            self.mod.browser_download(context, "https://source.example/file.pdf", {"source.example"})
        self.assertEqual(len(calls), 1)
        self.assertEqual(raised.exception.result["code"], "source_boundary")
        self.assertEqual(raised.exception.result["blocked_host"], "other.example")
        self.assertNotIn("PRIVATE", str(raised.exception.result))

    def test_citation_post_redirect_switches_to_get_without_replaying_form(self):
        from types import SimpleNamespace
        calls=[]
        def post(url,**kwargs):
            calls.append(('POST',url,kwargs))
            return SimpleNamespace(status=303,headers={'location':'/citation.bib'},url=url)
        def get(url,**kwargs):
            calls.append(('GET',url,kwargs))
            return SimpleNamespace(status=200,headers={'content-type':'text/plain'},url=url,body=lambda:b'@article{x,title={Example}}')
        context=SimpleNamespace(request=SimpleNamespace(get=get,post=post))
        data,media,url=self.mod.browser_download(context,'https://source.example/export',{'source.example'},form={'doi':'10.1234/a&b','format':'bibtex'})
        self.assertEqual([c[0] for c in calls],['POST','GET'])
        self.assertIn('doi=10.1234%2Fa%26b',calls[0][2]['data'])
        self.assertNotIn('data',calls[1][2])
        self.assertEqual(url,'https://source.example/citation.bib')

    def test_citation_post_cannot_replay_form_to_another_source(self):
        from types import SimpleNamespace
        calls=[]
        def post(url,**kwargs):
            calls.append(url)
            return SimpleNamespace(status=307,headers={'location':'https://other.example/export'},url=url)
        context=SimpleNamespace(request=SimpleNamespace(post=post))
        with self.assertRaises(ServiceError) as raised:
            self.mod.browser_download(context,'https://source.example/export',{'source.example'},form={'doi':'10.1234/x'})
        self.assertEqual(calls,['https://source.example/export'])
        self.assertEqual(raised.exception.result['code'],'source_boundary')

    def test_fulltext_target_cannot_expand_mathscinet_into_another_provider(self):
        for target in ["https://www.sciencedirect.com/science/article/pii/X", "https://evil.libproxy.knu.ac.kr/mathscinet/article?mr=1"]:
            with self.subTest(target=target), self.assertRaises(ServiceError):
                self.mod.mathscinet_target(target)
        self.assertEqual(self.mod.mathscinet_target("MR2733384"), "2733384")

    def test_wos_stream_count_uses_source_records_and_keeps_every_received_record(self):
        import json
        events = json.loads((ROOT / "tests/fixtures/wos-search.json").read_text("utf-8"))
        raw = "\n".join(json.dumps(event) for event in events)
        self.assertTrue(hasattr(self.mod, "wos_events"), "WOS streaming browser-response parser is absent")
        result = self.mod.wos_events(raw)
        self.assertEqual(result["total"], 18)
        self.assertEqual(len(result["records"]), 18)

    def test_eccc_keeps_native_duplicate_hits_and_labels_snippets(self):
        self.assertTrue(hasattr(self.mod, "eccc_records"), "ECCC browser result parser is absent")
        raw = (ROOT / "tests/fixtures/eccc-search.html").read_text("utf-8")
        rows = self.mod.eccc_records(raw)
        self.assertEqual(sum(r["id"] == "TR23-135" for r in rows), 2)
        self.assertIn("snippet", rows[0])
        self.assertNotIn("abstract", rows[0])

    def test_eccc_revision_metadata_keeps_original_and_revised_downloads_separate(self):
        self.assertTrue(hasattr(self.mod, "eccc_versions"), "ECCC revision parser is absent")
        raw = (ROOT / "tests/fixtures/eccc-report.html").read_text("utf-8")
        versions = self.mod.eccc_versions(raw)
        self.assertEqual({v["revision"] for v in versions}, {0, 1})
        revised = next(v for v in versions if v["revision"] == 1)
        self.assertIn("$A:", revised["abstract"])
        self.assertTrue(revised["pdf"].endswith("/revision/1/download"))

    def test_acm_keeps_original_and_reprint_separate_and_preserves_title_spaces(self):
        self.assertTrue(hasattr(self.mod, "acm_records"), "ACM result parser is absent")
        raw = (ROOT / "tests/fixtures/acm-search.html").read_text("utf-8")
        records = self.mod.acm_records(raw, "https://dl-acm-org.libproxy.knu.ac.kr/")
        self.assertEqual({r["id"] for r in records}, {"10.1145/3588287.3588297", "10.1145/800157.805047"})
        original = next(r for r in records if r["id"] == "10.1145/800157.805047")
        self.assertEqual(original["title"], "The complexity of theorem-proving procedures")



if __name__ == "__main__":
    unittest.main()
