"""The installed state contract (``state_contract``, layer 2): family registration, registered validators and record checks.

Registration and validation are called directly. The publication check runs
the real ``ResearchRepository`` on the Git port's in-process fake (설계 4.3);
calls to ``json.dumps`` are counted by observing its code (``ObservedCalls``),
not by replacing it.
"""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest

import jsonschema

from do_math.state_contract import StateContract, default_state_contract
from support.state_builders import current_state, installed_contract, with_validator
from support.fakes.clock import FakeClock
from support.fakes.git_backend import InProcessGit
from support.provider_probes import ObservedCalls
from support.storage_records import record_store

RECORD = {"type": "object", "additionalProperties": False,
          "properties": {"id": {"type": "string"}}, "required": ["id"]}


class SchemaRegistrationTests(unittest.TestCase):
    def test_repositories_share_one_installed_contract_and_tests_build_their_own(self):
        shared = default_state_contract()
        self.assertIs(default_state_contract(), shared)
        own = installed_contract()
        own.register_family("research", "fixture_record", schema=RECORD)
        self.assertIsNone(shared.family("research", "fixture_record"))
        self.assertEqual(set(own._families) - set(shared._families), {("research", "fixture_record")})

    def test_a_family_is_registered_once_and_keeps_its_own_schema_copy(self):
        schema = {"type": "object", "additionalProperties": False,
                  "properties": {"id": {"type": "string"}}, "required": ["id"]}
        contract = StateContract()
        contract.register_family("research", "sample", schema=schema)
        schema["properties"]["id"]["type"] = "not-a-json-schema-type"
        registered = contract.family("research", "sample").schema
        jsonschema.Draft202012Validator(registered).validate({"id": "valid"})
        with self.assertRaises(jsonschema.ValidationError) as rejected:
            jsonschema.Draft202012Validator(registered).validate({"id": 123})
        self.assertEqual((list(rejected.exception.absolute_path), rejected.exception.validator), (["id"], "type"))
        with self.assertRaisesRegex(ValueError, "^record family already registered: sample$"):
            contract.register_family("research", "sample", schema=RECORD)
        with self.assertRaisesRegex(ValueError, "^record family already registered: sources$"):
            installed_contract().register_family("research", "sources", shape="list", validator=lambda record: None)

    def test_every_built_in_family_schema_is_a_valid_json_schema(self):
        """About 1.6 s, over the 0.2 s unit budget: a full meta-schema check of every installed family schema."""
        # Built-in schemas are not re-checked at process start; this test is their check.
        families = default_state_contract().families()
        self.assertGreater(len(families), 50)
        for family in families:
            with self.subTest(family=family.name):
                self.assertIsNone(jsonschema.Draft202012Validator.check_schema(family.schema))


class ManifestMemoTests(unittest.TestCase):
    def test_manifest_is_computed_once_until_a_registration(self):
        installed = default_state_contract().manifest()
        contract = installed_contract()
        with ObservedCalls(dumps=json.dumps) as calls:
            first = contract.manifest()
            self.assertEqual(contract.manifest(), first)
            self.assertEqual(calls.count("dumps"), 1)
            contract.register_family("research", "memo_fixture", schema=RECORD)
            self.assertNotEqual(contract.manifest()["sha256"], first["sha256"])
        self.assertEqual(first, installed)
        self.assertEqual(default_state_contract().manifest(), installed)


class RegisteredValidatorTests(unittest.TestCase):
    def test_registered_validator_enforces_current_rules(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            # Both repository objects read the same Git objects.
            backend, clock = InProcessGit(), FakeClock()
            before = record_store(root, backend=backend, clock=clock)
            head = before.initialize(*current_state({'sources': [
                {'id': 'SO-input', 'path': 'original.txt', 'sha256': 'a' * 64}]}))

            def check_source(record):
                if record['path'] != 'original.txt':
                    raise ValueError('repaired source rule')
            contract = with_validator(installed_contract(), 'research', 'sources', check_source)
            after = record_store(root, contract=contract, backend=backend, clock=clock)
            loaded, instance, runtime = after.load(head)
            self.assertEqual(loaded, head)
            instance['sources'][0]['path'] = 'unexpected.txt'
            with self.assertRaisesRegex(ValueError, '^repaired source rule$'):
                after.save_with_state(head, instance, runtime)
            self.assertEqual(after.load()[1]['sources'][0]['path'], 'original.txt')


class StateContractValidationTests(unittest.TestCase):
    def test_installed_receipt_family_checks_execution_ref(self):
        family = default_state_contract().family("runtime", "integrations")
        self.assertIsNotNone(family)
        self.assertEqual({("EX-1", "executions")}, set(family.references({"execution_id": "EX-1"})))

    def test_invalid_execution_and_activity_are_rejected_by_the_state_contract(self):
        # Inspection receives loaded states only; loading validates execution
        # states and activity ownership, so the contract is where they are rejected.
        from support.entry import entry
        _entry = entry()
        from do_math import activities, execution_profiles, knowledge_io, model_policy
        profiles = execution_profiles.build_profiles({
            "session_limits": model_policy.LIMITS, "tier_models": model_policy.MODELS,
            "observation_mode": "event_driven", "max_input_bytes": 500000,
            "effort": "medium", "operator_effort": "high", "operator_timeout_seconds": 600,
            "scholarly_enabled": True, "scholarly_server": None, "claude_only_assigned_model": False}, host=_entry.ports.host)
        instance, runtime = current_state({"object_format": "sha1", "knowledge": {}, "expositions": {},
            **{k: v for k, v in profiles.items() if k != "role_profile_refs"}}, {"executions": {}})
        instance = knowledge_io.ensure_ontology(instance)
        activity = activities.open_activity(runtime, activity_id="AT-1", activity_kind="research_work",
            owner_ref="task", input_refs=[], opened_at="2026-09-20T00:00:00Z")
        profile = next(p for p in profiles["execution_profiles"].values() if p["role"] == "research_work")
        execution = {"id": "EX-1", "role": "research_work", "actor_kind": "ai", "owner_activity_id": "AT-1",
            "created_at": "2026-09-20T00:00:00Z", "status": "running", "input_manifest": [], "context_origin": []}
        execution_profiles.bind_execution(execution, profile)
        runtime["executions"]["EX-1"] = execution
        activity["assigned_execution_ids"] = ["EX-1"]
        contract = default_state_contract()
        contract.validate(instance, runtime)
        invalid = deepcopy(runtime)
        invalid["executions"]["EX-1"]["status"] = "teleporting"
        with self.assertRaisesRegex(ValueError, "executions/EX-1/status"):
            contract.validate(instance, invalid)
        orphan = deepcopy(runtime)
        orphan["activities"]["AT-1"]["assigned_execution_ids"] = []
        with self.assertRaisesRegex(ValueError, "EX-1: execution has no matching activity"):
            contract.validate(instance, orphan)


if __name__ == "__main__":
    unittest.main()
