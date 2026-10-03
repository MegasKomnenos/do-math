"""The model double at the workers' spawn seam (설계 4.2): a provider CLI that answers from the actual role input.

A worker starts its provider CLI with ``spawn`` (``subprocess.Popen``'s
shape); ``ModelDouble.spawn`` returns a process whose ``communicate`` reads
the prompt, picks the answer, and does what a model does in its workspace: a
bound role writes its draft and submits it with the real workspace submission
tool, handing the turn to the owner (``owner_turn``) until the central receipt
is final. It then writes the provider's event stream and final message.

Answers: ``on(role, **conditions)`` adds a rule matching the role and
action (or context) fields, and ``reply(answer)`` queues one answer for it;
queued answers are used in order and a rule's last answer stays. ``raw(value, expected_receipt=...)``
replaces the output; further builders join as tests need them. A call no rule
matches gets the default responder's smallest valid answer
(``support.default_responder.DefaultResponder.respond``). The double never validates an
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
    candidate binding and before the integration seal. Normal answers are bound
    and require an accepted central receipt. Negative samples name their exact
    expected_receipt. Only mode="standalone", expected_receipt=None emits plain
    JSON without submission. returncode declares the provider exit after a
    matching receipt; it never hides an unexpected receipt.
    """

    def __init__(self, make, *, sealed=True, after_binding=None, mode="bound", expected_receipt="accepted",
                 returncode=0):
        from do_math.control_transport import FINAL_RECEIPTS
        if mode not in {"bound", "standalone"}:
            raise ValueError("answer mode must be bound or standalone")
        if (mode == "bound" and expected_receipt not in FINAL_RECEIPTS or
                mode == "standalone" and expected_receipt is not None):
            raise ValueError("bound answers require an exact terminal receipt; standalone answers require None")
        if type(returncode) is not int or returncode not in (0, 1):
            raise ValueError("the provider returncode must be 0 or 1")
        self.make, self.sealed, self.after_binding = make, sealed, after_binding
        self.mode, self.expected_receipt, self.returncode = mode, expected_receipt, returncode


def default(*, expected_receipt="accepted"):
    return Answer(lambda out, ctx: out, expected_receipt=expected_receipt)


def raw(value, *, expected_receipt, mode="bound", returncode=0):
    """Exactly ``value`` as the output, without candidate binding or the integration seal."""
    return Answer(lambda out, ctx: value, sealed=False, mode=mode, expected_receipt=expected_receipt,
                  returncode=returncode)


def amend(*, expected_receipt="accepted", **fields):
    """The default response with ``fields`` set, then bound and sealed like any default answer."""
    return Answer(lambda out, ctx: {**out, **fields}, expected_receipt=expected_receipt)


def rebound(change, *, expected_receipt="accepted"):
    """The default response, bound like any default answer, then ``change(output, context)`` before the seal."""
    return Answer(lambda out, ctx: out, after_binding=change, expected_receipt=expected_receipt)


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
        from support.default_responder import DefaultResponder
        self.clock, self.rules, self.calls, self.receipts = clock, [], [], []
        self.responder = responder or DefaultResponder()

    def on(self, role, **conditions):
        rule = Rule(role, conditions)
        self.rules.append(rule)
        return rule

    def spawn(self, command, *, stdin=None, stdout=None, stderr=None, cwd=None, env=None, shell=False,
              creationflags=0):
        return FakeCLI(self, list(command), stdout, stderr, Path(cwd))

    def output(self, role, ctx, workspace):
        """Return (output, Answer); the same per-call contract travels to the CLI.

        Consumers preparing drafts use the first value. CLI consumers must pass
        both to finish; no shared mutable current-answer state crosses workers.
        """
        rule = next((rule for rule in self.rules if rule.answers and rule.matches(role, ctx)), None)
        answer = rule.next() if rule else default()
        return self.render(answer, role, ctx, workspace), answer

    def render(self, answer, role, ctx, workspace):
        from support.role_answers import bind_candidates, seal_response
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
        from support.default_responder import context_from
        prompt = input.decode("utf-8")
        role = prompt.split(MARKER, 1)[1].split(".", 1)[0]
        ctx = context_from(prompt, self.workspace)
        out, answer = self.model.output(role, ctx, self.workspace)
        self.model.calls.append({"role": role, "action": ctx.get("action", {}), "output": out})
        self.finish(out, answer)
        return None, None

    def finish(self, out, answer, *, before_exit=None):
        """Apply the declared mode, compare the receipt, then emit the provider result."""
        final = (self._submit(out, answer.expected_receipt) if answer.mode == "bound"
                 else json.dumps(out, ensure_ascii=False))
        if before_exit is not None:
            before_exit()
        self.returncode = answer.returncode
        if self.returncode == 0:
            self._write_stream(final)

    def check_receipt(self, receipt, expected_receipt):
        if not receipt or receipt.get("state") != expected_receipt:
            raise AssertionError("expected receipt " + str(expected_receipt) + "; actual " + repr(receipt))

    def receipt_received(self, context, delivery, receipt):
        """Observation hook; the shared sender always enforces the call's expectation."""
        self.model.receipts.append(receipt)

    def submission_turn(self):
        owner_turn()

    def _submit(self, out, expected_receipt):
        """Submit through the actual workspace tool and compare the owner's final receipt."""
        from do_math.canonical import canonical_json
        from do_math.control_protocol import SUBMIT_INTENT
        from do_math.control_server import wait_receipt
        from do_math.control_transport import FINAL_RECEIPTS
        from do_math.submission_tool import request_control
        try:
            context = json.loads((self.workspace / "input" / "submission" / "context.json").read_bytes())
            binding = context["control_binding"]
            if not isinstance(binding, dict) or not binding:
                raise ValueError("empty control binding")
        except (OSError, ValueError, KeyError, TypeError) as error:
            raise AssertionError("normal bound response requires control binding") from error
        (self.workspace / "output.json").write_bytes(canonical_json(out))
        delivery = request_control(self.workspace, "output.json", kind=SUBMIT_INTENT, wait_seconds=0,
                                   clock=self.model.clock)
        for _ in range(100):
            receipt = (delivery if delivery.get("state") in FINAL_RECEIPTS else
                       wait_receipt(binding, delivery["request_id"], 0, clock=self.model.clock))
            if receipt and receipt.get("state") in FINAL_RECEIPTS:
                self.receipt_received(context, delivery, receipt)
                self.check_receipt(receipt, expected_receipt)
                return json.dumps({"submission": delivery["request_id"], "receipt": receipt["state"]})
            self.submission_turn()
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
