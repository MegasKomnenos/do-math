"""정상 생산 상태의 한 필드 변조와 거부의 원자성. 실행 결과는 별도 측정한다."""
from copy import deepcopy
import re
import unittest

from do_math import delegations
from support.governance_cases import delegated_sim

class GovernanceDelegationRejectionTests(unittest.TestCase):
    def test_original_content_is_bound_when_delegation_is_approved(self):
        from support.governance_delegation import replacement_case
        from support.entry import entry
        i, r, _, case = replacement_case()
        i['decisions']['ORIGINAL']['effect']['slot'] = 'another-seat'
        before = deepcopy((i, r))
        with self.assertRaisesRegex(ValueError, '^original decision differs from delegated approval$'):
            delegations.prepare_application(i, r, 'DG', case, now_iso=entry().ports.clock.now())
        self.assertEqual((i, r), before)

    def test_inactive(self):
        sim = delegated_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        app = next(row for row in r['delegation_applications'].values() if row['delegation_id'] == 'DG-close')
        case = deepcopy(app['basis']['case'])
        d = deepcopy(i['delegations']['DG-close'])
        d['status'] = 'revoked'
        before = deepcopy((i, r, case, d))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('delegation inactive') + "$"):
            delegations.validate_delegation(d, now_iso=sim.clock.now())
        self.assertEqual((i, r, case, d), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_forbidden_kind(self):
        sim = delegated_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        app = next(row for row in r['delegation_applications'].values() if row['delegation_id'] == 'DG-close')
        case = deepcopy(app['basis']['case'])
        d = deepcopy(i['delegations']['DG-close'])
        d['decision_kind'] = 'proposal_adoption'
        before = deepcopy((i, r, case, d))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('this decision requires a new explicit user decision') + "$"):
            delegations.validate_delegation(d, now_iso=sim.clock.now())
        self.assertEqual((i, r, case, d), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_empty_scope(self):
        sim = delegated_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        app = next(row for row in r['delegation_applications'].values() if row['delegation_id'] == 'DG-close')
        case = deepcopy(app['basis']['case'])
        d = deepcopy(i['delegations']['DG-close'])
        d['included_targets'] = []
        before = deepcopy((i, r, case, d))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('delegation needs explicit included scope') + "$"):
            delegations.validate_delegation(d, now_iso=sim.clock.now())
        self.assertEqual((i, r, case, d), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_limits_object(self):
        sim = delegated_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        app = next(row for row in r['delegation_applications'].values() if row['delegation_id'] == 'DG-close')
        case = deepcopy(app['basis']['case'])
        d = deepcopy(i['delegations']['DG-close'])
        d['resource_limits'] = []
        before = deepcopy((i, r, case, d))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('resource limits must be mapped') + "$"):
            delegations.validate_delegation(d, now_iso=sim.clock.now())
        self.assertEqual((i, r, case, d), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_negative_limit(self):
        sim = delegated_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        app = next(row for row in r['delegation_applications'].values() if row['delegation_id'] == 'DG-close')
        case = deepcopy(app['basis']['case'])
        d = deepcopy(i['delegations']['DG-close'])
        d['resource_limits']['steps'] = -1
        before = deepcopy((i, r, case, d))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('invalid delegation resource limit') + "$"):
            delegations.validate_delegation(d, now_iso=sim.clock.now())
        self.assertEqual((i, r, case, d), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_boolean_limit(self):
        sim = delegated_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        app = next(row for row in r['delegation_applications'].values() if row['delegation_id'] == 'DG-close')
        case = deepcopy(app['basis']['case'])
        d = deepcopy(i['delegations']['DG-close'])
        d['resource_limits']['steps'] = True
        before = deepcopy((i, r, case, d))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('invalid delegation resource limit') + "$"):
            delegations.validate_delegation(d, now_iso=sim.clock.now())
        self.assertEqual((i, r, case, d), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_expired(self):
        sim = delegated_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        app = next(row for row in r['delegation_applications'].values() if row['delegation_id'] == 'DG-close')
        case = deepcopy(app['basis']['case'])
        d = deepcopy(i['delegations']['DG-close'])
        d['expires_at'] = sim.clock.now()
        before = deepcopy((i, r, case, d))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('delegation expired') + "$"):
            delegations.validate_delegation(d, now_iso=sim.clock.now())
        self.assertEqual((i, r, case, d), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_missing_id(self):
        sim = delegated_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        app = next(row for row in r['delegation_applications'].values() if row['delegation_id'] == 'DG-close')
        case = deepcopy(app['basis']['case'])
        d = deepcopy(i['delegations']['DG-close'])
        d['id'] = ''
        before = deepcopy((i, r, case, d))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('missing delegation id') + "$"):
            delegations.validate_delegation(d, now_iso=sim.clock.now())
        self.assertEqual((i, r, case, d), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_missing_decision_kind(self):
        sim = delegated_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        app = next(row for row in r['delegation_applications'].values() if row['delegation_id'] == 'DG-close')
        case = deepcopy(app['basis']['case'])
        d = deepcopy(i['delegations']['DG-close'])
        d['decision_kind'] = ''
        before = deepcopy((i, r, case, d))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('missing delegation decision_kind') + "$"):
            delegations.validate_delegation(d, now_iso=sim.clock.now())
        self.assertEqual((i, r, case, d), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_missing_original_decision_id(self):
        sim = delegated_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        app = next(row for row in r['delegation_applications'].values() if row['delegation_id'] == 'DG-close')
        case = deepcopy(app['basis']['case'])
        d = deepcopy(i['delegations']['DG-close'])
        d['original_decision_id'] = ''
        before = deepcopy((i, r, case, d))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('missing delegation original_decision_id') + "$"):
            delegations.validate_delegation(d, now_iso=sim.clock.now())
        self.assertEqual((i, r, case, d), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_missing_source_ref(self):
        sim = delegated_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        app = next(row for row in r['delegation_applications'].values() if row['delegation_id'] == 'DG-close')
        case = deepcopy(app['basis']['case'])
        d = deepcopy(i['delegations']['DG-close'])
        d['source_ref'] = ''
        before = deepcopy((i, r, case, d))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('missing delegation source_ref') + "$"):
            delegations.validate_delegation(d, now_iso=sim.clock.now())
        self.assertEqual((i, r, case, d), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_missing_decision_id(self):
        sim = delegated_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        app = next(row for row in r['delegation_applications'].values() if row['delegation_id'] == 'DG-close')
        case = deepcopy(app['basis']['case'])
        d = deepcopy(i['delegations']['DG-close'])
        d['decision_id'] = ''
        before = deepcopy((i, r, case, d))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('missing delegation decision_id') + "$"):
            delegations.validate_delegation(d, now_iso=sim.clock.now())
        self.assertEqual((i, r, case, d), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_duplicate_included_targets(self):
        sim = delegated_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        app = next(row for row in r['delegation_applications'].values() if row['delegation_id'] == 'DG-close')
        case = deepcopy(app['basis']['case'])
        d = deepcopy(i['delegations']['DG-close'])
        d['included_targets'] = ['same', 'same']
        before = deepcopy((i, r, case, d))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('invalid delegation included_targets') + "$"):
            delegations.validate_delegation(d, now_iso=sim.clock.now())
        self.assertEqual((i, r, case, d), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_duplicate_excluded_targets(self):
        sim = delegated_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        app = next(row for row in r['delegation_applications'].values() if row['delegation_id'] == 'DG-close')
        case = deepcopy(app['basis']['case'])
        d = deepcopy(i['delegations']['DG-close'])
        d['excluded_targets'] = ['same', 'same']
        before = deepcopy((i, r, case, d))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('invalid delegation excluded_targets') + "$"):
            delegations.validate_delegation(d, now_iso=sim.clock.now())
        self.assertEqual((i, r, case, d), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_duplicate_external_effects(self):
        sim = delegated_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        app = next(row for row in r['delegation_applications'].values() if row['delegation_id'] == 'DG-close')
        case = deepcopy(app['basis']['case'])
        d = deepcopy(i['delegations']['DG-close'])
        d['external_effects'] = ['same', 'same']
        before = deepcopy((i, r, case, d))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('invalid delegation external_effects') + "$"):
            delegations.validate_delegation(d, now_iso=sim.clock.now())
        self.assertEqual((i, r, case, d), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_refs_object(self):
        sim = delegated_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        app = next(row for row in r['delegation_applications'].values() if row['delegation_id'] == 'DG-close')
        case = deepcopy(app['basis']['case'])
        case['basis_refs'] = {}
        before = deepcopy((i, r, case))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('case basis refs must be a list') + "$"):
            delegations.case_basis_reference_ids(case)
        self.assertEqual((i, r, case), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_refs_extra_key(self):
        sim = delegated_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        app = next(row for row in r['delegation_applications'].values() if row['delegation_id'] == 'DG-close')
        case = deepcopy(app['basis']['case'])
        case['basis_refs'] = [{'id': 'x', 'extra': 1}]
        before = deepcopy((i, r, case))
        with self.assertRaisesRegex(ValueError, "^" + re.escape("case basis reference must be a record ID or an exact {'id': ID} object") + "$"):
            delegations.case_basis_reference_ids(case)
        self.assertEqual((i, r, case), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_refs_empty_id(self):
        sim = delegated_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        app = next(row for row in r['delegation_applications'].values() if row['delegation_id'] == 'DG-close')
        case = deepcopy(app['basis']['case'])
        case['basis_refs'] = ['']
        before = deepcopy((i, r, case))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('case basis refs must name distinct record IDs') + "$"):
            delegations.case_basis_reference_ids(case)
        self.assertEqual((i, r, case), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_refs_duplicate(self):
        sim = delegated_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        app = next(row for row in r['delegation_applications'].values() if row['delegation_id'] == 'DG-close')
        case = deepcopy(app['basis']['case'])
        case['basis_refs'] *= 2
        before = deepcopy((i, r, case))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('case basis refs must name distinct record IDs') + "$"):
            delegations.case_basis_reference_ids(case)
        self.assertEqual((i, r, case), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_original_actor(self):
        sim = delegated_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        app = next(row for row in r['delegation_applications'].values() if row['delegation_id'] == 'DG-close')
        case = deepcopy(app['basis']['case'])
        i['decisions']['DC-close-original']['actor'] = 'ai'
        before = deepcopy((i, r, case))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('original decision is absent or incompatible') + "$"):
            delegations.prepare_application(i, r, 'DG-close', case, now_iso=sim.clock.now())
        self.assertEqual((i, r, case), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_approval_actor(self):
        sim = delegated_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        app = next(row for row in r['delegation_applications'].values() if row['delegation_id'] == 'DG-close')
        case = deepcopy(app['basis']['case'])
        i['decisions']['DC-close-delegation']['actor'] = 'ai'
        before = deepcopy((i, r, case))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('delegation has no current user approval') + "$"):
            delegations.prepare_application(i, r, 'DG-close', case, now_iso=sim.clock.now())
        self.assertEqual((i, r, case), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_approval_scope(self):
        sim = delegated_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        app = next(row for row in r['delegation_applications'].values() if row['delegation_id'] == 'DG-close')
        case = deepcopy(app['basis']['case'])
        i['decisions']['DC-close-delegation']['change']['delegation']['resource_limits']['steps'] = 3
        before = deepcopy((i, r, case))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('approval does not bind the exact delegated scope') + "$"):
            delegations.prepare_application(i, r, 'DG-close', case, now_iso=sim.clock.now())
        self.assertEqual((i, r, case), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_outside_target(self):
        sim = delegated_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        app = next(row for row in r['delegation_applications'].values() if row['delegation_id'] == 'DG-close')
        case = deepcopy(app['basis']['case'])
        case['target_id'] = 'missing'
        before = deepcopy((i, r, case))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('case outside delegation scope') + "$"):
            delegations.prepare_application(i, r, 'DG-close', case, now_iso=sim.clock.now())
        self.assertEqual((i, r, case), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_external_effect(self):
        sim = delegated_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        app = next(row for row in r['delegation_applications'].values() if row['delegation_id'] == 'DG-close')
        case = deepcopy(app['basis']['case'])
        case['external_effects'] = ['network']
        before = deepcopy((i, r, case))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('external effect outside delegation') + "$"):
            delegations.prepare_application(i, r, 'DG-close', case, now_iso=sim.clock.now())
        self.assertEqual((i, r, case), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_resource_limit(self):
        sim = delegated_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        app = next(row for row in r['delegation_applications'].values() if row['delegation_id'] == 'DG-close')
        case = deepcopy(app['basis']['case'])
        case['resources']['steps'] = 3
        before = deepcopy((i, r, case))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('resource request outside delegation') + "$"):
            delegations.prepare_application(i, r, 'DG-close', case, now_iso=sim.clock.now())
        self.assertEqual((i, r, case), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_resource_boolean(self):
        sim = delegated_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        app = next(row for row in r['delegation_applications'].values() if row['delegation_id'] == 'DG-close')
        case = deepcopy(app['basis']['case'])
        case['resources']['steps'] = True
        before = deepcopy((i, r, case))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('resource request outside delegation') + "$"):
            delegations.prepare_application(i, r, 'DG-close', case, now_iso=sim.clock.now())
        self.assertEqual((i, r, case), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_effect_object(self):
        sim = delegated_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        app = next(row for row in r['delegation_applications'].values() if row['delegation_id'] == 'DG-close')
        case = deepcopy(app['basis']['case'])
        case['effect'] = []
        before = deepcopy((i, r, case))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('case must preserve exact proposed effect') + "$"):
            delegations.prepare_application(i, r, 'DG-close', case, now_iso=sim.clock.now())
        self.assertEqual((i, r, case), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_basis_missing(self):
        sim = delegated_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        app = next(row for row in r['delegation_applications'].values() if row['delegation_id'] == 'DG-close')
        case = deepcopy(app['basis']['case'])
        case['basis_refs'] = ['missing']
        before = deepcopy((i, r, case))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('case basis reference does not resolve') + "$"):
            delegations.prepare_application(i, r, 'DG-close', case, now_iso=sim.clock.now())
        self.assertEqual((i, r, case), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_judgment_input(self):
        sim = delegated_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        app = next(row for row in r['delegation_applications'].values() if row['delegation_id'] == 'DG-close')
        case = deepcopy(app['basis']['case'])
        r['executions']['EX-close-check']['delegation_input_sha256'] = '0' * 64
        before = deepcopy((i, r, case))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('judgment execution must bind blind shared input') + "$"):
            delegations._checked(i, r, app['id'], sim.clock.now())
        self.assertEqual((i, r, case), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_judgment_output(self):
        sim = delegated_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        for changes in ({'decision': None}, {'decision': 'matching'}, {'reason': None},
                        {'reason': []}, {'reason': ''}, {'reason': ' \t\n'}):
            with self.subTest(changes=changes):
                instance, runtime = deepcopy(stored)
                application = next(row for row in runtime['delegation_applications'].values()
                                   if row['delegation_id'] == 'DG-close')
                judgment = application['judgments'].pop('check')
                output = {**judgment['output'], **changes}
                before = deepcopy((instance, runtime, output))
                with self.assertRaisesRegex(ValueError, '^judgment needs current input, verdict, reasons$'):
                    delegations.record_judgment(runtime, application['id'], output,
                        execution_id=judgment['execution_id'], stage='check')
                self.assertEqual((instance, runtime, output), before)
                self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)
        i, r = deepcopy(stored)
        app = next(row for row in r['delegation_applications'].values() if row['delegation_id'] == 'DG-close')
        case = deepcopy(app['basis']['case'])
        app['judgments']['check']['output']['input_sha256'] = '0' * 64
        before = deepcopy((i, r, case))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('judgment needs current input, verdict, reasons') + "$"):
            delegations._checked(i, r, app['id'], sim.clock.now())
        self.assertEqual((i, r, case), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_judgment_seal(self):
        sim = delegated_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        app = next(row for row in r['delegation_applications'].values() if row['delegation_id'] == 'DG-close')
        case = deepcopy(app['basis']['case'])
        app['judgments']['check']['sha256'] = '0' * 64
        before = deepcopy((i, r, case))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('delegation verdict is not current matching judgment') + "$"):
            delegations._checked(i, r, app['id'], sim.clock.now())
        self.assertEqual((i, r, case), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_missing_judgment(self):
        sim = delegated_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        app = next(row for row in r['delegation_applications'].values() if row['delegation_id'] == 'DG-close')
        case = deepcopy(app['basis']['case'])
        del app['judgments']['check']
        before = deepcopy((i, r, case))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('two independent judgments required') + "$"):
            delegations._checked(i, r, app['id'], sim.clock.now())
        self.assertEqual((i, r, case), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_stale_basis(self):
        sim = delegated_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        app = next(row for row in r['delegation_applications'].values() if row['delegation_id'] == 'DG-close')
        case = deepcopy(app['basis']['case'])
        app['basis']['case']['resources']['steps'] = 2
        before = deepcopy((i, r, case))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('delegation application stale') + "$"):
            delegations._checked(i, r, app['id'], sim.clock.now())
        self.assertEqual((i, r, case), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_repeated_stage(self):
        sim = delegated_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        app = next(row for row in r['delegation_applications'].values() if row['delegation_id'] == 'DG-close')
        case = deepcopy(app['basis']['case'])
        stage = 'interpret'
        before = deepcopy((i, r, case))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('invalid or sealed judgment stage') + "$"):
            delegations.record_judgment(r, app['id'], app['judgments']['interpret']['output'], execution_id='EX-close-interpret', stage=stage)
        self.assertEqual((i, r, case), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_unknown_stage(self):
        sim = delegated_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        app = next(row for row in r['delegation_applications'].values() if row['delegation_id'] == 'DG-close')
        case = deepcopy(app['basis']['case'])
        stage = 'other'
        before = deepcopy((i, r, case))
        with self.assertRaisesRegex(ValueError, "^" + re.escape('invalid or sealed judgment stage') + "$"):
            delegations.record_judgment(r, app['id'], app['judgments']['interpret']['output'], execution_id='EX-close-interpret', stage=stage)
        self.assertEqual((i, r, case), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)
