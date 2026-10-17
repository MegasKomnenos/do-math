"""4-B: every formal wait uses its declared condition and preserves explicit stops."""
from copy import deepcopy
import json
from pathlib import Path
import unittest

from do_math import trust_validation
from do_math.governance import authorize
from support.engine_lifecycle import applied
from do_math.wait_rules import FORMAL_WAIT_RULES, FORMAL_RECOVERABLE_STOPS, formal_wait
from support.knowledge_formal_engine import attempts, parked, run_formal, scene, stop_with_control, warm_scenes
from support.wait_reporting import assert_wait_report

setUpModule = warm_scenes


class FormalWaitContractTests(unittest.TestCase):
    def test_resolving_one_of_two_owner_obligations_preserves_the_remaining_wait(self):
        from do_math.activities import wait_for
        sim, action, environment, binding, owner = parked()
        second = {**deepcopy(action), 'id': sim.clock.new_id('AC')}
        sim.runtime['waiting_actions'][second['id']] = formal_wait(second, 'formal_stopped', 'explicit stop',
            detail={'stop_reasons': ['execution_stop_requested']})
        condition = {'action_ids': [action['id'], second['id']]}
        wait_for(sim.runtime, owner, kind='formal_authority', reason='two formal obligations',
            condition=condition, next_owner='trust_governance', at=sim.clock.now())
        held = deepcopy(sim.runtime['activities'][owner])
        sim.instance['trust_environments'][environment['id']] = environment
        sim.runtime['trust_bindings'][environment['id']] = binding
        sim.instance['active_trust_environment'] = environment['id']
        sim.engine._save()
        sim.engine._resume_formal_waits()
        self.assertNotIn(action['id'], sim.runtime['waiting_actions'])
        self.assertIn(second['id'], sim.runtime['waiting_actions'])
        self.assertEqual(sim.runtime['activities'][owner], held)
        self.assertEqual([a['id'] for a in sim.runtime['queue']], [action['id']])
        sim.engine._save()
        self.assertEqual(sim.engine.store.load()[2]['activities'][owner], held)

    def test_actual_authority_stop_waits_for_exact_role_and_preserves_attempt(self):
        sim, action = scene()
        grant_id = authorize(sim.instance, action, runtime=sim.runtime, at=sim.clock.now())['grant_id']
        stop_with_control(sim, action, 'decision', config={'change': {'kind': 'revoke', 'grant_id': grant_id}})
        first, = attempts(sim)
        waiting = deepcopy(sim.runtime['waiting_actions'][action['id']])
        self.assertEqual(waiting['kind'], 'formal_stopped')
        self.assertIn('authority_changed', waiting['detail']['stop_reasons'])
        self.assertNotIn('execution_stop_requested', waiting['detail']['stop_reasons'])
        self.assertEqual(first['stop_requested'], 'grant_revoked')
        assert_wait_report(self, sim.engine, action['id'])
        original = sim.engine.store.read(first['result_ref'], sim.engine.head)
        held = deepcopy(sim.runtime)
        for _ in range(2):
            sim.engine._resume_formal_waits()
            self.assertEqual(sim.runtime, held)
        applied(sim, 'decision', config={'change': {'kind': 'grant', 'grant': {
            'id': 'GR-other-role', 'kind': 'local', 'roles': ['maintenance'], 'reuse': 'reusable'}}})
        self.assertEqual(sim.runtime['waiting_actions'][action['id']], waiting)
        applied(sim, 'decision', config={'change': {'kind': 'grant', 'grant': {
            'id': 'GR-formal-restored', 'kind': 'local', 'roles': ['formal_check'], 'reuse': 'reusable'}}})
        sim.engine._resume_formal_waits()
        successor, = [row for row in sim.runtime['queue'] if row['id'] == action['id']]
        self.assertEqual(successor['continuation_of'], first['id'])
        self.assertEqual(sim.runtime['activities'][first['owner_activity_id']]['status'], 'ready')
        run_formal(sim, successor)
        second, = [row for row in attempts(sim) if row['id'] != first['id']]
        self.assertEqual((second['owner_activity_id'], second['continuation_of'], second['formal_status']),
                         (first['owner_activity_id'], first['id'], 'verified'))
        self.assertEqual(sim.engine.store.read(first['result_ref'], sim.engine.head), original)
        self.assertEqual(sim.runtime['executions'][first['id']], first)

    def test_live_environment_failure_preserves_wait_until_record_repair_and_one_successor(self):
        sim, action = scene()
        engine = sim.engine
        environment = sim.instance['trust_environments'][sim.instance['active_trust_environment']]
        # Own only the record path; never alter a restored template's shared toolchain.
        original = Path(environment['toolchain_record']['path']).read_bytes()
        record = sim.root / 'owned-records' / Path(environment['toolchain_record']['path']).name
        record.parent.mkdir()
        record.write_bytes(b'{')
        environment['toolchain_record']['path'] = str(record)
        engine._save()
        run_formal(sim, action)
        first, = attempts(sim)
        waiting = deepcopy(sim.runtime['waiting_actions'][action['id']])
        self.assertEqual(waiting['kind'], 'formal_environment')
        self.assertEqual(waiting['detail'], trust_validation.wait_detail(sim.instance))
        self.assertEqual(first['outcome'], 'execution_incomplete')
        self.assertNotIn('submission_receipt', first)
        raw = engine.store.read(first['result_ref'], engine.head)
        self.assertEqual(json.loads(raw)['error_kind'], 'trust_environment')
        assert_wait_report(self, engine, action['id'])
        held = deepcopy(sim.runtime)
        for _ in range(2):
            engine._resume_formal_waits()
            self.assertEqual(sim.runtime, held)
        record.write_bytes(original)
        engine._resume_formal_waits()
        successor, = [row for row in sim.runtime['queue'] if row['id'] == action['id']]
        self.assertEqual(successor['continuation_of'], first['id'])
        owner = first['owner_activity_id']
        self.assertEqual(sim.runtime['activities'][owner]['status'], 'ready')
        resumed = deepcopy(sim.runtime)
        engine._resume_formal_waits()
        self.assertEqual(sim.runtime, resumed)
        run_formal(sim, successor)
        second, = [row for row in attempts(sim) if row['id'] != first['id']]
        self.assertEqual((second['continuation_of'], second['owner_activity_id'], second['formal_status']),
                         (first['id'], owner, 'verified'))
        self.assertEqual(engine.store.read(first['result_ref'], engine.head), raw)
        self.assertEqual(sim.runtime['executions'][first['id']], first)

    def test_every_declared_formal_wait_has_a_negative_condition_and_exact_release(self):
        for kind, rule in FORMAL_WAIT_RULES.items():
            reasons = (*sorted(FORMAL_RECOVERABLE_STOPS), 'execution_stop_requested') if kind == 'formal_stopped' else (None,)
            for stopped_by in reasons:
                with self.subTest(kind=kind, stopped_by=stopped_by):
                    sim, action, environment, binding, _ = parked()
                    detail = (trust_validation.wait_detail(sim.instance) if kind == 'formal_environment' else
                              {'stop_reasons': [stopped_by]} if kind == 'formal_stopped' else None)
                    if kind == 'formal_authority':
                        # parked() ran the real formal owner with no active environment.
                        entry = deepcopy(sim.runtime['waiting_actions'][action['id']])
                        self.assertEqual(entry['kind'], kind)
                        self.assertEqual(entry['action']['id'], action['id'])
                    else:
                        # Resolver cases; actual environment/stop producers have separate owner tests.
                        entry = formal_wait(action, kind, 'Held formal check', detail=detail)
                        sim.runtime['waiting_actions'][action['id']] = entry
                    sim.engine._save()
                    assert_wait_report(self, sim.engine, action['id'])
                    before = deepcopy((sim.instance, sim.runtime))
                    for _ in range(2):
                        sim.engine._resume_formal_waits()
                        self.assertEqual((sim.instance, sim.runtime), before)
                    sim.instance['trust_environments'][environment['id']] = environment
                    sim.runtime['trust_bindings'][environment['id']] = binding
                    sim.instance['active_trust_environment'] = environment['id']
                    if stopped_by == 'execution_stop_requested':
                        held = deepcopy(sim.runtime)
                        sim.engine._resume_formal_waits()
                        self.assertEqual(sim.runtime, held)
                        self.assertEqual(sim.runtime['waiting_actions'][action['id']], entry)
                    else:
                        sim.engine._resume_formal_waits()
                        self.assertNotIn(action['id'], sim.runtime['waiting_actions'])
                        queued = [row for row in sim.runtime['queue'] if row['id'] == action['id']]
                        self.assertEqual(queued, [action])
                        resumed = deepcopy(sim.runtime)
                        sim.engine._resume_formal_waits()
                        self.assertEqual(sim.runtime, resumed)
                        sim.engine._save()
                        self.assertEqual(sim.engine.store.load()[2]['queue'], sim.runtime['queue'])
