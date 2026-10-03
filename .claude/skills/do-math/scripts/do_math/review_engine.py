"""ResearchEngine integration for the finite independent identity-review cycle."""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path

from .values import compact_json_bytes, json_digest
from .execution_profiles import review_research
from .canonical import canonical_json, exact_content_hash
from .review_cycle import (accept_result, context_for, next_actions, record_turn, stage_schema, start_review,
                          defer_for_research, accept_research_result, research_schema, record_recovery_event,
                          authorize_record_replacement, reserved_review_slots, ReviewRestorationError,
                          validate_sealed_review, validate_review_binding, validate_review_independence,
                          replacement_authority, identity_assessment, review_action as _action,
                          resource_disposition, validate_resource_disposition, slot_key,
                          classify_research_source, review_proposal as _proposal, staged_review_candidate,
                          PROPOSAL_FIELDS, inline_source_row, inline_source_bytes)
from .input_basis import capture_review_input_basis, review_input_basis_changes
from . import knowledge_records as kr
from .review_policy import build_review_policy, minimum_scope_executions


def _pending_key(action):
    return f"{action['review_cycle_id']}:{slot_key(action)}"


def _seat_schema(cycle, action):
    """The stage schema of one pending seat, bound to its cycle's proposal digest."""
    schema = stage_schema(action['stage'])
    schema['properties']['proposal_digest']['enum'] = [cycle['proposal_digest']]
    return schema


def _independence_seat(action):
    """The seat that sealed replay passes to validate_review_independence for this action."""
    if action.get('role') == 'supplemental_research':
        return {'role': 'supplemental_research', 'research_request_id': action['research_request_id']}
    return _action(action)


class ReviewEngineMixin:
    """Mixin requiring ResearchEngine's state, queue, repository, and save methods.

    The owning engine saves cycle/knowledge/queue mutations atomically with the
    execution result. `_record_review_input` may also be called once an execution
    starts, so failed attempts retain the input that was actually delivered.
    """

    def _adopted_review_policy(self):
        policy = self.instance.get('review_policy')
        if policy is None:
            raise ValueError('adopted review policy is required before review admission')
        return build_review_policy(policy)

    def _assessment_reassessment_control(self, request):
        """ENGINE control dispatch calls this once before ordinary role requests."""
        spec = request.get('config', {}).get('assessment_reassessment')
        if spec is None:
            return None
        if request.get('action') != 'request' or request.get('config', {}).get('role') != 'identity_review':
            raise ValueError('assessment reassessment requires an identity_review request')
        result = self._start_assessment_reassessment(**spec)
        self.runtime.setdefault('history', []).append({'kind': 'assessment_reassessment_control',
            'request_id': request.get('id'), 'result': deepcopy(result)})
        return result

    def _reassessment_premises(self, knowledge_id):
        record = self.instance['knowledge'][knowledge_id]
        context_fields = ('id', 'lifecycle', 'kind_definition_id', 'kind_use_suspended', 'dependencies',
                          'source_basis', 'relation_claim', 'relation_endpoint_basis')
        return {**self._review_publication_premises(knowledge_id),
                'sources': deepcopy(self.instance.get('sources', [])),
                'knowledge_context': {key: deepcopy(record.get(key)) for key in context_fields},
                'kind_definition': deepcopy(self.instance.get('kind_definitions', {}).get(record.get('kind_definition_id'))),
                'dependency_uses': {identifier: kr.usable_links(self.instance, identifier) for identifier in record.get('dependencies', [])}}

    def _qualified_assessment_defect(self, assessment, original, evidence):
        """Only a reproducible lineage defect or a sealed independent objection qualifies."""
        kind = evidence.get('kind')
        if kind == 'author_context':
            eid = evidence.get('execution_id')
            if eid not in {row['execution_id'] for row in original['results'].values()}:
                return None
            from .governance import execution_lineage
            authors = set(original.get('producer_execution_ids', [])) | set(original['proposal'].get('producer_execution_ids', []))
            for current, row in execution_lineage(self.runtime, eid):
                if current in authors:
                    return {'kind': kind, 'execution_id': eid, 'author_execution_id': current,
                            'reason_refs': [eid, current], 'reason': 'Original reviewer inherited its proposal author context'}
                if row is None:
                    return None  # Missing records alone do not prove an incorrect judgment.
        elif kind == 'independent_objection':
            source = self.runtime.get('review_cycles', {}).get(evidence.get('review_cycle_id'))
            if source is None or source['id'] == original['id']:
                return None
            if source.get('proposal', {}).get('original_assessment') != assessment:
                return None  # Merely naming an IA in an output does not establish that it was read.
            from .knowledge import assessment_reassessment_proposal
            authors = set(assessment_reassessment_proposal(self.instance, assessment['id'], runtime=self.runtime)['producer_execution_ids']) | set(original.get('producer_execution_ids', []))
            validate_sealed_review(source, self.runtime, instance=self.instance, excluded_execution_ids=authors, clock=self.ports.clock, at=self.ports.clock.now())
            entry = source['results'].get(evidence.get('result_key'))
            if entry is None or evidence['result_key'] not in source['sealed']:
                return None
            finding = next((f for f in entry['output'].get('findings', []) + entry['output'].get('new_findings', [])
                            if f['id'] == evidence.get('finding_id')), None)
            if finding and finding.get('statement', '').strip() and 'assessment:' + assessment['id'] in finding.get('evidence', []):
                return {**deepcopy(evidence), 'reason_refs': [source['id'], entry['execution_id'], finding['id']],
                        'reason': finding['statement'], 'finding': deepcopy(finding)}
        return None

    def _start_assessment_reassessment(self, assessment_id, assessment_sha256, evidence):
        from .knowledge import assessment_reassessment_proposal, suspend_assessment_use
        from .activities import open_activity
        assessment = self.instance['identity_assessments'].get(assessment_id)
        if assessment is None or exact_content_hash(assessment) != assessment_sha256:
            raise ValueError('reassessment requires the exact original assessment')
        original = self.runtime.get('review_cycles', {}).get(assessment['review_cycle_id'])
        if not original or original['status'] == 'working' or original.get('assessment_id', assessment_id) != assessment_id:
            raise ValueError('original assessment has no completed review provenance')
        qualified = self._qualified_assessment_defect(assessment, original, evidence)
        if qualified is None:
            self.runtime.setdefault('history', []).append({'kind': 'assessment_report', 'assessment_id': assessment_id,
                'assessment_sha256': assessment_sha256, 'evidence': deepcopy(evidence), 'disposition': 'report_only'})
            return {'disposition': 'report_only', 'assessment_id': assessment_id, 'next_owner': 'independent_review'}
        use = next(row for row in self.instance['assessment_uses'].values() if row['assessment_id'] == assessment_id)
        if use['status'] == 'withdrawn':
            raise ValueError('a withdrawn assessment cannot be reopened as active')
        for cid, cycle in self.runtime.get('review_cycles', {}).items():
            spec = cycle['proposal'].get('assessment_reassessment', {})
            if spec.get('assessment_id') == assessment_id and cycle['proposal'].get('defect_evidence') == qualified:
                return {'disposition': 'already_open' if cycle['status'] == 'working' else 'already_reviewed',
                        'review_cycle_id': cid, 'assessment_id': assessment_id}
        knowledge_id = original['knowledge_id']
        policy = build_review_policy(original['review_policy'])
        proposal = assessment_reassessment_proposal(self.instance, assessment_id, runtime=self.runtime)
        proposal['producer_execution_ids'] = sorted(set(proposal['producer_execution_ids']) | set(original.get('producer_execution_ids', [])))
        proposal.update(original_assessment=deepcopy(assessment), original_policy=deepcopy(policy),
            original_proposal=deepcopy(original['proposal']),
            original_sealed_results={k: deepcopy(original['results'][k]) for k in original['sealed']},
            current_premises=self._reassessment_premises(knowledge_id),
            original_premises=deepcopy(original.get('publication_premises', {})), defect_evidence=qualified)
        cycle = start_review(proposal, policy['minimum_initial_slots'], policy['judge_slots'], policy['round_limit'], policy=policy)
        cid, owner = self.ports.clock.new_id('RC'), self.ports.clock.new_id('AT')
        cycle.update(id=cid, knowledge_id=knowledge_id, owner_activity_id=owner,
            identity_basis=deepcopy(assessment['basis']), policy_ref=assessment['policy_ref'], input_snapshot=self.head,
            publication_premises=deepcopy(proposal['current_premises']), producer_execution_ids=proposal['producer_execution_ids'],
            slot_profiles={}, input_bindings={})
        cycle['review_input_basis'] = capture_review_input_basis(cycle)
        instance, runtime = suspend_assessment_use(self.instance, self.runtime, assessment_id,
            reason=qualified['reason'], actor_ref=cid, reason_refs=qualified['reason_refs'], clock=self.ports.clock)
        runtime.setdefault('review_cycles', {})[cid] = cycle
        open_activity(runtime, activity_id=owner, activity_kind='identity_review', owner_ref=assessment_id,
            input_refs=[assessment_id, original['id']], opened_at=self.ports.clock.now(),
            execution_limit=policy['activity_execution_limit'])
        self.instance, self.runtime = instance, runtime
        self._queue_identity_actions(knowledge_id, cid)
        return {'disposition': 'reassessment_opened', 'assessment_id': assessment_id,
                'review_cycle_id': cid, 'owner_activity_id': owner, 'status': 'suspended'}

    def _publish_assessment_reassessment(self, action, cycle, execution_id):
        from .knowledge import apply_assessment_reassessment
        self._review_cycle(action)
        validate_sealed_review(cycle, self.runtime, instance=self.instance, read_artifact=self.store.read,
                               git_dir=self.store.git_dir, clock=self.ports.clock, at=self.ports.clock.now())
        aid = cycle['proposal']['assessment_reassessment']['assessment_id']
        self.instance, self.runtime = apply_assessment_reassessment(self.instance, self.runtime, aid, cycle['id'],
            reason='Sealed independent reassessment of the original judgment: ' + cycle['decision'], actor_ref=execution_id, clock=self.ports.clock, at=self.ports.clock.now())
        use = next(u for u in self.instance['assessment_uses'].values() if u['assessment_id'] == aid)
        conditions = ['new qualified defect evidence', 'changed judgment target or premises', 'explicit source-bound review authority']
        result = {'assessment_id': aid, 'review_cycle_id': cycle['id'], 'status': use['status'],
                  'decision': cycle['decision'], 'next_owner': 'research_plan', 'revisit_conditions': conditions}
        self.runtime['review_cycles'][cycle['id']]['history'].append({'event': 'assessment_reassessment_applied', **result})
        self.runtime['queue'][:] = [a for a in self.runtime['queue'] if a.get('review_cycle_id') != cycle['id']]
        self._enqueue('research_plan', reason='Consume original judgment reassessment and downstream effects', identity_review=result)
        return result

    def _settle_assessment_reassessments(self):
        """After real EX termination/reload, finish bounded work and retain its next owner."""
        from .activities import finish_activity
        settled = []
        for cid, cycle in self.runtime.get('review_cycles', {}).items():
            if not cycle['proposal'].get('assessment_reassessment') or cycle['status'] == 'working':
                continue
            applied = next((h for h in reversed(cycle['history']) if h.get('event') == 'assessment_reassessment_applied'), None)
            activity = self.runtime.get('activities', {}).get(cycle.get('owner_activity_id'))
            if not applied or not activity or activity['status'] == 'finished':
                continue
            if any(e.get('status') != 'ended' and e.get('owner_activity_id') == activity['id'] for e in self.runtime['executions'].values()):
                continue
            followup = {k: deepcopy(v) for k, v in applied.items() if k != 'event'}
            finish_activity(self.runtime, activity['id'], result_refs=[cid, applied['assessment_id']],
                unresolved=[followup] if applied['status'] == 'suspended' else [], followups=[followup],
                at=self.ports.clock.now())
            settled.append(cid)
        return settled

    def _start_staged_identity_review(self, transition_id, knowledge_id):
        candidate = staged_review_candidate(self.instance, self.runtime, transition_id, knowledge_id)
        policy = self._adopted_review_policy()
        for cid, prior in self.runtime.get('review_cycles', {}).items():
            if prior.get('transition_id') == transition_id and prior.get('knowledge_id') == knowledge_id:
                if prior.get('staged_candidate') != candidate:
                    raise ValueError('staged review candidate changed; do not reuse its old review')
                self._review_cycle({'role': 'identity_review', 'target': knowledge_id, 'review_cycle_id': cid})
                self._queue_identity_actions(knowledge_id, cid)
                return cid
        cycle = start_review(candidate['proposal'], reviewers=policy['minimum_initial_slots'],
            judges=policy['judge_slots'], max_rounds=policy['round_limit'], policy=policy)
        cid = self.ports.clock.new_id('RC')
        cycle.update(id=cid, knowledge_id=knowledge_id, transition_id=transition_id,
            staged_candidate=candidate, identity_basis=deepcopy(candidate['identity_basis']), input_snapshot=self.head,
            producer_execution_ids=list(dict.fromkeys([
                *([self.instance['knowledge'][knowledge_id]['producer_execution']] if self.instance['knowledge'][knowledge_id].get('producer_execution') else []),
                *([self.runtime['trust_transitions'][transition_id]['results'][knowledge_id]['execution_id']]
                  if self.runtime['trust_transitions'][transition_id]['results'][knowledge_id].get('execution_id') else [])])),
            slot_profiles={}, input_bindings={},
            policy_ref=policy['id'] + ':' + exact_content_hash(policy),
            publication_premises=self._review_publication_premises(knowledge_id))
        cycle['review_input_basis'] = capture_review_input_basis(cycle)
        self.runtime.setdefault('review_cycles', {})[cid] = cycle
        self._queue_identity_actions(knowledge_id, cid)
        return cid

    def _completed_staged_identity_review(self, transition_id, knowledge_id, cycle_id):
        cycle = self.runtime['review_cycles'][cycle_id]
        if cycle.get('transition_id') != transition_id or cycle.get('knowledge_id') != knowledge_id:
            raise ValueError('staged review belongs to another transition target')
        self._review_cycle({'role': 'identity_review', 'target': knowledge_id, 'review_cycle_id': cycle_id})
        if cycle['status'] != 'completed' or cycle.get('decision') != 'match':
            raise ValueError('staged identity review has no completed match')
        assessment = identity_assessment(cycle, reason='Sealed staged identity review')
        return {**assessment, 'policy_ref': cycle['policy_ref'], 'identity_basis': deepcopy(cycle['identity_basis']),
                'transition_id': transition_id, 'knowledge_id': knowledge_id,
                'transition_basis': cycle['staged_candidate']['transition_basis']}


    def _admit_review_execution(self, action, execution):
        """Reserve an actual AI attempt before runner start; ENGINE owns registration."""
        cid = action.get('review_cycle_id') or action.get('owner_review_cycle_id')
        if not cid or execution.get('actor_kind') != 'ai':
            return {'disposition': 'not_applicable'}
        cycle = self.runtime['review_cycles'][cid]
        if resource_disposition(cycle):
            return {'disposition': 'review_resource_pending', 'cycle_id': cid}
        eid, owner = execution['id'], execution.get('owner_activity_id')
        accounting = cycle['execution_accounting']
        admissions = accounting.get('admissions', {})
        binding = {'action': deepcopy(action), 'owner_activity_id': owner}
        if eid in admissions:
            # Admission checked this attempt; its result is checked again when it is accepted.
            if {key: value for key, value in admissions[eid].items() if key != 'delegation_authority'} != binding:
                raise ValueError('review execution admission identity changed')
            return {'disposition': 'already_admitted', 'execution_id': eid}
        self._review_cycle({'role': 'identity_review', 'target': cycle['knowledge_id'], 'review_cycle_id': cid})
        projected = {**self.runtime, 'executions': {**self.runtime.get('executions', {}), eid: execution}}
        validate_review_independence(cycle, projected, eid, _independence_seat(action))
        changes = review_input_basis_changes(cycle.get('review_input_basis', {}), cycle)
        if changes:
            raise ValueError('review inputs changed before admission: ' + json.dumps(changes, ensure_ascii=False))
        if not owner or (cycle.get('owner_activity_id') is not None and cycle['owner_activity_id'] != owner):
            raise ValueError('review admission requires its actual owner activity')
        authority = self._review_replacement_authority(action)
        if authority is not None and not authority['allowed']:
            return {'disposition': 'authorization_denied', 'authority': authority}
        delegation_authority = self._delegation_authority_binding(cycle, action)
        if delegation_authority is not None:
            binding['delegation_authority'] = delegation_authority
        assigned = [key for key, row in self.runtime.get('executions', {}).items()
                    if row.get('owner_activity_id') == owner and row.get('actor_kind') == 'ai' and key != eid]
        used = list(dict.fromkeys([*accounting['executions_used'], *assigned]))
        reserved = reserved_review_slots(cycle, self.runtime.get('executions', {}))
        accounting['executions_used'] = used
        limit = cycle['activity_execution_limit']
        outcome = {'execution_id': eid, 'used': len(used), 'limit': limit,
                   'reserved_execution_slots': deepcopy(reserved), 'owner_activity_id': owner}
        if cycle.get('owner_activity_id') is None:
            cycle['owner_activity_id'] = owner
            cycle['review_input_basis'] = capture_review_input_basis(cycle)
        if len(used) >= limit:
            return {**outcome, 'disposition': 'review_budget_exhausted'}
        if action.get('stage') == 'scope':
            required = minimum_scope_executions(max(cycle['review_policy']['minimum_initial_slots'],
                len(cycle['retained_reviewer_slots'])), cycle['max_rounds'], len(used) + 1)
            if required > limit:
                return {**outcome, 'disposition': 'review_scope_unaffordable', 'minimum_required': required}
        if action.get('role') != 'identity_review' and (len(used) + 1 + len(reserved) > limit):
            return {**outcome, 'disposition': 'review_followup_reserved'}
        activity = self.runtime.get('activities', {}).get(owner)
        if activity is not None:
            activity['execution_limit'] = limit
        admissions[eid] = binding
        accounting['admissions'] = admissions
        accounting['executions_used'].append(eid)
        return {**outcome, 'disposition': 'admitted'}

    def _request_review_resource_disposition(self, action, reason, detail):
        """Stop only this review's attempts, then hand its actual evidence to planning."""
        cycle = self.runtime['review_cycles'][action.get('review_cycle_id') or action['owner_review_cycle_id']]
        record = resource_disposition(cycle)
        if record is None:
            record = {'event': 'review_resource_disposition', 'state': 'draining', 'reason': reason,
                'proposal_digest': cycle['proposal_digest'], 'policy': deepcopy(cycle['review_policy']),
                'limit': cycle['activity_execution_limit'],
                'executions_used': list(cycle['execution_accounting']['executions_used']),
                'pending_actions': next_actions(cycle), 'detail': deepcopy(detail),
                'disposition': cycle['review_policy']['overflow_disposition'],
                'at': self.ports.clock.now()}
            cycle['history'].append(record)
        validate_resource_disposition(cycle, self.runtime)
        self.runtime['queue'][:] = [row for row in self.runtime['queue']
            if (row.get('review_cycle_id') or row.get('owner_review_cycle_id')) != cycle['id']]
        for key, waiting in list(self.runtime.get('waiting_actions', {}).items()):
            held = waiting.get('action', {})
            if (held.get('review_cycle_id') or held.get('owner_review_cycle_id')) == cycle['id']:
                self.runtime['waiting_actions'].pop(key)
        for eid in cycle['execution_accounting']['executions_used']:
            execution = self.runtime['executions'][eid]
            if execution['status'] != 'ended':
                execution['stop_requested'] = 'review_resource_disposition'
        self._settle_review_resource_dispositions()

    def _settle_review_resource_dispositions(self):
        from .activities import finish_activity, wait_for
        changed = []
        for cid, cycle in self.runtime.get('review_cycles', {}).items():
            record = resource_disposition(cycle)
            if not record or record['state'] == 'ended':
                continue
            activity = self.runtime['activities'][cycle['owner_activity_id']]
            if any(self.runtime['executions'][eid]['status'] != 'ended'
                   for eid in activity['assigned_execution_ids']):
                continue
            from .session_slots import held_reservations
            if held_reservations(self.runtime, activity['assigned_execution_ids']):
                continue
            # A deferred review stays frozen until its proposal really changes or
            # is withdrawn. Elapsed time and newly free slots cannot reset it.
            item = self.instance['knowledge'].get(cycle['knowledge_id'], {})
            superseded = (item.get('lifecycle') in {'withdrawn', 'superseded'}
                or item.get('exposition_id') != cycle['proposal'].get('exposition_id')
                or item.get('review_cycle_id') not in {None, cid})
            closed = self._instance_closed()
            if record['state'] == 'deferred' and not superseded and not closed:
                continue
            stamp = self.ports.clock.now()
            followup = {'cycle_id': cid, 'knowledge_id': cycle['knowledge_id'], 'reason': record['reason'],
                        'next_owner': 'research_plan', 'proposal_digest': cycle['proposal_digest']}
            if record['state'] == 'draining':
                cycle['followup'].append(deepcopy(followup))
                if not closed:
                    self._enqueue('research_plan', reason='Review resources cannot complete the fixed proposal',
                                  evidence_refs=[cid, cycle['knowledge_id']])
            if record['disposition'] == 'defer' and not superseded and not closed:
                record['state'] = 'deferred'
                activity['unresolved'] = [deepcopy(followup)]
                activity['followups'] = [deepcopy(followup)]
                wait_for(self.runtime, activity['id'], reason='review_resource_deferred',
                    condition={'cycle_id': cid, 'proposal_digest': cycle['proposal_digest']}, next_owner='research_plan', at=stamp)
            else:
                record.update(state='ended', ended_at=stamp)
                if superseded or closed:
                    record['resolution'] = {'kind': 'instance_ended' if closed else 'proposal_superseded', 'knowledge_id': item.get('id'),
                                            'exposition_id': item.get('exposition_id')}
                cycle.update(status='unresolved', decision='unresolved', phase='ended')
                finish_activity(self.runtime, activity['id'], result_refs=[cid], unresolved=[followup],
                                followups=[followup], at=stamp)
            validate_resource_disposition(cycle, self.runtime)
            changed.append(cid)
        return changed

    def _start_identity_review(self, knowledge_id, previous_cycle_id=None):
        self._settle_review_resource_dispositions()
        item = self.instance['knowledge'][knowledge_id]
        cycles = self.runtime.setdefault('review_cycles', {})
        current_id = item.get('review_cycle_id')
        if previous_cycle_id is None and current_id in cycles:
            current = cycles[current_id]
            if _proposal(self.instance, knowledge_id) != current['proposal']:
                raise ValueError('sealed review proposal changed; submit an explicit new revision')
            self._review_cycle({'role': 'identity_review', 'target': knowledge_id, 'review_cycle_id': current_id})
            self._queue_identity_actions(knowledge_id, current_id)
            return current_id
        previous = cycles.get(previous_cycle_id) if previous_cycle_id else None
        if previous_cycle_id and previous is None:
            raise ValueError('previous review cycle does not exist')
        if previous is not None and previous['status'] == 'working':
            raise ValueError('finish or explicitly close the prior review before revising')
        if previous is not None and previous.get('knowledge_id') != knowledge_id:
            # A revised proposal may have a new knowledge ID, but the explicit
            # revision relation must identify the source item.
            if item.get('supersedes') != previous.get('knowledge_id'):
                raise ValueError('revision must name the previous knowledge item')
        policy = self._adopted_review_policy()
        reviewers = policy['minimum_initial_slots']
        if previous is not None and previous['reviewer_slots']:
            reviewers = list(previous['reviewer_slots'])
        round_limit = policy['round_limit']
        cycle = start_review(_proposal(self.instance, knowledge_id), reviewers=reviewers, max_rounds=round_limit,
                             judges=previous['judge_slots'] if previous else 3, previous=previous,
                             policy=policy)
        cycle_id = self.ports.clock.new_id('RC')
        cycle.update(id=cycle_id, knowledge_id=knowledge_id, input_snapshot=self.head,
                     producer_execution_ids=list(dict.fromkeys([*(previous.get('producer_execution_ids', []) if previous else []),
                                                *([item['producer_execution']] if item.get('producer_execution') else [])])))
        cycle['identity_basis'] = kr.identity_basis(self.instance, knowledge_id)
        cycle['slot_profiles'] = deepcopy(previous.get('slot_profiles', {})) if previous else {}
        cycle['input_bindings'] = deepcopy(previous.get('input_bindings', {})) if previous else {}
        cycle['policy_ref'] = cycle['review_policy']['id'] + ':' + exact_content_hash(cycle['review_policy'])
        cycle['publication_premises'] = self._review_publication_premises(knowledge_id)
        cycle['review_input_basis'] = capture_review_input_basis(cycle)
        cycles[cycle_id] = cycle
        item['review_cycle_id'] = cycle_id
        self._queue_identity_actions(knowledge_id, cycle_id)
        return cycle_id

    def _reconcile_review_host_profiles(self):
        """A changed host approval cannot silently rewrite a frozen review profile."""
        from .execution_profiles import match_profile_ref
        changed = []
        approved = self.instance.get('host_capacity_ref')
        expected = [approved] if approved else []
        for cid, cycle in self.runtime.get('review_cycles', {}).items():
            if cycle['status'] != 'working' or resource_disposition(cycle):
                continue
            references = [*(cycle.get('slot_profiles') or {}).values(),
                          (cycle.get('scope_assessment') or {}).get('selected_profile_ref')]
            references += [self.runtime['executions'][eid].get('execution_profile_ref')
                           for eid in cycle['execution_accounting']['executions_used']]
            mismatched = [ref for ref in references if ref is not None
                and match_profile_ref(self.instance['execution_profiles'], ref).get('host_capacity_refs', []) != expected]
            if not mismatched:
                continue
            if not cycle.get('owner_activity_id'):
                action = next((a for a in self.runtime['queue'] if a.get('review_cycle_id') == cid),
                    {'id': self.ports.clock.new_id('AC'), 'role': 'identity_review', 'target': cycle['knowledge_id'], 'review_cycle_id': cid})
                cycle['owner_activity_id'] = self._activity_for_action(action)['id']
                cycle['review_input_basis'] = capture_review_input_basis(cycle)
            self._request_review_resource_disposition({'review_cycle_id': cid}, 'review_host_configuration_changed',
                {'profile_refs': mismatched, 'adopted_host_ref': approved})
            changed.append(cid)
        return changed

    def _review_publication_premises(self, knowledge_id):
        return kr.review_publication_premises(self.instance, knowledge_id)

    def _queue_identity_actions(self, knowledge_id, cycle_id):
        cycle = self.runtime['review_cycles'][cycle_id]
        for action in next_actions(cycle):
            exists = any(queued.get('role') == 'identity_review' and
                         queued.get('review_cycle_id') == cycle_id and
                         all(queued.get(key) == value for key, value in action.items())
                         for queued in self.runtime['queue'])
            held = any(entry.get('action', {}).get('role') == 'identity_review'
                       and entry['action'].get('review_cycle_id') == cycle_id
                       and all(entry['action'].get(key) == value for key, value in action.items())
                       for entry in self.runtime.get('waiting_actions', {}).values())
            if not exists and not held:
                assignment = {}
                if cycle.get('transition_id'):
                    assignment['transition_id'] = cycle['transition_id']
                if cycle.get('owner_activity_id'):
                    assignment['owner_activity_id'] = cycle['owner_activity_id']
                profile = cycle.get('slot_profiles', {}).get(action['slot']) or (cycle.get('scope_assessment') or {}).get('selected_profile_ref')
                if profile is not None:
                    assignment['profile_ref'] = deepcopy(profile)
                self._enqueue('identity_review', knowledge_id, review_cycle_id=cycle_id, **action, **assignment)

    def _obsolete_review_reason(self, action):
        cycle_id = action.get('review_cycle_id')
        if not cycle_id or action['role'] not in {'identity_review', 'supplemental_research'}:
            return None
        cycle = self.runtime.get('review_cycles', {}).get(cycle_id)
        if cycle and resource_disposition(cycle):
            return 'The review is preserving an incomplete resource disposition for planning'
        item = self.instance['knowledge'].get(action.get('target'), {})
        if not cycle or cycle.get('status') != 'working' or (not cycle.get('transition_id') and not cycle['proposal'].get('assessment_reassessment') and item.get('review_cycle_id') != cycle_id):
            return 'The assigned review ended or its proposal revision was superseded'
        if action['role'] == 'identity_review' and _action(action) not in next_actions(cycle):
            return 'The assigned review slot is no longer pending'
        if action['role'] == 'supplemental_research' and cycle.get('research', {}).get(action.get('research_request_id'), {}).get('status') != 'pending':
            return 'The fixed investigation is no longer pending'
        return None

    def _review_cycle(self, action):
        if action.get('role') != 'identity_review':
            raise ValueError('action is not an identity review')
        cycle = self.runtime.get('review_cycles', {}).get(action.get('review_cycle_id'))
        if cycle is None or cycle.get('knowledge_id') != action.get('target'):
            raise ValueError('review action refers to another or missing proposal')
        item = self.instance['knowledge'][action['target']]
        reassessment = cycle['proposal'].get('assessment_reassessment')
        if reassessment is not None:
            from .knowledge import assessment_reassessment_proposal
            expected = assessment_reassessment_proposal(self.instance, reassessment['assessment_id'], runtime=self.runtime)
            if reassessment != expected['assessment_reassessment']:
                raise ValueError('reassessment exact original judgment changed')
            if cycle['publication_premises'] != self._reassessment_premises(action['target']):
                raise ValueError('reassessment current premises changed; preserve suspension and request a new basis')
            return cycle
        if cycle.get('transition_id'):
            current = staged_review_candidate(self.instance, self.runtime, cycle['transition_id'], action['target'])
            if current != cycle.get('staged_candidate') or current['proposal'] != cycle['proposal']:
                raise ValueError('staged review candidate changed')
            if cycle.get('publication_premises') != self._review_publication_premises(action['target']):
                raise ValueError('staged review publication premises changed')
            return cycle
        if item.get('review_cycle_id') != action['review_cycle_id']:
            raise ValueError('review action belongs to a superseded proposal revision')
        live = _proposal(self.instance, action['target'])
        if any(live[name] != cycle['proposal'][name] for name in PROPOSAL_FIELDS):
            raise ValueError('sealed mathematical proposal changed during review')
        if cycle.get('publication_premises') != self._review_publication_premises(action['target']):
            raise ValueError('review publication premises changed: formal, exposition, trust or policy')
        return cycle

    def _review_schema(self, action):
        cycle = self._review_cycle(action)
        if _action(action) not in next_actions(cycle):
            raise ValueError('review action is not pending')
        return _seat_schema(cycle, action)

    def _prepare_review_context(self, action, workspace: Path, *, sources=None):
        """Return a runnable context or an activity-owned recovery disposition.

        ENGINE must branch on this result before it creates a provider execution.
        A failed reconstruction is already durable state, not an exception that
        should escape and be retried as though nothing had been recorded.
        """
        cycle = self._review_cycle(action)
        key = slot_key(action)
        if key in cycle.get('blocked_actions', {}) and key not in cycle.get('replacement_actions', {}):
            event = cycle['recovery_events'][cycle['blocked_actions'][key]]
            return {'disposition': 'recovery_recorded', 'recovery': {
                'disposition': 'replacement_authorization_required', 'review_cycle_id': cycle['id'],
                'action': _action(action), 'recovery_event': deepcopy(event), 'owner_activity_id': cycle.get('owner_activity_id'),
                'next_owner': 'governance', 'review_status': cycle['status'], 'review_closure': 'not_closed'}}
        authority = self._review_replacement_authority(action)
        if authority is not None and not authority['allowed']:
            return {'disposition': 'authorization_denied', 'authority': authority,
                    'recovery': {'disposition': 'authorization_denied', 'authority': authority,
                                 'action': _action(action), 'review_cycle_id': action['review_cycle_id'],
                                 'next_owner': 'governance', 'review_closure': 'not_closed'},
                    'review_cycle_id': action['review_cycle_id'], 'action': _action(action)}
        try:
            return {"disposition": "ready", "context": self._build_review_context(action, workspace, cycle, sources=sources)}
        except ReviewRestorationError as error:
            return {'disposition': 'recovery_recorded',
                    'recovery': self._record_review_recovery(action, error, retryable=error.diagnostics['retryable'])}
        except OSError as error:
            import errno
            retryable = error.errno in {errno.EAGAIN, errno.EINTR, errno.EBUSY, errno.ETIMEDOUT}
            return {'disposition': 'recovery_recorded',
                    'recovery': self._record_review_recovery(action, error, retryable=retryable)}


    def _delegation_authority_binding(self, cycle, action):
        """Seal the applied delegation behind a replacement slot, if one authorizes it."""
        if action.get('replacement_for') is None:
            return None
        replacement = cycle['replacement_actions'][slot_key(action)]
        if not replacement.get('delegation_id'):
            return None
        app = self.runtime['delegation_applications'][replacement['case']['application_id']]
        return {'application_id': app['id'], 'application_sha256': exact_content_hash(app),
                'judgment_executions': {j['execution_id']: exact_content_hash(self.runtime['executions'][j['execution_id']])
                                        for j in app['judgments'].values()}}

    def _review_replacement_authority(self, action, execution_id=None):
        if action.get('replacement_for') is None:
            return None
        cycle = self._review_cycle(action)
        key = slot_key(action)
        replacement = cycle.get('replacement_actions', {}).get(key)
        if replacement is None or replacement['action'] != _action(action):
            return {'allowed': False, 'reason': 'replacement does not match the authorized slot'}
        return replacement_authority(self.instance, self.runtime, cycle, replacement, execution_id, clock=self.ports.clock, at=self.ports.clock.now())

    def _build_review_context(self, action, workspace: Path, cycle, *, sources=None):
        """cycle is the current cycle _prepare_review_context has just checked."""
        changes = review_input_basis_changes(cycle.get('review_input_basis', {}), cycle)
        if changes:
            raise ValueError('review policy, scope, profile, or activity input changed: ' + json.dumps(changes, ensure_ascii=False))
        owner = action.get('owner_activity_id')
        if owner is not None and cycle.get('owner_activity_id') is None:
            cycle = deepcopy(cycle)
            cycle['owner_activity_id'] = owner
            cycle['review_input_basis'] = capture_review_input_basis(cycle)
            self.runtime['review_cycles'][action['review_cycle_id']] = cycle
        elif owner is not None and owner != cycle.get('owner_activity_id'):
            raise ValueError('review action changed its owner activity')
        context = context_for(cycle, _action(action))
        for investigation in context.get('supplemental_results', []):
            investigation['source_records'] = self._materialize_research_sources(investigation.get('source_records', []), workspace, slot=action['slot'])
            investigation['result']['source_records'] = self._materialize_research_sources(investigation['result'].get('source_records', []), workspace, slot=action['slot'])
        directory = (workspace / 'input' / 'review-sources').resolve()
        workspace = workspace.resolve()
        if not directory.is_relative_to(workspace):
            raise ValueError('review source directory escapes workspace')
        directory.mkdir(parents=True, exist_ok=True)
        references = {}
        for reference in context['source_refs']:
            # context_for matched each referenced message with its manifest row (validate_transcript).
            slot, index = reference['slot'], reference['index']
            raw = compact_json_bytes(cycle['turns'][slot][index])
            path = directory / f"{reference['sha256']}.json"
            if not path.resolve().is_relative_to(directory):
                raise ValueError('review source file escapes its materialization directory')
            if path.exists() and path.read_bytes() != raw:
                raise ReviewRestorationError('immutable review source path contains different bytes', cause_kind='materialized_content_mismatch',
                    coordinate={'slot': slot, 'index': index, 'path': str(path)}, expected_sha256=reference['sha256'],
                    observed_sha256=hashlib.sha256(path.read_bytes()).hexdigest(), verified_indices=range(len(cycle['turns'][slot])))
            path.write_bytes(raw)
            reference['local_path'] = path.relative_to(workspace).as_posix()
            references[reference['ref']] = deepcopy(reference)
        for message in context['self_messages']:
            content = message.get('content')
            if isinstance(content, dict) and 'source_ref' in content:
                content['source_ref'] = deepcopy(references[content['source_ref']['ref']])
        context['output_schema'] = _seat_schema(cycle, action)
        context['review_cycle_id'] = action['review_cycle_id']
        context['snapshot'] = cycle['input_snapshot']
        context['identity_basis'] = deepcopy(cycle['identity_basis'])
        context['policy_ref'] = cycle['policy_ref']
        context['source_instructions'] = ('Read each referenced source through its local_path when needed. '
            'The JSON file contains the exact original public message; its content is the original source body. '
            'Compare the complete current proposal. Prior revision judgments do not approve this revision.')
        context['research_request_contract'] = {
            'extension_file': 'activity-extensions.json',
            'field': 'research_requests',
            'item': {'id': 'local request ID', 'question': 'One fixed question to investigate',
                     'source_refs': ['proposal or proposal:<field.path>, issue:<id>, supplied source ref, or readable knowledge ID']},
            'remaining_requests': max(0, self.instance['config']['review_research_limit'] - len(cycle.get('research', {}))),
            'instructions': 'If investigation is necessary, write research_requests and return unresolved provisionally for initial/judge. The slot is deferred without sealing a verdict; all requested answers return to this same slot. Use an existing answer when it resolves the question. Investigation cannot replace your final complete review.'}
        # This is the new request, excluding the restored transcript. Appending the
        # complete rendered prompt here would recursively duplicate old messages.
        request = {key: deepcopy(value) for key, value in context.items()
                   if key not in ('proposal', 'self_messages', 'output_schema')}
        request['action'] = deepcopy(action)
        prepared = {'proposal_digest': cycle['proposal_digest'], 'proposal': deepcopy(context['proposal']),
                    'restored_messages': deepcopy(context['self_messages']),
                    'request': request, 'slot': action['slot'],
                    'visible_execution_ids': [entry['execution_id'] for entry in context['completed_results'].values()] +
                                             [entry['result']['execution_id'] for entry in context.get('supplemental_results', [])],
                    'workspace': str(workspace), 'supplied_sources': deepcopy(sources if sources is not None else self.instance.get('sources', [])),
                    'source_snapshot': self.head}
        self.runtime.setdefault('review_inputs', {})[_pending_key(action)] = prepared
        return context

    def _record_review_recovery(self, action, error, *, retryable, preserved_range=None):
        """Persist a slot-local restoration fact and describe the next owner."""
        cycle = self._review_cycle(action)
        event = {'reason': str(error), 'error_type': type(error).__name__, 'retryable': retryable,
                 'cause_kind': 'io_failure' if isinstance(error, OSError) else 'restoration_failure',
                 'coordinate': {'slot': action.get('slot'), **({'path': error.filename, 'errno': error.errno} if isinstance(error, OSError) else {})},
                 'preserved_range': preserved_range or {'slot': action.get('slot'), 'verified_indices': []}}
        if isinstance(error, OSError):
            event['continuity_broken'] = False
        event.update(deepcopy(getattr(error, 'diagnostics', {})))
        updated = record_recovery_event(cycle, _action(action), event)
        self.runtime['review_cycles'][action['review_cycle_id']] = updated
        self.runtime.setdefault('history', []).append({"kind": "review_recovery_recorded", "review_cycle_id": action['review_cycle_id'],
                                                       "action": _action(action), "reason": event['reason'], "retryable": retryable})
        recovery = updated['recovery_events'][-1]
        return {"disposition": "slot_restore_retry" if retryable else "replacement_authorization_required",
                "review_cycle_id": action['review_cycle_id'], "action": _action(action),
                "recovery_event": deepcopy(recovery), "owner_activity_id": updated.get('owner_activity_id'),
                "review_status": updated['status'], "review_closure": "not_closed",
                'next_owner': 'review_recovery' if retryable else 'governance'}

    def _authorize_review_replacement(self, action, *, grant_id=None, delegation_id=None, case=None, at=None):
        """Apply the current GOVERNANCE authorization result without creating a run."""
        at = self.ports.clock.now() if at is None else at
        cycle = self._review_cycle(action)
        outcome = authorize_record_replacement(cycle, _action(action), self.instance, runtime=self.runtime,
                                               grant_id=grant_id, delegation_id=delegation_id, case=case, at=at, clock=self.ports.clock)
        if delegation_id is not None and outcome['disposition'] == 'replacement_ready' and outcome['cycle'] is not cycle:
            from .delegations import apply_application
            def install(instance, runtime, effect):
                runtime['review_cycles'][action['review_cycle_id']] = outcome['cycle']
                return instance, runtime
            self.instance, self.runtime, _ = apply_application(self.instance, self.runtime, case['application_id'],
                                                               apply_effect=install, now_iso=at)
        if outcome['cycle'] is not cycle:
            self.runtime['review_cycles'][action['review_cycle_id']] = outcome['cycle']
        if outcome['disposition'] == 'replacement_ready':
            self._release_review_wait(action, at=at)
            self.runtime['queue'][:] = [a for a in self.runtime['queue'] if not (
                a.get('review_cycle_id') == action['review_cycle_id'] and
                all(a.get(k) == action.get(k) for k in ('stage', 'slot', 'round')))]
            self._queue_identity_actions(action['target'], action['review_cycle_id'])
        self.runtime.setdefault('history', []).append({"kind": "review_replacement_disposition",
            "review_cycle_id": action['review_cycle_id'], "action": _action(action),
            "disposition": outcome['disposition'], "grant_id": outcome.get('authority', {}).get('grant_id'),
            "reason": outcome.get('reason')})
        return outcome

    def _release_review_wait(self, action, *, at=None):
        """Resolve only this slot's restoration wait through the activity owner API."""
        from . import activities
        at = at or self.ports.clock.now()
        waits = self.runtime.setdefault('waiting_actions', {})
        released = []
        for identifier, entry in list(waits.items()):
            held = entry.get('action', {})
            if (entry.get('kind') in {'review_input_restoration', 'review_recovery', 'review_authority'} and
                    all(held.get(key) == action.get(key) for key in ('review_cycle_id', 'stage', 'round', 'slot'))):
                released.append(identifier)
                del waits[identifier]
        cycle = self.runtime['review_cycles'][action['review_cycle_id']]
        owner = cycle.get('owner_activity_id') or action.get('owner_activity_id')
        activity = self.runtime.get('activities', {}).get(owner)
        if activity and activity['status'] == 'waiting':
            waiting = activity['waiting']
            condition = waiting.get('condition', {})
            recovery = condition.get('recovery', {}) if isinstance(condition, dict) else {}
            held = recovery.get('action', {})
            matching = (recovery.get('review_cycle_id') == action['review_cycle_id'] and
                        all(held.get(k) == action.get(k) for k in ('stage', 'round', 'slot')))
            action_ids = condition.get('action_ids', []) if isinstance(condition, dict) else []
            matching = matching or bool(set(action_ids) & set(released))
            if matching:
                activities.resume_activity(self.runtime, owner, condition=deepcopy(condition), at=at)
        self.runtime.setdefault('history', []).append({'kind': 'review_wait_resolved',
            'review_cycle_id': action['review_cycle_id'], 'action': _action(action), 'waiting_action_ids': released, 'at': at})
        return released

    def _retry_review_restoration(self, action, workspace, *, at=None):
        """Recheck recovered exact bytes; successful verification reopens the held action."""
        cycle = self._review_cycle(action)
        key = slot_key(action)
        blocked = cycle.get('blocked_actions', {}).pop(key, None)
        try:
            outcome = self._prepare_review_context(action, workspace)
        except (ValueError, KeyError):
            if blocked is not None:
                cycle['blocked_actions'][key] = blocked
            raise
        if outcome['disposition'] != 'ready':
            if blocked is not None and key not in self.runtime['review_cycles'][cycle['id']]['blocked_actions']:
                self.runtime['review_cycles'][cycle['id']]['blocked_actions'][key] = blocked
            return outcome
        self._release_review_wait(action, at=at)
        self._queue_identity_actions(action['target'], action['review_cycle_id'])
        return {'disposition': 'review_resumed', 'review_cycle_id': action['review_cycle_id'],
                'action': _action(action), 'owner_activity_id': cycle.get('owner_activity_id')}

    def _record_review_input(self, action, execution_id, cycle=None):
        """Record delivered input once; the engine may call this before the runner.

        cycle is the current cycle when the caller has just checked it (_checked_review_result).
        """
        if cycle is None:
            cycle = self._review_cycle(action)
        prepared = self.runtime.get('review_inputs', {}).get(_pending_key(action))
        if not prepared or prepared['proposal_digest'] != cycle['proposal_digest']:
            raise ValueError('the review execution has no matching prepared input')
        execution = self.runtime['executions'][execution_id]
        admitted = self._admit_review_execution(action, execution)
        if admitted['disposition'] not in {'admitted', 'already_admitted'}:
            raise ValueError('review input cannot start: ' + admitted['disposition'])
        if cycle.get('owner_activity_id') is not None and execution.get('owner_activity_id') != cycle['owner_activity_id']:
            raise ValueError('review execution changed its owner activity')
        profile = execution.get('execution_profile_ref')
        expected_profile = (cycle.get('scope_assessment') or {}).get('selected_profile_ref')
        profiles = cycle.get('slot_profiles', {})
        if (expected_profile is not None and profile != expected_profile) or (
                action['slot'] in profiles and profiles[action['slot']] != profile):
            raise ValueError('logical review slot profile changed')
        binding = {'role_slot_id': action['slot'], 'profile_ref': deepcopy(profile),
                   'input_sha256': execution['input_manifest']['prompt']['sha256'],
                   'input_snapshot': execution.get('input_snapshot', self.head),
                   'proposal_digest': prepared['proposal_digest'],
                   'restored_messages': deepcopy(prepared['restored_messages']),
                   'request': deepcopy(prepared['request']),
                   'visible_execution_ids': list(prepared['visible_execution_ids'])}
        existing = cycle.get('input_bindings', {}).get(execution_id)
        if existing is not None:
            if {key: value for key, value in existing.items() if key != 'delegation_authority'} != binding:
                raise ValueError('delivered review input binding changed')
            return cycle
        authority = self._review_replacement_authority(action, execution_id)
        if authority is not None and not authority['allowed']:
            raise ValueError('replacement authority is no longer current: ' + authority['reason'])
        delegation_authority = self._delegation_authority_binding(cycle, action)
        if delegation_authority is not None:
            binding['delegation_authority'] = delegation_authority
        messages = [{'role': 'user', 'kind': 'proposal', 'content': deepcopy(prepared['proposal']),
                     'message_id': f'{execution_id}:proposal'},
                    {'role': 'user', 'kind': 'review_request', 'content': deepcopy(prepared['request']),
                     'message_id': f'{execution_id}:request'}]
        cycle = record_turn(cycle, action['slot'], messages)
        cycle.setdefault('slot_profiles', {})[action['slot']] = deepcopy(profile)
        cycle.setdefault('input_bindings', {})[execution_id] = binding
        self.runtime['review_cycles'][action['review_cycle_id']] = cycle
        return cycle

    def _record_review_prompt(self, execution_id, prompt, *, artifact_ref):
        """Seal the exact provider-delivered prompt, after provider boundary additions."""
        if not isinstance(prompt, str) or not isinstance(artifact_ref, str) or not artifact_ref:
            raise ValueError('delivered review prompt requires exact text and artifact reference')
        execution = self.runtime['executions'][execution_id]
        action = execution['action']
        if action.get('role') != 'identity_review' or not action.get('review_cycle_id'):
            return False
        cycle = self._review_cycle(action)
        source = {'artifact_ref': artifact_ref, 'sha256': hashlib.sha256(prompt.encode('utf-8')).hexdigest(),
                  'bytes': len(prompt.encode('utf-8'))}
        message = {'role': 'user', 'kind': 'delivered_prompt', 'content': prompt,
                   'message_id': execution_id + ':delivered_prompt', 'source': source}
        self.runtime['review_cycles'][cycle['id']] = record_turn(cycle, action['slot'], [message])
        return True

    def _record_review_observation(self, execution_id, event, *, artifact_ref, event_index):
        """Append observed public content only; never extract provider reasoning blocks."""
        execution = self.runtime['executions'][execution_id]
        action = execution['action']
        if action.get('role') != 'identity_review' or not action.get('review_cycle_id'):
            return False
        if type(event_index) is not int or event_index < 0 or not isinstance(artifact_ref, str) or not artifact_ref:
            raise ValueError('public review event requires an ordered artifact coordinate')
        messages = []
        kind, item = event.get('type'), event.get('item', {})
        if kind == 'public_message':
            message = event.get('message', {})
            if message.get('role') not in {'user', 'assistant', 'tool'} or 'content' not in message:
                raise ValueError('invalid normalized public message')
            messages.append({key: deepcopy(message[key]) for key in ('role', 'content', 'call', 'arguments') if key in message})
        elif kind == 'item.completed' and item.get('type') == 'agent_message':
            messages.append({'role': 'assistant', 'content': item['text']})
        elif kind == 'item.completed' and item.get('type') in {'command_execution', 'mcp_tool_call'}:
            keys = ('command', 'aggregated_output', 'exit_code') if item['type'] == 'command_execution' else ('server', 'tool', 'arguments', 'result', 'error')
            messages.append({'role': 'tool', 'call': item.get('id'),
                             'content': {key: deepcopy(item[key]) for key in keys if key in item}})
        elif kind in {'assistant', 'user'}:
            for block in event.get('message', {}).get('content', []):
                if not isinstance(block, dict):
                    continue
                if block.get('type') == 'text':
                    messages.append({'role': kind, 'content': block['text']})
                elif block.get('type') == 'tool_use':
                    messages.append({'role': 'assistant', 'content': deepcopy(block)})
                elif block.get('type') == 'tool_result':
                    messages.append({'role': 'tool', 'content': deepcopy(block)})
        if not messages:
            return False
        source = {'artifact_ref': artifact_ref, 'event_index': event_index,
                  'event_sha256': json_digest(event)}
        for index, message in enumerate(messages):
            for field in ('content', 'arguments', 'call'):
                if field not in message:
                    continue
                try:
                    canonical_json(message[field])
                except ValueError:
                    # Provider JSON numbers remain exact text outside integer-only state.
                    message[field] = compact_json_bytes(message[field]).decode('utf-8')
            message.update(kind='observed_public_message', source=deepcopy(source),
                           message_id=f'{execution_id}:public:{event_index}:{index}')
        cycle = self._review_cycle(action)
        prior = [row for row in cycle.get('turns', {}).get(action['slot'], [])
                 if row.get('message_id', '').startswith(execution_id + ':public:')]
        known = {row['message_id'] for row in prior}
        if prior and event_index < max(row['source']['event_index'] for row in prior) and any(row['message_id'] not in known for row in messages):
            raise ValueError('observed public review event arrived out of order')
        self.runtime['review_cycles'][cycle['id']] = record_turn(cycle, action['slot'], messages)
        return True

    def _checked_review_result(self, action, execution_id):
        """The one currentness and independence check of a returned review attempt, final or provisional."""
        cycle = self._review_cycle(action)
        validate_review_independence(cycle, self.runtime, execution_id, _action(action))
        changes = review_input_basis_changes(cycle.get('review_input_basis', {}), cycle)
        if changes:
            raise ValueError('review inputs changed before acceptance: ' + json.dumps(changes, ensure_ascii=False))
        return cycle

    def _apply_identity_review(self, action, output, execution_id):
        before_instance, before_runtime = deepcopy(self.instance), deepcopy(self.runtime)
        try:
            return self._accept_identity_review(action, output, execution_id)
        except (ValueError, KeyError, TypeError):
            self.instance, self.runtime = before_instance, before_runtime
            raise

    def _accept_identity_review(self, action, output, execution_id):
        authority = self._review_replacement_authority(action, execution_id)
        if authority is not None and not authority['allowed']:
            raise ValueError('replacement authority is no longer current: ' + authority['reason'])
        item = self.instance['knowledge'][action['target']]
        execution = self.runtime.get('executions', {}).get(execution_id)
        if execution is None or execution.get('role') != 'identity_review':
            raise ValueError('identity review requires its actual execution record')
        recorded_action = execution.get('action', {})
        if any(recorded_action.get(name) != action.get(name) for name in ('target', 'review_cycle_id', 'stage', 'slot', 'round')):
            raise ValueError('execution was assigned to a different review action')
        if _action(recorded_action) != _action(action):
            raise ValueError('execution replacement binding differs from its authorized action')
        cycle = self._checked_review_result(action, execution_id)
        selected_profile = (cycle.get('scope_assessment') or {}).get('selected_profile_ref')
        if selected_profile is not None and execution.get('execution_profile_ref') != selected_profile:
            raise ValueError('identity review execution did not use the scope assessment profile')
        cycle = self._record_review_input(action, execution_id, cycle)
        if cycle['proposal'].get('assessment_reassessment'):
            validate_review_binding(cycle, self.runtime, execution_id, _action(action), output, instance=self.instance)
        prepared = self.runtime['review_inputs'][_pending_key(action)]
        manifest = {'proposal_digest': cycle['proposal_digest'], 'role_slot_id': action['slot'],
                    'visible_execution_ids': prepared['visible_execution_ids'],
                    'input_snapshot': execution.get('input_snapshot', self.head),
                    'input_sha256': execution['input_manifest']['prompt']['sha256'],
                    'continuation_of': execution.get('continuation_of', []),
                    'context_origin': execution.get('context_origin', []),
                    'review_input_basis': deepcopy(cycle.get('review_input_basis')),
                    'selected_profile_ref': deepcopy(selected_profile),
                    'owner_activity_id': cycle.get('owner_activity_id')}
        if action.get('replacement_for') is not None:
            manifest.update(replacement_for=action['replacement_for'], grant_id=action['grant_id'],
                            grant_sha256=action['grant_sha256'], continuity_broken=True)
        updated = accept_result(cycle, _action(action), output, execution_id, input_manifest=manifest)
        if action['stage'] == 'scope':
            # Scope is the one authorized transition from an unassigned review
            # to its frozen initial slots, profile, and activity limit.
            updated['review_input_basis'] = capture_review_input_basis(updated)
        self.runtime['review_cycles'][action['review_cycle_id']] = updated
        self.runtime['review_inputs'].pop(_pending_key(action), None)
        if updated['status'] == 'working':
            self._queue_identity_actions(item['id'], action['review_cycle_id'])
            return
        self._publish_identity_review_result(action, updated, execution_id)

    def _publish_identity_review_result(self, action, updated, execution_id):
        knowledge_id = action['target']
        if updated['proposal'].get('assessment_reassessment'):
            return self._publish_assessment_reassessment(action, updated, execution_id)
        if updated.get('transition_id'):
            self._review_cycle(action)
            self.runtime.setdefault('history', []).append({'kind': 'staged_identity_review_completed',
                'review_cycle_id': updated['id'], 'transition_id': updated['transition_id'],
                'knowledge_id': knowledge_id, 'decision': updated['decision'], 'next_owner': 'trust_transition'})
            self.runtime['queue'][:] = [row for row in self.runtime['queue'] if row.get('review_cycle_id') != updated['id']]
            self._enqueue('trust_activate', transition_id=updated['transition_id'])
            return
        # The caller seals the basis. Worker output cannot supply publication authority.
        if updated.get('publication_premises') != self._review_publication_premises(knowledge_id):
            raise ValueError('review publication premises changed before publication')
        if updated['decision'] == 'match':
            # Publication rechecks the current identity; the olean fingerprint was
            # checked before compiling and a later change surfaces at the next check.
            from .trust_validation import require_active_environment
            require_active_environment(self.instance, self.runtime, current_identity=True, host=self.ports.host)
        assessment = identity_assessment(updated, reason='Complete independent review')
        assessment['basis'] = deepcopy(updated['identity_basis'])
        published, assessment_id = kr.record_identity_assessment(
            self.instance, knowledge_id, assessment, updated['policy_ref'], runtime=self.runtime, clock=self.ports.clock)
        self.instance = published
        item = self.instance['knowledge'][knowledge_id]
        updated['assessment_id'] = assessment_id
        updated['assessment_use_ids'] = [use['id'] for use in published['assessment_uses'].values()
                                         if use['assessment_id'] == assessment_id]
        effective = any(link['assessment_id'] == assessment_id for link in kr.usable_links(published, knowledge_id))
        reason = ('Complete identity match with current split evidence' if effective else
                  'Identity assessment recorded; current knowledge use is not established')
        for entry in updated['results'].values():
            producer_action = self.runtime['executions'].get(entry['execution_id'], {}).get('action',
                {'role': 'identity_review', 'target': item['id'], 'review_cycle_id': action['review_cycle_id'], **entry['action']})
            self._record_output_questions(producer_action, entry['output'], entry['execution_id'], public=True)
        self._record_review_questions(updated, execution_id)
        self.runtime['queue'][:] = [queued for queued in self.runtime['queue'] if not (
            queued.get('role') in {'identity_review', 'supplemental_research'} and queued.get('review_cycle_id') == action['review_cycle_id'])]
        followup = {'cycle_id': action['review_cycle_id'], 'knowledge_id': item['id'],
                    'assessment_id': assessment_id, 'assessment_use_ids': list(updated['assessment_use_ids']),
                    'formal_result_id': item['formal_result_id'], 'exposition_id': item['exposition_id'],
                    'proposal_digest': updated['proposal_digest'], 'decision': updated['decision'],
                    'status': updated['status'], 'effective': effective,
                    'issues': deepcopy(updated['issues']), 'findings': deepcopy(updated['findings']),
                    'remaining_questions': deepcopy(updated['followup']),
                    'supplemental_research': deepcopy(updated.get('research', {})),
                    'actual_scope': [{'execution_id': entry['execution_id'], 'action': deepcopy(entry['action']),
                                      'scope_complete': entry['output'].get('scope_complete')}
                                     for entry in updated['results'].values() if entry['stage'] in ('initial', 'judge')],
                    'reason': reason}
        self._enqueue('research_plan', reason=reason, identity_review=followup,
                      evidence_refs=[updated['id'], item['id']])

    def _research_source_spec(self, cycle, action, reference):
        """Seal one fixed investigation source admitted by the shared classification."""
        prepared = self.runtime.get('review_inputs', {}).get(_pending_key(action), {})
        own = {s['ref']: s for s in prepared.get('request', {}).get('source_refs', []) if s.get('slot') == action['slot']}
        kind, value = classify_research_source(reference, proposal=cycle['proposal'], issues=cycle['issues'],
            own_source_refs=own, sources=prepared.get('supplied_sources', self.instance.get('sources', [])),
            knowledge_ids=self.instance.get('knowledge', {}))
        if kind == 'transcript':
            value = cycle['turns'][action['slot']][own[reference]['index']]
        elif kind == 'source':
            snapshot = prepared.get('source_snapshot', self.head)
            raw = self.store.read(value['path'], snapshot)
            if value.get('sha256'):
                self._sealed_bytes(value['path'], value['sha256'], raw=raw,
                                   error='supplied research source bytes changed')
            return {'ref': reference, 'artifact_ref': value['path'], 'snapshot': snapshot,
                    'sha256': value.get('sha256') or hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)}
        elif kind == 'knowledge':
            value = {**_proposal(self.instance, reference), 'usable_links': kr.usable_links(self.instance, reference)}
        return inline_source_row(reference, value)

    def _defer_review_for_research(self, action, output, execution_id):
        if action.get('role') != 'identity_review' or not action.get('review_cycle_id'):
            return False
        requests = self.runtime['executions'][execution_id].get('extensions', {}).get('research_requests', [])
        if not requests: return False
        execution = self.runtime['executions'][execution_id]
        if execution.get('role') != 'identity_review' or any(execution.get('action', {}).get(key) != action.get(key)
                for key in ('target', 'review_cycle_id', 'stage', 'slot', 'round')):
            raise ValueError('research request execution was assigned to another review slot')
        cycle = self._checked_review_result(action, execution_id)
        source_specs = [[self._research_source_spec(cycle, action, ref) for ref in request['source_refs']]
                        for request in requests]
        cycle = self._record_review_input(action, execution_id, cycle)
        # This attempt returned provisionally. Its logical slot still needs a
        # future final response, even while ENGINE has not ended its execution.
        projected_executions = {**self.runtime['executions'], execution_id: {**execution, 'status': 'ended'}}
        reserved = reserved_review_slots(cycle, projected_executions)
        used = len(cycle['execution_accounting']['executions_used'])
        updated = defer_for_research(cycle, _action(action), output, requests, execution_id, source_specs,
            limit=self.instance['config']['review_research_limit'],
            budget_available=(used + len(requests) + len(reserved) <= cycle['activity_execution_limit']))
        self.runtime['review_cycles'][action['review_cycle_id']] = updated
        self.runtime.get('review_inputs', {}).pop(_pending_key(action), None)
        self.runtime['queue'][:] = [queued for queued in self.runtime['queue'] if not (
            queued.get('role') == 'identity_review' and queued.get('review_cycle_id') == action['review_cycle_id'] and
            all(queued.get(key) == action.get(key) for key in ('stage', 'slot', 'round')))]
        if updated['status'] != 'working':
            self._publish_identity_review_result(action, updated, execution_id)
            return True
        for request in requests:
            request_id = f"{execution_id}:{request['id']}"
            self._enqueue('supplemental_research', action['target'], review_cycle_id=action['review_cycle_id'],
                research_request_id=request_id, requesting_slot=action['slot'], stage='investigating',
                slot='research-' + request_id, round=action['round'], owner_review_cycle_id=action['review_cycle_id'],
                **({'owner_activity_id': updated['owner_activity_id']} if updated.get('owner_activity_id') else {}))
        self._queue_identity_actions(action['target'], action['review_cycle_id'])
        return True

    def _pending_review_research(self, action):
        if not review_research(action):
            raise ValueError('action is not a review investigation')
        cycle = self.runtime['review_cycles'].get(action['review_cycle_id'])
        request = cycle.get('research', {}).get(action.get('research_request_id')) if cycle else None
        if not request or cycle['status'] != 'working' or request['status'] != 'pending':
            raise ValueError('review investigation is not pending')
        if action.get('requesting_slot') != request['action']['slot']:
            raise ValueError('review investigation points to a different requesting slot')
        parent_action = {'role': 'identity_review', 'target': action['target'], 'review_cycle_id': action['review_cycle_id'], **request['action']}
        self._review_cycle(parent_action)
        return cycle, request

    def _review_research_schema(self, action):
        _, request = self._pending_review_research(action)
        schema = research_schema()
        fields = schema['properties']
        fields['research_request_id']['enum'] = [request['id']]
        fields['request_digest']['enum'] = [request['request_digest']]
        return schema

    def _materialize_research_sources(self, sources, workspace, *, slot=None):
        workspace = Path(workspace).resolve()
        directory = workspace / 'input' / 'review-research'
        directory.mkdir(parents=True, exist_ok=True)
        if not directory.resolve().is_relative_to(workspace): raise ValueError('research source directory escapes workspace')
        visible = []
        for i, source in enumerate(sources):
            coordinate = {'slot': slot, 'source_index': i, 'source_ref': source['ref'],
                          'artifact_ref': source.get('artifact_ref'), 'snapshot': source.get('snapshot', self.head)}
            try:
                raw = None if 'inline' in source else self.store.read(source['artifact_ref'], source.get('snapshot', self.head))
            except OSError as error:
                import errno
                raise ReviewRestorationError(str(error), cause_kind='fixed_source_io_unavailable',
                    coordinate={**coordinate, 'errno': error.errno, 'path': error.filename},
                    expected_sha256=source['sha256'],
                    retryable=error.errno in {errno.EAGAIN, errno.EINTR, errno.EBUSY, errno.ETIMEDOUT}) from error
            # Inline text is derived from state and compared; a sealed artifact row
            # already matched in this process (이음새-정본.md §3) is not hashed again.
            try:
                if 'inline' in source:
                    raw = inline_source_bytes(source)
                else:
                    self._sealed_bytes(source['artifact_ref'], source['sha256'], source['bytes'], raw=raw)
            except ValueError as mismatch:
                observed = raw if raw is not None else compact_json_bytes(source['inline'])
                raise ReviewRestorationError('fixed research source bytes changed', cause_kind='fixed_source_content_mismatch',
                    coordinate=coordinate, expected_sha256=source['sha256'],
                    observed_sha256=hashlib.sha256(observed).hexdigest()) from mismatch
            suffix = '.json' if 'inline' in source else Path(source['artifact_ref']).suffix
            path = directory / f"{i:04d}-{source['sha256']}{suffix}"
            if not path.resolve().is_relative_to(directory.resolve()): raise ValueError('research source file escapes workspace')
            observed = path.read_bytes() if path.exists() else None
            if observed is not None and observed != raw:
                raise ReviewRestorationError('research source file has different bytes', cause_kind='materialized_content_mismatch',
                    coordinate={**coordinate, 'path': str(path)}, expected_sha256=source['sha256'],
                    observed_sha256=hashlib.sha256(observed).hexdigest())
            path.write_bytes(raw)
            visible.append({key: deepcopy(value) for key, value in source.items() if key != 'inline'} |
                           {'local_path': path.relative_to(workspace).as_posix()})
        return visible

    def _review_research_context(self, action, workspace):
        cycle, request = self._pending_review_research(action)
        sources = self._materialize_research_sources(request['source_records'], workspace)
        return {'proposal': deepcopy(cycle['proposal']), 'review_research': {
            'id': request['id'], 'request_digest': request['request_digest'], 'question': request['question'],
            'proposal_digest': cycle['proposal_digest'], 'requesting_slot': request['action']['slot'], 'sources': sources,
            'instructions': 'Investigate only this fixed question using the exact supplied source files. Return answered or unresolved with precise evidence. Do not judge proposal identity, revise knowledge, start nested research, or request external actions. Additional evidence you derive may be saved in this workspace and cited as workspace:<relative-path>.'}}

    def _apply_review_research(self, action, output, execution_id):
        cycle, request = self._pending_review_research(action)
        execution = self.runtime['executions'].get(execution_id)
        if not execution or execution.get('role') != 'supplemental_research' or execution.get('action', {}).get('research_request_id') != request['id']:
            raise ValueError('research result has no matching assigned execution')
        if execution_id not in cycle['execution_accounting'].get('admissions', {}):
            raise ValueError('review investigation must be admitted before execution, not on result acceptance')
        # Sealed replay checks the same seat shape (validate_sealed_review).
        validate_review_independence(cycle, self.runtime, execution_id, _independence_seat(action))
        records = deepcopy(request['source_records'])
        outputs = execution.get('output_files', [])
        allowed = {source['ref'] for source in records}
        from .submission import fixed_research_reference_path
        for name in [*output.get('used_sources', []), *output.get('evidence_refs', [])]:
            path = fixed_research_reference_path(name, allowed)
            if path is None: continue
            file = next((entry for entry in outputs if entry['path'] == path), None)
            if file is None: raise ValueError('investigation evidence file was not preserved')
            if name not in allowed:
                records.append({'ref': name, 'artifact_ref': file['artifact_ref'], 'sha256': file['sha256'], 'bytes': file['bytes']})
                allowed.add(name)
        updated = accept_research_result(cycle, request['id'], output, execution_id, source_records=records)
        self.runtime['review_cycles'][action['review_cycle_id']] = updated
        self._queue_identity_actions(action['target'], action['review_cycle_id'])

    def _abandon_review_research(self, action, execution_id, reason):
        if action.get('role') != 'supplemental_research' or not action.get('research_request_id'):
            return False
        current = self.runtime.get('review_cycles', {}).get(action.get('review_cycle_id'))
        if not current or current['status'] != 'working' or current.get('research', {}).get(action['research_request_id'], {}).get('status') != 'pending':
            return False
        cycle, request = self._pending_review_research(action)
        output = {'summary': 'The assigned investigation execution did not complete', 'used_sources': [],
                  'questions': [request['question']], 'research_request_id': request['id'],
                  'request_digest': request['request_digest'], 'outcome': 'unresolved',
                  'answer': 'Execution incomplete: ' + str(reason), 'scope_complete': False, 'evidence_refs': []}
        updated = accept_research_result(cycle, request['id'], output, execution_id,
                                        source_records=request['source_records'], execution_status='incomplete')
        self.runtime['review_cycles'][action['review_cycle_id']] = updated
        self._queue_identity_actions(action['target'], action['review_cycle_id'])
        return True

    def _finish_failed_investigation(self, action, execution_id, reason):
        """Close a no-longer-retried question and retain its failed handoff."""
        if not self._abandon_review_research(action, execution_id, reason):
            return False
        previous = self.runtime.get('waiting_actions', {}).pop(action.get('id'), None)
        self.runtime.setdefault('history', []).append({'kind': 'failed_investigation_returned',
            'execution_id': execution_id, 'research_request_id': action['research_request_id'],
            'review_cycle_id': action['review_cycle_id'], 'reason': reason, 'previous': previous})
        return True
