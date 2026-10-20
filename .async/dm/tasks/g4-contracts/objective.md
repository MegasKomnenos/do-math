# 전체 일반 검사에서 드러난 계약 fixture·단언·문서 수리

G4 full4의 측정 Git 경계와 조건부 symlink skip를 제외한 18개 실패/오류 행을 한 묶음으로 해결한다. 서로 같은 현행 계약을 소비하는 fixture, 단언 helper, 문서 표기를 함께 고치고 필요한 작은 확인을 마친다. 이 task의 통과만으로 G4를 닫지 않는다.

SESSION_JSON와 task.json, inputs/context.md·plan.md·seams.md를 먼저 읽는다. 작업 사본의 AGENTS.md·시험-지침과 manager0064/review.md, 저장 범위 사용자 지시를 적용한다. 추가 입력의 C:/math/.async/dm와 docs는 읽기 전용 원자료이며 제품은 자기 workspace만 사용한다. full4 원보고의 실패·subTest·fixture와 현재 정의/직접 소비자를 먼저 읽는다. 보고에 적힌 원인도 코드로 확인하고, 제품 결함과 현행 계약과 어긋난 fixture를 구별한다.

현재 원증거는 selected4288=실제4288, 4262passed/14failed/9error/1skipped/2not_run, fixture error1, exit1이다. manager는 정본시험2/공식미러2 수리만 통합·부분 수용했다. 서로 다른 판본의 부분 성공을 전체 통과로 합산하지 않는다. 이번 task는 지정된 실제 실패의 수리와 필요한 직접 확인을 끝내는 것이 목적이다. 전가족 저장 생산/전필드/새reader/옛head quota나 별도 감사·프레임워크를 만들지 않는다. 이미 충분한 공통 codec·업무 근거는 재사용한다.

원 실패 보고를 보존하고 코드를 읽어 충분한 부분은 정적으로 판정한다. 실행이 필요한 수리만 정확한 실패 ID 또는 관련 최소 묶음으로 공식 run_tests.py에서 확인한다. 단언 약화·skip 추가·선택 축소·구판 필드 복원·호환 계층·내부 검사 대역으로 성공을 만들지 않는다. 같은 문제를 문서 번호/실패 행마다 새 task로 나누지 않는다. 직접 관련 수리·helper 소비자·공식미러를 이 task에서 함께 마친다. 새 런타임 결함이면 원실패와 수리 이유·관련 확인을 남긴다. 범위 밖 결정이 필요하면 유효 결과와 정확한 남김을 보고한다.

시험은 한 번에 하나만 실행하며 전체 G4/T3/T4/T5·변이·유료 호출은 이번 배정에 덧붙이지 않는다. 아래 명시한 기존 측정 meta 시험의 작은 native 자식 호출은 해당 meta 동작 확인에 한해 포함한다. TEMP/TMP/TMPDIR는 저장소 밖의 짧고 고유한 경로를 쓰고 기존 GIT_CEILING_DIRECTORIES를 보존·추가한다. 실행 중 제품/시험/미러를 수정하지 않는다. 시간은 소프트 기준이며 timeout으로 종료/성공 판정하지 않는다. 실제 command/cwd/필요환경·exit·원 report/stdout/stderr와 제출판 SHA를 보존한다. 선택과 실제 row, fixture, skip, source 변경 여부를 함께 판정한다.

공식 build_skill_mirrors.py로 자기 수정의 미러만 생성/check한다. .timings.json 등 이번 관측 캐시는 evidence에 보존 후 자기 base로 복원해 통합 대상에서 제외한다. 원 자료는 task/evidence 또는 저장소 밖 새 경로에 둔다. 변경 이유·직접 확인·한계·남은 문제를 report.json에 쓰고 check.py report C:/math/.async/dm g4-contracts를 통과시킨다. 공용 소스/문서/queue/state·다른 task·engine·graphify·기존 연구·공용 Git index/commit은 수정하지 않는다. 제품 설명을 바꿀 필요가 있으면 배정된 설명 파일에 실제 계약을 연결하고, 다른 task 소유 문서의 필요한 변경은 report에 정확한 심볼/내용으로 남긴다.

## 구체적인 범위와 보존할 성질

1. 저장 관리정보 3오류: knowledge/expositions에 폐기된 history를 넣지 않는다. 현재 허용된 review_cycle_id/관리 이력과 내용·효력 변경의 차이를 실제 저장/복원/현재성 단언으로 유지한다. knowledge_close_currentness의 family 순회와 formal_results 등의 허용 필드를 같은 수신 계약으로 확인한다. 폐기 필드를 중앙 schema에 되살리는 수리는 하지 않는다.
2. 복구/checkpoint 3행: parent_execution_id=None/값을 직접 주입하는 옛 fixture를 현행 formal_check/continuation·operational_review action.target 관계로 바꾼다. normal_inline의 정상 형식 완료/null checkpoint, 부모·자식 원 행동/원산출물·재시작의 마지막 유효 checkpoint 및 손상/부재 반려 성질을 보존한다.
3. 운영 과제 처분 2오류: submission.issued_input이 실제로 읽을 input_bundle·봉인된 context·input_snapshot을 준비한다. 현재 실제 지급 helper를 재사용하고 원 source·과제 권한·개별 assessment·이전 처분 검사를 유지한다. reader를 대역으로 바꾸거나 input 검사를 없애지 않는다.
4. 독립 검토 1행: conversation_id를 두 execution에 주입하는 대신 governance.validate_independent_execution이 소비하는 실제 continuation_of 계보로 작성자와 검토자의 비독립 반례를 구성한다. 새 독립 대화의 정상 대조·scoped receipt·실제 Git bytes와 정확 반려를 보존한다.
5. 운영자 HOLD 1행/네 subTest: scheduled_operator.execute의 startup은 operator/startup.json과, held 결과는 동작 계약과 각각 정확히 대조한다. g4-general이 수리한 CLI 여정이 현재 참고다. HOLD의 비실행·상태 불변을 유지한다.
6. 반복 보류 1행: action.repetition_bases의 현행 세 계보와 revision_targets/observation_rule_targets의 판본 계보를 구별한다. 다섯 계보의 한도·정확 승인/오승인·중복 방지·두 번째 주기를 현행 생산 모양으로 보존한다.
7. 설치 복구 1행: resume_installation_repair의 후속 준비/활동 ready와 successor_state·조건·원 repair_attempt/행동/정산을 함께 대조한다. 단순히 실제 관측값을 기대값으로 복사하지 않는다. r40-r43의 수용된 활동 재개 성질이 근거다.
8. 단언 helper 1구조행/6발견: storage_execution_pairs의 내용·저장 단언 5개와 storage_action_pairs.merge_samples의 실제 단언을 구조 검사에서 정확히 읽을 수 있게 역할을 드러낸다. 실제 정의와 모든 소비자를 함께 바꾸고 ASSERTION_HELPERS 예외 목록 추가나 의미 없는 None 반환 단언은 하지 않는다. 이미 통과한 큰 저장 시나리오를 이름 변경만으로 전부 재실행할 필요는 없다. 본문/소비 보존과 구조 검사로 충분한지 판단한다.
9. 문서 기호 3행: README의 scheduled_operator.execute와 CLI-실행-계약의 operator_bootstrap.verify_snapshot을 실제 파일·함수 참조로 표기하여 저장 필드로 오인되지 않게 한다. 동일 원인의 세 소비자는 함께 확인한다. 문서 검사 예외를 추가하지 않는다.
10. 상태 문서 1행: status_field_schema는 빈 배열에서 원소 필드를 입증하지 못한다. 초기화 실패 보고 성질과 실제 비빈 task waits 응답의 유효 문서 필드를 정확히 연결한다. status.tasks[].waits 문구를 삭제하거나 빈 표본에서 타입을 지어내지 않는다. doc_code와 unit/boundary 직접 소비자가 같은 계약을 사용한다.
11. 이행 원장 1행: migration/dispositions/provider.1.json의 legacy ID는 보존하면서 new_ids를 현재 native 조각/원수신 시각/좌표·순서/지연 재생 시험에 연결한다. 없는 새 ID로 바꾸거나 원 성질을 버리지 않는다.

## 자원·권한·완료

기본 --jobs 1, 동시 시험 슬롯1개다. 병행 g4-measurement는 native 자식용 최대2슬롯을 쓴다. 전체 일반을 재실행하지 않고 지정 실패의 원인을 수리·판정한 뒤 보고한다. writes 중 do_math/는 위 실패를 조사하다 확인된 직접 제품 결함만을 위한 범위다. 지금은 주로 fixture/기대값 문제라는 근거가 있으며, 관측된 제품 동작을 정상으로 단정하지 않는다. 측정 runner/branch_gate/adapter_coverage/selection/t3_store/시험-지침은 다른 task 소유다. 새 공개 인터페이스를 무관하게 추가하지 않는다.

완료 시 아래 지정 행 각각의 수리/확인/남김을 연결한다. 공통 원인에 대한 정적 판정이 충분하면 그 이유를 쓰고 불필요한 재실행을 하지 않는다. 지정 실패 밖 새 문제가 드러나면 정확한 입력/현재 코드/영향을 남긴다. 작은 성공을 최종 전체판 성공으로 표시하지 않는다.

## 지정 실패 ID

- assertion_helper_calls
  - `structure.test_test_smells.SmellTests.test_new_system_tests_have_no_smell`
- document_symbol_notation
  - `structure.test_doc_code.DocumentCodeTests.test_all_dotted_document_fields_have_an_owner`
  - `unit.test_engine_trace_report_corruption.TraceCorruptionTests.test_unreadable_error_sidecar_has_bounded_explicit_status`
  - `unit.test_role_input_packaging.RoleInputTests.test_role_input_uses_current_schema_documents_and_private_resume_bytes`
- independent_review_lineage
  - `unit.test_knowledge_impact_review.ImpactReviewTests.test_review_resolver_uses_actual_git_bytes_and_scoped_receipt`
- issued_operational_input
  - `sim.test_scheduling_task_dispositions.OperationalTaskDispositionTests.test_operational_completion_and_transfer_use_real_task_domain_validation`
  - `sim.test_scheduling_task_dispositions.OperationalTaskDispositionTests.test_operational_task_disposition_uses_authoritative_item_assessment`
- migration_test_identity
  - `structure.test_migration_ledgers.MigrationLedgerTests.test_every_legacy_test_is_still_present_or_disposed_of`
- operator_startup_envelope
  - `sim.test_operator_finish_cli.OperatorCommandTests.test_hold_stops_wake_engine_and_supervisor_at_the_public_boundary`
- recovery_execution_fixture
  - `sim.test_knowledge_currentness.RecoveryMaterialTests.test_normal_formal_completion_has_null_checkpoint_and_reports_unrestorable_sources`
  - `sim.test_knowledge_currentness.RecoveryMaterialTests.test_recovery_captures_parent_and_inline_child_without_losing_action`
  - `sim.test_engine_checkpoint_persistence.CheckpointPersistenceTests.test_restart_preserves_last_valid_checkpoint_and_records_invalid_final_observation`
- repaired_activity_readiness
  - `unit.test_repair_execution.InstallationRepairTests.test_installation_repair_continues_latest_rejected_bundles_without_resetting_count`
- repetition_version_binding
  - `unit.test_repetition_hold_contract.RepetitionHoldContractTests.test_every_lineage_keeps_its_hold_until_the_exact_user_continuation`
- status_task_wait_binding
  - `unit.test_storage_report_projections.ReportProjections.test_human_report_preserves_loaded_initialization_blocker_and_machine_finding`
- stored_administrative_metadata
  - `sim.test_call_stop_flags.GoalAuditStopTests.test_administrative_history_does_not_stop_but_content_change_does`
  - `unit.test_knowledge_close_currentness.CurrentnessGuards.test_basis_ignores_scheduling_and_history_but_preserves_content_and_effect`
  - `unit.test_knowledge_io_contracts.CandidateImportTests.test_relation_claim_endpoint_basis_matches_the_storage_contract`
