"""The model double for Claude-configured Sims: the same answers as ``support.model``, written as Claude print streams.

``support.model.ModelDouble`` answers every role from its actual input but
writes only the Codex event stream. ``ClaudeModelDouble`` keeps its rules,
default responder and submission path and writes a Claude stream instead: an
init event and a success result whose output is the structured final (when the
worker passed ``--json-schema``) or the result text (a bound role's submission
receipt). Put it on a Sim with ``sim.model = ClaudeModelDouble(sim.clock)``;
the Sim's worker programs read ``sim.model`` at each call.

``limit(role, times=1)`` makes the next calls of ``role`` end as a native
admission rejection: the CLI leaves ``partial.txt`` in its workspace, reports a
rejected ``rate_limit_event`` and a failed result, and exits 1, as a Claude CLI
over its usage limit does. The collector classifies that stream as a provider
limit (``claude_stream.provider_limit``). ``contexts`` lists every call's input
context in order.
"""
import json

from support.model import MARKER, FakeCLI, ModelDouble

SESSION = "claude-double-session"
INIT = {"type": "system", "subtype": "init", "session_id": SESSION}
USAGE = {"input_tokens": 1, "output_tokens": 1}
REJECTED = {"type": "rate_limit_event", "session_id": SESSION,
            "rate_limit_info": {"status": "rejected", "rateLimitType": "five_hour"}}
FAILED = {"type": "result", "subtype": "error_during_execution", "is_error": True, "session_id": SESSION,
          "usage": USAGE}


def _rows(*events):
    return b"".join(json.dumps(event, ensure_ascii=False).encode("utf-8") + b"\n" for event in events)


class ClaudeModelDouble(ModelDouble):
    def __init__(self, clock, responder=None):
        super().__init__(clock, responder)
        self.limits, self.contexts = {}, []

    def limit(self, role, times=1):
        self.limits[role] = self.limits.get(role, 0) + times
        return self

    def spawn(self, command, *, stdin=None, stdout=None, stderr=None, cwd=None, env=None, shell=False,
              creationflags=0):
        from pathlib import Path
        return ClaudeCLI(self, list(command), stdout, stderr, Path(cwd))


class ClaudeCLI(FakeCLI):
    def communicate(self, input=None, timeout=None):
        from support.default_responder import context_from
        prompt = input.decode("utf-8")
        role = prompt.split(MARKER, 1)[1].split(".", 1)[0]
        self.model.contexts.append(context_from(prompt, self.workspace))
        if self.model.limits.get(role):
            self.model.limits[role] -= 1
            (self.workspace / "partial.txt").write_text("retained evidence", encoding="utf-8")
            self.stdout.write(_rows(REJECTED, INIT, FAILED))
            self.returncode = 1
            return None, None
        return super().communicate(input, timeout)

    def _write_stream(self, final):
        if "--print" not in self.command:
            raise NotImplementedError("the Claude model double answers only Claude print commands: " + self.command[0])
        output = ({"structured_output": json.loads(final)} if "--json-schema" in self.command
                  else {"result": final})
        self.stdout.write(_rows(INIT, {"type": "result", "subtype": "success", "is_error": False,
                                       "session_id": SESSION, "usage": USAGE, **output}))
