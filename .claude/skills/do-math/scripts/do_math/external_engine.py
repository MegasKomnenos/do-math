"""Engine integration for granted external operations: preparation, reconciliation, retry and their machine executions."""
from __future__ import annotations

from copy import deepcopy
from .external import prepare_operation, validate_operation, execute_operation, reconcile_operation, prepare_retry, recover_operation
from .execution_lifecycle import MACHINE_OUTPUT_RECEIPT

class ExternalEngineMixin:
    def _external_control(self, config, source_ref, *, academic_binding=None):
        """Apply one external operation control.

        ``academic_binding`` binds a prepared operation to the academic effect of
        a task (the engine's accepted external request). Only the engine passes
        it; a control payload cannot carry it.
        """
        operation = config.get('operation')
        if operation == 'prepare':
            if self.instance['lifecycle'].get('adoption', {}).get('external_policy') != 'explicit_grants':
                raise ValueError('external effects are disabled by the adopted policy')
            grant = self.instance.get('grants', {}).get(config.get('grant_id'))
            if not grant or grant.get('kind') != 'http': raise ValueError('HTTP operation requires an explicit HTTP grant')
            stable_source_ref = config.get('source_ref') or ('external:' + str(config['id']) if config.get('id') else source_ref)
            profile = self._execution_profile({'role': 'external_action'})
            scope = {key: config[key] for key in ('target_id', 'purpose', 'subject') if key in config}
            if 'actor_kind' in config and config['actor_kind'] != profile['actor_kind']:
                raise ValueError('external request scope differs from the actual execution profile: actor_kind')
            scope['actor_kind'] = profile['actor_kind']
            entry = prepare_operation(config.get('request'), config['grant_id'], stable_source_ref, config.get('id'), **scope)
            if academic_binding is not None:
                entry['academic_binding'] = deepcopy(academic_binding)
            if grant.get('academic_only') or grant.get('requires_academic') or academic_binding is not None:
                from .academic import bind_external_prerequisite
                entry = bind_external_prerequisite(self.instance, self.runtime, self._solution_basis(), entry,
                    resolve_evidence=self._academic_evidence)
            self._validate_external(entry, grant)
            existing = self.runtime['external_operations'].get(entry['id'])
            immutable = ('id', 'request_sha256', 'grant_id', 'source_ref', 'target_id', 'purpose', 'subject',
                         'actor_kind', 'academic_basis', 'academic_binding')
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
            for key in ('http_status', 'body_base64', 'body_sha256', 'error', 'credential_env', 'reconciliation', 'handling', 'succeeded', 'effect_absent'):
                entry.pop(key, None)
            self.runtime['external_operations'][entry['id']] = entry
            self._enqueue('external_action', entry['id'], grant_id=grant_id, source_ref=source_ref)
            self._lifecycle_event('external_operation_retry_prepared', target=entry['id'], source_ref=source_ref,
                                  previous_status=previous['status'])
        else:
            raise ValueError('external operation must be prepare, reconcile, or retry')

    def _external_prerequisite(self, operation, grant):
        from .academic import external_prerequisite
        return external_prerequisite(self.instance, self.runtime, self._solution_basis(), operation, grant,
                                     resolve_evidence=self._academic_evidence)

    def _validate_external(self, operation, grant):
        validate_operation(operation, grant, self._lifecycle_now().isoformat(), runtime=self.runtime,
                           academic_check=self._external_prerequisite)

    def _external_execution_record(self, operation):
        execution_id = operation.setdefault('execution_id', self.ports.clock.new_id('EX'))
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
                record['submission_receipt'] = {'kind': MACHINE_OUTPUT_RECEIPT, 'state': 'accepted',
                    'execution_id': execution_id, 'evidence_ref': operation['id'],
                    'source_sha256': operation['request_sha256'], 'accepted_at': self._lifecycle_now().isoformat()}
            self._end_machine_execution(record, outcome='cancelled' if operation['status'] == 'cancelled'
                                        else 'output_accepted' if accepted else 'execution_incomplete',
                                        disposition={'external_operation': operation['id'],
                                                     'effect_status': operation['status']})
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

    def _run_external_action(self, action):
        operation_id = action['target']
        operation = self.runtime['external_operations'][operation_id]
        if operation['status'] in {'confirmed', 'failed', 'cancelled'}: return
        if not operation.get('execution_id'): operation['execution_id'] = self.ports.clock.new_id('EX')
        if operation['status'] == 'unknown' or operation.get('transmission_phase') == 'recorded':
            if operation['status'] == 'prepared':
                operation.update(recover_operation(operation), error='Executor resumed without a confirmed remote outcome')
            self._external_execution_record(operation)
            self._lifecycle_event('external_reconciliation_required', target=operation_id)
            return
        previous = self.runtime['executions'].get(operation.get('execution_id'))
        if previous and previous['status'] == 'ended':
            operation['continuation_of'] = previous['id']
            operation['execution_id'] = self.ports.clock.new_id('EX')
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
            self._apply_inbox()
            return bool(self.runtime.get('stop_requested') or self.runtime.get('status') in {'paused', 'closed'} or
                        self.runtime['executions'].get(operation['execution_id'], {}).get('stop_requested'))
        try:
            from .execution_profiles import match_profile_ref
            fixed_profile = match_profile_ref(self.instance['execution_profiles'], action['profile_ref'])
            result = execute_operation(deepcopy(operation), deepcopy(grant), persist=persist,
                timeout_seconds=fixed_profile['window']['call_timeout_seconds'], should_stop=should_stop,
                runtime=self.runtime, academic_check=self._external_prerequisite,
                current_grant=lambda gid: self.instance['grants'].get(gid, {}), transport=self.ports.http.request)
        except Exception as error:
            result = deepcopy(self.runtime['external_operations'][operation_id])
            sent = result.get('transmitted') is True
            result.update(status='unknown' if sent else 'cancelled', succeeded=None if sent else False,
                          effect_absent=None if sent else True, transmitted=sent, error=f'{type(error).__name__}: {error}')
            persist(result)
        self._lifecycle_event('external_operation_' + result['status'], target=operation_id,
                              source_ref=result['source_ref'], request_sha256=result['request_sha256'])
