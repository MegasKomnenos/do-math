# worker·제어 수송·CLI의 실제 미도달 수리와 직접 확인

사용자 목표는 실제 제품 경로의 결과를 확인하는 시험으로 결함의 누락을 막는 것이다. g5-full의 fresh T3는 4287passed/Windows1314 조건부skip1이지만 55모듈517arc/653행 미도달로 G5가 미충족이다. 이 task는 gap-scope.json의 12모듈29arc/74행만 현행 계약에 따라 판정하고, 관련 제품/시험 수리·최소 확인·관련 설명·공식 미러를 함께 마친다. 좌표는 관측된 공백이며 도달 가능성이나 제품 결함의 사전 판정이 아니다.

## 입력과 소유

SESSION_JSON, task.json, inputs/context.md·plan.md·seams.md, 자기 workspace의 do-math AGENTS.md와 scripts/tests/시험-지침.md를 먼저 읽는다. 공용 소스와 다른 task 기록은 읽기 전용이다. managers/0069/review.md·assignment-scope.json, managers/0068/review.md·verification-review.json, g5-full의 report.json·evidence/judgment.md·full1/report.json·coverage.json·gap-inventory.json을 필요한 부분만 읽는다. 원 선택 색인은 g5-full/evidence/observed-caches/.claude/skills/do-math/scripts/tests/.selection-index.json에 보존돼 있다. workspace의 복원된 cache를 원측정으로 사용하지 않는다.

실제 선행은 g5-full의 미도달 측정이다. g5-core와 g5-inputs의 정의·사본·진행 중 결과를 바꾸거나 소비하지 않는다. 자기 시작판은 manager가 수용한 g5-io 변경도 포함한다. 이 12개 제품 파일은 원측정 SHA와 현재 공용판이 같다. 직접시험/helper/CLI 설명과 대응 미러의 정확한 허용 범위는 task.json이다. g5-core 소유 tests/unit/test_engine_control_transport.py·sim/test_engine_control_server_wire.py·support/engine_control.py 등은 읽기 전용이다. 같은 제공자를 시험할 필요는 새로 허용한 tests/unit/test_worker_control_branches.py 또는 적합한 자기 소유 기존 시험에서 처리한다. 공유 helper 수리가 필수라면 파일·호출부·원반례를 남긴다. 범위 상한은 전수 수정/실행 quota가 아니다.

## 맡은 결과

claude_worker/codex_worker/control_server의 실제 script 입구와 import 경로, codex_adapter/local_host의 현재 provider 조립, provider_final의 정확 반려, control_transport의 파일 경쟁·영수증/게시 계약, cli의 입력 파일·공개 제어·실패 반환, reporting의 시간대 fallback, scheduled_operator/operator_bootstrap/probe_cli의 현재 설치·기동·상태 반환을 원좌표와 실제 caller로 판단한다. 대상 파일 목록과 함수별 원문은 gap-scope.json에 있다.

먼저 불필요한 중복 방어·죽은 계약을 제거/축소할 수 있는지 확인한다. 실제 입력의 형식·참조·권한·현재성·원내용 보존·종료 장벽은 유지한다. 유효한 입력으로 도달 가능한 공백은 가장 싼 기존 시험에 정확 결과/반려/상태/bytes 단언을 더하며 관련 결함을 같은 task에서 고친다. 내부 제품 함수를 패치하거나 호출만 하고 끝내는 시험, 원문 없이 통과시키는 예외 포착, 구판 fixture를 살리는 fallback은 해결책이 아니다. 포트/OS 경계의 대역과 실제 제품 판단을 구별한다.

직접 script/__main__/import fallback과 subprocess 미도달은 실제 입구·측정 소유를 확인해 판정한다. 별도 child 또는 T4 실행을 T3 도달로 수동 합치지 않는다. 원설계5.5의 의도적 미도달 제외에는 해당 행의 구체적 사유·현재 계약·기존 구조검사 근거가 필요하다. 불필요한 코드의 제거를 우선 검토하며 blanket no-cover, 새skip, 층/분모/임계값 완화는 허용하지 않는다. 현 환경에서 해결할 수 없는 조건은 정확한 좌표·이유로 남긴다.

sources/storage-scope-direction-2026-10-15.md와 원설계3.3/A22·5.5를 적용한다. 공통 codec/저장검증·기존 업무 단언을 재사용하고 실제 공백만 보완한다. 전가족·전생산자·전필드·새reader·옛head 일괄 재입증, 새 framework·장기감사를 추가하지 않는다.

## 최소 확인과 자원

시험슬롯1개, 기본 --jobs 1, 한 공식명령씩이다. 다른 두 task와 전체시험worker3 이하를 유지한다. 자기 scripts/run_tests.py의 가장 작은 관련 선택으로 필요한 불확실성만 확인한다. 필요하면 그 선택의 --tier T3 원coverage로 해당 좌표의 도달을 확인하되 다른 모듈 gap/exit1을 실제 시험 실패와 구별한다. 같은 동작을 일반/T3로 불필요하게 반복하지 않으며 정적 판단으로 충분하면 실행하지 않는다. 소프트 시간 초과는 기록하며 경과 시간만으로 중단/skip/실패/변이포착으로 세지 않는다. 실행 중 소스를 고정한다.

전체G4/T3·전체변이·T4/T5·유료호출·실예약·설치/호스트권한 변경·내부 다중worker meta는 배정 밖이다. 자기 범위의 최소 공식 선택만 수행한다. 모든 동료 종료를 기다리는 barrier는 없다.

T3 도구가 실제 Git root를 필요로 할 때만 자기 workspace에 독립 .git/실제 소스의 로컬 기준commit을 준비할 수 있다. g5-full/evidence/prepare.py를 자기 경로에 맞춰 준비 전후 bytes와 실제 root/HEAD를 남긴다. 공용 Git·다른.git 복사·가짜HEAD·global설정·remote/push는 사용하지 않는다. 기존 GIT_CEILING_DIRECTORIES를 보존하고 자기 task 부모/저장소밖 짧은 고유 temp root를 추가한다. 로컬 HEAD는 공용main/성공 인증이 아니다.

command/cwd/관측exit·원report/stdout/stderr·선택/고유실제행/fixture·판본SHA/실행중변경을 보존한다. 필요한 coverage는 원/현재 좌표·도달/남김으로 연결하고 여러 판본의 결과를 전체 성공으로 합산하지 않는다. 생성 index/timing/store는 원자료 보존 후 base의 bytes/부재로 복원한다.

## 제출

evidence/judgment.md와 report.json에 구체적 수리/불필요 분기 제거/정당한 제외/미검증 남김, 재사용한 근거와 확인 한계를 적는다. 원좌표는 같은 원인의 묶음별로 판정할 수 있다. 배정의 실제 남김이 있으면 partial/blocked로 보고하며 이 task 성공을 전체 G5 충족으로 쓰지 않는다.

허용 범위의 정본과 관련 설명을 함께 수정하고 공식 build_skill_mirrors.py로 대응 미러를 생성/check한다. 공용 설명에 필요한 계약은 정확한 파일·심볼로 report에 남긴다. 제품 변경은 자기 workspace만 수정한다. 공용 context/plan/seams/queue/state·engine·다른 task/스킬·기존 연구·graphify는 수정하지 않는다. python C:/math/services/async-development/check.py report C:/math/.async/dm g5-worker를 통과시킨다. 최종 통합판G4/G5·G6~G8·실경계/환경 조건은 별도다.
