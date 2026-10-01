"""Record identity rules the engine publishes by: exact evidence hashes and globally unique record IDs."""
import hashlib
import unittest

from do_math.canonical import canonical_json, exact_content_hash
from do_math.engine import _record_evidence
from do_math.state_contract import default_state_contract
from support.state_builders import current_state


class QueryIdentity(unittest.TestCase):
    def test_exact_evidence_binds_persisted_bytes_and_code_points(self):
        record = {"id": "FR-one", "title": "e\u0301", "verification": {"\u212a": "e\u0301", "K": "\u00e9"}}

        def evidence(value):
            raw = canonical_json({"record": value})
            row = {"snapshot": "snapshot", "path": "research/formal_results/FR-one.json", "record": value,
                   "bytes": raw, "sha256": hashlib.sha256(raw).hexdigest(), "json_pointer": "/record"}
            return _record_evidence(row)
        first = evidence(record)
        self.assertEqual(first["json_pointer"], "/record")
        self.assertEqual(first["sha256"], hashlib.sha256(canonical_json({"record": record})).hexdigest())
        self.assertEqual(first["logical_sha256"], exact_content_hash(record))
        same_metadata = {**record, "title": "\u00e9"}
        self.assertNotEqual(first["logical_sha256"], evidence(same_metadata)["logical_sha256"])
        changed_payload = {**record, "verification": {"\u212a": "\u00e9", "K": "\u00e9"}}
        self.assertNotEqual(first["logical_sha256"], evidence(changed_payload)["logical_sha256"])

    def test_duplicate_id_is_rejected_across_families(self):
        # The state contract checks global record IDs of every bundle candidate
        # (_validate_bundle_candidate -> validate_candidate) before publication.
        instance, runtime = current_state(
            {"object_format": "sha1", "sources": [{"id": "DUP", "path": "input.txt", "sha256": "a" * 64}]},
            {"events": [{"id": "DUP", "kind": "created"}]})
        with self.assertRaisesRegex(ValueError, "record IDs must be globally unique: DUP"):
            default_state_contract().validate(instance, runtime)


if __name__ == "__main__":
    unittest.main()
