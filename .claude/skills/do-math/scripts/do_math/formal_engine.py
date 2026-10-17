"""Engine integration for Lean verification: trust environments, their transitions and checks, and formal checks."""
from __future__ import annotations

from .wait_rules import waiting_action
from functools import partial
from copy import deepcopy
from pathlib import Path
from .knowledge import begin_transition, record_transition_result, activate_transition, invalidate_environment, validate_basis
from .execution_lifecycle import MACHINE_OUTPUT_RECEIPT
from .canonical import canonical_json, exact_content_hash
from .state_contract import ARTIFACT_ROOT
from .wait_rules import FORMAL_WAIT_RULES, FORMAL_RECOVERABLE_STOPS, formal_wait

def _toolchain_matches(expected, actual):
    return isinstance(actual, dict) and bool(actual.get('sha256')) and expected == actual


class FormalEngineMixin:
    def _trust_control(self, config, source_ref):
        operation = config.get('operation')
        from .trust_validation import environment_errors
        if operation == 'register':
            from .trust_validation import register_request_errors
            from .trust_inventory import read_record, usable_errors, binding as baseline_binding
            errors = register_request_errors(config)
            if errors:
                raise ValueError('; '.join(errors))
            reference, bound = config['toolchain_record'], config['binding']
            try:
                record = read_record(reference['path'])
            except OSError as error:
                raise ValueError('toolchain record unavailable: ' + str(error)) from error
            if (record['id'] != reference['id'] or record['identity'] != config['toolchain']
                    or bound['baseline'] >= len(record['baselines']) or baseline_binding(record, bound['baseline']) != bound):
                raise ValueError('trust registration differs from its toolchain record')
            errors = usable_errors(record)
            if record['baselines'][bound['baseline']]['validation']['status'] != 'verified':
                errors.append('bound toolchain baseline has no successful representative check')
            if errors:
                raise ValueError('; '.join(errors))
            environment_id = self.ports.clock.new_id('TE')
            environment = {'id': environment_id, 'toolchain': deepcopy(config['toolchain']),
                           'allowed_axioms': deepcopy(config['allowed_axioms']), 'status': 'registered',
                           'source_ref': source_ref, 'toolchain_record': deepcopy(reference)}
            errors = environment_errors(environment, bound)
            if errors:
                raise ValueError('; '.join(errors))
            self.instance.setdefault('trust_environments', {})[environment_id] = environment
            self.runtime.setdefault('trust_bindings', {})[environment_id] = deepcopy(bound)
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
            transition = begin_transition(self.instance, environment_id, clock=self.ports.clock)
            # Registration and stored-state validation own the lexical contract.
            # Live identity/fingerprint admission remains in check_environment.
            transition.update(source_ref=source_ref, created_at=self._lifecycle_now().isoformat())
            transition.setdefault('history', []).append({'kind': 'environment_fixed',
                'environment_id': environment_id, 'environment_sha256': exact_content_hash(environment),
                'source_ref': source_ref, 'at': transition['created_at']})
            self.runtime['trust_transitions'][transition['id']] = transition
            for target in transition['targets']:
                self._enqueue('trust_check', target['id'], transition_id=transition['id'], source_ref=source_ref)
            if not transition['targets']:
                self._enqueue('trust_activate', transition_id=transition['id'], source_ref=source_ref)
            self._lifecycle_event('trust_transition_started', target=transition['id'], source_ref=source_ref)
        elif operation == 'invalidate':
            self.instance, self.runtime = invalidate_environment(self.instance, self.runtime,
                config.get('env_id'), config.get('reason', 'Trust environment invalidated by explicit user decision'), clock=self.ports.clock)
            self._lifecycle_event('trust_environment_invalidated', target=config.get('env_id'), source_ref=source_ref)
        else:
            raise ValueError('trust operation must be register, transition or invalidate')

    def _formal_environment(self):
        """The active environment's stored contract; live files are checked by the formal step."""
        self._require_action_clock()
        from .trust_validation import require_active_environment
        return require_active_environment(self.instance, self.runtime, host=self.ports.host)

    def _apply_trust_rebind(self, check):
        """Follow a baseline that setup_lean.py --rerecord appended; never author one."""
        rebind = check.get('rebind')
        environment_id = check.get('environment_id')
        bindings = self.runtime.setdefault('trust_bindings', {})
        if not rebind or bindings.get(environment_id) != rebind['previous']:
            return
        bindings[environment_id] = deepcopy(rebind['current'])
        self._lifecycle_event('trust_environment_rebound', target=environment_id, schedule=False,
            basis={'toolchain_record': deepcopy(check['toolchain_record']),
                   'previous': deepcopy(rebind['previous']), 'current': deepcopy(rebind['current']),
                   'recorded_at': rebind['recorded_at']})

    def _resume_formal_waits(self):
        """Requeue parked formal checks once the condition that parked them is gone.

        A ``formal_environment`` wait resumes when its toolchain record or the
        active environment changed. A ``formal_authority`` wait, and a
        ``formal_stopped`` wait stopped only by a pause or by changed authority,
        environment or input, resumes when an active environment admits formal
        checks and the action is authorized: the gate ``_formal_steps`` applies
        again before any compiler start. A check stopped by an explicit
        execution stop stays parked.
        """
        from .governance import authorize
        from .trust_validation import environment_changed
        for identifier, waiting in list(self.runtime.get('waiting_actions', {}).items()):
            kind, detail = waiting.get('kind'), waiting.get('detail', {})
            rule = FORMAL_WAIT_RULES.get(kind)
            if rule is None:
                continue
            if rule['resume'] == 'environment_changed':
                if not environment_changed(self.instance, detail):
                    continue
            elif rule['resume'] == 'authority_and_environment' or (rule['resume'] == 'recoverable_stop'
                    and set(detail.get('stop_reasons', ())) <= FORMAL_RECOVERABLE_STOPS):
                try:
                    self._formal_environment()
                except ValueError:
                    continue
                if not authorize(self.instance, waiting['action'], runtime=self.runtime, at=self.ports.clock.now())['allowed']:
                    continue
            else:
                continue
            if not any(queued.get('id') == identifier for queued in self.runtime['queue']):
                action = deepcopy(waiting['action'])
                if waiting.get('execution_id'):
                    action['continuation_of'] = waiting['execution_id']
                self.runtime['queue'].append(action)
            del self.runtime['waiting_actions'][identifier]
            # Release only this formal owner's matching obligation. The next
            # registration must not be what makes an already resolved wait disappear.
            activity = self.runtime.get('activities', {}).get(waiting['action'].get('owner_activity_id'))
            if activity and activity['status'] == 'waiting' and activity['waiting']['kind'] == kind:
                condition = activity['waiting']['condition']
                direct = condition == {'kind': kind, 'knowledge_id': waiting['action'].get('target')}
                action_ids = condition.get('action_ids', []) if isinstance(condition, dict) else []
                if direct or (identifier in action_ids and not any(
                        aid in self.runtime['waiting_actions'] for aid in action_ids)):
                    from .activities import resume_activity
                    resume_activity(self.runtime, activity['id'], condition=condition, at=self.ports.clock.now())
            self.runtime['history'].append({'kind': kind + '_wait_resumed', 'action_id': identifier,
                                            'previous': deepcopy(detail)})

    def _run_trust_activation(self, action):
        from .trust_validation import check_environment
        return self._run_machine_steps(self._trust_activation_steps(action),
                                       calculator=partial(check_environment, host=self.ports.host))

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
        execution_id = self.ports.clock.new_id('EX')
        execution = self._register_execution(action, {'id': execution_id, 'role': 'trust_activate',
            'status': 'running', 'created_at': self._lifecycle_now().isoformat(),
             'input_snapshot': self.head,
             'input_manifest': [{'kind': 'trust_transition', 'id': transition_id, 'sha256': exact_content_hash(transition)}]})
        # These machine actions own fresh activities or continue their own
        # attempts, never AI review-restoration waits. Their built profiles
        # reserve neither provider/model slots nor host capacity.
        self._save()
        environment = deepcopy(self.instance['trust_environments'][transition['to_environment']])
        binding = deepcopy(self.runtime.get('trust_bindings', {}).get(transition['to_environment']))
        # One record read, identity check and fingerprint scan; there is no long scan to cancel.
        verification = yield execution_id, {'environment': environment, 'binding': binding, 'clock': self.ports.clock}
        self._live_execution_ids.discard(execution_id)
        execution = self.runtime['executions'][execution_id]
        if (self._execution_stop_requested(action, execution) or bool(self.runtime.get('maintenance_fence'))
                or self.instance['trust_environments'].get(transition['to_environment']) != environment):
            self._end_machine_execution(execution, outcome='execution_incomplete', disposition={'kind':'environment_interrupted'})
            from .activities import wait_for
            wait_for(self.runtime, execution['owner_activity_id'], kind='environment_interrupted', reason='environment_interrupted',
                     condition={'transition_id':transition_id}, next_owner='engine', at=self._lifecycle_now().isoformat())
            self._record_machine_continuation(action, execution_id)
            self._save({f'{ARTIFACT_ROOT}{execution_id}/environment.json':canonical_json(verification)})
            return False
        self._action_lifecycle_gate(action)
        if verification.get('status') == 'verified':
            self._apply_trust_rebind(verification)
        self._finish_trust_transition(transition_id, verification)
        transition = self.runtime['trust_transitions'][transition_id]
        execution = self.runtime['executions'][execution_id]
        artifact = f'{ARTIFACT_ROOT}{execution_id}/trust-activation.json'
        result = {'transition_id': transition_id, 'status': transition['status'],
                  'trust_environment_id': transition['to_environment'],
                  'reason': next((r['reason'] for r in reversed(transition.get('history', []))
                                  if r.get('kind') == 'activation_failed'), None)}
        accepted = transition['status'] == 'active'
        execution['result_ref'] = artifact
        if accepted:
            execution['submission_receipt'] = {'kind': MACHINE_OUTPUT_RECEIPT, 'state': 'accepted',
                'execution_id': execution_id, 'evidence_ref': artifact,
                'source_sha256': exact_content_hash(result), 'trust_environment_id': transition['to_environment'],
                'accepted_at': self._lifecycle_now().isoformat()}
        if not self._end_machine_execution(execution, outcome='output_accepted' if accepted else 'execution_incomplete',
                                           disposition={'kind': 'trust_activation', **result, 'artifact_ref': artifact}):
            self._save({artifact: canonical_json(result)})
            return False
        from .activities import finish_activity
        finish_activity(self.runtime, execution['owner_activity_id'], result_refs=[artifact],
                        unresolved=[] if accepted else [transition_id], followups=[], at=self._lifecycle_now().isoformat())
        self._save({artifact: canonical_json(result)})
        self._remove_action(action)
        self._refresh_readiness()
        self._save()

    def _run_trust_check(self, action):
        from .trust_validation import verify_formal
        return self._run_machine_steps(self._trust_check_steps(action),
                                       calculator=partial(verify_formal, host=self.ports.host))

    def _trust_check_steps(self, action):
        transition_id, knowledge_id = action['transition_id'], action['target']
        transition = self.runtime['trust_transitions'][transition_id]
        if transition['status'] not in {'checking', 'ready'}: return
        if knowledge_id in transition['results']:
            if transition['status'] == 'ready':
                self._enqueue('trust_activate', transition_id=transition_id, source_ref=transition['source_ref'])
            return
        target = next((t for t in transition['targets'] if t['id'] == knowledge_id), None)
        if target is None: raise ValueError('trust check is not an assigned transition target')
        environment = deepcopy(self.instance['trust_environments'][transition['to_environment']])
        from .knowledge_records import proposal_view
        item = proposal_view(self.instance, knowledge_id)
        execution_id = self.ports.clock.new_id('EX')
        workspace = Path(self.instance['workspace']) / 'trust' / execution_id
        workspace.mkdir(parents=True, exist_ok=True)
        execution = self._register_execution(action, {'id': execution_id, 'role': 'trust_check', 'status': 'running',
            'created_at': self._lifecycle_now().isoformat()})
        self._save()
        toolchain = environment['toolchain']
        check = validate_basis([target['basis']], self.instance, self.runtime)
        stop_requested = False
        raw_result = None
        def should_stop():
            # Owner-thread judgment of published state; the verifier reads only its flag.
            nonlocal stop_requested
            stop_requested = stop_requested or bool(
                self._execution_stop_requested(action, self.runtime['executions'][execution_id]) or
                self.instance['trust_environments'].get(transition['to_environment']) != environment or
                not validate_basis([target['basis']], self.instance, self.runtime)['valid'])
            return stop_requested
        binding = deepcopy(self.runtime.get('trust_bindings', {}).get(transition['to_environment']))
        try:
            if not check['valid']: raise ValueError('trust transition basis changed: ' + ', '.join(check['reasons']))
            if environment.get('status') == 'invalid': raise ValueError('trust transition environment was invalidated')
            from .execution_profiles import match_profile_ref, machine_invocation
            fixed = match_profile_ref(self.instance['execution_profiles'], execution['execution_profile_ref'])
            invocation = machine_invocation(fixed, trust_environment=environment,
                on_started=lambda identity: self._machine_started(execution_id, identity))
            result = yield from self._lean_machine_call(execution_id, invocation, source=item['lean_code'],
                declarations=item['declaration_names'], workspace=workspace, environment=environment,
                binding=binding, should_stop=should_stop, stopped_reason='stopped before trust verification')
            raw_result = deepcopy(result)
            if should_stop():
                result = {**result, 'status': 'stopped', 'reason': 'trust verification stopped by control request'}
            if result.get('status') == 'verified' and (result.get('source_sha256') != target['source_sha256'] or
                    not _toolchain_matches(toolchain, result.get('toolchain'))):
                result = {**result, 'status': 'rejected', 'reason': 'Compiler fingerprint or source differs from the fixed transition input'}
            if result.get('status') == 'verified':
                from .lean_evidence import compare_formal_results
                result['identity_comparison'] = compare_formal_results(target, result)
        except Exception as error:
            result = {'status': 'failed', 'reason': f'{type(error).__name__}: {error}'}
        if result.get('environment_check', {}).get('status') == 'verified':
            self._apply_trust_rebind(result['environment_check'])
        result.update(id=knowledge_id, execution_id=execution_id, trust_environment_id=transition['to_environment'],
                      allowed_axioms=deepcopy(environment['allowed_axioms']))
        artifact = f'{ARTIFACT_ROOT}{execution_id}/trust-result.json'
        result['artifact_ref'] = artifact
        self._preserve_machine_return(execution_id, f'{ARTIFACT_ROOT}{self.ports.clock.new_id("BA")}/trust-returned.json',
                                      raw_result or result)
        execution = self.runtime['executions'][execution_id]
        execution['result_ref'] = artifact
        # Machine result disposition is independent of the worker submission protocol.
        accepted = result['status'] == 'verified'
        if accepted:
            execution['submission_receipt'] = {'kind': MACHINE_OUTPUT_RECEIPT, 'state': 'accepted',
                'execution_id': execution_id, 'evidence_ref': artifact, 'source_sha256': result['source_sha256'],
                'trust_environment_id': transition['to_environment'], 'accepted_at': self._lifecycle_now().isoformat()}
        if not self._end_machine_execution(execution, outcome='output_accepted' if accepted else 'execution_incomplete',
                                           disposition={'trust_result': artifact, 'status': result['status']}):
            self._save({artifact: canonical_json(result)})
            return False
        if result['status'] == 'stopped' or stop_requested:
            result.update(status='stopped', reason=result.get('reason') or 'trust verification stopped')
            self._record_machine_continuation(action, execution_id)
            from .activities import wait_for
            wait_for(self.runtime, execution['owner_activity_id'], kind='trust_check_stopped', reason='trust_check_stopped',
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
            self._enqueue('trust_activate', transition_id=transition_id,
                          source_ref=self.runtime['trust_transitions'][transition_id]['source_ref'])
        self._remove_action(action)
        self._refresh_readiness()
        self._save()

    def _formal(self, action):
        from .trust_validation import verify_formal
        return self._run_machine_steps(self._formal_steps(deepcopy(action)),
                                       calculator=partial(verify_formal, host=self.ports.host))

    def _formal_steps(self, action):
        """One central Lean check of a knowledge proposal (the ``formal_check`` machine role).

        The scheduler starts it in the owner pass in which ``_dispatchable``
        passed the action's lifecycle gate; that gate is its last before start.
        A verified result becomes the proposal's formal result and opens its
        identity review; a failed one returns to the research plan.
        """
        from .activities import continue_activity, wait_for
        from .execution_profiles import machine_invocation
        from .lean_evidence import lean_source_sha256
        from .governance import authorize
        from .input_basis import capture_decision_basis, decision_basis_changes
        from .knowledge_records import proposal_view, record_formal_result
        from .payloads import json_safe
        from .planning import action_read_ids
        action.setdefault('id', self.ports.clock.new_id('AC'))
        action.setdefault('lineage_id', action['id'])
        kid = action['target']
        proposal = proposal_view(self.instance, kid)
        profile = self._execution_profile(action)
        execution_id = self.ports.clock.new_id('EX')
        environment_error = None
        try:
            environment = deepcopy(self._formal_environment())
            binding = deepcopy(self.runtime['trust_bindings'][environment['id']])
            invocation = machine_invocation(profile, trust_environment=environment,
                on_started=lambda identity: self._machine_started(execution_id, identity))
        except ValueError as error:
            environment, environment_error = None, str(error)
        environment_id = environment['id'] if environment else None
        authority = authorize(self.instance, action, runtime=self.runtime, at=self.ports.clock.now())
        if not authority['allowed'] or environment is None:
            activity = self._activity_for_action(action)
            reason = authority['reason'] if not authority['allowed'] else environment_error
            wait_for(self.runtime, activity['id'], kind='formal_authority', reason=reason,
                condition={'kind': 'formal_authority', 'knowledge_id': kid}, next_owner='trust_governance',
                at=self.ports.clock.now())
            self.runtime.setdefault('waiting_actions', {})[action['id']] = formal_wait(action, 'formal_authority', reason)
            self._remove_action(action)
            self._save()
            return
        source, declarations = proposal['lean_code'], deepcopy(proposal['declaration_names'])
        predecessor = self.runtime['executions'].get(action.get('continuation_of'))
        manifest = [{'kind': 'formal_source', 'sha256': lean_source_sha256(source),
                     'declaration_names': declarations},
                    {'kind': 'trust_environment', 'id': environment_id,
                     'sha256': exact_content_hash(environment)}]
        if predecessor and predecessor.get('role') == 'formal_check':
            prior = predecessor.get('input_manifest', [])
            if prior != manifest:
                self._remove_action(action)
                self._enqueue('research_plan', reason='Formal continuation inputs changed; reassess the preserved result',
                              evidence_refs=[kid, predecessor['id']])
                self._settle_activity(predecessor['id'])
                self._save()
                return
        workspace = Path(self.instance['workspace']) / 'formal' / execution_id
        execution = self._register_execution(action, {
            'id': execution_id, 'role': 'formal_check', 'status': 'running',
            'created_at': self.ports.clock.now(), 'grant_id': authority['grant_id'],
            'input_snapshot': self.head,
            'decision_basis': capture_decision_basis(self.instance, self.runtime,
                action_read_ids(action, self.instance, self.runtime)),
            'input_manifest': manifest}, profile=profile)
        workspace.mkdir(parents=True)
        self._save()
        stop_reasons = set()
        def stop():
            # Owner-thread judgment of published state; the verifier reads only its flag.
            reasons = set()
            if self._instance_closed():
                reasons.add('instance_ended')
            if self.runtime['status'] == 'paused' or self.runtime.get('stop_requested'):
                reasons.add('instance_paused')
            requested_stop = self.runtime['executions'][execution_id].get('stop_requested')
            if requested_stop:
                # governance._dispose_grant_consumers marks revocation on the
                # running attempt. It is recoverable authority loss, not an
                # explicit request to hold this execution permanently.
                reasons.add('authority_changed' if requested_stop == 'grant_revoked' else 'execution_stop_requested')
            if not authorize(self.instance, action, runtime=self.runtime, at=self.ports.clock.now())['allowed']:
                reasons.add('authority_changed')
            if (self.instance.get('active_trust_environment') != environment_id
                    or self.instance.get('trust_environments', {}).get(environment_id) != environment):
                reasons.add('trust_environment_changed')
            if decision_basis_changes(execution['decision_basis'], self.instance, self.runtime):
                reasons.add('input_changed')
            stop_reasons.update(reasons)
            return bool(reasons)
        result = yield from self._lean_machine_call(execution_id, invocation, source=source,
            declarations=declarations, workspace=workspace, environment=environment, binding=binding,
            should_stop=stop, stopped_reason='formal authority changed')
        result = json_safe(result)
        # Preserve returned evidence before currentness checks or domain publication.
        raw_bundle = self.ports.clock.new_id('BA')
        self._preserve_machine_return(execution_id, f'{ARTIFACT_ROOT}{raw_bundle}/formal-returned.json', result,
                                      artifact_bundle=raw_bundle)
        if stop():
            result = {**result, 'status': 'stopped', 'reason': ', '.join(sorted(stop_reasons))}
        # A public revision creates new KN/FR records; stop() checks the old
        # proposal's decision basis without rewriting its returned evidence.
        bundle = self.ports.clock.new_id('BA')
        reference = f'{ARTIFACT_ROOT}{bundle}/formal.json'
        execution = self.runtime['executions'][execution_id]
        execution.update(result_ref=reference, artifact_bundle=bundle, formal_status=result['status'])
        # A held execution keeps its capacity and records no formal result.
        released = self._release_machine_execution(execution, at=self.ports.clock.now())
        if released:
            # Failed compiler runs remain evidence. Only complete checked evidence can seal a formal result.
            if result['status'] == 'verified':
                try:
                    self._require_action_clock()
                    # stop() checked the fixed environment. The receiver still
                    # checks active authority, new transitions and exact evidence.
                    self.instance = record_formal_result(self.instance, kid,
                        {**result, 'execution_id': execution_id, 'artifact_ref': reference}, environment_id,
                        runtime=self.runtime)
                except ValueError as error:
                    result = {**result, 'status': 'failed', 'reason': str(error)}
                    execution['formal_status'] = 'failed'
            if result.get('environment_check', {}).get('status') == 'verified':
                self._apply_trust_rebind(result['environment_check'])
            if result['status'] == 'verified':
                execution['submission_receipt'] = {'kind': MACHINE_OUTPUT_RECEIPT, 'state': 'accepted',
                    'execution_id': execution_id, 'evidence_ref': reference, 'source_sha256': lean_source_sha256(source),
                    'trust_environment_id': environment_id, 'accepted_at': self.ports.clock.now()}
            self._end_machine_execution(execution,
                outcome='output_accepted' if result['status'] == 'verified' else 'execution_incomplete',
                disposition={'kind': 'formal_result', 'status': result['status'], 'artifact_ref': reference,
                             'stop_reasons': sorted(stop_reasons)})
            resumable = (result['status'] == 'stopped' and 'instance_paused' in stop_reasons
                         and not stop_reasons.intersection({'instance_ended', 'authority_changed',
                                                            'trust_environment_changed', 'input_changed'}))
            if resumable:
                continue_activity(self.runtime, execution_id, at=self.ports.clock.now(),
                                  reason='formal_paused')
            else:
                self._remove_action(action)
            if result.get('error_kind') == 'trust_environment' and not resumable:
                self.runtime.setdefault('waiting_actions', {})[action['id']] = formal_wait(action, 'formal_environment',
                    result['reason'], execution_id=execution_id, detail={'environment_id': environment_id,
                        'record_state': result.get('environment_check', {}).get('record_state')})
            elif result['status'] != 'verified' and result['status'] != 'stopped':
                self._enqueue('research_plan', reason='Assess preserved formal verification result', formal_target=kid)
            elif result['status'] == 'stopped' and not resumable and 'instance_ended' not in stop_reasons:
                self.runtime.setdefault('waiting_actions', {})[action['id']] = formal_wait(action, 'formal_stopped',
                    result.get('reason'), execution_id=execution_id, detail={'stop_reasons': sorted(stop_reasons)})
            self._settle_activity(execution_id)
        # The formal bundle holds the checked Lean source beside its judged result.
        self._save({f'{ARTIFACT_ROOT}{bundle}/proposal.lean': source.encode(), reference: canonical_json(result)})
        if released and result['status'] == 'verified':
            try:
                self._start_identity_review(kid)
            except (ValueError, KeyError, TypeError) as error:
                review_action = {'id': self.ports.clock.new_id('AC'), 'role': 'identity_review', 'target': kid}
                self.runtime.setdefault('waiting_actions', {})[review_action['id']] = waiting_action({
                    'action': review_action,
                    'kind': 'review_initialization', 'execution_id': execution_id,
                    'reason': str(error), 'next_owner': 'review_policy'})
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
                    or exact_content_hash(environment) != bindings[0]['environment_sha256']):
                raise ValueError('target trust environment changed during transition')
            if (verification.get('status') != 'verified' or verification.get('environment_id') != transition['to_environment']
                    or verification.get('identity_sha256') != exact_content_hash(environment['toolchain'])
                    or verification.get('binding') != self.runtime.get('trust_bindings', {}).get(transition['to_environment'])):
                raise ValueError('current environment check required: ' + '; '.join(verification.get('errors', [])))
            from .lean_evidence import compare_formal_results
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
                self.instance = activate_transition(self.instance, candidate, runtime=self.runtime, clock=self.ports.clock, at=self.ports.clock.now())
            else:
                self.instance = activate_transition(self.instance, transition, runtime=self.runtime, clock=self.ports.clock, at=self.ports.clock.now())
        except ValueError as error:
            transition['status'] = 'failed'
            transition.setdefault('history', []).append({'kind': 'activation_failed', 'reason': str(error),
                                                         'at': self._lifecycle_now().isoformat()})
            event = self._lifecycle_event('trust_transition_failed', target=transition_id, reason=str(error))
            self._enqueue('research_plan', reason='Trust transition failed; the previous environment remains in force',
                          transition_id=transition_id, event_refs=[event['id']])
        else:
            self.instance['trust_environments'][transition['to_environment']]['validation_receipt'] = deepcopy(verification)
            transition.update(status='active', activated_at=self._lifecycle_now().isoformat())
            self._lifecycle_event('trust_transition_activated', target=transition_id)
