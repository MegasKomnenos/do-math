# 설정·실행 프로필·자원 예약의 실제 저장 계약

사용자가 사용하는 실행 설정, 채택된 프로필/자원 한도와 실제 예약이 생산 단계부터 저장 검증·재적재까지 일치하게 한다. R01/1-A·1-B와 K-78의 남은 저장 가족 중 같은 profile/입장 생산자를 공유하는 아래 여섯 가족을 한 작업에서 판정하고, 확인한 공백의 필요한 구현·직접시험·최소 확인·미러를 함께 마친다.

- research: `config`, `capacity_constraints`, `execution_profiles`, `host_capacity_ref`, `role_profile_refs`
- runtime: `reservations`

SESSION_JSON/task.json, inputs/context.md·plan.md·seams.md와 do-math AGENTS.md·시험-지침.md를 읽는다. 원요구는 C:/math/docs/do-math/continuous-development-2026-10-13의 sources/user-decisions.md·model-policy-2026-10-14.md·document-batching-2026-10-14.md·requirements-index.json 및 phases/001/tasks/closure-map/evidence/requirement-state.json의 1-A/1-B/K-78, tracking-state.json의 R01/KEEP-STORAGE다. 조사/대역-사각지대.md·설계.md·단계-전환표-2026-10-03.json은 C:/math/docs/do-math/시험-재편-2026-09-29 아래의 원자료다. 옛 API나 저장 대역을 복원하는 배정이 아니다.

직접 선행은 수용된 keep-storage다. 그 report/evidence/families.json과 judgment.md, r22-storage/evidence/family-judgment.json의 해당 여섯 행을 현재 정의로 확인한다. r21-r22의 37프로필 저장과 r34-r36의 profile1665/필수입력 차분, r15-r16의 정산 근거 중 이번 성질에 실제 필요한 부분만 재사용한다. 표의 group 명칭은 탐색용이며 reservations가 task-execution에 속한다는 이유로 profile/입장 생산자와 따로 나누지 않는다. 진행 중 storage-knowledge/keep-contracts/keep-proof의 미수용 결과는 소비하지 않는다.

## 결과와 완료 판단

1. `execution_profiles.build_profiles/apply_editions/host_constraint/with_host_resources`, `configuration`의 실제 설정 생산·검사, `governance_engine`의 configure 채택, `SessionSlots._admission/acquire` 및 `budget.plan_reservations`의 작성 경로를 실제 `default_state_contract().family(root,family)`와 저장 검사에 연결한다. 기존 unit/test_producer_record_storage.py의 host/profile/reservation/configure 시험 및 관련 sim/unit 시험은 충분한 성질을 먼저 재사용한다. 필드 이름이 소스에 나타난다는 구조 검사만으로 모든 필드가 생산됐다고 판정하지 않는다.
2. 가족별 현행 형상(map/singleton/metadata), 필수·선택 필드와 실제 생산 분기를 대조한다. 생산자가 쓰는 필드는 수신 계약이 받아야 하고 수신 계약의 필수·선택 필드는 실제 생산자에 연결돼야 한다. 설정 입력은 사용자가 제공하는 값이며 저장 출력은 실제 초기화/configure 생산자 결과여야 한다. 손으로 완성한 출력 record나 expected와 actual을 같은 serializer로 다시 만든 비교는 피한다. 스칼라 참조와 역할별 profile-ref 목록에 record 객체의 키 검사 방식을 강제하지 않는다.
3. 현재 지원하는 공급자·설정 불리언의 값, AI/기계 역할의 실제 분기, host 제약 있음/없음, 유효한 다중도 0/1/여럿, 선택 필드 있음/없음을 해당 생산자 계약에 맞게 판정한다. 불가능한 조합은 실제 guard와 이유로 제외하며 모든 축의 무조건적인 Cartesian product나 가상 기능을 추가하지 않는다. 기존 유효 profile/권한/실행 builder를 사용하고 출력에 필드를 사후 보충하지 않는다.
4. 생산한 값이 실제 StateContract/ResearchRepository 검증을 통과하고 저장·재적재에서 독립 입력의 의미를 보존하는지 필요한 최소 표본으로 확인한다. profile 판본과 SHA, 채택 선택과 옛 실행의 고정 판본, host authority/ref·scope·한도, 실제 acquire의 예약 owner/unit/amount/status를 구별한다. 반려는 실제 실패 필드·참조·사유에 결박하고 이미 있는 권한/정산 반려를 반복 복제하지 않는다. 저장 대역에 검사 우회나 실제 프로필/예약 생산자의 대역을 넣지 않는다.
5. 현재 시험의 충분한 근거, 새로 보완한 공백, 실제 runtime 결함, 정당한 비생산/제거 후보를 구별한다. 미생산 선택 필드가 있으면 먼저 현행 다른 생산자와 소비 목적을 확인한다. 표본이 없다는 이유만으로 계약을 삭제하거나 옛 값을 기본 보충하지 않는다. 1-B의 모든 쓰기지점 도달은 최종 fresh T3에 연결할 정확한 위치/시험으로 남긴다. 이번 작은 실행을 모든 분기의 최종 측정으로 주장하지 않는다.

여섯 가족 각각에 제공/소비 심볼·필드/입력축·정확 단언·원보고/판본·직접 확인한 방법·충족 또는 구체적 남김을 남긴다. 기존6+나머지 가족의 수를 전체 완료율로 쓰지 않는다. 새로운 대형 registry나 감사 프레임워크를 만드는 것이 목표가 아니다. 필요하면 `support/storage_profile_pairs.py`와 자동 수집되는 `contracts/test_storage_profile_pairs.py`에 실제 producer samples/receiver를 모은다. 기존 `contracts.pairs.Pair`의 의미를 재사용할 수 있지만 모든 형상에 Pair를 강제하지 않는다. 다른 task 소유의 일반 PAIRS 파일을 수정하지 않아도 독립 계약시험으로 수집되게 한다.

## 소유 범위와 확인

제품 수정은 task.json의 profile/configuration/budget/session_slots/configure 제공자, 전용 helper/계약시험과 해당 직접시험·미러에 한한다. 공용 `record_schemas/__init__.py`, `record_schemas/schemas.py`, `state_contract.py`, `contracts/pairs.py`, `contracts/test_pairs.py`, `test_producer_record_storage.py`, `storage_records.py`, 지식/신뢰/review helper는 storage-knowledge 소유이므로 읽기 전용이다. role_answers/observation_inputs/시험 규칙·지침은 keep-contracts 소유다. 이들은 시작판에서 그대로 소비한다. 중앙 schema 등 범위 밖의 실제 수정이 필요하면 정확한 반례·원인·필요 경로를 보고하고 유효한 나머지 작업을 완료한다. 우회 schema/예외로 숨기지 않는다. 문서의 인터페이스 설명은 report로 인계한다.

정적 확인으로 충분한 성질은 새로 실행하지 않는다. 실행이 필요하면 자기 workspace의 공식 run_tests.py --jobs 1로 실제 불확실성을 푸는 가장 작은 선택을 쓴다. 동시에 시험할 수 있는 task는 keep-contracts/storage-knowledge/이 task의 최대3개다. 실 Lean/유료 공급자/HTTP/실 OS 예약·설치 변경·전체 일반/T3/변이/T4/T5는 실행하지 않는다. 실제 Repository/검사와 외부 Git/Job/host 대역의 근거 범위를 구별한다.

초기 실패·fixture 오류·선택/고유 실제 row·exit·source SHA·실행 중 변경과 소프트 비용을 보존한다. 별도 판본 성공을 단일 최종판 성공으로 합산하지 않고 충분한 기존 시험을 반복하지 않는다. 비용캐시는 관측 근거를 evidence에 보존한 뒤 own base로 복원한다. 공식 미러 생성/check와 check.py report C:/math/.async/dm storage-profiles를 마치고 report.json을 제출한다. 공용 소스/문서/queue/state·서비스 engine·Git index·graphify·기존 연구 운전은 수정하지 않는다.
