"""The lifecycle through public controls and restarts on the Sim (``engine.control``, ``ResearchEngine``).

A new instance comes from the public ``initialize`` (a Sim without activation);
an active one is a restore of this process's public activation
(``Sim.activated()``), whose build ran the public initialization, controls,
probe, trust and the interpretation calls through the worker and model double.
A restart is a new engine on the same repository and ports (``sim.restart()``).
"""
from copy import deepcopy
from datetime import datetime, timedelta
import hashlib
import json
import tempfile
import unittest

from do_math.engine import ResearchEngine
from do_math.initialization import original_input_bytes
from support.engine_lifecycle import applied
from support.scheduling_clock import ScriptedClock, with_clock
from support.sim import Sim, warm_template
from support.wait_reporting import assert_status_report

setUpModule = warm_template


def new_instance(test, **options):
    """A Sim of a publicly initialized instance; removed with ``test``."""
    directory = tempfile.TemporaryDirectory()
    test.addCleanup(directory.cleanup)
    return Sim(directory.name, **options)


def read_publication(engine, head=None):
    """First load with a new installed contract decodes Git bytes instead of a publication cache."""
    from do_math.repository import ResearchRepository
    from support.state_builders import installed_contract
    reader = ResearchRepository(engine.store.repository, engine.instance['id'],
        backend=engine.ports.git_backend, clock=engine.ports.clock, contract=installed_contract())
    head, instance, runtime = reader.load(head or engine.head)
    return reader, head, instance, runtime


def assert_runtime_metadata(test, engine, expected, *, absent=(), head=None):
    """Decode a publication and check independent metadata values, including object contents."""
    import json
    reader, head, _, runtime = read_publication(engine, head)
    envelope = json.loads(reader.read('runtime/_state/metadata.json', head))
    manifest = json.loads(reader.read('runtime/_state/manifest.json', head))
    for name, value in expected.items():
        test.assertEqual(runtime[name], value, name)
        test.assertIs(type(runtime[name]), type(value), name)
        test.assertEqual(envelope['record'][name], value, name)
        family = reader.contract.family('runtime', name)
        test.assertEqual(family.shape, 'metadata')
        test.assertEqual(manifest['containers'][name], {'shape': 'metadata'})
        test.assertEqual(list(family.checker.iter_errors(value)), [])
    for name in absent:
        test.assertNotIn(name, runtime)
        test.assertNotIn(name, envelope['record'])
        test.assertNotIn(name, manifest['containers'])
    return runtime


def assert_conversation_publication(test, engine, expected, policy, *, lost=None, head=None):
    """Compare the actual map record, policy metadata and optional ID-to-generation singleton."""
    import json
    reader, head, instance, runtime = read_publication(engine, head)
    test.assertEqual(runtime['conversations'], {expected['id']: expected})
    actual = runtime['conversations'][expected['id']]
    test.assertIs(type(actual['generation']), int)
    test.assertIs(type(actual['lease_seconds']), int)
    path = 'runtime/conversations/' + expected['id'] + '.json'
    test.assertEqual(json.loads(reader.read(path, head))['record'], expected)
    test.assertEqual(reader.read_record(expected['id'], head)['json_pointer'], '/record')
    test.assertEqual(instance['conversation_loss_policy'], policy)
    metadata = json.loads(reader.read('research/_state/metadata.json', head))
    test.assertEqual(metadata['record']['conversation_loss_policy'], policy)
    manifest = json.loads(reader.read('research/_state/manifest.json', head))
    test.assertEqual(manifest['containers']['conversation_loss_policy'], {'shape': 'metadata'})
    manifest = json.loads(reader.read('runtime/_state/manifest.json', head))
    test.assertEqual(manifest['containers']['conversations'], {'shape': 'map', 'ids': [expected['id']]})
    if lost is None:
        test.assertNotIn('lost_conversation_generations', runtime)
        test.assertNotIn('lost_conversation_generations', manifest['containers'])
    else:
        test.assertEqual(runtime['lost_conversation_generations'], lost)
        test.assertTrue(all(type(value) is int for value in runtime['lost_conversation_generations'].values()))
        test.assertEqual(manifest['containers']['lost_conversation_generations'], {'shape': 'singleton'})
        envelope = json.loads(reader.read('runtime/lost_conversation_generations/state.json', head))
        test.assertEqual(envelope['record'], lost)
    return actual


def assert_closed_family_samples(test, name, samples, *, root='runtime'):
    """Use the common reverse-field check on actual closed records from this module's publications."""
    from contracts.pairs import Pair, assert_pair
    from do_math.state_contract import validate_record
    from support.state_builders import installed_contract
    from support.storage_authority_pairs import _named_fields
    family = installed_contract().family(root, name)
    schema = family.schema['additionalProperties'] if name == 'extended_controls' else family.schema

    def written(value):
        values = list(value.values()) if name == 'extended_controls' else [value]
        return _named_fields(schema, values)

    def receive(value):
        validate_record(family.checker, value, name)
        if family.validator:
            family.validator(value)

    assert_pair(test, Pair(name, lambda root: samples, receive,
                          frozenset(_named_fields(schema)), written), samples)


def assert_control_singleton(test, engine, root, name, expected, *, head=None):
    """One cold load checks the singleton blob, manifest and exact producer content."""
    reader, head, instance, runtime = read_publication(engine, head)
    value = (instance if root == 'research' else runtime)[name]
    test.assertEqual(value, expected)
    test.assertEqual(json.loads(reader.read(f'{root}/{name}/state.json', head))['record'], expected)
    manifest = json.loads(reader.read(f'{root}/_state/manifest.json', head))
    test.assertEqual(manifest['containers'][name], {'shape': 'singleton'})
    return value


class InitializingLifecycleTests(unittest.TestCase):
    def test_processed_and_extended_controls_preserve_exact_requests_across_replay(self):
        """About 2.5 s: public success/rejection/replay, several cold singleton reads and two restarts."""
        from pathlib import Path
        sim = new_instance(self)
        engine = sim.engine
        initial_head = engine.head
        assert_control_singleton(self, engine, 'runtime', 'processed_controls', [])
        assert_control_singleton(self, engine, 'runtime', 'extended_controls', {})
        config = {'operation': 'attach', 'id': 'chat', 'generation': 1, 'lease_seconds': 60,
                  'disconnect_policy': 'continue_authorized'}
        text = '승인 e\u0301\r\n원 요청 그대로 🙂\n'
        submitted_at = sim.clock.now()
        sent = sim.control('conversation', config=config, text=text, request_id='UC-storage-exact')
        path = Path(sim.instance['workspace']) / 'control' / sim.instance_id / (sent['request_id'] + '.json')
        raw = path.read_bytes()
        request = json.loads(raw)
        self.assertEqual((request['text'], request['config'], request['origin'], request['created_at']),
                         (text, config, 'user', submitted_at))
        config['generation'] = 99  # the admitted payload owns its copy
        sim.advance(3)
        engine.process_controls()
        processed_at = sim.clock.now()
        expected = {sent['request_id']: {'request': request, 'action': 'conversation', 'processed_at': processed_at}}
        accepted_head = engine.head
        sample = assert_control_singleton(self, engine, 'runtime', 'extended_controls', expected)
        assert_closed_family_samples(self, 'extended_controls', [('attached', sample)])
        assert_control_singleton(self, engine, 'runtime', 'processed_controls', [sent['request_id']])
        self.assertEqual(engine.control_result(sent['request_id'])['effect'], 'applied')
        before = deepcopy((engine.instance, engine.runtime))
        self.assertTrue(engine._apply_extended_control(deepcopy(request)))
        with self.assertRaisesRegex(ValueError, '^user control ID reused with changed content$'):
            engine._apply_extended_control({**request, 'text': text + 'changed'})
        self.assertEqual((engine.instance, engine.runtime), before)
        sample[sent['request_id']]['request']['config']['generation'] = 100
        assert_control_singleton(self, engine, 'runtime', 'extended_controls', expected)
        replay = sim.control('conversation', config=request['config'], text=text, request_id=sent['request_id'])
        self.assertTrue(replay['replayed'])
        with self.assertRaisesRegex(ValueError, '^request_id reused with different payload$'):
            sim.control('conversation', config=request['config'], text=text + 'changed', request_id=sent['request_id'])
        sim.restart()
        engine = sim.engine
        engine.process_controls()
        self.assertEqual(engine.head, accepted_head)
        self.assertEqual(path.read_bytes(), raw)
        bad = sim.control('conversation', config={'operation': 'heartbeat', 'id': 'chat', 'generation': 999})
        engine.process_controls()
        self.assertEqual(engine.control_result(bad['request_id'])['effect'], 'rejected')
        paused = applied(sim, 'pause')
        resumed = applied(sim, 'resume')
        sim.advance(2)
        following = applied(sim, 'conversation', config={'operation': 'detach', 'id': 'chat', 'generation': 1})
        follow_path = path.with_name(following['request_id'] + '.json')
        expected[following['request_id']] = {'request': json.loads(follow_path.read_bytes()),
            'action': 'conversation', 'processed_at': sim.clock.now()}
        order = [q['request_id'] for q in (sent, bad, paused, resumed, following)]
        assert_control_singleton(self, engine, 'runtime', 'processed_controls', order)
        assert_control_singleton(self, engine, 'runtime', 'extended_controls', expected)
        self.assertEqual([row['request']['id'] for row in sim.runtime['history']
            if row.get('kind') in {'user_control', 'rejected_user_control'}], order)
        sim.restart()
        sim.engine.process_controls()
        assert_control_singleton(self, sim.engine, 'runtime', 'processed_controls', order)
        assert_control_singleton(self, sim.engine, 'runtime', 'extended_controls', expected)
        assert_control_singleton(self, sim.engine, 'runtime', 'processed_controls', [], head=initial_head)
        assert_control_singleton(self, sim.engine, 'runtime', 'extended_controls', {}, head=initial_head)
        assert_control_singleton(self, sim.engine, 'runtime', 'processed_controls', [sent['request_id']], head=accepted_head)
        assert_control_singleton(self, sim.engine, 'runtime', 'extended_controls',
            {sent['request_id']: expected[sent['request_id']]}, head=accepted_head)

    def test_recovery_check_and_preparation_counter_store_the_actual_engine_results(self):
        from do_math.execution_lifecycle import transition_execution
        sim = new_instance(self)
        engine = sim.engine
        initial_head = engine.head
        self.assertFalse(engine._activate_initialization()['activated'])
        engine._save()
        assert_runtime_metadata(self, engine, {'recovery_checked': True, 'cycles': 0})
        action = {'id': 'AC-storage-preparation', 'role': 'research_preparation'}
        execution = engine._register_execution(action,
            {'id': 'EX-storage-preparation', 'role': 'research_preparation', 'status': 'running'})
        self.assertFalse(engine._activate_initialization()['activated'])
        engine._save()
        busy_head = engine.head
        assert_runtime_metadata(self, engine, {'recovery_checked': False, 'cycles': 0})
        # Direct result application is the layer-2 producer; this does not certify call admission.
        engine._apply(action, {'candidates': []}, execution['id'], owns_response=False)
        execution = engine.runtime['executions'][execution['id']]
        transition_execution(execution, 'stopping', at=sim.clock.now())
        transition_execution(execution, 'ended', at=sim.clock.now(), outcome='execution_incomplete')
        self.assertFalse(engine._activate_initialization()['activated'])
        engine._save()
        assert_runtime_metadata(self, engine, {'recovery_checked': True, 'cycles': 1})
        assert_runtime_metadata(self, engine, {'recovery_checked': False, 'cycles': 0}, head=busy_head)
        assert_runtime_metadata(self, engine, {'recovery_checked': False, 'cycles': 0}, head=initial_head)

    def test_public_utc_watermark_is_published_only_with_normal_change(self):
        sim = new_instance(self, goal='Preserve this original input')
        engine = sim.engine
        engine._save()  # Establish any ordinary derived runtime fields first.
        head = engine.head
        initial_updated = engine.runtime['updated_at']
        initial = datetime.fromisoformat(engine.runtime['last_observed_utc'])
        observed = initial + timedelta(hours=2)
        sim.clock.set_wall(observed)  # the wall clock moves; the monotonic clock stays
        engine._require_action_clock()
        engine._save()
        self.assertEqual(engine.head, head, 'clock observation alone created a commit')
        assert_runtime_metadata(self, engine, {'updated_at': initial_updated,
                                              'last_observed_utc': initial.isoformat()})
        engine.instance['title'] = 'Ordinary state update'
        # now() is a publication timestamp, independent of the guarded wall() sample.
        engine.ports = with_clock(sim, ScriptedClock(['2090-01-01T02:07:08.123456+00:00'], base=sim.clock))
        try:
            engine._save()
        finally:
            engine.ports = sim.ports
        self.assertEqual(engine.runtime['last_observed_utc'], observed.isoformat())
        assert_runtime_metadata(self, engine, {'updated_at': '2090-01-01T02:07:08.123456+00:00',
                                              'last_observed_utc': observed.isoformat()})
        assert_runtime_metadata(self, engine, {'updated_at': initial_updated,
                                              'last_observed_utc': initial.isoformat()}, head=head)
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
        assert_runtime_metadata(self, engine, {'last_observed_utc': trusted,
                                              'updated_at': '2090-01-01T02:30:00+00:00',
                                              'status': 'paused', 'resume_lifecycle': 'initializing',
                                              'stop_requested': 'clock_regression'})

    def test_public_unicode_original_survives_restart(self):
        source = 'Cafe\u0301\r\n원문 🙂\n'  # combining accent, CRLF and non-ASCII UTF-8
        sim = new_instance(self, goal=source)
        expected = deepcopy(sim.instance['lifecycle'])
        self.assertEqual(expected['immutable_input'], {'text': source, 'bytes': len(source.encode('utf-8')),
            'sha256': hashlib.sha256(source.encode('utf-8')).hexdigest()})
        self.assertEqual(expected['input_id'], sim.runtime['inputs'][0]['id'])
        self.assertEqual(expected['state'], 'initializing')
        self.assertEqual(expected['adoption'], {})
        assert_control_singleton(self, sim.engine, 'research', 'lifecycle', expected)
        initial_head = sim.engine.head
        sim.restart()
        self.assertEqual(original_input_bytes(sim.instance['lifecycle']['immutable_input']), source.encode())
        assert_control_singleton(self, sim.engine, 'research', 'lifecycle', expected, head=initial_head)

    def test_public_initializing_pause_resume_preserves_source_and_missing(self):
        sim = new_instance(self, goal='Preserve this original input')
        source = deepcopy(sim.runtime['inputs'])
        original_head = sim.engine.head
        applied(sim, 'pause', config={})
        self.assertEqual(sim.runtime['resume_lifecycle'], 'initializing')
        pause_head = sim.engine.head
        assert_runtime_metadata(self, sim.engine, {'status': 'paused', 'resume_lifecycle': 'initializing',
                                                  'stop_requested': 'user_pause'})
        applied(sim, 'resume', config={})
        assert_runtime_metadata(self, sim.engine, {'status': 'initializing'},
                                absent=('resume_lifecycle', 'stop_requested'))
        assert_runtime_metadata(self, sim.engine, {'status': 'paused', 'resume_lifecycle': 'initializing',
                                                  'stop_requested': 'user_pause'}, head=pause_head)
        assert_runtime_metadata(self, sim.engine, {'status': 'initializing', 'cycles': 0, 'recovery_checked': False},
                                absent=('resume_lifecycle', 'stop_requested', 'next_research_reconsider_at'), head=original_head)
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
        assert_runtime_metadata(self, sim.engine, {'status': 'closed'})
        self.assertTrue(sim.instance['lifecycle']['permanently_closed'])

    def test_new_instance_is_v5_initializing_without_implicit_authority(self):
        sim = new_instance(self, goal='Prove the stated goal')
        import json
        reader, initial, instance, runtime = read_publication(sim.engine)
        self.assertNotIn('conversation_loss_policy', instance)
        self.assertNotIn('conversation_loss_policy', json.loads(
            reader.read('research/_state/metadata.json', initial))['record'])
        self.assertNotIn('conversation_loss_policy', json.loads(
            reader.read('research/_state/manifest.json', initial))['containers'])
        self.assertEqual(runtime['conversations'], {})
        self.assertNotIn('lost_conversation_generations', runtime)
        initial_availability = assert_runtime_metadata(self, sim.engine,
            {'availability': {'state': 'blocked', 'reason': 'initialization_incomplete'}},
            absent=('user_pause',))['availability']
        head, instance, runtime = sim.engine.store.load()
        self.assertEqual(runtime['status'], 'initializing')
        self.assertEqual(runtime['queue'], [])
        self.assertEqual(instance['grants'], {})
        self.assertEqual(head, sim.engine.head)
        status = sim.engine.run(max_steps=1)
        self.assertEqual(status['status'], 'initializing')
        self.assertEqual((sim.model.calls, sim.jobs.launched), ([], []), 'the first run calls no model')
        blocked = assert_runtime_metadata(self, sim.engine, {'availability': {
            'state': 'blocked', 'reason': 'initialization_incomplete', 'next_owner': 'user'}})['availability']
        assert_closed_family_samples(self, 'availability', [('initial', initial_availability), ('missing', blocked)])
        for policy in ('pause', 'continue_authorized'):
            applied(sim, 'decision', config={'change': {'kind': 'initialization', 'operation': 'adopt',
                                                       'conversation_loss_policy': policy}})
            reader, published, instance, runtime = read_publication(sim.engine)
            self.assertEqual(instance['conversation_loss_policy'], policy)
            self.assertEqual(json.loads(reader.read('research/_state/metadata.json', published))['record']
                             ['conversation_loss_policy'], policy)
            self.assertEqual(instance['grants'], {}, 'adopting a loss policy grants no authority')
        self.assertNotIn('conversation_loss_policy', read_publication(sim.engine, initial)[2])


class ActiveLifecycleTests(unittest.TestCase):
    def test_public_call_mode_init_activate_pause_resume_and_persistence(self):
        """About 4.5 s: real controls, nested lifecycle checks, cold decodes, old heads and close."""
        # The public initialization and activation built this process's template; this copy is their result.
        sim = Sim.activated()
        from do_math.canonical import exact_content_hash
        from support.sim import GOAL
        engine = sim.engine
        active = deepcopy(sim.instance['lifecycle'])
        adoption = active['adoption']
        for field, value in (('config', sim.instance['config']), ('governance', sim.instance['governance']),
                             ('review_policy', sim.instance['review_policy'])):
            self.assertEqual(adoption[field + '_sha256'], exact_content_hash(value))
        requests = [row['request'] for row in sim.runtime['history'] if row.get('kind') == 'user_control']
        adopted = next(q for q in requests if q.get('config', {}).get('change', {}).get('research_grant_ids'))
        for field in ('initial_profile_ref', 'initial_grant_ids', 'research_grant_ids', 'external_policy'):
            self.assertEqual(adoption[field], adopted['config']['change'][field])
        self.assertEqual(adoption['source_refs'], [q['id'] for q in requests
            if q.get('config', {}).get('change', {}).get('kind') == 'initialization'
            and q['config']['change'].get('operation', 'adopt') in {'governance', 'adopt'}])
        self.assertEqual(active['immutable_input'], {'text': GOAL, 'bytes': len(GOAL.encode('utf-8')),
            'sha256': hashlib.sha256(GOAL.encode('utf-8')).hexdigest()})
        bundle = next(row for row in sim.runtime['intent_imports'].values() if row['input_ref'] == active['input_id'])
        self.assertEqual(active['intent_check'], {'input_sha256': hashlib.sha256(GOAL.encode()).hexdigest(),
            'interpretation_execution_id': bundle['execution_id'], 'check_execution_id': bundle['check']['execution_id']})
        self.assertNotEqual(bundle['execution_id'], bundle['check']['execution_id'])
        self.assertEqual(active['activation'], {'missing': [], 'observation_errors': []})
        samples = [('active', assert_control_singleton(self, engine, 'research', 'lifecycle', active))]
        active_head = engine.head
        self.assertEqual(sim.instance['lifecycle']['state'], 'active')
        activated_at = datetime.fromisoformat(sim.instance['lifecycle']['activated_at'])
        self.assertEqual(sim.instance['config']['research_reconsider_seconds'], 86400)
        assert_runtime_metadata(self, sim.engine, {'status': 'ready', 'recovery_checked': True,
            'availability': {'state': 'available'},
            'next_research_reconsider_at': (activated_at + timedelta(days=1)).isoformat()},
            absent=('resume_lifecycle', 'stop_requested'))
        self.assertEqual(len(sim.runtime['intent_imports']), 1)
        self.assertTrue(sim.instance['active_trust_environment'])
        queued = deepcopy(sim.runtime['queue'])
        attempts = set(sim.runtime['executions'])
        sim.engine.run(until_active=True)
        self.assertEqual(set(sim.runtime['executions']), attempts)
        self.assertEqual(sim.runtime['queue'], queued)
        applied(sim, 'pause', config={})
        self.assertEqual(sim.runtime['resume_lifecycle'], 'active')
        pause_head = sim.engine.head
        paused = deepcopy(sim.instance['lifecycle'])
        self.assertEqual(paused['history'][-1]['kind'], 'pause')
        self.assertEqual(paused['history'][-1]['reason'], 'user_pause')
        self.assertEqual(paused['immutable_input'], active['immutable_input'])
        samples.append(('paused', assert_control_singleton(self, engine, 'research', 'lifecycle', paused)))
        assert_runtime_metadata(self, sim.engine, {'status': 'paused', 'resume_lifecycle': 'active',
                                                  'stop_requested': 'user_pause'})
        applied(sim, 'resume', config={})
        self.assertEqual(sim.instance['lifecycle']['state'], 'active')
        sim.restart()
        self.assertEqual(sim.instance['lifecycle']['state'], 'active')
        self.assertNotIn('task_readiness', sim.runtime)
        self.assertNotIn('initial_request', sim.instance['lifecycle'])
        assert_runtime_metadata(self, sim.engine, {'status': 'ready', 'recovery_checked': True},
                                absent=('resume_lifecycle', 'stop_requested'))
        assert_runtime_metadata(self, sim.engine, {'status': 'paused', 'resume_lifecycle': 'active',
                                                  'stop_requested': 'user_pause'}, head=pause_head)
        resumed = deepcopy(sim.instance['lifecycle'])
        self.assertEqual(resumed, {**paused, 'state': 'active'})
        assert_control_singleton(self, sim.engine, 'research', 'lifecycle', active, head=active_head)
        closed_request = applied(sim, 'close', text='Seal the original input and adopted lifecycle')
        closed = deepcopy(sim.instance['lifecycle'])
        self.assertEqual(closed, {**resumed, 'permanently_closed': True,
            'history': [*resumed['history'], {'kind': 'closed', 'source_ref': closed_request['request_id']}]})
        self.assertEqual(sim.runtime['status'], 'closed')
        samples.append(('closed', assert_control_singleton(self, sim.engine, 'research', 'lifecycle', closed)))
        assert_closed_family_samples(self, 'lifecycle', samples, root='research')

    def test_reconsideration_deadline_is_stored_consumed_and_renewed(self):
        """About 2.9 s: actual readiness/renewal, publication and cold reader/restart."""
        from do_math.planning import collect_due_events
        sim = Sim.activated()
        engine = sim.engine
        due = datetime.fromisoformat(sim.instance['lifecycle']['activated_at']) + timedelta(days=1)
        initial_head = engine.head
        assert_runtime_metadata(self, engine, {'next_research_reconsider_at': due.isoformat()})
        self.assertEqual(collect_due_events(sim.instance, sim.runtime,
            (due - timedelta(microseconds=1)).isoformat()), [])
        observed = due + timedelta(seconds=13, microseconds=123456)
        sim.clock.set_wall(observed)
        engine._refresh_readiness()
        engine._save()
        renewed = (observed + timedelta(days=1)).isoformat()
        assert_runtime_metadata(self, engine, {'next_research_reconsider_at': renewed})
        events = [row for row in sim.runtime['events'] if row['kind'] == 'research_reconsider_due']
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]['at'], due.isoformat())
        self.assertEqual(collect_due_events(sim.instance, sim.runtime, observed.isoformat()), [])
        sim.restart()
        assert_runtime_metadata(self, sim.engine, {'next_research_reconsider_at': renewed})
        assert_runtime_metadata(self, sim.engine, {'next_research_reconsider_at': due.isoformat()}, head=initial_head)




class PublicControlBoundaryTests(unittest.TestCase):
    def test_idle_lease_expiry_is_consumed_once_across_public_run_and_restart(self):
        """About 14 s: two policies, accepted preparation, idle scheduler expiry and four restarts."""
        from support.default_responder import DefaultResponder
        for policy in ('pause', 'continue_authorized'):
            with self.subTest(policy=policy):
                sim = Sim.activated()
                sim.model.responder = DefaultResponder(preparation_candidates=[])
                sim.step()
                applied(sim, 'conversation', config={'operation': 'attach', 'id': 'idle-lease',
                    'generation': 1, 'lease_seconds': 10, 'disconnect_policy': policy})
                calls = len(sim.model.calls)
                sim.advance(9)
                sim.restart()
                sim.engine.run(max_steps=1)
                self.assertEqual(sim.runtime['conversations']['idle-lease']['status'], 'connected')
                sim.advance(1)
                sim.engine.run(max_steps=1)
                row = deepcopy(sim.runtime['conversations']['idle-lease'])
                self.assertEqual(row['status'], 'lost')
                self.assertEqual(row['lost_at'], sim.clock.now())
                self.assertEqual(sim.instance['lifecycle']['state'], 'paused' if policy == 'pause' else 'active')
                def losses():
                    return [event for event in sim.runtime['events']
                            if event['kind'] == 'conversation_lost' and event.get('target') == 'idle-lease']
                lost = deepcopy(losses())
                self.assertEqual(len(lost), 1)
                for _ in range(2):
                    sim.restart()
                    sim.engine.run(max_steps=1)
                    self.assertEqual(sim.runtime['conversations']['idle-lease'], row)
                    self.assertEqual(losses(), lost)
                self.assertEqual(len(sim.model.calls), calls)

    def test_operator_pause_keeps_its_origin_and_cannot_release_a_user_pause(self):
        """About 4 s: public controls, reporting, restart and cold decodes of the hold and old head."""
        sim = Sim.activated()
        assert_runtime_metadata(self, sim.engine, {}, absent=('user_pause',))
        before = deepcopy(sim.runtime['executions'])
        operator = applied(sim, 'pause', origin='operator', text='operator inspection')
        self.assertNotIn('user_pause', sim.runtime)
        history = next(row for row in sim.runtime['history']
                       if row.get('request', {}).get('id') == operator['request_id'])
        self.assertEqual(history['request']['origin'], 'operator')
        self.assertEqual(sim.runtime['resume_lifecycle'], 'active')
        created_at = sim.clock.now()
        user = applied(sim, 'pause', text='user holds research')
        expected = {'request_id': user['request_id'], 'reason': 'user holds research', 'created_at': created_at}
        self.assertEqual(sim.runtime['user_pause'], expected)
        pause_head = sim.engine.head
        assert_runtime_metadata(self, sim.engine, {'user_pause': expected})
        pause = deepcopy(sim.runtime['user_pause'])
        report, human = assert_status_report(self, sim.engine)
        self.assertEqual(report['operating_summary']['primary_blocker'],
                         {'kind': 'user_pause', 'next_owner': 'user', **pause})
        self.assertEqual(report['user_pause'], pause)
        self.assertIn('blocking: user_pause next=user', human)
        self.assertIn('  reason: user holds research', human)
        self.assertIn('  request_id: ' + user['request_id'], human)
        self.assertIn('  created_at: ' + pause['created_at'], human)
        report['operating_summary']['primary_blocker']['reason'] = 'observer change'
        self.assertEqual(sim.engine.store.load()[2]['user_pause'], pause)
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
        report, human = assert_status_report(self, sim.engine)
        self.assertEqual(report['operating_summary']['primary_blocker']['request_id'], user['request_id'])
        self.assertIn('  reason: user holds research', human)
        applied(sim, 'resume', text='user releases research')
        assert_runtime_metadata(self, sim.engine, {}, absent=('user_pause',))
        assert_runtime_metadata(self, sim.engine, {'user_pause': expected}, head=pause_head)
        self.assertNotIn('user_pause', sim.runtime)
        self.assertEqual(sim.instance['lifecycle']['state'], 'active')
        sim.restart()
        self.assertEqual(sim.engine.control_result(rejected['request_id']), receipt)
        self.assertEqual(sim.runtime['executions'], before)
        report, human = assert_status_report(self, sim.engine)
        self.assertIsNone(report['user_pause'])
        self.assertNotEqual((report['operating_summary']['primary_blocker'] or {}).get('kind'), 'user_pause')
        self.assertNotIn('blocking: user_pause', human)
        self.assertNotIn(user['request_id'], human)

    def test_regressed_clock_remains_blocked_after_wall_time_catches_up(self):
        """About 4.1 s: real clock-block producers, cold guard/owner/history reads and restart."""
        sim = Sim.activated()
        engine = sim.engine
        available_head = engine.head
        self.assertTrue(engine._clock_guard()['usable'])
        wall = sim.clock.wall()
        before = deepcopy((engine.instance, engine.runtime))
        sim.clock.set_wall(wall - timedelta(seconds=1))
        failure = deepcopy(engine._clock_guard())
        self.assertFalse(failure['usable'])
        self.assertEqual(failure, {'usable': False, 'reason': 'persisted_utc_regression',
            'last_observed_utc': before[1]['last_observed_utc'],
            'observed_utc': (wall - timedelta(seconds=1)).isoformat(),
            'expected_at_least': before[1]['last_observed_utc']})
        self.assertNotIn('clock_guard', before[1], 'a computed guard alone is not published')
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
        paused = deepcopy((engine.instance, engine.runtime))
        for _ in range(2):
            engine._refresh_readiness()
            self.assertEqual((engine.instance, engine.runtime), paused,
                             'the retained clock failure must not publish another lifecycle pause')
        engine._save()
        expected_guard = {'state': 'blocked', **failure}
        actual_guard = assert_runtime_metadata(self, engine, {
            'availability': {'state': 'blocked', 'reason': 'clock_regression'},
            'clock_guard': expected_guard})['clock_guard']
        assert_closed_family_samples(self, 'clock_guard', [('retained failure', actual_guard)])
        blocked_head = engine.head
        self.assertFalse(engine._prepare_executor_pass())
        assert_runtime_metadata(self, engine, {'availability': {
            'state': 'blocked', 'reason': 'clock_regression', 'next_owner': 'operator'}})
        engine._refresh_readiness()
        engine._save()
        assert_runtime_metadata(self, engine, {'availability': {'state': 'blocked', 'reason': 'clock_regression'}})
        assert_runtime_metadata(self, engine, {'availability': {'state': 'available'}}, head=available_head)
        sim.restart()
        self.assertEqual(sim.instance['lifecycle']['history'], paused[0]['lifecycle']['history'])
        self.assertTrue(sim.engine._clock_guard()['usable'])
        assert_runtime_metadata(self, sim.engine, {'clock_guard': expected_guard})
        applied(sim, 'resume', text='Resume after cold owner re-observed the recovered clock')
        self.assertEqual(sim.instance['lifecycle']['state'], 'active')
        self.assertNotIn('stop_requested', sim.runtime)
        self.assertEqual(sim.runtime['executions'], before[1]['executions'])
        assert_runtime_metadata(self, sim.engine, {'clock_guard': expected_guard}, head=blocked_head)
        assert_runtime_metadata(self, sim.engine, {}, absent=('clock_guard',), head=available_head)

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
        """Public controls and cold Git decodes (~3 s) preserve exact lease values and historical heads."""
        sim = Sim.activated()
        start = sim.clock.wall()
        attached = applied(sim, 'conversation', config={'operation': 'attach', 'id': 'lease',
            'generation': 1, 'lease_seconds': 10, 'disconnect_policy': 'pause'})
        connected = {'id': 'lease', 'generation': 1, 'status': 'connected', 'lease_seconds': 10,
            'disconnect_policy': 'pause', 'attached_at': start.isoformat(), 'last_heartbeat_at': start.isoformat(),
            'lease_expires_at': (start + timedelta(seconds=10)).isoformat(), 'source_ref': attached['request_id']}
        attached_head = sim.engine.head
        samples = [('attach', assert_conversation_publication(self, sim.engine, connected, 'pause'))]
        sim.advance(2)
        heartbeat = applied(sim, 'conversation', text='live heartbeat', config={
            'operation': 'heartbeat', 'id': 'lease', 'generation': 1})
        renewed = {**connected, 'last_heartbeat_at': (start + timedelta(seconds=2)).isoformat(),
            'lease_expires_at': (start + timedelta(seconds=12)).isoformat(), 'source_ref': heartbeat['request_id']}
        heartbeat_head = sim.engine.head
        samples.append(('heartbeat', assert_conversation_publication(self, sim.engine, renewed, 'pause')))
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
        expired = {**renewed, 'status': 'lost', 'lost_at': (start + timedelta(seconds=12)).isoformat(),
                   'loss_reason': 'heartbeat_lease_expired'}
        lost_head = sim.engine.head
        samples.append(('expired', assert_conversation_publication(self, sim.engine, expired, 'pause', lost={'lease': 1})))
        duplicate = sim.control('conversation', text='same generation cannot reconnect', config={
            'operation': 'attach', 'id': 'lease', 'generation': 1, 'lease_seconds': 10})
        sim.engine.process_controls()
        self.assertEqual(sim.engine.control_result(duplicate['request_id'])['reason'],
                         'reattachment requires a new connection generation')
        reattached = applied(sim, 'conversation', text='new generation', config={
            'operation': 'attach', 'id': 'lease', 'generation': 2, 'lease_seconds': 10})
        replacement = {**connected, 'generation': 2, 'attached_at': (start + timedelta(seconds=12)).isoformat(),
            'last_heartbeat_at': (start + timedelta(seconds=12)).isoformat(),
            'lease_expires_at': (start + timedelta(seconds=22)).isoformat(), 'source_ref': reattached['request_id']}
        samples.append(('new generation', assert_conversation_publication(self, sim.engine, replacement, 'pause',
                                                                         lost={'lease': 1})))
        self.assertEqual(sim.runtime['status'], 'paused')
        applied(sim, 'resume', text='explicit resume after reconnect')
        self.assertEqual(sim.instance['lifecycle']['state'], 'active')
        assert_conversation_publication(self, sim.engine, replacement, 'pause', lost={'lease': 1})
        assert_conversation_publication(self, sim.engine, connected, 'pause', head=attached_head)
        assert_conversation_publication(self, sim.engine, renewed, 'pause', head=heartbeat_head)
        assert_conversation_publication(self, sim.engine, expired, 'pause', lost={'lease': 1}, head=lost_head)
        assert_closed_family_samples(self, 'conversations', samples)
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
        """About 3 s: four public attachments, cold storage reads, detach/expiry, restart and explicit resume."""
        sim = Sim.activated()
        self.assertEqual(sim.instance['conversation_loss_policy'], 'continue_authorized')

        def assert_saved_policy(policy, generation, request):
            at = sim.clock.wall()
            expected = {'id': 'lease', 'generation': generation, 'status': 'connected', 'lease_seconds': 10,
                'disconnect_policy': policy, 'attached_at': at.isoformat(), 'last_heartbeat_at': at.isoformat(),
                'lease_expires_at': (at + timedelta(seconds=10)).isoformat(), 'source_ref': request['request_id']}
            assert_conversation_publication(self, sim.engine, expected, policy,
                                            lost=None if generation == 1 else {'lease': 1})
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
            return expected

        request = applied(sim, 'conversation', config={'operation': 'attach', 'id': 'lease',
            'generation': 1, 'lease_seconds': 10, 'disconnect_policy': 'pause'})
        connected = assert_saved_policy('pause', 1, request)
        attached_head = sim.engine.head
        sim.advance(1)
        detached = applied(sim, 'conversation', config={'operation': 'detach', 'id': 'lease',
            'generation': 1})
        lost_record = {**connected, 'status': 'lost', 'lost_at': sim.clock.now(), 'loss_reason': 'explicit_detach'}
        assert_conversation_publication(self, sim.engine, lost_record, 'pause', lost={'lease': 1})
        detach_head = sim.engine.head
        loss = next(event for event in sim.runtime['events']
                    if event['kind'] == 'conversation_lost' and event.get('target') == 'lease')
        self.assertEqual(loss['source_ref'], detached['request_id'])
        self.assertNotEqual(lost_record['source_ref'], detached['request_id'],
                            'detach is the event source; the record retains the last live signal')
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
        replacement = assert_saved_policy('continue_authorized', 4, request)
        grants = deepcopy(sim.instance['grants'])
        sim.advance(10)
        self.assertTrue(sim.engine._check_conversations())
        sim.engine._save()
        expired = {**replacement, 'status': 'lost', 'lost_at': sim.clock.now(), 'loss_reason': 'heartbeat_lease_expired'}
        assert_conversation_publication(self, sim.engine, expired, 'continue_authorized', lost={'lease': 1})
        self.assertEqual(sim.instance['lifecycle']['state'], 'active')
        self.assertEqual(sim.instance['grants'], grants, 'continuation does not issue authority')
        assert_conversation_publication(self, sim.engine, connected, 'pause', head=attached_head)
        assert_conversation_publication(self, sim.engine, lost_record, 'pause', lost={'lease': 1}, head=detach_head)

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


class StateBoundaryTests(unittest.TestCase):
    def test_closed_run_records_startup_mismatch_without_reopening_or_pausing(self):
        """T3 about 7 s: an actual copied/frozen installation and validated closed state are required."""
        from pathlib import Path
        import operator_bootstrap
        from support.storage_finish_installation import copy_installation
        sim = Sim.activated()
        root = copy_installation(sim.root / 'startup-installation')
        manifest = Path(operator_bootstrap.freeze(root, sim.root / 'startup-frozen')['manifest'])
        applied(sim, 'close', text='close before installation changes')
        entry = root / 'scripts/do_math.py'
        entry.write_bytes(entry.read_bytes() + b'\n# changed installation entry\n')
        engine = ResearchEngine(sim.repository, sim.instance_id, ports=sim.ports, installation_root=root,
            codex_home=sim.codex_home, environment=sim.environment, host_id=sim.host_id)
        before = deepcopy(engine.instance['lifecycle'])
        attempts = len(sim.model.calls)
        result = engine.run(max_steps=1, installation_manifest=manifest)
        self.assertEqual(result['startup']['bootstrap']['comparison'], 'different')
        self.assertEqual(result['status'], 'closed')
        self.assertEqual(engine.instance['lifecycle'], before)
        self.assertEqual(len(sim.model.calls), attempts)
        self.assertEqual(engine.store.load(engine.head)[2]['status'], 'closed')

    def test_control_cannot_reuse_another_preserved_source_identity(self):
        """T3 about 2.3 s: public control receipt and original source must pass real publication."""
        sim = Sim.activated()
        source_id = next(iter(sim.instance['governance_sources']))
        before = deepcopy(sim.instance['governance_sources'])
        request = sim.control('decision', request_id=source_id, text='A different original input',
            config={'change': {'kind': 'revoke', 'grant_id': next(iter(sim.instance['grants']))}})
        self.assertTrue(request['accepted'])
        sim.engine.process_controls()
        receipt = sim.engine.control_result(request['request_id'])
        self.assertEqual((receipt['effect'], receipt['reason']), ('rejected', 'preserved control source ID reused'))
        self.assertEqual(sim.instance['governance_sources'], before)
        self.assertNotIn(source_id, sim.runtime['extended_controls'])

    def test_machine_execution_already_stopping_ends_once_with_its_registered_ticket(self):
        from do_math.execution_lifecycle import transition_execution
        sim = Sim.activated()
        execution = sim.engine._register_execution({'id': 'AC-machine-end', 'role': 'trust_activate'},
            {'id': 'EX-machine-end', 'role': 'trust_activate', 'status': 'running'})
        self.assertIsNotNone(execution)
        self.assertEqual(execution['launch_ticket']['kind'], 'owner_thread')
        transition_execution(execution, 'stopping', at=sim.clock.now())
        self.assertTrue(sim.engine._end_machine_execution(execution, outcome='execution_incomplete',
                                                        disposition={'reason': 'before launch'}))
        ended = deepcopy(execution)
        self.assertTrue(sim.engine._end_machine_execution(execution, outcome='execution_incomplete',
                                                        disposition={'reason': 'before launch'}))
        self.assertEqual(execution, ended)
        self.assertEqual(execution['status'], 'ended')
        self.assertEqual(execution['launch_ticket']['phase'], 'finished')
        sim.engine._save()
        self.assertEqual(sim.engine.store.load(sim.engine.head)[2]['executions'][execution['id']], ended)


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
        request = sim.runtime['extended_controls'][approved['request_id']]['request']
        request['origin'] = 'ai'
        with self.assertRaisesRegex(ValueError, '^limited recovery requires user approval$'):
            sim.engine._check_limited_recovery(action)
        request['origin'] = 'user'
        sim.engine._check_limited_recovery(action)
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
