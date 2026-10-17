"""Real execution producers on the stored, publicly initialized profile inputs.

Git, clock, Jobs and scheduler are port fakes. Publication and receiving checks
are the installed Repository/StateContract; no output fields are filled in here.
"""
from copy import deepcopy
from dataclasses import dataclass, field
import hashlib
import json
from pathlib import Path

from contracts.pairs import Pair
from do_math import activities, execution_lifecycle as lifecycle
from do_math.execution_lifecycle import transition_execution
from do_math.session_slots import SessionSlots
from do_math.state_contract import default_state_contract
from support.fakes.clock import FakeClock
from support.storage_profile_pairs import family_receiver
from support.storage_records import engine_on, fake_ports, record_store


@dataclass
class ExecutionScene:
    store: object
    engine: object
    samples: list = field(default_factory=list)

    @property
    def slots(self):
        engine = self.engine
        return SessionSlots(engine.runtime, engine.instance, clock=engine.ports.clock,
                            jobs=engine.ports.jobs, host_id=engine.host_id)

    def publish(self, branch):
        self.engine._save()
        # A new Repository also exercises receiving, rather than only the
        # publishing Repository's cached validated view.
        reader = record_store(self.store.repository, backend=self.engine.ports.git_backend,
                              clock=self.engine.ports.clock)
        head, _, runtime = reader.load(self.engine.head)
        self.samples.append((branch, head, deepcopy(runtime)))
        return runtime


def execution_scene(root, case):
    # Cases share immutable stored profile inputs, not mutable port histories.
    ports = fake_ports(FakeClock(*case.inputs.ports.clock.state()), case.inputs.ports.git_backend)
    store = record_store(root / 'repository', backend=ports.git_backend, clock=ports.clock)
    engine, _ = engine_on(store, deepcopy(case.instance), deepcopy(case.runtime),
                          workspace=root / 'work', ports=ports)
    return ExecutionScene(store, engine)


def new_attempt(scene, reference, *, index, owner='AY-storage', continuation_of=None):
    """Create and attach, without admission or a native process."""
    engine = scene.engine
    profile = engine.instance['execution_profiles'][reference['id']]
    execution = lifecycle.create_execution(execution_id=f'EX-storage-{index}', owner_activity_id=owner,
        actor_kind=profile['actor_kind'], input_manifest=[], profile_ref=reference,
        created_at=engine.ports.clock.now(), continuation_of=continuation_of,
        context_origin=[continuation_of] if continuation_of else None)
    execution['role'] = profile['role']
    activities.assign_execution(engine.runtime, owner, execution)
    return execution


def stored_activity_samples(root, case):
    scene = execution_scene(root, case)
    engine, clock = scene.engine, scene.engine.ports.clock
    scene.publish('empty')
    activities.open_activity(engine.runtime, activity_id='AY-storage', activity_kind='maintenance',
        owner_ref={'kind': 'storage-example', 'text': 'e\u0301\r\n'}, input_refs=['IN-one', {'input': 'two'}],
        opened_at=clock.now(), stage='collect', execution_limit=2)
    scene.publish('ready')
    reference = engine.instance['role_profile_refs']['maintenance'][0]
    previous = None
    for index in range(2):
        execution = new_attempt(scene, reference, index=index, continuation_of=previous)
        lifecycle.begin_preparation(execution, at=clock.now())
        scene.publish(f'preparing-{index}')
        execution = engine.runtime['executions'][f'EX-storage-{index}']
        lifecycle.end_preparation(execution, at=clock.now(), stage='context',
            reason='Explicit synthetic input failure', cancelled=bool(index))
        previous = execution['id']
        scene.publish(f'ended-{index}')
    activities.wait_for(engine.runtime, 'AY-storage', kind='required_input', reason='Need exact input',
        condition={'input': 'e\u0301'}, next_owner='user', at=clock.now())
    scene.publish('waiting')
    activities.resume_activity(engine.runtime, 'AY-storage', condition={'input': 'e\u0301'}, at=clock.now())
    scene.publish('resumed')
    activities.finish_activity(engine.runtime, 'AY-storage', result_refs=['IN-one'],
        unresolved=[{'input': 'two'}], followups=['Ask user'], at=clock.now())
    scene.publish('finished')
    return scene


def stored_pair(family_name, snapshots):
    """Only closed object families use Pair's top-level field obligation.

    The open provider_wake has no named fields; its content needs assertions.
    Executions use the same required and optional field obligation.
    """
    family = default_state_contract().family('runtime', family_name)
    samples = [(branch, row) for branch, _, runtime in snapshots
               for row in runtime.get(family_name, {}).values()]
    return Pair(family_name, lambda root: samples, family_receiver(family),
                frozenset(family.schema['properties']))


class StoredExecutions:
    """Collect only published rows, through a new receiving Repository per head.

    Scenes own their independent content assertions. This is just the existing
    Pair's sample transport, not a second field registry or coverage algorithm.
    """
    def __init__(self, case):
        self.case, self.snapshots = case, []

    def read(self, engine, branch, *, identifiers=None, head=None):
        reader = record_store(engine.store.repository, instance_id=engine.instance['id'],
                              backend=engine.ports.git_backend, clock=engine.ports.clock)
        head, _, runtime = reader.load(head or engine.head)
        if identifiers is not None:
            runtime = {**runtime, 'executions': {key: runtime['executions'][key] for key in identifiers}}
        self.snapshots.append((branch, head, deepcopy(runtime)))
        return runtime['executions']


def stored_execution_inputs(samples):
    """Preparation writes the hashes/bases/rules; no execution fields are supplied."""
    from do_math import academic
    from do_math.canonical import exact_content_hash
    from support.academic_scenes import consumer_sim, MANUSCRIPT
    from support.governance_cases import records_sim

    case = samples.case
    sim = consumer_sim()
    engine = sim.engine
    # The approved user requirement is independent of the prepared execution.
    expected_requirements = exact_content_hash({'items': [{**MANUSCRIPT, 'required_inputs': [], 'external_effects': []}]})
    case.assertEqual(academic.current_requirements(sim.instance)['sha256'], expected_requirements)
    # The generated task needs its real assessment preparation before a
    # contract reviewer may receive it (revision_waits enforces that input).
    sim.run_until(lambda s: any(a['role'] == 'task_contract_review' and a.get('target') in s.runtime['tasks']
                  for a in s.runtime['queue']), max_steps=8)
    task = deepcopy(next(t for t in sim.runtime['tasks'].values() if t.get('academic_requirement_id')))
    action = {'id': 'AC-stored-academic', 'role': 'task_contract_review', 'target': task['id']}
    prepared = engine._prepare_call(action)
    case.assertIsInstance(prepared, dict)
    eid = prepared['execution_id']
    row = samples.read(engine, 'academic-input', identifiers=[eid])[eid]
    case.assertEqual(row['academic_requirements_sha256'], expected_requirements)
    engine._session_slots().release(eid)
    # A plan on the same genuinely solved state captures its current solution.
    expected_basis = deepcopy(task['solution_basis'])
    case.assertTrue(expected_basis)
    plan = engine._prepare_call({'id': 'AC-stored-plan', 'role': 'research_plan'})
    case.assertIsInstance(plan, dict)
    row = samples.read(engine, 'solution-input', identifiers=[plan['execution_id']])[plan['execution_id']]
    case.assertEqual(row['input_solution_basis'], expected_basis)
    case.assertTrue(expected_basis['records'])

    sim = records_sim()
    engine = sim.engine
    action = {'id': 'AC-stored-audit', 'role': 'goal_audit', 'basis': engine._goal_basis_key(),
              'required': 2, 'slot': 0}
    # Read the independently approved audit and its source records before preparation.
    audit = deepcopy(sim.instance['governance']['AU-close'])
    required = {ref: deepcopy(sim.instance['governance'][ref]) for ref in audit['content']['required_inputs']}
    expected_audits = [{'audit': audit, 'audit_sha256': exact_content_hash(audit), 'inputs': required,
                        'input_hashes': {ref: exact_content_hash(value) for ref, value in required.items()}}]
    case.assertTrue(expected_audits)
    prepared = engine._prepare_call(action)
    eid = prepared['execution_id']
    row = samples.read(engine, 'additional-audit-input', identifiers=[eid])[eid]
    case.assertEqual(row['additional_audit_input'], expected_audits)
    case.assertEqual(row['additional_audit_input'][0]['audit']['id'], audit['id'])



def assert_stored_delegation_input(samples):
    from do_math.canonical import exact_content_hash
    from support.execution_inputs import delegated_judgment_scene
    case = samples.case
    sim, judges, shared = delegated_judgment_scene()
    engine = sim.engine
    action = deepcopy(judges[0])
    application = sim.runtime['delegation_applications'][action['delegation_application_id']]
    expected_hash = exact_content_hash(application['basis'])
    case.assertEqual(application['input_sha256'], expected_hash)
    # Initial and research grants both authorize this interpreter; this input
    # deliberately selects the adopted research grant rather than asking the
    # authority checker to choose between two valid user grants.
    action['grant_id'] = sim.instance['lifecycle']['adoption']['research_grant_ids'][0]
    prepared = engine._prepare_call(action)
    case.assertIsInstance(prepared, dict)
    eid = prepared['execution_id']
    row = samples.read(engine, 'delegation-input', identifiers=[eid])[eid]
    case.assertEqual(row['delegation_input_sha256'], expected_hash)
    case.assertEqual(prepared['context']['delegation_case']['basis'], application['basis'])


def stored_kind_input(samples):
    from support.sim import Sim
    from support.engine_lifecycle import clear_work, _ended_execution
    case = samples.case
    sim = Sim.activated()
    engine = sim.engine
    clear_work(sim)
    proposal = {'family': 'knowledge', 'token': 'method_note', 'meaning': 'A nonmathematical method observation',
                'constraints': {'mathematical_claim': False}}
    _ended_execution(engine, 'EX-kind-author', 'research_work')
    engine.runtime['executions']['EX-kind-author']['extensions'] = {'kind_definitions': [proposal]}
    engine._apply_extensions({'role': 'research_work'}, 'EX-kind-author')
    definition = next(row for row in engine.instance['kind_definitions'].values() if row['token'] == proposal['token'])
    action, = [a for a in engine.runtime['queue'] if a.get('kind_definition_id') == definition['id']]
    from do_math.canonical import exact_content_hash
    expected = {'kind_definition': {'id': definition['id'], 'sha256': exact_content_hash(definition)}}
    engine._save()
    prepared = engine._prepare_call(action)
    case.assertIsInstance(prepared, dict)
    eid = prepared['execution_id']
    row = samples.read(engine, 'kind-input', identifiers=[eid])[eid]
    case.assertEqual(row['input_basis'], expected)
    case.assertEqual(prepared['context']['kind_definition_to_check']['meaning'], proposal['meaning'])


def stored_provider_returns(samples):
    """Explicit native bytes -> parser -> runner -> owner -> validated storage."""
    from dataclasses import replace
    import json
    from pathlib import Path
    from support.sim import Sim
    from support.provider_runs import ProviderJobs, ScriptedCLI, CLAUDE_INIT, claude_result, model_runner
    case = samples.case
    usage = {'input_tokens': 13, 'output_tokens': 3, 'cache_creation_input_tokens': .25}
    model_usage = {'claude-opus-5': {'inputTokens': 13, 'costUSD': .125}}
    scopes = {'usage': 'sum_of_reported_segment_counters',
              'model_usage_reported': 'last_reported_cumulative_model_usage',
              'total_cost_usd': 'last_reported_estimate_not_invoice'}
    for locked in (False, True):
        sim = Sim.activated()
        sim._apply('configure', config={'tier_models': {t: 'claude-opus-5' for t in ('low', 'medium', 'high')},
            'session_limits': {'work': {'claude-opus-5': 3}}, 'claude_only_assigned_model': locked})
        engine = sim.engine
        events = [CLAUDE_INIT, claude_result(b'{}', usage=usage, modelUsage=model_usage, total_cost_usd=.125)]
        raw = b''.join(json.dumps(event, ensure_ascii=False).encode() + b'\n' for event in events)
        jobs = ProviderJobs(ScriptedCLI(stdout=raw), clock=sim.clock)
        engine.ports = replace(engine.ports, jobs=jobs)
        steps = engine._call_steps({'id': 'AC-usage', 'role': 'maintenance'})
        arguments = next(steps)
        result = model_runner(sim.root, jobs, sim.clock).run(**arguments)
        case.assertEqual(result['usage_segments'], [{'segment': 0, 'line': 2, 'usage': usage}])
        engine._local_call_returned(arguments['execution_id'], result)
        try:
            steps.send(result)
        except StopIteration:
            pass
        eid = arguments['execution_id']
        row = samples.read(engine, 'native-usage-' + str(locked), identifiers=[eid])[eid]
        case.assertEqual(row['usage_segments'], [{'segment': 0, 'line': 2,
            'usage': {'input_tokens': 13, 'output_tokens': 3,
                      'cache_creation_input_tokens': {'reported_decimal': '0.25'}}}])
        case.assertEqual(row['model_usage_reported'], {'claude-opus-5': {
            'inputTokens': 13, 'costUSD': {'reported_decimal': '0.125'}}})
        case.assertEqual(row['usage_scope'], scopes)
        case.assertEqual(row['reported_models'], ['claude-opus-5'])
        case.assertEqual(Path(arguments['evidence_dir'], 'stdout.jsonl').read_bytes(), raw)
        source, = [value for value in engine.runtime['checkpoints'][eid]['observation_sources']
                   if value['path'] == 'stdout.jsonl']
        case.assertEqual(engine.store.read(source['artifact_ref'], engine.head), raw)
        case.assertEqual((source['bytes'], source['sha256']), (len(raw), hashlib.sha256(raw).hexdigest()))
        report = json.loads(row['provider_observation']['reported_fields_json'])
        case.assertEqual(report['model_usage_reported'], model_usage)



def assert_stored_provider_failure(samples, *, unconfirmed=False):
    from dataclasses import replace
    from support.sim import Sim
    from support.provider_runs import ProviderJobs, ScriptedCLI, CLAUDE_INIT, claude_result, model_runner
    case = samples.case
    # The returned failure is an execution value; the provider gate is a
    # separate consumer and cannot stand in for this assertion.
    sim = Sim.activated()
    sim._apply('configure', config={'tier_models': {t: 'claude-opus-5' for t in ('low', 'medium', 'high')},
                                  'session_limits': {'work': {'claude-opus-5': 3}}})
    engine = sim.engine
    info = {'status': 'rejected', 'rateLimitType': 'five_hour', 'detail': 'Exact e\u0301\r\n', 'utilization': .75}
    events = [{'type': 'rate_limit_event', 'rate_limit_info': info}, CLAUDE_INIT,
              claude_result(b'{}', subtype='error_during_execution', is_error=True)]
    raw = b''.join(json.dumps(event, ensure_ascii=False).encode() + b'\n' for event in events)
    jobs = ProviderJobs(ScriptedCLI(stdout=raw), clock=sim.clock)
    engine.ports = replace(engine.ports, jobs=jobs)
    steps = engine._call_steps({'id': 'AC-limited', 'role': 'maintenance'})
    arguments = next(steps)
    old_head = engine.head
    old = deepcopy(engine.store.load(old_head))
    reservations = deepcopy(engine.runtime['reservations'])
    result = model_runner(sim.root, jobs, sim.clock).run(**arguments)
    engine._local_call_returned(arguments['execution_id'], result)
    expected = {'kind': 'provider_limit', 'provider': 'claude', 'retry_at': None,
        'limit_windows': [{'type': 'five_hour', 'resetsAt': None}], 'evidence_line': 1,
        'native_info': info, 'observed_at': sim.clock.now(),
        'evidence_ref': str(Path(arguments['evidence_dir']) / 'stdout.jsonl')}
    case.assertEqual(result['failure'], expected)
    if unconfirmed:
        jobs.empty[arguments['launch_ticket']['job_name']] = None
    try:
        steps.send(result)
    except StopIteration:
        pass
    eid = arguments['execution_id']
    row = samples.read(engine, 'provider-limit', identifiers=[eid])[eid]
    expected['native_info'] = {**info, 'utilization': {'reported_decimal': '0.75'}}
    case.assertEqual(row['failure'], expected)
    case.assertEqual(row['error_kind'], 'provider_limit')
    case.assertEqual(row['status'], 'stopping' if unconfirmed else 'ended')
    if unconfirmed:
        case.assertEqual(row['capacity']['local_termination'], 'unknown')
        case.assertEqual(engine.runtime['reservations'], reservations)
        case.assertEqual(json.loads(engine.store.read(row['result_ref'], engine.head))['failure'], expected)
    case.assertEqual(Path(arguments['evidence_dir'], 'stdout.jsonl').read_bytes(), raw)
    case.assertEqual(engine.store.load(old_head), old)


def stored_observation_and_stop(samples):
    import hashlib
    import json
    from support.engine_control import running_work
    from support.observation_inputs import observation_rule
    from support.sim import Sim
    case = samples.case
    sim = Sim.activated()
    rule = observation_rule('checkpoint_count_gte', 'checkpoint', '$execution', threshold=2)
    with running_work(sim, rules=[rule]) as call:
        eid, engine = call.execution_id, call.engine
        row = samples.read(engine, 'bound-rules', identifiers=[eid])[eid]
        bound = {**rule, 'subject': {'kind': 'checkpoint', 'id': eid}}
        case.assertEqual(row['observation_rules'], [bound])
        case.assertEqual(call.tracker.rules, [bound])
        for events, count in (([], 0), ([{'type': 'turn.started'}], 1),
                              ([{'type': 'fixture', 'text': 'e\u0301\r\n'}, {'type': 'turn.completed'}], 3)):
            call.observe(*events)
            row = samples.read(engine, 'fact-sequence-' + str(count), identifiers=[eid])[eid]
            case.assertEqual(row['observation_fact_sequence'], count)
            facts = [fact for fact in engine.runtime['observation_facts'].values() if fact['execution_id'] == eid]
            case.assertEqual(len(facts), count)
            for fact in facts:
                case.assertEqual(hashlib.sha256(fact['event_json'].encode()).hexdigest(), fact['event_sha256'])
        case.assertEqual([json.loads(f['event_json']) for f in facts],
                         [{'type': 'turn.started'}, {'type': 'fixture', 'text': 'e\u0301\r\n'}, {'type': 'turn.completed'}])
        call.submit('safety_boundary', {'inflight_calls': False, 'call_ids': []}, 'boundary-stored')
        call.receive()
        receipt = call.receipt('boundary-stored')
        case.assertEqual(receipt['state'], 'accepted')
        engine.runtime['executions'][eid]['stop_requested'] = 'first e\u0301\r\n'
        case.assertIs(call.arguments['should_stop'](), True)
        row = samples.read(engine, 'first-stop', identifiers=[eid])[eid]
        case.assertEqual(row['stop_reason'], 'first e\u0301\r\n')
        first_head, first = engine.head, deepcopy(row)
        sim.advance(1)
        engine.runtime['executions'][eid]['stop_requested'] = 'second request'
        engine.runtime['tasks'][call.execution['action']['target']]['question'] += ' Changed contract.'
        case.assertIs(call.arguments['should_stop'](), True)
        engine._save()
        row = samples.read(engine, 'later-stop', identifiers=[eid])[eid]
        case.assertEqual(row['stop_reason'], first['stop_reason'])
        case.assertEqual(row['stop_observed_at'], first['stop_observed_at'])
        case.assertTrue(row['currentness_changes'])
        case.assertEqual([t['to'] for t in row['transitions']].count('stopping'), 1)
        case.assertEqual(samples.read(engine, 'old-first-stop', identifiers=[eid], head=first_head)[eid], first)


def stored_operator_runner(samples):
    import json
    from pathlib import Path
    from do_math import scheduled_operator as operator
    from support.operator_finish_scene import Scene
    case = samples.case
    scene = Scene()
    expected = deepcopy(scene.answer())
    before = deepcopy(scene.load())
    result = scene.call(operator.recovery, failure={'kind': 'engine_unavailable', 'error': 'Exact e\u0301\r\n'})
    case.assertEqual(result['outcome'], 'repaired')
    # recovery owns its own Repository; refresh the engine's head for the reader.
    scene.sim.engine.head = result['snapshot']
    eid = result['execution_id']
    row = samples.read(scene.sim.engine, 'operator-runner', identifiers=[eid])[eid]
    case.assertEqual(row['runner'], {'status': 'completed',
        'evidence_ref': str(Path(result['run_directory']) / 'runner-result.json')})
    raw = json.loads(Path(row['runner']['evidence_ref']).read_bytes())
    case.assertEqual(raw['status'], 'completed')
    case.assertEqual(raw['output'], expected)
    case.assertEqual(row['output'], expected)
    case.assertEqual(scene.sim.engine.store.load(before[0]), before)


def stored_operational_dispositions(samples):
    """Real issued review input and application; independently chosen verdicts."""
    from support.engine_control import running_work
    from support.observation_inputs import write_checkpoint
    from support.sim import Sim
    case = samples.case
    for kind in ('continue', 'retry', 'resume'):
        sim = Sim.activated()
        with running_work(sim) as call:
            engine, eid = sim.engine, call.execution_id
            if kind == 'resume':
                write_checkpoint(call.workspace, claim='Exact resume e\u0301\r\n')
                call.observe()
            action = {'id': 'AC-review-' + kind, 'role': 'operational_review', 'target': eid, 'live': True}
            prepared = engine._prepare_call(action)
            case.assertIsInstance(prepared, dict)
            reviewer = prepared['execution_id']
            specific = ({'next_review': {'at': sim.clock.now(), 'reason': 'Review the next checkpoint'}}
                        if kind == 'continue' else {'scope': 'Same unfinished task'})
            if kind == 'retry':
                specific['replay_safety'] = 'No output or external effect was accepted'
            if kind == 'resume':
                specific['checkpoint_ref'] = engine.runtime['checkpoints'][eid]['artifact_ref']
            proposal = {'kind': kind, 'basis_refs': [eid], 'next_owner': 'engine',
                        'reason': 'Exact disposition e\u0301\r\n', **specific}
            output = {'summary': 'Independent operating decision', 'questions': [], 'used_sources': [],
                      'disposition': proposal}
            engine._apply(prepared['action'], deepcopy(output), reviewer)
            engine._save()
            rows = samples.read(engine, kind + '-applied', identifiers=[eid, reviewer])
            case.assertEqual(rows[reviewer]['output'], output)
            record, = [r for r in engine.runtime['operational_dispositions'].values() if r['execution_id'] == reviewer]
            case.assertEqual(record['disposition'], proposal)
            old_head, old_target = engine.head, deepcopy(rows[eid])
            if kind == 'continue':
                case.assertEqual(rows[eid]['operational_continuation'],
                                 {'disposition_id': record['id'], 'next_review': specific['next_review']})
                case.assertNotIn('pending_operational_disposition', rows[eid])
                continue
            case.assertEqual(rows[eid]['pending_operational_disposition'], record['id'])
            case.assertEqual(rows[eid]['stop_requested'], 'operational_' + kind)
            case.assertEqual(record['status'], 'awaiting_termination')
            # The actual stop observer records its first reason before the
            # external port confirms the Job ended and releases reservations.
            case.assertTrue(call.arguments['should_stop']())
            job = next(job for job in sim.jobs.launched if job.name == call.arguments['launch_ticket']['job_name'])
            job.terminate()
            engine._local_call_returned(eid, {'status': 'stopped'})
            target = engine.runtime['executions'][eid]
            case.assertTrue(lifecycle.release_or_hold(target, engine._session_slots(), at=sim.clock.now()))
            lifecycle.transition_execution(target, 'ended', at=sim.clock.now(), outcome='execution_incomplete')
            engine._complete_operational_disposition(engine.runtime['operational_dispositions'][record['id']])
            engine._save()
            rows = samples.read(engine, kind + '-completed', identifiers=[eid, reviewer])
            case.assertNotIn('pending_operational_disposition', rows[eid])
            retry, = [a for a in engine.runtime['queue'] if a.get('continuation_of') == eid]
            case.assertEqual(retry['owner_activity_id'], old_target['owner_activity_id'])
            before = deepcopy(engine.runtime)
            engine._complete_operational_disposition(engine.runtime['operational_dispositions'][record['id']])
            case.assertEqual(engine.runtime, before)
            case.assertEqual(samples.read(engine, kind + '-old-head', identifiers=[eid], head=old_head)[eid], old_target)


def stored_late_return(samples):
    from support.scheduling_parallel import ready_work_sim
    case = samples.case
    sim = ready_work_sim(1)
    engine = sim.engine
    # Prepare a genuine work call and change its target before its return.
    action, = deepcopy(sim.runtime['queue'])
    prepared = engine._prepare_call(action)
    case.assertIsInstance(prepared, dict)
    eid = prepared['execution_id']
    before = samples.read(engine, 'before-target-close', identifiers=[eid])[eid]
    old_head = engine.head
    engine.runtime['tasks'][action['target']]['status'] = 'closed'
    engine._save()
    returned = {'status': 'completed', 'output': {'report': 'Late e\u0301\r\n'}, 'usage': {}, 'error': None}
    engine._local_call_returned(eid, returned)
    engine._receive_call(prepared, deepcopy(returned))
    row = samples.read(engine, 'late-return', identifiers=[eid])[eid]
    case.assertEqual(row['preserved_reason'], 'The assigned task is already completed or closed')
    case.assertEqual(row['result_disposition'], {'kind': 'preserved_after_target_change'})
    raw = json.loads(engine.store.read(row['result_ref'], engine.head))
    case.assertEqual(raw['output'], returned['output'])
    case.assertEqual(row['outcome'], 'execution_incomplete')
    case.assertEqual(samples.read(engine, 'before-target-close-again', identifiers=[eid], head=old_head)[eid], before)


def stored_recovery_and_machine_outputs(samples):
    from support.provider_live import running_execution
    from support.sim import Sim
    from support.scheduling_machine import formal_scene
    from support.engine_lifecycle import external_sim, http_grant, extended, run_machine
    case = samples.case
    sim = Sim.activated()
    running_execution(sim, 'EX-storage-recovery', 'maintenance')
    engine = sim.engine
    engine._failed_live_review({'live': True, 'target': 'EX-storage-recovery'}, 'Exact recovery e\u0301\r\n')
    lifecycle.recover_execution(engine.runtime['executions']['EX-storage-recovery'], at=sim.clock.now())
    engine._save()
    row = samples.read(engine, 'recovery-pending', identifiers=['EX-storage-recovery'])['EX-storage-recovery']
    case.assertEqual(row['recovery_disposition'], 'reconcile_local_and_remote')
    case.assertEqual(row['after_stop'], {'decision': 'wait', 'reason': 'Exact recovery e\u0301\r\n'})
    lifecycle.end_recovered(engine.runtime['executions']['EX-storage-recovery'], at=sim.clock.now(),
        outcome='execution_incomplete', disposition='preserved_for_followup')
    engine._save()
    row = samples.read(engine, 'recovery-ended', identifiers=['EX-storage-recovery'])['EX-storage-recovery']
    case.assertNotIn('recovery_disposition', row)

    sim, action, _ = formal_scene()
    sim.engine.runtime['queue'] = [action]
    sim.engine._save()
    sim.engine.run(max_steps=1)
    rows = samples.read(sim.engine, 'formal-output')
    row, = [r for r in rows.values() if r.get('action', {}).get('id') == action['id']]
    case.assertEqual(row['formal_status'], 'verified')
    raw = sim.engine.store.read(row['raw_result_ref'], sim.engine.head)
    case.assertTrue(raw)
    case.assertEqual(row['outcome'], 'output_accepted')

    sim = external_sim()
    config = http_grant(sim.engine)
    sim.ports.http.table['/effect'] = (201, b'created', None)
    extended(sim.engine, 'external', config)
    prepared = deepcopy(sim.runtime['external_operations'][config['id']])
    run_machine(sim, 'external_action')
    operation = sim.runtime['external_operations'][config['id']]
    eid = operation['execution_id']
    row = samples.read(sim.engine, 'external-output', identifiers=[eid])[eid]
    case.assertEqual({key: row[key] for key in ('source_ref', 'operation_id', 'request_sha256',
        'effect_status', 'http_status', 'succeeded')}, {'source_ref': prepared['source_ref'],
        'operation_id': config['id'], 'request_sha256': prepared['request_sha256'],
        'effect_status': 'confirmed', 'http_status': 201, 'succeeded': True})
    case.assertEqual(len(sim.ports.http.requests), 1)


def assert_stored_unsealed_return_preserves_the_exact_rejected_candidate_and_check_refs(self, samples=None):
    from support.submission_receiver import history
    scene = history()
    engine = scene.engine
    transition_execution(engine.runtime['executions'][scene.execution_id], 'stopping', at=scene.sim.clock.now())
    engine._save()
    old_head = engine.head
    old = deepcopy(engine.store.load(old_head))
    output = deepcopy(scene.output)
    received = engine._receive_submission(scene.action, {'status': 'completed', 'output': output},
        scene.execution_id, scene.context, scene.schema, scene.workspace)
    engine._save()
    reader = record_store(scene.sim.repository, instance_id=scene.sim.instance_id,
                          backend=scene.sim.ports.git_backend, clock=scene.sim.clock)
    head, _, runtime = reader.load(engine.head)
    row = runtime['executions'][scene.execution_id]
    self.assertEqual(json.loads(reader.read(row['submitted_output_ref'], head)), output)
    self.assertEqual(json.loads(reader.read(row['submitted_extensions_ref'], head)), {})
    self.assertEqual(row['extensions'], {})
    check = json.loads(reader.read(row['submission_check_ref'], head))
    self.assertIs(check['passed'], False)
    issue, = [item for item in check['issues'] if item['rule_id'] == 'submission.sealed_candidate']
    self.assertEqual(issue['path'], 'submission_receipt')
    self.assertEqual(issue['message'], 'worker output was not captured by the central submit path')
    self.assertEqual(received['status'], 'returned')
    self.assertEqual(row['integration_result']['status'], 'returned')
    self.assertEqual(row['outcome'], 'execution_incomplete')
    self.assertEqual(reader.load(old_head), old)

    if samples is not None:
        samples.read(engine, 'unsealed-return', identifiers=[scene.execution_id])


def assert_stored_maintenance_archive_writes_termination_and_collection_before_local_cleanup(self, samples=None):
    from support.sim import Sim
    sim = Sim.activated()
    engine = sim.engine
    action = {'id': 'AC-archive-input', 'role': 'maintenance'}
    engine._action_lifecycle_gate(action)
    execution = engine._register_execution(action, {'id': 'EX-archive', 'role': 'maintenance'})
    profile = engine.instance['execution_profiles'][execution['execution_profile_ref']['id']]
    slots = engine._session_slots()
    self.assertIs(slots.acquire(execution['id'], profile=profile, execution=execution), True)
    self.assertIs(slots.release(execution['id']), True)
    transition_execution(execution, 'stopping', at=sim.clock.now())
    transition_execution(execution, 'ended', at=sim.clock.now(), outcome='cancelled')
    activities.finish_activity(engine.runtime, execution['owner_activity_id'], result_refs=[],
                               unresolved=[], followups=[], at=sim.clock.now())
    raw = b'\x00\xff\r\n' + 'Exact e\u0301 archive'.encode('utf-8')
    run = Path(engine.instance['workspace']) / 'runs' / execution['id']
    run.mkdir(parents=True)
    (run / 'evidence.bin').write_bytes(raw)
    engine._save()
    request = sim.control('request', config={'role': 'maintenance', 'cleanup_execution_ids': ['EX-archive']})
    engine.process_controls()
    cleanup, = [item for item in engine.runtime['queue'] if item.get('requested_by') == request['request_id']]
    old_head = engine.head
    old = deepcopy(engine.store.load(old_head))
    engine._maintenance_cleanup(cleanup, 'EX-archive')
    reader = record_store(sim.repository, instance_id=sim.instance_id,
                          backend=sim.ports.git_backend, clock=sim.clock)
    head, _, runtime = reader.load(engine.head)
    row = runtime['executions']['EX-archive']
    termination = row['termination']
    self.assertIs(termination['local_terminated'], True)
    receipt = reader.read(termination['evidence_ref'], termination['snapshot'])
    self.assertEqual((termination['bytes'], termination['sha256']),
                     (len(receipt), hashlib.sha256(receipt).hexdigest()))
    files = row['collection']['retention_manifest']
    evidence, = [item for item in files if item['path'] == 'evidence.bin']
    self.assertEqual(reader.read(evidence['artifact_ref'], evidence['snapshot']), raw)
    self.assertEqual((evidence['bytes'], evidence['sha256']), (len(raw), hashlib.sha256(raw).hexdigest()))
    self.assertEqual(termination['snapshot'], evidence['snapshot'])
    self.assertIs(run.exists(), False)
    self.assertEqual(reader.load(old_head), old)

    if samples is not None:
        samples.read(engine, 'maintenance-archive', identifiers=['EX-archive'])


def assert_stored_prepared_call_and_returned_evidence_keep_their_own_inputs_after_reload(self, samples=None):
    """One ready work call; the public prefix is shared by the existing scheduling fixture.

    This takes seconds cold because real preparation, submission and Git
    publication are the subject. Only external ports are doubles.
    """
    from support.scheduling_parallel import ready_work_sim, RATING
    from support.provider_probes import ObservedCalls
    from do_math.payloads import json_safe
    from do_math.execution_profiles import resolve_profile
    from do_math.planning import contract_hash

    sim = ready_work_sim(1)
    preparation = next(row for row in reversed(list(sim.runtime['executions'].values()))
                       if row['role'] == 'research_preparation' and row.get('model_decisions'))
    self.assertEqual(preparation['model_decisions'], {'0': RATING})
    self.assertEqual(sim.engine.store.load()[2]['executions'][preparation['id']]['model_decisions'], {'0': RATING})
    action, = deepcopy(sim.runtime['queue'])
    task = deepcopy(sim.runtime['tasks'][action['target']])
    governance = deepcopy(sim.engine._governance())

    def capture(arguments):
        prepared = arguments['prepared']
        return {'prepared': {key: deepcopy(prepared[key]) for key in
                ('execution', 'context', 'fitted', 'profile', 'prompt')},
                'result': json_safe(arguments['result'])}

    with ObservedCalls(receive=sim.engine._receive_call, capture={'receive': capture}) as observed:
        sim.engine.run(max_steps=1)
    captured, = observed.captured('receive')
    prepared, returned = captured['prepared'], captured['result']
    identifier = prepared['execution']['id']
    reader = record_store(sim.repository, instance_id=sim.instance_id,
                          backend=sim.ports.git_backend, clock=sim.clock)
    head, instance, runtime = reader.load(sim.engine.head)
    row = runtime['executions'][identifier]
    profile = resolve_profile(instance['execution_profiles'], row['execution_profile_ref'])
    self.assertEqual(profile, prepared['profile'])
    self.assertEqual(row['id'], prepared['context']['execution_id'])
    self.assertEqual(row['role'], 'research_work')
    self.assertEqual(row['actor_kind'], 'ai')
    self.assertEqual(row['action']['id'], action['id'])
    self.assertEqual(row['action']['target'], task['id'])
    self.assertEqual(row['owner_activity_id'], row['action']['owner_activity_id'])
    self.assertEqual((row['model'], row['effort']), (profile['ai']['model'], profile['ai']['effort']))
    self.assertEqual(row['model_selection'], prepared['execution']['model_selection'])
    self.assertEqual(row['grant_id'], prepared['context']['action']['grant_id'])
    self.assertEqual(row['goal_revision'], governance['goal_revision'])
    self.assertEqual(row['policy_revision'], governance['policy_revision'])
    self.assertEqual(row['contract_sha256'], contract_hash(task))
    self.assertEqual(row['input_snapshot'], prepared['context']['snapshot'])
    self.assertEqual(row['observed_at'], prepared['context']['observed_at'])
    self.assertEqual(row['created_at'], row['input_preparation']['started_at'])
    self.assertIs(type(row['input_preparation_milliseconds']), int)
    self.assertEqual(row['input_preparation_milliseconds'], 0)
    self.assertEqual(row['input_manifest'], prepared['fitted']['manifest'])
    self.assertEqual(row['input_reductions'], prepared['fitted']['reductions'])
    raw_prompt = prepared['prompt'].encode('utf-8')
    prompt = row['input_manifest']['prompt']
    self.assertEqual(prompt['artifact_ref'], 'runtime/artifacts/' + row['input_bundle'] + '/input.txt')
    self.assertEqual((prompt['sha256'], prompt['bytes']),
                     (hashlib.sha256(raw_prompt).hexdigest(), len(raw_prompt)))
    self.assertEqual(reader.read(prompt['artifact_ref'], head), raw_prompt)
    for field in ('decision_basis', 'source_basis', 'validity_basis', 'input_metrics', 'control_transport'):
        self.assertEqual(row[field], prepared['execution'][field])
    self.assertEqual(row['control_transport']['execution_id'], identifier)
    self.assertNotIn('capability', row['control_transport'])
    self.assertEqual(row['usage'], returned['usage'])
    report = row['provider_observation']
    self.assertEqual(json.loads(report['reported_fields_json']), returned['provider_observation'])
    for field in ('usage_segments', 'model_usage_reported', 'usage_scope', 'reported_models'):
        self.assertEqual(field in row, field in returned)
        if field in returned:
            self.assertEqual(row[field], returned[field])
    preserved = json.loads(reader.read(row['result_ref'], head))
    self.assertEqual(preserved['execution'], returned['execution'])
    self.assertEqual(row['result_ref'], 'runtime/artifacts/' + row['artifact_bundle'] + '/result.json')
    self.assertIs(row['outputs_complete'], True)
    for output in row['output_files']:
        raw = reader.read(output['artifact_ref'], head)
        self.assertEqual((output['bytes'], output['sha256']), (len(raw), hashlib.sha256(raw).hexdigest()))
    self.assertEqual(row['error'], None)
    self.assertEqual((row['status'], row['outcome']), ('ended', 'output_accepted'))
    submitted = json.loads(reader.read(row['submission_intent']['output_ref'], head))
    result, = [value for value in runtime['tasks'][task['id']]['results'] if value['execution_id'] == identifier]
    self.assertEqual(result['report'], submitted['report'])
    self.assertNotIn('output', row)  # This slot belongs to operational-review outputs.
    self.assertEqual(row['submission_receipt']['execution_id'], identifier)
    check = json.loads(reader.read(row['submission_intent']['check_ref'], head))
    self.assertIs(check['passed'], True)
    self.assertEqual(row['extensions'], json.loads(reader.read(row['submission_intent']['extensions_ref'], head)))
    self.assertEqual(row['capacity']['process']['execution_id'], identifier)
    self.assertEqual(row['capacity']['local_termination'], 'confirmed')
    self.assertNotIn('pid', row)
    self.assertNotIn('finished_at', row)
    self.assertNotIn('integration_id', row)  # Only bundle application's private candidate carries it.
    self.assertEqual(reader.load(row['input_snapshot'])[2]['executions'][identifier]['status'], 'queued')
    sim.restart()
    self.assertEqual(sim.runtime['executions'][identifier], row)

    if samples is not None:
        samples.read(sim.engine, 'work-return')
