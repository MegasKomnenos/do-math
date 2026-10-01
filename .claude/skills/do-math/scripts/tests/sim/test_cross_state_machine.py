"""Short T2 exploration; the larger event/flow budget lives under flows/."""
import unittest

from support.cross_machine import assert_machine, ControlMachine, SHORT
from support.sim import warm_template

setUpModule = warm_template


class CrossStateMachineTests(unittest.TestCase):
    def test_short_transition_sequences(self):
        """Two four-event examples; template restoration and real publication may exceed 2 s."""
        assert_machine(ControlMachine, SHORT)
