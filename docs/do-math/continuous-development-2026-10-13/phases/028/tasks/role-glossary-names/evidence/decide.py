"""Authored bounded ownership judgments, expanded to original occurrences for audit."""
import ast
import collections
import hashlib
import json
import re
from pathlib import Path
from analyze import ROOT, RUN, OUT, SKILL, read, save, sha

P = {}
def profile(key, files, judgment):
    P[key]={'definitions':['repo:.claude/skills/do-math/scripts/'+f for f in files.split()], 'judgment':judgment}

profile('activity','do_math/activities.py do_math/execution_lifecycle.py do_math/record_schemas/schemas.py',
        '활동 status는 ACTIVITY_STATUSES이고 실행 status는 EXECUTION_STATUSES다. 활동의 finished와 실행의 ended/output_accepted를 과제 완료로 차용하지 않는다.')
profile('record','do_math/knowledge_records.py do_math/record_schemas/schemas.py',
        '기록 효력은 RECORD_LIFECYCLES, 판정 사용 효력은 ASSESSMENT_USE_STATUSES다. formal_use는 formal_results의 별도 축이며 현행 저장 enum은 active/suspended/withdrawn이다.')
profile('universal_lifecycle','do_math/record_schemas/schemas.py do_math/knowledge_records.py',
        '이 절은 보편 개념의 상태를 정의한다. GLOSSARY5행은 보편 상태와 CLI 기록 이름이 다를 수 있고 동의어로 추측하지 말라고 명시한다. 특히 보편 형식 사용 효력 historical을 현행 formal_results.formal_use의 withdrawn 필드 값으로 전사하지 않는다. 보편 과제/인스턴스 상태도 저장 enum과 자동 등치하지 않는다. 이 이름 판정에서 runtime이나 개념을 임의 개명하지 않는다.')
profile('ontology','do_math/knowledge_io.py do_math/submission.py do_math/core_engine.py',
        'BUILTIN_DEFINITIONS의 relation token은 의미가 다른 연구관계와 수학관계다. catalog_definitions가 활성 정의를 입력에 싣고 _payload_issues가 해당 가족과 같은 묶음의 신규 제안을 검사한다. 개념 F/U/K를 literal 필드로 추가하지 않는다.')
profile('repetition','do_math/revisions.py do_math/repair_execution.py do_math/contracts.py do_math/task_contracts.py',
        'repetition_hold/owner=user와 repetition_continue는 revisions의 보류·사용자 재개 계약이다. import_rework/selection_failure/exhaustion_empty는 각각의 계보 계수다. 기술 retry/resume의 새 execution·continuation_of와 출력 repair_responses는 다른 계수이며 item_reviews는 task_contract_review 응답이다.')
profile('input','do_math/core_engine.py do_math/context_store.py do_math/contracts.py do_math/planning.py',
        'CoreEngineMixin._context가 역할·action별 입력을 생산한다. reading_map/prompt_documents가 문서 순서를, INLINE_SCOPES/BLOCKED_KEYS/input_class/prepare_role_input이 inline/map/blocked와 record_index/record_map을 결정한다. 이름 존재만으로 다른 scope의 지급을 보장하지 않는다.')
profile('overflow','do_math/context_store.py do_math/input_recovery.py do_math/core_engine.py do_math/review_cycle.py do_math/knowledge_records.py',
        'prepare_role_input의 문맥 바이트 예산과 직접/지도 필드, review_cycle.context_for의 proposal 단일 지급과 judged_verification 투영을 구별한다. retry-action의 비해소/재포장 해소 및 실패 이력은 024 지정 단락만 재사용한다.')
profile('currentness','do_math/input_basis.py do_math/core_engine.py do_math/submission.py do_math/context_store.py',
        '입력 snapshot의 manifest.prompt.sha256와 source basis를 고정한다. used_sources/지원 확장 참조는 보고된 실제 의존이며 제공 전부를 사용으로 세지 않는다. 결과 현재성은 _validate_bundle_current에서 적용 직전 다시 검사한다.')
profile('envelope','do_math/contracts.py do_math/provider_final.py do_math/model_call.py do_math/model_runner.py',
        'COMMON의 summary/used_sources/questions, 선택 repair_responses/integration_bundles와 실제 action_schema가 응답을 소유한다. 비결박 Codex의 output_json 봉투는 output_contract/semantic_output이며 의미 output.schema.json과 전송 transport.schema.json을 구분한다.')
profile('prepare','do_math/contracts.py do_math/submission.py do_math/execution_profiles.py',
        'research_preparation candidates[].TASK_CANDIDATE의 scope/expected/완료의무와 PROFILE_REF{id,revision,sha256}다. {id,version}은 명시 반례다. 일반 action_schema는 regenerate_after도 요구하므로 CLI의 비전수 필드 설명을 완전 객체 예제로 취급하지 않는다.')
profile('contract','do_math/contracts.py do_math/task_contracts.py',
        'task_contract_review.item_reviews[]의 item_id는 CONTRACT_REVIEW_ITEMS 다섯 값이며 decision 세 값은 contract_review_decision으로 우선순위·근거·미입력 조건을 검사한다. 전체 판정은 집계자의 값이다.')
profile('plan','do_math/contracts.py do_math/planning.py do_math/task_contracts.py do_math/submission.py',
        'research_plan의 PLAN_DISPOSITION.kind와 task_assessments[].decision/item_dispositions[].kind/unresolved[]는 별도 소유자다. selected/not_selected/not_assessable과 fulfilled/open/waived/transferred를 섞지 않는다. ready_task_ids는 고정 입력 모집단이고 missing/unexpected/duplicate는 소비 오류 분류다.')
profile('work','do_math/contracts.py do_math/submission.py do_math/knowledge_io.py',
        '과제 기반 research_work/supplemental_research의 outcome/report/knowledge/relations/remaining_work/checkpoint를 소유한다. RELATION.source/target/evidence와 knowledge의 declaration_names/dependencies는 서로 다르다. CLI748의 active enum 설명은 action_schema의 TEXT 및 active-or-proposed 수신 검사와 달라 수정 대상이다.')
profile('scope','do_math/review_cycle.py do_math/review_policy.py do_math/review_engine.py do_math/core_engine.py',
        'identity_review scope는 stage_schema(scope).scope_assessment/SCOPE_ASSESSMENT 및 validate_scope_assessment다. profile 참조와 overflow_disposition unresolved/defer는 동일성 decision이 아니다. _response_schema/_review_schema가 배정 stage로 선택한다.')
profile('audit','do_math/contracts.py do_math/academic.py do_math/governance.py do_math/governance_engine.py',
        'goal_audit decision은 satisfied/not_satisfied/unresolved, reason/scope_complete는 같은 응답이다. _governance_schema의 additional_audits와 현재 goal basis의 실제 집계는 별도이며 이름 판정으로 수학적 해결을 인증하지 않는다.')
profile('operation','do_math/contracts.py do_math/operational_dispositions.py do_math/repair_execution.py do_math/core_engine.py',
        'operational_review는 disposition 객체의 여섯 kind를 쓴다. continue.next_review, repair.repair_target/meaning_preserving/verification, resume.checkpoint_ref/scope, retry.scope/replay_safety, task_disposition.task_id/task_state, user_decision.question/effect의 실제 분기를 읽는다. root decision은 명시 음성 예시이며 task_disposition은 _response_schema에서 task_assessments도 요구한다.')
profile('intent','do_math/governance.py do_math/core_engine.py do_math/delegations.py',
        'interpret의 import_units[]/question_details[]와 check의 decision/findings/scope_complete/bundle_sha256/unit_ids/question_ids는 interpretation_schema의 다른 단계다. 산문 import_unit은 원소 단수형이다. delegation_judgment는 _response_schema의 별도 봉인 input_sha256/decision/reason 객체다.')
profile('maintenance','do_math/contracts.py do_math/core_engine.py do_math/integration.py do_math/knowledge_io.py',
        '기본 maintenance report/remaining_work에 kind_definition_check 또는 impact_review가 배정 action에 따라 추가된다. definition_id/definition_sha256는 후보와 일치하는 const이며 family/token/meaning/constraints는 등록 정의다. 일반 report가 독립 판정을 대신하지 않는다.')
for stage in ('initial','organize','answer','judge'):
    profile(stage,'do_math/review_cycle.py do_math/review_engine.py do_math/core_engine.py',{
        'initial':'initial의 findings[]는 id/statement/evidence, root decision은 match/mismatch/unresolved와 scope_complete다.',
        'organize':'organize.issues[]는 id/finding_refs/answer_role_slot_id다. finding_refs[]는 stage(initial/judge/answer), round>=1, slot, id다. root decision은 없으며 판정 역할의 동명 필드를 차용하지 않는다.',
        'answer':'answer.answers[]는 issue_id/disposition(maintain/revise/split/withdraw)/statement/evidence, new_findings[]는 id/statement/evidence/parent_issue_ids다. root decision은 없다.',
        'judge':'judge root decision(match/mismatch/unresolved), scope_complete, issue_verdicts[]와 new_findings[]다. issue_verdicts[].decision은 approved/rejected/unresolved이며 root decision과 별도 enum이다.'}[stage]+' stage_schema와 accept_result/_organize/_answer/_judge가 해당 stage를 소비한다. CLI 문장 검출 공백은 F2로 반환한다.')
profile('research','do_math/review_cycle.py do_math/review_engine.py do_math/submission.py',
        '검토 자리의 supplemental_research는 research_schema의 research_request_id/request_digest/outcome/answer/scope_complete/evidence_refs다. 일반 연구 outcome submitted와 구별하며 answered는 validate_research_answer의 범위·근거·미해결 조건을 따른다. review_research 확장 가족은 비어 있다.')
profile('checkpoint','do_math/observations.py do_math/submission.py do_math/context_store.py',
        'checkpoint.json 객체는 CHECKPOINT_SCHEMA/checkpoint_value/read_checkpoint 소유다. 주 응답 문자열 checkpoint와 구별한다. current_claim/evidence_paths/attempts/remaining_work/next_step/progress_state는 필수, iteration/counters는 선택이다. 예제는 전체 checkpoint 객체이고 evidence 파일의 실재는 예제 문법 승인과 별도다.')
profile('rules','do_math/observations.py do_math/control_transport.py do_math/control_protocol.py',
        'SELF_CHECK_RESPONSE_SCHEMA의 rule_proposal={current_revision,reason,rules}를 validate_rule_proposal/validate_rules/validate_execution_rules로 revision과 선택 profile.observation.rule_bindings에 대조한다. observation_unavailable은 관찰 진단이고 timeout은 고정 window의 대체물이 아니다.')
profile('extensions','do_math/submission.py do_math/integration.py do_math/knowledge_io.py',
        'extension_schema(action)의 가족별 배열이다. preparation.contract_checks[].{task_title,sibling_boundaries}, work.knowledge_metadata[].confirmed_scope 및 planning.task_dispositions[].{task_id,disposition:withdraw,reason}는 다른 가족이다. load_extensions의 JSON parser와 _payload_issues가 닫힌 가족/역할/참조를 검사하며 빈 배열/부재는 요청 없음이다.')
profile('delivery','do_math/submission.py do_math/control_transport.py do_math/submission_tool.py do_math/integration.py do_math/repair_execution.py',
        'producer CLI의 --new-knowledge-id replacement_id 및 draft_path 조기제출/preview는 check_submission/producer_check와 중앙 delivery를 구별한다. capture_eligible와 check.passed는 accepted와 다르다. integration_bundles의 impact_set/basis_refs/authority_refs/profile_refs는 해당 bundle/대상 기록 소유이며 024 운영 retry 두 단락만 재사용한다.')
profile('recovery','do_math/core_engine.py do_math/repair_execution.py do_math/provider_engine.py do_math/scheduled_operator.py do_math/execution_lifecycle.py',
        '설치 repair_target, installation_repair_pending/waiting은 scheduled_operator의 외부 수리 분기다. recovery의 local_termination_confirmed/remote_termination/finished_at, execution.continuation_of와 외부 unknown은 같은 뜻이 아니다. queued/paused를 실제 종료나 원격 성공으로 바꾸지 않는다.')
profile('stop','do_math/execution_window.py do_math/core_engine.py do_math/call_engine.py do_math/wiring.py',
        'finish-request/stop-request 및 execution-window.json은 실행기 제어 파일이다. finish_notice_seconds의 운영 기한과 작업 예산 deadline_source=none을 분리한다. 설치 지문/해시 변화 확인은 core_engine의 기존 경계이며 강한 격리 보증이 아니다.')
profile('formal','do_math/formal.py do_math/formal_preview.py do_math/review_policy.py do_math/review_cycle.py do_math/review_engine.py do_math/academic.py do_math/governance.py',
        'formal_check/preview의 status와 verified/rejected/failed/unavailable/stopped, allowed_axioms/sorryAx 및 toolchain/proof evidence는 formal/lean_preview의 실제 반환이다. review_scope 입력 카운터와 review_followups는 review_policy/review_engine, goal_basis_sha256는 mathematical_goal_basis, 학술 confirmed/succeeded/completed는 academic의 별도 소비다. P03/P08/P10의 검수된 정확 성질만 재사용한다.')
profile('history','do_math/core_engine.py do_math/context_store.py do_math/planning.py do_math/contracts.py',
        'recent_history/preparation_history의 종료 실행 행과 ongoing_work의 실행/action 행은 _context의 서로 다른 투영이다. task_catalog.source_ref/현재 tasks 모집단과 ready_task_ids는 선택 권한을 늘리지 않는다. action_source와 configuration_source는 원문 참조이며 이전 실패를 현재 승인으로 바꾸지 않는다.')
profile('provider','do_math/claude_stream.py do_math/claude_worker.py do_math/codex_worker.py do_math/codex_adapter.py do_math/model_call.py do_math/session_slots.py do_math/provider_final.py',
        'CLI argv의 danger-full-access/never/bypassPermissions 및 stream-json/init/result/modelUsage/agent_message/final.txt는 해당 공급자 worker/parser 소유다. Claude final_path 부재와 structured_output 비요구는 명시 음성 설명이다. 로컬 슬롯 execution_attempts/Job 종료를 원격 호출·청구·OS 격리로 확대하지 않는다.')
profile('verification','probe_cli.py run_tests.py',
        'scripts/tests/와 probe_cli.py는 설치 파일/명령 경로다. --skill-only는 모델 없는 설치 구조 검사이며 실호출과 다르다. 이 조사에서는 어느 runner/probe도 실행하지 않았다.')
profile('wait','do_math/revisions.py do_math/core_engine.py do_math/repair_execution.py do_math/task_scope.py do_math/questions.py do_math/provider_wait.py do_math/execution_window.py do_math/claude_stream.py do_math/reporting.py do_math/cli_contract.py',
        'revision_dependency/targets/delegated_targets와 decision_basis/review_basis_key는 개정·현재성 소유다. error_kind와 output_validation은 repair_execution의 수신/후속 분류다. question_links/resolution_history/question_answer는 questions의 질문별 대상 계약, provider_waits는 provider_wait, 마무리 필드는 execution_window, usage 구간은 claude_stream, timeline/status/input_metrics는 reporting/cli_contract의 별도 투영이다.')
profile('revision','do_math/revisions.py do_math/task_scope.py do_math/task_contracts.py do_math/core_engine.py',
        'revision_targets/delegated_targets/revision_request_action_id/revision_resolutions와 pending_revisions/blocked_actions는 개정의 미완료·위임·해소를 다룬다. decision_basis와 review_basis_key는 실제 판단 전제의 현재성을 확인하며 단순 snapshot 전진과 다르다.')
profile('failure','do_math/repair_execution.py do_math/call_engine.py do_math/integration.py do_math/model_call.py',
        'execution.error_kind의 output_parse/output_schema/output_contract/input_failure, publication_failure/submission_failure/currentness_changed/provider_limit/execution_failure/model_policy는 실제 수신/분류/후속의 값이다. integration.currentness만 있는 반환과 혼합 반려를 구분한다. lineage_id/refresh/recovery는 각 후속의 원 실행 결속이다.')
profile('question','do_math/questions.py do_math/question_engine.py do_math/governance.py',
        'question_links의 owner/status/resolution_history와 question_answer/resolves_questions/target_ids/unresolved_target_ids는 질문별 실제 영향 집합과 사용자 원문을 소유한다. --responds-to는 CLI 원문 접수에 연결되고 confirmed_question_ids는 독립 대조 결과다. import_user_decision/import_application_authority는 해당 원문/봉인 승인으로만 해소한다.')
profile('provider_wait','do_math/provider_wait.py do_math/model_policy.py do_math/reporting.py',
        'claude_only_assigned_model 설정과 provider_waits waiting/checking/available, 공개 open은 공급자 재관찰·호출 허용을 나타낸다. 이전 정상 응답은 새 제한 generation을 해제하지 않으며 외부 unknown 재전송 권한도 아니다.')
profile('scheduler','do_math/scheduled_operator.py operator_bootstrap.py do_math/cli_contract.py',
        'operator wake/status/hold는 실제 mode choices와 예약 감독의 wake 조회/정리·HOLD 검사다. 모델 없는 진입점 요청과 연구 action의 권한/슬롯 관문은 별도다. 현재 task는 OS 예약을 호출하지 않는다.')
profile('usage','do_math/claude_stream.py do_math/model_call.py do_math/call_engine.py',
        'origin.kind=task-notification의 후속 init/result를 parse_response가 선택하며 usage_segments/usage는 구간, model_usage_reported는 마지막 누적, usage_scope는 범위다. 누적을 매 구간 더하지 않으며 원출력을 보존한다.')
profile('timeline','do_math/reporting.py do_math/cli_contract.py',
        'timeline의 --repository/--instance/--snapshot/--format/--timezone/--include-operations는 build_parser의 해당 명령 인자다. reporting.timeline/timeline_csv가 고정 snapshot 실행행과 별도 운영로그의 unit/evidence_source를 분리한다. Asia/Seoul은 시간대 예시이며 새 제품 필드가 아니다.')
profile('metrics','do_math/contracts.py do_math/call_engine.py do_math/context_store.py',
        'prompt_metrics/call_engine이 input_metrics의 UTF-8 byte 분해와 총량을 보존하고 source_ref로 축소 전 원문을 회수한다. 토큰·청구액으로 환산하지 않는다.')
profile('status','do_math/reporting.py do_math/cli_contract.py',
        'status.operating_summary는 status_report의 같은 snapshot 파생 투영이다. lifecycle/workspace/차단/다음소유자·지속정책·grant·supervision을 실제 보고가 소유하며 호스트 PID/예약은 operator status의 별도 현장관측이다.')

def occurrence_profile(section,line,default):
    # Exact current paragraph coordinates, explicitly authored after source read.
    if section==260:
        if 869<=line<=871: return 'operation'
        if line==875: return 'recovery'
    if section==264:
        if line==909: return 'formal'
        if 911<=line<=917: return 'scope'
        if 919<=line<=923: return 'audit'
    if section==268:
        if line<=983: return 'revision'
        if line<=995: return 'failure'
        if line==997 or line==1001: return 'question'
        if line==999: return 'provider_wait'
        if line==1003: return 'scheduler'
        if line==1005: return 'stop'
        if line==1007: return 'usage'
        if 1009<=line<=1014: return 'timeline'
        if line==1016: return 'metrics'
        if line==1018: return 'status'
    return default

section_profiles={53:'activity',59:'universal_lifecycle',71:'universal_lifecycle',81:'audit',82:'scope',93:'delivery',101:'ontology',106:'record',107:'ontology',115:'universal_lifecycle',119:'contract',123:'prepare',131:'repetition',133:'activity',149:'delivery',153:'input',160:'rules',187:'initial',189:'judge',190:'record',192:'audit',
    236:'input',237:'overflow',238:'currentness',239:'envelope',240:'prepare',241:'contract',242:'plan',243:'work',244:'scope',245:'audit',246:'operation',247:'intent',248:'maintenance',249:'initial',250:'initial',251:'organize',252:'answer',253:'judge',254:'research',256:'checkpoint',257:'rules',258:'extensions',259:'stop',260:'delivery',261:'recovery',262:'recovery',263:'stop',264:'formal',265:'history',266:'provider',267:'verification',268:'wait'}

def classify(section, token, key):
    # Names explicitly denied or used as notation never acquire a field schema.
    if token in {'K','F','U','검증된 수학 지식','알려진 수학','논리적 폐쇄','원장 변경','원자료','자료·근거','정보 상태','계약 검토','계획자','최종 선택','루트','래퍼','작업자','범위 계획자','검토 주기','논리 자리'}:
        return '개념 표기/명시 동의어 또는 금지 동의어', 'GLOSSARY 도입의 보편 정의 경계 및 이 절의 명시 정의가 정본이다. literal 코드 필드나 지원 보증으로 해석하지 않는다.'
    if token=='{id, version}':
        return '명시 음성 예시', '후보 profile_refs의 실제 PROFILE_REF는 id/revision/sha256이며 version은 허용 필드가 아니다.'
    if section==246 and token=='decision':
        return '명시 음성 예시', 'operational_review 주 응답에 이 root 필드를 쓰지 말라는 문장이다. disposition.kind와 구별한다.'
    if token in {'--output','replacement_id'} and section==260:
        return '명령 인자/조건부 필드', '--new-knowledge-id에는 --output을 주지 않는 음성 설명과 이후 submit 경로의 --output 허용을 구분한다. replacement_id는 지식 변경의 선택 새 ID다.'
    if '/' in token or token.endswith(('.py','.json','.md','.jsonl','.txt','.zip')) or token in {'TK-','KN-','schema.json'}:
        # A dotted array property containing [] is a property, not a filename.
        if '[]' not in token and not token.startswith(('status.','input_manifest.')) and not token.startswith('{'):
            return '파일·경로·참조/CLI 표기', '구체 파일/실행별 placeholder 또는 명령·선택지 표기다. 해당 절 소유 경계에서 생성/소비하지만 이름 존재를 파일 실재·접근·성공 증거로 삼지 않는다.'
    if token.startswith('{'):
        return '부분 객체·필드 집합 표기', '문장에 지정된 소유자의 부분 모양이며 완전 주 응답 예제가 아니다. 필수 여부와 허용 값은 실제 schema/수신 검사로 확인한다.'
    if key:
        return '명시 소유 코드 이름·값·조합', P[key]['judgment']
    return '보편 개념', '보편 개념·표현의 정의이며 코드 필드/명령의 지원을 주장하지 않는다. GLOSSARY 도입5행의 구현 비보증 경계를 적용한다.'

sections=read(OUT/'slice-map.json')
decisions=[]
for s in sections:
    n=int(s['id'].split('-')[1]); key=section_profiles.get(n)
    names=collections.defaultdict(list)
    for o in s['inline_occurrences']:
        owner=occurrence_profile(n,o['line'],key)
        names[(o['name'],owner)].append(o['line'])
    occurrences=[]
    for (token,owner), lines in names.items():
        category,reason=classify(n,token,owner)
        occurrences.append({'name':token,'lines':lines,'classification':category,'owner_profile':owner,'reason':reason})
    conclusion='유지'
    if n==243: conclusion='문구 수정'
    elif n in {250,251,252,253,256}: conclusion='검사 보강'
    elif n in {237,260}: conclusion='기존 근거 재사용'
    decisions.append({'id':s['id'],'document':s['document'],'current_lines':[s['current_start'],s['current_end']],
        'heading':s['heading'],'owner_profile':key,'conclusion':conclusion,
        'reason':P[key]['judgment'] if key else '이 절은 보편 개념/절 구획을 정의한다. GLOSSARY 도입의 구현 비보증을 유지하며 코드 이름이 없는 문장을 임의 필드로 등록하지 않는다.',
        'names':occurrences,'no_inline_reason':None if names else ('절 구획 제목이며 독립 이름 주장이 없다.' if len(s['text'].strip().splitlines())==1 else '산문 개념·권한·보증 경계의 정의다. 문장을 읽었으며 명시 코드 이름을 주장하지 않는다.')})

# Bare names in prose/table/fences not captured by backticks. These are bounded
# explicit claims, not a search for all dictionary words in the repository.
bare={
236:('workspace action task knowledge_catalog sources kind_definitions scholarly submission_contract reference_catalog proposal','input'),
243:('knowledge relations remaining_work checkpoint declaration_names dependencies','work'),
247:('source_range.start source_range.end','intent'),
250:('findings[].id findings[].statement findings[].evidence','initial'),
251:('issues[].id issues[].finding_refs issues[].answer_role_slot_id finding_refs[].stage finding_refs[].round finding_refs[].slot finding_refs[].id','organize'),
252:('answers[].issue_id answers[].disposition answers[].statement answers[].evidence new_findings[].id new_findings[].statement new_findings[].evidence new_findings[].parent_issue_ids','answer'),
253:('issue_verdicts[].issue_id issue_verdicts[].decision issue_verdicts[].reason issue_verdicts[].evidence','judge'),
254:('research_request_id request_digest outcome answer scope_complete evidence_refs','research'),
256:('current_claim evidence_paths attempts remaining_work next_step progress_state iteration counters','checkpoint'),
265:('previous_output','history'),
268:('timeline --repository --instance --snapshot --format --timezone --include-operations origin.kind=task-notification','wait')}
extra=[]
for n,(tokens,key) in bare.items():
    s=next(s for s in sections if s['id']==f'N01-{n:03}')
    extra.append({'section':s['id'],'owner_profile':key,'names':tokens.split(),'scope':'code fence keys or explicit prose-to-schema projection; names with []/. denote containing-owner paths, not new fields',
                  'lines':[s['current_start'],s['current_end']]})

# Source SHA + actual AST declarations make all owner references inspectable.
paths=sorted({r.split(':',1)[1] for p in P.values() for r in p['definitions']})
sources=[]
for relative in paths:
    path=ROOT/relative
    assert path.is_file(),relative
    text=path.read_text(encoding='utf-8-sig'); tree=ast.parse(text)
    symbols=[]
    for node in tree.body:
        if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)):
            symbols.append({'name':node.name,'lines':[node.lineno,node.end_lineno]})
            if isinstance(node,ast.ClassDef):
                symbols.extend({'name':node.name+'.'+m.name,'lines':[m.lineno,m.end_lineno]} for m in node.body if isinstance(m,(ast.FunctionDef,ast.AsyncFunctionDef)))
        elif isinstance(node,(ast.Assign,ast.AnnAssign)):
            targets=node.targets if isinstance(node,ast.Assign) else [node.target]
            for t in targets:
                if isinstance(t,ast.Name): symbols.append({'name':t.id,'lines':[node.lineno,node.end_lineno]})
    sources.append({'path':'repo:'+relative,'sha256':sha(path),'bytes':path.stat().st_size,'declarations':symbols})

# Confirm only the exact previously reviewed paragraphs, without inheriting
# all meanings of their containing section.
prior=read(RUN/'phases/024/tasks/document-waits/evidence/section-semantic-review.json')
reused=[]
for row in prior['exact_sentences']:
    if row['section'] not in {'N01-237','N01-260'}: continue
    current=next(s for s in sections if s['id']==row['section'])['text']
    for sentence in row['sentences']:
        assert sentence in current,(row['section'],row['token'])
    reused.append({'section':row['section'],'token':row['token'],'sentences':row['sentences'],'scope':'024 exact paragraph only; remaining current section independently judged here'})
save('exact-reuse.json',{'reference':'run:phases/024/tasks/document-waits/evidence/section-semantic-review.json','sha256':sha(RUN/'phases/024/tasks/document-waits/evidence/section-semantic-review.json'),'rows':reused,'manager':'run:phases/024/manager-evidence/section-check.json'})
save('owner-profiles.json',P)
save('source-profiles.json',sources)
save('section-decisions.json',decisions)
save('non-inline-claims.json',extra)
table=['# 배정 절별 결정','', '이름별 원 출현과 소유자는 section-decisions.json, 정의와 SHA는 owner-profiles.json/source-profiles.json, 비인라인 주장은 non-inline-claims.json을 따른다. 조사표는 제품 정본이 아니다.','', '| 절 | 현재 행 | 제목 | 결론 | 소유자 |','|---|---|---|---|---|']
for d in decisions:
    table.append(f"| {d['id']} | {d['current_lines'][0]}–{d['current_lines'][1]} | {d['heading'].replace('|','/')} | {d['conclusion']} | {d['owner_profile'] or '보편 개념/구획'} |")
(OUT/'decision-table.md').write_text('\n'.join(table)+'\n',encoding='utf-8')
print(json.dumps({'sections':len(decisions),'occurrences':sum(len(o['lines']) for d in decisions for o in d['names']),'source_files':len(sources),'conclusions':dict(collections.Counter(d['conclusion'] for d in decisions)),'exact_reused_name_rows':len(reused)},ensure_ascii=False))
