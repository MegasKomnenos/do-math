import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock


BASELINE_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = BASELINE_ROOT / "scripts" / "zbmath_match.py"
SPEC = importlib.util.spec_from_file_location("zbmath_match", MODULE_PATH)
zbmath_match = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(zbmath_match)


def candidate(candidate_id, title, year, dois=(), creators=("Example Ada",)):
    return {
        "candidate_id": candidate_id,
        "normalized": {
            "title": title.lower(),
            "year": year,
            "dois": list(dois),
            "creators": [value.lower() for value in creators],
            "creator_role": "author",
        },
        "fields": [{"name": "title", "value": title}],
        "provenance": [
            {"field_code": "68", "rank": 3, "path": "intake/example.bib"}
        ],
    }


class CandidateInputTests(unittest.TestCase):
    def test_loads_only_doi_less_candidates_in_numeric_mr_order(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "candidates.jsonl"
            rows = [
                candidate("MR20", "Twenty", 2000),
                candidate("MR3", "Three", 1990),
                candidate("MR10", "Ten", 1980, dois=("10.1/ten",)),
            ]
            path.write_text(
                "".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8"
            )

            loaded = zbmath_match.load_doi_less_candidates(path)

        self.assertEqual([row["candidate_id"] for row in loaded], ["MR3", "MR20"])
        self.assertEqual(loaded[0]["query"]["t"], "Three")
        self.assertEqual(loaded[0]["query"]["a"], ["example ada"])
        self.assertEqual(loaded[0]["query"]["y"], "1990")
        self.assertEqual(loaded[0]["query"]["n"], 3)
        self.assertEqual(loaded[0]["query"]["m"], 0)

    def test_batches_are_deterministic_and_never_exceed_one_hundred(self):
        rows = [
            {"candidate_id": f"MR{i}", "query": {"t": str(i)}}
            for i in range(1, 206)
        ]

        batches = list(zbmath_match.make_batches(rows, batch_size=100))

        self.assertEqual([len(batch) for batch in batches], [100, 100, 5])
        self.assertEqual(batches[0][0]["candidate_id"], "MR1")
        self.assertEqual(batches[-1][-1]["candidate_id"], "MR205")


class EnvelopeTests(unittest.TestCase):
    def _valid_envelope(self):
        body = json.dumps(
            {
                "results": [
                    [
                        {
                            "score": 12.5,
                            "probability": 0.9,
                            "zbl_id": "1234.56789",
                            "title": "An Example",
                            "authors": ["Ada Example"],
                            "source": "Example Journal",
                            "pagination": "1-10",
                            "year": "2020",
                        }
                    ],
                    [],
                ]
            },
            ensure_ascii=False,
            separators=(",", ":"),
        ).encode()
        return zbmath_match.make_envelope(
            batch_number=1,
            candidate_ids=["MR1", "MR2"],
            queries=[{"t": "An Example"}, {"t": "No Result"}],
            endpoint="https://zbmath.org/citationmatching/match",
            status=200,
            headers={"Content-Type": "application/json"},
            body=body,
            retrieved_at="2026-09-04T14:00:00Z",
        )

    def test_validates_body_hash_and_query_result_alignment(self):
        envelope = self._valid_envelope()
        parsed = zbmath_match.validate_envelope_data(
            envelope,
            expected_batch_number=1,
            expected_candidate_ids=["MR1", "MR2"],
            expected_queries=[{"t": "An Example"}, {"t": "No Result"}],
        )
        self.assertEqual(len(parsed["results"]), 2)

        envelope["response_sha256"] = "0" * 64
        with self.assertRaises(zbmath_match.ResponseValidationError):
            zbmath_match.validate_envelope_data(
                envelope,
                expected_batch_number=1,
                expected_candidate_ids=["MR1", "MR2"],
                expected_queries=[{"t": "An Example"}, {"t": "No Result"}],
            )

    def test_rejects_partial_batch_response(self):
        envelope = self._valid_envelope()
        envelope["response_text"] = json.dumps({"results": [[]]})
        envelope["response_sha256"] = hashlib.sha256(
            envelope["response_text"].encode("utf-8")
        ).hexdigest()

        with self.assertRaises(zbmath_match.ResponseValidationError):
            zbmath_match.validate_envelope_data(
                envelope,
                expected_batch_number=1,
                expected_candidate_ids=["MR1", "MR2"],
                expected_queries=[{"t": "An Example"}, {"t": "No Result"}],
            )

    def test_existing_corrupt_envelope_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "batch-0001.json"
            path.write_text("{}\n", encoding="utf-8")

            with self.assertRaises(zbmath_match.ExistingResponseError):
                zbmath_match.load_existing_envelope(
                    path,
                    batch_number=1,
                    candidate_ids=["MR1"],
                    queries=[{"t": "Example"}],
                )

    def test_collection_retries_invalid_http_200_batch_as_a_whole(self):
        invalid = (200, {"content-type": "application/json"}, b'{"results":[null]}')
        valid = (200, {"content-type": "application/json"}, b'{"results":[[]]}')
        batches = [[{"candidate_id": "MR1", "query": {"t": "Example"}}]]
        with tempfile.TemporaryDirectory() as tmp:
            response_root = Path(tmp)
            with mock.patch.object(
                zbmath_match, "_request_batch", side_effect=[invalid, valid]
            ) as request_batch, mock.patch.object(zbmath_match.time, "sleep"):
                existing, collected, remaining = zbmath_match.collect_responses(
                    batches,
                    response_root,
                    delay_seconds=0,
                    max_retries=1,
                )

            self.assertEqual((existing, collected, remaining), (0, 1, 0))
            self.assertEqual(request_batch.call_count, 2)
            self.assertTrue((response_root / "batch-0001.json").exists())


class TriageTests(unittest.TestCase):
    def test_prefers_exact_title_and_same_year_over_higher_scored_reissue(self):
        row = candidate("MR1", "Shape theory", 1989)
        results = [
            {
                "score": 14.0,
                "zbl_id": "1400.00001",
                "title": "Shape theory",
                "authors": ["Ada Example"],
                "year": "2008",
            },
            {
                "score": 13.0,
                "zbl_id": "0663.18001",
                "title": "Shape theory",
                "authors": ["Ada Example"],
                "year": "1989",
            },
        ]

        triage = zbmath_match.triage_results(row, results)

        self.assertEqual(triage["classification"], "exact_title_same_year")
        self.assertEqual(triage["best_result_index"], 1)

    def test_distinguishes_no_results_from_fuzzy_candidates(self):
        row = candidate("MR1", "A Specific Book", 2001)
        self.assertEqual(
            zbmath_match.triage_results(row, [])["classification"], "no_results"
        )
        fuzzy = zbmath_match.triage_results(
            row,
            [{"score": 0, "zbl_id": "0000.00000", "title": "Another Book", "year": "2001"}],
        )
        self.assertEqual(fuzzy["classification"], "fuzzy_candidates_only")


class RealCandidateTests(unittest.TestCase):
    def test_actual_b002_doi_less_universe_is_complete(self):
        path = BASELINE_ROOT / "catalog" / "B002-candidates.jsonl"
        if not path.exists():
            self.skipTest("B002 candidate index is absent")

        rows = zbmath_match.load_doi_less_candidates(path)

        self.assertEqual(len(rows), 2710)
        self.assertEqual(len({row["candidate_id"] for row in rows}), 2710)

    def test_normalization_manifest_output_list_binds_candidate_hash(self):
        with tempfile.TemporaryDirectory() as tmp:
            candidate_path = Path(tmp) / "candidates.jsonl"
            candidate_path.write_text("{}\n", encoding="utf-8")
            manifest = {
                "outputs": [
                    {
                        "path": "catalog/B002-candidates.jsonl",
                        "sha256": hashlib.sha256(candidate_path.read_bytes()).hexdigest(),
                    },
                    {"path": "catalog/B002-relations.jsonl", "sha256": "0" * 64},
                ]
            }

            zbmath_match.validate_source_manifest(manifest, candidate_path)

            manifest["outputs"][0]["sha256"] = "f" * 64
            with self.assertRaises(zbmath_match.ZbmathMatchError):
                zbmath_match.validate_source_manifest(manifest, candidate_path)


if __name__ == "__main__":
    unittest.main()
