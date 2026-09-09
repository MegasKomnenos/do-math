import importlib
from pathlib import Path
import sys
import tempfile
import unittest
import httpx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scholarly import ArtifactStore, ServiceError


class EuDMLContract(unittest.TestCase):
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
