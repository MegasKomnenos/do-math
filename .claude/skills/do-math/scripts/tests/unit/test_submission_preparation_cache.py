"""Schema validation caches are keyed by the exact schema text."""
import unittest

from do_math import preflight


class PreparationCacheTests(unittest.TestCase):
    def test_valid_schema_cache_does_not_hide_a_changed_invalid_schema(self):
        from jsonschema.exceptions import SchemaError
        preflight._check_schema_pair('{"type":"object"}')
        preflight._check_schema_pair('{"type":"object"}')
        with self.assertRaisesRegex(SchemaError, "'not-a-json-schema-type' is not valid under any of the given schemas"):
            preflight._check_schema_pair('{"type":"not-a-json-schema-type"}')
