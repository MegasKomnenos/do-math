"""Schema builders share no mutable node (의무 1-E): a result changed in place changes no other result and no global.

``BUILDERS`` names every public product function whose name says it builds a
schema, with calls covering its arguments. ``TRANSFORMERS`` names the ones that
take a caller's schema and return it changed; their results are checked through
the builders that use them. A schema function in neither table fails the walk,
so a new builder cannot be missed the way a hand-kept list misses it.
"""
import ast
from pathlib import Path
import sys
import unittest

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


class SchemaBuilderTests(unittest.TestCase):
    def test_every_schema_function_is_declared(self):
        declared = set(_calls()) | set(TRANSFORMERS)
        self.assertEqual(sorted(_schema_functions() - declared), [], 'schema functions not declared here')
        self.assertEqual(sorted(declared - _schema_functions()), [], 'declared schema functions that no longer exist')

    def test_results_share_no_node_with_each_other_or_a_module_global(self):
        calls = _calls()
        global_nodes = set()
        for name, module in list(sys.modules.items()):
            if name == 'do_math' or name.startswith('do_math.'):
                for value in vars(module).values():
                    global_nodes.update(id(node) for node in _containers(value))
        seen, kept = {}, []  # earlier results stay alive, so their node IDs cannot be reused
        for builder, variants in calls.items():
            for index, call in enumerate(variants):
                with self.subTest(builder=builder, call=index):
                    kept.append(call())
                    nodes = [id(node) for node in _containers(kept[-1])]
                    self.assertEqual(len(nodes), len(set(nodes)), 'a node appears twice in one result')
                    self.assertEqual(global_nodes & set(nodes), set(), 'the result holds a module-global node')
                    self.assertEqual(set(seen) & set(nodes), set(), 'the result shares a node with an earlier result')
                    seen.update(dict.fromkeys(nodes))


if __name__ == '__main__':
    unittest.main()
