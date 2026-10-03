"""4-A: admission authority waits declare actual producers and resolvers."""
import ast
import importlib
from pathlib import Path
import unittest

from do_math.wait_rules import AUTHORITY_WAIT_RULES
from support.source_values import assignments_in, result_values

PRODUCT = Path(__file__).resolve().parents[2] / 'do_math'


class AuthorityWaitDeclarationTests(unittest.TestCase):
    def test_real_authority_wait_producers_cover_the_declared_kind(self):
        tree = ast.parse((PRODUCT / 'wait_rules.py').read_text(encoding='utf-8'))
        producer = next(node for node in tree.body if isinstance(node, ast.FunctionDef)
                        and node.name == 'action_authority_wait')
        kinds = set()
        for returned in (node for node in ast.walk(producer) if isinstance(node, ast.Return)):
            record = returned.value.args[0]
            self.assertEqual(returned.value.func.id, 'waiting_action')
            for key, value in zip(record.keys, record.values):
                if isinstance(key, ast.Constant) and key.value == 'kind':
                    kinds |= result_values(value, assignments_in(producer))
        self.assertEqual(kinds, set(AUTHORITY_WAIT_RULES))
        sites = []
        for path in PRODUCT.rglob('*.py'):
            source = ast.parse(path.read_text(encoding='utf-8'))
            sites.extend((path.name, node.lineno) for node in ast.walk(source)
                         if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                         and node.func.id == 'action_authority_wait')
        self.assertTrue(sites)
        for kind, row in AUTHORITY_WAIT_RULES.items():
            with self.subTest(kind=kind):
                self.assertTrue(row['condition'])
                self.assertEqual(row['next_owner'], 'user')
                self.assertTrue(row['resolvers'])
                for reference in row['resolvers']:
                    module, *attributes = reference.split('.')
                    target = importlib.import_module('do_math.' + module)
                    for name in attributes:
                        target = getattr(target, name)
                    self.assertTrue(callable(target), reference)
