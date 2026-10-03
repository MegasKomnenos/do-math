"""Opt-in live CLI scenes; the existing model, Jobs and calls defaults are unchanged.

The hook runs at the provider spawn boundary, before submitting the sealed answer.
It may emit raw events and yield the live Job while the real runner polls it.
Returning False simulates a failed external CLI, through the real worker.
"""
import json
from pathlib import Path

from support.default_responder import context_from
from support.fakes.jobs import job_turn
from support.model import FakeCLI


def install(sim, hook):
    class CLI(FakeCLI):
        def event(self, event):
            self.stdout.write(json.dumps(event).encode() + b'\n')
            self.stdout.flush()
            job_turn()

        def until(self, predicate, message, limit=200):
            for _ in range(limit):
                if predicate():
                    return
                sim.clock.advance(.25)
                job_turn()
            raise AssertionError(message)

        def communicate(self, input=None, timeout=None):
            context = context_from(input.decode('utf-8'), self.workspace)
            role = context['action']['role']
            out, answer = self.model.output(role, context, self.workspace)
            self.model.calls.append({'role': role, 'action': context['action'], 'output': out})
            if hook(self, context) is False:
                self.stderr.write(b'fixture interruption')
                self.stderr.flush()
                self.returncode = 1
                return None, None
            self.finish(out, answer)
            return None, None

        def submission_turn(self):
            # A live Job yields to its runner: directly yielding to the owner
            # while it waits in Job.inspect would deadlock.
            job_turn()

    def spawn(command, *, stdin=None, stdout=None, stderr=None, cwd=None, env=None,
              shell=False, creationflags=0):
        return CLI(sim.model, list(command), stdout, stderr, Path(cwd))

    sim.jobs.live = True
    sim.model.spawn = spawn


def execution(sim, workspace):
    return sim.runtime['executions'][workspace.parent.name]
