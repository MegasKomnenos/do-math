import importlib
from pathlib import Path
import sys
import tempfile
import unittest
import httpx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scholarly import ArtifactStore, ServiceError
from waits import CONNECT_WAIT_S, SOURCE_WAIT_S


class EuDMLContract(unittest.TestCase):
    def test_real_book_catalogue_body_is_not_reported_as_fulltext(self):
        mod = importlib.import_module("eudml")
        data = (ROOT / "tests/fixtures/eudml-book.xml").read_bytes()
        with tempfile.TemporaryDirectory() as folder, httpx.Client(transport=httpx.MockTransport(lambda request: httpx.Response(200, content=data, headers={"Content-Type": "application/xml"}))) as client:
            result = mod.EuDML(ArtifactStore(folder), client=client).fetch("204358", parts=["metadata", "fulltext", "supplementary"])
            self.assertEqual(result["status"], "partial")
            self.assertEqual(result["target"], "204358")
            self.assertEqual(result["components"]["metadata"]["status"], "available")
            self.assertEqual(result["components"]["fulltext"]["status"], "not_offered")
            self.assertEqual(result["components"]["supplementary"]["status"], "available")
        changed = data.replace(b"urn:eudml:doc:204358", b"urn:eudml:doc:999999").replace(b"PPN577927043", b"provider:204358")
        with tempfile.TemporaryDirectory() as folder, httpx.Client(transport=httpx.MockTransport(lambda request: httpx.Response(200, content=changed, headers={"Content-Type": "application/xml"}))) as client:
            with self.assertRaises(ServiceError) as raised:
                mod.EuDML(ArtifactStore(folder), client=client).fetch("204358", parts=["metadata"])
            self.assertEqual(raised.exception.result["code"], "identity_mismatch")

    def test_article_and_nested_book_part_native_bodies_remain_fulltext(self):
        from xml.etree import ElementTree
        mod = importlib.import_module("eudml")
        article = ElementTree.fromstring((ROOT / "tests/fixtures/eudml-article.xml").read_bytes())
        body = ElementTree.SubElement(article, "body")
        section = ElementTree.SubElement(body, "sec")
        ElementTree.SubElement(section, "p").text = "Native article body."
        book = ElementTree.fromstring((ROOT / "tests/fixtures/eudml-book.xml").read_bytes())
        part = book.find("./body/book-part")
        part_body = ElementTree.SubElement(part, "body")
        ElementTree.SubElement(part_body, "p").text = "Native preface body."
        for target, data in (("196516", ElementTree.tostring(article)), ("204358", ElementTree.tostring(book))):
            with self.subTest(target=target), tempfile.TemporaryDirectory() as folder, httpx.Client(transport=httpx.MockTransport(lambda request, data=data: httpx.Response(200, content=data, headers={"Content-Type": "application/xml"}))) as client:
                result = mod.EuDML(ArtifactStore(folder), client=client).fetch(target, parts=["metadata", "fulltext", "supplementary"])
                self.assertEqual(result["status"], "ok")
                self.assertEqual(result["components"]["metadata"]["status"], "available")
                self.assertEqual(result["components"]["fulltext"]["status"], "available")
                self.assertEqual(result["components"]["supplementary"]["status"], "available")

    def test_cql_search_waits_for_observed_gateway_response_without_relaxing_common_client(self):
        mod = importlib.import_module("eudml")
        observed = {}
        def serve(request):
            observed.update(request.extensions["timeout"])
            observed["user_agent"] = request.headers["user-agent"]
            return httpx.Response(200, content=(ROOT / "tests/fixtures/eudml-search.xml").read_bytes(), headers={"Content-Type": "application/rss+xml"})
        with tempfile.TemporaryDirectory() as folder:
            with httpx.Client(transport=httpx.MockTransport(serve), timeout=httpx.Timeout(45, connect=20), headers={"User-Agent":"scholarly-mcp/0.1 (local scholarly research)"}) as client:
                result = mod.EuDML(ArtifactStore(folder), client=client).search('all="P versus NP"', options={}, start=0, limit=2, export="rss")
                self.assertEqual(result["received"], 2)
                self.assertEqual(observed["read"], SOURCE_WAIT_S)
                self.assertEqual(observed["connect"], CONNECT_WAIT_S)
                self.assertEqual(client.timeout.read, 45)
                self.assertEqual(observed["user_agent"], "scholarly-mcp/0.1 (local scholarly research)")

    def test_nlm_fetch_uses_observed_slow_ttfb_budget_without_relaxing_common_client(self):
        mod = importlib.import_module("eudml")
        observed = {}
        def serve(request):
            observed.update(request.extensions["timeout"])
            observed["user_agent"] = request.headers["user-agent"]
            return httpx.Response(200, content=(ROOT / "tests/fixtures/eudml-article.xml").read_bytes(), headers={"Content-Type": "application/xml"})
        with tempfile.TemporaryDirectory() as folder:
            with httpx.Client(transport=httpx.MockTransport(serve), timeout=httpx.Timeout(45, connect=20), headers={"User-Agent":"scholarly-mcp/0.1 (local scholarly research)"}) as client:
                mod.EuDML(ArtifactStore(folder), client=client).fetch("196516", parts=["metadata"])
                self.assertEqual(observed["read"], SOURCE_WAIT_S)
                self.assertEqual(observed["connect"], CONNECT_WAIT_S)
                self.assertEqual(observed["user_agent"], f"python-httpx/{httpx.__version__}")
                self.assertEqual(client.headers["User-Agent"], "scholarly-mcp/0.1 (local scholarly research)")
                self.assertEqual(client.timeout.read, 45)

    def test_rss_range_and_publication_year_are_distinct_from_feed_dates(self):
        self.assertTrue((ROOT / "eudml.py").exists(), "EuDML adapter is absent")
        mod = importlib.import_module("eudml")
        rows, total, offset = mod.parse_rss((ROOT / "tests/fixtures/eudml-search.xml").read_bytes())
        self.assertEqual((total, offset, len(rows)), (8, 0, 2))
        self.assertEqual(rows[0]["id"], "196516")
        self.assertEqual(rows[0]["year"], "2001")
        self.assertIn("2016", rows[0]["pubDate"])

    def test_native_eudml_id_is_checked_and_external_pdf_is_not_downloaded(self):
        self.assertTrue((ROOT / "eudml.py").exists(), "EuDML adapter is absent")
        mod = importlib.import_module("eudml")
        calls = []
        def serve(request):
            calls.append(request)
            self.assertEqual(request.url.host, "eudml.org")
            self.assertIn("application/xml", request.headers["accept"])
            return httpx.Response(200, content=(ROOT / "tests/fixtures/eudml-article.xml").read_bytes(), headers={"Content-Type": "application/xml"})
        with tempfile.TemporaryDirectory() as folder, httpx.Client(transport=httpx.MockTransport(serve)) as client:
            result = mod.EuDML(ArtifactStore(folder), client=client).fetch("196516", parts=["metadata", "fulltext"])
            self.assertEqual(len(calls), 1)
            self.assertEqual(result["status"], "partial")
            self.assertEqual(result["components"]["metadata"]["status"], "available")
            self.assertEqual(result["components"]["fulltext"]["status"], "not_offered")

    def test_cited_document_id_cannot_substitute_for_the_current_article_id(self):
        from xml.etree import ElementTree
        mod = importlib.import_module("eudml")
        tree = ElementTree.fromstring((ROOT / "tests/fixtures/eudml-article.xml").read_bytes())
        tree.find("./front/article-meta/article-id[@pub-id-type='eudml-id']").text = "urn:eudml:doc:999999"
        back = ElementTree.SubElement(tree, "back")
        ElementTree.SubElement(back, "pub-id", {"pub-id-type": "eudml-id"}).text = "urn:eudml:doc:196516"
        data = ElementTree.tostring(tree)
        with tempfile.TemporaryDirectory() as folder, httpx.Client(transport=httpx.MockTransport(lambda request: httpx.Response(200, content=data, headers={"Content-Type": "application/xml"}))) as client:
            with self.assertRaises(ServiceError) as raised:
                mod.EuDML(ArtifactStore(folder), client=client).fetch("196516", parts=["metadata"])
            self.assertEqual(raised.exception.result["code"], "identity_mismatch")


if __name__ == "__main__":
    unittest.main()
