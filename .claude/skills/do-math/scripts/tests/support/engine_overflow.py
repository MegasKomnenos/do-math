"""Input overflow scenes of the engine region on the Sim: a public maintenance request held by its first overflow.

The legacy tests configured ``max_input_bytes`` through the CLI on the synthetic
active state, wrote the new profiles' capability evidence by hand, and drove
``DefaultResponder``. Here every step is a public control on the restored public
activation (the CLI's ``configure`` and ``request --retry-action`` send exactly
these controls; ``boundary/test_engine_cli.py`` runs the command surface), the
new profile editions get their capability evidence from the public ``probe``
decision over the fake host, and model calls run through the worker and the
model double.

- ``apply_limit(sim, limit, request_id)``: the public ``configure`` of
  ``max_input_bytes`` applied by the owner, then the probe of every AI profile
  the configuration adopted. A rejected control fails at once.
- ``overflowed_sim()``: a restored copy of one activation whose queue was
  cleared, whose limit is 1 byte, and whose public maintenance request
  ``UC-maintenance`` one owner pass held by its first input overflow.
- ``held(sim)``: ``(action ID, waiting row)`` of the held maintenance request.
- ``retry(sim, action_id, request_id)``: the public ``request`` retrying the held
  action, applied by the owner as the CLI's command does.
- ``close_provider_gate(engine, provider)`` and
  ``gate_closes_before_admission(sim, provider)``: a provider's gate closed by a
  reported usage limit, now or when the engine next admits a prepared action.
- ``held_work(sim)``: research work held by an input overflow for the planner.
"""
from contextlib import contextmanager
import sys
from support.monitoring_slots import reserve_tool

from support.engine_lifecycle import applied, clear_work
from support.sim import Sim, built

REASON = 'Check the installed recovery boundary'


def apply_limit(sim, limit, request_id):
    applied(sim, 'configure', config={'max_input_bytes': limit}, request_id=request_id)
    refs = [ref for rows in sim.instance['role_profile_refs'].values() for ref in rows
            if sim.instance['execution_profiles'][ref['id']]['actor_kind'] == 'ai']
    applied(sim, 'decision', config={'change': {'kind': 'initialization', 'operation': 'probe', 'profile_refs': refs}})


def held(sim):
    """The held maintenance request: ``(action ID, its waiting row)``."""
    return next((key, row) for key, row in sim.runtime.get('waiting_actions', {}).items()
                if row.get('kind') == 'input_overflow' and row['action']['role'] == 'maintenance')


def retry(sim, action_id, request_id):
    """The CLI's ``request --retry-action``: the control, then the owner applies it; returns the control's answer."""
    answer = sim.control('request', config={'retry_action': action_id}, request_id=request_id)
    sim.engine.process_controls()
    return answer


def close_provider_gate(engine, provider):
    """``provider``'s gate closed by a usage limit one of its ended calls reported; returns the gate's retry time.

    The gate is the session slots' own record of that result
    (``SessionSlots.provider_result_from_run``, as the engine applies a
    returned call): a ``provider_limit`` failure without a reset time, so the
    retry waits the configured initial interval. Nothing is published here.
    """
    execution_id = next(row['id'] for row in engine.runtime['executions'].values()
                        if row.get('status') == 'ended' and row.get('capacity', {}).get('provider') == provider)
    result = {'status': 'failed', 'error_kind': 'provider_limit', 'error': 'usage limit reached',
              'failure': {'kind': 'provider_limit', 'provider': provider, 'message': 'usage limit reached'}}
    gate = engine._session_slots().provider_result_from_run(execution_id, result, engine.instance['config'])
    if gate['open']:
        raise AssertionError('the usage limit did not close the provider gate: ' + repr(gate))
    return engine.runtime['provider_waits']['PW-' + provider]['retry_at']


@contextmanager
def gate_closes_before_admission(sim, provider):
    """Close ``provider``'s gate when the engine first starts ``_provider_admit`` inside the block.

    The admission then refuses an action whose dispatch check passed and whose
    input was prepared, which is where the engine records a deferred start. In
    one owner pass nothing closes a gate between the two checks, so the closing
    is placed at that point: a ``sys.monitoring`` start event of the admission's
    code runs ``close_provider_gate`` on the engine first; nothing is replaced.
    Yields ``{'retry_at': the gate's retry time, once it closed}``.
    """
    from do_math.provider_engine import ProviderEngineMixin
    code, state = ProviderEngineMixin._provider_admit.__code__, {'retry_at': None}
    monitoring = sys.monitoring
    tool = reserve_tool('do-math provider gate at admission')

    def started(started_code, offset):
        if state['retry_at'] is None:
            state['retry_at'] = 'closing'
            state['retry_at'] = close_provider_gate(sim.engine, provider)
    monitoring.register_callback(tool, monitoring.events.PY_START, started)
    monitoring.set_local_events(tool, code, monitoring.events.PY_START)
    try:
        yield state
    finally:
        monitoring.set_local_events(tool, code, monitoring.events.NO_EVENTS)
        monitoring.register_callback(tool, monitoring.events.PY_START, None)
        monitoring.free_tool_id(tool)


def held_work(sim):
    """Research work ``AC-held`` on the reviewed task ``TK-1``, held by an input overflow for the planner's choice.

    The task offers two research profiles, the adopted one (``small``) and a
    sealed copy with twice its input limit (``large``, which the wait offers).
    The action's activity ``AY-held`` waits for the planner; the wait names the
    question ``QU-held``. The state is the engine's, unsaved (the legacy
    ``context_engine`` held it in memory). Returns ``large``'s reference.
    """
    from copy import deepcopy
    from do_math import activities, execution_profiles, planning
    from support.engine_lifecycle import approve, research_grant, task
    engine = sim.engine
    clear_work(sim)
    row = task(engine, 'TK-1', approved=False)
    small = execution_profiles.resolve_profile(engine.instance['execution_profiles'],
                                               engine.instance['role_profile_refs']['research_work'][0])
    large = deepcopy(small)
    large['input']['max_input_bytes'] *= 2
    large = execution_profiles.seal_profile(large)
    engine.instance['execution_profiles'][large['id']] = large
    row['profile_refs'] = [execution_profiles.profile_ref(small), execution_profiles.profile_ref(large)]
    row['status'] = 'active'
    approve(engine, row)
    at = engine._lifecycle_now().isoformat()
    action = {'id': 'AC-held', 'role': 'research_work', 'target': row['id'], 'owner_activity_id': 'AY-held',
              'grant_id': research_grant(engine), 'selected_contract_sha256': planning.contract_hash(row),
              'profile_ref': execution_profiles.profile_ref(small),
              'model_assessment': {'difficulty': 'low', 'importance': 'low', 'reason': 'Bounded work'}}
    activities.open_activity(engine.runtime, activity_id='AY-held', activity_kind='research_work', owner_ref='AC-held',
                             input_refs=[row['id']], opened_at=at)
    activities.wait_for(engine.runtime, 'AY-held', reason='input_overflow', condition={'action_ids': ['AC-held']},
                        next_owner='research_plan', at=at)
    engine.runtime['waiting_actions'] = {'AC-held': {'kind': 'input_overflow', 'action': action,
        'question_id': 'QU-held', 'next_owner': 'research_plan', 'detail': {
            'allowed_profile_candidates': [large['id']], 'cause': 'required_role_input',
            'packed_bytes': small['input']['max_input_bytes'] + 10}}}
    return execution_profiles.profile_ref(large)


def _overflowed(root, shared):
    sim = Sim.activated(root, shared=shared)
    apply_limit(sim, 1, 'UC-limit-small')
    clear_work(sim)
    # The CLI's request: the control, then the owner applies it before the command returns.
    requested = sim.control('request', text=REASON, config={'role': 'maintenance', 'target': None},
                            request_id='UC-maintenance')
    if not requested['accepted']:
        raise AssertionError(requested)
    sim.engine.process_controls()
    sim.step()
    if len(sim.runtime.get('input_overflows', [])) != 1:
        raise AssertionError('the maintenance request was not held by one input overflow: ' + repr(sim.waiting()))
    held(sim)
    return sim


def overflowed_sim():
    return built('engine-overflowed-maintenance', _overflowed)
