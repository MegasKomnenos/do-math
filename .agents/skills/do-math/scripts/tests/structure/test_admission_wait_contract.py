"""4-A: real admission producers, wait declarations and resolvers agree."""
import ast
import importlib
from pathlib import Path
import unittest

from do_math import wait_rules
from support.source_values import assignments_in, result_values

PRODUCT = Path(__file__).resolve().parents[2] / 'do_math'


class AdmissionWaitDeclarationTests(unittest.TestCase):
    def test_budget_conflicts_and_wait_generators_have_complete_resolvers(self):
        tree = ast.parse((PRODUCT / 'budget.py').read_text(encoding='utf-8'))
        constraints = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == 'BudgetConflict':
                kind = next((value.value for value in node.keywords if value.arg == 'constraint_kind'), None)
                self.assertIsNotNone(kind, node.lineno)
                constraints |= result_values(kind, {})
        self.assertEqual(constraints, set(wait_rules.BUDGET_WAIT_KINDS))
        slots = ast.parse((PRODUCT / 'session_slots.py').read_text(encoding='utf-8'))
        produced = set()
        sites = []
        functions = {node.name: node for node in ast.walk(slots) if isinstance(node, ast.FunctionDef)}
        producers = []
        for function in functions.values():
            for assignment in (node for node in ast.walk(function) if isinstance(node, ast.Assign)):
                if not any(isinstance(target, ast.Attribute) and target.attr == 'admission_wait'
                           and isinstance(target.value, ast.Name) and target.value.id == 'self'
                           for target in assignment.targets):
                    continue
                value = assignment.value
                if isinstance(value, ast.Constant) and value.value is None:
                    continue
                if isinstance(value, ast.Dict):
                    producers.append((function, value))
                elif isinstance(value, ast.Call) and isinstance(value.func, ast.Attribute) and \
                        isinstance(value.func.value, ast.Name) and value.func.value.id == 'self':
                    delegated = functions[value.func.attr]
                    returns = [node.value for node in ast.walk(delegated)
                               if isinstance(node, ast.Return) and isinstance(node.value, ast.Dict)]
                    self.assertTrue(returns, delegated.name)
                    producers.extend((delegated, returned) for returned in returns)
                else:
                    self.fail('unregistered dynamic admission wait producer: ' + ast.dump(value))
        for function, node in producers:
            value = next((value for key, value in zip(node.keys, node.values)
                          if isinstance(key, ast.Constant) and key.value == 'kind'), None)
            self.assertIsNotNone(value, (function.name, node.lineno))
            if isinstance(value, ast.Attribute) and ast.unparse(value) == 'wait_rules.PROVIDER_WAIT':
                produced.add(wait_rules.PROVIDER_WAIT)
            elif isinstance(value, ast.Name) and value.id == 'kind':
                assigned = assignments_in(function)['kind']
                self.assertTrue(all(isinstance(row, ast.Subscript) and
                    ast.unparse(row.value) == 'wait_rules.BUDGET_WAIT_KINDS' for row in assigned))
                produced.update(wait_rules.BUDGET_WAIT_KINDS[kind] for kind in constraints)
            else:
                produced |= result_values(value, assignments_in(function))
            sites.append((function.name, node.lineno))
        self.assertTrue(sites)
        self.assertEqual(produced, set(wait_rules.ADMISSION_WAIT_RULES))
        for kind, rule in wait_rules.ADMISSION_WAIT_RULES.items():
            with self.subTest(kind=kind):
                self.assertTrue(rule['fields'])
                self.assertTrue(rule['condition'])
                self.assertTrue(rule['resolvers'])
                for resolver in rule['resolvers']:
                    module, *attributes = resolver.split('.')
                    target = importlib.import_module('do_math.' + module)
                    for name in attributes:
                        target = getattr(target, name)
                    self.assertTrue(callable(target), resolver)
                self.assertEqual(kind in wait_rules.SLOT_WAITS, rule['slot'])
                self.assertEqual(kind in wait_rules.RESOURCE_WAITS, rule['resource'])
        self.assertEqual(wait_rules.ADMISSION_WAITS, frozenset(produced))
