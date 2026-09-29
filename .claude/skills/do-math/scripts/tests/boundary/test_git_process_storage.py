"""GitStateStore over the real git process (``git_process.GitProcess``): what installed Git adds to the store's rules.

The store's own rules run on the in-process fake (``unit/test_git_state_store.py``).
Here the Git backend port's real implementation writes loose objects in this
process and runs one git process per read or ref move; Git itself is the
oracle for what the store wrote (trees, commits, ``fsck``), and hooks, the
index and attributes of a real repository must not touch a publication.
Processes are counted by their ``subprocess.Popen`` audit events. ``os.fsync``
raises no audit event, so a spy that calls the real function counts the
flushes.
"""
from __future__ import annotations

import os
from pathlib import Path
import random
import re
import shlex
import subprocess
import tempfile
import threading
import unittest
from unittest.mock import patch

from do_math.git_store import GitStateStore, GitStateStoreConflict, GitStateStoreError, StateSnapshot
from do_math.wiring import real_ports
from research_fixtures import git_init
from support.storage_files import audit_events

INSTANCE_ID = "RI-00000000000000000000000000"
REF = 'refs/heads/do-math/' + INSTANCE_ID


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


def real_store(repository: Path) -> GitStateStore:
    """The store with the product's real Git backend and clock, as the entry points assemble them."""
    ports = real_ports()
    return GitStateStore(repository, INSTANCE_ID, backend=ports.git_backend, clock=ports.clock)


def argument_list(arguments) -> list[str]:
    """A started process's arguments; on Windows the audit event carries the ``list2cmdline`` string."""
    if not isinstance(arguments, str):
        return [str(value) for value in arguments]
    # list2cmdline quotes only arguments with blanks, and these hold no quotes of their own.
    return [token[1:-1] if len(token) > 1 and token[0] == token[-1] == '"' else token
            for token in shlex.split(arguments, posix=False)]


def git_runs(events) -> list[list[str]]:
    """The argument lists after ``git`` and its ``-C``/``-c`` options, one per git process started."""
    runs = []
    for _, arguments in events:
        argv = argument_list(arguments[1])
        if Path(argv[0]).stem.lower() != 'git':
            continue
        position = 1
        while position < len(argv) and argv[position] in ('-C', '-c'):
            position += 2
        runs.append(argv[position:])
    return runs


def git_commands(events) -> list[str]:
    return [run[0] for run in git_runs(events)]


class GitProcessStoreTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.temporary = Path(temporary.name)
        self.repository = self.temporary / "repository"
        self.repository.mkdir()
        git_init(self.repository)
        self.store = real_store(self.repository)

    def initial_changes(self) -> dict[str, bytes]:
        return {
            "research/instance.json": b'{"revision": 1}\n',
            "runtime/state.json": b'{"state": "initializing"}\n',
        }

    def test_publication_writes_objects_in_process_and_moves_the_ref_only_by_cas(self):
        first = self.store.publish(None, self.initial_changes())
        before = loose_objects(self.repository)
        with audit_events('subprocess.Popen') as events, patch('os.fsync', wraps=os.fsync) as fsync:
            later = self.store.publish(first.head, {'runtime/state.json': b'{"state": "running"}\n',
                                                    'research/new/deep.json': b'{}\n'})
        self.assertEqual(git_commands(events), ['update-ref'])
        # Installed Git for Windows flushes each new loose object (core.fsyncObjectFiles=true).
        created = loose_objects(self.repository) - before
        self.assertTrue(created)
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
        listed = git(self.repository, "cat-file", "--batch-check",
                     input="".join(f"{oid}\n" for oid in results[0]).encode())
        self.assertEqual(listed.decode().split().count("blob"), 20)
        objects = Path(git(self.repository, "rev-parse", "--git-path", "objects").decode().strip())
        objects = objects if objects.is_absolute() else self.repository / objects
        self.assertEqual(list(objects.glob("??/tmp_obj_*")), [])

    def test_many_blobs_use_no_hash_process_and_preserve_raw_bytes(self):
        (self.repository / '.gitattributes').write_text('* text eol=lf\n', encoding='utf-8')
        changes = {**self.initial_changes(), **{
            f'runtime/artifacts/batch/자료 {i}.bin': bytes(range(256)) + b'\r\n\x00' + bytes([i])
            for i in range(38)}}
        with audit_events('subprocess.Popen') as events:
            snapshot = self.store.publish(None, changes)
        self.assertEqual(git_commands(events), ['update-ref'])
        self.assertEqual(self.store.read_many(snapshot.head, list(changes)), changes)

    def test_unicode_artifact_path_preserves_the_supplied_code_points(self):
        path = "runtime/artifacts/one/e\u0301.txt"
        snapshot = self.store.publish(None, {**self.initial_changes(), path: b"raw"})
        self.assertEqual(self.store.read_bytes(snapshot.head, path), b"raw")
        self.store._published = self.store._read = None  # list the tree through git ls-tree
        paths = self.store.tree_paths(snapshot.head)
        self.assertIn(path, paths)
        self.assertNotIn("runtime/artifacts/one/é.txt", paths)

    def test_a_forgotten_tree_is_listed_by_one_git_process_and_then_reused(self):
        snapshot = self.store.publish(None, self.initial_changes())
        self.store._published = self.store._read = None  # forget the trees this store published and read
        with audit_events('subprocess.Popen') as events:
            first = self.store.tree_paths(snapshot.head)
            second = self.store.tree_paths(snapshot.head)
        self.assertEqual(first, second)
        self.assertEqual(git_commands(events), ['ls-tree'])

    def test_batch_read_is_exact_and_missing_blob_is_an_error(self):
        changes = {**self.initial_changes(), 'runtime/artifacts/batch/빈 파일': b'',
                   'runtime/artifacts/batch/바이너리': b'\x00\xff\n\r\nblob missing\n'}
        snapshot = self.store.publish(None, changes)
        with audit_events('subprocess.Popen') as events:
            values = self.store.read_many(snapshot.head, list(changes))
        self.assertEqual(values, changes)
        self.assertEqual(git_commands(events), ['cat-file'])
        with audit_events('subprocess.Popen') as events:
            self.assertEqual(self.store.read_many(snapshot.head, []), {})
        self.assertEqual(git_commands(events), [])
        with self.assertRaisesRegex(GitStateStoreError, 'batch read did not return a blob: runtime/absent'):
            self.store.read_many(snapshot.head, ['research/instance.json', 'runtime/absent'])

    def test_simultaneous_stale_cas_has_one_winner_and_no_overwrite(self):
        initial = self.store.publish(None, self.initial_changes())
        barrier = threading.Barrier(2)
        results: list[tuple[str, object]] = []
        results_lock = threading.Lock()

        def publish(label: str) -> None:
            local = real_store(self.repository)
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
        conflict = next(value for kind, value in results if kind == "conflict")
        self.assertIn('publish compare-and-swap', str(conflict))
        self.assertIn(self.store.read_bytes(self.store.read_snapshot().head, "runtime/state.json"), (b"left", b"right"))

    def test_publish_does_not_change_worktree_or_default_index(self):
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

    def test_publish_does_not_execute_repository_hook(self):
        hook_directory = self.repository / "hostile-hooks"
        hook_directory.mkdir()
        marker = self.repository / "hook-ran"
        hook = hook_directory / "reference-transaction"
        hook.write_text(f"#!/bin/sh\necho invoked > '{marker.as_posix()}'\n", encoding="utf-8")
        hook.chmod(0o755)
        git(self.repository, "config", "core.hooksPath", str(hook_directory))

        snapshot = self.store.publish(None, self.initial_changes())

        self.assertFalse(marker.exists())
        self.assertEqual(self.store.read_snapshot().head, snapshot.head)

    def test_non_commit_or_corrupt_existing_ref_is_not_treated_as_absent(self):
        blob = git(self.repository, "hash-object", "-w", "--stdin", input=b"not a commit").decode().strip()
        corrupt_path = self.store.git_dir / self.store.ref
        corrupt_path.parent.mkdir(parents=True, exist_ok=True)
        corrupt_path.write_text(blob + "\n", encoding="ascii")
        with self.assertRaisesRegex(GitStateStoreError, 'state ref must point to a commit'):
            self.store.read_snapshot()

        corrupt_path.write_text("not-an-object-id\n", encoding="ascii")
        with self.assertRaisesRegex(GitStateStoreError,
                                    re.escape(f'git rev-parse --verify --quiet {REF} failed: '
                                              f'warning: ignoring broken ref {REF}')):
            self.store.read_snapshot()


class SnapshotMetadataProcessTests(unittest.TestCase):
    """The ref and both subtrees in one ``cat-file`` batch; ``rev-parse`` only when the ref line is missing."""

    def test_one_batch_reads_the_ref_and_both_subtrees(self):
        for object_format in ('sha1', 'sha256'):
            with self.subTest(object_format=object_format), tempfile.TemporaryDirectory() as temporary:
                repository = Path(temporary) / 'repository'
                repository.mkdir()
                git(repository, 'init', '-q', f'--object-format={object_format}')
                store = real_store(repository)
                head = store.publish(None, {'research/instance.json': b'{}\n', 'runtime/state.json': b'{}\n'}).head
                self.assertEqual(len(head), 40 if object_format == 'sha1' else 64)
                with audit_events('subprocess.Popen') as events:
                    self.assertEqual(store.read_snapshot(), StateSnapshot(head))
                self.assertEqual(git_runs(events),
                                 [['cat-file', '--batch-check=%(objectname) %(objecttype) %(objectsize)']])

    def test_absent_ref_is_none_but_a_broken_ref_is_rejected_with_gits_report(self):
        with tempfile.TemporaryDirectory() as temporary:
            repository = Path(temporary) / 'repository'
            repository.mkdir()
            git_init(repository)
            store = real_store(repository)
            with audit_events('subprocess.Popen') as events:
                self.assertEqual(store.read_snapshot(), StateSnapshot(None))
            self.assertEqual(git_commands(events), ['cat-file', 'rev-parse'])
            broken = store.git_dir / store.ref
            broken.parent.mkdir(parents=True, exist_ok=True)
            broken.write_text("not-an-object-id\n", encoding="ascii")
            with self.assertRaisesRegex(GitStateStoreError, 'rev-parse --verify --quiet .* failed: warning: '):
                store.read_snapshot()


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
        git(repository, "update-index", "-z", "--index-info", input="".join(record + "\0" for record in records).encode(),
            env=index)
        return git(repository, "write-tree", env=index).decode().strip()

    def assertTreesAndCommitsMatchGit(self, object_format: str) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repository = Path(temporary) / "repository"
            repository.mkdir()
            if object_format == "sha1":
                git_init(repository)
            else:
                git(repository, "init", "-q", f"--object-format={object_format}")
            index = {"GIT_INDEX_FILE": str(Path(temporary) / "oracle-index")}
            rng = random.Random("do-math-" + object_format)
            store = real_store(repository)
            model: dict[str, bytes] = {}
            head, heads, expected = None, [], []
            for round_number in range(4):
                changes = self.random_changes(rng, model)
                if head is None:
                    changes.update({"research/keep": b"k", "runtime/keep": b"k"})
                if round_number == 2:
                    store = real_store(repository)  # parent tree read through ls-tree
                head = store.publish(head, changes).head
                for path, raw in changes.items():
                    if raw is None:
                        model.pop(path, None)
                    else:
                        model[path] = raw
                self.assertEqual(store.tree_paths(head), set(model))
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
                arguments = ["-c", "commit.gpgSign=false", "commit-tree", f"{commit}^{{tree}}",
                             *(["-p", parent] if parent else [])]
                oracle = git(repository, *arguments, input=b"do-math state\n", env={**self.GIT_DEFAULTS, **identity})
                self.assertEqual(oracle.decode().strip(), commit)
            checked = subprocess.run(["git", "-C", str(repository), "fsck", "--strict", "--no-progress"],
                                     capture_output=True, env={**os.environ, **self.GIT_DEFAULTS})
            # Only the unborn-HEAD notice may appear; any object finding fails.
            findings = [line for line in (checked.stdout + checked.stderr).decode().splitlines()
                        if not line.startswith("notice: HEAD points to an unborn branch")]
            self.assertEqual((checked.returncode, findings), (0, []))

    def test_sha1_trees_and_commits_match_git(self):
        self.assertTreesAndCommitsMatchGit("sha1")

    def test_sha256_trees_and_commits_match_git(self):
        self.assertTreesAndCommitsMatchGit("sha256")


if __name__ == "__main__":
    unittest.main()
