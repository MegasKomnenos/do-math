"""Feature-five condition and planning regressions; no persisted-ready fixtures."""
from copy import deepcopy
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from do_math import planning
from test_redesign_TASKS import approved_fixture, approve


class ActivityConditionTests(unittest.TestCase):
    def test_activity_kind_uses_the_stored_activity_contract(self):
        from do_math.activities import open_activity
        runtime = {'activities': {}, 'executions': {}}
        open_activity(runtime, activity_id='AT-kind', activity_kind='research_work',
            owner_ref='TK-kind', input_refs=[], opened_at='2026-09-25T00:00:00Z')
        condition = {'op': 'record_field_equals', 'space': 'runtime', 'family': 'activity',
            'record_id': 'AT-kind', 'pointer': '/activity_kind', 'value': 'research_work'}
        planning.validate_condition(condition)
        self.assertEqual(planning.evaluate_condition(condition, {}, runtime)['state'], 'ready')
        self.assertEqual(planning.evaluate_condition(
            {**condition, 'value': 'maintenance'}, {}, runtime)['state'], 'not_ready')
        self.assertEqual(planning.evaluate_condition(
            {**condition, 'record_id': 'AT-missing'}, {}, runtime)['state'], 'not_ready')
        with self.assertRaisesRegex(ValueError, 'exposed machine field'):
            planning.validate_condition({**condition, 'pointer': '/role'})
class PlanningTests(unittest.TestCase):
    def setUp(self):
        self.task,self.instance,self.runtime=approved_fixture()
        self.instance['knowledge']={'K':{'id':'K','lifecycle':'active','value':1}}

    def condition(self,op='record_exists',**changes):
        return dict(op=op,space='research',family='knowledge',record_id='K',**changes)

    def test_conditions_and_errors_preserve_basis(self):
        condition={'op':'all','args':[self.condition(),self.condition('record_field_equals',pointer='/value',value=1)]}
        before=deepcopy(self.instance)
        result=planning.evaluate_condition(condition,self.instance,self.runtime)
        self.assertEqual(result['state'],'ready');self.assertEqual(len(result['basis']),2)
        self.assertEqual(before,self.instance)
        self.instance['knowledge']['K']['value']=True
        self.assertEqual(planning.evaluate_condition(condition,self.instance,self.runtime)['state'],'not_ready')
        changed=planning.evaluate_condition(self.condition(),self.instance,self.runtime)
        self.assertNotEqual(changed['basis'][0]['sha256'],result['basis'][0]['sha256'])
        for invalid in [{'op':'unknown'},self.condition('record_field_equals',pointer='/question',value=1),
                        {'op':'any','args':[{'op':'always'},{'op':'unknown'}]}]:
            self.assertEqual(planning.evaluate_condition(invalid,self.instance,self.runtime)['state'],'evaluation_error')
        self.instance['knowledge'].clear()
        result=planning.evaluate_condition(self.condition(),self.instance,self.runtime)
        self.assertEqual(result['state'],'not_ready');self.assertIn('absencequery',result['basis'][0])

    def test_task_ready_rechecks_reviews_inputs_and_conditions(self):
        self.assertEqual(planning.task_ready(self.task,self.instance,self.runtime)['state'],'ready')
        self.task['reviews'][0]['revision']=2
        self.assertEqual(planning.task_ready(self.task,self.instance,self.runtime)['state'],'not_ready')
        self.task['occurrence_condition']=self.condition('record_lifecycle_is',value='withdrawn')
        approve(self.task,self.instance,self.runtime)
        self.assertEqual(planning.task_ready(self.task,self.instance,self.runtime)['state'],'not_ready')

    def test_contract_hash_only_changes_for_contract_fields(self):
        baseline=planning.contract_hash(self.task)
        self.task.update(status='waiting',waiting={'kind':'external_event'},history=['bookkeeping'])
        self.assertEqual(planning.contract_hash(self.task),baseline)
        self.task['question']='changed'
        self.assertNotEqual(planning.contract_hash(self.task),baseline)

    def test_periodic_exploration_is_not_consumed_by_preparation_only(self):
        from do_math.model_policy import preparation_only
        for field in ('assessment_targets', 'observation_rule_targets'):
            with self.subTest(field=field):
                runtime = deepcopy(self.runtime)
                supplement = {'id': 'AC-supplement', 'role': 'research_preparation',
                    field: {self.task['id']: {'revision': self.task['revision'],
                        'contract_sha256': planning.contract_hash(self.task)}}}
                runtime.update(status='active', queue=[supplement], executions={},
                    waiting_actions={}, events=[], pending_events=[],
                    next_research_reconsider_at='2026-09-24T00:00:00Z')
                original = deepcopy(supplement)
                planning.schedule_reconsideration(self.instance, runtime,
                    now='2026-09-25T00:00:00Z')
                self.assertEqual(supplement, original)
                general = [a for a in runtime['queue']
                           if a['role'] == 'research_preparation' and not preparation_only(a)]
                self.assertEqual(len(general), 1)
                due = [e['id'] for e in runtime['events'] if e['kind'] == 'research_reconsider_due']
                self.assertEqual(general[0]['event_refs'], due)
                self.assertTrue(general[0]['periodic_reconsideration'])
                planning.schedule_reconsideration(self.instance, runtime,
                    now='2026-09-25T00:00:01Z')
                self.assertEqual(len(runtime['queue']), 2)

    def test_due_events_are_unique_and_paused_preserves_pending(self):
        self.runtime['next_research_reconsider_at']='2026-01-01T00:00:00Z'
        self.task.update(wake_at='2026-01-01T00:00:00Z',due_conditions=[{'op':'always'}],newinput=True)
        events=planning.collect_due_events(self.instance,self.runtime,'2026-01-02T00:00:00Z')
        self.assertEqual(sorted(e['kind'] for e in events),['research_reconsider_due','task_condition_due','task_new_input','task_wake_due'])
        self.assertEqual(len(events),len({e['id'] for e in events}))
        self.runtime['status']='paused'
        result=planning.apply_event_schedule(self.instance,self.runtime,'2026-01-02T00:00:00Z')
        self.assertTrue(result['runtime']['pending_events'])
        self.assertFalse(planning.apply_event_schedule(result['instance'],result['runtime'],'2026-01-02T00:00:00Z')['events'])

    def test_condition_state_storage_accepts_each_actual_evaluation_result(self):
        from jsonschema import Draft202012Validator
        from do_math.record_schemas import RUNTIME_FIELDS
        validator = Draft202012Validator(RUNTIME_FIELDS['condition_states'])
        cases = [({'op': 'always'}, 'ready'),
                 ({'op': 'record_exists', 'space': 'research', 'family': 'source',
                   'record_id': 'SO-missing'}, 'not_ready'),
                 ({'op': 'unsupported'}, 'evaluation_error')]
        for condition, expected in cases:
            with self.subTest(expected=expected):
                runtime = deepcopy(self.runtime)
                runtime['tasks'][self.task['id']]['due_conditions'] = [condition]
                scheduled = planning.apply_event_schedule(self.instance, runtime, '2026-09-24T00:00:00Z')
                states = scheduled['runtime']['condition_states']
                self.assertEqual(list(states.values()), [expected])
                validator.validate(states)
        for obsolete in ('blocked', 'unknown', 'unavailable'):
            self.assertTrue(list(validator.iter_errors({'condition': obsolete})))

    def test_source_arrival_and_trust_transition_are_machine_conditions(self):
        condition={'op':'all','args':[
            {'op':'record_exists','space':'research','family':'source','record_id':'SO-new'},
            {'op':'record_lifecycle_is','space':'research','family':'trust-environment','record_id':'TE-1','value':'active'}]}
        self.assertEqual(planning.evaluate_condition(condition,self.instance,self.runtime)['state'],'not_ready')
        self.instance['sources'].append({'id':'SO-new','sha256':'a'*64})
        self.instance['trust_environments']={'TE-1':{'id':'TE-1','status':'active'}}
        self.assertEqual(planning.evaluate_condition(condition,self.instance,self.runtime)['state'],'ready')
        self.instance['trust_environments']['TE-1']['status']='invalid'
        self.assertEqual(planning.evaluate_condition(condition,self.instance,self.runtime)['state'],'not_ready')

    def test_condition_rearms_after_false_without_repeating_while_true(self):
        conditions = [self.condition('record_field_equals', pointer='/value', value=1),
                      self.condition('record_lifecycle_is', value='active')]
        self.task['due_conditions'] = conditions
        first = planning.apply_event_schedule(self.instance, self.runtime, '2026-09-24T00:00:00Z')
        self.assertEqual(len(first['events']), 2)
        original_events = deepcopy(first['events'])
        instance, runtime = first['instance'], first['runtime']
        runtime['pending_events'] = []
        instance['knowledge']['K'].update(value=0, lifecycle='withdrawn')
        false = planning.apply_event_schedule(instance, runtime, '2026-09-24T00:00:01Z')
        self.assertEqual(false['events'], [])
        instance, runtime = false['instance'], false['runtime']
        instance['knowledge']['K'].update(value=1, lifecycle='active')
        again = planning.apply_event_schedule(instance, runtime, '2026-09-24T00:00:02Z')
        self.assertEqual(len(again['events']), 2)
        self.assertEqual(len({row['id'] for row in again['runtime']['events']}), 4)
        self.assertEqual(again['runtime']['events'][:2], original_events)
        self.assertEqual(set(again['runtime']['pending_events']), {row['id'] for row in again['events']})
        repeated = planning.apply_event_schedule(again['instance'], again['runtime'], '2026-09-24T00:00:03Z')
        self.assertEqual(repeated['events'], [])

    def test_relation_condition_rechecks_its_proof_after_import(self):
        from do_math import knowledge_io
        from test_redesign_KNOWLEDGE import KnowledgeRedesign
        from do_math import knowledge_records as kr
        i,r,kid,aid=KnowledgeRedesign().verified()
        template=next(t for t in knowledge_io.relation_templates() if t['token']=='formally_implies')
        i,_=knowledge_io.register_kind_definition(i,template,source_ref='source',actor_ref='producer')
        i=knowledge_io.check_kind_definition(i,'relation','formally_implies',check_ref='check',actor_ref='reviewer')
        i=knowledge_io.activate_kind_definition(i,'relation','formally_implies',approval_ref='approved',actor_ref='reviewer')
        fid=i['knowledge'][kid]['formal_result_id'];xid=i['knowledge'][kid]['exposition_id']
        claim={'kind':'formally_implies','source':kid,'target':kid,'confirmed_scope':'True implies True'}
        i['expositions'][xid]['relation_claim']=claim
        i,aid=kr.record_identity_assessment(i,kid,{'decision':'match','basis':kr.identity_basis(i,kid),'cycle_id':'RC-relation'},'policy:1',runtime=r)
        relation={'id':'RL-1','kind':'formally_implies','source':kid,'target':kid,
            'confirmed_scope':'True implies True','evidence':'reflexivity',
            'formal_result_refs':[fid],'assessment_refs':[aid]}
        i['relations']=[relation]
        condition={'op':'relation_exists','subkind':'formally_implies','from_id':kid,'to_id':kid}
        actual=planning.evaluate_condition(condition,i,r)
        self.assertEqual(actual['state'],'ready',actual)
        i['formal_results'][fid]['formal_use']='suspended'
        self.assertNotEqual(planning.evaluate_condition(condition,i,r)['state'],'ready')

    def test_cited_task_basis_ignores_lifecycle_and_appended_results_but_not_contract_rewrites(self):
        t=self.task;t['results']=[{'execution_id':'EX-1','summary':'first'}]
        basis=[planning.task_reference_basis(t)];tasks={t['id']:deepcopy(t)}
        tasks[t['id']].update(status='active',selected_by='EX-2',reviews=[])
        tasks[t['id']]['results'].append({'execution_id':'EX-3','summary':'later'})
        self.assertEqual(planning.task_reference_changes(basis,tasks),[])
        tasks[t['id']]['scope']['included'].append('new');tasks[t['id']]['results'][0]['summary']='rewritten'
        self.assertEqual(planning.task_reference_changes(basis,tasks),['contract_changed:TK-1','results_changed:TK-1'])
        self.assertEqual(planning.task_reference_changes(basis,{}),['missing:TK-1'])


class ConditionIndexTests(unittest.TestCase):
    def test_compound_condition_scans_one_population_and_rechecks_the_next_evaluation(self):
        from unittest.mock import patch
        instance = {'knowledge': {'K' + str(i): {'id': 'K' + str(i)} for i in range(200)}}
        condition = {'op': 'all', 'args': [
            {'op': 'record_exists', 'space': 'research', 'family': 'knowledge', 'record_id': 'K' + str(i)}
            for i in range(50)]}
        with patch.object(planning, '_records', wraps=planning._records) as scans:
            result = planning.evaluate_condition(condition, instance, {})
            self.assertEqual(scans.call_count, 1)
        self.assertEqual(result['state'], 'ready')
        self.assertEqual(len(result['basis']), 50)
        del instance['knowledge']['K0']
        self.assertEqual(planning.evaluate_condition(condition, instance, {})['state'], 'not_ready')
        duplicate = {'tasks': {'K1': {'id': 'K1'}}}
        result = planning.evaluate_condition(condition, instance, duplicate)
        self.assertEqual(result['state'], 'evaluation_error')
        self.assertIn('duplicate', result['errors'][0])
        wrong_family = {'op': 'record_exists', 'space': 'runtime', 'family': 'task', 'record_id': 'K1'}
        result = planning.evaluate_condition(wrong_family, instance, {})
        self.assertEqual(result['state'], 'evaluation_error')
        self.assertIn('another family', result['errors'][0])
if __name__=='__main__':unittest.main(verbosity=2)
