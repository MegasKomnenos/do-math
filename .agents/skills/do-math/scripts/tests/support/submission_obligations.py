"""제출 2-A의 구조 입구 표. 정상 외곽과 잘못된 목표 원소를 분리한다.

등록부는 제품 EXTENSION_ROLES, 국면은 extension_schema의 조건에서 온다.
이 표는 구조 반려만 선언한다. 실행 시점의 권한·현재성·도메인 적용은
실제 역할 호출에서 따로 확인해야 하며, 구조 표본을 의미상 정상 답으로 세지 않는다.
"""
from copy import deepcopy
from dataclasses import dataclass
import re

from do_math import contracts, integration, submission
from support.ingress import malformed, NOT_TEXTS


@dataclass(frozen=True)
class Ingress:
    name: str
    action: dict
    family: str
    schema: dict
    premise: str
    receiver: str = 'submission.payload_issues → integration.inspect_bundles'
    rejection: str = 'schema.type와 정확한 activity-extensions.json 좌표'
    consumption: str = '중앙 요청 영수증·check·event 불변, 새 정상 요청은 별도 수락'


def action_rows():
    """역할 전건과 키 존재/값을 판정하는 세 가지 국면 분기."""
    rows = [(role, {'role': role}, 'contracts.ROLES의 보통 역할') for role in contracts.ROLES]
    for fields in ({'assessment_targets': {}}, {'observation_rule_targets': {}},
                   {'assessment_targets': {}, 'observation_rule_targets': {}}):
        rows.append(('research_preparation:' + '+'.join(fields),
                     {'role': 'research_preparation', **fields},
                     'model_policy.preparation_only는 대상 키의 존재를 판정'))
    rows.extend([
        ('identity_review:cycle', {'role': 'identity_review', 'review_cycle_id': 'RV-input'},
         'research_requests는 실제 cycle ID가 있는 경우만 허용'),
        ('supplemental_research:cycle', {'role': 'supplemental_research', 'review_cycle_id': 'RV-input'},
         'execution_profiles.review_research의 고정 질문 조사에는 확장 없음'),
    ])
    return rows


def extension_ingresses():
    return [Ingress(name + ':' + family, action, family, shape, premise)
            for name, action, premise in action_rows()
            for family, shape in submission.extension_schema(action)['properties'].items()]


def schema_seed(schema):
    """오입력의 외곽을 만드는 구조 표본. 의미상 수락 표본은 아니다.

새 형식을 추측하지 않는다. 지원하지 않는 pattern은 명시적으로 실패한다.
각 소비 시험은 완성한 외곽을 JSON Schema로 먼저 검증한다.
"""
    if 'const' in schema:
        return deepcopy(schema['const'])
    if 'enum' in schema:
        return deepcopy(schema['enum'][0])
    for alternative in ('anyOf', 'oneOf'):
        if alternative in schema:
            return schema_seed(schema[alternative][0])
    kind = schema.get('type', 'object')
    if isinstance(kind, list):
        kind = kind[0]
    if kind == 'object':
        value = {key: schema_seed(schema['properties'][key]) for key in schema.get('required', [])}
        for key, child in schema.get('properties', {}).items():
            if len(value) >= schema.get('minProperties', 0):
                break
            value.setdefault(key, schema_seed(child))
        while len(value) < schema.get('minProperties', 0):
            if schema.get('additionalProperties') is False:
                raise AssertionError('닫힌 구조 표본에서 minProperties를 만족할 키가 없다')
            value['구조표본' + str(len(value))] = '값'
        # Conditional requirements belong to the supplied schema, including
        # the property constraints that make its required fields valid.
        from jsonschema import Draft202012Validator
        for clause in schema.get('allOf', []):
            if 'if' in clause and Draft202012Validator(clause['if']).is_valid(value):
                consequence = clause.get('then', {})
                for key in consequence.get('required', []):
                    value.setdefault(key, schema_seed(schema['properties'][key]))
                for key, child in consequence.get('properties', {}).items():
                    if key in value:
                        value[key] = schema_seed({**schema['properties'][key], **child})
        return value
    if kind == 'array':
        return [schema_seed(schema.get('items', {})) for _ in range(schema.get('minItems', 0))]
    if kind == 'null':
        return None
    if kind == 'boolean':
        return False
    if kind in ('integer', 'number'):
        return max(0, schema.get('minimum', 0))
    if kind == 'string':
        if 'pattern' in schema:
            candidates = ['0' * 64, '0' * 40, '2090-01-02T00:00:00+00:00',
                          *[prefix + '-' + '0' * 26 for prefix in ('KN', 'EP', 'TK', 'IN', 'GR')]]
            for value in candidates:
                if re.search(schema['pattern'], value):
                    return value
            raise AssertionError('구조 표본에 명시되지 않은 pattern: ' + schema['pattern'])
        return '표본' * max(1, schema.get('minLength', 1))
    raise AssertionError('구조 표본에 명시되지 않은 type: ' + str(kind))


def structural_envelope(action, extensions):
    schema = contracts.action_schema(action)
    output = schema_seed(schema)
    output.pop('integration_bundles', None)
    output.pop('repair_responses', None)
    context = {'action': action, 'execution_id': 'EX-structural', 'snapshot': 'a' * 40,
               'tasks': [], 'knowledge_catalog': [], 'grants': [], 'decisions': [],
               'available_input_refs': [], 'supplied_record_ids': []}
    # 잘못된 가족의 배열 형은 member_values에서 거부되므로, 소유 좌표는
    # 정상 대조 배열에서 먼저 만든다. 원소형 오류는 이 외곽을 보존한다.
    members = integration.member_values(output, extensions, context)
    output['integration_bundles'] = [{'integration_id': 'IN-structural',
        'members': sorted(members), 'impact_set': [], 'authority_refs': []}]
    return output, schema, context


def item_shapes():
    """공통 malformed의 객체가 아닌 원소 전건. 정상 배열 외곽에 넣는다."""
    return malformed({'type': 'object'})


def mutation_target_inputs(family, schema):
    """개정/철회 식별자에 해시 불가능한 비빈 JSON도 포함한다."""
    field = {'knowledge_changes': 'id', 'task_dispositions': 'task_id',
             'revision_resolutions': 'record_id'}.get(family)
    if field is None:
        return
    for value in [*NOT_TEXTS, ['wrong-id'], {'id': 'wrong-id'}]:
        item = schema_seed(schema['items'])
        item[field] = value
        yield field, [item]


ROOT_REFERENCES = ('.', './', 'workspace:.', 'workspace:./')


def maintenance_output():
    return {'summary': '제출 입구 계약', 'used_sources': [], 'questions': [],
            'report': '정상 외곽을 보존한 반려와 뒤 정상 제출을 확인한다.', 'remaining_work': []}


def required_and_enum_inputs(schema):
    """정상 구조 표본에서 필수 키 하나 또는 열거값 하나만 바꾼다.

배열은 정상 원소 한 개를 넣어 중첩 경계까지 내려간다. 각 대안의
표본은 해당 대안의 정본으로 만들며 소비자가 전체 스키마를 재검사한다.
"""
    seed = schema_seed(schema)
    kind = schema.get('type')
    if kind == 'array' and 'items' in schema:
        seed = [schema_seed(schema['items'])]
        for label, changed in required_and_enum_inputs(schema['items']):
            yield '0/' + label, [changed]
    elif kind == 'object':
        for key in schema.get('required', []):
            changed = deepcopy(seed)
            del changed[key]
            yield key + ':required', changed
        for key, child in schema.get('properties', {}).items():
            for label, value in required_and_enum_inputs(child):
                changed = deepcopy(seed)
                changed[key] = value
                yield key + '/' + label, changed
    if 'enum' in schema:
        yield ':enum', '열거_밖_제출_값'
    if 'const' in schema:
        yield ':const', '고정값_밖_제출_값'
