from pathlib import Path
import sys
import unittest

import jsonschema

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math.state_contract import StateContract


class SchemaRegistrationTests(unittest.TestCase):
    def test_changed_schema_is_validated_and_previous_registration_is_detached(self):
        schema = {"type": "object", "additionalProperties": False,
                  "properties": {"id": {"type": "string"}}, "required": ["id"]}
        first = StateContract()
        first.register_family("research", "sample", schema=schema)
        schema["properties"]["id"]["type"] = "not-a-json-schema-type"
        with self.assertRaises(jsonschema.SchemaError):
            StateContract().register_family("research", "sample", schema=schema)
        registered = first.family("research", "sample").schema
        jsonschema.Draft202012Validator(registered).validate({"id": "valid"})
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.Draft202012Validator(registered).validate({"id": 123})


if __name__ == "__main__":
    unittest.main()
