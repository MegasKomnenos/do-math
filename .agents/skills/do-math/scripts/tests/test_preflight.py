import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math.preflight import _contained, inspect_bundle, sha256


REPOSITORY = Path(__file__).resolve().parents[5]


class PreflightTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name)
        self.bundle = self.repo / "docs/do-math/통합-설계-명세-v9"
        shutil.copytree(REPOSITORY / "docs/do-math/통합-설계-명세-v9", self.bundle,
                        ignore=shutil.ignore_patterns("__pycache__"))
        for name in ("do-math/통합-설계.md", "형식과-절차.md"):
            shutil.copyfile(REPOSITORY / "docs" / name, self.repo / "docs" / name)

    def check(self, name):
        return next(row for row in inspect_bundle(self.repo)["checks"] if row["check"] == name)

    def write(self, name, value):
        (self.bundle / name).write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")

    def test_existing_report_cannot_hide_a_changed_design(self):
        path = self.repo / "docs/do-math/통합-설계.md"
        path.write_bytes(path.read_bytes() + b"\nchanged after validation\n")
        self.assertEqual(self.check("validation_input_basis")["status"], "blocked")
        self.assertIn("do-math/통합-설계.md", self.check("validation_input_basis")["changed"])

    def test_missing_report_is_incomplete(self):
        (self.bundle / "validation-report.json").unlink()
        self.assertEqual(self.check("validation_input_basis")["status"], "incomplete")

    def test_unreadable_schema_is_incomplete(self):
        (self.bundle / "schemas/activity.schema.json").unlink()
        self.assertEqual(self.check("schema_bytes")["status"], "incomplete")

    def test_schema_tampering_is_detected(self):
        path = self.bundle / "schemas/activity.schema.json"
        path.write_bytes(path.read_bytes() + b" ")
        result = self.check("schema_bytes")
        self.assertEqual(result["status"], "blocked")
        self.assertIn("schemas/activity.schema.json", result["changed"])

    def test_new_fixture_is_not_covered_by_old_report(self):
        self.write("fixtures/unverified.json", {})
        self.assertIn("do-math/통합-설계-명세-v9/fixtures/unverified.json",
                      self.check("validation_input_basis")["unreported"])

    def test_report_cannot_drop_design_from_basis(self):
        report = json.loads((self.bundle / "validation-report.json").read_bytes())
        report["input_basis"] = [row for row in report["input_basis"] if row["path"] != "do-math/통합-설계.md"]
        self.write("validation-report.json", report)
        self.assertIn("do-math/통합-설계.md", self.check("validation_input_basis")["unreported"])

    def test_report_paths_cannot_escape_docs(self):
        report = json.loads((self.bundle / "validation-report.json").read_bytes())
        report["input_basis"].append({"path": "../outside.json", "sha256": "0" * 64})
        self.write("validation-report.json", report)
        self.assertEqual(self.check("validation_input_basis")["status"], "incomplete")

    def test_source_hash_alone_cannot_hide_missing_vectors(self):
        source = self.repo / "docs/do-math/통합-설계.md"
        mapping = json.loads((self.bundle / "source-vector-map.json").read_bytes())
        missing_id = mapping["vectors"].pop()["id"]
        mapping["source_sha256"] = sha256(source.read_bytes())
        self.write("source-vector-map.json", mapping)
        result = self.check("source_vector_correspondence")
        self.assertEqual(result["status"], "blocked")
        vector_diff = next(row for row in result["differences"] if row["kind"] == "vectors")
        self.assertIn(missing_id, vector_diff["missing"])

    def test_empty_registry_is_not_verified(self):
        self.write("schema-registry.json", {"families": []})
        self.assertEqual(self.check("schema_bytes")["status"], "incomplete")

    def test_rehashed_invalid_schema_is_incomplete(self):
        registry = json.loads((self.bundle / "schema-registry.json").read_bytes())
        row = next(row for row in registry["families"] if row["family"] == "activity")
        invalid = b"{not JSON"
        (self.bundle / row["path"]).write_bytes(invalid)
        row["sha256"] = sha256(invalid)
        self.write("schema-registry.json", registry)
        self.assertEqual(self.check("schema_bytes")["status"], "incomplete")

    def test_swapped_schema_paths_are_blocked(self):
        registry = json.loads((self.bundle / "schema-registry.json").read_bytes())
        a = next(row for row in registry["families"] if row["family"] == "activity")
        b = next(row for row in registry["families"] if row["family"] == "artifact")
        a["path"], b["path"] = b["path"], a["path"]
        a["sha256"], b["sha256"] = b["sha256"], a["sha256"]
        self.write("schema-registry.json", registry)
        self.assertEqual(self.check("schema_bytes")["status"], "blocked")

    def test_duplicate_json_keys_fail(self):
        (self.bundle / "schema-registry.json").write_text('{"families": [], "families": []}', encoding="utf-8")
        self.assertEqual(self.check("schema_bytes")["status"], "incomplete")

    def test_read_only(self):
        before = {p.relative_to(self.repo): sha256(p.read_bytes()) for p in self.repo.rglob("*") if p.is_file()}
        inspect_bundle(self.repo)
        after = {p.relative_to(self.repo): sha256(p.read_bytes()) for p in self.repo.rglob("*") if p.is_file()}
        self.assertEqual(before, after)

    def test_reject_unsafe_paths(self):
        for name in ("../secret", "a/../secret", "C:/secret", "a\\b", "/secret", "a//b"):
            with self.subTest(name=name), self.assertRaises(ValueError):
                _contained(self.repo, name)


if __name__ == "__main__":
    unittest.main()
