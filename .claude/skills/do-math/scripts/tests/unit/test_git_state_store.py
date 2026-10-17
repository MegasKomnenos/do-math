"""GitStateStore (layer 2): one parent-linked state commit chain per instance, over the in-process Git fake.

The store writes blobs, trees and commits and moves the instance ref by
compare-and-swap; paths, artifact bundles, parents, caches and the writer lock
are its own rules, so these tests run it on the Git port's fake
(``ObservedGit`` lists the port operations it asks for) and on real folders
for its physical boundaries. What the real git process adds (in-process loose
objects and their flush, one process per operation, hooks, the index, object
formats Git itself wrote) is in ``boundary/test_git_process_storage.py``.
"""
from pathlib import Path
import re
import tempfile
import unittest

from do_math.git_store import GitStateStore, GitStateStoreConflict, GitStateStoreError, StateSnapshot
from do_math.ids import oid_shape
from support.fakes.clock import FakeClock
from support.fakes.git_backend import make_repository
from support.storage_files import junction, remove_link
from support.storage_git import ObservedGit

INSTANCE_ID = "RI-00000000000000000000000000"
REF = 'refs/heads/do-math/' + INSTANCE_ID
REPARSE = 'physical path crosses a reparse point or symlink: '


def commit_parents(backend, repository, commit):
    kind, body = backend.read_objects(repository, [commit])[0]
    assert kind == 'commit'
    return [line.split(' ', 1)[1] for line in body.decode('ascii').split('\n\n', 1)[0].split('\n')
            if line.startswith('parent ')]


class StoreCase(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.repository = make_repository(self.root / 'repository')
        self.backend = ObservedGit()
        self.store = GitStateStore(self.repository, INSTANCE_ID, backend=self.backend, clock=FakeClock())

    def initial_changes(self):
        return {
            "research/instance.json": b'{"revision": 1}\n',
            "runtime/state.json": b'{"state": "initializing"}\n',
        }

    def forget_trees(self):
        self.store._published = self.store._read = None


class GitStateStoreTests(StoreCase):
    def test_ref_update_error_rereads_the_head_and_allows_the_next_publication(self):
        from do_math.ports.git_backend import GitBackendError
        initial = self.store.publish(None, self.initial_changes())
        with self.store.writer_lock():
            current = self.store.publish(initial.head, {'runtime/state.json': b'locked'})
            for committed in (False, True):
                with self.subTest(committed=committed):
                    original = self.backend.update_ref
                    moved = []

                    def unavailable(repository, ref, new, old):
                        if committed:
                            self.assertTrue(original(repository, ref, new, old))
                            moved.append(new)
                        raise GitBackendError('ref update response unavailable')

                    self.backend.update_ref = unavailable
                    try:
                        with self.assertRaisesRegex(GitStateStoreError, '^ref update response unavailable$') as caught:
                            self.store.publish(current.head, {'runtime/state.json': b'candidate'})
                    finally:
                        del self.backend.update_ref
                    self.assertIsInstance(caught.exception.__cause__, GitBackendError)
                    authoritative = moved[0] if committed else current.head
                    mark = len(self.backend.calls)
                    self.assertEqual(self.store.read_snapshot().head, authoritative)
                    self.assertIn('object_info', self.backend.operations(mark))
                    self.assertEqual(self.store.read_bytes(authoritative, 'runtime/state.json'),
                                     b'candidate' if committed else b'locked')
                    current = self.store.publish(authoritative, {'runtime/state.json': b'locked'})
                    self.assertEqual(commit_parents(self.backend, self.repository, current.head), [authoritative])

    def test_oid_shape_is_separate_from_instance_format(self):
        self.assertEqual(oid_shape("a" * 64), "sha256")
        with self.assertRaisesRegex(ValueError, 'OID must be a lowercase sha1 object ID'):
            self.store.validate_oid("a" * 64)
        with self.assertRaisesRegex(ValueError, 'OID must be a lowercase 40/64-character hexadecimal string'):
            oid_shape("A" * 40)

    def test_tree_cache_reuses_only_immutable_oids(self):
        snapshot = self.store.publish(None, self.initial_changes())
        self.forget_trees()
        mark = len(self.backend.calls)
        first = self.store.tree_paths(snapshot.head)
        second = self.store.tree_paths(snapshot.head)
        self.assertEqual(first, second)
        # One list_tree is one ls-tree of the real backend.
        self.assertEqual(self.backend.operations(mark).count('list_tree'), 1)

    def test_own_publication_lists_the_new_tree_without_enumerating_it(self):
        first = self.store.publish(None, {**self.initial_changes(), 'runtime/artifacts/one/a.bin': b'a'})
        mark = len(self.backend.calls)
        later = self.store.publish(first.head, {'runtime/state.json': None, 'research/next.json': b'{}\n',
                                                'runtime/artifacts/two/b.bin': b'b'})
        listed = self.store.tree_paths(later.head)
        # The parent list also came from its own publication.
        self.assertNotIn('list_tree', self.backend.operations(mark))
        # Reading an older snapshot does not displace the tree just published.
        self.store.tree_paths(first.head)
        mark = len(self.backend.calls)
        self.store.publish(later.head, {'research/again.json': b'{}\n'})
        self.assertEqual(self.backend.operations(mark), ['update_ref'])
        self.forget_trees()
        self.assertEqual(listed, self.store.tree_paths(later.head))

    def test_path_that_is_also_a_directory_is_rejected_before_git_drops_it(self):
        first = self.store.publish(None, {**self.initial_changes(), 'research/a': b'file'})
        with self.assertRaisesRegex(ValueError, 'both a file and a directory'):
            self.store.publish(first.head, {'research/a/b': b'child'})
        with self.assertRaisesRegex(ValueError, 'both a file and a directory'):
            self.store.validate_candidate_paths({'research/x', 'research/x/y'})
        self.assertEqual(self.store.read_snapshot().head, first.head)

    def test_physical_boundary_is_proved_on_open_and_after_git_errors_only(self):
        """The repository is moved and a junction takes its place after the store opened.

        Publishing and reading still succeed, so neither boundary was proved
        again; the Git error of a missing blob proves them and reports the
        reparse point.
        """
        snapshot = self.store.publish(None, self.initial_changes())
        moved = self.root / 'moved'
        self.repository.rename(moved)
        junction(moved, self.repository)
        self.addCleanup(remove_link, self.repository)
        later = self.store.publish(snapshot.head, {'runtime/state.json': b'{"state": "running"}\n'})
        self.assertEqual(self.store.read_many(later.head, ['runtime/state.json']),
                         {'runtime/state.json': b'{"state": "running"}\n'})
        with self.assertRaisesRegex(ValueError, re.escape(REPARSE + str(self.repository))):
            self.store.read_bytes(later.head, 'runtime/absent.json')

    def test_writer_lock_leaves_the_final_cas_as_the_only_ref_comparison(self):
        first = self.store.publish(None, self.initial_changes())
        with self.store.writer_lock():
            mark = len(self.backend.calls)
            later = self.store.publish(first.head, {'runtime/state.json': b'{"state": "running"}\n'})
            self.assertEqual(self.backend.operations(mark), ['update_ref'])
            # Under the lock no do-math writer moves the ref, so the head this
            # store just published is not read back.
            mark = len(self.backend.calls)
            self.assertEqual(self.store.read_snapshot(), StateSnapshot(later.head))
            self.assertEqual(self.backend.operations(mark, writes=True), [])
            # A writer outside the lock (another store on the same repository) is still refused by that final CAS.
            outside = GitStateStore(self.repository, INSTANCE_ID, backend=ObservedGit(self.backend.objects),
                                    clock=FakeClock())
            moved = outside.publish(later.head, {'runtime/state.json': b'{"state": "moved"}\n'})
            with self.assertRaisesRegex(GitStateStoreConflict, 'publish compare-and-swap'):
                self.store.publish(later.head, {'runtime/state.json': b'{"state": "lost"}\n'})
            # The failed CAS proves the remembered head stale; it is read again.
            self.assertEqual(self.store.read_snapshot().head, moved.head)
        mark = len(self.backend.calls)
        self.assertEqual(self.store.read_snapshot().head, moved.head)
        self.assertEqual(self.backend.operations(mark, writes=True), ['object_info'])

    def test_unicode_artifact_path_preserves_the_supplied_code_points(self):
        path = "runtime/artifacts/one/e\u0301.txt"
        snapshot = self.store.publish(None, {**self.initial_changes(), path: b"raw"})
        self.assertEqual(self.store.read_bytes(snapshot.head, path), b"raw")
        self.assertIn(path, self.store.tree_paths(snapshot.head))
        self.assertNotIn("runtime/artifacts/one/é.txt", self.store.tree_paths(snapshot.head))

    def test_initial_commit_has_no_parent_and_later_commit_has_one_parent(self):
        initial = self.store.publish(None, self.initial_changes())
        self.assertIsNotNone(initial.head)
        self.assertEqual(len(initial.head), 40)
        self.assertEqual(commit_parents(self.backend, self.repository, initial.head), [])
        later = self.store.publish(initial.head, {"runtime/state.json": b'{"state": "running"}\n'})
        self.assertEqual(commit_parents(self.backend, self.repository, later.head), [initial.head])

    def test_runtime_only_update_preserves_research_tree_and_old_snapshot_bytes(self):
        initial = self.store.publish(None, self.initial_changes())
        later = self.store.publish(initial.head, {"runtime/state.json": b'{"state": "running"}\n'})
        research = self.backend.object_info(self.repository, [f'{later.head}:research', f'{initial.head}:research'])
        self.assertEqual(research[0][:2], research[1][:2])
        self.assertEqual(research[0][1], 'tree')
        self.assertEqual(self.store.read_bytes(initial.head, "runtime/state.json"),
                         self.initial_changes()["runtime/state.json"])
        self.assertEqual(self.store.read_bytes(later.head, "runtime/state.json"), b'{"state": "running"}\n')

    def test_writer_lock_is_an_os_lock_without_stale_pid_contents(self):
        with self.store.writer_lock():
            snapshot = self.store.publish(None, self.initial_changes())
        lock_path = self.store.git_dir / f"do-math-{INSTANCE_ID}.lock"
        self.assertEqual(lock_path.read_bytes(), b"\0")
        self.assertEqual(self.store.read_snapshot().head, snapshot.head)

    def test_existing_artifact_bundle_cannot_be_changed_or_deleted(self):
        initial = self.store.publish(None, {
            **self.initial_changes(),
            "runtime/artifacts/bundle_01/output.txt": b"sealed\n",
        })
        with self.assertRaisesRegex(ValueError, 'existing runtime artifact bundles are immutable'):
            self.store.publish(initial.head, {"runtime/artifacts/bundle_01/output.txt": b"altered\n"})
        with self.assertRaisesRegex(ValueError, 'existing runtime artifact bundles are immutable'):
            self.store.publish(initial.head, {"runtime/artifacts/bundle_01/output.txt": None})
        self.assertEqual(self.store.read_snapshot().head, initial.head)

    def test_invalid_and_case_colliding_paths_are_rejected(self):
        invalid_paths = (
            ("research/../escape.txt", 'path contains an invalid segment'),
            ("research/back\\slash.txt", 'path must be a POSIX relative path'),
            ("research/CON.txt", 'path contains a reserved Windows device name'),
            ("research/trailing. ", 'path contains an invalid segment'),
            ("/research/absolute.txt", 'path must be a POSIX relative path'),
        )
        for path, message in invalid_paths:
            with self.subTest(path=path), self.assertRaisesRegex(ValueError, re.escape(message)):
                self.store.publish(None, {path: b"x", "runtime/state.json": b"{}"})
        with self.assertRaisesRegex(ValueError, re.escape(
                "Windows case-colliding paths: 'research/A.txt' and 'research/a.txt'")):
            self.store.publish(None, {
                "research/A.txt": b"one",
                "research/a.txt": b"two",
                "runtime/state.json": b"{}",
            })
        self.assertIsNone(self.store.read_snapshot().head)

    def test_case_colliding_directory_segments_are_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Windows case-colliding path segments: '):
            self.store.publish(None, {
                "research/Foo/a.txt": b"one",
                "research/foo/b.txt": b"two",
                "runtime/state.json": b"{}",
            })
        self.assertIsNone(self.store.read_snapshot().head)

    def test_only_registry_instance_ids_are_accepted_before_ref_use(self):
        backend = ObservedGit()
        with self.assertRaisesRegex(ValueError, 'instance_id must be the registry RI-prefixed canonical ULID'):
            GitStateStore(self.repository, "inst_01", backend=backend, clock=FakeClock())
        self.assertEqual(backend.calls, [])

    def test_repository_junction_is_rejected_before_resolve(self):
        link = junction(self.repository, self.root / "repository-link")
        self.addCleanup(remove_link, link)
        backend = ObservedGit()
        with self.assertRaisesRegex(ValueError, re.escape(REPARSE + str(link))):
            GitStateStore(link, INSTANCE_ID, backend=backend, clock=FakeClock())
        self.assertEqual(backend.calls, [])

    def test_physical_file_boundary_checks_opened_handle(self):
        from do_math.file_io import PhysicalBoundary
        boundary = PhysicalBoundary(self.repository)
        file = self.repository / "boundary.bin"
        with boundary.open(file, "xb") as stream:
            stream.write(b"bounded")
        with boundary.open(file, "rb") as stream:
            self.assertEqual(stream.read(), b"bounded")
        outside = self.root / "outside.bin"
        with self.assertRaisesRegex(ValueError, 'file path is outside the physical boundary'):
            boundary.open(outside, "xb").__enter__()
        with self.assertRaisesRegex(ValueError, 'file path is outside the physical boundary'):
            boundary.open(self.repository / ".." / "outside.bin", "xb").__enter__()
        self.assertFalse(outside.exists())

    def test_physical_boundary_refuses_a_reparse_point_below_its_root(self):
        from do_math.file_io import PhysicalBoundary
        root = self.root / "bounded"
        target = self.root / "elsewhere"
        root.mkdir()
        target.mkdir()
        (target / "file.bin").write_bytes(b"outside")
        boundary = PhysicalBoundary(root)
        link = junction(target, root / "link")
        self.addCleanup(remove_link, link)
        with self.assertRaisesRegex(ValueError, re.escape(REPARSE + str(link))):
            boundary.open(link / "file.bin", "rb").__enter__()


class GitStateStoreSha256Tests(unittest.TestCase):
    def test_sha256_repository_uses_64_character_oids(self):
        with tempfile.TemporaryDirectory() as temporary:
            repository = make_repository(Path(temporary) / "sha256", 'sha256')
            store = GitStateStore(repository, INSTANCE_ID, backend=ObservedGit(), clock=FakeClock())
            snapshot = store.publish(None, {
                "research/instance.json": b"{}\n",
                "runtime/state.json": b"{}\n",
            })
            self.assertEqual(store.object_format, "sha256")
            self.assertEqual(len(snapshot.head), 64)
            with self.assertRaisesRegex(ValueError, 'OID must be a lowercase sha256 object ID'):
                store.read_bytes("0" * 40, "runtime/state.json")


class SnapshotMetadataTests(unittest.TestCase):
    def test_one_batch_reads_the_ref_and_both_subtrees(self):
        for object_format in ('sha1', 'sha256'):
            with self.subTest(object_format=object_format), tempfile.TemporaryDirectory() as temporary:
                repository = make_repository(Path(temporary) / 'repository', object_format)
                backend = ObservedGit()
                store = GitStateStore(repository, INSTANCE_ID, backend=backend, clock=FakeClock())
                head = store.publish(None, {'research/instance.json': b'{}\n', 'runtime/state.json': b'{}\n'}).head
                mark = len(backend.calls)
                self.assertEqual(store.read_snapshot(), StateSnapshot(head))
                self.assertEqual(backend.calls[mark:], [('object_info', ([REF, REF + ':research', REF + ':runtime'],))])

    def test_absent_ref_is_none_and_resolved_separately(self):
        with tempfile.TemporaryDirectory() as temporary:
            repository = make_repository(Path(temporary) / 'repository')
            backend = ObservedGit()
            store = GitStateStore(repository, INSTANCE_ID, backend=backend, clock=FakeClock())
            mark = len(backend.calls)
            self.assertEqual(store.read_snapshot(), StateSnapshot(None))
            self.assertEqual(backend.operations(mark), ['object_info', 'ref_oid'])


if __name__ == '__main__':
    unittest.main()


class BatchOutputTests(unittest.TestCase):
    def test_object_info_keeps_missing_order_and_both_oid_widths(self):
        from do_math.storage_finish_git_output import parse_object_info
        for width in (40, 64):
            with self.subTest(width=width):
                oid = 'a' * width
                self.assertEqual(parse_object_info(['one', 'missing', 'two'],
                                 f'{oid} blob 2\nmissing missing\n{oid} tree 0\n'.encode()),
                                 [(oid, 'blob', 2), None, (oid, 'tree', 0)])
        self.assertEqual(parse_object_info([], b''), [])

    def test_binary_payload_and_every_read_frame_refusal(self):
        from do_math.storage_finish_git_output import parse_read_objects
        from do_math.ports.git_backend import GitBackendError
        raw = b'oid blob 4\n\x00\xff\nX\nabsent missing\noid blob 0\n\n'
        self.assertEqual(parse_read_objects(['one', 'absent', 'empty'], raw),
                         [('blob', b'\x00\xff\nX'), None, ('blob', b'')])
        self.assertEqual(parse_read_objects([], b''), [])
        for data, reason in [(b'', 'no object header'), (b'oid blob extra\n', 'no object header'),
                             (b'oid blob 3\nab', 'truncated batch object'),
                             (b'oid blob 2\nabX', 'truncated batch object'),
                             (b'oid blob 0\n\nextra', 'unexpected trailing batch output')]:
            with self.subTest(raw=data), self.assertRaisesRegex(GitBackendError, reason):
                parse_read_objects(['one'], data)


class ProjectOutputTests(unittest.TestCase):
    def test_project_decoders_keep_empty_false_exit_and_strict_utf8_distinct(self):
        from do_math.storage_finish_git_output import parse_project_root, parse_project_tree, parse_project_paths
        self.assertIsNone(parse_project_root(b' \n'))
        self.assertEqual(parse_project_root(b' /repo \n'), Path('/repo'))
        self.assertEqual(parse_project_tree(False, b' tree \n'), 'tree')
        self.assertEqual(parse_project_tree(0, b''), '')
        for code in (1, 128, None):
            self.assertIsNone(parse_project_tree(code, b'HEAD:absent\n'))
        self.assertEqual(parse_project_paths(False, b'a\0a\0sub/b\0'), frozenset({'a', 'sub/b'}))
        self.assertEqual(parse_project_paths(None, b''), frozenset())
        with self.assertRaisesRegex(RuntimeError, '^cannot read tracked paths for the configured project$'):
            parse_project_paths(128, b'\xff')
        for parse, args in ((parse_project_root, (b'\xff',)),
                            (parse_project_tree, (0, b'\xff')),
                            (parse_project_paths, (0, b'\xff\0'))):
            with self.subTest(parser=parse.__name__), self.assertRaises(UnicodeDecodeError) as rejected:
                parse(*args)
            self.assertEqual(rejected.exception.encoding, 'utf-8')
            self.assertEqual(rejected.exception.object, b'\xff')
            self.assertEqual((rejected.exception.start, rejected.exception.end), (0, 1))
            self.assertEqual(rejected.exception.reason, 'invalid start byte')
        self.assertIsNone(parse_project_tree(1, b'\xff'))
