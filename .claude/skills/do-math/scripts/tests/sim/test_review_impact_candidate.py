"""The preview and the receiver apply a held bundle to a candidate copy through one domain callback (``core_engine._apply_bundle_candidate``).

The bundle is the one ``support.review_sim.impact_sim()`` holds for impact
review: research work revised observations ``A`` and ``C``. It is split from
the producer's sealed submission and the input the producer was issued, as the
receiver splits it, and applied to copies of the state on the Sim's engine.
"""
from copy import deepcopy
import unittest

from do_math import integration, knowledge, submission
from do_math.canonical import canonical_json
from support.review_sim import held_impact, impact_sim, observations


class SharedCandidateTests(unittest.TestCase):
    def test_shared_candidate_applies_actual_domain_revision_without_mutating_preview_source(self):
        sim = impact_sim()
        engine = sim.engine
        waiting, producer, identifier, _ = held_impact(sim)
        sealed = submission.read_sealed_submission(producer, engine.head, engine.store.read, git_dir=engine.store.git_dir)
        context, _ = engine._issued_input(producer)
        [bundle] = [row for row in integration.split_bundles(sealed['output'], sealed['extensions'], context)
                    if row['integration_id'] == identifier]
        bundle['owns_response'] = False
        for change in bundle['extensions']['knowledge_changes']:
            roots = knowledge.revision_roots(engine.instance, change['id'])
            change['impact_set'] = knowledge.plan_impact(engine.instance, engine.runtime, roots, [])['computed_impact']
        roots = set().union(*(knowledge.revision_roots(engine.instance, change['id'])
                              for change in bundle['extensions']['knowledge_changes']))
        bundle['impact_set'] = knowledge.plan_impact(engine.instance, engine.runtime, roots, [])['computed_impact']
        # Preview and receiver both call this exact domain callback; storage is tested separately.
        original = canonical_json(engine.instance)
        candidate, running = deepcopy(engine.instance), deepcopy(engine.runtime)
        engine._apply_bundle_candidate(candidate, running, bundle, action=waiting['action'],
                                       execution_id=producer['id'], extensions=bundle['extensions'])
        self.assertEqual(canonical_json(engine.instance), original)
        ids = observations(sim)
        self.assertEqual({ids['A'], ids['C']}, {row['supersedes'] for row in candidate['knowledge'].values() if row.get('supersedes')})
        self.assertEqual([row for row in running['queue'] if row.get('reason') == 'knowledge currentness changed'], [])


if __name__ == '__main__':
    unittest.main()
