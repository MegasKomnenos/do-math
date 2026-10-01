"""The three legacy continuation premise changes, with current stored trust states."""
import unittest

from do_math import formal, trust_validation
from support.engine_lifecycle import applied
from support.knowledge_formal_engine import scene, stop_with_control, run_formal, warm_scenes
from support.provider_probes import ObservedCalls


def setUpModule():
    warm_scenes()


class FormalContinuationTests(unittest.TestCase):
    def test_resume_rechecks_source_trust_and_authority_before_another_call(self):
        """About 3 s: three independent stored scenes each start and cancel a real verifier/worker."""
        self.assertNotIn('inactive', trust_validation.ENVIRONMENT_STATUSES)
        self.assertIn('invalid', trust_validation.ENVIRONMENT_STATUSES)
        for changed in ('source', 'trust', 'authority'):
            with self.subTest(changed=changed):
                sim, action = scene()
                with ObservedCalls(verifier=formal.verify_lean) as observed:
                    stop_with_control(sim, action, 'pause')
                    applied(sim, 'resume', config={})
                    continuation = next(a for a in sim.runtime['queue'] if a['id'] == action['id'])
                    if changed == 'source':
                        fid = sim.instance['knowledge']['K1']['formal_result_id']
                        sim.instance['formal_results'][fid]['lean_code'] += '\n-- changed candidate'
                    elif changed == 'trust':
                        sim.instance['trust_environments'][sim.instance['active_trust_environment']]['status'] = 'invalid'
                        sim.instance['active_trust_environment'] = None
                    else:
                        sim.instance['grants']['GR-research-sim']['status'] = 'revoked'
                    sim.engine._save()
                    run_formal(sim, continuation)
                self.assertEqual(observed.count('verifier'), 1)
                self.assertEqual(len([e for e in sim.runtime['executions'].values()
                                      if e['role'] == 'formal_check']), 1)
