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


if __name__ == '__main__':
    unittest.main()
