"""Short T2 exploration; the larger event/flow budget lives under flows/."""
from copy import deepcopy
import unittest

from support.cross_machine import assert_machine, ControlMachine, SHORT
from support.sim import warm_template

setUpModule = warm_template


class CrossStateMachineTests(unittest.TestCase):
    def test_role_selection_filters_the_actual_expired_authority_only(self):
        from support.cross_research_machine import RoleInputSelection
        from support.sim import Sim
        selection = RoleInputSelection()
        selection.sim = Sim.activated()
        action = deepcopy(selection.current_action('research_preparation'))
        self.assertIsNotNone(action)
        self.assertTrue(selection.ready('research_preparation'))
        self.assertEqual(selection.current_action('research_preparation'), action)
        selection.sim.advance(86401)
        self.assertIsNotNone(selection.current_action('research_preparation'))
        with self.assertRaisesRegex(ValueError, '^research authority: no current grant permits this action$'):
            selection.sim.engine._action_lifecycle_gate(deepcopy(action))
        self.assertFalse(selection.ready('research_preparation'))
        self.assertEqual(selection.current_action('research_preparation'), action)

    def test_role_selection_propagates_a_stale_profile_from_its_input(self):
        from support.cross_research_machine import RoleInputSelection
        from support.sim import Sim

        class StaleSelection(RoleInputSelection):
            damage = False

            def current_action(self, role, stage=None):
                action = deepcopy(super().current_action(role, stage))
                if action is not None and self.damage:
                    action['profile_ref'] = deepcopy(self.sim.instance['role_profile_refs'][role][0])
                    action['profile_ref']['sha256'] = '0' * 64
                return action

        selection = StaleSelection()
        selection.sim = Sim.activated()
        self.assertTrue(selection.ready('research_preparation'))
        before = deepcopy((selection.sim.instance, selection.sim.runtime))
        selection.damage = True
        with self.assertRaisesRegex(ValueError, '^profile reference is absent or stale$'):
            selection.ready('research_preparation')
        self.assertEqual((selection.sim.instance, selection.sim.runtime), before)
        selection.damage = False
        self.assertTrue(selection.ready('research_preparation'))

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
