# test_submission_tools

| 항목 | 값 |
|---|---|
| 조각 | `review` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_submission_tools.py` (703행) |
| 클래스 / 테스트 | 4 / 34 |
| 시험 대상 제품 코드 | `do_math/submission.py`의 `request_control`, `seal_submission`, `producer_check`, `_producer_check`, `install_tools`, `main`(설치된 `input/tools/check_submission.py`로 실행), `PREVIEW_CONTRACT_ID`; `do_math/control_transport.py`의 `ControlTransport`(`issue`, `pump`, `worker_receipt`, `mcp_server_config`, MCP 도구 `control_submit`·`control_receipt`·`submit_draft`); `do_math/context_store.py`의 `fit_context`; `do_math/engine.py`의 `ResearchEngine.run`, `process_controls`, `_context`, `_research_source_spec`, `_execution_profile`, `control`; `do_math/scheduled_operator.py`의 `recovery`, `OPERATOR_SCHEMA`; `do_math/governance.py`의 `authorize`; `do_math/knowledge.py`의 `assess_use`, `plan_impact`, `revision_roots`; `do_math/review_cycle.py`의 `record_turn` |
| 사용하는 픽스처 모듈 | `purpose_fixtures`(`ActivatedPurposeHarness`, `PurposeHarness`, `PurposeRunner`, `CheckedRunner`, `purpose_copy`, `common`, `parse_context`), `research_fixtures`(`await_control`, `await_stop`, `git_init`, `local_job_runner`, `seal_response`, `candidate`, `disposition`), `state_fixtures`(`ACTIVE_LEAN_COMMAND`) |
| 격리 표지 | 없음 |
| 시작 상태 | 1단(임시 작업 공간에 도구를 설치하고 제품 함수·명령을 직접 부름)이 21개다. 2단(`make_active`가 복원하는 `state_fixtures.active_instance`)이 8개다. 2단 위의 더 깊은 빌드(`purpose_fixtures.purpose_state`, `purpose_copy`)가 5개다 |

## 목적

모듈 docstring은 "실제 생산자 명령을, 공급된 독립 작업 공간에서 돌린다"고 밝힌다.

`submission.install_tools`는 작업자 작업 공간의 `input/` 아래에 네 가지를 설치한다.

- 엔진 코드를 뺀 `do_math` 판 zip(`tools/submission-support.zip`).
- 그 zip을 경로에 넣고 `submission.main`을 부르는 `tools/check_submission.py`.
- 고정 입력(`submission/context.json`, `schema.json`, `extensions.schema.json`).
- 문맥의 `submission_contract`. 여기에는 명령, 스키마 참조, 도구 digest, 한도, 버림용 `.scratch` 폴더가 적힌다.

작업자는 이 명령으로 초안을 스스로 검사하고(`--output`), 중앙에 미리보기나 제출을 요청하고(`--preview`, `--submit`과 `--wait-seconds`), 새 지식 ID를 받는다(`--new-knowledge-id`). 요청은 `ControlTransport`의 파일 전송이나 MCP 서버(`control_submit`, `control_receipt`, `submit_draft`)로 간다.

이 모듈은 네 무리로 나뉜다.

1. `LocalControlProtocolTests`: 실제 전송과 Git 저장소로 요청과 영수증 프로토콜을 본다.
2. `ProducerToolTests`: 설치된 검사 명령이 무엇을 거부하고 통과시키는지를 본다. 실제 엔진이 작업자 출력을 받는 경계도 함께 본다.
3. `OperatorProducerTests`: 설치 복구 운영자가 연구 제출 경로를 쓰지 않는지를 본다.
4. `ReviewFailureTests`: 검토와 실행 실패가 대기로 멈추고 저절로 재생성되지 않는지를 본다.

## 모듈 수준 요소

- 행 11: 스킬의 `scripts/` 폴더를 `sys.path` 맨 앞에 조건 없이 넣는 공통 경로 머리다.
- 행 12: `purpose_fixtures`를 `purpose`라는 이름으로 import한다. 기반 클래스(`purpose.ActivatedPurposeHarness`), 러너(`purpose.PurposeRunner`), 응답 조각(`purpose.common`)을 이 이름으로 쓴다.
- 행 2–18: 나머지 import다. 모듈 함수, 상수, `setUpModule`은 없다.
- 행 702–703: 직접 실행하면 `unittest.main(verbosity=2)`를 돈다.

## LocalControlProtocolTests (행 21–185)

- 기반: `unittest.TestCase`. 표지와 클래스 속성은 없다.
- `setUp` (행 56–80)은 앞의 세 테스트보다 뒤에 정의되어 있지만 모든 테스트의 시작 상태를 만든다. 순서는 다음과 같다.
  1. 임시 폴더를 만든다(`addCleanup`으로 정리). 작업 공간 `worker/`와 저장소 `repo/`를 둔다.
  2. `git_init(repo)`로 빈 Git 저장소를 만들고, `GitStateStore(repo, "RI-01ARZ3NDEKTSV4RRFFQ69G5FAV")`를 연다. `self.head = None`으로 둔다.
  3. `ControlTransport(root/"delivery")`에서 `issue("EX-worker", "GR-worker", workspace=...)`로 결속을 발급한다.
  4. maintenance 문맥(`AC-worker`, `EX-worker`, `control_binding`, `snapshot="fixed"`, 빈 목록들)과 `contracts.schema_for("maintenance")`로 `install_tools(workspace, context, schema, None)`을 부른다.
  5. 출력(`summary="Inspect only"`, `report="Inspected"`)을 `seal_response`하고, 그 정본 바이트를 `worker/.scratch/draft.json`에 쓴다.

  엔진은 없다. 게시자는 도우미 `publish_intent`가 대신한다. 준비의 단은 1단(제품 함수와 명령을 임시 작업 공간 위에서 직접 부름)에 실제 Git 저장소를 더한 것이다.
- 도우미:
  - `mcp(name, arguments)` (행 82–92): 실제 MCP 서버를 자식 프로세스로 한 번 띄운다.
    - `ControlTransport.mcp_server_config(self.binding)`의 명령과 인자로 `subprocess.run`을 부른다. 인자는 `control_transport.py mcp --<필드>=<값> ...`이고, 시간 상한은 30초다.
    - 표준 입력으로 JSON-RPC `tools/call` 요청 한 줄을 보낸다.
    - 종료 코드 0과 봉투에 `error`가 없음을 단언한다. 그 뒤 `result.content[0].text`를 JSON으로 해석해 돌려준다.
  - `publish_intent(request)` (행 94–105): 중앙 게시자의 대역이다.
    - 요청의 `draft_path`를 `seal_submission`으로 실제 봉인한다.
    - 봉인 artifact와 `receipt-check.json`을 `runtime/artifacts/<request_id>/` 아래에 `store.publish`로 게시하고, `self.head`를 갱신한다. 첫 게시에는 `research/transport-fixture.json`을 더한다.
    - 봉인이 통과하지 못하면 `{"state": "rejected", "reason": "Draft validation failed", "result": check}`를 돌려준다. 통과하면 `{"state": "accepted", "published": True, "snapshot": head}`를 돌려준다.
    - 반려여도 artifact는 게시된다.

### `test_a_corrected_draft_at_the_same_path_gets_a_new_submission_attempt` (행 22–32)
- 성질: 같은 경로의 초안을 고쳐 다시 제출하면 새 요청 ID의 새 시도가 된다. 앞의 반려는 뒤의 수락을 막지 않는다.
- 준비: 클래스 절의 `setUp`. 초안을 `b'{invalid json'`으로 바꾼다.
- 실행: `submission.request_control(workspace, '.scratch/draft.json', kind='submit_intent', wait_seconds=0)`을 부른다. 결속은 설치된 문맥의 `control_binding`에서 온다. 이어서 `transport.pump(self.publish_intent)`를 부른다. 초안을 원래 바이트로 되돌린 뒤 같은 두 호출을 되풀이한다.
- 단언: 첫 요청의 `worker_receipt(...)['state']`가 `'rejected'`다. 두 `request_id`가 다르다. 둘째 요청은 `'accepted'`다.
- 대역: `publish_intent`(게시자 대역).
- 비고: 제품 `request_control`의 주석("A locator is mutable; a corrected draft at the same path is a new call.")이 이 성질을 말한다.

### `test_sealed_submission_preserves_the_snapshot_read_log` (행 34–40)
- 성질: 중앙 봉인은 작업자가 읽기 도구로 남긴 스냅숏 읽기 기록을 `reads.jsonl` artifact로 보존한다.
- 준비: 클래스 절의 `setUp`. `checks/reads.jsonl`에 한 줄 `{"request": "DC-1", "status": "ok"}`를 쓴다.
- 실행: `seal_submission(workspace, '.scratch/draft.json', execution_id='EX-worker', ...)`.
- 단언: `artifacts['reads.jsonl']`이 로그 파일 바이트와 같다.
- 대역: 없음.

### `test_supplied_tool_generates_fresh_sibling_ids_without_publishing` (행 42–54)
- 성질: 설치된 검사 명령의 `--new-knowledge-id`는 부를 때마다 새 `KN-` ID를 출력한다. 이때 게시하지 않고 작업 공간에 파일도 남기지 않는다.
- 준비: 클래스 절의 `setUp`. 작업 공간의 모든 경로 목록을 떠 둔다.
- 실행: `subprocess.run([sys.executable, '-B', 'input/tools/check_submission.py', '--new-knowledge-id'], cwd=workspace, timeout=30)`을 두 번 부른다.
- 단언:
  - 종료 코드가 0이다.
  - `replacement_id`가 정규식 `^KN-[0-7][0-9A-HJKMNP-TV-Z]{25}$`(ULID 모양)에 맞고, 두 ID가 다르다.
  - `self.head`가 `None`이다.
  - 작업 공간 경로 목록이 호출 전과 같다.
- 대역: 없음.
- 비고:
  - 실제 자식 프로세스 둘을 띄운다.
  - 이 테스트에서 `self.head`를 바꿀 수 있는 것은 `publish_intent`뿐이고, 여기서는 그것을 부르지 않는다. 그래서 `head`가 `None`이라는 단언은 이 구성에서 자명하다. "게시하지 않음"의 실질은 작업 공간 목록 비교가 맡는다.

### `test_real_mcp_intent_and_receipt_share_preserved_git_evidence` (행 107–120)
- 성질: 실제 MCP 서버로 보낸 제출 의도와 받은 영수증은 같은 Git 증거를 가리킨다. 게시된 출력은 초안 바이트와 같다. 한 번 처리된 요청은 다시 게시되지 않는다.
- 준비: 클래스 절의 `setUp`. `producer_check(workspace, draft)`로 `raw_output_path`를 얻는다.
- 실행:
  - `mcp("control_submit", {"request_id": "CT-local", "kind": "submit_intent", "payload": {"draft_path": ...}})`.
  - `transport.pump(self.publish_intent)`.
  - `mcp("control_receipt", {"request_id": "CT-local", "wait_seconds": 0})`.
  - 끝으로 실패를 내는 게시자로 `pump`를 다시 부른다.
- 단언:
  - 제출 응답의 `state`가 `"submitted"`다. 펌프 영수증이 비지 않았고 모두 `accepted`다.
  - MCP 영수증은 `accepted`이고, `snapshot`이 `self.head`와 같다.
  - 저장소의 `runtime/artifacts/CT-local/output.json`이 초안 바이트와 같다.
  - 재펌프는 게시자를 부르지 않는다(부르면 `self.fail("A replay must not publish twice")`). 헤드도 그대로다.
- 대역: `publish_intent`.
- 비고: MCP 서버 자식 프로세스 둘과 Git을 실제로 쓴다.

### `test_mcp_configuration_preserves_leading_hyphen_tokens` (행 122–127)
- 성질: 전송 토큰이 하이픈으로 시작해도 MCP 서버 구성의 인자가 옵션으로 오해되지 않는다. 서버는 정상으로 답한다.
- 준비: 클래스 절의 `setUp` 위에서, `do_math.control_transport.token_urlsafe`를 `"-transport-token"`, `"-capability-token"`을 차례로 내는 대역으로 바꾼다. 그 상태로 `transport.issue("EX-worker", "GR-worker")`를 다시 불러 `self.binding`을 바꾼다. 작업 공간은 주지 않는다.
- 실행: `mcp("control_receipt", {"request_id": "CT-not-submitted", "wait_seconds": 0})`.
- 단언: 결과가 `None`이다(없는 요청). 도우미 `mcp` 안에서 종료 코드 0과 `error` 부재도 단언한다.
- 대역: `mock.patch("do_math.control_transport.token_urlsafe", side_effect=[...])`.
- 비고: 제품 `mcp_server_config`는 인자를 `--<필드>=<값>` 한 토큰으로 만든다. 그래서 값이 하이픈으로 시작해도 별도 인자가 되지 않는다.

### `test_submit_draft_mcp_derives_internal_evidence_from_one_path` (행 129–135)
- 성질: MCP `submit_draft` 도구는 초안 경로 하나만 받는다. 전송 inbox에 적히는 payload도 그 경로 하나다. 검사와 해시 같은 내부 증거는 중앙이 스스로 만든다.
- 준비: 클래스 절의 `setUp`.
- 실행: `mcp("submit_draft", {"draft_path": ".scratch/draft.json", "wait_seconds": 0})`, 이어서 `transport.pump(self.publish_intent)`.
- 단언: `delivery/<transport_id>/inbox/`의 첫 JSON 파일의 `payload`가 `{"draft_path": ".scratch/draft.json"}`과 정확히 같다. 결과의 `delivery.state`가 `"submitted"`다. 첫 펌프 영수증은 `"accepted"`다.
- 대역: `publish_intent`.
- 비고: MCP 서버 자식 프로세스를 실제로 쓴다. 서버의 `submit_draft`는 안에서 `submission.request_control`을 부른다.

### `test_installed_submit_command_waits_for_real_central_receipt` (행 137–154)
- 성질: 설치된 명령의 `--submit --wait-seconds`는 중앙 영수증이 실제로 올 때까지 기다린 뒤, 받아들임과 스냅숏을 출력하고 0으로 끝난다.
- 준비: 클래스 절의 `setUp`. 명령은 `submission_contract["command"]`에 `--output <초안 절대 경로> --submit --wait-seconds 20`을 더한 것이다.
- 실행: `subprocess.Popen(command, cwd=workspace)`로 띄운다. 25초 상한 안에서 `transport.pump(self.publish_intent)`를 0.02초 간격으로 되풀이한 뒤, `communicate(timeout=5)`로 출력을 받는다.
- 단언: 종료 코드가 0이다. 출력 JSON의 `delivery.state`가 `"accepted"`이고, `delivery.snapshot`이 `self.head`와 같다.
- 대역: `publish_intent`.
- 비고: 실제 자식 프로세스를 쓴다. 폴링 상한은 25초, 간격은 0.02초다. `finally`에서 남은 프로세스를 `kill`한다.

### `test_accepted_submission_is_unchanged_when_original_draft_changes_later` (행 156–166)
- 성질: 받아들인 제출의 Git 출력은 원본 초안이 뒤에 바뀌어도 그대로다.
- 준비: 클래스 절의 `setUp`. `producer_check`로 초안 경로를 얻고, 원래 바이트를 떠 둔다.
- 실행: `mcp("control_submit", {"request_id": "CT-changed", ...})`, `pump(self.publish_intent)`, `mcp("control_receipt", ...)`를 부른 뒤 초안을 `{"changed": true}`로 덮어쓴다.
- 단언: 영수증이 `"accepted"`다. `runtime/artifacts/CT-changed/output.json`이 원래 바이트와 같다.
- 대역: `publish_intent`.
- 비고: MCP 자식 프로세스 둘과 Git을 실제로 쓴다.

### `test_invalid_wait_budget_does_not_queue_a_request` (행 168–172)
- 성질: 음수, NaN, 무한대, 불리언 같은 잘못된 대기 예산은 요청을 큐에 넣기 전에 거부된다.
- 준비: 클래스 절의 `setUp`.
- 실행: 네 예산으로 `request_control(workspace, ".scratch/draft.json", kind="submit_intent", wait_seconds=budget)`를 부른다. 끝으로 실패를 내는 게시자로 `pump`를 부른다.
- 단언: 각 경우 `ValueError`가 난다. 유형만 확인하고 메시지(`"wait_seconds must be a finite nonnegative caller budget"`)는 고정하지 않는다. 펌프가 게시자를 부르지 않는다(부르면 `self.fail("Invalid budget queued a request")`).
- 대역: 없음.
- 비고: `subTest(budget=...)` 네 경우는 `-1`, `float("nan")`, `float("inf")`, `True`다. 마지막 펌프 확인은 `subTest` 밖에서 한 번 한다.

### `test_preview_is_an_explicit_nonpublication_control_request` (행 174–185)
- 성질: 미리보기는 명시적인 비게시 제어 요청이다. 전송은 게시자의 `previewed` 결과를 영수증으로 그대로 전하고, 저장소에는 아무것도 게시되지 않는다.
- 준비: 클래스 절의 `setUp`.
- 실행:
  - `request_control(workspace, ".scratch/draft.json", kind="submission_preview", wait_seconds=0)`.
  - `transport.pump(lambda request: {"state": "previewed", "result": result})`. `result`는 `contract_id=submission.PREVIEW_CONTRACT_ID`, `passed=False`, `authoritative=False`에 문제 하나를 담는다.
  - `mcp("control_receipt", ...)`.
- 단언: 요청 전달 `state`가 `"submitted"`다. 영수증 `state`가 `"previewed"`이고, `result`가 준 결과와 같다. `self.head`가 `None`이다.
- 대역: 람다 게시자.
- 비고: 주석대로 이 테스트는 전송 의미만 보며, 실제 영역 미리보기는 따로 검사한다(`test_submission_flow`의 미리보기 시험들).

## ProducerToolTests (행 188–465)

- 기반: `purpose.ActivatedPurposeHarness`. 상속 사슬은 `PurposeHarness`, 그 위의 `unittest.TestCase`다.
  - `ActivatedPurposeHarness.setUp`은 `install_adapter_fixture`로 `do_math.initialization.adapter_for`를 `FixtureAdapter`로 바꾼다.
  - `make_active(**config)`는 `restore_template(state_fixtures.active_instance, config=config)`의 사본에 `PurposeRunner`를 단 엔진을 연다(2단).
  - `purpose_copy`는 `purpose_state` 빌드의 사본을 연다.
  - `PurposeHarness.fixture_config`는 시나리오 설정이다(검토자 2, `lean_command=['test-double']` 등).
- 클래스 표지와 클래스 속성은 없다.
- `setUp` (행 189–195)은 `super().setUp()` 뒤에 새 임시 폴더를 `self.root`로 둔다. 주석대로 생산자 전용 검사는 여기에 작업 공간을 만들고, 엔진을 쓰는 검사는 `make_active`나 `purpose_copy`가 `self.root`를 복원 사본으로 바꾼다.
- 도우미:
  - `prepare(role="research_preparation", *, context_values=None, **configuration)` (행 283–296): 생산자 작업 공간 하나를 만든다.
    - 경로는 `self.root/<role>-producer-<번호>`다.
    - 문맥은 `AC-producer`와 `EX-producer`, `snapshot="fixed-producer-input"`, `observed_at="2026-09-23T00:00:00Z"`, `budget_unit="concurrent_sessions"`, 빈 목록들, `ensure_ontology`에서 얻은 종류 정의로 이루어진다. `context_values`로 덮어쓴다.
    - `install_tools(workspace, context, contracts.action_schema(action), configuration.get("max_artifact_bytes"))`를 부른다.
    - 문맥에 `submission_contract`가 생기고 그 `command`가 비지 않음을 단언한다.
    - 반환값은 `(None, workspace, context)`다.
  - `check_output(workspace, context, output, extension=None)` (행 298–313): 설치된 명령으로 초안 하나를 검사한다.
    - 출력의 사본을 만든다. `extension`이 주어지면 `activity-extensions.json`에 쓴다. `integration_bundles`가 없으면 `seal_response`한다.
    - 사본을 `.scratch/submission.json`에 쓴다.
    - `[*command, "--output", <초안>]`을 `subprocess.run(..., timeout=30)`으로 돈다.
    - 세 가지를 단언한다. 종료 코드가 0 또는 1이다. 종료 코드 0과 출력 JSON의 `passed`가 일치한다. 초안 바이트를 해석한 값이 사본과 같다("a validator cannot rewrite the author's meaning").
    - 반환값은 검사 결과 JSON이다.

### `test_revoked_original_grant_preserves_late_output_despite_alternative_grant` (행 197–224)
- 성질: 실행 도중 원래 grant가 취소되면, 같은 역할을 허가하는 다른 grant가 있어도 그 실행의 늦은 출력은 받아들여지지 않는다. 출력은 결과로 보존되고, 행동은 대기로 간다.
- 준비: 2단. `make_active(**fixture_config(scholarly_enabled=False))`로 연다.
  - 대기열을 maintenance 행동 `AC-revoked` 하나로 둔다.
  - maintenance 역할의 grant를 복사해 ID `ZZ-alternative`로 더하고 저장한다.
  - 러너는 `CheckedRunner(Runner())`다. 스크립트 `Runner.run`은 네 일을 한다.
    1. `on_started({"pid": 1})`를 부른다.
    2. 실행 중인 실행의 grant를 `control(repo, id, 'decision', config={'change': {'kind': 'revoke', ...}})`로 취소하고, `await_control`로 소유자 루프가 적용하기를 기다린다.
    3. grant를 뺀 행동이 `governance.authorize`로 여전히 허가됨을 단언한다. 곧 대체 grant가 실제로 있다.
    4. `report="Preserve the completed portion."`인 완료 출력을 돌려준다.
- 실행: `engine.run(max_steps=1)`.
- 단언:
  - `AC-revoked` 실행이 `ended`이고, `outcome`이 `output_accepted`가 아니다. `stop_requested`는 `'grant_revoked'`다.
  - `store.read(execution['result_ref'])`의 `output.report`가 보존 문구와 같다.
  - `AC-revoked`가 `waiting_actions`에 있다.
- 대역:
  - `CheckedRunner`. 모델 응답만 스크립트하고, 생산자 검사와 실제 제어 전송 제출은 그대로 쓴다.
  - 스크립트 `Runner`.
  - `local_job_runner`. `CheckedRunner.run`에 붙어 있으며, 호출마다 실제 Windows Job 자식 하나를 띄운다.
- 비고: `await_control`의 상한은 60초이고 0.01초 간격으로 폴링한다. 실제 Windows Job 자식 프로세스를 쓴다.

### `test_unsealed_invalid_runner_output_is_preserved_for_operational_review` (행 226–241)
- 성질: 출력 수리 한도가 0일 때 러너가 출력 검증 실패를 보고하면 세 가지가 일어난다. 실행은 미완료로 끝나고, 행동은 대기로 가며, 그 실행을 대상으로 한 운영 검토가 대기열에 오른다. 수리 재시도는 생기지 않는다.
- 준비: 2단. `make_active(**fixture_config(scholarly_enabled=False, max_output_repairs=0))`. 러너는 `CheckedRunner(Runner())`이고, `Runner`는 `status="failed"`, `output={}`, `error_kind="output_validation"`을 돌려준다.
- 실행: `engine.run(max_steps=1)`.
- 단언: 새 실행의 `outcome`이 `"execution_incomplete"`다. 그 행동 ID가 `waiting_actions`에 있다. 대기열에 `role == "operational_review"`이고 `target`이 그 실행인 행동이 있다. `repair`를 가진 행동은 대기열에 없다.
- 대역: `CheckedRunner`, 스크립트 `Runner`, `local_job_runner`(실제 Windows Job).
- 비고: `CheckedRunner`는 출력이 `None`이 아니면 제출 의도를 보낸다. 그래서 이 테스트의 빈 출력도 `seal_response`와 제출 경로를 지난다. 그 영수증의 상태는 단언하지 않는다.

### `test_local_call_timeout_parks_only_the_timed_out_request` (행 243–260)
- 성질: 한 호출이 로컬 호출 기한을 넘기면 그 요청만 대기로 멈춘다. 인스턴스는 일시정지되지 않고, 다른 독립 행동은 대기열에 남는다.
- 준비: 2단. `make_active(**fixture_config(scholarly_enabled=False, call_timeout_seconds=1))`. 주석대로 1초 기한은 시험 대상 호출에만 해당하고 활성화의 해석 호출에는 해당하지 않는다. 대기열에는 `AC-timeout`(maintenance)과 `AC-independent`(research_preparation)를 둔다. `Runner`는 1.05초 잠든 뒤 `await_stop(should_stop, 10)`이 참임을 단언하고 `status="stopped"`를 돌려준다.
- 실행: `engine.run(max_steps=1)`.
- 단언: 런타임 `status`가 `"paused"`가 아니다. `AC-timeout`이 `waiting_actions`에 있다. `AC-independent`가 대기열에 있다.
- 대역: `CheckedRunner`, 스크립트 `Runner`, `local_job_runner`(실제 Windows Job).
- 비고:
  - 기한을 넘기려고 고정 대기 `time.sleep(1.05)`를 쓴다.
  - 정지 판정은 `await_stop`으로 폴링한다. 상한은 10초, 간격은 0.01초다.

### `test_receiver_rejects_unknown_insight_kind_and_missing_evidence` (행 262–281)
- 성질: 수신자는 등록되지 않은 통찰 종류나 없는 증거 ID를 가진 `research_insights` 확장을 받아들이지 않는다. 실행은 미완료로 끝나고, 지식은 생기지 않으며, 출력은 비봉인 제출 artifact로 보존된다.
- 준비: 2단. 경우마다 `make_active(**fixture_config(scholarly_enabled=False, max_output_repairs=0))`로 새 사본을 연다. `Runner`는 `on_started` 뒤에 작업 공간의 `activity-extensions.json`에 통찰 하나를 쓰고 `candidates=[]` 출력을 돌려준다.
- 실행: `engine.run(max_steps=1)`.
- 단언: 새 실행의 `outcome`이 `"execution_incomplete"`이고, `instance["knowledge"]`가 `{}`다. `store.read(execution['submitted_output_ref'])`를 해석하면 출력과 같다. 거부 사유 문구는 고정하지 않는다.
- 대역: `CheckedRunner`, 스크립트 `Runner`, `local_job_runner`(실제 Windows Job).
- 비고:
  - `subTest(changes=...)` 두 경우는 `{"kind": "unregistered_kind"}`와 `{"evidence_ids": ["KN-missing"]}`다.
  - `submitted_output_ref`는 제품 `_receive_submission`의 비봉인 분기(`engine.py` 행 2271)에서만 기록된다. 그래서 이 단언은 중앙 제출이 받아들여지지 않아 비봉인 경로로 보존되었음을 함께 확인한다.

### `test_producer_checks_main_shape_and_preserves_precise_failure_coordinates` (행 315–322)
- 성질: 설치된 검사 명령은 주 출력의 모양을 검사한다. 필수 필드가 빠지면 불통과로 답하고, 문제 좌표에 그 필드 이름이 드러난다.
- 준비: 1단. 클래스 도우미 `prepare()`(research_preparation)를 쓴다. 유효한 출력은 `purpose.common(...)`에 `candidates=[]`를 더한 것이다.
- 실행: `check_output`으로 유효한 출력을 검사하고, `candidates`를 뺀 출력을 검사한다.
- 단언: 앞의 것은 통과한다. 뒤의 것은 불통과이고, `json.dumps(issues)`에 `"candidates"`가 든다.
- 대역: 없음. 명령은 실제 자식 프로세스다.
- 비고: 이름은 "정확한 실패 좌표의 보존"을 말하지만, 단언은 문제 목록의 직렬화에 필드 이름 문자열이 나오는지만 본다. 경로 값 자체는 비교하지 않는다.

### `test_producer_checks_used_sources` (행 324–327)
- 성질: 공급되지 않은 레코드(`KN-missing`)를 `used_sources`로 대면 생산자 검사가 불통과로 답한다.
- 준비: 1단, `prepare()`.
- 실행: `check_output(..., used_sources=["KN-missing"])`.
- 단언: `passed`가 거짓이다. 사유는 고정하지 않는다.
- 대역: 없음.

### `test_reference_support_includes_visible_execution_history_and_supplied_catalogs` (행 329–340)
- 성질: 생산자는 문맥에 보이는 이전 실행 ID와, 입력 초과로 작업 공간 파일에 옮겨진 공급 목록의 경로를 근거로 댈 수 있다.
- 준비: 1단. `prepare(context_values={...})`로 준비한다. 문맥에는 `preparation_history=[{"execution_id": "EX-earlier", ...}]`, `goal="g"`, 30000자의 `large_optional_evidence`가 든다. 이어서 `fit_context(context, max_bytes=20000, workspace=..., mandatory_keys=["goal", "action"])`를 부르고, 목록에서 `key == "kind_definitions"`인 행의 `path`를 얻는다.
- 실행: 두 근거마다 `check_output(..., used_sources=[reference])`.
- 단언: 두 경우 모두 통과한다.
- 대역: 없음.
- 비고: `subTest(reference=...)` 두 경우는 `"EX-earlier"`와, `fit_context`가 옮긴 종류 정의 목록의 경로다.

### `test_producer_checks_checkpoint_evidence_paths` (행 341–349)
- 성질: 작업 공간의 `checkpoint.json`이 존재하지 않는 증거 경로를 가리키면 생산자 검사가 불통과로 답하고, 문제에 그 경로가 드러난다.
- 준비: 1단, `prepare()`. `checkpoint.json`의 `evidence_paths`에 `"missing-proof.txt"`를 둔다. 나머지 필드(`current_claim`, `attempts`, `remaining_work`, `next_step`, `progress_state="ready_to_submit"`)는 채운다.
- 실행: `check_output`.
- 단언: `passed`가 거짓이고, 문제의 직렬화에 `"missing-proof.txt"`가 든다.
- 대역: 없음.

### `test_live_review_validates_sidecar_before_applying_continue` (행 351–368)
- 성질: 실시간 운영 검토의 응답에 잘못된 확장(등록되지 않은 통찰 종류)이 있으면, 그 검토의 `continue` 처분은 적용되지 않는다. 검토 실행은 미완료로 끝나고, 대상 실행에는 운영 계속 기록이 붙지 않으며, 그 검토의 운영 처분 레코드도 생기지 않는다.
- 준비: 2단 위의 더 깊은 빌드다. 주석대로 준비된 과제에서 시작하며, 그 작업의 실시간 검토가 대상이다.
  - `purpose_copy(self, purpose.PurposeRunner(observation="continue"), until="prepared", config=fixture_config(scholarly_enabled=False, tool_review_window_seconds=1))`로 연다.
  - `runner.answer`를 감싼다. `operational_review` 역할이면 작업 공간에 `kind="not_registered"` 통찰을 쓴 뒤 원래 답을 돌려준다.
- 실행: `self.drive(engine, predicate=...)`. 조건은 끝난 `operational_review` 실행이 생기는 것이다.
- 단언: 검토 실행의 `outcome`이 `"execution_incomplete"`다. 대상 실행에 `operational_continuation`이 없다. `operational_dispositions`에 `execution_id`가 검토 실행인 행이 없다.
- 대역: `PurposeRunner`(`observation="continue"`)와 감싼 `answer`. `PurposeRunner.run`의 `local_job_runner`가 실제 Windows Job을 띄운다.
- 비고: `drive`의 단계 상한은 45다. 흐름이 `paused`, `closed`, `waiting`으로 멈추면 실패를 낸다.

### `test_producer_checks_sidecar_kinds_references_and_self_repair` (행 370–379)
- 성질: 생산자 검사는 확장 파일의 통찰 종류와 증거 참조를 검사한다. 같은 작업 공간에서 확장을 고치면 다시 통과한다.
- 준비: 1단, `prepare()`. 통찰은 `kind="unregistered_kind"`, `evidence_ids=["KN-missing"]`이다.
- 실행: 확장 `{"research_insights": [insight]}`로 `check_output`을 부른다. 이어서 `kind="question"`, `evidence_ids=[]`로 고쳐 다시 부른다.
- 단언: 첫 검사는 불통과이고, 문제의 직렬화에 `"research_insights"`가 든다. 둘째 검사는 통과한다.
- 대역: 없음.
- 비고: 두 검사는 같은 작업 공간의 생산자 검사 사슬(`checks/.producer-head`)에 이어진다. 사슬 연결 자체는 단언하지 않는다.

### `test_empty_known_extension_family_remains_a_semantic_noop` (행 381–384)
- 성질: 빈 알려진 확장 계열(`knowledge_changes: []`)은 의미 없는 변경으로 통과한다.
- 준비: 1단, `prepare("maintenance")`. 출력은 `purpose.common(...)`에 `report`와 `remaining_work=[]`를 더한 것이다.
- 실행: 확장 `{"knowledge_changes": []}`로 `check_output`.
- 단언: 통과한다.
- 대역: 없음.

### `test_producer_receives_artifact_and_checkpoint_limits_and_excludes_disposable_scratch` (행 386–399)
- 성질: 생산자는 계약에서 artifact 한도와 체크포인트 한도를 받는다. 관찰 규칙 한도는 받지 않는다. 버림용 `.scratch`의 큰 파일은 한도 계산에서 빠지지만, 일반 출력 파일이 한도를 넘으면 불통과다.
- 준비: 1단, `prepare(max_artifact_bytes=100)`.
- 실행: `.scratch/disposable.bin`(101바이트)을 둔 채 `check_output`을 부른다. 이어서 `evidence.bin`(101바이트)을 더해 다시 부른다.
- 단언:
  - `limits.max_artifact_bytes`가 100이고, `limits.checkpoint_bytes`가 `4*1024*1024`다. `limits`에 `observation_rules_bytes` 키가 없다.
  - 첫 검사는 통과한다. 둘째 검사는 불통과이고, 문제의 직렬화에 `"evidence.bin"`이 든다.
- 대역: 없음.
- 비고: 체크포인트 한도 4 MiB는 제품 상수 `observations.CHECKPOINT_MAX_BYTES`의 값을 시험에 직접 적은 것이다.

### `test_producer_checks_live_checkpoint_but_not_a_rules_file` (행 401–411)
- 성질: 생산자 검사는 살아 있는 `checkpoint.json`의 모양을 검사한다. 남은 `observation-rules.json`은 일반 출력으로 다루어 규칙으로 검사하지 않는다.
- 준비: 1단, `prepare()`. `checkpoint.json`은 `{"current_claim":"unfinished schema"}`(필드 부족)다. `observation-rules.json`에는 잘못된 규칙 배열을 쓴다.
- 실행: `check_output`.
- 단언: 불통과다. 문제의 직렬화에 `"checkpoint.json"`이 들고, `"observation-rules.json"`은 들지 않는다.
- 대역: 없음.
- 비고: 주석(행 405)은 규칙은 자기 점검 응답으로만 바뀌며, 남은 규칙 파일은 일반 출력이라고 설명한다.

### `test_producer_checks_planning_population_and_exact_completion_criteria` (행 413–432)
- 성질: 연구 계획 역할의 생산자 검사는 두 가지를 본다. 하나는 도출된 준비 완료 과제 전부에 처분이 있는지다. 다른 하나는 과제를 완료로 판정할 때 완료 기준 항목의 처분을 요구하는지다.
- 준비: 1단. 과제 `TK-ready`는 `research_fixtures.candidate()`에 `revision=1`, `status="planned"`, 빈 결과를 더한 것이다.
- 실행: 세 번 검사한다.
  1. `prepare("research_plan", context_values={"tasks": [task], "ready_task_ids": [tid]})`에서 처분이 빈 계획 출력을 검사한다.
  2. 처분 `disposition(tid)`(`uncertainty=""`)를 넣고, 확장 `model_assessments` 하나를 더해 검사한다.
  3. 과제를 `waiting`으로 바꾸고 결과 하나를 붙인다. 새 작업 공간(`ready_task_ids=[]`)에서 `decision="completed"`, `item_dispositions=[]`인 `task_assessments`를 검사한다. 확장은 `{}`다.
- 단언:
  - 첫 검사는 불통과이고, 문제에 `"every derived-ready task"`가 든다.
  - 둘째 검사는 통과한다.
  - 셋째 검사는 불통과다. 사유는 고정하지 않는다.
- 대역: 없음.

### `test_supplied_checker_is_standalone_and_does_not_mutate_fixed_inputs` (행 434–450)
- 성질: 설치된 검사 도구는 엔진 코드 없이 독립으로 돈다. 검사는 고정 입력(`input/` 아래)을 바꾸지 않으며, 명령의 스크립트 경로는 작업 공간 안에 있다.
- 준비: 1단, `prepare()`. `input/` 아래 모든 파일의 sha256을 떠 둔다.
- 실행: zip 이름 목록을 읽고, `check_output`으로 유효한 출력을 검사한 뒤 해시를 다시 뜬다.
- 단언:
  - zip에 `do_math/engine.py`가 없고, `_engine.py`로 끝나는 이름이 없으며, `do_math/record_schemas/__init__.py`가 있다.
  - 검사가 통과한다.
  - 전후 해시 사전이 같다.
  - 명령의 `.py` 인자가 작업 공간 안으로 해석된다.
- 대역: 없음.
- 비고: 제품 `install_tools`의 주석대로 적용 콜백은 중앙에 남고 공유 검사 코드만 실린다. zip은 `engine.py`와 `*_engine.py`를 뺀다.

### `test_producer_check_reuses_the_prepared_tool_digest` (행 453–465)
- 성질: 생산자 검사는 준비 때 고정한 도구 digest를 재사용하며, 검사할 때 zip을 다시 읽지 않는다.
- 준비: 1단, `prepare()`. 출력을 `seal_response`하고 `.scratch/submission.json`에 쓴다.
- 실행: `submission.read_stable`을 `wraps`로 감싼 채, 프로세스 안에서 `submission._producer_check(workspace, ".scratch/submission.json", [])`를 부른다.
- 단언: 결과의 `tool_sha256`이 계약의 `tool_sha256`과 같다. `read_stable` 호출 가운데 첫 인자가 `submission-support.zip`으로 끝나는 것이 없다.
- 대역: `mock.patch.object(submission, "read_stable", wraps=submission.read_stable)`.
- 비고: 주석대로 준비가 digest를 고정하고 도구 호출은 zip을 다시 읽지 않는다. 제품 `_producer_check`의 주석 "Preparation fixed the support archive's digest; each check reuses it."과 같다.

## OperatorProducerTests (행 468–500)

- 기반: `purpose.ActivatedPurposeHarness`. 표지, 설정 훅 재정의, 도우미, 클래스 속성은 없다.

### `test_failure_recovery_preserves_a_structured_nonresearch_report` (행 469–500)
- 성질: 설치 복구 운영자(`scheduled_operator.recovery`)는 연구 제출 경로를 쓰지 않는다. 운영자 스키마의 구조화된 보고를 실행 출력으로 보존하되, 수리 성공으로 치지 않는다.
- 준비: 2단. `make_active(**fixture_config(scholarly_enabled=False, operator_enabled=True))`. 스크립트 `Runner.run`은 `@local_job_runner`로 감싸져 있으며 다음을 한다.
  - `on_started()`를 인자 없이 부른다. 그러면 실제 Windows Job이 시작된다.
  - `output_schema`가 `operator.OPERATOR_SCHEMA`임을 단언한다.
  - 프롬프트에 `"Synthetic launcher failure"`가 듦을 단언한다.
  - 작업 공간에 `input/submission/context.json`이 없음을 단언한다(메시지 "installation recovery must not acquire the research submission path").
  - 운영자 출력을 기록하고, `status="failed"`, `error_kind="output_validation"`으로 돌려준다.
- 실행: `patch.object(operator, "ModelRunner", Runner)` 안에서 `operator.recovery(repo, instance_id, self.root, failure={"kind": "engine_unavailable", "error": "Synthetic launcher failure"})`를 부른다.
- 단언:
  - 결과 `outcome`이 `"recovery_failed"`이고, 러너가 정확히 한 번 불렸다.
  - 저장소에서 다시 읽은 실행의 `output`이 기록한 출력과 같고, `outcome`은 `"execution_incomplete"`이며, `submission_receipt`가 없다.
  - 소유 활동의 `waiting.reason`이 `"recovery_failed"`다.
  - 인스턴스 지식이 엔진의 것과 같다.
- 대역: `mock.patch.object(operator, "ModelRunner", Runner)`와 `local_job_runner`(실제 Windows Job).
- 비고: 주석대로 스키마 검증은 `ModelRunner`의 몫이다. 이 픽스처는 그에 대응하는 실패한 실행을 보고할 뿐 수리 성공을 주지 않는다.

## ReviewFailureTests (행 503–699)

- 기반: `purpose.ActivatedPurposeHarness`. 표지는 없다.
- 클래스 속성 `CONFIG` (행 508): `purpose.PurposeHarness.fixture_config(scholarly_enabled=False, lean_command=list(ACTIVE_LEAN_COMMAND))`다. 주석(행 504–507)은 이 흐름이 지식을 형식 검사하므로, 형식 검사가 시드의 활성 신뢰 환경 명령(`state_fixtures.ACTIVE_LEAN_COMMAND`)을 쓰도록 고정한다고 설명한다.
- 설정 훅은 재정의하지 않는다. 기반의 `setUp`(어댑터 패치)을 쓴다.
- 도우미:
  - `make_active` (행 510–511): 기반의 `make_active`를 `CONFIG`로 부른다(2단). 인자를 받지 않는다.
  - `make_review` (행 513–516): docstring은 "실제 과제 흐름이 식별 검토 주기를 연 뒤의 같은 활성 상태"라고 말한다. `purpose_copy(self, purpose.PurposeRunner(), until="review", config=CONFIG, external_policy="explicit_grants", signed=False)`로 연다. 2단 위의 더 깊은 빌드다.
  - `review_is_next(engine)` (행 519–523): 정적 메서드다. 검토 주기가 있고 대기열 첫 행동이 `identity_review`일 때 참이다. 주석은 운영 역할이 슬롯 없이 배정되므로(decision 4) 들여온 지식이 대기열에 올린 계획이 먼저 돌며, 이 검사들은 검토가 다음 차례일 때 시작한다고 설명한다.
- 행 590–592의 주석은 v5 `task_scope` 결정이 살아 있는 과제를 직접 철회하지 않으며, 철회 회귀는 `test_task_scope`가 맡는다고 적는다. 대응하는 테스트는 이 클래스에 없다.

### `test_failed_contract_review_is_not_regenerated_while_waiting_for_diagnosis` (행 525–536)
- 성질: 계약 검토 실행이 실패하면, 진단을 기다리는 동안 같은 과제의 계약 검토가 다시 생성되지 않는다.
- 준비: 2단, 클래스 도우미 `make_active()`. 먼저 기본 `PurposeRunner`로 `engine.run(max_steps=1)`을 돌려 과제 하나가 생기게 한다. 그다음 러너를 `CheckedRunner(Runner())`로 바꾼다. 이 `Runner`는 `status="failed"`, `error="reviewer unavailable"`을 돌려준다.
- 실행: `engine.run(max_steps=1)`.
- 단언: `waiting_actions` 가운데 행동 대상이 그 과제인 것이 있다. 대기열에 그 과제를 대상으로 한 `task_contract_review`가 없다.
- 대역: `PurposeRunner`(첫 단계), `CheckedRunner`, 스크립트 `Runner`. 둘 다 `local_job_runner`로 실제 Windows Job을 띄운다.

### `test_failed_identity_slot_is_not_regenerated_after_its_peer_finishes` (행 538–557)
- 성질: 식별 검토의 한 슬롯(`initial-0`)이 실패하면, 동료 슬롯이 끝난 뒤에도 그 슬롯이 다시 생성되지 않고 대기에 남는다.
- 준비: 2단 위의 더 깊은 빌드, `make_review()`. 두 곳을 바꾼다.
  - `runner.run`: 문맥의 슬롯이 `initial-0`이면 `on_started({"pid": 1})`를 부르고 실패를 돌려준다.
  - `runner.answer`: `operational_review`에는 `kind="repair"`, `next_owner="operations"` 처분을 돌려준다.
- 실행: `engine.run(max_steps=3)`.
- 단언: 대기열에 `slot == "initial-0"`인 `identity_review`가 없다. `waiting_actions`에 슬롯 `initial-0` 행동이 있다.
- 대역: `PurposeRunner`의 `run`과 `answer` 치환. 실패 분기는 원래 `run`을 거치지 않으므로 `local_job_runner`를 타지 않고, 엔진의 `on_started`를 직접 부른다.

### `test_explicit_diagnosis_can_open_one_new_attempt_of_a_failed_action` (행 559–588)
- 성질: 실패한 행동은 운영자가 명시로 요청한 운영 검토가 `retry` 처분을 내리면, 정확히 하나의 새 시도로 다시 열린다. 새 시도는 같은 행동 ID를 쓰고, 실패한 실행을 `continuation_of`로 가리킨다.
- 준비: 2단, `make_active()`. 대기열을 maintenance 행동 `AC-failed` 하나로 둔다. 러너는 `CheckedRunner(Runner())`이고, `Runner`는 역할에 따라 답한다.
  - maintenance는 `"configuration failure"`로 실패한다.
  - 그 밖의 역할(운영 검토)은 `kind="retry"`, `next_owner="engine"`, 범위 "One new attempt of the failed action" 처분으로 완료한다.
- 실행:
  1. `engine.run(max_steps=1)`로 실패시킨다.
  2. `control(repo, id, "request", origin="operator", config={"role": "operational_review", "target": failed}, text=...)`를 보내고 `process_controls()`로 적용한다.
  3. 대기열을 그 진단 행동 하나로 줄이고 저장한 뒤 `engine.run(max_steps=1)`을 돌린다.
- 단언: 대기열의 maintenance 행동이 정확히 1개다. 그 `id`가 `"AC-failed"`이고, `continuation_of`가 실패한 실행 ID다.
- 대역: `CheckedRunner`, 스크립트 `Runner`, `local_job_runner`(실제 Windows Job).

### `test_late_identity_result_is_preserved_without_retrying_a_superseded_slot` (행 594–616)
- 성질: 식별 검토가 도는 도중 대상 지식이 개정되면, 늦게 도착한 검토 결과는 받아들여지지 않지만 봉인된 제출로 보존된다. 대체된 주기의 슬롯은 다시 시도되지 않는다.
- 준비: 2단 위의 더 깊은 빌드, `make_review()`. `review_is_next`가 아니면 `drive`로 그 상태까지 몬다. 주기 ID를 잡는다. `runner.run`을 감싸, 원래 결과를 얻은 뒤 대상 지식을 개정한다. 개정은 `control(..., "knowledge", config={"operation": "revise", ...})`로 보내고 `await_control`로 기다린다. `declared_impact`에는 `plan_impact(...)['computed_impact']`를 쓴다.
- 실행: `engine.run(max_steps=1)`.
- 단언: 대기열에 그 `review_cycle_id`를 가진 행동이 없다. 식별 검토 실행의 `outcome`이 `output_accepted`가 아니다. `store.read(review['submission_intent']['output_ref'])`가 `None`이 아니다.
- 대역: 감싼 `PurposeRunner.run`(원래 `run`은 `local_job_runner`로 실제 Windows Job을 띄운다).
- 비고:
  - `await_control`의 상한은 60초다.
  - `assertIsNotNone`은 실질적인 확인을 하지 않는다. `submission_intent`가 없으면 `KeyError`가 나고, 경로가 없으면 `ResearchRepository.read`가 부르는 `git cat-file blob`이 실패한다. 그래서 이 단언은 실제로는 봉인 intent와 그 artifact가 있는지를 확인한다.

### `test_large_own_review_history_does_not_request_mathematical_reconstruction` (행 618–637)
- 성질: 식별 검토 슬롯 자신의 보존 이력이 입력 한도를 넘어도, 엔진은 모델을 부르지 않는다. 지식을 바꾸지 않고, 검토 자원 처분 이벤트도 만들지 않는다.
- 준비: 2단 위의 더 깊은 빌드, `make_review()`. 필요하면 `drive`로 검토 차례까지 몬다. 한도는 대기열 식별 검토 행동의 고정 프로필 한도(`engine._execution_profile(action)["input"]["max_input_bytes"]`)다. 주석대로 입력 한도는 현재 설정이 아니라 고정 프로필의 값이다. `review_cycle.record_turn`으로 그 슬롯에 한도를 넘는 assistant 메시지 하나를 기록하고 저장한다. 지식 사본과 러너 호출 수를 떠 둔다.
- 실행: `engine.run(max_steps=1)`.
- 단언: 러너 호출 수가 그대로다. 지식이 사본과 같다. 주기 `history`에 `event == "review_resource_disposition"`인 행이 없다.
- 대역: `PurposeRunner`(호출 수 확인에 `runner.calls`를 쓴다).
- 비고: 이름의 "수학적 재구성을 요청하지 않음"은 모델 호출이 없고 자원 처분 이벤트가 없다는 두 단언으로만 드러난다. 엔진이 대신 무엇을 하는지(예: 입력 초과 기록)는 단언하지 않는다.

### `test_fixed_question_resolver_accepts_the_supplied_source_aliases` (행 639–661)
- 성질: 검토 주기가 열린 뒤 공급된 원천도, 고정 질문 해석기는 원천의 여러 별칭 모두로 같은 원천(같은 sha256)으로 해석한다.
- 준비: 2단 위의 더 깊은 빌드, `make_review()`. 복원 루트의 `paper.txt`에 원문을 쓰고, `control(..., "source", config={"path": ...})`와 `process_controls()`로 원천을 공급한다. 주석대로 검토 입력은 준비 시점에 인스턴스의 원천을 읽으므로 원천이 주기보다 늦게 와도 된다. 대기열의 식별 검토 행동으로 `engine._context(action, root/"source-alias-input")`를 만들고, 첫 원천과 주기를 잡는다.
- 실행: 각 별칭으로 `engine._research_source_spec(cycle, action, reference)`를 부른다.
- 단언: `ValueError`가 나지 않는다(나면 "a supplied source alias was refused" 메시지로 실패). 해석된 `sha256`이 원천의 `sha256`과 같다.
- 대역: 없음.
- 비고: `subTest(reference=...)` 다섯 경우는 원천의 `id`, `"source:" + name`, `local_path`, `path`, `name`이다.

### `test_private_insight_rechecks_its_own_basis_when_published_after_peer_review` (행 662–699)
- 성질: 식별 검토 슬롯이 사적으로 제안한 통찰은 게시될 때 자기 근거를 다시 확인한다. 동료 검토 도중 근거 지식이 개정되었으면, 통찰은 활성 레코드로 들어오되 사용이 중단된다.
- 준비: 2단, `make_active()`.
  - `control(..., "knowledge", config={"operation": "import", "candidate": {...}})`로 관찰 지식을 들여오고 `process_controls()`로 적용한다.
  - 대기열을 `research_preparation` 행동만 남기고 저장한다.
  - `runner.answer`를 감싼다. `identity_review`의 `stage='initial'`, `slot='initial-0'`이면 `evidence_ids=[kid]`인 질문 통찰을 확장 파일에 쓴다.
  - `runner.run`을 감싼다. `slot='initial-1'`의 원래 결과를 얻은 뒤, 그 지식의 `statement`를 `control` 개정으로 바꾸고 `await_control`로 기다린다.
- 실행: `self.drive(engine, predicate=...)`. 조건은 제목이 `"Private followup"`인 지식이 생기는 것이다.
- 단언: 그 통찰의 `use_suspended`가 참이고, `lifecycle`이 `"active"`다. `knowledge.assess_use(insight, instance)["valid"]`가 거짓이고, `dependencies`가 `[kid]`다.
- 대역: 감싼 `PurposeRunner`의 `run`과 `answer`. 실제 Windows Job을 띄운다.
- 비고: `drive` 상한은 45단계, `await_control` 상한은 60초다.

## 관계

- 같은 제품 기능을 다른 층에서 검사하는 모듈:
  - `test_submission_flow`는 같은 제출 흐름의 중앙 수신·봉인·적용을 엔진 메서드 단위로 검사한다. 이 모듈은 작업자 쪽 도구, 전송, 명령과 실제 엔진 구동의 경계를 본다.
  - `mcp_server_config`는 `test_control_transport`와 `test_execution_profiles`도 쓴다.
  - `producer_check`는 `test_impact_review`, `test_role_input`, `test_submission_checks`도 쓴다. `request_control`은 `test_engine`도 쓴다.
  - `fit_context`의 입력 초과 규칙은 `test_context_store`, `test_role_input`, `test_submission_boundaries`가 더 넓게 본다.
- 픽스처 의존:
  - 엔진을 쓰는 테스트는 모두 `purpose_fixtures.ActivatedPurposeHarness`의 템플릿 사본(`make_active`, `purpose_copy`) 위에서 돈다.
  - 러너는 `CheckedRunner`나 `PurposeRunner`다. 둘 다 `research_fixtures.local_job_runner`로 호출마다 실제 Windows Job 자식(`python -c "import time; time.sleep(600)"`)을 띄우고, 끝나면 종료한다.
  - 소유자 루프를 기다릴 때는 `research_fixtures.await_control`과 `await_stop`을 쓴다.
  - `CheckedRunner`를 쓰는 모듈은 이 모듈과 `test_submission_boundaries` 둘뿐이다.
- 이 모듈에만 있는 도우미: `LocalControlProtocolTests.mcp`와 `publish_intent`, `ProducerToolTests.prepare`와 `check_output`, `ReviewFailureTests.make_review`와 `review_is_next`(그리고 `make_active` 재정의). 모듈 함수는 없다.
- 겹치거나 보완하는 시험:
  - `test_accepted_submission_is_unchanged_when_original_draft_changes_later`는 `test_submission_flow`의 `test_central_seal_uses_actual_bytes_and_survives_original_draft_change`와 같은 성질을 MCP와 Git 게시 층에서 본다.
  - `test_empty_known_extension_family_remains_a_semantic_noop`은 `test_submission_flow`의 `test_empty_known_extension_is_normalized_at_capture_and_sealed_read`와 짝을 이룬다.
  - `test_receiver_rejects_unknown_insight_kind_and_missing_evidence`(엔진 수신 경계)와 `test_producer_checks_sidecar_kinds_references_and_self_repair`(생산자 명령), `test_live_review_validates_sidecar_before_applying_continue`(실시간 운영 검토)는 같은 잘못된 `research_insights` 확장을 세 경계에서 본다.
  - 실행 실패 뒤 대기와 운영 검토로 넘어가는 성질은 `test_submission_boundaries`의 `test_execution_failure_is_parked_before_diagnosis`와 이 모듈의 `test_unsealed_invalid_runner_output_is_preserved_for_operational_review`가 각각 실행 실패와 출력 검증 실패에 대해 본다.
