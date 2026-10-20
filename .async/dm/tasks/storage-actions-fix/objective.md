# 요청 큐·보류의 남은 저장 계약과 공용 필드 순회를 함께 마친다

사용자 목표는 실제 생산값과 저장 수신 계약의 불일치가 시험을 빠져나가지 않게 하는 것이다. storage-actions가 수리한 입력 소유권을 보존하고, runtime.queue/runtime.waiting_actions와 이들이 공유하는 _ACTION의 미완료 필드·내용 대응을 마친다. 공용 helper 한 줄만 고친 뒤 나머지를 새 task로 넘기지 않고 실제 표본·필요한 제품/시험·설명·미러 수리를 함께 맡는다.

SESSION_JSON·task.json·inputs/context.md·plan.md·seams.md와 do-math AGENTS.md·시험-지침.md를 읽는다. 원요구 R01/1-A·1-B/K-78, 사용자/모델/묶음 결정 및 설계 3.3/A20은 task.inputs에 연결했다. C:/math/.async/dm/tasks/storage-actions/objective.md의 지정 질문을 계승하되, 그 문서의 공용 helper 읽기 전용 제한은 이 배정의 writes와 아래 소유 범위로 대체한다. 원 보고·실패·진단 소스는 수정하지 않는다.

## 시작판과 남은 결과

manager0060은 storage-actions의 정본5·미러5를 부분 수용했다. _enqueue는 revision binding 전에 전체 요청을 deepcopy한다. 원입력·ID/lineage·병합/순서·live 비병합·revision 부모·네 준비 보류의 검증 저장/별도 reader decode·정확 반려/write0의 최종9passed와909PythonSHA를 확인했다. 두 가족을 완료 수에 추가하지 않았다. 관련 원근거는 storage-actions/evidence/judgment.md·families.json·verification.json·historical-reuse.json 및 managers/0060/review.md·source-review.json·verification-review.json이다.

F2는 tests/support/storage_authority_pairs.py:_named_fields가 실제 _ACTION.repetition_lineage의 items=False에 .get을 호출하는 오류다. 별도 shared-action-inventory는 선택1/error1·실제exit1이고 전체 역방향 통과 근거가 아니다. 이 함수의 AST는 이후 ontology 수용판에서도 같으며, 최신 파일에는 storage-ontology-fix의 실제 종류 표본 수리가 함께 있다. 오래된 helper 파일 전체를 복원하지 않는다. reverse-blocker.json과 shared-action-diagnostic-source 두 파일은 재사용 가능한 조사 자료이지 그대로 복원할 구현 지시는 아니다.

1. 기존 _named_fields에서 boolean JSON schema와 object schema를 구별한다. 실제 사용하는 닫힌 중첩 object/array 및 tuple prefixItems의 명명된 필드 의무를 빠뜨리지 않고, True/False 자체에 properties가 없는 의미를 처리한다. 스키마 변형을 무조건 건너뛰거나 _ACTION만 면제하지 않는다. 기존 Pair/assert_pair와 이 순회 함수를 고쳐 사용하며 별도 registry/대체 순회 알고리즘을 만들지 않는다. 실제 실패 입력을 포함한 가장 작은 helper 확인으로 오류가 해소됐는지 먼저 판단한 뒤 필요한 생산 장면을 실행한다. 기존 authority/input/execution 소비의 필드 의미와 최신 종류 check 수리를 보존한다.
2. 시작판 공통 _ACTION은89필드(id/role 필수), waiting 행은27필드다. 현재 정의를 기준으로 실제 producer·consumer·저장 위치·독립 원값·직접 단언을 대응한다. queue만이 아니라 executions.action/waiting_actions.action/input_overflows.action 등 유효 공통 소비를 구별하고, 두 가족 각각의 표본과 공통 schema 전체 역방향을 구별한다. 각 유효 필수/선택·닫힌 중첩 필드는 실제 생산 표본에서 수신 검사와 assert_pair 역방향을 통과해야 한다. 미생산 optional을 추가한 작은 반례로 누락 검출을 확인한다. 기존89라는 숫자를 지키려고 무생산 슬롯을 채우거나, 표본이 없다는 이유만으로 유효 필드를 삭제하지 않는다. 제거는 현재 생산·소비를 확인한 슬롯에 한하며 실제 소비와 설명을 함께 바꾼다.
3. 준비 외 diagnosis/recovery/review/delegation/impact 등의 보류를 실제 owner 경로에서 만든다. kind/condition/next_owner, 원 action/execution/input_snapshot, 진단·복구·검토·위임 등의 닫힌 중첩 값과 열린 evidence의 원내용을 연결한다. action/행 reason의 null과 문자도 실제 생산·소비 및 기존 근거에 맞게 판단한다. public control/record_due_events 등의 요청 생산은 독립 사건·영수증·의무/관찰 자료와 연결한다. 선행의 합성 _enqueue refs 표본이 실제 모든 owner 생산을 입증했다고 세지 않는다. 충분한 기존 종료·재개·정산·현재성/권한·예약·원owner·재전달 성질은 원보고와 현재 코드를 재사용한다.
4. 실제 production → ResearchRepository의 검증 게시 → 별도 installed_contract 객체를 받은 새 reader의 첫 load로 저장값을 확인한다. queue 순서/manifest, waiting singleton blob, 필요한 원artifact·참조·옛head·독립 원문/내용을 확인한다. 저장 직전에 수신 필드를 보충하는 fixture나 publication cache를 새 decode로 세는 방법은 사용하지 않는다. 기존 storage_execution_pairs의 실제 장면과 storage_action_pairs.preparation_case를 필요에 맞게 재사용한다. 공통화가 필요하면 기존 소비자도 같은 helper를 소비하게 하고 기존 단언을 유지한다. 111초 진단의 모든 장면을 매번 반복할 의무는 없으며 남은 질문을 답하는 최소 조합을 고른다.
5. 확인한 실제 결함은 제공자·소비자·schema·직접시험·공용 설명·공식 미러에서 함께 수리한다. 새로운 whole-action deepcopy와 겹치는 기존 payload별 복사가 불필요하다면 같은 수리에서 단순화할 수 있지만 원입력/반환/다른 요청의 격리를 유지한다. 이 작은 정리를 별도 task로 나누지 않는다. 기존 구판 alias/default/불필요 fallback/검증 예외를 추가하지 않는다. 필요한 정확 타입/참조/키 불일치의 반려 사유·head 불변/write0와 손상 read는 이미 충분한 선행 근거를 재사용하고 변경이 영향을 주는 부분만 확인한다.

## 선행과 수정 소유

직접 선행은 storage-actions와 storage-ontology-fix다. 전자는 입력 소유권·준비 장면과 시험의 수용판, 후자는 이번에 수정할 storage_authority_pairs 및 기존 종류 소비자의 최신 수용판을 제공한다. 두 task는 이미 수용됐다. storage-recovery는 아직 시작하지 않았으며 이 결과 수용 뒤 core/중앙schema/저장 직접시험·설명을 소비한다. 진행 중인 다른 task의 사본이나 미수용 결과에 의존하지 않는다.

task.json.writes에는 원 action 제공자/저장/직접시험과 관련 추가 action owner, 공통 contracts/support 시험 helper 및 미러를 포함한다. 이 범위 안에서는 이번 두 가족·공통 action 계약·직접 영향받는 기존 소비에 필요한 수정을 맡는다. 공용 helper를 읽기 전용으로 두었던 이전 제약은 없다. 넓은 helper 디렉터리 권한은 같은 장면/검사 정본을 고치고 소비자를 함께 옮기기 위한 것이며 무관한 시험 재편을 뜻하지 않는다. products 자체의 전체 tasks/checkpoints/external_operations, 연구 capability/review 정책, 질문 네 가족의 전체 대응은 후속의 몫이다. action의 필요한 실제 생산 맥락으로는 사용할 수 있다.

## 확인과 보고

정적 코드와 기존 원보고로 충분한 성질은 재실행하지 않는다. 필요한 변경은 자기 workspace 공식 scripts/run_tests.py --jobs 1의 최소 관련 선택으로 확인한다. 각task jobs1·전체 시험worker상한3이다. 전체 일반/fresh T3/극단변이/T4/T5·유료 provider/HTTP/native Git/Lean/Job·설치/OS예약은 이 배정이 아니다. 모든 쓰기분기 도달 인증과 이번 필드/내용 대응을 구별한다.

가족별·공통 action별 현재 필드/실제 생산·수신 심볼·독립 값·정확 시험ID/판본·수리/재사용/남김을 보고한다. 최초 실패·준비 오류·교정판, 선택/고유 실제row/counts/fixture·실제관측exit/source SHA/changed_during_run·소프트초과를 보존하며 서로 다른 판본을 합산하지 않는다. 공용 helper 오류 해소만으로 두 가족 전체 완료를 주장하지 않는다.

공식 build_skill_mirrors.py 생성/check를 수행하고 비용캐시는 관측을 evidence에 보존한 뒤 own base로 복원한다. `python C:/math/services/async-development/check.py report C:/math/.async/dm storage-actions-fix`를 통과시킨다. 공용source/context/plan/seams/queue/state·다른 task·engine·Git index/commit·graphify·기존 연구는 수정하지 않는다. 원84가족의 나머지·관찰4 최종판/다른원요구/K/P2·G4~G8·L01/Windows1314·최종review는 별도 남긴다.
