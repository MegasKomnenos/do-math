"""Staged identity reviews during a trust transition (``review_engine``, ``knowledge``, layer 2).

While a transition to a new trust environment is recorded, the engine reviews
the candidate re-verified under the new toolchain in the same scope cycle but
publishes nothing; the transition's activation consumes the completed review's
receipt. Every test runs the product's ``ResearchEngine`` over the stored
review state of ``support.review_scene``; the round trips store the activated
states in a ``ResearchRepository`` on the Git port's fake and load them back.
"""
from copy import deepcopy
import tempfile
import unittest

from do_math import canonical, knowledge, knowledge_records as kr
from do_math.configuration import DEFAULT_CONFIG
from do_math.execution_profiles import build_profiles
from research_fixtures import current_state, trust_environment, trust_fixture
from support.fakes.clock import FakeClock
from support.fakes.git_backend import InProcessGit
from support.provider_probes import ObservedCalls
from support.review_scene import ReviewScene, warm
from support.storage_records import record_store

TRANSITION_KEYS = {'transition_id', 'from_environment'}


def setUpModule():
    warm()


class StagedReviewCase(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.scene = ReviewScene(temporary.name)
        self.engine = self.scene.engine

    def staged_transition(self):
        """A transition to the registered environment ``TE-next`` whose result re-verifies ``K1`` with another proof term."""
        engine = self.engine
        engine.instance['trust_environments']['TE-next'] = {'id': 'TE-next', 'status': 'registered',
            'toolchain': {'sha256': 'new-toolchain', 'version': 'next'}, 'allowed_axioms': []}
        transition = knowledge.begin_transition(engine.instance, 'TE-next')
        fid = engine.instance['knowledge']['K1']['formal_result_id']
        result = deepcopy(engine.instance['formal_results'][fid]['verification'])
        result.update(id='K1', toolchain=engine.instance['trust_environments']['TE-next']['toolchain'])
        result['declaration_evidence']['sample']['value'] = 'staged verified proof'
        transition = knowledge.record_transition_result(engine.instance, transition, result)
        engine.runtime['trust_transitions'] = {transition['id']: transition}
        return transition['id']

    def review_staged(self, transition_id):
        """Run the staged review of ``K1`` (scope and two initial slots); returns ``(cycle ID, receipt)``."""
        cid = self.engine._start_staged_identity_review(transition_id, 'K1')
        for _ in range(3):
            self.scene.execute()
        return cid, self.engine._completed_staged_identity_review(transition_id, 'K1', cid)


class StagedReviewTests(StagedReviewCase):
    def test_staged_candidate_uses_the_same_scope_cycle_without_publication(self):
        engine, scene = self.engine, self.scene
        transition_id = self.staged_transition()
        before = deepcopy(engine.instance)
        cid = engine._start_staged_identity_review(transition_id, 'K1')
        self.assertEqual(scene.pending()['stage'], 'scope')
        cycle = engine.runtime['review_cycles'][cid]
        self.assertEqual(cycle['proposal']['formal']['toolchain'], engine.instance['trust_environments']['TE-next']['toolchain'])
        scene.execute(); scene.execute(); scene.execute()
        self.assertEqual(engine.instance, before)
        receipt = engine._completed_staged_identity_review(transition_id, 'K1', cid)
        self.assertEqual(receipt['decision'], 'match')
        self.assertEqual(receipt['review_cycle_id'], cid)
        self.assertEqual(receipt['transition_basis'], cycle['staged_candidate']['transition_basis'])
        engine.runtime['trust_transitions'][transition_id]['results']['K1']['declaration_evidence']['sample']['value'] = 'changed'
        with self.assertRaisesRegex(ValueError, 'staged review candidate changed'):
            engine._completed_staged_identity_review(transition_id, 'K1', cid)

    def test_completed_staged_review_is_consumed_by_transition_activation(self):
        engine = self.engine
        transition_id = self.staged_transition()
        before = deepcopy(engine.instance)
        cid, receipt = self.review_staged(transition_id)
        candidate = deepcopy(engine.runtime['trust_transitions'][transition_id])
        candidate['results']['K1']['identity_review'] = receipt

        activated = knowledge.activate_transition(engine.instance, candidate, runtime=engine.runtime)

        self.assertEqual(activated['active_trust_environment'], candidate['to_environment'])
        current = activated['knowledge']['K1']
        self.assertNotEqual(current['formal_result_id'], before['knowledge']['K1']['formal_result_id'])
        self.assertNotEqual(current['exposition_id'], before['knowledge']['K1']['exposition_id'])
        self.assertEqual(activated['formal_results'][current['formal_result_id']]['supersedes'],
                         before['knowledge']['K1']['formal_result_id'])
        self.assertEqual(activated['expositions'][current['exposition_id']]['supersedes'],
                         before['knowledge']['K1']['exposition_id'])
        assessment = next(row for row in activated['identity_assessments'].values()
                          if row.get('review_cycle_id') == cid)
        self.assertEqual(assessment['execution_ids'], receipt['execution_ids'])
        self.assertEqual(assessment['formal_result_id'], current['formal_result_id'])
        self.assertEqual(assessment['exposition_id'], current['exposition_id'])
        self.assertTrue(any(use['assessment_id'] == assessment['id'] and use['status'] == 'active'
                            for use in activated['assessment_uses'].values()))
        self.assertEqual(engine.instance, before)

    def test_staged_activation_rejects_tampered_receipt_and_stale_policy(self):
        engine = self.engine
        transition_id = self.staged_transition()
        _, receipt = self.review_staged(transition_id)

        forged = deepcopy(engine.runtime['trust_transitions'][transition_id])
        forged['results']['K1']['identity_review'] = {**receipt, 'proposal_digest': '0' * 64}
        before = deepcopy(engine.instance)
        with self.assertRaisesRegex(ValueError, 'staged identity review receipt is stale, altered, or not a complete match'):
            knowledge.activate_transition(engine.instance, forged, runtime=engine.runtime)
        self.assertEqual(engine.instance, before)

        for field, value in (('transition_id', 'TR-another'), ('knowledge_id', 'K-another')):
            wrong_owner = deepcopy(engine.runtime['trust_transitions'][transition_id])
            wrong_owner['results']['K1']['identity_review'] = {**receipt, field: value}
            with self.subTest(field=field), self.assertRaisesRegex(
                    ValueError, 'staged identity review receipt is stale, altered, or not a complete match'):
                knowledge.activate_transition(engine.instance, wrong_owner, runtime=engine.runtime)
            self.assertEqual(engine.instance, before)

        stale_instance = deepcopy(engine.instance)
        stale_instance['review_policy']['round_limit'] += 1
        stale_before = deepcopy(stale_instance)
        candidate = deepcopy(engine.runtime['trust_transitions'][transition_id])
        candidate['results']['K1']['identity_review'] = receipt
        with self.assertRaisesRegex(ValueError, 'staged identity review publication premises changed'):
            knowledge.activate_transition(stale_instance, candidate, runtime=engine.runtime)
        self.assertEqual(stale_instance, stale_before)


class StagedRoundTripTests(StagedReviewCase):
    INSTANCE_ID = 'RI-00000000000000000000000000'

    def transition_hashes(self, save):
        """``(head, calls)``: ``save()``'s result and every content hash it computed over a transition record."""
        with ObservedCalls(hash=canonical.exact_content_hash) as observed:
            head = save()
        return head, [value for value in observed.captured('hash')
                      if isinstance(value['value'], dict) and TRANSITION_KEYS <= set(value['value'])]

    def assert_staged_activation_round_trip(self, *, followup_transition):
        engine, scene = self.engine, self.scene
        root = scene.root
        old_fixture = trust_fixture(root, ['old-lean'])
        old_environment, old_binding = trust_environment(old_fixture, environment_id='TE-review',
                                                         source_ref='fixture:old-trust-environment')
        engine.instance['trust_environments']['TE-review'] = old_environment
        formal = engine.instance['formal_results'][engine.instance['knowledge']['K1']['formal_result_id']]
        formal['verification'].update(toolchain=deepcopy(old_environment['toolchain']),
                                      allowed_axioms=deepcopy(old_environment['allowed_axioms']))
        next_fixture = trust_fixture(root, ['next-lean'])
        next_environment, next_binding = trust_environment(next_fixture, environment_id='TE-next', status='registered',
                                                           source_ref='fixture:next-trust-environment')
        engine.instance['trust_environments']['TE-next'] = next_environment
        engine.runtime['trust_bindings'] = {'TE-review': old_binding, 'TE-next': next_binding}
        transition = knowledge.begin_transition(engine.instance, 'TE-next')
        result = deepcopy(formal['verification'])
        result.update(id='K1', toolchain=deepcopy(next_fixture['toolchain']),
                      allowed_axioms=deepcopy(next_fixture['allowed_axioms']))
        result['declaration_evidence']['sample']['value'] = 'staged verified proof'
        transition = knowledge.record_transition_result(engine.instance, transition, result)
        transition_id = transition['id']
        engine.runtime['trust_transitions'] = {transition_id: transition}
        before = deepcopy(engine.instance)
        cid, receipt = self.review_staged(transition_id)
        candidate = deepcopy(engine.runtime['trust_transitions'][transition_id])
        candidate['results']['K1']['identity_review'] = receipt
        activated = knowledge.activate_transition(engine.instance, candidate, runtime=engine.runtime)

        repository_path = root / 'round-trip-repository'
        backend = InProcessGit()
        repository = record_store(repository_path, instance_id=self.INSTANCE_ID, backend=backend, clock=FakeClock())

        def reloaded(head):
            return record_store(repository_path, instance_id=self.INSTANCE_ID, backend=backend, clock=FakeClock()).load(head)[1]
        # Every stored state passes the current lifecycle gate.
        lifecycle_instance, lifecycle_runtime = current_state()
        persisted_runtime_before = {**lifecycle_runtime, 'trust_bindings': {'TE-review': old_binding}}
        persisted_runtime_after = {**deepcopy(engine.runtime), **lifecycle_runtime}
        persisted_runtime_after['trust_transitions'][transition_id]['status'] = 'active'
        # This domain-level fixture has explicitly applied the queued activation.
        persisted_runtime_after['queue'] = [a for a in persisted_runtime_after['queue']
            if not (a['role'] == 'trust_activate' and a.get('transition_id') == transition_id)]
        execution_ids = list(persisted_runtime_after['executions'])
        persisted_runtime_after['activities'] = {'AY-fixture': {
            'id': 'AY-fixture', 'activity_kind': 'identity_review', 'owner_ref': cid,
            'opened_at': '2026-09-22T00:00:00+00:00', 'input_refs': ['K1'],
            'status': 'finished', 'stage': 'identity_review', 'execution_limit': 24,
            'assigned_execution_ids': execution_ids, 'result_refs': [cid],
            'unresolved': [], 'followups': [], 'finished_at': '2026-09-22T00:00:01+00:00'}}
        for execution_id, execution in persisted_runtime_after['executions'].items():
            execution['action'].setdefault('id', 'AC-' + execution_id)
            execution['input_manifest'] = {'review_cycle_id': cid, 'prompt': {'sha256': 'a' * 64}}
            execution['created_at'] = '2026-09-22T00:00:00+00:00'
            execution['context_origin'] = []
            execution['ended_at'] = '2026-09-22T00:00:01+00:00'
            execution['submission_receipt'] = {'accepted': True}
        for cycle in persisted_runtime_after['review_cycles'].values():
            cycle['producer_execution_ids'] = []
            for binding in cycle.get('input_bindings', {}).values():
                binding['input_sha256'] = 'a' * 64
        persisted_before, persisted_after = deepcopy(before), deepcopy(activated)
        capacity_constraints = build_profiles(DEFAULT_CONFIG)['capacity_constraints']
        for state in (persisted_before, persisted_after):
            state['capacity_constraints'] = deepcopy(capacity_constraints)
            state.pop('role_profile_refs', None)
            state['lifecycle'] = deepcopy(lifecycle_instance['lifecycle'])
        first = repository.initialize(persisted_before, persisted_runtime_before)
        # A staged review new to the parent binds its transition by hash.
        second, rehashed = self.transition_hashes(
            lambda: repository.save_with_state(first, persisted_after, persisted_runtime_after)[0])
        self.assertTrue(rehashed)
        old_loaded = reloaded(first)
        new_loaded = reloaded(second)

        for family in ('formal_results', 'identity_assessments'):
            for identifier, record in before[family].items():
                self.assertEqual(old_loaded[family][identifier], record)
                self.assertEqual(new_loaded[family][identifier], record)
        current = new_loaded['knowledge']['K1']
        assessment = next(row for row in new_loaded['identity_assessments'].values()
                          if row.get('review_cycle_id') == cid)
        self.assertEqual(new_loaded['formal_results'][current['formal_result_id']]['transition_id'], transition_id)
        self.assertEqual(new_loaded['expositions'][current['exposition_id']]['formal_result_id'], current['formal_result_id'])
        self.assertEqual(assessment['formal_result_id'], current['formal_result_id'])
        self.assertEqual(assessment['exposition_id'], current['exposition_id'])
        self.assertTrue(any(use['assessment_id'] == assessment['id'] for use in new_loaded['assessment_uses'].values()))
        if not followup_transition:
            return

        first_transition_records = {
            'formal': deepcopy(persisted_after['formal_results'][current['formal_result_id']]),
            'exposition': deepcopy(persisted_after['expositions'][current['exposition_id']]),
            'assessment': deepcopy(assessment),
        }
        final_fixture = trust_fixture(root, ['final-lean'])
        final_environment, final_binding = trust_environment(final_fixture, environment_id='TE-final', status='registered',
                                                             source_ref='fixture:final-trust-environment')
        persisted_after['trust_environments']['TE-final'] = final_environment
        persisted_runtime_after['trust_bindings']['TE-final'] = final_binding
        continuity = knowledge.begin_transition(persisted_after, 'TE-final')
        continuity_result = deepcopy(first_transition_records['formal']['verification'])
        continuity_result.update(id='K1', toolchain=deepcopy(final_fixture['toolchain']),
                                 allowed_axioms=deepcopy(final_fixture['allowed_axioms']))
        continuity = knowledge.record_transition_result(persisted_after, continuity, continuity_result)
        persisted_runtime_after['trust_transitions'][continuity['id']] = continuity
        twice_activated = knowledge.activate_transition(
            persisted_after, continuity, runtime=persisted_runtime_after)
        persisted_runtime_after['trust_transitions'][continuity['id']]['status'] = 'active'

        self.assertEqual(twice_activated['formal_results'][current['formal_result_id']],
                         first_transition_records['formal'])
        self.assertEqual(twice_activated['expositions'][current['exposition_id']],
                         first_transition_records['exposition'])
        self.assertEqual(twice_activated['identity_assessments'][assessment['id']],
                         first_transition_records['assessment'])
        reviewed_environment = persisted_runtime_after['review_cycles'][cid]['staged_candidate']['target_environment']
        self.assertEqual(reviewed_environment['status'], 'registered')
        self.assertEqual(twice_activated['trust_environments']['TE-next']['status'], 'superseded')
        # The sealed result binds the identity (toolchain), not a hash of the mutable environment record.
        sealed = twice_activated['formal_results'][current['formal_result_id']]
        self.assertNotIn('trust_environment_digest', sealed['verification'])
        self.assertEqual(sealed['verification']['toolchain'], reviewed_environment['toolchain'])
        self.assertFalse(kr.formal_usable(twice_activated, sealed))
        self.assertFalse(kr.assessment_current(twice_activated, assessment['id']))
        self.assertTrue(kr.usable_links(twice_activated, 'K1'))

        # The finished staged review and its transition equal the parent's: the hash is not recomputed.
        third, rehashed = self.transition_hashes(
            lambda: repository.save_with_state(second, twice_activated, persisted_runtime_after)[0])
        self.assertEqual(rehashed, [])
        twice_loaded = reloaded(third)
        self.assertEqual(twice_loaded['formal_results'][current['formal_result_id']],
                         first_transition_records['formal'])
        self.assertEqual(twice_loaded['expositions'][current['exposition_id']],
                         first_transition_records['exposition'])
        self.assertEqual(twice_loaded['identity_assessments'][assessment['id']],
                         first_transition_records['assessment'])
        self.assertFalse(kr.assessment_current(twice_loaded, assessment['id']))
        self.assertTrue(kr.usable_links(twice_loaded, 'K1'))

    def test_staged_activation_git_round_trip_preserves_old_and_loads_new_records(self):
        """About 0.3 s, over the 0.2 s unit budget: two synthetic toolchains are hashed and two states pass the storage contract."""
        self.assert_staged_activation_round_trip(followup_transition=False)

    def test_staged_assessment_survives_a_second_transition_and_git_round_trip(self):
        """About 0.4 s, over the 0.2 s unit budget: three synthetic toolchains are hashed and three states pass the storage contract."""
        self.assert_staged_activation_round_trip(followup_transition=True)


if __name__ == '__main__':
    unittest.main()
