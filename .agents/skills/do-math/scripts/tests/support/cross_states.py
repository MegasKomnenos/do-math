"""Finite public-path producers for cross-event preconditions (no queue edits).

Detection bounds: 60 owner passes per producer, 12 per armed event. They are
limits, never claims that those paths have been reached in CODE-ONLY work.
"""
from support.cross_contracts import ContractOracle
from support.cross_events import responder
from support.sim import Sim, built

PRODUCER_BOUND = 60
EVENT_BOUND = 12


def applied(sim, action, **options):
    request = sim.control(action, **options)
    sim.engine.process_controls()
    result = sim.engine.control_result(request['request_id'])
    assert result.get('effect') != 'rejected', result
    return result


def queued(sim, role, stage=None):
    return next((a for a in sim.runtime['queue'] if a['role'] == role
                 and (stage is None or a.get('stage') == stage)), None)


def drive(sim, predicate, bound=PRODUCER_BOUND):
    oracle = ContractOracle(sim)
    for _ in range(bound):
        if predicate(sim):
            return
        sim.advance(sim.instance['config']['plan_settle_seconds'] + 1)
        sim.step()
        assert not getattr(sim.model.responder, 'failures', []), sim.model.responder.failures
        oracle.check(sim)
    recent = list(sim.runtime['executions'].values())[-8:]
    assert predicate(sim), ('cross producer bound', bound, sim.waiting(),
        [{key: row.get(key) for key in ('id', 'role', 'outcome', 'errors', 'output_errors', 'diagnosis')}
         for row in recent])


def activate(root=None, shared=None):
    sim = Sim.activated() if root is None else Sim.activated(root, shared=shared)
    applied(sim, 'configure', config={'max_output_repairs': 0})
    return sim


def _build_plan_ready(root, shared):
    sim = activate(root, shared)
    drive(sim, lambda s: queued(s, 'research_plan') is not None
          and any(row['state'] == 'ready' for row in s.engine._task_readiness.values()))
    return sim


def _restore_start(name, build):
    """Restore a quiescent public prefix; derive the generation gates without an owner pass.

    The new engine's readiness cache is initially empty. Recompute it with the
    actual pure task judgment and its normal cache producer, preserving every
    published record and clock/ID value. Generated events and verdicts after
    this fixed prefix still execute normally.
    """
    from copy import deepcopy
    from do_math.lifecycle_engine import _SCHEDULABLE
    from do_math.planning import task_ready
    sim = built(name, build)
    before = deepcopy((sim.instance, sim.runtime, sim.clock.state()))
    context = sim.engine._evaluation_context()
    for identifier, task in sim.runtime['tasks'].items():
        if task.get('status') in _SCHEDULABLE:
            evaluation = task_ready(task, sim.instance, sim.runtime, evaluation_context=context)
            sim.engine._record_readiness(identifier, evaluation, sim.clock.now())
    assert (sim.instance, sim.runtime, sim.clock.state()) == before, 'prefix readiness changed durable facts or IDs'
    ContractOracle(sim).check(sim)
    return sim


def plan_ready():
    return _restore_start('cross-plan-ready', _build_plan_ready)


def supplemental_ready():
    from do_math.execution_profiles import profile_ref
    from support.model import rebound
    sim = activate()

    def bind_supplemental(out, context):
        current = context['role_profile_refs']['supplemental_research']
        refs = [profile_ref(p) for p in context['execution_profiles']
                if p['role'] == 'supplemental_research' and profile_ref(p) in current]
        assert refs
        for candidate in out['candidates']:
            candidate['profile_refs'].extend(refs)

    sim.model.on('research_preparation').reply(rebound(bind_supplemental))
    drive(sim, lambda s: queued(s, 'research_plan') is not None
          and any(row['state'] == 'ready' for row in s.engine._task_readiness.values()))
    assert_event(sim, queued(sim, 'research_plan'), 'selection', 'not_selected')
    tid = next(tid for tid, row in sim.engine._task_readiness.items() if row['state'] == 'ready')
    applied(sim, 'request', config={'role': 'supplemental_research', 'target': tid})
    assert queued(sim, 'supplemental_research') is not None
    return sim


def _build_returned_plan(root, shared):
    sim = _build_plan_ready(root, shared)
    drive(sim, lambda s: queued(s, 'research_work') is not None)
    drive(sim, lambda s: queued(s, 'research_plan') is not None and any(
        t.get('results') for t in s.runtime['tasks'].values()))
    return sim


def returned_plan():
    return _restore_start('cross-returned-plan', _build_returned_plan)


def review_stage(stage='initial'):
    from support.review_research import research_sim
    from support.engine_purpose import PurposeResponder
    sim = research_sim()
    class ReviewEventResponder(PurposeResponder):
        def answer(self, role, context, workspace):
            if role == 'maintenance':
                from support.default_responder import DefaultResponder
                return DefaultResponder().respond(role, context, workspace)
            return super().answer(role, context, workspace)
    sim.model.responder = ReviewEventResponder('dispute' if stage in {'answer', 'judge'} else 'direct')
    drive(sim, lambda s: queued(s, 'identity_review', stage) is not None)
    return sim


def goal_ready():
    from support.review_research import research_sim
    sim = research_sim()
    drive(sim, lambda s: queued(s, 'goal_audit') is not None)
    return sim


def investigation_ready():
    from support.review_research import InvestigationResponder, research_sim
    sim = research_sim()
    sim.model.responder = InvestigationResponder()
    drive(sim, lambda s: queued(s, 'supplemental_research') is not None)
    return sim


def failure_ready():
    from support.model import raw, default
    sim = activate()
    # Real worker output fails the actual receiver. Only this first action is
    # damaged; automatic repair responses cannot perpetuate the invalid output.
    first = queued(sim, 'research_preparation')
    assert first is not None
    sim.model.on('research_preparation', id=first['id']).reply(raw({'invalid': True}, expected_receipt='rejected')).reply(default())
    drive(sim, lambda s: queued(s, 'operational_review') is not None)
    return sim


def maintenance_ready():
    sim = activate()
    applied(sim, 'request', text='Inspect retained recovery evidence', config={'role': 'maintenance'})
    assert queued(sim, 'maintenance') is not None
    return sim


def interpretation_ready():
    sim = activate()
    applied(sim, 'input', text='Keep the natural-number domain explicit in the current question.')
    drive(sim, lambda s: queued(s, 'intent_interpretation', 'check') is not None)
    return sim


def _build_waived_plan(root, shared):
    from do_math.planning import contract_hash
    sim = _build_returned_plan(root, shared)
    for task in sim.runtime['tasks'].values():
        if task.get('results') and task['status'] not in {'completed', 'closed'}:
            applied(sim, 'decision', config={'change': {'kind': 'task_scope', 'task_id': task['id'],
                'revision': task['revision'], 'contract_sha256': contract_hash(task),
                'disposition': 'waive', 'obligation_ids': [o['id'] for o in task['completion_obligations']],
                'reason': 'The remaining obligation is explicitly waived for this investigation.'}})
    assert queued(sim, 'research_plan') is not None
    return sim


def waived_plan():
    return _restore_start('cross-waived-plan', _build_waived_plan)


def checkpoint_failure():
    import json
    from support.live_finish_model import install
    sim = activate()
    fired = []

    def interrupt(cli, context):
        if fired or context['action']['role'] != 'research_preparation':
            return
        fired.append(context['action']['id'])
        (cli.workspace / 'checkpoint.json').write_text(json.dumps({
            'current_claim': 'The bounded case was inspected.', 'evidence_paths': [],
            'attempts': ['Compared the supplied domain.'], 'remaining_work': ['Complete the general argument.'],
            'next_step': 'Read the preserved argument.', 'progress_state': 'blocked'}), encoding='utf-8')
        return False

    install(sim, interrupt)
    drive(sim, lambda s: queued(s, 'operational_review') is not None)
    target = queued(sim, 'operational_review')['target']
    assert sim.runtime['checkpoints'][target]['artifact_ref']
    return sim


def kind_ready():
    sim = activate()
    applied(sim, 'knowledge', config={'operation': 'register-kind', 'definition': {
        'family': 'knowledge', 'token': 'cross_bounded_observation',
        'meaning': 'An observation limited to the explicitly supplied finite domain.', 'constraints': {}}})
    assert queued(sim, 'maintenance') is not None
    return sim


def operational_task_ready():
    from do_math.planning import contract_hash
    from support.default_responder import DefaultResponder
    from support.role_answers import candidate

    class PreserveReturned(DefaultResponder):
        def respond(self, role, ctx, workspace):
            out = super().respond(role, ctx, workspace)
            if role == 'research_plan':
                for assessment in out['task_assessments']:
                    assessment['decision'] = 'incomplete'
                    for item in assessment['item_dispositions']:
                        item['kind'] = 'open'
            return out

    sim = activate()
    proposal = candidate('Independently judgeable argument')
    proposal['completion_obligations'][0]['judges'] = ['research_plan', 'operational_review']
    sim.model.responder = PreserveReturned(preparation_candidates=[proposal])
    drive(sim, lambda s: any(t.get('results') for t in s.runtime['tasks'].values()))
    task = next(t for t in sim.runtime['tasks'].values() if t.get('results'))
    applied(sim, 'decision', config={'change': {'kind': 'task_scope', 'task_id': task['id'],
        'revision': task['revision'], 'contract_sha256': contract_hash(task), 'disposition': 'waive',
        'obligation_ids': [o['id'] for o in task['completion_obligations']],
        'reason': 'Explicitly authorize closure of this bounded task if selected.'}})
    target = next(e['id'] for e in sim.runtime['executions'].values()
                  if e['role'] == 'research_work' and e['action'].get('target') == task['id'])
    applied(sim, 'request', text='Independently assess the returned task',
            config={'role': 'operational_review', 'target': target})
    return sim


def _initializing_sim(research_grants):
    """Adopt exact public grants before activation; no synthetic authority rows."""
    from datetime import timedelta
    from tempfile import TemporaryDirectory
    from do_math.canonical import exact_content_hash
    from support.state_builders import charter_record
    from support.trust_inputs import trust_fixture
    directory = TemporaryDirectory(prefix='cross-initial-')
    sim = Sim(directory.name)
    sim.cross_temporary = directory
    applied(sim, 'configure', config={'max_output_repairs': 0,
        'tool_review_window_seconds': 60, 'self_check_response_window_seconds': 5})
    expiry = (sim.clock.wall() + timedelta(days=1)).isoformat()
    applied(sim, 'decision', config={'change': {'kind': 'initialization', 'operation': 'governance',
        'records': [charter_record(sim.instance['lifecycle']['immutable_input']['text'])]}})
    for identifier, roles in [('GR-cross-initial', ['intent_interpretation', 'maintenance']), *research_grants]:
        applied(sim, 'decision', config={'change': {'kind': 'grant', 'grant': {'id': identifier,
            'kind': 'local', 'roles': roles, 'reuse': 'reusable', 'expires_at': expiry}}})
    digest = exact_content_hash(sim.instance['config'])
    applied(sim, 'decision', config={'change': {'kind': 'initialization', 'operation': 'probe', 'config_sha256': digest}})
    applied(sim, 'trust', config=trust_fixture(sim.shared, sim.instance['config']['lean_command'], directory=sim.shared / 'trust'))
    applied(sim, 'trust', config={'operation': 'transition', 'env_id': next(iter(sim.instance['trust_environments']))})
    reference = sim.engine._select_model({'role': 'intent_interpretation'})['profile_ref']
    applied(sim, 'decision', config={'change': {'kind': 'initialization', 'config_sha256': digest,
        'adopt_current_governance': True, 'conversation_loss_policy': 'continue_authorized',
        'external_policy': 'disabled', 'adopt_default_review_policy': True,
        'initial_profile_ref': reference, 'initial_grant_ids': ['GR-cross-initial'],
        'research_grant_ids': [identifier for identifier, _ in research_grants]}})
    return sim


def initial_diagnosis_ready():
    """Public initialization stopped before its first maintenance diagnosis."""
    from do_math.contracts import ROLES
    from support.model import raw, default
    sim = _initializing_sim([('GR-cross-research', list(ROLES) + ['formal_check'])])
    sim.model.on('intent_interpretation', stage='interpret').reply(raw({'invalid': True}, expected_receipt='rejected')).reply(default())
    drive(sim, lambda s: queued(s, 'maintenance') is not None)
    return sim


def split_writer_plan_ready():
    """Public activation/preparation/review under independently adopted grants.

    Revoking only the writer later leaves a genuinely pending revision while
    the planner can retire its target. One sixty-pass bound covers the prefix.
    """
    from do_math.contracts import ROLES
    sim = _initializing_sim([
        ('GR-cross-research', [role for role in ROLES if role != 'research_preparation'] + ['formal_check']),
        ('GR-cross-writer', ['research_preparation'])])
    drive(sim, lambda s: s.instance['lifecycle']['state'] == 'active'
          and queued(s, 'research_plan') is not None
          and any(row['state'] == 'ready' for row in s.engine._task_readiness.values()))
    return sim


def assert_event(sim, action, event, value):
    response = responder(sim)
    count = len(response.observed)
    response.arm(action, event, value)
    try:
        drive(sim, lambda s: len(response.observed) > count, bound=EVENT_BOUND)
    except AssertionError:
        from support.cross_diagnostics import preserve
        preserve(sim, 'event-failure')
        raise
    observed = response.observed[count]
    assert observed['action']['id'] == action['id'], 'another action consumed the armed event'
    rows = [row for row in sim.runtime['executions'].values()
            if row['action']['id'] == action['id'] and row['status'] == 'ended']
    if not rows or rows[-1]['outcome'] != 'output_accepted':
        from support.cross_diagnostics import preserve
        location = preserve(sim, 'event-rejected')
        raise AssertionError(('event not accepted', event, value, str(location),
                              [(r['id'], r['outcome'], r.get('error')) for r in rows]))
    assert observed['event'] == event and observed['value'] == value
    ContractOracle(sim).check(sim)
    return observed
