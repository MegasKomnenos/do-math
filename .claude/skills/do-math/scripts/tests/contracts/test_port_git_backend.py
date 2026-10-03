"""Git backend port contract (설계 2.2): the git process and the in-process fake answer alike.

Repositories are built without a git process: ``make_repository`` (the fake's
module) writes the minimal layout Git reads (HEAD, config, objects/, refs/heads/) and
``write_object`` writes loose objects, the form GitStateStore itself writes.
The real side (boundary/test_port_git_backend.py) checks that git reads this
layout too.
"""
import unittest

from support.fakes.git_backend import make_fake, ProjectWorktree


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


if __name__ == '__main__':
    unittest.main()
