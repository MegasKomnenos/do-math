"""Crossmark field direction and absence semantics."""
import importlib
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path
import sys

import httpx


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scholarly import ArtifactStore, ServiceError


class CrossmarkSemantics(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.api = importlib.import_module("api_adapters")
        cls.registry = importlib.import_module("registry")

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.store = ArtifactStore(self.tmp.name)

    def adapter(self, item):
        def response(request):
            return httpx.Response(200, json={"status": "ok", "message-type": "work", "message": item})
        client = httpx.Client(transport=httpx.MockTransport(response))
        self.addCleanup(client.close)
        return self.api.Crossmark(self.store, client=client)

    def test_fetch_distinguishes_incoming_updates_from_general_relations_and_assertions(self):
        item = {
            "DOI": "10.5555/original",
            "update-policy": "https://doi.org/10.5555/policy",
            "updated-by": [
                {"DOI": "10.5555/retraction", "type": "retraction", "source": "publisher", "updated": {"date-time": "2021-11-17T00:00:00Z"}},
                {"DOI": "10.5555/retraction", "type": "retraction", "source": "retraction-watch", "updated": {"date-time": "2021-11-17T00:00:00Z"}},
            ],
            "relation": {"has-review": [{"id": "10.5555/review", "id-type": "doi"}]},
            "assertion": [{"name": "received", "label": "Received", "value": "2021-01-01"}],
            "content-domain": {"domain": ["example.test"], "crossmark-restriction": True},
        }
        result = self.adapter(item).fetch(item["DOI"], parts=["metadata"])
        summary = result["crossmark"]
        self.assertEqual(summary["registration"], "registered")
        self.assertEqual(summary["record_update_state"], "has_registered_updates")
        self.assertEqual(summary["updated-by"]["direction"], "incoming_updates_to_this_work")
        self.assertEqual(summary["updated-by"]["count"], 2)
        self.assertEqual(summary["updated-by"]["items"], item["updated-by"])
        self.assertEqual(summary["update-to"]["count"], 0)
        self.assertEqual(summary["relation"]["value"], item["relation"])
        self.assertEqual(summary["assertion"], item["assertion"])

    def test_fetch_marks_notice_direction_and_update_metadata_without_policy(self):
        item = {
            "DOI": "10.5555/retraction",
            "update-to": [{"DOI": "10.5555/original", "type": "retraction", "source": "retraction-watch", "updated": {"date-time": "2021-11-17T00:00:00Z"}}],
            "content-domain": {"domain": [], "crossmark-restriction": False},
        }
        summary = self.adapter(item).fetch(item["DOI"], parts=["metadata"])["crossmark"]
        self.assertEqual(summary["registration"], "update_metadata_only")
        self.assertEqual(summary["record_update_state"], "is_update")
        self.assertEqual(summary["update-to"]["direction"], "outgoing_targets_updated_by_this_work")
        self.assertEqual(summary["update-to"]["items"][0]["DOI"], "10.5555/original")

    def test_fetch_does_not_turn_missing_fields_into_no_real_world_updates(self):
        item = {"DOI": "10.5555/unregistered", "content-domain": {"domain": [], "crossmark-restriction": False}}
        summary = self.adapter(item).fetch(item["DOI"], parts=["metadata"])["crossmark"]
        self.assertEqual(summary["registration"], "not_registered_in_record")
        self.assertEqual(summary["record_update_state"], "no_registered_updates_in_record")
        self.assertIn("does not prove", summary["absence_scope"])

    def test_malformed_present_updates_preserve_metadata_and_report_unknown(self):
        item = {"DOI": "10.5555/malformed", "updated-by": {"DOI": "10.5555/notice", "type": "retraction"},
                "assertion": {"name": "unexpected"}, "relation": ["unexpected"], "content-domain": "unexpected"}
        result = self.adapter(item).fetch(item["DOI"], parts=["metadata"])
        summary = result["crossmark"]
        self.assertEqual(result["status"], "partial")
        self.assertEqual(summary["registration"], "unknown")
        self.assertEqual(summary["record_update_state"], "unknown")
        self.assertIsNone(summary["updated-by"]["count"])
        self.assertEqual(summary["updated-by"]["unparsed_value"], item["updated-by"])
        self.assertEqual(summary["assertion"], item["assertion"])
        self.assertEqual(summary["relation"]["value"], item["relation"])
        self.assertEqual(summary["content-domain"], item["content-domain"])
        self.assertEqual({x["field"] for x in summary["schema_warnings"]},
                         {"updated-by", "assertion", "relation", "content-domain"})
        self.assertEqual(result["components"]["metadata"]["status"], "available")

    def test_unknown_update_type_is_preserved_without_relabeling_assertion(self):
        item = {"DOI": "10.5555/new", "update-to": [{"type": "future_kind", "provider_extra": 7}]}
        summary = self.adapter(item).fetch(item["DOI"], parts=["metadata"])["crossmark"]
        self.assertEqual(summary["update-to"]["items"], item["update-to"])
        self.assertEqual(summary["schema_warnings"], [])
        self.assertIn("update entries", summary["source_scope"])

    def test_source_guide_names_both_directions_and_schema_update_values(self):
        usage = self.registry.SOURCES["crossmark"].usage
        joined = " ".join(str(value) for value in usage.values())
        self.assertIn("updated-by", joined)
        self.assertIn("update-to", joined)
        self.assertIn("new_version", joined)
        self.assertIn("retraction-watch", joined)
        self.assertIn("relation", joined)

    def test_crossmark_paces_requests_for_the_public_list_rate(self):
        adapter = self.adapter({"DOI": "10.5555/pace"})
        with patch('api_adapters.time.monotonic', side_effect=[10.0, 10.0, 10.5, 11.5]), patch('api_adapters.time.sleep') as sleep:
            adapter.fetch('10.5555/pace', parts=['metadata'])
            adapter.fetch('10.5555/pace', parts=['metadata'])
        sleep.assert_called_once_with(1.0)

    def test_source_guide_explains_list_rate_headers_and_429_scope(self):
        limits = self.registry.SOURCES["crossmark"].usage["limits"]
        self.assertIn("목록", limits)
        self.assertIn("초당 1건", limits)
        self.assertIn("x-rate-limit-interval", limits)
        self.assertIn("429", limits)
        self.assertIn("자료 부재", limits)

    def test_rate_limit_preserves_standard_and_crossref_limit_headers(self):
        headers = {
            "Retry-After": "2",
            "X-Rate-Limit-Limit": "1",
            "X-Rate-Limit-Interval": "1s",
            "X-Rate-Limit-Type": "list",
            "X-Concurrency-Limit": "1",
        }
        client = httpx.Client(transport=httpx.MockTransport(lambda request: httpx.Response(429, headers=headers)))
        self.addCleanup(client.close)
        adapter = self.api.Crossmark(self.store, client=client)
        with self.assertRaises(ServiceError) as caught:
            adapter.search("", options={"filter": "is-update:true,update-type:retraction"}, limit=1)
        error = caught.exception.result
        self.assertEqual(error["http_status"], 429)
        self.assertEqual(error["retry_after"], "2")
        self.assertEqual(error["rate_limit"], "1")
        self.assertEqual(error["rate_limit_interval"], "1s")
        self.assertEqual(error["rate_limit_type"], "list")
        self.assertEqual(error["concurrency_limit"], "1")

    def test_success_evidence_preserves_crossref_limit_headers(self):
        item = {"DOI": "10.5555/original", "content-domain": {"domain": [], "crossmark-restriction": False}}
        headers = {
            "Content-Type": "application/json",
            "X-Rate-Limit-Limit": "1",
            "X-Rate-Limit-Interval": "1s",
            "X-Rate-Limit-Type": "list",
            "X-Concurrency-Limit": "1",
        }
        client = httpx.Client(transport=httpx.MockTransport(
            lambda request: httpx.Response(200, headers=headers, json={"status": "ok", "message-type": "work", "message": item})
        ))
        self.addCleanup(client.close)
        evidence = self.api.Crossmark(self.store, client=client).fetch(item["DOI"], parts=["metadata"])["evidence"]
        self.assertEqual(evidence["rate_limit"], "1")
        self.assertEqual(evidence["rate_limit_interval"], "1s")
        self.assertEqual(evidence["rate_limit_type"], "list")
        self.assertEqual(evidence["concurrency_limit"], "1")


if __name__ == "__main__":
    unittest.main()
