"""Integration tests for immutable Git object state storage in fresh repositories."""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import os
import unittest
from unittest.mock import patch


SCRIPTS = Path(__file__).resolve().parents[1]
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from do_math.git_store import GitStateStore, GitStateStoreConflict, GitStateStoreError  # noqa: E402


INSTANCE_ID = "RI-00000000000000000000000000"


def git(repository: Path, *arguments: str, input: bytes | None = None) -> bytes:
    completed = subprocess.run(
        ["git", "-C", str(repository), *arguments],
        input=input,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    return completed.stdout


class GitStateStoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.repository = Path(self.temporary.name) / "repository"
        self.repository.mkdir()
        git(self.repository, "init", "-q")
        self.store = GitStateStore(self.repository, INSTANCE_ID)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def initial_changes(self) -> dict[str, bytes]:
        return {
            "research/instance.json": b'{"revision": 1}\n',
            "runtime/state.json": b'{"state": "initializing"}\n',
        }

    def test_oid_shape_is_separate_from_instance_format(self):
        from do_math.git_store import oid_shape
        self.assertEqual(oid_shape("a" * 64), "sha256")
        with self.assertRaises(ValueError):
            self.store._validate_oid("a" * 64)
        with self.assertRaises(ValueError):
            oid_shape("A" * 40)

    def test_unicode_artifact_path_preserves_the_supplied_code_points(self):
        path = "runtime/artifacts/one/e\u0301.txt"
        snapshot = self.store.publish(None, {**self.initial_changes(), path: b"raw"})
        self.assertEqual(self.store.read_bytes(snapshot.head, path), b"raw")
        self.assertIn(path, self.store._tree_paths(snapshot.head))
        self.assertNotIn("runtime/artifacts/one/\u00e9.txt", self.store._tree_paths(snapshot.head))

    def test_many_blobs_use_one_hash_process_and_preserve_raw_bytes(self):
        (self.repository / '.gitattributes').write_text('* text eol=lf\n', encoding='utf-8')
        changes = {**self.initial_changes(), **{
            f'runtime/artifacts/batch/자료 {i}.bin': bytes(range(256)) + b'\r\n\x00' + bytes([i])
            for i in range(38)}}
        with patch.object(self.store, '_git', wraps=self.store._git) as calls:
            snapshot = self.store.publish(None, changes)
        hashes = [c for c in calls.call_args_list if c.args[0] == 'hash-object']
        self.assertEqual(len(hashes), 1)
        for path, raw in changes.items():
            self.assertEqual(self.store.read_bytes(snapshot.head, path), raw)

    def test_batch_read_is_exact_and_missing_blob_is_an_error(self):
        changes = {**self.initial_changes(), 'runtime/artifacts/batch/빈 파일': b'',
                   'runtime/artifacts/batch/바이너리': b'\x00\xff\n\r\nblob missing\n'}
        snapshot = self.store.publish(None, changes)
        self.assertTrue(callable(getattr(self.store, 'read_many', None)), 'batch read is required')
        with patch.object(self.store, '_git', wraps=self.store._git) as calls:
            values = self.store.read_many(snapshot.head, list(changes))
        self.assertEqual(values, changes)
        self.assertEqual(len(calls.call_args_list), 1)
        self.assertEqual(self.store.read_many(snapshot.head, []), {})
        with self.assertRaises(GitStateStoreError):
            self.store.read_many(snapshot.head, ['research/instance.json', 'runtime/absent'])

    def test_initial_commit_has_no_parent_and_later_commit_has_one_parent(self) -> None:
        initial = self.store.publish(None, self.initial_changes())
        self.assertIsNotNone(initial.head)
        self.assertEqual(len(initial.head), 40)
        self.assertEqual(git(self.repository, "rev-list", "--parents", "-n", "1", initial.head).split(), [initial.head.encode()])

        later = self.store.publish(initial.head, {"runtime/state.json": b'{"state": "running"}\n'})
        self.assertEqual(
            git(self.repository, "rev-list", "--parents", "-n", "1", later.head).split(),
            [later.head.encode(), initial.head.encode()],
        )

    def test_runtime_only_update_preserves_research_tree_and_old_snapshot_bytes(self) -> None:
        initial = self.store.publish(None, self.initial_changes())
        later = self.store.publish(initial.head, {"runtime/state.json": b'{"state": "running"}\n'})

        self.assertEqual(later.research_tree, initial.research_tree)
        self.assertEqual(self.store.read_bytes(initial.head, "runtime/state.json"), self.initial_changes()["runtime/state.json"])
        self.assertEqual(self.store.read_bytes(later.head, "runtime/state.json"), b'{"state": "running"}\n')

    def test_simultaneous_stale_cas_has_one_winner_and_no_overwrite(self) -> None:
        initial = self.store.publish(None, self.initial_changes())
        barrier = threading.Barrier(2)
        results: list[tuple[str, object]] = []
        results_lock = threading.Lock()

        def publish(label: str) -> None:
            local = GitStateStore(self.repository, INSTANCE_ID)
            barrier.wait()
            try:
                snapshot = local.publish(initial.head, {"runtime/state.json": label.encode()})
                result: tuple[str, object] = ("published", snapshot)
            except GitStateStoreConflict as error:
                result = ("conflict", error)
            with results_lock:
                results.append(result)

        left = threading.Thread(target=publish, args=("left",))
        right = threading.Thread(target=publish, args=("right",))
        left.start()
        right.start()
        left.join(20)
        right.join(20)
        self.assertFalse(left.is_alive())
        self.assertFalse(right.is_alive())
        self.assertEqual([kind for kind, _ in results].count("published"), 1)
        self.assertEqual([kind for kind, _ in results].count("conflict"), 1)
        self.assertIn(self.store.read_bytes(self.store.read_snapshot().head, "runtime/state.json"), (b"left", b"right"))

    def test_publish_does_not_change_worktree_or_default_index(self) -> None:
        initial = self.store.publish(None, self.initial_changes())
        user_file = self.repository / "user.txt"
        user_file.write_bytes(b"staged user change\n")
        git(self.repository, "add", "user.txt")
        index = Path(git(self.repository, "rev-parse", "--git-path", "index").decode().strip())
        if not index.is_absolute():
            index = self.repository / index
        before_index = index.read_bytes()

        self.store.publish(initial.head, {"runtime/state.json": b'{"state": "running"}\n'})

        self.assertEqual(user_file.read_bytes(), b"staged user change\n")
        self.assertEqual(index.read_bytes(), before_index)
        self.assertEqual(list(self.store._git_dir.glob("do-math-index-*")), [])

    def test_publish_does_not_execute_repository_hook(self) -> None:
        hook_directory = self.repository / "hostile-hooks"
        hook_directory.mkdir()
        marker = self.repository / "hook-ran"
        hook = hook_directory / "reference-transaction"
        hook.write_text(f"#!/bin/sh\necho invoked > '{marker.as_posix()}'\n", encoding="utf-8")
        hook.chmod(0o755)
        git(self.repository, "config", "core.hooksPath", str(hook_directory))

        self.store.publish(None, self.initial_changes())

        self.assertFalse(marker.exists())

    def test_writer_lock_is_an_os_lock_without_stale_pid_contents(self) -> None:
        with self.store.writer_lock():
            snapshot = self.store.publish(None, self.initial_changes())
        lock_path = self.store._git_dir / f"do-math-{INSTANCE_ID}.lock"
        self.assertEqual(lock_path.read_bytes(), b"\0")
        self.assertEqual(self.store.read_snapshot().head, snapshot.head)

    def test_existing_artifact_bundle_cannot_be_changed_or_deleted(self) -> None:
        initial = self.store.publish(None, {
            **self.initial_changes(),
            "runtime/artifacts/bundle_01/output.txt": b"sealed\n",
        })
        with self.assertRaises(ValueError):
            self.store.publish(initial.head, {"runtime/artifacts/bundle_01/output.txt": b"altered\n"})
        with self.assertRaises(ValueError):
            self.store.publish(initial.head, {"runtime/artifacts/bundle_01/output.txt": None})
        self.assertEqual(self.store.read_snapshot().head, initial.head)

    def test_invalid_and_case_colliding_paths_are_rejected(self) -> None:
        invalid_paths = (
            "research/../escape.txt",
            "research/back\\slash.txt",
            "research/CON.txt",
            "research/trailing. ",
            "/research/absolute.txt",
        )
        for path in invalid_paths:
            with self.subTest(path=path), self.assertRaises(ValueError):
                self.store.publish(None, {path: b"x", "runtime/state.json": b"{}"})
        with self.assertRaises(ValueError):
            self.store.publish(None, {
                "research/A.txt": b"one",
                "research/a.txt": b"two",
                "runtime/state.json": b"{}",
            })

    def test_case_colliding_directory_segments_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            self.store.publish(None, {
                "research/Foo/a.txt": b"one",
                "research/foo/b.txt": b"two",
                "runtime/state.json": b"{}",
            })

    def test_only_registry_instance_ids_are_accepted_before_ref_use(self) -> None:
        with self.assertRaises(ValueError):
            GitStateStore(self.repository, "inst_01")

    def test_repository_junction_is_rejected_before_resolve(self):
        link = Path(self.temporary.name) / "repository-link"
        if os.name == "nt":
            created = subprocess.run(["cmd.exe", "/d", "/c", "mklink", "/J", str(link), str(self.repository)], capture_output=True)
            self.assertEqual(created.returncode, 0, created.stderr)
        else:
            link.symlink_to(self.repository, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "reparse|symlink"):
            GitStateStore(link, INSTANCE_ID)

    def test_physical_file_boundary_checks_opened_handle(self):
        from do_math import git_store
        self.assertTrue(hasattr(git_store, "PhysicalBoundary"))
        boundary = git_store.PhysicalBoundary(self.repository)
        file = self.repository / "boundary.bin"
        with boundary.open(file, "xb") as stream:
            stream.write(b"bounded")
        with boundary.open(file, "rb") as stream:
            self.assertEqual(stream.read(), b"bounded")
        outside = Path(self.temporary.name) / "outside.bin"
        with self.assertRaises(ValueError):
            boundary.open(outside, "xb").__enter__()

    def test_non_commit_or_corrupt_existing_ref_is_not_treated_as_absent(self) -> None:
        blob = git(self.repository, "hash-object", "-w", "--stdin", input=b"not a commit").decode().strip()
        corrupt_path = self.store._git_dir / self.store.ref
        corrupt_path.parent.mkdir(parents=True, exist_ok=True)
        corrupt_path.write_text(blob + "\n", encoding="ascii")
        with self.assertRaises(GitStateStoreError):
            self.store.read_snapshot()

        corrupt_path.write_text("not-an-object-id\n", encoding="ascii")
        with self.assertRaises(GitStateStoreError):
            self.store.read_snapshot()


class GitStateStoreSha256Tests(unittest.TestCase):
    def test_sha256_repository_uses_64_character_oids(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repository = Path(temporary) / "sha256"
            repository.mkdir()
            git(repository, "init", "--object-format=sha256", "-q")
            store = GitStateStore(repository, INSTANCE_ID)
            snapshot = store.publish(None, {
                "research/instance.json": b"{}\n",
                "runtime/state.json": b"{}\n",
            })
            self.assertEqual(store.object_format, "sha256")
            self.assertEqual(len(snapshot.head), 64)
            with self.assertRaises(ValueError):
                store.read_bytes("0" * 40, "runtime/state.json")


if __name__ == "__main__":
    unittest.main(verbosity=2)
