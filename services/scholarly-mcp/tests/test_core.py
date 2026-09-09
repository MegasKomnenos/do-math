"""Common contracts: preservation, bounded reads, source and credential boundaries."""
import importlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class CoreContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not (ROOT / "scholarly.py").is_file():
            raise AssertionError("The scholarly MCP implementation required by the handoff is absent")
        cls.lib = importlib.import_module("scholarly")

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.store = self.lib.ArtifactStore(Path(self.tmp.name))

    def test_same_bytes_from_different_sources_keep_separate_provenance(self):
        left = self.store.put(b"same document", "text/plain", "arxiv", "https://arxiv.org/abs/1234.5678v2")
        right = self.store.put(b"same document", "text/plain", "eccc", "https://eccc.weizmann.ac.il/report/2020/1/")
        self.assertEqual(left["sha256"], right["sha256"])
        self.assertNotEqual(left["ref"], right["ref"])
        self.assertEqual(self.store.read(left["ref"])[0]["source"], "arxiv")
        self.assertEqual(self.store.read(right["ref"])[0]["source"], "eccc")

    def test_saved_artifact_survives_new_server_instance(self):
        a = self.store.put("수식 α²".encode(), "text/plain", "eccc", "https://eccc.weizmann.ac.il/")
        reopened = self.lib.ArtifactStore(Path(self.tmp.name))
        self.assertEqual(reopened.read(a["ref"])[1].decode(), "수식 α²")

    def test_arbitrary_files_and_traversal_are_not_artifact_references(self):
        for value in ["../../.credentials/kudos.md", "C:/math/.credentials/kudos.md", "file:///C:/math/.credentials/kudos.md"]:
            with self.subTest(value=value), self.assertRaises(self.lib.ServiceError):
                self.store.read(value)

    def test_fields_and_record_window_preserve_missing_and_null(self):
        rows = [{"title": "one", "abstract": None}, {"title": "two"}, {"title": "three", "abstract": "α²"}]
        a = self.store.put(json.dumps(rows, ensure_ascii=False).encode(), "application/json", "crossref", "https://api.crossref.org/works")
        out = self.lib.extract_artifact(self.store, a["ref"], fields=["title", "abstract"], start=1, count=2)
        self.assertEqual(out["items"], rows[1:])
        self.assertEqual(out["total"], 3)
        self.assertEqual(out["returned"], 2)
        self.assertEqual(out["missing_fields"], [{"index": 1, "fields": ["abstract"]}])

    def test_long_output_is_recoverable_with_exact_next_position(self):
        a = self.store.put(("가나다\n" * 1000).encode(), "text/plain", "eccc", "https://eccc.weizmann.ac.il/")
        out = self.lib.extract_artifact(self.store, a["ref"], start=7, count=11)
        self.assertEqual(out["total"], 1000)
        self.assertEqual(out["next_start"], 18)
        self.assertEqual(len(out["items"]), 11)

    def test_secret_values_and_token_urls_are_redacted(self):
        clean = self.lib.Sanitizer(["PRIVATE-SECRET-123"])
        raw = {"url": "https://api.example.org/doc?q=NP&api_key=PRIVATE-SECRET-123#token=abc", "text": "error PRIVATE-SECRET-123", "Authorization": "Bearer anything"}
        result = clean.value(raw)
        serial = json.dumps(result)
        self.assertNotIn("PRIVATE-SECRET-123", serial)
        self.assertNotIn("anything", serial)
        self.assertNotIn("token=abc", serial)
        self.assertIn("q=NP", serial)

    def test_invalid_ranges_do_not_silently_wrap_or_return_all(self):
        a = self.store.put(b"first\nsecond", "text/plain", "eccc", "https://eccc.weizmann.ac.il/")
        for options in [{"start": -1}, {"count": 0}, {"count": -1}]:
            with self.subTest(options=options), self.assertRaises(self.lib.ServiceError):
                self.lib.extract_artifact(self.store, a["ref"], **options)

    def test_native_mathscinet_bibtex_export_is_readable_as_five_records(self):
        data = (ROOT / "tests/fixtures/mathscinet.bib").read_bytes()
        artifact = self.store.put(data, "application/x-bibtex", "mathscinet", "https://mathscinet.ams.org/mathscinet/")
        result = self.lib.extract_artifact(self.store, artifact["ref"], count=5)
        self.assertEqual(result["total"], 5)
        self.assertEqual(result["items"][0]["id"], "MR4048204")
        self.assertIn("{P}", result["items"][0]["title"])

    def test_acm_native_citations_retain_distinct_publication_years(self):
        data = (ROOT / "tests/fixtures/acm.bib").read_bytes()
        artifact = self.store.put(data, "application/x-bibtex", "acm-dl", "https://dl.acm.org/")
        result = self.lib.extract_artifact(self.store, artifact["ref"], count=5)
        self.assertEqual(result["total"], 2)
        self.assertEqual({r["year"] for r in result["items"]}, {"1971", "2023"})

    def test_session_identifiers_are_excluded_from_browser_response_evidence(self):
        clean = self.lib.Sanitizer()
        result = clean.value({"url": "https://www.webofscience.com/search?SID=PRIVATE-SESSION&query=NP", "access_token": "PRIVATE-ACCESS", "csrfToken": "PRIVATE-CSRF"})
        self.assertNotIn("PRIVATE-", json.dumps(result))

    def test_embedded_authenticated_urls_in_text_exports_are_sanitized(self):
        clean = self.lib.Sanitizer()
        text = 'UR https://www.webofscience.com/record?SID=PRIVATE-SESSION&query=NP\n'
        result = clean.text(text)
        self.assertNotIn("PRIVATE-SESSION", result)
        self.assertIn("query=NP", result)

    def test_url_redaction_preserves_bibtex_delimiters(self):
        original = '@article{x, title={A}, url={https://example.org/p?SID=PRIVATE&q=NP}}\n'
        cleaned = self.lib.Sanitizer().text(original)
        self.assertEqual(cleaned, '@article{x, title={A}, url={https://example.org/p?q=NP}}\n')

    def test_relative_url_fields_do_not_expose_request_forgery_tokens(self):
        value = {"href": "/export?_csrf=PRIVATE-CSRF&format=RIS", "url": "/document?SID=PRIVATE-SID&id=1"}
        cleaned = self.lib.Sanitizer().value(value)
        self.assertNotIn("PRIVATE-", str(cleaned))
        self.assertEqual(cleaned["href"], "/export?format=RIS")

    def test_wos_native_export_keeps_full_records_and_cited_references(self):
        data = (ROOT / "tests/fixtures/wos.txt").read_bytes()
        artifact = self.store.put(data, "application/x-wos", "wos", "https://www.webofscience.com/")
        result = self.lib.extract_artifact(self.store, artifact["ref"], count=5)
        self.assertEqual(result["total"], 5)
        self.assertEqual(result["items"][0]["fields"]["ti"], ["P versus NP and geometry"])
        self.assertEqual(len(result["items"][0]["fields"]["cr"]), 47)

    def test_archive_members_are_read_without_extracting_paths_into_the_workspace(self):
        import io, zipfile
        archive = io.BytesIO()
        with zipfile.ZipFile(archive, "w") as zipped:
            zipped.writestr("../outside.txt", "archive bytes, not a filesystem write")
            zipped.writestr("repo/Mathlib/Test.lean", "theorem example : True := True.intro\n")
            zipped.writestr("repo/data.json", '{ "precision": 1.234567890123456789, "access_token": "documentation-example" }\n')
            zipped.writestr("repo/references.bib", '@article{example, title={Exact title}, year={2025}}\n')
        ref = self.store.put(archive.getvalue(), "application/zip", "github", "https://api.github.com/repos/test/test/zipball/x")
        result = self.lib.extract_artifact(self.store, ref["ref"], selection="repo/Mathlib/Test.lean")
        child = result["items"][0]["artifact"]
        self.assertEqual(self.store.read(child["ref"])[1], b"theorem example : True := True.intro\n")
        self.assertFalse((Path(self.tmp.name).parent / "outside.txt").exists())
        data = self.lib.extract_artifact(self.store, ref["ref"], selection="repo/data.json")["items"][0]["artifact"]
        self.assertEqual(self.store.read(data["ref"])[1], b'{ "precision": 1.234567890123456789, "access_token": "documentation-example" }\n')
        citation = self.lib.extract_artifact(self.store, ref["ref"], selection="repo/references.bib")["items"][0]["artifact"]
        parsed = self.lib.extract_artifact(self.store, citation["ref"], fields=["title"], count=1)
        self.assertEqual(parsed["items"][0]["title"], "Exact title")

    def test_public_commit_signatures_and_pagination_are_not_authentication_secrets(self):
        original = {"signature": "-----BEGIN PGP SIGNATURE-----\npublic verification data", "page_token": "public-pagination", "token_count": 42}
        self.assertEqual(self.lib.Sanitizer().value(original), original)
        payload = {"signature": original["signature"], "payload": "message https://Example.org/search?q=two%20words&sort=desc\n"}
        self.assertEqual(self.lib.Sanitizer().value(payload), payload)

    def test_signed_proquest_media_and_nested_viewer_urls_remove_access_parameters(self):
        from urllib.parse import quote, unquote
        link = "https://media.proquest.com/media/document?_a=PRIVATE-ACCESS&_s=PRIVATE-SIGNATURE&cit%3Atitle=Article"
        clean = self.lib.Sanitizer().url(link)
        self.assertNotIn("PRIVATE", clean)
        self.assertIn("Article", clean)
        nested = "/viewer.html?file=" + quote(link, safe="")
        self.assertNotIn("PRIVATE", unquote(self.lib.Sanitizer().url(nested)))

    def test_xml_url_redaction_preserves_well_formed_markup_and_namespace_values(self):
        raw = b'<r xmlns:x="urn:types" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="x:Record"><link>https://source.example/search?q=NP&amp;start=2&amp;token=PRIVATE</link></r>'
        artifact = self.store.put(raw, "application/xml", "source", "https://source.example/")
        result = self.lib.extract_artifact(self.store, artifact["ref"], selection="link", count=1)
        from xml.etree import ElementTree
        element = ElementTree.fromstring(result["items"][0])
        self.assertEqual(element.text, "https://source.example/search?q=NP&start=2")
        stored = self.store.read(artifact["ref"])[1]
        self.assertNotIn(b"PRIVATE", stored)
        self.assertIn(b'xmlns:x="urn:types"', stored)

    def test_bibtex_free_annotations_outside_entries_do_not_hide_records(self):
        text = b'Editorial note\n@article{one,title={First},year=2025}\n#OK\n@article{two,title={Second},journal=eccc}\n'
        artifact = self.store.put(text, "application/x-bibtex", "source", "https://source.example/references.bib")
        result = self.lib.extract_artifact(self.store, artifact["ref"], count=2)
        self.assertEqual([row["id"] for row in result["items"]], ["one", "two"])
        raw = self.lib.extract_artifact(self.store, artifact["ref"], selection="raw", start=2, count=1)
        self.assertEqual(raw["items"], ["#OK"])

    def test_xml_external_entities_are_not_read_from_preserved_source_files(self):
        private = Path(self.tmp.name) / "private.txt"
        private.write_text("PRIVATE FILE CONTENT", "utf-8")
        data = '<!DOCTYPE root [<!ENTITY external SYSTEM "' + private.as_uri() + '">]><root>&external;</root>'
        artifact = self.store.put(data, "application/xml", "source", "https://source.example/data.xml", preserve_bytes=True)
        with self.assertRaises(self.lib.ServiceError) as raised:
            self.lib.extract_artifact(self.store, artifact["ref"])
        self.assertEqual(raised.exception.result["code"], "xml_entities_not_supported")


if __name__ == "__main__":
    unittest.main()
