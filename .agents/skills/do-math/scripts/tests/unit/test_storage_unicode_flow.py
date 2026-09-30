"""Unicode strings keep their exact code points through storage, hashing and role input (layers 1 and 2).

The samples are a decomposed string (e + COMBINING ACUTE ACCENT) and two keys
that normalization would merge (KELVIN SIGN and ASCII K). They are written as
named escapes, so no editor normalization can change them. Storage runs the
real ``ResearchRepository`` on the Git port's in-process fake (설계 4.3).
"""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from do_math.canonical import canonical_json
from do_math.context_store import build_role_manifest, read_source, write_source_catalog
from research_fixtures import current_state, installed_contract
from support.storage_records import record_store

DECOMPOSED = "e\N{COMBINING ACUTE ACCENT}"
KELVIN = "\N{KELVIN SIGN}"
SURROGATE_REFUSED = "JSON strings cannot contain surrogate code points"


def exact_value():
    return {"text": DECOMPOSED, "names": {KELVIN: "kelvin", "K": "ascii"}}


def unicode_contract(properties):
    """The installed families plus ``research/unicode_fixture`` records of ``id`` and ``properties``."""
    contract = installed_contract()
    contract.register_family("research", "unicode_fixture", schema={
        "type": "object", "additionalProperties": False,
        "properties": {"id": {"type": "string"}, **properties}, "required": ["id", *properties]})
    return contract


class UnicodeFlowTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)

    def test_exact_json_keeps_nfd_and_distinct_mathematical_keys(self):
        value = exact_value()
        raw = canonical_json(value)
        self.assertEqual(raw, canonical_json(value))
        self.assertEqual(json.loads(raw), value)
        self.assertIn('"' + KELVIN + '"', raw.decode("utf-8"))
        self.assertIn('"K"', raw.decode("utf-8"))
        self.assertNotEqual(canonical_json(DECOMPOSED), canonical_json("\N{LATIN SMALL LETTER E WITH ACUTE}"))

    def test_exact_json_preserves_scalars_and_rejects_surrogates(self):
        text = "\U0000d7ff\U0000e000\U00010000\U0010ffff " + DECOMPOSED + " " + KELVIN + " K"
        self.assertEqual(json.loads(canonical_json({text: text})), {text: text})
        # The last is a high and a low surrogate as two code points (not U+10000), built
        # with chr because a tool may merge the escaped pair into the one character.
        for invalid in ("\ud800", "\udbff", "\udc00", "\udfff", chr(0xD800) + chr(0xDC00)):
            for value in ({"text": "prefix" + invalid + "suffix"}, {invalid: "value"}):
                with self.subTest(value=repr(value)), self.assertRaises(ValueError) as refused:
                    canonical_json(value)
                self.assertEqual(str(refused.exception), SURROGATE_REFUSED)

    def test_git_save_reload_stores_the_record_as_exact_json(self):
        repository = record_store(self.root / "repository", contract=unicode_contract({"payload": {"type": "object"}}))
        record = {"id": "UF-1", "payload": exact_value()}
        head = repository.initialize(*current_state({"unicode_fixture": {"UF-1": record}}))
        _, instance, _ = repository.load(head)
        descriptor = repository.read_record("UF-1", head)
        stored = json.loads(descriptor["bytes"])
        self.assertEqual(instance["unicode_fixture"]["UF-1"], record)
        self.assertEqual(stored["record"], record)

    def test_record_envelope_with_an_unknown_field_is_rejected_without_conversion(self):
        repository = record_store(self.root / "repository", contract=unicode_contract({"text": {"type": "string"}}))
        head = repository.initialize(*current_state({"unicode_fixture": {"UL-1": {"id": "UL-1", "text": DECOMPOSED}}}))
        descriptor = repository.read_record("UL-1", head)
        stored = json.loads(descriptor["bytes"])
        stored["unexpected_field"] = True
        # Another writer's bytes: the store's own publication, past the repository's checks.
        corrupt = repository._store.publish(head, {descriptor["path"]: canonical_json(stored)}).head
        with self.assertRaisesRegex(ValueError, "^invalid record envelope fields$"):
            repository.load(corrupt)

    def test_source_catalog_and_direct_input_hash_exact_bytes(self):
        value = exact_value()
        workspace = self.root / "workspace"
        workspace.mkdir()
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


if __name__ == "__main__":
    unittest.main()
