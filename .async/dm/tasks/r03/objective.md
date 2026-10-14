# 목적과 완료할 결과

R03/1-A의 신뢰 등록 요청과 관찰 기록 두 가족을 실제 생산자에서 수신 검사까지 연결해 판단하고, 빠진 시험 연결은 이 작업에서 수리한다. 사용자 목표는 생산자가 내는 값이 현행 수신·저장 계약과 어긋나도 시험이 통과하는 공백을 막는 것이다. 기존에 충분한 단언·원보고는 유지하고 확인된 공백만 보완한다. 합성 identity/baseline을 받아 등록 helper가 통과하는 사실과 setup_lean의 실제 조립 분기가 통과하는 사실, rule_ids 조각 수신과 tracker 전체 record 수신을 구별한다.

## 입력·쓰기 경계

SESSION_JSON의 workspace와 고정 inputs/context.md·plan.md·seams.md, task.json이 현재 배정이다. r04만 선행이다. 같은 pairs.py·test_pairs.py를 수정할 수 있으므로 수용된 r02-fix의 요청40입력/args/lock과 r04의 실제8결과·JSON16 내용 단언을 보존한다. C:/math/.async/dm/tasks/r04/report.json·evidence, managers/0007/review.md·source-review.json은 읽기 전용 수용 근거다. 진행 중 r05·r11의 중간 파일이나 완료를 기다리지 않는다.

원문은 C:/math/docs/do-math/continuous-development-2026-10-13/sources/user-decisions.md·requirements-index.json과 같은 실행의 phases/001/tasks/closure-map/evidence/{tracking-state,requirement-state,prior-review-state,evidence-catalog}.json이다. tracking R03, requirement 1-A, current_work.trust_record_basis_integration 및 PR08/B76·PR18의 이 질문에 해당하는 부분을 읽는다. 관찰 tracker의 실제 생산/복원에는 원래 P2 C-03의 해당 반례도 연결한다. run:은 위 continuous-development 실행 루트, 과거 repo:docs/...는 C:/math의 원자료다. 과거 source 좌표·함수명은 현행 정의에 대응하고 오래된 API를 복원하지 않는다.

쓰기 범위는 task.json의 계약 pairs, toolchain/신뢰/관찰 직접 시험과 support/trust_inputs.py·observation_inputs.py, 대응 미러와 공식 비용 캐시다. 제품 runtime·공용소스·다른 task·engine·Git index는 수정하지 않는다. 범위 밖 runtime 결함을 발견하면 정확 입력·기대/실제·파일/심볼·필요 쓰기를 보고하고 범위 안 유효한 결과를 마친다. 범위 안 시험 수리와 필요한 최소 확인을 별도 task로 미루지 않는다.

## 종료할 질문

1. `_trust_request_samples`/`_receive_trust_request`/`_trust_request_fields`를 `setup_lean.record_installation`·`rerecord`·`write_trust_request`, `trust_inventory.registration_request`·record/binding 검사와 `trust_validation.register_request_errors`/`environment_errors`의 현행 역할에 연결한다. setup의 core/project, 새 기록·동일 기록 재사용·재기록 등 현재 실제 유효 생산 분기와 선택 필드/목록 축을 정리하고, 기존 직접 시험이 어느 분기를 실제로 거치는지 확인한다. 저장 record·등록 요청·채택된 환경·runtime binding은 서로 다른 객체이므로 각 실제 소비자가 받는 값을 구별한다. 모든 분기를 거친다고 주장하려고 불가능한 조합이나 의미 없는 동일 표본을 추가하지 않는다.
2. 수신 검사의 필수+선택 필드 역방향은 원문 설계 3.3/A20의 의미를 따른다. 현재 소비자가 아는 필드가 어느 실제 생산 분기에서 나오는지 확인한다. 순방향은 해당 생산값을 실제 수신 검사에 보낸 단언으로, 역방향은 정확 필드/분기 대응으로 뒷받침한다. setup 생산 증거가 부족하면 기존 외부 Job/Lean 대역과 작은 임시 toolchain을 사용해 실제 setup 출력·게시 요청을 연결한다. 검증된 것으로 보이게 validation/build_kind 등을 사후 보충하거나 실제 setup을 새 fake로 가리지 않는다. 정상 대조와 해당 실패/정지의 반려 의미는 기존 단언을 유지한다. 대형 설치 비용·실Lean 인증을 이 질문의 선행으로 요구하지 않는다.
3. `observations.ObservationTracker`의 실제 관찰·self-check 응답·의무 record 생산과 저장용 반환, `StateContract`/`validate_record`, 기존 저장/복원 시험을 연결한다. `accepted_rule_ids`/`receive_stored_rule_ids`가 입증하는 rule_ids 성질과 전체 record 생산 성질을 구별한다. 현재 유효 생산 분기, 선택 필드 있음/없음과 관계 0·1·여럿 중 이 record 계약에 실제로 존재하는 축, 필수+선택 역방향을 대조한다. 원래 C-03의 open→boundary→rule proposal→close→저장/복원과 폐기된 control_call_ids 사본 부재를 현행 단언에 연결한다. 전체 관찰 기계/시간/진행성 재검토로 확대하지 않는다.
4. 원문 요구에 충분한 기존 성질은 정확 단언과 판본 근거로 유지한다. 공백이면 기존 pair/fixture/검사기를 재사용해 해당 입력·단언을 수리한다. 기대값은 독립 입력·명시 계약에서 얻는다. 생산/수신을 같이 가리는 mock, schema 필드명을 단순 검색한 것을 실제 생산 증거로 쓰는 방식, 같은 serializer로 expected를 재계산하는 방식은 피한다. 원보고 부재는 그 범위의 미확인으로 남기고 과거 counts를 현재 통과로 합산하지 않는다. PR08/PR18·K/P2 전체가 아니라 실제 연결한 부분만 판정한다.

## 필요한 확인과 제출

정적으로 충분한 질문은 정의·소비자·단언 대조로 마친다. 수리한 경우 해당 성질의 최소 반례와 관련 공식 ID만 실행한다. pairs를 바꾸면 contracts.test_pairs를 인계 범위로 사용하며, 다른 허용 시험은 실제 변경과 남은 불확실성에 필요한 최소 ID/모듈을 고른다. 공식 도구는 자기 workspace의 scripts/run_tests.py, jobs1이다. 실행 중 소스를 고정하고 선택·실제 row·exit·판본·한계를 보존한다. 전체 일반/fresh T3/변이/T4/T5·원격모델·도구 설치·실Lean·예약·연구 운전은 배정하지 않는다.

정본 변경은 공식 build_skill_mirrors.py --target .agents로 생성하고 --check --target .agents 및 실제 변경 경로를 확인한다. 미러가 바이트 일치하면 동일 시험을 미러에서 반복하지 않는다. 공식 비용 캐시는 evidence에 보존한 뒤 자기 base로 복원해 r05/r11과 부수적인 통합 충돌을 피한다.

evidence는 현재 생산 분기·소비자/검사기·필드/입력축·정확 시험ID/단언·기존 원보고·판정을 다음 작업자가 따라갈 만큼 연결한다. 기존 성질 유지/한정 수리 완료/정확 미결/최종 판본 대기를 구분한다. 새 평행 등록부나 전수 감사 체계는 만들지 않는다. 공용 context/plan/seams/queue/state·base/inputs·원자료·다른 task를 수정하지 않고 graphify를 갱신하지 않는다. async report 형식에 실제 변경을 모두 적고 `python C:/math/services/async-development/check.py report C:/math/.async/dm r03`으로 제출을 확인한다. 다른1-A 가족·R06 전체 null·G4~G8·L01·Windows1314 symlink 미검사는 남긴다.
