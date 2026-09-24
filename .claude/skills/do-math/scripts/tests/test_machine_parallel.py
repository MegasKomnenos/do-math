"""Owner-thread machine continuations, scheduler progress, and real Job barriers."""
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace
import os
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math.engine import ResearchEngine
from do_math.parallel import ModelCalls
from do_math.execution_lifecycle import transition_execution
from do_math.repository import new_id
from do_math import knowledge_records
from test_lifecycle_engine import FakeEngine, AdapterDouble
from test_categories import test_group


class Host(FakeEngine):
    _formal = ResearchEngine._formal
    _formal_steps = ResearchEngine._formal_steps
    _machine_started = ResearchEngine._machine_started
    _execution_profile = ResearchEngine._execution_profile
    _provider_status = ResearchEngine._provider_status
    _settle_recovered_execution = ResearchEngine._settle_recovered_execution

    def __init__(self, root):
        self.owner_thread = threading.get_ident()
        super().__init__(root)
        self._calls = None
        self._live_execution_ids = set()
        self.activate()
        from do_math.execution_profiles import build_profiles
        self.instance['config']['lean_command'] = self.instance['trust_environments'][self.instance['active_trust_environment']]['toolchain']['configured_command']
        configured = build_profiles(self.instance['config'])
        self.instance['execution_profiles'].update(configured['execution_profiles'])
        self.instance['role_profile_refs'].update(configured['role_profile_refs'])
        self.ai_finished = threading.Event()
        self.tick = 0.
        self.control_action = lambda: None
        self.identity_reviews = []
        self.runner = SimpleNamespace(run=lambda **args: {'status': 'completed'})

    def storage_double(self):
        self.store = SimpleNamespace(load=lambda: ('fixture-head', deepcopy(self.saves[-1]['instance']), deepcopy(self.saves[-1]['runtime'])))
        self._state_signature = lambda: 'fixture'
        self._transport_bindings = {}

    def _save(self, artifacts=None):
        if threading.get_ident() != self.owner_thread:
            raise AssertionError('engine mutation escaped the owner thread')
        super()._save(artifacts)

    def _controls(self):
        if self._calls is not None:
            self._calls.pump()
        self.control_action()

    def _check_installation(self, **kwargs): return True
    def _available_inputs(self): return []
    def _retry_provider_actions(self): pass
    def _refresh_readiness(self): pass
    def _settle_activity(self, execution_id): pass
    def _start_identity_review(self, kid): self.identity_reviews.append(kid)
    def _remove_action(self, action):
        self.runtime['queue'][:] = [a for a in self.runtime['queue'] if a.get('id') != action.get('id')]

    def _call_steps(self, action):
        # Only the model response is synthetic. Admission, collection and release
        # still use the scheduler's real Git-backed reservation implementation.
        profile = self._execution_profile(action)
        eid = new_id('EX')
        execution = self._register_execution(action, {'id': eid, 'role': action['role'], 'status': 'queued'})
        assert self._provider_slots().acquire(eid, profile['budget_kind'], profile['ai']['model'],
                                             profile=profile, execution=execution)
        transition_execution(execution, 'running', at=self._lifecycle_now().isoformat())
        result = yield {'execution_id': eid}
        assert result['status'] == 'completed', result
        self._end_machine_execution(execution, outcome='execution_incomplete', disposition={'kind': 'synthetic_AI_return'})
        self._remove_action(action)
        self.ai_finished.set()

    def candidate(self, kid):
        self.instance, _ = knowledge_records.create_candidate(self.instance, {
            'id': kid, 'kind': 'lemma', 'statement': 'One equals one', 'summary': 'Reflexivity',
            'lean_code': 'theorem fixture : 1 = 1 := rfl', 'declaration_names': ['fixture'], 'dependencies': []},
            source_ref='UI-source', actor_ref='EX-author')
        return {'id': new_id('AC'), 'role': 'formal_check', 'target': kid}


@test_group('unit')
class MachineSchedulerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.enterContext(patch('do_math.initialization.adapter_for', return_value=AdapterDouble()))
        self.enterContext(patch('do_math.windows_job.named_job_empty', return_value=True))
        self.host = Host(self.temp.name)
        self.enterContext(patch('do_math.scheduler.time.monotonic', side_effect=lambda: self.host.tick))

    def run_case(self, *, trust=False, cancel=False):
        host = self.host
        if trust:
            host.knowledge('K1')
            environment = host.environment('next')
            host.control('trust', {'operation': 'transition', 'env_id': environment})
            action = next(a for a in host.runtime['queue'] if a['role'] == 'trust_check')
            action.setdefault('id', new_id('AC'))
        else:
            action = host.candidate('K1')
        second = host.candidate('K2')
        host.runtime['queue'] = [action, {'id': new_id('AC'), 'role': 'maintenance'}, second]
        observed = []
        def control():
            if host.ai_finished.is_set():
                host.tick = 100000.
                if cancel == 'revoke':
                    for grant in host.instance['grants'].values():
                        grant['status'] = 'revoked'
                elif cancel:
                    host.runtime['status'] = 'paused'
                    host.instance['lifecycle']['state'] = 'paused'
        host.control_action = control
        def verify(**args):
            args['on_started']({'job_name': 'synthetic-formal-job'})
            for _ in range(500):
                stopped = args['should_stop']()
                if host.ai_finished.is_set():
                    observed.append(args['should_stop']())
                    # Return a late success intentionally; currentness must decide.
                    return host.verification(args['source'], args['declarations'], args['expected_toolchain'])
                time.sleep(.01)
            raise AssertionError('AI completion was blocked by the formal verifier')
        host.formal_verifier = verify
        host._run_parallel(max_steps=2)
        self.assertTrue(host.ai_finished.is_set())
        details = {path: raw.decode('utf-8', 'replace') for saved in host.saves for path, raw in saved['artifacts'].items()
                   if path.endswith(('formal.json', 'trust-result.json'))}
        self.assertEqual(observed, [bool(cancel)], str(details) + str(host.runtime.get('waiting_actions')))
        machines = [e for e in host.runtime['executions'].values() if e['role'] in {'formal_check', 'trust_check'}]
        self.assertEqual(len(machines), 1, 'the second Lean request must stay unstarted')
        self.assertEqual(machines[0]['status'], 'ended')
        self.assertEqual(machines[0]['capacity']['local_termination'], 'confirmed')
        model = next(e for e in host.runtime['executions'].values() if e['role'] == 'maintenance')
        self.assertEqual(model['capacity']['local_termination'], 'confirmed')
        if cancel:
            self.assertEqual(machines[0]['outcome'], 'execution_incomplete')
            self.assertEqual(host.identity_reviews, [])
        return host

    def test_formal_allows_ai_collection_after_long_elapsed_time(self):
        self.run_case()

    def test_formal_user_stop_rejects_a_late_verified_result(self):
        self.run_case(cancel=True)

    def test_trust_check_allows_ai_collection_after_long_elapsed_time(self):
        self.run_case(trust=True)

    def test_trust_check_user_stop_rejects_a_late_verified_result(self):
        self.run_case(trust=True, cancel=True)

    def test_revoked_authority_rejects_both_kinds_of_formal_result(self):
        self.run_case(cancel='revoke')

    def test_trust_revoked_authority_rejects_late_result(self):
        self.run_case(trust=True, cancel='revoke')

    @test_group('integration')
    def test_machine_artifacts_publish_to_real_immutable_git_bundles(self):
        import subprocess
        from do_math.git_store import GitStateStore
        for trust in (False, True):
            with self.subTest(trust=trust):
                root = Path(self.temp.name) / str(trust); root.mkdir()
                self.host = Host(root)
                repo = root / 'repo'; repo.mkdir()
                subprocess.run(['git', '-C', str(repo), 'init', '-q'], check=True)
                store = GitStateStore(repo, new_id('RI'))
                head = store.publish(None, {'research/state.json': b'{}', 'runtime/state.json': b'{}'}).head
                save = self.host._save
                def publish(artifacts=None):
                    nonlocal head
                    if artifacts:
                        head = store.publish(head, artifacts).head
                    save(artifacts)
                    # ResearchRepository.save_with_state returns new normalized roots.
                    self.host.instance = deepcopy(self.host.instance)
                    self.host.runtime = deepcopy(self.host.runtime)
                self.host._save = publish
                host = self.run_case(trust=trust)
                machine = next(e for e in host.runtime['executions'].values()
                               if e['role'] in {'formal_check', 'trust_check'})
                self.assertNotEqual(machine['raw_result_ref'].split('/')[2], machine['result_ref'].split('/')[2])
                self.assertIn(b'verified', store.read_bytes(head, machine['raw_result_ref']))
                self.assertIn(b'verified', store.read_bytes(head, machine['result_ref']))
                self.assertEqual(machine['outcome'], 'output_accepted')

    def test_owner_exception_stops_worker_preserves_result_and_reconciles_capacity(self):
        host = self.host
        host.runtime['queue'] = [host.candidate('K1')]
        host.storage_double()
        from types import MethodType
        host._settle_activity = MethodType(ResearchEngine._settle_activity, host)
        def verify(**args):
            args['on_started']({'job_name': 'synthetic-owned-job'})
            while not args['should_stop'](): time.sleep(.01)
            return {'status': 'stopped', 'reason': 'owner stopped', 'stdout': 'preserved evidence'}
        host.formal_verifier = verify
        def control():
            if any(e.get('process') for e in host.runtime['executions'].values()):
                raise RuntimeError('injected owner failure')
        host.control_action = control
        with self.assertRaisesRegex(RuntimeError, 'injected owner failure'):
            host._run_parallel(max_steps=1)
        formal = next(e for e in host.runtime['executions'].values() if e['role'] == 'formal_check')
        self.assertEqual(formal['status'], 'ended')
        self.assertEqual(formal['capacity']['local_termination'], 'confirmed')
        self.assertEqual(host.identity_reviews, [])
        self.assertTrue(any('preserved evidence' in raw.decode() for raw in host.saves[-1]['artifacts'].values()))
        self.assertEqual(host.runtime['waiting_actions'][formal['action']['id']]['kind'], 'execution_failure')
        self.assertFalse(any(a.get('id') == formal['action']['id'] for a in host.runtime['queue']))
        self.assertTrue(any(a['role'] == 'operational_review' and a.get('target') == formal['id'] for a in host.runtime['queue']))
        self.assertEqual(host.runtime['activities'][formal['owner_activity_id']]['status'], 'waiting')

    def test_publication_failure_keeps_local_result_and_durable_unsettled_record(self):
        host = self.host
        host.runtime['queue'] = [host.candidate('K1')]
        host.storage_double()
        host.formal_verifier = lambda **args: {'status': 'failed', 'reason': 'retained compiler evidence'}
        save = host._save
        def fail_result_save(artifacts=None):
            if artifacts: raise OSError('injected result storage failure')
            save(artifacts)
        host._save = fail_result_save
        with self.assertRaisesRegex(OSError, 'result storage failure'):
            host._run_parallel(max_steps=1)
        _, _, durable = host.store.load()
        formal = next(e for e in durable['executions'].values() if e['role'] == 'formal_check')
        self.assertNotEqual(formal['status'], 'ended')
        self.assertNotEqual(formal['capacity']['local_termination'], 'confirmed')
        local = Path(host.instance['workspace']) / 'execution-recovery' / formal['id'] / 'returned-result.json'
        self.assertIn('retained compiler evidence', local.read_text(encoding='utf-8'))


@test_group('resource')
class CallManagerTests(unittest.TestCase):
    @test_group('unit')
    def test_admission_transition_preserves_native_utc_precision(self):
        from datetime import datetime, timezone
        from do_math.execution_lifecycle import create_execution
        from do_math.execution_profiles import build_profiles, profile_ref
        from do_math.session_slots import SessionSlots
        from do_math.engine import DEFAULT_CONFIG
        instant = datetime(2026, 9, 23, 0, 0, 0, 997259, tzinfo=timezone.utc)
        class Clock(datetime):
            @classmethod
            def now(cls, tz=None): return instant
        instance = build_profiles(DEFAULT_CONFIG)
        profile = next(p for p in instance['execution_profiles'].values() if p['role'] == 'formal_check')
        runtime = {'executions': {}, 'reservations': {}}
        execution = create_execution(execution_id='EX-precision', owner_activity_id='AY-precision', actor_kind='machine',
            input_manifest=[], profile_ref=profile_ref(profile), created_at=instant.isoformat())
        execution['role'] = 'formal_check'
        with patch('datetime.datetime', Clock), patch('do_math.session_slots.time.time', return_value=instant.timestamp() - .000001):
            self.assertTrue(SessionSlots(runtime, instance).acquire(execution['id'], profile['budget_kind'], None,
                profile=profile, execution=execution))
        self.assertEqual(execution['transitions'][-1]['at'], instant.isoformat())

    def test_close_answers_pending_stop_queries_and_fails_other_callbacks(self):
        calls = ModelCalls()
        seen = []
        def continuation():
            seen.append((yield))
        one, two = continuation(), continuation()
        next(one); next(two)
        calls.start_call(one, lambda should_stop: {'stopped': should_stop()}, {'should_stop': lambda: False}, execution_id='EX-one')
        calls.start_call(two, lambda on_started: on_started({}), {'on_started': lambda identity: self.fail('must not run')}, execution_id='EX-two')
        until = time.monotonic() + 3
        while calls.events.qsize() < 2 and time.monotonic() < until:
            time.sleep(.01)
        self.assertEqual(calls.events.qsize(), 2)
        calls.close()
        self.assertEqual(calls.collect(), 2)
        self.assertEqual(calls.collect(), 0)
        self.assertIn({'stopped': True}, seen)
        self.assertTrue(any(r.get('status') == 'failed' for r in seen))
        self.assertFalse(any(t.is_alive() for t in calls.threads))

    @unittest.skipUnless(os.name == 'nt', 'Windows Job required')
    def test_failed_start_publication_never_resumes_the_real_job(self):
        from do_math.formal import _job_run
        with tempfile.TemporaryDirectory() as root:
            marker = Path(root) / 'must-not-run'
            def reject(identity):
                self.assertFalse(marker.exists())
                raise OSError('simulated publication failure')
            with self.assertRaisesRegex(OSError, 'publication'):
                _job_run([sys.executable, '-c', f'from pathlib import Path; Path({str(marker)!r}).touch()'],
                         Path(root), on_started=reject)
            self.assertFalse(marker.exists())

    @unittest.skipUnless(os.name == 'nt', 'Windows Job required')
    def test_real_job_cancellation_uses_owner_callbacks_and_collects_once(self):
        from do_math.formal import _job_run
        from do_math.windows_job import named_job_empty
        owner = threading.get_ident()
        calls = ModelCalls()
        started, returned = [], []
        def on_started(identity):
            self.assertEqual(threading.get_ident(), owner)
            started.append(identity)
        def continuation():
            returned.append((yield))
        generator = continuation(); next(generator)
        with tempfile.TemporaryDirectory() as root:
            calls.start_call(generator, _job_run, {'command': [sys.executable, '-c', 'import time; time.sleep(30)'],
                'cwd': Path(root), 'on_started': on_started, 'should_stop': lambda: bool(started)}, execution_id='EX-real')
            until = time.monotonic() + 15
            try:
                while calls.futures and time.monotonic() < until:
                    calls.collect(); time.sleep(.01)
                self.assertFalse(calls.futures)
                self.assertEqual(len(returned), 1)
                self.assertTrue(returned[0][-1])
                self.assertTrue(named_job_empty(started[0]['job_name']))
                self.assertEqual(calls.collect(), 0)
            finally:
                calls.close()


if __name__ == '__main__':
    unittest.main()
