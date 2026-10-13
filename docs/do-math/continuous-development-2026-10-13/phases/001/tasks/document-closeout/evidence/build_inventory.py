"""Serialize the reviewed binding inventory and bounded packet proposals.

Only stdlib source inspection is performed; this is not a product checker.
"""
import ast
import hashlib
import json
from pathlib import Path
import re

REPO = Path('C:/math')
OUT = Path(__file__).resolve().parent
SKILL = '.claude/skills/do-math/'
SCRIPTS = SKILL + 'scripts/'
DOC_CODE = 'repo:' + SCRIPTS + 'tests/support/doc_code.py'
ORIGINAL = 'repo:docs/do-math/시험-재편-2026-09-29/조사/결함-범주.md'
TABLE = 'repo:docs/do-math/시험-재편-2026-09-29/단계-전환표-2026-10-03.json'
CENSUS = json.loads((OUT / 'source-census.json').read_text(encoding='utf-8'))
SOURCES = {}


def save(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def location(path, symbol=None):
    source = (REPO / path).read_text(encoding='utf-8-sig')
    SOURCES[path] = hashlib.sha256((REPO / path).read_bytes()).hexdigest()
    result = {'path': 'repo:' + path}
    if symbol:
        matches = []
        def walk(nodes, prefix=''):
            for node in nodes:
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    qualified = prefix + node.name
                    if symbol in (node.name, qualified):
                        matches.append((node, qualified))
                    walk(node.body, qualified + '.')
        walk(ast.parse(source).body)
        assert len(matches) == 1, (path, symbol, len(matches))
        node, qualified = matches[0]
        result.update(symbol=qualified, line=node.lineno, end_line=node.end_lineno)
    return result


def producer(file, symbol):
    return location(SCRIPTS + 'do_math/' + file, symbol)


def test(file, symbol=None):
    return location(SCRIPTS + 'tests/' + file, symbol)


STRUCT = test('structure/test_doc_code.py', 'test_documented_scoped_fields_belong_to_their_actual_schema')
ROWS = []


def add(owner, definition, mode, producers, tests=(), *, lines=(), ast_lines=(), packet=None, detail='', dependencies=()):
    docs = [{k: v for k, v in row.items() if k in ('document', 'line', 'token', 'text', 'aliases')}
            for row in CENSUS['field_occurrences'] if row['category'] == 'field' and row['owner'] == owner]
    ROWS.append({'owner': owner, 'definition': definition, 'mode': mode,
        'binding_source': {'path': DOC_CODE, 'lines': list(lines)},
        'ast_sites': list(ast_lines), 'documents': docs, 'producers_or_contracts': producers,
        'existing_tests': list(tests) or [STRUCT], 'dependencies': list(dependencies),
        'decision': 'retain' if not packet else 'replace_bounded_binding', 'next_packet': packet,
        'assessment': detail or '정본 정의의 이름/경로 검사로 유지한다. 필드 값과 권한·정책 의미의 전건 검증을 뜻하지 않는다.',
        'evidence_kind': 'current source inspection; existing tests located, no tests run by this task'})


def build_rows():
    record = location(SCRIPTS + 'do_math/record_schemas/schemas.py')
    state = producer('state_contract.py', 'default_state_contract')
    contract = location(SCRIPTS + 'do_math/contracts.py')
    for name, definition in {
        'config': 'config_schema()', 'action': "RECORDS['queue']", 'task': "RECORDS['tasks']",
        'execution': "RECORDS['executions']", 'profile': "RECORDS['execution_profiles']",
        'lifecycle': "RESEARCH_FIELDS['lifecycle']", 'runtime': "default_state_contract families rooted at runtime",
        'instance': "default_state_contract families rooted at research", 'formal_result': "RECORDS['formal_results']",
        'execution_to_review': "RECORDS['executions']"}.items():
        add(name, definition, 'shared_contract', [record, state], lines=(250, 258),
            detail=('직접 문서 참조·하위 결속·현재 문서 시험의 명시적 소비가 확인되지 않았다. instance 이름과 research-root 조립은 제거 후보이며 runtime 등 살아 있는 정본 참조는 보존한다.'
                    if name=='instance' else '직접 점 경로 문서가 없어도 하위 결속 또는 저장/역할 구분 반례가 소비한다. 제거 대상이 아니다.'
                    if name in ('config','execution','profile') else '저장 스키마와 역할 입력을 구별하는 정본 참조로 유지한다.'))
        if name=='instance':
            ROWS[-1]['decision']='remove_candidate_no_explicit_consumer'
    for name, parent, key in (
        ('ai','profile','ai'), ('assessment','task','assessment'), ('scope','task','scope'),
        ('expected','task','expected'), ('immutable_input','lifecycle','immutable_input'),
        ('maintenance_fence','runtime','maintenance_fence'), ('session_limits','config','session_limits')):
        add(name, f'{parent}.properties.{key}', 'shared_contract', [record], lines=(263,), dependencies=(parent,))
    direct = {
        'revisit': (270, 'PLAN_DISPOSITION.properties.revisit', contract),
        'activation': (272, 'RESEARCH_FIELDS.lifecycle.activation', record),
        'disposition': (273, 'contracts.disposition_schema()', contract),
        'observation': (274, 'RECORDS.execution_profiles.observation', record),
        'user_request': (276, 'RECORDS.inputs', record),
        'governance_record': (277, 'RECORDS.governance', record),
        'governance_content': (278, 'RECORDS.governance.content', record),
        'subject': (297, 'RECORDS.executions.observation_rules.items.subject', record),
        'source_range': (298, 'governance.interpretation_schema(interpret).import_units.items.source_range', producer('governance.py','interpretation_schema')),
        'candidates': (317, 'contracts.schema_for(research_preparation).candidates', contract),
        'task_assessments': (318, 'contracts.schema_for(research_plan).task_assessments', contract),
        'item_dispositions': (319, 'task_assessments.items.item_dispositions', contract),
        'question_details': (323, 'governance.interpretation_schema(interpret).question_details', producer('governance.py','interpretation_schema')),
        'external_rejections': (324, 'array(RECORDS.external_rejections)', record),
    }
    for owner, (line, definition, source) in direct.items():
        add(owner, definition, 'shared_contract', [source], lines=(line,))
    for owner in ('task_conditions','knowledge_changes','revision_resolutions','contract_checks'):
        add(owner, 'submission.extension_schema(research_preparation).properties.' + owner,
            'shared_contract', [producer('submission.py','extension_schema')], lines=(320,321))
    for owner, line, module, definition in (
        ('role_tiers',275,'model_policy.py','ROLE_TIERS'),
        ('candidate_record',279,'knowledge_io.py','_KNOWLEDGE_FIELDS'),
        ('worker_feedback',301,'observations.py','WORKER_FEEDBACK_FIELDS')):
        add(owner, definition, 'shared_vocabulary_projection', [location(SCRIPTS+'do_math/'+module)], lines=(line,),
            detail='제품의 공유 목록을 키로 투영하는 이름 검사다. 현재 문서 소비가 있으므로 유지하며 값의 의미나 실제 전달을 인증하지 않는다.')

    # Existing replacements: keep exact scope. record_map.read_tool is separate from its closed base.
    add('record_map','context_store.record_map actual base + install_tools.read_tool AST','mixed_actual_and_ast',
        [producer('context_store.py','record_map'),producer('submission.py','install_tools')],
        [test('structure/test_doc_code.py','test_role_input_fields_do_not_borrow_names_from_the_stored_execution'),
         test('unit/test_submission_preview_commands.py','test_worker_commands_use_the_console_interpreter_when_the_engine_runs_windowless')],
        lines=(351,353),ast_lines=(353,),packet='P03',
        detail='B119의 실제 record_map 기본 키는 유지한다. read_tool만 설치 후 실제 객체/파일 경계에 옮긴다. DOC-RETURN-PURE를 다시 배정하지 않는다.')
    add('operating_summary','reporting.operating_summary(current_state()) + fixed supervision keys','actual_pure_sample',
        [producer('reporting.py','operating_summary')],
        [test('structure/test_doc_code.py','test_explicit_producer_composition_keeps_owners_and_rejects_stale_bindings')],
        lines=(356,359,363),detail='B120 유지. 초기화 표본의 최상위와 supervision만 근거다. primary_blocker 내부나 빈 grants 원소를 추론하지 않는다.')
    boundary = {
        'status': ('reporting.py','status_report','unit/test_storage_report_projections.py','test_human_report_preserves_loaded_initialization_blocker_and_machine_finding','B121/B131'),
        'operation_progress': ('trace_report.py','progress','unit/test_engine_trace_report_corruption.py','test_unreadable_error_sidecar_has_bounded_explicit_status','B122'),
        'query_record': ('core_engine.py','_query_record','unit/test_storage_record_queries.py','test_query_family_names_are_the_condition_grammar_names','B130'),
        'query_result': ('cli.py','execute','boundary/test_engine_cli.py','test_query_read_export_and_check_use_a_fixed_repository_snapshot','B130'),
        'init_result': ('cli.py','execute','boundary/test_engine_cli.py','test_original_request_is_preserved_separately_from_the_mathematical_goal','B131'),
        'scheduling_result': ('cli.py','execute','boundary/test_engine_cli.py','test_original_request_is_preserved_separately_from_the_mathematical_goal','B131'),
        'selection_result': ('cli.py','execute','boundary/test_engine_cli.py','test_profile_selection_respects_the_role_floor_without_model_execution','B131'),
        'input_manifest': ('context_store.py','prepare_role_input','unit/test_role_input_packaging.py','test_role_input_uses_current_schema_documents_and_private_resume_bytes','B132'),
        'prompt': ('context_store.py','prepare_role_input','unit/test_role_input_packaging.py','test_role_input_uses_current_schema_documents_and_private_resume_bytes','B132'),
        'documents': ('context_store.py','prepare_role_input','unit/test_role_input_packaging.py','test_role_input_uses_current_schema_documents_and_private_resume_bytes','B132'),
        'result_source': ('context_store.py','restore_continuation','unit/test_role_input_packaging.py','test_multihop_restores_latest_file_and_stage_evidence','B133'),
        'rejected_response': ('context_store.py','restore_continuation','unit/test_role_input_packaging.py','test_multihop_restores_latest_file_and_stage_evidence','B133'),
        'previous_output_files': ('context_store.py','restore_continuation','unit/test_role_input_packaging.py','test_multihop_restores_latest_file_and_stage_evidence','B133'),
        'profile_selection': ('context_store.py','prepare_role_input','unit/test_role_input_packaging.py','test_candidate_population_is_compact_profile_bound_and_reproducible','B134'),
    }
    for owner,(file,symbol,tf,method,history) in boundary.items():
        add(owner, history + ' actual return boundary sentinel', 'actual_boundary', [producer(file,symbol)],
            [test(tf,method)],lines=(27,33,35,37,283,285,286,287,306,368,369),
            detail=history+'의 지정 실제 반환 검사를 유지한다. 문서 구조 검사의 defer는 이 생산자 제공 시험으로만 보완한다.'+
            (' 단 계약/운영-점검.md:21은 다른 생산자이며 P01에서 해당 문서 결속만 교정한다.' if owner=='result_source' else ''))

    op = [producer('core_engine.py','CoreEngineMixin._context')]
    op_tests = [test('sim/test_role_input_context.py','test_live_review_receives_the_already_sealed_target_checkpoint'),
                test('sim/test_role_input_context.py','test_large_checkpoint_stays_readable_without_becoming_mandatory_prompt_text'),
                test('sim/test_role_input_context.py','test_live_review_receives_exact_checkpoint_evidence_files'),
                test('sim/test_knowledge_currentness.py','test_failed_execution_materials_are_restored_for_its_operational_review'),
                test('sim/test_knowledge_currentness.py','test_recovery_captures_parent_and_inline_child_without_losing_action'),
                test('flows/test_knowledge_impact_retry.py','test_an_unreadable_held_submission_is_consumed_once_before_its_review_is_prepared')]
    for owner, sites, definition in (
        ('checkpoint_source',(282,), '_context operational_evidence.checkpoint_source; 문서 21행 recovery_materials와 현재 혼동'),
        ('recovery_source',(284,), '_context.recover 정상/진단 반환; 독립 문서 루트는 없고 두 하위 결속이 소비'),
        ('checkpoint_files',(332,), '_context operational_evidence.checkpoint_files + stored evidence_files'),
        ('recovered_output_files',(), 'array(recovery_source); 실제 출력에는 entry와 recover가 합성됨'),
        ('recovery_materials',(335,), '_context recovery_materials; output_files만 수동 recovery_source 연결'),
        ('operational_evidence',(370,371), '_context evidence + activity_continuations 수동 조립')):
        add(owner,definition,'ast_or_manual_composition',op,op_tests,lines=sites or (334,),ast_lines=sites,packet='P01',
            dependencies=('recovery_source',) if owner in ('recovered_output_files','recovery_materials') else (),
            detail='실제 운영 점검 입력/복원 파일 경계로 교체한다. 정상 local_path, 진단 restoration_error, checkpoint 부재/null을 같은 생산자의 구별된 경우로 검증한다. 일반 재개 결과에서 이름을 빌리지 않는다.')

    files_tests=[test('sim/test_role_input_context.py','test_task_result_paths_survive_packaging_without_entering_validation_hashes'),
                 test('sim/test_role_input_context.py','test_planning_keeps_completed_report_and_active_work_as_readable_context'),
                 test('unit/test_context_catalog.py','test_new_catalog_is_hashed_from_the_bytes_it_wrote'),
                 test('sim/test_submission_receiver.py','test_independent_bundle_does_not_repeat_the_task_report'),
                 test('flows/test_submission_acceptance.py','test_large_accepted_report_survives_revision_review_and_resumed_work')]
    for owner,sites,definition,prod in (
        ('source_ref',(292,),'write_source_catalog.ref',producer('context_store.py','write_source_catalog')),
        ('materialized_output_files',(327,328),'_preserve_outputs stored_file -> _context restored_file',producer('core_engine.py','CoreEngineMixin._context')),
        ('research_sources',(330,),'_context sources + RECORDS.sources',producer('core_engine.py','CoreEngineMixin._context')),
        ('results',(341,),'_apply research output filter + _context restored output_files',producer('core_engine.py','CoreEngineMixin._apply'))):
        add(owner,definition,'ast_or_manual_composition',[prod],files_tests,lines=sites,ast_lines=sites,packet='P02',
            dependencies=('materialized_output_files',) if owner=='results' else (),
            detail='저장 과제 결과와 역할에 지급된 원문/파일의 경계를 검증한다. stored_file·retained·result 조립을 함께 제거하되 B133 previous_output_files는 재구현하지 않는다.')
    tools_tests=[test('unit/test_submission_preview_commands.py','test_worker_commands_use_the_console_interpreter_when_the_engine_runs_windowless'),
                 test('sim/test_role_input_context.py','test_runner_takes_its_tools_only_from_the_pinned_profile'),
                 test('sim/test_role_input_context.py','test_self_check_evidence_follows_the_submission_citation_rule'),
                 test('sim/test_knowledge_project_identity.py','test_project_identity_bounds_role_input_and_detects_file_changes')]
    for owner,sites,definition in (
        ('execution_window',(348,), '_context execution_window'),('scholarly',(348,), '_context scholarly + pinned profile update'),
        ('formal_verifier',(348,), '_context formal_verifier + install_tools.preview'),
        ('preview',(349,), 'install_tools formal_verifier.preview'),('submission_contract',(355,), 'install_tools final contract')):
        add(owner,definition,'ast_or_manual_composition',
            [producer('core_engine.py','CoreEngineMixin._context'),producer('submission.py','install_tools'),producer('context_store.py','prepare_role_input')],
            tools_tests,lines=sites,ast_lines=sites,packet='P03',
            detail='준비 완료/도구 설치 이후 실제 입력과 생성 도구 파일에 결속한다. configured/command 존재를 학술 호출이나 Lean 검증 성공으로 세지 않는다.')

    review_stage_tests=[test('unit/test_review_cycle_stages.py','test_initial_barrier_and_blindness'),
                        test('unit/test_review_cycle_stages.py','test_judge_new_findings_get_organizer_assignment_and_answer')]
    for owner,site,symbol in (('role_review',294,'context_for'),('pending_findings',325,'_add_findings')):
        add(owner,'review_cycle.'+symbol,'ast_or_manual_composition',[producer('review_cycle.py',symbol)],review_stage_tests,
            lines=(site,),ast_lines=(site,),packet='P04',
            detail='실제 context_for 결과의 proposal/pending_findings를 재사용한다. _add_findings의 내부 사전 대입만으로 최종 지급을 주장하지 않는다.')
    research_tests=[test('unit/test_review_research_owner_contract.py','test_fixed_question_context_keeps_original_bytes_after_unrelated_publication'),
                    test('unit/test_review_research_owner_contract.py','test_prepared_source_uses_its_snapshot_after_head_advances'),
                    test('boundary/test_review_source_restoration.py')]
    for owner,site,symbol in (('review_research',293,'_review_research_context'),('review_sources',346,'_materialize_research_sources')):
        add(owner,'review_engine.'+symbol,'ast_or_consumed_shape',[producer('review_engine.py',symbol)],research_tests,
            lines=(site,),ast_lines=(site,),packet='P05',
            detail='고정 질문의 실제 materialized sources를 사용한다. review_sources는 현재 source를 읽은 키이므로 반환 보장의 근거가 아니다. 연구 원자료와 별도 소유자다.')
    imports_tests=[test('unit/test_governance_imports.py','test_import_check_must_resolve_a_real_execution_and_bound_input'),
                   test('unit/test_governance_imports.py','test_unapproved_or_stale_import_cannot_change_charter'),
                   test('unit/test_governance_imports.py','test_initial_configuration_keeps_its_owner_through_completion')]
    for owner,sites,symbol in (('import_payload',(299,),'validate_import_units'),('import_check',(303,305),'check_import')):
        add(owner,'governance.'+symbol,'ast_or_consumed_shape',[producer('governance.py',symbol)],imports_tests,
            lines=sites,ast_lines=sites,packet='P06',detail='import_payload.kind는 소비 계약, import_check.sha256는 독립 점검 실제 결과다. 두 의미와 submission_check를 합치지 않는다.')
    subtests=[test('unit/test_submission_checks.py','test_machine_checks_compare_exact_inputs_and_preserve_skipped_checks'),
              test('sim/test_repair_routing.py','test_a_rejected_submission_travels_with_the_repair')]
    for owner,site,file,symbol in (('submission_check',302,'submission.py','check_submission'),
                                 ('repair',280,'repair_execution.py','route_submission_return')):
        add(owner,file+':'+symbol,'ast_selected_object',[producer(file,symbol)],subtests,
            lines=(site,),ast_lines=(site,),packet='P07',detail='실제 제출 검사 결과와 같은 제출의 생산자 수리 전달을 사용한다. 반려 전/후 체크와 import 점검은 다른 소유자다.')
    trust_tests=[test('sim/test_toolchain_tools.py','test_identity_detects_executable_checker_and_project_input_changes'),
                 test('boundary/test_knowledge_lean_verifier.py','test_lake_search_paths_are_observed_once_per_unchanged_project_input'),
                 test('boundary/test_knowledge_lean_verifier.py','test_inspection_matches_actual_formal_verifier'),
                 test('unit/test_trust_environment.py','test_live_admission_tracks_added_and_removed_judgment_files_but_ignores_notes')]
    for owner,sites,file,symbol in (('project',(307,308),'formal.py','_project_identity'),
        ('toolchain',(309,),'formal.py','inspect_toolchain'),('environment_check',(311,312,313),'trust_validation.py','check_environment')):
        add(owner,file+':'+symbol,'ast_or_manual_composition',[producer(file,symbol)],trust_tests,
            lines=sites,ast_lines=sites,packet='P08',detail='project의 비-Lake null과 성공 경로, check_environment의 verified/rebind/invalid 변형을 구별한다. observed identity와 승인 성공은 같지 않다.')
    add('change','planning.evaluate_condition.visit decision.change reads','consumed_shape',
        [producer('planning.py','evaluate_condition')],
        [test('unit/test_planning_conditions.py','test_conditions_and_errors_preserve_basis'),
         test('unit/test_planning_conditions.py','test_readiness_document_tables_match_the_condition_grammar')],
        lines=(300,),ast_lines=(300,),packet='P09',detail='선택적 소비 키는 출력 스키마가 아니다. decision change의 실제 생산/수신 계약에서 value 읽기의 조건을 검증한다.')
    for owner,site,file,symbol,tf,method in (
        ('governance',366,'governance.py','governance_view','unit/test_governance_records.py','test_initialized_charter_is_single_authority_and_binds_approved_original'),
        ('academic_validation',367,'academic.py','academic_status','unit/test_academic_requirements.py','test_unsolved_not_applicable')):
        add(owner,file+':'+symbol,'ast_selected_return',[producer(file,symbol)],[test(tf,method)],
            lines=(site,),ast_lines=(site,),packet='P10',detail='두 고정 문서 경로 charter/status를 기존 순수 반환에 연결한다. 전체 학술 상태 의미 재감사를 추가하지 않는다.')
    add('plan_settle_wait',"DispatchEngineMixin._plan_settle_waits action['dispatch_wait']",'ast_selected_object',
        [producer('dispatch_engine.py','_plan_settle_waits')],
        [test('sim/test_scheduling_session_slots.py','test_a_plan_waits_for_pending_contract_reviews_so_nearby_approvals_share_one_decision'),
         test('sim/test_scheduling_session_slots.py','test_the_settle_wait_ends_at_its_configured_limit')],
        lines=(291,),ast_lines=(291,),packet='P11',detail='13-C D-06 의미 대조와 함께 실제 dispatch_wait에 연결한다. 대기 이름 존재만으로 최초 준비/명시 요청/회복 예외를 증명하지 않는다.')


def build_packets():
    descriptions = {
        'P01': ('운영 증거와 종료 후 복구', 'DOC-RETURN-ROLE',
            '실행 중/종료 후의 봉인 checkpoint·근거 파일과 정상/체크포인트/활동 결과를 기존 _context 및 포장 결과에서 확인한다.',
            '정상 local_path 한 항목 삭제, 위조 해시/크기, 복원 불가 restoration_error, checkpoint_source=None, live_review에서 recovery_materials 부재를 구별한다. 운영 문서 15/21행과 일반 재개 문서 45행을 서로 바꿔 검증하면 실패해야 한다.',
            '운영-점검.md의 모호한 result_source/checkpoint_source를 operational_evidence/recovery_materials의 명시 경로로 교정하고 해당 경로를 그 실제 객체에 결속한다. 정상/진단/부재 조건도 문장과 일치해야 한다. B133의 정상 재개/반려/이전 파일 경계는 유지한다.'),
        'P02': ('원자료·과제 결과와 물질화된 파일', 'DOC-RETURN-ROLE',
            '기존 catalog 및 포장 시험의 실제 source_ref, sources, task.results, restored output_files와 원문 바이트를 확인한다.',
            '다른 실행/원자료의 local_path 차용, 결과 report 또는 한 파일 local_path 삭제, 빈 배열, 저장 execution에 local_path를 붙여 대신 검증하는 경우를 거부한다.',
            '생산 출력의 보존 필터와 저장→역할 입력의 실제 연결을 재사용해 stored_file/retained/result 문자열 조립을 제거한다. 현재 포장 시험의 수제 result는 물질화 근거다. _apply 생산·중복 방지는 기존 sim 수신 시험과 flows.test_submission_acceptance의 600k 보고/증거 파일 재개 검증으로 연결하며 새 장기 엔진 경로를 만들지 않는다.'),
        'P03': ('실행 안내와 설치 도구', 'DOC-RETURN-ROLE',
            '실제 _context 실행 창·고정 프로필의 scholarly 및 install_tools 후 formal_verifier.preview/record_map.read_tool/submission_contract를 확인한다.',
            '실제 최종 입력에서 self_check_directory/command/checkpoint_bytes/max_artifact_bytes 삭제, 미설치 preview, 다른 도구 command 차용, windowless interpreter 거부를 확인한다.',
            '기존 준비/도구 설치 시험을 확장해 최종 fitted 또는 정확한 참조 파일을 읽는다. record_map 기본 실제 반환은 보존하고 여기서는 read_tool만 교체한다.'),
        'P04': ('검토 자리 입력', 'DOC-RETURN-REVIEW',
            'context_for의 실제 scope/initial 및 finding이 열린 answer/judge 결과에서 proposal과 pending_findings[].ref를 확인한다.',
            '숨긴 동료 판단 유출, 빈 findings로 ref를 추론, 다른 stage/record의 ref 차용, 실제 한 원소 ref 삭제를 거부한다.',
            'context_for/_add_findings AST와 identity_basis/policy_ref 수동 comprehension 결속을 제거하고 기존 단계/봉인 시험의 반환에 연결한다.'),
        'P05': ('고정 질문과 보충 조사 원자료', 'DOC-RETURN-REVIEW',
            '기존 _review_research_context 및 _materialize_research_sources의 고정 질문·source ref·snapshot·실제 파일을 사용한다.',
            'proposal/digest 변경, 원자료 바이트 손상/부재, 반환 ref 삭제, research_sources의 키 차용을 거부한다.',
            'review_research와 review_sources를 실제 반환에 연결하고 소비 키 수집을 반환 스키마로 쓰는 결속을 제거한다. 원자료 예외를 없애 정상화하지 않는다.'),
        'P06': ('수입 payload와 독립 점검 결과', 'DOC-RETURN-REVIEW',
            '실제 수입 생산/수신의 payload.kind와 check_import 반환 sha256를 기존 승인·수리 시험에서 확인한다.',
            'kind 부재/다른 unit 종류, 자기 점검·오래된 입력, 실제 sha256 삭제, submission_check.passed 차용을 거부한다.',
            '입력 소비 계약은 기존 해석/소유자 정의에 연결하고 import_check의 반환/추가 AST 조립을 실제 결과로 교체한다. 입력과 출력 의무를 분리해서 기록한다.'),
        'P07': ('제출 검사와 반려 전달', 'DOC-RETURN-REVIEW',
            '실제 check_submission의 passed와 route_submission_return이 만든 repair.previous_output을 기존 경계에서 확인한다.',
            'failed/skipped를 성공으로 바꾸기, 이전 원문 유실, import_check.sha256 차용, 실제 passed/previous_output 누락을 거부한다.',
            'result/retry AST를 제거한다. 정상·반려가 실제 동일 제출을 가리키는 증거와 기존 실패·소유자 단언을 유지한다.'),
        'P08': ('도구 사슬·프로젝트와 신뢰 검사', 'DOC-RETURN-TRUST',
            '기존 실제 formal inspection/프로젝트 경계의 source_identity/search_paths와 실제 check_environment의 changed_files를 사용한다.',
            'non-Lake의 project=None, verified/rebind에서 changed_files 부재, 파일 추가/삭제/변경 invalid, nested key 삭제를 조건별로 확인한다.',
            'environment_base 및 project/toolchain 수동 조립을 제거한다. 이름의 변형 모집단을 닫되 실제 Lean/Job 전관문은 gate task 책임으로 남긴다.'),
        'P09': ('조건 평가의 change 소비', 'DOC-RETURN-TRUST',
            'references/과제-착수조건.md:17의 change.value를 현행 decision 변경 형식과 실제 조건 평가에 연결한다.',
            '변경 종류/대상/field가 다른 경우와 value 부재/null의 현행 계약을 구별한다. 소비자가 get으로 읽는다는 이유만으로 무조건 필수 출력으로 만들지 않는다.',
            'visit의 소비 키 추출 하나를 실제 입력 계약/기존 평가 시험에 연결하고 조건 문서 표/JSON 예시 검증은 재사용한다.'),
        'P10': ('헌장과 학술 상태의 두 순수 조회', 'DOC-RETURN-TRUST',
            '현재 헌장 governance.charter와 academic_validation.status를 기존 순수 함수 실제 결과에서 확인한다.',
            '헌장 비유일성, 초기화/목표 미해결 상태와 실제 반환 키 삭제를 구별하고 다른 상태 보고 키를 빌리지 않는다.',
            'governance_view/academic_status의 두 AST 반환 추출을 제거한다. B119~B122의 닫힌 PURE 모집단은 다시 구현하지 않는다.'),
        'P11': ('대기 정책 의미와 plan_settle 결속', '13-C / D-06',
            'CLI-실행-계약.md:234의 대기 조건·최초 준비 설명을 _plan_settle_waits/_dispatchable와 기존 시계 주입 시험에 대조한다.',
            'pending contract review 유무, 제한 전/동일 시각, requested_by/recovery 우회, 처음부터 후보 전부를 기다린다는 잘못된 문장을 구별한다. 원문에 이름만 존재하는 정책도 이름과 의미 판정을 구분한다.',
            'plan_settle_wait를 실제 dispatch_wait에 연결하고 D-06의 조건·예외 표를 종료한다. 아래 5개 lexical policy 후보는 각 문서 문장과 소유자 정의로 분류하되 일반 자연어 정책 엔진을 만들지 않는다.'),
    }
    packets = []
    for identifier,(title,legacy,normal,negative,finish) in descriptions.items():
        rows=[r for r in ROWS if r['next_packet']==identifier]
        docs={(x['document'],x['line']): x for r in rows for x in r['documents']}
        if identifier=='P01':
            for x in CENSUS['field_occurrences']:
                if x['document'].endswith('/계약/운영-점검.md') and x['line']==21:
                    docs[(x['document'],x['line'])] = x
        packet={'id':identifier,'title':title,'legacy_work':legacy,
            'requirement': {'path':ORIGINAL,'lines':[1181,1184,1201,1600,1613]},
            'owners':[r['owner'] for r in rows], 'ast_sites':sorted({n for r in rows for n in r['ast_sites']}),
            'original_document_locations':[{'path':p,'line':n,'text':x['text']} for (p,n),x in sorted(docs.items())],
            'producers':unique([p for r in rows for p in r['producers_or_contracts']]),
            'reuse_tests':unique([t for r in rows for t in r['existing_tests']]),
            'normal':normal,'counterexamples':negative,'exit':finish,
            'remaining':'13-C의 다른 packet과 최종 판본 관문은 별도다. 이 packet의 실제 소유자 외에 새 추론 규칙을 발견하며 범위를 늘리지 않는다.',
            'execution':'manager가 정확한 writes를 배정한 뒤 한 task로 수행. doc_code 및 공유 검사 소비자를 같이 고치므로 제품 변경 task끼리 병렬 실행하지 않는다.',
            'verification':'기존 공식 run_tests.py로 수정 전 반례와 수정 후 직접 관련 시험을 실행하고 원보고/판본을 보존한다. 현재 조사에서는 실행하지 않았다.'}
        if identifier=='P11':
            packet['policy_name_only_candidates']=CENSUS['policy_mentions']
            packet['policy_semantic_boundary']='현재 code에 있는 policy 접미 5개 이름은 존재 검사 유지 판정이다. 이 packet의 의미 수리는 원문 검산 D-06의 plan_settle 조건으로 한정한다. 다른 명시 정책 문장은 N slice에서 해당 소유자 의미로 연결하고, 새 실제 불일치만 별도 finding으로 반환한다.'
        packets.append(packet)
    names = [x for x in CENSUS['all_inline_spans'] if re.fullmatch(r'[a-z][a-z0-9_]*',x['token'])
             or '=' in x['token'] or ('.' in x['token'] and x['token'] not in {r['token'] for r in CENSUS['field_occurrences']})]
    groups = {
        'N01': ['SKILL.md','README.md','GLOSSARY.md','references/CLI-실행-계약.md','references/초기화-운전.md','references/초기화-효율과-정비.md'],
        'N02': [d['path'].removeprefix('repo:'+SKILL) for d in CENSUS['documents']
                if '/references/' in d['path'] and not any(d['path'].endswith('/'+f) for f in ('CLI-실행-계약.md','초기화-운전.md','초기화-효율과-정비.md'))],
        'N03': [d['path'].removeprefix('repo:'+SKILL) for d in CENSUS['documents'] if '/계약/' in d['path']],
    }
    for identifier,docs in groups.items():
        paths=['repo:'+SKILL+d for d in docs]
        candidates=[x for x in names if x['document'] in paths]
        slices=[]
        for path in paths:
            lines=(REPO/path.removeprefix('repo:')).read_text(encoding='utf-8-sig').splitlines()
            headings=[(1,'도입')]+[(i,line) for i,line in enumerate(lines,1) if line.startswith(('## ','### ')) and i!=1]
            for position,(start,title) in enumerate(headings):
                end=headings[position+1][0]-1 if position+1<len(headings) else len(lines)
                if end<start:
                    continue
                matching=[x for x in candidates if x['document']==path and start<=x['line']<=end]
                slices.append({'id':f'{identifier}-{len(slices)+1:03d}', 'document':path,
                    'start_line':start,'end_line':end,'heading':title,
                    'candidate_occurrences':len(matching),'distinct_tokens':sorted({x['token'] for x in matching}),
                    'dispatch_rule':'이 고정 절의 현재 이름·표·코드펜스만 검토한다. 인접 절을 묶을 때도 합집합 원소를 먼저 명시한다.'})
        packets.append({'id':identifier,'title':'고정 문서의 단독/조합 이름 및 역할 산출 이름 판정',
            'legacy_work':'R27 및 R28의 산출 이름 부분','document_partition':paths,
            'candidate_occurrences':len(candidates),'candidate_distinct_tokens':len({x['token'] for x in candidates}),
            'candidate_index':'source-census.json.all_inline_spans (document로 선택; 코드/산문 문맥은 현재 원문에서 읽음)',
            'required_slices':slices,
            'reuse_tests':[test('structure/test_doc_code.py'),test('unit/test_planning_conditions.py','test_readiness_document_tables_match_the_condition_grammar'),
                          test('unit/test_planning_conditions.py','test_documented_readiness_examples_match_the_live_grammar')],
            'normal':'현재 문서에 이름으로 드는 명령·인자·필드·정책·산출 이름을 해당 실제 정의/역할 스키마에 연결한다. 코드펜스 JSON과 표·산문도 해당 파일의 문맥으로 분류한다.',
            'counterexamples':'존재하는 타 역할의 동명 필드, 단독 이름 오타, config.ghost=1 같은 조합, 잘못된 단축 명령을 전역 어휘 존재만으로 통과시키지 않는다.',
            'exit':'각 배정 문서/절의 현재 이름에 정의 또는 구체적 비코드/파일명 제외 사유를 남긴다. 같은 소유자의 dotted 반환 교체는 P01~P11 결과를 참조하고 재구현하지 않는다.',
            'remaining':'이 lexical 후보 수는 전체 요구 이름의 분모가 아니다. 코드펜스/산문을 살펴 누락을 분류한 뒤 각 파일 판정을 닫는다. 전체24파일의 배정 합집합과 중복을 manager가 대조한다.'})
    packets.append({'id':'L01','title':'실제 운전 읽기 경계의 비교 가능한 한도 확정','legacy_work':'R28 읽기 한도',
        'source':TABLE,'history_pointer':'current_work.independent_schema_boundary_followup.reading_boundary_review',
        'fixed_input':[location(SKILL+'SKILL.md'),producer('contracts.py','reading_map'),producer('contracts.py','render_prompt'),
                       producer('context_store.py','prepare_role_input'),location(SCRIPTS+'do_math/cli_worker.py')],
        'normal':'기존 10역할 문서→stdin 전달과 운전자의 순차·구간 읽기를 재사용한다. 역할 문서 총합을 단일 shell 출력으로 간주하지 않는다.',
        'counterexamples':'unknown 한도를 통과로 세기, token 수를 근거 없이 byte로 환산, 일부 잘린 출력/단일 끝표지만으로 전문 회수를 주장하는 경우를 제외한다.',
        'question':'어느 실제 운전 host/tool/version/read-call 설정을 13-C의 비교 대상으로 고정할 것인가? 그 도구의 권위 있는 한도 단위와 절단 규칙은 무엇인가?',
        'exit':'고정된 실제 읽기/구간별로 같은 단위의 한도와 온전한 회수 근거를 연결한다. byte 계약이 없으면 단위를 맞춘 요구 개정 여부를 manager가 원문 권한 안에서 결정하거나 미충족으로 상신한다.',
        'remaining':'본 작업은 호스트 실험/도구 탐색을 하지 않았다. 기존 검토의 CLI 버전을 현재 버전이라고 재인증하지 않는다. 외부 조건 확인은 gate-readiness 결과와 manager가 통합한다.'})
    return packets


def unique(rows):
    return list({json.dumps(row,sort_keys=True):row for row in rows}.values())


def legacy_candidates():
    definitions={
        'ProcessId':('external_name','README의 Win32_Process 속성. do-math 필드로 새 namespace를 만들지 않는다. 실제 OS 조회 범위는 별도 경계 확인이다.',[]),
        'ParentProcessId':('external_name','README의 Win32_Process 속성으로 문서가 소유자를 명시한다.',[]),
        'CommandLine':('external_name','README의 Win32_Process 속성으로 문서가 소유자를 명시한다.',[]),
        'PT0S':('representation_not_python_name','PowerShell의 TimeSpan.Zero를 scheduler가 표시하는 값. Python 문자열 어휘 누락을 제품 결함으로 세지 않는다.',
                [location(SCRIPTS+'operator_schedule.ps1'),test('boundary/test_operator_schedule_adapter.py')]),
        'F':('glossary_not_code','가시 연구 프런티어를 설명하는 용어집 표기다. 코드 필드 존재 의무와 구별한다.',[]),
        'U':('glossary_not_code','미지 지평을 설명하는 용어집 표기다.',[]),
        'needs_revision':('explicit_negative_example','CLI 문장이 이 API의 과제 상태값이 아니라고 명시한다. 정상 enum에 추가하면 의미를 뒤집는다.',[]),
        'import_unit':('singular_prose_for_array_item','import_units 배열 원소의 산문 단수형. interpretation_schema의 unit 정의와 validate_import_units가 소유한다.',
                       [producer('governance.py','interpretation_schema'),producer('governance.py','validate_import_units')]),
        'rg':('external_command','검색 도구의 이름이며 제품 필드가 아니다. 이 task의 실제 rg 호출은 도구 사용 근거일 뿐 제품 설치 전부의 증거는 아니다.',[]),
        'TaskOutput':('conditional_external_tool','문장이 실제 도구로 제공될 때만 사용하라고 명시한다. 현재 미제공을 do-math 누락 필드로 바꾸지 않는다.',[]),
        'checkpoint_schema':('keyword_producer_found','_context 1651행의 checkpoint_schema=CHECKPOINT_SCHEMA. 문자열 상수만 찾은 구판 lexical 조회가 keyword를 빠뜨렸다.',
                             [producer('core_engine.py','CoreEngineMixin._context')]),
        'FileRenameInfoEx':('external_api_numeric_binding','file_io._replace_once가 클래스 번호22/flag3으로 호출한다. Python 변수명 부재는 API 결속 부재가 아니다. Windows 의미 전체는 여기서 재인증하지 않는다.',
                            [producer('file_io.py','_replace_once')]),
        'describe_source':('external_scholarly_contract_pending','scholarly 서버가 노출하는 경계 이름. 문서의 실제 세션/자료원별 설명 의무는 G7에서 서버 판본과 호출로 확인한다.',[]),
        'not_implemented':('external_scholarly_contract_pending','scholarly 응답 상태 어휘. 현재 외부 계약/실제 녹화 확인 없이 내부 schema에 복제하지 않는다.',[]),
        'restricted':('external_scholarly_contract_pending','scholarly 응답 상태 어휘. G7에 외부 판본·실제 응답 근거를 연결한다.',[]),
        'LIVE_INSTALLATION_ROOT':('confirmed_stale_document_name','현행 bootstrap에 이 이름은 없다. main이 manifest[installation_root] 또는 snapshot_root를 scheduled_operator.main의 installation_root 인자로 넘긴다. 독립-운영.md:21을 이 실제 경계로 교정할 한정 작업이 필요하다.',
                                  [location(SCRIPTS+'operator_bootstrap.py','main'),producer('scheduled_operator.py','main'),
                                   test('boundary/test_operator_bootstrap_info.py','test_frozen_entry_reports_original_installation_and_exact_verified_manifest')]),
        'question_detail':('singular_prose_for_array_item','question_details 배열 원소의 산문 단수형. interpretation_schema의 question_fields와 validate_import_units가 소유한다.',
                           [producer('governance.py','interpretation_schema'),producer('governance.py','validate_import_units')]),
    }
    return [{'token':token,'classification':kind,'judgment':reason,'definitions_or_tests':sources,
             'occurrences':[r for r in CENSUS['all_inline_spans'] if r['token']==token]}
            for token,(kind,reason,sources) in definitions.items()]


def command_census():
    path=SCRIPTS+'do_math/cli_contract.py'
    source=(REPO/path).read_text(encoding='utf-8-sig')
    location(path)
    tree=ast.parse(source)
    names=set()
    for node in ast.walk(tree):
        if isinstance(node,ast.Call) and isinstance(node.func,ast.Attribute) and node.func.attr=='add_parser' and node.args:
            if isinstance(node.args[0],ast.Constant): names.add(node.args[0].value)
        if isinstance(node,ast.For) and any(isinstance(x,ast.Call) and isinstance(x.func,ast.Attribute) and x.func.attr=='add_parser' for x in ast.walk(node)):
            names.update(ast.literal_eval(node.iter))
    short=[]; flags=[]
    for row in CENSUS['all_inline_spans']:
        first=row['token'].split()[0] if row['token'].split() else ''
        if first in names:
            short.append({**row,'command':first,'association':'inline command candidate; bare words require prose classification'})
        for flag in re.findall(r'--[a-z][a-z-]*',row['token']):
            flags.append({**row,'flag':flag})
    return {'source':'repo:'+path,'literal_parser_commands':sorted(names),
            'short_or_bare_command_candidates':short,'inline_flag_mentions':flags,
            'note':'참조 모집단의 정적 목록이다. parser를 실행하지 않았고 인자 유효성을 새로 검증한 결과가 아니다. 실제 검증 소유자는 structure.test_doc_code와 cli_contract이다.'}


def main():
    build_rows()
    packets=build_packets()
    candidates=legacy_candidates()
    commands=command_census()
    ast_calls=CENSUS['remaining_ast_calls']
    for item in ast_calls:
        owners=[r['owner'] for r in ROWS if item['line'] in r['ast_sites']]
        assert owners, item
        item['inventory_owners']=owners
    inventory={
        'scope':'001/document-closeout A1~A4; 현재 문서 결속의 정적 조사. 13-C 완료 선언이 아니다.',
        'documents':CENSUS['documents'], 'documents_rule':CENSUS['documents_rule'],
        'denominators':{'documents':len(CENSUS['documents']),'declared_schema_owners':len(ROWS),
                        'inline_dotted_field_occurrences':189,'lexical_owners':79,'ast_call_sites':len(ast_calls),
                        'note':'34는 구문 호출 지점 수다. 348행 loop가 세 owner를 만들며 한 owner에 여러 호출도 있다. 79는 이름 분류이며 두 동명 오결속이 있어 의미상 생산자 수가 아니다. 완료율 분모로 쓰지 않는다.'},
        'bindings':sorted(ROWS,key=lambda r:r['owner']), 'ast_site_inventory':ast_calls,
        'manual_compositions':[
            {'lines':[250,257],'kind':'shared_contract','consumer_owners':['runtime','instance'],'decision':'retain runtime family shapes; unconsumed instance/research-root is a removal candidate'},
            {'lines':[275,279,301],'kind':'shared_vocabulary','consumer_owners':['role_tiers','candidate_record','worker_feedback'],'decision':'retain name-only scope'},
            {'lines':[294,296],'kind':'source_expression_substitution','consumer_owners':['role_review'],'packet':'P04'},
            {'lines':[303,305],'kind':'source_expression_and_written_keys','consumer_owners':['import_check'],'packet':'P06'},
            {'lines':[307,314],'kind':'project_and_environment_base','consumer_owners':['project','toolchain','environment_check'],'packet':'P08'},
            {'lines':[325,328,330,333],'kind':'array_and_source_spreads','consumer_owners':['pending_findings','materialized_output_files','research_sources','checkpoint_files'],'packets':['P04','P02','P01']},
            {'lines':[334,336],'kind':'recovery_source_indirect_use','consumer_owners':['recovered_output_files','recovery_materials'],'packet':'P01'},
            {'lines':[338,345],'kind':'research_output_retained_and_result','consumer_owners':['results','materialized_output_files'],'packet':'P02'},
            {'lines':[349,354],'kind':'installed_tool_overlays','consumer_owners':['formal_verifier','preview','record_map'],'packet':'P03'},
            {'lines':[356,365],'kind':'actual_return_fixed_projection','consumer_owners':['operating_summary'],'decision':'retain B120'},
            {'lines':[370,372],'kind':'operational_evidence_overlay','consumer_owners':['operational_evidence'],'packet':'P01'},
        ],
        'unused_direct_owners':{
            'config':'session_limits parent and negative cross-family tests',
            'execution':'stored-versus-role-input negative tests; execution_to_review is a separate semantic alias',
            'profile':'ai/observation parents and schema tests',
            'instance':'No current explicit document, child-binding or document-test consumer found; removal candidate, not an obligation to exercise an invented document path',
            'recovery_source':'indirect recovered_output_files and recovery_materials.output_files; retain until P01 replacement'},
        'removal_candidates':[
            'instance의 노출과 research-root 조립은 현재 명시 소비가 없어 제거 후보. runtime 가족·config/profile 하위 결속·저장 execution과 역할 입력 구별은 보존한다.',
            'P01 완료 뒤 recovery_source와 그 중복 shape는 실제 경계 projection으로 대체하므로 제거 가능. 지금 무소비로 삭제하면 현재 문서 검사가 줄어든다.',
            'P02 완료 뒤 stored_file/retained/result 수동 조립은 실제 생산·물질화 증거로 교체해 제거한다.',
            'P04/P08 완료 뒤 source-expression bindings와 environment_base 조립을 제거한다.',
            '마지막 실제 AST 소비자 교체 뒤 producer_nodes/produced_object_schema/written_object_schema/consumed_object_schema와 그 구문 전용 합성 시험을 제거한다. 현재 다른 시험 소비자는 doc_code/test_doc_code 밖에 검색되지 않았다. 소유자·배열·default-reject 반례는 보존한다.'
        ],
        'other_reference_census':{
            'command_mentions':CENSUS['command_mentions'],'policy_mentions':CENSUS['policy_mentions'],
            'command_and_flag_candidates':commands,
            'lexical_policy_names':sorted({r['policy'] for r in CENSUS['policy_mentions']}),
            'limitations':'명령은 ENTRY 및 코드 예시의 실제 parser 소유자, bare flag는 전역 어휘다. 함수/상수/진단은 이름 존재 범위. 단독/조합/코드펜스와 정책 의미/도구 읽기 한도는 N01~N03/P11/L01에 남는다.'},
        'legacy_17_lexical_candidates':candidates,
    }
    for packet in packets:
        if packet['id'].startswith('N'):
            packet['slice_interpretation']='제목별 좌표는 작업 수가 아니다. 이미 정본/실제 반환에 연결된 이름은 재구현하지 않고 현재 의미가 달라지는 미결만 배정한다. 3494회 같은 lexical 출현을 3494개 결함/작업으로 세지 않는다.'
            packet['legacy_candidates']=[c for c in candidates if any(r['document'] in packet['document_partition'] for r in c['occurrences'])]
    save('binding-inventory.json',inventory)
    save('followup-packets.json',{'status':'proposals_for_manager_not_new_assignments','packets':packets,
        'sequencing':'P01 동명 소유자 교정 우선. P02/P03로 ROLE의 나머지 실제 경계를 닫고 P04~P11에서 고정된 잔여를 마감한다. 이름은 N 각 파일/절 한정 slice로, 읽기 한도는 L01의 실제 호스트 결정 뒤 처리한다. 공통 helper/소비자를 수정하는 task는 한 번에 하나다.',
        'closed_work_not_redispatched':['DOC-OPTIONAL-FLAG','DOC-RETURN-PURE','DOC-RETURN-CLI','B132 manifest/prompt/documents','B133 restore_continuation boundary','B134 profile_selection']})
    for row in CENSUS['documents']:
        SOURCES[row['path'].removeprefix('repo:')]=row['sha256']
    SOURCES[DOC_CODE.removeprefix('repo:')]=hashlib.sha256((REPO/DOC_CODE.removeprefix('repo:')).read_bytes()).hexdigest()
    save('reviewed-source-hashes.json',{'source_hashes':SOURCES,'note':'Current referenced code/tests/docs; compare again at submission. Hashes prove edition equality, not runtime success.'})
    print(json.dumps({'bindings':len(ROWS),'documents':len(CENSUS['documents']),'ast_sites':len(ast_calls),
        'packets':len(packets),'referenced_source_files':len(SOURCES),
        'unused_direct_owners':sorted(set(r['owner'] for r in ROWS if not r['documents']))},ensure_ascii=False,indent=2))


if __name__=='__main__':
    main()
