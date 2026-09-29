"""A task's observation rules bound to one execution (``observations``, layer 2) and required at preparation (``submission``).

A task rule names ``$execution`` where it means "the execution that runs this
task". Starting an execution binds that subject to the new execution ID;
persisting rules from an execution turns the ID back into ``$execution``. A
rule already bound to another execution is never rebound.
"""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest

from do_math import execution_profiles, observations
from do_math.configuration import DEFAULT_CONFIG

CHECKPOINTS = {'id': 'checkpoints', 'operator': 'checkpoint_count_gte',
               'subject': {'kind': 'checkpoint', 'id': '$execution'},
               'basis': {'source': 'checkpoint', 'unit': 'count'}, 'threshold': 2, 'required_evidence': ['contract']}
NOT_EXECUTION = 'task rule execution-bound subject must be \\$execution'
OTHER_EXECUTION = 'persisted rule refers to another execution'


class PreparationRuleTests(unittest.TestCase):
    def test_producer_reports_missing_initial_rules_before_contract_review(self):
        """A preparation whose candidate declares no initial rules draws one issue on that candidate."""
        from do_math.contracts import schema_for
        from do_math.submission import payload_issues
        from record_fixtures import contract_check, preparation_context
        from research_fixtures import candidate
        from runner_fixtures import common, rating
        output = {**common("research_preparation"), "candidates": [candidate('one')]}
        # The extensions of ``record_fixtures.preparation_issues`` without the fixture's observation rules.
        extensions = {"model_assessments": [rating(task_title='one')], "contract_checks": [contract_check()]}
        output["integration_bundles"] = [{"integration_id": "IN-check", "members": ["output", *[
            f"activity-extensions.json/{family}/{i}" for family, rows in extensions.items() for i, _ in enumerate(rows)]],
            "impact_set": [], "authority_refs": []}]
        with tempfile.TemporaryDirectory() as directory:
            issues = payload_issues(output, schema_for("research_preparation"), preparation_context(), extensions,
                                    Path(directory))
        self.assertIn('initial_observation_rules', json.dumps(issues, ensure_ascii=False))
        self.assertEqual([(issue['rule_id'], issue['path'], issue['message']) for issue in issues],
                         [('submission.output.candidates.*.initial_observation_rules',
                           'output/candidates/0/initial_observation_rules',
                           'observation rules must be a nonempty list of at most 16 rules')])


class ExecutionBindingTests(unittest.TestCase):
    def test_foreign_execution_is_not_silently_rebound(self):
        rules = [{**deepcopy(CHECKPOINTS), 'subject': {'kind': 'checkpoint', 'id': 'EX-foreign'}, 'threshold': 1,
                  'required_evidence': ['input/contract.json']}]
        with self.assertRaisesRegex(ValueError, NOT_EXECUTION):
            observations.bind_task_rules(rules, 'EX-new')
        with self.assertRaisesRegex(ValueError, OTHER_EXECUTION):
            observations.task_rules_from_execution(rules, 'EX-new')

    def test_one_task_rule_can_start_two_distinct_executions(self):
        profile = next(p for p in execution_profiles.build_profiles({**deepcopy(DEFAULT_CONFIG),
            'tool_review_window_seconds': 60, 'self_check_response_window_seconds': 5})['execution_profiles'].values()
                       if p['role'] == 'research_work')
        rules = [deepcopy(CHECKPOINTS)]
        binder = getattr(observations, 'bind_task_rules', None)
        self.assertTrue(callable(binder), 'task rules need an execution binding before tracker admission')
        with tempfile.TemporaryDirectory() as directory:
            for eid in ('EX-first', 'EX-second'):
                bound = binder(rules, eid)
                config = observations.tracker_config(profile, initial_self_check_rules=bound)
                tracker = observations.ObservationTracker(eid, Path(directory), config)
                self.assertEqual(tracker.rules[0]['subject']['id'], eid)
        self.assertEqual(rules[0]['subject']['id'], '$execution')

    def test_checkpoint_iterations_bind_and_round_trip_for_each_execution(self):
        template = [{'id': 'iteration-review', 'operator': 'iteration_gte',
            'subject': {'kind': 'iteration', 'id': '$execution'},
            'basis': {'source': 'checkpoint', 'unit': 'count'},
            'threshold': 10, 'repeat_interval': 10, 'required_evidence': ['contract']}]
        for eid in ('EX-first', 'EX-retry'):
            with self.subTest(execution=eid):
                bound = observations.bind_task_rules(template, eid)
                observations.validate_execution_rules(bound, bindings=observations.observation_rule_contract(),
                                                      execution_id=eid)
                self.assertEqual(bound[0]['subject']['id'], eid)
                due = observations.evaluate_rules(bound, {'iterations': {eid: 10}})
                self.assertEqual([row['rule_id'] for row in due], ['iteration-review'])
                self.assertEqual(observations.task_rules_from_execution(bound, eid), template)
                foreign = deepcopy(bound)
                foreign[0]['subject']['id'] = 'EX-foreign'
                with self.assertRaisesRegex(ValueError, NOT_EXECUTION):
                    observations.bind_task_rules(foreign, eid)
                with self.assertRaisesRegex(ValueError, OTHER_EXECUTION):
                    observations.task_rules_from_execution(foreign, eid)
                with self.assertRaisesRegex(ValueError, 'rule subject belongs to a different execution'):
                    observations.validate_execution_rules(foreign, bindings=observations.observation_rule_contract(),
                                                          execution_id=eid)
        self.assertEqual(template[0]['subject']['id'], '$execution')

    def test_iterations_have_only_the_checkpoint_source(self):
        # Provider events carry no iterations, so an event-sourced iteration rule is not admitted.
        rules = [{'id': 'search', 'operator': 'iteration_gte',
            'subject': {'kind': 'iteration', 'id': '$execution'},
            'basis': {'source': 'execution_events', 'unit': 'count'},
            'threshold': 2, 'required_evidence': ['contract']}]
        with self.assertRaisesRegex(ValueError, 'rule basis of iteration_gte must be source checkpoint in count'):
            observations.bind_task_rules(rules, 'EX-new')


if __name__ == '__main__':
    unittest.main()
