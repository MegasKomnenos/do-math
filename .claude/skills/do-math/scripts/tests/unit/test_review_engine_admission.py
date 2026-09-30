"""The engine's identity review mixin (``review_engine``, layer 2): policy, admission and publication premises.

Every test runs the product's ``ResearchEngine`` over the stored review state
of ``support.review_scene`` (candidate theorem ``K1``, verified formal
evidence, the fixture review policy) and calls the mixin as the owner does.
"""
from copy import deepcopy
import tempfile
import unittest

from do_math import execution_profiles, knowledge_records as kr, review_cycle, review_policy
from support.engine_lifecycle import ObservedCalls, code_of
from support.review_scene import ReviewScene, warm


def setUpModule():
    warm()


class ReviewSceneCase(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.scene = ReviewScene(temporary.name)
        self.engine = self.scene.engine


class AdoptedPolicyTests(ReviewSceneCase):
    def test_adopted_instance_policy_is_the_only_opening_and_publication_policy(self):
        engine, scene = self.engine, self.scene
        approved = deepcopy(engine.instance['review_policy'])
        approved.update(id='ADOPTED', minimum_initial_slots=3,
                        required_perspectives=['formal', 'semantic', 'scope'], activity_execution_limit=18)
        engine.instance['review_policy'] = approved
        cid = engine._start_identity_review('K1')
        self.assertEqual(engine.runtime['review_cycles'][cid]['review_policy'], approved)
        context = engine._prepare_review_context(scene.pending(), scene.root / 'scope')['context']
        self.assertEqual(context['review_policy'], approved)
        engine.instance['review_policy']['activity_execution_limit'] = 19
        with self.assertRaisesRegex(ValueError, 'review publication premises changed: formal, exposition, trust or policy'):
            engine._review_cycle(scene.pending())
        with self.assertRaisesRegex(ValueError, 'review publication premises changed: formal, exposition, trust or policy'):
            engine._start_identity_review('K1')

    def test_kernel_evidence_outside_the_reviewed_projection_still_binds_publication(self):
        engine = self.engine
        cid = engine._start_identity_review('K1')
        sealed = deepcopy(engine.runtime['review_cycles'][cid]['proposal'])
        formal = engine.instance['formal_results'][engine.instance['knowledge']['K1']['formal_result_id']]
        formal['verification']['declaration_evidence']['sample']['value'] = 'another proof term'
        self.assertEqual(review_cycle.review_proposal(engine.instance, 'K1'), sealed)
        with self.assertRaisesRegex(ValueError, 'review publication premises changed: formal, exposition, trust or policy'):
            engine._review_cycle(self.scene.pending())

    def test_v5_missing_adopted_policy_does_not_use_config_default(self):
        engine = self.engine
        engine.instance.pop('review_policy', None)
        with self.assertRaisesRegex(ValueError, 'adopted review policy is required before review admission'):
            engine._start_identity_review('K1')


class AdmissionTests(ReviewSceneCase):
    def test_admission_counts_failed_and_retried_executions_before_results(self):
        engine, scene = self.engine, self.scene
        limit = review_policy.minimum_scope_executions(2, 2)
        engine.instance['review_policy']['activity_execution_limit'] = limit
        cid = scene.start('K1', scope={**scene.scope, 'activity_execution_limit': limit})
        action = scene.pending()
        attempts = [f'attempt-{number}' for number in range(1, limit + 1)]
        for eid in attempts:
            execution = {'id': eid, 'actor_kind': 'ai', 'owner_activity_id': 'AY', 'status': 'queued'}
            self.assertEqual(engine._admit_review_execution(action, execution)['disposition'], 'admitted')
            self.assertEqual(engine._admit_review_execution(action, execution)['disposition'], 'already_admitted')
            execution['status'] = 'ended'
            engine.runtime['executions'][eid] = execution
        denied = engine._admit_review_execution(action, {'id': 'attempt-extra', 'actor_kind': 'ai', 'owner_activity_id': 'AY'})
        self.assertEqual(denied['disposition'], 'review_budget_exhausted')
        self.assertEqual(engine.runtime['review_cycles'][cid]['execution_accounting']['executions_used'], attempts)
        self.assertEqual(engine.runtime['review_cycles'][cid]['results'], {})

    def test_optional_research_cannot_consume_mandatory_followup_reservations(self):
        engine, scene = self.engine, self.scene
        engine.instance['review_policy']['activity_execution_limit'] = 12
        cid = scene.start('K1', scope={**scene.scope, 'activity_execution_limit': 12})
        action = {**scene.pending(), 'role': 'supplemental_research', 'stage': 'investigating', 'research_request_id': 'R'}
        denied = engine._admit_review_execution(action, {'id': 'optional', 'actor_kind': 'ai', 'owner_activity_id': 'AY'})
        self.assertEqual(denied['disposition'], 'review_followup_reserved')
        stages = {row['stage'] for row in denied['reserved_execution_slots']}
        self.assertTrue({'initial', 'organize', 'answer', 'judge'} <= stages)
        self.assertEqual(engine.runtime['review_cycles'][cid]['execution_accounting']['executions_used'], [])

    def test_admission_cannot_reseal_changed_policy_or_scope(self):
        engine, scene = self.engine, self.scene
        cid = scene.start('K1')
        cycle = engine.runtime['review_cycles'][cid]
        cycle['activity_execution_limit'] += 1
        with self.assertRaisesRegex(ValueError, 'review inputs changed before admission'):
            engine._admit_review_execution(scene.pending(), {'id': 'stale', 'actor_kind': 'ai', 'owner_activity_id': 'AY'})
        self.assertEqual(cycle['execution_accounting']['executions_used'], [])

    def test_every_review_owned_attempt_uses_owner_admission_before_registration(self):
        """A supplemental research attempt owned by a review whose reserved slots it would consume is not registered.

        The owner's registration (``_register_execution``) admits the attempt
        through the review before binding it; the refusal becomes the review's
        resource disposition request. Both calls are observed as they start
        (``ObservedCalls``); nothing is replaced.
        """
        engine, scene = self.engine, self.scene
        engine.instance['review_policy']['activity_execution_limit'] = 12
        cid = scene.start('K1', scope={**scene.scope, 'activity_execution_limit': 12})
        action = {'id': 'AC-review', 'role': 'supplemental_research', 'target': 'K1', 'owner_review_cycle_id': cid,
                  'review_cycle_id': cid, 'stage': 'investigating', 'research_request_id': 'R'}
        profile = engine._execution_profile(deepcopy(action))  # the profile the owner selects for this action
        self.assertIn(profile['id'], {key for key, row in engine.instance['execution_profiles'].items()
                                      if row['role'] == 'supplemental_research'})
        engine.runtime['queue'].append(action)
        with ObservedCalls(admit=code_of(engine._admit_review_execution),
                           dispose=code_of(engine._request_review_resource_disposition)) as observed:
            result = engine._register_execution(action, {'id': 'EX-attempt', 'role': action['role'], 'status': 'queued'})
        self.assertIsNone(result)
        [admitted] = observed.calls['admit']
        self.assertEqual(admitted['execution']['id'], 'EX-attempt')
        self.assertEqual(admitted['execution']['actor_kind'], 'ai')
        self.assertEqual(admitted['execution']['execution_profile_ref'], execution_profiles.profile_ref(profile))
        self.assertNotIn('EX-attempt', engine.runtime['executions'])
        [requested] = observed.calls['dispose']
        self.assertIs(requested['action'], action)
        self.assertEqual(requested['reason'], 'review_followup_reserved')
        self.assertEqual((requested['detail']['disposition'], requested['detail']['execution_id']),
                         ('review_followup_reserved', 'EX-attempt'))
        cycle = engine.runtime['review_cycles'][cid]
        record = review_cycle.resource_disposition(cycle)
        self.assertEqual((record['reason'], record['detail']), ('review_followup_reserved', requested['detail']))
        self.assertEqual(cycle['execution_accounting']['executions_used'], [])


class PublicationTests(ReviewSceneCase):
    def test_split_proposal_binds_real_formal_exposition_and_current_basis(self):
        engine = self.engine
        before = deepcopy(engine.instance['knowledge']['K1'])
        cid = self.scene.start('K1')
        cycle = engine.runtime['review_cycles'][cid]
        self.assertEqual(cycle['proposal']['lean_code'], kr.proposal_view(engine.instance, 'K1')['lean_code'])
        self.assertEqual(cycle['identity_basis'], kr.identity_basis(engine.instance, 'K1'))
        self.assertEqual(cycle['proposal']['formal_result_id'], before['formal_result_id'])
        self.assertEqual(cycle['proposal']['exposition_id'], before['exposition_id'])
        for field in ('formal', 'lean_code', 'reviews', 'status', 'identity_assessment'):
            self.assertNotIn(field, engine.instance['knowledge']['K1'])

    def test_runtime_trust_barrier_leaves_final_slot_pending_for_retry(self):
        engine, scene = self.engine, self.scene
        cid = scene.start('K1')
        scene.execute()
        before = deepcopy(engine.runtime['review_cycles'][cid])
        engine.runtime['trust_transitions'] = {'TR': {'status': 'ready'}}
        with self.assertRaisesRegex(ValueError, 'formal admission is blocked during a trust transition'):
            scene.execute()
        after = engine.runtime['review_cycles'][cid]
        self.assertEqual({k: v for k, v in after.items() if k != 'execution_accounting'},
                         {k: v for k, v in before.items() if k != 'execution_accounting'})
        self.assertEqual(after['execution_accounting']['executions_used'], ['ex-1', 'ex-2'])

    def test_final_match_does_not_override_suspension_or_formal_change(self):
        """About 0.25 s, over the 0.2 s unit budget: five failure cases each restore a scene and run two slots."""
        premises = 'review publication premises changed: formal, exposition, trust or policy'
        cases = {'suspended': 'match cannot activate without current formal evidence', 'source_hash': premises,
                 'environment': premises, 'trust_transition': 'formal admission is blocked during a trust transition',
                 'policy': premises}
        for failure, reason in cases.items():
            with self.subTest(failure=failure):
                scene = ReviewScene(self.scene.root / failure)
                engine = scene.engine
                scene.start('K1')
                scene.execute()
                formal = engine.instance['formal_results'][engine.instance['knowledge']['K1']['formal_result_id']]
                if failure == 'suspended': formal['formal_use'] = 'suspended'
                elif failure == 'source_hash': formal['verification']['source_sha256'] = 'changed'
                elif failure == 'environment': engine.instance['trust_environments']['TE-review']['status'] = 'invalid'
                elif failure == 'policy': engine.instance['review_policy']['activity_execution_limit'] += 1
                else: engine.runtime['trust_transitions'] = {'TR-pending': {'status': 'checking'}}
                with self.assertRaisesRegex(ValueError, reason):
                    scene.execute()
                self.assertEqual(engine.instance['identity_assessments'], {})
                self.assertFalse(scene.usable())

    def test_fresh_exact_formal_check_preserves_eligibility(self):
        engine, scene = self.engine, self.scene
        scene.start('K1')
        scene.execute()
        formal = engine.instance['formal_results'][engine.instance['knowledge']['K1']['formal_result_id']]
        verification = deepcopy(formal['verification'])
        engine.instance = kr.record_formal_result(engine.instance, 'K1', verification, 'TE-review', runtime=engine.runtime)
        scene.execute()
        self.assertTrue(scene.usable())
        self.assertEqual(scene.assessment()['basis'], kr.identity_basis(engine.instance, 'K1'))

    def test_environment_transition_during_review_invalidates_old_environment_use(self):
        engine, scene = self.engine, self.scene
        scene.start('K1')
        scene.execute()
        engine.instance['active_trust_environment'] = 'TE-new'
        engine.instance['trust_environments']['TE-review']['status'] = 'superseded'
        with self.assertRaisesRegex(ValueError, 'review publication premises changed: formal, exposition, trust or policy'):
            scene.execute()
        self.assertFalse(scene.usable())

    def test_mutated_proposal_and_old_action_are_rejected(self):
        engine, scene = self.engine, self.scene
        cycle_id = scene.start('K1')
        old_action = deepcopy(scene.pending())
        formal = engine.instance['formal_results'][engine.instance['knowledge']['K1']['formal_result_id']]
        original = formal['lean_code']
        formal['lean_code'] += '\n-- changed during review'
        with self.assertRaisesRegex(ValueError, 'sealed mathematical proposal'):
            engine._review_schema(old_action)
        formal['lean_code'] = original
        scene.execute()
        scene.execute()
        kid = scene.revise()
        scene.start(kid, previous_cycle_id=cycle_id)
        with self.assertRaisesRegex(ValueError, 'review action is not pending'):
            engine._review_schema(old_action)


if __name__ == '__main__':
    unittest.main()
