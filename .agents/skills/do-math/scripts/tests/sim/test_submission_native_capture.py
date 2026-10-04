"""The engine's central capture of a native final (``_collect_submitted_result``) on a Sim's engine and store.

The start is the legacy ``engine_fixtures.start_native_final`` on a restored
Sim (``support.submission_scenes.native_scene``): the running maintenance
execution ``EX-history`` with its sealed input bundle, installed tools and
decision basis. The provider evidence is the explicit fixture
``support.submission_receiver.native_result`` (its launch ticket from the Sim's
Jobs and clock ports). The capture of a real Windows Job's collection is the
boundary test ``boundary.test_submission_native_job``.

The public activation already sealed its own central checks, so a seal count
the legacy test compared with 1 is the activation's count plus 1 here.
"""
from copy import deepcopy
import hashlib
import json
import unittest

from do_math.canonical import canonical_json
from do_math.execution_lifecycle import NATIVE_FINAL_RECEIPT, transition_execution
from do_math.payloads import json_safe
from support.engine_context import damage
from support.sim import warm_template
from support.submission_receiver import native_result, submit
from support.submission_scenes import lost_acknowledgment, native_scene, unmatched

setUpModule = warm_template


class NativeFinalGitTests(unittest.TestCase):
    def setUp(self):
        self.scene = native_scene()
        self.base = self.engine._submission_check_summary(self.engine.head, self.engine.runtime)
        self.assertEqual((self.base['status'], self.base['unresolved']), ('verified', []), self.base)

    @property
    def engine(self):
        return self.scene.engine

    def native(self, execution, raw):
        scene = self.scene
        return native_result(scene.sim, execution, scene.context, raw, scene.workspace)

    def collect(self, execution, result, engine=None):
        scene = self.scene
        return (engine or self.engine)._collect_submitted_result(execution, result, scene.context, scene.schema,
                                                                 scene.workspace)

    def test_terminated_native_recovery_records_the_real_receipt_without_reopening_the_attempt(self):
        scene = self.scene
        engine = self.engine
        execution = engine.runtime['executions']['EX-history']
        raw = canonical_json(scene.output)
        result = self.native(execution, raw)
        transition_execution(execution, 'stopping', at=scene.sim.clock.now())
        transition_execution(execution, 'ended', at=scene.sim.clock.now(), outcome='execution_incomplete',
                             disposition='preserved_for_followup')
        engine._save()
        execution = engine.runtime['executions']['EX-history']
        before = deepcopy(execution)
        parent = engine.head
        receipt = engine._capture_native_submission(execution, result, scene.context, scene.schema,
            scene.workspace, raw, recovery_request='UC-native-recovery')
        self.assertEqual(receipt, {
            'id': receipt['id'], 'kind': NATIVE_FINAL_RECEIPT, 'state': 'accepted',
            'execution_id': execution['id'], 'received_at': scene.sim.clock.now(),
            'parent_snapshot': parent, 'final_sha256': hashlib.sha256(raw).hexdigest(),
            'recovery_request_id': 'UC-native-recovery', 'payload': receipt['payload']})
        self.assertEqual(execution['status'], 'ended')
        self.assertEqual(execution['outcome'], 'execution_incomplete')
        self.assertEqual(execution['transitions'], before['transitions'])
        self.assertEqual(execution['ended_at'], before['ended_at'])
        self.assertEqual(execution['result_disposition'], before['result_disposition'])
        self.assertEqual(execution['submission_receipt'], receipt)
        self.assertEqual(execution['authority_revocation'], {
            'scope': 'execution_research', 'reason': 'submission_intent',
            'at': receipt['received_at'], 'receipt_id': receipt['id']})
        self.assertEqual(execution, {**before, 'submission_intent': execution['submission_intent'],
            'submission_receipt': receipt, 'authority_revocation': {
                'scope': 'execution_research', 'reason': 'submission_intent',
                'at': receipt['received_at'], 'receipt_id': receipt['id']}})
        self.assertEqual(engine.store.read(execution['submission_intent']['output_ref'], engine.head), raw)
        published = deepcopy(execution)
        engine._reload()
        self.assertEqual(engine.runtime['executions']['EX-history'], published)

    def test_rejected_native_final_leaves_explicit_retry_to_the_existing_fresh_execution_path(self):
        execution = self.engine.runtime['executions']['EX-history']
        result = self.native(execution, b'{malformed')
        failed = self.collect(execution, result)
        self.assertEqual(failed['status'], 'failed')
        self.assertIn('central structural validation', failed['error'])
        execution = self.engine.runtime['executions']['EX-history']
        reference = 'runtime/artifacts/BA-native-rejection/result.json'
        execution['result_ref'] = reference
        self.engine._save({reference: canonical_json(json_safe(failed))})
        head = self.engine.head
        execution = self.engine.runtime['executions']['EX-history']
        self.assertFalse(self.engine._resume_initial_native_final({'id': 'UC-explicit-retry'}, {}, execution))
        self.assertNotIn('submission_intent', execution)
        self.assertEqual(self.engine.head, head)
        self.assertEqual(json.loads(self.engine.store.read(reference, self.engine.head))['error'], failed['error'])

    def test_explicit_early_seal_precedes_different_final_and_damage_never_falls_back(self):
        scene = self.scene
        _, receipt = submit(scene, 'CT-early', json.dumps(scene.output, ensure_ascii=False).encode())
        self.assertEqual(receipt['state'], 'accepted', receipt)
        execution = self.engine.runtime['executions']['EX-history']
        result = {'status': 'completed', 'output': {'summary': 'alternate'}, 'collection': 'provider_evidence_only'}
        collected = self.collect(execution, result)
        self.assertEqual(collected['output'], scene.output)
        # Sealed rows are matched once per process (이음새-정본.md §3); damage is found by a process that
        # has not matched the row yet: the engine of an unmatched copy whose sealed output bytes changed.
        other = unmatched(scene.sim)
        reference = other.runtime['executions']['EX-history']['submission_intent']['output_ref']
        head = damage(other.store, reference, b'{"summary":"damaged"}')
        other._reload()
        self.assertEqual(other.head, head)
        rejected = self.collect(other.runtime['executions']['EX-history'], result, engine=other)
        self.assertEqual(rejected['status'], 'failed')
        self.assertIsNone(rejected['output'])
        self.assertEqual(rejected['error'],
                         'existing sealed submission cannot be read: sealed submission output hash differs: ' + reference)
        self.assertEqual(other.head, head)

    def test_stopped_currentness_and_revoked_authority_preserve_without_capture(self):
        engine = self.engine
        execution = engine.runtime['executions']['EX-history']
        result = self.native(execution, json.dumps(self.scene.output).encode())
        original_runtime, original_instance = deepcopy(engine.runtime), deepcopy(engine.instance)
        head = engine.head
        for boundary in ('user_stop', 'paused', 'changed_input', 'revoked_grant', 'stopped_result', 'no_barrier'):
            with self.subTest(boundary=boundary):
                engine.runtime, engine.instance = deepcopy(original_runtime), deepcopy(original_instance)
                execution = engine.runtime['executions']['EX-history']
                value = deepcopy(result)
                if boundary == 'user_stop':
                    execution['stop_requested'] = 'user'
                elif boundary == 'paused':
                    engine.runtime['status'] = 'paused'
                    engine.instance['lifecycle']['state'] = 'paused'
                elif boundary == 'changed_input':
                    execution['currentness_changes'] = [{'field': 'test'}]
                elif boundary == 'revoked_grant':
                    engine.instance['grants'][execution['grant_id']]['status'] = 'revoked'
                elif boundary == 'stopped_result':
                    value['status'] = 'stopped'
                else:
                    value['execution']['collect']['termination_barrier']['confirmed'] = False
                rejected = self.collect(execution, value)
                self.assertEqual(rejected['status'], 'failed', rejected)
                self.assertNotIn('submission_intent', execution)
                self.assertEqual(engine.head, head)
                self.assertFalse(any(e['kind'] == 'submission_checked' and e.get('target') == 'EX-history'
                                     for e in engine.runtime['events']))
                self.assertEqual([e for e in engine.runtime['events'] if e['kind'] == 'submission_checked'],
                                 [e for e in original_runtime['events'] if e['kind'] == 'submission_checked'])

    def test_lost_cas_acknowledgment_resolves_one_native_capture(self):
        engine = self.engine
        execution = engine.runtime['executions']['EX-history']
        result = self.native(execution, json.dumps(self.scene.output).encode())
        with lost_acknowledgment(self.scene.sim) as lost:
            collected = self.collect(execution, result)
        self.assertEqual(len(lost), 1, 'the capture published no commit')
        self.assertEqual(collected['status'], 'completed', collected)
        self.assertEqual(self.engine.head, lost[0])
        summary = self.engine._submission_check_summary(self.engine.head, self.engine.runtime)
        self.assertEqual(summary['status'], 'verified', summary)
        self.assertEqual(summary['seal_count'], self.base['seal_count'] + 1)

    def test_malformed_native_json_is_preserved_as_one_rejected_central_check(self):
        engine = self.engine
        execution = engine.runtime['executions']['EX-history']
        result = self.native(execution, b'{"report":')
        rejected = self.collect(execution, result)
        self.assertEqual(rejected['status'], 'failed')
        self.assertNotIn('submission_intent', self.engine.runtime['executions']['EX-history'])
        summary = self.engine._submission_check_summary(self.engine.head, self.engine.runtime)
        self.assertEqual(summary['status'], 'verified', summary)
        self.assertEqual(summary['seal_count'], self.base['seal_count'] + 1, rejected)
        self.assertTrue(summary['unresolved'])
        head = self.engine.head
        self.collect(self.engine.runtime['executions']['EX-history'], result)
        self.assertEqual(self.engine.head, head)


class NativeRepairTests(unittest.TestCase):
    def setUp(self):
        # The running maintenance execution is registered on a restored Sim's activation.
        self.scene = native_scene()

    def test_normal_malformed_final_routes_back_to_producer(self):
        scene = self.scene
        engine = scene.engine
        execution = engine.runtime['executions']['EX-history']
        raw = b'{"report":'
        result = native_result(scene.sim, execution, scene.context, raw, scene.workspace)
        received = engine._collect_submitted_result(execution, result, scene.context, scene.schema, scene.workspace)
        self.assertEqual(received['error_kind'], 'output_validation')
        engine = scene.engine
        transition_execution(engine.runtime['executions'][execution['id']], 'stopping', at=scene.sim.clock.now())
        engine._receive_submission(scene.context['action'], received, execution['id'], scene.context, scene.schema,
                                   scene.workspace)
        retry = next(a for a in engine.runtime['queue'] if a.get('continuation_of') == execution['id'])
        self.assertEqual(retry['role'], scene.context['action']['role'])
        self.assertEqual(retry['repair_attempt'], 1)
        self.assertEqual(engine.store.read(retry['repair']['raw_output_ref'], engine.head), raw)


if __name__ == '__main__':
    unittest.main()
