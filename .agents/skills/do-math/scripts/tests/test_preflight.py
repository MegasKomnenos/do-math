import hashlib
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math.preflight import inspect_bundle


class PreflightTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "skill"
        shutil.copytree(Path(__file__).resolve().parents[2], self.root,
                        ignore=shutil.ignore_patterns("__pycache__"))

    def test_current_installation_has_all_roles_and_schemas(self):
        report = inspect_bundle(self.root)
        self.assertEqual(report["status"], "verified")
        self.assertEqual([row["roles"] for row in report["checks"]], [10, 10])
        self.assertIn("document_semantics", report["not_verified"])

    def test_missing_required_document_is_incomplete(self):
        (self.root / "GLOSSARY.md").unlink()
        self.assertEqual(inspect_bundle(self.root)["status"], "incomplete")

    def test_reading_map_cannot_escape_skill(self):
        path = self.root / "SKILL.md"
        path.write_text(path.read_text(encoding="utf-8").replace(
            "`GLOSSARY.md`", "`../outside.md`"), encoding="utf-8")
        self.assertEqual(inspect_bundle(self.root)["status"], "incomplete")

    def test_missing_operating_contract_is_incomplete(self):
        (self.root / "references/CLI-실행-계약.md").unlink()
        self.assertEqual(inspect_bundle(self.root)["status"], "incomplete")

    def test_missing_independent_operator_contract_is_incomplete(self):
        (self.root / "계약/독립-운영.md").unlink()
        self.assertEqual(inspect_bundle(self.root)["status"], "incomplete")

    def test_missing_scheduler_entrypoint_is_incomplete(self):
        (self.root / "scripts/operator_schedule.ps1").unlink()
        self.assertEqual(inspect_bundle(self.root)["status"], "incomplete")

    def test_read_only_and_observed_document_hashes(self):
        def hashes():
            return {p.relative_to(self.root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                    for p in self.root.rglob("*") if p.is_file()}
        before = hashes()
        report = inspect_bundle(self.root)
        self.assertEqual(before, hashes())
        for name, digest in report["checks"][0]["documents"].items():
            self.assertEqual(digest, before[name])


if __name__ == "__main__":
    unittest.main()
