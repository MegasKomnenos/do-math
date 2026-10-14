# 목적과 완료할 결과

R05/1-C의 네 외부 값 경계에서 수용한 값이 저장·해시·JSON 직렬화까지 계약대로 전달되는지 판단하고, 확인된 시험 공백을 같은 task에서 수리한다. 대상은 공급자 사건, 사용자 학술 요구 ID, 러너 영수증, 모델 확장 필드다. 이 경계에서 실제 생산되는 명시 null과 소비도 함께 확인하되, 제품 전체 null 필드의 R06 모집단을 이번 결과로 종결하지 않는다. 이미 충분한 정의·단언·원보고는 재사용한다.

## 입력과 수정 범위

SESSION_JSON의 workspace, 고정 inputs/context.md·plan.md·seams.md, task.json을 기준으로 한다. 스킬 상대 경로는 자기 workspace다. 원문은 C:/math/docs/do-math/continuous-development-2026-10-13/sources/user-decisions.md·requirements-index.json, phases/001/tasks/closure-map/evidence/requirement-state.json의 1-C와 tracking-state.json의 R05/R06다. 같은 evidence의 native_input_integration·lean_value_integration·storage_detail_integration 및 prior-review-state의 PR06/PR15 중 실제 경계에 연결되는 부분을 읽는다. 원 요구와 과거 판정, 현재 정의를 구별하고 관련 K/P2만 연결한다. 과거 run:은 위 continuous-development 루트, repo:docs/...는 C:/math의 읽기 전용 원자료다.

수용된 r02-fix의 요청/결과 시험과 r07-fix의 output_contract 수리는 시작 사본에 있다. r04는 같은 시점에 별도 사본에서 조건 enum·한도 소비·기존 결과8표본의 JSON 내용 단언을 맡는다. r04 결과는 이 작업의 선행이 아니다. 현재 pairs와 provider_runs는 읽기만 하고 그 수정이나 재구현을 하지 않는다. 이 task는 외부 값의 입력축과 실제 생산·소비 의미를 맡으며 기존 결과8표본을 다시 만드는 작업을 하지 않는다.

제품 writes는 flows/test_provider_native_storage.py·test_provider_observation_ingress.py, unit/test_storage_repository.py, 필요할 때 새 unit/test_external_value_boundaries.py, support/provider_native_inputs.py 및 대응 미러다. 새 파일은 기존 파일에서 충분히 표현하기 어려울 때만 쓴다. runtime은 읽기 전용이다. 실제 runtime 결함이 확인되면 최소 입력·기대/실제·파일/심볼·필요한 후속 쓰기를 보고하고 허용 범위의 유효한 결과를 마친다. 정상 기대값이나 제품 계약을 바꿔 결함을 숨기지 않는다.

## 종료할 질문

1. 각 경계의 실제 입력 수신자, 생산자, 저장/해시/직렬화 소비자와 기존 정확 단언을 연결한다. 대표 진입점은 ModelRunner/두 worker와 collector, ObservationTracker 및 owner의 _observe_running, repository.validate_storage_value·canonical_json, payloads.json_safe, values.compact_json_bytes/json_digest다. 사용자 학술 요구 ID와 모델 확장 필드는 현재 수신·생산 정의를 따라 확정한다. scholarly 서버 command/args 설정을 사용자 학술 요구 ID로 대신하지 않는다.
2. 각 경계에 실수, 2**53 경계와 초과 정수, bytes, 비ASCII·공백 문자열, 명시 null, 빈 list/dict를 대응시킨다. 실제 경계가 수용·명시 반려·계약상 변환하는 경우를 구별한다. JSON stream이 직접 받지 않는 bytes를 억지로 JSON에 넣거나, 저장이 금지한 float를 원값으로 저장하도록 계약을 바꾸지 않는다. 실제 raw bytes 증거, 문자열 JSON, 안전한 저장 투영값의 서로 다른 책임을 설명한다. 각 조합의 충분한 기존 근거를 재사용하고 빠진 축에만 최소 실제 경로 단언을 보완한다.
3. 반환값의 내용·바이트/해시·부재와 명시 null을 확인한다. 예외가 없다는 사실만으로 의미 보존을 주장하지 않으며 기대값을 검사 대상 직렬화 함수로 다시 계산하지 않는다. 저장 반려는 정확 사유와 상태 불변을 확인한다. 명시 null은 실제 생산자 또는 현행 수신 계약이 허용한다는 근거가 있을 때 소비에 넣는다. observations의 deadline_only 거부는 현재 followup을 생략한다. 과거 followup=None을 도달 가능한 결함으로 다시 주장하려면 현재 생산 근거가 필요하다.
4. R05 네 가족의 판정과 이번에 다룬 R06 null slice를 구분한다. 모집단 밖 null 필드나 다른 요청·저장 가족, PR06/PR15 및 K/P2 전체의 완료를 주장하지 않는다. 확인하지 못한 경계는 정확한 남은 질문으로 남긴다. 기존 공급자 숫자·원문 offset·정상 후속·중복 불변과 StateContract 검증을 유지한다.

## 필요한 확인과 제출

정적 대조로 충분한 질문은 거기서 끝낸다. 변경하면 그 성질의 최소 입력/공식 ID만 실행하고 실제로 손댄 모듈의 필요한 회귀로 인계한다. 자기 workspace의 scripts/run_tests.py, jobs1을 사용한다. 내부 runner/adapter/collector/repository를 대역으로 바꾸지 않고 기존 외부 Job·CLI/Git 포트 대역을 재사용한다. 새 실제 모델·Job·Lean·예약·네트워크와 전체 일반/T3/변이/T4/T5 실행은 배정하지 않는다.

실행 중 소스를 고정하고 선택 ID·실제 row·exit·판본·실패와 한계를 보존한다. 변경 정본과 미러는 공식 build_skill_mirrors.py --target .agents로 함께 생성하고 --check --target .agents를 확인한다. 미러 byte 일치로 충분하면 시험을 반복하지 않는다. 비용 캐시 두 개는 실행 후 evidence에 보존하고 자기 base로 복원한다. 공용소스·공용 문서/queue/state·engine·다른 task·과거 원자료·Git index를 수정하지 않으며 graphify를 갱신하지 않는다.

자기 evidence에 경계별 입력축·실제 정의/소비·단언·판정을 필요한 만큼 남기고 async report.json으로 제출한다. 기존 성질 유지/수리 완료/미결/최종 판본 대기를 구별한다. python C:/math/services/async-development/check.py report C:/math/.async/dm r05의 PASS를 확인한다. G4~G8, L01 Q1/Q2·UTF-8 byte, Windows1314 symlink 미검사 등 기존 남김은 유지한다.
