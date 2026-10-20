# 목적과 완료할 결과

R10/2-A의 관찰·공급자 입구가 잘못된 입력을 계약대로 처리하고, 같은 항목을 중복 적용하지 않으며, 뒤의 정상 입력을 실제 owner/store까지 진행시키는지 판단한다. 충분한 현재 정의·단언·원보고는 유지하고 확인된 시험 공백이나 실제 수신 결함만 같은 task에서 수리한다. 반려 종류마다 별도 task를 만들거나 기존 모집단을 무조건 재실행하지 않는다.

## 입력과 범위

SESSION_JSON의 workspace, 고정 inputs/context.md·plan.md·seams.md, task.json이 기준이다. 스킬 상대 경로는 자기 workspace다. 원문은 C:/math/docs/do-math/continuous-development-2026-10-13/sources/user-decisions.md·requirements-index.json과 phases/001/tasks/closure-map/evidence의 requirement-state.json[2-A], tracking-state.json[R10], prior-review-state.json[PR15], evidence-catalog.json[current_work.provider_population_integration]다. 원 문서의 과거 run:은 이 continuous-development 루트, repo:docs/...는 C:/math의 읽기 전용 자료다. 현재 없는 과거 Temp 원보고는 수치만으로 통과 근거로 쓰지 않는다.

수용된 r05의 네 값 경계 수리와 null slice가 시작판에 있다. r05 report·boundary-map·verification 및 managers/0009/review.md·source-review.json으로 직접 실행한 범위와 정적으로 연결한 범위를 구별한다. r05의 EXTERNAL_JSON_VALUES, 숫자/bytes/offset/해시·StateContract 단언과 deadline_only followup 부재를 보존한다. r03은 pairs 및 신뢰/관찰 record의 생산·수신, r14는 scheduler/parallel 진행성과 기계 완료를 별도 사본에서 처리한다. 그 중간 결과를 읽어 전제로 삼거나 두 배정을 수정하지 않는다.

수정 가능한 시험은 flows/test_provider_raw_ingress.py·test_provider_observation_ingress.py·test_provider_native_inputs.py·test_provider_native_storage.py와 support/provider_native_inputs.py, 필요할 때 좁은 support/provider_ingress.py 및 대응 미러다. 새 helper는 실제 중복이나 공통 fixture 필요가 있을 때만 추가한다. provider_live·provider_runs·provider_close_inputs·observation_inputs·ingress·Sim 등 기존 외부 포트/입력 helper와 계약 시험은 읽기 전용으로 재사용한다.

실제 입력으로 현행 반려 계약을 깨는 runtime 결함을 관측한 경우에 한해 do_math/observation_transport.py·observations.py·core_engine.py·review_engine.py·codex_stream.py·claude_stream.py와 미러에서 해당 수신/owner 경로를 함께 수리할 수 있다. 일반 리팩터링·새 API·스키마나 반려 정책 변경은 목표가 아니다. 범위 밖 제공자 수정이 꼭 필요하면 정확한 입력·기대/실제·심볼·필요 쓰기를 보고하고 허용된 유효 결과를 마친다. 정상 기대를 바꾸거나 예외를 통째로 삼켜 고장을 숨기지 않는다.

## 답할 질문

1. 현재 ADAPTERS와 OBSERVATION_MODES를 기준으로 raw decode→ModelRunner/실제 worker·collector→ObservationTracker→CoreEngineMixin._observe_running→저장, 공개 native block→ReviewEngineMixin._record_review_observation, 제어 영수증/관찰 결속의 경계를 구분한다. raw 입력·내부 ObservationBatch·수신 검사를 이미 통과한 dict의 책임을 섞지 않는다. 잘못된 값을 내부 함수에 직접 넣은 결과만으로 공개 도달 고장을 주장하지 않는다.
2. 원문 2-A의 잘못된 모양·적용 전제 소실·ID 충돌/재전달을 이 입구의 실제 필드와 상태에 대응한다. 기존 RAW_CASES 7축, native_rejection_cases의 외곽/하위 좌표, 결속의 receipt/event 양순서, 동일 내용/다른 내용·순서 역전·빈 후속 batch를 현재 검사와 연결한다. 해당 형식에 없는 경로 축이나 deadline_only에서 생성하지 않는 self-check 결속 등은 정의 근거를 남기고 억지 조합을 만들지 않는다. 등록 표만으로 전건 실행을 주장하지 않는다.
3. 정확한 반려 사유·next_owner·followup의 부재/값, 정확 한 번 소비, 뒤 정상 event/공개 내용과 durable reload, 관련 offset·receipt·head 불변을 실제 단언과 연결한다. live decode가 malformed row를 관찰 사건으로 넘겨 다음 정상 행을 처리하는 계약과 strict collector가 같은 원 stream 전체를 incomplete로 반려하는 계약을 구별한다. collector의 unrelated output validation 실패를 raw 반려의 근거로 쓰지 않는다. 기존 정상 대조군과 source/raw 증거를 보존한다.
4. 종결·삭제 전제는 실제 존재하는 수신 경로와 현행 계약에만 적용한다. ended 실행의 늦은 사실 보존과 다른 실행 진행은 현재 정상 계약일 수 있으므로 무조건 반려하도록 바꾸지 않는다. 현재 실행/검토 대상의 변화가 도달 가능한 위치와 이미 검사된 위치를 구별하고 미확인 축은 정확히 남긴다.
5. 충분한 단언이 있으면 현재 판본과 보존 원보고를 확인해 재사용한다. 빠진 입력/단언만 기존 시험에 보완하고 필요한 최소 공식 ID를 실행한다. R05가 이미 닫은 값 영역을 다시 구현하지 않는다. R06의 이 경계 null slice는 재사용하되 전 제품 null 생산·모든 소비자 모집단은 닫지 않는다. PR15의 해당 slice와 관련 K/P2만 판단하고 R08 공개 제어/수송·R09 제출 입구·2-A 전체·R14 진행성으로 확대하지 않는다.

## 확인과 제출

정적 대조로 충분하면 거기서 끝내며 무변경 조사도 허용한다. 수정 시 자기 workspace scripts/run_tests.py, jobs1로 불확실성을 해소할 최소 입력/공식 ID만 실행한다. 실제 runner/worker/adapter/collector/tracker/owner/repository를 대역으로 바꾸지 않고 외부 Job/CLI/Git 포트는 기존 대역을 쓴다. 새 실제 모델·Job·Lean·예약·네트워크 및 전체 일반/T3/변이/T4/T5 실행은 배정하지 않는다. 시간 기준은 soft이며 정확 단언을 줄이거나 timeout으로 성공을 만들지 않는다.

실행 중 소스를 고정하고 선택 ID·실제 row·exit·판본·실패·미실행과 한계를 보존한다. 공유 runtime/helper를 고쳤다면 실제 직접 소비자의 보존 성질을 읽고 필요한 최소 관련 회귀만 확인한다. 이미 실행한 충분한 검사를 판본/결과 구분 없이 다시 돌리지 않는다. 서로 다른 판본의 부분 성공을 단일 최종 전체 성공으로 합산하지 않는다.

변경 정본/미러는 공식 build_skill_mirrors.py --target .agents로 함께 생성하고 --check --target .agents를 확인한다. 미러 byte 일치로 충분하면 시험을 반복하지 않는다. 비용 캐시 두 개는 evidence에 보존한 뒤 자기 base로 복원한다. 공용소스·context/plan/seams/queue/state·engine·다른 task·과거 원자료·Git index를 수정하지 않으며 graphify도 갱신하지 않는다.

자기 evidence에 실제 입력/도달 전제·수신/owner·정확 단언·원보고/판본·판정을 필요한 만큼 연결한다. 범위 밖 전수 감사나 새 관리 도구를 만들지 않는다. 충분한 기존 성질·수리 완료·정확 미결·최종 판본 대기를 구분해 report.json을 쓰고 python C:/math/services/async-development/check.py report C:/math/.async/dm r10의 PASS를 확인한다. G4~G8, L01 Q1/Q2·원문 UTF-8 byte, Windows1314 symlink 실반려 미검사는 유지한다.
