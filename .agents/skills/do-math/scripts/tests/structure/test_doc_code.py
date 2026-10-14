"""13-C commands, policies, dotted fields, functions and constants in role documents.

Unqualified prose field names and reading-boundary obligations still require
separate closure; dotted references are checked against their actual owners.
"""
from pathlib import Path
import re
import unittest
from support.doc_code import (command_issues, constant_reference_issues, consumed_object_schema, declared_policy_names, diagnostic_names, diagnostic_reference_issues, documented_policies, documents,
                              field_bindings, field_schemas, function_reference_issues, parser_options, policy_issues, produced_object_schema, scoped_field_issues, tool_options, unowned_field_references, written_object_schema)

SKILL = Path(__file__).resolve().parents[3]
SCRIPTS = SKILL / 'scripts'


class DocumentCodeTests(unittest.TestCase):
    def test_governance_fields_require_their_actual_boundary_owner(self):
        schemas = field_schemas()
        from support.doc_code import GOVERNANCE_BOUNDARIES, governance_field_issues
        for owner, text in (
                ('import_payload', '`payload.kind` <!-- do-math fields: payload=import_payload -->'),
                ('import_check', '`check.sha256` <!-- do-math fields: check=import_check -->'),
                ('governance', '`governance.charter`'),
                ('academic_validation', '`academic_validation.status`')):
            with self.subTest(text=text), self.assertRaisesRegex(ValueError, 'actual governance value'):
                scoped_field_issues(text, schemas)
            with self.assertRaisesRegex(ValueError, 'actual governance value'):
                scoped_field_issues(text, schemas, defer_governance=set(GOVERNANCE_BOUNDARIES) - {owner})
            self.assertEqual(scoped_field_issues(text, schemas, defer_governance=(owner,)), [])
            self.assertEqual(governance_field_issues(text, owner, None),
                             [('actual field', text.split('`')[1])])
        with self.assertRaisesRegex(ValueError, 'Unknown deferred governance owners'):
            scoped_field_issues('', schemas, defer_governance=('import_checks',))
        with self.assertRaisesRegex(ValueError, 'status fields require the actual'):
            scoped_field_issues('`status.budget`', schemas, defer_governance=GOVERNANCE_BOUNDARIES)
        self.assertEqual(governance_field_issues('`check.passed` <!-- do-math fields: check=import_check -->',
            'import_check', {'sha256': 'seal'}), [('actual field', 'check.passed')])
        self.assertEqual(governance_field_issues('`payload.kind` <!-- do-math fields: payload=import_payload -->',
            'import_payload', {}), [])
        self.assertEqual(governance_field_issues('`payload.deadline_offset_ms` <!-- do-math fields: payload=import_payload -->',
            'import_payload', {}), [('actual field', 'payload.deadline_offset_ms')])

    def test_deferred_governance_has_the_assigned_actual_document_check(self):
        import ast
        from support.doc_code import GOVERNANCE_BOUNDARIES
        owners = {
            'import_payload': ('unit/test_governance_imports.py', 'ImportSealTests',
                'test_import_unit_target_matches_each_governance_consumer'),
            'import_check': ('unit/test_governance_imports.py', 'ImportSealTests',
                'test_documented_import_check_is_bound_to_its_exact_bundle'),
            'governance': ('unit/test_governance_records.py', 'DomainGovernanceTests',
                'test_initialized_charter_is_single_authority_and_binds_approved_original'),
            'academic_validation': ('unit/test_academic_requirements.py', 'Tests',
                'test_documented_status_keeps_each_current_query_branch')}
        def verify(mapping):
            self.assertEqual(set(mapping), set(GOVERNANCE_BOUNDARIES))
            for owner, (path, class_name, method) in mapping.items():
                tree = ast.parse((SCRIPTS / 'tests' / path).read_text(encoding='utf-8'))
                cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == class_name)
                methods = [n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == method]
                self.assertEqual(len(methods), 1)
                self.assertTrue(any(isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
                    and n.func.id == 'assert_governance_documents' and any(k.arg == 'owner'
                    and isinstance(k.value, ast.Constant) and k.value.value == owner for k in n.keywords)
                    for n in ast.walk(methods[0])))
        verify(owners)
        for fault in ('missing_owner', 'wrong_owner', 'missing_method', 'wrong_method'):
            changed = dict(owners)
            if fault == 'missing_owner':
                del changed['import_check']
            elif fault == 'wrong_owner':
                changed['import_checks'] = changed.pop('import_check')
            elif fault == 'missing_method':
                changed['import_check'] = (*changed['import_check'][:2], 'missing')
            else:
                changed['import_check'] = (*changed['import_check'][:2], 'test_import_reapplication_is_idempotent')
            with self.subTest(fault=fault), self.assertRaises(AssertionError):
                verify(changed)

    def test_delivery_fields_require_their_actual_return_owner(self):
        schemas = field_schemas()
        from support.doc_code import DELIVERY_INPUT_BOUNDARIES, delivery_field_issues
        for field in ('submission_check.passed', 'repair.previous_output'):
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, 'actual delivery input'):
                scoped_field_issues('`' + field + '`', schemas)
            owner = field.split('.')[0]
            with self.assertRaisesRegex(ValueError, 'actual delivery input'):
                scoped_field_issues('`' + field + '`', schemas,
                    defer_delivery_inputs=set(DELIVERY_INPUT_BOUNDARIES) - {owner})
            self.assertEqual(scoped_field_issues('`' + field + '`', schemas,
                defer_delivery_inputs=(owner,)), [])
            self.assertEqual(delivery_field_issues('`' + field + '`', owner, {}), [('actual field', field)])
        with self.assertRaisesRegex(ValueError, 'Unknown deferred delivery input owners'):
            scoped_field_issues('', schemas, defer_delivery_inputs=('repairs',))
        with self.assertRaisesRegex(ValueError, 'status fields require the actual'):
            scoped_field_issues('`status.budget`', schemas, defer_delivery_inputs=DELIVERY_INPUT_BOUNDARIES)
        self.assertEqual(delivery_field_issues('`check.sha256` <!-- do-math fields: check=submission_check -->',
            'submission_check', {'passed': True}), [('actual field', 'check.sha256')])

    def test_deferred_delivery_has_the_assigned_actual_document_check(self):
        import ast
        from support.doc_code import DELIVERY_INPUT_BOUNDARIES
        owners = {
            'submission_check': ('unit/test_submission_checks.py', 'CheckHistoryTests',
                'test_documented_pass_is_bound_to_the_actual_candidate_and_check'),
            'repair': ('sim/test_repair_routing.py', 'SubmissionReturnTests',
                'test_repeated_submission_return_stops_producer_and_opens_one_diagnosis')}
        def verify(mapping):
            self.assertEqual(set(mapping), set(DELIVERY_INPUT_BOUNDARIES))
            for owner, (path, class_name, name) in mapping.items():
                tree = ast.parse((SCRIPTS / 'tests' / path).read_text(encoding='utf-8'))
                cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == class_name)
                methods = [n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == name]
                self.assertEqual(len(methods), 1)
                self.assertTrue(any(isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
                    and n.func.id == 'assert_delivery_documents' and any(k.arg == 'owner'
                    and isinstance(k.value, ast.Constant) and k.value.value == owner for k in n.keywords)
                    for n in ast.walk(methods[0])))
        verify(owners)
        for fault in ('missing_owner', 'wrong_owner', 'missing_method', 'wrong_method'):
            changed = dict(owners)
            if fault == 'missing_owner':
                del changed['repair']
            elif fault == 'wrong_owner':
                changed['repairs'] = changed.pop('repair')
            elif fault == 'missing_method':
                changed['repair'] = (*changed['repair'][:2], 'missing')
            else:
                changed['repair'] = (*changed['repair'][:2], 'test_a_rejected_submission_travels_with_the_repair')
            with self.subTest(fault=fault), self.assertRaises(AssertionError):
                verify(changed)

    def test_review_fields_require_their_actual_input_owner(self):
        schemas = field_schemas()
        from support.doc_code import REVIEW_INPUT_BOUNDARIES, review_field_issues
        for field in ('role_review.proposal', 'pending_findings[].ref',
                      'review_research.question', 'review_sources[].ref'):
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, 'actual review input'):
                scoped_field_issues('`' + field + '`', schemas)
            owner = field.split('.')[0]
            if '[' in owner:
                owner = owner.split('[')[0]
            with self.assertRaisesRegex(ValueError, 'actual review input'):
                scoped_field_issues('`' + field + '`', schemas,
                                    defer_review_inputs=set(REVIEW_INPUT_BOUNDARIES) - {owner})
            self.assertEqual(scoped_field_issues('`' + field + '`', schemas,
                                                defer_review_inputs=(owner,)), [])
        with self.assertRaisesRegex(ValueError, 'Unknown deferred review input owners'):
            scoped_field_issues('', schemas, defer_review_inputs=('review_source',))
        for text in ('`status.budget`', '`research_sources[].local_path`', '`preview.command`'):
            with self.assertRaisesRegex(ValueError, 'fields require the actual'):
                scoped_field_issues(text, schemas, defer_review_inputs=REVIEW_INPUT_BOUNDARIES)
        self.assertEqual(review_field_issues('`pending_findings[].ref`', 'pending_findings', []),
                         [('actual field', 'pending_findings[].ref')])
        self.assertEqual(review_field_issues('`sources[].ref` <!-- do-math fields: sources=review_sources -->',
                         'review_sources', [{'ref': 'exact'}]), [])
        self.assertEqual(review_field_issues('`sources[].ref`', 'review_sources', [{'ref': 'exact'}]), [])

    def test_deferred_reviews_have_their_actual_document_check(self):
        import ast
        from support.doc_code import REVIEW_INPUT_BOUNDARIES
        owners = {'role_review': ('sim/test_submission_review_inputs.py', 'ReviewInputTests', 'test_review_stage_documents_reach_the_final_seat_input'),
                  'pending_findings': ('sim/test_submission_review_inputs.py', 'ReviewInputTests', 'test_review_stage_documents_reach_the_final_seat_input'),
                  'review_research': ('unit/test_review_research_owner_contract.py', 'ResearchOwnerContractTests', 'test_fixed_question_context_keeps_original_bytes_after_unrelated_publication'),
                  'review_sources': ('unit/test_review_research_owner_contract.py', 'ResearchOwnerContractTests', 'test_fixed_question_context_keeps_original_bytes_after_unrelated_publication')}
        def verify(mapping):
            self.assertEqual(set(mapping), set(REVIEW_INPUT_BOUNDARIES))
            for owner, (path, class_name, name) in mapping.items():
                tree = ast.parse((SCRIPTS / 'tests' / path).read_text(encoding='utf-8'))
                cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == class_name)
                methods = [n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == name]
                self.assertEqual(len(methods), 1)
                self.assertTrue(any(isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
                    and n.func.id == 'assert_review_documents' and any(k.arg == 'owner'
                    and isinstance(k.value, ast.Constant) and k.value.value == owner for k in n.keywords)
                    for n in ast.walk(methods[0])), owner + ' needs its actual document check')
        verify(owners)
        for fault in ('missing_owner', 'wrong_owner', 'missing_method', 'wrong_method'):
            changed = dict(owners)
            if fault == 'missing_owner':
                del changed['review_sources']
            elif fault == 'wrong_owner':
                changed['review_source'] = changed.pop('review_sources')
            elif fault == 'missing_method':
                changed['review_sources'] = (*changed['review_sources'][:2], 'missing')
            else:
                changed['review_sources'] = (*changed['review_sources'][:2], 'test_research_schema_pins_question_and_digest')
            with self.subTest(fault=fault), self.assertRaises(AssertionError):
                verify(changed)

    def test_tool_fields_require_their_actual_installed_input(self):
        schemas = field_schemas()
        fields = ('execution_window.self_check_directory', 'scholarly.configured',
                  'formal_verifier.mechanism', 'preview.command',
                  'record_map.read_tool.command', 'submission_contract.limits.checkpoint_bytes')
        for field in fields:
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, 'actual tool input'):
                scoped_field_issues('`' + field + '`', schemas)
        from support.doc_code import TOOL_INPUT_BOUNDARIES
        for field, owner in zip(fields, TOOL_INPUT_BOUNDARIES):
            with self.subTest(owner=owner):
                with self.assertRaisesRegex(ValueError, 'actual tool input'):
                    scoped_field_issues('`' + field + '`', schemas,
                        defer_tool_inputs=set(TOOL_INPUT_BOUNDARIES) - {owner}, defer_review_inputs=('role_review', 'pending_findings', 'review_research', 'review_sources'), defer_delivery_inputs=('submission_check', 'repair'), defer_governance=('import_payload', 'import_check', 'governance', 'academic_validation'))
                self.assertEqual(scoped_field_issues('`' + field + '`', schemas,
                                 defer_tool_inputs=(owner,), defer_review_inputs=('role_review', 'pending_findings', 'review_research', 'review_sources'), defer_delivery_inputs=('submission_check', 'repair'), defer_governance=('import_payload', 'import_check', 'governance', 'academic_validation')), [])
        with self.assertRaisesRegex(ValueError, 'Unknown deferred tool input owners'):
            scoped_field_issues('', schemas, defer_tool_inputs=('preveiw',), defer_review_inputs=('role_review', 'pending_findings', 'review_research', 'review_sources'), defer_delivery_inputs=('submission_check', 'repair'), defer_governance=('import_payload', 'import_check', 'governance', 'academic_validation'))
        for text in ('`status.budget`', '`results[].report`', '`operational_evidence.checkpoint_source`'):
            with self.assertRaisesRegex(ValueError, 'fields require the actual'):
                scoped_field_issues(text, schemas, defer_tool_inputs=TOOL_INPUT_BOUNDARIES, defer_review_inputs=('role_review', 'pending_findings', 'review_research', 'review_sources'), defer_delivery_inputs=('submission_check', 'repair'), defer_governance=('import_payload', 'import_check', 'governance', 'academic_validation'))

    def test_deferred_tools_have_their_actual_document_check(self):
        import ast
        from support.doc_code import TOOL_INPUT_BOUNDARIES
        tree = ast.parse((SCRIPTS / 'tests/sim/test_role_input_context.py').read_text(encoding='utf-8'))
        cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'PreparedInputTests')
        method = next(n for n in cls.body if isinstance(n, ast.FunctionDef)
                      and n.name == 'test_installed_tools_match_the_final_role_input_and_reject_damage')
        calls = [k.value.value for n in ast.walk(method) if isinstance(n, ast.Call)
                 and isinstance(n.func, ast.Name) and n.func.id == 'assert_tool_documents'
                 for k in n.keywords if k.arg == 'owner' and isinstance(k.value, ast.Constant)]
        def verify(owners):
            self.assertEqual(set(owners), set(TOOL_INPUT_BOUNDARIES))
            self.assertLessEqual(set(owners), set(calls))
        verify(TOOL_INPUT_BOUNDARIES)
        for changed in (set(TOOL_INPUT_BOUNDARIES) - {'preview'},
                        (set(TOOL_INPUT_BOUNDARIES) - {'preview'}) | {'preveiw'}):
            with self.assertRaises(AssertionError):
                verify(changed)
        calls.remove('scholarly')
        with self.assertRaises(AssertionError):
            verify(TOOL_INPUT_BOUNDARIES)

    def test_result_fields_require_their_actual_input_owner(self):
        schemas = field_schemas()
        owners = {'source_ref': '.path', 'materialized_output_files': '[].local_path',
                  'research_sources': '[].local_path', 'results': '[].report'}
        for owner, suffix in owners.items():
            for text in (f'`{owner}{suffix}`',
                         f'`value{suffix}` <!-- do-math fields: value={owner} -->'):
                with self.subTest(owner=owner, text=text), self.assertRaisesRegex(
                        ValueError, owner + ' fields require the actual result input'):
                    scoped_field_issues(text, schemas)
                with self.assertRaisesRegex(ValueError, owner + ' fields require the actual result input'):
                    scoped_field_issues(text, schemas, defer_result_inputs=set(owners) - {owner})
                self.assertEqual(scoped_field_issues(text, schemas, defer_result_inputs=(owner,)), [])
        with self.assertRaisesRegex(ValueError, 'Unknown deferred result input owners'):
            scoped_field_issues('', schemas, defer_result_inputs=('resutls',))
        for text, owner in (('`result_source.local_path`', 'result_source'),
                            ('`operational_evidence.activity_continuations`', 'operational_evidence'),
                            ('`status.budget`', 'status')):
            with self.assertRaisesRegex(ValueError, owner + ' fields require the actual'):
                scoped_field_issues(text, schemas, defer_result_inputs=owners)

    def test_deferred_result_inputs_have_a_document_check_in_the_assigned_method(self):
        import ast
        from support.doc_code import RESULT_INPUT_BOUNDARIES
        owners = {
            'source_ref': ('unit/test_context_catalog.py', 'ContextStoreTests',
                           'test_new_catalog_is_hashed_from_the_bytes_it_wrote'),
            'materialized_output_files': ('sim/test_role_input_context.py', 'PackagedInputTests',
                           'test_task_result_paths_survive_packaging_without_entering_validation_hashes'),
            'research_sources': ('sim/test_role_input_context.py', 'PackagedInputTests',
                           'test_planning_keeps_completed_report_and_active_work_as_readable_context'),
            'results': ('flows/test_submission_acceptance.py', 'AcceptanceTests',
                           'test_large_accepted_report_survives_revision_review_and_resumed_work')}
        def verify(mapping):
            self.assertEqual(set(mapping), set(RESULT_INPUT_BOUNDARIES), 'deferred result owners differ')
            for owner, (path, class_name, method_name) in mapping.items():
                tree = ast.parse((SCRIPTS / 'tests' / path).read_text(encoding='utf-8'))
                cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == class_name)
                methods = [n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == method_name]
                self.assertEqual(len(methods), 1, owner + ' needs assigned method')
                calls = [n for n in ast.walk(methods[0]) if isinstance(n, ast.Call)
                         and isinstance(n.func, ast.Name) and n.func.id == 'assert_result_documents'
                         and any(k.arg == 'owner' and isinstance(k.value, ast.Constant)
                                 and k.value.value == owner for k in n.keywords)]
                self.assertTrue(calls, owner + ' needs its actual document check')
        verify(owners)
        for fault in ('wrong_owner', 'missing_owner', 'missing_method', 'wrong_method'):
            changed = dict(owners)
            if fault == 'wrong_owner':
                changed['resutls'] = changed.pop('results')
            elif fault == 'missing_owner':
                del changed['source_ref']
            elif fault == 'missing_method':
                changed['results'] = (*changed['results'][:2], 'test_missing')
            else:
                changed['research_sources'] = (*changed['research_sources'][:2],
                    'test_manifest_batch_read_keeps_exact_validation_and_missing_bindings')
            with self.subTest(fault=fault), self.assertRaises(AssertionError):
                verify(changed)

    def test_operational_fields_require_their_actual_input_owner(self):
        schemas = field_schemas()
        for owner, field in (('operational_evidence', 'activity_continuations'),
                             ('recovery_materials', 'output_files[].restoration_error')):
            with self.subTest(owner=owner), self.assertRaisesRegex(ValueError, owner + ' fields require the actual'):
                scoped_field_issues('`' + owner + '.' + field + '`', schemas)
            other = {'operational_evidence', 'recovery_materials'} - {owner}
            with self.assertRaisesRegex(ValueError, owner + ' fields require the actual'):
                scoped_field_issues('`' + owner + '.' + field + '`', schemas, defer_operational_inputs=other)
            self.assertEqual(scoped_field_issues('`' + owner + '.' + field + '`', schemas,
                defer_result_inputs=('source_ref', 'materialized_output_files', 'research_sources', 'results'),
                defer_operational_inputs=(owner,)), [])
        for name in ('checkpoint_source', 'recovery_source', 'checkpoint_files', 'recovered_output_files'):
            self.assertNotIn(name, schemas)
        with self.assertRaisesRegex(ValueError, 'Unknown deferred operational input owners'):
            scoped_field_issues('', schemas, defer_operational_inputs=('operational_evience',))
        with self.assertRaisesRegex(ValueError, 'result_source fields require the actual continuation'):
            scoped_field_issues('`result_source.local_path`', schemas,
                               defer_result_inputs=('source_ref', 'materialized_output_files', 'research_sources', 'results'),
                               defer_operational_inputs=('operational_evidence', 'recovery_materials'))

    def test_deferred_operational_inputs_have_a_document_check_in_the_assigned_method(self):
        import ast
        from support.doc_code import OPERATIONAL_INPUT_BOUNDARIES
        owners = {
            'operational_evidence': ('sim/test_role_input_context.py', 'OperationalInputTests',
                                    'test_live_review_receives_exact_checkpoint_evidence_files'),
            'recovery_materials': ('sim/test_knowledge_currentness.py', 'RecoveryMaterialTests',
                                  'test_failed_execution_materials_are_restored_for_its_operational_review')}
        def verify(mapping):
            expected = set(OPERATIONAL_INPUT_BOUNDARIES)
            self.assertEqual(set(mapping), expected,
                f'deferred operational owners differ: missing={sorted(expected - set(mapping))}, '
                f'unexpected={sorted(set(mapping) - expected)}')
            for owner, (path, class_name, method_name) in mapping.items():
                tree = ast.parse((SCRIPTS / 'tests' / path).read_text(encoding='utf-8'))
                classes = [n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == class_name]
                self.assertEqual(len(classes), 1)
                methods = [n for n in classes[0].body if isinstance(n, ast.FunctionDef) and n.name == method_name]
                self.assertEqual(len(methods), 1, owner + ' needs assigned method ' + method_name)
                calls = [n for n in ast.walk(methods[0]) if isinstance(n, ast.Call)
                         and isinstance(n.func, ast.Name) and n.func.id == 'assert_operational_documents'
                         and any(k.arg == 'owner' and isinstance(k.value, ast.Constant)
                                 and k.value.value == owner for k in n.keywords)]
                self.assertTrue(calls, owner + ' needs its actual document check')
        verify(owners)
        rejections = {
            'wrong_owner': "deferred operational owners differ: missing=['operational_evidence'], unexpected=['operational_evience']",
            'missing_owner': "deferred operational owners differ: missing=['recovery_materials'], unexpected=[]",
            'missing_method': 'recovery_materials needs assigned method test_missing',
            'wrong_method': 'operational_evidence needs its actual document check'}
        for fault in ('wrong_owner', 'missing_owner', 'missing_method', 'wrong_method'):
            changed = dict(owners)
            if fault == 'wrong_owner':
                changed['operational_evience'] = changed.pop('operational_evidence')
            elif fault == 'missing_owner':
                del changed['recovery_materials']
            elif fault == 'missing_method':
                changed['recovery_materials'] = (*changed['recovery_materials'][:2], 'test_missing')
            else:
                changed['operational_evidence'] = (*changed['operational_evidence'][:2],
                    'test_review_gets_the_same_canonical_basis_set_as_application')
            with self.subTest(fault=fault), self.assertRaisesRegex(AssertionError, re.escape(rejections[fault]) + r'$'):
                verify(changed)

    def test_operational_document_names_the_result_and_checkpoint_owners(self):
        from support.doc_code import SPAN
        text = (SKILL / '계약/운영-점검.md').read_text(encoding='utf-8')
        self.assertIn('operational_evidence.checkpoint_source.local_path', SPAN.findall(text))
        self.assertIn('recovery_materials.result_source.local_path', SPAN.findall(text))
        self.assertNotIn('checkpoint_source.local_path', SPAN.findall(text))
        self.assertNotIn('result_source.local_path', SPAN.findall(text))

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
        self.assertEqual(command_issues('`do_math.py status [--goal-file question.txt]`', options, flags),
                         [('command option', 'status', '--goal-file')])
        self.assertEqual(command_issues('`status [--goal-file question.txt]`', options, flags),
                         [('command option', 'status', '--goal-file')])
        self.assertEqual(command_issues('`status [--json] [--snapshot OID]`', options, flags), [])
        self.assertEqual(command_issues('`do_math.py init [--goal-file question.txt]`', options, flags), [])
        self.assertEqual(command_issues('`timeline --include-operations`', options, flags), [])
        self.assertEqual(command_issues('```powershell\npython $dmCli run `\n --watch\n```', options, flags), [])
        self.assertEqual(command_issues('```powershell\npython $dmCli status `\n [--goal-file question.txt]\n```', options, flags),
                         [('command option', 'status', '--goal-file')])
        self.assertEqual(command_issues('```sh\npython do_math.py status \\\n [--goal-file question.txt]\n```', options, flags),
                         [('command option', 'status', '--goal-file')])
        self.assertEqual(command_issues('`do_math.py run --watch` and `--goal-file` belongs to init.', options, flags), [])
        self.assertEqual(command_issues('`do_math.py run [--watch]` and `[--goal-file question.txt]` belongs to init.', options, flags), [])

    def test_documented_scoped_fields_belong_to_their_actual_schema(self):
        schemas = field_schemas()
        for text in ('`profile_selection.allowed_profiles`',
                     '`result.allowed_profiles` <!-- do-math fields: result=profile_selection -->'):
            with self.subTest(text=text):
                with self.assertRaisesRegex(ValueError, 'profile_selection fields require the actual'):
                    scoped_field_issues(text, schemas)
                with self.assertRaisesRegex(ValueError, 'profile_selection fields require the actual'):
                    scoped_field_issues(text, schemas,
                                        defer_role_inputs=('input_manifest', 'prompt', 'documents'))
                self.assertEqual(scoped_field_issues(text, schemas,
                    defer_role_inputs=('profile_selection',)), [])
                self.assertEqual(unowned_field_references(text, schemas), [])
        # Continuation fields need the restored response, including its files.
        for owner, suffix in (('result_source', '.local_path'), ('rejected_response', '.local_path'),
                              ('previous_output_files', '[].local_path')):
            for text in (f'`{owner}{suffix}`',
                         f'`result{suffix}` <!-- do-math fields: result={owner} -->'):
                with self.subTest(owner=owner, text=text):
                    with self.assertRaisesRegex(ValueError, owner + ' fields require the actual continuation result'):
                        scoped_field_issues(text, schemas)
                    others = {'result_source', 'rejected_response', 'previous_output_files'} - {owner}
                    with self.assertRaisesRegex(ValueError, owner + ' fields require the actual continuation result'):
                        scoped_field_issues(text, schemas, defer_status=True, defer_operation_progress=True,
                            defer_query_record=True, defer_query_result=True,
                            defer_cli_results=('init_result', 'scheduling_result', 'selection_result'),
                            defer_result_inputs=('source_ref', 'materialized_output_files', 'research_sources', 'results'),
                            defer_operational_inputs=('operational_evidence', 'recovery_materials'),
                            defer_role_inputs=('input_manifest', 'prompt', 'documents', 'profile_selection'),
                            defer_continuations=others)
                    self.assertEqual(scoped_field_issues(text, schemas, defer_continuations=(owner,)), [])
                    self.assertEqual(unowned_field_references(text, schemas), [])
        with self.assertRaisesRegex(ValueError, 'Unknown deferred continuation owners'):
            scoped_field_issues('', schemas, defer_continuations=('result_sorce',))
        with self.assertRaisesRegex(ValueError, 'status fields require the actual repository report'):
            scoped_field_issues('`status.budget`', schemas,
                defer_continuations=('result_source', 'rejected_response', 'previous_output_files'))
        # unit.test_storage_report_projections checks these same documents with
        # status_report's actual repository response, including result=status.
        for text in ('`status.budget`', '`result.config_sha256` <!-- do-math fields: result=status -->'):
            with self.assertRaisesRegex(ValueError, 'status fields require the actual repository report'):
                scoped_field_issues(text, schemas)
            self.assertEqual(scoped_field_issues(text, schemas, defer_status=True), [])
            self.assertEqual(unowned_field_references(text, schemas), [])
        self.assertEqual(unowned_field_references('`statuz.budget`', schemas), ['statuz.budget'])
        # unit.test_engine_trace_report_corruption owns the independent file
        # response; deferring either boundary must not defer the other one.
        for text in ('`operation_progress.telemetry_errors`',
                     '`result.telemetry_errors` <!-- do-math fields: result=operation_progress -->'):
            with self.assertRaisesRegex(ValueError, 'operation_progress fields require the actual file report'):
                scoped_field_issues(text, schemas)
            with self.assertRaisesRegex(ValueError, 'operation_progress fields require the actual file report'):
                scoped_field_issues(text, schemas, defer_status=True)
            self.assertEqual(scoped_field_issues(text, schemas, defer_operation_progress=True), [])
            self.assertEqual(unowned_field_references(text, schemas), [])
        with self.assertRaisesRegex(ValueError, 'status fields require the actual repository report'):
            scoped_field_issues('`status.budget`', schemas, defer_operation_progress=True)
        self.assertEqual(unowned_field_references('`operation_progres.telemetry_errors`', schemas),
                         ['operation_progres.telemetry_errors'])
        # Existing record/CLI tests provide these independent query responses.
        for owner, field in (('query_record', 'family'), ('query_result', 'snapshot')):
            for text in (f'`{owner}.{field}`',
                         f'`result.{field}` <!-- do-math fields: result={owner} -->'):
                with self.assertRaisesRegex(ValueError, owner + ' fields require the actual'):
                    scoped_field_issues(text, schemas)
                with self.assertRaisesRegex(ValueError, owner + ' fields require the actual'):
                    scoped_field_issues(text, schemas, defer_status=True, defer_operation_progress=True,
                                        **{'defer_query_result' if owner == 'query_record'
                                           else 'defer_query_record': True})
                self.assertEqual(scoped_field_issues(text, schemas,
                    **{'defer_' + owner: True}), [])
                self.assertEqual(unowned_field_references(text, schemas), [])
        with self.assertRaisesRegex(ValueError, 'status fields require the actual repository report'):
            scoped_field_issues('`status.budget`', schemas, defer_query_record=True, defer_query_result=True)
        with self.assertRaisesRegex(ValueError, 'operation_progress fields require the actual file report'):
            scoped_field_issues('`operation_progress.telemetry_errors`', schemas,
                                defer_query_record=True, defer_query_result=True)
        for owner, field in (('init_result', 'instance_id'),
                             ('scheduling_result', 'operator_schedule'),
                             ('selection_result', 'selection.profile_ref')):
            for text in (f'`{owner}.{field}`',
                         f'`result.{field}` <!-- do-math fields: result={owner} -->'):
                with self.subTest(owner=owner, text=text):
                    with self.assertRaisesRegex(ValueError, owner + ' fields require the actual CLI result'):
                        scoped_field_issues(text, schemas)
                    others = {'init_result', 'scheduling_result', 'selection_result'} - {owner}
                    with self.assertRaisesRegex(ValueError, owner + ' fields require the actual CLI result'):
                        scoped_field_issues(text, schemas, defer_status=True, defer_operation_progress=True,
                                            defer_query_record=True, defer_query_result=True,
                                            defer_cli_results=others)
                    self.assertEqual(scoped_field_issues(text, schemas, defer_cli_results=(owner,)), [])
                    self.assertEqual(unowned_field_references(text, schemas), [])
        with self.assertRaisesRegex(ValueError, 'Unknown deferred CLI result owners'):
            scoped_field_issues('', schemas, defer_cli_results=('selection_reslt',))
        with self.assertRaisesRegex(ValueError, 'status fields require the actual repository report'):
            scoped_field_issues('`status.budget`', schemas,
                                defer_cli_results=('init_result', 'scheduling_result', 'selection_result'))
        issues = [(document.relative_to(SKILL).as_posix(), *issue)
                  for document in documents(SKILL)
                  for issue in scoped_field_issues(document.read_text(encoding='utf-8'), schemas,
                                                  defer_status=True, defer_operation_progress=True,
                                                  defer_query_record=True, defer_query_result=True,
                                                  defer_cli_results=('init_result', 'scheduling_result', 'selection_result'),
                                                  defer_result_inputs=('source_ref', 'materialized_output_files', 'research_sources', 'results'),
                                                  defer_operational_inputs=('operational_evidence', 'recovery_materials'),
                                                  defer_continuations=('result_source', 'rejected_response', 'previous_output_files'),
                                                  defer_role_inputs=('input_manifest', 'prompt', 'documents', 'profile_selection'),
                                                  defer_tool_inputs=('execution_window', 'scholarly', 'formal_verifier', 'preview',
                                                                     'record_map.read_tool', 'submission_contract'), defer_review_inputs=('role_review', 'pending_findings', 'review_research', 'review_sources'), defer_delivery_inputs=('submission_check', 'repair'), defer_governance=('import_payload', 'import_check', 'governance', 'academic_validation'))]
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
            '`execution.execution_window.effective_deadline_at` '
            '`record_map.snapshot` `record_map.ledger` `record_map.families` '
            '`record_map.blocked_keys` `record_map.instruction` '
            '`assessment.current` `runtime.user_pause`', schemas), [])
        self.assertEqual(scoped_field_issues('`execution.execution_window.self_check_directory`', schemas),
                         [('scoped field', 'execution.execution_window.self_check_directory')])
        from support.doc_code import tool_field_issues
        self.assertEqual(tool_field_issues('`execution_window.effective_deadline_at`', 'execution_window', {}),
                         [('actual field', 'execution_window.effective_deadline_at')])
        self.assertEqual(tool_field_issues('`record_map.read_tool.nonexistent`', 'record_map.read_tool', {}),
                         [('actual field', 'record_map.read_tool.nonexistent')])
        self.assertEqual(scoped_field_issues('`runtime.checkpoint_bytes`', schemas),
                         [('scoped field', 'runtime.checkpoint_bytes')])
        self.assertEqual(scoped_field_issues('`record_map.nonexistent` `record_map.families.nonexistent`', schemas),
                         [('scoped field', 'record_map.families.nonexistent'), ('scoped field', 'record_map.nonexistent')])

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
        def conditional(choice):
            return {'base': 1, **({'optional': 1} if choice else {})}
        def array_producer():
            values = [{'item': 1} for _ in range(1)]
            target = []
            target.append({'own': 1})
            other = []
            other.append({'foreign': 1})
        schema = produced_object_schema(conditional)
        self.assertEqual(scoped_field_issues('`view.base` `view.optional`', {'view': schema}), [])
        self.assertEqual(set(produced_object_schema(array_producer, 'values', list_item=True)['properties']), {'item'})
        self.assertEqual(set(produced_object_schema(array_producer, 'target.append', argument=0)['properties']), {'own'})
        with self.assertRaisesRegex(ValueError, 'Review producer list item'):
            produced_object_schema(array_producer, 'target', list_item=True)
        schema = produced_object_schema(result, bindings={'extra': {'properties': {'observed': {}}}})
        self.assertEqual(scoped_field_issues('`view.own` `view.observed`', {'view': schema}), [])
        with self.assertRaisesRegex(ValueError, 'Unused producer bindings'):
            produced_object_schema(result, bindings={'extra': {'properties': {}}, 'obsolete': {'properties': {}}})
        schema = produced_object_schema(alternatives, variants=True)
        self.assertEqual(scoped_field_issues('`view.left` `view.right`', {'view': schema}), [])
        with self.assertRaisesRegex(ValueError, 'Review document field producer'):
            produced_object_schema(alternatives)
        schemas = field_schemas()
        self.assertEqual(scoped_field_issues(
            '`operational_evidence.activity_continuations`', schemas,
            defer_result_inputs=('source_ref', 'materialized_output_files', 'research_sources', 'results'),
            defer_operational_inputs=('operational_evidence',)), [])
        self.assertEqual(scoped_field_issues('`operating_summary.scope` `operating_summary.lifecycle` '
            '`operating_summary.initialization` `operating_summary.execution_status` `operating_summary.goal_status` '
            '`operating_summary.primary_blocker` `operating_summary.workspace` '
            '`operating_summary.conversation_loss_policy` `operating_summary.active_execution_ids` '
            '`operating_summary.grants` `operating_summary.supervision.configured_enabled` '
            '`operating_summary.supervision.interval_seconds` `operating_summary.supervision.actual_schedule`', schemas), [])
        for token in ('operating_summary.operator_enabled', 'operating_summary.configured_enabled',
                      'operating_summary.supervision.operator_enabled',
                      'operating_summary.primary_blocker.kind', 'operating_summary.grants[].id'):
            with self.subTest(token=token):
                self.assertEqual(scoped_field_issues('`' + token + '`', schemas), [('scoped field', token)])

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
        from support.doc_code import governance_field_issues
        self.assertEqual(governance_field_issues('`governance.charter`', 'governance', {'charter': {}}), [])
        self.assertEqual(governance_field_issues('`governance.mathematical_goal_basis`', 'governance', {'charter': {}}),
                         [('actual field', 'governance.mathematical_goal_basis')])

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
            '`action.role`', schemas, defer_delivery_inputs=('repair',)), [])

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
        def loop_producer(first, second):
            for row in first:
                row['first'] = 1
            for row in second:
                row['second'] = 2
        schema = written_object_schema(loop_producer, 'row', iteration='first')
        self.assertEqual(set(schema['properties']), {'first'})
        schemas = field_schemas()
        for owner, suffix in (('input_manifest', '.prompt.sha256'), ('prompt', '.artifact_ref'),
                              ('documents', '[].artifact_ref')):
            for text in (f'`{owner}{suffix}`',
                         f'`result{suffix}` <!-- do-math fields: result={owner} -->'):
                with self.subTest(owner=owner, text=text):
                    with self.assertRaisesRegex(ValueError, owner + ' fields require the actual role input'):
                        scoped_field_issues(text, schemas)
                    with self.assertRaisesRegex(ValueError, owner + ' fields require the actual role input'):
                        scoped_field_issues(text, schemas, defer_status=True, defer_operation_progress=True,
                            defer_query_record=True, defer_query_result=True,
                            defer_cli_results=('init_result', 'scheduling_result', 'selection_result'),
                            defer_result_inputs=('source_ref', 'materialized_output_files', 'research_sources', 'results'),
                            defer_operational_inputs=('operational_evidence', 'recovery_materials'),
                            defer_role_inputs={'input_manifest', 'prompt', 'documents', 'profile_selection'} - {owner})
                    self.assertEqual(scoped_field_issues(text, schemas, defer_role_inputs=(owner,)), [])
                    self.assertEqual(unowned_field_references(text, schemas), [])
        with self.assertRaisesRegex(ValueError, 'Unknown deferred role input owners'):
            scoped_field_issues('', schemas, defer_role_inputs=('input_manfiest',))
        with self.assertRaisesRegex(ValueError, 'status fields require the actual repository report'):
            scoped_field_issues('`status.budget`', schemas,
                                defer_role_inputs=('input_manifest', 'prompt', 'documents', 'profile_selection'))

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
        with self.assertRaisesRegex(ValueError, 'actual delivery input'):
            scoped_field_issues('`check.passed` <!-- do-math fields: check=submission_check -->', schemas)
        from support.doc_code import governance_field_issues
        with self.assertRaisesRegex(ValueError, 'actual governance value'):
            scoped_field_issues('`check.sha256` <!-- do-math fields: check=import_check -->', schemas)
        self.assertEqual(governance_field_issues('`check.sha256` <!-- do-math fields: check=import_check -->',
                         'import_check', {'sha256': 'actual'}), [])
        self.assertEqual(governance_field_issues('`check.passed` <!-- do-math fields: check=import_check -->',
                         'import_check', {'sha256': 'actual'}), [('actual field', 'check.passed')])
        from support.doc_code import delivery_field_issues
        self.assertEqual(delivery_field_issues('`check.sha256` <!-- do-math fields: check=submission_check -->',
                         'submission_check', {'passed': True}), [('actual field', 'check.sha256')])
        self.assertEqual(scoped_field_issues('`change.value` '
            '`toolchain.project.search_paths` `environment_check.changed_files`', schemas), [])
        self.assertEqual(scoped_field_issues('`change.nonexistent`', schemas),
                         [('scoped field', 'change.nonexistent')])
        self.assertEqual(governance_field_issues('`payload.deadline_offset_ms` <!-- do-math fields: payload=import_payload -->',
                         'import_payload', {'kind': 'charter'}), [('actual field', 'payload.deadline_offset_ms')])

    def test_all_dotted_document_fields_have_an_owner(self):
        schemas = field_schemas()
        pending = [(document.relative_to(SKILL).as_posix(), token)
                   for document in documents(SKILL)
                   for token in unowned_field_references(document.read_text(encoding='utf-8'), schemas)]
        self.assertEqual(pending, [])
        self.assertEqual(unowned_field_references('`recrod.id` `new_space.value`', schemas),
                         ['new_space.value', 'recrod.id'])
        self.assertEqual(unowned_field_references('`record.id` <!-- do-math fields: record=governance_record -->', schemas), [])
        self.assertEqual(unowned_field_references('`pythonw.exe` `integration.currentness` `os.scandir(...)`', schemas), [])

    def test_array_paths_follow_items_instead_of_borrowing_parent_or_map_fields(self):
        item = {'properties': {'own': {}, 'nested': {'type': 'array', 'items': {'properties': {'leaf': {}}}}}}
        schemas = {'rows': {'type': 'array', 'items': item},
                   'mapping': {'type': 'object', 'additionalProperties': item},
                   'object': {'properties': {'own': {}}}}
        self.assertEqual(scoped_field_issues('`rows[].own` `rows[0].nested[].leaf`', schemas), [])
        for token in ('rows.own', 'rows[].leaf', 'mapping[].own', 'object[].own'):
            self.assertEqual(scoped_field_issues('`' + token + '`', schemas), [('scoped field', token)])
        self.assertEqual(unowned_field_references('`unknown[].own` `integration[].currentness` `unknown[].json`', schemas),
                         ['integration[].currentness', 'unknown[].json', 'unknown[].own'])
        self.assertEqual(scoped_field_issues('`data[].own` <!-- do-math fields: data=rows -->', schemas), [])
        actual = field_schemas()
        with self.assertRaisesRegex(ValueError, 'documents fields require the actual role input'):
            scoped_field_issues('`documents[].artifact_ref`', actual)
        self.assertEqual(scoped_field_issues('`question_details[].id`', actual), [])
        with self.assertRaisesRegex(ValueError, 'results fields require the actual result input'):
            scoped_field_issues('`results[].report` `results[].output_files[].local_path`', actual)
        self.assertEqual(scoped_field_issues('`execution.output_files[].local_path`', actual),
                         [('scoped field', 'execution.output_files[].local_path')])

    def test_documented_module_constants_exist_independently_of_field_names(self):
        issues = [(document.relative_to(SKILL).as_posix(), *issue)
                  for document in documents(SKILL)
                  for issue in constant_reference_issues(document.read_text(encoding='utf-8'))]
        self.assertEqual(issues, [])
        self.assertEqual(constant_reference_issues('`planning.RECORD_FAMILIES` `observations.OPERATORS` `knowledge.AUTHORED_FIELDS`'), [])
        self.assertEqual(constant_reference_issues('`planning.MISSING_CONSTANT` `missing_module.OPERATORS`'),
                         [('constant reference', 'missing_module.OPERATORS'), ('constant reference', 'planning.MISSING_CONSTANT')])

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
