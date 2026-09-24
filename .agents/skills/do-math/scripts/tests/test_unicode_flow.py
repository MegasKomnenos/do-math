from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parents[1]
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from do_math.context_store import build_role_manifest, read_source, write_source_catalog
from do_math.initialization import initialize_state, original_input_bytes
from do_math.repository import ResearchRepository, canonical_json


INSTANCE_ID = "RI-00000000000000000000000000"


class UnicodeFlowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.repository_path = self.root / "repository"
        self.repository_path.mkdir()
        subprocess.run(["git", "-C", str(self.repository_path), "init", "-q"], check=True)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_exact_json_keeps_nfd_and_distinct_mathematical_keys(self) -> None:
        value = {"text": "e\u0301", "names": {"K": "kelvin", "K": "ascii"}}
        raw = canonical_json(value)
        self.assertEqual(raw, canonical_json(value))
        self.assertEqual(json.loads(raw), value)
        self.assertIn('"K"', raw.decode("utf-8"))
        self.assertIn('"K"', raw.decode("utf-8"))

    def test_exact_json_preserves_scalars_and_rejects_surrogates(self) -> None:
        text = "\ud7ff\ue000\U00010000\U0010ffff e\u0301 K K"
        self.assertEqual(json.loads(canonical_json({text: text})), {text: text})
        for invalid in ("\ud800", "\udbff", "\udc00", "\udfff", "\ud800\udc00"):
            for value in ({"text": "prefix" + invalid + "suffix"}, {invalid: "value"}):
                with self.subTest(value=repr(value)), self.assertRaisesRegex(ValueError, "surrogate"):
                    canonical_json(value)

    def test_git_save_reload_has_plain_exact_json_and_schema_two(self) -> None:
        repository = ResearchRepository(self.repository_path, INSTANCE_ID)
        schema = {
            "type": "object", "additionalProperties": False,
            "properties": {"id": {"type": "string"}, "payload": {"type": "object"}},
            "required": ["id", "payload"],
        }
        repository.register_family("research", "unicode_fixture", schema=schema)
        record = {"id": "UF-1", "payload": {"text": "e\u0301", "names": {"K": "kelvin", "K": "ascii"}}}
        head = repository.initialize({"feature_version": 5, "unicode_fixture": {"UF-1": record}}, {"feature_version": 5})
        _, instance, _ = repository.load(head)
        descriptor = repository.read_record("UF-1", head)
        stored = json.loads(descriptor["bytes"])
        self.assertEqual(instance["unicode_fixture"]["UF-1"], record)
        self.assertEqual(stored["record"], record)
        self.assertNotIn("utf8_base64", descriptor["bytes"].decode("utf-8"))

    def test_schema_one_record_is_rejected_without_automatic_conversion(self) -> None:
        repository = ResearchRepository(self.repository_path, INSTANCE_ID)
        schema = {
            "type": "object", "additionalProperties": False,
            "properties": {"id": {"type": "string"}, "text": {"type": "string"}},
            "required": ["id", "text"],
        }
        repository.register_family("research", "unicode_fixture", schema=schema)
        head = repository.initialize({"feature_version": 5, "unicode_fixture": {"UL-1": {"id": "UL-1", "text": "e\u0301"}}},
                                     {"feature_version": 5})
        descriptor = repository.read_record("UL-1", head)
        stored = json.loads(descriptor["bytes"])
        stored["unexpected_field"] = True
        corrupt = repository._store.publish(head, {descriptor["path"]: canonical_json(stored)}).head
        with self.assertRaisesRegex(ValueError, "invalid record envelope"):
            repository.load(corrupt)

    def test_source_catalog_and_direct_input_hash_exact_bytes(self) -> None:
        value = {"text": "e\u0301", "names": {"K": "kelvin", "K": "ascii"}}
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            catalog = write_source_catalog({"proposal": value}, workspace)
            source_ref = catalog["entries"]["proposal"]
            source = read_source(workspace, source_ref, limit=1_000_000)
            manifest = build_role_manifest({"proposal": value}, workspace=workspace,
                                           role="research_work", direct_keys=["proposal"], reference_keys=[])
        expected = canonical_json(value)
        self.assertEqual(source["bytes"], expected)
        self.assertEqual(json.loads(source["bytes"]), value)
        self.assertEqual(source_ref["sha256"], hashlib.sha256(expected).hexdigest())
        self.assertEqual(manifest["direct"][0]["sha256"], hashlib.sha256(expected).hexdigest())

    def test_initial_immutable_input_is_one_exact_utf8_representation(self) -> None:
        source = "e\u0301 and K/K"
        instance, _ = initialize_state(instance_id=INSTANCE_ID, goal="goal", goal_kind="mathematical",
                                       workspace=self.root / "workspace", config={}, source_input=source)
        immutable = instance["lifecycle"]["immutable_input"]
        self.assertEqual(immutable, {
            "text": source,
            "sha256": hashlib.sha256(source.encode("utf-8")).hexdigest(),
            "bytes": len(source.encode("utf-8")),
        })
        self.assertEqual(original_input_bytes(immutable), source.encode("utf-8"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
