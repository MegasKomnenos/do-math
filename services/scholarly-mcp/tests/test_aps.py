import importlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
import httpx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scholarly import ArtifactStore


class APSContract(unittest.TestCase):
    def test_keyless_metadata_keeps_full_authorship_without_large_preview(self):
        self.assertTrue((ROOT / "aps.py").exists(), "APS public adapter is absent")
        mod = importlib.import_module("aps")
        fixture = (ROOT / "tests/fixtures/aps-article.json").read_bytes()
        def serve(request):
            self.assertNotIn("authorization", request.headers)
            self.assertNotIn("x-api-key", request.headers)
            return httpx.Response(200, content=fixture, headers={"Content-Type": "application/json"})
        with tempfile.TemporaryDirectory() as folder, httpx.Client(transport=httpx.MockTransport(serve)) as client:
            store = ArtifactStore(folder)
            result = mod.APS(store, client=client).fetch("10.1103/PhysRevLett.116.061102", parts=["metadata", "abstract"])
            self.assertEqual(result["status"], "ok")
            self.assertLess(len(json.dumps(result)), 12000)
            data = json.loads(store.read(result["records"]["ref"])[1])
            self.assertGreater(len(data[0]["authors"]), 100)


if __name__ == "__main__":
    unittest.main()
