"""Real relation, approved task, input seal and delegated revision producers."""
from copy import deepcopy
from support.role_answers import candidate, review_items


def produce_task(sim, title='계획 과제', *, revises=None, inputs=(), revision_targets=(), obligations=None):
    """수신자가 식별자·판본·의무·승인 봉인을 생산하고 저장한다."""
    from support.engine_lifecycle import _ended_execution, research_grant
    from support.observation_inputs import prepared_rule_conditions
    engine = sim.engine
    eid = sim.ports.clock.new_id('EX')
    _ended_execution(engine, eid, 'research_preparation')
    wire = candidate(title, revises=revises, refs=inputs)
    if obligations is not None:
        wire['completion_obligations'] = deepcopy(obligations)
    wire['profile_refs'] = deepcopy(engine.instance['role_profile_refs']['research_work'])
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
