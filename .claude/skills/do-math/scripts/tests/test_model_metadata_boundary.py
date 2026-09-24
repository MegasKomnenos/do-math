from copy import deepcopy
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from do_math.contracts import task_candidate_record
from do_math.execution_profiles import build_profiles,profile_ref
from do_math.engine import DEFAULT_CONFIG
from test_redesign_ENGINE import routing_engine
from research_fixtures import candidate, disposition


class ModelMetadataBoundaryTests(unittest.TestCase):
    def test_plan_receiver_uses_the_authored_dispositions_without_a_legacy_projection(self):
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
        profiles = build_profiles(config)['execution_profiles']
        work = next(p for p in profiles.values() if p['role'] == 'research_work'
                    and p['ai']['tier'] == 'low')
        tasks = {'TK-one': {'profile_refs': [profile_ref(work)], 'model_assessment': {
            'difficulty': 'low', 'importance': 'low', 'reason': 'Bounded work'}}}
        selected = model_policy.selection(config,
            {'role': 'task_contract_review', 'target': 'TK-one'}, tasks, {}, profiles=profiles)
        reviewer = profiles[selected['profile_ref']['id']]
        self.assertEqual(reviewer['role'], 'task_contract_review')
        self.assertEqual(reviewer['ai']['tier'], config['role_tiers']['task_contract_review'])
        selected_work = model_policy.selection(config,
            {'role': 'research_work', 'target': 'TK-one'}, tasks, {}, profiles=profiles)
        self.assertEqual(selected_work['profile_ref'], profile_ref(work))
        tasks['TK-one']['profile_refs'] = []
        with self.assertRaisesRegex(ValueError, 'permitted role/model edition'):
            model_policy.selection(config, {'role': 'research_work', 'target': 'TK-one'},
                tasks, {}, profiles=profiles)

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


if __name__=='__main__': unittest.main()
