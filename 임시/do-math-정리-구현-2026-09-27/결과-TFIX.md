# 결과: TFIX(시험 기반·픽스처)

이 문서는 do-math 정리 구현에서 TFIX 그룹이 한 일을 통합자와 뒤이은 TORG 작업자에게 넘기는 반환이다. 형식은 공통 계약 7절을 따른다. 경로는 따로 적지 않으면 `C:/math-worktrees/c-tfix/.claude/skills/do-math/scripts/` 기준이다.

## 1. 브랜치, 커밋, 바꾼 파일

- worktree `C:/math-worktrees/c-tfix`, 브랜치 `c-tfix`. 시작점은 통합 브랜치 `c-int`의 `be07df8`이다.
- 마지막 커밋: `df32cca` "do-math 정리 TFIX: 시험 도우미를 픽스처 모듈로 모아 시험 모듈 사이의 결합을 끊음". push, 병합, 다른 브랜치 조작은 하지 않았다.
- 규모: 105개 파일, 4569행 추가, 4128행 삭제. 추가분 가운데 약 3200행은 새 픽스처 모듈로 옮긴 정의와 그 모듈 docstring이다.

바꾼 파일은 다음과 같다.

- **제품**(`do_math/`): 없음.
- **시험 기반**
  - 새 픽스처 모듈 7개: `tests/engine_fixtures.py`, `tests/runner_fixtures.py`, `tests/purpose_fixtures.py`, `tests/record_fixtures.py`, `tests/knowledge_fixtures.py`, `tests/review_fixtures.py`, `tests/provider_fixtures.py`
  - 고친 기존 픽스처 모듈: `tests/research_fixtures.py`, `tests/state_fixtures.py`
  - `test_categories.py`: 격리 라벨 정리(TSB-08)
- **시험 모듈**(96개, 모두 `tests/`): test_academic_engine, test_academic_preparation, test_approved_five_repairs, test_checkpoint_persistence, test_claude_adapter, test_claude_stream, test_cli_advanced, test_codex_adapter, test_connection_repairs, test_contract_checks, test_control_shapes, test_controls, test_currentness_recovery, test_decision_basis, test_diagnosed_installation_recovery, test_document_followup, test_efficiency, test_engine, test_execution_observation_profile, test_external, test_formal, test_formal_input_manifest, test_formal_runtime, test_governance_engine, test_host_resources, test_impact_bundle, test_initial_intent_connection, test_initialization_efficiency, test_initialization_probe_batch, test_initialization_review_repairs, test_input_recovery, test_knowledge, test_knowledge_import_engine, test_knowledge_io, test_lean_preview, test_lifecycle_currentness, test_lifecycle_engine, test_machine_parallel, test_machine_scheduling, test_model_assessment_flow, test_model_metadata_boundary, test_model_runner, test_native_final_submission, test_observation_admission, test_observation_audit1, test_observations, test_operator, test_performance_repairs, test_planning, test_preflight, test_provider_final_contract, test_provider_recovery, test_provider_wait, test_purpose_engine, test_query_records, test_question_flow, test_redesign_CONTRACTS, test_redesign_ENGINE, test_redesign_EVIDENCE, test_redesign_EVIDENCE_walkthroughs, test_redesign_GOVERNANCE, test_redesign_KNOWLEDGE, test_redesign_LIFECYCLE, test_redesign_OBSERVATION, test_redesign_PROFILES, test_redesign_REVIEWS, test_redesign_STORAGE, test_redesign_SURFACE, test_redesign_TASKS, test_relation_dependencies, test_repair_execution, test_repair_plan, test_reporting, test_research_recovery, test_research_reliability, test_review_cycle, test_review_engine, test_review_research, test_revision_obligations, test_run_feedback, test_session_scheduler, test_six_connections, test_state_checks, test_static_review_repairs, test_stop_flags, test_submission_boundaries, test_submission_flow, test_submission_tools, test_task_scope, test_test_runner, test_trust_continuation, test_walkthrough_contract_repairs, test_walkthrough_followup, test_walkthrough_repairs
- **문서**: `이음새-정본.md`의 시험 도우미 행 세 개를 더했다. `시험-지침.md`와 `test_reading_map.py`는 파견문대로 고치지 않았다.
- **worktree 밖**: 파견문이 지운다고 정한 빈 디렉터리 `C:/math/.claude/skills/do-math/scripts/tests/fixtures/`를 지웠다. 파일이 없고 Git이 추적하지 않던 폴더다.

## 2. ID별 처분

- **TSB-01 — 구현함.**
  - 시험 모듈이 서로에게서 빌려 쓰던 도우미를 모두 픽스처 모듈로 옮겼다. 픽스처 모듈이 시험 모듈을 import하던 역방향 간선 두 개(`state_fixtures`→`test_lifecycle_engine.FakeEngine`, `research_fixtures`→`test_engine.ScriptedRunner`)도 없어졌다.
  - 시작 시점에는 시험 모듈끼리의 import가 267곳, 빌려 주는 시험 모듈이 45개, 빌려 쓰는 모듈이 81개였다. 지금은 1곳이 남는다. `test_reading_map.py:11`(`from test_purpose_engine import ActiveStateHarness`)이며, DOC 소유라 고치지 않았다(4절, 8절).
  - `FakeEngine.approve(SimpleNamespace(...))`와 `FakeEngine.verification(engine, ...)`처럼 메서드를 묶이지 않은 함수로 부르던 곳은 모듈 함수 `engine_fixtures.approve_contract`와 `engine_fixtures.formal_verification`으로 바꿨다. `FakeEngine`도 이 두 함수를 쓴다.
  - `research_fixtures` docstring에 픽스처 모듈의 소유 규칙과 빌드 19개의 목록을 적었다(TSB-13). `시험-지침.md` 4.3의 갱신은 4절에 적었다.
- **TSB-06 — 구현함(`test_reading_map` 쪽은 4절의 문서 변경으로 남김).**
  - `ActiveStateHarness`를 지웠다. `test_document_followup`은 `ActivatedPurposeHarness.make_active`를 쓴다. `ActivatedPurposeHarness` docstring의 `ActiveStateHarness.make` 언급도 고쳤다.
  - 저장소 생성만 하던 `git init` 자식 프로세스를 `git_init`으로 바꿨다. 대상은 검증 파일이 센 영역 안의 호출 전부다. `research_fixtures.new_instance`, `PurposeHarness.setUp`, `test_initial_intent_connection`, `test_initialization_efficiency`, `test_preflight`, `test_provider_wait`, `test_host_resources`(2곳), `test_machine_parallel`, `test_operator`(2곳), `test_review_engine`, `test_submission_flow`, `test_submission_tools`가 여기에 든다.
  - 옮긴 픽스처 안의 호출도 바꿨다. `KnowledgeRoundtripHarness`(옛 `KnowledgeAudit2.setUp`), `start_query_repository`(옛 `QueryRecordTests.setUp`), `start_repair_host`(옛 `RepairExecutionTests.setUp`), `test_impact_bundle`, `test_performance_repairs`가 여기에 든다. 이 가운데 foundation 조각의 것은 TSA-01(TORG)과 겹친다.
  - 자식 프로세스나 Git 작업 트리가 검사 대상인 `test_background_processes`와 `test_formal`은 그대로 두었다. foundation 조각에 남은 `git init` 호출(`test_repository`, `test_redesign_STORAGE`, `test_redesign_SURFACE` 등 약 20곳)은 TSA-01에 남긴다.
- **TSB-08 — 구현함.** `test_categories.LABELS`는 `('lean', 'resource')`다. `isolation_for`의 `in_process` 되돌림 분기와 docstring 문장을 지웠다. `CallManagerTests`의 클래스 표지와 메서드 표지 8개를 지우고, 실제 스레드 종료나 Windows Job을 다루는 세 메서드(`test_close_sets_every_stop_flag_and_fails_pending_start_callbacks`, `test_failed_start_publication_never_resumes_the_real_job`, `test_real_job_cancellation_uses_owner_judgment_and_collects_once`)에만 `resource`를 붙였다. 격리되는 시험의 집합은 전과 같다. `test_test_runner`의 자기시험은 "라벨이 상속되고 메서드 라벨이 클래스 라벨을 이긴다"를 `lean`과 `resource`로 단언하게 고쳤다. `run_tests.py`에는 같은 철자의 지역 변수만 있고 라벨 처리가 없어 고치지 않았다.
- **TSB-13 — 구현함.** `research_fixtures` docstring은 이제 빌드를 "둘"이 아니라 19개로 적는다. 공유 빌드 6개는 키워드와 만드는 상태를 적고, 한 모듈 전용 빌드 13개는 이름과 모듈을 적는다. 복원마다 경로 키 캐시를 비운다는 문장은 TSB-14를 따라 지웠다.
- **TSB-14 — 구현함.**
  - 확인 1. `forget_repository_caches`가 비우던 캐시는 `VERIFIED_ARTIFACTS`와 `_VALIDATED_READS` 둘이었다. 앞의 것은 키 `(git_dir, path, sha256)`에 봉인 sha256을 담는다(`do_math/repository.py:43-51`). 뒤의 것은 키 `(git_dir, head OID, contract)`에 커밋 OID를 담는다(`repository.py:98-125, 247-248`). 둘 다 내용 식별을 키에 담는다. 이 함수가 비우지 않던 캐시도 모두 확인했다. `_ISSUED_INPUTS`의 키는 읽은 바이트의 sha256이다(`submission.py:125-132`). `planning._VALID_ARTIFACTS`의 키는 (판정 함수, 경로, sha256)이다(`planning.py:565`). `_ARTIFACT_FACTS`는 게시 계보를 따른다.
  - 확인 2. 디스크 바이트를 훼손하고 탐지를 단언하는 시험은 `test_submission_flow.py:451`과 `test_native_final_submission.py:166` 둘이다. 둘 다 `patch.dict(... VERIFIED_ARTIFACTS, clear=True)`로 스스로 캐시를 비운다. 다른 곳은 `grep`으로 찾지 못했다.
  - 그래서 `forget_repository_caches`와 `_Template.restore` 안의 호출을 지웠다. `test_purpose_engine`의 템플릿 자기시험에서 `repository._VALIDATED_READS`를 단언하던 두 줄도 지웠다.
  - 통합표는 고정 묶음 이름 두 개(`BA-history-input`, `BA-partial-input`)를 `new_id('BA')`로 바꾸라고 했다. 이 변경은 STO-16 뒤로 필요가 없어져 하지 않았다(7절).
- **TSB-15 — 구현함.** `test_approved_five_repairs`의 `INPUT_RECOVERY_CONFIG`와 `restore_input_recovery_state`, 효과 없던 `patch.object(InputRecoveryPublicTests, 'setUp', ...)`을 지웠다. 같은 일을 하는 정의는 `state_fixtures`의 `ACTIVE_CONFIG`, `active_repository()`, `start_active_copy(test)` 하나로 모았다. 호출자 네 곳이 이것을 쓴다. `test_approved_five_repairs`의 `NativeRepairTests.setUp`(→`start_native_final`)과 `ResearchAdmissionTests`, 통합표 정정이 더한 `test_academic_engine.AcademicTaskPersistenceTests.setUp`, `test_input_recovery.InputRecoveryPublicTests.setUp`이다.
- **TSA-04 — 구현함.**
  - `test_impact_bundle._seal_review`는 이제 봉인 기록을 제품 `_stage_submission_capture`로 만든다. `ImpactReviewHarness.seal_review_fixture`를 쓰고, 그 호스트는 `bare_engine()`에 `_lifecycle_event`만 autospec으로 바꾼 것이다(TSA-06). `ImpactBundleTests`는 `ImpactReviewHarness`를 상속한다.
  - 중복 거부 시험 두 개를 지웠다. `test_review_rejects_changed_sealed_output_without_execution_output_copy`와 `test_external_premise_change_after_review_requires_a_new_judgment`다.
  - 지우기 전에 뒤의 시험에만 있던 단언을 `test_redesign_CONTRACTS`의 거부 경우 반복으로 옮겼다. 하나는 거부 뒤 runtime이 그대로라는 단언이다. 옮기면서 모든 거부 경우로 넓혔다. 다른 하나는 두 시험이 단언한 거부 사유 문구다(`stale`→"current assignment", `tampered_output`→"sealed output_ref hash differs").
- **TSA-05 — 구현함(harness 인스턴스 세 곳은 남김).**
  - 여러 곳에 사본이 있던 조립은 공유 정의 하나씩으로 모았다. 헌장과 승인 거버넌스는 `research_fixtures.charter`와 `approved_governance`로 모았다. 사본 6곳을 바꿨다. GOVERNANCE의 `initial`과 `AcademicConsumerTests.host`, SURFACE, EVIDENCE, STORAGE, decision_basis다. `FakeEngine.activate`의 헌장 literal과 `charter_record`도 같은 `charter` 위에 다시 세웠다. 지식 후보는 `knowledge_fixtures.knowledge_candidate`로, 형식 증거는 `formal_result`로, 관찰 규칙은 `research_fixtures.observation_rule`로 모았다. 사본의 값은 인자로 그대로 보존했고, 옛 함수와 새 함수의 반환이 같은지 대조했다(5절).
  - 모듈을 건너 쓰이던 TestCase 픽스처 메서드는 모두 픽스처 모듈의 함수나 harness로 옮겼다. 모듈 안에서만 쓰이던 것 가운데 GOVERNANCE `ReplacementAuthorityTests.fixture/checked`와 TASKS `AssessmentApplicationTests.fixture/apply`는 모듈 함수로 바꿨다.
  - 남은 harness 인스턴스 사용은 세 곳이다. `test_redesign_ENGINE`의 `ImpactReviewHarness()`와 `ReassessmentHarness()`, `test_redesign_STORAGE`의 `ImpactReviewHarness()`다. 이들은 시험 클래스가 아니라 소유가 명시된 harness이므로 한 클래스를 고쳐 다른 모듈이 조용히 바뀌는 문제는 없다. 다만 "TestCase 인스턴스를 픽스처로 쓴다"는 모양은 남는다(6절).
- **TSA-06 — 구현함.**
  - 믹스인 직접 인스턴스 6곳은 ENG 그룹(`78f00bb`)이 이미 `bare_engine`으로 바꿔 두었다. `test_decision_basis.py:17,59`와 `test_questions.py:59,72,89,164`다.
  - 나머지 손 대역은 모두 바꿨다.
    - `test_observations`의 `_observe_running`: `bare_engine`에 autospec 대입
    - `test_machine_scheduling` 3곳: `bare_engine`과 autospec. `SchedulerMixin`·`DecisionEngineMixin`의 비결합 호출도 결합 호출로 바꿈
    - `test_redesign_CONTRACTS`의 봉인 호스트: `bare_engine`
    - `test_walkthrough_contract_repairs`의 `_enqueue` 호스트: `bare_engine`
    - `test_reporting` 2곳과 `test_redesign_PROFILES` 2곳: `create_autospec(ResearchRepository, instance=True)`
    - `test_redesign_EVIDENCE.InputSnapshot`: autospec 저장소 `engine_fixtures.input_snapshot_store`
    - `test_performance_repairs.candidate_repository`: 실제 `ResearchRepository` 생성자
    - `test_performance_repairs.SnapshotMetadataTests.store`: `git_init`으로 만든 빈 저장소 위의 실제 `GitStateStore` 생성자에 `_git`만 autospec
  - 옮기는 대역도 같은 방식으로 만들었다(파견문의 통합 수리 교훈). 손으로 적은 `SimpleNamespace` 결과 대신 `subprocess.CompletedProcess`를 쓰고, spec 없는 `Mock()` 저장소 대신 autospec을 쓴다.

## 3. 새 공유 정의, 픽스처 모듈의 구조, 지운 공개 이름

### 3.1 픽스처 모듈의 구조

시험 모듈은 아래 모듈에서만 픽스처를 가져온다. 한 시험 모듈만 쓰는 픽스처는 그 모듈의 모듈 함수로 남긴다. 두 번째 모듈이 쓰게 되면 먼저 영역에 맞는 픽스처 모듈로 옮긴다. 이 규칙은 `research_fixtures` docstring의 "Fixture modules" 절에 적었다. 각 모듈의 docstring은 담은 것을 나열한다.

| 모듈 | 담은 것 | 옛 위치 |
|---|---|---|
| `research_fixtures` | 공통 입력(`candidate`, `review_items`, `disposition` 등), 새로 둔 **`charter`·`approved_governance`**(`charter_record`는 이 위에 다시 세움), **`Clock`·`observation_rule`·`self_check_response`**, **`cli_result`**, `git_init`, `run_cli`, 공개 활성화 `activate`, 템플릿 `restore_template`·`activated_instance` | 굵은 이름은 GOVERNANCE `charter`, OBSERVATION `Clock`·`rule`·`ObservationRedesignTests.response`, `test_input_recovery.cli`에서 옮김 |
| `state_fixtures` | 합성 활성 상태 `active_engine`·`active_instance`, 새로 둔 **`ACTIVE_CONFIG`·`active_repository`·`start_active_copy`**, `owner_calls`·`start_model_call`·`complete_academic_task` | 굵은 이름은 `test_input_recovery`의 같은 이름·`InputRecoveryPublicTests.setUp`, `test_approved_five_repairs`의 사본 |
| `engine_fixtures` | `FakeEngine`, `approve_contract`, `formal_verification`, `initialized`, `initialized_instance`, `PublicInitializationRunner`, `context_engine`, `package`, `initial_failure_engine`, `NoRepository`, `routing_engine`, `intent_import`, `intent_verdict`, `reassessment_engine`, `governance_host`, `goal_audit_host`, `start_submission_history`, `submit_history`, `start_native_final`, `native_result`, `start_repair_host`, `QUERY_INSTANCE_ID`, `start_query_repository`, `EVIDENCE_TIME`, `input_snapshot_store`, `evidence_engine`, `evidence_task`, `reviewed_task`, `plan_output`, `apply_plan`, `truth_candidate`, `accept_knowledge`, `audit_goal` | `test_lifecycle_engine`, `test_static_review_repairs`, `test_redesign_ENGINE`(`IntentConnections` 포함), `test_six_connections.PlanningConnections`, `test_governance_engine.CentralGovernanceTests`, `test_submission_flow.CentralSubmissionHistoryTests`, `test_native_final_submission`, `test_repair_execution.RepairExecutionTests`, `test_query_records.QueryRecordTests`, `test_redesign_EVIDENCE` |
| `runner_fixtures` | `ScriptedRunner`, `common`, `context_from`, `contract_checks`, `formal_ok`, `rating` | `test_engine`, `test_model_assessment_flow.rating` |
| `purpose_fixtures` | `PurposeRunner`과 그 문장·도우미(`SOURCE`, `STATEMENT`, `EXPLANATION`, `GOAL`, `NEW_GOAL`, `parse_context`, `common`, `candidate`, `theorem`, `formal_fixture`), `PurposeHarness`, `ActivatedPurposeHarness`, `AcademicRunner`, `requirement`, `SOLVED_REQUIREMENT_CRITERIA`, `drive_to`, `solved_instance`, `signed_formal_fixture`, `purpose_state`, `purpose_copy`, `CheckedRunner`, `ASSESSMENT_CONFIG`, `assessment_preparation_instance`, `prepared_assessment_engine`, `CURRENTNESS_CONFIG` | `test_purpose_engine`, `test_academic_engine`, `test_review_research`, `test_submission_boundaries`, `test_model_assessment_flow`, `test_currentness_recovery` |
| `record_fixtures` | 거버넌스(`domain_governance`, `governance_import`, `checked_import`, `audited_governance`, `applied_initial_intent`), 과제 계약(`task_contract`, `approved_task`, `approve_task`, `task_disposition`, `transfer_assessment`, `apply_assessment`, `completed_with_knowledge`, `specialist_assessment`, `withdrawable_task`, `withdraw_prepared`, `installation_repair_state`, `contract_check`, `preparation_context`, `preparation_issues`), 제출·표면(`execution_state`, `two_observation_output`, `observation_knowledge`, `research_work_context`, `surface_state`, `stored_surface_state`) | `test_redesign_GOVERNANCE`(`DomainGovernanceTests`, `AuditRepairTests`), `test_initial_intent_connection`, `test_redesign_TASKS`(`AssessmentApplicationTests` 포함), `test_research_reliability.CompletionBasisTests`, `test_walkthrough_contract_repairs.WalkthroughRepairs`, `test_task_scope.TaskScopeTests`, `test_contract_checks`, `test_redesign_STORAGE._execution_state`, `test_redesign_CONTRACTS`, `test_redesign_SURFACE` |
| `knowledge_fixtures` | `knowledge_candidate`, `formal_result`, `formal_evidence`, `seal_knowledge`, `add_knowledge`, `knowledge_graph`, `impact_declaration`, `revise_knowledge`, `activate_kind`, `verified_knowledge`, `formal_boundary_engine` | `test_knowledge`, `test_knowledge_io.activate`, `test_redesign_KNOWLEDGE`(`candidate`, `KnowledgeRedesign.verified`), `test_knowledge_import_engine.FormalBoundaryTests.host` |
| `review_fixtures` | `ReviewFakeEngine`, `grant_replacement`, `scoped_start`, `review_stage_output`, `defer_review_for_research`, `deferred_research_cycle`, `research_answer`, `reviewed_candidate`, harness `ReassessmentHarness`·`KnowledgeRoundtripHarness`·`ImpactReviewHarness` | `test_review_engine`(`FakeEngine`), `test_review_cycle`(`ReviewCycleTests.output`), `test_review_research`(`SplitReviewResearchTests.defer`, `PureResearchTests`), `test_redesign_STORAGE._reviewed_candidate`, `test_redesign_REVIEWS.AssessmentReassessmentTests`, `test_redesign_KNOWLEDGE.KnowledgeAudit2`, `test_redesign_CONTRACTS.ImpactReviewTests` |
| `provider_fixtures` | `Job`, `Execution`, `Adapter`, `mock_adapter`, `runner_with`, `FakeJob`, `claude_stream`, `CLAUDE_INIT`, `CLAUDE_RESULT`, `PROVIDER_MODEL`, `PROVIDER_LIMIT_FAILURE`, `instant`, `provider_repository`, `admit`, `report`, `finish`, `transact`, `PROFILE_CONFIG`, `host_capacity_fixture`, `actual_command`, `HTTPFixtureHandler` | `test_model_runner`, `test_codex_adapter`, `test_claude_adapter`, `test_provider_wait`(`ProviderTests.make_repository` 포함), `test_redesign_PROFILES.CONFIG`, `test_host_resources.fixture`, `test_formal.actual_command`, `test_external.H` |

`ImpactReviewHarness`, `ReassessmentHarness`, `KnowledgeRoundtripHarness`, `PurposeHarness`, `ActivatedPurposeHarness`는 시험 없는 `unittest.TestCase` 기반이다. 옛 시험 클래스(`ImpactReviewTests`, `AssessmentReassessmentTests`, `KnowledgeAudit2`, `KnowledgeRawSource`, `KnowledgeReassessmentConnection`, `ReassessmentGitTests`, `ImpactBundleTests`, `CheckpointPersistenceTests`)는 이 기반을 상속한다. setUp이 여러 속성을 채우고 시험 본문이 그 속성을 다시 대입하는 상태형 픽스처이기 때문이다. 상태 없는 픽스처는 모두 모듈 함수로 옮겼다. TestCase에 속성을 채우는 setUp형 픽스처는 `start_…(test)` 함수로 옮겼다. `start_active_copy`, `start_submission_history`, `start_native_final`, `start_query_repository`, `start_repair_host`가 그렇다.

### 3.2 이름 규칙과 바뀐 이름

옮긴 정의는 원래 이름을 쓰는 것이 기본이다. 다음 경우에만 이름을 바꿨다. 옮긴 모듈 안에서 이름이 겹치는 경우, 원래 모듈 밖에서는 뜻이 없는 이름인 경우, 메서드가 함수가 된 경우다.

| 옛 이름 | 새 이름 |
|---|---|
| `test_external.H` | `provider_fixtures.HTTPFixtureHandler` |
| `test_redesign_PROFILES.CONFIG` | `provider_fixtures.PROFILE_CONFIG` |
| `test_host_resources.fixture` | `provider_fixtures.host_capacity_fixture` |
| `test_codex_adapter._FakeJob` | `provider_fixtures.FakeJob` |
| `test_claude_adapter.stream`, `INIT`, `RESULT` | `provider_fixtures.claude_stream`, `CLAUDE_INIT`, `CLAUDE_RESULT` |
| `test_provider_wait.MODEL`, `FAILURE` | `provider_fixtures.PROVIDER_MODEL`, `PROVIDER_LIMIT_FAILURE` |
| `test_review_engine.FakeEngine` | `review_fixtures.ReviewFakeEngine`(`engine_fixtures.FakeEngine`과 구별) |
| `test_redesign_TASKS.approved_fixture`, `approve`, `task`, `disposition` | `record_fixtures.approved_task`, `approve_task`, `task_contract`, `task_disposition` |
| `test_redesign_CONTRACTS.response`, `context`, `knowledge` | `record_fixtures.two_observation_output`, `research_work_context`, `observation_knowledge` |
| `test_contract_checks.checks` | `record_fixtures.contract_check` |
| `test_knowledge.candidate`, `evidence`, `seal`, `add`, `fixture`, `declaration`, `revise` | `knowledge_fixtures.knowledge_candidate`, `formal_evidence`, `seal_knowledge`, `add_knowledge`, `knowledge_graph`, `impact_declaration`, `revise_knowledge` |
| `test_knowledge_io.activate` | `knowledge_fixtures.activate_kind` |
| `test_redesign_EVIDENCE.engine_fixture`, `task_fixture`, `plan_fixture`, `candidate`, `TIME` | `engine_fixtures.evidence_engine`, `evidence_task`, `plan_output`, `truth_candidate`, `EVIDENCE_TIME` |
| `test_redesign_EVIDENCE.InputSnapshot`(손 대역) | `engine_fixtures.input_snapshot_store`(autospec) |
| `test_redesign_OBSERVATION.rule` | `research_fixtures.observation_rule` |
| 메서드였던 픽스처 | 2절과 3.1의 새 이름(`domain_governance`, `checked_import`, `transfer_assessment`, `verified_knowledge` 등) |

### 3.3 지운 공개 이름

- `test_purpose_engine.ActiveStateHarness`(TSB-06), `test_purpose_engine.TOOLCHAIN`(쓰는 곳이 없음)
- `research_fixtures.forget_repository_caches`(TSB-14)
- `test_approved_five_repairs.INPUT_RECOVERY_CONFIG`, `restore_input_recovery_state`(TSB-15)
- `test_categories`의 라벨 `in_process`(TSB-08)
- `test_governance_engine.CentralGovernanceTests.mixin`: `host`가 옮겨 가 호출자가 없어졌다.
- `test_impact_bundle`의 시험 두 개(TSA-04)
- 옮긴 정의가 옛 모듈에 남긴 이름. 재수출은 두지 않았다. 옛 경로로 import하는 곳은 `test_reading_map` 한 곳뿐이다(5절).

## 4. 필요한 문서 변경

- **`tests/test_reading_map.py`(DOC 소유, 병합 전에 필요).** 이 파일은 지운 `ActiveStateHarness`를 import한다. `run_tests.py`는 import 오류가 하나라도 있으면 아무 시험도 돌리지 않는다. 따라서 c-tfix와 c-doc을 합친 트리는 아래 변경 없이는 시험을 돌릴 수 없다. 바꿀 줄은 네 개다.
  - 11행: `from test_purpose_engine import ActiveStateHarness` → `from purpose_fixtures import ActivatedPurposeHarness`
  - 60행: `class DocumentContextTests(ActiveStateHarness):` → `class DocumentContextTests(ActivatedPurposeHarness):`
  - 62행과 74행: `engine,_=self.make()` → `engine,_=self.make_active()`

  이 변경을 적용한 사본에서 `test_reading_map` 전체가 통과했다(5절).
- **`tests/시험-지침.md`(DOC).**
  - 4.3의 1~3단: "각 도우미의 인자와 복원 규칙은 `tests/research_fixtures.py`의 모듈 docstring에 있다"는 그대로 맞다. 준비된 빌드가 둘이라는 인상을 주는 서술이 있으면, docstring의 "What to use" 목록(공유 빌드 6개와 한 모듈 전용 빌드 13개)을 가리키게 한다.
  - 4.1: "같은 성질의 시험이 있는지 먼저 찾는다" 옆에 픽스처 소유 규칙 한 문장을 둔다. "새 시험은 다른 시험 모듈에서 도우미를 import하지 않는다. 두 모듈이 쓰는 도우미는 `research_fixtures` docstring의 'Fixture modules'에 적힌 영역별 픽스처 모듈에 둔다."
  - 4.6의 `git_init`, `run_cli` 안내는 그대로 맞다.
- **`research_fixtures` docstring(TORG).** 한 모듈 전용 빌드 13개의 목록에 시험 모듈 이름이 들어 있다. TORG가 그 빌드를 담은 모듈을 옮기거나 합치면 목록의 모듈 이름을 함께 고쳐야 한다.

## 5. 실행한 시험

기계적 확인은 다음과 같다.

- 바꾼 `.py` 전부와 `test_categories.py`, `run_tests.py`를 `python -m py_compile`로 확인했다. 오류는 없다.
- `scripts/tests`의 모든 모듈(시험 132개와 픽스처 9개)을 `importlib.import_module`로 적재했다. 실패는 `test_reading_map` 1개이며, 원인은 4절의 import다.
- 옛 경로 grep: `grep -rnE "^\s*(from test_\w+ import|import test_\w+)" scripts/tests/*.py`의 결과는 `test_reading_map.py:11`과 `test_categories` import뿐이다. `test_categories`는 시험 모듈이 아니라 시험 기반이다. 문자열 속 `test_*.` 참조는 `research_fixtures` docstring의 시험 ID 세 개뿐이다.
- 모듈 변수 읽기 점검: 각 모듈이 읽지만 정의하지 않는 전역 이름을 `symtable`로 찾았다. 결과는 0건이다.
- 동등성 대조: 옛 정의(HEAD 판본)와 새 정의의 반환을 같은 입력으로 비교했다. 다음이 같거나, 생성 ID·시각만 달랐다.
  - `domain_governance`, `governance_import`, `checked_import`, `audited_governance`, `applied_initial_intent`
  - `surface_state`, `stored_surface_state`, `approved_task`, `transfer_assessment`, `withdrawable_task`
  - `knowledge_graph`, `formal_evidence`, `knowledge_candidate`, `verified_knowledge`
  - `evidence_engine`의 instance와 runtime, `accept_knowledge`의 형식 결과, `truth_candidate`
  - `observation_rule`, `supply_observation_rules`의 규칙, 다섯 곳 헌장의 내용 해시 대상
  - `AcademicConsumerTests.host`, STORAGE `_approved_governance`, `BasisTests.setUp`

시험 실행 규칙은 다음과 같다.

- 실행은 모두 `scripts/run_tests.py`로 했고, 시험 프로세스는 한 번에 하나였다. `DO_MATH_KNOWLEDGE_TEST_LEAN`에는 계약 6절의 경로를 주었다.
- 편집 중인 worktree는 `test_reading_map`의 import 때문에 실행기가 거부한다. 그래서 worktree 안의 임시 사본(`.tfix-scratch/verify`, 커밋 전에 지움)에 skill 폴더를 복사했다. 사본의 `test_reading_map.py`에만 4절의 네 줄 변경을 적용하고 돌렸다. 두 번째 실행 뒤 사본과 worktree를 `diff -rq`로 대조했다. 차이는 `test_reading_map.py` 하나였다.

실행 결과는 다음과 같다.

1. `python scripts/run_tests.py test_reading_map test_contract_checks test_query_records test_relation_dependencies test_repair_execution test_redesign_REVIEWS test_redesign_KNOWLEDGE test_redesign_CONTRACTS test_impact_bundle test_redesign_STORAGE test_redesign_EVIDENCE test_redesign_EVIDENCE_walkthroughs test_review_cycle test_redesign_GOVERNANCE test_redesign_TASKS test_task_scope test_walkthrough_contract_repairs test_walkthrough_repairs test_repair_plan test_execution_observation_profile test_knowledge test_knowledge_io test_knowledge_import_engine test_redesign_OBSERVATION test_observations test_observation_audit1 test_machine_scheduling test_reporting test_performance_repairs test_redesign_PROFILES test_test_runner test_decision_basis test_redesign_SURFACE test_state_checks test_planning test_revision_obligations test_formal_input_manifest test_claude_adapter test_codex_adapter test_model_runner test_provider_final_contract test_claude_stream test_trust_continuation test_model_metadata_boundary`
   - 결과: 선택 792, 통과 791, 실패 1. 205초가 걸렸고, lean 격리 `PortableFormalBoundaryTests`도 포함한다.
   - 실패 1건은 `test_walkthrough_repairs.WalkthroughRepairs.test_readiness_document_tables_match_the_condition_grammar`다. 이 실패는 변경 전부터 있었다. 시작점 `be07df8`을 `git archive`로 푼 사본에서 같은 시험 ID만 돌려 똑같이 실패함을 확인했다. `후속-배정.md`의 KS→DOC 항목(과제-착수조건 포인터 문서)과 같은 원인이다.
2. 인계 확인의 나머지 모듈을 돌렸다. 명령은 `python scripts/run_tests.py test_lifecycle_engine test_connection_repairs test_input_recovery test_initialization_probe_batch test_approved_five_repairs test_academic_engine test_research_recovery test_six_connections test_submission_flow test_native_final_submission test_initialization_efficiency test_static_review_repairs test_governance_engine test_redesign_ENGINE test_research_reliability test_walkthrough_followup test_provider_wait test_initial_intent_connection test_preflight test_host_resources test_machine_parallel test_operator test_review_engine test_submission_tools test_purpose_engine test_document_followup test_checkpoint_persistence test_model_assessment_flow test_academic_preparation test_submission_boundaries test_review_research test_diagnosed_installation_recovery test_external`이다.
   - 결과: 선택 619, 통과 617, 실패 1, 건너뜀 1. 1468초가 걸렸다. 조각별로는 host 48초, lifecycle 152초, research 494초, review 480초, academic 295초다.
   - 실패 1건은 `test_static_review_repairs.InputBoundaryRepairs.test_profile_query_document_reads_cli_result_envelope`이다. 두 subTest가 모두 실패한다. 이 실패도 변경 전부터 있었다. `be07df8` 사본에서 같은 ID로 똑같이 실패했다. `references/초기화-운전.md`의 PowerShell 조회가 "선택한 프로필 ID가 조회 결과에 모두 있지 않다"로 멈춘다(8절).
   - 건너뜀 1건은 `test_approved_five_repairs.ToolchainContractTests.test_inspection_matches_actual_formal_verifier`다. 건너뛴 이유는 "portable Lean is not installed"다. 이 시험은 `formal.toolchain_root()`의 기본 경로를 읽는데, 그 경로가 검증 사본의 위치 기준이라 도구 모음이 없었다. 환경 원인이다.

돌리지 않은 관련 시험도 있다. 아래 모듈은 import 줄만 바뀌었다. 옮긴 정의를 그대로 가져오고 동작을 바꾸지 않았으므로 컴파일, 전체 import, grep으로만 확인했다(시험 지침 2절의 소비자 쪽 확인).

- test_controls, test_efficiency, test_engine, test_observation_admission, test_provider_recovery, test_stop_flags
- test_run_feedback, test_session_scheduler, test_question_flow, test_lifecycle_currentness, test_currentness_recovery
- test_initialization_review_repairs, test_redesign_LIFECYCLE, test_cli_advanced
- test_formal, test_formal_runtime, test_lean_preview(Lean 실호출 시험이며 바뀐 것은 `actual_command`의 import뿐)

## 6. 기능이나 시험 범위가 바뀐 것

- **`test_impact_bundle`의 시험 두 개 삭제(TSA-04).**
  - 이유: `test_redesign_CONTRACTS`의 `tampered_output`·`stale` 경우와 같은 성질이다.
  - 잃는 것: 없다. 두 시험의 사유 문구 단언과 runtime 불변 단언은 CONTRACTS로 옮겼고, runtime 불변은 모든 거부 경우로 넓어졌다.
  - 얻는 것: 봉인 기록 모양의 손 사본 약 45행이 제품 `_stage_submission_capture` 호출로 바뀌었다. 봉인 모양이 바뀌면 이 시험도 따라간다.
- **템플릿 복원 뒤 제품 캐시를 비우지 않음(TSB-14).**
  - 잃는 것: 복원 직후 첫 적재가 늘 전체 검증을 한다는 보장. 남는 항목은 모두 내용 식별로 키가 붙어 틀린 답을 내지 않는다.
  - 얻는 것: 시험 기반이 제품의 사적 캐시 이름을 모른다.
- **`test_purpose_engine`의 템플릿 자기시험에서 `_VALIDATED_READS` 단언 삭제(TSB-14).** 제품 사적 캐시에 대한 단언이라 지웠다. 복원본이 독립 사본이라는 나머지 단언은 그대로다.
- **harness 인스턴스 세 곳 유지(TSA-05).**
  - 대상: `test_redesign_ENGINE`의 `ImpactReviewRouting.fixture`와 재심사 요청 시험, `test_redesign_STORAGE.test_actual_impact_request_has_closed_nested_plan_schema`.
  - 이유: 두 클래스 모두 다른 픽스처와 함께 쓰는 한 메서드에서만 이 상태를 쓴다. 클래스 전체를 harness로 바꾸면 무관한 시험에 setUp 비용이 붙는다.
  - 잃는 것: TSA-05가 겨냥한 "TestCase 인스턴스를 픽스처로 쓰는 모양"이 세 곳 남는다. 이 harness는 시험 클래스가 아니므로 결합 위험은 없다.
- **`test_performance_repairs`의 저장소 대역을 실제 생성자로 바꿈(TSA-06).**
  - 잃는 것: "자식 프로세스 없음"이라는 모듈 전제. 이제 생성자마다 `git rev-parse` 한 번과 `git_init`의 복사가 든다. 모듈 docstring을 고쳤다.
  - 얻는 것: 제품 생성자가 속성을 바꾸면 대역이 즉시 실패한다.

이 밖에 옮긴 정의의 동작은 바꾸지 않았다. 확인 범위는 5절의 동등성 대조와 두 번의 인계 실행(1411개 시험)이다.

## 7. 막힌 지점, 접근을 바꾼 지점, 예상과 달랐던 결과

- **`test_reading_map` 때문에 worktree에서 실행기를 쓸 수 없었다.** TSB-06은 `ActiveStateHarness`를 지우라고 하고, 파견문은 그 사용처인 `test_reading_map.py`를 고치지 못하게 한다. `run_tests.py`는 import 오류가 하나라도 있으면 아무것도 돌리지 않는다. 재수출로 옛 이름을 남기면 결합이 숨으므로, 이름을 지우고 worktree 안 임시 사본에서만 4절의 변경을 적용해 시험했다. 통합자가 c-doc과 c-tfix를 합칠 때 이 네 줄이 필요하다.
- **고정 묶음 이름을 되돌렸다(TSB-14).** 처음에는 통합표대로 두 이름을 `new_id('BA')`로 바꿨다. 그 뒤 파견문의 STO-16 경위를 원문으로 확인했다. `_ISSUED_INPUTS`는 바이트 sha256으로 키가 붙고, `_ARTIFACT_FACTS`는 게시 계보가 같을 때만 쓰인다. 그래서 고정 이름은 더 이상 어긋남을 만들지 못한다. 필요 없는 변경이라 되돌렸다.
- **`AssessmentFlowTests.prepare_engine`은 메서드로 남겼다.** 처음에는 모듈 함수로만 바꿨다. 그런데 같은 모듈의 `RejectedAcademicAssessmentTests`가 `patch.object(self, "prepare_engine", ...)`로 이 메서드를 가로채 `AssessmentFlowTests`의 시험을 다시 돈다. 함수로만 두면 이 이음새가 사라진다. 그래서 메서드가 `purpose_fixtures.prepared_assessment_engine(self)`를 부르게 두었다. 다른 모듈(`test_academic_preparation`)은 함수를 직접 쓴다.
- **이름 바꾸기 도구의 범위 오류를 한 번 잡았다.** `test_redesign_STORAGE`에서 지역 import로 들어온 `candidate`의 호출을 파일 전체에서 바꿨다. 그 결과 `research_fixtures.candidate`를 쓰던 두 곳까지 바뀌었다. diff 검토에서 찾아 되돌렸다. 이후 이름 바꾸기는 import가 있는 함수 범위로만 한정했다. 같은 이름을 다른 모듈에서 가져오는 함수는 제외했다.
- **셸 heredoc이 백슬래시 이스케이프를 풀었다.** 편집 스크립트를 heredoc으로 넘기면 `\n`, `\\`가 실제 개행으로 바뀌는 일이 두 번 있었다. `start_repair_host`의 바이트 literal과 `test_approved_five_repairs`의 줄 이음이다. 둘 다 발견해 고쳤다. 백슬래시가 든 편집은 파일로 쓴 스크립트로 했다.
- **TSA-06의 믹스인 6곳은 이미 되어 있었다**(ENG `78f00bb`).
- **commit-harness와 작문 독해 절차는 적용하지 않았다.** 파견문이 기억 노드 생성을 금하므로 브랜치 커밋만 했다. `write-for-reader`의 `writing_flow.py`는 합의·상태 파일을 새로 쓰는데, 파견문은 worktree 밖 쓰기를 이 산출 파일 하나로 제한한다. 그래서 이 반환은 품질 계약과 에이전트 채널 규칙만 적용했고, 별도 독해 검증을 거치지 않았다.

## 8. 다른 그룹 범위에서 발견한 문제

- **DOC 또는 통합자, `test_reading_map.py`.** 4절의 네 줄 변경이 없으면 병합 트리에서 실행기가 아무 시험도 돌리지 않는다.
- **DOC, `references/초기화-운전.md`의 프로필 조회 PowerShell.** `test_static_review_repairs...test_profile_query_document_reads_cli_result_envelope`가 `be07df8`에서도 실패한다. 문서 조각이 조회 결과에서 선택한 프로필 ID를 찾지 못한다. ENG-07이 `query`의 공개 가족 이름을 바꾼 뒤 문서의 필터가 따라가지 않은 것으로 보인다. 확인은 하지 않았다.
- **DOC, 과제-착수조건 문서 표.** `test_walkthrough_repairs...test_readiness_document_tables_match_the_condition_grammar`가 `be07df8`에서 실패한다. `후속-배정.md`의 KS→DOC 항목과 같은 것이다.
- **ENG, `scheduled_operator.py:487`.** 복구 경로가 `repo._store._git_dir`로 저장소의 사적 속성을 거쳐 Git 디렉터리를 읽는다. 공개 속성 `ResearchRepository.git_dir`가 같은 값을 준다. 이 때문에 `test_redesign_PROFILES`의 autospec 저장소 대역도 사적 `_store`를 채워야 했다(`repository_double`). ENG-09와 같은 갈래다.
- **TORG, foundation 조각의 `git init` 자식 프로세스.** 약 20곳이 남아 있다(TSA-01). 옮긴 픽스처 안의 호출은 이미 `git_init`으로 바꿨다(2절 TSB-06).
- **TORG, 픽스처 소유 규칙의 유지.** 모듈을 성질별로 나누면, 지금 한 모듈 전용인 빌드나 모듈 함수가 두 모듈에 걸칠 수 있다. 그때는 옛 모듈에서 import하지 말고 영역 픽스처 모듈로 먼저 옮긴다. `research_fixtures` docstring의 한 모듈 전용 빌드 목록도 함께 고친다.
