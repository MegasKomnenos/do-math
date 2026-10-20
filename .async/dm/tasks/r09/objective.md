# 목적과 완료할 결과

원문2-A/R09의 제출 확장 가족·참조 검증기에서 잘못된 모양, 적용 전제 소실, 동일 ID 충돌/재전달이 정확히 반려되고 한 번 소비되며 뒤 정상 제출이 진행하는지 현재 실제 경로로 판단한다. 확인된 가까운 시험/helper·허용 runtime의 공백은 같은 task에서 수리하고 관련 최소 확인·미러까지 마친다. 단순 목록 생성이나 과거 사례 수를 현재 완료 증거로 쓰지 않는다.

## 입력과 현재 위치

SESSION_JSON workspace, 고정 inputs/context.md·plan.md·seams.md와 task.json을 읽는다. C:/math/docs/do-math/continuous-development-2026-10-13의 sources/user-decisions.md·requirements-index.json·모델/묶음 지시, phases/001/tasks/closure-map/evidence의 tracking-state.json R09, requirement-state.json 2-A, prior-review-state.json PR07 B29/B47 제출 slice, evidence-catalog.json current_work.submission_population_integration/submission_identity_integration가 원자료다. repo:는 자기 workspace, 과거 run:은 위 continuous-development 루트이며 C:/math/docs와 C:/math/.async/dm는 읽기 전용 자료다. 큰 JSON은 해당 항목만 읽고 원보고가 없으면 부재로 남긴다.

r05의 네 외부 값 경계와 extension null/부재/빈 가족·hash 보존은 수용됐다. tasks/r05/report.json·evidence/boundary-map.json·verification.json 및 managers/0009/review.md의 그 slice를 재사용하고 전체 R06/2-A로 확대하지 않는다. 현재 수용된 r14는 진행성 부분 수리이며 본 작업의 전제가 되는 추가 결과는 없다. r08(제어), r03-fix(관찰 저장), r14-fix(진행성)의 정의·중간 사본은 바꾸거나 소비하지 않는다.

## 종료할 질문

1. submission.EXTENSION_ROLES·extension_schema의 현재 role/phase/가족과 validate_reference/_validate_reference·연구 참조·supplied_record_ids, integration의 실제 member/reference 소비를 기존 submission_obligations의 action_rows/extension_ingresses와 현재 단언에 연결한다. 역사13모듈/81사례는 위치표다. 실제 현행 생산/수신과 유한 입력축으로 충분성을 판단하고 입력 수 자체를 목표로 삼지 않는다.
2. 원문 비객체·빈 목록·None·0·잘못된 스칼라/경로(빈/루트/상위)·필수/enum 및 참조 입력을 각 실제 수신 전제와 연결한다. 낮은 helper의 string 전제와 owner 공개 입구의 구조화된 반려 책임을 구별한다. payload_issues/check_submission의 rule_id/path/message·분류와 원바이트/해시, schema 실패의 skip 의미를 확인한다. 같은 구현 함수로 기대값을 재계산하지 않고 정본 계약·독립 기대값을 사용한다.
3. OwnerIngressAssertions.reject_and_replay와 실제 submission_model/worker→ControlTransport→core 중앙 봉인/수신→domain/store를 읽어 정확 반려 1회, 변이된 같은 locator/동일 ID 재전달의 불변, payload 충돌, 뒤 정상 수락·실제 적용·reload를 연결한다. 일부 issue만 선택하는 검사가 추가 비정상 issue를 숨기는지 등 실제 공백을 확인한 범위만 보완한다. producer 검사 성공만으로 중앙 owner를 대신하지 않는다. 필요한 반례는 기존 정상 외곽·실제 소유 흐름을 사용한다.
4. 적용 시점 종결·삭제 전제는 실제 제품 생산자가 있는 경우만 도달 시나리오로 세운다. 공개 작업으로 불가능한 삭제를 저장 dict에서 지워 reachable evidence로 포장하지 않는다. 고정 입력 snapshot의 허용된 역사 참조와 현재 대상 권한을 구별한다. 같은 ID 두 transport/양순서는 수송 공통 경계와 제출 고유 의미를 구분해 r08과 중복 전수 실행하지 않는다. 제출 고유 내용/중앙 receipt 공백이면 자기 helper에서 처리하고 수송 자체 결함은 r08 범위로 보고한다.
5. PR07 B29/B47의 관련 실제 hunk→현재 caller/검사→원보고의 정확 row/판본을 대조한다. 충분한 성질은 유지하며 원문 범위를 넘어 전체 PR07/K/P2나 공개 제어·관찰 입구를 재감사하지 않는다. 필요한 수리·직접 소비 확인을 모듈/가족마다 따로 넘기지 않고 같은 task에서 끝낸다.

## 수정 범위와 독립성

task.json writes가 권한 정본이다. 제출 ingress/extension/reference/identity 관련 unit·flows·sim 시험, submission_obligations·submission_owner_obligations·submission_advertised 및 필요한 submission_calls helper와 각 미러가 대상이다. 실제 재현한 해당 결함이면 submission.py·integration.py 안의 수신/참조/구조화된 반려를 수리할 수 있다. 전체 제출 기능을 다시 설계하는 배정은 아니다.

core_engine.py·control_transport/protocol/contracts, 공유 support.ingress·record_builders·provider_probes, 관찰/스케줄링/record schema와 다른 task의 파일은 읽기 전용이다. 이미 넓은 권한을 가진 진행 중 r08/core와 충돌하지 않게 했다. 범위 밖 owner 수정이 실제로 필요하면 정확 입력·관측·필요한 파일을 보고하고 범위 안 유효 결과를 마친다. 계약 자체 변경이 필요하면 소비자/문서까지 필요한 범위를 보고하며 호환 경로·별도 등록 체계를 임의로 추가하지 않는다.

## 최소 확인과 제출

정적 확인/기존 원보고로 충분하면 새 시험을 돌리지 않는다. 새 입력/단언·runtime 수정에만 자기 workspace의 공식 scripts/run_tests.py jobs1로 가장 작은 관련 ID를 실행한다. 실패는 먼저 읽고 수리한 뒤 해당 ID만 확인한다. 충분한 광범위 회귀를 반복하거나 시간 기준 때문에 입력·단언을 줄이지 않는다. 실제 제품 메서드를 가짜로 바꾸지 않으며 외부 대역은 기존 계약 fixture를 사용한다. 전체 일반/T3/변이/T4/T5·새 외부 모델/Lean/Job/설치/예약은 이 배정이 아니다.

소스 고정·선택/실제 row·exit·해시·최초 실패·fixture 오류·남김을 evidence에 보존한다. 서로 다른 판본의 성공을 전체 성공으로 합산하지 않는다. 공식 build_skill_mirrors.py --target .agents 및 --check --target .agents와 대응 바이트를 확인하고 비용 캐시2개는 evidence 보존 후 자기 base로 복원한다. report에 실제 변경 전부와 원문/현행 경계/정확 단언/증거/처분을 담고 check.py report C:/math/.async/dm r09의 PASS를 확인한다. 공용소스·공용문서/queue/state·engine·다른 task·원자료·Git index를 수정하지 않고 graphify를 갱신하지 않는다. 다른 미결과 G4~G8·L01·Windows1314 미검사는 유지한다.
