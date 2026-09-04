import importlib.util
import unittest
from pathlib import Path


BASELINE_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = BASELINE_ROOT / "scripts" / "crossref_title_review.py"
SPEC = importlib.util.spec_from_file_location("crossref_title_review", MODULE_PATH)
crossref_title_review = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(crossref_title_review)


class TextProjectionTests(unittest.TestCase):
    def test_jats_and_mathml_tags_do_not_become_title_words(self):
        value = (
            '<jats:title><mml:math xmlns:mml="urn:mml"><mml:mi>F</mml:mi>'
            '<mml:mo>(</mml:mo><mml:mi>R</mml:mi><mml:mo>)</mml:mo>'
            "</mml:math> theories of gravity</jats:title>"
        )

        self.assertEqual(
            crossref_title_review.plain_crossref_text(value),
            "F(R) theories of gravity",
        )


class ClassificationTests(unittest.TestCase):
    def test_exact_containment_similar_and_mismatch_are_distinct(self):
        exact = crossref_title_review.compare_titles(
            ["An Example"], [{"candidate_id": "MR1", "title": "an example"}]
        )
        contained = crossref_title_review.compare_titles(
            ["An Example: A Modern Treatment"],
            [{"candidate_id": "MR1", "title": "an example"}],
        )
        similar = crossref_title_review.compare_titles(
            ["Methods for Sparse Linear Systems"],
            [{"candidate_id": "MR1", "title": "method for sparse linear systems"}],
        )
        mismatch = crossref_title_review.compare_titles(
            ["A Biology Paper"],
            [{"candidate_id": "MR1", "title": "distributed algorithms"}],
        )

        self.assertEqual(exact["classification"], "exact_title")
        self.assertEqual(contained["classification"], "title_containment")
        self.assertEqual(similar["classification"], "similar_title")
        self.assertEqual(mismatch["classification"], "title_mismatch_review")

    def test_best_candidate_is_kept_for_a_shared_doi(self):
        result = crossref_title_review.compare_titles(
            ["Volume Two"],
            [
                {"candidate_id": "MR1", "title": "volume one"},
                {"candidate_id": "MR2", "title": "volume two"},
            ],
        )

        self.assertEqual(result["best_candidate_id"], "MR2")
        self.assertEqual(result["classification"], "exact_title")

    def test_absent_crossref_title_has_its_own_state(self):
        result = crossref_title_review.compare_titles(
            [], [{"candidate_id": "MR1", "title": "an example"}]
        )

        self.assertEqual(result["classification"], "missing_crossref_title")


class RealIndexTests(unittest.TestCase):
    def test_actual_crossref_index_has_one_review_record_per_doi(self):
        candidates = BASELINE_ROOT / "catalog" / "B002-candidates.jsonl"
        crossref = BASELINE_ROOT / "catalog" / "B002-crossref.jsonl"
        if not candidates.exists() or not crossref.exists():
            self.skipTest("B002 Crossref index is absent")

        records = crossref_title_review.build_review_records(candidates, crossref)

        self.assertEqual(len(records), 2748)
        self.assertEqual(len({record["doi"] for record in records}), 2748)
        self.assertEqual(
            sum(len(record["candidate_ids"]) for record in records), 2762
        )


if __name__ == "__main__":
    unittest.main()
