# 목적과 완료할 결과

R04/1-A의 남은 질문인 조건 문법의 enum·반복 한도 다섯 키의 실제 소비·러너 결과 영수증의 JSON 전달을 판정하고, 확인된 시험 공백은 이 task에서 수리한다. 사용자 목표는 실제 생산·수신의 불일치가 시험을 빠져나가지 않게 하는 것이다. 기존에 충분히 입증된 성질은 유지하며, 새 구현이 필요한지 먼저 현재 정의·단언·원보고로 판단한다. 이 작업은 전체 review나 새 기능 설계가 아니다.

## 입력과 수정 경계

SESSION_JSON의 workspace와 고정 inputs/context.md·plan.md·seams.md, task.json을 기준으로 일한다. 스킬 상대 경로는 workspace 기준이다. C:/math/.async/dm/tasks/r02-fix/report.json·evidence와 managers/0005/review.md·source-review.json은 수용된 요청 시험 수리의 읽기 전용 근거다. r02-fix만 선행이며 r07-fix·r18-fix의 결과를 기다리거나 중간 파일을 소비하지 않는다.

원문은 C:/math/docs/do-math/continuous-development-2026-10-13/sources/user-decisions.md와 requirements-index.json, 같은 실행의 phases/001/tasks/closure-map/evidence/requirement-state.json·tracking-state.json·prior-review-state.json·evidence-catalog.json이다. tracking R04, requirement 1-A, current_work.boundary_storage_guard_correction 및 PR18에서 이 질문과 직접 연결되는 slice를 읽는다. run:은 위 continuous-development 실행 루트, 과거 repo:docs/...는 C:/math의 원자료다. 보존 원보고가 없으면 부재를 명시하고 과거 counts를 새 성공으로 쓰지 않는다. PR18 전체·K/P2 전체를 다시 감사하는 배정이 아니다.

제품 쓰기는 task.json에 지정한 contracts/pairs.py·test_pairs.py, structure/test_storage_fields.py, unit/test_repetition_hold_contract.py와 각 미러, 공식 비용 캐시에 한정한다. 이 파일들의 공유 helper·반례·수리·필요한 검증을 한 담당자가 끝낸다. 현재 실제 runtime 결함은 확인되지 않았으므로 런타임을 임의 변경하지 않는다. 범위 밖 결함이면 입력·정확 기대/실제·파일/심볼과 필요한 후속 쓰기를 보고하고 맡은 범위의 유효한 결과를 남긴다. 제품 계약 자체를 바꾸어 시험을 통과시키지 않는다.

## 종료할 질문

1. `contracts/pairs.py:enumerated_pointers`, `_condition_pairs`, `accepted_condition`을 `planning.EXPOSED_FIELDS`·`RECORD_FAMILIES`·`lifecycle_values`·`validate_condition`과 `StateContract`의 현재 enum에 연결한다. 현재 노출된 enum 필드 모집단, 저장 enum과 lifecycle 후보 차이, 생산자 수용/반려·수신 범위와 역방향 단언을 대조한다. 필수+선택 역방향은 원문 설계 3.3/A20의 의미를 적용하되 enum 값 모집단과 객체 필드 모집단을 혼동하지 않는다. 누락된 실제 필드나 유효 값이 있으면 해당 경로의 작은 단언을 수리한다. 이미 충분하면 근거로 종료하고 새 시험을 억지로 만들지 않는다.
2. `task_contracts.REPEAT_LINEAGES`의 현재 다섯 계보와 `revisions.record_repetition`의 `lineage + '_limit'` 읽기를 `structure/test_storage_fields.py` 및 `unit/test_repetition_hold_contract.py`에 연결한다. 이름이 코드에 존재한다는 사실과 실제 설정값이 hold 발생·해소에 영향을 준다는 사실을 구별한다. 기존 다섯 계보의 임계점·정확 사용자 계속·중복 불변 단언이 이 좁은 소비 질문을 충분히 답하면 재사용한다. 반복·대기 원문 전체를 이번에 종결하지 않는다.
3. `_runner_result_samples`의 두 공급자 × collected/bound/incomplete/stopped 여덟 실제 결과가 `_receive_stored_result`와 `_receive_operator_record`를 통해 무엇을 입증하는지 확인한다. 실제 소비자는 `call_engine`·`scheduler`의 `canonical_json(json_safe(result))`와 `scheduled_operator._json`이다. 기존 값·바이트/hash·결과 의미 단언을 보존하고, 직렬화가 예외 없이 끝났다는 사실만으로 내용 보존을 주장하지 않는다. 실제 저장된 JSON에서 대표 중첩 영수증·bytes 증거·명시 null/부재·공급자 decimal 등의 현행 변환 계약이 확인되는지 대조한다. 빠진 단언이 있으면 기존 실제 결과를 재사용해 보완하고 기대값을 같은 직렬화 함수로 다시 계산하지 않는다. R05/R06의 모든 외부 값/모든 null 필드 조사로 확대하지 않는다.
4. 수용된 r02-fix의 요청 40조합·scholarly args 0/1/여럿·정확 profile_ref/binding·lock 단언을 유지한다. 같은 실제 결과를 확인하기 위해 새 fake runner/adapter/collector나 평행 등록부를 만들지 않는다. 기대값은 현행 계약과 독립 입력에서 얻고 대역은 기존 외부 Job·CLI 경계에 둔다.

## 최소 확인과 제출

먼저 정적으로 답할 수 있는 질문은 정의와 단언의 대응으로 마친다. 시험을 고쳤다면 해당 성질의 최소 반례와 관련 공식 ID/모듈만 실행한다. 기본 도구는 자기 workspace의 `scripts/run_tests.py`, jobs1이다. pairs를 바꾸면 contracts.test_pairs를 인계 범위로 사용하고 다른 두 모듈은 실제 변경/남은 불확실성에 필요한 경우만 추가한다. 충분한 기존 실행을 새 이유 없이 반복하지 않는다. 실행 중 소스를 고정하고 선택·실제 row·exit·판본·한계를 남긴다. 전체 일반/T3/변이/T4/T5, 원격 모델·설치·예약·연구 운전은 배정하지 않는다.

정본 변경 시 공식 build_skill_mirrors.py --target .agents로 미러를 생성하고 --check --target .agents 및 변경 경로를 확인한다. 대응 미러의 바이트 일치로 충분하면 같은 시험을 미러에서 반복하지 않는다. 공식 비용 캐시는 evidence에 보존한 뒤 자기 base로 복원하여 다른 진행 중 수리와 부수적인 캐시 충돌을 피한다. 허용 경로 밖 생성 변경을 제출하지 않는다.

evidence에는 모집단·실제 정의/소비자·정확 시험 ID/단언·기존 증거·판정을 필요한 만큼 연결한다. 판정은 기존 성질 유지/한정 수리 완료/정확 미결/최종 판본 대기를 구별한다. 공용소스·engine·context/plan/seams/queue/state·원자료·다른 task·Git index를 수정하지 않고 graphify를 갱신하지 않는다. 보고 형식은 async protocol을 따르며 실제 변경 전부를 changes에 쓴다. `python C:/math/services/async-development/check.py report C:/math/.async/dm r04`로 제출을 확인한다. 전체 G4~G8, L01과 symlink 미검사는 그대로 남긴다.
