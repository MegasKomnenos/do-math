"""4-A: preparation producers and real resolvers cover the declared kinds."""
import ast
import importlib
from pathlib import Path
import unittest

from do_math.wait_rules import PREPARATION_WAIT_RULES, PREPARATION_INPUT_WAITS, TASK_OBSERVATION_WAITS
from support.source_values import assignments_in, result_values

PRODUCT = Path(__file__).resolve().parents[2] / 'do_math'


class PreparationWaitDeclarationTests(unittest.TestCase):
    def test_preparation_wait_producers_and_resolvers_cover_the_declaration(self):
        tree = ast.parse((PRODUCT / 'wait_rules.py').read_text(encoding='utf-8'))
        functions = {node.name: node for node in tree.body if isinstance(node, ast.FunctionDef)}
        kinds = set()
        sites = []
        for path in sorted(PRODUCT.rglob('*.py')):
            source = ast.parse(path.read_text(encoding='utf-8'))
            for function in (node for node in ast.walk(source) if isinstance(node, ast.FunctionDef)):
                for node in ast.walk(function):
                    if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Name):
                        continue
                    name = node.func.id
                    if name not in {'observation_preparation_wait', 'preparation_deferral_kind'}:
                        continue
                    producer = functions[name]
                    assignments = assignments_in(producer)
                    for returned in (value for value in ast.walk(producer) if isinstance(value, ast.Return)):
                        expression = returned.value
                        if isinstance(expression, ast.Call) and isinstance(expression.func, ast.Name) and expression.func.id == 'waiting_action':
                            expression = expression.args[0]
                        if isinstance(expression, ast.Dict):
                            expression = next(value for key, value in zip(expression.keys, expression.values)
                                              if isinstance(key, ast.Constant) and key.value == 'kind')
                        kinds |= result_values(expression, assignments)
                    sites.append((path.name, function.name, node.lineno))
        self.assertTrue(sites)
        self.assertEqual(kinds, set(PREPARATION_WAIT_RULES))
        self.assertEqual(PREPARATION_INPUT_WAITS | TASK_OBSERVATION_WAITS, kinds)
        self.assertFalse(PREPARATION_INPUT_WAITS & TASK_OBSERVATION_WAITS)
        for kind, rule in PREPARATION_WAIT_RULES.items():
            with self.subTest(kind=kind):
                self.assertTrue(rule['condition'])
                self.assertTrue(rule['next_owner'])
                self.assertTrue(rule['resolvers'])
                for reference in rule['resolvers']:
                    module, *attributes = reference.split('.')
                    target = importlib.import_module('do_math.' + module)
                    for name in attributes:
                        target = getattr(target, name)
                    self.assertTrue(callable(target), reference)
