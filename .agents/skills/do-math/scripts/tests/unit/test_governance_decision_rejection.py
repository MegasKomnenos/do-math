"""사용자 결정 생산자의 정상 제안에서 거부 입력을 만든다."""
from copy import deepcopy
import re
import unittest

from do_math import governance as gov
from support.governance_cases import delegated_sim

class GovernanceDecisionRejectionTests(unittest.TestCase):
    def test_grant_kind(self):
        sim = delegated_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        change = deepcopy(i['decisions']['DC-close-original']['change'])
        change['decision_id'] = 'DC-close-new'
        change['grant']['id'] = 'GR-close-new'
        change['grant']['kind'] = 'unknown'
        before = deepcopy((i, r))
        with self.assertRaisesRegex(ValueError, '^' + re.escape('grant kind must be local or http') + '$'):
            gov.apply_decision(i, r, change, source_ref='GS-close-delegation', clock=sim.clock)
        self.assertEqual((i, r), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_grant_expired(self):
        sim = delegated_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        change = deepcopy(i['decisions']['DC-close-original']['change'])
        change['decision_id'] = 'DC-close-new'
        change['grant']['id'] = 'GR-close-new'
        change['grant']['expires_at'] = sim.clock.now()
        before = deepcopy((i, r))
        with self.assertRaisesRegex(ValueError, '^' + re.escape('new grant has already expired') + '$'):
            gov.apply_decision(i, r, change, source_ref='GS-close-delegation', clock=sim.clock)
        self.assertEqual((i, r), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_grant_roles_empty(self):
        sim = delegated_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        change = deepcopy(i['decisions']['DC-close-original']['change'])
        change['decision_id'] = 'DC-close-new'
        change['grant']['id'] = 'GR-close-new'
        change['grant']['roles'] = []
        before = deepcopy((i, r))
        with self.assertRaisesRegex(ValueError, '^' + re.escape('local grant requires supported roles') + '$'):
            gov.apply_decision(i, r, change, source_ref='GS-close-delegation', clock=sim.clock)
        self.assertEqual((i, r), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_grant_roles_unknown(self):
        sim = delegated_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        change = deepcopy(i['decisions']['DC-close-original']['change'])
        change['decision_id'] = 'DC-close-new'
        change['grant']['id'] = 'GR-close-new'
        change['grant']['roles'] = ['unknown']
        before = deepcopy((i, r))
        with self.assertRaisesRegex(ValueError, '^' + re.escape('local grant requires supported roles') + '$'):
            gov.apply_decision(i, r, change, source_ref='GS-close-delegation', clock=sim.clock)
        self.assertEqual((i, r), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_grant_duplicate(self):
        sim = delegated_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        change = deepcopy(i['decisions']['DC-close-original']['change'])
        change['decision_id'] = 'DC-close-new'
        change['grant']['id'] = 'GR-close-new'
        change['grant']['id'] = 'GR-close'
        before = deepcopy((i, r))
        with self.assertRaisesRegex(ValueError, '^' + re.escape('grant ID already exists; revoke it before replacing authority') + '$'):
            gov.apply_decision(i, r, change, source_ref='GS-close-delegation', clock=sim.clock)
        self.assertEqual((i, r), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_grant_reuse(self):
        sim = delegated_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        change = deepcopy(i['decisions']['DC-close-original']['change'])
        change['decision_id'] = 'DC-close-new'
        change['grant']['id'] = 'GR-close-new'
        change['grant']['reuse'] = 'forever'
        before = deepcopy((i, r))
        with self.assertRaisesRegex(ValueError, '^' + re.escape('grant reuse must be explicit once or reusable') + '$'):
            gov.apply_decision(i, r, change, source_ref='GS-close-delegation', clock=sim.clock)
        self.assertEqual((i, r), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_replacement_missing(self):
        sim = delegated_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        change = deepcopy(i['decisions']['DC-close-original']['change'])
        change['decision_id'] = 'DC-close-new'
        change['grant']['id'] = 'GR-close-new'
        change['replaces'] = ['missing']
        before = deepcopy((i, r))
        with self.assertRaisesRegex(ValueError, '^' + re.escape('replacement requires distinct active grants') + '$'):
            gov.apply_decision(i, r, change, source_ref='GS-close-delegation', clock=sim.clock)
        self.assertEqual((i, r), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_replacement_self(self):
        sim = delegated_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        change = deepcopy(i['decisions']['DC-close-original']['change'])
        change['decision_id'] = 'DC-close-new'
        change['grant']['id'] = 'GR-close-new'
        change['replaces'] = ['GR-close-new']
        before = deepcopy((i, r))
        with self.assertRaisesRegex(ValueError, '^' + re.escape('replacement requires distinct active grants') + '$'):
            gov.apply_decision(i, r, change, source_ref='GS-close-delegation', clock=sim.clock)
        self.assertEqual((i, r), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_http_origins_missing(self):
        sim = delegated_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        change = deepcopy(i['decisions']['DC-close-original']['change'])
        change['decision_id'] = 'DC-close-new'
        change['grant']['id'] = 'GR-close-new'
        change['grant']['kind'] = 'http'
        before = deepcopy((i, r))
        with self.assertRaisesRegex(ValueError, '^' + re.escape('HTTP grant must specify origins and methods') + '$'):
            gov.apply_decision(i, r, change, source_ref='GS-close-delegation', clock=sim.clock)
        self.assertEqual((i, r), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_decision_reused(self):
        sim = delegated_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        change = deepcopy(i['decisions']['DC-close-original']['change'])
        change['decision_id'] = 'DC-close-new'
        change['grant']['id'] = 'GR-close-new'
        change = deepcopy(i['decisions']['DC-close-original']['change'])
        change['grant']['reuse'] = 'once'
        before = deepcopy((i, r))
        with self.assertRaisesRegex(ValueError, '^' + re.escape('decision ID reused with different content') + '$'):
            gov.apply_decision(i, r, change, source_ref='GS-close-delegation', clock=sim.clock)
        self.assertEqual((i, r), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_original_decision_missing(self):
        sim = delegated_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        change = deepcopy(i['decisions']['DC-close-delegation']['change'])
        change['decision_id'] = 'DC-close-new'
        change['delegation']['id'] = 'DG-close-new'
        change['delegation']['original_decision_id'] = 'missing'
        before = deepcopy((i, r))
        with self.assertRaisesRegex(ValueError, '^' + re.escape('delegation must bind an actual current user decision of the same kind') + '$'):
            gov.apply_decision(i, r, change, source_ref='GS-close-delegation', clock=sim.clock)
        self.assertEqual((i, r), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_delegation_duplicate(self):
        sim = delegated_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        change = deepcopy(i['decisions']['DC-close-delegation']['change'])
        change['decision_id'] = 'DC-close-new'
        change['delegation']['id'] = 'DG-close-new'
        change['delegation']['id'] = 'DG-close'
        before = deepcopy((i, r))
        with self.assertRaisesRegex(ValueError, '^' + re.escape('delegation ID already exists') + '$'):
            gov.apply_decision(i, r, change, source_ref='GS-close-delegation', clock=sim.clock)
        self.assertEqual((i, r), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_revoke_missing(self):
        sim = delegated_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        change = deepcopy(i['decisions']['DC-close-delegation']['change'])
        change['decision_id'] = 'DC-close-new'
        change['delegation']['id'] = 'DG-close-new'
        change = {'kind': 'revoke', 'grant_id': 'missing'}
        before = deepcopy((i, r))
        with self.assertRaisesRegex(ValueError, '^' + re.escape('grant not found') + '$'):
            gov.apply_decision(i, r, change, source_ref='GS-close-delegation', clock=sim.clock)
        self.assertEqual((i, r), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_revoke_delegation_missing(self):
        sim = delegated_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        change = deepcopy(i['decisions']['DC-close-delegation']['change'])
        change['decision_id'] = 'DC-close-new'
        change['delegation']['id'] = 'DG-close-new'
        change = {'kind': 'revoke_delegation', 'delegation_id': 'missing'}
        before = deepcopy((i, r))
        with self.assertRaisesRegex(ValueError, '^' + re.escape('delegation not found') + '$'):
            gov.apply_decision(i, r, change, source_ref='GS-close-delegation', clock=sim.clock)
        self.assertEqual((i, r), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_unsupported_decision(self):
        sim = delegated_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        change = deepcopy(i['decisions']['DC-close-delegation']['change'])
        change['decision_id'] = 'DC-close-new'
        change['delegation']['id'] = 'DG-close-new'
        change = {'kind': 'unknown'}
        before = deepcopy((i, r))
        with self.assertRaisesRegex(ValueError, '^' + re.escape('unsupported governance decision: unknown') + '$'):
            gov.apply_decision(i, r, change, source_ref='GS-close-delegation', clock=sim.clock)
        self.assertEqual((i, r), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)
