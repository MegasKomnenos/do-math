"""Real relation, approved task, input seal and delegated revision producers."""
from copy import deepcopy
from do_math import contracts, planning
from support.role_answers import candidate, disposition, review_items


def produce_task(sim, title='계획 과제', *, revises=None, inputs=(), revision_targets=(), obligations=None,
                 question=None, profiles=None):
    """수신자가 식별자·판본·의무·승인 봉인을 생산하고 저장한다."""
    from support.engine_lifecycle import _ended_execution, research_grant
    from support.observation_inputs import prepared_rule_conditions
    engine = sim.engine
    eid = sim.ports.clock.new_id('EX')
    _ended_execution(engine, eid, 'research_preparation')
    wire = candidate(title, revises=revises, refs=inputs)
    if obligations is not None:
        wire['completion_obligations'] = deepcopy(obligations)
    if question is not None:
        wire['question'] = question
    wire['profile_refs'] = deepcopy(engine.instance['role_profile_refs']['research_work'] if profiles is None else profiles)
    wire['authority_refs'] = [research_grant(engine)]
    execution = engine.runtime['executions'][eid]
    execution.update(input_snapshot=engine.head,
                     extensions={'model_assessments': [{'task_title': title, 'difficulty': 'low',
                         'importance': 'low', 'reason': '유한한 과제'}],
                         'task_conditions': [{**prepared_rule_conditions([title])[0], 'task_title': title}]})
    execution['extensions']['task_conditions'][0].pop('task_id', None)
    if revision_targets:
        execution['extensions']['task_conditions'][0]['knowledge_revision_targets'] = list(revision_targets)
    engine._apply_model_metadata({'role': 'research_preparation'}, {'candidates': [wire]}, eid)
    issue_preparation(sim, execution)
    engine._apply({'role': 'research_preparation'}, {'candidates': [wire]}, eid, owns_response=False)
    task = next(row for row in engine.runtime['tasks'].values() if row['title'] == title)
    reviewer = sim.ports.clock.new_id('EX')
    _ended_execution(engine, reviewer, 'task_contract_review')
    engine._apply({'role': 'task_contract_review', 'target': task['id']},
                  review_items([task['id']]), reviewer, owns_response=False)
    identifier = task['id']
    engine._save()
    return identifier

def issue_preparation(sim, execution):
    """정본 입력 생산자가 고정 문맥·prompt·manifest를 같은 묶음으로 봉인한다."""
    from pathlib import Path
    from do_math.context_store import prepare_role_input
    engine = sim.engine
    action = {'id': 'AC-' + execution['id'], 'role': 'research_preparation'}
    workspace = Path(engine.instance['workspace']) / 'runs' / execution['id'] / 'workspace'
    workspace.mkdir(parents=True, exist_ok=True)
    context = engine._context(action, workspace, execution_id=execution['id'])
    profile = next(p for p in engine.instance['execution_profiles'].values()
                   if p['role'] == action['role'])
    bundle = 'BA-' + execution['id']
    fitted = prepare_role_input(context, instance=sim.instance, runtime=sim.runtime,
        role=action['role'], profile=profile, snapshot=engine.head, workspace=workspace,
        activity_id=execution['owner_activity_id'], output_schema=engine._response_schema(action),
        documents=engine._documents[action['role']], artifact_prefix='runtime/artifacts/' + bundle,
        install_submission_tools=True, max_artifact_bytes=sim.instance['config']['max_artifact_bytes'],
        clock=sim.ports.clock)
    execution.update(input_bundle=bundle, input_manifest=deepcopy(fitted['manifest']))
    engine._save(engine._input_artifacts(bundle, engine._response_schema(action), fitted, workspace))

def _build_relation(root, shared):
    from do_math.knowledge_io import import_relation
    from support.engine_lifecycle import theorems, clear_work
    from support.sim import Sim
    sim = Sim.activated(root, shared=shared)
    clear_work(sim)
    kid, = theorems(sim, 'planning_endpoint')
    produce_task(sim)
    item = sim.instance['knowledge'][kid]
    aid = next(row['id'] for row in sim.instance['identity_assessments'].values()
               if row.get('formal_result_id') == item['formal_result_id'] and row.get('decision') == 'match')
    sim.engine.instance, _ = import_relation(sim.instance, {'kind': 'supports', 'source': kid, 'target': kid,
        'evidence': '동일한 항등식의 검증 근거', 'evidence_refs': [sim.instance_id],
        'formal_result_refs': [item['formal_result_id']], 'assessment_refs': [aid]},
        source_ref=sim.instance_id, actor_ref=sim.instance_id, clock=sim.ports.clock)
    clear_work(sim)
    return sim

def relation_sim():
    from support.sim import built
    return built('planning-relation-inputs', _build_relation)

def delegated_revision(sim):
    """실제 준비 과제가 지식 개정을 위임받고 부모 수신자가 대기를 만든다."""
    from do_math import revisions
    from support.planning_owner import enqueue
    engine = sim.engine
    kid = sim.instance['relations'][-1]['source']
    parent = enqueue(engine, 'research_preparation', revision_targets=revisions.capture_targets(
        sim.instance, sim.runtime, [kid], required=True))
    tid = produce_task(sim, '위임 과제', revision_targets=[kid])
    task = sim.runtime['tasks'][tid]
    eid = task['producer_execution']
    engine.runtime['executions'][eid]['extensions']['revision_resolutions'] = [{
        'record_id': kid, 'disposition': 'delegated', 'task_title': task['title'], 'reason': '지식 개정을 위임한다.'}]
    engine._apply_revision_followup(parent, {'summary': '위임'}, eid)
    engine._remove_action(parent)
    engine._save()
    return parent['id'], tid, kid


def _build(root, shared):
    from support.sim import Sim
    from support.engine_lifecycle import clear_work
    sim = Sim.activated(root, shared=shared)
    clear_work(sim)
    produce_task(sim)
    clear_work(sim)
    return sim


def prepared_sim():
    from support.sim import built
    return built('planning-contract-inputs', _build)


def warm_prepared():
    prepared_sim()


def only_task(sim):
    return next(row for row in sim.runtime['tasks'].values() if row['title'] == '계획 과제')


def withdraw(sim, identifier):
    from do_math.task_scope import apply_task_dispositions
    from support.engine_lifecycle import _ended_execution
    engine = sim.engine
    eid = sim.ports.clock.new_id('EX')
    _ended_execution(engine, eid, 'research_plan')
    engine.instance, engine.runtime = apply_task_dispositions(engine.instance, engine.runtime,
        [{'task_id': identifier, 'disposition': 'withdraw', 'reason': '미수행 과제를 철회한다.'}],
        execution_id=eid, input_tasks=deepcopy(engine.runtime['tasks']), clock=sim.ports.clock)
    engine._save()


def _build_hold(root, shared):
    from do_math import revisions
    from support.engine_lifecycle import applied, clear_work
    from support.planning_owner import enqueue
    sim = _build(root, shared)
    applied(sim, 'configure', config={'contract_revision_limit': 1})
    clear_work(sim)
    task = only_task(sim)
    enqueue(sim.engine, 'research_preparation', task['id'])
    revisions.record_repetition(sim.instance, sim.runtime, lineage='contract_revision', lineage_id=task['id'],
        event_ref=task['producer_execution'], outcome='authored', owner='ai', reason='첫 계약 생산',
        version=task['revision'], clock=sim.ports.clock)
    sim.engine._save()
    return sim


def held_sim():
    from support.sim import built
    return built('planning-repetition-held', _build_hold)


def continuation_input(sim):
    from do_math import revisions
    task = only_task(sim)
    hold = revisions.repetition_hold(sim.runtime, 'contract_revision', task['id'])
    action = next(a for a in sim.runtime['queue'] if a['role'] == 'research_preparation')
    return {'kind': 'repetition_continue', 'decision_id': 'DC-planning-continue',
        'lineage': 'contract_revision', 'lineage_id': task['id'], 'hold_event_ref': hold['event_ref'],
        'allowed_action': revisions.action_scope(action), 'baseline_revision': task['revision']}


def warm_held():
    held_sim()


def _build_empty_hold(root, shared):
    from support.sim import Sim
    from support.default_responder import DefaultResponder
    from support.engine_lifecycle import clear_work
    sim = Sim(root, shared=shared, config={'exhaustion_empty_limit': 1})
    sim.activate()
    clear_work(sim)
    sim.model.responder = DefaultResponder(preparation_candidates=[])
    sim.engine._enqueue('research_preparation', reason='빈 준비의 실제 제출과 보류')
    sim.engine._save()
    sim.run_until(lambda s: any(r.get('kind') == 'repetition_hold' and r.get('lineage') == 'exhaustion_empty'
                               for r in s.runtime['history'])
                  and all(e['status'] == 'ended' for e in s.runtime['executions'].values()), max_steps=8)
    clear_work(sim)
    return sim


def empty_hold_sim():
    from support.sim import built
    return built('planning-empty-hold-inputs', _build_empty_hold)


def warm_empty_hold():
    empty_hold_sim()


def contract():
    wire = candidate('계획 계약')
    row = contracts.task_candidate_record(wire, task_id='TK-planning')
    row.pop('revises_task_id')
    row.update(status='planned', results=[], reviews=[], occurrence_condition={'op': 'always'})
    return row


def fulfilled(task):
    return {'task_id': task['id'], 'decision': 'completed', 'reason': '보고된 의무의 독립 판정',
            'item_dispositions': [{'obligation_id': row['id'], 'kind': 'fulfilled',
                                   'evidence_refs': ['EX-planning-work']}
                                  for row in task['completion_obligations']], 'unresolved': []}


def selected_plan(task):
    return {'dispositions': [disposition(task['id'])], 'task_assessments': [],
            'preparation_requests': [], 'goal_audit': False}


def returned(sim):
    """실제 작업 수신자가 결과를 붙인 뒤 평가 입력을 만든다."""
    from support.engine_lifecycle import _ended_execution
    from support.default_responder import common
    engine = sim.engine
    task = only_task(sim)
    _ended_execution(engine, 'EX-planning-work', 'research_work')
    engine._apply({'role': 'research_work', 'target': task['id']},
                  {**common('research_work'), 'outcome': 'submitted',
                   'report': '자연수의 덧셈 항등식을 확인했다.'}, 'EX-planning-work')
    _ended_execution(engine, 'EX-planning-plan', 'research_plan')
    engine._save()
    return fulfilled(only_task(sim))


def _build_transfer(root, shared):
    from support.sim import Sim
    from support.engine_lifecycle import applied, clear_work
    sim = Sim.activated(root, shared=shared)
    clear_work(sim)
    produce_task(sim)
    recipient = produce_task(sim, '받는 과제')
    returned(sim)
    task = only_task(sim)
    applied(sim, 'decision', config={'change': {'kind': 'task_scope',
        'task_id': task['id'], 'disposition': 'transfer', 'revision': task['revision'],
        'contract_sha256': planning.contract_hash(task), 'obligation_ids': ['OB-argument'],
        'target_task_id': recipient, 'reason': '사용자가 수신 과제로 의무를 옮긴다.'}})
    clear_work(sim)
    return sim


def transfer_sim():
    from support.sim import built
    return built('planning-transfer-inputs', _build_transfer)


def transfer_input(sim):
    task = only_task(sim)
    decision = next(row for row in sim.instance['decisions'].values()
                    if row.get('change', {}).get('kind') == 'task_scope')
    assessment = fulfilled(task)
    assessment.update(decision='closed', item_dispositions=[{
        'obligation_id': 'OB-argument', 'kind': 'transferred', 'evidence_refs': [],
        'authority_ref': decision['id'], 'target_task_id': decision['change']['target_task_id'],
        'target_obligation_id': 'OB-inherited'}])
    return assessment


def warm_transfer():
    from support.sim import warm_built
    warm_built('planning-transfer-inputs', _build_transfer)


def defer_revision(sim, identifiers, *, required=False):
    """정상 개정 처분 수신으로 revision_dependency 대기를 생산한다."""
    from do_math import revisions
    from support.engine_lifecycle import _ended_execution
    from support.planning_owner import enqueue
    engine = sim.engine
    action = enqueue(engine, 'research_preparation', revision_targets=revisions.capture_targets(
        engine.instance, engine.runtime, identifiers, required=required))
    eid = sim.ports.clock.new_id('EX')
    _ended_execution(engine, eid, 'research_preparation')
    engine.runtime['executions'][eid]['extensions'] = {'revision_resolutions': [
        {'record_id': identifier, 'disposition': 'deferred', 'reason': '추가 근거를 기다린다.'}
        for identifier in identifiers]}
    issues = revisions.submission_errors({'candidates': []}, engine.runtime['executions'][eid]['extensions'], {
        'action': action, 'tasks': list(engine.runtime['tasks'].values()),
        'knowledge_catalog': list(engine.instance['knowledge'].values())})
    if issues:
        raise AssertionError('정상 개정 보류 입력이 수신 계약을 어겼다: ' + repr(issues))
    engine._apply_revision_followup(action, {'summary': '개정 보류'}, eid)
    engine._remove_action(action)
    engine._save()
    return action['id']


def select(sim):
    from support.engine_lifecycle import _ended_execution
    engine = sim.engine
    task = only_task(sim)
    eid = sim.ports.clock.new_id('EX')
    _ended_execution(engine, eid, 'research_plan')
    engine._apply_task_plan(selected_plan(task), eid, deepcopy(engine.runtime['tasks']), [task['id']],
                           evaluation_context=engine._evaluation_context())
    action = next(a for a in engine.runtime['queue'] if a.get('target') == task['id'] and a['role'] == 'research_work')
    engine._save()
    return next(a for a in engine.runtime['queue'] if a['id'] == action['id'])


def warm_relation():
    from support.sim import warm_built
    warm_built('planning-relation-inputs', _build_relation)


def _build_specialist(root, shared):
    """소유 작업의 실제 Lean·동일성 수신 결과를 전문 판정 의무에 연결한다."""
    from datetime import timedelta
    from do_math.task_scope import apply_task_assessments
    from support.sim import Sim
    from support.model import Answer
    from support.engine_lifecycle import _ended_execution, clear_work, theorems
    from support.default_responder import common
    sim = Sim.activated(root, shared=shared)
    clear_work(sim)
    endpoint, = theorems(sim, 'planning_specialist_endpoint')
    obligation = candidate()['completion_obligations'][0]
    obligation['judges'] = ['identity_review']
    tid = produce_task(sim, obligations=[obligation])
    clear_work(sim)
    source = 'theorem planning_specialist : 1 = 1 := rfl'
    sim.lean.allow(source, ['planning_specialist'], signatures={'planning_specialist': 'planning_specialist : 1 = 1'},
        declaration_evidence={'planning_specialist': {'type': '1 = 1', 'value': None}}, axioms={'planning_specialist': []}, dependencies={'planning_specialist': {}})

    def wait_for_specialist(output, context):
        for assessment in output['task_assessments']:
            assessment['decision'] = 'incomplete'
            for row in assessment['item_dispositions']:
                row['kind'] = 'open'
        for row in output['dispositions']:
            row.update(kind='not_selected', reason='독립 전문 판정 수신을 기다린다.', next_owner='research_plan',
                revisit={'event_refs': [], 'at': (sim.ports.clock.wall() + timedelta(days=1)).isoformat()})
        output['goal_audit'] = False
        return output

    sim.model.on('research_plan').reply(Answer(wait_for_specialist))
    _ended_execution(sim.engine, 'EX-specialist-work', 'research_work')
    claim = {'kind': 'formally_implies', 'source': endpoint, 'target': endpoint,
             'confirmed_scope': 'One equals one'}
    sim.runtime['executions']['EX-specialist-work']['extensions'] = {'knowledge_metadata': [{
        'title': 'planning-specialist', 'relation_claim': claim}]}
    sim.engine._apply({'role': 'research_work', 'target': tid}, {**common('research_work'),
        'outcome': 'submitted', 'report': '항등식을 형식 증명하고 전문 판정을 요청한다.', 'knowledge': [{
            'kind': 'theorem', 'title': 'planning-specialist', 'statement': 'One equals one',
            'explanation': 'Reflexivity', 'summary': 'Reflexivity', 'lean_code': source,
            'declaration_names': ['planning_specialist'], 'dependencies': []}]}, 'EX-specialist-work')
    sim.engine._save()
    kid = next(k for k, row in sim.instance['knowledge'].items() if row['title'] == 'planning-specialist')

    def judged(scene):
        cid = scene.instance['knowledge'][kid].get('review_cycle_id')
        return bool(cid and scene.runtime['review_cycles'][cid]['status'] != 'working'
                    and all(e['status'] == 'ended' for e in scene.runtime['executions'].values()))

    sim.run_until(judged, max_steps=20)
    cid = sim.instance['knowledge'][kid]['review_cycle_id']
    if sim.runtime['review_cycles'][cid].get('decision') != 'match':
        raise AssertionError('전문 판정의 실제 동일성 주기가 일치로 끝나지 않았다.')
    aid = next(row['id'] for row in sim.instance['identity_assessments'].values()
               if row.get('review_cycle_id') == cid and row.get('decision') == 'match')
    clear_work(sim)
    _ended_execution(sim.engine, 'EX-specialist-plan', 'research_plan')
    assessment = fulfilled(only_task(sim))
    assessment['item_dispositions'][0]['evidence_refs'] = [aid]
    sim.engine.instance, sim.engine.runtime = apply_task_assessments(sim.instance, sim.runtime, [assessment],
        execution_id='EX-specialist-plan', input_tasks=deepcopy(sim.runtime['tasks']), clock=sim.ports.clock)
    from do_math.knowledge_io import import_relation
    sim.engine.instance, _ = import_relation(sim.instance, {**claim, 'evidence': '독립 판정을 마친 자기 함의',
        'formal_result_refs': [sim.instance['knowledge'][kid]['formal_result_id']], 'assessment_refs': [aid]},
        source_ref='EX-specialist-work', actor_ref='EX-specialist-work', clock=sim.ports.clock)
    sim.engine._save()
    return sim


def specialist_sim():
    from support.sim import built
    return built('planning-specialist-inputs', _build_specialist)


def warm_specialist():
    from support.sim import warm_built
    warm_built('planning-specialist-inputs', _build_specialist)
