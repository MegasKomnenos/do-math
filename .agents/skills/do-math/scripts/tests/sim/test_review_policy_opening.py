"""The owner opens an identity review with the adopted review policy frozen, at its scope stage (설계 4.1).

The template (``support.review_sim.opened_sim``) is a public activation that
adopted the default review policy, then a theorem imported by public control
that the owner verified through the Lean double; the owner's formal check
opened its identity review. Nothing in the engine is replaced. The mixin's own
rule is ``unit.test_review_policy_scope.EngineScopeTests``; this is the owner's
path to it.
"""
import unittest

from do_math.canonical import exact_content_hash
from support.review_sim import cycle_of, opened_sim, warm_opened


def setUpModule():
    warm_opened()


class OwnerOpenedReviewTests(unittest.TestCase):
    def test_owner_opened_review_freezes_the_adopted_policy_and_starts_at_its_scope_stage(self):
        sim = opened_sim()
        adopted = sim.instance['review_policy']
        self.assertEqual(sim.instance['lifecycle']['adoption']['review_policy_sha256'], exact_content_hash(adopted))
        cycle = cycle_of(sim)
        self.assertEqual(cycle['review_policy'], adopted)
        self.assertEqual((cycle['phase'], cycle['scope_assessment'], cycle['owner_activity_id']), ('scope', None, None))
        self.assertEqual(cycle['review_input_basis']['values']['review_policy'], adopted)
        self.assertEqual([(a['stage'], a['slot']) for a in sim.runtime['queue']
                          if a['role'] == 'identity_review' and a['review_cycle_id'] == cycle['id']], [('scope', 'scope')])


if __name__ == '__main__':
    unittest.main()
