"""The real host observation port (layer 3, 설계 10절 A18): this machine's Lean and provider CLIs.

The operations call the observation code where it lives, ``formal`` and the
provider adapters, through their modules; the port only names the three
observations the product makes of its host.
"""
from . import formal


def adapter_for(profile, *, clock, jobs):
    """The provider adapter whose CLI ``profile`` runs."""
    from .claude_adapter import provider_adapter
    return provider_adapter(profile["ai"]["provider"], clock=clock, jobs=jobs)


class LocalHost:
    def __init__(self, *, jobs, clock, environment, git_backend):
        self.jobs, self.clock, self.environment = jobs, clock, environment
        self.git_backend = git_backend

    def discover_lean(self):
        return formal.discover_lean()

    def toolchain_identity_errors(self, toolchain, *, should_stop=None):
        return formal.toolchain_identity_errors(toolchain, should_stop=should_stop, jobs=self.jobs, clock=self.clock, environment=self.environment, git_backend=self.git_backend)

    def cli_observation_key(self, profile):
        return adapter_for(profile, clock=self.clock, jobs=self.jobs).observation_key()

    def cli_identity(self, profile):
        return adapter_for(profile, clock=self.clock, jobs=self.jobs).capability_identity()

    def cli_describe(self, profile):
        return adapter_for(profile, clock=self.clock, jobs=self.jobs).describe()
