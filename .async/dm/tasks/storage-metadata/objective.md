# 초기화 신원과 메타데이터의 실제 저장 계약을 확인·보완한다

사용자 목표는 실제 생산값과 저장 수신 계약의 어긋남이 시험을 빠져나가지 않는 것이다. 같은 초기화·저장 인코더를 쓰는 research.id/object_format/title/workspace/created_at 다섯 가족을 한 task에서 마친다. 중앙 schema와 권한·실행 공급자 수정 없이 독립 진행 가능한 묶음이다. 작은 필드마다 task를 나누지 않는다.

SESSION_JSON, task.json, inputs/context.md·plan.md·seams.md와 do-math AGENTS.md·시험-지침.md를 읽는다. 원문은 C:/math/docs/do-math/continuous-development-2026-10-13/sources/user-decisions.md·requirements-index.json·model-policy-2026-10-14.md·document-batching-2026-10-14.md, phases/001/tasks/closure-map/evidence/requirement-state.json의 R01/1-A·1-B/K-78과 C:/math/docs/do-math/시험-재편-2026-09-29/설계.md 3.3/A20이다. 직접 입력은 C:/math/.async/dm/tasks/keep-storage/report.json·evidence/families.json·judgment.md, tasks/storage-profiles/report.json·evidence/judgment.md, managers/0048/review.md다. C:/math의 원자료는 읽기 전용이다.

keep-storage가 남긴 다섯 가족의 판정을 실제로 소비하므로 그것만 선행이다. storage-authority/execution-fields의 종료를 기다리거나 미수용 workspace를 읽지 않는다. 같은 scalar-metadata 그룹으로 묶였어도 capability_evidence는 map이고 이번 다섯 가족이 아니다. goal_status/conversation_loss_policy, runtime 상태·시각·pause 등 나머지 가족도 별도 남김이다.

## 확인할 실제 의미

1. initialization.initialize_state의 instance_id/title/workspace/created_at 생산과 ResearchRepository._save의 object_format 설정·Git 형식 불일치 반려를 읽는다. StateContract의 metadata 등록, _encode_families/_decode_families의 root metadata 파일과 /value 단위 검사를 실제 정의로 연결한다. scalar에는 required/optional 객체 key가 없다는 면제와 실제 값/내용의 검사는 구별한다. 빈 fields==빈 written으로 충족 판정하지 않는다.
2. tests/unit/test_record_family_storage.py의 test_scalar_metadata_is_one_closed_record_per_root는 수동 current_state와 파일 개수/SHA를 확인한다. 그것이 실제 초기화 생산값의 다섯 의미를 이미 검사하는지 읽고, 부족한 단언만 기존 직접시험에 보완한다. 기존 초기화/공개 profile_cases 등 충분한 저장 근거가 있으면 정확 ID·판본과 현재 소스를 연결해 재사용한다. 시험 수를 늘리거나 새 범용 metadata registry/helper를 만들 필요는 없다. helper는 소비자가 하나면 해당 시험 모듈에 둔다.
3. 실제 유효 초기화 입력으로 명시 title와 빈 title의 goal[:80] 선택, exact Unicode/개행 내용, workspace 문자열, 주입 clock과 명시 created_at의 현재 시각 정규화, 실제 instance ID를 각각 독립 입력 기대값에 연결한다. 임의 새 형식 규칙이나 경로 정규화 정책을 만들지 않는다. object_format은 실제 sha1/sha256 저장소가 생산한 값으로 확인하고 저장 형식 불일치가 게시 전에 거절되는 현재 성질을 유지한다. 이미 충분한 기존 양측 검사를 이유 없이 다시 실행하지 않는다.
4. 실제 initialize_state 출력→검증된 Repository initialize/save→별도 Repository load로 다섯 값을 확인한다. metadata를 별도 레코드마다 전체 state 복제로 만들지 않고, root metadata의 현재 포장과 원값 보존·정확 반려·옛 head 불변을 연결한다. 형식 반려를 확인할 경우 정확 대상/원인과 정상 대조를 둔다. 저장 형식/instance identity를 고의로 손상시키는 반례와 정상 producer를 구별한다. 비검증 _save 대역이나 사후 필드 보충을 성공 근거로 쓰지 않는다.
5. 자기 writes의 초기화·저장 codec/검사와 직접시험에서 실제 결함을 발견하면 관련 수리·확인을 함께 마친다. 중앙 record_schemas, governance, core/call/session의 실행 제공자, 공용 storage_records와 producer시험·이음새-정본.md는 다른 작업의 경계라 읽기 전용이다. 현재 확인된 다섯 정의는 scalar이며 새 schema 변경 필요가 확인된 것은 아니다. 범위 밖 실제 결함이면 정확 반례와 필요한 파일을 보고하고 독립 가능한 결과를 마친다. 가상 결함을 위해 범위를 넓히지 않는다.

## 검증과 인계

정적 분석과 정확 기존 근거가 충분하면 실행하지 않는다. 새 수리의 불확실성만 workspace 공식 run_tests.py --jobs 1의 작은 관련 ID로 확인한다. 현재 storage-authority와 이 task는 두 슬롯이며 이후 execution-fields와 병행해도 두 슬롯이다. 전체 일반/fresh T3/변이/T4/T5·유료 모델/HTTP/실 Lean/native Job/OS 예약/설치·대형 비용 실행은 하지 않는다. 실제 Repository/StateContract와 Git/clock/host 포트 대역을 구별한다.

다섯 가족 각각의 현재 shape·실제 producer/receiver·입력축·정확 값/반려 단언·기존 근거/새 보완·충족 또는 구체적 남김을 report/evidence로 전달한다. 원자료의 이름 검색 후보를 실제 root field 생산으로 오인하지 않는다. 쓰기 심볼·SHA·시험 ID는 최종 fresh T3 연결 입력으로 남기며 모든 쓰기분기 도달 완료로 확대하지 않는다. 다른 가족·전체 R01/K-78·G4~G8·L01/Windows1314·최종 review는 닫지 않는다.

초기 실패/fixture 오류·선택/실제 row·관측 exit·source SHA·실행중 변경·소프트초과를 보존하고 서로 다른 판본 통과를 합산하지 않는다. 비용캐시 관측을 evidence에 보존한 뒤 own base로 복원하고 공식 build_skill_mirrors.py 생성/check를 수행한다. check.py report C:/math/.async/dm storage-metadata로 보고를 검사한다. 공용 source/context/plan/seams/queue/state, 다른 task, engine, Git index, graphify와 기존 연구 운전은 수정하지 않는다.
