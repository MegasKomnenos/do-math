"""Host observation port: what this machine offers, observed without changing it (설계 10절 A17, A18).

Three observations: the Lean command found when the configuration names none,
the local facts behind an approved toolchain identity, and the provider CLI a
profile runs (the key under which profiles may share one observation, its
identity and its command surface).
"""
from typing import Protocol


class Host(Protocol):
    def discover_lean(self) -> list | None:
        """The installed Lean command, or None; never downloads or changes PATH."""

    def toolchain_identity_errors(self, toolchain: dict, *, should_stop=None) -> list:
        """Why the local executables, checker and project differ from ``toolchain``; empty when they match."""

    def cli_observation_key(self, profile: dict):
        """A hashable key; profiles with equal keys may share one CLI observation."""

    def cli_identity(self, profile: dict) -> dict:
        """The local identity of the provider CLI ``profile`` runs; claims no behavioural capability."""

    def cli_describe(self, profile: dict) -> dict:
        """The provider CLI's command surface (version and help) as a capability observation."""
