# test_control_transport

| 항목 | 값 |
|---|---|
| 조각 | `foundation` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_control_transport.py` (433행) |
| 클래스 / 테스트 | 3 / 18 |
| 시험 대상 제품 코드 | `do_math/control_transport.py`의 `ControlTransport`(`issue`, `receive`, `pump`, `_pump_paths`, `close`, `request_self_check`, `worker_submit`, `worker_receipt`, `wait_receipt`, `worker_self_check`, `validate_binding`, `mcp_server_config`, `_receipt`, `_reject_unvalidated`, `_reject_delivery_file`), 모듈 함수 `_json`, `_is_open`, `_decode_json`, `_create_json_once`, `_mcp_server`, `main`, 상수 `SELF_CHECK_TOOL`; `do_math/file_io.py`의 `check_path_segment`, `file_fingerprint`, `fingerprint_settled`, `RACY_NS` |
| 사용하는 픽스처 모듈 | 없음 |
| 격리 표지 | 없음 |
| 시작 상태 | 네 단 밖. 임시 폴더 위의 실제 전송 파일(`inbox`, `outbox`, `worker-inbox`, `binding.json`, `state.json`)을 쓴다. 첫 시험은 메모리 전용 전송이다. 세 시험은 실제 Python 자식 프로세스(MCP 서버 또는 `python -c`)를 띄운다. 두 시험은 실제 스레드를 쓴다 |

## 목적

모듈 docstring은 "The execution control transport: requests and receipts, previews, and the worker-side MCP child over real files."이다. 시험 대상 `control_transport.py`의 docstring에 따르면 전송 파일은 연구 상태가 아니라 배달 재료다. 엔진이 유일한 권위이므로, 엔진이 요청을 검증하고 권위 레코드를 공개한 뒤에야 전송이 `accepted`를 낸다. 지역 능력(capability)은 협조하는 작업자를 실행에 묶을 뿐 같은 사용자 사이의 강한 인증이 아니다. 이 모듈이 지키는 계약은 다음과 같다.

- 잘못된 요청은 조회 가능한 거절 영수증을 남기고, 뒤 요청을 막지 않는다.
- 요청 ID는 모든 전송에 걸쳐 한 번만 쓰인다. 같은 ID를 다른 내용으로 쓰면 충돌로 거부한다.
- 파일 이름에 경로, 글롭, 장치 이름을 쓸 수 없다. 전송 루트 밖의 결합은 적재하지 않는다.
- 닫힌 전송은 읽지 않되, 닫기와 경합한 배달에는 `closed`로 답한다.
- 최종 영수증을 받은 배달은 지문이 바뀌기 전까지 다시 읽지 않는다.
- 미리보기는 재생할 수 있지만 공개 영수증이 될 수 없다.
- 받았지만 공개되지 않은 요청은 복구 때 공개된다.
- 작업자 쪽 MCP 자식과 직접 자식 프로세스가 실제 파일로 왕복한다.

## 모듈 수준 요소

- 행 17: `sys.path.insert(0, str(Path(__file__).resolve().parents[1]))`로 `scripts/` 폴더를 경로 앞에 넣는 공통 머리다.
- 행 18: `from do_math import control_transport as transport_module`. 모듈 함수 `_json`, `_is_open`, `_decode_json`을 `patch.object`로 바꾸고 상수 `SELF_CHECK_TOOL`을 읽을 때 이 이름을 쓴다.
- 행 432–433: 직접 실행하면 `unittest.main()`을 부른다.

## ControlTransportIoTests (행 22–282)

- 기반: `unittest.TestCase`. 표지, 클래스 속성, 도우미가 없다.
- `setUp` (행 23–29): 임시 폴더를 만들고 `addCleanup`으로 정리를 등록한다. `ControlTransport(root / "transport")`를 `self.transport`에 두고, `issue("EX-transport", "GR-transport")`로 결합 `self.binding`과 그 끝점 폴더 `self.endpoint`를 얻는다. 발급은 끝점 아래에 `inbox`, `outbox`, `worker-inbox`, `worker-outbox`, `binding.json`, 그리고 `state.json`(`open`)을 만든다.

### `test_nonstring_control_fields_reject_without_breaking_later_requests` (행 31–52)
- 성질: `transport_id`나 `kind`가 문자열이 아닌 요청은 엔진에 닿지 않고 거절된다. 거절은 기록되어 같은 요청의 재생에 같은 영수증을 주며, 뒤따르는 정상 요청의 처리를 막지 않는다.
- 준비: 루트 없는 메모리 전용 `ControlTransport()`와 그 결합. 게시 콜백 `publish`는 받은 요청 ID를 `published`에 기록하고 `{"state": "rejected", "reason": "fixture receiver"}`를 돌려준다. `subTest(field=..., value=...)` 네 경우는 필드 `transport_id`와 `kind` 각각에 값 `[]`와 `{}`를 넣은 것이다.
- 실행: 각 경우 `transport.receive(request, publish=publish)`를 두 번 부른다. 끝으로 정상 요청 `valid-after-errors`를 받는다.
- 단언: 각 경우 첫 영수증의 `state`가 `"rejected"`이고, 재생 영수증이 첫 영수증과 같다(주석 "The rejection is recorded: the same request replays it."). 네 경우 뒤 `published`가 비어 있다. 정상 요청의 영수증 `reason`이 `"fixture receiver"`이고, `published`가 `["valid-after-errors"]`다.
- 대역: 게시 콜백.
- 비고: `transport_id`가 문자열이 아니면 제품은 발신자를 `None`으로 두고, 거절을 `(None, request_id)` 키로 메모리에 기록한다(`_reject_unvalidated`). 재생 때는 `_receipt`가 모든 전송의 기록에서 같은 ID를 찾아 돌려준다. 거절 사유 문구는 단언하지 않는다.

### `test_competing_different_payloads_cannot_both_submit` (행 54–96)
- 성질: 같은 요청 ID로 내용이 다른 두 제출이 동시에 경합하면, 하나만 제출되고 다른 하나는 내용 충돌 오류를 받는다. 저장된 내용으로 다시 제출하면 멱등하게 `submitted`다.
- 준비: 수신함의 `race-one.json` 경로. `threading.Barrier(2)`와 스레드별 표지. `transport_module._json`을 감싼 `synchronized_json`은 그 경로를 읽어 "없음"을 본 첫 순간에 장벽에서 기다린다. 그래서 두 스레드가 모두 파일이 없음을 본 뒤에야 쓰기로 넘어간다.
- 실행: 두 스레드가 `ControlTransport.worker_submit(binding, request_id="race-one", kind="submit_intent", payload={"manifest": ["first.json"/"second.json"]})`를 부른다. 예외는 결과 목록에 담는다. `join(timeout=15)`로 기다린다.
- 단언:
  - 두 스레드가 모두 끝났다(`"race reproduction deadlocked"`).
  - 사전 결과가 1개이고 `ValueError`가 1개다. 오류 문자열에 `"different content"`가 있다.
  - 수신함 파일의 `request_id`가 제출 결과의 `request_id`와 같다.
  - 저장된 `payload`로 다시 제출하면 `state`가 `"submitted"`다.
- 대역: `patch.object(transport_module, "_json", side_effect=synchronized_json)`. 실제 스레드 둘과 실제 파일을 쓴다.
- 비고: 제품의 `_create_json_once`는 임시 파일을 `os.link`로 최종 이름에 거는데, 이미 있으면 `FileExistsError`로 실패한다. 그래서 동시 쓰기에서 하나만 이긴다. 진 쪽은 다시 읽은 내용이 자기 요청과 달라 `"request_id was already submitted with different content"`를 받는다. 장벽 상한은 10초, 스레드 대기 상한은 15초다.

### `test_file_identifiers_reject_path_glob_and_windows_device_names` (행 98–113)
- 성질: 요청 ID와 자기 점검 ID는 하나의 안전한 파일 이름이어야 한다. 경로 이동, 구분자, 글롭 문자, Windows 장치 이름, 끝 점은 모든 입구에서 거부된다.
- 준비: 잘못된 이름 일곱 개. `../escape`, `part/name`, `part\name`, `wild*card`, `query?`, `CON`, `trail.`이다.
- 실행: 이름마다 `subTest`로 네 입구를 부른다. 요청 ID로 `worker_submit`과 `worker_receipt`를, 자기 점검 ID로 `self.transport.request_self_check`와 `ControlTransport.worker_self_check`를 부른다.
- 단언: 모든 호출이 `ValueError`를 메시지 조각 `"safe file name"`으로 낸다.
- 대역: 없음.
- 비고: 제품의 `_require_file_name`은 `file_io.check_path_segment`(빈 이름, `.`/`..`, 끝의 점·공백, 구분자, `<>:"|?*`, 제어 문자, 예약 장치 이름)에 `[`와 `]` 거부를 더하고, 실패를 `"<이름> must be a safe file name component"`로 바꾼다. 이 시험은 `[`와 `]`를 넣지 않으므로 그 추가 규칙은 보지 않는다.

### `test_transport_id_cannot_load_a_binding_outside_the_transport_root` (행 115–135)
- 성질: `transport_id`에 경로 이동(`../outside`)을 넣어 전송 루트 밖의 가짜 결합을 적재하게 할 수 없다. 그 요청은 엔진에 닿지 않고 거절되며, 밖의 끝점에 영수증을 쓰지 않는다.
- 준비: 루트 밖 `outside/endpoint`에 네 하위 폴더와 `state.json`(`open`)을 만든다. `outside/binding.json`에는 원래 결합에서 `transport_id="../outside"`, `endpoint`를 밖으로 바꾼 가짜 결합을 쓴다. 요청은 그 결합의 네 필드에 `request_id="safe-request"`와 `submit_intent`를 붙인 것이다.
- 실행: 새 `ControlTransport(root / "transport").receive(request, publish=...)`. 게시 콜백은 받은 값을 기록하고 수락을 돌려준다.
- 단언: 영수증 `state`가 `"rejected"`이고 `reason`에 `"transport_id"`가 있다. 게시 기록이 비어 있다. `outside_endpoint/outbox/safe-request.json`이 없다.
- 대역: 게시 콜백.

### `test_pump_reads_only_open_transports_and_close_answers_a_raced_delivery` (행 137–149)
- 성질: 전송을 닫을 때 그 수신함에 이미 도착한 배달은 `closed` 영수증을 받는다. 닫힌 뒤 도착한 배달은 어떤 전송 객체의 펌프도 읽지 않는다.
- 준비: 같은 루트에 둘째 전송 `EX-closed`를 발급하고, 그 수신함에 `raced.json`을 직접 쓴다.
- 실행: `self.transport.close(closed, reason="execution ended")`. 이어서 수신함에 `late.json`을 쓰고, 기존 객체와 새 객체로 각각 `pump(refuse)`를 부른다. `refuse`는 불리면 실패시키는 콜백이다.
- 단언: `worker_receipt(closed, "raced").state`가 `"closed"`다. 두 펌프가 모두 `[]`를 돌려준다. `late`의 영수증은 `None`이다.
- 대역: 실패 콜백.
- 비고: `close`는 `state.json`을 `closed`로 바꾼 뒤, 수신함의 배달을 게시자 없이 받아 `closed` 영수증을 쓴다. 새 객체는 첫 펌프에서 `binding.json`이 있는 전송 가운데 `state.json`이 `open`인 것만 연 전송으로 센다.

### `test_open_transports_are_read_at_the_first_pump_not_at_construction` (행 151–164)
- 성질: 전송 객체는 생성할 때 디스크의 전송 상태를 읽지 않는다. 첫 펌프에서 읽으며, 그 사이에 그 객체로 발급하거나 닫은 전송도 반영한다.
- 준비: `_is_open`을 불리면 `AssertionError("constructor read a transport")`를 던지게 패치한 채 `later = ControlTransport(root / "transport")`를 만든다. 패치를 푼 뒤 `later`로 `EX-later`를 발급하고, `EX-closed`를 발급해 닫는다. 세 결합(`setUp`의 것, 새로 연 것, 닫은 것)의 수신함에 각각 `first-open`, `second-open`, `after-close` 요청을 쓴다.
- 실행: `later.pump(...)`. 콜백은 요청 ID를 기록하고 거절을 돌려준다.
- 단언: 기록된 ID를 정렬하면 `["first-open", "second-open"]`이다.
- 대역: `_is_open` 패치(생성 중에만), 게시 콜백.
- 비고: 주석(154행)은 첫 펌프 전에 이 객체로 발급하고 닫은 전송을 가리킨다. 제품 생성자 주석은 "The set is read from disk at the first pump: commands that never pump read no transport."다.

### `test_request_id_rejected_without_engine_record_stays_taken_in_every_transport` (행 166–181)
- 성질: 엔진이 기록을 남기지 않은 조기 거절도 전송의 영수함에 남아 그 요청 ID를 점유한다. 다른 전송이 같은 ID를 다른 내용으로 쓰면, 기억이 없는 새 전송 객체도 디스크에서 그것을 찾아 엔진에 닿기 전에 거부한다.
- 준비: `setUp`의 수신함에 `shared` 요청(`draft_path="a.json"`)을 쓰고, 거절을 돌려주는 콜백으로 펌프한다. 둘째 전송 `EX-other`의 수신함에 같은 ID의 다른 내용(`b.json`)을 쓴다.
- 실행: 새 `ControlTransport(root / "transport").pump(...)`. 콜백은 불리면 실패한다.
- 단언: `worker_receipt(other, "shared")`의 `(state, stage)`가 `("rejected", "delivery_validation")`이고, `reason`에 `"different content"`가 있다.
- 대역: 게시 콜백과 실패 콜백.
- 비고: 주석(167행과 176행)은 엔진이 조기 거절의 영수증을 기록하지 않으므로 전송의 영수함만이 ID를 점유하고, 새 객체는 첫 영수증을 디스크에서 찾아야 한다고 설명한다. 제품 `_receipt`는 발신자 자신의 영수증을 먼저 보고, 없으면 메모리의 모든 기록을, 그다음 루트 아래 모든 전송의 `outbox`를 존재 검사로 훑는다. 내용 해시가 다르면 `"request_id was reused with different content"`가 나고, `_pump_paths`가 그것을 배달 파일 거절(`stage="delivery_validation"`)로 바꾼다.

### `test_close_records_a_changed_redelivery_it_cannot_settle` (행 183–194)
- 성질: 닫기가 정리하는 수신함에 이미 영수증을 받은 뒤 내용이 바뀐 배달이 있으면, 닫기는 원래 영수증을 바꾸지 않고, 그 배달을 정리하지 못한 사실을 닫힌 상태에 기록한다.
- 준비: `worker_submit`으로 `changed`(`first.json`)를 제출하고, 사유 `fixture`의 거절로 펌프한다. 수신함 파일의 `first.json`을 `other.json`으로 바꿔 쓴다.
- 실행: `state = self.transport.close(self.binding, reason="execution ended")`.
- 단언: `worker_receipt(..., "changed").reason`이 여전히 `"fixture"`다. `state.json`의 내용이 돌려받은 `state`와 같다. `unsettled_deliveries`의 `source` 목록이 `["inbox/changed.json"]`이고, 첫 항목의 `reason`에 `"different content"`가 있다.
- 대역: 게시 콜백.
- 비고: 제품 주석은 "A changed redelivery keeps the receipt it already has; the closed state records why."다. 바뀐 배달은 `receive`에서 내용 충돌이 난다. 이어서 배달 파일 거절로 넘어가지만, 영수함에 이미 다른 단계의 영수증이 있어 다시 `"request_id was already received with different content"`가 나고, `close`가 그것을 모은다.

### `test_malformed_request_has_queryable_rejection_and_preserves_source` (행 196–218)
- 성질: JSON으로 읽을 수 없는 배달은 원 바이트를 보존한 채 조회 가능한 배달 검증 거절을 받는다. 같은 바이트의 재생은 같은 영수증을 주고, 바이트가 바뀌면 충돌로 거부되며 원 영수증은 유지된다.
- 준비: 수신함에 `malformed-one.json`으로 `b'{"request_id":'`를 쓴다.
- 실행: 펌프(콜백은 불리면 실패). 이어서 `worker_receipt`, `wait_receipt(..., 0)`, 재생 펌프를 부른다. 끝으로 파일을 `b'{"different":'`로 바꾸고 다시 펌프한다.
- 단언:
  - 결과가 1개다. 영수증은 `state="rejected"`, `stage="delivery_validation"`, `source_sha256`이 원 바이트의 SHA-256, `source="inbox/malformed-one.json"`이고, `reason`에 `"JSON"`이 있다.
  - 원 파일 바이트가 그대로다.
  - `worker_receipt`, `wait_receipt(…, 0)`, 재생 펌프의 첫 결과가 모두 같은 영수증이다.
  - 바뀐 바이트의 펌프는 `ValueError`(`"different content"`)를 전파한다. 그 뒤에도 `worker_receipt`가 원 영수증과 같다.
- 대역: 실패 콜백.
- 비고: 거절 사유는 `_decode_json`의 `"transport file ... is not valid UTF-8 JSON: ..."`이다. 바뀐 바이트의 오류는 `_reject_delivery_file`이 `except` 블록 안에서 던지므로 `pump` 밖으로 나온다.

### `test_concurrent_real_files_do_not_reproduce_old_permission_error` (행 220–261)
- 성질: 작업자 두 스레드가 실제 파일로 제출하고 엔진이 동시에 펌프해도, 파일 접근 경합으로 `PermissionError`를 비롯한 어떤 오류도 나지 않는다.
- 준비: 세 참여자의 `threading.Barrier(3)`, 멈춤 이벤트. 생산자 `producer(prefix)`는 장벽을 지난 뒤 `left-0`…`left-39`처럼 요청 40개를 차례로 제출하고, 예외를 `errors`에 담는다. 두 생산자는 데몬 스레드다(주석 "A broken I/O implementation must not keep the test process alive.").
- 실행: 주 스레드도 장벽을 지난 뒤, 생산자가 살아 있는 동안 0.01초 간격으로 `self.transport.pump(...)`(거절 콜백)를 부른다. 15초가 지나면 수신함 목록을 담은 `TimeoutError`를 기록하고 멈춘다. 펌프 예외도 기록하고 멈춘다. 끝나면 멈춤 이벤트를 세우고 스레드를 1초씩 기다린 뒤 한 번 더 펌프한다.
- 단언: 살아 있는 스레드가 없다. `errors`에 `PermissionError`가 없다. `errors`가 비어 있다.
- 대역: 거절 콜백. 실제 스레드와 파일을 쓴다.
- 비고: 이름의 "old permission error"는 과거에 있던 결함을 가리킨다. 원문과 제품 주석에는 그 결함의 내용이 적혀 있지 않다. 폴링 간격은 `time.sleep(.01)`, 상한은 15초다.

### `test_final_delivery_is_not_reread_until_its_fingerprint_changes` (행 263–282)
- 성질: 최종 영수증을 받은 배달은 파일 지문이 안정되고 바뀌지 않는 한 다시 읽거나 받지 않는다. 지문이 바뀌면 다시 읽고, 내용이 달라졌으면 충돌로 거부한다.
- 준비: `worker_submit`으로 `cached`(`first.json`)를 제출하고 파일의 원래 `stat`을 기록한다. `self.transport.receive`를 `wraps`로 감싸 호출 수를 센다. `file_io.RACY_NS`를 0으로 패치한다. 주석(270행)은 새 파일의 생성 시각을 늙게 할 수 없으므로 과거의 지문을 모두 안정된 것으로 본다고 설명한다.
- 실행: 감시 중인 `self.transport.pump`를 세 번 부른다. 첫 수신, `_decode_json`을 막은 재펌프, 내용과 수정 시각을 바꾼 뒤의 펌프다.
- 단언: 단계별로 확인하는 결과는 다음과 같다.
  1. 첫 펌프(거절 콜백)를 한다.
  2. `_decode_json`을 `AssertionError('final delivery reread')`로 패치한 채 다시 펌프하면, 결과가 첫 결과와 같다. `receive` 호출 수는 1이다.
  3. 파일 내용의 `first.json`을 `other.json`으로 바꾸고, `os.utime`으로 수정 시각을 1초 늦춘다. 펌프하면 `ValueError`(`"different content"`)가 나고, `receive` 호출 수는 2다.
- 대역: `patch.object(self.transport, 'receive', wraps=...)`, `patch.object(file_io, 'RACY_NS', 0)`, `_decode_json` 패치.
- 비고: 제품 `_pump_paths`는 최종 영수증(`accepted`, `rejected`, `closed`, `previewed`)을 받았고 지문이 안정되었으며 읽는 동안 지문이 바뀌지 않았을 때만 캐시한다. 캐시가 맞으면 영수증 사본을 돌려준다. `RACY_NS`는 기본 2초이고, 그보다 최근에 바뀐 지문은 캐시 근거가 되지 못한다.

## ControlPreviewTests (행 285–343)

`unittest.TestCase`를 그대로 상속한다. 표지, 클래스 속성, 훅, 도우미가 없다. 각 시험이 임시 폴더에 전송을 만든다.

### `test_preview_is_replayable_but_never_a_publication_receipt` (행 286–303)
- 성질: 제출 미리보기는 검사 결과만 담은 `previewed` 영수증을 받고, 공개 식별자나 스냅숏을 싣지 않는다. 같은 미리보기는 새 전송 객체에서도 다시 검사하지 않고 같은 영수증으로 재생된다.
- 준비: `issue("EX-preview", "GR-preview")`. `worker_submit`으로 `preview-1`(`kind="submission_preview"`, `output_sha256`)을 제출한다. 콜백 `inspect`는 호출을 기록하고 `{"state": "previewed", "result": {"valid": True, "snapshot": "checked-snapshot"}}`을 돌려준다.
- 실행: `transport.pump(inspect)`, `wait_receipt(binding, "preview-1", 0)`, 새 `ControlTransport(directory).pump(...)`(실패 콜백).
- 단언: 영수증의 `state`가 `"previewed"`이고 `result.valid`가 참이다. 최상위에 `publication_id`와 `snapshot` 키가 없다. `wait_receipt`와 새 객체의 첫 펌프 결과가 같은 영수증이다. 콜백 호출이 1회다.
- 대역: 검사 콜백과 실패 콜백.
- 비고: 제품 `_store`는 미리보기 영수증에 `reason`과 `result`만 복사한다. 결과 안의 `snapshot`은 `result` 아래에 남을 뿐 최상위로 올라오지 않는다. 시험은 그것을 최상위 부재로 확인한다.

### `test_preview_cannot_be_misreported_as_accepted_publication` (행 305–312)
- 성질: 미리보기 요청에 게시자가 공개된 수락을 돌려주면 전송은 그것을 받아들이지 않고, 영수증도 남기지 않는다.
- 준비: 전송과 결합. 결합에 `request_id="preview-1"`, `kind="submission_preview"`, 빈 `payload`를 붙인 요청.
- 실행: `transport.receive(request, publish=lambda _: {"state": "accepted", "published": True, "snapshot": "head"})`.
- 단언: `ValueError`의 메시지 조각이 `"without publication"`이다. 제품 문구는 `"preview must return a check result without publication"`이다. `worker_receipt(binding, "preview-1")`가 `None`이다.
- 대역: 게시 콜백.

### `test_real_mcp_child_delivers_preview_and_returns_its_structured_result` (행 314–343)
- 성질: 작업자 쪽 실제 MCP 서버 자식은 미리보기 종류를 제출 도구에 노출하고, 제출을 전송 파일로 전달하며, 엔진이 펌프한 미리보기 영수증의 구조화된 결과를 영수증 도구로 돌려준다.
- 준비: 전송과 결합. `transport.mcp_server_config(binding)`의 명령(`sys.executable`)과 인자(`control_transport.py mcp --endpoint=... ...`)로 `subprocess.Popen` 자식을 텍스트 모드 표준 입출력 파이프와 함께 띄운다. 지역 함수 `rpc(number, method, params)`는 JSON-RPC 한 줄을 쓰고 한 줄을 읽는다.
- 실행: 네 번의 RPC와 한 번의 펌프다.
  1. `initialize`(`protocolVersion` `2024-11-05`).
  2. `tools/list`.
  3. `tools/call control_submit`(`request_id="preview-mcp"`, `kind="submission_preview"`, `payload={"draft": "fixture"}`).
  4. 시험 프로세스에서 `transport.pump(...)`. 콜백은 `{"state": "previewed", "result": {"valid": False, "issues": ["stale input"]}}`을 돌려준다.
  5. `tools/call control_receipt`(`wait_seconds=0`).
- 단언: `control_submit`의 `inputSchema.properties.kind.enum`에 `submission_preview`가 있다. 제출 응답에 `error`가 없다. 영수증 응답의 `result.content[0].text`를 JSON으로 읽으면 `state`가 `"previewed"`이고 `result.issues`가 `["stale input"]`이다.
- 대역: 펌프 콜백. MCP 서버는 실제 자식 프로세스다.
- 비고: 실제 Python 자식 프로세스를 쓴다. `finally`에서 표준 입력을 닫아 서버 루프를 끝내고 `wait(timeout=10)`으로 기다린 뒤 파이프를 닫는다.

## ControlTransportTests (행 346–429)

`unittest.TestCase`를 그대로 상속한다. 표지, 클래스 속성, 훅, 도우미가 없다.

### `test_mcp_child_offers_the_self_check_tool_only_to_self_checking_executions` (행 347–368)
- 성질: MCP 자식은 자기 점검에 답하는 실행의 결합(`self_check=True`)에만 자기 점검 도구를 제공한다. 두 결합 모두 결합 검증을 통과한다.
- 준비: 한 전송에서 `self_check`가 참과 거짓인 결합 둘을 발급한다(`EX-True`, `EX-False`).
- 실행: 결합마다 `ControlTransport.validate_binding(binding, execution_id=...)`를 부른다. MCP 자식을 띄워 `tools/list`를 한 번 부르고 도구 이름 집합을 모은다.
- 단언: 참 결합의 도구 집합에서 거짓 결합의 도구 집합을 빼면 `{transport_module.SELF_CHECK_TOOL}`이다.
- 대역: 없음. 실제 자식 프로세스 둘을 쓴다.
- 비고: 주석(348행)은 연구 작업만 자기 점검에 답한다고 밝히며 `observations.tracker_config`를 가리킨다. 차집합 단언은 두 목록이 이 도구 하나만 다르다는 것까지 고정한다.

### `test_control_rejects_an_unconfirmed_boundary_and_request_id_reuse` (행 370–380)
- 성질: 진행 중인 호출이 있다고 보고하는 안전 경계 요청은 거절된다. 같은 요청의 재생은 같은 거절이다. 같은 ID를 다른 내용으로 다시 쓰면 충돌로 거부된다. 영수증에는 능력 비밀이 실리지 않는다.
- 준비: 전송과 결합. 결합에 `request_id="CT-1"`, `kind="safety_boundary"`, `payload={"inflight_calls": True}`를 붙인 요청.
- 실행: 게시자 없이 `transport.receive(request)`를 두 번 부른다. 이어서 `payload`를 `{"inflight_calls": False}`로 바꿔 부른다.
- 단언: 두 영수증의 `state`가 `"rejected"`다. 셋째 호출은 `ValueError`(`"different content"`)다. `worker_receipt(capability, "CT-1")`에 `capability` 키가 없다.
- 대역: 없음.
- 비고: 거절 사유는 `_validate_request`의 `"boundary report has an in-flight call"`이다. 시험은 사유 문구를 단언하지 않는다. 이름의 "unconfirmed boundary"는 `inflight_calls`가 `False`로 확인되지 않은 경계를 뜻한다.

### `test_received_but_unpublished_request_is_published_on_recovery` (행 382–395)
- 성질: 게시자 없이 받기만 한 요청(`received`)은 최종 영수증이 아니다. 복구된 새 전송 객체가 게시자와 함께 펌프하면 그 요청이 정확히 한 번 공개된다.
- 준비: 전송과 결합. `worker_submit`으로 `request-receive`를 제출한다.
- 실행: `transport.pump()`(게시자 없음). 이어서 새 `ControlTransport(root).pump(publish)`. 콜백은 호출을 기록하고 `{"state": "accepted", "published": True, "snapshot": "verified-CAS"}`를 돌려준다.
- 단언: 첫 펌프의 첫 영수증 `state`가 `"received"`다. 둘째 펌프의 첫 영수증 `state`가 `"accepted"`다. 콜백 호출이 1회다.
- 대역: 게시 콜백.
- 비고: 제품 `receive`는 이전 영수증이 있어도 그 상태가 최종이 아니면 계속 진행해 게시자를 부른다.

### `test_child_process_round_trips_submit_receipt_self_check_and_close` (행 397–429)
- 성질: 별도 프로세스의 작업자가 정적 메서드만으로 전송 파일을 통해 다음을 왕복한다. 제출, 영수증 조회, 자기 점검 요청의 폴링과 응답, 닫힌 뒤의 제출 거부다. 공개된 요청은 복구된 전송 객체에서 다시 공개되지 않는다.
- 준비: 지역 함수 `child(statement, binding)`은 `PYTHONPATH`에 `scripts/` 폴더를 앞세운 환경으로 `subprocess.run([sys.executable, "-c", statement, json.dumps(binding)], check=True)`을 돌리고, 표준 출력을 JSON으로 읽는다. 전송과 결합 `EX-1`/`GR-1`.
- 실행: 지역 함수 `child`로 작업자 쪽 정적 메서드(`worker_submit`, `wait_receipt`, `worker_self_check`)를 자식 프로세스에서 네 번 부르고, 시험 프로세스에서 `pump`, `request_self_check`, `close`, 닫힌 뒤의 `worker_submit`을 부른다.
- 단언: 단계별로 확인하는 결과는 다음과 같다.
  1. 자식이 `worker_submit(b, request_id='CT-1', kind='submit_intent', payload={'manifest': ['result.json']})`을 부른다. 결과 `state`가 `"submitted"`다.
  2. 시험 프로세스가 펌프한다. 콜백은 `snapshot="SN-1"`, `publication_id="PR-1"`인 수락을 돌려준다. 첫 영수증 `state`가 `"accepted"`다.
  3. 자식이 `wait_receipt(b, 'CT-1', 0)`을 부른다. 결과 `snapshot`이 `"SN-1"`이다.
  4. 새 `ControlTransport(root)`가 펌프한다(실패 콜백). 첫 영수증의 `publication_id`가 `"PR-1"`이다.
  5. `transport.request_self_check(binding, request={"self_check_id": "SC-1", "execution_id": "EX-1", "payload": {"obligation": "report scope"}})`를 부른다. 자식이 `worker_self_check(b, self_check_id='SC-1')`로 폴링하면 `payload.obligation`이 `"report scope"`다.
  6. 자식이 스키마에 맞는 자기 점검 응답을 `worker_self_check(..., response=...)`로 보낸다. 결과 `state`가 `"submitted"`다.
  7. 펌프한다. 마지막 영수증의 `kind`가 `"self_check_response"`다.
  8. `transport.close(binding, reason="execution ended")` 뒤, 시험 프로세스에서 `worker_submit(binding, request_id="CT-2", ...)`의 `state`가 `"closed"`다.
- 대역: 게시 콜백과 실패 콜백. 작업자는 실제 자식 프로세스(`python -c`) 네 번이다.
- 비고: 6의 자기 점검 응답은 `SELF_CHECK_RESPONSE_SCHEMA`의 필수 필드를 모두 갖춘다. 제품은 작업자 쪽(`worker_submit`)과 엔진 쪽(`_validate_request`, 발급된 요청의 존재)에서 두 번 검사한다. 8의 `closed`는 작업자 쪽 `worker_submit`이 `state.json`을 읽어 곧바로 돌려준 결과이며, 배달 파일을 쓰지 않는다.

## 관계

- 같은 제품 기능을 다른 층에서 검사하는 모듈:
  - `test_execution_lifecycle`의 `test_intent_stops_and_revokes_execution_authority_in_same_git_publication`은 전송의 수락 영수증이 실행 레코드와 한 Git 공개로 묶이는 것을 본다. 같은 모듈의 `test_accepted_output_requires_a_real_transport_receipt`도 실제 전송 영수증을 쓴다.
  - `test_owned_job_children`의 `test_local_control_receipt_remains_responsive_during_child_cpu_load`는 CPU 부하 아래에서 제출과 펌프가 응답하는지 본다.
  - `test_provider_final_contract`는 발급된 결합이 작업자 요청에 실리고 CLI 스키마를 대신하는 것을 본다. `test_execution_profiles`는 결합이 두 러너와 작업자 계약에 전달되는 것을 본다.
- 픽스처 의존: 없다. 모든 준비가 이 모듈 안에 있다.
- 이 모듈에만 있는 도우미: 테스트 안의 지역 함수 `synchronized_json`, `submit`, `producer`, `rpc`, `child`, 콜백 `publish`, `inspect`, `refuse`.
