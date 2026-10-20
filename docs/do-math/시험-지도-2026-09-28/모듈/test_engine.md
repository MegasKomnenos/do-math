# test_engine

| 항목 | 값 |
|---|---|
| 조각 | `lifecycle` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_engine.py` (766행) |
| 클래스 / 테스트 | 7 / 32 |
| 시험 대상 제품 코드 | `do_math/engine.py`의 `initialize`, `control`, `ResearchEngine`(`run`, `_enqueue`, `_register_execution`, `_provider_admit`, `_call_steps`, `_context`, `_save`, `_check_installation`, `_apply_inbox`, `_upkeep`, `_maintenance_cleanup`, `check`, `status`, `process_controls`, `_refresh_readiness`, `_lifecycle_event`), `_record_evidence`; `do_math/scheduler.py`의 `_dispatchable`; `do_math/state_contract.py`의 `default_state_contract`; `do_math/repository.py`의 `ResearchRepository`, `canonical_json`, `exact_content_hash`; `do_math/context_store.py`의 `prepare_role_input`; `do_math/windows_job.py`의 `WindowsJob`; `do_math/codex_adapter.py`의 `CodexExecAdapter.wait_for_termination`; `do_math/knowledge_records.py`의 `usable_links` |
| 사용하는 픽스처 모듈 | `research_fixtures`(`activate`, `candidate`, `charter_change`, `current_state`, `FixtureAdapter`, `git_init`, `governance_start`, `install_adapter_fixture`, `restore_template`, `send_control`, 그리고 `PublicGitFlow` 안에서 `contract_review`, `intent_response`, `assessment`, `seal_response`, `local_job_runner`, `planning_model_assessments`); `engine_fixtures`(`initialized`, `routing_engine`); `runner_fixtures`(`context_from`, `formal_ok`, `ScriptedRunner`, `contract_checks`); `state_fixtures`(`active_instance`, `ACTIVE_LEAN_COMMAND`) |
| 격리 표지 | 없음 |
| 시작 상태 | 4단(공개 `initialize`에서 시작) 4개(그 가운데 공개 활성화까지 도는 것은 `test_public_initialization_reaches_active_with_distinct_interpretation`과 `PublicGitFlow` 2개), 2단(`state_fixtures.active_instance` 복원) 다수, 2단 위의 모듈 전용 빌드 `efficiency_instance`, 1단(검증기·순수 함수) 2개, `routing_engine` 메모리 엔진 2개. 엔진을 모는 시험은 `ScriptedRunner`가 실제 Windows Job 자식 프로세스를 띄운다 |

## 목적

모듈 docstring은 "연구 엔진 자신의 동작: 초기화와 활성화, 큐, 배정, 게시, 설치 점검"을 시험한다고 밝힌다. 모듈은 `ResearchEngine`의 소유자 루프를 여러 층에서 검사한다. 공개 초기화와 활성화의 끝단 연결, 형식 지식 발행 규칙, 실행 도중 충돌한 실행의 복구, 증거 레코드의 정확한 해시, 큐 병합 규칙, 사용자 정지(pause)와 모델 시작의 경계, 설치 판본 점검의 주기, 게시의 멱등성, 과제 준비도(readiness)의 파생이 그 대상이다.

이 모듈에는 `research_fixtures` docstring의 "When to keep the public path or the child process" 절이 "전용 시험(dedicated tests)이 지키는 끝단 연결"로 이름을 들어 지목한 시험 두 개가 있다. 둘은 템플릿 복원으로 대체하면 안 되는 공개 경로를 유지한다.

- `EngineTests.test_public_initialization_reaches_active_with_distinct_interpretation`은 **공개 `initialize` → 공개 제어(`control`)로 채운 활성화 조건 → 실제 해석 실행 두 번(작성자와 검사자) → `active` 상태**로 이어지는 연결을 지킨다. 템플릿(`activated_instance`)은 이 경로를 한 번 돈 결과만 복원하므로, 활성화 과정에 결함이 있어도 최종 상태가 같으면 템플릿에서 시작한 시험은 드러내지 못한다. 이 시험은 그 과정 자체를 매번 돈다.
- `PublicGitFlow.test_public_activation_work_receipt_assessment_and_next_plan`은 **공개 활성화 → 연구 준비 → 과제 계약 검토 → 계획 → 연구 작업 → 작업 제출의 실제 제어 전송 수신증(receipt) → 다음 계획의 결과 평가 → 과제 `completed`와 지식 발행 → Git에 게시된 상태**로 이어지는 연결을 지킨다. 모든 역할 출력이 실제 작업자처럼 `submission.request_control`로 `submit_intent`를 보내고 `ControlTransport.wait_receipt`로 영속 수신증을 기다린다.

같은 docstring은 세 번째 전용 연결로 `purpose_fixtures.solved_instance` 빌드(`test_purpose_engine.SolvedPurposeTests`가 읽음)를 드는데, 이는 이 모듈 밖이다.

## 모듈 수준 요소

- 행 15–16 `SCRIPTS`: 스킬의 `scripts/` 폴더. `sys.path` 앞에 넣어 `do_math`를 import하게 하는 공통 머리다. `test_crash_recovery_and_artifact_immutability`가 자식 프로세스에 이 경로를 인자로 넘겨 `do_math.windows_job`을 import시킨다.
- `formal_fail(**_)` (행 27): 형식 검사기 대역. 항상 `{"status": "failed", "reason": "mock formal failure; not Lean sorry evidence"}`를 돌려준다. `test_formal_requires_two_blind_reviews_and_failure_does_not_create_k`의 후반부에서만 쓴다.
- `efficiency_instance(root, shared, *, config, charter)` (행 441–460): `restore_template` 빌드. `state_fixtures.active_instance`로 합성 활성 상태를 만들고, `work-0/runs`를 만든 뒤 `research_preparation` 하나를 큐에 넣어(`reason="Prepare the bounded efficiency fixture"`) `_save`로 게시한다. `charter=True`이면 공개 `decision` 제어로 헌장 개정(`charter_change`)을 보내 학술 요구 `explain`(`scope="solution"`, `criteria=["explain structure"]`, `assessor="research_plan"`)을 승인시키며, 이 사용자 결정 이벤트가 계획 하나를 연다. 인스턴스 ID를 돌려준다. `research_fixtures` docstring의 "What to use"에 이 모듈 전용 빌드로 등재돼 있다. 사용처는 `QueuedPreparationTests.open`.
- 행 463–464 `EFFICIENCY_CONFIG`: `efficiency_instance`에 넘기는 설정. 운전자·학술 검색을 끄고, `lean_command=["test-lean"]`, `tool_review_window_seconds=60`, `self_check_response_window_seconds=5`다.
- 행 766: 직접 실행하면 `unittest.main(verbosity=2)`.

## EngineTests (행 30–203)

`unittest.TestCase`를 상속한다. 표지는 없다.

- `setUp` (행 31–34): `install_adapter_fixture(self)`로 `do_math.initialization.adapter_for`를 `FixtureAdapter`로 바꾼다(외부 CLI 관측만 대체하고 증거 해시와 능력 관문은 유지). 임시 디렉터리를 `self.root`로 두고 `git_init(self.root / "repo")`로 저장소를 만든다.
- `tearDown` (행 36): 임시 디렉터리를 지운다.
- `make(runner, verifier=formal_ok, **config)` (행 38–43): 4단 공개 경로. `initialize(self.repo, goal="goal", ...)`를 `reviewers=2`, `goal_auditors=2`, `lean_command=["test-lean"]`, 학술 검색·운전자 끔, `plan_settle_seconds=1`(기본)로 부르고, 새 `ResearchEngine`을 만든 뒤 `activate(engine, self.root, initialization_runner=ScriptedRunner())`로 공개 활성화를 돈다. `(engine, instance_id)`를 돌려준다. docstring에 따르면 공개 초기화 시험만 이 도우미를 쓴다.
- `active(runner, verifier=formal_ok, **config)` (행 45–56): 2단. `restore_template(active_instance, config=...)`로 합성 활성 상태 사본을 받는다. 설정은 `make`와 같되 `lean_command`가 `ACTIVE_LEAN_COMMAND`(`synthetic-lean`, `base`)다. `self.root`와 `self.repo`를 사본 경로로 바꾸고 새 엔진을 돌려준다. docstring은 호출마다 이전 사본이 교체되므로 앞 엔진을 끝낸 뒤 다음을 요청하라고 적는다. `research_fixtures` docstring은 이 도우미를 "plain form"으로 가리킨다.

### `test_initialization_reports_missing_values_without_model_dispatch` (행 58–73)
- 성질: 활성화 조건이 비어 있는 초기화 인스턴스는 모델을 부르지 않고, 빠진 값 목록과 사용자 차단 상태를 게시한다.
- 준비: 4단. 공개 `initialize`(목표 `"Explicit initial input"`, 학술 검색·운전자 끔)만 돈 인스턴스. 활성화 제어는 보내지 않는다.
- 실행: `ScriptedRunner`를 단 엔진의 `run(max_steps=1)`.
- 단언: 수명 상태가 `initializing`이다. `lifecycle.activation.missing`이 `governance`, `configuration`, `independent_intent`, `trust_environment`, `research_authority` 다섯을 포함한다(부분집합 비교). 러너의 `prompts`가 비어 있다(모델 호출 없음). `grants`가 `{}`다. 저장소에서 다시 읽은 인스턴스의 `missing`이 메모리 값과 같고, 게시된 런타임의 `availability`가 정확히 `{"state": "blocked", "reason": "initialization_incomplete", "next_owner": "user"}`다.
- 대역: `FixtureAdapter`(`setUp`). 러너는 불리지 않는다.

### `test_public_initialization_reaches_active_with_distinct_interpretation` (행 75–81)
- 성질: 공개 초기화와 공개 제어만으로 인스턴스가 `active`에 이르고, 원 입력의 해석과 그 검사는 서로 다른 실행이 맡는다.
- 준비: 4단. `make(ScriptedRunner())`가 공개 `initialize`와 `research_fixtures.activate`를 돈다. `activate`는 헌장 승인, 초기 권한 `GR-initial-fixture`와 연구 권한 `GR-research-fixture`, 현재 설정 해시를 지정한 능력 관측(probe), 합성 신뢰 환경 등록과 전환, 초기화 채택 결정을 모두 공개 `control`로 보내고, `engine.run(until_active=True)`로 해석 실행 두 번(작성자·검사자)을 실제 로컬 Job에서 돌린다.
- 실행: `make` 안의 `initialize`, `control`, `process_controls`, `run(until_active=True)`.
- 단언: 수명 상태가 `active`다. `lifecycle.intent_check`의 `interpretation_execution_id`와 `check_execution_id`가 다르다. `capability_evidence`가 비어 있지 않다. `activation.missing`이 `[]`다.
- 대역: `FixtureAdapter`(능력 관측), `ScriptedRunner`(해석 출력), `trust_fixture`의 합성 툴체인, `formal_ok`(검증기로 넘기지만 이 경로에서는 불리지 않는다).
- 비고: `research_fixtures` docstring이 지목한 전용 시험이다. 4절 규칙 3의 판별 질문("활성화 과정에 결함이 있어도 끝 상태가 같다면 실패해야 하는가")에 "그렇다"로 답하는 시험이므로 템플릿으로 바꾸지 않는다. 실제 외부 자원: `ScriptedRunner`의 `local_job_runner`가 해석 실행마다 `python -c "import time; time.sleep(600)"` Windows Job을 띄우고 끝낸다.

### `test_nonformal_mathematical_goal_is_not_solved` (행 83–97)
- 성질: 비형식 결과만 있는 수학 목표는 필요한 목표 감사가 모두 끝나도 `mathematically_solved`가 되지 않고 형식 지식 `K`도 0이다.
- 준비: 2단. `active(ScriptedRunner())`. `formal=False`이므로 작업은 비형식 정리를 낸다.
- 실행: `run(max_steps=1)`을 최대 20번 돌리고, 끝난 `goal_audit` 실행이 설정 `goal_auditors`(2) 이상이면 멈춘다. 주석은 결정 지점이 목표 감사의 판단이고 이후 단계는 준비와 판단을 반복할 뿐이라고 설명한다.
- 단언: 끝난 목표 감사가 하나 이상 있다. 결과(`results`)를 가진 과제가 있다. 마지막 `status`의 `goal_status`가 `mathematically_solved`가 아니다. `status["knowledge"]["K"]`가 0이다.
- 대역: `ScriptedRunner`, `formal_ok`, `FixtureAdapter`.
- 비고: 20단계 상한 안에 목표 감사가 둘 끝나지 않아도 루프는 조용히 끝나고, 단언은 감사가 하나 이상인지만 본다. 실제 Windows Job 자식 프로세스를 역할 호출마다 띄운다.

### `test_formal_requires_two_blind_reviews_and_failure_does_not_create_k` (행 99–140)
- 성질: 형식 지식은 같은 검토 주기의 서로 다른 두 자리(slot)에서 이뤄진 맹검 식별 검토 둘을 거쳐야 발행되고, 활성 신뢰 환경의 툴체인에 결박되며, 형식 검사가 실패하면 `K`가 생기지 않는다.
- 준비: 2단 두 번. 전반은 `ScriptedRunner(formal=True)`와 `formal_ok`, 후반은 새 `ScriptedRunner(formal=True)`와 `formal_fail`로 `active`를 다시 부른다(사본 교체).
- 실행: 전반은 `run(max_steps=4)`씩 최대 30단계를 돌려 `K == 1`이면 멈춘다. 닿지 못하면 스냅숏·큐·대기·실행 요약을 JSON으로 싣고 실패한다. 후반은 `run(max_steps=4)`씩 최대 20단계를 돌려 `formal_status == "failed"`로 끝난 `formal_check` 실행이 생기면 멈추고, 닿지 못하면 실패한다.
- 단언: 전반에서 `K`가 1이다. `usable_links`가 있는 지식 `kid`를 찾고, 그 링크의 `assessment_id`에서 `review_cycle_id`를 얻는다. 러너가 받은 `identity_review` 프롬프트 가운데 단계 `initial`, 대상 `kid`, 그 주기이고 실행 결과가 `output_accepted`인 것이 정확히 2개다. 두 검토의 `slot`은 서로 다르고 `review_cycle_id`는 하나다. 두 프롬프트 모두 문자열 `"reviews"`를 담지 않는다(다른 검토의 판단을 보지 못하는 맹검). 지식의 형식 결과가 가리키는 신뢰 환경의 `status`가 `active`이고, 그것이 `active_trust_environment`와 같으며, 형식 결과 `verification.toolchain`이 활성 환경의 `toolchain`과 같다. 후반에서는 `K`가 0이다.
- 대역: `ScriptedRunner(formal=True)`, `formal_ok`(두 고정 원문만 검증하는 컴파일러 대역), `formal_fail`, `FixtureAdapter`.
- 비고: 한 시험 안에서 템플릿 사본을 두 번 받는다. 실제 Windows Job 자식 프로세스를 쓴다.

### `test_plan_rejects_missing_candidate_and_criterion` (행 142–157)
- 성질: 준비된 과제를 다루지 않은 계획, 또는 반환된 과제의 완료 의무 판정을 비운 계획은 출력 검증에서 거부되어 실패 대기로 보존된다.
- 준비: 2단. 두 경우(`invalid` = `"missing"`, `"criterion"`)마다 `active(ScriptedRunner(invalid_plan=invalid), max_output_repairs=0)`. `ScriptedRunner`는 `"missing"`이면 계획의 `dispositions`를 비우고, `"criterion"`이면 모든 `task_assessments`의 `item_dispositions`를 비운다. 수리 횟수 0이라 첫 거부가 곧 결과다(주석: 출력 수리는 다른 곳에서 시험한다).
- 실행: `run(max_steps=1)`을 최대 20번, 역할 `research_plan`이고 종류가 `output_validation` 또는 `execution_failure`인 대기 행동이 생기면 멈춘다. 닿지 못하면 실패한다.
- 단언: 상태가 `completed`가 아니다. 그 대기의 실행이 모두 `ended`다. 대기 사유(`reason`) 가운데 하나가 `"missing"`이면 `derived-ready`를, `"criterion"`이면 `obligation`을 담는다. 거부 사유는 메시지 조각으로 고정된다.
- 대역: `ScriptedRunner(invalid_plan=...)`, `formal_ok`, `FixtureAdapter`.
- 비고: 두 경우를 `subTest` 없이 반복한다. 실제 Windows Job 자식 프로세스를 쓴다.

### `test_crash_recovery_and_artifact_immutability` (행 160–203)
- 성질: 발사 소유자가 죽고 Job이 비어 있는 실행은 다음 엔진이 `execution_incomplete`로 복구해 소유 활동과 복구 기록에 남기고, 그 결과 산출물 묶음은 게시 뒤 바꿀 수 없다.
- 준비: 2단. `active(ScriptedRunner())` 위에서 `research_preparation`을 큐에 넣고, 실행 `EX-crash`를 `queued`로 등록한 뒤 프로필을 골라 `_provider_admit`으로 입장시킨다(참이어야 한다). 별도 Python 자식 프로세스로 `owner_identity()`를 얻어 이미 끝난 실제 소유자를 만들고, 그것을 `launch_ticket.owner`로 넣어 단계를 `dispatched`로 바꾼다(주석: 살아 있는 unittest 프로세스를 죽은 소유자로 세면 안 된다). 발사 표의 Job 이름으로 `python -c pass` Job을 만들어 세션 슬롯에 `started`로 기록하고 재개한다. `CodexExecAdapter('fixture-cli').wait_for_termination`을 원래의 10초 상한으로 불러 참이어야 하고, Job의 활성 프로세스가 0이어야 한다(주석: 루트 신호만으로는 Job의 활성 개수 갱신보다 앞설 수 있다). 그 뒤 `_save`.
- 실행: 새 `ResearchEngine(...).run(max_steps=1)`, 이어서 `ResearchRepository.load`와 `save_with_state`.
- 단언: 게시된 런타임에서 `EX-crash`의 `outcome`이 `execution_incomplete`다. 소유 활동의 `assigned_execution_ids`가 `EX-crash`를 담는다. `recoveries`가 비어 있지 않다. 소유 활동이 `waiting`이거나 `unresolved`를 가진다. 복구된 실행의 `result_ref`를 저장소에서 읽을 수 있다. 같은 `artifact_bundle` 아래에 새 파일 `other.txt`를 더하는 `save_with_state`는 `ValueError`로 거부된다(유형만 본다).
- 대역: `FixtureAdapter`(`setUp`), 두 엔진에 단 `ScriptedRunner`. 발사 소유자, Job, 수집 장벽은 대역이 아니라 실제 자원이다.
- 비고: 실제 외부 자원이 셋이다. `subprocess.check_output`으로 띄우는 Python 자식 프로세스, 실제 `WindowsJob`, 실제 수집 장벽(`wait_for_termination`, 상한 10초).

## QueryIdentity (행 206–233)

`unittest.TestCase`를 상속한다. 설정 훅과 도우미가 없다.

### `test_exact_evidence_binds_persisted_bytes_and_code_points` (행 207–223)
- 성질: 레코드 증거는 게시된 바이트의 해시와 레코드 내용의 코드 포인트 수준 해시를 따로 결박하고, 유니코드 정규화로 같아 보이는 값도 구별한다.
- 준비: 1단. 레코드 `FR-one`의 `title`은 `e`와 결합 악센트 U+0301로 된 분해형 `"é"`이고, `verification`은 켈빈 기호 `"K"`(K)와 라틴 `"K"`를 서로 다른 키로 가진다. 내부 함수 `evidence(value)`는 `canonical_json({"record": value})`의 바이트와 SHA-256으로 행을 만들어 `_record_evidence`에 넘긴다.
- 실행: `do_math.engine._record_evidence` 세 번.
- 단언: 결과의 `json_pointer`가 `/record`다. `sha256`이 정규 JSON 바이트의 해시와 같다. `logical_sha256`이 `exact_content_hash(record)`와 같다. `title`만 완성형 `"é"`(U+00E9)로 바꾼 레코드의 `logical_sha256`은 다르다. `verification`의 켈빈 키 값만 분해형 `"é"`에서 완성형 `"é"`(U+00E9)로 바꾼 레코드의 `logical_sha256`도 다르다.
- 대역: 없음.
- 비고: 원문은 `"K"` 키를 이스케이프 없이 문자 그대로 적었기 때문에 편집기에서는 `"K"` 키가 둘인 사전처럼 보인다. 실제로는 서로 다른 두 키다.

### `test_duplicate_id_is_rejected_across_families` (행 225–233)
- 성질: 상태 계약은 서로 다른 레코드 계열에 걸쳐 같은 ID를 거부한다.
- 준비: 1단. `current_state`로 `sources`에 ID `DUP`, 런타임 `events`에 같은 ID `DUP`를 둔 상태.
- 실행: `default_state_contract().validate(instance, runtime)`.
- 단언: `ValueError`를 메시지 정규식 `"record IDs must be globally unique: DUP"`로 던진다.
- 대역: 없음.
- 비고: 주석은 게시 전 번들 후보마다 이 검사가 `_validate_bundle_candidate`에서 `validate_candidate`로 이어져 돈다고 적는다.

## ObservationMerge (행 236–251)

`unittest.TestCase`를 상속한다. 설정 훅과 도우미가 없다.

### `test_merged_review_keeps_all_obligations_and_evidence_refs` (행 237–251)
- 성질: 같은 실행에 대한 실시간 운영 검토 요청 둘은 하나로 합쳐지되, 두 요청의 의무와 관찰 참조를 모두 보존하고 관찰 정보는 나중 것을 따른다.
- 준비: `engine_fixtures.routing_engine()` 메모리 엔진.
- 실행: `_enqueue("operational_review", "EX-worker", live=True, ...)`를 두 번. 첫째는 `OB-a`, `artifact:a`, 관찰 순번 1이고, 둘째는 `OB-b`, `artifact:b`, 순번 2다.
- 단언: 큐 길이가 1이다. 합쳐진 행동의 `id`가 첫 행동과 같다. `obligation_ids`가 `["OB-a", "OB-b"]`, `observation_refs`가 `["artifact:a", "artifact:b"]`이고, `observation.sequence`가 2다.
- 대역: `routing_engine`(저장소 없는 엔진).

## PublicGitFlow (행 254–360)

`unittest.TestCase`를 상속한다. 설정 훅이 없고, 시험 안에 지역 러너 클래스 `Runner`를 정의한다.

### `test_public_activation_work_receipt_assessment_and_next_plan` (행 255–360)
- 성질: 공개 초기화부터 연구 작업의 수신증, 반환 결과 평가, 다음 계획, 과제 완료까지 실제 Git 저장소 위의 최소 연구 흐름이 모든 실행을 `output_accepted`로 끝내며 이어진다.
- 준비: 4단. 임시 디렉터리에 `engine_fixtures.initialized`로 공개 `initialize`를 돈다. 목표는 `"Record and assess a bounded observation"`, 설정은 학술 검색·운전자 끔, `lean_command=["fixture-lean"]`, `observation_mode="periodic"`, `tool_review_window_seconds=600`, `self_check_response_window_seconds=60`, 각종 한도 3이다. 지역 `Runner`는 `local_job_runner`로 감싼 `run`이 실제 로컬 Job 안에서 `execute`를 부르고, 예외를 stdout에 찍고 다시 던진다. `execute`는 작업공간의 `input/submission/context.json`에서 역할을 읽어 `roles`에 쌓고 `on_started`를 부른 뒤 역할별 출력을 만든다.
  - `intent_interpretation`: `intent_response(context)`.
  - `research_preparation`: 과제가 없을 때만 후보 `"bounded observation"` 하나를 낸다. 그 후보의 `profile_refs`는 `research_work` 프로필이고 `authority_refs`는 `GR-research-fixture`다. 출력 스키마에 `observed_at`이 있으면 채운다. 후보가 있으면 `activity-extensions.json`에 `contract_checks`, 관찰 규칙 `rule-attempt`(`counter_gte`, 대상 `attempts`, 임계 10, 근거 `checkpoint`)를 담은 `task_conditions`, 모델 평가를 쓴다.
  - `task_contract_review`: `contract_review(context)`.
  - `research_plan`: 준비된 과제 모두를 `selected`로 처분하고, 반환된 과제마다 `assessment`를 붙이며, `goal_audit=False`로 둔다. 확장 파일에 `planning_model_assessments`를 쓴다.
  - `research_work`: `outcome="submitted"`와 관찰 지식 하나를 낸다.
  - 그 밖의 역할: `AssertionError`.

  역할마다 `seal_response`로 봉인하고 `draft.json`을 쓴다. 그런 다음 `context["control_binding"]`이 인자의 `control_binding`과 같은지, 그리고 `self_check` 도구가 `research_work`에만 있는지 단언한다. 끝으로 실제 전송 `submission.request_control(..., kind="submit_intent", wait_seconds=0)`을 보내 상태가 `submitted` 또는 `already_received`인지 확인하고, `ControlTransport.wait_receipt(..., 60)`의 수신증 상태가 `accepted`인지 확인한다.
- 실행: 엔진의 `run`을 `checked_run`으로 감싼다. `checked_run`은 매 호출 뒤 `output_accepted`가 아닌 채로 끝난 실행이 없음을 단언하고, 있으면 큐의 수리 쟁점을 함께 싣는다. `activate(engine, root, initialization_runner=runner)`로 공개 활성화를 돌고, `run(max_steps=1)`을 최대 15번 돌려 `completed` 과제가 생기면 멈춘다. 닿지 못하면 최근 기록 5개를 싣고 실패한다.
- 단언: 활성화 뒤 수명 상태가 `active`다. 완료 과제 평가의 첫 `item_dispositions` 종류가 `fulfilled`다. `instance["knowledge"]`가 비어 있지 않다. 러너가 `research_plan`을 2번 이상, `research_work`를 정확히 1번 받았다. 저장소에서 다시 읽은 런타임에서 그 과제가 `completed`이고 `integrations`가 비어 있지 않다. 각 역할 호출 안에서 제어 결박 일치, 자기 점검 도구의 역할 한정, 제출 전송 상태, 수신증 `accepted`를 단언한다.
- 대역: `FixtureAdapter`(`install_adapter_fixture`), 지역 `Runner`(모델 출력 대역), `trust_fixture` 합성 툴체인(`activate` 안). 제어 전송, 봉인, 스키마 검증, Git 게시는 실제다.
- 비고: `research_fixtures` docstring이 지목한 전용 시험이다. 지키는 끝단 연결은 목적 절에 적었다. 실제 외부 자원: 역할 호출마다 `local_job_runner`가 Windows Job 자식 프로세스를 띄운다. 수신증 대기 상한은 60초다.

## MaintenanceConnections (행 363–417)

`unittest.TestCase`를 상속한다. 설정 훅과 도우미가 없다.

### `test_maintenance_archives_complete_run_before_approved_cleanup` (행 364–417)
- 성질: 정비 정리는 사용자가 승인한 정확한 실행 범위만 지우고, 지우기 전에 그 실행의 run 폴더 파일 전부를 해시가 맞는 산출물로 보존한다.
- 준비: 실제 Git 저장소(`git_init`)와 `routing_engine`. 인스턴스는 `governance_start`에 기본 설정의 실행 프로필을 더한 것이다. 통치 원문 `SOURCE-cleanup`을 보존하고 `governance.apply_decision`으로 `maintenance` 역할의 로컬 권한 `GR-cleanup`을 적용한다. 행동 `AC-cleanup`은 `cleanup_execution_ids=["EX-finished"]`와 요청자 `UC-cleanup`을 가지며, 같은 사용자 요청 기록을 `history`에 둔다. `EX-finished`와 `EX-maintenance` 두 실행을 활동과 함께 만들어 `cancelled`로 끝내고, 합성 종료 증거(`launch_ticket` 단계 `not_started`, `capacity.local_termination="confirmed"`)를 붙인다. 주석은 범위·스키마·참조·Git I/O는 실제라고 적는다. `ResearchRepository.initialize`로 게시하고, `work/runs/EX-finished`에 `workspace/draft.txt`와 `evidence/runner.json`을 쓴다.
- 실행: 작성자 잠금 안에서 `_maintenance_cleanup`을 두 번 부른다. 먼저 범위를 `EX-maintenance`로 바꾼 행동으로, 다음에 원래 행동으로.
- 단언: 범위를 바꾼 호출은 `ValueError`(`"exact user-approved"`)로 거부되고, 그때 `head`가 바뀌지 않으며 run 폴더가 남아 있다. 원래 호출의 `deleted`가 `["runs/EX-finished"]`이고 run 폴더가 사라진다. `EX-finished`의 `collection.retention_manifest`가 2행이며, 각 행의 산출물을 그 스냅숏에서 읽은 바이트의 SHA-256이 행의 `sha256`과 같다.
- 대역: `routing_engine`의 자동 사양 대역 메서드. 종료 증거는 합성이다.
- 비고: 실제 Git 저장소를 쓴다.

## SourceIntegrityCheckTests (행 420–438)

`unittest.TestCase`를 상속한다. 설정 훅과 도우미가 없다.

### `test_current_corrupt_source_is_found_by_the_explicit_full_byte_check` (행 421–438)
- 성질: 현재 스냅숏의 원자료 바이트가 손상되면 명시적 `check`의 전체 바이트 검사가 그것을 찾아내고, 검사는 게시 상태를 바꾸지 않는다.
- 준비: 4단(공개 `initialize`에 원자료 `source.txt` 첨부). 저장소의 불변 산출물 관문 `_validate_artifact_changes`만 `patch.object`로 끄고 원자료 경로에 `b"corrupt bytes"`를 게시해 손상을 만든다(주석: 의도한 손상 픽스처이고 시험하는 읽기·복구 관문은 실제다).
- 실행: 새 엔진의 `check(requested_areas=["record_storage"])`.
- 단언: `passed`가 거짓이다. `inspection.findings` 가운데 원자료 경로를 `evidence`에 담은 행이 있다. 저장소의 `read_snapshot().head`가 손상 게시의 head와 같다(검사가 새로 게시하지 않았다).
- 대역: `_validate_artifact_changes`를 `return_value=None`으로 패치.
- 비고: 주석은 `run`과 제어는 산출물의 존재와 길이만 보고 전체 바이트는 `check`의 몫이라고 적는다. `test_construction_and_status_leave_installation_and_artifact_bytes_to_run_and_check`가 그 반대편을 검사한다.

## QueuedPreparationTests (행 467–763)

`unittest.TestCase`를 상속한다. 클래스 docstring은 "게시된 준비 하나가 큐에 있는 합성 활성 상태 위의 엔진(`efficiency_instance`)"이라고 밝힌다.

- `model_process(arguments, *, resume)` (행 471–486): 문맥 관리자. 발사 표의 Job 이름으로 `python -c "import time; time.sleep(600)"` `WindowsJob`을 만들고 `on_started`에 그 프로세스 식별을 보고한다. `resume=True`이면 재개한다. 나갈 때 Job을 종료하고 10초 안에 끝나는지와 활성 프로세스 0을 단언한 뒤 닫는다.
- `setUp` (행 488–490): `do_math.initialization.adapter_for`를 `FixtureAdapter()`로 패치하고(`enterContext`), `open(charter=False)`를 부른다.
- `open(*, charter)` (행 492–496): `restore_template(efficiency_instance, config=EFFICIENCY_CONFIG, charter=charter)` 사본 위에 새 `ScriptedRunner`를 단 `self.engine`을 만든다. `self.workspace`는 `root / "work-0"`다.
- `startup()` (행 498–502): `open(charter=True)`로 헌장 사본을 받고 `_refresh_readiness()`를 부른 뒤 큐의 `research_plan` 행동을 돌려준다.

시작 상태는 2단 위의 모듈 전용 빌드다. 기본은 준비 하나가 큐에 게시된 상태이고, `startup`을 쓰는 시험은 헌장 개정 결정이 적용되어 계획 하나가 더 열린 상태다.

### `test_pending_preparation_keeps_every_reason_without_duplicate_text` (행 504–514)
- 성질: 대기 중인 준비 요청들은 하나로 합쳐지며, 모든 사유와 이벤트 참조를 보존하되 같은 사유 문장을 두 번 적지 않는다.
- 준비: 클래스 절 기본 상태에서 큐를 비운다.
- 실행: `_enqueue("research_preparation", ...)` 세 번(사유 A와 이벤트 `A`, 사유 B와 이벤트 `B`, 같은 B를 한 번 더).
- 단언: 큐 길이 1. 사유가 `"Investigate definition A"`를 담고, `"Check independent obligation B"`는 한 번만 나온다. `event_refs`가 `["A", "B"]`다.
- 대역: 없음.

### `test_stopping_execution_input_is_never_merged` (행 516–524)
- 성질: 정지 중인 실행이 입력으로 가진 행동에는 새 요청을 합치지 않는다.
- 준비: 기본 상태. 큐를 행동 `A`(사유 `old`) 하나로 두고, 같은 행동을 입력으로 가진 `stopping` 실행 `E`를 넣는다.
- 실행: `_enqueue("research_preparation", reason="new", event_refs=["later"])`.
- 단언: 큐 길이 2. 첫 행동의 사유가 `old` 그대로이고 `event_refs` 키가 없다.
- 대역: 없음.

### `test_active_charter_update_can_plan_and_preserves_its_event` (행 526–532)
- 성질: 활성 상태의 헌장 갱신이 연 계획은 배정 가능하고, 배정 가능성을 판정해도 이벤트는 바뀌지 않으며 대기 이벤트로 남는다.
- 준비: `startup()`이 돌려준 계획 행동. 이벤트 목록의 사본.
- 실행: `_dispatchable(action)`.
- 단언: 행동에 `initial_preparation_wait` 키가 없다. `_dispatchable`이 참이다. `runtime["events"]`가 사본과 같다. `pending_events`가 비어 있지 않다.
- 대역: `FixtureAdapter`.
- 비고: 제품 코드에는 `initial_preparation_wait` 키나 초기 준비 대기 분기가 없다(`do_math/` 전체 검색 결과 없음, 판정 함수는 `scheduler.py`의 `_dispatchable`, 행 218–268). 그러므로 첫 단언은 늘 성립하며, 사라진 대기 기제가 되살아나는 것을 막는 회귀 방지로만 작동한다.

### `test_charter_replanning_preserves_ongoing_preparation_and_consumes_its_event` (행 534–548)
- 성질: 헌장 갱신이 연 재계획은 진행 중인 준비를 없애지 않고, 계획이 받아들여지면 그 사용자 결정 이벤트를 소비한다.
- 준비: `startup()` 뒤 새 `ScriptedRunner`를 달고 `_save`.
- 실행: `run(max_steps=3)`.
- 단언: 러너가 받은 `research_plan` 입력이 정확히 1개이고 그 `ready_task_ids`가 `[]`다. 역할 호출의 다중집합이 `research_preparation`, `task_contract_review`, `research_plan` 셋이다(`assertCountEqual`). 마지막 `user_decision_applied` 이벤트의 ID를 담은 `event_consumption` 기록이 `history`에 있고, 그 ID가 `pending_events`에 없다.
- 대역: `ScriptedRunner`, `FixtureAdapter`.
- 비고: 실제 Windows Job 자식 프로세스를 쓴다.

### `test_regular_empty_plan_can_still_dispatch` (행 550–551)
- 성질: 이벤트도 과제도 가리키지 않는 일반 계획 요청은 배정 가능하다.
- 준비: 기본 상태.
- 실행: `_dispatchable({"role": "research_plan", "reason": "assess failed approach"})`.
- 단언: 참이다.
- 대역: 없음.

### `test_pause_received_during_input_preparation_prevents_model_start` (행 553–577)
- 성질: 입력을 준비하는 도중에 받은 사용자 정지는 모델 시작을 막고, 실행을 시작 기록 없이 `cancelled`로 끝내며, run 폴더를 남기지 않는다.
- 준비: 기본 상태. 실행 ID 집합, 러너 호출 수, `runs/` 목록을 기록한다. `_context`를 감싸 원래 문맥을 만든 뒤 공개 `control(..., "pause", ...)`을 보내게 한다. `_upkeep`은 불리면 `AssertionError`를 던지도록 패치한다(주석: 준비는 사용자 제어만 적용하고 주기 정비는 소유자 루프에 맡긴다).
- 실행: `_call_steps(queue[0])` 생성기의 첫 `next`.
- 단언: `StopIteration`이 난다(모델 호출 인자를 내지 않는다). 상태가 `paused`다. 러너 호출 수가 그대로다. 새 실행이 정확히 하나이고 `(status, outcome)`이 `("ended", "cancelled")`이며, `started_at`이 `None`이고 `capacity` 키가 없다. `runs/` 목록이 그대로다.
- 대역: `_context`(`side_effect` 래퍼), `_upkeep`(호출 금지 대역).

### `test_pause_before_model_resume_has_no_checkpoint_grace` (행 579–591)
- 성질: 모델 프로세스가 재개되기 전에 정지가 오면, 체크포인트 유예 없이 곧바로 정지 요청이 참이 된다.
- 준비: 기본 상태. `_call_steps(queue[0])`의 첫 `next`로 호출 인자를 받는다.
- 실행: `model_process(arguments, resume=False)` 안에서 공개 `control(..., "pause")`, `_apply_inbox(pump=False)`, `_upkeep()`.
- 단언: `arguments["should_stop"]()`이 참이다(메시지: 멈춘 모델은 체크포인트 유예를 위해 재개되지 않는다). 끝에 `status="stopped"` 결과를 보내면 생성기가 `StopIteration`으로 끝난다.
- 대역: 없음. 실제 `WindowsJob`을 만들되 재개하지 않는다.
- 비고: 실제 외부 자원: Windows Job(`model_process`). 종료 대기 상한 10초.

### `test_execution_effort_is_its_pinned_profile_effort_not_the_current_setting` (행 593–608)
- 성질: 실행의 추론 노력(effort)은 고정된 프로필 판본의 값이지 현재 설정값이 아니다.
- 준비: 기본 상태. 큐 첫 행동 역할의 프로필 참조에서 `ai.effort`를 읽고, `instance.config.effort`를 그와 다른 `EFFORTS` 값으로 바꾼다(주석: 노력만 바꾸는 `configure`는 고정 판본을 그대로 둔다).
- 실행: `_call_steps(action)`의 첫 `next`.
- 단언: 호출 인자의 `effort`와 등록된 실행의 `effort`가 모두 고정값이다. 끝에 생성기를 닫는다.
- 대역: 없음.

### `test_running_model_stops_immediately_after_public_pause` (행 610–625)
- 성질: 실행 중인 모델은 공개 정지가 적용되면 즉시 정지 요청을 받고 실행이 `stopping`이 된다.
- 준비: 기본 상태. `_call_steps`의 첫 `next`로 인자를 받는다.
- 실행: `model_process(arguments, resume=True)` 안에서 먼저 `should_stop()`이 거짓임을 보고, 공개 `control(..., "pause")`, `_apply_inbox(pump=False)`, `_upkeep()`.
- 단언: 정지 전 `should_stop()`이 거짓이고 뒤에는 참이다. 실행의 `status`가 `stopping`이다. 끝에 `status="stopped"` 결과를 보내면 `StopIteration`.
- 대역: 없음. 실제 Windows Job을 재개해 돌린다.
- 비고: 실제 외부 자원: Windows Job. `test_pause_before_model_resume_has_no_checkpoint_grace`와 달리 모델이 이미 실행 중이다.

### `test_installation_polling_is_bounded_and_forced_checks_still_detect_edits` (행 627–636)
- 성질: 설치 판본 점검은 주기적 호출에서 해시 계산 횟수가 제한되고, 강제 점검은 바뀐 설치를 찾아 인스턴스를 멈춘다.
- 준비: 기본 상태.
- 실행: `_installation_manifest`를 현재 판본을 돌려주도록 패치하고 `_check_installation()`을 10번. 다음에 `{"sha256": "changed"}`를 돌려주도록 패치하고 `_check_installation(force=True)`.
- 단언: `_check_installation`이 호출 가능하다. 10번 모두 참이고 판본 계산 호출이 1번 이하다. 강제 점검은 거짓이고 상태가 `paused`가 된다.
- 대역: `_installation_manifest` 패치.
- 비고: 제품은 비강제 점검을 단조 시계 1초 간격으로 제한하고, 불일치 시 종결되지 않은 인스턴스를 `paused`로 바꾼다(`engine.py` `_check_installation`, 행 687–700).

### `test_construction_and_status_leave_installation_and_artifact_bytes_to_run_and_check` (행 638–654)
- 성질: 엔진 생성과 `status`는 설치 판본 해시, 프롬프트 문서 적재, 산출물 바이트 읽기를 하지 않는다. 그것들은 `run`과 `check`의 몫이다.
- 준비: 기본 상태에 공개 `source` 제어로 원자료 `note.txt`를 넣고 `process_controls`.
- 실행: `ResearchEngine._installation_manifest`와 `engine_module.all_prompt_documents`를 호출 금지 대역으로 패치한 채 새 엔진을 만들고, 그 저장소의 `read`와 `read_many`도 호출 금지로 패치한 채 `status()`.
- 단언: 원자료가 들어갔다. 금지 대역이 한 번도 불리지 않는다. `submission_checks.status`가 `not_evaluated`다. 검사 영역 `record_storage`의 `checked_invariants`가 `"artifact presence and length"`를 담는다.
- 대역: 네 가지 호출 금지 대역(`AssertionError` side_effect).

### `test_installation_change_cannot_reopen_a_terminal_instance` (행 656–664)
- 성질: 종결된 인스턴스는 설치 변경을 발견해도 `paused`로 되살아나지 않는다.
- 준비: 기본 상태. `_installation`에 먼저 접근해 적재 판본의 해시를 계산시킨다.
- 실행: `subTest`로 `terminal` ∈ {`closed`, `completed`}마다 상태를 그 값으로 두고, 판본을 `changed`로 패치해 `_check_installation(force=True)`.
- 단언: 반환이 거짓이고 상태가 종결값 그대로다.
- 대역: `_installation_manifest` 패치.
- 비고: `subTest` 케이스는 `closed`, `completed`다.

### `test_initial_wait_ends_on_new_independent_user_decision` (행 666–670)
- 성질: 이름은 초기 대기가 새 사용자 결정으로 끝난다고 말한다. 단언은 새 사용자 결정 이벤트를 참조로 더한 계획이 배정 가능하다는 것만 본다.
- 준비: `startup()`의 계획 행동. `_lifecycle_event("user_decision_applied", decision_id="new-policy")`를 만들어 그 ID를 행동의 `event_refs`에 더한다.
- 실행: `_dispatchable(action)`.
- 단언: 참이다.
- 대역: 없음.
- 비고: 제품에는 초기 준비 대기 기제가 없다(`test_active_charter_update_can_plan_and_preserves_its_event`의 비고 참조). 이 시험은 그런 대기가 다시 생겨 계획을 막는 것을 방지하는 회귀 방지다. 이벤트를 더하기 전에도 같은 결과인지는 이 시험이 보지 않는다.

### `test_empty_or_failed_initial_preparation_does_not_wait_forever` (행 672–678)
- 성질: 앞선 준비가 빈 출력으로 받아들여졌든 미완으로 끝났든, 계획은 영원히 기다리지 않고 배정 가능하다.
- 준비: `startup()`의 계획 행동.
- 실행: `subTest`로 `outcome` ∈ {`output_accepted`, `execution_incomplete`}마다 그 결과로 끝난 준비 실행 `E`를 넣고 `_dispatchable(action)`.
- 단언: 두 경우 모두 참이다.
- 대역: 없음.
- 비고: `subTest` 케이스는 두 결과값이다. 앞 시험과 같은 회귀 방지 성격이다.

### `test_plan_receives_public_running_preparation_without_private_output` (행 680–697)
- 성질: 계획의 입력은 진행 중인 준비를 공개 필드로 받고, 그 준비의 비공개 출력은 받지 않는다.
- 준비: 기본 상태에 `running` 준비 실행 `E`를 넣는다. 목표·정책 개정 1, 사유 `"derive last-car recurrence"`, 그리고 행동의 `repair.previous_output`에 `{"secret": "private draft"}`를 둔다.
- 실행: `_context({"role": "research_plan"}, root/"plan")`, 이어서 `research_plan` 프로필로 `prepare_role_input(...)`.
- 단언: 맞춘 문맥의 `ongoing_work`에서 `execution_id == "E"`인 행이 1개이고, 그 행의 `(goal_revision, policy_revision)`이 `(1, 1)`, 사유가 원문 그대로, `input_snapshot`이 현재 head다. 그 행 목록의 문자열에 `"private draft"`가 없다.
- 대역: 없음.
- 비고: 주석은 끝나지 않은 준비가 상태에서 만든 `ongoing_work` 행으로 계획에 닿는다고 적는다.

### `test_task_result_materialization_batches_reads_without_losing_files` (행 699–715)
- 성질: 계획 입력을 만들 때 과제 결과 파일 여러 개는 Git 읽기 한 번으로 묶여 모두 온전히 복원된다.
- 준비: 기본 상태에 12개의 이진 산출물(각 257바이트)과 그 목록을 결과로 가진 활성 과제 `T`를 넣고 `_save(files)`로 게시한다.
- 실행: 저장소의 `_git`을 `wraps`로 감시하며 `_context({"role": "research_plan"}, root/"results-plan")`.
- 단언: `cat-file` 호출이 정확히 1번이다. 문맥의 첫 과제 결과에 파일이 12개이고, 각 파일의 `local_path` 바이트가 원래 바이트와 같다.
- 대역: `_git` 감시(`wraps`, 동작은 실제).
- 비고: 실제 Git 자식 프로세스를 쓴다.

### `test_repeated_idle_save_does_not_publish_but_real_changes_do` (행 717–729)
- 성질: 바뀐 것이 없는 저장은 새 커밋을 만들지 않고, 상태 변경이나 산출물 추가는 새 커밋을 만든다.
- 준비: 기본 상태.
- 실행: `_save()` 두 번, `cycles`를 1 늘려 `_save()`, 산출물 하나를 넣어 `_save({...})`.
- 단언: 두 번째 저장 뒤 head가 같다. 상태를 바꾼 저장 뒤 head가 다르다. 산출물 저장 뒤 head가 또 다르고, 그 산출물을 읽으면 `b"\x00\xff"`다.
- 대역: 없음.

### `test_reopened_idle_engine_does_not_publish_again` (행 731–737)
- 성질: 같은 상태를 다시 연 엔진의 저장은 새 커밋을 만들지 않는다.
- 준비: 기본 상태에서 `_save()` 뒤 head.
- 실행: 새 `ResearchEngine`으로 다시 열어 `_save()`.
- 단언: 다시 연 엔진의 head가 앞 head와 같다.
- 대역: 없음.

### `test_merged_user_requests_keep_all_request_references` (행 739–744)
- 성질: 합쳐진 계획 요청은 두 사용자 요청의 참조를 모두 보존한다.
- 준비: 기본 상태에서 큐를 비운다.
- 실행: `_enqueue("research_plan", ..., requested_by="UC-first")`, 이어서 `requested_by="UC-second"`.
- 단언: 큐 첫 행동의 `requested_by_refs`가 `["UC-first", "UC-second"]`다.
- 대역: 없음.

### `test_readiness_is_derived_and_changes_with_contract_review_evidence` (행 746–763)
- 성질: 과제 준비도는 저장되지 않는 파생값이다. 다시 계산해도 같은 입력에서는 같고 게시를 만들지 않으며, 계약 검토 증거가 생기면 바뀐다.
- 준비: 기본 상태에 새 `ScriptedRunner`.
- 실행: `run(max_steps=1)`(준비 실행이 과제를 제안), `_save`, `_refresh_readiness`, `_save`, 다시 `run(max_steps=1)`(계약 검토).
- 단언: 첫 과제의 준비도가 `ready`가 아니다. 다시 계산해도 같은 값이고 저장이 head를 바꾸지 않는다. 두 번째 실행 뒤 과제 상태가 `planned`, 준비도가 `ready`로 바뀌어 처음 값과 다르다. 저장소에서 읽은 런타임에 `task_readiness` 키가 없다.
- 대역: `ScriptedRunner`.
- 비고: 실제 Windows Job 자식 프로세스를 쓴다.

## 관계

- **다른 층의 같은 기능.** 공개 초기화의 수명 제어와 영속은 `test_lifecycle_engine`의 `PublicLifecycleTests`와 `PersistedConnections`가, 초기 의도 연결은 `test_initial_intent_connection`이, 능력 관측 묶음은 `test_initialization_probe_batch`가, 관찰 설정 입장은 `test_observation_admission`이 검사한다. 체크포인트와 실시간 관찰은 `test_checkpoint_persistence`와 `test_live_observation`의 몫이다. `ScriptedRunner`와 `formal_ok`로 목표 판정까지 모는 목적 시나리오는 `purpose_fixtures`를 쓰는 `test_purpose_engine`이 맡는다.
- **픽스처 의존.** `research_fixtures.activate`와 `install_adapter_fixture`(공개 경로), `restore_template`와 `state_fixtures.active_instance`(2단), `engine_fixtures.routing_engine`(메모리 엔진), `runner_fixtures.ScriptedRunner`(실제 로컬 Job 안의 합성 역할 출력).
- **이 모듈에만 있는 도우미.** `formal_fail`, `efficiency_instance`와 `EFFICIENCY_CONFIG`, `EngineTests.make`와 `active`, `QueuedPreparationTests.model_process`, `open`, `startup`. `research_fixtures` docstring은 `EngineTests.active`를 `restore_template`의 기본 사용형으로 가리킨다.
- **겹치거나 보완하는 시험.** `test_active_charter_update_can_plan_and_preserves_its_event`, `test_initial_wait_ends_on_new_independent_user_decision`, `test_empty_or_failed_initial_preparation_does_not_wait_forever`는 모두 초기 준비 대기 기제가 없는 현재 제품에서 `_dispatchable`이 참임을 보는 회귀 방지다. `test_pause_before_model_resume_has_no_checkpoint_grace`와 `test_running_model_stops_immediately_after_public_pause`는 정지의 두 시점(재개 전·실행 중)을 나눠 본다. `SourceIntegrityCheckTests`와 `test_construction_and_status_leave_installation_and_artifact_bytes_to_run_and_check`는 "전체 바이트는 `check`, 존재·길이는 `run`과 제어"라는 역할 분담을 양쪽에서 확인한다. `test_repeated_idle_save_does_not_publish_but_real_changes_do`와 `test_reopened_idle_engine_does_not_publish_again`은 게시 멱등성을 한 엔진과 재적재 엔진에서 각각 본다.
