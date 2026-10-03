"""3-A의 실제 prepare_role_input 표본. 구조 입력과 공개 호출 증거를 구별한다."""
from copy import deepcopy
from pathlib import Path

from do_math import contracts, submission
from do_math.context_store import prepare_role_input
from support.fakes.clock import FakeClock
from support.record_builders import surface_state


SOURCE = {'id': 'SO-advertised', 'name': '논문.txt', 'path': 'research/sources/논문.txt',
          'local_path': 'input/sources/논문.txt'}
SOURCE_FORMS = ('SO-advertised', '논문.txt', 'source:논문.txt',
                'research/sources/논문.txt', 'input/sources/논문.txt')


def advertised_input(root, role, *, recovery=False):
    """역할 직접 자료의 최소 모양. cycle/ready/returned의 의미 상태는 만들지 않는다."""
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    instance, runtime = surface_state()
    action = {'id': 'AC-advertised', 'role': role}
    direct = {
        'research_preparation': {'tasks': [], 'resources': {}, 'knowledge_catalog': [], 'blocked_actions': []},
        'research_plan': {'tasks': [], 'resources': {}, 'knowledge_catalog': [], 'ready_task_ids': [],
                          'input_overflow_requests': [], 'review_followups': []},
        'research_work': {'task': {'id': 'TK-assigned'}},
        'supplemental_research': {'task': {'id': 'TK-assigned'}},
        'task_contract_review': {'task': {'id': 'TK-assigned'}},
        'identity_review': {'role_review': {}},
        'goal_audit': {'eligible_knowledge': []},
        'operational_review': {'execution_to_review': {'id': 'EX-work'}, 'observation': {},
                               'operational_evidence': {}, 'admissible_basis_refs': ['EX-work']},
        'intent_interpretation': {'user_request': {'id': 'UI-source'}, 'interpretation_to_check': None},
        'maintenance': {},
    }
    if set(direct) != set(contracts.ROLES):
        raise AssertionError('새 역할의 직접 자료 전제를 submission_advertised에 추가해야 한다')
    context = {'action': action, 'execution_id': 'EX-advertised', 'sources': [deepcopy(SOURCE)], **direct[role]}
    if recovery:
        context['previous_execution'] = {'id': 'EX-previous', 'result_source': {
            'artifact_ref': 'runtime/artifacts/BA-previous/result.json'}}
    source = root / SOURCE['local_path']
    source.parent.mkdir(parents=True, exist_ok=True)
    source.write_bytes('제공한 원문'.encode('utf-8'))
    profile = next(p for p in instance['execution_profiles'].values() if p['role'] == role)
    return prepare_role_input(context, instance=instance, runtime=runtime, role=role,
        profile=profile, snapshot='a' * 40, workspace=root, activity_id=action['id'],
        output_schema=contracts.action_schema(action), install_submission_tools=True,
        max_artifact_bytes=None, clock=FakeClock())


def pair_samples(root):
    return [(role, (advertised_input(root / role, role)['validation_context'], root / role))
            for role in contracts.ROLES]


def receive_catalog(value):
    context, workspace = value
    for row in context['reference_catalog']:
        submission.validate_reference(row['value'], context, workspace)
