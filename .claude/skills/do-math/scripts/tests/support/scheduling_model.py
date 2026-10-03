"""The model double with the explicit answers of the scheduling region's legacy runners.

The legacy tests answered a call with an explicit output in two ways, and
``support.model``'s builders always start from the default responder (which
also writes the role's activity extensions), so neither is reproduced there:

- ``explicit(value)``: the legacy ``producer_result`` runner. ``value`` alone
  is the output: candidates are bound, the response is sealed and the model
  submits it with the workspace tool; no default response or extension file.
  Normal calls require acceptance. A rejection scene declares
  expected_receipt='rejected'; returncode=1 separately preserves a provider
  failure with no final message when that is the test's contract.
- ``explicit(value, mode="standalone", expected_receipt=None)``: a runner that returned its output without the
  submission tool. ``value`` is the provider's final message and nothing is
  bound, sealed or submitted, so the engine receives it as a native final.

``scenario_model(sim, responder=None)`` gives ``sim`` a ``ScenarioModel`` (the
Sim resolves ``sim.model`` at each call) and returns it; ``on(...).reply(...)``
takes these answers beside ``support.model``'s. ``receipts`` lists every final
receipt a tool submission received, as the transport returned it to the model.
``during(role, hook)`` runs ``hook(context, workspace)`` inside each call of
``role`` (in the provider process, while the owner waits for the call) before
the model answers, so a test can observe what the model sees during its call.
"""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path

from support.model import Answer, FakeCLI, ModelDouble


class Explicit(Answer):
    def __init__(self, value, *, mode, expected_receipt, returncode, extensions=None):
        super().__init__(lambda out, ctx: deepcopy(value), sealed=mode == 'bound', mode=mode,
                         expected_receipt=expected_receipt, returncode=returncode)
        self.extensions = extensions


def explicit(value, *, extensions=None, mode="bound", expected_receipt="accepted", returncode=0):
    """Submit an explicit sealed draft; negative scenes declare receipt and provider exit."""
    return Explicit(value, mode=mode, expected_receipt=expected_receipt,
                    returncode=returncode, extensions=extensions)


class ScenarioCLI(FakeCLI):
    def communicate(self, input=None, timeout=None):
        from support.default_responder import context_from
        from support.model import MARKER
        prompt = input.decode('utf-8')
        role = prompt.split(MARKER, 1)[1].split('.', 1)[0]
        ctx = context_from(prompt, self.workspace)
        for hook_role, hook in self.model.hooks:
            if hook_role == role:
                hook(ctx, self.workspace)
        return super().communicate(input, timeout)


class ScenarioModel(ModelDouble):
    def __init__(self, clock, responder=None):
        super().__init__(clock, responder)
        self.hooks = []

    def during(self, role, hook):
        """Run ``hook(context, workspace)`` in each ``role`` call before it answers."""
        self.hooks.append((role, hook))
        return self

    def spawn(self, command, *, stdin=None, stdout=None, stderr=None, cwd=None, env=None, shell=False,
              creationflags=0):
        return ScenarioCLI(self, list(command), stdout, stderr, Path(cwd))

    def render(self, answer, role, ctx, workspace):
        from support.role_answers import bind_candidates, seal_response
        if not isinstance(answer, Explicit):
            return super().render(answer, role, ctx, workspace)
        out = answer.make(None, ctx)
        if answer.extensions is not None:
            (Path(workspace) / 'activity-extensions.json').write_text(json.dumps(answer.extensions), encoding='utf-8')
        if answer.sealed:
            bind_candidates(out, ctx)
            seal_response(out, ctx, workspace)
        return out


def scenario_model(sim, responder=None):
    sim.model = ScenarioModel(sim.clock, responder)
    return sim.model
