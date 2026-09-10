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
    def test_native_bibtex_uses_the_public_download_without_a_browser(self):
        from drops import DROPS
        raw = (ROOT / 'tests/fixtures/drops.bib').read_bytes()
        calls = []
        def respond(request):
            calls.append(request.url.path)
            return httpx.Response(200, content=raw, headers={'Content-Type': 'text/plain'})
        with tempfile.TemporaryDirectory() as temp, httpx.Client(transport=httpx.MockTransport(respond)) as client:
            adapter = DROPS(ArtifactStore(temp), None, client)
            artifact = adapter.native_export('https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.CSL.2020.5', 'bibtex')
            self.assertEqual(calls, ['/entities/document/10.4230/LIPIcs.CSL.2020.5/metadata/bibtex/download'])
            self.assertEqual(adapter.store.read(artifact['ref'])[1], raw)
            self.assertEqual(artifact['media_type'], 'application/x-bibtex')

    def test_native_xml_formats_validate_the_document_header(self):
        module = importlib.import_module('drops')
        for kind in ('xml', 'acm-xml', 'doaj-xml'):
            raw = (ROOT / 'tests/fixtures' / ('drops.' + kind + '.xml')).read_bytes()
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as temp, httpx.Client(transport=httpx.MockTransport(lambda req: httpx.Response(200, content=raw, headers={'Content-Type': 'application/xml'}))) as client:
                adapter = module.DROPS(ArtifactStore(temp), gateway=None, client=client)
                artifact = adapter.native_export('https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.CSL.2020.5', kind)
                self.assertEqual(artifact['format'], kind)
                with self.assertRaises(ServiceError) as cm:
                    adapter.native_export('https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.CSL.2020.6', kind)
                self.assertEqual(cm.exception.result['code'], 'identity_mismatch')

    def test_files_are_selected_from_the_current_document_file_section(self):
        from drops import file_links
        raw = '<a href="/storage/related.pdf">Related</a><section class="metadata files"><a href="/storage/paper.pdf">PDF</a><a href="/storage/paper.pdf">Thumb</a><a href="/storage/paper.html">HTML</a><a href="https://example.org/foreign.pdf">Other</a></section>'
        self.assertEqual(file_links(raw, 'https://drops.dagstuhl.de/'), ['https://drops.dagstuhl.de/storage/paper.pdf', 'https://drops.dagstuhl.de/storage/paper.html'])

    def test_artifact_xml_identifies_the_artifact_not_a_paper(self):
        from drops import DROPS
        raw = (ROOT / 'tests/fixtures/drops-artifact.xml').read_bytes()
        with tempfile.TemporaryDirectory() as temp, httpx.Client(transport=httpx.MockTransport(lambda req: httpx.Response(200, content=raw, headers={'Content-Type': 'application/xml'}))) as client:
            adapter = DROPS(ArtifactStore(temp), None, client)
            artifact = adapter.native_export('https://drops.dagstuhl.de/entities/artifact/10.4230/artifacts.27685', 'xml')
            self.assertEqual(artifact['format'], 'xml')

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
