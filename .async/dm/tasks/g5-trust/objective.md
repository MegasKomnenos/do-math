# Lean·신뢰의 미도달과 지식 영향 처리의 실제 계약 마무리

사용자 목표는 실제 제품 경로를 시험하여 결함의 누락을 막는 것이다. 전체 fresh T3의 G5는 아직 미충족이다. 이 task는 미배정 formal.py·formal_engine.py·setup_lean.py의 원43arc/68행과 g5-publish가 남긴 knowledge.py의2arc/1행을 현행 계약으로 판단하고, 필요한 구현·직접시험·관련 설명·공식 미러를 함께 마친다. 관측 좌표가 곧 제품 결함 또는 도달 가능성의 증명은 아니다. 정확한 원/현재 좌표와 시작SHA는 gap-scope.json에 있다.

## 입력·소유·선행

SESSION_JSON, task.json, inputs/context.md·plan.md·seams.md와 자기 workspace의 do-math AGENTS.md·scripts/tests/시험-지침.md를 읽는다. manager0073의 review.md·assignment-scope.json과 g5-publish/evidence/judgment.md·remaining-scope.json·submitted/raw/report.json·coverage.json, g5-full/evidence/full1/report.json·coverage.json·gap-inventory.json을 필요한 범위에서 소비한다. 경로는 C:/math/.async/dm 기준이며 원설계는 C:/math/docs/do-math/시험-재편-2026-09-29/설계.md다.

실제 선행은 원측정 g5-full과 수용한 지식 수정·남김 g5-publish다. 진행 중 g5-calls·g5-state의 정의/objective/사본/결과는 바꾸거나 소비하지 않는다. 두 task 종료를 기다릴 이유도 없다. 제품 수정은 task.json의 정확한 writes 범위만 허용한다. formal.py·formal_engine.py·setup_lean.py·knowledge.py가 주대상이며 knowledge_io.py·knowledge_records.py·trust_validation.py·record_schemas/schemas.py는 아래 실제 결함의 제공/소비·형식 정합 수리에 필요할 때만 사용한다. review_engine.py는 아래 잘못된 설명 주석의 좁은 정정용이다. 범위는 전수 수정/시험 quota가 아니다.

g5-state가 소유한 record_schemas/__init__.py·lifecycle_engine.py·repository.py·state_checks.py·tests/support/record_builders.py·flows/test_lifecycle_engine_trust.py와 g5-calls의 core_engine.py·call_engine.py·공유 engine helper·README/착수조건/초기화정비 설명은 읽기 전용이다. 기존 fixture는 그대로 소비하고 새 작은 입력이 필요하면 소유한 기존 시험/helper 또는 허용한 trust_branch_inputs.py·test_trust_branch_contracts.py에 둔다. 공통 프레임워크를 새로 만들지 않는다. 배정 밖 실제 제공자 수정이 필수면 정확한 파일·호출자·반례·필요 변경을 보고한다.

## 맡은 결과

1. `formal.discover_lean`, `_job_run`, `_project_identity`, `toolchain_identity_errors`, `verify_lean`의 발견·중단·관측 실패를 실제 caller/지원계약과 대조한다. 제품 검증 함수를 패치하지 않고 기존 외부 host/jobs/파일 경계와 실제 반환을 사용한다. 중단·실패를 검증 성공으로 바꾸지 않고 원 stdout/stderr·reason·종료/소유 의미를 유지한다.
2. `FormalEngineMixin._trust_control`, `_resume_formal_waits`, `_trust_activation_steps`, `_trust_check_steps`, `_formal_steps`, `_finish_trust_transition`의 현재 baseline·입장·정산·대기·환경/원문 변경을 판단한다. 실제 저장/봉인/현재성·권한과 결과 보존을 유지하며 불필요한 중복 방어는 먼저 제거/축소할 수 있는지 살핀다. 호출만 하는 표본 대신 정확한 결과/반려/상태를 단언한다.
3. `setup_lean.observe_identity`, `verify_environment`, `run`, `install`, `main`의 실제 설치/검사 계약과 원좌표를 판단한다. 기존 sim/test_toolchain_tools.py·test_lean_discovery.py와 toolchain 시험이 입증한 부분은 재사용한다. 임시 경로에서 표준 외부 I/O 경계를 제어한 직접 확인은 가능하지만 공용 toolchain 설치/다운로드·호스트설정 변경은 하지 않는다. 실환경이 필요한 부분은 현재 지원계약과 설계5.5의 구체 사유 또는 남김으로 기록한다. 가짜 내부 함수 출력으로 설치/검증 성공을 꾸미지 않는다.
4. `knowledge._apply_impact_effects`의 generic else(현재339→345/345행)를 실제 영향 생산자와 연결한다. `_basis_records`는 kind-definition/trust-environment도 포함하지만 두 닫힌 저장 형식은 이 else가 쓰는 input_current/use_history를 허용하지 않는다. manager는 이 불일치만 정적으로 확인했고 실제 합법적 영향 집합의 도달/게시 실패까지 확인하지 않았다. 먼저 현재 생산자·참조 방향과 권위 기록의 보존/무효화/재평가 의미를 확인한다. 도달하지 않는 불필요한 일반 분기라면 축소를 먼저 고려하고, 실제 결함이면 가장 작은 합법적 사례와 정합 수리로 마친다. 필드를 추가하는 수리를 미리 정답으로 삼거나 합성 잘못된 상태를 정상 결과로 단언하지 않는다. 스키마가 정말 필요하면 정본 trust_validation/record_schemas 및 소비자·직접시험·설명을 같은 변경에서 맞춘다. 전가족 저장 재입증은 하지 않는다.
5. `knowledge.invalidate_environment`의 원831→829/현재830→828을 처리한다. 해당 환경에 의존하지 않는 active assessment use의 유지와 해당 환경 의존 use의 중단·environment_revalidation을 기존 가장 작은 유효 입력에서 구별한다. 이미 확인한 일반 중단/재검증을 반복할 필요는 없다.
6. 작은 설명 오류를 함께 고친다. scripts/이음새-정본.md §3의 `initialization.activation_gaps`는 실제 존재하지 않는다. 정책 검증의 정본은 `initialization.activation_requirements`→`review_policy.build_review_policy`이며 lifecycle_engine._activate_initialization의 실제 소비를 확인해 정확히 연결한다. review_engine._retry_review_initialization의 `validate_lifecycle already built` 주석도 실제 검증 주체에 맞춘다. 설명 정정만을 위한 별도 시험/문서 task는 만들지 않는다.

실제 공개 형식·참조·권한·증거·현재성·원내용 보존·종료 장벽은 유지한다. 의도적 미도달 제외는 원설계5.5와 현재 caller/지원계약에 근거한 같은 행의 구체 사유가 필요하다. blanket no-cover, 새skip, 층/분모/임계값 변경, 자식/T4 도달을 T3에 수동 합치는 방식은 사용하지 않는다. 소프트 시간 초과는 기록하되 시간만으로 중단/실패/skip을 만들지 않는다.

## 필요한 만큼의 확인과 자원

sources/storage-scope-direction-2026-10-15.md와 원설계3.3/A22를 적용한다. 공통 codec/저장 검증·기존 업무 단언을 재사용하고, 이번 남은 불확실성이 무엇인지 먼저 적는다. 전가족/전생산자/전필드/새reader/옛head quota·장기감사를 만들지 않는다. 정적 판단으로 충분한 곳은 실행하지 않는다.

시험슬롯1, 기본 --jobs 1, 한 공식 명령씩이다. g5-calls1·g5-state1와 동시 시험worker 합계3 이하를 유지한다. 자기 scripts/run_tests.py의 가장 작은 관련 선택으로 확인하고 도달 판단이 필요할 때 해당 선택의 --tier T3 원coverage를 사용한다. 부분선택 전체분모 gate/exit1과 실제 시험 실패를 구별하며 같은 동작을 일반/T3로 불필요하게 반복하지 않는다. 실행 중 workspace 소스는 고정한다.

전체G4/T3·전체변이·T4/T5 전체·유료 호출·실예약·공용 Lean 설치/실환경 변경·내부 다중worker meta는 범위 밖이다. 실제 Lean/Mathlib와 기타 G7 연쇄의 최종 실증을 이번 대역 결과로 주장하지 않는다. 제품 실행 입구의 별도 자식 검사가 필요하면 범위/조건을 보고하고 원 coverage의 한계를 보존한다.

T3 도구가 실제 Git root를 요구할 때만 자기 workspace에 독립 .git/실제 소스 로컬 기준commit을 준비할 수 있다. g5-full/evidence/prepare.py를 자기 경로에 맞춰 사용하고 준비 전후 bytes·실제 root/HEAD를 남긴다. 공용 Git·다른 .git 복사·가짜HEAD·global 설정·remote/push는 사용하지 않는다. 기존 GIT_CEILING_DIRECTORIES를 보존하고 자기 task 부모/저장소 밖 짧은 고유 temp root를 추가한다. 로컬 HEAD는 공용main/성공 인증이 아니다.

command/cwd/관측exit·원report/stdout/stderr·선택/고유실제행/fixture·판본SHA/실행중변경을 보존한다. coverage를 썼으면 원/현재 좌표와 도달/제거/구체 제외/미검증을 연결한다. 여러 판본의 결과를 전체 성공으로 합산하지 않는다. 생성 index/timing/store는 원자료 보존 뒤 base bytes/부재로 복원한다.

## 제출

허용 정본과 관련 설명을 함께 수정하고 공식 build_skill_mirrors.py로 대응 미러를 생성/check한다. evidence/judgment.md와 report.json에 구체 수리·불필요 분기 제거·사유 있는 제외·미검증 남김, 재사용 근거와 실제 확인 한계를 기록한다. 배정의 실제 남김이 있으면 partial/blocked로 사실대로 보고한다. task 완료를 전체 G5 충족으로 세지 않는다.

공용소스/context/plan/seams/queue/state·engine·다른 task/스킬·기존 연구·graphify는 수정하지 않는다. python C:/math/services/async-development/check.py report C:/math/.async/dm g5-trust를 통과시킨다. g5-publish의 나머지 external_engine/integration/retention/submission5arc/2행, worker/IO 환경 남김, 최종G4~G8·G1~G3 연결은 별도 계획에 남는다.
