import importlib
from pathlib import Path
import sys
import tempfile
import unittest
import httpx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scholarly import ArtifactStore, ServiceError


class UnpaywallContract(unittest.TestCase):
    def test_contact_email_is_internal_and_oa_links_do_not_trigger_other_sources(self):
        self.assertTrue((ROOT / "unpaywall.py").exists(), "Unpaywall adapter is absent")
        mod = importlib.import_module("unpaywall")
        calls = []
        def response(request):
            calls.append(request)
            self.assertEqual(request.url.host, "api.unpaywall.org")
            self.assertEqual(request.url.params["email"], "private-contact@example.invalid")
            self.assertNotIn("authorization", request.headers)
            return httpx.Response(200, json={"doi": "10.1000/example", "title": "An example", "is_oa": True,
                "best_oa_location": {"url_for_pdf": "https://another-publisher.example/paper.pdf"}})
        with tempfile.TemporaryDirectory() as folder, httpx.Client(transport=httpx.MockTransport(response)) as client:
            store = ArtifactStore(folder)
            adapter = mod.Unpaywall(store, client=client, contact_email="private-contact@example.invalid")
            result = adapter.fetch("10.1000/example", parts=["metadata", "fulltext"])
            self.assertEqual(len(calls), 1)
            self.assertEqual(result["status"], "partial")
            self.assertEqual(result["components"]["fulltext"]["status"], "not_offered")
            self.assertNotIn("private-contact", str(result))

    def test_missing_contact_information_does_not_request_api_credentials(self):
        self.assertTrue((ROOT / "unpaywall.py").exists(), "Unpaywall adapter is absent")
        mod = importlib.import_module("unpaywall")
        with tempfile.TemporaryDirectory() as folder:
            adapter = mod.Unpaywall(ArtifactStore(folder))
            with self.assertRaises(ServiceError) as raised:
                adapter.fetch("10.1000/example", parts=["metadata"])
            self.assertEqual(raised.exception.result["code"], "contact_email_required")


if __name__ == "__main__":
    unittest.main()
