"""Characterization: the unified digest owners reproduce the removed helpers byte for byte.

Stored records carry these digests, so the removed module-local formulas are
written out here as the oracle. A change here means stored digests change.
"""
from pathlib import Path
import hashlib
import json
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math.file_io import json_digest
from do_math.observations import _raw_json
from do_math.repository import canonical_json, exact_content_hash


# State-tree values: strings, safe integers, nesting and empty values only.
STATE_VALUES = [
    {},
    [],
    "",
    None,
    True,
    0,
    -(2 ** 53 - 1),
    2 ** 53 - 1,
    "é and é stay distinct",
    {"한글": "数学 \U0001d53d ∀x", "ascii": "a\"b\\c\n\t"},
    {"b": [1, {"z": [], "a": {}}], "a": {"nested": [[""], [None, False]]}},
]

# Values outside the state tree may carry fractional numbers.
JSON_VALUES = STATE_VALUES + [
    {"score": 0.1, "tiny": 1e-07, "huge": 1.5e300, "negative_zero": -0.0},
    [3.141592653589793, {"α": 2.5, "list": [1, 1.0]}],
]


def old_state_helper(value):
    # execution_profiles._digest, initialization.digest, integration.digest,
    # knowledge_records.digest/exact_digest, lifecycle_engine._digest,
    # planning._hash, governance.digest and the inline call sites.
    return hashlib.sha256(canonical_json(value)).hexdigest()


def old_compact_without_nan_guard(value):
    # academic._hash, delegations._hash, external._hash, state_contract inline,
    # formal untracked inventory.
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                     separators=(",", ":")).encode()).hexdigest()


def old_compact_with_nan_guard(value):
    # claude_stream._hash, control_transport._digest, input_basis._review_basis_digest,
    # review_cycle._digest.
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
                                     allow_nan=False).encode("utf-8")).hexdigest()


def old_rules_digest(rules):
    # observations rules_digest and _replace_rules before this change.
    return hashlib.sha256(json.dumps(rules, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


class DigestCharacterizationTests(unittest.TestCase):
    def test_state_value_identity_matches_removed_helpers(self):
        for value in STATE_VALUES:
            with self.subTest(value=value):
                self.assertEqual(exact_content_hash(value), old_state_helper(value))

    def test_json_digest_matches_removed_compact_helpers(self):
        for value in JSON_VALUES:
            with self.subTest(value=value):
                self.assertEqual(json_digest(value), old_compact_with_nan_guard(value))
                self.assertEqual(json_digest(value), old_compact_without_nan_guard(value))

    def test_known_digests_stay_fixed(self):
        value = {"b": [1, "é"], "a": {}}
        self.assertEqual(exact_content_hash(value),
                         "ee49335f888d488008ebfc784c14ad09c707cdd6d121811d20e6e0a4f4dcb598")
        self.assertEqual(json_digest({"b": [1, "é", 0.5], "a": {}}),
                         "2927b31b4f42ab05bd8db76af7629cbdf29db3f4ccc2ef33d833faea5d6f8f92")

    def test_json_digest_refuses_non_finite_numbers(self):
        for number in (float("nan"), float("inf"), float("-inf"), float("1e999")):
            with self.subTest(number=number), self.assertRaises(ValueError):
                json_digest({"value": number})

    def test_observation_rule_digest_matches_removed_formula(self):
        rules = [{"id": "régle", "operator": "tool_calls_gte", "threshold": 3, "repeat_interval": 2,
                  "subject": {"kind": "tool", "id": "lean"}, "basis": {"source": "events", "unit": "count"},
                  "required_evidence": ["証拠"]}]
        for value in (rules, [], [{"nested": {"b": 1, "a": [None, True]}}]):
            with self.subTest(value=value):
                self.assertEqual(hashlib.sha256(_raw_json(value).encode()).hexdigest(), old_rules_digest(value))


if __name__ == "__main__":
    unittest.main()
