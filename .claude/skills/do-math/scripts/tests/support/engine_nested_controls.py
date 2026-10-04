"""정상 외곽을 보존한 중첩 입구 행. 잘못된 잎은 공통 malformed 정본에서 얻는다."""
from copy import deepcopy

from support.ingress import malformed
from support.knowledge_builders import knowledge_candidate


def nested_controls():
    cases = [
        ('input', {'responds_to': ['QU-one']}, ('responds_to', 0), 'string'),
        ('decision', {'change': {'kind': 'grant', 'grant': {'id': 'GR-nested', 'kind': 'local',
            'roles': ['research_work'], 'reuse': 'reusable'}}}, ('change', 'grant', 'roles', 0), 'string'),
        ('knowledge', {'operation': 'import', 'candidate': knowledge_candidate()},
            ('candidate', 'declaration_names', 0), 'string'),
        ('request', {'role': 'identity_review', 'assessment_reassessment': {
            'assessment_id': 'IA-one', 'assessment_sha256': 'a' * 64, 'evidence': {}}},
            ('assessment_reassessment', 'evidence'), 'object'),
    ]
    rows = []
    for action, original, path, kind in cases:
        generated = malformed({'properties': {'leaf': {'type': kind}}})
        for index, (label, wrong) in enumerate(generated):
            value = deepcopy(original)
            parent = value
            for part in path[:-1]:
                parent = parent[part]
            parent[path[-1]] = wrong['leaf']
            reason = 'config/' + '/'.join(map(str, path)) + ': invalid type (expected ' + kind + ')'
            rows.append((f'{action}-{index}', action, original, value, reason))
    return rows
