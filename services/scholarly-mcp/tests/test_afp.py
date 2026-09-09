import importlib
from pathlib import Path
import sys
import tempfile
import unittest
import httpx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scholarly import ArtifactStore


class AFPContract(unittest.TestCase):
    def test_file_is_fetched_at_resolved_mercurial_revision_without_credentials(self):
        self.assertTrue((ROOT / "afp.py").exists(), "AFP adapter is absent")
        mod = importlib.import_module("afp")
        commit = "1" * 40
        calls = []
        def respond(request):
            calls.append(request)
            self.assertNotIn("authorization", request.headers)
            self.assertNotIn("private-token", request.headers)
            if request.url.path.endswith("/repository/commits"):
                return httpx.Response(200, json=[{"id": commit, "hg_id": commit}])
            if "/repository/files/" in request.url.path:
                self.assertEqual(request.url.params["ref"], commit)
                return httpx.Response(200, content=b'theory Sample imports Main begin\nend\n', headers={"Content-Type": "text/plain"})
            return httpx.Response(200, json={"path_with_namespace": "isa-afp/afp-devel", "default_branch": "branch/default", "vcs_type": "hg"})
        with tempfile.TemporaryDirectory() as folder, httpx.Client(transport=httpx.MockTransport(respond)) as client:
            store = ArtifactStore(folder)
            adapter = mod.AFP(store, client=client)
            result = adapter.fetch("afp-devel@branch/default:thys/Sample/Sample.thy", parts=["metadata", "fulltext"])
            self.assertEqual(result["status"], "ok")
            self.assertEqual(result["commit"], commit)
            self.assertEqual(store.read(result["components"]["fulltext"]["artifact"]["ref"])[1], b'theory Sample imports Main begin\nend\n')


if __name__ == "__main__":
    unittest.main()
