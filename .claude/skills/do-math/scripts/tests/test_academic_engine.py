"""Integration checks for postsolution academic requirements.

These tests use the in-memory CAS repository and scripted runner from the
purpose-engine suite.  They verify engine orchestration, not a model judgment
or a Lean invocation.
"""
from __future__ import annotations

from copy import deepcopy
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
import sys
import threading
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from do_math.engine import control
from do_math import external as external_module
from do_math.repository import canonical_json
from test_purpose_engine import PurposeHarness, PurposeRunner


def requirement(criteria: list[str], *, required_inputs=None, external_effects=None) -> dict:
    return {
        "id": "writeup",
        "scope": "A reader-facing account of the solved natural-number theorem.",
        "criteria": criteria,
        "assessor": "research_plan",
        "required_inputs": required_inputs or [],
        "external_effects": external_effects or [],
    }


class AcademicRunner(PurposeRunner):
    """Purpose fixture that supplies an explicit planner resolution when asked."""

    def __init__(self, *args, effect_request=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.effect_request = effect_request

    def answer(self, role, context, workspace):
        action = context["action"]
        if role == "research_plan" and action.get("rejection_id"):
            (workspace / "activity-extensions.json").write_bytes(canonical_json({
                "academic_resolutions": [{
                    "id": action["rejection_id"], "decision": "resolved",
                    "evidence": "The planner compared the preserved objection with the completed reviewed task report.",
                }],
            }))
        if role == "research_work" and context["task"].get("academic_requirement_id"):
            task = context["task"]
            effects = task.get("required_external_effects", [])
            if effects and self.effect_request:
                (workspace / "activity-extensions.json").write_bytes(canonical_json({"external_requests": [{
                    "id": "academic-effect", "academic_effect_id": effects[0]["id"],
                    "grant_id": effects[0].get("grant_id") or self.effect_request["grant_id"],
                    "purpose": effects[0]["scope"], "request": deepcopy(self.effect_request["request"]),
                }]}))
            self.work_order.append(task["title"])
            return {
                "summary": "The academic criterion is addressed by the submitted reader-facing account.",
                "used_sources": task.get("reuse", []), "questions": [], "outcome": "submitted",
                "report": "The report explains the exact natural-number domain and the reviewed equality.",
                "knowledge": [], "relations": [], "remaining_work": [],
                "checkpoint": "The required account and its evidence are ready for independent assessment.",
            }
        return super().answer(role, context, workspace)


class AcademicEngineTests(PurposeHarness):
    def make(self, *args, **kwargs):
        engine, _ = super().make(*args, **kwargs)
        runner = AcademicRunner(**getattr(self, "runner_options", {}))
        engine.runner = runner
        self.runners[-1] = runner
        return engine, runner

    def _set_requirements(self, engine, criteria, decision_id, **extra):
        control(self.repo, engine.instance["id"], "decision", config={"change": {
            "kind": "academic_requirements", "decision_id": decision_id,
            "requirements": [requirement(criteria, **extra)],
        }})
        engine.process_controls()

    def _academic_tasks(self, engine):
        return [task for task in engine.runtime["tasks"].values() if task.get("academic_requirement_id") == "writeup"]

    def test_explicit_requirement_blocks_runtime_completion_until_independent_assessment(self):
        engine, runner = self.make()
        self._set_requirements(engine, ["draft account", "cite reviewed equality"], "academic-v1")

        self.drive(engine, predicate=lambda current: current.instance["goal_status"] == "mathematically_solved")
        tasks = self._academic_tasks(engine)
        self.assertEqual(len(tasks), 1)
        task = tasks[0]
        self.assertEqual(task["completion_criteria"], ["draft account", "cite reviewed equality"])
        self.assertNotEqual(engine.runtime["status"], "completed")
        self.assertNotEqual(task["status"], "completed")

        self.drive(engine, predicate=lambda current: current.runtime["status"] == "completed", limit=30)
        task = self._academic_tasks(engine)[0]
        self.assertEqual(task["status"], "completed")
        self.assertTrue(any(review["decision"] == "approved" for review in task["reviews"]))
        self.assertNotEqual(task["assessment"]["execution_id"], task["results"][0]["execution_id"])
        self.assertEqual([item["criterion"] for item in task["assessment"]["criteria_results"]], task["completion_criteria"])
        recorded = [entry for entry in engine.runtime["academic_assessments"] if entry["task_id"] == task["id"]]
        self.assertEqual(len(recorded), 1)
        self.assertEqual(recorded[0]["decision"], "satisfied")
        self.assertEqual(engine.status()["academic_validation"]["status"], "completed")
        self.assertIn(task["title"], runner.work_order)

    def test_changed_same_requirement_id_supersedes_old_contract_and_creates_new_criteria(self):
        engine, _ = self.make()
        self._set_requirements(engine, ["draft account"], "academic-v1")
        self.drive(engine, predicate=lambda current: current.instance["goal_status"] == "mathematically_solved")
        old = self._academic_tasks(engine)[0]
        old_basis = deepcopy(old["solution_basis"])
        old_hash = old["requirements_sha256"]

        self._set_requirements(engine, ["draft account", "archival supplement"], "academic-v2")
        engine.run(max_steps=1)
        tasks = self._academic_tasks(engine)
        self.assertEqual(len(tasks), 2)
        superseded = next(task for task in tasks if task["id"] == old["id"])
        current = next(task for task in tasks if task["id"] != old["id"])
        self.assertEqual(superseded["status"], "closed")
        self.assertEqual(superseded["scope_disposition"]["kind"], "superseded_requirements")
        self.assertEqual(current["academic_requirement_id"], "writeup")
        self.assertEqual(current["completion_criteria"], ["draft account", "archival supplement"])
        self.assertEqual(current["solution_basis"], old_basis)
        self.assertNotEqual(current["requirements_sha256"], old_hash)
        self.assertNotEqual(engine.runtime["status"], "completed")

    def test_external_rejection_keeps_formal_solution_and_requires_planner_evidence_to_clear(self):
        engine, _ = self.make()
        self.drive(engine)
        knowledge = next(iter(engine.instance["knowledge"].values()))
        formal_before = deepcopy(knowledge["formal"])
        self.assertEqual(engine.runtime["status"], "completed")

        control(self.repo, engine.instance["id"], "decision", config={"change": {
            "kind": "academic_rejection", "actor": "external referee",
            "text": "The reader-facing explanation needs a specific response.",
        }})
        engine.process_controls()
        rejection = engine.runtime["external_rejections"][-1]
        self.assertFalse(rejection["resolved"])
        self.assertEqual(engine.instance["goal_status"], "mathematically_solved")
        self.assertEqual(engine.instance["knowledge"][knowledge["id"]]["formal"], formal_before)
        self.assertNotEqual(engine.runtime["status"], "completed")

        self.drive(engine, predicate=lambda current: current.runtime["status"] == "completed", limit=12)
        rejection = next(item for item in engine.runtime["external_rejections"] if item["id"] == rejection["id"])
        self.assertTrue(rejection["resolved"])
        self.assertTrue(rejection["resolution_evidence"].strip())
        resolution_execution = engine.runtime["executions"][rejection["resolution_execution_id"]]
        self.assertEqual(resolution_execution["action"]["role"], "research_plan")
        self.assertEqual(engine.instance["goal_status"], "mathematically_solved")
        self.assertEqual(engine.instance["knowledge"][knowledge["id"]]["formal"], formal_before)

    def test_required_external_effect_uses_confirmed_loopback_receipt_before_completion(self):
        received = []
        handler_errors = []
        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):
                try:
                    length = int(self.headers.get("Content-Length", "0"))
                    body = self.rfile.read(length)
                    received.append({"path": self.path, "body": body, "bytes": length})
                    response = b"accepted"
                    self.send_response(200)
                    self.send_header("Content-Type", "text/plain")
                    self.send_header("Content-Length", str(len(response)))
                    self.end_headers()
                    self.wfile.write(response)
                    self.wfile.flush()
                except Exception as error:
                    handler_errors.append(f"{type(error).__name__}: {error}")
                    raise
            def log_message(self, *_):
                pass
        server = HTTPServer(("127.0.0.1", 0), Handler)
        worker = threading.Thread(target=server.serve_forever, daemon=True)
        worker.start(); self.addCleanup(server.server_close); self.addCleanup(server.shutdown)
        origin = f"http://127.0.0.1:{server.server_port}"
        self.runner_options = {"effect_request": {"grant_id": "HTTP", "request": {"method": "POST", "url": origin + "/submit", "body": "proof"}}}
        engine, _ = self.make()
        engine.instance["grants"]["HTTP"] = {"id": "HTTP", "kind": "http", "status": "active", "allowed_origins": [origin],
            "allowed_methods": ["POST"], "allowed_path_prefixes": ["/"]}
        engine._save()
        self._set_requirements(engine, ["send manuscript"], "academic-effect-v1", required_inputs=["context:goal"],
            external_effects=[{"id": "submit", "scope": "send manuscript", "grant_id": "HTTP"}])
        transport_errors = []
        original_http = external_module._http
        def observed_http(*args):
            try:
                return original_http(*args)
            except BaseException as error:
                transport_errors.append({"type": type(error).__name__, "errno": getattr(error, "errno", None), "text": str(error)})
                raise
        with patch.object(external_module, "_http", observed_http):
            self.drive(engine, predicate=lambda current: current.runtime["status"] == "completed", limit=35)
        task = self._academic_tasks(engine)[0]
        self.assertEqual(task["inputs"][-1], "context:goal")
        self.assertEqual(task["required_external_effects"][0]["id"], "submit")
        operation = next(item for item in engine.runtime["external_operations"].values() if item.get("academic_binding", {}).get("task_id") == task["id"])
        self.assertEqual((operation["status"], operation["succeeded"], operation["grant_id"]), ("confirmed", True, "HTTP"))
        self.assertEqual(operation["academic_binding"]["effect_id"], "submit")
        self.assertEqual(handler_errors, [])
        self.assertEqual(transport_errors, [])
        self.assertEqual(received, [{"path": "/submit", "body": b"proof", "bytes": 5}])

    def test_non2xx_or_unknown_external_effect_cannot_complete_academic_requirement(self):
        received = []
        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):
                self.rfile.read(int(self.headers.get("Content-Length", "0")))
                received.append(self.path)
                if self.path == "/reject":
                    body = b"rejected"
                    self.send_response(409)
                    self.send_header("Content-Length", str(len(body)))
                    self.end_headers(); self.wfile.write(body)
                else:
                    self.close_connection = True
            def log_message(self, *_):
                pass
        server = HTTPServer(("127.0.0.1", 0), Handler)
        worker = threading.Thread(target=server.serve_forever, daemon=True)
        worker.start(); self.addCleanup(server.server_close); self.addCleanup(server.shutdown)
        origin = f"http://127.0.0.1:{server.server_port}"

        for suffix, expected in (("/reject", ("confirmed", False)), ("/unknown", ("unknown", None))):
            self.runner_options = {"effect_request": {"grant_id": "HTTP", "request": {"method": "POST", "url": origin + suffix, "body": "proof"}}}
            engine, _ = self.make()
            engine.instance["grants"]["HTTP"] = {"id": "HTTP", "kind": "http", "status": "active", "allowed_origins": [origin],
                "allowed_methods": ["POST"], "allowed_path_prefixes": ["/"]}
            engine._save()
            self._set_requirements(engine, ["send manuscript"], "academic-effect" + suffix.replace("/", "-"),
                external_effects=[{"id": "submit", "scope": "send manuscript", "grant_id": "HTTP"}])
            operation = None
            for _ in range(30):
                engine.run(max_steps=1)
                operation = next(iter(engine.runtime["external_operations"].values()), None)
                if operation and operation.get("status") in {"confirmed", "unknown"}:
                    break
            self.assertIsNotNone(operation)
            self.assertEqual((operation["status"], operation.get("succeeded")), expected)
            self.assertNotEqual(engine.status()["academic_validation"]["status"], "completed")
            self.assertNotEqual(engine.runtime["status"], "completed")
        self.assertEqual(received, ["/reject", "/unknown"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
