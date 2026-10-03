"""Git backend port contract (설계 2.2): the git process and the in-process fake answer alike.

Repositories are built without a git process: ``make_repository`` (the fake's
module) writes the minimal layout Git reads (HEAD, config, objects/, refs/heads/) and
``write_object`` writes loose objects, the form GitStateStore itself writes.
The real side (boundary/test_port_git_backend.py) checks that git reads this
layout too.
"""

import hashlib

from pathlib import Path

import tempfile


import zlib

from do_math.ports.git_backend import GitBackendError
from support.fakes.git_backend import make_repository

REF = 'refs/heads/do-math/RI-01M3HM0X0000000000000000AB'

def write_object(repository, kind, body, object_format='sha1'):
    raw = kind.encode() + b' ' + str(len(body)).encode() + b'\0' + body
    oid = (hashlib.sha256 if object_format == 'sha256' else hashlib.sha1)(raw).hexdigest()
    path = Path(repository) / '.git' / 'objects' / oid[:2] / oid[2:]
    path.parent.mkdir(exist_ok=True)
    path.write_bytes(zlib.compress(raw))
    return oid

def tree(repository, entries, object_format='sha1'):
    """entries: [(mode, name, oid)] in Git order."""
    width = 32 if object_format == 'sha256' else 20
    body = b''.join(mode.encode() + b' ' + name.encode() + b'\0' + bytes.fromhex(oid)[:width]
                    for mode, name, oid in sorted(entries, key=lambda e: e[1] + ('/' if e[0] == '40000' else '')))
    return write_object(repository, 'tree', body, object_format)

def commit(repository, tree_oid, parent=None, object_format='sha1'):
    signature = 'do-math <do-math@invalid> 1700000000 +0000'
    parents = f'parent {parent}\n' if parent else ''
    return write_object(repository, 'commit', f'tree {tree_oid}\n{parents}author {signature}\ncommitter {signature}\n\n'
                        'do-math state\n'.encode(), object_format)

class GitBackendContract:
    object_format = 'sha1'

    def make(self):
        raise NotImplementedError

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.repo = make_repository(self.directory.name, self.object_format)
        f = self.object_format
        self.blob = write_object(self.repo, 'blob', b'{"a": 1}\n', f)
        self.other = write_object(self.repo, 'blob', b'second\n', f)
        research = tree(self.repo, [('100644', 'state.json', self.blob)], f)
        runtime = tree(self.repo, [('100644', 'queue.json', self.other)], f)
        self.root = tree(self.repo, [('40000', 'research', research), ('40000', 'runtime', runtime)], f)
        self.research = research
        self.first = commit(self.repo, self.root, None, f)
        self.second = commit(self.repo, self.root, self.first, f)
        self.third = commit(self.repo, self.root, self.second, f)
        self.backend = self.make()

    def test_describe_reports_git_dir_object_format_and_objects(self):
        git_dir, object_format, objects = self.backend.describe(self.repo)
        self.assertEqual(Path(git_dir).resolve(), (self.repo / '.git').resolve())
        self.assertEqual(object_format, self.object_format)
        self.assertEqual((self.repo / objects).resolve(), (self.repo / '.git' / 'objects').resolve())

    def test_an_absent_ref_resolves_to_none_and_update_ref_creates_it_only_from_absent(self):
        self.assertIsNone(self.backend.ref_oid(self.repo, REF))
        self.assertFalse(self.backend.update_ref(self.repo, REF, self.first, self.second))
        self.assertIsNone(self.backend.ref_oid(self.repo, REF))
        self.assertTrue(self.backend.update_ref(self.repo, REF, self.first, None))
        self.assertEqual(self.backend.ref_oid(self.repo, REF), self.first)

    def test_broken_ref_text_is_an_error_but_missing_object_keeps_its_oid(self):
        self.assertIsNone(self.backend.ref_oid(self.repo, REF))
        path = self.repo / '.git' / REF
        path.parent.mkdir(parents=True, exist_ok=True)
        width = 64 if self.object_format == 'sha256' else 40
        for raw in (b'not-an-object-id\n', b'a' * (width - 1) + b'\n'):
            path.write_bytes(raw)
            with self.subTest(raw=raw), self.assertRaises(GitBackendError) as caught:
                self.backend.ref_oid(self.repo, REF)
            self.assertTrue(str(caught.exception))
        oid = 'a' * width
        path.write_text(oid + '\n', encoding='ascii')
        self.assertEqual(self.backend.ref_oid(self.repo, REF), oid)
        self.assertEqual(self.backend.object_info(self.repo, [REF]), [None])


    def test_update_ref_is_a_compare_and_swap(self):
        self.assertTrue(self.backend.update_ref(self.repo, REF, self.first, None))
        self.assertFalse(self.backend.update_ref(self.repo, REF, self.third, self.second))
        self.assertEqual(self.backend.ref_oid(self.repo, REF), self.first)
        self.assertTrue(self.backend.update_ref(self.repo, REF, self.second, self.first))
        self.assertEqual(self.backend.ref_oid(self.repo, REF), self.second)

    def test_object_info_resolves_refs_and_paths_and_reports_missing_as_none(self):
        self.backend.update_ref(self.repo, REF, self.first, None)
        info = self.backend.object_info(self.repo, [REF, REF + ':research', f'{self.first}:research/state.json',
                                                    f'{self.first}:research/absent.json'])
        self.assertEqual(info, [(self.first, 'commit', info[0][2]), (self.research, 'tree', info[1][2]),
                                (self.blob, 'blob', len(b'{"a": 1}\n')), None])

    def test_read_objects_returns_kind_and_exact_bytes_and_none_for_missing(self):
        read = self.backend.read_objects(self.repo, [f'{self.first}:research/state.json',
                                                     f'{self.first}:runtime/queue.json',
                                                     f'{self.first}:nothing', f'{self.first}:research'])
        self.assertEqual(read[:3], [('blob', b'{"a": 1}\n'), ('blob', b'second\n'), None])
        self.assertEqual(read[3][0], 'tree')

    def test_list_tree_is_recursive_and_includes_subtrees(self):
        rows = sorted(self.backend.list_tree(self.repo, self.first), key=lambda row: row[3])
        rows = [(mode, kind, oid, path.decode('utf-8')) for mode, kind, oid, path in rows]
        self.assertEqual([(row[1], row[3]) for row in rows], [
            ('tree', 'research'), ('blob', 'research/state.json'), ('tree', 'runtime'), ('blob', 'runtime/queue.json')])
        self.assertEqual({row[3]: row[2] for row in rows}['research/state.json'], self.blob)

    def test_write_object_stores_the_exact_object_under_gits_oid_once(self):
        body = b'{"written": true}\n'
        raw = b'blob %d\0' % len(body) + body
        expected = (hashlib.sha256 if self.object_format == 'sha256' else hashlib.sha1)(raw).hexdigest()
        self.assertEqual(self.backend.write_object(self.repo, 'blob', body), expected)
        self.assertEqual(self.backend.write_object(self.repo, 'blob', body), expected)
        self.assertEqual(self.backend.read_objects(self.repo, [expected]), [('blob', body)])
        self.assertEqual(self.backend.object_info(self.repo, [expected]), [(expected, 'blob', len(body))])

    def test_written_trees_and_commits_resolve_like_objects_already_in_the_repository(self):
        blob = self.backend.write_object(self.repo, 'blob', b'written\n')
        written_tree = self.backend.write_object(self.repo, 'tree', b'40000 research\0' + bytes.fromhex(self.research)
                                                 + b'100644 state.json\0' + bytes.fromhex(blob))
        signature = 'do-math <do-math@invalid> 1700000000 +0000'
        written = self.backend.write_object(self.repo, 'commit', (
            f'tree {written_tree}\nparent {self.first}\nauthor {signature}\ncommitter {signature}\n\ndo-math state\n'
        ).encode())
        self.assertEqual(self.backend.read_objects(self.repo, [f'{written}:state.json', f'{written}:research/state.json']),
                         [('blob', b'written\n'), ('blob', b'{"a": 1}\n')])
        self.assertEqual(self.backend.first_parent_line(self.repo, self.first, written), [written])

    def test_first_parent_line_lists_commits_after_parent_up_to_head_in_order(self):
        self.assertEqual(self.backend.first_parent_line(self.repo, self.first, self.third), [self.second, self.third])
        self.assertEqual(self.backend.first_parent_line(self.repo, self.third, self.third), [])

    def configure_project(self, *, head=True):
        """Declare the same index/worktree in each backend's fixture."""
        raise NotImplementedError

    def test_project_snapshot_reports_subtree_and_repository_relative_index(self):
        self.configure_project()
        project = self.repo / 'research'
        root = self.backend.project_repository_root(project)
        self.assertEqual(root, self.repo.resolve())
        facts = self.backend.project_snapshot(project, root)
        self.assertEqual(facts.repository_root, root)
        self.assertEqual(facts.tree_oid, self.research)
        self.assertEqual(facts.raw_diff, b'')
        self.assertEqual(facts.tracked_paths, frozenset({'research/state.json'}))
        whole = self.backend.project_snapshot(self.repo, root)
        self.assertEqual(whole.tree_oid, self.root)
        self.assertEqual(whole.tracked_paths, frozenset({'research/state.json', 'runtime/queue.json'}))

    def test_project_without_head_or_subtree_has_none_tree(self):
        self.configure_project(head=False)
        facts = self.backend.project_snapshot(self.repo, self.repo.resolve())
        self.assertIsNone(facts.tree_oid)
        self.assertEqual(facts.raw_diff, b'')
        self.assertEqual(facts.tracked_paths, frozenset())

    def test_project_untracked_subdirectory_has_no_tree_or_index_paths(self):
        self.configure_project()
        project = self.repo / 'untracked'
        project.mkdir()
        facts = self.backend.project_snapshot(project, self.repo.resolve())
        self.assertEqual((facts.tree_oid, facts.raw_diff, facts.tracked_paths), (None, b'', frozenset()))

    def test_project_without_git_has_empty_facts_and_outside_root_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            outside = Path(directory).resolve()
            self.assertIsNone(self.backend.project_repository_root(outside))
            facts = self.backend.project_snapshot(outside, None)
            self.assertEqual((facts.repository_root, facts.tree_oid, facts.raw_diff, facts.tracked_paths),
                             (None, None, b'', frozenset()))
            with self.assertRaises(ValueError):
                self.backend.project_snapshot(outside, self.repo.resolve())

    def test_project_stop_before_and_after_each_read(self):
        self.configure_project()
        for count in range(1, 7):
            seen = []
            def stop():
                seen.append(None)
                return len(seen) == count
            with self.subTest(check=count), self.assertRaisesRegex(RuntimeError, 'stopped'):
                self.backend.project_snapshot(self.repo, self.repo.resolve(), should_stop=stop)
            self.assertEqual(len(seen), count)
        for count in (1, 2):
            seen = []
            def stop():
                seen.append(None)
                return len(seen) == count
            with self.assertRaisesRegex(RuntimeError, 'stopped'):
                self.backend.project_repository_root(self.repo, should_stop=stop)
            self.assertEqual(len(seen), count)

    def test_project_disappeared_repository_is_tracked_path_failure(self):
        self.configure_project()
        root = self.backend.project_repository_root(self.repo)
        self.remove_project()
        with self.assertRaisesRegex(RuntimeError, '^cannot read tracked paths for the configured project$'):
            self.backend.project_snapshot(self.repo, root)

    def test_project_diff_preserves_non_utf8_bytes(self):
        self.configure_project()
        raw = b'\xff\n'
        new = write_object(self.repo, 'blob', raw, self.object_format)
        expected = (f'diff --git a/research/state.json b/research/state.json\n'
                    f'index {self.blob[:7]}..{new[:7]} 100644\n'
                    '--- a/research/state.json\n+++ b/research/state.json\n'
                    '@@ -1 +1 @@\n-{"a": 1}\n').encode() + b'+\xff\n'
        (self.repo / 'research/state.json').write_bytes(raw)
        self.declare_project_diff(expected)
        facts = self.backend.project_snapshot(self.repo / 'research', self.repo.resolve())
        self.assertEqual(facts.raw_diff, expected)
        self.assertEqual(facts.tree_oid, self.research)
        self.assertEqual(facts.tracked_paths, frozenset({'research/state.json'}))
