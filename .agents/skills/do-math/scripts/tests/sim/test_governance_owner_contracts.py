"""실제 엔진의 도메인 소비자 등록·원천·설정 입력 계약."""
from copy import deepcopy
import unittest

from do_math import governance as gov
from do_math.governance_engine import bind_host_configuration
from do_math.canonical import exact_content_hash
from support.governance_cases import records_sim
from support.scheduling_hosts import host_configuration


class GovernanceOwnerContractTests(unittest.TestCase):
    def test_builtin_authority_owner_cannot_be_replaced(self):
        sim = records_sim()
        handlers = sim.engine.governance_owner_handlers()
        adapter = handlers['configuration']
        before = dict(handlers)
        with self.assertRaisesRegex(ValueError, '^cannot replace a governance authority owner$'):
            gov.register_import_owner(handlers, 'grant', **adapter)
        self.assertEqual(handlers, before)

    def test_duplicate_registered_owner_is_rejected(self):
        sim = records_sim()
        handlers = sim.engine.governance_owner_handlers()
        before = dict(handlers)
        with self.assertRaisesRegex(ValueError, '^import owner already registered$'):
            gov.register_import_owner(handlers, 'configuration', **handlers['configuration'])
        self.assertEqual(handlers, before)

    def test_noncallable_owner_is_rejected_before_registration(self):
        sim = records_sim()
        handlers = sim.engine.governance_owner_handlers()
        adapter = {**handlers['configuration'], 'apply': 'not callable'}
        before = dict(handlers)
        with self.assertRaisesRegex(ValueError, '^owner needs apply, validate and currentness functions$'):
            gov.register_import_owner(handlers, 'custom', **adapter)
        self.assertEqual(handlers, before)

    def test_custom_owner_contract_is_copied_into_catalog(self):
        sim = records_sim()
        handlers = sim.engine.governance_owner_handlers()
        contract = {'document': 'custom.md', 'section': 'bounded'}
        gov.register_import_owner(handlers, 'custom', **handlers['configuration'], contract=contract)
        contract['section'] = 'changed'
        catalog = gov.import_consumer_catalog(handlers, clock=sim.clock)
        self.assertEqual(next(row for row in catalog if row['owner_kind'] == 'custom'),
                         {'owner_kind': 'custom', 'payload_contract': {'document': 'custom.md', 'section': 'bounded'}})
        self.assertEqual([row['owner_kind'] for row in catalog],
                         sorted(gov.DECISION_OWNER_KINDS | {'configuration', 'research_record', 'evidence', 'custom'}))

    def test_custom_owner_without_contract_is_not_advertised(self):
        sim = records_sim()
        handlers = sim.engine.governance_owner_handlers()
        gov.register_import_owner(handlers, 'custom', **handlers['configuration'])
        before = dict(handlers)
        with self.assertRaisesRegex(ValueError, '^registered import owner has no producer contract: custom$'):
            gov.import_consumer_catalog(handlers, clock=sim.clock)
        self.assertEqual(handlers, before)

    def test_nonobject_owner_adapter_is_rejected(self):
        sim = records_sim()
        handlers = sim.engine.governance_owner_handlers()
        handlers['custom'] = []
        before = dict(handlers)
        with self.assertRaisesRegex(ValueError, '^owner registration needs apply/validate/basis$'):
            gov._owner_handlers(handlers, clock=sim.clock)
        self.assertEqual(handlers, before)

    def test_configuration_owner_requires_this_instance(self):
        sim = records_sim()
        handler = sim.engine.governance_owner_handlers()['configuration']
        unit = {'owner_ref': sim.instance['id'], 'payload': {'config': {'call_timeout_seconds': 901}}}
        self.assertIsNone(handler['validate'](sim.instance, sim.runtime, unit))
        unit['owner_ref'] = 'other'
        before = deepcopy((sim.instance, sim.runtime))
        with self.assertRaisesRegex(ValueError, '^configuration import must bind this instance and an explicit config patch$'):
            handler['validate'](sim.instance, sim.runtime, unit)
        self.assertEqual((sim.instance, sim.runtime), before)

    def test_host_alias_requires_user_authority_without_writing_source(self):
        sim = records_sim()
        config = host_configuration()
        before = deepcopy((sim.instance, config))
        with self.assertRaisesRegex(ValueError, '^host configuration request requires user authority$'):
            bind_host_configuration(sim.instance, config, origin='operator')
        self.assertEqual((sim.instance, config), before)

    def test_host_source_collision_is_rejected_without_rebinding(self):
        sim = records_sim()
        config = host_configuration()
        identifier = 'GS-host-' + exact_content_hash({'host_resources': config['host_resources']})
        sim.instance['governance_sources'][identifier] = gov.preserve_source(identifier, '다른 승인', origin='user')
        before = deepcopy((sim.instance, config))
        with self.assertRaisesRegex(ValueError, '^host configuration source identity changed$'):
            bind_host_configuration(sim.instance, config, origin='user')
        self.assertEqual((sim.instance, config), before)

    def test_source_revision_and_nonobject_source_are_rejected(self):
        source = gov.preserve_source('GS-close', '원문', origin='user')
        self.assertEqual(source['bytes'], 6)
        with self.assertRaisesRegex(ValueError, '^source revision must be positive$'):
            gov.preserve_source(source['id'], source['text'], origin=source['origin'], revision=0)
        with self.assertRaisesRegex(ValueError, '^immutable source required$'):
            gov.validate_source([])

    def test_unknown_interpretation_stage_is_rejected(self):
        with self.assertRaisesRegex(ValueError, '^unknown interpretation stage$'):
            gov.interpretation_schema('unknown')
        schema = gov.interpretation_schema('check')
        self.assertEqual(schema['properties']['decision']['enum'], ['approved', 'revision_required', 'unresolved'])
        self.assertNotIn('repair', schema['required'])

    def test_missing_input_reference_is_rejected_without_writing(self):
        sim = records_sim()
        before = deepcopy((sim.instance, sim.runtime))
        with self.assertRaisesRegex(ValueError, '^intent input reference does not resolve$'):
            gov.import_input_source(sim.instance, sim.runtime, 'missing')
        self.assertEqual((sim.instance, sim.runtime), before)
