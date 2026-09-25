"""Actual TASKS mixins retain revision ownership through delegation and retry.

The harness supplies only queue storage; no provider or Git behavior is mocked as
an end-to-end result. Central dispatch/serialization remains the MAIN regression.
"""
from copy import deepcopy
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from do_math import planning,revisions
from do_math.revision_engine import RevisionEngineMixin
from do_math.decision_engine import DecisionEngineMixin
from test_redesign_TASKS import approved_fixture,approve,disposition


class OwnerHarness(RevisionEngineMixin,DecisionEngineMixin):
    def __init__(self):
        task,self.instance,self.runtime=approved_fixture()
        self.runtime['waiting_actions']={}
        self.counter=0

    def _remove_action(self,action):
        self.runtime['queue'][:]=[a for a in self.runtime['queue'] if a.get('id')!=action.get('id')]

    def _enqueue(self,role,target=None,**fields):
        self.counter+=1
        action={'id':'AC-'+str(self.counter),'role':role,**fields}
        if target:action['target']=target
        self._bind_revision_action(action)
        self.runtime['queue'].append(action)
        return action


class RevisionObligationTests(unittest.TestCase):
    def test_closed_target_does_not_erase_other_targets_or_merged_new_request(self):
        h=OwnerHarness();other=deepcopy(h.runtime['tasks']['TK-1']);other['id']='TK-2'
        h.runtime['tasks']['TK-2']=other
        a=h._enqueue('research_preparation',revision_targets=revisions.capture_targets(h.instance,h.runtime,['TK-1','TK-2']))
        h.runtime['tasks']['TK-1']['status']='closed';h._retire_closed_revision_targets()
        self.assertEqual(set(a['revision_targets']),{'TK-2'})
        a['unbound_request']=True
        h.runtime['tasks']['TK-2']['status']='closed';h._retire_closed_revision_targets()
        self.assertEqual(h.runtime['queue'],[a]);self.assertEqual(a['revision_targets'],{})
        a['revision_targets']={'TK-2':{}};a['unbound_request']=False
        h._retire_closed_revision_targets();self.assertEqual(h.runtime['queue'],[])

    def test_revision_blocks_consumer_but_independent_work_can_overlap(self):
        h=OwnerHarness();a=h.runtime['tasks']['TK-1']
        b=deepcopy(a);b.update(id='TK-B',inputs=['TK-1'],reviews=[]);h.runtime['tasks']['TK-B']=b
        c=deepcopy(a);c.update(id='TK-C',reviews=[]);h.runtime['tasks']['TK-C']=c
        writer=h._enqueue('research_preparation','TK-1')
        read={'id':'AC-B','role':'research_work','target':'TK-B'}
        independent={'id':'AC-C','role':'research_work','target':'TK-C'}
        self.assertTrue(planning.revision_waits(read,h.instance,h.runtime))
        self.assertEqual(planning.revision_waits(independent,h.instance,h.runtime),[])
        h.runtime['executions']['EX-reader']={'id':'EX-reader','status':'running','action':read}
        self.assertTrue(planning.revision_waits(writer,h.instance,h.runtime))
        h.runtime['executions']['EX-reader']['status']='ended'
        self.assertEqual(planning.revision_waits(writer,h.instance,h.runtime),[])

    def delegated(self):
        h=OwnerHarness();h.instance['knowledge']={'KN-source':{'id':'KN-source','revision':1,'statement':'old'}}
        parent=h._enqueue('research_preparation',revision_targets=revisions.capture_targets(h.instance,h.runtime,['KN-source'],required=True))
        task=h.runtime['tasks']['TK-1'];task.update(title='Correct source',producer_execution='EX-prep',knowledge_revision_targets=['KN-source'])
        h.runtime['executions']['EX-prep']={'id':'EX-prep','role':'research_preparation','status':'ended',
            'extensions':{'revision_resolutions':[{'record_id':'KN-source','disposition':'delegated','task_title':'Correct source','reason':'research replacement'}]}}
        h._apply_revision_followup(parent,{'summary':'delegate research'},'EX-prep');h._remove_action(parent)
        return h,parent

    def test_delegated_work_and_review_do_not_block_on_own_obligation(self):
        h,parent=self.delegated();entry=h.runtime['waiting_actions'][parent['id']]
        self.assertEqual(entry['delegated_targets'],{'KN-source':'TK-1'})
        review={'id':'AC-review','role':'task_contract_review','target':'TK-1'}
        self.assertEqual(planning.revision_waits(review,h.instance,h.runtime),[])
        work=h._enqueue('research_work','TK-1')
        self.assertIn('KN-source',work['revision_targets'])
        self.assertEqual(planning.revision_waits(work,h.instance,h.runtime),[])
        h.runtime['executions']['EX-work']={'id':'EX-work','role':'research_work','status':'ended','extensions':{
            'knowledge_changes':[{'id':'KN-source'}],
            'revision_resolutions':[{'record_id':'KN-source','disposition':'revised','reason':'authored correction'}]}}
        h.instance['knowledge']['KN-source']['revision']=2
        h._apply_revision_followup(work,{'summary':'correction','outcome':'submitted'},'EX-work')
        self.assertNotIn(parent['id'],h.runtime['waiting_actions'])
        self.assertEqual(h.runtime['tasks']['TK-1']['status'],'waiting')
        self.assertEqual(h.runtime['tasks']['TK-1']['waiting']['next_owner'],'research_plan')

    def test_maintenance_can_read_pending_revisions_and_cycles(self):
        h,parent=self.delegated()
        maintenance={'role':'maintenance','id':'AC-check','target':'KN-source'}
        self.assertEqual(planning.revision_waits(maintenance,h.instance,h.runtime),[])
        self.assertEqual([(row['state'],set(row['action']['revision_targets'])) for row in planning.pending_revisions(h.runtime)],[('waiting',{'KN-source'})])
        self.assertEqual(planning.revision_cycles(h.instance,h.runtime),[])

    def test_closed_delegate_keeps_obligation_for_new_preparer(self):
        h,parent=self.delegated();h.runtime['tasks']['TK-1']['status']='closed';h.runtime['queue']=[]
        h.runtime['waiting_actions']['failed-child']={'kind':'execution_failure','action':{
            'id':'failed-child','role':'research_work','target':'TK-1','revision_targets':revisions.capture_targets(h.instance,h.runtime,['KN-source'])}}
        h._retire_closed_revision_targets();h._reconcile_revision_delegations()
        self.assertNotIn('failed-child',h.runtime['waiting_actions'])
        entry=h.runtime['waiting_actions'][parent['id']]
        self.assertEqual(set(entry['revision_targets']),{'KN-source'});self.assertFalse(entry['delegated_targets'])
        new=h._enqueue('research_preparation',revision_targets=revisions.capture_targets(h.instance,h.runtime,['KN-source']))
        self.assertIn(parent['id'],new['revision_parent_ids'])
        self.assertEqual(planning.revision_waits(new,h.instance,h.runtime),[])
        self.assertEqual(planning.revision_cycles(h.instance,h.runtime),[])

    def test_plan_selection_and_predispatch_use_actual_current_input(self):
        h=OwnerHarness();h.runtime['executions']['EX-plan']={'id':'EX-plan','role':'research_plan','status':'ended'}
        plan={'dispositions':[disposition('TK-1')],'task_assessments':[],'preparation_requests':[]}
        h._apply_task_plan(plan,'EX-plan',deepcopy(h.runtime['tasks']),['TK-1'])
        action=next(a for a in h.runtime['queue'] if a['role']=='research_work')
        self.assertTrue(h._selected_action_current(action))
        h.instance['sources'][0]['sha256']='b'*64
        self.assertFalse(h._selected_action_current(action))
        self.assertFalse(any(a['role']=='research_work' for a in h.runtime['queue']))
        self.assertTrue(any(a['role']=='research_plan' for a in h.runtime['queue']))
        from do_math.engine import ResearchEngine
        from do_math.governance import governance_view
        from research_fixtures import contract_review
        h._governance = lambda: governance_view(h.instance)
        h._governance_revisions = ResearchEngine._governance_revisions.__get__(h)
        task = h.runtime['tasks']['TK-1']
        review_action = {'role': 'task_contract_review', 'target': task['id']}
        ResearchEngine._apply(h, review_action, contract_review({'task': task}),
                             'EX-fresh-review', owns_response=False)
        self.assertNotIn('waiting', task)
        self.assertEqual(planning.task_ready(task, h.instance, h.runtime)['state'], 'ready')
        task['waiting'] = {'kind': 'external_event', 'next_owner': 'user'}
        ResearchEngine._apply(h, review_action, contract_review({'task': task}),
                             'EX-other-review', owns_response=False)
        self.assertEqual(task['waiting'], {'kind': 'external_event', 'next_owner': 'user'})
        self.assertEqual(planning.task_ready(task, h.instance, h.runtime)['state'], 'not_ready')

    def test_revision_cannot_omit_target_or_cancel_required_repair_as_unchanged(self):
        h=OwnerHarness();task=h.runtime['tasks']['TK-1']
        action={'role':'research_preparation','revision_targets':revisions.capture_targets(h.instance,h.runtime,['TK-1'],required=True)}
        context={'action':action,'tasks':[task]}
        self.assertTrue(revisions.submission_errors({}, {},context))
        extension={'revision_resolutions':[{'record_id':'TK-1','disposition':'unchanged','reason':'skip'}]}
        self.assertTrue(revisions.submission_errors({},extension,context))
        extension['revision_resolutions'][0]['disposition']='revised'
        self.assertEqual(revisions.submission_errors({'candidates':[{'title':'revision','revises_task_id':'TK-1'}]},extension,context),[])


if __name__=='__main__':unittest.main(verbosity=2)
