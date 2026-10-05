"""Schema builders share no mutable node (의무 1-E): a result changed in place changes no other result and no global.

``_calls`` samples public module functions whose name contains schema, with
calls covering the declared arguments. ``TRANSFORMERS`` names the ones that
take a caller's schema and return it changed; their results are checked through
the builders that use them. A schema function without a declaration fails the walk,
so a newly named schema function cannot silently miss the walk. Each argument
variant runs twice to catch retained results. Unnamed composition helpers have
a separate probe. Class schema methods are declared by their tested delegate or
borrowed-input contract; reviewed constant builders have direct probes below.
The bounded ownership dispositions come from return_ownership_review (G4/G5) in
docs/do-math/시험-재편-2026-09-29/단계-전환표-2026-10-03.json. This registration
does not certify that the name-based census covers the whole 1-E population.
Action/extension samples cover ROLES and their shape-changing preparation,
review-cycle and stage inputs, without multiplying unrelated axes. Audit and
impact samples exercise filtering and repeated option construction.
"""
import ast
from copy import deepcopy
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

PRODUCT = Path(__file__).resolve().parents[2] / 'do_math'
REQUEST = {'integration_id': 'IN-1', 'payload_sha256': 'a' * 64, 'producer_execution_id': 'EX-1',
           'input_snapshot': 'b' * 40, 'plans': {'scope': {'digest': 'c' * 64}}}


def _calls():
    from do_math import contracts, governance, integration, record_schemas, review_cycle, submission, supervision
    from do_math.contracts import ROLES
    # Empty target maps are the installed preflight's presence-based inputs.
    # The ordinary role sample supplies the fourth (neither key) combination.
    preparations = [{'role': 'research_preparation', **targets} for targets in (
        {'assessment_targets': {}}, {'observation_rule_targets': {}},
        {'assessment_targets': {}, 'observation_rule_targets': {}})]
    actions = [{'role': role} for role in ROLES] + preparations + [
        {'role': 'maintenance', 'stage': 'impact_review', 'input_basis': {'impact_review': REQUEST}},
        {'role': 'intent_interpretation', 'stage': 'check'}]
    extensions = [{'role': role, **cycle} for role in ROLES
                  for cycle in ({}, {'review_cycle_id': 'RC-1'})] + preparations
    # The schema consumes the installed governance records' identity, status
    # and content, including the required_inputs list (not a keyed mapping).
    audit = {'id': 'AU-1', 'kind': 'additional_audit', 'revision': 1, 'supersedes': [],
             'status': 'active', 'content': {'scope': ['P'], 'required_inputs': ['CH1', 'POL1'],
             'assessor': 'goal_audit', 'verdict_mapping': {
                 'pass': 'satisfied', 'partial': 'not_satisfied', 'unknown': 'unresolved'}}}
    inactive = {**deepcopy(audit), 'id': 'AU-old', 'status': 'superseded', 'superseded_by': 'AU-1'}
    policy = {'id': 'POL1', 'kind': 'policy', 'revision': 1, 'supersedes': [], 'status': 'active',
              'content': {'rule_id': 'R1', 'text': 'Require evidence', 'scope': ['P'],
                          'reason_refs': ['CH1'], 'audit_refs': []}}
    second_audit = {**deepcopy(audit), 'id': 'AU-2'}
    audits = [{}, {'AU-1': audit}, {'AU-old': inactive, 'POL1': policy},
              {'AU-1': audit, 'AU-2': second_audit, 'AU-old': inactive, 'POL1': policy}]
    requests = [REQUEST, {**REQUEST, 'plans': {
        'bundle': {'digest': 'c' * 64},
        'activity-extensions.json/knowledge_changes/0': {'digest': 'd' * 64}}}]
    return {
        'do_math.contracts.schema_for': [lambda role=role: contracts.schema_for(role) for role in ROLES],
        'do_math.contracts.action_schema': [lambda action=action: contracts.action_schema(action)
                                            for action in actions],
        'do_math.contracts.disposition_schema': [contracts.disposition_schema],
        'do_math.governance.additional_audit_schema': [
            lambda records=records: governance.additional_audit_schema({'governance': records}) for records in audits],
        'do_math.governance.interpretation_schema': [lambda stage=stage: governance.interpretation_schema(stage)
                                                     for stage in ('interpret', 'check')],
        'do_math.integration.impact_review_response_schema': [
            lambda request=request: integration.impact_review_response_schema(request) for request in requests],
        'do_math.record_schemas.config_schema': [record_schemas.config_schema],
        'do_math.review_cycle.stage_schema': [lambda stage=stage: review_cycle.stage_schema(stage)
                                              for stage in ('scope', 'initial', 'organize', 'answer', 'judge')],
        'do_math.review_cycle.research_schema': [review_cycle.research_schema],
        'do_math.review_cycle.research_request_schema': [review_cycle.research_request_schema],
        'do_math.submission.extension_schema': [lambda action=action: submission.extension_schema(action)
                                                for action in extensions],
        'do_math.supervision.repair_report_schema': [lambda diagnosed=diagnosed: supervision.repair_report_schema(
            diagnosed=diagnosed) for diagnosed in (False, True)],
    }


TRANSFORMERS = {
    'do_math.contracts.identify_schema': 'content-addresses a caller schema',
    'do_math.contracts.schema_reference': 'refers to a caller schema',
    'do_math.contracts.with_integration_schema': 'wraps a caller schema; checked through schema_for',
    'do_math.governance_engine.GovernanceEngineMixin._governance_schema':
        'borrows non-audit input; audit copies and adds additional_audit_schema; '
        'CoreEngineMixin._response_schema owns the final with_integration_schema copy',
}


DELEGATED_SCHEMA_METHODS = {
    'do_math.core_engine.CoreEngineMixin._response_schema':
        'every successful branch ends in with_integration_schema -> identify_schema -> json_copy; '
        '_calls exercises that copy boundary through schema_for/action_schema',
    'do_math.review_engine.ReviewEngineMixin._review_schema':
        'pending-seat validation then _seat_schema; _composition_calls covers all five stages; '
        'the method adds no mutable input to the returned schema',
    'do_math.review_engine.ReviewEngineMixin._review_research_schema':
        '_calls covers research_schema; the method adds two fresh enum lists containing only '
        'the valid pending request ID and digest strings',
}


# Borrowed constant lookups are not owned builders: task_contracts.repetition_outcome
# and repair_execution.recovery_outcome return their global table rows for reading.
# G5 explicitly excludes them; no copy API or immutable-return promise is implied.


def _schema_functions():
    """Public module functions and all class methods whose names contain schema."""
    found = set()
    for path in PRODUCT.rglob('*.py'):
        module = '.'.join(('do_math',) + path.relative_to(PRODUCT).with_suffix('').parts).removesuffix('.__init__')
        for node in ast.parse(path.read_text(encoding='utf-8')).body:
            if isinstance(node, ast.FunctionDef) and 'schema' in node.name and not node.name.startswith('_'):
                found.add(module + '.' + node.name)
            elif isinstance(node, ast.ClassDef):
                for method in node.body:
                    if isinstance(method, (ast.FunctionDef, ast.AsyncFunctionDef)) and 'schema' in method.name:
                        found.add(module + '.' + node.name + '.' + method.name)
    return found


def _containers(value):
    found, pending = [], [value]
    while pending:
        node = pending.pop()
        if isinstance(node, (dict, list)):
            found.append(node)
            pending.extend(node.values() if isinstance(node, dict) else node)
    return found


def _composition_calls():
    """Schema constructors omitted by the schema-name walk; use their real schema inputs."""
    from do_math import cli_contract, contracts, control_contracts, review_cycle, review_engine
    from do_math.record_schemas import schemas
    return {
        'do_math.contracts.closed_object': [
            lambda: contracts.closed_object({'name': contracts.STRING}),
            lambda: contracts.closed_object({'name': contracts.STRING}, [])],
        'do_math.contracts._schema': [lambda: contracts._schema({'sample': contracts.STRING})],
        'do_math.control_contracts.obj': [control_contracts.obj,
            lambda: control_contracts.obj({'id': control_contracts.TEXT})],
        'do_math.control_contracts.fields': [control_contracts.fields,
            lambda: control_contracts.fields(text='id reason', lists='refs', objects='scope')],
        'do_math.record_schemas.schemas.array': [schemas.array] + [
            lambda unique=unique: schemas.array(schemas.ID, unique) for unique in (False, True)],
        'do_math.record_schemas.schemas.nullable': [lambda: schemas.nullable(schemas.TEXT)],
        'do_math.record_schemas.schemas.enum': [lambda: schemas.enum(), lambda: schemas.enum('one', 'two')],
        'do_math.record_schemas.schemas.obj': [lambda: schemas.obj({}),
            lambda: schemas.obj({'id': schemas.ID}, ('id',))],
        'do_math.record_schemas.schemas.record': [lambda: schemas.record({}),
            lambda: schemas.record({'name': schemas.TEXT}, ('name',))],
        'do_math.record_schemas.schemas.mapping': [lambda: schemas.mapping(schemas.TEXT)],
        'do_math.review_cycle._array': [lambda: review_cycle._array(review_cycle.TEXT)],
        'do_math.review_engine._seat_schema': [lambda stage=stage: review_engine._seat_schema(
            {'proposal_digest': 'a' * 64}, {'stage': stage})
            for stage in ('scope', 'initial', 'organize', 'answer', 'judge')],
        'do_math.cli_contract._request_schema': [lambda: cli_contract._request_schema(cli_contract.build_parser())],
    }


def _isolation_problems(calls):
    """Keep every sampled result alive and report every alias without mutating product globals."""
    global_nodes = set()
    for name, module in list(sys.modules.items()):
        if name == 'do_math' or name.startswith('do_math.'):
            for value in vars(module).values():
                global_nodes.update(id(node) for node in _containers(value))
    seen, kept, problems = set(), [], []
    for builder, variants in calls.items():
        for index, call in enumerate(variants):
            for repeat in range(2):
                kept.append(call())
                if not isinstance(kept[-1], dict):
                    problems.append((builder, index, repeat, ['the builder did not return a schema object']))
                    continue
                nodes = [id(node) for node in _containers(kept[-1])]
                reasons = []
                if len(nodes) != len(set(nodes)):
                    reasons.append('a node appears twice in one result')
                if global_nodes & set(nodes):
                    reasons.append('the result holds a module-global node')
                if seen & set(nodes):
                    reasons.append('the result shares a node with an earlier result')
                if reasons:
                    problems.append((builder, index, repeat, reasons))
                seen.update(nodes)
    return problems


def _constant_object_calls():
    """Reviewed owned dict builders outside the schema-name census (G5)."""
    from do_math import contracts, knowledge_io, planning
    from do_math.state_contract import StateContract
    contract = StateContract()
    contract.register_family('research', 'sample', schema=contracts.closed_object({'name': contracts.STRING}))
    # One installed definition for each of the three existing constructor shapes.
    definitions = {}
    for row in knowledge_io.BUILTIN_DEFINITIONS:
        shape = (row['family'], row['constraints']['mathematical_claim'], row['constraints']['requires_evidence'])
        definitions.setdefault(shape, row)
    return {
        'do_math.planning.lifecycle_values': [planning.lifecycle_values],
        'do_math.knowledge_io._definition': [
            lambda row=row: knowledge_io._definition(row['family'], row['token'], row['meaning'],
                mathematical=row['constraints']['mathematical_claim'], evidence=row['constraints']['requires_evidence'])
            for row in definitions.values()],
        # The two checker calls cover the initial digest computation and cache hit.
        'do_math.state_contract.StateContract.manifest': [contract.manifest],
    }


class SchemaBuilderTests(unittest.TestCase):
    def test_control_schema_composition_does_not_share_mutable_field_nodes(self):
        """The unnamed obj/fields builders also fall under the 1-E isolation invariant."""
        from do_math import control_contracts
        first = control_contracts.obj(control_contracts.fields(text='id'))
        second = control_contracts.obj(control_contracts.fields(text='id'))
        expected = {'second': deepcopy(second), 'global': deepcopy(control_contracts.TEXT)}
        child = first['properties']['id']
        original = deepcopy(child)
        try:
            child['type'] = 'integer'
            self.assertEqual({'second': second, 'global': control_contracts.TEXT}, expected)
        finally:
            # Restore through the returned object even if this exposes a shared
            # node, so a red reproduction cannot contaminate later tests.
            child.clear()
            child.update(original)

    def test_every_schema_function_is_declared(self):
        declared = set(_calls()) | set(TRANSFORMERS) | set(DELEGATED_SCHEMA_METHODS)
        self.assertEqual(sorted(_schema_functions() - declared), [], 'schema functions not declared here')
        self.assertEqual(sorted(declared - _schema_functions()), [], 'declared schema functions that no longer exist')

    def test_results_share_no_node_with_each_other_or_a_module_global(self):
        self.assertEqual(_isolation_problems(_calls()), [])

    def test_schema_samples_reach_context_dependent_shapes(self):
        # Confirm the added fixtures actually enter the intended producer shapes.
        from do_math.contracts import ROLES
        calls = _calls()
        actions = calls['do_math.contracts.action_schema']
        self.assertIn('regenerate_after', actions[ROLES.index('research_preparation')]()['required'])
        for call in actions[len(ROLES):len(ROLES) + 3]:
            schema = call()
            self.assertEqual(schema['properties']['candidates']['maxItems'], 0)
            self.assertNotIn('regenerate_after', schema['properties'])
        self.assertIn('impact_review', actions[-2]()['properties'])
        self.assertIn('bundle_sha256', actions[-1]()['required'])
        extensions = calls['do_math.submission.extension_schema']
        ordinary = extensions[2 * ROLES.index('research_preparation')]()['properties']
        self.assertIn('task_title', ordinary['model_assessments']['items']['required'])
        for call, observes in zip(extensions[-3:], (False, True, True)):
            properties = call()['properties']
            self.assertIn('task_id', properties['model_assessments']['items']['required'])
            self.assertEqual('task_conditions' in properties, observes)
            self.assertEqual('observation_rule_deferrals' in properties, observes)
            if observes:
                self.assertEqual(properties['task_conditions']['items']['required'], ['task_id', 'observation_rules'])
        for cycle in (0, 1):
            identity = extensions[2 * ROLES.index('identity_review') + cycle]()['properties']
            self.assertEqual('research_requests' in identity, bool(cycle))
            supplemental = extensions[2 * ROLES.index('supplemental_research') + cycle]()['properties']
            self.assertEqual(bool(supplemental), not cycle)
        for call, count in zip(calls['do_math.governance.additional_audit_schema'], (0, 1, 0, 2)):
            schema = call()
            self.assertEqual((schema['minItems'], schema['maxItems']), (count, count))
            if count:
                self.assertEqual(len(schema['items']['oneOf']), count)
                for option in schema['items']['oneOf']:
                    self.assertEqual(option['properties']['input_hashes']['required'], ['CH1', 'POL1'])
                    self.assertEqual(option['properties']['verdict']['enum'], ['pass', 'partial', 'unknown'])
            else:
                self.assertIs(schema['items'], False)
        for call, count in zip(calls['do_math.integration.impact_review_response_schema'], (1, 2)):
            decisions = call()['properties']['plan_decisions']
            self.assertEqual((decisions['minItems'], decisions['maxItems']), (count, count))
            self.assertEqual(len(decisions['items']['oneOf']), count)

    def test_unnamed_schema_composition_results_detach_every_mutable_node(self):
        self.assertEqual(_isolation_problems(_composition_calls()), [])

    def test_constant_object_builders_detach_mutable_nodes_and_keep_immutable_leaves(self):
        from do_math import planning
        from do_math.state_contract import StateContract
        self.assertEqual(_isolation_problems(_constant_object_calls()), [])
        # lifecycle_values intentionally shares the owners' immutable frozensets.
        for family, values in planning.lifecycle_values().items():
            with self.subTest(family=family):
                self.assertIsInstance(values, frozenset)
                self.assertTrue(all(isinstance(value, str) for value in values))
        self.assertTrue(all(isinstance(value, str) for value in StateContract().manifest().values()))

    def test_observation_contract_builders_detach_all_rows_from_each_other_and_operators(self):
        from do_math import execution_profiles, observations
        calls = {
            'do_math.observations.observation_rule_contract': observations.observation_rule_contract,
            'do_math.execution_profiles._research_observation_rule_contract':
                execution_profiles._research_observation_rule_contract,
        }
        seen = {id(node) for node in _containers(observations.OPERATORS)}
        kept = []
        for name, call in calls.items():
            for repeat in range(2):
                with self.subTest(builder=name, repeat=repeat):
                    result = call()
                    kept.append(result)
                    self.assertIsInstance(result, list)
                    self.assertEqual([row['operator'] for row in result], sorted(observations.OPERATORS))
                    for row in result:
                        self.assertIsInstance(row, dict)
                        self.assertTrue(all(isinstance(value, str) for value in row.values()))
                    nodes = [id(node) for node in _containers(result)]
                    self.assertEqual(len(nodes), len(set(nodes)))
                    self.assertFalse(seen.intersection(nodes))
                    seen.update(nodes)

    def test_blocked_key_builder_returns_independent_sets_of_immutable_names(self):
        from do_math import context_store
        before = deepcopy(context_store.BLOCKED_KEYS)
        kept = []
        # All exact keys, one role fallback, and an unregistered scope.
        for scope in (*context_store.BLOCKED_KEYS, 'identity_review:scope', 'unregistered'):
            with self.subTest(scope=scope):
                first, second = context_store._blocked(scope), context_store._blocked(scope)
                self.assertIsInstance(first, set)
                self.assertIsInstance(second, set)
                self.assertTrue(all(isinstance(value, str) for value in first | second))
                self.assertEqual(first, second)
                for result in (first, second):
                    self.assertTrue(all(result is not earlier for earlier in kept))
                    kept.append(result)
                expected = second.copy()
                original = first.copy()
                try:
                    first.add('isolation-probe')
                    self.assertEqual(second, expected)
                    self.assertEqual(context_store.BLOCKED_KEYS, before)
                finally:
                    first.clear()
                    first.update(original)


class SchemaBuilderIsolationCheckTests(unittest.TestCase):
    def test_a_builder_without_a_schema_cannot_pass_by_having_no_mutable_nodes(self):
        checker = SchemaBuilderTests('test_results_share_no_node_with_each_other_or_a_module_global')
        with patch(__name__ + '._calls', return_value={'disabled-builder': [lambda: None]}):
            with self.assertRaisesRegex(AssertionError, 'the builder did not return a schema object'):
                checker.test_results_share_no_node_with_each_other_or_a_module_global()

    def test_a_retained_mutable_result_is_detected_on_the_repeated_call(self):
        retained = {'type': 'object', 'properties': {}}
        checker = SchemaBuilderTests('test_results_share_no_node_with_each_other_or_a_module_global')
        # Replace only this structural check's own sample catalog, never product code.
        with patch(__name__ + '._calls', return_value={'retained-schema': [lambda: retained]}):
            with self.assertRaisesRegex(AssertionError, 'the result shares a node with an earlier result'):
                checker.test_results_share_no_node_with_each_other_or_a_module_global()
        self.assertEqual(retained, {'type': 'object', 'properties': {}})

    def test_independent_results_remain_valid_on_the_repeated_call(self):
        calls = []
        def fresh():
            calls.append(None)
            return {'type': 'object', 'properties': {}}
        checker = SchemaBuilderTests('test_results_share_no_node_with_each_other_or_a_module_global')
        with patch(__name__ + '._calls', return_value={'fresh-schema': [fresh]}):
            checker.test_results_share_no_node_with_each_other_or_a_module_global()
        self.assertEqual(len(calls), 2)


if __name__ == '__main__':
    unittest.main()
