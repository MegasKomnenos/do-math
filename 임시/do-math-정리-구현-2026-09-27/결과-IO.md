# do-math 정리 구현 결과: IO 그룹 (외부 프로세스·제어·관찰)

경로는 worktree `C:/math-worktrees/c-io/.claude/skills/do-math/` 기준이다. `scripts/do_math/`는 `do_math/`로, `scripts/tests/`는 `tests/`로 줄여 적는다. 저장소 밖 보조 스크립트는 모두 `C:/math-worktrees/tools/`에 두었고, 제품 코드에는 호출 도구를 더하지 않았다. Codex·Claude를 부르는 실행은 하나도 하지 않았다.

## 1. 브랜치, 커밋, 바꾼 파일

- 브랜치: `c-io` (시작점 `c-int` = `d380cd3`)
- 마지막 커밋: `e3c5ac1`
- 제품(13): `do_math/cli_worker.py`(새 모듈), `do_math/claude_adapter.py`, `do_math/claude_worker.py`, `do_math/cli.py`, `do_math/codex_adapter.py`, `do_math/codex_worker.py`, `do_math/control_contracts.py`, `do_math/control_transport.py`, `do_math/engine.py`(`_observe_running`와 import 한 줄만), `do_math/model_runner.py`, `do_math/observation_transport.py`, `do_math/observations.py`, `do_math/scheduled_operator.py`
- 시험(23): `tests/research_fixtures.py`, `tests/test_background_processes.py`(주석), `test_checkpoint_persistence`, `test_claude_adapter`, `test_cli`, `test_codex_adapter`, `test_control_preview`, `test_control_transport_io`, `test_currentness_recovery`, `test_execution_observation_profile`, `test_host_resources`, `test_model_runner`, `test_native_final_submission`, `test_observation_audit1`, `test_observations`, `test_provider_final_contract`, `test_redesign_ACTIVITIES`, `test_redesign_ENGINE`, `test_redesign_EVIDENCE_walkthroughs`, `test_redesign_OBSERVATION`, `test_redesign_PROFILES`, `test_research_reliability`, `test_worker_temporary_outputs`
- 문서(1): `scripts/이음새-정본.md` 6절 표(행 3개 수정, 1개 추가)

## 2. ID별 처분

| ID | 처분 | 내용 |
|---|---|---|
| IO-01 | 구현함 | 러너 세 클래스를 `ModelRunner` 하나로 합쳤다. 생성자가 `ADAPTERS`로 공급자마다 어댑터를 만들어 `adapters`에 두고, `run`이 `provider_for(model)`로 고른다. `claude:` 접두 제거는 `run` 안 한 곳이다(`model_runner.py:48-53`). 공급자별 worker 요청 필드는 어댑터 메서드 `LocalCLIAdapter.worker_options`와 `CodexExecAdapter.worker_options`로 옮겼다. worker 공통 골격은 새 중립 모듈 `cli_worker.py`로 옮겼고, 두 worker가 이를 import한다. `CodexExecution`은 `CLIExecution`으로 이름을 바꿨고 모듈 docstring을 고쳤다. 식별 모듈에 `cli_worker`를 더했다(Codex 7개, Claude 10개). 시험의 러너 생성은 `test_model_runner.runner_with(adapter, provider)`로 통일했고, 대역 어댑터는 자기 공급자의 실제 `worker_options`를 쓴다(`Adapter(result, provider)`, `mock_adapter(provider)`). |
| IO-02 | 구현함(조건 안의 형태, 통합표 제안과 다름) | 제안한 `(transport_id, request_id)` 키 직접 읽기는 조건을 깨므로 하지 않았다. 엔진 기록에 없는 요청의 ID를 다른 전송이 재사용하는 경우, 전역 조회 없이는 거부할 수 없기 때문이다. 대신 `_receipt`의 glob을 전송 디렉터리마다 존재 검사 하나로 바꿨다(`control_transport.py:489-498`). 이렇게 하면 전역 유일성과 거부 경로가 그대로 남고 새 상태도 없다. 실측(IO-02 측정, 7절): 새 요청 조회의 중앙값이 300 전송에서 41.8→6.0ms, 1000 전송에서 179→37ms로 줄었다. 비용은 여전히 전송 수에 비례한다. O(1) 조회에는 전역 색인이 필요하며, 색인은 새 영속 상태이거나, 쓰기 잠금 수명에 묶인 프로세스 캐시(새 상태와 무효화 규칙)다. 재사용 거부를 고정하는 시험을 더했다(`test_request_id_rejected_without_engine_record_stays_taken_in_every_transport`). |
| IO-03 | 구현함 | 생성자는 전송을 읽지 않는다. `_open`은 `None`에서 시작하고, 첫 `pump`가 스캔한다. `issue`와 `close`는 집합이 있을 때만 갱신한다(`control_transport.py:159-160, 176-178, 258-264`). 시험 `test_open_transports_are_read_at_the_first_pump_not_at_construction`을 더했다. |
| IO-04 | 구현함 | `output.schema.json`은 `control_binding is None`일 때만 쓴다(`model_runner.py:97-103`). `test_provider_final_contract`의 bound 분기는 파일이 없음을, unbound 분기는 전체 스키마 보존을 단언한다. |
| IO-05 | 구현함 | 다음을 지웠다: `observation_subjects` 읽기, `validate_rules`·`validate_rule_proposal`의 `allowed_subjects` 인자와 분기, `self_check_feedback`의 `rejected_rule_reasons` 인자와 payload 필드, `WORKER_FEEDBACK_FIELDS`의 해당 항목, `last_checkpoint`. `responses` 목록은 정수 `response_count`로 바꿨다. `test_redesign_OBSERVATION.py:77`을 고쳤다. |
| IO-06 | 구현함 | 다음을 지웠다: `CLIExecution`의 `request_path`·`prompt_path`·`snapshot_dir`·`stop_requested`, 생성자 인자 `describe_timeout`(클래스 속성 10.0으로 남김), `ObservationBatch.bytes_received`, `ControlTransport.receipt`·`records`, `collect`의 JSON 실패 대체 분기, 러너의 `hasattr`·`isinstance` 방어 조건. 시험 8개 파일을 현행 계약으로 고쳤다. 스냅숏 요청은 `worker_argv[-1]`이 가리키는 실제 파일을, 영수증은 `worker_receipt` 또는 같은 요청의 재수신 재생을 읽는다. |
| IO-07 | 구현함 | 손 조립 해석 8곳을 `strict_json_loads`로 바꿨다: `model_runner.py` 최종 응답·저장 요청, `observations.py` checkpoint·`observation-rules.json`, `codex_worker.load_request`, `claude_worker.load_request`·출력 스키마, `cli._json_document`. 영역 밖 `payloads.py:175`, `repository.py:731·820`, `submission.py:238`은 건드리지 않았다(8절). |
| IO-08 | 구현함 | `record_self_check_response`가 `self_check_response_errors`로 판정하고, `import jsonschema`를 지웠다(`observations.py:843-850`). |
| IO-09 | 구현함 | `evaluate_rules`의 `validate_rules` 호출과 두 `build_argv`의 `validate_execution_binding` 호출을 지웠다. |
| IO-10 | 구현함 | `cli.WIRE_VERSION`과 `cli.ERROR_EXIT_CODES`를 두었다. `main`은 공통 `_fail`로 오류 종류마다 이 표의 종료 코드를 쓰고, `--describe`는 같은 표를 싣는다. `request_fields`는 `list(request_schema['properties'])`다. `test_cli`에 발견 계약과 실제 종료 코드의 일치 단언을 더했다. |
| IO-11 | 구현함 | 다음을 했다: `CliInputError`·`ValueError` 절 통합, `prepare-import-approval`의 중복 `canonical_json` import 제거, `CANDIDATE` 텍스트 목록에서 `formal_result_ref` 제외. |
| IO-12 | 구현함 | 2절 1항의 설계 변경으로 닫았다. `control_self_check` 도구 입력 스키마의 `response`를 2라운드 이전 모양 `{"type": "object"}`로 되돌렸다. 응답 모양은 도구 `description`에 `SELF_CHECK_RESPONSE_SCHEMA`의 JSON 직렬로 싣는다(`control_transport.py:542-544`). 정확성은 공유 함수 `self_check_response_errors`가 보내는 쪽(`worker_submit`)과 받는 쪽(IO-08)에서 판정한다. 근거와 수리 보고 스키마의 처분은 7절에 적었다. |
| IO-13 | 구현함 | `ObservationTracker.observe`가 `source`를 키워드 필수로 받는다. `source is None`일 때 쓰던 세 의미(대체 시계, 모든 의무를 전달·인지된 것으로 보는 판정, 폴 인지 건너뛰기)를 지웠다(`observations.py:552-555, 660-661, 923-929`). 시험 89곳은 `research_fixtures.observe(tracker, event)`로 옮겼다. 이 도우미는 추적기 시계를 수신 시각으로 한 다음 한 바이트 행의 좌표를 준다. 옛 "모두 인지됨" 가정에 기대던 시험 둘(`test_research_reliability` 소유자 구분, `test_observation_audit1.submission`)은 `research_fixtures.acknowledge`로 실제 전달과 성공 조회를 거친다. |
| HIS-13 | 구현함 | 엔진 `_observe_running(execution_id, tracker, batch)`는 `ObservationBatch`만 받는다. dict 분기, `batch is None` 처리, 비묶음 자기 점검 요청 경로를 지웠고, 쓰이지 않게 된 `self_check_request` import 한 줄도 지웠다. dict를 넘기던 시험 4곳은 `research_fixtures.observation_batch`로 옮겼다(빈 묶음은 tick, 실제 사건은 그 사건을 담은 묶음). |
| HIS-10 | 구현함(오프라인 재생) | `probe_cli --role`은 더하지 않았다. 재생 스크립트 `C:/math-worktrees/tools/his10_codex_final_replay.py`가 제품의 `CodexExecAdapter.parse_response`와 `LocalCLIAdapter.validate_final`, 곧 `collect`가 final을 판정하는 두 단계를 보존 기록에 적용한다. 결과: 서로 다른 Codex 스트림 34개(사본 328개). final.txt가 있는 29개가 모두 일치하고 모두 `turn.completed`로 끝났다. 여러 `agent_message`가 있는 표본 5개도 일치했다. 불일치 사례는 0개다. 좌표와 확인하지 못한 범위는 7절에 적었다. |
| REV-25 | 구현함(설계로 닫음) | 역할 응답 스키마는 CLI로 가지 않는다. 엔진은 모든 실행에 바인딩을 발급한다(`engine.py:3021`). 러너는 그 바인딩을 받으면(`engine.py:3259`) 출력 스키마를 요청에 넣지 않는다(`model_runner.py:97`). CLI에 닿는 나머지 두 경로는 IO-12 조치로 입증된 모양이 되었다. MCP 도구 입력 스키마는 되돌렸고, 수리 보고 스키마는 `OPERATOR_SCHEMA`의 키워드로 줄였다. 실제 공급자 실행은 하지 않았다. |

영역 밖 관찰 두 건도 처리했다.
- `control_transport.close`: 삼킨 `ValueError`는 기록되지 않았다. 지금은 정착시키지 못한 재전달마다 `{"source": "inbox/<파일>", "reason": ...}`을 닫힌 상태 `state.json`의 `unsettled_deliveries`에 기록하고, 반환값에도 싣는다(`control_transport.py:296-317`). 시험 `test_close_records_a_changed_redelivery_it_cannot_settle`을 더했다.
- `claude_worker` 직접 적재 시험: `test_codex_adapter.test_claude_worker_remains_importable_as_its_direct_job_root`를 codex 쪽 시험과 같은 형태로 더했다.

## 3. 새 공유 정의와 지운 공개 이름

새 공유 정의(이음새 정본 6절에 반영):
- `cli_worker.py`: `STATUS_BINDING_KEYS`, `COMMON_REQUIRED`, `COMMON_OPTIONAL`, `validate_execution_binding`, `validate_max_runtime`, `check_common_request`, `run_cli`(모두 `codex_worker`에서 옮김), 그리고 새로 둔 `ENV_ALLOWLIST`, `allowed_environment(source, extra)`
- `codex_adapter.py`: `CLIExecution`(이름 변경), `LocalCLIAdapter.worker_options(evidence_dir)`
- `model_runner.py`: `ModelRunner.adapters`(공급자 → 어댑터)
- `cli.py`: `WIRE_VERSION`, `ERROR_EXIT_CODES`(모듈 안에서 공유하므로 정본 표에는 올리지 않음)
- 시험 도우미: `research_fixtures.observe`, `acknowledge`, `observation_batch`(정본 표에 올림), `test_model_runner.runner_with`, `mock_adapter`

지운 공개 이름:
- `model_runner.CodexModelRunner`, `ClaudeModelRunner`, `ModelRunner.codex`·`claude`
- `codex_adapter.CodexExecution`(와 필드 `request_path`, `prompt_path`, `snapshot_dir`, `stop_requested`)
- `codex_worker`의 `STATUS_BINDING_KEYS`, `COMMON_REQUIRED`, `COMMON_OPTIONAL`, `_ENV_ALLOWLIST`, `validate_execution_binding`, `validate_max_runtime`, `check_common_request`, `run_cli`(→ `cli_worker`)
- `LocalCLIAdapter.__init__`의 `describe_timeout` 인자
- `ObservationBatch.bytes_received`
- `ControlTransport.receipt`, `ControlTransport.records`
- `self_check_feedback`의 `rejected_rule_reasons` 인자와 `WORKER_FEEDBACK_FIELDS`의 같은 이름
- `validate_rules`·`validate_rule_proposal`의 `allowed_subjects` 인자
- `ObservationTracker.allowed_subjects`·`responses`·`last_checkpoint`(→ `response_count`)
- `observe`의 `source=None` 기본값

옛 이름은 `grep -rn`으로 확인했다. `docs/do-math/` 아래의 동결된 역사 기록 밖에 남은 참조는 없다.

## 4. 필요한 문서 변경

1. `references/공통-실행.md` 165행: "정확한 응답 형식은 `control_self_check` 도구의 입력 스키마로 공개된다"를 이렇게 바꾼다: "정확한 응답 형식은 `control_self_check` 도구 설명에 JSON Schema로 공개된다. 도구 입력 스키마는 `response`가 객체라는 것만 알린다." 형식이 틀린 응답이 도구 오류로 돌아온다는 뒤 문장은 그대로 맞다.
2. `references/초기화-운전.md` 215행: Codex 어댑터 식별 모듈 목록에 `cli_worker`를 더한다(`cli_worker`, `codex_worker`, `control_transport`, `file_io`, `windows_job`, `scholarly`, `codex_adapter`). "Claude 어댑터는 여기에 `claude_worker`, `claude_adapter`, `claude_stream`을 더한다"는 그대로 맞다.
3. `.agents/` 생성 사본: 통합자가 재생성한다.

`계약/독립-운영.md` 55행의 `repair_outcome=repaired|unresolved` 요구는 그대로 맞다. 허용 값은 이제 CLI 스키마가 아니라 프롬프트(`scheduled_operator.py` 555-556행)와 수신 검사 `collect_repair_verification`이 정한다.

## 5. 실행한 시험

모두 `scripts/`에서 `python run_tests.py --output <새 폴더> ...`로 돌렸다. 한 번에 한 프로세스만 띄웠다. 조각 실행과 전체 실행은 하지 않았다.

1. 편집 확인 `io-r1`: `test_model_runner test_codex_adapter test_claude_adapter test_control_transport_io test_observations test_observation_audit1 test_redesign_OBSERVATION test_provider_final_contract test_control_preview test_worker_temporary_outputs test_execution_observation_profile`. 결과는 통과 112, 실패 1이었다. 실패한 `test_codex_adapter...test_invalid_timeout_duplicate_json_and_windows_sandbox_fail_before_start`의 원인은 IO-07이다. 요청 파일의 `NaN`이 필드 검사 전에 엄격 해석에서 거부되어, 사유 문구가 바뀌었다. 시험을 현행 계약으로 고쳐 두 규칙을 따로 단언하게 했다. `NaN` 요청은 "non-finite JSON constant"로, `max_runtime_seconds=0`은 "max_runtime"으로 거부됨을 본다. 고친 시험은 2번 실행에서 통과했다.
2. 인계 확인 `io-r2`(`DO_MATH_KNOWLEDGE_TEST_LEAN` 지정): 위 고친 시험 하나와 `test_redesign_PROFILES test_redesign_ACTIVITIES test_checkpoint_persistence test_research_reliability test_host_resources test_native_final_submission test_background_processes test_cli test_currentness_recovery test_redesign_EVIDENCE_walkthroughs test_redesign_ENGINE test_diagnosed_installation_recovery test_operator test_contracts test_engine`. 결과는 통과 276, 오류 1이었다(270초). 오류는 `test_redesign_EVIDENCE_walkthroughs.DesignWalkthroughs.test_w12_query_import_metadata_and_next_snapshot_preserve_epistemic_distinctions`다. `TypeError: start_review() got an unexpected keyword argument 'owner_activity_id'`가 `tests/test_redesign_STORAGE.py:1216`에서 났다. 이 오류는 변경 전부터 있던 것이다. 이 브랜치는 `review_cycle.py`와 `test_redesign_STORAGE.py`를 바꾸지 않았고(`git diff c-int`로 확인), `c-int`의 `start_review`(`review_cycle.py:108-109`)에는 그 인자가 없다(8절).
3. IO-02 변경 뒤 `io-r3`: `test_control_transport_io test_control_preview test_redesign_ACTIVITIES`. 결과는 통과 35다(새 시험 3개 포함).
4. `io-r4`: `test_redesign_PROFILES.ProfileTests.test_execution_control_is_registered_and_round_trips_in_child`(MCP 자식 왕복). 결과는 통과 1이다.

기계적 확인: 제품·시험·`probe_cli.py` 전체를 컴파일했고, `tests/test_*.py` 전 모듈을 `importlib`로 적재했다(오류 0). 옛 이름 grep도 했다(3절).

돌리지 않은 관련 시험: 소비자 쪽 모듈은 지침 2절에 따라 import 확인만 했다. 예를 들면 `test_probe_cli`(`ModelRunner` 소비), `test_submission_tools`·`test_machine_parallel`(제어 전송 소비), `test_redesign_STORAGE`, 그 밖에 추적기·엔진을 간접으로 쓰는 모듈이다. `io-r2`의 `test_redesign_ENGINE`·`test_engine`은 IO-02 조회 변경 전에 돌렸다. 조회 변경의 계약 시험은 `io-r3`에서 돌렸다.

## 6. 기능이나 시험 범위가 바뀐 것

- 바인딩된 실행의 `provider-evidence/`(IO-04): `output.schema.json`이 빠진다. 까닭은 공급자가 받지 않은 스키마를 공급자 증거처럼 남기기 때문이다. 잃는 것은 없다. 같은 스키마가 입력 묶음 `runtime/artifacts/<bundle>/schema.json`으로 봉인된다. 얻는 것은 실행마다 파일 하나와 봉인 산출 하나가 줄고 오해 소지가 사라지는 것이다.
- 작업자에게 가는 자기 점검 요청 payload(IO-05): 늘 `[]`이던 `rejected_rule_reasons`가 빠진다. 까닭은 생산자가 없기 때문이다. 잃는 것은 없다.
- 엄격 해석(IO-07): worker 요청, CLI JSON 파일, 규칙 파일, 최종 응답, checkpoint가 중복 키·이름 붙은 상수·지수 넘침을 한 규칙으로 거부한다. 거부 사유 문구가 바뀐다(예: 요청의 `NaN`은 "non-finite JSON constant"). 규칙 파일의 중복 키는 이제 제출 검사와 같이 "duplicate"로 반려된다.
- MCP 도구 `control_self_check`(IO-12): 입력 스키마가 응답 모양을 강제하지 않는다. 까닭은 공급자 수용이 확인된 모양만 공급자에게 보내기 위해서다. 잃는 것은 공급자가 스키마로 모델 출력을 미리 제한할 가능성이다. 이 가능성은 원래 확인되지 않았다. 얻는 것은 실측 없이도 도구 목록이 거부될 위험이 없다는 것이다. 형식 오류는 전처럼 `worker_submit`이 도구 오류로 돌려주고 수신자가 다시 판정한다.
- 수리 보고 스키마: `repair_outcome`의 `enum`과 `verification_evidence` 항목의 `minLength`를 CLI 스키마에서 뺐다. 까닭은 보존된 실제 실행에서 이 키워드들이 수리 보고 스키마로 쓰인 기록이 없기 때문이다(7절). 잃는 것은 이것이다. 허용되지 않은 `repair_outcome` 값은 러너 `output_validation`으로 실패하는 대신 `collect_repair_verification`에서 거부된다. 결과는 같은 `recovery_failed`이고 오류 문구만 다르다. 빈 문자열 증거 경로는 파일이 아니므로 같은 함수가 거부한다.
- 관찰(IO-13, HIS-13): 추적기의 두 번째 판정 의미가 사라졌다. 시험은 운영 의미를 검사한다. 연구 행동이 의무를 어기려면 실제 전달과 성공한 조회가 먼저 있어야 한다. 이 전제에 기대던 시험 둘은 `acknowledge`로 그 전제를 실제 경로로 만든다.
- `close`: 닫힌 `state.json`에 `unsettled_deliveries`가 생길 수 있다. 얻는 것은 삼킨 오류의 기록이다.
- 핀 고정 프로필이 있는 Codex 실행에 `claude_only_assigned_model`을 따로 넘기면, 이제 Claude와 같게 "a pinned profile supplies ..."로 거부된다. 전에는 옛 `ModelRunner`가 Codex에 대해 조용히 버렸다. 제품 호출자(엔진, 수리, `probe_cli`) 가운데 프로필과 함께 이 인자를 넘기는 곳은 없다(grep `claude_only_assigned_model=`: `probe_cli.py:69` 한 곳, 프로필 없음).
- IO-02: 거부 결과는 같다. 조회 비용만 바뀐다.
- IO-01, IO-03, IO-06, IO-08, IO-09, IO-10, IO-11: 제품 동작 변화는 없다(확인 범위: 5절의 시험).

## 7. 막힌 지점, 접근을 바꾼 지점, 예상과 달랐던 결과

**IO-12 근거: 되돌린 모양이 실제 운전에서 쓰였다.**
- 이력: `{"type": "object"}` 모양의 `response` 노드는 `7d2597e`(2026-09-23)이 들였고 `379a171`(2026-09-26)이 바꿨다(`git log -S`). `c44dd7b`의 `control_transport.py` 453-454행이 그 모양이다.
- 실행 기록: `C:/math/.skill-workspace/initialization-fixes/measured-export/runtime/`의 실제 Codex 실행 네 건이 모두 `control_binding`을 가진 바인딩 실행이다. 곧 `execution_control` MCP 서버가 CLI에 설정되어 도구 목록을 냈다. 네 건은 `artifacts/BA-01M3BY026Z7EM0ZMC8MYR2GP30`, `BA-01M3BY3F0E50QET1DMDK39P0R3`, `BA-01M3BY8JJEP81F0PDB27G32PYD`, `BA-01M3BYB4GBFKMB5WVD1A172K2E`의 `provider-evidence/`이며, `gpt-6-sol`로 2026-09-25에 실행되었다. 모두 `cli_exit_code` 0, `stderr.txt` 0바이트, 마지막 사건 `turn.completed`다.
- 판본: 이 실행의 설치 기록 `runtime/installation/state.json`이 적은 `control_transport.py` 해시 `b846cd58…`는 `git show c44dd7b:…/control_transport.py`의 sha256과 같다. 같은 폴더의 사본이 `.skill-workspace/initialization-review-20260925/handoff-snapshot/`에도 있다.
- 범위: 이 실행들은 제어 도구를 부르지 않았다. 입증된 것은 "이 입력 스키마를 가진 서버가 도구 목록 단계에서 실행을 깨지 않았다"까지다. Claude로 바인딩된 실행의 보존 기록은 찾지 못했다(`.skill-workspace`, 두 `임시` 보관소, `docs/do-math`에서 `control_self_check`·`execution_control`을 grep한 결과, stream 파일에 일치가 없었다). 되돌린 모양은 2라운드 이전 판의 Codex·Claude 공통 설정 경로에서 쓰던 모양 그대로다.

**수리 보고 스키마(`scheduled_operator.py:58`).** 이력상 `enum`·`minLength`는 `7d2597e`부터 있었다. 2라운드가 새로 넣은 것이 아니다. 그러나 보존된 실행 가운데 진단된 수리 보고 스키마를 받은 실행은 없었다(`repair_outcome` grep 0건). 보존된 출력 스키마 실행의 키워드를 조사한 결과는 이렇다. Codex `--output-schema` 실행은 1건이며 `additionalProperties`·`required`만 썼다. 그 밖에 `docs/do-math/개선-검증-2026-09-16/operator-probe.json`의 운영자 실행이 비진단 `OPERATOR_SCHEMA`(`type`·`items`·`additionalProperties`·`required`)를 받아 완료했다. 파견문의 두 경우("2라운드 이전부터 실제 운전에서 쓰임" / "새로 들어옴") 가운데 앞 경우의 "실제 운전에서 쓰임"이 성립하지 않으므로, 입증된 모양으로 줄였다. 조사 스크립트는 `C:/math-worktrees/tools/io_schema_keywords.py`다.

**HIS-10 재생 좌표.**
- 표본: `thread.started`로 시작하는 서로 다른 Codex stdout 34개. 내용 해시로 중복을 제거했으며 사본은 328개다. 결과 파일은 `C:/math-worktrees/reports/his10-replay.json`이다.
- 출처: `.skill-workspace/do-math-claude/codex-live-1789688563111208300/evidence`, 위 measured-export 네 건(바인딩, 2026-09-25), `docs/do-math/구현-검증-2026-09-14/`와 `docs/do-math/문서-검증-2026-09-15/readers/` 아래 29개(같은 사본이 `임시/do-math-resume-20260920/checks/*/repository/docs/do-math/`에 있다).
- 결과: final.txt가 있는 29개 모두 `final.txt`가 종료 직전 `agent_message`와 바이트 단위로 같았다. 29개 모두 `parse_complete`이고 `turn.completed`로 끝났다. 여러 메시지를 가진 5개는 `BY8JJEP81`(3개), `BYB4GBFKMB`(2개), `feature2/cli-profile`의 `local-access-pass`·`unelevated-absolute-failure`·`unelevated-relative-failure`(각 2개)다.
- final.txt가 없는 5개는 모두 중지된 실행이다: `구현-검증-2026-09-14/cli/cancel`, `stop-receipt/cancel`(마지막 사건 `turn.started`), `feature2/observation/*/raw-executions/EX-01M2FG4…`, `EX-01M2FGPK…`, `EX-01M2FH13…`(마지막 `item.started`). 제품은 이들을 `final_message_missing`·`turn_completed_missing`으로 판정하며, 이는 설계대로다. 불일치 사례는 없다.
- 확인하지 못한 범위: 2라운드 이후 판(`379a171` 이후)으로 실행한 Codex 기록은 없다. 표본의 Codex CLI 판본은 2026-09-14~25 사이의 것뿐이다. 빈 final이나 여러 줄 final의 끝 줄바꿈이 다른 경우는 표본에 없다. `--output-schema`를 쓴 비결합 표본은 1개다. Claude는 이 대조의 대상이 아니다(final을 stream에서 고른다).

**IO-02 측정.** 스크립트는 `C:/math-worktrees/tools/io02_glob_cost.py`, `io02_stat_cost.py`다. 임시 폴더에 전송 디렉터리 N개와 outbox 파일 3개씩을 만들고 새 ID를 20회 조회해 중앙값을 쟀다. 시험 실행과 겹친 부하 아래의 값이다.

| 방식 | 100 | 300 | 1000 |
|---|---|---|---|
| glob | 14.4ms | 41.8ms | 179ms |
| 목록+존재 검사 | 2.0ms | 6.0ms | 37ms |

**접근을 바꾼 지점.**
- IO-10에서 `main`의 예외 절을 합치다가 `GitStateStoreError`가 `RuntimeError`의 하위 클래스임을 확인했다(`git_store.py:30`). 그래서 절 순서를 원래대로 되돌렸다(도구 오류 → 계약 오류 `RuntimeError`).
- IO-01에서 처음에는 Codex 호출의 `claude_only_assigned_model`을 옛 `ModelRunner`처럼 버리려 했다. 그러나 프로필이 있을 때 명시 인자를 거부하는 시험(`test_redesign_ENGINE...test_runner_takes_its_tools_only_from_the_pinned_profile`)과 제품 호출자 확인에 따라 거부 규칙을 두 공급자에 같게 두었다(6절).
- 셸 heredoc 인용 문제로 긴 편집 스크립트는 `C:/math-worktrees/tools/io_edit_*.py` 파일로 돌렸다. 시험 호출 89곳의 변환은 AST 기반 `io_convert_observe.py`로 했다.

## 8. 다른 그룹 범위에서 발견한 문제

- REV/STO(통합 브랜치 `c-int`에 이미 있음): `tests/test_redesign_STORAGE.py:1216`의 `_reviewed_candidate`가 `review_cycle.start_review(..., owner_activity_id=...)`를 부르는데, `c-int`의 `start_review`(`review_cycle.py:108-109`)는 그 인자를 받지 않는다. 그래서 `test_redesign_EVIDENCE_walkthroughs...test_w12_query_import_metadata_and_next_snapshot_preserve_epistemic_distinctions`가 `TypeError`로 오류가 난다. `test_redesign_STORAGE`의 같은 도우미를 쓰는 다른 시험도 영향을 받을 수 있다.
- ENG: `engine.py`의 `_publish_control_request`는 같은 요청 ID를 인스턴스 전체 `control_receipts`에서 선형으로 찾는다(현재 1136-1137행). 전송 쪽 전역 규칙(IO-02)과 뜻은 맞는다. 이력에 비례하는 조회 비용은 ENG 범위다.
- STO/REV: IO-07과 같은 손 조립 해석이 `payloads.py:175`, `repository.py:731`, `repository.py:820`, `submission.py:238`에 남아 있다(검증 IO-07 정정).
