"""감사 입력과 엔진 판정의 거부는 저장된 생산 상태에서 검증한다."""
from copy import deepcopy
import re
import unittest

from do_math import governance as gov
from support.governance_cases import auditor_sim, audit_output

class GovernanceAuditRejectionTests(unittest.TestCase):
    def test_empty_required(self):
        sim = auditor_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        e = sim.engine
        action = deepcopy(sim.runtime['executions']['EX-close-auditor']['action'])
        output = audit_output(sim)
        action['required'] = 0
        before = deepcopy((sim.instance, sim.runtime))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('goal audit requires a positive count and an in-range integer slot') + "$"):
            e._apply_governance_goal_audit(action, output, 'EX-close-auditor')
        self.assertEqual((sim.instance, sim.runtime), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_boolean_required(self):
        sim = auditor_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        e = sim.engine
        action = deepcopy(sim.runtime['executions']['EX-close-auditor']['action'])
        output = audit_output(sim)
        action['required'] = True
        before = deepcopy((sim.instance, sim.runtime))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('goal audit requires a positive count and an in-range integer slot') + "$"):
            e._apply_governance_goal_audit(action, output, 'EX-close-auditor')
        self.assertEqual((sim.instance, sim.runtime), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_negative_slot(self):
        sim = auditor_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        e = sim.engine
        action = deepcopy(sim.runtime['executions']['EX-close-auditor']['action'])
        output = audit_output(sim)
        action['slot'] = -1
        before = deepcopy((sim.instance, sim.runtime))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('goal audit requires a positive count and an in-range integer slot') + "$"):
            e._apply_governance_goal_audit(action, output, 'EX-close-auditor')
        self.assertEqual((sim.instance, sim.runtime), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_boolean_slot(self):
        sim = auditor_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        e = sim.engine
        action = deepcopy(sim.runtime['executions']['EX-close-auditor']['action'])
        output = audit_output(sim)
        action['slot'] = True
        before = deepcopy((sim.instance, sim.runtime))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('goal audit requires a positive count and an in-range integer slot') + "$"):
            e._apply_governance_goal_audit(action, output, 'EX-close-auditor')
        self.assertEqual((sim.instance, sim.runtime), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_stale_goal_basis(self):
        sim = auditor_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        e = sim.engine
        action = deepcopy(sim.runtime['executions']['EX-close-auditor']['action'])
        output = audit_output(sim)
        action['basis'] = '0' * 64
        before = deepcopy((sim.instance, sim.runtime))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('goal audit inputs changed before acceptance') + "$"):
            e._apply_governance_goal_audit(action, output, 'EX-close-auditor')
        self.assertEqual((sim.instance, sim.runtime), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_delivered_audit(self):
        sim = auditor_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        e = sim.engine
        action = deepcopy(sim.runtime['executions']['EX-close-auditor']['action'])
        output = audit_output(sim)
        sim.runtime['executions']['EX-close-auditor']['additional_audit_input'] = []
        before = deepcopy((sim.instance, sim.runtime))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('goal auditor did not receive these current additional-audit inputs') + "$"):
            gov.evaluate_goal_audits(sim.instance, sim.runtime, 'EX-close-auditor', output['additional_audits'])
        self.assertEqual((sim.instance, sim.runtime), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_missing_audit_result(self):
        sim = auditor_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        e = sim.engine
        action = deepcopy(sim.runtime['executions']['EX-close-auditor']['action'])
        output = audit_output(sim)
        output['additional_audits'] = []
        before = deepcopy((sim.instance, sim.runtime))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('all additional audits require actual verdicts') + "$"):
            gov.evaluate_goal_audits(sim.instance, sim.runtime, 'EX-close-auditor', output['additional_audits'])
        self.assertEqual((sim.instance, sim.runtime), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_wrong_audit_identity(self):
        sim = auditor_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        e = sim.engine
        action = deepcopy(sim.runtime['executions']['EX-close-auditor']['action'])
        output = audit_output(sim)
        output['additional_audits'][0]['audit_ref'] = 'missing'
        before = deepcopy((sim.instance, sim.runtime))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('additional audit result identity differs') + "$"):
            gov.evaluate_goal_audits(sim.instance, sim.runtime, 'EX-close-auditor', output['additional_audits'])
        self.assertEqual((sim.instance, sim.runtime), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_nonobject_audit_result(self):
        sim = auditor_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        e = sim.engine
        action = deepcopy(sim.runtime['executions']['EX-close-auditor']['action'])
        output = audit_output(sim)
        output['additional_audits'][0] = 'pass'
        before = deepcopy((sim.instance, sim.runtime))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('additional audit result identity differs') + "$"):
            gov.evaluate_goal_audits(sim.instance, sim.runtime, 'EX-close-auditor', output['additional_audits'])
        self.assertEqual((sim.instance, sim.runtime), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_bind_wrong_input(self):
        sim = auditor_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        e = sim.engine
        action = deepcopy(sim.runtime['executions']['EX-close-auditor']['action'])
        output = audit_output(sim)
        context = e._governance_context(action, {})
        context['additional_audit_input'] = []
        before = deepcopy((sim.instance, sim.runtime))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('delivered additional audit input changed') + "$"):
            e._bind_governance_input(action, sim.runtime['executions']['EX-close-auditor'], context)
        self.assertEqual((sim.instance, sim.runtime), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_request_wrong_basis(self):
        sim = auditor_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        e = sim.engine
        action = deepcopy(sim.runtime['executions']['EX-close-auditor']['action'])
        output = audit_output(sim)
        pass
        before = deepcopy((sim.instance, sim.runtime))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('goal audit request basis changed') + "$"):
            e._ensure_goal_audit_requests('0' * 64, 'EX-close-auditor')
        self.assertEqual((sim.instance, sim.runtime), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)
