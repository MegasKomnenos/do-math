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
import unittest
import zlib

from support.fakes.git_backend import make_fake, make_repository

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

    def test_first_parent_line_lists_commits_after_parent_up_to_head_in_order(self):
        self.assertEqual(self.backend.first_parent_line(self.repo, self.first, self.third), [self.second, self.third])
        self.assertEqual(self.backend.first_parent_line(self.repo, self.third, self.third), [])


class FakeGitBackendContract(GitBackendContract, unittest.TestCase):
    def make(self):
        return make_fake()


class FakeSha256GitBackendContract(GitBackendContract, unittest.TestCase):
    object_format = 'sha256'

    def make(self):
        return make_fake()


if __name__ == '__main__':
    unittest.main()
