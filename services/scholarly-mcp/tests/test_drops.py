import importlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
import httpx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scholarly import ArtifactStore, ServiceError


class DropsContract(unittest.TestCase):
    def test_public_metadata_fetch_needs_no_browser_or_separate_credentials(self):
        self.assertTrue((ROOT / "drops.py").exists(), "DROPS adapter is absent")
        module = importlib.import_module("drops")
        raw = (ROOT / "tests/fixtures/drops-schema.json").read_bytes()
        calls = []
        def respond(request):
            calls.append(str(request.url))
            return httpx.Response(200, content=raw, headers={"Content-Type": "application/ld+json"})
        with tempfile.TemporaryDirectory() as tmp, httpx.Client(transport=httpx.MockTransport(respond)) as client:
            adapter = module.DROPS(ArtifactStore(tmp), gateway=None, client=client)
            result = adapter.fetch("10.4230/LIPIcs.CSL.2020.5", parts=["metadata", "abstract"])
            self.assertEqual(result["status"], "ok")
            self.assertEqual(len(calls), 1)
            row = json.loads(adapter.store.read(result["records"]["ref"])[1])[0]
            self.assertIn("Bounded Theories", row["headline"])
            with self.assertRaises(ServiceError):
                adapter.fetch("https://example.org/unrelated", parts=["metadata"])


if __name__ == "__main__":
    unittest.main()
