"""Incidental insights a finished review releases (``core_engine._apply_extensions``, layer 2).

Reviewers' incidental insights are held per review cycle while it runs. When
the cycle has finished, applying the next reviewer's extensions releases them:
only registered kinds become knowledge, and one plan opens on exactly those
records. The test applies the extensions on the product's ``ResearchEngine``
over the stored review state of ``support.review_scene``; the queue plan and
academic resolution steps of ``_apply_extensions`` run as they are.
"""
from copy import deepcopy
import tempfile
import unittest

from support.review_scene import ReviewScene, warm


def setUpModule():
    warm()


class ReleasedInsightTests(unittest.TestCase):
    def test_released_incidental_insights_plan_only_preserved_items(self):
        for valid in (True, False):
            with self.subTest(valid=valid), tempfile.TemporaryDirectory() as directory:
                engine = ReviewScene(directory).engine
                engine.runtime['executions'].update({'EX-old': {'id': 'EX-old', 'status': 'ended'},
                    'EX-current': {'id': 'EX-current', 'status': 'ended', 'extensions': {}}})
                engine.runtime['review_cycles'] = {'RC': {'status': 'completed'}}
                engine.runtime['private_insights'] = {'RC': [{'source_execution': 'EX-old',
                    'kind': 'question' if valid else 'unregistered', 'title': 'Question ' + str(i),
                    'statement': 'What remains?', 'summary': 'A retained question', 'evidence_ids': []} for i in range(3)]}
                before = deepcopy(engine.instance['knowledge'])
                engine._apply_extensions({'role': 'identity_review', 'review_cycle_id': 'RC'}, 'EX-current')
                plans = [a for a in engine.runtime['queue'] if a['role'] == 'research_plan']
                self.assertEqual(len(plans), int(valid))
                if valid:
                    released = set(engine.instance['knowledge']) - set(before)
                    self.assertEqual(len(released), 3)
                    self.assertEqual(sorted(plans[0]['evidence_refs']), sorted(released))
                    self.assertEqual({key: engine.instance['knowledge'][key] for key in before}, before)
                else:
                    self.assertEqual(engine.instance['knowledge'], before)


if __name__ == '__main__':
    unittest.main()
