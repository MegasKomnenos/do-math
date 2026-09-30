"""The model double at the workers' spawn seam (설계 4.2): a provider CLI that answers from the actual role input.

A worker starts its provider CLI with ``spawn`` (``subprocess.Popen``'s
shape); ``ModelDouble.spawn`` returns a process whose ``communicate`` reads
the prompt, picks the answer, and does what a model does in its workspace: a
bound role writes its draft and submits it with the real workspace submission
tool, handing the turn to the owner (``owner_turn``) until the central receipt
is final. It then writes the provider's event stream and final message.

Answers: ``on(role, **conditions)`` adds a rule matching the role and
action (or context) fields, and ``reply(answer)`` queues one answer for it;
queued answers are used in order and a rule's last answer stays. ``raw(value)``
replaces the output; further builders join as tests need them. A call no rule
matches gets the default responder's smallest valid answer
(``runner_fixtures.ScriptedRunner.respond``). The double never validates an
answer against the output schema: the engine's receiving checks do.
"""
from __future__ import annotations

import json
from pathlib import Path

from support.fakes.calls import owner_turn
from support.fakes.jobs import job_turn

MARKER = "You are the do-math role: "


class Answer:
    """How one call's output is made from the default response and the input context.

    ``after_binding(output, context)``, when given, changes a sealed answer after
    candidate binding and before the integration seal.
    """

    def __init__(self, make, *, sealed=True, after_binding=None):
        self.make, self.sealed, self.after_binding = make, sealed, after_binding


def default():
    return Answer(lambda out, ctx: out)


def raw(value):
    """Exactly ``value`` as the output, without candidate binding or the integration seal."""
    return Answer(lambda out, ctx: value, sealed=False)


def amend(**fields):
    """The default response with ``fields`` set, then bound and sealed like any default answer."""
    return Answer(lambda out, ctx: {**out, **fields})


def rebound(change):
    """The default response, bound like any default answer, then ``change(output, context)`` before the seal."""
    return Answer(lambda out, ctx: out, after_binding=change)


class Rule:
    def __init__(self, role, conditions):
        self.role, self.conditions, self.answers, self.used = role, conditions, [], 0

    def matches(self, role, ctx):
        if role != self.role:
            return False
        action = ctx.get("action", {})
        return all(action.get(key) == value or ctx.get(key) == value for key, value in self.conditions.items())

    def reply(self, answer):
        self.answers.append(answer)
        return self

    def next(self):
        answer = self.answers[min(self.used, len(self.answers) - 1)]
        self.used += 1
        return answer


class ModelDouble:
    def __init__(self, clock, responder=None):
        from runner_fixtures import ScriptedRunner
        self.clock, self.rules, self.calls = clock, [], []
        self.responder = responder or ScriptedRunner()

    def on(self, role, **conditions):
        rule = Rule(role, conditions)
        self.rules.append(rule)
        return rule

    def spawn(self, command, *, stdin=None, stdout=None, stderr=None, cwd=None, env=None, shell=False,
              creationflags=0):
        return FakeCLI(self, list(command), stdout, stderr, Path(cwd))

    def output(self, role, ctx, workspace):
        from research_fixtures import bind_candidates, seal_response
        rule = next((rule for rule in self.rules if rule.answers and rule.matches(role, ctx)), None)
        answer = rule.next() if rule else default()
        out = answer.make(self.responder.respond(role, ctx, workspace), ctx)
        if answer.sealed:
            bind_candidates(out, ctx)
            if answer.after_binding is not None:
                answer.after_binding(out, ctx)
            seal_response(out, ctx, workspace)
        return out


class FakeCLI:
    """One provider CLI process: ``communicate`` runs the whole call."""

    def __init__(self, model, command, stdout, stderr, workspace):
        self.model, self.command, self.stdout, self.stderr, self.workspace = model, command, stdout, stderr, workspace
        self.returncode = None

    def communicate(self, input=None, timeout=None):
        from runner_fixtures import context_from
        prompt = input.decode("utf-8")
        role = prompt.split(MARKER, 1)[1].split(".", 1)[0]
        ctx = context_from(prompt, self.workspace)
        out = self.model.output(role, ctx, self.workspace)
        self.model.calls.append({"role": role, "action": ctx.get("action", {}), "output": out})
        final = self._submit(out) if (self.workspace / "input" / "submission" / "context.json").is_file() \
            else json.dumps(out, ensure_ascii=False)
        self._write_stream(final)
        self.returncode = 0
        return None, None

    def _submit(self, out):
        """A bound role's draft goes through the workspace submission tool; wait for the final receipt."""
        from do_math.canonical import canonical_json
        from do_math.control_protocol import SUBMIT_INTENT
        from do_math.control_server import wait_receipt
        from do_math.control_transport import FINAL_RECEIPTS
        from do_math.submission_tool import request_control
        (self.workspace / "output.json").write_bytes(canonical_json(out))
        delivery = request_control(self.workspace, "output.json", kind=SUBMIT_INTENT, wait_seconds=0,
                                   clock=self.model.clock)
        binding = json.loads((self.workspace / "input" / "submission" / "context.json").read_bytes())["control_binding"]
        for _ in range(100):
            receipt = wait_receipt(binding, delivery["request_id"], 0)
            if receipt and receipt.get("state") in FINAL_RECEIPTS:
                return json.dumps({"submission": delivery["request_id"], "receipt": receipt["state"]})
            owner_turn()
        raise AssertionError("the owner did not receipt submission " + delivery["request_id"] + " in 100 passes")

    def _write_stream(self, final):
        """Write the stream a row at a time; a live Job (``support.fakes.jobs``) lets its runner observe each row."""
        if Path(self.command[0]).stem.lower() != "codex":
            raise NotImplementedError("the model double writes only the Codex event stream: " + self.command[0])
        for row in codex_stream_bytes(final).splitlines(keepends=True):
            self.stdout.write(row)
            self.stdout.flush()
            job_turn()
        final_path = self.command[self.command.index("--output-last-message") + 1]
        Path(final_path).write_bytes(final.encode("utf-8"))

    def kill(self):
        self.returncode = 1


def codex_stream_bytes(final):
    """A completed ``codex exec --json`` stream whose last agent message is ``final``."""
    events = [{"type": "thread.started", "thread_id": "fake-thread"}, {"type": "turn.started"},
              {"type": "item.completed", "item": {"id": "item_0", "type": "agent_message", "text": final}},
              # The usage row carries the fields a recorded Codex stream reports (corpus).
              {"type": "turn.completed", "usage": {"input_tokens": 1, "cached_input_tokens": 0,
                                                   "cache_write_input_tokens": 0, "output_tokens": 1,
                                                   "reasoning_output_tokens": 0}}]
    return "".join(json.dumps(event) + "\n" for event in events).encode("utf-8")
