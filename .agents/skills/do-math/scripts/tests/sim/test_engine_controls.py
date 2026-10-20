"""User and operator controls on a Sim: transitions, receipts and their identities, queueing and the maintenance fence.

The public ``control`` (``engine``, layer 3) admits a request into the
instance's inbox and the owner applies it (``core_engine._apply_inbox``,
``lifecycle_engine``, ``maintenance_gate``, layer 2). Every test runs the
real engine and storage on the port fakes: an initialized instance
(``Sim(root)``) or a restored activation (``Sim.activated()``). The legacy tests
ran some of these on an engine double whose repository was an autospec; here a
request replays against the published state, and a state change the owner did
not make from the inbox is published through the engine's own save.
"""
from pathlib import Path
import base64
import hashlib
import tempfile
import unittest

from do_math.control_contracts import control_request_id
from do_math.planning import task_ready
from do_math.scheduled_operator import engine_start_guard
from support.engine_lifecycle import clear_work, extended, task
from support.sim import Sim, warm_template

setUpModule = warm_template
CLOSED_LIFECYCLE = 'closed/completed instance cannot apply lifecycle controls'


def paused_then_resumed(sim, **pause):
    """``sim`` paused with ``pause`` (control keyword arguments) and resumed; returns the first pause's receipt."""
    first = sim.control('pause', **pause)
    sim.engine.process_controls()
    sim.control('resume')
    sim.engine.process_controls()
    if sim.engine.status()['status'] == 'paused':
        raise AssertionError("the fixture's resume did not apply")
    return first


class InitializedControlTest(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.sim = Sim(self.root / 'sim', goal='control fixture')


class ControlTransitionTests(InitializedControlTest):
    def test_pause_and_resume_cannot_reopen_a_publicly_closed_instance(self):
        sim, engine = self.sim, self.sim.engine
        sim.control('close')
        engine.process_controls()
        self.assertEqual(engine.status()['status'], 'closed')
        sim.control('pause')
        engine.process_controls()
        self.assertEqual(engine.status()['status'], 'closed')
        rejected = sim.control('resume')
        engine.process_controls()
        status = engine.status()
        self.assertEqual(status['status'], 'closed')
        self.assertEqual(status['pending_controls'], 0)
        _, _, runtime = engine.store.load()
        last = runtime['history'][-1]
        self.assertEqual((last['kind'], last['request']['id'], last['reason']),
                         ('rejected_user_control', rejected['request_id'], CLOSED_LIFECYCLE))

    def test_request_accepted_before_public_close_does_not_reopen_it(self):
        sim, engine = self.sim, self.sim.engine
        sim.control('request', config={'role': 'maintenance'})
        sim.control('close')
        engine.process_controls()
        status = engine.status()
        self.assertEqual(status['status'], 'closed')
        self.assertEqual(status['pending_actions'], 0)
        self.assertEqual(status['pending_controls'], 0)


class ActiveTransitionTests(unittest.TestCase):
    def test_stale_request_is_consumed_and_does_not_poison_later_controls(self):
        from copy import deepcopy
        sim = Sim.activated()
        engine = sim.engine
        clear_work(sim)
        # A task a returned preparation produced, with its sealed approving contract review.
        task(engine, 'TK-stale')
        engine._save()
        self.assertEqual(task_ready(engine.runtime['tasks']['TK-stale'], engine.instance, engine.runtime,
                                    evaluation_context=engine._evaluation_context())['state'], 'ready')
        request = sim.control('request', config={'role': 'supplemental_research', 'target': 'TK-stale'})
        # Delay an admitted file while a public decision removes its readiness premise.
        inbox = Path(sim.instance['workspace']) / 'control' / sim.instance_id
        path = inbox / (request['request_id'] + '.json')
        raw = path.read_bytes()
        delayed = sim.root / 'delayed-supplement.json'
        path.rename(delayed)
        current = engine.runtime['tasks']['TK-stale']
        from do_math.planning import contract_hash
        revision = sim.control('decision', config={'change': {'kind': 'task_scope',
            'task_id': current['id'], 'revision': current['revision'], 'contract_sha256': contract_hash(current),
            'disposition': 'revise', 'reason': 'public readiness premise change'}})
        engine.process_controls()
        self.assertEqual(engine.control_result(revision['request_id'])['effect'], 'applied')
        self.assertEqual(task_ready(engine.runtime['tasks']['TK-stale'], engine.instance, engine.runtime,
            evaluation_context=engine._evaluation_context())['state'], 'not_ready')
        delayed.rename(path)
        self.assertEqual(path.read_bytes(), raw)
        before = deepcopy((engine.runtime['tasks'], engine.runtime['executions'], engine.runtime['reservations']))
        sim.control('pause')
        engine.process_controls()
        status = engine.status()
        self.assertEqual(status['status'], 'paused')
        self.assertEqual(status['pending_controls'], 0)
        _, _, runtime = engine.store.load()
        self.assertIn(request['request_id'], runtime['processed_controls'])
        self.assertEqual((runtime['tasks'], runtime['executions'], runtime['reservations']), before)
        rows = [row for row in runtime['history'] if row.get('request', {}).get('id') == request['request_id']]
        self.assertEqual([(row['kind'], row['reason']) for row in rows],
                         [('rejected_user_control', 'supplemental task is no longer ready')])
        receipt = deepcopy(engine.control_result(request['request_id']))
        rejected_state = deepcopy((engine.head, engine.instance, engine.runtime))
        sim.restart()
        sim.engine.process_controls()
        self.assertEqual((sim.engine.head, sim.instance, sim.runtime), rejected_state)
        self.assertEqual(sim.engine.control_result(request['request_id']), receipt)
        self.assertEqual(sim.runtime['processed_controls'].count(request['request_id']), 1)
        self.assertEqual(path.read_bytes(), raw)

    def test_crash_marks_owning_activity_unresolved(self):
        sim = Sim.activated()
        engine = sim.engine
        clear_work(sim)
        engine._enqueue('research_preparation', reason='Prepare the control transition fixture')
        engine._save()
        action = engine.runtime['queue'][0]
        engine._register_execution(action, {'id': 'EX-crashed', 'role': action['role'], 'status': 'running',
                                            'input_snapshot': engine.head, 'input_manifest': []})
        engine._save()
        sim.restart()  # the owner process ended; a new one takes over the same repository
        sim.step()
        _, _, runtime = sim.engine.store.load()
        recovered = runtime['executions']['EX-crashed']
        self.assertEqual(recovered['status'], 'stopping')
        self.assertNotIn('outcome', recovered)
        self.assertEqual(recovered['recovery_disposition'], 'reconcile_local_and_remote')
        owner = runtime['activities'][recovered['owner_activity_id']]
        self.assertIn('EX-crashed', owner['assigned_execution_ids'])
        self.assertTrue(runtime['recoveries'])
        disposition = next(row for recovery in runtime['recoveries'].values()
                           for row in recovery['dispositions'] if row['execution_id'] == 'EX-crashed')
        self.assertFalse(disposition['local_termination_confirmed'])
        self.assertEqual(disposition['remote_termination'], 'unknown')
        self.assertEqual(disposition['next_owner'], 'operator')


class SourceControlReceiptTests(InitializedControlTest):
    def test_unchanged_source_control_publishes_one_replayable_receipt(self):
        sim, engine = self.sim, self.sim.engine
        source = self.root / 'source.txt'
        source.write_text('fixed source\n', encoding='utf-8')
        sim.control('source', config={'path': str(source)})
        engine.process_controls()
        before = dict(engine.instance['sources'][0])
        self.assertEqual(before['revision'], 1)
        sent = sim.control('source', config={'path': str(source)}, request_id='UC-unchanged-source')
        self.assertEqual(sent['effect'], 'pending engine processing')
        engine._apply_inbox(pump=False)
        engine._upkeep()
        receipt = engine.control_result('UC-unchanged-source')
        self.assertEqual((receipt['effect'], receipt['reason']), ('applied', 'source content unchanged'))
        self.assertEqual(engine.instance['sources'][0], before)
        replay = sim.control('source', config={'path': str(source)}, request_id='UC-unchanged-source')
        self.assertEqual(replay['snapshot'], receipt['snapshot'])
        self.assertEqual(len([row for row in engine.runtime['history']
                              if row.get('request', {}).get('id') == 'UC-unchanged-source']), 1)
        source.write_text('updated source\n', encoding='utf-8')
        sim.control('source', config={'path': str(source)}, request_id='UC-changed-source')
        engine._apply_inbox(pump=False)
        engine._upkeep()
        self.assertEqual(engine.instance['sources'][0]['revision'], 2)
        self.assertEqual(engine.store.read(engine.instance['sources'][0]['path'], engine.head), source.read_bytes())


class UserControlIdentityTests(InitializedControlTest):
    def test_same_request_replays_before_changed_state_admission(self):
        sim, engine = self.sim, self.sim.engine
        first = sim.control('request', config={'role': 'maintenance'}, request_id='UC-explicit')
        # The instance closes while the request waits in the inbox (the owner applies a close directly).
        extended(engine, 'close', {})
        engine._save()
        with self.assertRaisesRegex(ValueError, '^closed/completed instance cannot accept new research activities$'):
            sim.control('request', config={'role': 'maintenance'}, request_id='UC-other')
        replay = sim.control('request', config={'role': 'maintenance'}, request_id='UC-explicit')
        self.assertEqual(first['request_id'], replay['request_id'])
        self.assertTrue(replay['replayed'])
        inbox = Path(engine.instance['workspace']) / 'control' / sim.instance_id
        self.assertEqual([path.name for path in inbox.glob('*.json')], ['UC-explicit.json'])
        with self.assertRaisesRegex(ValueError, '^request_id reused with different payload$'):
            sim.control('request', config={'role': 'maintenance'}, text='changed', request_id='UC-explicit')

    def test_git_replay_keeps_original_outcome_and_snapshot_after_close(self):
        sim, engine = self.sim, self.sim.engine
        first = sim.control('pause', text='pause once')
        engine.process_controls()
        original = engine.control_result(first['request_id'])
        self.assertEqual(original['status'], 'paused')
        sim.control('close')
        engine.process_controls()
        self.assertEqual(engine.runtime['status'], 'closed')
        replay = sim.control('pause', text='pause once')
        self.assertTrue(replay['replayed'])
        self.assertEqual({key: replay[key] for key in original}, original)
        self.assertNotEqual(engine.head, original['snapshot'])
        self.assertEqual(first['request_id'], control_request_id(sim.instance_id, 'pause', text='pause once'))

    def test_default_pause_after_resume_is_a_new_request_that_pauses(self):
        sim = self.sim
        first = paused_then_resumed(sim, text='hold')
        again = sim.control('pause', text='hold')
        self.assertNotEqual(again['request_id'], first['request_id'])
        self.assertNotIn('replayed', again)
        sim.engine.process_controls()
        self.assertEqual(sim.engine.status()['status'], 'paused')

    def test_explicit_idempotency_key_keeps_its_request_id_and_replays_after_resume(self):
        sim = self.sim
        first = paused_then_resumed(sim, text='hold', idempotency_key='hold-once')
        again = sim.control('pause', text='hold', idempotency_key='hold-once')
        self.assertEqual(again['request_id'], first['request_id'])
        self.assertEqual(again['request_id'],
                         control_request_id(sim.instance_id, 'pause', text='hold', idempotency_key='hold-once'))
        self.assertTrue(again['replayed'])
        sim.restart()
        self.assertNotEqual(sim.engine.status()['status'], 'paused')

    def test_normalized_source_has_one_identity_and_rejects_wrong_bytes(self):
        sim = self.sim
        spec = {'name': 'source.txt', 'body_base64': base64.b64encode(b'original').decode(),
                'sha256': hashlib.sha256(b'original').hexdigest(), 'bytes': 8}
        result = sim.control('source', config=spec, idempotency_key='source-once')
        self.assertEqual(result['request_id'],
                         control_request_id(sim.instance_id, 'source', config=spec, idempotency_key='source-once'))
        with self.assertRaisesRegex(ValueError, '^source bytes differ from their declared hash or size$'):
            sim.control('source', config={**spec, 'bytes': 7})


class ControlQueueTests(unittest.TestCase):
    def test_every_queued_user_control_has_a_stable_queue_identity(self):
        # resume only restores the lifecycle (lifecycle_engine._resume_lifecycle); it queues no activity.
        sim = Sim.activated()
        clear_work(sim)
        for action, config, role in (('input', {}, 'intent_interpretation'),
                                     ('request', {'role': 'maintenance'}, 'maintenance')):
            with self.subTest(action=action):
                before = [row['id'] for row in sim.runtime['queue']]
                sim.control(action, text='Explicit request', config=config)
                sim.engine.process_controls()
                added = [row for row in sim.runtime['queue'] if row['id'] not in before]
                self.assertEqual([row['role'] for row in added], [role])
                self.assertTrue(added[0]['id'].startswith('AC-'), added[0])
                self.assertEqual(added[0]['id'], added[0]['lineage_id'])

    def test_distinct_approved_cleanup_scopes_are_not_merged(self):
        with tempfile.TemporaryDirectory() as directory:
            engine = Sim(Path(directory)).engine
            before = list(engine.runtime['queue'])
            engine._enqueue('maintenance', requested_by='UC-one', cleanup_execution_ids=['EX-one'])
            engine._enqueue('maintenance', requested_by='UC-two', cleanup_execution_ids=['EX-two'])
            self.assertEqual(engine.runtime['queue'][:len(before)], before)
            added = engine.runtime['queue'][len(before):]
            self.assertEqual([(row['requested_by'], row['cleanup_execution_ids']) for row in added],
                             [('UC-one', ['EX-one']), ('UC-two', ['EX-two'])])


class PublicMaintenanceFenceTests(unittest.TestCase):
    def test_public_maintenance_fence_survives_restart_and_preserves_user_pause(self):
        sim = Sim.activated()
        request = sim.control('quiesce', origin='operator', text='fixture installation maintenance')
        sim.engine.process_controls()
        sim.restart()  # a new owner reads the fence from the published state
        fence = sim.runtime['maintenance_fence']
        self.assertEqual((fence['state'], fence['request_id']), ('quiescent', request['request_id']))
        guard = engine_start_guard(sim.repository, sim.instance_id, Path(sim.instance['workspace']),
                                   status=sim.engine.status(), codex_home=sim.codex_home, environment=sim.environment, host_id=sim.host_id, ports=sim.ports)
        self.assertEqual(guard['outcome'], 'maintenance_waiting')
        sim.control('pause', origin='user', text='separate user pause')
        sim.engine.process_controls()
        sim.control('release_quiesce', origin='operator', text='fixture complete', config={'fence_id': fence['request_id']})
        sim.engine.process_controls()
        sim.restart()
        self.assertNotIn('maintenance_fence', sim.runtime)
        self.assertEqual(sim.runtime['status'], 'paused')
        self.assertEqual(sim.runtime['user_pause']['reason'], 'separate user pause')




class TerminalRequestTests(unittest.TestCase):
    def test_input_and_activity_requests_after_close_are_rejected_once(self):
        from copy import deepcopy
        import json
        from support.engine_shapes import inbox
        sim = Sim.activated()
        maintenance = sim.control('request', config={'role': 'maintenance'}, text='late maintenance')
        request_file, = [path for path in inbox(sim).glob('*.json')
                         if json.loads(path.read_bytes()).get('id') == maintenance['request_id']]
        raw = request_file.read_bytes()
        delayed = sim.root / 'delayed-maintenance.json'
        request_file.rename(delayed)
        closed = sim.control('close', text='terminal request boundary')
        sim.engine.process_controls()
        self.assertEqual(sim.engine.control_result(closed['request_id'])['effect'], 'applied')
        before = deepcopy((sim.runtime['executions'], sim.runtime['reservations']))
        delayed.rename(request_file)
        self.assertEqual(request_file.read_bytes(), raw)
        requests = [
            (sim.control('input', text='a late research input'),
             'new research input requires an unfinished instance'),
            (maintenance,
             'instance ended before the activity request was applied'),
        ]
        sim.engine.process_controls()
        for envelope, reason in requests:
            receipt = sim.engine.control_result(envelope['request_id'])
            self.assertEqual((receipt['effect'], receipt['reason']), ('rejected', reason))
            self.assertEqual(sim.runtime['processed_controls'].count(envelope['request_id']), 1)
        receipts = [deepcopy(sim.engine.control_result(e['request_id'])) for e, _ in requests]
        sim.restart()
        sim.engine.process_controls()
        self.assertTrue(sim.instance['lifecycle']['permanently_closed'])
        self.assertTrue(any(row['kind'] == 'closed' and row['source_ref'] == closed['request_id']
                            for row in sim.instance['lifecycle']['history']))
        self.assertEqual(sim.runtime['status'], 'closed')
        self.assertEqual((sim.runtime['executions'], sim.runtime['reservations']), before)
        self.assertEqual([sim.engine.control_result(e['request_id']) for e, _ in requests], receipts)
        self.assertEqual(sim.runtime['queue'], [])
        self.assertEqual(sim.model.calls, [])
        # Operational configuration remains a valid control on an ended instance.
        value = sim.instance['config']['plan_settle_seconds'] + 1
        following = sim.control('configure', config={'plan_settle_seconds': value})
        sim.engine.process_controls()
        self.assertEqual(sim.engine.control_result(following['request_id'])['effect'], 'applied')
        sim.restart()
        sim.engine.process_controls()
        self.assertEqual(sim.instance['config']['plan_settle_seconds'], value)
        self.assertEqual(sim.runtime['status'], 'closed')
        self.assertEqual(sim.runtime['processed_controls'].count(following['request_id']), 1)
        self.assertEqual([sim.engine.control_result(e['request_id']) for e, _ in requests], receipts)
        self.assertEqual((sim.runtime['executions'], sim.runtime['reservations']), before)

    def test_cleanup_request_binds_only_the_named_existing_execution(self):
        from copy import deepcopy
        sim = Sim.activated()
        ended = next(row for row in sim.runtime['executions'].values() if row['status'] == 'ended')
        clear_work(sim)
        before = deepcopy(sim.runtime['executions'])
        with self.assertRaisesRegex(ValueError, 'cleanup.*user'):
            sim.control('request', origin='operator', config={
                'role': 'maintenance', 'cleanup_execution_ids': [ended['id']]})
        request = sim.control('request', config={
            'role': 'maintenance', 'cleanup_execution_ids': [ended['id']]})
        sim.engine.process_controls()
        self.assertEqual(sim.engine.control_result(request['request_id'])['effect'], 'applied')
        action, = [a for a in sim.runtime['queue'] if a.get('requested_by') == request['request_id']]
        self.assertEqual(action['role'], 'maintenance')
        self.assertEqual(action['cleanup_execution_ids'], [ended['id']])
        self.assertEqual(sim.runtime['executions'], before)
        stored = sim.engine.store.load(sim.engine.head)[2]
        self.assertEqual(stored['queue'], sim.runtime['queue'])
        self.assertEqual(stored['executions'], before)

    def test_acceptance_lock_recheck_replays_the_other_public_submission(self):
        from support.engine_control import on_audit
        from support.engine_shapes import inbox
        sim = Sim.activated()
        entered, first = [], []
        def competing_submission(arguments):
            path = arguments[0]
            if not entered and isinstance(path, str) and Path(path).name == '.acceptance.lock':
                entered.append(True)
                first.append(sim.control('pause', request_id='UC-lock-recheck', text='same request'))
        with on_audit('open', competing_submission):
            second = sim.control('pause', request_id='UC-lock-recheck', text='same request')
        self.assertEqual(len(first), 1)
        self.assertEqual(second['request_id'], first[0]['request_id'])
        self.assertIs(second['replayed'], True)
        self.assertEqual(second['effect'], 'pending engine processing')
        self.assertEqual(len(list(inbox(sim).glob('UC-lock-recheck.json'))), 1)
        sim.engine.process_controls()
        self.assertEqual(sim.engine.control_result(second['request_id'])['effect'], 'applied')
        self.assertEqual(sim.runtime['processed_controls'].count(second['request_id']), 1)

    def test_processed_request_replays_from_published_history_after_inbox_removal(self):
        from copy import deepcopy
        from support.engine_shapes import inbox
        sim = Sim.activated()
        first = sim.control('pause', request_id='UC-history-only', text='preserve receipt')
        sim.engine.process_controls()
        receipt = deepcopy(sim.engine.control_result(first['request_id']))
        (inbox(sim) / (first['request_id'] + '.json')).unlink()
        before = deepcopy((sim.engine.head, sim.runtime))
        replay = sim.control('pause', request_id=first['request_id'], text='preserve receipt')
        self.assertIs(replay['replayed'], True)
        self.assertEqual({key: replay[key] for key in receipt}, receipt)
        self.assertFalse((inbox(sim) / (first['request_id'] + '.json')).exists())
        self.assertEqual((sim.engine.head, sim.runtime), before)
        self.assertEqual(sim.runtime['processed_controls'].count(first['request_id']), 1)
if __name__ == '__main__':
    unittest.main()
