"""3-C current canonical rules and their complete direct call-site population.

Finite behavioral spaces are checked in their existing domain test modules.
This table covers three original pairs; it does not declare the other eight
original pairs or every future semantic copy verified.
"""
import ast
from pathlib import Path
import unittest


SCRIPTS = Path(__file__).resolve().parents[2]
RULES = {
    'B-16': ('model_policy.py', 'work_profile_selection', {
        ('core_engine.py', '_apply'), ('lifecycle_engine.py', '_refresh_readiness'),
        ('planning.py', 'task_ready'), ('planning_engine.py', '_finish_assessment_preparation')}),
    'C-12': ('planning.py', 'instance_ended', {
        ('core_engine.py', 'submit_control'), ('lifecycle_engine.py', '_instance_closed'),
        ('provider_engine.py', 'record_model_policy_violation'),
        ('repair_execution.py', 'recovery_held'), ('reporting.py', 'task_status')}),
    'D-02': ('task_scope.py', 'validate_withdrawal_scope', {
        ('submission.py', '_payload_issues'), ('submission.py', 'disposition'),
        ('task_scope.py', '_validate')}),
}


class CanonicalRuleTests(unittest.TestCase):
    def test_every_declared_rule_has_one_definition_and_all_direct_consumers_use_it(self):
        trees = {p.name: ast.parse(p.read_text(encoding='utf-8'))
                 for p in (SCRIPTS / 'do_math').glob('*.py')}
        for rule, (owner, name, expected) in RULES.items():
            with self.subTest(rule=rule):
                definitions = [(path, node.name) for path, tree in trees.items()
                    for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                    and node.name == name]
                self.assertEqual(definitions, [(owner, name)])
                calls = set()
                for path, tree in trees.items():
                    bindings = {}
                    for node in ast.walk(tree):
                        if isinstance(node, ast.ImportFrom):
                            module = (node.module or '').split('.')[-1]
                            for imported in node.names:
                                if imported.name == name and module == owner[:-3]:
                                    bindings[imported.asname or name] = name
                    for function in ast.walk(tree):
                        if not isinstance(function, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            continue
                        for call in ast.walk(function):
                            if not isinstance(call, ast.Call):
                                continue
                            if isinstance(call.func, ast.Name) and call.func.id == name:
                                self.assertTrue(path == owner or call.func.id in bindings,
                                                'shared rule name is not imported from its owner')
                                calls.add((path, function.name))
                            elif isinstance(call.func, ast.Attribute) and call.func.attr == name:
                                self.assertIsInstance(call.func.value, ast.Name)
                                self.assertEqual(call.func.value.id, owner[:-3])
                                calls.add((path, function.name))
                            elif isinstance(call.func, ast.Name) and call.func.id in bindings:
                                calls.add((path, function.name))
                self.assertEqual(calls, expected, 'new or missing direct consumers require declaration review')
