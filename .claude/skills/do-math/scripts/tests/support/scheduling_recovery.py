"""Start states of the research recovery tests, moved from ``test_research_recovery``'s ``restore_template`` builds.

Each is a template built once per process through the public activation (the
first two of an instance configured with ``max_output_repairs`` 0, ``NO_REPAIR``)
and restored per test (``support.sim.built``). The legacy builds started from the synthetic
active state and drove it with ``PurposeAnswers`` or a local invalid runner; here
the owner runs on the Sim and the model double answers.

- ``reviewed_sim()``: the legacy ``reviewed_task``. The default responder's
  preparation proposed one task, its contract review approved it, and the plan
  it opened is queued. The task readiness is process state (preserved rule
  K-20): a test that needs it calls ``_refresh_readiness``.
- ``failed_plan_sim()``: the legacy ``parked_failed_plan``. The only queued
  action ``AC-failed`` was a plan that selected the absent task ``TK-completed``;
  its execution ended ``execution_incomplete`` and the action waits in
  ``waiting_actions``. ``failed_execution(sim)`` is that execution.
- ``limited_recovery_sim()``: the legacy ``paused_limited_recovery`` (docstring there).
- ``empty_plan(**changes)``: a plan output deciding nothing, with ``changes``.
"""
from __future__ import annotations

from support.scheduling_model import explicit, scenario_model
from support.sim import Sim, built

NO_REPAIR = {'max_output_repairs': 0}


def empty_plan(**changes):
    from support.purpose_answers import common
    return {**common('Compare the current task population.'), 'dispositions': [], 'preparation_requests': [],
            'goal_audit': False, 'task_assessments': [], **changes}


def _plan_queued(sim):
    return any(row['role'] == 'research_plan' for row in sim.runtime['queue'])


def _reviewed(root, shared):
    sim = Sim.activated(root, shared=shared, config=NO_REPAIR)
    sim.run_until(lambda s: _plan_queued(s) and any(row['state'] == 'ready' for row in s.engine._task_readiness.values()),
                  max_steps=45)
    return sim


def _failed_plan(root, shared):
    from support.role_answers import disposition
    sim = Sim.activated(root, shared=shared, config=NO_REPAIR)
    scenario_model(sim).on('research_plan').reply(explicit(empty_plan(dispositions=[disposition('TK-completed')])))
    sim.engine.runtime['queue'] = [{'id': 'AC-failed', 'role': 'research_plan'}]
    sim.engine._save()
    sim.step()
    failed = failed_execution(sim)
    if failed['outcome'] != 'execution_incomplete' or 'AC-failed' not in sim.runtime['waiting_actions']:
        raise AssertionError('The invalid plan was not parked: ' + repr(failed))
    return sim


def _limited_recovery(root, shared):
    from datetime import timedelta
    from support.engine_lifecycle import applied
    sim = Sim.activated(root, shared=shared)
    engine = sim.engine
    engine.runtime['queue'] = []
    engine._enqueue('maintenance', engine.instance['id'], id='AC-limited',
                    reason='Inspect the preserved recovery state and report remaining work')
    engine._save()
    applied(sim, 'pause', text='Keep general research paused')
    action = next(a for a in sim.runtime['queue'] if a['id'] == 'AC-limited')
    applied(sim, 'decision', config={'change': {
        'kind': 'limited_recovery', 'action_id': action['id'],
        'grant_id': sim.instance['lifecycle']['adoption']['research_grant_ids'][0],
        'profile_ref': sim.engine._select_model(action)['profile_ref'],
        'purpose': 'Inspect the preserved recovery state',
        'procedure': 'Read the supplied state and return a maintenance report',
        'expires_at': (sim.clock.wall() + timedelta(minutes=5)).isoformat()}})
    return sim


def reviewed_sim():
    return built('scheduling-reviewed-task', _reviewed)


def limited_recovery_sim():
    """The legacy ``paused_limited_recovery``: a user pause and an approved limited recovery of the maintenance ``AC-limited``.

    Both went through public controls; the decision expires five minutes after the build on the Sim clock.
    """
    return built('scheduling-paused-limited-recovery', _limited_recovery)


def failed_plan_sim():
    return built('scheduling-parked-failed-plan', _failed_plan)


def failed_execution(sim):
    return next(row for row in sim.runtime['executions'].values() if row.get('action', {}).get('id') == 'AC-failed')
