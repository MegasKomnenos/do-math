"""Engine integration for the execution lifecycle: clock, pause and resume, dispatch authority, readiness and machine executions.

Initialization adoption, knowledge, external and formal flows live in their
own engine mixins (initialization_engine, knowledge_engine, external_engine,
formal_engine); the extended control application here routes to them.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import timedelta
import hashlib
import math
import time

from .governance import apply_decision, timestamp
from .planning import (instance_ended, task_ready, contract_hash, record_due_events, contract_review_current, review_basis_key,
                       capture_task_basis, governance_revisions, assigned_event_refs, CONTRACT_REVIEW_MISSING)
from .canonical import canonical_json, exact_content_hash
from .initialization import activation_requirements, capability_requirements
from .execution_profiles import INITIAL_ROLES
from .session_slots import live_action_ids
from .state_contract import ARTIFACT_ROOT
from .task_contracts import LIFECYCLE_STATES, TERMINAL_TASK_STATUSES

_SCHEDULABLE = LIFECYCLE_STATES - TERMINAL_TASK_STATUSES


def _reconsider_interval(config):
    return timedelta(seconds=config['research_reconsider_seconds'])


def preserve_rejected_candidate(store, snapshot, *, raw, reason, clock):
    """Keep rejected bytes on the verified head, never publish the rejected state.

    Loading ``snapshot`` validates it under the state contract; a head that
    does not load is damaged and is not rewritten.
    """
    if not isinstance(raw, bytes):
        raise TypeError('candidate raw bytes required')
    try:
        _, instance, runtime = store.load(snapshot)
    except (ValueError, TypeError, KeyError, OSError, RuntimeError) as exc:
        raise ValueError('damaged current state cannot be rewritten: ' + str(exc)) from exc
    identity = clock.new_id('RJ')
    path = ARTIFACT_ROOT + identity + '/candidate.raw'
    audit = ARTIFACT_ROOT + identity + '/rejection.json'
    new_head = store.save_with_state(snapshot, instance, runtime, artifacts={path: raw, audit: canonical_json({
        'id': identity, 'candidate_ref': path, 'sha256': hashlib.sha256(raw).hexdigest(),
        'base_snapshot': snapshot, 'reason': reason, 'disposition': 'rejected_not_applied'})})[0]
    return {'snapshot': new_head, 'raw_ref': path, 'audit_ref': audit}


class LifecycleEngineMixin:
    def _lifecycle_now(self):
        clock = self.lifecycle_clock
        return timestamp(clock()) if clock else self.ports.clock.wall()


    def _lifecycle_event(self, kind, *, target=None, source_ref=None, schedule=True, **details):
        guard = self._clock_guard()
        if not guard['usable']:
            raise RuntimeError('cannot publish a lifecycle event while the clock guard blocks new actions')
        when = guard['observed_utc']
        event = {'id': self.ports.clock.new_id('EV'), 'kind': kind, 'at': when, 'opened_at': when,
                 'target': target, 'source_ref': source_ref, **deepcopy(details)}
        self.runtime['events'].append(event)
        if schedule: self.runtime['pending_events'].append(event['id'])
        self.runtime['last_observed_utc'] = when
        return event

    def _clock_guard(self):
        """A retained regression blocks authority until a verified re-observation."""
        before = self.lifecycle_monotonic()
        now = self._lifecycle_now()
        after = self.lifecycle_monotonic()
        persisted = self.runtime.get('last_observed_utc')
        if not persisted:
            return {'usable': False, 'reason': 'missing_utc_high_water'}
        previous = timestamp(persisted)
        # A reported tick is not an exact instant. Use a full reported resolution
        # on either side (covers truncation or rounding), plus representation error.
        # UTC intervals round outwards to datetime's microsecond precision; the
        # monotonic interval also includes the float's ULP at this uptime.
        wall_radius = timedelta(microseconds=math.ceil(
            time.get_clock_info('time').resolution * 1_000_000) + 1)
        mono_radius = time.get_clock_info('monotonic').resolution + max(math.ulp(before), math.ulp(after))
        anchor = self._clock_anchor
        reason = 'persisted_utc_regression' if now < previous else None
        expected = None
        if anchor is not None:
            if now < anchor[0] and reason is None:
                reason = 'live_utc_regression'
            elapsed_lower = max(0., before - mono_radius - (anchor[1] + anchor[3]))
            expected = anchor[0] - anchor[2] + timedelta(microseconds=math.floor(elapsed_lower * 1_000_000))
            if now + wall_radius < expected and reason is None:
                reason = 'live_monotonic_regression'
        if reason:
            self._clock_failure = {'usable': False, 'reason': reason,
                                   'last_observed_utc': persisted, 'observed_utc': now.isoformat(),
                                   'expected_at_least': (expected if reason == 'live_monotonic_regression'
                                                        else previous if reason == 'persisted_utc_regression'
                                                        else anchor[0]).isoformat()}
            return self._clock_failure
        if self._clock_failure:
            return self._clock_failure
        self._clock_anchor = (now, after, wall_radius, mono_radius)
        return {'usable': True, 'observed_utc': now.isoformat()}

    def _require_action_clock(self):
        guard = self._clock_guard()
        if not guard['usable']:
            raise ValueError('clock prevents new authority: ' + guard['reason'])
        return guard['observed_utc']

    def _capability_requirements(self, reference):
        return capability_requirements(self.instance, reference, at=self._lifecycle_now().isoformat())

    def _instance_closed(self):
        return instance_ended(self.instance, self.runtime)

    def _request_stop_all(self, reason):
        """Record one stop reason on every execution that has not ended."""
        for execution in self.runtime['executions'].values():
            if execution.get('status') != 'ended':
                execution['stop_requested'] = reason

    def _pause_lifecycle(self, reason):
        if self._instance_closed():
            raise ValueError('closed/completed instance cannot pause or reopen')
        lifecycle = self.instance['lifecycle']
        if lifecycle['state'] != 'paused':
            self.runtime['resume_lifecycle'] = lifecycle['state']
            lifecycle['state'] = 'paused'
        self.runtime['status'] = 'paused'
        self.runtime['stop_requested'] = reason
        lifecycle.setdefault('history', []).append({'kind': 'pause', 'id': self.ports.clock.new_id('PA'), 'reason': reason})
        self._request_stop_all(reason)

    def _conversation_live(self):
        if self.instance.get('conversation_loss_policy') != 'pause':
            return True
        now = self._lifecycle_now()
        lost = self.runtime.get('lost_conversation_generations', {})
        return any(row.get('status') == 'connected' and timestamp(row['lease_expires_at']) > now
                   and row['generation'] > lost.get(row['id'], 0)
                   for row in self.runtime.get('conversations', {}).values())

    def _resume_lifecycle(self, request):
        if self._instance_closed():
            raise ValueError('closed/completed instance cannot resume')
        if request.get('origin', 'user') != 'user' and (
                self.runtime.get('user_pause') or self.runtime.get('model_policy_violation')
                or self.runtime.get('stop_requested') == 'conversation_lost'):
            raise ValueError('an effective user pause requires an explicit user resume')
        expected = request.get('config', {}).get('expected_user_pause_reason')
        if expected is not None and self.runtime.get('user_pause', {}).get('reason') != expected:
            raise ValueError('the effective user pause is not the released HOLD')
        self._require_action_clock()
        if not self._conversation_live():
            raise ValueError('conversation pause requires a live new connection generation')
        target = self.runtime.get('resume_lifecycle', self.instance['lifecycle']['state'])
        if target not in {'initializing', 'active'}:
            raise ValueError('resume lifecycle is missing')
        # Resume restores lifecycle, not expired permissions or tool evidence.
        # Each dispatch rechecks those facts; maintenance/transition recovery must remain possible.
        self.instance['lifecycle']['state'] = target
        self.runtime['status'] = 'initializing' if target == 'initializing' else 'ready'
        self.runtime.pop('stop_requested', None)
        if request.get('origin', 'user') == 'user':
            self.runtime.pop('user_pause', None)
            self.runtime.pop('model_policy_violation', None)
        self.runtime.pop('resume_lifecycle', None)


    def _activate_initialization(self):
        if self._instance_closed():
            raise ValueError('closed/completed instance cannot activate')
        lifecycle = self.instance['lifecycle']
        if lifecycle['state'] != 'initializing':
            return {'activated': lifecycle['state'] == 'active', 'missing': []}
        self._require_action_clock()
        from .session_slots import quiescence
        self.runtime['recovery_checked'] = not any(quiescence(self.runtime).values())
        requirements = activation_requirements(self.instance, self.runtime, at=self._lifecycle_now().isoformat(),
            owner_handlers=self.governance_owner_handlers())
        lifecycle.setdefault('activation', {})['missing'] = requirements['missing']
        lifecycle['activation']['observation_errors'] = requirements['observation_errors']
        if not requirements['satisfied']:
            self.runtime['status'] = 'initializing'
            self.runtime['availability'] = {'state': 'blocked', 'reason': 'initialization_incomplete',
                                            'next_owner': 'user'}
            return {'activated': False, **requirements}
        self._lifecycle_event('initialization_activated', target=self.instance.get('id'))
        lifecycle['state'] = 'active'
        lifecycle['activated_at'] = self._lifecycle_now().isoformat()
        self.runtime['status'] = 'ready'
        self.runtime['availability'] = {'state': 'available'}
        self.runtime['next_research_reconsider_at'] = (self._lifecycle_now() + _reconsider_interval(self.instance['config'])).isoformat()
        from .knowledge_records import knowledge_view
        initial_role = 'research_plan' if knowledge_view(self.instance) else 'research_preparation'
        # The first reader owns initialization facts; assignment is not
        # consumption, and later user events are never added to its fixed input.
        self._enqueue(initial_role, reason='initialization activation',
                      event_refs=list(dict.fromkeys(self.runtime['pending_events'])))
        return {'activated': True, **requirements}

    def _action_lifecycle_gate(self, action):
        """Admit the action under the current lifecycle, authority and clock; return its profile.

        Selecting the profile records the action's profile reference and actor kind.
        """
        if self._instance_closed():
            raise ValueError('closed/completed instance cannot dispatch')
        self._require_action_clock()
        profile = self._execution_profile(action)
        lifecycle = self.instance['lifecycle']['state']
        if lifecycle == 'paused' and self._limited_recovery_allowed(action):
            return profile
        if lifecycle == 'paused' or not self._conversation_live():
            raise ValueError('lifecycle or conversation prevents dispatch')
        if lifecycle == 'initializing':
            from .initialization import grant_current
            adoption = self.instance['lifecycle'].get('adoption', {})
            if action['role'] in {'trust_check', 'trust_activate'}:
                transition = self.runtime['trust_transitions'].get(action.get('transition_id'), {})
                if not transition.get('source_ref'):
                    raise ValueError('trust preparation requires explicit transition authority')
                return profile
            if action['role'] not in INITIAL_ROLES:
                raise ValueError('research dispatch waits for initialization')
            gid = action.get('grant_id')
            candidates = {g: self.instance['grants'][g] for g in adoption.get('initial_grant_ids', [])
                          if grant_current(self.instance, g, self._lifecycle_now(), initial=True)}
            if gid is not None and gid not in candidates:
                raise ValueError('narrow initial operating grant required')
            from .governance import authorize
            authority = authorize({**self.instance, 'grants': candidates}, action,
                                  self._lifecycle_now().isoformat(), runtime=self.runtime)
            if not authority['allowed']:
                raise ValueError('initial operating authority: ' + authority['reason'])
            action['grant_id'] = authority['grant_id']
            if action['role'] == 'intent_interpretation':
                action.setdefault('profile_ref', adoption.get('initial_profile_ref'))
                if action['profile_ref'] != adoption.get('initial_profile_ref'):
                    raise ValueError('initial interpretation must use its adopted exact profile')
        elif lifecycle == 'active':
            if action['role'] == 'external_action' and self.instance['lifecycle'].get('adoption', {}).get('external_policy') != 'explicit_grants':
                raise ValueError('the adopted policy does not permit external effects')
            initial_ids = self.instance['lifecycle'].get('adoption', {}).get('initial_grant_ids', [])
            if action.get('grant_id') and (action['grant_id'] in initial_ids or
                    self.instance['grants'].get(action['grant_id'], {}).get('initialization_only')):
                raise ValueError('initialization authority cannot authorize research')
            if action['role'] not in {'trust_check', 'trust_activate', 'external_action'}:
                from .governance import authorize
                candidates = self.instance['lifecycle'].get('adoption', {}).get('research_grant_ids', [])
                grants = {gid: grant for gid, grant in self.instance['grants'].items()
                          if gid not in initial_ids and not grant.get('initialization_only') and
                          (action.get('grant_id') is not None or gid in candidates)}
                authority = authorize({**self.instance, 'grants': grants}, action,
                                      self._lifecycle_now().isoformat(), runtime=self.runtime)
                if not authority['allowed']:
                    raise ValueError('research authority: ' + authority['reason'])
                action['grant_id'] = authority['grant_id']
        else:
            raise ValueError('invalid lifecycle state')
        return profile

    @staticmethod
    def _recovery_action_basis(action):
        transient = {'repair', 'dispatch_wait', 'model_selection', 'owner_activity_id', 'activity_id',
                     'execution_id', 'continuation_of', 'actor_kind'}
        return exact_content_hash({k: v for k, v in action.items() if k not in transient})

    def _recovery_pause_basis(self):
        return exact_content_hash({key:self.runtime.get(key) for key in
                        ('stop_requested', 'user_pause', 'model_policy_violation', 'resume_lifecycle')})

    def _limited_recovery_control(self, change, source_ref):
        if self.instance['lifecycle']['state'] != 'paused' or self.runtime.get('status') != 'paused':
            raise ValueError('limited recovery requires paused research')
        actions = [a for a in self.runtime['queue'] if a.get('id') == change.get('action_id')]
        if len(actions) != 1:
            raise ValueError('limited recovery must name one existing queued action')
        action = actions[0]
        if action['role'] not in {'maintenance', 'trust_check', 'trust_activate'}:
            raise ValueError('limited recovery cannot authorize ordinary research')
        for field in ('procedure', 'purpose', 'grant_id', 'expires_at'):
            if not isinstance(change.get(field), str) or not change[field].strip():
                raise ValueError('limited recovery requires ' + field)
        from .execution_profiles import match_profile_ref
        profile = match_profile_ref(self.instance['execution_profiles'], change['profile_ref'])
        if profile['role'] != action['role']:
            raise ValueError('limited recovery requires the exact role profile')
        if timestamp(change['expires_at']) <= self._lifecycle_now():
            raise ValueError('limited recovery approval has expired')
        action.update(grant_id=change['grant_id'], purpose=change['purpose'], profile_ref=deepcopy(change['profile_ref']))
        self._execution_profile(action)  # Also enforce the current role/model selection contract.
        action.setdefault('lineage_id', action['id'])
        pause = self.instance['lifecycle']['history'][-1]['id']
        action.setdefault('repair', {})['limited_recovery'] = {
            'source_ref': source_ref, 'pause_id': pause, 'action_sha256': self._recovery_action_basis(action),
            'procedure': change['procedure'], 'expires_at': change['expires_at'],
            'pause_basis': self._recovery_pause_basis()}
        self._lifecycle_event('limited_recovery_approved', target=action['id'], source_ref=source_ref,
            schedule=False, basis={**deepcopy(action['repair']['limited_recovery']),
                                   'approval_sha256': exact_content_hash(change)})
        # Validate against the just-preserved request before the common control
        # handler publishes it in extended_controls. No second authority ledger.
        self._check_limited_recovery(action, change=change)

    def _check_limited_recovery(self, action, *, change=None):
        from .execution_profiles import match_profile_ref
        from .governance import authorize
        lifecycle = self.instance['lifecycle']
        if (lifecycle['state'] != 'paused' or self.runtime.get('status') != 'paused'
                or lifecycle.get('permanently_closed')):
            raise ValueError('limited recovery requires paused, nonclosed research')
        binding = action.get('repair', {}).get('limited_recovery', {})
        if (binding.get('pause_id') != lifecycle.get('history', [{}])[-1].get('id')
                or binding.get('pause_basis') != self._recovery_pause_basis()
                or binding.get('action_sha256') != self._recovery_action_basis(action)):
            raise ValueError('limited recovery action or pause changed')
        if change is None:
            request = self.runtime['extended_controls'][binding['source_ref']]['request']
            if request.get('origin', 'user') != 'user':
                raise ValueError('limited recovery requires user approval')
            change = request['config']['change']
        approvals = [event for event in self.runtime['events']
                     if event.get('kind') == 'limited_recovery_approved' and event.get('source_ref') == binding.get('source_ref')]
        expected = {**binding, 'approval_sha256': exact_content_hash(change)}
        if len(approvals) != 1 or approvals[0].get('basis') != expected or approvals[0].get('target') != action.get('id'):
            raise ValueError('limited recovery lacks its immutable approval binding')
        if (change.get('kind') != 'limited_recovery' or change.get('action_id') != action.get('id')
                or change.get('grant_id') != action.get('grant_id') or change.get('purpose') != action.get('purpose')
                or change.get('profile_ref') != action.get('profile_ref')
                or change.get('procedure') != binding.get('procedure')
                or change.get('expires_at') != binding.get('expires_at')
                or timestamp(change['expires_at']) <= self._lifecycle_now()):
            raise ValueError('limited recovery no longer matches its approval')
        profile = match_profile_ref(self.instance['execution_profiles'], action['profile_ref'])
        if (profile['role'] != action['role']
                or action['role'] not in {'maintenance', 'trust_check', 'trust_activate'}):
            raise ValueError('limited recovery profile or role is outside scope')
        request = {**action, 'actor_kind': profile['actor_kind']}
        authority = authorize(self.instance, request, self._lifecycle_now().isoformat(), runtime=self.runtime)
        if not authority['allowed']:
            raise ValueError('limited recovery authority: ' + authority['reason'])
        if not self._capability_requirements(action['profile_ref'])['satisfied']:
            raise ValueError('limited recovery capability evidence is unavailable')

    def _limited_recovery_allowed(self, action):
        """A request without a limited recovery binding is not allowed; a stale binding is refused."""
        if not action.get('repair', {}).get('limited_recovery'):
            return False
        try:
            self._check_limited_recovery(action)
            return True
        except ValueError:
            return False

    def _execution_stop_requested(self, action, execution=None):
        """Central runners use this instead of a blanket paused-state veto."""
        if not self._clock_guard()['usable']:
            return True
        if self._instance_closed() or (execution or {}).get('stop_requested'):
            return True
        if self.instance['lifecycle']['state'] == 'paused':
            return not self._limited_recovery_allowed(action)
        return bool(self.runtime.get('stop_requested') or not self._conversation_live())

    def _apply_extended_control(self, request):
        action = request.get('action')
        if action not in {'close', 'pause', 'resume', 'decision', 'knowledge', 'trust', 'external', 'conversation'}:
            return False
        if action == 'close' and self.runtime.get('status') == 'closed':
            return True
        if self._instance_closed():
            raise ValueError('closed/completed instance cannot apply lifecycle controls')
        source_ref = request.get('id')
        if not isinstance(source_ref, str) or not source_ref:
            raise ValueError('extended control requires its preserved user request ID')
        if action == 'close':
            lifecycle = self.instance['lifecycle']
            lifecycle['permanently_closed'] = True
            lifecycle.setdefault('history', []).append({'kind':'closed', 'source_ref':source_ref})
            self.runtime.update(status='closed', stop_requested='closed', queue=[])
            self.runtime.pop('resume_lifecycle', None)
            self._request_stop_all('closed')
            return True
        if action == 'pause':
            self._pause_lifecycle('user_pause')
            if request.get('origin', 'user') == 'user':
                self.runtime['user_pause'] = {'request_id': source_ref, 'reason': request.get('text', ''),
                                              'created_at': request.get('created_at')}
            return True
        if action == 'resume':
            self._resume_lifecycle(request)
            return True
        self._require_action_clock()
        digest = exact_content_hash(request)
        old = self.runtime['extended_controls'].get(source_ref)
        if old:
            if exact_content_hash(old['request']) != digest:
                raise ValueError('user control ID reused with changed content')
            return True
        before_instance, before_runtime = deepcopy(self.instance), deepcopy(self.runtime)
        try:
            config = request.get('config', {})
            if not isinstance(config, dict): raise ValueError('control config must be an object')
            from .governance import preserve_source
            source = preserve_source(source_ref, request.get('text') or canonical_json(request).decode('utf-8'),
                                     origin=request.get('origin', 'user'))
            existing = self.instance.setdefault('governance_sources', {}).get(source_ref)
            if existing is not None and existing != source:
                raise ValueError('preserved control source ID reused')
            self.instance['governance_sources'][source_ref] = source
            if action == 'decision' and config.get('change', {}).get('kind') == 'initialization':
                if request.get('origin', 'user') != 'user':
                    raise ValueError('initialization adoption requires user authority')
                self._initialization_control(config['change'], source_ref)
            elif action == 'decision' and config.get('change', {}).get('kind') == 'limited_recovery':
                if request.get('origin', 'user') != 'user':
                    raise ValueError('limited recovery requires explicit user authority')
                self._limited_recovery_control(config['change'], source_ref)
            elif action == 'decision':
                if config.get('change', {}).get('kind') == 'repetition_continue' and request.get('origin', 'user') != 'user':
                    raise ValueError('repetition continuation requires explicit user authority')
                self.instance, self.runtime, result = apply_decision(self.instance, self.runtime,
                    config.get('change', {}), source_ref=source_ref, actor='user', at=self._lifecycle_now().isoformat(), clock=self.ports.clock)
                self._lifecycle_event('user_decision_applied', source_ref=source_ref, decision_id=result['id'])
            elif action == 'knowledge':
                self._knowledge_control(config, source_ref)
            elif action == 'trust':
                self._trust_control(config, source_ref)
            elif action == 'external':
                self._external_control(config, source_ref)
            else:
                self._conversation_control(config, source_ref)
            # Owner decision APIs return candidate requests. Give each its
            # durable identity at this application boundary, before storage.
            for queued in self.runtime['queue']:
                queued.setdefault('id', self.ports.clock.new_id('AC'))
                queued.setdefault('lineage_id', queued['id'])
            self.runtime['extended_controls'][source_ref] = {'request': deepcopy(request), 'action': action,
                                                            'processed_at': self._lifecycle_now().isoformat()}
            self._invalidate_goal_currentness()
            if self.instance['lifecycle']['state'] == 'initializing':
                self._queue_initial_intent()
                self._activate_initialization()
            else:
                self._refresh_readiness()
        except Exception as error:
            self.instance, self.runtime = before_instance, before_runtime
            rejection = preserve_rejected_candidate(self.store, self.head, raw=canonical_json(request), clock=self.ports.clock,
                reason=f'{type(error).__name__}: {error}')
            self.head = rejection['snapshot']
            self._evaluate_stops()
            raise
        return True

    def _conversation_control(self, config, source_ref):
        operation, conversation_id, generation = config.get('operation'), config.get('id'), config.get('generation')
        if not isinstance(conversation_id, str) or not conversation_id or isinstance(generation, bool) or not isinstance(generation, int) or generation < 1:
            raise ValueError('conversation requires an ID and positive connection generation')
        current = self.runtime['conversations'].get(conversation_id)
        now = self._lifecycle_now()
        def lease_expiry(seconds):
            try:
                return (now + timedelta(seconds=seconds)).isoformat()
            except OverflowError as error:
                raise ValueError('conversation lease exceeds the supported timestamp range') from error
        if operation == 'attach':
            policy = config.get('disconnect_policy', self.instance.get('conversation_loss_policy'))
            if policy not in {'pause', 'continue_authorized'}:
                raise ValueError('conversation loss policy requires an explicit user decision')
            if current and generation <= current['generation']:
                raise ValueError('reattachment requires a new connection generation')
            lease = config.get('lease_seconds')
            if isinstance(lease, bool) or not isinstance(lease, (int, float)) or not 0 < lease < float('inf'):
                raise ValueError('conversation lease_seconds must be finite and positive')
            current = {'id': conversation_id, 'generation': generation, 'status': 'connected',
                'lease_seconds': lease, 'disconnect_policy': policy, 'attached_at': now.isoformat(),
                'last_heartbeat_at': now.isoformat(), 'lease_expires_at': lease_expiry(lease),
                'source_ref': source_ref}
            self.runtime['conversations'][conversation_id] = current
            self.instance['conversation_loss_policy'] = policy
        elif operation in {'heartbeat', 'detach'}:
            if not current or current['generation'] != generation or current['status'] != 'connected':
                raise ValueError('signal does not identify the current connected conversation generation')
            if operation == 'heartbeat':
                if timestamp(current['lease_expires_at']) <= now:
                    raise ValueError('expired generation must reconnect with a new generation')
                current.update(last_heartbeat_at=now.isoformat(), lease_expires_at=lease_expiry(current['lease_seconds']), source_ref=source_ref)
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
            self.runtime.setdefault('lost_conversation_generations', {})[conversation['id']] = conversation['generation']
            if self.runtime.get('status') != 'closed': self._pause_lifecycle('conversation_lost')
            self._request_stop_all('conversation_lost')

    def _check_conversations(self):
        now = self._lifecycle_now()
        changed = False
        for conversation in self.runtime.get('conversations', {}).values():
            if conversation.get('status') == 'connected' and timestamp(conversation['lease_expires_at']) <= now:
                self._lose_conversation(conversation, 'heartbeat_lease_expired')
                changed = True
        return changed

    def _record_readiness(self, task_id, evaluation, when):
        previous = self._task_readiness.get(task_id, {})
        if {k: v for k, v in previous.items() if k != 'evaluated_at'} != evaluation:
            self._task_readiness[task_id] = {**evaluation, 'evaluated_at': when}

    def _refresh_readiness(self):
        guard = self._clock_guard()
        if not guard['usable']:
            self.runtime['clock_guard'] = {'state': 'blocked', **guard}
            self.runtime['availability'] = {'state': 'blocked', 'reason': 'clock_regression'}
            if not self._instance_closed():
                self._pause_lifecycle('clock_regression')
            return
        if self.instance['lifecycle']['state'] == 'paused':
            return
        if self._instance_closed():
            return
        if self.instance['lifecycle']['state'] == 'initializing':
            self._queue_initial_intent()
            self._activate_initialization()
            if self.instance['lifecycle']['state'] == 'initializing':
                return
        self._retire_closed_revision_targets()
        self._retire_sealed_goal_audit_requests()
        self._reconcile_revision_delegations()
        live_actions = live_action_ids(self.runtime)
        for action in list(self.runtime['queue']):
            if action.get('id') in live_actions:
                continue
            self._bind_revision_action(action)
            self._cancel_selected_revision_targets(action)
        from .planning import revision_cycles
        cycles = revision_cycles(self.instance, self.runtime)
        if cycles != self.runtime.get('revision_cycles', []):
            self.runtime['revision_cycles'] = cycles
            if cycles:
                self._enqueue('research_plan', reason='Explicit revision dependencies form a cycle; combine or redesign the recorded obligations', revision_cycles=cycles)
        now = self._lifecycle_now()
        evaluation_context = {**self._evaluation_context(), 'now': now.isoformat()}
        from .task_scope import refresh_task_assessments
        changed_assessments = refresh_task_assessments(self.instance, self.runtime,
            evaluation_context=evaluation_context)
        reassess = [tid for tid in changed_assessments
            if self.runtime['tasks'][tid].get('status') not in TERMINAL_TASK_STATUSES
            and self.runtime['tasks'][tid].get('results')]
        if reassess:
            self._enqueue('research_plan', reason='Assessment evidence changed; reassess existing results: '
                          + ', '.join(sorted(reassess)))
        for task_id, task in self.runtime['tasks'].items():
            assessment = task.get('assessment', {})
            if task.get('status') not in TERMINAL_TASK_STATUSES or assessment.get('current') is not False:
                continue
            basis = exact_content_hash({key: assessment.get(key) for key in
                ('execution_id', 'contract_sha256', 'results_sha256', 'basis')})
            if not any(event['kind'] == 'task_assessment_invalidated' and event.get('target') == task_id
                       and event.get('basis_sha256') == basis for event in self.runtime['events']):
                self._lifecycle_event('task_assessment_invalidated', target=task_id,
                    source_ref=assessment.get('execution_id'), basis_sha256=basis, next_owner='research_plan',
                    reason=assessment.get('invalidated_reason', 'Recorded terminal assessment is no longer current'))
        self._check_conversations()
        self._invalidate_goal_currentness()
        self._retry_observation_configuration()
        missing_assessments = self._ensure_model_assessments()
        editions = governance_revisions(self.instance)
        for task_id, task in self.runtime['tasks'].items():
            if task.get('status') not in _SCHEDULABLE:
                self._task_readiness.pop(task_id, None)
                continue
            if task_id in missing_assessments:
                self._record_readiness(task_id, {'state': 'not_ready', 'basis': [],
                    'errors': ['model assessment or observation rules required before contract review']}, now.isoformat())
                continue
            from .model_policy import work_profile_selection
            try:
                work_profile_selection(self.instance['config'], task, self.instance)
            except ValueError as error:
                owner='governance' if task.get('academic_requirement_id') else 'research_preparation'
                reason='work profile requirement: '+str(error)
                self._record_readiness(task_id, {'state':'not_ready','basis':[], 'errors':[reason],
                    'waits':[{'kind':'contract_revision','target_refs':[task_id],'next_owner':owner}]}, now.isoformat())
                from .task_contracts import returned_task_ids
                live=any(e['status']!='ended' and e.get('action',{}).get('target')==task_id
                         for e in self.runtime['executions'].values())
                if (owner=='research_preparation' and not live and task.get('status') in {'planned','waiting'}
                        and task_id not in returned_task_ids(self.runtime['tasks'])):
                    self._enqueue('research_preparation', task_id,
                        reason='Reprepare the unchanged research obligation with a permitted current work profile: '+str(error))
                continue
            required = {'revision': task['revision'], 'contract_sha256': contract_hash(task), **editions}
            # One premise snapshot serves the review key and every recorded review of this task.
            task_basis = capture_task_basis(task, self.instance, self.runtime)
            review_key = review_basis_key(task, self.instance, self.runtime, task_basis=task_basis)
            for review in task.get('reviews', []):
                currentness = contract_review_current(review, task, self.instance, self.runtime, task_basis=task_basis)
                review['inputs_current'] = currentness['valid']
                if currentness['changes']:
                    review['currentness_changes'] = currentness['changes']
                else:
                    review.pop('currentness_changes', None)
            # inputs_current, set just above, already compares every review with `required`.
            approved = any(review['inputs_current'] and review.get('decision') == 'approved'
                           for review in task.get('reviews', []))
            reviewed = any(review['inputs_current'] for review in task.get('reviews', []))
            blocked_review = any(entry.get('action', {}).get('role') == 'task_contract_review'
                and entry['action'].get('target') == task_id
                and entry['action'].get('contract_basis') == required
                and entry['action'].get('review_basis_key') == review_key
                for entry in self.runtime.get('waiting_actions', {}).values())
            # A review already running on this contract is not doubled when only its outside premises
            # moved; once it ends, its own currentness check above decides whether another is needed.
            live_review = any(execution.get('status') != 'ended' and execution.get('action', {}).get('role') == 'task_contract_review'
                and execution['action'].get('target') == task_id and execution['action'].get('contract_basis') == required
                for execution in self.runtime['executions'].values())
            if not reviewed and not blocked_review and not live_review:
                candidates = [a for a in self.runtime['queue'] if a.get('role') == 'task_contract_review' and a.get('target') == task_id]
                same = next((a for a in candidates if a.get('contract_basis') == required and a.get('review_basis_key') == review_key), None)
                if same is None:
                    self.runtime['queue'][:] = [a for a in self.runtime['queue'] if a not in candidates]
                    self._enqueue('task_contract_review', task_id, contract_basis=required, review_basis_key=review_key,
                                  reason='Current contract and policy require independent approval')
            evaluation = (deepcopy(task_ready(task, self.instance, self.runtime,
                                    action={'role': 'research_work', 'target': task_id, 'actor_kind': 'ai'},
                                    evaluation_context=evaluation_context)) if approved else
                          {'state': 'not_ready', 'basis': [], 'errors': [CONTRACT_REVIEW_MISSING]})
            previous = self._task_readiness.get(task_id)
            self._record_readiness(task_id, {**evaluation, 'contract_basis': required}, now.isoformat())
            if evaluation['state'] == 'ready':
                if not previous or previous['state'] != 'ready' and not previous.get('dispatch_occupied'):
                    self._lifecycle_event('task_became_ready', target=task_id,
                                          basis={'records': evaluation['basis']})
            elif previous and (previous['state'] == 'ready' or
                               previous.get('dispatch_occupied') and not evaluation.get('dispatch_occupied')):
                self._lifecycle_event('task_readiness_lost', target=task_id, errors=evaluation['errors'],
                                      basis={'dispatch_occupied': evaluation.get('dispatch_occupied', False)},
                                      schedule=not evaluation.get('dispatch_occupied', False))
            if evaluation['state'] == 'evaluation_error' and (not previous or previous.get('errors') != evaluation['errors']):
                self._lifecycle_event('task_condition_evaluation_error', target=task_id, errors=evaluation['errors'])
        record_due_events(self.instance, self.runtime, now.isoformat())
        # An ended instance returned above (_instance_closed); only a lost conversation pauses here.
        if self.runtime.get('status') == 'paused':
            return
        self._schedule_reconsideration(now.isoformat())
        events = {event['id']: event for event in self.runtime['events']}
        assigned_refs = assigned_event_refs(self.runtime)
        pending = [event_id for event_id in dict.fromkeys(self.runtime['pending_events'])
                   if event_id not in assigned_refs]
        if not pending: return
        running_ids = live_action_ids(self.runtime)
        assigned = False
        for role in ('research_preparation', 'research_plan'):
            selected = [event_id for event_id in pending if
                        (events[event_id]['kind'] == 'research_reconsider_due') == (role == 'research_preparation')]
            if not selected: continue
            # A preparation that outlasts its interval does not reset its own
            # clock; one due event remains pending for the subsequent activity.
            if role == 'research_preparation' and any(
                    activity.get('activity_kind') == role and activity.get('status') == 'working'
                    for activity in self.runtime['activities'].values()):
                continue
            queued = next((a for a in self.runtime['queue'] if a.get('role') == role and a.get('id') not in running_ids
                           and 'assessment_targets' not in a and 'observation_rule_targets' not in a), None)
            opened = queued is None or 'opened_at' not in queued
            if queued is None:
                self._enqueue(role, id=self.ports.clock.new_id('AC'), reason='Preserved research events require reconsideration',
                              opened_at=now.isoformat(), event_refs=selected)
                queued = self.runtime['queue'][-1]
            else:
                queued.setdefault('id', self.ports.clock.new_id('AC'))
                queued.setdefault('opened_at', now.isoformat())
                queued['event_refs'] = list(dict.fromkeys([*queued.get('event_refs', []), *selected]))
            if opened and role == 'research_preparation':
                self.runtime['next_research_reconsider_at'] = (timestamp(queued['opened_at']) + _reconsider_interval(self.instance['config'])).isoformat()
            assigned = True
        # Assignment is not consumption. The owning engine consumes only the
        # exact event_refs in an accepted execution's immutable input.
        if assigned and self.runtime.get('status') == 'waiting': self.runtime['status'] = 'ready'

    def _release_machine_execution(self, execution, *, at):
        """Mark the local call returned and return its capacity; False holds it at the termination barrier."""
        from .execution_lifecycle import release_or_hold
        from .launch import mark_returned
        if execution.get('launch_ticket'):
            mark_returned(execution['launch_ticket'])
        return release_or_hold(execution, self._session_slots(), at=at)

    def _end_machine_execution(self, execution, *, outcome, disposition):
        """The one ending of a machine execution: release its capacity, then end it."""
        from .execution_lifecycle import transition_execution
        at = self._lifecycle_now().isoformat()
        if execution['status'] == 'ended':
            return True
        if not self._release_machine_execution(execution, at=at):
            return False
        if execution['status'] in {'starting', 'running'}:
            transition_execution(execution, 'stopping', at=at, reason='local machine call returned')
        transition_execution(execution, 'ended', at=at, outcome=outcome, disposition=disposition)
        return True

    def _lean_machine_call(self, execution_id, invocation, *, source, declarations, workspace, environment,
                           binding, should_stop, stopped_reason):
        """Run one Lean machine calculation unless it is stopped first; return its result.

        Formal and trust checks start the verifier with the same arguments: the
        frozen command and toolchain (``invocation``), the approved axioms and the
        launch ticket. ``should_stop`` is the owner's stop judgment.
        """
        arguments = dict(source=source, declarations=declarations, workspace=workspace,
                         environment=environment, binding=binding, verifier=self.formal_verifier, **invocation,
                         allowed_axioms=tuple(environment['allowed_axioms']),
                         launch_ticket=deepcopy(self.runtime['executions'][execution_id]['launch_ticket']),
                         should_stop=should_stop)
        if should_stop():
            return {'status': 'stopped', 'reason': stopped_reason}
        result = yield execution_id, arguments
        self._live_execution_ids.discard(execution_id)
        return result

    def _preserve_machine_return(self, execution_id, reference, result, **fields):
        """Publish a returned calculation as ``reference`` before any judgment of it.

        The execution's result reference names this evidence until the judged
        result replaces it; ``fields`` are recorded with it.
        """
        self.runtime['executions'][execution_id].update(result_ref=reference, raw_result_ref=reference, **fields)
        self._save({reference: canonical_json(result)})

    def _process_machine_action(self, action):
        """Start one machine action; this lifecycle gate is the last one before its start."""
        role = action.get('role')
        if role not in {'external_action', 'trust_check', 'trust_activate'}: return False
        self._action_lifecycle_gate(action)
        if role == 'external_action':
            completed = self._run_external_action(action)
        elif role == 'trust_check':
            completed = self._run_trust_check(action)
            if (self.runtime.get('status') == 'paused' and
                    action['target'] not in self.runtime['trust_transitions'][action['transition_id']]['results']):
                # Keep the unfinished target for an explicit resume, without repeating completed targets.
                self._save()
                return True
        else:
            completed = self._run_trust_activation(action)
        if completed is False:
            self._save()
            return True
        self.runtime['queue'][:] = [queued for queued in self.runtime['queue'] if queued != action]
        self._refresh_readiness()
        self._save()
        return True
