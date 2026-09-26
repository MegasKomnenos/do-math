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
from research_fixtures import bare_engine, current_state

AT = "2026-09-20T00:00:00Z"


class RepairExecutionTests(unittest.TestCase):
    def test_operational_retry_of_an_ended_attempt_keeps_its_registered_successor(self):
        host=self.host
        parent=host.runtime['executions']['EX-target']
        child=execution_lifecycle.create_execution(execution_id='EX-next',owner_activity_id=parent['owner_activity_id'],
            actor_kind='ai',input_manifest={},profile_ref=parent['execution_profile_ref'],created_at=AT)
        child.update(role=parent['role'],continuation_of=parent['id'],
                     action={**parent['action'],'continuation_of':parent['id']})
        activities.assign_execution(host.runtime,parent['owner_activity_id'],child)
        host._save()
        record=host.runtime['operational_dispositions']['OD-repair']
        result=ResearchEngine._complete_operational_disposition(host,record)
        self.assertEqual(result['status'],'superseded')
        self.assertEqual(host.runtime['queue'],[])
        host._save()
        _,_,stored=host.store.load()
        self.assertEqual(stored['operational_dispositions']['OD-repair']['status'],'superseded')
        self.assertEqual(stored['executions']['EX-next']['continuation_of'],'EX-target')

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        repo = root / "repo"
        repo.mkdir()
        subprocess.run(["git", "-C", str(repo), "init", "-q"], check=True)
        self.host = host = bare_engine(store=ResearchRepository(repo, "RI-01ARZ3NDEKTSV4RRFFQ69G5FAV"))
        configured = execution_profiles.build_profiles(DEFAULT_CONFIG)
        profiles = configured["execution_profiles"]
        host.instance, host.runtime = current_state({"workspace": str(root / "private"),
            "capacity_constraints": configured["capacity_constraints"],
            "execution_profiles": {key: p for key, p in profiles.items()
                                   if p["role"] in {"research_work", "operational_review"}}},
            {"tasks": {}, "executions": {}, "queue": [], "operational_dispositions": {}})
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
        with patch.object(repair_execution, "installation_sha256", return_value="a" * 64):
            result = ResearchEngine._complete_operational_disposition(host,
                host.runtime["operational_dispositions"]["OD-repair"])
        self.assertEqual(result["status"], "installation_repair_pending")
        self.assertEqual(host.runtime["queue"], [])
        self.assertEqual(self.destination.read_bytes(), b"damaged")
        head = host.head
        self.assertEqual(ResearchEngine._complete_operational_disposition(host, result), result)
        self.assertEqual(host.head, head)


class InstallationIdentityTests(unittest.TestCase):
    def test_identity_covers_the_installed_skill_but_not_its_tests(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in ('scripts/do_math/a.py', 'scripts/tests/test_a.py', 'examples/case.json'):
                (root / name).parent.mkdir(parents=True, exist_ok=True)
                (root / name).write_text('one', encoding='utf-8')
            before = repair_execution.installation_sha256(root)
            # A regression test alone does not reopen the same failure's automatic repair.
            (root / 'scripts/tests/test_a.py').write_text('two', encoding='utf-8')
            self.assertEqual(repair_execution.installation_sha256(root), before)
            (root / 'examples/case.json').write_text('two', encoding='utf-8')
            self.assertNotEqual(repair_execution.installation_sha256(root), before)


if __name__ == "__main__":
    unittest.main()
