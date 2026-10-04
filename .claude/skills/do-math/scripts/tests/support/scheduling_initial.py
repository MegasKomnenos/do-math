"""An initializing Sim whose initial interpretation failed: the start of the initial diagnosis tests.

Moved from ``engine_fixtures.initial_failure_engine``, which built the same
records on an in-memory ``FakeEngine`` seed under an autospec store. Here the
instance is a real initializing one: ``adopted_sim()`` restores a template that
applied the public activation controls (charter, grants, probe, trust and the
initialization decision whose initial grant covers intent interpretation and
maintenance), so the engine queued the initial interpretation but no owner pass
ran it. ``initial_failure(sim, kind, stage)`` then records the failed attempt
the legacy fixture wrote, on that real queued action, and publishes it through
the engine's own ``_save`` under the storage contract:

- the action (``stage`` as given, activity ``AY-original``) left the queue;
- execution ``EX-bad`` ran it, its launch ended and its local termination is
  confirmed, and it ended ``execution_incomplete``;
- the activity waits for maintenance, and ``waiting_actions`` holds the wait
  of ``kind`` (``output_validation`` adds the second repair attempt with
  ``IN-pending`` left to retry).

Returns ``(action, wait)``; the initial grant is ``GRANT``.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import timedelta

from support.sim import Sim, built

GRANT = 'GR-initial-sim'
TEXT = 'Synthetic Sim input; not actual host verification or user approval'


def _adopt(sim):
    """The controls of ``Sim.activate`` with an initial grant for both initialization roles, and no owner run."""
    from do_math.canonical import exact_content_hash
    from do_math.model_policy import selection
    from do_math.contracts import ROLES
    from support.state_builders import charter_record
    from support.trust_inputs import trust_fixture
    engine = sim.engine
    windows = {key: value for key, value in {'tool_review_window_seconds': 60,
                                             'self_check_response_window_seconds': 5}.items()
               if key not in sim.instance['config']}
    if windows:
        sim._apply('configure', config=windows)
    expiry = (sim.clock.wall() + timedelta(days=1)).isoformat()
    config_sha256 = exact_content_hash(sim.instance['config'])
    initial_ref = selection(sim.instance['config'], {'role': 'intent_interpretation'}, {},
                            sim.instance['knowledge'], instance=sim.instance)['profile_ref']
    charter = charter_record(sim.instance['lifecycle']['immutable_input']['text'])
    for action, config in [
            ('decision', {'change': {'kind': 'initialization', 'operation': 'governance', 'records': [charter]}}),
            ('decision', {'change': {'kind': 'grant', 'grant': {'id': GRANT, 'kind': 'local',
                'roles': ['intent_interpretation', 'maintenance'], 'reuse': 'reusable', 'expires_at': expiry}}}),
            ('decision', {'change': {'kind': 'grant', 'grant': {'id': 'GR-research-sim', 'kind': 'local',
                'roles': list(ROLES) + ['formal_check'], 'reuse': 'reusable', 'expires_at': expiry}}}),
            ('decision', {'change': {'kind': 'initialization', 'operation': 'probe', 'config_sha256': config_sha256}}),
            ('trust', trust_fixture(sim.shared, sim.instance['config']['lean_command'], directory=sim.shared / 'trust'))]:
        sim.control(action, text=TEXT, config=config)
    engine.process_controls()
    sim._check_applied()
    environment = next(iter(sim.instance['trust_environments']))
    sim._apply('trust', config={'operation': 'transition', 'env_id': environment})
    sim._apply('decision', config={'change': {'kind': 'initialization', 'config_sha256': config_sha256,
        'adopt_current_governance': True, 'conversation_loss_policy': 'continue_authorized',
        'external_policy': 'disabled', 'adopt_default_review_policy': True, 'initial_profile_ref': initial_ref,
        'initial_grant_ids': [GRANT], 'research_grant_ids': ['GR-research-sim']}})
    if not any(row['role'] == 'intent_interpretation' for row in sim.runtime['queue']):
        raise AssertionError('the initialization decision queued no initial interpretation')
    return sim


def adopted_sim():
    """A restored initializing Sim whose initialization is adopted and whose initial interpretation is queued."""
    return built('scheduling-adopted-initialization', lambda root, shared: _adopt(Sim(root, shared=shared)))


def initial_failure(sim, kind='execution_failure', stage='interpret'):
    from do_math import activities, execution_lifecycle, execution_profiles
    from support.execution_inputs import dispatched_launch
    if stage == 'check':
        sim.run_until(lambda current: any(row['role'] == 'intent_interpretation'
            and row.get('stage', 'interpret') == 'check' for row in current.runtime['queue'])
            and all(row['status'] == 'ended' for row in current.runtime['executions'].values()), max_steps=8)
    engine = sim.engine
    runtime = engine.runtime
    queued = next(row for row in runtime['queue'] if row['role'] == 'intent_interpretation'
                  and row.get('stage', 'interpret') == stage)
    action = {**deepcopy(queued), 'stage': stage, 'owner_activity_id': 'AY-original'}
    profile = execution_profiles.resolve_profile(engine.instance['execution_profiles'], action['profile_ref'])
    at = sim.clock.now()
    activities.open_activity(runtime, activity_id='AY-original', activity_kind='intent_interpretation',
                             owner_ref='engine', input_refs=[action['target']], opened_at=at)
    failed = execution_lifecycle.create_execution(execution_id='EX-bad', owner_activity_id='AY-original',
        actor_kind='ai', input_manifest={}, profile_ref=execution_profiles.profile_ref(profile), created_at=at)
    failed['launch_ticket'] = {**dispatched_launch(failed['id'], profile, jobs=sim.jobs, clock=sim.clock), 'phase': 'finished'}
    failed.update(role=action['role'], action=deepcopy(action), capacity={'local_termination': 'confirmed'})
    activities.assign_execution(runtime, 'AY-original', failed)
    for status in ('starting', 'stopping'):
        execution_lifecycle.transition_execution(failed, status, at=at)
    execution_lifecycle.transition_execution(failed, 'ended', at=at, outcome='execution_incomplete')
    activities.wait_for(runtime, 'AY-original', kind=kind, reason=kind, condition={'action_ids': [action['id']]},
                        next_owner='maintenance', at=at)
    wait = {'kind': kind, 'action': action, 'execution_id': 'EX-bad', 'reason': 'synthetic failure'}
    if kind == 'output_validation':
        action.update(repair_attempt=2, repair={'execution_id': 'EX-bad', 'issues': [], 'retry_bundle_ids': ['IN-pending']})
    runtime.update(queue=[], waiting_actions={action['id']: wait})
    engine._save()
    runtime = engine.runtime  # a save may replace the runtime with the published object
    wait = runtime['waiting_actions'][action['id']]
    return wait['action'], wait
