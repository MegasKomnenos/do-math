"""Assigned observation-rule preparation as the producer submits it (``submission.payload_issues``) and as the
planner reads its targets (``planning``), layer 1; moved from ``test_academic_preparation``'s ``RuleSubmissionTests``.

A preparation assigned ``observation_rule_targets`` must dispose every target
exactly once, by rule conditions or an explicit deferral, and may edit nothing
else. The workspace is a temporary folder; the response is sealed as the
worker seals it (``research_fixtures.seal_response``). Each refusal is pinned
by its issue's rule and message.
"""
from pathlib import Path
import tempfile
import unittest

from do_math.canonical import canonical_json
from do_math.contracts import action_schema
from do_math.model_policy import assessment_basis
from do_math.planning import action_read_ids, revision_waits
from do_math.submission import payload_issues
from research_fixtures import candidate, prepared_rule_conditions, seal_response
from runner_fixtures import common, rating

COVERAGE = ('submission.activity-extensions.json.task_conditions', 'activity-extensions.json/task_conditions',
            'observation rule coverage must dispose every assigned target exactly once')


def reasons(issues):
    return [(issue['rule_id'], issue['path'], issue['message']) for issue in issues]


class RuleSubmissionTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.workspace = Path(temp.name)
        self.task = {**candidate('one'), 'id': 'TK-one', 'revision': 1, 'status': 'planned'}
        self.action = {'id': 'AC-rules', 'role': 'research_preparation',
                       'observation_rule_targets': {'TK-one': assessment_basis(self.task)}}
        self.context = {'action': self.action, 'budget_unit': 'concurrent_sessions', 'tasks': [self.task],
                        'knowledge_catalog': [], 'kind_definitions': {}, 'sources': []}

    def issues(self, extensions, candidates=None):
        output = {**common('research_preparation'), 'candidates': candidates or []}
        (self.workspace / 'activity-extensions.json').write_bytes(canonical_json(extensions))
        seal_response(output, self.context, self.workspace)
        return payload_issues(output, action_schema(self.action), self.context, extensions, self.workspace)

    def test_rules_only_and_combined_preparation_cover_exact_assignments(self):
        extensions = {'task_conditions': prepared_rule_conditions(['TK-one'])}
        self.assertEqual(self.issues(extensions), [])
        self.action['assessment_targets'] = {'TK-one': assessment_basis(self.task)}
        self.assertEqual(reasons(self.issues(extensions)), [
            ('submission.activity-extensions.json.model_assessments', 'activity-extensions.json/model_assessments',
             'model assessment coverage: {"missing": ["TK-one"], "unexpected": []}')])
        self.assertEqual(self.issues({**extensions, 'model_assessments': [rating(task_id='TK-one')]}), [])

    def test_deferral_is_explicit_complete_and_exclusive(self):
        deferred = {'task_id': 'TK-one', 'reason': 'Need the source',
                    'missing_inputs': ['source:paper'], 'next_owner': 'research_preparation'}
        self.assertEqual(reasons(self.issues({})), [COVERAGE])  # no implicit omission
        self.assertEqual(self.issues({'observation_rule_deferrals': [deferred]}), [])
        self.assertEqual(reasons(self.issues({'observation_rule_deferrals': [deferred, deferred]})), [COVERAGE])
        self.assertEqual(reasons(self.issues({'observation_rule_deferrals': [deferred],
                                              'task_conditions': prepared_rule_conditions(['TK-one'])})), [COVERAGE])

    def test_unauthorized_contract_edits_foreign_targets_and_stale_editions_fail(self):
        good = prepared_rule_conditions(['TK-one'])
        for extra in ({'dependencies': []}, {'task_title': 'one'}, {'completion_obligations': []}):
            with self.subTest(extra=extra):
                field, = extra
                self.assertEqual(reasons(self.issues({'task_conditions': [{**good[0], **extra}]})), [
                    ('schema.additionalProperties', 'activity-extensions.json/task_conditions/0',
                     f"Additional properties are not allowed ('{field}' was unexpected)")])
        self.assertEqual(reasons(self.issues({'task_conditions': prepared_rule_conditions(['TK-other'])})), [
            ('submission.activity-extensions.json.task_conditions.*', 'activity-extensions.json/task_conditions/0',
             'task condition must name exactly one prepared target'), COVERAGE])
        self.assertEqual([(issue['rule_id'], issue['path']) for issue in self.issues({'task_conditions': good},
                                                                                      [candidate('new')])],
                         [('schema.maxItems', 'output/candidates')])
        self.task['revision'] += 1
        self.assertEqual(reasons(self.issues({'task_conditions': good})), [
            (COVERAGE[0], COVERAGE[1], 'observation rule target contract edition changed: TK-one')])

    def test_assigned_rules_are_declared_writes_and_keep_other_readers_out(self):
        runtime = {'tasks': {'TK-one': self.task}, 'queue': [self.action], 'executions': {
            'EX-rules': {'id': 'EX-rules', 'status': 'running', 'action': self.action}}, 'waiting_actions': {}}
        instance = {'knowledge': {}}
        self.assertIn('TK-one', action_read_ids(self.action, instance, runtime))
        review = {'id': 'AC-review', 'role': 'task_contract_review', 'target': 'TK-one'}
        self.assertEqual(revision_waits(review, instance, runtime), [
            {'kind': 'contract_revision', 'action_id': 'AC-rules', 'record_ids': ['TK-one'],
             'reason': 'required record has an unresolved revision'}])
        runtime['executions'] = {'EX-work': {'id': 'EX-work', 'status': 'running',
                                             'action': {'id': 'AC-work', 'role': 'research_work', 'target': 'TK-one'}}}
        self.assertEqual(revision_waits(self.action, instance, runtime), [
            {'kind': 'contract_revision', 'execution_id': 'EX-work', 'record_ids': ['TK-one'],
             'reason': 'existing reader must finish before revision'}])


if __name__ == '__main__':
    unittest.main()
