# 같은 과제의 중복 검토와 관리 정보에 의한 근거 무효화 수리

사용자가 의미가 같은 근거를 계속 사용할 수 있고 실제 근거가 달라졌을 때는 올바르게 재판정되도록 한다. 수용된 r44-r46 조사에서 남긴 F1/F2를 기존 readiness/knowledge/core owner에서 구현·직접검증·필요 설명·미러까지 한 작업으로 끝낸다. r44-r46·r41 수용 뒤 시작한다. 조사 완료를 5-A 수리 완료로 오인하지 않는다.

SESSION_JSON/task.json, inputs/context.md·plan.md·seams.md 및 do-math AGENTS.md·시험-지침.md를 읽는다. 원자료는 C:/math/docs/do-math/continuous-development-2026-10-13의 sources/user-decisions.md·requirements-index.json, phases/001/tasks/closure-map/evidence/tracking-state.json의 R44/R45/R46와 requirement-state의 5-A, C:/math/docs/do-math/시험-재편-2026-09-29/조사/결함-범주.md의 5-A다. 단계-전환표 B74~B77의 충분한 성질은 기존 조사 근거를 재사용한다.

직접 인계는 C:/math/.async/dm/tasks/r44-r46/report.json 및 evidence/followup-packets.json·judgment-matrix.json·conclusion.md·source-editions.json·test-assertions.json·pure-probe-results.json, managers/0034/review.md·source-review.json이다. 선행 r41/report.json과 실제 수용판을 읽고 조사 당시 SHA/함수 중 r41이 바꾼 관련 owner만 다시 대조한다. 진행 중 다른 작업 사본을 읽거나 배정을 바꾸지 않는다. r50은 독립 운영자 작업이므로 이 task의 선행이 아니다.

## F1: 같은 과제 판본의 미종결 검토 억제

현재 lifecycle_engine.LifecycleEngineMixin._refresh_readiness의 required는 revision/contract_sha256뿐 아니라 goal_revision/policy_revision을 포함한다. live_review가 전체 equality를 요구하므로 정책만 바뀌어도 동일 과제 계약의 running/stopping 검토를 놓치고 다른 review_basis_key를 enqueue할 수 있다. core._enqueue는 미착수 queue를 병합하므로 live 억제를 대신하지 않는다. 이는 정적 확인한 제품 결함이며 조사에서 새 엔진 실행으로 재현한 것은 아니다.

동일 과제 계약의 진행 중 검토를 외부 정책/근거 변화만으로 중복 개설하지 않게 수리한다. 결과의 수락 현재성과 ended 뒤 후속은 최신 전체 정책/근거를 계속 사용해야 한다. 실제 계약 revision/hash가 달라진 경우의 별도 판본 의미, 다른 target의 개설, 원 execution/action/봉인과 기존 대기 책임을 보존한다. 모든 대상·판본을 전역으로 막는 규칙을 추가하지 않는다.

기존 sim.test_lifecycle_engine_controls.ReadinessTests.test_live_review_suppresses_reopening_until_return_after_external_premise_change를 실제 정책 결정 분기로 보완한다. 실제 _register_execution과 유효 user policy_change 생산/소비 경로를 사용하고, 과제 revision/contract가 그대로라는 전제·정책/key 변화·running 및 stopping 각각의 추가요청0·ended 뒤 최신key 정확1개·반복 refresh 불변·다른target 및 원action 보존을 필요한 최소 입력으로 확인한다. 기존 시험은 profile 변경의 running과 ended만 직접 단언하며 stopping으로 전이한 직후 바로 ended로 전이하므로 stopping 사이 refresh 근거는 없다. 이 한계를 실제 단언으로 메운다. 이미 충분한 다른 입력축을 다시 큰 여정으로 만들지 않는다.

## F2: 의미 근거와 관리 정보의 구별

knowledge._hash/capture_basis/validate_basis와 core._goal_basis_key가 KN 전체를 해시한다. 조사 순수 입력은 review_cycle_id 또는 관리 history만 추가해 hash_changed와 decision_basis_changes=[]를 관측했다. 이 입력은 저장 schema를 통과한 전체 상태가 아니므로 후속 검증은 기존 유효 producer/저장 harness에서 시작한다.

기존 knowledge 근거 owner에 무엇이 의미 근거인지 선언하고 필요한 capture/validate와 goal key가 같은 정의를 소비하게 한다. review scheduling ID와 관리 이력만 바뀐 경우 수학 근거/현재 사용 효력이 같으면 근거를 유지한다. 실제 수학 내용·판본·참조/출처·효력/사용 중단·신뢰·명시 검증·필요한 기록 모집단의 변화는 계속 감지한다. 다른 가족의 상태/수락이 관리 정보인지 효력인지 실제 소비 의미로 판정하며 무조건 제외하지 않는다. 좁은 인용용 decision_reference의 무수정 재사용을 확정하지 않는다. frozen artifact/원문 bytes·전송/상태 무결성용 exact hash까지 일괄 약화하지 않는다. 구현 선택은 현재 owner에 맞게 작게 유지하고 호환 계층·새 registry를 만들지 않는다.

실제 소비는 governance_engine._apply_governance_goal_audit→record_basis→knowledge_engine._invalidate_goal_currentness, knowledge_io.import_candidate→relation_endpoint_basis→knowledge_records.record_premises_current, core._goal_basis_key→goal stop/수락/slot, core._apply_extensions의 research_insights다. review_engine._start_identity_review는 실제 KN.review_cycle_id 생산자다. 필요한 의미를 이 기존 연결에서 확인하고 호출부 계약을 보존한다.

최소 검증은 기존 unit.test_knowledge_close_currentness.CurrentnessGuards·unit.test_knowledge_io_contracts의 relation endpoint, sim.test_governance_goal_audit.GoalConsumerTests·sim.test_call_stop_flags.GoalAuditStopTests의 직접 소비를 우선 쓴다. 관리 변화 안정성과 실제 내용/효력 변화 반려를 독립 기대값으로 대조하고 goal의 불필요한 stop/무효화 부재와 유효 변화의 stop/재판정 보존, 관계 endpoint 현재성을 확인한다. 기존 저장 fixture가 이미 소유한 곳에서 저장/reload를 함께 본다. 단순히 바뀐 capture 함수를 양쪽 기대/관측에 재호출한 equality만으로 의미 수리를 증명하지 않는다. research_insights 등 불변 소비는 코드로 충분하면 추가 실행하지 않는다. 전체 엔진/대형 설치·전체 해시 감사를 새 완료 조건으로 만들지 않는다.

## 범위·인계

제품 쓰기는 task.json의 knowledge.py·knowledge_records.py·core_engine.py·lifecycle_engine.py와 지정 직접시험/필요 helper·이음새-정본.md·대응 미러다. knowledge_records는 기존 정본의 공유/소비 조정이 필요할 때만 바꾼다. r41의 역할 판정·과제 대기 수리를 보존한다. operator_bootstrap/supervision/scheduled_operator/repair_execution과 시간·기동 기능은 읽기 전용이며 r50/r49-startup이 소유한다. 필요한 수정이 범위 밖이면 정확 경로·입력·영향을 남긴다.

정적 확인으로 충분한 성질은 거기서 끝낸다. 변경 성질의 실행은 자기 workspace 공식 run_tests.py의 가장 작은 직접 선택을 --jobs 1로 수행한다. selected/실제row/exit·소스SHA·초기 실패/준비 오류·실행중변경/소프트 비용을 보존한다. 다른 판본의 passed를 단일 성공으로 합산하지 않는다. 미러는 공식 생성기로 자기 workspace에서 build/check하고 비용 캐시는 evidence에 원바이트를 보존한 뒤 own base로 복원한다. 실모델/Lean/HTTP/OS예약·전체 일반/T3/변이/T4/T5는 실행하지 않는다.

report에는 F1/F2의 현재 결과와 근거 필드·producer/consumer·실제 확인·미확인 범위를 기록한다. B74~B77 및 r31-fix 등의 충분한 성질을 재검증 없이 유지하고, 이번 수리로 5-A의 남김이 해소됐는지 구체적으로 판정한다. 다른 원요구/보존/P2·G4~G8·L01/Windows1314는 별도다. r49-startup이 이어받을 core/lifecycle·goal stop 시험/설명의 실제 변경 심볼과 계약을 인계한다. check.py report C:/math/.async/dm r44-fix PASS로 마친다. 공용 소스/공용 문서/queue/state·다른 task/engine/Git index·graphify·기존 연구 운전은 수정하지 않는다.
