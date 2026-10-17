"""채택 호스트 변경 생산자가 고정된 검토 프로필을 다시 묶지 않는 계약."""
from copy import deepcopy

from do_math import review_cycle as rc
from support.review_owner_inputs import ReviewOwnerCase
from support.review_scene import warm
from support.scheduling_hosts import host_configuration


def setUpModule():
    warm()


class HostResourceContractTests(ReviewOwnerCase):
    def changed_host(self, *, owner=True):
        if owner:
            cid, _ = self.opened()
            self.engine._activity_for_action(self.scene.pending())
            self.scene.execute()
        else:
            scope = {**self.scene.scope, 'selected_profile_ref': deepcopy(self.scene.profile)}
            cid = self.scene.start('K1', scope=scope)
        settings = host_configuration()['host_resources']
        self.engine.instance, self.engine.runtime = self.engine._configure_candidate(
            self.engine.instance, self.engine.runtime, {'config': {'host_resources': settings}})
        before = deepcopy(self.engine.instance['identity_assessments'])
        self.assertEqual(self.engine._reconcile_review_host_profiles(), [cid])
        cycle = self.engine.runtime['review_cycles'][cid]
        record = rc.resource_disposition(cycle)
        self.assertEqual(record['reason'], 'review_host_configuration_changed')
        self.assertEqual(self.engine.instance['identity_assessments'], before)
        return cycle, record

    def test_changed_host_closes_existing_owner_without_rewriting_pinned_profile(self):
        cycle, record = self.changed_host()
        self.assertEqual(cycle['slot_profiles']['initial-0'], self.scene.profile)
        self.assertEqual(record['state'], 'ended')
        self.assertEqual(rc.validate_resource_disposition(cycle, self.engine.runtime, instance=self.engine.instance), record)
        before = deepcopy(self.engine.runtime)
        self.assertEqual(self.engine._reconcile_review_host_profiles(), [])
        self.assertEqual(self.engine.runtime, before)

    def test_upkeep_publishes_the_resource_disposition_of_a_real_frozen_review(self):
        """T3 22.6 s cold: public import/formal check and scope execution provide a saveable frozen review."""
        from support.review_sim import opened_sim, cycle_of
        sim = opened_sim()
        sim.run_until(lambda current: bool(cycle_of(current).get('slot_profiles')), max_steps=3)
        engine = sim.engine
        cycle = cycle_of(sim)
        original_profiles = deepcopy(cycle.get('slot_profiles', {}))
        settings = host_configuration()['host_resources']
        engine.instance, engine.runtime = engine._configure_candidate(
            engine.instance, engine.runtime, {'config': {'host_resources': settings}})
        engine._save()
        engine._upkeep(schedule_reviews=False)
        cycle = cycle_of(sim)
        record = rc.resource_disposition(cycle)
        self.assertEqual((record['reason'], record['state']), ('review_host_configuration_changed', 'ended'))
        self.assertEqual(cycle.get('slot_profiles', {}), original_profiles)
        self.assertEqual(engine.store.load()[2]['review_cycles'][cycle['id']], cycle)

    def test_changed_host_creates_owner_for_unstarted_frozen_scope(self):
        cycle, record = self.changed_host(owner=False)
        self.assertIn(cycle['owner_activity_id'], self.engine.runtime['activities'])
        self.assertEqual(self.engine.runtime['activities'][cycle['owner_activity_id']]['status'], 'finished')
        self.assertEqual(record['executions_used'], [])
        self.assertEqual(rc.validate_resource_disposition(cycle, self.engine.runtime), record)

    def test_host_change_requires_actual_pinned_profile(self):
        original, _ = self.changed_host()
        for refs, reason in [([], 'review host change has no pinned profile evidence'),
                ([{'id': 'other', 'revision': 1}], 'review host change refers to a profile outside the frozen review')]:
            cycle = deepcopy(original)
            rc.resource_disposition(cycle)['detail']['profile_refs'] = refs
            with self.subTest(refs=refs), self.assertRaisesRegex(ValueError, reason):
                rc.validate_resource_disposition(cycle, self.engine.runtime)

    def test_host_change_rejects_nonhost_adopted_constraint(self):
        cycle, _ = self.changed_host()
        other = next(key for key, value in self.engine.instance['capacity_constraints'].items() if value['kind'] != 'host')
        rc.resource_disposition(cycle)['detail']['adopted_host_ref'] = other
        with self.assertRaisesRegex(ValueError, 'review host change names no adopted host constraint'):
            rc.validate_resource_disposition(cycle, self.engine.runtime, instance=self.engine.instance)

    def test_host_change_cannot_claim_the_original_unconstrained_profile_changed(self):
        cycle, _ = self.changed_host()
        rc.resource_disposition(cycle)['detail']['adopted_host_ref'] = None
        with self.assertRaisesRegex(ValueError, 'review pinned profile already matches the host configuration'):
            rc.validate_resource_disposition(cycle, self.engine.runtime, instance=self.engine.instance)

    def test_affordable_scope_cannot_use_scope_exhaustion_as_its_reason(self):
        cycle, record = self.changed_host()
        record['reason'] = 'review_scope_unaffordable'
        with self.assertRaisesRegex(ValueError, 'minimum review scope fits the execution limit'):
            rc.validate_resource_disposition(cycle, self.engine.runtime)
