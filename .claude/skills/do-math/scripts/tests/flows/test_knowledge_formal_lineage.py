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
        sim.lean.allow('theorem resume_fixture : 1 = 1 := rfl', ['resume_fixture'],
                       signatures={'resume_fixture': 'resume_fixture : 1 = 1'},
            declaration_evidence={'resume_fixture': {'type': '1 = 1', 'value': None}}, axioms={'resume_fixture': []}, dependencies={'resume_fixture': {}})
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


class FormalResultPlanningTests(unittest.TestCase):
    def test_formal_failure_opens_one_actual_plan_while_verified_result_does_not(self):
        from support.cross_contracts import assert_call_records
        from support.default_responder import DefaultResponder
        from support.model import amend
        for valid in (True, False):
            with self.subTest(verified=valid):
                sim, action = scene(declarations=('k1',) if valid else ('k1', 'missing'))
                sim.model.responder = DefaultResponder(preparation_candidates=[], plan_assessments=False)
                sim.model.on('research_plan').reply(amend(goal_audit=False))
                before = assert_call_records(self, sim)
                run_formal(sim, action)
                result, = attempts(sim)
                self.assertEqual(result['formal_status'], 'verified' if valid else 'failed')
                requests = [a for a in sim.runtime['queue'] if a.get('formal_target') == 'K1']
                self.assertEqual(len(requests), int(not valid))
                sim.step()
                after = assert_call_records(self, sim)
                self.assertEqual(after['research_plan'] - before['research_plan'], int(not valid))
                plans = [row for row in sim.runtime['executions'].values()
                         if row['role'] == 'research_plan' and row['action'].get('formal_target') == 'K1']
                self.assertEqual(len(plans), int(not valid))
                if not valid:
                    self.assertEqual(plans[0]['outcome'], 'output_accepted', plans[0].get('error'))
                    for _ in range(2):
                        sim.step()
                        self.assertEqual(assert_call_records(self, sim)['research_plan'], after['research_plan'])
                    self.assertFalse(any(a.get('formal_target') == 'K1' for a in sim.runtime['queue']))
                self.assertEqual(sim.engine.store.load(sim.engine.head)[2], sim.runtime)
