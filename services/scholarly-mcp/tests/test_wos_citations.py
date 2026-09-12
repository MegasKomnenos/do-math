from pathlib import Path
import sys
import unittest
from unittest.mock import Mock
import json
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from browser_adapters import WebOfScience
from scholarly import ArtifactStore, ServiceError


class WOSCitingWorksContract(unittest.TestCase):
    def test_search_dispatches_an_incoming_citation_window_without_rewriting_the_target(self):
        adapter = WebOfScience(None, None)
        adapter.search_citations = Mock(return_value={"status": "ok", "kind": "citations"})
        result = adapter.search("WOS:000269418800023", options={"kind": "citations"}, start=19, limit=2, export="plain")
        self.assertEqual(result["kind"], "citations")
        adapter.search_citations.assert_called_once_with("WOS:000269418800023", start=19, limit=2, export="plain", sort="date-descending")

    def test_citation_search_rejects_an_unknown_export_before_opening_wos(self):
        adapter = WebOfScience(None, None)
        adapter.search_citations = Mock()
        with self.assertRaises(ServiceError) as raised:
            adapter.search("WOS:000269418800023", options={"kind": "citations"}, export="made-up")
        self.assertEqual(raised.exception.result["code"], "invalid_export")
        adapter.search_citations.assert_not_called()

    def test_native_citing_request_must_bind_the_selected_accession(self):
        adapter = WebOfScience(None, None)
        request = json.loads((ROOT / "tests/fixtures/wos-citing-request-sanitized.json").read_text("utf-8"))
        self.assertEqual(adapter.validate_citing_request(request, "WOS:000269418800023", "date-descending"), 50)
        request["search"]["parentId"]["value"] = "WOS:OTHER"
        with self.assertRaises(ServiceError) as raised:
            adapter.validate_citing_request(request, "WOS:000269418800023", "date-descending")
        self.assertEqual(raised.exception.result["code"], "identity_mismatch")

    def test_citing_target_accepts_accession_doi_and_full_record_url_only(self):
        adapter = WebOfScience(None, None)
        self.assertEqual(adapter.citing_target("WOS:000269418800023"), ("UT=(WOS:000269418800023)", None))
        self.assertEqual(adapter.citing_target("10.1145/1562164.1562186"), ('DO=("10.1145/1562164.1562186")', "10.1145/1562164.1562186"))
        self.assertEqual(adapter.citing_target("https://www.webofscience.com/wos/woscc/full-record/WOS:000269418800023"),
                         ("UT=(WOS:000269418800023)", None))
        with self.assertRaises(ServiceError):
            adapter.citing_target("The Status of the P versus NP Problem")

    def test_fetch_keeps_cited_references_and_separates_incoming_citations(self):
        with tempfile.TemporaryDirectory() as temp:
            store = ArtifactStore(temp)
            records = store.put(json.dumps([{"id": "WOS:000269418800023", "fields": {"cr": ["ONE", "TWO"]}}]),
                                "application/json", "wos", "https://www.webofscience.com/")
            parent = {"status": "ok", "source": "wos", "query": "UT=(WOS:000269418800023)",
                      "total": 1, "received": 1, "records": records}
            incoming = {"status": "ok", "kind": "citations", "total": 125, "received": 20, "records": {"ref": "incoming"}}
            adapter = WebOfScience(store, None)
            adapter.search = Mock(side_effect=[parent, incoming])
            result = adapter.fetch("WOS:000269418800023", parts=["supplementary"])
        component = result["components"]["supplementary"]
        self.assertEqual(component["artifact"], records)
        self.assertEqual(component["references"]["direction"], "outgoing")
        self.assertEqual(component["references"]["count"], 2)
        self.assertEqual(component["citations"]["direction"], "incoming")
        self.assertEqual(component["citations"]["total"], 125)
        self.assertEqual(adapter.search.call_args_list[1].kwargs["options"], {"kind": "citations"})


if __name__ == "__main__":
    unittest.main()
