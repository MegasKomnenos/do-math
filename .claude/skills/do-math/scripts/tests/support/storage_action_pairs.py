"""Action producers and their validated publications, with cold contract readers.

The preparation scene is shared with the existing release/settlement test.
These samples are complete states; callers must distinguish fields actually
seen here from the larger shared action schema's field obligation.
"""
from copy import deepcopy

from contracts.pairs import Pair
from do_math.repository import ResearchRepository
from do_math.state_contract import validate_record
from support.state_builders import installed_contract
from support.storage_authority_pairs import _named_fields


def reader(engine):
    return ResearchRepository(engine.store.repository, engine.store._store.instance_id,
        contract=installed_contract(), backend=engine.ports.git_backend, clock=engine.ports.clock)


def keep(engine, samples, branch, *, previous=None):
    # A different contract object bypasses Repository._read_key's publication
    # cache. This reader's first load must decode the actual published blobs.
    cold = reader(engine)
    loaded = cold.load(engine.head)
    if loaded != (engine.head, engine.instance, engine.runtime):
        raise AssertionError('cold action decode differs from producer: ' + branch)
    if previous is not None and cold.load(previous[0]) != previous:
        raise AssertionError('previous action head changed: ' + branch)
    samples.append((branch, deepcopy(loaded[1:])))
    return loaded


def actions(state):
    """All actual receivers of the common action shape, not just live queue rows."""
    runtime = state[1]
    return [*runtime.get('queue', []),
        *(row['action'] for row in runtime.get('executions', {}).values() if 'action' in row),
        *(row['action'] for row in runtime.get('waiting_actions', {}).values()),
        *(row['action'] for row in runtime.get('input_overflows', [])),
        *(row['authority_request'] for cycle in runtime.get('review_cycles', {}).values()
          for row in cycle.get('replacement_actions', {}).values() if 'authority_request' in row)]


def action_pair(contract, samples):
    family = contract.family('runtime', 'queue')

    def receive(state):
        for action in actions(state):
            validate_record(family.checker, action, 'runtime/queue')
            if family.validator:
                family.validator(action)

    return Pair('shared stored action', lambda root: samples, receive,
        frozenset(_named_fields(family.schema)), lambda state: _named_fields(family.schema, actions(state)))


def waiting_pair(contract, samples):
    family = contract.family('runtime', 'waiting_actions')
    # action has its own shared Pair. The remaining row is a separate obligation.
    schema = deepcopy(family.schema['additionalProperties'])
    del schema['properties']['action']

    def receive(state):
        validate_record(family.checker, state[1].get('waiting_actions', {}), 'runtime/waiting_actions')

    return Pair('stored waiting row', lambda root: samples, receive, frozenset(_named_fields(schema)),
        lambda state: _named_fields(schema, list(state[1].get('waiting_actions', {}).values())))


class StoredActions:
    """Let existing execution scenes keep their content assertions and cold-read full states."""
    def __init__(self, case):
        self.case, self.samples = case, []

    def read(self, engine, branch, *, identifiers=None, head=None):
        loaded = reader(engine).load(head or engine.head)
        self.samples.append((branch, deepcopy(loaded[1:])))
        rows = loaded[2]['executions']
        return rows if identifiers is None else {key: rows[key] for key in identifiers}


def question_samples(samples):
    """Actual question binding and revision exception producers, at their storage seam."""
    from do_math import questions
    from support.engine_lifecycle import _ended_execution, clear_work, task
    from support.role_answers import review_items
    from support.sim import Sim
    sim = Sim.activated()
    clear_work(sim)
    engine = sim.engine
    row = task(engine, 'TK-storage-question', approved=False)
    _ended_execution(engine, 'EX-storage-question-report', 'research_work')
    linked = questions.link(engine.runtime, execution_id='EX-storage-question-report', field='output/questions/0',
        owner='operations', targets=[row['id']], blocks=True, obligation={'kind': 'input_retrieval',
            'subject_ref': row['id'], 'requirement_ref': 'support'}, clock=engine.ports.clock)
    engine.runtime['executions']['EX-storage-question-report']['output'] = {'questions': ['Retrieve the exact support input']}
    engine._reconcile_question_actions()
    engine._save()
    keep(engine, samples.samples, 'question has a real pending handler')
    _ended_execution(engine, 'EX-storage-question-review', 'task_contract_review')
    engine._apply({'role': 'task_contract_review', 'target': row['id']},
        review_items([row['id']], decision='revision_required', findings=['Check this contract input']),
        'EX-storage-question-review', owns_response=False)
    preparation = next(a for a in engine.runtime['queue'] if a['role'] == 'research_preparation')
    _ended_execution(engine, 'EX-storage-deferred', 'research_preparation')
    engine.runtime['executions']['EX-storage-deferred']['extensions'] = {'revision_resolutions': [{
        'record_id': row['id'], 'disposition': 'deferred', 'question_ids': ['output:questions/0'], 'reason': 'Wait for the user scope question'}],
        'question_routes': [{'question_index': 0, 'owner': 'user', 'target_ids': [row['id']],
            'reason': 'The original scope belongs to its user owner'}]}
    deferred_output = {'questions': ['Which exact original scope may be changed?']}
    deferred_ref = 'runtime/artifacts/BA-storage-deferred/output.json'
    from do_math.canonical import canonical_json
    engine._record_output_questions(preparation, deferred_output, 'EX-storage-deferred', source_ref=deferred_ref)
    engine._apply_revision_followup(preparation, {'summary': 'Keep the exact request while waiting'}, 'EX-storage-deferred')
    engine._remove_action(preparation)
    engine._save({deferred_ref: canonical_json(deferred_output)})
    user_question = next(q for q in engine.runtime['question_links'] if q['owner'] == 'user')
    samples.case.assertEqual(engine.runtime['waiting_actions'][preparation['id']]['deferrals'][row['id']]['question_ids'],
                             [user_question['id']])
    keep(engine, samples.samples, 'deferred revision retains its actual question')
    _ended_execution(engine, 'EX-storage-dismissal', 'research_preparation')
    resolution = {'record_id': row['id'], 'disposition': 'dismissed', 'request_refs': ['EX-storage-question-review'],
        'evidence_refs': [row['id']], 'reason': 'The supplied contract already covers this responsibility'}
    engine.runtime['executions']['EX-storage-dismissal']['extensions'] = {'revision_resolutions': [resolution]}
    engine._apply_revision_followup(preparation, {'summary': 'Dismiss the disproved AI request'}, 'EX-storage-dismissal')
    engine._save()
    keep(engine, samples.samples, 'dismissal creates a separate independent reconsideration')


def impact_samples(samples):
    """A real returned work bundle and the independent unresolved impact verdict."""
    from do_math import submission
    from support.review_sim import held_impact, impact_review_answer, impact_sim, observations
    case = samples.case
    sim = impact_sim()
    engine = sim.engine
    waiting, producer, identifier, request = held_impact(sim)
    original = submission.read_sealed_submission(producer, engine.head, engine.store.read,
        git_dir=engine.store.git_dir)['output']
    case.assertEqual(request['producer_execution_id'], producer['id'])
    case.assertEqual(request['input_snapshot'], producer['input_snapshot'])
    case.assertEqual(request['integration_id'], identifier)
    ids = observations(sim)
    case.assertIn(ids['B'], {kid for plan in request['plans'].values() for kid in plan['declared_impact']})
    action, = [a for a in engine.runtime['queue'] if a.get('stage') == 'impact_review']
    case.assertEqual(action['input_basis'], {'impact_review': request})
    keep(engine, samples.samples, 'impact owner holds original bundle')
    scope = next(iter(request['plans']))
    sim.model.on('maintenance', stage='impact_review').reply(impact_review_answer({scope: 'unresolved'}))
    sim.step()
    entry = engine.runtime['waiting_actions'][waiting['action']['id']]
    review, = [e for e in engine.runtime['executions'].values()
        if e.get('action', {}).get('stage') == 'impact_review']
    case.assertEqual(entry['review_execution_ids'], {identifier: review['id']})
    case.assertEqual(entry['kind'], 'impact_review_blocked')
    case.assertEqual(entry['next_owner'], 'research_preparation')
    case.assertEqual(submission.read_sealed_submission(engine.runtime['executions'][producer['id']],
        engine.head, engine.store.read, git_dir=engine.store.git_dir)['output'], original)
    keep(engine, samples.samples, 'independent impact verdict preserves held content')


def revision_samples(samples):
    """Actual revision owners produce delegation, deferral and detached history."""
    from do_math import revisions
    from support.engine_lifecycle import _ended_execution
    from support.planning_owner import enqueue, owner_sim, theorem_id
    case = samples.case
    sim = owner_sim()
    engine = sim.engine
    kid, tid = theorem_id(sim), 'TK-1'
    parent = enqueue(engine, 'research_preparation', revision_targets=revisions.capture_targets(
        sim.instance, sim.runtime, [kid, tid], required=True))
    task = engine.runtime['tasks'][tid]
    task.update(title='Correct source', producer_execution='EX-storage-prep', knowledge_revision_targets=[kid])
    _ended_execution(engine, 'EX-storage-prep', 'research_preparation')
    engine.runtime['executions']['EX-storage-prep']['extensions'] = {'revision_resolutions': [
        {'record_id': kid, 'disposition': 'delegated', 'task_title': task['title'], 'reason': 'Research exact correction'},
        {'record_id': tid, 'disposition': 'deferred', 'reason': 'Original task evidence e\u0301\r\n'}]}
    engine._apply_revision_followup(parent, {'summary': 'Delegate and wait'}, 'EX-storage-prep')
    engine._remove_action(parent)
    engine._save()
    entry = engine.runtime['waiting_actions'][parent['id']]
    case.assertEqual(entry['delegated_targets'], {kid: tid})
    case.assertEqual(entry['reason'], 'Research exact correction; Original task evidence e\u0301\r\n')
    keep(engine, samples.samples, 'revision delegated and deferred by owner')
    work = enqueue(engine, 'research_work', tid)
    case.assertEqual(work['revision_request_action_id'], parent['id'])
    engine._save()
    keep(engine, samples.samples, 'delegated work retains the requesting revision owner')
    engine._remove_action(work)
    child = enqueue(engine, 'research_preparation', revision_targets=revisions.capture_targets(
        sim.instance, sim.runtime, [tid]))
    case.assertEqual(child['revision_parent_ids'], [parent['id']])
    engine._save()
    keep(engine, samples.samples, 'revision child binds the retained parent')
    _ended_execution(engine, 'EX-storage-child', 'research_preparation')
    engine.runtime['executions']['EX-storage-child']['extensions'] = {'revision_resolutions': [
        {'record_id': tid, 'disposition': 'deferred', 'reason': 'Still missing e\u0301\r\n'}]}
    engine._apply_revision_followup(child, {'summary': 'Keep original obligation'}, 'EX-storage-child')
    engine._remove_action(child)
    engine._save()
    case.assertEqual(engine.runtime['waiting_actions'][parent['id']]['deferrals'], {
        tid: {'execution_id': 'EX-storage-child', 'reason': 'Still missing e\u0301\r\n'}})
    keep(engine, samples.samples, 'child records deferral on original owner')
    engine.runtime['tasks'][tid]['status'] = 'closed'
    engine._reconcile_revision_delegations()
    engine._save()
    expected = [{'record_id': kid, 'task_id': tid}]
    case.assertEqual(engine.runtime['waiting_actions'][parent['id']]['delegation_history'], expected)
    followup, = [a for a in engine.runtime['queue'] if a.get('revision_followup')]
    case.assertEqual(followup['revision_followup'], expected)
    keep(engine, samples.samples, 'detached delegation retains original revision')


def judgment_samples(samples):
    from do_math import planning, revisions
    from do_math.execution_lifecycle import begin_preparation, end_preparation
    from support.engine_lifecycle import _ended_execution
    from support.planning_contract_inputs import prepared_sim, only_task, produce_task
    from support.planning_owner import enqueue
    from support.role_answers import review_items
    case = samples.case
    sim = prepared_sim()
    engine, tid = sim.engine, only_task(sim)['id']
    _ended_execution(engine, 'EX-storage-rejected-contract', 'task_contract_review')
    output = review_items([tid], decision='revision_required', next_owner='research_preparation',
                        findings=['Explain the boundary e\u0301\r\n'])
    engine._apply({'role': 'task_contract_review', 'target': tid}, output,
                  'EX-storage-rejected-contract', owns_response=False)
    revision, = [a for a in engine.runtime['queue'] if a.get('contract_review_execution')]
    case.assertEqual(revision['contract_review_execution'], 'EX-storage-rejected-contract')
    first = deepcopy(revision['revision_targets'][tid])
    engine._save()
    keep(engine, samples.samples, 'contract reviewer returns the exact revision obligation')
    produce_task(sim, 'Revised contract', revises=tid)
    engine._enqueue('research_preparation', tid, contract_review_execution='EX-storage-rejected-contract',
        reason='Reconsider the newly authored contract',
        revision_targets=revisions.capture_targets(sim.instance, sim.runtime, [tid]))
    merged = next(a for a in engine.runtime['queue'] if a['id'] == revision['id'])
    case.assertEqual(merged['superseded_revision_bases'], [{tid: first}])
    engine._save()
    keep(engine, samples.samples, 'merging actual contract editions preserves the old basis')
    engine.runtime['queue'] = []
    target = 'EX-storage-rejected-contract'
    action = enqueue(engine, 'operational_review', target, reason='Inspect the retained failure')
    changes = [{'field': 'contract_sha256', 'before': first['contract_sha256'],
                'after': planning.contract_hash(engine.runtime['tasks'][tid])}]
    for index in range(2):
        execution = engine._register_execution(action, {'id': 'EX-storage-refresh-' + str(index),
            'role': action['role']})
        begin_preparation(execution, at=sim.clock.now())
        end_preparation(execution, at=sim.clock.now(), stage='context', reason='Changed decision premises', cancelled=False)
        engine._refresh_changed_decision(action, execution['id'], changes)
        engine._save()
        if index == 0:
            action, = engine.runtime['queue']
            case.assertEqual(action['refresh'], {'execution_id': execution['id'], 'attempt': 1, 'changes': changes})
            keep(engine, samples.samples, 'one refresh retains the actual changed premises')
    wait = engine.runtime['waiting_actions'][action['id']]
    case.assertEqual((wait['owner'], wait['next_owner'], wait['release_condition']),
                     ('ai', 'operations', 'new consistent decision input'))
    case.assertEqual(wait['changes'], changes)
    keep(engine, samples.samples, 'repeated currentness conflict waits for operations')
    engine._enqueue('task_contract_review', tid)
    engine._enqueue('research_plan')
    plan = next(a for a in engine.runtime['queue'] if a['role'] == 'research_plan')
    case.assertTrue(engine._plan_settle_waits(plan))
    case.assertEqual(plan['settle_started_at'], sim.clock.now())
    case.assertEqual(plan['dispatch_wait']['kind'], 'plan_settle')
    engine._save()
    keep(engine, samples.samples, 'one planner settles the pending contract judgments')


def repetition_samples(samples):
    from do_math import revisions
    from support.scheduling_recovery import failed_plan_sim, failed_execution
    case = samples.case
    sim = failed_plan_sim()
    failed = failed_execution(sim)
    revisions.record_execution_outcome(sim.instance, sim.runtime, failed['action'], {}, failed['id'],
        accepted=False, clock=sim.clock)
    sim.engine._save()
    diagnostic, = [a for a in sim.runtime['queue'] if a.get('repetition_lineage')]
    case.assertEqual(diagnostic['repetition_lineage'],
        ['selection_failure', failed['action']['repetition_bases']['selection_failure']])
    case.assertEqual(diagnostic['receipt_refs'], [failed['id']])
    case.assertEqual(diagnostic['target'], failed['id'])
    keep(sim.engine, samples.samples, 'actual rejected plan writes its diagnostic tuple lineage')


def observation_samples(samples):
    from support.engine_control import running_work
    from support.observation_inputs import observation_rule, self_check_response, write_checkpoint
    from support.sim import Sim
    case = samples.case
    sim = Sim.activated()
    with running_work(sim, rules=[observation_rule()]) as call:
        engine = sim.engine
        write_checkpoint(call.workspace, counters={'attempts': 2}, claim='Independent checkpoint e\u0301\r\n')
        call.observe({'type': 'tick'})
        obligation, = call.tracker.obligations.values()
        response = self_check_response(obligation, status='indeterminate', evidence=[])
        call.self_check(obligation['id'], response)
        call.receive()
        engine._save()
        actions = [a for a in engine.runtime['queue'] if a.get('obligation_ids')]
        case.assertTrue(actions)
        for action in actions:
            case.assertEqual(action['obligation_ids'], [obligation['id']])
            case.assertEqual(action['target'], call.execution_id)
            for ref in action['observation_refs']:
                case.assertIn(ref, engine.runtime['self_check_responses'] | engine.runtime.get('self_check_obligations', {}))
        keep(engine, samples.samples, 'actual checkpoint obligation and response request review')
        call.finish({'status': 'stopped', 'error': None, 'output': None, 'usage': {}})
        wait = engine.runtime['waiting_actions'][call.execution['action']['id']]
        case.assertIsNone(wait['reason'])
        case.assertEqual(wait['execution_id'], call.execution_id)
        case.assertEqual(wait['input_snapshot'], call.execution['input_snapshot'])
        keep(engine, samples.samples, 'stopped execution preserves a null runner reason and exact input')


def review_research_samples(samples):
    from support.review_research import research_sim, InvestigationResponder
    case = samples.case
    sim = research_sim()
    sim.model.responder = InvestigationResponder()
    sim.run_until(lambda s: any(a['role'] == 'supplemental_research' for a in s.runtime['queue']), max_steps=8)
    engine = sim.engine
    action, = [a for a in engine.runtime['queue'] if a['role'] == 'supplemental_research']
    cycle = engine.runtime['review_cycles'][action['owner_review_cycle_id']]
    request = cycle['research'][action['research_request_id']]
    case.assertEqual(action['review_cycle_id'], cycle['id'])
    case.assertEqual(action['requesting_slot'], request['action']['slot'])
    case.assertTrue(action['research_request_id'].startswith(request['requested_by'] + ':'))
    keep(engine, samples.samples, 'real review requests its fixed-source investigation')
    sim.run_until(lambda s: any(c.get('decision') == 'match' for c in s.runtime['review_cycles'].values()), max_steps=12)
    followup, = [a for a in engine.runtime['queue'] if a.get('identity_review')]
    case.assertEqual(followup['identity_review']['knowledge_id'], action['target'])
    keep(engine, samples.samples, 'finished review publishes its exact planning consequence')


def other_owner_samples(samples):
    from support.academic_resolution_cases import rejection_case
    from support.engine_lifecycle import applied, task
    from support.planning_owner import owner_sim, theorem_id
    from support.governance_cases import question_sim
    from support.storage_execution_pairs import stored_kind_input, assert_stored_provider_failure
    from do_math import planning
    case = samples.case
    stored_kind_input(samples)
    assert_stored_provider_failure(samples)
    sim = question_sim()
    wait, = [w for w in sim.runtime['waiting_actions'].values() if w['kind'] == 'import_user_decision']
    case.assertEqual(sim.runtime['intent_imports'][wait['import_id']]['input_ref'], wait['action']['target'])
    keep(sim.engine, samples.samples, 'checked interpretation retains its blocking question owner')
    sim, _, _ = rejection_case(actor='Reviewer e\u0301', text='Exact external rejection\r\n')
    rejection = sim.runtime['external_rejections'][-1]
    action = next(a for a in sim.runtime['queue'] if a.get('rejection_id'))
    case.assertEqual(action['rejection_id'], rejection['id'])
    keep(sim.engine, samples.samples, 'external rejection retains the original review request')
    sim = owner_sim()
    engine, kid = sim.engine, theorem_id(sim)
    applied(sim, 'knowledge', request_id='UC-storage-withdrawal', config={'operation': 'invalidate',
        'id': kid, 'reason': 'Exact evidence withdrawal e\u0301\r\n'})
    action, = [a for a in engine.runtime['queue'] if a.get('knowledge_id') == kid]
    case.assertEqual((action['knowledge_id'], action['source_ref']), (kid, 'UC-storage-withdrawal'))
    keep(engine, samples.samples, 'public knowledge control preserves its original source')
    task(engine, 'TK-storage-transfer', approved=False)
    engine._save()
    donor = engine.runtime['tasks']['TK-1']
    applied(sim, 'decision', request_id='UC-storage-scope', config={'change': {'kind': 'task_scope',
        'task_id': donor['id'], 'disposition': 'transfer', 'revision': donor['revision'],
        'contract_sha256': planning.contract_hash(donor), 'obligation_ids': ['OB-scope'],
        'target_task_id': 'TK-storage-transfer', 'reason': 'Transfer only the explicit scope'}})
    action, = [a for a in engine.runtime['queue'] if a.get('scope_decision_id')]
    case.assertEqual(engine.instance['decisions'][action['scope_decision_id']]['source_ref'], 'UC-storage-scope')
    keep(engine, samples.samples, 'public scope decision requests its independent planner')


def work_overflow_samples(samples):
    """A real large contract overflows one allowed profile and offers the other."""
    from support.engine_overflow import apply_limit
    from support.engine_lifecycle import clear_work
    from support.planning_contract_inputs import produce_task
    from support.planning_owner import enqueue
    from support.sim import Sim
    case = samples.case
    sim = Sim.activated()
    engine = sim.engine
    large = [deepcopy(ref) for ref in sim.instance['role_profile_refs']['research_work']
        if sim.instance['execution_profiles'][ref['id']]['ai']['tier'] == 'high']
    apply_limit(sim, 500000, 'UC-storage-small-work')
    small = [deepcopy(ref) for ref in sim.instance['role_profile_refs']['research_work']
        if sim.instance['execution_profiles'][ref['id']]['ai']['tier'] == 'low']
    clear_work(sim)
    question = 'Preserve this independent task question e\u0301\r\n' * 14000
    tid = produce_task(sim, 'Exact large task', question=question, profiles=[*small, *large])
    clear_work(sim)
    action = enqueue(engine, 'research_work', tid, profile_ref=small[0])
    engine._save()
    engine._prepare_call(action)
    wait = engine.runtime['waiting_actions'][action['id']]
    case.assertEqual(wait['kind'], 'input_overflow')
    case.assertEqual(wait['next_owner'], 'research_plan', wait['detail'])
    request, = [a for a in engine.runtime['queue'] if a.get('input_overflow')]
    detail = wait['detail']
    case.assertEqual(request['input_overflow'], detail)
    case.assertEqual(request['overflow_activity_id'], wait['action']['owner_activity_id'])
    case.assertEqual(engine.runtime['tasks'][tid]['question'], question)
    case.assertEqual(detail['cause'], 'required_role_input')
    case.assertTrue(detail['allowed_profile_candidates'])
    case.assertEqual(detail['limit_bytes'], 500000)
    case.assertGreater(detail['mandatory_bytes'], detail['context_budget_bytes'])
    case.assertEqual(detail['prompt_metrics']['prompt_bytes'], detail['packed_bytes'])
    engine._save()
    keep(engine, samples.samples, 'actual work overflow offers the allowed larger profile')
    from support.provider_probes import ObservedCalls
    rejected = deepcopy(engine.runtime)
    next(a for a in rejected['queue'] if a.get('input_overflow'))['input_overflow']['without_restored_dialogue_bytes'] = 0
    head = engine.head
    with ObservedCalls(write=engine.ports.git_backend.write_object) as writes:
        with case.assertRaisesRegex(ValueError,
                "Additional properties are not allowed \\('without_restored_dialogue_bytes' was unexpected\\)"):
            engine.store.save_with_state(head, engine.instance, rejected)
        case.assertEqual(writes.count('write'), 0)
    case.assertEqual(engine.store.resolve_snapshot(None), head)


def formal_failure_samples(samples):
    from support.scheduling_machine import formal_scene
    case = samples.case
    sim, action, _ = formal_scene()
    sim.runtime['queue'] = [action]
    sim.lean.inputs.clear()  # The compiler port has no accepted facts for this input.
    sim.engine._save()
    sim.step()
    followup, = [a for a in sim.runtime['queue'] if a.get('formal_target')]
    case.assertEqual(followup['formal_target'], action['target'])
    keep(sim.engine, samples.samples, 'failed compiler result retains its exact formal target')


def control_and_due_samples(samples):
    """Public requests and actual due events supply independent request provenance."""
    from do_math import planning
    from support.engine_lifecycle import applied, clear_work
    from support.sim import Sim
    case = samples.case
    sim = Sim.activated()
    engine = sim.engine
    clear_work(sim)
    eid = next(e['id'] for e in engine.runtime['executions'].values() if e['status'] == 'ended')
    applied(sim, 'request', text='Exact cleanup e\u0301\r\n', request_id='UC-storage-cleanup',
        config={'role': 'maintenance', 'cleanup_execution_ids': [eid]})
    action, = [a for a in engine.runtime['queue'] if a.get('requested_by') == 'UC-storage-cleanup']
    case.assertEqual(action['cleanup_execution_ids'], [eid])
    case.assertEqual(action['reason'], 'Exact cleanup e\u0301\r\n')
    request = next(row['request'] for row in engine.runtime['history']
        if row.get('request', {}).get('id') == 'UC-storage-cleanup')
    case.assertEqual(request['config']['cleanup_execution_ids'], action['cleanup_execution_ids'])
    keep(engine, samples.samples, 'public control preserves its cleanup scope')
    engine.runtime['queue'] = []
    engine.runtime['pending_events'] = []
    engine.runtime['next_research_reconsider_at'] = sim.clock.now()
    due = planning.record_due_events(sim.instance, sim.runtime, sim.clock.now())
    periodic, = [row for row in due if row['kind'] == 'research_reconsider_due']
    engine._schedule_reconsideration(sim.clock.now())
    engine._refresh_readiness()
    engine._save()
    preparation, = [a for a in engine.runtime['queue'] if a['role'] == 'research_preparation']
    case.assertIn(periodic['id'], preparation['event_refs'])
    case.assertIs(preparation['periodic_reconsideration'], True)
    case.assertEqual(preparation['exhaustion_event_ref'], next(row['id'] for row in engine.runtime['events']
        if row['kind'] == 'research_exhausted'))
    keep(engine, samples.samples, 'due event opens one preserved preparation')


def recovery_samples(samples):
    """Real review-input loss and public replacement; no waiting record is seeded."""
    from support.governance_delegation import public_replacement_case
    case = samples.case
    sim, request = public_replacement_case()
    engine = sim.engine
    held, = [row for row in engine.runtime['waiting_actions'].values()
        if row['kind'] == 'review_input_restoration' and row['action']['stage'] == 'initial']
    action = held['action']
    cycle = engine.runtime['review_cycles'][action['review_cycle_id']]
    case.assertEqual(held['detail']['review_cycle_id'], cycle['id'])
    case.assertEqual(held['detail']['action']['slot'], action['slot'])
    case.assertEqual(held['next_owner'], 'governance')
    keep(engine, samples.samples, 'actual review input loss and replacement history')


def overflow_samples(samples):
    from support.engine_overflow import overflowed_sim, held, retry
    case = samples.case
    sim = overflowed_sim()
    engine = sim.engine
    aid, wait = held(sim)
    original = deepcopy(wait)
    case.assertEqual(wait['action']['requested_by'], 'UC-maintenance')
    case.assertEqual(wait['detail']['role'], 'maintenance')
    case.assertEqual(wait['detail']['limit_bytes'], 1)
    overflow_action = engine.runtime['input_overflows'][-1]['action']
    attempt = next(e for e in engine.runtime['executions'].values()
        if e.get('action', {}).get('id') == aid)
    case.assertEqual(wait['action'], {**overflow_action, 'continuation_of': attempt['id']})
    keep(engine, samples.samples, 'actual packed input overflow')
    retry(sim, aid, 'UC-storage-overflow-retry')
    action, = [a for a in engine.runtime['queue'] if a['id'] == aid]
    case.assertEqual(action['input_overflow_retry']['request_id'], 'UC-storage-overflow-retry')
    case.assertEqual(action['owner_activity_id'], original['action']['owner_activity_id'])
    keep(engine, samples.samples, 'public retry preserves the overflow owner')


def diagnosis_samples(samples, *, allow_retry=False):
    from do_math import submission
    from support.model import amend, raw
    from support.scheduling_initial import adopted_sim, GRANT
    case = samples.case
    sim = adopted_sim()
    engine = sim.engine
    guidance = 'Original diagnosis e\u0301\r\nneeds an explicit correction'
    sim.model.on('intent_interpretation', stage='interpret').reply(
        raw({'not': 'an interpretation'}, expected_receipt='rejected'))
    sim.model.on('maintenance').reply(amend(initial_submission_diagnosis={'decision': 'wait', 'guidance': guidance}))
    sim.run_until(lambda s: any(w.get('diagnosis') for w in s.runtime.get('waiting_actions', {}).values()), max_steps=8)
    wait, = [w for w in engine.runtime['waiting_actions'].values() if w.get('diagnosis')]
    diagnosis = engine.runtime['executions'][wait['diagnosis']['execution_id']]
    output = submission.read_sealed_submission(diagnosis, engine.head, engine.store.read,
        git_dir=engine.store.git_dir)['output']
    case.assertEqual(output['initial_submission_diagnosis'], {'decision': 'wait', 'guidance': guidance})
    case.assertEqual(wait['reason'], guidance)
    case.assertEqual(wait['next_owner'], 'maintenance')
    case.assertEqual(diagnosis['action']['target'], wait['execution_id'])
    keep(engine, samples.samples, 'initial owner stores actual diagnosis guidance')
    # The layer-2 diagnosis producer receives a retry choice, but its owner
    # cannot continue after the current initial grant is revoked.
    engine.apply_initial_diagnosis(diagnosis['action'], {'initial_submission_diagnosis': {
        'decision': 'retry', 'guidance': 'Retry the preserved exact input'}}, diagnosis['id'])
    if not allow_retry:
        engine.instance['grants'][GRANT]['status'] = 'revoked'
    engine.continue_initial_retries()
    if allow_retry:
        retry, = engine.runtime['queue']
        case.assertEqual(retry['diagnosis_attempt'], 1)
        case.assertEqual(retry['continuation_of'], wait['execution_id'])
        keep(engine, samples.samples, 'actual initial retry preserves the bounded diagnosis')
        return
    wait = engine.runtime['waiting_actions'][wait['action']['id']]
    case.assertEqual(wait['diagnosis']['retry_error'], 'initial operating authority: no current grant permits this action')
    keep(engine, samples.samples, 'revoked initial authority preserves retry error')


def diagnosed_retry_samples(samples):
    diagnosis_samples(samples, allow_retry=True)


def intent_samples(samples):
    from support.engine_lifecycle import clear_work
    from support.model import amend
    from support.sim import Sim
    case = samples.case
    sim = Sim.activated()
    clear_work(sim)
    sim.model.on('intent_interpretation', stage='check').reply(
        amend(decision='revision_required', scope_complete=False, findings=['Missing second clause e\u0301\r\n']))
    sim.control('input', text='Keep the original purpose e\u0301\r\n', request_id='UC-storage-intent')
    sim.run_until(lambda s: any(a.get('intent_repair') for a in s.runtime['queue']), max_steps=12)
    engine = sim.engine
    rework, = [a for a in engine.runtime['queue'] if a.get('intent_repair')]
    check = engine.runtime['executions'][rework['intent_repair']['check_execution_id']]
    case.assertEqual(check['action']['stage'], 'check')
    case.assertEqual(rework['intent_repair']['findings'], ['Missing second clause e\u0301\r\n'])
    case.assertEqual(rework['previous_import_id'], rework['intent_repair']['import_id'])
    keep(engine, samples.samples, 'actual input interpretation check requests bounded rework')
    intent_evidence_samples(samples)


def intent_evidence_samples(samples):
    if getattr(samples, '_intent_evidence_collected', False):
        return
    samples._intent_evidence_collected = True
    from support.intent_evidence import waiting_sim, evidence_waits
    sim = waiting_sim(evidence_ref='source:intent-check-source.txt')
    wait, = evidence_waits(sim)
    bundle = deepcopy(sim.runtime['intent_imports'][wait['import_id']])
    samples.read(sim.engine, 'intent check waits for actual question evidence')
    sim.restart()
    sim.run_until(lambda s: any(a.get('import_check_release') for a in s.runtime['queue']), max_steps=4)
    samples.read(sim.engine, 'released intent check retains its exact evidence authorization')
    sim.run_until(lambda s: s.runtime['intent_imports'][bundle['id']].get('application', {}).get('status') == 'applied'
        and all(e['status'] == 'ended' for e in s.runtime['executions'].values()), max_steps=4)
    samples.read(sim.engine, 'independent recheck preserves old and current seals')
    received = sim.runtime['intent_imports'][bundle['id']]
    samples.case.assertEqual(received['check_history'], [bundle['check']])
    samples.case.assertEqual(received['sha256'], bundle['sha256'])
    return sim, bundle


def preparation_case(kind, *, source=None):
    """Actual call/planning owner writes one of the four preparation waits."""
    from do_math import execution_profiles
    from do_math.model_policy import assessment_basis
    from do_math.observations import OPERATORS
    from support.observation_inputs import observation_rule
    from support.planning_contract_inputs import prepared_sim, only_task
    from support.planning_owner import enqueue
    from support.academic_scenes import rule_prepared, ended
    from support.default_responder import rating
    from support.scheduling_parallel import ready_work_sim

    if kind == 'observation_rules':
        sim = ready_work_sim(1)
        action = deepcopy(sim.runtime['queue'][0])
        rule = observation_rule('iteration_gte', OPERATORS['iteration_gte']['subject_kind'], '$execution')
        rule['subject']['id'] = 'EX-previous'
        sim.runtime.setdefault('task_observation_rules', {})[action['target']] = [rule]
        sim.engine._save()
        sim.engine._prepare_call(action)
        return sim, action, None
    if kind == 'observation_configuration':
        sim = prepared_sim()
        normal = deepcopy(sim.instance['config'])
        invalid = deepcopy(normal)
        del invalid['tool_review_window_seconds']
        execution_profiles.apply_editions(sim.instance, execution_profiles.build_profiles(invalid, host=sim.ports.host))
        action = enqueue(sim.engine, 'task_contract_review', only_task(sim)['id'])
        sim.engine._prepare_call(action)
        return sim, action, normal
    sim = rule_prepared() if kind == 'observation_rule_input' else prepared_sim()
    engine = sim.engine
    if source is not None:
        from do_math.control_contracts import normalized_source
        sim.control('source', config=normalized_source('assessment-evidence.txt', source),
                    request_id='UC-storage-assessment-source')
        engine.process_controls()
    if kind == 'observation_rule_input':
        for task in sim.runtime['tasks'].values():
            task['model_assessment'] = {key: value for key, value in rating(task_id=task['id']).items() if key != 'task_id'}
        sim.runtime['queue'] = []
        engine._ensure_model_assessments()
        action = next(row for row in sim.runtime['queue'] if row.get('observation_rule_targets'))
        extensions = {'observation_rule_deferrals': [{'task_id': identifier, 'reason': 'Missing source',
            'missing_inputs': ['user_input'], 'next_owner': 'user'}
            for identifier in action['observation_rule_targets']]}
    else:
        task = only_task(sim)
        task.pop('model_assessment', None)
        action = enqueue(engine, 'research_preparation', assessment_targets={task['id']: assessment_basis(task)})
        extensions = {'model_assessment_deferrals': [{'task_id': task['id'], 'reason': 'Missing assessment input'}]}
    ended(engine, 'EX-prep-deferred', 'research_preparation')
    engine.runtime['executions']['EX-prep-deferred'].update(action=action, extensions=extensions)
    engine._apply_model_metadata(action, {'candidates': []}, 'EX-prep-deferred')
    engine._finish_assessment_preparation(action, 'EX-prep-deferred')
    engine._remove_action(action)
    return sim, action, None


def assert_merge_samples(samples):
    """The existing merge assertions, shared with the whole stored action Pair."""
    from support.sim import Sim
    import json
    case = samples.case
    sim = Sim.activated()
    engine = sim.engine
    engine.runtime['queue'] = []
    events = [event['id'] for event in engine.runtime['events'][:2]]
    case.assertEqual(len(events), 2)
    fields = ('receipt_refs', 'obligation_ids', 'observation_refs', 'evidence_refs')
    first_refs = {key: [key + ':one', key + ':shared'] for key in fields}
    other_refs = {key: [key + ':shared', key + ':two', key + ':one'] for key in fields}
    engine._enqueue('research_plan', reason='First e\u0301\r\n', requested_by='UC-one',
                    event_refs=[events[0]], observation={'sequence': 1}, **first_refs)
    first = deepcopy(engine.runtime['queue'][0])
    engine._enqueue('research_plan', id='AC-second-input', reason='Second\n', requested_by='UC-two',
                    event_refs=[events[1], events[0]], observation={'sequence': 2}, **other_refs)
    engine._enqueue('research_plan', id='AC-second-input', reason='First e\u0301\r\n', requested_by='UC-one',
                    event_refs=[events[0]], observation={'sequence': 3})
    merged, = engine.runtime['queue']
    case.assertEqual((merged['id'], merged['lineage_id']), (first['id'], first['lineage_id']))
    case.assertEqual(merged['reasons'], ['First e\u0301\r\n', 'Second\n'])
    case.assertEqual(merged['reason'], 'First e\u0301\r\n\nSecond\n')
    case.assertEqual((merged['requested_by'], merged['requested_by_refs']), ('UC-one', ['UC-one', 'UC-two']))
    case.assertEqual(merged['event_refs'], events)
    case.assertEqual(merged['merged_action_ids'], ['AC-second-input'])
    case.assertEqual(merged['observation'], {'sequence': 3})
    case.assertIs(merged['unbound_request'], True)
    for key in fields:
        case.assertEqual(merged[key], [key + ':one', key + ':shared', key + ':two'])
    # An incompatible trigger-specific judgment must survive independently.
    engine._enqueue('research_plan', formal_target='K-first')
    engine._enqueue('research_plan', formal_target='K-other')
    case.assertEqual([a.get('formal_target') for a in engine.runtime['queue']], ['K-first', 'K-other'])
    expected = deepcopy(engine.runtime['queue'])
    states = []
    engine._save()
    old = keep(engine, states, 'merged ordered requests')
    engine._remove_action(expected[0])
    engine._save()
    current = keep(engine, states, 'consumed only the selected request', previous=old)
    case.assertEqual(current[2]['queue'], expected[1:])
    manifest = json.loads(reader(engine).read('runtime/_state/manifest.json', current[0]))
    case.assertEqual(manifest['containers']['queue']['ids'], [expected[1]['id']])
    sim.restart()
    case.assertEqual(sim.runtime['queue'], expected[1:])
    samples.samples.extend(states)
