"""해석 재작성은 정상 봉인 부모와 원문 계보를 보존해야 한다."""
from copy import deepcopy
import re
import unittest
from do_math import governance as gov
from support.governance_sim import checked_sim, checked_bundle

class GovernanceReworkContractTests(unittest.TestCase):
    def test_different_exact_source(self):
        sim = checked_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        bundle = r['intent_imports'][checked_bundle(sim)['id']]
        source = deepcopy(bundle['source'])
        output = deepcopy(bundle['output'])
        output['repair'] = {'previous_sha256': bundle['sha256'], 'changed_unit_ids': [], 'actions': ['현재 전제를 다시 검토한다.']}
        previous = bundle['id']
        source = gov.preserve_source(source['id'], '바뀐 원문', origin='user')
        before = deepcopy((i, r, output, source))
        with self.assertRaisesRegex(ValueError, '^' + re.escape('source differs from the exact public input') + '$'):
            gov.prepare_import(i, r, source, output, execution_id=bundle['execution_id'], input_ref=bundle['input_ref'],
                               previous_id=previous, owner_handlers=sim.engine.governance_owner_handlers(), clock=sim.clock)
        self.assertEqual((i, r, output, source), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_missing_parent(self):
        sim = checked_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        bundle = r['intent_imports'][checked_bundle(sim)['id']]
        source = deepcopy(bundle['source'])
        output = deepcopy(bundle['output'])
        output['repair'] = {'previous_sha256': bundle['sha256'], 'changed_unit_ids': [], 'actions': ['현재 전제를 다시 검토한다.']}
        previous = bundle['id']
        previous = 'missing'
        before = deepcopy((i, r, output, source))
        with self.assertRaisesRegex(ValueError, '^' + re.escape('rework must follow a sealed failed or changed import') + '$'):
            gov.prepare_import(i, r, source, output, execution_id=bundle['execution_id'], input_ref=bundle['input_ref'],
                               previous_id=previous, owner_handlers=sim.engine.governance_owner_handlers(), clock=sim.clock)
        self.assertEqual((i, r, output, source), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_superseded_parent(self):
        sim = checked_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        bundle = r['intent_imports'][checked_bundle(sim)['id']]
        source = deepcopy(bundle['source'])
        output = deepcopy(bundle['output'])
        output['repair'] = {'previous_sha256': bundle['sha256'], 'changed_unit_ids': [], 'actions': ['현재 전제를 다시 검토한다.']}
        previous = bundle['id']
        bundle['superseded_by'] = 'next'
        before = deepcopy((i, r, output, source))
        with self.assertRaisesRegex(ValueError, '^' + re.escape('rework must follow a sealed failed or changed import') + '$'):
            gov.prepare_import(i, r, source, output, execution_id=bundle['execution_id'], input_ref=bundle['input_ref'],
                               previous_id=previous, owner_handlers=sim.engine.governance_owner_handlers(), clock=sim.clock)
        self.assertEqual((i, r, output, source), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_changed_parent_seal(self):
        sim = checked_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        bundle = r['intent_imports'][checked_bundle(sim)['id']]
        source = deepcopy(bundle['source'])
        output = deepcopy(bundle['output'])
        output['repair'] = {'previous_sha256': bundle['sha256'], 'changed_unit_ids': [], 'actions': ['현재 전제를 다시 검토한다.']}
        previous = bundle['id']
        bundle['sha256'] = '0' * 64
        before = deepcopy((i, r, output, source))
        with self.assertRaisesRegex(ValueError, '^' + re.escape('rework parent seal changed') + '$'):
            gov.prepare_import(i, r, source, output, execution_id=bundle['execution_id'], input_ref=bundle['input_ref'],
                               previous_id=previous, owner_handlers=sim.engine.governance_owner_handlers(), clock=sim.clock)
        self.assertEqual((i, r, output, source), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_missing_repair_unit(self):
        sim = checked_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        bundle = r['intent_imports'][checked_bundle(sim)['id']]
        source = deepcopy(bundle['source'])
        output = deepcopy(bundle['output'])
        output['repair'] = {'previous_sha256': bundle['sha256'], 'changed_unit_ids': [], 'actions': ['현재 전제를 다시 검토한다.']}
        previous = bundle['id']
        output['repair']['changed_unit_ids'] = ['missing']
        before = deepcopy((i, r, output, source))
        with self.assertRaisesRegex(ValueError, '^' + re.escape('repair unit missing') + '$'):
            gov.prepare_import(i, r, source, output, execution_id=bundle['execution_id'], input_ref=bundle['input_ref'],
                               previous_id=previous, owner_handlers=sim.engine.governance_owner_handlers(), clock=sim.clock)
        self.assertEqual((i, r, output, source), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_reused_source_identity(self):
        sim = checked_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        bundle = r['intent_imports'][checked_bundle(sim)['id']]
        source = deepcopy(bundle['source'])
        output = deepcopy(bundle['output'])
        output['repair'] = {'previous_sha256': bundle['sha256'], 'changed_unit_ids': [], 'actions': ['현재 전제를 다시 검토한다.']}
        previous = bundle['id']
        previous = None
        i['governance_sources'][source['id']] = gov.preserve_source(source['id'], '다른 원문', origin='user')
        before = deepcopy((i, r, output, source))
        with self.assertRaisesRegex(ValueError, '^' + re.escape('source identity reused with different bytes') + '$'):
            gov.prepare_import(i, r, source, output, execution_id=bundle['execution_id'], input_ref=bundle['input_ref'],
                               previous_id=previous, owner_handlers=sim.engine.governance_owner_handlers(), clock=sim.clock)
        self.assertEqual((i, r, output, source), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)
