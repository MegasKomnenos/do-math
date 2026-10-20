# 실행 레코드의 실제 생산·수신 계약을 마무리한다

사용자 목표는 실제 생산값이 검증 켜진 저장소를 통과하며, 스키마에만 남은 필드와 검사되지 않는 쓰기가 시험을 빠져나가지 않게 하는 것이다. storage-execution이 마친 activities/provider_waits/provider_wake 세 가족은 다시 조사하지 않는다. 남긴 runtime.executions 한 가족의 required+optional 대응과 F1, 같은 검사 helper의 중복만 이 task에서 구현·수정·필요한 확인까지 마친다. 원래 102필드라는 수를 보존하는 것이 목표는 아니다. 현재 사용 목적과 실제 생산·소비에 맞는 계약을 남긴다.

SESSION_JSON, task.json, inputs/context.md·plan.md·seams.md, do-math AGENTS.md·시험-지침.md를 읽는다. 원문 요구는 C:/math/docs/do-math/continuous-development-2026-10-13/sources/user-decisions.md·requirements-index.json·model-policy-2026-10-14.md·document-batching-2026-10-14.md, phases/001/tasks/closure-map/evidence/requirement-state.json의 R01/1-A·1-B/K-78과 C:/math/docs/do-math/시험-재편-2026-09-29/설계.md 3.3/A20이다. 직접 입력은 C:/math/.async/dm/tasks/storage-execution/report.json·evidence/judgment.md·families.json·execution-fields.json·execution-write-candidates.json·historical-rows.json·assertion-sources.json·write-sites.json 및 managers/0048/review.md다. 원자료는 읽기 전용이다.

선행은 storage-execution과 storage-authority다. 전자는 실제 실행 저장 helper·부분 근거를 제공한다. 후자는 수정 중인 governance 및 중앙 schema/checker의 수용판을 제공하며, 특히 실행 독립성 소비를 그 판본에서 판단해야 한다. storage-authority의 정의/진행을 바꾸지 않는다. 후속 시작판에 그 수용 결과가 반영된 뒤 같은 파일을 한 번에 수정한다. 독립 storage-metadata의 완료는 요구하지 않으며 그 미수용 workspace를 읽지 않는다.

## 실제 판정과 수리

1. execution-fields.json은 102개 이름의 후보 색인이며 모든 행이 not_closed_by_this_task다. AST 쓰기 후보, 다른 record의 같은 이름, 중첩 필드, 시험 literal을 실행 최상위 실제 생산/저장 근거로 승격하지 않는다. 현재 RECORDS['executions']와 실제 생성·입장·준비·실행·수집·실패·종료·재시작 경로를 대조해 기존 충분한 producer→검증 저장/load·독립 기대값의 정확 ID/판본을 먼저 재사용한다. 새 전수 파일 목록이나 거대 역할 조합을 만들지 않는다.
2. F1의 최소 세 이름을 현재 소비 목적에서 해결한다. execution.pid는 launch owner/process 및 capacity.process의 중첩 신원과 구별한다. finished_at은 activity/recovery/trust 종료 자료이고 execution 종료 정본은 ended_at이다. conversation_id는 governance.validate_independent_execution이 읽지만 현행 실행 최상위 생산을 찾지 못했다. 같은 함수의 provider_session_id도 실제 허용/생산/소비를 함께 확인한다. manager의 현재 검색은 두 이름의 실행 소비가 이 함수에만 있음을 확인했지만, 그것만으로 독립성 요구를 폐기한 것은 아니다. 실제 continuation/context lineage와 공급자 세션 신원이 무엇을 보장하는지 현재 producer·수신자·직접시험으로 판단한다. 필요한 독립성 검사를 약화하거나 중첩 신원을 무의미하게 복사하지 않는다.
3. 사용되지 않는 허용 필드/소비는 같은 변경에서 정리하고 실제 필요한 자료는 그 정본 생산·수신·검사로 연결한다. 구판 alias/default/자동 변환, fixture 사후 필드 보충, 열린 schema나 검사 예외로 역방향 공백을 메우지 않는다. 기록된 연구의 서로 다른 실행·프로필·입력 판본은 구판 호환과 구별한다. 제거한 필드의 정확 반려와 현재 정상 record의 수신을 함께 확인한다. F1 세 개만 처리한 뒤 나머지 필드를 닫았다고 하지 않는다.
4. 현재 유효 필드에는 실제 생산 branch→설치 checker/validator→Repository/StateContract 게시·별도 load와 그 의미를 검사하는 단언을 연결한다. 역할별 결과·원결과/raw ref·제출/관찰·현재성/근거·프로필/예약·시간/종료/재시작 필드는 기존 불변 직접 근거를 적극 재사용한다. 추가 회귀는 실제 남은 공백에만 둔다. 모든 필드를 한 객체에 넣는 합성 fixture나 새 범용 registry는 만들지 않는다. 명시 null, 원결과·정확 owner·한 번 정산·공개 pause/restart·옛 head 불변은 보존한다.
5. storage-execution 시작 뒤 storage-knowledge가 추가한 contracts.pairs.assert_pair를 현재 정본으로 소비한다. 전용 StorageExecutionPairTests.assert_pair의 같은 역방향 규칙을 다시 구현하지 말고 기존 호출을 공통 정의에 연결한다. 기존 정확 dict/내용/오류 원인 단언은 유지한다. 이 작은 보완을 별도 task로 나누지 않는다.
6. 실제 필요한 제공자·소비자·schema·직접시험·이음새 설명·미러를 task.json의 범위에서 함께 수정한다. 실행 자료를 전달하는 경계 밖 제품을 임의 정리하지 않는다. tasks/queue의 전체 역방향, 역사 A-02 review-cycle 종료/공개 삭제의 무관한 전수조사, 다른 저장 가족은 배정 밖이다. 관련된 현행 생산자가 새로 확인되면 그 정확한 영향만 함께 기록한다.

## 검증·결과

정적 판단과 원보고의 정확 관련 row/판본 비교로 충분한 성질은 반복 실행하지 않는다. 수리의 불확실성만 자기 workspace 공식 run_tests.py --jobs 1의 작은 관련 ID로 확인한다. storage-authority 수용 후 이 task와 독립 storage-metadata의 최대 두 시험 슬롯이며 전체 상한3을 넘지 않는다. 전체 일반/fresh T3/극단 변이/T4/T5·유료 모델/HTTP/실 Lean/native Job/OS 예약/설치·대형 비용 실행은 하지 않는다. 실제 저장/engine과 외부 포트 대역을 구별한다.

필드별 결과는 현행 정본·생산 분기·저장 수신·정확 단언/원판본·유지/수리/제거·구체적인 남김으로 기록한다. 최종 fresh T3에 필요한 producer/쓰기 심볼·소스 SHA·관련 ID는 보존하되 이번 작은 실행을 모든 쓰기분기 도달0의 증거로 쓰지 않는다. 전체 R01/K-78·다른 원요구/K/P2·G4~G8·L01/Windows1314·최종 review는 종결하지 않는다.

초기 실패와 fixture 오류·selected/고유 실제 row·관측 exit·소스 SHA·실행중 변경·소프트초과를 구별해 보존한다. 서로 다른 판본의 통과를 합산하지 않는다. 비용캐시는 evidence에 관측값을 보존한 뒤 own base로 복원한다. 공식 build_skill_mirrors.py 생성/check와 check.py report C:/math/.async/dm execution-fields를 마친다. 공용 source/context/plan/seams/queue/state, 다른 task, engine, Git index, graphify와 기존 연구 운전은 수정하지 않는다.
