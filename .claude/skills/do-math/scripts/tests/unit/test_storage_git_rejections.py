"""GitStateStore 입력 및 Git 의미 포트의 잘못된 객체 응답을 구분한다."""
from pathlib import Path
import re
import tempfile
import unittest

from do_math.git_store import GitStateStoreError
from support.fakes.git_backend import InProcessGit
from support.state_builders import current_state
from support.storage_records import record_store


class WrongObjects(InProcessGit):
    """외부 Git가 blob 대신 tree를 반환하는 의미 포트 입력."""
    def read_objects(self, repository, specs):
        return [('tree', b'') for spec in specs]

    def object_info(self, repository, specs):
        return [('a' * 40, 'tree', 0) for spec in specs]


class GitRejections(unittest.TestCase):
    def test_missing_required_subtree_refuses_initial_and_deleting_publication(self):
        with tempfile.TemporaryDirectory() as directory:
            store = record_store(Path(directory))._store
            for changes, missing in (({'runtime/x': b'x'}, 'research'),
                                     ({'research/x': b'x'}, 'runtime')):
                with self.assertRaisesRegex(ValueError, '^the state must contain a ' + missing + ' subtree$'):
                    store.publish(None, changes)
                self.assertIsNone(store.read_snapshot().head)
            head = store.publish(None, {'research/x': b'x', 'runtime/x': b'x'}).head
            for root in ('research', 'runtime'):
                with self.assertRaisesRegex(ValueError, '^the state must contain a ' + root + ' subtree$'):
                    store.publish(head, {root + '/x': None})
                self.assertEqual(store.read_snapshot().head, head)

    def test_changes_and_path_boundaries_reject_before_publication(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = record_store(Path(directory))
            head = repo.initialize(*current_state())
            store = repo._store
            for changes, kind, reason in (([], TypeError, 'changes must be a mapping of paths to bytes or None'),
                    ({'research/x': 'string'}, TypeError, 'change contents must be bytes or None')):
                with self.assertRaisesRegex(kind, '^' + reason + '$'):
                    store.publish(head, changes)
                self.assertEqual(store.read_snapshot().head, head)
            for path, reason in (('', 'path must be a non-empty POSIX relative path'),
                                 ('/research/x', 'path must be a POSIX relative path'),
                                 ('outside/x', 'state paths must be files below research/ or runtime/'),
                                 ('runtime/artifacts/bundle', 'artifact paths must name a bundle and a file')):
                with self.subTest(path=path), self.assertRaisesRegex(ValueError, '^' + reason + '$'):
                    store.validate_path(path)
            with self.assertRaisesRegex(ValueError, '^state path is both a file and a directory: research/x$'):
                store.validate_candidate_paths({'research/x', 'research/x/y'})

    def test_subtree_metadata_count_missing_and_kind_are_distinct(self):
        with tempfile.TemporaryDirectory() as directory:
            store = record_store(Path(directory))._store
            for rows, reason in (([], 'incomplete state subtree metadata'),
                                 (['x missing'], "state object lacks required 'research' subtree"),
                                 (['a' * 40 + ' blob'], "state 'research' entry must be a tree")):
                with self.subTest(rows=rows), self.assertRaisesRegex(GitStateStoreError, '^' + re.escape(reason) + '$'):
                    store._check_subtrees(rows, ('research',))
            self.assertIsNone(store._check_subtrees(['a' * 40 + ' tree'], ('research',)))

    def test_batch_read_and_sizes_refuse_nonblob_port_answers(self):
        with tempfile.TemporaryDirectory() as directory:
            store = record_store(Path(directory), backend=WrongObjects())._store
            for call, reason in ((store.read_many, 'batch read did not return a blob: research/x'),
                                 (store.blob_sizes, 'batch size did not return a blob: research/x')):
                with self.assertRaisesRegex(GitStateStoreError, '^' + reason + '$'):
                    call('a' * 40, ['research/x'])
                with self.assertRaisesRegex(ValueError, '^missing must be "raise" or "omit"$'):
                    call('a' * 40, ['research/x'], missing='ignore')
                self.assertEqual(call('a' * 40, []), {})


    def test_noncommit_ref_and_non_utf8_tree_are_refused_without_rewriting_history(self):
        with tempfile.TemporaryDirectory() as directory:
            backend = InProcessGit()
            repo = record_store(Path(directory), backend=backend)
            head = repo.initialize(*current_state())
            store = repo._store
            root_tree = backend.read_objects(store.repository, [head])[0][1].splitlines()[0].split()[1].decode()
            self.assertTrue(backend.update_ref(store.repository, store.ref, root_tree, head))
            with self.assertRaises(GitStateStoreError) as caught:
                store.read_snapshot()
            self.assertIs(type(caught.exception), GitStateStoreError)
            self.assertEqual(str(caught.exception), 'state ref must point to a commit')
            self.assertEqual(backend.ref_oid(store.repository, store.ref), root_tree)
            self.assertTrue(backend.update_ref(store.repository, store.ref, head, root_tree))
            blob = backend.write_object(store.repository, 'blob', b'unchanged\n')
            invalid_tree = backend.write_object(store.repository, 'tree',
                b'100644 \xff\0' + bytes.fromhex(blob))
            entries = dict(store._tree(head).directories[''])
            entries['research'] = ('40000', invalid_tree)
            invalid_head = store._write_commit(store._write_tree_object(entries), head)
            self.assertTrue(backend.update_ref(store.repository, store.ref, invalid_head, head))
            with self.assertRaises(GitStateStoreError) as caught:
                store.tree_paths(invalid_head)
            self.assertIs(type(caught.exception), GitStateStoreError)
            self.assertEqual(str(caught.exception), 'existing state contains a non-UTF-8 path')
            self.assertIs(type(caught.exception.__cause__), UnicodeDecodeError)
            self.assertEqual(caught.exception.__cause__.object, b'research/\xff')
            self.assertEqual(backend.ref_oid(store.repository, store.ref), invalid_head)
            self.assertEqual(repo.load(head)[2]['inputs'][0]['id'], 'UI-fixture')
            self.assertFalse((store.git_dir / (store.ref + '.lock')).exists())

    def test_directory_delete_and_absent_descendant_delete_preserve_all_blob_bytes(self):
        from support.storage_git import ObservedGit

        with tempfile.TemporaryDirectory() as directory:
            backend = ObservedGit()
            repo = record_store(Path(directory), backend=backend)
            head = repo.initialize(*current_state())
            store = repo._store
            paths = sorted(store.tree_paths(head))
            original = store.read_many(head, paths)
            for removed in ('research/_state', 'runtime/never-created/absent'):
                with self.subTest(path=removed):
                    start = len(backend.calls)
                    final = store.publish(head, {removed: None}).head
                    self.assertNotEqual(final, head)
                    self.assertEqual([args for name, args in backend.calls[start:] if name == 'update_ref'],
                                     [(final, head)])
                    self.assertEqual(store.tree_paths(final), frozenset(paths))
                    self.assertEqual(store.read_many(final, paths), original)
                    self.assertEqual(store.read_snapshot().head, final)
                    self.assertEqual(repo.load(final)[1:], repo.load(head)[1:])
                    head = final
            self.assertFalse((store.git_dir / (store.ref + '.lock')).exists())

    def test_git_port_failures_keep_the_original_reason_cause_and_ref(self):
        from do_math.ports.git_backend import GitBackendError
        from support.storage_git import ObservedGit

        class UnsupportedFormat(InProcessGit):
            def describe(self, repository):
                git_dir, _, objects = super().describe(repository)
                return git_dir, 'sha512', objects

        with tempfile.TemporaryDirectory() as directory:
            backend = ObservedGit()
            repo = record_store(Path(directory), backend=backend)
            head = repo.initialize(*current_state())
            path = 'research/_state/metadata.json'
            original = repo.read(path, head)
            with self.assertRaises(GitStateStoreError) as caught:
                record_store(Path(directory), backend=UnsupportedFormat())
            self.assertIs(type(caught.exception), GitStateStoreError)
            self.assertEqual(str(caught.exception), "unsupported Git object format: 'sha512'")
            failure = GitBackendError('storage port read refused')

            def refuse_read(operation, arguments):
                if operation == 'read_objects':
                    raise failure

            backend.before = refuse_read
            try:
                with self.assertRaises(GitStateStoreError) as caught:
                    repo.read(path, head)
                self.assertIs(type(caught.exception), GitStateStoreError)
                self.assertIs(caught.exception.__cause__, failure)
                self.assertEqual(str(caught.exception), 'storage port read refused')
            finally:
                backend.before = None
            self.assertEqual(repo.read(path, head), original)
            self.assertEqual(repo.load()[0], head)


if __name__ == '__main__':
    unittest.main()
