"""Delegated publication binds the preserved approval and the current case.

The existing delegation fixtures belong to the governance region; this consumer
uses their public producers without changing that region's tests or helpers.
"""
from copy import deepcopy
import unittest

from do_math import delegations
from do_math.canonical import exact_content_hash
from support.entry import entry
from support.governance_delegation import replacement_case


class DelegatedPublicationTests(unittest.TestCase):
    def test_each_decision_keeps_the_hash_of_its_preserved_source(self):
        for decision_id in ('ORIGINAL', 'DD'):
            instance, runtime, _, case = replacement_case()
            decision = instance['decisions'][decision_id]
            decision['source_sha256'] = '0' * 64
            if decision_id == 'ORIGINAL':
                instance['decisions']['DD']['original_decision_sha256'] = exact_content_hash(decision)
            before = deepcopy((instance, runtime))
            with self.subTest(decision=decision_id), self.assertRaisesRegex(
                    ValueError, '^decision source differs from its preserved approval$'):
                delegations.prepare_application(instance, runtime, 'DG', case, now_iso=entry().ports.clock.now())
            self.assertEqual((instance, runtime), before)


    def test_case_id_cannot_be_reused_for_a_different_effect(self):
        instance, runtime, _, case = replacement_case()
        now = entry().ports.clock.now()
        application = delegations.prepare_application(instance, runtime, 'DG', case, now_iso=now)
        self.assertEqual(delegations.prepare_application(instance, runtime, 'DG', case, now_iso=now), application)
        changed = deepcopy(case)
        changed['effect']['reason'] = 'different authorized effect'
        before = deepcopy(runtime)
        with self.assertRaisesRegex(ValueError, '^delegation case ID reused with different content$'):
            delegations.prepare_application(instance, runtime, 'DG', changed, now_iso=now)
        self.assertEqual(runtime, before)

    def test_reusing_a_case_rechecks_current_and_preserved_basis(self):
        for fault in ('current', 'preserved'):
            instance, runtime, _, case = replacement_case()
            now = entry().ports.clock.now()
            application = delegations.prepare_application(instance, runtime, 'DG', case, now_iso=now)
            if fault == 'current':
                instance['knowledge']['K']['revision'] += 1
            else:
                runtime['delegation_applications'][application['id']]['basis']['target']['revision'] += 1
            before = deepcopy((instance, runtime))
            with self.subTest(fault=fault), self.assertRaisesRegex(ValueError, '^delegation application stale$'):
                delegations.prepare_application(instance, runtime, 'DG', case, now_iso=now)
            self.assertEqual((instance, runtime), before)




class ExternalPublicationTests(unittest.TestCase):
    def test_retry_preserves_a_separate_user_resume_wait(self):
        from do_math import activities
        from support.engine_lifecycle import external_sim, http_grant, run_machine
        from support.academic_scenes import user_source
        sim = external_sim()
        engine = sim.engine
        config, source = http_grant(engine), user_source(engine)
        engine._external_control(config, source)
        sim.ports.http.table['/effect'] = (503, b'uncertain', None)
        run_machine(sim, 'external_action')
        operation = deepcopy(engine.runtime['external_operations'][config['id']])
        self.assertEqual(operation['status'], 'unknown')
        owner = engine.runtime['executions'][operation['execution_id']]['owner_activity_id']
        activities.wait_for(engine.runtime, owner, kind='user_resume', reason='A separate user pause',
            condition={'pause_id': 'pause-during-reconciliation'}, next_owner='user', at=sim.clock.now())
        waiting = deepcopy(engine.runtime['activities'][owner])
        proof = {'kind': 'verified_idempotency', 'request_sha256': operation['request_sha256'],
                 'idempotency_key': operation['idempotency_key'], 'evidence_ref': 'remote:idempotency-contract',
                 'valid_until': '2199-01-01T00:00:00Z'}
        engine._external_control({**config, 'operation': 'retry', 'evidence': proof}, source)
        self.assertEqual(engine.runtime['activities'][owner], waiting)
        result = engine.runtime['external_operations'][config['id']]
        self.assertEqual((result['status'], result['continuation_of']), ('prepared', operation['execution_id']))
        self.assertEqual(len(sim.ports.http.requests), 1)
