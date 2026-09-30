"""Lifecycle helpers of the engine region on the Sim: controls, grants, tasks, theorems, trust and HTTP effects.

They replace the in-memory ``engine_fixtures.FakeEngine`` helpers with the
same steps on a Sim's real engine and storage, so every save passes the
storage contract; nothing here replaces an engine method or the store.

Controls and owner steps:
- ``applied(sim, action, **options)`` sends a public control and has the owner
  apply it; a rejected control fails at once (preserved rule K-35).
  ``extended(engine, action, config)`` applies one control directly, as the
  owner does for a queued request, and raises its rejection.
- ``run_machine(sim, role)`` starts the first queued machine action as the owner
  does and finishes its calculation on the calls port; ``only`` keeps the queued
  actions of some roles; ``clear_work`` publishes an empty queue.
- ``control_at_inbox_check(sim, n, action, ...)`` writes a public control as the
  owner reads its inbox for the n-th time (an audit event of that listing), and
  ``file_access(directory)`` records what the process opens or lists there.
- ``ObservedCalls(name=code, ...)`` records every start of those code objects
  with a copy of its arguments (``sys.monitoring``; ``code_of`` and
  ``artifact_reader_code`` name the code); ``ticking_clock(sim)`` makes every
  wall-clock read move the Sim clock, so no two time samples are equal.

Start states and records:
- ``lifecycle_sim()`` restores an active instance adopting explicit HTTP grants
  with two reviewed theorems ``k1`` and ``k2`` and a second toolchain
  (``prepared_environment``) already configured; ``external_sim()`` is the same
  activation without knowledge. Both are templates built once per process.
- ``grant``, ``task``, ``approve`` and ``queue_work`` add a grant by decision, a
  task a returned preparation produced, its sealed contract review, and the
  research work the planner queues for it.
- ``theorems(sim, *names)`` imports formal candidates by control and runs the
  owner until the Lean double verified them and their identity reviews ended;
  ``solve_goal`` records satisfied goal audits through the receiver;
  ``invalidate`` is the user's invalidation of a record.
- ``next_environment(sim, name)`` registers a new synthetic toolchain whose
  command is its own Lean and configures that command by control, as a user
  moving to another toolchain does; ``transition`` requests the move.
- ``failing_lean(sim)`` makes every later Lean check exit with an error;
  ``recorded_verifier(sim)`` rebuilds the engine with a formal verifier that
  records its arguments and runs the product's own ``verify_lean``.
- ``http_grant`` decides an HTTP grant and returns its prepare config;
  ``http_fails`` makes the HTTP port fake record each request and then raise.
"""
from __future__ import annotations

from contextlib import contextmanager
from copy import deepcopy
from datetime import timedelta
import inspect
import os
from pathlib import Path
import sys

from do_math.engine import ResearchEngine
from do_math.governance import OPERATING_ROLES, TASK_WORK_ROLES
from support.sim import Sim, built

THEOREMS = ('k1', 'k2')
NEXT = 'next'  # the directory of the second toolchain the lifecycle template registers
ASSESSMENT = {'difficulty': 'low', 'importance': 'low', 'reason': 'Bounded fixture'}


def applied(sim, action, **options):
    """A public control the owner applied; a rejected one fails with its reason."""
    options.setdefault('text', 'lifecycle test control: ' + action)
    request = sim.control(action, **options)
    sim.engine.process_controls()
    result = sim.engine.control_result(request['request_id'])
    if result.get('effect') == 'rejected':
        raise AssertionError(f'control {action} was rejected: {result.get("reason")}')
    return request


def extended(engine, action, config, request_id=None):
    """Apply one control the way the owner applies a queued request; its rejection raises."""
    return engine._apply_extended_control({'id': request_id or 'UI-' + str(len(engine.runtime['extended_controls'])),
                                           'action': action, 'config': config})


def grant(engine, identifier, *, initial=False, spec=None, request_id=None):
    """A grant decision: ``spec`` as given, else a local grant for one day (initial: intent interpretation)."""
    spec = spec or {'kind': 'local', 'roles': ['intent_interpretation'] if initial else sorted(TASK_WORK_ROLES | OPERATING_ROLES),
                    'reuse': 'reusable', 'expires_at': (engine.ports.clock.wall() + timedelta(days=1)).isoformat()}
    return extended(engine, 'decision', {'change': {'kind': 'grant', 'grant': {'id': identifier, **spec}}}, request_id)


def research_grant(engine):
    return engine.instance['lifecycle']['adoption']['research_grant_ids'][0]


def _ended_execution(engine, identifier, role):
    """A returned execution a record names (its producer or reviewer); registered once."""
    from do_math.execution_lifecycle import transition_execution
    if identifier in engine.runtime['executions']:
        return
    execution = engine._register_execution({'id': 'AC-' + identifier, 'role': role},
                                           {'id': identifier, 'role': role, 'status': 'running'})
    at = engine._lifecycle_now().isoformat()
    transition_execution(execution, 'stopping', at=at)
    transition_execution(execution, 'ended', at=at, outcome='execution_incomplete')


def task(engine, task_id='TK-one', *, approved=True, condition=None, inputs=None):
    """A planned task a returned preparation produced, under the adopted research grant, with its assessment and rules.

    ``approved`` seals an approving contract review by a returned reviewer.
    The shape is ``engine_fixtures.evidence_task``. Unlike the in-memory
    ``FakeEngine.task`` it names executions the instance holds and carries the
    model assessment and observation rules the product requires before a
    contract review (``FakeEngine`` returned no missing assessment).
    """
    from engine_fixtures import evidence_task
    from research_fixtures import prepared_rule_conditions
    _ended_execution(engine, 'EX-preparation', 'research_preparation')
    row = evidence_task(task_id)
    row.update(inputs=list(inputs or []), authority_refs=[research_grant(engine)],
               occurrence_condition=condition or {'op': 'always'}, model_assessment=dict(ASSESSMENT),
               initial_observation_rules=prepared_rule_conditions([task_id])[0]['observation_rules'],
               # the adopted editions; the registry also keeps editions a later configuration replaced
               profile_refs=deepcopy(engine.instance['role_profile_refs']['research_work']
                                     + engine.instance['role_profile_refs']['supplemental_research']))
    engine.runtime['tasks'][task_id] = row
    if approved:
        approve(engine, row)
    return row


def approve(engine, row, decision='approved'):
    """Seal one contract review of ``row`` with ``decision`` by the returned reviewer ``EX-review-<task>``."""
    from do_math import planning
    from research_fixtures import review_items
    reviewer = 'EX-review-' + row['id']
    _ended_execution(engine, reviewer, 'task_contract_review')
    row['reviews'] = [planning.seal_contract_review(row, review_items([row['id']], decision=decision), engine.instance,
                                                    engine.runtime, execution_id=reviewer)]


def queue_work(engine, task_id):
    """The research work on ``task_id`` the planner queues, with its model assessment."""
    engine._enqueue('research_work', task_id, reason='Work on the reviewed task', model_assessment=dict(ASSESSMENT))
    return next(row for row in engine.runtime['queue'] if row['role'] == 'research_work' and row['target'] == task_id)


def clear_work(sim):
    """Publish the instance without queued actions or pending events, as a test's start."""
    sim.engine.runtime['queue'].clear()
    sim.engine.runtime['pending_events'].clear()
    sim.engine._save()


def theorems(sim, *names):
    """Theorem candidates ``name : 1 = 1`` imported by control, verified by the Lean double and identity-reviewed.

    The owner runs the product's formal check and identity review (model double)
    until every review cycle ended; the research work those passes queued is
    dropped. Returns the knowledge IDs in the order of ``names``.
    """
    engine = sim.engine
    clear_work(sim)
    for name in names:
        applied(sim, 'knowledge', config={'operation': 'import', 'candidate': {
            'kind': 'theorem', 'title': name, 'statement': 'One equals one (' + name + ')', 'summary': 'Reflexivity',
            'explanation': 'By reflexivity.', 'lean_code': f'theorem {name} : 1 = 1 := rfl',
            'declaration_names': [name], 'dependencies': []}})
    kids = [next(k for k, row in sim.instance['knowledge'].items() if row['title'] == name) for name in names]

    def reviewed(s):
        rows = [s.instance['knowledge'][k] for k in kids]
        return all(row.get('review_cycle_id') and s.runtime['review_cycles'][row['review_cycle_id']]['status'] != 'working'
                   for row in rows)
    sim.run_until(reviewed, max_steps=12)
    for kid in kids:
        cycle = sim.runtime['review_cycles'][sim.instance['knowledge'][kid]['review_cycle_id']]
        if cycle.get('decision') != 'match':
            raise AssertionError(f'the identity review of {kid} ended {cycle.get("decision")!r}, not a match')
    clear_work(sim)
    return kids


def solve_goal(engine, kid):
    """Every configured goal auditor returns ``satisfied`` on ``kid``; the engine's receiver records the judgments.

    The auditors' returned executions are registered and bound to the governance
    input they read, as ``engine_fixtures.audit_goal`` does; the goal judgment,
    the goal status and the solution basis are the receiver's.
    """
    basis, required = engine._goal_basis_key(), engine.instance['config']['goal_auditors']
    for slot in range(required):
        eid = f'EX-goal-audit-{slot}'
        _ended_execution(engine, eid, 'goal_audit')
        engine._bind_governance_input({'role': 'goal_audit'}, engine.runtime['executions'][eid],
                                      engine._governance_context({'role': 'goal_audit'}, {}))
        engine._apply({'role': 'goal_audit', 'slot': slot, 'basis': basis, 'required': required},
                      {'decision': 'satisfied', 'scope_complete': True, 'used_sources': [kid],
                       'summary': 'Fixture auditor response for the stated charter', 'questions': []}, eid)


def invalidate(engine, kid, reason):
    """The user's invalidation of ``kid`` with its computed impact declared."""
    from do_math.knowledge import plan_impact
    impact = plan_impact(engine.instance, engine.runtime, [kid], [])
    extended(engine, 'knowledge', {'operation': 'invalidate', 'id': kid, 'reason': reason,
                                   'declared_impact': impact['computed_impact']})


def lean_of(directory):
    return directory / 'toolchain' / 'bin' / 'lean.exe'


def next_environment(sim, name, *, configure=True, base=None):
    """A new synthetic toolchain registered by control; ``configure`` makes its Lean the configured command.

    Returns the environment ID. The toolchain lives in ``(base or sim.root) / name / 'trust'``.
    A template keeps it under ``sim.shared``, which a restore never copies: the
    trust record fingerprints the files' creation times, which a copy changes.
    A test that changes toolchain files registers its own under ``sim.root``.
    """
    from research_fixtures import trust_fixture
    directory = (base or sim.root) / name / 'trust'
    request = trust_fixture(directory.parent, [str(lean_of(directory))], directory=directory)
    applied(sim, 'trust', config=request)
    environment = next(k for k, row in sim.instance['trust_environments'].items() if row['toolchain'] == request['toolchain'])
    if configure:
        applied(sim, 'configure', config={'lean_command': [str(lean_of(directory))]})
    return environment


def transition(sim, environment):
    """Apply the move to ``environment`` as the owner applies the user's control; returns the transition ID."""
    extended(sim.engine, 'trust', {'operation': 'transition', 'env_id': environment})
    return next(reversed(sim.runtime['trust_transitions']))


def run_machine(sim, role):
    """Process the first queued ``role`` machine action and finish its calculation, as the owner does.

    The owner starts the action (its lifecycle gate is the last before start) on
    the calls port, answers the calculation's callbacks, receives transport
    requests, collects it and resumes its continuation (``state_fixtures.owner_calls``).
    Returns the action.
    """
    engine = sim.engine
    action = next(row for row in engine.runtime['queue'] if row['role'] == role)
    calls = engine._calls = sim.ports.calls.new(on_returned=engine._local_call_returned,
                                                on_observation_error=engine._observation_failed)
    try:
        engine._process_machine_action(action)
        while calls.futures:
            calls.wait(0.05)
            calls.pump()
            if engine._transport is not None:
                engine._transport.pump(engine._publish_control_request)
            calls.collect()
    finally:
        calls.close()
        engine._calls = None
    return action


def executions(sim, role):
    return [row for row in sim.runtime['executions'].values() if row.get('role') == role]


def failing_lean(sim, message='fixture: the compiler failed'):
    """Every later Lean check exits with code 1 and ``message`` on its error stream."""
    class Failing:
        def __init__(self, command, stderr):
            self.command, self.stderr, self.returncode = command, stderr, None

        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

        def wait(self, timeout=None):
            sim.lean.checks.append({'declarations': [], 'extract': None, 'failed': message})
            self.stderr.write((message + '\n').encode())
            self.returncode = 1
            return 1

        def kill(self):
            self.returncode = 1
    sim.lean.spawn = lambda command, *, cwd=None, stdout=None, stderr=None, shell=False, creationflags=0: \
        Failing(list(command), stderr)


def recorded_verifier(sim, change=None):
    """Rebuild the engine (a process restart) with a verifier that records each call and runs ``verify_lean``.

    ``change(result)`` may rewrite what the verifier returns. Returns the list of
    recorded argument maps (without the stop and start callbacks).
    """
    from do_math.formal import verify_lean
    calls = []

    def verifier(**arguments):
        calls.append({key: deepcopy(value) for key, value in arguments.items()
                      if key not in ('should_stop', 'on_started', 'clock')})
        result = verify_lean(jobs=sim.ports.jobs, **arguments)
        return change(result) if change else result
    sim.engine = ResearchEngine(sim.repository, sim.instance_id, ports=sim.ports, formal_verifier=verifier)
    return calls


_WATCHES = []
_HOOKED = []


def _normal(path):
    return os.path.normcase(os.path.abspath(path))


def _audit(event, args):
    if not _WATCHES or event not in ('open', 'os.scandir', 'os.listdir') or not args:
        return
    path = args[0]
    if isinstance(path, bytes):
        path = os.fsdecode(path)
    if not isinstance(path, (str, os.PathLike)):
        return  # a file descriptor
    target = _normal(path)
    for root, callback in list(_WATCHES):
        if target == root or target.startswith(root + os.sep):
            callback(event, target)


@contextmanager
def _watching(directory, callback):
    """Call ``callback(event, path)`` for each open or listing under ``directory`` while the block runs.

    An audit hook cannot be removed, so one hook is installed once and serves
    only the blocks that are open; outside them it returns at once.
    """
    if not _HOOKED:
        sys.addaudithook(_audit)
        _HOOKED.append(True)
    watch = (_normal(directory), callback)
    _WATCHES.append(watch)
    try:
        yield
    finally:
        _WATCHES.remove(watch)


def code_of(function):
    """The code object a function, method or closure runs."""
    return inspect.unwrap(getattr(function, '__func__', function)).__code__


class ObservedCalls:
    """Record each start of the given code objects while open, with a copy of its arguments (``sys.monitoring``).

    Nothing is replaced: only these code objects raise start events, so other
    code runs unobserved. ``calls[name]`` lists the argument mappings in call
    order (the same approach as main's ``support/provider_probes.ObservedCalls``).
    """

    def __init__(self, **codes):
        self.names = {code: name for name, code in codes.items()}
        self.calls = {name: [] for name in codes}

    def __enter__(self):
        monitoring = sys.monitoring
        self.tool = next(tool for tool in (3, 4, 0, 2) if monitoring.get_tool(tool) is None)
        monitoring.use_tool_id(self.tool, 'do-math engine observed calls')

        def started(code, offset):
            self.calls[self.names[code]].append(dict(sys._getframe(1).f_locals))
        monitoring.register_callback(self.tool, monitoring.events.PY_START, started)
        for code in self.names:
            monitoring.set_local_events(self.tool, code, monitoring.events.PY_START)
        return self

    def __exit__(self, *exception):
        monitoring = sys.monitoring
        for code in self.names:
            monitoring.set_local_events(self.tool, code, monitoring.events.NO_EVENTS)
        monitoring.register_callback(self.tool, monitoring.events.PY_START, None)
        monitoring.free_tool_id(self.tool)
        return False


def artifact_reader_code():
    """The code of the task-evidence reader every evaluation context carries (``core_engine._evaluation_context_for``)."""
    from do_math import core_engine
    return next(value for value in core_engine._evaluation_context_for.__code__.co_consts
                if getattr(value, 'co_name', None) == 'read_artifact')


def ticking_clock(sim, seconds=0.001):
    """From now on every wall-clock read of the Sim clock first moves both clocks ``seconds`` forward.

    Two time samples are then never equal, as on a real clock, so an assertion
    that two recorded times are equal or ordered can fail.
    """
    clock = sim.clock
    wall = type(clock).wall

    def ticking():
        clock.advance(seconds)
        return wall(clock)
    clock.wall = ticking


@contextmanager
def file_access(directory):
    """Record what the process opens or lists under ``directory`` while the block runs (Python audit events)."""
    seen = []
    with _watching(directory, lambda event, path: seen.append((event, path))):
        yield seen


@contextmanager
def control_at_inbox_check(sim, number, action, **options):
    """Queue the public control ``action`` just as the owner reads its control inbox for the ``number``-th time.

    The owner reads the inbox (``core_engine._inbox``) by listing its folder;
    the control is written in that listing's audit event, before the listing
    runs, so this very read applies it. Yields ``{'checks': reads so far, 'request': the control}``.
    """
    inbox = _normal(Path(sim.instance['workspace']) / 'control' / sim.instance_id)
    state = {'checks': 0, 'request': None, 'busy': False}

    def arrive(event, path):
        if event != 'os.scandir' or path != inbox or state['busy']:
            return
        state['checks'] += 1
        if state['checks'] == number:
            state['busy'] = True  # writing the control may list the folder itself
            try:
                state['request'] = sim.control(action, **{'text': 'arrives at inbox read ' + str(number), **options})
            finally:
                state['busy'] = False
    with _watching(inbox, arrive):
        yield state


def _build_lifecycle(root, shared):
    sim = Sim(root, shared=shared)
    sim.activate(external_policy='explicit_grants')
    theorems(sim, *THEOREMS)
    next_environment(sim, NEXT, base=sim.shared)
    clear_work(sim)
    return sim


def lifecycle_sim():
    """An active instance adopting explicit HTTP grants, with the reviewed theorems ``k1`` and ``k2``.

    A second toolchain (``prepared_environment``) is registered and its Lean is the
    configured command, so the formal and trust profiles already name it; a test
    starts a transition to it. The queue and pending events are empty.
    """
    return built('engine-lifecycle', _build_lifecycle)


def prepared_environment(sim):
    """The environment ``lifecycle_sim`` registered (``NEXT``, under ``shared``) for a transition; never change its files."""
    executable = str(lean_of(sim.shared / NEXT / 'trust'))
    return next(k for k, row in sim.instance['trust_environments'].items() if row['toolchain']['executable'] == executable)


def only(sim, *roles):
    """Keep only the queued actions of ``roles``: other work a control queued is not this test's subject.

    The change is the engine's; save it before an owner pass (``sim.step``), which reloads the published state.
    """
    sim.engine.runtime['queue'][:] = [row for row in sim.engine.runtime['queue'] if row['role'] in roles]


def warm_lifecycle():
    """``setUpModule``: build the lifecycle template before the first test, so no test pays for it."""
    lifecycle_sim()


def _build_external(root, shared):
    sim = Sim(root, shared=shared)
    sim.activate(external_policy='explicit_grants')
    clear_work(sim)
    return sim


def external_sim():
    """An active instance adopting explicit HTTP grants, without knowledge; queue and pending events empty."""
    return built('engine-external', _build_external)


def warm_external():
    external_sim()


ORIGIN = 'http://127.0.0.1:1'


def http_grant(engine, gid='GR-http-audit', *, once=False, credentials=False, scope=None, origin=ORIGIN,
               prefixes=('/effect',)):
    """A decided HTTP grant for POST under ``prefixes``; returns the ``external`` prepare config ``OP-audit`` (not sent)."""
    row = {'id': gid, 'kind': 'http', 'reuse': 'once' if once else 'reusable', 'allowed_origins': [origin],
           'allowed_methods': ['POST'], 'allowed_path_prefixes': list(prefixes)}
    if credentials:
        row['credential_env'] = {'X-Test': CREDENTIAL}
    row.update(scope or {})
    extended(engine, 'decision', {'change': {'kind': 'grant', 'grant': row}})
    return {'operation': 'prepare', 'id': 'OP-audit', 'grant_id': gid,
            'request': {'method': 'POST', 'url': origin + '/effect', 'body': 'test'}}


CREDENTIAL = 'LIFECYCLE_AUDIT_TEST_TOKEN'


def http_fails(sim, error):
    """Every later HTTP request is recorded by the port fake, then raises ``error`` (a transport outcome unknown)."""
    http = sim.ports.http
    record = type(http).request

    def request(request, header, timeout):
        record(http, request, header, timeout)
        raise error
    http.table.setdefault('/effect', (500, b'', None))
    http.request = request
