"""Semantic Git boundary failures and observations, on the real in-process Git world."""
from support.fakes.git_backend import InProcessGit


class GitInitFaults(InProcessGit):
    def __init__(self, *, init_failure=None, inspect_failure=None):
        super().__init__()
        self.init_failure, self.inspect_failure = init_failure, inspect_failure
        self.observed = []

    def initialize_repository(self, repository):
        self.observed.append(('initialize', repository.is_dir(), tuple(repository.iterdir())))
        if isinstance(self.init_failure, BaseException):
            raise self.init_failure
        if self.init_failure:
            return False
        return super().initialize_repository(repository)

    def repository_exists(self, repository):
        self.observed.append(('exists', repository.is_dir()))
        if isinstance(self.inspect_failure, BaseException):
            raise self.inspect_failure
        if self.inspect_failure:
            return False
        return super().repository_exists(repository)
