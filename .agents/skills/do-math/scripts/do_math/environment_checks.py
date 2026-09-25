"""Deferred full-scope publication checks owned by the existing executor."""
from copy import deepcopy
import hashlib
from pathlib import Path

from .repository import canonical_json, exact_content_hash, new_id
from .trust_validation import manifest_errors, verify_environment_files


class ObservationPending(Exception):
    def __init__(self, request_id, *, invalid=False):
        self.request_id, self.invalid = request_id, invalid
        super().__init__('environment observation failed' if invalid else 'environment observation pending')


def environment_key(environment):
    # The separately checked manifest hash covers all its bytes. No large
    # nested payload is serialized again merely to name this observation.
    return exact_content_hash({k:v for k,v in environment.items() if k != 'manifest'})


class EnvironmentChecks:
    def __init__(self, engine):
        self.engine, self.entries = engine, {}
        self.calls = getattr(engine, '_calls', None)

    def observe(self, environment, operation):
        errors = manifest_errors(environment)
        if errors:
            raise ValueError('; '.join(errors))
        key = exact_content_hash({'operation':operation,'environment':environment_key(environment)})
        calls = getattr(self.engine, '_calls', None)
        if (calls is None or calls.stopping or operation == 'preview' or self.engine.runtime.get('maintenance_fence')
                or self.engine.runtime.get('status') in {'paused','closed'}):
            raise ObservationPending(key)
        if self.calls is not calls:
            if self.calls is not None and self.calls.futures:
                raise ValueError('environment executor changed before drain')
            self.entries.clear()
            self.calls = calls
        attempt = getattr(self.engine, '_environment_attempt', None)
        previous = self.entries.get(key)
        if previous and ((previous.get('result') or {}).get('status') == 'cancelled'
                or previous.get('consumed_attempt') is not None and previous['consumed_attempt'] != attempt):
            # A failed/stale publication is another admission boundary. Do not
            # turn a completed observation into an indefinite live-file cache.
            self.entries.pop(key)
        if key not in self.entries:
            fixed = deepcopy(environment)
            path = 'runtime/artifacts/' + new_id('BA') + '/environment-observation.json'
            entry = self.entries[key] = {'operation':operation, 'result':None, 'artifact_ref':path,
                                        'environment_key':environment_key(fixed), 'environment_id':fixed.get('id')}
            def continuation():
                result = yield
                entry['result'] = result
                raw = canonical_json({'operation':operation, 'environment_key':environment_key(fixed), 'observation':result})
                entry['evidence'] = {'artifact_ref':path, 'sha256':hashlib.sha256(raw).hexdigest(),
                                     'environment_key':environment_key(fixed)}
                for waiting in self.engine.runtime.get('waiting_actions', {}).values():
                    if waiting.get('environment_request') == key:
                        waiting['reason'] = 'environment observed' if result.get('status') == 'verified' else 'environment observation requires recheck'
                        waiting['next_owner'] = 'engine' if result.get('status') == 'verified' else 'trust_governance'
                self.engine._save({path:raw})
            generator = continuation()
            next(generator)
            def stop():
                current = self.engine.instance.get('trust_environments', {}).get(self.engine.instance.get('active_trust_environment'))
                return (self.engine._calls.stopping or self.engine.runtime.get('status') in {'paused','closed'}
                        or bool(self.engine.runtime.get('maintenance_fence'))
                        or current is None or environment_key(current) != entry['environment_key'])
            self.engine._calls.start_call(generator, verify_environment_files,
                {'environment':fixed, 'should_stop':stop})
        entry = self.entries[key]
        if entry['result'] is None:
            raise ObservationPending(key)
        if entry['result'].get('status') != 'verified':
            raise ObservationPending(key, invalid=True)
        # The normal integration path still validates the complete current
        # action, grants, sources, review scope and candidate before publication.
        execution = self.engine.runtime.get('executions', {}).get(operation)
        entry['consumed_attempt'] = attempt
        if execution is not None:
            refs = execution.setdefault('environment_observations', [])
            if entry['evidence'] not in refs:
                refs.append(deepcopy(entry['evidence']))
        return entry['result']

    def ready(self, request_id):
        calls = getattr(self.engine, '_calls', None)
        if calls is None or calls.stopping:
            return False
        if self.calls is not calls:
            return True
        if request_id not in self.entries:
            return True
        entry = self.entries[request_id]
        if entry['result'] is None:
            return False
        if entry['result'].get('status') in {'verified','cancelled'}:
            return True
        env = self.engine.instance.get('trust_environments', {}).get(self.engine.instance.get('active_trust_environment'))
        return env is None or environment_key(env) != entry['environment_key']

    def discard(self, operation):
        self.entries = {k:v for k,v in self.entries.items() if v['operation'] != operation or v['result'] is None}


def verify_formal(*, environment, verifier, **arguments):
    before = verify_environment_files(environment, should_stop=arguments.get('should_stop'))
    if before['status'] != 'verified':
        return {'status':'stopped' if before['status'] == 'cancelled' else 'failed',
                'reason':'environment admission failed: ' + '; '.join(before.get('errors', [])),
                'error_kind':'trust_environment', 'environment_observations':[before], 'launch_not_created':True}
    result = verifier(**arguments)
    result['environment_observations'] = [before]
    if result.get('status') == 'verified':
        after = verify_environment_files(environment, should_stop=arguments.get('should_stop'))
        result['environment_observations'].append(after)
        if after['status'] != 'verified':
            return {**result, 'status':'stopped' if after['status'] == 'cancelled' else 'failed',
                    'error_kind':'trust_environment',
                    'reason':'environment after verification: ' + '; '.join(after.get('errors', []))}
    return result
