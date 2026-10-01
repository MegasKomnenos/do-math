"""Identity reviews the owner runs (설계 4.1): registration, admission, preparation failure and public reassessment.

The tests restore ``support.review_sim`` templates: a theorem whose identity
review the owner opened after the Lean double verified it, and the same
review run by the owner to a match through the worker, the model double and
submission. Nothing in the engine is replaced; an operating-system refusal to
create a folder is ``Path.mkdir`` raising (the file system is not a port, 설계 2.2).
"""
import errno
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from do_math.canonical import exact_content_hash
from do_math.engine import ResearchEngine
from support.review_sim import cycle_of, opened_sim, review_executions, reviewed_sim, theorem_id, warm_opened, warm_reviewed


def setUpModule():
    warm_opened()
    warm_reviewed()


class OwnerReviewTests(unittest.TestCase):
    def test_owner_registration_admits_every_review_attempt_and_publishes_the_initial_match(self):
        """The owner-run review (``reviewed_sim``): each attempt the owner registered was admitted by its review.

        The executions are the owner's (registered through ``_register_execution``,
        their answers submitted and received); the review counted exactly those
        attempts in registration order, bound them to the one activity the scope
        execution established, and published the two initial slots' match.
        """
        sim = reviewed_sim()
        cycle = cycle_of(sim)
        executions = review_executions(sim, cycle['id'])
        self.assertEqual([(row['action']['stage'], row['action']['slot']) for row in executions],
                         [('scope', 'scope'), ('initial', 'initial-0'), ('initial', 'initial-1')])
        ids = [row['id'] for row in executions]
        self.assertEqual(cycle['execution_accounting']['executions_used'], ids)
        self.assertEqual(sorted(cycle['execution_accounting']['admissions']), sorted(ids))
        self.assertTrue(all(row['outcome'] == 'output_accepted' and row['submission_receipt']['state'] == 'accepted'
                            for row in executions))
        self.assertEqual({row['owner_activity_id'] for row in executions}, {cycle['owner_activity_id']})
        self.assertEqual(sim.runtime['activities'][cycle['owner_activity_id']]['status'], 'finished')
        self.assertEqual(cycle['review_input_basis']['values']['scope_assessment']['assessment_id'],
                         cycle['scope_assessment']['assessment_id'])
        assessment = sim.instance['identity_assessments'][cycle['assessment_id']]
        self.assertEqual((assessment['decision'], assessment['execution_ids']), ('match', ids[1:]))
        self.assertEqual(assessment['review_cycle_id'], cycle['id'])


class PreparationFailureTests(unittest.TestCase):
    def test_review_materialization_failure_ends_preparation_and_saves_recovery(self):
        sim = opened_sim()
        kid = theorem_id(sim)
        [action] = [a for a in sim.runtime['queue'] if a['role'] == 'identity_review']
        original = Path.mkdir

        def unavailable(path, *args, **kwargs):
            if 'review-sources' in path.parts:
                raise OSError(errno.EBUSY, 'Regression source materialization busy')
            return original(path, *args, **kwargs)
        with patch.object(Path, 'mkdir', unavailable):
            sim.step()
        self.assertEqual(sim.model.calls, [], 'no model call starts for an attempt whose input failed')
        attempts = [e for e in sim.runtime['executions'].values() if e.get('action', {}).get('id') == action['id']]
        self.assertEqual(len(attempts), 1)
        self.assertEqual(attempts[0]['status'], 'ended')
        wait = sim.runtime['waiting_actions'][action['id']]
        self.assertEqual(wait['kind'], 'review_input_restoration')
        self.assertEqual(wait['next_owner'], 'review_recovery')
        reloaded = ResearchEngine(sim.repository, sim.instance_id, ports=sim.ports, codex_home=sim.codex_home, environment=sim.environment, host_id=sim.host_id)
        self.assertEqual(reloaded.runtime['waiting_actions'][action['id']], wait)
        with tempfile.TemporaryDirectory() as directory:
            outcome = sim.engine._retry_review_restoration(wait['action'], Path(directory) / 'restored', at=sim.clock.now())
        self.assertEqual(outcome['disposition'], 'review_resumed')
        self.assertNotIn(action['id'], sim.runtime['waiting_actions'])
        self.assertEqual(cycle_of(sim)['knowledge_id'], kid)


class PublicReassessmentTests(unittest.TestCase):
    def test_public_admission_binds_original_assessment_hash(self):
        sim = reviewed_sim()
        assessment = sim.instance['identity_assessments'][cycle_of(sim)['assessment_id']]
        config = {'role': 'identity_review', 'assessment_reassessment': {
            'assessment_id': assessment['id'], 'assessment_sha256': exact_content_hash(assessment),
            'evidence': {'kind': 'report', 'text': 'Read this original judgment'}}}
        result = sim.control('request', config=config)
        self.assertTrue(result['accepted'])
        wrong = {**config, 'assessment_reassessment': {**config['assessment_reassessment'], 'assessment_sha256': '0' * 64}}
        with self.assertRaisesRegex(ValueError, 'assessment reassessment must identify the current original judgment'):
            sim.control('request', config=wrong)
        sim.engine.process_controls()
        outcome = sim.engine.control_result(result['request_id'])
        self.assertNotEqual(outcome.get('effect'), 'rejected', outcome)
        report = next(row for row in reversed(sim.runtime['history']) if row.get('kind') == 'assessment_report')
        self.assertEqual((report['assessment_id'], report['disposition']), (assessment['id'], 'report_only'))
        use = next(row for row in sim.instance['assessment_uses'].values() if row['assessment_id'] == assessment['id'])
        self.assertEqual(use['status'], 'active')


if __name__ == '__main__':
    unittest.main()
