"""실제 해석 생산자의 원문·질문·봉인 계약을 한 필드씩 검증한다."""
from copy import deepcopy
import re
import unittest

from do_math import governance as gov
from support.governance_sim import checked_sim, checked_bundle

class GovernanceSemanticCheckRejectionTests(unittest.TestCase):
    def test_a_sealed_check_cannot_be_replaced_in_place(self):
        sim = checked_sim()
        bundle = checked_bundle(sim)
        output = {key: deepcopy(value) for key, value in bundle['check'].items()
                  if key not in {'sha256', 'execution_id'}}
        before = deepcopy((sim.instance, sim.runtime, output))
        with self.assertRaises(ValueError) as caught:
            gov.check_import(sim.instance, sim.runtime, bundle['id'], output,
                execution_id=bundle['check']['execution_id'],
                owner_handlers=sim.engine.governance_owner_handlers(), clock=sim.clock)
        self.assertEqual(str(caught.exception), 'check is sealed; reauthor instead')
        self.assertEqual((sim.instance, sim.runtime, output), before)

    def test_checker_role(self):
        sim = checked_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        bundle = r['intent_imports'][checked_bundle(sim)['id']]
        identifier = bundle['id']
        handlers = sim.engine.governance_owner_handlers()
        check_output = {k: deepcopy(v) for k, v in bundle['check'].items() if k not in {'sha256', 'execution_id'}}
        checker = bundle['check']['execution_id']
        del bundle['check']
        r['executions'][checker]['role'] = 'maintenance'
        before = deepcopy((i, r, check_output))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('checker execution must bind exact preserved import input') + "$"):
            gov.check_import(i, r, identifier, check_output, execution_id=checker, owner_handlers=handlers, clock=sim.clock)
        self.assertEqual((i, r, check_output), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_checker_hash(self):
        sim = checked_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        bundle = r['intent_imports'][checked_bundle(sim)['id']]
        identifier = bundle['id']
        handlers = sim.engine.governance_owner_handlers()
        check_output = {k: deepcopy(v) for k, v in bundle['check'].items() if k not in {'sha256', 'execution_id'}}
        checker = bundle['check']['execution_id']
        del bundle['check']
        r['executions'][checker]['intent_import_sha256'] = '0' * 64
        before = deepcopy((i, r, check_output))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('checker execution must bind exact preserved import input') + "$"):
            gov.check_import(i, r, identifier, check_output, execution_id=checker, owner_handlers=handlers, clock=sim.clock)
        self.assertEqual((i, r, check_output), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_check_read_hash(self):
        sim = checked_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        bundle = r['intent_imports'][checked_bundle(sim)['id']]
        identifier = bundle['id']
        handlers = sim.engine.governance_owner_handlers()
        check_output = {k: deepcopy(v) for k, v in bundle['check'].items() if k not in {'sha256', 'execution_id'}}
        checker = bundle['check']['execution_id']
        del bundle['check']
        check_output['bundle_sha256'] = '0' * 64
        before = deepcopy((i, r, check_output))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('check read a different import') + "$"):
            gov.check_import(i, r, identifier, check_output, execution_id=checker, owner_handlers=handlers, clock=sim.clock)
        self.assertEqual((i, r, check_output), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_semantic_verdict(self):
        sim = checked_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        bundle = r['intent_imports'][checked_bundle(sim)['id']]
        identifier = bundle['id']
        handlers = sim.engine.governance_owner_handlers()
        check_output = {k: deepcopy(v) for k, v in bundle['check'].items() if k not in {'sha256', 'execution_id'}}
        checker = bundle['check']['execution_id']
        del bundle['check']
        check_output['decision'] = 'maybe'
        before = deepcopy((i, r, check_output))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('invalid semantic verdict') + "$"):
            gov.check_import(i, r, identifier, check_output, execution_id=checker, owner_handlers=handlers, clock=sim.clock)
        self.assertEqual((i, r, check_output), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_scope_boolean(self):
        sim = checked_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        bundle = r['intent_imports'][checked_bundle(sim)['id']]
        identifier = bundle['id']
        handlers = sim.engine.governance_owner_handlers()
        check_output = {k: deepcopy(v) for k, v in bundle['check'].items() if k not in {'sha256', 'execution_id'}}
        checker = bundle['check']['execution_id']
        del bundle['check']
        check_output['scope_complete'] = 'yes'
        before = deepcopy((i, r, check_output))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('scope completeness required') + "$"):
            gov.check_import(i, r, identifier, check_output, execution_id=checker, owner_handlers=handlers, clock=sim.clock)
        self.assertEqual((i, r, check_output), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_missing_unit_coverage(self):
        sim = checked_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        bundle = r['intent_imports'][checked_bundle(sim)['id']]
        identifier = bundle['id']
        handlers = sim.engine.governance_owner_handlers()
        check_output = {k: deepcopy(v) for k, v in bundle['check'].items() if k not in {'sha256', 'execution_id'}}
        checker = bundle['check']['execution_id']
        del bundle['check']
        check_output['unit_ids'] = []
        before = deepcopy((i, r, check_output))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('check must cover all meaning units and questions') + "$"):
            gov.check_import(i, r, identifier, check_output, execution_id=checker, owner_handlers=handlers, clock=sim.clock)
        self.assertEqual((i, r, check_output), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_repair_findings(self):
        sim = checked_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        bundle = r['intent_imports'][checked_bundle(sim)['id']]
        identifier = bundle['id']
        handlers = sim.engine.governance_owner_handlers()
        check_output = {k: deepcopy(v) for k, v in bundle['check'].items() if k not in {'sha256', 'execution_id'}}
        checker = bundle['check']['execution_id']
        del bundle['check']
        check_output['decision'] = 'revision_required'
        before = deepcopy((i, r, check_output))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('failed check needs repair findings') + "$"):
            gov.check_import(i, r, identifier, check_output, execution_id=checker, owner_handlers=handlers, clock=sim.clock)
        self.assertEqual((i, r, check_output), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)
