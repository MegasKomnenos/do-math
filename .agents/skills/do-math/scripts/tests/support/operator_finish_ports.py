"""Faults at operator external ports, without replacing product names."""
from support.fakes.scheduler import FakeScheduler
from support.fakes.git_backend import InProcessGit
from do_math.ports.git_backend import ProjectSnapshot


class SourceGit(InProcessGit):
    """Explicit source-worktree reads; state-storage operations remain InProcessGit's."""
    def __init__(self, repository, *, commit='a' * 40, tree='b' * 40, diff=b'', tracked_paths=(), objects=None):
        super().__init__(objects)
        self.source_repository, self.source_commit = repository, commit
        self.source_snapshot = ProjectSnapshot(repository, tree, diff, frozenset(tracked_paths))

    def project_repository_root(self, project_root, *, should_stop=None):
        return self.source_repository

    def project_snapshot(self, project_root, repository_root, *, should_stop=None):
        return self.source_snapshot

    def object_info(self, repository, specs):
        if repository == self.source_repository and specs == ['HEAD']:
            return [None if self.source_commit is None else (self.source_commit, 'commit', 123)]
        return super().object_info(repository, specs)


class Scheduler(FakeScheduler):
    def __init__(self, *, error=None, observe=None):
        super().__init__()
        self.error, self.observe = error, observe

    def run(self, action, arguments):
        if self.observe:
            self.observe(action, arguments)
        if self.error:
            self.calls.append((action, dict(arguments)))
            raise self.error
        return super().run(action, arguments)


class UnreadableOnce(InProcessGit):
    """One failing status load; recovery's subsequent locked load still works."""
    def __init__(self, objects):
        super().__init__(objects)
        self.fail = True

    def describe(self, repository):
        if self.fail:
            self.fail = False
            raise SyntaxError('engine broken')
        return super().describe(repository)
