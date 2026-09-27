# 결과: TORG-B(시험 재편, foundation 밖 조각과 시험 지침)

이 문서는 do-math 정리 구현에서 TORG-B 작업자가 한 일을 통합자에게 넘기는 반환이다. 형식은 공통 계약 7절을 따른다. 경로는 따로 적지 않으면 `C:/math-worktrees/c-torgb/.claude/skills/do-math/scripts/` 기준이다.

## 1. 브랜치, 커밋, 바꾼 파일

- worktree `C:/math-worktrees/c-torgb`, 브랜치 `c-torgb`. 시작점은 통합 브랜치 `c-int`의 `cdcaffd`다.
- 커밋은 세 개다. 마지막 커밋은 `e1e5104`이다. 앞의 둘(`6fa2a7c`, `002bdb2`)은 작업 중 커밋이다. push, 병합, 다른 브랜치 조작은 하지 않았다.
- 규모(`cdcaffd..e1e5104`): 51개 파일, 약 5500행 추가, 5650행 삭제. 대부분은 시험 클래스의 이동이다.

바꾼 파일은 다음과 같다.

- **제품**(`do_math/`): 없음.
- **시험 기반**
  - `test_categories.py`: `SHARDS`의 host·lifecycle·research·review·academic 항목만 고쳤다. foundation 항목은 그대로다.
  - 픽스처 모듈 세 개. `tests/purpose_fixtures.py`(하네스 축소, `solved_instance` 반환값), `tests/engine_fixtures.py`(`formal_check_engine` 추가), `tests/research_fixtures.py`(docstring의 빌드·모듈 이름, 미사용 import).
- **시험 모듈**
  - 지운 모듈 14개: `test_approved_five_repairs`, `test_walkthrough_followup`, `test_run_feedback`, `test_research_reliability`, `test_initialization_review_repairs`, `test_connection_repairs`, `test_six_connections`, `test_static_review_repairs`, `test_redesign_ENGINE`, `test_efficiency`, `test_initialization_efficiency`, `test_document_followup`, `test_lifecycle_currentness`, `test_currentness_recovery`(→ `test_currentness`로 이름을 바꿈).
  - 새 모듈 9개: `test_role_input`, `test_live_observation`, `test_task_completion`, `test_planning_engine`, `test_formal_engine`, `test_operation_trace`, `test_payloads`, `test_repetition`, `test_currentness`.
  - 고친 모듈: `test_academic_engine`, `test_academic_preparation`, `test_checkpoint_persistence`, `test_cli`, `test_control_shapes`, `test_controls`, `test_engine`, `test_external`, `test_formal`, `test_governance_engine`, `test_host_resources`, `test_input_recovery`, `test_lifecycle_engine`, `test_model_assessment_flow`, `test_native_final_submission`, `test_operator`, `test_provider_recovery`, `test_purpose_engine`, `test_question_flow`, `test_research_recovery`, `test_review_engine`, `test_review_research`, `test_session_scheduler`, `test_submission_boundaries`, `test_submission_flow`, `test_submission_tools`.
- **문서**: `tests/시험-지침.md`.
- **worktree 안의 기록**: 작문 독해 절차의 상태와 증거는 `--root C:/math-worktrees/c-torgb`로 worktree의 `.codex/writing-flow/do-math-guide2-20260927/`에 두었다. 이 경로는 `.gitignore` 대상이라 커밋에 없다. 작업용 임시 폴더 `.torgb-scratch/`는 반환 전에 지웠다.

## 2. ID별 처분

- **TSB-02 — 구현함.** 계기 이름 모듈 14개의 시험을 전부 소유 모듈·성질 이름의 모듈로 옮기고 합쳤다. 옮길 때 시험 본문, 픽스처 메서드, 모듈 수준 빌드는 바꾸지 않았다. 확인 방법은 5절에 있다. 예외는 모듈 이름이 바뀌어 생긴 import 별칭 네 곳이다(`common` → `role_output`·`purpose_common`, 같은 함수). 계기 이름의 클래스와 시험도 고쳤다. `test_lifecycle_engine`의 `Audit2LifecycleTests` → `LifecycleBoundaryTests`, `AuditRepairTests` → `GrantAndExternalEffectTests`이다. `test_11_`·`test_12_`·`test_13_`·`test_16_` 접두사 10건과 `test_cli`의 `test_audit_`·`test_audit2_` 접두사 9건은 지웠다. 이름 대응표는 3절에 있다. `test_lifecycle_currentness` docstring이 내용과 맞지 않던 문제는 이 모듈을 `test_currentness`로 합치면서 없어졌다.
- **TSB-03 — 구현함.**
  - `GitPurposeTests`를 지웠다. 대신 `test_purpose_engine.SolvedPurposeTests.test_public_activation_reaches_the_solution_with_archived_role_inputs`가 `restore_template(solved_instance, criteria=None)` 복원본에서 같은 단언을 한다.
  - 통합표 정정대로 `runner.work_order == ['A']`를 보존했다. 이를 위해 `solved_instance`는 `{'instance_id', 'head', 'work_order'}`를 반환한다. `work_order`는 빌드를 돈 러너의 기록이다.
  - 원래 시험의 `snapshot == engine.head`도 같은 방식으로 보존했다. 이 단언은 구동 엔진이 마지막에 게시한 헤드가 저장된 헤드와 같은지를 본다. 복원본에서 새 엔진으로는 늘 참이 되므로, 빌드가 반환한 `head`와 저장된 헤드를 대조한다.
  - 소비자 네 곳(`test_academic_engine` 2곳, `test_model_assessment_flow`, 옛 `test_lifecycle_currentness`)은 `['instance_id']`를 읽게 고쳤다. 보고 훅은 TSB-09와 함께 지웠다.
  - 두 경로의 차이: 원래 시험은 `PurposeRunner`를, 빌드는 `AcademicRunner`를 쓴다. 학술 과제가 없으면(`criteria=None`) 두 러너의 답은 같다(`purpose_fixtures.AcademicRunner.answer`).
- **TSB-04 — 구현함.** 통합표의 정정을 따랐다.
  - (a) `test_purpose_engine...test_work_budget_execution_is_not_bounded_by_operations_call_timeout`을 지웠다. 남는 쪽인 `RunWithoutDeadlineTests`(지금 `test_session_scheduler`)에 한 줄을 더했다. 지운 시험은 작업 역할 호출과 운영 역할 호출이 모두 있었음을 단언했는데, 남는 쪽은 그렇지 않았다. 그래서 `assertEqual({role in WORK_ROLES for call}, {True, False})`로 두 종류가 모두 관찰되었음을 단언한다.
  - (b) `test_purpose_engine...test_repository_enforces_snapshot_cas_and_artifact_immutability`를 지웠다. 정정대로, 이 시험의 `ValueError`는 OID 모양 검사다. OID 모양은 `test_git_store`가, CAS 충돌은 `test_repository`가 단언한다.
  - (c) `test_efficiency...test_plan_settle_waits_only_up_to_limit`을 지웠다. 남는 쪽은 `PlanSettleTests`다.
- **TSB-05 — 조건 불성립(측정값).** 5절의 계측 실행(643개 시험, 1536초)에서 잰 값은 다음과 같다.
  - 복원: 복사를 동반한 복원이 143회, 합계 80.1초였다. 전체 시간의 5.2%다.
  - 하드 링크 복원: 부하 없는 벤치마크에서 복원 1회의 중앙값이 줄었다. 합성 활성 상태는 0.315초에서 0.203초로, 공개 활성화 상태는 1.108초에서 0.698초로 줄었다. 약 35%의 절감이므로 위 실행에서 아낄 수 있는 시간은 약 28초(1.8%)다.
  - 파생 빌드: 공개 활성화를 다시 도는 파생 빌드 가운데 부모 템플릿이 같은 프로세스에 이미 있는 것은 `solved_instance` 둘뿐이다. `ready_work(public=True)` 세 키는 목표와 설정이 달라 부모가 되는 `activated_instance` 키가 따로 만들어지지 않는다. 공개 활성화 빌드는 7.9~8.7초였으므로 아낄 수 있는 시간은 약 17초(1.1%)다.
  - 두 수단 모두 새 규칙을 만든다. 하드 링크는 pristine과 live가 객체 파일을 공유하는 규칙을, 파생 빌드는 템플릿 사이의 부모 수명 규칙을 만든다. 실익이 1~2% 수준이라 계약 2절 7항의 "실익이 확인될 때"에 해당하지 않는다고 판정했다.
  - 원자료에 있던 "공개 활성화 44.8초"는 부하 중 값이었다. 이번 실행에서 공개 활성화 빌드는 약 8초였다.
- **TSB-09 — 구현함.** 네 곳을 지웠다.
  - `purpose_fixtures.PurposeHarness.tearDown`의 `DO_MATH_PURPOSE_TEST_REPORT` 보고
  - `test_purpose_engine`의 `GitPurposeTests` 보고 블록과 `__main__` 보고 블록
  - `test_input_recovery`의 `INPUT_RECOVERY_REPORT` 블록
  - `test_host_resources`의 `evidence()`와 그 호출 5곳. `lifetime-settlements` 기록만을 위해 모으던 `observed` 목록도 함께 지웠다.

  보고 훅이 없어지면서 `PurposeHarness`·`ActivatedPurposeHarness`의 `runners`·`engines` 목록도 쓰는 곳이 없어졌다. 그래서 목록과, 목록을 고치던 두 줄(`test_academic_engine`, `test_review_research`의 `self.runners[-1] = runner`)을 지웠다.
- **TSB-10 — 구현함.**
  - 미사용 import를 지웠다. 범위는 다섯 조각의 모든 시험 모듈과 픽스처 모듈이며, `ast`로 전수 집계했다. 남은 것은 `test_external`의 `from do_math.external import *` 하나다. 별표 import라 쓰임을 이름으로 가를 수 없어 두었다.
  - `test_redesign_ENGINE`(지금 `test_engine.PublicGitFlow`)의 디버그 `print` 두 줄과 `test_external`의 `time.sleep(.02)`를 지웠다. `test_external` 10개 시험은 모두 통과했다.
  - `test_academic_engine._set_requirements`의 쓰이지 않는 `decision_id` 인자와 호출자 4곳의 인자를 지웠다.
  - `TOOLCHAIN`은 TFIX가 이미 지웠다.
- **TSB-12 — 구현함.**
  - `test_every_call_budget_control_produces_stable_queue_identity` → `test_every_queued_user_control_has_a_stable_queue_identity`
  - `test_elapsed_legacy_run_limit_does_not_block_the_next_execution` → `test_elapsed_time_does_not_block_the_next_execution_and_work_calls_have_no_timeout`
  - `test_legacy_live_review_validates_sidecar_before_applying_continue` → `test_live_review_validates_sidecar_before_applying_continue`
  - `test_empty_queue_uses_goal_exhaustion_not_legacy_cycle_limit` → `test_empty_queue_prepares_from_goal_exhaustion_regardless_of_cycle_count`
  - 지운 단언은 셋이다. `_apply`의 `owns_response` 시그니처 단언, `PublicGitGovernanceTests.engine_type`의 `GovernanceEngineMixin` 상속 단언, `test_operator`의 `parking-unimodality` 부재 단언이다. 앞의 둘 가운데 `engine_type`은 상속 단언을 지우자 `ResearchEngine`을 돌려주는 일만 남아, 호출 10곳을 `ResearchEngine(...)`으로 바꾸고 메서드를 지웠다.
- **TSB-16 — 구현함.** 이의 시험 `test_objection_judgment_answer_and_final_approval_use_real_engine`을 `self.make('dispute', review_rounds=3)`으로 바꾸고, 그 주기가 `('match', 2)`로 닫혔다는 단언을 더했다. `test_review_research...test_confirmed_withdrawal_closes_before_the_round_cap`은 지웠다. 이 시험만 쓰던 `purpose_state(review_rounds=3)` 빌드도 없어졌다. 대신 `activated_instance(review_rounds=3)` 빌드가 하나 생겼고, 이번 실행에서 8.2초였다.
- **TSB-17 — 구현함(지침만 고침, 측정 안 함).** `시험-지침.md` 2절에서 조각 시간 판정의 규칙을 바꾸었다. 조각 시간은 `--shard <이름>` 단독 실행으로 재고, 그 이유(템플릿의 프로세스 안 재사용)를 적었다. 통합 확인의 조각별 시간은 이 판정에 쓰지 않는다. 300초 목표는 전체 합계로 판정한다. 3절 규칙 7의 "조각별 시간은 … 잰다"와 2절의 묶음 실행 문단도 같은 뜻으로 맞췄다. 조각별 재측정과 `SHARDS` 재배치는 하지 않았다.

처분별 건수: 구현함 8, 조건 불성립 1(TSB-05).

## 3. 새 공유 정의, 지운 공개 이름, 이름 대응표

### 3.1 새로 만들거나 바꾼 공유 정의

- `tests/engine_fixtures.py`의 `formal_check_engine(test)`는 새로 만든 정의다. 옛 `FormalContinuationTests.make`를 옮긴 것이며 `(engine, action)`을 돌려준다. 옛 `ReviewScopeBudgetTests`가 `FormalContinuationTests()`를 인스턴스로 만들어 이 메서드를 빌려 썼다. 두 클래스가 다른 모듈(`test_formal_engine`, `test_review_engine`)로 가면서 픽스처 모듈로 옮겼다. 시작 상태는 같다.
- `purpose_fixtures.solved_instance`의 반환값이 바뀌었다. 이제 `{'instance_id', 'head', 'work_order'}`를 돌려준다(TSB-03).
- `purpose_fixtures.PurposeHarness`에는 `fixture_config`와 `drive`만 남았다. `setUp`, `tearDown`, `make`(새 저장소에서 공개 초기화·활성화)는 지웠다. 쓰던 곳이 `GitPurposeTests` 하나뿐이었다.
- `ActivatedPurposeHarness`의 `setUp`은 어댑터 패치만 한다. `runners`·`engines` 목록은 지웠다.

### 3.2 지운 공개 이름

- 모듈 14개(1절)와 그 모듈 수준 이름. 모듈 수준 빌드·상수는 그 빌드를 쓰는 클래스와 함께 옮겼다. `efficiency_instance`·`EFFICIENCY_CONFIG`는 `test_engine`으로, `plan_ready_instance`는 `test_currentness`로 갔다. `AT`는 `test_research_recovery`와 `test_operator`에 각각 들어갔다. `AT`는 시각 문자열 상수이며 도우미가 아니다.
- `GitPurposeTests`와 이 절 위의 시험 삭제 5건(TSB-03·04·16)
- `PurposeHarness.setUp`·`tearDown`·`make`, `PublicGitGovernanceTests.engine_type`

### 3.3 모듈 이름 대응표(옛 모듈 → 새 위치)

클래스를 나누어 옮긴 곳은 괄호에 옮긴 시험 수와 새 클래스 이름을 적었다. 새 클래스 이름이 없으면 옛 이름을 그대로 쓴다.

- `test_approved_five_repairs`
  - `WaitOwnershipTests` → `test_submission_flow`
  - `ToolchainContractTests` → `test_formal`
  - `RuleBindingTests` → `test_live_observation`
  - `PartialWithdrawalTests` → `test_task_completion`
  - `NativeRepairTests` → `test_native_final_submission`
  - `InitialDiagnosisTests` → `test_research_recovery`
  - `ResearchAdmissionTests` → `test_session_scheduler`
- `test_walkthrough_followup`
  - `RepetitionReceiptTests`를 나눔
    - 2개 → `test_submission_flow.ReceiptPreservationTests`
    - 1개 → `test_review_engine.ReleasedInsightTests`
    - 1개 → `test_checkpoint_persistence.CheckpointPreservationTests`
    - 1개 → `test_research_recovery.RetryEffectTests`
    - 5개 → `test_repetition.RepetitionLineageTests`
  - `WalkthroughEngineTests`를 나눔
    - 4개와 `seed_plan` → `test_repetition.RepetitionEngineTests`
    - 2개 → `test_review_engine.ReviewPreparationFailureTests`
- `test_run_feedback` → `test_session_scheduler`(네 클래스 모두)
- `test_research_reliability`
  - `ObservationCollectionTests`, `NativeBatchTests` → `test_live_observation`
  - `OperationalInputTests` → `test_role_input`
  - `CompletionBasisTests` → `test_task_completion`
  - `SchedulingResponsibilityTests` → `test_session_scheduler`
- `test_initialization_review_repairs`
  - `WorkProfileAdmissionTests` → `test_planning_engine`
  - `RecoveryOwnershipTests` → `test_research_recovery`
  - `ApprovalDraftTests` → `test_governance_engine`
- `test_connection_repairs`
  - `FormalContinuationTests` → `test_formal_engine`
  - `ReviewScopeBudgetTests` → `test_review_engine`
  - `TransferReferenceTests` → `test_task_completion`
  - `FixedResearchReferenceTests`, `PartialCaptureTests`, `PartialCaptureGitTests` → `test_submission_flow`
  - `HostConfigurationTests` → `test_host_resources`
  - `ReviewOverflowGitTests`를 나눔. 두 클래스 모두 같은 `setUp`을 쓴다.
    - 1개 → `test_review_engine.ReviewInputOverflowTests`
    - 1개 → `test_formal_engine.FormalAttemptLineageTests`
- `test_six_connections`
  - `InputConnections` → `test_role_input`
  - `PlanningConnections` → `test_planning_engine`
  - `OverflowConnections`, `OverflowGitConnection` → `test_input_recovery`
  - `ProviderConnections` → `test_provider_recovery`
- `test_static_review_repairs`
  - `InputBoundaryRepairs`를 나눔
    - 3개 → `test_question_flow.QuestionSourceTests`
    - 1개 → `test_cli.DocumentedQueryTests`
    - 1개 → `test_controls.SourceControlReceiptTests`
    - 나머지 9개 → `test_role_input.RoleInputBoundaryTests`
  - `RecoveryBoundaryRepairs` → `test_research_recovery.RecoveryBoundaryTests`
  - `WakeRepairs` → `test_operator.WakeTests`
- `test_redesign_ENGINE`
  - `test_engine`: `QueryIdentity`, `ObservationMerge`, `PublicGitFlow`, `MaintenanceConnections`
  - `test_governance_engine`: `IntentConnections`, `GovernanceOwnerConnections`
  - `test_controls`: `ControlReceipts`, `UserControlIdentity`, `ControlQueueConnections`
  - `test_submission_flow`: `KnowledgeConnections`, `BundleConnections`, `CentralSubmissionEvidence`, `ContinuationConnections`, `LivePreviewConnections`
  - `test_review_engine`: `ImpactReviewRouting`, `AssessmentReassessmentConnections`, `DelegationConnections`
  - `test_formal_engine`: `FormalAuthority`, `FormalBindingConnections`
  - `test_planning_engine`: `KindSemanticConnections`, `EvaluationConnections`, `DuplicateRevisionConnections`
  - `test_research_recovery`: `ExecutionConnections`, `FinalBoundaryConnections`
  - `test_live_observation`: `ObservationTransactions`, `TaskObservationRoleTests`
  - `test_role_input`: `InputManifestConnections`
  - `test_lifecycle_engine`: `PersistedConnections`
  - `test_session_scheduler`: `MachineAdmissionConnections`
  - `ReceiptAndQuotaConnections`를 나눔
    - 1개 → `test_submission_flow.TaskReceiptTests`
    - 1개 → `test_review_engine.ReviewAttemptAdmissionTests`
  - `AuditConsumerConnections`를 나눔
    - 1개 → `test_live_observation.ReviewDialogueObservationTests`
    - 1개 → `test_research_recovery.OperationalRepairCandidateTests`
    - 1개 → `test_engine.SourceIntegrityCheckTests`
    - 3개 → `test_role_input.PreparedInputTests`
- `test_efficiency`의 `EfficiencyTests` → `test_engine.QueuedPreparationTests`
- `test_initialization_efficiency`
  - `EfficiencyUnits`를 나눔
    - 5개 → `test_operation_trace.OperationTraceTests`
    - 1개 → `test_role_input.ArchivedControlInputTests`
    - 1개 → `test_payloads.PayloadEncodingTests`
    - 1개 → `test_controls.MaintenanceFenceTests`
  - `PayloadStorageTests` → `test_payloads`
  - `DeferredPublicationTests`를 나눔
    - 1개 → `test_controls.PublicMaintenanceFenceTests`
    - 1개 → `test_submission_flow.SubmissionPublicationWaitTests`
- `test_document_followup`의 `FollowupDocumentTests` → `test_role_input`
- `test_lifecycle_currentness`의 `CurrentnessTests` → `test_currentness.SolvedStateCurrentnessTests`
- `test_currentness_recovery` → `test_currentness`(이름만 바꿈)

`SHARDS` 배치는 다음과 같다. 새 모듈 가운데 `test_currentness`는 research에, `test_repetition`은 review에 두었다. 나머지 새 모듈은 lifecycle에 두었다.

| 조각 | 전 | 후 |
|---|---|---|
| lifecycle | 389 | 335 |
| review | 145 | 176 |
| host | 152 | 160 |
| research | 84 | 114 |
| academic | 60 | 41 |

연구 조각에는 이제 `solved_instance(criteria=None)` 빌드(이번 실행 46.6초)가 붙는다. 이 빌드는 옛 `GitPurposeTests`가 따로 돌던 경로를 대신한다.

## 4. 필요한 문서 변경

- **`scripts/이음새-정본.md` 246행(`await_stop` 행).** "`test_connection_repairs`와 `test_machine_parallel`의 정지 대기가 이것을 쓴다"를 "`test_formal_engine`과 `test_machine_parallel`의 정지 대기가 이것을 쓴다"로 바꾼다. 이 파일은 이 파견의 수정 범위 밖이라 고치지 않았다.
- **`research_fixtures` docstring**의 모듈·빌드 이름은 고쳤다. 공개 경로를 유지하는 e2e 목록, 한 모듈 전용 빌드의 모듈 이름, `solved_instance` 반환값이 대상이었다.
- 역사 기록(`docs/do-math/boundary-repairs-2026-09-25/*.json`, `implementation-v5/traceability.json`, `review-2026-09-18/` 등)에는 지운 모듈 이름이 남는다. 동결된 기록이므로 고치지 않는다.

## 5. 실행한 시험

기계적 확인은 다음과 같다.

- `python -m py_compile scripts/tests/*.py scripts/test_categories.py scripts/run_tests.py`: 오류 없음.
- `scripts/tests`의 모든 모듈(시험 127개와 픽스처 9개)을 `importlib.import_module`로 적재했다. 실패는 0이다.
- `python scripts/run_tests.py --list`: 정상 종료, 1855행.
- 옛 이름 grep: 지운 모듈 14개, `GitPurposeTests`, `PurposeHarness.make`의 이름을 `git grep`으로 찾았다. 남은 곳은 4절의 `이음새-정본.md` 한 행과 역사 기록뿐이다.
- 이동 보존 대조: 기준 커밋 `6fa2a7c`(내용 수정 뒤, 이동 전)과 이동 뒤 트리의 모든 시험 메서드 본문을 `ast`로 추출해 이름별로 비교했다. 본문이 달라진 것은 import 별칭을 바꾼 4건뿐이다(`QuestionSourceTests` 2건, `FollowupDocumentTests` 2건). 픽스처 메서드 본문의 변화는 없다.

시험 ID 수의 전후 대조(`--list`)는 다음과 같다.

- foundation: 1029 → 1029
- 다섯 조각 합계: 830 → 826. 차이 −4의 내역은 TSB-04에서 −3, TSB-16에서 −1, TSB-03에서 −1+1이다.
- 전에만 있는 이름 28개와 후에만 있는 이름 24개는 모두 2절의 이름 변경과 삭제로 설명된다. 짝이 없는 이름은 없다.

실행한 시험은 다음과 같다.

- 명령(`scripts/` 상위 폴더에서, `DO_MATH_KNOWLEDGE_TEST_LEAN`에 계약 6절의 경로를 줌): `python ../../../.torgb-scratch/measured_run.py <계측 파일> test_checkpoint_persistence test_cli test_controls test_currentness test_engine test_formal test_formal_engine test_governance_engine test_host_resources test_input_recovery test_lifecycle_engine test_live_observation test_native_final_submission test_operation_trace test_operator test_payloads test_planning_engine test_provider_recovery test_question_flow test_repetition test_research_recovery test_review_engine test_role_input test_session_scheduler test_submission_flow test_task_completion test_purpose_engine test_review_research test_academic_engine test_model_assessment_flow test_external test_submission_tools.ProducerToolTests.test_live_review_validates_sidecar_before_applying_continue`
- `measured_run.py`는 `run_tests.main`을 그대로 부르는 감싸개다. 부르기 전에 템플릿 빌드와 복원의 시간을 기록하게 해 두었다(TSB-05). 시험 프로세스는 이것 하나만 띄웠다.
- 결과: 선택 643, 통과 642, 건너뜀 1, 실패 0, 오류 0. 1536초가 걸렸다.
  - 건너뜀은 `test_formal.ToolchainContractTests.test_inspection_matches_actual_formal_verifier`다. 사유는 "portable Lean is not installed"다. 이 시험은 `formal.toolchain_root()`의 기본 경로(worktree 기준)를 읽는다. TFIX 반환에도 같은 건너뜀이 있다. 환경 원인이다.
  - TFIX가 변경 전부터 실패한다고 보고한 `test_static_review_repairs...test_profile_query_document_reads_cli_result_envelope`은 지금 `test_cli.DocumentedQueryTests`에 있으며 통과했다.
- 조각 실행과 전체 실행은 하지 않았다. 위 실행의 조각별 시간은 여러 조각을 한 프로세스에서 돈 값이므로 조각 시간이 아니다.

돌리지 않은 관련 시험과 이유는 다음과 같다. 모두 컴파일, 전체 import, grep으로만 확인했다(시험 지침 2절의 소비자 쪽 확인).

- import 줄만 바뀐 모듈: `test_academic_preparation`, `test_control_shapes`, `test_submission_boundaries`
- `ActivatedPurposeHarness`의 소비자로서 하네스의 `runners`·`engines` 목록 삭제만 영향이 있는 모듈: `test_submission_tools`(이름을 바꾼 한 시험은 돌렸다), `test_submission_boundaries`, `test_academic_preparation`, foundation의 `test_reading_map`. 목록을 읽는 곳이 없음을 grep으로 확인했다.
- `test_lifecycle_engine`의 `_available_inputs` 대역 삭제 두 곳은 돌린 범위에 든다. `test_lifecycle_engine` 전체가 통과했다.

## 6. 기능이나 시험 범위가 바뀐 것

- **공개 초기화·활성화 e2e 한 번 감소(TSB-03).**
  - 이유: `solved_instance` 빌드가 같은 경로를 돈다.
  - 잃는 것: 새 저장소에서 `PurposeRunner`로 도는 별도 한 바퀴. 같은 경로는 빌드(`AcademicRunner`, 학술 과제 없음)와 `test_engine.PublicGitFlow`가 돈다. 단언은 모두 보존했다(`work_order`와 게시 헤드는 빌드 반환값으로).
  - 얻는 것: 한 프로세스에서 공개 활성화에서 해결까지의 구동이 한 번 준다.
- **중복 시험 4개 삭제(TSB-04·16).** 잃는 성질은 없다. (a)에서는 남는 쪽에 두 종류 호출이 모두 관찰되었다는 단언을 더했다. TSB-16에서는 이의 시험이 회차 상한 3에서 2회차에 닫힘을 단언한다. 다만 이의 시험은 이제 `review_rounds=3` 설정에서만 돈다. 기본 상한 2에서 같은 흐름이 도는지는 따로 단언하지 않는다.
- **보고 훅 삭제(TSB-09).** 환경변수를 설정해 증거 파일을 받던 수동 사용법이 없어진다. 저장소 안에 생산자는 없었다.
- **구현 모양 단언 삭제(TSB-12).** 시그니처·상속·특정 문자열 부재 단언 세 개를 지웠다. 행동 단언은 같은 시험과 이웃 시험에 남는다.
- **`_available_inputs` 대역 삭제(관찰).** `test_lifecycle_engine`의 두 시험과 `ControlReceipts`의 한 시험에서 지웠다. 제품에서 `_available_inputs`를 부르는 곳은 `engine._context`(1658행) 하나이고, `_context`를 부르는 곳은 `_call_steps` 하나다(3008행). 세 시험은 이 경로를 지나지 않거나(`_call_steps` 대역, 기계 행동 경로, 제어 게시), 지나더라도 결과를 단언하지 않는다. 지운 뒤에도 모두 통과했다.
- **시험 위치.** 시험 모듈 이름이 바뀌어 시험 ID가 달라졌다. 시험 ID를 외부에서 참조하던 역사 기록은 옛 이름으로 남는다.

## 7. 막힌 지점, 접근을 바꾼 지점, 예상과 달랐던 결과

- **클래스 사이의 빌림.** `ReviewScopeBudgetTests`가 다른 시험 클래스를 인스턴스로 만들어 픽스처 메서드를 빌려 썼다. 두 클래스의 소유 모듈이 달라, 메서드를 `engine_fixtures.formal_check_engine`으로 옮겼다(3.1).
- **분류 기준.** 계기 모듈의 클래스는 대부분 `engine.py`의 사적 메서드를 검사한다. 그래서 "소유 제품 모듈"만으로 나누면 거의 전부가 `test_engine`으로 모인다. 이를 피하려고 engine 안의 영역(제어, 제출, 역할 입력, 관찰, 복구, 계획, 형식 검사)을 성질로 삼아 나누었다. 여러 영역을 섞은 점검 회차 클래스는 시험 단위로 나누었다. 도우미 메서드가 있는 클래스는 그 도우미를 쓰는 시험끼리 함께 옮겼다.
- **이동 도구.** 클래스와 메서드를 옮기면서 필요한 import와 모듈 수준 정의를 `symtable`로 찾아 함께 옮기는 일회용 스크립트를 썼다. 이 스크립트는 반환 전에 지웠다. 이름 충돌(`common`이 두 픽스처 모듈에서 다른 함수)은 별칭으로 풀었고, 5절의 본문 대조로 다른 변화가 없음을 확인했다.
- **TSB-05의 전제.** 검토의 "부하 중 공개 활성화 44.8초"와 달리, 이번 실행의 공개 활성화 빌드는 약 8초였다. `ready_work(public=True)`는 부모 템플릿과 키가 달라 파생 빌드로 절감할 수 없다. 그래서 두 수단의 기대 이득이 검토 추정보다 작았다.
- **작문 독해 절차.** `writing_flow.py`를 세션 ID `do-math-guide2-20260927`로 적용했다. 상태 루트는 worktree로 지정했다(1절). 독해를 네 번 했다.
  - 첫 독해에서 무거운 두 항목(조각 시간은 단독 실행으로, 시험·도우미의 배치)이 전달되었다.
  - 이번 고침이 만든 대목의 지적 셋(지시 대상, 교차 참조, 경로 기준)은 고쳐 새 판본을 다시 읽혔다.
  - 마지막 독해의 지적 둘은 이번 고침 범위 밖의 기존 문장이라 유지했다.
  - 판정은 `accept`이고, `status`의 `completion_problem`은 비었다.

## 8. 다른 그룹 범위에서 발견한 문제

- **TORG-A, foundation의 계기 이름 모듈.** `test_boundary_repairs`, `test_walkthrough_repairs`, `test_walkthrough_contract_repairs`, `test_performance_repairs`, `test_observation_audit1`, 그리고 `test_redesign_*`의 `AuditRepairTests`(CONTRACTS, GOVERNANCE)와 `KnowledgeAudit2`, `test_redesign_SURFACE`의 `test_audit*` 이름이 남아 있다.
- **TSA, `test_knowledge_import_engine.py`의 `DO_MATH_KNOWLEDGE_AUDIT_DIR`.** TSB-09와 같은 생산자 없는 보고 훅인지 확인이 필요하다(TSB 검토 5절). foundation 소유라 보지 않았다.
- **병합 주의.** TORG-A가 foundation 모듈에서 `purpose_fixtures`·`research_fixtures`의 이름을 쓰거나 고치면 이 브랜치의 픽스처 변경과 겹칠 수 있다. 겹칠 수 있는 곳은 둘이다. 하나는 `PurposeHarness.make`·`setUp`·`tearDown`의 삭제와 `ActivatedPurposeHarness`의 `runners`·`engines` 목록 삭제다. 다른 하나는 `solved_instance`의 반환값이다. foundation에서 `ActivatedPurposeHarness`를 쓰는 `test_reading_map`은 이 변경과 충돌하지 않음을 grep으로 확인했다.
