"""Formal scenes on real storage, replacing test_formal_engine's engine doubles.

``scene`` replaces ``engine_fixtures.formal_check_engine``: public activation,
the product candidate producer, and a queued central check. ``parked`` replaces
``test_formal_engine.parked_formal_check`` without environment/authority/save
patches. ``owner_calls`` ports ``state_fixtures.owner_calls`` to the deterministic
calls port, with a bounded drain. ``stop_with_control`` holds the Lean *spawn
double* inside the real worker, then applies a checked public control. No engine
method, verifier or repository is replaced.
"""
from contextlib import contextmanager
from copy import deepcopy
import sys
from support.monitoring_slots import reserve_tool

from do_math import knowledge_records
from support.engine_lifecycle import applied, clear_work
from support.fakes.jobs import job_turn
from support.sim import Sim, built, warm_template

SOURCE = '-- e\N{COMBINING ACUTE ACCENT}\r\ntheorem t : True := by trivial'


def python_sim():
    return built('knowledge:formal-python-command', lambda root, shared:
        Sim.activated(root, shared=shared, config={'lean_command': [sys.executable]}))


def warm_scenes():
    warm_template()
    python_sim()


def scene(*, source='theorem k1 : 1 = 1 := rfl', declarations=('k1',), python_command=False):
    sim = python_sim() if python_command else Sim.activated()
    for text, name, signature, type_ in ((
            'theorem k1 : 1 = 1 := rfl', 'k1', 'k1 : 1 = 1', '1 = 1'),
            (SOURCE, 't', 't : True', 'True')):
        sim.lean.allow(text, [name], signatures={name: signature},
                       declaration_evidence={name: {'type': type_, 'value': None}},
                       axioms={name: []}, dependencies={name: {}})
    clear_work(sim)
    engine = sim.engine
    engine.instance, _ = knowledge_records.create_candidate(engine.instance, {
        'id': 'K1', 'kind': 'lemma', 'title': 'Formal fixture', 'statement': 'One equals one',
        'summary': 'Reflexivity', 'explanation': 'Synthetic formal test input',
        'lean_code': source, 'declaration_names': list(declarations), 'dependencies': []},
        source_ref=engine.instance['lifecycle']['input_id'],
        actor_ref=next(iter(engine.runtime['executions'])), clock=sim.ports.clock)
    engine._enqueue('formal_check', 'K1')
    engine._save()
    return sim, next(a for a in sim.runtime['queue'] if a['role'] == 'formal_check')


@contextmanager
def owner_calls(sim):
    engine = sim.engine
    calls = engine._calls = sim.ports.calls.new(on_returned=engine._local_call_returned,
                                               on_observation_error=engine._observation_failed)
    try:
        yield calls
        for _ in range(100):
            if not calls.futures:
                break
            calls.wait(0.05)
            calls.pump()
            if engine._transport is not None:
                engine._transport.pump(engine._publish_control_request)
            calls.collect()
        else:
            raise AssertionError('formal calculation did not settle in 100 owner turns')
    finally:
        calls.close()
        engine._calls = None


def run_formal(sim, action):
    with owner_calls(sim):
        sim.engine._formal(action)


def stop_with_control(sim, action, operation, **options):
    """Start the real verifier and worker, then stop its live Job by public control."""
    original = sim.lean.spawn
    started = []

    def spawn(command, **options):
        process = original(command, **options)

        def wait(timeout=None):
            started.append(list(command))
            for _ in range(100):
                job_turn()
            raise AssertionError('public control did not terminate the Lean Job')
        process.wait = wait
        return process

    sim.jobs.live = True
    sim.lean.spawn = spawn
    try:
        with owner_calls(sim) as calls:
            sim.engine._formal(action)
            calls.wait(0.05)
            if len(started) != 1:
                raise AssertionError(f'expected one running compiler before control: {started!r}')
            options.setdefault('config', {})
            applied(sim, operation, **options)
            calls.judge()
    finally:
        sim.lean.spawn = original
        sim.jobs.live = False
    return started


def attempts(sim):
    return [e for e in sim.runtime['executions'].values() if e['role'] == 'formal_check']


class ReturnedValues:
    """Copy a lower product function's results as it returns, before its caller can change them."""
    def __init__(self, function):
        self.code, self.values = function.__code__, []

    def __enter__(self):
        monitoring = sys.monitoring
        self.tool = reserve_tool('knowledge verifier returns')

        def returned(code, offset, value):
            self.values.append(deepcopy(value))
        monitoring.register_callback(self.tool, monitoring.events.PY_RETURN, returned)
        monitoring.set_local_events(self.tool, self.code, monitoring.events.PY_RETURN)
        return self

    def __exit__(self, *exception):
        monitoring = sys.monitoring
        monitoring.set_local_events(self.tool, self.code, monitoring.events.NO_EVENTS)
        monitoring.register_callback(self.tool, monitoring.events.PY_RETURN, None)
        monitoring.free_tool_id(self.tool)
        return False


def parked():
    sim, action = scene(source='theorem t : True := by trivial', declarations=('t',))
    environment = deepcopy(sim.engine._formal_environment())
    binding = deepcopy(sim.runtime['trust_bindings'][environment['id']])
    sim.instance['active_trust_environment'] = None
    sim.instance['trust_environments'] = {}
    sim.instance['sources'] = []
    sim.runtime['trust_bindings'] = {}
    sim.runtime['trust_transitions'] = {}
    before = set(sim.runtime['activities'])
    sim.engine._formal(action)
    activity, = set(sim.runtime['activities']) - before
    return sim, action, environment, binding, activity
