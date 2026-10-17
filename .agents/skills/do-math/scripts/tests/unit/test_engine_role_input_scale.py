"""10-A 기본 입력 상한: 역할 전건×대표 상태, 37개 프로필과 100×10 과제 이력.

실측6.375초: 25상태의 실제 문서·스키마 포장이 필요하다. 단위 예산 초과에도 모집단은
줄이지 않는다. 큰 Lean·manifest·전 저장 가족은 별도 축이며 이 시험의 성적에 합치지 않는다.
"""
import json
from pathlib import Path
import tempfile
import unittest

from do_math import contracts
from do_math.canonical import same_json_value
from do_math.configuration import DEFAULT_CONFIG
from do_math.context_store import input_class, input_scope, prepare_role_input, read_source, verify_manifest_artifacts
from support.engine_size_cases import (HISTORY_PER_TASK, PROFILE_COUNT, TASK_COUNT,
    assert_input_budget, role_cases, scale_context, scale_state)
from support.entry import entry


class RoleInputScaleTests(unittest.TestCase):
    def test_every_role_state_keeps_required_input_within_the_default_byte_budget(self):
        values = entry()
        instance, runtime = scale_state()
        self.assertEqual(len(instance['execution_profiles']), PROFILE_COUNT)
        self.assertEqual(len(runtime['tasks']), TASK_COUNT)
        self.assertEqual([len(task['results']) for task in runtime['tasks'].values()], [HISTORY_PER_TASK] * TASK_COUNT)
        for role, index, action in role_cases():
            with self.subTest(role=role, state=index), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                profile = next(p for p in instance['execution_profiles'].values() if p['role'] == role)
                limit = DEFAULT_CONFIG['max_input_bytes']
                self.assertEqual(profile['input']['max_input_bytes'], limit)
                context = scale_context(instance, runtime, action)
                result = prepare_role_input(context, instance=instance,
                    runtime=runtime, role=role, profile=profile, snapshot='a' * 40, workspace=root,
                    activity_id='AC-size', artifact_prefix='runtime/artifacts/BA-size', clock=values.ports.clock)
                assert_input_budget(self, result, role, profile)
                verify_manifest_artifacts(result['manifest'], result['artifacts'].__getitem__)
                scope = input_scope(action, runtime)
                for key, expected in context.items():
                    if input_class(scope, key) == 'blocked':
                        self.assertNotIn(key, result['context'])
                        self.assertNotIn(key, result['validation_context'])
                        self.assertNotIn(key, {row['key'] for row in result['manifest']['catalog']})
                        continue
                    if key == 'tasks' and role in ('research_plan', 'research_preparation'):
                        continue  # Complete originals are checked through their task sources below.
                    if key == 'ready_task_ids' and role == 'research_plan':
                        self.assertEqual(sorted(result['context'][key]), sorted(expected))
                        self.assertEqual(result['context'][key], result['manifest']['candidate_order']['ids'])
                        self.assertEqual(result['validation_context'][key], result['context'][key])
                        continue
                    actual = result['context'][key]
                    if isinstance(actual, dict) and set(actual) == {'source_ref', 'total'}:
                        ref = actual['source_ref']
                        source = read_source(root, ref, limit=max(1, ref['bytes']))
                        self.assertEqual((source['status'], source['truncated']), ('ok', False))
                        actual = json.loads(source['bytes'])
                    self.assertTrue(same_json_value(actual, expected), key)
                    self.assertTrue(same_json_value(result['validation_context'][key], expected), key)
                if role in ('research_plan', 'research_preparation'):
                    compared = result['context']['tasks']
                    self.assertEqual(sorted(row['id'] for row in compared), sorted(runtime['tasks']))
                    self.assertEqual([row['result_count'] for row in compared], [HISTORY_PER_TASK] * TASK_COUNT)
                    for row in compared:
                        source = read_source(root, row['source_ref'], limit=row['source_ref']['bytes'])
                        self.assertEqual((source['status'], source['truncated']), ('ok', False))
                        self.assertEqual(json.loads(source['bytes']), runtime['tasks'][row['id']])
                    ref = result['context']['profile_selection']['profiles_ref']
                    source = read_source(root, ref, limit=ref['bytes'])
                    self.assertEqual((source['status'], source['truncated']), ('ok', False))
                    supplied = json.loads(source['bytes'])
                    self.assertEqual({p['id']: p for p in supplied}, instance['execution_profiles'])
                if role == 'research_plan':
                    self.assertEqual(sorted(result['context']['ready_task_ids']), sorted(runtime['tasks']))
