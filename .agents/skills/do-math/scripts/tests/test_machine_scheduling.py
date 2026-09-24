"""Host-capacity scheduling with real reservation arithmetic.

Lifecycle and input-currentness predicates are explicit preconditions here;
this test does not claim to validate authority or process termination.
"""
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from do_math import execution_profiles as profiles
from do_math.scheduler import SchedulerMixin
from do_math.session_slots import SessionSlots
from test_host_resources import fixture


class MachineSchedulingTests(unittest.TestCase):
    def test_plan_settle_action_survives_the_persisted_queue_contract(self):
        from do_math.record_schemas import RECORDS
        from do_math.repository import new_id
        from jsonschema import Draft202012Validator
        scheduler = SimpleNamespace(instance={'config': {'plan_settle_seconds': 300}},
            runtime={'queue': [{'role': 'task_contract_review'}]})
        action = {'id': new_id('AC'), 'role': 'research_plan'}
        self.assertTrue(SchedulerMixin._plan_settle_waits(scheduler, action))
        Draft202012Validator(RECORDS['queue']).validate(action)
        self.assertEqual(action['dispatch_wait']['since'], action['settle_started_at'])

    def test_operational_review_of_targetless_preparation_has_only_real_references(self):
        from do_math.decision_engine import DecisionEngineMixin
        runtime = {'tasks': {}, 'executions': {'EX-preparation': {
            'id': 'EX-preparation', 'action': {'role': 'research_preparation'},
            'decision_basis': {'records': [{'id': 'KN-basis', 'sha256': 'a' * 64}]}}}}
        engine = SimpleNamespace(instance={}, runtime=runtime)
        refs = DecisionEngineMixin._decision_references(engine,
            {'role': 'operational_review', 'target': 'EX-preparation'})
        self.assertEqual(refs, ['EX-preparation', 'KN-basis'])

    def test_blocked_machine_does_not_hide_a_smaller_ready_machine(self):
        instance,selected,constraint=fixture()
        big=profiles.with_host_resources(selected['formal_check'],constraint,
            {'jobs':1,'memory_bytes':384*1024**2,'cpu_rate_basis_points':6000})
        original=next(p for p in instance['execution_profiles'].values() if p['role']=='trust_check')
        small=profiles.with_host_resources(original,constraint,
            {'jobs':1,'memory_bytes':128*1024**2,'cpu_rate_basis_points':2000})
        instance['execution_profiles'].update({p['id']:p for p in (big,small)})
        runtime={'tasks':{},'executions':{},'reservations':{}}
        slots=SessionSlots(runtime,instance)
        held=selected['research_work']
        self.assertTrue(slots.acquire('EX-held',held['budget_kind'],held['ai']['model'],
            profile=held,execution={'id':'EX-held','role':'research_work','status':'queued'}))
        scheduler=SimpleNamespace(instance=instance,runtime=runtime,
            _action_lifecycle_gate=lambda action:None,
            _revision_dispatch_waits=lambda action:[],
            _selected_action_current=lambda action,**kwargs:True,
            _evaluation_context=lambda:{},
            _execution_profile=lambda action:profiles.resolve_profile(instance['execution_profiles'],action['profile_ref']))
        queue=[{'id':'AC-big','role':'formal_check','profile_ref':profiles.profile_ref(big)},
               {'id':'AC-small','role':'trust_check','profile_ref':profiles.profile_ref(small)}]
        before=deepcopy(runtime)
        choose=lambda:next((a for a in queue if SchedulerMixin._dispatchable(scheduler,a)),None)
        self.assertEqual(choose()['id'],'AC-small')
        self.assertEqual(runtime,before,'readiness must not reserve or create an execution')
        self.assertEqual(queue[0]['dispatch_wait']['kind'],'host_capacity')
        self.assertTrue(slots.release('EX-held',reason='fixture: no process was created'))
        released=deepcopy(runtime)
        self.assertEqual(choose()['id'],'AC-big')
        self.assertNotIn('dispatch_wait',queue[0])
        self.assertEqual(runtime,released)


if __name__=='__main__': unittest.main()
