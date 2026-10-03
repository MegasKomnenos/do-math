"""A checked active delegation built by real governance, interpretation and storage producers."""
from copy import deepcopy

from do_math import delegations, governance
from support.governance_sim import interpreted, returned
from support.sim import Sim, built


def _delegated(root, shared):
    sim = Sim.activated(root, shared=shared)
    source = governance.preserve_source('GS-close-delegation', '인스턴스의 한정된 검토를 위임한다.', origin='user')
    sim.instance['governance_sources'][source['id']] = source
    changes = [
        {'kind': 'grant', 'decision_id': 'DC-close-original', 'grant': {
            'id': 'GR-close', 'kind': 'local', 'roles': ['maintenance'], 'reuse': 'reusable'}},
        {'kind': 'delegation', 'decision_id': 'DC-close-delegation', 'delegation': {
            'id': 'DG-close', 'status': 'active', 'decision_kind': 'grant',
            'original_decision_id': 'DC-close-original', 'included_targets': [sim.instance['id']],
            'excluded_targets': [], 'external_effects': [], 'resource_limits': {'steps': 2},
            'expires_at': '2099-01-01T00:00:00Z'}},
    ]
    for change in changes:
        sim.engine.instance, sim.engine.runtime, _ = governance.apply_decision(
            sim.instance, sim.runtime, change, source_ref=source['id'], clock=sim.clock)
    case = {'id': 'CASE-close', 'decision_kind': 'grant', 'target_id': sim.instance['id'],
            'external_effects': [], 'resources': {'steps': 1}, 'effect': {'operation': 'bounded_review'},
            'basis_refs': [governance.governance_view(sim.instance)['charter']['id']]}
    application = delegations.prepare_application(sim.instance, sim.runtime, 'DG-close', case, now_iso=sim.clock.now())
    for stage, eid in (('interpret', 'EX-close-interpret'), ('check', 'EX-close-check')):
        execution = returned(sim.engine, {'id': 'AC-' + eid, 'role': 'intent_interpretation',
            'target': sim.instance['lifecycle']['input_id'], 'delegation_application_id': application['id']}, eid)
        execution['delegation_input_sha256'] = application['input_sha256']
        delegations.record_judgment(sim.runtime, application['id'], {
            'input_sha256': application['input_sha256'], 'decision': 'within_scope',
            'reason': '보존한 사용자 결정의 범위와 일치한다.'}, execution_id=eid, stage=stage)
    sim.engine._save()
    return sim

def delegated_sim():
    return built('governance-close-delegated', _delegated)


def _question(root, shared):
    sim = Sim.activated(root, shared=shared)
    sim.model.on('intent_interpretation').reply(interpreted(question='자연수 범위인가?'))
    sim.control('input', text='명제의 범위를 확인한다.', request_id='IN-close-question')
    sim.run_until(lambda s: any(row.get('kind') == 'import_user_decision'
                               for row in s.runtime.get('waiting_actions', {}).values()), max_steps=12)
    return sim


def question_sim():
    return built('governance-close-question', _question)


def question_bundle(sim):
    wait = next(row for row in sim.runtime['waiting_actions'].values() if row.get('kind') == 'import_user_decision')
    return sim.runtime['intent_imports'][wait['import_id']]


def _initial_question(root, shared):
    from support.governance_sim import initial_sim
    return initial_sim(root, question='자연수 범위인가?', shared=shared)


def initial_question_sim():
    return built('governance-initial-question', _initial_question)


def _records(root, shared):
    sim = Sim.activated(root, shared=shared)
    source = governance.preserve_source('GS-close', '정확한 정책과 감사 및 위임을 승인한다.', origin='user')
    sim.instance['governance_sources'][source['id']] = source
    charter = governance.governance_view(sim.instance)['charter']['id']
    records = [
        {'id': 'PO-close', 'kind': 'policy', 'revision': 1, 'supersedes': [],
         'content': {'rule_id': 'bounded', 'text': '정해진 범위만 연구한다.', 'scope': ['P'],
                     'reason_refs': [charter], 'audit_refs': []}},
        {'id': 'CX-close', 'kind': 'research_context', 'revision': 1, 'supersedes': [],
         'content': {'terms': [{'term': 'P', 'definition': '연구 명제', 'boundary': '자연수',
                                'avoid_synonyms': [], 'record_refs': [charter]}]}},
        {'id': 'AU-close', 'kind': 'additional_audit', 'revision': 1, 'supersedes': [],
         'content': {'scope': ['P'], 'required_inputs': [charter], 'assessor': 'goal_audit',
                     'verdict_mapping': {'pass': 'satisfied', 'partial': 'not_satisfied', 'unknown': 'unresolved'}}},
    ]
    for record in records:
        sim.engine.instance, sim.engine.runtime, _ = governance.apply_decision(
            sim.instance, sim.runtime, {'kind': record['kind'], 'record': record},
            source_ref=source['id'], clock=sim.clock)
    sim.engine._save()
    return sim


def records_sim():
    return built('governance-close-records', _records)


def proposed_record(instance, identifier):
    """저장 행에서 실제 승인 결정의 원래 제안을 꺼낸다."""
    record = instance['governance'][identifier]
    return deepcopy(instance['decisions'][record['approval_ref']]['change']['record'])


def _planned(root, shared):
    sim = Sim.activated(root, shared=shared)
    sim.run_until(lambda s: any(a['role'] == 'research_work' for a in s.runtime['queue']), max_steps=16)
    return sim


def planned_sim():
    return built('governance-close-planned', _planned)


def _auditor(root, shared):
    sim = _records(root, shared)
    action = {'id': 'AC-close-auditor', 'role': 'goal_audit', 'target': None,
              'basis': sim.engine._goal_basis_key(), 'required': 2, 'slot': 0}
    execution = returned(sim.engine, action, 'EX-close-auditor')
    sim.engine._bind_governance_input(action, execution, sim.engine._governance_context(action, {}))
    sim.engine._save()
    return sim


def auditor_sim():
    return built('governance-close-auditor', _auditor)


def audit_output(sim, verdict='pass'):
    """실제 전달된 감사 입력을 답의 좌표로 사용한다."""
    execution = sim.runtime['executions']['EX-close-auditor']
    return {'decision': 'satisfied', 'scope_complete': True, 'used_sources': [],
            'summary': '승인된 감사 기준 비교', 'questions': [], 'reason': '전달된 기록으로만 판단한다.',
            'additional_audits': [{'audit_ref': 'AU-close', 'assessor': 'goal_audit', 'verdict': verdict,
                'reason': '승인된 기준과 비교한 합성 판단',
                'input_hashes': deepcopy(execution['additional_audit_input'][0]['input_hashes'])}]}


def _review_question(root, shared):
    from support.engine_lifecycle import applied, clear_work
    from support.model import amend
    sim = Sim.activated(root, shared=shared)
    clear_work(sim)
    # 질문이 남은 initial 답은 match가 아니다. 실제 수신 계약의 unresolved를 쓴다.
    sim.model.on('identity_review', stage='initial').reply(amend(
        decision='unresolved', questions=['표현 범위의 후속 연구는?']))
    name = 'governance_close_theorem'
    source = f'theorem {name} : 1 = 1 := rfl'
    sim.lean.allow(source, [name], signatures={name: name + ' : 1 = 1'},
        declaration_evidence={name: {'type': '1 = 1', 'value': None}}, axioms={name: []}, dependencies={name: {}})
    applied(sim, 'knowledge', config={'operation': 'import', 'candidate': {
        'kind': 'theorem', 'title': name, 'statement': 'One equals one (' + name + ')',
        'summary': 'Reflexivity', 'explanation': 'By reflexivity.', 'lean_code': source,
        'declaration_names': [name], 'dependencies': []}})
    # 단언 대상인 봉인된 질문 결과가 확정되는 첫 소유자 반환에서 멈춘다.
    sim.run_until(lambda s: any(row.get('output', {}).get('questions')
        for cycle in s.runtime['review_cycles'].values() for row in cycle['results'].values()), max_steps=12)
    return sim


def review_question_sim():
    return built('governance-close-review-question', _review_question)


def _unadopted(root, shared):
    return Sim(root, shared=shared)


def initial_approval_scene():
    """공개 최초 승인 생산자의 전후 상태와 정확한 승인 입력을 반환한다."""
    from support.engine_lifecycle import applied
    from support.state_builders import charter_record
    sim = built('governance-close-unadopted', _unadopted)
    before_i, before_r = deepcopy(sim.instance), deepcopy(sim.runtime)
    record = charter_record(sim.instance['lifecycle']['immutable_input']['text'])
    applied(sim, 'decision', text='정확한 최초 헌장을 승인한다.', request_id='DC-close-initial',
            config={'change': {'kind': 'initialization', 'operation': 'governance', 'records': [record]}})
    installed = sim.instance['governance'][record['id']]
    approval = deepcopy(sim.instance['decisions'][installed['approval_ref']])
    source = deepcopy(sim.instance['governance_sources'][installed['source_ref']])
    approval_source = deepcopy(sim.instance['governance_sources'][approval['source_ref']])
    return sim, before_i, before_r, source, approval, approval_source, [record]


def replacement_engine(root):
    """저장 계약을 지나는 실제 검토 복구 생산자로 교체 행동을 만든다."""
    from support.review_inputs import grant_replacement
    from support.review_scene import ReviewScene
    scene = ReviewScene(root)
    engine = scene.engine
    # 합성 후보가 인용한 작성 실행을 실제 등록·종료 생산자로 보충한다.
    returned(engine, {'id': 'AC-close-author', 'role': 'research_work'}, 'author')
    grant_replacement(engine)
    scene.start('K1')
    action = deepcopy(scene.pending())
    engine._record_review_recovery(action, ValueError('permanent_loss'), retryable=False)
    result = engine._authorize_review_replacement(action, grant_id='GR-review')
    if result['disposition'] != 'replacement_ready':
        raise AssertionError('정상 검토 교체 생산 실패: ' + repr(result))
    replacement = next(a for a in engine.runtime['queue'] if a.get('replacement_for') is not None)
    engine._save()
    return engine, deepcopy(replacement)


def _transfer(root, shared):
    """의무 이전 직전의 두 과제와 실제 독립 계획 실행을 저장한다."""
    from do_math import planning
    from support.engine_lifecycle import applied, clear_work, task
    sim = Sim.activated(root, shared=shared)
    clear_work(sim)
    task(sim.engine, 'TK-close-source')
    task(sim.engine, 'TK-close-target')
    work = returned(sim.engine, {'id': 'AC-close-work', 'role': 'research_work',
        'target': 'TK-close-source'}, 'EX-close-work')
    donor = sim.runtime['tasks']['TK-close-source']
    donor.update(status='waiting', results=[{'id': 'EV-close-work', 'execution_id': work['id']}])
    sim.engine._save()
    donor = sim.runtime['tasks']['TK-close-source']
    applied(sim, 'decision', request_id='DC-close-transfer', config={'change': {
        'kind': 'task_scope', 'task_id': donor['id'], 'disposition': 'transfer',
        'revision': donor['revision'], 'contract_sha256': planning.contract_hash(donor),
        'obligation_ids': [row['id'] for row in donor['completion_obligations']],
        'target_task_id': 'TK-close-target', 'reason': '남은 의무를 독립 수신 과제로 옮긴다.'}})
    clear_work(sim)
    snapshot = sim.engine.head
    execution = returned(sim.engine, {'id': 'AC-close-transfer-plan', 'role': 'research_plan'}, 'EX-close-transfer-plan')
    execution.update(input_snapshot=snapshot, **planning.governance_revisions(sim.instance))
    sim.engine._save()
    return sim


def transfer_sim():
    return built('governance-close-transfer', _transfer)


def transfer_output(sim):
    """사용자가 승인한 이전의 정확한 의무와 대상만 답에 포함한다."""
    from support.role_answers import disposition
    donor = sim.runtime['tasks']['TK-close-source']
    decision = next(row['id'] for row in sim.instance['decisions'].values()
                    if row.get('change', {}).get('task_id') == donor['id']
                    and row['change'].get('disposition') == 'transfer')
    return {'summary': '의무를 이전한 뒤 수신 과제를 고른다.', 'used_sources': [], 'questions': [],
        'dispositions': [disposition('TK-close-target')], 'preparation_requests': [], 'goal_audit': False,
        'task_assessments': [{'task_id': donor['id'], 'decision': 'closed', 'reason': '모든 의무의 명시적 이전',
            'item_dispositions': [{'obligation_id': row['id'], 'kind': 'transferred', 'evidence_refs': [],
                'authority_ref': decision, 'target_task_id': 'TK-close-target',
                'target_obligation_id': 'INHERITED-' + row['id']} for row in donor['completion_obligations']],
            'unresolved': []}]}
