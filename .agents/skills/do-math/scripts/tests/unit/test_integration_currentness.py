"""Live semantic drift is distinct from a declaration wrong at submission time."""
from copy import deepcopy
import unittest

from do_math import integration, knowledge
from do_math.git_store import GitStateStoreError
from do_math.input_basis import CurrentnessChanged


class LiveHashTests(unittest.TestCase):
    def test_disappeared_fixed_knowledge_target_is_drift_before_root_traversal(self):
        record = {'id': 'KN-fixed', 'title': 'Original observation', 'statement': 'One'}
        digest = knowledge.content_hash(record)
        context = {'action': {'role': 'research_preparation'}, 'snapshot': 'a' * 40,
                   'knowledge_catalog': [{**record, 'content_sha256': digest}]}
        output = {'integration_bundles': [{'integration_id': 'IN-fixed', 'members': [
            'output', 'activity-extensions.json/knowledge_changes/0'], 'impact_set': [],
            'authority_refs': [], 'previous_hashes': {record['id']: digest}}]}
        extensions = {'knowledge_changes': [{'id': record['id'], 'impact_set': []}]}
        self.assertEqual(integration.inspect_bundles(output, extensions, context), [])
        bundle, = integration.split_bundles(output, extensions, context)
        with self.assertRaises(CurrentnessChanged) as changed:
            integration.bundle_impact_request({}, {'executions': {'EX-fixed': {'input_snapshot': context['snapshot']}}},
                bundle, producer_execution_id='EX-fixed', input_snapshot=context['snapshot'])
        self.assertEqual(changed.exception.changes, [{'id': record['id'], 'field': 'content_sha256',
                                                      'before': digest, 'after': None}])

    def test_live_impact_gate_signals_actual_content_change(self):
        task = {'id': 'TK-fixed', 'title': 'Finite sum', 'question': 'Compute S'}
        digest = knowledge.content_hash(task)
        context = {'action': {'role': 'research_preparation'}, 'snapshot': 'a' * 40,
                   'tasks': [{**task, 'content_sha256': digest}]}
        extensions = {'revision_resolutions': [{'record_id': task['id']}]}
        output = {'integration_bundles': [{'integration_id': 'IN-fixed',
            'members': ['output', 'activity-extensions.json/revision_resolutions/0'],
            'impact_set': [], 'authority_refs': [], 'previous_hashes': {task['id']: digest}}]}
        runtime = {'tasks': {task['id']: {**task, 'question': 'Compute a different sum'}},
                   'executions': {'EX-fixed': {'input_snapshot': context['snapshot']}}}
        calls = []
        def current(instance, running, bundle):
            integration.bundle_impact_request(instance, running, bundle,
                producer_execution_id='EX-fixed', input_snapshot=context['snapshot'])
        before = deepcopy(runtime)
        receipt = integration.apply_bundles({}, runtime, output, extensions, context,
            execution_id='EX-fixed', validate_current=current,
            apply_bundle=lambda *args: calls.append('apply'), validate_candidate=lambda *args: None,
            publish=lambda *args: calls.append('publish'))
        self.assertEqual(calls, [])
        self.assertEqual(runtime, before)
        self.assertEqual([row['rule_id'] for row in receipt['issues']], ['integration.currentness'])
        self.assertEqual(integration.submission_outcome(receipt), 'premises_changed')
        self.assertEqual(integration.failure_kind(receipt['issues']), 'currentness_changed')
        self.assertEqual(receipt['bundles'][0]['next_owner'], 'refresh_decision')

    def test_storage_and_environment_failures_keep_the_engine_owner(self):
        from do_math.trust_validation import EnvironmentUnavailable
        context = {'action': {'role': 'maintenance'}, 'snapshot': 'a' * 40, 'execution_id': 'EX-fixed'}
        for error in (OSError('read failed'), GitStateStoreError('Git unavailable'),
                      EnvironmentUnavailable('toolchain unavailable', {'environment_id': 'TE-fixed'})):
            with self.subTest(error=type(error).__name__):
                def current(*args):
                    raise error
                receipt = integration.apply_bundles({}, {}, {}, {}, context, execution_id='EX-fixed',
                    validate_current=current, apply_bundle=lambda *args: self.fail('applied'),
                    validate_candidate=lambda *args: None, publish=lambda *args: self.fail('published'))
                self.assertEqual(integration.submission_outcome(receipt), 'publication_wait')
                self.assertEqual(integration.failure_kind(receipt['issues']), 'input_failure')
                self.assertEqual(receipt['bundles'][0]['next_owner'], 'engine')
