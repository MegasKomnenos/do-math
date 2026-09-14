# 적대 검토에 대한 작성자 판단

작성일: 2026-09-08. 대상 검토: `adversarial-review.md`의 AR-01~AR-20. 판단은 19.8절대로 적용·부분 적용·기각·미확인 중 하나이며, 변경 좌표는 반영 뒤 9차 초안의 행이다. 재검증은 `build_spec.py` 재생성 뒤 `verify_spec.py --refresh-examples`와 `verify_spec.py`를 순서대로 실행해 70건 통과를 확인한 결과이며 `validation-report.json`이 고정한다.

| ID | 원 주장 요지 | 자체 판단과 재현 | 처분 | 변경 좌표 |
|---|---|---|---|---|
| AR-01 | 19절 제목이 v8 | 원문 대조로 확인 | 적용 | 초안 1945 |
| AR-02 | 8.3절 상신 항목이 11.3절의 제안 초과 처분과 충돌 | 726행과 950행을 대조해 확인. 결정 B는 재구성을 계획의 판단으로 두므로 제안 초과는 즉시 상신이 아니라 활동 unresolved 종료 뒤 다음 계획의 판단이어야 한다 | 적용 | 초안 722~729의 네 항목 재구성, 716, V145 1742, V162 1759 |
| AR-03 | 상신 대기가 3.2.1절의 waiting 조건과 양립 불가 | 185행과 spec_checks.transition을 대조해 확인 | 적용 | 초안 729, V210 1807 |
| AR-04 | 검토·연구 수행 밖 AI 활동의 누적 초과 처분 부재 | 725·730행과 6.6절 545행을 대조해 확인. 사용자의 원칙대로 자기 실수는 한 번 수리하고 재발은 상신한다 | 적용 | 초안 725·731, V211 1808, spec_checks.overflow_disposition |
| AR-05 | 보류의 효과와 상신 활동의 종료 조건 미정 | 353행·185행과 대조해 확인 | 적용 | 초안 727, V212 1809, Q22 1921 |
| AR-06 | 잘림 허가의 목록·순서와 일반 허가 조건이 스키마·검사에 없음 | build_spec의 permission 페이로드와 pack_listings를 대조해 확인 | 적용 | 초안 759, common truncation_permission과 permission.truncation, spec_checks.check_truncation_permission, V213 1810, verify_spec 시험 |
| AR-07 | 재구성 반환의 기록 가족 부재와 주체 불일치 | activity-result의 kind 열거와 role-contracts를 대조해 확인. 결정 B의 주체는 다음 계획이며 검토 계획자가 아니다 | 적용 | 초안 952·797·2076, activity-result의 identity_review 페이로드, plan.user_decision_requests, role-contracts planning 문면 |
| AR-08 | 종료 원인의 닫힌 값 주장이 스키마에 없음 | CAUSE.code가 자유 문자열임을 확인. 원인 코드 전건을 닫는 것은 이번 결정 밖이므로 문면을 낮춘다 | 적용 | 초안 482 |
| AR-09 | 계약 개정 경로의 프로필 변경과 결정 F의 관계 미정 | 5.5절 381·385행과 대조해 확인 | 적용 | 초안 727 |
| AR-10 | 최종 계수 차이 초과의 처분 없음 | 714행 확인 | 적용 | 초안 714, V214 1811 |
| AR-11 | V203의 기대가 16.1절보다 넓음 | 1391행과 대조해 확인 | 적용 | V203 1800 |
| AR-12 | 참조 항목의 인자 필드 없음 | 스키마 대조로 확인 | 적용 | input-manifest transcript reference.arguments_ref |
| AR-13 | 안정 부분 순서의 검사기 부재와 복원 대화 위치 미정 | provided_order가 자유 문자열임을 확인. 구성 이름을 닫고 상대 순서를 검사한다. 실제 바이트 배치의 일치는 어댑터 검증의 몫이라 남긴다 | 부분 적용 | 초안 702, input-manifest provided_order 열거, verify_spec 순서 검사 |
| AR-14 | apply_edits.py가 1019행을 재현하지 못함 | 시뮬레이션 재현 확인 | 적용 | apply_edits.py에 치환 기록 |
| AR-15 | 상신 질문의 형식과 보류 기록이 묶음에 없음 | runtime.threshold_holds의 kind 열거를 확인 | 적용 | 초안 727·1224, runtime.threshold_holds kind에 context_overflow·output_truncation |
| AR-16 | 정리 요청의 적용 경로와 사용자가 볼 정보 | 문면 대조로 확인 | 적용 | 초안 727 |
| AR-17 | 통치 전문의 범위와 결정 전문의 목차 회수가 겹침 | 문면 대조로 확인 | 적용 | 초안 724 |
| AR-18 | 참조 재열람 반복 초과의 종료자가 총한도뿐 | 시간 순 추적으로 확인 | 적용 | 초안 725 |
| AR-19 | 재지정 V18이 규칙에 미연결 | source-vector-map 확인 | 적용 | R17 source_vectors |
| AR-20 | 어댑터의 초과 시 동작 필드 없음 | 스키마 대조로 확인 | 적용 | execution-profile ai.compaction의 overflow_behavior·overflow_evidence_ref, spec_checks.check_restoration_profile |

기각한 지적은 없다. 검토자의 결정별 표에서 부분이었던 B·C·F·J·3은 위 처분으로 반영이 됐고, J는 순서의 상대 검사까지만 기계 검사이며 실제 배치는 D01의 어댑터 검증에 남는다.

재검증 결과: 시험 70건 통과, 벡터 214건 가운데 철회 2건, Q 22건, 초안 해시와 source-vector-map 일치. 실제 어댑터의 압축 제어·멈춘 이유 반환·결과별 artifact 수집은 검증하지 않았고 D01의 몫이다.
