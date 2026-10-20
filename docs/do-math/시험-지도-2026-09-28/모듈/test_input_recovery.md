# test_input_recovery

| 항목 | 값 |
|---|---|
| 조각 | `lifecycle` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_input_recovery.py` (448행) |
| 클래스 / 테스트 | 4 / 10 |
| 시험 대상 제품 코드 | 입력 초과(input overflow) 처리를 맡는 `ResearchEngine`의 메서드 `_pending_input_overflow_retry`, `_resolve_input_overflow_question`, `_apply_input_overflow_resolutions`, `_provider_admit`(대역으로 대체), `_context`, `run`, `process_controls`; `do_math/cli.py`의 `configure`, `request --retry-action`, `status`, `close`(`run_cli`/`cli_result` 경유); `do_math/execution_profiles.py`의 `build_profiles`, `resolve_profile`, `seal_profile`, `profile_ref`, `capability_evidence`; `do_math/submission.py`의 `extension_schema`, `payload_issues`; `do_math/integration.py`의 `apply_bundles`; `do_math/planning.py`의 `contract_hash` |
| 사용하는 픽스처 모듈 | `research_fixtures`: `FixtureAdapter`, `bare_engine`, `cli_result`, `restore_template`, `run_cli`, `seal_response`, `local_job_runner`, `producer_result`, `supply_observation_rules`; `state_fixtures`: `ACTIVE_CONFIG`, `active_instance`, `start_active_copy`; `engine_fixtures`: `context_engine`, `package`; `runner_fixtures`: `ScriptedRunner`, `formal_ok`, `common`, `context_from`; `record_fixtures`: `approved_task`, `approve_task`, `task_contract` |
| 격리 표지 | 없음. 다만 `ScriptedRunner`와 지역 러너가 `local_job_runner`로 모델 호출마다 실제 Windows Job 자식 프로세스를 띄운다 |
| 시작 상태 | `InputRecoveryPublicTests`: 2단 위에 쌓은 모듈 전용 빌드 `overflowed_maintenance`(`restore_template`). `InputRecoveryMarkerUnitTests`: 1단(정적 메서드 직접 호출)과 `bare_engine`. `OverflowConnections`: 메모리 엔진 대역 `context_engine`(실제 문맥 생산자, 대역 저장소) 위의 `approved_task`. `OverflowGitConnection`: 2단(`start_active_copy`)에서 시험용 러너로 엔진을 세 단계 몬다 |

## 목적

모듈 docstring은 "입력 초과 복구: 계획자의 프로필 선택과 공개 재시도를, 메모리에서와 임시 Git 인스턴스에서" 시험한다고 밝힌다.

입력 초과는 AI 행동의 역할 입력을 포장했더니 실행 프로필의 `max_input_bytes`를 넘은 상황이다. 엔진은 그 행동을 `waiting_actions`에 `input_overflow` 대기로 붙잡고, 해결 질문(`question_links`)을 열며, `runtime['input_overflows']`에 실패를 기록한다. 풀리는 길은 둘이다.

1. 공개 재시도: 사용자가 설정으로 한도를 올린 뒤 `request --retry-action <행동 ID>`를 보낸다. 엔진은 행동에 재시도 표지(`input_overflow_retry`, 상태 `pending`)를 달아 다시 포장하고, 이번에도 넘치면 새 실패와 새 질문을, 맞으면 해결 기록(`input_overflow_retry_resolved`)을 남긴다.
2. 계획자의 선택: 연구 계획(`research_plan`) 실행의 문맥에 붙잡힌 행동과 허용 프로필 후보(`input_overflow_requests`)가 실리고, 계획자는 확장 `input_overflow_resolutions`로 더 큰 프로필 하나를 고른다. 엔진은 같은 행동(같은 소유 활동, 같은 모델 평가)을 고른 프로필로 대기열에 되돌린다.

이 모듈은 두 길의 공개 연결, 재시도 표지의 의미, 계획자 선택의 검증(낡은 계약, 제공되지 않은 프로필, 바뀐 질문, 다른 역할, 중복, 알 수 없는 행동), 통합 영수증에 의한 중복 방지, 그리고 선택된 프로필로 원래 작업이 러너에 도달하는 끝까지의 흐름을 검사한다.

## 모듈 수준 요소

- 행 11–13: `SCRIPTS`(스킬의 `scripts/` 폴더)를 없을 때만 `sys.path` 앞에 넣는다.
- 행 15–26: 제품 `execution_profiles`, `ResearchEngine`, `canonical_json`, `planning`과 픽스처 `ScriptedRunner`, `formal_ok`, `FixtureAdapter`, `bare_engine`, `cli_result`, `restore_template`, `run_cli`, `ACTIVE_CONFIG`, `active_instance`, `start_active_copy`, `context_engine`, `package`, 그리고 `patch`, `create_autospec`, `hashlib`, `tempfile`을 가져온다. import가 여러 무리로 흩어져 있다.
- `apply_limit(root, repository, identifier, limit, request_id)` (행 29–48): docstring: "`max_input_bytes`를 공개적으로 설정하고 새 프로필의 능력 증거를 기록한다." `root/<request_id>.json`에 `{"max_input_bytes": limit}`을 `canonical_json`으로 쓰고 `cli_result(root, "configure", ..., "--request-id", request_id)`로 공개 `configure`를 보낸다. 수락되지 않으면 `AssertionError`. 이어 `ResearchEngine(repository, identifier, runner=ScriptedRunner(), formal_verifier=formal_ok)`로 `process_controls()`를 해 설정을 적용한다. 설정이 새 프로필 판본을 만들므로, `maintenance` 역할의 AI 프로필마다 `capability_evidence(profile, FixtureAdapter().describe(), observed_at=runtime['last_observed_utc'])`를 계산해 `instance['capability_evidence']`에 넣고 `_save()`한다. 적용된 엔진을 돌려준다. `research_fixtures` docstring이 말하는 규칙("나중 `configure`는 새 능력 증거가 필요한 새 프로필 판본을 만든다")을 여기서 손으로 채운다. 쓰는 곳은 `overflowed_maintenance`와 클래스 도우미 `InputRecoveryPublicTests.apply_limit`다.
- `overflowed_maintenance(root, shared)` (행 51–69): `restore_template` 빌드. docstring: "첫 입력 초과로 붙잡힌 공개 유지보수 요청. 검증된 활성 상태에서 공개 `configure`가 `max_input_bytes`를 1로 두고, 공개 `request`가 유지보수를 대기열에 넣고, 엔진 한 단계가 그것을 붙잡는다. 인스턴스 ID를 돌려준다." 구현은 `state_fixtures.active_instance(root, shared, config=ACTIVE_CONFIG)`로 2단 상태를 같은 `root`에 만들고, `do_math.initialization.adapter_for`를 `FixtureAdapter`로 패치한 채 `apply_limit(..., 1, "UC-limit-small")`, `cli_result(... "request", "--role", "maintenance", "--reason", "Check the installed recovery boundary", "--request-id", "UC-maintenance")`, `ResearchEngine(..., runner=ScriptedRunner(), formal_verifier=formal_ok).run(max_steps=1)`을 차례로 한다. 2단 위에 쌓은 더 깊은 빌드다. `research_fixtures` docstring의 "What to use"가 이 빌드를 `test_input_recovery` 전용으로 적는다.
- 행 446–448: 직접 실행하면 `unittest`를 다시 import하고 `unittest.main()`.

## InputRecoveryPublicTests (행 72–202)

`unittest.TestCase`를 그대로 상속한다. 클래스 표지와 속성은 없다.

- `setUp` (행 73–74): `state_fixtures.start_active_copy(self)`. `do_math.initialization.adapter_for`를 `FixtureAdapter`로 바꾸는 패치를 시험 수명 동안 걸고, 2단 사본을 받아 `self.root`, `self.repo`, `self.identifier`를 둔다. 두 시험 모두 곧바로 `overflowed()`로 사본을 바꾸므로, `setUp`이 복원한 2단 사본 자체는 쓰이지 않고 어댑터 패치만 효력을 갖는다.
- `overflowed()` (행 76–79): docstring: "사본을 `overflowed_maintenance`의 상태로 바꾼다." `restore_template(overflowed_maintenance)`로 `self.root`, `self.identifier`를 다시 두고 `self.repo = root/"repository"`.
- `cli(*arguments)` (행 81–82): `cli_result(self.root, *arguments)`. 명령이 실패하거나 봉투 `exit_code`가 0이 아니면 `AssertionError`를 내고 `result`를 돌려준다.
- `instance_args(identifier)` (행 84–85): `("--repository", str(self.repo), "--instance", identifier)`.
- `apply_limit(identifier, limit, request_id)` (행 87–88): 모듈 함수 `apply_limit(self.root, self.repo, ...)`의 포장.

### `test_public_retry_replays_refails_resolves_and_rejects_after_close` (행 90–160)
- 성질: 공개 재시도는 같은 요청 ID로 재생되고, 한도가 그대로면 다시 실패해 새 질문을 열며, 한도를 올리면 해결되어 두 실패 기록을 보존하고, 인스턴스를 닫은 뒤에는 입력 오류로 거부된다.
- 준비: `overflowed()`. 복사된 상태는 첫 초과다(주석 행 94–95).
- 실행과 단언: 네 단계로 나뉜다.
  1. 첫 초과 확인: 엔진을 열어 `input_overflows`가 하나임을 단언한다(실패 메시지에 상태·대기열·대기·최근 기록 다섯 개를 싣는다). `waiting_actions`의 첫 항목에서 행동 ID와 질문 ID를 얻는다. 질문의 `origin_field == 'resolution_question/question'`이고 `origin_execution_id`가 있다. 공개 `status --json`의 `question_links`에서 같은 질문의 `text`가 대기 세부의 `resolution_question.question`과 같고, 공개 질문에 `source_status` 키가 없다.
  2. 같은 한도의 재시도: `request --retry-action <행동> --request-id UC-retry-same-limit`을 두 번 보낸다. 첫째 `accepted`, 둘째 `replayed`가 참이다. 엔진을 `run(max_steps=1)`로 한 단계 돌린다. `input_overflows`가 둘, 기록에서 `input_overflow_retry_started`이고 `request_id == 'UC-retry-same-limit'`인 항목이 정확히 하나, `input_overflow_retry_failed` 항목이 있다. 첫 질문은 `resolved`, 행동은 새 질문으로 다시 붙잡혔고 그 질문은 `open`이다.
  3. 큰 한도의 재시도: `apply_limit(..., 3_000_000, 'UC-limit-large')`로 한도를 올리고 그때의 `maintenance` 프로필 참조를 떠 둔다. `--request-id UC-retry-large`로 재시도(수락 단언)하고 한 단계 돌린다. 행동이 대기에서 빠지고, 둘째 질문이 `resolved`다. `input_overflow_retry_resolved` 기록의 `profile_ref`가 떠 둔 참조 가운데 하나이고 `prompt_bytes <= limit_bytes`다. `input_overflows`는 여전히 둘이다(메시지: 성공한 수락은 두 과거 실패를 보존해야 한다).
  4. 닫은 뒤: 공개 `close`를 보내고 `process_controls()`로 적용한다. 이어 `run_cli`로 `--request-id UC-retry-closed` 재시도를 보내면 반환 코드 2이고 오류 `message`에 `'closed/completed'`가 있다(메시지 조각 고정). 다시 연 엔진의 `status == 'closed'`, 대기열이 비어 있다.
- 단언: 위 네 단계에 적은 것을 요약하면 다음과 같다. 첫 초과는 실패 기록 하나와 공개 질문을 남긴다. 같은 한도의 재시도는 재생되고, 재시도 시작 기록이 한 번, 실패 기록이 더해지며, 옛 질문이 닫히고 새 질문이 열린다. 큰 한도의 재시도는 행동을 풀고 둘째 질문을 닫으며, 해결 기록의 프로필이 현재 프로필이고 두 실패 기록이 보존된다. 닫힌 인스턴스의 재시도는 반환 코드 2와 메시지 조각 `'closed/completed'`로 거부되고 대기열이 비어 있다.
- 대역: `ScriptedRunner`(러너 자리, 이 시험에서 모델 출력은 단언하지 않는다), `formal_ok`, `adapter_for` 패치(`setUp`).
- 비고: 엔진은 매 단계 새로 연다. CLI는 모두 프로세스 안의 `run_cli`다. `ScriptedRunner.run`은 `research_fixtures.local_job_runner`로 장식되어 있어, 모델 호출이 실제로 시작되는 단계(3단계의 해결된 재시도)에서는 실제 Windows Job 자식 프로세스(`python -c "import time; time.sleep(600)"`)를 띄우고 호출이 끝나면 종료한다. 종료 확인의 대기 상한은 10초다. 이 시험에는 `resource` 표지가 없다.

### `test_resolved_retry_marker_survives_provider_deferral_and_repreparation` (행 162–202)
- 성질: 해결된 재시도 표지는 공급자 수락이 미뤄져 행동이 다시 준비되어도 유지되며, 질문의 해결 참조와 이력이 바뀌지 않고 해결 기록이 한 번만 남는다.
- 준비: `overflowed()`. 붙잡힌 행동 ID와 질문 ID를 얻는다. `apply_limit(..., 3_000_000, 'UC-marker-limit-large')`와 `request --retry-action ... --request-id UC-marker-retry`.
- 실행: (1) 새 엔진에서 `_provider_admit`을 지역 함수 `defer`로 바꿔 `run(max_steps=1)`. `defer`는 행동에 `dispatch_wait = {'kind': 'capacity', 'provider': 'test-double', 'next_owner': 'scheduler'}`를 달고 `False`를 돌려준다. (2) 또 새 엔진을 열어 대역 없이 `run(max_steps=1)`.
- 단언: (1) 뒤 질문의 `resolution_history`와 `resolution_ref`를 떠 두고, 대기열의 그 행동의 `input_overflow_retry.state == 'resolved'`. (2) 뒤 질문의 `resolution_ref`와 `resolution_history`가 떠 둔 것과 같다. 기록에서 `input_overflow_retry_resolved`이고 `request_id == 'UC-marker-retry'`인 항목이 정확히 하나다. 그 행동의 실행 가운데 `outcome == 'start_failed'`, `result_disposition.kind == 'capacity'`이고 전이 사유에 `'provider admission deferred'`가 있는 것이 있고, `outcome == 'output_accepted'`인 것도 있다.
- 대역: `patch.object(engine, '_provider_admit', side_effect=defer)`, `ScriptedRunner`, `formal_ok`, `adapter_for` 패치.
- 비고: 둘째 단계의 실제 모델 호출은 `ScriptedRunner`의 `local_job_runner`를 거쳐 실제 Windows Job 자식 프로세스를 띄운다.

## InputRecoveryMarkerUnitTests (행 205–229)

`unittest.TestCase`를 그대로 상속한다. 표지·훅·도우미·클래스 속성이 없다.

### `test_only_explicit_pending_retry_marker_is_active` (행 206–215)
- 성질: 재시도 표지는 상태가 명시적으로 `pending`일 때만 활성이다. 상태가 없는 옛 표지, `resolved`, `failed`는 활성이 아니다.
- 준비: 1단. 행동 사전 넷: `state='pending'`, 상태 없음(`legacy_pending`), `'resolved'`, `'failed'`.
- 실행: `ResearchEngine._pending_input_overflow_retry(action)`를 클래스에서 직접 부른다.
- 단언: `pending`만 `None`이 아니고 나머지 셋은 `None`이다.
- 대역: 없음.

### `test_preexisting_user_resolution_is_preserved_when_retry_input_fits` (행 217–229)
- 성질: 재시도 입력이 맞아 질문을 해결하려 할 때, 그 질문이 이미 사용자 결정으로 해결되어 있으면 기존 해결 참조와 이력을 덮어쓰지 않는다.
- 준비: `bare_engine(runtime=...)`. 질문 `QU-overflow`가 `status='resolved'`, `resolution_ref='DE-user'`, 이력 `[{'resolution_ref': 'DE-user', 'affected_ids': ['AC-held']}]`.
- 실행: `engine._resolve_input_overflow_question('QU-overflow', execution_id='EX-retry', kind='input_overflow_retry_resolved', evidence={'action_id': 'AC-held'})`.
- 단언: 반환값이 `'already_resolved'`, 질문의 `resolution_ref`가 `'DE-user'`, 이력이 원래와 같다.
- 대역: `bare_engine`(저장소 없는 엔진).

## OverflowConnections (행 232–359)

`unittest.TestCase`를 그대로 상속한다. 표지·설정 훅·클래스 속성은 없고, 시험마다 도우미 `fixture`로 새 엔진을 만든다.

- `fixture()` (행 233–269): `(engine, 큰 프로필 참조)`를 돌려준다. 단계는 다음과 같다.
  1. `record_fixtures.approved_task()`의 과제 `TK-1`(비형식 과제, 원천 `SO-1`, 허가 `GR-1`)과 상태로 `engine_fixtures.context_engine(instance, runtime)`을 만든다. 이 엔진은 실제 문맥 생산자를 유지하고, 저장소를 `ResearchRepository`의 `create_autospec` 대역으로, 호스트 관찰과 무관한 메서드(`_preparation_checkpoint`, `_session_slots`, `_academic_status`, `_planning_history`, `_execution_profile` 등)를 대역으로 바꾼 `bare_engine`이다.
  2. `build_profiles(config)`로 프로필을 만들어 인스턴스에 싣고, 저장소 대역의 `read`가 `b'source'`를 돌려주게 하며 원천 `SO-1`의 해시를 그 바이트의 SHA-256으로 맞춘다.
  3. `research_work`의 첫 프로필을 `small`로, 그 `max_input_bytes`를 두 배로 늘려 봉인한 것을 `large`로 두고 `large`를 인스턴스에 넣는다. 과제의 `profile_refs`를 두 참조로, `status`를 `active`로 두고 `approve_task`로 다시 승인한다.
  4. 행동 `AC-held`(`research_work`, 소유 활동 `AY-held`, 허가 `GR-1`, `selected_contract_sha256 = contract_hash(task)`, 프로필 `small`, 모델 평가 `low`/`low`/`'Bounded work'`)를 만든다. `activities.open_activity`로 `AY-held`를 열고 `wait_for(..., reason='input_overflow', next_owner='research_plan')`로 대기시킨다. `waiting_actions['AC-held']`를 `input_overflow` 대기(질문 `QU-held`, 세부 `allowed_profile_candidates=[large['id']]`, `cause='required_role_input'`, `packed_bytes = small 한도 + 10`)로 둔다.
  5. `conversation_loss_policy='continue_authorized'`, `_require_action_clock`을 고정 시각 `'2026-09-23T00:00:00+00:00'`의 대역으로 두고, `context_engine`이 예외 대역으로 바꿔 둔 `_execution_profile`을 실제 메서드(`ResearchEngine._execution_profile.__get__(engine)`)로 되돌린다.

  시작 상태는 메모리 엔진 대역이다. 저장소가 없으므로 Git과 프로세스를 쓰지 않는다. `engine_fixtures.package(engine, root)`는 `research_plan` 행동 `AC-plan`의 실제 문맥을 만들고 `prepare_role_input`으로 역할 입력을 `root`에 포장한 뒤, `(포장 결과, root/input/submission/context.json의 고정 문맥)`을 돌려준다.

### `test_overflow_choices_are_supplied_without_changing_ready_population` (행 271–279)
- 성질: 붙잡힌 행동과 허용 프로필 후보가 연구 계획 실행의 문맥에 공급되며, 그 행동이 준비된 과제 목록에 끼어들지 않는다.
- 준비: 클래스 `fixture`.
- 실행: 임시 디렉터리에 `package(engine, dir)`.
- 단언: 고정 문맥의 `ready_task_ids == []`. 포장 문맥의 `input_overflow_requests[0]`가 `action_id='AC-held'`, `owner_activity_id='AY-held'`, `allowed_profile_refs=[큰 프로필 참조]`다.
- 대역: `context_engine`의 대역.

### `test_planner_extension_accepts_exact_choice_and_requeues_same_obligation` (행 281–297)
- 성질: 계획자 확장의 정확한 선택은 스키마를 통과하고, 적용되면 같은 행동(같은 소유 활동, 같은 모델 평가)을 고른 프로필과 대기 중 재시도 표지로 대기열에 되돌리며 대기를 푼다.
- 준비: 클래스 `fixture`. 선택 `{'action_id': 'AC-held', 'profile_ref': 큰 참조, 'reason': 'Required evidence fits'}`.
- 실행: `jsonschema.validate({'input_overflow_resolutions': [choice]}, submission.extension_schema({'role': 'research_plan'}))`, `package`로 고정 문맥을 얻은 뒤 `engine._apply_input_overflow_resolutions([choice], fixed, 'EX-plan')`.
- 단언: 스키마 검증이 예외 없이 끝난다. 대기열의 `AC-held`가 `owner_activity_id='AY-held'`, `profile_ref=큰 참조`, `model_assessment.difficulty='low'`, `input_overflow_retry.request_id='EX-plan'`, `input_overflow_retry.state='pending'`이다. `waiting_actions`에 `AC-held`가 없다.
- 대역: `context_engine`의 대역.

### `test_stale_contract_or_unoffered_profile_cannot_release_wait` (행 299–315)
- 성질: 과제 계약이 바뀌었거나, 제공되지 않은 프로필을 골랐거나, 대기의 질문이 바뀌었거나, 대기 행동의 역할이 다르면 계획자의 선택은 대기를 풀지 못한다.
- 준비: `subTest`마다 새 `fixture()`와 `package`의 고정 문맥, 그리고 변형 하나.
- 실행: `_apply_input_overflow_resolutions([choice], fixed, 'EX-plan')`.
- 단언: `ValueError`(유형만). `AC-held`가 여전히 `waiting_actions`에 있다.
- 대역: `context_engine`의 대역.
- 비고: `subTest` 케이스 `mutation`은 넷이다. `'contract'`: 과제 `TK-1`의 `revision`을 1 올린다(포장 뒤에 바꾸므로 고정 문맥과 현재 계약이 어긋난다). `'profile'`: 선택의 프로필을 `research_plan`의 첫 프로필로. `'question'`: 대기의 `question_id`를 `'QU-new-failure'`로. `'review'`: 대기 행동의 `role`을 `'identity_review'`로. 이름은 "stale contract or unoffered profile"만 말하지만 질문과 역할 변형도 포함한다.

### `test_shared_submission_check_rejects_duplicate_and_unoffered_choices` (행 317–336)
- 성질: 제출 검사(`payload_issues`)가 계획자 확장의 선택을 검증해, 중복 선택, 제공되지 않은 프로필, 알 수 없는 행동을 문제로 보고하고 올바른 선택은 통과시킨다.
- 준비: 클래스 `fixture`와 `package`의 고정 문맥.
- 실행: 네 방식(`'valid'`, `'duplicate'`, `'profile'`, `'unknown'`)마다 `root/activity-extensions.json`에 확장을 쓰고, `runner_fixtures.common('research_plan')` 출력을 `research_fixtures.seal_response(output, fixed, root)`로 봉인한 뒤 `submission.payload_issues(output, contracts.schema_for('research_plan'), fixed, extensions, root)`.
- 단언: 문제 목록이 비어 있는지가 `mode != 'valid'`와 맞는다(실패 메시지에 방식과 문제 목록을 싣는다). 문제의 내용은 고정하지 않는다.
- 대역: `context_engine`의 대역.
- 비고: `subTest`를 쓰지 않는 반복이다. `'duplicate'`는 같은 행을 두 번, `'profile'`은 `research_plan` 프로필, `'unknown'`은 `action_id='AC-unknown'`이다. 이름의 "shared"는 제품 `payload_issues`의 docstring "Shared producer/receiver entry point"(`submission.py` 행 1009), 곧 생산자와 수신자가 같은 검사 입구를 쓴다는 뜻이다. 이 시험은 그 입구를 한 번씩 직접 부를 뿐, 생산자 쪽과 수신자 쪽 경로를 따로 지나지는 않는다.

### `test_same_integration_receipt_prevents_duplicate_retry` (행 338–359)
- 성질: 같은 실행의 같은 통합 묶음을 다시 적용하면 통합 영수증 때문에 `already_accepted`가 되어, 재시도 행동이 두 번 대기열에 들어가지 않는다.
- 준비: 클래스 `fixture`와 `package`의 고정 문맥. 확장은 올바른 선택 하나. 콜백 `apply`는 묶음의 `integration_id`를 `calls`에 적고, 넘겨받은 인스턴스·런타임을 엔진에 실은 뒤 `_apply_input_overflow_resolutions`를 부른다. 나머지 콜백(`validate_candidate`, `validate_current`, `publish`)은 아무것도 하지 않는다.
- 실행: `integration.apply_bundles(instance, runtime, common('research_plan'), extension, fixed, execution_id='EX-plan', **callbacks)`를 한 번, 그 결과 상태로 한 번 더.
- 단언: 첫 결과 `status == 'accepted'`(실패 메시지에 `issues`). 둘째 결과의 첫 묶음 `status == 'already_accepted'`. `apply` 콜백이 한 번만 불렸다. 둘째 결과의 대기열에 `AC-held`가 하나다.
- 대역: `context_engine`의 대역과 통합 콜백 대역.

## OverflowGitConnection (행 362–443)

`unittest.TestCase`를 그대로 상속한다. 표지·훅·도우미·클래스 속성이 없다. 유일한 시험이 시작에서 `start_active_copy(self)`를 직접 부른다.

### `test_plan_choice_repackages_original_work_and_reaches_runner` (행 363–443)
- 성질: Git 인스턴스에서 입력 초과로 붙잡힌 원래 작업은 계획자가 고른 큰 프로필로 다시 포장되어 같은 소유 활동으로 러너에 도달하고, 해결 질문이 닫히며, 두 번의 시도가 서로 다른 실행으로 남는다.
- 준비: 2단(`start_active_copy`). 지역 러너 클래스 `Runner`의 `run`은 `research_fixtures.local_job_runner`로 감싸져 있으며, 프롬프트에서 `context_from`으로 문맥을 읽어 행동 사본을 `calls`에 적는다. 역할이 `research_plan`이면 문맥의 첫 `input_overflow_requests` 행에 대해 첫 허용 프로필을 고르는 확장을 작업공간의 `activity-extensions.json`에 쓴다. `research_work`이면 `outcome='submitted'`와 보고를 담은 출력을 낸다. 다른 역할이면 `AssertionError('Unexpected role: ...')`를 던진다. 매번 `on_started`를 부르고 `producer_result`로 완료 결과를 돌려준다. 엔진은 `ResearchEngine(repo, identifier, runner=Runner())`. `research_work`의 마지막 프로필을 바탕으로 `max_input_bytes=2000000`인 `large`와 `500000`인 `small`을 봉인해 인스턴스에 넣고(관찰 설정 `tool_review_window_seconds=60`, `self_check_response_window_seconds=5`), 둘의 능력 증거를 `FixtureAdapter().describe()`로 기록한다. 과제는 `task_contract()`를 바탕으로 `status='active'`, 허가 `GR-research`, 프로필 `[small, large]`, 모델 평가 `high`/`high`로 두고, 질문을 `'Inspect the following fixed evidence: ' + 'required evidence ' * 40000`(약 72만 바이트로 `small`보다 크고 `large`보다 작다)으로 채운다. `supply_observation_rules`로 초기 관찰 규칙을 채우고 `approve_task`로 승인한다. 행동 `AC-overflow-work`(프로필 `small`)를 대기열에 넣고 `_save()`한다.
- 실행: `engine.run(max_steps=1)`을 세 번.
- 단언: 첫 단계 뒤 러너 호출이 없고, 행동이 `waiting_actions`에 `next_owner == 'research_plan'`으로 붙잡혔다. 소유 활동 ID와 질문 ID를 떠 둔다. 둘째 단계 뒤 호출 역할이 `['research_plan']`이고, 대기열의 그 행동이 `profile_ref = large 참조`, 같은 소유 활동이며, 질문은 아직 `open`이다. 셋째 단계 뒤 호출 역할이 `['research_plan', 'research_work']`이고, 마지막 호출 행동의 `profile_ref`와 `owner_activity_id`가 `large`와 떠 둔 활동이며, 질문이 `resolved`다. 그 행동의 실행이 둘이고 ID가 서로 다르며, 하나는 `outcome == 'output_accepted'`다.
- 대역: 지역 `Runner`(`local_job_runner` 장식), `adapter_for` 패치(`start_active_copy`).
- 비고: `local_job_runner`는 러너 호출마다 실제 Windows Job 자식 프로세스를 띄우고 끝나면 종료한다(대기 상한 10초). 이 시험에서는 호출이 두 번이다. 둘째 단계 뒤 질문이 아직 `open`이라는 단언은 계획자의 선택만으로는 질문이 닫히지 않고, 다시 포장된 입력이 실제로 맞았을 때 닫힌다는 순서를 고정한다.

## 관계

- 같은 제품 기능을 다른 층에서 검사하는 모듈: 역할 입력의 포장과 크기 측정은 `test_role_input`이, 공개 `request --retry-action`의 수락·재생만은 `test_cli`가, 공급자 수락 미룸과 대기는 `test_provider_recovery`가 다룬다. 통합 묶음(`integration.apply_bundles`)과 제출 검사(`payload_issues`)는 제출 경계 모듈들이 일반적으로 다루고, 이 모듈은 입력 초과 확장에 한정해 본다.
- 픽스처 의존: `state_fixtures.active_instance`(빌드의 바탕), `start_active_copy`(`setUp`, `OverflowGitConnection`); `research_fixtures.restore_template`, `cli_result`, `run_cli`(공개 CLI), `FixtureAdapter`(능력 증거), `bare_engine`, `seal_response`, `local_job_runner`, `producer_result`, `supply_observation_rules`; `engine_fixtures.context_engine`, `package`; `runner_fixtures.ScriptedRunner`, `formal_ok`, `common`, `context_from`; `record_fixtures.approved_task`, `approve_task`, `task_contract`.
- 이 모듈에만 있는 도우미: 모듈 함수 `apply_limit`, 빌드 `overflowed_maintenance`, 클래스 도우미 `overflowed`, `cli`, `instance_args`, `apply_limit`(포장), `fixture`.
- 겹침과 보완: 공개 재시도 경로(`InputRecoveryPublicTests`)와 계획자 선택 경로(`OverflowConnections`, `OverflowGitConnection`)가 입력 초과를 푸는 두 길을 나눠 맡는다. 재시도 표지의 의미는 공개 흐름(`test_resolved_retry_marker_survives_provider_deferral_and_repreparation`)과 단위(`InputRecoveryMarkerUnitTests`)에서 짝으로 확인한다. 계획자 선택은 메모리 엔진에서 검증 분기 하나씩을, Git 인스턴스에서 끝까지의 흐름을 본다.
