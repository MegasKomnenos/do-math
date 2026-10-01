"""Session slot scenes: an initialized instance with one work slot per model, and admissions on it.

- ``slot_sim()``: the legacy ``SlotTests`` start (``engine_fixtures.initialized_instance``):
  a public initialize with ``session_limits`` of one work slot per model and the
  scheduled operator on, restored from a template built once per process.
- ``reserve(sim, eid, *, operational=False, jobs=None)``: moved from
  ``SlotTests.reserve``. Admit a work role, which holds a model slot
  (``task_contract_review``), or an operational role, which holds none
  (``research_plan``), on the high model's profile: an activity and a starting
  execution are recorded and the slots ledger acquires. ``jobs`` is the Jobs port
  the ledger confirms Job ends with (default: the Sim's). Returns ``(accepted, execution)``.
- ``slots(sim, *, observer=False, jobs=None)``: the slots ledger over the engine's state.
"""
from __future__ import annotations

from do_math.activities import assign_execution, open_activity
from do_math.execution_lifecycle import create_execution, transition_execution
from do_math.execution_profiles import profile_ref
from do_math.model_policy import MODELS
from do_math.session_slots import SessionSlots
from support.sim import Sim, built

LIMITS = {'work': {model: 1 for model in MODELS.values()}}


def _slot_instance(root, shared):
    return Sim(root, shared=shared, goal='Reservation boundary fixture',
               config={'operator_enabled': True, 'session_limits': LIMITS})


def slot_sim():
    return built('scheduling-slot-instance', _slot_instance)


def slots(sim, *, observer=False, jobs=None):
    return SessionSlots(sim.engine.runtime, sim.engine.instance, observer=observer, clock=sim.clock,
                        jobs=jobs or sim.jobs, host_id=sim.host_id)


def reserve(sim, eid, *, operational=False, jobs=None):
    engine = sim.engine
    role = 'research_plan' if operational else 'task_contract_review'
    profile = next(p for p in engine.instance['execution_profiles'].values()
                   if p['role'] == role and p['ai']['model'] == MODELS['high'])
    at = sim.clock.now()
    action = {'id': 'AC-' + eid, 'role': role, 'profile_ref': profile_ref(profile)}
    activity = open_activity(engine.runtime, activity_id='AY-' + eid, activity_kind=role,
                             owner_ref=engine.instance['id'], input_refs=[], opened_at=at)
    execution = create_execution(execution_id=eid, owner_activity_id=activity['id'], actor_kind='ai',
                                 input_manifest=[], profile_ref=profile_ref(profile), created_at=at)
    execution.update(role=role, action=action, input_snapshot=engine.head)
    transition_execution(execution, 'starting', at=at)
    assign_execution(engine.runtime, activity['id'], execution)
    return slots(sim, jobs=jobs).acquire(eid, profile=profile, execution=execution), execution
