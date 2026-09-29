"""Invalid input is rejected at its boundary without blocking later controls."""
from copy import deepcopy
from pathlib import Path
import json
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from engine_fixtures import QUERY_INSTANCE_ID, start_query_repository
from do_math.control_contracts import PAYLOADS
from do_math.engine import ResearchEngine, control
from do_math.repository import canonical_json

# Every public control action: the shaped payloads and configure, whose shape is the configuration section.
ACTIONS = (*PAYLOADS, 'configure')
BAD_PAYLOADS = [
    ('decision', {'change': []}),
    ('decision', {'change': {'kind': 'charter', 'record': {'kind': 'charter', 'content': []}}}),
    ('decision', {'change': {'kind': 'grant', 'grant': {'kind': 'local', 'roles': ['maintenance'], 'expires_at': 1}}}),
    ('decision', {'change': {'kind': 'initialization', 'operation': 'probe', 'profile_ref': []}}),
    ('request', {'role': 'maintenance', 'review_replacement': {'action': []}}),
    ('request', {'role': 'maintenance', 'review_restoration': {'action': []}}),
    ('knowledge', {'operation': 'import', 'candidate': []}),
    ('knowledge', {'operation': 'import-relation', 'relation': []}),
    ('knowledge', {'operation': 'revise', 'id': 'KN-one', 'changes': [], 'reason': 'test'}),
    ('trust', {'operation': 'register', 'toolchain': [], 'manifest': {}, 'allowed_axioms': []}),
    ('external', {'operation': 'reconcile', 'id': 'EO-one', 'evidence': []}),
    ('conversation', {'operation': 'attach', 'id': 'one', 'generation': [], 'lease_seconds': 60}),
]


class ControlShapeBoundaryTests(unittest.TestCase):
    def setUp(self):
        start_query_repository(self)

    def test_all_public_actions_reject_nonobject_config_without_creating_inbox(self):
        f = self
        for action in ACTIONS:
            for value in ([], [1], False, 0, 'text'):
                with self.subTest(action=action, value=value), self.assertRaises(ValueError):
                    control(f.git, QUERY_INSTANCE_ID, action, config=value, text='input')
        inbox = f.workspace / 'control' / QUERY_INSTANCE_ID
        self.assertEqual(list(inbox.glob('*.json')), [])

    def test_nested_shapes_are_rejected_before_publication(self):
        f = self
        for action, config in BAD_PAYLOADS:
            with self.subTest(action=action, config=config), self.assertRaises(ValueError):
                control(f.git, QUERY_INSTANCE_ID, action, config=config)
        inbox = f.workspace / 'control' / QUERY_INSTANCE_ID
        self.assertEqual(list(inbox.glob('*.json')), [])

    def test_cli_nested_decision_errors_are_input_errors_without_pending_requests(self):
        f = self
        for index, (_, config) in enumerate(BAD_PAYLOADS[1:3]):
            path = f.root / ('decision-' + str(index) + '.json')
            path.write_bytes(canonical_json(config['change']))
            result = subprocess.run([sys.executable, str(Path(__file__).resolve().parents[1] / 'do_math.py'),
                'decision', '--repository', str(f.git), '--instance', QUERY_INSTANCE_ID,
                '--file', str(path)], capture_output=True, text=True, encoding='utf-8')
            self.assertEqual(result.returncode, 2, result.stderr)
            self.assertEqual(json.loads(result.stdout)['error']['kind'], 'input_error')
        self.assertEqual(list((f.workspace / 'control' / QUERY_INSTANCE_ID).glob('*.json')), [])

    def test_receiver_rejects_bad_payload_once_then_processes_following_valid_control(self):
        f = self
        bad_ids = []
        for index, (action, config) in enumerate([('pause', [1]), *BAD_PAYLOADS]):
            identifier = 'UC-invalid-' + str(index)
            control(f.git, QUERY_INSTANCE_ID, 'pause', request_id=identifier)
            path = f.workspace / 'control' / QUERY_INSTANCE_ID / (identifier + '.json')
            request = json.loads(path.read_bytes())
            request.update(action=action, config=config)
            path.write_bytes(canonical_json(request))
            bad_ids.append(identifier)
        control(f.git, QUERY_INSTANCE_ID, 'pause', text='valid later request', request_id='UC-good')
        engine = ResearchEngine(f.git, QUERY_INSTANCE_ID)
        engine.process_controls()
        for identifier in bad_ids:
            self.assertEqual(engine.runtime['processed_controls'].count(identifier), 1)
            self.assertEqual(engine.control_result(identifier)['effect'], 'rejected')
        self.assertEqual(engine.control_result('UC-good')['effect'], 'applied')
        engine = ResearchEngine(f.git, QUERY_INSTANCE_ID)
        engine.process_controls()
        self.assertTrue(all(engine.runtime['processed_controls'].count(identifier) == 1 for identifier in bad_ids))

    def test_out_of_range_lease_is_rejected_without_blocking_later_control(self):
        f = self
        control(f.git, QUERY_INSTANCE_ID, 'conversation', request_id='UC-lease', config={
            'operation': 'attach', 'id': 'conversation', 'generation': 1,
            'disconnect_policy': 'pause', 'lease_seconds': (1 << 53) - 1})
        control(f.git, QUERY_INSTANCE_ID, 'pause', request_id='UC-after-lease')
        engine = ResearchEngine(f.git, QUERY_INSTANCE_ID)
        engine.process_controls()
        self.assertEqual(engine.control_result('UC-lease')['effect'], 'rejected')
        self.assertEqual(engine.control_result('UC-after-lease')['effect'], 'applied')


class DomainShapeTests(unittest.TestCase):
    def test_initialization_checks_the_boolean_flags_its_owner_actually_consumes(self):
        from do_math.control_contracts import validate_control_payload
        for key in ('adopt_current_governance', 'adopt_default_review_policy'):
            with self.subTest(key=key):
                validate_control_payload('decision', '', {'change': {'kind': 'initialization', key: True}})
                with self.assertRaises(ValueError):
                    validate_control_payload('decision', '', {'change': {'kind': 'initialization', key: ['yes']}})

    def test_input_carries_no_approval_and_domain_approvals_are_validated(self):
        from do_math.control_contracts import validate_control_payload
        from do_math import governance
        from record_fixtures import checked_import, audited_governance
        instance, runtime, bundle, _ = checked_import()
        with self.assertRaises(ValueError):
            validate_control_payload('input', 'text', {'import_approvals': {}})
        for value in ([1], 'text', True, {'actor': 'user', 'source_ref': []}):
            approvals = {'U': value}
            with self.subTest(value=value), self.assertRaises(ValueError):
                governance.apply_import(instance, runtime, bundle['id'], approvals=approvals)

    def test_shape_check_preserves_partial_configuration_and_nullable_candidate_fields(self):
        from do_math.control_contracts import validate_control_payload
        validate_control_payload('configure', '', {'tier_models': {'low': 'custom-low',
            'medium': 'custom-medium', 'high': 'custom-high'}})
        validate_control_payload('knowledge', '', {'operation': 'import',
            'candidate': {'relation_claim': None, 'formal_result_ref': None}})

    def test_targetless_plan_can_be_resubmitted_as_the_exact_allowed_action(self):
        from do_math.control_contracts import validate_decision_shape
        validate_decision_shape({'kind': 'repetition_continue',
            'allowed_action': {'id': 'AC-plan', 'role': 'research_plan', 'target': None}})

    def test_trust_registration_nested_structures_return_errors_without_host_io(self):
        from research_fixtures import trust_environment, trust_fixture
        from do_math.control_contracts import validate_control_payload
        from do_math.trust_validation import environment_errors
        with tempfile.TemporaryDirectory() as directory:
            config = trust_fixture(Path(directory), ['lean'])
            environment, binding = trust_environment(config)
            with patch.object(Path, 'resolve', side_effect=AssertionError('host access')), \
                 patch('os.stat', side_effect=AssertionError('host access')):
                validate_control_payload('trust', 'register', config)
                self.assertEqual(environment_errors(environment, binding), [])
                for field in ('toolchain_record', 'binding', 'toolchain'):
                    for value in (None, False, 1, 'text', [{}], {}):
                        with self.subTest(field=field, value=value):
                            with self.assertRaises(ValueError):
                                validate_control_payload('trust', 'register', {**config, field: value})
                            changed = {**environment, field: value} if field != 'binding' else environment
                            self.assertTrue(environment_errors(changed, value if field == 'binding' else binding))
                with self.assertRaises(ValueError):
                    validate_control_payload('trust', 'register', {**config, 'unrecognized': True})
                with self.assertRaisesRegex(ValueError, 'enum'):
                    validate_control_payload('trust', 'recheck', {'operation': 'recheck', 'env_id': 'TE-x'})

    def test_time_boundaries_reject_nonstrings_instead_of_treating_falsy_input_as_now(self):
        from do_math import governance
        from do_math.values import parse_utc
        for parse in (governance.timestamp, parse_utc):
            for value in (False, 0, 1, [], {}, ''):
                with self.subTest(parse=parse, value=value), self.assertRaises(ValueError):
                    parse(value)

    def test_authorize_checks_time_even_without_an_eligible_grant(self):
        from do_math.governance import authorize
        for grants in ({}, {'GR-other': {'id': 'GR-other', 'kind': 'external', 'roles': []}}):
            with self.subTest(grants=grants), self.assertRaises(ValueError):
                authorize({'grants': grants}, {'role': 'maintenance'}, at='')

    def test_unknown_knowledge_operation_cannot_mutate_review_or_running_work(self):
        from types import SimpleNamespace
        from do_math.knowledge_engine import KnowledgeEngineMixin
        from do_math.control_contracts import validate_control_payload
        owner = SimpleNamespace(instance={'knowledge': {'KN-one': {'review_cycle_id': 'RC-one'}}},
            runtime={'review_cycles': {'RC-one': {'status': 'working', 'research': {}, 'history': []}},
                     'executions': {'EX-one': {'status': 'running', 'action': {'target': 'KN-one'}}}})
        before = deepcopy((owner.instance, owner.runtime))
        config = {'operation': 'unknown-operation', 'id': 'KN-one'}
        with self.assertRaises(ValueError):
            validate_control_payload('knowledge', '', config)
        with self.assertRaises(ValueError):
            KnowledgeEngineMixin._knowledge_control(owner, config, 'UC-one')
        self.assertEqual((owner.instance, owner.runtime), before)


if __name__ == '__main__':
    unittest.main()
