"""13-C command names and command-specific flags across the operating/role documents.

Fields, policies and reading-boundary obligations have separate closure work;
this test does not substitute flag vocabulary for those requirements.
"""
from pathlib import Path
import unittest
from support.doc_code import (command_issues, declared_policy_names, diagnostic_names, diagnostic_reference_issues, documented_policies, documents,
                              field_schemas, function_reference_issues, parser_options, policy_issues, produced_object_schema, scoped_field_issues, tool_options)

SKILL = Path(__file__).resolve().parents[3]
SCRIPTS = SKILL / 'scripts'


class DocumentCodeTests(unittest.TestCase):
    def test_documented_commands_and_options_exist(self):
        from do_math.cli_contract import build_parser
        options = parser_options(build_parser())
        flags = tool_options(SCRIPTS)
        self.assertGreater(len(options), 0)
        missing = []
        for document in documents(SKILL):
            text = document.read_text(encoding='utf-8')
            missing += [(document.relative_to(SKILL).as_posix(), *issue)
                        for issue in command_issues(text, options, flags)]
        self.assertEqual(sorted(set(missing)), [])

    def test_another_commands_flag_cannot_validate_the_documented_command(self):
        from do_math.cli_contract import build_parser
        options = parser_options(build_parser())
        flags = set().union(*options.values())
        self.assertEqual(command_issues('`do_math.py status --goal-file question.txt`', options, flags),
                         [('command option', 'status', '--goal-file')])
        self.assertEqual(command_issues('`timeline --include-operations`', options, flags), [])
        self.assertEqual(command_issues('```powershell\npython $dmCli run `\n --watch\n```', options, flags), [])
        self.assertEqual(command_issues('`do_math.py run --watch` and `--goal-file` belongs to init.', options, flags), [])

    def test_documented_scoped_fields_belong_to_their_actual_schema(self):
        schemas = field_schemas()
        issues = [(document.relative_to(SKILL).as_posix(), *issue)
                  for document in documents(SKILL)
                  for issue in scoped_field_issues(document.read_text(encoding='utf-8'), schemas)]
        self.assertEqual(issues, [])

    def test_a_field_from_another_family_cannot_validate_a_scoped_name(self):
        schemas = field_schemas()
        self.assertEqual(scoped_field_issues('`config.plan_settle_seconds` and `action.role`', schemas), [])
        self.assertEqual(scoped_field_issues('`config.owner_activity_id`', schemas),
                         [('scoped field', 'config.owner_activity_id')])
        self.assertEqual(scoped_field_issues('`profile.input.max_input_bytes`', schemas), [])
        self.assertEqual(scoped_field_issues('`action.input_basis.impact_review`', schemas), [])
        self.assertEqual(scoped_field_issues('`action.input_basis.nonexistent_review`', schemas),
                         [('scoped field', 'action.input_basis.nonexistent_review')])

    def test_role_input_fields_do_not_borrow_names_from_the_stored_execution(self):
        schemas = field_schemas()
        self.assertEqual(scoped_field_issues(
            '`execution_window.self_check_directory` `execution.execution_window.effective_deadline_at` '
            '`formal_verifier.preview.command` `record_map.read_tool.command` '
            '`submission_contract.limits.checkpoint_bytes` `assessment.current` `runtime.user_pause`', schemas), [])
        self.assertEqual(scoped_field_issues('`execution.execution_window.self_check_directory`', schemas),
                         [('scoped field', 'execution.execution_window.self_check_directory')])
        self.assertEqual(scoped_field_issues('`execution_window.effective_deadline_at`', schemas),
                         [('scoped field', 'execution_window.effective_deadline_at')])
        self.assertEqual(scoped_field_issues('`record_map.read_tool.nonexistent` `runtime.checkpoint_bytes`', schemas),
                         [('scoped field', 'record_map.read_tool.nonexistent'), ('scoped field', 'runtime.checkpoint_bytes')])

    def test_producer_fields_do_not_come_from_nested_scopes_or_unknown_spreads(self):
        def nested_only(context):
            def unrelated():
                context['value'] = {'foreign': 1}
        def returned():
            def unrelated():
                return {'foreign': 1}
            return {'local': {'field': 1}}
        def spread(extra):
            return {'local': 1, **extra}
        with self.assertRaisesRegex(ValueError, 'Review document field producer'):
            produced_object_schema(nested_only, 'context["value"]')
        self.assertEqual(scoped_field_issues('`data.local.field`',
                         {'data': produced_object_schema(returned)}), [])
        self.assertEqual(scoped_field_issues('`data.foreign`',
                         {'data': produced_object_schema(returned)}), [('scoped field', 'data.foreign')])
        with self.assertRaisesRegex(ValueError, 'Unresolved object keys'):
            produced_object_schema(spread)

    def test_explicit_producer_composition_keeps_owners_and_rejects_stale_bindings(self):
        def result(extra):
            return {'own': 1, **extra}
        def alternatives(choice):
            if choice:
                return {'left': 1}
            return {'right': 1}
        schema = produced_object_schema(result, bindings={'extra': {'properties': {'observed': {}}}})
        self.assertEqual(scoped_field_issues('`view.own` `view.observed`', {'view': schema}), [])
        with self.assertRaisesRegex(ValueError, 'Unused producer bindings'):
            produced_object_schema(result, bindings={'extra': {'properties': {}}, 'obsolete': {'properties': {}}})
        schema = produced_object_schema(alternatives, variants=True)
        self.assertEqual(scoped_field_issues('`view.left` `view.right`', {'view': schema}), [])
        with self.assertRaisesRegex(ValueError, 'Review document field producer'):
            produced_object_schema(alternatives)
        schemas = field_schemas()
        self.assertEqual(scoped_field_issues('`status.operating_summary.primary_blocker` '
            '`status.budget` `profile_selection.allowed_profiles` `operational_evidence.activity_continuations`', schemas), [])
        self.assertEqual(scoped_field_issues('`status.allowed_profiles`', schemas), [('scoped field', 'status.allowed_profiles')])

    def test_documented_function_references_resolve_to_callables(self):
        issues = [(document.relative_to(SKILL).as_posix(), *issue)
                  for document in documents(SKILL)
                  for issue in function_reference_issues(document.read_text(encoding='utf-8'))]
        self.assertEqual(issues, [])
        self.assertEqual(function_reference_issues('`os.scandir(...)` `governance.mathematical_goal_basis(...)` '
                         '`knowledge_records.judged_verification(...)`'), [])
        self.assertEqual(function_reference_issues('`governance.missing_function(...)`'),
                         [('function reference', 'governance.missing_function(...)')])
        self.assertEqual(function_reference_issues('`planning.RECORD_FAMILIES(...)`'),
                         [('function reference', 'planning.RECORD_FAMILIES(...)')])
        self.assertEqual(scoped_field_issues('`governance.charter`', field_schemas()), [])
        self.assertEqual(scoped_field_issues('`governance.mathematical_goal_basis`', field_schemas()),
                         [('scoped field', 'governance.mathematical_goal_basis')])

    def test_documented_diagnostic_codes_belong_to_their_actual_owner(self):
        names = diagnostic_names(SCRIPTS)
        issues = [(document.relative_to(SKILL).as_posix(), *issue)
                  for document in documents(SKILL)
                  for issue in diagnostic_reference_issues(document.read_text(encoding='utf-8'), names)]
        self.assertEqual(issues, [])
        self.assertEqual(diagnostic_reference_issues('`contract_check.coverage` `integration.currentness`', names), [])
        self.assertEqual(diagnostic_reference_issues('`integration.py` `integration.preview_bundles(...)`', names), [])
        self.assertEqual(diagnostic_reference_issues('`integration.coverage` `contract_check.currentness`', names),
                         [('diagnostic code', 'contract_check.currentness'), ('diagnostic code', 'integration.coverage')])

    def test_documented_policy_names_have_installed_owners(self):
        names = declared_policy_names(SCRIPTS)
        mentioned = set().union(*(documented_policies(document.read_text(encoding='utf-8'))
                                  for document in documents(SKILL)))
        self.assertTrue({'conversation_loss_policy', 'external_policy'} <= mentioned)
        issues = [(document.relative_to(SKILL).as_posix(), *issue)
                  for document in documents(SKILL)
                  for issue in policy_issues(document.read_text(encoding='utf-8'), names)]
        self.assertEqual(issues, [])

    def test_an_undefined_policy_is_not_accepted_as_an_arbitrary_code_word(self):
        names = declared_policy_names(SCRIPTS)
        self.assertEqual(policy_issues('`conversation_loss_policy` and `external_policy`', names), [])
        self.assertEqual(policy_issues('`undefined_recovery_policy`', names),
                         [('policy name', 'undefined_recovery_policy')])


if __name__ == '__main__':
    unittest.main()
