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


def make_fake(**facts):
    return FakeHost(**facts)
