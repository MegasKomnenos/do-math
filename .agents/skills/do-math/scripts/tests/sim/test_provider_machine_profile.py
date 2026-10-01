"""Machine (Lean) profiles: the profile pins the command, the verifier binds the tool's bytes (layer 2 and 3).

``execution_profiles.machine_invocation`` (layer 2) turns a formal-check
profile and its approved trust environment into the verifier's arguments;
``formal.verify_lean`` (layer 3) refuses a toolchain that changed after
approval before it starts any Job. The Jobs port fake records every launch, so
"not started" is observed rather than assumed.
"""
import hashlib
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from do_math import execution_profiles as ep
from do_math import formal
from support.provider_inputs import PROFILE_CONFIG
from support.provider_runs import ProviderJobs

SOURCE = "theorem t : True := True.intro"


def profiles(**changes):
    from support.entry import entry
    _entry = entry()
    return ep.build_profiles({**PROFILE_CONFIG, "lean_command": ["lean-A"], **changes}, host=_entry.ports.host)


def formal_profile(state):
    return next(p for p in state["execution_profiles"].values() if p["role"] == "formal_check")


def approved(tool, command):
    """An approved identity whose recorded executable is this tool file."""
    def digest(path):
        return hashlib.sha256(Path(path).read_bytes()).hexdigest()
    checker = Path(formal.__file__).resolve()
    return {"executable": str(Path(tool).resolve()), "sha256": digest(tool), "configured_command": command,
            "version": "fixture", "version_exit": 0, "verifier_sha256": digest(checker),
            "verifier_path": str(checker), "executables": {str(Path(tool).resolve()): digest(tool)}, "project": None}


class MachineProfileTests(unittest.TestCase):
    def test_machine_profile_pins_the_command_and_the_verifier_checks_tool_bytes(self):
        from support.entry import entry
        _entry = entry()
        a, b = profiles(), profiles(lean_command=["lean-B"])
        self.assertNotEqual(ep.profile_ref(formal_profile(a)), ep.profile_ref(formal_profile(b)))
        with tempfile.TemporaryDirectory() as directory:
            tool = Path(directory) / "lean.exe"
            tool.write_bytes(b"edition one")
            p = formal_profile(profiles(lean_command=[str(tool)]))
            env = {"toolchain": approved(tool, [str(tool)])}
            args = ep.machine_invocation(p, trust_environment=env)
            self.assertNotIn("timeout_seconds", args)
            self.assertEqual(args["lean_command"], [str(tool)])
            self.assertEqual(args["expected_toolchain"], env["toolchain"])
            tool.write_bytes(b"edition two")
            second = profiles(lean_command=[str(tool)])
            # The profile names the command only; the approved identity binds its bytes once, in the verifier.
            self.assertEqual(ep.profile_ref(p), ep.profile_ref(formal_profile(second)))
            self.assertEqual(ep.machine_invocation(p, trust_environment=env), args)
            jobs = ProviderJobs()
            result = formal.verify_lean(source=SOURCE, declarations=["t"], workspace=Path(directory), jobs=jobs, **args, clock=_entry.ports.clock, environment=_entry.environment)
            self.assertEqual(jobs.launched, [], "changed tool was started")
            self.assertEqual((result["status"], result["reason"]), ("rejected", "approved toolchain changed before execution"))
            self.assertEqual(result["identity_errors"], ["approved toolchain file changed: " + str(tool.resolve())])
            self.assertEqual(result["error_kind"], "trust_environment")
            with self.assertRaisesRegex(ValueError, "profile command differs from the approved trust environment"):
                ep.machine_invocation(formal_profile(second),
                                      trust_environment={"toolchain": {"configured_command": ["different"]}})

    def test_machine_command_alias_keeps_adopted_argv_and_the_verifier_checks_resolution(self):
        from support.entry import entry
        _entry = entry()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "approved").mkdir()
            (root / "elsewhere").mkdir()
            tool = root / "approved" / "lean.exe"
            tool.write_bytes(b"edition")
            p = formal_profile(profiles(lean_command=["lean"]))
            args = ep.machine_invocation(p, trust_environment={"toolchain": approved(tool, ["lean"])})
            self.assertEqual(args["lean_command"], ["lean"])
            # On this search path the alias resolves to another file with the same bytes.
            other = root / "elsewhere" / "lean.exe"
            other.write_bytes(b"edition")
            jobs = ProviderJobs()
            with patch.dict(os.environ, {"PATH": str(other.parent)}):
                result = formal.verify_lean(source=SOURCE, declarations=["t"], workspace=root, jobs=jobs, **args, clock=_entry.ports.clock, environment=_entry.environment)
            self.assertEqual(jobs.launched, [], "another resolution was started")
            self.assertEqual((result["status"], result["reason"]), ("rejected", "approved toolchain changed before execution"))
            self.assertEqual(result["error_kind"], "trust_environment")


if __name__ == "__main__":
    unittest.main()
