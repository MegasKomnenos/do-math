"""Snapshot-facing repository tests using only fresh temporary Git repositories."""

from __future__ import annotations

import math
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest
import base64


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
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.repository_path = self.root / "repository"
        self.repository_path.mkdir()
        import subprocess

        subprocess.run(["git", "-C", str(self.repository_path), "init", "-q"], check=True)
        self.repository = ResearchRepository(self.repository_path, INSTANCE_ID)
        self.initial_head = self.repository.initialize({"name": "instance", "revision": 1}, {"state": "initializing"})

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_initialize_load_save_and_exact_old_snapshot_read(self) -> None:
        head, instance, runtime = self.repository.load()
        self.assertEqual(head, self.initial_head)
        self.assertEqual(instance, {"name": "instance", "revision": 1})
        self.assertEqual(runtime, {"state": "initializing"})

        later = self.repository.save(head, instance, {"state": "active"})
        self.assertEqual(self.repository.load(self.initial_head)[2], {"state": "initializing"})
        self.assertEqual(self.repository.read("runtime/state.json", later), canonical_json({"state": "active"}))

    def test_stale_save_conflict_does_not_overwrite(self) -> None:
        second = ResearchRepository(self.repository_path, INSTANCE_ID)
        winner = self.repository.save(self.initial_head, {"name": "instance", "revision": 1}, {"state": "winner"})
        with self.assertRaises(GitStateStoreConflict):
            second.save(self.initial_head, {"name": "instance", "revision": 1}, {"state": "loser"})
        self.assertEqual(self.repository.load(winner)[2], {"state": "winner"})

    def test_new_artifact_bundle_is_saved_with_state_and_existing_bundle_is_immutable(self) -> None:
        first = self.repository.save(
            self.initial_head,
            {"name": "instance", "revision": 1},
            {"state": "running"},
            artifacts={"runtime/artifacts/AB-01/output.txt": b"sealed"},
        )
        with self.assertRaises(ValueError):
            self.repository.save(
                first,
                {"name": "instance", "revision": 1},
                {"state": "running"},
                artifacts={"runtime/artifacts/AB-01/other.txt": b"forbidden"},
            )
        later = self.repository.save(
            first,
            {"name": "instance", "revision": 1},
            {"state": "ended"},
            artifacts={"runtime/artifacts/AB-02/output.txt": b"new bundle"},
        )
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
        self.assertEqual(self.repository.list_files("research/"), ["research/instance.json"])
        self.assertEqual(self.repository.list_files("runtime/"), ["runtime/state.json"])
        with self.assertRaises(ValueError):
            self.repository.list_files("../")

    def test_duplicate_json_and_nonfinite_values_are_rejected(self) -> None:
        bad_head = self.repository._store.publish(self.initial_head, {
            "research/instance.json": b'{"name":"first","name":"second"}\n',
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
        self.assertEqual(result["files"], ["research/instance.json"])
        self.assertEqual((destination / "research" / "instance.json").read_bytes(), canonical_json({"name": "instance", "revision": 1}))
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


if __name__ == "__main__":
    unittest.main(verbosity=2)
