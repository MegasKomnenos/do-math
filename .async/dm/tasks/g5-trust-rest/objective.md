# Lean·신뢰의 남은 계약과 반환 분기 해석 마무리

사용자 목표는 실제 제품 경로의 결함이 시험을 빠져나가지 않게 하는 것이다. 수용된 g5-trust는 권위 기록에 저장 형식 밖 필드를 쓰던 결함을 고쳤고 단일 최종 부분 T3의 48개 시험을 통과했다. 전체 G5는 미완료이며, 이 task는 그 뒤 남은 formal.py·formal_engine.py의 9arc/10행을 실제 계약으로 판단하고 필요한 수리·최소 확인·관련 설명·공식 미러를 함께 마친다. 이 좌표는 과거 측정의 남김이며 새 시험 개수나 모든 생산자 재입증 quota가 아니다.

## 입력과 소유

SESSION_JSON, task.json, inputs/context.md·plan.md·seams.md, workspace의 do-math AGENTS.md와 scripts/tests/시험-지침.md를 읽는다. 추가 입력의 C:/math/.async/dm/managers/0076/review.md·verification-review.json·assignment-scope.json, tasks/g5-trust/report.json·evidence/judgment.md·remaining-scope.json·coordinate-judgment.json·final1/raw/report.json·coverage.json은 수용 근거다. 이 task의 gap-scope.json은 정확한 좌표와 시작 예정 SHA를 보존한다. 원설계는 C:/math/docs/do-math/시험-재편-2026-09-29/설계.md다. sources/storage-scope-direction-2026-10-15.md의 사용자 범위 교정을 적용한다.

실제 선행은 g5-trust 하나다. 진행 중 g5-core-rest·g5-entry-io의 배정·사본·결과는 바꾸거나 소비하지 않는다. 자기 시작판의 core_engine._register_execution, dispatch/review admission, SessionSlots, profiles와 저장 검증은 읽어야 하는 제공자다. 그 수정 권한은 없다. 필요한 제공자 결함이 확인되면 정확한 호출자·반례·최소 변경을 보고한다. 다른 작업 종료만을 기다리거나 미완성 제공자를 복사하지 않는다.

쓰기 범위는 task.json의 정확한 경로와 대응 미러다. 주대상은 formal.py·formal_engine.py이며 trust_validation.py·knowledge_records.py는 아래 구체 계약을 함께 고쳐야 할 때만 사용한다. 현재 수용된 지식 영향 처분 수리·설치 CLI 성과를 재개발하지 않는다. 공통 helper·측정 프레임워크·스키마 전체를 새로 만들거나 제품 지원 정책을 바꾸지 않는다.

## 맡은 결과

1. `formal._job_run`의 146→-105는 stopped 반환 동작을 최종 시험이 확인했지만 raw executed_branches에는 없는 좌표다. 기존 원coverage·현재 한 줄 if/return과 try/finally의 실제 제어 흐름을 먼저 읽는다. 같은 중단 시나리오를 반복하기 전에 좌표/측정 해석 문제인지 판단한다. 필요하면 작은 독립 측정 입력으로 해석을 확인하고, 코드 표기를 명확히 하는 작은 수리와 해당 직접시험을 함께 수행할 수 있다. 측정값을 수동 보충하거나 tracer 결함으로 미리 단정하지 않는다. 측정 제공자 변경이 필수면 이번 허용 범위를 넘어 임의 수정하지 않고 구체 증거를 보고한다. 실제 Job 종료·원 stdout/stderr·오류 전파는 보존한다.
2. `FormalEngineMixin._trust_control`의 transition 경로 62→63/63은 등록과 저장 경계의 environment/binding 검증이 이미 보장하는지 확인한다. 공개 등록 입력검사와 실제 toolchain 내용/현재성 확인은 유지한다. 적재된 유효 환경에서 불가능한 중복 lexical 방어라면 그 caller·보장을 근거로 줄이고, 합법적 도달이 있으면 가장 작은 입력과 정확 거절·상태 보존으로 확인한다. 유효 저장 형식을 깨뜨린 내부 객체를 정상 caller로 취급하지 않는다.
3. `_trust_activation_steps` 174→175/175, `_trust_check_steps` 245→246/246, `_formal_steps` 400→401/401~402의 등록 None을 함께 판단한다. machine 역할의 uncapped 설정만으로 None 불가능을 단정하지 않는다. `_register_execution`의 activity waiting·review admission·SessionSlots가 실제 caller에서 어떤 결과를 허용하는지 확인한다. 시험용 capped Lean profile이나 내부 등록 함수 대역을 만들어 경로를 꾸미지 않는다. 도달 가능한 거절은 정확한 실행 미생성·대기/queue/소유 의미를 단언하고, 불필요한 guard이면 실제 전제와 함께 축소한다.
4. `_trust_check_steps` 264→283과 266→283은 준비된 환경의 lexical 오류/invalid 상태를 잡는 경로다. 등록·저장·고정 transition과 실제 dispatch gate를 연결한다. 공개 invalidation 뒤 최종 정산 실패는 이미 g5-trust가 확인했으므로 같은 보장을 재시험할 필요는 없다. 현재 호출 시점에서 별도로 가능한 실패인지 또는 중복 방어인지 판단한다. 사용자의 명시 무효화와 결과 보존은 유지한다.
5. `_formal_steps` 439→440/440의 같은 K 원문·선언 변경은 공개 revise가 새 ID를 만들고 원기초 변경으로 stop하는 기존 계약과 대조한다. import의 기존 ID 반려, 실제 생산자·현재성 검사가 이 조건을 배제하면 불필요한 검사를 줄일 수 있다. 합법적 변경이 남으면 실제 그 경로를 확인한다. 내부 저장 dict를 직접 덮어 분기를 통과시키지 않는다.
6. `_formal_steps` 451→452/452·456~458의 최종 게시 오류는 stop 판정, owner 정산, `_formal_environment`, `record_formal_result` 사이의 실제 순서와 실패 의미를 판단한다. 외부 결과에 대한 필요한 증거 검증·권한/현재성·보존을 줄이지 않는다. verifier의 내부 반환에 불완전한 verified dict를 주입해 도달했다고 세지 않는다. 정적 근거가 충분하면 중복 방어만 줄이며, 실제 오류 가능성이 있다면 기존 외부 compiler/Jobs 경계와 가장 작은 직접 단언으로 확인한다.

실제 caller와 저장·입력 계약이 충분한 곳은 정적 판단으로 끝낸다. 유효한 입력을 찾는 무한 탐색이나 전가족·전필드·새 reader·옛 head의 반복 입증을 요구하지 않는다. 불필요한 장치를 제거하는 선택을 먼저 검토하고, 유지해야 할 방어를 없애기 위해 도달 숫자를 맞추지 않는다. 원설계5.5에 따른 의도적 제외가 타당하면 정확한 해당 행의 계약·사유를 남긴다. 현재 호스트/시험에서 도달하지 않았다는 사실만으로 제외하지 않는다. 새 skip, blanket no-cover, 층/분모/임계값 완화, 자식/T4 coverage의 T3 수동 합산은 허용하지 않는다.

## 필요한 확인과 제출

시험슬롯1, 기본 --jobs 1, 한 공식 명령씩이다. core-rest1·entry-io1과 합계3 이하다. 수리의 실제 불확실성을 해소하는 자기 workspace의 scripts/run_tests.py 최소 선택만 사용한다. 도달이 쟁점이면 해당 선택의 --tier T3 원coverage를 보존하되 부분선택의 gate/exit1과 실제 시험 실패를 구별한다. 충분한 원근거가 있는 동작은 재사용하고 일반/T3를 무조건 두 번 돌리지 않는다. 측정 중 소스는 고정한다. 소프트 시간 초과는 기록하며 시간만으로 중단·실패·skip을 만들지 않는다.

T3가 실제 Git root를 요구하면 g5-trust/evidence/prepare.py의 방법으로 자기 workspace의 독립 .git/실제 소스 기준commit만 준비할 수 있다. 실제 root/HEAD·준비 전후 bytes를 남기고 기존 GIT_CEILING_DIRECTORIES를 보존하며 자기 task 부모와 저장소 밖 짧은 고유 temp를 추가한다. 공용 Git·다른 task .git·가짜 HEAD·global 설정·remote/push는 사용하지 않는다. 이 HEAD는 공용판/성공 인증이 아니다.

command/cwd/관측exit·원report/stdout/stderr·선택/고유실제행/fixture·판본SHA/실행중변경을 보존한다. 원/현재 좌표별 도달·삭제·구체 제외·남김을 연결하되 그 좌표 처분을 최종 전체 gap 수로 부르지 않는다. 여러 판본의 부분 결과를 단일 전체 성공으로 합산하지 않는다. 생성 cache/index/timing/store는 원자료 보존 뒤 base bytes/부재로 복원한다.

전체 G4/T3·변이·T4/T5 전체, 유료 호출, 공용 Lean 설치/다운로드, 실제 예약·호스트설정 변경은 이번 범위 밖이다. 외부 대역의 성공을 실제 Lean/Mathlib·Windows Job 종료로 확대하지 않는다. 관련 설명과 허용 정본을 함께 고치고 공식 build_skill_mirrors.py로 미러를 생성/check한다. evidence/judgment.md와 report.json에 판단 이유·재사용한 보장·직접 확인 범위·남김을 설명한다. 실제 남김이 있으면 partial/blocked로 보고한다.

공용소스/context/plan/seams/queue/state·engine·다른 task/skill·기존 연구·graphify는 수정하지 않는다. `python C:/math/services/async-development/check.py report C:/math/.async/dm g5-trust-rest`로 제출을 확인한다. 최종 수용판 전체 G4/G5·G6~G8·G1~G3 연결·L01/실경계는 공용 계획에 남는다.
