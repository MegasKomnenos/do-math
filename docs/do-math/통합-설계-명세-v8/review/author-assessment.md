# 적대 검토 피드백의 자체 타당성 판단

독립 검토가 지적한 14건을 작성자가 직접 재현했다. 결함의 취지는 모두 타당했다. 13건은 수정 방향까지 수용했고, ADV-009는 결함을 인정하되 생산자가 수신 결과를 미리 쓰게 하는 방향을 채택하지 않고 예비 재생성 시각으로 해결했다. 아래 판정은 검토자의 권위를 근거로 한 승인이 아니라 원문·입력·실제 반환을 대조한 작성자의 판단이다.

독립 검토의 대상은 review-basis.json에 해시로 고정한 수정 전 판본이다. 원 검토는 adversarial-review.md, 원 반례 코드는 adversarial-probes.py, 수정 전 작성자의 일괄 재현 결과는 feedback-reproduction-full.json에 보존했다. 작성자의 별도 반례는 self-probes-before-feedback.json에 있다. 검토자는 작성자의 추가 반례를 보지 않고 결과를 봉인했다.

원 반례 코드는 수정 전 인터페이스와 잘못된 입력의 통과를 관찰하는 역사 자료다. 수정 후에는 집계 함수가 기대 논리 자리 집합을 요구하고 잘못된 전이가 예외를 내므로, 그 코드를 그대로 끝까지 실행하는 것을 회귀 통과 조건으로 사용하지 않는다. 현재 회귀 검사는 상위 디렉터리 verify_spec.py의 test_regression_*와 역할·스키마·codec 검사다.

| 지적 | 자체 판단 | 근거와 적용 | 현재 검증 |
|---|---|---|---|
| ADV-001 | 적용 | run과 resume의 payload는 같아도 전체 요청 해시가 달랐다. 재시도 문면·request_fingerprint·check_replay를 schema_version, request_id, command, caller, payload 전체에 결박했다. | test_regression_entire_request_idempotency |
| ADV-002 | 적용 | paused/resume_lifecycle=active 자체는 active에서 정지한 경우 유효하므로 스키마에서 일괄 금지하지 않았다. 전이 검사에서 resume_lifecycle이 실제 이전 상태와 같은지 확인한다. | test_regression_pause_entry_preserves_stage |
| ADV-003 | 적용 | 빈 근거로 활성화·대기 해소가 통과했다. R41·R42를 소유 규칙으로 추가하고 활성화 전건·대기 해소·새 요청의 공개를 전이에서 요구했다. | test_regression_activation_and_waiting_guards |
| ADV-004 | 적용 | 10단위 예약 중 소비 3·반환 2만 기록하고 settled가 됐다. settled에는 소비+반환=예약을 요구하며 미확인 잔액은 held/unrecoverable에 남긴다. | test_regression_settled_balance |
| ADV-005 | 적용 | goal의 satisfied와 scope_complete=false가 함께 통과했다. 모든 satisfied에 범위 완결을 구조적으로 요구한다. 실제 범위·근거 검사는 별도 의무다. | test_regression_satisfied_requires_complete_scope |
| ADV-006 | 적용 | 초기 한 표 또는 열린 이의가 남은 최종 match가 승인됐다. 집계가 기대 slot 집합과 실제 slot별 결과의 정확한 대응을 받고 열린 이의의 match를 막도록 바꿨다. | test_regression_aggregation_needs_exact_slots_and_closed_issues |
| ADV-007 | 적용 | 같은 자리의 세 결과가 세 판정자로 집계됐다. issue-state의 고유·배정 자리 검사와 집계 함수의 기대 자리 집합 대조를 추가했다. | test_regression_duplicate_judge_cannot_be_three_votes |
| ADV-008 | 적용 | 저장 예제의 최소 할당부터 한도를 초과했다. 계획의 초기 검토 수·답변 몫·최종 몫·총한도, 자리·범위 대응, 기본·조건부 관점과 결론 폐쇄를 검사하고 예제를 교체했다. policy·proposal의 실제 정확한 참조 대조는 본문에 계속 명시했다. | test_regression_review_plan_allocations, test_all_structural_examples |
| ADV-009 | 부분 적용, 결함 해소 | 무산출 결과에 재생성 시각이 없다는 지적은 맞다. 그러나 생산자가 accepted 계약 집합을 확정하는 방식은 수신자 소유권을 침범할 수 있다. 생산자는 observed_at보다 뒤의 예비 regenerate_after를 제출하고 수신자가 실제 무산출일 때만 소비하도록 B 19.5를 구체화했다. | test_regression_preparation_future_fallback |
| ADV-010 | 적용 | full을 표현하려고 허위 partial_reason이 필요했다. partial에는 필수, full에는 금지하는 분기로 바꿨다. | test_regression_full_has_no_partial_reason |
| ADV-011 | 적용 | 현재 task에 완료와 닫힘 근거가 공존했다. completion_ref와 closure_ref를 각 종결 상태에만 허용한다. 과거 근거는 원래 기록과 정확한 참조로 보존한다. | test_regression_task_terminal_fields_are_exclusive |
| ADV-012 | 적용 | 실제 init 예제의 instance_id가 F였고 다른 외래 ID도 종류 제한이 없었다. 명시적 가족 ID에 typed ID를 적용하고 다형적 record_id·수학 항목 ID와 구별했다. 배열의 공통 정의가 다른 종류로 함께 바뀌지 않도록 사본을 사용한다. | test_regression_foreign_ids_are_typed, test_all_structural_examples |
| ADV-013 | 적용 | normalize 성공이 ID 하나로 통과했다. 응답 mode·family를 분기하고 normalize의 candidate_ref·check_ref를 필수로 했으며 요청·응답 쌍의 결속도 검사한다. | test_regression_record_normalize_response_binding |
| ADV-014 | 적용 | 현재 원천 맵과 레지스트리 값은 맞았지만 손상 후에도 검사기가 통과했다. V/Q의 원문·기대·행·해시·소유 연결과 레지스트리 메타데이터를 대조하고 생성 스키마와 저작 선언도 비교한다. | test_source_vectors_and_quality_bijection, test_regression_source_map_content_tampering, test_registry_exact_bijection_and_hash, test_generated_schema_matches_authoring_source |

작성자가 추가로 확인한 항목도 함께 반영했다.

| 항목 | 확인과 수정 | 검증 |
|---|---|---|
| 후보·K 목차의 기본 정보 | 일반 항목에 묶으면서 description을 필수로 만들고 revision·work_class·저작 계보·선언 정보를 빠뜨렸다. 후보와 K 항목을 분리해 B 8.5의 직접 제공 필드를 복원했다. | test_regression_candidate_and_canon_listing_contracts |
| 종류 정의의 필드 확장 | required_fields로 존재하지 않는 권한 필드를 요구할 수 있었다. 현행 F 필드의 허용 범위만 인정한다. | test_regression_unknown_kind_fields_and_missing_common_document |
| 공통 문서 누락 | 파일 두 개라는 수만으로 SKILL·GLOSSARY의 존재를 대신했다. 두 이름의 정확히 한 번 포함을 요구한다. 실제 전문 주입 검사는 별도 어댑터 의무다. | 같은 회귀 검사 |
| 배정과 선택 처분 불일치 | 선택 처분 없이 dispatch_order를 만들 수 있었다. 선택 ID 집합과 배정 순서를 대조한다. 제공 모집단·현재성은 원문 계약에 따른 수신 검사다. | test_regression_dispatch_requires_selected_disposition |
| 개별 검토 반환의 소유 | 개별 검토·심사·답변·정리를 공용 assessment나 원장 상태와 혼동하지 않도록 review-result와 역할별 출력 대응을 추가했다. 개별 결과를 수신한 실행기가 집계한다. | test_review_result_phase_authority, test_role_output_contracts_cover_every_stage, test_execution_output_schema_binding |
| 검사 환경의 판본 | 실제 검증한 Python·JSON Schema·YAML 도구 판본을 toolchain-lock.json에 고정했다. | test_toolchain_lock |

수정 후 검사는 validation-report.json에 기록한다. 명세 검사, 합성 전제 아래 순수 계약 검사, 원문 대응만 이 보고의 검증 범위다. 실제 OS 격리·입력 주입·프로세스 및 원격 종료·공급자 한도·전체 런타임 관문·Lean·연구 효능·외부 정의 동기화는 완료로 주장하지 않는다.

판정: 위 결함의 교정과 해당 명세 회귀 검증을 통과했다. 독립 검토의 수정 전 DEFECT 기록을 PASS로 바꾸지 않는다. 이 판정은 작성자의 수정 후 자체 검증이며, 수정 후 독립 재검토를 수행했다는 보고가 아니다.
