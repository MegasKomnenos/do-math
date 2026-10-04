"""10-A 역할×대표 상태 입력표. 규모와 계약 상한은 측정 전에 고정한다.

역할 모집단은 contracts.ROLES, 세부 상태는 context_store.input_scope와
role_direct_keys 및 초기화-운전의 호출 전제를 대조한다. 표의 상태는 포장
입력이며 실제 검토 자리 생산·저장 사슬을 대신하지 않는다.
"""
from copy import deepcopy

from do_math.contracts import ROLES
from support.record_builders import surface_state, task_contract


TASK_COUNT = 100
HISTORY_PER_TASK = 10
PROFILE_COUNT = 37

# 각 행은 공통 정상 상태 외에 입력 분류나 필수 근거가 달라지는 실제 조건이다.
VARIANTS = {
    'research_preparation': ({}, {'assessment_targets': {'TK-000': 1}},
                             {'observation_rule_targets': {'TK-000': 1}}),
    'research_plan': ({},),
    'research_work': ({}, {'continuation_of': 'EX-previous'}),
    'task_contract_review': ({},),
    'identity_review': tuple({'stage': stage} for stage in ('scope', 'initial', 'organize', 'answer', 'judge')),
    'goal_audit': ({},),
    'supplemental_research': ({}, {'review_cycle_id': 'RC-size'}),
    'intent_interpretation': ({'stage': 'interpret'}, {'stage': 'check'},
                              {'delegation_application_id': 'DA-size'}),
    'maintenance': ({}, {'kind_definition_id': 'KD-size'}, {'stage': 'impact_review'},
                    {'initial_submission_diagnosis': True}),
    'operational_review': ({}, {'target': 'EX-review'}, {'target': 'EX-audit'}),
}


def role_cases():
    """중앙 역할을 전부 순회하고 새 역할의 대표 상태 선언 누락은 거부한다."""
    if set(VARIANTS) != set(ROLES):
        raise AssertionError('10-A 역할 대표 상태표가 ROLES와 다름')
    return [(role, index, {'role': role, **deepcopy(options)})
            for role in ROLES for index, options in enumerate(VARIANTS[role])]


def scale_state():
    """실제 기본 프로필 생산자와 계약 입력 빌더로 37개·100×10 규모를 만든다."""
    instance, runtime = surface_state()
    tasks = {}
    for index in range(TASK_COUNT):
        task = task_contract()
        task.update(id=f'TK-{index:03d}', status='planned', title=f'규모 과제 {index}',
                    results=[{'execution_id': f'EX-{index:03d}-{turn:02d}',
                              'report': f'과제 {index}의 독립 이력 {turn}: 전제와 미해결 의무를 보존한다.'}
                             for turn in range(HISTORY_PER_TASK)])
        tasks[task['id']] = task
    runtime.update(tasks=tasks, executions={
        'EX-review': {'id': 'EX-review', 'status': 'ended', 'action': {'review_cycle_id': 'RC-size'}},
        'EX-audit': {'id': 'EX-audit', 'status': 'ended', 'action': {'role': 'goal_audit'}}})
    return instance, runtime


def scale_context(instance, runtime, action):
    """필수 모집단은 자르지 않고 프로필 원문도 실제 현행 등록부 전건을 공급한다."""
    task = deepcopy(runtime['tasks']['TK-000'])
    direct = {
        'research_preparation': {'resources': {}, 'knowledge_catalog': [], 'blocked_actions': []},
        'research_plan': {'resources': {}, 'knowledge_catalog': [], 'ready_task_ids': list(runtime['tasks'])},
        'research_work': {'task': task}, 'task_contract_review': {'task': task},
        'supplemental_research': ({'review_research': {'sources': []}, 'proposal': {'revision': 1}}
                                  if action.get('review_cycle_id') else {'task': task}),
        'identity_review': {'role_review': {'stage': action.get('stage'), 'source_refs': []}},
        'goal_audit': {'eligible_knowledge': []},
        'intent_interpretation': {'user_request': {'id': 'UI-size', 'text': '제약을 포함한 요청 전문'},
                                  'interpretation_to_check': None},
        'operational_review': {'execution_to_review': {'id': action.get('target', 'EX-general')},
                               'observation': {}, 'operational_evidence': {}, 'admissible_basis_refs': []},
        'maintenance': {'impact_review_input': {}} if action.get('stage') == 'impact_review' else {},
    }[action['role']]
    if action.get('continuation_of'):
        direct.update(previous_execution={'id': action['continuation_of']},
                      continuation_history=[{'execution_id': action['continuation_of'], 'report': '이전 수행 근거'}])
    return {'action': {'id': 'AC-size', **action}, 'tasks': deepcopy(list(runtime['tasks'].values())),
            'execution_profiles': deepcopy(list(instance['execution_profiles'].values())),
            'role_profile_refs': deepcopy(instance['role_profile_refs']), **direct}


def stored_scale_sim():
    """정상 계약 생산자와 실행 수명 생산자로 100×10을 만들고 실제 저장 검증을 지난다.

    모델 1000회를 실행했다는 주장이 아니다. 검사의 시작점은 종료 실행을 참조하는
    저장 입력이며 실제 도메인 생산자를 쓴다. 현재 프로필은 과거 판본과 구별한다.
    """
    from do_math.contracts import task_candidate_record
    from support.engine_lifecycle import _ended_execution, research_grant
    from support.role_answers import candidate
    from support.sim import Sim
    sim = Sim.activated()
    engine = sim.engine
    _ended_execution(engine, 'EX-size-author', 'research_preparation')
    for index in range(TASK_COUNT):
        identifier = f'TK-size-{index:03d}'
        proposed = candidate(title=f'규모 과제 {index}')
        proposed.update(profile_refs=deepcopy(sim.instance['role_profile_refs']['research_work']),
                        authority_refs=[research_grant(engine)])
        row = task_candidate_record(proposed, task_id=identifier)
        row.pop('revises_task_id')
        row.update(status='planned', producer_execution='EX-size-author', results=[], reviews=[],
                   occurrence_condition={'op': 'always'}, initial_observation_rules=[], revision_history=[])
        for turn in range(HISTORY_PER_TASK):
            execution_id = f'EX-size-{index:03d}-{turn:02d}'
            _ended_execution(engine, execution_id, 'research_work')
            row['results'].append({'id': f'EV-size-{index:03d}-{turn:02d}',
                'execution_id': execution_id, 'report': f'과제 {index} 이력 {turn}: 원문 근거와 남은 의무'})
        engine.runtime['tasks'][identifier] = row
    engine._save()
    sim.restart()
    return sim
