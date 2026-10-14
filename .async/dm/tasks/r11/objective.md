# 목적과 완료할 결과

R11/2-C의 현재 공개 run 조기 반환 분기와 실제 시험을 연결하고, 빠진 입력·단언이 확인되면 같은 task에서 보완한다. 정상 결과 봉투, 종료 전제 뒤 추가 착수 없음, 정리·저장 상태를 기존 근거와 현재 코드로 판단한다. 특히 until_active가 active로 바뀌는 동안 live futures를 기다리는 분기에 실제 호출 전제가 있는지 해결한다. 전체 스케줄러·진행성·정산 재감사가 아니다.

## 입력과 수정 범위

SESSION_JSON의 workspace 및 고정 inputs/context.md·plan.md·seams.md와 task.json을 읽는다. 원문은 C:/math/docs/do-math/continuous-development-2026-10-13/sources/user-decisions.md·requirements-index.json, phases/001/tasks/closure-map/evidence/requirement-state.json의 2-C와 tracking-state.json의 R11다. evidence-catalog의 current_work.scheduling_population_integration, prior-review-state의 PR11 중 이번 반환 경로에 직접 연결되는 변경과 원보고를 읽는다. 과거 run:은 위 continuous-development 루트, repo:docs/...는 C:/math의 읽기 전용 원자료다. 원보고가 없으면 부재를 적고 과거 counts를 새 성공으로 쓰지 않는다.

현재 쓰기는 tests/sim/test_scheduling_close_exits.py, tests/flows/test_scheduling_close_remaining_exits.py·test_scheduling_close_repair_exit.py, tests/support/scheduling_exit_contracts.py 및 각 미러다. 공통 표와 이 표의 직접 소비 수리를 한 담당자가 맡는다. engine.py·scheduler.py·dispatch_engine.py·lifecycle_engine.py와 실제 Calls 구현 및 다른 시험/support는 읽기 전용이다. 실제 runtime 결함이면 정확 전제·반례·영향·필요한 파일을 보고하고 범위 안 결과를 마친다. 필요한 호출을 만들기 위해 실제 제품 owner를 대역으로 바꾸거나 runtime을 임의 수정하지 않는다.

r04·r05와 의미 있는 쓰기가 겹치지 않고 선행 결과도 요구하지 않는다. 시작 사본만 사용하고 다른 진행 task의 중간 파일을 소비하지 않는다.

## 종료할 질문

1. ResearchEngine.run/_run_executor에서 _prepare_executor_pass, SchedulerMixin._run_parallel의 break/continue/최종 반환, DispatchEngineMixin의 _owner_stopping·_idle_wait_status·_settled_run_status까지 현재 분기를 확인한다. fence, pause/closed/completed, 설치 수리·미종료 recovery, initializing, idle/capacity, until_active, clock guard, watch, 양수 max_steps draining의 현행 전제를 tests/support/scheduling_exit_contracts.py:EXIT_CASES와 실제 정확 시험 ID·단언에 연결한다. 옛 줄 번호나 수동 표 존재만으로 모든 분기가 실행됐다고 주장하지 않는다.
2. 시작 전 종료는 신규 execution/예약이 없고 기존 기록이 보존되며, 공개 run이 정상 봉투를 반환하는지 본다. 이미 실행된 작업을 회수하는 draining/watch/중도 정지와 구별한다. max_steps 동안 허용된 선행 실행까지 0으로 강제하지 않고, 종료 전제 뒤 새 착수 없음과 남은 완료 적용·정리를 본다. 원문 의미를 축소하지 않으면서 실제 분기의 시간 순서를 명시한다. _calls=None·_executor_running=False와 필요한 durable reload 단언도 유지한다.
3. until_active and lifecycle.state=='active'에서 futures가 남은 분기의 도달 전제를 현재 공개 호출자·활성화 전이·scheduler 순서로 판단한다. 도달하면 실제 공개 run과 기존 시계/Calls/model 포트 fixture로 최소 사건열을 구성해 기다림·완료 적용·추가 착수 없음·반환을 확인한다. 도달하지 못하면 호출자/생산 전제에 따른 근거를 남기고 사후에 상태를 억지로 조립한 경로를 실사용 근거로 세지 않는다. 기존 already-active/no-future 시험만으로 live-future 질문이 해결됐다고 보고하지 않는다.
4. 기존 반환/정산 시험이 이미 해당 분기를 입증하면 재사용한다. 필요한 시험/표만 수정하며 새로운 전역 AST 프레임워크나 병렬 등록부를 만들지 않는다. PR11·관련 K/P2의 해당 성질만 처분하고 R14~R16 전체 진행성/정산 질문과 G4~G8은 별도로 남긴다.

## 최소 확인과 제출

먼저 정적으로 판단하고 기존 증거가 충분하면 실행하지 않는다. 보완한 동작에는 최소 공식 ID/관련 모듈만 사용한다. 도구는 자기 workspace의 scripts/run_tests.py, jobs1이다. 현재 Sim의 검증된 저장과 외부 포트 대역을 재사용하고 시간 경과를 성공/변이 포착의 대리 기준으로 쓰지 않는다. 준비 실패는 제품 결함 재현과 구별한다. 새 실제 모델·Job·Lean·설치·예약과 전체 일반/T3/변이/T4/T5는 배정하지 않는다.

실행 중 소스를 고정하고 선택·실제 row·exit·해시·한계를 보존한다. 변경 정본은 공식 build_skill_mirrors.py --target .agents로 생성하고 --check --target .agents 및 대응 바이트를 확인한다. 비용 캐시 두 개는 evidence 보존 후 자기 base로 복원한다. 같은 미러 시험을 불필요하게 반복하지 않는다.

evidence에는 현재 분기·전제·시험·단언·기존 원보고·판정과 until_active의 결론을 남긴다. 공용소스·engine 서비스·공용 문서/queue/state·다른 task·원자료·Git index는 수정하지 않고 graphify를 갱신하지 않는다. async report.json에는 실제 변경 전부와 확인 범위·한계를 적으며 python C:/math/services/async-development/check.py report C:/math/.async/dm r11의 PASS를 확인한다. L01·Windows1314 symlink 미검사 및 다른 의미 미결은 유지한다.
