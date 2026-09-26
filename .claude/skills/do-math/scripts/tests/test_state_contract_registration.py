from pathlib import Path
import sys
import unittest

import jsonschema

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math.state_contract import StateContract, check_schema


class SchemaRegistrationTests(unittest.TestCase):
    def test_default_contracts_do_not_share_mutable_schemas_or_registrations(self):
        first = StateContract.default()
        family = first.family("research", "knowledge")
        family.schema["fixture_marker"] = True
        first.register_family("research", "fixture_record", schema={
            "type": "object", "additionalProperties": False,
            "properties": {"id": {"type": "string"}}, "required": ["id"]})

        second = StateContract.default()
        self.assertNotIn("fixture_marker", second.family("research", "knowledge").schema)
        self.assertIsNone(second.family("research", "fixture_record"))

    def test_changed_schema_is_validated_and_previous_registration_is_detached(self):
        schema = {"type": "object", "additionalProperties": False,
                  "properties": {"id": {"type": "string"}}, "required": ["id"]}
        first = StateContract()
        first.register_family("research", "sample", schema=schema)
        schema["properties"]["id"]["type"] = "not-a-json-schema-type"
        with self.assertRaises(jsonschema.SchemaError):
            check_schema(schema)  # the boundary for schemas from outside the product
        registered = first.family("research", "sample").schema
        jsonschema.Draft202012Validator(registered).validate({"id": "valid"})
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.Draft202012Validator(registered).validate({"id": 123})


    def test_every_built_in_family_schema_is_a_valid_json_schema(self):
        # Built-in schemas are not re-checked at process start; this test is their check.
        contract = StateContract.default()
        families = [contract.family(root, name) for root, name in contract._families]
        self.assertGreater(len(families), 50)
        for family in families:
            with self.subTest(family=family.name):
                check_schema(family.schema)

    def test_repository_registration_checks_an_outside_schema(self):
        import tempfile
        from unittest.mock import patch
        from do_math.repository import ResearchRepository
        with patch('do_math.repository.GitStateStore'), tempfile.TemporaryDirectory() as directory:
            repository = ResearchRepository(Path(directory), 'RI-fixture')
            with self.assertRaises(jsonschema.SchemaError):
                repository.register_family('research', 'outside', schema={'type': 'not-a-json-schema-type'})


class ManifestMemoTests(unittest.TestCase):
    def test_manifest_is_computed_once_per_registration_generation(self):
        from unittest.mock import patch
        import json
        contract = StateContract.default()
        with patch.object(json, "dumps", wraps=json.dumps) as dumps:
            first = contract.manifest()
            self.assertEqual(contract.manifest(), first)
            self.assertEqual(dumps.call_count, 1)
            contract.register_family("research", "memo_fixture", schema={
                "type": "object", "additionalProperties": False,
                "properties": {"id": {"type": "string"}}, "required": ["id"]})
            self.assertNotEqual(contract.manifest()["sha256"], first["sha256"])
        self.assertEqual(StateContract.default().manifest(), first)

    def test_only_an_unchanged_default_contract_counts_as_installed(self):
        contract = StateContract.default()
        self.assertEqual(contract.installed_generation, contract.validation_generation)
        contract.register_family("research", "sources", shape="list", validator=lambda record: None)
        self.assertNotEqual(contract.installed_generation, contract.validation_generation)
        self.assertIsNone(StateContract().installed_generation)


if __name__ == "__main__":
    unittest.main()
