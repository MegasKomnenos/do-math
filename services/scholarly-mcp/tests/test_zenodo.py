import hashlib
import importlib
from pathlib import Path
import sys
import tempfile
import unittest
import httpx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scholarly import ArtifactStore


class ZenodoContract(unittest.TestCase):
    def run_fetch(self, content):
        mod = importlib.import_module("api_adapters")
        expected = b"original file bytes\n"
        def serve(request):
            if request.url.path.endswith("/content"):
                return httpx.Response(200, content=content, headers={"Content-Type": "text/plain"})
            return httpx.Response(200, json={"id": 42, "metadata": {"title": "Example", "description": "Record description"},
                "files": [{"key": "file.txt", "size": len(expected), "checksum": "md5:" + hashlib.md5(expected).hexdigest(),
                    "links": {"self": "https://zenodo.org/api/records/42/files/file.txt/content"}}]})
        with tempfile.TemporaryDirectory() as folder, httpx.Client(transport=httpx.MockTransport(serve)) as client:
            store = ArtifactStore(folder)
            result = mod.Zenodo(store, client=client).fetch("42", parts=["metadata", "fulltext"])
            if result["components"]["fulltext"]["status"] == "available":
                artifact = result["components"]["fulltext"]["artifacts"][0]["artifact"]
                self.assertEqual(store.read(artifact["ref"])[1], expected)
            return result

    def test_public_record_files_are_checked_against_provider_checksum(self):
        self.assertEqual(self.run_fetch(b"original file bytes\n")["status"], "ok")

    def test_corrupted_download_does_not_become_available_fulltext(self):
        result = self.run_fetch(b"corrupt file bytes\n")
        self.assertEqual(result["status"], "partial")
        self.assertEqual(result["components"]["fulltext"]["failures"][0]["code"], "file_integrity_mismatch")


if __name__ == "__main__":
    unittest.main()
