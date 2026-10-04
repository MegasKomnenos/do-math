"""3-C current canonical rules and their complete direct call-site population.

Finite behavioral spaces are checked in their existing domain test modules.
This table covers eight original pairs; it does not declare the other three
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
    'B-32': ('task_contracts.py', 'unsupplied_task_inputs', {
        ('core_engine.py', '_apply'), ('planning.py', 'task_ready'),
        ('submission.py', '_payload_issues'), ('submission.py', 'candidate')}),
    'B-33:settings': ('observations.py', 'observation_settings_errors', {
        ('call_engine.py', '_prepare_call'), ('initialization.py', 'activation_requirements'),
        ('initialization_engine.py', '_initialization_control'), ('observations.py', 'tracker_config'),
        ('planning_engine.py', '_retry_observation_configuration'),
        ('submission.py', '_payload_issues'), ('submission.py', 'candidate')}),
    'B-33:binding': ('observations.py', 'tracker_config', {('call_engine.py', '_prepare_call')}),
}


class CanonicalRuleTests(unittest.TestCase):
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
