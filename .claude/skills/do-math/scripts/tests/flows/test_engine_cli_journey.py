"""13-A 공개 초기화·활성화 여정과 지식 기록 유무에 따른 최초 배정.

init부터 실제 CLI로 이어 가며 각 명령의 응답을 다음 입력에 쓴다.
실측 약6초. 공개 제어·조회 전건을 잇는 시나리오라 flows에 둔다.
"""
from datetime import timedelta
from contextlib import redirect_stdout
import hashlib
from io import StringIO
import json
from pathlib import Path
import tempfile
import unittest

import setup_lean
from do_math.contracts import ROLES
from do_math.trust_inventory import validation_program
from support.engine_cli_journey import JOURNEY_STEPS, Journey, CliSim
from support.model import rebound
from support.sim import Sim
from support.state_builders import charter_record


class CliJourneyTests(unittest.TestCase):
    def test_public_preparation_chains_snapshot_config_hash_grants_and_profile(self):
        self.assertEqual(self.preparation(), 'research_preparation')

    def test_existing_unverified_knowledge_selects_plan_at_the_activation_stop(self):
        self.assertEqual(self.preparation(with_knowledge=True), 'research_plan')

    def preparation(self, *, with_knowledge=False):
        original = 'n+0=n을 증명한다.\r\n제약: 외부 공개 금지. e\N{COMBINING ACUTE ACCENT}; \N{KELVIN SIGN}\n'
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            sim = CliSim(root / 'sim', goal='n+0=n을 증명한다.', original=original)
            intent_inputs = []
            def observe_intent(output, context):
                intent_inputs.append(context)
                if len(intent_inputs) > 10:
                    raise AssertionError('초기 해석/검사가 10회의 대역 응답 상한을 초과함')
            sim.model.on('intent_interpretation').reply(rebound(observe_intent))
            journey = Journey(sim, root)
            journey.steps.append('create')
            status = journey.call('status', '--json', step='status')
            self.assertEqual(status['operating_summary']['lifecycle'], 'initializing')
            snapshot, files = journey.files('research/')
            _, runtime_files = journey.files('runtime/')
            self.assertEqual(len({row['path'] for row in files}), len(files))
            self.assertEqual(len({row['path'] for row in runtime_files}), len(runtime_files))
            lifecycle_path = next(row['path'] for row in files if '/lifecycle/' in row['path'])
            read = journey.call('read', '--snapshot', snapshot, '--path', lifecycle_path, step='read_original')
            self.assertEqual(read['sha256'], hashlib.sha256(read['text'].encode('utf-8')).hexdigest())
            _, instance, runtime = journey.state()
            self.assertEqual(instance['lifecycle']['immutable_input'],
                {'text': original, 'sha256': hashlib.sha256(original.encode('utf-8')).hexdigest(),
                 'bytes': len(original.encode('utf-8'))})
            settings, _ = journey.document('관찰값', {'tool_review_window_seconds': 60,
                                                     'self_check_response_window_seconds': 5})
            configured = journey.call('configure', '--origin', 'operator', '--config-file', settings, step='configure')
            self.assertEqual(configured['effect'], 'applied')
            _, instance, runtime = journey.state()
            configured_source = json.loads((Path(instance['workspace']) / 'control' / sim.instance_id /
                                            (configured['request_id'] + '.json')).read_bytes())
            self.assertEqual(configured_source['origin'], 'operator')
            self.assertEqual(runtime['processed_controls'].count(configured['request_id']), 1)
            self.assertEqual(instance['config']['tool_review_window_seconds'], 60)
            governance, governance_raw = journey.decision('헌장', {'kind': 'initialization',
                'operation': 'governance', 'records': [charter_record(original)]}, step='governance')
            _, instance, runtime = journey.state()
            source = instance['governance_sources'][governance['request_id']]
            self.assertEqual((source['origin'], source['text']), ('user', governance_raw))
            self.assertEqual((source['sha256'], source['bytes']),
                             (hashlib.sha256(governance_raw.encode('utf-8')).hexdigest(), len(governance_raw.encode('utf-8'))))
            expiry = (sim.clock.wall() + timedelta(days=1)).isoformat()
            grant_ids, grant_decisions = [], []
            for label, roles in [('initial', ['intent_interpretation', 'maintenance']),
                                 ('research', [*ROLES, 'formal_check'])]:
                grant_id = 'GR-journey-' + label
                decision_id = 'DC-journey-' + label
                receipt, grant_raw = journey.decision(label, {'kind': 'grant', 'decision_id': decision_id, 'grant': {'id': grant_id, 'kind': 'local',
                    'roles': roles, 'task_ids': [], 'reuse': 'reusable', 'expires_at': expiry}}, step=label + '_grant')
                grant_ids.append(grant_id)
                grant_decisions.append(decision_id)
                _, granted, grant_runtime = journey.state()
                approval = granted['governance_sources'][receipt['request_id']]
                self.assertEqual((approval['origin'], approval['text'], approval['sha256'], approval['bytes']),
                    ('user', grant_raw, hashlib.sha256(grant_raw.encode('utf-8')).hexdigest(), len(grant_raw.encode('utf-8'))))
                self.assertEqual(granted['grants'][grant_id]['source_ref'], receipt['request_id'])
                self.assertEqual(grant_runtime['executions'], {})
            grants = journey.call('query', '--kind', 'grant', '--limit', '1000', step='grant_query')
            # kind 조회는 가족 또는 kind 일치다. grant 결정 기록도 전체 결과에 포함된다.
            self.assertEqual(sorted(row['record']['id'] for row in grants['items']),
                             sorted(grant_ids + grant_decisions))
            config_hash = journey.call('status', '--json')['config_sha256']
            journey.decision('능력관측', {'kind': 'initialization', 'operation': 'probe', 'config_sha256': config_hash}, step='probe')
            capabilities = journey.call('query', '--kind', 'capability_evidence', '--limit', '1000', step='capability_query')
            _, instance, _ = journey.state()
            current = {ref['id'] for refs in instance['role_profile_refs'].values() for ref in refs
                       if instance['execution_profiles'][ref['id']]['actor_kind'] == 'ai'}
            self.assertEqual(sorted(row['record']['execution_profile_ref']['id'] for row in capabilities['items']), sorted(current))
            journey.decision('채택', {'kind': 'initialization', 'operation': 'adopt', 'config_sha256': config_hash,
                'adopt_current_governance': True, 'conversation_loss_policy': 'continue_authorized',
                'external_policy': 'disabled', 'adopt_default_review_policy': True,
                'initial_grant_ids': [grant_ids[0]], 'research_grant_ids': [grant_ids[1]]}, step='adopt')
            selected = journey.call('select-profile', '--role', 'intent_interpretation', step='select')
            self.assertEqual(selected['selection']['tier'], 'high')
            self.assertEqual(selected['profile']['id'], selected['selection']['profile_ref']['id'])
            self.assertEqual((journey.state()[2]['executions'], sim.model.calls), ({}, []))
            # 설치 파일만 외부 Lean 대역으로 만들고 기록·해시·trust 요청은 공개 도구가 생산한다.
            executable = sim.trust_lean
            executable.parent.mkdir(parents=True)
            executable.write_bytes(b'engine journey external Lean double')
            prelude = executable.parents[1] / 'lib' / 'lean' / 'Init' / 'Prelude.olean'
            prelude.parent.mkdir(parents=True)
            prelude.write_bytes(b'engine journey synthetic prelude')
            representative, _ = validation_program({'project': None})
            sim.lean.inputs[representative.encode('utf-8')] = {}
            command_file, _ = journey.document('Lean명령', {'lean_command': [str(executable)]})
            trust_file = root / '공개신뢰요청.json'
            output = StringIO()
            with redirect_stdout(output):
                setup_lean.main(['--verify-only', '--command-file', str(command_file),
                    '--records-dir', str(root / 'records'), '--evidence-dir', str(root / 'evidence'),
                    '--trust-file', str(trust_file)], ports=sim.ports, environment=sim.environment)
            prepared = json.loads(output.getvalue())
            self.assertEqual(prepared['status'], 'recorded')
            self.assertEqual(len(sim.lean.checks), 1)
            journey.steps.append('prepare_trust')
            registration = journey.call('trust', '--file', trust_file, step='register_trust')
            self.assertEqual(registration['effect'], 'applied')
            environments = journey.call('query', '--kind', 'trust-environment', '--limit', '1000')
            self.assertEqual(len(environments['items']), 1)
            environment_id = environments['items'][0]['record']['id']
            transition, _ = journey.document('신뢰전환', {'operation': 'transition', 'env_id': environment_id})
            self.assertEqual(journey.call('trust', '--file', transition, step='transition')['effect'], 'applied')
            if with_knowledge:
                # 이 조건부 시작 입력의 K 생산·저장은 정상 도메인 생산자다.
                # CLI 수입 절차 인증과 구별하고, 최초 배정의 공개 run 경계만 검사한다.
                from do_math import knowledge_io
                from support.knowledge_builders import knowledge_candidate
                sim.restart()
                sim.engine.instance, sim.engine.runtime, kid = knowledge_io.import_candidate(
                    sim.instance, sim.runtime, knowledge_candidate(), source_ref='engine:조건부 지식 입력',
                    actor_ref='engine:규모 시험', clock=sim.clock)
                sim.engine._save()
                knowledge = journey.call('query', '--kind', 'knowledge', '--limit', '1000')
                self.assertEqual([row['record']['id'] for row in knowledge['items']], [kid])
            result = journey.call('run', '--until-active', step='activate')
            _, instance, runtime = journey.state()
            self.assertEqual(result['operating_summary']['lifecycle'], 'active')
            self.assertEqual(instance['lifecycle']['state'], 'active')
            first = [row for row in runtime['queue'] if row['role'] in {'research_plan', 'research_preparation'}]
            self.assertEqual([row['role'] for row in first], ['research_plan' if with_knowledge else 'research_preparation'])
            research = [row for row in runtime['executions'].values()
                        if row['role'] in set(ROLES) - {'intent_interpretation', 'maintenance'}]
            self.assertEqual(research, [])
            self.assertEqual([row for row in sim.model.calls
                              if row['role'] in set(ROLES) - {'intent_interpretation', 'maintenance'}], [])
            interpreted = [ctx for ctx in intent_inputs if ctx['action'].get('stage') != 'check']
            self.assertEqual(len(interpreted), 1)
            self.assertEqual(interpreted[0]['user_request']['text'], original)
            self.assertEqual(instance['lifecycle']['immutable_input']['text'], original)
            # 실제 활성화 뒤 반환 경계: 두 번째 호출은 상한 없는 공개 명령 하나다.
            execution_ids = list(runtime['executions'])
            call_count = len(sim.model.calls)
            sim.advance(2)
            self.assertEqual(journey.call('run', '--until-active')['operating_summary']['lifecycle'], 'active')
            self.assertEqual(list(journey.state()[2]['executions']), execution_ids)
            self.assertEqual(len(sim.model.calls), call_count)
            expected_steps = [row[0] for row in JOURNEY_STEPS if row[-1] == 'implemented'
                              and row[0] not in {'pause', 'resume', 'close'}]
            self.assertEqual(journey.steps, expected_steps)
            return first[0]['role']

    def test_pause_resume_close_use_prior_receipts_and_do_not_reopen_closed_research(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            sim = Sim(root / 'sim')
            journey = Journey(sim, root)
            first = journey.call('pause', '--reason', '사용자 중지', step='pause')
            sim.advance(3)
            replay = journey.call('pause', '--reason', '사용자 중지')
            self.assertEqual((replay['request_id'], replay['snapshot'], replay['effect']),
                             (first['request_id'], first['snapshot'], 'applied'))
            self.assertEqual(journey.call('resume', '--reason', '사용자 재개', step='resume')['effect'], 'applied')
            self.assertEqual(journey.call('close', '--reason', '사용자 종결', step='close')['effect'], 'applied')
            before = journey.state()
            rejected = journey.call('resume', '--reason', '종결 후 요청')
            self.assertEqual((rejected['effect'], rejected['reason']),
                             ('rejected', 'closed/completed instance cannot apply lifecycle controls'))
            _, instance, runtime = journey.state()
            self.assertEqual((instance['lifecycle']['permanently_closed'], runtime['status']), (True, 'closed'))
            self.assertEqual((runtime['queue'], runtime['executions']), (before[2]['queue'], before[2]['executions']))
            self.assertEqual(sim.model.calls, [])
            self.assertEqual(journey.steps, [row[0] for row in JOURNEY_STEPS if row[0] in {'pause', 'resume', 'close'}])


class CliSnapshotAndControlTests(unittest.TestCase):
    """Public inputs and snapshot outputs; all owner/storage work uses the real implementation."""

    def setUp(self):
        self.root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.sim = CliSim(self.root / 'sim', goal='Preserve source bytes',
                          original='Preserve source bytes.\r\nDo not run research.')
        self.journey = Journey(self.sim, self.root)

    def invoke(self, command, *arguments):
        from do_math import cli
        output = StringIO()
        with redirect_stdout(output):
            code = cli.main([command, '--repository', str(self.sim.repository),
                             '--instance', self.sim.instance_id, *map(str, arguments)],
                            ports=self.sim.ports, environment=self.sim.environment,
                            host_id=self.sim.host_id, codex_home=self.sim.codex_home)
        return code, output.getvalue()

    def test_source_read_output_and_export_preserve_the_published_snapshot(self):
        raw = b'\xff\x00source\r\n'
        source = self.root / 'source.bin'
        source.write_bytes(raw)
        _, previous, _ = self.journey.state()
        before_ids = {row['id'] for row in previous['sources']}
        receipt = self.journey.call('source', '--file', source)
        self.assertEqual(receipt['effect'], 'applied')
        head, instance, runtime = self.journey.state()
        record, = [row for row in instance['sources'] if row['id'] not in before_ids]
        history, = [row for row in runtime['history'] if row.get('request', {}).get('id') == receipt['request_id']]
        self.assertEqual(history['source_id'], record['id'])
        self.assertEqual(record['name'], source.name)
        self.assertEqual(record['sha256'], hashlib.sha256(raw).hexdigest())
        self.assertEqual(record['bytes'], len(raw))
        output = self.root / 'download' / 'source.bin'
        downloaded = self.journey.call('read', '--path', record['path'], '--snapshot', head, '--output', output)
        self.assertEqual(output.read_bytes(), raw)
        self.assertEqual((downloaded['snapshot'], downloaded['size'], downloaded['sha256']),
                         (head, len(raw), hashlib.sha256(raw).hexdigest()))
        self.assertEqual(downloaded['provenance'], {'snapshot': head, 'path': record['path'],
            'sha256': hashlib.sha256(raw).hexdigest(), 'range': {'start': 0, 'end': len(raw), 'total': len(raw)}})
        import base64
        encoded = self.journey.call('read', '--path', record['path'], '--snapshot', head)
        self.assertEqual(encoded, {key: value for key, value in downloaded.items() if key != 'output'} |
                         {'base64': base64.b64encode(raw).decode('ascii')})
        self.assertEqual(base64.b64decode(encoded['base64']), raw)
        # Each exported file is checked against the same pinned Repository snapshot.
        for all_files in (False, True):
            with self.subTest(all_files=all_files):
                destination = self.root / ('all' if all_files else 'research')
                flags = ('--all',) if all_files else ()
                exported = self.journey.call('export', '--destination', destination, '--snapshot', head, *flags)
                prefixes = ('research/', 'runtime/') if all_files else ('research/',)
                expected = sorted({path for prefix in prefixes
                                   for path in self.sim.engine.store.list_files(prefix, head)})
                self.assertTrue(expected)
                self.assertEqual(exported, {'snapshot': head, 'files': expected})
                actual = sorted(path.relative_to(destination).as_posix()
                                for path in destination.rglob('*') if path.is_file())
                self.assertEqual(actual, expected)
                for path in expected:
                    self.assertEqual((destination / path).read_bytes(), self.sim.engine.store.read(path, head))
        self.assertEqual(self.journey.state(), (head, instance, runtime))
        self.assertEqual(self.sim.model.calls, [])

    def test_timeline_and_scoped_check_report_the_same_snapshot_without_execution(self):
        head, instance, runtime = self.journey.state()
        self.assertEqual(runtime['executions'], {})
        report = self.journey.call('timeline', '--snapshot', head, '--timezone', 'UTC')
        self.assertEqual((report['snapshot'], report['timezone'], report['rows'], report['counts_by_unit']),
                         (head, 'UTC', [], {}))
        code, csv = self.invoke('timeline', '--snapshot', head, '--timezone', 'UTC', '--format', 'csv')
        self.assertEqual(code, 0)
        self.assertEqual(csv, 'unit,id,snapshot\r\n\n')
        checked = self.journey.call('check', '--snapshot', head, '--kinds', 'record_storage')
        self.assertEqual(checked['snapshot'], head)
        self.assertEqual((checked['exit_code'], checked['passed']), (0, True))
        self.assertEqual(checked['inspection']['status'], 'healthy')
        self.assertEqual(self.journey.state(), (head, instance, runtime))
        self.assertEqual(self.sim.model.calls, [])

    def test_select_profile_rejects_unknown_role_and_task_without_state_change(self):
        before = self.journey.state()
        role = next(iter(before[1]['role_profile_refs']))
        for arguments, message in (
            (('--role', 'outside-role'), 'unknown execution role'),
            (('--role', role, '--task', 'TA-absent'), 'unknown task'),
        ):
            with self.subTest(arguments=arguments):
                code, output = self.invoke('select-profile', *arguments)
                self.assertEqual(code, 2)
                error = json.loads(output)['error']
                self.assertEqual(error, {'kind': 'input_error', 'message': message,
                                         'next_owner': 'user', 'retryable': False})
                self.assertEqual(self.journey.state(), before)
        self.assertEqual(self.sim.model.calls, [])

    def test_quiesce_and_release_use_the_public_receipt_as_fence_identity(self):
        before = self.journey.state()
        held = self.journey.call('quiesce', '--reason', 'Inspect without dispatch')
        self.assertEqual(held['effect'], 'applied')
        runtime = self.journey.state()[2]
        self.assertEqual(runtime['maintenance_fence']['request_id'], held['request_id'])
        self.assertEqual(runtime['maintenance_fence']['state'], 'quiescent')
        released = self.journey.call('release-quiesce', '--fence', held['request_id'])
        self.assertEqual(released['effect'], 'applied')
        runtime = self.journey.state()[2]
        self.assertNotIn('maintenance_fence', runtime)
        self.assertEqual(runtime['executions'], before[2]['executions'])
        self.assertEqual(self.sim.model.calls, [])

    def test_configure_replay_does_not_repeat_scheduler_effects(self):
        configuration, _ = self.journey.document('schedule', {'operator_interval_seconds': 8100})
        first = self.journey.call('configure', '--config-file', configuration, '--request-id', 'schedule-once')
        self.assertEqual(first['effect'], 'applied')
        before = self.journey.state()
        calls = list(self.sim.ports.scheduler.calls)
        self.assertTrue(calls)
        replay = self.journey.call('configure', '--config-file', configuration, '--request-id', 'schedule-once')
        self.assertEqual((replay['request_id'], replay['snapshot'], replay['effect']),
                         (first['request_id'], first['snapshot'], 'applied'))
        self.assertEqual(replay['operator_schedule'], {'status': 'not_reapplied',
            'reason': 'original control receipt replayed; explicit operator install or uninstall reconciles current configuration'})
        self.assertEqual(self.sim.ports.scheduler.calls, calls)
        self.assertEqual(self.journey.state(), before)

    def test_request_queues_the_requested_role_without_running_it(self):
        receipt = self.journey.call('request', '--role', 'maintenance', '--reason', 'Inspect local evidence')
        self.assertEqual(receipt['effect'], 'applied')
        _, _, runtime = self.journey.state()
        queued, = [row for row in runtime['queue'] if row.get('requested_by') == receipt['request_id']]
        self.assertEqual((queued['role'], queued['reason']), ('maintenance', 'Inspect local evidence'))
        self.assertEqual(self.sim.model.calls, [])
        self.assertEqual(runtime['executions'], {})

    def test_invalid_reassessment_document_is_rejected_before_admission(self):
        path, _ = self.journey.document('reassessment', {})
        before = self.journey.state()
        code, output = self.invoke('request', '--assessment-reassessment-file', path)
        self.assertEqual(code, 2)
        self.assertEqual(json.loads(output)['error'], {
            'kind': 'input_error',
            'message': 'assessment reassessment requires the exact assessment hash and defect evidence',
            'next_owner': 'user', 'retryable': False})
        self.assertEqual(self.journey.state(), before)
        self.assertEqual(self.sim.model.calls, [])


class CliInitializationSourceTests(unittest.TestCase):
    def test_init_sources_and_effort_are_preserved_and_missing_source_has_no_instance(self):
        from do_math import cli
        from do_math.repository import ResearchRepository
        from support.entry import entry
        root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        values = entry()
        config = root / 'config.json'
        config.write_text(json.dumps({'operator_enabled': False, 'scholarly_enabled': False}), encoding='utf-8')
        source = root / 'notes.txt'
        raw = 'Exact source \u03bb\r\n'.encode('utf-8')
        source.write_bytes(raw)
        for present in (False, True):
            with self.subTest(present=present):
                repository = root / ('valid-repo' if present else 'invalid-repo')
                workspace = root / ('valid-work' if present else 'invalid-work')
                supplied = source if present else root / 'missing.txt'
                output = StringIO()
                with redirect_stdout(output):
                    code = cli.main(['init', '--create-repository', '--repository', str(repository),
                        '--workspace', str(workspace), '--goal', 'Read the source', '--effort', 'high',
                        '--config-file', str(config), '--source', str(supplied)],
                        ports=values.ports, environment=values.environment,
                        host_id=values.host_id, codex_home=values.codex_home)
                envelope = json.loads(output.getvalue())
                if not present:
                    self.assertEqual(code, 2)
                    self.assertEqual(envelope['error']['message'], '--source is not a file: ' + str(supplied))
                    self.assertFalse(workspace.exists())
                else:
                    self.assertEqual(code, 0)
                    result = envelope['result']
                    store = ResearchRepository(repository, result['instance_id'],
                                               backend=values.ports.git_backend, clock=values.ports.clock)
                    head, instance, runtime = store.load()
                    record, = instance['sources']
                    self.assertEqual(head, result['snapshot'])
                    self.assertEqual(instance['config']['effort'], 'high')
                    self.assertEqual((record['name'], record['sha256'], record['bytes']),
                                     (source.name, hashlib.sha256(raw).hexdigest(), len(raw)))
                    self.assertEqual(store.read(record['path'], head), raw)
                    self.assertEqual(runtime['executions'], {})
