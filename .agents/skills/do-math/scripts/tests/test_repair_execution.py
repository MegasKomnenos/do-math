"""Real Git/file-effect tests for the central deterministic repair consumer."""
from copy import deepcopy
import hashlib
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math import activities, execution_lifecycle, execution_profiles
from do_math.engine import DEFAULT_CONFIG
from do_math.repository import ResearchRepository, canonical_json
from do_math import repair_execution

AT = "2026-09-20T00:00:00Z"


class RepositoryHost:
    """Only the ENGINE save facade; all persistence/validation uses the real store."""
    def _save(self, artifacts=None):
        self.head = self.store.save(self.head, self.instance, self.runtime, artifacts=artifacts)
        self.head, self.instance, self.runtime = self.store.load(self.head)


class RepairExecutionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        repo = root / "repo"
        repo.mkdir()
        subprocess.run(["git", "-C", str(repo), "init", "-q"], check=True)
        self.host = host = RepositoryHost()
        host.store = ResearchRepository(repo, "RI-01ARZ3NDEKTSV4RRFFQ69G5FAV")
        configured = execution_profiles.build_profiles(DEFAULT_CONFIG)
        profiles = configured["execution_profiles"]
        host.instance = {"feature_version": 5, "workspace": str(root / "private"),
            "capacity_constraints": configured["capacity_constraints"],
            "execution_profiles": {key: p for key, p in profiles.items()
                                   if p["role"] in {"research_work", "operational_review"}}}
        host.runtime = {"feature_version": 5, "executions": {}, "queue": [], "operational_dispositions": {}}
        for eid, role, aid in [("EX-target", "research_work", "AY-target"),
                                ("EX-review", "operational_review", "AY-review")]:
            profile = next(p for p in host.instance["execution_profiles"].values() if p["role"] == role)
            activities.open_activity(host.runtime, activity_id=aid, activity_kind=role,
                owner_ref="engine", input_refs=[], opened_at=AT)
            execution = execution_lifecycle.create_execution(execution_id=eid, owner_activity_id=aid,
                actor_kind="ai", input_manifest={}, profile_ref=execution_profiles.profile_ref(profile), created_at=AT)
            execution.update(role=role, action={"id": "AC-" + eid, "role": role, "owner_activity_id": aid})
            activities.assign_execution(host.runtime, aid, execution)
            execution_lifecycle.transition_execution(execution, "ended", at=AT, outcome="cancelled")
        self.raw = b"sealed mathematical input\n"
        self.digest = hashlib.sha256(self.raw).hexdigest()
        self.relative = "input/catalog/tasks.json"
        target = host.runtime["executions"]["EX-target"]
        target["input_bundle"] = "BA-target"
        target["input_manifest"] = {"catalog": [{"path": self.relative, "sha256": self.digest, "bytes": len(self.raw)}],
                                    "execution_profile_ref": target["execution_profile_ref"]}
        self.source = "runtime/artifacts/BA-target/" + self.relative
        self.destination = root / "private/runs/EX-target/workspace" / self.relative
        self.destination.parent.mkdir(parents=True)
        self.destination.write_bytes(b"damaged")
        self.record = {"id": "OD-repair", "execution_id": "EX-review", "target_execution_id": "EX-target",
            "created_at": AT, "status": "repair_required", "disposition": {
                "kind": "repair", "basis_refs": ["EX-target"], "next_owner": "engine",
                "reason": "Restore the sealed input", "repair_target": self.relative,
                "meaning_preserving": True, "verification": "sha256:" + self.digest}}
        host.runtime["operational_dispositions"][self.record["id"]] = deepcopy(self.record)
        host.runtime["executions"]["EX-review"]["action"]["target"] = "EX-target"
        host.head = host.store.initialize(host.instance, host.runtime)
        host._save({self.source: self.raw,
                    "runtime/artifacts/BA-target/manifest.json": canonical_json(target["input_manifest"])})

    def run_repair(self):
        return repair_execution.complete_repair(self.host, self.host.runtime["operational_dispositions"]["OD-repair"])

    def test_actual_restore_verify_and_explicit_activity_followup(self):
        result = self.run_repair()
        self.assertEqual(result["status"], "applied")
        self.assertEqual(self.destination.read_bytes(), self.raw)
        proof = result["result"]["repair"]
        self.assertTrue(proof["repair_verification"]["passed"])
        self.assertEqual(proof["repair_effect"]["effect_refs"], proof["repair_verification"]["effect_refs"])
        action = self.host.runtime["queue"][0]
        self.assertEqual(action["continuation_of"], "EX-target")
        self.assertEqual(action["owner_activity_id"], "AY-target")
        self.assertEqual(len(self.host.runtime["executions"]), 2)  # no fictitious provider run
        self.assertEqual(self.host.store.load()[2]["operational_dispositions"]["OD-repair"], result)

    def reload(self):
        self.host.head, self.host.instance, self.host.runtime = self.host.store.load()

    def test_actual_corruption_after_effect_fails_verification_without_followup(self):
        replace = repair_execution._replace_input
        def corrupt(*args):
            replace(*args)
            self.destination.write_bytes(b"corrupted after restoration")
        with patch.object(repair_execution, "_replace_input", side_effect=corrupt):
            result = self.run_repair()
        self.assertEqual(result["status"], "repair_verification_failed")
        self.assertFalse(result["result"]["repair"]["repair_verification"]["passed"])
        self.assertEqual(self.host.runtime["queue"], [])
        self.assertEqual(result["result"]["followup"]["next_owner"], "operational_review")

    def test_interruption_after_file_effect_reconciles_without_replacing_twice(self):
        replace = repair_execution._replace_input
        def interrupt(*args):
            replace(*args)
            raise RuntimeError("simulated loss after actual os.replace")
        with patch.object(repair_execution, "_replace_input", side_effect=interrupt):
            with self.assertRaisesRegex(RuntimeError, "simulated loss"):
                self.run_repair()
        self.reload()
        self.assertEqual(self.host.runtime["operational_dispositions"]["OD-repair"]["status"], "repair_running")
        with patch.object(repair_execution, "_replace_input", side_effect=AssertionError("duplicate effect")):
            result = self.run_repair()
        self.assertEqual(result["status"], "applied")
        head = self.host.head
        self.assertEqual(self.run_repair(), result)
        self.assertEqual(head, self.host.head)
        self.assertEqual(len(self.host.runtime["queue"]), 1)

    def test_interruption_after_verification_retains_proof_and_only_opens_followup(self):
        save = self.host._save
        def interrupt(artifacts=None):
            save(artifacts)
            if self.host.runtime["operational_dispositions"]["OD-repair"]["status"] == "repair_resume_required":
                raise RuntimeError("simulated loss after verification CAS")
        with patch.object(self.host, "_save", side_effect=interrupt):
            with self.assertRaisesRegex(RuntimeError, "simulated loss"):
                self.run_repair()
        self.reload()
        with patch.object(repair_execution, "_replace_input", side_effect=AssertionError("duplicate effect")):
            result = self.run_repair()
        self.assertEqual(result["status"], "applied")
        self.assertEqual(len(self.host.runtime["queue"]), 1)

    def test_interrupted_resume_queue_and_receipt_are_one_git_cas(self):
        save = self.host._save
        def interrupt(artifacts=None):
            if self.host.runtime["operational_dispositions"]["OD-repair"]["status"] == "applied":
                raise RuntimeError("simulated loss before final CAS")
            save(artifacts)
        with patch.object(self.host, "_save", side_effect=interrupt):
            with self.assertRaisesRegex(RuntimeError, "simulated loss"):
                self.run_repair()
        self.reload()
        self.assertEqual(self.host.runtime["queue"], [])
        self.assertEqual(self.host.runtime["operational_dispositions"]["OD-repair"]["status"], "repair_resuming")
        self.assertEqual(self.run_repair()["status"], "applied")
        self.assertEqual(len(self.host.runtime["queue"]), 1)

    def test_prose_is_returned_to_owner_and_never_executed(self):
        record = self.host.runtime["operational_dispositions"]["OD-repair"]
        record["disposition"]["verification"] = "Write-Output hacked; remove everything"
        self.host._save()
        result = self.run_repair()
        self.assertEqual(result["status"], "repair_deferred")
        self.assertIn("prose is not executed", result["result"]["followup"]["reason"])
        self.assertEqual(self.destination.read_bytes(), b"damaged")
        self.assertEqual(self.host.runtime["queue"], [])

    def test_source_hash_is_checked_before_file_mutation(self):
        target = self.host.runtime["executions"]["EX-target"]
        target["input_bundle"] = "BA-bad-source"
        self.host._save({"runtime/artifacts/BA-bad-source/" + self.relative: b"incorrect source",
            "runtime/artifacts/BA-bad-source/manifest.json": canonical_json(target["input_manifest"])})
        result = self.run_repair()
        self.assertEqual(result["status"], "repair_deferred")
        self.assertIn("manifest hash/length", result["result"]["followup"]["reason"])
        self.assertEqual(self.destination.read_bytes(), b"damaged")

    def test_missing_sealed_source_returns_reason_and_next_owner(self):
        target = self.host.runtime["executions"]["EX-target"]
        target["input_bundle"] = "BA-missing-source"
        self.host._save({"runtime/artifacts/BA-missing-source/manifest.json": canonical_json(target["input_manifest"])})
        result = self.run_repair()
        self.assertEqual(result["status"], "repair_deferred")
        self.assertEqual(result["result"]["followup"]["next_owner"], "operational_review")
        self.assertIn("failed", result["result"]["followup"]["reason"])
        self.assertEqual(self.destination.read_bytes(), b"damaged")

    def test_different_post_intent_target_is_not_overwritten_on_recovery(self):
        with patch.object(repair_execution, "_replace_input", side_effect=RuntimeError("lost before effect")):
            with self.assertRaises(RuntimeError):
                self.run_repair()
        self.reload()
        self.destination.write_bytes(b"new information not in original intent")
        result = self.run_repair()
        self.assertEqual(result["status"], "repair_deferred")
        self.assertIn("changed after intent", result["result"]["followup"]["reason"])
        self.assertEqual(self.destination.read_bytes(), b"new information not in original intent")
        self.assertEqual(self.host.runtime["queue"], [])

    def test_profile_binding_is_checked_against_sealed_manifest(self):
        self.host.runtime["executions"]["EX-target"]["input_manifest"]["execution_profile_ref"] = {}
        result = self.run_repair()
        self.assertEqual(result["status"], "repair_deferred")
        self.assertEqual(self.destination.read_bytes(), b"damaged")


if __name__ == "__main__":
    if "--evidence" in sys.argv:
        import json
        position = sys.argv.index("--evidence")
        evidence = Path(sys.argv[position + 1])
        del sys.argv[position:position + 2]
        program = unittest.main(exit=False)
        evidence.write_text(json.dumps({"tests_run": program.result.testsRun,
            "passed": program.result.wasSuccessful(), "failures": [str(x) for x in program.result.failures],
            "errors": [str(x) for x in program.result.errors],
            "test_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "source_sha256": hashlib.sha256(Path(repair_execution.__file__).read_bytes()).hexdigest(),
            "actual": "Real isolated Git CAS/schema repository, sealed artifacts and filesystem replacements",
            "doubles": "ENGINE facade (real store), injected crash/corruption boundaries; no live provider"}, indent=2), encoding="utf-8")
        sys.exit(0 if program.result.wasSuccessful() else 1)
    unittest.main()
