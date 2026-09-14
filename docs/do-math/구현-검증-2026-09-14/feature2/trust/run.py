"""Scratch-only actual Lean trust-transition evidence runner.

Identity assessments below are deliberately synthetic pre-existing records.  The
script exercises actual Lean compilation, axiom reporting, trust invalidation,
transition checks, and activation; it does not claim an actual semantic review.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
FROZEN = Path(r"C:\math\.skill-workspace\do-math-feature2-tests-fg5ma0v3\do-math\scripts")
sys.path.insert(0, str(FROZEN))

from do_math.formal import verify_lean
from do_math.knowledge import register_environment
from do_math.lifecycle_engine import LifecycleEngineMixin
from do_math.repository import canonical_json

LEAN = r"C:\math\.skill-workspace\do-math-toolchains\lean-4.32.0\lean-4.32.0-windows\bin\lean.exe"


def save_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_json(value))


class Harness(LifecycleEngineMixin):
    def __init__(self, name: str):
        self.workspace = ROOT / name
        self.workspace.mkdir(parents=True, exist_ok=True)
        self.current_time = datetime(2026, 9, 14, tzinfo=timezone.utc)
        self.lifecycle_clock = lambda: self.current_time.isoformat()
        self.instance = {"id": name, "workspace": str(self.workspace), "goal": "trust transition fixture",
            "goal_kind": "mathematical", "goal_status": "unresolved", "policies": "fixture",
            "knowledge": {}, "relations": [], "goal_judgments": [], "sources": [],
            "config": {"research_reconsider_seconds": 3600, "lean_timeout_seconds": 30,
                       "external_timeout_seconds": 5}}
        self.runtime = {"status": "ready", "tasks": {}, "executions": {}, "activities": {},
                        "queue": [], "history": [], "questions": []}
        self.head = "scratch-0"
        self.formal_verifier = verify_lean
        self.saves = 0
        self._upgrade_runtime()

    def _enqueue(self, role, target=None, **extra):
        action = {"role": role, **extra}
        if target is not None:
            action["target"] = target
        if action not in self.runtime["queue"]:
            self.runtime["queue"].append(action)

    def _save(self, artifacts=None):
        self.saves += 1
        self.head = f"scratch-{self.saves}"
        snapshot = ROOT / "states" / f"{self.instance['id']}-{self.saves:03d}.json"
        save_json(snapshot, {"instance": self.instance, "runtime": self.runtime})
        for rel, raw in (artifacts or {}).items():
            destination = ROOT / "artifacts" / self.instance["id"] / rel.replace("/", "_")
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(raw)

    def control(self, config, tag):
        return self._apply_extended_control({"id": tag, "action": "trust", "config": config})

    def _start_identity_review(self, knowledge_id, previous_cycle_id=None):
        # Only needed if a trust transition changes the signature.  This runner
        # keeps signatures unchanged, so no semantic-review action is created.
        raise AssertionError("semantic review should not be invoked in this exact-signature trust run")

    def process_one(self, role):
        action = next(item for item in self.runtime["queue"] if item["role"] == role)
        if not self._process_machine_action(action):
            raise AssertionError(f"machine action not accepted: {action}")


def initial_record(engine: Harness, source: str, allowed_axioms: tuple[str, ...], label: str):
    raw = verify_lean(source=source, declarations=["good"], workspace=engine.workspace,
                      lean_command=[LEAN], timeout_seconds=30, allowed_axioms=allowed_axioms)
    save_json(ROOT / "raw" / f"{label}-initial-formal.json", raw)
    (ROOT / "raw" / f"{label}.lean").write_text(source, encoding="utf-8")
    if raw["status"] != "verified":
        raise AssertionError(raw)
    engine.instance, old_id = register_environment(engine.instance, raw["toolchain"], list(allowed_axioms))
    engine.instance["trust_environments"][old_id]["status"] = "active"
    engine.instance["active_trust_environment"] = old_id
    formal = {**deepcopy(raw), "trust_environment_id": old_id, "trust_environment_status": "active"}
    # Synthetic only: isolates the controller from the independent-review runner.
    engine.instance["knowledge"]["K"] = {"id": "K", "revision": 1, "status": "verified",
        "statement": "True", "summary": "Fixture theorem", "lean_code": source,
        "declaration_names": ["good"], "dependencies": [], "formal": formal,
        "use_suspended": False, "use_suspensions": [], "use_suspension_reasons": [],
        "identity_assessment": {"effective": True, "decision": "match", "synthetic": True,
                                "reason": "Pre-existing synthetic fixture; no model review was run"}}
    return raw, old_id


def transition(engine: Harness, old_id: str, toolchain: dict, allowed_axioms: list[str], tag: str):
    engine.control({"operation": "invalidate", "env_id": old_id,
                    "reason": "Actual compiler environment invalidated for scratch transition"}, tag + "-invalidate")
    engine.instance["knowledge"]["K"]["use_suspensions"].append({"kind": "semantic", "reason": "Unrelated semantic dispute remains"})
    engine.instance["knowledge"]["K"]["use_suspension_reasons"].append("Unrelated semantic dispute remains")
    engine.instance["knowledge"]["K"]["use_suspended"] = True
    engine.control({"operation": "register", "toolchain": toolchain, "allowed_axioms": allowed_axioms}, tag + "-register")
    new_id = next(env_id for env_id in engine.instance["trust_environments"] if env_id != old_id)
    engine.control({"operation": "transition", "env_id": new_id}, tag + "-transition")
    transition_id = next(reversed(engine.runtime["trust_transitions"]))
    return new_id, transition_id


def main():
    if ROOT.exists():
        ROOT.mkdir(parents=True, exist_ok=True)
    (ROOT / "raw").mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init", "-q", str(ROOT)], check=True)
    subprocess.run(["git", "-C", str(ROOT), "config", "user.email", "scratch@example.invalid"], check=True)
    subprocess.run(["git", "-C", str(ROOT), "config", "user.name", "do-math scratch"], check=True)

    success_source = "theorem good : True := True.intro\n"
    success = Harness("success")
    initial, old = initial_record(success, success_source, ("propext", "Classical.choice", "Quot.sound"), "success")
    new, success_transition = transition(success, old, initial["toolchain"], ["propext", "Classical.choice", "Quot.sound"], "success")
    success.process_one("trust_check")
    completed = success.runtime["trust_transitions"][success_transition]
    result = completed["results"]["K"]
    assert completed["status"] == "active", completed
    assert success.instance["active_trust_environment"] == new
    assert result["status"] == "verified" and result["signature_hash"] == initial["signature_hash"]
    assert success.instance["knowledge"]["K"]["use_suspended"] is True
    assert {cause["kind"] for cause in success.instance["knowledge"]["K"]["use_suspensions"]} == {"semantic"}
    save_json(ROOT / "states" / "success-final.json", {"instance": success.instance, "runtime": success.runtime})

    fail_source = "axiom trustedAxiom : True\ntheorem good : True := trustedAxiom\n"
    failure = Harness("failure")
    initial_failure, old_failure = initial_record(failure, fail_source, ("trustedAxiom",), "failure")
    new_failure, failed_transition = transition(failure, old_failure, initial_failure["toolchain"], ["propext"], "failure")
    failure.process_one("trust_check")
    failed = failure.runtime["trust_transitions"][failed_transition]
    failed_result = failed["results"]["K"]
    assert failed_result["status"] == "rejected", failed_result
    assert failed["status"] == "failed", failed
    assert failure.instance["active_trust_environment"] is None
    assert failure.instance["trust_environments"][new_failure]["status"] == "registered"
    assert failure.instance["knowledge"]["K"]["formal"]["trust_environment_id"] == old_failure
    assert any(cause["kind"] == "semantic" for cause in failure.instance["knowledge"]["K"]["use_suspensions"])
    save_json(ROOT / "states" / "failure-final.json", {"instance": failure.instance, "runtime": failure.runtime})

    report = {"scope": {"actual": ["portable Lean 4.32 compiler version/check/signature/axiom output",
                                       "trust invalidation, explicit registration, target check, activation/rejection"],
                        "synthetic": ["pre-existing identity_assessment only; no model/semantic review"]},
              "success": {"transition_id": success_transition, "old_environment": old, "new_environment": new,
                          "status": completed["status"], "target_result": {key: result.get(key) for key in ("status", "source_sha256", "signature_hash", "declaration_signatures", "axioms", "artifact_ref")},
                          "remaining_suspensions": success.instance["knowledge"]["K"]["use_suspensions"]},
              "failure": {"transition_id": failed_transition, "old_environment": old_failure, "new_environment": new_failure,
                          "status": failed["status"], "target_result": {key: failed_result.get(key) for key in ("status", "reason", "source_sha256", "signature_hash", "axioms", "artifact_ref")},
                          "active_environment": failure.instance["active_trust_environment"],
                          "remaining_suspensions": failure.instance["knowledge"]["K"]["use_suspensions"]}}
    save_json(ROOT / "report.json", report)
    (ROOT / "README.md").write_text("Actual Lean trust-transition scratch evidence. See report.json and raw/.\n"
        "Identity assessment fixture records are synthetic and do not establish semantic-review evidence.\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(ROOT), "add", "."], check=True)
    subprocess.run(["git", "-C", str(ROOT), "commit", "-qm", "scratch actual Lean trust evidence"], check=True)
    subprocess.run(["git", "-C", str(ROOT), "bundle", "create", str(ROOT / "live-trust.bundle"), "--all"], check=True)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
