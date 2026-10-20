# 호출·관찰의 시간 규칙과 실제 정지 국면

사용자가 필요로 하는 결과는 호출·관찰이 현재 계약의 시각과 국면에 따라 판단되고, 늦게 처리한 사건이나 공개 정지가 잘못된 재시작·기한·자기점검을 만들지 않는 것이다. R47/R48(원문 6-A)의 지정 질문을 현재 생산자·소비자·기존 단언에 연결하고, 확인한 공백의 구현/시험 수리·미러·필요한 최소 확인을 한 작업에서 끝낸다. 과거에 폐기한 전체 run 기한이나 checkpoint 유예를 되살리는 배정이 아니다.

SESSION_JSON의 자기 workspace/task.json과 inputs/context.md·plan.md·seams.md부터 읽는다. C:/math 원자료와 다른 task 기록은 읽기 전용이다. 사용자 user-decisions.md·model-policy·document-batching, do-math AGENTS.md와 시험 지침을 적용한다. manager0031/review.md와 수용된 r40-r43의 계수/공급자 시간 구별을 확인한다.

## 종료할 질문

1. **R47 호출 창.** execution_window.AI_CALL_TIME_RULES와 실제 execution profile/WORK_ROLES/ROLE_TIERS에서 현재 유한 모집단을 얻는다. call_engine._prepare_call의 입력 게시 뒤 기한 생성, _call_started의 UTC 설명 게시, _call_stop_requested의 monotonic 만료·finish notice와 ModelRunner의 실제 소비를 대조한다. work 호출의 무기한과 operational 호출의 고정 프로필 기한을 구별하고 현재 설정 변화로 기존 프로필을 재해석하지 않는다. 기존 test_provider_execution_window의 전 역할·tier·경계 단언이 충분한 부분은 재사용하며 실제 owner 연결이 빠진 부분만 보완한다. 이벤트/수신/처리 시각은 각각 실제 정의에 따라 구별한다.
2. **R47 정지 국면.** B84와 sim.test_engine_queue의 입력 준비 중, 모델 resume 전, 실행 중 공개 pause를 읽고 최초 stop_observed_at/stop-request bytes·즉시 정지·추가 기동 없음이 현재 호출 경로까지 연결되는지 판단한다. 현 계약에 전체 run deadline과 checkpoint grace는 없다. 기존 정지·종료·수용 원결과·예약 정산 경계는 r14-fix/r15-r16 등의 한정 근거를 재사용하고 새 전체 정산 감사를 시작하지 않는다.
3. **R48 관찰 국면.** observations.OBSERVATION_PHASE_RULES와 ObservationTracker.set_execution_status/observe/_hold_deadlines 및 observation_transport의 실제 source received_at/received_monotonic/행 offset 생산을 대조한다. running/stopping/ended, event_driven/periodic/deadline_only, live/evaluate, 도구 timeout 있음/없음·출력 전송·무기한 도구대기·종료 뒤 밀린 사건·자기점검 응답의 현재 의미를 기존 TimingPhaseTests와 직접 owner 시험에 연결한다. 도구가 내보낸 timeout과 owner의 고정 관찰 창을 혼동하지 않는다. replay/종료 뒤 사건이 새 live 타이머를 열지 않는지, 실제 수신 시각과 뒤 처리 시각을 바꾸어도 계약에 맞는지 판단한다. helper가 이미 만든 source만 검사한 경우와 실제 transport가 source를 생산한 경우를 구별한다.

역사 current_work.observation_phase_time_integration(B81), ai_call_time_rule_integration(B82), stop_phase_time_verification(B84)의 원보고/한정 성질과 현재 코드를 대조한다. 과거 108/12/9/99 같은 수는 현행 모집단을 대신하지 않는다. 세부 requirement-state/tracking-state/prior-review-state의 R47/R48·6-A·PR19와 직접 연결된 K/P2만 기존 근거/수리/정확 미결/최종판 대기로 판정한다. 원보고의 부재·실패·판본 차이는 그대로 남긴다. 명칭이 과거와 달라졌다는 이유만으로 이미 충분한 검사를 다시 만들지 않는다.

## 소유 범위와 확인

task.json의 call_engine/execution_window/model_runner/observations/observation_transport, 지정 직접 시험·전용 helper·대응 미러만 수정한다. r37-review의 core/review, r39-report의 reporting/wait_reporting와 제품 공용 이음새 설명은 읽기 전용이다. 새 전역 타이머·상태 스키마·호환 분기·범용 감사체계는 필요성이 확인되지 않으면 추가하지 않는다. 현 계약을 고치는 범위로 한정하며, 범위 밖 실제 결함이나 계약 변경이 필요하면 입력·관측·영향·정확 파일/심볼을 보고한다. 제품 내부를 대역으로 덮거나 허용 파일에서 다른 owner의 상태를 임의 해소해 우회하지 않는다.

시각은 기존 clock 포트, CLI/Job 등은 기존 외부 경계 대역을 사용한다. 정적 분석으로 충분한 불변 성질은 실행하지 않는다. 실행이 필요한 수정 성질만 자기 workspace의 공식 run_tests.py --jobs 1에 작은 ID/직접 관련 선택으로 확인한다. 실제 유료 모델/Lean/HTTP/OS 예약·전체 일반/T3/변이/T4/T5는 실행하지 않는다. 소프트 시간 초과는 원인·실익과 함께 기록하고 정확성을 줄이거나 하드 timeout을 추가하지 않는다. 미러는 공식 생성기로 자기 workspace에서 build/check하고 캐시는 관측 bytes를 증거에 보존한 뒤 own base로 복원한다.

report.json에는 각 질문의 현재 생산/소비/단언 심볼, 유지한 기존 성질·고친 공백·남김과 이유, 실제 선택/row/exit/소스 SHA·실패/준비 오류·판본·미실행 범위를 남긴다. 매 성질마다 새 단일 end-to-end 시험을 요구하지 않는다. 형식·등록만으로 실제 동작을 인증하지 않으며 별도 판본 성공을 합쳐 단일 최종판 성공으로 쓰지 않는다. check.py report C:/math/.async/dm r47-r48 PASS로 마친다. R49 주기점검/대화임대·R50 기동판본, 전체6-A/PR19·G4~G8·L01/Windows1314는 이 배정의 완료 범위가 아니다. 공용소스/공용문서/queue/state·engine·Git index·graphify·기존 연구 운전은 수정하지 않는다.
