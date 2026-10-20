# test_external_operations

| 항목 | 값 |
|---|---|
| 조각 | `foundation` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_external_operations.py` (105행) |
| 클래스 / 테스트 | 2 / 6 |
| 시험 대상 제품 코드 | `do_math/external.py`의 `prepare_operation`, `execute_operation`(안에서 `validate_operation`), `reconcile_operation`; `do_math/governance.py`의 `apply_decision`(`grant`, `revoke` 결정), `preserve_source`, 간접으로 `_dispose_grant_consumers`와 `grant_scope_reason` |
| 사용하는 픽스처 모듈 | `research_fixtures`(`governance_start`) |
| 격리 표지 | 없음 |
| 시작 상태 | 1단. 연산 기록과 허가(grant)를 사전으로 만들어 제품 함수를 직접 부른다. 전송(transport)은 람다 대역이고 요청은 프로세스를 떠나지 않는다 |

## 목적

모듈 docstring은 "허가 아래의 외부 연산: 준비, 전송 상태, 대조(reconciliation), 범위 메타데이터"를 시험하며 "어떤 요청도 프로세스를 떠나지 않고, 전송과 응답은 합성"이라고 밝힌다. 제품의 외부 연산은 `external.prepare_operation`이 요청을 정규화하고 요청 해시와 멱등 키를 묶은 `prepared` 기록을 만들고, `execute_operation`이 허가를 확인한 뒤 `persist` 콜백으로 전송 전 상태를 먼저 기록하고 전송한다. 이 모듈은 다음 네 규칙을 본다.

- 한 번 전송 표지가 기록된 연산은 복구 없이 다시 보낼 수 없고, 결과가 모르는(`unknown`) 연산은 요청에 묶인 증거로만 대조한다.
- 2xx가 아닌 응답은 효과가 없음이 증명될 때만 `failed`가 되고, 자격 증명이 없으면 연산은 `prepared`로 남아 대기 사유를 기록한다.
- 허가를 철회하면 아직 전송하지 않은 준비 연산만 취소된다.
- HTTP 허가의 범위 메타데이터(대상, 목적, 주체, 실행 종류)와 일회성(`reuse='once'`) 장부가 실제 전송 경로에서 검사된다.

## 모듈 수준 요소

- 행 11: 스킬의 `scripts/` 폴더를 `sys.path` 앞에 넣는 공통 머리.
- 행 104–105: 직접 실행하면 `unittest.main()`으로 이 모듈의 시험을 돈다.

## ExternalOperationTests (행 18–81)

`unittest.TestCase`를 그대로 상속한다. 클래스 표지, 클래스 속성, 설정 훅이 없다. 도우미 메서드 둘이 뒤의 세 시험의 입력을 만든다.

- `_grant(**extra)` (행 33–41): 활성 허가 `G`. `expires_at=None`, 허용 출처 `https://example.test`, 허용 메서드 `POST`, 허용 경로 접두 `/submit`, 빈 `credential_env`. `extra`로 필드를 덮어쓴다. `kind`가 없으므로 `validate_operation`의 HTTP 범위 검사(`grant.get("kind") == "http"`)는 돌지 않는다.
- `_operation()` (행 43–47): `prepare_operation`으로 만든 `POST https://example.test/submit` 연산(본문 `"proof"`, 허가 `G`, 원천 `source`).

### `test_unknown_with_sent_marker_cannot_silently_retransmit` (행 19–26)
- 성질: 전송 표지가 기록된 연산은 복구 없이 다시 전송되지 않는다.
- 준비: `prepare_operation`으로 `POST https://example.test/p` 연산을 만든 뒤 `transmitted=True`, `transmission_phase="recorded"`로 바꾼다. 허가는 출처·메서드·경로 `/`를 모두 허용하는 활성 허가다. 전송 호출을 세는 `calls` 목록을 둔다.
- 실행: `execute_operation(op, grant, persist=lambda _: True, transport=...)`. 전송 대역은 호출되면 `calls`에 1을 더하고 200 응답을 돌려준다.
- 단언: `ValueError`가 나고 `calls`가 빈 목록이다. 예외 유형만 보고 메시지는 고정하지 않는다. 제품에서 이 경로의 메시지는 `"recorded transmission requires recovery before another send"`다.
- 대역: 전송 람다, 항상 참인 `persist` 람다.
- 비고: 이름은 "unknown"을 말하지만 연산의 `status`는 `prepared` 그대로다. 거부는 `status == "unknown"` 분기가 아니라 전송 표지 분기에서 난다. 거부 사유를 메시지로 고정하지 않으므로 어느 분기에서 거부되었는지는 단언이 가리지 않는다.

### `test_reconciliation_cannot_assert_success_from_unbound_text` (행 28–31)
- 성질: 결과를 모르는 연산은 연산에 묶이지 않은 글 한 줄로 성공을 대조할 수 없다.
- 준비: `prepare_operation`으로 만든 연산의 `status`를 `"unknown"`으로 바꾼다.
- 실행: `reconcile_operation(op, "a receipt", "confirmed", source="user", succeeded=True)`(함수 안에서 import).
- 단언: `ValueError`. 예외 유형만 본다. 증거가 사전이 아니므로 제품의 첫 검사(`"invalid reconciliation"`)에서 거부된다.
- 대역: 없음.
- 비고: 증거가 사전이지만 연산 ID·요청 해시·멱등 키를 묶지 않은 경우(`"reconciliation evidence must bind the exact external operation"`)는 이 모듈에서 따로 검사하지 않는다.

### `test_non_2xx_is_failed_only_when_effect_absence_is_evidenced` (행 49–57)
- 성질: 2xx가 아닌 응답은 응답이 효과 없음(`effect_absent`)을 명시할 때 `failed`로 기록된다.
- 준비: `_operation()`과 `_grant()`.
- 실행: 전송 대역이 `{"http_status": 409, "body": b"rejected", "effect_absent": True}`를 돌려주는 `execute_operation`.
- 단언: 결과의 `status`가 `"failed"`, `succeeded`가 `False`(동일성 비교), `effect_absent`가 참이다.
- 대역: 전송 람다, `persist` 람다.
- 비고: 이름의 "only when"이 뜻하는 반대편, 곧 `effect_absent` 없는 비2xx 응답이 `unknown`으로 남는 경로(`"non-success response does not establish effect absence"`)는 이 시험에서 단언하지 않는다.

### `test_missing_credential_preserves_prepared_operation_and_wait_reason` (행 59–69)
- 성질: 허가가 요구하는 자격 증명 환경변수가 없으면 연산은 전송되지 않은 `prepared` 상태로 남고 대기 사유 `credential_unavailable`을 기록한다.
- 준비: `_operation()`. 환경변수 `DO_MATH_TEST_MISSING_SECRET`을 `os.environ`에서 빼 두고, 원래 값이 있었으면 `addCleanup`으로 되돌린다. 허가는 `_grant(credential_env={"Authorization": "DO_MATH_TEST_MISSING_SECRET"})`.
- 실행: `transport` 없이 `execute_operation(operation, grant, persist=lambda _: True)`.
- 단언: 결과의 `status`가 `"prepared"`, `transmitted`가 거짓, `waiting_reason["kind"]`가 `"credential_unavailable"`이다.
- 대역: `persist` 람다. 전송 대역을 주지 않지만 제품이 자격 증명 확인에서 먼저 돌아오므로 실제 HTTP 전송 함수(`_http`)에 닿지 않는다.
- 비고: 실제 환경변수를 읽고 고친다. 원래 값이 없었으면 정리 함수는 아무것도 하지 않는다.

### `test_revocation_cancels_only_untransmitted_prepared_effects` (행 71–81)
- 성질: 허가를 철회하면 그 허가 아래의 전송 전 준비 연산이 `cancelled`로 바뀌고 전송되지 않은 상태로 남는다.
- 준비: `governance_start`로 빈 거버넌스 가족을 가진 인스턴스 `I`를 만들고 사용자 원천 `user`를 `gov.preserve_source`로 보존한다. `apply_decision`으로 HTTP 허가 `G`(`reuse='reusable'`, 출처·메서드·경로 `/submit`)를 채택한다. 런타임의 `external_operations`에 `_operation()` 하나를 둔다.
- 실행: `apply_decision(instance, runtime, {"kind": "revoke", "grant_id": "G", "decision_id": "D"}, source_ref="user")`.
- 단언: 갱신된 런타임에서 그 연산의 `status`가 `"cancelled"`이고 `transmitted`가 거짓이다.
- 대역: 없음.
- 비고: 이름은 "only untransmitted"를 말하지만 시험에는 전송 전 연산 하나만 있다. 전송이 기록된 연산이 취소되지 않고 `recover_operation`으로 넘어가는 반대 분기(`governance.py`의 `_dispose_grant_consumers`)는 단언하지 않는다.

## ExternalScopeConsumerTests (행 84–101)

`unittest.TestCase`를 그대로 상속한다. 표지, 속성, 훅, 도우미가 없다.

### `test_external_scope_metadata_is_checked_in_actual_send_and_once_ledger` (행 85–101)
- 성질: HTTP 허가의 범위 메타데이터(목적 등)는 실제 전송 경로에서 검사되고, 일회성 허가는 장부에 다른 사례가 이미 있으면 다시 쓸 수 없다.
- 준비: `kind='http'`, `reuse='once'`, `included_targets=['T']`, `purposes=['publish']`, `subjects=['external_operation']`, `execution_kinds=['machine']`인 허가 `G`. `prepare_operation`에 `target_id='T'`, `purpose='publish'`, `subject='external_operation'`, `actor_kind='machine'`을 주어 범위 메타데이터를 단 연산. 전송 호출 인자를 모으는 `calls`.
- 실행: 세 번 `execute_operation`을 부른다. (1) 원 연산을 빈 `runtime={}`로. (2) `purpose`만 `'unapproved'`로 바꾼 사본을 빈 런타임으로. (3) 원 연산을, 첫 결과를 ID `USED`로 바꾸어 `external_operations`에 담은 런타임으로.
- 단언: (1)의 `status`가 `'confirmed'`. (2)와 (3)은 `ValueError`. 끝으로 `calls` 길이가 1이어서 거부된 두 호출은 전송하지 않았다. 예외 유형만 보고 메시지는 고정하지 않는다. 제품에서 (2)는 `"purpose outside grant"`, (3)은 `"one-case grant already reserved or consumed"`로 거부되는 경로다.
- 대역: 전송 람다(200, `b'ok'`), `persist` 람다.

## 관계

- 같은 제품 기능을 다른 층에서 검사하는 모듈: `test_external`(외부 연산의 넓은 경로, `host` 조각), `test_lifecycle_engine`(엔진 안의 실행), `test_family_records`와 `test_state_checks`(연산 기록의 저장 검증), `test_json_digests`(`prepare_operation`의 해시), `test_academic`(학술 선행 조건이 붙은 연산 준비).
- 픽스처 의존: `research_fixtures.governance_start` 하나. 허가와 연산은 모두 시험 안에서 만든다.
- 이 모듈에만 있는 도우미: `ExternalOperationTests._grant`, `_operation`.
- 겹치거나 보완하는 시험: `test_governance`의 허가 채택·철회 시험은 거버넌스 쪽 결과를, 이 모듈의 철회 시험은 그 결과가 외부 연산 장부에 미치는 영향을 본다.
