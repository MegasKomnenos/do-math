"""Receipt publication and delivery races through the real control transport.

Only filesystem calls are controlled at their external boundary; request
validation, publication checks, durable receipts and close all run unchanged.
"""
import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from do_math.control_transport import ControlTransport
from support.fakes.clock import FakeClock


class PublisherTests(unittest.TestCase):
    def test_invalid_publisher_decisions_never_become_final_receipts(self):
        transport = ControlTransport(clock=FakeClock())
        binding = transport.issue('EX-publication', 'GR-publication')
        for index, (kind, decision, reason) in enumerate((
            ('submission_preview', {'state': 'previewed', 'result': []},
             'previewed receipt requires a structured check result'),
            ('submit_intent', None, 'transport publisher must return accepted or rejected'),
            ('submit_intent', {'state': 'received'}, 'transport publisher must return accepted or rejected'),
            ('submit_intent', {'state': 'accepted', 'published': False, 'snapshot': 'head'},
             'accepted receipt requires a published authoritative snapshot'),
            ('submit_intent', {'state': 'accepted', 'published': True, 'snapshot': ''},
             'accepted receipt requires a published authoritative snapshot'),
            ('submit_intent', {'state': 'accepted', 'published': True, 'snapshot': 7},
             'accepted receipt requires a published authoritative snapshot'),
        )):
            request = {**binding, 'request_id': f'RQ-{index}', 'kind': kind, 'payload': {}}
            with self.subTest(decision=decision):
                with self.assertRaises(ValueError) as caught:
                    transport.receive(request, publish=lambda _: decision)
                self.assertEqual(str(caught.exception), reason)
                # The same request can still be processed after the bad publisher is fixed.
                valid = ({'state': 'previewed', 'result': {'valid': True}} if kind == 'submission_preview'
                         else {'state': 'accepted', 'published': True, 'snapshot': 'authoritative-head'})
                receipt = transport.receive(request, publish=lambda _: valid)
                self.assertEqual(receipt['state'], valid['state'])
                self.assertEqual(receipt['request_sha256'], hashlib.sha256(
                    json.dumps(request, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()).hexdigest())
                self.assertEqual(transport.receive(request, publish=lambda _: self.fail('must not publish twice')), receipt)


class DeliveryRaceTests(unittest.TestCase):
    def setUp(self):
        root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.transport = ControlTransport(root, clock=FakeClock())
        self.binding = self.transport.issue('EX-race', 'GR-race')
        self.endpoint = Path(self.binding['endpoint'])

    def deliver(self, request_id):
        ControlTransport.worker_submit(self.binding, request_id=request_id, kind='submit_intent', payload={})
        return self.endpoint / 'inbox' / (request_id + '.json')

    def test_disappearing_delivery_does_not_block_the_following_request(self):
        for phase in ('stat', 'open'):
            with self.subTest(phase=phase):
                path = self.deliver('RQ-' + phase)
                following = self.deliver('RQ-following-' + phase)
                original_stat, original_open = os.stat, Path.open
                removed = []

                def stat(target, *args, **kwargs):
                    if phase == 'stat' and Path(target) == path and not removed:
                        path.unlink()
                        removed.append(phase)
                    return original_stat(target, *args, **kwargs)

                def opened(target, *args, **kwargs):
                    if phase == 'open' and target == path and not removed:
                        path.unlink()
                        removed.append(phase)
                    return original_open(target, *args, **kwargs)

                with patch('os.stat', stat), patch.object(Path, 'open', opened):
                    rows = self.transport.pump()
                self.assertEqual(removed, [phase])
                self.assertFalse(path.exists())
                self.assertIsNone(ControlTransport.worker_receipt(self.binding, path.stem))
                by_id = {row['request_id']: row for row in rows}
                self.assertEqual(by_id[following.stem]['state'], 'received')
                self.assertEqual(ControlTransport.worker_receipt(self.binding, following.stem), by_id[following.stem])

    def test_link_publication_survives_temporary_name_disappearing(self):
        original = os.link
        published = []

        def link(source, destination, *args, **kwargs):
            result = original(source, destination, *args, **kwargs)
            Path(source).unlink()
            published.append(Path(destination))
            return result

        with patch('os.link', link):
            result = ControlTransport.worker_submit(self.binding, request_id='RQ-link', kind='submit_intent', payload={})
        path, = published
        self.assertEqual(result, {'request_id': 'RQ-link', 'state': 'submitted'})
        self.assertEqual(json.loads(path.read_bytes())['request_id'], 'RQ-link')
        self.assertEqual(list(path.parent.glob('*.tmp')), [])
        receipt, = self.transport.pump()
        self.assertEqual(receipt['state'], 'received')

    def test_unreadable_state_is_rejected_by_the_receipt_and_preserves_delivery(self):
        path = self.deliver('RQ-state')
        raw = path.read_bytes()
        (self.endpoint / 'state.json').write_bytes(b'[]')
        recovered = ControlTransport(self.transport.root, clock=self.transport.clock)
        receipt, = recovered.pump()
        self.assertEqual((receipt['state'], receipt['stage']), ('rejected', 'delivery_validation'))
        self.assertEqual(receipt['reason'], f'transport file {self.endpoint / "state.json"} is not an object')
        self.assertEqual(receipt['source_sha256'], hashlib.sha256(raw).hexdigest())
        self.assertEqual(path.read_bytes(), raw)
        self.assertEqual(ControlTransport.worker_receipt(self.binding, path.stem), receipt)

    def test_close_records_a_corrupt_existing_receipt_without_replacing_it(self):
        path = self.endpoint / 'inbox/RQ-broken.json'
        outbox = self.endpoint / 'outbox/RQ-broken.json'
        path.write_bytes(b'[]')
        outbox.write_bytes(b'[]')
        state = self.transport.close(self.binding, reason='owner ended')
        self.assertEqual(state, {'state': 'closed', 'reason': 'owner ended', 'unsettled_deliveries': [
            {'source': 'inbox/RQ-broken.json', 'reason': f'transport file {outbox} is not an object'}]})
        self.assertEqual(json.loads((self.endpoint / 'state.json').read_bytes()), state)
        self.assertEqual((path.read_bytes(), outbox.read_bytes()), (b'[]', b'[]'))
        self.assertEqual(self.transport.pump(), [])

    def test_disappearing_rejection_is_reported_as_a_publication_failure(self):
        path = self.endpoint / 'inbox/RQ-missing-receipt.json'
        path.write_bytes(b'[]')
        outbox = self.endpoint / 'outbox' / path.name
        outbox.write_bytes(b'{}')
        original = os.link

        def link(source, destination, *args, **kwargs):
            if Path(destination) == outbox:
                outbox.unlink()
                raise FileExistsError('another publisher claimed the receipt before it disappeared')
            return original(source, destination, *args, **kwargs)

        with patch('os.link', link), self.assertRaisesRegex(RuntimeError, '^delivery rejection disappeared after publication$'):
            self.transport.pump()
        self.assertEqual(path.read_bytes(), b'[]')
        self.assertFalse(outbox.exists())
