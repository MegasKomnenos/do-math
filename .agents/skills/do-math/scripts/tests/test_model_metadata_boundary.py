from copy import deepcopy
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from do_math.contracts import task_candidate_record
from do_math.execution_profiles import build_profiles,profile_ref
from do_math.configuration import DEFAULT_CONFIG
from engine_fixtures import routing_engine
from research_fixtures import bare_engine, candidate, disposition


class ModelMetadataBoundaryTests(unittest.TestCase):
    def test_plan_receiver_records_model_decisions_without_changing_the_authored_dispositions(self):
        engine = routing_engine()
        engine.instance['config'] = deepcopy(DEFAULT_CONFIG)
        rating = {'difficulty': 'low', 'importance': 'medium', 'reason': 'The supplied bounded contract'}
        output = {'dispositions': [disposition('TK-selected'),
                                   disposition('TK-waiting', kind='not_selected')]}
        original = deepcopy(output)
        engine.runtime['executions']['EX-plan'] = {'extensions': {
            'model_assessments': [{'task_id': 'TK-selected', **rating}]}}
        engine._apply_model_metadata({'role': 'research_plan'}, output, 'EX-plan')
        self.assertEqual(engine.runtime['executions']['EX-plan']['model_decisions'], {'TK-selected': rating})
        self.assertEqual(output, original)
        engine.runtime['executions']['EX-plan']['extensions']['model_assessments'] = []
        with self.assertRaisesRegex(ValueError, 'missing'):
            engine._apply_model_metadata({'role': 'research_plan'}, output, 'EX-plan')
        engine.runtime['executions']['EX-plan']['extensions']['model_assessments'] = [
            {'task_id': 'TK-selected', **rating}, {'task_id': 'TK-waiting', **rating}]
        with self.assertRaisesRegex(ValueError, 'unexpected'):
            engine._apply_model_metadata({'role': 'research_plan'}, output, 'EX-plan')

    def test_plan_rates_a_selected_task_only_to_change_or_supply_its_stored_assessment(self):
        engine = routing_engine()
        engine.instance['config'] = deepcopy(DEFAULT_CONFIG)
        stored = {'difficulty': 'low', 'importance': 'medium', 'reason': 'Reviewed with the contract'}
        changed = {'difficulty': 'high', 'importance': 'high', 'reason': 'A failed attempt showed the gap is central'}
        engine.runtime['tasks'] = {'TK-kept': {'id': 'TK-kept', 'model_assessment': stored},
                                   'TK-unrated': {'id': 'TK-unrated'}}
        output = {'dispositions': [disposition('TK-kept'), disposition('TK-unrated'),
                                   disposition('TK-waiting', kind='not_selected')]}
        def apply(rows):
            engine.runtime['executions']['EX-plan'] = {'extensions': {'model_assessments': rows}}
            engine._apply_model_metadata({'role': 'research_plan'}, output, 'EX-plan')
            return engine.runtime['executions']['EX-plan']['model_decisions']
        self.assertEqual(apply([{'task_id': 'TK-unrated', **stored}]), {'TK-unrated': stored})
        self.assertEqual(apply([{'task_id': 'TK-kept', **changed}, {'task_id': 'TK-unrated', **stored}]),
                         {'TK-kept': changed, 'TK-unrated': stored})
        with self.assertRaisesRegex(ValueError, 'missing'):
            apply([{'task_id': 'TK-kept', **changed}])
        with self.assertRaisesRegex(ValueError, 'unexpected'):
            apply([{'task_id': 'TK-unrated', **stored}, {'task_id': 'TK-waiting', **stored}])
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            apply([{'task_id': 'TK-unrated', **stored}, {'task_id': 'TK-unrated', **changed}])

    def test_formal_contract_binds_the_supplied_environment_without_changing_wire(self):
        item = candidate('formal work', formal=True)
        original = deepcopy(item)
        contract = task_candidate_record(item, task_id='TK-one', trust_environment_id='TE-author')
        self.assertEqual(contract['trust_environment_id'], 'TE-author')
        self.assertEqual(item, original)
        item['work_class'] = 'nonformal'
        self.assertNotIn('trust_environment_id', task_candidate_record(item,
            task_id='TK-other', trust_environment_id='TE-author'))

    def test_task_work_allowlist_does_not_block_the_independent_contract_reviewer(self):
        from do_math import model_policy
        config = deepcopy(DEFAULT_CONFIG)
        instance = build_profiles(config)
        profiles = instance['execution_profiles']
        work = next(p for p in profiles.values() if p['role'] == 'research_work'
                    and p['ai']['tier'] == 'low')
        tasks = {'TK-one': {'profile_refs': [profile_ref(work)], 'model_assessment': {
            'difficulty': 'low', 'importance': 'low', 'reason': 'Bounded work'}}}
        selected = model_policy.selection(config,
            {'role': 'task_contract_review', 'target': 'TK-one'}, tasks, {}, instance=instance)
        reviewer = profiles[selected['profile_ref']['id']]
        self.assertEqual(reviewer['role'], 'task_contract_review')
        self.assertEqual(reviewer['ai']['tier'], config['role_tiers']['task_contract_review'])
        selected_work = model_policy.selection(config,
            {'role': 'research_work', 'target': 'TK-one'}, tasks, {}, instance=instance)
        self.assertEqual(selected_work['profile_ref'], profile_ref(work))
        tasks['TK-one']['profile_refs'] = []
        with self.assertRaisesRegex(ValueError, 'permitted role/model edition'):
            model_policy.selection(config, {'role': 'research_work', 'target': 'TK-one'},
                tasks, {}, instance=instance)

    def test_assessment_is_preserved_without_changing_the_candidate_wire_shape(self):
        engine=routing_engine()
        engine.instance['config']={**deepcopy(DEFAULT_CONFIG),}
        item=candidate('bounded observation')
        profile=next(p for p in build_profiles(DEFAULT_CONFIG)['execution_profiles'].values()
                     if p['role']=='research_work')
        item['profile_refs']=[profile_ref(profile)]
        output={'candidates':[item]}
        original=deepcopy(output)
        rating={'difficulty':'low','importance':'low','reason':'A bounded test task'}
        engine.runtime['executions']['EX-prepare']={'extensions':{
            'model_assessments':[{'task_title':item['title'],**rating}]}}
        engine._apply_model_metadata({'role':'research_preparation'},output,'EX-prepare')
        contract=task_candidate_record(output['candidates'][0],task_id='TK-test')
        self.assertEqual(output,original)
        self.assertEqual(engine.runtime['executions']['EX-prepare']['model_decisions'],
                         {item['title']:rating})
        self.assertEqual(contract['title'],item['title'])

    def test_processed_rejection_cannot_erase_a_fresh_equal_or_changed_assessment(self):
        from do_math.model_policy import assessment_basis, LIMITS
        from record_fixtures import approved_task
        from runner_fixtures import rating
        from research_fixtures import prepared_rule_conditions
        for unchanged in (False, True):
            with self.subTest(unchanged=unchanged):
                task, instance, runtime = approved_task()
                rules = prepared_rule_conditions([task['id']])[0]['observation_rules']
                task['initial_observation_rules'] = deepcopy(rules)
                instance['config'] = {'session_limits': deepcopy(LIMITS)}
                task.update(academic_requirement_id='R', revision_requested={'revision': task['revision'], 'source': 'REJECT',
                    'reason': 'task contract review returned revision_required'},
                    model_assessment=rating())
                task['reviews'] = [{**assessment_basis(task), 'decision': 'revision_required', 'execution_id': 'REJECT'}]
                host = bare_engine(instance, runtime)
                host._ensure_model_assessments()
                revised = rating() if unchanged else {**rating(), 'importance': 'high'}
                task['model_assessment'] = deepcopy(revised)
                task['initial_observation_rules'] = deepcopy(rules)
                runtime['queue'] = [{'id': 'NEW-REVIEW', 'role': 'task_contract_review', 'target': task['id']}]
                for _ in range(3):
                    host._ensure_model_assessments()
                self.assertEqual(task['model_assessment'], revised)
                self.assertEqual(len(task['model_assessment_history']), 1)
                self.assertEqual([a['id'] for a in runtime['queue']], ['NEW-REVIEW'])
                task['reviews'].append({**assessment_basis(task), 'decision': 'unresolved', 'execution_id': 'REJECT-NEW'})
                host._ensure_model_assessments()
                self.assertNotIn('model_assessment', task)
                self.assertEqual(len(task['model_assessment_history']), 2)


if __name__=='__main__': unittest.main()
