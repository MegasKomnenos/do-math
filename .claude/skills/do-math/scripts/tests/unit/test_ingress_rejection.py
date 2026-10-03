"""The control actions' check rejects every malformed shape in its own form (의무 2-A, layer 2).

For every public control action and every wrong shape its payload schema makes
(``support.ingress.malformed``), and for a text that is not a string, the check
``control_contracts.validate_control_payload`` raises ``ValueError``. Another
exception would escape the owner loop's rejection (조사 범주 2: an input the loop
cannot reject stops the instance); an accepted shape would mean the check is
weaker than its own schema.
"""
import unittest

from support.ingress import NOT_TEXTS, control_actions, malformed


class ControlPayloadRejectionTests(unittest.TestCase):
    def test_every_malformed_payload_and_text_is_rejected_with_value_error(self):
        from do_math.control_contracts import validate_control_payload
        cases = 0
        for action, schema in sorted(control_actions().items()):
            shapes = [('config ' + label, '', config, r'^config(/\S+)?: invalid ') for label, config in malformed(schema)]
            shapes += [('text ' + repr(text), text, {}, '^control text must be a string$') for text in NOT_TEXTS]
            for label, text, config, reason in shapes:
                cases += 1
                with self.subTest(action=action, shape=label), self.assertRaisesRegex(ValueError, reason):
                    validate_control_payload(action, text, config)
        self.assertGreater(cases, 100)

    def test_an_unknown_action_is_rejected_with_value_error(self):
        from do_math.control_contracts import validate_control_payload
        for action in ('', 'unknown', None, 0):
            with self.subTest(action=action), self.assertRaisesRegex(ValueError, '^unknown control action$'):
                validate_control_payload(action, '', {})



class TransportDeliveryTests(unittest.TestCase):
    """The control transport's delivery files (의무 2-A): a damaged file gets one rejection receipt and the pump goes on."""

    def setUp(self):
        import tempfile
        from pathlib import Path
        from do_math.control_transport import ControlTransport
        from support.fakes.clock import FakeClock
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.transport = ControlTransport(Path(directory.name) / 'control', clock=FakeClock())
        self.binding = self.transport.issue('EX-01M3HM0X0000000000000000AB', 'GR-ingress', workspace=directory.name)
        self.inbox = Path(self.binding['endpoint']) / 'inbox'

    def deliver(self, name, raw):
        (self.inbox / (name + '.json')).write_bytes(raw)

    def states(self):
        return {receipt['request_id']: receipt['state'] for receipt in self.transport.pump()}

    def test_damaged_deliveries_are_rejected_once_and_a_valid_request_is_still_received(self):
        import json
        from do_math.control_transport import ControlTransport
        valid = {key: self.binding[key] for key in ('transport_id', 'capability', 'execution_id', 'grant_id')}
        damaged = {'RQ-bad-json': b'{not json', 'RQ-list': b'[]', 'RQ-no-id': b'{}',
                   'RQ-wrong-capability': json.dumps({**valid, 'capability': 'x' * 43, 'request_id': 'RQ-wrong-capability',
                                                      'kind': 'submit_intent', 'payload': {'draft_path': 'o.json'}}).encode()}
        for name, raw in damaged.items():
            self.deliver(name, raw)
        first = self.states()
        self.assertEqual({name: first[name] for name in damaged}, dict.fromkeys(damaged, 'rejected'))
        self.assertEqual(self.states(), first, 'a second pass reports the same receipts and receives nothing twice')
        ControlTransport.worker_submit(self.binding, request_id='RQ-valid', kind='submit_intent',
                                       payload={'draft_path': 'output.json'})
        self.assertEqual(self.states()['RQ-valid'], 'received')

    def test_a_delivery_rewritten_under_a_rejected_request_id_is_rejected(self):
        self.deliver('RQ-reused', b'{not json')
        self.assertEqual(self.states()['RQ-reused'], 'rejected')
        self.deliver('RQ-reused', b'[1]')
        self.assertEqual(self.states()['RQ-reused'], 'rejected')


if __name__ == '__main__':
    unittest.main()
