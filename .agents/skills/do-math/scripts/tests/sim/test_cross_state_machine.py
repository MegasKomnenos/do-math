"""Short T2 exploration; the larger event/flow budget lives under flows/."""
from copy import deepcopy
import unittest

from support.cross_machine import assert_machine, ControlMachine, SHORT
from support.sim import warm_template

setUpModule = warm_template


class CrossStateMachineTests(unittest.TestCase):
    def test_new_capacity_events_can_restore_a_previously_requested_limit(self):
        """동일 값의 새 사건과 과거 요청의 재전달을 구분한다."""
        machine = ControlMachine()
        try:
            for value in (2, 0, 2):
                machine.configure_capacity(slots=value)
                machine.restart()
                self.assertTrue(all(limit == value for limit in
                                    machine.sim.instance['config']['session_limits']['work'].values()))
                machine.contracts_after_every_event()
            keys = [event[1]['idempotency_key'] for event in machine.events if event[0] == 'configure']
            self.assertEqual(len(keys), 3)
            self.assertEqual(len(set(keys)), 3)
        finally:
            machine.teardown()

    def test_explicit_capacity_request_replay_keeps_the_later_configuration(self):
        """같은 요청 키의 재전달은 과거 설정을 새 설정 위에 다시 적용하지 않는다."""
        machine = ControlMachine()
        try:
            limits = deepcopy(machine.sim.instance['config']['session_limits'])
            limits['work'] = {model: 2 for model in limits['work']}
            key = machine.sim.clock.new_id('EV')
            first = machine.control('configure', config={'session_limits': limits}, idempotency_key=key)
            machine.configure_capacity(slots=0)
            machine.restart()
            before = deepcopy(machine.sim.instance['config'])
            controls = len([row for row in machine.sim.runtime['history'] if row.get('kind') == 'user_control'])
            replay = machine.control('configure', config={'session_limits': limits}, idempotency_key=key)
            self.assertEqual(replay, first)
            self.assertEqual(machine.sim.instance['config'], before)
            self.assertEqual(len([row for row in machine.sim.runtime['history']
                                 if row.get('kind') == 'user_control']), controls)
            machine.contracts_after_every_event()
        finally:
            machine.teardown()

    def test_short_transition_sequences(self):
        """Two four-event examples; template restoration and real publication may exceed 2 s."""
        assert_machine(ControlMachine, SHORT)
