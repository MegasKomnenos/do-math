import importlib.util
import unittest
from pathlib import Path


BASELINE_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = BASELINE_ROOT / "scripts" / "build_unified_catalog.py"
SPEC = importlib.util.spec_from_file_location("build_unified_catalog", MODULE_PATH)
unified = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(unified)


def b001(candidate_id, doi=""):
    return {
        "candidate_id": candidate_id,
        "source_id": "mathscinet" if candidate_id.startswith("MR") else "scopus",
        "normalized": {
            "title": "example",
            "creators": ["example ada"],
            "year": 2020,
            "dois": [doi] if doi else [],
        },
    }


def b002(candidate_id, doi=""):
    return {
        "candidate_id": candidate_id,
        "normalized": {
            "title": "example",
            "creators": ["example ada"],
            "year": 2020,
            "dois": [doi] if doi else [],
        },
    }


class UnifiedCandidateTests(unittest.TestCase):
    def test_same_mr_is_one_global_candidate_with_both_catalog_refs(self):
        records = unified.build_unified_candidates(
            [b001("MR10"), b001("B001-SCOPUS-x")],
            [b002("MR10"), b002("MR20")],
        )

        self.assertEqual(len(records), 3)
        overlap = next(record for record in records if record["global_candidate_id"] == "MR10")
        self.assertEqual(overlap["primary_record"], {"catalog": "B002", "candidate_id": "MR10"})
        self.assertEqual(
            overlap["records"],
            [
                {"catalog": "B001", "candidate_id": "MR10"},
                {"catalog": "B002", "candidate_id": "MR10"},
            ],
        )

    def test_same_doi_across_non_mr_records_is_not_merged(self):
        records = unified.build_unified_candidates(
            [b001("B001-SCOPUS-x", "10.1/same")],
            [b002("MR20", "10.1/same")],
        )

        self.assertEqual(len(records), 2)
        self.assertEqual(
            {record["global_candidate_id"] for record in records},
            {"B001-SCOPUS-x", "MR20"},
        )


class UnifiedRelationTests(unittest.TestCase):
    def test_converts_b002_members_and_keeps_b001_cross_catalog_relations(self):
        b001_relations = [
            {
                "relation_id": "B001-REL-a",
                "relation_type": "same_doi_candidate",
                "status": "unverified_candidate",
                "signal": {"doi": "10.1/same"},
                "members": [
                    {"catalog": "B001", "candidate_id": "B001-SCOPUS-x"},
                    {"catalog": "B002", "candidate_id": "MR20"},
                ],
            }
        ]
        b002_relations = [
            {
                "relation_id": "B002-REL-b",
                "relation_type": "edition_or_version_candidate",
                "status": "unverified_candidate",
                "signal": {"title": "example"},
                "members": ["MR20", "MR30"],
            }
        ]

        relations = unified.build_unified_relations(b001_relations, b002_relations)

        self.assertEqual(len(relations), 2)
        converted = next(row for row in relations if row["relation_id"] == "B002-REL-b")
        self.assertEqual(
            converted["members"],
            [
                {"catalog": "B002", "candidate_id": "MR20"},
                {"catalog": "B002", "candidate_id": "MR30"},
            ],
        )


class RealCatalogTests(unittest.TestCase):
    def test_current_catalogs_have_expected_safe_union(self):
        paths = [
            BASELINE_ROOT / "catalog/B001-candidates.jsonl",
            BASELINE_ROOT / "catalog/B002-candidates.jsonl",
        ]
        if not all(path.exists() for path in paths):
            self.skipTest("candidate catalogs are absent")
        b001_rows = unified.load_jsonl(paths[0])
        b002_rows = unified.load_jsonl(paths[1])

        records = unified.build_unified_candidates(b001_rows, b002_rows)

        self.assertEqual(len(records), 25793)
        self.assertEqual(sum(len(row["records"]) == 2 for row in records), 108)


if __name__ == "__main__":
    unittest.main()
