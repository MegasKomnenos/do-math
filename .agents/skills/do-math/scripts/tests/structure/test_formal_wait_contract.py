"""4-A: formal wait construction covers exactly the declared release policies."""
import ast
import importlib
from pathlib import Path
import unittest

from do_math.wait_rules import FORMAL_WAIT_RULES, FORMAL_RECOVERABLE_STOPS
from support.source_values import assignments_in, result_values

PRODUCT = Path(__file__).resolve().parents[2] / 'do_math'


class FormalWaitDeclarationTests(unittest.TestCase):
    def test_real_formal_wait_producers_and_resolvers_cover_the_declaration(self):
        kinds, sites = set(), []
        for path in sorted(PRODUCT.rglob('*.py')):
            tree = ast.parse(path.read_text(encoding='utf-8'))
            for function in (node for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))):
                for node in ast.walk(function):
                    if not isinstance(node, ast.Call):
                        continue
                    name = node.func.id if isinstance(node.func, ast.Name) else getattr(node.func, 'attr', None)
                    if name != 'formal_wait':
                        continue
                    kind = node.args[1] if len(node.args) >= 2 else next((value.value for value in node.keywords
                        if value.arg == 'kind'), None)
                    self.assertIsNotNone(kind, (str(path), node.lineno))
                    kinds |= result_values(kind, assignments_in(function))
                    sites.append((str(path.relative_to(PRODUCT)), function.name, node.lineno))
        self.assertTrue(sites)
        self.assertEqual(kinds, set(FORMAL_WAIT_RULES))
        for kind, rule in FORMAL_WAIT_RULES.items():
            with self.subTest(kind=kind):
                self.assertIn(rule['resume'], {'environment_changed', 'authority_and_environment', 'recoverable_stop'})
                self.assertTrue(rule['condition'])
                self.assertTrue(rule['resolvers'])
                for reference in rule['resolvers']:
                    module, *attributes = reference.split('.')
                    target = importlib.import_module('do_math.' + module)
                    for name in attributes:
                        target = getattr(target, name)
                    self.assertTrue(callable(target), reference)
        self.assertNotIn('execution_stop_requested', FORMAL_RECOVERABLE_STOPS)
