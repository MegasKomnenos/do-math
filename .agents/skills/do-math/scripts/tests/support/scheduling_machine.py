"""A machine calculation held open beside an AI call on a Sim: scenes, the held Lean check and owner-pass probes.

Moved from ``test_machine_parallel``'s ``Host`` (a ``FakeEngine`` with engine
methods replaced) and its ``run_case``. The engine is the Sim's real engine
with its default formal verifier (``verify_lean`` on the Jobs port), so the
Lean worker Job's start is published by ``formal._job_run`` itself and the
calculation reads its own stop flag. What is held open is the Lean double's
check inside that Job: a real Lean process may take hours, and the double's
``wait`` hands the calculation's turn to the owner meanwhile. Formal and trust
checks both reach it through ``trust_validation.verify_formal``.

- ``formal_scene()``: an active instance with two imported theorem candidates;
  its queue is the first candidate's formal check, a maintenance request, and
  the second candidate's formal check. ``trust_scene()``: the lifecycle
  template (two reviewed theorems, a prepared second toolchain) with one
  imported candidate and a transition to the prepared toolchain; its queue is
  the first theorem's trust check, a maintenance request and the candidate's
  formal check. Both return ``(sim, machine action, second action)``.
- ``take_turns(sim)``: the waiting check and the AI call take turns (round robin).
- ``hold_lean(sim, hold)``: every later Lean check runs ``hold()`` before it
  answers, on the calculation's turn (``owner_turn`` passes the turn to the owner).
- ``HeldLean(sim, control=...)``: holds the check until the owner has run the
  maintenance call to its end, moves the clock by ``LONG`` and lets one owner
  pass run on it, then queues ``control(sim)`` and answers at once. The
  calculation reads its flag clear and returns the late success; the owner
  publishes the control before it collects that result and judges its currentness.
- ``PassProbe(engine_code)``: counts owner passes (``_controls`` starts) and
  records the flag of one call when each ``_save`` starts and returns
  (``sys.monitoring``), so a test sees which publication set the flag.
- ``new_rows(sim, family, before)`` and ``artifact(sim, reference)`` read the
  rows added since ``before`` and a published artifact's JSON.
"""
from __future__ import annotations

import json
import sys
from support.monitoring_slots import reserve_tool

from do_math.engine import ResearchEngine
from support.engine_lifecycle import applied, clear_work, lifecycle_sim, prepared_environment, transition
from support.fakes.calls import owner_turn
from support.scheduling_parallel import round_robin
from support.sim import Sim

LEAN_ROLES = ('formal_check', 'trust_check')
# A long elapsed time: beyond every call's time limit (the operator roles' 5400 s), within the
# Sim grants' day. Wall and monotonic time move together; the clock guard refuses one without the other.
LONG = 3 * 3600.0


def theorem(name):
    return {'kind': 'theorem', 'title': name, 'statement': 'One equals one (' + name + ')', 'summary': 'Reflexivity',
            'explanation': 'By reflexivity.', 'lean_code': f'theorem {name} : 1 = 1 := rfl',
            'declaration_names': [name], 'dependencies': []}


def imported(sim, name):
    sim.lean.allow(f'theorem {name} : 1 = 1 := rfl', [name], signatures={name: name + ' : 1 = 1'})
    before = set(sim.instance['knowledge'])
    applied(sim, 'knowledge', config={'operation': 'import', 'candidate': theorem(name)})
    kid, = set(sim.instance['knowledge']) - before
    return kid


def _queue(sim, first, second):
    e = sim.engine
    e._enqueue('maintenance', reason='An AI call beside the machine check')
    maintenance = next(a for a in e.runtime['queue'] if a['role'] == 'maintenance')
    e.runtime['queue'][:] = [first, maintenance, second]
    e._save()
    return first, second


def formal_scene():
    sim = Sim.activated()
    clear_work(sim)
    kids = [imported(sim, name) for name in ('late_one', 'late_two')]
    checks = [next(a for a in sim.runtime['queue'] if a['role'] == 'formal_check' and a['target'] == kid) for kid in kids]
    return (sim, *_queue(sim, *checks))


def trust_scene():
    sim = lifecycle_sim()
    kid = imported(sim, 'late_one')
    transition(sim, prepared_environment(sim))
    queue = sim.runtime['queue']
    trust = next(a for a in queue if a['role'] == 'trust_check')
    formal = next(a for a in queue if a['role'] == 'formal_check' and a['target'] == kid)
    return (sim, *_queue(sim, trust, formal))


def take_turns(sim):
    sim.ports.calls.choose = round_robin()


def maintenance_ended(sim, before):
    return any(row['role'] == 'maintenance' and row['status'] == 'ended'
               for eid, row in sim.runtime['executions'].items() if eid not in before)


def hold_lean(sim, hold):
    spawn = sim.lean.spawn

    def held(command, **options):
        process = spawn(command, **options)
        answer = process.wait

        def wait(timeout=None):
            hold()
            return answer(timeout)
        process.wait = wait
        return process
    sim.lean.spawn = held


class HeldLean:
    def __init__(self, sim, *, control=None, jump=LONG):
        self.sim, self.control, self.jump = sim, control, jump
        self.before = set(sim.runtime['executions'])
        self.held, self.failures = 0, []
        hold_lean(sim, self.hold)

    def hold(self):
        sim = self.sim
        self.held += 1
        try:
            for _ in range(500):
                if maintenance_ended(sim, self.before):
                    break
                owner_turn()
            else:
                raise AssertionError('AI completion was blocked by the Lean check')
            sim.advance(self.jump)
            owner_turn()  # an owner pass on the moved clock while the check still runs
        except BaseException as error:
            # The Lean worker records any failure of its process as a worker error; keep it for the test.
            self.failures.append(repr(error))
            raise
        if self.control is not None:
            self.control(sim)  # queued as the check answers: published before the owner collects


def new_rows(sim, family, before):
    return [row for key, row in sim.runtime.get(family, {}).items() if key not in before]


def artifact(sim, reference):
    return json.loads(sim.engine.store.read(reference, sim.engine.head))


class PassProbe:
    """Owner passes and one call's stop flag around each publication, seen through ``sys.monitoring``.

    ``passes`` counts ``_controls`` starts (one per owner pass). ``flags`` lists
    ``(pass, flag at the start, flag at the return)`` of every ``_save``; a
    ``flag`` is ``None`` while the watched call has no future.
    """

    def __init__(self, execution_id=None):
        self.execution_id, self.passes, self.flags = execution_id, 0, []
        self._starts = []

    def flag(self, engine):
        calls = getattr(engine, '_calls', None)
        for future in (calls.futures if calls is not None else ()):
            if future.execution_id == self.execution_id:
                return future.stop.is_set()
        return None

    def __enter__(self):
        monitoring = sys.monitoring
        self.tool = reserve_tool('do-math pass probe')
        self.controls = ResearchEngine._controls.__code__
        self.save = ResearchEngine._save.__code__

        def started(code, offset):
            engine = sys._getframe(1).f_locals['self']
            if code is self.controls:
                self.passes += 1
            elif code is self.save:
                self._starts.append(self.flag(engine))

        def returned(code, offset, value):
            if code is self.save and self._starts:
                engine = sys._getframe(1).f_locals['self']
                self.flags.append((self.passes, self._starts.pop(), self.flag(engine)))
        monitoring.register_callback(self.tool, monitoring.events.PY_START, started)
        monitoring.register_callback(self.tool, monitoring.events.PY_RETURN, returned)
        monitoring.set_local_events(self.tool, self.controls, monitoring.events.PY_START)
        monitoring.set_local_events(self.tool, self.save, monitoring.events.PY_START | monitoring.events.PY_RETURN)
        return self

    def __exit__(self, *exception):
        monitoring = sys.monitoring
        for code in (self.controls, self.save):
            monitoring.set_local_events(self.tool, code, monitoring.events.NO_EVENTS)
        monitoring.register_callback(self.tool, monitoring.events.PY_START, None)
        monitoring.register_callback(self.tool, monitoring.events.PY_RETURN, None)
        monitoring.free_tool_id(self.tool)
        return False
