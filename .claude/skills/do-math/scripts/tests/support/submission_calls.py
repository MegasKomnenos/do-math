"""The model double with the answers of the submission region's legacy scripted runners.

The legacy tests of ``test_submission_boundaries`` and ``test_submission_tools``
gave the engine a ``CheckedRunner`` around a scripted runner: the script chose
the result, did things while the call was in flight (sent a control and waited
until the owner applied it), and ``CheckedRunner`` sealed any output, checked it
with the producer check and submitted it through the control transport. Here
the Sim's model double answers at the worker's spawn seam, so the runner, the
worker, the collector and the transport are the product's:

- ``submitted(value, extensions=None)``: ``value`` as the output (a callable
  ``value(context)`` makes it from the call's input); candidates are bound, the
  response is sealed unless it declares its bundles, and the model submits it
  with the workspace tool, whatever the receipt (the legacy ``CheckedRunner``).
  ``extensions``, when given, is written to ``activity-extensions.json`` first
  (a callable makes it from the input too).
- ``failed(error)``: the provider CLI exits with an error and writes no final
  message (a legacy runner's ``{"status": "failed", ...}``).
- ``SubmissionModel.before(role, hook)`` and ``after(role, hook)`` run
  ``hook(context, workspace)`` inside each call of ``role``: before the model
  answers, or after its answer was submitted and received its final receipt
  (or, for an answer made without the tool, after the answer), before the CLI
  exits. ``calls`` records ``role``, ``action`` and ``execution_id`` of each call.
- ``applied_now(sim, action, **options)``: from inside a call, a public control
  the owner applied: the call hands the turn to the owner until the request is
  in ``processed_controls`` (the legacy ``research_fixtures.await_control``).
- ``submission_model(sim, responder=None)`` gives ``sim`` a ``SubmissionModel``
  and returns it; ``on(...).reply(...)`` takes these answers and ``support.model``'s.
- ``configured_sim(**config)``: a restored copy of a template built once per
  process through the public activation with ``config`` (the legacy tests
  started from the synthetic active state built with that configuration; a
  later ``configure`` control would make new profile editions instead).
"""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path

from support.model import Answer, FakeCLI, MARKER, ModelDouble, default


class Submitted(Answer):
    def __init__(self, value, extensions):
        super().__init__(lambda out, ctx: deepcopy(value(ctx) if callable(value) else value))
        self.extensions = extensions


class Failed(Answer):
    def __init__(self, error):
        super().__init__(lambda out, ctx: None, sealed=False)
        self.error = error


def submitted(value, extensions=None):
    return Submitted(value, extensions)


def failed(error):
    return Failed(error)


class _Failure(Exception):
    pass


class SubmissionCLI(FakeCLI):
    def communicate(self, input=None, timeout=None):
        from runner_fixtures import context_from
        prompt = input.decode('utf-8')
        role = prompt.split(MARKER, 1)[1].split('.', 1)[0]
        ctx = context_from(prompt, self.workspace)
        self.model.calls.append({'role': role, 'action': ctx.get('action', {}), 'execution_id': ctx.get('execution_id')})
        for hook in self.model.hooks('before', role):
            hook(ctx, self.workspace)
        try:
            out = self.model.output(role, ctx, self.workspace)
        except _Failure:
            self.returncode = 1
            return None, None
        final = self._submit(out) if (self.workspace / 'input' / 'submission' / 'context.json').is_file() \
            else json.dumps(out, ensure_ascii=False)
        for hook in self.model.hooks('after', role):
            hook(ctx, self.workspace)
        self._write_stream(final)
        self.returncode = 0
        return None, None


class SubmissionModel(ModelDouble):
    def __init__(self, clock, responder=None):
        super().__init__(clock, responder)
        self._hooks = []

    def before(self, role, hook):
        self._hooks.append(('before', role, hook))
        return self

    def after(self, role, hook):
        self._hooks.append(('after', role, hook))
        return self

    def hooks(self, when, role):
        return [hook for moment, hook_role, hook in self._hooks if moment == when and hook_role == role]

    def spawn(self, command, *, stdin=None, stdout=None, stderr=None, cwd=None, env=None, shell=False,
              creationflags=0):
        return SubmissionCLI(self, list(command), stdout, stderr, Path(cwd))

    def output(self, role, ctx, workspace):
        from research_fixtures import bind_candidates, seal_response
        rule = next((rule for rule in self.rules if rule.answers and rule.matches(role, ctx)), None)
        answer = rule.next() if rule else default()
        if isinstance(answer, Failed):
            raise _Failure(answer.error)
        if isinstance(answer, Submitted):
            out = answer.make(None, ctx)
            extensions = answer.extensions(ctx) if callable(answer.extensions) else answer.extensions
            if extensions is not None:
                (Path(workspace) / 'activity-extensions.json').write_text(json.dumps(extensions), encoding='utf-8')
            bind_candidates(out, ctx)
            if 'integration_bundles' not in out:
                seal_response(out, ctx, workspace)
            return out
        return super().output(role, ctx, workspace)


def submission_model(sim, responder=None):
    sim.model = SubmissionModel(sim.clock, responder)
    return sim.model


def configured_sim(**config):
    from support.sim import Sim, built
    return built('submission-configured-' + repr(sorted(config.items())),
                 lambda root, shared: Sim.activated(root, shared=shared, config=config))


def applied_now(sim, action, **options):
    """A public control sent from inside a call and applied by the owner before the call goes on."""
    from support.fakes.calls import owner_turn
    request = sim.control(action, **options)
    for _ in range(100):
        if request['request_id'] in sim.engine.runtime.get('processed_controls', []):
            return request
        owner_turn()
    raise AssertionError('the owner did not apply control ' + request['request_id'] + ' in 100 passes')
