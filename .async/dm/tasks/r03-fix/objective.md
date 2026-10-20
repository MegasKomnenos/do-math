# 목적과 완료할 결과

r03이 남긴 F2를 해결한다. 관찰 tracker가 현재 생산·저장하는 기록과 수신 스키마가 같은 현행 계약을 갖게 하고, 생산자 없는 수신 필드를 일반 계약 시험이 놓치지 않게 만든다. r03의 신뢰 요청·전체 record 순방향·저장/restart 수리는 수용됐지만 설계 3.3/A20의 관찰 전체 필드 역방향은 미충족이다. 스키마 정리와 실제 생산 표본의 계약쌍 등록, 관련 반례·미러·최소 검증을 이 task에서 마무리한다.

## 입력과 쓰기 범위

SESSION_JSON의 workspace, inputs/context.md·plan.md·seams.md, task.json이 배정 정본이다. 선행은 r03이다. C:/math/.async/dm/tasks/r03/report.json·evidence/{review.md,observation-field-map.json,verification.json,original-basis.json} 및 managers/0010/review.md·source-review.json은 읽기 전용 수용 근거다. 공용 소스가 아니라 자기 workspace의 수용판을 수정한다. 진행 중 r10/r14의 중간 파일이나 종료를 기다리지 않는다.

원문은 C:/math/docs/do-math/시험-재편-2026-09-29/설계.md의 3.3/A20와 같은 폴더의 조사/결함-범주.md, C:/math/docs/do-math/continuous-development-2026-10-13/sources/{user-decisions.md,requirements-index.json}, phases/001/tasks/closure-map/evidence의 R03·1-A·PR18·C-03 해당 부분이다. 현재 do-math/AGENTS.md의 현행 계약 하나·구판 호환 금지 원칙을 따른다. 과거 저장 자료를 위한 자동 보충/변환은 요구가 아니다. 과거 run:은 위 continuous-development 실행 루트다.

task.json의 writes는 record_schemas/schemas.py와 필요시 같은 계약 소비자 __init__.py, 기존 contracts/pairs.py·test_pairs.py, 관찰 tracker/직접 record 저장 시험·observation_inputs helper·public record storage, 관련 이음새 설명과 미러·공식 비용 캐시다. 모든 허용 파일을 바꿔야 한다는 뜻은 아니다. observations.py·core_engine.py·review_engine.py·공급자 입구와 parallel/scheduler 및 r10/r14 helper는 읽기 전용이다. 이 문제를 해결하려고 옛 producer 필드나 별칭을 새로 만들지 않는다. 새 발견에 범위 밖 생산자 수정이 꼭 필요하면 정확 입력·기대/실제·심볼·필요 쓰기를 남기고 범위 안 결과를 마친다.

## 해결할 질문과 구현 조건

1. r03의 필드 대응을 현행 정의·생산·실제 저장 경로에서 확인한다. 보고된 미생산 선택 필드는 observation_facts의 event/elapsed_ms, self_check_obligations의 opened_at, self_check_responses의 response/reason, observations metadata row의 active_revision/active_rules_sha256/checkpoint_status/evidence_refs/obligation_ids/previous_rules_sha256/proposal_sha256/review_window_ms/rule_revision/rules/trigger다. obligation status=closed도 현행 생산자가 없다. 현재 사용자 기능에 필요한 생산 필드를 누락한 문제인지, 불필요한 허용 필드 잔존인지 구별한다. 확인한 현행 경로에는 후자이므로 필요 없는 필드와 closed를 제거하는 방향으로 계약을 단순화한다. 원문 의미를 바꾸는 근거 없는 필수화·enum 축소를 더하지 않는다.
2. observation_facts는 현재 fact가 내는 event_json/event_sha256/monotonic_offset_ms를 필수로 받는 한 형태가 되어야 한다. event를 허용하는 옛 oneOf 분기만 지우다가 실제 필수 세 필드를 선택으로 풀지 않는다. JSON 파싱·SHA 일치와 source의 현재 좌표/시각 검사는 보존한다. response_json/errors, obligation의 offset·delivery/ack·hold/response_ref, 실제 response 내부 rule_update의 rules/digest/revision/feedback 등 현행 계약은 유지한다. 다른 가족의 같은 이름은 삭제 근거가 아니다. runtime.observations는 map의 각 row라는 수신 단위를 유지한다.
3. 기존 PAIRS/일반 시험에 네 가족의 실제 전체 record를 연결한다. r03의 support.observation_inputs.tracker_record_samples와 기존 actual owner fixture를 재사용하고, 현재 수신 schema의 필수+선택 top-level 필드를 정확히 소비한다. metadata map은 실제 row 속성으로 대응한다. 모든 실제 필드마다 생산 분기가 있도록 빠진 표본/관찰값을 보완하며 core_engine만 더하는 observation_refs 등은 실제 owner 출구에서 얻는다. 생산·수신을 둘 다 가리는 fake, fields=None/부분집합 면제, 저장값에 사후 schema 키 보충, 필드명 정적 출현을 실제 표본으로 간주하는 방법은 쓰지 않는다. rule_ids 조각 pair는 기존 의미대로 유지하거나 전체 pair와 역할을 분명히 하되 해당 Unicode/입력 보존 단언은 잃지 않는다. 이 좁은 계약 때문에 모든 관찰 상태/시간/진행성을 전수 재작성하지 않는다.
4. 현재 생산 record가 실제 검사·저장에 통과하는 정상 대조와, 제거한 필드 또는 closed를 추가했을 때 같은 정본 검사에서 거부되는 작은 반례를 묶는다. generic 역방향이 새 미생산 허용 필드를 발견한다는 성질도 기존 방식의 최소 반례로 확인한다. 현행 fact JSON/SHA/offset 필수 누락과 내용 변조 반려를 보존한다. C-03의 boundary/rule_update/answered·execution stopping·재시작과 control_call_ids 부재, r02-fix/r04/r03의 요청·결과·신뢰 단언을 보존한다. 계약 변경 때문에 obsolete fixture가 있으면 현행 실제 생산으로 고치며 제품 호환 분기를 추가하지 않는다.
5. 필요한 설명은 같은 계약 변경 안에서 정리한다. 상세 필드 정의는 schemas.py에 두고 중복 schema나 새 평행 등록부를 만들지 않는다. 관련 정본 이음새 문서에 실제 의미 변경을 설명할 필요가 있을 때만 해당 부분을 바꾼다. r03 원보고/과거 증거는 수정하지 않고 후속 처분으로 연결한다. PR18/C-03도 실제 확인한 성질만 판단한다.

## 최소 확인과 제출

정적 확인으로 충분한 생산/소비 범위는 그것으로 마친다. 수정한 계약쌍은 자기 workspace의 공식 scripts/run_tests.py contracts.test_pairs --jobs 1을 인계 범위로 삼고, 추가로 바꾼 저장 계약의 실제 producer/checker와 C-03·반려를 확인하는 가장 작은 관련 ID만 실행한다. 기존 단언이 이미 충분하면 중복 시험을 만들지 않는다. 전체 일반/fresh T3/변이/T4/T5, 실모델·설치·실Lean·예약·연구 운전은 이 배정에 없다. 실행 중 소스를 고정하고 선택/실제 row·exit·판본·한계를 보존한다. task별 jobs1이다.

공식 build_skill_mirrors.py --target .agents로 대응 미러를 생성하고 --check --target .agents로 확인한다. 바이트가 같으면 같은 시험을 미러에서 반복하지 않는다. 공식 비용 캐시 두 개는 evidence에 보존한 뒤 자기 base로 복원한다. 두 진행 중 task와 캐시 충돌을 만들지 않는다.

evidence에는 제거/유지 필드와 이유, 실제 생산 심볼/분기·정본 수신·정확 시험 ID/단언, 범위와 미결을 연결한다. 기존 성질 유지·F2 수리·최종 판본 대기를 구별하며 전체 PR/K/P2·R06·G4~G8·L01·Windows1314를 종결하지 않는다. 공용 context/plan/seams/queue/state·다른 task·base/inputs·engine·Git index·graphify는 수정하지 않는다. 실제 변경을 report.json에 적고 python C:/math/services/async-development/check.py report C:/math/.async/dm r03-fix로 제출 형식을 확인한다.
