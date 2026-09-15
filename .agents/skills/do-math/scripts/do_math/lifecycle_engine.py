"""Engine integration for currentness, scheduling, authority and external effects."""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
import hashlib
from pathlib import Path

from .external import prepare_operation, validate_operation, execute_operation, reconcile_operation
from .governance import ensure_governance, apply_decision, timestamp
from .knowledge import (revise_knowledge, invalidate_knowledge, register_environment,
    begin_transition, record_transition_result, activate_transition, invalidate_environment,
    validate_basis, assess_use)
from .planning import task_ready, contract_hash, apply_event_schedule
from .input_basis import sources_current
from .repository import canonical_json, new_id

_DEFAULT_AXIOMS = ['propext', 'Classical.choice', 'Quot.sound']
_SCHEDULABLE = {'planned', 'ready', 'waiting', 'needs_revision'}


def _digest(value):
    return hashlib.sha256(canonical_json(value)).hexdigest()


def _reconsider_interval(config):
    seconds = config.get('research_reconsider_seconds', 86400)
    if isinstance(seconds, bool) or not isinstance(seconds, int) or seconds <= 0:
        raise ValueError('research_reconsider_seconds must be a positive integer')
    return timedelta(seconds=seconds)


def _toolchain_matches(expected, actual):
    if not isinstance(actual, dict) or not actual.get('sha256'):
        return False
    if actual['sha256'] != expected.get('sha256'):
        return False
    if expected.get('version') and actual.get('version') != expected['version']:
        return False
    return expected.get('project') == actual.get('project') and expected.get('configured_command') == actual.get('configured_command')


class LifecycleEngineMixin:
    def _lifecycle_now(self):
        clock = getattr(self, 'lifecycle_clock', None)
        return timestamp(clock() if clock else None)

    def _upgrade_runtime(self):
        if any(root.get('feature_version', 1) not in {1, 2} for root in (self.instance, self.runtime)):
            raise ValueError('unsupported feature version; an explicit verified migration is required')
        legacy_upgrade = (self.instance.get('contract_id') == 'do-math-cli/1' and
                          min(self.instance.get('feature_version', 1), self.runtime.get('feature_version', 1)) == 1)
        self.instance = ensure_governance(self.instance, self._lifecycle_now().isoformat())
        self.instance['feature_version'] = max(2, self.instance.get('feature_version', 0))
        self.runtime['feature_version'] = max(2, self.runtime.get('feature_version', 0))
        for name, value in {'events': [], 'pending_events': [], 'review_cycles': {},
            'external_operations': {}, 'trust_transitions': {}, 'conversations': {},
            'checkpoints': {}, 'observations': {}, 'condition_states': {}, 'task_readiness': {},
            'extended_controls': {}, 'tasks': {}, 'executions': {}, 'activities': {},
            'queue': [], 'history': [], 'questions': []}.items():
            self.runtime.setdefault(name, deepcopy(value))
        self.instance.setdefault('trust_environments', {})
        self.instance.setdefault('active_trust_environment', None)
        for task in self.runtime['tasks'].values():
            task.setdefault('feature_version', 2)
            if legacy_upgrade: task['feature_version'] = max(2, task['feature_version'])
            task.setdefault('revision', 1)
        if 'next_research_reconsider_at' not in self.runtime:
            self.runtime['next_research_reconsider_at'] = (self._lifecycle_now() + _reconsider_interval(
                self.instance.get('config', {}))).isoformat()
        # Legacy formal results without an actual executable fingerprint remain
        # unbound. A later real compiler result may establish their environment.
        if legacy_upgrade:
            targets = [key for key, item in self.instance.get('knowledge', {}).items()
                       if item.get('status') == 'verified' and not item.get('review_cycle_id')]
            for knowledge_id in targets:
                item = self.instance['knowledge'][knowledge_id]
                self.instance, self.runtime = revise_knowledge(self.instance, self.runtime, knowledge_id,
                    {'statement': item['statement']}, reason='Feature 2 requires a fresh formal check and complete identity review',
                    actor_ref='migration:' + str(self.head) + ':feature-2')
                migrated = self.instance['knowledge'][knowledge_id]
                migrated['legacy_approval_ref'] = {'snapshot': self.head, 'history_index': len(migrated['history']) - 1,
                                                   'contract_id': 'do-math-cli/1', 'feature_version': 1}
                self.runtime['queue'][:] = [a for a in self.runtime['queue'] if not
                    (a.get('target') == knowledge_id and a.get('role') in {'identity_review', 'formal_check'})]
                self._enqueue('formal_check', knowledge_id, reason='Revalidate preserved feature 1 approval under feature 2')
            if targets:
                # Feature 1's goal-audit basis hashed the complete knowledge
                # catalog, including these legacy approvals.
                for judgment in self.instance.get('goal_judgments', []):
                    if isinstance(judgment.get('basis'), str):
                        judgment.update(current=False, invalidated_reason='Legacy approval in the goal-audit basis requires revalidation')
                if self.instance.get('goal_status') in {'mathematically_solved', 'research_goal_satisfied'}:
                    self.instance['goal_status'] = 'unresolved'
                if self.runtime.get('status') == 'completed': self.runtime['status'] = 'ready'
                self._lifecycle_event('legacy_approvals_require_revalidation', source_ref=str(self.head), knowledge_ids=targets)
                self._enqueue('research_plan', reason='Legacy knowledge requires fresh formal and semantic evidence')

    def _lifecycle_event(self, kind, *, target=None, source_ref=None, schedule=True, **details):
        when = self._lifecycle_now().isoformat()
        event = {'id': new_id('EV'), 'kind': kind, 'at': when, 'opened_at': when,
                 'target': target, 'source_ref': source_ref, **deepcopy(details)}
        self.runtime['events'].append(event)
        if schedule: self.runtime['pending_events'].append(event['id'])
        return event

    def _apply_extended_control(self, request):
        action = request.get('action')
        if action not in {'decision', 'knowledge', 'trust', 'external', 'conversation'}:
            return False
        self._upgrade_runtime()
        source_ref = request.get('id')
        if not isinstance(source_ref, str) or not source_ref:
            raise ValueError('extended control requires its preserved user request ID')
        digest = _digest(request)
        old = self.runtime['extended_controls'].get(source_ref)
        if old:
            if old['sha256'] != digest:
                raise ValueError('user control ID reused with changed content')
            return True
        before_instance, before_runtime = deepcopy(self.instance), deepcopy(self.runtime)
        try:
            config = request.get('config', {})
            if not isinstance(config, dict): raise ValueError('control config must be an object')
            if action == 'decision':
                self.instance, self.runtime, result = apply_decision(self.instance, self.runtime,
                    config.get('change', {}), source_ref=source_ref, actor='user', at=self._lifecycle_now().isoformat())
                self._lifecycle_event('user_decision_applied', source_ref=source_ref, decision_id=result['id'])
            elif action == 'knowledge':
                self._knowledge_control(config, source_ref)
            elif action == 'trust':
                self._trust_control(config, source_ref)
            elif action == 'external':
                self._external_control(config, source_ref)
            else:
                self._conversation_control(config, source_ref)
            self.runtime['extended_controls'][source_ref] = {'sha256': digest, 'action': action,
                                                            'applied_at': self._lifecycle_now().isoformat()}
            self._invalidate_goal_currentness()
            self._refresh_readiness()
        except Exception:
            self.instance, self.runtime = before_instance, before_runtime
            raise
        return True

    def _invalidate_goal_currentness(self):
        judgments = self.instance.get('goal_judgments', [])
        basis = self.instance.get('goal_assessment_basis', judgments[-1].get('basis') if judgments else None)
        current = [j for j in judgments if j.get('basis') == basis] if basis is not None else judgments[-1:]
        for judgment in current:
            invalid_dependencies = [record_id for record_id in judgment.get('dependencies', [])
                if record_id in self.instance.get('knowledge', {}) and not assess_use(self.instance['knowledge'][record_id], self.instance)['valid']]
            if (judgment.get('record_basis') and not validate_basis(judgment['record_basis'], self.instance, self.runtime)['valid']) or (judgment.get('source_basis') and not sources_current(judgment['source_basis'], self.instance)) or (
                    judgment.get('goal_revision', self.instance.get('goal_revision')) != self.instance.get('goal_revision')) or (
                    judgment.get('policy_revision', self.instance.get('policy_revision')) != self.instance.get('policy_revision')) or invalid_dependencies:
                judgment['current'] = False
                judgment['invalidated_reason'] = ('A mathematical dependency is no longer usable: ' + ', '.join(invalid_dependencies)
                                                   if invalid_dependencies else 'The actual judgment basis changed')
        stale = [j for j in current if j.get('current') is False]
        if stale and self.instance.get('goal_status') in {'mathematically_solved', 'research_goal_satisfied'}:
            self.instance['goal_status'] = 'unresolved'
            if self.runtime.get('status') == 'completed': self.runtime['status'] = 'ready'
            self._lifecycle_event('goal_basis_invalidated', judgment_ids=[j.get('id', j.get('execution_id')) for j in stale])
            self._enqueue('research_plan', reason='Previously used goal evidence is no longer current')

    def _knowledge_control(self, config, source_ref):
        operation, knowledge_id = config.get('operation'), config.get('id')
        reason = config.get('reason', '')
        item = self.instance['knowledge'].get(knowledge_id)
        if item is None: raise ValueError('knowledge item does not exist')
        previous_cycle = item.get('review_cycle_id')
        if previous_cycle in self.runtime['review_cycles']:
            cycle = self.runtime['review_cycles'][previous_cycle]
            if cycle['status'] == 'working':
                cycle.update(status='unresolved', decision='unresolved', phase='ended')
                cycle.setdefault('history', []).append({'event': 'user_knowledge_change', 'source_ref': source_ref, 'reason': reason})
                for investigation in cycle.get('research', {}).values():
                    if investigation.get('status') == 'pending':
                        investigation.update(status='cancelled', cancellation={'source_ref': source_ref, 'reason': reason})
                cycle['deferred_actions'] = {}
        for execution in self.runtime['executions'].values():
            if execution.get('status') != 'ended' and execution.get('action', {}).get('target') == knowledge_id:
                execution['stop_requested'] = 'knowledge_' + str(operation)
        if operation == 'revise':
            self.instance, self.runtime = revise_knowledge(self.instance, self.runtime, knowledge_id,
                config.get('changes', {}), reason=reason, actor_ref=source_ref)
            item = self.instance['knowledge'][knowledge_id]
            item['previous_review_cycle_id'] = previous_cycle
            item.pop('review_cycle_id', None)
            if isinstance(item.get('identity_assessment'), dict):
                item['identity_assessment']['effective'] = False
                item['identity_assessment']['reason'] = 'Knowledge revision awaits a fresh full review'
            self.runtime['queue'][:] = [a for a in self.runtime['queue'] if not (a.get('target') == knowledge_id and
                (a.get('role') in {'identity_review', 'formal_check'} or (a.get('role') == 'supplemental_research' and a.get('review_cycle_id'))))]
            if item.get('lean_code'):
                self._enqueue('formal_check', knowledge_id, previous_cycle_id=previous_cycle, source_ref=source_ref)
        elif operation == 'invalidate':
            self.instance, self.runtime = invalidate_knowledge(self.instance, self.runtime, knowledge_id,
                reason=reason, actor_ref=source_ref)
            if isinstance(self.instance['knowledge'][knowledge_id].get('identity_assessment'), dict):
                self.instance['knowledge'][knowledge_id]['identity_assessment']['effective'] = False
            self.runtime['queue'][:] = [a for a in self.runtime['queue'] if not (a.get('target') == knowledge_id and
                (a.get('role') in {'identity_review', 'formal_check'} or (a.get('role') == 'supplemental_research' and a.get('review_cycle_id'))))]
        else:
            raise ValueError('knowledge operation must be revise or invalidate')
        self._lifecycle_event('knowledge_' + operation, target=knowledge_id, source_ref=source_ref, reason=reason)
        self._enqueue('research_plan', reason=reason, knowledge_id=knowledge_id, source_ref=source_ref)

    def _trust_control(self, config, source_ref):
        operation = config.get('operation')
        if operation == 'register':
            self.instance, environment_id = register_environment(self.instance, config.get('toolchain', {}),
                                                                 config.get('allowed_axioms', _DEFAULT_AXIOMS))
            self.instance['trust_environments'][environment_id]['source_ref'] = source_ref
            self._lifecycle_event('trust_environment_registered', target=environment_id, source_ref=source_ref)
        elif operation == 'transition':
            environment_id = config.get('env_id')
            environment = self.instance['trust_environments'].get(environment_id)
            if not environment or environment.get('status') == 'invalid':
                raise ValueError('transition target must be a noninvalid registered environment')
            if not environment.get('toolchain', {}).get('sha256'):
                raise ValueError('transition needs an exact executable fingerprint')
            if any(t.get('status') in {'checking', 'ready'} for t in self.runtime['trust_transitions'].values()):
                raise ValueError('a trust transition is already in progress')
            transition = begin_transition(self.instance, environment_id)
            for target in transition['targets']:
                formal = self.instance['knowledge'][target['id']].get('formal', {})
                target['signature_hash'] = formal.get('signature_hash')
                target['declaration_signatures'] = deepcopy(formal.get('declaration_signatures'))
                target['project'] = deepcopy(formal.get('toolchain', {}).get('project'))
                target['dependencies'] = deepcopy(self.instance['knowledge'][target['id']].get('dependencies', []))
            transition.update(source_ref=source_ref, opened_at=self._lifecycle_now().isoformat(), environment_sha256=_digest(environment))
            self.runtime['trust_transitions'][transition['id']] = transition
            for target in transition['targets']:
                self._enqueue('trust_check', target['id'], transition_id=transition['id'], source_ref=source_ref)
            if not transition['targets']:
                self._enqueue('trust_activate', transition_id=transition['id'], source_ref=source_ref)
            self._lifecycle_event('trust_transition_started', target=transition['id'], source_ref=source_ref)
        elif operation == 'invalidate':
            self.instance, self.runtime = invalidate_environment(self.instance, self.runtime,
                config.get('env_id'), config.get('reason', 'Trust environment invalidated by explicit user decision'))
            self._lifecycle_event('trust_environment_invalidated', target=config.get('env_id'), source_ref=source_ref)
        else:
            raise ValueError('trust operation must be register, transition or invalidate')

    def _external_control(self, config, source_ref):
        operation = config.get('operation')
        if operation == 'prepare':
            grant = self.instance.get('grants', {}).get(config.get('grant_id'))
            if not grant or grant.get('kind') != 'http': raise ValueError('HTTP operation requires an explicit HTTP grant')
            stable_source_ref = config.get('source_ref') or ('external:' + str(config['id']) if config.get('id') else source_ref)
            entry = prepare_operation(config.get('request'), config['grant_id'], stable_source_ref, config.get('id'))
            validate_operation(entry, grant, self._lifecycle_now().isoformat())
            existing = self.runtime['external_operations'].get(entry['id'])
            immutable = ('id', 'request_sha256', 'grant_id', 'source_ref')
            if existing:
                if any(existing.get(key) != entry.get(key) for key in immutable): raise ValueError('external operation ID already identifies another ledger')
                if existing.get('status') == 'prepared': self._enqueue('external_action', entry['id'], grant_id=entry['grant_id'], source_ref=source_ref)
                return
            entry['execution_id'] = new_id('EX')
            entry['created_from'] = source_ref
            self.runtime['external_operations'][entry['id']] = entry
            self._enqueue('external_action', entry['id'], grant_id=entry['grant_id'], source_ref=source_ref)
            self._lifecycle_event('external_operation_prepared', target=entry['id'], source_ref=source_ref)
        elif operation == 'reconcile':
            entry = self.runtime['external_operations'].get(config.get('id'))
            if entry is None: raise ValueError('external operation does not exist')
            entry = reconcile_operation(entry, config.get('evidence'), config.get('result'), source='user', succeeded=config.get('succeeded'))
            entry['reconciliation']['source_ref'] = source_ref
            self.runtime['external_operations'][entry['id']] = entry
            self._external_execution_record(entry)
            self._lifecycle_event('external_operation_reconciled', target=entry['id'], source_ref=source_ref,
                                  outcome=entry['status'], evidence=config['evidence'])
        elif operation == 'retry':
            entry = self.runtime['external_operations'].get(config.get('id'))
            grant_id = config.get('grant_id')
            if entry is None:
                raise ValueError('external operation does not exist')
            if entry.get('status') not in {'failed', 'cancelled'}:
                raise ValueError('only a known failed or cancelled operation can be retried')
            if not isinstance(grant_id, str) or not grant_id or grant_id != entry.get('grant_id'):
                raise ValueError('retry requires the operation\'s explicit current grant')
            grant = self.instance.get('grants', {}).get(grant_id)
            if not grant or grant.get('kind') != 'http':
                raise ValueError('retry requires an active HTTP grant')
            transmitted = entry.get('transmitted')
            if transmitted is not False and not grant.get('allow_idempotent_retry'):
                raise ValueError('retry after possible transmission requires allow_idempotent_retry')
            trial = {**entry, 'status': 'prepared'}
            validate_operation(trial, grant, self._lifecycle_now().isoformat())
            previous = {key: deepcopy(value) for key, value in entry.items()
                        if key not in {'history', 'attempts'}}
            history = [*deepcopy(entry.get('history', [])), {'action': 'retry_prepared', 'source_ref': source_ref,
                       'previous': previous, 'previous_status': entry['status'],
                       'previous_execution_id': entry.get('execution_id'), 'at': self._lifecycle_now().isoformat()}]
            attempts = deepcopy(entry.get('attempts', []))
            if attempts and 'outcome' not in attempts[-1]:
                attempts[-1].update(outcome=entry['status'], transmitted=transmitted)
            else:
                attempts.append({'request_sha256': entry['request_sha256'], 'outcome': entry['status'],
                                 'transmitted': transmitted})
            entry = deepcopy(entry)
            entry.update(status='prepared', execution_id=new_id('EX'), history=history, attempts=attempts,
                         retry_authorized=True, retried_from=source_ref, transmitted=False)
            for key in ('http_status', 'body_base64', 'body_sha256', 'error', 'credential_env', 'reconciliation', 'succeeded'):
                entry.pop(key, None)
            self.runtime['external_operations'][entry['id']] = entry
            self._enqueue('external_action', entry['id'], grant_id=grant_id, source_ref=source_ref)
            self._lifecycle_event('external_operation_retry_prepared', target=entry['id'], source_ref=source_ref,
                                  previous_status=previous['status'])
        else:
            raise ValueError('external operation must be prepare, reconcile, or retry')

    def _conversation_control(self, config, source_ref):
        operation, conversation_id, generation = config.get('operation'), config.get('id'), config.get('generation')
        if not isinstance(conversation_id, str) or not conversation_id or isinstance(generation, bool) or not isinstance(generation, int) or generation < 1:
            raise ValueError('conversation requires an ID and positive connection generation')
        current = self.runtime['conversations'].get(conversation_id)
        now = self._lifecycle_now()
        if operation == 'attach':
            policy = config.get('disconnect_policy', self.instance.get('conversation_loss_policy'))
            if policy == 'continue': policy = 'continue_authorized'
            if policy not in {'pause', 'continue_authorized'}:
                raise ValueError('conversation loss policy requires an explicit user decision')
            if current and generation <= current['generation']:
                raise ValueError('reattachment requires a new connection generation')
            lease = config.get('lease_seconds')
            if isinstance(lease, bool) or not isinstance(lease, (int, float)) or not 0 < lease < float('inf'):
                raise ValueError('conversation lease_seconds must be finite and positive')
            current = {'id': conversation_id, 'generation': generation, 'status': 'connected',
                'lease_seconds': lease, 'disconnect_policy': policy, 'attached_at': now.isoformat(),
                'last_heartbeat_at': now.isoformat(), 'lease_expires_at': (now + timedelta(seconds=lease)).isoformat(),
                'source_ref': source_ref}
            self.runtime['conversations'][conversation_id] = current
            self.instance['conversation_loss_policy'] = policy
        elif operation in {'heartbeat', 'detach'}:
            if not current or current['generation'] != generation or current['status'] != 'connected':
                raise ValueError('signal does not identify the current connected conversation generation')
            if operation == 'heartbeat':
                if timestamp(current['lease_expires_at']) <= now:
                    raise ValueError('expired generation must reconnect with a new generation')
                current.update(last_heartbeat_at=now.isoformat(), lease_expires_at=(now + timedelta(seconds=current['lease_seconds'])).isoformat(), source_ref=source_ref)
            else:
                self._lose_conversation(current, 'explicit_detach', source_ref)
        else:
            raise ValueError('conversation operation must be attach, heartbeat or detach')
        self._lifecycle_event('conversation_' + operation, target=conversation_id, source_ref=source_ref, generation=generation, schedule=False)

    def _lose_conversation(self, conversation, reason, source_ref=None):
        if conversation['status'] != 'connected': return
        conversation.update(status='lost', lost_at=self._lifecycle_now().isoformat(), loss_reason=reason)
        self._lifecycle_event('conversation_lost', target=conversation['id'], source_ref=source_ref,
                              generation=conversation['generation'], reason=reason, schedule=False)
        if self.instance.get('conversation_loss_policy', conversation['disconnect_policy']) == 'pause':
            if self.runtime.get('status') != 'closed': self.runtime['status'] = 'paused'
            self.runtime['stop_requested'] = 'conversation_lost'
            for execution in self.runtime['executions'].values():
                if execution.get('status') not in {'ended', 'finished'}:
                    execution['stop_requested'] = 'conversation_lost'

    def _check_conversations(self):
        now = self._lifecycle_now()
        changed = False
        for conversation in self.runtime.get('conversations', {}).values():
            if conversation.get('status') == 'connected' and timestamp(conversation['lease_expires_at']) <= now:
                self._lose_conversation(conversation, 'heartbeat_lease_expired')
                changed = True
        return changed

    def _refresh_readiness(self):
        self._upgrade_runtime()
        now = self._lifecycle_now()
        self._check_conversations()
        self._invalidate_goal_currentness()
        for task_id, task in self.runtime['tasks'].items():
            if task.get('status') not in _SCHEDULABLE: continue
            required = {'revision': task['revision'], 'contract_sha256': contract_hash(task),
                        'goal_revision': self.instance['goal_revision'], 'policy_revision': self.instance['policy_revision']}
            approved = any(review.get('decision') == 'approved' and review.get('inputs_current', True) and all(review.get(key) == value for key, value in required.items())
                           for review in task.get('reviews', []))
            reviewed = any(review.get('inputs_current', True) and all(review.get(key) == value for key, value in required.items()) for review in task.get('reviews', []))
            if not approved and not reviewed:
                # Older queues may have an unbound review from governance. Bind it
                # to the current contract rather than adding a duplicate request.
                candidates = [a for a in self.runtime['queue'] if a.get('role') == 'task_contract_review' and a.get('target') == task_id]
                same = next((a for a in candidates if a.get('contract_basis') == required), None)
                if same is None:
                    self.runtime['queue'][:] = [a for a in self.runtime['queue'] if a not in candidates]
                    self._enqueue('task_contract_review', task_id, contract_basis=required,
                                  reason='Current contract and policy require independent approval')
            # The source API supports legacy tasks; this integration deliberately
            # requires the stronger current-contract basis for migrated tasks.
            evaluation = task_ready(deepcopy(task), deepcopy(self.instance), deepcopy(self.runtime))
            if not approved:
                evaluation = {'state': 'not_ready', 'basis': [], 'errors': ['current revision lacks approved contract review']}
            previous = self.runtime['task_readiness'].get(task_id)
            self.runtime['task_readiness'][task_id] = {**evaluation, 'evaluated_at': now.isoformat(), 'contract_basis': required}
            if evaluation['state'] == 'ready':
                task['status'] = 'ready'
                if not previous or previous['state'] != 'ready':
                    self._lifecycle_event('task_became_ready', target=task_id, basis=evaluation['basis'])
            elif task['status'] == 'ready':
                task['status'] = 'waiting'
                self._lifecycle_event('task_readiness_lost', target=task_id, errors=evaluation['errors'])
            if evaluation['state'] == 'evaluation_error' and (not previous or previous.get('errors') != evaluation['errors']):
                self._lifecycle_event('task_condition_evaluation_error', target=task_id, errors=evaluation['errors'])
        old_pending_inputs = {event.get('target') for event in self.runtime['events']
                              if event['id'] in self.runtime['pending_events'] and event['kind'] == 'task_new_input'}
        scheduled = apply_event_schedule(self.instance, self.runtime, now.isoformat())
        duplicate_ids = {event['id'] for event in scheduled['events']
                         if event['kind'] == 'task_new_input' and event.get('target') in old_pending_inputs}
        if duplicate_ids:
            scheduled['runtime']['events'] = [event for event in scheduled['runtime']['events'] if event['id'] not in duplicate_ids]
            scheduled['runtime']['pending_events'] = [event_id for event_id in scheduled['runtime']['pending_events'] if event_id not in duplicate_ids]
        self.instance, self.runtime = scheduled['instance'], scheduled['runtime']
        if self.runtime.get('status') in {'paused', 'closed', 'completed', 'budget_exhausted'}:
            return
        events = {event['id']: event for event in self.runtime['events']}
        pending = [event_id for event_id in dict.fromkeys(self.runtime['pending_events'])
                   if not events[event_id].get('assigned_to')]
        if not pending: return
        running_ids = {execution.get('action', {}).get('id') for execution in self.runtime['executions'].values()
                       if execution.get('status') in {'starting', 'running'}}
        assigned = False
        for role in ('research_preparation', 'research_plan'):
            selected = [event_id for event_id in pending if
                        (events[event_id]['kind'] == 'research_reconsider_due') == (role == 'research_preparation')]
            if not selected: continue
            # A preparation that outlasts its interval does not reset its own
            # clock; one due event remains pending for the subsequent activity.
            if role == 'research_preparation' and any(activity.get('role') == role and activity.get('status') in {'active', 'running'}
                                                     for activity in self.runtime['activities'].values()):
                continue
            queued = next((a for a in self.runtime['queue'] if a.get('role') == role and a.get('id') not in running_ids), None)
            opened = queued is None or 'opened_at' not in queued
            if queued is None:
                self._enqueue(role, id=new_id('AC'), reason='Preserved research events require reconsideration',
                              opened_at=now.isoformat(), event_refs=selected)
                queued = self.runtime['queue'][-1]
            else:
                queued.setdefault('id', new_id('AC'))
                queued.setdefault('opened_at', now.isoformat())
                queued['event_refs'] = list(dict.fromkeys([*queued.get('event_refs', []), *selected]))
            if opened and role == 'research_preparation':
                self.runtime['next_research_reconsider_at'] = (timestamp(queued['opened_at']) + _reconsider_interval(self.instance['config'])).isoformat()
            for event_id in selected:
                events[event_id]['assigned_to'] = queued['id']
                events[event_id]['assigned_at'] = now.isoformat()
            assigned = True
        # Assignment is not consumption. The owning engine consumes only the
        # exact event_refs in an accepted execution's immutable input.
        if assigned and self.runtime.get('status') == 'waiting': self.runtime['status'] = 'ready'

    def _bind_formal_environment(self, result):
        self._upgrade_runtime()
        output = deepcopy(result)
        toolchain = output.get('toolchain')
        allowed = output.get('allowed_axioms', self.instance.get('config', {}).get('allowed_axioms', _DEFAULT_AXIOMS))
        output['allowed_axioms'] = deepcopy(allowed)
        if not isinstance(toolchain, dict) or not toolchain.get('sha256') or not toolchain.get('version'):
            output.update(trust_environment_id=None, trust_environment_status='unknown',
                          trust_environment_reason='Actual compiler fingerprint and version require a real probe')
            return output
        existing = next((env for env in self.instance['trust_environments'].values()
                         if _toolchain_matches(env.get('toolchain', {}), toolchain) and env.get('allowed_axioms') == allowed), None)
        if existing is None:
            self.instance, environment_id = register_environment(self.instance, toolchain, allowed)
            existing = self.instance['trust_environments'][environment_id]
        else:
            environment_id = existing['id']
        if self.instance.get('active_trust_environment') is None and not any(
                env.get('status') in {'invalid', 'superseded'} for env in self.instance['trust_environments'].values()):
            existing['status'] = 'active'
            self.instance['active_trust_environment'] = environment_id
        active = self.instance.get('active_trust_environment') == environment_id and existing['status'] == 'active'
        output.update(trust_environment_id=environment_id, trust_environment_status='active' if active else existing['status'])
        if not active:
            output['trust_environment_reason'] = 'An explicit complete trust transition is required before use'
        return output

    def _external_execution_record(self, operation):
        if not operation.get('execution_id'): operation['execution_id'] = new_id('EX')
        execution_id = operation['execution_id']
        http_status = operation.get('http_status')
        operation['succeeded'] = 200 <= http_status < 300 if isinstance(http_status, int) and not isinstance(http_status, bool) else None
        if operation['status'] == 'confirmed' and operation.get('reconciliation', {}).get('succeeded') is not None:
            operation['succeeded'] = operation['reconciliation']['succeeded']
        terminal = operation['status'] not in {'prepared', 'running'}
        old = self.runtime['executions'].get(execution_id, {})
        record = {**old, 'id': execution_id, 'role': 'external_action',
                  'grant_id': operation['grant_id'], 'status': 'ended' if terminal else ('starting' if operation['status'] == 'prepared' else 'running'),
                  'actor_kind': 'machine', 'action': {'role': 'external_action', 'target': operation['id']},
                  'outcome': operation['status'], 'operation_id': operation['id'],
                  'request_sha256': operation['request_sha256'], 'source_ref': operation['source_ref'],
                  'http_status': http_status, 'succeeded': operation['succeeded']}
        self.runtime['executions'][execution_id] = record
        self.runtime['external_operations'][operation['id']] = deepcopy(operation)
        if operation['status'] in {'prepared', 'running'}: self.runtime['active_execution'] = execution_id
        elif terminal and self.runtime.get('active_execution') == execution_id: self.runtime['active_execution'] = None
        if operation['status'] == 'confirmed':
            refs = self.instance.setdefault('available_input_refs', [])
            if operation['id'] not in refs: refs.append(operation['id'])

    def _process_machine_action(self, action):
        role = action.get('role')
        if role not in {'external_action', 'trust_check', 'trust_activate'}: return False
        self._upgrade_runtime()
        if role == 'external_action':
            self._run_external_action(action)
        elif role == 'trust_check':
            self._run_trust_check(action)
            if (self.runtime.get('status') == 'paused' and
                    action['target'] not in self.runtime['trust_transitions'][action['transition_id']]['results']):
                # Keep the unfinished target for an explicit resume, without repeating completed targets.
                self._save()
                return True
        else:
            self._finish_trust_transition(action['transition_id'])
        self.runtime['queue'][:] = [queued for queued in self.runtime['queue'] if queued != action]
        self._refresh_readiness()
        self._save()
        return True

    def _run_external_action(self, action):
        operation_id = action['target']
        operation = self.runtime['external_operations'][operation_id]
        if not operation.get('execution_id'): operation['execution_id'] = new_id('EX')
        if operation['status'] in {'confirmed', 'failed', 'cancelled'}: return
        if operation['status'] == 'running' and operation.get('transmitted') is False:
            # transmitted=true is published before transport, so a published false proves that no request left.
            operation.update(status='failed', error='Executor resumed before the request was transmitted')
            self._external_execution_record(operation)
            self._lifecycle_event('external_operation_failed', target=operation_id, source_ref=operation['source_ref'],
                                  request_sha256=operation['request_sha256'])
            return
        if operation['status'] in {'unknown', 'running'}:
            if operation['status'] == 'running':
                operation.update(status='unknown', error='Executor resumed without a confirmed remote outcome')
            self._external_execution_record(operation)
            self._lifecycle_event('external_reconciliation_required', target=operation_id)
            return
        grant = self.instance.get('grants', {}).get(operation['grant_id'], {})
        academic_binding = operation.get('academic_binding')
        if academic_binding and (academic_binding.get('requirements_sha256') != self.instance.get('academic_requirements', {}).get('sha256') or
                academic_binding.get('solution_basis') != self._solution_basis()):
            operation.update(status='failed', error='Academic requirement or solution basis changed before transmission', transmitted=False)
            self._external_execution_record(operation)
            return
        try:
            validate_operation(operation, grant, self._lifecycle_now().isoformat())
        except ValueError as error:
            operation.update(status='failed', error=str(error), transmitted=False)
            self._external_execution_record(operation)
            self._lifecycle_event('external_operation_not_authorized', target=operation_id, reason=str(error))
            return
        def persist(update):
            current = self.runtime['external_operations'][operation_id]
            if current['request_sha256'] != update['request_sha256'] or current['execution_id'] != update.get('execution_id'):
                return False
            if update['status'] in {'prepared', 'running'}:
                validate_operation(update, self.instance['grants'].get(update['grant_id'], {}), self._lifecycle_now().isoformat())
            self.runtime['external_operations'][operation_id] = deepcopy(update)
            self._external_execution_record(update)
            self._save()
            return True
        def should_stop():
            return bool(self.runtime.get('stop_requested') or self.runtime.get('status') in {'paused', 'closed'} or
                        self.runtime['executions'].get(operation['execution_id'], {}).get('stop_requested'))
        try:
            result = execute_operation(deepcopy(operation), deepcopy(grant), persist=persist,
                timeout_seconds=self.instance['config'].get('external_timeout_seconds', 30), should_stop=should_stop)
        except Exception as error:
            result = deepcopy(self.runtime['external_operations'][operation_id])
            result.update(status='unknown' if result.get('attempts') else 'failed', error=f'{type(error).__name__}: {error}')
            persist(result)
        self._lifecycle_event('external_operation_' + result['status'], target=operation_id,
                              source_ref=result['source_ref'], request_sha256=result['request_sha256'])

    def _run_trust_check(self, action):
        transition_id, knowledge_id = action['transition_id'], action['target']
        transition = self.runtime['trust_transitions'][transition_id]
        if transition['status'] not in {'checking', 'ready'}: return
        if knowledge_id in transition['results']:
            if transition['status'] == 'ready': self._finish_trust_transition(transition_id)
            return
        target = next((t for t in transition['targets'] if t['id'] == knowledge_id), None)
        if target is None: raise ValueError('trust check is not an assigned transition target')
        environment = self.instance['trust_environments'][transition['to_environment']]
        item = self.instance['knowledge'][knowledge_id]
        execution_id = new_id('EX')
        workspace = Path(self.instance['workspace']) / 'trust' / execution_id
        workspace.mkdir(parents=True, exist_ok=True)
        self.runtime['executions'][execution_id] = {'id': execution_id, 'role': 'trust_check', 'status': 'running',
            'action': deepcopy(action), 'source_ref': transition['source_ref'], 'created_at': self._lifecycle_now().isoformat()}
        self.runtime['active_execution'] = execution_id
        self._save()
        toolchain = environment['toolchain']
        command = toolchain.get('lean_command') or toolchain.get('configured_command') or ([toolchain['executable']] if toolchain.get('executable') else None)
        check = validate_basis([target['basis']], self.instance, self.runtime)
        stop_requested = False
        def should_stop():
            nonlocal stop_requested
            self._controls()
            if self._check_conversations(): self._save()
            stop_requested = stop_requested or bool(
                self.runtime.get('status') in {'paused', 'closed'} or self.runtime.get('stop_requested') or
                self.runtime['executions'][execution_id].get('stop_requested'))
            return stop_requested
        try:
            if not check['valid']: raise ValueError('trust transition basis changed: ' + ', '.join(check['reasons']))
            if environment.get('status') == 'invalid': raise ValueError('trust transition environment was invalidated')
            if not command: raise ValueError('trust environment has no executable command')
            import inspect
            arguments = dict(source=item['lean_code'], declarations=item['declaration_names'], workspace=workspace,
                lean_command=command, timeout_seconds=self.instance['config'].get('lean_timeout_seconds', 120),
                allowed_axioms=tuple(environment['allowed_axioms']))
            parameters = inspect.signature(self.formal_verifier).parameters
            if 'should_stop' in parameters or any(p.kind == inspect.Parameter.VAR_KEYWORD for p in parameters.values()):
                arguments['should_stop'] = should_stop
            if should_stop():
                result = {'status': 'stopped', 'reason': 'stopped before trust verification'}
            else:
                result = self.formal_verifier(**arguments)
            if should_stop():
                result = {**result, 'status': 'stopped', 'reason': 'trust verification stopped by control request'}
            if result.get('status') == 'verified' and (result.get('source_sha256') != target['source_sha256'] or
                    not _toolchain_matches(toolchain, result.get('toolchain'))):
                result = {**result, 'status': 'rejected', 'reason': 'Compiler fingerprint or source differs from the fixed transition input'}
            if result.get('status') == 'verified' and (result.get('signature_hash') != target.get('signature_hash') or
                    result.get('declaration_signatures') != target.get('declaration_signatures') or
                    result.get('toolchain', {}).get('project') != target.get('project') or
                    item.get('dependencies', []) != target.get('dependencies')):
                result['semantic_review_required'] = True
        except Exception as error:
            result = {'status': 'failed', 'reason': f'{type(error).__name__}: {error}'}
        result.update(id=knowledge_id, execution_id=execution_id, trust_environment_id=transition['to_environment'],
                      allowed_axioms=deepcopy(environment['allowed_axioms']))
        artifact = f'runtime/artifacts/{execution_id}/trust-result.json'
        result['artifact_ref'] = artifact
        self.runtime['executions'][execution_id].update(status='ended', outcome=result['status'], artifact_ref=artifact)
        self.runtime['active_execution'] = None
        if result['status'] == 'stopped' or stop_requested:
            result.update(status='stopped', reason=result.get('reason') or 'trust verification stopped')
            self.runtime['executions'][execution_id]['outcome'] = 'stopped'
            if self.runtime.get('status') != 'closed': self.runtime['status'] = 'paused'
            self._lifecycle_event('trust_target_stopped', target=knowledge_id, transition_id=transition_id,
                                  execution_id=execution_id, artifact_ref=artifact)
            self._save({artifact: canonical_json(result)})
            return
        self.runtime['trust_transitions'][transition_id] = record_transition_result(self.instance, self.runtime['trust_transitions'][transition_id], result)
        self._save({artifact: canonical_json(result)})
        self._lifecycle_event('trust_target_checked', target=knowledge_id, transition_id=transition_id, result=result['status'])
        if self.runtime['trust_transitions'][transition_id]['status'] == 'ready':
            self._finish_trust_transition(transition_id)

    def _finish_trust_transition(self, transition_id):
        transition = self.runtime['trust_transitions'][transition_id]
        if transition['status'] in {'active', 'failed'}: return
        try:
            environment = self.instance['trust_environments'].get(transition['to_environment'])
            if not environment or environment.get('status') == 'invalid' or _digest(environment) != transition.get('environment_sha256'):
                raise ValueError('target trust environment changed during transition')
            self.instance = activate_transition(self.instance, transition)
        except ValueError as error:
            transition.update(status='failed', reason=str(error))
            self._lifecycle_event('trust_transition_failed', target=transition_id, reason=str(error))
            self._enqueue('research_plan', reason='Trust transition failed; the previous environment remains in force', transition_id=transition_id)
        else:
            transition.update(status='active', activated_at=self._lifecycle_now().isoformat())
            for knowledge_id, result in transition.get('results', {}).items():
                if result.get('semantic_review_required'):
                    item = self.instance['knowledge'][knowledge_id]
                    cycle_id = self._start_identity_review(knowledge_id, previous_cycle_id=item.get('review_cycle_id'))
                    self.runtime['review_cycles'][cycle_id]['trust_transition_id'] = transition_id
                    item.setdefault('use_suspensions', []).append({'kind': 'semantic', 'transition_id': transition_id,
                        'review_cycle_id': cycle_id, 'reason': 'trust transition changed signature, project, or dependencies'})
                    item['use_suspended'] = True
            self._lifecycle_event('trust_transition_activated', target=transition_id)
