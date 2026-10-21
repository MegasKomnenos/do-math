"""실제 해석 생산자의 원문·질문·봉인 계약을 한 필드씩 검증한다."""
from copy import deepcopy
import re
import unittest

from do_math import governance as gov
from do_math.canonical import exact_content_hash
from support.governance_sim import checked_sim, checked_bundle

class GovernanceImportSealRejectionTests(unittest.TestCase):
    def test_exact_change_approval_still_requires_its_preserved_original(self):
        from do_math.canonical import exact_content_hash
        sim = checked_sim()
        bundle = checked_bundle(sim)
        approvals = {unit['unit_id']: {'actor': 'user', 'source_ref': 'GS-unavailable',
            'source_sha256': 'a' * 64, 'change_sha256': exact_content_hash(unit['payload'])}
            for unit in bundle['output']['import_units'] if unit['payload']}
        before = deepcopy((sim.instance, sim.runtime, approvals))
        with self.assertRaises(ValueError) as caught:
            gov.apply_import(sim.instance, sim.runtime, bundle['id'], approvals=approvals,
                owner_handlers=sim.engine.governance_owner_handlers(), clock=sim.clock)
        self.assertEqual(str(caught.exception), 'change approval original is unavailable')
        self.assertEqual((sim.instance, sim.runtime, approvals), before)

    def test_missing_import(self):
        sim = checked_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        bundle = r['intent_imports'][checked_bundle(sim)['id']]
        identifier = bundle['id']
        handlers = sim.engine.governance_owner_handlers()
        identifier = 'missing'
        before = deepcopy((i, r))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('import is absent or superseded') + "$"):
            gov.current_import(i, r, identifier, owner_handlers=handlers, clock=sim.clock)
        self.assertEqual((i, r), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_superseded_import(self):
        sim = checked_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        bundle = r['intent_imports'][checked_bundle(sim)['id']]
        identifier = bundle['id']
        handlers = sim.engine.governance_owner_handlers()
        bundle['superseded_by'] = 'IM-next'
        before = deepcopy((i, r))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('import is absent or superseded') + "$"):
            gov.current_import(i, r, identifier, owner_handlers=handlers, clock=sim.clock)
        self.assertEqual((i, r), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_original_public_input(self):
        sim = checked_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        bundle = r['intent_imports'][checked_bundle(sim)['id']]
        identifier = bundle['id']
        handlers = sim.engine.governance_owner_handlers()
        next(row for row in r['inputs'] if row['id'] == bundle['input_ref'])['text'] += '!'
        before = deepcopy((i, r))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('original public input changed') + "$"):
            gov.current_import(i, r, identifier, owner_handlers=handlers, clock=sim.clock)
        self.assertEqual((i, r), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_bundle_seal(self):
        sim = checked_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        bundle = r['intent_imports'][checked_bundle(sim)['id']]
        identifier = bundle['id']
        handlers = sim.engine.governance_owner_handlers()
        bundle['sha256'] = '0' * 64
        before = deepcopy((i, r))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('sealed import changed') + "$"):
            gov.current_import(i, r, identifier, owner_handlers=handlers, clock=sim.clock)
        self.assertEqual((i, r), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_original_version(self):
        sim = checked_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        bundle = r['intent_imports'][checked_bundle(sim)['id']]
        identifier = bundle['id']
        handlers = sim.engine.governance_owner_handlers()
        i['governance_sources'][bundle['source']['id']] = gov.preserve_source(bundle['source']['id'], '바뀐 원문', origin='user')
        before = deepcopy((i, r))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('original version changed') + "$"):
            gov.current_import(i, r, identifier, owner_handlers=handlers, clock=sim.clock)
        self.assertEqual((i, r), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_receipt_seal(self):
        sim = checked_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        bundle = r['intent_imports'][checked_bundle(sim)['id']]
        identifier = bundle['id']
        handlers = sim.engine.governance_owner_handlers()
        bundle['application'] = {'status': 'applied', 'sha256': '0' * 64}
        before = deepcopy((i, r))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('sealed import application receipt changed') + "$"):
            gov.current_import(i, r, identifier, owner_handlers=handlers, clock=sim.clock)
        self.assertEqual((i, r), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_apply_not_approved(self):
        sim = checked_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        bundle = r['intent_imports'][checked_bundle(sim)['id']]
        identifier = bundle['id']
        handlers = sim.engine.governance_owner_handlers()
        bundle['status'] = 'unresolved'
        before = deepcopy((i, r))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('independent complete approval required') + "$"):
            gov.apply_import(i, r, identifier, owner_handlers=handlers, clock=sim.clock)
        self.assertEqual((i, r), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_check_seal(self):
        sim = checked_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        bundle = r['intent_imports'][checked_bundle(sim)['id']]
        identifier = bundle['id']
        handlers = sim.engine.governance_owner_handlers()
        bundle['check']['sha256'] = '0' * 64
        before = deepcopy((i, r))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('sealed check changed') + "$"):
            gov.apply_import(i, r, identifier, owner_handlers=handlers, clock=sim.clock)
        self.assertEqual((i, r), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_checker_evidence(self):
        sim = checked_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        bundle = r['intent_imports'][checked_bundle(sim)['id']]
        identifier = bundle['id']
        handlers = sim.engine.governance_owner_handlers()
        r['executions'][bundle['check']['execution_id']]['intent_import_sha256'] = '0' * 64
        before = deepcopy((i, r))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('checker execution must bind exact preserved import input') + "$"):
            gov.apply_import(i, r, identifier, owner_handlers=handlers, clock=sim.clock)
        self.assertEqual((i, r), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_missing_exact_approval(self):
        sim = checked_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        bundle = r['intent_imports'][checked_bundle(sim)['id']]
        identifier = bundle['id']
        handlers = sim.engine.governance_owner_handlers()
        pass
        before = deepcopy((i, r))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('semantic check is not user approval of the exact change') + "$"):
            gov.apply_import(i, r, identifier, owner_handlers=handlers, clock=sim.clock)
        self.assertEqual((i, r), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_control_origin(self):
        sim = checked_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        bundle = r['intent_imports'][checked_bundle(sim)['id']]
        identifier = bundle['id']
        handlers = sim.engine.governance_owner_handlers()
        request = {'id': 'DC-close-approval', 'action': 'decision', 'origin': 'user', 'text': '정확한 변경 승인',
                   'config': gov.import_approval_draft(i, r, identifier, owner_handlers=handlers, clock=sim.clock)}
        request['origin'] = 'operator'
        before = deepcopy((i, r, request))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('import approval requires an explicit user decision control') + "$"):
            gov.apply_import_control(i, r, request, owner_handlers=handlers, clock=sim.clock)
        self.assertEqual((i, r, request), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_control_import(self):
        sim = checked_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        bundle = r['intent_imports'][checked_bundle(sim)['id']]
        identifier = bundle['id']
        handlers = sim.engine.governance_owner_handlers()
        request = {'id': 'DC-close-approval', 'action': 'decision', 'origin': 'user', 'text': '정확한 변경 승인',
                   'config': gov.import_approval_draft(i, r, identifier, owner_handlers=handlers, clock=sim.clock)}
        request['config']['import_id'] = 'missing'
        before = deepcopy((i, r, request))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('import is absent') + "$"):
            gov.apply_import_control(i, r, request, owner_handlers=handlers, clock=sim.clock)
        self.assertEqual((i, r, request), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_control_bundle(self):
        sim = checked_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        bundle = r['intent_imports'][checked_bundle(sim)['id']]
        identifier = bundle['id']
        handlers = sim.engine.governance_owner_handlers()
        request = {'id': 'DC-close-approval', 'action': 'decision', 'origin': 'user', 'text': '정확한 변경 승인',
                   'config': gov.import_approval_draft(i, r, identifier, owner_handlers=handlers, clock=sim.clock)}
        request['config']['bundle_sha256'] = '0' * 64
        before = deepcopy((i, r, request))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('approval does not name the exact sealed interpretation and check') + "$"):
            gov.apply_import_control(i, r, request, owner_handlers=handlers, clock=sim.clock)
        self.assertEqual((i, r, request), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_control_units(self):
        sim = checked_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        bundle = r['intent_imports'][checked_bundle(sim)['id']]
        identifier = bundle['id']
        handlers = sim.engine.governance_owner_handlers()
        request = {'id': 'DC-close-approval', 'action': 'decision', 'origin': 'user', 'text': '정확한 변경 승인',
                   'config': gov.import_approval_draft(i, r, identifier, owner_handlers=handlers, clock=sim.clock)}
        request['config']['unit_hashes'] = {}
        before = deepcopy((i, r, request))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('approval must bind every exact proposed change') + "$"):
            gov.apply_import_control(i, r, request, owner_handlers=handlers, clock=sim.clock)
        self.assertEqual((i, r, request), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_control_source(self):
        sim = checked_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        bundle = r['intent_imports'][checked_bundle(sim)['id']]
        identifier = bundle['id']
        handlers = sim.engine.governance_owner_handlers()
        request = {'id': 'DC-close-approval', 'action': 'decision', 'origin': 'user', 'text': '정확한 변경 승인',
                   'config': gov.import_approval_draft(i, r, identifier, owner_handlers=handlers, clock=sim.clock)}
        i['governance_sources'][request['id']] = gov.preserve_source(request['id'], '다른 승인', origin='user')
        before = deepcopy((i, r, request))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('approval source identity reused') + "$"):
            gov.apply_import_control(i, r, request, owner_handlers=handlers, clock=sim.clock)
        self.assertEqual((i, r, request), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_draft_status(self):
        sim = checked_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        bundle = r['intent_imports'][checked_bundle(sim)['id']]
        identifier = bundle['id']
        handlers = sim.engine.governance_owner_handlers()
        bundle['status'] = 'unresolved'
        before = deepcopy((i, r))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('approval draft requires a complete independently checked import') + "$"):
            gov.import_approval_draft(i, r, identifier, owner_handlers=handlers, clock=sim.clock)
        self.assertEqual((i, r), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_draft_scope(self):
        sim = checked_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        bundle = r['intent_imports'][checked_bundle(sim)['id']]
        identifier = bundle['id']
        handlers = sim.engine.governance_owner_handlers()
        bundle['check']['scope_complete'] = False
        bundle['status'] = 'unresolved'
        bundle['check']['sha256'] = exact_content_hash({k: v for k, v in bundle['check'].items() if k != 'sha256'})
        before = deepcopy((i, r))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('approval draft requires a complete independently checked import') + "$"):
            gov.import_approval_draft(i, r, identifier, owner_handlers=handlers, clock=sim.clock)
        self.assertEqual((i, r), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_draft_decision(self):
        sim = checked_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        bundle = r['intent_imports'][checked_bundle(sim)['id']]
        identifier = bundle['id']
        handlers = sim.engine.governance_owner_handlers()
        bundle['check']['decision'] = 'unresolved'
        bundle['status'] = 'unresolved'
        bundle['check']['sha256'] = exact_content_hash({k: v for k, v in bundle['check'].items() if k != 'sha256'})
        before = deepcopy((i, r))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('approval draft requires a complete independently checked import') + "$"):
            gov.import_approval_draft(i, r, identifier, owner_handlers=handlers, clock=sim.clock)
        self.assertEqual((i, r), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_draft_seal(self):
        sim = checked_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        bundle = r['intent_imports'][checked_bundle(sim)['id']]
        identifier = bundle['id']
        handlers = sim.engine.governance_owner_handlers()
        bundle['check']['sha256'] = '0' * 64
        before = deepcopy((i, r))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('sealed check changed') + "$"):
            gov.import_approval_draft(i, r, identifier, owner_handlers=handlers, clock=sim.clock)
        self.assertEqual((i, r), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)
