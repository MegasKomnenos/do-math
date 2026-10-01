"""Scheduling judgments of the owner on a Sim, without a model call.

Session slots and their Git-published reservations, the owner's rescan rule,
plan settling, readiness events, machine admission under an approved host
constraint, the maintenance fence and the order of queued operating requests.
The engines are real and publish through their store; the legacy tests' clock
patches are the Sim clock and their autospec doubles are ``ObservedCalls``.
"""
from copy import deepcopy
from datetime import timedelta
from pathlib import Path
import platform
import unittest

from do_math import scheduled_operator, task_scope
from do_math.engine import ResearchEngine, initialize
from do_math.execution_lifecycle import create_execution, release_or_hold, transition_execution
from do_math.activities import assign_execution, open_activity
from do_math.execution_profiles import HOST_ROLES, host_constraint, profile_ref
from do_math.model_policy import MODELS
from do_math.scheduler import OWNER_RESCAN_SECONDS
from do_math.session_slots import SessionSlots
from support.engine_lifecycle import _ended_execution, applied, approve, clear_work, research_grant, task
from support.provider_probes import ObservedCalls
from support.scheduling_slots import reserve, slot_sim, slots
from support.sim import Sim, warm_template

MiB = 1024 ** 2


def setUpModule():
    warm_template()
    slot_sim()


class OwnerRescanTests(unittest.TestCase):
    def test_owner_rejudges_after_a_state_change_or_its_time_bound_but_not_after_an_observation(self):
        sim = Sim.activated()
        engine = sim.engine
        self.assertTrue(engine._scan_due())
        self.assertFalse(engine._scan_due(), 'an unchanged state was judged again')
        engine.runtime['history'].append({'kind': 'fixture_observation'})
        engine._publish_observation()
        self.assertFalse(engine._scan_due(), 'an observation publication made the owner judge again')
        engine.runtime['history'].append({'kind': 'fixture_change'})
        self.assertTrue(engine._scan_due())
        self.assertFalse(engine._scan_due())
        sim.advance(OWNER_RESCAN_SECONDS)
        self.assertTrue(engine._scan_due())


class SlotTests(unittest.TestCase):
    """The Git writer owns admission; observers never reconcile reservations."""

    def setUp(self):
        self.sim = slot_sim()
        self.workspace = Path(self.sim.instance['workspace'])

    @property
    def engine(self):
        return self.sim.engine

    def slots(self, *, observer=False):
        return slots(self.sim, observer=observer)

    def reserve(self, eid, *, operational=False):
        return reserve(self.sim, eid, operational=operational)

    def test_work_slot_operational_admission_and_reusable_slots_are_published_together(self):
        with self.engine.store.writer_lock():
            self.assertTrue(self.reserve('EX-work')[0])
            self.assertFalse(self.reserve('EX-blocked')[0])
            self.assertTrue(self.reserve('EX-operation', operational=True)[0])
            self.engine._save()
            head, _, runtime = self.engine.store.load()
            self.assertEqual(head, self.engine.head)
            self.assertTrue(runtime['reservations'])
            self.assertFalse([row for row in runtime['reservations'].values()
                              if row['owner_id'] == 'EX-operation' and row['unit'] == 'execution'])
            self.assertTrue(all(row['owner_id'] in runtime['executions'] for row in runtime['reservations'].values()))
            self.assertTrue(self.slots().release('EX-work'))
            self.assertTrue(self.reserve('EX-next')[0])
            self.engine._save()
        self.assertFalse(list(self.workspace.rglob('*.sqlite*')))

    def test_saved_reservations_survive_reopen_until_explicit_release(self):
        from support.entry import entry
        _entry = entry()
        with self.engine.store.writer_lock():
            self.assertTrue(self.reserve('EX-held')[0])
            self.engine._save()
        saved = deepcopy(self.engine.runtime['reservations'])
        # The legacy test reopened the engine in the same owner process (sim.restart models a new process).
        self.sim.engine = ResearchEngine(self.sim.repository, self.sim.instance_id, ports=self.sim.ports, codex_home=self.sim.codex_home, environment=self.sim.environment, host_id=self.sim.host_id)
        self.assertEqual(self.engine.runtime['reservations'], saved)
        self.assertEqual(self.slots(observer=True).snapshot()[MODELS['high']]['used'], 1)
        with self.engine.store.writer_lock():
            self.assertTrue(self.slots().release('EX-held'))
            self.engine._save()
        self.assertEqual(self.slots(observer=True).snapshot()[MODELS['high']]['used'], 0)

    def test_distinct_instances_have_distinct_reservation_ledgers(self):
        from support.entry import entry
        _entry = entry()
        with self.engine.store.writer_lock():
            self.assertTrue(self.reserve('EX-first-instance')[0])
            self.engine._save()
        config = self.engine.instance['config']
        created = initialize(self.sim.repository, goal='Separate reservation ledger', workspace=self.sim.root / 'other-work',
                             config={'session_limits': deepcopy(config['session_limits']), 'operator_enabled': False,
                                     'scholarly_enabled': False, 'lean_command': list(config['lean_command'])},
                             ports=self.sim.ports, codex_home=self.sim.codex_home, host_id=self.sim.host_id)
        other = ResearchEngine(self.sim.repository, created['instance_id'], ports=self.sim.ports, codex_home=self.sim.codex_home, environment=self.sim.environment, host_id=self.sim.host_id)
        self.assertNotEqual(other.instance['id'], self.engine.instance['id'])
        observer = SessionSlots(other.runtime, other.instance, observer=True, clock=self.sim.clock, jobs=self.sim.jobs, host_id=_entry.host_id)
        self.assertEqual(observer.snapshot()[MODELS['high']]['used'], 0)
        self.assertEqual(self.slots(observer=True).snapshot()[MODELS['high']]['used'], 1)
        self.assertEqual(other.store.load()[2]['reservations'], {})

    def test_observer_cannot_acquire_or_reconcile_an_unknown_lifetime(self):
        with self.engine.store.writer_lock():
            self.reserve('EX-held')
            self.engine._save()
        before = deepcopy(self.engine.runtime)
        observer = self.slots(observer=True)
        with self.assertRaisesRegex(ValueError, 'a read-only slot observer cannot mutate reservations'):
            observer.release('EX-held')
        observer.snapshot()
        self.assertEqual(self.engine.runtime, before)

    def test_recovery_requires_actual_failure_evidence(self):
        from support.entry import entry
        _entry = entry()
        head = self.engine.head
        with self.assertRaisesRegex(ValueError, 'recovery requires preserved engine failure evidence'):
            scheduled_operator.recovery(self.sim.repository, self.engine.instance['id'], self.workspace, failure={}, codex_home=_entry.codex_home, environment=_entry.environment, host_id=_entry.host_id, ports=_entry.ports)
        self.assertEqual(self.engine.store.load()[0], head)


class PlanSettleTests(unittest.TestCase):
    def setUp(self):
        self.sim = Sim.activated()
        self.engine = self.sim.engine
        self.engine.runtime['queue'] = []

    def queue(self, plan, review=True):
        self.engine.runtime['queue'] = [plan, *([{'id': 'AC-review', 'role': 'task_contract_review', 'target': 'TK-x'}]
                                               if review else [])]
        return plan

    def test_a_plan_waits_for_pending_contract_reviews_so_nearby_approvals_share_one_decision(self):
        plan = self.queue({'id': 'AC-plan', 'role': 'research_plan'})
        self.assertFalse(self.engine._dispatchable(plan))
        self.assertEqual(plan['dispatch_wait']['kind'], 'plan_settle')
        self.queue(plan, review=False)
        self.assertTrue(self.engine._dispatchable(plan))

    def test_the_settle_wait_ends_at_its_configured_limit(self):
        self.assertEqual(self.engine.instance['config']['plan_settle_seconds'], 300)
        started = (self.sim.clock.wall() - timedelta(seconds=301)).isoformat()
        plan = self.queue({'id': 'AC-plan', 'role': 'research_plan', 'settle_started_at': started})
        self.assertTrue(self.engine._dispatchable(plan), 'a slow review must not hold the first ready task for long')

    def test_an_explicitly_requested_plan_does_not_settle(self):
        plan = self.queue({'id': 'AC-plan', 'role': 'research_plan', 'requested_by': 'UC-user'})
        self.assertTrue(self.engine._dispatchable(plan))


class ReadinessResponsibilityTests(unittest.TestCase):
    def test_terminal_stale_assessment_gets_one_followup_without_reopening(self):
        sim = Sim.activated()
        clear_work(sim)
        engine = sim.engine
        # Task TK-1 waits for the missing input SO-new after an incomplete assessment by a returned plan.
        row = task(engine, 'TK-1', approved=False)
        for obligation in row['completion_obligations']:
            obligation.update(evidence_required=[])
        approve(engine, row)
        engine.runtime['tasks']['TK-1'].update(status='waiting', results=[{'id': 'EV-1', 'execution_id': 'EX-work'}])
        _ended_execution(engine, 'EX-plan', 'research_plan')
        assessment = {'task_id': 'TK-1', 'decision': 'incomplete', 'reason': 'One input is missing',
                      'item_dispositions': [{'obligation_id': 'OB-scope', 'kind': 'fulfilled', 'evidence_refs': ['EV-1']}],
                      'unresolved': [{'obligation_id': 'OB-proof', 'missing_inputs': ['SO-new'], 'next_owner': 'research_work'}]}
        engine.instance, engine.runtime = task_scope.apply_task_assessments(
            engine.instance, engine.runtime, [assessment], execution_id='EX-plan', input_tasks=deepcopy(engine.runtime['tasks']),
            evaluation_context=engine._evaluation_context(), clock=sim.clock)
        engine._save()
        engine.runtime['queue'] = [{'id': 'AC-other', 'role': 'research_preparation'}]
        row = engine.runtime['tasks']['TK-1']
        row['status'] = 'closed'
        row['assessment'].update(current=False, invalidated_reason='source corrected')
        engine._refresh_readiness()
        engine._refresh_readiness()
        self.assertEqual(row['status'], 'closed')
        events = [e for e in engine.runtime['events'] if e['kind'] == 'task_assessment_invalidated']
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]['target'], 'TK-1')
        self.assertTrue(any(events[0]['id'] in a.get('event_refs', []) for a in engine.runtime['queue']))

    def test_initial_preparation_owns_initial_events_until_accepted(self):
        engine = Sim.activated().engine
        first = next(a for a in engine.runtime['queue'] if a['role'] == 'research_preparation')
        self.assertEqual(set(first.get('event_refs', [])), set(engine.runtime['pending_events']))
        engine._refresh_readiness()
        self.assertFalse(any(a['role'] == 'research_plan' for a in engine.runtime['queue']))
        self.assertTrue(engine.runtime['pending_events'], 'Assignment is not consumption')

    def test_normal_dispatch_occupancy_does_not_request_a_new_plan(self):
        sim = Sim.activated()
        clear_work(sim)
        engine = sim.engine
        row = task(engine)
        engine._refresh_readiness()
        engine.runtime['queue'] = [{'id': 'AC-work', 'role': 'research_work', 'target': row['id']}]
        engine.runtime['pending_events'] = []
        engine._refresh_readiness()
        self.assertFalse(any(a['role'] == 'research_plan' for a in engine.runtime['queue']))
        self.assertTrue(engine._task_readiness[row['id']].get('dispatch_occupied'))
        engine.instance['grants'][research_grant(engine)]['status'] = 'revoked'
        engine._refresh_readiness()
        self.assertTrue(any(a['role'] == 'research_plan' for a in engine.runtime['queue']),
                        'Actual authority loss during occupancy still needs planning')


class MachineAdmissionTests(unittest.TestCase):
    """An active Sim whose host constraint is approved by a public configure: jobs 4, 512 MiB and 80 % CPU,
    with a control reserve of one job, 128 MiB and 20 %; every capped role demands one job, 128 MiB and 20 %.

    The configuration caps the AI roles and ``external_action``, which runs in the
    owner's thread; the Lean roles run as native Jobs and are uncapped
    (``execution_profiles.UNCAPPED_ROLES``, ``launch.ticket``). So host admission is
    seen on ``external_action``, a machine Job's start on ``formal_check``, and the
    capacity an unconfirmed Job holds on a capped native Job, AI research work.
    """

    def setUp(self):
        self.sim = Sim.activated()
        clear_work(self.sim)
        constraint = host_constraint(host_id=platform.node(),
                                     limits={'jobs': 4, 'memory_bytes': 512 * MiB, 'cpu_rate_basis_points': 8000},
                                     control_reserve={'jobs': 1, 'memory_bytes': 128 * MiB, 'cpu_rate_basis_points': 2000},
                                     authority_refs=['configuration:request'])
        demands = {role: {'jobs': 1, 'memory_bytes': 128 * MiB, 'cpu_rate_basis_points': 2000} for role in HOST_ROLES}
        applied(self.sim, 'configure', config={'host_resources': {'constraint': constraint, 'demands_by_role': demands}})
        self.engine = self.sim.engine

    def register(self, eid, role='external_action', status='running'):
        action = {'id': 'AC-' + eid[3:], 'role': role, 'target': 'EO-one' if role == 'external_action' else 'KN-one'}
        return action, self.engine._register_execution(action, {'id': eid, 'status': status, 'role': role})

    def hold_job(self, name):
        """A launched Job of ``name`` that has not ended: its local termination is unconfirmed."""
        held = ['fixture-held-job', '--never-resumed']
        self.sim.jobs.programs.insert(0, (lambda argv: argv == held, lambda argv, cwd, env: 0))
        self.sim.jobs.launch(held, name=name)

    def test_common_machine_admission_reserves_before_start_and_refuses_without_execution(self):
        engine = self.engine
        for index in range(3):
            _, execution = self.register(f'EX-machine-{index}')
            self.assertEqual(execution['status'], 'starting')
            self.assertEqual(len(execution['capacity']['reservation_ids']), 3)
            self.assertIsNone(execution['capacity']['provider'])
        action = {'id': 'AC-refused', 'role': 'external_action', 'target': 'EO-one'}
        engine.runtime['queue'].append(action)
        self.assertIsNone(engine._register_execution(action, {'id': 'EX-refused', 'status': 'running', 'role': 'external_action'}))
        self.assertNotIn('EX-refused', engine.runtime['executions'])
        self.assertEqual(engine.runtime['activities'][action['owner_activity_id']]['status'], 'waiting')
        self.assertEqual(len(engine.runtime['reservations']), 9)
        engine._local_call_returned('EX-machine-0', {'launch_not_created': True})
        self.assertTrue(engine._session_slots().release('EX-machine-0', reason='explicit local start failure'))
        retry = engine._register_execution(action, {'id': 'EX-retry', 'status': 'running', 'role': 'external_action'})
        self.assertEqual(retry['status'], 'starting')

    def test_machine_callback_seals_process_before_resume_and_keeps_uncertain_capacity(self):
        engine = self.engine
        _, execution = self.register('EX-one', 'formal_check', 'starting')
        self.assertEqual(execution['status'], 'starting')
        identity = {'job_name': execution['launch_ticket']['job_name'], 'pid': 17, 'creation_filetime': '12345'}

        def published(arguments):
            row = arguments['self'].runtime['executions']['EX-one']
            return deepcopy((row['capacity']['process'], row['status']))
        with ObservedCalls(save=ResearchEngine._save, capture={'save': published}) as observed:
            engine._machine_started('EX-one', identity)
        self.assertEqual(observed.captured('save'), [(identity, 'running')])
        self.hold_job(identity['job_name'])
        execution = engine.runtime['executions']['EX-one']
        self.assertFalse(release_or_hold(execution, engine._session_slots(), at=self.sim.clock.now()))
        self.assertEqual(execution['status'], 'stopping')
        self.assertEqual(execution['error'], 'Local Job termination is unconfirmed; capacity and output remain held for recovery.')

    def test_unconfirmed_job_termination_keeps_its_host_and_slot_reservations(self):
        engine = self.engine
        refs = engine.instance['role_profile_refs']['research_work']
        profile = next(engine.instance['execution_profiles'][ref['id']] for ref in refs
                       if engine.instance['execution_profiles'][ref['id']]['ai']['tier'] == 'high')
        at = self.sim.clock.now()
        open_activity(engine.runtime, activity_id='AY-work', activity_kind='research_work', owner_ref=engine.instance['id'],
                      input_refs=[], opened_at=at)
        execution = create_execution(execution_id='EX-work', owner_activity_id='AY-work', actor_kind='ai',
                                     input_manifest=[], profile_ref=profile_ref(profile), created_at=at)
        execution.update(role='research_work', input_snapshot=engine.head,
                         action={'id': 'AC-work', 'role': 'research_work', 'profile_ref': profile_ref(profile)})
        transition_execution(execution, 'starting', at=at)
        assign_execution(engine.runtime, 'AY-work', execution)
        slots = engine._session_slots()
        self.assertTrue(slots.acquire('EX-work', profile=profile, execution=execution))
        held = engine.runtime['executions']['EX-work']['capacity']['reservation_ids']
        self.assertEqual(sorted(engine.runtime['reservations'][rid]['unit'] for rid in held),
                         ['cpu_rate_basis_points', 'execution', 'jobs', 'memory_bytes'])
        identity = {'job_name': execution['launch_ticket']['job_name'], 'pid': 31, 'creation_filetime': '12345'}
        slots.started('EX-work', identity, at=at)
        self.hold_job(identity['job_name'])
        execution = engine.runtime['executions']['EX-work']
        self.assertFalse(release_or_hold(execution, engine._session_slots(), at=self.sim.clock.now()))
        self.assertEqual(execution['status'], 'stopping')
        self.assertEqual(execution['error'], 'Local Job termination is unconfirmed; capacity and output remain held for recovery.')
        self.assertEqual([engine.runtime['reservations'][rid]['state'] != 'settled' for rid in held], [True] * 4)

    def test_actual_git_snapshot_binds_machine_reservations_and_start_identity(self):
        engine = self.engine
        with engine.store.writer_lock():
            self.register('EX-machine')
            self.register('EX-formal', 'formal_check', 'starting')
            engine._save()
            admitted = engine.head
            _, _, staged = engine.store.load(admitted)
            self.assertEqual(staged['executions']['EX-machine']['status'], 'starting')
            self.assertEqual(sorted(row['owner_id'] for row in staged['reservations'].values()), ['EX-machine'] * 3)
            self.assertEqual(staged['executions']['EX-formal']['status'], 'starting')
            # The Job identity is a double; both pre-resume publications and the host
            # reservation records use the storage contract and the store's compare-and-swap.
            identity = {'job_name': engine.runtime['executions']['EX-formal']['launch_ticket']['job_name'],
                        'pid': 29, 'creation_filetime': '123456789012345678'}
            engine._machine_started('EX-formal', identity)
            _, _, started = engine.store.load(engine.head)
            self.assertNotEqual(engine.head, admitted)
            self.assertEqual(started['executions']['EX-formal']['capacity']['process'], identity)
            self.assertEqual(started['executions']['EX-formal']['status'], 'running')


class OperatingQueueTests(unittest.TestCase):
    def test_user_requests_and_intent_join_existing_operating_queue_in_order(self):
        sim = Sim.activated()
        clear_work(sim)
        sim.engine._enqueue('maintenance', reason='older operating request')
        sim.engine._save()
        sim.control('request', config={'role': 'research_preparation'}, text='new preparation request')
        sim.control('input', text='new information to interpret')
        sim.engine.process_controls()
        self.assertEqual([a['role'] for a in sim.runtime['queue']],
                         ['maintenance', 'research_preparation', 'intent_interpretation'])

    def test_run_that_starts_under_a_maintenance_fence_returns_without_an_execution(self):
        # The owner loop meets the fence in its first pass, before the loop's stopping check.
        sim = Sim.activated()
        sim.control('quiesce', text='fixture installation maintenance')
        sim.restart()
        sim.engine.process_controls()
        self.assertEqual(sim.runtime['maintenance_fence']['state'], 'quiescent')
        executions = deepcopy(sim.runtime['executions'])
        sim.engine.run(max_steps=1)
        self.assertEqual(sim.runtime['maintenance_fence']['state'], 'quiescent')
        self.assertEqual(sim.runtime['executions'], executions)


if __name__ == '__main__':
    unittest.main()
