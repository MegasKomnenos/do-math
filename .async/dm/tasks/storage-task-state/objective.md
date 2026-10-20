# 과제 계약·판정 이력과 재사용 관찰규칙의 저장 두 가족을 마친다

실제 준비·계획·판정으로 만든 과제가 저장과 재시작 뒤에도 원 계약·의무·판본을 보존하도록 runtime.tasks와 runtime.task_observation_rules의 생산·검증 게시·별도 decode·내용/필드 대응을 완성한다. 두 가족은 같은 과제 생성/개정과 관찰규칙 준비·무효화 경계를 사용하므로 필요한 구현·직접시험·설명·공식 미러 수리를 한 task에서 마친다. 필드 목록이나 읽기 보고만 만들고 관련 수리를 다시 쪼개지 않는다.

SESSION_JSON·task.json·inputs/context.md·plan.md·seams.md, do-math AGENTS.md와 scripts/tests/시험-지침.md를 읽는다. 원요구 R01/1-A·1-B/K-78와 설계 3.3/A20, 사용자/모델/묶음 결정은 task.inputs의 C:/math/docs 원자료를 따른다. 같은 root/family의 모집단은 C:/math/.async/dm/tasks/keep-storage/evidence/families.json이다. managers/0061/review.md와 storage-actions-fix/report.json, 시작 시 수용된 storage-recovery/storage-questions 보고, 기존 r41/r44-fix/storage-academic 및 계획/개정 수용 근거를 실제 소스·단언과 대조한다. 외부 원자료와 다른 task는 읽기 전용이다.

## 지정 질문과 완료 판단

1. tasks는 ID map이고 실제 수신 schema는 record_schemas.schemas.RECORDS['tasks']다. contracts.task_candidate_record → CoreEngineMixin._apply의 research_preparation, PlanningEngineMixin의 model metadata/queue plan, academic_engine의 사용자 학술 계약, task_scope의 판정/처분 등 현재 producer를 읽어 필수/선택/닫힌 중첩 필드의 실제 생산·저장 위치를 연결한다. 초기 준비·계약 개정·검토·계획 선택·결과/평가·현재성 변화·범위 이전/철회의 충분한 기존 장면을 재사용한다. 모든 필드가 한 과제나 한 실행에서 동시에 생겨야 한다는 조건은 추가하지 않는다.
2. 독립 wire 원문과 사용자 결정에서 question/scope/expected·진전기준/완료의무·inputs/basis/reuse/dependencies·profile/authority 참조를 대조한다. 계약 revision/hash, producer/author 실행, 실제 결과·검토/평가·revision/model-assessment 이력, 지식 개정·학술 의무/외부효과·이전된 의무의 원 좌표와 내용도 현재 생산 의미에 맞춰 연결한다. 열린 HISTORY/EVIDENCE는 빈 properties 순회만으로 끝내지 않고 원 응답·원결정·봉인 입력·과거 판본의 의미 있는 내용과 대조한다. 이미 검증한 권한·현재성·지정 심판·원 owner·정산 성질은 정확한 원보고/불변 코드로 재사용하며 거대한 전이 시나리오를 새로 반복하지 않는다.
3. task_observation_rules는 task ID에 배열을 연결하는 singleton mapping이고 item은 공통 _RULE이다. CoreEngineMixin._apply_extensions와 PlanningEngineMixin의 실제 준비 경로, observations.task_rules_from_execution/validate_task_rules/bind_task_rules 및 CallEngineMixin._prepare_call 소비를 연결한다. 원 실행 제출의 subject와 저장의 재사용 $execution, 다음 실행에 대한 binding이 서로 분리되는 의미를 보존한다. 필수/선택/닫힌 중첩 필드·규칙 순서·원 evidence 및 실제 새 규칙/개정 뒤 제거·재준비를 검증 저장/cold load와 대응한다. task.initial_observation_rules·실행 tracker의 live rule proposal·별도 runtime map은 서로 다른 소유/표현이므로 혼동하지 않는다. 공통 _RULE의 전체 의무와 이 가족에서 유효한 생산 표본을 구별하고, 특정 가족에 없는 필드를 공통 미생산으로 제거하지 않는다.
4. 실제 producer → ResearchRepository 검증 게시 → 별도 installed_contract 객체를 받은 새 ResearchRepository의 첫 load로 blob decode를 연결한다. tasks map의 ID/manifest, 규칙 singleton, 원문/순서·부재/null·필요 artifact·옛 head 불변을 필요한 최소 범위에서 확인한다. 저장 전에 schema 슬롯을 채우는 fixture, 복제한 생산 계산을 기대값으로 쓰는 방법, publication cache를 새 decode로 세는 방법은 사용하지 않는다. 선행 storage_action_pairs.reader/keep와 storage_authority_pairs._named_fields, 기존 contracts.pairs.Pair/assert_pair를 재사용한다. 같은 장면을 공통화하면 기존 소비자/단언도 함께 유지한다.
5. 현재 필드 전체와 실제 producer/소비자를 확인한 뒤 표본 미도달과 실제 미생산 슬롯을 구별한다. 유효 필드는 필요한 실제 장면으로 연결하고, 미생산 슬롯만 schema/직접소비/시험/설명/미러에서 함께 정리한다. 구판 alias/default/검증 우회·부분집합 면제나 필드 숫자 유지를 위한 filler를 추가하지 않는다. 미생산 optional을 추가한 작은 반례가 같은 역방향 검사에서 실패하는지 확인한다. 실제 결함이나 삭제 슬롯은 정확 반려 사유와 head 불변/write0 등 남은 불확실성에 필요한 최소 확인을 한다. schema helper를 수리해야 하면 기존 authority/input/action/execution 소비에 영향을 주는 범위를 함께 마치고 별도 알고리즘/registry를 만들지 않는다.

## 선행과 수정 소유

직접 선행은 storage-questions다. recovery→questions가 공통 core/call/중앙schema/저장 직접시험과 제품 설명을 바꾸므로 그 수용판을 받은 뒤 같은 지점을 수정한다. storage-actions-fix의 입력 소유권, boolean/tuple/map/조건 필드 순회, 현재 action86/wait24 계약도 이 경로로 상속한다. 진행 중 배정이나 다른 task의 미수용 사본은 바꾸거나 소비하지 않는다.

task.json.writes의 과제 제공자/소비자·저장schema·직접시험/helper·제품 설명·미러 안에서 이번 두 가족과 직접 영향받는 기존 소비에 필요한 수정을 맡는다. contracts/support 디렉터리 권한은 공유 장면/검사 정본을 고치고 소비자를 함께 맞추기 위한 것이며 무관한 시험 재편 권한이 아니다. 예전 helper 읽기 전용 제약을 이 task에 새로 적용하지 않는다. 외부 operation/checkpoints, research.capability_evidence/review_policy 네 가족 전체는 이 배정 밖이다. 과제의 직접 학술/외부효과 좌표는 필요한 만큼 읽고 보존한다. 범위 밖 결함은 정확 입력·파일/심볼·영향을 보고하되 독립적으로 마칠 부분은 계속 진행한다.

## 최소 확인과 인계

코드/원보고가 충분한 성질은 다시 실행하지 않는다. 필요한 변경만 자기 workspace 공식 scripts/run_tests.py --jobs 1의 최소 관련 ID로 확인한다. 각 task jobs1·전체 시험worker상한3이며 전체 일반/fresh T3/극단변이/T4/T5·실provider/HTTP/native Git/Lean/Job·설치/OS예약은 이 배정이 아니다. 모든 쓰기 분기 도달은 최종 fresh T3와 구별한다.

두 가족의 실제 필드·생산/수신 심볼·독립 내용 근거·정확 시험ID/판본과 유지/수리/남김을 보고한다. 최초 실패·교정판, 선택/고유 실제row/counts/fixture_counts·실제 관측exit/source SHA/changed_during_run·소프트초과를 보존하고 서로 다른 판본을 단일 통과로 합산하지 않는다. 충분한 근거가 없는 부분은 완료로 표기하지 않는다.

공식 build_skill_mirrors.py 생성/check 후 비용캐시는 관측 bytes를 evidence에 보존하고 own base로 복원한다. `python C:/math/services/async-development/check.py report C:/math/.async/dm storage-task-state`를 통과시킨다. 공용 source/context/plan/seams/queue/state·다른 task·engine·Git index/commit·graphify·기존 연구는 수정하지 않는다. manager가 통합·수용한다. 원84의 나머지·관찰4 최종판/다른 원요구/K/P2·G4~G8·L01/Windows1314·최종 review는 별도로 남는다.
