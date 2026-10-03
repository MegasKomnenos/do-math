"""Control helpers of the engine region: a running research call on a Sim, its worker's requests, and transport races.

- ``running_work(sim, rules=None)``: the research work of one reviewed task,
  started as the scheduler starts it. ``_call_steps`` prepares the call (the
  product fixes its grant, input bundle, control binding and observation
  tracker), the Jobs fake launches a Job that only waits, and the runner's
  start callback records its process, which moves the execution to
  ``running``. The block holds the call running and yields ``Call``. ``rules``
  replaces the task's initial observation rules before its contract review.
- ``Call.observe(*events)`` hands the owner the runner's next observation batch
  through the call's own callback (``on_observation``), as a runner does.
- ``Call.draft(kind)`` writes the model's answer (the Sim model double, from the
  call's actual prompt) to ``output.json`` and delivers it with the workspace
  submission tool; ``Call.submit(kind, payload, request_id)`` and
  ``Call.self_check(obligation_id, response)`` deliver the worker's other
  requests. ``Call.receive()`` is the owner's inbox pass that pumps the
  transport into ``_publish_control_request``; ``Call.receipt(request_id)`` is
  what the worker reads back.
- ``held_ref(sim)``: another writer holds the instance ref's lock while the
  block runs, so the next publication fails its compare-and-swap.
- ``on_audit(event, callback)``: while the block runs, ``callback(arguments)``
  is called in the raising thread for every ``event`` audit event
  (``sys.audit``). A test uses it to hold a thread at an exact point of a
  product call, such as ``os.link`` publishing a transport file, without
  replacing a product function. Python cannot remove an audit hook, so one
  hook is installed for the process and does nothing outside a block.
"""
from contextlib import contextmanager
from pathlib import Path
import sys

_CALLBACKS = []
_HOOK = []
WAIT = 'fixture: a research call that only waits'


def _hook(event, arguments):
    for name, callback in list(_CALLBACKS):
        if name == event:
            callback(arguments)


@contextmanager
def on_audit(event, callback):
    """Call ``callback(arguments)`` for each ``event`` audit event raised while the block runs."""
    if not _HOOK:
        sys.addaudithook(_hook)
        _HOOK.append(_hook)
    entry = (event, callback)
    _CALLBACKS.append(entry)
    try:
        yield
    finally:
        _CALLBACKS.remove(entry)


@contextmanager
def held_ref(sim):
    """Another writer holds the instance ref's lock file, as a concurrent Git ref transaction does."""
    path = sim.repository / '.git' / 'refs' / 'heads' / 'do-math' / (sim.instance_id + '.lock')
    path.write_bytes(b'')
    try:
        yield path
    finally:
        path.unlink()


class Call:
    """One running research call: the arguments the scheduler hands its runner, and its worker's actions."""

    def __init__(self, sim, arguments):
        self.sim, self.arguments = sim, arguments
        self.engine = sim.engine
        self.execution_id = arguments['execution_id']
        self.binding = arguments['control_binding']
        self.workspace = Path(arguments['workspace'])
        self.stream = Path(arguments['evidence_dir']) / 'stdout.jsonl'

    @property
    def tracker(self):
        return self.engine._trackers[self.execution_id]

    @property
    def execution(self):
        return self.engine.runtime['executions'][self.execution_id]

    def observe(self, *events):
        from support.provider_live import batch
        source = self.tracker.observation_source
        start = source['end_offset'] if source is not None else 0
        self.arguments['on_observation'](batch(self.sim, list(events), self.stream, start=start))

    def draft(self, kind='submit_intent'):
        """The model's answer to this call's prompt as the worker's draft, delivered by the workspace tool."""
        from do_math.canonical import canonical_json
        from do_math.submission_tool import request_control
        from support.default_responder import context_from
        context = context_from(self.arguments['prompt'], self.workspace)
        output, contract = self.sim.model.output('research_work', context, self.workspace)
        if (contract.mode, contract.expected_receipt) != ('bound', 'accepted'):
            raise AssertionError('the observed research worker requires a normal bound draft')
        (self.workspace / 'output.json').write_bytes(canonical_json(output))
        return request_control(self.workspace, 'output.json', kind=kind, wait_seconds=0, clock=self.sim.clock)

    def submit(self, kind, payload, request_id):
        from do_math.control_transport import ControlTransport
        return ControlTransport.worker_submit(self.binding, request_id=request_id, kind=kind, payload=payload)

    def self_check(self, obligation_id, response):
        from do_math.control_transport import ControlTransport
        return ControlTransport.worker_self_check(self.binding, self_check_id=obligation_id, response=response)

    def receive(self):
        """The owner's inbox pass: pump the transport into the publication hook, then apply user controls."""
        self.engine._apply_inbox()

    def receipt(self, request_id):
        from do_math.control_transport import ControlTransport
        return ControlTransport.worker_receipt(self.binding, request_id)


@contextmanager
def running_work(sim, *, rules=None):
    """The research work of task ``TK-control`` started as the scheduler starts it; the call stays running."""
    from do_math.windows_job import process_identity
    from support.engine_lifecycle import approve, clear_work, queue_work, task
    engine = sim.engine
    clear_work(sim)
    row = task(engine, 'TK-control', approved=rules is None)
    if rules is not None:
        row['initial_observation_rules'] = rules
        approve(engine, row)
    queue_work(engine, 'TK-control')
    engine._save()
    action = next(row for row in engine.runtime['queue'] if row['role'] == 'research_work')
    sim.jobs.programs.append((lambda argv: argv[2:3] == [WAIT], lambda argv, cwd, env: 0))
    steps = engine._call_steps(action)
    try:
        arguments = next(steps)
    except StopIteration:
        raise AssertionError('the owner did not start the research work: ' + repr(sim.waiting())) from None
    # The Job stays unresumed, so it holds a live process the whole time, as a running call's does.
    job = sim.jobs.launch([sys.executable, '-c', WAIT], cwd=arguments['workspace'],
                          name=arguments['launch_ticket']['job_name'])
    try:
        arguments['on_started']({**process_identity(job), 'job_name': job.name})
        yield Call(sim, arguments)
    finally:
        steps.close()
        job.terminate()
        job.close()
