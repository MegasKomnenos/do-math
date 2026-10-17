"""13-C commands, policies, dotted fields, functions and constants in role documents.

Selected review output declarations and partial JSON examples have explicit
stage/extension owners. Other prose and reading obligations require separate closure.
"""
from pathlib import Path
import re
import unittest
from support.doc_code import (command_issues, constant_reference_issues, declared_policy_names, diagnostic_names, diagnostic_reference_issues, documented_policies, documents,
                              field_bindings, field_schemas, function_reference_issues, parser_options, policy_issues, scoped_field_issues, tool_options, unowned_field_references)

SKILL = Path(__file__).resolve().parents[3]
SCRIPTS = SKILL / 'scripts'


class DocumentCodeTests(unittest.TestCase):
    def test_named_examples_and_declarations_are_checked_in_the_document_population(self):
        from support.doc_code import named_document_issues
        population = documents(SKILL)
        required = {'README.md', 'references/초기화-운전.md', 'references/CLI-실행-계약.md'}
        self.assertLessEqual(required, {path.relative_to(SKILL).as_posix() for path in population})
        issues = [(path.relative_to(SKILL).as_posix(), *issue)
                  for path in population
                  for issue in named_document_issues(path.read_text(encoding='utf-8'), path.relative_to(SKILL).as_posix())]
        self.assertEqual(issues, [])

    def test_setup_and_probe_examples_use_their_own_parser_and_input_rules(self):
        from support.doc_code import tool_command_issues
        for text in ('`setup_lean.py --verify-only --trust-file new.json`', '`probe_cli.py --skill-only`'):
            self.assertEqual(tool_command_issues(text), [])
        for text, owner, reason in (
                ('`setup_lean.py --verify-only --watch`', 'setup_lean.py', 'unrecognized arguments: --watch'),
                ('`probe_cli.py --skill-only --verify-only`', 'probe_cli.py', 'unrecognized arguments: --verify-only'),
                ('`setup_lean.py --inspect-only --verify-only`', 'setup_lean.py', 'not allowed with argument'),
                ('`setup_lean.py --inspect-only --trust-file new.json`', 'setup_lean.py', 'neither records nor validates'),
                ('`probe_cli.py --provider other`', 'probe_cli.py', 'invalid choice'),
                ('`probe_cli.py --provider codex`', 'probe_cli.py', 'live probes require explicit')):
            with self.subTest(text=text):
                issue, = tool_command_issues(text)
                self.assertEqual(issue[:2], ('tool arguments', owner))
                self.assertIn(reason, issue[2])

    def test_initialization_examples_reject_misspellings_borrowed_fields_and_absence(self):
        from support.doc_code import initialization_example_issues, _document_section
        cases = (
            ('README.md', '모델과 동시실행 예산 설정', ('"session_limits"', '"session_limitz"')),
            ('references/초기화-운전.md', '3. 초기화 권한과 연구 권한을 나눈다', ('"reuse": "reusable",', '"reuse": "reusable", "budget_kind": "work",')))
        for document, heading, (old, new) in cases:
            text = (SKILL / document).read_text(encoding='utf-8')
            check = lambda value: initialization_example_issues(value, document)
            with self.subTest(document=document):
                self.assertEqual(check(text), [])
                self.assertTrue(check(text.replace(old, new)))
                self.assertTrue(check(text.replace(heading, 'removed')))
                section = _document_section(text, heading)
                fences = re.findall(r'^```json\n.*?\n```', section, flags=re.M | re.S)
                for fence in fences:
                    self.assertTrue(check(text.replace(fence, '')))
        config = (SKILL / 'README.md').read_text(encoding='utf-8')
        self.assertTrue(initialization_example_issues(config.replace('"tier_models":', '"tier_modelz":'), 'README.md'))
        grant = (SKILL / 'references/초기화-운전.md').read_text(encoding='utf-8')
        self.assertTrue(initialization_example_issues(grant.replace('    "roles": ["intent_interpretation", "maintenance"],\n', ''), 'references/초기화-운전.md'))

    def test_identity_module_sentence_matches_both_actual_adapter_declarations(self):
        from support.doc_code import identity_module_issues
        text = (SKILL / 'references/초기화-운전.md').read_text(encoding='utf-8')
        self.assertEqual(identity_module_issues(text), [])
        for old, new in (('`control_protocol`, ', ''), ('`codex_adapter`이고', '`claude_adapter`이고')):
            with self.subTest(old=old):
                issues = identity_module_issues(text.replace(old, new))
                self.assertTrue(issues)
                self.assertEqual(issues[0][1], 'CodexExecAdapter')
        self.assertTrue(identity_module_issues(text.replace('Codex 어댑터의 식별 모듈은', 'removed')))

    def test_cli_tables_bind_state_default_enum_and_required_table_coverage(self):
        from support.doc_code import cli_table_issues, _document_section
        text = (SKILL / 'references/CLI-실행-계약.md').read_text(encoding='utf-8')
        self.assertEqual(cli_table_issues(text), [])
        for old, new, owner in (
                ('| `capacity_waiting` |', '| `capacity_waitng` |', 'runtime.status'),
                ('| `reviewers` | 2 |', '| `reviewers` | 200 |', 'reviewers'),
                ('| `observation_mode` | `event_driven` | `event_driven`, `periodic` |',
                 '| `observation_mode` | `event_driven` | `event_driven`, `periodical` |', 'observation_mode')):
            with self.subTest(owner=owner):
                issues = cli_table_issues(text.replace(old, new))
                self.assertTrue(any(issue[1] == owner for issue in issues), issues)
        for heading in ('인스턴스 실행 루프 `runtime.status`', '설정 계약'):
            self.assertTrue(cli_table_issues(text.replace(heading, 'removed')))
            self.assertTrue(cli_table_issues(text.replace(_document_section(text, heading), '')))

    def test_cli_query_synopsis_uses_actual_choices_and_requires_its_fence(self):
        from support.doc_code import cli_query_issues
        text = (SKILL / 'references/CLI-실행-계약.md').read_text(encoding='utf-8')
        self.assertEqual(cli_query_issues(text), [])
        self.assertEqual(cli_query_issues(text.replace('[--direction incoming|outgoing|both]',
                        '[--direction incoming|outgoing|sideways]'))[0][0], 'query direction choices')
        self.assertTrue(cli_query_issues(text.replace('### record `query`', '### removed')))
        self.assertTrue(cli_query_issues(text.replace('[--direction incoming|outgoing|both]', '')))

    def test_cli_knowledge_json_checks_control_shape_and_candidate_semantics_separately(self):
        from support.doc_code import cli_knowledge_example_issues, _document_section
        text = (SKILL / 'references/CLI-실행-계약.md').read_text(encoding='utf-8')
        self.assertEqual(cli_knowledge_example_issues(text), [])
        self.assertEqual(cli_knowledge_example_issues(text.replace('"operation":"import"',
                         '"operation":"improt"'))[0][0], 'document knowledge control')
        self.assertEqual(cli_knowledge_example_issues(text.replace('"summary":"목차 요약"',
                         '"summray":"목차 요약"')), [('document knowledge candidate', 'candidate summary is invalid')])
        for heading in ('candidate 수입', '종류 정의 등록', '관계 수입', '기존 지식 개정·무효화'):
            self.assertTrue(cli_knowledge_example_issues(text.replace(heading, 'removed')))
            section = _document_section(text, heading)
            for fence in re.findall(r'^```json\n.*?\n```', section, flags=re.M | re.S):
                self.assertTrue(cli_knowledge_example_issues(text.replace(fence, '')))

    def test_cli_review_stage_declarations_keep_root_item_and_enum_owners(self):
        from support.doc_code import cli_stage_issues, _document_section
        text = (SKILL / 'references/CLI-실행-계약.md').read_text(encoding='utf-8')
        self.assertEqual(cli_stage_issues(text), [])
        cases = (
            ('`scope_complete`, `findings`를 추가한다', '`scope_complete`, `findingz`를 추가한다', 'initial'),
            ('`issues`를 추가하며', '`issues`와 `decision`을 추가하며', 'organize'),
            ('`answers`와 `new_findings`를 추가한다', '`answerz`와 `new_findings`를 추가한다', 'answer'),
            ('`decision=approved|rejected|unresolved`, `reason`', '`decision=match|rejected|unresolved`, `reason`', 'judge/issue_verdicts[]'))
        for old, new, owner in cases:
            with self.subTest(owner=owner):
                self.assertIn(old, text)
                issues = cli_stage_issues(text.replace(old, new))
                self.assertTrue(any(issue[1] == owner for issue in issues), issues)
        for stage in ('initial', 'organize', 'answer', 'judge'):
            heading = '`' + stage + '`'
            self.assertTrue(cli_stage_issues(text.replace('### ' + heading, '### removed')))
            self.assertTrue(cli_stage_issues(text.replace(_document_section(text, heading), '')))

    def test_cli_checkpoint_file_example_uses_the_actual_value_checker(self):
        from support.doc_code import cli_checkpoint_issues, _document_section
        text = (SKILL / 'references/CLI-실행-계약.md').read_text(encoding='utf-8')
        self.assertEqual(cli_checkpoint_issues(text), [])
        issues = cli_checkpoint_issues(text.replace('"current_claim":', '"current_cliam":'))
        self.assertTrue(issues)
        self.assertEqual(issues[0][0], 'document checkpoint')
        self.assertTrue(cli_checkpoint_issues(text.replace('### `checkpoint.json`', '### removed')))
        section = _document_section(text, '`checkpoint.json`')
        fence, = re.findall(r'^```json\n.*?\n```', section, flags=re.M | re.S)
        self.assertTrue(cli_checkpoint_issues(text.replace(fence, '')))

    def test_corrected_cli_meanings_keep_their_current_structure_and_authority_boundaries(self):
        from support.doc_code import _document_section, _schema_path
        from do_math.control_contracts import PAYLOADS
        from do_math.contracts import action_schema
        from do_math.record_schemas.schemas import RECORDS
        text = (SKILL / 'references/CLI-실행-계약.md').read_text(encoding='utf-8')
        knowledge = _document_section(text, '`knowledge`')
        first = knowledge.split('\n\n', 1)[0]
        self.assertEqual(set(re.findall(r'`([a-z-]+)`', first)) - {'knowledge', 'closed', 'completed'},
                         set(PAYLOADS['knowledge']['properties']['operation']['enum']))
        for phrase in ('기존 ID의 수입은 거부된다', '새 replacement ID', '`supersedes`',
                       'revision을 1 올린다', '옛 기록과 형식 결과·판정', '현재 사용 가능', '`withdraw-kind`로 철회'):
            self.assertIn(phrase, knowledge)
        external = _document_section(text, '`external`')
        for phrase in ('별도 execution', '`running`', '`transmitted=true`', '2xx이면',
                       '`confirmed`, `succeeded=true`', '비2xx', '`failed`, `succeeded=false`',
                       '`unknown`, `succeeded=null`'):
            self.assertIn(phrase, external)
        operation_row, = [line for line in text.splitlines() if line.startswith('| 외부 operation |')]
        self.assertEqual(set(re.findall(r'`([a-z_]+)`', operation_row.split('|')[2])),
                         set(RECORDS['external_operations']['properties']['status']['enum']))
        schema = _schema_path(action_schema({'role': 'research_work'}), 'knowledge[].kind')[0]
        self.assertEqual(schema['type'], 'string')
        self.assertNotIn('enum', schema)
        work = _document_section(text, '연구 수행 `research_work`와 과제 기반 `supplemental_research`')
        for phrase in ('문자열(TEXT)', '중앙 수신의 의미 검사', '활성 종류', '같은 편입 묶음',
                       '미등록 종류는 반려', '독립 의미 검사와 활성화 권한'):
            self.assertIn(phrase, work)

    def test_identity_output_declarations_use_their_exact_stage_and_item(self):
        from support.doc_code import review_output_issues
        text = (SKILL / '계약/동일성-검토.md').read_text(encoding='utf-8')
        self.assertEqual(review_output_issues(text), [])
        changed = text.replace('와 `findings`를 반환한다', '와 `findingz`를 반환한다')
        self.assertEqual(review_output_issues(changed), [
            ('review output missing field', 'initial', 'findings'),
            ('review output field', 'initial', 'findingz')])
        changed = text.replace('쟁점 정리는 동일성을 승인하는 단계가 아니다.',
            '쟁점 정리는 동일성을 승인하는 단계가 아니다. 주 산출에는 `decision`을 반환한다.')
        self.assertEqual(review_output_issues(changed), [('review output field', 'organize', 'decision')])
        changed = text.replace('반환의 `finding_refs`', '반환의 `finding_refz`')
        self.assertEqual(review_output_issues(changed), [
            ('review output missing field', 'organize', 'issues[].finding_refs'),
            ('review output field', 'organize', 'finding_refz')])
        # decision belongs to judge/initial elsewhere; prose outside these
        # explicitly assigned output paragraphs must not acquire their owner.
        self.assertEqual(review_output_issues(text + '\n`invented_prose_name`\n'), [])

    def test_missing_review_output_section_or_declaration_is_rejected(self):
        from support.doc_code import review_output_issues, _document_section
        text = (SKILL / '계약/동일성-검토.md').read_text(encoding='utf-8')
        for heading in ('초기 검토에서는 전체 판단과 발견을 반환한다',
                        '쟁점 정리에서는 발견과 답변 담당을 연결한다'):
            with self.subTest(heading=heading):
                self.assertTrue(review_output_issues(text.replace('## ' + heading, '## removed')))
                self.assertTrue(review_output_issues(text.replace(_document_section(text, heading), '')))
        self.assertEqual(len(review_output_issues('')), 2)

    def test_preparation_partial_examples_use_their_exact_extension_branch(self):
        from support.doc_code import preparation_example_issues
        text = (SKILL / '계약/후보-준비.md').read_text(encoding='utf-8')
        self.assertEqual(preparation_example_issues(text), [])
        changed = text.replace('"independent_of_next_revision":false', '"independent_of_revision":false')
        issues = preparation_example_issues(changed)
        self.assertEqual([(issue[1], issue[2], issue[3]) for issue in issues], [
            ('sibling_boundaries[]', '', 'additionalProperties'),
            ('sibling_boundaries[]', '', 'required')])
        self.assertIn('independent_of_revision', issues[0][4])
        self.assertIn('independent_of_next_revision', issues[1][4])
        for identifier, family in (('TK-one', 'model_assessments'), ('TK-two', 'model_assessment_deferrals')):
            with self.subTest(family=family):
                changed = text.replace('"task_id": "' + identifier + '"', '"task_title": "' + identifier + '"')
                issues = preparation_example_issues(changed)
                self.assertEqual([(issue[1], issue[2], issue[3]) for issue in issues], [
                    ('assessment_targets', family + '/0', 'additionalProperties'),
                    ('assessment_targets', family + '/0', 'required')])
                self.assertIn('task_title', issues[0][4])
                self.assertIn('task_id', issues[1][4])

    def test_missing_preparation_document_section_or_json_example_is_rejected(self):
        from support.doc_code import preparation_example_issues
        text = (SKILL / '계약/후보-준비.md').read_text(encoding='utf-8')
        for heading in ('5. 제출 전에 계약을 스스로 점검한다',
                        '기존 과제의 평가와 관찰 규칙을 보충하는 실행'):
            with self.subTest(heading=heading):
                self.assertTrue(preparation_example_issues(text.replace(heading, 'removed')))
        for fence in re.findall(r'^```json\n.*?\n```', text, flags=re.M | re.S):
            with self.subTest(fence=fence):
                issues = preparation_example_issues(text.replace(fence, ''))
                self.assertEqual(len(issues), 1)
                self.assertEqual(issues[0][0], 'preparation example count')
        self.assertEqual(len(preparation_example_issues('')), 2)

    def test_operator_modes_use_the_actual_parser_for_bare_and_entry_commands(self):
        from do_math.cli_contract import build_parser
        options = parser_options(build_parser())
        flags = set().union(*options.values())
        for prefix in ('', 'do_math.py ', '$dmCli '):
            with self.subTest(prefix=prefix):
                for mode in ('install', 'probe'):
                    self.assertEqual(command_issues('`' + prefix + 'operator ' + mode + '`', options, flags), [])
                self.assertEqual(command_issues('`' + prefix + 'operator invent`', options, flags),
                                 [('command mode', 'operator', 'invent')])
        self.assertEqual(command_issues('```powershell\npython $dmCli operator invent `\n --workspace here\n```',
                                       options, flags), [('command mode', 'operator', 'invent')])
        self.assertEqual(command_issues('`operator install|probe`', options, flags), [])
        self.assertEqual(command_issues('`operator install|invent`', options, flags),
                         [('command mode', 'operator', 'invent')])

    def test_trust_fields_require_actual_inspection_and_environment_return(self):
        schemas = field_schemas()
        from support.doc_code import TRUST_BOUNDARIES, trust_field_issues
        for token in ('project.source_identity', 'toolchain.project.search_paths',
                      'environment_check.changed_files'):
            owner, _, suffix = token.partition('.')
            for text in ('`' + token + '`', '`result.' + suffix +
                         '` <!-- do-math fields: result=' + owner + ' -->'):
                with self.subTest(text=text), self.assertRaisesRegex(ValueError, 'actual trust boundary'):
                    scoped_field_issues(text, schemas)
                with self.assertRaisesRegex(ValueError, 'actual trust boundary'):
                    scoped_field_issues(text, schemas, defer_trust=set(TRUST_BOUNDARIES) - {owner})
                self.assertEqual(scoped_field_issues(text, schemas, defer_trust=(owner,)), [])
                self.assertEqual(trust_field_issues(text, owner, {}), [('actual field', text.split('`')[1])])
                self.assertEqual(unowned_field_references(text, schemas), [])
        with self.assertRaisesRegex(ValueError, 'Unknown deferred trust owners'):
            scoped_field_issues('', schemas, defer_trust=('projects',))
        with self.assertRaisesRegex(ValueError, 'actual repository report'):
            scoped_field_issues('`status.budget`', schemas, defer_trust=TRUST_BOUNDARIES)
        with self.assertRaisesRegex(ValueError, 'Unknown trust owner'):
            trust_field_issues('', 'projects', {})
        for owner, value, good, bad in (
                ('project', None, 'project.source_identity', 'project.source_identitty'),
                ('toolchain', {'project': None}, 'toolchain.project.search_paths', 'toolchain.project.search_path'),
                ('environment_check', {'status': 'verified', 'errors': []},
                 'environment_check.changed_files', 'environment_check.changed_filse')):
            self.assertEqual(trust_field_issues('`' + good + '`', owner, value), [])
            self.assertEqual(trust_field_issues('`' + bad + '`', owner, value), [('actual field', bad)])
        mismatch = {'status': 'invalid', 'errors': ['olean fingerprint differs from the bound toolchain baseline']}
        self.assertEqual(trust_field_issues('`environment_check.changed_files`', 'environment_check', mismatch),
                         [('actual field', 'environment_check.changed_files')])
        # A same-named stored field cannot replace the inspected project.
        self.assertEqual(trust_field_issues('`toolchain.project.search_paths`', 'toolchain',
                         {'source_identity': {}, 'search_paths': []}), [('actual field', 'toolchain.project.search_paths')])

    def test_deferred_trust_has_the_assigned_actual_document_check(self):
        import ast
        from support.doc_code import TRUST_BOUNDARIES
        owners = {
            'project': ('boundary/test_knowledge_lean_verifier.py', 'LakeEnvironmentTests',
                        'test_lake_search_paths_are_observed_once_per_unchanged_project_input'),
            'toolchain': ('boundary/test_knowledge_lean_verifier.py', 'LakeEnvironmentTests',
                          'test_lake_search_paths_are_observed_once_per_unchanged_project_input'),
            'environment_check': ('unit/test_trust_environment.py', 'ToolchainRecordTests',
                                  'test_documented_environment_branches_keep_absence_and_exact_changes')}
        def verify(mapping):
            self.assertEqual(set(mapping), set(TRUST_BOUNDARIES), 'document owner population differs')
            for owner, (path, cls_name, method) in mapping.items():
                tree = ast.parse((SCRIPTS / 'tests' / path).read_text(encoding='utf-8'))
                cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == cls_name)
                methods = [n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == method]
                self.assertEqual(len(methods), 1, owner + ' needs assigned method')
                self.assertTrue(any(isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
                    and n.func.id == 'assert_trust_documents' and any(k.arg == 'owner'
                    and isinstance(k.value, ast.Constant) and k.value.value == owner for k in n.keywords)
                    for n in ast.walk(methods[0])), owner + ' needs its actual document check')
        verify(owners)
        for fault in ('missing_owner', 'wrong_owner', 'missing_method', 'wrong_method'):
            changed = dict(owners)
            if fault == 'missing_owner': del changed['project']
            elif fault == 'wrong_owner': changed['projects'] = changed.pop('project')
            elif fault == 'missing_method': changed['project'] = (*changed['project'][:2], 'missing')
            else: changed['project'] = ('unit/test_trust_environment.py', 'ToolchainRecordTests',
                                      'test_current_environment_is_verified_from_record_identity_and_fingerprint')
            reason = ('document owner population differs' if fault in ('missing_owner', 'wrong_owner') else
                      'project needs assigned method' if fault == 'missing_method' else
                      'project needs its actual document check')
            with self.subTest(fault=fault), self.assertRaisesRegex(AssertionError, reason):
                verify(changed)

    def test_wait_fields_require_actual_condition_input_and_dispatch_wait(self):
        schemas = field_schemas()
        from support.doc_code import WAIT_BOUNDARIES, wait_field_issues
        for owner, token in (('change', 'change.value'), ('plan_settle_wait', 'plan_settle_wait.kind')):
            for text in ('`' + token + '`', '`result.' + token.split('.')[1] +
                         '` <!-- do-math fields: result=' + owner + ' -->'):
                with self.subTest(text=text), self.assertRaisesRegex(ValueError, 'actual wait boundary'):
                    scoped_field_issues(text, schemas)
                with self.assertRaisesRegex(ValueError, 'actual wait boundary'):
                    scoped_field_issues(text, schemas, defer_waits=set(WAIT_BOUNDARIES) - {owner})
                self.assertEqual(scoped_field_issues(text, schemas, defer_waits=(owner,)), [])
                self.assertEqual(unowned_field_references(text, schemas), [])
        with self.assertRaisesRegex(ValueError, 'Unknown deferred wait owners'):
            scoped_field_issues('', schemas, defer_waits=('changes',))
        with self.assertRaisesRegex(ValueError, 'actual repository report'):
            scoped_field_issues('`status.budget`', schemas, defer_waits=WAIT_BOUNDARIES)
        self.assertEqual(wait_field_issues('`change.value`', 'change', {}), [('actual field', 'change.value')])
        self.assertEqual(wait_field_issues('`dispatch_wait.kind` <!-- do-math fields: dispatch_wait=plan_settle_wait -->',
            'plan_settle_wait', {}), [('actual field', 'dispatch_wait.kind')])

    def test_deferred_waits_have_the_assigned_actual_document_check(self):
        import ast
        from support.doc_code import WAIT_BOUNDARIES
        owners = {
            'change': ('unit/test_planning_conditions.py', 'ReadinessConditionTests',
                       'test_documented_decision_value_uses_real_input_and_exact_types'),
            'plan_settle_wait': ('sim/test_scheduling_session_slots.py', 'PlanSettleTests',
                                'test_documented_wait_is_the_actual_queue_value_until_the_exact_limit')}
        def verify(mapping):
            self.assertEqual(set(mapping), set(WAIT_BOUNDARIES), 'document owner population differs')
            for owner, (path, cls_name, method) in mapping.items():
                tree = ast.parse((SCRIPTS / 'tests' / path).read_text(encoding='utf-8'))
                cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == cls_name)
                methods = [n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == method]
                self.assertEqual(len(methods), 1, owner + ' needs assigned method')
                self.assertTrue(any(isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
                    and n.func.id == 'assert_wait_documents' and any(k.arg == 'owner'
                    and isinstance(k.value, ast.Constant) and k.value.value == owner for k in n.keywords)
                    for n in ast.walk(methods[0])), owner + ' needs its actual document check')
        verify(owners)
        for fault in ('missing_owner', 'wrong_owner', 'missing_method', 'wrong_method'):
            changed = dict(owners)
            if fault == 'missing_owner': del changed['change']
            elif fault == 'wrong_owner': changed['changes'] = changed.pop('change')
            elif fault == 'missing_method': changed['change'] = (*changed['change'][:2], 'missing')
            else: changed['change'] = (*changed['change'][:2], 'test_readiness_document_tables_match_the_condition_grammar')
            reason = ('document owner population differs' if fault in ('missing_owner', 'wrong_owner') else
                      'change needs assigned method' if fault == 'missing_method' else
                      'change needs its actual document check')
            with self.subTest(fault=fault), self.assertRaisesRegex(AssertionError, reason):
                verify(changed)

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
            self.assertEqual(set(mapping), set(GOVERNANCE_BOUNDARIES), 'document owner population differs')
            for owner, (path, class_name, method) in mapping.items():
                tree = ast.parse((SCRIPTS / 'tests' / path).read_text(encoding='utf-8'))
                cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == class_name)
                methods = [n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == method]
                self.assertEqual(len(methods), 1, owner + ' needs assigned method')
                self.assertTrue(any(isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
                    and n.func.id == 'assert_governance_documents' and any(k.arg == 'owner'
                    and isinstance(k.value, ast.Constant) and k.value.value == owner for k in n.keywords)
                    for n in ast.walk(methods[0])), owner + ' needs its actual document check')
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
            reason = ('document owner population differs' if fault in ('missing_owner', 'wrong_owner') else
                      'import_check needs assigned method' if fault == 'missing_method' else
                      'import_check needs its actual document check')
            with self.subTest(fault=fault), self.assertRaisesRegex(AssertionError, reason):
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
            self.assertEqual(set(mapping), set(DELIVERY_INPUT_BOUNDARIES), 'document owner population differs')
            for owner, (path, class_name, name) in mapping.items():
                tree = ast.parse((SCRIPTS / 'tests' / path).read_text(encoding='utf-8'))
                cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == class_name)
                methods = [n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == name]
                self.assertEqual(len(methods), 1, owner + ' needs assigned method')
                self.assertTrue(any(isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
                    and n.func.id == 'assert_delivery_documents' and any(k.arg == 'owner'
                    and isinstance(k.value, ast.Constant) and k.value.value == owner for k in n.keywords)
                    for n in ast.walk(methods[0])), owner + ' needs its actual document check')
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
            reason = ('document owner population differs' if fault in ('missing_owner', 'wrong_owner') else
                      'repair needs assigned method' if fault == 'missing_method' else
                      'repair needs its actual document check')
            with self.subTest(fault=fault), self.assertRaisesRegex(AssertionError, reason):
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
            self.assertEqual(set(mapping), set(REVIEW_INPUT_BOUNDARIES), 'document owner population differs')
            for owner, (path, class_name, name) in mapping.items():
                tree = ast.parse((SCRIPTS / 'tests' / path).read_text(encoding='utf-8'))
                cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == class_name)
                methods = [n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == name]
                self.assertEqual(len(methods), 1, owner + ' needs assigned method')
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
            reason = ('document owner population differs' if fault in ('missing_owner', 'wrong_owner') else
                      'review_sources needs assigned method' if fault == 'missing_method' else
                      'review_sources needs its actual document check')
            with self.subTest(fault=fault), self.assertRaisesRegex(AssertionError, reason):
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
                        defer_tool_inputs=set(TOOL_INPUT_BOUNDARIES) - {owner}, defer_review_inputs=('role_review', 'pending_findings', 'review_research', 'review_sources'), defer_delivery_inputs=('submission_check', 'repair'), defer_governance=('import_payload', 'import_check', 'governance', 'academic_validation'), defer_waits=('change', 'plan_settle_wait'), defer_trust=('project', 'toolchain', 'environment_check'))
                self.assertEqual(scoped_field_issues('`' + field + '`', schemas,
                                 defer_tool_inputs=(owner,), defer_review_inputs=('role_review', 'pending_findings', 'review_research', 'review_sources'), defer_delivery_inputs=('submission_check', 'repair'), defer_governance=('import_payload', 'import_check', 'governance', 'academic_validation'), defer_waits=('change', 'plan_settle_wait'), defer_trust=('project', 'toolchain', 'environment_check')), [])
        with self.assertRaisesRegex(ValueError, 'Unknown deferred tool input owners'):
            scoped_field_issues('', schemas, defer_tool_inputs=('preveiw',), defer_review_inputs=('role_review', 'pending_findings', 'review_research', 'review_sources'), defer_delivery_inputs=('submission_check', 'repair'), defer_governance=('import_payload', 'import_check', 'governance', 'academic_validation'), defer_waits=('change', 'plan_settle_wait'), defer_trust=('project', 'toolchain', 'environment_check'))
        for text in ('`status.budget`', '`results[].report`', '`operational_evidence.checkpoint_source`'):
            with self.assertRaisesRegex(ValueError, 'fields require the actual'):
                scoped_field_issues(text, schemas, defer_tool_inputs=TOOL_INPUT_BOUNDARIES, defer_review_inputs=('role_review', 'pending_findings', 'review_research', 'review_sources'), defer_delivery_inputs=('submission_check', 'repair'), defer_governance=('import_payload', 'import_check', 'governance', 'academic_validation'), defer_waits=('change', 'plan_settle_wait'), defer_trust=('project', 'toolchain', 'environment_check'))

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
            self.assertEqual(set(owners), set(TOOL_INPUT_BOUNDARIES), 'tool owner population differs')
            self.assertLessEqual(set(owners), set(calls), 'tool document consumer missing: ' + repr(set(owners) - set(calls)))
        verify(TOOL_INPUT_BOUNDARIES)
        for changed in (set(TOOL_INPUT_BOUNDARIES) - {'preview'},
                        (set(TOOL_INPUT_BOUNDARIES) - {'preview'}) | {'preveiw'}):
            with self.assertRaisesRegex(AssertionError, 'tool owner population differs'):
                verify(changed)
        calls.remove('scholarly')
        with self.assertRaisesRegex(AssertionError, "tool document consumer missing:.*scholarly"):
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
            self.assertEqual(set(mapping), set(RESULT_INPUT_BOUNDARIES), 'document owner population differs')
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
            reason = ('document owner population differs' if fault in ('missing_owner', 'wrong_owner') else
                      'results needs assigned method' if fault == 'missing_method' else
                      'research_sources needs its actual document check')
            with self.subTest(fault=fault), self.assertRaisesRegex(AssertionError, reason):
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
                                                                     'record_map.read_tool', 'submission_contract'), defer_review_inputs=('role_review', 'pending_findings', 'review_research', 'review_sources'), defer_delivery_inputs=('submission_check', 'repair'), defer_governance=('import_payload', 'import_check', 'governance', 'academic_validation'), defer_waits=('change', 'plan_settle_wait'), defer_trust=('project', 'toolchain', 'environment_check'))]
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


    def test_operating_summary_and_operational_input_keep_their_owners(self):
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
        # Explicit calls use the existing function checker; bare names stay fields.
        self.assertEqual(governance_field_issues('`governance.apply_decision(...)`에서 생산한다.', 'governance', {}), [])
        self.assertEqual(function_reference_issues('`governance.apply_decision(...)`에서 생산한다.'), [])
        for token in ('governance.charter', 'governance.apply_decison', 'governance.apply_decision'):
            self.assertEqual(governance_field_issues('`' + token + '`', 'governance', {}),
                             [('actual field', token)])
        for token in ('governance.apply_decision', 'governance.apply_decison'):
            self.assertEqual(governance_field_issues('`' + token + '`에서 생산한다.', 'governance', {}),
                             [('actual field', token)])
        self.assertEqual(function_reference_issues('`governance.apply_decison(...)`에서 생산한다.'),
                         [('function reference', 'governance.apply_decison(...)')])
        self.assertEqual(governance_field_issues(
            '`view.apply_decision` <!-- do-math fields: view=governance -->', 'governance', {}),
            [('actual field', 'view.apply_decision')])
        from support.doc_code import delivery_field_issues
        self.assertEqual(delivery_field_issues('`check.sha256` <!-- do-math fields: check=submission_check -->',
                         'submission_check', {'passed': True}), [('actual field', 'check.sha256')])
        with self.assertRaisesRegex(ValueError, 'actual trust boundary'):
            scoped_field_issues('`toolchain.project.search_paths` `environment_check.changed_files`', schemas)
        from support.doc_code import wait_field_issues
        self.assertEqual(wait_field_issues('`change.value`', 'change', {'value': True}), [])
        self.assertEqual(wait_field_issues('`change.nonexistent`', 'change', {'value': True}),
                         [('actual field', 'change.nonexistent')])
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
