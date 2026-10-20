# 활동·실행·공급자 대기의 실제 저장 계약을 마무리한다

사용자는 실제 생산값이 검증 켜진 저장소를 통과하고, 스키마에만 남은 필드나 검사되지 않는 쓰기가 시험을 빠져나가지 않기를 원한다. R01/1-A·1-B와 K-78의 남은 저장 가족 중 같은 실행 수명·입장·공급자 대기 경로를 쓰는 네 가족의 현재 의미와 필요한 수리를 한 task에서 마친다. 이미 수용된 reservations/config/profile의 여섯 가족을 다시 조사하지 않는다. tasks와 queue는 이 네 가족의 실제 입력·연결로 소비하되 전체 필드 역방향 질문은 별도 남김이다.

SESSION_JSON, task.json, inputs/context.md·plan.md·seams.md, do-math AGENTS.md·시험-지침.md를 읽는다. 원자료는 C:/math/docs/do-math/continuous-development-2026-10-13/sources의 user-decisions.md·requirements-index.json·model-policy-2026-10-14.md·document-batching-2026-10-14.md, phases/001/tasks/closure-map/evidence/requirement-state.json의 R01/1-A·1-B와 K-78, C:/math/docs/do-math/시험-재편-2026-09-29/설계.md 3.3절/A20 및 조사/대역-사각지대.md다. 직접 입력은 C:/math/.async/dm/tasks/keep-storage/evidence/families.json·judgment.md와 storage-profiles의 report.json·evidence/families.json·write-sites.json, managers/0046/review.md다. C:/math의 원자료와 공용 소스는 읽기 전용이다.

선행은 storage-profiles 하나다. 실제 저장을 통과한 프로필/입장 입력과 family_receiver/acquire_profile를 재사용할 수 있어 그 수용 결과를 소비한다. storage-knowledge와 proof-baseline의 완료나 미수용 workspace를 기다리거나 소비하지 않는다. 기존 task의 배정은 유지한다.

## 네 가족과 판정 질문

모집단은 keep-storage/evidence/families.json의 runtime.activities, runtime.executions, runtime.provider_waits, runtime.provider_wake 네 행이다. 현재 원문·코드가 정의의 정본이며 과거 표의 필드/행 번호 불일치는 그 자체로 결함이 아니다.

1. 각 가족의 현행 shape, checker/validator, 실제 producer와 저장 caller를 확인한다. activities.open_activity/assign_execution/bind_action/wait/resume/finish 및 execution_lifecycle.create_execution/transition_execution의 실제 이름·분기를 읽는다. execution의 입장 전 준비, 시작/수집/종료·실패/재시작, 입력/출력/관찰·프로필/예약 참조는 기존 직접시험과 수용 결과를 먼저 연결한다. 모든 역할 조합을 새 거대 시나리오로 만들 필요는 없다.
2. 정본의 required+optional 각 필드에 실제 producer 분기→검증 receiver→저장·재적재와 독립 기대값을 연결한다. 필드명 사용·사후 fixture 보충·비검증 `_save` 대역만으로 충족 판정을 하지 않는다. 기존 충분한 시험과 불변 정의는 정확 ID·원보고/판본을 연결해 재사용한다. 필요한 설정·공급자 선택지와 0/1/여럿·선택 필드 있음/없음은 실제 유효 입력축으로 확인하며 불필요한 Cartesian product는 만들지 않는다.
3. SessionSlots.provider_result_from_run/acquire/release와 provider_wait의 실제 waiting/checking/available 생산을 저장·재적재에 연결한다. 같은 admitted provider와 실패 evidence, retry_at·generation·attempts·probe_owner·probe_started_at의 현재 의미, 늦은 성공이 새 반려를 풀지 않는 기존 성질을 보존한다. 제약 대기는 실제 성공 응답 또는 정확 owner의 결과로 해소되고 로컬 종료만으로 공급자 복구를 인증하지 않는다. 프로필/예약 필드 전체는 storage-profiles의 수용 범위를 재사용한다.
4. provider_wake는 scheduler.SchedulerMixin._schedule_provider_wake → scheduled_operator.reconcile_wake의 실제 반환에서 observed를 뺀 singleton이다. operator 미사용/기존 wake, 등록·취소·실패의 현재 유효 분기와 저장 receiver를 읽는다. 열린 EVIDENCE schema가 필드 이름을 모르면 그 면제와 실제 생산 출력/내용 보존을 명시한다. 빈 fields==빈 written만으로 통과시키거나 이 질문을 닫기 위해 불필요한 닫힌 schema를 만들지 않는다. scheduler 포트만 대역으로 두고 실제 OS 예약은 변경하지 않는다.
5. 확인된 시험 공백은 전용 tests/support/storage_execution_pairs.py·contracts/test_storage_execution_pairs.py 또는 해당 직접시험에서 최소 보완한다. 기존 Pair/family_receiver/record_store/engine_on을 읽어 재사용하되 모든 shape에 Pair를 강제하거나 새 범용 registry를 만들지 않는다. 생산자 필드와 저장 계약의 실제 불일치가 있으면 현재 소비 목적부터 판단하고 자기 writes의 실제 제공자·시험을 함께 고친다. 미생산 optional 필드를 무조건 지우거나 옛 기본값/우회 schema/검사 예외로 메우지 않는다.
6. 원래 A-02의 역사 review-cycle 종료나 공개 record 삭제가 이번 실제 실행/활동 생산자와 관련되면 현재 대상·생산자 유무를 기존 r08/r29-r30 남김과 연결해 함께 판정한다. 관계가 없으면 새 전수조사로 넓히지 않고 그 남김을 유지한다. 명시 null, 원결과 보존, 정확 owner·한 번 정산, 공개 pause/restart와 과거 head 불변은 관련 수용 성질을 약화하지 않는다.

## 소유 범위와 완료

task.json의 실행/활동·공급자 대기 제공자, 전용 helper/계약시험과 해당 직접시험·미러만 수정한다. core_engine/call_engine 등의 권한도 이 네 가족에 필요한 변경에 한한다. 중앙 state_contract·record_schemas, 일반 contracts/pairs.py·test_pairs.py, 공용 test_producer_record_storage/storage_records, 지식·신뢰·검토 helper와 이음새-정본.md는 실행 중 storage-knowledge 소유이므로 자기 시작판에서 읽기만 한다. storage_profile_pairs와 profile/config/budget 제공자도 읽기 전용이다. 중앙 schema 등 범위 밖 수리가 실제 필요하면 정확 필드·생산 반례·소비 오류·필요 경로를 보고하고 가능한 독립 작업을 마친다. 검사 우회로 범위 충돌을 숨기지 않는다. 변경 계약의 입출력·반려·호출자는 report로 manager에게 인계한다.

정적 판정으로 충분하면 실행하지 않는다. 수리의 불확실성만 자기 workspace 공식 run_tests.py --jobs 1의 작은 관련 ID로 확인한다. 현재 시험 슬롯은 storage-knowledge, proof-baseline, 이 task의 최대3개·각jobs1이다. proof-baseline에 예약된 첫 빈 슬롯을 빼앗지 않고 종료한 storage-profiles/keep-rejections의 다른 한 슬롯을 사용한다. 전체 일반/fresh T3/변이/T4/T5·유료 공급자/HTTP/실 Lean/새 native Job·OS 예약/설치·대형 비용 실행은 하지 않는다. 실제 Repository/StateContract와 포트 대역의 경계를 구별한다.

네 가족마다 제공/소비·필드/입력축·정확 단언·기존 근거/새 수리·충족 또는 구체적 남김을 적는다. 1-B의 모든 쓰기분기 미도달0은 최종 fresh T3의 과제다. 이번에는 해당 producer/쓰기 지점·source SHA·관련 시험 ID를 그 측정에 연결할 입력으로 남기며 작은 실행을 최종 도달 증거로 확대하지 않는다. 나머지61가족, 다른 K/P2·G4~G8·L01/Windows1314·최종 review는 종결하지 않는다.

초기 실패/fixture 오류와 selected/고유 실제 row·관측exit·source SHA·실행 중 변경·소프트초과를 보존한다. 다른 판본 성공을 한 최종판 성공으로 합산하지 않는다. 비용캐시를 evidence에 보존한 뒤 own base로 복원하고 공식 build_skill_mirrors.py 생성/check를 수행한다. check.py report C:/math/.async/dm storage-execution PASS로 report.json을 제출한다. 공용 source·context/plan/seams·queue/state, 다른 task, engine, Git index, graphify, 기존 연구 운전은 수정하지 않는다.
