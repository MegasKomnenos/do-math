"""Model calls for the currentness tests: an interrupted provider call, beside ``scheduling_model``'s answers and hooks.

The legacy currentness tests ran local scripted runners in real Jobs: a
``FailingRunner`` wrote partial files and a checkpoint into its workspace and
returned ``failed``; a ``ChangingRunner`` changed a source and waited for the
owner to apply its control during the call. On a Sim the worker runs the
provider CLI double in process, so these are the CLI double's behaviours:

- ``currentness_model(sim, responder=None)`` gives ``sim`` a ``CurrentnessModel``
  (a ``scheduling_model.ScenarioModel``, so ``on``, ``during``, ``explicit``
  and ``native_final`` work) and returns it.
- ``interrupt(role, write)``: the next call of ``role`` runs ``write(context,
  workspace)`` and then the provider process exits with an error and no final
  message ("fixture interruption" on its error stream), as a provider
  interrupted mid-call does; the worker and the engine's collector judge the
  result. Later calls of ``role`` answer normally.
- ``reseal(role, change)``: the next answer of ``role``, once bound and sealed
  as one bundle, has ``change(output, context)`` rewrite its declared bundles
  (for a split research response of more than one bundle).
- ``await_applied(sim, request)``: inside a call, hand the turn to the owner
  until it has applied the queued public control ``request`` (the legacy
  ``await_control``, on the calls fake's turns instead of a timed poll).
"""
from __future__ import annotations

from pathlib import Path

from support.fakes.calls import owner_turn
from support.scheduling_model import ScenarioCLI, ScenarioModel


class InterruptedCLI(ScenarioCLI):
    def communicate(self, input=None, timeout=None):
        from support.default_responder import context_from
        from support.model import MARKER
        prompt = input.decode('utf-8')
        role = prompt.split(MARKER, 1)[1].split('.', 1)[0]
        write = self.model.interruptions.pop(role, None)
        if write is None:
            return super().communicate(input, timeout)
        write(context_from(prompt, self.workspace), self.workspace)
        self.stderr.write(b'fixture interruption\n')
        self.returncode = 1
        return None, None


class CurrentnessModel(ScenarioModel):
    def __init__(self, clock, responder=None):
        super().__init__(clock, responder)
        self.interruptions, self.reseals = {}, {}

    def interrupt(self, role, write):
        self.interruptions[role] = write
        return self

    def reseal(self, role, change):
        """The next answer of ``role``, once sealed, has ``change(output, context)`` rewrite its declared bundles."""
        self.reseals[role] = change
        return self

    def output(self, role, ctx, workspace):
        out = super().output(role, ctx, workspace)
        change = self.reseals.pop(role, None)
        if change is not None:
            change(out, ctx)
        return out

    def spawn(self, command, *, stdin=None, stdout=None, stderr=None, cwd=None, env=None, shell=False,
              creationflags=0):
        return InterruptedCLI(self, list(command), stdout, stderr, Path(cwd))


def currentness_model(sim, responder=None):
    sim.model = CurrentnessModel(sim.clock, responder)
    return sim.model


def await_applied(sim, request, turns=100):
    for _ in range(turns):
        if request['request_id'] in sim.engine.runtime.get('processed_controls', []):
            return
        owner_turn()
    raise AssertionError('the owner did not apply control ' + request['request_id'] + f' in {turns} turns')
