"""4-B: actual preparation waits remain until their own profile/input changes.

Four real engine/Repository scenes exercise production entry, public input or
profile/rule release and durable idempotence. The combined test took 15.4s;
the scene work is retained rather than replacing the engine or persistence.
"""
from copy import deepcopy
import unittest

from do_math import execution_profiles
from do_math.model_policy import assessment_basis
from do_math.observations import OPERATORS
from do_math.wait_rules import PREPARATION_WAIT_RULES
from support.engine_lifecycle import _ended_execution, applied
from support.observation_inputs import observation_rule, prepared_rule_conditions
from support.planning_contract_inputs import prepared_sim, only_task, warm_prepared
from support.planning_owner import enqueue
from support.academic_scenes import rule_prepared, ended
from support.default_responder import rating
from support.scheduling_parallel import ready_work_sim
from support.wait_reporting import assert_wait_report

setUpModule = warm_prepared


def preparation_case(kind):
    if kind == 'observation_rules':
        sim = ready_work_sim(1)
        action = deepcopy(sim.runtime['queue'][0])
        rule = observation_rule('iteration_gte', OPERATORS['iteration_gte']['subject_kind'], '$execution')
        rule['subject']['id'] = 'EX-previous'
        sim.runtime.setdefault('task_observation_rules', {})[action['target']] = [rule]
        sim.engine._save()
        sim.engine._prepare_call(action)
        return sim, action, None
    if kind == 'observation_configuration':
        sim = prepared_sim()
        normal = deepcopy(sim.instance['config'])
        invalid = deepcopy(normal)
        del invalid['tool_review_window_seconds']
        execution_profiles.apply_editions(sim.instance, execution_profiles.build_profiles(invalid, host=sim.ports.host))
        action = enqueue(sim.engine, 'task_contract_review', only_task(sim)['id'])
        sim.engine._prepare_call(action)
        return sim, action, normal
    sim = rule_prepared() if kind == 'observation_rule_input' else prepared_sim()
    engine = sim.engine
    if kind == 'observation_rule_input':
        for task in sim.runtime['tasks'].values():
            task['model_assessment'] = {key: value for key, value in rating(task_id=task['id']).items() if key != 'task_id'}
        sim.runtime['queue'] = []
        engine._ensure_model_assessments()
        action = next(row for row in sim.runtime['queue'] if row.get('observation_rule_targets'))
        extensions = {'observation_rule_deferrals': [{'task_id': identifier, 'reason': 'Missing source',
            'missing_inputs': ['user_input'], 'next_owner': 'user'}
            for identifier in action['observation_rule_targets']]}
    else:
        task = only_task(sim)
        task.pop('model_assessment', None)
        action = enqueue(engine, 'research_preparation', assessment_targets={task['id']: assessment_basis(task)})
        extensions = {'model_assessment_deferrals': [{'task_id': task['id'], 'reason': 'Missing assessment input'}]}
    ended(engine, 'EX-prep-deferred', 'research_preparation')
    engine.runtime['executions']['EX-prep-deferred'].update(action=action, extensions=extensions)
    engine._apply_model_metadata(action, {'candidates': []}, 'EX-prep-deferred')
    engine._finish_assessment_preparation(action, 'EX-prep-deferred')
    engine._remove_action(action)
    return sim, action, None


class PreparationWaitContractTests(unittest.TestCase):
    def test_every_declared_preparation_wait_has_a_real_input_or_profile_exit(self):
        exercised = set()
        for kind in PREPARATION_WAIT_RULES:
            with self.subTest(kind=kind):
                sim, action, normal = preparation_case(kind)
                engine = sim.engine
                entry = deepcopy(sim.runtime['waiting_actions'][action['id']])
                self.assertEqual(entry['kind'], kind)
                self.assertEqual(entry['next_owner'], PREPARATION_WAIT_RULES[kind]['next_owner'])
                engine._save()
                assert_wait_report(self, engine, action['id'])
                if kind == 'observation_configuration':
                    before = deepcopy((sim.instance, sim.runtime))
                    engine._retry_observation_configuration()
                    self.assertEqual((sim.instance, sim.runtime), before)
                    sim.instance['config'] = normal
                    execution_profiles.apply_editions(sim.instance, execution_profiles.build_profiles(normal, host=sim.ports.host))
                    engine._retry_observation_configuration()
                elif kind == 'observation_rules':
                    task = sim.runtime['tasks'][action['target']]
                    prep = enqueue(engine, 'research_preparation', observation_rule_targets={task['id']: assessment_basis(task)})
                    conditions = prepared_rule_conditions([task['id']])
                    conditions[0]['observation_rules'][0]['threshold'] += 1
                    _ended_execution(engine, 'EX-valid-rules', 'research_preparation')
                    sim.runtime['executions']['EX-valid-rules'].update(action=prep, extensions={'task_conditions': conditions})
                    engine._apply_model_metadata(prep, {'candidates': []}, 'EX-valid-rules')
                    engine._finish_assessment_preparation(prep, 'EX-valid-rules')
                else:
                    before = deepcopy(sim.runtime['waiting_actions'][action['id']])
                    engine._ensure_model_assessments()
                    self.assertEqual(sim.runtime['waiting_actions'][action['id']], before)
                    engine._save()
                    applied(sim, 'input', text='Supply the missing preparation input')
                    engine._ensure_model_assessments()
                    for field in ('assessment_targets', 'observation_rule_targets'):
                        for identifier in action.get(field, {}):
                            self.assertEqual(sum(identifier in row.get(field, {})
                                for row in sim.runtime['queue']), 1, (kind, field, identifier))
                self.assertNotIn(action['id'], sim.runtime.get('waiting_actions', {}))
                after = deepcopy(sim.runtime)
                if kind == 'observation_configuration':
                    engine._retry_observation_configuration()
                elif kind == 'observation_rules':
                    engine._resolve_task_observation_waits(action['target'], 'EX-valid-rules')
                else:
                    engine._ensure_model_assessments()
                self.assertEqual(sim.runtime, after)
                engine._save()
                self.assertNotIn(action['id'], engine.store.load()[2].get('waiting_actions', {}))
                exercised.add(kind)
        self.assertEqual(exercised, set(PREPARATION_WAIT_RULES))
