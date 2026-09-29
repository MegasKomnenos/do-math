"""Host-capacity scheduling with real reservation arithmetic.

Lifecycle and input-currentness predicates are explicit preconditions here;
this test does not claim to validate authority or process termination.
"""
from copy import deepcopy
from pathlib import Path
import sys
import unittest
from unittest.mock import create_autospec
import time

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from do_math import execution_profiles as profiles
from do_math.session_slots import SessionSlots
from provider_fixtures import host_capacity_fixture
from research_fixtures import bare_engine
from do_math.parallel import ModelCalls


class MachineSchedulingTests(unittest.TestCase):
    def test_plan_settle_action_survives_the_persisted_queue_contract(self):
        from do_math.record_schemas import RECORDS
        from do_math.system_clock import new_id
        from jsonschema import Draft202012Validator
        scheduler = bare_engine({'config': {'plan_settle_seconds': 300}}, {'queue': [{'role': 'task_contract_review'}]})
        action = {'id': new_id('AC'), 'role': 'research_plan'}
        self.assertTrue(scheduler._plan_settle_waits(action))
        Draft202012Validator(RECORDS['queue']).validate(action)
        self.assertEqual(action['dispatch_wait']['since'], action['settle_started_at'])

    def test_operational_review_of_targetless_preparation_has_only_real_references(self):
        runtime = {'tasks': {}, 'executions': {'EX-preparation': {
            'id': 'EX-preparation', 'action': {'role': 'research_preparation'},
            'decision_basis': {'records': [{'id': 'KN-basis', 'sha256': 'a' * 64}]}}}}
        engine = bare_engine({}, runtime)
        refs = engine._decision_references({'role': 'operational_review', 'target': 'EX-preparation'})
        self.assertEqual(refs, ['EX-preparation', 'KN-basis'])

    def test_blocked_machine_does_not_hide_a_smaller_ready_machine(self):
        instance,selected,constraint=host_capacity_fixture()
        big=profiles.with_host_resources(selected['formal_check'],constraint,
            {'jobs':1,'memory_bytes':384*1024**2,'cpu_rate_basis_points':6000})
        original=next(p for p in instance['execution_profiles'].values() if p['role']=='trust_check')
        small=profiles.with_host_resources(original,constraint,
            {'jobs':1,'memory_bytes':128*1024**2,'cpu_rate_basis_points':2000})
        instance['execution_profiles'].update({p['id']:p for p in (big,small)})
        runtime={'tasks':{},'executions':{},'reservations':{}}
        slots=SessionSlots(runtime,instance)
        held=selected['research_work']
        self.assertTrue(slots.acquire('EX-held',
            profile=held,execution={'id':'EX-held','role':'research_work','status':'queued'}))
        scheduler=bare_engine(instance,runtime)
        scheduler._execution_profile=create_autospec(scheduler._execution_profile,
            side_effect=lambda action:profiles.resolve_profile(instance['execution_profiles'],action['profile_ref']))
        scheduler._action_lifecycle_gate=create_autospec(scheduler._action_lifecycle_gate,
            side_effect=lambda action:scheduler._execution_profile(action))
        scheduler._revision_dispatch_waits=create_autospec(scheduler._revision_dispatch_waits,return_value=[])
        scheduler._selected_action_current=create_autospec(scheduler._selected_action_current,return_value=True)
        scheduler._evaluation_context=create_autospec(scheduler._evaluation_context,return_value={})
        queue=[{'id':'AC-big','role':'formal_check','profile_ref':profiles.profile_ref(big)},
               {'id':'AC-small','role':'trust_check','profile_ref':profiles.profile_ref(small)}]
        before=deepcopy(runtime)
        choose=lambda:next((a for a in queue if scheduler._dispatchable(a)),None)
        self.assertEqual(choose()['id'],'AC-small')
        self.assertEqual(runtime,before,'readiness must not reserve or create an execution')
        self.assertEqual(queue[0]['dispatch_wait']['kind'],'host_capacity')
        self.assertTrue(slots.release('EX-held',reason='fixture: no process was created'))
        released=deepcopy(runtime)
        self.assertEqual(choose()['id'],'AC-big')
        self.assertNotIn('dispatch_wait',queue[0])
        self.assertEqual(runtime,released)


class ModelCallTests(unittest.TestCase):
    def test_parallel_call_carries_a_distinct_execution_id(self):
        events = []
        class Runner:
            def run(self, **arguments):
                arguments["on_started"]({"pid": 7})
                return {"status": "completed"}
        def operation():
            result = yield {"on_started": lambda observed: events.append(observed)}
            events.append(result)
        generator = operation(); arguments = next(generator)
        calls = ModelCalls()
        try:
            calls.start_call(generator, Runner().run, arguments, execution_id="EX-1")
            deadline = time.monotonic() + 10
            while not calls.collect():
                self.assertLess(time.monotonic(), deadline,
                    "EX-1 did not complete; pending callbacks=" + str(calls.events.qsize()))
                time.sleep(.01)
        finally:
            calls.close()
        self.assertEqual(events, [{"pid": 7}, {"status": "completed"}])


if __name__=='__main__': unittest.main()
