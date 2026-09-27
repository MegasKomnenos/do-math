# 결과: TORG-A(시험 재편, foundation 조각)

이 문서는 do-math 정리 구현에서 TORG-A 작업자가 한 일을 통합자에게 넘기는 반환이다. 형식은 공통 계약 7절을 따른다. 경로는 따로 적지 않으면 `C:/math-worktrees/c-torga/.claude/skills/do-math/scripts/` 기준이다.

## 1. 브랜치, 커밋, 바꾼 파일

- worktree는 `C:/math-worktrees/c-torga`, 브랜치는 `c-torga`다. 시작점은 통합 브랜치 `c-int`의 `cdcaffd`다. push, 병합, 다른 브랜치 조작은 하지 않았다.
- 커밋은 셋이다. 내용 변경과 파일 이동을 나눠, 이동한 시험의 본문이 바뀌지 않았음을 커밋 단위로 확인할 수 있게 했다.
  - `be3b27b` TORG-A 1: 시험 내용 정리. TSA-01, TSA-03, TSA-07, TSA-08, TSA-10과 통합자 추가 항목이 여기 있다. 모듈 이름은 바꾸지 않았다.
  - `912c4ad` TORG-A 2: 모듈 20개의 이름만 바꿨다(`git mv`와 `SHARDS['foundation']`). 파일 내용은 바꾸지 않았으므로 Git이 모두 100% 이름 변경으로 기록한다.
  - `a51ce02` TORG-A 3: 모듈 사이의 시험 이동(TSA-02). 클래스와 메서드를 옮기고, 비게 된 모듈 10개를 지우고, 새 모듈 6개를 만들었다.

바꾼 파일은 다음과 같다.

- **제품**(`do_math/`): 없음.
- **문서**: 없음. `시험-지침.md`는 파견문대로 고치지 않았다.
- **픽스처 모듈**: 없음. 픽스처 모듈의 docstring은 foundation 시험 모듈을 가리키지 않아 고칠 곳이 없었다(3.4절).
- **시험 기반**: `test_categories.py`의 `SHARDS['foundation']` 항목만 고쳤다. foundation 모듈은 74개에서 69개가 되었다.
- **시험 모듈**(모두 `tests/`)
  - 이름을 바꾼 모듈 20개와 지운 모듈 10개, 새 모듈 6개는 3.1절의 표에 있다.
  - 이름은 그대로 두고 시험을 받거나 내용을 고친 모듈: test_academic, test_claude_adapter, test_context_store, test_contracts, test_git_store, test_knowledge, test_machine_scheduling, test_model_metadata_boundary, test_observations, test_planning, test_questions, test_repair_execution, test_reporting, test_repository, test_review_cycle, test_state_checks, test_task_scope, test_test_runner, test_trust_continuation, test_unicode_flow, test_formal_input_manifest

## 2. ID별 처분

- **TSA-01 — 구현함.**
  - foundation의 `git init` 자식 프로세스 25곳을 `research_fixtures.git_init`으로 바꿨다. 17개 파일에 걸쳐 있다(옛 이름으로 test_boundary_repairs, test_execution_observation_profile, test_formal_input_manifest, test_git_store 2곳, test_performance_save, test_redesign_ACTIVITIES, test_redesign_CONTRACTS 4곳, test_redesign_EVIDENCE_walkthroughs, test_redesign_KNOWLEDGE, test_redesign_PROFILES, test_redesign_STORAGE, test_redesign_SURFACE 3곳, test_redesign_TASKS, test_reporting 2곳, test_repository 2곳, test_storage_validation, test_unicode_flow).
  - `--object-format=sha256`이 필요한 곳은 자식 프로세스를 유지했다. 현재 좌표는 `tests/test_git_store.py:395`, `tests/test_git_store.py:472`의 sha256 분기, `tests/test_family_records.py:918`이다. `test_git_store`의 Git 배관 대조 시험은 한 줄로 sha1과 sha256을 모두 만들었다. 그래서 sha1일 때만 `git_init`을 쓰도록 분기를 나눴다.
  - `test_unicode_flow`의 setUp은 더 이상 저장소를 만들지 않는다. 저장소를 쓰는 두 시험만 `git_init(self.root / "repository")`로 만든다.
  - 쓸모가 없어진 `import subprocess`는 지웠다. 파일 안에서 다른 곳이 쓰는 경우는 남겼다.
- **TSA-02 — 구현함(1단계와 2단계 모두).**
  - 계기 이름 모듈 25개를 모두 없앴다. 성질이나 제품 모듈의 이름으로 바꾸거나, 성질별 모듈로 흩었다. 대응은 3.1절의 표에 있다.
  - 계기 이름 클래스는 성질 이름으로 바꿨다. `WalkthroughRepairs`, `AuditTests`, `AuditRepairTests`, `Audit1Tests`, `KnowledgeAudit2`, `FollowupRegressions`, `FollowupTests`, `AuditWorkflowTests`, `AuditPersistenceTests`, `AuditRecoveryTests`, `*RedesignTests`, `SourceCorrectionRegressionTest`가 여기 든다. 두 모듈에 같은 이름으로 있던 `WalkthroughRepairs`는 없어졌다. 대응은 3.2절에 있다.
  - 계기 번호와 계기 접두어가 붙은 시험 이름도 성질 이름으로 바꿨다. `test_03`~`test_11`, `test_audit_*`, `test_audit2_*`, `v5`, `version_five`가 여기 든다. 목록은 3.3절에 있다.
  - 옮길 때 시험의 단언과 시작 상태는 바꾸지 않았다. 예외는 하나다. `StorageValueTests`의 한 시험은 이제 다른 모듈로 간 도우미 `storage_state([])`를 불렀다. 그래서 그 반환값과 같은 리터럴로 바꿔 적었다(7절).
  - 통합표 1단계 정정이 행선지가 빠졌다고 한 두 클래스의 행선지는 다음과 같다. `ImpactReviewRetryTests`는 `test_impact_review`로, `ToolDiscoveryTests`는 새 모듈 `test_installation_discovery`로 갔다.
  - 통합표 1단계 목록과 행선지가 다른 곳이 있다. 모두 파견문의 원칙("이 성질의 시험은 어디 있는가"가 이름으로 드러난다)을 따른 결과다.
    - `test_boundary_repairs`는 `test_repository`에 합치지 않았다. 제품 모듈 `payloads.py`의 성질만 검사하므로 `test_payloads`로 이름을 바꿨다.
    - `test_performance_repairs`의 `SubmissionShapeWorkTests`는 `test_contracts`가 아니라 `test_submission_checks`로 갔다. 검사 대상이 `contracts.py`의 스키마가 아니라 `submission.py`의 모양 검사이기 때문이다.
    - `test_repair_plan`과 두 `test_walkthrough_*` 모듈은 제안대로 시험 단위로 흩었다.
- **TSA-03 — 구현함.** 통합표의 정정을 따랐다. (l)(m)(n)은 중복이 아니므로 두었다. 부분 중복 4쌍 (a)(b)(h)(k)는 지울 쪽에만 있던 단언을 옮긴 뒤 지웠다. 지운 시험은 14개다. 옮긴 단언과 그 행선지는 다음과 같다(시험 이름은 커밋 1 시점의 이름).
  - (a) `test_redesign_STORAGE`의 세 시험을 지웠다. NFD≠NFC 대조는 `test_unicode_flow.test_exact_json_keeps_nfd_and_distinct_mathematical_keys`로, 리스트 순서 보존은 `StorageValueTests.test_value_validation_and_serialization_keep_the_same_domain`으로 옮겼다. `test_repository`의 비유한 값 부분은 지웠다. 그 가운데 `-inf`는 남길 시험의 거부 목록에 없었으므로 더했다. 남은 시험은 `test_duplicate_json_keys_are_rejected_on_load`로 이름을 바꿨다.
  - (b) `test_unicode_flow.test_initial_immutable_input_is_one_exact_utf8_representation`을 지웠다. `immutable_input`의 정확한 모양(`text`, `sha256`, `bytes`)은 STORAGE의 `test_original_input_bytes_are_the_exact_working_text`로 옮겼다.
  - (c) CONTRACTS의 `test_plan_schema_has_one_population_disposition_list`를 지웠다. 처분 방식은 TSA-07 항목에 적었다.
  - (d) `test_contracts`의 `independent_confirmation` 부분을 지웠다. 스키마 단계의 거부 단언은 CONTRACTS의 `test_knowledge_change_cannot_self_confirm_its_impact`로 옮겼다(`jsonschema.validate`로 `extension_schema` 직접 확인). 남은 시험은 `test_knowledge_change_requires_a_declared_impact_set`으로 이름을 바꿨다.
  - (e) `test_performance_save.test_stale_parent_loser_does_not_publish`를 지웠다. "현재 head가 승자다"라는 단언은 `test_repository.test_stale_save_conflict_does_not_overwrite`로 옮겼다.
  - (f) `ClockResolutionTests.test_elapsed_time_regression_outside_resolution_interval_is_rejected`를 지웠다. 남길 시험의 부분집합이다.
  - (g) `test_academic_file_evidence_is_resolved_at_snapshot_not_from_its_name`을 지웠다. 해석기 없는 기록 거부는 `test_resolution_is_current_only_while_its_real_evidence_is_unchanged`로 옮겼다.
  - (h) `test_external_rejection_resolution_requires_a_current_structured_record`를 지웠다. 봉인되지 않은 손 기록 행이 반박을 해소하지 않는다는 단언은 `test_academic.Tests.test_rejection_needs_a_structured_current_resolution`으로 옮겼다. 원래 흐름을 흔들지 않도록 사본 runtime 위에서 단언한다.
  - (i)(j) KNOWLEDGE의 `test_environment_scoped_invalidation`과 `test_environment_recovery_restores_only_environment_suspension`을 지웠다.
  - (k) audit1의 `test_profile_binds_source_unit_and_current_execution`과 다른 시험의 위조 출처 부분을 지웠다. 그 시험은 `test_checkpoint_counter_rule_ignores_counters_from_another_source`로 이름을 바꿨다. `tracker.rules` 동일성과 `_replace_rules`의 `observation_rules_rejected`는 `test_shared_contract_rejects_forged_source_and_other_execution_subject`로 옮겼다. 원래 시험은 좁은 프로필 결속 때문에 거부되던 규칙으로 교체를 시도했다. 남길 시험의 프로필은 전체 계약을 결속하므로 그 규칙이 받아들여진다. 그래서 교체 규칙으로 다른 실행을 가리키는 규칙을 썼다. 교체 경로도 같은 실행 결속 검사를 거친다는 성질은 그대로 단언한다. 교체 뒤 규칙이 바뀌지 않았다는 단언도 더했다.
  - (o) `test_preparation_failure_and_pause_have_distinct_terminal_outcomes`를 지웠다. cancelled 분기와 `input_preparation.stage` 단언은 `test_11_preparation_attempt_is_durable_before_input_and_failure`(지금 `StoredExecutionTests.test_preparation_attempt_is_durable_before_input_and_failure`)로 옮겼다.
  - (p) ACTIVITIES의 `test_stdio_mcp_server_submits_and_reads_a_published_receipt`를 지웠다.
- **TSA-07 — 구현함(1항목은 이미 되어 있음).** 통합표 3절의 모순은 파견문대로 TSA-07의 방향으로 풀었다.
  - 옛 필드 부재를 하나씩 단언하던 곳을 지웠다. `test_contracts`의 `selections`·`deferred`, CONTRACTS의 `completion_criteria`·`decision`이 여기 든다. 대신 `test_contracts.ContractTests.test_every_role_has_closed_schema`를 일반형으로 넓혔다. 이제 모든 역할 스키마의 모든 깊이에서, `properties`를 선언한 객체가 `additionalProperties: false`인지 본다. 넓히기 전에 현재 스키마가 이 조건을 모두 만족함을 확인했다(위반 0건).
  - 구 설정 목록 두 곳은 `test_configuration.ConfigurationTests.test_configuration_outside_the_current_contract_is_rejected_before_creating_an_instance` 하나로 줄였다. 이 시험은 발명한 키 `invented_setting`과 `session_limits: None`을 쓰고, 인스턴스를 만들기 전에 거부된다는 단언을 유지한다. PROFILES의 `test_unused_observation_settings_are_rejected_at_configuration_boundary`는 지웠다. 그 시험이 보던 오류 문구("outside the stored configuration section: <키>")는 새 시험이 단언한다.
  - 지운 시험: `test_session_slots_has_only_git_authority`, STORAGE의 `test_flat_governance_is_not_a_second_storage_authority`, `test_removed_task_readiness_view_is_an_unregistered_family`.
  - 지운 단언: OBSERVATION의 `execution_events` 행과 지운 연산자 부분 시험, `utf8_base64` 부재 단언 세 줄.
  - `--goal-kind` 시험은 발명한 옵션 `--invented-option`과 JSON 필드 `invented_option`으로 바꾸고, `test_unknown_init_option_has_no_repository_or_workspace_effect`로 이름을 바꿨다.
  - 구 개념 시험 이름 셋을 바꿨다. `…_not_sqlite`, `…without_a_legacy_projection`, `…legacy_criteria…`다. `test_unicode_flow`의 `…schema_two`·`…schema_one`도 바꿨다(3.3절).
  - `test_planning.py:119-120`의 구 조건 상태 값 단언은 이미 없다. `ec2c1da`(K-저장)가 그 시험을 지웠다(`git log -S"for obsolete in ('blocked'"`).
- **TSA-08 — 구현함.**
  - 인라인 존재 단언을 지웠다(`hasattr`, `callable(getattr(...))`, `inspect.signature`). 위치는 test_claude_adapter, test_git_store 2곳, ACTIVITIES 3곳, CONTRACTS 3곳, KNOWLEDGE 3곳, PROFILES 6곳, TASKS 2곳이다.
  - 세 도우미 `module()`, `integration()`, `profiles()`(`ProfileTests`의 것)를 지우고 모듈 머리의 일반 import와 모듈 참조로 바꿨다. `api = self.profiles()`와 `module = self.integration()`처럼 지역 별칭에 담던 곳도 모듈 이름을 직접 쓰게 했다. 문자열 상수가 바뀌지 않았음을 AST로 대조했다. `Audit1Tests.profiles(**changes)`는 존재 확인이 아니라 픽스처이므로 남겼다.
  - 존재만 보던 시험 `test_public_candidate_and_record_evidence_apis_exist`를 지웠다.
  - 이 정리로 쓸모없어진 import(`importlib`, `inspect`, 지역 `ModelRunner`)도 지웠다.
- **TSA-10 — 구현함.** K-저장(`ec2c1da`)이 이미 신탁 셋과 그 비교 시험 둘을 지우고 고정값 시험까지 지운 상태였다. 남은 것은 `old_rules_digest` 신탁과 그 비교 시험이었다.
  - 신탁과 비교 시험을 지우고, 세 digest 공식을 값 영역별 고정값으로 고정했다(`STATE_DIGESTS`, `JSON_DIGESTS`, `RULE_DIGESTS`).
  - 고정값이 덮는 값 영역은 다음과 같다. 두 유니코드 정규형, 이스케이프, 중첩, 빈 값, 안전 정수 경계, 소수·음의 0·큰 수(`json_digest`), 관찰 규칙의 원문 JSON(`_raw_json`)이다.
  - 모듈은 `test_file_io`나 `test_repository`에 합치지 않고 `test_json_digests`로 이름을 바꿨다. 두 digest 소유자(`repository`, `file_io`)와 관찰 규칙 digest를 한 성질로 함께 보는 모듈이라, 합치면 한 성질이 두 모듈로 갈라지기 때문이다.
- **통합자 추가 항목(`repository_double`) — 구현함.** `test_redesign_PROFILES`(지금 `test_supervisor_recovery`)의 대역은 이미 `create_autospec(ResearchRepository, instance=True)` 기반이었다. 그런데 `ResearchRepository.git_dir`는 property라 autospec이 값을 채우지 않는다. 그래서 사적 `_store` 대역을 지우고 `repo.git_dir = root`로 공개 속성을 준다. docstring도 공개 `git_dir`를 적게 고쳤다. `test_recovery_never_restarts_with_unknown_local_termination`과 `test_recovery_requires_current_profile_capability_before_reservation` 두 ID가 통과했다(5절).

## 3. 새 공유 정의, 지운 공개 이름, 바뀐 이름

### 3.1 모듈(옛 이름 → 새 이름)

새 공유 정의는 없다. 픽스처 모듈은 고치지 않았다. 한 모듈 전용 도우미는 그것을 쓰는 시험과 함께 옮겼다. 두 모듈이 한 도우미를 쓰게 되는 분할은 하지 않았다(7절).

이름만 바꾼 모듈(커밋 2에서 `git mv`, 커밋 3에서 시험을 주고받음):

| 옛 이름 | 새 이름 | 커밋 3에서 달라진 것 |
|---|---|---|
| test_boundary_repairs | test_payloads | docstring |
| test_digest_characterization | test_json_digests | 없음 |
| test_current_contract | test_configuration | 클래스 `ConfigurationTests` |
| test_control_transport_io | test_control_transport | `ControlPreviewTests`, `ControlTransportTests`를 받음 |
| test_state_contract_registration | test_state_contract | `RegisteredValidatorTests`, `StateContractValidationTests`를 받음 |
| test_delegation_storage | test_delegations | 거버넌스의 위임 시험과 `ReplacementAuthorityTests`를 받음 |
| test_impact_bundle | test_impact_review | `ImpactReviewTests`, `ImpactReviewRetryTests`를 받음 |
| test_redesign_ACTIVITIES | test_execution_lifecycle | 제어 전송 시험 3개와 병렬 호출 시험 1개를 내보냄 |
| test_redesign_GOVERNANCE | test_governance | 학술·목표 보증·질문·위임·외부 작업 시험을 내보내고 의도 가져오기 시험을 받음 |
| test_redesign_LIFECYCLE | test_lifecycle_gates | `ConversationLeaseTests`를 받음 |
| test_redesign_PROFILES | test_execution_profiles | 감독 복구 시험 5개를 내보내고 `ResourceWaitTests`를 받음 |
| test_redesign_STORAGE | test_family_records | `ProducerStorageContractTests`를 받음 |
| test_redesign_TASKS | test_task_contracts | 반복 시험을 한 클래스로 모으고 walkthrough 시험을 받음 |
| test_redesign_EVIDENCE_walkthroughs | test_design_walkthroughs | `PriorityVectorTests`를 받음 |
| test_redesign_EVIDENCE_host | test_owned_job_children | docstring |
| test_redesign_REVIEWS | test_review_policy | 재평가와 봉인 재생 시험을 내보냄 |
| test_redesign_KNOWLEDGE | test_knowledge_storage | 지식 기록 시험과 재평가 시험을 내보냄 |
| test_redesign_CONTRACTS | test_submission_checks | 통합 묶음·역할 스키마·영향 검토 시험을 내보냄 |
| test_redesign_SURFACE | test_retention | 역할 입력·상태 검사·보고·CLI·상태 계약 시험을 내보냄 |
| test_repair_plan | test_goal_audit | 자원 대기·준비 복사 시험을 내보내고 목표 보증 시험을 받음 |

지운 모듈(시험을 모두 옮김):

| 옛 모듈 | 시험의 행선지 |
|---|---|
| test_observation_audit1 | test_observations(`SelfCheckControlBindingTests`) |
| test_execution_observation_profile | test_observations(`ExecutionObservationProfileTests`) |
| test_redesign_OBSERVATION | test_observations(`ObservationRuleTests`) |
| test_performance_save | test_repository(`SaveWithStateTests`) |
| test_performance_repairs | test_repository(`CandidateCopyTests`, `StorageValueTests`, `SealedArtifactReadTests`), test_git_store(`SnapshotMetadataTests`), test_state_checks(`BatchedInspectionTests`), test_planning(`ArtifactConditionTests`), test_impact_review(`ImpactReviewRetryTests`), test_submission_checks(`SubmissionShapeTests`), test_installation_discovery(`ToolDiscoveryTests`) |
| test_storage_validation | test_state_contract(`RegisteredValidatorTests`) |
| test_control_preview | test_control_transport(`ControlPreviewTests`) |
| test_redesign_EVIDENCE | test_design_walkthroughs(`PriorityVectorTests`), test_family_records(`ProducerStorageContractTests`) |
| test_walkthrough_repairs | test_governance(`IntentImportTests` 8), test_planning(`ReadinessConditionTests` 4), test_task_contracts(`TaskDependencyTests` 2), test_model_metadata_boundary, test_review_policy, test_knowledge, test_context_store(각 1) |
| test_walkthrough_contract_repairs | test_repair_execution(`InstallationRepairRoutingTests` 7), test_task_contracts(`AssessmentApplicationTests` 4, `TaskContractsTest` 1), test_cli_surface, test_lifecycle_gates(`ConversationLeaseTests`), test_submission_checks, test_knowledge, test_trust_continuation(`PublicationTrustIdentityTests`)(각 1) |

새 모듈:

| 새 모듈 | 담은 것 |
|---|---|
| test_integration_bundles | CONTRACTS의 `DefaultBundleTests`와 묶음 적용 시험 15개(`BundleApplicationTests`) |
| test_reassessment | REVIEWS의 `ReassessmentGitTests`·`AssessmentReassessmentTests`, KNOWLEDGE의 `KnowledgeReassessmentConnection`과 재평가 시험 7개(`DomainReassessmentTests`) |
| test_supervisor_recovery | PROFILES의 감독·복구 시험 5개와 그 도우미 `repository_double`, `capability_adapter`(`SupervisorRecoveryTests`) |
| test_installation_discovery | `ToolDiscoveryTests` |
| test_external_operations | 거버넌스의 외부 작업 시험 5개(`ExternalOperationTests`)와 `ExternalScopeConsumerTests` |
| test_cli_surface | CLI 조회 출처 시험과 알 수 없는 init 옵션 시험(`CliSurfaceTests`) |

그 밖에 이름이 그대로인 모듈이 받은 클래스는 다음과 같다.

- test_academic: `AcademicConsumerTests`, `AcademicGovernanceTests`
- test_context_store: `RoleInputTests`(SURFACE 17개와 walkthrough 1개)
- test_contracts: `ContractTests`에 역할 스키마 시험 5개
- test_goal_audit: `GoalAssuranceTests`
- test_knowledge: `KnowledgeRecordTests`(옛 `KnowledgeRedesign`)와 `KnowledgeTests`에 2개
- test_machine_scheduling: `ModelCallTests`
- test_questions: `GovernanceQuestionTests`
- test_reporting: `StatusSnapshotTests`와 `ReportingTests`에 1개
- test_review_cycle: `SealedReplayTests`
- test_state_checks: `BatchedInspectionTests`, `CheckAreaTests`

### 3.2 클래스(옛 이름 → 새 이름)

- `AuditTests`(audit1) → `SelfCheckControlBindingTests`, `ObservationRedesignTests` → `ObservationRuleTests`
- CONTRACTS: `AuditRepairTests` → `CheckHistoryTests`, `ContractBoundaryTests` → `SubmissionBoundaryTests`(남은 제출 시험), 나머지는 `BundleApplicationTests`·`ContractTests`·`StateContractValidationTests`
- `SubmissionShapeWorkTests` → `SubmissionShapeTests`, `SealedArtifactTests` → `SealedArtifactReadTests`와 `ArtifactConditionTests`
- `SurfaceRedesignTests` → `RetentionTests`(남은 보존 시험), 나머지는 `RoleInputTests`·`CheckAreaTests`·`StatusSnapshotTests`·`CliSurfaceTests`·`StateContractValidationTests`
- KNOWLEDGE: `KnowledgeRedesign` → `KnowledgeRecordTests`, `KnowledgeAudit2` → `KnowledgeRoundtripTests`와 `DomainReassessmentTests`, `KnowledgeRawSource` → `ExactSourceTests`
- `ReviewRedesignTests` → `ReviewScopeTests`, `Audit1Tests` → `MachineAndProviderEvidenceTests`, `GoalAuditFlowRepairTests` → `GoalAuditSlotTests`
- `DispatchResourceRepairTests` → `ResourceWaitTests`와 `ReportingTests`, `ReadinessCopyRepairTests` → `ReadinessCopyTests`
- GOVERNANCE: `AuditRepairTests` → `ImportApprovalTests`, `RegisteredOwnerTests`, `GoalAssuranceTests`, `DelegationJudgmentTests`, `DomainGovernanceTests`로 나눔. `GovernanceRedesignTests` → `DomainGovernanceTests`, `ExternalOperationTests`, `DelegationJudgmentTests`로 나눔.
- ACTIVITIES: `ProviderAndParallelTests` → `ProviderAdmissionTests`, `AuditRecoveryTests` → `StoredExecutionTests`
- LIFECYCLE: `LifecycleRedesignTests` → `ActivationGateTests`, `FollowupTests` → `LifecycleTransitionTests`
- TASKS: `AuditWorkflowTests` → `TaskContractReviewTests`, `AuditPersistenceTests` → `TaskContractStorageTests`, `FollowupRegressions` → `TaskReadinessTests`(반복 시험 5개는 `RepetitionLineageTests`로), `RepetitionProductionTests` → `RepetitionLineageTests`
- `StorageRedesignTests` → `FamilyRecordStorageTests`, `CurrentContractTests` → `ConfigurationTests`, `SourceCorrectionRegressionTest` → `SourceCorrectionTest`
- 두 `WalkthroughRepairs` → 시험마다 3.1절의 행선지 클래스

### 3.3 시험 메서드(옛 이름 → 새 이름)

- ACTIVITIES `test_03_real_recovery_record_completion_round_trip` → `test_recovery_record_completion_round_trips_through_git`, `test_04_…`·`test_06_…`·`test_07_…`·`test_11_…` → 번호만 뺀 이름
- SURFACE `test_audit_*`(5개)와 `test_audit2_impact_review_evidence_is_required_direct_input` → 접두어를 뺀 이름
- `test_v5_scope_waiver_…` → `test_scope_waiver_…`, `test_actual_constructor_review_and_ready_population_use_v5_contract` → `…use_the_task_contract`, `test_missing_v5_scope_…` → `test_missing_scope_…`, `test_planning_routes_v5_tasks_…` → `test_planning_routes_tasks_…`, `test_version_five_persists_family_files_and_reconstructs_views` → `test_state_persists_as_family_files_and_reconstructs_views`
- TSA-07: `test_provider_mixin_uses_git_runtime_reservation_not_sqlite` → `test_provider_admission_reserves_runtime_capacity_and_settles_after_the_job_is_empty`, `test_plan_receiver_uses_the_authored_dispositions_without_a_legacy_projection` → `test_plan_receiver_records_model_decisions_without_changing_the_authored_dispositions`, `test_v5_transfer_approval_does_not_copy_legacy_criteria_or_close_source` → `test_task_scope_transfer_decision_changes_no_task_and_requires_the_current_contract`, `test_git_save_reload_has_plain_exact_json_and_schema_two` → `test_git_save_reload_stores_the_record_as_exact_json`, `test_schema_one_record_is_rejected_without_automatic_conversion` → `test_record_envelope_with_an_unknown_field_is_rejected_without_conversion`, `test_removed_goal_kind_option_…` → `test_unknown_init_option_…`, `test_retired_configuration_…` → `test_configuration_outside_the_current_contract_…`
- TSA-03: `test_duplicate_json_and_nonfinite_values_are_rejected` → `test_duplicate_json_keys_are_rejected_on_load`, `test_knowledge_change_carries_declared_impact_without_producer_confirmation` → `test_knowledge_change_requires_a_declared_impact_set`, `test_profile_cannot_register_nonexistent_source_or_mix_counter_sources` → `test_checkpoint_counter_rule_ignores_counters_from_another_source`
- TSA-10: `test_observation_rule_digest_matches_removed_formula` → `test_observation_rule_digests_stay_fixed`, 새 `test_state_value_digests_stay_fixed`, `test_json_digests_stay_fixed`

### 3.4 지운 공개 이름

- 시험 모듈 도우미: `test_claude_adapter.ClaudeTests.module`, `test_redesign_CONTRACTS.ContractBoundaryTests.integration`, `test_redesign_PROFILES.ProfileTests.profiles`, `test_digest_characterization.old_rules_digest`
- 3.1절의 옛 모듈 이름 전부와 3.2절의 옛 클래스 이름 전부. 재수출은 두지 않았다. 옛 모듈을 import하는 곳은 없다(`grep` 결과 0건, 5절).
- `research_fixtures` docstring의 한 모듈 전용 빌드 목록은 foundation 모듈을 가리키지 않아 고치지 않았다. 다른 픽스처 모듈의 docstring도 foundation 시험 모듈이나 옮긴 클래스를 가리키지 않는다.

## 4. 필요한 문서 변경

- **`tests/시험-지침.md`(DOC)**: 바꿀 문장은 없다. 이 문서는 모듈 목록을 옮겨 적지 않고 `SHARDS`를 정본으로 가리킨다. 4.1의 "같은 성질의 시험이 이미 있는지 먼저 찾는다"는 이제 모듈 이름으로 찾을 수 있다.
- **graphify 그래프(`.claude/skills/do-math/` 탐색용)**: 옛 시험 모듈 이름을 담고 있을 수 있다. 프로젝트 규칙상 사용자가 명시적으로 요청할 때만 갱신하므로 손대지 않았다.
- **역사 기록**: `docs/do-math/implementation-v5/traceability.json`(동결), `docs/do-math/initialization-repairs-20260925.json`, `docs/do-math/boundary-repairs-2026-09-25/`의 보관 실행 기록은 옛 모듈 이름을 담는다. 모두 역사 기록이므로 고치지 않는다.

## 5. 실행한 시험

실행은 모두 `scripts/run_tests.py`로 했다. 시험 프로세스는 한 번에 하나만 띄웠고, 조각 실행(`--shard`)과 전체 실행은 하지 않았다. `DO_MATH_KNOWLEDGE_TEST_LEAN`에는 계약 6절의 경로를 주었다. 그래서 lean 격리 클래스도 대상 안에서 실제로 돌았다.

**기계적 확인**(커밋 3 시점)

- `scripts/tests`의 모든 `.py`와 `test_categories.py`를 `python -m py_compile`로 확인했다. 오류는 없다.
- 시험 모듈 128개와 픽스처 모듈 9개를 모두 `importlib.import_module`로 적재했다. 실패는 없다.
- 옛 모듈 이름으로 import하는 곳은 `grep` 결과 0건이다. 옛 모듈 이름을 담은 곳은 역사 기록 JSON과 지운 `__pycache__`뿐이다(4절).
- `test_categories.unregistered_modules('tests')`의 결과는 `([], [])`다. `run_tests.py --list`(전체)는 1842개를 냈다. 조각별로 foundation 1012, lifecycle 389, host 152, review 145, research 84, academic 60이다.
- 재편한 모듈마다, 모듈 전역에서 읽지만 정의하지 않는 이름을 찾았다. 결과는 0건이다.

**시험 ID 수의 전후 대조**(`run_tests.py --list --shard foundation`)

| 시점 | ID 수 | 차이 |
|---|---|---|
| 시작 `cdcaffd` | 1029 | |
| 커밋 1 `be3b27b` | 1012 | −17 = TSA-03 −14, TSA-07 −4, TSA-08 −1, TSA-10 +2(신탁 비교 1개를 고정값 시험 3개로) |
| 커밋 2 `912c4ad` | 1012 | 0(모듈 이름만 바꿈) |
| 커밋 3 `a51ce02` | 1012 | 0 |

커밋 1과 커밋 3의 ID를 메서드 이름으로 대조했다. 3.3절에서 바꾼 이름을 반영하면 1012개가 1:1로 대응한다. 한쪽에만 있는 메서드도, 이름이 겹쳐 대응이 모호한 메서드도 없다. 시험 ID의 `모듈.클래스` 부분만 3.1절과 3.2절대로 바뀌었다.

**실행 결과**

1. 커밋 1의 확인: 커밋 1에서 고친 29개 모듈을 돌렸다(`python scripts/run_tests.py test_academic test_boundary_repairs test_claude_adapter test_contracts test_current_contract test_digest_characterization test_execution_observation_profile test_formal_input_manifest test_git_store test_model_metadata_boundary test_observation_audit1 test_performance_repairs test_performance_save test_redesign_ACTIVITIES test_redesign_CONTRACTS test_redesign_EVIDENCE_walkthroughs test_redesign_GOVERNANCE test_redesign_KNOWLEDGE test_redesign_LIFECYCLE test_redesign_OBSERVATION test_redesign_PROFILES test_redesign_STORAGE test_redesign_SURFACE test_redesign_TASKS test_reporting test_repository test_storage_validation test_unicode_flow test_walkthrough_contract_repairs`).
   - 결과: 선택 598, 통과 596, 실패 2. 125초가 걸렸다.
   - 실패 2건은 `test_redesign_PROFILES.ProfileTests.test_recovery_never_restarts_with_unknown_local_termination`과 `…test_recovery_requires_current_profile_capability_before_reservation`이다. 이 실패는 변경 전부터 있었다. 통합자가 알린 `cdcaffd`의 문제와 같은 ID와 같은 원인이다. `repository_double`을 고친 뒤 두 ID만 돌려 2개 모두 통과했다.
2. 커밋 3의 확인: 커밋 3에서 시험을 주거나 받거나 이름·docstring이 바뀐 43개 모듈을 돌렸다(test_academic test_cli_surface test_configuration test_context_store test_contracts test_control_transport test_delegations test_design_walkthroughs test_execution_lifecycle test_execution_profiles test_external_operations test_family_records test_git_store test_goal_audit test_governance test_impact_review test_installation_discovery test_integration_bundles test_knowledge test_knowledge_storage test_lifecycle_gates test_machine_scheduling test_model_metadata_boundary test_observations test_owned_job_children test_payloads test_planning test_questions test_reassessment test_repair_execution test_reporting test_repository test_retention test_review_cycle test_review_policy test_state_checks test_state_contract test_submission_checks test_supervisor_recovery test_task_contracts test_task_scope test_test_runner test_trust_continuation).
   - 결과: 선택 815, 통과 813, 건너뜀 1, 실패 1. 148초가 걸렸다. 선택에는 격리 실행 셋(`lean`·`resource` 표지 클래스)이 포함된다.
   - 실패 1건은 `test_test_runner.RunnerTests.test_positional_ids_select_a_module_class_or_method_without_prefix_collisions`다. 이 작업이 만든 실패다. 이 자기시험은 지운 모듈 `test_redesign_EVIDENCE`를 접두어 충돌 예로 썼다. 그래서 `test_knowledge`로 바꿨는데, 처음 쓴 단언("행에 `test_knowledge_`가 없다")이 `test_knowledge_input_…` 같은 메서드 이름에도 걸렸다. 단언을 "모든 행의 모듈이 정확히 `test_knowledge`다"로 고쳤다(빈 결과가 통과하지 않도록 `rows`가 비지 않았음도 단언한다). 그 ID만 다시 돌려 통과했다.
   - 건너뜀 1건은 `test_context_store.ContextStoreTests.test_outside_symlink_is_reported_when_supported`다. 이 기계에서 심볼릭 링크를 만들 권한이 없다(`WinError 1314`). 환경 원인이며, 이 작업이 옮기거나 고친 시험이 아니다.

**돌리지 않은 관련 시험**

- 커밋 3에서 바뀌지 않은 foundation 모듈 26개는 커밋 3 뒤에 돌리지 않았다. 그 가운데 test_claude_adapter, test_formal_input_manifest, test_json_digests(옛 test_digest_characterization), test_unicode_flow는 커밋 1에서 고쳤고 확인 1에서 통과했다. 나머지 22개는 이 작업이 고치지 않았다: test_budget, test_claude_stream, test_codex_adapter, test_completion_settlement, test_contract_checks, test_decision_basis, test_environment_validation, test_execution_window, test_file_io, test_knowledge_import_engine, test_knowledge_io, test_model_runner, test_preparation_cache, test_provider_final_contract, test_query_records, test_reading_map, test_reference_catalog, test_relation_dependencies, test_review_scope_wire, test_revision_obligations, test_scholarly, test_standalone.
- 다른 조각은 돌리지 않았다. 다른 조각의 시험 모듈은 foundation 시험 모듈을 import하지 않는다(`grep` 0건). 이 작업은 픽스처 모듈과 제품을 고치지 않았으므로, 다른 조각에 닿는 변경은 `SHARDS`뿐이다. 그 확인은 위의 `--list` 전체 실행과 `unregistered_modules`로 했다.
- 시간 효과(TSA-01의 절감량)는 재지 않았다. 파견문이 조각 실행을 금하고, 통합표가 확정 방법을 조각 전후 쌍 비교로 정했기 때문이다. 통합자가 조각 시간을 잴 때 확정된다.

## 6. 기능이나 시험 범위가 바뀐 것

- **TSA-03의 중복 시험 14개 삭제.**
  - 이유: 같은 제품 함수를 같은 입력으로 지나 같은 결과를 단언했다.
  - 잃는 것: 없다. 지운 쪽에만 있던 단언은 2절대로 남긴 시험에 옮겼다.
  - 얻는 것: 한 성질을 고칠 때 고칠 시험이 하나다.
  - (k)의 교체 규칙은 입력이 다르다. 원래 시험은 좁은 프로필 결속을 벗어나는 규칙을 썼다. 옮긴 단언은 다른 실행을 가리키는 규칙을 쓴다. 두 입력 모두 "교체도 실행 결속 검사를 거친다"를 본다. 좁은 프로필 결속 자체의 거부는 남은 `test_missing_profile_observability_contract_is_not_support`와 `ExecutionObservationProfileTests`가 본다.
- **TSA-07: 옛 이름 나열을 닫힌 스키마의 일반형 시험으로 바꿈.**
  - 잃는 것: 옛 이름(`selections`, `deferred`, `completion_criteria`, `decision`, 구 설정 9종, 구 관찰 설정 3종, `execution_events`, `utf8_base64`, `task_readiness`, 평탄 `goal`, `sqlite3`)을 이름으로 나열한 회귀 검사.
  - 얻는 것: 역할 스키마의 모든 깊이의 객체가 닫혀 있는지 보는 검사. 위 옛 이름이 다시 들어오는 회귀는 이 일반형 검사와 설정·저장 계약의 닫힌 검사(`invented_setting`, 미등록 가족 거부 `test_unknown_family_and_malformed_map_do_not_become_singletons`)가 잡는다.
  - 전제: 닫힌 스키마가 유지되는 동안만 성립한다.
- **TSA-10: 신탁 비교를 고정값 비교로 바꿈.**
  - 잃는 것: 없다. 신탁은 공식을 다시 적은 것이었고, 고정값은 같은 값 영역에서 공식 변화를 똑같이 잡는다.
  - 얻는 것: 지운 이름을 가리키는 주석이 없어지고, 저장 digest가 바뀌면 어느 값에서 바뀌었는지 바로 보인다.
  - 조건: 고정값이 `STATE_DIGESTS`·`JSON_DIGESTS`·`RULE_DIGESTS`의 값 영역을 덮는 동안 성립한다.
- **TSA-08, TSA-01, TSA-02**: 검사 범위는 바뀌지 않는다. 존재 단언은 바로 다음 호출이 같은 실패를 낸다. `git_init`은 `git init -q`로 만든 빈 `.git`의 복사다. 이동 전후 시험 메서드는 1:1로 대응한다(5절).

## 7. 막힌 지점, 접근을 바꾼 지점, 예상과 달랐던 결과

- **내용 변경과 이동을 커밋으로 나눴다.** 먼저 시험 내용만 고치고(커밋 1) 그 모듈들을 돌렸다. 그다음 이름만 바꾸고(커밋 2), 마지막에 시험을 옮겼다(커밋 3). 이동은 AST로 클래스와 메서드의 원문 줄을 그대로 잘라 붙이는 도구로 했다. 도구는 다음을 막았다: 옮긴 코드가 쓰는 모듈 수준 도우미가 두 행선지에 걸리는 경우, 남는 쪽이 옮겨 간 도우미를 쓰는 경우, 행선지에서 같은 이름이 다른 정의로 묶이는 경우, 남는 메서드를 부르는 메서드만 옮기는 경우. 이동 뒤 시험 ID 수와 메서드 이름의 1:1 대응을 확인했다.
- **도우미 한 개는 리터럴로 바꿔 적었다.** 파견문은 픽스처 모듈의 docstring만 고치게 한다. `test_performance_repairs.storage_state`는 `BatchedInspectionTests`(→ test_state_checks)와 `StorageValueTests`(→ test_repository)가 함께 썼다. 그래서 `StorageValueTests`의 한 호출 `storage_state([])`를 그 반환값과 같은 리터럴로 바꾸고, 도우미는 `test_state_checks`에 두었다. 다른 공유 도우미가 두 모듈에 걸리는 분할은 하지 않았다. `fixture_engine`을 쓰는 LIFECYCLE의 세 클래스를 한 모듈(`test_lifecycle_gates`)에 둔 것도 이 때문이다.
- **TSA-10은 앞선 커널이 이미 절반을 했다.** `ec2c1da`가 신탁 셋, 신탁 비교 시험 둘, 고정값 시험까지 지운 상태였다. 그래서 남은 신탁 하나를 지우고, 통합표의 결과(값 영역별 고정값)를 현재 원문 위에 다시 세웠다. 이전 고정값 두 개(`ee49…`, `2927…`)는 현재 공식으로도 같은 값이 나왔다. 그래서 공식이 바뀌어서가 아니라 판본 표지 정리와 함께 지워진 것으로 보인다.
- **TSA-03 (k)의 교체 입력을 바꿨다.** 원래 교체 규칙 `observation_rule()`은 남길 시험의 전체 계약 프로필에서 받아들여진다. 그래서 같은 실행 결속 검사를 거치는 입력(다른 실행을 가리키는 규칙)으로 바꿨다. 이 변경은 첫 실행 전에 코드를 읽고 정했다. 실행은 한 번에 통과했다.
- **TSA-07의 일반형 시험은 새로 쓰지 않고 넓혔다.** `test_every_role_has_closed_schema`가 이미 최상위 닫힘을 보고 있었다. 이를 모든 깊이로 넓혀 옛 필드 부재 단언의 자리를 채웠다.
- **셸 heredoc이 편집 스크립트를 깨뜨렸다.** 따옴표가 많은 Python 편집 스크립트를 heredoc으로 넘기자 bash가 따옴표 짝을 찾지 못했다. 이런 편집은 파일로 쓴 스크립트로 했다.
- **작문 독해 절차는 적용하지 않았다.** 이 반환은 프로젝트 지침의 작문 품질 계약을 따라 썼다. 그러나 `write-for-reader`의 `writing_flow.py`는 합의·상태 파일을 새로 쓴다. 파견문은 worktree 밖 쓰기를 이 산출 파일 하나로 제한하므로 그 도구는 돌리지 않았다. 기억 노드도 파견문대로 만들지 않았다.
- **통합자 추가 항목은 첫 실행에서 드러났다.** 커밋 1의 확인 실행에서 두 시험이 실패했다. 통합자가 알린 두 ID와 같았다(`recovery_waiting`, "installation maintenance is already active"). `repository_double`을 고친 뒤 두 ID만 다시 돌려 통과했다.

## 8. 다른 그룹 범위에서 발견한 문제

- **TORG-B, 새 모듈 이름의 충돌 가능성.** 이 작업이 foundation에 새로 만든 이름은 다음과 같다. 합칠 때 TORG-B가 다른 조각에 같은 이름을 만들었는지 확인해야 한다.
  - 이름을 바꾼 모듈: test_payloads, test_json_digests, test_configuration, test_control_transport, test_state_contract, test_delegations, test_impact_review, test_execution_lifecycle, test_governance, test_lifecycle_gates, test_execution_profiles, test_family_records, test_task_contracts, test_design_walkthroughs, test_owned_job_children, test_review_policy, test_knowledge_storage, test_submission_checks, test_retention, test_goal_audit
  - 새 모듈: test_integration_bundles, test_reassessment, test_supervisor_recovery, test_installation_discovery, test_external_operations, test_cli_surface

  특히 겹칠 만한 이름이 둘 있다. `test_governance`는 lifecycle 조각의 `test_governance_engine`과 가깝다. `test_supervisor_recovery`는 host 조각의 `test_operator`와 성질이 가깝다.
- **TORG-B, 감독 복구 시험의 위치.** `test_supervisor_recovery`의 시험은 `scheduled_operator`의 복구를 검사한다. host 조각의 `test_operator`도 같은 제품 모듈을 검사한다. 조각을 넘는 이동은 이 작업의 범위가 아니어서 foundation에 새 모듈로 두었다. 두 모듈을 합칠지는 통합자가 정할 일이다. 외부 작업(`test_external_operations`와 host의 `test_external`), 제어 전송(`test_control_transport`와 host의 `test_background_processes`)도 같은 질문이 남는다.
- **foundation 안의 남은 표기.** `test_knowledge_io`의 docstring("v5 authoritative families")과 `test_task_contracts.TaskContractStorageTests.setUp`의 임시 폴더 접두어 `tasks-audit1-`에는 옛 판본·계기 표기가 남아 있다. 시험 이름이나 모듈 조직이 아니어서 고치지 않았다.
- **시험 함수 안의 쓰이지 않는 지역 import.** 원래부터 있던 것들이다. 예: `test_academic.py:86`의 `seal_profile`, `profile_ref`, `BOUNDARY`, 옮긴 walkthrough 시험의 `goal_audit_host`. 시험 본문을 바꾸지 않는다는 원칙에 따라 남겼다. 모듈 수준의 쓰이지 않는 import는 재편한 모듈에서 지웠다(test_goal_audit, test_review_policy, test_knowledge_storage, test_state_checks, test_contracts).
