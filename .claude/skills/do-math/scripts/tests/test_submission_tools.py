"""Exercise the actual producer command in its supplied, standalone workspace."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import purpose_fixtures as purpose
from do_math.repository import canonical_json
from do_math import contracts, submission, knowledge_io
from research_fixtures import await_control, await_stop, git_init, local_job_runner, seal_response
from purpose_fixtures import CheckedRunner
from purpose_fixtures import purpose_copy
from state_fixtures import ACTIVE_LEAN_COMMAND


class LocalControlProtocolTests(unittest.TestCase):
    def test_a_corrected_draft_at_the_same_path_gets_a_new_submission_attempt(self):
        original = self.draft.read_bytes()
        self.draft.write_bytes(b'{invalid json')
        first = submission.request_control(self.workspace, '.scratch/draft.json', kind='submit_intent', wait_seconds=0)
        self.transport.pump(self.publish_intent)
        self.assertEqual(self.transport.worker_receipt(self.binding, first['request_id'])['state'], 'rejected')
        self.draft.write_bytes(original)
        second = submission.request_control(self.workspace, '.scratch/draft.json', kind='submit_intent', wait_seconds=0)
        self.assertNotEqual(first['request_id'], second['request_id'])
        self.transport.pump(self.publish_intent)
        self.assertEqual(self.transport.worker_receipt(self.binding, second['request_id'])['state'], 'accepted')

    def test_sealed_submission_preserves_the_snapshot_read_log(self):
        log = self.workspace / 'checks/reads.jsonl'
        log.parent.mkdir(exist_ok=True)
        log.write_bytes(b'{"request": "DC-1", "status": "ok"}\n')
        sealed = submission.seal_submission(self.workspace, '.scratch/draft.json', execution_id='EX-worker',
            context=self.context, schema=self.schema, max_artifact_bytes=1024 * 1024)
        self.assertEqual(sealed['artifacts']['reads.jsonl'], log.read_bytes())

    def test_supplied_tool_generates_fresh_sibling_ids_without_publishing(self):
        identifiers = []
        before = sorted(str(path.relative_to(self.workspace)) for path in self.workspace.rglob('*'))
        for _ in range(2):
            result = subprocess.run([sys.executable, '-B', 'input/tools/check_submission.py',
                '--new-knowledge-id'], cwd=self.workspace, text=True, capture_output=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stderr)
            identifier = json.loads(result.stdout)['replacement_id']
            self.assertRegex(identifier, r'^KN-[0-7][0-9A-HJKMNP-TV-Z]{25}$')
            identifiers.append(identifier)
        self.assertNotEqual(*identifiers)
        self.assertIsNone(self.head)
        self.assertEqual(before, sorted(str(path.relative_to(self.workspace)) for path in self.workspace.rglob('*')))

    def setUp(self):
        from do_math.control_transport import ControlTransport
        from do_math.git_store import GitStateStore
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.workspace = self.root / "worker"
        self.workspace.mkdir()
        self.repo = self.root / "repo"
        self.repo.mkdir()
        git_init(self.repo)
        self.store = GitStateStore(self.repo, "RI-01ARZ3NDEKTSV4RRFFQ69G5FAV")
        self.head = None
        self.transport = ControlTransport(self.root / "delivery")
        self.binding = self.transport.issue("EX-worker", "GR-worker", workspace=self.workspace)
        self.context = {"action": {"role": "maintenance", "id": "AC-worker"}, "execution_id": "EX-worker",
            "control_binding": self.binding, "snapshot": "fixed", "tasks": [], "knowledge_catalog": [],
            "sources": [], "kind_definitions": {}}
        self.schema = contracts.schema_for("maintenance")
        submission.install_tools(self.workspace, self.context, self.schema, None)
        self.output = {"summary": "Inspect only", "used_sources": [], "questions": [], "report": "Inspected", "remaining_work": []}
        seal_response(self.output, self.context, self.workspace)
        self.draft = self.workspace / ".scratch/draft.json"
        self.draft.parent.mkdir()
        self.draft.write_bytes(canonical_json(self.output))

    def mcp(self, name, arguments):
        from do_math.control_transport import ControlTransport
        server = ControlTransport.mcp_server_config(self.binding)
        request = {"jsonrpc": "2.0", "id": 1, "method": "tools/call",
                   "params": {"name": name, "arguments": arguments}}
        process = subprocess.run([server["command"], *server["args"]],
            input=json.dumps(request) + "\n", text=True, capture_output=True, timeout=30)
        self.assertEqual(0, process.returncode, process.stderr)
        envelope = json.loads(process.stdout)
        self.assertNotIn("error", envelope)
        return json.loads(envelope["result"]["content"][0]["text"])

    def publish_intent(self, request):
        sealed = submission.seal_submission(self.workspace, request["payload"]["draft_path"],
            execution_id="EX-worker", context=self.context, schema=self.schema, max_artifact_bytes=1024 * 1024)
        changes = {"runtime/artifacts/" + request["request_id"] + "/" + name: data
                   for name, data in sealed["artifacts"].items()}
        if self.head is None:
            changes["research/transport-fixture.json"] = canonical_json({"scope": "transport evidence only"})
        changes["runtime/artifacts/" + request["request_id"] + "/receipt-check.json"] = canonical_json(sealed["check"])
        snapshot = self.store.publish(self.head, changes)
        self.head = snapshot.head
        return ({"state": "rejected", "reason": "Draft validation failed", "result": sealed["check"]} if not sealed["passed"] else
                 {"state": "accepted", "published": True, "snapshot": self.head})

    def test_real_mcp_intent_and_receipt_share_preserved_git_evidence(self):
        check = submission.producer_check(self.workspace, self.draft)
        request = {"request_id": "CT-local", "kind": "submit_intent",
                   "payload": {"draft_path": check["raw_output_path"]}}
        self.assertEqual("submitted", self.mcp("control_submit", request)["state"])
        receipts = self.transport.pump(self.publish_intent)
        self.assertTrue(receipts and all(row["state"] == "accepted" for row in receipts), receipts)
        receipt = self.mcp("control_receipt", {"request_id": "CT-local", "wait_seconds": 0})
        self.assertEqual("accepted", receipt["state"])
        self.assertEqual(self.head, receipt["snapshot"])
        self.assertEqual(self.draft.read_bytes(), self.store.read_bytes(self.head, "runtime/artifacts/CT-local/output.json"))
        previous_head = self.head
        self.transport.pump(lambda _: self.fail("A replay must not publish twice"))
        self.assertEqual(previous_head, self.head)

    def test_mcp_configuration_preserves_leading_hyphen_tokens(self):
        from unittest.mock import patch
        with patch("do_math.control_transport.token_urlsafe", side_effect=["-transport-token", "-capability-token"]):
            self.binding = self.transport.issue("EX-worker", "GR-worker")
        result = self.mcp("control_receipt", {"request_id": "CT-not-submitted", "wait_seconds": 0})
        self.assertIsNone(result)

    def test_submit_draft_mcp_derives_internal_evidence_from_one_path(self):
        result = self.mcp("submit_draft", {"draft_path": ".scratch/draft.json", "wait_seconds": 0})
        self.assertEqual({"draft_path": ".scratch/draft.json"},
                         json.loads(next((self.root / "delivery" / self.binding["transport_id"] / "inbox").glob("*.json")).read_text())["payload"])
        self.assertEqual("submitted", result["delivery"]["state"])
        receipt = self.transport.pump(self.publish_intent)[0]
        self.assertEqual("accepted", receipt["state"])

    def test_installed_submit_command_waits_for_real_central_receipt(self):
        import time
        command = [*self.context["submission_contract"]["command"], "--output", str(self.draft), "--submit", "--wait-seconds", "20"]
        process = subprocess.Popen(command, cwd=self.workspace, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            until = time.monotonic() + 25
            while process.poll() is None and time.monotonic() < until:
                self.transport.pump(self.publish_intent)
                time.sleep(.02)
            stdout, stderr = process.communicate(timeout=5)
        finally:
            if process.poll() is None:
                process.kill()
                process.communicate()
        self.assertEqual(0, process.returncode, stderr.decode("utf-8", "replace") + stdout.decode("utf-8", "replace"))
        result = json.loads(stdout)
        self.assertEqual("accepted", result["delivery"]["state"])
        self.assertEqual(self.head, result["delivery"]["snapshot"])

    def test_accepted_submission_is_unchanged_when_original_draft_changes_later(self):
        check = submission.producer_check(self.workspace, self.draft)
        original = self.draft.read_bytes()
        self.mcp("control_submit", {"request_id": "CT-changed", "kind": "submit_intent",
                                     "payload": {"draft_path": check["raw_output_path"]}})
        self.transport.pump(self.publish_intent)
        receipt = self.mcp("control_receipt", {"request_id": "CT-changed", "wait_seconds": 0})
        self.assertEqual("accepted", receipt["state"])
        self.draft.write_bytes(canonical_json({"changed": True}))
        self.assertEqual(original, self.store.read_bytes(self.head,
            "runtime/artifacts/CT-changed/output.json"))

    def test_invalid_wait_budget_does_not_queue_a_request(self):
        for budget in (-1, float("nan"), float("inf"), True):
            with self.subTest(budget=budget), self.assertRaises(ValueError):
                submission.request_control(self.workspace, ".scratch/draft.json", kind="submit_intent", wait_seconds=budget)
        self.transport.pump(lambda _: self.fail("Invalid budget queued a request"))

    def test_preview_is_an_explicit_nonpublication_control_request(self):
        delivery = submission.request_control(self.workspace, ".scratch/draft.json",
            kind="submission_preview", wait_seconds=0)
        self.assertEqual("submitted", delivery["state"])
        # This tests transport semantics only; actual domain preview is tested separately.
        result = {"contract_id": submission.PREVIEW_CONTRACT_ID, "passed": False, "authoritative": False,
                  "issues": [{"rule_id": "integration.candidate", "message": "Visible candidate issue"}]}
        self.transport.pump(lambda request: {"state": "previewed", "result": result})
        receipt = self.mcp("control_receipt", {"request_id": delivery["request_id"], "wait_seconds": 0})
        self.assertEqual("previewed", receipt["state"])
        self.assertEqual(result, receipt["result"])
        self.assertIsNone(self.head)


class ProducerToolTests(purpose.ActivatedPurposeHarness):
    def setUp(self):
        super().setUp()
        # Producer-only checks write their workspaces here; an engine check
        # replaces root with its restored copy.
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)

    def test_revoked_original_grant_preserves_late_output_despite_alternative_grant(self):
        from do_math import governance
        from do_math.engine import control
        engine, _ = self.make_active(**self.fixture_config(scholarly_enabled=False))
        engine.runtime["queue"] = [{"id": "AC-revoked", "role": "maintenance"}]
        grant = next(value for value in engine.instance["grants"].values() if "maintenance" in value.get("roles", []))
        alternative = {**deepcopy(grant), "id": "ZZ-alternative"}
        engine.instance["grants"][alternative["id"]] = alternative
        engine._save()
        class Runner:
            def run(inner, **args):
                args["on_started"]({"pid": 1})
                execution = next(value for value in engine.runtime["executions"].values() if value["status"] == "running")
                await_control(engine, control(self.repo, engine.instance['id'], 'decision', config={'change': {
                    'kind': 'revoke', 'grant_id': execution['grant_id']}}))
                unbound = {key: value for key, value in execution['action'].items() if key != 'grant_id'}
                self.assertTrue(governance.authorize(engine.instance, unbound)['allowed'])
                return {"status": "completed", "output": {**purpose.common("Completed before revocation."),
                    "report": "Preserve the completed portion.", "remaining_work": []}, "usage": {}}
        engine.runner = CheckedRunner(Runner())
        engine.run(max_steps=1)
        execution = next(e for e in engine.runtime['executions'].values() if e['action']['id'] == 'AC-revoked')
        self.assertEqual(execution['status'], 'ended')
        self.assertNotEqual(execution['outcome'], 'output_accepted')
        self.assertEqual(execution.get('stop_requested'), 'grant_revoked')
        preserved = json.loads(engine.store.read(execution['result_ref']))
        self.assertEqual(preserved['output']['report'], 'Preserve the completed portion.')
        self.assertIn("AC-revoked", engine.runtime["waiting_actions"])

    def test_unsealed_invalid_runner_output_is_preserved_for_operational_review(self):
        engine, _ = self.make_active(**self.fixture_config(scholarly_enabled=False, max_output_repairs=0))
        before = set(engine.runtime["executions"])
        class Runner:
            def run(inner, **args):
                args["on_started"]({"pid": 1})
                return {"status": "failed", "output": {}, "usage": {}, "error_kind": "output_validation",
                        "error": "output/candidates: required property is missing"}
        engine.runner = CheckedRunner(Runner())
        engine.run(max_steps=1)
        execution = next(value for key, value in engine.runtime["executions"].items() if key not in before)
        self.assertEqual(execution["outcome"], "execution_incomplete")
        self.assertIn(execution["action"]["id"], engine.runtime["waiting_actions"])
        self.assertTrue(any(a["role"] == "operational_review" and a.get("target") == execution["id"]
                            for a in engine.runtime["queue"]))
        self.assertFalse(any(a.get("repair") for a in engine.runtime["queue"]))

    def test_local_call_timeout_parks_only_the_timed_out_request(self):
        import time
        # The one-second deadline belongs to the calls under test, not to activation's intent calls.
        engine, _ = self.make_active(**self.fixture_config(scholarly_enabled=False, call_timeout_seconds=1))
        engine.runtime["queue"] = [{"id": "AC-timeout", "role": "maintenance"},
                                   {"id": "AC-independent", "role": "research_preparation"}]
        engine._save()
        class Runner:
            def run(inner, **args):
                args["on_started"]({"pid": 1})
                time.sleep(1.05)
                self.assertTrue(await_stop(args["should_stop"], 10))
                return {"status": "stopped", "output": None, "usage": {}, "error": "local call deadline"}
        engine.runner = CheckedRunner(Runner())
        engine.run(max_steps=1)
        self.assertNotEqual(engine.runtime["status"], "paused")
        self.assertIn("AC-timeout", engine.runtime["waiting_actions"])
        self.assertTrue(any(a.get("id") == "AC-independent" for a in engine.runtime["queue"]))

    def test_receiver_rejects_unknown_insight_kind_and_missing_evidence(self):
        for changes in ({"kind": "unregistered_kind"}, {"evidence_ids": ["KN-missing"]}):
            with self.subTest(changes=changes):
                engine, _ = self.make_active(**self.fixture_config(scholarly_enabled=False, max_output_repairs=0))
                before = set(engine.runtime['executions'])
                output = {**purpose.common("Preserve a candidate."), "candidates": []}
                insight = {"kind": "question", "title": "Question", "statement": "What remains?",
                           "summary": "An open question.", "evidence_ids": [], **changes}
                class Runner:
                    def run(inner, **args):
                        args["on_started"]({"pid": 1})
                        (args["workspace"] / "activity-extensions.json").write_bytes(canonical_json({"research_insights": [insight]}))
                        return {"status": "completed", "output": output, "usage": {}}
                engine.runner = CheckedRunner(Runner())
                engine.run(max_steps=1)
                execution = next(e for eid, e in engine.runtime['executions'].items() if eid not in before)
                self.assertEqual(execution["outcome"], "execution_incomplete")
                self.assertEqual(engine.instance["knowledge"], {})
                saved = engine.store.read(execution['submitted_output_ref'])
                self.assertEqual(json.loads(saved), output)

    def prepare(self, role="research_preparation", *, context_values=None, **configuration):
        workspace = self.root / (role + "-producer-" + str(len(list(self.root.glob(role + "-producer-*")))))
        workspace.mkdir(exist_ok=True)
        context = {"action": {"id": "AC-producer", "role": role}, "execution_id": "EX-producer",
            "snapshot": "fixed-producer-input", "observed_at": "2026-09-23T00:00:00Z", "budget_unit": "concurrent_sessions",
            "tasks": [], "ready_task_ids": [], "knowledge_catalog": [], "sources": [],
            "kind_definitions": knowledge_io.catalog_definitions(knowledge_io.ensure_ontology({}))}
        context.update(context_values or {})
        submission.install_tools(workspace, context, contracts.action_schema(context["action"]),
                                 configuration.get("max_artifact_bytes"))
        self.assertIn("submission_contract", context,
                      "the producer needs an executable check, fixed inputs and limits")
        self.assertTrue(context["submission_contract"]["command"])
        return None, workspace, context

    def check_output(self, workspace, context, output, extension=None):
        output = deepcopy(output)
        draft = workspace / ".scratch/submission.json"
        draft.parent.mkdir(exist_ok=True)
        if extension is not None:
            (workspace / "activity-extensions.json").write_bytes(canonical_json(extension))
        if "integration_bundles" not in output:
            seal_response(output, context, workspace)
        draft.write_bytes(canonical_json(output))
        command = [*context["submission_contract"]["command"], "--output", str(draft)]
        process = subprocess.run(command, cwd=workspace, capture_output=True, timeout=30)
        self.assertIn(process.returncode, (0, 1), process.stderr.decode("utf-8", "replace"))
        result = json.loads(process.stdout)
        self.assertEqual(process.returncode == 0, result["passed"])
        self.assertEqual(json.loads(draft.read_bytes()), output, "a validator cannot rewrite the author's meaning")
        return result

    def test_producer_checks_main_shape_and_preserves_precise_failure_coordinates(self):
        _, workspace, context = self.prepare()
        valid = {**purpose.common("A bounded preparation."), "candidates": []}
        self.assertTrue(self.check_output(workspace, context, valid)["passed"])
        invalid = {key: value for key, value in valid.items() if key != "candidates"}
        result = self.check_output(workspace, context, invalid)
        self.assertFalse(result["passed"])
        self.assertIn("candidates", json.dumps(result["issues"]))

    def test_producer_checks_used_sources(self):
        _, workspace, context = self.prepare()
        output = {**purpose.common("A bounded preparation."), "candidates": [], "used_sources": ["KN-missing"]}
        self.assertFalse(self.check_output(workspace, context, output)["passed"])

    def test_reference_support_includes_visible_execution_history_and_supplied_catalogs(self):
        from do_math.context_store import fit_context
        previous = "EX-earlier"
        _, workspace, context = self.prepare(context_values={
            "preparation_history": [{"execution_id": previous, "report": "Earlier preparation result"}],
            "goal": "g", "large_optional_evidence": {"text": "x" * 30000}})
        fitted = fit_context(context, max_bytes=20000, workspace=workspace, mandatory_keys=["goal", "action"])
        catalog = next(row["path"] for row in fitted["manifest"] if row["key"] == "kind_definitions")
        for reference in (previous, catalog):
            with self.subTest(reference=reference):
                output = {**purpose.common("Read the supplied evidence."), "candidates": [], "used_sources": [reference]}
                self.assertTrue(self.check_output(workspace, context, output)["passed"])
    def test_producer_checks_checkpoint_evidence_paths(self):
        _, workspace, context = self.prepare()
        output = {**purpose.common("A bounded preparation."), "candidates": []}
        (workspace / "checkpoint.json").write_bytes(canonical_json({
            "current_claim": "A bounded result", "evidence_paths": ["missing-proof.txt"],
            "attempts": [], "remaining_work": [], "next_step": "submit", "progress_state": "ready_to_submit"}))
        result = self.check_output(workspace, context, output)
        self.assertFalse(result["passed"])
        self.assertIn("missing-proof.txt", json.dumps(result["issues"]))

    def test_live_review_validates_sidecar_before_applying_continue(self):
        # From the prepared task: the live review of its work is the subject.
        engine, runner = purpose_copy(self, purpose.PurposeRunner(observation="continue"), until="prepared",
            config=self.fixture_config(scholarly_enabled=False, tool_review_window_seconds=1))
        original = runner.answer
        def answer(role, context, workspace):
            if role == "operational_review":
                (workspace / "activity-extensions.json").write_bytes(canonical_json({"research_insights": [{
                    "kind": "not_registered", "title": "Bad insight", "statement": "x", "summary": "x"}]}))
            return original(role, context, workspace)
        runner.answer = answer
        self.drive(engine, predicate=lambda e: any(x["role"] == "operational_review" and x["status"] == "ended" for x in e.runtime["executions"].values()))
        reviewed = next(x for x in engine.runtime["executions"].values() if x["role"] == "operational_review")
        self.assertEqual(reviewed["outcome"], "execution_incomplete")
        target = engine.runtime["executions"][reviewed["action"]["target"]]
        self.assertNotIn("operational_continuation", target)
        self.assertFalse(any(row.get("execution_id") == reviewed["id"]
                             for row in engine.runtime.get("operational_dispositions", {}).values()))

    def test_producer_checks_sidecar_kinds_references_and_self_repair(self):
        _, workspace, context = self.prepare()
        output = {**purpose.common("A bounded preparation."), "candidates": []}
        insight = {"kind": "unregistered_kind", "title": "Question", "statement": "What remains?",
                   "summary": "An open question.", "evidence_ids": ["KN-missing"]}
        result = self.check_output(workspace, context, output, {"research_insights": [insight]})
        self.assertFalse(result["passed"])
        self.assertIn("research_insights", json.dumps(result["issues"]))
        insight.update(kind="question", evidence_ids=[])
        self.assertTrue(self.check_output(workspace, context, output, {"research_insights": [insight]})["passed"])

    def test_empty_known_extension_family_remains_a_semantic_noop(self):
        _, workspace, context = self.prepare("maintenance")
        output = {**purpose.common("No changes requested."), "report": "Observed only.", "remaining_work": []}
        self.assertTrue(self.check_output(workspace, context, output, {"knowledge_changes": []})["passed"])

    def test_producer_receives_artifact_and_checkpoint_limits_and_excludes_disposable_scratch(self):
        _, workspace, context = self.prepare(max_artifact_bytes=100)
        limits = context["submission_contract"]["limits"]
        self.assertEqual(limits["max_artifact_bytes"], 100)
        self.assertEqual(limits["checkpoint_bytes"], 4 * 1024 * 1024)
        self.assertNotIn("observation_rules_bytes", limits)
        output = {**purpose.common("No proposal."), "candidates": []}
        (workspace / ".scratch").mkdir()
        (workspace / ".scratch/disposable.bin").write_bytes(b"x" * 101)
        self.assertTrue(self.check_output(workspace, context, output)["passed"])
        (workspace / "evidence.bin").write_bytes(b"x" * 101)
        result = self.check_output(workspace, context, output)
        self.assertFalse(result["passed"])
        self.assertIn("evidence.bin", json.dumps(result["issues"]))

    def test_producer_checks_live_checkpoint_but_not_a_rules_file(self):
        _, workspace, context = self.prepare()
        output = {**purpose.common("No proposal."), "candidates": []}
        (workspace / "checkpoint.json").write_text('{"current_claim":"unfinished schema"}', encoding="utf-8")
        # Rules change only through a self-check response; a leftover rules file is ordinary output.
        (workspace / "observation-rules.json").write_text('[{"id":"bad","op":"counter_gte","threshold":true}]', encoding="utf-8")
        result = self.check_output(workspace, context, output)
        self.assertFalse(result["passed"])
        issues = json.dumps(result["issues"])
        self.assertIn("checkpoint.json", issues)
        self.assertNotIn("observation-rules.json", issues)

    def test_producer_checks_planning_population_and_exact_completion_criteria(self):
        from research_fixtures import candidate, disposition
        tid = "TK-ready"
        task = {**candidate(), "id": tid, "revision": 1, "status": "planned", "results": []}
        _, workspace, context = self.prepare("research_plan", context_values={"tasks": [task], "ready_task_ids": [tid]})
        self.assertIn("submission_contract", context)
        output = {**purpose.common("Current population."), "dispositions": [],
                  "preparation_requests": [], "goal_audit": False, "task_assessments": []}
        result = self.check_output(workspace, context, output)
        self.assertFalse(result["passed"])
        self.assertIn("every derived-ready task", json.dumps(result["issues"]))
        output["dispositions"] = [{**disposition(tid), "uncertainty": ""}]
        extension = {"model_assessments": [{"task_id": tid, "difficulty": "low", "importance": "low", "reason": "Bounded task"}]}
        self.assertTrue(self.check_output(workspace, context, output, extension)["passed"])
        task.update(status="waiting", results=[{"execution_id": "EX-work", "report": "Partial argument"}])
        _, workspace, context = self.prepare("research_plan", context_values={"tasks": [task], "ready_task_ids": []})
        output["dispositions"] = []
        output["task_assessments"] = [{"task_id": tid, "decision": "completed", "reason": "Claimed complete",
                                       "item_dispositions": [], "unresolved": []}]
        self.assertFalse(self.check_output(workspace, context, output, {})["passed"])

    def test_supplied_checker_is_standalone_and_does_not_mutate_fixed_inputs(self):
        import zipfile
        _, workspace, context = self.prepare()
        with zipfile.ZipFile(workspace / "input/tools/submission-support.zip") as archive:
            self.assertNotIn("do_math/engine.py", archive.namelist())
            self.assertFalse(any(name.endswith("_engine.py") for name in archive.namelist()))
            self.assertIn("do_math/record_schemas/__init__.py", archive.namelist())
        before = {p.relative_to(workspace).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                  for p in (workspace / "input").rglob("*") if p.is_file()}
        self.assertTrue(self.check_output(workspace, context,
            {**purpose.common("No proposal."), "candidates": []})["passed"])
        after = {p.relative_to(workspace).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                 for p in (workspace / "input").rglob("*") if p.is_file()}
        self.assertEqual(after, before)
        for part in context["submission_contract"]["command"][1:]:
            if part.endswith(".py"):
                self.assertTrue((workspace / part).resolve().is_relative_to(workspace.resolve()))


    def test_producer_check_reuses_the_prepared_tool_digest(self):
        from unittest.mock import patch
        _, workspace, context = self.prepare()
        output = {**purpose.common("No proposal."), "candidates": []}
        seal_response(output, context, workspace)
        draft = workspace / ".scratch/submission.json"
        draft.parent.mkdir(exist_ok=True)
        draft.write_bytes(canonical_json(output))
        with patch.object(submission, "read_stable", wraps=submission.read_stable) as read:
            result = submission._producer_check(workspace, ".scratch/submission.json", [])
        self.assertEqual(result["tool_sha256"], context["submission_contract"]["tool_sha256"])
        # Preparation fixed the archive digest; a tool call never rereads the archive.
        self.assertFalse(any(str(call.args[0]).endswith("submission-support.zip") for call in read.call_args_list))


class OperatorProducerTests(purpose.ActivatedPurposeHarness):
    def test_failure_recovery_preserves_a_structured_nonresearch_report(self):
        from unittest.mock import patch
        from do_math import scheduled_operator as operator
        engine, _ = self.make_active(**self.fixture_config(scholarly_enabled=False, operator_enabled=True))
        observed = []
        class Runner:
            @local_job_runner
            def run(inner, **args):
                args["on_started"]()
                self.assertEqual(args["output_schema"], operator.OPERATOR_SCHEMA)
                self.assertIn("Synthetic launcher failure", args["prompt"])
                self.assertFalse((args["workspace"] / "input/submission/context.json").exists(),
                                 "installation recovery must not acquire the research submission path")
                output = {"summary": "Observed current status.", "observed_status": "ready", "actions": [],
                          "evidence_paths": [], "user_questions": [], "next_step": "Return the recorded observation."}
                observed.append(output)
                # ModelRunner owns schema validation; this fixture reports the
                # corresponding failed execution without granting repair success.
                return {"status": "failed", "output": output, "usage": {}, "error_kind": "output_validation",
                        "error": "Scripted diagnosis remains incomplete"}
        with patch.object(operator, "ModelRunner", Runner):
            result = operator.recovery(self.repo, engine.instance["id"], self.root,
                failure={"kind": "engine_unavailable", "error": "Synthetic launcher failure"})
        self.assertEqual(result["outcome"], "recovery_failed", result)
        self.assertEqual(len(observed), 1)
        _, state, runtime = operator.ResearchRepository(self.repo, engine.instance["id"]).load()
        execution = runtime["executions"][result["execution_id"]]
        self.assertEqual(execution["output"], observed[0])
        self.assertEqual(execution["outcome"], "execution_incomplete")
        self.assertNotIn("submission_receipt", execution)
        self.assertEqual(runtime["activities"][execution["owner_activity_id"]]["waiting"]["reason"], "recovery_failed")
        self.assertEqual(state["knowledge"], engine.instance["knowledge"])


class ReviewFailureTests(purpose.ActivatedPurposeHarness):
    # These checks start after initialization; preserve real Git-backed
    # review and submission while reusing validated active state. The flow
    # formally checks its knowledge, so formal checks pin the seed's active
    # trust environment command (state_fixtures.ACTIVE_LEAN_COMMAND).
    CONFIG = purpose.PurposeHarness.fixture_config(scholarly_enabled=False, lean_command=list(ACTIVE_LEAN_COMMAND))

    def make_active(self):
        return super().make_active(**self.CONFIG)

    def make_review(self):
        """The same active state after the real task flow opened its identity review cycle."""
        return purpose_copy(self, purpose.PurposeRunner(), until="review", config=self.CONFIG,
                            external_policy="explicit_grants", signed=False)

    @staticmethod
    def review_is_next(engine):
        # Operating roles dispatch without a slot (decision 4), so a plan queued by the
        # imported knowledge runs first; these checks start when the review is next.
        queue = engine.runtime["queue"]
        return bool(engine.runtime["review_cycles"]) and bool(queue) and queue[0]["role"] == "identity_review"

    def test_failed_contract_review_is_not_regenerated_while_waiting_for_diagnosis(self):
        engine, _ = self.make_active()
        engine.run(max_steps=1)
        task_id = next(iter(engine.runtime["tasks"]))
        class Runner:
            def run(inner, **args):
                args["on_started"]({"pid": 1})
                return {"status": "failed", "output": None, "usage": {}, "error": "reviewer unavailable"}
        engine.runner = CheckedRunner(Runner())
        engine.run(max_steps=1)
        self.assertTrue(any(e["action"].get("target") == task_id for e in engine.runtime["waiting_actions"].values()))
        self.assertFalse(any(a["role"] == "task_contract_review" and a.get("target") == task_id for a in engine.runtime["queue"]))

    def test_failed_identity_slot_is_not_regenerated_after_its_peer_finishes(self):
        engine, runner = self.make_review()
        original_run, original_answer = runner.run, runner.answer
        def run(**args):
            context = purpose.parse_context(args["prompt"], args["workspace"])
            if context["action"].get("slot") == "initial-0":
                args["on_started"]({"pid": 1})
                return {"status": "failed", "output": None, "usage": {}, "error": "reviewer unavailable"}
            return original_run(**args)
        def answer(role, context, workspace):
            if role == "operational_review":
                return {**purpose.common("Preserved failure needs repair."), "disposition": {
                    "kind": "repair", "basis_refs": [context["action"]["target"]], "next_owner": "operations",
                    "reason": "Repair the execution environment.", "repair_target": "execution environment",
                    "meaning_preserving": True, "verification": "Repeat the failed environment check"}}
            return original_answer(role, context, workspace)
        runner.run, runner.answer = run, answer
        engine.run(max_steps=3)
        self.assertFalse(any(a["role"] == "identity_review" and a.get("slot") == "initial-0" for a in engine.runtime["queue"]))
        self.assertTrue(any(e["action"].get("slot") == "initial-0" for e in engine.runtime["waiting_actions"].values()))

    def test_explicit_diagnosis_can_open_one_new_attempt_of_a_failed_action(self):
        from do_math.engine import control
        engine, _ = self.make_active()
        engine.runtime["queue"] = [{"id": "AC-failed", "role": "maintenance"}]
        engine._save()
        class Runner:
            def run(inner, **args):
                context = purpose.parse_context(args["prompt"], args["workspace"])
                args["on_started"]({"pid": 1})
                if context["action"]["role"] == "maintenance":
                    return {"status": "failed", "output": None, "usage": {}, "error": "configuration failure"}
                return {"status": "completed", "usage": {}, "output": {
                    **purpose.common("The explicit repair diagnosis is complete."), "disposition": {
                        "kind": "retry", "basis_refs": [context["action"]["target"]], "next_owner": "engine",
                        "reason": "The independent operator repaired the execution configuration and requested this diagnosis.",
                        "scope": "One new attempt of the failed action", "replay_safety": "The failed local action produced no external effects"}}}
        engine.runner = CheckedRunner(Runner())
        engine.run(max_steps=1)
        failed = next(eid for eid, e in engine.runtime['executions'].items() if e['action']['id'] == 'AC-failed')
        control(self.repo, engine.instance["id"], "request", origin="operator", config={"role": "operational_review", "target": failed},
                text="Inspect the repaired execution configuration before one new attempt.")
        engine.process_controls()
        diagnosis = next(a for a in engine.runtime['queue'] if a['role'] == 'operational_review' and a.get('target') == failed)
        engine.runtime['queue'] = [diagnosis]
        engine._save()
        engine.run(max_steps=1)
        retries = [a for a in engine.runtime["queue"] if a["role"] == "maintenance"]
        self.assertEqual(len(retries), 1)
        self.assertEqual(retries[0]["id"], "AC-failed")
        self.assertEqual(retries[0]['continuation_of'], failed)

    # v5 task_scope decisions authorize named obligations; they do not directly
    # withdraw a live task. test_task_scope's live/terminal withdrawal regression
    # covers both research_work and task_contract_review at the owning boundary.

    def test_late_identity_result_is_preserved_without_retrying_a_superseded_slot(self):
        from do_math.engine import control
        engine, runner = self.make_review()
        if not self.review_is_next(engine):
            self.drive(engine, predicate=self.review_is_next)
        cid = next(iter(engine.runtime["review_cycles"]))
        original = runner.run
        def run(**args):
            result = original(**args)
            context = purpose.parse_context(args["prompt"], args["workspace"])
            from do_math.knowledge import plan_impact, revision_roots
            changes = {'explanation': 'A replacement explanation of the same domain.'}
            roots = revision_roots(engine.instance, context['action']['target'])
            await_control(engine, control(self.repo, engine.instance["id"], "knowledge", config={"operation": "revise", "id": context["action"]["target"],
                'changes': changes, 'declared_impact': plan_impact(engine.instance, engine.runtime, roots, [])['computed_impact'],
                "reason": "Revise the sealed proposal."}))
            return result
        runner.run = run
        engine.run(max_steps=1)
        self.assertFalse(any(a.get("review_cycle_id") == cid for a in engine.runtime["queue"]))
        review = next(e for e in engine.runtime["executions"].values() if e["role"] == "identity_review")
        self.assertNotEqual(review["outcome"], "output_accepted")
        self.assertIsNotNone(engine.store.read(review['submission_intent']['output_ref']))

    def test_large_own_review_history_does_not_request_mathematical_reconstruction(self):
        from do_math.review_cycle import record_turn
        engine, runner = self.make_review()
        if not self.review_is_next(engine):
            self.drive(engine, predicate=self.review_is_next)
        action = next(a for a in engine.runtime["queue"] if a["role"] == "identity_review")
        cid, kid = action["review_cycle_id"], action["target"]
        # The review input limit is its pinned profile's (context_store.prepare_role_input),
        # not the live config; the retained history alone exceeds it.
        limit = engine._execution_profile(action)["input"]["max_input_bytes"]
        engine.runtime["review_cycles"][cid] = record_turn(engine.runtime["review_cycles"][cid], action["slot"], [
            {"role": "assistant", "content": "Retained earlier reasoning. " * (limit // 28 + 1), "message_id": "retained-history"}])
        before = deepcopy(engine.instance["knowledge"][kid])
        engine._save()
        count = len(runner.calls)
        engine.run(max_steps=1)
        self.assertEqual(len(runner.calls), count)
        self.assertEqual(engine.instance["knowledge"][kid], before)
        self.assertFalse(any(row.get("event") == "review_resource_disposition"
                             for row in engine.runtime["review_cycles"][cid]["history"]))

    def test_fixed_question_resolver_accepts_the_supplied_source_aliases(self):
        from do_math.engine import control
        # Review input reads the instance's supplied sources when it is prepared,
        # so the source may arrive after the cycle opened.
        engine, _ = self.make_review()
        path = self.root / "paper.txt"
        path.write_text("The exact original source.", encoding="utf-8")
        control(self.repo, engine.instance["id"], "source", config={"path": str(path)})
        engine.process_controls()
        action = next(a for a in engine.runtime["queue"] if a["role"] == "identity_review")
        workspace = self.root / "source-alias-input"
        context = engine._context(action, workspace)
        source = context["sources"][0]
        cycle = engine.runtime["review_cycles"][action["review_cycle_id"]]
        for reference in (source["id"], "source:" + source["name"], source["local_path"], source["path"], source["name"]):
            with self.subTest(reference=reference):
                error = None
                try:
                    resolved = engine._research_source_spec(cycle, action, reference)
                except ValueError as rejected:
                    error = str(rejected)
                self.assertIsNone(error, "a supplied source alias was refused: " + str(error))
                self.assertEqual(resolved["sha256"], source["sha256"])
    def test_private_insight_rechecks_its_own_basis_when_published_after_peer_review(self):
        from do_math.engine import control
        engine, runner = self.make_active()
        control(self.repo, engine.instance["id"], "knowledge", config={"operation": "import", "candidate": {
            "kind": "observation", "title": "Earlier computation", "statement": "The answer is one.",
            "explanation": "A bounded computation.", "summary": "One was computed.", "lean_code": ""}})
        engine.process_controls()
        kid = next(iter(engine.instance["knowledge"]))
        engine.runtime["queue"] = [a for a in engine.runtime["queue"] if a["role"] == "research_preparation"]
        engine._save()
        original_run, original_answer = runner.run, runner.answer
        def answer(role, context, workspace):
            action = context["action"]
            if role == 'identity_review' and action.get('stage') == 'initial' and action.get('slot') == 'initial-0':
                (workspace / 'activity-extensions.json').write_bytes(canonical_json({'research_insights': [{
                    'kind': 'question', 'title': 'Private followup', 'statement': 'What follows from the old computation?',
                    'summary': 'A possible followup.', 'evidence_ids': [kid]}]}))
            return original_answer(role, context, workspace)
        def run(**args):
            context = purpose.parse_context(args['prompt'], args['workspace'])
            result = original_run(**args)
            action = context['action']
            if action['role'] == 'identity_review' and action.get('stage') == 'initial' and action.get('slot') == 'initial-1':
                from do_math.knowledge import plan_impact, revision_roots
                changes = {'statement': 'The corrected answer is two.'}
                roots = revision_roots(engine.instance, kid)
                await_control(engine, control(self.repo, engine.instance['id'], 'knowledge', config={'operation': 'revise', 'id': kid,
                    'changes': changes, 'declared_impact': plan_impact(engine.instance, engine.runtime, roots, [])['computed_impact'],
                    'reason': 'Correct a computation.'}))
            return result
        runner.run, runner.answer = run, answer
        self.drive(engine, predicate=lambda e: any(k["title"] == "Private followup" for k in e.instance["knowledge"].values()))
        insight = next(k for k in engine.instance["knowledge"].values() if k["title"] == "Private followup")
        self.assertTrue(insight.get("use_suspended", False))
        self.assertEqual(insight["lifecycle"], "active")
        from do_math.knowledge import assess_use
        self.assertFalse(assess_use(insight, engine.instance)["valid"])
        self.assertEqual(insight["dependencies"], [kid])


if __name__ == "__main__":
    unittest.main(verbosity=2)
