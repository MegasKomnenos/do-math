"""Dispatch readiness on the real engine: plan settling, decision references, and host capacity by real reservation arithmetic.

The cases call the engine's own readiness steps (``dispatch_engine``,
``decision_engine``) on a Sim's active instance: the lifecycle gate, the
revision and currentness checks and the admission check all run as the
scheduler runs them. ``ModelCallTests`` drives the calls manager
(``parallel.ModelCalls``, layer 3) directly on a real thread.
"""
from copy import deepcopy
import platform
import threading
import time
import unittest

from jsonschema import Draft202012Validator

from do_math import execution_profiles as profiles
from do_math.parallel import ModelCalls
from do_math.record_schemas import RECORDS
from do_math.session_slots import SessionSlots
from support.engine_lifecycle import applied, clear_work
from support.sim import Sim, warm_template

setUpModule = warm_template
MiB = 1024 ** 2


def configure_host(sim):
    """The user's host approval: 4 jobs, 512 MiB, 80 % CPU with a control reserve of 1 job, 128 MiB, 20 %.

    Every capped role demands one job, 128 MiB and 20 %, so 3 jobs, 384 MiB and
    60 % can be lent to executions. Returns the adopted constraint.
    """
    constraint = profiles.host_constraint(
        host_id=platform.node(), limits={'jobs': 4, 'memory_bytes': 512 * MiB, 'cpu_rate_basis_points': 8000},
        control_reserve={'jobs': 1, 'memory_bytes': 128 * MiB, 'cpu_rate_basis_points': 2000},
        authority_refs=['configuration:request'])
    demands = {role: {'jobs': 1, 'memory_bytes': 128 * MiB, 'cpu_rate_basis_points': 2000} for role in profiles.HOST_ROLES}
    applied(sim, 'configure', config={'host_resources': {'constraint': constraint, 'demands_by_role': demands}})
    return sim.instance['capacity_constraints'][sim.instance['host_capacity_ref']]


def adopted_profile(instance, role):
    return instance['execution_profiles'][instance['role_profile_refs'][role][0]['id']]


class MachineSchedulingTests(unittest.TestCase):
    def test_plan_settle_action_survives_the_persisted_queue_contract(self):
        sim = Sim.activated()
        e = sim.engine
        self.assertEqual(e.instance['config']['plan_settle_seconds'], 300)
        e.runtime['queue'] = [{'role': 'task_contract_review'}]
        action = {'id': sim.clock.new_id('AC'), 'role': 'research_plan'}
        self.assertTrue(e._plan_settle_waits(action))
        Draft202012Validator(RECORDS['queue']).validate(action)
        self.assertEqual(action['dispatch_wait']['since'], action['settle_started_at'])
        self.assertEqual(action['dispatch_wait'], {'kind': 'plan_settle', 'since': action['settle_started_at'],
                                                   'limit_seconds': 300})

    def test_operational_review_of_targetless_preparation_has_only_real_references(self):
        sim = Sim.activated()
        e = sim.engine
        self.assertEqual(e.runtime['tasks'], {})
        e.runtime['executions']['EX-preparation'] = {
            'id': 'EX-preparation', 'action': {'role': 'research_preparation'},
            'decision_basis': {'records': [{'id': 'KN-basis', 'sha256': 'a' * 64}]}}
        refs = e._decision_references({'role': 'operational_review', 'target': 'EX-preparation'})
        self.assertEqual(refs, ['EX-preparation', 'KN-basis'])

    def test_blocked_machine_does_not_hide_a_smaller_ready_machine(self):
        sim = Sim.activated()
        clear_work(sim)
        constraint = configure_host(sim)
        e = sim.engine
        instance, runtime = e.instance, e.runtime
        # A synthetic state the product cannot make (no product edition caps a Lean role, and one role never
        # holds two editions): host-capped Lean editions beside the current uncapped ones. It takes the
        # admission's defensive path, which counts a capped machine edition's demands (session_slots._admission).
        big = profiles.with_host_resources(adopted_profile(instance, 'formal_check'), constraint,
                                           {'jobs': 1, 'memory_bytes': 384 * MiB, 'cpu_rate_basis_points': 6000})
        small = profiles.with_host_resources(adopted_profile(instance, 'trust_check'), constraint,
                                             {'jobs': 1, 'memory_bytes': 128 * MiB, 'cpu_rate_basis_points': 2000})
        for profile in (big, small):
            instance['execution_profiles'][profile['id']] = profile
            instance['role_profile_refs'][profile['role']].append(profiles.profile_ref(profile))
        slots = SessionSlots(runtime, instance, clock=sim.clock, jobs=sim.jobs)
        held = adopted_profile(instance, 'research_work')
        self.assertTrue(slots.acquire('EX-held', profile=held,
                                      execution={'id': 'EX-held', 'role': 'research_work', 'status': 'queued'}))
        queue = [{'id': 'AC-big', 'role': 'formal_check', 'target': 'KN-big', 'profile_ref': profiles.profile_ref(big)},
                 {'id': 'AC-small', 'role': 'trust_check', 'target': 'KN-small', 'profile_ref': profiles.profile_ref(small)}]
        before = deepcopy(runtime)

        def choose():
            return next((a for a in queue if e._dispatchable(a)), None)
        self.assertEqual(choose()['id'], 'AC-small')
        self.assertEqual(runtime, before, 'readiness must not reserve or create an execution')
        self.assertEqual(queue[0]['dispatch_wait']['kind'], 'host_capacity')
        self.assertTrue(slots.release('EX-held', reason='fixture: no process was created'))
        released = deepcopy(runtime)
        # 384 MiB and 60 % are exactly what the host lends: admission at the boundary.
        self.assertEqual(choose()['id'], 'AC-big')
        self.assertNotIn('dispatch_wait', queue[0])
        self.assertEqual(runtime, released)


def collected(calls, timeout):
    """Collect until one call finished or ``timeout`` seconds pass; whether one did."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if calls.collect():
            return True
        calls.wait(0.01)
    return bool(calls.collect())


class ModelCallTests(unittest.TestCase):
    def test_parallel_call_carries_a_distinct_execution_id(self):
        events = []
        caller = []

        class Runner:
            def run(self, **arguments):
                caller.append(threading.current_thread().name)
                arguments["on_started"]({"pid": 7})
                return {"status": "completed"}

        def operation():
            result = yield {"on_started": lambda observed: events.append(observed)}
            events.append(result)
        generator = operation()
        arguments = next(generator)
        calls = ModelCalls()
        try:
            future = calls.start_call(generator, Runner().run, arguments, execution_id="EX-1")
            self.assertEqual(future.execution_id, "EX-1")
            finished = collected(calls, 10)
            self.assertTrue(finished, "EX-1 did not complete; pending callbacks=" + str(calls.events.qsize()))
        finally:
            calls.close()
        self.assertEqual(events, [{"pid": 7}, {"status": "completed"}])
        self.assertEqual(caller, ["do-math-call"], "the runner ran on the call's own thread")


if __name__ == '__main__':
    unittest.main()
