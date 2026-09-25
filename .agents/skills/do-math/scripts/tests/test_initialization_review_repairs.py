"""Cross-boundary regressions from the first real initialization/handoff trace."""
from copy import deepcopy
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math import activities, execution_profiles, model_policy, operational_dispositions, planning, repair_execution
from do_math.initialization import governance_working_view
from test_lifecycle_engine import AdapterDouble, FakeEngine


class WorkProfileAdmissionTests(unittest.TestCase):
    def test_policy_change_reprepares_an_unstarted_incompatible_contract(self):
        with tempfile.TemporaryDirectory() as directory, patch('do_math.initialization.adapter_for', return_value=AdapterDouble()):
            engine=FakeEngine(directory);engine.activate()
            task=engine.task(approved=False)
            task['model_assessment']={'difficulty':'low','importance':'low','reason':'local'}
            low=next(p for p in engine.instance['execution_profiles'].values()
                     if p['role']=='research_work' and p['ai']['tier']=='low')
            task['profile_refs']=[execution_profiles.profile_ref(low)];engine.approve(task)
            engine.instance['config']['role_tiers']['research_work']='high'
            engine._refresh_readiness()
            self.assertEqual(engine._task_readiness[task['id']]['state'],'not_ready')
            self.assertTrue(any(a['role']=='research_preparation' and a.get('target')==task['id']
                                for a in engine.runtime['queue']))
            self.assertFalse(any(a['role']=='task_contract_review' and a.get('target')==task['id']
                                 for a in engine.runtime['queue']))

    def test_reviewed_contract_cannot_be_ready_with_an_inadequate_allowed_profile(self):
        with tempfile.TemporaryDirectory() as directory, patch('do_math.initialization.adapter_for', return_value=AdapterDouble()):
            engine = FakeEngine(directory)
            engine.activate()
            task = engine.task(approved=False)
            task['model_assessment'] = {'difficulty':'low', 'importance':'high', 'reason':'goal-critical'}
            low = next(p for p in engine.instance['execution_profiles'].values()
                       if p['role']=='research_work' and p['ai']['tier']=='low')
            task['profile_refs'] = [execution_profiles.profile_ref(low)]
            engine.approve(task)
            result = planning.task_ready(task, governance_working_view(engine.instance), engine.runtime)
            self.assertEqual(result['state'], 'not_ready')
            self.assertIn('work profile requirement', result['errors'][0])
            high = next(p for p in engine.instance['execution_profiles'].values()
                        if p['role']=='research_work' and p['ai']['tier']=='high')
            task['profile_refs'] = [execution_profiles.profile_ref(high)]
            engine.approve(task)
            self.assertEqual(planning.task_ready(task, governance_working_view(engine.instance), engine.runtime)['state'], 'ready')
            self.assertEqual(model_policy.work_profile_selection(engine.instance['config'], task,
                engine.instance['execution_profiles'])['profile_ref'], task['profile_refs'][0])


class RecoveryOwnershipTests(unittest.TestCase):
    def runtime(self, status='running', *, successor=True):
        target={'id':'EX-old','status':'ended','owner_activity_id':'AY-one',
                'action':{'id':'AC-one','role':'research_plan'},'error':'returned'}
        runtime={'executions':{'EX-old':target},'activities':{},'queue':[],'operational_dispositions':{}}
        if successor:
            runtime['executions']['EX-new']={'id':'EX-new','status':status,'owner_activity_id':'AY-one',
                'continuation_of':'EX-old','action':{'id':'AC-one','role':'research_plan'}}
        return runtime

    def record(self, kind='retry'):
        return {'id':'OD-one','status':'applied','target_execution_id':'EX-old',
                'disposition':{'kind':kind}}

    def test_live_and_ended_successors_supersede_old_retry_and_resume(self):
        for kind in ('retry','resume'):
            for status in ('starting','running','ended'):
                with self.subTest(kind=kind,status=status):
                    runtime=self.runtime(status)
                    record=self.record(kind)
                    self.assertTrue(operational_dispositions.reconcile_recovery(runtime,record))
                    self.assertEqual(record['status'],'superseded')
                    self.assertEqual(runtime['queue'],[])
                    self.assertEqual(runtime['executions']['EX-old']['error'],'returned')

    def test_unrelated_success_cannot_supersede_failure(self):
        runtime=self.runtime('ended')
        runtime['executions']['EX-new']['owner_activity_id']='AY-other'
        self.assertIsNone(activities.successor_state(runtime,'EX-old'))
        self.assertFalse(operational_dispositions.reconcile_recovery(runtime,self.record()))

    def test_queued_continuation_already_owns_recovery(self):
        runtime=self.runtime(successor=False)
        runtime['queue']=[{'id':'AC-one','continuation_of':'EX-old','owner_activity_id':'AY-one'}]
        before=deepcopy(runtime)
        self.assertTrue(operational_dispositions.reconcile_recovery(runtime,self.record()))
        self.assertEqual(runtime,before)

    def test_task_continuation_does_not_discharge_a_separate_installation_defect(self):
        runtime=self.runtime()
        runtime['executions']['EX-other']={'id':'EX-other','status':'ended','owner_activity_id':'AY-other'}
        old={**self.record('repair'),'status':'installation_repair_pending'}
        current={**old,'id':'OD-other','target_execution_id':'EX-other'}
        runtime['operational_dispositions']={old['id']:old,current['id']:current}
        self.assertEqual(repair_execution.pending_installation_repair(runtime),old)
        self.assertFalse(operational_dispositions.reconcile_recovery(runtime,old))

    def test_successful_installation_repair_preserves_the_existing_continuation(self):
        runtime=self.runtime()
        record={**self.record('repair'),'status':'installation_repair_pending'}
        result=repair_execution.resume_installation_repair(runtime,record,repaired_by='EX-repair',at='2026-09-25T00:00:00Z')
        self.assertIsNone(result)
        self.assertEqual(runtime['queue'],[])
        self.assertEqual(record['status'],'applied')
        self.assertEqual(record['result']['installation_repair']['successor']['live_execution_ids'],['EX-new'])

    def test_already_applied_retry_keeps_its_receipt(self):
        record={**self.record(),'result':{'continuation_action_id':'AC-one'}}
        self.assertFalse(operational_dispositions.reconcile_recovery(self.runtime(),record))
        self.assertEqual(record['status'],'applied')


class ApprovalDraftTests(unittest.TestCase):
    def test_exact_draft_reaches_existing_consumer_without_mutating_source_state(self):
        from test_redesign_GOVERNANCE import AuditRepairTests
        from do_math import governance
        instance,runtime,bundle,request=AuditRepairTests().checked_import()
        before=deepcopy((instance,runtime))
        draft=governance.import_approval_draft(instance,runtime,bundle['id'])
        self.assertEqual(draft,request['config'])
        self.assertEqual((instance,runtime),before)
        updated,state,receipt=governance.apply_import_control(instance,runtime,{**request,'config':draft})
        self.assertEqual(receipt['status'],'applied')
        broken=deepcopy(runtime)
        broken['intent_imports'][bundle['id']]['check']['scope_complete']=False
        with self.assertRaises(ValueError):
            governance.import_approval_draft(instance,broken,bundle['id'])


if __name__=='__main__':
    unittest.main()
