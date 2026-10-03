"""중앙 묶음 구조의 빈 분기: 좌표·중복·권한·기존 판본을 정확히 지목한다."""
from copy import deepcopy
import unittest

from do_math import integration
from support.record_builders import research_work_context, two_observation_output


class BundleCoordinateTests(unittest.TestCase):
    def test_nonobject_and_nonarray_envelopes_have_structured_rejections(self):
        context = research_work_context()
        for output, extensions, rule, path, message in [
                ([], {}, 'integration.manifest', 'output', 'response and extensions must be objects'),
                ({}, [], 'integration.manifest', 'activity-extensions.json', 'response and extensions must be objects'),
                (two_observation_output(), {'knowledge_metadata': None}, 'integration.members',
                 'activity-extensions.json', 'extension families must be arrays: knowledge_metadata')]:
            with self.subTest(rule=rule, path=path):
                self.assertEqual(integration.inspect_bundles(output, extensions, context),
                                 [integration.issue(rule, path, message)])

    def test_duplicate_bundle_ids_and_unassigned_member_are_distinguished(self):
        output = two_observation_output()
        duplicate = deepcopy(output)
        duplicate['integration_bundles'][1]['integration_id'] = 'IN-A'
        self.assertEqual(integration.inspect_bundles(duplicate, {}, research_work_context()),
            [integration.issue('integration.members', 'output/integration_bundles', 'integration IDs must be unique')])
        missing = deepcopy(output)
        missing['integration_bundles'].pop()
        self.assertEqual(integration.inspect_bundles(missing, {}, research_work_context()),
            [integration.issue('integration.members', 'output/knowledge/1', 'mutation has no declared integration bundle')])
        unknown = deepcopy(output)
        unknown['integration_bundles'][0]['members'].append('output/knowledge/99')
        self.assertEqual(integration.inspect_bundles(unknown, {}, research_work_context()),
            [integration.issue('integration.members', 'output/knowledge/99', 'unknown or multiply assigned member')])

    def test_new_identity_and_cross_bundle_metadata_closure_are_not_authority_errors(self):
        output = two_observation_output()
        output['knowledge'][1]['title'] = 'A'
        self.assertEqual(integration.inspect_bundles(output, {}, research_work_context()),
            [integration.issue('integration.new_identity', 'output/knowledge/1', 'duplicate new identity: A')])
        output = two_observation_output()
        coordinate = 'activity-extensions.json/knowledge_metadata/0'
        output['integration_bundles'][1]['members'].append(coordinate)
        self.assertEqual(integration.inspect_bundles(output, {'knowledge_metadata': [{'title': 'A'}]}, research_work_context()),
            [integration.issue('integration.reference_closure', coordinate,
                               'merge bundles referencing new object: A', 'IN-B')])

    def test_unknown_authority_names_the_exact_reference_and_owner(self):
        output = two_observation_output()
        output['integration_bundles'][1]['authority_refs'] = ['GR-outside']
        self.assertEqual(integration.inspect_bundles(output, {}, research_work_context()),
            [integration.issue('integration.authority_reference', 'output/integration_bundles',
                               'authority is not in the fixed visible input: GR-outside', 'IN-B')])

    def test_read_failure_is_classified_by_rule_not_error_text(self):
        self.assertEqual(integration.failure_kind([{'rule_id': 'submission.read', 'message': 'schema.type'}]), 'input_failure')
        self.assertEqual(integration.failure_kind([{'rule_id': 'unrelated', 'message': 'submission.read'}]), 'output_contract')

    def test_empty_impact_assignment_is_rejected_before_schema_generation(self):
        with self.assertRaisesRegex(ValueError, '^impact review must name an actual plan$'):
            integration.impact_review_response_schema({'plans': {}})
