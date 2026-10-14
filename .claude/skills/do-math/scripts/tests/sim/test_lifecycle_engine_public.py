"""The lifecycle through public controls and restarts on the Sim (``engine.control``, ``ResearchEngine``).

A new instance comes from the public ``initialize`` (a Sim without activation);
an active one is a restore of this process's public activation
(``Sim.activated()``), whose build ran the public initialization, controls,
probe, trust and the interpretation calls through the worker and model double.
A restart is a new engine on the same repository and ports (``sim.restart()``).
"""
from copy import deepcopy
from datetime import datetime, timedelta
import tempfile
import unittest

from do_math.engine import ResearchEngine
from do_math.initialization import original_input_bytes
from support.engine_lifecycle import applied
from support.sim import Sim, warm_template

setUpModule = warm_template


def new_instance(test, **options):
    """A Sim of a publicly initialized instance; removed with ``test``."""
    directory = tempfile.TemporaryDirectory()
    test.addCleanup(directory.cleanup)
    return Sim(directory.name, **options)


class InitializingLifecycleTests(unittest.TestCase):
    def test_public_utc_watermark_is_published_only_with_normal_change(self):
        sim = new_instance(self, goal='Preserve this original input')
        engine = sim.engine
        engine._save()  # Establish any ordinary derived runtime fields first.
        head = engine.head
        initial = datetime.fromisoformat(engine.runtime['last_observed_utc'])
        observed = initial + timedelta(hours=2)
        sim.clock.set_wall(observed)  # the wall clock moves; the monotonic clock stays
        engine._require_action_clock()
        engine._save()
        self.assertEqual(engine.head, head, 'clock observation alone created a commit')
        engine.instance['title'] = 'Ordinary state update'
        engine._save()
        self.assertEqual(engine.runtime['last_observed_utc'], observed.isoformat())
        restarted = ResearchEngine(sim.repository, sim.instance_id, ports=sim.ports, codex_home=sim.codex_home, environment=sim.environment, host_id=sim.host_id)
        sim.clock.set_wall(observed - timedelta(microseconds=1))
        self.assertEqual(restarted._clock_guard()['reason'], 'persisted_utc_regression')
        # A later rejected sample does not revoke the prior trusted sample.
        sim.clock.set_wall(observed + timedelta(hours=1))
        trusted = engine._require_action_clock()
        sim.clock.set_wall(observed + timedelta(minutes=30))
        self.assertFalse(engine._clock_guard()['usable'])
        engine._pause_lifecycle('clock_regression')
        engine._save()
        self.assertEqual(engine.store.load()[2]['last_observed_utc'], trusted)

    def test_public_unicode_original_survives_restart(self):
        source = 'Cafe\u0301'  # a combining accent, not the precomposed letter
        sim = new_instance(self, goal=source)
        sim.restart()
        self.assertEqual(original_input_bytes(sim.instance['lifecycle']['immutable_input']), source.encode())

    def test_public_initializing_pause_resume_preserves_source_and_missing(self):
        sim = new_instance(self, goal='Preserve this original input')
        source = deepcopy(sim.runtime['inputs'])
        applied(sim, 'pause', config={})
        self.assertEqual(sim.runtime['resume_lifecycle'], 'initializing')
        applied(sim, 'resume', config={})
        sim.restart()
        self.assertEqual(sim.instance['lifecycle']['state'], 'initializing')
        self.assertEqual(sim.runtime['inputs'], source)
        self.assertIn('independent_intent', sim.instance['lifecycle']['activation']['missing'])
        self.assertNotIn('missing', sim.runtime['availability'])
        applied(sim, 'close', config={})
        self.assertTrue(sim.instance['lifecycle']['permanently_closed'])
        for action in ('pause', 'resume'):
            # After the resume, the same pause is a new request; a closed instance rejects both.
            request = sim.control(action, text='lifecycle test control: ' + action, config={})
            sim.engine.process_controls()
            self.assertEqual(sim.engine.control_result(request['request_id'])['effect'], 'rejected', action)
        sim.restart()
        self.assertEqual(sim.runtime['status'], 'closed')
        self.assertTrue(sim.instance['lifecycle']['permanently_closed'])

    def test_new_instance_is_v5_initializing_without_implicit_authority(self):
        sim = new_instance(self, goal='Prove the stated goal')
        head, instance, runtime = sim.engine.store.load()
        self.assertEqual(runtime['status'], 'initializing')
        self.assertEqual(runtime['queue'], [])
        self.assertEqual(instance['grants'], {})
        self.assertEqual(head, sim.engine.head)
        status = sim.engine.run(max_steps=1)
        self.assertEqual(status['status'], 'initializing')
        self.assertEqual((sim.model.calls, sim.jobs.launched), ([], []), 'the first run calls no model')


class ActiveLifecycleTests(unittest.TestCase):
    def test_public_call_mode_init_activate_pause_resume_and_persistence(self):
        # The public initialization and activation built this process's template; this copy is their result.
        sim = Sim.activated()
        self.assertEqual(sim.instance['lifecycle']['state'], 'active')
        self.assertEqual(len(sim.runtime['intent_imports']), 1)
        self.assertTrue(sim.instance['active_trust_environment'])
        queued = deepcopy(sim.runtime['queue'])
        attempts = set(sim.runtime['executions'])
        sim.engine.run(until_active=True)
        self.assertEqual(set(sim.runtime['executions']), attempts)
        self.assertEqual(sim.runtime['queue'], queued)
        applied(sim, 'pause', config={})
        self.assertEqual(sim.runtime['resume_lifecycle'], 'active')
        applied(sim, 'resume', config={})
        self.assertEqual(sim.instance['lifecycle']['state'], 'active')
        sim.restart()
        self.assertEqual(sim.instance['lifecycle']['state'], 'active')
        self.assertNotIn('task_readiness', sim.runtime)
        self.assertNotIn('initial_request', sim.instance['lifecycle'])




class PublicControlBoundaryTests(unittest.TestCase):
    def test_operator_pause_keeps_its_origin_and_cannot_release_a_user_pause(self):
        sim = Sim.activated()
        before = deepcopy(sim.runtime['executions'])
        operator = applied(sim, 'pause', origin='operator', text='operator inspection')
        self.assertNotIn('user_pause', sim.runtime)
        history = next(row for row in sim.runtime['history']
                       if row.get('request', {}).get('id') == operator['request_id'])
        self.assertEqual(history['request']['origin'], 'operator')
        self.assertEqual(sim.runtime['resume_lifecycle'], 'active')
        user = applied(sim, 'pause', text='user holds research')
        pause = deepcopy(sim.runtime['user_pause'])
        rejected = sim.control('resume', origin='operator', text='operator inspection complete')
        self.assertTrue(rejected['accepted'])
        sim.engine.process_controls()
        receipt = sim.engine.control_result(rejected['request_id'])
        self.assertEqual((receipt['effect'], receipt['reason']),
                         ('rejected', 'an effective user pause requires an explicit user resume'))
        self.assertEqual(sim.runtime['user_pause'], pause)
        self.assertEqual(pause['request_id'], user['request_id'])
        self.assertEqual(sim.runtime['resume_lifecycle'], 'active')
        self.assertEqual(sim.runtime['executions'], before)
        applied(sim, 'resume', text='user releases research')
        self.assertNotIn('user_pause', sim.runtime)
        self.assertEqual(sim.instance['lifecycle']['state'], 'active')
        sim.restart()
        self.assertEqual(sim.engine.control_result(rejected['request_id']), receipt)
        self.assertEqual(sim.runtime['executions'], before)

    def test_regressed_clock_remains_blocked_after_wall_time_catches_up(self):
        sim = Sim.activated()
        engine = sim.engine
        self.assertTrue(engine._clock_guard()['usable'])
        wall = sim.clock.wall()
        before = deepcopy((engine.instance, engine.runtime))
        sim.clock.set_wall(wall - timedelta(seconds=1))
        failure = deepcopy(engine._clock_guard())
        self.assertFalse(failure['usable'])
        sim.clock.set_wall(wall)
        self.assertEqual(engine._clock_guard(), failure)
        with self.assertRaisesRegex(RuntimeError, '^cannot publish a lifecycle event while the clock guard blocks new actions$'):
            engine._lifecycle_event('user_input_available')
        self.assertEqual((engine.instance, engine.runtime), before)
        self.assertTrue(engine._execution_stop_requested(engine.runtime['queue'][0]))
        engine._refresh_readiness()
        self.assertEqual(engine.runtime['clock_guard'], {'state': 'blocked', **failure})
        self.assertEqual(engine.runtime['availability'], {'state': 'blocked', 'reason': 'clock_regression'})
        self.assertEqual(engine.instance['lifecycle']['state'], 'paused')
        self.assertEqual(engine.runtime['resume_lifecycle'], 'active')
        self.assertEqual(engine.runtime['executions'], before[1]['executions'])

    def test_closed_marker_blocks_dispatch_without_inventing_a_closed_phase(self):
        sim = Sim.activated()
        engine = sim.engine
        action = deepcopy(sim.runtime['queue'][0])
        before = deepcopy((engine.instance, engine.runtime))
        self.assertEqual(engine._activate_initialization(), {'activated': True, 'missing': []})
        self.assertEqual((engine.instance, engine.runtime), before)
        applied(sim, 'close', text='permanent lifecycle boundary')
        self.assertTrue(sim.instance['lifecycle']['permanently_closed'])
        self.assertEqual(sim.instance['lifecycle']['state'], 'active')
        self.assertEqual(sim.runtime['status'], 'closed')
        sealed = deepcopy((engine.instance, engine.runtime))
        with self.assertRaisesRegex(ValueError, '^closed/completed instance cannot dispatch$'):
            engine._action_lifecycle_gate(action)
        engine._refresh_readiness()
        self.assertEqual((engine.instance, engine.runtime), sealed)
        sim.clock.set_wall(sim.clock.wall() - timedelta(seconds=1))
        engine._refresh_readiness()
        self.assertEqual(engine.runtime['clock_guard']['state'], 'blocked')
        self.assertEqual(engine.instance['lifecycle'], sealed[0]['lifecycle'])
        self.assertEqual(engine.runtime['status'], 'closed')
        self.assertNotIn('resume_lifecycle', engine.runtime)
        self.assertEqual(engine.runtime['executions'], sealed[1]['executions'])

    def test_heartbeat_is_judged_at_delivery_and_cannot_revive_an_expired_generation(self):
        sim = Sim.activated()
        applied(sim, 'conversation', config={'operation': 'attach', 'id': 'lease',
            'generation': 1, 'lease_seconds': 10, 'disconnect_policy': 'pause'})
        sim.advance(2)
        heartbeat = applied(sim, 'conversation', text='live heartbeat', config={
            'operation': 'heartbeat', 'id': 'lease', 'generation': 1})
        row = deepcopy(sim.runtime['conversations']['lease'])
        self.assertEqual(row['last_heartbeat_at'], sim.clock.now())
        self.assertEqual(row['lease_expires_at'], (sim.clock.wall() + timedelta(seconds=10)).isoformat())
        self.assertEqual(row['source_ref'], heartbeat['request_id'])
        delayed = sim.control('conversation', text='admitted before expiry', config={
            'operation': 'heartbeat', 'id': 'lease', 'generation': 1})
        self.assertTrue(delayed['accepted'])
        self.assertEqual(delayed['effect'], 'pending engine processing')
        sim.advance(10)
        # Apply the already-admitted envelope before general readiness expires the lease.
        sim.engine._apply_inbox()
        receipt = sim.engine.control_result(delayed['request_id'])
        self.assertEqual((receipt['effect'], receipt['reason']),
                         ('rejected', 'expired generation must reconnect with a new generation'))
        self.assertEqual(sim.runtime['conversations']['lease'], row)
        sim.engine._refresh_readiness()
        self.assertEqual(sim.runtime['conversations']['lease']['status'], 'lost')
        self.assertEqual(sim.runtime['status'], 'paused')
        self.assertEqual(sim.runtime['lost_conversation_generations']['lease'], 1)
        lost = deepcopy((sim.instance, sim.runtime))
        sim.engine._lose_conversation(sim.runtime['conversations']['lease'], 'duplicate loss')
        self.assertEqual((sim.instance, sim.runtime), lost)
        sim.engine._save()  # Persist the owner-observed loss before the next public caller reloads it.
        duplicate = sim.control('conversation', text='same generation cannot reconnect', config={
            'operation': 'attach', 'id': 'lease', 'generation': 1, 'lease_seconds': 10})
        sim.engine.process_controls()
        self.assertEqual(sim.engine.control_result(duplicate['request_id'])['reason'],
                         'reattachment requires a new connection generation')
        applied(sim, 'conversation', text='new generation', config={
            'operation': 'attach', 'id': 'lease', 'generation': 2, 'lease_seconds': 10})
        self.assertEqual(sim.runtime['status'], 'paused')
        applied(sim, 'resume', text='explicit resume after reconnect')
        self.assertEqual(sim.instance['lifecycle']['state'], 'active')
        sim.restart()
        self.assertEqual(sim.engine.control_result(delayed['request_id']), receipt)

    def test_conversation_lease_boundary_agrees_for_resume_heartbeat_and_loss(self):
        for policy in ('pause', 'continue_authorized'):
            for offset in (-0.000001, 0, 0.000001):
                with self.subTest(policy=policy, offset=offset):
                    sim = Sim.activated()
                    attached = applied(sim, 'conversation', config={'operation': 'attach',
                        'id': 'lease', 'generation': 1, 'lease_seconds': 10,
                        'disconnect_policy': policy})
                    row = deepcopy(sim.runtime['conversations']['lease'])
                    self.assertEqual(row['source_ref'], attached['request_id'])
                    status_before = sim.runtime['status']
                    sim.advance(10 + offset)
                    self.assertEqual(sim.engine._conversation_live(),
                                     policy != 'pause' or offset < 0)
                    if offset < 0:
                        sim.engine._conversation_control({'operation': 'heartbeat',
                            'id': 'lease', 'generation': 1}, attached['request_id'])
                        renewed = sim.runtime['conversations']['lease']
                        self.assertEqual(renewed['last_heartbeat_at'], sim.clock.now())
                        self.assertEqual(renewed['lease_expires_at'],
                                         (sim.clock.wall() + timedelta(seconds=10)).isoformat())
                        self.assertFalse(sim.engine._check_conversations())
                    else:
                        with self.assertRaisesRegex(ValueError, 'expired generation'):
                            sim.engine._conversation_control({'operation': 'heartbeat',
                                'id': 'lease', 'generation': 1}, attached['request_id'])
                        self.assertEqual(sim.runtime['conversations']['lease'], row)
                        self.assertTrue(sim.engine._check_conversations())
                        self.assertEqual(sim.runtime['conversations']['lease']['loss_reason'],
                                         'heartbeat_lease_expired')
                        after_loss = deepcopy((sim.instance, sim.runtime))
                        self.assertFalse(sim.engine._check_conversations())
                        self.assertEqual((sim.instance, sim.runtime), after_loss)
                        self.assertEqual(sim.runtime['status'],
                                         'paused' if policy == 'pause' else status_before)

    def test_resume_requires_a_live_generation_newer_than_the_lost_generation(self):
        """About 2.3 s: four public attachments with storage/restart checks, loss and explicit resume."""
        sim = Sim.activated()
        self.assertEqual(sim.instance['conversation_loss_policy'], 'continue_authorized')

        def assert_saved_policy(policy, generation, request):
            def check(instance, runtime):
                self.assertEqual(instance['conversation_loss_policy'], policy)
                row = runtime['conversations']['lease']
                self.assertEqual(row['disconnect_policy'], policy)
                self.assertEqual(row['generation'], generation)
                self.assertEqual(row['source_ref'], request['request_id'])
            check(sim.instance, sim.runtime)
            _, stored, runtime = sim.engine.store.load()
            check(stored, runtime)
            sim.restart()
            check(sim.instance, sim.runtime)

        request = applied(sim, 'conversation', config={'operation': 'attach', 'id': 'lease',
            'generation': 1, 'lease_seconds': 10, 'disconnect_policy': 'pause'})
        assert_saved_policy('pause', 1, request)
        applied(sim, 'conversation', config={'operation': 'detach', 'id': 'lease',
            'generation': 1})
        self.assertFalse(sim.engine._conversation_live())
        self.assertEqual(sim.runtime['lost_conversation_generations']['lease'], 1)
        for generation in (1, 2):
            with self.subTest(generation=generation):
                if generation == 1:
                    with self.assertRaisesRegex(ValueError, 'new connection generation'):
                        sim.engine._conversation_control({'operation': 'attach', 'id': 'lease',
                            'generation': generation, 'lease_seconds': 10}, 'same-generation')
                    self.assertFalse(sim.engine._conversation_live())
                else:
                    request = applied(sim, 'conversation', config={'operation': 'attach', 'id': 'lease',
                        'generation': generation, 'lease_seconds': 10})
                    assert_saved_policy('pause', generation, request)
                    self.assertTrue(sim.engine._conversation_live())
                    applied(sim, 'resume')
                    self.assertEqual(sim.instance['lifecycle']['state'], 'active')
        request = applied(sim, 'conversation', config={'operation': 'attach', 'id': 'lease',
            'generation': 3, 'lease_seconds': 10, 'disconnect_policy': 'continue_authorized'})
        assert_saved_policy('continue_authorized', 3, request)
        request = applied(sim, 'conversation', config={'operation': 'attach', 'id': 'lease',
            'generation': 4, 'lease_seconds': 10})
        assert_saved_policy('continue_authorized', 4, request)

    def test_semantically_invalid_conversations_preserve_the_live_connection(self):
        sim = Sim.activated()
        applied(sim, 'conversation', config={'operation': 'attach', 'id': 'live',
            'generation': 1, 'lease_seconds': 60, 'disconnect_policy': 'continue_authorized'})
        before = deepcopy(sim.runtime['conversations'])
        cases = [
            ({'operation': 'attach', 'id': '', 'generation': 1, 'lease_seconds': 60},
             'conversation requires an ID and positive connection generation'),
            ({'operation': 'attach', 'id': 'missing-lease', 'generation': 1},
             'conversation lease_seconds must be finite and positive'),
            ({'operation': 'unknown', 'id': 'live', 'generation': 1},
             'conversation operation must be attach, heartbeat or detach'),
        ]
        for config, reason in cases:
            with self.subTest(config=config):
                request = sim.control('conversation', text='negative conversation input', config=config)
                self.assertTrue(request['accepted'])
                sim.engine.process_controls()
                receipt = sim.engine.control_result(request['request_id'])
                self.assertEqual((receipt['effect'], receipt['reason']), ('rejected', reason))
                self.assertEqual(sim.runtime['conversations'], before)
                self.assertNotIn(request['request_id'], sim.runtime['extended_controls'])
                self.assertNotIn(request['request_id'], sim.instance['governance_sources'])
                self.assertEqual(sim.runtime['processed_controls'].count(request['request_id']), 1)
        applied(sim, 'conversation', config={'operation': 'heartbeat', 'id': 'live', 'generation': 1})
        self.assertEqual(sim.runtime['conversations']['live']['status'], 'connected')

    def test_nonuser_decisions_are_refused_both_at_admission_and_after_external_tampering(self):
        import json
        from pathlib import Path
        from do_math.canonical import canonical_json
        sim = Sim.activated()
        # Only negative external envelopes below are altered. No normal decision is fabricated.
        cases = [
            ('initialization', 'initialization adoption requires user authority'),
            ('limited_recovery', 'limited recovery requires explicit user authority'),
            ('repetition_continue', 'repetition continuation requires explicit user authority'),
        ]
        before = deepcopy((sim.instance['decisions'], sim.instance['grants'], sim.runtime['queue']))
        for kind, reason in cases:
            with self.subTest(kind=kind):
                config = {'change': {'kind': kind}}
                with self.assertRaisesRegex(ValueError, '^operator controls are limited to '):
                    sim.control('decision', origin='operator', text='negative origin', config=config)
                request = sim.control('decision', text='negative external origin', config=config)
                path = Path(sim.instance['workspace']) / 'control' / sim.instance_id / (request['request_id'] + '.json')
                envelope = json.loads(path.read_bytes())
                self.assertEqual(envelope['origin'], 'user')
                envelope['origin'] = 'operator'
                raw = canonical_json(envelope)
                path.write_bytes(raw)
                sim.engine.process_controls()
                receipt = sim.engine.control_result(request['request_id'])
                self.assertEqual((receipt['effect'], receipt['reason']), ('rejected', reason))
                self.assertEqual(path.read_bytes(), raw)
                self.assertNotIn(request['request_id'], sim.instance['governance_sources'])
                self.assertNotIn(request['request_id'], sim.runtime['extended_controls'])
                self.assertEqual((sim.instance['decisions'], sim.instance['grants'], sim.runtime['queue']), before)
                self.assertEqual(sim.runtime['processed_controls'].count(request['request_id']), 1)
                sim.engine.process_controls()
                self.assertEqual(sim.engine.control_result(request['request_id']), receipt)


class LimitedRecoveryPublicTests(unittest.TestCase):
    def queued_repair(self):
        sim = Sim.activated()
        applied(sim, 'request', text='inspect current research', config={'role': 'maintenance'})
        action = next(row for row in sim.runtime['queue'] if row['role'] == 'maintenance')
        change = {'kind': 'limited_recovery', 'action_id': action['id'],
            'grant_id': sim.instance['lifecycle']['adoption']['research_grant_ids'][0],
            'profile_ref': sim.engine._select_model(action)['profile_ref'],
            'purpose': 'inspect current research', 'procedure': 'Inspect the current state and report unresolved facts',
            'expires_at': (sim.clock.wall() + timedelta(minutes=5)).isoformat()}
        return sim, action['id'], change

    def test_approval_checks_live_phase_action_role_profile_and_expiry(self):
        sim, action_id, change = self.queued_repair()
        attempts = deepcopy(sim.runtime['executions'])
        active = sim.control('decision', text='approval before pause', config={'change': change})
        sim.engine.process_controls()
        self.assertEqual(sim.engine.control_result(active['request_id'])['reason'],
                         'limited recovery requires paused research')
        applied(sim, 'pause', text='pause for a bounded repair')
        general = next(row for row in sim.runtime['queue'] if row['role'] == 'research_preparation')
        cases = [
            ({'action_id': 'AC-absent'}, 'limited recovery must name one existing queued action'),
            ({'action_id': general['id']}, 'limited recovery cannot authorize ordinary research'),
            *[({field: ''}, 'limited recovery requires ' + field)
              for field in ('procedure', 'purpose', 'grant_id', 'expires_at')],
            ({'profile_ref': sim.instance['role_profile_refs']['research_preparation'][0]},
             'limited recovery requires the exact role profile'),
            ({'expires_at': sim.clock.now()}, 'limited recovery approval has expired'),
        ]
        for difference, reason in cases:
            with self.subTest(difference=difference):
                before = deepcopy((sim.instance['grants'], sim.runtime['queue']))
                request = sim.control('decision', text='negative limited recovery', config={'change': {**change, **difference}})
                self.assertTrue(request['accepted'])
                sim.engine.process_controls()
                receipt = sim.engine.control_result(request['request_id'])
                self.assertEqual((receipt['effect'], receipt['reason']), ('rejected', reason))
                self.assertEqual((sim.instance['grants'], sim.runtime['queue']), before)
                self.assertNotIn(request['request_id'], sim.runtime['extended_controls'])
        approved = applied(sim, 'decision', text='approve bounded repair', config={'change': change})
        action = next(row for row in sim.runtime['queue'] if row['id'] == action_id)
        sim.engine._check_limited_recovery(action)
        binding = action['repair']['limited_recovery']
        self.assertEqual(binding['source_ref'], approved['request_id'])
        self.assertEqual(sim.instance['governance_sources'][approved['request_id']]['origin'], 'user')
        self.assertEqual(sim.runtime['executions'], attempts)
        self.assertEqual(sim.runtime['status'], 'paused')
        self.assertEqual(sim.runtime['resume_lifecycle'], 'active')

    def test_expiry_and_capability_loss_reject_the_previously_approved_action(self):
        sim, action_id, change = self.queued_repair()
        applied(sim, 'pause', text='bounded recovery')
        approved = applied(sim, 'decision', text='approve exact action', config={'change': change})
        action = next(row for row in sim.runtime['queue'] if row['id'] == action_id)
        sim.engine._check_limited_recovery(action)
        before = deepcopy((sim.instance, sim.runtime))
        identity = sim.ports.host.identity
        try:
            sim.ports.host.identity = {'host': 'changed-after-approval'}
            with self.assertRaisesRegex(ValueError, '^limited recovery capability evidence is unavailable$'):
                sim.engine._check_limited_recovery(action)
        finally:
            sim.ports.host.identity = identity
        sim.engine._check_limited_recovery(action)
        sim.advance(300)
        with self.assertRaisesRegex(ValueError, '^limited recovery no longer matches its approval$'):
            sim.engine._check_limited_recovery(action)
        self.assertFalse(sim.engine._limited_recovery_allowed(action))
        self.assertTrue(sim.engine._execution_stop_requested(action))
        self.assertEqual((sim.instance, sim.runtime), before)
        self.assertEqual(sim.engine.control_result(approved['request_id'])['effect'], 'applied')

    def test_revocation_removes_recovery_authority_without_reopening_research(self):
        sim, action_id, change = self.queued_repair()
        applied(sim, 'pause', text='bounded recovery')
        applied(sim, 'decision', text='approve exact action', config={'change': change})
        action = deepcopy(next(row for row in sim.runtime['queue'] if row['id'] == action_id))
        attempts = deepcopy(sim.runtime['executions'])
        applied(sim, 'decision', text='revoke repair authority',
                config={'change': {'kind': 'revoke', 'grant_id': change['grant_id']}})
        with self.assertRaisesRegex(ValueError, '^limited recovery authority: '):
            sim.engine._check_limited_recovery(action)
        self.assertFalse(sim.engine._limited_recovery_allowed(action))
        self.assertEqual(sim.instance['grants'][change['grant_id']]['status'], 'revoked')
        self.assertEqual(sim.runtime['status'], 'paused')
        self.assertEqual(sim.runtime['resume_lifecycle'], 'active')
        self.assertEqual(sim.runtime['executions'], attempts)
        applied(sim, 'resume', text='resume phase after revocation; no grant is restored')
        with self.assertRaisesRegex(ValueError, '^limited recovery requires paused, nonclosed research$'):
            sim.engine._check_limited_recovery(action)
        self.assertEqual(sim.instance['grants'][change['grant_id']]['status'], 'revoked')
        self.assertEqual(sim.runtime['executions'], attempts)
if __name__ == '__main__':
    unittest.main()
