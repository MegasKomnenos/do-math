"""Regression cases for STORAGE's version-5 family-record persistence boundary."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
import sys
from copy import deepcopy
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from do_math.repository import ResearchRepository, canonical_json, semantic_content_hash
from do_math.events import EventPublisher
from do_math.state_contract import STATE_FORMAT_VERSION, StateContract
from do_math.git_store import GitStateStoreConflict
from do_math.repository import transport_json


INSTANCE_ID = "RI-01ARZ3NDEKTSV4RRFFQ69G5FAV"


class StorageRedesignTests(unittest.TestCase):
    def native_preparation_task(self):
        from do_math.contracts import task_candidate_record
        # Exact normal final from REAL run013; model not called by this test.
        raw = (Path(__file__).parent / 'fixtures/native-preparation-task.json').read_bytes()
        candidate = json.loads(raw)['candidates'][0]
        task = task_candidate_record(candidate, task_id='TK-native-preparation')
        task.pop('revises_task_id')
        task['status'] = 'planned'
        return task

    def task_reference_fixture_instance(self, task):
        # Exact recorded profiles and source-bound user approval from run013.
        return json.loads((Path(__file__).parent /
            'fixtures/native-task-reference-owners.json').read_bytes())

    def test_native_task_input_and_basis_locators_survive_actual_git_storage(self):
        task = self.native_preparation_task()
        self.assertIn('context:goal', task['basis_refs'])
        self.assertIn('source:NatAddZero.lean', task['inputs'])
        head = self.repository.initialize(self.task_reference_fixture_instance(task),
            {'feature_version': 5, 'tasks': {task['id']: task}})
        saved = self.repository.load(head)[2]['tasks'][task['id']]
        for field in ('inputs', 'basis_refs', 'reuse', 'dependencies', 'authority_refs', 'profile_refs'):
            self.assertEqual(saved[field], task[field])

    def test_task_source_path_locators_keep_exact_unicode_in_git(self):
        task = self.native_preparation_task()
        refs = ['source:e\u0301.lean', 'input/sources/\u212a.lean',
                'runtime/artifacts/BA-source/report.md', 'context:policy', 'tool:lean']
        task.update(inputs=refs, basis_refs=refs)
        head = self.repository.initialize(self.task_reference_fixture_instance(task),
            {'feature_version': 5, 'tasks': {task['id']: task}})
        saved = self.repository.load(head)[2]['tasks'][task['id']]
        self.assertEqual(saved['inputs'], refs)
        self.assertEqual(saved['basis_refs'], refs)

    def test_task_locator_storage_does_not_widen_record_or_profile_authority(self):
        task = self.native_preparation_task()
        task.update(inputs=[], basis_refs=[])
        head = self.repository.initialize(self.task_reference_fixture_instance(task),
            {'feature_version': 5, 'tasks': {task['id']: task}})
        _, instance, runtime = self.repository.load(head)
        for field in ('reuse', 'dependencies', 'authority_refs', 'profile_refs'):
            with self.subTest(field=field):
                changed = deepcopy(runtime)
                changed['tasks'][task['id']][field] = ['context:goal']
                with self.assertRaisesRegex(ValueError, field):
                    self.repository.validate_candidate(instance, changed, head)

    def test_final_goal_assessment_keeps_its_recorded_group_key_in_git(self):
        basis = 'a' * 64
        head = self.repository.initialize({'feature_version': 5, 'goal_assessment_basis': basis},
                                          {'feature_version': 5})
        self.assertEqual(self.repository.load(head)[1]['goal_assessment_basis'], basis)

    def test_scoped_review_research_request_survives_action_storage(self):
        import test_review_research as research_tests
        cycle, _ = research_tests.PureResearchTests().fixture()
        request_id = next(iter(cycle['research']))
        action = {'id': 'AC-investigation', 'role': 'supplemental_research',
                  'research_request_id': request_id, 'slot': 'research-' + request_id,
                  'stage': 'investigating'}
        self.assertIn(':', request_id)
        head = self.repository.initialize({'feature_version': 5},
            {'feature_version': 5, 'queue': [action]})
        self.assertEqual(self.repository.load(head)[2]['queue'], [action])

    def test_lossless_query_cursor_retains_exact_search_text(self):
        from do_math.repository import _encode_cursor, _decode_cursor
        cursor = {"snapshot": "a" * 40, "prefix": "research/", "text": "e\u0301", "last_path": "research/a.json"}
        self.assertEqual(_decode_cursor(_encode_cursor(cursor)), cursor)

    def test_plain_exact_json_rejects_invalid_stored_records_on_git_read(self):
        import json
        schema = {"type": "object", "additionalProperties": False,
            "properties": {"id": {"type": "string"}, "payload": {"type": "object", "additionalProperties": False,
                "properties": {"text": {"type": "string"}}, "required": ["text"]}}, "required": ["id", "payload"]}
        self.repository.register_family("research", "exact_negative", schema=schema)
        head = self.repository.initialize({"feature_version": 5, "exact_negative": {
            "EN-1": {"id": "EN-1", "payload": {"text": "e\u0301"}}}}, {"feature_version": 5})
        descriptor = self.repository.read_record("EN-1", head)
        stored = json.loads(descriptor["bytes"])
        for payload in ({"text": "valid string", "unknown": "forbidden"}, {"text": 3}):
            with self.subTest(payload=payload):
                broken = deepcopy(stored); broken["record"]["payload"] = payload
                head = self.repository._store.publish(head, {descriptor["path"]: canonical_json(broken)}).head
                with self.assertRaises(ValueError): self.repository.load(head)

    def test_exact_singleton_root_is_typed_without_wrapper_autodetection(self):
        schema = {"type": "array", "items": {"type": "object", "additionalProperties": False,
            "properties": {"value": {"type": "string"}}, "required": ["value"]}}
        self.repository.register_family("runtime", "exact_history", shape="singleton", schema=schema,
                                        identity=False)
        history = [{"value": "e\u0301\r\n"}]
        head = self.repository.initialize({"feature_version": 5}, {"feature_version": 5, "exact_history": history})
        _, instance, runtime = self.repository.load(head)
        self.assertEqual(runtime["exact_history"], history)
        descriptor = self.repository.records(head, family="exact_history")[0]
        self.assertEqual(descriptor["json_pointer"], "/record")
        self.assertNotIn("utf8_base64", descriptor["bytes"].decode("utf-8"))

    def test_lossless_json_preserves_values_and_mathematical_dictionary_keys(self):
        import json
        from do_math.repository import lossless_json
        value = {"source": '-- e\u0301\r\n', "declarations": {"\u212a": "\u2126", "K": "\u03a9"}}
        raw = lossless_json(value)
        self.assertEqual(json.loads(raw), value)
        self.assertNotEqual(lossless_json("e\u0301"), lossless_json("\u00e9"))
        for invalid in (0.5, float("nan"), 2 ** 53, "\ud800", {1: "not a string key"}):
            with self.assertRaises(ValueError): lossless_json(invalid)
        self.assertEqual(canonical_json(value), raw)

    def test_registered_exact_payload_keeps_closed_logical_validation_and_file_coordinates(self):
        import json
        schema = {"type": "object", "additionalProperties": False,
            "properties": {"id": {"type": "string"}, "machine": {"type": "string"},
                "payload": {"type": "object", "additionalProperties": {"type": "string"}}},
            "required": ["id", "machine", "payload"]}
        self.repository.register_family("research", "exact_fixture", schema=schema)
        record = {"id": "EF-1", "machine": "e\u0301", "payload": {"\u212a": "e\u0301\r\n", "K": "\u00e9"}}
        instance = {"feature_version": 5, "exact_fixture": {record["id"]: record}}
        runtime = {"feature_version": 5}
        checked = self.repository.validate_candidate(instance, runtime)
        self.assertEqual(record["machine"], "e\u0301")  # pure candidate
        self.assertEqual(checked["instance"]["exact_fixture"]["EF-1"]["machine"], "e\u0301")
        head = self.repository.initialize(instance, runtime)
        _, state, run = self.repository.load(head)
        self.assertEqual(state["exact_fixture"]["EF-1"]["payload"], record["payload"])
        descriptor = self.repository.read_record("EF-1", head)
        stored = json.loads(self.repository.read(descriptor["path"], head))
        self.assertEqual(stored["record"]["payload"], record["payload"])
        self.assertEqual(descriptor["sha256"], hashlib.sha256(descriptor["bytes"]).hexdigest())
        self.assertEqual(descriptor["json_pointer"], "/record")
        self.assertEqual(descriptor["record"], state["exact_fixture"]["EF-1"])
        self.assertNotIn("utf8_base64", descriptor["bytes"].decode("utf-8"))
        self.assertEqual(self.repository.save(head, state, run), head)
        state["exact_fixture"]["EF-1"]["payload"]["K"] = 7
        with self.assertRaises(ValueError): self.repository.validate_candidate(state, run)

    def test_governance_original_text_survives_lossless_git_and_immutable_check(self):
        from do_math.governance import preserve_source
        text = 'Prove that "e\u0301" contains two Unicode code points.\r\n'
        source = preserve_source("GS-exact", text, origin="user")
        instance = {"feature_version": 5, "governance_sources": {source["id"]: source}}
        head = self.repository.initialize(instance, {"feature_version": 5})
        _, state, runtime = self.repository.load(head)
        self.assertEqual(state["governance_sources"][source["id"]], source)
        state["governance_sources"][source["id"]] = preserve_source("GS-exact", text.replace("e\u0301", "\u00e9"), origin="user")
        with self.assertRaisesRegex(ValueError, "immutable"):
            self.repository.save(head, state, runtime)

    def test_actual_host_profile_reservation_round_trip_and_authority_refs(self):
        import platform
        from do_math import execution_profiles as profiles, governance
        from do_math.session_slots import GitSessionSlots
        instance, runtime = self._execution_state()
        source = governance.preserve_source("GS-host", "Disposable test approval: local jobs 3, memory 4096, CPU 8000; reserve 1/1024/1000", origin="user")
        instance["governance_sources"] = {source["id"]: source}
        constraint = profiles.host_constraint(host_id=platform.node(),
            limits={"jobs": 3, "memory_bytes": 4096, "cpu_rate_basis_points": 8000},
            control_reserve={"jobs": 1, "memory_bytes": 1024, "cpu_rate_basis_points": 1000},
            authority_refs=[source["id"]])
        instance["capacity_constraints"][constraint["id"]] = constraint
        instance["host_capacity_ref"] = constraint["id"]
        execution = runtime["executions"]["EX-1"]
        original = profiles.resolve_profile(instance["execution_profiles"], execution["execution_profile_ref"])
        profile = profiles.with_host_resources(original, constraint,
            {"jobs": 1, "memory_bytes": 1024, "cpu_rate_basis_points": 1000})
        instance["execution_profiles"][profile["id"]] = profile
        from do_math.execution_lifecycle import create_execution
        from do_math.activities import assign_execution
        execution = create_execution(execution_id="EX-host", owner_activity_id="AT-1", actor_kind="machine",
            input_manifest={}, profile_ref=profiles.profile_ref(profile), created_at="2026-09-20T00:00:00Z")
        execution["role"] = profile["role"]
        assign_execution(runtime, "AT-1", execution)
        self.assertTrue(GitSessionSlots(runtime, instance).acquire("EX-host", profile["budget_kind"], None,
            profile=profile, execution=execution, current_time=100))
        head = self.repository.initialize(instance, runtime)
        _, saved, loaded = self.repository.load(head)
        self.assertEqual(loaded["executions"]["EX-host"]["capacity"]["provider"], None)
        self.assertEqual({row["unit"] for row in loaded["reservations"].values()},
                         {"jobs", "memory_bytes", "cpu_rate_basis_points"})
        for mutation in ("tampered_limit", "host_mismatch", "missing_authority"):
            broken = deepcopy(saved)
            if mutation == "tampered_limit": broken["capacity_constraints"][constraint["id"]]["memory_bytes"] += 1
            elif mutation == "missing_authority": broken["governance_sources"] = {}
            else:
                body = deepcopy(profile)
                body["host_resources"]["host_id"] = "other-host"
                bad = profiles.seal_profile(body)
                broken["execution_profiles"][bad["id"]] = bad
            with self.assertRaisesRegex(ValueError, "host|authority"):
                self.repository.validate_candidate(broken, loaded)

    def test_adopted_host_authoring_retains_shared_constraint_pointer(self):
        import platform
        from do_math import execution_profiles as profiles, governance
        instance, runtime = self._execution_state()
        source = governance.preserve_source("GS-host-config", "Explicit disposable host-policy test approval", origin="user")
        instance["governance_sources"] = {source["id"]: source}
        constraint = profiles.host_constraint(host_id=platform.node(),
            limits={"jobs": 3, "memory_bytes": 4096, "cpu_rate_basis_points": 8000},
            control_reserve={"jobs": 1, "memory_bytes": 1024, "cpu_rate_basis_points": 1000},
            authority_refs=[source["id"]])
        instance["config"]["host_resources"] = {"constraint": constraint, "demands_by_role": {
            role: {"jobs": 1, "memory_bytes": 1024, "cpu_rate_basis_points": 1000}
            for role in instance["role_profile_refs"]}}
        adopted = profiles.build_profiles(instance["config"])
        for family in ("execution_profiles", "capacity_constraints"):
            instance[family].update(adopted[family])
        instance["role_profile_refs"] = adopted["role_profile_refs"]
        instance["host_capacity_ref"] = adopted["host_capacity_ref"]
        head = self.repository.initialize(instance, runtime)
        _, saved, loaded = self.repository.load(head)
        self.assertEqual(saved["host_capacity_ref"], constraint["id"])
        self.assertEqual(saved["config"]["host_resources"], instance["config"]["host_resources"])
        saved["host_capacity_ref"] = "CP-absent"
        with self.assertRaises(ValueError): self.repository.validate_candidate(saved, loaded)

    def test_cleanup_scope_preserves_exact_user_request_and_execution_references(self):
        instance, runtime = self._execution_state()
        action = {"id": "AC-cleanup", "role": "maintenance", "requested_by": "UC-cleanup",
                  "cleanup_execution_ids": ["EX-1"]}
        runtime["queue"] = [action]
        runtime["history"] = [{"kind": "user_control", "request": {"id": "UC-cleanup", "origin": "user",
            "action": "request", "config": {"role": "maintenance", "cleanup_execution_ids": ["EX-1"]}}}]
        head = self.repository.initialize(instance, runtime)
        _, saved, loaded = self.repository.load(head)
        self.assertEqual(loaded["queue"][0], action)
        for change in ("missing_execution", "different_request", "not_user", "wrong_role"):
            broken = deepcopy(loaded)
            if change == "missing_execution": broken["queue"][0]["cleanup_execution_ids"] = ["EX-absent"]
            elif change == "different_request": broken["history"][0]["request"]["config"]["cleanup_execution_ids"] = []
            elif change == "not_user": broken["history"][0]["request"]["origin"] = "engine"
            else: broken["queue"][0]["role"] = "research_work"
            with self.assertRaisesRegex(ValueError, "cleanup"):
                self.repository.validate_candidate(saved, broken)

    def test_failed_execution_wait_preserves_actual_failure_and_snapshot(self):
        instance, runtime = self._execution_state()
        action = {"id": "AC-failed", "role": "formal_check"}
        runtime["waiting_actions"] = {action["id"]: {"action": action, "kind": "execution_failure",
            "failure_kind": "execution_failure", "reason": None, "execution_id": "EX-1", "input_snapshot": "a" * 40}}
        head = self.repository.initialize(instance, runtime)
        _, instance, loaded = self.repository.load(head)
        self.assertEqual(loaded["waiting_actions"], runtime["waiting_actions"])
        loaded["waiting_actions"][action["id"]]["execution_id"] = "EX-missing"
        with self.assertRaisesRegex(ValueError, "waiting action reference"):
            self.repository.validate_candidate(instance, loaded)

    def test_actual_execution_window_preserves_integer_measurement_and_owner(self):
        from do_math.execution_window import publish
        instance, runtime = self._execution_state()
        work = self.repository_path / "window"
        work.mkdir()
        window = publish(work, "EX-1", 12.75, instance["config"], "operations",
            deadline_source="operational_call", clock=lambda: 12.0)
        runtime["executions"]["EX-1"]["execution_window"] = window
        # Same values written by ENGINE's should_stop callback; the lifecycle
        # owner still controls the independent execution status/stop-phase axes.
        from do_math.execution_lifecycle import transition_execution
        execution = runtime["executions"]["EX-1"]
        for status in ("starting", "running"):
            transition_execution(execution, status, at="2026-09-20T00:00:00Z")
        execution.update(stop_reason="submission_intent", stop_observed_at="2026-09-20T00:00:01Z")
        transition_execution(execution, "stopping", at="2026-09-20T00:00:01Z", stop_phase="terminating")
        head = self.repository.initialize(instance, runtime)
        _, saved, loaded = self.repository.load(head)
        self.assertEqual(loaded["executions"]["EX-1"]["execution_window"]["remaining_ms_at_start"], 750)
        loaded["executions"]["EX-1"]["execution_window"]["execution_id"] = "EX-other"
        with self.assertRaisesRegex(ValueError, "execution window"):
            self.repository.validate_candidate(saved, loaded)

    def test_checkpoint_observation_evidence_uses_actual_same_cas_bytes(self):
        from do_math.observations import recovered_checkpoint
        instance, runtime = self._execution_state()
        head = self.repository.initialize(instance, runtime)
        raw = b'{"type":"public_message","message":"observed"}\n'
        reference = "runtime/artifacts/BA-observation/provider-evidence/events.jsonl"
        checkpoint = recovered_checkpoint(self.repository_path / "missing-checkpoint")
        checkpoint.update(observation_sources=[{"artifact_ref": reference, "path": "events.jsonl",
            "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}],
            observation_evidence_complete=True, observation_evidence_omitted=[])
        runtime["checkpoints"] = {"EX-1": checkpoint}
        with self.assertRaisesRegex(ValueError, "artifact evidence"):
            self.repository.validate_candidate(instance, runtime, head)
        head = self.repository.save(head, instance, runtime, artifacts={reference: raw})
        _, instance, loaded = self.repository.load(head)
        self.assertEqual(loaded["checkpoints"]["EX-1"], checkpoint)
        for change in ("bytes", "omissions", "final"):
            broken = deepcopy(loaded)
            row = broken["checkpoints"]["EX-1"]
            if change == "bytes": row["observation_sources"][0]["bytes"] += 1
            elif change == "omissions": row["observation_evidence_omitted"] = [{"path": "missing", "reason": "read_error"}]
            else:
                row["final_observation"] = deepcopy(checkpoint)
                row["final_observation"]["observation_sources"][0]["sha256"] = "0" * 64
            with self.assertRaises(ValueError): self.repository.validate_candidate(instance, broken, head)

    def test_actual_submission_authority_revocation_round_trip(self):
        from do_math.execution_lifecycle import transition_execution, record_submission_intent
        instance, runtime = self._execution_state("maintenance")
        head = self.repository.initialize(instance, runtime)
        from v5_fixtures import sealed_maintenance_submission
        with tempfile.TemporaryDirectory() as workspace:
            intent, artifacts = sealed_maintenance_submission(workspace, "EX-1")
        execution = runtime["executions"]["EX-1"]
        for status in ("starting", "running"):
            transition_execution(execution, status, at="2026-09-20T00:00:00Z")
        record_submission_intent(execution, intent,
            {"id": "CT-submit", "kind": "submit_intent", "state": "accepted", "execution_id": "EX-1"},
            at="2026-09-20T00:00:01Z")
        head = self.repository.save(head, instance, runtime, artifacts=artifacts)
        _, instance, runtime = self.repository.load(head)
        self.assertEqual(runtime["executions"]["EX-1"]["authority_revocation"]["receipt_id"], "CT-submit")
        for field, value in (("receipt_id", "CT-other"), ("state", "rejected"), ("kind", "self_check")):
            broken = deepcopy(runtime)
            if field == "receipt_id": broken["executions"]["EX-1"]["authority_revocation"][field] = value
            else: broken["executions"]["EX-1"]["submission_receipt"][field] = value
            with self.assertRaisesRegex(ValueError, "revocation"):
                self.repository.validate_candidate(instance, broken)

    def test_actual_impact_request_has_closed_nested_plan_schema(self):
        from test_redesign_CONTRACTS import ImpactReviewTests
        from do_math.record_schemas.schemas import RECORDS
        from jsonschema import Draft202012Validator
        owner = ImpactReviewTests()
        owner.setUp()
        action = {"id": "AC-review", "role": "maintenance", "stage": "impact_review",
            "input_basis": {"impact_review": owner.request()}}
        validator = Draft202012Validator(RECORDS["queue"])
        validator.validate(action)
        instance, runtime = self._execution_state("research_work")
        instance.update(owner.instance)
        producer = runtime["executions"].pop("EX-1")
        producer["id"] = "EX-producer"
        runtime["executions"][producer["id"]] = producer
        runtime["activities"]["AT-1"]["assigned_execution_ids"] = [producer["id"]]
        runtime["queue"] = [deepcopy(action)]
        head = self.repository.initialize(instance, runtime)
        loaded = self.repository.load(head)[2]
        loaded["queue"][0]["input_basis"]["impact_review"]["plans"]["bundle"]["digest"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "plan hash"):
            self.repository.validate_candidate(instance, loaded)
        action["input_basis"]["impact_review"]["plans"]["bundle"]["unregistered"] = True
        with self.assertRaises(Exception): validator.validate(action)

    def test_actual_input_preparation_begin_and_cancel_round_trip(self):
        from do_math.execution_lifecycle import begin_preparation, end_preparation
        instance, runtime = self._execution_state()
        execution = runtime["executions"]["EX-1"]
        begin_preparation(execution, at="2026-09-20T00:00:00Z")
        head = self.repository.initialize(instance, runtime)
        _, instance, runtime = self.repository.load(head)
        end_preparation(runtime["executions"]["EX-1"], at="2026-09-20T00:01:00Z",
                        stage="packing", reason="input overflow", cancelled=True)
        head = self.repository.save(head, instance, runtime)
        saved = self.repository.load(head)[2]["executions"]["EX-1"]
        self.assertEqual(saved["outcome"], "cancelled")
        self.assertEqual(saved["input_preparation"]["reason"], "input overflow")
        runtime["executions"]["EX-1"]["input_preparation"]["unregistered"] = True
        with self.assertRaises(ValueError): self.repository.validate_candidate(instance, runtime)

    def test_task_input_invalidation_keeps_request_and_reason(self):
        from do_math.record_schemas.schemas import RECORDS
        from jsonschema import Draft202012Validator
        fields = RECORDS["tasks"]["properties"]
        for value in (False, True, "UC-source"):
            Draft202012Validator(fields["newinput"]).validate(value)
        Draft202012Validator(fields["assessment"]["properties"]["invalidated_reason"]).validate("Required source content changed")
        with self.assertRaises(Exception): Draft202012Validator(fields["newinput"]).validate(3)

    def test_actual_input_metrics_overflow_and_validity_basis_round_trip(self):
        from do_math.context_store import fit_context
        from do_math.contracts import prompt_metrics
        from do_math.knowledge import capture_basis
        instance, runtime = self._execution_state()
        execution = runtime["executions"]["EX-1"]
        execution["input_metrics"] = prompt_metrics("prompt", {"required": "body"}, {}, [])
        execution["validity_basis"] = capture_basis(instance, runtime, [])
        fitted = fit_context({"required": "body" * 50}, max_bytes=10,
            workspace=self.repository_path / "overflow", mandatory_keys=["required"], role="research_plan",
            profile_id=execution["execution_profile_ref"]["id"], activity_id="AT-1")
        runtime["queue"] = [{"id": "AC-overflow", "role": "research_plan",
            "input_overflow": fitted["overflow"], "overflow_activity_id": "AT-1"}]
        head = self.repository.initialize(instance, runtime)
        loaded = self.repository.load(head)[2]
        self.assertEqual(loaded["executions"]["EX-1"]["validity_basis"], [])
        self.assertEqual(loaded["queue"][0]["input_overflow"], fitted["overflow"])
        runtime["queue"][0]["input_overflow"]["unregistered"] = True
        with self.assertRaises(ValueError): self.repository.validate_candidate(instance, runtime)

    def test_scoped_external_operation_keeps_actual_producer_fields(self):
        from do_math.external import prepare_operation
        from do_math.record_schemas.schemas import RECORDS
        from jsonschema import Draft202012Validator
        row = prepare_operation({"method": "POST", "url": "https://example.test/action"}, "GR-1", "SO-1",
            target_id="TK-1", purpose="publish", subject="result", budget_kind="operations", actor_kind="ai")
        Draft202012Validator(RECORDS["external_operations"]).validate(row)
        with self.assertRaises(Exception):
            Draft202012Validator(RECORDS["external_operations"]).validate({**row, "unregistered_scope": True})

    def test_queue_preserves_actual_model_selection_producer(self):
        from do_math.model_policy import selection
        instance, runtime = self._execution_state("research_plan")
        runtime["queue"] = [{"id": "AC-plan", "role": "research_plan"}]
        action = runtime["queue"][0]
        action["model_selection"] = selection(instance["config"], action, {}, {}, profiles=instance["execution_profiles"])
        head = self.repository.initialize(instance, runtime)
        loaded = self.repository.load(head)[2]
        self.assertEqual(loaded["queue"][0]["model_selection"], action["model_selection"])
        wrong = deepcopy(loaded)
        wrong["queue"][0]["model_selection"]["profile_ref"]["sha256"] = "0" * 64
        with self.assertRaises(ValueError): self.repository.validate_candidate(instance, wrong)

    def test_flat_governance_is_not_a_second_storage_authority(self):
        with self.assertRaisesRegex(ValueError, "unregistered|unknown"):
            self.repository.validate_candidate({"feature_version": 5, "goal": "parallel authority"}, {"feature_version": 5})

    def test_actual_external_uncertainty_reconciliation_and_retry_round_trip(self):
        from do_math import governance as gov, external
        instance = self._approved_governance()
        source_id = next(iter(instance["governance_sources"]))
        instance, runtime, _ = gov.apply_decision(instance, {"feature_version": 5, "queue": [], "history": []},
            {"kind": "grant", "grant": {"id": "GR-http", "kind": "http", "reuse": "reusable",
             "allowed_origins": ["https://example.test"], "allowed_methods": ["POST"], "allowed_path_prefixes": ["/"]}},
            source_ref=source_id)
        operation = external.prepare_operation({"method": "POST", "url": "https://example.test/action"}, "GR-http", source_id)
        # Domain requests acquire durable IDs at the lifecycle application
        # boundary; this focused external-ledger fixture supplies that identity.
        from do_math.repository import new_id
        for action in runtime["queue"]:
            action.setdefault("id", new_id("AC"))
            action.setdefault("lineage_id", action["id"])
        runtime["external_operations"] = {operation["id"]: operation}
        head = self.repository.initialize(instance, runtime)
        def persist(row):
            nonlocal head
            runtime["external_operations"][row["id"]] = deepcopy(row)
            head = self.repository.save(head, instance, runtime)
            self.assertEqual(self.repository.load(head)[2]["external_operations"][row["id"]], row)
        unknown = external.execute_operation(operation, instance["grants"]["GR-http"], persist=persist,
            transport=lambda *_: {"http_status": 503, "body": b"uncertain"}, runtime=runtime)
        self.assertEqual(unknown["status"], "unknown")
        proof = {"operation_id": operation["id"], "request_sha256": operation["request_sha256"],
            "idempotency_key": operation["idempotency_key"], "evidence_ref": "synthetic-remote-receipt",
            "observed_at": "2026-09-20T00:00:00Z", "fact": "effect_absent"}
        absent = external.reconcile_operation(unknown, proof, "failed", source="user", effect_absent=True)
        persist(absent)
        retry = external.prepare_retry(absent, {"kind": "effect_absent", "request_sha256": operation["request_sha256"],
            "idempotency_key": operation["idempotency_key"], "evidence_ref": proof["evidence_ref"]}, source="user")
        persist(retry)
        self.assertEqual(self.repository.load(head)[2]["external_operations"][operation["id"]]["previous_outcome"], "failed")

    def test_actual_plan_disposition_and_repetition_request_round_trip(self):
        from do_math.decision_engine import DecisionEngineMixin
        from v5_fixtures import candidate, disposition
        instance, runtime = self._execution_state("research_plan")
        task = {**candidate(), "id": "TK-1", "revision": 1, "status": "planned"}
        task.pop("revises_task_id")
        runtime["tasks"] = {task["id"]: task}
        engine = DecisionEngineMixin()
        engine.instance, engine.runtime = instance, runtime
        output = {"dispositions": [disposition(task["id"], kind="not_selected")],
                  "task_assessments": [], "preparation_requests": ["Refine the contract"]}
        output["dispositions"][0]["revisit"]["at"] = "2026-09-21T00:00:00Z"
        output["dispositions"][0]["uncertainty"] = "Contract refinement remains"
        engine._apply_task_plan(output, "EX-1", deepcopy(runtime["tasks"]), [task["id"]])
        head = self.repository.initialize(engine.instance, engine.runtime)
        _, _, loaded = self.repository.load(head)
        self.assertEqual(loaded["tasks"][task["id"]]["selection_disposition"]["execution_id"], "EX-1")
        self.assertEqual(loaded["queue"][0]["requested_by"], "EX-1")

    def test_candidate_rebuilds_only_declared_derived_views_without_mutating_caller(self):
        instance, runtime = self._execution_state()
        runtime["task_readiness"] = {"obsolete": {}}
        candidate = self.repository.validate_candidate(instance, runtime)
        self.assertEqual(candidate["runtime"]["task_readiness"], {})
        self.assertEqual(runtime["task_readiness"], {"obsolete": {}})

    def test_configure_preserves_selected_profile_edition_not_all_historical_editions(self):
        from do_math.execution_profiles import build_profiles
        instance, runtime = self._execution_state()
        old_ref = runtime["executions"]["EX-1"]["execution_profile_ref"]
        instance["config"]["call_timeout_seconds"] += 1
        editions = build_profiles(instance["config"])
        instance["execution_profiles"].update(editions["execution_profiles"])
        instance["capacity_constraints"].update(editions["capacity_constraints"])
        instance["role_profile_refs"] = editions["role_profile_refs"]
        checked = self.repository.validate_candidate(instance, runtime)
        self.assertEqual(checked["instance"]["role_profile_refs"], editions["role_profile_refs"])
        self.assertIn(old_ref["id"], checked["instance"]["execution_profiles"])
        head = self.repository.initialize(instance, runtime)
        self.assertEqual(self.repository.load(head)[1]["role_profile_refs"], editions["role_profile_refs"])
        bad = deepcopy(instance)
        selected_role = next(iter(bad["role_profile_refs"]))
        bad["role_profile_refs"][selected_role][0]["sha256"] = "0" * 64
        with self.assertRaises(ValueError):
            self.repository.validate_candidate(bad, runtime)

    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.repository_path = Path(self.temporary.name) / "repository"
        self.repository_path.mkdir()
        subprocess.run(["git", "-C", str(self.repository_path), "init", "-q"], check=True)
        self.repository = ResearchRepository(self.repository_path, INSTANCE_ID)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_version_five_persists_family_files_and_reconstructs_views(self) -> None:
        instance = {"feature_version": 5, "sources": [{"id": "SO-01", "path": "runtime/artifacts/input/source.txt", "sha256": "a" * 64}]}
        runtime = {"feature_version": 5, "events": [{"id": "EV-01", "kind": "created"}]}

        head = self.repository.initialize(instance, runtime)

        loaded = self.repository.load(head)
        self.assertEqual(loaded[1]["sources"], instance["sources"])
        self.assertEqual(loaded[2]["events"][0]["event_seq"], 1)
        files = self.repository.list_files("research/", head) + self.repository.list_files("runtime/", head)
        self.assertIn("research/sources/SO-01.json", files)
        self.assertIn("runtime/events/EV-01.json", files)
        self.assertNotIn("research/instance.json", files)
        self.assertNotIn("runtime/state.json", files)

    def test_save_rejects_global_identifier_collision_and_missing_reference(self) -> None:
        instance = {"feature_version": 5, "sources": [{"id": "SO-01", "path": "input.txt", "sha256": "a" * 64}]}
        runtime = {"feature_version": 5}
        head = self.repository.initialize(instance, runtime)

        collision = {"feature_version": 5, "events": [{"id": "SO-01", "kind": "created"}]}
        with self.assertRaisesRegex(ValueError, "globally unique"):
            self.repository.save(head, instance, collision)

        contract = StateContract.default()
        contract.register_family(
            "runtime",
            "links",
            schema={"type": "object", "properties": {"id": {"type": "string"}, "target_id": {"type": "string"}}, "required": ["id", "target_id"], "additionalProperties": False},
            references=lambda record: [record["target_id"]],
        )
        repository = ResearchRepository(self.repository_path, "RI-01ARZ3NDEKTSV4RRFFQ69G5FAW", contract=contract)
        with self.assertRaisesRegex(ValueError, "unknown record"):
            repository.initialize(
                {"feature_version": STATE_FORMAT_VERSION},
                {"feature_version": STATE_FORMAT_VERSION, "links": {"LK-01": {"id": "LK-01", "target_id": "missing"}}},
            )

    def test_byte_and_semantic_hashes_are_explicitly_distinct(self) -> None:
        record = {"id": "KN-01", "statement": "one", "updated_at": "2026-09-20T00:00:00Z"}

        self.assertEqual(hashlib.sha256(canonical_json(record)).hexdigest(), semantic_content_hash(record))
        self.assertNotEqual(
            semantic_content_hash(record, projection=("id", "statement")),
            semantic_content_hash(record),
        )

    def test_public_events_receive_contiguous_sequence_at_publish_boundary(self) -> None:
        _, runtime = EventPublisher.prepare(
            {"feature_version": STATE_FORMAT_VERSION},
            {"feature_version": STATE_FORMAT_VERSION, "events": {
                "EV-01": {"id": "EV-01", "kind": "created"},
                "EV-02": {"id": "EV-02", "kind": "queued"},
            }},
            parent_last_seq=7,
        )

        self.assertEqual([runtime["events"][event_id]["event_seq"] for event_id in ("EV-01", "EV-02")], [8, 9])
        self.assertEqual(runtime["event_cursor"], 9)

    def test_republication_keeps_prior_event_sequence_and_only_numbers_new_events(self) -> None:
        _, runtime = EventPublisher.prepare(
            {"feature_version": STATE_FORMAT_VERSION},
            {"feature_version": STATE_FORMAT_VERSION, "events": {
                "EV-01": {"id": "EV-01", "event_seq": 8, "kind": "created"},
                "EV-02": {"id": "EV-02", "kind": "queued"},
            }},
            parent_last_seq=8,
        )

        self.assertEqual(runtime["events"]["EV-01"]["event_seq"], 8)
        self.assertEqual(runtime["events"]["EV-02"]["event_seq"], 9)

    def test_canonical_json_rejects_float_and_keeps_distinct_unicode_keys(self) -> None:
        with self.assertRaisesRegex(ValueError, "floating-point"):
            canonical_json({"ratio": 1.0})
        self.assertEqual(json.loads(canonical_json({"K": 1, "K": 2})), {"K": 1, "K": 2})

    def test_unknown_family_and_malformed_map_do_not_become_singletons(self):
        for state in ({"unregistered_records": {}}, {"knowledge": {"KN-1": {"id": "KN-2"}}}):
            with self.subTest(state=state), self.assertRaises(ValueError):
                self.repository.initialize({"feature_version": 5, **state}, {"feature_version": 5})

    def test_list_record_validation_cannot_be_bypassed(self):
        with self.assertRaises(ValueError):
            self.repository.initialize({"feature_version": 5, "relations": [
                {"id": "RL-1", "kind": "supports", "source": "absent", "target": "absent"}]}, {"feature_version": 5})

    def test_save_and_cas_failure_do_not_mutate_caller(self):
        instance, runtime = {"feature_version": 5}, {"feature_version": 5, "events": [{"id": "EV-1", "kind": "created"}]}
        original = deepcopy((instance, runtime))
        with patch.object(self.repository._store, "publish", side_effect=GitStateStoreConflict("race")):
            with self.assertRaises(GitStateStoreConflict):
                self.repository.initialize(instance, runtime)
        self.assertEqual((instance, runtime), original)

    def test_published_event_content_is_immutable_and_retry_uses_parent(self):
        instance, runtime = {"feature_version": 5}, {"feature_version": 5, "events": [{"id": "EV-1", "kind": "created"}]}
        head = self.repository.initialize(instance, runtime)
        _, instance, runtime = self.repository.load(head)
        runtime["events"][0]["kind"] = "rewritten"
        with self.assertRaisesRegex(ValueError, "content cannot be rewritten"):
            self.repository.save(head, instance, runtime)

    def test_public_candidate_and_record_evidence_apis_exist(self):
        for name in ("validate_candidate", "records", "read_record"):
            self.assertTrue(callable(getattr(self.repository, name, None)), name)

    def test_real_event_storage_retry_removal_and_order(self):
        instance, runtime = {"feature_version": 5}, {"feature_version": 5, "events": [{"id": "EV-1", "kind": "created"}]}
        head = self.repository.initialize(instance, runtime)
        _, instance, runtime = self.repository.load(head)
        runtime["events"].append({"id": "EV-2", "kind": "queued"})
        before = deepcopy((instance, runtime))
        with patch.object(self.repository._store, "publish", side_effect=GitStateStoreConflict("late race")):
            with self.assertRaises(GitStateStoreConflict):
                self.repository.save(head, instance, runtime)
        self.assertEqual((instance, runtime), before)
        next_head = self.repository.save(head, instance, runtime)
        _, instance, runtime = self.repository.load(next_head)
        self.assertEqual([e["event_seq"] for e in runtime["events"]], [1, 2])
        retry = self.repository.save(next_head, instance, runtime)
        self.assertEqual(self.repository.load(retry)[2]["events"], runtime["events"])
        runtime["events"].reverse()
        with self.assertRaisesRegex(ValueError, "order"):
            self.repository.save(retry, instance, runtime)
        runtime["events"].clear()
        with self.assertRaisesRegex(ValueError, "removed"):
            self.repository.save(retry, instance, runtime)

    def test_empty_family_and_list_order_round_trip_and_runtime_oid(self):
        instance = {"feature_version": 5, "knowledge": {}, "sources": []}
        runtime = {"feature_version": 5, "events": []}
        head = self.repository.initialize(instance, runtime)
        first = self.repository._store.read_snapshot()
        runtime["events"] = [{"id": "EV-Z", "kind": "first"}, {"id": "EV-A", "kind": "second"}]
        next_head = self.repository.save(head, instance, runtime)
        self.assertEqual(self.repository._store.read_snapshot().research_tree, first.research_tree)
        _, loaded, state = self.repository.load(next_head)
        self.assertEqual(loaded["knowledge"], {})
        self.assertEqual(loaded["sources"], [])
        self.assertEqual([r["id"] for r in state["events"]], ["EV-Z", "EV-A"])

    def test_exact_record_evidence_and_corrupt_record_rejected_on_load(self):
        instance = {"feature_version": 5, "sources": [{"id": "SO-1", "path": "input.txt", "sha256": "a" * 64}]}
        head = self.repository.initialize(instance, {"feature_version": 5})
        descriptor = self.repository.read_record("SO-1", head)
        raw = self.repository.read(descriptor["path"], head)
        self.assertEqual(raw, descriptor["bytes"])
        self.assertEqual(hashlib.sha256(raw).hexdigest(), descriptor["sha256"])
        import json
        tampered = json.loads(raw)
        tampered["record"]["unknown_authority"] = True
        bad = self.repository._store.publish(head, {descriptor["path"]: canonical_json(tampered)}).head
        with self.assertRaisesRegex(ValueError, "Additional properties"):
            self.repository.load(bad)

    def test_pure_validation_rejects_duplicate_list_ids_and_unknown_record_fields(self):
        row = {"id": "SO-1", "path": "input.txt", "sha256": "a" * 64}
        for rows in ([row, row], [{**row, "mystery": True}]):
            with self.subTest(rows=rows), self.assertRaises(ValueError):
                self.repository.validate_candidate({"feature_version": 5, "sources": rows}, {"feature_version": 5})
        self.assertIsNone(self.repository._store.read_snapshot().head)

    def test_storage_object_format_and_contract_versions_are_enforced(self):
        head = self.repository.initialize({"feature_version": 5}, {"feature_version": 5})
        _, instance, runtime = self.repository.load(head)
        instance["object_format"] = "sha256"
        with self.assertRaisesRegex(ValueError, "object_format"):
            self.repository.save(head, instance, runtime)
        import json
        path = "research/_state/manifest.json"
        manifest = json.loads(self.repository.read(path, head))
        manifest["contract"]["sha256"] = "0" * 64
        bad = self.repository._store.publish(head, {path: canonical_json(manifest)}).head
        self.repository.load(bad)  # Same edition is checked against current values and layout.
        manifest["contract"]["schema_version"] += 1
        incompatible = self.repository._store.publish(bad, {path: canonical_json(manifest)}).head
        with self.assertRaisesRegex(ValueError, "contract/schema"):
            self.repository.load(incompatible)

    def test_transport_decimals_do_not_relax_storage(self):
        self.assertIn(b"1.25", transport_json({"seconds": 1.25}))
        with self.assertRaises(ValueError):
            canonical_json({"seconds": 1.25})
        with self.assertRaises(ValueError):
            transport_json({"seconds": float("nan")})
        self.assertEqual(canonical_json({"a": [2, 1]}), canonical_json({"a": [2, 1]}))
        self.assertNotEqual(canonical_json({"a": [2, 1]}), canonical_json({"a": [1, 2]}))

    def test_pending_event_references_remain_unconsumed_after_publication(self):
        instance = {"feature_version": 5}
        runtime = {"feature_version": 5, "events": [{"id": "EV-1", "kind": "created"}], "pending_events": ["EV-1"]}
        head = self.repository.initialize(instance, runtime)
        _, instance, runtime = self.repository.load(head)
        self.assertEqual(runtime["pending_events"], ["EV-1"])
        runtime["pending_events"] = ["EV-missing"]
        with self.assertRaises(ValueError):
            self.repository.save(head, instance, runtime)

    def test_load_rejects_removed_required_contract_field(self):
        import json
        head = self.repository.initialize({"feature_version": 5}, {"feature_version": 5})
        path = "runtime/_state/manifest.json"
        manifest = json.loads(self.repository.read(path, head))
        del manifest["containers"]["feature_version"]
        bad = self.repository._store.publish(head, {path: canonical_json(manifest), "runtime/feature_version/state.json": None}).head
        with self.assertRaisesRegex(ValueError, "feature_version"):
            self.repository.load(bad)

    def test_current_lifecycle_empty_families_are_registered(self):
        names = ("trust_transitions", "conversations", "checkpoints", "observations", "condition_states", "extended_controls")
        result = self.repository.validate_candidate({"feature_version": 5}, {"feature_version": 5, **{name: {} for name in names}})
        self.assertTrue(result["valid"])

    def _execution_state(self, role="formal_check"):
        from do_math.engine import DEFAULT_CONFIG
        from do_math.execution_profiles import build_profiles, profile_ref
        from do_math.activities import open_activity, assign_execution
        from do_math.execution_lifecycle import create_execution
        instance = {"feature_version": 5, "config": deepcopy(DEFAULT_CONFIG), **build_profiles(DEFAULT_CONFIG)}
        profile = next(p for p in instance["execution_profiles"].values() if p["role"] == role)
        runtime = {"feature_version": 5, "executions": {}}
        open_activity(runtime, activity_id="AT-1", activity_kind="formal_check", owner_ref="engine", input_refs=[], opened_at="2026-09-20T00:00:00Z")
        execution = create_execution(execution_id="EX-1", owner_activity_id="AT-1", actor_kind=profile["actor_kind"], input_manifest={}, profile_ref=profile_ref(profile), created_at="2026-09-20T00:00:00Z")
        execution["role"] = role
        assign_execution(runtime, "AT-1", execution)
        return instance, runtime

    def test_academic_resolution_accepts_only_resolved_sealed_artifact_evidence(self):
        from do_math import academic
        instance, runtime = self._execution_state("research_plan")
        instance.update(self._approved_governance())
        basis = {"goal_ref": "CH-1", "records": []}
        runtime["executions"]["EX-1"].update(role="research_plan", input_solution_basis=basis)
        runtime["external_rejections"] = [{"id": "RJ-1", "actor": "reviewer", "text": "objection",
            "source_ref": "input", "solution_basis": basis, "resolved": False}]
        head = self.repository.initialize(instance, runtime)
        path = "runtime/artifacts/BA-1/reply.txt"
        raw = b"preserved answer"
        academic.record_resolution(instance, runtime, basis, {"id": "RJ-1", "decision": "resolved",
            "evidence": "verified reply", "evidence_refs": [path]}, execution_id="EX-1",
            resolve_evidence=lambda ref: raw if ref == path else None)
        with self.assertRaisesRegex(ValueError, "artifact evidence"):
            self.repository.validate_candidate(instance, runtime, head)
        saved = self.repository.save(head, instance, runtime, artifacts={path: raw})
        _, instance, runtime = self.repository.load(saved)
        self.assertEqual(runtime["academic_resolution_records"][0]["evidence_hashes"][path], hashlib.sha256(raw).hexdigest())
        broken = deepcopy(runtime)
        row = broken["academic_resolution_records"][0]
        row["evidence_hashes"][path] = "0" * 64
        row["sha256"] = academic._hash({k: v for k, v in row.items() if k != "sha256"})
        with self.assertRaisesRegex(ValueError, "artifact evidence"):
            self.repository.validate_candidate(instance, broken, saved)

    def test_academic_assessment_binds_declared_task_assessment_hash(self):
        import jsonschema
        schema = self.repository.contract.family("runtime", "academic_assessments").schema
        row = {"requirement_id": "R-1", "solution_basis": {"goal_ref": "CH-1", "records": []},
            "requirements_sha256": "a" * 64, "decision": "unresolved", "evidence": [],
            "assessor": "research_plan", "execution_id": "EX-1", "task_id": "TK-1",
            "task_assessment_sha256": "b" * 64}
        jsonschema.validate([row], schema)
        row["task_assessment_sha256"] = "not-a-hash"
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate([row], schema)

    def test_task_dependencies_resolve_tasks_or_existing_knowledge(self):
        from do_math.knowledge_io import ensure_ontology
        from do_math.knowledge_records import create_candidate
        instance = ensure_ontology({"feature_version": 5})
        instance, kid = create_candidate(instance, {"kind": "observation", "statement": "prior result",
            "dependencies": []}, source_ref="input", actor_ref="user")
        task = {"id": "TK-1", "revision": 1, "question": "Check this result", "status": "planned",
            "scope": {"included": ["result"], "excluded": []},
            "expected": {"outputs": ["assessment"], "research_change": "Check result"},
            "progress_criteria": [{"id": "p", "claim": "gather evidence"}],
            "completion_obligations": [{"id": "o", "claim": "assess result", "judges": ["research_plan"]}],
            "dependencies": [kid]}
        runtime = {"feature_version": 5, "tasks": {task["id"]: task}}
        self.repository.validate_candidate(instance, runtime)
        task["dependencies"] = ["K-missing"]
        with self.assertRaisesRegex(ValueError, "unknown record"):
            self.repository.validate_candidate(instance, runtime)

    def test_actual_profiles_activities_and_observation_producers(self):
        from do_math.observations import ObservationTracker
        instance, runtime = self._execution_state()
        tracker = ObservationTracker("EX-1", self.repository_path, {"observation_mode": "deadline_only"}, clock=lambda: 1.25)
        fact = tracker._fact("observation_fact", {"type": "provider_report", "cost": 0.125}, 1.5)
        runtime["observation_facts"] = {fact["id"]: fact}
        head = self.repository.initialize(instance, runtime)
        _, saved, state = self.repository.load(head)
        self.assertEqual(state["observation_facts"][fact["id"]], fact)
        self.assertEqual(saved["role_profile_refs"], instance["role_profile_refs"])
        self.assertIn("research/role_profile_refs/state.json", self.repository.list_files("research/", head))
        selection = next(row for row in self.repository.records(head, family="role_profile_refs"))
        self.assertTrue(all(set(ref) == {"id", "revision", "sha256"} for refs in selection["record"].values() for ref in refs))
        broken = deepcopy(state)
        broken["executions"]["EX-1"]["execution_profile_ref"]["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "profile"):
            self.repository.validate_candidate(saved, broken, head)
        broken = deepcopy(state)
        broken["observation_facts"][fact["id"]]["event_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "event.*hash"):
            self.repository.validate_candidate(saved, broken, head)

    def _approved_governance(self):
        from do_math import governance as gov
        record = {"id": "CH-1", "kind": "charter", "revision": 1, "supersedes": [], "content": {
            "rationale": "Study P", "goal": "Prove P", "desired_result": "Proof", "success_criteria": ["P proved"],
            "partial_success_criteria": [], "included_scope": ["P"], "excluded_scope": [], "priorities": [],
            "preferences": [], "evidence_boundary": "proof", "academic_requirements": [], "decision_authority": "user", "stop_conditions": []}}
        source = gov.preserve_source("GS-1", "Study P", origin="user")
        approval = {"id": "DC-1", "actor": "user", "source_ref": source["id"], "source_sha256": source["sha256"], "record_hashes": {record["id"]: gov.digest(record)}}
        instance = gov.initialize_governance({"id": INSTANCE_ID, "feature_version": 5}, source, approval, [record])
        return instance

    def test_governance_actual_approval_and_semantics(self):
        from do_math import governance as gov
        instance = self._approved_governance()
        head = self.repository.initialize(instance, {"feature_version": 5})
        _, instance, runtime = self.repository.load(head)
        self.assertEqual(gov.governance_view(instance)["goal"], "Prove P")
        instance["governance"]["CH-1"]["content"]["goal"] = "Something else"
        with self.assertRaisesRegex(ValueError, "approved proposal"):
            self.repository.validate_candidate(instance, runtime, head)

    def test_registration_requires_closed_schema_and_runs_repeated_owner_checker(self):
        contract = StateContract.default()
        for schema in (None, {"type": "object"}):
            with self.assertRaises(ValueError):
                contract.register_family("runtime", "unknown", schema=schema)
        def reject(_):
            raise ValueError("owner checker invoked")
        contract.register_family("research", "sources", shape="list", validator=reject)
        repository = ResearchRepository(self.repository_path, "RI-01ARZ3NDEKTSV4RRFFQ69G5FAW", contract=contract)
        with self.assertRaisesRegex(ValueError, "owner checker invoked"):
            repository.validate_candidate({"feature_version": 5, "sources": [{"id": "SO-1", "path": "x", "sha256": "a" * 64}]}, {"feature_version": 5})

    def test_real_stale_cas_retry_keeps_pending_obligations_and_caller(self):
        head = self.repository.initialize({"feature_version": 5}, {"feature_version": 5, "events": [{"id": "EV-1", "kind": "first"}], "pending_events": ["EV-1"]})
        _, instance, winner = self.repository.load(head)
        loser = deepcopy(winner)
        winner["events"].append({"id": "EV-2", "kind": "winner"})
        accepted = self.repository.save(head, instance, winner)
        loser["events"].append({"id": "EV-3", "kind": "retry"})
        before = deepcopy((instance, loser))
        with self.assertRaises(GitStateStoreConflict):
            self.repository.save(head, instance, loser)
        self.assertEqual((instance, loser), before)
        _, instance, retry = self.repository.load(accepted)
        retry["events"].append(loser["events"][-1])
        final = self.repository.save(accepted, instance, retry)
        saved = self.repository.load(final)[2]
        self.assertEqual([r["event_seq"] for r in saved["events"]], [1, 2, 3])
        self.assertEqual(saved["pending_events"], ["EV-1"])

    def test_family_round_trip_on_sha256_repository(self):
        path = Path(self.temporary.name) / "sha256"
        path.mkdir()
        subprocess.run(["git", "-C", str(path), "init", "-q", "--object-format=sha256"], check=True)
        repository = ResearchRepository(path, INSTANCE_ID)
        head = repository.initialize({"feature_version": 5}, {"feature_version": 5})
        self.assertEqual(len(head), 64)
        self.assertEqual(repository.load(head)[1]["object_format"], "sha256")

    def test_identity_bearing_singleton_and_nonexecution_question(self):
        contract = StateContract.default()
        contract.register_family("research", "singleton_proof", shape="singleton", schema={
            "type": "object", "additionalProperties": False, "properties": {"id": {"type": "string"}, "claim": {"type": "string"}}, "required": ["id", "claim"]})
        repository = ResearchRepository(self.repository_path, "RI-01ARZ3NDEKTSV4RRFFQ69G5FAW", contract=contract)
        question = {"id": "QU-1", "origin_execution_id": None, "origin_field": "input_overflow/AC-1",
            "source_ref": "runtime/artifacts/BA-1/overflow.json", "owner": "user", "target_ids": ["SP-1"],
            "status": "open", "resolution_ref": None}
        head = repository.initialize({"feature_version": 5, "singleton_proof": {"id": "SP-1", "claim": "P"}},
            {"feature_version": 5, "question_links": [question]})
        self.assertEqual(repository.read_record("SP-1", head)["path"], "research/singleton_proof/SP-1.json")
        self.assertIsNone(repository.load(head)[2]["question_links"][0]["origin_execution_id"])

    def test_question_target_can_be_a_preserved_waiting_action_coordinate(self):
        runtime = {"feature_version": 5, "waiting_actions": {"AC-1": {
            "action": {"id": "AC-1", "role": "research_plan"}, "reason": "input_overflow", "question_id": "QU-1"}},
            "question_links": [{"id": "QU-1", "origin_execution_id": None, "origin_field": "input_overflow/AC-1",
                "source_ref": "archived-overflow", "owner": "user", "target_ids": ["AC-1"], "status": "open", "resolution_ref": None}]}
        self.repository.validate_candidate({"feature_version": 5}, runtime)
        runtime["question_links"][0]["target_ids"] = ["AC-absent"]
        with self.assertRaisesRegex(ValueError, "question target"):
            self.repository.validate_candidate({"feature_version": 5}, runtime)

    def test_resolved_question_preserves_a_historical_action_coordinate(self):
        runtime = {"feature_version": 5, "waiting_actions": {},
            "question_links": [{"id": "QU-1", "origin_execution_id": None,
                "origin_field": "resolution_question/question", "source_ref": "archived-overflow",
                "owner": "user", "target_ids": ["AC-finished"], "unresolved_target_ids": [],
                "blocks": True, "status": "resolved", "resolution_ref": None}]}
        self.repository.validate_candidate({"feature_version": 5}, runtime)

    def test_relation_schema_and_domain_kind_evidence_are_both_enforced(self):
        from do_math import knowledge_io as io, knowledge_records as kr
        instance = io.ensure_ontology({"feature_version": 5})
        for text in ("one", "two"):
            instance, _ = kr.create_candidate(instance, {"kind": "observation", "statement": text, "dependencies": []}, source_ref="input", actor_ref="user")
        instance, _ = io.register_kind_definition(instance, {"family": "relation", "token": "supports", "meaning": "Research support", "constraints": {"requires_evidence": True}}, source_ref="source", actor_ref="author")
        instance = io.check_kind_definition(instance, "relation", "supports", check_ref="checked", actor_ref="checker")
        instance = io.activate_kind_definition(instance, "relation", "supports", approval_ref="approved", actor_ref="user")
        ids = list(instance["knowledge"])
        instance, relation_id = io.import_relation(instance, {"kind": "supports", "source": ids[0], "target": ids[1], "evidence": "input"}, source_ref="source", actor_ref="author")
        head = self.repository.initialize(instance, {"feature_version": 5})
        _, saved, runtime = self.repository.load(head)
        self.assertEqual(self.repository.read_record(relation_id, head)["family"], "relations")
        saved["relations"][0].pop("evidence")
        with self.assertRaisesRegex(ValueError, "evidence_required"):
            self.repository.validate_candidate(saved, runtime, head)

    def test_installed_initialization_and_knowledge_producers_round_trip(self):
        from do_math.initialization import initialize_state
        from do_math.knowledge_io import ensure_ontology
        from do_math.knowledge_records import create_candidate
        instance, runtime = initialize_state(instance_id=INSTANCE_ID, goal="question", goal_kind="mathematical",
            workspace=self.repository_path, config={}, source_input="question")
        instance = ensure_ontology(instance)
        instance, kid = create_candidate(instance, {"kind": "observation", "statement": "a bounded observation", "dependencies": []}, source_ref="user-input", actor_ref="user")
        head = self.repository.initialize(instance, runtime)
        _, loaded, _ = self.repository.load(head)
        self.assertEqual(loaded["knowledge"][kid], instance["knowledge"][kid])
        self.assertEqual(self.repository.read_record(kid, head)["family"], "knowledge")
        bad = deepcopy(loaded)
        bad["knowledge"][kid]["exposition_id"] = "XP-absent"
        with self.assertRaisesRegex(ValueError, "unknown record"):
            self.repository.save(head, bad, runtime)

    def test_complete_lifecycle_candidate_uses_installed_current_state_gate(self):
        from do_math.initialization import initialize_state
        instance, runtime = initialize_state(instance_id=INSTANCE_ID, goal="P", goal_kind="mathematical",
            workspace=self.repository_path, config={}, source_input="P")
        self.repository.validate_candidate(instance, runtime)
        runtime["status"] = "invented_status"
        with self.assertRaisesRegex(ValueError, "runtime_status"):
            self.repository.validate_candidate(instance, runtime)

    def test_original_input_bytes_are_the_exact_working_text(self):
        from do_math.initialization import initialize_state, original_input_bytes
        source = "e\u0301 original input"
        instance, runtime = initialize_state(instance_id=INSTANCE_ID, goal="P", goal_kind="mathematical",
            workspace=self.repository_path, config={}, source_input=source)
        original = instance["lifecycle"]["immutable_input"]
        self.assertEqual(original_input_bytes(original), source.encode("utf-8"))
        self.assertEqual(original["text"], source)
        original["sha256"] = "0" * 64
        with self.assertRaises(ValueError): self.repository.validate_candidate(instance, runtime)

    def test_initial_input_and_loaded_pending_event_references_are_checked(self):
        from do_math.initialization import initialize_state
        instance, runtime = initialize_state(instance_id=INSTANCE_ID, goal="P", goal_kind="mathematical",
            workspace=self.repository_path, config={}, source_input="P")
        runtime["inputs"] = []
        with self.assertRaisesRegex(ValueError, "unknown record"):
            self.repository.validate_candidate(instance, runtime)
        head = self.repository.initialize({"feature_version": 5}, {"feature_version": 5,
            "events": [{"id": "EV-1", "kind": "first"}], "pending_events": ["EV-1"]})
        import json
        path = "runtime/pending_events/state.json"
        value = json.loads(self.repository.read(path, head))
        value["record"] = ["EV-unknown"]
        bad = self.repository._store.publish(head, {path: canonical_json(value)}).head
        with self.assertRaisesRegex(ValueError, "unknown record"):
            self.repository.load(bad)

    def test_public_initialize_control_and_source_bound_grant_round_trip(self):
        from do_math.engine import initialize, ResearchEngine
        from v5_fixtures import send_control
        initialized = initialize(self.repository_path, goal="Preserve original request",
            workspace=self.repository_path / "work", config={"scholarly_enabled": False})
        engine = ResearchEngine(self.repository_path, initialized["instance_id"])
        send_control(engine, "decision", config={"change": {"kind": "grant", "grant": {
            "id": "GR-test", "kind": "local", "roles": ["maintenance"], "reuse": "reusable",
            "execution_kinds": ["ai"], "purposes": ["maintenance"], "subjects": ["maintenance"]}}})
        reloaded = ResearchEngine(self.repository_path, initialized["instance_id"])
        from do_math.governance import validate_grant_source
        grant = reloaded.instance["grants"]["GR-test"]
        validate_grant_source(reloaded.instance, grant)
        self.assertEqual(grant["subjects"], ["maintenance"])
        changed = deepcopy(reloaded.instance)
        changed["grants"]["GR-test"]["subjects"].append("unapproved publication")
        with self.assertRaisesRegex(ValueError, "approved scope"):
            reloaded.store.validate_candidate(changed, reloaded.runtime)
        send_control(reloaded, "request", text="Inspect this run", config={"role": "maintenance"})
        _, _, runtime = reloaded.store.load()
        self.assertTrue(any(row.get("requested_by") for row in runtime["queue"]))

    def test_public_initial_grant_adoption_preserves_exact_approved_scope(self):
        from do_math.engine import initialize, ResearchEngine
        from v5_fixtures import send_control
        from datetime import datetime, timedelta, timezone
        initialized = initialize(self.repository_path, goal="Check explicit initial grant adoption",
            workspace=self.repository_path / "initial-work", config={"scholarly_enabled": False})
        engine = ResearchEngine(self.repository_path, initialized["instance_id"])
        send_control(engine, "decision", config={"change": {"kind": "grant", "grant": {
            "id": "GR-initial", "kind": "local", "roles": ["intent_interpretation"],
            "budget_kind": "operations", "reuse": "reusable",
            "expires_at": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()}}})
        approved = deepcopy(engine.instance["grants"]["GR-initial"])
        send_control(engine, "decision", config={"change": {"kind": "initialization", "initial_grant_ids": ["GR-initial"]}})
        _, instance, runtime = engine.store.load()
        self.assertEqual(instance["grants"]["GR-initial"], approved)
        broken = deepcopy(instance)
        broken["grants"]["GR-initial"]["initialization_only"] = True
        with self.assertRaises(ValueError):
            engine.store.validate_candidate(broken, runtime)

    def test_public_trust_owner_flow_round_trip_requires_complete_manifest(self):
        from do_math.engine import initialize, ResearchEngine
        from do_math.initialization import trust_environment_errors
        from v5_fixtures import send_control, trust_fixture
        initialized = initialize(self.repository_path, goal="Check a synthetic environment contract",
            workspace=self.repository_path / "trust-work", config={"scholarly_enabled": False})
        engine = ResearchEngine(self.repository_path, initialized["instance_id"])
        # Real files/owner flow, synthetic toolchain bytes: this is not Lean evidence.
        config = trust_fixture(self.repository_path, ["synthetic-lean"])
        send_control(engine, "trust", config=config)
        eid = next(reversed(engine.instance["trust_environments"]))
        self.assertEqual(trust_environment_errors(engine.instance["trust_environments"][eid], verify_files=True), [])
        send_control(engine, "trust", config={"operation": "transition", "env_id": eid})
        engine._finish_trust_transition(next(reversed(engine.runtime["trust_transitions"])))
        engine._save()
        _, instance, runtime = engine.store.load()
        self.assertEqual(instance["active_trust_environment"], eid)
        broken = deepcopy(instance)
        broken["trust_environments"][eid]["manifest"] = {"validation": {"status": "verified", "evidence_refs": ["a claim"]}}
        with self.assertRaisesRegex(ValueError, "trust"):
            engine.store.validate_candidate(broken, runtime)

    def test_actual_repetition_binding_is_a_closed_queue_contract(self):
        from do_math.revisions import bind_repetition_bases
        instance = {"feature_version": 5}
        runtime = {"feature_version": 5, "tasks": {}, "queue": [{"id": "AC-repeat", "role": "research_plan"}]}
        action = runtime["queue"][0]
        bind_repetition_bases(instance, runtime, action)
        head = self.repository.initialize(instance, runtime)
        self.assertEqual(self.repository.load(head)[2]["queue"][0]["repetition_bases"], action["repetition_bases"])
        action["repetition_bases"]["invented_lineage"] = "a" * 64
        with self.assertRaises(ValueError):
            self.repository.validate_candidate(instance, runtime, head)

    def test_actual_uncertainty_text_and_object_preserve_wire_meaning(self):
        import jsonschema
        from do_math import submission, knowledge_io
        wire = submission.extension_schema({"role": "research_work"}, {})
        for value in ("Not a proof", {"claim": "Not a proof", "scope": "finite search only"}):
            jsonschema.validate({"knowledge_metadata": [{"title": "Bounded", "uncertainty_assessment": value}]}, wire)
            instance, runtime, kid = knowledge_io.import_candidate({"feature_version": 5}, {"feature_version": 5},
                {"kind": "observation", "title": "Bounded", "statement": "Finite search", "explanation": "Bounded search only",
                 "summary": "No proof", "lean_code": "", "declaration_names": [], "dependencies": [],
                 "uncertainty_assessment": value}, source_ref="input", actor_ref="user")
            checked = self.repository.validate_candidate(instance, runtime)
            self.assertEqual(checked["instance"]["knowledge"][kid]["uncertainty_assessment"], value)

    def test_scalar_metadata_is_one_closed_record_per_root(self):
        instance = {"feature_version": 5, "id": INSTANCE_ID, "title": "Title", "created_at": "2026-09-20T00:00:00Z"}
        runtime = {"feature_version": 5, "status": "ready", "cycles": 0}
        head = self.repository.initialize(instance, runtime)
        self.assertIn("research/_state/metadata.json", self.repository.list_files("research/", head))
        self.assertNotIn("research/title/state.json", self.repository.list_files("research/", head))
        self.assertEqual(self.repository.load(head)[1]["title"], "Title")
        rows = self.repository.records(head, family="metadata")
        self.assertEqual(len(rows), 2)
        self.assertTrue(all(row["sha256"] == hashlib.sha256(row["bytes"]).hexdigest() for row in rows))

    def _reviewed_candidate(self, *, verified=False):
        from do_math import knowledge_records as kr, knowledge_io, review_cycle as rc
        from do_math.review_engine import ReviewEngineMixin
        from do_math.review_policy import default_scope_assessment
        from do_math.execution_lifecycle import create_execution
        from do_math.activities import assign_execution
        instance, runtime = self._execution_state("identity_review")
        if verified:
            from test_lifecycle_engine import FakeEngine
            owner = FakeEngine(self.repository_path)
            eid = owner.environment("synthetic-base", active=True)
            instance["trust_environments"] = deepcopy(owner.instance["trust_environments"])
            instance["active_trust_environment"] = eid
            runtime["trust_transitions"] = deepcopy(owner.runtime["trust_transitions"])
        instance = knowledge_io.ensure_ontology(instance)
        instance, runtime, kid = knowledge_io.import_candidate(instance, runtime, {"kind": "theorem", "title": "Truth", "summary": "Truth",
            "statement": "True", "explanation": "Truth", "lean_code": "theorem t : True := True.intro",
            "declaration_names": ["t"], "dependencies": []}, source_ref="input", actor_ref="EX-1")
        if verified:
            from test_knowledge import evidence
            instance = kr.record_formal_result(instance, kid, evidence(instance, kid, eid), eid, runtime=runtime)
        cycle = rc.start_review({**kr.proposal_view(instance, kid), "revision": 1}, reviewers=1, max_rounds=1,
            owner_activity_id="AT-1")
        cycle.update(id="RC-1", knowledge_id=kid, identity_basis=kr.identity_basis(instance, kid),
            input_snapshot="a" * 40, producer_execution_ids=[], policy_ref="policy-test",
            slot_profiles={}, input_bindings={}, publication_premises={}, review_input_basis={})
        profile = runtime["executions"]["EX-1"]["execution_profile_ref"]
        for index in range(2):
            action = rc.next_actions(cycle)[0]
            eid = "EX-review-" + str(index)
            execution = create_execution(execution_id=eid, owner_activity_id="AT-1", actor_kind="ai",
                input_manifest={}, profile_ref=profile, created_at="2026-09-20T00:00:00Z")
            execution["role"] = "identity_review"
            assign_execution(runtime, "AT-1", execution)
            output = {"proposal_digest": cycle["proposal_digest"], "summary": "Synthetic reviewer output",
                "used_sources": ["proposal"], "questions": [], "scope_complete": verified or index == 0}
            if action["stage"] == "scope":
                scope = default_scope_assessment(cycle["review_policy"], ["initial-0"])
                scope["selected_profile_ref"] = profile
                output["scope_assessment"] = scope
            else:
                output.update(decision="match" if verified else "unresolved", findings=[])
            cycle = rc.accept_result(cycle, action, output, eid,
                input_manifest={"proposal_digest": cycle["proposal_digest"], "role_slot_id": action["slot"]})
        self.assertEqual(cycle["status"], "completed" if verified else "unresolved")
        runtime["review_cycles"] = {cycle["id"]: cycle}
        assessment = ReviewEngineMixin._identity_assessment(cycle, effective=False, reason="Scope remains incomplete")
        assessment["basis"] = kr.identity_basis(instance, kid)
        instance, aid = kr.record_identity_assessment(instance, kid, assessment, cycle["policy_ref"], runtime=runtime)
        return instance, runtime, kid, aid

    def test_actual_review_cycle_and_identity_producer_round_trip(self):
        instance, runtime, kid, aid = self._reviewed_candidate()
        cycle = runtime["review_cycles"]["RC-1"]
        head = self.repository.initialize(instance, runtime)
        _, saved, loaded = self.repository.load(head)
        self.assertEqual(saved["identity_assessments"][aid]["review_cycle_id"], "RC-1")
        self.assertEqual(loaded["review_cycles"]["RC-1"]["sealed"], cycle["sealed"])
        broken = deepcopy(loaded)
        broken["review_cycles"] = {}
        with self.assertRaisesRegex(ValueError, "unknown record"):
            self.repository.validate_candidate(saved, broken)

    def test_staged_review_producer_keeps_transient_candidate_and_real_transition(self):
        from test_lifecycle_engine import FakeEngine
        from test_knowledge import evidence
        from do_math import knowledge as k
        from do_math.review_engine import ReviewEngineMixin
        from do_math.review_policy import build_review_policy
        from do_math.repository import new_id
        instance, runtime, kid, _ = self._reviewed_candidate(verified=True)
        environment_owner = FakeEngine(self.repository_path)
        eid = environment_owner.environment("synthetic-staged")
        instance["trust_environments"][eid] = deepcopy(environment_owner.instance["trust_environments"][eid])
        instance["review_policy"] = build_review_policy(reviewer_count=1, max_rounds=1)
        transition = k.begin_transition(instance, eid)
        transition = k.record_transition_result(instance, transition, {"id": kid, **evidence(instance, kid, eid)})
        runtime["trust_transitions"][transition["id"]] = transition
        runtime.setdefault("queue", [])
        class Owner(ReviewEngineMixin):
            def _enqueue(self, role, target, **values):
                self.runtime["queue"].append({"id": new_id("AC"), "role": role, "target": target, **values})
        owner = Owner()
        owner.instance, owner.runtime, owner.head = instance, runtime, "a" * 40
        before = deepcopy(instance["formal_results"])
        cid = owner._start_staged_identity_review(transition["id"], kid)
        head = self.repository.initialize(instance, runtime)
        _, saved, loaded = self.repository.load(head)
        self.assertEqual(saved["formal_results"], before)
        self.assertEqual(loaded["review_cycles"][cid]["transition_id"], transition["id"])
        broken = deepcopy(loaded)
        broken["review_cycles"][cid]["staged_candidate"]["transition_basis"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "staged review"):
            self.repository.validate_candidate(saved, broken)

    def test_verified_identity_and_environment_continuity_round_trip(self):
        from test_lifecycle_engine import FakeEngine
        from test_knowledge import evidence
        from do_math import knowledge as k
        instance, runtime, kid, aid = self._reviewed_candidate(verified=True)
        head = self.repository.initialize(instance, runtime)
        _, instance, runtime = self.repository.load(head)
        use = k.assess_use(instance["knowledge"][kid], instance)
        self.assertTrue(use["valid"], use)
        owner = FakeEngine(self.repository_path)
        eid = owner.environment("synthetic-next")
        instance["trust_environments"][eid] = deepcopy(owner.instance["trust_environments"][eid])
        transition = k.begin_transition(instance, eid)
        transition = k.record_transition_result(instance, transition, {"id": kid, **evidence(instance, kid, eid)})
        instance = k.activate_transition(instance, transition)
        transition["status"] = "active"
        runtime["trust_transitions"][transition["id"]] = transition
        next_head = self.repository.save(head, instance, runtime)
        _, saved, loaded = self.repository.load(next_head)
        inherited = next(a for a in saved["identity_assessments"].values() if a.get("previous_assessment_id") == aid)
        self.assertTrue(inherited["continuity_comparison"]["equivalent"])
        for change in ("comparison", "review"):
            broken = deepcopy(saved)
            row = broken["identity_assessments"][inherited["id"]]
            if change == "comparison": row["continuity_comparison"]["equivalent"] = False
            else: row["review_cycle_id"] = "RC-missing"
            with self.assertRaises(ValueError): self.repository.validate_candidate(broken, loaded)

    def test_unchanged_many_record_save_does_not_rewrite_blobs(self):
        instance = {"feature_version": 5, "sources": [{"id": "SO-" + str(i), "path": "runtime/artifacts/B/file" + str(i),
            "sha256": "a" * 64} for i in range(64)]}
        head = self.repository.initialize(instance, {"feature_version": 5})
        _, instance, runtime = self.repository.load(head)
        with patch.object(self.repository._store, "_write_blobs", wraps=self.repository._store._write_blobs) as write:
            same = self.repository.save(head, instance, runtime)
        print("STORAGE no-op blob writes:", sum(len(c.args[0]) for c in write.call_args_list), flush=True)
        self.assertEqual(same, head)
        self.assertEqual(sum(len(c.args[0]) for c in write.call_args_list), 0)
        runtime["status"] = "ready"
        with patch.object(self.repository._store, "_write_blobs", wraps=self.repository._store._write_blobs) as write:
            changed = self.repository.save(head, instance, runtime)
        self.assertNotEqual(changed, head)
        self.assertLessEqual(sum(len(c.args[0]) for c in write.call_args_list), 2)


if __name__ == "__main__":
    unittest.main()
