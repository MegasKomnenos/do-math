"""The model double with the explicit answers of the scheduling region's legacy runners.

The legacy tests answered a call with an explicit output in two ways, and
``support.model``'s builders always start from the default responder (which
also writes the role's activity extensions), so neither is reproduced there:

- ``explicit(value)``: the legacy ``producer_result`` runner. ``value`` alone
  is the output: candidates are bound, the response is sealed and the model
  submits it with the workspace tool; no default response or extension file.
  As the legacy ``submit_intent`` failed the call unless the receipt was
  ``accepted``, the provider process then exits with an error and no final
  message, so the engine receives a failed call.
- ``native_final(value)``: a runner that returned its output without the
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

from support.model import Answer, FakeCLI, ModelDouble, default


class Explicit(Answer):
    def __init__(self, value, *, native, extensions=None):
        super().__init__(lambda out, ctx: deepcopy(value), sealed=not native)
        self.value, self.native, self.extensions = value, native, extensions


class NativeFinal(dict):
    """An output the model answers as its final message, not through the submission tool."""


class Produced(dict):
    """An explicit output the model submits and that must be accepted (the legacy ``submit_intent`` rule)."""


class SubmissionRejected(Exception):
    pass


def explicit(value, *, extensions=None):
    """``extensions``, when given, is written to the workspace's ``activity-extensions.json`` before the seal."""
    return Explicit(value, native=False, extensions=extensions)


def native_final(value):
    return Explicit(value, native=True)


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
        try:
            return super().communicate(input, timeout)
        except SubmissionRejected:
            # Like the legacy producer, the provider process fails when its submission is not accepted:
            # it exits with an error and leaves no final message.
            self.returncode = 1
            return None, None

    def _submit(self, out):
        """``FakeCLI._submit``, keeping the whole final receipt the producer received in ``model.receipts``."""
        if isinstance(out, NativeFinal):
            return json.dumps(out, ensure_ascii=False)
        from do_math.canonical import canonical_json
        from do_math.control_protocol import SUBMIT_INTENT
        from do_math.control_server import wait_receipt
        from do_math.control_transport import FINAL_RECEIPTS
        from do_math.submission_tool import request_control
        from support.fakes.calls import owner_turn
        (self.workspace / 'output.json').write_bytes(canonical_json(out))
        delivery = request_control(self.workspace, 'output.json', kind=SUBMIT_INTENT, wait_seconds=0,
                                   clock=self.model.clock)
        binding = json.loads((self.workspace / 'input' / 'submission' / 'context.json').read_bytes())['control_binding']
        for _ in range(100):
            receipt = wait_receipt(binding, delivery['request_id'], 0, clock=self.model.clock)
            if receipt and receipt.get('state') in FINAL_RECEIPTS:
                self.model.receipts.append(receipt)
                if isinstance(out, Produced) and receipt['state'] != 'accepted':
                    raise SubmissionRejected(delivery['request_id'])
                return json.dumps({'submission': delivery['request_id'], 'receipt': receipt['state']})
            owner_turn()
        raise AssertionError('the owner did not receipt submission ' + delivery['request_id'] + ' in 100 passes')


class ScenarioModel(ModelDouble):
    def __init__(self, clock, responder=None):
        super().__init__(clock, responder)
        self.receipts, self.hooks = [], []

    def during(self, role, hook):
        """Run ``hook(context, workspace)`` in each ``role`` call before it answers."""
        self.hooks.append((role, hook))
        return self

    def spawn(self, command, *, stdin=None, stdout=None, stderr=None, cwd=None, env=None, shell=False,
              creationflags=0):
        return ScenarioCLI(self, list(command), stdout, stderr, Path(cwd))

    def output(self, role, ctx, workspace):
        from support.role_answers import bind_candidates, seal_response
        rule = next((rule for rule in self.rules if rule.answers and rule.matches(role, ctx)), None)
        answer = rule.next() if rule else default()
        if not isinstance(answer, Explicit):
            out = answer.make(self.responder.respond(role, ctx, workspace), ctx)
            if answer.sealed:
                bind_candidates(out, ctx)
                if answer.after_binding is not None:
                    answer.after_binding(out, ctx)
                seal_response(out, ctx, workspace)
            return out
        if answer.native:
            return NativeFinal(deepcopy(answer.value))
        out = Produced(deepcopy(answer.value))
        if answer.extensions is not None:
            (Path(workspace) / 'activity-extensions.json').write_text(json.dumps(answer.extensions), encoding='utf-8')
        bind_candidates(out, ctx)
        seal_response(out, ctx, workspace)
        return out


def scenario_model(sim, responder=None):
    sim.model = ScenarioModel(sim.clock, responder)
    return sim.model
