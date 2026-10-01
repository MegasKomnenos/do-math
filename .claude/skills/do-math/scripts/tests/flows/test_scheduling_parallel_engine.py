"""Scheduling through the owner loop with model calls: parallel work, model capacity, plans and call deadlines.

Every scene runs model calls through the worker on a Sim (over the 2 s Sim
budget). Ready work is ``support.scheduling_parallel.ready_work_sim``; the
active start is the default activation, with its activation work cleared where
the legacy test started from the synthetic active state's empty queue.
"""
from copy import deepcopy
import threading
import unittest

from do_math.engine import ResearchEngine
from do_math.execution_profiles import WORK_ROLES
from do_math.model_policy import LIMITS, MODELS
from do_math.model_runner import ModelRunner
from support.role_answers import candidate
from support.default_responder import DefaultResponder, common
from support.engine_lifecycle import applied, clear_work
from support.provider_probes import ObservedCalls
from support.scheduling_initial import GRANT
from support.scheduling_model import native_final, scenario_model
from support.scheduling_parallel import Overlap, ready_work_sim, round_robin
from support.sim import Sim, warm_template

def setUpModule():
    warm_template()
    for count in (1, 2, 3):
        ready_work_sim(count)


LOW ={'difficulty': 'low', 'importance': 'low', 'reason': 'a local bounded comparison with an explicit method'}


def configure_limits(sim, limits):
    """A public configure of ``limits`` and the probe decision that observes the new AI editions' capabilities."""
    applied(sim, 'configure', config={'session_limits': limits})
    refs = [ref for rows in sim.instance['role_profile_refs'].values() for ref in rows
            if sim.instance['execution_profiles'][ref['id']]['actor_kind'] == 'ai']
    applied(sim, 'decision', config={'change': {'kind': 'initialization', 'operation': 'probe', 'profile_refs': refs}})


def run_models():
    """Observe the model of every runner call."""
    return ObservedCalls(run=ModelRunner.run, capture={'run': lambda arguments: arguments['model']})


def executions(sim, role):
    return [row for row in sim.runtime['executions'].values() if row['role'] == role]


class ParallelWorkTests(unittest.TestCase):
    def test_three_calls_overlap_and_apply_serially_to_distinct_workspaces(self):
        """About 7 s: three research work calls through the worker, each waiting until all three are in flight."""
        sim = ready_work_sim(3)
        sim.ports.calls.choose = round_robin()
        overlap = Overlap(sim, 3)
        scenario_model(sim).during('research_work', overlap)
        main = threading.get_ident()
        with ObservedCalls(save=ResearchEngine._save, run=ModelRunner.run,
                           capture={'save': lambda arguments: threading.get_ident(),
                                    'run': lambda arguments: arguments['model']}) as observed:
            state = sim.engine.run(max_steps=3)
        self.assertEqual(set(observed.captured('save')), {main})
        # Every call saw all three in flight before it answered: none returned before the last one started.
        self.assertEqual(overlap.waited_out, [True] * 3)
        self.assertEqual(overlap.peak, 3)
        self.assertEqual(len(set(overlap.workspaces)), 3)
        self.assertEqual(observed.captured('run'), [MODELS['high']] * 3)
        self.assertEqual(len({(p / 'same-name.txt').read_text(encoding='utf-8') for p in overlap.workspaces}), 3)
        self.assertEqual(len([e for e in executions(sim, 'research_work') if e.get('outcome') == 'output_accepted']), 3)
        self.assertEqual(state['budget'][MODELS['high']]['used'], 0)
        checked = sim.engine.check()
        self.assertEqual(checked['errors'], [], checked)
        # Every persisted-state area is clean, so the check passes; live trust
        # files are outside the snapshot the inspection reads.
        self.assertEqual(checked['inspection']['not_checked'], [], checked)
        self.assertEqual(checked['inspection']['findings'], [], checked)
        self.assertTrue(checked['passed'], checked)

    def test_planner_queue_order_cancels_only_unstarted_requests_and_preserves_obligations(self):
        """Over the 2 s Sim budget by its start state only: the three-task ready work template."""
        sim = ready_work_sim(3)
        engine = sim.engine
        engine._refresh_readiness()
        first, second, third = deepcopy(engine.runtime['queue'])
        engine.runtime['executions']['EX-plan'] = {'input_snapshot': engine.head, 'status': 'ended', 'extensions': {
            'queued_requests': [{'request_id': third['id'], 'decision': 'keep', 'reason': 'opens the next proof question'},
                                {'request_id': first['id'], 'decision': 'keep', 'reason': 'follow after third'},
                                {'request_id': second['id'], 'decision': 'cancel', 'reason': 'defer this approach'}]}}
        engine._apply_queue_plan('EX-plan')
        self.assertEqual([a['id'] for a in engine.runtime['queue']], [third['id'], first['id']])
        task = engine.runtime['tasks'][second['target']]
        self.assertEqual(task['status'], 'planned')
        self.assertEqual([row['id'] for row in task['completion_obligations']], ['OB-argument'])


class ModelCapacityTests(unittest.TestCase):
    def test_unavailable_assigned_model_waits_without_spending_other_model_slots(self):
        """About 4 s: capacity configured by control around one research work call."""
        sim = ready_work_sim(1)
        limits = deepcopy(LIMITS)
        limits['work'][MODELS['high']] = 0
        configure_limits(sim, limits)
        scenario_model(sim)
        # One observation over both runs and the reconfiguration, as the legacy runner counted its models.
        with run_models() as observed:
            state = sim.engine.run(max_steps=1)
            self.assertEqual(state['status'], 'capacity_waiting')
            self.assertEqual(observed.captured('run'), [])
            self.assertEqual(state['capacity_waiting'][0]['model_selection']['model'], MODELS['high'])
            limits['work'][MODELS['high']] = 1
            configure_limits(sim, limits)
            sim.engine.run(max_steps=1)
        self.assertEqual(observed.captured('run'), [MODELS['high']])

    def test_blocked_high_priority_work_does_not_block_independent_low_model_work(self):
        """About 6 s: a real contract review and plan, then one research work call."""
        sim = ready_work_sim(2)
        limits = deepcopy(LIMITS)
        limits['work'][MODELS['high']] = 0
        configure_limits(sim, limits)
        engine = sim.engine
        high = engine.runtime['queue'][0]['target']
        task = engine.runtime['tasks'][engine.runtime['queue'][1]['target']]
        task['model_assessment'] = {'difficulty': 'low', 'importance': 'low', 'reason': 'bounded local transcription'}
        # Complete another real contract review after the model judgment changes.
        pending = deepcopy(engine.runtime['queue'])
        engine.runtime['queue'] = []
        engine._enqueue('task_contract_review', task['id'])
        scenario_model(sim, DefaultResponder())
        engine._save()
        sim.step()
        # The changed contract lost its selection; a real plan selects it again under
        # the new judgment while the high task's selected work waits for its model.
        engine = sim.engine
        engine.runtime['queue'] = [a for a in pending if a['target'] == high] + engine.runtime['queue']
        engine._save()
        sim.step()
        with run_models() as observed:
            sim.step()
        self.assertEqual(observed.captured('run'), [MODELS['low']])
        self.assertTrue(any(a.get('target') == high for a in sim.runtime['queue']))


class AssessmentFlowTests(unittest.TestCase):
    """The default activation: its own preparation, review and plan, answered with a low model rating."""

    def drive(self, sim, done):
        for _ in range(12):
            sim.step()
            if done(sim):
                return

    def test_model_assessments_flow_from_preparation_through_review_and_planning_to_execution(self):
        """About 8 s: preparation, contract review, plan and research work through the worker."""
        sim = Sim.activated()
        scenario_model(sim, DefaultResponder(model_rating=LOW))
        # Every assertion reads the first work execution and the submissions up to it.
        self.drive(sim, lambda s: any(e['status'] == 'ended' for e in executions(s, 'research_work')))
        tasks = list(sim.runtime['tasks'].values())
        self.assertEqual(tasks[0]['model_assessment'], LOW)
        work = executions(sim, 'research_work')
        self.assertTrue(work)
        self.assertEqual(work[0]['model'], MODELS['low'])
        self.assertEqual(work[0]['model_selection']['assessment'], LOW)
        inspection = sim.engine.check()
        self.assertEqual(inspection['errors'], [])
        self.assertEqual(inspection['submission_checks']['status'], 'verified')
        self.assertEqual(inspection['inspection']['not_checked'], [])
        self.assertEqual(inspection['inspection']['status'], 'healthy')

    def test_selected_task_without_a_plan_assessment_runs_at_its_reviewed_assessment(self):
        """About 7 s: receipt, plan application and dispatch each decide the unrated selection."""
        sim = Sim.activated()
        # The plan rates no selected task, so the receiver accepts it and dispatch reads the task record.
        scenario_model(sim, DefaultResponder(model_rating=LOW, plan_assessments=False))
        self.drive(sim, lambda s: bool(executions(s, 'research_work')))
        plans = executions(sim, 'research_plan')
        self.assertTrue(plans)
        self.assertEqual(plans[0].get('model_decisions'), {})
        work = executions(sim, 'research_work')
        self.assertTrue(work, [e.get('reason') for e in sim.runtime.get('waiting_actions', {}).values()])
        self.assertEqual(work[0]['model'], MODELS['low'])
        self.assertEqual(work[0]['model_selection']['assessment'], LOW)


class OperatingQueueTests(unittest.TestCase):
    def test_output_repair_keeps_the_original_operating_queue_position(self):
        """About 3 s: one preparation call through the worker."""
        sim = Sim.activated()
        engine = sim.engine
        # The newer request replaces activation's own preparation and keeps ownership
        # of its events; unowned events would schedule a plan into this queue.
        activation = next(a for a in engine.runtime['queue'] if a['role'] == 'research_preparation')
        # The older operating request carries the initialization-only grant, so its dispatch
        # check holds it in an active instance while the newer request runs.
        engine.runtime['queue'] = [{'id': 'AC-older', 'role': 'maintenance', 'reason': 'older operating request',
                                    'grant_id': GRANT},
                                   {'id': 'AC-preparation', 'role': 'research_preparation', 'reason': 'newer operating request',
                                    'event_refs': activation['event_refs']}]
        engine._save()
        invalid = common('research_preparation')
        invalid.pop('candidates')
        model = scenario_model(sim)
        model.on('research_preparation').reply(native_final(invalid))
        sim.step()
        self.assertEqual([call['role'] for call in model.calls], ['research_preparation'])
        self.assertEqual([a['id'] for a in sim.runtime['queue']], ['AC-older', 'AC-preparation'])
        self.assertEqual(sim.runtime['queue'][1]['repair_attempt'], 1)
        self.assertEqual(sim.runtime['queue'][0]['dispatch_wait']['reason'], 'initialization authority cannot authorize research')


class PlanOpeningTests(unittest.TestCase):
    """The default activation with its activation work cleared, so only the tested preparation can open a plan."""

    def prepare(self, candidates, *, ready_candidate=False):
        self.sim = sim = Sim.activated()
        clear_work(sim)
        self.assertEqual(sim.runtime['queue'], [])
        self.assertFalse(sim.runtime.get('pending_events'))
        if ready_candidate:
            scenario_model(sim, DefaultResponder(preparation_candidates=[candidate('deferred')]))
            sim.engine._enqueue('research_preparation', reason='Prepare a task that will await a decision')
            sim.engine._save()
            sim.engine.run(max_steps=2)
            self.assertTrue(any(row['state'] == 'ready' for row in sim.engine._task_readiness.values()))
        # Isolate the preparation trigger from previously queued plans. The task
        # and its approval remain actual receiver-created records.
        sim.engine.runtime['queue'] = []
        sim.engine._enqueue('research_preparation', reason='Explicit regression preparation')
        scenario_model(sim, DefaultResponder(preparation_candidates=candidates))
        sim.engine._save()
        sim.engine.run(max_steps=1)
        return sim

    def plans(self):
        return [a for a in self.sim.runtime['queue'] if a['role'] == 'research_plan']

    def test_new_contracts_awaiting_review_do_not_open_a_plan_with_nothing_to_decide(self):
        """About 3 s: one preparation call."""
        sim = self.prepare([candidate('one')])
        self.assertTrue(any(a['role'] == 'task_contract_review' for a in sim.runtime['queue']))
        self.assertEqual(self.plans(), [])

    def test_preparation_still_opens_a_plan_when_a_ready_task_awaits_a_decision(self):
        """About 5 s: two preparations and a contract review."""
        self.prepare([candidate('one')], ready_candidate=True)
        self.assertEqual(len(self.plans()), 1)

    def test_preparation_without_any_pending_review_still_opens_a_plan(self):
        """About 3 s: one preparation call."""
        self.prepare([])
        self.assertEqual(len(self.plans()), 1, self.plans())

    def test_a_running_review_of_the_same_contract_is_not_doubled_when_its_outside_premises_move(self):
        """About 3 s: one preparation call."""
        sim = Sim.activated()
        clear_work(sim)
        scenario_model(sim, DefaultResponder(preparation_candidates=[candidate('window')]))
        sim.engine._enqueue('research_preparation', reason='Prepare the contract under review')
        sim.engine._save()
        sim.step()
        engine = sim.engine
        running = next(a for a in engine.runtime['queue'] if a['role'] == 'task_contract_review')
        engine._register_execution(running, {'id': sim.clock.new_id('EX'), 'role': 'task_contract_review',
                                             'status': 'running', 'created_at': sim.clock.now(), 'input_snapshot': engine.head})
        engine._refresh_readiness()
        reviews = [a for a in engine.runtime['queue'] if a['role'] == 'task_contract_review']
        self.assertEqual([a['id'] for a in reviews], [running['id']],
                         'the finished review\'s own currentness check decides whether another review is needed')


class TaskAdmissionTests(unittest.TestCase):
    def test_public_task_flow_keeps_observation_and_state_contracts_consistent(self):
        """About 10 s: preparation, contract review, plan and research work through the worker."""
        sim = Sim.activated()
        clear_work(sim)
        applied(sim, 'configure', config={'plan_settle_seconds': 1})
        refs = [ref for rows in sim.instance['role_profile_refs'].values() for ref in rows
                if sim.instance['execution_profiles'][ref['id']]['actor_kind'] == 'ai']
        applied(sim, 'decision', config={'change': {'kind': 'initialization', 'operation': 'probe', 'profile_refs': refs}})
        scenario_model(sim, DefaultResponder())
        sim.engine._enqueue('research_preparation', reason='Exercise task admission after the approved initial fixture')
        sim.engine._save()
        before = set(sim.runtime['executions'])
        with ObservedCalls(admit=ResearchEngine._provider_admit) as observed:
            # Readiness events may open an extra plan; a step counts an action,
            # not one of the four conceptual research phases.
            sim.engine.run(max_steps=8)
        started = [row for eid, row in sim.runtime['executions'].items() if eid not in before and row['actor_kind'] == 'ai']
        self.assertEqual(observed.count('admit'), len(started))
        # A refused admission ends its attempt start_failed with this reason (call_engine).
        self.assertEqual([row['id'] for row in started if any(step.get('reason') == 'provider admission deferred'
                                                               for step in row.get('transitions', []))], [])
        work = executions(sim, 'research_work')
        self.assertTrue(work, {'tasks': sim.runtime['tasks'], 'queue': sim.runtime['queue'],
                               'waits': sim.runtime.get('waiting_actions')})
        self.assertTrue(work[0]['observation_rules'])
        report = sim.engine.check()
        self.assertEqual(report['errors'], [])
        # The initial interpretations are the public activation's own, with their role input manifests.
        self.assertEqual(report['inspection']['status'], 'healthy', report)
        self.assertEqual(report['inspection']['findings'], [], report)


class CallDeadlineTests(unittest.TestCase):
    def test_elapsed_time_does_not_block_the_next_execution_and_work_calls_have_no_timeout(self):
        """About 4 s: a preparation and a contract review through the worker."""
        sim = Sim.activated()
        clear_work(sim)
        sim.engine._enqueue('research_preparation', reason='Prepare a contract for the deadline regression')
        sim.engine._save()
        scenario_model(sim, DefaultResponder(preparation_candidates=[candidate('deadline regression')]))
        from support.provider_probes import ObservedCalls
        # Elapsed time belongs to the external provider process. Its real worker,
        # collector and ModelRunner still run; the work role has no call deadline.
        spawn = sim.model.spawn

        def start(command, **options):
            process = spawn(command, **options)
            communicate = process.communicate

            def completed(*args, **kwargs):
                result = communicate(*args, **kwargs)
                sim.advance(10000)
                return result
            process.communicate = completed
            return process
        sim.model.spawn = start
        with ObservedCalls(run=ModelRunner.run) as observed:
            sim.engine.run(max_steps=2)
        calls = observed.captured('run')
        self.assertEqual(len(calls), 2)
        self.assertEqual({call['profile']['role'] in WORK_ROLES for call in calls}, {True, False})
        for call in calls:
            if call['profile']['role'] in WORK_ROLES:
                self.assertIsNone(call['timeout_seconds'])
            else:
                self.assertGreater(call['timeout_seconds'], 0)
                self.assertLessEqual(call['timeout_seconds'], call['profile']['window']['call_timeout_seconds'])
        self.assertNotEqual(sim.runtime['status'], 'paused')


if __name__ == '__main__':
    unittest.main()
