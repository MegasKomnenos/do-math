"""Null meanings at the real submission producer and its preserved check chain."""
from pathlib import Path
import tempfile
import unittest

from do_math import contracts, submission
from do_math.canonical import canonical_json
from support.entry import entry
from support.role_answers import seal_response


class SubmissionNullTests(unittest.TestCase):
    def test_missing_issued_schema_keeps_failure_history_and_no_submission_intent(self):
        """About 0.4 s: three preserved producer checks, two captures and sealed replay."""
        from unit.test_submission_capture import receipt_for
        clock = entry().ports.clock
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary)
            context = {'action': {'id': 'AC-null', 'role': 'maintenance'},
                       'execution_id': 'EX-null', 'snapshot': 'fixture-input',
                       'tasks': [], 'knowledge_catalog': [], 'sources': [], 'kind_definitions': {}}
            schema = contracts.schema_for('maintenance')
            submission.install_tools(workspace, context, schema, None, clock=clock)
            output = {'summary': 'Inspect', 'used_sources': [], 'questions': [],
                      'report': 'Preserve the exact check history.', 'remaining_work': []}
            seal_response(output, context, workspace)
            draft = workspace / 'draft.json'
            draft.write_bytes(canonical_json(output))
            schema_path = workspace / 'input/submission/schema.json'
            schema_bytes = schema_path.read_bytes()
            schema_path.unlink()

            missing = submission.producer_check(workspace, 'draft.json', clock=clock)
            self.assertIsNone(missing['schema_ref'])
            self.assertIsNone(missing['previous_producer_check_id'])
            self.assertFalse(missing['passed'])
            self.assertEqual([(row['rule_id'], row['path']) for row in missing['issues']],
                             [('submission.read', 'submission')])
            self.assertEqual(submission.read_producer_checks(workspace, missing['id']), [missing])

            schema_path.write_bytes(schema_bytes)
            draft.write_bytes(b'{')
            malformed = submission.producer_check(workspace, 'draft.json', clock=clock)
            self.assertEqual(malformed['schema_ref'], contracts.schema_reference(schema))
            self.assertEqual(malformed['previous_producer_check_id'], missing['id'])
            self.assertEqual([(row['rule_id'], row['path']) for row in malformed['issues']],
                             [('submission.parse', 'submission')])
            rejected = submission.seal_submission(workspace, 'draft.json', execution_id='EX-null',
                context=context, schema=schema, max_artifact_bytes=1024 * 1024, clock=clock)
            self.assertFalse(rejected['capture_eligible'])
            self.assertIsNone(rejected['intent'])
            self.assertEqual(submission.load_json(rejected['artifacts']['check.json']), rejected['check'])
            self.assertEqual([(row['rule_id'], row['path']) for row in rejected['check']['issues']],
                             [('submission.parse', 'submission')])

            draft.write_bytes(canonical_json(output))
            repaired = submission.producer_check(workspace, 'draft.json', clock=clock)
            self.assertTrue(repaired['passed'], repaired['issues'])
            self.assertEqual(repaired['issues'], [])
            history = submission.read_producer_checks(workspace, repaired['id'])
            self.assertEqual(history, [missing, malformed, repaired])
            self.assertEqual([(row['rule_id'], row['previous_check_id'], row['status'])
                              for row in repaired['repairs']],
                             [('submission.parse', malformed['id'], 'resolved')])
            summary = submission.summarize_checks(history, history_window=3)
            self.assertEqual([row['check_id'] for row in summary['unresolved']], [missing['id']])
            self.assertIsNone(summary['rule_evidence']['submission.read'][0]['schema_ref'])

            captured = submission.seal_submission(workspace, execution_id='EX-null',
                context=context, schema=schema, raw_output=canonical_json(output),
                max_artifact_bytes=1024 * 1024, clock=clock)
            self.assertTrue(captured['capture_eligible'], captured['check']['issues'])
            self.assertIsNone(captured['intent']['draft_path'])
            prefix = 'runtime/artifacts/BA-null/submission/'
            artifacts = {prefix + name: raw for name, raw in captured['artifacts'].items()}
            intent = {**captured['intent'], **{name + '_ref': prefix + name + '.json'
                                            for name in ('output', 'extensions', 'check', 'manifest')}}
            receipt = {**receipt_for(artifacts), 'execution_id': 'EX-null'}
            replay = submission.read_sealed_submission({'id': 'EX-null', 'submission_intent': intent,
                                                        'submission_receipt': receipt},
                'fixture-output', lambda path, snapshot: artifacts[path])
            self.assertEqual(replay['output'], output)
            self.assertEqual(replay['check'], captured['check'])
