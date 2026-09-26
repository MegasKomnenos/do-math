"""Snapshot-facing repository tests using only fresh temporary Git repositories."""

from __future__ import annotations

import math
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest
import base64
from unittest.mock import patch


SCRIPTS = Path(__file__).resolve().parents[1]
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from do_math.git_store import GitStateStoreConflict  # noqa: E402
from do_math.repository import (  # noqa: E402
    ResearchRepository,
    RepositoryCursorError,
    canonical_json,
    new_id,
)


INSTANCE_ID = "RI-00000000000000000000000000"


class ResearchRepositoryTests(unittest.TestCase):
    def test_export_reads_bounded_batches_and_preserves_binary_contents(self):
        head,instance,runtime=self.repository.load()
        files={f'runtime/artifacts/BA-export/{i}.bin':bytes([i%256])*1024 for i in range(150)}
        head=self.repository.save_with_state(head,instance,runtime,artifacts=files)[0]
        with patch.object(self.repository._store,'read_bytes',side_effect=AssertionError('per-file Git read')), \
             patch.object(self.repository._store,'read_many',wraps=self.repository._store.read_many) as batch:
            result=self.repository.export(self.root/'batched',head,prefixes=('runtime/artifacts/',))
        self.assertEqual(batch.call_count,3)
        self.assertTrue(all(len(call.args[1])<=64 for call in batch.call_args_list))
        self.assertEqual(set(result['files']),set(files))
        for name,raw in files.items():self.assertEqual((self.root/'batched'/name).read_bytes(),raw)

    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.repository_path = self.root / "repository"
        self.repository_path.mkdir()
        import subprocess

        subprocess.run(["git", "-C", str(self.repository_path), "init", "-q"], check=True)
        self.repository = ResearchRepository(self.repository_path, INSTANCE_ID)
        self.initial_head = self.repository.initialize({"feature_version": 5, "title": "instance"}, {"feature_version": 5, "status": "initializing"})

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_initialize_load_save_and_exact_old_snapshot_read(self) -> None:
        head, instance, runtime = self.repository.load()
        self.assertEqual(head, self.initial_head)
        self.assertEqual(instance["title"], "instance")
        self.assertEqual(instance["object_format"], "sha1")
        self.assertEqual(runtime["status"], "initializing")

        later = self.repository.save_with_state(head, instance, {"feature_version": 5, "status": "active"})[0]
        self.assertEqual(self.repository.load(self.initial_head)[2]["status"], "initializing")
        self.assertEqual(json.loads(self.repository.read("runtime/_state/metadata.json", later))["record"]["status"], "active")

    def test_stale_save_conflict_does_not_overwrite(self) -> None:
        second = ResearchRepository(self.repository_path, INSTANCE_ID)
        winner = self.repository.save_with_state(self.initial_head, {"feature_version": 5, "title": "instance"}, {"feature_version": 5, "status": "winner"})[0]
        with self.assertRaises(GitStateStoreConflict):
            second.save_with_state(self.initial_head, {"feature_version": 5, "title": "instance"}, {"feature_version": 5, "status": "loser"})[0]
        self.assertEqual(self.repository.load(winner)[2]["status"], "winner")

    def test_new_artifact_bundle_is_saved_with_state_and_existing_bundle_is_immutable(self) -> None:
        first = self.repository.save_with_state(
            self.initial_head,
            {"feature_version": 5, "title": "instance"},
            {"feature_version": 5, "status": "running"},
            artifacts={"runtime/artifacts/AB-01/output.txt": b"sealed"},
        )[0]
        with self.assertRaises(ValueError):
            self.repository.save_with_state(
                first,
                {"feature_version": 5, "title": "instance"},
                {"feature_version": 5, "status": "running"},
                artifacts={"runtime/artifacts/AB-01/other.txt": b"forbidden"},
            )[0]
        later = self.repository.save_with_state(
            first,
            {"feature_version": 5, "title": "instance"},
            {"feature_version": 5, "status": "ended"},
            artifacts={"runtime/artifacts/AB-02/output.txt": b"new bundle"},
        )[0]
        self.assertEqual(self.repository.read("runtime/artifacts/AB-01/output.txt", later), b"sealed")

    def test_query_cursor_is_bound_to_snapshot_and_query_and_has_no_empty_page(self) -> None:
        head = self.repository._store.publish(self.initial_head, {
            "research/a.txt": b"needle alpha",
            "research/b.txt": b"needle beta",
            "research/c.txt": b"not here",
        }).head
        first = self.repository.query(snapshot=head, prefix="research/", text="needle", limit=1)
        self.assertEqual(first["total"], 2)
        self.assertEqual(len(first["items"]), 1)
        self.assertTrue(first["truncated"])
        self.assertIsNotNone(first["next_cursor"])

        second = self.repository.query(snapshot=head, prefix="research/", text="needle", limit=1, cursor=first["next_cursor"])
        self.assertEqual(len(second["items"]), 1)
        self.assertNotEqual(first["items"][0]["path"], second["items"][0]["path"])
        self.assertFalse(second["truncated"])
        with self.assertRaises(RepositoryCursorError):
            self.repository.query(snapshot=head, prefix="research/", text="other", limit=1, cursor=first["next_cursor"])
        with self.assertRaises(RepositoryCursorError):
            self.repository.query(snapshot=head, prefix="research/", text="needle", limit=1, cursor=first["next_cursor"] + "x")
        forged = base64.urlsafe_b64encode(canonical_json({
            "snapshot": head,
            "prefix": "research/",
            "text": "needle",
            "last_path": "research/aa.txt",
        })).decode("ascii").rstrip("=")
        with self.assertRaises(RepositoryCursorError):
            self.repository.query(snapshot=head, prefix="research/", text="needle", limit=1, cursor=forged)
        empty = self.repository.query(snapshot=head, prefix="research/", text="absent", limit=1)
        self.assertEqual(empty, {"snapshot": head, "total": 0, "items": [], "next_cursor": None, "truncated": False})

    def test_list_files_prefix_and_read_reject_implicit_missing_snapshot(self) -> None:
        self.assertIn("research/_state/metadata.json", self.repository.list_files("research/"))
        self.assertNotIn("research/instance.json", self.repository.list_files("research/"))
        self.assertIn("runtime/_state/metadata.json", self.repository.list_files("runtime/"))
        with self.assertRaises(ValueError):
            self.repository.list_files("../")

    def test_duplicate_json_and_nonfinite_values_are_rejected(self) -> None:
        bad_head = self.repository._store.publish(self.initial_head, {
            "research/_state/metadata.json": b'{"name":"first","name":"second"}\n',
        }).head
        with self.assertRaises(ValueError):
            self.repository.load(bad_head)
        for value in (math.nan, math.inf, -math.inf):
            with self.subTest(value=value), self.assertRaises(ValueError):
                canonical_json({"value": value})

    def test_export_refuses_nonempty_or_reparse_destination_and_preserves_prefix(self) -> None:
        destination = self.root / "export"
        result = self.repository.export(destination, prefixes=("research/",))
        self.assertEqual(result["snapshot"], self.initial_head)
        self.assertEqual(result["files"], self.repository.list_files("research/"))
        self.assertEqual((destination / "research" / "_state" / "metadata.json").read_bytes(), self.repository.read("research/_state/metadata.json"))
        with self.assertRaises(ValueError):
            self.repository.export(destination, prefixes=("research/",))

        target = self.root / "target"
        target.mkdir()
        link = self.root / "reparse-export"
        try:
            os.symlink(target, link, target_is_directory=True)
        except OSError:
            created = subprocess.run(
                ["cmd.exe", "/d", "/c", "mklink", "/J", str(link), str(target)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(created.returncode, 0, created.stderr.decode("utf-8", "replace"))
        with self.assertRaises(ValueError):
            self.repository.export(link, prefixes=("research/",))

    def test_new_id_is_canonical_ulid_and_canonical_json_is_stable(self) -> None:
        identifier = new_id("RI")
        self.assertRegex(identifier, re.compile(r"^RI-[0-7][0-9A-HJKMNP-TV-Z]{25}$"))
        self.assertEqual(canonical_json({"b": 1, "a": [True, None]}), b'{\n  "a": [\n    true,\n    null\n  ],\n  "b": 1\n}\n')


class ValidatedReadReuseTests(unittest.TestCase):
    """Same-fact rechecks stay out of reads: own heads, shared heads, matched bytes."""

    def setUp(self) -> None:
        from do_math.initialization import initialize_state
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        subprocess.run(["git", "-C", str(self.root), "init", "-q"], check=True)
        self.identifier = new_id("RI")
        self.repository = ResearchRepository(self.root, self.identifier)
        # The large original input is stored as a sealed payload blob.
        instance, runtime = initialize_state(instance_id=self.identifier, goal="G", workspace=self.root / "work",
                                             config={}, source_input="x" * 70000)
        self.head = self.repository.initialize(instance, runtime)

    def counters(self):
        from contextlib import ExitStack
        from do_math import repository as module
        from do_math.state_contract import StateContract
        stack = ExitStack()
        decode = stack.enter_context(patch.object(module, "_decode_families", wraps=module._decode_families))
        validate = stack.enter_context(patch.object(StateContract, "validate", autospec=True,
                                                    side_effect=StateContract.validate))
        return stack, decode, validate

    def outside_head(self, parent, bundle):
        """A head another writer published: same state plus one artifact bundle."""
        return self.repository._store.publish(parent, {f"runtime/artifacts/{bundle}/note.bin": bundle.encode()}).head

    def test_own_publication_is_not_revalidated_but_an_outside_head_is(self):
        from do_math.preflight import inspect_persisted_state
        head, instance, runtime = self.repository.load()
        runtime["cycles"] = 1
        stack, decode, validate = self.counters()
        with stack:
            new_head, saved_instance, saved_runtime = self.repository.save_with_state(head, instance, runtime)
            _, loaded_instance, loaded_runtime = self.repository.load(new_head)
            self.assertTrue(inspect_persisted_state(self.repository, new_head)["valid"])
        self.assertEqual((decode.call_count, validate.call_count), (0, 1))  # the candidate check only
        self.assertEqual(loaded_runtime["cycles"], 1)
        saved_runtime["cycles"] = 99  # returned views are detached from the shared entry
        self.assertEqual(self.repository.load(new_head)[2]["cycles"], 1)
        rows = self.repository.records(new_head, family="lifecycle")
        self.assertEqual(len(rows), 1)
        outside = self.outside_head(new_head, "BA-outside")
        stack, decode, validate = self.counters()
        with stack:
            self.assertEqual(self.repository.load(outside)[2]["cycles"], 1)
        self.assertEqual((decode.call_count, validate.call_count), (1, 1))

    def test_one_head_is_validated_once_across_repository_objects(self):
        outside = self.outside_head(self.head, "BA-shared")
        stack, decode, _ = self.counters()
        with stack:
            ResearchRepository(self.root, self.identifier).load(outside)
            ResearchRepository(self.root, self.identifier).load(outside)
            self.assertEqual(decode.call_count, 1)
            from do_math.state_contract import StateContract
            custom = StateContract.default()
            custom.register_family("research", "sources", shape="list", validator=lambda record: None)
            ResearchRepository(self.root, self.identifier, contract=custom).load(outside)
            self.assertEqual(decode.call_count, 2)  # another contract is another validation

    def test_payload_bytes_are_hashed_once_per_repository(self):
        import hashlib
        payloads = {path: raw for path, raw in self.repository._read_documents(self.head)[3].items()
                    if path.startswith("runtime/artifacts/payload-")}
        self.assertEqual(len(payloads), 1)
        raw = next(iter(payloads.values()))
        outside = self.outside_head(self.head, "BA-payload")
        with patch.object(hashlib, "sha256", wraps=hashlib.sha256) as sha256:
            self.assertEqual(len(self.repository.load(outside)[1]["lifecycle"]["immutable_input"]["text"]), 70000)
        self.assertFalse(any(call.args and call.args[0] == raw for call in sha256.call_args_list))

    def test_evidence_rows_are_read_once_and_new_rows_are_still_matched(self):
        import hashlib
        path, raw = "runtime/artifacts/BA-evidence/observation.json", b'{"observed": true}\n'
        head, instance, runtime = self.repository.load()
        head = self.repository.save_with_state(head, instance, runtime, artifacts={path: raw})[0]
        def rows(digest):
            return {"checkpoints": {"CP-1": {"evidence_files": [{"artifact_ref": path, "sha256": digest, "bytes": len(raw)}]}}}
        digest = hashlib.sha256(raw).hexdigest()
        with patch.object(self.repository._store, "read_many", wraps=self.repository._store.read_many) as reads:
            self.repository._validate_artifact_evidence(rows(digest), head)
            self.repository._validate_artifact_evidence(rows(digest), self.outside_head(head, "BA-evidence-2"))
        self.assertEqual(reads.call_count, 1)
        with self.assertRaisesRegex(ValueError, "hash differs"):
            self.repository._validate_artifact_evidence(rows("0" * 64), head)

    def test_unchanged_records_skip_record_local_and_immutable_hash_checks(self):
        from do_math import governance, initialization
        from do_math.state_contract import StateContract
        checked = []
        contract = StateContract.default()
        contract.register_family("research", "governance_sources", shape="map",
                                 validator=lambda record: checked.append(record["id"]))
        repository = ResearchRepository(self.root, self.identifier, contract=contract)
        head, instance, runtime = repository.load()
        instance["governance_sources"]["GS-1"] = governance.preserve_source("GS-1", "first", origin="user")
        head, instance, runtime = repository.save_with_state(head, instance, runtime)
        self.assertEqual(checked, ["GS-1"])
        instance["governance_sources"]["GS-2"] = governance.preserve_source("GS-2", "second", origin="user")
        runtime["cycles"] = 1
        with patch.object(governance, "validate_source", wraps=governance.validate_source) as source, \
             patch.object(initialization, "original_input_bytes", wraps=initialization.original_input_bytes) as original:
            head, instance, runtime = repository.save_with_state(head, instance, runtime)
        self.assertEqual(checked, ["GS-1", "GS-2"])
        self.assertEqual([call.args[0]["id"] for call in source.call_args_list], ["GS-2"])
        self.assertEqual(original.call_count, 0)
        instance["governance_sources"]["GS-3"] = {**governance.preserve_source("GS-3", "third", origin="user"),
                                                  "sha256": "0" * 64}
        with self.assertRaisesRegex(ValueError, "immutable source"):
            repository.save_with_state(head, instance, runtime)


if __name__ == "__main__":
    unittest.main(verbosity=2)
