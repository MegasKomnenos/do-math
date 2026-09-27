# 결과 — ENG(엔진) 그룹

기준은 worktree `C:/math-worktrees/c-eng`의 브랜치 `c-eng`이다. 경로는 따로 적지 않으면 `.claude/skills/do-math/scripts/` 기준 상대 경로다. 행 번호는 커밋 `78f00bb`의 원문 좌표다.

## 1. 브랜치, 커밋, 바꾼 파일

- 브랜치: `c-eng`(시작: `c-int`의 `09991b9`)
- 마지막 커밋: `78f00bb` "do-math 정리 ENG: 엔진 구조 정리와 엔진 후보 구현"
- 제품(12): `do_math/engine.py`, `do_math/lifecycle_engine.py`, `do_math/reporting.py`, `do_math/question_engine.py`, `do_math/cli.py`, `do_math/submission.py`, `do_math/repository.py`, `do_math/configuration.py`, `do_math/control_contracts.py`, `do_math/governance_engine.py`, `do_math/initialization.py`, `do_math/scheduler.py`
- 시험(16): `tests/research_fixtures.py`, `tests/state_fixtures.py`, `tests/test_cli.py`, `tests/test_connection_repairs.py`, `tests/test_decision_basis.py`, `tests/test_efficiency.py`, `tests/test_knowledge_import_engine.py`, `tests/test_lifecycle_engine.py`, `tests/test_performance_repairs.py`, `tests/test_query_records.py`, `tests/test_questions.py`, `tests/test_redesign_CONTRACTS.py`, `tests/test_redesign_ENGINE.py`, `tests/test_redesign_PROFILES.py`, `tests/test_redesign_SURFACE.py`, `tests/test_submission_tools.py`
- 문서(1): `이음새-정본.md`(6절 표에 4행 추가). 스킬 문서와 `AGENTS.md`는 고치지 않았다.

## 2. ID별 처분

담당 20건 모두 `구현함`이다. 파견문이 붙인 영역 밖 관찰 4건은 이 절 끝에 따로 적는다.

| ID | 처분 | 내용과 좌표 |
|---|---|---|
| ENG-01 | 구현함 | 보호 키 집합을 `control_contracts.USER_DECISION_SETTINGS`(5키, `host_resources` 포함) 하나로 두었다. `engine.control`(`engine.py:263-264`, `.get` 비교)과 `governance_engine._configure_candidate`(`governance_engine.py:52-53`, `:102`)가 이것을 쓴다. 운영자의 `host_resources` 변경은 이제 접수에서 거부된다. |
| ENG-02 | 구현함 | `_call_steps`의 실행 기록에서 `"effort": config["effort"]`를 지웠다(`engine.py:3147` 부근). 실행 effort는 `_register_execution`이 프로필에서 정한 값 하나다. |
| ENG-03 | 구현함 | status 투영을 `reporting.status_report`(`reporting.py:151-226`) 하나로 모았다. `engine.status`(`engine.py:1399-1409`)는 현재 head를 적재하고 호스트 관측값만 모아 넘기는 얇은 층이며, 쓰이지 않던 `snapshot` 인자를 지웠다. `snapshot_report`는 같은 함수를 부른다. 호스트에서 조회 순간에 관측하는 필드는 `reporting.OBSERVED_FIELDS`(`research_observed_at`, `research_wake_reasons`, `operation_progress`, `pending_controls`, `budget`, `provider_waits`)이고, `--snapshot`에서는 호출자가 넘기지 않으면 None이다. 사람용 출력은 `reporting.render_human_report` 하나로 합치고 `cli._human_status`를 지웠다. |
| ENG-16 | 구현함 | status의 `research_effectiveness`, `budget_observed_at`, `question_scope`, check의 `research_effectiveness`, reporting 쪽 `research_effectiveness` 사본과 사람용 출력의 "research effectiveness: not evaluated" 줄을 지웠다. |
| ENG-04 | 구현함 | 부적격 분기를 `submission.preview_submission`으로 옮겼다(`submission.py:1237-1262`). 봉인 check가 `capture_eligible=False`이면 후보를 적용하지 않고 같은 응답 골격(`check_id`, `schema_ref`, `input_hashes` 포함)을 돌려준다. 엔진은 부적격이면 `output.json`을 해석하지 않고 None을 넘긴다(`engine.py:2168-2172`). 계약 문자열은 `submission.PREVIEW_CONTRACT_ID` 하나이며 시험 2건이 이것을 쓴다. |
| ENG-05 | 구현함 | 결박을 `_external_control(..., academic_binding=)`의 키워드 인자로 넘긴다(`lifecycle_engine.py:732-757`). 엔진의 `_validate_external` 재정의, 사후 대입, 속성 저장·복원을 지웠다. 통합표가 예로 든 `config["academic_binding"]`을 쓰지 않은 이유는 7절에 적는다. |
| ENG-06 | 구현함 | `cycles`, `processed_controls`, `reservations`, `provider_waits`, `updated_at`을 `initialization.initialize_state`(`initialization.py:257-258`)로 옮기고 `engine.initialize`의 재대입(`grants`, `question_links` 포함)과 `CONTRACT` 별칭을 지웠다. `tests/test_query_records.py`는 별칭을 import만 하고 쓰지 않아 import를 지웠다. |
| ENG-07 | 구현함 | 공개 가족 이름을 `planning.RECORD_FAMILIES`의 역표에서 파생한다(`engine.py:334-345`, `_QUERY_FAMILIES`). 표에 없는 `question_links`만 `question`으로 둔다. `formal_results`는 `formal-result`, `execution_profiles`는 `execution-profile` 등으로 바뀐다. |
| ENG-08 | 구현함 | 형식 검사(`_formal`, `_formal_steps`)를 `lifecycle_engine.py:1477-1649`로 옮겼다. 두 Lean 기계 실행이 공유하는 골격은 `_lean_machine_call`(인자 조립, 시작 전 정지, 호출), `_preserve_machine_return`(반환 원문 보존), `_release_machine_execution`, `_end_machine_execution`(종료 처리 하나)이다(`lifecycle_engine.py:1122-1170`). 보존한 차이와 배치 판단은 7절에 적는다. 엔진에는 형식 검사 코드가 남지 않는다. |
| ENG-11 | 구현함 | `_controls`를 `_apply_inbox`(펌프 포함, inbox 적용)와 `_upkeep`(주기 정리 여덟 가지와 피드백 재전달)으로 나눴다(`engine.py:782-929`). `_controls`는 둘을 차례로 부르는 합성이다. 입력 준비의 두 호출(`engine.py:3018`, `:3044`)과 외부 전송 정지 판정(`lifecycle_engine.py:1347`)은 `_apply_inbox`만 부른다. 소유 루프, `run` 시작, `process_controls`, 호출 종료는 `_controls`를 부른다. |
| ENG-14 | 구현함 | 생성자와 `process_controls`의 `ensure_ontology` 호출을 지웠다. `initialize`의 호출은 남는다. |
| ENG-15 | 구현함 | `_observe_running`(`engine.py:2625-2729`)은 관찰과 스트림 변화를 tracker 사본에서 먼저 계산한다. 쓸 것(검토 관찰 행, 관찰 결과, 스트림 변화, 의무 변화)이 없으면 runtime 사본도 게시도 없이 tracker만 반영하고 끝난다. |
| ENG-17 | 구현함 | 네 곳을 지웠다: `retry.pop("after_stop")`, `execution.pop("activity_id")`, `deadline_only` 분기, `run` 시작의 `recovery_checked = True`. |
| ENG-19 | 구현함 | `_CONTROL_READERS`, `_CONTROL_READER_LIMIT`, `_control_reader`, `OrderedDict` import와 시험 `test_control_reuses_one_reader_per_repository_and_instance`를 지웠다. `control()`은 `ResearchRepository`를 직접 만든다. |
| ENG-20 | 구현함 | 붙잡을 head 집합을 `ResearchRepository.save_with_state(..., retain=)`로 넘기고 저장소가 `retain_reads`를 부른다(`repository.py:408-419`). `_save`의 `git_dir` 형 검사와 `_evaluation_context_for`의 `getattr`을 지우고 `store.git_dir`을 직접 읽는다. 시험 대역 `StateStore`는 `git_dir = None`과 `retain` 인자를 가진다. `bare_engine`은 store를 주지 않으면 `StateStore`를 쓴다. |
| ENG-21 | 구현함 | `_feedback_delivered`, `_retrying_publication`, `_next_lean_discovery`·`_lean_found`, `_goal_audit_contract`를 `_init_process_state`(`engine.py:439-444`)에서 초기화하고 직접 접근한다. `_external_preparation_binding`은 ENG-05로 사라졌다. |
| ENG-22 | 구현함 | `_read_extensions`를 지우고 `submission.read_extensions`를 부른다. 사용자 제어 요청 조회 3곳은 `_user_control_request(runtime, request_id)`(`engine.py:195-198`)로, 미종료 action ID 집합 3곳은 `_live_action_ids()`(`engine.py:3418-3420`)로 모았다. `_control_result`의 조회는 통합표 정정대로 다른 규칙이라 두었다. 형식 검사의 `reference` 이중 대입이 사라졌고, `proposal.lean`은 형식 묶음 한 곳에 한 번 저장한다(7절). `(snapshot, path)` 람다 8곳은 이미 없다: `grep "lambda snapshot, path"` 0건이며, `이음새-정본.md` 6절 `read_artifact(path, snapshot)` 행이 커널에서 인자 순서를 통일했다. |
| ENG-23 | 구현함 | docstring 첫 줄을 "observable provider CLI executions (Codex, Claude)"로 고쳤다. 같은 docstring의 낡은 `do-math-state/6`도 `state_contract.STATE_CONTRACT_ID`를 가리키도록 고쳤다. |
| HIS-02 | 구현함 | 아래 좌표 표를 본다. 믹스인 직접 인스턴스 6곳(`tests/test_decision_basis.py` 2곳, `tests/test_questions.py` 4곳)은 `research_fixtures.bare_engine`으로 옮겼다. |
| HIS-08 | 구현함 | 코드는 바꾸지 않았다. `engine._recover_disappeared`의 queued·예약 없음 분기(`engine.py:1495-1496`)에 판정과 이유를 한 문장으로 적었다. |

HIS-02에서 처리한 좌표(원 검토 좌표 → 현재 좌표)는 다음과 같다. RUN 그룹은 이 좌표를 다시 다루지 않는다.

| 대상 | 처리 |
|---|---|
| `engine.py` `_feedback_delivered`, `_retrying_publication`, `_next_lean_discovery`, `_goal_audit_contract`, `_external_preparation_binding` 2곳 | 초기화 이동 또는 삭제(ENG-21·ENG-05) |
| `lifecycle_engine.py` `_clock_guard`의 `_clock_failure`(원 89행, 현재 111행) | `_init_process_state`에서 None으로 초기화, 직접 접근 |
| `lifecycle_engine.py` `_activate_initialization`·`_complete_initial_intent`의 `_governance_owner_handlers` 방어(원 172·341행, 현재 194·363행) | 직접 호출 |
| `lifecycle_engine.py` `_external_control`의 결박 속성·`hasattr(_solution_basis)`·`getattr(_academic_evidence)`(원 725·730·732행) | 키워드 인자와 직접 호출 |
| `lifecycle_engine.py` `_external_prerequisite`의 `hasattr`·`getattr`(원 811·813행, 현재 836-837행) | 직접 호출 |
| `scheduler.py` `_goal_basis_key_at_head`의 `_goal_basis_memo`(46행) | `_init_process_state`에서 None으로 초기화, 직접 접근 |

RUN-09 가운데 HIS-02와 겹치지 않는 `lifecycle_engine.py:61`(`lifecycle_clock`)과 `:79`(`lifecycle_monotonic`)의 `getattr`은 처리하지 않았다. RUN-09의 몫이다.

영역 밖 관찰 4건의 처분:

- **`_register_execution`의 프로필 재선택**: `_register_execution(action, execution, *, profile=None)`으로 호출자가 이미 고른 프로필을 받는다(`engine.py:535-543`). AI 경로(`_call_steps`)와 형식 검사는 자기 선택을 넘긴다. 신뢰 검사·외부 작업·신뢰 활성은 넘길 프로필 변수가 없어 지금처럼 등록 안에서 고른다. RUN-03이 관문의 프로필을 반환하게 하면 그 값을 넘길 수 있다.
- **AI·형식 검사 시작의 관문 재통과**: `_call_steps` 첫머리와 `_formal_steps`의 `_action_lifecycle_gate`를 지웠다. 같은 소유 루프 바퀴에서 `_dispatchable`이 통과시킨 관문이 시작 전 마지막 관문이며, 두 호출 사이에 상태를 바꾸는 사건이 없다. 시작 뒤의 권한·정지 재확인(`_call_steps`의 `governance.authorize`, `_execution_stop_requested`, head 비교, 형식 검사의 `authorize`와 `stop()`)은 그대로다. 두 함수의 docstring에 이 전제를 적었다. 시험 도우미 `state_fixtures.start_model_call`은 스케줄러처럼 관문을 먼저 통과시킨다.
- **`control_receipts` 선형 조회**: 조회 비용은 줄이지 않았다. 측정 결과 영수증 2,000개 선형 조회는 0.095ms였고, 같은 `_publish_control_request`가 요청마다 하는 instance·runtime 전체 deepcopy는 영수증 2,000개만으로도 26.7ms였다. 색인은 새 상태와 수명 규칙을 더하면서 요청 비용을 0.4% 미만 줄인다. 전역 ID 유일성 판정은 바꾸지 않았다.
- **설정 검사 오류 문구**: `configuration.validate_config`의 문구를 `configuration has fields outside the stored configuration section: <키 목록>`으로 고치고 `RESPONSE_CONTRACT_ID` import를 지웠다. 이 문구를 단언하던 `tests/test_redesign_PROFILES.py:120`을 새 문구와 키로 고쳤다.

## 3. 새 공유 정의와 지운 공개 이름

`이음새-정본.md` 6절 표에 행을 더한 새 공유 정의는 다음 넷이다.

| 정본 | 위치 | 쓰는 곳 |
|---|---|---|
| `USER_DECISION_SETTINGS` | `control_contracts.py` | `engine.control`, `governance_engine._configure_candidate` |
| `status_report(store, head, instance, runtime, *, observation, requested_areas)`, `OBSERVED_FIELDS` | `reporting.py` | `engine.status`, `reporting.snapshot_report`, 시험 |
| `question_view(instance, runtime, read_many)`, `user_questions(view)` | `question_engine.py` | `QuestionEngineMixin`, `reporting.status_report` |
| `ResearchRepository.save_with_state(..., retain=heads)` | `repository.py` | `engine._save` |

모듈 안에서만 쓰는 새 이름은 표에 올리지 않았다: `submission.PREVIEW_CONTRACT_ID`(제품 쓰는 곳 하나, 시험이 import), `engine._user_control_request`, `ResearchEngine._live_action_ids`·`_apply_inbox`·`_upkeep`, `LifecycleEngineMixin._lean_machine_call`·`_preserve_machine_return`·`_release_machine_execution`.

지운 이름: `engine.CONTRACT`, `engine._CONTROL_READERS`, `engine._CONTROL_READER_LIMIT`, `engine._control_reader`, `ResearchEngine._read_extensions`, `ResearchEngine._validate_external`(재정의), `cli._human_status`. `ResearchEngine._formal`·`_formal_steps`는 `LifecycleEngineMixin`으로 옮겼고 같은 이름으로 엔진에서 부를 수 있다. `ResearchEngine.status`는 `snapshot` 인자를 잃었다. 옛 이름 grep(`_CONTROL_READER`, `_control_reader`, `_read_extensions`, `_external_preparation_binding`, `_human_status`, `research_effectiveness`, `budget_observed_at`, `import CONTRACT`)은 스킬 폴더와 `AGENTS.md`에서 0건이다.

## 4. 필요한 문서 변경

| 문서와 절 | 바꿀 내용 |
|---|---|
| `references/초기화-운전.md:169`, `:174` | `query --kind execution_profiles`를 `query --kind execution-profile`로 바꾼다. 같은 절의 `capability_evidence`(:212), `intent_imports`(:305, :331)는 조건 문법에 없는 가족이라 그대로다. |
| `references/CLI-실행-계약.md` record `query` 절(:636-646) | 결과 `record.family`와 `--kind`의 가족 이름이 조건 문법 가족 이름(`planning.RECORD_FAMILIES`)이며, 그 표에 없는 가족은 저장 이름이고 질문 행은 `question`이라는 규칙을 한 문장으로 적는다. |
| `README.md` status 필드 표(:233-248)와 :508 | `status --snapshot OID --json`도 현재 status와 같은 필드를 가지며, 호스트에서 조회 순간에 관측하는 필드(`research_observed_at`, `research_wake_reasons`, `operation_progress`, `pending_controls`, `budget`, `provider_waits`)는 과거 snapshot에서 null이라는 점을 적는다. 표의 `pending_controls` 행에 현재 조회에서만 값이 있다는 조건을 붙인다. `host_observation` 필드와 `research_effectiveness`는 더 이상 없다(현재 문서에 언급은 없다). |
| `README.md` :487 부근 | 사람용 status 텍스트는 현재 조회와 `--snapshot`이 같은 렌더러 하나를 쓰며 관측하지 않은 필드는 `not observed`로 적는다는 점을 필요하면 더한다. |
| `references/CLI-실행-계약.md` configure 설명(:254) | 운영자 출처 configure가 바꿀 수 없는 설정에 `host_resources`가 포함되고 접수에서 거부된다는 점을 적는다(현재 문서는 운영자 제한 목록을 적지 않으므로, 적는다면 `session_limits`, `tier_models`, `role_tiers`, `claude_only_assigned_model`, `host_resources` 다섯이다). |

`references/CLI-실행-계약.md:75-76`의 `<formal_bundle>/proposal.lean`·`formal.json` 배치는 구현과 맞으므로 바꾸지 않는다.

## 5. 실행한 시험

모두 `.claude/skills/do-math`에서 `python scripts/run_tests.py …`로 돌렸다. Lean이 필요한 실행에는 `DO_MATH_KNOWLEDGE_TEST_LEAN=C:/math/.skill-workspace/do-math-toolchains/lean-4.32.0/lean-4.32.0-windows/bin/lean.exe`를 주었다.

| 대상 | 결과 |
|---|---|
| `test_query_records.QueryFamilyNameTests test_questions test_decision_basis test_reporting test_redesign_PROFILES.ProfileTests.test_unused_observation_settings_are_rejected_at_configuration_boundary` | 27 통과 |
| `test_redesign_ENGINE test_efficiency test_redesign_CONTRACTS.ContractBoundaryTests test_redesign_SURFACE test_query_records test_cli` | 196 통과, 오류 1 → 수리 |
| `test_redesign_ENGINE.ObservationTransactions test_lifecycle_engine test_connection_repairs test_engine test_governance_engine test_repository` | 134 통과, 실패 1 → 수리 |
| `test_redesign_ENGINE.ObservationTransactions test_observations test_checkpoint_persistence test_research_reliability test_stop_flags test_machine_parallel test_walkthrough_followup test_knowledge_import_engine test_performance_repairs test_submission_tools test_controls` | 185 통과, 오류 7 → 수리 |
| `test_knowledge_import_engine`(재실행) | 14 통과 |
| `test_submission_flow test_redesign_LIFECYCLE test_redesign_CONTRACTS test_redesign_PROFILES test_control_shapes test_academic_engine test_external test_operator` | 184 통과 |

실패·오류의 원인과 처리:

- 두 번째 줄의 오류와 세 번째 줄의 실패는 한 원인이다. 새 시험 `test_idle_observation_tick_neither_copies_nor_publishes_the_runtime`을 넣을 때 편집 기준 문자열이 기존 시험 `test_failed_observation_publication_does_not_advance_the_tracker`의 중간에 걸려, 기존 시험의 뒷부분 다섯 줄이 새 시험 안으로 옮겨졌다. 또 새 시험의 첫 틱은 규칙 신호 미측정 관찰을 내므로 유휴 틱이 아니었다. 기존 시험을 원래대로 되돌리고, 새 시험은 첫 틱 뒤의 두 번째 틱을 유휴 틱으로 단언하도록 고쳤다. 네 번째 줄 실행에서 `ObservationTransactions` 두 시험이 모두 통과했다.
- 네 번째 줄의 오류 7건은 `tests/test_knowledge_import_engine.py:152`의 `_register_execution` 대역이 새 키워드 인자 `profile`을 받지 못해서 났다. 대역 서명에 `profile=None`을 더했고 재실행에서 14건 모두 통과했다.
- 변경 전부터 실패하던 시험은 이번 실행에서 관찰되지 않았다.

결함을 고친 시험이 수정 전 코드에서 실패하는지는 자기 트리에서 해당 줄만 잠시 되돌려 확인하고 복원했다(기준 worktree는 만들지 않았다).

- `test_efficiency.EfficiencyTests.test_execution_effort_is_its_pinned_profile_effort_not_the_current_setting`: `"effort": config["effort"]`를 되살리면 `'minimal' != 'medium'`으로 실패했다.
- `test_connection_repairs.HostConfigurationTests.test_public_init_configure_and_removal`: 보호 키를 옛 4개로 줄이면 `ValueError not raised`로 실패했다. 복원 뒤 통과했다.
- `test_connection_repairs.FormalContinuationTests.test_check_stopped_before_start_ends_and_returns_its_capacity`: `_release_machine_execution`에서 `mark_returned`를 빼 옛 형식 검사 종료와 같게 하면 `('stopping', 'unknown') != ('ended', 'confirmed')`로 실패했다. 복원 뒤 클래스 4건이 통과했다.

나머지 새 시험(질의 가족 이름, 부적격 미리보기 골격, 유휴 관찰 틱, status 모양 일치, 입력 준비 중 정비 미실행)은 수정 전 코드에서 실패함을 코드로만 확인했다. 예를 들어 옛 `_observe_running`은 틱마다 `_save`를 불렀고, 옛 `_query_record`에는 `formal-result` 별칭이 없었다.

기계적 확인: 바꾼 `.py` 파일 전부 `py_compile` 통과, `scripts/tests`의 `test_*.py` 135개 모두 `importlib.import_module` 성공, 3절의 옛 이름 grep 0건.

돌리지 않은 관련 시험과 이유:

- `engine.status`·`reporting.status_report`의 다른 소비자 모듈(`status()`를 부르는 약 20개 시험 모듈)은 시험 지침 2절에 따라 통합 확인에 맡겼다. 필드 집합은 넓어지거나 그대로이고, 지운 필드 셋은 시험 단언이 0건이다.
- `bare_engine()`을 store 없이 쓰는 약 30개 모듈은 돌리지 않았다. 기본 store를 None에서 `StateStore`로 바꾼 변경은, 이전에 store에 닿던 경로가 모두 `AttributeError`로 실패했으므로 전에 통과하던 시험의 경로를 바꾸지 않는다. store에 닿지 않던 유일한 변경 경로 `_evaluation_context_for`는 `StateStore.git_dir`(None)로 이전 값과 같다.
- `test_research_recovery`(HIS-08 주석만 바뀜).

## 6. 기능이나 시험 범위가 바뀐 것

| 대상 | 이유 | 잃는 것 | 얻는 것 |
|---|---|---|---|
| `status --json` 출력 | ENG-03·16 | `host_observation`, `research_effectiveness`, `budget_observed_at`, `question_scope` 필드. `--snapshot`의 `host_observation` 인자 키 `observed_at`은 `research_observed_at`으로 바뀌고 모르는 키는 `ValueError` | 현재 조회와 `--snapshot`의 필드 집합이 같다. `--snapshot`에 `title`, `knowledge`, `questions`, `question_links`, `waiting_actions`, `academic_validation` 등이 생기고 관측 필드는 null이다 |
| 사람용 status 텍스트 | ENG-03 | 과제 행·`blocking` 행이 두 번 나오던 출력, "research effectiveness: not evaluated" 줄, "host observation" 줄 | 렌더러 하나, 관측하지 않은 값은 `not observed` |
| `check` 출력 | ENG-16 | `research_effectiveness` | 없음 |
| `query`의 `family`와 `--kind` 값 | ENG-07 | `execution_profiles`, `formal_results`, `expositions`, `identity_assessments`, `assessment_uses`, `goal_judgments`, `governance_sources`의 저장 이름 표기 | 조건 문법 이름 하나(`execution-profile` 등) |
| 부적격 미리보기 응답 | ENG-04 | 없음 | `check_id`·`schema_ref`·`input_hashes`가 생기고 `not_checked`가 정상 응답 목록에 `candidate_application`을 더한 목록이 된다 |
| 운영자 configure의 `host_resources` 변경 | ENG-01 | 적용 단계의 거부 영수증 | 접수 단계의 `ValueError`(최종 효과 동일) |
| AI 실행의 effort | ENG-02 | 설정값이 고정 프로필과 다를 때 설정값을 쓰던 동작 | 고정 프로필 effort 하나 |
| 시작 전에 정지된 형식 검사 | ENG-08의 종료 처리 통일 | 없음 | 이전에는 발사표를 반환 표시하지 않아 종료 장벽에서 `stopping`·`local_termination=unknown`으로 보류되었다. 이제 반환 표시 뒤 용량을 돌려주고 끝나며 정지 사유에 따라 계속·대기로 간다 |
| 적재 때 내장 지식 종류 보충 | ENG-14 | 설치에 새 내장 종류가 생겼을 때 기존 인스턴스를 채우던 보충(현재 인스턴스 없음) | 적재 경로와 무관한 상태 |
| `run` 시작의 `recovery_checked = True` | ENG-17 | 없음(유일한 독자 직전에 다시 계산) | 없음 |
| 유휴 관찰 틱 | ENG-15 | 소유자가 아직 게시하지 않은 변경을 유휴 틱이 대신 게시하던 부수 효과(다음 `_save`가 게시한다) | runtime 전체 deepcopy와 상태 비교의 틱당 1회 |
| `_call_steps`·`_formal`의 관문 | 영역 밖 관찰 | 두 함수가 스스로 관문을 통과하던 자기완결성. 직접 부르는 호출자는 관문을 먼저 통과시켜야 한다 | 같은 바퀴의 중복 관문 제거 |
| 시험 | ENG-19 | `test_control_reuses_one_reader_per_repository_and_instance` 삭제. 시험의 `control()` 호출마다 저장소 생성(git 조회 1회)이 다시 생긴다(조각 시간 영향은 재지 않았다) | 프로세스 전역 상태 하나 제거 |
| 시험 | 신규·강화 | 없음 | 2절·5절의 새 시험 7건과 기존 시험 단언 강화 3건(`test_cli` status 모양, `test_redesign_SURFACE` 관측 필드, `test_efficiency` 입력 준비 중 정비 미실행) |

## 7. 막힌 지점, 접근을 바꾼 지점, 예상과 달랐던 결과

- **ENG-05의 전달 방식.** 통합표는 `config["academic_binding"]`을 예로 들었다. 그러나 사용자 external 제어의 payload 스키마(`control_contracts.py`의 `obj()`)는 `additionalProperties: false`가 없어, 설정 키로 받으면 사용자 제어가 학술 결박을 위조해 넣을 수 있다. 신뢰 경계 밖 입력의 수신 검사(계약 4절)를 약하게 하지 않으려고 제어 payload가 실을 수 없는 키워드 인자로 넘겼다.
- **ENG-08의 배치.** 통합표는 "형식 검사는 판정 뒤 처리만 엔진에 남긴다"고 했다. 판정 뒤 처리는 `knowledge_records.record_formal_result`, `_start_identity_review`, `_enqueue`로, 모두 소유 모듈이나 믹스인의 호출이다. 또 형식 결과 기록은 용량 반환과 실행 종료 사이에 와야 한다(반환이 보류되면 기록하지 않고, 기록 실패는 종료 결과를 바꾼다). 이 호출들을 엔진 메서드로 떼면 종료 순서 한가운데 엔진 호출점이 셋 생긴다. 그래서 형식 검사 전체를 신뢰 검사 옆 `lifecycle_engine`에 두고 엔진에는 형식 검사 코드를 남기지 않았다.
- **ENG-08에서 보존한 차이.** 신뢰 검사는 여전히 반환 뒤 정지 재확인·재결박을 원문 보존 전에 하고, 전 구간을 `except Exception`으로 감싼다. 형식 검사는 원문 보존을 먼저 하고, 재결박을 형식 결과 기록 뒤에 한다. 정지 판정도 합치지 않았다. 형식 검사는 사유 집합을 모아 재개 가능 여부를 가르고, 신뢰 검사는 시계·대화 조건을 포함한 `_execution_stop_requested`를 쓰는 불리언 판정이어서, 합치면 동작이 바뀐다. `release_or_hold`의 호출 조건 차이는 실제 차이가 아니었다. `release_or_hold` 자체가 `capacity`가 없으면 참을 돌려준다(`execution_lifecycle.py:184`).
- **ENG-08에서 드러난 결함.** 옛 형식 검사 종료는 `mark_returned` 없이 `release_or_hold`를 불러, 시작 전에 정지된 검사가 종료 장벽에 보류되었다. `_end_machine_execution`으로 통일하면서 이 경로가 고쳐졌고, 재현 시험을 더했다(5절).
- **`proposal.lean`의 한 곳.** 원 검토는 원 반환 묶음을 제안했으나 공개 문서(`references/CLI-실행-계약.md:75`)와 시험(`test_redesign_ENGINE.py`의 원문 보존 시험)이 `formal.json`과 같은 형식 묶음을 가리킨다. 그래서 형식 묶음에만 두고 원 반환 묶음에서 뺐다. 문서 변경이 필요 없다.
- **ENG-03의 관측 필드 분류.** README :508은 `budget`·`provider_waits`를 한 snapshot에서 재구성한 값으로 설명하고, 통합표 정정은 `budget`을 `--snapshot`에서 호출자 관측으로만 채우라고 한다. 통합표를 따랐다. `provider_waits`와 `research_wake_reasons`는 조회 시각으로 `open`과 도래 여부를 판정하므로 같은 관측 필드에 넣었다.
- **ENG-20의 시험 대역.** `bare_engine`의 store가 None이면 `store.git_dir`에서 실패하므로, 제품에 예외를 두지 않고 대역 쪽에서 `StateStore`를 기본값으로 주었다.
- **작문 절차.** 이 파일에는 `write-for-reader`의 `명료한_산문.md`, `AI_프롬프트.md`, `에이전트_채널.md`를 적용했다. `writing_flow.py`의 별도 독해는 실행하지 않았다.

## 8. 다른 그룹 범위에서 발견한 문제

- **RUN**: `lifecycle_engine.py:61`(`lifecycle_clock`)과 `:79`(`lifecycle_monotonic`)의 방어 `getattr`이 남아 있다(RUN-09). 기계 경로의 관문 중복(`_process_machine_action`, `_run_external_action`, `_trust_check_steps`, `_trust_activation_steps` 재확인)은 RUN-03 몫이다. `_register_execution`이 이제 `profile=`을 받으므로, RUN-03이 관문의 프로필을 반환하게 하면 신뢰 검사·외부 작업 등록에 넘길 수 있다.
- **RUN·OPS**: 미종료 action ID 집합의 같은 규칙이 `governance_engine._configure_candidate`(2곳), `reporting.dispatch_waits`, `scheduler._dispatchable`의 `live` 목록에도 있다. 엔진 안의 3곳은 `ResearchEngine._live_action_ids`로 모았다.
- **REV·STO**: `review_engine.py:182`, `:184`가 `getattr(self.store, 'read', None)`, `getattr(self.store, "git_dir", None)`을 쓴다. ENG-20과 같은 시험 수용 방어다.
- **RUN(관찰)**: `_call_steps`의 실행 기록은 `"model": chosen_model["model"]`로 모델을 `model_selection`에서 다시 쓴다(`engine.py:3147`). ENG-02와 같은 모양이지만 `model_selection`이 고정 프로필과 어긋날 수 있는지는 확인하지 않았다.
- **HIS·TSB**: `tests/test_lifecycle_engine.py:48`의 `FakeEngine`은 `_controls`만 무효화한다. 새 `_apply_inbox`는 무효화되지 않지만 이 대역의 빈 inbox에서는 효과가 없다.
- **정리 대상 잔재(기존)**: `submission.py:24`의 `is_reparse`, `initialization.py:6`의 `Path`는 쓰이지 않는 import다. 이번 변경 전부터 있었다.
