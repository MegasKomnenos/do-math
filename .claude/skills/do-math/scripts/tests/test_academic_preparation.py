"""Assigned observation preparation: producer coverage and engine transitions."""
from copy import deepcopy
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math.contracts import action_schema
from do_math.model_policy import assessment_basis
from do_math.observations import validate_rule_preparation
from do_math.planning import action_read_ids, revision_waits
from do_math.submission import payload_issues
from test_engine import common
import test_model_assessment_flow as assessment_tests
from test_model_assessment_flow import rating
from test_purpose_engine import ActivatedPurposeHarness, PurposeRunner
from research_fixtures import candidate, prepared_rule_conditions, seal_response


class RuleSubmissionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.workspace = Path(self.temp.name)
        self.task = {**candidate('one'), 'id': 'TK-one', 'revision': 1, 'status': 'planned'}
        self.action = {'id': 'AC-rules', 'role': 'research_preparation',
                       'observation_rule_targets': {'TK-one': assessment_basis(self.task)}}
        self.context = {'action': self.action, 'budget_unit': 'concurrent_sessions', 'tasks': [self.task],
                        'knowledge_catalog': [], 'kind_definitions': {}, 'sources': []}

    def issues(self, extensions, candidates=None):
        output = {**common('research_preparation'), 'candidates': candidates or []}
        from do_math.repository import canonical_json
        (self.workspace / 'activity-extensions.json').write_bytes(canonical_json(extensions))
        seal_response(output, self.context, self.workspace)
        return payload_issues(output, action_schema(self.action), self.context, extensions, self.workspace)

    def test_rules_only_and_combined_preparation_cover_exact_assignments(self):
        extensions = {'task_conditions': prepared_rule_conditions(['TK-one'])}
        self.assertEqual(self.issues(extensions), [])
        self.action['assessment_targets'] = {'TK-one': assessment_basis(self.task)}
        self.assertTrue(self.issues(extensions))
        self.assertEqual(self.issues({**extensions, 'model_assessments': [rating(task_id='TK-one')]}), [])

    def test_deferral_is_explicit_complete_and_exclusive(self):
        deferred = {'task_id': 'TK-one', 'reason': 'Need the source',
                    'missing_inputs': ['source:paper'], 'next_owner': 'research_preparation'}
        self.assertTrue(self.issues({}))
        self.assertEqual(self.issues({'observation_rule_deferrals': [deferred]}), [])
        self.assertTrue(self.issues({'observation_rule_deferrals': [deferred, deferred]}))
        self.assertTrue(self.issues({'observation_rule_deferrals': [deferred],
                                    'task_conditions': prepared_rule_conditions(['TK-one'])}))

    def test_unauthorized_contract_edits_foreign_targets_and_stale_editions_fail(self):
        good = prepared_rule_conditions(['TK-one'])
        for extra in ({'dependencies': []}, {'task_title': 'one'}, {'completion_obligations': []}):
            self.assertTrue(self.issues({'task_conditions': [{**good[0], **extra}]}))
        self.assertTrue(self.issues({'task_conditions': prepared_rule_conditions(['TK-other'])}))
        self.assertTrue(self.issues({'task_conditions': good}, [candidate('new')]))
        self.task['revision'] += 1
        self.assertTrue(self.issues({'task_conditions': good}))

    def test_assigned_rules_are_declared_writes_and_keep_other_readers_out(self):
        runtime = {'tasks': {'TK-one': self.task}, 'queue': [self.action], 'executions': {
            'EX-rules': {'id': 'EX-rules', 'status': 'running', 'action': self.action}}, 'waiting_actions': {}}
        instance = {'knowledge': {}}
        self.assertIn('TK-one', action_read_ids(self.action, instance, runtime))
        waits = revision_waits({'id': 'AC-review', 'role': 'task_contract_review', 'target': 'TK-one'}, instance, runtime)
        self.assertTrue(waits)
        runtime['executions'] = {'EX-work': {'id': 'EX-work', 'status': 'running',
            'action': {'id': 'AC-work', 'role': 'research_work', 'target': 'TK-one'}}}
        self.assertTrue(revision_waits(self.action, instance, runtime))

    def test_terminal_targets_retire_without_erasing_other_preparation_obligations(self):
        from do_math.revision_engine import RevisionEngineMixin
        from types import SimpleNamespace
        action = deepcopy(self.action)
        action['observation_rule_targets']['TK-two'] = deepcopy(action['observation_rule_targets']['TK-one'])
        runtime = {'tasks': {'TK-one': {**self.task, 'status': 'closed'},
                             'TK-two': {**self.task, 'id': 'TK-two'}},
                   'queue': [action], 'executions': {}, 'waiting_actions': {}, 'history': []}
        host = SimpleNamespace(runtime=runtime, _remove_action=lambda a: runtime['queue'].remove(a))
        RevisionEngineMixin._retire_closed_revision_targets(host)
        self.assertEqual(set(action['observation_rule_targets']), {'TK-two'})
        self.assertEqual(runtime['queue'], [action])
        runtime['tasks']['TK-two']['status'] = 'completed'
        RevisionEngineMixin._retire_closed_revision_targets(host)
        self.assertEqual(runtime['queue'], [])


class RulePreparationFlowTests(ActivatedPurposeHarness):
    def prepare(self):
        engine = assessment_tests.AssessmentFlowTests.prepare_engine(self)
        engine.runtime['queue'] = []
        for task in engine.runtime['tasks'].values():
            task['initial_observation_rules'] = []
        engine._refresh_readiness()
        engine._save()
        return engine

    def test_combined_preparation_preserves_user_terms_and_publishes_fresh_review(self):
        engine = self.prepare()
        before = deepcopy(engine.runtime['tasks'])
        action = next(a for a in engine.runtime['queue'] if a.get('observation_rule_targets'))
        self.assertEqual(set(action['assessment_targets']), set(action['observation_rule_targets']))
        failed_id = 'AC-old-rules'
        failed_action = {'id': failed_id, 'role': 'research_work', 'target': next(iter(before))}
        activity = engine._activity_for_action(failed_action)
        from do_math.activities import wait_for
        wait_for(engine.runtime, activity['id'], reason='missing rules', condition={'kind': 'observation_rules'},
                 next_owner='research_preparation', at=engine._lifecycle_now().isoformat())
        engine.runtime['waiting_actions'][failed_id] = {'action': failed_action,
            'kind': 'observation_rules', 'reason': 'missing rules'}
        engine._save()
        engine.runner = PurposeRunner()
        engine.run(max_steps=1)
        self.assertNotIn(failed_id, engine.runtime['waiting_actions'])
        self.assertEqual(engine.runtime['activities'][activity['id']]['status'], 'finished')
        for tid, task in engine.runtime['tasks'].items():
            for key in ('question', 'scope', 'expected', 'completion_obligations', 'academic_requirement_id', 'authority_refs'):
                self.assertEqual(task[key], before[tid][key])
            self.assertEqual(task['revision'], before[tid]['revision'] + 1)
            self.assertTrue(task['initial_observation_rules'])
            self.assertTrue(task['model_assessment'])
            reviews = [a for a in engine.runtime['queue'] if a['role'] == 'task_contract_review' and a.get('target') == tid]
            self.assertEqual(len(reviews), 1)
            self.assertEqual(reviews[0]['contract_basis']['revision'], task['revision'])
        self.assertEqual(engine.runtime['cycles'], 0)
        self.assertTrue(any(h['kind'] == 'observation_rules_resolved' for h in engine.runtime['history']))

    def test_assessed_task_rule_deferral_waits_for_relevant_new_input(self):
        engine = self.prepare()
        for task in engine.runtime['tasks'].values():
            task['model_assessment'] = {k: v for k, v in rating(task_id=task['id']).items() if k != 'task_id'}
        engine.runtime['queue'] = []
        engine._ensure_model_assessments()
        action = next(a for a in engine.runtime['queue'] if a.get('observation_rule_targets'))
        self.assertNotIn('assessment_targets', action)
        extensions = {'observation_rule_deferrals': [{'task_id': tid, 'reason': 'Missing source text',
            'missing_inputs': ['source:paper'], 'next_owner': 'research_preparation'} for tid in action['observation_rule_targets']]}
        engine.runtime['executions']['EX-deferred'] = {'id': 'EX-deferred', 'role': 'research_preparation',
            'status': 'ended', 'action': action, 'extensions': extensions}
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
        engine = self.prepare()
        action = next(a for a in engine.runtime['queue'] if a.get('observation_rule_targets'))
        tid = next(iter(action['observation_rule_targets']))
        extensions = {'task_conditions': prepared_rule_conditions(action['observation_rule_targets']),
                      'model_assessments': [rating(task_id=t) for t in action['assessment_targets']]}
        engine.runtime['executions']['EX-prepare'] = {'extensions': extensions, 'status': 'ended', 'action': action}
        engine.runtime['executions']['EX-live'] = {'status': 'running', 'action': {'role': 'research_work', 'target': tid}}
        before = deepcopy(engine.runtime['tasks'])
        with self.assertRaisesRegex(ValueError, 'live execution'):
            engine._apply_model_metadata(action, {'candidates': []}, 'EX-prepare')
        self.assertEqual(engine.runtime['tasks'], before)
        del engine.runtime['executions']['EX-live']
        engine.runtime['tasks'][tid]['revision'] += 1
        with self.assertRaisesRegex(ValueError, 'edition changed'):
            engine._apply_model_metadata(action, {'candidates': []}, 'EX-prepare')


if __name__ == '__main__':
    unittest.main()
