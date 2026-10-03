"""7-A(b,c) expectations derived from contracts, not dispatch predicates."""
from copy import deepcopy


def actions(runtime):
    return (list(runtime['queue'])
            + [row['action'] for row in runtime.get('waiting_actions', {}).values()]
            + [row['action'] for row in runtime['executions'].values()
               if row['status'] != 'ended' and row.get('action')])


def preservation_requests(runtime):
    """7-A(b)의 병합·개정 요청을 추적한다. 단일 내부 배정은 종결 때 취소할 수 있다."""
    result = []
    for action in actions(runtime):
        reason = action.get('reason', '')
        atoms = set(reason.split('\n')) if isinstance(reason, str) else set()
        atoms.update(text for text in action.get('reasons', []) if isinstance(text, str))
        if action.get('revision_of') or len(atoms) > 1:
            result.append(action)
    return result


def reasons(value):
    """Exact request reason atoms, including archived/merged action evidence."""
    result = set()
    if isinstance(value, dict):
        for key, item in value.items():
            if key == 'reasons' and isinstance(item, list):
                result.update(text for text in item if isinstance(text, str))
            elif key == 'reason' and isinstance(item, str):
                result.update(item.split('\n'))
            result.update(reasons(item))
    elif isinstance(value, list):
        for item in value:
            result.update(reasons(item))
    return result


class RequestReasonLoss(AssertionError):
    """The observer's exact producer requests and surviving request evidence."""
    def __init__(self, before, evidence, runtime):
        self.requests = deepcopy(before)
        self.preserved = deepcopy(evidence)
        self.runtime_status = runtime.get('status')
        self.lost = reasons(before) - reasons(evidence)
        super().__init__(('lost request reasons', self.lost))


def assert_preserved_reasons(before, runtime):
    # History includes consumed and explicitly retired requests. An unrelated
    # top-level string does not count as a request's preservation evidence.
    evidence = [*actions(runtime), *runtime['history'],
                *[row['action'] for row in runtime['executions'].values() if row.get('action')],
                *[task['scope_disposition'] for task in runtime.get('tasks', {}).values()
                  if task.get('scope_disposition')]]
    if not reasons(before) <= reasons(evidence):
        raise RequestReasonLoss(before, evidence, runtime)


def assert_independent_actions(before, runtime):
    observed = {a['id'] for a in actions(runtime)}
    observed.update(row['action']['id'] for row in runtime['executions'].values() if row.get('action'))
    assert set(before) <= observed, ('independent action erased', set(before) - observed)


def assert_single_owners(runtime):
    recovery_owners = set()
    for execution in runtime['executions'].values():
        if execution['status'] != 'ended' and execution.get('role') == 'recovery':
            owner = execution['owner_activity_id']
            assert owner not in recovery_owners, ('duplicate installation recovery owner', owner)
            recovery_owners.add(owner)
    owners = {}
    for action in actions(runtime):
        # An action may be projected in both the queue and live/wait records.
        # That is one owner, whereas a distinct action in the same slot is not.
        key = (action.get('lineage_id', action['id']), action['role'], action.get('target'),
               action.get('review_cycle_id'), action.get('basis'), action.get('stage'),
               action.get('round'), action.get('slot'), action.get('selected_contract_sha256'))
        assert owners.setdefault(key, action['id']) == action['id'], ('duplicate lineage owner', key)
    slots = {}
    for action in actions(runtime):
        if action['role'] not in {'identity_review', 'goal_audit'}:
            continue
        key = tuple(action.get(k) for k in ('role', 'target', 'review_cycle_id', 'basis', 'stage', 'round', 'slot'))
        assert slots.setdefault(key, action['id']) == action['id'], ('duplicate review slot', key)


def assert_replacement(before, submitted, current):
    for key in ('scope', 'completion_obligations', 'expected', 'progress_criteria'):
        assert current[key] == submitted[key], ('revision must replace', key)
        assert current['revision_history'][-1][key] == before[key], ('old contract lost', key)
    assert current['revision'] == before['revision'] + 1


def assert_no_resume_replay(before, runtime):
    """A resume control supplies no revised input or recovery authorization."""
    pending_ids = {a['id'] for a in runtime['queue']}
    for identifier, wait in before.items():
        if wait.get('kind') not in {'output_validation', 'execution_failure', 'submission_failure'}:
            continue
        assert identifier not in pending_ids, ('resume resurrected unchanged failed action', identifier)
        assert runtime['executions'][wait['execution_id']]['status'] == 'ended'


def assert_dispositions_settled(runtime):
    for record in runtime.get('operational_dispositions', {}).values():
        target = runtime['executions'][record['target_execution_id']]
        reviewer = runtime['executions'][record['execution_id']]
        if target['status'] != 'ended' or reviewer['status'] != 'ended':
            continue
        if runtime['status'] in {'paused', 'closed', 'completed'}:
            continue
        assert record['status'] != 'awaiting_termination', ('ended disposition left unsettled', record)
        if record['disposition']['kind'] in {'retry', 'resume'}:
            successor = record.get('result', {}).get('continuation_action_id')
            if not successor:
                descendants = [a for a in actions(runtime) if a.get('continuation_of') == target['id']]
                descendants += [e['action'] for e in runtime['executions'].values()
                                if e.get('action') and e.get('continuation_of') == target['id']]
                if descendants:
                    assert record['status'] == 'superseded', record


class CapacityWitness:
    """Inspect new reservations against adopted resource editions at admission.

Existing reservations may outlive a limit reduction; only new reservations are
required to use the current edition. No admission_check/_select_model oracle.
"""
    def __init__(self, sim):
        self.seen = set(sim.runtime.get('reservations', {}))

    def check(self, sim):
        adopted = {ref['id'] for refs in sim.instance['role_profile_refs'].values() for ref in refs}
        current = {ref for pid in adopted for ref in
                   sim.instance['execution_profiles'][pid].get('ai', {}).get('capacity_refs', [])}
        for key, row in sim.runtime.get('reservations', {}).items():
            if key in self.seen:
                continue
            constraint = sim.instance['capacity_constraints'][row['constraint_id']]
            if constraint['kind'] == 'concurrency':
                assert row['constraint_id'] in current, ('stale capacity edition', row)
                assert constraint['work_slots'] > 0, ('admitted to a zero-slot resource', row)
                held = [r for r in sim.runtime['reservations'].values() if r['state'] == 'held'
                        and sim.instance['capacity_constraints'][r['constraint_id']].get('model') == constraint['model']]
                assert sum(r['reserved'] - r['returned'] for r in held) <= constraint['work_slots'], (
                    'current model capacity exceeded', constraint, held)
        self.seen.update(sim.runtime.get('reservations', {}))


def assert_current_model_requirements(sim):
    """The two-axis maximum and role floor from references/모델과-실행예산.

This computes the expected tier independently; it never invokes selection or
assessment_tier. Explicit immutable profiles may exceed the required floor.
"""
    from do_math.model_policy import ROLE_TIERS
    rank = {'low': 0, 'medium': 1, 'high': 2}
    config = sim.instance['config']
    live = {e['action']['id'] for e in sim.runtime['executions'].values()
            if e['status'] != 'ended' and e.get('action')}
    for action in actions(sim.runtime):
        selection = action.get('model_selection')
        if action['id'] in live or not selection:
            continue
        task = sim.runtime['tasks'].get(action.get('target'), {})
        if not task and action.get('target') in sim.instance['knowledge']:
            task = sim.runtime['tasks'].get(sim.instance['knowledge'][action['target']].get('task_id'), {})
        assessment = action.get('model_assessment') or task.get('model_assessment')
        parent = sim.runtime['executions'].get(action.get('target'), {})
        reviewed = parent.get('model_selection')
        floor = config['role_tiers'].get(action['role'], ROLE_TIERS.get(action['role'], 'low'))
        values = [floor]
        if assessment:
            values += [assessment['difficulty'], assessment['importance']]
        elif reviewed:
            axes = reviewed.get('assessment')
            values += [axes['difficulty'], axes['importance']] if axes else [reviewed['tier']]
        elif action['role'] in {'research_work', 'supplemental_research'}:
            values.append('high')
        expected = sorted(values, key=rank.__getitem__)[-1]
        if action.get('profile_ref'):
            assert rank[selection['tier']] >= rank[expected], action
        else:
            assert selection['tier'] == expected, ('stale model requirement', action, expected)
            assert selection['model'] == config['tier_models'][expected], ('stale model mapping', action)


def judgment_evidence(rows):
    # Currentness is a derived, mutable annotation (knowledge_engine). Preserve
    # the actual judgment, its basis and dependencies, allowing invalidation.
    return [{k: deepcopy(v) for k, v in row.items() if k not in {'current', 'invalidated_reason'}} for row in rows]


def assert_ended_evidence(before, current, runtime):
    """Physical termination is final; held sealed output may be integrated later.

    유지보수/편입 영향의 독립 검토: acceptance of the original sealed bundle
    after independent review does not reopen its producer's execution authority.
    """
    for key in ('status', 'ended_at', 'transitions', 'authority_revocation',
                'input_manifest', 'execution_profile_ref', 'action', 'output_files'):
        assert current.get(key) == before.get(key), ('ended execution evidence changed', key)
    if current.get('outcome') == before.get('outcome'):
        return
    assert (before.get('outcome'), current.get('outcome')) == (
        'execution_incomplete', 'output_accepted'), 'unjustified terminal result change'
    receipt = before.get('submission_receipt')
    assert receipt and current.get('submission_receipt') == receipt, 'late integration lost sealed receipt'
    assert current.get('submission_intent') == before.get('submission_intent'), 'late integration changed sealed input'
    disposition = current.get('result_disposition', {})
    assert disposition.get('kind') == 'submission_integrated', 'late integration lacks disposition'
    identifiers = disposition.get('integration_ids')
    assert identifiers, 'late integration lacks integration receipts'
    for identifier in identifiers:
        assert runtime.get('integrations', {}).get(identifier, {}).get('execution_id') == current['id'], (
            'late integration receipt names another producer', identifier)
