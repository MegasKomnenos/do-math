"""실제 해석 생산자의 원문·질문·봉인 계약을 한 필드씩 검증한다."""
from copy import deepcopy
import re
import unittest

from do_math import governance as gov
from support.governance_sim import checked_sim, checked_bundle

class GovernanceCheckerLineageTests(unittest.TestCase):
    def test_checker_absent(self):
        sim = checked_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        bundle = r['intent_imports'][checked_bundle(sim)['id']]
        identifier = bundle['id']
        handlers = sim.engine.governance_owner_handlers()
        author = bundle['execution_id']
        checker = bundle['check']['execution_id']
        checker = 'missing'
        before = deepcopy((i, r))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('independent checker execution required') + "$"):
            gov.validate_independent_execution(r, checker, [author])
        self.assertEqual((i, r), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_checker_is_author(self):
        sim = checked_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        bundle = r['intent_imports'][checked_bundle(sim)['id']]
        identifier = bundle['id']
        handlers = sim.engine.governance_owner_handlers()
        author = bundle['execution_id']
        checker = bundle['check']['execution_id']
        checker = author
        before = deepcopy((i, r))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('independent checker execution required') + "$"):
            gov.validate_independent_execution(r, checker, [author])
        self.assertEqual((i, r), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_checker_resumes_author(self):
        sim = checked_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        bundle = r['intent_imports'][checked_bundle(sim)['id']]
        identifier = bundle['id']
        handlers = sim.engine.governance_owner_handlers()
        author = bundle['execution_id']
        checker = bundle['check']['execution_id']
        r['executions'][checker]['continuation_of'] = author
        before = deepcopy((i, r))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('checker resumes an author lineage') + "$"):
            gov.validate_independent_execution(r, checker, [author])
        self.assertEqual((i, r), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_checker_missing_predecessor(self):
        sim = checked_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        bundle = r['intent_imports'][checked_bundle(sim)['id']]
        identifier = bundle['id']
        handlers = sim.engine.governance_owner_handlers()
        author = bundle['execution_id']
        checker = bundle['check']['execution_id']
        r['executions'][checker]['continuation_of'] = 'missing'
        before = deepcopy((i, r))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('checker continuation lineage does not resolve') + "$"):
            gov.validate_independent_execution(r, checker, [author])
        self.assertEqual((i, r), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_checker_cycle(self):
        sim = checked_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        bundle = r['intent_imports'][checked_bundle(sim)['id']]
        identifier = bundle['id']
        handlers = sim.engine.governance_owner_handlers()
        author = bundle['execution_id']
        checker = bundle['check']['execution_id']
        r['executions'][checker]['continuation_of'] = checker
        before = deepcopy((i, r))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('checker resumes an author lineage') + "$"):
            gov.validate_independent_execution(r, checker, [author])
        self.assertEqual((i, r), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)
