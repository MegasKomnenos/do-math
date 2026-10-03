"""A duplicate history row cannot confer new evidence on a genuinely completed review.

The normal Sim producer runs actual registration, submission and storage. Its
first build is flow-sized; only the normal template is needed. Whether exact
duplicate history is rejected or normalized remains a separate policy choice.
"""
from copy import deepcopy
import unittest

from do_math import review_cycle as rc
from support.gap_inputs import ExecutedLines, observation
from support.review_replay_inputs import replay_sim


def setUpModule():
    replay_sim()


class DuplicateDeferEvidenceTests(unittest.TestCase):
    def test_duplicate_defer_does_not_add_research_or_change_sealed_evidence(self):
        sim = replay_sim()
        original = deepcopy(next(iter(sim.runtime['review_cycles'].values())))
        def replay(cycle):
            return rc.validate_sealed_review(cycle, sim.runtime, instance=sim.instance,
                read_artifact=sim.engine.store.read, git_dir=sim.engine.store.git_dir,
                clock=sim.clock, at=sim.clock.now())
        normal = replay(original)
        changed = deepcopy(original)
        event = next(h for h in changed['history'] if h.get('event') == 'review_deferred_for_research')
        self.assertTrue(event['request_ids'])
        changed['history'].append(deepcopy(event))
        before = deepcopy((changed, sim.instance, sim.runtime))
        head = sim.engine.head
        with ExecutedLines(rc.validate_sealed_review) as reached:
            try:
                result = replay(changed)
            except ValueError as error:
                observation('R1', error=str(error), contract='duplicate policy undecided')
            else:
                # This is evidence integrity, not an oracle that duplicates must be accepted.
                self.assertEqual(result, normal)
                observation('R1', disposition='normalized', decision=result['decision'],
                            research_ids=list(result['research']), contract='duplicate policy undecided')
        observation('R1-lines', lines=reached.lines, crossed_285_286=reached.crossed(285, 286))
        self.assertEqual((changed, sim.instance, sim.runtime), before)
        self.assertEqual(sim.engine.head, head)
        # Duplication must not exempt the underlying source from validation.
        damaged = deepcopy(changed)
        request = next(iter(damaged['research'].values()))
        request['request_digest'] = '0' * 64
        with self.assertRaisesRegex(ValueError, '^supplemental request digest changed$'):
            replay(damaged)
        self.assertEqual(replay(original), normal)
