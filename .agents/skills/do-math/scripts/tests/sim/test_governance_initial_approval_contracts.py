"""공개 최초 승인에서 생산된 원천·승인·헌장의 거부 전제."""
from copy import deepcopy
import re
import unittest

from do_math import governance as gov
from support.governance_cases import initial_approval_scene

class GovernanceInitialApprovalTests(unittest.TestCase):
    def test_already_initialized(self):
        sim, i, r, source, approval, approval_source, records = initial_approval_scene()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i['governance'] = deepcopy(sim.instance['governance'])
        before = deepcopy((i, r, approval, approval_source, records, source))
        with self.assertRaisesRegex(ValueError, '^' + re.escape('governance is already initialized') + '$'):
            gov.initialize_governance(i, source, approval, records, approval_source=approval_source)
        self.assertEqual((i, r, approval, approval_source, records, source), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_original_input_binding(self):
        sim, i, r, source, approval, approval_source, records = initial_approval_scene()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        approval['input_source_ref'] = 'missing'
        before = deepcopy((i, r, approval, approval_source, records, source))
        with self.assertRaisesRegex(ValueError, '^' + re.escape('approval does not bind the original initialization input') + '$'):
            gov.initialize_governance(i, source, approval, records, approval_source=approval_source)
        self.assertEqual((i, r, approval, approval_source, records, source), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_record_hash_binding(self):
        sim, i, r, source, approval, approval_source, records = initial_approval_scene()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        approval['record_hashes'] = {}
        before = deepcopy((i, r, approval, approval_source, records, source))
        with self.assertRaisesRegex(ValueError, '^' + re.escape('approval must bind the exact proposed records') + '$'):
            gov.initialize_governance(i, source, approval, records, approval_source=approval_source)
        self.assertEqual((i, r, approval, approval_source, records, source), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_source_identity_collision(self):
        sim, i, r, source, approval, approval_source, records = initial_approval_scene()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i['governance_sources'][source['id']] = gov.preserve_source(source['id'], '다른 원문', origin='user')
        before = deepcopy((i, r, approval, approval_source, records, source))
        with self.assertRaisesRegex(ValueError, '^' + re.escape('source ID already bound') + '$'):
            gov.initialize_governance(i, source, approval, records, approval_source=approval_source)
        self.assertEqual((i, r, approval, approval_source, records, source), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_approval_identity_collision(self):
        sim, i, r, source, approval, approval_source, records = initial_approval_scene()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i['decisions'][approval['id']] = deepcopy(approval)
        before = deepcopy((i, r, approval, approval_source, records, source))
        with self.assertRaisesRegex(ValueError, '^' + re.escape('initial approval ID already exists') + '$'):
            gov.initialize_governance(i, source, approval, records, approval_source=approval_source)
        self.assertEqual((i, r, approval, approval_source, records, source), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_approval_source_collision(self):
        sim, i, r, source, approval, approval_source, records = initial_approval_scene()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i['governance_sources'][approval_source['id']] = gov.preserve_source(approval_source['id'], '다른 승인', origin='user')
        before = deepcopy((i, r, approval, approval_source, records, source))
        with self.assertRaisesRegex(ValueError, '^' + re.escape('approval original source ID already bound') + '$'):
            gov.initialize_governance(i, source, approval, records, approval_source=approval_source)
        self.assertEqual((i, r, approval, approval_source, records, source), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_nonuser_approval(self):
        sim, i, r, source, approval, approval_source, records = initial_approval_scene()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        approval['actor'] = 'ai'
        before = deepcopy((i, r, approval, approval_source, records, source))
        with self.assertRaisesRegex(ValueError, '^' + re.escape('initialization requires actual user approval of the immutable input') + '$'):
            gov.initialize_governance(i, source, approval, records, approval_source=approval_source)
        self.assertEqual((i, r, approval, approval_source, records, source), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)
