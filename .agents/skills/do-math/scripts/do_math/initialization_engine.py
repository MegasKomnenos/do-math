"""Engine integration for initialization adoption: settings, governance records, CLI probes and the initial interpretation."""
from __future__ import annotations

from copy import deepcopy
import json
from .repository import exact_content_hash, new_id

class InitializationEngineMixin:
    def _initialization_control(self, change, source_ref):
        """Existing decision control adopts settings or refreshes observed CLI evidence."""
        from .initialization import governance_basis, grant_current, adapter_for
        from .execution_profiles import match_profile_ref, capability_evidence
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
                'record_hashes': {r['id']: exact_content_hash(r) for r in records}}
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
            profiles = [match_profile_ref(self.instance['execution_profiles'], ref) for ref in refs]
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
            adoption['config_sha256'] = exact_content_hash(self.instance['config'])
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
            adoption['review_policy_sha256'] = exact_content_hash(policy)
        if 'profile_refs' in change:
            refs = change['profile_refs']
            if not isinstance(refs, list) or not refs:
                raise ValueError('adoption requires exact profile references')
            from .observations import observation_settings_errors
            for ref in refs:
                errors = observation_settings_errors(match_profile_ref(self.instance['execution_profiles'], ref))
                if errors:
                    raise ValueError('observation_configuration: ' + json.dumps(errors, ensure_ascii=False))
            adoption['profile_refs'] = deepcopy(refs)
        if 'initial_profile_ref' in change:
            profile = match_profile_ref(self.instance['execution_profiles'], change['initial_profile_ref'])
            if profile['role'] != 'intent_interpretation':
                raise ValueError('initial profile must permit intent_interpretation')
            from .model_policy import selection
            selection(self.instance['config'], {'role': 'intent_interpretation',
                'profile_ref': change['initial_profile_ref']}, {}, self.instance['knowledge'],
                instance=self.instance)
            adoption['initial_profile_ref'] = deepcopy(change['initial_profile_ref'])
        elif adoption.get('config_sha256') == exact_content_hash(self.instance['config']) and adoption.get('profile_refs'):
            from .model_policy import selection
            chosen = selection(self.instance['config'], {'role': 'intent_interpretation'}, {},
                               self.instance['knowledge'], instance=self.instance)['profile_ref']
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
        input_id = lifecycle['input_id']
        if any(row.get('input_ref') == input_id and not row.get('superseded_by')
               and row.get('application', {}).get('status') == 'awaiting_decision'
               for row in self.runtime.get('intent_imports', {}).values()):
            return
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
            owner_handlers=self._governance_owner_handlers())
        return True
