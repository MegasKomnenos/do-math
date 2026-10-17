"""The control inbox consumes a rejected item once and keeps working (의무 2-A, layer 3).

A malformed item reaches the inbox when a file is damaged or written by another
edition, so the cases bypass the public submit check: each is a real inbox file
(the envelope ``control`` writes) with one part changed. After an owner pass
the item is consumed exactly once (its ID, or its file name when the envelope
is broken, is processed and one rejection is recorded, also after a second
pass), the pass raised nothing, and a valid pause after it is applied.
"""
from copy import deepcopy
import json
import base64
from pathlib import Path
import unittest

from support.ingress import control_actions, malformed
from support.sim import Sim, warm_template

setUpModule = warm_template


def _inbox(sim):
    return Path(sim.instance['workspace']) / 'control' / sim.instance_id


def _envelope(sim):
    """The envelope ``control`` writes for a valid request, taken from a real inbox file and then removed."""
    request = sim.control('pause', text='envelope template')
    path = _inbox(sim) / (request['request_id'] + '.json')
    envelope = json.loads(path.read_bytes())
    path.unlink()
    return envelope


def _rejections(sim, name):
    return [row for row in sim.runtime['history']
            if row.get('kind') == 'rejected_user_control' and row.get('request', {}).get('id') == name]


class ControlInboxConsumptionTests(unittest.TestCase):
    """About 7 s and 12 s, over the 2 s Sim budget: each case is a real owner pass over the inbox."""

    def assert_consumed_once_and_the_loop_continues(self, sim, cases):
        for name, raw, reason in cases:
            with self.subTest(case=name):
                (_inbox(sim) / (name + '.json')).write_bytes(raw)
                before_instance, before = deepcopy(sim.instance), deepcopy(sim.runtime)
                sim.engine.process_controls()
                first_head = sim.engine.head
                sim.engine.process_controls()
                self.assertEqual(sim.engine.head, first_head)
                _, instance, stored = sim.engine.store.load()
                self.assertEqual(instance, before_instance)
                self.assertEqual(stored['processed_controls'], [*before['processed_controls'], name])
                delta = stored['history'][len(before['history']):]
                self.assertEqual(len(delta), 1)
                self.assertEqual((delta[0]['kind'], delta[0]['reason']), ('rejected_user_control', reason))
                self.assertEqual(sim.engine.control_result(name)['reason'], reason)
                for field in set(before) - {'history', 'processed_controls', 'updated_at', 'last_observed_utc'}:
                    self.assertEqual(stored[field], before[field], field)
                self.assertEqual((_inbox(sim) / (name + '.json')).read_bytes(), raw)
        rejected_state = deepcopy((sim.instance, sim.runtime, sim.engine.head))
        sim.restart()
        sim.engine.process_controls()
        self.assertEqual((sim.instance, sim.runtime, sim.engine.head), rejected_state)
        normal = sim.control('pause', text='after the rejected items')
        sim.engine.process_controls()
        self.assertEqual(sim.runtime['status'], 'paused')
        self.assertEqual(sim.engine.control_result(normal['request_id'])['effect'], 'applied')
        sim.restart()
        sim.engine.process_controls()
        self.assertEqual(sim.runtime['status'], 'paused')
        self.assertEqual(sim.runtime['processed_controls'].count(normal['request_id']), 1)
        self.assertEqual(sim.model.calls, [])

    def test_each_action_rejects_a_malformed_payload_once(self):
        sim = Sim.activated()
        envelope = _envelope(sim)
        cases = []
        for index, (action, schema) in enumerate(sorted(control_actions().items())):
            label, config = malformed(schema)[0]
            name = f'RQ-ingress-{index:02d}'
            request = {**deepcopy(envelope), 'id': name, 'action': action, 'config': config,
                       'accepted_order': envelope['accepted_order'] + f'.{index:02d}'}
            cases.append((name, json.dumps(request).encode(), 'config: invalid type (expected object)'))
        self.assert_consumed_once_and_the_loop_continues(sim, cases)

    def test_a_broken_envelope_is_rejected_once(self):
        sim = Sim.activated()
        envelope = _envelope(sim)
        broken = {
            'RQ-ingress-json': b'{not json',
            'RQ-ingress-encoding': b'\xff',
            'RQ-ingress-list': b'[]',
            'RQ-ingress-other-id': json.dumps({**envelope, 'id': 'RQ-someone-else'}).encode(),
            'RQ-ingress-other-instance': json.dumps({**envelope, 'id': 'RQ-ingress-other-instance',
                                                     'instance_id': 'RI-00000000000000000000000000'}).encode(),
            'RQ-ingress-no-order': json.dumps({key: value for key, value in {**envelope, 'id': 'RQ-ingress-no-order'}.items()
                                               if key != 'accepted_order'}).encode(),
            'RQ-ingress-no-action': json.dumps({key: value for key, value in {**envelope, 'id': 'RQ-ingress-no-action'}.items()
                                                if key != 'action'}).encode(),
        }
        reasons = {
            'RQ-ingress-json': 'Expecting property name enclosed in double quotes: line 1 column 2 (char 1)',
            'RQ-ingress-encoding': "'utf-8' codec can't decode byte 0xff in position 0: invalid start byte",
            'RQ-ingress-list': 'control identity mismatch',
            'RQ-ingress-other-id': 'control identity mismatch',
            'RQ-ingress-other-instance': 'control identity mismatch',
            'RQ-ingress-no-order': 'control ordering envelope is invalid',
            'RQ-ingress-no-action': 'control action envelope is invalid',
        }
        self.assert_consumed_once_and_the_loop_continues(sim,
            [(name, raw, reasons[name]) for name, raw in broken.items()])
        for name, raw in broken.items():
            row, = _rejections(sim, name)
            self.assertEqual(row['request']['origin'], 'untrusted_file')
            self.assertEqual(base64.b64decode(row['request']['source']['base64']), raw)
        before = deepcopy(sim.runtime)
        sim.restart()
        sim.engine.process_controls()
        self.assertEqual(sim.runtime['processed_controls'], before['processed_controls'])
        self.assertEqual(sim.runtime['history'], before['history'])


if __name__ == '__main__':
    unittest.main()
