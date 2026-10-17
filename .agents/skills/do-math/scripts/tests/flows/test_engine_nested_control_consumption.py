"""중첩 오입력의 실제 owner 반려·저장·두 번째 순회와 뒤 정상 입력을 확인한다.

16개 행의 실제 저장 게시가 필요하므로 flows에 둔다.
"""
from copy import deepcopy
import json
from pathlib import Path
import re
import unittest

from do_math.control_contracts import validate_control_payload
from support.engine_nested_controls import nested_controls
from support.sim import Sim, warm_template


setUpModule = warm_template


class NestedControlConsumptionTests(unittest.TestCase):
    def test_nested_invalid_leaves_are_consumed_once_without_domain_effects(self):
        sim = Sim.activated()
        admitted = sim.control('pause', text='중첩 입력 전 사용자 정지')
        inbox = Path(sim.instance['workspace']) / 'control' / sim.instance_id
        envelope = json.loads((inbox / (admitted['request_id'] + '.json')).read_bytes())
        sim.engine.process_controls()
        for index, (label, action, valid, malformed, reason) in enumerate(nested_controls()):
            with self.subTest(case=label):
                validate_control_payload(action, '입구 검사', valid)
                with self.assertRaisesRegex(ValueError, '^' + re.escape(reason) + '$'):
                    validate_control_payload(action, '입구 검사', malformed)
                identifier = 'UC-nested-' + label
                request = {**deepcopy(envelope), 'id': identifier, 'action': action, 'config': malformed,
                           'accepted_order': f'{index + 100:020d}'}
                path = inbox / (identifier + '.json')
                raw = json.dumps(request, ensure_ascii=False).encode('utf-8')
                path.write_bytes(raw)
                before_instance, before = deepcopy(sim.instance), deepcopy(sim.runtime)
                sim.engine.process_controls()
                first_head = sim.engine.head
                sim.engine.process_controls()
                _, stored_instance, stored = sim.engine.store.load()
                self.assertEqual(sim.engine.head, first_head)
                self.assertEqual(stored_instance, before_instance)
                self.assertEqual(stored['processed_controls'], [*before['processed_controls'], identifier])
                delta = stored['history'][len(before['history']):]
                self.assertEqual(len(delta), 1)
                self.assertEqual((delta[0]['kind'], delta[0]['reason'], delta[0]['request']),
                                 ('rejected_user_control', reason, request))
                self.assertEqual(path.read_bytes(), raw)
                for family in ('tasks', 'queue', 'executions', 'activities', 'reservations',
                               'extended_controls', 'inputs', 'questions', 'question_links'):
                    self.assertEqual(stored.get(family), before.get(family), family)
                self.assertEqual((sim.model.calls, sim.engine.control_result(identifier)['effect']), ([], 'rejected'))
        rejected_state = deepcopy((sim.engine.head, sim.instance, sim.runtime))
        sim.restart()
        sim.engine.process_controls()
        self.assertEqual((sim.engine.head, sim.instance, sim.runtime), rejected_state)
        resumed = sim.control('resume', text='중첩 반려 후 정상 요청')
        sim.engine.process_controls()
        self.assertEqual(sim.engine.control_result(resumed['request_id'])['effect'], 'applied')
        self.assertEqual(sim.runtime['processed_controls'].count(resumed['request_id']), 1)
        receipt = deepcopy(sim.engine.control_result(resumed['request_id']))
        sim.restart()
        sim.engine.process_controls()
        self.assertEqual(sim.engine.control_result(resumed['request_id']), receipt)
