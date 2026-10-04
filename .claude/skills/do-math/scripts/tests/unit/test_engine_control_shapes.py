"""Domain boundaries check their own input and never read a falsy value as a default (layer 2).

The control shape check (``control_contracts``), the import approval
(``governance.apply_import``), the time parsers, the grant authorization, the
trust registration checks and the knowledge control each reject a malformed
value with their own reason. Every negative case fixes that reason.
"""
from copy import deepcopy
from pathlib import Path
import re
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from do_math import governance
from do_math.control_contracts import fields, obj, user_decision_changed, validate_control_payload, validate_decision_shape
from do_math.governance import authorize
from do_math.knowledge_engine import KnowledgeEngineMixin
from do_math.trust_validation import environment_errors
from do_math.values import parse_utc
from support.record_builders import checked_import
from support.trust_inputs import trust_environment, trust_fixture

NOT_TIME = '^time must be a nonempty ISO timestamp string$'


def exactly(reason):
    return '^' + re.escape(reason) + '$'


class DomainShapeTests(unittest.TestCase):
    def test_central_and_owner_termination_rules_agree_for_every_declared_state(self):
        """3-C/C-12: the real owner wrapper and canonical predicate on the finite state space."""
        from itertools import product
        from do_math.planning import instance_ended
        from do_math.record_schemas.schemas import RESEARCH_FIELDS, RUNTIME_FIELDS
        from support.sim import Sim
        sim = Sim.activated()
        before = deepcopy(sim.engine.store.load())
        states = RESEARCH_FIELDS['lifecycle']['properties']['state']['enum']
        statuses = RUNTIME_FIELDS['status']['enum']
        for life, status, permanently_closed in product(states, statuses, (False, True)):
            with self.subTest(lifecycle=life, status=status, permanently_closed=permanently_closed):
                sim.instance['lifecycle'].update(state=life, permanently_closed=permanently_closed)
                sim.runtime['status'] = status
                expected = permanently_closed or status in ('closed', 'completed')
                self.assertIs(instance_ended(sim.instance, sim.runtime), expected)
                self.assertIs(sim.engine._instance_closed(), expected)
        self.assertEqual(sim.engine.store.load(), before)

    def test_control_field_builders_enforce_declared_types_and_allow_unspecified_properties(self):
        from jsonschema import Draft202012Validator
        schema = obj(fields(text='id reason', lists='roles targets', objects='resources'))
        validator = Draft202012Validator(schema)
        valid = {'id': 'UC-one', 'reason': 'request', 'roles': ['maintenance'],
                 'targets': [], 'resources': {}, 'domain_owned': True}
        self.assertTrue(validator.is_valid(valid))
        for key in ('id', 'reason', 'roles', 'targets', 'resources'):
            with self.subTest(key=key):
                self.assertFalse(validator.is_valid({**valid, key: 0}))
        self.assertTrue(Draft202012Validator(obj()).is_valid({'domain_owned': True}))
        self.assertFalse(Draft202012Validator(obj()).is_valid([]))

    def test_user_decision_change_distinguishes_operational_settings_from_model_authority(self):
        from do_math.configuration import DEFAULT_CONFIG
        current = deepcopy(DEFAULT_CONFIG)
        before = deepcopy(current)
        self.assertIs(user_decision_changed(current, deepcopy(current)), False)
        operational = {**current, 'plan_settle_seconds': current['plan_settle_seconds'] + 1}
        self.assertIs(user_decision_changed(current, operational), False)
        model_authority = {**current, 'claude_only_assigned_model': not current['claude_only_assigned_model']}
        self.assertIs(user_decision_changed(current, model_authority), True)
        self.assertEqual(current, before)

    def test_initialization_checks_the_boolean_flags_its_owner_actually_consumes(self):
        for key in ('adopt_current_governance', 'adopt_default_review_policy'):
            with self.subTest(key=key):
                self.assertIsNone(validate_control_payload('decision', '', {'change': {'kind': 'initialization', key: True}}))
                with self.assertRaisesRegex(ValueError, exactly(f'config/change/{key}: invalid type (expected boolean)')):
                    validate_control_payload('decision', '', {'change': {'kind': 'initialization', key: ['yes']}})

    def test_input_carries_no_approval_and_domain_approvals_are_validated(self):
        from support.entry import entry
        _entry = entry()
        instance, runtime, bundle, _ = checked_import()
        with self.assertRaisesRegex(ValueError, exactly('config: invalid additionalProperties (expected False)')):
            validate_control_payload('input', 'text', {'import_approvals': {}})
        for value, reason in (([1], 'import_approvals/U: invalid type (expected object)'),
                              ('text', 'import_approvals/U: invalid type (expected object)'),
                              (True, 'import_approvals/U: invalid type (expected object)'),
                              ({'actor': 'user', 'source_ref': []}, 'import_approvals/U/source_ref: invalid type (expected string)')):
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, exactly(reason)):
                governance.apply_import(instance, runtime, bundle['id'], approvals={'U': value}, clock=_entry.ports.clock)

    def test_shape_check_preserves_partial_configuration_and_nullable_candidate_fields(self):
        self.assertIsNone(validate_control_payload('configure', '', {'tier_models': {
            'low': 'custom-low', 'medium': 'custom-medium', 'high': 'custom-high'}}))
        self.assertIsNone(validate_control_payload('knowledge', '', {'operation': 'import',
            'candidate': {'relation_claim': None, 'formal_result_ref': None}}))

    def test_targetless_plan_can_be_resubmitted_as_the_exact_allowed_action(self):
        self.assertIsNone(validate_decision_shape({'kind': 'repetition_continue',
            'allowed_action': {'id': 'AC-plan', 'role': 'research_plan', 'target': None}}))
        for damaged in ([], 0, False, 'plan'):
            with self.subTest(damaged=damaged), self.assertRaisesRegex(ValueError,
                    exactly('change/allowed_action: invalid type (expected object)')):
                validate_decision_shape({'kind': 'repetition_continue', 'allowed_action': damaged})

    def test_trust_registration_nested_structures_return_errors_without_host_io(self):
        environment_reason = {
            'toolchain_record': 'toolchain_record requires the absolute path of <record ID>.json and that ID',
            'binding': 'trust binding requires a baseline index and its fingerprint, content and validation digests'}
        with tempfile.TemporaryDirectory() as directory:
            config = trust_fixture(Path(directory), ['lean'])
            environment, binding = trust_environment(config)
            with patch.object(Path, 'resolve', side_effect=AssertionError('host access')), \
                    patch('os.stat', side_effect=AssertionError('host access')):
                self.assertIsNone(validate_control_payload('trust', 'register', config))
                self.assertEqual(environment_errors(environment, binding), [])
                for field in ('toolchain_record', 'binding', 'toolchain'):
                    for value in (None, False, 1, 'text', [{}], {}):
                        with self.subTest(field=field, value=value):
                            first = environment_reason.get(field) or (
                                'toolchain.configured_command is missing' if value == {} else 'toolchain must be an object')
                            register = (f'config/{field}: invalid type (expected object)' if value != {}
                                        else 'config: ' + first)
                            with self.assertRaisesRegex(ValueError, '^' + re.escape(register) + ('$' if value != {} else '')):
                                validate_control_payload('trust', 'register', {**config, field: value})
                            changed = {**environment, field: value} if field != 'binding' else environment
                            errors = environment_errors(changed, value if field == 'binding' else binding)
                            self.assertEqual(errors[0], first)
                with self.assertRaisesRegex(ValueError, exactly(
                        'config: trust register requires exactly toolchain, allowed_axioms, toolchain_record and binding')):
                    validate_control_payload('trust', 'register', {**config, 'unrecognized': True})
                with self.assertRaisesRegex(ValueError, exactly(
                        "config/operation: invalid enum (expected ['register', 'transition', 'invalidate'])")):
                    validate_control_payload('trust', 'recheck', {'operation': 'recheck', 'env_id': 'TE-x'})

    def test_time_boundaries_reject_nonstrings_instead_of_treating_falsy_input_as_now(self):
        for parse in (governance.timestamp, parse_utc):
            for value in (False, 0, 1, [], {}, ''):
                with self.subTest(parse=parse, value=value), self.assertRaisesRegex(ValueError, NOT_TIME):
                    parse(value)

    def test_authorize_checks_time_even_without_an_eligible_grant(self):
        for grants in ({}, {'GR-other': {'id': 'GR-other', 'kind': 'external', 'roles': []}}):
            with self.subTest(grants=grants), self.assertRaisesRegex(ValueError, NOT_TIME):
                authorize({'grants': grants}, {'role': 'maintenance'}, at='')

    def test_unknown_knowledge_operation_cannot_mutate_review_or_running_work(self):
        owner = SimpleNamespace(instance={'knowledge': {'KN-one': {'review_cycle_id': 'RC-one'}}},
            runtime={'review_cycles': {'RC-one': {'status': 'working', 'research': {}, 'history': []}},
                     'executions': {'EX-one': {'status': 'running', 'action': {'target': 'KN-one'}}}})
        before = deepcopy((owner.instance, owner.runtime))
        config = {'operation': 'unknown-operation', 'id': 'KN-one'}
        with self.assertRaisesRegex(ValueError, exactly(
                "config/operation: invalid enum (expected ['import', 'register-kind', 'withdraw-kind', "
                "'import-relation', 'revise', 'invalidate'])")):
            validate_control_payload('knowledge', '', config)
        with self.assertRaisesRegex(ValueError, '^knowledge operation must be revise or invalidate$'):
            KnowledgeEngineMixin._knowledge_control(owner, config, 'UC-one')
        self.assertEqual((owner.instance, owner.runtime), before)


if __name__ == '__main__':
    unittest.main()
