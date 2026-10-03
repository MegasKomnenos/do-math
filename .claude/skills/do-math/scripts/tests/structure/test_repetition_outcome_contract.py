"""The result declaration covers every actual repetition producer both ways."""
import ast
from pathlib import Path
import unittest

from do_math.task_contracts import REPETITION_OUTCOMES
from support.source_values import assignments_in, result_values

PRODUCT = Path(__file__).resolve().parents[2] / 'do_math'


class RepetitionOutcomeDeclarationTests(unittest.TestCase):
    def test_every_produced_result_has_exactly_one_declared_counting_rule(self):
        produced, sites = set(), []
        for path in sorted(PRODUCT.rglob('*.py')):
            tree = ast.parse(path.read_text(encoding='utf-8'))
            for function in (node for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))):
                assignments = assignments_in(function)
                for node in ast.walk(function):
                    if not isinstance(node, ast.Call):
                        continue
                    name = node.func.id if isinstance(node.func, ast.Name) else getattr(node.func, 'attr', None)
                    if name != 'record_repetition':
                        continue
                    outcome = next((field.value for field in node.keywords if field.arg == 'outcome'), None)
                    self.assertIsNotNone(outcome, (str(path), node.lineno))
                    produced |= result_values(outcome, assignments)
                    sites.append((str(path.relative_to(PRODUCT)), function.name, node.lineno))
        self.assertTrue(sites)
        self.assertEqual(produced, set(REPETITION_OUTCOMES))
        for outcome, row in REPETITION_OUTCOMES.items():
            with self.subTest(outcome=outcome):
                self.assertEqual(set(row), {'counter', 'diagnose'})
                self.assertIn(row['counter'], {'reset', 'retain', 'increment'})
                self.assertIs(type(row['diagnose']), bool)
