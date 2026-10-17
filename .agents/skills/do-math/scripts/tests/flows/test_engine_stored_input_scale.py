"""10-A의 실제 저장·재적재·읽기 경로. 100×10 전체와 현재 프로필37을 보존한다.

1000 실행 수명과 저장 계약 검증이 필요하므로 flows에 둔다. 모델 반복 실행은
대상이 아니며 종료 기록은 정상 도메인 생산자로 만든다.
"""
from copy import deepcopy
import json
import hashlib
from pathlib import Path
import tempfile
import unittest

from do_math import contracts, input_tool, submission
from do_math.canonical import canonical_json, exact_content_hash
from do_math.configuration import DEFAULT_CONFIG
from do_math.context_store import prepare_role_input, verify_manifest_artifacts
from support.engine_size_cases import assert_input_budget, stored_scale_sim, TASK_COUNT, HISTORY_PER_TASK, PROFILE_COUNT
from support.role_input_requirements import assert_judgment_inputs
from support.engine_tool_output import invoke_tool
from support.engine_cli_journey import Journey
from support.trust_inputs import trust_fixture
from support.sim import Sim, warm_template

setUpModule = warm_template


class StoredInputScaleTests(unittest.TestCase):
    def test_56230_file_toolchain_manifest_registers_by_reference_without_state_amplification(self):
        from do_math import trust_inventory
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            sim = Sim(root / 'sim')
            seed = trust_fixture(root / 'seed', [str(sim.trust_lean)])
            original = trust_inventory.read_record(seed['toolchain_record']['path'])
            # 파일 관찰 결과가 입력인 정상 baseline 생산자. 실제56230파일 설치/검증 주장이 아니다.
            paths = [f'toolchain/lib/lean/Scale/{number:05d}.olean' for number in range(56230)]
            fingerprints = {name: [8192, '1000000000', '1000000000'] for name in paths}
            contents = {name: hashlib.sha256(name.encode()).hexdigest() for name in paths}
            baseline = trust_inventory.new_baseline(
                {'files': fingerprints, 'sha256': exact_content_hash(fingerprints)},
                {'files': contents, 'sha256': exact_content_hash(contents)},
                original['baselines'][0]['validation'], clock=sim.clock)
            record = trust_inventory.new_record(original['identity'], baseline)
            record_path = root / (record['id'] + '.json')
            trust_inventory.write_record(record_path, record)
            self.assertEqual(trust_inventory.read_record(record_path), record)
            self.assertEqual(len(record['baselines'][0]['content']['files']), 56230)
            request = trust_inventory.registration_request(record, record_path, trust_inventory.binding(record))
            journey = Journey(sim, root)
            path, _ = journey.document('trust', request)
            result = journey.call('trust', '--file', path)
            self.assertEqual(result['effect'], 'applied')
            before = deepcopy(journey.state())
            replay = journey.call('trust', '--file', path)
            self.assertEqual(replay['request_id'], result['request_id'])
            self.assertEqual(journey.state(), before)
            snapshot, instance, runtime = before
            self.assertEqual(len(instance['trust_environments']), 1)
            environment = next(iter(instance['trust_environments'].values()))
            self.assertEqual(environment['toolchain_record'], request['toolchain_record'])
            self.assertEqual(runtime['trust_bindings'][environment['id']], request['binding'])
            self.assertEqual(environment['status'], 'registered')
            raw = record_path.read_bytes()
            logical = canonical_json({'instance': instance, 'runtime': runtime})
            # B-04의 예시1.2배: 외부 원천 한 벌 + instance/runtime 논리 레코드 전건.
            self.assertLessEqual(len(raw) + len(logical), len(raw) * 6 // 5)
            self.assertNotIn(paths[-1].encode(), logical)
            transition, _ = journey.document('transition', {'operation': 'transition', 'env_id': environment['id']})
            self.assertEqual(journey.call('trust', '--file', transition)['effect'], 'applied')
            self.assertEqual([r['status'] for r in journey.state()[2]['trust_transitions'].values()], ['checking'])
            # 현재 파일 지문 대조/활성화는 다른 관문이며 합성 관찰값으로 성공을 주장하지 않는다.

    def test_large_manifest_is_preserved_once_and_public_tool_exports_exact_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            # 조사 B-04의 대형 불변 원천: 작은 corpus seed와 별도의 약5MB manifest.
            manifest = {'entries': [{'id': f'entry-{number:03d}',
                'text': f'원천 {number}: ' + 'x' * 8192} for number in range(603)]}
            raw = canonical_json(manifest)
            self.assertGreater(len(raw), 4_900_000)
            path = base / 'manifest.json'
            path.write_bytes(raw)
            sim = Sim(base / 'sim', sources=[path])
            sim.restart()
            store = sim.engine.store
            self.assertEqual(len(sim.instance['sources']), 1)
            source = sim.instance['sources'][0]
            self.assertEqual((source['bytes'], source['sha256']), (len(raw), hashlib.sha256(raw).hexdigest()))
            self.assertEqual(store.read(source['path']), raw)
            paths = store.list_files('research/') + store.list_files('runtime/')
            material = store.read_many(paths)
            # 원천 한 벌 + 메타데이터만. 현재 결과로 상수를 맞추지 않고 복제 한 벌도 탐지한다.
            self.assertEqual(sum(value == raw for value in material.values()), 1)
            metadata = {key: value for key, value in material.items() if key != source['path']}
            self.assertLess(sum(map(len, metadata.values())), len(raw))
            root = base / 'reader'
            action = {'id': 'AC-manifest', 'role': 'maintenance'}
            context = sim.engine._context(action, root)
            profile = sim.instance['execution_profiles'][sim.instance['role_profile_refs']['maintenance'][0]['id']]
            packed = prepare_role_input(context, instance=sim.instance, runtime=sim.runtime,
                role='maintenance', profile=profile, snapshot=sim.engine.head, workspace=root,
                activity_id=action['id'], artifact_prefix='runtime/artifacts/BA-manifest', clock=sim.clock)
            self.assertEqual(profile['input']['max_input_bytes'], DEFAULT_CONFIG['max_input_bytes'])
            assert_input_budget(self, packed, 'maintenance', profile)
            assert_judgment_inputs(self, 'maintenance', packed, root, producer_context=context)
            verify_manifest_artifacts(packed['manifest'], packed['artifacts'].__getitem__)
            submission.install_tools(root, packed['validation_context'], contracts.schema_for('maintenance'), None, clock=sim.clock)
            code, output = invoke_tool(input_tool.read_main, root,
                ['--path', source['path'], '--output', 'read/manifest.json'], ports=sim.ports, environment=sim.environment)
            result = json.loads(output)
            self.assertEqual((code, result['status']), (0, 'ok'), result)
            self.assertEqual((root / 'read/manifest.json').read_bytes(), raw)
            self.assertEqual(result['records'][0]['sha256'], source['sha256'])
            self.assertLessEqual(len(output), 4096)

    def test_all_tasks_histories_profiles_survive_storage_packaging_and_public_reads(self):
        sim = stored_scale_sim()
        head, instance, runtime = sim.engine.store.load()
        self.assertEqual(len(runtime['tasks']), TASK_COUNT)
        self.assertEqual([len(t['results']) for t in runtime['tasks'].values()], [HISTORY_PER_TASK] * TASK_COUNT)
        current = {ref['id'] for refs in instance['role_profile_refs'].values() for ref in refs}
        self.assertEqual(len(current), PROFILE_COUNT)
        store = sim.engine.store
        paths = store.list_files('research/', head) + store.list_files('runtime/', head)
        documents = store.read_many(paths, head)
        # Real task/execution/profile producers and registered metadata share the family codec.
        # Charge every serialized file, including both manifests and referenced payloads.
        logical = canonical_json({'instance': instance, 'runtime': runtime})
        self.assertLessEqual(sum(map(len, documents.values())), 2 * len(logical) + 1024 * len(paths))
        for role in ('research_preparation', 'research_plan'):
            with self.subTest(role=role), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                action = {'id': 'AC-size-' + role, 'role': role}
                # 실제 context 생산자가 저장 상태를 읽어 역할별 입력을 조립한다.
                context = sim.engine._context(action, root)
                profile = instance['execution_profiles'][instance['role_profile_refs'][role][0]['id']]
                packaged = prepare_role_input(context, instance=instance, runtime=runtime,
                    role=role, profile=profile, snapshot=head, workspace=root, activity_id=action['id'],
                    artifact_prefix='runtime/artifacts/BA-size-' + role, clock=sim.clock)
                self.assertEqual(profile['input']['max_input_bytes'], DEFAULT_CONFIG['max_input_bytes'])
                assert_input_budget(self, packaged, role, profile)
                assert_judgment_inputs(self, role, packaged, root, producer_context=context)
                verify_manifest_artifacts(packaged['manifest'], packaged['artifacts'].__getitem__)
                fixed = {**deepcopy(packaged['validation_context']), 'record_store': {
                    'repository': str(sim.repository), 'instance_id': sim.instance_id}}
                submission.install_tools(root, fixed, contracts.schema_for(role), None, clock=sim.clock)
                identifiers = [*runtime['tasks'], *sorted(current)]
                arguments = [part for identifier in identifiers for part in ('--id', identifier)]
                code, raw = invoke_tool(input_tool.read_main, root, arguments,
                                       ports=sim.ports, environment=sim.environment)
                answer = json.loads(raw)
                self.assertEqual((code, answer['status'], answer['snapshot']), (0, 'ok', head))
                originals = [*runtime['tasks'].values(), *[instance['execution_profiles'][key] for key in sorted(current)]]
                self.assertEqual([r['record'] for r in answer['records']], originals)
                # 출력 크기는 요청한 정상 레코드 전체와 각 행의 메타데이터 한 벌로 제한한다.
                source_bytes = sum(len(canonical_json(row)) for row in originals)
                self.assertLessEqual(len(raw), 2 * source_bytes + 1024 * len(identifiers))
                rows = [json.loads(line) for line in (root / 'checks/reads.jsonl').read_bytes().splitlines()]
                self.assertEqual([r['request'] for r in rows], identifiers)
                self.assertEqual([r['status'] for r in rows], ['ok'] * len(identifiers))
