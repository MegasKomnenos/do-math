# test_submission_flow

| 항목 | 값 |
|---|---|
| 조각 | `review` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_submission_flow.py` (982행) |
| 클래스 / 테스트 | 14 / 34 |
| 시험 대상 제품 코드 | `do_math/submission.py`의 `seal_submission`, `read_sealed_submission`, `issued_input`, `producer_check`, `request_control`, `install_tools`, `fixed_research_reference_path`, `load_json`, `SealedSubmissionError`; `do_math/engine.py`의 `ResearchEngine._preview_submission`, `_collect_submitted_result`, `_sealed_submission_files`, `_submission_check_summary`, `_apply_submission_bundles`, `_apply_bundle_candidate`, `_validate_bundle_impacts`, `_receive_submission`, `_submission_repair_context`, `_publish_control_request`, `_retry_submission_publications`, `_apply`, `status`; `do_math/execution_lifecycle.py`의 `create_execution`, `transition_execution`, `record_submission_intent`; `do_math/integration.py`의 `split_bundles`, `issue`, `ImpactReviewRequired`; `do_math/knowledge.py`의 `_apply_impact_effects`; `do_math/knowledge_io.py`의 `import_candidate`, `ensure_ontology`; `do_math/control_transport.py`의 `ControlTransport` |
| 사용하는 픽스처 모듈 | `engine_fixtures`(`approve_contract`, `native_result`, `routing_engine`, `start_submission_history`, `submit_history`, `context_engine`), `knowledge_fixtures`(`knowledge_candidate`), `research_fixtures`(`bare_engine`, `git_init`, `seal_response`, `candidate`, `sealed_maintenance_submission`, `fixture_setup_lean`), `record_fixtures`(`two_observation_output`, `research_work_context`) |
| 격리 표지 | 없음 |
| 시작 상태 | 단이 섞여 있다. 1단(순수 함수·검증기에 임시 작업 공간을 준 것)이 14개, 메모리 엔진 대역(`routing_engine`, `bare_engine`, `context_engine`)이 15개, 2단(`start_submission_history`가 복원하는 `state_fixtures.active_instance`)이 5개다 |

## 목적

모듈 docstring은 "중앙에서 봉인하는 제출 흐름"을 시험한다고 밝힌다. 세부 주제로 봉인(sealing), 포착(capture), 미리보기(preview), 번들 적용, 영수증, 게시 대기를 든다.

이 흐름의 뼈대는 다음과 같다. 작업자(AI 실행)는 작업 공간에 초안을 쓰고, 초안의 위치만 제어 전송(`ControlTransport`)으로 보낸다. 중앙 엔진은 `submission.seal_submission`으로 그 순간의 실제 바이트를 한 번 읽는다. 이어서 같은 바이트를 수신자 모드로 검사하고, 결과를 되돌릴 수 없는 CAS artifact(`output.json`, `extensions.json`, `check.json`, `manifest.json`, `files/...`)로 떼어 낸다. 받아들인 제출은 `execution_lifecycle.record_submission_intent`가 실행의 `submission_intent`와 `submission_receipt`로 기록한다. 이후의 모든 소비자는 작업 공간이 아니라 `submission.read_sealed_submission`으로 Git에 봉인된 바이트를 다시 읽는다. 적용은 `ResearchEngine._apply_submission_bundles`가 맡는다. 이 함수는 출력의 `integration_bundles`를 독립 후보로 나눠 번들마다 따로 검증하고 게시한다.

이 모듈은 그 흐름의 다섯 계약을 검사한다.

- 봉인은 검사한 바로 그 바이트를 고정하고, 나중의 파일 변경과 섞이지 않는다.
- 전송은 위치 정보만 싣는다.
- 봉인을 되읽을 때는 영수증의 해시와 크기, 검사의 결속(실행, 모드, 스키마, 입력 해시)을 모두 대조한다.
- 번들 적용은 독립 번들 단위로 커밋되고, 재시도해도 이미 받아들인 번들을 되풀이하지 않는다.
- 미리보기는 같은 영역 콜백을 쓰되 아무것도 게시하지 않는다.

## 모듈 수준 요소

- 행 13: 스킬의 `scripts/` 폴더(`Path(__file__).resolve().parents[1]`)를 `sys.path` 맨 앞에 넣는 공통 경로 머리다. 조건 없이 넣는다.
- 행 2–23: import 목록이다. 모듈 함수, 상수, `setUpModule`은 없다.
- 행 981–982: 직접 실행하면 `unittest.main()`을 돈다. `verbosity` 인자는 없다.

## SubmissionFlowTests (행 26–359)

- 기반: `unittest.TestCase`. 클래스 표지와 클래스 속성은 없다.
- `setUp` (행 169–199)은 테스트 사이에 끼어 정의되어 있지만, 클래스의 모든 테스트가 쓰는 시작 상태를 만든다. 순서는 다음과 같다.
  1. `tempfile.TemporaryDirectory`를 만들고 `addCleanup`으로 지운다. 그 아래에 `workspace/`와 `delivery/`를 둔다.
  2. `ControlTransport(delivery)`를 만들고, `issue("EX-flow", "GR-flow", workspace=...)`로 결속(`self.binding`)을 발급한다.
  3. `self.context`를 만든다. 역할은 `maintenance`, 행동 ID는 `AC-flow`, `execution_id`는 `"EX-flow"`이고, `control_binding`이 들어 있다. `snapshot`은 `"fixed"`이고 `tasks`, `knowledge_catalog`, `sources`, `kind_definitions`는 모두 비었다.
  4. `self.schema = contracts.schema_for("maintenance")`를 잡고 `submission.install_tools(workspace, context, schema, None)`로 도구 판을 설치한다. 이 호출은 `context`에 `reference_catalog`와 `submission_contract`를 채운다.
  5. `self.output`을 만든다. 필드는 `summary="Inspect only"`, `report="Inspected"`이고, `used_sources`, `questions`, `remaining_work`는 비었다. `seal_response`가 여기에 `integration_bundles` 하나를 붙인다.
  6. 그 정본 JSON 바이트를 `workspace/.scratch/draft.json`(`self.draft`)에 쓴다.

  저장소도 엔진도 없다. 순수 함수와 검증기를 임시 작업 공간 위에서 직접 부르는 1단이다. 네 테스트는 예외로 엔진 대역이나 실제 Git 저장소를 더 쓰며, 항목마다 밝힌다. 엔진 대역을 쓰는 것은 `test_real_preview_entry_accepts_questions_without_publishing`(`context_engine`), `test_stopped_provider_recovers_the_frozen_submission_without_reading_original`과 `test_result_file_recovery_uses_the_receipt_snapshot_not_live_workspace`(`bare_engine`)이고, 실제 Git 저장소를 쓰는 것은 `test_central_candidate_is_read_from_its_git_receipt_without_legacy_fields`다.
- 클래스 도우미 메서드는 없다.

### `test_issued_input_is_parsed_once_per_content_and_returned_as_copies` (행 27–57)
- 성질: `issued_input`은 호출마다 바이트를 읽지만, 같은 내용은 프로세스에서 한 번만 해석하고 호출자에게는 사본을 준다. 내용이 바뀌면 다시 해석한다.
- 준비: 1단. 이 테스트는 `setUp`의 산출을 쓰지 않는다. 읽기 함수 `read(path, snapshot)`는 읽은 경로를 기록하고, 파일 이름과 nonce를 담은 정본 JSON을 돌려준다. nonce는 `uuid4`로 정하며, 주석대로 다른 테스트가 프로세스에 남긴 메모 항목과 바이트가 겹치지 않게 한다. 실행 레코드는 `{'input_bundle': 'BA-<uuid>'}`다.
- 실행: `submission.issued_input(execution, 'head', read)`를 부른다. 같은 실행으로 두 번, 다른 번들과 스냅숏(`'other'`)으로 한 번, nonce를 바꾼 뒤 한 번 더 부른다.
- 단언:
  - 두 번 부른 뒤 읽은 경로가 `runtime/artifacts/<번들>/input/submission/context.json`과 `.../schema.json`을 두 번 되풀이한 목록과 같다. 곧 바이트는 매번 읽는다.
  - `load_json`의 호출 수는 2다(내용 둘을 한 번씩 해석).
  - 첫 결과에 넣은 `changed` 키가 둘째 결과에 없다. 스키마 결과의 `file`은 `'schema.json'`이다.
  - 다른 번들과 스냅숏으로 불러도 해석 수는 2 그대로이고, 결과는 둘째 결과와 같다. 앞서 스키마 사본에 넣은 `changed`가 새 스키마 결과에 없다.
  - nonce를 바꾸면 해석 수가 4가 되고, 새 결과의 `nonce`가 바뀐 값이다.
- 대역: `mock.patch.object(submission, 'load_json', wraps=submission.load_json)`로 해석 횟수를 센다. 읽기 함수는 손으로 만든 대역이다.
- 비고:
  - 메모의 키가 바이트의 sha256이라는 제품 규칙(`submission.py`의 `_ISSUED_INPUTS` 주석, `이음새-정본.md` §3의 `submission.issued_input` 언급)을 행동으로 확인한다.
  - 함수 안의 `import uuid`는 모듈 머리(행 8)의 import와 겹친다.

### `test_real_preview_entry_accepts_questions_without_publishing` (행 59–103)
- 성질: 엔진의 실제 미리보기 입구 `_preview_submission`은 질문이 있는 초안을 통과시킨다. 이때 런타임을 바꾸지 않고, `artifact_bundle`이나 질문 연결을 남기지 않으며, 게시되지 않은 artifact를 Git에서 읽지 않는다. 잘못된 초안에는 불통과를 답한다.
- 준비: 메모리 엔진 대역이다.
  - `engine_fixtures.context_engine()`을 쓴다. 이 엔진은 실제 문맥 생산자를 유지하며, 저장소는 `ResearchRepository`의 autospec이다. 엔진의 `instance['workspace']`는 임시 루트이고, 실행 `EX-flow`(maintenance, running, `input_bundle='BA-preview'`)를 런타임에 등록한다.
  - 문맥은 `setUp`의 것을 복사해 `action`, `snapshot`, `workspace`를 바꾸고 `submission_contract`를 뺀 것이다. 이 문맥으로 `runs/EX-flow/workspace`에 도구를 다시 설치한다.
  - 출력은 `questions=['What should operations decide?']`로 바꿔 `seal_response`한 뒤 `draft.json`에 쓴다.
  - `activity-extensions.json`에는 `{"knowledge_changes": []}`를 둔다.
- 실행: `engine._preview_submission(execution, {'draft_path': 'draft.json'})`를 부른다. 다음에 `used_sources=['TK-not-in-input']`로 바꾼 초안으로 한 번 더 부른다.
- 단언:
  - 첫 미리보기는 `passed`가 참이다. 호출 전후 `canonical_json(engine.runtime)`이 같다. 실행에 `artifact_bundle` 키가 없다. `store.validate_candidate`가 정확히 한 번 불렸다. `runtime['question_links']`가 비었다.
  - 둘째 미리보기는 `passed`가 거짓이다. 런타임은 여전히 같고, `validate_candidate` 호출은 늘지 않아 여전히 한 번이다. 거부 사유 문구는 고정하지 않는다.
- 대역:
  - `engine.store.read.side_effect`는 입력 번들의 `context.json`과 `schema.json` 두 경로만 답한다. 다른 경로를 읽으면 `AssertionError('preview read an unpublished artifact from Git: ...')`를 던진다.
  - `engine._validate_bundle_current`를 `create_autospec(..., return_value=None)`로 바꾼다.
  - `context_engine`이 기본으로 넣는 대역(`_execution_profile` 등)도 있다.

### `test_central_candidate_is_read_from_its_git_receipt_without_legacy_fields` (행 105–167)
- 성질: 받아들인 제출은 `submission_intent`와 `submission_receipt`만으로 실제 Git 저장소에서 되읽힌다. 저장소 식별(`git_dir`)을 주어도 결과가 같다. 출력, 확장, 검사 결속 가운데 하나라도 바꾸면 되읽기가 거부된다. 주석(행 127)은 저장소 식별이 있으면 봉인 행을 프로세스당 한 번만 해시한다고 말하지만, 이 테스트의 단언은 그 성질을 검출하지 못한다(비고 참조).
- 준비: `setUp`(1단) 위에 실제 Git 저장소를 더한다.
  - `seal_submission(workspace, '.scratch/draft.json', ...)`의 산출 artifact를 `runtime/artifacts/BA-central/submission/` 접두로 옮긴다.
  - intent에는 `output_ref`, `extensions_ref`, `check_ref`를 채운다. receipt는 `state='accepted'`이고, 각 artifact의 경로·sha256·크기를 담는다.
  - `git_init`로 만든 저장소에 `GitStateStore(repo, 'RI-01ARZ3NDEKTSV4RRFFQ69G5FAV').publish(None, {...})`로 artifact를 게시한다.
- 실행: `submission.read_sealed_submission`을 세 방식으로 부른다. 첫째는 저장소 읽기 함수만 준다. 둘째는 `git_dir=store.git_dir`를 더한다. 셋째는 둘째와 같되 `hashlib`를 대역으로 바꾼다.
- 단언:
  - 되읽은 `output`이 `self.output`과 같고, `extensions`는 `{}`이며, `check['passed']`는 참이다.
  - `git_dir`를 준 호출의 결과가 같다.
  - `submission.hashlib`를 `Mock(sha256=Mock(side_effect=AssertionError('sealed row rehashed')))`로 바꿔도 같은 결과가 나온다. 이 단언이 실제로 확인하는 것은 되읽기 경로에서 `submission` 모듈 자신이 `hashlib.sha256`을 부르지 않는다는 것뿐이다(주석은 `이음새-정본.md` §3을 가리킨다).
  - 변조 다섯 경우는 모두 `SealedSubmissionError`를 던진다. 예외 유형만 확인하고 메시지는 고정하지 않는다.
- 대역: `mock.patch.object(submission, 'hashlib', Mock(...))`. 변조 경우에는 사전 기반 읽기 람다를 쓴다.
- 비고:
  - `subTest(mutation=...)` 다섯 경우는 다음과 같다.
    - `output`: 보고서를 바꾼 출력.
    - `extensions`: 검사하지 않은 `research_insights`를 넣은 확장.
    - `execution`: 검사의 `execution_id`를 `EX-other`로 바꿈.
    - `mode`: 검사의 `mode`를 `producer`로 바꿈.
    - `schema`: `schema_ref.sha256`을 `'0'*64`로 바꿈.
  - 매 경우 검사 ID, intent의 해시, receipt의 artifact 행을 새 바이트에 맞게 다시 계산한다. 그래서 바이트 해시·영수증 행·검사 ID 대조(`submission.py` 행 71–87)는 통과한다. 원문을 읽으면 다섯 경우 모두 그 뒤의 검사 결속 규칙(행 88–93: `mode`, `execution_id`, `schema_ref`, 출력·확장의 `input_hashes`, 메시지 "sealed check does not bind this candidate")에서 거부된다. 다만 테스트는 예외 유형만 보므로 어느 사유로 거부되는지는 고정하지 않는다.
  - 해시 대역의 한계: 봉인 행의 해시는 `read_sealed_submission`이 부르는 `repository.sealed_bytes`가 `repository.verify_artifact`(`repository.py` 행 65–71)에서 `repository` 모듈의 `hashlib`로 계산한다. `patch.object(submission, 'hashlib', ...)`는 `submission` 모듈의 이름만 바꾸므로 이 계산을 가로채지 못한다. 그래서 프로세스 메모(`VERIFIED_ARTIFACTS`)가 작동하지 않아 셋째 호출이 행을 다시 해시하더라도 이 단언은 통과한다. 이름과 주석이 말하는 "프로세스당 한 번 해시"는 이 테스트로 보증되지 않는다. 막는 것은 `submission.py`가 행을 제 `hashlib`로 따로 비교하는 회귀(`이음새-정본.md` §3이 금하는 로컬 비교)뿐이다.
  - 이름의 "without legacy fields"는 실행 레코드가 `submission_intent`와 `submission_receipt` 외의 필드를 갖지 않는 구성으로만 드러난다. 옛 필드의 부재를 따로 단언하지는 않는다.
  - 실제 Git 저장소를 쓴다. `GitStateStore`는 git 자식 프로세스를 부른다.

### `test_central_seal_uses_actual_bytes_and_survives_original_draft_change` (행 201–210)
- 성질: 중앙 봉인은 검사한 실제 바이트를 담고, 원본 초안이 뒤에 바뀌어도 봉인은 그대로다. 제어 폴더의 정지 요청 파일은 출력 목록에 들지 않는다.
- 준비: `SubmissionFlowTests` 절의 `setUp`(1단).
- 실행: `seal_submission(workspace, '.scratch/draft.json', execution_id='EX-flow', ..., max_artifact_bytes=1024*1024)`로 봉인한 뒤, 초안을 `{"changed": true}`로 덮어쓴다.
- 단언: 봉인 결과의 `passed`가 참이다. 덮어쓰기 전의 초안 바이트가 `artifacts['output.json']`과 같고, 그것을 해석하면 `self.output`이다. `manifest`의 경로 집합에 `.control/stop-request.json`이 없다.
- 대역: 없음.
- 비고: 이 테스트에서는 `.control/stop-request.json`을 만들지 않으므로, 마지막 단언은 부재만 확인한다. 정지 요청 파일이 실제로 있을 때 목록에서 빠지는지는 `test_control_changes_do_not_change_candidate_hashes_or_output_manifest`가 본다.

### `test_central_capture_never_mixes_checked_draft_with_a_later_file_version` (행 212–231)
- 성질: 중앙 포착 도중 초안 파일이 바뀌어도, 검사한 출력과 포착한 파일 사본은 같은 판의 바이트다.
- 준비: `setUp`(1단). 초안은 `workspace/draft.json`(`.scratch` 밖)에 둔다.
- 실행: `submission.collect_outputs`를 `racing_collect`로 바꾼 채 `seal_submission(workspace, "draft.json", ...)`를 부른다. `racing_collect`는 호출 기록을 남기고, 초안을 보고서만 바꾼 판으로 다시 쓴 뒤 원래 `collect_outputs`를 부른다.
- 단언: `passed`가 참이다. `collect_outputs`는 정확히 한 번 불렸다. `artifacts['output.json']`이 `artifacts['files/draft.json']`과 같다.
- 대역: `mock.patch.object(submission, "collect_outputs", racing_collect)`로 경쟁 쓰기를 흉내 낸다.
- 비고: 제품 `seal_submission`은 초안 바이트를 먼저 읽고 그 바이트를 `captured_files`로 `collect_outputs`에 넘긴다. 그래서 수집기가 파일을 다시 읽어 뒤의 판을 섞지 않는다. 단언이 이 결속을 확인한다.

### `test_submit_transport_contains_only_the_draft_locator` (행 233–238)
- 성질: 작업자 쪽 제출 요청의 payload에는 초안 위치 하나만 실린다.
- 준비: `setUp`(1단).
- 실행: `submission.request_control(workspace, ".scratch/draft.json", kind="submit_intent", wait_seconds=0, binding=...)`.
- 단언: `ControlTransport.worker_submit`의 호출 키워드 `payload`가 `{"draft_path": ".scratch/draft.json"}`과 정확히 같다.
- 대역: `mock.patch.object(ControlTransport, "worker_submit", return_value={"state": "submitted"})`.

### `test_control_changes_do_not_change_candidate_hashes_or_output_manifest` (행 240–249)
- 성질: 작업 공간의 `.control/` 파일이 바뀌어도 생산자 검사의 입력 해시와 출력 목록은 바뀌지 않는다.
- 준비: `setUp`(1단).
- 실행: `submission.producer_check(workspace, draft)`를 부르고 `collect_outputs(workspace, max_bytes=1024*1024)`의 `manifest`를 잰다. 이어서 `.control/stop-request.json`(`{"reason": "submission_intent"}`)을 만든 뒤 둘을 다시 잰다.
- 단언: 두 검사의 `input_hashes`가 같고, 두 목록이 같다.
- 대역: 없음.

### `test_lifecycle_accepts_only_central_sealed_candidate_not_worker_manifest` (행 251–262)
- 성질: 수명 주기 모듈은 중앙에서 봉인한 후보(`candidate_id`와 `output_ref`를 가진 intent)와 받아들인 제출 영수증을 기록하고, 실행을 `stopping`으로 옮긴다.
- 준비: 1단. `execution_lifecycle.create_execution(execution_id="EX-flow", owner_activity_id="AY-flow", actor_kind="ai", ...)`로 실행을 만들고 `starting`, `running`으로 옮긴다.
- 실행: `record_submission_intent(execution, intent, receipt)`. intent는 `candidate_id="CS-one"`과 `output_ref`를 갖는다. receipt는 `kind="submit_intent"`, `state="accepted"`, `execution_id="EX-flow"`다.
- 단언: 실행의 `status`가 `"stopping"`이고, `submission_intent`가 준 intent와 같다.
- 대역: 없음.
- 비고: 이름은 작업자 manifest를 받지 않는다는 거부 쪽도 말하지만, 이 테스트는 받아들이는 경로 하나만 단언한다. 제품의 거부 사유(`"submission intent requires a centrally sealed candidate"` 등)는 여기서 부르지 않는다.

### `test_stopped_provider_recovers_the_frozen_submission_without_reading_original` (행 264–281)
- 성질: 제공자 결과가 `stopped`여도, 이미 봉인된 제출이 있으면 엔진은 원본 초안이 아니라 봉인된 바이트에서 완료 결과를 회수한다.
- 준비:
  - `setUp`에서 봉인한 뒤 초안을 `{"changed": true}`로 바꾼다.
  - 엔진은 `bare_engine({"lifecycle": {"state": "active"}}, {"status": "running"}, head="sealed-head", store=autospec)`로 만든 메모리 엔진 대역이다. `store.read.return_value`는 봉인된 `output.json` 바이트다.
  - 실행 레코드의 `submission_intent`는 `output_ref="sealed/output.json"`과 그 바이트의 sha256을 갖는다.
- 실행: `engine._collect_submitted_result(execution, {"status": "stopped", "usage": {}}, context, schema, workspace)`.
- 단언: 반환의 `status`가 `"completed"`, `collection`이 `"sealed_submission"`이고, `output`이 `self.output`과 같다.
- 대역: `ResearchRepository` autospec 저장소와, `engine._clock_guard`의 autospec(`{"usable": True}`).

### `test_result_file_recovery_uses_the_receipt_snapshot_not_live_workspace` (행 283–297)
- 성질: 봉인된 연구 파일은 영수증의 스냅숏에서 회수되며, 뒤에 바뀐 작업 공간의 파일은 쓰이지 않는다.
- 준비: 작업 공간에 `research.txt`(`b"accepted bytes"`)를 두고 봉인한 뒤, 그 파일을 `b"later mutation"`으로 바꾼다. 엔진은 `bare_engine(head="sealed-head", store=autospec)`이다. `store.read.side_effect`는 `sealed/files/<경로>`를 봉인 artifact에 대응시킨다. 실행의 `submission_intent.file_refs`는 봉인 manifest 행에 `artifact_ref`를 붙인 것이다.
- 실행: `engine._sealed_submission_files(execution)`.
- 단언: 회수된 `files['research.txt']`가 `b"accepted bytes"`다.
- 대역: `ResearchRepository` autospec 저장소.

### `test_illegal_draft_reference_is_rejected_before_transport` (행 299–307)
- 성질: 작업 공간 밖을 가리키는 초안 경로(`../outside.json`)는 중앙 봉인에서 읽기 단계 문제로 거부된다.
- 준비: `setUp`(1단). 작업 공간의 부모에 `outside.json`을 둔다.
- 실행: `seal_submission(workspace, "../outside.json", ...)`.
- 단언: `passed`가 거짓이고, `check['issues']`에 `rule_id == "submission.read"`인 행이 있다. 규칙 ID로 거부 사유를 고정하지만, 메시지는 보지 않는다.
- 대역: 없음.
- 비고: 이름은 "전송 전에" 거부된다고 말하지만, 이 테스트가 부르는 것은 중앙 포착인 `seal_submission`이다. 작업자 쪽 전송 함수 `request_control`에도 같은 경로 거부(`"submission draft must be inside this workspace"`)가 있으나, 여기서는 부르지 않는다.

### `test_central_candidate_rejects_missing_workspace_reference` (행 309–318)
- 성질: 출력이 존재하지 않는 작업 공간 파일(`workspace:missing-evidence.txt`)을 근거로 대면, 중앙 후보가 거부된다.
- 준비: `setUp`의 출력에 `used_sources=["workspace:missing-evidence.txt"]`를 넣고, 다시 `seal_response`해 초안에 쓴다.
- 실행: `seal_submission(workspace, ".scratch/draft.json", ...)`.
- 단언: `passed`가 거짓이다. 문제 행 가운데 `path == "output/used_sources/0"`이고 메시지에 `"preserved workspace file"`이 든 것이 있다. 경로와 메시지 조각으로 거부 사유를 고정한다.
- 대역: 없음.

### `test_empty_known_extension_is_normalized_at_capture_and_sealed_read` (행 320–350)
- 성질: 빈 알려진 확장 계열(`knowledge_changes: []`)은 생산자 검사와 중앙 봉인에서 같은 입력 해시를 낳고, 원 바이트 그대로 보존되며, 되읽을 때는 `{}`로 정규화된다. 모르는 계열, 잘못된 모양, 없는 레코드를 가리키는 변경은 포착 자격이 없다.
- 준비: `setUp`(1단). `activity-extensions.json`에 정본이 아닌 바이트 `b'{ "knowledge_changes": [] }\r\n'`을 쓴다.
- 실행:
  - `producer_check`와 `seal_submission`을 부른다.
  - 봉인 artifact를 `runtime/artifacts/BA-empty/` 접두로 옮겨 intent와 receipt를 만들고, 사전 기반 읽기로 `read_sealed_submission`을 부른다.
  - 잘못된 확장 셋으로 `seal_submission`을 다시 부른다.
- 단언:
  - 두 검사가 모두 통과하고, 두 `input_hashes`가 같다.
  - `artifacts['extensions.json']`과 `artifacts['files/activity-extensions.json']`이 원 바이트와 같다.
  - 되읽은 `extensions`가 `{}`다.
  - 잘못된 세 경우는 모두 `capture_eligible`이 거짓이다. 사유 문구는 고정하지 않는다.
- 대역: 없음.
- 비고: `subTest(invalid=...)` 세 경우는 `{"unknown_family": []}`, `{"knowledge_changes": {}}`, `{"knowledge_changes": [{"id": "KN-unavailable"}]}`다.

### `test_central_candidate_rejects_malformed_draft_bytes` (행 352–359)
- 성질: JSON으로 해석되지 않는 초안 바이트는 해석 단계 문제로 거부된다.
- 준비: `setUp`(1단). 초안을 `b'{"summary":'`로 덮어쓴다.
- 실행: `seal_submission(workspace, ".scratch/draft.json", ...)`.
- 단언: `passed`가 거짓이고, 문제 행에 `rule_id == "submission.parse"`가 있다. 규칙 ID로 사유를 고정한다.
- 대역: 없음.

## CentralSubmissionHistoryTests (행 362–454)

- 기반: `unittest.TestCase`. 표지와 클래스 속성은 없다.
- `setUp` (행 363–365)은 `engine_fixtures.start_submission_history(self)`를 부른다. 이 도우미가 만드는 상태는 다음과 같다.
  - `state_fixtures.start_active_copy`가 `restore_template(active_instance, config=ACTIVE_CONFIG)`의 사본을 준다. 이것이 2단이다.
  - 그 사본에 실제 `ResearchEngine`을 연다.
  - 실행 중인 maintenance 실행 `EX-history`를 등록한다. 이 실행은 봉인된 입력 번들 `BA-history-input`(프롬프트, `context.json`, `schema.json`)을 갖는다.
  - `runs/EX-history/workspace`에 제출 도구를 설치한다.
  - 테스트 객체에 `engine`, `workspace`, `context`, `schema`, `transport`, `binding`, `output`을 채운다. 여기서 `output`은 `summary='Exact é diagnostic'`이고 `seal_response`가 번들 하나를 붙인 유효한 출력이다.

  주석대로 모델 호출도 Lean 호출도 없다. `FixtureAdapter` 패치는 테스트가 끝날 때까지 유지된다.
- 클래스 도우미 메서드는 없다. 제출은 `engine_fixtures.submit_history(test, request_id, raw)`로 한다. 이 도우미는 `raw`를 `draft.json`에 쓰고, 요청을 `transport.receive(request, publish=engine._publish_control_request)`로 실제 중앙 수신에 넘긴다.

### `test_orphan_impact_is_returned_then_default_bundle_preserves_raw_git_input` (행 367–400)
- 성질: 두 단계를 본다.
  1. 입력에 없는 레코드(`read-source`)를 영향 집합으로 선언한 번들은 중앙 검사에서 반려된다. 실행은 계속 돌고, 미해결 문제로 `integration.mutation_root`가 남는다.
  2. `integration_bundles`가 없는 출력은 기본 번들 하나로 받아들여진다. 이때 게시된 원 바이트(비ASCII, 들여쓰기 3칸)가 그대로 보존된다. 보존된 바이트와 봉인 입력에서 나눈 번들은 원래 출력에서 나눈 것과 같고, 그 번들이 적용된다.
- 준비: `setUp`(2단). 반려용 출력은 번들의 `impact_set`을 `["read-source"]`로 바꾼 것이다. 기본용 출력은 `integration_bundles`를 빼고, `report`를 결합 문자·한글·이모지·줄바꿈이 섞인 문자열로 바꾼 것이다. 이 출력을 `json.dumps(..., ensure_ascii=False, indent=3)`로 인코딩한다.
- 실행:
  - `submit_history(self, "CT-impact", ...)`로 반려용을 제출하고 `_submission_check_summary`를 부른다.
  - `submit_history(self, "CT-default", raw)`로 기본용을 제출한다.
  - 엔진을 `ResearchEngine(self.repo, self.identifier)`로 다시 연다(재시작).
  - `store.read`로 봉인 출력과 입력 번들의 `context.json`을 읽는다.
  - `integration.split_bundles`를 원래 출력과 봉인 입력 쪽에 각각 부르고, 마지막으로 `_apply_submission_bundles(action, restored, {}, "EX-history", fixed, [])`를 부른다.
- 단언:
  - 첫 영수증의 `state`가 `"rejected"`이고, 실행 `status`는 `"running"`이다. 요약의 `unresolved`에 `rule_id == "integration.mutation_root"`가 있다.
  - 둘째 영수증은 `"accepted"`다. 재시작 뒤 `submission_intent.output_ref`의 저장 바이트가 `raw`와 같고, 해석하면 `integration_bundles`가 없다.
  - 두 번들 분할 결과가 같고 길이가 1이며, 번들의 `authority_refs`가 `[action["grant_id"]]`다.
  - 적용 결과의 `status`가 `"accepted"`이고 번들이 하나다. `store.load()`로 읽은 저장 런타임의 `integrations`에 그 `integration_id`가 있다. 적용 뒤에도 저장 바이트가 `raw`와 같다.
- 대역: 없음. 실제 Git 저장소 위의 실제 엔진이다.
- 비고: 함수 안의 `from do_math import integration`은 모듈 머리(행 14)의 import와 겹친다.

### `test_rejected_corrected_replayed_and_snapshot_bound_central_checks` (행 402–454)
- 성질: 여러 성질을 한 시나리오로 본다.
  - 반려된 중앙 검사도 게시 ID와 원 바이트 증거를 남기고, 실행과 권한은 유지된다.
  - 재시작 뒤 같은 요청을 재생하면 로컬 바이트가 바뀌었어도 원래 영수증을 돌려주고 새로 게시하지 않는다.
  - 선택적인 로컬 검사 이력이 깨져 있어도 제출을 막지 않는다.
  - 고친 제출이 받아들여지면 봉인 수 2, 미해결 0이 된다.
  - 요약은 스냅숏에 묶여 있어, 과거 헤드의 요약은 그대로다.
  - 검사 이벤트가 빠지거나 봉인 바이트가 변조되면 요약이 `incomplete`가 된다.
- 준비: `setUp`(2단). 반려용 초안은 `report`를 뺀 출력의 정본 JSON이다.
- 실행: 일곱 단계를 차례로 밟는다.
  1. `submit_history(self, 'CT-bad', bad)`로 반려용을 제출한다.
  2. `_submission_check_summary(first_head, runtime)`로 첫 요약을 잰다.
  3. 엔진을 다시 열고 `draft.json`을 `b'{changed local bytes'`로 바꾼 뒤, `_publish_control_request(request)`로 같은 요청을 재생한다.
  4. `checks/broken.json`에 깨진 바이트를 쓰고 `submit_history(self, 'CT-good', ...)`로 고친 제출을 보낸다.
  5. 과거 헤드를 `store.load(first_head)`로 읽어 그 요약을 다시 잰다.
  6. `CT-good`을 `_publish_control_request`로 재생한다.
  7. 두 가지 손상을 흉내 낸다. 하나는 `submission_checked` 이벤트를 뺀 런타임 사본이다. 다른 하나는 `store._store.publish`로 봉인 경로 덮어쓰기를 시도하는 것과, 읽기를 가로채 변조된 바이트를 주는 것이다.
- 단언:
  - 반려 영수증의 `state`가 `'rejected'`이고 `publication_id`가 있다. 실행 `status`는 `'running'`이고, `authority_revocation`이 없다.
  - 첫 요약은 `status='verified'`, `seal_count=1`이고 `unresolved`가 비지 않았다.
  - 저장된 영수증의 `payload.submission_check.artifacts` 가운데 `/output.json` 행의 바이트가 `bad`와 같고, 그 sha256이 행의 값과 같다.
  - 재생 영수증은 `'rejected'`다. 헤드는 첫 헤드 그대로이고, `result`가 원래 반려의 `result`와 같다.
  - 고친 제출은 `'accepted'`다. 최종 요약은 `verified`, `seal_count=2`, `unresolved=[]`다. 규칙 실패 수의 합이 첫 요약과 같다(실패 이력은 사라지지 않는다). 실행은 `'stopping'`이다.
  - 과거 헤드의 요약이 첫 요약과 같다.
  - `CT-good` 재생도 `'accepted'`이고, 봉인 수는 2 그대로다.
  - `submission_checked` 이벤트를 뺀 런타임의 요약은 `'incomplete'`다.
  - 봉인 경로 덮어쓰기는 `ValueError`를 메시지 조각 `'immutable'`로 던진다.
  - `do_math.repository.VERIFIED_ARTIFACTS`를 비우고 초안 경로 읽기가 `b'tampered'`를 주게 하면, 요약이 `'incomplete'`다.
- 대역: 마지막 단계만 대역을 쓴다. `patch.dict('do_math.repository.VERIFIED_ARTIFACTS', clear=True)`로 "이 행을 아직 대조하지 않은 프로세스"를 흉내 낸다. `patch.object(engine.store, 'read', side_effect=...)`로 초안 경로만 변조된 바이트를 준다.
- 비고: 주석(행 448–449)은 이 프로세스가 이미 초안을 대조했으므로 다시 비교하지 않으며, 메모가 없는 프로세스는 바이트를 비교해 거부한다고 설명한다(`이음새-정본.md` §3).

## WaitOwnershipTests (행 457–497)

- 기반: `unittest.TestCase`. 표지, 설정 훅, 클래스 속성은 없다.
- 도우미 `receive(kind, *, creates_wait=True)` (행 458–486)가 메모리 엔진 대역을 만들고 `_receive_submission`을 한 번 부른다. 구성은 다음과 같다.
  - 엔진: `bare_engine()`. `head='fixed'`이고, 인스턴스 수명 상태는 `initializing`이다.
  - 런타임: 실행 `EX-one`(`status='ended'`)이 `submission_intent`(`output_ref='out'`, `extensions_ref='ext'`, `check_ref='check'`)를 갖는다.
  - 저장소: `ResearchRepository` autospec이다. `git_dir`는 매번 새 uuid 값이다.
  - 행동: `AC-one`(`intent_interpretation`, 대상 `UI-one`).
  - `_apply_submission_bundles`는 `status='accepted'`, 빈 번들을 돌려주는 autospec이다. `creates_wait`가 참이면 이 호출 안에서 `waiting_actions['AC-one']`에 `kind` 대기를 새로 만든다. 거짓이면 호출 전에 같은 대기가 이미 있다.
  - `_remove_action`과 `_record_task_receipt`는 아무것도 하지 않는 autospec이다.
  - `do_math.engine.submission.read_sealed_submission`을 봉인 결과 사전으로 패치한다. 주석대로 봉인은 따로 검사되며, 여기서는 대기 소유 규칙만 본다.

  반환값은 호출 뒤의 런타임이다. 준비 단계는 메모리 엔진 대역이다.

### `test_new_user_wait_survives_successful_response` (행 488–493)
- 성질: 응답을 받아들이는 도중 영역 적용이 새로 만든 사용자 쪽 대기는 성공한 응답 뒤에도 남는다.
- 준비: 클래스 절의 `receive` 도우미를 `creates_wait=True`로 쓴다.
- 실행: `receive(kind)`.
- 단언: 반환 런타임의 `waiting_actions`에 `AC-one`이 있고, 그 `kind`가 준 값과 같다.
- 대역: 클래스 절의 도우미가 설치하는 autospec 넷과 `read_sealed_submission` 패치.
- 비고: `subTest(kind=...)`는 `import_application_authority`와 `import_user_decision` 두 경우다. 제품 `_receive_submission`은 수신 전에 저장한 대기(`previous_wait`)가 `submission_publication`이나 `impact_review`이고 지금 대기와 같을 때만 지운다. 이 테스트에서는 수신 전 대기가 없으므로 새 대기가 남는다.

### `test_resolved_publication_and_impact_waits_are_removed` (행 495–497)
- 성질: 이 응답이 해소하는 게시 대기와 영향 검토 대기는 받아들인 뒤 지워진다.
- 준비: 클래스 절의 `receive` 도우미를 `creates_wait=False`로 쓴다. 대기가 호출 전에 있다.
- 실행: `kind`가 `submission_publication`인 경우와 `impact_review`인 경우로 `receive`를 부른다.
- 단언: 두 경우 모두 반환 런타임의 `waiting_actions`에 `AC-one`이 없다.
- 대역: 클래스 절과 같은 autospec 넷과 패치.
- 비고: 두 경우를 `for` 문으로 돌며 `subTest`는 쓰지 않는다. 그래서 첫 경우가 실패하면 둘째 경우는 돌지 않는다.

## ReceiptPreservationTests (행 500–530)

- 기반: `unittest.TestCase`. 표지, 설정 훅, 도우미는 없다.

### `test_dependency_impact_keeps_execution_and_activity_receipts_unchanged` (행 501–510)
- 성질: 지식 의존 영향을 적용해도 이미 끝난 실행과 활동의 영수증은 바뀌지 않는다. 영향 기록은 이력에 남는다.
- 준비: 1단. 인스턴스에는 지식 `KN` 하나가 있다. 런타임에는 끝난 실행 `EX`(`outcome='output_accepted'`), 끝난 활동 `AY`, 빈 대기열이 있다.
- 실행: `knowledge._apply_impact_effects(instance, runtime, {'EX', 'AY'}, {'KN'}, reason='Source changed', impact_digest='a'*64)`.
- 단언: 바뀐 런타임의 `executions`와 `activities`가 원래와 같다. `history[-1]['affected_ids']`가 `['AY', 'EX']`다.
- 대역: 없음.

### `test_accepted_batch_opens_one_plan_and_preserves_all_evidence` (행 512–530)
- 성질: 연구 작업 응답 하나를 받아들이면, 지식 후보의 수(3, 1, 0)와 관계없이 연구 계획 행동이 정확히 하나 열린다. 그 행동은 받아들인 모든 지식을 증거로, 실행을 영수증으로 가리킨다. 사용자가 직접 들여온 비형식 후보는 계획을 열고, `plan_nonformal=False`인 형식 후보는 형식 검사를 연다.
- 준비: 메모리 엔진 대역이다.
  - 후보 수마다 새 `routing_engine()`을 만든다. `knowledge_io.ensure_ontology`로 온톨로지를 채우고, 활성 과제 `TK`와 실행 중인 연구 작업 실행 `EX`를 둔다.
  - 출력은 `outcome='partial'`, `remaining_work=['Open obligation']`이다. 지식은 `knowledge_candidate(title='K<i>', lean_code='', declaration_names=[])`로 만든 `count`개다.
- 실행:
  - `engine._apply({'id': 'AC', 'role': 'research_work', 'target': 'TK'}, output, 'EX')`.
  - 이어서 `knowledge_io.import_candidate({}, {}, ...)`를 두 번 부른다. 한 번은 비형식 후보로, 한 번은 기본 후보(형식)로 `plan_nonformal=False`를 준다.
- 단언:
  - 대기열의 `research_plan` 행동이 정확히 1개다. 그 `evidence_refs` 집합이 인스턴스 지식 ID 집합과 같고, `receipt_refs`가 `['EX']`다.
  - 직접 들여온 비형식 후보의 대기열 역할이 `['research_plan']`이다.
  - 형식 후보(`plan_nonformal=False`)의 대기열 역할이 `['formal_check']`다.
- 대역: `routing_engine`이 넣는 autospec(`_bind_revision_action`, `_cancel_selected_revision_targets`, `_record_output_questions`)과 `NoRepository` 저장소.
- 비고: 세 후보 수를 `for` 문으로 돌며 `subTest`는 쓰지 않는다.

## FixedResearchReferenceTests (행 533–540)

- 기반: `unittest.TestCase`. 표지, 훅, 도우미는 없다.

### `test_fixed_sources_and_collectable_workspace_paths` (행 534–540)
- 성질: 고정 원천은 `None`으로, 수집 가능한 작업 공간 좌표는 그 상대 경로로 해석된다. 할당되지 않은 레코드, 탈출 경로, 입력 폴더, 절대 경로, 버림용 `.scratch` 경로는 거부된다.
- 준비: 1단. 원천 집합은 `{'proposal'}`이다.
- 실행: `submission.fixed_research_reference_path(reference, {'proposal'})`.
- 단언: `'proposal'`은 `None`을 돌려주고, `'workspace:result.txt'`는 `'result.txt'`를 돌려준다. 거부 다섯 경우는 모두 `ValueError`를 던진다. 예외 유형만 보고 메시지는 고정하지 않는다.
- 대역: 없음.
- 비고: `subTest(reference=...)` 다섯 경우는 `KN-unassigned`, `workspace:../escape`, `workspace:input/source.txt`, `workspace:C:/escape`, `workspace:.scratch/discarded.txt`다.

## PartialCaptureTests (행 543–570)

- 기반: `unittest.TestCase`. 표지, 훅, 도우미는 없다.

### `test_only_independent_local_errors_can_be_captured` (행 544–570)
- 성질: 후보 전체가 통과하지 못해도, 문제가 독립 번들 하나에 국한되고 다른 번들이 온전하면 후보 전체를 포착할 수 있다(`capture_eligible`). 모든 번들이 실패하거나, 번들이 서로 이어져 있거나, 주 출력 모양이 깨지면 포착하지 못한다.
- 준비: 1단. 임시 작업 공간에 `record_fixtures.research_work_context()`(연구 작업 문맥, `execution_id='EX-partial'`)와 `contracts.action_schema`로 도구를 설치한다. 출력은 `two_observation_output()`이다. 이 출력은 번들 `IN-A`(`output`, `output/knowledge/0`)와 `IN-B`(`output/knowledge/1`)를 가지며, 둘째 지식의 의존을 `['KN-not-supplied']`로 바꾼다.
- 실행: `seal_submission(workspace, execution_id='EX-partial', ..., raw_output=canonical_json(value))`로 초안 파일 없이 바이트를 직접 넘긴다. 이 방식으로 네 변형을 봉인한다.
- 단언:
  - 원래 출력은 `passed`가 거짓이지만 `capture_eligible`이 참이고, `artifacts['output.json']`이 넘긴 바이트와 같다.
  - 첫 지식도 없는 의존을 갖는 `all_bad`는 포착하지 못한다.
  - 둘째 지식이 첫 지식 `'A'`에 의존하는 `connected`도 포착하지 못한다.
  - `report`를 뺀 `malformed`도 포착하지 못한다.
- 대역: 없음.
- 비고: 제품 규칙은 `submission.capture_eligible`의 docstring("A whole immutable candidate may contain independently returnable members")과 그 본문이다. 본문은 문제 행마다 소유 번들이 하나여야 하고, 실패하지 않은 번들이 하나 이상 남아야 한다고 정한다.

## PartialCaptureGitTests (행 573–653)

- 기반: `unittest.TestCase`. 표지와 클래스 속성은 없다.
- `setUp` (행 574–618)은 `start_submission_history(self)`(2단) 위에 부분 포착 시나리오를 쌓는다. 순서는 다음과 같다.
  1. 연구 작업 행동 `AC-partial`의 수명 관문을 통과시키고, 실행 `EX-partial`을 등록한다.
  2. `research_fixtures.candidate()`로 과제 후보를 만든다. 그 실행의 프로필과 행동의 grant를 붙인 뒤 `contracts.task_candidate_record(..., task_id='TK-partial')`로 과제 레코드를 만든다. 레코드는 `planned` 상태이고, 발생 조건은 `always`다.
  3. 검토 실행 `EX-review`를 등록하고, `approve_contract`로 계약 검토를 봉인한다.
  4. 행동과 실행의 대상을 과제로 잇고, `contract_sha256`을 기록한 뒤 저장한다.
  5. 실행에 grant, 입력 번들 `BA-partial-input`, 입력 스냅숏, 결정 근거(`capture_decision_basis`), 거버넌스 판을 채운다.
  6. `runs/EX-partial/workspace`에 연구 작업 문맥으로 도구를 설치한다. 문맥에는 과제, 종류 정의, grant가 든다. 입력 번들의 `context.json`과 `schema.json`을 게시하고 결속을 발급한다.
  7. `self.output`을 `two_observation_output()`으로 만들고 두 가지를 바꾼다. 하나는 `output` 좌표를 `IN-A`에서 `IN-B`로 옮기는 것이다. 주석대로 독립인 A 레코드가 과제 처분 없이 들여와지도록 포착 이음새를 일부러 시험한다. 다른 하나는 둘째 지식의 의존을 `['KN-not-supplied']`로 바꾸는 것이다.

  결과로 `IN-A`는 온전하고 `IN-B`는 실패하는 부분 후보가 된다.

### `test_early_submission_preview_reload_and_partial_application` (행 620–642)
- 성질: 부분 후보는 미리보기에서 번들별 결과(통과, 반려)를 게시 없이 보여 준다. 조기 제출로 봉인되고, 재시작 뒤 봉인에서 되읽혀 번들별로 적용된다. 다시 적용하면 이미 받아들인 번들은 `already_accepted`다.
- 준비: 클래스 절의 `setUp`(2단). 출력의 정본 바이트를 `draft.json`에 쓴다.
- 실행:
  - `engine._preview_submission(execution, {'draft_path': 'draft.json'})`로 미리보기한다.
  - `transport.receive(request, publish=engine._publish_control_request)`로 제출한다(`request_id='CT-partial'`).
  - `ResearchEngine(self.repo, self.identifier)`로 다시 열고 `read_sealed_submission`으로 되읽는다.
  - `_apply_submission_bundles`를 두 번 부른다.
- 단언:
  - 미리보기 뒤 헤드가 그대로이고, 번들 상태가 `['preview_passed', 'returned']`다.
  - 영수증은 `'accepted'`다.
  - 되읽은 검사의 `passed`가 거짓이고, 요약 `status`는 `'verified'`다.
  - 첫 적용의 번들 상태가 `['accepted', 'returned']`이고, 둘째 적용의 첫 번들은 `'already_accepted'`다.
- 대역: 없음.

### `test_native_final_reaches_the_same_partial_candidate` (행 644–653)
- 성질: 조기 제출 없이 제공자의 네이티브 최종 출력으로 같은 부분 후보를 보내도, 같은 중앙 포착을 거쳐 같은 번들별 결과에 이른다.
- 준비: 클래스 절의 `setUp`(2단). `engine_fixtures.native_result(execution, context, raw, workspace)`로 네이티브 결과를 만든다. 이 픽스처는 프로세스 없이 순수 프로토콜 증거만 만든다.
- 실행: `_collect_submitted_result(execution, result, context, schema, workspace)`로 포착한 뒤 `_receive_submission(..., preserved=True)`를 부른다.
- 단언: 포착의 `collection`이 `'sealed_submission'`이고, `rejected_submission` 키가 없다. 수신 결과의 번들 상태가 `['accepted', 'returned']`다.
- 대역: `native_result`의 합성 제공자 증거.

## KnowledgeConnections (행 656–687)

- 기반: `unittest.TestCase`. 표지, 훅, 도우미는 없다. 두 테스트 모두 `routing_engine()` 메모리 엔진 대역에서 `_apply`를 직접 부른다. 인스턴스에는 `sources=[]`, `kind_definitions={}`, `config.reviewers=2`를 넣는다.

### `test_research_receipt_creates_separate_knowledge_authorities` (행 657–676)
- 성질: 연구 작업 영수증이 형식 정리를 들여올 때, 지식 레코드에는 Lean 코드, 형식 결과, 검토가 직접 붙지 않는다. 대신 별도의 형식 결과 레코드와 설명 레코드가 생긴다. 과제에는 결과 하나가 붙고, 과제는 `waiting`으로 간다.
- 준비: 메모리 엔진 대역. 활성 과제 `TK-work`와 끝난 실행 `EX-work`를 둔다. 출력은 `outcome='submitted'`이고, `theorem t : True := by trivial` 정리 하나를 담는다.
- 실행: `engine._apply({"id": "AC-work", "role": "research_work", "target": "TK-work"}, output, "EX-work")`.
- 단언: 들여온 레코드에 `lean_code`, `formal`, `reviews` 키가 없다. `formal_result_id`가 `instance['formal_results']`에, `exposition_id`가 `instance['expositions']`에 있다. 과제 결과가 1개이고 과제 상태는 `"waiting"`이다.
- 대역: `routing_engine`의 autospec 셋과 `NoRepository`.

### `test_independent_bundle_does_not_repeat_the_task_report` (행 678–687)
- 성질: 응답을 소유하지 않는 독립 번들(`owns_response=False`)을 적용해도 과제 보고가 다시 붙지 않는다.
- 준비: 메모리 엔진 대역. `waiting` 과제 `TK-work`에 이미 결과 `{"report": "already accepted"}`가 하나 있다.
- 실행: `engine._apply(..., output, "EX-work", owns_response=False)`.
- 단언: 과제의 `results`가 원래 목록 그대로다.
- 대역: `routing_engine`의 autospec 셋과 `NoRepository`.

## BundleConnections (행 690–737)

- 기반: `unittest.TestCase`. 표지, 훅, 도우미는 없다.

### `test_independent_commit_survives_later_bundle_failure_and_retry` (행 691–737)
- 성질: 한 응답의 독립 번들 둘 가운데 뒤 번들이 실패해도, 먼저 커밋된 번들은 되돌려지지 않는다. 작업 영수증은 모든 번들이 끝날 때까지 기록되지 않는다. 같은 응답을 다시 적용하면 커밋된 번들은 `already_accepted`로 건너뛰고, 다시 게시하지도 영역 효과를 되풀이하지도 않는다.
- 준비: 메모리 엔진 대역. `routing_engine()`에 `head="input-snapshot"`, 실행 `EX-work`(입력 스냅숏이 같은 헤드), `accepted_titles=[]`를 둔다. 저장소는 `ResearchRepository` autospec이다.
  - `save_validated`는 받은 후보의 인스턴스와 런타임 사본을 `published`에 쌓고 `snapshot-<n>`을 돌려준다. `load`는 마지막 게시를 돌려준다.
  - `_validate_bundle_current`는 그냥 autospec이다. `_validate_bundle_candidate`는 받은 상태를 그대로 후보로 돌려준다.
  - `_apply`는 지식 제목이 `"invalid"`이면 `ValueError('rejected candidate')`를 던지고, 아니면 `accepted_titles`에 제목을 더한다.
  - 영역 후속 함수 아홉(`_apply_model_metadata`, `_apply_extensions`, `_apply_revision_followup`, `_apply_action_resolutions`, `_apply_question_resolutions`, `_resolve_failed_actions`, `_ensure_academic_followup`, `_consume_action_events`, `_record_task_receipt`)은 autospec이다. `_defer_review_for_research`는 `False`를 돌려준다.
  - 출력의 번들은 `IN-good`(`output`, 지식 0 `"valid"`)과 `IN-bad`(지식 1 `"invalid"`)다.
- 실행: `engine._apply_submission_bundles(action, output, {}, "EX-work", context, [])`를 두 번 부른다.
- 단언:
  - 첫 호출의 `retry_bundle_ids`가 `["IN-bad"]`다. `accepted_titles`가 `["valid"]`이고 게시는 1번이다. `_record_task_receipt`는 불리지 않았다. 게시된 런타임의 `integrations`에 `IN-good`이 있다.
  - 둘째 호출의 첫 번들 상태는 `"already_accepted"`다. `accepted_titles`는 그대로 `["valid"]`이고, 게시 수도 1 그대로다.
- 대역: 위의 저장소 autospec과 `side_effect`, 엔진 메서드 autospec 열셋(검증 콜백 둘, `_apply`, 영역 후속 함수 아홉, `_defer_review_for_research`).

## CentralSubmissionEvidence (행 740–785)

- 기반: `unittest.TestCase`. 표지와 설정 훅은 없다.
- 도우미 `fixture(root)` (행 741–754)가 준비를 만든다.
  - 엔진은 `routing_engine()`이고, `config.max_output_repairs=1`이다.
  - 출력은 `{"summary": "preserved exact draft"}`이고, 초안에는 `indent=4`로 인코딩한 바이트를 쓴다.
  - 문맥은 maintenance 행동이다. 스키마는 `summary` 하나를 요구하는 식별 스키마이고, `install_tools(root, context, schema, 10000000)`로 도구를 설치한다.
  - `_response_schema`를 그 스키마를 돌려주는 autospec으로 바꾼다.
  - 실행 레코드 `EX-work`는 `stopping` 상태다.

  반환값은 `(engine, output, context, execution)`이다. `test_unsealed_runner_output_is_preserved_but_cannot_be_integrated`만 이 도우미를 쓴다.

### `test_unsealed_runner_output_is_preserved_but_cannot_be_integrated` (행 756–772)
- 성질: 중앙 제출 경로를 거치지 않은 러너 출력은 보존되지만 통합되지 않는다. 적용 단계에는 `submission.sealed_candidate` 문제가 넘어가고, 저장 artifact에는 출력이 들어간다.
- 준비: 메모리 엔진 대역. `fixture(root)`로 만들고 실행을 런타임에 등록한다. `_apply_submission_bundles`는 `status="returned"`을 돌려주는 autospec이다. `_remove_action`, `_record_task_receipt`, `_save`도 autospec이다.
- 실행: `engine._receive_submission(context["action"], {"output": output}, "EX-work", context, engine._response_schema(...), root)`. 실행에 `submission_intent`가 없으므로 비봉인 분기를 탄다.
- 단언: 반환 `status`가 `"returned"`다. `_apply_submission_bundles`의 마지막 위치 인자(문제 목록)에 `rule_id == "submission.sealed_candidate"`가 있다. `_save`의 첫 인자(artifact 사전)에 `/output.json`으로 끝나는 경로가 있다.
- 대역: 엔진 메서드 autospec 다섯과 `routing_engine`의 대역.

### `test_retry_receives_prior_accepted_response_across_multiple_attempts` (행 774–785)
- 성질: 수리 재시도의 문맥은 여러 대에 걸친 계승 사슬(`EX-two`의 `continuation_of`가 `EX-one`)을 따라가, 조상 실행이 이미 받아들인 응답 해시와 통합 ID를 받는다.
- 준비: 메모리 엔진 대역. `routing_engine()`에 실행 `EX-one`(빈 행동)과 `EX-two`(`continuation_of='EX-one'`)를 둔다. 통합 영수증 `IN-report`는 `execution_id='EX-one'`, `response_sha256='a'*64`다. 문제는 `integration.issue("integration.candidate", "output", "repair this")`로 만든다.
- 실행: `engine._submission_repair_context(context, {"continuation_of": "EX-two", "repair": {"issues": [issue]}})`.
- 단언: `context["accepted_response"]`가 `{"integration_id": "IN-report", "response_sha256": "a"*64}`다. `submission_failures`가 `[issue]`이고, `accepted_integration_ids`가 `["IN-report"]`다.
- 대역: `routing_engine`의 대역.
- 비고: 클래스 도우미 `fixture`를 쓰지 않는다.

## ContinuationConnections (행 788–841)

- 기반: `unittest.TestCase`. 표지, 훅, 도우미는 없다.

### `test_same_domain_callback_is_available_to_preview_without_publication` (행 790–812)
- 성질: 번들 후보 적용 콜백 `_apply_bundle_candidate`는 호출자가 준 상태 사본에만 영역 효과를 내고, 엔진 자신의 상태를 바꾸거나 저장하지 않는다. 그래서 미리보기가 같은 콜백을 쓸 수 있다.
- 준비: 메모리 엔진 대역. `routing_engine()`에 `head="snapshot"`과 실행 `EX-one`을 둔다. 영역 후속 함수 일곱은 autospec이다. `_defer_review_for_research`는 `False`를 돌려준다. `_save`는 `AssertionError("preview cannot publish")`를 던진다. `_apply`는 런타임 이력에 `{"kind": "candidate"}`를 더한다. 원래 `(instance, runtime)`의 사본을 두 벌 뜬다.
- 실행: `engine._apply_bundle_candidate(instance, runtime, bundle, action={"role": "research_work"}, execution_id="EX-one", extensions={})`. 번들은 `IN-one`이고 `owns_response=True`다.
- 단언: 엔진의 `(instance, runtime)`이 원래와 같다. 넘긴 사본 런타임의 `history`가 `[{"kind": "candidate"}]`다. `_save`와 `_record_task_receipt`는 불리지 않았다.
- 대역: 엔진 메서드 autospec 열.

### `test_bundle_requires_live_prior_hash_and_review_only_for_impact_beyond_the_closure` (행 814–841)
- 성질: 지식 변경 번들의 영향 검증은 세 규칙을 따른다.
  - 선언한 영향이 계산한 폐포와 같으면 통과한다.
  - 영향 선언을 빠뜨려도 폐포를 적용하므로 검토가 필요 없다.
  - 폐포 밖 레코드를 선언하면 영향 검토가 필요하다.
  - 입력 뒤에 레코드가 바뀌어 이전 해시가 맞지 않으면 거부된다.
- 준비: 메모리 엔진 대역.
  - `routing_engine()`에 `knowledge_io.import_candidate`로 정리 하나를 들여오고, 그것에 의존하는 과제 `TK-dependent`와 무관한 과제 `TK-other`를 둔다.
  - 번들은 `IN-revision`이다. `knowledge_changes`에 요약 변경 하나를 담고, `impact_set=["TK-dependent"]`, `previous_hashes`는 현재 `knowledge.content_hash`다.
  - 실행 `EX-author`의 입력 스냅숏은 `"fixed"`다.
- 실행: `engine._validate_bundle_impacts(instance, runtime, bundle, action=..., execution_id="EX-author")`를 네 가지 번들로 부른다.
- 단언:
  - 원래 번들은 예외 없이 지난다.
  - `impact_set=[]`인 번들은 `{}`를 돌려준다.
  - `impact_set`에 `TK-other`를 더한 번들은 `integration.ImpactReviewRequired`를 던진다.
  - 지식 제목을 바꾼 뒤 원래 번들은 `ValueError`를 정규식 `"hash|changed"`로 던진다. 사유를 두 낱말 가운데 하나로 느슨하게 고정한다.
- 대역: `routing_engine`의 대역. `NoRepository` 저장소에서 읽기가 일어나지 않는 경로다.
- 비고: 주석(행 834)은 선언과 관계없이 계산한 폐포를 적용하므로 누락에는 검토가 필요 없다고 설명한다.

## LivePreviewConnections (행 844–897)

- 기반: `unittest.TestCase`. 표지, 훅, 도우미는 없다.

### `test_installed_preview_uses_receiver_domain_callback_without_publication` (행 845–897)
- 성질: 작업 공간에 설치된 실제 명령 `check_submission.py --preview`는 자식 프로세스에서 제어 전송으로 미리보기를 요청한다. 엔진은 수신자의 영역 콜백 `_apply_bundle_candidate`를 정확히 한 번 쓰고, 아무것도 게시하지 않은 채 `previewed` 영수증을 돌려준다.
- 준비: 메모리 엔진 대역에 실제 자식 프로세스를 더한다.
  - `routing_engine()`의 작업 공간은 임시 루트이고, `max_artifact_bytes=10000000`, `head="fixed-snapshot"`이다.
  - `ControlTransport(root/"transport")`로 `issue("EX-work", "GR-one")`을 발급한다.
  - 스키마는 `contracts.with_integration_schema(schema_for("maintenance"))`이고, 출력은 번들 `IN-one` 하나를 가진 maintenance 출력이다. 도구를 설치하고 `draft.json`을 쓴다.
  - 실행 `EX-work`를 등록한다(`running`, `input_bundle="BA-input"`). 저장소는 autospec이며, `read`는 `schema.json`이면 스키마를, 아니면 작업 공간의 `input/submission/context.json` 바이트를 준다.
  - `_clock_guard`는 `usable` autospec이다. `_validate_bundle_current`, `_validate_bundle_candidate`와 영역 후속 함수 여섯은 autospec이다. `_defer_review_for_research`는 `False`를 돌려준다.
- 실행: `subprocess.Popen([sys.executable, "-B", "<workspace>/input/tools/check_submission.py", "--output", "draft.json", "--preview", "--wait-seconds", "20"], cwd=workspace)`로 명령을 띄운다. 25초 상한 안에서 `transport.pump(engine._publish_control_request)`를 0.02초 간격으로 되풀이한다.
- 단언:
  - 자식의 종료 코드가 0이다.
  - `_apply_bundle_candidate`(`wraps`) 호출 수가 1이다.
  - 엔진의 `(instance, runtime)`이 호출 전과 같다.
  - `store.save_with_state`와 `store.save_validated`가 불리지 않았다.
  - 전송의 첫 영수증은 `state="previewed"`이고, `result.passed`가 참이며, `publication_id` 키가 없다.
- 대역: `mock.patch("do_math.engine.governance.authorize", return_value={"allowed": True})`, `_apply_bundle_candidate`의 `wraps` 패치, 위의 autospec들.
- 비고:
  - 실제 자식 프로세스(Python 인터프리터 시작과 설치된 zip 도구)를 쓴다.
  - 폴링 상한은 25초, 간격은 0.02초다. 상한을 넘기면 `kill`한다.
  - `transport._receipts`(비공개 속성)를 직접 읽는다.

## TaskReceiptTests (행 900–935)

- 기반: `unittest.TestCase`. 표지, 훅, 도우미는 없다.

### `test_task_receipt_occurs_once_after_the_complete_bundle_result` (행 901–935)
- 성질: 봉인된 제출을 받을 때, 모든 번들 결과가 끝난 뒤에만 과제 영수증이 한 번 기록된다. 번들이 엔진 소유 재시도로 반려되면 영수증은 기록되지 않는다. 그때 실행은 `stopping`에 머물고, 대기열 대신 `next_owner="engine"` 대기가 생긴다.
- 준비: 메모리 엔진 대역.
  - 경우마다 임시 작업 공간에서 `research_fixtures.sealed_maintenance_submission(workspace, 'EX-work')`로 실제 중앙 봉인 바이트를 만든다. intent에 `extensions_ref`와 `check_ref`를 채운다.
  - `routing_engine()`의 저장소를 autospec으로 바꾼다. `read`는 봉인 artifact 사전에서 답하고, `git_dir`는 새 uuid다.
  - 실행 `EX-work`는 `stopping`이며, 받아들인 `submit_intent` 영수증과 artifact 행을 갖는다.
  - `_save`, `_resolve_failed_actions`, `_ensure_academic_followup`은 autospec이다.
  - `_apply_submission_bundles`는 순서 목록에 `"all bundles"`를 더하고 경우별 결과를 돌려준다. `_record_task_receipt`는 `"task receipt"`를 더한다.
- 실행: `engine._receive_submission(action, {"output": output}, "EX-work", context, engine._response_schema(action), workspace)`.
- 단언:
  - `owner=None`(받아들임)이면 순서가 `["all bundles", "task receipt"]`이고, 실행이 `"ended"`다.
  - `owner="engine"`(반려, 엔진 소유)이면 순서가 `["all bundles"]`이고, 실행이 `"stopping"`이다. 이때 대기열이 비고, `waiting_actions[AC-one].next_owner`가 `"engine"`이다.
- 대역: 저장소 autospec과 엔진 메서드 autospec 다섯.
- 비고: `subTest(owner=...)` 두 경우는 `None`과 `"engine"`이다. 봉인 바이트는 실제 `seal_submission`이 만든다.

## SubmissionPublicationWaitTests (행 938–978)

- 기반: `unittest.TestCase`. 표지, 훅, 도우미는 없다.

### `test_sealed_response_waits_for_a_record_change_after_a_failed_identity_check` (행 939–978)
- 성질: 받아들인 봉인 응답의 게시가 활성 신뢰 환경의 식별 검사 실패로 막히면, 응답은 `submission_publication` 대기로 남는다. 파일을 복원하기만 해서는 재시도되지 않고, 사용자가 도구 모음 기록을 다시 기록해야 대기가 풀려 게시된다. 상태 조회는 식별 검사나 파일 스캔을 하지 않는다.
- 준비: 2단. `start_submission_history(self)`를 테스트 안에서 직접 부른다. `submit_history(self, 'CT-environment', raw)`로 유효한 출력을 제출해 받아들여지게 한다. 활성 신뢰 환경의 도구 모음 실행 파일 옆 `lake.exe`의 원래 바이트를 저장해 둔다.
- 실행:
  1. `engine._apply`를 `gated_apply`로 감싼다. `gated_apply`는 적용 전에 `trust_validation.require_active_environment(..., current_identity=True)`를 부른다. 주석대로 영역 소비자만 합성이고, 게시 관문과 대기는 실제다.
  2. `lake.exe`를 `b'accidentally replaced launcher'`로 바꾸고 `_receive_submission(..., preserved=True)`를 부른다.
  3. 대기를 확인한 뒤 `lake.exe`를 원래 바이트로 되돌린다. `_receive_submission`이 `AssertionError('retried before a change')`를 던지도록 패치한 채 `_retry_submission_publications()`를 부른다.
  4. `fixture_setup_lean(...)` 안에서 `setup_lean.rerecord(['unused'], <기록 폴더>, <evidence>, None)`로 다시 기록한다.
  5. `_retry_submission_publications()`를 다시 부른다.
  6. 마지막으로 `engine.status()`를 부른다.
- 단언:
  - 대기의 `(kind, next_owner)`가 `('submission_publication', 'engine')`이고, `detail.environment_id`가 활성 환경 ID다.
  - 복원만 한 뒤의 재시도는 `_receive_submission`을 부르지 않는다. 불렀다면 패치가 실패를 낸다.
  - 다시 기록한 뒤에는 대기가 사라지고, 실행 `outcome`이 `'output_accepted'`이며, 봉인 출력 바이트가 `raw`와 같다.
  - `status()`는 `do_math.formal.toolchain_identity_errors`와 `do_math.trust_inventory.observe_fingerprint`를 부르지 않는다. 둘 다 `AssertionError`로 패치되어 있다.
- 대역:
  - `patch.object(engine, '_apply', side_effect=gated_apply)`.
  - `patch.object(engine, '_receive_submission', side_effect=AssertionError(...))`(3단계 안).
  - `research_fixtures.fixture_setup_lean`. 이 컨텍스트는 `setup_lean.observe_identity`, `verify_environment`, `do_math.file_io.RACY_NS`를 패치한다.
  - `status()` 확인용 패치 둘.
- 비고:
  - 합성 도구 모음 파일을 실제로 덮어쓰고 되돌리며, `setup_lean.rerecord`가 도구 모음 기록 파일에 새 기준선을 더한다.
  - `state_fixtures.active_instance`는 합성 도구 모음을 `restore_template`의 `shared` 폴더에 둔다(docstring: "The synthetic toolchain goes to ``shared``"). `FakeEngine.environment`는 `trust_fixture(self.root/name, ...)`를 부르고 빌드에서 `self.root`는 `shared`다. 따라서 이 테스트가 쓰는 `lake.exe`와 기록 파일은 템플릿의 `shared` 아래에 있다. `research_fixtures` docstring은 `shared`를 "never copied or cleared and must only be read afterwards"라고 적는다.
  - 되돌림은 불완전하다. `lake.exe`의 바이트는 `try`/`finally`나 `addCleanup` 없이 정상 경로(행 965)에서만 되돌린다. 그래서 행 959와 965 사이에서 단언이나 호출이 실패하면 바꾼 바이트가 그대로 남는다. `rerecord`가 기록 파일에 더한 기준선과, `trust_inventory.writer_lock`이 기록 폴더에 만든 `.lock` 파일은 아예 되돌리지 않는다. 되돌린 `lake.exe`의 수정 시각도 원래와 다르다. 다만 `.exe`는 지문 대상 확장자(`trust_inventory.JUDGMENT_SUFFIXES`: `.olean`, `.dll`, `.so`, `.dylib`)가 아니다.
  - `shared`는 템플릿 키(`active_instance`, `config=ACTIVE_CONFIG`)마다 프로세스에 하나이고, `start_active_copy`를 쓰는 모든 시험이 같은 도구 모음과 기록 파일을 본다. 그래서 같은 프로세스에서 뒤에 도는 시험은 이 테스트가 남긴 기록(기준선 둘, 바뀐 `record_state`)을 본다. 이 테스트가 도중에 실패하면, 현재 식별을 확인하는 뒤 시험(`toolchain_identity_errors`를 거치는 게시 관문)이 "approved toolchain file changed" 오류를 받을 수 있다.
  - 모듈 머리에서 이미 가져온 `start_submission_history`와 `submit_history`를 함수 안에서 다시 import한다.

## 관계

- 같은 제품 기능을 다른 층에서 검사하는 모듈:
  - `test_submission_tools`는 같은 제출 도구를 작업자 쪽 명령, MCP, 실제 엔진 구동으로 검사한다. 이 모듈은 중앙 수신과 봉인 쪽을 본다.
  - `test_native_final_submission`은 `_collect_submitted_result`의 네이티브 최종 출력 경로를 따로 검사한다. `PartialCaptureGitTests.test_native_final_reaches_the_same_partial_candidate`는 그 경로가 부분 후보에서 조기 제출과 같은 결과에 이르는지만 본다.
  - `seal_submission`은 `test_impact_review`, `test_role_input`, `test_submission_checks`, `test_submission_tools`도 부른다. `test_controls`는 `do_math.engine.submission.seal_submission`을 패치할 뿐 부르지 않는다. `read_sealed_submission`을 직접 부르는 다른 모듈은 `test_governance_engine`이고, `test_impact_review`와 `test_review_engine`은 패치한다. `_receive_submission`은 `test_currentness`, `test_repetition`, `test_native_final_submission`도 부르고, `test_completion_settlement`와 `test_review_engine`은 autospec 대역으로 바꾼다. `_preview_submission`은 `test_controls`가 autospec 대역으로 바꿀 뿐, 실제로 부르는 모듈은 이 모듈뿐이다.
  - `fixed_research_reference_path`와 `_submission_check_summary`를 부르는 모듈은 이 모듈과 `test_native_final_submission`뿐이다. 앞의 것은 이 모듈에서만 부른다.
- 픽스처 의존:
  - 2단 시작 상태는 모두 `engine_fixtures.start_submission_history`에서 온다. 이 도우미를 쓰는 다른 모듈은 `test_controls`다. `start_native_final`은 그 위의 변형이며 `test_native_final_submission`이 쓴다.
  - 메모리 엔진 대역은 `engine_fixtures.routing_engine`, `context_engine`, `research_fixtures.bare_engine`이다.
  - 실제 봉인 바이트는 `research_fixtures.seal_response`와 `sealed_maintenance_submission`이 만든다.
  - 부분 포착 입력은 `record_fixtures.two_observation_output`과 `research_work_context`다.
- 이 모듈에만 있는 도우미: `WaitOwnershipTests.receive`와 `CentralSubmissionEvidence.fixture`. 모듈 함수는 없다.
- 겹치거나 보완하는 시험:
  - `test_central_seal_uses_actual_bytes_and_survives_original_draft_change`와 `test_submission_tools`의 `test_accepted_submission_is_unchanged_when_original_draft_changes_later`는 같은 성질("원본 초안이 바뀌어도 봉인은 그대로")을 다른 층에서 본다. 앞의 것은 `seal_submission`을 직접 부르고, 뒤의 것은 MCP 전송과 Git 게시를 거친다.
  - `test_submit_transport_contains_only_the_draft_locator`와 `test_submission_tools`의 `test_submit_draft_mcp_derives_internal_evidence_from_one_path`는 둘 다 payload가 초안 위치 하나뿐임을 본다. 앞의 것은 `worker_submit` 패치로, 뒤의 것은 실제 전송 inbox 파일로 확인한다.
  - `test_real_preview_entry_accepts_questions_without_publishing`(엔진 입구 직접 호출), `test_installed_preview_uses_receiver_domain_callback_without_publication`(설치된 명령과 자식 프로세스), `test_submission_tools`의 `test_preview_is_an_explicit_nonpublication_control_request`(전송 의미만)는 미리보기의 비게시 성질을 세 층에서 본다.
  - `test_empty_known_extension_is_normalized_at_capture_and_sealed_read`와 `test_submission_tools`의 `test_empty_known_extension_family_remains_a_semantic_noop`은 빈 `knowledge_changes`를 각각 중앙 봉인과 생산자 명령에서 본다.
