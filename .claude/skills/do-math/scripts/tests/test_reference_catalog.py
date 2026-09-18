"""Reference hints are projections of visibility, never additional authority."""
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math.submission import reference_catalog, reported_references, validate_reference


class CatalogTests(unittest.TestCase):
    def test_current_aliases_and_historical_bytes_remain_distinct(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "input/knowledge/K.json"
            path.parent.mkdir(parents=True)
            path.write_text('{}')
            context = {"action": {"role": "research_plan"},
                "knowledge_catalog": [{"id": "K", "path": "input/knowledge/K.json"}],
                "tasks": [{"id": "T"}], "sources": [{"id": "S", "name": "paper",
                    "path": "research/source/paper", "local_path": "input/sources/paper"}],
                "previous_execution": {"id": "E", "result_source": {"artifact_ref": "runtime/artifacts/old/result.json"}}}
            rows = reference_catalog(context, root)
            for row in rows:
                validate_reference(row["value"], context, root)
            values = {row["value"]: row for row in rows}
            self.assertEqual(values["input/knowledge/K.json"]["canonical_ref"], "K")
            self.assertEqual(values["runtime/artifacts/old/result.json"]["kind"], "historical_artifact")
            refs = reported_references({"used_sources": ["workspace:input/knowledge/K.json", "source:paper",
                "S", "runtime/artifacts/old/result.json"]}, {}, context)
            self.assertEqual(refs, ["K", "paper", "runtime/artifacts/old/result.json"])
            context["reference_catalog"] = [{"value": "unprovided", "path": "unprovided"}]
            with self.assertRaises(ValueError):
                validate_reference("unprovided", context, root)

    def test_fixed_question_catalog_only_exposes_its_source_set(self):
        with tempfile.TemporaryDirectory() as directory:
            context = {"action": {"role": "supplemental_research", "review_cycle_id": "R"},
                "knowledge_catalog": [{"id": "allowed"}, {"id": "other"}],
                "review_research": {"sources": [{"ref": "allowed"}]}}
            self.assertEqual([r["value"] for r in reference_catalog(context, Path(directory))], ["allowed"])


if __name__ == "__main__":
    unittest.main()
