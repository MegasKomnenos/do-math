"""Snapshot-facing repository tests using only fresh temporary Git repositories."""

from __future__ import annotations

import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest
import base64
from unittest.mock import create_autospec, patch
import hashlib
from copy import deepcopy


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
from research_fixtures import bare_engine, current_state, git_init  # noqa: E402
from do_math import repository
from do_math.state_checks import inspect_state


def candidate_repository(test):
    """A repository over the installed contract in a new empty Git repository; candidate validation never reaches it."""
    return repository.ResearchRepository(git_init(Path(test.enterContext(tempfile.TemporaryDirectory()))),
                                         'RI-01ARZ3NDEKTSV4RRFFQ69G5FAV')


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

    def test_published_artifacts_are_not_read_again_at_later_heads_only(self):
        path, raw = "runtime/artifacts/BA-known/input.txt", b"archived input\n"
        head, instance, runtime = self.repository.load()
        before = head
        written = self.repository.save_with_state(head, instance, runtime, artifacts={path: raw})[0]
        instance["title"] = "later"
        later = self.repository.save_with_state(written, instance, runtime)[0]
        store = self.repository._store
        with patch.object(store, "read_bytes", side_effect=AssertionError("Git read")), \
                patch.object(store, "blob_sizes", wraps=store.blob_sizes) as sizes:
            for snapshot in (written, later):
                self.assertEqual(self.repository.read(path, snapshot), raw)
                self.assertEqual(self.repository.blob_sizes([path], snapshot), {path: len(raw)})
        self.assertEqual([call.args[1] for call in sizes.call_args_list], [[], []])
        # A head that precedes the artifact still asks Git, which reports it absent.
        self.assertEqual(self.repository.blob_sizes([path], before, missing="omit"), {})
        with self.assertRaises(Exception):
            self.repository.read(path, before)

    def test_live_input_snapshots_stay_validated_beyond_the_read_bound(self):
        from do_math import repository as module
        head, instance, runtime = self.repository.load()
        pinned = head
        module.retain_reads(self.repository.git_dir, {pinned})
        try:
            for index in range(module._VALIDATED_READ_LIMIT + 2):
                instance["title"] = f"title {index}"
                head = self.repository.save_with_state(head, instance, runtime)[0]
            self.assertIsNotNone(self.repository.published_state(pinned))
            module.retain_reads(self.repository.git_dir, set())
            instance["title"] = "released"
            self.repository.save_with_state(head, instance, runtime)
            self.assertIsNone(self.repository.published_state(pinned))
        finally:
            module.retain_reads(self.repository.git_dir, set())

    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.repository_path = self.root / "repository"
        self.repository_path.mkdir()
        git_init(self.repository_path)
        self.repository = ResearchRepository(self.repository_path, INSTANCE_ID)
        self.initial_head = self.repository.initialize(*current_state({"title": "instance"}))

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_initialize_load_save_and_exact_old_snapshot_read(self) -> None:
        head, instance, runtime = self.repository.load()
        self.assertEqual(head, self.initial_head)
        self.assertEqual(instance["title"], "instance")
        self.assertEqual(instance["object_format"], "sha1")
        self.assertEqual(runtime["status"], "initializing")

        later = self.repository.save_with_state(head, instance, {**runtime, "status": "running"})[0]
        self.assertEqual(self.repository.load(self.initial_head)[2]["status"], "initializing")
        self.assertEqual(json.loads(self.repository.read("runtime/_state/metadata.json", later))["record"]["status"], "running")

    def test_stale_save_conflict_does_not_overwrite(self) -> None:
        second = ResearchRepository(self.repository_path, INSTANCE_ID)
        winner = self.repository.save_with_state(self.initial_head, *current_state({"title": "instance"}, {"status": "running"}))[0]
        with self.assertRaises(GitStateStoreConflict):
            second.save_with_state(self.initial_head, *current_state({"title": "instance"}, {"status": "paused"}))[0]
        self.assertEqual(self.repository.load()[0], winner)
        self.assertEqual(self.repository.load(winner)[2]["status"], "running")

    def test_new_artifact_bundle_is_saved_with_state_and_existing_bundle_is_immutable(self) -> None:
        first = self.repository.save_with_state(
            self.initial_head,
            *current_state({"title": "instance"}, {"status": "running"}),
            artifacts={"runtime/artifacts/AB-01/output.txt": b"sealed"},
        )[0]
        with self.assertRaises(ValueError):
            self.repository.save_with_state(
                first,
                *current_state({"title": "instance"}, {"status": "running"}),
                artifacts={"runtime/artifacts/AB-01/other.txt": b"forbidden"},
            )[0]
        later = self.repository.save_with_state(
            first,
            *current_state({"title": "instance"}, {"status": "completed"}),
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

    def test_duplicate_json_keys_are_rejected_on_load(self) -> None:
        bad_head = self.repository._store.publish(self.initial_head, {
            "research/_state/metadata.json": b'{"name":"first","name":"second"}\n',
        }).head
        with self.assertRaises(ValueError):
            self.repository.load(bad_head)

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
        git_init(self.root)
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
        head, instance, runtime = self.repository.load()
        runtime["cycles"] = 1
        stack, decode, validate = self.counters()
        with stack:
            new_head, saved_instance, saved_runtime = self.repository.save_with_state(head, instance, runtime)
            _, loaded_instance, loaded_runtime = self.repository.load(new_head)
            self.assertEqual(self.repository.view(new_head)[2]["cycles"], 1)
        self.assertEqual((decode.call_count, validate.call_count), (0, 1))  # the candidate check only
        self.assertEqual(loaded_runtime["cycles"], 1)
        saved_runtime["cycles"] = 99  # returned views are detached from the shared entry
        self.assertEqual(self.repository.load(new_head)[2]["cycles"], 1)
        rows = [row for row in self.repository.load_records(new_head)[3] if row["family"] == "lifecycle"]
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
            from research_fixtures import installed_contract
            ResearchRepository(self.root, self.identifier, contract=installed_contract()).load(outside)
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
        from research_fixtures import installed_contract, with_validator
        checked = []
        contract = installed_contract()
        installed = contract.family("research", "governance_sources").validator
        def counted(record):
            checked.append(record["id"])
            installed(record)
        with_validator(contract, "research", "governance_sources", counted)
        repository = ResearchRepository(self.root, self.identifier, contract=contract)
        head, instance, runtime = repository.load()
        instance["governance_sources"]["GS-1"] = governance.preserve_source("GS-1", "first", origin="user")
        head, instance, runtime = repository.save_with_state(head, instance, runtime)
        self.assertEqual(checked, ["GS-1"])
        instance["governance_sources"]["GS-2"] = governance.preserve_source("GS-2", "second", origin="user")
        runtime["cycles"] = 1
        with patch.object(initialization, "original_input_bytes", wraps=initialization.original_input_bytes) as original:
            head, instance, runtime = repository.save_with_state(head, instance, runtime)
        self.assertEqual(checked, ["GS-1", "GS-2"])
        self.assertEqual(original.call_count, 0)
        instance["governance_sources"]["GS-3"] = {**governance.preserve_source("GS-3", "third", origin="user"),
                                                  "sha256": "0" * 64}
        with self.assertRaisesRegex(ValueError, "immutable source"):
            repository.save_with_state(head, instance, runtime)


class SaveWithStateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.repository_path = self.root / "repository"
        self.repository_path.mkdir()
        git_init(self.repository_path)
        self.repository = ResearchRepository(self.repository_path, INSTANCE_ID)
        self.initial_head = self.repository.initialize(*current_state({"title": "instance"}))

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_unchanged_state_is_noop_and_returns_normalized_reload_views(self) -> None:
        head, instance, runtime = self.repository.load()
        saved_head, saved_instance, saved_runtime = self.repository.save_with_state(head, instance, runtime)
        reloaded_head, reloaded_instance, reloaded_runtime = self.repository.load(saved_head)
        self.assertEqual(saved_head, head)
        self.assertEqual((saved_head, saved_instance, saved_runtime),
                         (reloaded_head, reloaded_instance, reloaded_runtime))

    def test_changed_state_writes_the_same_canonical_files_and_returns_reload_views(self) -> None:
        head, instance, runtime = self.repository.load()
        changed_runtime = {**runtime, "status": "running"}
        expected = self.repository.validate_candidate(instance, changed_runtime, head)
        saved_head, saved_instance, saved_runtime = self.repository.save_with_state(head, instance, changed_runtime)
        stored = self.repository._store.read_many(saved_head, sorted(expected["files"]))
        self.assertNotEqual(saved_head, head)
        self.assertEqual(stored, expected["files"])
        self.assertEqual((saved_head, saved_instance, saved_runtime), self.repository.load(saved_head))

    def test_regular_save_still_rejects_invalid_input(self) -> None:
        head, instance, runtime = self.repository.load()
        invalid_runtime = {**runtime, "status": float("nan")}
        with self.assertRaises(ValueError):
            self.repository.save_with_state(head, instance, invalid_runtime)[0]
        self.assertEqual(self.repository.load()[0], head)

    def test_save_reads_parent_family_bytes_once_and_preserves_reload_equivalence(self) -> None:
        head, instance, runtime = self.repository.load()
        with patch.object(self.repository._store, 'read_many', wraps=self.repository._store.read_many) as reads:
            saved = self.repository.save_with_state(head, instance, {**runtime, 'status': 'running'})
        self.assertEqual(len([call for call in reads.call_args_list if call.args[0] == head]), 0)
        self.assertEqual(saved, self.repository.load(saved[0]))

    def test_save_rereads_only_new_artifact_evidence(self) -> None:
        head, instance, runtime = self.repository.load()
        ref, raw = "runtime/artifacts/AB-evidence/notes.txt", b"checkpoint evidence"
        runtime["checkpoints"] = {"EX-evidence": {"evidence_files": [{"path": "notes.txt",
            "artifact_ref": ref, "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)}]}}
        head = self.repository.save_with_state(head, instance, runtime, artifacts={ref: raw})[0]
        head, instance, runtime = self.repository.load(head)
        with patch.object(self.repository._store, 'read_many', wraps=self.repository._store.read_many) as reads:
            saved = self.repository.save_with_state(head, instance, {**runtime, 'status': 'running'})
        self.assertFalse(any(ref in call.args[1] for call in reads.call_args_list))
        self.assertEqual(saved, self.repository.load(saved[0]))
        changed = deepcopy(saved[2])
        changed["checkpoints"]["EX-evidence"]["evidence_files"][0]["bytes"] += 1
        with self.assertRaisesRegex(ValueError, "artifact evidence"):
            self.repository.save_with_state(saved[0], saved[1], changed)

    def test_reused_parent_bytes_still_reject_a_damaged_previous_snapshot(self) -> None:
        head, instance, runtime = self.repository.load()
        damaged = self.repository._store.publish(head, {'runtime/_state/metadata.json': b'{}\n'}).head
        with patch.object(self.repository._store, 'publish', wraps=self.repository._store.publish) as publish:
            with self.assertRaises(ValueError):
                self.repository.save_with_state(damaged, instance, runtime)
        publish.assert_not_called()
        self.assertEqual(self.repository._store.read_snapshot().head, damaged)

    def test_stale_head_is_rejected_before_artifact_shape(self) -> None:
        head, instance, runtime = self.repository.load()
        self.repository.save_with_state(head, instance, {**runtime, "status": "running"})
        with self.assertRaises(GitStateStoreConflict):
            self.repository.save_with_state(
                head, instance, runtime, artifacts={"outside-artifacts.txt": b"not allowed"}
            )

    def test_artifact_bytes_and_namespace_are_checked_by_the_same_save_call(self) -> None:
        head, instance, runtime = self.repository.load()
        artifact_path = "runtime/artifacts/AB-01/output.txt"
        artifact_bytes = b"sealed artifact bytes"
        saved_head, _, _ = self.repository.save_with_state(
            head, instance, runtime, artifacts={artifact_path: artifact_bytes}
        )
        self.assertEqual(self.repository.read(artifact_path, saved_head), artifact_bytes)
        reloaded_head, reloaded_instance, reloaded_runtime = self.repository.load(saved_head)
        with self.assertRaises(ValueError):
            self.repository.save_with_state(
                reloaded_head,
                deepcopy(reloaded_instance),
                deepcopy(reloaded_runtime),
                artifacts={"outside-artifacts.txt": b"not allowed"},
            )
        self.assertEqual(self.repository.load()[0], saved_head)


class CandidateCopyTests(unittest.TestCase):
    def test_candidate_numbers_events_without_a_second_whole_state_copy(self):
        instance, runtime = current_state({'title': 'fixture'}, {'events': [{'id': 'EV-1', 'kind': 'created'}]})
        before = deepcopy((instance, runtime))
        with patch.object(repository, 'deepcopy', wraps=deepcopy) as copies:
            candidate = candidate_repository(self).validate_candidate(instance, runtime)
        # One copy of each root; event numbering works on that detached copy.
        self.assertEqual([call.args[0] for call in copies.call_args_list], [instance, runtime])
        self.assertEqual((instance, runtime), before)
        self.assertEqual(candidate['runtime']['events'][0]['event_seq'], 1)
        candidate['runtime']['events'][0]['kind'] = 'changed returned candidate'
        self.assertEqual((instance, runtime), before)

    def test_late_event_failure_never_numbers_the_callers_original(self):
        instance, runtime = current_state(runtime={'events': [
            {'id': 'EV-1', 'kind': 'created'},
            {'id': 'EV-2', 'kind': 'queued', 'event_seq': 99}]})
        before = deepcopy((instance, runtime))
        with self.assertRaisesRegex(ValueError, 'contiguous'):
            candidate_repository(self).validate_candidate(instance, runtime)
        self.assertEqual((instance, runtime), before)


class StorageValueTests(unittest.TestCase):
    def test_value_validation_and_serialization_keep_the_same_domain(self):
        for value in (None, True, False, 0, -(2**53 - 1), 2**53 - 1,
                      {'e\u0301': ['한글', '😀', 1], 'é': None}):
            with self.subTest(value=value):
                self.assertIsNone(repository.validate_storage_value(value))
                self.assertIsInstance(repository.canonical_json(value), bytes)
        invalid = [0.0, float('nan'), float('inf'), float('-inf'), 2**53, -(2**53), '\ud800',
                   {1: 'non-string key'}, {'\udfff': 1}, b'raw', (1,), {'nested': [0.5]}]
        for value in invalid:
            with self.subTest(value=repr(value)):
                with self.assertRaises(ValueError) as checked:
                    repository.validate_storage_value(value)
                with self.assertRaises(ValueError) as encoded:
                    repository.canonical_json(value)
                self.assertEqual(str(checked.exception), str(encoded.exception))
        self.assertNotEqual(repository.canonical_json(True), repository.canonical_json(1))
        self.assertNotEqual(repository.canonical_json({'a': [2, 1]}), repository.canonical_json({'a': [1, 2]}))

    def test_inspection_builds_no_json_bytes_and_publication_checks_the_value_domain(self):
        instance, runtime = {'sources': []}, {'executions': {'EX-1': {'id': 'EX-1', 'output_files': []}}}
        with patch.object(repository, 'canonical_json', side_effect=AssertionError('unused serialization')):
            self.assertEqual(inspect_state(instance, runtime, requested_areas=['record_storage'])['status'], 'healthy')
        # The storage value domain belongs to loading and publication: each
        # record serialized for a candidate passes the storage value check.
        instance, runtime = current_state(runtime={'provider_wake': {'measured': float('nan')}})
        with self.assertRaisesRegex(ValueError, 'floating-point'):
            candidate_repository(self).validate_candidate(instance, runtime)

    def test_a_float_equal_to_the_parent_integer_is_still_rejected(self):
        # 1.0 == 1, so the record equals its parent's and skips its schema check
        # and serialization; sealing the candidate rejects the float first.
        with tempfile.TemporaryDirectory() as directory:
            store = repository.ResearchRepository(git_init(directory), repository.new_id('RI'))
            head = store.initialize(*current_state(runtime={'provider_wake': {'measured': 1}}))
            _, instance, runtime = store.load(head)
            runtime['provider_wake']['measured'] = 1.0
            with self.assertRaisesRegex(ValueError, 'floating-point'):
                store.save_with_state(head, instance, runtime)
            self.assertEqual(store.load()[0], head)


class SealedArtifactReadTests(unittest.TestCase):
    def test_a_sealed_row_is_hashed_once_and_matched_rows_are_not_reread(self):
        import uuid
        raw = b'sealed bytes'
        digest = hashlib.sha256(raw).hexdigest()
        path = 'runtime/artifacts/BA-sealed/output.json'
        engine = bare_engine(head='a' * 40, store=create_autospec(repository.ResearchRepository, instance=True))
        engine.store.git_dir = 'git-' + uuid.uuid4().hex
        engine.store.read.return_value = raw
        with self.assertRaisesRegex(ValueError, 'differs from its record'):
            engine._sealed_bytes(path, 'b' * 64, len(raw))
        self.assertEqual(engine._sealed_bytes(path, digest, len(raw)), raw)
        with patch.object(repository.hashlib, 'sha256', side_effect=AssertionError('matched row rehashed')):
            self.assertEqual(engine._sealed_bytes(path, digest, len(raw)), raw)
            engine.store.read.reset_mock()
            self.assertIsNone(engine._sealed_bytes(path, digest, len(raw), needed=False))
        engine.store.read.assert_not_called()


if __name__ == "__main__":
    unittest.main(verbosity=2)
