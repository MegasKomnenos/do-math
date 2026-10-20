# 수명 상태·시각·재개 메타데이터 8가족의 실제 저장 계약을 마친다

사용자 목표는 실제 생산값과 저장 수신 계약의 어긋남이 시험을 빠져나가지 않게 만드는 것이다. research 메타데이터의 수용 결과를 이어 runtime의 같은 scalar 저장 경계를 한 묶음으로 판정하고 필요한 구현·직접시험 보완·최소 확인까지 마친다. 필드마다 작은 task나 새 registry를 만들지 않는다.

SESSION_JSON, task.json, inputs/context.md·plan.md·seams.md와 do-math AGENTS.md·시험-지침.md를 읽는다. 원자료는 C:/math/docs/do-math/continuous-development-2026-10-13/sources의 user-decisions.md·requirements-index.json·model-policy-2026-10-14.md·document-batching-2026-10-14.md, phases/001/tasks/closure-map/evidence/requirement-state.json의 R01/1-A·1-B/K-78과 C:/math/docs/do-math/시험-재편-2026-09-29/설계.md 3.3/A20이다. C:/math/.async/dm/tasks/keep-storage/evidence/families.json의 root/family를 유지하고 storage-metadata의 수용 보고·근거와 managers/0050/review.md를 읽는다. 원자료와 공용 소스는 읽기 전용이다.

## 대상과 독립성

대상은 runtime.status, cycles, updated_at, recovery_checked, last_observed_utc, resume_lifecycle, stop_requested, next_research_reconsider_at의 정확한 8가족이다. 현재 모두 metadata 값이며 status는 enum, cycles는 NAT, recovery_checked는 BOOL, stop_requested는 boolean/string, next_research_reconsider_at는 nullable TEXT, 나머지는 TEXT다. availability/clock_guard/user_pause의 객체 내용, event_cursor/events/pending_events, research.lifecycle 전체 필드 역방향과 다른 가족은 이 판정으로 닫지 않는다.

storage-metadata만 선행이다. 수용된 실제 initialize_state→검증 저장→새 contract의 reader와 scalar 검사 방법을 소비한다. keep-storage는 그 선행에 포함된다. 실행 중 execution-fields와 대기 storage-academic의 제공자·중앙schema 수리를 기다리거나 미수용 workspace를 읽지 않는다. 현재 scalar 정의에서 별도의 schema 수리가 필요하다는 사실은 확인되지 않았다. core_engine/call_engine/session_slots/governance/academic/중앙record_schemas와 공통 storage_records·pairs는 읽기 전용이다. 그 경계에 실제 결함이 있으면 정확한 입력·오류·필요 파일을 보고하고 독립 범위를 마친다. 가상의 결함이나 단순 파일 읽기를 의존성으로 만들지 않는다.

## 판단하고 보완할 의미

1. 실제 root 쓰기와 동명 nested execution/task/status 쓰기를 구별한다. initialize_state, LifecycleEngineMixin._activate_initialization/_pause_lifecycle/_resume_lifecycle/_lifecycle_event/_clock_guard/_refresh_readiness, ResearchEngine._save/_apply, planning.schedule_reconsideration/collect_due_events의 현재 쓰기·소비를 확인한다. 원표 references는 검색 후보이며 실제 root 생산 인증이 아니다. 정확한 심볼·SHA·시험 ID를 최종 fresh T3 연결 입력으로 남긴다.
2. 수용된 r39-r42/r39-report, r47-r48, r49-startup과 기존 lifecycle public/controls/gates, storage publication 시험의 충분한 성질을 원보고·현재 소스와 대조해 재사용한다. 이미 확인한 긴 승인/권한·기동·운전 전체를 다시 실행하지 않는다. 같은 성질을 새 helper에서 반복하기보다 기존 단언에 빠진 저장값/반려 의미만 보완한다. static+유효한 원근거로 충분한 항목은 실행 없이 판정한다.
3. 초기 status/cycles/recovery_checked와 실제 활성화, pause/resume의 원 phase, 재개 뒤 resume_lifecycle/stop_requested 제거, closed/completed의 재개 불가를 실제 생산·저장·별도 load와 연결한다. 실행기 nested stop marker와 runtime stop_requested를 혼동하지 않는다. 허용된 boolean/문자열을 실제 작성자가 있는 것으로 간주하지 말고 쓰기/소비 또는 정확한 남김을 구별한다. 상태 enum 전 값의 실제 생산과 기존 단언을 판정하되 손으로 상태를 바꾼 fixture를 정상 producer로 세지 않는다.
4. updated_at은 현재 _save의 clock.now(), last_observed_utc는 검증된 관측/정상 게시의 UTC high-water라는 차이를 보존한다. _clock_guard의 읽기 관측 자체가 무조건 저장되는 것으로 바꾸지 않는다. clock 회귀·정상 변경 뒤 저장·재시작의 기존 성질을 유지하고 독립 시각 입력과 정확 저장값을 결박한다. 불필요한 새 문자열 형식 정책/정규화를 만들지 않는다.
5. cycles는 실제 research 결과 적용 시 증가하는 root 값과 초기0의 의미를, recovery_checked는 실제 활성화의 quiescence 검사 결과를 확인한다. next_research_reconsider_at는 초기 부재·활성화 예약·재고 갱신·만기 소비를 현재 생산 경로로 판단한다. nullable 허용과 실제 null 생산 여부는 구별한다. 다른 runtime counter나 OS 예약 성공을 이 결과로 인증하지 않는다.
6. scalar에는 required/optional 객체key가 없으므로 빈 fields==빈 written으로 완료 처리하지 않는다. 각 /value의 독립 기대값·설치 checker·검증된 Repository 게시·별도 reader decode, 같은 root metadata 포장과 옛 head 불변을 연결한다. 실제 저장 pointer는 runtime/_state/metadata.json#/record/<name>이며 새 wrapper는 필요 없다. 손상 read가 필요할 때만 비검증 publish를 쓰고 정상 성공은 실제 검증 경로를 통과시킨다. 정상대조와 정확한 반려 대상/원인·게시 전 head 불변을 유지한다.
7. 자기 writes의 lifecycle/planning/초기화/Repository/StateContract 또는 직접시험에서 확인한 실제 결함은 관련 수리와 확인까지 한 번에 마친다. 신규 전용 helper/계약시험은 기존 시험을 보완하는 편이 불명확할 때만 사용한다. 필요하면 contracts.pairs.assert_pair를 소비하며 순방향/역방향 알고리즘을 복제하지 않는다. 구판 별칭·자동변환·검증 우회·기대값 약화는 추가하지 않는다. 수용된 metadata5 단언은 보존한다.

## 최소 확인과 인계

제품 수정은 자기 workspace의 task.json.writes에 한한다. 공식 run_tests.py --jobs 1로 새 수리의 불확실성만 가장 작은 관련 ID에서 확인한다. 실행 체인 execution-fields→storage-academic와 본 task는 최대2개의 시험 슬롯이며 전체 상한3을 지킨다. 전체 일반/fresh T3/전체변이/T4/T5·유료 모델/HTTP/실Lean/native Job/설치/OS예약·대형 비용 실행은 하지 않는다. 실제 제품 생산/저장과 외부 Git/clock/host/Calls 포트 대역을 구별한다.

8가족별 현재 shape·생산/수신·독립 입력축·단언·재사용한 원보고/판본·보완·충족 또는 구체적 남김을 report/evidence에 남긴다. 모든 쓰기분기 전건 도달은 측정하지 않은 채 완료라고 하지 않는다. 최종 통합판 실행은 후속 관문이다. 초기 실패/fixture 오류·선택/고유 실제row·관측exit·소스SHA·실행중변경·소프트초과를 보존하고 다른 판본의 성공을 합산하지 않는다. 확인이 충분하면 반복하지 않는다. 비용캐시는 관측을 evidence에 보존한 뒤 own base로 복원하고 공식 build_skill_mirrors.py 생성/check를 수행한다.

protocol 형식 report.json을 작성하고 python C:/math/services/async-development/check.py report C:/math/.async/dm storage-lifecycle로 검사한다. 공용 context/plan/seams/queue/state·다른task·engine·Git index/commit·graphify·기존 연구는 수정하지 않는다. 다른 가족·원요구/K/P2·G4~G8·L01·Windows1314·최종review는 남기며 manager가 통합·수용과 공용 설명을 맡는다.
