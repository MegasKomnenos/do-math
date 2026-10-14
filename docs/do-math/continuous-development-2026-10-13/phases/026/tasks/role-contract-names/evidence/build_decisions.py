"""Serialize the human section judgments; inspect selected source/test bodies without importing product code."""
import ast
import hashlib
import json
import re
from pathlib import Path

REPO = Path('C:/math')
RUN = REPO / 'docs/do-math/continuous-development-2026-10-13'
OUT = RUN / 'phases/026/tasks/role-contract-names/evidence'
DM = '.claude/skills/do-math/scripts/do_math/'
TS = '.claude/skills/do-math/scripts/tests/'

def read(p):
    return p.read_text(encoding='utf-8-sig')

def save(name, obj):
    (OUT/name).write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

def loc(file, symbol):
    path = REPO/file
    source = read(path)
    tree = ast.parse(source)
    candidates = []
    def walk(node, prefix=''):
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                name = prefix + child.name
                if name == symbol or ('.' not in symbol and child.name == symbol):
                    candidates.append((name, child))
                walk(child, name+'.')
            elif isinstance(child, (ast.Assign, ast.AnnAssign)):
                targets = child.targets if isinstance(child, ast.Assign) else [child.target]
                if any(isinstance(t, ast.Name) and t.id == symbol for t in targets):
                    candidates.append((symbol, child))
            else:
                walk(child, prefix)
    walk(tree)
    if len(candidates) != 1:
        raise ValueError((file, symbol, [x[0] for x in candidates]))
    name, node = candidates[0]
    return {'path':'repo:'+file, 'symbol':name, 'line':node.lineno, 'end_line':node.end_lineno,
        'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
        'excerpt':'\n'.join(f'{i}: {line}' for i,line in enumerate(source.splitlines(),1) if node.lineno <= i <= node.end_lineno)}

P = {}
def profile(key, meaning, defs, consumers, tests):
    P[key] = {'meaning':meaning, 'definitions':[loc(DM+f,s) for f,s in defs],
        'consumers':[loc(DM+f,s) for f,s in consumers], 'tests':[loc(TS+f,s) for f,s in tests],
        'verification_kind':'current source/test-body inspection; no product/test execution in 026'}

profile('input', '배정 역할의 입력 키와 중첩 원소. 저장 RECORDS와 _context/prepare_role_input의 최종 입력은 별도 소유자다.',
 [('role_input_requirements.py','judgment_input_keys'),('role_input_requirements.py','judgment_input_paths'),('record_schemas/schemas.py','RECORDS')],
 [('core_engine.py','CoreEngineMixin._context'),('context_store.py','prepare_role_input')],
 [('structure/test_doc_code.py','test_role_input_fields_do_not_borrow_names_from_the_stored_execution')])
profile('task', 'task 저장 계약과 후보 wire의 질문·scope·expected·의무·판정자. task.id/revision/producer_execution은 수신자가 붙이며 후보 output에는 저작하지 않는다.',
 [('contracts.py','TASK_CANDIDATE'),('contracts.py','PROGRESS'),('contracts.py','OBLIGATION')],
 [('contracts.py','task_candidate_record'),('task_contracts.py','validate_task_contract')],
 [('unit/test_submission_contract_checks.py','test_a_cited_sibling_contract_is_declared_at_its_current_revision')])
profile('plan', 'research_plan 주 응답의 dispositions/task_assessments와 ready/returned 고정 모집단. 전문 판정 ID·scope 권위는 완료 의미의 별도 검사다.',
 [('contracts.py','SCHEMAS'),('contracts.py','PLAN_DISPOSITION'),('contracts.py','ITEM_DISPOSITION')],
 [('task_contracts.py','validate_plan_dispositions'),('task_contracts.py','validate_item_dispositions'),('core_engine.py','CoreEngineMixin._apply_plan')],
 [('unit/test_planning_assessments.py','test_plan_covers_every_ready_and_returned_task_and_rejects_double_disposition'),('unit/test_planning_assessments.py','test_foreign_stale_or_cycle_only_receipt_does_not_authorize_completion')])
profile('work', 'research_work 및 일반 supplemental_research 주 응답. outcome은 수행 보고이며 과제 완료·수학 인증이 아니다. knowledge.kind는 action_schema의 동적 등록 종류로 검사한다.',
 [('contracts.py','SCHEMAS'),('contracts.py','KNOWLEDGE'),('contracts.py','RELATION'),('contracts.py','action_schema')],
 [('submission.py','_payload_issues'),('core_engine.py','CoreEngineMixin._apply')],
 [('unit/test_submission_contracts.py','test_every_role_has_closed_schema')])
profile('review', 'identity_review의 실제 stage_schema: scope/initial/organize/answer/judge는 서로 다른 응답. organize는 issues와 finding_refs/answer_role_slot_id이며 전체 decision이 없다.',
 [('review_cycle.py','stage_schema')],
 [('review_cycle.py','validate_visible_output'),('review_cycle.py','accept_result'),('review_cycle.py','context_for')],
 [('unit/test_review_cycle_stages.py','test_stage_schema_is_specific'),('unit/test_review_cycle_stages.py','test_organizer_omission_forgery_and_owner_checks')])
profile('review-scope', 'scope_assessment 출력의 자리/프로필/상한과 role_review의 scope_executions_used/minimum_scope_execution_limit/retained_reviewer_slots 입력을 구별. U+N+4와 U+2N+7은 minimum_scope_executions의 두 분기다.',
 [('review_policy.py','SCOPE_ASSESSMENT'),('review_policy.py','minimum_scope_executions')],
 [('review_policy.py','validate_scope_assessment'),('review_cycle.py','validate_visible_output')],
 [('unit/test_review_scope_wire.py','test_one_real_response_contract_reaches_the_consumer'),('unit/test_review_scope_wire.py','test_submission_checks_scope_with_the_conditions_the_review_accepts'),('unit/test_review_policy_rejections.py','test_minimum_budget_includes_used_attempts_and_both_round_shapes')])
profile('research', '검토 자리의 고정 질문 응답은 research_schema(research_request_id/request_digest/answer/outcome/scope_complete/evidence_refs). 일반 과제 조사 wire와 교환할 수 없다.',
 [('review_cycle.py','research_schema'),('review_cycle.py','research_request_schema')],
 [('review_cycle.py','validate_research_answer'),('review_cycle.py','validate_provisional'),('submission.py','extension_schema')],
 [('unit/test_review_research_owner_contract.py','test_fixed_question_context_keeps_original_bytes_after_unrelated_publication')])
profile('goal', 'goal_audit 주 응답 decision/reason/scope_complete와 추가 감사 additional_audits는 별도 계약. audit_ref/assessor/verdict/input_hashes는 audit 입력과 정확히 일치해야 한다.',
 [('contracts.py','SCHEMAS'),('governance.py','additional_audit_schema'),('governance.py','additional_audit_input')],
 [('governance.py','evaluate_goal_audits'),('governance.py','validate_goal_additional_audits'),('core_engine.py','CoreEngineMixin._context')],
 [('structure/test_doc_code.py','test_document_variables_have_line_local_owners_without_a_union_of_families')])
profile('operational', 'operational_review 주 응답은 disposition(kind별 여섯 구조)이며 decision은 해당 응답의 주 필드가 아니다. basis_refs와 used_sources, 기술 후속과 task_assessments는 별도 검사.',
 [('contracts.py','disposition_schema'),('operational_dispositions.py','admissible_basis_refs')],
 [('operational_dispositions.py','validate_disposition'),('operational_dispositions.py','require_basis_refs'),('core_engine.py','CoreEngineMixin._apply_operational_disposition'),('core_engine.py','CoreEngineMixin._response_schema')],
 [('structure/test_doc_code.py','test_operational_document_names_the_result_and_checkpoint_owners')])
profile('maintenance', '일반 maintenance report/remaining_work와 initial_submission_diagnosis, kind_definition_check, impact_review 동적 응답을 구별. action.stage=impact_review의 확장은 금지된다.',
 [('contracts.py','action_schema'),('core_engine.py','CoreEngineMixin._response_schema')],
 [('core_engine.py','CoreEngineMixin._apply_kind_definition_check'),('submission.py','_payload_issues')],
 [('structure/test_schema_builders.py','test_schema_samples_reach_context_dependent_shapes')])
profile('intent', 'intent_interpretation의 interpret/check 분기. import_unit와 question_detail은 import_units/question_details 배열 원소의 산문 단수형이며 wire에 새 필드를 추가하지 않는다.',
 [('governance.py','interpretation_schema')],
 [('governance.py','validate_import_units'),('governance.py','prepare_import'),('governance.py','check_import')],
 [('sim/test_governance_interpretation.py','test_failed_check_returns_to_authoring_with_findings'),('sim/test_governance_interpretation.py','test_check_cannot_apply_unresolved_proposed_changes')])
profile('delegation', '동적 delegation_judgment는 input_sha256/decision/reason이며 import_units 응답이 아니다. 위임 등록 금지 종류는 proposal_adoption/contract_limit_continuation.',
 [('core_engine.py','CoreEngineMixin._response_schema'),('delegations.py','judgment_input')],
 [('core_engine.py','CoreEngineMixin._apply_delegation_judgment')],
 [('structure/test_schema_builders.py','test_schema_samples_reach_context_dependent_shapes')])
profile('contract-review', 'task_contract_review의 item_reviews는 다섯 item_id 전건. 각 item.decision과 전체 계약 집계는 별도며 주 응답 전체 decision은 만들지 않는다.',
 [('contracts.py','CONTRACT_REVIEW_ITEMS'),('contracts.py','REVIEW_ITEM')],
 [('contracts.py','contract_review_decision'),('planning.py','seal_contract_review')],
 [('unit/test_submission_contracts.py','test_every_role_has_closed_schema')])
profile('extensions', 'activity-extensions.json의 역할별 가족·배열 원소. 주 응답 필드와 확장 이름을 혼용하지 않는다. 고정 질문 조사와 영향 검토의 확장 금지를 유지한다.',
 [('submission.py','EXTENSION_ROLES'),('submission.py','extension_schema')],
 [('submission.py','_payload_issues'),('core_engine.py','CoreEngineMixin._apply_extensions')],
 [('unit/test_submission_contracts.py','test_academic_resolution_carries_real_evidence_references')])
profile('checks', 'contract_checks[].sibling_boundaries의 다섯 필드와 contract_check 다섯 진단은 submission 소유. TK-W는 예시 식별자이며 실제 연구 ID 존재를 주장하지 않는다.',
 [('submission.py','extension_schema'),('submission.py','contract_check_errors')],
 [('submission.py','_payload_issues')],
 [('unit/test_submission_contract_checks.py','test_every_candidate_needs_exactly_one_self_check'),('unit/test_submission_contract_checks.py','test_a_boundary_may_not_silently_depend_on_a_sibling_under_revision')])
profile('assessment', '일반 준비 model_assessments는 task_title, 보충 전용/계획은 task_id. 보충 모델·관찰 전건은 별도 coverage이고 후보/계약 개정을 허가하지 않는다.',
 [('model_policy.py','ASSESSMENT_SCHEMA'),('model_policy.py','assessment_key'),('submission.py','extension_schema')],
 [('model_policy.py','validate_assessments'),('model_policy.py','edition_current')],
 [('structure/test_schema_builders.py','test_schema_samples_reach_context_dependent_shapes')])
profile('operator', 'operator install/probe의 mode는 cli_contract.build_parser 소유. 정기 check/probe는 모델 없이 동작하며 결과 shape는 분기별로 다르다. 복구 AI는 내부 maintenance wire가 아닌 repair_report_schema를 사용한다.',
 [('cli_contract.py','build_parser'),('supervision.py','repair_report_schema'),('supervision.py','OPERATOR_SCHEMA')],
 [('scheduled_operator.py','check'),('scheduled_operator.py','recovery'),('supervision.py','collect_repair_verification')],
 [('sim/test_operator_finish_cli.py','test_hold_stops_wake_engine_and_supervisor_at_the_public_boundary')])
profile('condition', 'task_conditions의 occurrence_condition은 planning 조건 문법이며 space/family와 /usable_as_k는 후보 wire의 직접 필드가 아니다. observation_rules/iteration_gte/$execution은 관찰 규칙의 대상 결박이다.',
 [('planning.py','validate_condition'),('observations.py','validate_task_rules')],
 [('planning.py','evaluate_condition'),('submission.py','_payload_issues')],
 [('unit/test_planning_conditions.py','test_readiness_document_tables_match_the_condition_grammar')])
profile('declaration', 'prime 선언명은 lean_evidence의 제한된 지원 문법 예시. 허용 이름과 실제 Lean 선언/서명·공리 검증은 별도다.',
 [('lean_evidence.py','is_lean_identifier')],
 [('lean_evidence.py','declaration_rejection')],
 [('boundary/test_knowledge_lean_verifier.py','test_actual_prime_declarations_have_signatures_and_axioms')])

default = {'독립-운영':'operator','동일성-검토':'review','목표-감사':'goal','보충-조사':'research',
    '연구-계획':'plan','연구-수행':'work','운영-점검':'operational','유지보수':'maintenance',
    '의도-해석':'intent','작업-계약-검토':'contract-review','후보-준비':'task'}
slice_profiles = {
    3:['operator','input'], 9:['review','input'], 10:['review-scope','review','input'], 11:['review','input'],
    12:['review','input','extensions'],13:['review','input'],15:['review','input'],18:['research','review','extensions'],19:['review','input'],
    21:['goal','input'],22:['goal','input'],24:['goal','input'],27:['research','work','input'],28:['research','input'],
    29:['research','extensions'],30:['research','input'],31:['work','input'],32:['research','work'],
    35:['input','plan','task','extensions'],36:['plan','task','input'],37:['plan','input','extensions','assessment'],
    38:['extensions','input'],39:['plan','extensions','input'],41:['plan','input'],46:['plan','goal','input'],
    49:['task','input','work'],50:['task','work','input'],51:['work','extensions','input'],52:['input','extensions','operational'],
    53:['work','input','declaration'],54:['extensions','task','input'],55:['extensions','task'],59:['work','extensions','input'],
    61:['work','input'],62:['work','input'],66:['work','input'],67:['work','input'],70:['input','operational'],
    71:['input','task','operational'],72:['operational','input'],74:['operational','operator'],77:['operational','plan','task'],
    79:['operational','input','extensions'],80:['operational','extensions'],81:['operational','input'],
    84:['maintenance','input','extensions'],87:['maintenance','input'],89:['maintenance','extensions'],
    93:['maintenance','extensions','input'],95:['maintenance','operator'],102:['intent','input'],103:['intent','input'],
    104:['intent','input'],105:['intent','input'],106:['intent','input'],107:['delegation'],
    111:['task','input','contract-review'],112:['task'],113:['task'],114:['task','input'],115:['task','plan'],
    116:['task','input'],117:['task','extensions'],118:['task','input'],119:['task','input'],120:['contract-review','input'],
    127:['contract-review','assessment','task'],130:['input','task'],132:['task','work','input'],134:['extensions','task'],
    135:['task','extensions','input','assessment','condition'],136:['checks','task','input'],137:['task','extensions'],
    138:['task','input'],140:['task'],143:['assessment','extensions'],144:['assessment','extensions','input','condition']}

excluded = {'.git': '제외 디렉터리 이름; 설치 inventory의 집합 제외 규칙', '.lake':'빌드 디렉터리 제외 이름',
 '.pyc':'바이트코드 suffix 제외 규칙','__pycache__':'바이트코드 디렉터리 제외 규칙',
 'SKILL.md':'지급 문서 파일명; contracts.reading_map/prompt_documents가 소유',
 'checkpoint.json':'workspace 체크포인트 파일명; CHECKPOINT_SCHEMA/checkpoint_path와 연결',
 'activity-extensions.json':'submission.read_extensions의 고정 확장 파일명',
 'observation-feedback.json':'execution_window.feedback_path가 .control/observation-feedback.json으로 지급하는 파일 basename',
 '.control/stop-request.json':'execution_window.stop_request_path의 정확 파일명',
 '공통-실행.md':'references/공통-실행.md 문서 이름',
 '∀ x : Nat, ∃ y : Nat, y = x':'양화 순서 차이를 설명하는 수학 예시; API/필드가 아님',
 '좋은 증명을 만든다':'판정할 수 없는 계약 문구의 반례 인용', '충분히 검토한다':'판정할 수 없는 계약 문구의 반례 인용',
 'τ(n)':'경계 의존을 설명하는 수학 기호', '0≤k≤τ(n)−3':'수학 예시 구간',
 'τ(n)−2≤k≤τ(n)+2':'수학 예시 구간', 'TK-W':'예시 과제 이름; 실재 기록으로 읽지 않음',
 'TK-':'과제 기록 ID prefix; submission.RECORD_ID의 제한된 문면 참조',
 'KN-':'지식 기록 ID prefix; submission.RECORD_ID의 제한된 문면 참조',
 "'":'Lean 선언명 prime suffix를 설명하는 문자', "sumTo_succ'":'지원 선언명 문법 예시; 설치된 실제 선언을 주장하지 않음',
 "N.foo''":'지원 선언명 문법 예시; 설치된 실제 선언을 주장하지 않음'}

extension_names = {'revision_requests','revision_resolutions','task_conditions','contract_checks','task_dispositions',
 'research_insights','external_requests','knowledge_changes','kind_definitions','knowledge_metadata','relations',
 'observation_rules','research_requests','academic_resolutions','model_assessments','model_assessment_deferrals',
 'observation_rule_deferrals','queued_requests','action_resolutions','input_overflow_resolutions'}
input_names = {'action','task','goal','goal_revision','policies','governance','governance_records','decisions','grants','delegations',
 'tasks','question_links','sources','reference_catalog','record_index','original_source','import_consumers','instance_id',
 'eligible_knowledge','knowledge_catalog','additional_audit_input','task_catalog','ongoing_work','ready_task_ids','returned_task_ids',
 'recent_history','preparation_history','academic_phase','academic_requirements','academic_validation','pending_revisions',
 'input_overflow_requests','review_followups','queued_work','blocked_actions','task_readiness','available_input_refs','supplied_record_ids',
 'execution_to_review','observation','operational_evidence','recovery_materials','admissible_basis_refs','repetition_holds',
 'formal_verifier','observed_toolchain','initial_observation_rules','kind_definitions','role_profile_refs',
 'assessment_targets','observation_rule_targets','observed_at','model_assessment_history','observation_rule_history',
 'verified_summaries','waiting_actions','reviews','revision_requested'}
task_names={'title','question','scope','expected','included','excluded','outputs','research_change','description','progress_criteria',
 'completion_obligations','claim','judges','evidence_required','evidence_requirements','inputs','reuse','dependencies','profile_refs',
 'authority_refs','basis_refs','work_class','revises_task_id','producer_execution','required_external_effects',
 'solution_basis','academic_requirement_id','knowledge_revision_targets','transferred_obligations'}

def owner_for(doc, sn, token, keys, line, context):
    root=re.split(r'[.\[=]',token)[0]
    if token=='decision' and doc=='운영-점검' and sn==72:
        return 'negative example: no output.decision', '본문은 decision이 아니라 disposition을 반환하라고 한다. operational_review의 주 decision 소유를 승인하지 않는다.'
    if token=='decision' and doc=='작업-계약-검토' and '별도의 전체' in context:
        return 'negative example: no top-level decision', 'item_reviews[].decision과 전체 집계를 구별하는 금지 예시. 주 응답에 decision을 새로 추가하지 않는다.'
    if token in ('summary','used_sources','questions'):
        if doc=='후보-준비' and sn==130 and '지식 목차' in context:
            return 'knowledge_catalog[].summary', '저자 요약이며 verified_summaries와 증거 수준이 다르다. _context가 knowledge_records.reader_view의 summary를 투영한다.'
        if doc=='연구-수행' and sn==59:
            return 'research_work output.knowledge.items.'+token, 'KNOWLEDGE 항목의 필드. 주 응답 COMMON.summary와 다른 객체의 소유자다.'
        return doc+' main-output common/'+token, '배정된 실제 역할/단계 응답의 공통 필드. contracts.COMMON, review_cycle.stage_schema/research_schema, governance.interpretation_schema를 문맥별로 적용한다.'
    if token in excluded:
        return 'noncode/file/example', excluded[token]
    if doc=='후보-준비' and token in ('space','family','/usable_as_k=true','iteration_gte','$execution'):
        return 'task_conditions occurrence_condition/observation_rules grammar', P['condition']['meaning']
    if token.startswith(('workspace:', 'source:', 'operator/', 'input/', 'scripts/')):
        return 'file/locator', '로컬/입력 참조나 설치 파일 위치. 실제 읽기·자료 존재·성공을 이름만으로 주장하지 않는다.'
    if token in ('operator install','operator probe','quiesce','probe','--version','--help','probe_cli.py --skill-only'):
        return 'operator/CLI', P['operator']['meaning']
    if token in ('null','true','false'):
        return 'JSON literal', '각 문장의 배열/부재/null·논리값 의미를 유지하는 JSON 리터럴; 필드 이름이 아님'
    if token in ('import_unit','question_detail'):
        return 'intent/'+('import_units.items' if token=='import_unit' else 'question_details.items'), P['intent']['meaning']
    if token=='kind_definitions' and doc=='연구-수행':
        return 'research_work input.kind_definitions', '등록 종류의 입력 목록. kind_definitions 확장에 새 정의를 제안하는 것과 별도다.'
    if root in extension_names and ('extensions' in keys or 'checks' in keys or 'assessment' in keys or root in ('research_requests','contract_checks')):
        # relations in work's main output and observation_rules in stored task are separately explained by their section.
        if token=='relations' and doc=='연구-수행' and sn in (50,60):
            return 'research_work output.relations/input.relations', P['work']['meaning']
        return 'extension/'+root, P['extensions']['meaning']
    if root in ('action','task','execution_to_review','operational_evidence','recovery_materials','formal_verifier','record_map',
                'profile_selection','user_request','immutable_input','external_rejections') or token in input_names:
        return doc+' role input/'+root, P['input']['meaning']
    if doc in ('후보-준비','작업-계약-검토','연구-수행') and (root in task_names or token=='{id, claim, evidence_required}' or token=='{id, claim, judges, evidence_required}'):
        if doc=='연구-수행' and token=='title' and sn==59:
            return 'research_work output.knowledge.items.title', P['work']['meaning']
        return ('candidates.items/' if doc=='후보-준비' else 'task input/')+root, P['task']['meaning']
    if root=='contract_check':
        return 'submission diagnostic/'+token, P['checks']['meaning']
    if doc=='동일성-검토':
        stage={9:'assignment',10:'scope',11:'assessment_reassessment',12:'proposal/formal',13:'role_review history',
            14:'initial',15:'organize',16:'answer',17:'judge',18:'review research',19:'aggregate/assessment use'}.get(sn,'review')
        if token in ('self_messages','completed_results','supplemental_results','previous_reviews','pending_findings','pending_findings[].ref',
            'answer_requests','research_request_contract','retained_reviewer_slots','scope_executions_used','minimum_scope_execution_limit','role_review'):
            return 'role_review/'+token, P['review']['meaning']
        if token in ('identity_assessments','assessment_uses'):
            return 'stored '+token, 'identity_assessments는 공개 판정 기록, assessment_uses는 판정 사용 효력이며 편입 승인과 별도다.'
        return 'identity_review '+stage+' contextual contract', P['review-scope' if sn==10 else 'review']['meaning']
    if doc=='보충-조사':
        return ('supplemental_research general output' if sn==31 else 'fixed review research/contextual reference'), P['work' if sn==31 else 'research']['meaning']
    if doc=='목표-감사':
        return 'goal_audit/'+('additional_audits.items' if sn==24 and token in ('audit_ref','assessor','verdict','input_hashes','reason') else 'output or eligible_knowledge proposal/verification'), P['goal']['meaning']
    if doc=='독립-운영':
        return ('repair_report_schema diagnosed output' if sn==6 and token not in ('waiting','stopping','repaired') else 'scheduled operator branch/profile contract'), P['operator']['meaning']
    if doc=='유지보수':
        return ('maintenance dynamic '+{87:'initial_submission_diagnosis',89:'kind_definition_check',93:'impact_review'}.get(sn,'report/remaining_work or input state')), P['maintenance']['meaning']
    if doc=='의도-해석':
        return 'intent '+{104:'interpret import_units/question_details',105:'check',106:'repair/action lineage',107:'delegation_judgment'}.get(sn,'input/apply')+' contextual contract', P['intent' if sn!=107 else 'delegation']['meaning']
    if doc=='작업-계약-검토':
        return 'task_contract_review item_reviews.items/'+token, P['contract-review']['meaning']
    if doc=='후보-준비':
        return ('research_preparation supplement-only extension' if sn==144 else 'research_preparation '+('contract_checks items/diagnostics' if sn==136 else 'output/context'))+'/'+token, P['assessment' if sn in (143,144) else 'checks' if sn==136 else 'task']['meaning']
    if doc=='연구-계획':
        return 'research_plan dispositions/task_assessments/input state or diagnostic/'+token, P['plan']['meaning']
    if doc=='운영-점검':
        return 'operational_review disposition/'+{73:'continue',74:'repair',75:'resume',76:'retry',77:'task_disposition',78:'user_decision'}.get(sn,'input failure/common')+'/'+token, P['operational']['meaning']
    return 'research_work output/knowledge/relations/observation feedback/'+token, P['work']['meaning']

slices=json.loads(read(OUT/'slice-map.json'))
decisions=[]
for section in slices:
    doc=Path(section['document']).stem
    sn=int(section['id'].split('-')[-1])
    keys=slice_profiles.get(sn,[default[doc]])
    tokens={}
    for occurrence in section['current_occurrences']:
        token=occurrence['text']
        owner,why=owner_for(doc,sn,token,keys,occurrence['line'],occurrence['context'])
        tokens.setdefault((token,owner,why),[]).append(occurrence['line'])
    bindings=[]
    for (token,owner,why), lines in tokens.items():
        bindings.append({'name':token,'lines':sorted(set(lines)),'owner':owner,
            'decision':'correct-wording' if sn==2 and token=='model_called=false' else 'keep/exclude' if owner.startswith(('noncode','file/','JSON')) else 'keep',
            'reason':why,'source_profiles':keys})
    decisions.append({'id':section['id'],'document':section['document'],'heading':section['heading'],
        'current_range':section['current_range'],'bindings':bindings,'profiles':keys,
        'decision':'correct-wording' if sn==2 else 'keep' if bindings else 'noncode-section',
        'scope':'이 절의 현재 이름/조합과 직접 소비만 판정; 수학 절차 전체의 재감사나 새로운 실행 성공이 아님'})
save('source-profiles.json',P)
save('decisions.json',decisions)

fences=[]
population=json.loads(read(OUT/'population.json'))
for document in population:
    source=read(REPO/document['ref'][5:])
    for match in re.finditer(r'```json\n(.*?)```',source,re.S):
        value=json.loads(match.group(1))
        line=source[:match.start()].count('\n')+1
        def keys_in(v,prefix=''):
            if isinstance(v,dict):
                for key,child in v.items():
                    yield prefix+key
                    yield from keys_in(child,prefix+key+'.')
            elif isinstance(v,list):
                for child in v:
                    yield from keys_in(child,prefix+'[].')
        fences.append({'document':document['ref'],'line':line,'value':value,'field_paths':sorted(set(keys_in(value))),
            'owner':'submission.extension_schema research_preparation supplement-only' if 'model_assessments' in value else 'submission.extension_schema contract_checks[].sibling_boundaries.items',
            'decision':'keep','reason':'부분 객체 예시다. 하나는 모델 평가/보류 확장 파일 예시이고 다른 하나는 배열 원소 예시다. 주 응답 전체로 검사하지 않으며 assessment/checks의 현재 정의와 필드가 같다. TK-one/TK-two/TK-W는 예시 ID다.',
            'schema_execution':'not_run; JSON parsing only; product schema inspected in source'})
save('fence-decisions.json',fences)

summary={'documents':len(population),'lines':sum(d['lines'] for d in population),'slices':len(decisions),
    'inline_occurrences':sum(len(d['occurrences']) for d in population),'document_token_pairs':sum(len({o['text'] for o in d['occurrences']}) for d in population),
    'json_examples':len(fences),'delta_slices_vs_historical_lexical_list':sum(bool(s['added_tokens'] or s['removed_tokens']) for s in slices),
    'meaning_of_counts':'현재 원문의 좌표 대조 수이며 이름 수를 13-C/G 완료율로 쓰지 않는다. 기존 후보에 없던 dotted/code/file 이름의 상당수는 당시 목록 분류 차이이며 실제 소스 추가를 주장하지 않는다.'}
save('decision-summary.json',summary)

lines=['# N03 역할 계약의 현재 이름 판정', '', '행마다 이름과 occurrence 좌표는 decisions.json에 있다. source-profiles.json은 실제 정의·소비·시험 본문과 SHA를 보존한다. 제품 코드/시험은 실행하지 않았다.', '',
    '| 절 | 현재 문서·행 | 판정 | 이름 수 | 정의·소비 프로필 |', '|---|---|---|---:|---|']
for row in decisions:
    lines.append('| '+row['id']+' | '+Path(row['document']).name+':'+str(row['current_range'])+' | '+row['decision']+' | '+str(len(row['bindings']))+' | '+', '.join(row['profiles'])+' |')
(OUT/'decision-table.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False))
