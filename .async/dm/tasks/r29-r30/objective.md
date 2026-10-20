# R29/R30: 소유 루프의 단위 실패와 독립 작업 진행

사용자 원문 2-B의 제어 적용·행동 준비·관찰 적용·결과 회수/편입·정비/정산 질문을 현재 owner에서 마친다. 한 요청/행동/실행의 실패를 기록하고 같은 입력을 무한 재생하지 않으면서 다른 작업을 진행할 수 있어야 한다. R29/R30이 같은 owner·Calls·실패 보존 경계를 쓰므로 현재 관계 판정, 필요한 수리와 직접 검증을 한 task에 묶는다. 새 일반 실패 프레임워크나 모든 예외를 삼키는 최상위 catch를 전제하지 않는다.

## 시작판과 입력

SESSION_JSON과 task.json, inputs/context.md·plan.md·seams.md를 읽는다. r06-finish는 공유 core/governance_engine의 null 반려 수용판을 제공하므로 선행이다. r15-r16의 실제 반환 drain/증거와 r25-r26의 공개 native 재수신 실패 회귀 수용판도 소비한다. r14-fix/r08/r12-r13-fix의 관찰·제어·공개 위임 의미를 유지한다. r22-snapshots의 중간 사본을 사용하지 않는다. manager0023은 이 task가 state에 없고 아직 시작되지 않았음을 확인한 뒤 아래 F1을 같은 수신 실패 경계에 묶었다. 실행 중 worker의 배정을 변경한 것이 아니다.

원문은 C:/math/docs/do-math/시험-재편-2026-09-29/조사/결함-범주.md의 2-B(소유 루프 다섯 단계·단위 예외와 봉인 입력 읽기/해시 실패), 같은 단계-전환표와 continuous-development-2026-10-13/phases/001/tasks/closure-map/evidence의 requirement-state/tracking-state R29/R30다. 현재 계약·사용자 결정과 과거 미성립 진단을 구별한다. PR11의 B63 및 해당 기존 개선은 원 diff→현재 소비→정확 단언/보존 원보고로 직접 관련된 부분만 판단한다. 과거 counts를 새 성공으로 합산하지 않는다.

## 완료할 결과

1. 현재 engine.run/_run_executor, scheduler._run_parallel/_abort_parallel_calls, core._apply_inbox/_observe_running, dispatch._observation_failed/_record_interrupted_calls, call/formal/execution_lifecycle의 단위 경계를 실제 호출과 연결한다. 기존 제어 반려·preparation wait·연구 실패 재시도·관찰 publication·반환 예외 시험이 각각 무엇을 보장하는지 먼저 읽는다. r11의 정상 조기 반환, r14-fix의 진행성, r15-r16의 drain은 같은 성질이 아니므로 2-B 전건 증거로 대신하지 않는다.
2. 원문 입력축을 현재 단계별로 대응한다. 포트의 실제 실패(봉인 원문 읽기/해시 불일치·반환/게시 오류)와 구현 단위 예외를 구별한다. 기존 포트와 실제 작은 손상 파일을 우선 사용한다. 원문이 요구한 단위 예외 주입은 좁은 실패 지점에 한정할 수 있지만, 검증 대상의 정상 producer/수신/저장/정산을 가짜 구현으로 대체하지 않는다. 현재 등록 목록을 하나 더 만드는 것으로 완료하지 않는다.
3. 충분한 경계는 정적으로 종료하고, 확인된 공백은 이 task에서 수리한다. 격리할 수 있는 요청/행동/실행은 정확 실패·원인·기초/원문·소유/예약을 남겨야 한다. 동일 입력 재진입에서 무한 재시도나 중복 정산이 없어야 하며 공개 run의 실제 정상 봉투와 독립 단위 진행, 필요하면 저장/restart를 확인한다. 실패를 성공으로 바꾸거나 예외 이름만 저장하고 원 단위/근거를 잃지 않는다. 기존 공개 pause·종결·unknown 종료의 held 예약을 유지한다.
4. 저장소 전체 CAS/게시 불능처럼 한 단위만 격리해 안전하게 계속할 수 없는 실패는 구체적 영향과 현재 반환 계약을 별도로 판단한다. 원문 의무의 면제로 자동 처리하지 않고, 기존 raw artifact/owner 복구·send marker를 보존한다. 정상 반환을 만들기 위해 durability/현재성/원 불변식 위반을 숨기지 않는다. R12/R13의 원 AssertionError·알려지지 않은 ValueError 검출을 예외 허용 목록으로 약화하지 않는다.
5. 입구의 특정 역사 종료/삭제 의미가 이 작업의 실제 생산 경로에서 드러나면 R08/R09 남김에 함께 연결한다. 그 질문만 위해 옛 API나 내부 del을 가짜 공개 생산자로 만들지 않는다. 확인한 가까운 정확 반려 단언/구조 발견은 같은 수리에 묶되 구조44건 전수·최종 관문을 새 의무로 추가하지 않는다.

## 수정과 독립성

### 함께 해결할 r25-r26 F1: 정상 native 응답의 재수신

`C:/math/.async/dm/tasks/r25-r26/evidence/review.md` F1과 `related-final-2/report.json`의 `ConditionalCliJourneyTests.test_normal_native_final_public_retry_reuses_the_preserved_response_without_a_new_model`을 읽는다. 외부 Git capture 게시 한 번의 OSError 뒤 정상 provider terminal/CLI exit0/confirmed·ended/원 result bytes는 남지만 공개 request/run은 모델을 다시 호출했다(2!=1). 현재 `_collect_submitted_result`가 중앙 실패로 status=failed를 만들고 `_receive_call`이 이를 저장하여 `_resume_initial_native_final`의 completed 관문을 통과하지 못한다. 이 중앙 수신 실패의 복구가 먼저 사용할 수 있는 결과다. 같은 core/call 수정·직접 확인에 묶어 해결한다.

정상 공급자 증거와 중앙 수신 실패를 보존·소비하는 현행 표현부터 판단한다. status 검사만 무조건 풀거나 failed/중단/부정확한 응답을 정상으로 올리지 않는다. `native_final.verified_native_final`의 원 응답/요청/모델/종료·현재 권한/outputs 봉인 검증과 원실행·원artifact/실패 이력·예약/소유를 유지한다. 이미 보존한 정상 해석의 재수신에는 새 해석 호출이 없어야 하고 정확1회 편입·request 재전달·restart를 확인한다. 기술 실패의 실제 새 호출 재시도 및 유효하지 않은 native 반려도 보존한다.

수용한 실패 회귀는 아직 성공 경로 끝까지 실행되지 않았다. 성공 후 독립적인 다음 단계(intent check 등)가 run에서 정상 호출될 수 있으므로 request의 재수신 완료, 같은 원해석의 호출 수, 후속 run의 역할/단계를 나누어 올바른 계약을 단언한다. 현재 총호출=1을 무조건 유지하거나 반대로 원해석 중복을 허용하지 않는다. post-request와 post-run의 저장 상태를 각각 새로 읽어 정확한 경계를 확인한다. 외부 장애 helper는 검증할 중앙 수신을 가짜로 대체하지 않는다.

추가 writes는 native_final.py와 이 회귀/초기 retry·native 직접 시험/helper 및 대응 미러다. 설치 재기록 문서나 다른 CLI 기능을 다시 감사하지 않는다. r25-r26 원보고의 partial/실패는 그대로 보존하고 새 결과에 F1의 처분을 명시한다.

task.json writes의 engine/core/governance_engine·scheduler/parallel/dispatch/call/formal/execution_lifecycle·control_transport와 지정 직접 시험/helper만 수정한다. runtime은 확인된 단위 경계 결함에 한정한다. 공통 Sim/provider/model/port 구현, review/governance/delegations/schema/저장/context, CLI/initialization/repair_execution와 corpus/parser는 읽기 전용이다. 저장 snapshot의 표현은 공개 provider 인터페이스로 소비하며 다른 task 중간 표현에 결합하지 않는다. 선택 파일을 모두 수정할 필요는 없다.

필요한 새 전용 시험/helper는 지정 scheduling_bulkheads/owner_failure_cases에만 둔다. 실패 경계의 현재 인터페이스·정확 출력/오류 의미는 report에 실제 심볼로 설명한다. 다른 쓰기 소유자가 필요한 결함은 정확 입력/소비자/파일과 영향을 보고하고 독립 결과는 마친다. 기존 입력/권한/현재성 검사나 호출 상한을 제거해 성공을 만들지 않는다.

## 최소 확인과 보고

AGENTS.md·시험-지침과 공식 run_tests.py --jobs 1을 따른다. 변경한 경계의 가장 작은 실패/정상 후속 선택만 실행한다. 앞 수용판 관련 회귀는 변경 영향이 있는 것만 확인하고 전체 LONG/전체 일반/T3/변이/T4/T5를 실행하지 않는다. 선택·실제 고유row·원실패/fixture 교정·exit·소스SHA·실행 중 변경·소프트초과를 보존한다. 최종 판본의 성공과 앞 판본의 재사용 근거를 구별한다.

정본 고정 뒤 공식 build_skill_mirrors.py --target .agents와 --check를 완료하고 변경쌍 byte 일치를 확인한다. 비용캐시는 증거 보존 후 own base로 복원한다. report.json은 다섯 단계별 충족 성질/실제 수리/구체적 미결, run 반환과 단위 실패의 관계를 설명한다. check.py report C:/math/.async/dm r29-r30 PASS로 제출한다. 새 외부 실호출·공용소스/문서/queue/state·Git index·다른 task·graphify·기존 연구 운전은 하지 않는다. 전체2-B/PR/K/P2와 G4~G8은 근거가 있는 범위만 판정한다.
