"""Composable answers made from the worker's actual, verified role input.

These change only the external model responder. Binding, sealing, submission,
ModelRunner, receivers and Repository remain actual. A choice is consumed once;
it cannot turn an output repair into an infinite sequence of the same answer.
"""
from copy import deepcopy
from datetime import datetime, timedelta
import json

from support.role_answers import candidate, contract_review, planning_model_assessments


def extensions(workspace, **changes):
    path = workspace / 'activity-extensions.json'
    value = json.loads(path.read_bytes()) if path.exists() else {}
    value.update(changes)
    path.write_text(json.dumps(value), encoding='utf-8')


class EventResponder:
    def __init__(self, base):
        self.base = base
        self.pending = {}
        self.observed = []

    @property
    def failures(self):
        return getattr(self.base, 'failures', [])

    def arm(self, action, event, value):
        assert action['id'] not in self.pending, action
        self.pending[action['id']] = (event, value)

    def respond(self, role, ctx, workspace):
        # The base checks actual input before any judgment is changed.
        if ctx['action'].get('delegation_application_id'):
            from do_math.canonical import exact_content_hash
            case = ctx['delegation_case']
            assert set(case) == {'basis', 'input_sha256'}, 'peer judgments leaked into blind case'
            assert exact_content_hash(case['basis']) == case['input_sha256']
            assert ctx['user_request']['delegation_case'] == case
            out = {'summary': 'Compare only the supplied blind delegation case.', 'used_sources': [], 'questions': [],
                'delegation_judgment': {'input_sha256': case['input_sha256'], 'decision': 'unresolved',
                    'reason': 'The supplied authority requires an explicit case comparison.'}}
        else:
            out = self.base.respond(role, ctx, workspace)
        if role == 'research_plan':
            # Materialized result rows include local paths. Rehashing them does
            # not recover the receiver's stored returned-task population.
            returned = set(ctx['returned_task_ids'])
            out['task_assessments'] = [row for row in out['task_assessments'] if row['task_id'] in returned]
            assert {row['task_id'] for row in out['task_assessments']} == returned
            assert len(out['task_assessments']) == len(returned)
        if role == 'identity_review':
            review, action = ctx['role_review'], ctx['action']
            assert out['proposal_digest'] == review['proposal_digest']
            # Follow-up cardinality comes from the actual issues. In particular
            # a split answer must not make the next organizer drop one finding.
            if action['stage'] == 'organize':
                out['issues'] = [{'id': 'cross-issue-' + str(action['round']) + '-' + str(i),
                    'finding_refs': [deepcopy(row['ref'])],
                    'answer_role_slot_id': row['ref']['slot'] if row['ref']['stage'] in {'initial', 'answer'}
                    else review['reviewer_slots'][0]} for i, row in enumerate(review['pending_findings'])]
            elif action['stage'] == 'answer':
                out['answers'] = [{'issue_id': identifier, 'disposition': 'withdraw',
                    'statement': 'The supplied explanation fixes the same explicit natural-number domain.',
                    'evidence': ['proposal:explanation']} for identifier in review['answer_requests']]
            elif action['stage'] == 'judge':
                out['issue_verdicts'] = [{'issue_id': identifier, 'decision': 'rejected',
                    'reason': 'The original explanation explicitly fixes the natural-number domain.',
                    'evidence': ['proposal:explanation']} for identifier in review['issues']]
        choice = self.pending.pop(ctx['action']['id'], None)
        armed = choice is not None
        if choice is None:
            # A predecessor writer can run before the armed plan. Its default
            # answer must resolve the supplied revision targets too.
            if (role == 'research_preparation' and ctx['action'].get('revision_targets')
                    and set(ctx['action']['revision_targets']) <= {t['id'] for t in ctx.get('tasks', [])}):
                choice = ('revision', True)
            else:
                return out
        event, value = choice
        original = deepcopy(out)
        if event == 'contract':
            out.update(contract_review(ctx, decision=value,
                findings=[] if value == 'approved' else ['The supplied domain needs an explicit boundary.']))
        elif event == 'work':
            assert ctx['task']['id'] == ctx['action']['target']
            out.update(outcome=value)
            if role == 'supplemental_research':
                out['report'] = ('Inspected the supplied task ' + ctx['task']['title']
                    + '; the explicit domain is retained. Outcome: ' + value + '.')
            if value != 'submitted':
                out.update(knowledge=[], relations=[], remaining_work=['Complete the supplied argument.'])
        elif event in {'selection', 'withdraw', 'revision_request', 'audit'}:
            assert {r['task_id'] for r in out['dispositions']} == set(ctx['ready_task_ids'])
            if event == 'selection':
                assert out['dispositions'], 'selection requires actual ready tasks'
                for row in out['dispositions']:
                    row.update(kind=value)
                    if value != 'selected':
                        row.update(next_owner='research_plan', parallel_task_ids=[],
                            revisit={'at': (datetime.fromisoformat(ctx['observed_at'].replace('Z', '+00:00'))
                                + timedelta(days=1)).isoformat(), 'event_refs': []},
                            missing_inputs=['Explicit domain clarification'] if value == 'not_assessable' else [])
            elif event == 'withdraw':
                # Not-ready tasks remain visible through authenticated catalog
                # sources, even when the ready/returned tasks list is empty.
                from do_math.context_store import read_source
                supplied = {t['id'] for t in ctx['tasks']}
                for entry in ctx.get('task_catalog', []):
                    if entry['id'] in supplied:
                        continue
                    reference = entry['source_ref']
                    read = read_source(workspace, reference, limit=max(1, reference['bytes']))
                    assert read['status'] == 'ok' and not read['truncated'], read
                    task = {**entry, **json.loads(read['bytes'])}
                    assert task['id'] == entry['id']
                    ctx['tasks'].append(task)
                targets = [t['id'] for t in ctx['tasks'] if t['status'] in {'planned', 'waiting'}
                           and not t.get('results') and t.get('producer_execution')]
                assert targets, ctx['action']
                for row in out['dispositions']:
                    row.update(kind='not_selected', next_owner='research_plan',
                        revisit={'at': (datetime.fromisoformat(ctx['observed_at'].replace('Z', '+00:00'))
                            + timedelta(days=1)).isoformat(), 'event_refs': []})
                extensions(workspace, task_dispositions=[{'task_id': tid,
                    'disposition': 'withdraw', 'reason': 'This independent approach is no longer required.'}
                    for tid in targets])
            elif event == 'revision_request':
                assert ctx['ready_task_ids'], ctx['action']
                for row in out['dispositions']:
                    row.update(kind='not_selected', next_owner='research_preparation',
                        revisit={'at': (datetime.fromisoformat(ctx['observed_at'].replace('Z', '+00:00'))
                            + timedelta(days=1)).isoformat(), 'event_refs': []})
                extensions(workspace, revision_requests=[{'record_ids': list(ctx['ready_task_ids']),
                    'reason': 'Replace the contract with a narrower explicit domain.'}])
                out['preparation_requests'] = ['Independently compare the alternative proof approach.']
            else:
                out['goal_audit'] = value
            extensions(workspace, model_assessments=planning_model_assessments(out, ctx))
        elif event == 'assessment':
            assert out['task_assessments'], ctx['action']
            for row in out['task_assessments']:
                row['decision'] = value
                if value == 'incomplete':
                    for item in row['item_dispositions']:
                        item['kind'] = 'open'
                elif value == 'completed':
                    from support.role_answers import assessment
                    task = next(t for t in ctx['tasks'] if t['id'] == row['task_id'])
                    row['item_dispositions'] = assessment(task)['item_dispositions']
                    row['unresolved'] = []
                elif value == 'closed':
                    authority = next(d for d in ctx['decisions'] if d.get('change', {}).get('kind') == 'task_scope'
                        and d['change'].get('task_id') == row['task_id'] and d['change'].get('disposition') == 'waive')
                    for item in row['item_dispositions']:
                        item.update(kind='waived', authority_ref=authority['id'])
        elif event == 'revision':
            tasks = {row['id']: row for row in ctx['tasks']}
            targets = ctx['action']['revision_targets']
            assert targets and set(targets) <= tasks.keys()
            out['candidates'] = []
            for tid in targets:
                item = candidate(tasks[tid]['title'], revises=tid)
                item['scope'] = {'included': ['Only the explicit natural-number domain'], 'excluded': ['Other domains']}
                item['completion_obligations'][0]['claim'] = 'Report the narrowed domain only.'
                out['candidates'].append(item)
            from support.default_responder import contract_checks, rating
            from support.observation_inputs import supply_observation_rules
            extra = {'revision_resolutions': [{'record_id': tid, 'disposition': 'revised',
                'reason': 'Replace the old contract, retaining its historical edition.'} for tid in targets],
                'contract_checks': contract_checks(out['candidates']),
                'model_assessments': [rating(task_title=row['title']) for row in out['candidates']]}
            supply_observation_rules(out['candidates'], extra)
            extensions(workspace, **extra)
        elif event in {'identity', 'goal', 'interpretation'}:
            out['decision'] = value
            out['scope_complete'] = value != 'unresolved'
            if event == 'identity':
                assert out['proposal_digest'] == ctx['role_review']['proposal_digest']
                if ctx['action']['stage'] == 'initial':
                    out['findings'] = [] if value == 'match' else [{'id': 'cross-domain',
                        'statement': 'Compare the declared domain with the supplied explanation.',
                        'evidence': ['proposal:explanation']}]
            elif event == 'interpretation' and value != 'approved':
                out['findings'] = ['The supplied interpretation requires a domain clarification.']
        elif event == 'answer':
            assert out['answers'], ctx['action']
            for row in out['answers']:
                row['disposition'] = value
            if value == 'split':
                out['new_findings'] = [{'id': row['issue_id'] + '-part-' + str(i),
                    'parent_issue_ids': [row['issue_id']], 'statement': text,
                    'evidence': list(row['evidence'])}
                    for row in out['answers'] for i, text in enumerate(
                        ['Compare the quantified domain.', 'Compare the operation on that domain.'])]
        elif event == 'verdict':
            assert out['issue_verdicts'], ctx['action']
            for row in out['issue_verdicts']:
                row['decision'] = value
            out['decision'] = {'approved': 'mismatch', 'rejected': 'match', 'unresolved': 'unresolved'}[value]
            out['scope_complete'] = value != 'unresolved'
        elif event == 'investigation':
            request = ctx['review_research']
            out.update(outcome=value, research_request_id=request['id'], request_digest=request['request_digest'],
                scope_complete=value == 'answered')
            if value == 'unresolved':
                out.update(answer='The supplied sources do not resolve the domain question.', evidence_refs=[])
        elif event == 'task_operation':
            from support.role_answers import assessment
            task = ctx['proposal']['task']
            assert task['id'] == ctx['execution_to_review']['action']['target']
            row = assessment(task)
            row['decision'] = value
            if value == 'incomplete':
                for item in row['item_dispositions']:
                    item['kind'] = 'open'
            if value == 'closed':
                authority = next(d for d in ctx['decisions'] if d.get('change', {}).get('kind') == 'task_scope'
                    and d['change'].get('task_id') == task['id'] and d['change'].get('disposition') == 'waive')
                for item in row['item_dispositions']:
                    item.update(kind='waived', authority_ref=authority['id'])
            out.update(task_assessments=[row], disposition={'kind': 'task_disposition',
                'task_id': task['id'], 'task_state': value, 'basis_refs': [ctx['action']['target']],
                'next_owner': 'engine', 'reason': 'Judge each supplied returned obligation under its named authority.'})
        elif event in {'operation', 'operation_revision'}:
            target = ctx['action']['target']
            assert target in ctx['admissible_basis_refs']
            proposal = {'kind': value, 'basis_refs': [target], 'next_owner': 'engine',
                'reason': 'Use the preserved result and current input to settle this activity.'}
            if value == 'continue':
                proposal['next_review'] = None
            elif value == 'retry':
                proposal.update(scope='Same unfinished activity', replay_safety='No external effects were submitted')
            elif value == 'resume':
                checkpoint = ctx['operational_evidence']['checkpoint']
                assert checkpoint and checkpoint['artifact_ref'] in ctx['admissible_basis_refs']
                proposal.update(checkpoint_ref=checkpoint['artifact_ref'], scope='The preserved unfinished argument')
            elif value == 'repair':
                proposal.update(repair_target='installation:scripts/do_math/core_engine.py',
                    next_owner='installation_recovery', meaning_preserving=True,
                    verification='Reproduce the preserved receiver failure with its original input')
            elif value == 'user_decision':
                proposal.update(question='Which remaining approach should be attempted?', effect='Select the next activity')
            else:
                raise AssertionError('operation needs its own current checkpoint/task producer: ' + value)
            out['disposition'] = proposal
            if event == 'operation_revision':
                assert value == 'continue'
                task_id = ctx['execution_to_review']['action']['target']
                provided = {row['id'] for row in ctx.get('tasks', [])}
                provided.update(row['id'] for row in ctx.get('task_catalog', []))
                if ctx.get('task'):
                    provided.add(ctx['task']['id'])
                assert task_id in provided, (task_id, provided)
                extensions(workspace, revision_requests=[{'record_ids': [task_id],
                    'reason': 'Replace the reviewed task contract with a narrower explicit domain.'}])
        elif event == 'kind_check':
            action = ctx['action']
            out['kind_definition_check'] = {'definition_id': action['kind_definition_id'],
                'definition_sha256': action['kind_definition_sha256'], 'decision': value,
                'findings': [] if value == 'approved' else ['The proposed kind needs a sharper boundary.']}
        elif event == 'impact':
            request = ctx['action']['input_basis']['impact_review']
            out['impact_review'] = {key: request[key] for key in
                ('integration_id', 'payload_sha256', 'producer_execution_id', 'input_snapshot')}
            out['impact_review']['plan_decisions'] = [{'scope': scope, 'plan_digest': plan['digest'],
                'decision': value, 'affected_ids': sorted(set(plan['computed_impact']) | set(plan['declared_impact'])),
                'reason': 'Compare the exact supplied mutation with its dependency scope.'}
                for scope, plan in request['plans'].items()]
        elif event == 'initial_diagnosis':
            assert ctx['initial_submission_diagnosis']['failed_execution']['status'] == 'ended'
            out['initial_submission_diagnosis'] = {'decision': value,
                'guidance': 'Read the current input and return the exact interpretation schema.'}
        elif event == 'delegation':
            out['delegation_judgment']['decision'] = value
        else:
            raise AssertionError('unknown cross event: ' + event)
        if armed:
            self.observed.append({'event': event, 'value': value, 'action': deepcopy(ctx['action']),
                'input': deepcopy(ctx), 'before': original, 'output': deepcopy(out)})
        return out


def responder(sim):
    if not isinstance(sim.model.responder, EventResponder):
        sim.model.responder = EventResponder(sim.model.responder)
    return sim.model.responder
