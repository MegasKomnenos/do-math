"""3-C current canonical rules and their complete direct call-site population.

Finite behavioral spaces are checked in their existing domain test modules.
The table covers ten canonical original pairs plus the separate input-supply
rule. Environment rejection has a distinct producer/consumer check and real
domain differential test. Neither proves every future semantic copy absent.
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
    'C-19': ('governance.py', 'authorize', {
        ('call_engine.py', '_prepare_call'), ('call_engine.py', '_call_stop_requested'),
        ('core_engine.py', '_publish_control_request'), ('core_engine.py', '_validate_bundle_current'),
        ('core_engine.py', '_finish_native_recovery'), ('core_engine.py', '_capture_native_submission'),
        ('core_engine.py', '_cleanup_scope'), ('formal_engine.py', '_resume_formal_waits'),
        ('formal_engine.py', '_formal_steps'), ('formal_engine.py', 'stop'),
        ('governance.py', 'authorize_review_replacement'), ('governance_engine.py', '_resume_action_authority_waits'),
        ('lifecycle_engine.py', '_action_lifecycle_gate'), ('lifecycle_engine.py', '_check_limited_recovery'),
        ('planning.py', 'task_ready')}),
    'B-36': ('lifecycle_engine.py', '_limited_recovery_allowed', {
        ('core_engine.py', '_publish_control_request'), ('core_engine.py', '_validate_bundle_current'),
        ('dispatch_engine.py', '_owner_stopping'), ('lifecycle_engine.py', '_action_lifecycle_gate'),
        ('lifecycle_engine.py', '_execution_stop_requested')}),
    'B-49': ('file_io.py', 'executable_identity', {
        ('cli_execution.py', 'checked_start_paths'), ('codex_adapter.py', 'capability_identity'),
        ('codex_adapter.py', 'observation_key'), ('formal.py', '_project_identity'),
        ('formal.py', 'inspect_toolchain'), ('formal.py', 'verify_lean')}),
    'extra:task-input-supply': ('task_contracts.py', 'unsupplied_task_inputs', {
        ('core_engine.py', '_apply'), ('planning.py', 'task_ready'),
        ('submission.py', '_payload_issues'), ('submission.py', 'candidate')}),
    'B-32': ('context_store.py', 'role_direct_keys', {
        ('context_store.py', 'prepare_role_input'), ('context_store.py', 'fit_context')}),
    'B-33:settings': ('observations.py', 'observation_settings_errors', {
        ('call_engine.py', '_prepare_call'), ('initialization.py', 'activation_requirements'),
        ('initialization_engine.py', '_initialization_control'), ('observations.py', 'tracker_config'),
        ('planning_engine.py', '_retry_observation_configuration'),
        ('submission.py', '_payload_issues'), ('submission.py', 'candidate')}),
    'B-33:binding': ('observations.py', 'tracker_config', {('call_engine.py', '_prepare_call')}),
    'C-13': ('context_store.py', '_input_overflow', {
        ('context_store.py', 'prepare_role_input'), ('context_store.py', 'fit_context')}),
    'A-47': ('input_recovery.py', 'input_overflow_disposition', {
        ('context_store.py', 'prepare_role_input'), ('call_engine.py', '_prepare_call')}),
}


class CanonicalRuleTests(unittest.TestCase):
    def test_formal_identity_rejections_preserve_the_kind_the_actual_owner_routes(self):
        import inspect
        from textwrap import dedent
        from do_math import formal
        from do_math.formal_engine import FormalEngineMixin
        producer = ast.parse(inspect.getsource(formal.verify_lean))
        consumer = ast.parse(dedent(inspect.getsource(FormalEngineMixin._formal_steps)))
        kinds = [value.value for node in ast.walk(producer) if isinstance(node, ast.Dict)
                 for key, value in zip(node.keys, node.values)
                 if isinstance(key, ast.Constant) and key.value == 'error_kind' and isinstance(value, ast.Constant)]
        self.assertGreaterEqual(len(kinds), 2, 'both known identity rejection exits need their environment kind')
        self.assertEqual(set(kinds), {'trust_environment'})
        routes = [node for node in ast.walk(consumer) if isinstance(node, ast.Compare)
                  and isinstance(node.left, ast.Call) and isinstance(node.left.func, ast.Attribute)
                  and node.left.func.attr == 'get' and node.left.args
                  and isinstance(node.left.args[0], ast.Constant) and node.left.args[0].value == 'error_kind']
        self.assertTrue(any(isinstance(value, ast.Constant) and value.value in kinds
                            for node in routes for value in node.comparators))

    def test_every_declared_rule_has_one_definition_and_all_direct_consumers_use_it(self):
        trees = {p.name: ast.parse(p.read_text(encoding='utf-8'))
                 for p in (SCRIPTS / 'do_math').glob('*.py')}
        nodes = {path: tuple(ast.walk(tree)) for path, tree in trees.items()}
        functions = {path: [node for node in items if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))]
                     for path, items in nodes.items()}
        sites = {path: [(function.name, call) for function in items for call in ast.walk(function)
                        if isinstance(call, ast.Call)] for path, items in functions.items()}
        for rule, (owner, name, expected) in RULES.items():
            with self.subTest(rule=rule):
                definitions = [(path, node.name) for path, items in functions.items()
                               for node in items if node.name == name]
                self.assertEqual(definitions, [(owner, name)])
                calls = set()
                for path, tree in trees.items():
                    bindings = {}
                    for node in nodes[path]:
                        if isinstance(node, ast.ImportFrom):
                            module = (node.module or '').split('.')[-1]
                            for imported in node.names:
                                if imported.name == name and module == owner[:-3]:
                                    bindings[imported.asname or name] = name
                    for function, call in sites[path]:
                        if isinstance(call.func, ast.Name) and call.func.id == name:
                            self.assertTrue(path == owner or call.func.id in bindings,
                                            'shared rule name is not imported from its owner')
                            calls.add((path, function))
                        elif isinstance(call.func, ast.Attribute) and call.func.attr == name:
                            self.assertIsInstance(call.func.value, ast.Name)
                            if name.startswith('_'):
                                self.assertEqual(call.func.value.id, 'self', 'shared owner predicate uses its inherited method')
                            else:
                                self.assertEqual(call.func.value.id, owner[:-3])
                            calls.add((path, function))
                        elif isinstance(call.func, ast.Name) and call.func.id in bindings:
                            calls.add((path, function))
                self.assertEqual(calls, expected, 'new or missing direct consumers require declaration review')
