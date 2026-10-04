"""13-C command names and command-specific flags across the operating/role documents.

Fields, policies and reading-boundary obligations have separate closure work;
this test does not substitute flag vocabulary for those requirements.
"""
from pathlib import Path
import unittest
from support.doc_code import (command_issues, consumed_object_schema, declared_policy_names, diagnostic_names, diagnostic_reference_issues, documented_policies, documents,
                              field_bindings, field_schemas, function_reference_issues, parser_options, policy_issues, produced_object_schema, scoped_field_issues, tool_options, unowned_field_references, written_object_schema)

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

    def test_document_variables_have_line_local_owners_without_a_union_of_families(self):
        schemas = field_schemas()
        self.assertEqual(scoped_field_issues('`record.content.academic_requirements` <!-- do-math fields: record=governance_record -->', schemas), [])
        self.assertEqual(scoped_field_issues('`record.explanation` <!-- do-math fields: record=candidate_record -->', schemas), [])
        self.assertEqual(scoped_field_issues('`record.explanation` <!-- do-math fields: record=governance_record -->', schemas),
                         [('scoped field', 'record.explanation')])
        self.assertEqual(scoped_field_issues('`record.content` <!-- do-math fields: record=candidate_record -->', schemas),
                         [('scoped field', 'record.content')])
        self.assertEqual(scoped_field_issues('`record.id` <!-- do-math fields: record=missing_owner -->', schemas),
                         [('field binding', 'record=missing_owner')])
        text = '`task.content` <!-- do-math fields: task=governance_record -->'
        self.assertEqual(scoped_field_issues(text, schemas),
                         [('field binding', 'task=governance_record'), ('scoped field', 'task.content')])
        first, _ = field_bindings('`record.id` <!-- do-math fields: record=governance_record -->', schemas)
        second, _ = field_bindings('`record.id`', schemas)
        self.assertIn('record', first)
        self.assertNotIn('record', second)
        self.assertEqual(scoped_field_issues('`recrod.id` <!-- do-math fields: record=governance_record -->', schemas),
                         [('unused field binding', 'record')])
        self.assertEqual(scoped_field_issues('`activation.observation_errors` `disposition.kind` '
            '`observation.rule_bindings` `role_tiers.recovery` `repair.previous_output` '
            '`checkpoint_source.local_path` `result_source.local_path` `rejected_response.local_path`', schemas), [])

    def test_cli_result_branches_and_incremental_manifest_fields_remain_separate(self):
        def producer(command):
            result = {}
            if command == 'first':
                result['only_first'] = 1
                return {'first': 1}, 0
            if command == 'second':
                result['only_second'] = 2
                return {'second': 2}, 0
        schema = written_object_schema(producer, 'result', branch="command == 'first'")
        self.assertEqual(set(schema['properties']), {'only_first'})
        schema = produced_object_schema(producer, branch="command == 'second'", return_item=0)
        self.assertEqual(set(schema['properties']), {'second'})
        with self.assertRaisesRegex(ValueError, 'Review producer branch'):
            written_object_schema(producer, 'result', branch="command == 'missing'")
        schemas = field_schemas()
        self.assertEqual(scoped_field_issues('`input_manifest.prompt.sha256` `prompt.artifact_ref` '
            '`init_result.instance_id` `selection_result.selection.profile_ref` `query_record.family`', schemas), [])
        self.assertEqual(scoped_field_issues('`init_result.selection`', schemas), [('scoped field', 'init_result.selection')])

    def test_optional_reads_and_same_named_checks_keep_their_actual_owners(self):
        def consumer(payload, other, field):
            payload['written_only'] = 1
            def nested():
                return payload.get('nested_only')
            return payload.get('kind'), other.get('foreign'), payload.get(field)
        schema = consumed_object_schema(consumer, 'payload')
        self.assertEqual(set(schema['properties']), {'kind'})
        with self.assertRaisesRegex(ValueError, 'No fixed read fields'):
            consumed_object_schema(consumer, 'missing')
        schemas = field_schemas()
        self.assertEqual(scoped_field_issues('`check.passed` <!-- do-math fields: check=submission_check -->', schemas), [])
        self.assertEqual(scoped_field_issues('`check.sha256` <!-- do-math fields: check=import_check -->', schemas), [])
        self.assertEqual(scoped_field_issues('`check.passed` <!-- do-math fields: check=import_check -->', schemas),
                         [('scoped field', 'check.passed')])
        self.assertEqual(scoped_field_issues('`check.sha256` <!-- do-math fields: check=submission_check -->', schemas),
                         [('scoped field', 'check.sha256')])
        self.assertEqual(scoped_field_issues('`change.value` `review_research.question` `source_ref.path` '
            '`toolchain.project.search_paths` `environment_check.changed_files` `role_review.proposal`', schemas), [])
        self.assertEqual(scoped_field_issues('`change.nonexistent` `source_ref.passed`', schemas),
                         [('scoped field', 'change.nonexistent'), ('scoped field', 'source_ref.passed')])
        self.assertEqual(scoped_field_issues('`payload.deadline_offset_ms` <!-- do-math fields: payload=import_payload -->', schemas),
                         [('scoped field', 'payload.deadline_offset_ms')])

    def test_all_simple_dotted_document_fields_have_an_owner(self):
        schemas = field_schemas()
        pending = [(document.relative_to(SKILL).as_posix(), token)
                   for document in documents(SKILL)
                   for token in unowned_field_references(document.read_text(encoding='utf-8'), schemas)]
        self.assertEqual(pending, [])
        self.assertEqual(unowned_field_references('`recrod.id` `new_space.value`', schemas),
                         ['new_space.value', 'recrod.id'])
        self.assertEqual(unowned_field_references('`record.id` <!-- do-math fields: record=governance_record -->', schemas), [])
        self.assertEqual(unowned_field_references('`pythonw.exe` `integration.currentness` `os.scandir(...)`', schemas), [])

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
