"""Central governance transitions; ENGINE owns one public Git publication.

The hooks stage ordinary controls and model results on the same roots as the
other engine mixins. They never publish a second control receipt or call save.
"""
from .wait_rules import waiting_action
from copy import deepcopy
from pathlib import Path

from . import governance, academic, knowledge, knowledge_records, execution_profiles, questions
from .configuration import validate_config
from .control_contracts import user_decision_changed
from .canonical import canonical_json, exact_content_hash
from .session_slots import live_action_ids
from .task_contracts import TERMINAL_TASK_STATUSES
from .wait_rules import AUTHORITY_WAIT_RULES


def bind_host_configuration(instance, config, *, origin):
    """Resolve the explicit request-source alias to the preserved user input."""
    config = deepcopy(config)
    host = config.get('host_resources')
    if host is None or 'configuration:request' not in host['constraint']['authority_refs']:
        return config
    if origin != 'user':
        raise ValueError('host configuration request requires user authority')
    raw = canonical_json({'host_resources': host})
    identifier = 'GS-host-' + exact_content_hash({'host_resources': host})
    source = governance.preserve_source(identifier, raw.decode('utf-8'), origin='user')
    sources = instance['governance_sources']
    if identifier in sources and sources[identifier] != source:
        raise ValueError('host configuration source identity changed')
    sources[identifier] = source
    constraint = host['constraint']
    host['constraint'] = execution_profiles.host_constraint(host_id=constraint['host_id'],
        limits={'jobs': constraint['max_jobs'], 'memory_bytes': constraint['memory_bytes'],
                'cpu_rate_basis_points': constraint['cpu_rate_basis_points']},
        control_reserve=constraint['control_reserve'],
        authority_refs=[identifier if ref == 'configuration:request' else ref for ref in constraint['authority_refs']])
    return config


class GovernanceEngineMixin:
    def _configure_candidate(self, instance, runtime, request):
        """Single transition for public configure and checked configuration units."""
        from .scholarly_config import resolve_scholarly_server
        from .wait_rules import RESOURCE_WAITS
        from .session_slots import quiescence
        patch = request.get('config', {})
        if not isinstance(patch, dict): raise ValueError('configuration patch must be an object')
        if request.get('origin', 'user') not in {'user', 'operator'}: raise ValueError('unknown configuration authority')
        current = instance['config']
        candidate = {**current, **patch}
        validate_config(candidate, host_id=self.host_id)
        result, state = deepcopy(instance), deepcopy(runtime)
        candidate = bind_host_configuration(result, candidate, origin=request.get('origin', 'user'))
        if request.get('origin', 'user') == 'operator' and user_decision_changed(current, candidate):
            raise ValueError('resource settings require a user decision at application time')
        host_changed = candidate.get('host_resources') != current.get('host_resources')
        if host_changed and (self._executor_running or self._calls is not None
                or self._live_execution_ids or any(quiescence(runtime).values())):
            raise ValueError('host resource changes require a stopped executor with no live execution or held reservation')
        if candidate['scholarly_enabled']:
            candidate['scholarly_server'] = resolve_scholarly_server(candidate['scholarly_server'], start=Path.cwd(), codex_home=self.codex_home)
        editions = execution_profiles.build_profiles(candidate, host=self.ports.host)
        result['config'] = candidate
        execution_profiles.apply_editions(result, editions)
        live = live_action_ids(state)
        waiting = [row['action'] for row in state.get('waiting_actions', {}).values()]
        for pending in [*state['queue'], *waiting]:
            if pending.get('id') not in live: pending.pop('model_selection', None)
        if host_changed:
            from . import revisions
            def without_host(profile):
                return {key: value for key, value in profile.items() if key not in
                    {'id', 'sha256', 'host_resources', 'host_capacity_refs', 'host_capacity_status'}}
            for pending in [*state['queue'], *waiting]:
                if pending.get('target') in state.get('tasks', {}) or not pending.get('profile_ref'):
                    continue
                cycle = state.get('review_cycles', {}).get(pending.get('review_cycle_id'), {})
                if (cycle.get('scope_assessment') or cycle.get('slot_profiles')
                        or cycle.get('execution_accounting', {}).get('executions_used')):
                    continue
                original = execution_profiles.match_profile_ref(result['execution_profiles'], pending['profile_ref'])
                replacements = [profile for profile in editions['execution_profiles'].values()
                                if without_host(profile) == without_host(original)]
                if len(replacements) == 1:
                    pending['profile_ref'] = execution_profiles.profile_ref(replacements[0])
            affected = []
            for tid, task in state.get('tasks', {}).items():
                if task.get('status') in TERMINAL_TASK_STATUSES:
                    continue
                profiles = [execution_profiles.match_profile_ref(result['execution_profiles'], ref)
                            for ref in task.get('profile_refs', [])]
                if any(profile.get('host_capacity_refs', []) != ([result['host_capacity_ref']]
                        if result.get('host_capacity_ref') else []) for profile in profiles):
                    affected.append(tid)
            if affected:
                state['queue'].insert(0, {'id': self.ports.clock.new_id('AC'), 'role': 'research_preparation',
                    'reason': 'Reprepare task profile contracts for the newly adopted host resources',
                    'revision_targets': revisions.capture_targets(result, state, affected)})
        resources_changed = user_decision_changed(current, candidate)
        if state.get('status') in {'waiting', 'capacity_waiting'} and resources_changed:
            for action in state['queue']:
                if (action.get('id') not in live and action.get('dispatch_wait', {}).get('kind') in RESOURCE_WAITS):
                    action.pop('dispatch_wait', None)
            if state['queue']:
                state['status'] = 'ready'
        return result, state

    def governance_owner_handlers(self):
        handlers = governance.import_owner_handlers(clock=self.ports.clock)
        def configure(instance, runtime, unit, approval):
            return self._configure_candidate(instance, runtime, {'action': 'configure',
                'origin': approval['actor'], 'config': unit['payload']['config']})
        governance.register_configuration_owner(handlers, apply=configure, host_id=self.host_id)
        return handlers

    def _governance_input_source(self, input_id):
        return governance.import_input_source(self.instance, self.runtime, input_id)

    def _governance_context(self, action, context):
        # The caller built this context for this role; prepare_role_input copies it before use.
        if action['role'] == 'goal_audit':
            context['additional_audit_input'] = governance.additional_audit_input(self.instance, self.runtime)
        elif action['role'] == 'intent_interpretation' and not action.get('delegation_application_id'):
            request = next(row for row in self.runtime['inputs'] if row['id'] == action['target'])
            source = self._governance_input_source(action['target'])
            context['user_request'] = {**deepcopy(request), 'text': source['text'], 'sha256': source['sha256']}
            context['original_source'] = source
            # A task_scope unit binds the contract edition by the hash the decision checks (apply_decision).
            from .planning import contract_hash
            for task in context.get('tasks', []):
                task['contract_sha256'] = contract_hash(task)
            context['import_consumers'] = governance.import_consumer_catalog(self.governance_owner_handlers(), clock=self.ports.clock)
            context['governance_records'] = deepcopy(list(self.instance.get('governance', {}).values()))
            context['delegations'] = deepcopy(list(self.instance.get('delegations', {}).values()))
            context['source_coordinate_unit'] = 'unicode_codepoint'
            context['interpretation_stage'] = action.get('stage', 'interpret')
            context['interpretation_to_check'] = deepcopy(self.runtime.get('intent_imports', {}).get(action.get('import_id')))
            if action.get('import_check_release'):
                release = next(row for row in self.runtime['history']
                    if row.get('kind') == 'import_check_evidence_resumed' and row.get('sha256') == action['import_check_release'])
                context['import_check_evidence'] = governance.import_check_evidence_basis(self.instance, self.runtime, release['previous'])
            if action.get('previous_import_id'):
                context['previous_interpretation'] = deepcopy(self.runtime['intent_imports'][action['previous_import_id']])
        return context

    def _governance_schema(self, action, schema):
        if action['role'] != 'goal_audit': return schema
        schema = deepcopy(schema)
        schema['properties']['additional_audits'] = governance.additional_audit_schema(self.instance)
        if 'additional_audits' not in schema['required']: schema['required'].append('additional_audits')
        return schema

    def _bind_governance_input(self, action, execution, context):
        if action['role'] == 'goal_audit':
            expected = governance.additional_audit_input(self.instance, self.runtime)
            if context.get('additional_audit_input') != expected: raise ValueError('delivered additional audit input changed')
            execution['additional_audit_input'] = deepcopy(expected)
        if action.get('import_check_release'):
            bundle = self.runtime['intent_imports'][action['import_id']]
            release = governance.import_check_release(self.runtime, bundle, execution['id'], bundle['check'])
            expected = governance.import_check_evidence_basis(self.instance, self.runtime, release['previous'])
            if context.get('import_check_evidence') != expected:
                raise ValueError('delivered import check evidence changed')
            execution['import_check_basis'] = deepcopy(expected)

    def _retire_import_check_waits(self, bundle, reason):
        for aid, wait in list(self.runtime.get('waiting_actions', {}).items()):
            if wait.get('kind') != 'import_check_evidence' or wait['import_id'] != bundle['id']:
                continue
            self.runtime['history'].append({'kind': 'import_check_evidence_retired', 'reason': reason,
                'import_id': bundle['id'], 'previous': deepcopy(wait)})
            del self.runtime['waiting_actions'][aid]

    def _wait_import_check_evidence(self, action, bundle, execution_id, *, source_ref=None,
                                    read_artifact=None, output_files=None):
        execution = self.runtime['executions'][execution_id]
        output = bundle['check']
        routes = {r['question_index']: r for r in execution.get('extensions', {}).get('question_routes', [])}
        errors = governance.import_check_input_errors(output, execution.get('extensions', {}))
        if errors:
            raise ValueError(errors[0])
        source_ref = source_ref or execution.get('submission_intent', {}).get('output_ref')
        if not source_ref:
            raise ValueError('import check questions require the sealed output source')
        scopes = {}
        for index, route in routes.items():
            row = questions.link(self.runtime, execution_id=execution_id, field='questions/' + str(index),
                owner=route['owner'], targets=route['target_ids'], source_ref=source_ref,
                reason=route['reason'], blocks=route.get('blocks', False),
                obligation=route.get('obligation'), existing_question_id=route.get('existing_question_id'),
                handler_role=route.get('handler_role'), reopen_reason=route.get('reopen_reason'),
                observation_basis=([self._resolve_execution_evidence(execution_id, ref,
                    read_artifact=read_artifact, output_files=output_files) for ref in route['reopen_basis_refs']]
                    if route.get('reopen_basis_refs') else None), clock=self.ports.clock)
            scopes[row['id']] = list(dict.fromkeys([*scopes.get(row['id'], []), *route['target_ids']]))
        _, issued_instance, issued_runtime = self.store.view(execution['input_snapshot'])
        supplied = {q['id'] for q in issued_runtime.get('question_links', [])}
        # Read receipts in the check's actual input, not receipts arriving during its call.
        receipt_basis = {qid: questions.question_scope_state(issued_runtime, qid, scope)
            if qid in supplied else {'resolved': False, 'resolution_refs': []} for qid, scope in scopes.items()}
        # QU routing/report counts and the mutable import/check are not content evidence.
        excluded = ({q['id'] for q in self.runtime.get('question_links', [])} | set(self.runtime.get('intent_imports', {}))
            | {bundle['execution_id'], execution_id, *(c['execution_id'] for c in bundle['check_history'])})
        evidence = {ref: questions.reference_basis(issued_instance, issued_runtime, ref)
                    for ref in output.get('used_sources', []) if ref not in excluded}
        self.runtime.setdefault('waiting_actions', {})[action['id']] = waiting_action({
            'action': deepcopy(action), 'kind': 'import_check_evidence', 'import_id': bundle['id'],
            'execution_id': execution_id, 'bundle_sha256': bundle['sha256'],
            'source_sha256': bundle['source']['sha256'], 'check_sha256': output['sha256'],
            'question_ids': list(scopes), 'question_scopes': scopes, 'question_resolution_basis': receipt_basis,
            'evidence_basis': evidence, 'reason': '; '.join(output['findings']) or 'Required interpretation check evidence is unavailable',
            'next_owner': 'question_handler'})

    def _resume_import_check_waits(self):
        """One new independent check for a real release of this fixed input wait."""
        from .session_slots import held_reservations
        if self.instance.get('lifecycle', {}).get('state') == 'paused' or self._instance_closed():
            return False
        changed = False
        for aid, wait in list(self.runtime.get('waiting_actions', {}).items()):
            if wait.get('kind') != 'import_check_evidence':
                continue
            bundle = self.runtime['intent_imports'][wait['import_id']]
            owners = {eid: e for eid, e in self.runtime['executions'].items()
                      if e.get('action', {}).get('id') == aid}
            if any(e['status'] != 'ended' for e in owners.values()) or held_reservations(self.runtime, owners):
                continue
            if self.runtime['executions'][wait['execution_id']].get('outcome') != 'output_accepted':
                continue
            if bundle.get('superseded_by'):
                self._retire_import_check_waits(bundle, 'Interpretation was superseded')
                changed = True
                continue
            try:
                governance.current_import(self.instance, self.runtime, bundle['id'],
                    owner_handlers=self.governance_owner_handlers(), clock=self.ports.clock)
            except ValueError as error:
                if str(error) not in {'original public input changed', 'original version changed',
                        'import authority or affected targets changed', 'import domain premises changed',
                        'import domain owner is no longer registered'}:
                    raise
                self._queue_intent_rework(bundle, str(error))
                changed = True
                continue
            basis = governance.import_check_evidence_basis(self.instance, self.runtime, wait)
            if not governance.import_check_evidence_ready(wait, basis):
                continue
            identifier = self.ports.clock.new_id('AC')
            release = {'kind': 'import_check_evidence_resumed', 'action_id': identifier,
                       'previous': deepcopy(wait), 'basis': basis}
            release['sha256'] = exact_content_hash(release)
            self.runtime['history'].append(release)
            fields = {key: deepcopy(wait['action'][key]) for key in
                      ('initialization', 'grant_id', 'profile_ref', 'owner_activity_id', 'lineage_id') if key in wait['action']}
            self._enqueue('intent_interpretation', bundle['input_ref'], stage='check', import_id=bundle['id'],
                id=identifier, import_check_release=release['sha256'], **fields,
                reason='Required evidence changed; independently check the same preserved interpretation')
            del self.runtime['waiting_actions'][aid]
            changed = True
        return changed

    def _queue_intent_rework(self, bundle, reason):
        self._retire_import_check_waits(bundle, reason)
        author = self.runtime.get('executions', {}).get(bundle['execution_id'], {}).get('action', {})
        fields = {key: deepcopy(author[key]) for key in ('initialization', 'grant_id', 'profile_ref', 'owner_activity_id') if key in author}
        input_id = bundle['input_ref']
        current_source = self._governance_input_source(input_id)
        if current_source == bundle['source']:
            fields['previous_import_id'] = bundle['id']
        # A changed original can need a fresh interpretation before any check
        # exists. Only a checked import supplies a semantic repair basis.
        if 'check' in bundle:
            fields['intent_repair'] = {'import_id': bundle['id'], 'previous_sha256': bundle['sha256'],
                'check_execution_id': bundle['check']['execution_id'], 'findings': [reason]}
        self._enqueue('intent_interpretation', input_id, stage='interpret',
                      reason=reason, lineage_id=author.get('lineage_id', bundle['execution_id']), **fields)

    def _after_governance_import(self, import_id):
        bundle = self.runtime['intent_imports'][import_id]
        if bundle.get('application', {}).get('status') != 'applied': return
        assigned = live_action_ids(self.runtime)
        obsolete = [a for a in self.runtime.get('queue', []) if a.get('id') not in assigned
                    and a.get('role') == 'intent_interpretation'
                    and import_id in (a.get('import_id'), a.get('previous_import_id'))]
        for action in obsolete:
            self.runtime['queue'].remove(action)
            self.runtime.setdefault('history', []).append({'kind': 'applied_import_supersedes_pending_interpretation',
                'import_id': import_id, 'action': deepcopy(action)})
        input_id = bundle['input_ref']
        if self.instance.get('lifecycle', {}).get('input_id') == input_id:
            self._complete_initial_intent(input_id)
            self._activate_initialization()
        elif self.instance.get('lifecycle', {}).get('state') != 'initializing':
            self._enqueue('research_preparation', reason='checked user information')
        self._resume_import_question_waits()

    def _resume_action_authority_waits(self):
        """Requeue an unstarted action once, retaining every pinned authority field."""
        from .activities import resume_activity
        at = self._lifecycle_now().isoformat()
        for identifier, waiting in list(self.runtime.get('waiting_actions', {}).items()):
            if waiting.get('kind') not in AUTHORITY_WAIT_RULES:
                continue
            action = waiting['action']
            if any(execution.get('status') != 'ended' and execution.get('action', {}).get('id') == identifier
                   for execution in self.runtime['executions'].values()):
                continue
            authority = governance.authorize(self.instance, action, runtime=self.runtime, at=at)
            if not authority['allowed']:
                continue
            activity = self.runtime.get('activities', {}).get(action.get('owner_activity_id'))
            condition = {'kind': waiting['kind'], 'action_id': identifier}
            if activity and activity['status'] == 'waiting' and activity['waiting']['condition'] == condition:
                resume_activity(self.runtime, activity['id'], condition=condition, at=at)
            if not any(row.get('id') == identifier for row in self.runtime['queue']):
                self.runtime['queue'].append(deepcopy(action))
            self.runtime['history'].append({'kind': 'action_authority_resolved', 'action_id': identifier,
                'authority': deepcopy(authority), 'previous': deepcopy(waiting)})
            del self.runtime['waiting_actions'][identifier]

    def _resume_import_question_waits(self):
        """Only an applied answer resumes the original interpretation lineage."""
        for aid, wait in list(self.runtime.get('waiting_actions', {}).items()):
            if wait.get('kind') != 'import_user_decision':
                continue
            bundle = self.runtime['intent_imports'][wait['import_id']]
            questions = [row for row in self.runtime.get('question_links', [])
                if row.get('source_kind') == 'intent_import' and row.get('source_id') == bundle['id']
                and row.get('blocks')]
            if not questions or any(row['status'] == 'open' for row in questions):
                continue
            self.runtime['history'].append({'kind': 'import_question_wait_resumed', 'action_id': aid,
                'import_id': bundle['id'], 'previous': deepcopy(wait),
                'resolution_refs': sorted({row['resolution_ref'] for row in questions if row.get('resolution_ref')})})
            del self.runtime['waiting_actions'][aid]
            if not bundle.get('superseded_by'):
                self._queue_intent_rework(bundle, 'Apply the resolved user answers to the preserved original: ' +
                    ', '.join(sorted({row['resolution_ref'] for row in questions if row.get('resolution_ref')})))

    def _governance_control(self, request):
        if request['action'] == 'configure':
            self.instance, self.runtime = self._configure_candidate(self.instance, self.runtime, request)
            return True
        change = request.get('config', {}).get('change', {})
        if request['action'] != 'decision' or change.get('kind') != 'import_approval': return False
        normalized = {**request, 'config': change}
        bundle = self.runtime.get('intent_imports', {}).get(change.get('import_id'))
        was_applied = bool(bundle and bundle.get('application', {}).get('status') == 'applied')
        before_instance, before_runtime = deepcopy(self.instance), deepcopy(self.runtime)
        try:
            self.instance, self.runtime, _ = governance.apply_import_control(self.instance, self.runtime,
                normalized, owner_handlers=self.governance_owner_handlers(), clock=self.ports.clock)
            if not was_applied: self._after_governance_import(change['import_id'])
        except (ValueError, KeyError, TypeError) as error:
            self.instance, self.runtime = before_instance, before_runtime
            self._reject_governance_import(request, str(error))
            raise
        return True

    def _reject_governance_import(self, request, reason):
        """Stage reauthor routing before ENGINE records its one rejection result."""
        change = request.get('config', {}).get('change', {})
        if request.get('action') == 'decision' and change.get('kind') == 'import_approval':
            bundle = self.runtime.get('intent_imports', {}).get(change.get('import_id'))
            # Premature approval does not invalidate an interpretation still
            # awaiting its independent check. Keep that check's existing route.
            if (bundle and bundle.get('status') == 'approved' and 'check' in bundle and not bundle.get('superseded_by')
                    and bundle.get('application', {}).get('status') != 'applied'):
                self._queue_intent_rework(bundle, reason)

    def _apply_governance_intent(self, action, output, execution_id, *, source_ref=None,
                                 read_artifact=None, output_files=None):
        target = action['target']
        source = self._governance_input_source(target)
        handlers = self.governance_owner_handlers()
        if action.get('stage', 'interpret') == 'interpret':
            bundle = governance.prepare_import(self.instance, self.runtime, source, output, execution_id=execution_id,
                previous_id=action.get('previous_import_id'), owner_handlers=handlers, input_ref=target, clock=self.ports.clock)
            if action.get('previous_import_id'):
                self._retire_import_check_waits(self.runtime['intent_imports'][action['previous_import_id']], 'Interpretation was superseded')
            self._enqueue('intent_interpretation', target, stage='check', import_id=bundle['id'],
                **{key: deepcopy(action[key]) for key in ('initialization', 'grant_id', 'profile_ref', 'owner_activity_id') if key in action},
                lineage_id=action.get('lineage_id', action.get('id', target)),
                reason='Independently compare every meaning unit and question with the exact original')
            return bundle
        existing = self.runtime['intent_imports'][action['import_id']]
        if existing['source'] != source:
            self._queue_intent_rework(existing, 'original source changed before independent check')
            raise ValueError('original source changed before independent check')
        bundle = governance.check_import(self.instance, self.runtime, action['import_id'], output,
                                         execution_id=execution_id, owner_handlers=handlers, clock=self.ports.clock)
        if bundle['check']['decision'] == 'revision_required':
            self._queue_intent_rework(bundle, '; '.join(bundle['check']['findings']) or 'independent check is unresolved')
            return bundle
        if bundle['status'] != 'approved':
            self._wait_import_check_evidence(action, bundle, execution_id, source_ref=source_ref,
                read_artifact=read_artifact, output_files=output_files)
            return bundle
        required = {u['unit_id'] for u in bundle['output']['import_units'] if u['payload']}
        if not any(q['blocks'] for q in bundle['output'].get('question_details', [])) and required:
            self.runtime.setdefault('waiting_actions', {})[action.get('id', bundle['id'])] = waiting_action({
                'action': deepcopy(action), 'kind': 'import_application_authority', 'import_id': bundle['id'],
                'reason': 'checked interpretation lacks exact change approval', 'next_owner': 'user'})
            return bundle
        self.instance, self.runtime, receipt = governance.apply_import(self.instance, self.runtime, bundle['id'],
            owner_handlers=handlers, clock=self.ports.clock)
        if receipt['status'] == 'awaiting_decision':
            self.runtime.setdefault('waiting_actions', {})[action.get('id', bundle['id'])] = waiting_action({
                'action': deepcopy(action), 'kind': 'import_user_decision', 'import_id': bundle['id'],
                'reason': 'Checked interpretation awaits its blocking user answers', 'next_owner': 'user'})
        self._after_governance_import(bundle['id'])
        return receipt

    def _goal_audit_seal(self, action):
        if action.get('role') != 'goal_audit':
            return None
        rows = [j for j in self.instance.get('goal_judgments', [])
                if j.get('basis') == action.get('basis') and j.get('slot') == action.get('slot')]
        if not rows:
            return None
        if len(rows) != 1 or rows[0].get('required') != action.get('required'):
            raise ValueError('conflicting goal audit slot seals')
        judgment = rows[0]
        producer = self.runtime.get('executions', {}).get(judgment.get('execution_id'), {})
        if producer.get('role') != 'goal_audit' or any(
                producer.get('action', {}).get(key) != judgment.get(key) for key in ('basis', 'slot', 'required')):
            raise ValueError('goal audit seal differs from its producer')
        return judgment

    def _committed_goal_audit(self, execution_id):
        rows = [j for j in self.instance.get('goal_judgments', []) if j.get('execution_id') == execution_id]
        if not rows:
            return None
        execution = self.runtime.get('executions', {}).get(execution_id, {})
        judgment = self._goal_audit_seal(execution.get('action', {}))
        if (len(rows) != 1 or judgment != rows[0] or not any(
                r.get('execution_id') == execution_id and 'output' in r.get('members', [])
                for r in self.runtime.get('integrations', {}).values())):
            raise ValueError('goal audit seal lacks its original integration receipt')
        return judgment

    def _ensure_goal_audit_requests(self, basis, request_execution_id):
        if self._goal_basis_key() != basis:
            raise ValueError('goal audit request basis changed')
        required = self.instance['config']['goal_auditors']
        summary = {'basis': basis, 'required': required, 'slots': []}
        for slot in range(required):
            scope = {'role': 'goal_audit', 'basis': basis, 'slot': slot, 'required': required}
            def matches(action):
                return all(action.get(key) == value for key, value in scope.items())
            judgment = self._goal_audit_seal(scope)
            live = next((e for e in self.runtime.get('executions', {}).values()
                         if e.get('status') != 'ended' and matches(e.get('action', {}))), None)
            queued = next((a for a in self.runtime.get('queue', []) if matches(a)), None)
            waiting = next((w for w in self.runtime.get('waiting_actions', {}).values()
                            if matches(w.get('action', {}))), None)
            row = {'slot': slot}
            if judgment:
                row.update(state='sealed', judgment_id=judgment['id'])
                if judgment.get('current') is False:
                    row.update(state='sealed_unusable', next_owner='research_plan',
                               reason=deepcopy(judgment.get('currentness_changes', 'sealed judgment is no longer current')))
            elif live:
                row.update(state='running', execution_id=live['id'])
            elif queued:
                row.update(state='queued', action_id=queued['id'])
            elif waiting:
                row.update(state='waiting', action_id=waiting['action']['id'],
                           kind=waiting.get('kind'), next_owner=waiting.get('next_owner'))
            else:
                identifier = self.ports.clock.new_id('AC')
                self._enqueue(**scope, id=identifier, requested_by=request_execution_id,
                              reason='Complete the unsealed slot of the requested goal audit')
                row.update(state='queued_new', action_id=identifier)
            summary['slots'].append(row)
        self.runtime.setdefault('history', []).append({'kind': 'goal_audit_request',
            'execution_id': request_execution_id, **deepcopy(summary)})
        return summary

    def _retire_sealed_goal_audit_requests(self):
        from .activities import finish_activity
        if not self.instance.get('goal_judgments'):
            return False
        executions = self.runtime.get('executions', {})
        waits = self.runtime.setdefault('waiting_actions', {})
        actions = {a['id']: a for a in self.runtime.get('queue', []) if a.get('role') == 'goal_audit'}
        actions.update({w['action']['id']: w['action'] for w in waits.values() if w.get('action', {}).get('id')})
        changed = False
        for identifier, action in actions.items():
            judgment = self._goal_audit_seal(action)
            if not judgment:
                continue
            owners = {eid: e for eid, e in executions.items() if e.get('action', {}).get('id') == identifier}
            from .session_slots import held_reservations
            if (any(e.get('status') != 'ended' for e in owners.values())
                    or held_reservations(self.runtime, owners)
                    or (judgment['execution_id'] in owners
                        and owners[judgment['execution_id']].get('outcome') != 'output_accepted')):
                continue
            previous = waits.pop(identifier, None)
            self.runtime['queue'][:] = [a for a in self.runtime['queue'] if a.get('id') != identifier]
            self.runtime.setdefault('history', []).append({'kind': 'goal_audit_request_superseded',
                'action': deepcopy(action), 'waiting': deepcopy(previous), 'judgment_id': judgment['id']})
            changed = True
            activity = self.runtime.get('activities', {}).get(action.get('owner_activity_id'))
            if not activity or activity.get('status') == 'finished':
                continue
            assigned = [executions.get(eid, {}) for eid in activity.get('assigned_execution_ids', [])]
            remaining = [*self.runtime['queue'], *(w.get('action', {}) for w in waits.values())]
            if (any(a.get('owner_activity_id') == activity['id'] for a in remaining)
                    or any(e.get('status') != 'ended' or e.get('action', {}).get('role') != 'goal_audit'
                           or any(e.get('action', {}).get(k) != action.get(k) for k in ('basis', 'slot', 'required'))
                           or (e.get('id') == judgment['execution_id'] and e.get('outcome') != 'output_accepted')
                           for e in assigned)
                    or held_reservations(self.runtime, activity.get('assigned_execution_ids', []))
                    or any(not isinstance(row, dict) or row.get('action_id') != identifier
                           for row in [*activity.get('unresolved', []), *activity.get('followups', [])])):
                continue
            unresolved = deepcopy(activity.get('unresolved', []))
            if judgment.get('current') is False:
                unresolved.append({'judgment_id': judgment['id'], 'reason': 'sealed judgment is no longer current'})
            finish_activity(self.runtime, activity['id'], result_refs=activity.get('result_refs', []),
                unresolved=unresolved, followups=[*activity.get('followups', []),
                    {'action_id': identifier, 'judgment_id': judgment['id'], 'reason': 'goal audit request superseded'}],
                at=self._lifecycle_now().isoformat())
        return changed

    def _record_goal_audit_followup(self, basis, judgments):
        judgment_ids = sorted(row['id'] for row in judgments)
        for event in self.runtime.get('events', []):
            if (event['kind'] == 'goal_audit_completed' and event.get('basis_sha256') == basis
                    and event.get('judgment_ids') == judgment_ids):
                return event['id']
        return self._lifecycle_event('goal_audit_completed', target=self.instance['id'],
            basis_sha256=basis, judgment_ids=judgment_ids, outcome='not_established', next_owner='research_plan')['id']

    def _apply_governance_goal_audit(self, action, output, execution_id):
        required, slot = action.get('required'), action.get('slot')
        if type(required) is not int or required < 1 or type(slot) is not int or not 0 <= slot < required:
            raise ValueError('goal audit requires a positive count and an in-range integer slot')
        if any(j['basis'] == action['basis'] and j['slot'] == action['slot'] for j in self.instance['goal_judgments']):
            raise ValueError('goal audit slot already sealed')
        if action['basis'] != self._goal_basis_key(): raise ValueError('goal audit inputs changed before acceptance')
        mapped = governance.evaluate_goal_audits(self.instance, self.runtime, execution_id, output.get('additional_audits', []))
        usable = [k for k in self.instance['knowledge'].values() if knowledge.assess_use(k, self.instance)['valid']]
        known = {k['id'] for k in usable} | {t['id'] for t in self.runtime['tasks'].values() if t.get('results')}
        cited = [ref for ref in output['used_sources'] if ref in known]
        dependencies = cited or [k['id'] for k in usable]
        links = [link for identifier in dependencies if identifier in self.instance['knowledge']
                 for link in knowledge_records.usable_links(self.instance, identifier)]
        view = governance.governance_view(self.instance)
        judgment = {**deepcopy(output), 'id': self.ports.clock.new_id('GJ'), 'execution_id': execution_id, 'slot': action['slot'],
            'basis': action['basis'], 'required': action['required'], 'formal_result_refs': sorted({r['formal_result_id'] for r in links}),
            'assessment_refs': sorted({r['assessment_id'] for r in links}), 'dependencies': dependencies,
            'record_basis': knowledge.capture_basis(self.instance, self.runtime, dependencies), 'basis_is_conservative': not bool(cited),
            'goal_revision': view['goal_revision'], 'goal_basis_sha256': governance.mathematical_goal_basis(view['charter']),
            'policy_revision': view['policy_revision'], 'current': True,
            'source_basis': deepcopy(self.runtime['executions'][execution_id].get('source_basis', [])), 'additional_audits': mapped}
        judgments = [j for j in self.instance['goal_judgments'] if j['basis'] == action['basis']] + [judgment]
        if (any(type(j.get('required')) is not int or j['required'] != required
                or type(j.get('slot')) is not int or not 0 <= j['slot'] < required for j in judgments)
                or len({j['slot'] for j in judgments}) != len(judgments)):
            raise ValueError('goal audit group has inconsistent slots or counts')
        self.instance['goal_judgments'].append(judgment)
        if len(judgments) != action['required']: return judgment
        # A satisfied verdict whose cited basis reaches no formal result cannot establish the
        # mathematical goal (academic.apply_goal_assurance); the group then returns as not established.
        satisfied = bool(usable) and all(j['decision'] == 'satisfied' and j['scope_complete'] and j.get('current', True)
            and j['formal_result_refs'] and all(a['decision'] == 'satisfied' for a in j['additional_audits']) for j in judgments)
        if satisfied:
            from .trust_validation import require_active_environment
            require_active_environment(self.instance, self.runtime, current_identity=True, host=self.ports.host)
            self.instance = academic.apply_goal_assurance(self.instance, decision='mathematically_solved',
                basis=action['basis'], judgments=judgments, runtime=self.runtime)
            self.runtime['status'] = 'completed'
            self._settle_goal_completion()
            self._ensure_academic_followup()
            if self.runtime['questions']:
                self.runtime['history'].append({'kind': 'questions_preserved_at_goal_completion', 'questions': self.runtime['questions']})
        else:
            self._record_goal_audit_followup(action['basis'], judgments)
        return judgment
