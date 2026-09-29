"""The two JSON digest owners and the values each one identifies.

State values are identified by ``repository.exact_content_hash``, which checks
the storage value domain; ``file_io.json_digest`` is for JSON outside the
state (transport files, provider values). Stored records and observation
feedback carry these digests, so each formula is pinned by fixed digests over
its value domain: a change of separators, key order, escaping or encoding
fails here.
"""
from pathlib import Path
import hashlib
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math import academic, external
from do_math.values import json_digest
from do_math.observations import _raw_json
from do_math.repository import exact_content_hash


# State-tree values: strings in both Unicode normal forms, escapes, nesting,
# empty values and the safe integer bounds.
STATE_DIGESTS = [
    ("é and é stay distinct", "50eab2edd9e5ff92980678503b0f683ed3dad2d3f36111a600dca142e1546ea4"),
    ({"한글": "数学 \U0001d53d ∀x", "ascii": "a\"b\\c\n\t"},
     "c2c5ff19da38919c6cbcb19c66f0cb2785d95dee01da2a04a3584c2c03bc1897"),
    ({"b": [1, {"z": [], "a": {}}], "a": {"nested": [[""], [None, False]]}},
     "979a7d71d018574b96ba1516b833d8bf9f9f8b1fd252d363935901779e30b944"),
    ({"object": {}, "list": [], "text": "", "null": None}, "5b19902385b2315a786db729443dc8a06429c0207d98faa7ec76e0964ee8c9c5"),
    ([-(2 ** 53 - 1), 0, 2 ** 53 - 1, True], "518cab47cb68142143bc0ea2af576830a5d54dc1b1d2dc5f6a0d46e3af83e502"),
]

# Values outside the state tree may carry fractional numbers.
JSON_DIGESTS = [
    ({"score": 0.1, "tiny": 1e-07, "huge": 1.5e300, "negative_zero": -0.0},
     "1f0a8ec374d3cbfc918341790bfdc34f5a5e29f8a5c6ae9d20708537408bd6a0"),
    ([3.141592653589793, {"α": 2.5, "list": [1, 1.0]}], "fae0409073c3ed7710a3da3e85081ecdfb55faa6cc6faf015270424d6d3437fc"),
]

# Observation rules and provider payloads keep their raw JSON text.
RULE_DIGESTS = [
    ([{"id": "régle", "operator": "tool_calls_gte", "threshold": 3, "repeat_interval": 2,
       "subject": {"kind": "tool", "id": "lean"}, "basis": {"source": "events", "unit": "count"},
       "required_evidence": ["証拠"]}], "26ec27c1ee2c1b0415b6053d5373d79861e551c47f93b515875e635c136df850"),
    ([], "4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945"),
    ([{"nested": {"b": 1, "a": [None, True]}}], "2fb84c630bb11854bb70dad70f1140ac24fbf8865812df1e573440111b79176e"),
]


class DigestCharacterizationTests(unittest.TestCase):
    def test_state_value_digests_stay_fixed(self):
        for value, digest in STATE_DIGESTS:
            with self.subTest(value=value):
                self.assertEqual(exact_content_hash(value), digest)

    def test_json_digests_stay_fixed(self):
        for value, digest in JSON_DIGESTS:
            with self.subTest(value=value):
                self.assertEqual(json_digest(value), digest)

    def test_observation_rule_digests_stay_fixed(self):
        for value, digest in RULE_DIGESTS:
            with self.subTest(value=value):
                self.assertEqual(hashlib.sha256(_raw_json(value).encode()).hexdigest(), digest)

    def test_state_value_identity_refuses_values_outside_the_storage_domain(self):
        for value in ({"limit": 0.5}, [1.0], {"value": float("nan")}):
            with self.subTest(value=value), self.assertRaises(ValueError):
                exact_content_hash(value)

    def test_stored_academic_and_external_identities_use_the_state_value_digest(self):
        requirements = academic.requirement_record([{"id": "R", "scope": "S", "assessor": "research_plan",
                                                     "criteria": ["C"]}])
        self.assertEqual(requirements["sha256"], exact_content_hash({"items": requirements["items"]}))
        record = {"id": "K-1", "claim": "é"}
        basis = academic.solution_basis("goal", [record])
        self.assertEqual(basis["records"], [{"id": "K-1", "sha256": exact_content_hash(record)}])
        operation = external.prepare_operation({"method": "GET", "url": "https://example.invalid/a"}, "G-1", "S-1")
        self.assertEqual(operation["request_sha256"], exact_content_hash(operation["request"]))
        self.assertTrue(external.request_binding_current(operation))

    def test_json_digest_refuses_non_finite_numbers(self):
        for number in (float("nan"), float("inf"), float("-inf"), float("1e999")):
            with self.subTest(number=number), self.assertRaises(ValueError):
                json_digest({"value": number})


if __name__ == "__main__":
    unittest.main()
