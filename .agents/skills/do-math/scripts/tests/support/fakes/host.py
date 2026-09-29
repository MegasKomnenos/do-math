"""Fake host port: a machine whose Lean, toolchain and provider CLIs a test declares.

``lean`` is the command Lean discovery finds (None: no Lean). A toolchain
identity check answers a malformed identity with the product's own shape
errors, as the real check does first, and a well-formed one with
``toolchain_errors`` (empty: the local files match). Every provider CLI is
present with ``identity`` and a verified command surface offering
``capabilities``; profiles of one provider share one observation.
"""
from copy import deepcopy

from do_math.lean_evidence import toolchain_errors as shape_errors

IDENTITY = {"host": "fake host", "implementation": "fake provider CLI"}
CAPABILITIES = {"jsonl": True, "model": True, "structured_output": True}


class FakeHost:
    def __init__(self, *, lean=None, toolchain_errors=(), identity=IDENTITY, capabilities=CAPABILITIES):
        self.lean, self.toolchain_errors = lean, list(toolchain_errors)
        self.identity, self.capabilities = deepcopy(identity), dict(capabilities)

    def discover_lean(self):
        return deepcopy(self.lean)

    def toolchain_identity_errors(self, toolchain, *, should_stop=None):
        return shape_errors(toolchain) or list(self.toolchain_errors)

    def cli_observation_key(self, profile):
        return ('fake', profile['ai']['provider'])

    def cli_identity(self, profile):
        return deepcopy(self.identity)

    def cli_describe(self, profile):
        return {"identity": deepcopy(self.identity), "verified": True,
                "scope": "synthetic_test_evidence_not_host_verification",
                "supported": dict(self.capabilities), "unknown": [],
                "version_sha256": "a" * 64, "exec_help_sha256": "b" * 64}


class ObservedHost(FakeHost):
    """The fake host with counted CLI observations; ``failures`` raises at the given describe call numbers.

    ``per_profile`` gives each profile its own observation key, as distinct CLI
    installations would, so a batch observes profiles one by one.
    """

    def __init__(self, *, failures=(), per_profile=False, **facts):
        super().__init__(**facts)
        self.key_calls = self.identity_calls = self.describe_calls = 0
        self.failures, self.per_profile = set(failures), per_profile
        self.description = None

    def observations(self):
        """``(key, identity, describe)`` call counts: every CLI observation the host was asked for."""
        return self.key_calls, self.identity_calls, self.describe_calls

    def cli_observation_key(self, profile):
        self.key_calls += 1
        return ('fake', profile['id']) if self.per_profile else super().cli_observation_key(profile)

    def cli_identity(self, profile):
        self.identity_calls += 1
        return super().cli_identity(profile)

    def cli_describe(self, profile):
        self.describe_calls += 1
        if self.describe_calls in self.failures:
            raise RuntimeError('probe failed')
        return deepcopy(self.description) if self.description is not None else super().cli_describe(profile)


def make_fake(**facts):
    return FakeHost(**facts)
