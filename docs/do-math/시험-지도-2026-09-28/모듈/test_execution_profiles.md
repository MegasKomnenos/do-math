# test_execution_profiles

| 항목 | 값 |
|---|---|
| 조각 | `foundation` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_execution_profiles.py` (903행) |
| 클래스 / 테스트 | 3 / 34 |
| 시험 대상 제품 코드 | `do_math/execution_profiles.py`의 `build_profiles`, `seal_profile`, `validate_profile`, `profile_ref`, `match_profile_ref`, `resolve_profile`, `select_profile`, `bind_execution`, `apply_editions`, `runtime_config`, `host_constraint`, `machine_invocation`, `runner_tools`, `prepare_prompt`, `boundary_prompt`, `prompt_seal`, `capability_evidence`, `structural_failure_evidence`, `execution_observation`, `_lean_contract`, `WINDOW_KEYS`, `HOST_ROLES`; `do_math/model_policy.py`의 `selection`; `do_math/session_slots.py`의 `SessionSlots`(`acquire`, `release`, `started`, `admission_check`, `provider_result_from_run`, `snapshot`); `do_math/model_runner.py`의 `ModelRunner.run`; `do_math/control_transport.py`의 `ControlTransport`와 MCP 서버; `do_math/codex_worker.py`·`claude_worker.py`·`cli_worker.py`의 요청 검사와 인자; `do_math/codex_adapter.py`의 `CodexExecAdapter.start`, `capability_identity`, `CLIExecution`; `do_math/claude_adapter.py`의 `ClaudePrintAdapter.start`, `collect`; `do_math/initialization.py`의 `capability_requirements`; `do_math/formal.py`의 `verify_lean`; `do_math/context_store.py`의 `prepare_role_input`; `do_math/observations.py`의 `tracker_config`, `observation_rule_contract`; `do_math/governance_engine.py`의 `_configure_candidate`; `do_math/state_contract.py`의 `default_state_contract`, `validate_record`; `do_math/file_io.py`의 `RACY_NS`, `sha256_file` |
| 사용하는 픽스처 모듈 | `provider_fixtures`의 `PROFILE_CONFIG`, `Adapter`, `runner_with`, `mock_adapter`, `FakeJob`, `claude_stream`, `CLAUDE_INIT`, `CLAUDE_RESULT`; `research_fixtures`의 `dispatched_launch`, `observation_rule`; `record_fixtures.surface_state`; `engine_fixtures.governance_host`(모듈 머리의 `PROFILE_CONFIG`, `dispatched_launch`를 뺀 나머지는 테스트 안에서 늦게 import) |
| 격리 표지 | 없음 |
| 시작 상태 | 대부분 1단(`build_profiles`로 만든 프로필 사전 위의 순수 함수와 `SessionSlots`). 러너 시험은 실제 `ModelRunner`에 수집기 대역을 끼운다. 제어 전송 시험은 실제 전송 파일과 실제 MCP 자식 프로세스를 쓴다. 마지막 시험은 `engine_fixtures.governance_host`의 저장소 없는 엔진이다 |

## 목적

모듈 docstring은 "Execution profiles: pinning and selection, admission atomicity, resource waits and observed provider evidence."이다. `execution_profiles.py`의 docstring은 "Immutable execution contracts; configuration is only a profile authoring input."이다. 실행 프로필은 역할마다 모델, 등급, 관찰 방식, 호출 창, 입력 한도, 경계 규칙, 도구, 용량 참조를 봉인한 불변 판본이다. 판본의 ID와 해시는 내용 해시(`EP-` + SHA-256)다. 실행은 판본 하나에 고정되고, 설정이 바뀌면 새 판본이 추가될 뿐 옛 판본은 등록된 채 남는다. 이 모듈이 보는 네 무리는 다음과 같다.

- 고정과 선택. 선택 비용은 허용 판본 수에 비례한다. 채택 판본만 쓰며 Lean을 읽지 않는다. 과제 허용 목록과 역할 하한을 지킨다. 명시한 옛 판본은 그 모델을 쓴다.
- 입장의 원자성. 모두 잡거나 하나도 잡지 않는다. 등록된 실행만 한 번 입장한다. 운영 역할은 슬롯을 쓰지 않는다. 판본이 바뀌어도 이력과 공급자 관문이 보존된다.
- 자원 대기. 용량 0과 공급자 점검을 구별하고 읽기 전용으로 판정한다. 설정 변경은 바뀐 자원 대기만 깨운다.
- 관찰된 공급자 증거. 능력 신원과 해시가 있다. 표면 증거를 Job 증거로 올리지 않는다. 구조적 시작 실패는 신원에 묶인 부정 증거를 낸다. 원생 보고는 범위를 넓히지 않고 저장 투영에 들어간다.

그 밖에 러너가 봉인된 입력과 요청을 고정하고 제어 전송 결합을 두 작업자에게 전달하는지도 본다.

## 모듈 수준 요소

- 행 10: `sys.path.insert(0, str(Path(__file__).resolve().parents[1]))`로 `scripts/` 폴더를 경로 앞에 넣는 공통 머리다.
- 행 902–903: 직접 실행하면 `unittest.main()`을 부른다.

모듈 머리에서 import하는 이름은 `exact_content_hash`, `dispatched_launch`, `execution_profiles`, `model_policy`, `PROFILE_CONFIG`, `DEFAULT_CONFIG`, `SessionSlots`다. `PROFILE_CONFIG`는 `build_profiles`에 필요한 키를 모두 갖춘 설정이다. 기본 모델 셋, 모델마다 작업 슬롯 3, `max_input_bytes=500000`, `call_timeout_seconds=600`, `scholarly_enabled=True`가 들어 있다.

공통 사실이 하나 있다. `SessionSlots.acquire`와 `dispatched_launch`가 만드는 발급 티켓은 `launch.ticket`에서 `windows_job.owner_identity()`로 현재 프로세스의 Windows 신원을 읽는다. 러너의 `validate_start`도 그 신원을 대조한다. 따라서 AI 프로필로 입장하거나 러너를 고정 프로필로 부르는 시험은 모두 Windows 호스트를 전제한다. 이 모듈에는 `skipUnless`가 없다.

## ProfileTests (행 19–590)

`unittest.TestCase`를 그대로 상속한다. 표지, 클래스 속성, 훅, 도우미가 없다.

### `test_selection_cost_depends_on_allowed_profiles_not_retained_editions` (행 21–50)
- 성질: 역할 프로필 선택의 비용은 허용된(채택된) 판본 수에 비례하고, 등록부에 남은 옛 판본 수와 무관하다. 선택은 등록부를 바꾸지 않는다. 허용 목록 밖의 판본, 낡은 참조, 빈 허용 목록은 거부된다.
- 준비: `max_input_bytes`만 500000+0…11로 바꾼 12개 설정으로 `build_profiles`를 부르고, 모든 판본을 한 등록부에 모은다. `lean_command=["fixture-no-lean"]`로 Lean 탐색을 막는다. 마지막 설정의 `role_profile_refs["maintenance"]`가 허용 목록이다.
- 실행: `match_profile_ref`를 `wraps`로 감싸 호출 수를 세면서 `model_policy.selection(config, {"role": "maintenance"}, {}, {}, instance=...)`을 부른다. 이어서 `select_profile`을 네 번 부른다. 허용 목록에 첫 참조를 한 번 더 넣은 경우, 빈 허용 목록, 개정 번호를 1 올린 낡은 참조, 그리고 허용 목록 밖의 같은 등급 옛 판본을 `profile_ref`로 명시한 경우다.
- 단언:
  - 선택한 참조가 허용 목록에 있다. `match_profile_ref` 호출 수가 `2 * len(allowed)` 이하다. 등록부가 사본과 같다.
  - 중복 허용 목록에서도 같은 판본이 골라진다.
  - 빈 목록은 `"permitted role/model edition"`, 낡은 참조는 `"absent or stale"`, 목록 밖 명시 판본은 `"permitted role/model edition"`으로 `ValueError`가 난다.
- 대역: `match_profile_ref`의 `wraps` 패치(호출 수 계측).
- 비고: 제품 `select_profile`은 허용 참조를 `id`로 중복 제거하고, 명시 참조가 있으면 그것만 후보로 삼되 허용 목록에 있어야 받아들인다(`execution_profiles.py` 297–311행).

### `test_ai_selection_uses_adopted_editions_without_building_or_reading_lean` (행 52–61)
- 성질: AI 역할의 선택은 채택된 판본 가운데서 고르며, 판본을 새로 봉인하거나 Lean 계약을 읽지 않는다.
- 준비: `lean_command=["fixture-no-lean"]`인 `PROFILE_CONFIG`로 만든 인스턴스.
- 실행: `_lean_contract`를 `AssertionError("AI selection read Lean")`로 패치하고 `seal_profile`을 `wraps`로 감싼 채 `selection(config, {"role": "maintenance"}, ...)`을 부른다.
- 단언: 선택한 프로필의 역할이 `maintenance`이고, 참조가 채택 목록에 있으며, `seal_profile` 호출 수가 0이다.
- 대역: `_lean_contract`와 `seal_profile` 패치.

### `test_profile_authoring_rejects_missing_unknown_and_invalid_host_demands` (행 63–83)
- 성질: 호스트 자원을 채택한 설정은 캡이 있는 모든 역할에 정확한 요구량을 요구한다. 빠진 역할, 모르는 역할, 잘못된 양은 프로필 작성 단계에서 거부된다.
- 준비: `host_constraint(host_id="fixture-host", ...)`로 만든 제약(한도 jobs 3, 4096바이트, CPU 10000, 예비분 1/1024/1000)과, `HOST_ROLES` 모든 역할에 1/1024/1000을 요구하는 표. 정상 설정의 `build_profiles`가 `host_capacity_ref`로 제약 ID를 돌려준다.
- 실행: `subTest(defect=...)` 세 경우로 `build_profiles(bad)`를 부른다. `research_work` 요구를 지운 경우, 모르는 역할 `invented`를 더한 경우, `research_work`의 메모리를 0으로 둔 경우다.
- 단언: 정상 설정의 `host_capacity_ref`가 제약 ID다. 세 경우 모두 `ValueError`다(유형만 본다).
- 대역: 없음.
- 비고: 제품의 거부 문구는 차례로 `"every capped role needs an explicit host demand in an adopted shared scope"`, `"host demands must name capped roles only"`, 그리고 요구량은 양수여야 한다는 `_host_amounts`의 문구다. 시험은 문구를 고정하지 않는다.

### `test_normal_final_delivery_rendering_preserves_the_sealed_profile` (행 85–100)
- 성질: 역할 프롬프트에 경계 규칙을 붙여 전달해도 봉인된 프로필은 바뀌지 않는다. 전달문에는 정상 JSON 최종 응답과 선택적 조기 제출의 안내, 그리고 모든 경계 규칙이 들어간다. 경계 규칙을 고친 프로필은 검증을 통과하지 못한다.
- 준비: `PROFILE_CONFIG`의 `research_work` 프로필과 그 사본. `contracts.render_prompt('research_work', {'action': {'role': 'research_work'}}, documents=[])`.
- 실행: `prepare_prompt(role_prompt, profile)`. 이어서 첫 규칙을 `'Use unassigned inputs.'`로 바꾼 사본에 `validate_profile`을 부른다.
- 단언: 전달문에 `'normal JSON final'`과 `'optional early submission'`이 있다. 프로필과 그 참조가 사본과 같다. 원래 경계의 모든 규칙이 전달문에 있다. 고친 사본은 `ValueError`다.
- 대역: 없음.
- 비고: 고친 사본의 거부는 경계 규칙 검사(`"this implementation supports only the declared instruction boundary"`)보다 앞선 내용 해시 검사(`"execution profile content differs from its immutable identity"`)에서 난다. 규칙을 바꾸면 해시가 달라지기 때문이다. 시험은 유형만 보므로 어느 검사가 막았는지 고정하지 않는다.

### `test_execution_control_is_registered_and_round_trips_in_child` (행 102–216)
- 성질: 러너는 발급된 제어 결합을 작업자 요청에 싣는다. 두 작업자는 그 결합으로 제어 MCP 서버를 등록한다. 실제 MCP 자식은 결합된 실행으로만 제출을 전달하고, 제출·영수증·자기 점검 요청·응답·닫힘을 왕복한다. 다른 실행을 가리키는 결합은 작업자와 러너 모두에서 거부된다.
- 준비:
  - scholarly 서버(`sys.executable`과 이 시험 파일)를 설정한 `PROFILE_CONFIG`의 `research_work` 프로필.
  - 임시 폴더의 `ControlTransport`. `issue("EX-bound", "GR-bound", self_check=True)`로 결합을 받는다. 주석은 연구 작업 실행이라고 밝힌다.
  - codex 칸의 `Adapter`와 `runner_with`.
- 실행: 결합을 준 `runner.run`, 두 작업자의 `load_request`·`build_argv`, 실제 MCP 자식과의 JSON-RPC 교환(`initialize`, `tools/list`, `tools/call`)과 시험 프로세스 쪽 `transport.pump`·`request_self_check`·`close`, 그리고 어긋난 결합으로 `validate_execution_binding`과 `runner.run`을 부른다.
- 단언: 단계별로 확인하는 결과는 다음과 같다.
  1. 결합을 준 `runner.run(... timeout_seconds=600, execution_id="EX-bound", profile=profile, launch_ticket=dispatched_launch(...), control_binding=binding)`. 대역이 받은 요청의 `control_binding`이 결합과 같다.
  2. 요청을 `codex_worker.load_request`로 읽어 `build_argv`로 인자를 만든다. 인자에 `mcp_servers.execution_control.command=`와 `mcp_servers.execution_control.args=`(각각 `mcp_server_config(binding)`의 JSON)가 있다.
  3. Codex 전용 필드를 빼고 `claude_path="claude"`를 넣은 Claude 요청을 파일로 써서 `claude_worker.load_request`와 `build_argv`에 넣는다. `--mcp-config`의 `execution_control`이 같은 설정이고, 서버 집합이 `{"execution_control", "scholarly"}`다.
  4. MCP 서버 설정으로 실제 자식을 띄운다(`encoding="utf-8"`). 지역 함수 `exchange`는 응답 ID를 확인하고, `rpc`는 오류가 없음을 확인하며, `call`은 도구 결과의 텍스트 JSON을 읽는다.
     - `initialize`의 `serverInfo.version`이 `"5"`다.
     - 도구 집합이 `{"control_submit", "control_receipt", "control_self_check", "submit_draft"}`다. `control_submit`의 `kind` 열거가 `REQUEST_KINDS`와 같다. `control_self_check`의 `response` 입력은 `{"type": "object"}`이고, 설명에 `SELF_CHECK_RESPONSE_SCHEMA`의 정렬된 JSON이 들어 있다.
     - `control_submit`(`REQ-one`, 인자에 가짜 `execution_id`를 넣음)은 `"submitted"`이고, 아직 영수증이 없다(`None`).
     - 펌프 콜백은 요청의 `(execution_id, grant_id)`가 `("EX-bound", "GR-bound")`임을 단언한 뒤 수락한다. 영수증은 `accepted`, `EX-bound`, 스냅숏 `"test-published-head"`다.
     - 새로 발급한 다른 전송에서 `REQ-one`의 영수증은 `None`이다. 한 번 더 펌프해도 게시는 1회뿐이다.
     - `request_self_check(... "SC-one" ...)` 뒤 `control_self_check` 폴링의 `execution_id`가 `"EX-bound"`다.
     - 스키마에 맞지 않는 응답(`{"answered": True}`)은 JSON-RPC 오류 코드 `-32602`를 받는다. 영수증도 수신함 파일(`self-check-SC-one.json`)도 생기지 않는다.
     - 올바른 응답을 보내고 펌프하면 `self-check-SC-one`의 영수증이 `"accepted"`다.
     - 닫은 뒤 `control_submit`(`REQ-after`)은 `"closed"`다.
     - `finally`에서 표준 입력을 닫고 기다린 뒤, 자식의 종료 코드가 0이다(실패 메시지는 표준 오류).
  5. 두 작업자 요청의 결합을 `execution_id="EX-other"`로 바꾸면 `cli_worker.validate_execution_binding`이 `ValueError`를 낸다.
  6. `execution_id="EX-other"`와 원래 결합으로 러너를 부르면 `ValueError`가 나고, 증거 폴더 `wrong`이 생기지 않는다.
- 대역: `Adapter`/`runner_with`, 펌프 콜백. MCP 서버는 실제 자식 프로세스다.
- 비고: 가짜 `execution_id` 인자는 도구 입력에서 무시되고 결합이 실행을 정한다. 펌프 콜백의 단언이 이것을 확인한다. 주석(157–159행)은 자기 점검 응답 스키마를 입력 노드가 아니라 설명에 싣는 이유를 밝힌다. 보존된 공급자 실행이 받아들인 평범한 객체 모양을 입력 노드로 유지하기 위해서다. 6의 거부는 러너가 증거 폴더를 만들기 전에 `validate_execution_binding`을 부르기 때문이다(`model_runner.py` 81–84행).

### `test_both_adapters_snapshot_the_exact_control_binding` (행 218–249)
- 성질: 두 어댑터는 시작할 때 요청을 비공개 스냅숏으로 복사해 작업자에게 넘긴다. 스냅숏에는 제어 결합과 실행 ID가 그대로 들어가고, 원래 요청 파일을 나중에 바꿔도 스냅숏은 바뀌지 않는다.
- 준비: 작업 공간 `workspace`를 가진 결합(`EX-snapshot`), 프롬프트와 스키마 파일, 두 공급자에 공통인 요청 필드다. 공통 필드에는 실행 ID, 프로필 참조, 결합이 들어 있다. Codex는 `codex_path`, `sandbox`, `approval_policy`, `final_path`를 더하고, Claude는 `claude_path`를 더한다.
- 실행: 공급자마다 요청 파일을 쓰고, `do_math.codex_adapter.WindowsJob`을 `Mock`으로 패치한 채 `adapter.start(request, cwd=root, env={})`를 부른다. 작업자 인자의 마지막 원소가 가리키는 스냅숏 파일을 읽는다. 원래 요청 파일을 `"{}"`로 덮어쓴 뒤 스냅숏을 다시 읽는다.
- 단언: 스냅숏의 `control_binding`이 결합과 같고 `execution_id`가 결합의 실행 ID다. 원래 파일을 덮어쓴 뒤에도 스냅숏의 결합이 같다.
- 대역: `WindowsJob` 패치(프로세스를 만들지 않는다).
- 비고: 주석(243행)은 작업자가 원래 파일이 아니라 인자에 적힌 스냅숏 요청을 실행한다고 밝힌다. `ClaudePrintAdapter`도 `start`를 기반 `LocalCLIAdapter`에서 물려받으므로 같은 패치가 두 어댑터에 적용된다.

### `test_admission_probe_preserves_history_and_provider_gate_across_capacity_editions` (행 251–290)
- 성질: 용량 설정이 바뀌어 새 판본이 채택되어도, 이미 정산된 옛 예약 이력은 그대로 남는다. 새 입장은 새 판본의 제약을 쓴다. 읽기 전용 입장 판정은 런타임을 바꾸지 않으며, 공급자 관문과 용량 한도를 따로 판정한다.
- 준비:
  - `PROFILE_CONFIG`의 인스턴스와 `research_work` 프로필 위에서 `EX-history`를 입장시키고 해제한다. 둘 다 참이다. 그 예약 행의 사본을 떠 둔다.
  - 그 모델의 작업 슬롯을 1로 바꾼 설정으로 `apply_editions`한다.
  - 공급자 관문 `PW-<provider>`를 `waiting`, `retry_at=100`, 시도 1로 둔다.
- 실행: 관찰자 `SessionSlots`의 `admission_check(profile, current_time=100)`를 세 번, `slots.acquire("EX-held", ..., current_time=100)`을 한 번 부른다. 그 사이에 공급자 관문을 지운다.
- 단언: 단계별로 확인하는 결과는 다음과 같다.
  1. `observer=True`인 `SessionSlots`의 `admission_check(profile, current_time=100)`가 허용이고, 런타임이 사본과 같다.
  2. `EX-held`를 시각 100에 입장시키면 참이다. 이력 예약이 사본과 같다. 새 예약의 `constraint_id`는 이력의 것과 다르다.
  3. 다시 읽기 전용 판정을 하면 대기 종류가 `"provider_limit"`이고, 런타임이 바뀌지 않는다. 관문이 이제 `EX-held`의 점검(`checking`)이기 때문이다.
  4. 관문을 지우고 판정하면 거부이고 대기 종류가 `"capacity"`다. 새 한도 1을 `EX-held`가 차지하고 있다. 런타임은 바뀌지 않는다.
- 대역: 없음.
- 비고: 첫 해제(`release("EX-history")`)는 `named_job_empty`를 패치하지 않으므로, 실제 Windows API로 발급 이름의 Job이 없음을 확인한다. 제품 `_admission`은 옛 판본에 잡힌 예약 행의 제약 ID를 같은 모델의 현재 제약으로 다시 매겨 센다(`session_slots.py`의 "A new capacity edition must still count executions reserved under older editions"). 이름의 "preserves history"는 정산된 이력 행이 바뀌지 않았다는 단언으로 확인된다.

### `test_work_has_no_deadline_and_operations_keep_their_call_window` (행 292–311)
- 성질: 작업 역할 러너는 마감 없이 돌고, 운영 역할 러너는 고정 프로필의 호출 창을 넘는 마감이나 마감 없음을 받지 않는다. 모든 프로필의 창은 정확히 `WINDOW_KEYS`를 갖는다.
- 준비: `PROFILE_CONFIG`의 프로필들. `research_work`는 마감 `None`, `operational_review`는 600으로 부른다.
- 실행: 역할마다 새 `Adapter`로 고정 프로필을 준 `runner.run`을 부른다. 운영 역할은 이어서 `None`과 `call_timeout_seconds + 1`(601)로 다시 부른다.
- 단언: 창의 키 집합이 `WINDOW_KEYS`다. 대역이 받은 요청의 `max_runtime_seconds`가 준 값과 같다. 운영 역할의 두 잘못된 값은 `ValueError`(`"deadline"`)다. 제품 문구는 `"runner deadline exceeds the pinned profile"`이다.
- 대역: `Adapter`, `runner_with`.
- 비고: 이 시험은 러너 층에서 작업 역할 무마감 규칙을 본다(`model_runner.py` 67–69행). 마감 없는 창의 공개(`execution_window.publish`에 마감 `None`)는 `test_execution_window`가 순수 함수로 본다. 엔진이 작업 역할의 `call_deadline`을 `None`으로 두는 분기(`engine.py` 3250–3251행) 자체는 이 시험도 `test_execution_window`도 단언하지 않는다.

### `test_selection_is_pinned_and_contract_allowlist_is_enforced` (행 313–337)
- 성질: 선택된 판본은 그 시점 설정을 고정한다. 허용 목록이 비면 거부되고, 허용 목록에 있으면 그 판본이 선택된다. 저장되지 않은 편집은 검증에서 걸린다. 새 판본이 채택되면 기본 선택은 새 판본을 고른다.
- 준비: `PROFILE_CONFIG` 판본과 낮은 평가의 `research_work` 요청.
- 실행: `selection`, `resolve_profile`, `runtime_config`를 부른다. 이어서 빈 허용 목록과 한 참조의 허용 목록으로 `select_profile`을 부른다. 모델을 바꾼 사본으로 `validate_profile`을 부른다. 끝으로 `max_input_bytes=400000`으로 새 판본을 만들어 옛 판본과 합친 등록부에서 `selection`을 부른다.
- 단언: 고정 설정의 `max_input_bytes`가 500000이다. 빈 허용 목록은 `ValueError`, 한 참조의 목록은 같은 `id`다. 모델을 바꾼 사본은 `ValueError`다. 새 선택의 `id`는 새 판본의 등록부에 있다.
- 대역: 없음.
- 비고: 320–321행은 `config["max_input_bytes"] = 1`인 사본 `config`를 만들지만, 이 변수는 이후 어디서도 쓰이지 않는다. 고정 설정이 설정 변경과 무관함을 보이려는 의도로 읽히지만, 실제 단언은 `runtime_config(profile)`이 판본의 값을 돌려준다는 것뿐이다. 주석(329행)은 참조 조회가 참조만 비교하고, 저장되지 않은 편집은 `validate_profile`이 잡는다고 설명한다.

### `test_modes_machine_fields_and_profile_rebinding` (행 339–352)
- 성질: 관찰 방식은 역할의 책임을 따른다. 연구 작업은 설정값, 다른 작업 역할은 주기, 운영 역할은 마감 전용이다. 기계 프로필에는 AI 필드가 없다. 실행은 판본 하나에 묶인 뒤 다른 판본으로 다시 묶일 수 없다.
- 준비: `PROFILE_CONFIG` 프로필들.
- 실행: 역할별 관찰 방식을 모은다. `formal_check` 프로필로 실행 `EX-one`을 `bind_execution`한 뒤, `trust_check` 프로필로 다시 묶는다.
- 단언: `research_work`는 `"event_driven"`, `identity_review`는 `"periodic"`, `operational_review`는 `"deadline_only"`다. 기계 프로필에 `ai` 키가 없다. 첫 결합 뒤 `execution_profile_ref`가 있다. 재결합은 `ValueError`다.
- 대역: 없음.
- 비고: 재결합의 거부는 "an execution cannot change its profile"이 아니라, 그보다 앞선 역할 검사 `"execution role differs from profile"`에서 난다. 실행의 역할은 `formal_check`이고 둘째 프로필의 역할은 `trust_check`이기 때문이다. 같은 역할의 다른 판본으로 재결합하는 경로는 이 시험이 보지 않는다.

### `test_research_profile_binds_all_implemented_signal_kinds_not_counter_names` (행 354–362)
- 성질: 연구 작업 프로필이 관찰기에 넘기는 규칙 결합은 구현된 신호 종류 전체의 계약이다. 초기 자기 점검 규칙이 세는 카운터 이름이 아니다.
- 준비: 도구 검토 창과 자기 점검 응답 창을 60초로 둔 `research_work` 프로필. `research_fixtures.observation_rule(threshold=1, id="SC-attempts", required_evidence=["checkpoint.json"])`(카운터 `attempts`)을 쓴다.
- 실행: `tracker_config(profile, initial_self_check_rules=[rule])`.
- 단언: 결과의 `observation_rule_bindings`가 `observation_rule_contract()`와 같다.
- 대역: 없음.

### `test_git_admission_all_or_nothing_and_unknown_release` (행 364–405)
- 성질: 입장은 모두 잡거나 아무것도 잡지 않는다. 예약 행은 저장 계약을 통과한다. 시작 기록은 멱등이다. 종료를 알 수 없으면 해제하지 않고 슬롯을 계속 센다. 확인되면 해제하며, 해제도 멱등이다. 운영 역할은 슬롯이 모두 차도 입장한다.
- 준비: `PROFILE_CONFIG` 인스턴스와 빈 런타임. `low` 등급 모델의 `research_work` 프로필.
- 실행: `slots.acquire`를 다섯 번(`EX-0`…`EX-2`, `EX-over`, 뒤에 `EX-3`과 `EX-op`), `slots.started`를 두 번, `slots.release("EX-0")`을 세 번 부르고, 사이마다 `slots.snapshot()`을 읽는다.
- 단언: 단계별로 확인하는 결과는 다음과 같다.
  1. `EX-0`…`EX-2` 입장이 모두 참이다(슬롯 3). 모든 예약 행이 `default_state_contract().family("runtime", "reservations").checker` 검증을 통과한다.
  2. `EX-over`는 거짓이고 런타임이 바뀌지 않는다.
  3. `started("EX-0", {"job_name": 티켓 이름, "pid": 1}, at=...)`은 런타임의 같은 객체를 돌려준다. 그 객체는 `running`, 시작 시각, 프로세스 신원을 갖는다. 같은 신원으로 다시 부르면 같은 객체를 돌려주고 런타임이 바뀌지 않는다.
  4. `named_job_empty=None`이면 `release("EX-0")`이 거짓이고, `snapshot()`의 사용 수가 3이다.
  5. `True`이면 해제가 두 번 모두 참이고, 사용 수가 2다.
  6. `EX-3` 입장이 참이다. 같은 모델의 `maintenance` 프로필은 `capacity_refs == []`이고, 그 입장 `EX-op`도 참이다. `EX-op`의 `reservation_ids`가 `[]`이고 사용 수가 3이다.
- 대역: `named_job_empty` 패치.
- 비고: 주석(396행)은 운영 AI 역할이 모든 작업 슬롯이 차도 모델 슬롯을 예약하지 않는다고 밝힌다. 이름의 "Git admission"은 저장 계약 검사를 가리키는 것으로 읽힌다. 이 시험은 실제 Git 저장소를 쓰지 않는다.

### `test_admission_accepts_registered_queued_execution_exactly_once` (행 407–421)
- 성질: 이미 등록된 대기 실행은 그 객체 그대로 한 번 입장한다. 같은 실행을 두 번 입장시키면 거부되고 런타임이 바뀌지 않는다.
- 준비: 런타임에 등록된 `EX-registered`(`queued`, 프로필 참조, 활동 `AY-one`).
- 실행: `acquire`를 두 번 부른다.
- 단언: 첫 호출이 참이다. 런타임의 실행이 같은 객체이고 `owner_activity_id`가 유지된다. 둘째 호출은 `ValueError`이고 런타임이 사본과 같다.
- 대역: 없음.
- 비고: 제품 문구는 `"execution IDs are single-use; only the registered unreserved execution can be admitted"`다. 시험은 유형만 본다.

### `test_runner_pins_request_and_exposes_reported_evidence` (행 423–440)
- 성질: 고정 프로필을 받은 러너는 작업자 요청에 실행 ID와 프로필 참조를 싣는다. 공급자가 보고한 사실은 알 수 없는 것을 알 수 없음으로 둔 채 결과에 드러낸다.
- 준비: `jsonl`에 `usage_total={"output_tokens": 3}`과 `stop_reason="end_turn"`을 담은 `Adapter`.
- 실행: `runner.run(... execution_id="EX-bound", profile=profile, ...)`.
- 단언: 요청의 `execution_id`가 `"EX-bound"`이고 `profile_ref`가 프로필 참조다. `provider_observation`의 `stop_reason`이 `"end_turn"`, `remote_termination`이 `"unknown"`, `usage_scope`가 `"reported_execution_counters_not_invoice"`다. 결과의 `execution_id`가 `"EX-bound"`다.
- 대역: `Adapter`, `runner_with`.

### `test_issued_workspace_binding_reaches_both_runners_and_worker_contracts` (행 442–479)
- 성질: 작업 공간이 있는 결합은 두 공급자의 러너와 작업자 계약에 그대로 전달되고, MCP 설정에 작업 공간이 실린다. 결합이 조금이라도 어긋나면 작업자 요청 검사와 러너 모두 거부하며, 러너는 증거 폴더를 만들지 않는다.
- 준비: `subTest(provider=model)` 두 경우(`codex`/`gpt-6-astra`, `claude`/`claude-opus-5`). 세 등급을 그 모델로 둔 설정의 `research_work` 프로필. 작업 공간 결합 `EX-bound`와 공급자별 `Adapter`.
- 실행: 결합을 준 `runner.run`. 이어서 `worker.load_request`, `mcp_server_config`, `worker.build_argv`를 부른다. 잘못된 결합 일곱 가지를 `subTest(invalid=index)`로 돈다. 요청 파일에 넣어 `load_request`를 부르고, 러너에 넣어 부른다.
  1. 모르는 키 `unexpected`.
  2. `execution_id="EX-other"`.
  3. 상대 경로 `endpoint`.
  4. 상대 경로 `workspace`.
  5. 빈 `workspace`.
  6. `workspace=None`.
  7. 다른 폴더 `workspace`.
- 단언: 요청의 `control_binding`이 결합과 같다. MCP 인자에 `--workspace=<작업 공간 절대 경로>`가 있다. `build_argv`가 참인 목록이다. 일곱 경우 모두 `load_request`와 `runner.run`이 `ValueError`이고, `invalid-<번호>` 폴더가 생기지 않는다.
- 대역: `Adapter`, `runner_with`.
- 비고: 일곱째 경우의 거부는 러너가 넘기는 `cwd`(작업 공간)와 결합의 작업 공간이 달라서 난다. 제품 문구는 `"control binding workspace differs from execution cwd"`다. `load_request` 쪽은 요청의 `cwd`로 같은 검사를 한다.

### `test_workers_validate_execution_binding` (행 481–502)
- 성질: 작업자 요청은 실행 ID와 프로필 참조가 정확하면 받아들여지고, 둘 가운데 하나가 없거나 잘못되면 거부된다.
- 준비: 실행 ID `EX-bound`와 프로필 참조를 가진 Codex 요청 파일.
- 실행: `codex_worker.load_request(path)`. 이어서 `subTest(invalid=...)` 두 경우. `execution_id`를 지운 경우(값이 `None`인 키를 뺀다)와 프로필 참조의 `id`를 공백으로 둔 경우다.
- 단언: 정상 요청이 받아들여지고 `execution_id`가 `"EX-bound"`다. 거부되면 `"worker rejects execution/profile binding: "`으로 실패시킨다. 두 잘못된 경우는 `ValueError`다.
- 대역: 없음.

### `test_provider_wait_is_canonical_and_serializes_retry_probe` (행 504–528)
- 성질: 공급자 한도 실패는 관문을 개별 가족 레코드로 기록하고, 런타임은 정규 JSON으로 부호화된다. 재시도 시각 전에는 입장이 막힌다. 시각이 되면 한 실행만 점검으로 입장하고, 동시에 다른 점검은 막힌다. 점검이 응답을 관찰하면 관문이 열린다.
- 준비: `PROFILE_CONFIG` 인스턴스, `research_work` 프로필. 지역 함수 `admit(eid, t)`는 시각 `t`에 입장시킨다.
- 실행: 지역 함수 `admit`으로 시각 10, 19, 21, 21, 22에 입장을 시도하고, 시각 10.5와 22에 `slots.provider_result_from_run`으로 실패와 완료를 적용한다. `canonical_json(runtime)`을 한 번 부른다.
- 단언: 단계별로 확인하는 결과는 다음과 같다.
  1. `EX-failure`가 시각 10에 입장한다(참).
  2. 공급자 한도 실패(`retry_at="1970-01-01T00:00:20+00:00"`)를 시각 10.5에 `provider_result_from_run`으로 적용한다. 모든 관문 행의 키가 그 행의 `id`와 같다(실패 메시지 `"provider gates must persist as individual family records"`). `canonical_json(runtime)`이 예외 없이 끝난다.
  3. 시각 19의 `EX-too-early`는 거짓이다.
  4. 시각 21의 `EX-probe`는 참이다.
  5. 같은 시각의 `EX-concurrent-probe`는 거짓이다.
  6. `EX-probe`의 완료 결과를 시각 22에 적용한다. 그 뒤 `EX-after`가 참이다.
- 대역: 없음.
- 비고: 재시도 시각은 공급자가 알려 준 20초다. 현재 시각 10.5보다 늦으므로 그대로 쓴다(`retry_time`). 관문이 열린 뒤 첫 입장은 관문을 `checking`으로 바꾸고 점검 소유자가 된다(`session_slots.py` 210–211행). 그래서 5가 막힌다. 슬롯은 모델당 3이고, 이 시험은 해제 없이 셋(`EX-failure`, `EX-probe`, `EX-after`)을 입장시키므로 마지막 입장에서 슬롯이 꼭 찬다.

### `test_capability_identity_has_host_worker_and_cli_hashes` (행 530–550)
- 성질: 능력 신원은 CLI 파일 해시, 작업자와 수집기가 쓰는 모듈 해시, 호스트 정보를 담는다. CLI 바이트가 바뀌면 CLI 해시만 바뀐다. 두 공급자의 모듈 집합은 실제로 쓰는 모듈 전부다.
- 준비: 임시 CLI 파일 `cli.exe`(`b"first"`)를 가리키는 `CodexExecAdapter`.
- 실행: `capability_identity()`를 두 번 부른다. 그 사이에 파일을 `b"second"`로 바꾼다. 이어서 이름만 준 두 어댑터의 모듈 해시 키를 모은다.
- 단언: 첫 신원의 `module_sha256`에 `windows_job`이 있다. 두 신원의 `cli_sha256`이 다르고 `module_sha256`이 같다. `host`가 있다. Codex 모듈 집합은 `{"cli_worker", "codex_worker", "control_transport", "file_io", "windows_job", "scholarly", "codex_adapter"}`이다. Claude는 거기에 `claude_worker`, `claude_adapter`, `claude_stream`을 더한 집합이다.
- 대역: 없음.
- 비고: 주석(543행)은 작업자가 Job 안에서 돌리거나 수집기가 쓰는 모든 모듈이 구현을 식별한다고 밝힌다. 이름의 "worker hash"는 별도 필드가 아니라 `module_sha256`의 `codex_worker`/`claude_worker` 항목이다.

### `test_unchanged_cli_and_sources_are_not_rehashed_for_each_identity` (행 552–563)
- 성질: 바뀌지 않은 CLI와 소스 파일은 신원을 구할 때마다 다시 해시하지 않는다.
- 준비: 임시 CLI 파일의 `CodexExecAdapter`. `file_io.RACY_NS`를 0으로 패치한다. 주석은 새 파일의 생성 시각을 늙게 할 수 없으므로 과거 지문을 모두 안정된 것으로 본다고 설명한다.
- 실행: 첫 `capability_identity()` 뒤, `file_io.sha256_file`을 `AssertionError("unchanged file was rehashed")`로 패치하고 다시 부른다.
- 단언: 둘째 신원이 첫 신원과 같다. 해시 함수가 불렸다면 실패했을 것이다.
- 대역: `RACY_NS`와 `sha256_file` 패치.
- 비고: 제품 `cached_sha256`은 파일 지문이 같고 안정되었으면 저장한 해시를 돌려준다. `capability_identity`의 주석은 이음새-정본 §2를 가리킨다.

### `test_capability_evidence_does_not_promote_surface_to_job_proof` (행 565–575)
- 성질: 명령 표면(도움말·버전)에서 얻은 능력 증거는 표면 능력만 지원으로 인정한다. 지역 Job 정지처럼 표면이 입증할 수 없는 능력은 설명이 지원한다고 말해도 알 수 없음으로 둔다.
- 준비: AI 프로필 하나. `scope="cli_command_surface_only"`, `verified=True`인 설명이다. `supported`는 `jsonl`, `model`, `local_job_stop`이 모두 참이고, `unknown`은 `["remote_termination"]`이다.
- 실행: `capability_evidence(profile, description, observed_at="2026-09-20T00:00:00Z")`.
- 단언: 증거의 `execution_profile_ref`가 프로필 참조다. `jsonl`은 `"supported"`, `local_job_stop`과 `remote_termination`은 `"unknown"`이다.
- 대역: 없음.
- 비고: 제품은 표면 범위이면 표면 능력 다섯(`jsonl`, `model`, `structured_output`, `effort_via_config`, `sandbox`) 밖의 이름을 모두 `unknown`으로 낮춘다(`execution_profiles.py` 394–420행). docstring은 "Help text is not a process-lifetime, isolation, or provider-behavior test."다.

### `test_unsupported_job_is_a_profile_failure_not_an_ordinary_retry` (행 577–590)
- 성질: 호스트가 원자적 지역 Job을 지원하지 않아 시작이 실패하면, 러너는 예외를 던지지 않고 프로필 관문이 다룰 구조적 실패로 분류한다.
- 준비: `mock_adapter()`의 `start`가 `WindowsJobUnsupportedError("atomic admission unsupported")`를 던진다.
- 실행: 프로필 없이 `runner.run(prompt="test", ..., model="test", effort="low", timeout_seconds=1)`.
- 단언: 예외가 나면 `"structural unsupported capability was not classified for the profile gate"`로 실패시킨다. 결과의 `error_kind`가 `"profile_unsupported"`이고, `capability_failure.capability`가 `"atomic_local_job"`이다.
- 대역: `mock_adapter`(실제 작업자 옵션을 가진 `Mock`).
- 비고: 프로필이 없으므로 신원에 묶인 능력 증거는 만들지 않는다. 그 경로는 `MachineAndProviderEvidenceTests.test_structural_failure_emits_identity_bound_negative_evidence`가 본다.

## MachineAndProviderEvidenceTests (행 593–848)

- 기반: `unittest.TestCase`. 표지, 클래스 속성, 훅이 없다.
- `profiles(self, **changes)` (행 594–596): `PROFILE_CONFIG`에 `lean_command=["lean-A"]`와 `changes`를 덧씌워 `build_profiles`를 부른다. `(execution_profiles 모듈, 결과)`를 돌려준다.
- `approved(self, tool, command)` (행 598–606): 승인된 도구 체인 신원을 만든다. docstring은 "An approved identity whose recorded executable is this tool file."이다. 실행 파일 경로와 SHA-256, 설정된 명령, 버전 `"fixture"`, 검증기(`formal.py`)의 경로와 해시, 실행 파일 목록, `project=None`을 담는다.

### `test_machine_profile_pins_the_command_and_the_verifier_checks_tool_bytes` (행 608–637)
- 성질: 기계(Lean) 프로필은 명령만 고정한다. 도구의 바이트는 승인된 신원이 검증기에서 한 번 묶는다. 도구 파일이 바뀌어도 프로필 참조는 같다. 그러나 검증기는 바뀐 도구를 실행하지 않고 신뢰 환경 거부로 돌려준다.
- 준비: 명령이 `lean-A`와 `lean-B`인 두 판본의 `formal_check` 프로필. 임시 `lean.exe`(`b"edition one"`)를 명령으로 둔 판본 `first`와, 그 도구의 승인 신원 `env`.
- 실행: 판본을 세 번 만들고(`lean-A`, `lean-B`, 도구 경로), `ep.machine_invocation`을 세 번 부르며, 도구 바이트를 바꾼 뒤 `formal.verify_lean`을 한 번 부른다.
- 단언: 단계별로 확인하는 결과는 다음과 같다.
  1. 두 명령 판본의 참조가 다르다.
  2. `machine_invocation(p, trust_environment=env)`의 인자에 `timeout_seconds`가 없다. `lean_command`가 `[도구 경로]`, `expected_toolchain`이 승인 신원이다.
  3. 도구를 `b"edition two"`로 바꾸고 판본을 다시 만들면 프로필 참조가 같다. `machine_invocation`도 같은 인자를 돌려준다.
  4. `do_math.formal._job_run`을 `AssertionError("changed tool was started")`로 패치하고 `formal.verify_lean(source=..., declarations=["t"], workspace=..., **args)`를 부른다. `(status, reason)`이 `("rejected", "approved toolchain changed before execution")`, `identity_errors`가 `["approved toolchain file changed: <경로>"]`, `error_kind`가 `"trust_environment"`다.
  5. 설정된 명령이 다른 신뢰 환경으로 `machine_invocation`을 부르면 `ValueError`다.
- 대역: `_job_run` 패치(실제 Lean을 부르지 않는다).
- 비고: 주석(627행)은 프로필이 명령만 이름 짓고 승인 신원이 바이트를 검증기에서 한 번 묶는다고 밝힌다. 제품 docstring은 "a Lean check has no deadline"이다. 2의 `timeout_seconds` 부재가 그것이다.

### `test_machine_command_alias_keeps_adopted_argv_and_the_verifier_checks_resolution` (행 639–653)
- 성질: 명령이 별칭(`lean`)이면 프로필은 채택된 인자를 그대로 쓴다. 검증기는 별칭이 실제로 가리키는 파일이 승인된 파일인지 확인한다.
- 준비: 임시 `lean.exe`와 명령 `["lean"]`인 판본. 승인 신원의 설정 명령도 `["lean"]`이다.
- 실행: `machine_invocation`을 부른다. 이어서 `do_math.formal.shutil.which`가 다른 파일 `other.exe`를 가리키게 하고 `_job_run`을 실패로 패치한 채 `verify_lean`을 부른다.
- 단언: 인자의 `lean_command`가 `["lean"]`이다. 검증 결과가 `("rejected", "approved toolchain changed before execution")`이고 `error_kind`가 `"trust_environment"`다.
- 대역: `shutil.which`와 `_job_run` 패치.

### `test_explicit_old_edition_uses_its_model_but_preserves_floor_and_allowlist` (행 655–675)
- 성질: 명시한 옛 판본은 설정이 바뀐 뒤에도 그 판본의 모델을 쓴다. 그러나 역할의 등급 하한과 과제 허용 목록은 여전히 적용된다. 허용 목록은 작업 역할에만 적용되고 해석 역할에는 미치지 않는다.
- 준비: `profiles()`의 옛 판본에서 `intent_interpretation`의 high 판본과 low 판본, `research_work`의 high 판본.
- 실행: `model_policy.selection`을 네 번 부른다. 옛 판본을 명시한 해석 역할(설정 변경 뒤), low 판본을 명시한 해석 역할, 허용 목록이 빈 대상의 해석 역할, 같은 대상의 연구 작업이다.
- 단언: 단계별로 확인하는 결과는 다음과 같다.
  1. high 모델을 `replacement-model`로 바꾼 설정에서, 옛 high 판본을 명시해 선택하면 모델이 옛 판본의 모델이다.
  2. low 판본을 명시하면 `ValueError`다. 해석 역할의 하한이 high이기 때문이다.
  3. 대상 `T`의 허용 목록이 비어 있어도 해석 역할의 명시 선택은 예외 없이 끝난다.
  4. 같은 조건에서 `research_work`의 high 판본을 명시하면 `ValueError`다.
- 대역: 없음.
- 비고: 주석(668행)은 과제 허용 목록이 작업을 다스리고 해석은 자기 프로필을 유지한다고 밝힌다. 2의 제품 문구는 `"explicit profile does not meet the role/task model requirement"`이고, 4의 문구는 `select_profile`의 `"permitted role/model edition"`이다. 시험은 둘 다 유형만 본다.

### `test_runner_preserves_exact_utf8_input_after_seal` (행 677–699)
- 성질: 러너는 봉인과 정확히 같은 UTF-8 바이트를 입력 파일로 쓴다. 봉인과 다른 프롬프트나 봉인 없는 호출은 증거 폴더를 만들기 전에 거부된다.
- 준비: `maintenance` 프로필. 한글을 포함한 텍스트 `"exact input\n한글\n"`에 `boundary_prompt(p)`를 붙인 입력. 그 UTF-8 바이트 수와 SHA-256으로 손수 만든 봉인.
- 실행: 봉인을 준 `runner.run`. 이어서 프롬프트에 `"extra"`를 붙이고 같은 봉인으로 부른다(폴더 `changed`). 끝으로 봉인을 빼고 부른다(폴더 `missing`).
- 단언: `evidence/input.txt`의 바이트가 입력의 UTF-8과 같다. 둘째와 셋째 호출은 `ValueError`(`"seal"`)다. 제품 문구는 `"runner input differs from its UTF-8 seal"`이다. `changed` 폴더가 없다.
- 대역: `Adapter`, `runner_with`.
- 비고: 셋째 호출의 `missing` 폴더가 없다는 것은 단언하지 않는다.

### `test_profile_tools_are_authoritative_and_detached` (행 701–707)
- 성질: 러너 도구는 프로필이 권위를 갖는 값이다. 돌려받은 사본을 바꿔도 프로필은 바뀌지 않는다.
- 준비: scholarly 서버 명령이 `"approved-old-server"`인 판본의 AI 프로필.
- 실행: `runner_tools(p)`의 `scholarly_server.command`를 `"mutated"`로 바꾼 뒤 다시 `runner_tools(p)`를 부른다.
- 단언: 처음 값이 `"approved-old-server"`이고, 바꾼 뒤에 다시 받은 값도 `"approved-old-server"`다.
- 대역: 없음.

### `test_structural_failure_emits_identity_bound_negative_evidence` (행 709–731)
- 성질: 고정 프로필의 러너가 구조적 시작 실패를 만나면, 그 순간의 신원에 묶인 부정 능력 증거를 결과에 싣는다.
- 준비: `maintenance` 프로필. `mock_adapter`의 `capability_identity`는 고정 신원(`cli_sha256`, `worker_sha256`, 호스트 `observed`)을 돌려주고, `start`는 `WindowsJobUnsupportedError`를 던진다. 봉인한 프롬프트를 쓴다.
- 실행: 고정 프로필과 실행 ID `EX-failure`로 `runner.run`.
- 단언: 결과에 `capability_evidence`가 있다. 그 `identity`가 고정 신원, `execution_profile_ref`가 프로필 참조, `capabilities.atomic_local_job.status`가 `"unsupported"`다. `id`가 `id`를 뺀 증거의 내용 해시에 `CE-`를 붙인 값이다.
- 대역: `mock_adapter`.

### `test_identity_is_observed_only_for_a_structural_start_failure` (행 733–748)
- 성질: 출력 경로 충돌 같은 구조적이지 않은 시작 실패는 신원을 관찰하지 않는다. CLI와 소스의 해시는 구조적 시작 실패의 증거로만 계산된다.
- 준비: `mock_adapter`의 `start`가 `FileExistsError("fixture launch conflict")`를 던진다.
- 실행: 고정 프로필로 `runner.run`.
- 단언: `error_kind`가 `"launch_conflict"`이고, `capability_identity`가 불리지 않았다.
- 대역: `mock_adapter`.
- 비고: 주석(747행)은 "Hashing the CLI and adapter sources is evidence for a failed start only."다.

### `test_negative_job_fact_vetoes_next_matching_assignment` (행 750–769)
- 성질: 실제 구조적 시작 실패의 부정 증거는 같은 신원의 다음 배정을 막는다. 그 뒤의 표면 증거가 지원을 말해도 막는다. 다른 호스트의 신원으로 일반화되지는 않는다.
- 준비: `maintenance` 프로필과 신원 `{"host": {"node": "one"}, "cli_sha256": ...}`. 같은 신원의 긍정 표면 증거와 부정 구조 증거를 인스턴스에 둔다. 부정 증거가 더 늦게 관찰되었다.
- 실행: `capability_requirements(state, 참조, current_identity=identity, at=...)`. 이어서 호스트 `two` 신원의 긍정 증거를 더하고 그 신원으로 다시 판정한다.
- 단언: 첫 판정은 만족되지 않는다(실패 메시지 `"actual structural failure did not block the next identical assignment"`). 둘째 판정은 만족된다(실패 메시지 `"failure was generalized to a different host"`).
- 대역: 없음.
- 비고: 제품은 신원이 같은 증거만 모은다. 범위가 `actual_local_start_failure`인 `atomic_local_job` 부정 사실이 하나라도 있으면 `atomic_local_job`을 부족 목록에 더한다(`initialization.py` 43–51행). 주석은 "Help/version output cannot clear a concrete failed local start."다.

### `test_native_claude_report_reaches_normal_result_without_scope_expansion` (행 771–811)
- 성질: Claude 원생 수집 결과는 결합 없는 러너에서 정상 결과가 된다. 저장 투영은 보고된 정지 사유, 사용량, 모델 사용을 그대로 보존한다. 알 수 없는 연산 수와 원격 종료는 알 수 없음으로 남아 범위가 넓어지지 않는다.
- 준비:
  - `maintenance` 프로필 사본의 모델을 `claude:haiku`, 공급자를 `claude`로 바꿔 `seal_profile`로 다시 봉인한다.
  - 임시 폴더에 요청(실행 ID와 참조), 입력(프롬프트), 표준 출력, 표준 오류, 최종 파일, 상태 파일을 쓴다. 표준 출력은 `claude_stream(CLAUDE_INIT, native)`다. `native`는 `CLAUDE_RESULT`에 `stop_reason="max_tokens"`, `modelUsage={"haiku": {"costUSD": 0.125}}`, `total_cost_usd=0.125`를 더한 결과다. 상태 파일에는 종료 코드 0, 입력·요청 해시, 스키마 해시 `None`, 실행 ID와 참조를 넣는다.
  - `CLIExecution`은 `FakeJob(JobInspection(0, (), True))`로 만든다.
- 실행: `ClaudePrintAdapter("not-launched").collect(ex)`. 그 수집 결과를 돌려주는 claude 칸 `Adapter`로 고정 프로필 러너를 부른다. 결과를 `execution_observation`으로 투영한다.
- 단언:
  - 수집 결과가 `"output_collected"`다(실패 메시지는 사유 목록). 러너 결과가 `"completed"`다.
  - 투영의 `stop_reason`이 `"max_tokens"`다.
  - `reported_fields_json`을 읽으면 `usage`가 `native["usage"]`, `model_usage_reported`가 `native["modelUsage"]`, `operation_count`와 `remote_termination`이 `"unknown"`, `evidence_sha256`이 표준 출력의 SHA-256이다.
- 대역: `FakeJob`, claude 칸 `Adapter`(실제 수집 결과를 되돌려 준다).
- 비고: Claude 수집기는 최종 응답을 스트림에서 고르므로(`final_from_stream`), 최종 파일 `b'{"ok":true}'`는 수집 판정에 쓰이지 않는다. `Adapter.collect`는 스크립트 결과를 뒤에 펼치므로, 실제 수집기가 계산한 `provider_observation`(표준 출력 해시 포함)이 대역의 재계산을 덮어쓴다. 이 시험은 `verified_native_final`이나 중앙 원생 제출 경로를 지나지 않는다. 그 경로는 `test_native_final_submission`의 소관이다.

### `test_surface_seal_and_runner_deliver_identical_complete_input` (행 813–837)
- 성질: 역할 입력 준비가 봉인한 프롬프트와 러너가 실제로 전달하는 입력은 바이트까지 같다. 경계 규칙은 정확히 한 번 들어간다.
- 준비: `record_fixtures.surface_state()`의 상태와 `research_preparation` 프로필, 그 역할의 출력 스키마.
- 실행: `context_store.prepare_role_input({...}, instance=state, runtime=runtime, role="research_preparation", profile=p, snapshot="a"*40, workspace=root, activity_id="AC-1", output_schema=schema, artifact_prefix="runtime/artifacts/EX-seal")`. 이어서 그 프롬프트와 명세의 봉인으로 러너를 부른다.
- 단언: `overflow`가 `None`이다. 프롬프트에 `boundary_prompt(p)`가 한 번 나온다. 명세의 봉인 필드가 `prompt_seal(prompt)`와 같다. 러너의 `evidence/input.txt`가 명세의 `artifact_ref`가 가리키는 산출물 바이트와 같다.
- 대역: `Adapter`, `runner_with`.

### `test_native_provider_observation_has_canonical_storage_projection` (행 839–848)
- 성질: 공급자 관찰에 소수(비용)가 있어도, 저장 투영은 그것을 JSON 문자열로 보존해 정규 JSON 저장 규칙을 지킨다. 관찰이 없으면 투영도 없다.
- 준비: `usage`에 `cost_usd=0.125`가 든 관찰.
- 실행: `execution_observation({"provider_observation": observation})`, `canonical_json(stored)`, `execution_observation({})`.
- 단언: `canonical_json`이 예외 없이 끝난다. `reported_fields_json`을 읽으면 관찰과 같다. `stop_reason`이 `"max_tokens"`다. 빈 결과의 투영이 `None`이다.
- 대역: 없음.
- 비고: 제품 docstring은 "Preserve reported numbers losslessly without admitting floats to Git state."다. `canonical_json`은 부동소수를 거부하므로, 이 성공이 소수가 문자열 안에만 있음을 보증한다.

## ResourceWaitTests (행 851–899)

- 기반: `unittest.TestCase`. 표지, 클래스 속성, 훅이 없다.
- `state(self, **changes)` (행 852–857): `DEFAULT_CONFIG`에 `changes`를 덧씌운 설정으로 인스턴스를 만든다. 빈 런타임(실행·예약·공급자 대기)과 `research_work` 프로필을 함께 돌려준다.

### `test_zero_capacity_and_provider_probe_are_distinct_and_read_only` (행 859–874)
- 성질: 작업 슬롯이 0인 모델의 대기는 사용자 몫의 용량 대기이며 재시도 시각이 없다. 공급자 관문이 닫힌 동안은 공급자 대기가 앞선다. 두 판정 모두 런타임을 바꾸지 않는다.
- 준비: 모든 모델의 작업 슬롯을 0으로 둔 `DEFAULT_CONFIG`로 `state(**config)`를 부른다.
- 실행: `admission_check(profile)`. 이어서 공급자 관문을 `waiting`, `retry_at=100`으로 두고, 시각 90과 110에 판정한다.
- 단언: 첫 대기의 `(kind, next_owner)`가 `("capacity", "user")`이고 `retry_at` 키가 없다. 시각 90은 `"provider_limit"`, 110은 `"capacity"`다. 런타임이 관문을 둔 직후의 사본과 같다.
- 대역: 없음.
- 비고: 제품은 용량 제약의 `work_slots`가 0이면 다음 소유자를 `user`로 둔다(`session_slots.py` 162–163행). 이 `SessionSlots`는 관찰자 모드가 아니지만, `admission_check`는 쓰지 않는 판정이다.

### `test_configure_wakes_only_changed_resource_waits_and_keeps_pinned_profile` (행 876–899)
- 성질: 자원 설정을 실제로 바꾸는 사용자 구성은 자원 대기 중인 요청의 대기를 풀고 인스턴스를 `ready`로 되돌리되, 요청의 고정 프로필은 그대로 둔다. 바뀌는 것이 없는 구성은 대기 상태를 유지한다. 일시정지는 풀지 않는다.
- 준비: `engine_fixtures.governance_host()`의 엔진이다. 작업 공간을 현재 폴더로 두고, 모든 등급 모델의 작업 슬롯을 0으로 바꿔 판본을 다시 만든다. 런타임은 `status="waiting"`이고, 큐에는 `goal_audit` 요청 `AC-wait` 하나가 있다. 그 요청은 채택 참조와 대기 `{"kind": "capacity", "next_owner": "user"}`를 갖는다.
- 실행: `e._configure_candidate(e.instance, e.runtime, ...)`를 네 번 부른다. 자원 변경(`waiting`), 빈 구성(`waiting`), 빈 구성(`capacity_waiting`), 자원 변경(`paused`)이다.
- 단언: 단계별로 확인하는 결과는 다음과 같다.
  1. `DEFAULT_CONFIG`의 `session_limits`로 바꾸는 요청으로 `e._configure_candidate(e.instance, e.runtime, request)`를 부른다. 후보 상태의 `status`가 `"ready"`다. 큐 요청에 `dispatch_wait`가 없다. `profile_ref`가 원래 값이다. 원래 런타임의 `status`는 여전히 `"waiting"`이다(후보는 사본이다).
  2. 빈 구성은 `"waiting"`을 유지한다.
  3. 런타임을 `capacity_waiting`으로 두고 빈 구성을 적용하면 `"capacity_waiting"`을 유지한다.
  4. 런타임을 `paused`로 두고 자원 변경 구성을 적용하면 `"paused"`다.
- 대역: `governance_host`의 autospec 대역 둘(`_complete_initial_intent`, `_activate_initialization`). 이 경로에서는 불리지 않는다.
- 비고: 제품은 `status`가 `waiting`/`capacity_waiting`이고 사용자 결정이 바뀐 경우에만 대기를 푼다. 풀리는 대기는 `RESOURCE_WAITS`(`capacity`, `host_capacity`, `resource_unclassified`) 종류뿐이다(`governance_engine.py` 101–107행). 이름의 "only changed"는 2와 3이 확인한다.

## 관계

- 같은 제품 기능을 다른 층에서 검사하는 모듈:
  - `test_budget`은 예약 산술을 순수 함수로 본다. 이 모듈은 그 산술을 `SessionSlots`의 입장과 해제 층에서 본다. `test_machine_scheduling`은 호스트 용량으로 배정 판단을 본다.
  - `test_configuration`은 설정에서 용량 제약과 AI 프로필로 가는 연결 하나를 본다. 이 모듈은 판본의 고정·선택·재채택 전반을 본다.
  - `test_model_runner`는 프로필 없는 러너 수명을 본다. 이 모듈은 고정 프로필이 러너 입력(봉인, 요청 고정, 창, 결합)을 어떻게 제한하는지 본다.
  - `test_control_transport`는 제어 전송 자체를 본다. 이 모듈은 결합이 러너와 두 작업자에게 전달되고 MCP 서버로 등록되는 것을 본다.
  - `test_codex_adapter`와 `test_claude_adapter`는 작업자 인자와 수집기를 본다. 이 모듈은 그 위의 능력 신원·증거와 결합 스냅숏을 본다.
  - `test_execution_lifecycle`의 `ProviderAdmissionTests`는 공급자 입장의 대기 기록과 복구 정산을 엔진 층에서 본다. 이 모듈은 관문의 점검 소유를 `SessionSlots` 층에서 본다.
  - `test_model_metadata_boundary`는 과제 허용 목록이 검토자에게 미치지 않는다는 규칙을 본다. 이 모듈은 명시 판본, 하한, 해석 역할과의 관계를 본다.
  - `test_native_final_submission`은 원생 최종 응답의 중앙 포착을 본다. 이 모듈의 Claude 원생 보고 시험은 그 앞 단계인 러너 결과와 저장 투영까지만 본다.
- 픽스처 의존: `provider_fixtures`(`PROFILE_CONFIG`, `Adapter`, `runner_with`, `mock_adapter`, `FakeJob`, `claude_stream`, `CLAUDE_INIT`, `CLAUDE_RESULT`), `research_fixtures`(`dispatched_launch`, `observation_rule`), `record_fixtures.surface_state`, `engine_fixtures.governance_host`. `mock_adapter`의 소비자는 이 모듈뿐이다.
- 이 모듈에만 있는 도우미: `MachineAndProviderEvidenceTests.profiles`, `approved`; `ResourceWaitTests.state`; 테스트 안의 지역 함수 `exchange`, `rpc`, `call`, `publish`, `formal_profile`, `admit`.
