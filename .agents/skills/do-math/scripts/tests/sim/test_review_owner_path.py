"""Identity reviews the owner runs (설계 4.1): registration, admission, preparation failure and public reassessment.

The tests restore ``support.review_sim`` templates: a theorem whose identity
review the owner opened after the Lean double verified it, and the same
review run by the owner to a match through the worker, the model double and
submission. Nothing in the engine is replaced; an operating-system refusal to
create a folder is ``Path.mkdir`` raising (the file system is not a port, 설계 2.2).
"""
import errno
from copy import deepcopy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from do_math.canonical import exact_content_hash
from do_math.engine import ResearchEngine
from do_math.reporting import status_report, render_human_report
from support.wait_reporting import assert_wait_report
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
        assert_wait_report(self, reloaded, action['id'])
        from support.engine_lifecycle import ObservedCalls, code_of
        activity = sim.runtime['activities'][attempts[0]['owner_activity_id']]
        self.assertEqual(activity['waiting']['kind'], 'review_input_restoration')
        activity['waiting']['reason'] = 'The original sealed review input still needs restoration'
        admissions = deepcopy(cycle_of(sim)['execution_accounting'])
        waiting_condition = deepcopy(activity['waiting'])
        with ObservedCalls(admission=code_of(sim.engine._admit_review_execution)) as observed:
            retry = sim.engine._register_execution(wait['action'],
                {'id': 'EX-held-review-input', 'role': 'identity_review', 'status': 'running'})
        self.assertIsNone(retry)
        self.assertEqual(observed.calls['admission'], [], 'explanation text cannot bypass the typed held-input gate')
        self.assertNotIn('EX-held-review-input', sim.runtime['executions'])
        self.assertEqual(cycle_of(sim)['execution_accounting'], admissions)
        self.assertEqual(activity['waiting']['kind'], 'review_input_restoration')
        self.assertEqual(activity['waiting'], waiting_condition, 'a blocked registration preserves the release coordinates')
        # The same real filesystem refusal keeps the exact action and activity
        # held when the recovery owner retries before the condition is met.
        before_wait = deepcopy(sim.runtime['waiting_actions'][action['id']])
        with tempfile.TemporaryDirectory() as directory, patch.object(Path, 'mkdir', unavailable):
            held = sim.engine._retry_review_restoration(wait['action'], Path(directory) / 'still-busy')
        self.assertEqual(held['disposition'], 'recovery_recorded')
        self.assertEqual(sim.runtime['waiting_actions'][action['id']], before_wait)
        self.assertEqual(activity['waiting'], waiting_condition)
        self.assertEqual(cycle_of(sim)['execution_accounting'], admissions)
        sim.engine._save()
        assert_wait_report(self, sim.engine, action['id'])
        with tempfile.TemporaryDirectory() as directory:
            outcome = sim.engine._retry_review_restoration(wait['action'], Path(directory) / 'restored', at=sim.clock.now())
        self.assertEqual(outcome['disposition'], 'review_resumed')
        self.assertNotIn(action['id'], sim.runtime['waiting_actions'])
        activity = sim.runtime['activities'][attempts[0]['owner_activity_id']]
        self.assertEqual(activity['status'], 'ready')
        self.assertNotIn('waiting', activity)
        self.assertEqual(cycle_of(sim)['execution_accounting'], admissions)
        queued = [row for row in sim.runtime['queue'] if row.get('review_cycle_id') == action['review_cycle_id']
                  and all(row.get(key) == action.get(key) for key in ('stage', 'round', 'slot'))]
        self.assertEqual(len(queued), 1)
        queue = deepcopy(sim.runtime['queue'])
        with tempfile.TemporaryDirectory() as directory:
            repeated = sim.engine._retry_review_restoration(wait['action'], Path(directory) / 'again')
        self.assertEqual(repeated['disposition'], 'review_resumed')
        self.assertEqual(sim.runtime['queue'], queue)
        self.assertEqual(cycle_of(sim)['knowledge_id'], kid)
        sim.engine._save()  # the outer control owner publishes the released wait
        head, instance, runtime = sim.engine.store.load()
        report = status_report(sim.engine.store, head, instance, runtime, requested_areas=['record_storage'],
            evaluation_context={'now': sim.clock.now(), 'host_id': sim.host_id})
        self.assertNotIn(action['id'], report['waiting_actions'])
        self.assertNotIn(activity['id'], report['waiting_activities'])
        self.assertFalse(any(line.startswith('activity ' + activity['id'] + ':') or
                             line.startswith('action ' + action['id'] + ':')
                             for line in render_human_report(report).splitlines()))
        from support.role_input_requirements import observe_judgment_inputs
        with observe_judgment_inputs(self) as prepared:
            sim.run_until(lambda s: any(row['role'] == 'identity_review'
                and row['action'].get('review_cycle_id') == action['review_cycle_id'] for row in prepared), max_steps=6)
        restored = [row for row in prepared if row['role'] == 'identity_review'
                    and row['action'].get('review_cycle_id') == action['review_cycle_id']]
        self.assertTrue(restored)
        self.assertEqual((restored[0]['action']['stage'], restored[0]['action']['slot']),
                         (action['stage'], action['slot']))


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
