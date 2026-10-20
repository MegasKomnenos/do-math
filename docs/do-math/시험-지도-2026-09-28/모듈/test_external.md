# test_external

| 항목 | 값 |
|---|---|
| 조각 | `host` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_external.py` (107행) |
| 클래스 / 테스트 | 1 / 10 |
| 시험 대상 제품 코드 | `do_math/external.py`의 `prepare_operation`, `validate_operation`, `execute_operation`, `_http`, `recover_operation`, `prepare_retry`, `reconcile_operation`(그리고 그 안의 `_url`, `_body`, `request_binding_current`, `_NoRedirect`); `do_math/repository.exact_content_hash` |
| 사용하는 픽스처 모듈 | `provider_fixtures.HTTPFixtureHandler` |
| 격리 표지 | 없음 |
| 시작 상태 | 1단에 가까운 직접 호출. 저장소·엔진 없이 제품 함수를 부르되, 각 시험마다 `setUp`이 실제 HTTP 서버를 루프백 주소에 띄운다 |

## 목적

원문에는 모듈 docstring이 없다. 제품 `external.py`의 docstring은 "감사 가능하고 허가(grant)에 묶인 외부 HTTP 조작"이다. 조작 하나는 `prepare_operation`으로 요청 바이트와 멱등 키를 고정한 기록이 되고, `execute_operation`이 허가를 검증한 뒤 "보내기 전에 저장, 보냄 표지를 저장, 응답을 저장"의 순서로 원장에 남기며 전송한다. 결과가 불확실하면 `unknown`이 되고, 그 뒤에는 증거에 묶인 조정(`reconcile_operation`)이나 재시도(`prepare_retry`)를 거쳐야만 진행한다. 이 모듈은 메서드·본문 규칙, 저장 순서와 자격 증명 비노출, 불확실 결과의 처리, 재지정(redirect) 거부, 원장 저장 실패, 멱등 키 변조, 자격 증명 대기와 재개, 전송 직전의 허가 철회를 검사한다.

## 모듈 수준 요소

- 행 6: `scripts/` 폴더를 `sys.path` 앞에 넣는 공통 머리.
- 행 7–10: `exact_content_hash`, `do_math.external`의 공개 이름 전부(`from do_math.external import *`, 제품에 `__all__`이 없어 밑줄 없는 이름이 모두 들어온다), 모듈 객체 `external`, `provider_fixtures.HTTPFixtureHandler`를 import한다.
- 행 107: 직접 실행하면 `unittest.main()`.

## Tests (행 11–106)

`unittest.TestCase`를 그대로 상속하고 표지가 없다. 설정·정리 훅이 매 시험마다 실제 HTTP 서버를 띄우고 내린다.

- `setUp` (행 41–44): `HTTPServer(('127.0.0.1', 0), HTTPFixtureHandler)`를 빈 포트에 열고 데몬 스레드에서 `serve_forever`한다. `self.origin`은 `http://127.0.0.1:<포트>`다. 픽스처 처리기는 POST에 201과 본문 `ok`를, GET에 `Location: http://evil/`인 302를 돌려준다(`provider_fixtures.py` 행 227–236). `self.grant`는 ID `G`, `status='active'`, 만료 없음, 허용 출처 `[self.origin]`, 허용 메서드 `['POST', 'GET']`, 허용 경로 접두 `['/ok']`, 자격 증명 머리 `{'X-Key': 'EXT_TEST_KEY'}`인 허가다. `patch.dict(os.environ, {'EXT_TEST_KEY': 'secret'})`를 `enterContext`로 걸어 시험이 끝나면 환경이 복원된다.
- `tearDown` (행 45): 서버를 `shutdown`하고 `server_close`한다.

### `test_method_body_contract_matches_preparation_validation_and_http_bytes` (행 12–39)
- 성질: 메서드와 본문의 조합 규칙이 준비, 검증, 실제 HTTP 바이트에서 같게 적용되고, GET·DELETE에 본문을 몰래 넣은 옛 기록은 전송 전에 거부된다.
- 준비: 네 메서드를 모두 허용하고 자격 증명 머리가 없는 허가. 본문 없음(`None`), 빈 문자열, `'é'`, 정수 `7`의 네 가지.
- 실행: 메서드 4 × 본문 4 = 16개의 `subTest(method=..., body=...)`. 거부 대상이면 `prepare_operation(request, 'G', 'S')`가 실패함만 본다. 나머지는 `prepare_operation`, `validate_operation(operation, grant, '2026-01-01T00:00:00Z')`, `external._http(operation, [], 5)`를 부른다. GET·DELETE의 통과 경우에는 요청 본문을 `'legacy'`로 바꾸고 `request_sha256`과 `idempotency_key`를 다시 계산해 해시 결합은 맞지만 규칙을 어긴 옛 기록을 만들고, `execute_operation`에 넘긴다.
- 단언: 본문 `7`(모든 메서드)과 GET·DELETE의 `'é'`는 `prepare_operation`에서 `ValueError`다(메시지 미단언; 제품 문구는 `body must be text`, `GET and DELETE cannot carry a nonempty body`). 나머지는 검증을 통과하고, `_http`가 돌려준 `body`가 `b'ok'`이며, 대역 opener의 `open`에 넘긴 `Request`의 `get_method()`가 그 메서드이고 `data`가 `'é'`이면 UTF-8 바이트 `b'\xc3\xa9'`, 그 밖(본문 없음·빈 본문)이면 `None`이다. 옛 기록의 `execute_operation`은 `ValueError`이고, 전송 대역이 한 번도 불리지 않았다(`calls == []`).
- 대역: `patch.object(external, 'build_opener')`로 opener를 바꾸고, 응답은 상태 200·본문 `ok`인 `MagicMock` 컨텍스트다. 옛 기록 경우의 `persist`는 항상 참, `transport`는 호출을 기록하는 람다다. 이 시험은 `setUp`의 실제 서버를 쓰지 않는다.
- 비고: 거부 사유를 메시지로 고정하지 않으므로, 옛 기록이 `_body` 규칙이 아닌 다른 이유로 거부되어도 통과한다.

### `test_persist_before_send_confirm_and_redact` (행 46–48)
- 성질: 전송 전에 준비 기록과 보냄 표지를 차례로 저장한 뒤 확인 결과를 저장하고, 결과에는 자격 증명 값이 남지 않는다.
- 준비: `setUp`의 서버와 허가. 본문 `'x'`인 POST `/ok`.
- 실행: `execute_operation(op, self.grant, persist=...)`. 실제 루프백 HTTP로 전송된다.
- 단언: 저장된 기록의 `status` 순서가 `['prepared', 'prepared', 'confirmed']`이고, 둘째 기록의 `transmitted`가 참이다(보냄 표지가 응답 전에 저장됨). 반환 `status`가 `confirmed`다. 반환 사전의 문자열에 `'secret'`이 없다.
- 대역: `persist`는 기록을 모으고 참을 돌려주는 람다.
- 비고: 실제 외부 자원은 루프백 HTTP 서버다.

### `test_unknown_retry_reconcile_and_scope` (행 49–58)
- 성질: 결과를 모르는 전송은 `unknown`이 되어 다시 보낼 수 없고, 조작에 정확히 묶인 증거로만 조정되며, 만료된 허가와 사용자 정보가 든 URL과 경로 탈출은 거부된다.
- 준비: 빈 본문 POST 조작.
- 실행: 아래 번호 단계에 적은 호출을 차례로 한다.
- 단언: 각 단계의 단언은 아래 번호 단계에 함께 적는다. 단계 목록:
  1. `transport`가 `TimeoutError`를 던지게 해 실행하면 `status`가 `unknown`이다.
  2. 그 `unknown` 조작을 다시 `execute_operation`하면 `ValueError`다(제품 문구 `unknown operation requires reconciliation`).
  3. 증거 자리에 문자열 `'receipt'`를 넘긴 `reconcile_operation`은 `ValueError`다(사전이 아님).
  4. `operation_id`, `request_sha256`, `idempotency_key`, `fact='succeeded'`, `evidence_ref`, `observed_at`을 갖춘 증거와 `succeeded=True`로 조정하면 `status`가 `confirmed`다.
  5. 만료 시각 `2000-01-01`인 허가로 `validate_operation`하면 `ValueError`다.
  6. `http://x@127.0.0.1:...` 형태의 URL과 `/ok/%2e%2e/outside` 경로는 `prepare_operation`에서 `ValueError`다.
- 대역: `transport` 람다(시간 초과), `persist` 항상 참.
- 비고: 모든 음성 단언이 예외 유형만 본다. 실제 HTTP 전송은 일어나지 않는다.

### `test_redirect_and_stale_ledger` (행 59–62)
- 성질: 원장 저장이 거부되면 전송하지 않고 실패하며, 서버의 재지정 응답은 따라가지 않고 거부된다.
- 준비: 빈 본문 GET `/ok` 조작.
- 실행: `persist`가 `False`를 돌려주는 실행, 이어서 `persist`가 참인 실행. 둘째는 실제 서버에 GET을 보내고 302를 받는다.
- 단언: 두 실행 모두 `ValueError`다. 첫째는 첫 저장에서 나는 원장 거부(제품 문구 `operation ledger is stale; ...`), 둘째는 `_NoRedirect.redirect_request`가 던지는 `redirect forbidden`이 전송 `try`의 잡는 목록(`TimeoutError`, `URLError`, `OSError`)에 없어 그대로 올라온 것이다. 메시지는 단언하지 않는다.
- 대역: `persist` 람다 두 가지.
- 비고: 실제 루프백 HTTP 서버를 쓴다.

### `test_tampered_key_and_terminal_persist` (행 63–66)
- 성질: 멱등 키가 바뀐 조작은 검증에서 거부되고, 자격 증명 환경변수가 없으면 전송하지 않고 대기 사유를 저장한 준비 상태로 끝난다.
- 준비: 빈 본문 POST 조작 둘. 첫째는 `idempotency_key`를 `'bad'`로 바꾼다. 둘째 전에 `os.environ`에서 `EXT_TEST_KEY`를 뺀다(`setUp`의 `patch.dict`가 시험 뒤 복원한다).
- 실행: 첫째에 `validate_operation`, 둘째에 `execute_operation`.
- 단언: 첫째는 `ValueError`(제품 문구 `request bytes or idempotency key changed`, 미단언). 둘째의 반환 `status`가 `prepared`, `transmitted`가 거짓이고, 마지막 저장 기록의 `waiting_reason.kind`가 `credential_unavailable`이다.
- 대역: `persist`는 기록을 모으는 람다.
- 비고: 이름의 "terminal persist"는 자격 증명 부재로 끝난 실행의 마지막 저장 기록을 가리킨다. 저장 실패를 다루는 시험은 행 71의 시험이다.

### `test_stop_before_send_is_explicitly_untransmitted` (행 67–69)
- 성질: 전송 전에 정지가 요청되면 조작은 명시적으로 미전송인 `cancelled`가 된다.
- 준비: 빈 본문 POST 조작.
- 실행: `should_stop=lambda: True`로 `execute_operation`.
- 단언: `(status, transmitted)`가 `('cancelled', False)`다.
- 대역: `persist` 항상 참, `should_stop` 항상 참.

### `test_terminal_persist_failure_is_not_returned_as_committed_success` (행 71–78)
- 성질: 확인 결과의 저장이 실패하면 성공으로 반환하지 않으며, 남은 보냄 표지는 복구하면 `unknown`이 되어 재전송이 막힌다.
- 준비: 본문 키가 없는 POST 조작. `persist`는 `status='confirmed'` 기록에만 `False`를 돌려주고 나머지는 모은다.
- 실행: `execute_operation`(실제 서버에 POST가 전송된다), 마지막으로 저장된 기록에 `recover_operation`, 그 결과로 다시 `execute_operation`.
- 단언: 첫 실행이 `ValueError`다. 복구 결과의 `status`가 `unknown`이다. 복구 결과의 재실행이 `ValueError`다.
- 대역: `persist` 함수.
- 비고: 실제 루프백 HTTP 서버를 쓴다. 마지막 저장 기록은 `status='prepared'`, `transmitted=True`인 보냄 표지이며, 제품의 `recover_operation`은 이를 불확실로 바꾼다.

### `test_fresh_revocation_before_send_prevents_transport` (행 80–84)
- 성질: 준비 기록을 저장한 뒤 전송 직전에 다시 읽은 허가가 철회되어 있으면 전송하지 않는다.
- 준비: 본문 키가 없는 POST 조작. `current`는 허가의 사본이고, `persist`가 호출될 때 `current['status']`를 `revoked`로 바꾼다.
- 실행: `current_grant=lambda _: current`, 전송 대역을 준 `execute_operation`.
- 단언: `ValueError`가 나고(메시지 미단언; 제품의 둘째 `validate_operation`이 `grant is inactive`를 던진다) 전송 대역이 불리지 않았다(`sent == []`).
- 대역: `persist`(철회를 일으킴), `current_grant`, `transport`(호출 기록).

### `test_retries_need_exact_nonexpired_idempotency_evidence` (행 86–92)
- 성질: 불확실한 조작의 재시도는 정확한 요청 해시와 멱등 키에 묶인 증거가 있어야 준비되고, 준비된 재시도는 실제로 전송되어 확인된다.
- 준비: 본문 키가 없는 POST 조작을 시간 초과 전송으로 `unknown`으로 만든다. 증거는 `kind='verified_idempotency'`, 같은 해시·키, `valid_until='2099-01-01T00:00:00Z'`, `evidence_ref`.
- 실행: `request_sha256`만 `'wrong'`으로 바꾼 증거로 `prepare_retry(source='adapter')`, 올바른 증거로 `prepare_retry`, 그 재시도를 `execute_operation`(실제 서버에 POST).
- 단언: 틀린 해시는 `ValueError`다. 올바른 재시도의 실행 결과 `status`가 `confirmed`다.
- 대역: 첫 전송의 `transport` 람다(시간 초과), `persist` 항상 참.
- 비고: 이름은 "만료되지 않은" 증거를 말하지만, 만료된 증거의 거부(`idempotency evidence expired`)는 단언하지 않는다. 단언하는 음성 경우는 해시 불일치 하나다. 실제 루프백 HTTP 서버를 쓴다.

### `test_credential_resume_loopback_clears_wait_and_preserves_identity` (행 94–106)
- 성질: 자격 증명이 없어 대기한 조작은 자격 증명이 생기면 같은 신원(ID, 요청 해시, 멱등 키)으로 재개되어 대기 사유 없이 확인되고, 확인된 조작은 다시 보낼 수 없다.
- 준비: `kind='http'`, `reuse='reusable'`을 더한 허가(제품의 `grant_scope_reason` 경로를 탄다). ID `OP-resume`, 본문 `credential-resume`인 POST 조작. `runtime={'external_operations': {}, 'executions': {}}`와 그 안에 조작을 기록하는 `persist`.
- 실행: `patch.dict(os.environ, {}, clear=True)` 안에서 첫 실행, 그 밖(`setUp`의 `EXT_TEST_KEY` 복원 상태)에서 대기 결과로 둘째 실행(실제 서버에 POST), 확인 결과로 셋째 실행.
- 단언: 첫 결과의 `waiting_reason.kind`가 `credential_unavailable`이다. 둘째 결과의 `status`가 `confirmed`이고 `waiting_reason` 키가 없으며, `id`, `request_sha256`, `idempotency_key`가 원 조작과 같다. 셋째 실행은 `ValueError`다(제품 문구 `recorded transmission requires recovery before another send`, 미단언).
- 대역: 환경변수 패치, `runtime`에 쓰는 `persist`.
- 비고: 행 95에서 이미 import한 `patch`를 함수 안에서 다시 import한다. 실제 루프백 HTTP 서버를 쓴다.

## 관계

- 같은 제품 기능을 다른 층에서 보는 모듈: `test_external_operations`(`foundation` 조각)는 외부 조작 기록의 도메인 규칙을, 엔진 층의 외부 행동 경로는 허가·거버넌스 시험(`test_governance`, `test_governance_engine`)이 다룬다.
- 픽스처 의존: `provider_fixtures.HTTPFixtureHandler` 하나. 이 처리기의 POST 201과 GET 302 응답이 확인 경로와 재지정 거부 경로를 만든다.
- 이 모듈의 특징: 실제 네트워크 대신 루프백 HTTP 서버를 시험마다 띄운다. 원격 서비스에는 연결하지 않는다. 첫 시험만 opener를 대역으로 바꿔 보낸 바이트를 직접 본다.
- 겹침과 보완: 재전송 금지는 `unknown`(행 49), 복구된 보냄 표지(행 71), 확인 뒤(행 94) 세 경우로 나뉜다. 자격 증명 부재는 대기 기록(행 63)과 재개(행 94)로 나뉜다.
