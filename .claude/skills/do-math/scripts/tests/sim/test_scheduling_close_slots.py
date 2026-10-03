"""실제 SessionSlots의 오류 전 원자성·동일성·공급자 결과 음성 분기."""
from copy import deepcopy
import unittest

from do_math.launch import mark_dispatched
from support.scheduling_slots import reserve, slot_sim, slots


def setUpModule():
    slot_sim()


class SlotBranchTests(unittest.TestCase):
    def test_identity_mismatch_never_changes_reservations(self):
        sim = slot_sim()
        profile = next(iter(sim.instance['execution_profiles'].values()))
        before = deepcopy(sim.runtime)
        with self.assertRaisesRegex(ValueError, '^execution identity differs from admission$'):
            slots(sim).acquire('EX-request', profile=profile, execution={'id': 'EX-other'})
        self.assertEqual(sim.runtime, before)

    def test_started_identity_is_fixed_and_repeat_is_idempotent(self):
        sim = slot_sim()
        accepted, execution = reserve(sim, 'EX-start')
        self.assertTrue(accepted)
        book = slots(sim)
        ticket = execution['launch_ticket']
        mark_dispatched(ticket)
        identity = {'job_name': ticket['job_name'], 'pid': 81, 'creation_filetime': '1234567890'}
        with self.assertRaisesRegex(ValueError, '^started Job differs from the published launch ticket$'):
            book.started('EX-start', {**identity, 'job_name': 'other'}, at=sim.clock.now())
        self.assertIsNone(execution['capacity']['process'])
        book.started('EX-start', identity, at=sim.clock.now())
        before = deepcopy(sim.runtime)
        sim.advance(1)
        self.assertIs(book.started('EX-start', identity, at=sim.clock.now()), execution)
        self.assertEqual(sim.runtime, before)
        with self.assertRaisesRegex(ValueError, '^execution process identity is already fixed$'):
            book.started('EX-start', {**identity, 'pid': 82}, at=sim.clock.now())
        self.assertEqual(sim.runtime, before)
        sim.engine._save()
        _, _, stored = sim.engine.store.load(sim.engine.head)
        self.assertEqual(stored['executions']['EX-start']['capacity']['process'], identity)

    def test_release_missing_and_unadmitted_execution_has_no_effect(self):
        sim = slot_sim()
        before = deepcopy(sim.runtime)
        self.assertFalse(slots(sim).release('EX-missing'))
        self.assertEqual(sim.runtime, before)

    def test_provider_result_requires_admitted_matching_provider(self):
        sim = slot_sim()
        config = {'provider_retry_initial_seconds': 10, 'provider_retry_max_seconds': 100}
        before = deepcopy(sim.runtime)
        with self.assertRaisesRegex(ValueError, '^provider result has no matching admitted execution$'):
            slots(sim).provider_result_from_run('EX-missing', {'status': 'completed'}, config)
        self.assertEqual(sim.runtime, before)
        accepted, row = reserve(sim, 'EX-provider')
        self.assertTrue(accepted)
        before = deepcopy(sim.runtime)
        for failure in ({'kind': 'other', 'provider': row['capacity']['provider']},
                        {'kind': 'provider_limit', 'provider': 'other'}):
            with self.subTest(failure=failure):
                with self.assertRaisesRegex(ValueError, '^provider failure differs from admission$'):
                    slots(sim).provider_result_from_run('EX-provider', {
                        'error_kind': 'provider_limit', 'failure': failure}, config)
                self.assertEqual(sim.runtime, before)
