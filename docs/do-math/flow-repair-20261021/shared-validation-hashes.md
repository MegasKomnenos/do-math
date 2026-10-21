# 공통 검사 입력·해시·실패 분류 수리

## 결과와 남은 범위

R4~R5의 제품 경로를 수정했다. 계획 역할의 전체 검사 catalog가 원장 과제의
의미 해시를 보존하며, 같은 잘못된 선언은 사전·중앙·preview·적용의 공통 검사에서
반려된다. 실제 내용·사용 효력·권한 변경과 저장·환경 실패는 별도로 처리한다.
새 검사 상속 체계, 개정 처분, 운영 질문 상태는 만들지 않았다.

제품 변경과 배정 안의 시험 수정은 완료했지만, 배정 밖
`scripts/tests/unit/test_knowledge_impact_review.py`의 기존 시험 계약 갱신이 남았다.
이 파일과 대응 공식 미러는 writes에 없으므로 수정하지 않았다. task 보고는
이 미완료를 포함해 partial로 제출한다. 전체 개발이나 연구 재개의 완료를 뜻하지 않는다.

## 확인한 원인과 선택

기존 `integration.inspect_bundles`는 이미 공통 검사였다. 문제는
`context_store.prepare_role_input`이 계획 역할의 검사 tasks를 원장 기록으로 교체하며
`content_sha256`을 잃은 것, 그리고 기대 해시가 없는 경우 공통 비교를 생략한 것이다.
뒤의 `bundle_impact_request`는 누락을 발견했지만, `apply_bundles`의 단계 문자열
currentness가 그 일반 ValueError를 실제 전제 변경으로 바꿨다.

수리한 제공·소비 정의는 `scripts/이음새-정본.md`의 「고정 입력 해시와 편입 실패」와
다음 심볼에 있다.

- `context_store.prepare_role_input`: 전체 원장 과제에 `knowledge.content_hash`를
  계산해 검사 문맥으로 지급한다. 역할의 비교 과제에서도 이미 지급한 해시를 유지한다.
  상세 파일과 전체 catalog는 유지한다. 복원한 결과 파일의 local_path나 source_ref를
  의미 해시에 넣지 않는다.
- `integration.inspect_bundles`: 구조·참조와 고정 입력의 mutation 대상/해시를 함께
  검사한다. 기존 대상 부재, 검사 해시 부재·손상, 제출 해시 누락·불일치를 구별한다.
  추가 선언한 previous_hashes도 고정 입력과 대조한다.
- `integration._missing_previous_hashes`: 공통 검사와 live 영향 검사가 함께 사용하는
  필수 이전 해시의 누락 집합이다. 두 위치에 별도 누락 조건을 두지 않는다.
- `integration.bundle_impact_request`: 고정 검사 뒤의 현재 원장 해시 불일치만
  기존 `input_basis.CurrentnessChanged`로 전달한다. 이 함수의 직접 호출자는 먼저
  고정 입력 선언을 검사해야 한다. 타입 자체의 정의는 수정하지 않았다.
- `integration.apply_bundles`, `failure_kind`, `submission_outcome`: 단계 이름으로
  전제 변경을 추정하지 않는다. 일반 ValueError는 integration.validation,
  실제 변경 신호는 integration.currentness다. 영수증의 next_owner도 같은 의미를 쓴다.
- `core_engine._validate_bundle_current`: 현재 권한과 정지를 영향 검토보다 먼저
  확인한다. 사용 효력·내용·출처·과제·목표/정책 판본은 기존 결정 전제 검사에 맡긴다.
- `core_engine._hold_submission_input_failure`: 깨진 검사 입력은 생산자 출력 수리를
  만들지 않고 기존 submission_failure/운영 진단으로 연결한다. 중앙 반려와 적용 반려가
  같은 소비를 쓴다. 그 뒤 운영 질문을 어떻게 종결할지는 R2~R3의 소유다.
- `submission.preview_submission`: 새 검사 경계의 공개 rule_id를 보존하면서 현재처럼
  비공개 후보·오류 본문은 숨긴다. submission_tool의 기존 producer_check 호출을 재사용한다.

| 확인한 경우 | 공통/적용 판정 | 다음 처리 |
|---|---|---|
| 기존 대상의 previous_hashes 누락·오류 | integration.previous_hash, output_contract | output_rejected, producer의 bounded 수리 |
| 고정 catalog에 없는 대상 | integration.mutation_target | 출력 반려 |
| 존재하는 대상의 검사 content_sha256 부재·손상 | integration.input_context, input_failure | 생산자 수리 없이 기존 운영 진단 |
| 올바른 고정 해시, 현재 내용 동일 | 공통 해시 검사 통과 | live 영향·권한·후보 검증·CAS는 계속 필요 |
| 올바른 선언 뒤 실제 내용 변경 | CurrentnessChanged, integration.currentness | premises_changed, refresh_decision |
| 내용 해시가 같아도 사용 효력 정지 | 기존 decision_basis_changes의 실제 변경 | premises_changed, refresh_decision |
| 현재 grant 회수 | 실제 authority 변경 | refresh 판단도 현재 권한에 묶임, paused 유지 |
| OSError/GitStateStoreError/EnvironmentUnavailable | 환경/저장 경계의 실패 | 엔진 소유 대기, 출력 수리 아님 |

## 직접 확인한 범위

모든 실행 근거는 task의 `evidence/`에 있다. 시험은 공식 run_tests.py로 하나씩 실행했고,
시험 실행 중 소스는 편집하지 않았다. 전체 회귀와 실제 공급자·Lean 실행은 수행하지 않았다.

1. `before-tests/report.json`: 수정 전 검사 해시 누락과 일반 ValueError의 잘못된
   premises_changed를 재현했다. 실제 계획 역할 두 종류에서 content_sha256 부재도 관측했다.
2. `audit-replay.json`, `replay_hashes.py`, `original-input/`: 원 실행
   EX-01M5D0ZPXND4CN3VV67DA6HGB2의 문맥·응답·확장·모델이 읽은 과제 상세를
   원바이트로 복사하고 SHA-256을 기록했다. baseline.json에서 복원한 integration.py로
   원래의 premises_changed를 재현했다. 수리판은 원래 결함 문맥을 input_failure로 반려하고,
   의미 해시가 있는 고정 문맥에서는 원 응답을 output_rejected로 돌려준다.
   과제 상세의 해시와 원장 과제에서 계산한 해시의 일치, 올바른 해시 선언의 공통 검사 통과,
   실제 내용을 바꾼 경우의 별도 refresh 판정을 확인했다. 과거 응답 전체를 현행 schema의
   정상 생산물로 간주하거나 실제 상태에 적용하지 않았다.
3. `repair-tests/report.json`: 단위 선택 65개 통과. 당시 새 sim 시험의 문맥/시간 fixture
   문제 1개는 뒤의 consumer-fixed-tests에서 수정·확인했다.
4. `consumer-fixed-tests/report.json`: 12개 통과. 실제 _context/prepare_role_input과
   설치된 producer 도구, 중앙 check_submission, 공통 inspect, 적용을 같은 입력으로 연결했다.
   missing/올바른 해시, 전체 catalog, 결과 파일 경로의 해시 비혼입, 실제 core의 사용 효력
   정지·권한 회수·paused 보존 및 입력 결함 진단을 확인했다.
5. `handoff-tests/report.json`: 선택 36개 중 35개 통과. 실제 후보 준비→과제 계약 교체→
   편입 영수증 게시가 통과했고, 중앙/preview/부분 편입/게시 재시도도 확인했다.
   남은 1개는 허용 범위의 기존 오류 문구 단언을 명시적 CurrentnessChanged.changes 단언으로
   고친 뒤 `impact-consumer-fixed/report.json`에서 통과했다. 같은 성공 시험을 다시 돌리지 않았다.
6. `final-owner-tests/report.json`: 마지막 영수증 owner 정합성 변경 뒤 6개 통과.
   실제 변경은 refresh_decision, 잘못된 선언은 producer, 환경/저장 실패는 engine이다.
   최종 대조에서 live 대상이 사라진 경우도 root 탐색 전에 실제 변경으로 판정하게 했고,
   `final-live-target-tests/report.json`에서 해당 반례를 포함한 7개가 통과했다.
7. `consumer-tests/report.json`의 native 수신 선택은 사용자 정지·paused·변경된 입력·
   회수된 grant·미확인 종료 장벽에서 capture하지 않는 기존 경계를 통과했다.
8. 공식 writing-skills 생성기로 Codex 사본을 생성하고 --check로 비교한다. 시험기가
   자동 갱신한 .timings.json 두 파일은 배정 산출물이 아니므로 시작판 바이트로 복원한다.

## 다음 작업이 필요한 정확한 경계

`outside-scope-consumers/report.json`에서 다음 두 기존 시험의 실패를 직접 확인했다.
필요한 제품 수리는 허용 파일에서 반영됐고, 남은 것은 시험의 현행 입력·신호 계약 갱신이다.

- `unit.test_knowledge_impact_review.ImpactBundleTests.test_previous_hashes_cover_the_exact_current_mutation_targets`:
  예전 ValueError 문구를 단언한다. 누락은 출력 선언 오류로 유지하고, 내용 변경 사례는
  올바른 고정 선언 뒤 live 기록을 변경해 CurrentnessChanged.changes의 id/field/before/after를
  확인해야 한다. 원래부터 틀린 해시를 live 변경의 대용으로 쓰지 않는다.
- `unit.test_knowledge_impact_review.ImpactReviewTests.test_review_required_is_a_waiting_disposition_not_a_producer_retry`:
  실제 mutation 대상이 없는 일반 research_work_context를 적용에 넘겨 새 공통 검사에서
  먼저 반려된다. 원판 mutation 대상의 content_sha256을 가진 고정 catalog가 필요하다.
- 같은 파일의 `test_sealed_review_allows_real_domain_git_retry_and_rejects_wrong_evidence`의
  적용·재전달 두 호출도 정적으로 확인한 같은 입력 결손이다. 이 시험은 실행하지 않았다.
  적용 전에 고정 catalog를 만들고, 적용 후 재전달에도 같은 고정 문맥을 재사용해야 한다.
  적용 뒤 live 상태에서 해시를 다시 계산해 고정 입력을 바꾸면 안 된다.

후속 writes에는 위 정본 시험 파일과 대응 `.agents/skills/do-math/scripts/tests/unit/` 파일이
필요하다. fixture를 공유할 필요가 있으면 `tests/support/knowledge_impact.py:ImpactCase` 및
그 미러도 함께 배정한다. 이번 task는 이 파일들을 수정하지 않았다.
공용 문서의 이 인터페이스 연결 및 최종 회귀는 manager가 통합 상태에서 판단해야 한다.
