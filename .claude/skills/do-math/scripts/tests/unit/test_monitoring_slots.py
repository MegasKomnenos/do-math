"""Nested test observers share Python's six IDs with the T3 measurement."""
from contextlib import ExitStack
import sys
import unittest

from support.monitoring_slots import reserve_tool


class SlotTests(unittest.TestCase):
    def test_the_sixth_slot_remains_available_without_displacing_other_tools(self):
        monitoring = sys.monitoring
        previous = [monitoring.get_tool(tool) for tool in range(6)]
        if previous[5] is not None:
            self.skipTest('the optimizer slot is already held by this interpreter')
        with ExitStack() as cleanup:
            for tool in range(5):
                if previous[tool] is None:
                    monitoring.use_tool_id(tool, 'slot occupancy specimen')
                    cleanup.callback(monitoring.free_tool_id, tool)
            held = [monitoring.get_tool(tool) for tool in range(5)]
            tool = reserve_tool('sixth-slot observer')
            cleanup.callback(monitoring.free_tool_id, tool)
            self.assertEqual(tool, 5)
            self.assertEqual([monitoring.get_tool(tool) for tool in range(5)], held)
            with self.assertRaisesRegex(RuntimeError, '^all six Python monitoring tool IDs are occupied$'):
                reserve_tool('cannot displace an owner')
        self.assertEqual([monitoring.get_tool(tool) for tool in range(6)], previous)
