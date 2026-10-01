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
            out = self.model.output(role, context, self.workspace)
            self.model.calls.append({'role': role, 'action': context['action'], 'output': out})
            if hook(self, context) is False:
                self.stderr.write(b'fixture interruption')
                self.stderr.flush()
                self.returncode = 1
                return None, None
            final = self._submit(out) if (self.workspace / 'input/submission/context.json').is_file() else json.dumps(out)
            self._write_stream(final)
            self.returncode = 0
            return None, None

        def _submit(self, out):
            # A live Job must yield to its runner, even if the owner probes the Job
            # while applying an observation. Yielding directly to the owner there
            # deadlocks: the owner is waiting in Job.inspect for this worker.
            from do_math.canonical import canonical_json
            from do_math.control_protocol import SUBMIT_INTENT
            from do_math.control_server import wait_receipt
            from do_math.control_transport import FINAL_RECEIPTS
            from do_math.submission_tool import request_control
            (self.workspace / 'output.json').write_bytes(canonical_json(out))
            delivery = request_control(self.workspace, 'output.json', kind=SUBMIT_INTENT,
                                       wait_seconds=0, clock=self.model.clock)
            binding = json.loads((self.workspace / 'input/submission/context.json').read_bytes())['control_binding']
            for _ in range(100):
                receipt = wait_receipt(binding, delivery['request_id'], 0, clock=sim.ports.clock)
                if receipt and receipt.get('state') in FINAL_RECEIPTS:
                    return json.dumps({'submission': delivery['request_id'], 'receipt': receipt['state']})
                job_turn()
            raise AssertionError('the owner did not receipt live submission ' + delivery['request_id'])

    def spawn(command, *, stdin=None, stdout=None, stderr=None, cwd=None, env=None,
              shell=False, creationflags=0):
        return CLI(sim.model, list(command), stdout, stderr, Path(cwd))

    sim.jobs.live = True
    sim.model.spawn = spawn


def execution(sim, workspace):
    return sim.runtime['executions'][workspace.parent.name]
