"""Terminal-state absorption after public close or actual goal completion, with real installation copies."""
import unittest
from support.sim import Sim


class InstallationEditionTests(unittest.TestCase):
    def test_installation_change_cannot_reopen_a_terminal_instance(self):
        """About 20-24 s: public close and actual goal completion with independent installation copies form a long flow."""
        from do_math.engine import ResearchEngine
        from support.engine_lifecycle import applied, lifecycle_sim, solve_goal, THEOREMS
        from support.storage_finish_installation import copy_installation
        for terminal in ('closed', 'completed'):
            with self.subTest(terminal=terminal):
                sim = Sim.activated() if terminal == 'closed' else lifecycle_sim()
                if terminal == 'closed':
                    applied(sim, 'close')
                else:
                    kid = next(k for k, row in sim.instance['knowledge'].items() if row['title'] == THEOREMS[0])
                    solve_goal(sim.engine, kid)
                    sim.engine._save()
                root = copy_installation(sim.root / 'installation')
                e = ResearchEngine(sim.repository, sim.instance_id, ports=sim.ports, installation_root=root, codex_home=sim.codex_home, environment=sim.environment, host_id=sim.host_id)
                self.assertEqual(e.runtime['status'], terminal)
                e._installation
                (root / 'scripts/do_math/engine.py').write_bytes(b'# edited installation\n')
                self.assertFalse(e._check_installation(force=True))
                self.assertEqual(e.runtime['status'], terminal)
                self.assertEqual(e.store.load()[2]['status'], terminal)
