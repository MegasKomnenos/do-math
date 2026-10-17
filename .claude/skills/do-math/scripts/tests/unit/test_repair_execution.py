"""Installation repair judgments (``repair_execution``, ``supervision``; layer 2) over a runtime that holds one
accepted diagnosis of an ended failure (``record_fixtures.installation_repair_state``)."""
from copy import deepcopy
from pathlib import Path
import tempfile
import unittest

from do_math import activities, repair_execution
from do_math.repair_execution import installation_failure, pending_installation_repair, resume_installation_repair
from do_math.supervision import collect_repair_verification, start_guard
from support.record_builders import installation_repair_state

REFUSED = 'installation repair requires a preserved accepted diagnosis of an ended failure'


class InstallationIdentityTests(unittest.TestCase):
    def test_unavailable_or_moving_source_head_never_certifies_an_installed_commit(self):
        from support.operator_finish_ports import SourceGit
        from do_math.repair_execution import installation_evidence
        from do_math.canonical import exact_content_hash
        import hashlib
        class MovingHead(SourceGit):
            def project_snapshot(self, project_root, repository_root, *, should_stop=None):
                self.source_commit = 'c' * 40
                return super().project_snapshot(project_root, repository_root, should_stop=should_stop)
        class UnreadableHead(SourceGit):
            def object_info(self, repository, specs):
                raise OSError('source is offline')
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            raw = b'installed document\n'
            (root / 'SKILL.md').write_bytes(raw)
            version = exact_content_hash({'SKILL.md': hashlib.sha256(raw).hexdigest()})
            for backend, reason in ((SourceGit(root, commit=None), 'source HEAD is not an available commit'),
                    (MovingHead(root), 'source HEAD changed during observation'),
                    (UnreadableHead(root), 'OSError: source is offline')):
                with self.subTest(reason=reason):
                    found = installation_evidence(root, backend=backend)
                    self.assertEqual(found['source_status'], 'unavailable')
                    self.assertIsNone(found['source_commit'])
                    self.assertEqual(found['source_reason'], reason)
                    self.assertEqual(found['installation_version'], version)
                    self.assertEqual((root / 'SKILL.md').read_bytes(), raw)
                    self.assertEqual(backend.objects, {})

    def test_identity_covers_the_installed_skill_but_not_its_tests(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in ('scripts/do_math/a.py', 'scripts/tests/test_a.py', 'examples/case.json'):
                (root / name).parent.mkdir(parents=True, exist_ok=True)
                (root / name).write_text('one', encoding='utf-8')
            before = repair_execution.installation_sha256(root)
            # A regression test alone does not reopen the same failure's automatic repair.
            (root / 'scripts/tests/test_a.py').write_text('two', encoding='utf-8')
            self.assertEqual(repair_execution.installation_sha256(root), before)
            (root / 'examples/case.json').write_text('two', encoding='utf-8')
            self.assertNotEqual(repair_execution.installation_sha256(root), before)


class InstallationRepairTests(unittest.TestCase):
    def test_installation_request_requires_accepted_diagnosis_and_keeps_stable_identity(self):
        runtime, record = installation_repair_state()
        before = installation_failure(runtime, record)
        self.assertEqual({key: before[key] for key in ('kind', 'diagnosis_id', 'target_execution_id', 'repair_target')},
                         {'kind': 'installation_defect', 'diagnosis_id': 'OD-repair', 'target_execution_id': 'EX-failed',
                          'repair_target': 'installation:scripts/do_math/task_scope.py'})
        record['result']['installation_repair'].update(status='failed', attempted_by='EX-repair')
        record['status'] = 'installation_repair_waiting'
        self.assertEqual(installation_failure(runtime, record), before)
        runtime['executions']['EX-failed']['contract_sha256'] = 'changed-contract'
        self.assertNotEqual(installation_failure(runtime, record)['failure_sha256'], before['failure_sha256'])
        runtime['executions']['EX-diagnosis']['outcome'] = 'execution_incomplete'
        with self.assertRaisesRegex(ValueError, REFUSED):
            installation_failure(runtime, record)

    def test_unattempted_installation_diagnosis_is_not_starved_by_an_old_wait(self):
        runtime, record = installation_repair_state()
        record['status'] = 'installation_repair_waiting'
        fresh = {**deepcopy(record), 'id': 'OD-fresh', 'status': 'installation_repair_pending'}
        runtime['operational_dispositions'][fresh['id']] = fresh
        self.assertEqual(pending_installation_repair(runtime)['id'], 'OD-fresh')
        del runtime['operational_dispositions']['OD-fresh']
        self.assertEqual(pending_installation_repair(runtime)['id'], 'OD-repair')
        record['status'] = 'applied'
        self.assertIsNone(pending_installation_repair(runtime))

    def test_installation_repair_continues_latest_rejected_bundles_without_resetting_count(self):
        runtime, record = installation_repair_state()
        previous = deepcopy(runtime['waiting_actions']['AC-work']['action'])
        target = deepcopy(runtime['executions']['EX-failed'])
        waiting = deepcopy(runtime['activities']['AY-work']['waiting'])
        self.assertIsNone(activities.successor_state(runtime, 'EX-failed'))
        action = resume_installation_repair(runtime, record, repaired_by='EX-repair', at='2026-09-22T01:00:00Z')
        self.assertEqual(action['repair']['execution_id'], 'EX-failed')
        self.assertEqual(action['repair_attempt'], 2)
        self.assertEqual(action['continuation_of'], 'EX-failed')
        self.assertEqual(runtime['waiting_actions'], {})
        self.assertEqual(record['status'], 'applied')
        self.assertEqual(record['result']['installation_repair']['continuation_action_id'], action['id'])
        self.assertEqual(action, {**previous, 'continuation_of': 'EX-failed',
                                  'owner_activity_id': target['owner_activity_id'], 'context_origin': []})
        activity = runtime['activities']['AY-work']
        self.assertEqual(activity['status'], 'ready')
        self.assertNotIn('waiting', activity)
        self.assertEqual(activity['resumed_at'], '2026-09-22T01:00:00Z')
        self.assertEqual(activity['followups'], [{'action_id': 'AC-work', 'execution_id': 'EX-failed',
            'reason': 'verified_installation_repair:OD-repair', 'next_owner': 'engine'}])
        self.assertEqual(waiting['condition'], {'error': 'receiver'})
        self.assertEqual(runtime['executions']['EX-failed'], target)
        self.assertEqual(activities.successor_state(runtime, 'EX-failed'), {
            'state': 'in_progress', 'execution_ids': [], 'live_execution_ids': [], 'action_ids': ['AC-work']})
        self.assertEqual(record['result']['installation_repair']['status'], 'repaired')
        self.assertEqual(record['result']['installation_repair']['repaired_by'], 'EX-repair')
        self.assertEqual(runtime['queue'], [action])
        self.assertEqual(runtime['status'], 'ready')


class InstallationTargetTests(unittest.TestCase):
    def test_a_repair_target_is_an_installed_file_and_the_failure_keeps_its_artifacts(self):
        from do_math.repair_execution import validate_installation_target
        target = {'status': 'ended', 'error': 'receiver rejected', 'result_ref': 'R', 'submitted_output_ref': 'O'}
        disposition = {'meaning_preserving': True, 'repair_target': 'installation:scripts/do_math/a.py'}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'scripts/do_math').mkdir(parents=True)
            (root / 'scripts/do_math/a.py').write_text('code', encoding='utf-8')
            self.assertEqual(validate_installation_target(disposition, target, root), ['R', 'O'])
            with self.assertRaisesRegex(ValueError, 'installation repair cannot change research meaning or authority'):
                validate_installation_target({**disposition, 'meaning_preserving': 'yes'}, target, root)
            for relative in ('', '../outside.py', 'scripts\\do_math\\a.py', 'C:/x.py', 'scripts/do_math/b.py', './a.py'):
                with self.subTest(relative=relative), self.assertRaisesRegex(
                        ValueError, 'installation repair target must name an existing file inside the installed skill'):
                    validate_installation_target({**disposition, 'repair_target': 'installation:' + relative}, target, root)
            with self.assertRaisesRegex(ValueError, 'installation repair requires a preserved ended failure'):
                validate_installation_target(disposition, {**target, 'status': 'running'}, root)
            with self.assertRaisesRegex(ValueError, 'installation defect has no preserved failure artifacts'):
                validate_installation_target(disposition, {'status': 'ended', 'error': 'x'}, root)

    def test_a_repair_without_a_held_request_continues_the_failed_action_itself(self):
        runtime, record = installation_repair_state()
        del runtime['waiting_actions']['AC-work']
        owner = runtime['activities']['AY-work']
        activities.resume_activity(runtime, owner['id'], condition=owner['waiting']['condition'],
                                   at='2026-09-22T00:30:00Z')
        action = resume_installation_repair(runtime, record, repaired_by='EX-repair', at='2026-09-22T01:00:00Z')
        self.assertEqual((action['continuation_of'], action['role']), ('EX-failed', 'research_plan'))
        self.assertNotIn('repair_attempt', action)
        self.assertEqual(runtime['queue'], [action])
        self.assertEqual(record['result']['installation_repair']['continuation_action_id'], action['id'])
        self.assertEqual((owner['status'], owner['resumed_at']), ('ready', '2026-09-22T00:30:00Z'))

    def test_a_repair_already_continued_by_a_successor_settles_on_it(self):
        runtime, record = installation_repair_state()
        runtime['executions']['EX-next'] = {'id': 'EX-next', 'role': 'research_plan', 'status': 'running',
                                            'continuation_of': 'EX-failed', 'owner_activity_id': 'AY-work'}
        runtime['executions']['EX-failed']['pending_operational_disposition'] = 'OD-repair'
        runtime['status'] = 'waiting'
        self.assertIsNone(resume_installation_repair(runtime, record, repaired_by='EX-repair', at='2026-09-22T01:00:00Z'))
        self.assertEqual(record['status'], 'applied')
        repair = record['result']['installation_repair']
        self.assertEqual((repair['status'], repair['repaired_by'], repair['successor']['state']),
                         ('repaired', 'EX-repair', 'in_progress'))
        self.assertNotIn('pending_operational_disposition', runtime['executions']['EX-failed'])
        self.assertEqual((runtime['status'], runtime['queue']), ('ready', []))


class RecoveryJudgmentTests(unittest.TestCase):
    """What the failure-only installation recovery (``scheduled_operator.recovery``) decides from its inputs."""

    def test_a_recovery_needs_preserved_failure_evidence(self):
        from do_math.repair_execution import check_recovery_failure
        for failure in (None, {'kind': 'engine_unavailable', 'error': 'import failed'},
                        {'kind': 'installation_defect', 'error': 'receiver'}):
            with self.subTest(failure=failure):
                self.assertIsNone(check_recovery_failure(failure))
        for failure in ({'kind': 'provider_limit', 'error': 'quota'}, {'kind': 'installation_defect', 'error': ''}):
            with self.subTest(failure=failure), self.assertRaisesRegex(ValueError, 'recovery requires preserved engine failure evidence'):
                check_recovery_failure(failure)

    def test_supervision_blocks_hold_or_disable_a_recovery(self):
        from do_math.repair_execution import recovery_block_outcome
        failure = {'kind': 'engine_unavailable', 'error': 'x'}
        self.assertEqual(recovery_block_outcome('disabled', failure), {'outcome': 'recovery_disabled', 'failure': failure})
        self.assertEqual(recovery_block_outcome('paused', failure), {'outcome': 'held'})
        self.assertIsNone(recovery_block_outcome(None, failure))
        self.assertIsNone(recovery_block_outcome('installation_repair', failure))

    def test_the_failure_to_repair_is_the_given_one_or_the_pending_diagnosis(self):
        from do_math.repair_execution import failure_to_repair, matching_diagnosis
        runtime, record = installation_repair_state()
        given = {'kind': 'engine_unavailable', 'error': 'x'}
        self.assertIs(failure_to_repair(runtime, given), given)
        pending = failure_to_repair(runtime, None)
        self.assertEqual(pending, installation_failure(runtime, record))
        self.assertIs(matching_diagnosis(runtime, pending), record)
        self.assertIsNone(matching_diagnosis(runtime, given))
        for changed in ({**pending, 'error': 'another error'}, {**pending, 'diagnosis_id': 'OD-absent'}):
            with self.subTest(changed=changed['diagnosis_id']), self.assertRaisesRegex(
                    ValueError, 'installation diagnosis is missing or differs from its published record'):
                matching_diagnosis(runtime, changed)
        record['status'] = 'applied'
        self.assertIsNone(failure_to_repair(runtime, None))

    def test_an_unended_execution_blocks_until_its_local_termination_is_confirmed(self):
        from do_math.repair_execution import unconfirmed_termination
        from support.fakes.jobs import FakeJobs
        jobs = FakeJobs()
        earlier_owner = {**jobs.owner, 'creation_filetime': '1'}  # the same PID of an ended process
        ticket = {'execution_id': 'EX-live', 'profile_sha256': 'a' * 64, 'kind': 'owner_thread',
                  'owner': earlier_owner, 'job_name': None, 'phase': 'dispatched'}
        runtime = {'executions': {'EX-done': {'id': 'EX-done', 'status': 'ended'}}}
        self.assertIsNone(unconfirmed_termination(runtime, jobs=jobs))
        runtime['executions']['EX-live'] = {'id': 'EX-live', 'status': 'running'}
        self.assertEqual(unconfirmed_termination(runtime, jobs=jobs), 'EX-live')
        runtime['executions']['EX-live']['launch_ticket'] = ticket
        self.assertIsNone(unconfirmed_termination(runtime, jobs=jobs))
        runtime['executions']['EX-live']['launch_ticket'] = {**ticket, 'owner': jobs.owner_identity()}
        self.assertEqual(unconfirmed_termination(runtime, jobs=jobs), 'EX-live')

    def test_a_failure_is_identified_by_its_diagnosis_or_its_fields(self):
        from do_math.repair_execution import failure_identity
        runtime, record = installation_repair_state()
        diagnosed = installation_failure(runtime, record)
        self.assertEqual(failure_identity(diagnosed, record), diagnosed['failure_sha256'])
        engine_failure = {'kind': 'engine_unavailable', 'error': 'import failed', 'error_type': 'ImportError'}
        identity = failure_identity(engine_failure, None)
        self.assertRegex(identity, '^[0-9a-f]{64}$')
        self.assertEqual(failure_identity({**engine_failure, 'error_type': 'OSError'}, None), identity)
        self.assertNotEqual(failure_identity({**engine_failure, 'error': 'other'}, None), identity)

    def test_one_automatic_repair_per_failure_and_installation_unless_no_repair_was_judged(self):
        from do_math.repair_execution import already_attempted
        identity = {'failure_sha256': 'f' * 64, 'installation_sha256': 'i' * 64}

        def runtime(**execution):
            return {'executions': {'EX-r': {'role': 'recovery', 'input_manifest': {'repair_identity': identity},
                                            **execution}}}
        self.assertTrue(already_attempted(runtime(), 'f' * 64, 'i' * 64))
        self.assertFalse(already_attempted(runtime(), 'f' * 64, 'j' * 64))
        self.assertFalse(already_attempted(runtime(role='maintenance'), 'f' * 64, 'i' * 64))
        limited = {'result_disposition': {'recovery': 'recovery_provider_limited'}}
        self.assertFalse(already_attempted(runtime(**limited), 'f' * 64, 'i' * 64))
        held = {'result_disposition': {'recovery': 'recovery_held'}}
        self.assertFalse(already_attempted(runtime(**held), 'f' * 64, 'i' * 64))
        self.assertTrue(already_attempted(runtime(**held, submission_receipt={'state': 'accepted'}), 'f' * 64, 'i' * 64))
        with self.assertRaisesRegex(ValueError, '^recovery disposition must be an object$'):
            already_attempted(runtime(result_disposition='invalid'), 'f' * 64, 'i' * 64)

    def test_the_repair_prompt_names_its_scope_and_carries_the_failure_record(self):
        import json
        from do_math.repair_execution import repair_prompt
        failure = {'kind': 'installation_defect', 'error': 'receiver'}
        arguments = dict(installation='C:/skill', repository='C:/repo', instance='RI-1', execution_id='EX-r', reference={'id': 'EP-1'})
        diagnosed = repair_prompt(failure, [{'artifact_ref': 'A'}], diagnosed=True, **arguments)
        self.assertTrue(diagnosed.startswith('Repair only the independently diagnosed do-math installation defect'))
        self.assertIn('Do not start the engine or wait for research', diagnosed)
        record = json.loads(diagnosed.rsplit('\n', 1)[1])
        self.assertEqual(record, {'failure': failure, 'failure_inputs': [{'artifact_ref': 'A'}], 'installation': 'C:/skill',
                                  'repository': 'C:/repo', 'instance': 'RI-1', 'execution_id': 'EX-r', 'profile_ref': {'id': 'EP-1'}})
        self.assertTrue(repair_prompt(failure, [], diagnosed=False, **arguments).startswith(
            'Repair only the do-math installation defect that prevents this engine from starting.'))

    def test_the_runner_result_gives_the_outcome_and_a_report_its_receipt(self):
        from do_math.execution_lifecycle import RECOVERY_REPORT_RECEIPT
        from do_math.repair_execution import recovery_report_receipt, runner_outcome
        self.assertEqual(runner_outcome({'status': 'completed'}), 'repaired')
        self.assertEqual(runner_outcome({'status': 'failed'}), 'recovery_failed')
        self.assertEqual(runner_outcome({'status': 'failed', 'error_kind': 'provider_limit'}), 'recovery_provider_limited')
        self.assertEqual(recovery_report_receipt('EX-r', evidence_ref='E', observed_at='T'), {
            'kind': RECOVERY_REPORT_RECEIPT, 'state': 'accepted', 'execution_id': 'EX-r', 'receiver': 'recovery_launcher',
            'observed_at': 'T', 'evidence_ref': 'E', 'scope': 'structured_recovery_report_not_research_integration'})

    def test_a_hold_a_pause_or_an_ended_instance_holds_the_outcome(self):
        from do_math.repair_execution import recovery_held
        state = {'lifecycle': {'state': 'active'}}
        self.assertFalse(recovery_held(False, state, {'status': 'ready'}))
        self.assertTrue(recovery_held(True, state, {'status': 'ready'}))
        self.assertTrue(recovery_held(False, state, {'status': 'ready', 'user_pause': {'id': 'P'}}))
        self.assertTrue(recovery_held(False, state, {'status': 'paused'}))
        self.assertTrue(recovery_held(False, state, {'status': 'closed'}))
        self.assertTrue(recovery_held(False, {'lifecycle': {'permanently_closed': True}}, {'status': 'ready'}))


class RecoveryAttemptTests(unittest.TestCase):
    """A released recovery execution is ended, its activity settled, and the attempt recorded on its diagnosis."""

    def setUp(self):
        from do_math import activities, execution_lifecycle
        self.runtime, self.record = installation_repair_state()
        at = '2026-09-22T00:30:00Z'
        activities.open_activity(self.runtime, activity_id='AY-recovery', activity_kind='recovery', owner_ref='operator',
                                 input_refs=[], opened_at=at)
        self.execution = execution_lifecycle.create_execution(execution_id='EX-repair', owner_activity_id='AY-recovery',
            actor_kind='ai', input_manifest={}, profile_ref={'id': 'EP-r', 'revision': 1, 'sha256': 'a' * 64}, created_at=at)
        self.execution['role'] = 'recovery'
        activities.assign_execution(self.runtime, 'AY-recovery', self.execution)
        for status in ('starting', 'running'):
            execution_lifecycle.transition_execution(self.execution, status, at=at)

    def record_attempt(self, outcome, diagnosis):
        from do_math.repair_execution import record_recovery_attempt
        record_recovery_attempt(self.runtime, self.execution, activity_id='AY-recovery', owner={'failure': 'F'},
                                outcome=outcome, diagnosis=diagnosis, execution_id='EX-repair', at='2026-09-22T01:00:00Z')

    def test_a_repaired_diagnosis_finishes_the_recovery_and_resumes_the_failed_request(self):
        self.execution['submission_receipt'] = repair_execution.recovery_report_receipt('EX-repair',
            evidence_ref='runtime/artifacts/BA-repair/report.json', observed_at='2026-09-22T01:00:00Z')
        self.record_attempt('repaired', self.record)
        self.assertEqual((self.execution['status'], self.execution['outcome'], self.execution['result_disposition']),
                         ('ended', 'output_accepted', {'recovery': 'repaired'}))
        self.assertEqual(self.runtime['activities']['AY-recovery']['status'], 'finished')
        self.assertEqual(self.record['status'], 'applied')
        self.assertEqual(self.record['result']['installation_repair']['repaired_by'], 'EX-repair')
        self.assertEqual([action['continuation_of'] for action in self.runtime['queue']], ['EX-failed'])

    def test_an_unrepaired_attempt_waits_and_marks_its_diagnosis(self):
        self.execution['submission_receipt'] = {'state': 'accepted'}
        self.record_attempt('recovery_failed', self.record)
        self.assertEqual((self.execution['outcome'], self.execution['result_disposition']),
                         ('output_accepted', {'recovery': 'recovery_failed'}))
        activity = self.runtime['activities']['AY-recovery']
        self.assertEqual((activity['status'], activity['waiting']['reason'], activity['waiting']['next_owner']),
                         ('waiting', 'recovery_failed', 'recovery'))
        self.assertEqual(activity['waiting']['condition'], {'kind': 'installation_repair_retry', 'failure': {'failure': 'F'}})
        self.assertEqual(self.record['status'], 'installation_repair_waiting')
        self.assertEqual({key: self.record['result']['installation_repair'][key] for key in ('status', 'attempted_by')},
                         {'status': 'recovery_failed', 'attempted_by': 'EX-repair'})

    def test_an_engine_failure_without_a_diagnosis_records_only_the_attempt(self):
        before = deepcopy(self.record)
        self.record_attempt('recovery_failed', None)
        self.assertEqual(self.execution['status'], 'ended')
        self.assertEqual(self.record, before)


class EngineStartTests(unittest.TestCase):
    def test_a_pending_installation_repair_holds_the_engine_start(self):
        status = {'status': 'ready', 'installation_repair': {'id': 'OD-pending'}}
        self.assertEqual(start_guard(status), {'outcome': 'installation_repair_waiting', 'before': status})


class RepairVerificationTests(unittest.TestCase):
    def test_report_without_real_regression_file_cannot_claim_repaired(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            for output, message in (
                    ({'repair_outcome': 'repaired', 'verification_evidence': []},
                     'diagnosed repair requires repaired outcome and regression evidence files'),
                    ({'repair_outcome': 'repaired', 'verification_evidence': ['missing.txt']},
                     'repair verification evidence must be a real file in its workspace'),
                    ({'repair_outcome': 'unresolved', 'verification_evidence': ['missing.txt']},
                     'diagnosed repair requires repaired outcome and regression evidence files')):
                with self.subTest(output=output), self.assertRaisesRegex(ValueError, message):
                    collect_repair_verification(output, workspace)
            (workspace / 'empty.txt').write_bytes(b'')
            with self.assertRaisesRegex(ValueError, 'repair verification evidence is empty'):
                collect_repair_verification({'repair_outcome': 'repaired', 'verification_evidence': ['empty.txt']}, workspace)
            (workspace / 'regression.txt').write_bytes(b'former input now accepted')
            rows = collect_repair_verification({'repair_outcome': 'repaired', 'verification_evidence': ['regression.txt']},
                                               workspace)
            self.assertEqual([(row['path'], row['bytes']) for row in rows], [('regression.txt', 25)])


class InitialRetryContinuationTests(unittest.TestCase):
    def test_clock_failure_keeps_a_remaining_wait_but_does_not_recreate_a_continued_one(self):
        """T3 about 3.5 s: real adopted initial state and diagnosis; only the clock fails around continuation."""
        from do_math.execution_lifecycle import transition_execution
        from support.scheduling_clock import with_clock
        from support.scheduling_initial import adopted_sim, initial_failure

        for after_removal in (False, True):
            with self.subTest(after_removal=after_removal):
                sim = adopted_sim()
                action, _ = initial_failure(sim)
                engine = sim.engine
                engine.route_failed_action(action, 'EX-bad', reason='Diagnose initial failure')
                diagnostic = engine.runtime['queue'].pop()
                reviewer = engine._register_execution(diagnostic,
                    {'id': 'EX-retry-diagnosis', 'role': 'maintenance', 'status': 'running'})
                self.assertIsNotNone(reviewer)
                engine.apply_initial_diagnosis(diagnostic, {'initial_submission_diagnosis': {
                    'decision': 'retry', 'guidance': 'Continue the unchanged initial obligation'}}, reviewer['id'])
                reviewer['submission_receipt'] = {'state': 'accepted', 'evidence_ref': 'synthetic:diagnosis'}
                transition_execution(reviewer, 'stopping', at=sim.clock.now())
                transition_execution(reviewer, 'ended', at=sim.clock.now(), outcome='output_accepted')
                engine._save()
                identifier = action['id']

                class FailingClock:
                    def __init__(self):
                        self.errors = []
                    def now(self):
                        removed = identifier not in engine.runtime['waiting_actions']
                        if not self.errors and removed == after_removal:
                            self.errors.append('clock unavailable during initial continuation')
                            raise OSError(self.errors[-1])
                        return sim.clock.now()
                    def __getattr__(self, name):
                        return getattr(sim.clock, name)

                clock = FailingClock()
                engine.ports = with_clock(sim, clock)
                engine.continue_initial_retries()
                self.assertEqual(clock.errors, ['clock unavailable during initial continuation'])
                if after_removal:
                    self.assertNotIn(identifier, engine.runtime['waiting_actions'])
                    retry, = engine.runtime['queue']
                    self.assertEqual((retry['id'], retry['continuation_of'], retry['diagnosis_attempt']),
                                     (identifier, 'EX-bad', 1))
                else:
                    wait = engine.runtime['waiting_actions'][identifier]
                    self.assertEqual((wait['diagnosis']['retry_error'], wait['reason'], wait['next_owner']),
                                     (clock.errors[0], clock.errors[0], 'maintenance'))
                    self.assertEqual(engine.runtime['queue'], [])
                self.assertEqual(engine.store.load(engine.head)[2], engine.runtime)
                before = deepcopy(engine.runtime)
                engine.continue_initial_retries()
                self.assertEqual(engine.runtime, before)


if __name__ == '__main__':
    unittest.main()
