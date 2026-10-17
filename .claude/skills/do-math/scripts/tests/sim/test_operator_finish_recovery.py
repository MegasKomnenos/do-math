"""Failure-only recovery with real store, capability, reservations and model collection."""
from copy import deepcopy
import json
import os
import sys
from pathlib import Path
import unittest

from do_math import formal, scheduled_operator as operator
from do_math import execution_lifecycle, execution_profiles, repair_execution
from do_math.canonical import canonical_json
from do_math.control_protocol import SUBMIT_INTENT
from do_math.file_io import os_lock
from do_math.git_store import GitStateStoreLockError
from do_math.model_runner import ModelRunner
from do_math.session_slots import SessionSlots
from support.operator_finish_observers import construction, outside_status
from support.engine_context import issue
from support.operator_finish_scene import Scene, diagnose
from support.provider_probes import ObservedCalls
from support.sim import warm_template
from support.storage_probes import Returns
from support.wait_reporting import assert_activity_wait_row

setUpModule = warm_template
FAILURE = {'kind': 'engine_unavailable', 'error': 'Synthetic launcher failure'}


class RecoveryTests(unittest.TestCase):
    def test_unreadable_installation_stops_recovery_before_any_model_call(self):
        """About 6.8 s: the real initialized recovery owner acquires and releases both publication locks."""
        scene = Scene()
        missing = scene.installation / 'missing'
        before = scene.load()
        with self.assertRaisesRegex(ValueError, '^cannot identify repair installation: '):
            scene.call(operator.recovery, failure=FAILURE, installation_root=missing)
        self.assertEqual(scene.load(), before)
        self.assertEqual(scene.cli.calls, [])
        self.assertEqual(scene.jobs.launched, [])
        # Failure also releases the maintenance lock, so a later owner can retry.
        with os_lock(scene.sim.engine.store.git_dir / 'do-math-installation-maintenance.lock', blocking=False):
            self.assertEqual(scene.load(), before)

    def test_recovery_publishes_under_locks_and_restarts_after_collection_and_unlock(self):
        direct = self.enterContext(ObservedCalls(run=ModelRunner.run, wake=operator.wake))
        scene = Scene()
        original = scene.load()[0]
        with scene.sim.engine.store.writer_lock():
            self.assertEqual(scene.call(operator.recovery, failure=FAILURE)['outcome'], 'engine_running')
        self.assertEqual(scene.cli.calls, [])
        self.assertEqual((direct.count('run'), direct.count('wake')), (0, 0))
        scene.answer()
        scene.cli.answer['next_step'] = None
        failed = scene.call(operator.recovery, failure=FAILURE)
        self.assertEqual(failed['outcome'], 'recovery_failed')
        prior = scene.load()[2]['executions'][failed['execution_id']]
        self.assertEqual(prior['status'], 'ended')
        self.assertEqual(prior['error'], "output/next_step: None is not of type 'string'")
        self.assertEqual((direct.count('run'), direct.count('wake')), (1, 0))
        failed_state = scene.load()
        waiting = deepcopy(failed_state[2]['activities'][prior['owner_activity_id']])
        self.assertEqual(waiting['waiting']['kind'], 'installation_repair_retry')
        self.assertEqual(waiting['waiting']['next_owner'], 'recovery')
        assert_activity_wait_row(self, scene.sim.engine.status(), waiting['id'], waiting)
        self.assertEqual(scene.call(operator.recovery, failure=FAILURE)['reason'],
                         'same failure and installation already attempted')
        self.assertEqual(scene.load(), failed_state)
        self.assertEqual(len(scene.cli.calls), 1)
        self.assertEqual((direct.count('run'), direct.count('wake')), (1, 0))
        # A real installation edition change permits a later attempt of the same failure.
        (scene.installation / 'SKILL.md').write_text('Second synthetic installation edition', encoding='utf-8')
        scene.answer()
        seen = []
        def during(call):
            _, _, runtime = scene.load()
            execution = next(e for e in runtime['executions'].values() if e.get('role') == 'recovery' and e['status'] == 'running')
            self.assertEqual(execution['status'], 'running')
            self.assertEqual(execution['capacity']['process']['pid'], scene.jobs.launched[-1].pid)
            activity = runtime['activities'][prior['owner_activity_id']]
            self.assertEqual(activity['status'], 'working')
            self.assertNotIn('waiting', activity)
            self.assertEqual(activity['assigned_execution_ids'], [prior['id'], execution['id']])
            self.assertIn('Do not change research records, goals, budgets, grants', call['prompt'])
            with self.assertRaisesRegex(GitStateStoreLockError, '^another local writer owns this instance lock$'), scene.sim.engine.store.writer_lock():
                self.fail('recovery did not exclude engine writer')
            seen.append(execution['id'])
        scene.cli.on_input = during
        def before_run(args):
            execution = scene.load()[2]['executions'][args['execution_id']]
            self.assertEqual(execution['status'], 'starting')
            return args
        def before_wake(args):
            with scene.sim.engine.store.writer_lock(), os_lock(
                    scene.sim.engine.store.git_dir / 'do-math-installation-maintenance.lock', blocking=False):
                executions = scene.load()[2]['executions'].values()
                self.assertTrue(all(e['status'] == 'ended' and
                    e['capacity']['local_termination'] == 'confirmed' for e in executions if e.get('role') == 'recovery'))
            self.assertTrue(all(job.closed and job.done for job in scene.jobs.launched))
            return args
        with ObservedCalls(wake=operator.wake, run=ModelRunner.run,
                           capture={'wake': before_wake, 'run': before_run}) as calls:
            result = scene.call(operator.recovery, failure={**FAILURE, 'observed_at': scene.ports.clock.now()})
        self.assertEqual(result['outcome'], 'repaired', result)
        self.assertEqual(len(seen), 1)
        self.assertEqual(calls.count('wake'), 1)
        self.assertEqual(calls.count('run'), 1)
        self.assertEqual((direct.count('run'), direct.count('wake')), (2, 1))
        new_head, state, runtime = scene.load()
        self.assertNotEqual(new_head, original)
        execution = runtime['executions'][result['execution_id']]
        self.assertEqual(execution['owner_activity_id'], prior['owner_activity_id'])
        activity = runtime['activities'][prior['owner_activity_id']]
        self.assertEqual(len(activity['assigned_execution_ids']), 2)
        self.assertEqual(activity['status'], 'finished')
        self.assertNotIn(activity['id'], scene.sim.engine.status()['waiting_activities'])
        self.assertEqual(runtime['executions'][prior['id']], prior)
        self.assertEqual((execution['role'], execution['status'], execution['outcome']),
                         ('recovery', 'ended', 'output_accepted'))
        self.assertEqual(execution['capacity']['reservation_ids'], [])
        self.assertEqual(execution['capacity']['local_termination'], 'confirmed')
        self.assertEqual(runtime['reservations'], {})
        self.assertEqual(execution['input_manifest']['repair_authority']['source'], 'adopted_operator_repair_scope')
        self.assertFalse((scene.workspace / 'session-slots').exists())
        self.assertTrue(any('execution_profiles/EP-' in name for name in scene.sim.engine.store.list_files('research/', new_head)))
        self.assertTrue(all(job.closed and job.done for job in scene.jobs.launched))
        with scene.sim.engine.store.writer_lock(), os_lock(
                scene.sim.engine.store.git_dir / 'do-math-installation-maintenance.lock', blocking=False):
            pass

    def test_diagnosed_repair_keeps_operational_wait_until_verified_then_resumes_once(self):
        """About 2.3 s, over the 2 s budget: one verified worker repair plus exact owner/store/report transitions."""
        scene = Scene()
        engine = scene.sim.engine
        at = scene.ports.clock.now()
        target = engine._register_execution({'id': 'AC-live-failure', 'role': 'maintenance'},
            {'id': 'EX-live-failure', 'role': 'maintenance', 'status': 'running'})
        source = 'runtime/artifacts/BA-live-failure/result.json'
        target.update(error='Installed receiver failed during the admitted call', result_ref=source)
        execution_lifecycle.transition_execution(target, 'stopping', at=at)
        execution_lifecycle.transition_execution(target, 'ended', at=at, outcome='execution_incomplete')
        engine._save({source: canonical_json({'error': target['error']})})
        review_action = {'id': 'AC-live-review', 'role': 'operational_review', 'target': target['id']}
        reviewer = engine._register_execution(review_action,
            {'id': 'EX-live-review', 'role': 'operational_review', 'status': 'running'})
        work = scene.workspace / 'live-review'
        work.mkdir()
        context = engine._context(review_action, work)
        issue(engine, reviewer, context, 'BA-live-review')
        disposition = {'kind': 'repair', 'basis_refs': [target['id']], 'next_owner': 'installation_recovery',
            'reason': 'Repair the independently diagnosed receiver',
            'repair_target': 'installation:scripts/do_math/engine.py', 'meaning_preserving': True,
            'verification': 'Run the receiver regression'}
        engine._apply_operational_disposition(review_action, disposition, reviewer['id'])
        record = next(row for row in engine.runtime['operational_dispositions'].values()
                      if row['execution_id'] == reviewer['id'])
        self.assertEqual(record['status'], 'repair_required')
        engine._save()
        before = scene.load()
        self.assertEqual(scene.call(operator.recovery)['reason'], 'no installation repair is pending')
        engine._run_pending_operational_repairs()
        self.assertEqual(scene.load(), before)
        self.assertEqual(scene.cli.calls, [])
        reviewer = engine.runtime['executions'][reviewer['id']]
        output_ref = 'runtime/artifacts/BA-live-review-output/output.json'
        execution_lifecycle.record_submission_intent(reviewer,
            {'candidate_id': 'CS-live-review', 'output_ref': output_ref, 'manifest': []},
            {'id': 'UC-live-review', 'kind': SUBMIT_INTENT, 'state': 'accepted',
             'execution_id': reviewer['id'], 'received_at': at})
        execution_lifecycle.transition_execution(reviewer, 'ended', at=at, outcome='output_accepted')
        engine._save({output_ref: canonical_json({'disposition': disposition})})
        # The accepted diagnosis lets the real settlement producer create this
        # kind; no activity wait or condition is injected by the test.
        target = engine.runtime['executions'][target['id']]
        engine._settle_activity(target['id'])
        aid = target['owner_activity_id']
        waiting = deepcopy(engine.runtime['activities'][aid])
        self.assertEqual(waiting['waiting']['kind'], 'operational_repair')
        self.assertEqual(waiting['waiting']['condition'], {'operational_disposition_ids': [record['id']]})
        engine._run_pending_operational_repairs()
        self.assertEqual(scene.load()[2]['operational_dispositions'][record['id']]['status'], 'installation_repair_pending')
        assert_activity_wait_row(self, engine.status(), aid, waiting)
        engine._settle_activity(reviewer['id'])
        engine._settle_activity(target['id'])
        engine._save()
        self.assertEqual(scene.load()[2]['activities'][aid], waiting)
        preserved = deepcopy(scene.load()[2]['executions'][target['id']])
        preserved.pop('pending_operational_disposition', None)
        others = deepcopy({key: value for key, value in scene.load()[2]['activities'].items() if key != aid})
        scene.answer(diagnosed=True)
        result = scene.call(operator.recovery)
        self.assertEqual(result['outcome'], 'repaired', result)
        after = scene.load()
        activity = after[2]['activities'][aid]
        self.assertEqual(activity['status'], 'ready')
        self.assertNotIn('waiting', activity)
        successor, = [row for row in after[2]['queue'] if row.get('continuation_of') == target['id']]
        self.assertEqual(successor['owner_activity_id'], aid)
        self.assertEqual(after[2]['executions'][target['id']], preserved)
        self.assertEqual({key: after[2]['activities'][key] for key in others}, others)
        self.assertNotIn(aid, engine.status()['waiting_activities'])
        self.assertEqual(scene.call(operator.recovery)['reason'], 'no installation repair is pending')
        self.assertEqual(scene.load(), after)
        self.assertEqual(len(scene.cli.calls), 1)

    def test_diagnosed_repair_restores_failed_request_and_preserves_regression_proof(self):
        direct = self.enterContext(ObservedCalls(run=ModelRunner.run, wake=operator.wake))
        scene = Scene()
        record = diagnose(scene)
        scene.answer(diagnosed=True)
        environment = dict(os.environ)
        with Returns(ModelRunner.run) as returned, ObservedCalls(gate=SessionSlots.provider_result_from_run, run=ModelRunner.run,
                           wake=operator.wake, job=formal._job_run) as calls:
            result = scene.call(operator.recovery)
        self.assertEqual(result['outcome'], 'repaired', result)
        _, _, runtime = scene.load()
        self.assertEqual(runtime['operational_dispositions'][record['id']]['status'], 'applied')
        successor = next(a for a in runtime['queue'] if a.get('continuation_of') == 'EX-failed')
        self.assertEqual(successor['repair_attempt'], 2)
        aid = runtime['executions']['EX-failed']['owner_activity_id']
        self.assertEqual(runtime['activities'][aid]['status'], 'ready')
        self.assertNotIn('waiting', runtime['activities'][aid])
        self.assertNotIn(aid, scene.sim.engine.status()['waiting_activities'])
        run = Path(result['run_directory'])
        self.assertTrue((run / 'regression-evidence.json').is_file())
        self.assertIn('actual rejected response', (run / 'workspace/input/failure-0.json').read_text())
        self.assertEqual(len(scene.commands), 1)
        self.assertEqual(calls.count('wake'), 1)
        self.assertEqual(calls.count('run'), 1)
        self.assertEqual((direct.count('run'), direct.count('wake')), (1, 1))
        runner = json.loads((run / 'runner-result.json').read_bytes())
        forwarded, = calls.captured('gate')
        self.assertEqual(forwarded['execution_id'], result['execution_id'])
        self.assertIs(forwarded['result'], returned.values[0])
        self.assertEqual(forwarded['result']['output'], runner['output'])
        self.assertEqual(forwarded['config'], scene.load()[1]['config'])
        self.assertEqual(runner['status'], 'completed')
        command = [sys.executable, str(scene.installation / 'scripts/probe_cli.py'), '--skill-only']
        job, = calls.captured('job')
        self.assertEqual(job['command'], command)
        self.assertEqual(job['cwd'], scene.sim.root)
        self.assertEqual(job['env'], environment)
        self.assertIs(job['jobs'], scene.ports.jobs)
        self.assertIs(job['clock'], scene.ports.clock)
        spawned, = scene.commands
        self.assertEqual(spawned['command'], command)
        self.assertEqual(spawned['cwd'], str(scene.sim.root))
        self.assertEqual(scene.jobs.launched[-1].env, environment)
        self.assertEqual(json.loads((run / 'verification.json').read_bytes()),
                         {'exit_code': 0, 'stdout': scene.stdout, 'stderr': scene.stderr})
        # Requires main's already-integrated spool/strict preservation change.
        self.assertEqual((job.get('evidence_dir'), job.get('decode_errors')), (run, 'strict'))

    def test_unresolved_diagnosis_does_not_restart_or_repeat(self):
        direct = self.enterContext(ObservedCalls(run=ModelRunner.run, wake=operator.wake))
        scene = Scene()
        record = diagnose(scene)
        scene.answer('unresolved', diagnosed=True)
        queue_before = deepcopy(scene.load()[2]['queue'])
        self.assertTrue(queue_before)
        result = scene.call(operator.recovery)
        self.assertEqual(result['outcome'], 'recovery_failed', result)
        _, _, runtime = scene.load()
        self.assertEqual(runtime['operational_dispositions'][record['id']]['status'], 'installation_repair_waiting')
        self.assertEqual(runtime['queue'], queue_before)
        self.assertEqual(scene.commands, [])
        self.assertEqual(scene.ports.scheduler.calls, [])
        self.assertEqual((direct.count('run'), direct.count('wake')), (1, 0))
        self.assertEqual(scene.call(operator.recovery), {'outcome': 'recovery_waiting',
            'reason': 'same failure and installation already attempted'})
        self.assertEqual(scene.load()[2]['queue'], queue_before)
        self.assertEqual(len(scene.cli.calls), 1)
        self.assertEqual((direct.count('run'), direct.count('wake')), (1, 0))

    def test_unsupported_capability_is_saved_before_reserving_or_calling(self):
        direct = self.enterContext(ObservedCalls(run=ModelRunner.run, wake=operator.wake))
        scene = Scene()
        scene.ports.host.identity['edition'] = 'unsupported-new-cli'
        scene.ports.host.capabilities['structured_output'] = False
        with ObservedCalls(run=ModelRunner.run, acquire=SessionSlots.acquire) as calls:
            result = scene.call(operator.recovery, failure=FAILURE)
        self.assertEqual((result['outcome'], result['reason']),
                         ('recovery_waiting', 'profile_capability_unavailable'))
        self.assertEqual(calls.count('run'), 0)
        self.assertEqual(calls.count('acquire'), 0)
        self.assertEqual((direct.count('run'), direct.count('wake')), (0, 0))
        _, state, runtime = scene.load()
        self.assertFalse(runtime['reservations'])
        evidence = next(e for e in state['capability_evidence'].values()
                        if e['identity'] == scene.ports.host.identity)
        self.assertEqual(evidence['capabilities']['structured_output']['status'], 'unsupported')

    def test_unknown_local_termination_holds_output_and_never_restarts(self):
        direct = self.enterContext(ObservedCalls(run=ModelRunner.run, wake=operator.wake))
        scene = Scene()
        scene.answer()
        def unknown(call):
            scene.jobs.empty[scene.jobs.launched[-1].name] = None
        scene.cli.on_input = unknown
        with Returns(ModelRunner.run) as returned, ObservedCalls(run=ModelRunner.run) as calls:
            result = scene.call(operator.recovery, failure=FAILURE)
        self.assertEqual(result['outcome'], 'recovery_termination_unknown', result)
        _, _, runtime = scene.load()
        execution = runtime['executions'][result['execution_id']]
        self.assertEqual(execution['status'], 'stopping')
        self.assertEqual(execution['capacity']['local_termination'], 'unknown')
        self.assertEqual(execution['error'],
            'Local Job termination is unconfirmed; capacity and output remain held for recovery.')
        self.assertEqual(execution['output'], scene.cli.answer)
        self.assertEqual(runtime['reservations'], {})
        args, = calls.captured('run')
        self.assertEqual(args['input_seal'], execution_profiles.prompt_seal(args['prompt']))
        self.assertEqual(args['input_seal'], execution['input_manifest']['prompt'])
        raw = args['prompt'].split(execution_profiles.boundary_prompt(args['profile']))[0]
        self.assertEqual(json.loads(raw.rsplit('\n', 1)[1])['installation'], str(scene.installation))
        self.assertEqual(Path(scene.commands[0]['command'][1]), scene.installation / 'scripts/probe_cli.py')
        self.assertEqual(scene.ports.scheduler.calls, [])
        self.assertEqual((direct.count('run'), direct.count('wake')), (1, 0))
        self.assertTrue(returned.values[0]['execution']['collect']['termination_barrier']['confirmed'])
        self.assertEqual(scene.call(operator.recovery, failure=FAILURE)['reason'],
                         'existing execution termination is unconfirmed')
        self.assertEqual(len(scene.cli.calls), 1)
        self.assertEqual((direct.count('run'), direct.count('wake')), (1, 0))

    def test_failed_structured_report_preserves_output_without_research_submission(self):
        direct = self.enterContext(ObservedCalls(run=ModelRunner.run, wake=operator.wake))
        scene = Scene()
        original_knowledge = deepcopy(scene.load()[1]['knowledge'])
        # Preserve every original report field; change only next_step to make
        # the real runner produce output_validation instead of a canned failure.
        original_output = scene.answer()
        output = {**deepcopy(original_output), 'next_step': None}
        self.assertEqual({key for key in output if output[key] != original_output[key]}, {'next_step'})
        scene.cli.answer = output
        def inspect(call):
            from do_math.provider_final import output_contract
            self.assertEqual(call['output_schema'], operator.OPERATOR_SCHEMA)
            self.assertEqual(call['schema'], output_contract('codex', operator.OPERATOR_SCHEMA))
            self.assertIn('Synthetic launcher failure', call['prompt'])
            self.assertFalse((Path(call['cwd']) / 'input/submission/context.json').exists())
        scene.cli.on_input = inspect
        with Returns(ModelRunner.run, snapshot=deepcopy) as reports:
            result = scene.call(operator.recovery, failure=FAILURE)
        report, = reports.snapshots
        self.assertEqual((report['status'], report['error_kind'], report['error']),
            ('failed', 'output_validation', "output/next_step: None is not of type 'string'"))
        self.assertEqual(report['output'], output)
        self.assertEqual(result['outcome'], 'recovery_failed', result)
        self.assertEqual(len(scene.cli.calls), 1)
        self.assertEqual((direct.count('run'), direct.count('wake')), (1, 0))
        _, state, runtime = scene.load()
        execution = runtime['executions'][result['execution_id']]
        self.assertEqual(execution['output'], output)
        self.assertEqual(execution['outcome'], 'execution_incomplete')
        self.assertEqual(execution['error'], "output/next_step: None is not of type 'string'")
        self.assertNotIn('submission_receipt', execution)
        self.assertEqual(runtime['activities'][execution['owner_activity_id']]['waiting']['reason'], 'recovery_failed')
        self.assertEqual(state['knowledge'], original_knowledge)

    def test_probe_routes_published_diagnosis_and_hold_blocks_recovery(self):
        direct = self.enterContext(ObservedCalls(run=ModelRunner.run, wake=operator.wake))
        scene = Scene()
        record = diagnose(scene)
        scene.answer('unresolved', diagnosed=True)
        before = scene.load()[0]
        with ObservedCalls(read=operator.read_status, guard=operator.start_guard) as wiring:
            guarded = scene.call(operator.engine_start_guard)
        self.assertEqual(guarded['outcome'], 'installation_repair_waiting')
        self.assertEqual(wiring.count('read'), 1)
        self.assertEqual(wiring.captured('guard')[0]['status'], guarded['before'])
        self.assertEqual(guarded['before']['installation_repair']['id'], record['id'])
        with ObservedCalls(recovery=operator.recovery) as calls:
            with Returns(operator.read_status, snapshot=deepcopy) as statuses, ObservedCalls(
                    load=operator.ResearchRepository.load, capture={'load': construction}) as loads:
                result = scene.call(operator.check, probe=True)
            status, = statuses.snapshots
            # status() also reloads: exclude only its exact current frame path,
            # separately from the Engine constructor's load.
            loaded, = [call for call in outside_status(loads, 'load') if not call['status_reload']]
            self.assertEqual(loads.count('load'), 3)
            self.assertEqual(sum(call['status_engine'] for call in loads.captured('load')), 1)
            self.assertEqual(sum(call['status_reload'] for call in loads.captured('load')), 1)
            self.assertEqual(loaded['arguments']['snapshot'], status['snapshot'])
            self.assertEqual(status['snapshot'], before)
            self.assertEqual(result['outcome'], 'installation_repair_pending')
            self.assertEqual(result['failure']['diagnosis_id'], record['id'])
            self.assertEqual(calls.count('recovery'), 0)
            self.assertEqual(scene.load()[0], before)
            self.assertEqual(scene.ports.scheduler.calls, [])
            self.assertEqual((direct.count('run'), direct.count('wake')), (0, 0))
            self.assertEqual(scene.call(operator.check)['outcome'], 'recovery_failed')
            self.assertEqual(calls.count('recovery'), 1)
            passed, = calls.captured('recovery')
            self.assertIsNone(passed['failure'])
            self.assertEqual((passed['repository'], passed['instance'], passed['workspace']), scene.args)
            operator.hold(scene.workspace, reason='user hold', clock=scene.ports.clock)
            self.assertEqual(scene.call(operator.check)['outcome'], 'held')
            self.assertEqual(calls.count('recovery'), 1)
            self.assertEqual((direct.count('run'), direct.count('wake')), (1, 0))

    def test_judged_repair_counts_once_even_if_hold_holds_failed_verification(self):
        direct = self.enterContext(ObservedCalls(run=ModelRunner.run, wake=operator.wake))
        scene = Scene()
        diagnose(scene)
        scene.answer(diagnosed=True)
        original = scene.cli.on_input
        def hold(call):
            original(call)
            operator.hold(scene.workspace, reason='user hold during the call', clock=scene.ports.clock)
        scene.cli.on_input = hold
        scene.exit_code = 1
        result = scene.call(operator.recovery)
        self.assertEqual(result['outcome'], 'recovery_held', scene.load()[2]['executions'][result['execution_id']])
        self.assertEqual(len(scene.commands), 1)
        self.assertEqual(scene.ports.scheduler.calls, [])
        self.assertEqual((direct.count('run'), direct.count('wake')), (1, 0))
        operator.release(scene.workspace, clock=scene.ports.clock)
        self.assertEqual(scene.call(operator.recovery), {'outcome': 'recovery_waiting',
            'reason': 'same failure and installation already attempted'})
        self.assertEqual(len(scene.cli.calls), 1)
        self.assertEqual((direct.count('run'), direct.count('wake')), (1, 0))

    def test_provider_limit_reaches_gate_unchanged_and_unjudged_repair_can_retry(self):
        direct = self.enterContext(ObservedCalls(run=ModelRunner.run, wake=operator.wake))
        scene = Scene()
        scene.claude()
        diagnose(scene)
        scene.answer('unresolved', diagnosed=True)
        scene.limited()
        with Returns(ModelRunner.run) as returned, ObservedCalls(gate=SessionSlots.provider_result_from_run) as calls:
            result = scene.call(operator.recovery)
        self.assertEqual(result['outcome'], 'recovery_provider_limited', scene.load()[2]['executions'][result['execution_id']])
        forwarded, = calls.captured('gate')
        self.assertIs(forwarded['result'], returned.values[0])
        self.assertEqual(forwarded['execution_id'], result['execution_id'])
        self.assertEqual(forwarded['config'], scene.load()[1]['config'])
        failure = returned.values[0]['failure']
        self.assertEqual((failure['kind'], failure['provider'], failure['retry_at']), ('provider_limit', 'claude', None))
        self.assertTrue(Path(failure['evidence_ref']).is_file())
        self.assertEqual(scene.commands, [])
        self.assertEqual(scene.ports.scheduler.calls, [])
        self.assertEqual((direct.count('run'), direct.count('wake')), (1, 0))
        before = scene.load()
        original = deepcopy(before[2]['executions'][result['execution_id']])
        aid = original['owner_activity_id']
        waiting = deepcopy(before[2]['activities'][aid])
        self.assertEqual(waiting['waiting']['kind'], 'installation_repair_retry')
        assert_activity_wait_row(self, scene.sim.engine.status(), aid, waiting)
        self.assertEqual(scene.call(operator.recovery)['reason'], 'provider_limit')
        self.assertEqual(scene.load(), before)
        self.assertEqual(len(scene.cli.calls), 1)
        self.assertEqual((direct.count('run'), direct.count('wake')), (1, 0))
        # Real admission requires the published provider gate to reopen; the old
        # slots double silently permitted an immediate retry.
        gate = scene.load()[2]['provider_waits']['PW-claude']
        scene.sim.advance(gate['retry_at'] - scene.ports.clock.wall().timestamp())
        next_attempt = scene.call(operator.recovery)
        self.assertEqual(len(scene.cli.calls), 2)
        self.assertEqual((direct.count('run'), direct.count('wake')), (2, 0))
        runtime = scene.load()[2]
        self.assertEqual(runtime['executions'][next_attempt['execution_id']]['owner_activity_id'], aid)
        self.assertEqual(runtime['activities'][aid]['assigned_execution_ids'], [original['id'], next_attempt['execution_id']])
        self.assertEqual(runtime['executions'][original['id']], original)

    def test_model_policy_pause_holds_future_calls_but_not_the_repair_attempt(self):
        direct = self.enterContext(ObservedCalls(run=ModelRunner.run, wake=operator.wake))
        scene = Scene()
        scene.claude()
        diagnose(scene)
        scene.answer('unresolved', diagnosed=True)
        scene.wrong_model()
        result = scene.call(operator.recovery)
        self.assertEqual(result['outcome'], 'recovery_held', scene.load()[2]['executions'][result['execution_id']])
        _, _, runtime = scene.load()
        self.assertEqual(runtime['status'], 'paused')
        self.assertEqual(runtime['model_policy_violation'], {'execution_id': result['execution_id'],
            'assigned_model': 'claude-opus-5', 'reported_models': ['other-model']})
        self.assertEqual(scene.commands, [])
        self.assertEqual(scene.ports.scheduler.calls, [])
        self.assertEqual((direct.count('run'), direct.count('wake')), (1, 0))
        self.assertEqual(scene.call(operator.recovery)['outcome'], 'held')
        guarded = scene.call(operator.engine_start_guard)
        self.assertEqual(guarded['outcome'], 'model_policy_waiting')
        self.assertEqual(guarded['before']['model_policy_violation'], runtime['model_policy_violation'])
        self.assertEqual(len(scene.cli.calls), 1)
        self.assertEqual((direct.count('run'), direct.count('wake')), (1, 0))
        scene.sim.restart()
        scene.sim._apply('resume', text='User permits the next model call')
        scene.call(operator.recovery)
        self.assertEqual(len(scene.cli.calls), 2)
        self.assertEqual((direct.count('run'), direct.count('wake')), (2, 0))

    def test_hold_before_report_does_not_use_up_the_repair(self):
        direct = self.enterContext(ObservedCalls(run=ModelRunner.run, wake=operator.wake))
        scene = Scene()
        diagnose(scene)
        scene.answer('unresolved', diagnosed=True)
        scene.cli.timeout = True
        scene.jobs.polls = 6
        original = scene.cli.on_input
        def hold(call):
            original(call)
            operator.hold(scene.workspace, reason='user hold during the call', clock=scene.ports.clock)
        scene.cli.on_input = hold
        with Returns(ModelRunner.run) as stopped:
            result = scene.call(operator.recovery)
        self.assertEqual(stopped.values[0]['status'], 'stopped')
        self.assertEqual(result['outcome'], 'recovery_held', scene.load()[2]['executions'][result['execution_id']])
        self.assertEqual(scene.commands, [])
        self.assertEqual(scene.ports.scheduler.calls, [])
        self.assertEqual((direct.count('run'), direct.count('wake')), (1, 0))
        operator.release(scene.workspace, clock=scene.ports.clock)
        scene.cli.on_input = original
        scene.call(operator.recovery)
        self.assertEqual(len(scene.cli.calls), 2)
        self.assertEqual((direct.count('run'), direct.count('wake')), (2, 0))
