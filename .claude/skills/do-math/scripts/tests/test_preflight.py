import hashlib
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math.preflight import inspect_bundle
from do_math.contracts import reading_map


class PersistedPreflightTests(unittest.TestCase):
    def setUp(self):
        import subprocess
        from do_math.repository import ResearchRepository, new_id
        from do_math.initialization import initialize_state
        self.temp=tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        root=Path(self.temp.name)
        subprocess.run(['git','init','-q',str(root)],check=True,capture_output=True)
        identifier=new_id('RI')
        self.store=ResearchRepository(root,identifier)
        self.instance,self.runtime=initialize_state(instance_id=identifier,goal='G',workspace=root/'work',config={},source_input='Original request')
        self.head=self.store.initialize(self.instance,self.runtime)

    def test_good_head_preserves_rejected_raw_not_candidate_state(self):
        from do_math.preflight import inspect_persisted_state,preserve_rejected_candidate
        self.assertTrue(inspect_persisted_state(self.store,self.head)['valid'])
        _,before_i,before_r=self.store.load(self.head)
        result=preserve_rejected_candidate(self.store,self.head,raw=b'{broken candidate',reason='schema rejection')
        self.assertEqual(self.store.read(result['raw_ref'],result['snapshot']),b'{broken candidate')
        _,after_i,after_r=self.store.load(result['snapshot'])
        self.assertEqual((after_i,after_r),(before_i,before_r))

    def test_damaged_head_is_not_rewritten_even_to_preserve_candidate(self):
        from do_math.preflight import inspect_persisted_state,preserve_rejected_candidate
        path=next(row['path'] for row in self.store.records(self.head) if row['family']=='lifecycle')
        damaged=self.store._store.publish(self.head,{path:b'{}\n'}).head
        self.assertFalse(inspect_persisted_state(self.store,damaged)['valid'])
        with self.assertRaisesRegex(ValueError,'damaged'):
            preserve_rejected_candidate(self.store,damaged,raw=b'raw',reason='candidate rejected')
        self.assertEqual(self.store._store.read_snapshot().head,damaged)

    def test_malformed_or_naive_high_water_is_rejected(self):
        from do_math.preflight import inspect_current_state
        for value in ('not-a-time','2026-09-20T00:00:00','2026-09-20T09:00:00+09:00'):
            with self.subTest(value=value):
                self.runtime['last_observed_utc']=value
                self.assertFalse(inspect_current_state(self.instance,self.runtime)['valid'])


class PreflightTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "skill"
        source = Path(__file__).resolve().parents[2]
        names = {name for assigned in reading_map(skill_root=source).values() for name in assigned}
        names.update(("README.md", "references/CLI-실행-계약.md", "계약/독립-운영.md",
                      "scripts/operator_schedule.ps1", "requirements.txt"))
        for name in names:
            destination = self.root / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source / name, destination)

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
