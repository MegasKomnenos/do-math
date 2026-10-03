"""4-A: real preparation/admission outcomes have one declared review wait kind."""
import ast
import importlib
from pathlib import Path
import unittest

from do_math import wait_rules
from support.source_values import result_values

PRODUCT = Path(__file__).resolve().parents[2] / 'do_math'


def returned_dispositions(function):
    values = set()
    for node in ast.walk(function):
        if not isinstance(node, ast.Return) or not isinstance(node.value, ast.Dict):
            continue
        for key, value in zip(node.value.keys, node.value.values):
            if isinstance(key, ast.Constant) and key.value == 'disposition':
                values |= result_values(value, {})
    return values


class ReviewWaitDeclarationTests(unittest.TestCase):
    def test_current_review_preparation_and_admission_cover_the_wait_declaration(self):
        review = ast.parse((PRODUCT / 'review_engine.py').read_text(encoding='utf-8'))
        functions = {node.name: node for node in ast.walk(review) if isinstance(node, ast.FunctionDef)}
        prepared = returned_dispositions(functions['_prepare_review_context']) - {'ready'}
        self.assertEqual(prepared, {row['prepared_disposition'] for row in wait_rules.REVIEW_WAIT_RULES.values()})
        admission = returned_dispositions(functions['_admit_review_execution'])
        core = ast.parse((PRODUCT / 'core_engine.py').read_text(encoding='utf-8'))
        register = next(node for node in ast.walk(core) if isinstance(node, ast.FunctionDef) and node.name == '_register_execution')
        handled = set()
        for node in ast.walk(register):
            if isinstance(node, ast.Compare) and ast.unparse(node.left) == "admission['disposition']":
                for comparator in node.comparators:
                    if isinstance(comparator, ast.Set):
                        for value in comparator.elts:
                            handled |= result_values(value, {})
        held = {value.value for node in ast.walk(register) if isinstance(node, ast.Dict)
                for key, value in zip(node.keys, node.values) if isinstance(key, ast.Constant)
                and key.value == 'disposition' and isinstance(value, ast.Constant)}
        self.assertEqual((admission - handled) | held,
                         {row['admission_disposition'] for row in wait_rules.REVIEW_WAIT_RULES.values()})
        for kind, row in wait_rules.REVIEW_WAIT_RULES.items():
            with self.subTest(kind=kind):
                self.assertEqual(wait_rules.review_wait_kind(row['prepared_disposition']), kind)
                self.assertEqual(wait_rules.review_wait_kind(row['admission_disposition']), kind)
                self.assertEqual(kind in wait_rules.REVIEW_ADMISSION_WAITS, row['block_admission'])
                self.assertEqual(kind in wait_rules.REVIEW_RESTORATION_WAITS, row['restore_control'])
                self.assertTrue(row['condition'])
                self.assertTrue(row['resolvers'])
                for reference in row['resolvers']:
                    module, *attributes = reference.split('.')
                    target = importlib.import_module('do_math.' + module)
                    for name in attributes:
                        target = getattr(target, name)
                    self.assertTrue(callable(target), reference)
