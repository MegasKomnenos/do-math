"""Invalid control input is rejected at its boundary without blocking later controls (``engine.control``, the owner's inbox).

Each test starts from a publicly initialized instance on the Sim
(``support.engine_gates.initialized_sim``). The public ``control`` checks a
request's shape before it writes the inbox; a request that reaches the inbox
anyway (a damaged or foreign file) is consumed once by the owner, rejected with
the shape check's reason, and later requests are still applied. The legacy
tests ran on a repository ``git_init`` made and the real Git process; the
engine, its store and its inbox are the product's here too, on the Sim's ports.
"""
from copy import deepcopy
import json
import re
import unittest

from do_math.canonical import canonical_json
from support.engine_gates import initialized_sim
from support.engine_shapes import ACTIONS, BAD_PAYLOADS, NOT_OBJECT, NOT_OBJECTS, inbox


def exactly(reason):
    return '^' + re.escape(reason) + '$'


class ControlShapeBoundaryTests(unittest.TestCase):
    def test_all_public_actions_reject_nonobject_config_without_creating_inbox(self):
        sim = initialized_sim()
        self.assertEqual(list(inbox(sim).glob('*.json')), [])
        for action in ACTIONS:
            for value in NOT_OBJECTS:
                with self.subTest(action=action, value=value), self.assertRaisesRegex(ValueError, exactly(NOT_OBJECT)):
                    sim.control(action, config=value, text='input')
        self.assertEqual(list(inbox(sim).glob('*.json')), [])

    def test_nested_shapes_are_rejected_before_publication(self):
        sim = initialized_sim()
        for action, config, reason in BAD_PAYLOADS:
            with self.subTest(action=action, config=config), self.assertRaisesRegex(ValueError, exactly(reason)):
                sim.control(action, config=config)
        self.assertEqual(list(inbox(sim).glob('*.json')), [])

    def test_receiver_rejects_bad_payload_once_then_processes_following_valid_control(self):
        sim = initialized_sim()
        bad = {}
        for index, (action, config, reason) in enumerate([('pause', [1], NOT_OBJECT), *BAD_PAYLOADS]):
            identifier = 'UC-invalid-' + str(index)
            sim.control('pause', request_id=identifier)
            path = inbox(sim) / (identifier + '.json')
            request = json.loads(path.read_bytes())
            request.update(action=action, config=deepcopy(config))
            path.write_bytes(canonical_json(request))  # a damaged inbox file: the public check never saw it
            bad[identifier] = reason
        sim.control('pause', text='valid later request', request_id='UC-good')
        sim.restart()
        sim.engine.process_controls()
        for identifier, reason in bad.items():
            with self.subTest(request=identifier):
                self.assertEqual(sim.runtime['processed_controls'].count(identifier), 1)
                result = sim.engine.control_result(identifier)
                self.assertEqual(result['effect'], 'rejected')
                self.assertEqual(result['reason'], reason)
        self.assertEqual(sim.engine.control_result('UC-good')['effect'], 'applied')
        self.assertEqual(sim.runtime['status'], 'paused')
        sim.restart()
        sim.engine.process_controls()
        self.assertEqual({identifier: sim.runtime['processed_controls'].count(identifier) for identifier in bad},
                         dict.fromkeys(bad, 1))

    def test_out_of_range_lease_is_rejected_without_blocking_later_control(self):
        sim = initialized_sim()
        sim.control('conversation', request_id='UC-lease', config={
            'operation': 'attach', 'id': 'conversation', 'generation': 1,
            'disconnect_policy': 'pause', 'lease_seconds': (1 << 53) - 1})
        sim.control('pause', request_id='UC-after-lease')
        sim.restart()
        sim.engine.process_controls()
        rejected = sim.engine.control_result('UC-lease')
        self.assertEqual(rejected['effect'], 'rejected')
        self.assertEqual(rejected['reason'], 'conversation lease exceeds the supported timestamp range')
        self.assertEqual(sim.engine.control_result('UC-after-lease')['effect'], 'applied')


if __name__ == '__main__':
    unittest.main()
