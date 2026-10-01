"""Host observation port contract (설계 10절 A17, A18): this machine's observations and the fake answer alike.

The shared contract holds what both sides must answer identically: a malformed
toolchain identity gets exactly the product's shape errors, discovery finds a
command or nothing, and a CLI observation has its key, identity and command
surface. What the local files and CLIs actually are is the real side's own
fact (boundary tier); the fake answers what a test declares.
"""

from pathlib import Path


from do_math.lean_evidence import toolchain_errors


PROFILE = {"ai": {"provider": "codex"}}

WELL_FORMED = {'executable': 'lean.exe', 'sha256': 'a' * 64, 'configured_command': ['lean'], 'version': 'Lean 4',
               'version_exit': 0, 'verifier_sha256': 'b' * 64, 'verifier_path': str(Path(__file__).resolve()),
               'executables': {}, 'project': None}

class HostContract:
    def make(self):
        raise NotImplementedError

    def test_a_malformed_toolchain_identity_gets_the_shape_errors(self):
        for toolchain in ({}, {'executable': ''}, []):
            with self.subTest(toolchain=toolchain):
                self.assertEqual(self.make().toolchain_identity_errors(toolchain), toolchain_errors(toolchain))
                self.assertNotEqual(toolchain_errors(toolchain), [])

    def test_discovery_finds_a_command_or_nothing(self):
        found = self.make().discover_lean()
        self.assertTrue(found is None or (isinstance(found, list) and found
                                          and all(isinstance(part, str) and part for part in found)), found)

    def test_a_cli_observation_has_a_stable_key_an_identity_and_a_command_surface(self):
        host = self.make()
        key = host.cli_observation_key(PROFILE)
        self.assertEqual(key, host.cli_observation_key(PROFILE))
        hash(key)
        self.assertIsInstance(host.cli_identity(PROFILE), dict)
        self.assertIsInstance(host.cli_describe(PROFILE)['verified'], bool)
