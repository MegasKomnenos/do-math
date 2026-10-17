"""4-B: actual preparation waits remain until their own profile/input changes.

Four real engine/Repository scenes exercise production entry, public input or
profile/rule release and durable idempotence. The combined test took 15.4s;
the scene work is retained rather than replacing the engine or persistence.
"""
from copy import deepcopy
import unittest

from do_math import execution_profiles
from do_math.model_policy import assessment_basis
from do_math.wait_rules import PREPARATION_WAIT_RULES
from support.engine_lifecycle import _ended_execution, applied
from support.observation_inputs import prepared_rule_conditions
from support.planning_contract_inputs import warm_prepared
from support.planning_owner import enqueue
from support.storage_action_pairs import preparation_case
from support.wait_reporting import assert_wait_report

setUpModule = warm_prepared


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
