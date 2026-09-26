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
from unittest.mock import create_autospec, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math.engine import ResearchEngine
from do_math.parallel import ModelCalls
from do_math.execution_lifecycle import transition_execution
from do_math.repository import ResearchRepository, new_id
from do_math import knowledge_records
from test_lifecycle_engine import FakeEngine
from research_fixtures import FixtureAdapter, await_stop
from state_fixtures import owner_calls
from test_categories import test_group


class Host(FakeEngine):
    _execution_profile = ResearchEngine._execution_profile

    def __init__(self, root):
        self.owner_thread = threading.get_ident()
        super().__init__(root)
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
        self.store = create_autospec(ResearchRepository, instance=True)
        self.store.load.side_effect = lambda snapshot=None: (
            'fixture-head', deepcopy(self.saves[-1]['instance']), deepcopy(self.saves[-1]['runtime']))

    def _save(self, artifacts=None):
        if threading.get_ident() != self.owner_thread:
            raise AssertionError('engine mutation escaped the owner thread')
        super()._save(artifacts)
        self._evaluate_stops()  # The real publication point judges stops after every save.

    def _controls(self, *, pump=True):
        if pump and self._calls is not None:
            self._calls.pump()
        self.control_action()

    def _check_installation(self, **kwargs): return True
    def _refresh_readiness(self): pass
    def _settle_activity(self, execution_id): pass
    def _start_identity_review(self, kid): self.identity_reviews.append(kid)

    def _call_steps(self, action):
        # Only the model response is synthetic. Admission, collection and release
        # still use the scheduler's real Git-backed reservation implementation.
        profile = self._execution_profile(action)
        eid = new_id('EX')
        execution = self._register_execution(action, {'id': eid, 'role': action['role'], 'status': 'queued'})
        assert self._session_slots().acquire(eid, profile=profile, execution=execution)
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
        self.enterContext(patch('do_math.initialization.adapter_for', return_value=FixtureAdapter()))
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
        verifier_entered, applied = threading.Event(), threading.Event()
        def control():
            if host.ai_finished.is_set() and verifier_entered.is_set() and not applied.is_set():
                host.tick = 100000.
                if cancel == 'revoke':
                    for grant in host.instance['grants'].values():
                        grant['status'] = 'revoked'
                elif cancel:
                    host.runtime['status'] = 'paused'
                    host.instance['lifecycle']['state'] = 'paused'
                host._save()  # A control is effective once published.
                applied.set()
        host.control_action = control
        def verify(**args):
            verifier_entered.set()
            args['on_started']({'job_name': args['launch_ticket']['job_name']})
            for _ in range(500):
                stopped = args['should_stop']()
                if host.ai_finished.is_set():
                    self.assertTrue(applied.wait(5), 'the owner loop did not apply the control')
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

    def test_environment_failure_waits_for_rerecord_before_compiler_retry(self):
        import os
        import setup_lean
        from research_fixtures import fixture_setup_lean
        host = self.host
        action = host.candidate('K-env')
        host.runtime['queue'] = [action]
        environment = host.instance['trust_environments'][host.instance['active_trust_environment']]
        bound = deepcopy(host.runtime['trust_bindings'][environment['id']])
        olean = Path(environment['toolchain']['executable']).parents[1] / 'lib/lean/Init/Prelude.olean'
        info = os.stat(olean)
        os.utime(olean, ns=(info.st_atime_ns, info.st_mtime_ns + 10**9))  # e.g. a cache re-download
        from unittest.mock import Mock
        host.formal_verifier = Mock()
        with owner_calls(host):
            host._formal(action)
        host.formal_verifier.assert_not_called()
        waiting = host.runtime['waiting_actions'][action['id']]
        self.assertEqual(waiting['kind'], 'formal_environment')
        self.assertEqual(waiting['next_owner'], 'trust_governance')
        previous = waiting['execution_id']
        host._resume_environment_waits()
        self.assertIn(action['id'], host.runtime['waiting_actions'])
        record_path = Path(environment['toolchain_record']['path'])
        with fixture_setup_lean(environment['toolchain'], record_path.parent / 'smoke.lean'):
            recorded =setup_lean.rerecord(['unused'], record_path.parent, record_path.parent / 'evidence', None)
        host._resume_environment_waits()
        successor = next(a for a in host.runtime['queue'] if a['id']==action['id'])
        self.assertEqual(successor['continuation_of'], previous)
        self.assertNotIn(action['id'], host.runtime['waiting_actions'])
        def verify(**args):
            args['on_started']({'job_name':args['launch_ticket']['job_name']})
            return host.verification(args['source'], args['declarations'], args['expected_toolchain'])
        host.formal_verifier = verify
        with owner_calls(host):
            host._formal(successor)
        latest = next(e for e in host.runtime['executions'].values() if e.get('continuation_of')==previous)
        self.assertEqual(latest['outcome'], 'output_accepted')
        self.assertEqual(host.runtime['trust_bindings'][environment['id']], recorded['binding'])
        rebound = [row for row in host.runtime['events'] if row['kind'] == 'trust_environment_rebound']
        self.assertEqual([(row['previous'], row['current']) for row in rebound], [(bound, recorded['binding'])])

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
                self.host._save = create_autospec(self.host._save, side_effect=publish)
                host = self.run_case(trust=trust)
                machine = next(e for e in host.runtime['executions'].values()
                               if e['role'] in {'formal_check', 'trust_check'})
                self.assertNotEqual(machine['raw_result_ref'].split('/')[2], machine['result_ref'].split('/')[2])
                self.assertIn(b'verified', store.read_bytes(head, machine['raw_result_ref']))
                self.assertIn(b'verified', store.read_bytes(head, machine['result_ref']))
                self.assertEqual(machine['outcome'], 'output_accepted')

    def test_stop_request_reaches_the_calculation_within_one_owner_pass(self):
        host = self.host
        host.runtime['queue'] = [host.candidate('K1')]
        passes, seen, flag = [0], {}, {}
        started = threading.Event()
        def control():
            passes[0] += 1
            if started.is_set() and 'applied' not in seen:
                host.runtime['status'] = 'paused'
                host.instance['lifecycle']['state'] = 'paused'
                host._save()  # The pause control's publication.
                seen['applied'] = passes[0]
                seen['flag_after_publication'] = flag['read']()
        host.control_action = control
        def verify(**args):
            args['on_started']({'job_name': args['launch_ticket']['job_name']})
            flag['read'] = args['should_stop']
            started.set()
            if not await_stop(args['should_stop'], timeout=30):
                raise AssertionError('the stop never reached the calculation')
            seen['observed'] = passes[0]
            return {'status': 'stopped', 'reason': 'flag observed'}
        host.formal_verifier = verify
        host._run_parallel(max_steps=1)
        self.assertTrue(seen['flag_after_publication'], 'the publication itself sets the flag')
        self.assertLessEqual(seen['observed'] - seen['applied'], 1, 'the calculation stops within one owner pass')
        formal = next(e for e in host.runtime['executions'].values() if e['role'] == 'formal_check')
        self.assertEqual(formal['result_disposition']['stop_reasons'], ['instance_paused'])

    def test_owner_exception_stops_worker_preserves_result_and_reconciles_capacity(self):
        host = self.host
        host.runtime['queue'] = [host.candidate('K1')]
        host.storage_double()
        from types import MethodType
        host._settle_activity = MethodType(ResearchEngine._settle_activity, host)
        def verify(**args):
            args['on_started']({'job_name': args['launch_ticket']['job_name']})
            await_stop(args['should_stop'])
            return {'status': 'stopped', 'reason': 'owner stopped',
                    'stdout': b'preserved evidence\xff', 'usage': {'cost_usd': 0.25}}
        host.formal_verifier = verify
        def control():
            if any(e.get('capacity', {}).get('process') for e in host.runtime['executions'].values()):
                raise RuntimeError('injected owner failure')
        host.control_action = control
        with self.assertRaisesRegex(RuntimeError, 'injected owner failure'):
            host._run_parallel(max_steps=1)
        formal = next(e for e in host.runtime['executions'].values() if e['role'] == 'formal_check')
        self.assertEqual(formal['status'], 'ended')
        self.assertEqual(formal['capacity']['local_termination'], 'confirmed')
        self.assertEqual(host.identity_reviews, [])
        import base64
        import json
        preserved = json.loads(host.saves[-1]['artifacts'][formal['result_ref']])
        self.assertEqual(base64.b64decode(preserved['stdout']['base64']), b'preserved evidence\xff')
        self.assertEqual(preserved['usage']['cost_usd'], {'reported_decimal': '0.25'})
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
        host._save = create_autospec(host._save, side_effect=fail_result_save)
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
    def test_collection_releases_finished_threads_but_retains_a_live_call(self):
        calls = ModelCalls()
        release = threading.Event()
        returned = []

        def continuation():
            returned.append((yield))

        def wait_for_release():
            release.wait()
            return "released"

        live = continuation()
        next(live)
        calls.start_call(live, wait_for_release, {}, execution_id="EX-live")
        live_thread = calls.threads[-1]
        try:
            for index in range(16):
                generator = continuation()
                next(generator)
                future = calls.start_call(generator, lambda value: value,
                    {"value": index}, execution_id="EX-finished-" + str(index))
                thread = calls.threads[-1]
                self.assertEqual(future.result(timeout=5), index)
                thread.join(timeout=5)
                self.assertFalse(thread.is_alive())
                self.assertEqual(calls.collect(), 1)
                self.assertEqual(calls.threads, [live_thread])
                self.assertEqual(len(calls.futures), 1)
            self.assertEqual(returned, list(range(16)))
        finally:
            release.set()
            calls.close()
        self.assertEqual(calls.collect(), 1)
        self.assertEqual(calls.collect(), 0)
        self.assertEqual(returned, [*range(16), "released"])
        self.assertEqual(calls.threads, [])
        self.assertEqual(calls.futures, {})

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
            self.assertTrue(SessionSlots(runtime, instance).acquire(execution['id'], profile=profile, execution=execution))
        self.assertEqual(execution['transitions'][-1]['at'], instant.isoformat())

    def test_close_sets_every_stop_flag_and_fails_pending_start_callbacks(self):
        calls = ModelCalls()
        seen = []
        def continuation():
            seen.append((yield))
        one, two = continuation(), continuation()
        next(one); next(two)
        def wait_for_flag(should_stop):
            while not should_stop():
                time.sleep(.01)
            return {'stopped': True}
        calls.start_call(one, wait_for_flag, {'should_stop': lambda: False}, execution_id='EX-one')
        calls.start_call(two, lambda on_started: on_started({}), {'on_started': lambda identity: self.fail('must not run')}, execution_id='EX-two')
        until = time.monotonic() + 3
        while calls.events.qsize() < 1 and time.monotonic() < until:
            time.sleep(.01)
        self.assertEqual(calls.events.qsize(), 1, 'only the start callback waits for the owner')
        calls.close()
        self.assertEqual(calls.collect(), 2)
        self.assertEqual(calls.collect(), 0)
        self.assertIn({'stopped': True}, seen)
        self.assertTrue(any(r.get('status') == 'failed' for r in seen))
        self.assertFalse(any(t.is_alive() for t in calls.threads))

    @test_group('unit')
    def test_owner_wait_wakes_on_a_returned_call_not_its_bound(self):
        calls = ModelCalls()
        def continuation():
            yield
        generator = continuation(); next(generator)
        release = threading.Event()
        calls.start_call(generator, lambda: release.wait(5), {}, execution_id='EX-wake')
        calls.wait(0); release.set()
        started = time.monotonic()
        calls.wait(30)
        self.assertLess(time.monotonic() - started, 5, 'a returned call wakes the owner')
        calls.collect()
        started = time.monotonic()
        calls.wait(.2)
        self.assertGreaterEqual(time.monotonic() - started, .15, 'nothing pending: the bound paces the owner')
        calls.close()

    @test_group('unit')
    def test_stop_flag_reads_never_wait_for_the_owner(self):
        calls = ModelCalls()
        judged = []
        def continuation():
            judged.append((yield))
        generator = continuation(); next(generator)
        def poll(should_stop):
            started = time.monotonic()
            for _ in range(1000):
                should_stop()
            return {'stopped': should_stop(), 'seconds': time.monotonic() - started}
        # The owner never pumps while the calculation polls its flag.
        future = calls.start_call(generator, poll, {'should_stop': lambda: judged.append('judged') or False},
                                  execution_id='EX-poll')
        result = future.result(timeout=5)
        self.assertFalse(result['stopped'])
        self.assertLess(result['seconds'], 1)
        self.assertEqual(judged, ['judged'], 'the judgment runs on the owner, once at start')
        calls.close()

    @test_group('unit')
    def test_owner_judgment_sets_the_flag_once_and_stops_the_calculation(self):
        calls = ModelCalls()
        owner = threading.get_ident()
        reasons, returned, judgments = [], [], []
        def judge():
            self.assertEqual(threading.get_ident(), owner)
            judgments.append(bool(reasons))
            return bool(reasons)
        def continuation():
            returned.append((yield))
        generator = continuation(); next(generator)
        def wait_for_flag(should_stop):
            while not should_stop():
                time.sleep(.01)
            return {'status': 'stopped'}
        future = calls.start_call(generator, wait_for_flag, {'should_stop': judge}, execution_id='EX-judged')
        calls.judge()
        self.assertFalse(future.stop.is_set())
        reasons.append('paused')  # A published stop reason.
        calls.judge()
        calls.judge()  # A set flag is not judged again.
        until = time.monotonic() + 5
        while calls.futures and time.monotonic() < until:
            calls.collect(); time.sleep(.01)
        self.assertEqual(returned, [{'status': 'stopped'}])
        self.assertEqual(judgments, [False, False, True])
        calls.close()

    @test_group('unit')
    def test_failed_judgment_fails_only_its_own_call(self):
        calls = ModelCalls()
        returned = []
        def continuation():
            returned.append((yield))
        generator = continuation(); next(generator)
        def wait_for_flag(should_stop):
            while not should_stop():
                time.sleep(.01)
            return {'status': 'stopped', 'evidence': 'kept'}
        state = {'fail': False}
        def judge():
            if state['fail']:
                raise KeyError('missing record')
            return False
        calls.start_call(generator, wait_for_flag, {'should_stop': judge}, execution_id='EX-broken')
        state['fail'] = True
        calls.judge()  # The owner does not raise.
        until = time.monotonic() + 5
        while calls.futures and time.monotonic() < until:
            calls.collect(); time.sleep(.01)
        self.assertEqual(returned[0]['status'], 'failed')
        self.assertEqual(returned[0]['evidence'], 'kept')
        self.assertIn('stop judgment failed: KeyError', returned[0]['error'])
        calls.close()

    @test_group('unit')
    def test_observations_queue_without_waiting_and_apply_before_collection(self):
        failures, applied, order = [], [], []
        calls = ModelCalls(on_observation_error=lambda eid, error: failures.append((eid, str(error))))
        def continuation():
            order.append(('collected', (yield)))
        def observe(item):
            if item == 'bad':
                raise ValueError('unapplied observation')
            applied.append(item)
            order.append(('applied', item))
        generator = continuation(); next(generator)
        def produce(on_observation, should_stop):
            for item in ('one', 'two'):
                on_observation(item)  # Returns without an owner round trip.
            return {'status': 'completed'}
        future = calls.start_call(generator, produce, {'on_observation': observe, 'should_stop': lambda: False},
                                  execution_id='EX-observed')
        future.result(timeout=5)
        self.assertEqual(applied, [], 'nothing is applied until the owner pumps')
        self.assertEqual(calls.collect(), 1)
        self.assertEqual(order, [('applied', 'one'), ('applied', 'two'), ('collected', {'status': 'completed'})])
        second = continuation(); next(second)
        def fail_then_wait(on_observation, should_stop):
            on_observation('bad')
            while not should_stop():
                time.sleep(.01)
            return {'status': 'stopped'}
        calls.start_call(second, fail_then_wait, {'on_observation': observe, 'should_stop': lambda: False},
                         execution_id='EX-failed-observation')
        until = time.monotonic() + 5
        while calls.futures and time.monotonic() < until:
            calls.collect(); time.sleep(.01)
        self.assertEqual(failures, [('EX-failed-observation', 'unapplied observation')])
        self.assertEqual(order[-1], ('collected', {'status': 'stopped'}))
        calls.close()

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
    def test_real_job_cancellation_uses_owner_judgment_and_collects_once(self):
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
                    calls.collect(); calls.judge(); time.sleep(.01)
                self.assertFalse(calls.futures)
                self.assertEqual(len(returned), 1)
                self.assertTrue(returned[0][-1])
                self.assertTrue(named_job_empty(started[0]['job_name']))
                self.assertEqual(calls.collect(), 0)
            finally:
                calls.close()


if __name__ == '__main__':
    unittest.main()
