"""4-A: current action-wait creation and kind changes cover one declaration."""
import ast
import importlib
from pathlib import Path
import unittest

from do_math.wait_rules import WAITING_ACTION_RULES, REVIEW_WAIT_RULES
from support.source_values import assignments_in, result_values

PRODUCT = Path(__file__).resolve().parents[2] / 'do_math'


def container_expression(node, aliases):
    if isinstance(node, ast.Name):
        return node.id in aliases
    if isinstance(node, ast.Subscript):
        return isinstance(node.slice, ast.Constant) and node.slice.value == 'waiting_actions'
    return (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
            and node.func.attr in {'get', 'setdefault'} and node.args
            and isinstance(node.args[0], ast.Constant) and node.args[0].value == 'waiting_actions')


class ActionWaitDeclarationTests(unittest.TestCase):
    def test_activity_wait_producers_and_storage_use_one_typed_kind_declaration(self):
        from do_math.wait_rules import ACTIVITY_WAIT_RULES, ACTIVITY_EXTRA_WAIT_RULES, PREPARATION_WAIT_RULES
        from do_math.record_schemas import RECORDS
        observed = set()
        sites = set()
        for path in sorted(PRODUCT.glob('*.py')):
            tree = ast.parse(path.read_text(encoding='utf-8'))
            aliases = {item.asname or item.name for node in ast.walk(tree)
                if isinstance(node, ast.ImportFrom) and (node.module or '').endswith('activities')
                for item in node.names if item.name == 'wait_for'}
            for function in (node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)):
                assignments = assignments_in(function)
                for call in (node for node in ast.walk(function) if isinstance(node, ast.Call)):
                    direct = isinstance(call.func, ast.Name) and (call.func.id in aliases or
                              path.name == 'activities.py' and call.func.id == 'wait_for')
                    qualified = (isinstance(call.func, ast.Attribute) and call.func.attr == 'wait_for'
                        and isinstance(call.func.value, ast.Name) and call.func.value.id == 'activities')
                    if not (direct or qualified):
                        continue
                    kinds = [kw.value for kw in call.keywords if kw.arg == 'kind']
                    self.assertEqual(len(kinds), 1, (path.name, function.name, 'untyped activity wait'))
                    value = kinds[0]
                    site = (path.name, function.name)
                    sites.add(site)
                    if site == ('activities.py', 'continue_activity'):
                        self.assertEqual(ast.unparse(value), 'wait_kind')
                        continue  # The public continuation API uses the checked constructor's enum.
                    expression = ast.unparse(value)
                    if expression in {"wait['kind']", "waiting['kind']"}:
                        observed.update(WAITING_ACTION_RULES)
                    elif expression == 'kind' and site == ('call_engine.py', '_prepare_call'):
                        observed.update(PREPARATION_WAIT_RULES)
                    elif expression == 'wait_kind' and site == ('core_engine.py', '_register_execution'):
                        observed.update(REVIEW_WAIT_RULES)
                    else:
                        observed.update(result_values(value, assignments))
        self.assertEqual(sites, {
            ('activities.py', 'continue_activity'), ('call_engine.py', '_prepare_call'),
            ('context_store.py', 'defer_input_overflow'), ('core_engine.py', '_register_execution'),
            ('core_engine.py', '_settle_activity'), ('external_engine.py', '_external_execution_record'),
            ('formal_engine.py', '_trust_activation_steps'), ('formal_engine.py', '_trust_check_steps'),
            ('formal_engine.py', '_formal_steps'), ('provider_engine.py', '_requeue_provider_action'),
            ('repair_execution.py', 'record_recovery_attempt'), ('review_engine.py', '_settle_review_resource_dispositions')})
        self.assertEqual(observed, set(ACTIVITY_WAIT_RULES) - {'required_input', 'user_resume'})
        self.assertFalse(set(WAITING_ACTION_RULES) & set(ACTIVITY_EXTRA_WAIT_RULES))
        schema = RECORDS['activities']['properties']['waiting']
        self.assertIn('kind', schema['required'])
        self.assertEqual(set(schema['properties']['kind']['enum']), set(ACTIVITY_WAIT_RULES))
        for rule in ACTIVITY_WAIT_RULES.values():
            self.assertTrue(rule['condition'])
            self.assertTrue(rule['resolvers'])
            for reference in rule['resolvers']:
                module, *attributes = reference.split('.')
                target = importlib.import_module('do_math.' + module)
                for name in attributes:
                    target = getattr(target, name)
                self.assertTrue(callable(target), reference)

    def test_every_current_wait_creation_uses_the_declaration_and_real_resolvers(self):
        parsed = [(path, ast.parse(path.read_text(encoding='utf-8'))) for path in sorted(PRODUCT.rglob('*.py'))]
        functions = {node.name: node for path, tree in parsed if path.name == 'wait_rules.py'
                     for node in tree.body if isinstance(node, ast.FunctionDef)}
        formal_kinds = set()
        for path, tree in parsed:
            for node in ast.walk(tree):
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == 'formal_wait':
                    formal_kinds |= result_values(node.args[1], {})
        kinds, sites, bypasses = set(), [], []
        for path, tree in parsed:
            for function in (node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)):
                assignments = assignments_in(function)
                aliases = {name for name, values in assignments.items()
                           if any(container_expression(value, set()) for value in values)}
                for node in ast.walk(function):
                    if isinstance(node, ast.Assign):
                        for target in node.targets:
                            if (isinstance(target, ast.Subscript) and container_expression(target.value, aliases)
                                    and isinstance(node.value, ast.Dict)):
                                bypasses.append((path.name, function.name, node.lineno))
                    if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Name):
                        continue
                    name = node.func.id
                    if name == 'update_waiting_action':
                        expression = next((item.value for item in node.keywords if item.arg == 'kind'), None)
                        if expression is None:
                            continue
                    elif name == 'waiting_action':
                        if function.name == 'update_waiting_action' and path.name == 'wait_rules.py':
                            continue
                        self.assertIsInstance(node.args[0], ast.Dict, (path.name, node.lineno))
                        expression = next((value for key, value in zip(node.args[0].keys, node.args[0].values)
                                           if isinstance(key, ast.Constant) and key.value == 'kind'), None)
                        if expression is None:
                            continue  # Copying a previously constructed complete record, without changing its kind.
                    else:
                        continue
                    if path.name == 'wait_rules.py' and function.name == 'formal_wait':
                        values = formal_kinds
                    elif ((isinstance(expression, ast.Call) and isinstance(expression.func, ast.Name)
                           and expression.func.id == 'review_wait_kind')
                          or function.name == '_register_execution' and isinstance(expression, ast.Name)):
                        if isinstance(expression, ast.Name):
                            self.assertTrue(assignments[expression.id])
                            for value in assignments[expression.id]:
                                self.assertIsInstance(value, ast.Call)
                                self.assertEqual(value.func.id, 'review_wait_kind')
                        values = set(REVIEW_WAIT_RULES)
                    else:
                        values = result_values(expression, assignments, functions)
                    kinds |= values
                    sites.append((path.name, function.name, node.lineno))
        self.assertEqual(bypasses, [], 'wait creation bypasses the canonical constructor')
        self.assertTrue(sites)
        self.assertEqual(kinds, set(WAITING_ACTION_RULES))
        for kind, rule in WAITING_ACTION_RULES.items():
            with self.subTest(kind=kind):
                self.assertTrue(rule['next_owner'])
                self.assertTrue(rule['condition'])
                self.assertTrue(rule['resolvers'])
                for reference in rule['resolvers']:
                    module, *attributes = reference.split('.')
                    target = importlib.import_module('do_math.' + module)
                    for name in attributes:
                        target = getattr(target, name)
                    self.assertTrue(callable(target), reference)
