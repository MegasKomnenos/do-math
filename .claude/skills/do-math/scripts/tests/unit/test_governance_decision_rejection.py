"""사용자 결정 생산자의 정상 제안에서 거부 입력을 만든다."""
from copy import deepcopy
import re
import unittest

from do_math import governance as gov
from support.governance_cases import delegated_sim

class GovernanceDecisionRejectionTests(unittest.TestCase):
    def test_delegation_rejects_a_changed_original_approval_source(self):
        sim = delegated_sim()
        i, r = deepcopy((sim.instance, sim.runtime))
        change = deepcopy(i['decisions']['DC-close-delegation']['change'])
        change['decision_id'] = 'DC-new-delegation'
        change['delegation']['id'] = 'DG-new-delegation'
        original = i['decisions']['DC-close-original']
        source = i['governance_sources'][original['source_ref']]
        i['governance_sources'][source['id']] = gov.preserve_source(
            source['id'], source['text'] + ' changed instruction', origin='user')
        before = deepcopy((i, r, change))
        with self.assertRaises(ValueError) as caught:
            gov.apply_decision(i, r, change, source_ref=source['id'], clock=sim.clock)
        self.assertEqual(str(caught.exception), 'original decision source differs from its preserved approval')
        self.assertEqual((i, r, change), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], (sim.instance, sim.runtime))

    def test_review_replacement_decision_requires_the_current_unsealed_slot(self):
        import tempfile
        from do_math.review_cycle import slot_key
        from support.governance_cases import replacement_engine
        with tempfile.TemporaryDirectory() as directory:
            engine, action = replacement_engine(directory)
            change = {'kind': 'review_replacement', 'grant_id': action['grant_id'],
                      'allowed_action': deepcopy(action)}
            source = engine.instance['grants'][action['grant_id']]['source_ref']
            for kind, reason in (
                ('target', 'review replacement decision requires the exact current review action'),
                ('sealed', 'review replacement decision requires an unsealed review slot'),
            ):
                i, r, proposed = deepcopy((engine.instance, engine.runtime, change))
                if kind == 'target':
                    proposed['allowed_action']['target'] = 'KN-different'
                else:
                    r['review_cycles'][action['review_cycle_id']]['results'][slot_key(action)] = {
                        'execution_id': 'EX-already-sealed'}
                before = deepcopy((i, r, proposed))
                with self.subTest(kind=kind), self.assertRaises(ValueError) as caught:
                    gov.apply_decision(i, r, proposed, source_ref=source, clock=engine.ports.clock)
                self.assertEqual(str(caught.exception), reason)
                self.assertEqual((i, r, proposed), before)

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
