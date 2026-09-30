"""The installed Lean behind a Sim's formal checks, for the knowledge boundary tests.

A Sim's Jobs fake runs ``formal._worker`` in process with the Lean double at its
spawn seam. ``InstalledLean`` is a spawn for that seam that starts the given
command as a real process (``subprocess.Popen``), so the owner's formal check
compiles with the portable Lean (``provider_fixtures.actual_command``; a
worktree reaches it through a junction to the main tree's toolchains). The
Job around it stays the fake's; real Jobs are ``boundary.test_knowledge_lean_verifier``'s.

- ``installed_toolchain()``: the installed Lean's identity as ``verify_lean``
  observes it on the knowledge candidate "Truth" (once per process); a failed
  observation fails at once.
- ``adopt_installed(sim, toolchain, directory)``: register ``toolchain`` by
  control (``knowledge_roundtrip.installed_request``, its record under
  ``directory``), make the host port find its command and configure no Lean
  command (``lean_command: None``), move the instance to it
  (``engine_lifecycle.transition``, the owner's trust activation) and put
  ``InstalledLean`` at the Lean seam. Returns the environment ID.

  The configured command (None) then differs from the approved command, as the
  legacy fixture's ``'unapproved-config-command'`` did (조사 K-42), while the
  profile's pinned command is the discovered, approved one
  (``execution_profiles._lean_contract``), so the formal check runs. An owner
  that handed the verifier the configured command instead of the approved one
  would give it no command.
"""
from copy import deepcopy
from pathlib import Path
import subprocess
import tempfile

from do_math.formal import verify_lean
from knowledge_fixtures import knowledge_candidate
from provider_fixtures import actual_command
from support.engine_lifecycle import applied, run_machine, transition
from support.knowledge_roundtrip import installed_request

_OBSERVED = []


def installed_toolchain():
    if not _OBSERVED:
        with tempfile.TemporaryDirectory() as directory:
            result = verify_lean(source=knowledge_candidate()['lean_code'], declarations=['truth'],
                                 workspace=Path(directory), lean_command=actual_command())
        if result['status'] != 'verified':
            raise AssertionError('the installed Lean did not verify the candidate: ' + repr(result))
        _OBSERVED.append(result['toolchain'])
    return deepcopy(_OBSERVED[0])


class InstalledLean:
    """A spawn that starts each Lean command as a real process; ``commands`` lists what it started."""

    def __init__(self):
        self.commands = []

    def spawn(self, command, *, cwd=None, stdout=None, stderr=None, shell=False, creationflags=0):
        self.commands.append(list(command))
        return subprocess.Popen(list(command), cwd=cwd, stdout=stdout, stderr=stderr, shell=shell,
                                creationflags=creationflags)


def adopt_installed(sim, toolchain, directory):
    request = installed_request(directory, toolchain)
    applied(sim, 'trust', config=request)
    environment = next(key for key, row in sim.instance['trust_environments'].items()
                       if row['toolchain'] == request['toolchain'])
    sim.ports.host.lean = list(toolchain['configured_command'])
    applied(sim, 'configure', config={'lean_command': None})
    if sim.instance['config']['lean_command'] is not None:
        raise AssertionError('the configured Lean command was not cleared')
    transition(sim, environment)
    run_machine(sim, 'trust_activate')
    if sim.instance['active_trust_environment'] != environment:
        raise AssertionError('the move to the installed toolchain did not activate: ' + repr(sim.waiting()))
    sim.lean = InstalledLean()
    return environment
