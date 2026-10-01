"""Public pause and two process restarts preserve the central check's attempt lineage.

Measured at 2.109 s after template restoration; the scenario belongs in flows.
"""
import unittest

from support.engine_lifecycle import applied
from support.knowledge_formal_engine import attempts, run_formal, scene, stop_with_control
from support.sim import warm_template


def setUpModule():
    warm_template()


class FormalAttemptLineageTests(unittest.TestCase):
    def test_public_pause_restart_resume_preserves_formal_attempt_lineage(self):
        sim, action = scene(source='theorem resume_fixture : 1 = 1 := rfl', declarations=('resume_fixture',))
        stop_with_control(sim, action, 'pause')
        first, = attempts(sim)
        self.assertEqual(first['status'], 'ended')
        sim.restart()
        applied(sim, 'resume', config={})
        action = next(a for a in sim.runtime['queue'] if a['role'] == 'formal_check')
        self.assertEqual(action['continuation_of'], first['id'])
        run_formal(sim, action)
        sim.restart()
        rows = attempts(sim)
        self.assertEqual(len(rows), 2)
        self.assertTrue(any(e.get('continuation_of') == first['id'] and e['formal_status'] == 'verified' for e in rows))
        self.assertTrue(any(a['role'] == 'identity_review' for a in sim.runtime['queue']))
