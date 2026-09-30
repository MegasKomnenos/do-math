"""The engine's provider admission (``provider_engine.ProviderEngineMixin``, layer 2) on the real engine.

The engine runs on the port fakes over a repository initialized with a small
state (``support.storage_records.engine_on``); its session slots use the Jobs
port fake, whose named-Job answer decides a recovery's local settlement. These
tests call the mixin's methods directly, as the owner loop does.
"""
from copy import deepcopy
from pathlib import Path
import sys
import tempfile
import unittest

from do_math.configuration import DEFAULT_CONFIG
from do_math.execution_profiles import TIERS, build_profiles
from do_math.scheduler import SchedulerMixin
from do_math.session_slots import SessionSlots
from provider_fixtures import PROVIDER_LIMIT_FAILURE, admit
from research_fixtures import current_state
from support.fakes.clock import FakeClock
from support.fakes.git_backend import InProcessGit
from support.provider_probes import ObservedCalls
from support.provider_runs import ProviderJobs, fake_ports
from support.storage_records import INSTANCE_ID, engine_on, record_store

TIME = "2026-09-20T00:00:00+00:00"


class EngineCase(unittest.TestCase):
    def engine(self, config, runtime=None):
        """The real engine over an initialized state with ``config`` and its profiles, and its Jobs fake."""
        root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        clock, backend = FakeClock(), InProcessGit()
        jobs = ProviderJobs(clock=clock)
        store = record_store(root / 'repository', backend=backend, clock=clock)
        instance, state = current_state({'id': INSTANCE_ID, 'config': config, **build_profiles(config)},
                                        {'executions': {}, 'reservations': {}, 'provider_waits': {}, 'queue': [],
                                         'status': 'ready', **(runtime or {})})
        engine, _ = engine_on(store, instance, state, workspace=root / 'work', ports=fake_ports(clock, backend, jobs))
        return engine, jobs


def work_profile(engine):
    return next(p for p in engine.instance['execution_profiles'].values()
                if p['role'] == 'research_work' and p['actor_kind'] == 'ai')


class ProviderAdmissionTests(EngineCase):
    def test_provider_mixin_records_structured_wait_on_refused_admission(self):
        engine, _ = self.engine({**deepcopy(DEFAULT_CONFIG), 'scholarly_enabled': False,
                                 'provider_retry_initial_seconds': 20, 'provider_retry_max_seconds': 60})
        profile = work_profile(engine)
        provider = profile['ai']['provider']
        self.assertTrue(engine._provider_admit({'id': 'AC-1'}, 'EX-1', profile=profile,
                                               execution={'id': 'EX-1', 'role': 'research_work', 'status': 'starting'}))
        # The provider refused the first call: its gate now waits for a retry time.
        engine._provider_outcome('EX-1', {'status': 'failed', 'error_kind': 'provider_limit', 'failure': {
            'kind': 'provider_limit', 'provider': provider, 'retry_at': None, 'limit_windows': [],
            'evidence_ref': 'stdout.jsonl'}})
        action = {'id': 'AC-2', 'model_selection': {'tier': profile['ai']['tier'], 'model': profile['ai']['model'],
                  'assessment': None, 'reason': 'Provider-admission fixture assignment'}}
        with ObservedCalls(acquire=SessionSlots.acquire, capture={'acquire': lambda arguments: arguments['self']}) as calls:
            admitted = engine._provider_admit(action, 'EX-2', profile=profile,
                                              execution={'id': 'EX-2', 'role': 'research_work', 'status': 'starting'})
        self.assertFalse(admitted)
        slots, = calls.captured('acquire')
        self.assertEqual(action['dispatch_wait'], slots.admission_wait)
        self.assertIsNot(action['dispatch_wait'], slots.admission_wait)
        self.assertEqual((action['dispatch_wait']['kind'], action['dispatch_wait']['provider']),
                         ('provider_limit', provider))
        self.assertNotIn('EX-2', engine.runtime['executions'])

    def test_provider_admission_reserves_runtime_capacity_and_settles_after_the_job_is_empty(self):
        config = {**deepcopy(DEFAULT_CONFIG), 'observation_mode': 'event_driven', 'max_input_bytes': 16_384,
                  'effort': 'medium', 'operator_effort': 'medium', 'operator_timeout_seconds': 60,
                  'scholarly_enabled': True, 'scholarly_server': None, 'claude_only_assigned_model': False,
                  'tier_models': {tier: 'gpt-5.6-terra' for tier in TIERS},
                  'session_limits': {'work': {'gpt-5.6-terra': 2}}}
        engine, jobs = self.engine(config)
        profile = work_profile(engine)
        execution = {'id': 'EX-git', 'role': profile['role'], 'status': 'starting'}
        self.assertTrue(engine._provider_admit({'id': 'AC-git'}, 'EX-git', profile=profile, execution=execution))
        self.assertIs(engine.runtime['executions']['EX-git'], execution)
        self.assertTrue(engine.runtime['reservations'])
        other = {'id': 'EX-independent', 'role': 'research_work', 'status': 'starting'}
        self.assertTrue(engine._provider_admit({'id': 'AC-independent'}, other['id'], profile=profile, execution=other))
        slots = engine._session_slots()
        name = execution['launch_ticket']['job_name']
        slots.started('EX-git', {'job_name': name}, at=TIME)
        self.assertEqual(execution['status'], 'running')
        # The worker still runs in the ticket's named Job: the recovery cannot settle.
        job = jobs.launch([sys.executable, 'codex_worker.py', 'request.json'], name=name)
        self.assertFalse(engine._settle_recovered_execution('EX-git', at=TIME))
        self.assertEqual(execution['status'], 'running')
        job.terminate()
        self.assertTrue(engine._settle_recovered_execution('EX-git', at=TIME))
        self.assertEqual((execution['status'], execution['outcome']), ('ended', 'execution_incomplete'))
        self.assertEqual(execution['capacity']['local_termination'], 'confirmed')
        self.assertEqual(other['status'], 'starting')
        held = [row for row in engine.runtime['reservations'].values() if row['owner_id'] == other['id']]
        self.assertTrue(held)
        self.assertTrue(all(row['state'] == 'held' for row in held))
        self.assertTrue(slots.release('EX-git'))


class ProviderResultTests(EngineCase):
    def test_result_observation_has_no_prepublication_schedule_effect(self):
        """About 0.2 s, at the unit budget: a real engine on an initialized repository and one publication are the subject."""
        # The scheduled operator is enabled, so a wake would reach the scheduler port.
        config = {**deepcopy(DEFAULT_CONFIG), 'scholarly_enabled': False, 'operator_enabled': True,
                  'tier_models': {tier: 'claude-opus-5' for tier in TIERS},
                  'session_limits': {'work': {'claude-opus-5': 3}}}
        engine, _ = self.engine(config)
        now = engine.ports.clock.wall_ns() / 1_000_000_000
        self.assertTrue(admit(engine._session_slots(), engine.instance, engine.runtime, 'EX-limit', current=now))
        with ObservedCalls(wake=SchedulerMixin._schedule_provider_wake) as calls:
            gate = engine._provider_outcome('EX-limit', {'status': 'failed', 'error_kind': 'provider_limit',
                                                         'failure': PROVIDER_LIMIT_FAILURE})
        self.assertEqual(gate['state'], 'waiting')
        self.assertEqual(calls.count('wake'), 0)
        self.assertEqual(engine.ports.scheduler.calls, [])
        # Publishing the result is what schedules the wake, after the Git publication.
        with ObservedCalls(wake=SchedulerMixin._schedule_provider_wake) as calls:
            engine._publish_provider_result()
        self.assertEqual(calls.count('wake'), 1)
        self.assertEqual([action for action, _ in engine.ports.scheduler.calls], ['status', 'schedule-wake'])


class ResourceWaitTests(EngineCase):
    def test_configure_wakes_only_changed_resource_waits_and_keeps_pinned_profile(self):
        """About 0.3 s, over the 0.2 s unit budget: four candidate configurations each author every profile edition."""
        config = {**deepcopy(DEFAULT_CONFIG), 'scholarly_enabled': False}
        config['session_limits']['work'] = {model: 0 for model in config['tier_models'].values()}
        e, _ = self.engine(config)
        # A goal audit waits for capacity the user withheld; its profile edition is pinned.
        e.runtime.update(status='waiting', queue=[{'id': 'AC-wait', 'role': 'goal_audit',
            'profile_ref': deepcopy(e.instance['role_profile_refs']['goal_audit'][0]),
            'dispatch_wait': {'kind': 'capacity', 'next_owner': 'user'}}])
        original = deepcopy(e.runtime['queue'][0]['profile_ref'])
        request = {'origin': 'user', 'config': {'session_limits': deepcopy(DEFAULT_CONFIG['session_limits'])}}
        _, state = e._configure_candidate(e.instance, e.runtime, request)
        self.assertEqual(state['status'], 'ready')
        self.assertNotIn('dispatch_wait', state['queue'][0])
        self.assertEqual(state['queue'][0]['profile_ref'], original)
        self.assertEqual(e.runtime['status'], 'waiting')
        _, same = e._configure_candidate(e.instance, e.runtime, {'origin': 'user', 'config': {}})
        self.assertEqual(same['status'], 'waiting')
        self.assertEqual(same['queue'][0]['dispatch_wait'], {'kind': 'capacity', 'next_owner': 'user'})
        e.runtime['status'] = 'capacity_waiting'
        _, same = e._configure_candidate(e.instance, e.runtime, {'origin': 'user', 'config': {}})
        self.assertEqual(same['status'], 'capacity_waiting')
        e.runtime['status'] = 'paused'
        _, paused = e._configure_candidate(e.instance, e.runtime, request)
        self.assertEqual(paused['status'], 'paused')


if __name__ == '__main__':
    unittest.main()
