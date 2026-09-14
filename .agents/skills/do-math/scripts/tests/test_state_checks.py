"""State checker tests against states produced by the real local harnesses."""
from __future__ import annotations

from copy import deepcopy
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
import sys
import threading
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from do_math.engine import control
from do_math.state_checks import state_errors
from test_academic_engine import AcademicRunner
from test_lifecycle_engine import FakeEngine
from test_purpose_engine import PurposeHarness


def academic_requirement(criteria):
    return {"id": "writeup", "scope": "A reader-facing account of the solved theorem.",
            "criteria": criteria, "assessor": "research_plan"}


class PurposeStateHarness(PurposeHarness):
    def make(self, *args, **kwargs):
        engine, _ = super().make(*args, **kwargs)
        runner = AcademicRunner()
        engine.runner = runner
        self.runners[-1] = runner
        return engine, runner

    def complete_academic_state(self):
        engine, _ = self.make()
        control(self.repo, engine.instance["id"], "decision", config={"change": {
            "kind": "academic_requirements", "decision_id": "academic-v1",
            "requirements": [academic_requirement(["draft account"])],
        }})
        engine.process_controls()
        self.drive(engine, predicate=lambda current: current.runtime["status"] == "completed", limit=40)
        return engine


class StateCheckTests(PurposeStateHarness):
    def assertError(self, instance, runtime, text):
        errors = state_errors(instance, runtime)
        self.assertTrue(any(text in error for error in errors), errors)

    def test_real_purpose_harness_solved_academic_state_is_clean(self):
        engine = self.complete_academic_state()
        self.assertEqual(engine.instance["goal_status"], "mathematically_solved")
        self.assertEqual(engine.runtime["status"], "completed")
        self.assertEqual(state_errors(engine.instance, engine.runtime), [])

    def test_mutated_real_purpose_state_detects_k_task_goal_source_and_supplement_errors(self):
        engine = self.complete_academic_state()
        instance, runtime = deepcopy(engine.instance), deepcopy(engine.runtime)
        knowledge_id = next(iter(instance["knowledge"]))
        instance["knowledge"][knowledge_id]["formal"]["source_sha256"] = "0" * 64
        self.assertError(instance, runtime, "formal source is stale")

        instance, runtime = deepcopy(engine.instance), deepcopy(engine.runtime)
        task = next(task for task in runtime["tasks"].values() if task.get("academic_requirement_id"))
        task["assessment"]["current"] = False
        runtime["executions"]["EX-live-work"] = {"id": "EX-live-work", "role": "research_work", "status": "running",
                                                     "action": {"target": task["id"]}}
        self.assertError(instance, runtime, "assessment is not current")
        self.assertError(instance, runtime, "has a live worker")

        instance, runtime = deepcopy(engine.instance), deepcopy(engine.runtime)
        instance["goal_judgments"][0]["current"] = False
        self.assertError(instance, runtime, "complete current agreeing audits")

        instance, runtime = deepcopy(engine.instance), deepcopy(engine.runtime)
        instance["sources"].append({"name": "broken", "path": "runtime/broken", "sha256": "not-a-hash", "bytes": -1})
        self.assertError(instance, runtime, "invalid sha256")
        self.assertError(instance, runtime, "invalid byte count")

        instance, runtime = deepcopy(engine.instance), deepcopy(engine.runtime)
        knowledge_id = next(iter(instance["knowledge"]))
        runtime["review_cycles"]["RC-pending"] = {"id": "RC-pending", "knowledge_id": knowledge_id, "status": "working",
            "research": {"request": {"status": "pending", "action": {"slot": "initial-0"}}}}
        runtime["queue"].append({"role": "supplemental_research", "target": knowledge_id, "review_cycle_id": "RC-pending",
                                 "research_request_id": "request", "requesting_slot": "wrong"})
        self.assertError(instance, runtime, "queued investigation is not linked")

    def test_real_lifecycle_prepare_run_and_reconcile_states_are_clean(self):
        engine = FakeEngine(self.root)
        received = []

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                received.append(self.path)
                self.send_response(200); self.end_headers(); self.wfile.write(b"local receipt")
            def do_POST(self):
                received.append(self.path)
                self.close_connection = True
            def log_message(self, *args):
                pass

        server = HTTPServer(("127.0.0.1", 0), Handler)
        worker = threading.Thread(target=server.serve_forever, daemon=True)
        worker.start()
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        origin = f"http://127.0.0.1:{server.server_port}"
        engine.instance["grants"]["HTTP"] = {"id": "HTTP", "kind": "http", "status": "active",
            "allowed_origins": [origin], "allowed_methods": ["GET", "POST"], "allowed_path_prefixes": ["/"]}

        engine.control("external", {"operation": "prepare", "grant_id": "HTTP", "id": "OP-ready",
                                     "request": {"method": "GET", "url": origin + "/read"}})
        # Preparation has a reserved EX ID but intentionally no execution row.
        self.assertEqual(state_errors(engine.instance, engine.runtime), [])
        engine.machine("external_action")
        self.assertEqual(engine.runtime["external_operations"]["OP-ready"]["status"], "confirmed")
        self.assertEqual(state_errors(engine.instance, engine.runtime), [])

        engine.control("external", {"operation": "prepare", "grant_id": "HTTP", "id": "OP-unknown",
                                     "request": {"method": "POST", "url": origin + "/uncertain", "body": "x"}})
        engine.machine("external_action")
        self.assertEqual(engine.runtime["external_operations"]["OP-unknown"]["status"], "unknown")
        self.assertEqual(state_errors(engine.instance, engine.runtime), [])
        engine.control("external", {"operation": "reconcile", "id": "OP-unknown", "result": "confirmed",
                                     "evidence": "Operator matched the preserved local receipt"})
        self.assertEqual(state_errors(engine.instance, engine.runtime), [])
        self.assertEqual(received, ["/read", "/uncertain"])

    def test_external_mapping_mutation_and_version_policy(self):
        engine = FakeEngine(self.root)
        engine.instance["feature_version"] = engine.runtime["feature_version"] = 2
        engine.instance["grants"]["HTTP"] = {"id": "HTTP", "kind": "http", "status": "active",
            "allowed_origins": ["http://127.0.0.1:1"], "allowed_methods": ["GET"], "allowed_path_prefixes": ["/"]}
        engine.control("external", {"operation": "prepare", "grant_id": "HTTP", "id": "OP",
                                     "request": {"method": "GET", "url": "http://127.0.0.1:1/"}})
        operation = engine.runtime["external_operations"]["OP"]
        # A false execution row for an unstarted ledger is not the valid prepared state.
        engine.runtime["executions"][operation["execution_id"]] = {"id": operation["execution_id"], "role": "external_action",
            "operation_id": "different", "status": "running", "outcome": "prepared"}
        self.assertError(engine.instance, engine.runtime, "missing EX execution mapping")

        engine = self.complete_academic_state()
        instance, runtime = deepcopy(engine.instance), deepcopy(engine.runtime)
        instance["feature_version"] = runtime["feature_version"] = 99
        self.assertError(instance, runtime, "unsupported feature version")

    def test_cli1_legacy_state_remains_readable(self):
        engine = self.complete_academic_state()
        instance, runtime = deepcopy(engine.instance), deepcopy(engine.runtime)
        instance["feature_version"] = runtime["feature_version"] = 1
        for record in instance["knowledge"].values():
            record.pop("use_suspensions", None)
            record.pop("review_cycle_id", None)
            record.pop("identity_assessment", None)
            record.get("formal", {}).pop("trust_environment_id", None)
            record.get("formal", {}).pop("trust_environment_status", None)
        # CLI-1 has no feature-2 currentness metadata. Its persisted structure
        # is still readable rather than being rejected as an unknown contract.
        self.assertEqual(state_errors(instance, runtime), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
