"""Current installation handoff and shared real Git retry fixture."""
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
from do_math.engine import DEFAULT_CONFIG, ResearchEngine
from do_math.repository import ResearchRepository, canonical_json
from do_math import repair_execution

AT = "2026-09-20T00:00:00Z"


class RepositoryHost:
    """Only the ENGINE save facade; all persistence/validation uses the real store."""
    def _save(self, artifacts=None):
        self.head = self.store.save_with_state(self.head, self.instance, self.runtime, artifacts=artifacts)[0]
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
            "created_at": AT, "status": "pending", "disposition": {
                "kind": "retry", "basis_refs": ["EX-target"], "next_owner": "engine",
                "reason": "Use a fresh workspace for the unfinished activity",
                "scope": "Same unfinished activity", "replay_safety": "No external effects"}}
        host.runtime["operational_dispositions"][self.record["id"]] = deepcopy(self.record)
        host.runtime["executions"]["EX-review"]["action"]["target"] = "EX-target"
        host.head = host.store.initialize(host.instance, host.runtime)
        host._save({self.source: self.raw,
                    "runtime/artifacts/BA-target/manifest.json": canonical_json(target["input_manifest"])})

    def test_installation_repair_handoff_preserves_failure_and_is_idempotent(self):
        host = self.host
        target = host.runtime["executions"]["EX-target"]
        target.update(error="Installed receiver rejected valid output", result_ref=self.source)
        record = host.runtime["operational_dispositions"]["OD-repair"]
        record.update(status="repair_required", disposition={"kind": "repair",
            "basis_refs": ["EX-target"], "next_owner": "installation_recovery",
            "reason": "Repair the installed receiver", "repair_target": "installation:scripts/do_math/engine.py",
            "meaning_preserving": True, "verification": "Run the receiver regression"})
        host._save()
        with patch.object(repair_execution, "installation_fingerprint", return_value="a" * 64):
            result = ResearchEngine._complete_operational_disposition(host,
                host.runtime["operational_dispositions"]["OD-repair"])
        self.assertEqual(result["status"], "installation_repair_pending")
        self.assertEqual(host.runtime["queue"], [])
        self.assertEqual(self.destination.read_bytes(), b"damaged")
        head = host.head
        self.assertEqual(ResearchEngine._complete_operational_disposition(host, result), result)
        self.assertEqual(host.head, head)


if __name__ == "__main__":
    unittest.main()
