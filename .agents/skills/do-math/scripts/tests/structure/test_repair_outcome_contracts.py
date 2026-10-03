"""4-C outcome declarations cover their real finite producers, not test fixtures."""
import ast
from pathlib import Path
import unittest

from do_math.integration import SUBMISSION_OUTCOMES
from do_math.repair_execution import RECOVERY_OUTCOMES
from support.source_values import assignments_in, result_values

PRODUCT = Path(__file__).resolve().parents[2] / 'do_math'


class RepairOutcomeDeclarationTests(unittest.TestCase):
    def test_recovery_results_are_all_declared_and_have_settlement_contracts(self):
        repair = ast.parse((PRODUCT / 'repair_execution.py').read_text(encoding='utf-8'))
        runner = next(node for node in repair.body if isinstance(node, ast.FunctionDef) and node.name == 'runner_outcome')
        produced, sites = set(), []
        for path in sorted(PRODUCT.rglob('*.py')):
            tree = ast.parse(path.read_text(encoding='utf-8'))
            for function in (node for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))):
                for node in ast.walk(function):
                    if not isinstance(node, ast.Call):
                        continue
                    name = node.func.id if isinstance(node.func, ast.Name) else getattr(node.func, 'attr', None)
                    if name != 'record_recovery_attempt':
                        continue
                    outcome = next((field.value for field in node.keywords if field.arg == 'outcome'), None)
                    self.assertIsNotNone(outcome, (str(path), node.lineno))
                    produced |= result_values(outcome, assignments_in(function), {'runner_outcome': runner})
                    sites.append((str(path.relative_to(PRODUCT)), function.name, node.lineno))
        self.assertTrue(sites)
        self.assertEqual(produced, set(RECOVERY_OUTCOMES))
        for outcome, row in RECOVERY_OUTCOMES.items():
            with self.subTest(outcome=outcome):
                self.assertEqual(set(row), {'counter', 'terminal', 'finish', 'report'})
                self.assertIn(row['counter'], {'attempt', 'exclude', 'report', 'unconfirmed'})
                self.assertIn(row['report'], {'required', 'absent', 'optional'})
                self.assertIs(type(row['terminal']), bool)
                self.assertIs(type(row['finish']), bool)
                self.assertFalse(row['finish'] and not row['terminal'])

    def test_submission_results_are_all_declared_and_have_counter_contracts(self):
        tree = ast.parse((PRODUCT / 'integration.py').read_text(encoding='utf-8'))
        function = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == 'submission_outcome')
        produced = set()
        for node in ast.walk(function):
            if isinstance(node, ast.Return):
                produced |= result_values(node.value, assignments_in(function))
        self.assertEqual(produced, set(SUBMISSION_OUTCOMES))
        for outcome, row in SUBMISSION_OUTCOMES.items():
            with self.subTest(outcome=outcome):
                self.assertEqual(set(row), {'output_repair', 'next_owner'})
                self.assertIs(type(row['output_repair']), bool)
                self.assertIn(row['next_owner'], {None, 'engine', 'impact_review', 'refresh_decision', 'producer'})
