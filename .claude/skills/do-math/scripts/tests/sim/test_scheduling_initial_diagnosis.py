"""The maintenance diagnosis of a failed initial interpretation and its one bounded retry (``repair_execution``, ``core_engine``).

Each test restores an initializing instance whose initialization is adopted
(``support.scheduling_initial``) and records the failed interpretation
``EX-bad`` on its real queued action; the engine methods then run on the Sim's
engine and publish through its store. The diagnosis execution ``EX-diagnosis``
is recorded the same way (``diagnosis_execution``).
"""
import hashlib
import tempfile
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

from do_math import activities, execution_lifecycle, execution_profiles
from do_math.control_protocol import SUBMIT_INTENT
from do_math.engine import ResearchEngine
from do_math.record_schemas import RUNTIME_FIELDS
from support.engine_context import publish
from support.provider_probes import ObservedCalls
from support.scheduling_initial import GRANT, adopted_sim, initial_failure

def rejected_submission(engine, action, execution_id):
    """Produce a real rejection from a schema-valid outer envelope, not a semantic acceptance fixture."""
    from do_math import submission
    from support.governance_sim import returned
    from support.submission_obligations import structural_envelope
    if execution_id not in engine.runtime['executions']:
        returned(engine, action, execution_id)
    output, schema, context = structural_envelope(action, {})
    Draft202012Validator(schema).validate(output)
    context.update(execution_id=execution_id, snapshot=engine.head)
    output['summary'] = []
    with tempfile.TemporaryDirectory() as directory:
        issues = submission.payload_issues(output, schema, context, {}, Path(directory), clock=engine.ports.clock)
        assert [(i['rule_id'], i['path'], i['message']) for i in issues] == [
            ('schema.type', 'output/summary', "[] is not of type 'string'")], issues
        received = engine._apply_submission_bundles(action, output, {}, execution_id, context, issues)
    assert received['status'] == 'returned' and received['issues'], received
    return received, output


def diagnosis_execution(sim, diagnostic, status):
    """The maintenance execution ``EX-diagnosis`` of ``diagnostic``: running, or ended with its output accepted."""
    engine = sim.engine
    runtime = engine.runtime
    at = sim.clock.now()
    profile = next(p for p in engine.instance['execution_profiles'].values() if p['role'] == 'maintenance')
    if 'AY-diagnosis' not in runtime['activities']:
        activities.open_activity(runtime, activity_id='AY-diagnosis', activity_kind='maintenance',
                                 owner_ref='engine', input_refs=['EX-bad'], opened_at=at)
    execution = runtime['executions'].get('EX-diagnosis')
    if execution is None:
        execution = execution_lifecycle.create_execution(execution_id='EX-diagnosis', owner_activity_id='AY-diagnosis',
            actor_kind='ai', input_manifest={}, profile_ref=execution_profiles.profile_ref(profile), created_at=at)
        execution.update(role='maintenance', action=dict(diagnostic))
        activities.assign_execution(runtime, 'AY-diagnosis', execution)
        execution_lifecycle.transition_execution(execution, 'starting', at=at)
        execution_lifecycle.transition_execution(execution, 'running', at=at)
    if status == 'ended':
        # An accepted output has a receipt: the submission is recorded as the central receiver records one.
        output_ref = 'runtime/artifacts/BA-diagnosis/submission/output.json'
        engine._save({output_ref: b'{}'})
        execution = engine.runtime['executions']['EX-diagnosis']
        execution_lifecycle.record_submission_intent(execution, {'candidate_id': 'CS-diagnosis', 'output_ref': output_ref, 'manifest': []},
            {'id': 'UC-diagnosis-receipt', 'kind': SUBMIT_INTENT, 'state': 'accepted', 'execution_id': 'EX-diagnosis',
             'received_at': at})
        execution_lifecycle.transition_execution(execution, 'ended', at=at, outcome='output_accepted')
    return execution


def retry_decision(guidance):
    return {'initial_submission_diagnosis': {'decision': 'retry', 'guidance': guidance}}


class InitialDiagnosisTests(unittest.TestCase):
    def test_exhausted_initial_repairs_have_a_reachable_diagnostic_owner(self):
        sim = adopted_sim()
        engine = sim.engine
        self.assertEqual(engine.instance['config']['max_output_repairs'], 1)
        queued = next(row for row in engine.runtime['queue'] if row['role'] == 'intent_interpretation')
        engine.runtime['queue'] = []
        action = {'id': 'AC-original', 'role': 'intent_interpretation', 'target': queued['target'], 'repair_attempt': 1}
        received, output = rejected_submission(engine, action, 'EX-bad')
        with ObservedCalls(enqueue=ResearchEngine._enqueue) as observed:
            engine.route_submission_return(action, received, 'EX-bad', output)
        (_, first), *_ = observed.calls['enqueue']
        self.assertEqual((first['role'], first['target']), ('maintenance', 'EX-bad'))
        self.assertTrue(first['extra']['initial_submission_diagnosis'])
        diagnosis, = engine.runtime['queue']
        self.assertEqual((diagnosis['role'], diagnosis['target'], diagnosis['initial_submission_diagnosis']),
                         ('maintenance', 'EX-bad', True))

    def test_diagnosis_retry_preserves_the_original_and_is_bounded(self):
        sim = adopted_sim()
        action, _ = initial_failure(sim, 'output_validation')
        engine = sim.engine
        diagnostic = {'id': 'AC-diagnosis', 'role': 'maintenance', 'target': 'EX-bad', 'initial_submission_diagnosis': True}
        engine.apply_initial_diagnosis(diagnostic, retry_decision('Return the missing required field'), 'EX-diagnosis')
        self.assertEqual(engine.runtime['queue'], [])
        diagnosis_execution(sim, diagnostic, 'ended')
        engine.continue_initial_retries()
        self.assertTrue(engine.runtime['queue'], engine.runtime['waiting_actions'])
        retry = engine.runtime['queue'].pop()
        self.assertEqual(retry['target'], action['target'])
        self.assertEqual(retry['owner_activity_id'], 'AY-original')
        self.assertEqual(retry['diagnosis_attempt'], 1)
        received, output = rejected_submission(engine, retry, 'EX-again')
        engine.route_submission_return(retry, received, 'EX-again', output)
        self.assertEqual(engine.runtime['queue'], [])

    def test_failed_diagnosed_retry_is_recorded_once_and_remains_storable(self):
        sim = adopted_sim()
        action, _ = initial_failure(sim)
        engine = sim.engine
        diagnostic = {'id': 'AC-diagnosis', 'role': 'maintenance', 'target': 'EX-bad', 'initial_submission_diagnosis': True}
        engine.apply_initial_diagnosis(diagnostic, retry_decision('Retry original input'), 'EX-diagnosis')
        diagnosis_execution(sim, diagnostic, 'ended')
        engine.instance['grants'][GRANT]['status'] = 'revoked'
        with ObservedCalls(save=ResearchEngine._save) as observed:
            engine.continue_initial_retries()
            engine.continue_initial_retries()
        wait = engine.runtime['waiting_actions'][action['id']]
        self.assertIn('retry_error', wait['diagnosis'])
        self.assertEqual(engine.runtime['queue'], [])
        self.assertEqual(observed.count('save'), 1)
        Draft202012Validator(RUNTIME_FIELDS['waiting_actions']).validate(engine.runtime['waiting_actions'])
        _, _, stored = engine.store.load()
        self.assertEqual(stored['waiting_actions'][action['id']]['diagnosis']['retry_error'], wait['diagnosis']['retry_error'])

    def test_initial_diagnosis_does_not_bypass_termination_source_or_authority(self):
        reasons = {'termination': 'initial retry requires confirmed local termination and released reservations',
                   'source': 'initial retry source differs from the immutable original input',
                   'grant': 'initial operating authority: no current grant permits this action'}
        for changed, reason in reasons.items():
            with self.subTest(changed=changed):
                sim = adopted_sim()
                _, wait = initial_failure(sim)
                engine = sim.engine
                if changed == 'termination':
                    engine.runtime['executions']['EX-bad']['capacity']['local_termination'] = 'unknown'
                elif changed == 'source':
                    engine.runtime['inputs'][0]['text'] = 'changed'
                else:
                    engine.instance['grants'][GRANT]['status'] = 'revoked'
                with self.assertRaisesRegex(ValueError, reason):
                    engine._continue_initial_execution(wait, request_id='EX-diagnosis',
                                                       diagnosis={'decision': 'retry', 'guidance': 'Retry'})
                self.assertEqual(engine.runtime['queue'], [])


class DiagnosisInputTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.workspace = Path(directory.name) / 'diagnosis'
        self.sim = adopted_sim()
        initial_failure(self.sim)
        self.engine = self.sim.engine

    def diagnosis_context(self):
        return self.engine._context({'id': 'AC-diagnosis', 'role': 'maintenance', 'target': 'EX-bad',
                                     'initial_submission_diagnosis': True}, self.workspace)

    def test_initial_diagnosis_receives_the_original_role_contract_bytes(self):
        prefix = 'runtime/artifacts/BA-original'
        originals = {prefix + '/input.txt': b'Original role contract and fixed prompt',
                     prefix + '/schema.json': b'{"type":"object"}',
                     prefix + '/input/submission/context.json': b'{"fixed":"original input"}'}
        prompt = originals[prefix + '/input.txt']
        failed = self.engine.runtime['executions']['EX-bad']
        failed['input_bundle'] = 'BA-original'
        # The role input manifest names the archived prompt.
        failed['input_manifest'] = {'prompt': {'artifact_ref': prefix + '/input.txt',
                                               'sha256': hashlib.sha256(prompt).hexdigest(), 'bytes': len(prompt)}}
        self.engine._save(originals)
        materials = self.diagnosis_context()['initial_submission_diagnosis']['materials']
        self.assertEqual({row['artifact_ref'] for row in materials}, set(originals))
        for row in materials:
            raw = (self.workspace / row['local_path']).read_bytes()
            self.assertEqual(raw, originals[row['artifact_ref']])
            self.assertEqual(hashlib.sha256(raw).hexdigest(), row['sha256'])

    def test_initial_diagnosis_receives_the_failed_checkpoint_evidence_files(self):
        # 계약/유지보수.md 42 and 공통-실행.md 49: the diagnosis reads the checkpoint and its evidence.
        evidence = b'partial interpretation notes'
        reference = 'runtime/artifacts/BA-checkpoint/evidence/notes.txt'
        publish(self.engine, {reference: evidence})
        self.engine.runtime.setdefault('checkpoints', {})['EX-bad'] = {'kind': 'worker_checkpoint',
            'checkpoint': {'current_claim': 'partial'}, 'evidence_files': [{'path': 'notes.txt',
            'artifact_ref': reference, 'sha256': hashlib.sha256(evidence).hexdigest(), 'bytes': len(evidence)}]}
        row = next(row for row in self.diagnosis_context()['initial_submission_diagnosis']['materials']
                   if row['artifact_ref'] == reference)
        self.assertEqual((self.workspace / row['local_path']).read_bytes(), evidence)


class InitialFailureKindTests(unittest.TestCase):
    def assert_one_authorized_followup(self, kind, stage):
        sim = adopted_sim()
        action, _ = initial_failure(sim, kind, stage)
        engine = sim.engine
        original = dict(engine.instance['lifecycle']['immutable_input'])
        engine.route_failed_action(action, 'EX-bad', reason='Diagnose actual failure')
        diagnostic = engine.runtime['queue'].pop()
        self.assertEqual(diagnostic['role'], 'maintenance')
        engine._action_lifecycle_gate(diagnostic)
        diagnosis_execution(sim, diagnostic, 'running')
        engine.apply_initial_diagnosis(diagnostic, retry_decision('Use the preserved contract'), 'EX-diagnosis')
        self.assertEqual(engine.runtime['queue'], [], 'candidate application cannot publish a native recovery')
        diagnosis_execution(sim, diagnostic, 'ended')
        engine.continue_initial_retries()
        self.assertTrue(engine.runtime['queue'], engine.runtime['waiting_actions'])
        retry = engine.runtime['queue'].pop()
        self.assertEqual(retry['stage'], stage)
        self.assertEqual(retry['owner_activity_id'], 'AY-original')
        self.assertEqual(retry['continuation_of'], 'EX-bad')
        self.assertEqual(retry['diagnosis_attempt'], 1)
        self.assertEqual(engine.instance['lifecycle']['immutable_input'], original)
        if kind == 'output_validation':
            self.assertEqual(retry['repair']['retry_bundle_ids'], ['IN-pending'])
        received, output = rejected_submission(engine, retry, 'EX-again')
        engine.route_submission_return(retry, received, 'EX-again', output)
        self.assertEqual(engine.runtime['queue'], [])

    def test_an_output_validation_failure_reaches_one_authorized_followup(self):
        for stage in ('interpret', 'check'):
            with self.subTest(stage=stage):
                self.assert_one_authorized_followup('output_validation', stage)

    def test_an_execution_failure_reaches_one_authorized_followup(self):
        for stage in ('interpret', 'check'):
            with self.subTest(stage=stage):
                self.assert_one_authorized_followup('execution_failure', stage)

    def test_a_submission_failure_reaches_one_authorized_followup(self):
        for stage in ('interpret', 'check'):
            with self.subTest(stage=stage):
                self.assert_one_authorized_followup('submission_failure', stage)


if __name__ == '__main__':
    unittest.main()
