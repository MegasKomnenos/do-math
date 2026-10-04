"""운영자 복구의 실제 저장·잠금·러너 경로. 복구 왕복 비용은 미측정이므로 흐름 층에서 확인한다."""
from copy import deepcopy
from dataclasses import replace
import json
from pathlib import Path
import unittest

from do_math import scheduled_operator as operator
from do_math.file_io import os_lock
from do_math.model_runner import ModelRunner
from do_math.windows_job import WindowsJobUnsupportedError
from support.operator_finish_ports import Scheduler
from support.operator_finish_scene import Scene, diagnose
from support.provider_probes import ObservedCalls
from support.sim import warm_template
from support.storage_probes import Returns
from support.role_input_requirements import assert_recovery_judgment_input

setUpModule = warm_template
FAILURE = {'kind': 'engine_unavailable', 'error': 'operator 계약 시험의 기동 실패'}


class RecoveryContractTests(unittest.TestCase):
    def test_live_execution_blocks_repair_before_capacity_or_model_creation(self):
        scene = Scene()
        engine = scene.sim.engine
        execution = engine._register_execution({'id': 'AC-live', 'role': 'maintenance'},
            {'id': 'EX-live', 'role': 'maintenance', 'status': 'running'})
        engine._save()
        before = scene.load()
        self.assertEqual(before[2]['executions'][execution['id']]['status'], 'running')
        result = scene.call(operator.recovery, failure=FAILURE)
        self.assertEqual(result, {'outcome': 'recovery_waiting',
            'reason': 'existing execution termination is unconfirmed', 'execution_id': execution['id']})
        self.assertEqual(scene.load(), before)
        self.assertEqual(scene.jobs.launched, [])
        self.assertEqual(scene.ports.scheduler.calls, [])
        with scene.sim.engine.store.writer_lock():
            self.assertEqual(scene.load()[0], before[0])

    def test_failed_verification_preserves_diagnosis_and_blocks_restart_and_repeat(self):
        scene = Scene()
        diagnosis = diagnose(scene)
        scene.answer(diagnosed=True)
        scene.exit_code, scene.stdout, scene.stderr = 9, '구조 검사 실패', '보존할 검증 진단'
        before = scene.load()
        result = scene.call(operator.recovery)
        self.assertEqual(result['outcome'], 'recovery_verification_failed')
        runtime = scene.load()[2]
        execution = runtime['executions'][result['execution_id']]
        self.assertEqual((execution['status'], execution['capacity']['local_termination']), ('ended', 'confirmed'))
        self.assertEqual(execution['capacity']['reservation_ids'], [])
        self.assertEqual(runtime['reservations'], before[2]['reservations'])
        self.assertEqual(runtime['queue'], before[2]['queue'])
        self.assertEqual(runtime['operational_dispositions'][diagnosis['id']]['status'], 'installation_repair_waiting')
        self.assertEqual(json.loads((Path(result['run_directory']) / 'verification.json').read_bytes()),
            {'exit_code': 9, 'stdout': scene.stdout, 'stderr': scene.stderr})
        self.assertEqual(scene.ports.scheduler.calls, [])
        self.assertEqual(len(scene.commands), 1)
        self.assertTrue(all(job.done and job.closed for job in scene.jobs.launched))
        repair_input = assert_recovery_judgment_input(self, scene, execution, source_snapshot=before[0])
        self.assertTrue(repair_input['failure_inputs'])
        saved = scene.load()
        self.assertEqual(scene.call(operator.recovery), {'outcome': 'recovery_waiting',
            'reason': 'same failure and installation already attempted'})
        self.assertEqual(scene.load(), saved)
        self.assertEqual(len(scene.cli.calls), 1)

    def test_missing_regression_file_rejects_repair_without_verification_or_restart(self):
        scene = Scene()
        diagnosis = diagnose(scene)
        scene.answer(diagnosed=True)
        scene.cli.answer['verification_evidence'] = ['missing-regression.txt']
        before = scene.load()
        result = scene.call(operator.recovery)
        self.assertEqual(result['outcome'], 'recovery_failed')
        runtime = scene.load()[2]
        execution = runtime['executions'][result['execution_id']]
        self.assertEqual(execution['error']['type'], 'ValueError')
        self.assertEqual(execution['error']['message'], 'repair verification evidence must be a real file in its workspace')
        self.assertEqual(execution['output'], scene.cli.answer)
        self.assertEqual((execution['status'], execution['capacity']['local_termination']), ('ended', 'confirmed'))
        self.assertEqual(runtime['queue'], before[2]['queue'])
        self.assertEqual(runtime['reservations'], before[2]['reservations'])
        self.assertEqual(runtime['operational_dispositions'][diagnosis['id']]['status'], 'installation_repair_waiting')
        self.assertEqual(scene.commands, [])
        self.assertEqual(scene.ports.scheduler.calls, [])
        self.assertTrue(all(job.done and job.closed for job in scene.jobs.launched))

    def test_distinct_preserved_failure_permits_one_attempt_in_same_installation(self):
        scene = Scene()
        scene.answer()
        scene.cli.answer['next_step'] = 7
        first = scene.call(operator.recovery, failure=FAILURE)
        self.assertEqual(first['outcome'], 'recovery_failed')
        same = scene.call(operator.recovery, failure={**FAILURE, 'observed_at': scene.ports.clock.now()})
        self.assertEqual(same, {'outcome': 'recovery_waiting', 'reason': 'same failure and installation already attempted'})
        second = scene.call(operator.recovery, failure={**FAILURE, 'error': '별도의 보존된 기동 실패'})
        self.assertEqual(second['outcome'], 'recovery_failed')
        runtime = scene.load()[2]
        old, new = (runtime['executions'][row['execution_id']] for row in (first, second))
        self.assertNotEqual(old['owner_activity_id'], new['owner_activity_id'])
        old_identity, new_identity = (row['input_manifest']['repair_identity'] for row in (old, new))
        self.assertEqual(old_identity['installation_sha256'], new_identity['installation_sha256'])
        self.assertNotEqual(old_identity['failure_sha256'], new_identity['failure_sha256'])
        self.assertEqual(len(scene.cli.calls), 2)
        self.assertEqual(scene.commands, [])
        self.assertEqual(scene.ports.scheduler.calls, [])
        self.assertEqual(runtime['reservations'], {})

    def test_absent_failure_and_diagnosis_wait_without_publication(self):
        scene = Scene()
        before = scene.load()
        self.assertEqual(scene.call(operator.recovery), {'outcome': 'recovery_waiting',
            'reason': 'no installation repair is pending'})
        self.assertEqual(scene.load(), before)
        self.assertEqual(scene.jobs.launched, [])
        self.assertEqual(scene.ports.scheduler.calls, [])

    def test_maintenance_lock_prevents_execution_and_releases_writer(self):
        scene = Scene()
        before = scene.load()
        with os_lock(scene.sim.engine.store.git_dir / 'do-math-installation-maintenance.lock', blocking=False):
            result = scene.call(operator.recovery, failure=FAILURE)
        self.assertEqual(result, {'outcome': 'recovery_waiting', 'reason': 'installation maintenance is already active'})
        self.assertEqual(scene.load(), before)
        self.assertEqual(scene.jobs.launched, [])
        self.assertEqual(scene.ports.scheduler.calls, [])
        with scene.sim.engine.store.writer_lock():
            self.assertEqual(scene.load()[0], before[0])

    def test_oversized_prompt_waits_before_reserving_or_starting_model(self):
        scene = Scene()
        scene.sim._apply('configure', config={'max_input_bytes': 1})
        before = scene.load()
        with ObservedCalls(run=ModelRunner.run) as calls:
            result = scene.call(operator.recovery, failure=FAILURE)
        self.assertEqual((result['outcome'], result['reason']), ('recovery_waiting', 'input_overflow'))
        self.assertGreater(result['prompt']['bytes'], 1)
        self.assertEqual(len(result['prompt']['sha256']), 64)
        self.assertEqual(calls.count('run'), 0)
        self.assertEqual(scene.load()[2]['executions'], before[2]['executions'])
        self.assertEqual(scene.load()[2]['activities'], before[2]['activities'])
        self.assertEqual(scene.load()[2]['reservations'], before[2]['reservations'])
        self.assertEqual(scene.jobs.launched, [])
        self.assertEqual(scene.ports.scheduler.calls, [])

    def test_unsupported_job_records_runner_capability_evidence_without_model_or_restart(self):
        scene = Scene()
        scene.jobs.refuse = WindowsJobUnsupportedError('operator atomic Job unavailable')
        before = scene.load()
        with Returns(ModelRunner.run, snapshot=deepcopy) as returned:
            result = scene.call(operator.recovery, failure=FAILURE)
        runner, = returned.snapshots
        self.assertEqual(result['outcome'], 'recovery_failed')
        evidence = runner['capability_evidence']
        _, state, runtime = scene.load()
        self.assertEqual(state['capability_evidence'][evidence['id']], evidence)
        self.assertEqual(evidence['capabilities']['atomic_local_job']['status'], 'unsupported')
        self.assertEqual(evidence['capabilities']['atomic_local_job']['execution_id'], result['execution_id'])
        self.assertEqual(runtime['executions'][result['execution_id']]['status'], 'ended')
        self.assertEqual(runtime['reservations'], before[2]['reservations'])
        self.assertEqual(scene.jobs.launched, [])
        self.assertEqual(scene.cli.calls, [])
        self.assertEqual(scene.ports.scheduler.calls, [])

    def test_ready_recovery_activity_is_reused_after_unjudged_provider_limit(self):
        scene = Scene()
        scene.claude()
        scene.answer()
        scene.limited()
        first = scene.call(operator.recovery, failure=FAILURE)
        self.assertEqual(first['outcome'], 'recovery_provider_limited')
        head, state, runtime = scene.load()
        execution = runtime['executions'][first['execution_id']]
        aid = execution['owner_activity_id']
        from do_math import activities
        activity = runtime['activities'][aid]
        activities.resume_activity(runtime, aid, condition=activity['waiting']['condition'], at=scene.ports.clock.now())
        scene.sim.engine.store.save_with_state(head, state, runtime)
        self.assertEqual(scene.load()[2]['activities'][aid]['status'], 'ready')
        gate = runtime['provider_waits']['PW-claude']
        scene.sim.advance(gate['retry_at'] - scene.ports.clock.wall().timestamp())
        second = scene.call(operator.recovery, failure=FAILURE)
        self.assertEqual(second['outcome'], 'recovery_provider_limited')
        after = scene.load()[2]
        self.assertEqual(after['executions'][second['execution_id']]['owner_activity_id'], aid)
        self.assertEqual(after['activities'][aid]['assigned_execution_ids'], [first['execution_id'], second['execution_id']])
        self.assertEqual(len(scene.cli.calls), 2)
        self.assertEqual(scene.ports.scheduler.calls, [])

    def test_child_diagnosis_scheduler_failure_preserves_successful_engine_evidence(self):
        scene = Scene()
        scheduler = Scheduler(error=OSError('operator scheduler unavailable'))
        scheduler.tasks = scene.ports.scheduler.tasks
        scene.ports = replace(scene.ports, scheduler=scheduler)
        scene.on_command = lambda command: diagnose(scene)
        result = scene.call(operator.run_engine)
        self.assertEqual(result['outcome'], 'completed')
        self.assertEqual(result['exit_code'], 0)
        self.assertEqual(result['supervisor_request'], {'status': 'failed', 'error': 'operator scheduler unavailable',
            'next_owner': 'scheduled_operator', 'fallback': 'periodic supervision'})
        self.assertEqual([action for action, _ in scheduler.calls], ['start-operator'])
        self.assertEqual(json.loads((Path(result['run_directory']) / 'result.json').read_bytes()), result)
        self.assertEqual(operator._load_json(scene.workspace / 'operator/latest-engine.json'), result)
        self.assertEqual(len(scene.commands), 1)
        self.assertEqual(scene.cli.calls, [])

    def test_diagnosis_probe_preserves_full_produced_failure_and_head(self):
        from do_math.repair_execution import installation_failure
        scene = Scene()
        record = diagnose(scene)
        before = scene.load()
        failure = installation_failure(before[2], record)
        result = scene.call(operator.check, probe=True)
        self.assertEqual(result, {'outcome': 'installation_repair_pending', 'model_called': False, 'failure': failure})
        self.assertEqual(scene.load(), before)
        self.assertEqual(scene.jobs.launched, [])
        self.assertEqual(scene.ports.scheduler.calls, [])

    def test_preserved_engine_failure_enters_recovery_before_engine_request(self):
        scene = Scene()
        scene.answer()
        normal = deepcopy(scene.cli.answer)
        scene.cli.answer['next_step'] = 7
        self.assertEqual({key for key in normal if normal[key] != scene.cli.answer[key]}, {'next_step'})
        operator._json(scene.workspace / 'operator/latest-engine.json', {
            'outcome': 'engine_failed', 'error': FAILURE['error']})
        before = scene.load()
        with ObservedCalls(recovery=operator.recovery) as calls:
            result = scene.call(operator.check)
        self.assertEqual(result['outcome'], 'recovery_failed')
        self.assertEqual(calls.count('recovery'), 1)
        execution = scene.load()[2]['executions'][result['execution_id']]
        repair_input = assert_recovery_judgment_input(self, scene, execution, source_snapshot=before[0])
        self.assertEqual(repair_input['failure_inputs'], [])
        self.assertEqual(execution['error'], "output/next_step: 7 is not of type 'string'")
        self.assertEqual(execution['output'], scene.cli.answer)
        self.assertEqual(execution['status'], 'ended')
        self.assertEqual(scene.ports.scheduler.calls, [])

    def test_waiting_guard_keeps_reconciled_wake_without_requesting_engine(self):
        scene = Scene()
        scene.sim.engine._idle_wait_status()
        scene.sim.engine._save()
        result = scene.call(operator.check)
        self.assertEqual(result['outcome'], 'not_started')
        self.assertEqual(result['provider_wake'], {'status': 'not_needed'})
        self.assertFalse(result['model_called'])
        self.assertEqual(scene.ports.scheduler.calls, [])
        self.assertEqual(scene.jobs.launched, [])
