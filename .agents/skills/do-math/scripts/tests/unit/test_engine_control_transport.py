"""The execution control transport over real files (``control_transport.ControlTransport``, layer 2).

Each test runs the product's transport on a temporary folder; one fake clock
port per test draws every transport's tokens, so two transports of a test never
share an ID. The legacy tests replaced module functions to force a race or to
see a read. Here nothing is replaced: a writer is held at the transport's own
``os.link`` by an audit-event callback (``support.engine_control.on_audit``),
receipts and reads are counted through ``sys.monitoring``
(``support.provider_probes.ObservedCalls``) and file-system audit events
(``support.engine_lifecycle.file_access``), and a delivery's file times are
moved beyond the racy window (``settle``) instead of narrowing that window.
"""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import threading
import unittest

from do_math import control_transport, file_io
from do_math.control_transport import ControlTransport
from support.engine_control import on_audit
from support.engine_lifecycle import file_access
from support.fakes.clock import FakeClock
from support.provider_probes import ObservedCalls, settle

BINDING_KEYS = ('transport_id', 'capability', 'execution_id', 'grant_id')
DIFFERENT_SUBMISSION = 'request_id was already submitted with different content'
DIFFERENT_RECEIPT = 'request_id was already received with different content'
REUSED = 'request_id was reused with different content'


def _submit(binding, request_id, marker, outcomes):
    """One writer of the race: its submission, or the collision it must report."""
    try:
        outcomes.append(ControlTransport.worker_submit(binding, request_id=request_id, kind='submit_intent',
                                                       payload={'manifest': [marker + '.json']}))
    except ValueError as error:
        outcomes.append(error)


def delivery(binding, request_id, **fields):
    """The request a worker writes to its inbox: the binding's identity, ``request_id`` and ``fields``."""
    request = {key: binding[key] for key in BINDING_KEYS}
    request.update({'request_id': request_id, 'kind': 'submit_intent', 'payload': {}, **fields})
    (Path(binding['endpoint']) / 'inbox' / (request_id + '.json')).write_text(json.dumps(request), encoding='utf-8')
    return request


class TransportDeliveryTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.clock = FakeClock()
        self.transport = ControlTransport(self.root / 'transport', clock=self.clock)
        self.binding = self.transport.issue('EX-transport', 'GR-transport')
        self.endpoint = Path(self.binding['endpoint'])

    def test_nonstring_control_fields_reject_without_breaking_later_requests(self):
        transport = ControlTransport(clock=self.clock)
        binding = transport.issue('EX-memory', 'GR-memory')
        published = []

        def publish(request):
            published.append(request['request_id'])
            return {'state': 'rejected', 'reason': 'fixture receiver'}
        reasons = {'transport_id': 'transport_id must be nonempty text', 'kind': 'unsupported control kind or payload'}
        for field in ('transport_id', 'kind'):
            for index, value in enumerate(([], {})):
                with self.subTest(field=field, value=value):
                    request = {**binding, 'request_id': field + '-' + str(index),
                               'kind': 'submit_intent', 'payload': {}, field: value}
                    receipt = transport.receive(request, publish=publish)
                    self.assertEqual((receipt['state'], receipt['reason']), ('rejected', reasons[field]))
                    # The rejection is recorded: the same request replays it.
                    self.assertEqual(transport.receive(request, publish=publish), receipt)
        self.assertEqual(published, [])
        receipt = transport.receive({**binding, 'request_id': 'valid-after-errors',
                                     'kind': 'submit_intent', 'payload': {}}, publish=publish)
        self.assertEqual((receipt['state'], receipt['reason']), ('rejected', 'fixture receiver'))
        self.assertEqual(published, ['valid-after-errors'])

    def test_competing_different_payloads_cannot_both_submit(self):
        request_id = 'race-one'
        request_path = self.endpoint / 'inbox' / (request_id + '.json')
        barrier = threading.Barrier(2)
        held, reached = threading.local(), []

        def hold(arguments):
            # A writer links its complete file to the final name only after reading that name absent;
            # each writer waits there until the other has read it absent too.
            if Path(arguments[1]) == request_path and not getattr(held, 'done', False):
                held.done = True
                reached.append(threading.current_thread().name)
                barrier.wait(timeout=10)
        outcomes = []
        with on_audit('os.link', hold):
            threads = [threading.Thread(target=_submit, args=(self.binding, request_id, marker, outcomes), name=marker)
                       for marker in ('first', 'second')]
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join(timeout=15)
        self.assertTrue(all(not thread.is_alive() for thread in threads), 'race reproduction deadlocked')
        self.assertEqual(sorted(reached), ['first', 'second'], 'both writers read the name absent before either linked')
        submitted = [value for value in outcomes if isinstance(value, dict)]
        collisions = [value for value in outcomes if isinstance(value, ValueError)]
        self.assertEqual(1, len(submitted), outcomes)
        self.assertEqual(1, len(collisions), outcomes)
        self.assertEqual(str(collisions[0]), DIFFERENT_SUBMISSION)
        stored = json.loads(request_path.read_text(encoding='utf-8'))
        self.assertEqual(submitted[0]['request_id'], stored['request_id'])
        replay = ControlTransport.worker_submit(self.binding, request_id=request_id, kind='submit_intent',
                                                payload=stored['payload'])
        self.assertEqual('submitted', replay['state'])

    def test_file_identifiers_reject_path_glob_and_windows_device_names(self):
        invalid = ('../escape', 'part/name', 'part\\name', 'wild*card', 'query?', 'CON', 'trail.')
        for request_id in invalid:
            with self.subTest(request_id=request_id):
                with self.assertRaisesRegex(ValueError, '^request_id must be a safe file name component$'):
                    ControlTransport.worker_submit(self.binding, request_id=request_id, kind='submit_intent',
                                                   payload={'manifest': []})
                with self.assertRaisesRegex(ValueError, '^request_id must be a safe file name component$'):
                    ControlTransport.worker_receipt(self.binding, request_id)
        for self_check_id in invalid:
            with self.subTest(self_check_id=self_check_id):
                with self.assertRaisesRegex(ValueError, '^self_check_id must be a safe file name component$'):
                    self.transport.request_self_check(self.binding, request={
                        'self_check_id': self_check_id, 'execution_id': self.binding['execution_id'], 'payload': {}})
                with self.assertRaisesRegex(ValueError, '^self_check_id must be a safe file name component$'):
                    ControlTransport.worker_self_check(self.binding, self_check_id=self_check_id)

    def test_transport_id_cannot_load_a_binding_outside_the_transport_root(self):
        outside = self.root / 'outside'
        outside_endpoint = outside / 'endpoint'
        for name in ('inbox', 'outbox', 'worker-inbox', 'worker-outbox'):
            (outside_endpoint / name).mkdir(parents=True, exist_ok=True)
        malicious = deepcopy(self.binding)
        malicious.update(transport_id='../outside', endpoint=str(outside_endpoint))
        (outside / 'binding.json').write_text(json.dumps(malicious), encoding='utf-8')
        (outside_endpoint / 'state.json').write_text('{"state":"open"}', encoding='utf-8')
        request = {key: malicious[key] for key in BINDING_KEYS}
        request.update(request_id='safe-request', kind='submit_intent', payload={'manifest': []})
        published = []
        receipt = ControlTransport(self.root / 'transport', clock=self.clock).receive(
            request, publish=lambda value: published.append(value) or {
                'state': 'accepted', 'published': True, 'snapshot': 'outside-snapshot'})
        self.assertEqual(('rejected', 'transport_id must be a safe file name component'),
                         (receipt['state'], receipt['reason']))
        self.assertEqual([], published)
        self.assertFalse((outside_endpoint / 'outbox' / 'safe-request.json').exists())

    def test_pump_reads_only_open_transports_and_close_answers_a_raced_delivery(self):
        closed = self.transport.issue('EX-closed', 'GR-closed')
        raced = delivery(closed, 'raced')
        self.transport.close(closed, reason='execution ended')
        receipt = ControlTransport.worker_receipt(closed, 'raced')
        self.assertEqual((receipt['state'], receipt['reason']), ('closed', 'execution ended'))
        (Path(closed['endpoint']) / 'inbox' / 'late.json').write_text(json.dumps({**raced, 'request_id': 'late'}),
                                                                       encoding='utf-8')
        refuse = lambda _: self.fail("a closed transport's delivery must not publish")
        self.assertEqual(self.transport.pump(refuse), [])
        self.assertEqual(ControlTransport(self.root / 'transport', clock=self.clock).pump(refuse), [])
        self.assertIsNone(ControlTransport.worker_receipt(closed, 'late'))

    def test_open_transports_are_read_at_the_first_pump_not_at_construction(self):
        reads = {'is_open': control_transport._is_open, 'json': control_transport._json,
                 'shared': file_io.read_bytes_shared}
        with ObservedCalls(**reads) as constructing, file_access(self.root / 'transport') as seen:
            later = ControlTransport(self.root / 'transport', clock=self.clock)
        self.assertEqual({name: constructing.count(name) for name in reads}, dict.fromkeys(reads, 0))
        self.assertEqual(seen, [])
        # A transport issued and one closed through this object before its first pump.
        issued = later.issue('EX-later', 'GR-later')
        closed = later.issue('EX-closed', 'GR-closed')
        later.close(closed, reason='execution ended')
        for binding, request_id in ((self.binding, 'first-open'), (issued, 'second-open'), (closed, 'after-close')):
            delivery(binding, request_id)
        published = []
        later.pump(lambda request: published.append(request['request_id']) or {'state': 'rejected', 'reason': 'fixture'})
        self.assertEqual(sorted(published), ['first-open', 'second-open'])

    def test_request_id_rejected_without_engine_record_stays_taken_in_every_transport(self):
        # The engine records no receipt for an early rejection; the transport's outbox alone keeps the ID taken.
        delivery(self.binding, 'shared', payload={'draft_path': 'a.json'})
        self.transport.pump(lambda _: {'state': 'rejected', 'reason': 'execution is no longer running'})
        other = self.transport.issue('EX-other', 'GR-other')
        delivery(other, 'shared', payload={'draft_path': 'b.json'})
        # A new transport object has no memory of the first receipt; it must find it on disk.
        fresh = ControlTransport(self.root / 'transport', clock=self.clock)
        fresh.pump(lambda _: self.fail('a reused request ID must not reach the engine'))
        receipt = ControlTransport.worker_receipt(other, 'shared')
        self.assertEqual((receipt['state'], receipt['stage'], receipt['reason']),
                         ('rejected', 'delivery_validation', REUSED))

    def test_close_records_a_changed_redelivery_it_cannot_settle(self):
        ControlTransport.worker_submit(self.binding, request_id='changed', kind='submit_intent',
                                       payload={'manifest': ['first.json']})
        self.transport.pump(lambda _: {'state': 'rejected', 'reason': 'fixture'})
        path = self.endpoint / 'inbox' / 'changed.json'
        path.write_bytes(path.read_bytes().replace(b'first.json', b'other.json'))
        state = self.transport.close(self.binding, reason='execution ended')
        self.assertEqual(ControlTransport.worker_receipt(self.binding, 'changed')['reason'], 'fixture')
        stored = json.loads((self.endpoint / 'state.json').read_text(encoding='utf-8'))
        self.assertEqual(stored, state)
        self.assertEqual(stored['unsettled_deliveries'], [{'source': 'inbox/changed.json', 'reason': REUSED}])

    def test_final_delivery_is_not_reread_until_its_fingerprint_changes(self):
        ControlTransport.worker_submit(self.binding, request_id='cached', kind='submit_intent',
                                       payload={'manifest': ['first.json']})
        path = self.endpoint / 'inbox' / 'cached.json'
        settle(path)  # its times lie beyond the racy window, so its fingerprint may stand for its bytes
        with ObservedCalls(receive=ControlTransport.receive, decode=control_transport._decode_json) as calls:
            first = self.transport.pump(lambda _: {'state': 'rejected', 'reason': 'fixture'})
            self.assertEqual(calls.count('receive'), 1)
            decoded = calls.count('decode')  # the delivery and the transport files the first pump read
            self.assertEqual(self.transport.pump(lambda _: self.fail('must not republish')), first)
            # The cached final delivery is decoded no more: no transport JSON was decoded at all.
            self.assertEqual((calls.count('receive'), calls.count('decode')), (1, decoded), 'the final delivery was read again')
            path.write_bytes(path.read_bytes().replace(b'first.json', b'other.json'))
            settle(path)
            changed = self.transport.pump(lambda _: self.fail('changed identity must not publish'))
            self.assertEqual([(row['state'], row['reason']) for row in changed], [('rejected', REUSED)])
            self.assertTrue(changed[0]['redelivery_conflict'])
            import hashlib
            self.assertEqual(changed[0]['source_sha256'], hashlib.sha256(path.read_bytes()).hexdigest())
            evidence = list((self.endpoint/'outbox'/'delivery-rejections').glob('cached-*.json'))
            self.assertEqual(len(evidence), 1)
            self.assertEqual(json.loads(evidence[0].read_bytes()), changed[0])
            self.assertEqual(ControlTransport.worker_receipt(self.binding, 'cached'), first[0])
            self.assertEqual(self.transport.pump(lambda _: self.fail('must not republish')), changed)
            self.assertEqual(calls.count('receive'), 2)
        ControlTransport.worker_submit(self.binding, request_id='following', kind='submit_intent',
                                       payload={'manifest': ['normal.json']})
        received = {row['request_id']: row for row in self.transport.pump()}
        self.assertEqual(received['following']['state'], 'received')
        self.assertEqual(received['cached'], changed[0])
        self.assertEqual(ControlTransport.worker_receipt(self.binding, 'cached'), first[0])


class TransportReceiptTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.clock = FakeClock()

    def test_preview_cannot_be_misreported_as_accepted_publication(self):
        transport = ControlTransport(self.root, clock=self.clock)
        binding = transport.issue('EX-preview', 'GR-preview')
        request = {**binding, 'request_id': 'preview-1', 'kind': 'submission_preview', 'payload': {}}
        with self.assertRaisesRegex(ValueError, '^preview must return a check result without publication$'):
            transport.receive(request, publish=lambda _: {'state': 'accepted', 'published': True, 'snapshot': 'head'})
        self.assertIsNone(ControlTransport.worker_receipt(binding, 'preview-1'))

    def test_control_rejects_an_unconfirmed_boundary_and_request_id_reuse(self):
        transport = ControlTransport(self.root, clock=self.clock)
        capability = transport.issue('EX-1', 'GR-1')
        request = {**capability, 'request_id': 'CT-1', 'kind': 'safety_boundary', 'payload': {'inflight_calls': True}}
        first = transport.receive(request)
        self.assertEqual((first['state'], first['reason']), ('rejected', 'boundary report has an in-flight call'))
        self.assertEqual(transport.receive(request), first)
        with self.assertRaisesRegex(ValueError, '^' + REUSED + '$'):
            transport.receive({**request, 'payload': {'inflight_calls': False}})
        self.assertNotIn('capability', ControlTransport.worker_receipt(capability, 'CT-1'))

    def test_received_but_unpublished_request_is_published_on_recovery(self):
        transport = ControlTransport(self.root, clock=self.clock)
        binding = transport.issue('EX-receive', 'GR-receive')
        ControlTransport.worker_submit(binding, request_id='request-receive', kind='submit_intent',
                                       payload={'manifest': []})
        self.assertEqual([row['state'] for row in transport.pump()], ['received'])
        recovered = ControlTransport(self.root, clock=self.clock)
        calls = []

        def publish(request):
            calls.append(request)
            return {'state': 'accepted', 'published': True, 'snapshot': 'verified-CAS'}
        self.assertEqual([row['state'] for row in recovered.pump(publish)], ['accepted'])
        self.assertEqual([row['request_id'] for row in calls], ['request-receive'])




class WorkerInputBoundaryTests(unittest.TestCase):
    def test_worker_validation_rejects_new_negative_shapes_before_delivery(self):
        from do_math.control_protocol import SELF_CHECK_RESPONSE, SUBMIT_INTENT
        with tempfile.TemporaryDirectory() as directory:
            transport = ControlTransport(directory, clock=FakeClock())
            binding = transport.issue('EX-worker-input', 'GR-worker-input')
            endpoint = Path(binding['endpoint'])
            cases = [
                ('RQ-nul\0', SUBMIT_INTENT, {}, 'request_id must be NUL-free'),
                ('RQ-[glob]', SUBMIT_INTENT, {}, 'request_id must be a safe file name component'),
                ('RQ-kind', 'not-a-control-kind', {}, 'unsupported control kind'),
                ('RQ-payload', SUBMIT_INTENT, [], 'control payload must be an object'),
            ]
            from support.ingress import NOT_TEXTS
            cases += [(f'RQ-kind-{index}', kind, {}, 'unsupported control kind')
                      for index, kind in enumerate(NOT_TEXTS)]
            for request_id, kind, payload, reason in cases:
                with self.subTest(request_id=request_id):
                    with self.assertRaises(ValueError) as caught:
                        ControlTransport.worker_submit(binding, request_id=request_id, kind=kind, payload=payload)
                    self.assertEqual(str(caught.exception), reason)
                    self.assertEqual(list((endpoint / 'inbox').iterdir()), [])
                    self.assertEqual(list((endpoint / 'outbox').iterdir()), [])
            with self.assertRaisesRegex(ValueError, '^self-check response does not match its schema: '):
                ControlTransport.worker_submit(binding, request_id='RQ-response',
                    kind=SELF_CHECK_RESPONSE, payload={'response': {}})
            with self.assertRaisesRegex(ValueError, '^unknown self-check request$'):
                ControlTransport.worker_self_check(binding, self_check_id='SC-absent', response={})
            self.assertEqual(list((endpoint / 'inbox').iterdir()), [])
            self.assertEqual(list((endpoint / 'outbox').iterdir()), [])
            delivered = ControlTransport.worker_submit(binding, request_id='RQ-after-errors',
                kind=SUBMIT_INTENT, payload={'draft_path': 'output.json'})
            self.assertEqual(delivered, {'request_id': 'RQ-after-errors', 'state': 'submitted'})
            receipt, = transport.pump()
            self.assertEqual((receipt['request_id'], receipt['state']), ('RQ-after-errors', 'received'))
            self.assertNotIn('snapshot', receipt)
            self.assertEqual(ControlTransport.worker_receipt(binding, 'RQ-after-errors'), receipt)

    def test_memory_transport_cannot_offer_file_worker_operations(self):
        from do_math.control_server import mcp_server_config
        clock = FakeClock()
        transport = ControlTransport(clock=clock)
        binding = transport.issue('EX-memory-only', 'GR-memory-only')
        for operation, reason in [
            (transport.pump, 'a memory-only transport has no inbox to pump'),
            (lambda: mcp_server_config(binding), 'file transport binding lacks an MCP endpoint'),
            (lambda: ControlTransport.worker_receipt(binding, 'RQ-none'), 'transport binding has no file endpoint'),
            (lambda: transport.receive([]), 'control request must be an object'),
            (lambda: transport.issue('EX-bad\0', 'GR-memory-only'), 'execution_id must be NUL-free'),
        ]:
            with self.subTest(reason=reason):
                with self.assertRaises(ValueError) as caught:
                    operation()
                self.assertEqual(str(caught.exception), reason)
        self.assertNotIn('endpoint', binding)

    def test_unknown_capability_rejection_does_not_write_to_the_other_transport(self):
        from do_math.control_protocol import SUBMIT_INTENT
        with tempfile.TemporaryDirectory() as directory:
            clock = FakeClock()
            owner = ControlTransport(Path(directory) / 'owner', clock=clock)
            binding = owner.issue('EX-foreign', 'GR-foreign')
            ControlTransport.worker_submit(binding, request_id='RQ-foreign', kind=SUBMIT_INTENT,
                                           payload={'draft_path': 'output.json'})
            path = Path(binding['endpoint']) / 'inbox' / 'RQ-foreign.json'
            raw = path.read_bytes()
            request = json.loads(raw)
            for receiver in (ControlTransport(clock=clock),
                             ControlTransport(Path(directory) / 'unrelated', clock=clock)):
                receipt = receiver.receive(request)
                self.assertEqual((receipt['state'], receipt['reason']),
                                 ('rejected', 'unknown transport capability'))
                self.assertEqual(receiver.receive(request), receipt)
                self.assertIsNone(ControlTransport.worker_receipt(binding, 'RQ-foreign'))
                self.assertEqual(path.read_bytes(), raw)
            own, = owner.pump()
            self.assertEqual(own['state'], 'received')
            self.assertEqual(own['execution_id'], binding['execution_id'])
            self.assertNotIn('snapshot', own)

    def test_restarted_receiver_rejects_an_unissued_self_check_without_losing_its_bytes(self):
        from do_math.control_protocol import SELF_CHECK_RESPONSE, SUBMIT_INTENT
        with tempfile.TemporaryDirectory() as directory:
            clock = FakeClock()
            owner = ControlTransport(directory, clock=clock)
            binding = owner.issue('EX-issued', 'GR-issued', self_check=True)
            request_id = 'RQ-unissued'
            ControlTransport.worker_submit(binding, request_id=request_id, kind=SUBMIT_INTENT,
                                           payload={'draft_path': 'output.json'})
            path = Path(binding['endpoint']) / 'inbox' / (request_id + '.json')
            malformed = json.loads(path.read_bytes())
            # Intentional external negative: bypass the worker's answer check, never fabricate an issued obligation.
            malformed.update(kind=SELF_CHECK_RESPONSE, payload={'self_check_id': 'SC-never-issued', 'response': {}})
            raw = json.dumps(malformed, sort_keys=True).encode('utf-8')
            path.write_bytes(raw)
            recovered = ControlTransport(directory, clock=clock)
            receipt, = recovered.pump()
            self.assertEqual((receipt['state'], receipt['reason']),
                             ('rejected', 'self-check response has no issued request'))
            self.assertEqual(path.read_bytes(), raw)
            self.assertEqual(ControlTransport.worker_receipt(binding, request_id), receipt)
            self.assertEqual(ControlTransport(directory, clock=clock).pump(), [receipt])
            self.assertEqual(list((Path(binding['endpoint']) / 'worker-inbox').iterdir()), [])


class DeliveryRecoveryTests(unittest.TestCase):
    def test_bad_delivery_filename_is_rejected_without_blocking_the_next_file(self):
        import hashlib
        with tempfile.TemporaryDirectory() as directory:
            transport = ControlTransport(directory, clock=FakeClock())
            binding = transport.issue('EX-filename', 'GR-filename')
            endpoint = Path(binding['endpoint'])
            path = endpoint / 'inbox' / 'RQ-[broken].json'
            raw = b'[]'
            path.write_bytes(raw)
            ControlTransport.worker_submit(binding, request_id='RQ-following', kind='submit_intent', payload={})
            rows = {row['request_id']: row for row in transport.pump()}
            rejected = rows[path.stem]
            self.assertEqual(rejected, {'request_id': path.stem, 'state': 'rejected',
                'stage': 'delivery_validation', 'reason': f'transport file {path} is not an object',
                'source': 'inbox/' + path.name, 'source_sha256': hashlib.sha256(raw).hexdigest(),
                'source_bytes': len(raw)})
            self.assertEqual(rows['RQ-following']['state'], 'received')
            self.assertEqual(json.loads((endpoint / 'outbox' / path.name).read_bytes()), rejected)
            self.assertEqual(path.read_bytes(), raw)
            # The malformed filename is a file coordinate, never a valid worker request ID.
            with self.assertRaisesRegex(ValueError, '^request_id must be a safe file name component$'):
                ControlTransport.worker_receipt(binding, path.stem)
            fresh = ControlTransport(directory, clock=transport.clock)
            self.assertEqual({row['request_id']: row for row in fresh.pump()}, rows)

    def test_rewritten_rejection_after_restart_does_not_starve_a_later_worker_delivery(self):
        """An immutable rejection and a later valid worker both survive receiver restart."""
        from do_math.control_protocol import SUBMIT_INTENT
        with tempfile.TemporaryDirectory() as directory:
            clock = FakeClock()
            transport = ControlTransport(directory, clock=clock)
            binding = transport.issue('EX-redelivery', 'GR-redelivery')
            endpoint = Path(binding['endpoint'])
            bad = endpoint / 'inbox' / 'RQ-0-corrupt.json'
            bad.write_bytes(b'\xff')
            first, = transport.pump()
            self.assertEqual((first['state'], first['stage']), ('rejected', 'delivery_validation'))
            self.assertEqual(first['source_bytes'], 1)
            bad.write_bytes(b'[]')  # a different intentionally malformed external envelope
            ControlTransport.worker_submit(binding, request_id='RQ-1-worker', kind=SUBMIT_INTENT,
                                           payload={'draft_path': 'output.json'})
            recovered = ControlTransport(directory, clock=clock)
            receipts = {row['request_id']: row for row in recovered.pump()}
            self.assertEqual(receipts['RQ-0-corrupt'], first)
            self.assertEqual(receipts['RQ-1-worker']['state'], 'received')
            self.assertEqual(ControlTransport.worker_receipt(binding, 'RQ-0-corrupt'), first)
            self.assertEqual(ControlTransport.worker_receipt(binding, 'RQ-1-worker'), receipts['RQ-1-worker'])
            self.assertEqual(bad.read_bytes(), b'[]')


class IssuedSelfCheckTransportTests(unittest.TestCase):
    def test_issued_request_replay_conflicts_and_closed_delivery_keep_the_original_notice(self):
        from do_math.observations import ObservationTracker
        from support.observation_inputs import observation_rule, write_checkpoint
        with tempfile.TemporaryDirectory() as directory:
            clock = FakeClock()
            workspace = Path(directory) / 'workspace'
            workspace.mkdir()
            tracker = ObservationTracker('EX-self-check', workspace, {
                'observation_rules': [observation_rule(required_evidence=['workspace:checkpoint.json'])],
                'self_check_response_window_seconds': 5, 'tool_review_window_seconds': 60},
                time_port=clock)
            write_checkpoint(workspace, counters={'attempts': 2})
            # A receipt-time tick at an empty stream is the same input the live runner emits while idle.
            emitted = tracker.observe({'type': 'tick'}, source={'stream': 'stdout.jsonl',
                'start_offset': 0, 'end_offset': 0, 'received_at': clock.now(),
                'received_monotonic': clock.monotonic()})
            obligation, = [row for row in emitted if row['kind'] == 'self_check_due']
            issued = tracker.issue_self_check(obligation['id'])
            transport = ControlTransport(Path(directory) / 'transport', clock=clock)
            binding = transport.issue(tracker.execution_id, 'GR-self-check', workspace=workspace, self_check=True)
            delivered = transport.request_self_check(binding, request=issued)
            self.assertEqual(delivered, issued)
            endpoint = Path(binding['endpoint'])
            notice = endpoint / 'worker-inbox' / (issued['self_check_id'] + '.json')
            surface = workspace / '.control' / 'self-checks' / notice.name
            originals = (notice.read_bytes(), surface.read_bytes())
            self.assertEqual(transport.request_self_check(binding, request=issued), issued)
            self.assertEqual((notice.read_bytes(), surface.read_bytes()), originals)
            self.assertEqual(ControlTransport.worker_self_check(binding, self_check_id=issued['self_check_id']), issued)
            for invalid in ([], {**issued, 'execution_id': 'EX-other'}, {**issued, 'payload': []}):
                with self.subTest(invalid=invalid):
                    with self.assertRaisesRegex(ValueError, "^self-check request must be this execution's exact issued request$"):
                        transport.request_self_check(binding, request=invalid)
                    self.assertEqual((notice.read_bytes(), surface.read_bytes()), originals)
            changed = deepcopy(issued)
            changed['payload']['unexpected_negative_field'] = True
            with self.assertRaisesRegex(ValueError, '^self_check_id was reused with different content$'):
                transport.request_self_check(binding, request=changed)
            self.assertEqual((notice.read_bytes(), surface.read_bytes()), originals)
            # Only this external delivery surface is corrupted; the tracker's issued request stays intact.
            surface.write_bytes(b'{}')
            with self.assertRaisesRegex(ValueError, '^workspace self-check notice differs from its issued request$'):
                transport.request_self_check(binding, request=issued)
            self.assertEqual(notice.read_bytes(), originals[0])
            self.assertEqual(surface.read_bytes(), b'{}')
            transport.close(binding, reason='owner ended execution')
            with self.assertRaisesRegex(ValueError, '^a closed transport cannot request a self-check$'):
                transport.request_self_check(binding, request=issued)
            self.assertEqual(notice.read_bytes(), originals[0])
            # A workspace-less transport has only its worker inbox; it is not a new authority.
            bare = transport.issue(tracker.execution_id, 'GR-self-check', self_check=True)
            self.assertEqual(transport.request_self_check(bare, request=issued), issued)
            self.assertEqual(ControlTransport.worker_self_check(bare, self_check_id=issued['self_check_id']), issued)
            self.assertEqual(list((endpoint / 'outbox').iterdir()), [])
if __name__ == '__main__':
    unittest.main()
