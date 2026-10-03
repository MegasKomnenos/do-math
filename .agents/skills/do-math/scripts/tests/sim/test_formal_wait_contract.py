"""4-B: every formal wait uses its declared condition and preserves explicit stops."""
from copy import deepcopy
import unittest

from do_math import trust_validation
from do_math.wait_rules import FORMAL_WAIT_RULES, FORMAL_RECOVERABLE_STOPS, formal_wait
from support.knowledge_formal_engine import parked, warm_scenes
from support.wait_reporting import assert_wait_report

setUpModule = warm_scenes


class FormalWaitContractTests(unittest.TestCase):
    def test_every_declared_formal_wait_has_a_negative_condition_and_exact_release(self):
        for kind, rule in FORMAL_WAIT_RULES.items():
            reasons = (*sorted(FORMAL_RECOVERABLE_STOPS), 'execution_stop_requested') if kind == 'formal_stopped' else (None,)
            for stopped_by in reasons:
                with self.subTest(kind=kind, stopped_by=stopped_by):
                    sim, action, environment, binding, _ = parked()
                    detail = (trust_validation.wait_detail(sim.instance) if kind == 'formal_environment' else
                              {'stop_reasons': [stopped_by]} if kind == 'formal_stopped' else None)
                    entry = formal_wait(action, kind, 'Held formal check', detail=detail)
                    sim.runtime['waiting_actions'][action['id']] = entry
                    sim.engine._save()
                    assert_wait_report(self, sim.engine, action['id'])
                    before = deepcopy((sim.instance, sim.runtime))
                    for _ in range(2):
                        sim.engine._resume_formal_waits()
                        self.assertEqual((sim.instance, sim.runtime), before)
                    sim.instance['trust_environments'][environment['id']] = environment
                    sim.runtime['trust_bindings'][environment['id']] = binding
                    sim.instance['active_trust_environment'] = environment['id']
                    if stopped_by == 'execution_stop_requested':
                        held = deepcopy(sim.runtime)
                        sim.engine._resume_formal_waits()
                        self.assertEqual(sim.runtime, held)
                        self.assertEqual(sim.runtime['waiting_actions'][action['id']], entry)
                    else:
                        sim.engine._resume_formal_waits()
                        self.assertNotIn(action['id'], sim.runtime['waiting_actions'])
                        queued = [row for row in sim.runtime['queue'] if row['id'] == action['id']]
                        self.assertEqual(queued, [action])
                        resumed = deepcopy(sim.runtime)
                        sim.engine._resume_formal_waits()
                        self.assertEqual(sim.runtime, resumed)
                        sim.engine._save()
                        self.assertEqual(sim.engine.store.load()[2]['queue'], sim.runtime['queue'])
