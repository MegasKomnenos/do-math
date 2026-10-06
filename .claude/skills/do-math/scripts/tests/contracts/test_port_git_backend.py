"""Git backend port contract (설계 2.2): the git process and the in-process fake answer alike.

Repositories are built without a git process: ``make_repository`` (the fake's
module) writes the minimal layout Git reads (HEAD, config, objects/, refs/heads/) and
``write_object`` writes loose objects, the form GitStateStore itself writes.
The real side (boundary/test_port_git_backend.py) checks that git reads this
layout too.
"""
import os
import stat
import sys
import tempfile
import unittest
from unittest.mock import patch

from do_math.file_io import atomic_replace
from support.fakes.git_backend import make_fake, make_repository, ProjectWorktree


from support.port_contracts.git_backend import GitBackendContract

class FakeGitBackendContract(GitBackendContract, unittest.TestCase):
    def make(self):
        return make_fake()

    def configure_project(self, *, head=True):
        self.backend.worktrees[self.repo.resolve()] = ProjectWorktree(
            trees={'.': self.root, 'research': self.research} if head else {},
            tracked_paths=frozenset({'research/state.json', 'runtime/queue.json'}) if head else frozenset())
        (self.repo / 'research').mkdir(exist_ok=True)

    def declare_project_diff(self, raw):
        self.backend.worktrees[self.repo.resolve()].diffs['research'] = raw

    def remove_project(self):
        del self.backend.worktrees[self.repo.resolve()]


class FakeSha256GitBackendContract(FakeGitBackendContract):
    object_format = 'sha256'

    def make(self):
        return make_fake()


class FakeGitRefPublicationTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.repo = make_repository(directory.name)
        self.backend = make_fake()
        self.ref = 'refs/heads/publication'
        self.path = self.repo / '.git' / self.ref
        self.lock = self.path.with_name(self.path.name + '.lock')
        self.old, self.new = 'a' * 40, 'b' * 40
        self.assertTrue(self.backend.update_ref(self.repo, self.ref, self.old, None))

    @unittest.skipUnless(os.name == 'nt', 'Windows read-only files refuse replacement')
    def test_transient_publication_denial_retries_the_owned_lock(self):
        self.path.chmod(stat.S_IREAD)
        self.addCleanup(self.path.chmod, stat.S_IWRITE)
        pending = []

        def release_read_only(_delay):
            pending.append(self.lock.read_bytes())
            self.assertEqual(self.path.read_text().strip(), self.old)
            self.assertFalse(self.backend.update_ref(self.repo, self.ref, 'c' * 40, self.old))
            self.path.chmod(stat.S_IWRITE)

        with patch('time.sleep', side_effect=release_read_only):
            self.assertTrue(self.backend.update_ref(self.repo, self.ref, self.new, self.old))
        self.assertEqual(pending, [(self.new + os.linesep).encode('ascii')])
        self.assertEqual(self.backend.ref_oid(self.repo, self.ref), self.new)
        self.assertFalse(self.lock.exists())

    @unittest.skipUnless(os.name == 'nt', 'Windows read-only files refuse replacement')
    def test_permanent_publication_denial_releases_owned_lock_for_later_update(self):
        """About 0.4 s: exhaust the real bounded file-publication retries."""
        self.path.chmod(stat.S_IREAD)
        self.addCleanup(self.path.chmod, stat.S_IWRITE)
        with self.assertRaises(PermissionError):
            self.backend.update_ref(self.repo, self.ref, self.new, self.old)
        self.assertEqual(self.backend.ref_oid(self.repo, self.ref), self.old)
        self.assertFalse(self.lock.exists())
        self.path.chmod(stat.S_IWRITE)
        self.assertTrue(self.backend.update_ref(self.repo, self.ref, self.new, self.old))
        self.assertEqual(self.backend.ref_oid(self.repo, self.ref), self.new)

    def test_cas_rejection_removes_own_lock_and_leaves_another_writers_lock(self):
        self.assertFalse(self.backend.update_ref(self.repo, self.ref, self.new, None))
        self.assertFalse(self.lock.exists())
        self.lock.write_bytes(b'another writer')
        self.assertFalse(self.backend.update_ref(self.repo, self.ref, self.new, self.old))
        self.assertEqual(self.lock.read_bytes(), b'another writer')
        self.assertEqual(self.backend.ref_oid(self.repo, self.ref), self.old)

    def test_success_leaves_lock_acquired_by_next_writer_after_publication(self):
        previous = sys.getprofile()

        def next_writer(frame, event, value):
            if ((event == 'return' and frame.f_code is atomic_replace.__code__)
                    or (event == 'c_return' and value is os.replace
                        and frame.f_code is self.backend.update_ref.__func__.__code__)):
                with self.lock.open('xb') as stream:
                    stream.write(b'next writer')

        sys.setprofile(next_writer)
        try:
            self.assertTrue(self.backend.update_ref(self.repo, self.ref, self.new, self.old))
        finally:
            sys.setprofile(previous)
        self.assertEqual(self.lock.read_bytes(), b'next writer')
        self.assertEqual(self.backend.ref_oid(self.repo, self.ref), self.new)


if __name__ == '__main__':
    unittest.main()
