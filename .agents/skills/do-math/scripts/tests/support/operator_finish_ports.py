"""Faults at operator external ports, without replacing product names."""
from support.fakes.scheduler import FakeScheduler
from support.fakes.git_backend import InProcessGit


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
