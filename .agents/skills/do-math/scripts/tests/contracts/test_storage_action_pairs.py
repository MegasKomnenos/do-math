"""Real queue/wait producers, exact input ownership and cold stored reads."""
from copy import deepcopy
import json
import unittest

from do_math.wait_rules import PREPARATION_WAIT_RULES
from do_math.canonical import canonical_json
from support.provider_probes import ObservedCalls
from support.fakes.clock import FakeClock
from support.sim import Sim, warm_template
from support.storage_action_pairs import keep, preparation_case, reader

setUpModule = warm_template


class StorageActionPairTests(unittest.TestCase):
    def test_shared_action_and_wait_fields_have_real_stored_producers(self):
        """About four minutes cold: real owner inputs, publication and first blob decode.

        Existing producer scenes retain their independent content assertions;
        one collected corpus supplies the common action and waiting obligations.
        This exceeds the contract soft budget because these are stored owners.
        """
        self.maxDiff = None
        from contracts.pairs import assert_pair
        from support.storage_action_pairs import StoredActions, action_pair, waiting_pair
        from support.state_builders import installed_contract
        from support.storage_execution_pairs import (stored_execution_inputs, assert_stored_delegation_input,
            stored_operational_dispositions, stored_recovery_and_machine_outputs)
        from support.storage_action_pairs import (impact_samples, revision_samples, control_and_due_samples,
            recovery_samples, overflow_samples, diagnosis_samples, intent_samples, judgment_samples,
            observation_samples, review_research_samples, other_owner_samples, work_overflow_samples,
            formal_failure_samples, assert_merge_samples, diagnosed_retry_samples, repetition_samples)
        samples = StoredActions(self)
        for scene in (judgment_samples, observation_samples, review_research_samples, other_owner_samples,
                      work_overflow_samples, formal_failure_samples, assert_merge_samples, repetition_samples,
                      impact_samples, revision_samples, control_and_due_samples, recovery_samples,
                      overflow_samples, diagnosis_samples, diagnosed_retry_samples, intent_samples, stored_execution_inputs, assert_stored_delegation_input,
                      stored_operational_dispositions, stored_recovery_and_machine_outputs):
            with self.subTest(scene=scene.__name__):
                scene(samples)
        for kind in PREPARATION_WAIT_RULES:
            sim, _, _ = preparation_case(kind, source=b'Exact assessment source\r\n'
                if kind == 'model_assessment_input' else None)
            sim.engine._save()
            keep(sim.engine, samples.samples, kind)
        contract = installed_contract()
        for pair in (action_pair(contract, samples.samples), waiting_pair(contract, samples.samples)):
            with self.subTest(pair=pair.name):
                assert_pair(self, pair, samples.samples)

        from do_math.state_contract import StateContract
        # Actual schemas acquire an optional field; the ordinary receiving
        # checker still accepts the same produced states, but reverse must fail.
        for family_name in ('queue', 'waiting_actions'):
            family = contract.family('runtime', family_name)
            schema = deepcopy(family.schema)
            row = schema if family_name == 'queue' else schema['additionalProperties']
            row['properties']['unproduced_optional'] = {'type': 'string'}
            drift = StateContract()
            drift.register_family('runtime', family_name, shape=family.shape, schema=schema, identity=family.identity)
            pair = (action_pair if family_name == 'queue' else waiting_pair)(drift, samples.samples)
            with self.assertRaisesRegex(AssertionError, 'unproduced_optional'):
                assert_pair(self, pair, samples.samples)


    def test_invalid_queue_and_wait_values_reject_before_writes_and_on_cold_read(self):
        sim, action, _ = preparation_case('model_assessment_input')
        engine = sim.engine
        engine._enqueue('maintenance', reason='Independent preserved request')
        engine._save()
        head, instance, runtime = reader(engine).load(engine.head)
        aid = action['id']
        cases = [
            (('queue', 0, 'role'), 17, "runtime/queue/None/role: 17 is not of type 'string'"),
            (('waiting_actions', aid, 'reason'), 17, 'runtime/waiting_actions/None/' + aid + "/reason: 17 is not valid under any of the given schemas"),
            (('waiting_actions', aid, 'action', 'role'), 17, 'runtime/waiting_actions/None/' + aid + "/action/role: 17 is not of type 'string'"),
            (('waiting_actions', aid, 'action', 'id'), 'AC-different', 'waiting action key differs from its preserved action'),
            (('waiting_actions', aid, 'execution_id'), 'EX-absent', 'waiting action reference does not resolve: execution_id'),
            (('waiting_actions', aid, 'input_version', 'goal'), True, 'runtime/waiting_actions/None/' + aid + "/input_version/goal: True is not of type 'integer'"),
        ]
        for field in ('activity_id', 'execution_id', 'created_at'):
            cases.append((('queue', 0, field), 'old-slot',
                "runtime/queue/None/: Additional properties are not allowed ('" + field + "' was unexpected)"))
        for field in ('condition', 'waiting_reason', 'recovery'):
            cases.append((('waiting_actions', aid, field), {},
                'runtime/waiting_actions/None/' + aid + ": Additional properties are not allowed ('" + field + "' was unexpected)"))
        for field in ('contract_revision', 'proposal_version'):
            cases.append((('queue', 0, 'repetition_bases'), {field: '0' * 64},
                "runtime/queue/None/repetition_bases: Additional properties are not allowed ('" + field + "' was unexpected)"))
        for tokens, value, message in cases:
            with self.subTest(tokens=tokens):
                changed = deepcopy(runtime)
                target = changed
                for token in tokens[:-1]:
                    target = target[token]
                target[tokens[-1]] = value
                with ObservedCalls(write=engine.ports.git_backend.write_object) as calls:
                    with self.assertRaises(ValueError) as error:
                        engine.store.save_with_state(head, instance, changed)
                    self.assertEqual(str(error.exception), message)
                    self.assertEqual(calls.count('write'), 0)
                self.assertEqual(reader(engine).load(head), (head, instance, runtime))
                self.assertEqual(engine.store.resolve_snapshot(None), head)
        # Only this negative read bypasses validation at publication.
        path = 'runtime/waiting_actions/state.json'
        broken = json.loads(reader(engine).read(path, head))
        broken['record'][aid]['action']['id'] = 'AC-different'
        damaged = engine.store._store.publish(head, {path: canonical_json(broken)}).head
        with self.assertRaisesRegex(ValueError, '^waiting action key differs from its preserved action$'):
            reader(engine).load(damaged)
        self.assertEqual(reader(engine).load(head), (head, instance, runtime))

    def test_live_action_does_not_absorb_a_later_request(self):
        sim = Sim.activated()
        engine = sim.engine
        engine.runtime['queue'] = []
        engine._enqueue('maintenance', reason='First request')
        first = engine.runtime['queue'][0]
        execution = engine._register_execution(first, {'id': 'EX-live-request', 'role': 'maintenance'})
        self.assertEqual(execution['status'], 'queued')
        immutable_input = deepcopy(execution['action'])
        engine._enqueue('maintenance', reason='Later request', requested_by='UC-later')
        self.assertEqual(len(engine.runtime['queue']), 2)
        later = deepcopy(engine.runtime['queue'][1])
        self.assertNotEqual(later['id'], first['id'])
        self.assertEqual(execution['action'], immutable_input)
        samples = []
        engine._save()
        old = keep(engine, samples, 'live request and independent successor')
        engine._remove_action(first)
        engine._save()
        loaded = keep(engine, samples, 'remove only original action', previous=old)
        self.assertEqual(loaded[2]['queue'], [later])
        self.assertEqual(loaded[2]['executions'][execution['id']]['action'], immutable_input)

    def test_revision_binding_owns_the_basis_and_preserves_the_parent_wait(self):
        from do_math import revisions
        from support.planning_contract_inputs import prepared_sim, only_task, defer_revision
        sim = prepared_sim()
        engine = sim.engine
        tid = only_task(sim)['id']
        parent = defer_revision(sim, [tid], required=True)
        original_parent = deepcopy(engine.runtime['waiting_actions'][parent])
        basis = revisions.capture_targets(sim.instance, sim.runtime, [tid])
        independent = deepcopy(basis)
        engine._enqueue('research_preparation', revision_targets=basis, reason='Independent revision request')
        child, = engine.runtime['queue']
        # Binding carries the parent's obligation, without changing the input.
        self.assertEqual(basis, independent)
        self.assertEqual(child['revision_parent_ids'], [parent])
        self.assertIs(child['revision_targets'][tid]['required'], True)
        self.assertEqual(child['revision_targets'][tid]['obligation_refs'], [
            {'action_id': parent, 'reason': '추가 근거를 기다린다.'}])
        basis[tid]['caller mutation'] = True
        self.assertNotIn('caller mutation', child['revision_targets'][tid])
        self.assertEqual(engine.runtime['waiting_actions'][parent], original_parent)
        engine._save()
        samples = []
        saved = keep(engine, samples, 'revision parent and bound child')
        self.assertEqual(saved[2]['waiting_actions'][parent], original_parent)
        self.assertEqual(saved[2]['queue'], [child])

    def test_enqueue_owns_all_mutable_request_inputs_before_any_merge(self):
        sim = Sim.activated()
        engine = sim.engine
        engine.runtime['queue'] = []
        fields = {'reason': '첫 요청 e\u0301\r\n', 'requested_by': 'UC-original',
            'observation': {'kind': 'explicit', 'notes': ['원문 e\u0301\r\n']},
            'obligation_ids': ['OB-original'], 'receipt_refs': ['CR-original'],
            'event_refs': [], 'observation_refs': ['artifact:original'],
            'evidence_refs': ['artifact:input'], 'revision_followup': [],
            'assessment_targets': {}, 'observation_rule_targets': {}}
        original = deepcopy(fields)
        expected_id = FakeClock(*sim.clock.state()).new_id('AC')
        engine._enqueue('research_plan', **fields)
        queued = deepcopy(engine.runtime['queue'][0])
        self.assertEqual({key: queued[key] for key in original}, original)
        self.assertEqual((queued['role'], queued['id'], queued['lineage_id']),
                         ('research_plan', expected_id, expected_id))
        for value in fields.values():
            if isinstance(value, list):
                value.append('caller mutation')
            elif isinstance(value, dict):
                value['caller mutation'] = True
        # Both merge-only inputs and comparison inputs must be owned on insert.
        self.assertEqual(engine.runtime['queue'], [queued])
        samples = []
        engine._save()
        old = keep(engine, samples, 'owned request')
        sim.restart()
        self.assertEqual(reader(sim.engine).load(old[0])[2]['queue'], [queued])

    def test_merge_keeps_first_identity_ordered_unique_triggers_and_separate_payloads(self):
        from support.storage_action_pairs import StoredActions, assert_merge_samples
        assert_merge_samples(StoredActions(self))

    def test_actual_preparation_waits_preserve_original_actions_and_diagnostic_content(self):
        """About 25 s cold: four real owner publications; external ports are doubles."""
        for kind in PREPARATION_WAIT_RULES:
            with self.subTest(kind=kind):
                sim, action, _ = preparation_case(kind)
                engine = sim.engine
                expected = deepcopy(engine.runtime['waiting_actions'][action['id']])
                engine._save()
                samples = []
                loaded = keep(engine, samples, kind)
                entry = loaded[2]['waiting_actions'][action['id']]
                self.assertEqual(entry, expected)
                self.assertEqual(entry['kind'], kind)
                self.assertEqual(entry['next_owner'], PREPARATION_WAIT_RULES[kind]['next_owner'])
                self.assertEqual(entry['action']['id'], action['id'])
                self.assertEqual(entry['action']['role'], action['role'])
                self.assertEqual(entry['action'].get('lineage_id'), action.get('lineage_id'))
                if kind == 'model_assessment_input':
                    identifier, = action['assessment_targets']
                    self.assertEqual(entry['question'], 'Task preparation pending: ' + identifier + ': Missing assessment input')
                    self.assertEqual(entry['reason'], entry['question'])
                    self.assertEqual(entry['input_version']['inputs'], [row['id'] for row in loaded[2]['inputs']])
                elif kind == 'observation_rule_input':
                    self.assertEqual(entry['observation_rule_deferrals'], [
                        {'task_id': identifier, 'reason': 'Missing source',
                         'missing_inputs': ['user_input'], 'next_owner': 'user'}
                        for identifier in action['observation_rule_targets']])
                    self.assertEqual(entry['rule_input_version'], {'user_input': [row['id'] for row in loaded[2]['inputs']]})
                else:
                    self.assertTrue(entry['reason'])
                manifest = json.loads(reader(engine).read('runtime/_state/manifest.json', loaded[0]))
                self.assertEqual(manifest['containers']['waiting_actions'], {'shape': 'singleton'})
                envelope = json.loads(reader(engine).read('runtime/waiting_actions/state.json', loaded[0]))
                self.assertEqual(envelope['record'][action['id']], expected)
                sim.restart()
                self.assertEqual(sim.runtime['waiting_actions'][action['id']], expected)
