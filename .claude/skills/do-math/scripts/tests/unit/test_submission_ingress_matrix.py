"""2-A: 제품 등록부 전건을 정상 역할 외곽 안에서 거부한다.

구조 표본만 쓰는 이 파일은 중앙 소비·의미 적용의 증거가 아니다.
오입력마다 정확한 schema rule/path/message를 독립 JSON Schema 계약과 대조한다.

정상 외곽 검증과 가족·국면 전건 순회 때문에 첫 실측 최대 0.922초로 단위 예산을 넘는다.
"""
from copy import deepcopy
from pathlib import Path
import tempfile
import unittest

import jsonschema

from do_math import contracts, submission
from support.fakes.clock import FakeClock
from support.ingress import malformed
from support.submission_obligations import (
    action_rows, extension_ingresses, item_shapes, structural_envelope, required_and_enum_inputs, schema_seed,
    mutation_target_inputs,
)


class ExtensionIngressTests(unittest.TestCase):
    def test_nontext_mutation_targets_return_schema_issues_without_hashing_the_target(self):
        """정상 외곽 안의 개정/철회 대상 형 오류를 구조화 반려한다."""
        clock = FakeClock()
        with tempfile.TemporaryDirectory() as directory:
            for row in extension_ingresses():
                for field, value in mutation_target_inputs(row.family, row.schema):
                    with self.subTest(ingress=row.name, field=field, value=value):
                        extensions = {row.family: value}
                        output, schema, context = structural_envelope(row.action, extensions)
                        original = deepcopy((output, extensions, context))
                        error, = jsonschema.Draft202012Validator(row.schema).iter_errors(value)
                        issues = submission.payload_issues(output, schema, context, extensions,
                            Path(directory), clock=clock)
                        self.assertEqual([(i['rule_id'], i['path'], i['message']) for i in issues],
                            [('schema.type', 'activity-extensions.json/' + row.family + '/0/' + field,
                              error.message)])
                        self.assertEqual((output, extensions, context), original)

    def test_every_family_required_and_nested_enum_rejections_keep_original_coordinates(self):
        """역할·국면 전건의 필수/열거 오류를 정상 외곽 안에서 대조한다."""
        clock = FakeClock()
        with tempfile.TemporaryDirectory() as directory:
            for row in extension_ingresses():
                jsonschema.Draft202012Validator(row.schema['items']).validate(schema_seed(row.schema['items']))
                for label, value in required_and_enum_inputs(row.schema):
                    with self.subTest(ingress=row.name, malformed=label):
                        extensions = {row.family: value}
                        output, schema, context = structural_envelope(row.action, extensions)
                        jsonschema.Draft202012Validator(schema).validate(output)
                        before = deepcopy((output, extensions, context))
                        expected = []
                        for error in jsonschema.Draft202012Validator(
                                submission.extension_schema(row.action)).iter_errors(extensions):
                            path = '/'.join(['activity-extensions.json', *map(str, error.absolute_path)])
                            if error.validator == 'required':
                                # 제출 반려 정본은 빠진 키 자체를 좌표로 지목한다.
                                expected.extend(('schema.required', path + '/' + key,
                                    'required property is missing') for key in error.validator_value
                                    if key not in error.instance)
                            else:
                                expected.append(('schema.' + error.validator, path, error.message))
                        self.assertTrue(expected, (row.name, label))
                        issues = submission.payload_issues(output, schema, context, extensions,
                            Path(directory), clock=clock)
                        self.assertEqual(sorted((issue['rule_id'], issue['path'], issue['message'])
                            for issue in issues if issue['rule_id'].startswith('schema.')), sorted(expected))
                        self.assertEqual((output, extensions, context), before)

    def test_registry_union_and_role_phase_filters_are_complete(self):
        rows = extension_ingresses()
        self.assertEqual({row.family for row in rows}, set(submission.EXTENSION_ROLES))
        self.assertEqual({action['role'] for _, action, _ in action_rows()}, set(contracts.ROLES))
        self.assertEqual(len({row.name for row in rows}), len(rows))
        for name, action, _ in action_rows():
            with self.subTest(action=name):
                actual = set(submission.extension_schema(action)['properties'])
                expected = {family for family, roles in submission.EXTENSION_ROLES.items()
                            if action['role'] in roles}
                if action['role'] == 'research_preparation' and any(
                        key in action for key in ('assessment_targets', 'observation_rule_targets')):
                    expected &= {'model_assessments', 'model_assessment_deferrals',
                                 'task_conditions', 'observation_rule_deferrals'}
                    if 'observation_rule_targets' not in action:
                        expected -= {'task_conditions', 'observation_rule_deferrals'}
                else:
                    expected -= {'model_assessment_deferrals', 'observation_rule_deferrals'}
                if action['role'] == 'supplemental_research' and action.get('review_cycle_id'):
                    expected.clear()
                if not action.get('review_cycle_id'):
                    expected.discard('research_requests')
                self.assertEqual(actual, expected)

    def test_every_family_rejects_nonobject_elements_at_the_element_coordinate(self):
        clock = FakeClock()
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            for row in extension_ingresses():
                for label, value in item_shapes():
                    with self.subTest(ingress=row.name, malformed=label):
                        extensions = {row.family: [value]}
                        output, schema, context = structural_envelope(row.action, extensions)
                        jsonschema.Draft202012Validator(schema).validate(output)
                        original = deepcopy((output, context, extensions))
                        issues = submission.payload_issues(output, schema, context, extensions,
                                                           workspace, clock=clock)
                        errors = list(jsonschema.Draft202012Validator(row.schema['items']).iter_errors(value))
                        self.assertEqual(len(errors), 1)
                        expected = ('schema.type', f'activity-extensions.json/{row.family}/0', errors[0].message)
                        self.assertEqual([(issue['rule_id'], issue['path'], issue['message'])
                                          for issue in issues if issue['rule_id'].startswith('schema.')], [expected])
                        self.assertEqual((output, context, extensions), original)

    def test_every_family_rejects_wrong_array_type_without_losing_the_outer_output(self):
        clock = FakeClock()
        with tempfile.TemporaryDirectory() as directory:
            for row in extension_ingresses():
                output, schema, context = structural_envelope(row.action, {row.family: []})
                jsonschema.Draft202012Validator(schema).validate(output)
                wrong = malformed({'type': 'object', 'properties': {row.family: row.schema}})
                for label, changed in wrong:
                    if not isinstance(changed, dict):
                        continue
                    with self.subTest(ingress=row.name, malformed=label):
                        issues = submission.payload_issues(output, schema, context, changed,
                                                           Path(directory), clock=clock)
                        error, = jsonschema.Draft202012Validator(row.schema).iter_errors(changed[row.family])
                        self.assertEqual([(i['rule_id'], i['path'], i['message']) for i in issues
                                          if i['rule_id'].startswith('schema.')],
                                         [('schema.type', 'activity-extensions.json/' + row.family, error.message)])

    def test_every_role_rejects_nonobject_output_at_output(self):
        clock = FakeClock()
        with tempfile.TemporaryDirectory() as directory:
            for name, action, _ in action_rows():
                schema = contracts.action_schema(action)
                for label, value in malformed({'type': 'object'}):
                    with self.subTest(role=name, malformed=label):
                        errors = submission.payload_issues(value, schema, {'action': action}, {},
                                                           Path(directory), clock=clock)
                        expected, = jsonschema.Draft202012Validator({'type': 'object'}).iter_errors(value)
                        self.assertEqual([(i['rule_id'], i['path'], i['message']) for i in errors],
                                         [('schema.type', 'output', expected.message)])
