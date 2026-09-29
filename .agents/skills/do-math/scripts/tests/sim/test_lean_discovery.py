"""Lean discovery on the real engine: with no configured Lean command the engine asks the host port, at most once a second."""
import tempfile
import unittest

from support.fakes.host import FakeHost
from support.sim import Sim


class DiscoveringHost(FakeHost):
    """The fake host with Lean discoveries counted."""

    def __init__(self, **facts):
        super().__init__(**facts)
        self.discoveries = 0

    def discover_lean(self):
        self.discoveries += 1
        return super().discover_lean()


class ToolDiscoveryTests(unittest.TestCase):
    def test_lean_is_rediscovered_at_most_once_per_second(self):
        host = DiscoveringHost(lean=['lean'])
        with tempfile.TemporaryDirectory() as directory:
            sim = Sim(directory, host=host, config={'lean_command': None})
            engine = sim.engine
            self.assertIsNone(engine.instance['config']['lean_command'])
            host.discoveries = 0
            sim.advance(1.0)
            for _ in range(5):
                self.assertIn('tool:lean', engine._available_inputs())
            self.assertEqual(host.discoveries, 1)
            host.lean = None
            sim.advance(0.5)
            self.assertIn('tool:lean', engine._available_inputs())
            self.assertEqual(host.discoveries, 1)
            sim.advance(0.5)
            self.assertNotIn('tool:lean', engine._available_inputs())
            self.assertEqual(host.discoveries, 2)

    def test_a_configured_lean_command_needs_no_discovery(self):
        host = DiscoveringHost(lean=None)
        with tempfile.TemporaryDirectory() as directory:
            sim = Sim(directory, host=host)
            host.discoveries = 0
            self.assertTrue(sim.engine.instance['config']['lean_command'])
            self.assertIn('tool:lean', sim.engine._available_inputs())
            self.assertEqual(host.discoveries, 0)


if __name__ == '__main__':
    unittest.main()
