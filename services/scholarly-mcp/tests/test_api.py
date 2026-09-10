"""Recorded provider responses and isolated error/source-boundary cases."""
import importlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
import httpx
import inspect

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scholarly import ArtifactStore, ServiceError


class APIContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not (ROOT / "api_adapters.py").exists():
            raise AssertionError("Source-specific API adapters are absent")
        cls.mod = importlib.import_module("api_adapters")

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.store = ArtifactStore(self.tmp.name)
        self.calls = []

    def adapter(self, source, response):
        def serve(request):
            self.calls.append(request)
            return response(request)
        client = httpx.Client(transport=httpx.MockTransport(serve))
        self.addCleanup(client.close)
        return self.mod.make_adapters(self.store, client=client)[source]

    def test_crossref_preserves_native_query_filters_all_received_fields_and_range(self):
        raw = (ROOT / "tests/fixtures/crossref.json").read_bytes()
        adapter = self.adapter("crossref", lambda req: httpx.Response(200, content=raw, headers={"Content-Type": "application/json"}))
        result = adapter.search("P versus NP", options={"filter": "from-pub-date:1970-01-01"}, start=0, limit=2)
        self.assertEqual(self.calls[0].url.params["query"], "P versus NP")
        self.assertEqual(self.calls[0].url.params["filter"], "from-pub-date:1970-01-01")
        records = self.store.read(result["records"]["ref"])[1]
        self.assertEqual(json.loads(records), json.loads(raw)["message"]["items"])
        self.assertEqual(result["received"], 2)
        self.assertTrue(result["has_more"])

    def test_rate_limit_is_an_error_with_retry_information_not_absence(self):
        adapter = self.adapter("crossref", lambda req: httpx.Response(429, headers={"Retry-After": "60"}, json={"message": "too many requests"}))
        with self.assertRaises(ServiceError) as cm:
            adapter.search("NP", options={}, start=0, limit=1)
        self.assertEqual(cm.exception.result["code"], "rate_limited")
        self.assertEqual(cm.exception.result["retry_after"], "60")
        self.assertEqual(len(self.calls), 1)

    def test_html_challenge_with_http_200_is_not_a_valid_api_response(self):
        adapter = self.adapter("dblp", lambda req: httpx.Response(200, headers={"Content-Type": "text/html"}, text="<html>Verify you are human</html>"))
        with self.assertRaises(ServiceError) as cm:
            adapter.search("NP", options={}, start=0, limit=1)
        self.assertEqual(cm.exception.result["status"], "restricted")

    def test_binary_request_rejects_html_before_preserving_a_form_token(self):
        token = 'synthetic-hidden-form-credential-for-test'
        client = httpx.Client(transport=httpx.MockTransport(lambda req: httpx.Response(200, headers={'Content-Type': 'text/html'}, text='<html><form><input name="_token" value="' + token + '"></form></html>')))
        self.addCleanup(client.close)
        adapter = self.mod.APIAdapter(self.store, client)
        adapter.source, adapter.hosts = 'drops', ('drops.dagstuhl.de',)
        with self.assertRaises(ServiceError):
            adapter.request('https://drops.dagstuhl.de/example.pdf', accept='binary')
        self.assertFalse(any(token.encode() in p.read_bytes() for p in Path(self.tmp.name).rglob('*') if p.is_file()))

    def test_explicit_html_request_preserves_content_after_removing_form_values(self):
        token = 'synthetic-hidden-form-credential-for-test'
        adapter = self.adapter('numdam', lambda req: httpx.Response(200, headers={'Content-Type': 'text/html'}, text='<html><pre>citation</pre><input name="_token" value="' + token + '"><script>hidden</script></html>'))
        raw, evidence = adapter.request('https://www.numdam.org/', accept='html')
        stored = self.store.read(evidence['ref'])[1]
        self.assertIn(b'citation', stored)
        self.assertNotIn(token.encode(), stored)
        self.assertNotIn(b'<script', stored)

    def test_cross_source_target_and_redirect_are_rejected(self):
        adapter = self.adapter("arxiv", lambda req: httpx.Response(302, headers={"Location": "https://api.crossref.org/works"}))
        with self.assertRaises(ServiceError):
            adapter.fetch("https://example.org/document.pdf", parts=["fulltext"])
        self.assertEqual(len(self.calls), 0)
        with self.assertRaises(ServiceError) as cm:
            adapter.search("ti:NP", options={}, start=0, limit=1)
        self.assertEqual(cm.exception.result["code"], "source_boundary")
        self.assertEqual(len(self.calls), 1)

    def test_unsupported_filter_is_not_silently_ignored(self):
        adapter = self.adapter("crossref", lambda req: httpx.Response(200, json={}))
        with self.assertRaises(ServiceError) as cm:
            adapter.search("NP", options={"made_up_filter": True}, start=0, limit=1)
        self.assertEqual(cm.exception.result["code"], "invalid_options")
        self.assertEqual(len(self.calls), 0)

    def test_arxiv_atom_results_retain_version_abstract_and_supplement_links(self):
        raw = (ROOT / "tests/fixtures/arxiv.xml").read_bytes()
        adapter = self.adapter("arxiv", lambda req: httpx.Response(200, content=raw, headers={"Content-Type": "application/atom+xml"}))
        result = adapter.search('ti:"P versus NP"', options={}, start=0, limit=2)
        rows = json.loads(self.store.read(result["records"]["ref"])[1])
        self.assertEqual(len(rows), 2)
        self.assertRegex(rows[0]["id"], r"v[0-9]+$")
        self.assertTrue(rows[0]["abstract"])
        self.assertTrue(rows[0]["links"])

    def test_public_api_implementation_has_no_separate_api_credential_input(self):
        self.assertNotIn("secrets", inspect.signature(self.mod.make_adapters).parameters)
        from registry import SOURCES
        for source in ("scopus", "wos", "ieee-xplore", "science-direct", "springer"):
            with self.subTest(source=source):
                self.assertEqual(SOURCES[source].transport, "playwright")

    def test_opencitations_keeps_citation_edges_and_does_not_fetch_cited_papers(self):
        raw = (ROOT / "tests/fixtures/opencitations.json").read_bytes()
        adapters = self.mod.make_adapters(self.store)
        self.assertIn("opencitations", adapters, "Public citation-graph adapter is absent")
        adapter = self.adapter("opencitations", lambda req: httpx.Response(200, content=raw, headers={"Content-Type": "application/json"}))
        result = adapter.search("doi:10.1145/321250.321251", options={"direction": "references"}, limit=2)
        self.assertEqual(len(self.calls), 1)
        self.assertEqual(result["total"], len(json.loads(raw)))
        self.assertEqual(json.loads(self.store.read(result["records"]["ref"])[1]), json.loads(raw)[:2])

    def test_opencitations_csv_preserves_native_table_and_selected_window(self):
        import csv, io
        raw = (ROOT / 'tests/fixtures/opencitations.csv').read_bytes()
        rows = list(csv.DictReader(io.StringIO(raw.decode('utf-8'))))
        adapter = self.adapter('opencitations', lambda req: httpx.Response(200, content=raw, headers={'Content-Type': 'text/csv'}))
        result = adapter.search('doi:10.1186/1756-8722-6-59', options={}, start=1, limit=2, export='csv')
        self.assertEqual(self.calls[0].headers['Accept'], 'text/csv')
        self.assertEqual(self.calls[0].url.params['format'], 'csv')
        self.assertEqual(self.store.read(result['native_export']['ref'])[1], raw)
        selected = list(csv.DictReader(io.StringIO(self.store.read(result['export']['ref'])[1].decode('utf-8'))))
        self.assertEqual(selected, rows[1:3])
        self.assertEqual(result['total'], len(rows))

    def test_opencitations_oci_fetch_and_parts_do_not_retrieve_papers(self):
        raw = [{'oci': '06101801781-06180334099', 'citing': 'doi:10.7717/peerj-cs.421', 'cited': 'doi:10.1108/jd-12-2013-0166'}]
        adapter = self.adapter('opencitations', lambda req: httpx.Response(200, json=raw))
        result = adapter.fetch('oci:06101801781-06180334099', parts=['metadata', 'fulltext'])
        self.assertEqual(self.calls[0].url.path, '/index/v2/citation/06101801781-06180334099')
        self.assertEqual(len(self.calls), 1)
        self.assertEqual(result['status'], 'partial')
        self.assertEqual(result['components']['fulltext']['status'], 'not_offered')
        self.assertEqual(result['components']['metadata']['status'], 'available')

    def test_numdam_oai_metadata_preserves_jats_and_observed_fulltext_links(self):
        raw = (ROOT / "tests/fixtures/numdam.xml").read_bytes()
        adapters = self.mod.make_adapters(self.store)
        self.assertIn("numdam", adapters, "Public Numdam metadata adapter is absent")
        adapter = self.adapter("numdam", lambda req: httpx.Response(200, content=raw, headers={"Content-Type": "text/xml"}))
        result = adapter.fetch("AIF_1956__6__1_0", parts=["metadata"])
        self.assertEqual(result["status"], "ok")
        self.assertEqual(len(self.calls), 1)
        records = json.loads(self.store.read(result["records"]["ref"])[1])
        self.assertIn("Géométrie", records[0]["title"])
        self.assertTrue(any(link.get("media_type") == "application/pdf" for link in records[0]["links"]))

    def test_github_file_retrieval_pins_branch_before_reading_content(self):
        import base64
        adapters = self.mod.make_adapters(self.store, client=httpx.Client(transport=httpx.MockTransport(lambda r: httpx.Response(500))))
        self.assertIn("github", adapters, "Public GitHub artifact adapter is absent")
        sha = "a" * 40
        def response(req):
            if "/commits/" in req.url.path:
                return httpx.Response(200, json={"sha": sha, "commit": {"message": "fixture commit"}})
            self.assertEqual(req.url.params["ref"], sha)
            return httpx.Response(200, json={"type": "file", "name": "lean-toolchain", "encoding": "base64", "content": base64.b64encode(b"leanprover/lean4:v4.22.0\n").decode()})
        adapter = self.adapter("github", response)
        result = adapter.fetch("leanprover-community/mathlib4@master:lean-toolchain", parts=["metadata", "fulltext"])
        self.assertEqual(result["revision"], sha)
        self.assertEqual(self.store.read(result["components"]["fulltext"]["artifact"]["ref"])[1], b"leanprover/lean4:v4.22.0\n")
        self.assertEqual(len(self.calls), 2)

    def test_software_heritage_origin_urls_remain_identifiers_not_external_fetches(self):
        adapters = self.mod.make_adapters(self.store, client=httpx.Client(transport=httpx.MockTransport(lambda r: httpx.Response(500))))
        self.assertIn("software-heritage", adapters, "Public software preservation adapter is absent")
        def response(req):
            self.assertEqual(req.url.host, "archive.softwareheritage.org")
            return httpx.Response(200, json={"url": "https://github.com/leanprover-community/mathlib4", "origin_visits_url": "https://archive.softwareheritage.org/api/1/origin/x/visits/"})
        adapter = self.adapter("software-heritage", response)
        result = adapter.fetch("https://github.com/leanprover-community/mathlib4", parts=["metadata"])
        self.assertEqual(result["status"], "ok")
        self.assertEqual(len(self.calls), 1)

    def test_software_heritage_uses_provider_cursor_instead_of_ignored_offset(self):
        def response(req):
            if req.url.params.get("page_token") == "NEXT-OPAQUE":
                return httpx.Response(200, json=[{"url": "https://example.org/second"}])
            return httpx.Response(200, json=[{"url": "https://example.org/first"}], headers={"Link": '<https://archive.softwareheritage.org/api/1/origin/search/mathlib/?limit=1&page_token=NEXT-OPAQUE>; rel="next"'})
        adapter = self.adapter("software-heritage", response)
        first = adapter.search("mathlib", options={}, limit=1)
        self.assertEqual(first["next"].get("cursor"), "NEXT-OPAQUE")
        second = adapter.search("mathlib", options={}, limit=1, cursor=first["next"]["cursor"])
        self.assertFalse(second["has_more"])
        self.assertEqual(json.loads(self.store.read(second["records"]["ref"])[1])[0]["url"], "https://example.org/second")


if __name__ == "__main__":
    unittest.main()
