# 목적과 완료할 결과

원래 R12·R13의 같은 교차 전이 검사 묶음을 현재 코드에서 판정하고, 확인한 시험 공백과 필요한 최소 수리를 이 task에서 끝낸다. 사용자 목표는 실제 엔진 사건 열에서 결함이 검사 밖으로 빠지지 않게 만드는 것이다. 7-A/2-D의 현행 사건 알파벳·짧은 고정씨앗·LONG 6×20·원래 회귀 순서에 대해 실제 생산/수신과 매 전이 불변식, 반려 목록 밖 예외 전파를 연결한다. 목록 존재나 과거 시험 수를 전건 충족으로 바꾸지 않는다. 같은 cross_machine/cross_contracts/helper를 공유하므로 R12와 R13을 별도 task로 나누지 않는다.

## 입력과 범위

SESSION_JSON의 workspace와 inputs/context.md·plan.md·seams.md, task.json이 현재 배정이다. 자기 workspace의 수용판을 쓴다. C:/math의 공용 소스와 다른 task 기록은 읽기 전용이다. 진행 중 r08/r09와 준비된 r14-fix의 중간 결과를 사용하거나 종료를 기다리지 않는다. 이 작업은 runtime 변경을 필요로 한다고 미리 가정하지 않는 독립 시험/의미 검토다.

원문은 C:/math/docs/do-math/시험-재편-2026-09-29/조사/결함-범주.md의 7-A(a/b/c), 2-D와 같은 폴더의 설계.md, 단계-전환표-2026-10-03.json이다. 기존 결과는 C:/math/docs/do-math/continuous-development-2026-10-13/phases/001/tasks/closure-map/evidence/{requirement-state,tracking-state,prior-review-state,evidence-catalog}.json의 7-A/2-D·R12/R13·PR16 해당 slice 및 그 정확 원보고 참조에서 읽는다. 역사 run:은 이 continuous-development 루트다. PR16의 B39/B54/B55/B60/B61 중 현재 교차 전이와 직접 연결되는 성질만 함께 판단하고 CLI·기동의 별도 R25/R26을 전체 종결하지 않는다.

수용된 r03-fix의 저장 계약은 managers/0013/review.md·source-review.json과 tasks/r03-fix/report.json에 있다. r11의 공개 run 종료 판정, r14의 F1/F2와 미결 F3는 공용 문서 및 각 report를 재사용한다. 이를 모든 사건 열의 진행성·정산 증거로 대신하지 않는다. R01이라는 옛 보드 의존 ID를 새로운 대기 장벽으로 만들지 않는다. 현재 Sim의 실제 저장/checker가 출발점이며 없어진 메모리 저장 대역을 복원하지 않는다.

task.json writes는 cross_* 전용 support, 그 직접 unit/sim/flows 시험, 대응 미러와 공식 비용 캐시다. 모든 허용 파일을 바꿀 필요는 없다. Sim·engine_control·provider/submission/scheduling 공용 helper, 모든 do_math runtime·record schema·문서는 읽기 전용이다. 범위 밖 runtime 결함을 발견하면 원 입력/순서·기대/실제·정확 심볼·필요한 쓰기 범위를 보고하고 범위 안 결과를 끝낸다. runtime을 대역으로 가리거나 현재 결함을 정상 기대값으로 고치지 않는다.

## 판정과 수리

1. 현재 ControlMachine/ResearchMachine/LiveMachine/DeadlineMachine과 cross_research_machine의 역할별 machine, flows의 required/planning/review/operational alphabets를 실제 @rule·@precondition·생산 경로·assert_machine 호출에 대응한다. 원래 공개 제어/역할별 결과/개정·은퇴/계획/운영 처분/설치 수리/실행 국면을 현행 의미로 대조한다. enum이나 메서드가 등록됐다는 사실과 실제로 그 값이 발생하고 소비됐다는 증거를 구별한다. 이미 충분한 원보고·정확 단언은 재사용하고 현재 미확인 축만 남긴다. 폐기한 run timeout과 현행 operational deadline/elapsed_work 의미를 혼동하지 않는다.
2. ContractOracle.check 및 cross_obligations의 원문 a/b/c 연결을 판단한다. 실제 store.load와 공개 상태·예약·execution·봉인 artifact, 사용자 pause/정비 fence/HOLD의 권한, 종결 흡수, 요청 이유 보존, 현재 모델·용량, 개정 교체/이력 추가, 대기 그래프/한 자리 소유권, 독립 행동 진행·정산을 해당 단언에 연결한다. 같은 제품 predicate로 기대값을 재계산하는 자기 확인이나 입력을 사후 보충하는 fixture가 있으면 목적에 맞게 좁게 고친다. RequestReasonLoss의 부가 진단이 최종 예외를 전파하는지, 역할 선택기의 ValueError 처리가 허용 반려와 불변식 실패를 구별하는지 실제 끝까지 읽는다. 넓은 except를 없애거나 늘리는 것 자체를 목표로 삼지 않는다.
3. SHORT와 LONG 설정, 각 machine의 최종 invariant, 고정 회귀(개정 중 identity review·공개 사본/요구 확장·봉인 산출·재시작 등)의 실제 사건 순서와 검사를 확인한다. 원래 길이·예제 수·검사 의미를 속도 때문에 축소하지 않는다. 현 LONG=6×20와 별도 live 4×8 설정을 서로 같은 모집단으로 세지 않는다. 새로운 범용 상태 기계나 전이 사본을 만들기 전에 기존 불필요한 fixture·준비·반복 비용을 줄일 수 있는지 판단한다. 성능 개선은 실제 병목과 같은 사건/단언 보존이 확인될 때만 한다.
4. 공백이 있으면 기존 전용 helper와 직접 시험 안에서 정상 대조·정확 반려/불변식 반례·실제 사건 도달을 함께 보완한다. 알려지지 않은 예외나 불변식 실패는 실패로 나와야 한다. 사용자가 요구하지 않은 무한 입력/동적 우회 완전성을 새 완료 조건으로 만들지 않는다. 현재 구조 검사에 남은 44개 unpinned_rejection 중 이 task가 실제 수정하는 cross_*의 발견은 같은 변경에서 다룰 수 있지만 다른 파일·검사기 자체로 확대하지 않는다. 남은 구조 묶음은 별도 계획에 있다.

## 최소 확인과 보고

정적으로 판단할 수 있는 부분은 원문·실제 코드·기존 정확 row의 대조로 끝낸다. 새 수리의 실제 동작은 공식 scripts/run_tests.py --jobs 1에서 가장 작은 직접 소비 ID로 확인한다. shared machine/oracle 변경이 LONG 소비에 영향을 주면 변경을 실제 소비하는 기존 LONG ID를 관련 확인에 포함한다. 무변경 모든 machine을 일괄 반복하거나 전체 T3를 실행하지 않는다. 실행하지 않은 알파벳/시나리오는 정적 확인 또는 미확인으로 기록한다. 소스를 고정하고 선택/실제 row·exit·판본·반례와 최종 결과를 보존하며 충분한 확인 뒤 반복하지 않는다. 기존 비용 문제는 부재한 원보고 수치를 합산하지 않고 실제 확인 범위로 보고한다.

변경이 있으면 공식 build_skill_mirrors.py --target .agents로 미러를 생성하고 완료 뒤 --check --target .agents로 확인한다. 바이트가 같으면 미러에서 시험을 반복하지 않는다. 비용 캐시 두 개는 자기 evidence에 보존하고 자기 base로 복원한다. 전체 일반/fresh T3/변이/T4/T5·실모델/Lean/설치/예약/연구 운전은 이 배정에 없다.

evidence에는 원문 항목→현재 사건/생산/소비→정확 단언/원보고/판본→유지·수리·미확인·최종 판본 대기를 다음 담당자가 판단할 수 있게 연결한다. R12/R13·7-A/2-D 및 PR16 관련 slice만 판정하고 G4~G8·R06·R14 F3·R15/R16·전체 PR/K/P2·L01·Windows1314를 종결하지 않는다. report.json은 실제 변경/확인/한계를 적고 python C:/math/services/async-development/check.py report C:/math/.async/dm r12-r13로 검사한다. 공용 문서/queue/state·다른 task·base/inputs·engine·Git index·graphify는 수정하지 않는다.
