"""Actual event/control/bundle producers and cold, installed-contract readers.

Only external ports are doubles. Snapshots are whole validated publications;
no stored row is extended to satisfy a receiving field.
"""
from copy import deepcopy
import hashlib
import json

from contracts.pairs import Pair
from do_math.repository import ResearchRepository
from do_math.state_contract import validate_record
from support.storage_authority_pairs import _named_fields
from support.state_builders import installed_contract

FAMILIES = ('events', 'pending_events', 'event_cursor', 'control_receipts', 'integrations')


def digest(value):
    return hashlib.sha256((json.dumps(value, ensure_ascii=False, sort_keys=True,
        indent=2, allow_nan=False) + '\n').encode('utf-8')).hexdigest()


def reader(engine):
    return ResearchRepository(engine.store.repository, engine.instance['id'], contract=installed_contract(),
        backend=engine.ports.git_backend, clock=engine.ports.clock)


def keep(engine, samples, branch, *, previous=None):
    """First load on a new contract decodes blobs, never the writer's cached view."""
    cold = reader(engine)
    head, instance, runtime = cold.load(engine.head)
    # Core may have staged an unrelated execution.integration_result after its
    # bundle CAS. Compare the five published families, never claim that staged
    # bookkeeping has already been saved.
    if head != engine.head or any((family in runtime) != (family in engine.runtime)
            or runtime.get(family) != engine.runtime.get(family) for family in FAMILIES):
        raise AssertionError('publication differs from owner: ' + branch)
    if previous is not None and cold.load(previous[0]) != previous:
        raise AssertionError('old head changed: ' + branch)
    samples.append((branch, deepcopy(runtime)))
    return runtime


def family_pair(contract, family, samples):
    definition = contract.family('runtime', family)
    atom = family in {'pending_events', 'event_cursor'}

    def rows(runtime):
        if family not in runtime:
            return []
        value = runtime[family]
        return [value] if atom else list(value.values()) if definition.shape == 'map' else value

    def receive(runtime):
        for value in rows(runtime):
            validate_record(definition.checker, value, 'runtime/' + family)
            if definition.validator:
                definition.validator(value)

    return Pair('runtime.' + family, lambda root: samples, receive,
        frozenset({'/value'} if atom else _named_fields(definition.schema)),
        lambda runtime: {'/value'} if atom and rows(runtime) else _named_fields(definition.schema, rows(runtime)))


def lifecycle_samples(root):
    from do_math import planning
    from support.engine_lifecycle import applied, clear_work, task
    from support.governance_sim import adopt_audit, goal_auditor
    from support.sim import Sim

    sim, samples = Sim.activated(root), []
    engine = sim.engine
    keep(engine, samples, 'activation')
    clear_work(sim)
    planning.schedule_reconsideration(engine.instance, engine.runtime,
        now=sim.clock.now(), clock=sim.clock, evaluation_context=engine._evaluation_context())
    engine._save()
    keep(engine, samples, 'exhaustion')
    row = task(engine, 'TK-event-input')
    row['newinput'] = 'RQ-exact-input'
    engine.runtime['next_research_reconsider_at'] = sim.clock.now()
    expected = deepcopy(planning.collect_due_events(engine.instance, engine.runtime, sim.clock.now()))
    planning.record_due_events(engine.instance, engine.runtime, sim.clock.now())
    pending = list(engine.runtime['pending_events'])
    engine._save()
    saved = keep(engine, samples, 'due input and periodic')
    if saved['pending_events'] != pending or any(
            {k: v for k, v in event.items() if k != 'event_seq'} != source
            for source in expected for event in saved['events'] if event['id'] == source['id']):
        raise AssertionError('publication changed due cause or consumed pending references')
    engine._refresh_readiness()
    # A reviewed task becomes unready when its actual input is absent.
    engine.runtime['tasks'][row['id']]['inputs'] = ['source:missing-event-input']
    engine._refresh_readiness()
    engine._save()
    keep(engine, samples, 'readiness lost')
    adopt_audit(sim)
    action, output = goal_auditor(engine)
    output.pop('findings')  # Current goal-auditor response no longer declares this slot.
    engine._apply_governance_goal_audit(action, output, 'AUDITOR')
    engine._save()
    keep(engine, samples, 'goal audit not established')
    applied(sim, 'conversation', config={'operation': 'attach', 'id': 'event-lease',
        'generation': 1, 'lease_seconds': 10, 'disconnect_policy': 'pause'})
    applied(sim, 'conversation', config={'operation': 'detach', 'id': 'event-lease', 'generation': 1})
    keep(engine, samples, 'conversation generation and loss')
    return sim, samples, expected


def control_samples():
    from support.engine_control import running_work
    from support.observation_inputs import observation_rule, self_check_response, write_checkpoint
    from support.provider_probes import ObservedCalls
    from support.sim import Sim
    from support.submission_scenes import lost_acknowledgment

    sim, samples, originals = Sim.activated(), [], []
    with running_work(sim, rules=[observation_rule()]) as call:
        engine = call.engine
        capture = lambda args: originals.append(deepcopy(args['request']))
        with ObservedCalls(publish=type(engine)._publish_control_request, capture={'publish': capture}):
            call.submit('safety_boundary', {'inflight_calls': False, 'call_ids': []}, 'RQ-event-boundary')
            call.receive()
            keep(engine, samples, 'accepted safety boundary')
            write_checkpoint(call.workspace, counters={'attempts': 2})
            call.observe({'type': 'tick'})
            obligation = next(row for row in call.tracker.obligations.values() if row['kind'] == 'self_check_due')
            call.self_check(obligation['id'], self_check_response(obligation))
            call.receive()
            keep(engine, samples, 'durable rejected self check')
            before = deepcopy((engine.head, engine.instance, engine.runtime))
            preview = call.draft(kind='submission_preview')
            call.receive()
            if call.receipt(preview['request_id'])['state'] != 'previewed' or (
                    engine.head, engine.instance, engine.runtime) != before:
                raise AssertionError('preview changed durable state')
            with lost_acknowledgment(sim) as lost:
                delivery = call.draft()
                call.receive()
            if not lost or call.receipt(delivery['request_id'])['state'] != 'accepted':
                raise AssertionError('lost CAS acknowledgment lost durable acceptance')
            keep(engine, samples, 'submission after lost acknowledgment', previous=before)
        for request in originals:
            stored = next((r for r in engine.runtime['control_receipts'].values()
                if r['request_id'] == request['request_id']), None)
            if stored is None:  # preview is a response, never a stored receipt
                continue
            safe = {k: v for k, v in request.items() if k != 'capability'}
            if stored['request'] != safe or stored['request_sha256'] != digest(safe):
                raise AssertionError('receipt did not preserve safe request bytes/content')
            before = deepcopy((engine.head, engine.instance, engine.runtime))
            engine._publish_control_request(request)
            conflict = deepcopy(request)
            conflict['payload']['unexpected'] = 'different e\u0301\r\n'
            answer = engine._publish_control_request(conflict)
            if answer != {'state': 'rejected', 'reason': 'request identity reused with different content'}:
                raise AssertionError('changed request was accepted')
            if (engine.head, engine.instance, engine.runtime) != before:
                raise AssertionError('redelivery reapplied a request')
    return sim, samples, originals


def bundle_samples():
    from support.submission_receiver import research
    scene, samples = research(), []
    engine = scene.engine
    before = engine.store.load(engine.head)
    output = deepcopy(scene.output)
    output['knowledge'][1]['kind'] = 'undefined_kind'
    result = engine._apply_submission_bundles(scene.action, output, {}, scene.execution_id, scene.context, [])
    if result['retry_bundle_ids'] != ['IN-B']:
        raise AssertionError('failed bundle was not returned independently')
    partial = keep(engine, samples, 'partial core bundle', previous=before)
    if set(partial['integrations']) - set(before[2].get('integrations', {})) != {'IN-A'} or 'IN-B' in partial['integrations']:
        raise AssertionError('failed bundle acquired a receipt')
    head, original = engine.head, deepcopy(partial['integrations']['IN-A'])
    replay = engine._apply_submission_bundles(scene.action, output, {}, scene.execution_id, scene.context, [])
    if replay['bundles'][0]['status'] != 'already_accepted' or engine.head != head:
        raise AssertionError('matching bundle replay applied twice')
    output['knowledge'][0]['statement'] += ' changed'
    conflict = engine._apply_submission_bundles(scene.action, output, {}, scene.execution_id, scene.context, [])
    if not any(r['rule_id'] == 'integration.id_reuse' for r in conflict['issues']):
        raise AssertionError('changed bundle payload reused receipt identity')
    result = engine._apply_submission_bundles(scene.action, scene.output, {}, scene.execution_id, scene.context, [])
    if result['status'] != 'accepted' or engine.runtime['integrations']['IN-A'] != original:
        raise AssertionError('repair changed original accepted bundle')
    keep(engine, samples, 'repaired core bundle', previous=before)
    # Collection without central capture is a different actual event writer.
    # Its check artifacts and unsealed event are published before disposition.
    from do_math.execution_lifecycle import transition_execution
    transition_execution(engine.runtime['executions'][scene.execution_id], 'stopping', at=scene.sim.clock.now())
    engine._receive_submission(scene.action, {'output': scene.output}, scene.execution_id,
        scene.context, scene.schema, scene.workspace)
    engine._save()
    keep(engine, samples, 'unsealed core collection', previous=before)
    return scene, samples


def external_samples():
    from support.engine_lifecycle import external_sim, applied, http_grant, run_machine
    sim, samples = external_sim(), []
    config = http_grant(sim.engine)
    sim.engine._save()
    applied(sim, 'external', config=config)
    sim.ports.http.table['/effect'] = (503, b'unknown outcome', None)
    run_machine(sim, 'external_action')
    operation = sim.runtime['external_operations'][config['id']]
    evidence = {'evidence_ref': 'remote-effect-log', 'operation_id': operation['id'],
        'request_sha256': operation['request_sha256'], 'idempotency_key': operation['idempotency_key'],
        'fact': 'effect_absent', 'observed_at': sim.clock.now()}
    applied(sim, 'external', config={'operation': 'reconcile', 'id': operation['id'],
        'result': 'failed', 'evidence': evidence})
    applied(sim, 'external', config={'operation': 'retry', 'id': operation['id'], 'grant_id': config['grant_id']})
    sim.ports.http.table['/effect'] = (201, b'confirmed', None)
    run_machine(sim, 'external_action')
    keep(sim.engine, samples, 'external reconcile retry confirmed')
    return sim, samples, evidence


def trust_samples():
    from support.engine_lifecycle import (lifecycle_sim, transition, prepared_environment,
        only, applied, run_machine)
    sim, samples = lifecycle_sim(), []
    tid = transition(sim, prepared_environment(sim))
    only(sim, 'trust_check', 'trust_activate')
    spawn, requests = sim.lean.spawn, []

    def pause(command, **options):
        if not requests:
            requests.append(sim.control('pause', text='pause exact trust event sample'))
        return spawn(command, **options)

    sim.lean.spawn = pause
    try:
        sim.engine._save()
        sim.step()
    finally:
        sim.lean.spawn = spawn
    keep(sim.engine, samples, 'stopped trust target')
    applied(sim, 'resume')
    run_machine(sim, 'trust_check')
    keep(sim.engine, samples, 'checked trust target')
    return sim, samples, tid
