# 목적과 완료할 결과

R15/R16의 반환 시 정산 질문을 같은 반환 시험·관측 helper에서 끝낸다. 원문 8-B의 `run` 반환 경로(단계 상한, idle, fence, 정지, until-active) × 실행 종류(AI, 형식 검사, 신뢰 검사, 외부 작업) × 시점(시작 전, 실행 중, 완료 회수 직후)을 현재 실제 producer/owner/저장 경계에 대응한다. 기존 성질을 재사용하고, 빠진 입력·정확 단언과 직접 확인한 결함만 수리·미러·최소 확인까지 한 task에서 마친다. 표나 문자열 등록만으로 모집단을 충족 처리하지 않는다.

## 입력과 실제 선행

SESSION_JSON의 workspace, inputs/context.md·plan.md·seams.md와 task.json을 읽는다. 공용소스/다른 task는 읽기 전용이다. `C:/math/docs/do-math/continuous-development-2026-10-13` 아래 sources/user-decisions.md·requirements-index.json과 phases/001/tasks/closure-map/evidence의 requirement-state.json 8-B, tracking-state.json R15/R16, prior-review-state.json PR11의 B33/B34/B50 해당 slice, evidence-catalog.json을 필요한 항목만 읽는다. 원문은 `C:/math/docs/do-math/시험-재편-2026-09-29/조사/결함-범주.md` 8-A/8-B 및 단계-전환표-2026-10-03.json의 return_settlement_integration/scheduling_population_integration/outcome_contract_integration에 연결돼 있다. 과거 `run:`은 위 continuous-development 루트이고 현재 제품 경로는 자기 workspace다. 과거 Git hunk는 `git -C C:/math show`로 읽는다.

이미 수용된 r11(공개 반환 전제·until_active/live future)과 r14/r14-fix(진행성·관찰 양보)를 먼저 소비한다. managers/0008·0012·0019의 review.md·source-review.json, tasks/r11·r14·r14-fix의 report.json과 필요한 원보고를 재사용한다. r11의 초기 fixture 오류·마지막2passed 및 r14-fix의20passed/16passed는 각각 다른 판본이다. 기존 성공을 전체 통합판 결과로 더하지 않는다. 선행은 r11/r14-fix뿐이며 위임·null·저장크기의 미완성 결과를 기다리거나 가져오지 않는다.

## 종료할 유한 질문

1. `ResearchEngine.run/_run_executor`와 `SchedulerMixin._run_parallel`, 실제 `MACHINE_ROLES`/dispatch, `call_engine`, `formal_engine`, `external_engine`에서 반환 위치와 적용 전제를 읽는다. 기존 `scheduling_return_matrix.scene/assert_returned`, `scheduling_exit_contracts.EXIT_CASES/STOP_PHASES`, `OwnerProbe/assert_settled`와 직접 시험이 어느 좌표를 실제 도달·반환 시점에 검사하는지 대응한다. 현재 trust_check/trust_activate의 분담을 원문 신뢰 종류에 연결하고, 단순 tuple 존재를 실행으로 세지 않는다. 같은 생산/수신 경계와 근거가 충분한 좌표는 묶어 정적으로 종료한다. 전 조합별 새 시험이나 새로운 제품 registry를 만들지 않는다.
2. idle/fence/until-active의 live-future 조합은 실제 호출/전제로 판정한다. r11의 공개 pause→제한 복구→resume으로 active와 미완료 future가 공존하는 경로는 재사용하고, until-active를 항상 무착수로 단정하지 않는다. 도달 불가능 처분은 현재 caller/guard와 의미로 설명한다. 내부 status 주입이나 옛 API 복원으로 존재하지 않는 경로를 만들지 않는다. 필요한 공개 경로의 실제 입력과 정상 대조만 보완한다.
3. 반환 시점의 미적용 완료0, 미종료 실행의 실제 owner 연결, 정상 종료 기계의 ended/confirmed/예약 반환, 실제 결과·원 artifact의 저장/재시작과 정확1회 적용을 검사한다. `owner_activity_id`의 단순 truthiness나 파일 비어 있지 않음만으로 충분한지 각 계약에 비추어 판단한다. r14-fix의 collect는 새 완료/owner 진입 밖 관찰을 다음 바퀴로 남길 수 있다. 중간 collect의 부채와 공개 run 반환 시 미적용 완료를 구별하며, 새 동작 때문에 필요 없는 중간 제약은 제거할 수 있지만 최종 정산/정확1회/순서 성질을 약화하지 않는다.
4. KD-1000/1001과 현재 시험의 종료 unknown, 첫 계산 전 pause·취소, 게시 실패/증거 보존을 정상 confirmed와 구별한다. unknown을 ended/confirmed로 꾸미거나 held 예약을 먼저 반환하지 않는다. 실제 반환값·소유/예약 기록·확인 증거의 의미를 보존한다. 동기 HTTP의 send 전/중/후 효과 확인·재조정 책임과 ModelCalls future 반환을 같은 경계로 합치지 않는다. 현재 HTTP/Job/CLI/Lean/clock 외부 대역은 재사용하며 제품 receiver/collector/owner/store를 대역으로 치환하지 않는다.
5. PR11 B33/B34/B50 중 이 반환/정산 경계의 실제 hunk→현재 소비자→원보고 해당 ID/판본만 함께 판단한다. r11/r14-fix에서 충분한 slice는 반복하지 않는다. 없는 Temp 보고의 과거 수치를 성공으로 세지 않고 필요한 성질을 현재 단언/최소 실행으로 연결한다. B63의 별도 산출 복구·R29/R30·전체 PR11/전체 G의 감사를 이 작업에 더하지 않는다. 수정하는 가까운 unpinned_rejection 발견은 함께 처리하되 구조44건 전체는 별도 묶음으로 남긴다.

## 수정 범위와 협업 경계

task.json writes가 권한 정본이다. 반환 matrix/settlement/external phases/evidence/publication/remaining exits의 직접 시험과 scheduling_return_*·scheduling_exit_contracts helper를 같은 작업이 소유한다. 새 helper는 기존 것으로 표현할 수 없을 때만 배정된 scheduling_settlement_cases.py에 둔다. 실제 재현한 반환 결함에 한해 scheduler/parallel/call_engine/formal_engine/dispatch_engine/execution_lifecycle/repair_execution을 수리할 수 있다. 진행성의4행 조각·read 경계·owner allowance·제어 우선순위·관찰 뒤 자기 결과 수신을 보존한다. helper 변경의 기존 progress/반환 직접 소비 확인도 쓰기 범위 안에서 최소로 묶는다.

진행 중 r06-domain/edges, r22-storage와 준비된 r12-r13-fix의 쓰기는 변경하지 않는다. core_engine·governance/delegations/review_engine·schema, external/external_engine/session_slots/model_call, repository/payloads/knowledge_records, 공용 Sim·lifecycle/모델/Job fixture는 읽기 전용이다. 직접 경계 관찰에 기존 ports/ObservedCalls/AfterReturn을 사용한다. 이 읽기 전용 파일에서 실제 결함을 확인하면 유효한 자기 결과를 마무리하고 정확 공개 입력·영향·필요한 심볼/쓰기와 남김을 보고한다. 가상 우회로 성공을 만들거나 다른 task에 중간 수리를 지시하지 않는다. 현재 선언된 원문 범위를 축소했다고 해석하지 않는다.

## 최소 확인과 보고

정적 비교로 충분한 성질은 재실행하지 않는다. 실행이 필요한 새/수정 동작만 자기 workspace의 scripts/run_tests.py/jobs1로 확인하고, 실패의 원인을 고친 뒤 영향 ID만 다시 실행한다. 전체 일반/T3/변이/T4/T5·실외부 HTTP/모델/Lean/Job/설치/예약은 이 배정이 아니다. 시간은 소프트 기준이며 성공 상한을 입력량에 비례해 늘리거나 시간 경과만으로 실패/통과를 정하지 않는다.

원문 좌표별 현재 판정은 자기 evidence에 간결하게 남긴다. 기존 충분한 성질·수리·도달 불가능의 실제 이유·정확 미결·최종판 대기를 구별한다. 새 대형 관리표나 모든 코드 재감사를 만들지 않는다. 실행은 선택/실제 row/exit/소스 SHA·최초 실패·fixture 오류·한계를 보존한다. 공식 build_skill_mirrors.py --target .agents 및 --check --target .agents를 사용하고 변경 대응 byte를 확인한다. 비용 캐시2개는 자기 evidence에 보존 후 base로 복원한다. report.json에 실제 결과·이유·확인 범위·남김을 적고 `python C:/math/services/async-development/check.py report C:/math/.async/dm r15-r16`을 통과시킨다. 공용 문서/queue/state·engine·원자료·다른 task·Git index를 수정하지 않고 graphify를 갱신하지 않는다.
