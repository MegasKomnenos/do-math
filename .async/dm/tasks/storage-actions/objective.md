# 실행 요청 큐와 보류 요청의 실제 저장 계약을 마친다

사용자 목표는 실제 생산값과 저장 수신 계약의 불일치가 시험을 빠져나가지 않게 하는 것이다. runtime.queue와 runtime.waiting_actions 두 가족을 같은 action 생산·병합·보류·재개와 공통 _ACTION 저장 계약의 묶음으로 맡는다. 필드 목록만 만들지 않고 필요한 구현·직접시험·설명·미러 수리를 한 task에서 마친다. 별도의 전수 조사 task나 필드별 작은 후속으로 나누지 않는다.

SESSION_JSON, task.json, inputs/context.md·plan.md·seams.md, do-math AGENTS.md·시험-지침.md를 읽는다. 원요구는 C:/math/docs/do-math/continuous-development-2026-10-13/sources의 user-decisions.md·requirements-index.json·model-policy-2026-10-14.md·document-batching-2026-10-14.md와 phases/001/tasks/closure-map/evidence/requirement-state.json의 R01/1-A·1-B/K-78, C:/math/docs/do-math/시험-재편-2026-09-29/설계.md 3.3/A20이다. C:/math/.async/dm/tasks/keep-storage/evidence/families.json의 원 root/family를 유지한다. managers/0056/review.md 및 r11/r12-r13-fix/r29-r30/r37-review/r37-edges/r40-r43/r41/r49-startup/execution-storage/storage-events/storage-inputs의 보고와 필요한 원근거는 읽기 전용이다. 전개 순서를 재발명하지 말고 현재 수용된 실제 코드를 따른다.

## 지정 질문과 완료 판단

1. queue는 list item record, waiting_actions는 action ID→닫힌 행 singleton이다. record_schemas.schemas._ACTION은 queue뿐 아니라 executions.action·waiting_actions.action·다른 중첩 저장 위치에서도 소비한다. 현재 schema/checker/semantic validator와 실제 writer·consumer·저장 위치를 대응한다. 공통 action 전체 필드의 생산 근거와 두 가족 각각에서 실제 나타나는 필드를 구별한다. queue에 없다는 이유만으로 실행 내 action에 실제 쓰이는 필드를 삭제하지 않는다. 반대로 다른 record의 동명 슬롯을 이 action의 생산 근거로 쓰지 않는다. 특정 가족의 표본만으로 공통 schema 전체 역방향을 충족했다고 쓰지 않는다.
2. CoreEngineMixin._enqueue의 실제 신규 ID/lineage, 같은 요청의 병합과 서로 다른 payload의 분리, reason/requested_by/event·receipt·obligation·observation·evidence refs의 순서와 중복 제거, revision 관련 basis/followup·owner와 현재성을 독립 입력/시각/ID에 연결한다. planning.record_due_events, 공개 제어/실제 적용과 각 owner가 작성한 요청에서 필요한 표본을 고른다. hand-built action을 직접 queue에 넣은 fixture는 실제 producer 근거와 구별한다. 원 요청의 deepcopy, 이미 live인 요청 비병합, 소비/폐기 뒤 다른 요청의 보존, 저장 순서와 옛head/restart의 충분한 기존 근거를 재사용한다. 모든 역할의 새 큰 시나리오를 반복할 필요는 없다.
3. wait_rules.waiting_action/update_waiting_action 및 core/call/dispatch/planning/revision/governance/formal/repair의 실제 호출을 확인한다. reason의 null/문자, kind/condition/next_owner, 원 action/execution/input_snapshot, 진단·복구·검토·위임·관찰준비 관련 닫힌 중첩 값과 열린 evidence를 구별한다. 보류→조건 해소/교정→재개·정산이 원 action/owner/lineage와 실제 예약·원결과를 보존하는 현행 성질을 기존 직접시험에서 연결한다. 반환 helper의 모양만 검사하지 말고 실제 owner가 runtime에 작성하여 검증 게시한 값을 새 reader로 확인한다. 필요 없는 optional은 전 생산·소비를 확인한 뒤에만 제거한다. 정확한 원문/필드 소비가 남으면 빈 표본을 이유로 삭제하지 않는다.
4. 실제 production→ResearchRepository.initialize/save_with_state의 검증 게시→새 installed_contract 객체를 받은 reader의 첫 load를 사용한다. queue의 record/list 순서와 waiting singleton blob/manifest, 독립 원값·참조·필요 artifact·옛head를 연결한다. Repository._read_key의 contract 객체를 바꿔 publication cache 반환을 별도 decode로 오인하지 않는다. 비검증 publish는 손상 read 반례에만 쓴다. 정상 저장 직전에 모든 optional을 채우는 합성 fixture로 역방향 검사를 통과시키지 않는다.
5. 닫힌 필수/선택·중첩 action/행 필드는 기존 contracts.pairs.assert_pair와 필요할 때 storage_authority_pairs._named_fields를 재사용한다. 열린 EVIDENCE/HISTORY에는 독립 내용·순서·참조 단언을 사용한다. 새 registry/범용 wrapper/역방향 알고리즘을 만들지 않는다. 현재 공유 _ACTION의 유효 생산 필드와 두 가족의 실제 저장 표본을 같은 근거에서 연결하고, 미생산 optional 추가를 기존 공통 검사가 놓치지 않는지 최소 반례로 확인한다. 필요한 정확 타입/참조/키 불일치·현재성 반려의 head불변/write0 및 손상 read는 기존 근거를 우선 재사용한다.
6. 확인한 결함은 자기 writes의 producer·소비자·schema·시험·설명·미러까지 함께 수리한다. 구판 alias/default 보충/검증 예외를 추가하지 않고 권한·현재성·원 owner·정산·불변 입력과 정확 1회 처리를 유지한다. `_ACTION`을 바꾸면 기존 실행·중첩 소비의 영향도 해당 변경에 필요한 최소 범위로 확인한다. 모든 action 쓰기분기의 fresh T3 도달 인증과 두 가족의 의미/필드 대응은 구별한다.

## 실제 선행과 수정 소유

storage-inputs 하나를 직접 선행으로 받는다. 기존 storage-events→storage-inputs가 core_engine·초기화·Repository·중앙schema·공유설명과 직접 저장시험을 소유하므로 그 수용판을 소비한다. 이는 같은 파일의 수리와 통합 충돌을 막는 실제 선행이며 다른 독립 결과의 종료는 요구하지 않는다. 미수용 workspace를 읽거나 진행 중 배정을 바꾸지 않는다.

task.json의 action 생산/대기·재개 제공자, 중앙schema/저장, 직접 단위·sim·flow·전용 계약시험/helper와 이음새 설명만 수정한다. 기존 helper/시험의 같은 장면은 공유하고, 새 storage_action_pairs.py 및 test_storage_action_pairs.py는 반복 장면을 실제로 함께 소비할 때 사용한다. 공통 contracts.pairs와 이미 수용된 다른 storage helper는 읽기 전용이다. 실제 결함이 writes 밖이면 최소 원 입력·실패·필요 심볼과 사용 영향을 남기고 독립 범위는 마친다. tasks 자체의 전체 저장 필드, history/questions/input_overflows 등 다른14미배정 가족의 전체 감사는 맡지 않는다. 이들 record를 action 생산·소비의 필요한 맥락으로 사용할 수 있다.

## 최소 확인과 보고

원보고와 현재 정적 판정으로 충분한 질문은 실행하지 않는다. 필요한 수정만 자기 workspace의 공식 scripts/run_tests.py --jobs 1로 최소 관련 선택을 확인한다. 전체 동시시험 상한3, 본 task는1이다. 전체 일반/fresh T3/극단변이/T4/T5·유료 공급자/HTTP/native Git/Lean/Job·설치/OS예약·대형 비용 실행은 배정하지 않는다. 실제 engine/Repository/StateContract와 외부 포트 대역을 구별한다.

가족별 현재 필드·생산 심볼/소스 SHA·수신/저장·독립 기대값·정확 시험ID/원보고판본과 유지/수리/구체적 남김을 보고한다. 선택·고유 실제row/counts·fixture_counts·실행 로그의 실제 exit·source SHA·changed_during_run·소프트초과를 보존한다. successful로 exit를 계산해 관측값으로 쓰지 않으며 최초 실패/준비 오류/교정판·서로 다른 판본의 성공을 합산하지 않는다. 판본 연결에 충분한 기존 근거를 불필요하게 재실행하지 않는다.

비용캐시는 관측을 evidence에 보존한 뒤 own base로 복원한다. 공식 build_skill_mirrors.py 생성/check·writes를 확인하고 report.json에 수행 결과·이유·검증 한계·남김을 기록해 `python C:/math/services/async-development/check.py report C:/math/.async/dm storage-actions`를 통과시킨다. 공용 source/context/plan/seams/queue/state·다른task·engine·Git index/commit·graphify·기존 연구는 수정하지 않는다. 원84가족의 나머지, 관찰4의 최종판·다른 원요구/K/P2·G4~G8·L01/Windows1314·최종review는 별도다.
