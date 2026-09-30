"""Assigned observation-rule preparation on the real engine: its receiver, its deferral wait and the retirement
of closed targets (``planning_engine``, ``revision_engine``; layer 2), moved from ``test_academic_preparation``.

The start is ``support.academic_scenes.rule_prepared``: the legacy
``assessment_preparation_instance`` on the public activation, with the queue
cleared and the tasks' observation rules removed, so readiness queues one
combined preparation of rules and model assessments for both tasks. A returned
preparation is registered as the engine registers one
(``support.academic_scenes.ended``). The legacy retirement test called the
mixin method on a ``SimpleNamespace`` host with a replaced ``_remove_action``;
here it is the Sim engine's own method. The preparation that runs through a
model call is ``flows.test_academic_preparation_calls``.
"""
from copy import deepcopy
import unittest

from do_math.model_policy import assessment_basis
from research_fixtures import candidate, prepared_rule_conditions
from runner_fixtures import rating
from support.academic_scenes import ended, rule_prepared, warm_assessment
from support.sim import Sim, warm_template


def setUpModule():
    warm_assessment()
    warm_template()


class RulePreparationFlowTests(unittest.TestCase):
    def test_assessed_task_rule_deferral_waits_for_relevant_new_input(self):
        engine = rule_prepared().engine
        for task in engine.runtime['tasks'].values():
            task['model_assessment'] = {k: v for k, v in rating(task_id=task['id']).items() if k != 'task_id'}
        engine.runtime['queue'] = []
        engine._ensure_model_assessments()
        action = next(a for a in engine.runtime['queue'] if a.get('observation_rule_targets'))
        self.assertNotIn('assessment_targets', action)
        extensions = {'observation_rule_deferrals': [{'task_id': tid, 'reason': 'Missing source text',
            'missing_inputs': ['source:paper'], 'next_owner': 'research_preparation'}
            for tid in action['observation_rule_targets']]}
        ended(engine, 'EX-deferred', 'research_preparation')
        engine.runtime['executions']['EX-deferred'].update(action=action, extensions=extensions)
        engine._finish_assessment_preparation(action, 'EX-deferred')
        engine.runtime['queue'] = []
        engine._ensure_model_assessments()
        self.assertFalse(any(a.get('observation_rule_targets') for a in engine.runtime['queue']))
        engine.instance['sources'].append({'name': 'unrelated', 'sha256': 'a' * 64, 'path': 'sources/unrelated'})
        engine._ensure_model_assessments()
        self.assertFalse(any(a.get('observation_rule_targets') for a in engine.runtime['queue']))
        engine.instance['sources'].append({'name': 'paper', 'sha256': 'f' * 64, 'path': 'sources/paper'})
        engine._ensure_model_assessments()
        self.assertNotIn(action['id'], engine.runtime['waiting_actions'])
        self.assertTrue(any(a.get('observation_rule_targets') for a in engine.runtime['queue']))

    def test_receiver_rejects_a_live_or_changed_target_without_mutating_it(self):
        engine = rule_prepared().engine
        action = next(a for a in engine.runtime['queue'] if a.get('observation_rule_targets'))
        tid = next(iter(action['observation_rule_targets']))
        extensions = {'task_conditions': prepared_rule_conditions(action['observation_rule_targets']),
                      'model_assessments': [rating(task_id=t) for t in action['assessment_targets']]}
        ended(engine, 'EX-prepare', 'research_preparation')
        engine.runtime['executions']['EX-prepare'].update(action=action, extensions=extensions)
        engine._register_execution({'id': 'AC-live', 'role': 'research_work', 'target': tid},
                                   {'id': 'EX-live', 'role': 'research_work', 'status': 'running'})
        before = deepcopy(engine.runtime['tasks'])
        with self.assertRaisesRegex(ValueError, '^preparation target has a live execution: ' + tid + '$'):
            engine._apply_model_metadata(action, {'candidates': []}, 'EX-prepare')
        self.assertEqual(engine.runtime['tasks'], before)
        del engine.runtime['executions']['EX-live']
        engine.runtime['tasks'][tid]['revision'] += 1
        changed = deepcopy(engine.runtime['tasks'])
        with self.assertRaisesRegex(ValueError, '^assessment_targets task edition changed: ' + tid + '$'):
            engine._apply_model_metadata(action, {'candidates': []}, 'EX-prepare')
        self.assertEqual(engine.runtime['tasks'], changed)


class RuleTargetRetirementTests(unittest.TestCase):
    def test_terminal_targets_retire_without_erasing_other_preparation_obligations(self):
        engine = Sim.activated().engine
        task = {**candidate('one'), 'id': 'TK-one', 'revision': 1, 'status': 'planned'}
        action = {'id': 'AC-rules', 'role': 'research_preparation',
                  'observation_rule_targets': {'TK-one': assessment_basis(task), 'TK-two': assessment_basis(task)}}
        engine.runtime.update(tasks={'TK-one': {**task, 'status': 'closed'}, 'TK-two': {**task, 'id': 'TK-two'}},
                              queue=[action], waiting_actions={})
        history = len(engine.runtime['history'])
        engine._retire_closed_revision_targets()
        self.assertEqual(set(action['observation_rule_targets']), {'TK-two'})
        self.assertEqual(engine.runtime['queue'], [action])
        self.assertEqual(engine.runtime['history'][history:], [{'kind': 'preparation_targets_retired_after_disposition',
                                                                'action_id': 'AC-rules', 'targets': ['TK-one']}])
        engine.runtime['tasks']['TK-two']['status'] = 'completed'
        engine._retire_closed_revision_targets()
        self.assertEqual(engine.runtime['queue'], [])


if __name__ == '__main__':
    unittest.main()
