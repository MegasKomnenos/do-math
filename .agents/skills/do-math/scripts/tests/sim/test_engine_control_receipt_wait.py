"""Receipts a worker reads back through its receipt wait (``control_server.wait_receipt``, layer 3) and the transport.

No engine runs: these check the product's transport (layer 2) over real files,
and also what a worker reads with ``wait_receipt``, which is layer 3, so they
sit with the layer-3 tests (the other transport tests are in
``unit/test_engine_control_transport.py``). A zero wait reads the stored receipt
once; the fake clock port draws the transport tokens.
"""
import hashlib
from pathlib import Path
import tempfile
import unittest

from do_math.control_server import wait_receipt
from do_math.control_transport import ControlTransport
from support.fakes.clock import FakeClock

DIFFERENT_RECEIPT = 'request_id was already received with different content'


class ReceiptWaitTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)

    def test_malformed_request_has_queryable_rejection_and_preserves_source(self):
        transport = ControlTransport(self.root / 'transport', clock=FakeClock())
        binding = transport.issue('EX-transport', 'GR-transport')
        request_id = 'malformed-one'
        source = Path(binding['endpoint']) / 'inbox' / (request_id + '.json')
        raw = b'{"request_id":'
        source.write_bytes(raw)
        results = transport.pump(lambda _: self.fail('malformed input must not publish'))
        self.assertEqual(1, len(results))
        receipt = results[0]
        self.assertEqual(('rejected', 'delivery_validation'), (receipt['state'], receipt['stage']))
        self.assertEqual(hashlib.sha256(raw).hexdigest(), receipt['source_sha256'])
        self.assertEqual('inbox/' + request_id + '.json', receipt['source'])
        self.assertRegex(receipt['reason'], r'^transport file .*malformed-one\.json is not valid UTF-8 JSON: ')
        self.assertEqual(raw, source.read_bytes())
        self.assertEqual(receipt, ControlTransport.worker_receipt(binding, request_id))
        self.assertEqual(receipt, wait_receipt(binding, request_id, 0))
        self.assertEqual(receipt, transport.pump(lambda _: self.fail('replay must not publish'))[0])
        source.write_bytes(b'{"different":')
        with self.assertRaisesRegex(ValueError, '^' + DIFFERENT_RECEIPT + '$'):
            transport.pump(lambda _: self.fail('changed malformed input must not publish'))
        self.assertEqual(receipt, ControlTransport.worker_receipt(binding, request_id))

    def test_preview_is_replayable_but_never_a_publication_receipt(self):
        clock = FakeClock()
        transport = ControlTransport(self.root, clock=clock)
        binding = transport.issue('EX-preview', 'GR-preview')
        ControlTransport.worker_submit(binding, request_id='preview-1', kind='submission_preview',
                                       payload={'output_sha256': 'a' * 64})
        calls = []

        def inspect(request):
            calls.append(request)
            return {'state': 'previewed', 'result': {'valid': True, 'snapshot': 'checked-snapshot'}}
        receipt = transport.pump(inspect)[0]
        self.assertEqual(receipt['state'], 'previewed')
        self.assertEqual(receipt['result'], {'valid': True, 'snapshot': 'checked-snapshot'})
        self.assertNotIn('publication_id', receipt)
        self.assertNotIn('snapshot', receipt)
        self.assertEqual(wait_receipt(binding, 'preview-1', 0), receipt)
        self.assertEqual(ControlTransport(self.root, clock=clock).pump(lambda _: self.fail('duplicate preview'))[0],
                         receipt)
        self.assertEqual([request['request_id'] for request in calls], ['preview-1'])


if __name__ == '__main__':
    unittest.main()
