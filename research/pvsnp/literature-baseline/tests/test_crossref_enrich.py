import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


BASELINE_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = BASELINE_ROOT / "scripts" / "crossref_enrich.py"
SPEC = importlib.util.spec_from_file_location("crossref_enrich", MODULE_PATH)
crossref_enrich = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(crossref_enrich)


def candidate(candidate_id, dois):
    return {
        "candidate_id": candidate_id,
        "normalized": {"dois": dois},
    }


class DoiInputTests(unittest.TestCase):
    def test_doi_mapping_is_unique_sorted_and_keeps_every_candidate(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "candidates.jsonl"
            records = [
                candidate("MR20", ["10.1000/same"]),
                candidate("MR3", ["10.2000/only", "10.1000/same"]),
                candidate("MR10", []),
            ]
            path.write_text(
                "".join(json.dumps(item) + "\n" for item in records),
                encoding="utf-8",
            )

            mapping = crossref_enrich.load_doi_candidates(path)

        self.assertEqual(list(mapping), ["10.1000/same", "10.2000/only"])
        self.assertEqual(mapping["10.1000/same"], ["MR3", "MR20"])
        self.assertEqual(mapping["10.2000/only"], ["MR3"])

    def test_response_filename_is_the_full_doi_sha256(self):
        expected = hashlib.sha256(b"10.1000/example").hexdigest() + ".json"
        self.assertEqual(crossref_enrich.response_filename("10.1000/example"), expected)


class EnvelopeTests(unittest.TestCase):
    def test_valid_200_envelope_checks_body_hash_and_returned_doi(self):
        body = json.dumps(
            {"status": "ok", "message": {"DOI": "10.1000/ABC"}},
            separators=(",", ":"),
        ).encode()
        envelope = crossref_enrich.make_envelope(
            doi="10.1000/abc",
            endpoint="https://api.crossref.org/works/10.1000%2Fabc",
            status=200,
            headers={"Content-Type": "application/json"},
            body=body,
            retrieved_at="2026-09-04T12:00:00Z",
        )

        validated = crossref_enrich.validate_envelope_data(
            envelope, expected_doi="10.1000/abc"
        )
        self.assertEqual(validated["state"], "found")

        envelope["response_sha256"] = "0" * 64
        with self.assertRaises(crossref_enrich.ResponseValidationError):
            crossref_enrich.validate_envelope_data(
                envelope, expected_doi="10.1000/abc"
            )

    def test_404_is_crossref_not_found_not_global_doi_absence(self):
        body = b"Resource not found."
        envelope = crossref_enrich.make_envelope(
            doi="10.9999/not-crossref",
            endpoint="https://api.crossref.org/works/10.9999%2Fnot-crossref",
            status=404,
            headers={"Content-Type": "text/plain"},
            body=body,
            retrieved_at="2026-09-04T12:00:00Z",
        )
        validated = crossref_enrich.validate_envelope_data(
            envelope, expected_doi="10.9999/not-crossref"
        )

        self.assertEqual(validated["state"], "crossref_not_found")

    def test_redirected_alias_preserves_requested_and_returned_doi(self):
        body = json.dumps(
            {
                "status": "ok",
                "message": {"DOI": "10.1007/978-0-387-69395-8"},
            }
        ).encode()
        envelope = crossref_enrich.make_envelope(
            doi="10.1007/b97702",
            endpoint="https://api.crossref.org/works/10.1007%2Fb97702",
            resolved_endpoint=(
                "https://api.crossref.org/works/10.1007/978-0-387-69395-8"
            ),
            status=200,
            headers={"Content-Type": "application/json"},
            body=body,
            retrieved_at="2026-09-04T12:00:00Z",
        )

        validated = crossref_enrich.validate_envelope_data(
            envelope, expected_doi="10.1007/b97702"
        )

        self.assertEqual(validated["state"], "found_alias")
        self.assertEqual(
            validated["returned_doi"], "10.1007/978-0-387-69395-8"
        )

    def test_changed_doi_without_matching_redirect_is_rejected(self):
        body = json.dumps(
            {"status": "ok", "message": {"DOI": "10.1000/different"}}
        ).encode()
        envelope = crossref_enrich.make_envelope(
            doi="10.1000/requested",
            endpoint="https://api.crossref.org/works/10.1000%2Frequested",
            status=200,
            headers={"Content-Type": "application/json"},
            body=body,
            retrieved_at="2026-09-04T12:00:00Z",
        )

        with self.assertRaises(crossref_enrich.ResponseValidationError):
            crossref_enrich.validate_envelope_data(
                envelope, expected_doi="10.1000/requested"
            )

    def test_existing_corrupt_envelope_is_rejected_instead_of_skipped(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / crossref_enrich.response_filename("10.1000/abc")
            path.write_text("{}\n", encoding="utf-8")

            with self.assertRaises(crossref_enrich.ExistingResponseError):
                crossref_enrich.load_existing_envelope(path, "10.1000/abc")


class DerivedIndexTests(unittest.TestCase):
    def test_index_keeps_version_metadata_but_not_abstract_text(self):
        message = {
            "DOI": "10.1000/ABC",
            "type": "journal-article",
            "title": ["An Example"],
            "author": [{"family": "Example", "given": "Ada"}],
            "publisher": "Example Society",
            "published": {"date-parts": [[2024, 5, 1]]},
            "ISBN": ["123"],
            "ISSN": ["456"],
            "URL": "https://doi.org/10.1000/abc",
            "relation": {"is-preprint-of": [{"id": "10.1000/final"}]},
            "update-to": [{"DOI": "10.1000/correction", "type": "correction"}],
            "abstract": "<jats:p>Copyrighted abstract text.</jats:p>",
        }
        body = json.dumps({"status": "ok", "message": message}).encode()
        envelope = crossref_enrich.make_envelope(
            doi="10.1000/abc",
            endpoint="https://api.crossref.org/works/10.1000%2Fabc",
            status=200,
            headers={"Content-Type": "application/json"},
            body=body,
            retrieved_at="2026-09-04T12:00:00Z",
        )

        record = crossref_enrich.index_record(
            envelope,
            ["MR2", "MR1"],
            "intake/B002-public/crossref/example.json",
        )

        self.assertEqual(record["candidate_ids"], ["MR1", "MR2"])
        self.assertTrue(record["crossref"]["abstract_present"])
        self.assertNotIn("abstract", record["crossref"])
        self.assertEqual(record["crossref"]["relation"], message["relation"])
        self.assertEqual(record["crossref"]["update_to"], message["update-to"])


class RealCandidateTests(unittest.TestCase):
    def test_actual_b002_doi_universe_is_complete(self):
        path = BASELINE_ROOT / "catalog" / "B002-candidates.jsonl"
        if not path.exists():
            self.skipTest("B002 candidate index is absent")

        mapping = crossref_enrich.load_doi_candidates(path)

        self.assertEqual(len(mapping), 2748)
        self.assertEqual(sum(len(ids) for ids in mapping.values()), 2762)


if __name__ == "__main__":
    unittest.main()
