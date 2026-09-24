"""Central v5 connections: domain failures must remain observable at consumers.

These tests use in-memory engine state for response routing. They do not claim
that an AI interpretation is semantically correct or that a provider ran.
"""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import sys
import unittest
from unittest.mock import Mock, patch
import tempfile
import subprocess
import hashlib
import json

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math.engine import ResearchEngine, _records
from do_math import execution_profiles, activities
from do_math.engine import DEFAULT_CONFIG, initialize, _repository, read_record, control
from do_math.repository import canonical_json
from do_math import integration


def routing_engine():
    engine = object.__new__(ResearchEngine)
    engine._slots = None
    engine.instance = {"id": "RI-test", "knowledge": {}, "relations": [],
                       "goal": "Original approved goal", "policies": "", "goal_status": "unresolved",
                       "config": {"goal_auditors": 2}, "goal_kind": "mathematical"}
    engine.runtime = {"tasks": {}, "activities": {}, "executions": {}, "queue": [],
                      "questions": [], "question_links": [], "history": [], "inputs": [],
                      "interpretations": {}, "status": "ready"}
    engine._bind_revision_action = Mock()
    engine._cancel_selected_revision_targets = Mock()
    engine._record_output_questions = Mock()
    return engine


class IntentConnections(unittest.TestCase):
    def make_import(self, engine, *, clarification=False, payload=None):
        text = "Keep the original purpose."
        engine.runtime["inputs"] = [{"id": "UC-input", "text": text, "config": {}, "origin": "user"}]
        questions = ["Which scope?"] if clarification else []
        output = {"summary": "interpretation", "used_sources": [], "questions": questions,
            "needs_clarification": clarification, "import_units": [{"unit_id": "IU-one",
                "source_range": {"start": 0, "end": len(text)}, "interpretation": text,
                "owner_kind": "charter", "owner_ref": "CH-one", "payload": payload or {},
                "decision_refs": [], "question_refs": ["Q-one"] if clarification else []}],
            "question_details": [{"id": "Q-one", "question_index": 0, "blocks": True,
                "target_ids": ["RI-test"], "reason": "scope choice changes the work", "source_unit_ids": ["IU-one"],
                "options": []}] if clarification else []}
        author_action = {"id": "AC-author", "role": "intent_interpretation", "target": "UC-input", "lineage_id": "AC-root"}
        engine.runtime["executions"]["EX-author"] = {"id": "EX-author", "status": "running",
            "role": "intent_interpretation", "action": deepcopy(author_action)}
        engine._apply(author_action, output, "EX-author")
        engine.runtime["executions"]["EX-author"]["status"] = "ended"
        bundle = next(iter(engine.runtime["intent_imports"].values()))
        engine.runtime["executions"]["EX-check"] = {"id": "EX-check", "role": "intent_interpretation",
                                                    "status": "ended", "intent_import_sha256": bundle["sha256"]}
        action = deepcopy(engine.runtime["queue"][0])
        engine.runtime["queue"] = []
        return bundle, action

    def verdict(self, bundle, decision="approved", complete=True):
        return {"decision": decision, "scope_complete": complete, "bundle_sha256": bundle["sha256"],
                "unit_ids": ["IU-one"], "question_ids": [q["id"] for q in bundle["output"]["question_details"]],
                "findings": [] if decision == "approved" else ["Missing second clause"],
                "summary": "check", "used_sources": [], "questions": []}

    def test_clarification_still_receives_independent_check(self):
        engine = routing_engine()
        bundle, action = self.make_import(engine, clarification=True)
        self.assertEqual(action["stage"], "check")
        self.assertEqual(action["import_id"], bundle["id"])
        self.assertEqual(engine.runtime["question_links"], [])
        engine._record_output_questions.assert_not_called()

    def test_failed_check_returns_to_authoring_with_findings(self):
        engine = routing_engine()
        bundle, action = self.make_import(engine)
        engine._apply(action, self.verdict(bundle, "revision_required", False), "EX-check")
        retry = engine.runtime["queue"][0]
        self.assertEqual(retry["stage"], "interpret")
        self.assertEqual(retry["lineage_id"], "AC-root")
        self.assertEqual(retry["previous_import_id"], bundle["id"])
        self.assertEqual(retry["intent_repair"]["findings"], ["Missing second clause"])
        self.assertEqual(engine.runtime["questions"], [])

    def test_check_cannot_apply_unresolved_proposed_changes(self):
        engine = routing_engine()
        bundle, action = self.make_import(engine, clarification=True,
            payload={"kind": "charter", "record": {"id": "CH-one"}})
        engine._apply(action, self.verdict(bundle), "EX-check")
        self.assertEqual(engine.instance["goal"], "Original approved goal")
        self.assertEqual(engine.runtime["intent_imports"][bundle["id"]]["application"]["status"], "awaiting_decision")
        self.assertEqual(len(engine.runtime["question_links"]), 1)
        self.assertFalse(any(a["role"] == "research_preparation" for a in engine.runtime["queue"]))


class QueryIdentity(unittest.TestCase):
    def test_exact_evidence_binds_persisted_bytes_and_code_points(self):
        from do_math.engine import _record_evidence
        from do_math.repository import exact_content_hash
        record = {"id": "FR-one", "title": "e\u0301", "verification": {"K": "e\u0301", "K": "é"}}
        def evidence(value):
            raw = canonical_json({"record": value})
            row = {"snapshot": "snapshot", "path": "research/formal_results/FR-one.json", "record": value,
                "bytes": raw, "sha256": hashlib.sha256(raw).hexdigest(), "json_pointer": "/record"}
            return _record_evidence(row)
        first = evidence(record)
        self.assertEqual(first["json_pointer"], "/record")
        self.assertEqual(first["sha256"], hashlib.sha256(canonical_json({"record": record})).hexdigest())
        self.assertEqual(first["logical_sha256"], exact_content_hash(record))
        same_metadata = {**record, "title": "é"}
        self.assertNotEqual(first["semantic_sha256"], evidence(same_metadata)["semantic_sha256"])
        changed_payload = {**record, "verification": {"K": "é", "K": "é"}}
        self.assertNotEqual(first["semantic_sha256"], evidence(changed_payload)["semantic_sha256"])

    def test_duplicate_id_is_rejected_across_families(self):
        engine = routing_engine()
        engine.instance["knowledge"]["DUP"] = {"id": "DUP"}
        engine.runtime["tasks"]["DUP"] = {"id": "DUP"}
        with self.assertRaisesRegex(ValueError, "[Dd]uplicate|collision"):
            _records(engine.instance, engine.runtime)


class ObservationMerge(unittest.TestCase):
    def test_merged_review_keeps_all_obligations_and_evidence_refs(self):
        engine = routing_engine()
        engine._enqueue("operational_review", "EX-worker", live=True,
                        obligation_ids=["OB-a"], observation_refs=["artifact:a"],
                        observation={"kind": "operational_review_due", "reason": "explicit", "sequence": 1})
        first = deepcopy(engine.runtime["queue"][0])
        engine._enqueue("operational_review", "EX-worker", live=True,
                        obligation_ids=["OB-b"], observation_refs=["artifact:b"],
                        observation={"kind": "operational_review_due", "reason": "periodic", "sequence": 2})
        self.assertEqual(len(engine.runtime["queue"]), 1)
        merged = engine.runtime["queue"][0]
        self.assertEqual(merged["id"], first["id"])
        self.assertEqual(merged["obligation_ids"], ["OB-a", "OB-b"])
        self.assertEqual(merged["observation_refs"], ["artifact:a", "artifact:b"])
        self.assertEqual(merged["observation"]["sequence"], 2)


class KnowledgeConnections(unittest.TestCase):
    def test_research_receipt_creates_separate_knowledge_authorities(self):
        engine = routing_engine()
        engine.instance.update(feature_version=5, sources=[], kind_definitions={})
        engine.instance["config"]["reviewers"] = 2
        engine.runtime["tasks"]["TK-work"] = {"id": "TK-work", "status": "active", "results": []}
        engine.runtime["executions"]["EX-work"] = {"id": "EX-work", "status": "ended", "extensions": {}}
        output = {"summary": "result", "used_sources": [], "questions": [], "report": "Established a result",
                  "outcome": "submitted", "remaining_work": [], "checkpoint": "done", "relations": [],
                  "knowledge": [{"kind": "theorem", "title": "T", "statement": "True", "explanation": "By construction",
                                 "summary": "True holds", "lean_code": "theorem t : True := by trivial",
                                 "declaration_names": ["t"], "dependencies": []}]}
        engine._apply({"id": "AC-work", "role": "research_work", "target": "TK-work"}, output, "EX-work")
        record = next(iter(engine.instance["knowledge"].values()))
        self.assertNotIn("lean_code", record)
        self.assertNotIn("formal", record)
        self.assertNotIn("reviews", record)
        self.assertIn(record["formal_result_id"], engine.instance["formal_results"])
        self.assertIn(record["exposition_id"], engine.instance["expositions"])
        self.assertEqual(len(engine.runtime["tasks"]["TK-work"]["results"]), 1)
        self.assertEqual(engine.runtime["tasks"]["TK-work"]["status"], "waiting")

    def test_independent_bundle_does_not_repeat_the_task_report(self):
        engine = routing_engine()
        self.assertIn("owns_response", __import__("inspect").signature(engine._apply).parameters)
        engine.instance.update(feature_version=5, sources=[], kind_definitions={})
        engine.instance["config"]["reviewers"] = 2
        engine.runtime["tasks"]["TK-work"] = {"id": "TK-work", "status": "waiting", "results": [{"report": "already accepted"}]}
        engine.runtime["executions"]["EX-work"] = {"id": "EX-work", "status": "ended", "extensions": {}}
        output = {"report": "already accepted", "outcome": "submitted", "remaining_work": [],
                  "summary": "result", "questions": [], "knowledge": [], "relations": []}
        engine._apply({"id": "AC-work", "role": "research_work", "target": "TK-work"}, output, "EX-work", owns_response=False)
        self.assertEqual(engine.runtime["tasks"]["TK-work"]["results"], [{"report": "already accepted"}])


class BundleConnections(unittest.TestCase):
    def test_independent_commit_survives_later_bundle_failure_and_retry(self):
        engine = routing_engine()
        engine.head = "input-snapshot"
        engine._saved_state = None
        engine.runtime["executions"]["EX-work"] = {"id": "EX-work", "input_snapshot": engine.head}
        engine.instance["accepted_titles"] = []
        engine.store = Mock()
        published = []
        def save(head, instance, runtime, **kwargs):
            published.append((deepcopy(instance), deepcopy(runtime)))
            return "snapshot-" + str(len(published)), deepcopy(instance), deepcopy(runtime)
        engine.store.save_with_state.side_effect = save
        engine.store.load.side_effect = lambda head=None: (head or "snapshot-" + str(len(published)),
            deepcopy(published[-1][0]), deepcopy(published[-1][1]))
        engine.store.validate_candidate = Mock(side_effect=lambda instance, runtime, head: {"instance": deepcopy(instance), "runtime": deepcopy(runtime)})
        engine._validate_bundle_current = Mock()
        engine._validate_bundle_candidate = Mock()
        def apply(action, output, execution_id, *, owns_response=True, question_source_ref=None):
            for item in output["knowledge"]:
                if item["title"] == "invalid":
                    raise ValueError("rejected candidate")
                engine.instance["accepted_titles"].append(item["title"])
            if owns_response:
                engine.runtime["history"].append({"kind": "report"})
        engine._apply = apply
        for name in ("_apply_model_metadata", "_apply_extensions", "_apply_revision_followup",
                     "_apply_action_resolutions", "_apply_question_resolutions", "_resolve_failed_actions",
                     "_ensure_academic_followup", "_consume_action_events", "_record_task_receipt"):
            setattr(engine, name, Mock())
        engine._defer_review_for_research = Mock(return_value=False)
        output = {"summary": "two independent claims", "knowledge": [{"title": "valid"}, {"title": "invalid"}],
                  "relations": [], "questions": [], "integration_bundles": [
                      {"integration_id": "IN-good", "members": ["output", "output/knowledge/0"], "impact_set": [], "authority_refs": []},
                      {"integration_id": "IN-bad", "members": ["output/knowledge/1"], "impact_set": [], "authority_refs": []}]}
        action = {"id": "AC-work", "role": "research_work", "target": "TK-work"}
        context = {"action": action, "snapshot": engine.head}
        result = engine._apply_submission_bundles(action, output, {}, "EX-work", context, [])
        self.assertEqual(result["retry_bundle_ids"], ["IN-bad"])
        self.assertEqual(engine.instance["accepted_titles"], ["valid"])
        self.assertEqual(len(published), 1)
        engine._record_task_receipt.assert_not_called()
        self.assertIn("IN-good", published[0][1]["integrations"])
        result = engine._apply_submission_bundles(action, output, {}, "EX-work", context, [])
        self.assertEqual(result["bundles"][0]["status"], "already_accepted")
        self.assertEqual(engine.instance["accepted_titles"], ["valid"])
        self.assertEqual(len(published), 1)


class ExecutionConnections(unittest.TestCase):
    def test_retry_retains_activity_with_explicit_parent_and_profile(self):
        engine = routing_engine()
        engine.instance["config"] = deepcopy(DEFAULT_CONFIG)
        engine.instance.update(execution_profiles.build_profiles(engine.instance["config"]))
        engine._select_model = Mock(return_value={"model": DEFAULT_CONFIG["tier_models"]["medium"]})
        action = {"id": "AC-work", "role": "research_work", "lineage_id": "AC-work"}
        first = engine._register_execution(action, {"id": "EX-first", "role": "research_work",
            "status": "starting", "created_at": "2026-09-20T00:00:00+00:00", "input_manifest": []})
        first["status"] = "ended"
        first["outcome"] = "execution_incomplete"
        retry_action = {**action, "continuation_of": first["id"]}
        second = engine._register_execution(retry_action, {"id": "EX-second", "role": "research_work",
            "status": "starting", "created_at": "2026-09-20T00:01:00+00:00", "input_manifest": []})
        self.assertEqual(first["owner_activity_id"], second["owner_activity_id"])
        self.assertEqual(second["continuation_of"], first["id"])
        self.assertEqual(first["execution_profile_ref"], second["execution_profile_ref"])
        self.assertEqual(len(engine.runtime["activities"]), 1)
        self.assertEqual(activities.validate_activities(engine.runtime), [])

    def test_missing_explicit_continuation_does_not_infer_from_same_target(self):
        engine = routing_engine()
        engine.instance["config"] = deepcopy(DEFAULT_CONFIG)
        engine.instance.update(execution_profiles.build_profiles(engine.instance["config"]))
        action = {"id": "AC-machine", "role": "formal_check", "target": "KN-one"}
        from do_math.session_slots import SessionSlots
        engine._slots = SessionSlots(engine.runtime, engine.instance)
        engine.runtime["executions"]["EX-unrelated"] = {"id": "EX-unrelated", "role": "formal_check",
            "status": "ended", "action": {"target": "KN-one"}, "owner_activity_id": "AY-unrelated"}
        row = engine._register_execution(action, {"id": "EX-new", "role": "formal_check", "status": "running",
            "created_at": "2026-09-20T00:00:00+00:00", "input_manifest": []})
        self.assertIsNone(row["continuation_of"])
        self.assertNotEqual(row["owner_activity_id"], "AY-unrelated")
        self.assertNotIn("model", row)


class PersistedConnections(unittest.TestCase):
    def test_new_instance_is_v5_initializing_without_implicit_authority(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            subprocess.run(["git", "init", "--quiet", str(root / "repo")], check=True, capture_output=True)
            result = initialize(root / "repo", goal="Prove the stated goal", workspace=root / "work",
                config={"scholarly_enabled": False, "operator_enabled": False})
            head, instance, runtime = _repository(root / "repo", result["instance_id"]).load()
            self.assertEqual(runtime["status"], "initializing")
            self.assertEqual(runtime["queue"], [])
            self.assertEqual(instance["feature_version"], 5)
            self.assertEqual(instance["grants"], {})
            profile_id = next(iter(instance["execution_profiles"]))
            found = read_record(root / "repo", instance["id"], profile_id, snapshot=head)
            raw = _repository(root / "repo", instance["id"]).read(found["path"], head)
            self.assertEqual(found["sha256"], hashlib.sha256(raw).hexdigest())
            self.assertEqual(found["bytes"], len(raw))
            self.assertEqual(found["snapshot"], head)
            engine = ResearchEngine(root / "repo", instance["id"], runner=Mock())
            status = engine.run(max_steps=1)
            self.assertEqual(status["status"], "initializing")
            engine.runner.run.assert_not_called()


class InputManifestConnections(unittest.TestCase):
    def test_delivered_previous_hashes_pass_the_actual_live_impact_gate(self):
        from test_redesign_SURFACE import surface_state
        from research_fixtures import candidate
        from do_math import contracts, knowledge_io, knowledge
        engine = routing_engine(); engine.instance, engine.runtime = surface_state()
        engine.instance.update(relations=[], goal_status="unresolved")
        engine.runtime.update(inputs=[], questions=[])
        engine.instance, engine.runtime, kid = knowledge_io.import_candidate(engine.instance, engine.runtime,
            {"kind": "observation", "title": "Record", "statement": "A bounded observation", "summary": "Observed",
                "explanation": "Exact e\u0301 source", "lean_code": "", "declaration_names": [], "dependencies": []},
            source_ref="EX-author", actor_ref="EX-author")
        task = contracts.task_candidate_record(candidate("bounded work"), task_id="TA-one")
        task.update(status="candidate", results=[])
        engine.runtime["tasks"][task["id"]] = task
        engine.head = "fixed-input"; engine.store = Mock(); engine.store.read_many.return_value = {}
        engine._documents = {"maintenance": contracts.prompt_documents("maintenance")}
        engine._preparation_checkpoint = Mock(); engine._academic_status = Mock(return_value={"status": "not_evaluated"})
        with tempfile.TemporaryDirectory() as temporary:
            engine.instance["workspace"] = temporary
            context = engine._context({"id": "AC-reader", "role": "maintenance"}, Path(temporary) / "reader")
        rows = {row["id"]: row for field in ("knowledge_catalog", "tasks") for row in context[field]}
        for identifier, record in ((kid, engine.instance["knowledge"][kid]), (task["id"], task)):
            self.assertEqual(rows[identifier]["content_sha256"], knowledge.content_hash(record))
        engine.runtime["executions"]["EX-producer"] = {"id": "EX-producer", "input_snapshot": engine.head}
        bundle = {"integration_id": "IN-edit", "payload_sha256": "a" * 64, "members": ["activity-extensions.json/knowledge_changes/0"],
            "previous_hashes": {kid: rows[kid]["content_sha256"]}, "impact_set": [], "output": {},
            "extensions": {"knowledge_changes": [{"id": kid, "changes": {"summary": "Refined observation"}, "impact_set": []}]}}
        request = integration.bundle_impact_request(engine.instance, engine.runtime, bundle,
            producer_execution_id="EX-producer", input_snapshot=engine.head)
        self.assertIn("bundle", request["plans"])

    def test_input_artifacts_preserve_the_exact_role_manifest_and_catalog(self):
        from test_redesign_SURFACE import surface_state
        from do_math import contracts
        from do_math.context_store import prepare_role_input
        engine = routing_engine()
        engine.instance, engine.runtime = surface_state()
        profile = next(row for row in engine.instance["execution_profiles"].values() if row["role"] == "maintenance")
        engine._documents = {"maintenance": contracts.prompt_documents("maintenance")}
        schema = contracts.schema_for("maintenance")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            context = {"action": {"role": "maintenance"}, "execution_id": "EX-maintenance"}
            fitted = prepare_role_input(context, instance=engine.instance, runtime=engine.runtime,
                role="maintenance", profile=profile, snapshot="a" * 40, workspace=root,
                activity_id="AC-1", output_schema=schema, documents=engine._documents["maintenance"])
            artifacts = engine._input_artifacts("BA-input", "maintenance", fitted["prompt"], schema, fitted, root)
            self.assertEqual(json.loads(artifacts["runtime/artifacts/BA-input/manifest.json"]), fitted["manifest"])
            for entry in fitted["manifest"]["catalog"]:
                raw = artifacts["runtime/artifacts/BA-input/" + entry["path"]]
                self.assertEqual(hashlib.sha256(raw).hexdigest(), entry["sha256"])


class FormalAuthority(unittest.TestCase):
    def test_missing_preapproved_environment_never_runs_or_autoapproves(self):
        from do_math import knowledge_io
        engine = routing_engine()
        engine.instance.update(feature_version=5, active_trust_environment=None, trust_environments={}, sources=[])
        engine.instance["config"] = deepcopy(DEFAULT_CONFIG)
        engine.instance.update(execution_profiles.build_profiles(engine.instance["config"]))
        engine.instance, engine.runtime, kid = knowledge_io.import_candidate(engine.instance, engine.runtime,
            {"kind": "theorem", "title": "T", "statement": "True", "summary": "True", "explanation": "A proof",
             "lean_code": "theorem t : True := by trivial", "declaration_names": ["t"], "dependencies": []},
            source_ref="EX-author", actor_ref="EX-author")
        # This isolates the actual trust-environment gate; public lifecycle/grant
        # admission is exercised by PublicGitFlow and LIFECYCLE's owner tests.
        engine._action_lifecycle_gate = Mock()
        engine._require_action_clock = Mock()
        engine.runtime["trust_transitions"] = {}
        engine.formal_verifier = Mock()
        engine._save = Mock()
        engine._formal({"id": "AC-formal", "role": "formal_check", "target": kid})
        engine.formal_verifier.assert_not_called()
        self.assertIsNone(engine.instance["active_trust_environment"])
        self.assertEqual(next(iter(engine.runtime["activities"].values()))["status"], "waiting")


class FormalBindingConnections(unittest.TestCase):
    def run_verifier(self, result):
        from do_math import knowledge_io
        engine = routing_engine()
        directory = tempfile.TemporaryDirectory(); self.addCleanup(directory.cleanup)
        config = {**deepcopy(DEFAULT_CONFIG), "lean_command": [sys.executable], }
        environment = {"id": "TE-one", "status": "active", "toolchain": {"configured_command": [sys.executable], "sha256": "a" * 64}, "allowed_axioms": []}
        engine.instance.update(feature_version=5, workspace=directory.name, sources=[], config=config,
            active_trust_environment="TE-one", trust_environments={"TE-one": environment})
        engine.instance.update(execution_profiles.build_profiles(config))
        engine.instance["config"] = {**config, "lean_command": ["unapproved-config-command"], }
        engine.instance, engine.runtime, kid = knowledge_io.import_candidate(engine.instance, engine.runtime,
            {"kind": "theorem", "title": "T", "statement": "True", "summary": "True", "explanation": "A proof",
                "lean_code": "-- e\u0301\r\ntheorem t : True := by trivial", "declaration_names": ["t"], "dependencies": []}, source_ref="EX-author", actor_ref="EX-author")
        engine.head = "fixed-input"; engine._save = Mock(); engine._controls = Mock()
        engine._check_conversations = Mock(return_value=False)
        engine._action_lifecycle_gate = Mock(); engine._formal_environment = Mock(return_value=deepcopy(environment))
        engine.formal_verifier = Mock(return_value=result)
        with patch("do_math.engine.governance.authorize", return_value={"allowed": True, "grant_id": "GR-one"}):
            engine._formal({"id": "AC-formal", "role": "formal_check", "target": kid})
        return engine, environment

    def test_verifier_uses_the_fixed_environment_command_and_fingerprint(self):
        engine, environment = self.run_verifier({"status": "failed", "reason": "compiler double, no proof claim"})
        kwargs = engine.formal_verifier.call_args.kwargs
        self.assertEqual(kwargs["lean_command"], [sys.executable])
        self.assertNotIn("timeout_seconds", kwargs)
        self.assertEqual(kwargs["expected_toolchain"], environment["toolchain"])
        self.assertEqual(kwargs["allowed_axioms"], ())
        self.assertEqual(next(e for e in engine.runtime["executions"].values() if e.get("role") == "formal_check")["outcome"], "execution_incomplete")

    def test_exact_compiler_keys_and_source_survive_result_artifacts(self):
        result = {"status": "failed", "reason": "compiler double retains exact names", "axioms": {"K": [], "K": []}}
        engine, _ = self.run_verifier(result)
        artifacts = {path: raw for call in engine._save.call_args_list if call.args for path, raw in call.args[0].items()}
        raw = next(raw for path, raw in artifacts.items() if path.endswith("formal.json"))
        self.assertEqual(json.loads(raw), result)
        source = next(raw for path, raw in artifacts.items() if path.endswith("proposal.lean"))
        self.assertEqual(source, engine.formal_verifier.call_args.kwargs["source"].encode("utf-8"))
        self.assertIn("e\u0301\r\n".encode("utf-8"), source)

    def test_publication_signature_distinguishes_exact_unicode_payload(self):
        engine = routing_engine(); engine.head = "snapshot"
        engine.instance["formal_results"] = {"FR-one": {"lean_code": '-- "e\u0301"'}}
        before = engine._state_signature()
        engine.instance["formal_results"]["FR-one"]["lean_code"] = '-- "é"'
        self.assertNotEqual(before, engine._state_signature())


class ControlReceipts(unittest.TestCase):
    def make_engine(self):
        engine = routing_engine()
        engine.head = "parent"
        engine.runtime.update(events=[], pending_events=[])
        temporary = tempfile.TemporaryDirectory(); self.addCleanup(temporary.cleanup)
        engine.instance["workspace"] = temporary.name
        engine.instance["config"]["max_artifact_bytes"] = 1024 * 1024
        (Path(temporary.name) / "runs/EX-work/workspace/.control").mkdir(parents=True)
        engine.store = Mock()
        engine.store.read.side_effect = [canonical_json({}), canonical_json({})]
        engine.instance["grants"] = {"GR-one": {"id": "GR-one", "kind": "local", "status": "active",
            "roles": ["research_work"], "task_ids": [], "expires_at": None}}
        engine.runtime["executions"]["EX-work"] = {"id": "EX-work", "role": "research_work", "status": "running",
            "grant_id": "GR-one", "action": {"role": "research_work"}, "input_bundle": "BA-input"}
        engine._clock_guard = Mock(return_value={"usable": True, "observed_utc": "2026-09-22T00:00:00Z"})
        engine._save = Mock(side_effect=lambda *a: setattr(engine, "head", "published"))
        request = {"request_id": "request-one", "transport_id": "local", "capability": "delivery-only",
            "execution_id": "EX-work", "grant_id": "GR-one", "kind": "submit_intent",
            "payload": {"draft_path": "draft.json"}}
        return engine, request

    @staticmethod
    def sealed():
        return {"passed": True, "capture_eligible": True, "check": {"issues": []}, "manifest": [],
            "intent": {"candidate_id": "CS-one", "draft_path": "draft.json",
                       "output_sha256": "a" * 64, "extensions_sha256": "b" * 64,
                       "schema_ref": {}, "manifest": []},
            "artifacts": {"output.json": b"{}", "extensions.json": b"{}",
                          "check.json": b"{}", "manifest.json": b"[]"}}

    def test_receipt_requires_successful_cas_and_replay_does_not_reapply(self):
        engine, request = self.make_engine()
        with patch("do_math.engine.submission.seal_submission", return_value=self.sealed()):
            receipt = engine._publish_control_request(request)
        self.assertEqual(receipt["snapshot"], "published")
        self.assertEqual(receipt["state"], "accepted")
        self.assertEqual(engine.runtime["executions"]["EX-work"]["status"], "stopping")
        self.assertEqual(engine.runtime["executions"]["EX-work"]["stop_phase"], "terminating")
        self.assertNotIn("outcome", engine.runtime["executions"]["EX-work"])
        stored = next(iter(engine.runtime["control_receipts"].values()))
        self.assertNotIn("capability", stored["request"])
        engine.store.read.side_effect = [canonical_json({}), canonical_json({})]
        with patch("do_math.engine.submission.seal_submission", return_value=self.sealed()):
            engine._publish_control_request(request)
        self.assertEqual(engine._save.call_count, 1)

    def test_preview_control_is_nonpublishing_and_returns_sanitized_result(self):
        engine, request = self.make_engine()
        request["kind"] = "submission_preview"
        result = {"contract_id": "do-math-candidate-preview/5", "passed": True, "authoritative": False}
        engine._preview_submission = Mock(return_value=result)
        before = deepcopy((engine.instance, engine.runtime))
        receipt = engine._publish_control_request(request)
        self.assertEqual(receipt, {"state": "previewed", "result": result})
        engine._save.assert_not_called()
        self.assertEqual((engine.instance, engine.runtime), before)

    def test_safety_boundary_updates_obligation_only_after_publication(self):
        from do_math.observations import ObservationTracker
        from test_redesign_OBSERVATION import Clock, rule
        engine, request = self.make_engine()
        with tempfile.TemporaryDirectory() as temporary:
            engine.instance["workspace"] = temporary
            (Path(temporary)/"runs/EX-work/workspace/.control").mkdir(parents=True)
            clock = Clock()
            tracker = ObservationTracker("EX-work", Path(temporary), {"observation_rules": [rule()],
                "tool_review_window_seconds": 60, "self_check_response_window_seconds": 5}, clock=clock)
            tracker.observe({"type": "item.started", "item": {"id": "C", "type": "command_execution"}})
            obligation = next(row for row in tracker.observe({"type": "tick", "counters": {"attempts": 2}})
                              if row["kind"] == "self_check_due")
            engine._trackers = {"EX-work": tracker}
            engine._transport = Mock(); engine._transport_bindings = {"EX-work": {}}
            request.update(kind="safety_boundary", payload={"inflight_calls": False, "call_ids": ["C"]})
            uncovered = {**deepcopy(request), "request_id": "uncovered", "payload": {"inflight_calls": False, "call_ids": []}}
            self.assertEqual(engine._publish_control_request(uncovered)["state"], "rejected")
            engine._save.side_effect = ValueError("CAS failed")
            self.assertEqual(engine._publish_control_request(request)["state"], "rejected")
            self.assertIsNone(tracker.obligations[obligation["id"]]["deadline_offset_ms"])
            engine._save.side_effect = lambda *a: setattr(engine, "head", "published")
            self.assertEqual(engine._publish_control_request(request)["state"], "accepted")
            self.assertEqual(tracker.obligations[obligation["id"]]["deadline_offset_ms"], 5000)
            self.assertEqual(engine.runtime["self_check_obligations"][obligation["id"]]["deadline_offset_ms"], 5000)

    def test_rejected_self_check_is_preserved_but_not_acknowledged_as_accepted(self):
        from do_math.observations import ObservationTracker
        from test_redesign_OBSERVATION import Clock, rule, ObservationRedesignTests
        engine, request = self.make_engine()
        with tempfile.TemporaryDirectory() as temporary:
            engine.instance["workspace"] = temporary
            (Path(temporary)/"runs/EX-work/workspace/.control").mkdir(parents=True)
            tracker = ObservationTracker("EX-work", Path(temporary), {"observation_rules": [rule()],
                "tool_review_window_seconds": 60, "self_check_response_window_seconds": 5}, clock=Clock())
            obligation = next(row for row in tracker.observe({"type": "tick", "counters": {"attempts": 2}})
                              if row["kind"] == "self_check_due")
            engine._trackers = {"EX-work": tracker}
            engine._available_inputs = Mock(return_value=[])
            engine._control_evidence_refs = Mock(return_value=set())
            response = ObservationRedesignTests.response(obligation)
            request.update(kind="self_check_response", payload={"self_check_id": obligation["id"], "response": response})
            receipt = engine._publish_control_request(request)
            self.assertEqual(receipt["state"], "rejected")
            self.assertTrue(engine.runtime["self_check_responses"])
            self.assertEqual(len(engine.runtime["queue"]), 1)
            self.assertTrue((Path(temporary)/"runs/EX-work/workspace/.control/observation-feedback.json").is_file())

    def test_failed_cas_does_not_acknowledge_submission(self):
        engine, request = self.make_engine()
        engine._save.side_effect = ValueError("CAS failed")
        with patch("do_math.engine.submission.seal_submission", return_value=self.sealed()):
            receipt = engine._publish_control_request(request)
        self.assertEqual(receipt["state"], "rejected")
        self.assertNotIn("submission_receipt", engine.runtime["executions"]["EX-work"])


class CentralSubmissionEvidence(unittest.TestCase):
    def fixture(self, root):
        engine = routing_engine()
        engine.instance['config']['max_output_repairs'] = 1
        output = {"summary": "preserved exact draft"}
        raw = json.dumps(output, indent=4).encode()
        from do_math import submission, contracts
        context = {"execution_id": "EX-work", "action": {"id": "AC-work", "role": "maintenance"}, "kind_definitions": {},
                   "knowledge_catalog": [], "tasks": []}
        schema = contracts.identify_schema({"type": "object", "properties": {"summary": {"type": "string"}}, "required": ["summary"]})
        submission.install_tools(root, context, schema, 10000000)
        (root / "draft.json").write_bytes(raw)
        engine._response_schema = Mock(return_value=schema)
        execution = {"id": "EX-work", "action": context["action"], "status": "stopping",
                     "stop_phase": "terminating"}
        return engine, output, context, execution

    def test_unsealed_runner_output_is_preserved_but_cannot_be_integrated(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            engine, output, context, execution = self.fixture(root)
            engine.runtime["executions"]["EX-work"] = execution
            engine._apply_submission_bundles = Mock(return_value={"status": "returned", "bundles": [],
                "issues": [], "retry_bundle_ids": []})
            engine._remove_action = Mock()
            engine._record_task_receipt = Mock()
            engine._save = Mock()
            result = engine._receive_submission(context["action"], {"output": output}, "EX-work",
                context, engine._response_schema(context["action"]), root)
            self.assertEqual(result["status"], "returned")
            issues = engine._apply_submission_bundles.call_args.args[-1]
            self.assertTrue(any(issue["rule_id"] == "submission.sealed_candidate" for issue in issues))
            saved = engine._save.call_args.args[0]
            self.assertTrue(any(path.endswith("/output.json") for path in saved))

    def test_retry_receives_prior_accepted_response_across_multiple_attempts(self):
        engine = routing_engine()
        engine.runtime["executions"].update({"EX-one": {"action": {}},
            "EX-two": {"action": {"continuation_of": "EX-one"}}})
        receipt = {"id": "IN-report", "execution_id": "EX-one", "response_sha256": "a" * 64}
        engine.runtime["integrations"] = {receipt["id"]: receipt}
        issue = integration.issue("integration.candidate", "output", "repair this")
        context = {}
        engine._submission_repair_context(context, {"continuation_of": "EX-two", "repair": {"issues": [issue]}})
        self.assertEqual(context["accepted_response"], {"integration_id": "IN-report", "response_sha256": "a" * 64})
        self.assertEqual(context["submission_failures"], [issue])
        self.assertEqual(context["accepted_integration_ids"], ["IN-report"])


class UserControlIdentity(unittest.TestCase):
    def test_same_request_replays_before_changed_state_admission(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            engine = routing_engine()
            engine.instance["workspace"] = str(root / "work")
            store = Mock()
            store.load.return_value = ("snapshot", engine.instance, engine.runtime)
            with patch("do_math.engine._repository", return_value=store), patch("do_math.engine._require_current_contract"):
                first = control(root, "RI-test", "request", config={"role": "maintenance"}, request_id="UC-explicit")
                engine.runtime["status"] = "closed"
                replay = control(root, "RI-test", "request", config={"role": "maintenance"}, request_id="UC-explicit")
                self.assertEqual(first["request_id"], replay["request_id"])
                self.assertTrue(replay["replayed"])
                self.assertEqual(len(list((root / "work/control/RI-test").glob("*.json"))), 1)
                with self.assertRaisesRegex(ValueError, "different"):
                    control(root, "RI-test", "request", config={"role": "maintenance"}, text="changed", request_id="UC-explicit")


    def test_git_replay_keeps_original_outcome_and_snapshot_after_close(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            subprocess.run(["git", "init", "-q", str(root / "repo")], check=True)
            created = initialize(root / "repo", goal="Control replay", workspace=root / "work")
            identifier = created["instance_id"]
            first = control(root / "repo", identifier, "pause", text="pause once")
            engine = ResearchEngine(root / "repo", identifier)
            engine.process_controls()
            original = engine.control_result(first["request_id"])
            self.assertEqual(original["status"], "paused")
            control(root / "repo", identifier, "close")
            engine.process_controls()
            self.assertEqual(engine.runtime["status"], "closed")
            replay = control(root / "repo", identifier, "pause", text="pause once")
            self.assertTrue(replay["replayed"])
            self.assertEqual({key: replay[key] for key in original}, original)
            self.assertNotEqual(engine.head, original["snapshot"])
            from do_math.cli import control_request_id
            self.assertEqual(first["request_id"], control_request_id(identifier, "pause", text="pause once"))

    def test_normalized_source_has_one_identity_and_rejects_wrong_bytes(self):
        from do_math.cli import control_request_id
        import base64
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            engine = routing_engine(); engine.instance["workspace"] = str(root / "work")
            store = Mock(); store.load.return_value = ("snapshot", engine.instance, engine.runtime)
            spec = {"name": "source.txt", "body_base64": base64.b64encode(b"original").decode(),
                    "sha256": hashlib.sha256(b"original").hexdigest(), "bytes": 8}
            with patch("do_math.engine._repository", return_value=store), patch("do_math.engine._require_current_contract"):
                result = control(root, "RI-test", "source", config=spec, idempotency_key="source-once")
                self.assertEqual(result["request_id"], control_request_id("RI-test", "source", config=spec, idempotency_key="source-once"))
                with self.assertRaisesRegex(ValueError, "hash or size"):
                    control(root, "RI-test", "source", config={**spec, "bytes": 7})


class PublicGitFlow(unittest.TestCase):
    def test_public_activation_work_receipt_assessment_and_next_plan(self):
        from research_fixtures import activate, install_adapter_fixture, candidate, contract_review, intent_response, assessment, seal_response, local_job_runner
        from do_math import submission, task_contracts
        from do_math.control_transport import ControlTransport
        install_adapter_fixture(self)
        class Runner:
            def __init__(self): self.roles = []
            @local_job_runner
            def run(runner, **arguments):
                try:
                    return runner.execute(**arguments)
                except Exception:
                    import traceback
                    traceback.print_exc(file=sys.stdout)
                    raise
            def execute(runner, **arguments):
                workspace = arguments["workspace"]
                context = json.loads((workspace / "input/submission/context.json").read_bytes())
                role = context["action"]["role"]; runner.roles.append(role)
                print("ENGINE public Git producer:", role, context["action"].get("stage"), arguments["execution_id"], flush=True)
                if context.get("submission_failures"):
                    print("ENGINE public Git prior receiver issues:", json.dumps(context["submission_failures"], ensure_ascii=False), flush=True)
                arguments["on_started"]()
                output = {"summary": role, "used_sources": [], "questions": []}
                if role == "intent_interpretation":
                    output = intent_response(context)
                elif role == "research_preparation":
                    row = candidate("bounded observation")
                    row["profile_refs"] = [execution_profiles.profile_ref(p) for p in context["execution_profiles"] if p["role"] == "research_work"]
                    row["authority_refs"] = ["GR-research-fixture"]
                    output["candidates"] = [row] if not context["tasks"] else []
                    if "observed_at" in arguments["output_schema"]["properties"]:
                        output["observed_at"] = context["observed_at"]
                    if output["candidates"]:
                        rules = [{"id": "rule-attempt", "operator": "counter_gte", "subject": {"kind": "counter", "id": "attempts"},
                            "basis": {"source": "checkpoint", "unit": "count"}, "threshold": 10, "required_evidence": ["checkpoint.json"]}]
                        (workspace / "activity-extensions.json").write_bytes(canonical_json({
                            "task_conditions": [{"task_title": row["title"], "occurrence_condition": {"op": "always"},
                                "dependencies": [], "knowledge_revision_targets": [], "observation_rules": rules}],
                            "model_assessments": [{"task_title": row["title"], "difficulty": "low",
                                "importance": "low", "reason": "Bounded synthetic task"}],
                        }))
                elif role == "task_contract_review":
                    output.update(contract_review(context))
                elif role == "research_plan":
                    tasks = {t["id"]: t for t in context["tasks"]}
                    output.update(dispositions=[{"task_id": tid, "kind": "selected", "reason": "Perform approved bounded work",
                        "uncertainty": "Outcome is unconfirmed before execution", "parallel_task_ids": [],
                        "expected_research_change": "Preserve an explicit observation", "revisit": {"at": None, "event_refs": []},
                        "missing_inputs": [], "next_owner": "research_work"} for tid in context["ready_task_ids"]],
                        task_assessments=[assessment(tasks[tid]) for tid in task_contracts.returned_task_ids(tasks)],
                        preparation_requests=[], goal_audit=False)
                elif role == "research_work":
                    output.update(outcome="submitted", report="The observation is bounded to this synthetic execution and its stated domain.",
                        checkpoint="Observation preserved", remaining_work=[], relations=[], knowledge=[{
                            "kind": "observation", "title": "Bounded observation", "statement": "The synthetic runner returned an observation.",
                            "explanation": "Evidence is this explicit synthetic execution", "summary": "A bounded observation",
                            "lean_code": "", "declaration_names": [], "dependencies": []}])
                else:
                    raise AssertionError("Unexpected role in minimum actual Git flow: " + role)
                seal_response(output, context, workspace)
                draft = workspace / "draft.json"; draft.write_bytes(canonical_json(output))
                self.assertEqual(context["control_binding"], arguments["control_binding"])
                # Queue through the real transport, let the engine's stop probe pump
                # the request, then read the durable receipt without a fixture sleep.
                delivery = submission.request_control(workspace, "draft.json", kind="submit_intent", wait_seconds=0)
                self.assertIn(delivery["state"], {"submitted", "already_received"}, delivery)
                arguments["should_stop"]()
                receipt = ControlTransport.worker_receipt(arguments["control_binding"], delivery["request_id"])
                self.assertEqual(receipt["state"], "accepted", receipt)
                return {"status": "completed", "output": output, "usage": {}}
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            subprocess.run(["git", "init", "--quiet", str(root / "repo")], check=True, capture_output=True)
            created = initialize(root / "repo", goal="Record and assess a bounded observation", workspace=root / "work", config={
                 "scholarly_enabled": False, "operator_enabled": False, "lean_command": ["fixture-lean"],
                "observation_mode": "periodic", "tool_review_window_seconds": 600, "self_check_response_window_seconds": 60,
                "import_rework_limit": 3, "selection_failure_limit": 3, "exhaustion_empty_limit": 3,
                "proposal_version_limit": 3, "contract_revision_limit": 3})
            runner = Runner(); engine = ResearchEngine(root / "repo", created["instance_id"], runner=runner)
            run = engine.run
            def checked_run(**kwargs):
                result = run(**kwargs)
                failures = [{key: execution.get(key) for key in ("id", "role", "outcome", "error")}
                    for execution in engine.runtime["executions"].values()
                    if execution["status"] == "ended" and execution.get("outcome") != "output_accepted"]
                self.assertEqual(failures, [], {"failures": failures, "repair_issues": [
                    action.get("repair", {}).get("issues", []) for action in engine.runtime["queue"]]})
                return result
            engine.run = checked_run
            activate(engine, root, initialization_runner=runner)
            self.assertEqual(engine.instance["lifecycle"]["state"], "active")
            for _ in range(15):
                engine.run(max_steps=1)
                if any(t.get("status") == "completed" for t in engine.runtime["tasks"].values()): break
            else: self.fail("Public flow did not assess returned work: " + repr(engine.runtime["history"][-5:]))
            task = next(t for t in engine.runtime["tasks"].values() if t["status"] == "completed")
            self.assertEqual(task["assessment"]["item_dispositions"][0]["kind"], "fulfilled")
            self.assertTrue(engine.instance["knowledge"])
            self.assertGreaterEqual(runner.roles.count("research_plan"), 2)
            self.assertEqual(runner.roles.count("research_work"), 1)
            _, instance, runtime = engine.store.load()
            self.assertEqual(runtime["tasks"][task["id"]]["status"], "completed")
            self.assertTrue(runtime["integrations"])


class ControlQueueConnections(unittest.TestCase):
    def engine(self, request):
        engine = routing_engine(); engine.head = "parent"; engine._calls = None
        engine.instance.update(config={**deepcopy(DEFAULT_CONFIG), }, lifecycle={"state": "active"})
        engine.runtime["processed_controls"] = []
        engine._inbox = Mock(return_value=[request]); engine._save = Mock(); engine._resume_lifecycle = Mock()
        for name in ("_review_recovery_control", "_knowledge_io_control", "_academic_control", "_apply_extended_control"):
            setattr(engine, name, Mock(return_value=False))
        for name in ("_schedule_operational_reviews", "_retry_submission_publications", "_retry_impact_reviews", "_run_pending_operational_repairs"):
            setattr(engine, name, Mock())
        return engine

    def test_every_call_budget_control_produces_stable_queue_identity(self):
        for action, config in (("input", {}), ("request", {"role": "maintenance"}), ("resume", {})):
            with self.subTest(action=action):
                engine = self.engine({"id": "UC-one", "action": action, "config": config, "text": "Explicit request"})
                engine._controls()
                self.assertEqual(len(engine.runtime["queue"]), 1)
                queued = engine.runtime["queue"][0]
                self.assertTrue(queued.get("id", "").startswith("AC-"), queued)
                self.assertEqual(queued["id"], queued["lineage_id"])

    def test_distinct_approved_cleanup_scopes_are_not_merged(self):
        engine = routing_engine()
        engine._enqueue("maintenance", requested_by="UC-one", cleanup_execution_ids=["EX-one"])
        engine._enqueue("maintenance", requested_by="UC-two", cleanup_execution_ids=["EX-two"])
        self.assertEqual(len(engine.runtime["queue"]), 2)
        self.assertEqual([row["cleanup_execution_ids"] for row in engine.runtime["queue"]], [["EX-one"], ["EX-two"]])


class GovernanceOwnerConnections(unittest.TestCase):
    def test_control_applies_actual_checked_import_and_records_one_public_result(self):
        from test_governance_engine import CentralGovernanceTests
        host, bundle, request = CentralGovernanceTests().host()
        engine = routing_engine(); engine.instance, engine.runtime = host.instance, host.runtime
        engine.runtime.update(status="ready", history=[], processed_controls=[])
        for execution in engine.runtime["executions"].values():
            execution.setdefault("status", "ended")
        engine.head = "fixed-parent"; engine._calls = None
        engine._inbox = Mock(return_value=[request]); engine._save = Mock()
        for name in ("_review_recovery_control", "_knowledge_io_control", "_academic_control", "_apply_extended_control"):
            setattr(engine, name, Mock(return_value=False))
        for name in ("_schedule_operational_reviews", "_retry_submission_publications", "_retry_impact_reviews", "_run_pending_operational_repairs"):
            setattr(engine, name, Mock())
        engine._controls()
        self.assertEqual(engine.instance["governance"]["CH2"]["content"]["goal"], "Prove Q")
        self.assertEqual(engine.runtime["intent_imports"][bundle["id"]]["application"]["status"], "applied")
        self.assertEqual(len([h for h in engine.runtime["history"] if h.get("kind") == "user_control"]), 1)
        engine._save.assert_called_once()
        engine._apply_extended_control.assert_not_called()


class MachineAdmissionConnections(unittest.TestCase):
    def fixture(self):
        from test_host_resources import fixture
        from do_math.session_slots import SessionSlots
        instance, selected, _ = fixture()
        engine = routing_engine(); engine.instance.update(instance)
        engine._execution_profile = Mock(return_value=selected["formal_check"])
        engine._slots = SessionSlots(engine.runtime, engine.instance)
        engine._admit_review_execution = Mock(return_value={"disposition": "not_applicable"})
        engine._save = Mock()
        return engine

    def test_common_machine_admission_reserves_before_start_and_refuses_without_execution(self):
        engine = self.fixture()
        for index in range(3):
            action = {"id": f"AC-machine-{index}", "role": "formal_check", "target": "KN-one"}
            execution = engine._register_execution(action, {"id": f"EX-machine-{index}", "status": "running", "role": "formal_check"})
            self.assertEqual(execution["status"], "starting")
            self.assertEqual(len(execution["capacity"]["reservation_ids"]), 3)
            self.assertIsNone(execution["capacity"]["provider"])
        action = {"id": "AC-refused", "role": "formal_check", "target": "KN-one"}
        engine.runtime["queue"].append(action)
        self.assertIsNone(engine._register_execution(action, {"id": "EX-refused", "status": "running", "role": "formal_check"}))
        self.assertNotIn("EX-refused", engine.runtime["executions"])
        self.assertEqual(engine.runtime["activities"][action["owner_activity_id"]]["status"], "waiting")
        self.assertEqual(len(engine.runtime["reservations"]), 9)
        self.assertTrue(engine._slots.release("EX-machine-0", reason="test never resumed"))
        retry = engine._register_execution(action, {"id": "EX-retry", "status": "running", "role": "formal_check"})
        self.assertEqual(retry["status"], "starting")

    def test_machine_callback_seals_process_before_resume_and_keeps_uncertain_capacity(self):
        engine = self.fixture()
        execution = engine._register_execution({"id": "AC-one", "role": "formal_check"},
            {"id": "EX-one", "status": "running", "role": "formal_check"})
        identity = {"job_name": "synthetic-machine-job", "pid": 17, "creation_filetime": "12345"}
        def published():
            self.assertEqual(execution["capacity"]["process"], identity)
            self.assertEqual(execution["status"], "running")
        engine._save.side_effect = published
        engine._machine_started("EX-one", identity)
        engine._save.assert_called_once()
        with patch("do_math.windows_job.named_job_empty", return_value=False):
            self.assertFalse(engine._release_call_slot("EX-one"))
        self.assertTrue(all(row["state"] != "settled" for row in engine.runtime["reservations"].values()))

    def test_actual_git_snapshot_binds_machine_reservations_and_start_identity(self):
        from do_math.repository import ResearchRepository, new_id
        from do_math.session_slots import SessionSlots
        from test_host_resources import fixture
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            subprocess.run(["git", "init", "--quiet", str(root / "repo")], check=True, capture_output=True)
            instance, profiles, _ = fixture()
            engine = routing_engine()
            engine.instance = {**instance, "id": new_id("RI"), "feature_version": 5, "workspace": str(root / "work")}
            engine.runtime = {"feature_version": 5, "executions": {}, "activities": {}, "tasks": {}, "queue": [], "history": []}
            engine.instance["role_profile_refs"]["formal_check"] = [execution_profiles.profile_ref(profiles["formal_check"])]
            engine.store = ResearchRepository(root / "repo", engine.instance["id"])
            engine.head = engine.store.initialize(engine.instance, engine.runtime)
            def save(artifacts=None):
                engine.head = engine.store.save_with_state(engine.head, engine.instance, engine.runtime, artifacts=artifacts)[0]
                engine.head, engine.instance, engine.runtime = engine.store.load(engine.head)
            engine._save = save
            engine._slots = SessionSlots(engine.runtime, engine.instance)
            with engine.store.writer_lock():
                engine._register_execution({"id": "AC-machine", "role": "formal_check"},
                    {"id": "EX-machine", "role": "formal_check", "status": "running"})
                engine._save()
                admitted = engine.head
                _, _, staged = engine.store.load(admitted)
                self.assertEqual(staged["executions"]["EX-machine"]["status"], "starting")
                self.assertEqual(len(staged["reservations"]), 3)
                # The Job identity is a double; both pre-resume publications and
                # the host reservation records use actual schema and Git CAS.
                identity = {"job_name": "ENGINE-fixture-machine", "pid": 29, "creation_filetime": "123456789012345678"}
                engine._machine_started("EX-machine", identity)
                _, _, started = engine.store.load(engine.head)
                self.assertNotEqual(engine.head, admitted)
                self.assertEqual(started["executions"]["EX-machine"]["capacity"]["process"], identity)
                self.assertEqual(started["executions"]["EX-machine"]["status"], "running")


class MaintenanceConnections(unittest.TestCase):
    def test_maintenance_archives_complete_run_before_approved_cleanup(self):
        from do_math import execution_lifecycle, governance
        from do_math.repository import ResearchRepository, new_id
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            subprocess.run(["git", "init", "--quiet", str(root / "repo")], check=True, capture_output=True)
            engine = routing_engine(); identifier = new_id("RI")
            engine.instance = {"id": identifier, "feature_version": 5, "workspace": str(root / "work"),
                               **execution_profiles.build_profiles(DEFAULT_CONFIG)}
            engine.runtime = {"feature_version": 5, "executions": {}, "activities": {}, "history": [], "queue": []}
            engine.instance["governance_sources"] = {"SOURCE-cleanup": governance.preserve_source(
                "SOURCE-cleanup", "Authorize local maintenance and cleanup of the requested ended run.", origin="user")}
            engine.instance, engine.runtime, _ = governance.apply_decision(engine.instance, engine.runtime,
                {"kind": "grant", "decision_id": "DEC-cleanup", "grant": {"id": "GR-cleanup", "kind": "local",
                    "roles": ["maintenance"], "reuse": "reusable", "budget_kind": "operations"}}, source_ref="SOURCE-cleanup")
            action = {"id": "AC-cleanup", "role": "maintenance", "budget_kind": "operations", "actor_kind": "ai",
                      "grant_id": "GR-cleanup", "requested_by": "UC-cleanup", "cleanup_execution_ids": ["EX-finished"]}
            engine.runtime["history"].append({"kind": "user_control", "request": {"id": "UC-cleanup", "origin": "user",
                "action": "request", "config": {"role": "maintenance", "cleanup_execution_ids": ["EX-finished"]}}})
            profile = next(p for p in engine.instance["execution_profiles"].values() if p["role"] == "maintenance")
            for eid in ("EX-finished", "EX-maintenance"):
                aid = "AY-" + eid
                activities.open_activity(engine.runtime, activity_id=aid, activity_kind="maintenance", owner_ref="GR-cleanup", input_refs=[], opened_at="2026-09-20T00:00:00Z")
                execution = execution_lifecycle.create_execution(execution_id=eid, owner_activity_id=aid, actor_kind="ai",
                    input_manifest={}, profile_ref=execution_profiles.profile_ref(profile), created_at="2026-09-20T00:00:00Z")
                execution.update(role="maintenance", action=deepcopy(action), grant_id="GR-cleanup")
                activities.assign_execution(engine.runtime, aid, execution)
                execution_lifecycle.transition_execution(execution, "ended", at="2026-09-20T00:00:01Z", outcome="cancelled")
                # Explicit synthetic termination evidence; all scope, schemas, references and Git I/O are real.
                execution["capacity"] = {"local_termination": "confirmed"}
                activities.finish_activity(engine.runtime, aid, result_refs=[], unresolved=[], followups=[], at="2026-09-20T00:00:01Z")
            engine.store = ResearchRepository(root / "repo", identifier)
            engine.head = engine.store.initialize(engine.instance, engine.runtime)
            def save(artifacts=None):
                engine.head = engine.store.save_with_state(engine.head, engine.instance, engine.runtime, artifacts=artifacts)[0]
                engine.head, engine.instance, engine.runtime = engine.store.load(engine.head)
            engine._save = save
            run = root / "work/runs/EX-finished"
            (run / "workspace").mkdir(parents=True); (run / "evidence").mkdir()
            (run / "workspace/draft.txt").write_bytes(b"draft retained")
            (run / "evidence/runner.json").write_bytes(b'{"local_job_empty":true}')
            with engine.store.writer_lock():
                before = engine.head
                with self.assertRaisesRegex(ValueError, "exact user-approved"):
                    engine._maintenance_cleanup({**action, "cleanup_execution_ids": ["EX-maintenance"]}, "EX-maintenance")
                self.assertEqual(engine.head, before)
                self.assertTrue(run.exists())
                result = engine._maintenance_cleanup(action, "EX-maintenance")
            self.assertEqual(result["deleted"], ["runs/EX-finished"],
                {"result": result, "candidates": engine.runtime["history"][-1]["candidates"]})
            self.assertFalse(run.exists())
            manifest = engine.runtime["executions"]["EX-finished"]["collection"]["retention_manifest"]
            self.assertEqual(len(manifest), 2)
            for row in manifest:
                raw = engine.store.read(row["artifact_ref"], row["snapshot"])
                self.assertEqual(hashlib.sha256(raw).hexdigest(), row["sha256"])


class KindSemanticConnections(unittest.TestCase):
    def test_proposed_kind_is_checked_by_a_separate_execution_before_activation(self):
        engine = routing_engine()
        engine.instance.update(feature_version=5, sources=[], kind_definitions={})
        definition = {"family": "knowledge", "token": "method_note", "meaning": "A nonmathematical method observation",
                      "constraints": {"mathematical_claim": False}}
        engine.runtime["executions"]["EX-author"] = {"id": "EX-author", "status": "ended", "role": "research_work",
            "action": {"role": "research_work"}, "extensions": {"kind_definitions": [definition]}}
        engine._apply_queue_plan = Mock(); engine._apply_academic_resolutions = Mock()
        engine._apply_extensions({"role": "research_work"}, "EX-author")
        definition = next(row for row in engine.instance["kind_definitions"].values() if row["token"] == "method_note")
        checks = [a for a in engine.runtime["queue"] if a.get("kind_definition_id") == definition["id"]]
        self.assertEqual(len(checks), 1)
        self.assertEqual(definition["status"], "candidate")
        action = checks[0]
        output = {"summary": "Independent semantic comparison", "used_sources": [], "questions": [],
                  "report": "Meaning and constraints agree", "remaining_work": [],
                  "kind_definition_check": {"definition_id": definition["id"], "definition_sha256": action["kind_definition_sha256"],
                                            "decision": "approved", "findings": []}}
        engine.runtime["executions"]["EX-check"] = {"id": "EX-check", "role": "maintenance", "status": "running",
            "input_basis": {"kind_definition": {"id": definition["id"], "sha256": action["kind_definition_sha256"]}}}
        with self.assertRaisesRegex(ValueError, "independent|author"):
            engine._apply(action, output, "EX-author")
        engine._apply(action, output, "EX-check")
        checked = engine.instance["kind_definitions"][definition["id"]]
        self.assertEqual(checked["status"], "active")
        self.assertEqual(checked["checked_by"], "EX-check")
        self.assertEqual(checked["check"]["decision"], "approved")
        self.assertEqual(engine.runtime["pending_kind_checks"], [])


class EvaluationConnections(unittest.TestCase):
    def test_declared_observation_and_repetition_values_can_be_adopted(self):
        from do_math.engine import validate_config
        validate_config({"tool_review_window_seconds": 20, "self_check_response_window_seconds": 30,
                         "import_rework_limit": 3, "selection_failure_limit": 3,
                         "exhaustion_empty_limit": 3, "proposal_version_limit": 3, "contract_revision_limit": 3})

    def test_artifact_condition_reads_exact_snapshot_and_validates_bytes(self):
        from do_math import planning
        engine = routing_engine(); engine.head = "a" * 40; engine.store = Mock()
        data = b'{"proof": true}'
        engine.store.read.return_value = data
        ref = {"path": "runtime/artifacts/BA-test/evidence.json", "snapshot": "b" * 40,
               "sha256": hashlib.sha256(data).hexdigest()}
        result = planning.evaluate_condition({"op": "artifact_valid", "artifact_ref": ref},
            engine.instance, engine.runtime, evaluation_context=engine._evaluation_context())
        self.assertEqual(result["state"], "ready")
        engine.store.read.assert_called_once_with(ref["path"], ref["snapshot"])
        engine.store.read.return_value = b'{"valid":true'
        ref["sha256"] = hashlib.sha256(engine.store.read.return_value).hexdigest()
        result = planning.evaluate_condition({"op": "artifact_valid", "artifact_ref": ref},
            engine.instance, engine.runtime, evaluation_context=engine._evaluation_context())
        self.assertEqual(result["state"], "evaluation_error")


class ContinuationConnections(unittest.TestCase):

    def test_same_domain_callback_is_available_to_preview_without_publication(self):
        engine = routing_engine()
        engine.head = "snapshot"
        engine.runtime["executions"]["EX-one"] = {"id": "EX-one", "extensions": {}}
        engine._apply_model_metadata = Mock()
        engine._defer_review_for_research = Mock(return_value=False)
        engine._apply_extensions = Mock()
        engine._apply_revision_followup = Mock()
        engine._apply_action_resolutions = Mock()
        engine._apply_question_resolutions = Mock()
        engine._consume_action_events = Mock()
        engine._record_task_receipt = Mock()
        engine._save = Mock(side_effect=AssertionError("preview cannot publish"))
        engine._apply = lambda *a, **kw: engine.runtime["history"].append({"kind": "candidate"})
        original = deepcopy((engine.instance, engine.runtime))
        instance, runtime = deepcopy(original)
        bundle = {"integration_id": "IN-one", "output": {}, "extensions": {}, "owns_response": True}
        engine._apply_bundle_candidate(instance, runtime, bundle, action={"role": "research_work"},
                                       execution_id="EX-one", extensions={})
        self.assertEqual((engine.instance, engine.runtime), original)
        self.assertEqual(runtime["history"], [{"kind": "candidate"}])
        engine._save.assert_not_called()
        engine._record_task_receipt.assert_not_called()

    def test_bundle_live_prior_hash_and_transitive_impact_are_required(self):
        from do_math import knowledge, knowledge_io
        engine = routing_engine()
        engine.instance.update(feature_version=5, sources=[], kind_definitions={})
        engine.instance, engine.runtime, kid = knowledge_io.import_candidate(engine.instance, engine.runtime,
            {"kind": "theorem", "title": "T", "statement": "True", "summary": "True", "explanation": "Proof",
             "lean_code": "theorem t : True := by trivial", "declaration_names": ["t"], "dependencies": []},
            source_ref="EX-author", actor_ref="EX-author")
        engine.runtime["tasks"]["TK-dependent"] = {"id": "TK-dependent", "dependencies": [kid]}
        change = {"id": kid, "changes": {"summary": "New summary"}, "reason": "clarification", "impact_set": ["TK-dependent"]}
        bundle = {"integration_id": "IN-revision", "output": {}, "owns_response": False,
                  "extensions": {"knowledge_changes": [change]}, "impact_set": ["TK-dependent"],
                  "previous_hashes": {kid: knowledge.content_hash(engine.instance["knowledge"][kid])},
                  "members": ["activity-extensions.json/knowledge_changes/0"], "payload_sha256": "a" * 64}
        engine.head = "fixed"
        action = {"id": "AC-revise", "role": "research_work"}
        engine.runtime["executions"]["EX-author"] = {"id": "EX-author", "role": "research_work", "input_snapshot": "fixed"}
        engine._validate_bundle_impacts(engine.instance, engine.runtime, bundle, action=action, execution_id="EX-author")
        changed = deepcopy(bundle); changed["impact_set"] = []
        with self.assertRaisesRegex(ValueError, "impact"):
            engine._validate_bundle_impacts(engine.instance, engine.runtime, changed, action=action, execution_id="EX-author")
        engine.instance["knowledge"][kid]["title"] = "Changed after input"
        with self.assertRaisesRegex(ValueError, "hash|changed"):
            engine._validate_bundle_impacts(engine.instance, engine.runtime, bundle, action=action, execution_id="EX-author")

class ImpactReviewRouting(unittest.TestCase):
    def fixture(self):
        # Reuse the owner's concrete domain fixture, not a substitute apply engine.
        from test_redesign_CONTRACTS import ImpactReviewTests
        source = ImpactReviewTests(); source.setUp()
        engine = routing_engine(); engine.instance = source.instance
        engine.runtime.update(source.runtime); engine.head = "current"
        engine.instance["workspace"] = "unused"
        action = {"id": "AC-held", "role": "research_work", "owner_activity_id": "AY-work"}
        producer = engine.runtime["executions"]["EX-producer"]
        producer.update(action=action, output=source.output, input_bundle="BA-input", status="ended", outcome="execution_incomplete")
        request = source.request()
        received = {"bundles": [{"integration_id": "IN-held", "next_owner": "impact_review", "impact_review_request": request}]}
        engine._hold_impact_reviews(action, "EX-producer", received)
        return engine, source, action, request, received

    def test_exact_request_waits_for_accepted_review_without_new_producer(self):
        engine, source, action, request, received = self.fixture()
        before = deepcopy(source.output)
        engine._hold_impact_reviews(action, "EX-producer", received)
        reviews = [row for row in engine.runtime["queue"] if row.get("stage") == "impact_review"]
        self.assertEqual(len(reviews), 1)
        review_action = reviews[0]
        self.assertEqual(review_action["input_basis"]["impact_review"], request)
        self.assertNotIn("continuation_of", review_action)
        engine._receive_submission = Mock(); engine._save = Mock(); engine._settle_activity = Mock()
        with patch("do_math.engine.submission.read_sealed_submission",
                   side_effect=lambda execution, *_: {"output": execution["output"]}):
            engine._retry_impact_reviews()
        engine._receive_submission.assert_not_called()
        engine.runtime["executions"]["EX-review"] = {"id": "EX-review", "status": "ended", "outcome": "output_accepted",
            "action": review_action, "output": source.review_output(request)}
        engine.store = Mock(); engine.store.read.return_value = b"{}"
        with patch("do_math.engine.submission.read_sealed_submission",
                   side_effect=lambda execution, *_: {"output": execution["output"]}):
            engine._retry_impact_reviews()
        self.assertEqual(engine._receive_submission.call_args.args[2], "EX-producer")
        self.assertTrue(engine._receive_submission.call_args.kwargs["preserved"])
        self.assertEqual(engine.runtime["waiting_actions"][action["id"]]["review_execution_ids"], {"IN-held": "EX-review"})
        self.assertEqual(source.output, before)

    def test_shared_candidate_applies_actual_domain_revision_without_mutating_preview_source(self):
        from do_math import knowledge
        engine, source, action, request, received = self.fixture()
        bundle = deepcopy(source.bundle)
        bundle["owns_response"] = False
        for change in bundle["extensions"]["knowledge_changes"]:
            roots = knowledge.revision_roots(engine.instance, change["id"], change["changes"])
            change["impact_set"] = knowledge.plan_impact(engine.instance, engine.runtime, roots, [])["computed_impact"]
        roots = set().union(*(knowledge.revision_roots(engine.instance, change["id"], change["changes"])
            for change in bundle["extensions"]["knowledge_changes"]))
        bundle["impact_set"] = knowledge.plan_impact(engine.instance, engine.runtime, roots, [])["computed_impact"]
        # Preview and receiver both call this exact domain callback; storage/CAS is
        # tested separately. Keep independent copies of the actual original state.
        original = canonical_json(engine.instance)
        candidate, running = deepcopy(engine.instance), deepcopy(engine.runtime)
        engine._apply_bundle_candidate(candidate, running, bundle, action=action,
            execution_id="EX-producer", extensions=bundle["extensions"])
        self.assertEqual(canonical_json(engine.instance), original)
        self.assertEqual({source.ids[0], source.ids[2]}, {row["supersedes"] for row in candidate["knowledge"].values() if row.get("supersedes")})
        self.assertEqual(len([row for row in running["queue"] if row.get("reason") == "knowledge currentness changed"]), 0)

    def test_unresolved_review_remains_held_and_has_one_final_rejected_receipt(self):
        engine, source, action, request, received = self.fixture()
        output = source.review_output(request); output["impact_review"]["plan_decisions"][0]["decision"] = "unresolved"
        engine.runtime["executions"]["EX-review"] = {"id": "EX-review", "status": "ended", "outcome": "output_accepted",
            "action": deepcopy(next(row for row in engine.runtime["queue"] if row.get("stage") == "impact_review")), "output": output}
        engine._record_task_receipt = Mock(); engine._save = Mock(); engine._receive_submission = Mock()
        with patch("do_math.engine.submission.read_sealed_submission",
                   side_effect=lambda execution, *_: {"output": execution["output"]}):
            engine._retry_impact_reviews(); engine._retry_impact_reviews()
        engine._receive_submission.assert_not_called()
        engine._record_task_receipt.assert_called_once()
        self.assertFalse(engine._record_task_receipt.call_args.kwargs["accepted"])
        self.assertEqual(engine.runtime["waiting_actions"][action["id"]]["kind"], "impact_review_blocked")
        self.assertEqual(len([row for row in engine.runtime["queue"] if row.get("stage") == "impact_review"]), 1)


class AssessmentReassessmentConnections(unittest.TestCase):
    def fixture(self):
        from test_redesign_REVIEWS import AssessmentReassessmentTests
        owner = AssessmentReassessmentTests(); owner.setUp(); self.addCleanup(owner.doCleanups)
        owner.engine.runtime["status"] = "ready"
        return owner

    def test_central_control_consumes_qualified_evidence_and_retains_bounded_followup(self):
        owner = self.fixture(); engine = owner.engine
        request = {"id": "UC-reassessment", "action": "request", "config": {"role": "identity_review",
            "assessment_reassessment": owner.request(owner.defect())}}
        self.assertTrue(ResearchEngine._review_recovery_control(engine, request))
        opened = engine.runtime["history"][-1]["result"]
        self.assertEqual(opened["disposition"], "reassessment_opened")
        self.assertEqual(owner.use()["status"], "suspended")
        owner.complete("unresolved")
        activity = engine.runtime["activities"][opened["owner_activity_id"]]
        # The review-domain harness creates executions; attach them through the
        # production activity API before exercising the central terminal hook.
        from do_math.activities import assign_execution
        for execution in list(engine.runtime["executions"].values()):
            if execution.get("owner_activity_id") == activity["id"]:
                assign_execution(engine.runtime, activity["id"], execution)
        ResearchEngine._settle_activity(engine, activity["assigned_execution_ids"][-1])
        self.assertEqual(activity["status"], "finished")
        self.assertEqual(activity["unresolved"][0]["next_owner"], "research_plan")
        self.assertTrue(activity["followups"][0]["revisit_conditions"])
        self.assertEqual(len(engine.instance["identity_assessments"]), 1)

    def test_ordinary_report_cannot_suspend_and_closed_control_cannot_open_review(self):
        owner = self.fixture(); engine = owner.engine
        request = {"id": "UC-report", "action": "request", "config": {"role": "identity_review",
            "assessment_reassessment": owner.request({"kind": "report", "text": "Maybe wrong"})}}
        self.assertTrue(ResearchEngine._review_recovery_control(engine, request))
        self.assertEqual(engine.runtime["history"][-1]["result"]["disposition"], "report_only")
        self.assertEqual(owner.use()["status"], "active")
        engine.runtime["status"] = "closed"
        with self.assertRaisesRegex(ValueError, "closed/completed"):
            ResearchEngine._review_recovery_control(engine, request)

    def test_public_admission_binds_original_assessment_hash(self):
        owner = self.fixture(); engine = owner.engine
        engine.instance["workspace"] = owner.directory.name
        store = Mock(); store.load.return_value = (engine.head, engine.instance, engine.runtime)
        config = {"role": "identity_review", "assessment_reassessment": owner.request({"kind": "report", "text": "Read this original judgment"})}
        with patch("do_math.engine._repository", return_value=store), patch("do_math.engine._require_current_contract"):
            result = control(Path(owner.directory.name), "RI-test", "request", config=config)
            self.assertTrue(result["accepted"])
            wrong = deepcopy(config); wrong["assessment_reassessment"]["assessment_sha256"] = "0" * 64
            with self.assertRaisesRegex(ValueError, "original judgment"):
                control(Path(owner.directory.name), "RI-test", "request", config=wrong)


class LivePreviewConnections(unittest.TestCase):
    def test_installed_preview_uses_receiver_domain_callback_without_publication(self):
        from do_math import submission, contracts
        from do_math.control_transport import ControlTransport
        import time
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            workspace = root / "runs/EX-work/workspace"; workspace.mkdir(parents=True)
            engine = routing_engine(); engine.instance["workspace"] = str(root)
            engine.instance["config"]["max_artifact_bytes"] = 10000000
            engine.head = "fixed-snapshot"; engine._trackers = {}
            transport = ControlTransport(root / "transport")
            binding = transport.issue("EX-work", "GR-one")
            action = {"id": "AC-work", "role": "maintenance", "grant_id": "GR-one"}
            context = {"snapshot": engine.head, "execution_id": "EX-work", "action": action,
                "kind_definitions": {}, "knowledge_catalog": [], "tasks": [], "control_binding": binding}
            schema = contracts.with_integration_schema(contracts.schema_for("maintenance"))
            output = {"summary": "Checked draft", "used_sources": [], "questions": [], "report": "Preserved maintenance findings",
                "remaining_work": [], "integration_bundles": [{"integration_id": "IN-one", "members": ["output"], "impact_set": [], "authority_refs": []}]}
            submission.install_tools(workspace, context, schema, 10000000)
            (workspace / "draft.json").write_bytes(canonical_json(output))
            engine.runtime["executions"]["EX-work"] = {"id": "EX-work", "status": "running", "grant_id": "GR-one", "action": action, "input_bundle": "BA-input"}
            engine.store = Mock()
            engine.store.read.side_effect = lambda path, head: canonical_json(schema) if path.endswith("schema.json") else (workspace / "input/submission/context.json").read_bytes()
            engine._clock_guard = Mock(return_value={"usable": True, "observed_utc": "2026-09-22T00:00:00Z"})
            engine._validate_bundle_current = Mock(); engine._validate_bundle_candidate = Mock()
            engine._defer_review_for_research = Mock(return_value=False)
            for name in ("_apply_model_metadata", "_apply_extensions", "_apply_revision_followup", "_apply_action_resolutions", "_apply_question_resolutions", "_consume_action_events"):
                setattr(engine, name, Mock())
            before = deepcopy((engine.instance, engine.runtime))
            process = subprocess.Popen([sys.executable, "-B", str(workspace / "input/tools/check_submission.py"),
                "--output", "draft.json", "--preview", "--wait-seconds", "20"], cwd=workspace,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            try:
                with patch("do_math.engine.governance.authorize", return_value={"allowed": True}), patch.object(engine, "_apply_bundle_candidate", wraps=engine._apply_bundle_candidate) as candidate:
                    deadline = time.monotonic() + 25
                    while process.poll() is None and time.monotonic() < deadline:
                        transport.pump(engine._publish_control_request)
                        time.sleep(.02)
                    if process.poll() is None: process.kill()
                    stdout, stderr = process.communicate()
                    self.assertEqual(process.returncode, 0, stdout + stderr)
                    self.assertEqual(candidate.call_count, 1)
            finally:
                if process.poll() is None:
                    process.kill()
                process.communicate()
            self.assertEqual((engine.instance, engine.runtime), before)
            engine.store.save_with_state.assert_not_called()
            receipt = next(iter(transport._receipts.values()))
            self.assertEqual(receipt["state"], "previewed")
            self.assertTrue(receipt["result"]["passed"], receipt)
            self.assertNotIn("publication_id", receipt)


class DelegationConnections(unittest.TestCase):
    def test_actual_blind_judgments_apply_the_approved_review_recovery(self):
        from test_review_engine import FakeEngine, grant_replacement
        from do_math import governance
        from types import MethodType
        with tempfile.TemporaryDirectory() as temporary:
            engine = FakeEngine(temporary)
            grant_replacement(engine)
            cid = engine._start_identity_review("K1")
            action = deepcopy(engine.pending())
            engine._record_review_recovery(action, ValueError("permanent_loss"), retryable=False)
            engine.instance["decisions"]["ORIGINAL"] = {"id": "ORIGINAL", "actor": "user", "kind": "review_replacement", "source_ref": "SOURCE-review"}
            engine.instance, engine.runtime, _ = governance.apply_decision(engine.instance, engine.runtime,
                {"kind": "delegation", "decision_id": "DD", "delegation": {"id": "DG", "status": "active", "decision_kind": "review_replacement",
                    "original_decision_id": "ORIGINAL", "included_targets": ["K1"], "excluded_targets": [], "external_effects": [], "resource_limits": {}, "expires_at": None}}, source_ref="SOURCE-review")
            effect = {"review_cycle_id": cid, "stage": action["stage"], "slot": action["slot"],
                      "round": action["round"], "replacement_for": 0,
                      "continuity_break_cause": "permanent_loss"}
            case = {"id": "CASE", "decision_kind": "review_replacement", "target_id": "K1", "external_effects": [], "resources": {}, "effect": effect,
                    "basis_refs": [{"id": cid}]}
            request = {"id": "UC-case", "action": "request", "config": {"role": "maintenance", "review_replacement": {"action": action, "grant_id": "GR-review", "delegation_id": "DG", "case": case}}}
            engine._review_recovery_control = MethodType(ResearchEngine._review_recovery_control, engine)
            engine._apply_delegation_judgment = MethodType(ResearchEngine._apply_delegation_judgment, engine)
            self.assertTrue(engine._review_recovery_control(request))
            engine.runtime.setdefault("history", []).append({"kind": "user_control", "request": request})
            judgments = [a for a in engine.runtime["queue"] if a.get("delegation_application_id")]
            self.assertEqual(len(judgments), 2)
            application_id = judgments[0]["delegation_application_id"]
            application = engine.runtime["delegation_applications"][application_id]
            for index, judgment in enumerate(judgments):
                eid = "EX-delegation-" + str(index)
                engine.runtime["executions"][eid] = {"id": eid, "role": "intent_interpretation", "status": "running",
                    "input_sha256": hashlib.sha256(("exact rendered prompt " + str(index)).encode()).hexdigest(),
                    "delegation_input_sha256": application["input_sha256"]}
                engine._apply_delegation_judgment(judgment, {"delegation_judgment": {"input_sha256": application["input_sha256"], "decision": "within_scope", "reason": "This exact case stays within the original approved replacement"}}, eid)
            self.assertEqual(engine.runtime["delegation_applications"][application_id]["application"]["status"], "applied")
            self.assertTrue(any(a.get("replacement_for") == 0 for a in engine.runtime["queue"]))


class ObservationTransactions(unittest.TestCase):
    def test_failed_observation_publication_does_not_advance_the_tracker(self):
        from do_math.observations import ObservationTracker
        from test_redesign_OBSERVATION import Clock, rule
        engine = routing_engine(); engine._controls = Mock(); engine._check_conversations = Mock(return_value=False)
        engine.runtime["executions"]["EX-one"] = {"id": "EX-one", "role": "research_work", "action": {"role": "research_work"}}
        engine._inline_reviewing = False; engine._transport = Mock(); engine._transport_bindings = {"EX-one": {}}
        with tempfile.TemporaryDirectory() as temporary:
            tracker = ObservationTracker("EX-one", Path(temporary), {"observation_rules": [rule()], "tool_review_window_seconds": 60, "self_check_response_window_seconds": 5}, clock=Clock())
            before = deepcopy((engine.instance, engine.runtime))
            engine._save = Mock(side_effect=ValueError("CAS failure"))
            with self.assertRaisesRegex(ValueError, "CAS"):
                engine._observe_running("EX-one", tracker, {"type": "tick", "counters": {"attempts": 2}})
            self.assertEqual(tracker.counters, {})
            self.assertEqual((engine.instance, engine.runtime), before)
            engine._transport.request_self_check.assert_not_called()
            engine._save.side_effect = None
            engine._observe_running("EX-one", tracker, {"type": "tick", "counters": {"attempts": 2}})
            self.assertEqual(tracker.counters, {"attempts": 2})
            self.assertTrue(engine.runtime["self_check_obligations"])
            engine._transport.request_self_check.assert_called_once()


class ReceiptAndQuotaConnections(unittest.TestCase):
    def test_task_receipt_occurs_once_after_the_complete_bundle_result(self):
        for owner in (None, "engine"):
            with self.subTest(owner=owner), tempfile.TemporaryDirectory() as temporary:
                workspace = Path(temporary)
                from types import SimpleNamespace
                from research_fixtures import sealed_maintenance_submission
                from do_math import submission
                intent, artifacts = sealed_maintenance_submission(workspace, 'EX-work')
                prefix = intent['output_ref'].removesuffix('output.json')
                intent.update(extensions_ref=prefix+'extensions.json', check_ref=prefix+'check.json')
                engine = routing_engine()
                engine.store = SimpleNamespace(read=lambda path, head: artifacts[path])
                engine.head = 'fixture-snapshot'
                output = submission.load_json(artifacts[intent['output_ref']])
                context = submission.load_json((workspace/'input/submission/context.json').read_bytes())
                receipt_artifacts = [{'path': path, 'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)}
                                     for path, raw in artifacts.items()]
                execution = {'id': 'EX-work', 'action': context['action'], 'status': 'stopping',
                    'stop_phase': 'terminating', 'submission_intent': intent,
                    'submission_receipt': {'kind': 'submit_intent', 'state': 'accepted',
                        'execution_id': 'EX-work', 'payload': {'submission_check': {'artifacts': receipt_artifacts}}}}
                engine.runtime["executions"][execution["id"]] = execution
                action = {"id": "AC-one", "role": "maintenance"}
                engine._save = Mock(); engine._resolve_failed_actions = Mock(); engine._ensure_academic_followup = Mock()
                ordered = []
                result = {"status": "accepted" if owner is None else "partial", "bundles": [{"integration_id": "IN-one", "status": "accepted" if owner is None else "returned", "next_owner": owner}], "retry_bundle_ids": [] if owner is None else ["IN-one"], "issues": []}
                def bundles(*args): ordered.append("all bundles"); return result
                engine._apply_submission_bundles = bundles
                engine._record_task_receipt = Mock(side_effect=lambda *a, **kw: ordered.append("task receipt"))
                engine._receive_submission(action, {"output": output}, execution["id"], context, engine._response_schema(action), workspace)
                self.assertEqual(ordered, ["all bundles", "task receipt"] if owner is None else ["all bundles"])
                self.assertEqual(execution["status"], "ended" if owner is None else "stopping")
                if owner:
                    self.assertEqual(engine.runtime["queue"], [])
                    self.assertEqual(engine.runtime["waiting_actions"][action["id"]]["next_owner"], "engine")

    def test_every_review_owned_attempt_uses_owner_admission_before_registration(self):
        engine = routing_engine()
        profile = next(p for p in execution_profiles.build_profiles(DEFAULT_CONFIG)["execution_profiles"].values()
                       if p["role"] == "supplemental_research")
        engine._execution_profile = Mock(return_value=profile)
        engine._admit_review_execution = Mock(return_value={"disposition": "review_followup_reserved"})
        engine._request_review_resource_disposition = Mock()
        action = {"id": "AC-review", "role": "supplemental_research", "owner_review_cycle_id": "RC-one"}
        engine.runtime["queue"] = [action]
        result = engine._register_execution(action, {"id": "EX-attempt", "role": action["role"], "status": "queued"})
        self.assertIsNone(result)
        execution = engine._admit_review_execution.call_args.args[1]
        self.assertEqual(execution["actor_kind"], "ai")
        self.assertEqual(execution["execution_profile_ref"], execution_profiles.profile_ref(profile))
        self.assertNotIn("EX-attempt", engine.runtime["executions"])
        engine._request_review_resource_disposition.assert_called_once_with(
            action, "review_followup_reserved", {"disposition": "review_followup_reserved"})


class FinalBoundaryConnections(unittest.TestCase):
    def test_operational_completion_and_transfer_use_real_task_domain_validation(self):
        from test_redesign_TASKS import AssessmentApplicationTests
        from do_math import planning
        instance, runtime, assessment = AssessmentApplicationTests().fixture()
        assessment["decision"] = "closed"
        for obligation in runtime["tasks"]["TK-1"]["completion_obligations"]:
            obligation["judges"] = ["operational_review"]
        instance["decisions"]["DC-1"]["change"]["contract_sha256"] = planning.contract_hash(runtime["tasks"]["TK-1"])
        runtime["executions"].pop("EX-plan")
        runtime["executions"].update({"EX-work": {"id": "EX-work", "role": "research_work", "status": "ended", "action": {"target": "TK-1"}},
            "EX-review": {"id": "EX-review", "role": "operational_review", "input_snapshot": "input", "output": {"task_assessments": [assessment]}}})
        engine = routing_engine(); engine.instance, engine.runtime = instance, runtime
        engine.store = Mock(); engine.store.load.return_value = ("input", deepcopy(instance), deepcopy(runtime))
        engine._evaluation_context = Mock(return_value={})
        record = {"id": "OD-one", "execution_id": "EX-review", "target_execution_id": "EX-work",
            "disposition": {"kind": "task_disposition", "task_id": "TK-1", "task_state": "closed", "authority_ref": "DC-1"}}
        engine.runtime["operational_dispositions"] = {record["id"]: record}
        before = deepcopy((engine.instance, engine.runtime))
        engine.instance["decisions"]["DC-1"]["status"] = "revoked"
        with self.assertRaisesRegex(ValueError, "current"):
            engine._complete_operational_disposition(record)
        self.assertNotEqual(engine.runtime["tasks"]["TK-1"]["status"], "closed")
        engine.instance, engine.runtime = before
        engine._complete_operational_disposition(engine.runtime["operational_dispositions"]["OD-one"])
        self.assertEqual(engine.runtime["tasks"]["TK-1"]["status"], "closed")
        self.assertEqual(engine.runtime["tasks"]["TK-2"]["completion_obligations"][-1]["id"], "OB-inherited")
        self.assertEqual(engine.runtime["tasks"]["TK-2"]["reviews"], [])

    def test_paused_initialization_reads_original_input_but_active_corruption_fails(self):
        engine = routing_engine()
        engine.instance.update(feature_version=5, governance={}, lifecycle={"state": "paused", "input_id": "UC-one", "immutable_input": {"ref": "UC-one"}})
        engine.runtime.update(resume_lifecycle="initializing", inputs=[{"id": "UC-one", "config": {"goal": "Original goal"}}])
        self.assertEqual(engine._governance()["goal"], "Original goal")
        self.assertEqual(engine._governance()["status"], "unadopted_input")
        engine.instance["governance"] = {"GD-policy": {"kind": "policy", "status": "active"}}
        self.assertEqual(engine._governance()["goal"], "Original goal")
        engine.instance["lifecycle"]["state"] = "active"
        with self.assertRaisesRegex(ValueError, "charter"):
            engine._governance()

    def test_operational_task_disposition_uses_authoritative_item_assessment(self):
        engine = routing_engine()
        assessment = {"task_id": "TK-one", "decision": "completed", "reason": "All obligations assessed", "item_dispositions": [], "unresolved": []}
        engine.runtime["tasks"]["TK-one"] = {"id": "TK-one", "status": "active"}
        engine.runtime["executions"] = {"EX-work": {"id": "EX-work", "status": "ended", "action": {"target": "TK-one"}},
            "EX-review": {"input_snapshot": "input", "output": {"task_assessments": [assessment]}}}
        engine.store = Mock(); engine.store.load.return_value = ("input", {}, {"tasks": {"TK-one": {"id": "TK-one"}}})
        engine._evaluation_context = Mock(return_value={"snapshot": "current"})
        record = {"id": "OD-one", "execution_id": "EX-review", "target_execution_id": "EX-work", "disposition": {"kind": "task_disposition", "task_id": "TK-one", "task_state": "completed", "authority_ref": "designated obligation judge"}}
        completed = deepcopy(engine.runtime); completed["tasks"]["TK-one"]["status"] = "completed"
        with patch("do_math.engine.task_scope.apply_task_assessments", return_value=(engine.instance, completed)) as apply:
            engine._complete_operational_disposition(record)
        self.assertEqual(apply.call_args.args[2], [assessment])
        self.assertEqual(apply.call_args.kwargs["execution_id"], "EX-review")
        self.assertEqual(apply.call_args.kwargs["evaluation_context"], {"snapshot": "current"})
        self.assertEqual(engine.runtime["tasks"]["TK-one"]["status"], "completed")


class AuditConsumerConnections(unittest.TestCase):
    def test_review_public_dialogue_keeps_raw_row_order_and_retries_after_failed_cas(self):
        from do_math.observations import ObservationTracker
        engine = routing_engine()
        engine._controls = Mock(); engine._check_conversations = Mock(return_value=False)
        engine._inline_reviewing = False; engine._record_review_observation = Mock()
        engine.runtime["executions"]["EX-review"] = {"id": "EX-review", "action": {"role": "identity_review", "review_cycle_id": "RC-one"}}
        with tempfile.TemporaryDirectory() as temporary:
            engine.instance["workspace"] = temporary
            path = Path(temporary) / "runs/EX-review/evidence/stdout.jsonl"
            path.parent.mkdir(parents=True)
            event = {"type": "item.completed", "item": {"type": "agent_message", "text": "Visible independent judgment"}}
            row = json.dumps(event).encode() + b"\n"
            path.write_bytes(b"\n" + row)
            tracker = ObservationTracker("EX-review", Path(temporary), {"observation_mode": "deadline_only", "research_self_checks": False})
            engine._save = Mock(side_effect=ValueError("CAS failed"))
            with self.assertRaisesRegex(ValueError, "CAS"):
                engine._observe_running("EX-review", tracker, event)
            self.assertFalse(getattr(engine, "_review_event_cursors", {}))
            engine._save.side_effect = None
            engine._observe_running("EX-review", tracker, event)
            call = engine._record_review_observation.call_args
            self.assertEqual(call.args, ("EX-review", event))
            self.assertEqual(call.kwargs["event_index"], 1)
            self.assertEqual(engine._save.call_args.args[0][call.kwargs["artifact_ref"]], row)
            self.assertEqual(engine._review_event_cursors["EX-review"], (2, len(b"\n" + row)))
            tail = {"type": "item.completed", "item": {"type": "agent_message", "text": "Final unterminated public message"}}
            with path.open("ab") as stream: stream.write(json.dumps(tail).encode())
            engine._drain_review_observations("EX-review", tracker)
            self.assertEqual(engine._record_review_observation.call_args.args, ("EX-review", tail))
            self.assertEqual(engine._record_review_observation.call_args.kwargs["event_index"], 2)

    def test_central_repair_restores_actual_sealed_bytes_before_one_continuation(self):
        from test_repair_execution import RepairExecutionTests
        fixture = RepairExecutionTests("test_actual_restore_verify_and_explicit_activity_followup")
        fixture.setUp(); self.addCleanup(fixture.doCleanups)
        host = fixture.host
        host.runtime["executions"]["EX-target"]["pending_operational_disposition"] = "OD-repair"
        host._save()
        result = ResearchEngine._complete_operational_disposition(host, host.runtime["operational_dispositions"]["OD-repair"])
        host._save()
        self.assertEqual(result["status"], "applied")
        self.assertEqual(fixture.destination.read_bytes(), fixture.raw)
        self.assertEqual(len(host.runtime["queue"]), 1)
        self.assertEqual(host.runtime["queue"][0]["continuation_of"], "EX-target")
        self.assertNotIn("pending_operational_disposition", host.runtime["executions"]["EX-target"])
        ResearchEngine._complete_operational_disposition(host, host.runtime["operational_dispositions"]["OD-repair"])
        self.assertEqual(len(host.runtime["queue"]), 1)
        proof = host.runtime["operational_dispositions"]["OD-repair"]["result"]["repair"]
        self.assertEqual(proof["repair_effect"]["effect_refs"], proof["repair_verification"]["effect_refs"])

    def test_operational_repair_candidate_never_mutates_files_or_publishes(self):
        engine = routing_engine(); engine._save = Mock()
        engine.runtime["executions"] = {"EX-target": {"id": "EX-target", "status": "ended"}}
        proposal = {"kind": "repair", "basis_refs": ["EX-target"], "next_owner": "engine", "reason": "Restore input",
                    "repair_target": "input/catalog/task.json", "meaning_preserving": True, "verification": "sha256:" + "a" * 64}
        with patch("do_math.engine.repair_execution.complete_repair") as effect:
            with self.assertRaisesRegex(ValueError, 'requires retry'):
                engine._apply_operational_disposition({"target": "EX-target"}, proposal, "EX-review")
            effect.assert_not_called()
        engine._save.assert_not_called()
        self.assertFalse(engine.runtime.get('operational_dispositions'))
        self.assertEqual(engine.runtime["queue"], [])

    def test_current_corrupt_source_is_rejected_before_any_recovery_publication(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            subprocess.run(["git", "init", "-q", str(root / "repo")], check=True)
            source = root / "source.txt"; source.write_text("preserved original", encoding="utf-8")
            created = initialize(root / "repo", goal="Read the preserved source", workspace=root / "work", sources=[source])
            store = _repository(root / "repo", created["instance_id"])
            head, instance, runtime = store.load()
            raw_store = store._store
            # Deliberate corruption fixture: only bypass the writer's immutable-artifact
            # guard while injecting damage. The tested read and recovery gates are real.
            with patch.object(raw_store, "_validate_artifact_changes", return_value=None):
                damaged = raw_store.publish(head, {instance["sources"][0]["path"]: b"corrupt bytes"}).head
            with self.assertRaises((ValueError, RuntimeError)):
                ResearchEngine(root / "repo", created["instance_id"]).run(max_steps=1)
            self.assertEqual(raw_store.read_snapshot().head, damaged)

    def test_continuation_preserves_older_files_and_latest_replacements(self):
        from do_math.context_store import restore_continuation
        raw = {"old": b"old proof", "new": b"new proof", "notes": b"old notes", "result-first": b"first", "result-second": b"second"}
        def entry(path, ref): return {"path": path, "artifact_ref": ref, "sha256": hashlib.sha256(raw[ref]).hexdigest(), "bytes": len(raw[ref])}
        runtime = {"executions": {
            "EX-first": {"id": "EX-first", "role": "research_work", "status": "ended", "owner_activity_id": "AY-one", "continuation_of": None,
                "result_ref": "result-first", "output_files": [entry("proof.lean", "old"), entry("notes.txt", "notes")]},
            "EX-second": {"id": "EX-second", "role": "research_work", "status": "ended", "owner_activity_id": "AY-one", "continuation_of": "EX-first",
                "result_ref": "result-second", "output_files": [entry("proof.lean", "new")]}}}
        action = {"role": "research_work", "continuation_of": "EX-second"}
        with tempfile.TemporaryDirectory() as temporary:
            context = restore_continuation(runtime, action, Path(temporary), snapshot="fixed", read_artifact=raw.__getitem__)
            self.assertEqual({row["path"]: row["artifact_ref"] for row in context["previous_output_files"]}, {"proof.lean": "new", "notes.txt": "notes"})
            self.assertEqual([row["execution_id"] for row in context["continuation_history"]], ["EX-first", "EX-second"])
            self.assertEqual((Path(temporary) / "input/previous-output/proof.lean").read_bytes(), b"new proof")
            runtime["executions"]["EX-first"]["continuation_of"] = "EX-second"
            with self.assertRaisesRegex(ValueError, "cycle"):
                restore_continuation(runtime, action, Path(temporary), snapshot="fixed", read_artifact=raw.__getitem__)

    def test_discard_records_cancelled_preparation_and_explicit_continuation(self):
        from do_math import execution_lifecycle
        engine = routing_engine()
        with tempfile.TemporaryDirectory() as temporary:
            engine.instance["workspace"] = temporary
            engine.instance["config"] = deepcopy(DEFAULT_CONFIG)
            engine.instance.update(execution_profiles.build_profiles(DEFAULT_CONFIG))
            action = {"id": "AC-one", "role": "research_preparation"}
            engine.runtime["queue"] = [action]
            execution = engine._register_execution(action, {"id": "EX-one", "role": action["role"], "status": "queued"})
            execution_lifecycle.begin_preparation(execution, at="2026-09-20T00:00:00+00:00")
            base = Path(temporary) / "runs/EX-one"
            base.mkdir(parents=True)
            (base / "partial").write_text("incomplete private input")
            engine._transport_bindings = {}; engine._save = Mock()
            engine._discard_prepared_input(base, "EX-one")
            ended = engine.runtime["executions"]["EX-one"]
            self.assertEqual(ended["outcome"], "cancelled")
            self.assertEqual(engine.runtime["queue"][0]["continuation_of"], "EX-one")
            self.assertEqual(engine.runtime["queue"][0]["owner_activity_id"], ended["owner_activity_id"])
            self.assertFalse(base.exists())
            engine._save.assert_called()

    def test_runner_tools_consume_the_selected_edition(self):
        engine = routing_engine()
        profile = next(p for p in execution_profiles.build_profiles(DEFAULT_CONFIG)["execution_profiles"].values()
                       if p["actor_kind"] == "ai")
        engine.instance["config"] = {"scholarly_enabled": True, "scholarly_server": {"command": "changed"}}
        engine.runner = Mock(); engine.runner.run = lambda **kwargs: None
        arguments = {"profile": profile}
        engine._runner_tools(arguments)
        for name, value in execution_profiles.runner_tools(profile).items():
            self.assertEqual(arguments[name], value)

class TaskObservationRoleTests(unittest.TestCase):
    def test_task_rules_follow_the_selected_roles_observation_contract(self):
        from do_math.observations import tracker_config, ObservationTracker

        class BeforeInput(Exception):
            pass

        settings = {**deepcopy(DEFAULT_CONFIG), "tool_review_window_seconds": 60,
                    "self_check_response_window_seconds": 5}
        profiles = execution_profiles.build_profiles(settings)["execution_profiles"]
        rule = {"id": "checkpoints", "operator": "checkpoint_count_gte",
                "subject": {"kind": "checkpoint", "id": "$execution"},
                "basis": {"source": "checkpoint", "unit": "count"},
                "threshold": 2, "required_evidence": ["contract"]}
        for role in ("research_work", "supplemental_research"):
            with self.subTest(role=role):
                engine = routing_engine()
                engine.head = "snapshot-one"
                engine.instance["config"] = deepcopy(settings)
                engine.runtime["tasks"]["TK-one"] = {"initial_observation_rules": [deepcopy(rule)]}
                profile = next(p for p in profiles.values() if p["role"] == role)
                engine._check_installation = Mock(return_value=True)
                engine._clock_guard = Mock(return_value={"usable": True})
                engine._evaluation_context = Mock(return_value={})
                engine._action_lifecycle_gate = Mock()
                engine._revision_dispatch_waits = Mock(return_value=[])
                engine._selected_action_current = Mock(return_value=True)
                engine._obsolete_action_reason = Mock(return_value=None)
                engine._execution_profile = Mock(return_value=profile)
                engine._activity_for_action = Mock(return_value={"id": "AY-one"})
                engine._register_execution = Mock(side_effect=BeforeInput)
                action = {"id": "AC-one", "role": role, "target": "TK-one"}
                with patch("do_math.engine.tracker_config", wraps=tracker_config) as configured, \
                     patch("do_math.engine.governance.authorize", return_value={"allowed": True, "grant_id": "GR-one"}), \
                     patch("do_math.engine.planning.task_ready", return_value={"state": "ready"}):
                    with self.assertRaises(BeforeInput):
                        next(engine._call_steps(action))
                eid = engine._register_execution.call_args.args[1]["id"]
                config = tracker_config(profile, initial_self_check_rules=
                    configured.call_args.kwargs["initial_self_check_rules"])
                tracker = ObservationTracker(eid, Path("."), config)
                self.assertEqual(tracker.research_self_checks, role == "research_work")
                self.assertEqual(bool(tracker.rules), role == "research_work")
                if tracker.rules:
                    self.assertEqual(tracker.rules[0]["subject"]["id"], eid)
                self.assertEqual(engine.runtime["tasks"]["TK-one"]["initial_observation_rules"], [rule])


if __name__ == "__main__":
    unittest.main()
