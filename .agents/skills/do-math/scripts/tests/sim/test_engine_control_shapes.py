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




class ControlAdmissionTests(unittest.TestCase):
    def test_receiver_refuses_damaged_normalized_source_bytes_and_keeps_the_next_request(self):
        from do_math.control_contracts import normalized_source
        sim = initialized_sim()
        identifier = 'UC-damaged-source'
        sim.control('source', config=normalized_source('bad.txt', b'original'), request_id=identifier)
        path = inbox(sim) / (identifier + '.json')
        request = json.loads(path.read_bytes())
        request['config']['bytes'] += 1
        path.write_bytes(canonical_json(request))
        good = sim.control('source', config=normalized_source('good.txt', b'after rejection'))
        sim.engine._apply_inbox(pump=False)
        rejected = sim.engine.control_result(identifier)
        self.assertEqual((rejected['effect'], rejected['reason']),
                         ('rejected', 'source bytes differ from their declared hash or size'))
        self.assertEqual(sim.runtime['processed_controls'].count(identifier), 1)
        self.assertEqual(sim.engine.control_result(good['request_id'])['effect'], 'applied')
        source, = sim.instance['sources']
        self.assertEqual(source['name'], 'good.txt')
        self.assertEqual(sim.engine.store.read(source['path'], sim.engine.head), b'after rejection')
        sim.engine._apply_inbox(pump=False)
        self.assertEqual(sim.runtime['processed_controls'].count(identifier), 1)

    def test_source_path_errors_leave_no_inbox_and_a_valid_source_still_imports(self):
        import hashlib
        from do_math.control_contracts import normalized_source
        sim = initialized_sim()
        before = deepcopy((sim.engine.head, sim.instance, sim.runtime))
        cases = [({}, 'source requires a file path or normalized bytes'),
                 ({'path': str(sim.root / 'absent.txt')}, 'source path must identify a readable file'),
                 ({'path': str(sim.root)}, 'source path must identify a readable file')]
        for config, reason in cases:
            with self.subTest(config=config):
                with self.assertRaisesRegex(ValueError, exactly(reason)):
                    sim.control('source', config=config)
                self.assertEqual(list(inbox(sim).glob('*.json')), [])
                self.assertEqual((sim.engine.head, sim.instance, sim.runtime), before)
        raw = b'valid source after path errors\n'
        sent = sim.control('source', config=normalized_source('valid.txt', raw))
        sim.engine.process_controls()
        self.assertEqual(sim.engine.control_result(sent['request_id'])['effect'], 'applied')
        sim.restart()
        source, = sim.instance['sources']
        self.assertEqual((source['sha256'], source['bytes']), (hashlib.sha256(raw).hexdigest(), len(raw)))
        self.assertEqual(sim.engine.store.read(source['path'], sim.engine.head), raw)

    def test_semantic_request_rejections_leave_no_inbox_or_execution(self):
        sim = initialized_sim()
        before = deepcopy((sim.engine.head, sim.instance, sim.runtime))
        cases = [
            ('pause', {'origin': 'worker'}, 'control origin must be user or operator'),
            ('pause', {'request_id': 'UC-two-identities', 'idempotency_key': 'also-a-key'},
             'request_id and idempotency_key are mutually exclusive'),
            ('input', {'text': '  '}, 'input text is required'),
            ('input', {'text': 'answer', 'config': {'responds_to': ['Q-absent']}},
             'responds_to must identify distinct open user questions'),
            ('request', {'config': {'retry_action': ''}},
             'retry_action must be the sole nonempty request mode'),
            ('request', {'config': {'retry_action': 'AC-absent', 'role': 'maintenance'}},
             'retry_action must be the sole nonempty request mode'),
            ('request', {'config': {'role': 'identity_review', 'assessment_reassessment': {}}},
             'assessment reassessment requires the exact assessment hash and defect evidence'),
            ('request', {'config': {'role': 'not-a-role'}}, 'unsupported requested role'),
            ('request', {'config': {'role': 'maintenance', 'cleanup_execution_ids': []}},
             'maintenance cleanup requires distinct existing execution IDs'),
            ('request', {'config': {'role': 'maintenance', 'cleanup_execution_ids': ['EX-absent']}},
             'maintenance cleanup requires distinct existing execution IDs'),
            ('request', {'config': {'role': 'supplemental_research', 'target': 'TK-absent'}},
             'supplemental research requires a task whose current contract is ready'),
            ('request', {'config': {'role': 'operational_review', 'target': 'EX-absent'}},
             'operational review requires an existing execution ID'),
        ]
        for action, options, reason in cases:
            with self.subTest(action=action, options=options):
                with self.assertRaisesRegex(ValueError, exactly(reason)):
                    sim.control(action, **options)
                self.assertEqual(list(inbox(sim).glob('*.json')), [])
                self.assertEqual((sim.engine.head, sim.instance, sim.runtime), before)
        good = sim.control('pause', text='valid after semantic rejections')
        sim.engine.process_controls()
        self.assertEqual(sim.engine.control_result(good['request_id'])['effect'], 'applied')
        self.assertEqual(sim.runtime['processed_controls'].count(good['request_id']), 1)
        self.assertEqual(sim.runtime['executions'], before[2]['executions'])
if __name__ == '__main__':
    unittest.main()
