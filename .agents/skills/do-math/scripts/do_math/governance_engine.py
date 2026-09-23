"""Central governance transitions; ENGINE owns one public Git publication.

The hooks stage ordinary controls and model results on the same roots as the
other engine mixins. They never publish a second control receipt or call save.
"""
from copy import deepcopy
from pathlib import Path

from . import governance, academic, knowledge, knowledge_records, execution_profiles
from .repository import new_id, canonical_json


def bind_host_configuration(instance, config, *, origin):
    """Resolve the explicit request-source alias to the preserved user input."""
    import hashlib
    config = deepcopy(config)
    host = config.get('host_resources')
    if host is None or 'configuration:request' not in host['constraint']['authority_refs']:
        return config
    if origin != 'user':
        raise ValueError('host configuration request requires user authority')
    raw = canonical_json({'host_resources': host})
    identifier = 'GS-host-' + hashlib.sha256(raw).hexdigest()
    source = governance.preserve_source(identifier, raw.decode('utf-8'), origin='user')
    sources = instance.setdefault('governance_sources', {})
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
        from .engine import validate_config, DEFAULT_CONFIG
        from .scholarly import resolve_scholarly_server
        from .session_slots import SessionSlots
        patch = request.get('config', {})
        if not isinstance(patch, dict): raise ValueError('configuration patch must be an object')
        if request.get('origin', 'user') not in {'user', 'operator'}: raise ValueError('unknown configuration authority')
        current = {**deepcopy(DEFAULT_CONFIG), 'session_limits': None, **instance['config']}
        candidate = {**current, **patch}
        validate_config(candidate)
        result, state = deepcopy(instance), deepcopy(runtime)
        candidate = bind_host_configuration(result, candidate, origin=request.get('origin', 'user'))
        if candidate.get('session_limits') is not None:
            if {'model', 'operator_model'} & patch.keys(): raise ValueError('session mode selects models with tier_models; model is a legacy option')
            if {'work_calls', 'operations_calls'} & patch.keys(): raise ValueError('session mode uses session_limits; explicitly set session_limits=null to configure legacy call budgets')
        changes_mode = (candidate.get('session_limits') is None) != (current.get('session_limits') is None)
        if changes_mode and (getattr(self, '_executor_running', False) or getattr(self, '_calls', None) is not None
                             or getattr(self, '_live_execution_ids', set())):
            raise ValueError('budget mode conversion requires a stopped executor')
        protected = ('work_calls', 'operations_calls', 'session_limits', 'tier_models', 'role_tiers', 'model',
                     'role_models', 'operator_model', 'claude_only_assigned_model', 'host_resources')
        if request.get('origin', 'user') == 'operator' and any(candidate.get(k) != current.get(k) for k in protected):
            raise ValueError('resource settings require a user decision at application time')
        host_changed = candidate.get('host_resources') != current.get('host_resources')
        if host_changed and (getattr(self, '_executor_running', False) or getattr(self, '_calls', None) is not None
                or getattr(self, '_live_execution_ids', set())
                or any(row['status'] != 'ended' for row in runtime.get('executions', {}).values())
                or any(row.get('state') == 'held' for row in runtime.get('reservations', {}).values())):
            raise ValueError('host resource changes require a stopped executor with no live execution or held reservation')
        validate_config(candidate)
        if candidate['scholarly_enabled']:
            candidate['scholarly_server'] = resolve_scholarly_server(candidate['scholarly_server'], start=Path.cwd())
        editions = execution_profiles.build_profiles(candidate)
        result['config'] = candidate
        result.setdefault('execution_profiles', {}).update(editions['execution_profiles'])
        result.setdefault('capacity_constraints', {}).update(editions['capacity_constraints'])
        result['role_profile_refs'] = editions['role_profile_refs']
        if editions.get('host_capacity_ref'):
            result['host_capacity_ref'] = editions['host_capacity_ref']
        else:
            result.pop('host_capacity_ref', None)
        if candidate.get('session_limits') is not None:
            # A detached ledger view stages the same configure transition. Do
            # not mutate self._slots' live roots before the common Git CAS.
            slots = SessionSlots(Path(result['workspace']), result['id'], runtime=state, instance=result)
            try: slots.configure(candidate['session_limits'])
            finally: slots.close()
            live = {e.get('action', {}).get('id') for e in state['executions'].values() if e['status'] != 'ended'}
            waiting = [row['action'] for row in state.get('waiting_actions', {}).values()]
            for pending in [*state['queue'], *waiting]:
                if pending.get('id') not in live: pending.pop('model_selection', None)
        if host_changed:
            from . import revisions
            waiting = [row['action'] for row in state.get('waiting_actions', {}).values()]
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
                original = execution_profiles.resolve_profile(result['execution_profiles'], pending['profile_ref'])
                replacements = [profile for profile in editions['execution_profiles'].values()
                                if without_host(profile) == without_host(original)]
                if len(replacements) == 1:
                    pending['profile_ref'] = execution_profiles.profile_ref(replacements[0])
                    if pending.get('model_selection'):
                        pending['model_selection']['profile_ref'] = deepcopy(pending['profile_ref'])
            affected = []
            for tid, task in state.get('tasks', {}).items():
                if task.get('status') in {'completed', 'closed'}:
                    continue
                profiles = [execution_profiles.resolve_profile(result['execution_profiles'], ref)
                            for ref in task.get('profile_refs', [])]
                if any(profile.get('host_capacity_refs', []) != ([result['host_capacity_ref']]
                        if result.get('host_capacity_ref') else []) for profile in profiles):
                    affected.append(tid)
            if affected:
                state['queue'].insert(0, {'id': new_id('AC'), 'role': 'research_preparation',
                    'reason': 'Reprepare task profile contracts for the newly adopted host resources',
                    'revision_targets': revisions.capture_targets(result, state, affected)})
        if state.get('status') in {'budget_exhausted', 'capacity_waiting'}: state['status'] = 'ready'
        return result, state

    def _governance_owner_handlers(self):
        handlers = governance.import_owner_handlers()
        def configure(instance, runtime, unit, approval):
            return self._configure_candidate(instance, runtime, {'action': 'configure',
                'origin': approval['actor'], 'config': unit['payload']['config']})
        governance.register_configuration_owner(handlers, apply=configure)
        return handlers

    def _governance_input_source(self, input_id):
        return governance.import_input_source(self.instance, self.runtime, input_id)

    def _governance_context(self, action, context):
        context = deepcopy(context)
        if action['role'] == 'goal_audit':
            context['additional_audit_input'] = governance.additional_audit_input(self.instance, self.runtime)
        elif action['role'] == 'intent_interpretation' and not action.get('delegation_application_id'):
            request = next(row for row in self.runtime['inputs'] if row['id'] == action['target'])
            source = self._governance_input_source(action['target'])
            context['user_request'] = {**deepcopy(request), 'text': source['text'], 'sha256': source['sha256']}
            context['original_source'] = source
            context['import_consumers'] = governance.import_consumer_catalog(self._governance_owner_handlers())
            context['governance_records'] = deepcopy(list(self.instance.get('governance', {}).values()))
            context['delegations'] = deepcopy(list(self.instance.get('delegations', {}).values()))
            context['config'] = deepcopy(self.instance.get('config', {}))
            context['source_coordinate_unit'] = 'unicode_codepoint'
            context['interpretation_stage'] = action.get('stage', 'interpret')
            context['interpretation_to_check'] = deepcopy(self.runtime.get('intent_imports', {}).get(action.get('import_id')))
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

    def _queue_intent_rework(self, bundle, reason):
        author = self.runtime.get('executions', {}).get(bundle['execution_id'], {}).get('action', {})
        fields = {key: deepcopy(author[key]) for key in ('initialization', 'grant_id', 'profile_ref', 'owner_activity_id') if key in author}
        input_id = bundle.get('input_ref', bundle['source']['id'])
        current_source = self._governance_input_source(input_id) if any(
            row['id'] == input_id for row in self.runtime.get('inputs', [])) else bundle['source']
        if current_source == bundle['source']:
            fields['previous_import_id'] = bundle['id']
        fields['intent_repair'] = {'import_id': bundle['id'], 'previous_sha256': bundle['sha256'],
            'check_execution_id': bundle.get('check', {}).get('execution_id'), 'findings': [reason]}
        self._enqueue('intent_interpretation', input_id, stage='interpret',
                      reason=reason, lineage_id=author.get('lineage_id', bundle['execution_id']), **fields)

    def _after_governance_import(self, import_id):
        bundle = self.runtime['intent_imports'][import_id]
        if bundle.get('application', {}).get('status') != 'applied': return
        assigned = {e.get('action', {}).get('id') for e in self.runtime.get('executions', {}).values()
                    if e.get('status') != 'ended'}
        obsolete = [a for a in self.runtime.get('queue', []) if a.get('id') not in assigned
                    and a.get('role') == 'intent_interpretation'
                    and import_id in (a.get('import_id'), a.get('previous_import_id'))]
        for action in obsolete:
            self.runtime['queue'].remove(action)
            self.runtime.setdefault('history', []).append({'kind': 'applied_import_supersedes_pending_interpretation',
                'import_id': import_id, 'action': deepcopy(action)})
        input_id = bundle.get('input_ref', bundle['source']['id'])
        if self.instance.get('lifecycle', {}).get('input_id') == input_id:
            self._complete_initial_intent(input_id)
            self._activate_initialization()
        elif self.instance.get('lifecycle', {}).get('state') != 'initializing':
            self._enqueue('research_preparation', reason='checked user information', import_id=import_id)
        self._resume_import_question_waits()

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
            del self.runtime['waiting_actions'][aid]
            if not bundle.get('superseded_by'):
                self._queue_intent_rework(bundle, 'Apply the resolved user answers to the preserved original: ' +
                    ', '.join(sorted({row['resolution_ref'] for row in questions if row.get('resolution_ref')})))

    def _governance_control(self, request):
        if request['action'] == 'configure':
            self.instance, self.runtime = self._configure_candidate(self.instance, self.runtime, request)
            return True
        spec = request.get('config', {})
        change = spec.get('change', spec)
        if request['action'] != 'decision' or change.get('kind') != 'import_approval': return False
        normalized = {**request, 'config': change}
        bundle = self.runtime.get('intent_imports', {}).get(change.get('import_id'))
        was_applied = bool(bundle and bundle.get('application', {}).get('status') == 'applied')
        before_instance, before_runtime = deepcopy(self.instance), deepcopy(self.runtime)
        try:
            input_id = (bundle.get('input_ref', bundle['source']['id']) if bundle else None)
            if bundle and any(row['id'] == input_id for row in self.runtime.get('inputs', [])):
                if self._governance_input_source(input_id) != bundle['source']:
                    raise ValueError('original source changed before later approval')
            self.instance, self.runtime, _ = governance.apply_import_control(self.instance, self.runtime,
                normalized, owner_handlers=self._governance_owner_handlers())
            if not was_applied: self._after_governance_import(change['import_id'])
        except (ValueError, KeyError, TypeError) as error:
            self.instance, self.runtime = before_instance, before_runtime
            self._reject_governance_import(request, str(error))
            raise
        return True

    def _reject_governance_import(self, request, reason):
        """Stage reauthor routing before ENGINE records its one rejection result."""
        spec = request.get('config', {})
        change = spec.get('change', spec)
        if request.get('action') == 'decision' and change.get('kind') == 'import_approval':
            bundle = self.runtime.get('intent_imports', {}).get(change.get('import_id'))
            if bundle and not bundle.get('superseded_by') and bundle.get('application', {}).get('status') != 'applied':
                self._queue_intent_rework(bundle, reason)

    def _apply_governance_intent(self, action, output, execution_id):
        target = action['target']
        source = self._governance_input_source(target)
        handlers = self._governance_owner_handlers()
        if action.get('stage', 'interpret') == 'interpret':
            bundle = governance.prepare_import(self.instance, self.runtime, source, output, execution_id=execution_id,
                previous_id=action.get('previous_import_id'), owner_handlers=handlers, input_ref=target)
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
                                         execution_id=execution_id, owner_handlers=handlers)
        if bundle['status'] != 'approved':
            self._queue_intent_rework(bundle, '; '.join(bundle['check']['findings']) or 'independent check is unresolved')
            return bundle
        request = next(row for row in self.runtime['inputs'] if row['id'] == target)
        approvals = request.get('config', {}).get('import_approvals', {})
        required = {u['unit_id'] for u in bundle['output']['import_units'] if u['payload']}
        if not any(q['blocks'] for q in bundle['output'].get('question_details', [])) and required - approvals.keys():
            self.runtime.setdefault('waiting_actions', {})[action.get('id', bundle['id'])] = {
                'action': deepcopy(action), 'kind': 'import_application_authority', 'import_id': bundle['id'],
                'reason': 'checked interpretation lacks exact change approval', 'next_owner': 'user'}
            return bundle
        self.instance, self.runtime, receipt = governance.apply_import(self.instance, self.runtime, bundle['id'],
            approvals=approvals, owner_handlers=handlers)
        if receipt['status'] == 'awaiting_decision':
            self.runtime.setdefault('waiting_actions', {})[action.get('id', bundle['id'])] = {
                'action': deepcopy(action), 'kind': 'import_user_decision', 'import_id': bundle['id'],
                'reason': 'Checked interpretation awaits its blocking user answers', 'next_owner': 'user'}
        self._after_governance_import(bundle['id'])
        return receipt

    def _apply_governance_goal_audit(self, action, output, execution_id):
        if any(j['basis'] == action['basis'] and j['slot'] == action['slot'] for j in self.instance['goal_judgments']):
            raise ValueError('goal audit slot already sealed')
        if action['basis'] != self._goal_basis_key(): raise ValueError('goal audit inputs changed before acceptance')
        if governance.governance_view(self.instance)['goal_kind'] != 'mathematical':
            raise ValueError('nonformal tasks do not establish a nonformal final goal guarantee')
        mapped = governance.evaluate_goal_audits(self.instance, self.runtime, execution_id, output.get('additional_audits', []))
        usable = [k for k in self.instance['knowledge'].values() if knowledge.assess_use(k, self.instance)['valid']]
        known = {k['id'] for k in usable} | {t['id'] for t in self.runtime['tasks'].values() if t.get('results')}
        cited = [ref for ref in output['used_sources'] if ref in known]
        dependencies = cited or [k['id'] for k in usable]
        links = [link for identifier in dependencies if identifier in self.instance['knowledge']
                 for link in knowledge_records.usable_links(self.instance, identifier)]
        view = governance.governance_view(self.instance)
        judgment = {**deepcopy(output), 'id': new_id('GJ'), 'execution_id': execution_id, 'slot': action['slot'],
            'basis': action['basis'], 'required': action['required'], 'formal_result_refs': sorted({r['formal_result_id'] for r in links}),
            'assessment_refs': sorted({r['assessment_id'] for r in links}), 'dependencies': dependencies,
            'record_basis': knowledge.capture_basis(self.instance, self.runtime, dependencies), 'basis_is_conservative': not bool(cited),
            'goal_revision': view.get('goal_revision', 1), 'policy_revision': view.get('policy_revision', 1), 'current': True,
            'source_basis': deepcopy(self.runtime['executions'][execution_id].get('source_basis', [])), 'additional_audits': mapped}
        self.instance['goal_judgments'].append(judgment)
        judgments = [j for j in self.instance['goal_judgments'] if j['basis'] == action['basis']]
        if len(judgments) != action['required']: return judgment
        satisfied = bool(usable) and all(j['decision'] == 'satisfied' and j['scope_complete'] and j.get('current', True)
            and all(a['decision'] == 'satisfied' for a in j['additional_audits']) for j in judgments)
        if satisfied:
            from .initialization import require_trust_environment
            require_trust_environment(self.instance, self.runtime)
            self.instance = academic.apply_goal_assurance(self.instance, decision='mathematically_solved',
                basis=action['basis'], judgments=judgments, runtime=self.runtime)
            self.runtime['status'] = 'completed'; self.runtime['queue'] = []
            self._ensure_academic_followup()
            if self.runtime['questions']:
                self.runtime['history'].append({'kind': 'questions_preserved_at_goal_completion', 'questions': self.runtime['questions']})
        return judgment
