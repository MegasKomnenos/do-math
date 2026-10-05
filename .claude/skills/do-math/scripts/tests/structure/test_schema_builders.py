"""Schema builders share no mutable node (의무 1-E): a result changed in place changes no other result and no global.

``_calls`` samples public product functions whose name contains schema, with
calls covering the declared arguments. ``TRANSFORMERS`` names the ones that
take a caller's schema and return it changed; their results are checked through
the builders that use them. A schema function in neither table fails the walk,
so a newly named schema function cannot silently miss the walk. Each argument
variant runs twice to catch retained results. Unnamed composition helpers have
a separate probe; the name-based census alone is not a complete 1-E population.
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
}


def _schema_functions():
    """Public module-level functions of the product whose names say they build or change a schema."""
    found = set()
    for path in PRODUCT.rglob('*.py'):
        module = '.'.join(('do_math',) + path.relative_to(PRODUCT).with_suffix('').parts).removesuffix('.__init__')
        for node in ast.parse(path.read_text(encoding='utf-8')).body:
            if isinstance(node, ast.FunctionDef) and 'schema' in node.name and not node.name.startswith('_'):
                found.add(module + '.' + node.name)
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
        declared = set(_calls()) | set(TRANSFORMERS)
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
