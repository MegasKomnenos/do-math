"""Schema builders share no mutable node (의무 1-E): a result changed in place changes no other result and no global.

``_calls`` samples public product functions whose name contains schema, with
calls covering the declared arguments. ``TRANSFORMERS`` names the ones that
take a caller's schema and return it changed; their results are checked through
the builders that use them. A schema function in neither table fails the walk,
so a newly named schema function cannot silently miss the walk. Each argument
variant runs twice to catch retained results. Unnamed composition helpers have
a separate probe; the name-based census alone is not a complete 1-E population.
"""
import ast
from copy import deepcopy
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

PRODUCT = Path(__file__).resolve().parents[2] / 'do_math'
ROLES_WITH_ACTIONS = ('research_preparation', 'research_work', 'maintenance', 'intent_interpretation')
REQUEST = {'integration_id': 'IN-1', 'payload_sha256': 'a' * 64, 'producer_execution_id': 'EX-1',
           'input_snapshot': 'b' * 40, 'plans': {'scope': {'digest': 'c' * 64}}}


def _calls():
    from do_math import contracts, governance, integration, record_schemas, review_cycle, submission, supervision
    from do_math.contracts import ROLES
    return {
        'do_math.contracts.schema_for': [lambda role=role: contracts.schema_for(role) for role in ROLES],
        'do_math.contracts.action_schema': [lambda role=role: contracts.action_schema({'role': role})
                                            for role in ROLES_WITH_ACTIONS],
        'do_math.contracts.disposition_schema': [contracts.disposition_schema],
        'do_math.governance.additional_audit_schema': [lambda: governance.additional_audit_schema({})],
        'do_math.governance.interpretation_schema': [lambda stage=stage: governance.interpretation_schema(stage)
                                                     for stage in ('interpret', 'check')],
        'do_math.integration.impact_review_response_schema': [lambda: integration.impact_review_response_schema(REQUEST)],
        'do_math.record_schemas.config_schema': [record_schemas.config_schema],
        'do_math.review_cycle.stage_schema': [lambda stage=stage: review_cycle.stage_schema(stage)
                                              for stage in ('scope', 'initial', 'organize', 'answer', 'judge')],
        'do_math.review_cycle.research_schema': [review_cycle.research_schema],
        'do_math.review_cycle.research_request_schema': [review_cycle.research_request_schema],
        'do_math.submission.extension_schema': [lambda: submission.extension_schema(
            {'role': 'research_work', 'review_cycle_id': 'RC-1'})],
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
