# core의 남은 시간 국면과 엔진 기동 판본

새 입력이 없어도 예정된 점검·대화 임대 만료가 현행 규칙대로 한 번 처리되고, 재시작 뒤에도 중복·누락 없이 올바른 후속으로 이어지게 한다. 같은 core owner를 쓰는 엔진 기동 판본의 정확한 남김도 이 task에서 함께 마친다. r41·r47-r48·r50·r44-fix 수용 뒤 시작하여 그 통합판을 소비한다. 관련 구현·직접 시험·현재 설명·미러를 한 작업으로 마감한다.

SESSION_JSON, task.json, inputs/context.md·plan.md·seams.md 및 do-math AGENTS.md·시험-지침.md를 읽는다. 원자료 루트는 C:/math/docs/do-math/continuous-development-2026-10-13이다. sources/user-decisions.md·requirements-index.json과 phases/001/tasks/closure-map/evidence/tracking-state.json의 R49/R50, requirement-state의 6-A/12-A 및 직접 교차하는 보존/P2를 읽는다. C:/math/docs/do-math/시험-재편-2026-09-29/조사/결함-범주.md의 6-A/12-A와 단계-전환표의 conversation_lease_time_integration(B83), scheduled_review_trigger_verification(B91), operator_population_integration(B52)을 현재 정의/소비/단언과 연결한다. B83의 실제 처리 UTC·세 소비자·두 정책/경계, B91의 동일 owner 여섯 국면/모델0·1 호출은 충분한 불변 성질을 재사용한다. B91의 재시작/tracker 소유 예약 미확인을 같은 owner 전체 인증으로 바꾸지 않는다.

선행 report/evidence를 먼저 읽는다. r47-r48은 UTC 관찰 발동에 source.received_at, 기록에 처리 시각을 보존하고 전달 전 도구 행이 응답 창을 바꾸던 계산을 수리했다. 그 관찰 수신 시각 계약을 대화 임대의 실제 처리 UTC 계약에 무조건 적용하지 않는다. r41의 역할/과제 대기 수리와 r50의 운영자/수리 보고 계약은 보존한다. r50이 엔진 기동에 남긴 실제 경로·공백·근거를 사용하고 미리 결함이나 새 기능을 가정하지 않는다.

r44-fix/report.json과 managers/0034/review.md를 추가로 읽는다. r44-fix는 정책 변경 중 같은 과제 검토의 중복 억제와 KN 관리정보에 의한 근거 무효화를 수리한다. core/lifecycle·test_call_stop_flags·이음새 설명을 공유하므로 이 선행은 충돌을 피하고 수용된 계약을 보존하기 위한 것이다. 해당 task의 실제 결과를 먼저 확인하고 수정한 관련 심볼만 재대조하며, 그 수리를 시간/기동 변경으로 되돌리거나 전체 재검증을 반복하지 않는다. 이 문단은 manager0034가 미착수 상태에서 추가한 입력이며 원래 R49/R50 목표·쓰기 범위는 유지한다.

1. 현재 시간 규칙의 실제 생산/소비 범위를 고정한다. ObservationTracker의 periodic/explicit review와 core._schedule_operational_reviews의 tracker 없는 operational_continuation.next_review, scheduler 주기 upkeep을 구별한다. 새 입력 없는 경과, 미예약/기한 전/동일/후, running/stopping/ended, tracker 소유/비소유, 같은 owner 반복 및 저장/restart에서 의미 있는 전이를 판정한다. 실제 수락된 운영 continue/예약 생산→queue/실행→소비를 이용하고 내부 next_review만 손으로 만든 표본을 실제 생산 증거로 쓰지 않는다. 재시작이 대상 실행을 stopping/ended로 복구하는 현행 규칙을 유지하며 옛 running 상태를 강제해 예약을 살리지 않는다. 발동 대상이 살아 있을 때 정확 한 번, 대상이 끝났을 때 신규 발동 없음과 원 예약의 처분을 확인한다. 기존 증거가 충분한 조합은 새 실행 없이 유지한다.
2. lifecycle_engine.conversation_lease_live/_conversation_control/_check_conversations/_lose_conversation과 실제 scheduler/공개 resume 소비를 연결한다. 두 disconnect policy, 만료 직전/동일/후, 늦게 처리한 heartbeat, generation 불일치/재연결, 새 입력 없이 경과와 restart의 필요한 축을 현재 owner에서 판정한다. 임대는 실제 처리 UTC와 엄격한 expiry>now를 사용하고 generation 권한은 별도다. 만료 뒤 기존 세대 heartbeat가 되살리지 않으며 새 세대·명시 resume/continue_authorized의 차이를 보존한다. 같은 만료의 중복 pause/stop·이력·후속이 없는지 기존 clock guard/종결 불변식과 함께 가장 작은 경로로 확인한다. 연구 역할을 실제 유료 호출할 필요는 없다.
3. r50이 인계한 엔진 기동 경로 전건의 원12-A 질문을 마친다. 현재 core._installation_manifest/_check_installation·ResearchEngine 초기화/공개 CLI와 설치본/정본 생성 결과 또는 기록 manifest의 연결에서 실제 부족한 부분만 구현·검증한다. 실행 중 설치 drift를 시작 때의 판본 관문 증거로 혼동하지 않는다. r50의 운영자 부문은 불변 근거로 재사용하고 공유 수리 보고/기동 설명은 실제 새 계약으로 갱신한다. 필요한 파일이 쓰기 범위 밖이면 정확 입력/영향/owner를 보고하며 임의 호환 계층이나 우회 정상 기대값을 만들지 않는다. 두 task 결과를 합쳐 단일 최종판 실행 성공으로 주장하지 않는다.

정본 쓰기는 task.json의 core/engine/lifecycle/scheduler·관찰/CLI 관련 직접 owner와 지정 시험/helper, 이음새-정본.md·references/CLI-실행-계약.md·README.md 및 대응 미러다. 새로운 registry·타이머·저장 schema가 목적상 필요한지 먼저 검토한다. 폐기 run 기한/checkpoint 유예를 되살리지 않고 실제 시계 포트를 사용한다. 현재 sufficient API와 단언을 재사용한다. operator_bootstrap/supervision/repair_execution은 r50 수용판을 읽기만 한다. scheduled_operator의 공유 기동 기록과 CLI 연결은 아래0035 인계를 따른다.

## manager0035의 수용 결과와 정확 기동 인계

r41의32파일·r50의26파일을 충돌 없이 통합했다. r41의 machine 입장 성공 뒤 resume, 정확 개정 원owner 정산, 과제 wait reason/basis_ref와 학술 준비 queue/live 대상 표시를 유지한다. r50/evidence/engine-startup-handoff.md·source-sha.json·review.md와 managers/0035/review.md가 실제 인계다. 선행 r44-fix가 더 바꾸는 관련 core/lifecycle 함수만 다시 대조한다.

r50은 repair_execution.installation_evidence(설치 전체 bytes와 source Git 관측), supervision.check_repair_version(수리 보고와 수리 후 관측의 대조), operator_bootstrap.startup_evidence(검증한 동결 manifest와 live target 파일별 차이)를 제공한다. source_commit은 실제 source HEAD이며 Git을 읽을 수 없으면 null/사유다. 연구 snapshot이나 설치 bytes의 clean/커밋 반영 인증이 아니다. 이 정의들을 복제하거나 구판 필드 기본값을 넣지 않는다.

현재 scheduled_operator.main은 동작 전에 operator/startup.json을 쓰고 stdout 결과에도 startup을 붙인다. cli.execute의 operator check/probe/wake/run-engine은 main을 거치지 않아 이 기록을 우회한다. 현재 엔진 _installation은 시작 당시 자신을 baseline으로 삼고 _check_installation은 시작 후 변화만 검사한다. run_tests.FOLDERS와 무관한 이 기동 모집단에서 실제 engine run·예약 bootstrap·직접 CLI 연결을 마감한다. 기록 manifest 없는 경우는 비교 불가/원천을 명시하며 독립 대조 성공으로 꾸미지 않는다. 읽기 전용 status의 지연 해시 성질과 기존 시작 후 polling/terminal 흡수를 보존한다.

중복 구현 없이 두 operator 진입점을 잇도록 미착수 배정의 writes에 scheduled_operator.py와 직접 operator 시험/helper를 추가했다. 기존 main의 기록 생산을 필요한 작은 공유 함수로 옮겨 직접 CLI가 소비할 수 있으며 선택한 인터페이스의 실제 입력·출력·실패를 설명에 남긴다. 기동 입력을 실제로 추가해야 할 때만 cli_contract.py와 test_engine_cli_contract.py를 함께 고친다. test_planning_document_context.py의 기존 construction/status 지연 해시·bounded polling 단언도 같은 범위에서 유지한다. 새 파일 권한이 새 registry/새 CLI 옵션 자체를 요구하는 것은 아니다. r50의 보고 schema·수신 대조·복구 결과/lock/예약/재시작 계약은 보존하며 같은 검증을 이유 없이 반복하지 않는다.

검증은 정적 확인으로 충분하면 거기서 끝낸다. 실행이 필요한 수정 성질만 자기 workspace의 공식 run_tests.py --jobs 1에서 작은 ID/직접 관련 선택으로 확인한다. 원보고의 selected/row/exit·소스 SHA·실행 중 변경·초기 실패/준비 오류·소프트 비용을 보존하고 별도 판본 성공을 합산하지 않는다. 외부 유료 모델/Lean/HTTP/OS 예약·전체 일반/T3/변이/T4/T5는 실행하지 않는다. 미러는 공식 생성기로 build/check하고 비용 캐시 bytes를 evidence에 보존한 뒤 own base로 복원한다.

보고는 R49의 규칙/국면과 R50 엔진 기동을 각각 충족·수리·정확 남김으로 판정하고, 실제 심볼/단언/원보고로 연결한다. 전체6-A/12-A·PR/K/P2·G4~G8·L01/Windows1314는 필요한 근거 없이 닫지 않는다. check.py report C:/math/.async/dm r49-startup PASS로 마친다. 공용소스/공용문서·queue·state/다른 task/engine/Git index/graphify/기존 연구 운전은 수정하지 않는다.
