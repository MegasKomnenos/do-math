"""Integration checks for postsolution academic requirements.

These tests use the temporary Git repository and scripted runner from the
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
from research_fixtures import charter_change, policy_change, send_control, assessment
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
                    "evidence_refs": [row['id'] for row in context['knowledge_catalog'] if row.get('usable_as_k')],
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
        kwargs.setdefault('plan_settle_seconds', 1)  # This suite tests academic obligations, not review batching latency.
        engine, _ = super().make(*args, **kwargs)
        runner = AcademicRunner(**getattr(self, "runner_options", {}))
        engine.runner = runner
        self.runners[-1] = runner
        return engine, runner

    def _set_requirements(self, engine, criteria, decision_id, **extra):
        send_control(engine, "decision", config={"change": charter_change(engine, academic_requirements=[requirement(criteria, **extra)])})

    def _academic_tasks(self, engine):
        return [task for task in engine.runtime["tasks"].values() if task.get("academic_requirement_id") == "writeup"]

    def _requirement_change_fixture(self, *, completed=False):
        from state_fixtures import active_engine, complete_academic_task
        engine = active_engine(self.repo, self.root / "academic-change")
        self.engines.append(engine)
        # Mathematical proof construction is covered by the end-to-end test.
        # Only that premise is synthetic; controls, followup and storage are real.
        basis = {"goal_ref": "synthetic-solution", "records": []}
        self.enterContext(patch.object(engine, "_solution_basis", return_value=basis))
        engine.instance["goal_status"] = "mathematically_solved"
        engine._save()
        requirements = [requirement(["draft account"])]
        if completed:
            # The whole instance must remain open for public requirement changes.
            requirements.append({**requirement(["Independent remaining account"]), "id": "remaining"})
        send_control(engine, "decision", config={"change": charter_change(engine,
            academic_requirements=requirements)})
        engine._ensure_academic_followup()
        engine._save()
        if completed:
            complete_academic_task(engine, self._academic_tasks(engine)[0], basis)
            self.assertEqual(engine.runtime["status"], "ready")
            self.assertTrue(self._academic_tasks(engine)[0]["assessment"]["current"])
        engine.head, engine.instance, engine.runtime = engine.store.load()
        return engine

    def _publish_followup(self, engine):
        engine._ensure_academic_followup()
        engine._save()
        engine.head, engine.instance, engine.runtime = engine.store.load()

    def test_explicit_requirement_blocks_runtime_completion_until_independent_assessment(self):
        engine, runner = self.make()
        self._set_requirements(engine, ["draft account", "cite reviewed equality"], "academic-v1")

        self.drive(engine, predicate=lambda current: current.instance["goal_status"] == "mathematically_solved")
        tasks = self._academic_tasks(engine)
        self.assertEqual(len(tasks), 1)
        task = tasks[0]
        self.assertEqual([row["claim"] for row in task["completion_obligations"]], ["draft account", "cite reviewed equality"])
        self.assertNotEqual(engine.runtime["status"], "completed")
        self.assertNotEqual(task["status"], "completed")

        self.drive(engine, predicate=lambda current: current.runtime["status"] == "completed", limit=30)
        task = self._academic_tasks(engine)[0]
        self.assertEqual(task["status"], "completed")
        self.assertTrue(any(review["decision"] == "approved" for review in task["reviews"]))
        self.assertNotEqual(task["assessment"]["execution_id"], task["results"][0]["execution_id"])
        self.assertEqual([item["obligation_id"] for item in task["assessment"]["item_dispositions"]], [row["id"] for row in task["completion_obligations"]])
        recorded = [entry for entry in engine.runtime["academic_assessments"] if entry["task_id"] == task["id"]]
        self.assertEqual(len(recorded), 1)
        self.assertEqual(recorded[0]["decision"], "satisfied")
        self.assertEqual(engine.status()["academic_validation"]["status"], "completed")
        self.assertIn(task["title"], runner.work_order)

    def test_changed_same_requirement_id_supersedes_old_contract_and_creates_new_criteria(self):
        engine = self._requirement_change_fixture()
        old = self._academic_tasks(engine)[0]
        old_basis = deepcopy(old["solution_basis"])
        old_hash = old["requirements_sha256"]

        self._set_requirements(engine, ["draft account", "archival supplement"], "academic-v2")
        self._publish_followup(engine)
        tasks = self._academic_tasks(engine)
        self.assertEqual(len(tasks), 2)
        superseded = next(task for task in tasks if task["id"] == old["id"])
        current = next(task for task in tasks if task["id"] != old["id"])
        self.assertEqual(superseded["status"], "closed")
        self.assertEqual(superseded["scope_disposition"]["kind"], "superseded_requirements")
        self.assertEqual(current["academic_requirement_id"], "writeup")
        self.assertEqual([row["claim"] for row in current["completion_obligations"]], ["draft account", "archival supplement"])
        self.assertEqual(current["solution_basis"], old_basis)
        self.assertNotEqual(current["requirements_sha256"], old_hash)
        self.assertNotEqual(engine.runtime["status"], "completed")

    def test_changed_requirements_preserve_completed_academic_task(self):
        engine = self._requirement_change_fixture(completed=True)
        old = self._academic_tasks(engine)[0]
        self.assertEqual(old["status"], "completed")

        self._set_requirements(engine, ["draft account", "archival supplement"], "academic-v2")
        self._publish_followup(engine)
        tasks = self._academic_tasks(engine)
        preserved = next(task for task in tasks if task["id"] == old["id"])
        current = next(task for task in tasks if task["id"] != old["id"])
        self.assertEqual(preserved["status"], "completed")
        self.assertNotIn("scope_disposition", preserved)
        self.assertFalse(preserved["assessment"]["current"])
        self.assertTrue(preserved["assessment"]["invalidated_reason"].strip())
        self.assertEqual([row["claim"] for row in current["completion_obligations"]], ["draft account", "archival supplement"])
        self.assertNotEqual(engine.runtime["status"], "completed")

    def test_removing_all_requirements_retires_old_tasks_and_completes_followup(self):
        engine = self._requirement_change_fixture(completed=True)
        before = deepcopy(engine.runtime["tasks"])
        self.assertTrue(any(task["status"] == "completed" for task in before.values()))
        self.assertTrue(any(task["status"] != "completed" for task in before.values()))
        send_control(engine, "decision", config={"change": charter_change(
            engine, academic_requirements=[])})
        self._publish_followup(engine)
        self.assertEqual(set(engine.runtime["tasks"]), set(before))
        for tid, previous in before.items():
            current = engine.runtime["tasks"][tid]
            self.assertEqual(current["results"], previous["results"])
            if previous["status"] == "completed":
                self.assertEqual(current["status"], "completed")
                self.assertFalse(current["assessment"]["current"])
            else:
                self.assertEqual(current["status"], "closed")
                self.assertEqual(current["scope_disposition"]["kind"], "superseded_requirements")
        self.assertEqual(engine.instance["goal_status"], "mathematically_solved")
        self.assertEqual(engine._academic_status()["status"], "not_applicable")
        self.assertEqual(engine.runtime["status"], "completed")
        self.assertEqual(engine.runtime["queue"], [])

    def test_removing_all_requirements_preserves_unresolved_external_rejection(self):
        engine = self._requirement_change_fixture()
        send_control(engine, "decision", config={"change": {
            "kind": "academic_rejection", "actor": "referee",
            "text": "The preserved solution still needs a response."}})
        rejection = deepcopy(engine.runtime["external_rejections"][-1])
        send_control(engine, "decision", config={"change": charter_change(
            engine, academic_requirements=[])})
        self._publish_followup(engine)
        self.assertEqual(engine._academic_status()["status"], "externally_rejected")
        self.assertNotEqual(engine.runtime["status"], "completed")
        self.assertEqual(engine.runtime["external_rejections"][-1], rejection)
        self.assertTrue(all(task["status"] == "closed"
                            for task in engine.runtime["tasks"].values()))
        self.assertFalse(any(action.get("target") in engine.runtime["tasks"]
                             for action in engine.runtime["queue"]))

    def test_completed_instance_rejects_requirement_changes(self):
        engine = self._requirement_change_fixture()
        from state_fixtures import complete_academic_task
        complete_academic_task(engine, self._academic_tasks(engine)[0], engine._solution_basis())
        self.assertEqual(engine.runtime["status"], "completed")
        before = deepcopy(engine.runtime["tasks"])
        request = control(self.repo, engine.instance["id"], "decision", config={
            "change": charter_change(engine, academic_requirements=[requirement(["New requirement"])])})
        engine.process_controls()
        rejected = [row for row in engine.runtime["history"]
                    if row.get("kind") == "rejected_user_control"
                    and row.get("request", {}).get("id") == request["request_id"]]
        self.assertEqual(len(rejected), 1)
        self.assertIn("closed/completed", rejected[0]["reason"])
        self.assertEqual(engine.runtime["status"], "completed")
        self.assertEqual(engine.store.load()[2]["tasks"], before)

    def test_external_rejection_keeps_formal_solution_and_requires_planner_evidence_to_clear(self):
        engine, _ = self.make()
        self.drive(engine)
        knowledge = next(iter(engine.instance["knowledge"].values()))
        formal_before = deepcopy(engine.instance["formal_results"][knowledge["formal_result_id"]])
        self.assertEqual(engine.runtime["status"], "completed")

        control(self.repo, engine.instance["id"], "decision", config={"change": {
            "kind": "academic_rejection", "actor": "external referee",
            "text": "The reader-facing explanation needs a specific response.",
        }})
        engine.process_controls()
        rejection = engine.runtime["external_rejections"][-1]
        rejection_before = deepcopy(rejection)
        self.assertFalse(rejection["resolved"])
        self.assertEqual(engine.instance["goal_status"], "mathematically_solved")
        self.assertEqual(engine.instance["formal_results"][knowledge["formal_result_id"]], formal_before)
        self.assertNotEqual(engine.runtime["status"], "completed")

        self.drive(engine, predicate=lambda current: current.runtime["status"] == "completed", limit=12)
        rejection = next(item for item in engine.runtime["external_rejections"] if item["id"] == rejection["id"])
        self.assertEqual(rejection, rejection_before)
        resolution = next(row for row in engine.runtime['academic_resolution_records']
                          if row['rejection_id'] == rejection['id'])
        self.assertEqual(resolution['decision'], 'resolved')
        self.assertTrue(resolution['evidence'].strip())
        from do_math import academic
        self.assertEqual(academic.unresolved_rejections(engine.instance, engine.runtime, engine._solution_basis(),
                                                       resolve_evidence=engine._academic_evidence), [])
        resolution_execution = engine.runtime["executions"][resolution['execution_id']]
        self.assertEqual(resolution_execution["action"]["role"], "research_plan")
        self.assertEqual(engine.instance["goal_status"], "mathematically_solved")
        self.assertEqual(engine.instance["formal_results"][knowledge["formal_result_id"]], formal_before)

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
        engine, _ = self.make(external_policy="explicit_grants")
        send_control(engine, "decision", text="Explicit test-only permission for this loopback endpoint",
            config={"change": {"kind": "grant", "grant": {"id": "HTTP", "kind": "http",
                "allowed_origins": [origin], "allowed_methods": ["POST"], "allowed_path_prefixes": ["/"],
                "reuse": "reusable"}}})
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

        for suffix in ('/reject', '/unknown'):
            self.runner_options = {"effect_request": {"grant_id": "HTTP", "request": {"method": "POST", "url": origin + suffix, "body": "proof"}}}
            engine, _ = self.make(external_policy="explicit_grants")
            send_control(engine, "decision", text="Explicit test-only permission for this loopback endpoint",
                config={"change": {"kind": "grant", "grant": {"id": "HTTP", "kind": "http",
                    "allowed_origins": [origin], "allowed_methods": ["POST"], "allowed_path_prefixes": ["/"],
                    "reuse": "reusable"}}})
            self._set_requirements(engine, ["send manuscript"], "academic-effect" + suffix.replace("/", "-"),
                external_effects=[{"id": "submit", "scope": "send manuscript", "grant_id": "HTTP"}])
            # The successful loopback test covers the full mathematical path.
            # Here only that premise is synthetic; preparation, external Job,
            # actual HTTP outcome, receipt gate and typed storage remain real.
            basis = {'goal_ref': 'synthetic-solution', 'records': []}
            self.enterContext(patch.object(engine, '_solution_basis', return_value=basis))
            engine.instance['goal_status'] = 'mathematically_solved'
            engine.runtime['queue'] = []
            engine._ensure_academic_followup()
            engine._save()
            operation = None
            for _ in range(30):
                engine.run(max_steps=1)
                operation = next(iter(engine.runtime["external_operations"].values()), None)
                if operation and operation.get("status") in {"confirmed", "unknown"}:
                    break
            self.assertIsNotNone(operation)
            self.assertEqual((operation["status"], operation.get("succeeded")), ('unknown', None))
            task = self._academic_tasks(engine)[0]
            # The loop stops before any planner assessment exists, so the status checks below hold even without the
            # receipt gate. Submit the planner's completed assessment to that gate against the actual ledger state.
            completed = assessment(task)
            from do_math.task_scope import apply_task_assessments
            original_instance, original_runtime = engine.instance, engine.runtime
            try:
                engine.instance, engine.runtime = deepcopy(original_instance), deepcopy(original_runtime)
                engine.runtime['executions']['EX-planner-fixture'] = {'id': 'EX-planner-fixture',
                    'role': 'research_plan', 'status': 'ended', 'input_solution_basis': deepcopy(task['solution_basis'])}
                engine.instance, engine.runtime = apply_task_assessments(engine.instance, engine.runtime, [completed],
                    execution_id='EX-planner-fixture', input_tasks=deepcopy(engine.runtime['tasks']))
                with self.assertRaisesRegex(ValueError, "lacks confirmed successful required external effects"):
                    engine._record_academic_assessment(engine.runtime['tasks'][task['id']], completed, 'EX-planner-fixture')
            finally:
                engine.instance, engine.runtime = original_instance, original_runtime
            self.assertFalse([entry for entry in engine.runtime.get("academic_assessments", []) if entry.get("task_id") == task["id"]])
            self.assertNotEqual(engine.status()["academic_validation"]["status"], "completed")
            self.assertNotEqual(engine.runtime["status"], "completed")
        self.assertEqual(received, ["/reject", "/unknown"])


class AcademicTaskPersistenceTests(unittest.TestCase):
    def setUp(self):
        from test_input_recovery import InputRecoveryPublicTests
        InputRecoveryPublicTests.setUp(self)

    def test_user_requirement_task_keeps_charter_provenance_without_invented_execution(self):
        from do_math.engine import ResearchEngine
        from do_math.governance import governance_view
        engine = ResearchEngine(self.repo, self.identifier)
        send_control(engine, "decision", config={"change": charter_change(engine,
            academic_requirements=[{**requirement(["Explain the supplied result"]), "id": "원고 검토"}])})
        # Only the mathematical solution basis is synthetic; generation, approval,
        # record/reference validation and Git publication are real.
        basis = {"goal_ref": "synthetic-solution", "records": []}
        with patch.object(engine, "_solution_basis", return_value=basis):
            engine.instance["goal_status"] = "mathematically_solved"
            engine._ensure_academic_followup()
            engine._save()
        task = next(t for t in engine.runtime["tasks"].values() if t.get("academic_requirement_id"))
        charter = governance_view(engine.instance)["charter"]
        self.assertNotIn("producer_execution", task)
        self.assertEqual(task["basis_refs"], [charter["id"], charter["approval_ref"]])
        self.assertEqual(task["academic_requirement_id"], "원고 검토")
        self.assertEqual(task["requirements_sha256"], governance_view(engine.instance)["academic_requirements"]["sha256"])
        preparation = next(a for a in engine.runtime['queue'] if task['id'] in a.get('observation_rule_targets', {}))
        self.assertEqual(preparation['role'], 'research_preparation')
        self.assertFalse(any(a['role'] == 'task_contract_review' and a.get('target') == task['id']
                             for a in engine.runtime['queue']))
        _, _, saved = engine.store.load()
        self.assertEqual(saved["tasks"][task["id"]], task)


if __name__ == "__main__":
    unittest.main(verbosity=2)
