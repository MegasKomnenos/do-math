"""Model assessments as a preparation producer submits them (``submission.payload_issues``, layer 1), moved from
``test_model_assessment_flow``'s ``AssessmentSubmissionTests``.

A preparation must assess every new or revised candidate exactly once; an
assessment-only preparation may only assess, or explicitly defer, its assigned
targets. The workspace is a temporary folder; the response is sealed as the
worker seals it (``research_fixtures.seal_response``). The legacy tests checked
only that some issue was reported, and most rejected inputs also lack contract
self-checks, whose coverage issue then stands beside the assessment issue
(test map 8.2). Each list is compared whole here, so the assessment rule's own
issue is pinned by its rule and message.
"""
from copy import deepcopy
from pathlib import Path
import tempfile
import unittest

from do_math.canonical import canonical_json, exact_content_hash
from do_math.contracts import schema_for
from do_math.planning import contract_hash
from do_math.submission import payload_issues
from research_fixtures import candidate, seal_response, supply_observation_rules
from runner_fixtures import common, contract_checks, rating

MODEL = ('submission.activity-extensions.json.model_assessments', 'activity-extensions.json/model_assessments')


def model(message):
    return (*MODEL, message)


def self_check(missing):
    return ('contract_check.coverage', 'activity-extensions.json/contract_checks',
            'contract self-check coverage: every candidate needs exactly one entry; missing ' + missing)


class AssessmentSubmissionTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.workspace = Path(temp.name)
        self.context = {"action": {"role": "research_preparation"}, "budget_unit": "concurrent_sessions",
                        "tasks": [], "knowledge_catalog": [], "kind_definitions": {}, "sources": []}
        self.output = {**common("research_preparation"), "candidates": [candidate("one"), candidate("two")]}

    def issues(self, extensions):
        """(rule, path, message) of each issue; candidates get their observation rules so rules never mask assessments."""
        extensions = deepcopy(extensions)
        if 'assessment_targets' not in self.context['action']:
            supply_observation_rules(self.output['candidates'], extensions)
        (self.workspace / 'activity-extensions.json').write_bytes(canonical_json(extensions))
        output = deepcopy(self.output)
        for task in self.context['tasks']:
            task.setdefault('content_sha256', exact_content_hash(task))
        seal_response(output, self.context, self.workspace)
        return [(issue['rule_id'], issue['path'], issue['message'])
                for issue in payload_issues(output, schema_for("research_preparation"), self.context, extensions, self.workspace)]

    def test_missing_candidate_assessments_are_rejected_with_missing_titles(self):
        self.assertEqual(self.issues({"model_assessments": [rating(task_title="one")]}), [
            self_check('["one", "two"]'), model('model assessment coverage: {"missing": ["two"], "unexpected": []}')])

    def test_missing_family_cannot_bypass_the_completeness_check(self):
        self.assertEqual(self.issues({}), [
            self_check('["one", "two"]'), model('model assessment coverage: {"missing": ["one", "two"], "unexpected": []}')])

    def test_exact_coverage_is_accepted_and_duplicates_and_foreign_targets_are_rejected(self):
        self.assertEqual(self.issues({"model_assessments": [rating(task_title="one"), rating(task_title="two")],
                                      "contract_checks": contract_checks(self.output["candidates"])}), [])
        expected = {('one', 'one'): 'duplicate model assessment: one',
                    ('one', 'foreign'): 'model assessment coverage: {"missing": ["two"], "unexpected": ["foreign"]}'}
        for titles, message in expected.items():
            with self.subTest(titles=titles):
                self.assertEqual(self.issues({"model_assessments": [rating(task_title=x) for x in titles]}),
                                 [self_check('["one", "two"]'), model(message)])

    def test_revised_candidate_also_needs_a_new_assessment(self):
        old = {**candidate('one'), "id": "TK-old", "revision": 1, "status": "waiting", "model_assessment": rating()}
        self.context["tasks"] = [old]
        self.context['action']['revision_targets'] = {'TK-old': {'revision': 1, 'contract_sha256': contract_hash(old)}}
        self.output["candidates"] = [{**candidate('one'), "revises_task_id": "TK-old"}]
        # The old edition's assessment does not fill the new candidate implicitly.
        self.assertEqual(self.issues({}), [
            ('submission.activity-extensions.json.revision_resolutions', 'activity-extensions.json/revision_resolutions',
             'resolve each declared target exactly once, using a task withdrawal only for task targets'),
            self_check('["one"]'), model('model assessment coverage: {"missing": ["one"], "unexpected": []}')])

    def test_empty_preparation_requires_no_candidate_assessments(self):
        self.output["candidates"] = []
        self.assertEqual(self.issues({}), [])

    def test_assessment_only_payload_cannot_edit_contracts_or_use_other_extensions(self):
        task = {**candidate('one'), 'id': 'TK-one', 'revision': 1, 'status': 'waiting'}
        self.context['tasks'] = [task]
        self.context["action"]["assessment_targets"] = {"TK-one": {"revision": 1, "contract_sha256": contract_hash(task)}}
        self.output["candidates"] = []
        good = {"model_assessments": [rating(task_id="TK-one")]}
        self.assertEqual(self.issues(good), [])
        self.output["candidates"] = [candidate('one')]
        self.assertEqual(self.issues(good), [
            ('submission.output.candidates.*.initial_observation_rules', 'output/candidates/0/initial_observation_rules',
             'observation rules must be a nonempty list of at most 16 rules'),
            model('assessment-only preparation cannot create or revise contracts')])
        self.output["candidates"] = []
        self.assertEqual(self.issues({**good, "task_dispositions": [
            {"task_id": "TK-one", "disposition": "withdraw", "reason": "change user scope"}]}), [
            ('schema.additionalProperties', 'activity-extensions.json',
             "Additional properties are not allowed ('task_dispositions' was unexpected)")])
        self.assertEqual(self.issues({"model_assessments": [rating(task_id="TK-other")]}), [
            model('model assessment coverage: {"missing": ["TK-one"], "unexpected": ["TK-other"]}')])

    def test_assessment_only_deferrals_must_cover_targets_without_overlap(self):
        self.context["action"]["assessment_targets"] = {"TK-one": {}, "TK-two": {}}
        self.output["candidates"] = []
        valid = {"model_assessments": [rating(task_id="TK-one")],
                 "model_assessment_deferrals": [{"task_id": "TK-two", "reason": "Need the required source."}]}
        self.assertEqual(self.issues(valid), [])
        self.assertEqual(self.issues({"model_assessments": [rating(task_id="TK-one")]}), [
            model('model assessment coverage: {"missing": ["TK-two"], "unexpected": []}')])
        self.assertEqual(self.issues({**valid, "model_assessments": [rating(task_id="TK-one"), rating(task_id="TK-two")]}), [
            model('assessment and deferral must identify each target exactly once')])


if __name__ == '__main__':
    unittest.main()
