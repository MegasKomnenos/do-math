"""Integration tests for immutable Git object state storage in fresh repositories."""

from __future__ import annotations

from pathlib import Path
import random
import subprocess
import sys
import tempfile
import threading
import os
import unittest
from unittest.mock import create_autospec, patch


SCRIPTS = Path(__file__).resolve().parents[1]
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from do_math.git_store import GitStateStore, GitStateStoreConflict, GitStateStoreError, StateSnapshot  # noqa: E402
from research_fixtures import git_init  # noqa: E402


def git_result(returncode, stdout=b'', stderr=b''):
    return subprocess.CompletedProcess(['git'], returncode, stdout, stderr)


INSTANCE_ID = "RI-00000000000000000000000000"


def git(repository: Path, *arguments: str, input: bytes | None = None, env: dict[str, str] | None = None) -> bytes:
    completed = subprocess.run(
        ["git", "-C", str(repository), *arguments],
        input=input,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=None if env is None else {**os.environ, **env},
        check=True,
    )
    return completed.stdout


def loose_objects(repository: Path) -> set[Path]:
    objects = Path(git(repository, "rev-parse", "--git-path", "objects").decode().strip())
    objects = objects if objects.is_absolute() else repository / objects
    return {path for path in objects.glob("??/*") if not path.name.startswith("tmp_obj_")}


class GitStateStoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.repository = Path(self.temporary.name) / "repository"
        self.repository.mkdir()
        git_init(self.repository)
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

    def forget_trees(self) -> None:
        self.store._published = self.store._read = None

    def test_tree_cache_reuses_only_immutable_oids(self):
        snapshot = self.store.publish(None, self.initial_changes())
        self.forget_trees()
        with patch.object(self.store, '_git', wraps=self.store._git) as calls:
            first = self.store._tree_paths(snapshot.head)
            second = self.store._tree_paths(snapshot.head)
        self.assertEqual(first, second)
        self.assertEqual(sum(c.args[0] == 'ls-tree' for c in calls.call_args_list), 1)

    def test_own_publication_lists_the_new_tree_without_enumerating_it(self):
        first = self.store.publish(None, {**self.initial_changes(), 'runtime/artifacts/one/a.bin': b'a'})
        with patch.object(self.store, '_git', wraps=self.store._git) as calls:
            later = self.store.publish(first.head, {'runtime/state.json': None, 'research/next.json': b'{}\n',
                                                    'runtime/artifacts/two/b.bin': b'b'})
            listed = self.store._tree_paths(later.head)
        # The parent list also came from its own publication.
        self.assertEqual(sum(c.args[0] == 'ls-tree' for c in calls.call_args_list), 0)
        # Reading an older snapshot does not displace the tree just published.
        self.store._tree_paths(first.head)
        with patch.object(self.store, '_git', wraps=self.store._git) as calls:
            self.store.publish(later.head, {'research/again.json': b'{}\n'})
        self.assertEqual([c.args[0] for c in calls.call_args_list], ['update-ref'])
        self.forget_trees()
        self.assertEqual(listed, self.store._tree_paths(later.head))

    def test_publication_writes_objects_in_process_and_moves_the_ref_only_by_cas(self):
        first = self.store.publish(None, self.initial_changes())
        before = loose_objects(self.repository)
        with patch.object(self.store, '_git', wraps=self.store._git) as calls, \
             patch('do_math.git_store.os.fsync', wraps=os.fsync) as fsync:
            later = self.store.publish(first.head, {'runtime/state.json': b'{"state": "running"}\n',
                                                    'research/new/deep.json': b'{}\n'})
        self.assertEqual([c.args[0] for c in calls.call_args_list], ['update-ref'])
        # Installed Git for Windows flushes each new loose object (core.fsyncObjectFiles=true).
        created = loose_objects(self.repository) - before
        self.assertEqual(fsync.call_count, len(created))
        self.assertEqual(self.store.read_bytes(later.head, 'research/new/deep.json'), b'{}\n')

    def test_concurrent_writers_of_one_object_all_succeed(self):
        barrier = threading.Barrier(4)
        results: list[list[str]] = []

        def write() -> None:
            barrier.wait()
            results.append([self.store._write_object(b"blob", b"same bytes %d\n" % number) for number in range(20)])

        threads = [threading.Thread(target=write) for _ in range(4)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(20)
        self.assertEqual(len(results), 4)
        self.assertEqual(len({tuple(oids) for oids in results}), 1)
        listed = git(self.repository, "cat-file", "--batch-check", input="".join(f"{oid}\n" for oid in results[0]).encode())
        self.assertEqual(listed.decode().split().count("blob"), 20)
        objects = Path(git(self.repository, "rev-parse", "--git-path", "objects").decode().strip())
        objects = objects if objects.is_absolute() else self.repository / objects
        self.assertEqual(list(objects.glob("??/tmp_obj_*")), [])

    def test_path_that_is_also_a_directory_is_rejected_before_git_drops_it(self):
        first = self.store.publish(None, {**self.initial_changes(), 'research/a': b'file'})
        with self.assertRaisesRegex(ValueError, 'both a file and a directory'):
            self.store.publish(first.head, {'research/a/b': b'child'})
        with self.assertRaisesRegex(ValueError, 'both a file and a directory'):
            self.store._validate_candidate_paths({'research/x', 'research/x/y'})
        self.assertEqual(self.store.read_snapshot().head, first.head)

    def test_physical_boundary_is_proved_on_open_and_after_git_errors_only(self):
        snapshot = self.store.publish(None, self.initial_changes())
        changed = ValueError('boundary changed')
        with patch.object(self.store._repository_boundary, 'check', side_effect=changed) as repository_check, \
             patch.object(self.store._git_boundary, 'check', side_effect=changed) as git_check:
            later = self.store.publish(snapshot.head, {'runtime/state.json': b'{"state": "running"}\n'})
            self.assertEqual(self.store.read_many(later.head, ['runtime/state.json']),
                             {'runtime/state.json': b'{"state": "running"}\n'})
            self.assertEqual((repository_check.call_count, git_check.call_count), (0, 0))
            with self.assertRaisesRegex(ValueError, 'boundary changed'):
                self.store.read_bytes(later.head, 'runtime/absent.json')

    def test_writer_lock_leaves_the_final_cas_as_the_only_ref_comparison(self):
        first = self.store.publish(None, self.initial_changes())
        with self.store.writer_lock():
            with patch.object(self.store, '_git', wraps=self.store._git) as calls:
                later = self.store.publish(first.head, {'runtime/state.json': b'{"state": "running"}\n'})
            ref_reads = [c for c in calls.call_args_list if c.args[0] in {'rev-parse', 'update-ref'}
                         or c.args[:2] == ('cat-file', '-t')]
            self.assertEqual([c.args[0] for c in ref_reads], ['update-ref'])
            # Under the lock no do-math writer moves the ref, so the head this
            # store just published is not read back.
            with patch.object(self.store, '_git', wraps=self.store._git) as calls:
                self.assertEqual(self.store.read_snapshot(), StateSnapshot(later.head))
            self.assertEqual(calls.call_count, 0)
            # A writer outside the lock is still refused by that final CAS.
            outside = GitStateStore(self.repository, INSTANCE_ID)
            moved = outside.publish(later.head, {'runtime/state.json': b'{"state": "moved"}\n'})
            with self.assertRaisesRegex(GitStateStoreConflict, 'publish compare-and-swap'):
                self.store.publish(later.head, {'runtime/state.json': b'{"state": "lost"}\n'})
            # The failed CAS proves the remembered head stale; it is read again.
            self.assertEqual(self.store.read_snapshot().head, moved.head)
        with patch.object(self.store, '_git', wraps=self.store._git) as calls:
            self.assertEqual(self.store.read_snapshot().head, moved.head)
        self.assertEqual(calls.call_count, 1)

    def test_unicode_artifact_path_preserves_the_supplied_code_points(self):
        path = "runtime/artifacts/one/e\u0301.txt"
        snapshot = self.store.publish(None, {**self.initial_changes(), path: b"raw"})
        self.assertEqual(self.store.read_bytes(snapshot.head, path), b"raw")
        self.assertIn(path, self.store._tree_paths(snapshot.head))
        self.assertNotIn("runtime/artifacts/one/\u00e9.txt", self.store._tree_paths(snapshot.head))

    def test_many_blobs_use_no_hash_process_and_preserve_raw_bytes(self):
        (self.repository / '.gitattributes').write_text('* text eol=lf\n', encoding='utf-8')
        changes = {**self.initial_changes(), **{
            f'runtime/artifacts/batch/자료 {i}.bin': bytes(range(256)) + b'\r\n\x00' + bytes([i])
            for i in range(38)}}
        with patch.object(self.store, '_git', wraps=self.store._git) as calls:
            snapshot = self.store.publish(None, changes)
        self.assertEqual([c.args[0] for c in calls.call_args_list], ['update-ref'])
        self.assertEqual(self.store.read_many(snapshot.head, list(changes)), changes)

    def test_batch_read_is_exact_and_missing_blob_is_an_error(self):
        changes = {**self.initial_changes(), 'runtime/artifacts/batch/빈 파일': b'',
                   'runtime/artifacts/batch/바이너리': b'\x00\xff\n\r\nblob missing\n'}
        snapshot = self.store.publish(None, changes)
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

        research_tree = lambda commit: git(self.repository, "rev-parse", f"{commit}:research").strip()
        self.assertEqual(research_tree(later.head), research_tree(initial.head))
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
        boundary = git_store.PhysicalBoundary(self.repository)
        file = self.repository / "boundary.bin"
        with boundary.open(file, "xb") as stream:
            stream.write(b"bounded")
        with boundary.open(file, "rb") as stream:
            self.assertEqual(stream.read(), b"bounded")
        outside = Path(self.temporary.name) / "outside.bin"
        with self.assertRaises(ValueError):
            boundary.open(outside, "xb").__enter__()
        with self.assertRaises(ValueError):
            boundary.open(self.repository / ".." / "outside.bin", "xb").__enter__()

    def test_physical_boundary_refuses_a_reparse_point_below_its_root(self):
        from do_math import git_store
        root = Path(self.temporary.name) / "bounded"
        target = Path(self.temporary.name) / "elsewhere"
        root.mkdir()
        target.mkdir()
        (target / "file.bin").write_bytes(b"outside")
        boundary = git_store.PhysicalBoundary(root)
        link = root / "link"
        if os.name == "nt":
            created = subprocess.run(["cmd.exe", "/d", "/c", "mklink", "/J", str(link), str(target)], capture_output=True)
            self.assertEqual(created.returncode, 0, created.stderr)
        else:
            link.symlink_to(target, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "reparse|symlink"):
            boundary.open(link / "file.bin", "rb").__enter__()

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


class InProcessObjectsMatchGitPlumbingTests(unittest.TestCase):
    """Differential check of the in-process writer against Git's own index plumbing."""

    # Names whose order flips at the "/" a subtree name sorts with, plus non-ASCII.
    NAMES = ("a", "a.b", "a-b", "a0", "b", "é")
    GIT_DEFAULTS = {"GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull}

    @staticmethod
    def valid(paths) -> bool:
        directories = {path[:end] for path in paths for end in range(len(path)) if path[end] == "/"}
        return not directories & set(paths)

    def random_changes(self, rng: random.Random, model: dict[str, bytes]) -> dict[str, bytes | None]:
        """Adds, edits, deletes (some emptying a directory), directory-path deletes, file<->directory swaps."""
        proposals: list[dict[str, bytes | None]] = []
        files = sorted(path for path in model if not path.endswith("/keep"))
        if files:
            victim = rng.choice(files)
            proposals.append({victim: None, victim + "/a": b"file became directory"})
        directories = sorted({path.rpartition("/")[0] for path in files if path.count("/") >= 2})
        if directories:
            replaced = rng.choice(directories)
            below = {path: None for path in model if path.startswith(replaced + "/")}
            proposals.append({**below, replaced: b"directory became file"})
            others = [path for path in directories if path != replaced and not path.startswith(replaced + "/")]
            if others:
                proposals.append({rng.choice(others): None})  # names a directory: no file to delete
        for _ in range(10):
            roll = rng.random()
            if files and roll < 0.3:
                proposals.append({rng.choice(files): None})
            elif files and roll < 0.5:
                proposals.append({rng.choice(files): rng.randbytes(rng.randint(0, 24))})
            else:
                parts = [rng.choice(("research", "runtime")), *(rng.choice(self.NAMES) for _ in range(rng.randint(1, 3)))]
                proposals.append({"/".join(parts): rng.randbytes(rng.randint(0, 24))})
        changes: dict[str, bytes | None] = {}
        for proposal in proposals:
            candidate = {**changes, **proposal}
            paths = {path for path in model if candidate.get(path, model[path]) is not None}
            paths |= {path for path, raw in candidate.items() if raw is not None}
            if self.valid(paths):
                changes = candidate
        return changes

    def oracle_tree(self, repository: Path, index: dict[str, str], changes: dict[str, bytes | None], width: int) -> str:
        """Apply the same changes to a persistent index, deletions first, and let Git write the tree."""
        with tempfile.TemporaryDirectory() as directory:
            added = [(path, raw) for path, raw in changes.items() if raw is not None]
            for number, (_, raw) in enumerate(added):
                (Path(directory) / str(number)).write_bytes(raw)
            names = "".join(f"{(Path(directory) / str(number)).as_posix()}\n" for number in range(len(added))).encode()
            oids = git(repository, "hash-object", "--no-filters", "--stdin-paths", input=names).decode().split() if added else []
        records = [f"0 {'0' * width}\t{path}" for path, raw in changes.items() if raw is None]
        records += [f"100644 {oid}\t{path}" for (path, _), oid in zip(added, oids)]
        git(repository, "update-index", "-z", "--index-info", input="".join(record + "\0" for record in records).encode(), env=index)
        return git(repository, "write-tree", env=index).decode().strip()

    def check(self, object_format: str) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repository = Path(temporary) / "repository"
            repository.mkdir()
            if object_format == "sha1":
                git_init(repository)
            else:
                git(repository, "init", "-q", f"--object-format={object_format}")
            index = {"GIT_INDEX_FILE": str(Path(temporary) / "oracle-index")}
            rng = random.Random("do-math-" + object_format)
            store = GitStateStore(repository, INSTANCE_ID)
            model: dict[str, bytes] = {}
            head, heads, expected = None, [], []
            for round_number in range(4):
                changes = self.random_changes(rng, model)
                if head is None:
                    changes.update({"research/keep": b"k", "runtime/keep": b"k"})
                if round_number == 2:
                    store = GitStateStore(repository, INSTANCE_ID)  # parent tree read through ls-tree
                head = store.publish(head, changes).head
                for path, raw in changes.items():
                    if raw is None:
                        model.pop(path, None)
                    else:
                        model[path] = raw
                self.assertEqual(store._tree_paths(head), set(model))
                heads.append(head)
                expected.append(self.oracle_tree(repository, index, changes, store.oid_length))
            trees = git(repository, "rev-parse", *(f"{commit}^{{tree}}" for commit in heads)).decode().split()
            self.assertEqual(trees, expected)
            self.assertEqual(store.read_many(head, sorted(model)), model)
            for commit, parent in ((heads[0], None), (heads[-1], heads[-2])):
                seconds, zone = git(repository, "cat-file", "commit", commit).decode().split("\ncommitter ")[1].split("\n")[0].split()[-2:]
                identity = {"GIT_AUTHOR_NAME": "do-math", "GIT_AUTHOR_EMAIL": "do-math@invalid",
                            "GIT_COMMITTER_NAME": "do-math", "GIT_COMMITTER_EMAIL": "do-math@invalid",
                            "GIT_AUTHOR_DATE": f"{seconds} {zone}", "GIT_COMMITTER_DATE": f"{seconds} {zone}"}
                arguments = ["-c", "commit.gpgSign=false", "commit-tree", f"{commit}^{{tree}}", *(["-p", parent] if parent else [])]
                oracle = git(repository, *arguments, input=b"do-math state\n", env={**self.GIT_DEFAULTS, **identity})
                self.assertEqual(oracle.decode().strip(), commit)
            checked = subprocess.run(["git", "-C", str(repository), "fsck", "--strict", "--no-progress"],
                                     capture_output=True, env={**os.environ, **self.GIT_DEFAULTS})
            # Only the unborn-HEAD notice may appear; any object finding fails.
            findings = [line for line in (checked.stdout + checked.stderr).decode().splitlines()
                        if not line.startswith("notice: HEAD points to an unborn branch")]
            self.assertEqual((checked.returncode, findings), (0, []))

    def test_sha1_trees_and_commits_match_git(self) -> None:
        self.check("sha1")

    def test_sha256_trees_and_commits_match_git(self) -> None:
        self.check("sha256")


class SnapshotMetadataTests(unittest.TestCase):
    INSTANCE = 'RI-01ARZ3NDEKTSV4RRFFQ69G5FAV'
    REF = 'refs/heads/do-math/' + INSTANCE

    def setUp(self):
        self.repository = git_init(Path(self.enterContext(tempfile.TemporaryDirectory())))

    def store(self, *, length=40, root_type='commit', rows=None, returncode=0, resolved=None):
        """A store over an empty repository whose later Git calls answer with the given metadata."""
        store = GitStateStore(self.repository, self.INSTANCE)
        store.object_format = 'sha1' if length == 40 else 'sha256'
        head, research, runtime = ('a' * length, 'b' * length, 'c' * length)
        values = rows if rows is not None else [head + ' ' + root_type, research + ' tree', runtime + ' tree']
        if resolved is None:
            resolved = git_result(0, (head + '\n').encode())
        # One batch query; rev-parse (``resolved``) runs only when the ref line is missing.
        store._git = create_autospec(store._git, side_effect=[
            git_result(returncode, ('\n'.join(values) + '\n').encode()), resolved])
        return store, head

    def test_one_batch_reads_the_ref_and_both_subtrees(self):
        for length in (40, 64):
            with self.subTest(length=length):
                store, head = self.store(length=length)
                self.assertEqual(store.read_snapshot(), StateSnapshot(head))
                self.assertEqual(store._git.call_count, 1)
                request = store._git.call_args
                self.assertEqual(request.args, ('cat-file', '--batch-check=%(objectname) %(objecttype)'))
                self.assertEqual(request.kwargs['input'],
                                 f'{self.REF}\n{self.REF}:research\n{self.REF}:runtime\n'.encode())

    def test_absent_ref_is_none_but_corrupt_ref_is_rejected(self):
        missing = [self.REF + suffix + ' missing' for suffix in ('', ':research', ':runtime')]
        store, _ = self.store(rows=missing, resolved=git_result(1))
        self.assertEqual(store.read_snapshot(), StateSnapshot(None))
        self.assertEqual([call.args[0] for call in store._git.call_args_list], ['cat-file', 'rev-parse'])
        store, _ = self.store(rows=missing, resolved=git_result(1, stderr=b'bad ref'))
        with self.assertRaisesRegex(GitStateStoreError, 'cannot resolve'):
            store.read_snapshot()

    def test_wrong_or_incomplete_metadata_never_returns_a_snapshot(self):
        head, tree, ref = 'a' * 40, 'b' * 40, self.REF
        cases = [([head + ' blob', ref + ':research missing', ref + ':runtime missing'], 'commit'),
                 ([ref + ' missing'], 'unreadable'),
                 ([head + ' commit extra', tree + ' tree', tree + ' tree'], 'invalid state commit'),
                 ([head + ' commit', ref + ':research missing', tree + ' tree'], 'research'),
                 ([head + ' commit', tree + ' blob', tree + ' tree'], 'tree'),
                 ([head + ' commit', tree + ' tree'], 'incomplete'),
                 ([head + ' commit', tree + ' tree', tree + ' tree', tree + ' tree'], 'incomplete')]
        for rows, message in cases:
            with self.subTest(rows=rows):
                store, _ = self.store(rows=rows)
                with self.assertRaisesRegex(GitStateStoreError, message):
                    store.read_snapshot()
        store, _ = self.store(returncode=1)
        with self.assertRaises(GitStateStoreError):
            store.read_snapshot()


if __name__ == "__main__":
    unittest.main(verbosity=2)
