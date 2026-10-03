"""정상 저장 상태와 실제 공개 CLI에서 운영자 경계의 결과·무호출을 확인한다."""
from contextlib import chdir, redirect_stdout
from copy import deepcopy
from dataclasses import replace
import io
import json
from pathlib import Path
import unittest

from do_math import scheduled_operator as operator
from support.operator_finish_ports import UnreadableOnce
from support.operator_finish_scene import Scene
from support.provider_probes import ObservedCalls
from support.sim import warm_template

setUpModule = warm_template


class SupervisionContractTests(unittest.TestCase):
    def test_public_status_preserves_published_repair_owner_and_evidence(self):
        from do_math import cli
        from support.operator_finish_scene import diagnose
        scene = Scene()
        diagnosis = diagnose(scene)
        before = scene.load()
        output = io.StringIO()
        with redirect_stdout(output), chdir(scene.sim.root):
            code = cli.main(['status', '--json', '--repository', str(scene.args[0]), '--instance', scene.args[1]],
                ports=scene.ports, environment=scene.sim.environment,
                host_id=scene.sim.host_id, codex_home=scene.sim.codex_home)
        self.assertEqual(code, 0, output.getvalue())
        status = json.loads(output.getvalue())['result']
        self.assertEqual(status['snapshot'], before[0])
        self.assertEqual(status['installation_repair'], before[2]['operational_dispositions'][diagnosis['id']])
        self.assertEqual(status['installation_repair']['status'], 'installation_repair_pending')
        self.assertEqual(status['operating_summary']['primary_blocker']['next_owner'], 'installation_recovery')
        human = io.StringIO()
        with redirect_stdout(human), chdir(scene.sim.root):
            human_code = cli.main(['status', '--repository', str(scene.args[0]), '--instance', scene.args[1]],
                ports=scene.ports, environment=scene.sim.environment,
                host_id=scene.sim.host_id, codex_home=scene.sim.codex_home)
        self.assertEqual(human_code, 0)
        self.assertIn('blocking: installation_repair next=installation_recovery', human.getvalue())
        self.assertIn('snapshot: ' + before[0], human.getvalue())
        self.assertEqual(scene.load(), before)
        self.assertEqual(scene.jobs.launched, [])
        self.assertEqual(scene.ports.scheduler.calls, [])

    def test_scheduled_engine_rereads_pause_after_a_startable_probe(self):
        scene = Scene()
        probe = scene.call(operator.check, probe=True)
        self.assertEqual(probe['engine_start']['outcome'], 'startable')
        scene.sim._apply('pause', text='예약 후 실제 기동 전 사용자 정지')
        before = scene.load()
        with ObservedCalls(read=operator.read_status) as calls:
            result = scene.call(operator.run_engine)
        self.assertEqual(calls.count('read'), 1)
        self.assertEqual(result['outcome'], 'paused')
        self.assertEqual(result['before']['snapshot'], before[0])
        self.assertEqual(result['before']['status'], 'paused')
        self.assertNotEqual(result['before']['snapshot'], probe['status']['snapshot'])
        self.assertEqual(scene.load(), before)
        self.assertEqual(scene.jobs.launched, [])
        self.assertEqual(scene.ports.scheduler.calls, [])

    def test_scheduled_engine_rereads_accepted_diagnosis_after_a_startable_probe(self):
        from support.operator_finish_scene import diagnose
        scene = Scene()
        probe = scene.call(operator.check, probe=True)
        self.assertEqual(probe['engine_start']['outcome'], 'startable')
        diagnosis = diagnose(scene)
        before = scene.load()
        result = scene.call(operator.run_engine)
        self.assertEqual(result['outcome'], 'installation_repair_waiting')
        self.assertEqual(result['before']['installation_repair']['id'], diagnosis['id'])
        self.assertEqual(result['before']['snapshot'], before[0])
        self.assertEqual(scene.load(), before)
        self.assertEqual(scene.jobs.launched, [])
        self.assertEqual(scene.ports.scheduler.calls, [])

    def test_workspace_is_loaded_from_real_repository(self):
        scene = Scene()
        head = scene.load()[0]
        actual = operator.resolve_workspace(scene.args[0], scene.args[1], ports=scene.ports)
        self.assertEqual(actual, scene.workspace.resolve())
        self.assertEqual(scene.load()[0], head)
        self.assertEqual(scene.jobs.launched, [])
        self.assertEqual(scene.ports.scheduler.calls, [])

    def test_empty_workspace_is_rejected_after_real_storage_validation(self):
        scene = Scene()
        head, state, runtime = scene.load()
        invalid = deepcopy(state)
        invalid['workspace'] = ''
        self.assertEqual({key for key in state if state[key] != invalid[key]}, {'workspace'})
        saved = scene.sim.engine.store.save_with_state(head, invalid, runtime)[0]
        with self.assertRaisesRegex(ValueError, '^instance does not have a workspace$'):
            operator.resolve_workspace(scene.args[0], scene.args[1], ports=scene.ports)
        self.assertEqual(scene.load()[0], saved)
        self.assertEqual(scene.load()[1]['workspace'], '')
        self.assertEqual(scene.jobs.launched, [])

    def test_start_guard_load_failure_is_preserved_without_child_or_scheduler(self):
        scene = Scene()
        original = scene.load()[0]
        scene.ports = replace(scene.ports, git_backend=UnreadableOnce(scene.ports.git_backend.objects))
        result = scene.call(operator.run_engine)
        self.assertEqual(result, {'outcome': 'engine_failed', 'kind': 'engine_unavailable',
                                 'error_type': 'SyntaxError', 'error': 'engine broken'})
        self.assertEqual(json.loads((scene.workspace / 'operator/latest-engine.json').read_bytes()), result)
        self.assertEqual(scene.load()[0], original)
        self.assertEqual(scene.commands, [])
        self.assertEqual(scene.cli.calls, [])
        self.assertEqual(scene.ports.scheduler.calls, [])

    def test_paused_check_does_not_read_preserved_failure_or_recover(self):
        scene = Scene()
        scene.sim._apply('pause', text='사용자 일시 정지')
        operator._json(scene.workspace / 'operator/latest-engine.json', {'outcome': 'engine_failed', 'error': 'old failure'})
        before = scene.load()[0]
        with ObservedCalls(load=operator._load_json, recovery=operator.recovery) as calls:
            result = scene.call(operator.check)
        self.assertEqual(result['outcome'], 'paused')
        self.assertEqual(result['status']['status'], 'paused')
        self.assertEqual((calls.count('load'), calls.count('recovery')), (0, 0))
        self.assertEqual(scene.load()[0], before)
        self.assertEqual(scene.ports.scheduler.calls, [])

    def test_cli_dispatches_all_three_actions_with_explicit_ports_and_preserves_hold(self):
        scene = Scene()
        held = operator.hold(scene.workspace, reason='CLI 경계 확인', clock=scene.ports.clock)
        before = scene.load()[0]
        for action in ('check', 'wake', 'run-engine'):
            output = io.StringIO()
            with self.subTest(action=action), redirect_stdout(output), chdir(scene.sim.root):
                code = operator.main([action, '--repository', str(scene.args[0]), '--instance', scene.args[1],
                    '--workspace', str(scene.workspace), '--probe'], ports=scene.ports,
                    environment=scene.sim.environment, host_id=scene.sim.host_id, codex_home=scene.sim.codex_home,
                    installation_root=scene.installation)
            self.assertEqual((code, json.loads(output.getvalue())), (0, {'outcome': 'held'}))
        self.assertEqual(operator._load_json(scene.workspace / 'operator/HOLD.json'), held)
        self.assertEqual(scene.load()[0], before)
        self.assertEqual(scene.commands, [])
        self.assertEqual(scene.cli.calls, [])
        self.assertEqual(scene.ports.scheduler.calls, [])

    def test_cli_probe_emits_exact_real_status_and_does_not_start_jobs(self):
        scene = Scene()
        status = operator.read_status(*scene.args[:2], ports=scene.ports,
            environment=scene.sim.environment, host_id=scene.sim.host_id, codex_home=scene.sim.codex_home)
        output = io.StringIO()
        with redirect_stdout(output), chdir(scene.sim.root):
            code = operator.main(['check', '--repository', str(scene.args[0]), '--instance', scene.args[1],
                '--workspace', str(scene.workspace), '--probe'], ports=scene.ports,
                environment=scene.sim.environment, host_id=scene.sim.host_id, codex_home=scene.sim.codex_home,
                installation_root=scene.installation)
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(output.getvalue()), {'outcome': 'observed', 'status': status, 'model_called': False,
            'engine_start': {'outcome': 'startable', 'before': status}})
        self.assertEqual(scene.commands, [])
        self.assertEqual(scene.cli.calls, [])
        self.assertEqual(scene.ports.scheduler.calls, [])
