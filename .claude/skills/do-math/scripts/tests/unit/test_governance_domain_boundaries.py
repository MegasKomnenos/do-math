"""소유자 계약과 입구 스키마가 먼저 차단하는 입력을 구분한다."""
from copy import deepcopy
import unittest

from do_math import governance as gov
from support.governance_cases import delegated_sim
from support.governance_sim import checked_sim, checked_bundle


class GovernanceDomainBoundaryTests(unittest.TestCase):
    def test_task_ids_object_is_rejected_by_admission_before_domain_branch(self):
        sim = delegated_sim()
        change = deepcopy(sim.instance['decisions']['DC-close-original']['change'])
        change['grant']['task_ids'] = {}
        before = deepcopy((sim.instance, sim.runtime, change))
        with self.assertRaisesRegex(ValueError, r'^change/grant/task_ids: invalid type \(expected array\)$'):
            gov.apply_decision(sim.instance, sim.runtime, change, source_ref='GS-close-delegation', clock=sim.clock)
        self.assertEqual((sim.instance, sim.runtime, change), before)

    def test_credential_array_is_rejected_by_admission_before_domain_branch(self):
        sim = delegated_sim()
        change = deepcopy(sim.instance['decisions']['DC-close-original']['change'])
        change['grant']['credential_env'] = []
        before = deepcopy((sim.instance, sim.runtime, change))
        with self.assertRaisesRegex(ValueError, r'^change/grant/credential_env: invalid type \(expected object\)$'):
            gov.apply_decision(sim.instance, sim.runtime, change, source_ref='GS-close-delegation', clock=sim.clock)
        self.assertEqual((sim.instance, sim.runtime, change), before)

    def test_delegation_array_is_rejected_by_admission_before_domain_branch(self):
        sim = delegated_sim()
        change = deepcopy(sim.instance['decisions']['DC-close-delegation']['change'])
        change['delegation'] = []
        before = deepcopy((sim.instance, sim.runtime, change))
        with self.assertRaisesRegex(ValueError, r'^change/delegation: invalid type \(expected object\)$'):
            gov.apply_decision(sim.instance, sim.runtime, change, source_ref='GS-close-delegation', clock=sim.clock)
        self.assertEqual((sim.instance, sim.runtime, change), before)

    def test_configuration_owner_must_remain_registered(self):
        sim = checked_sim('configuration')
        bundle = checked_bundle(sim)
        before = deepcopy((sim.instance, sim.runtime))
        with self.assertRaisesRegex(ValueError, '^import domain owner is no longer registered$'):
            gov.current_import(sim.instance, sim.runtime, bundle['id'], clock=sim.clock)
        self.assertEqual((sim.instance, sim.runtime), before)

    def test_configuration_currentness_uses_owner_premise(self):
        sim = checked_sim('configuration')
        bundle = checked_bundle(sim)
        sim.instance['config']['call_timeout_seconds'] += 1
        before = deepcopy((sim.instance, sim.runtime))
        with self.assertRaisesRegex(ValueError, '^import domain premises changed$'):
            gov.current_import(sim.instance, sim.runtime, bundle['id'],
                owner_handlers=sim.engine.governance_owner_handlers(), clock=sim.clock)
        self.assertEqual((sim.instance, sim.runtime), before)

    def test_changed_original_requires_new_import_lineage(self):
        sim = checked_sim()
        i, r = deepcopy((sim.instance, sim.runtime))
        bundle = r['intent_imports'][checked_bundle(sim)['id']]
        request = next(row for row in r['inputs'] if row['id'] == bundle['input_ref'])
        request['text'] = 'X' + request['text'][1:]
        source = gov.import_input_source(i, r, bundle['input_ref'])
        output = deepcopy(bundle['output'])
        output['repair'] = {'previous_sha256': bundle['sha256'], 'changed_unit_ids': [], 'actions': ['원문 변경 재검토']}
        before = deepcopy((i, r, source, output))
        with self.assertRaisesRegex(ValueError, '^a new original requires a new import lineage$'):
            gov.prepare_import(i, r, source, output, execution_id=bundle['execution_id'], input_ref=bundle['input_ref'],
                previous_id=bundle['id'], owner_handlers=sim.engine.governance_owner_handlers(), clock=sim.clock)
        self.assertEqual((i, r, source, output), before)

    def test_payload_owner_must_match_unit_owner(self):
        sim = checked_sim()
        bundle = checked_bundle(sim)
        output = deepcopy(bundle['output'])
        output['import_units'][0]['owner_kind'] = 'policy'
        before = deepcopy((sim.instance, sim.runtime, output))
        with self.assertRaisesRegex(ValueError, '^payload and unit have different owners$'):
            gov.validate_import_units(sim.instance, sim.runtime, bundle['source'], output, clock=sim.clock)
        self.assertEqual((sim.instance, sim.runtime, output), before)

    def test_payload_target_must_match_owner_coordinate(self):
        sim = checked_sim()
        bundle = checked_bundle(sim)
        output = deepcopy(bundle['output'])
        output['import_units'][0]['owner_ref'] = 'other'
        before = deepcopy((sim.instance, sim.runtime, output))
        with self.assertRaisesRegex(ValueError, '^payload target differs from owner coordinate$'):
            gov.validate_import_units(sim.instance, sim.runtime, bundle['source'], output, clock=sim.clock)
        self.assertEqual((sim.instance, sim.runtime, output), before)
