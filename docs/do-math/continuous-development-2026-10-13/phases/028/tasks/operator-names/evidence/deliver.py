"""Finite, section-specific judgments and evidence bindings for operator-names."""
import ast
import collections
import hashlib
import json
import re
from pathlib import Path

REPO=Path('C:/math')
RUN=REPO/'docs/do-math/continuous-development-2026-10-13'
OUT=RUN/'phases/028/tasks/operator-names/evidence'
SKILL='.claude/skills/do-math/'
SCRIPTS=SKILL+'scripts/'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v):(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def ref(p):return 'repo:'+SCRIPTS+p
def runref(p):return 'run:'+p

# Each note names the specific producer/consumer, or explains the non-code term.
N={
1:('유지','frontmatter의 do-math는 스킬 이름·설명이다. 제품 함수나 상태 필드 선언이 없으며 제목 앞 도입 전체(1~9행)를 포함한다.','contracts.py:reading_map'),
2:('기존 근거 재사용','action.role은 queue의 배정 역할이고 render_prompt/prompt_documents가 같은 역할의 문서를 지급한다. 대화의 완독 문구는011의 정확 문장만 재사용하며 이름 판정으로 L01을 인증하지 않는다.','contracts.py:reading_map;contracts.py:render_prompt;do_math/record_schemas/schemas.py:RECORDS'),
3:('유지','do-math·GLOSSARY는 공통 정의의 문서 이름이다. 새 코드 필드가 없으며 목표/지식 축적의 의미 재감사는 배정 밖이다.','contracts.py:reading_map'),
4:('유지','운영 역할·작업 역할은 execution_profiles.WORK_ROLES와 governance.OPERATING_ROLES의 구별이다. 예약 감독은 scheduled_operator.check, 복구는 recovery이며 AI 역할 읽기 표에 감독 역할을 추가하지 않는다. 링크 문서는 실재한다.','do_math/execution_profiles.py:WORK_ROLES;do_math/governance.py:OPERATING_ROLES;do_math/contracts.py:ROLES;do_math/scheduled_operator.py:check'),
5:('유지','연구 흐름의 상위 제목뿐이며 단독 이름·표·명령·객체 주장이 없다.','do_math/contracts.py:reading_map'),
6:('유지','K/F/U는 용어집이 정한 형식 정본/가시 프런티어/미지 지평의 수학적 설명 기호다. Python 상수 존재를 요구하지 않는다. 실제 K 사용 가능성의 소비는 knowledge_view다.','do_math/knowledge_records.py:knowledge_view'),
7:('유지','후보 준비/작업 계약 검토는 research_preparation/task_contract_review 역할이고 후보 계약·평가·자기점검은 각 역할의 schema와 계약 문서 소유다. 승인·선택을 동일 이름으로 합치지 않는다.','do_math/contracts.py:schema_for;do_math/model_policy.py:validate_assessments'),
8:('기존 근거 재사용','selected/not_selected/not_assessable은 PLAN_DISPOSITION의 처분 값이다. plan_settle_seconds는 config 값이고 DispatchEngineMixin의 정산 대기 소비가 소유한다. operator는 명시 제어 출처이며 역할 추가가 아니다. P09/P11의024 정확 정산 문장만 재사용한다.','do_math/contracts.py:PLAN_DISPOSITION;do_math/dispatch_engine.py:_plan_settle_waits;do_math/record_schemas/__init__.py:config_schema'),
9:('기존 근거 재사용','action.revision_targets는 queue 입력, integration_bundles는 submission.extension_schema의 생산자 선언 확장이다. 저장/동적 입력과 혼동하지 않고 P06/P07·023의 지정 적용 성질만 재사용한다.','do_math/record_schemas/schemas.py:RECORDS;do_math/submission.py:extension_schema;do_math/integration.py:inspect_bundles'),
10:('유지','공통 실행·학술자료 활용은 지급 문서 이름이며 체크포인트는 observations.CHECKPOINT_SCHEMA 소유다. scholarly 도구 실측이나 문헌 판독 성공을 새로 주장하지 않는다.','do_math/contracts.py:reading_map;do_math/observations.py:CHECKPOINT_SCHEMA'),
11:('기존 근거 재사용','형식 검사/동일성 검토/목표 감사는 formal_check/identity_review/goal_audit의 별도 역할·기계 작업이다. K는 usable 지식이다. 검토별 권한/봉인/전문 단일지급은022의 정확 성질을 유지한다.','do_math/contracts.py:ROLES;do_math/knowledge_records.py:knowledge_view;do_math/review_cycle.py:context_for'),
12:('유지','새 기술 이름이 없는 연구 판단 설명이다. 연구 진전·목표 상대성의 산문을 필드 선언으로 읽지 않는다.','do_math/contracts.py:schema_for'),
13:('유지','P/H/H→P는 명시적인 수학 설명 예시이며 제품 변수·schema 필드가 아니다. 과제 완료와 목표 만족을 구별하는 현재 용어를 유지한다.','do_math/knowledge_records.py:formal_usable'),
14:('기존 근거 재사용','읽기 표는 contracts.reading_map의 실제 정본이다. common+10역할의 순서/파일 존재를 실제 순수 parser로 확인했다. action.role/stage는 queue, check는 intent_interpretation의 단계, scope는 identity_review의 단계다. implementation_documents는 _context가 지급·manifest에 보존하며 formal_check/예약감독을 AI 행으로 추가하지 않는다.','do_math/contracts.py:reading_map;do_math/contracts.py:action_schema;do_math/core_engine.py:_context;do_math/record_schemas/schemas.py:RECORDS'),
15:('유지','quiesce는 CLI 정비 제어, do-math-cli/5는 RESPONSE_CONTRACT_ID, do-math-state/9는 STATE_CONTRACT_ID다. 두 판본과 역할 의미를 구별한다.','do_math/cli_contract.py:build_parser;do_math/contracts.py:RESPONSE_CONTRACT_ID;do_math/state_contract.py:STATE_CONTRACT_ID'),
16:('유지','next_owner는 CLI 오류 또는 감독 실패의 진단 필드다. 명칭만으로 queue 생성·배정·기동을 증명하지 않는다는 문장과 각 실제 오류 생산자가 일치한다.','do_math/cli.py:_fail;do_math/scheduled_operator.py:run_engine'),
17:('유지','절차 제목·내부 링크만 있다. 후속1~5단계의 개별 원문을 따로 연결했다.','do_math/cli_contract.py:build_parser'),
18:('검사 보강','init/profile/configure는 실제 parser, 설정 키/effort/모델 budget은 config_schema·validate_config·model_policy, scholarly_server는 resolve_scholarly_server 소유다. setup_lean/probe 외부 CLI·파일/모델 예시와 명시 비지원 minimal/ultra를 구별했다. 현재 JSON 설정 예시는 validate_config 통과지만 session_limitz 오타와 setup --watch는 문서 helper가 놓친다(F1/F2).','do_math/cli_contract.py:build_parser;do_math/configuration.py:validate_config;do_math/model_policy.py:validate_policy;setup_lean.py:main;do_math/scholarly_config.py:resolve_scholarly_server;do_math/claude_adapter.py:ClaudePrintAdapter'),
19:('기존 근거 재사용','result.instance_id/snapshot/status는 init 결과, operator_schedule/reconcile_error/null은 별도의 일정 반환 분기다. init JSON은 설명용 응답 봉투이며 QR/RI/OID placeholder를 실제 저장 ID로 승인하지 않는다. B132/B133의 실제 분기/문서 검사를 한정 재사용한다.','do_math/cli.py:execute;do_math/cli.py:_schedule_failure;do_math/cli.py:_emit'),
20:('기존 근거 재사용','immutable_input.text/sha256/bytes는 lifecycle 불변 원입력 세 필드의 축약 표기다. --until-active는 활성화 뒤 연구 배정 전 반환, conversation_loss_policy의 continue_authorized/pause는026~027의 정확 지정 정책 의미를 재사용한다.','do_math/initialization.py:initialize_state;do_math/initialization_engine.py:_initialization_control;do_math/lifecycle_engine.py:_conversation_control'),
21:('유지','operator 모드·반환 분기와 result.json/latest-engine.json 경로는 scheduled_operator.run_engine·supervision이 소유한다. outcome=running은 _job_run 전 기록이다. Win32_Process와 세 속성은 PowerShell CIM 외부 이름이며013 실관측 스크립트/원보고를 연결했다. 새 프로세스나 모델 호출은 없다.','do_math/scheduled_operator.py:run_engine;do_math/supervision.py:engine_run_outcome;operator_schedule.ps1:Task-View;tests/support/scheduler_live.py:INSPECT'),
22:('유지','새 하위 제목인 책임·인계 판단 기준을 포함해192~211행을 원22절에 결속했다. 인계 근거·보고 항목의 산문이며 새로운 코드 필드 선언이 없다.','do_math/reporting.py:operating_summary'),
23:('유지','조회/변경 경로의 제목·링크다. 명령·필드는 바로 이어지는 개별 절에서 판정했다.','do_math/cli_contract.py:build_parser'),
24:('기존 근거 재사용','표의 snapshot/status/goal_status/knowledge/K/질문·대기·trust/assurance는 reporting.status_report의 실제 투영, tasks.assessment_pending은 task_status다. OBSERVED_FIELDS 여섯 값은 snapshot에서 None이다. 실제 반환 검사 unit.test_storage_report_projections와 B132 범위를 재사용하며 표의 bare 필드 전부를 단순 scoped helper의 통과로 인증하지 않는다.','do_math/reporting.py:status_report;do_math/reporting.py:task_status;do_math/reporting.py:OBSERVED_FIELDS'),
25:('유지','run/watch와 call_timeout_seconds는 CLI 배정/운영 프로필 계약이다. 작업/운영 기한과 형식 검사 용량을 구별한다. 새 명령 조합이나 전체 시간 정책을 만들지 않는다.','do_math/cli_contract.py:build_parser;do_math/execution_profiles.py:build_profiles;do_math/dispatch_engine.py'),
26:('유지','--max-steps/--watch는 run parser에 속하며 action 시작 개수와 waiting 감시다. 옵션이 모든 명령에 있다고 보지 않는다.','do_math/cli_contract.py:build_parser;do_math/engine.py:run'),
27:('유지','ready/waiting/capacity_waiting/paused/completed/closed는 runtime.status와 실행 루프의 반환 상태다. 해당 상태와 questions를 읽는 경로를 직접 대조했고 수학적 승인과 분리했다.','do_math/engine.py:run;do_math/reporting.py:status_report;do_math/lifecycle_engine.py'),
28:('기존 근거 재사용','submission_contract.command는 실제 입력 지급, --submit/submit_draft는 중앙 선택적 제출, scratch는 수집 제외 경로다. retry/input_overflow와 request의 retry-action은 실패 활동/기술적 수리 소비자 소유다. P03/P07·024의 지정 문장만 재사용한다.','tests/support/engine_context.py;do_math/context_store.py;do_math/repair_execution.py;do_math/cli_contract.py:build_parser'),
29:('유지','제목만 있고 새 이름 주장/표/객체가 없다.','do_math/control_contracts.py:DECISION'),
30:('유지','input의 --text/--file은 mutually exclusive 사용자 원문 입력이다. 의도 수입/독립검사 경로와 source 파일 수입을 구별한다.','do_math/cli_contract.py:build_parser;do_math/cli.py:execute'),
31:('기존 근거 재사용','decision --file의 kind=charter/record/supersedes/content는 사용자 통치 요청이다. effect/reason은 제어 영수증이고 저장 governance.record와 임의 일반 record를 혼동하지 않는다.023의 정확 통치 경계를 재사용한다.','do_math/control_contracts.py:DECISION;do_math/governance.py;do_math/cli.py:execute'),
32:('유지','source는 CLI 원바이트 수입이며 completed는 task 상태, assessment.current/invalidated_reason은 task 판정의 현재성이다. 기록 보존과 dependency 사용을 구별하는 생산/소비 정의를 연결했다.','do_math/task_scope.py;do_math/record_schemas/schemas.py:RECORDS;do_math/core_engine.py;do_math/cli.py:execute'),
33:('유지','조회 구간의 상위 제목뿐이며 새 이름 주장 없다.','do_math/cli_contract.py:build_parser'),
34:('기존 근거 재사용','query는 records 분기와 files 분기가 다르다. 방향/cursor/snapshot/total/loaded/truncated/next_cursor는 CLI parser·query_records/repository 반환이 소유한다. B132/B134 지정 조회 성질만 재사용한다.','do_math/cli_contract.py:build_parser;do_math/repository.py;do_math/core_engine.py:query_records'),
35:('기존 근거 재사용','read의 id/path 선택·output 제약과 text/base64는 실제 CLI.execute의 파일 반환 분기다. record는 복원된 논리 객체다. B132 지정 read 소비를 재사용한다.','do_math/cli_contract.py:build_parser;do_math/cli.py:execute;do_math/core_engine.py:read_record'),
36:('기존 근거 재사용','query --files의 prefix와 export --all은 실제 repository 조회/내보내기 입력이다. research/runtime와 slash는 POSIX 저장 경로 및 명시 예시다. 조회 사본을 새 정본으로 만들지 않는다.','do_math/cli_contract.py:build_parser;do_math/cli.py:execute;do_math/repository.py'),
37:('유지','pending engine processing/busy/replayed는 제어 영수증·잠금 분기, .control/은 실행별 정지 관리 경로다. unknown은 원격 미관측 범위이고 closed/completed/input_overflow는 서로 다른 상태/실패 분류다. CLI idempotency-key와 request retry-action의 실제 입력 소유를 연결했다.','do_math/core_engine.py;do_math/lifecycle_engine.py;do_math/cli_contract.py:build_parser;do_math/cli_worker.py'),
38:('기존 근거 재사용','operator modes/설정 키/role_tiers.recovery는 실제 parser·config·예약 생산자다. PT0S는 Windows duration 표현, execution_limit는 Task-View 반환이다. 정상probe/HOLD/조회오류는027 정확 row를 재사용한다. 고정 bootstrap/PS 경로는 설치 시 제공되며 독립운영 링크 문장의 다른 의미까지 재감사하지 않는다.','do_math/cli_contract.py:build_parser;do_math/scheduled_operator.py;operator_schedule.ps1;operator_bootstrap.py;do_math/record_schemas/__init__.py:config_schema'),
39:('유지','여덟 CLI 제어 synopsis는 parser와 control_contracts.PAYLOADS의 실제 동작을 가리킨다. confirmed는 외부 원장 상태이며 HTTP 성공과 다르다. .../AC-ID는 메타변수로 필수 runtime 인자 생략 synopsis다.','do_math/cli_contract.py:build_parser;do_math/control_contracts.py:PAYLOADS;do_math/external.py'),
40:('유지','accepted/effect/reason은 CLI 제어 접수·적용 영수증 필드다. exit0을 연구 승인으로 해석하지 않는 문장과 실제 _control/_emit를 연결했다.','do_math/cli.py:_control;do_math/cli.py:_emit;do_math/core_engine.py'),
41:('유지','danger-full-access/never/bypassPermissions는 공급자 worker argv와 어댑터 옵션의 실제 외부CLI 이름이다. 기존 사용자 권한과 Job 수명 관리의 범위를 명시하며 강한 OS 보안 격리로 확대하지 않는다.','do_math/codex_adapter.py:worker_options;do_math/claude_worker.py'),
42:('기존 근거 재사용','status의 provider_waits/questions/question_links/waiting_actions와 timeline --include-operations는 snapshot 투영과 호스트 관측의 소비자다. operations 경로·UTC/timezone/CSV는 reporting.timeline의 별도 unit이다. B132의 고정 snapshot 및 현재 직접 반환 검사 범위를 재사용한다.','do_math/reporting.py:status_report;do_math/reporting.py:timeline;do_math/trace_report.py'),
43:('검사 보강','scope=installed_skill_structure/status=verified는 preflight.inspect_bundle의 제한된 반환이다. probe_cli/run_tests는 각각 도구 main 소유이며 새 실행하지 않았다. 도구 옵션 조합은 다른 도구 flag 전역 합집합으로 승인될 수 있어 F1에 보강한다. 시간 정책의 일반 의미 감사는 이 이름 작업 밖이다.','do_math/preflight.py:inspect_bundle;probe_cli.py:main;run_tests.py:main'),
44:('검사 보강','claude-opus-5는 외부 모델 식별 예시, claude_only_assigned_model은 실제 설정이며 probe cases/only-assigned-model의 Claude 제한은 probe_cli.main과 model_call의 소비다. 다른 도구 --verify-only 차용이 현재 helper에서 누락되어 F1에 포함한다. 실제 모델 제공/계정 가용성은 새로 관측하지 않았다.','probe_cli.py:main;do_math/configuration.py:validate_config;do_math/model_call.py'),
45:('유지','dispatch_waits.kind=provider_limit는 queue 배정 대기이며 waiting_actions 실패 보류와 다르다. operator wake/status/uninstall은 실제 parser 및 예약 모드다.013의 실제 held wake 하위 경계만 재사용한다.','do_math/provider_wait.py;do_math/scheduled_operator.py:reconcile_wake;do_math/reporting.py:dispatch_waits;do_math/cli_contract.py:build_parser'),
46:('유지','input --responds-to는 반복가능 옵션, resolves_questions는 사용자 구조화 decision의 질문 참조다. 질문 수입·검사와 일반 resume를 구별한다.','do_math/cli_contract.py:build_parser;do_math/control_contracts.py:DECISION;do_math/question_engine.py'),
269:('유지','trust_activate는 기계 action, payloads는 물리 저장 코덱의 참조다. dmCli/Repository/Instance는 PowerShell 예시 지역 변수이며 사용자 실제 값 필요를 명시한다. --file/effect/accepted는 CLI 입력/영수증이다.','do_math/formal_engine.py;do_math/payloads.py:encode;do_math/cli_contract.py:build_parser'),
270:('기존 근거 재사용','result.snapshot/items[].path는 query_result, lifecycle.immutable_input은 저장 원문이며 user_request.text는 역할 입력이다. 두 관찰 창/주기/config_sha256은 config 및 능력 관측 대상이다. representative_check_seconds와 observation_window_warnings는 실제 설치/초기화 반환이며025 지정 신뢰 성질과 기존 status/query 경계를 재사용한다.','do_math/initialization.py;do_math/initialization_engine.py;do_math/reporting.py:status_report;do_math/trust_inventory.py:representative_check_seconds;do_math/cli.py:execute'),
271:('유지','완전한 통치 JSON의 kind/operation/records와 두 governance record·content는 DECISION/GOVERNANCE_RECORD/저장 governance 정의로 대조했다. 파일명01-governance는 운영자가 만들 예시다. 원문 승인 및 독립 적용을 새 실행으로 인증하지 않는다.','do_math/control_contracts.py:DECISION;do_math/control_contracts.py:GOVERNANCE_RECORD;do_math/initialization_engine.py:_initialization_control'),
272:('검사 보강','두 완전 grant 요청의 roles/task_ids/reuse/expires_at는 control GRANT와 governance의 local 권한이다. formal_check는 기계 작업으로 research grant에만 포함된다. 날짜는 명시 placeholder다. budget_kind 차용 반례는 실제 closed GRANT가 반려하나 문서 helper는 JSON을 검사하지 않아 F2에 보강한다.','do_math/control_contracts.py:GRANT;do_math/control_contracts.py:DECISION;do_math/governance.py:normalized_grant;do_math/initialization_engine.py:_initialization_control'),
273:('문구 수정','현행 설정/probe/adopt/profile_ref·선택 반환과026~027 정책 문장은 지정 성질을 재사용한다. 그러나 Codex 식별 모듈을7개, Claude를10개로 열거하는180행은 실제 identity_modules14/17개와 다르다. 빠진7개와 source/test를 identity-module-mismatch에 보존했다. F3로 정확 문구 및 집합 일치 검사를 반환한다.','do_math/codex_adapter.py:CodexExecAdapter.identity_modules;do_math/claude_adapter.py:ClaudePrintAdapter.identity_modules;do_math/initialization_engine.py:_initialization_control;do_math/model_policy.py:selection'),
274:('검사 보강','setup 모드·반환/status와 등록의 다섯 키/allowed_axioms/record binding은 실제 producer다. toolchain.project.search_paths/null·registration은025의 정확 성질만 재사용한다. 작은 transition JSON은 trust PAYLOADS 구조로 확인했다. setup 모드/인자 guard가 문서 helper에 결속되지 않은 F1만 새 보강으로 남긴다.','setup_lean.py:main;do_math/trust_inventory.py:registration_request;do_math/trust_validation.py:register_request_errors;do_math/formal.py:inspect_toolchain'),
275:('기존 근거 재사용','import_units/unit_id/check.sha256은 수입·독립 검사, import_approval의 bundle/check/unit_hashes는 원문·봉인 승인 입력이다. apply_import_control은 governance의 실제 수신자다. immutable_input/user_request와 lifecycle/knowledge/events를 구별하며023·027 지정 소비를 재사용한다. 승인 JSON 해시 placeholder를 유효 승인으로 해석하지 않는다.','do_math/governance.py:apply_import_control;do_math/governance.py:import_approval_draft;do_math/initialization.py:initial_intent_evidence;do_math/initialization_engine.py'),
276:('유지','초기화/정비 문서의 도입 설명이며 새 단독 코드 이름이나 예시 객체가 없다.','do_math/trust_inventory.py'),
277:('유지','olean suffix와 setup_lean은 지문 모집단·기록 작성자다. 판본/지문/내용hash 세 의미를 이름 판정에서 합치지 않는다.','do_math/trust_inventory.py:JUDGMENT_SUFFIXES;setup_lean.py:record_installation'),
278:('유지','trust register는 실행 가능한 하위 명령이 아니라 trust PAYLOADS.operation=register의 산문 축약이다. 옆 링크의 실제 명령은 trust --file이다. trust_activate는 기계 작업, match/satisfied는 서로 다른 판정 값, formal_usable/environment_check는 실제 형식 사용/반환 이름이다. setup flags 검사는 F1의 같은 도구 범위다.','do_math/control_contracts.py:PAYLOADS;do_math/formal_engine.py;do_math/knowledge_records.py:formal_usable;do_math/trust_validation.py:check_environment;setup_lean.py:main'),
279:('기존 근거 재사용','environment_check.changed_files는 지문 불일치 분기의 실제 반환이고 changed_file_count/errors/identity_errors도 그 소유자 문맥이다. formal_environment/authority/stopped/submission_publication은 대기 이름, trust_governance는 다음 담당이다. trust register/transition은 JSON operation 축약이다.025의 조건부 부재/50제한/재결박 성질을 재사용한다.','do_math/trust_validation.py:check_environment;do_math/formal_engine.py;do_math/formal.py;do_math/dispatch_engine.py'),
280:('유지','--check-contents/--rerecord는 setup의 서로 다른 모드, passed/mismatch는 trust_inventory.content_check 결과다. 감독의 주기 자동점검이란 의미로 읽지 않는다.','setup_lean.py:check_contents;do_math/trust_inventory.py:content_check'),
281:('기존 근거 재사용','파일 suffix/lean-toolchain/lake-manifest/lakefile/formal.py는 실제 판정 입력 또는 명시 제외다. os.scandir는 표준 라이브러리 callable로 실제 helper 확인, inspect_toolchain/project.source_identity는 형식 생산자다.025 지정 null/source_identity 성질만 재사용한다.','do_math/formal.py:inspect_toolchain;do_math/trust_inventory.py:observe_fingerprint;do_math/trust_inventory.py:JUDGMENT_SUFFIXES'),
282:('유지','schema/identity/baselines/checks는 RECORD_SCHEMA의 물리 기록 필드, do-math-toolchain-record/1은 SCHEMA 상수다. toolchain_record/validation_receipt는 환경 기록, runtime.trust_bindings는 별도 map이다. 대표 검사 Mathlib/norm_num은 Lean 코드 예시이고 소요 초는 실제 producer다.','do_math/trust_inventory.py:RECORD_SCHEMA;do_math/trust_inventory.py:representative_check_seconds;do_math/record_schemas/schemas.py:RECORDS;do_math/record_schemas/schemas.py:RUNTIME_FIELDS'),
283:('검사 보강','모드 표/종료 코드/status/record_path/id/binding/mismatched는 setup.main·trust_inventory의 분기별 반환이다. records/.lock은 OS lock 파일명이고 수동삭제 대상이 아니다. --command-file 모드 제약·타 도구 flag 차용은 F1에 같은 도구 정본으로 보강한다.','setup_lean.py:main;do_math/trust_inventory.py;do_math/file_io.py:os_lock'),
284:('유지','lake 제외와 NTFS 위험은 명시된 비보증 범위다. Python 이름의 결함으로 만들거나 새 OS 실험을 수행하지 않는다.','do_math/trust_inventory.py:JUDGMENT_SUFFIXES'),
285:('유지','payloads는 payloads.encode의 물리 참조, payload_refs/json_pointer_scope=decoded_record는 read_record의 복원된 논리 반환이다. request_source_ref는 prepare_role_input의 큰 요청 상세 파일 참조다. 실제 소비를 확인하고 별도 input schema를 복제하지 않는다.','do_math/payloads.py:encode;do_math/payloads.py:decode;do_math/core_engine.py:read_record;do_math/context_store.py:prepare_role_input'),
286:('유지','launch_ticket는 launch의 소유·시작 기록, not_started는 실제 로컬 시작 실패다. PID/FILETIME/Job은 OS 정체/수명 이름이다. 현 소비와 기존 Jobs 근거만 연결하며 메타데이터 부재를 종료 확인으로 만들지 않는다.','do_math/launch.py;do_math/execution_lifecycle.py;do_math/ports/jobs.py'),
287:('유지','quiesce/release-quiesce/--fence는 CLI 정비 제어, maintenance_fence.state의 quiescent/draining/blocked는 runtime 정비 기록과 재구성 상태다. effect=applied와 실제 종료를 구별한다.','do_math/cli_contract.py:build_parser;do_math/lifecycle_engine.py;do_math/record_schemas/schemas.py:RUNTIME_FIELDS'),
288:('유지','operations/live/errors는 로컬 trace의 동적 경로, operation_progress.telemetry_errors는 progress 실제 반환이다. FileRenameInfoEx·두 Flags는 file_io._replace_once가 Win32 SetFileInformationByHandle에22/3으로 전달하는 외부 이름이다.018 실제 atomic-replace row/현재 소스 불변을 재사용하며 Python 심볼 부재를 결함으로 만들지 않는다.','do_math/operation_trace.py;do_math/trace_report.py:progress;do_math/file_io.py:_replace_once;do_math/file_io.py:atomic_replace'),
}

# Correct shorthand roots are expanded once, then every occurrence refers to
# that section's explicitly described ownership rather than a repo-wide word hit.
def owners(spec):
    result=[]
    for item in spec.split(';'):
        if not item.startswith(('do_math/','tests/')) and item=='contracts.py:reading_map': item='do_math/'+item
        if item.startswith('contracts.py:'): item='do_math/'+item
        file,sep,symbol=item.partition(':')
        assert (REPO/SCRIPTS/file).is_file(), file
        result.append({'path':ref(file),'symbol':symbol or 'module declarations and consumers',
                       'sha256':sha(REPO/SCRIPTS/file)})
    return result

sections=read(OUT/'section-profiles.json')
assert set(N)=={int(s['id'].split('-')[1]) for s in sections}
def classification(token,number):
    if token in {'minimal','ultra','claude --bare'}: return '명시 비지원/비사용 외부 예시'
    if token.startswith('$'): return 'PowerShell 예시 지역변수'
    if token in {'Get-CimInstance Win32_Process','ProcessId','ParentProcessId','CommandLine','Running','PT0S','FileRenameInfoEx','REPLACE_IF_EXISTS | POSIX_SEMANTICS','os.scandir(...)'}: return '외부 OS/표준 라이브러리 이름·표현'
    if re.search(r'\.(md|py|json|exe|txt|jsonl)$',token) or '/' in token and not token.startswith('immutable_input.') or token in {'.olean','.exe','.dll','.so','.dylib','.lean','.lake','.ilean','.trace','.hash','.c','.ir','lean-toolchain'}: return '파일/동적 경로/명시 suffix; 필드 존재와 구별'
    if token in {'jsonschema==4.26.0','codex exec','claude --print','claude auth status','PATH','CLAUDE_CONFIG_DIR','claude:opus','claude:sonnet','claude:haiku','claude:','claude-','gpt-5.6-sol','claude-opus-5','import Mathlib','norm_num','True','propext','Classical.choice','Quot.sound','n + 0 = n','danger-full-access','never','bypassPermissions'}: return '외부 CLI/의존성/모델 또는 Lean 이름; 설치/호출 성공 미주장'
    if token.startswith('--') or token.split(' ')[0] in {'init','run','status','profile','operator','input','decision','configure','request','query','read','source','knowledge','trust','external','conversation','export','check','quiesce','resume','close','uninstall','select-profile'}:return '해당 명령의 parser/JSON operation/메타변수 조합'
    if token in {'지문 불일치와 재기록'}:return '문서 절 제목'
    return '해당 절의 생산/소비 객체 필드·역할·상태/선택 값; 상세 소유 설명 참조'

decisions=[]
for s in sections:
    number=int(s['id'].split('-')[1]);verdict,note,spec=N[number]
    owned=owners(spec)
    decisions.append({'id':s['id'],'document':s['document'],'heading':s['heading'],
       'historical_lines':[s['start_line'],s['end_line']], 'current_lines':[s['current_start'],s['current_end']],
       'document_sha256':s['sha256'],'conclusion':verdict,'detail':note,'owners':owned,
       'inline_occurrences':[{**o,'classification':classification(o['text'],number),'owner_scope':s['id']} for o in s['inline']],
       'tables_commands_and_prose':'현재 절 전문의 표/명령·JSON fence/산문을 current-sections.md 및 section-profiles.json.text/code_lines에서 확인. 인접 원절과 구별.',
       'no_inline_names_reason':None if s['inline'] else note,
       'json_examples':'json-example-bindings.json' if any(x['section']==s['id'] for x in read(OUT/'json-example-bindings.json')) else None})
save('section-decisions.json',decisions)

bindings=[
 {'id':'commands','sections':[s['id'] for s in sections if any(classification(o['text'],int(s['id'].split('-')[1])).startswith('해당 명령') for o in s['inline'])],
  'test':'structure.test_doc_code.DocumentCodeTests.test_documented_commands_and_options_exist',
  'file':'tests/structure/test_doc_code.py','symbols':['test_documented_commands_and_options_exist','test_another_commands_flag_cannot_validate_the_documented_command','test_operator_modes_use_the_actual_parser_for_bare_and_entry_commands'],
  'scope':'do_math.py/$dmCli 및 bare synopsis의 command+flag, operator mode choices. setup_lean/probe/run_tests는 ENTRY 밖이므로 F1. 예시 필수 실제 값/OS 실행/모델 가용성은 검사하지 않는다.'},
 {'id':'scoped-names','sections':['N01-002','N01-009','N01-014','N01-020','N01-024','N01-028','N01-032','N01-270','N01-273','N01-275','N01-279','N01-281','N01-287','N01-288'],
  'test':'structure.test_doc_code.DocumentCodeTests.test_documented_scoped_fields_belong_to_their_actual_schema',
  'file':'tests/structure/test_doc_code.py','symbols':['test_documented_scoped_fields_belong_to_their_actual_schema','test_a_field_from_another_family_cannot_validate_a_scoped_name','test_all_dotted_document_fields_have_an_owner','test_array_paths_follow_items_instead_of_borrowing_parent_or_map_fields'],
  'scope':'순수 dotted paths의 실제 owner/line-local alias/array items. bare필드나 slash 압축·JSON 키·class의 module 목록 조합은 범위 밖. defer된 반환은 해당 실제 소비 시험이 맡는다.'},
 {'id':'policy','sections':['N01-020','N01-273'],
  'test':'structure.test_doc_code.DocumentCodeTests.test_documented_policy_names_have_installed_owners',
  'file':'tests/structure/test_doc_code.py','symbols':['test_documented_policy_names_have_installed_owners','test_an_undefined_policy_is_not_accepted_as_an_arbitrary_code_word'],
  'scope':'policy 이름의 실제 schema/module 선언. 026 다섯 의미 및027 기본방침 저장·연결 양쪽 정책은 별도 정확 consumer 단언/원보고만 재사용.'},
 {'id':'reading-map','sections':['N01-002','N01-004','N01-014'],
  'test':'unit.test_planning_reading_map.ReadingMapTests.test_role_rows_add_their_references_after_the_common_documents',
  'file':'tests/unit/test_planning_reading_map.py','symbols':['test_declared_shared_procedures_are_supplied_in_reading_order','test_role_rows_add_their_references_after_the_common_documents','test_missing_or_ambiguous_reading_map_is_an_error'],
  'scope':'actual prompt_documents/render_prompt의 순서·원bytes·hash, 빠진 문서/중복 표 반려. 이번 actual reading_map 순수 관찰과 기존 source 단언을 연결하며 새 테스트 실행 또는 독해/준수 성공으로 세지 않는다.'},
 {'id':'status-query','sections':['N01-019','N01-024','N01-034','N01-035','N01-036','N01-042','N01-270','N01-273'],
  'test':'unit.test_storage_report_projections.ReportProjections',
  'file':'tests/unit/test_storage_report_projections.py','symbols':['test_status_refuses_unknown_observation_before_rendering','test_human_report_preserves_loaded_initialization_blocker_and_machine_finding'],
  'scope':'status 실제 반환·snapshot null 관측과 명시 status/result owner. init/schedule/select/query/read의 정확 B132~B134 직접 소비는 binding-inventory의 source와 현재 구현을 연결해 재사용 범위를 제한한다.'},
 {'id':'current-policy-store','sections':['N01-020','N01-273'],
  'test':'sim.test_initialization_controls.InitialAdoptionTests',
  'file':'tests/sim/test_initialization_controls.py','symbols':['test_default_review_policy_is_generated_from_current_config_and_saved','test_explicit_review_policy_takes_precedence_over_default_adoption','test_each_adoption_field_refuses_what_it_does_not_name'],
  'scope':'공개 adopt→실제 store.load/restart의 독립3/2/17/hash, explicit 객체 우선, stale/누락.027 c3 해당 passed row와 현재SHA 재사용.'},
 {'id':'connection-store','sections':['N01-020','N01-037','N01-273'],
  'test':'sim.test_lifecycle_engine_public.PublicControlBoundaryTests.test_resume_requires_a_live_generation_newer_than_the_lost_generation',
  'file':'tests/sim/test_lifecycle_engine_public.py','symbols':['test_resume_requires_a_live_generation_newer_than_the_lost_generation'],
  'scope':'instance/runtime 정책·generation/source_ref를 양쪽 저장/restart에 독립 단언한다.026의 이전SHA를 그대로 재사용하지 않고027 c3 새 판본을 쓴다.'},
 {'id':'probe','sections':['N01-038'],
  'test':'sim.test_operator_finish_cli.OperatorCommandTests',
  'file':'tests/sim/test_operator_finish_cli.py','symbols':['test_normal_probe_observes_without_calling_a_model_or_starting_research','test_probe_status_failure_returns_its_error_without_a_required_model_marker'],
  'scope':'정상observed/no-model/no-start와 조회오류/HOLD 분기의 marker 부재를 구별.027 c3 실제 passed row에 결속하며 README의 다른 복구 의미까지 인증하지 않는다.'},
 {'id':'trust','sections':['N01-270','N01-274','N01-278','N01-279','N01-281','N01-282','N01-283'],
  'test':'structure.test_doc_code.DocumentCodeTests.test_trust_fields_require_actual_inspection_and_environment_return',
  'file':'tests/structure/test_doc_code.py','symbols':['test_trust_fields_require_actual_inspection_and_environment_return','test_deferred_trust_has_the_assigned_actual_document_check'],
  'scope':'defer_trust는 자체 성공이 아니다.025의 실제 inspection/environment 반환으로 null/분기별부재·50 제한/재결박을 검사했고 현doc/producer/test SHA와 manager 검수만 재사용한다. setup 모드표 조합은 F1.'},
 {'id':'identity-modules','sections':['N01-273'],
  'test':'sim.test_provider_collection.IdentityTests.test_capability_identity_has_host_worker_and_cli_hashes',
  'file':'tests/sim/test_provider_collection.py','symbols':['test_capability_identity_has_host_worker_and_cli_hashes'],
  'scope':'현재 시험은 actual capability_identity module 집합14/17을 정확 단언하지만 문서180행을 읽지 않는다. 해당 생산자 속성 자체가 정본이고 문서 누락7개/조합은 F3. 이번 시험을 실행하지 않았다.'},
 {'id':'atomic-os','sections':['N01-288'],
  'test':'boundary.test_storage_atomic_replace.MetadataPublicationTests',
  'file':'tests/boundary/test_storage_atomic_replace.py','symbols':['test_reader_keeps_one_version_without_blocking_atomic_replacement','test_sharing_failure_retries_only_the_same_rename','test_permanent_failure_is_bounded_and_unrelated_errors_are_not_retried'],
  'scope':'실제 Win32 rename/read-sharing·같은 rename 반복·5/32/2 반려를018 c4 해당 row/현재 product+test SHA에 결속해 한정재사용한다. 외부 명칭을 Python 변수로 찾는 검사는 적용하지 않는다.'},
]
for b in bindings:
    p=REPO/SCRIPTS/b.pop('file');b['path']='repo:'+p.relative_to(REPO).as_posix();b['sha256']=sha(p)
    tree=ast.parse(p.read_text(encoding='utf-8-sig'));lines=p.read_text(encoding='utf-8-sig').splitlines()
    methods=[]
    for symbol in b.pop('symbols'):
        nodes=[x for x in ast.walk(tree) if isinstance(x,(ast.FunctionDef,ast.AsyncFunctionDef)) and x.name==symbol]
        assert len(nodes)==1,(p,symbol)
        x=nodes[0];text='\n'.join(lines[x.lineno-1:x.end_lineno])
        methods.append({'symbol':symbol,'lines':[x.lineno,x.end_lineno],'body_sha256':hashlib.sha256(text.encode()).hexdigest(),
                        'assertion_calls':sorted({call.func.attr for call in ast.walk(x) if isinstance(call,ast.Call) and isinstance(call.func,ast.Attribute) and call.func.attr.startswith('assert')})})
    b['methods']=methods
save('test-bindings.json',bindings)

# Read the original input inventories without adopting their old coordinates
# or treating their counts as a new successful execution.
original=RUN/'phases/001/tasks/document-closeout/evidence'
packet=next(p for p in read(original/'followup-packets.json')['packets'] if p['id']=='N01')
census=read(original/'source-census.json')
inventory=read(original/'binding-inventory.json')
documents={s['document'] for s in sections}
selected_history=[x for x in census['all_inline_spans'] if x['document'] in documents]
save('historical-reuse.json',{'original_packet':'run:phases/001/tasks/document-closeout/evidence/followup-packets.json',
    'candidate_occurrences':sum(x['candidate_occurrences'] for x in packet['required_slices'] if x['id'] in {s['id'] for s in sections}),
    'historical_all_inline':len(selected_history),'current_all_inline':sum(len(s['inline']) for s in sections),
    'count_rule':'424는원packet 후보,646은원all_inline_spans,655는현재code fence 제외 inline 전건이다. 서로 다른 모집단을 완료율로 나누지 않는다.',
    'binding_rows':[x for x in inventory['bindings'] if any(y['document'] in documents for y in x.get('documents',[]))],
    'policies':read(RUN/'phases/026/tasks/policy-semantics/evidence/policy-decisions.json'),
    'prior_policy_test_refs':read(RUN/'phases/026/tasks/policy-semantics/evidence/test-bindings.json'),
    'scope':'역사표는owner/정확원문진입점이다.027이변경한문장·시험은027의actual source와c3로대체했고026기본방침/연결의old gap을유지판정으로종결하지 않는다.'})
print(json.dumps({'sections':len(decisions),'conclusions':dict(collections.Counter(x['conclusion'] for x in decisions)),
      'inline_occurrences':sum(len(x['inline_occurrences']) for x in decisions),'test_bindings':len(bindings)},ensure_ascii=False))
