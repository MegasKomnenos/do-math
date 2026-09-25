"""Engine integration for currentness, scheduling, authority and external effects."""
from __future__ import annotations

from copy import deepcopy
from datetime import timedelta
import hashlib
import json
import math
import time
from pathlib import Path

from .external import prepare_operation, validate_operation, execute_operation, reconcile_operation, prepare_retry, recover_operation
from .governance import apply_decision, timestamp
from .knowledge import (revise_knowledge, invalidate_knowledge, register_environment,
    begin_transition, record_transition_result, activate_transition, invalidate_environment,
    validate_basis, assess_use)
from .planning import (task_ready, contract_hash, apply_event_schedule, contract_review_current, review_basis_key,
                       capture_task_basis)
from .input_basis import sources_current
from .repository import canonical_json, new_id
from .initialization import activation_requirements, capability_requirements, governance_working_view

from .trust_validation import AXIOMS
_SCHEDULABLE = {'planned', 'waiting', 'active'}


def _digest(value):
    return hashlib.sha256(canonical_json(value)).hexdigest()


def _reconsider_interval(config):
    seconds = config.get('research_reconsider_seconds', 86400)
    if isinstance(seconds, bool) or not isinstance(seconds, int) or seconds <= 0:
        raise ValueError('research_reconsider_seconds must be a positive integer')
    return timedelta(seconds=seconds)


def _toolchain_matches(expected, actual):
    return isinstance(actual, dict) and bool(actual.get('sha256')) and expected == actual


class LifecycleEngineMixin:
    def _verify_current_head(self):
        store = getattr(self, 'store', None)
        if not callable(getattr(store, 'load', None)):
            return  # Pure mixin fixtures have no persisted head.
        if getattr(self, '_verified_lifecycle_head', None) == self.head:
            return
        from .preflight import inspect_persisted_state
        report = inspect_persisted_state(store, self.head)
        if not report['valid']:
            raise ValueError('damaged current state; no recovery write allowed: ' + str(report['errors']))
        self._verified_lifecycle_head = self.head

    def _lifecycle_now(self):
        clock = getattr(self, 'lifecycle_clock', None)
        return timestamp(clock() if clock else None)


    def _lifecycle_event(self, kind, *, target=None, source_ref=None, schedule=True, **details):
        guard = self._clock_guard()
        if not guard['usable']:
            raise RuntimeError('cannot publish a lifecycle event while the clock guard blocks new actions')
        when = guard['observed_utc']
        event = {'id': new_id('EV'), 'kind': kind, 'at': when, 'opened_at': when,
                 'target': target, 'source_ref': source_ref, **deepcopy(details)}
        self.runtime['events'].append(event)
        if schedule: self.runtime['pending_events'].append(event['id'])
        self.runtime['last_observed_utc'] = when
        return event

    def _clock_guard(self):
        """A retained regression blocks authority until a verified re-observation."""
        monotonic_clock = getattr(self, 'lifecycle_monotonic', time.monotonic)
        before = monotonic_clock()
        now = self._lifecycle_now()
        after = monotonic_clock()
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
        anchor = getattr(self, '_clock_anchor', None)
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
        if getattr(self, '_clock_failure', None):
            return self._clock_failure
        self._clock_anchor = (now, after, wall_radius, mono_radius)
        return {'usable': True, 'observed_utc': now.isoformat()}

    def _require_action_clock(self):
        guard = self._clock_guard()
        if not guard['usable']:
            raise ValueError('clock prevents new authority: ' + guard['reason'])
        return guard['observed_utc']

    def _capability_requirements(self, reference, required=()):
        return capability_requirements(self.instance, reference, required, at=self._lifecycle_now().isoformat())

    def _pause_lifecycle(self, reason):
        if self.runtime.get('status') in {'closed', 'completed'} or self.instance['lifecycle'].get('permanently_closed'):
            raise ValueError('closed/completed instance cannot pause or reopen')
        lifecycle = self.instance['lifecycle']
        if lifecycle['state'] != 'paused':
            self.runtime['resume_lifecycle'] = lifecycle['state']
            lifecycle['state'] = 'paused'
        self.runtime['status'] = 'paused'
        self.runtime['stop_requested'] = reason
        lifecycle.setdefault('history', []).append({'kind': 'pause', 'id': new_id('PA'), 'reason': reason})
        for execution in self.runtime['executions'].values():
            if execution.get('status') not in {'ended', 'finished'}:
                execution['stop_requested'] = reason

    def _conversation_live(self):
        if self.instance.get('conversation_loss_policy') != 'pause':
            return True
        now = self._lifecycle_now()
        lost = self.runtime.get('lost_conversation_generations', {})
        return any(row.get('status') == 'connected' and timestamp(row['lease_expires_at']) > now
                   and row['generation'] > lost.get(row['id'], 0)
                   for row in self.runtime.get('conversations', {}).values())

    def _resume_lifecycle(self, request):
        if self.runtime.get('status') in {'closed', 'completed'} or self.instance['lifecycle'].get('permanently_closed'):
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
        if self.runtime.get('status') in {'closed', 'completed'} or self.instance['lifecycle'].get('permanently_closed'):
            raise ValueError('closed/completed instance cannot activate')
        lifecycle = self.instance['lifecycle']
        if lifecycle['state'] != 'initializing':
            return {'activated': lifecycle['state'] == 'active', 'missing': []}
        self._require_action_clock()
        self.runtime['recovery_checked'] = not any(
            e.get('status') != 'ended' for e in self.runtime.get('executions', {}).values()) and not any(
            r.get('state') == 'held' for r in self.runtime.get('reservations', {}).values())
        requirements = activation_requirements(self.instance, self.runtime, at=self._lifecycle_now().isoformat(),
            owner_handlers=getattr(self, '_governance_owner_handlers', lambda: None)())
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

    def _initialization_control(self, change, source_ref):
        """Existing decision control adopts settings or refreshes observed CLI evidence."""
        from .initialization import digest, governance_basis, grant_current, INITIAL_ROLES, adapter_for
        from .execution_profiles import resolve_profile, capability_evidence
        from .review_policy import build_review_policy
        lifecycle = self.instance['lifecycle']
        operation = change.get('operation', 'adopt')
        if lifecycle['state'] == 'active' and operation != 'probe':
            raise ValueError('initialization adoption cannot replace an active contract')
        if operation == 'governance':
            from .governance import initialize_governance, preserve_source
            records = change.get('records')
            if not isinstance(records, list) or not records:
                raise ValueError('exact user-approved governance records required')
            initial_source = preserve_source(new_id('GS'), lifecycle['immutable_input']['text'], origin='user')
            approval_source = self.instance['governance_sources'][source_ref]
            approval = {'id': new_id('DC'), 'kind': 'initial_governance', 'actor': 'user',
                'source_ref': source_ref, 'source_sha256': approval_source['sha256'],
                'input_source_ref': initial_source['id'], 'input_source_sha256': initial_source['sha256'],
                'record_hashes': {r['id']: digest(r) for r in records}}
            self.instance = initialize_governance(self.instance, initial_source, approval, records,
                                                  approval_source=approval_source)
            self.instance['lifecycle']['adoption']['governance_sha256'] = governance_basis(self.instance)
            self.instance['lifecycle']['adoption'].setdefault('source_refs', []).append(source_ref)
            return
        if operation == 'probe':
            if 'profile_ref' in change and 'profile_refs' in change:
                raise ValueError('supply profile_ref or profile_refs, not both')
            refs = change.get('profile_refs', [change.get('profile_ref')])
            if not isinstance(refs, list) or not refs:
                raise ValueError('capability probe requires exact profile references')
            profiles = [resolve_profile(self.instance['execution_profiles'], ref) for ref in refs]
            if len({profile['id'] for profile in profiles}) != len(profiles):
                raise ValueError('capability probe profile references must be distinct')
            if any(profile['actor_kind'] != 'ai' for profile in profiles):
                raise ValueError('CLI capability probe requires AI profiles')
            observations, rows = {}, []
            for profile in profiles:
                adapter = adapter_for(profile)
                key = (profile['ai']['provider'], adapter.observation_key())
                if key not in observations:
                    observations[key] = adapter.describe()
                rows.append(capability_evidence(profile, observations[key], observed_at=self._lifecycle_now().isoformat()))
            # A failed observation leaves the previous evidence intact. These
            # remain individual observed facts, never an aggregate permission.
            self.instance.setdefault('capability_evidence', {}).update({row['id']: row for row in rows})
            return
        if operation != 'adopt':
            raise ValueError('initialization operation must be governance, adopt or probe')
        adoption = deepcopy(lifecycle.get('adoption', {}))
        if change.get('adopt_current_config') is True:
            adoption['config_sha256'] = digest(self.instance['config'])
        if change.get('adopt_current_governance') is True:
            adoption['governance_sha256'] = governance_basis(self.instance)
        if 'conversation_loss_policy' in change:
            if change['conversation_loss_policy'] not in {'pause', 'continue_authorized'}:
                raise ValueError('explicit conversation loss policy required')
            self.instance['conversation_loss_policy'] = change['conversation_loss_policy']
        if 'external_policy' in change:
            if change['external_policy'] not in {'disabled', 'explicit_grants'}:
                raise ValueError('external policy must be disabled or explicit_grants')
            adoption['external_policy'] = change['external_policy']
        if 'review_policy' in change or change.get('adopt_default_review_policy'):
            policy = build_review_policy(change.get('review_policy'),
                reviewer_count=self.instance['config'].get('reviewers'),
                max_rounds=self.instance['config'].get('review_rounds'))
            self.instance['review_policy'] = policy
            adoption['review_policy_sha256'] = digest(policy)
        if 'profile_refs' in change:
            refs = change['profile_refs']
            if not isinstance(refs, list) or not refs:
                raise ValueError('adoption requires exact profile references')
            from .observations import observation_settings_errors
            for ref in refs:
                errors = observation_settings_errors(resolve_profile(self.instance['execution_profiles'], ref))
                if errors:
                    raise ValueError('observation_configuration: ' + json.dumps(errors, ensure_ascii=False))
            adoption['profile_refs'] = deepcopy(refs)
        if 'initial_profile_ref' in change:
            profile = resolve_profile(self.instance['execution_profiles'], change['initial_profile_ref'])
            if profile['role'] != 'intent_interpretation':
                raise ValueError('initial profile must permit intent_interpretation')
            from .model_policy import selection
            selection(self.instance['config'], {'role': 'intent_interpretation',
                'profile_ref': change['initial_profile_ref']}, {}, self.instance['knowledge'],
                profiles=self.instance['execution_profiles'])
            adoption['initial_profile_ref'] = deepcopy(change['initial_profile_ref'])
        elif adoption.get('config_sha256') == digest(self.instance['config']) and adoption.get('profile_refs'):
            from .model_policy import selection
            chosen = selection(self.instance['config'], {'role': 'intent_interpretation'}, {},
                               self.instance['knowledge'], profiles=self.instance['execution_profiles'])['profile_ref']
            if chosen in adoption['profile_refs']:
                adoption['initial_profile_ref'] = chosen
        for field, initial in [('initial_grant_ids', True), ('research_grant_ids', False)]:
            if field in change:
                if not isinstance(change[field], list) or not change[field]:
                    raise ValueError(field + ' must be nonempty')
                for gid in change[field]:
                    if not grant_current(self.instance, gid, self._lifecycle_now(), initial=initial):
                        raise ValueError('grant is absent, stale or outside initialization scope: ' + gid)
                adoption[field] = list(change[field])
        if set(adoption.get('initial_grant_ids', [])) & set(adoption.get('research_grant_ids', [])):
            raise ValueError('initial and research authority must use distinct grants')
        adoption.setdefault('source_refs', [])
        if source_ref not in adoption['source_refs']:
            adoption['source_refs'].append(source_ref)
        lifecycle['adoption'] = adoption
        decision_id = new_id('DC')
        self.instance['decisions'][decision_id] = {'id': decision_id, 'kind': 'initialization',
            'source_ref': source_ref, 'actor': 'user', 'change': deepcopy(change), 'affected': [],
            'created_at': self._lifecycle_now().isoformat()}
        self._queue_initial_intent()

    def _queue_initial_intent(self):
        lifecycle = self.instance['lifecycle']
        if lifecycle.get('intent_check'):
            return
        adoption = lifecycle.get('adoption', {})
        ref = adoption.get('initial_profile_ref')
        if not ref or not self._capability_requirements(ref)['satisfied']:
            return
        from .initialization import grant_current
        if not any(grant_current(self.instance, gid, self._lifecycle_now(), initial=True)
                   and 'intent_interpretation' in self.instance['grants'][gid]['roles']
                   for gid in adoption.get('initial_grant_ids', [])):
            return
        input_id = lifecycle.setdefault('input_id', new_id('UI'))
        if any(row.get('input_ref') == input_id and not row.get('superseded_by')
               and row.get('application', {}).get('status') == 'awaiting_decision'
               for row in self.runtime.get('intent_imports', {}).values()):
            return
        if not any(row['id'] == input_id for row in self.runtime.setdefault('inputs', [])):
            self.runtime['inputs'].append({'id': input_id, 'text': lifecycle['immutable_input']['text'],
                'sha256': lifecycle['immutable_input']['sha256'], 'config': {}})
        pending = [*self.runtime['queue'],
                   *(row.get('action', {}) for row in self.runtime.get('waiting_actions', {}).values())]
        if not any(a.get('role') == 'intent_interpretation' and a.get('target') == input_id for a in pending):
            self._enqueue('intent_interpretation', input_id, stage='interpret', initialization=True,
                          profile_ref=ref, reason='Interpret preserved initialization input independently')

    def _complete_initial_intent(self, input_id):
        """Called after ENGINE applies the independently checked import units."""
        lifecycle = self.instance['lifecycle']
        if input_id != lifecycle.get('input_id'):
            return False
        from .initialization import initial_intent_evidence
        lifecycle['intent_check'] = initial_intent_evidence(self.instance, self.runtime,
            owner_handlers=getattr(self, '_governance_owner_handlers', lambda: None)())
        return True

    def _action_lifecycle_gate(self, action):
        if self.runtime.get('status') in {'closed', 'completed'} or self.instance['lifecycle'].get('permanently_closed'):
            raise ValueError('closed/completed instance cannot dispatch')
        self._require_action_clock()
        profile = self._execution_profile(action)
        from .execution_profiles import profile_ref
        action.update(profile_ref=profile_ref(profile), actor_kind=profile['actor_kind'], budget_kind=profile['budget_kind'])
        lifecycle = self.instance['lifecycle']['state']
        if lifecycle == 'paused' and self._limited_recovery_allowed(action):
            return
        if lifecycle == 'paused' or not self._conversation_live():
            raise ValueError('lifecycle or conversation prevents dispatch')
        if lifecycle == 'initializing':
            from .initialization import grant_current
            adoption = self.instance['lifecycle'].get('adoption', {})
            if action['role'] in {'trust_check', 'trust_activate'}:
                transition = self.runtime['trust_transitions'].get(action.get('transition_id'), {})
                if not transition.get('source_ref'):
                    raise ValueError('trust preparation requires explicit transition authority')
                return
            if action['role'] not in {'intent_interpretation', 'maintenance'}:
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

    @staticmethod
    def _recovery_action_basis(action):
        transient = {'repair', 'dispatch_wait', 'model_selection', 'owner_activity_id', 'activity_id',
                     'execution_id', 'continuation_of', 'actor_kind', 'budget_kind'}
        return _digest({k: v for k, v in action.items() if k not in transient})

    def _recovery_pause_basis(self):
        return _digest({key:self.runtime.get(key) for key in
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
        from .execution_profiles import resolve_profile
        profile = resolve_profile(self.instance['execution_profiles'], change['profile_ref'])
        if profile['role'] != action['role'] or profile['budget_kind'] != 'operations':
            raise ValueError('limited recovery requires the exact role and operations profile')
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
                                   'approval_sha256': _digest(change)})
        # Validate against the just-preserved request before the common control
        # handler publishes it in extended_controls. No second authority ledger.
        self._check_limited_recovery(action, change=change)

    def _check_limited_recovery(self, action, *, change=None):
        from .execution_profiles import resolve_profile
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
        expected = {**binding, 'approval_sha256': _digest(change)}
        if len(approvals) != 1 or approvals[0].get('basis') != expected or approvals[0].get('target') != action.get('id'):
            raise ValueError('limited recovery lacks its immutable approval binding')
        if (change.get('kind') != 'limited_recovery' or change.get('action_id') != action.get('id')
                or change.get('grant_id') != action.get('grant_id') or change.get('purpose') != action.get('purpose')
                or change.get('profile_ref') != action.get('profile_ref')
                or change.get('procedure') != binding.get('procedure')
                or change.get('expires_at') != binding.get('expires_at')
                or timestamp(change['expires_at']) <= self._lifecycle_now()):
            raise ValueError('limited recovery no longer matches its approval')
        profile = resolve_profile(self.instance['execution_profiles'], action['profile_ref'])
        if (profile['role'] != action['role'] or profile['budget_kind'] != 'operations'
                or action['role'] not in {'maintenance', 'trust_check', 'trust_activate'}):
            raise ValueError('limited recovery profile or role is outside scope')
        request = {**action, 'actor_kind': profile['actor_kind'], 'budget_kind': profile['budget_kind']}
        authority = authorize(self.instance, request, self._lifecycle_now().isoformat(), runtime=self.runtime)
        if not authority['allowed']:
            raise ValueError('limited recovery authority: ' + authority['reason'])
        if not self._capability_requirements(action['profile_ref'])['satisfied']:
            raise ValueError('limited recovery capability evidence is unavailable')

    def _limited_recovery_allowed(self, action):
        try:
            self._check_limited_recovery(action)
            return True
        except (ValueError, KeyError, TypeError, IndexError):
            return False

    def _execution_stop_requested(self, action, execution=None):
        """Central runners use this instead of a blanket paused-state veto."""
        if not self._clock_guard()['usable']:
            return True
        if (self.runtime.get('status') in {'closed', 'completed'}
                or self.instance['lifecycle'].get('permanently_closed')
                or (execution or {}).get('stop_requested')):
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
        if self.runtime.get('status') in {'closed', 'completed'} or self.instance.get('lifecycle', {}).get('permanently_closed'):
            raise ValueError('closed/completed instance cannot apply lifecycle controls')
        self._verify_current_head()
        source_ref = request.get('id')
        if not isinstance(source_ref, str) or not source_ref:
            raise ValueError('extended control requires its preserved user request ID')
        if action == 'close':
            lifecycle = self.instance['lifecycle']
            lifecycle['permanently_closed'] = True
            lifecycle.setdefault('history', []).append({'kind':'closed', 'source_ref':source_ref})
            self.runtime.update(status='closed', stop_requested='closed', queue=[])
            self.runtime.pop('resume_lifecycle', None)
            for execution in self.runtime['executions'].values():
                if execution.get('status') != 'ended': execution['stop_requested'] = 'closed'
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
        digest = _digest(request)
        old = self.runtime['extended_controls'].get(source_ref)
        if old:
            if _digest(old['request']) != digest:
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
            # Owner decision APIs return candidate requests. Give each its
            # durable identity at this application boundary, before storage.
            for queued in self.runtime['queue']:
                queued.setdefault('id', new_id('AC'))
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
            if callable(getattr(getattr(self, 'store', None), 'load', None)):
                from .preflight import preserve_rejected_candidate
                rejection = preserve_rejected_candidate(self.store, self.head, raw=canonical_json(request),
                    reason=f'{type(error).__name__}: {error}')
                self.head = rejection['snapshot']
            raise
        return True

    def _invalidate_goal_currentness(self):
        view = governance_working_view(self.instance) if self.instance.get('governance') else self.instance
        judgments = self.instance.get('goal_judgments', [])
        basis = self.instance.get('goal_assessment_basis', judgments[-1].get('basis') if judgments else None)
        current = [j for j in judgments if j.get('basis') == basis] if basis is not None else judgments[-1:]
        for judgment in current:
            invalid_dependencies = [record_id for record_id in judgment.get('dependencies', [])
                if record_id in self.instance.get('knowledge', {}) and not assess_use(self.instance['knowledge'][record_id], self.instance)['valid']]
            if (judgment.get('record_basis') and not validate_basis(judgment['record_basis'], self.instance, self.runtime)['valid']) or (judgment.get('source_basis') and not sources_current(judgment['source_basis'], self.instance)) or (
                    judgment.get('goal_revision', view.get('goal_revision')) != view.get('goal_revision')) or (
                    judgment.get('policy_revision', view.get('policy_revision')) != view.get('policy_revision')) or invalid_dependencies:
                judgment['current'] = False
                judgment['invalidated_reason'] = ('A mathematical dependency is no longer usable: ' + ', '.join(invalid_dependencies)
                                                   if invalid_dependencies else 'The actual judgment basis changed')
        stale = [j for j in current if j.get('current') is False]
        if stale and self.instance.get('goal_status') == 'mathematically_solved':
            self.instance['goal_status'] = 'unsolved'
            if self.runtime.get('status') == 'completed': self.runtime['status'] = 'ready'
            self._lifecycle_event('goal_basis_invalidated', judgment_ids=[j.get('id', j.get('execution_id')) for j in stale])
            self._enqueue('research_plan', reason='Previously used goal evidence is no longer current')

    def _knowledge_control(self, config, source_ref):
        operation, knowledge_id = config.get('operation'), config.get('id')
        if operation not in {'revise', 'invalidate'}:
            raise ValueError('knowledge operation must be revise or invalidate')
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
                config.get('changes', {}), reason=reason, actor_ref=source_ref,
                declared_impact=config.get('declared_impact'), independent_confirmation=config.get('independent_confirmation'))
            self.runtime['queue'][:] = [a for a in self.runtime['queue'] if not (a.get('target') == knowledge_id and
                (a.get('role') in {'identity_review', 'formal_check'} or (a.get('role') == 'supplemental_research' and a.get('review_cycle_id'))))]
        elif operation == 'invalidate':
            self.instance, self.runtime = invalidate_knowledge(self.instance, self.runtime, knowledge_id,
                reason=reason, actor_ref=source_ref, declared_impact=config.get('declared_impact'),
                independent_confirmation=config.get('independent_confirmation'))
            self.runtime['queue'][:] = [a for a in self.runtime['queue'] if not (a.get('target') == knowledge_id and
                (a.get('role') in {'identity_review', 'formal_check'} or (a.get('role') == 'supplemental_research' and a.get('review_cycle_id'))))]
        else:
            raise ValueError('knowledge operation must be revise or invalidate')
        self._lifecycle_event('knowledge_' + operation, target=knowledge_id, source_ref=source_ref, reason=reason)
        self._enqueue('research_plan', reason=reason, knowledge_id=knowledge_id, source_ref=source_ref)

    def _trust_control(self, config, source_ref):
        operation = config.get('operation')
        if operation == 'recheck':
            if config.get('env_id') not in self.instance['trust_environments']:
                raise ValueError('environment recheck needs an existing environment')
            checks = getattr(self, '_environment_checks', None)
            if checks is not None:
                checks.entries = {k:v for k,v in checks.entries.items()
                                  if v['result'] is None or v.get('environment_id') != config['env_id']}
            for aid, waiting in list(self.runtime.get('waiting_actions', {}).items()):
                if (waiting.get('kind') == 'formal_environment'
                        and waiting.get('detail', {}).get('environment_id') == config['env_id']):
                    if not any(a.get('id') == aid for a in self.runtime['queue']):
                        self.runtime['queue'].append({**deepcopy(waiting['action']),
                            'continuation_of':waiting['execution_id']})
                    del self.runtime['waiting_actions'][aid]
            self._lifecycle_event('trust_recheck_requested', target=config['env_id'], source_ref=source_ref)
            return
        if operation == 'register':
            self.instance, environment_id = register_environment(self.instance, config.get('toolchain', {}),
                                                                 config.get('allowed_axioms', list(AXIOMS)))
            environment = self.instance['trust_environments'][environment_id]
            environment.update(source_ref=source_ref, manifest=deepcopy(config.get('manifest', {})),
                               manifest_sha256=_digest(config.get('manifest', {})))
            from .initialization import trust_environment_errors
            errors = trust_environment_errors(environment, verify_files=False)
            if errors:
                raise ValueError('; '.join(errors))
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
            from .initialization import trust_environment_errors
            errors = trust_environment_errors(environment, verify_files=False)
            if errors:
                raise ValueError('; '.join(errors))
            transition.update(source_ref=source_ref, created_at=self._lifecycle_now().isoformat())
            transition.setdefault('history', []).append({'kind': 'environment_fixed',
                'environment_id': environment_id, 'environment_sha256': _digest(environment),
                'source_ref': source_ref, 'at': transition['created_at']})
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
            if self.instance['lifecycle'].get('adoption', {}).get('external_policy') != 'explicit_grants':
                raise ValueError('external effects are disabled by the adopted policy')
            grant = self.instance.get('grants', {}).get(config.get('grant_id'))
            if not grant or grant.get('kind') != 'http': raise ValueError('HTTP operation requires an explicit HTTP grant')
            stable_source_ref = config.get('source_ref') or ('external:' + str(config['id']) if config.get('id') else source_ref)
            profile = self._execution_profile({'role': 'external_action'})
            scope = {key: config[key] for key in ('target_id', 'purpose', 'subject') if key in config}
            for key in ('budget_kind', 'actor_kind'):
                if key in config and config[key] != profile[key]:
                    raise ValueError('external request scope differs from the actual execution profile: ' + key)
                scope[key] = profile[key]
            entry = prepare_operation(config.get('request'), config['grant_id'], stable_source_ref, config.get('id'), **scope)
            binding = getattr(self, '_external_preparation_binding', None)
            if binding is not None:
                entry['academic_binding'] = deepcopy(binding)
            if grant.get('academic_only') or grant.get('requires_academic') or binding is not None:
                from .academic import bind_external_prerequisite
                basis = self._solution_basis() if hasattr(self, '_solution_basis') else None
                entry = bind_external_prerequisite(self.instance, self.runtime, basis, entry,
                    resolve_evidence=getattr(self, '_academic_evidence', None))
            self._validate_external(entry, grant)
            existing = self.runtime['external_operations'].get(entry['id'])
            immutable = ('id', 'request_sha256', 'grant_id', 'source_ref', 'target_id', 'purpose', 'subject',
                         'budget_kind', 'actor_kind', 'academic_basis', 'academic_binding')
            if existing:
                if any(existing.get(key) != entry.get(key) for key in immutable): raise ValueError('external operation ID already identifies another ledger')
                if existing.get('status') == 'prepared': self._enqueue('external_action', entry['id'], grant_id=entry['grant_id'], source_ref=source_ref)
                return
            self.runtime['external_operations'][entry['id']] = entry
            self._enqueue('external_action', entry['id'], grant_id=entry['grant_id'], source_ref=source_ref)
            self._lifecycle_event('external_operation_prepared', target=entry['id'], source_ref=source_ref)
        elif operation == 'reconcile':
            entry = self.runtime['external_operations'].get(config.get('id'))
            if entry is None: raise ValueError('external operation does not exist')
            evidence = config.get('evidence')
            if not isinstance(evidence, dict):
                raise ValueError('reconciliation requires structured operation evidence')
            entry = reconcile_operation(entry, evidence, config.get('result'), source='user',
                succeeded=True if evidence.get('fact') == 'succeeded' else None,
                effect_absent=True if evidence.get('fact') == 'effect_absent' else None,
                idempotency_evidence=evidence.get('idempotency_evidence'))
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
            if entry.get('status') not in {'unknown', 'failed', 'cancelled'}:
                raise ValueError('completed operation cannot be retried')
            if not isinstance(grant_id, str) or not grant_id or grant_id != entry.get('grant_id'):
                raise ValueError('retry requires the operation\'s explicit current grant')
            grant = self.instance.get('grants', {}).get(grant_id)
            if not grant or grant.get('kind') != 'http':
                raise ValueError('retry requires an active HTTP grant')
            transmitted = entry.get('transmitted')
            retry = config.get('evidence')
            if not retry and entry.get('status') == 'failed' and entry.get('effect_absent') is True:
                proof = entry.get('reconciliation', {}).get('evidence', {})
                if proof.get('evidence_ref'):
                    retry = {'kind': 'effect_absent', 'request_sha256': entry['request_sha256'],
                             'idempotency_key': entry['idempotency_key'], 'evidence_ref': proof['evidence_ref']}
            if entry['status'] == 'cancelled' and transmitted is False and not entry.get('attempts'):
                trial = {**entry, 'status': 'prepared', 'transmission_phase': 'not_started'}
            else:
                if not isinstance(retry, dict): raise ValueError('retry requires request-bound effect or idempotency evidence')
                trial = prepare_retry(entry, retry, source='user', now_iso=self._lifecycle_now().isoformat())
            self._validate_external(trial, grant)
            previous = {key: deepcopy(value) for key, value in entry.items()
                        if key not in {'history', 'attempts'}}
            history = [*deepcopy(entry.get('history', [])), {'action': 'retry_prepared', 'source_ref': source_ref,
                       'previous': previous, 'previous_status': entry['status'],
                       'previous_execution_id': entry.get('execution_id'), 'at': self._lifecycle_now().isoformat()}]
            attempts = deepcopy(entry.get('attempts', []))
            if attempts and 'outcome' not in attempts[-1]:
                attempts[-1].update(outcome=entry['status'], transmitted=transmitted)
            elif transmitted is True:
                attempts.append({'request_sha256': entry['request_sha256'], 'outcome': entry['status'],
                                 'transmitted': transmitted})
            entry = deepcopy(trial)
            entry.pop('execution_id', None)
            entry.update(status='prepared', history=history, attempts=attempts,
                         retry_authorized=True, retried_from=source_ref, transmitted=False, transmission_phase='not_started',
                         continuation_of=previous.get('execution_id'))
            for key in ('http_status', 'body_base64', 'body_sha256', 'error', 'credential_env', 'reconciliation', 'succeeded', 'effect_absent'):
                entry.pop(key, None)
            self.runtime['external_operations'][entry['id']] = entry
            self._enqueue('external_action', entry['id'], grant_id=grant_id, source_ref=source_ref)
            self._lifecycle_event('external_operation_retry_prepared', target=entry['id'], source_ref=source_ref,
                                  previous_status=previous['status'])
        else:
            raise ValueError('external operation must be prepare, reconcile, or retry')

    def _external_prerequisite(self, operation, grant):
        from .academic import external_prerequisite
        basis = self._solution_basis() if hasattr(self, '_solution_basis') else None
        return external_prerequisite(self.instance, self.runtime, basis, operation, grant,
                                     resolve_evidence=getattr(self, '_academic_evidence', None))

    def _validate_external(self, operation, grant):
        validate_operation(operation, grant, self._lifecycle_now().isoformat(), runtime=self.runtime,
                           academic_check=self._external_prerequisite)

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

    def _record_readiness(self, task_id, evaluation, when):
        previous = self._task_readiness.get(task_id, {})
        if {k: v for k, v in previous.items() if k != 'evaluated_at'} != evaluation:
            self._task_readiness[task_id] = {**evaluation, 'evaluated_at': when}

    def _refresh_readiness(self):
        self._verify_current_head()
        guard = self._clock_guard()
        if not guard['usable']:
            self.runtime['clock_guard'] = {'state': 'blocked', **guard}
            self.runtime['availability'] = {'state': 'blocked', 'reason': 'clock_regression'}
            if self.runtime.get('status') not in {'closed', 'completed'}:
                self._pause_lifecycle('clock_regression')
            return
        if self.instance['lifecycle']['state'] == 'paused':
            return
        if self.runtime.get('status') in {'closed', 'completed'} or self.instance['lifecycle'].get('permanently_closed'):
            return
        if self.instance['lifecycle']['state'] == 'initializing':
            self._queue_initial_intent()
            self._activate_initialization()
            if self.instance['lifecycle']['state'] == 'initializing':
                return
        self._retire_closed_revision_targets()
        self._retire_sealed_goal_audit_requests()
        self._reconcile_revision_delegations()
        live_actions = {execution.get('action', {}).get('id') for execution in self.runtime['executions'].values()
                        if execution.get('status') != 'ended'}
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
            if self.runtime['tasks'][tid].get('status') not in {'completed', 'closed'}
            and self.runtime['tasks'][tid].get('results')]
        if reassess:
            self._enqueue('research_plan', reason='Assessment evidence changed; reassess existing results: '
                          + ', '.join(sorted(reassess)))
        from .repository import exact_content_hash
        for task_id, task in self.runtime['tasks'].items():
            assessment = task.get('assessment', {})
            if task.get('status') not in {'completed', 'closed'} or assessment.get('current') is not False:
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
        query_instance = governance_working_view(self.instance)
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
                work_profile_selection(self.instance['config'], task, self.instance['execution_profiles'])
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
            required = {'revision': task['revision'], 'contract_sha256': contract_hash(task),
                        'goal_revision': query_instance['goal_revision'], 'policy_revision': query_instance['policy_revision']}
            # One premise snapshot serves the review key and every recorded review of this task.
            task_basis = capture_task_basis(task, query_instance, self.runtime)
            review_key = review_basis_key(task, query_instance, self.runtime, task_basis=task_basis)
            for review in task.get('reviews', []):
                currentness = contract_review_current(review, task, query_instance, self.runtime, task_basis=task_basis)
                review['inputs_current'] = currentness['valid']
                if currentness['changes']:
                    review['currentness_changes'] = currentness['changes']
                else:
                    review.pop('currentness_changes', None)
            approved = any(review.get('decision') == 'approved'  and review.get('inputs_current', True) and all(review.get(key) == value for key, value in required.items())
                           for review in task.get('reviews', []))
            reviewed = any(review.get('inputs_current', True) and all(review.get(key) == value for key, value in required.items()) for review in task.get('reviews', []))
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
            if not approved and not reviewed and not blocked_review and not live_review:
                candidates = [a for a in self.runtime['queue'] if a.get('role') == 'task_contract_review' and a.get('target') == task_id]
                same = next((a for a in candidates if a.get('contract_basis') == required and a.get('review_basis_key') == review_key), None)
                if same is None:
                    self.runtime['queue'][:] = [a for a in self.runtime['queue'] if a not in candidates]
                    self._enqueue('task_contract_review', task_id, contract_basis=required, review_basis_key=review_key,
                                  reason='Current contract and policy require independent approval')
            evaluation = deepcopy(task_ready(task, query_instance, self.runtime,
                                    action={'role': 'research_work', 'target': task_id, 'budget_kind': 'work', 'actor_kind': 'ai'},
                                    evaluation_context=evaluation_context))
            if not approved:
                evaluation = {'state': 'not_ready', 'basis': [], 'errors': ['current revision lacks approved contract review']}
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
        old_pending_inputs = {event.get('target') for event in self.runtime['events']
                              if event['id'] in self.runtime['pending_events'] and event['kind'] == 'task_new_input'}
        scheduled = apply_event_schedule(self.instance, self.runtime, now.isoformat(),
                                         evaluation_context=evaluation_context)
        duplicate_ids = {event['id'] for event in scheduled['events']
                         if event['kind'] == 'task_new_input' and event.get('target') in old_pending_inputs}
        if duplicate_ids:
            scheduled['runtime']['events'] = [event for event in scheduled['runtime']['events'] if event['id'] not in duplicate_ids]
            scheduled['runtime']['pending_events'] = [event_id for event_id in scheduled['runtime']['pending_events'] if event_id not in duplicate_ids]
        self.instance, self.runtime = scheduled['instance'], scheduled['runtime']
        if self.runtime.get('status') in {'paused', 'closed', 'completed'}:
            return
        self._schedule_reconsideration(now.isoformat())
        events = {event['id']: event for event in self.runtime['events']}
        requests = self.runtime['queue'] + [e.get('action', {}) for e in self.runtime['executions'].values()
                                           if e.get('status') != 'ended']
        requests += [w['action'] for w in self.runtime.get('waiting_actions', {}).values() if 'action' in w]
        assigned_refs = {ref for a in requests for ref in a.get('event_refs', [])}
        pending = [event_id for event_id in dict.fromkeys(self.runtime['pending_events'])
                   if event_id not in assigned_refs]
        if not pending: return
        running_ids = {execution.get('action', {}).get('id') for execution in self.runtime['executions'].values()
                       if execution.get('status') != 'ended'}
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
                self._enqueue(role, id=new_id('AC'), reason='Preserved research events require reconsideration',
                              opened_at=now.isoformat(), event_refs=selected)
                queued = self.runtime['queue'][-1]
            else:
                queued.setdefault('id', new_id('AC'))
                queued.setdefault('opened_at', now.isoformat())
                queued['event_refs'] = list(dict.fromkeys([*queued.get('event_refs', []), *selected]))
            if opened and role == 'research_preparation':
                self.runtime['next_research_reconsider_at'] = (timestamp(queued['opened_at']) + _reconsider_interval(self.instance['config'])).isoformat()
            assigned = True
        # Assignment is not consumption. The owning engine consumes only the
        # exact event_refs in an accepted execution's immutable input.
        if assigned and self.runtime.get('status') == 'waiting': self.runtime['status'] = 'ready'

    def _bind_formal_environment(self, result):
        output = deepcopy(result)
        toolchain = output.get('toolchain')
        allowed = output.get('allowed_axioms', self.instance.get('config', {}).get('allowed_axioms', list(AXIOMS)))
        output['allowed_axioms'] = deepcopy(allowed)
        if not isinstance(toolchain, dict) or not toolchain.get('sha256') or not toolchain.get('version'):
            output.update(trust_environment_id=None, trust_environment_status='unknown',
                          trust_environment_reason='Actual compiler fingerprint and version require a real probe')
            return output
        environment = self._formal_environment()
        if not _toolchain_matches(environment['toolchain'], toolchain) or set(environment['allowed_axioms']) != set(allowed):
            raise ValueError('formal result differs from the previously approved environment')
        output.update(trust_environment_id=environment['id'], trust_environment_status='active')
        return output

    def _observe_environment(self, environment):
        from .environment_checks import EnvironmentChecks
        from .trust_validation import verify_environment_files
        operation = getattr(self, '_environment_operation', None)
        if operation is None:
            return verify_environment_files(environment)
        if not hasattr(self, '_environment_checks'):
            self._environment_checks = EnvironmentChecks(self)
        return self._environment_checks.observe(environment, operation)

    def _formal_environment(self, *, verify_files=True):
        """Required before checking and again before admitting a formal result."""
        self._require_action_clock()
        from .initialization import require_trust_environment
        return require_trust_environment(self.instance, self.runtime, observe=self._observe_environment, verify_files=verify_files)

    def _end_machine_execution(self, execution, *, outcome, disposition):
        from .execution_lifecycle import transition_execution
        at = self._lifecycle_now().isoformat()
        if execution['status'] == 'ended':
            return True
        if execution.get('launch_ticket') and execution['launch_ticket']['phase'] != 'not_started':
            execution['launch_ticket']['phase'] = 'finished'
        if execution.get('capacity') and not self._release_call_slot(execution['id']):
            transition_execution(execution, 'stopping', at=at, stop_phase='terminating',
                                 reason='local machine Job termination remains unconfirmed')
            execution['error'] = 'Machine capacity and result remain held until local Job termination is confirmed.'
            return False
        if execution['status'] in {'starting', 'running'}:
            transition_execution(execution, 'stopping', at=at, stop_phase='terminating',
                                 reason='local machine call returned')
        transition_execution(execution, 'ended', at=at, outcome=outcome, disposition=disposition)
        return True

    def _external_execution_record(self, operation):
        execution_id = operation.setdefault('execution_id', new_id('EX'))
        record = self.runtime['executions'].get(execution_id)
        if record is None:
            action = next((a for a in self.runtime['queue'] if a.get('role') == 'external_action'
                           and a.get('target') == operation['id']), None)
            if action is None:
                action = {'role': 'external_action', 'target': operation['id'],
                          'grant_id': operation['grant_id'], 'source_ref': operation['source_ref']}
            if operation.get('continuation_of'):
                action['continuation_of'] = operation['continuation_of']
            record = self._register_execution(action, {'id': execution_id, 'role': 'external_action',
                'grant_id': operation['grant_id'], 'status': 'running', 'created_at': self._lifecycle_now().isoformat()})
        if record['status'] != 'ended':
            record.update(operation_id=operation['id'], request_sha256=operation['request_sha256'],
                          source_ref=operation['source_ref'], effect_status=operation['status'],
                          http_status=operation.get('http_status'), succeeded=operation.get('succeeded'))
        self.runtime['external_operations'][operation['id']] = deepcopy(operation)
        terminal = operation['status'] != 'prepared' or operation.get('waiting_reason')
        if terminal:
            accepted = operation['status'] == 'confirmed' and operation.get('succeeded') is True
            if accepted and record['status'] != 'ended':
                record['submission_receipt'] = {'kind': 'machine_output', 'state': 'accepted',
                    'execution_id': execution_id, 'evidence_ref': operation['id'],
                    'source_sha256': operation['request_sha256'], 'accepted_at': self._lifecycle_now().isoformat()}
            self._end_machine_execution(record, outcome='cancelled' if operation['status'] == 'cancelled'
                                        else 'output_accepted' if accepted else 'execution_incomplete',
                                        disposition={'external_operation': operation['id'],
                                                     'effect_status': operation['status']})
            if self.runtime.get('active_execution') == execution_id:
                self.runtime['active_execution'] = None
            activity_id = record['owner_activity_id']
            activity = self.runtime['activities'][activity_id]
            if operation['status'] == 'confirmed' and operation.get('succeeded') is True and activity['status'] != 'finished':
                from .activities import finish_activity
                finish_activity(self.runtime, activity_id, result_refs=[operation['id']], unresolved=[], followups=[],
                                at=self._lifecycle_now().isoformat())
            if activity['status'] != 'finished':
                from .activities import wait_for
                reason = 'external_reconciliation' if operation['status'] == 'unknown' else 'external_followup'
                wait_for(self.runtime, activity_id, reason=reason,
                    condition={'operation_id': operation['id'], 'status': operation['status']},
                    next_owner='user', at=self._lifecycle_now().isoformat())
        else:
            self.runtime['active_execution'] = execution_id
        if operation['status'] == 'confirmed' and operation.get('succeeded') is True:
            refs = self.instance.setdefault('available_input_refs', [])
            if operation['id'] not in refs:
                refs.append(operation['id'])

    def _process_machine_action(self, action):
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

    def _run_trust_activation(self, action):
        from .trust_validation import verify_environment_files
        return self._run_machine_steps(self._trust_activation_steps(action), calculator=verify_environment_files)

    def _record_machine_continuation(self, action, execution_id):
        # A save replaces the state objects while this generator is suspended.
        # Persist the continuation on the current queue, not only its old input.
        action['continuation_of'] = execution_id
        for queued in self.runtime['queue']:
            if queued.get('id') == action.get('id'):
                queued['continuation_of'] = execution_id

    def _trust_activation_steps(self, action):
        transition_id = action['transition_id']
        transition = self.runtime['trust_transitions'][transition_id]
        if transition['status'] in {'active', 'failed'}:
            return
        execution_id = new_id('EX')
        execution = self._register_execution(action, {'id': execution_id, 'role': 'trust_activate',
            'status': 'running', 'created_at': self._lifecycle_now().isoformat(),
             'input_snapshot': self.head,
             'input_manifest': [{'kind': 'trust_transition', 'id': transition_id, 'sha256': _digest(transition)}]})
        if execution is None:
            return False
        self.runtime['active_execution'] = execution_id
        self._save()
        environment = deepcopy(self.instance['trust_environments'][transition['to_environment']])
        def stop():
            return (self._execution_stop_requested(action, self.runtime['executions'][execution_id]) or bool(self.runtime.get('maintenance_fence'))
                    or self.instance['trust_environments'].get(transition['to_environment']) != environment)
        from .execution_profiles import resolve_profile
        from . import trust_validation
        scan_profile = resolve_profile(self.instance['execution_profiles'], execution['execution_profile_ref'])['machine']
        if scan_profile['checker_sha256'] != hashlib.sha256(Path(trust_validation.__file__).read_bytes()).hexdigest():
            raise ValueError('environment checker changed before execution')
        verification = yield execution_id, {'environment':environment, 'should_stop':stop, 'workers':scan_profile['workers']}
        self._live_execution_ids.discard(execution_id)
        execution = self.runtime['executions'][execution_id]
        if verification.get('status') == 'cancelled' or stop():
            self._end_machine_execution(execution, outcome='execution_incomplete', disposition={'kind':'environment_interrupted'})
            from .activities import wait_for
            wait_for(self.runtime, execution['owner_activity_id'], reason='environment_interrupted',
                     condition={'transition_id':transition_id}, next_owner='engine', at=self._lifecycle_now().isoformat())
            self._record_machine_continuation(action, execution_id)
            self._save({f'runtime/artifacts/{execution_id}/environment.json':canonical_json(verification)})
            return False
        self._action_lifecycle_gate(action)
        self._finish_trust_transition(transition_id, verification)
        transition = self.runtime['trust_transitions'][transition_id]
        execution = self.runtime['executions'][execution_id]
        artifact = f'runtime/artifacts/{execution_id}/trust-activation.json'
        result = {'transition_id': transition_id, 'status': transition['status'],
                  'trust_environment_id': transition['to_environment'],
                  'reason': next((r['reason'] for r in reversed(transition.get('history', []))
                                  if r.get('kind') == 'activation_failed'), None)}
        accepted = transition['status'] == 'active'
        execution['result_ref'] = artifact
        if accepted:
            execution['submission_receipt'] = {'kind': 'machine_output', 'state': 'accepted',
                'execution_id': execution_id, 'evidence_ref': artifact,
                'source_sha256': _digest(result), 'trust_environment_id': transition['to_environment'],
                'accepted_at': self._lifecycle_now().isoformat()}
        if not self._end_machine_execution(execution, outcome='output_accepted' if accepted else 'execution_incomplete',
                                           disposition={'kind': 'trust_activation', **result, 'artifact_ref': artifact}):
            self._save({artifact: canonical_json(result)})
            return False
        self.runtime['active_execution'] = None
        from .activities import finish_activity
        finish_activity(self.runtime, execution['owner_activity_id'], result_refs=[artifact],
                        unresolved=[] if accepted else [transition_id], followups=[], at=self._lifecycle_now().isoformat())
        self._save({artifact: canonical_json(result)})
        if getattr(self, '_calls', None) is not None:
            self._remove_action(action)
            self._refresh_readiness()
            self._save()

    def _run_external_action(self, action):
        self._action_lifecycle_gate(action)
        operation_id = action['target']
        operation = self.runtime['external_operations'][operation_id]
        if operation['status'] in {'confirmed', 'failed', 'cancelled'}: return
        if not operation.get('execution_id'): operation['execution_id'] = new_id('EX')
        if operation['status'] == 'unknown' or operation.get('transmission_phase') == 'recorded':
            if operation['status'] == 'prepared':
                operation.update(recover_operation(operation), error='Executor resumed without a confirmed remote outcome')
            self._external_execution_record(operation)
            self._lifecycle_event('external_reconciliation_required', target=operation_id)
            return
        previous = self.runtime['executions'].get(operation.get('execution_id'))
        if previous and previous['status'] == 'ended':
            operation['continuation_of'] = previous['id']
            operation['execution_id'] = new_id('EX')
            action['continuation_of'] = previous['id']
            action['owner_activity_id'] = previous['owner_activity_id']
        grant = self.instance.get('grants', {}).get(operation['grant_id'], {})
        try:
            self._validate_external(operation, grant)
        except ValueError as error:
            operation.update(status='cancelled', effect_absent=True, succeeded=False, error=str(error), transmitted=False)
            self._external_execution_record(operation)
            self._lifecycle_event('external_operation_not_authorized', target=operation_id, reason=str(error))
            return
        def persist(update):
            current = self.runtime['external_operations'][operation_id]
            if current['request_sha256'] != update['request_sha256'] or current['execution_id'] != update.get('execution_id'):
                return False
            if update['status'] == 'prepared':
                if should_stop():
                    raise ValueError('external transmission stopped before authorization')
                self._require_action_clock()
                self._validate_external(update, self.instance['grants'].get(update['grant_id'], {}))
            self.runtime['external_operations'][operation_id] = deepcopy(update)
            self._external_execution_record(update)
            self._save()
            return True
        def should_stop():
            self._controls()
            return bool(self.runtime.get('stop_requested') or self.runtime.get('status') in {'paused', 'closed'} or
                        self.runtime['executions'].get(operation['execution_id'], {}).get('stop_requested'))
        try:
            from .execution_profiles import resolve_profile
            fixed_profile = resolve_profile(self.instance['execution_profiles'], action['profile_ref'])
            result = execute_operation(deepcopy(operation), deepcopy(grant), persist=persist,
                timeout_seconds=fixed_profile['window']['call_timeout_seconds'], should_stop=should_stop,
                runtime=self.runtime, academic_check=self._external_prerequisite,
                current_grant=lambda gid: self.instance['grants'].get(gid, {}))
        except Exception as error:
            result = deepcopy(self.runtime['external_operations'][operation_id])
            sent = result.get('transmitted') is True
            result.update(status='unknown' if sent else 'cancelled', succeeded=None if sent else False,
                          effect_absent=None if sent else True, error=f'{type(error).__name__}: {error}')
            persist(result)
        self._lifecycle_event('external_operation_' + result['status'], target=operation_id,
                              source_ref=result['source_ref'], request_sha256=result['request_sha256'])

    def _run_trust_check(self, action):
        from .environment_checks import verify_formal
        return self._run_machine_steps(self._trust_check_steps(action), calculator=verify_formal)

    def _trust_check_steps(self, action):
        self._action_lifecycle_gate(action)
        transition_id, knowledge_id = action['transition_id'], action['target']
        transition = self.runtime['trust_transitions'][transition_id]
        if transition['status'] not in {'checking', 'ready'}: return
        if knowledge_id in transition['results']:
            if transition['status'] == 'ready': self._enqueue('trust_activate', transition_id=transition_id)
            return
        target = next((t for t in transition['targets'] if t['id'] == knowledge_id), None)
        if target is None: raise ValueError('trust check is not an assigned transition target')
        environment = deepcopy(self.instance['trust_environments'][transition['to_environment']])
        from .knowledge_records import proposal_view
        item = proposal_view(self.instance, knowledge_id)
        execution_id = new_id('EX')
        workspace = Path(self.instance['workspace']) / 'trust' / execution_id
        workspace.mkdir(parents=True, exist_ok=True)
        execution = self._register_execution(action, {'id': execution_id, 'role': 'trust_check', 'status': 'running',
            'created_at': self._lifecycle_now().isoformat()})
        if execution is None:
            return False
        self.runtime['active_execution'] = execution_id
        self._save()
        toolchain = environment['toolchain']
        check = validate_basis([target['basis']], self.instance, self.runtime)
        stop_requested = False
        raw_result = None
        def should_stop():
            nonlocal stop_requested
            if getattr(self, '_calls', None) is not None and self._calls.stopping:
                stop_requested = True
                return True
            self._controls()
            if self._check_conversations(): self._save()
            stop_requested = stop_requested or bool(
                self._execution_stop_requested(action, self.runtime['executions'][execution_id]) or
                self.instance['trust_environments'].get(transition['to_environment']) != environment or
                not validate_basis([target['basis']], self.instance, self.runtime)['valid'])
            from .governance import authorize
            stop_requested = stop_requested or not authorize(self.instance, action, runtime=self.runtime)['allowed']
            return stop_requested
        try:
            from .initialization import trust_environment_errors
            errors = trust_environment_errors(environment, verify_files=False)
            if errors: raise ValueError('; '.join(errors))
            if not check['valid']: raise ValueError('trust transition basis changed: ' + ', '.join(check['reasons']))
            if environment.get('status') == 'invalid': raise ValueError('trust transition environment was invalidated')
            from .execution_profiles import resolve_profile, machine_invocation
            fixed = resolve_profile(self.instance['execution_profiles'], execution['execution_profile_ref'])
            invocation = machine_invocation(fixed, trust_environment=environment,
                on_started=lambda identity: self._machine_started(execution_id, identity))
            import inspect
            arguments = dict(source=item['lean_code'], declarations=item['declaration_names'], workspace=workspace,
                environment=environment, verifier=self.formal_verifier,
                **invocation, allowed_axioms=tuple(environment['allowed_axioms']))
            parameters = inspect.signature(self.formal_verifier).parameters
            if 'launch_ticket' in parameters or any(p.kind == inspect.Parameter.VAR_KEYWORD for p in parameters.values()):
                arguments['launch_ticket'] = deepcopy(execution['launch_ticket'])
            if 'should_stop' in parameters or any(p.kind == inspect.Parameter.VAR_KEYWORD for p in parameters.values()):
                arguments['should_stop'] = should_stop
            if should_stop():
                result = {'status': 'stopped', 'reason': 'stopped before trust verification'}
            else:
                result = yield execution_id, arguments
                self._live_execution_ids.discard(execution_id)
            raw_result = deepcopy(result)
            if should_stop():
                result = {**result, 'status': 'stopped', 'reason': 'trust verification stopped by control request'}
            if result.get('status') == 'verified' and (result.get('source_sha256') != target['source_sha256'] or
                    not _toolchain_matches(toolchain, result.get('toolchain'))):
                result = {**result, 'status': 'rejected', 'reason': 'Compiler fingerprint or source differs from the fixed transition input'}
            if result.get('status') == 'verified':
                from .formal import compare_formal_results
                result['identity_comparison'] = compare_formal_results(target, result)
        except Exception as error:
            result = {'status': 'failed', 'reason': f'{type(error).__name__}: {error}'}
        result.update(id=knowledge_id, execution_id=execution_id, trust_environment_id=transition['to_environment'],
                      allowed_axioms=deepcopy(environment['allowed_axioms']))
        artifact = f'runtime/artifacts/{execution_id}/trust-result.json'
        result['artifact_ref'] = artifact
        execution = self.runtime['executions'][execution_id]
        raw_artifact = f'runtime/artifacts/{new_id("BA")}/trust-returned.json'
        execution['result_ref'] = raw_artifact
        execution['raw_result_ref'] = raw_artifact
        self._save({raw_artifact: canonical_json(raw_result or result)})
        execution = self.runtime['executions'][execution_id]
        execution['result_ref'] = artifact
        # Machine result disposition is independent of the worker submission protocol.
        accepted = result['status'] == 'verified'
        if accepted:
            execution['submission_receipt'] = {'kind': 'machine_output', 'state': 'accepted',
                'execution_id': execution_id, 'evidence_ref': artifact, 'source_sha256': result['source_sha256'],
                'trust_environment_id': transition['to_environment'], 'accepted_at': self._lifecycle_now().isoformat()}
        if not self._end_machine_execution(execution, outcome='output_accepted' if accepted else 'execution_incomplete',
                                           disposition={'trust_result': artifact, 'status': result['status']}):
            self._save({artifact: canonical_json(result)})
            return False
        if self.runtime.get('active_execution') == execution_id:
            self.runtime['active_execution'] = None
        if result['status'] == 'stopped' or stop_requested:
            result.update(status='stopped', reason=result.get('reason') or 'trust verification stopped')
            self._record_machine_continuation(action, execution_id)
            from .activities import wait_for
            wait_for(self.runtime, execution['owner_activity_id'], reason='trust_check_stopped',
                     condition={'transition_id': transition_id, 'target': knowledge_id, 'resume': True},
                     next_owner='user', at=self._lifecycle_now().isoformat())
            if self.runtime.get('status') != 'closed': self._pause_lifecycle('trust_check_stopped')
            self._lifecycle_event('trust_target_stopped', target=knowledge_id, transition_id=transition_id,
                                  execution_id=execution_id, artifact_ref=artifact)
            self._save({artifact: canonical_json(result)})
            return
        self.runtime['trust_transitions'][transition_id] = record_transition_result(self.instance, self.runtime['trust_transitions'][transition_id], result)
        from .activities import finish_activity
        finish_activity(self.runtime, execution['owner_activity_id'], result_refs=[artifact], unresolved=[],
                        followups=[transition_id], at=self._lifecycle_now().isoformat())
        self._save({artifact: canonical_json(result)})
        self._lifecycle_event('trust_target_checked', target=knowledge_id, transition_id=transition_id, result=result['status'])
        if self.runtime['trust_transitions'][transition_id]['status'] == 'ready':
            self._enqueue('trust_activate', transition_id=transition_id)
        if getattr(self, '_calls', None) is not None:
            self.runtime['queue'][:] = [queued for queued in self.runtime['queue'] if queued != action]
            self._refresh_readiness()
            self._save()

    def _finish_trust_transition(self, transition_id, verification):
        self._require_action_clock()
        transition = self.runtime['trust_transitions'][transition_id]
        if transition['status'] in {'active', 'failed'}: return
        try:
            environment = self.instance['trust_environments'].get(transition['to_environment'])
            bindings = [row for row in transition.get('history', []) if row.get('kind') == 'environment_fixed']
            if (not environment or environment.get('status') == 'invalid' or len(bindings) != 1
                    or bindings[0]['environment_id'] != transition['to_environment']
                    or _digest(environment) != bindings[0]['environment_sha256']):
                raise ValueError('target trust environment changed during transition')
            if (verification.get('status') != 'verified'
                    or verification.get('manifest_sha256') != environment['manifest_sha256']):
                raise ValueError('complete current environment observation required: ' + '; '.join(verification.get('errors', [])))
            from .formal import compare_formal_results
            reviewed = {}
            pending = False
            for target in transition['targets']:
                result = transition.get('results', {}).get(target['id'], {})
                if result.get('status') != 'verified':
                    continue  # The domain checker rejects incomplete/failed targets.
                if not compare_formal_results(target, result)['requires_identity_review']:
                    continue
                cid = self._start_staged_identity_review(transition_id, target['id'])
                cycle = self.runtime['review_cycles'][cid]
                if cycle['status'] in {'completed', 'unresolved'}:
                    reviewed[target['id']] = self._completed_staged_identity_review(transition_id, target['id'], cid)
                else:
                    pending = True
            if pending:
                return  # Ready means checked, not activated; live K stays unchanged.
            if reviewed:
                candidate = deepcopy(transition)
                for kid, receipt in reviewed.items():
                    candidate['results'][kid]['identity_review'] = receipt
                self.instance = activate_transition(self.instance, candidate, runtime=self.runtime)
            else:
                self.instance = activate_transition(self.instance, transition, runtime=self.runtime)
        except ValueError as error:
            transition['status'] = 'failed'
            transition.setdefault('history', []).append({'kind': 'activation_failed', 'reason': str(error),
                                                         'at': self._lifecycle_now().isoformat()})
            self._lifecycle_event('trust_transition_failed', target=transition_id, reason=str(error))
            self._enqueue('research_plan', reason='Trust transition failed; the previous environment remains in force', transition_id=transition_id)
        else:
            self.instance['trust_environments'][transition['to_environment']]['validation_receipt'] = deepcopy(verification)
            transition.update(status='active', activated_at=self._lifecycle_now().isoformat())
            self._lifecycle_event('trust_transition_activated', target=transition_id)
