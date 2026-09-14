"""ResearchEngine integration for the finite independent identity-review cycle."""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

from .repository import canonical_json, new_id
from .review_cycle import (accept_result, context_for, next_actions, record_turn, stage_schema, start_review,
                          defer_for_research, accept_research_result, research_schema)


_PROPOSAL_FIELDS = ('id', 'revision', 'statement', 'explanation', 'summary', 'lean_code',
                    'declaration_names', 'dependencies', 'relation_claim', 'relation_endpoint_basis', 'confirmed_scope', 'epistemic_status')
_FORMAL_FIELDS = ('status', 'source_sha256', 'declarations', 'axioms', 'toolchain',
                  'environment', 'environment_sha256', 'trust_manifest', 'artifact_ref', 'execution_id',
                  'trust_environment_id', 'trust_environment_status', 'allowed_axioms')
_FORMAL_FIELDS += ('declaration_signatures', 'signature_hash')


def _proposal(item):
    result = {name: deepcopy(item.get(name, [] if name in ('declaration_names', 'dependencies') else ''))
              for name in _PROPOSAL_FIELDS}
    result['formal'] = {name: deepcopy(item['formal'][name]) for name in _FORMAL_FIELDS if name in item.get('formal', {})}
    return result


def _action(action):
    return {name: action[name] for name in ('stage', 'slot', 'round')}


def _pending_key(action):
    return f"{action['review_cycle_id']}:{action['stage']}:{action['round']}:{action['slot']}"


def _transcript_bytes(value):
    # review_cycle seals this canonical, compact encoding, rather than repository
    # JSON (which uses indentation and a terminal newline).
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False).encode('utf-8')


def _formal_basis(formal):
    # A fresh check may have new execution/artifact coordinates while proving
    # exactly the same source under exactly the same environment.
    return {name: deepcopy(value) for name, value in formal.items()
            if name not in ('execution_id', 'artifact_ref')}


class ReviewEngineMixin:
    """Mixin requiring ResearchEngine's state, queue, repository, and save methods.

    The owning engine saves cycle/knowledge/queue mutations atomically with the
    execution result. `_record_review_input` may also be called once an execution
    starts, so failed attempts retain the input that was actually delivered.
    """

    def _start_identity_review(self, knowledge_id, previous_cycle_id=None):
        item = self.instance['knowledge'][knowledge_id]
        cycles = self.runtime.setdefault('review_cycles', {})
        current_id = item.get('review_cycle_id')
        if previous_cycle_id is None and current_id in cycles:
            current = cycles[current_id]
            if _proposal(item) != _proposal(current['proposal']):
                raise ValueError('sealed review proposal changed; submit an explicit new revision')
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
            if item.get('revision_of') != previous.get('knowledge_id'):
                raise ValueError('revision must name the previous knowledge item')
        if not item.get('revision') or (previous is not None and item['revision'] == previous['revision']):
            old_revision = previous['revision'] if previous else 0
            item['revision'] = old_revision + 1 if isinstance(old_revision, int) else len(previous['previous_reviews']) + 2
        config = self.instance['config']
        reviewer_count = item.get('required_reviews', config.get('reviewers', 3))
        reviewers = item.get('reviewer_slots', reviewer_count)
        if previous is not None and isinstance(reviewers, int):
            if reviewers < len(previous['reviewer_slots']):
                raise ValueError('new revision cannot remove existing reviewer slots')
            reviewers = previous['reviewer_slots'] + [f'initial-{i}' for i in range(len(previous['reviewer_slots']), reviewers)]
        round_limit = config.get('objection_round_limit', config.get('review_rounds', 3))
        cycle = start_review(_proposal(item), reviewers=reviewers, max_rounds=round_limit,
                             judges=previous['judge_slots'] if previous else 3, previous=previous)
        cycle_id = new_id('RC')
        cycle.update(id=cycle_id, knowledge_id=knowledge_id, input_snapshot=self.head,
                     producer_execution_ids=list(dict.fromkeys([*(previous.get('producer_execution_ids', []) if previous else []),
                                                *item.get('producer_execution_ids', []),
                                                *([item['producer_execution']] if item.get('producer_execution') else [])])))
        cycles[cycle_id] = cycle
        item.setdefault('review_history', [])
        if previous_cycle_id and previous_cycle_id not in item['review_history']:
            item['review_history'].append(previous_cycle_id)
        if item.get('reviews'):
            item.setdefault('previous_initial_reviews', []).append({'cycle_id': current_id, 'reviews': deepcopy(item['reviews'])})
        item['reviews'] = []
        item['required_reviews'] = len(cycle['reviewer_slots'])
        item['review_cycle_id'] = cycle_id
        item['status'] = 'reviewing'
        item['identity_assessment'] = self._identity_assessment(cycle, effective=False,
                                                              reason='Independent review is in progress')
        self._queue_identity_actions(knowledge_id, cycle_id)
        return cycle_id

    def _queue_identity_actions(self, knowledge_id, cycle_id):
        cycle = self.runtime['review_cycles'][cycle_id]
        for action in next_actions(cycle):
            exists = any(queued.get('role') == 'identity_review' and
                         queued.get('review_cycle_id') == cycle_id and
                         all(queued.get(key) == value for key, value in action.items())
                         for queued in self.runtime['queue'])
            if not exists:
                self._enqueue('identity_review', knowledge_id, review_cycle_id=cycle_id, **action)

    def _review_cycle(self, action):
        if action.get('role') != 'identity_review':
            raise ValueError('action is not an identity review')
        cycle = self.runtime.get('review_cycles', {}).get(action.get('review_cycle_id'))
        if cycle is None or cycle.get('knowledge_id') != action.get('target'):
            raise ValueError('review action refers to another or missing proposal')
        item = self.instance['knowledge'][action['target']]
        if item.get('review_cycle_id') != action['review_cycle_id']:
            raise ValueError('review action belongs to a superseded proposal revision')
        live = _proposal(item)
        if any(live[name] != cycle['proposal'].get(name, [] if name in ('declaration_names', 'dependencies') else '') for name in _PROPOSAL_FIELDS):
            raise ValueError('sealed mathematical proposal changed during review')
        return cycle

    def _review_schema(self, action):
        cycle = self._review_cycle(action)
        if _action(action) not in next_actions(cycle):
            raise ValueError('review action is not pending')
        schema = stage_schema(action['stage'])
        schema['properties']['proposal_digest'] = {**schema['properties']['proposal_digest'], 'enum': [cycle['proposal_digest']]}
        return schema

    def _review_context(self, action, workspace: Path):
        cycle = self._review_cycle(action)
        context = context_for(cycle, _action(action))
        for investigation in context.get('supplemental_results', []):
            investigation['source_records'] = self._materialize_research_sources(investigation.get('source_records', []), workspace)
            investigation['result']['source_records'] = self._materialize_research_sources(investigation['result'].get('source_records', []), workspace)
        directory = (workspace / 'input' / 'review-sources').resolve()
        workspace = workspace.resolve()
        if not directory.is_relative_to(workspace):
            raise ValueError('review source directory escapes workspace')
        directory.mkdir(parents=True, exist_ok=True)
        references = {}
        for reference in context['source_refs']:
            slot = reference['slot']
            index = reference['index']
            try:
                message = cycle['turns'][slot][index]
            except (KeyError, IndexError) as error:
                raise ValueError('review source bytes are permanently unavailable') from error
            raw = _transcript_bytes(message)
            if hashlib.sha256(raw).hexdigest() != reference['sha256'] or len(raw) != reference['bytes']:
                raise ValueError('review source hash does not match its sealed transcript')
            path = directory / f"{reference['sha256']}.json"
            if not path.resolve().is_relative_to(directory):
                raise ValueError('review source file escapes its materialization directory')
            if path.exists() and path.read_bytes() != raw:
                raise ValueError('immutable review source path contains different bytes')
            path.write_bytes(raw)
            reference['local_path'] = path.relative_to(workspace).as_posix()
            references[reference['ref']] = deepcopy(reference)
        for message in context['self_messages']:
            content = message.get('content')
            if isinstance(content, dict) and 'source_ref' in content:
                content['source_ref'] = deepcopy(references[content['source_ref']['ref']])
        context['output_schema'] = self._review_schema(action)
        context['review_cycle_id'] = action['review_cycle_id']
        context['snapshot'] = cycle['input_snapshot']
        context['source_instructions'] = ('Read each referenced source through its local_path when needed. '
            'The JSON file contains the exact original public message; its content is the original source body. '
            'Compare the complete current proposal. Prior revision judgments do not approve this revision.')
        context['research_request_contract'] = {
            'extension_file': 'activity-extensions.json',
            'field': 'research_requests',
            'item': {'id': 'local request ID', 'question': 'One fixed question to investigate',
                     'source_refs': ['proposal or proposal:<field.path>, issue:<id>, supplied source ref, or readable knowledge ID']},
            'remaining_requests': max(0, self.instance['config'].get('review_research_limit', 3) - len(cycle.get('research', {}))),
            'instructions': 'If investigation is necessary, write research_requests and return unresolved provisionally for initial/judge. The slot is deferred without sealing a verdict; all requested answers return to this same slot. Use an existing answer when it resolves the question. Investigation cannot replace your final complete review.'}
        # This is the new request, excluding the restored transcript. Appending the
        # complete rendered prompt here would recursively duplicate old messages.
        request = {key: deepcopy(value) for key, value in context.items()
                   if key not in ('proposal', 'self_messages', 'output_schema')}
        request['action'] = deepcopy(action)
        prepared = {'proposal_digest': cycle['proposal_digest'], 'proposal': deepcopy(context['proposal']),
                    'request': request, 'slot': action['slot'],
                    'visible_execution_ids': [entry['execution_id'] for entry in context['completed_results'].values()] +
                                             [entry['result']['execution_id'] for entry in context.get('supplemental_results', [])],
                    'workspace': str(workspace)}
        self.runtime.setdefault('review_inputs', {})[_pending_key(action)] = prepared
        return context

    def _record_review_input(self, action, execution_id):
        """Record delivered input once; the engine may call this before the runner."""
        cycle = self._review_cycle(action)
        prepared = self.runtime.get('review_inputs', {}).get(_pending_key(action))
        if not prepared or prepared['proposal_digest'] != cycle['proposal_digest']:
            raise ValueError('the review execution has no matching prepared input')
        messages = [{'role': 'user', 'kind': 'proposal', 'content': deepcopy(prepared['proposal']),
                     'message_id': f'{execution_id}:proposal'},
                    {'role': 'user', 'kind': 'review_request', 'content': deepcopy(prepared['request']),
                     'message_id': f'{execution_id}:request'}]
        cycle = record_turn(cycle, action['slot'], messages)
        self.runtime['review_cycles'][action['review_cycle_id']] = cycle
        return cycle

    @staticmethod
    def _identity_assessment(cycle, *, effective, reason):
        final_entries = [cycle['results'][key] for key in cycle['sealed']
                         if cycle['results'][key]['action']['stage'] == ('initial' if not cycle['issues'] else 'judge')]
        if cycle['issues']:
            final_entries = [entry for entry in final_entries if entry['action']['round'] == cycle['round']]
        return {'cycle_id': cycle['id'], 'revision': cycle['revision'],
                'proposal_digest': cycle['proposal_digest'], 'decision': cycle['decision'],
                'status': cycle['status'], 'effective': effective,
                'source_sha256': cycle['proposal']['formal'].get('source_sha256'),
                'formal_environment': deepcopy(cycle['proposal']['formal'].get('toolchain')),
                'execution_ids': [entry['execution_id'] for entry in final_entries],
                'scope_complete': bool(final_entries) and all(entry['output'].get('scope_complete') for entry in final_entries),
                'reason': reason}

    def _apply_identity_review(self, action, output, execution_id):
        cycle = self._review_cycle(action)
        item = self.instance['knowledge'][action['target']]
        execution = self.runtime.get('executions', {}).get(execution_id)
        if execution is None or execution.get('role') != 'identity_review':
            raise ValueError('identity review requires its actual execution record')
        recorded_action = execution.get('action', {})
        if any(recorded_action.get(name) != action.get(name) for name in ('target', 'review_cycle_id', 'stage', 'slot', 'round')):
            raise ValueError('execution was assigned to a different review action')
        if execution_id in cycle.get('producer_execution_ids', []):
            raise ValueError('proposal author cannot review their own proposal')
        cycle = self._record_review_input(action, execution_id)
        prepared = self.runtime['review_inputs'][_pending_key(action)]
        manifest = {'proposal_digest': cycle['proposal_digest'], 'role_slot_id': action['slot'],
                    'visible_execution_ids': prepared['visible_execution_ids'],
                    'input_snapshot': execution.get('input_snapshot', self.head),
                    'input_sha256': execution.get('input_sha256'),
                    'continuation_of': execution.get('continuation_of', []),
                    'context_origin': execution.get('context_origin', [])}
        producer_context = set(cycle.get('producer_execution_ids', []))
        for name in ('continuation_of', 'context_origin'):
            origins = manifest[name] or []
            if isinstance(origins, str): origins = [origins]
            if producer_context.intersection(origins):
                raise ValueError('identity reviewer inherited author context')
        updated = accept_result(cycle, _action(action), output, execution_id, input_manifest=manifest)
        self.runtime['review_cycles'][action['review_cycle_id']] = updated
        self.runtime['review_inputs'].pop(_pending_key(action), None)
        if action['stage'] == 'initial':
            item.setdefault('reviews', []).append({'execution_id': execution_id, 'slot': action['slot'],
                'cycle_id': action['review_cycle_id'], **deepcopy(output)})
        if updated['status'] == 'working':
            self._queue_identity_actions(item['id'], action['review_cycle_id'])
            return
        self._publish_identity_review_result(action, updated)

    def _publish_identity_review_result(self, action, updated):
        item = self.instance['knowledge'][action['target']]
        formal = item.get('formal', {})
        source_hash = hashlib.sha256(item['lean_code'].encode('utf-8')).hexdigest()
        environment_id = formal.get('trust_environment_id')
        environment_current = ('trust_environment_status' not in formal or
            (environment_id is not None and self.instance.get('active_trust_environment') == environment_id and
             self.instance.get('trust_environments', {}).get(environment_id, {}).get('status') == 'active'))
        formal_current = (formal.get('status') == 'verified' and formal.get('source_sha256') == source_hash and
                          formal.get('trust_environment_status', 'active') == 'active' and
                          environment_current and
                          _formal_basis(_proposal(item)['formal']) == _formal_basis(updated['proposal']['formal']))
        transition_id = updated.get('trust_transition_id')
        if updated['decision'] == 'match' and formal_current and transition_id:
            causes = item.get('use_suspensions', [])
            resolved = [cause for cause in causes if cause.get('kind') == 'semantic' and cause.get('transition_id') == transition_id
                        and cause.get('review_cycle_id', updated['id']) == updated['id']]
            if resolved:
                remaining = [cause for cause in causes if cause not in resolved]
                old_reasons = list(item.get('use_suspension_reasons', []))
                unrelated = [reason for reason in old_reasons if reason not in {cause.get('reason') for cause in resolved}]
                item['use_suspensions'] = remaining
                item['use_suspension_reasons'] = list(dict.fromkeys([*unrelated, *[cause.get('reason') for cause in remaining if cause.get('reason')]]))
                item['use_suspended'] = bool(remaining or item['use_suspension_reasons'])
                item.setdefault('use_history', []).append({'action': 'trust_semantics_revalidated', 'transition_id': transition_id,
                                                          'review_cycle_id': updated['id'], 'resolved_suspensions': resolved})
        effective = updated['decision'] == 'match' and formal_current and not item.get('use_suspended', False)
        if effective:
            item['status'] = 'verified'
            item['verified_at'] = datetime.now(timezone.utc).isoformat()
            reason = 'Complete identity match and the exact formal source and environment remain valid'
        elif item.get('use_suspended', False):
            item['status'] = 'suspended'
            reason = 'Identity review is complete but use remains suspended pending its reassessment contract'
        elif updated['decision'] == 'unresolved':
            item['status'] = 'unresolved'
            reason = 'Required identity review remains unresolved; no mathematical approval was created'
        else:
            item['status'] = 'needs_revision'
            reason = ('Independent review confirmed a mismatch' if updated['decision'] == 'mismatch'
                      else 'Formal source or environment no longer matches the reviewed proposal')
        item['identity_assessment'] = self._identity_assessment(updated, effective=effective, reason=reason)
        item['identity_assessment']['formal_verification'] = deepcopy(_proposal(item)['formal'])
        if updated['decision'] == 'unresolved':
            questions = [question for entry in updated['results'].values() for question in entry['output'].get('questions', [])]
            for investigation in updated.get('research', {}).values():
                if investigation.get('status') in {'pending', 'unresolved'}:
                    questions.append(investigation['question'])
                    if investigation.get('result'):
                        questions.extend(investigation['result']['output'].get('questions', []))
            for followup in updated.get('followup', []):
                questions.extend(request['question'] for request in followup.get('research_requests', []))
            for question in dict.fromkeys(questions):
                message = f"Identity review {updated['id']} unresolved: {question}"
                if message not in self.runtime.setdefault('questions', []): self.runtime['questions'].append(message)
        if action['review_cycle_id'] not in item.setdefault('review_history', []):
            item['review_history'].append(action['review_cycle_id'])
        self.runtime['queue'][:] = [queued for queued in self.runtime['queue'] if not (
            queued.get('role') in {'identity_review', 'supplemental_research'} and queued.get('review_cycle_id') == action['review_cycle_id'])]
        followup = {'cycle_id': action['review_cycle_id'], 'knowledge_id': item['id'],
                    'proposal_digest': updated['proposal_digest'], 'decision': updated['decision'],
                    'status': updated['status'], 'effective': effective,
                    'issues': deepcopy(updated['issues']), 'findings': deepcopy(updated['findings']),
                    'remaining_questions': deepcopy(updated['followup']),
                    'supplemental_research': deepcopy(updated.get('research', {})),
                    'actual_scope': [{'execution_id': entry['execution_id'], 'action': deepcopy(entry['action']),
                                      'scope_complete': entry['output'].get('scope_complete')}
                                     for entry in updated['results'].values() if entry['stage'] in ('initial', 'judge')],
                    'reason': reason}
        self._enqueue('research_plan', reason=reason, identity_review=followup)

    def _research_source_spec(self, cycle, action, reference):
        """Resolve only fixed proposal, public issue, supplied source, or own transcript refs."""
        value = None
        if reference == 'proposal':
            value = cycle['proposal']
        elif reference.startswith('proposal:'):
            value = cycle['proposal']
            for name in reference.removeprefix('proposal:').replace('/', '.').strip('.').split('.'):
                if not isinstance(value, dict) or name not in value: raise ValueError('unknown proposal source coordinate')
                value = value[name]
        elif reference.startswith('issue:'):
            issue_id = reference.removeprefix('issue:')
            if issue_id not in cycle['issues']: raise ValueError('unknown public issue source')
            value = cycle['issues'][issue_id]
        else:
            prepared = self.runtime.get('review_inputs', {}).get(_pending_key(action), {})
            source = next((s for s in prepared.get('request', {}).get('source_refs', []) if s.get('ref') == reference), None)
            if source:
                if source.get('slot') != action['slot']: raise ValueError('another slot transcript is private')
                value = cycle['turns'][action['slot']][source['index']]
            else:
                supplied = next((s for s in self.instance.get('sources', []) if reference in (s.get('path'), s.get('name'))), None)
                if supplied:
                    raw = self.store.read(supplied['path'], self.head)
                    if supplied.get('sha256') and hashlib.sha256(raw).hexdigest() != supplied['sha256']:
                        raise ValueError('supplied research source bytes changed')
                    return {'ref': reference, 'artifact_ref': supplied['path'], 'snapshot': self.head,
                            'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)}
                record = self.instance.get('knowledge', {}).get(reference)
                if record is None: raise ValueError('research source is not in the supplied readable source set: ' + reference)
                value = {**_proposal(record), 'status': record.get('status'), 'use_suspended': record.get('use_suspended', False)}
        raw = _transcript_bytes(value)
        return {'ref': reference, 'inline': deepcopy(value), 'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)}

    def _defer_review_for_research(self, action, output, execution_id):
        if action.get('role') != 'identity_review' or not action.get('review_cycle_id'):
            return False
        requests = self.runtime['executions'][execution_id].get('extensions', {}).get('research_requests', [])
        if not requests: return False
        cycle = self._review_cycle(action)
        execution = self.runtime['executions'][execution_id]
        if execution.get('role') != 'identity_review' or any(execution.get('action', {}).get(key) != action.get(key)
                for key in ('target', 'review_cycle_id', 'stage', 'slot', 'round')):
            raise ValueError('research request execution was assigned to another review slot')
        if not isinstance(requests, list): raise ValueError('research_requests must be a list')
        if execution_id in cycle.get('producer_execution_ids', []): raise ValueError('author cannot request independent review research')
        source_specs = []
        for request in requests:
            if not isinstance(request, dict) or not isinstance(request.get('source_refs'), list):
                raise ValueError('research request requires explicit source_refs')
            source_specs.append([self._research_source_spec(cycle, action, ref) for ref in request['source_refs']])
        cycle = self._record_review_input(action, execution_id)
        used = sum(ex.get('budget_kind') == 'work' for ex in self.runtime.get('executions', {}).values())
        remaining = self.instance['config'].get('work_calls', 40) - used
        reserved = len(next_actions(cycle)) + len(cycle.get('deferred_actions', {}))
        if cycle['phase'] == 'initial': reserved += 4 + (cycle['reviewers'] + 3 if cycle['max_rounds'] > 1 else 0)
        elif cycle['phase'] in ('organize', 'answer'): reserved += 3
        elif cycle['phase'] == 'judge' and cycle['round'] < cycle['max_rounds']: reserved += cycle['reviewers'] + 3
        updated = defer_for_research(cycle, _action(action), output, requests, execution_id,
            limit=self.instance['config'].get('review_research_limit', 3), budget_available=remaining >= len(requests) + reserved)
        self.runtime['review_cycles'][action['review_cycle_id']] = updated
        self.runtime.get('review_inputs', {}).pop(_pending_key(action), None)
        self.runtime['queue'][:] = [queued for queued in self.runtime['queue'] if not (
            queued.get('role') == 'identity_review' and queued.get('review_cycle_id') == action['review_cycle_id'] and
            all(queued.get(key) == action.get(key) for key in ('stage', 'slot', 'round')))]
        if updated['status'] != 'working':
            self._publish_identity_review_result(action, updated)
            return True
        for request, specs in zip(requests, source_specs):
            request_id = f"{execution_id}:{request['id']}"
            record = updated['research'][request_id]
            record['source_records'] = specs
            record['request_digest'] = hashlib.sha256(canonical_json({'question': record['question'],
                'proposal_digest': updated['proposal_digest'],
                'sources': [{key: s[key] for key in ('ref', 'sha256', 'bytes')} for s in specs]})).hexdigest()
            self._enqueue('supplemental_research', action['target'], review_cycle_id=action['review_cycle_id'],
                research_request_id=request_id, requesting_slot=action['slot'], stage='investigating',
                slot='research-' + request_id, round=action['round'], owner_review_cycle_id=action['review_cycle_id'])
        self._queue_identity_actions(action['target'], action['review_cycle_id'])
        return True

    def _pending_review_research(self, action):
        if action.get('role') != 'supplemental_research' or not action.get('review_cycle_id'):
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
        schema['properties']['research_request_id']['enum'] = [request['id']]
        schema['properties']['request_digest']['enum'] = [request['request_digest']]
        return schema

    def _materialize_research_sources(self, sources, workspace):
        workspace = Path(workspace).resolve()
        directory = workspace / 'input' / 'review-research'
        directory.mkdir(parents=True, exist_ok=True)
        if not directory.resolve().is_relative_to(workspace): raise ValueError('research source directory escapes workspace')
        visible = []
        for i, source in enumerate(sources):
            raw = _transcript_bytes(source['inline']) if 'inline' in source else self.store.read(source['artifact_ref'], source.get('snapshot', self.head))
            if hashlib.sha256(raw).hexdigest() != source['sha256'] or len(raw) != source['bytes']:
                raise ValueError('fixed research source bytes changed')
            suffix = '.json' if 'inline' in source else Path(source['artifact_ref']).suffix
            path = directory / f"{i:04d}-{source['sha256']}{suffix}"
            if not path.resolve().is_relative_to(directory.resolve()): raise ValueError('research source file escapes workspace')
            if path.exists() and path.read_bytes() != raw: raise ValueError('research source file has different bytes')
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
        if execution_id in cycle.get('producer_execution_ids', []): raise ValueError('investigation execution cannot be the proposal author')
        for name in ('continuation_of', 'context_origin'):
            origins = execution.get(name, []) or []
            if isinstance(origins, str): origins = [origins]
            if set(cycle.get('producer_execution_ids', [])).intersection(origins):
                raise ValueError('review investigation cannot inherit author context')
        if any(execution.get('extensions', {}).get(key) for key in ('knowledge_changes', 'external_requests', 'research_requests', 'task_conditions')):
            raise ValueError('fixed review investigation cannot author changes or start nested work')
        records = deepcopy(request['source_records'])
        outputs = execution.get('output_files', [])
        allowed = {source['ref'] for source in records}
        for name in [*output.get('used_sources', []), *output.get('evidence_refs', [])]:
            if name in allowed: continue
            if not isinstance(name, str) or not name.startswith('workspace:'):
                raise ValueError('investigation cites evidence outside its fixed source set')
            path = name.removeprefix('workspace:')
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
