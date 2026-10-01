"""Public activation on the Sim (설계 9.1, 1d): the real engine becomes active through public controls on port fakes."""
from pathlib import Path
import tempfile
import unittest

from support.sim import Sim


class PublicActivationTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)

    def test_public_activation_reaches_active_through_the_worker_with_all_time_from_the_clock_port(self):
        """About 7 s, over the 2 s Sim budget: the public path from an empty repository is what it checks."""
        sim = Sim.activated(self.root)
        self.assertEqual(sim.instance['lifecycle']['state'], 'active')
        # The initial interpretation ran through the product's runner, adapter and worker to the model double.
        self.assertIn('intent_interpretation', [call['role'] for call in sim.model.calls])
        self.assertTrue(sim.jobs.launched)
        self.assertTrue(all(Path(job.argv[1]).name == 'codex_worker.py' for job in sim.jobs.launched))
        self.assertEqual(sim.real_time_leaks(), [])


if __name__ == '__main__':
    unittest.main()
