# 결과-OPS

OPS 그룹(운영·초기화·스크립트)의 구현 결과다. 형식은 계약 7절을 따른다. 좌표는 `.claude/skills/do-math/` 아래 경로이고, 행 번호는 커밋 `59a18cd` 기준이다.

## 1. 브랜치, 커밋, 바꾼 파일

- 브랜치: `c-ops`. 시작점은 `c-int`의 `640e9e3`이다.
- 마지막 커밋: `59a18cd`

바꾼 파일은 다음과 같다.

- **제품**
  - 삭제: `scripts/check_coverage.py`
  - 수정: `scripts/do_math/configuration.py`, `scripts/do_math/engine.py`(OPS-09 한 줄, 설정 재검사 한 곳), `scripts/do_math/governance.py`, `scripts/do_math/governance_engine.py`, `scripts/do_math/initialization.py`, `scripts/do_math/record_schemas/__init__.py`, `scripts/do_math/trust_inventory.py`, `scripts/operator_bootstrap.py`, `scripts/probe_cli.py`
  - 시험 편성: `scripts/test_categories.py`(`SHARDS`에서 지운 모듈 세 개만 뺐다)
- **시험**
  - 삭제: `scripts/tests/test_redesign_EVIDENCE_binding.py`, `scripts/tests/test_redesign_EVIDENCE_scope.py`, `scripts/tests/test_redesign_EVIDENCE_run.py`
  - 수정: `scripts/tests/research_fixtures.py`, `test_decision_basis.py`, `test_environment_validation.py`, `test_governance_engine.py`, `test_knowledge_import_engine.py`, `test_observation_audit1.py`, `test_redesign_ENGINE.py`, `test_redesign_EVIDENCE.py`, `test_redesign_GOVERNANCE.py`, `test_redesign_STORAGE.py`, `test_redesign_SURFACE.py`, `test_review_engine.py`, `test_state_checks.py`
- **문서**
  - 추가: `docs/do-math/implementation-v5/README.md`. 추적표가 역사 기록이며 더는 검사되지 않는다는 한 줄 안내다. `traceability.json`은 고치지 않았다.
  - 수정: `scripts/이음새-정본.md`. 6절 표에 새 행 두 개만 더했다.

## 2. ID별 처분

| ID | 처분 | 내용과 좌표 |
|---|---|---|
| OPS-02 | 구현함 | `check_coverage.py`와 추적표 전용 시험 모듈 두 개(`test_redesign_EVIDENCE_binding`, `test_redesign_EVIDENCE_scope`)를 지웠다. `test_redesign_EVIDENCE.py`에서는 `TraceabilityCheckerTests`, `repository_root`·`ROOT`·`TRACE`·`SOURCE`, `import check_coverage`를 지웠다. `SHARDS['foundation']`에서 세 모듈을 뺐다. 추적표·로컬 보관소·`docs/do-math`에 기대는 시험은 `check_coverage\|traceab\|docs/do-math\|implementation-v5\|통합-설계-명세\|do-math-implementation-20260920\|resume-20260920\|source-vector-map`로 스킬 전체를 검색해 전수로 찾았다. 결과는 위 세 파일뿐이다. `test_performance_repairs.py:270-288`과 `test_standalone.py:36`의 `docs`는 임시 폴더 안의 합성 경로라 대상이 아니다. |
| OPS-01 | OPS-02에 흡수(`test_redesign_EVIDENCE.py`의 `TraceabilityCheckerTests.test_full_trace_is_structurally_valid_not_an_execution_pass` 삭제) | 로컬 보관소를 읽는 기본 시험이 없어졌다. 흡수를 택했으므로 CLI(`check_coverage.main`)도 남기지 않았다. |
| OPS-03 | OPS-02에 흡수(`check_coverage.py`의 `scope_artifact_errors`·`adopted_scope`·`runs` 분기는 파일째 삭제, `test_redesign_EVIDENCE_scope.py` 삭제) | |
| HIS-17 | OPS-02에 흡수(`test_redesign_EVIDENCE.py`의 보관소 대조 시험 삭제) | 제안의 `skipUnless` 대신 시험을 지웠다. 파견문에 따라 추적표 JSON의 머리 한 줄은 두지 않고, 같은 안내를 `docs/do-math/implementation-v5/README.md`에 두었다. |
| TSA-09 | 구현함 | 다음을 지웠다. `test_redesign_EVIDENCE_run.py`와 그 `SHARDS` 등록, `test_knowledge_import_engine.py`의 `DO_MATH_KNOWLEDGE_AUDIT_DIR` 쓰기(옛 306-310행), `test_observation_audit1.py`의 `--evidence` 블록과 쓸모없어진 `import hashlib`(`__main__`은 `unittest.main(verbosity=2)` 한 줄), `test_redesign_STORAGE.py`의 `print("STORAGE no-op blob writes:" …)`. `test_state_checks.py`의 docstring은 현재 성질만 적는 한 줄로 고쳤다. |
| OPS-06 | 구현함 | `do_math/trust_inventory.py:217-225`의 `writer_lock`이 이제 `os_lock(directory / '.lock', blocking=False)`를 쓴다. 배타 생성, PID 쓰기, `unlink`, `RuntimeError`를 지웠다. 시험 `test_environment_validation.py:186`은 `assertRaises(OSError)`로 고쳤다. `setup_lean.main`은 `OSError`를 종료 코드 2로 처리하므로(`setup_lean.py:277`) 종료 코드 계약은 그대로다. 문서의 수동 삭제 절차는 4절에 적었다. |
| OPS-08 | 구현함 | `governance_engine.py:207`(`_governance_control`)과 `:225`(`_reject_governance_import`)이 `request.get('config', {}).get('change', {})` 한 모양만 받는다. 시험은 `test_governance_engine.py` 세 곳을 고쳤다. `host()`에서 요청을 `{'change': …}`로 감쌌고, `wrong['config']['change']['check_sha256']`와 `CONF-APPROVE` 요청을 고쳤다. 통합표 정정대로 `checked_import`는 그대로 두었다. |
| OPS-09 | 구현함 | governance 쪽만 했다. `governance.ensure_governance`를 지웠고, 그 호출처 `engine.py:169`는 이제 `knowledge_io.ensure_ontology(instance)`이며, `apply_decision`에서는 `deepcopy`로 바꿨다. 네 가족(`governance`, `governance_sources`, `decisions`, `grants`)에 대한 `setdefault`는 직접 색인으로 바꿨다. 대상은 `_install_record`, `initialize_governance`(`grants` 보충 삭제, `.get` 기본값 둘 포함), `_apply_domain_decision`, `apply_import`, `apply_import_control`, `governance_engine.bind_host_configuration`이다. 선택 단계(엔진이 채우는 초기 필드를 `initialize_state`로 옮기기)는 파견문의 배정 밖이라 하지 않았다. 엔진 쪽 중복 재설정은 ENG-06이 했다. |
| OPS-10 | 구현함 | 새 함수 `governance.source_record(text)`가 `{text, sha256, bytes}`를 만든다(`governance.py:38`). 이 함수를 쓰는 곳은 다음과 같다. `preserve_source`(`validate_source`는 이를 거친다), `initialization.original_input_bytes`의 기대값, `initialize_state`(원문을 한 번만 해시하고 `inputs[0].sha256`도 그 값을 쓴다). `initial_intent_evidence`는 재해시 대신 `original['sha256']`과 `original['text']`로 대조한다. 저장 값의 모양은 그대로다. |
| OPS-12 | 구현함 | `initialization.capability_requirements`(`:38-40`)에서 CE ID 재해시와 조용한 제외를 지웠다. 저장 검증기로 `record_schemas/__init__.py`의 `_capability_evidence_rules`를 새로 두고 `RECORD_RULES["capability_evidence"]`에 등록했다. 이 검증기는 바뀐 행에만 돈다. 새 시험은 `test_state_checks.StateCheckTests.test_capability_evidence_id_must_match_its_content_at_load`다. |
| OPS-13 | 구현함 | `apply_import_control`(`governance.py:1144-1146`)이 `_current_import` 대신 `runtime['intent_imports']`를 조회해 묶음이 있는지만 확인하고, 봉인 좌표(`bundle_sha256`, `check_sha256`, `unit_hashes`)를 대조한다. 현재성은 `apply_import`의 `_current_import`가 한 번 검사한다. |
| OPS-14 | 구현함 | `validate_governance_state`의 최상위 5개 키 거부와 그 문구("in feature 5")를 지웠다. "v5 scope approval"은 "scope approval"로 고쳤다. `validate_grant_source`의 `decision.get("source_sha256", source["sha256"])`와 `governance_engine._apply_governance_goal_audit`의 `view.get('goal_revision', 1)`·`view.get('policy_revision', 1)`은 직접 색인으로 바꿨다. |
| OPS-15 | 구현함 | 미사용 import를 지웠다(`initialization.py`의 `Path`와 `hashlib`, `operator_bootstrap.py`의 `os`, `probe_cli.py`의 `sys`). `governance_engine.py`의 `DEFAULT_CONFIG`는 시작 원문에 이미 없었다(`:10`은 `validate_config`만 import). 중복 import는 현재 이름이 `match_profile_ref`였고, `activation_requirements` 안의 재import를 지웠다. `_configure_candidate`의 `live`·`waiting` 재계산 두 곳도 지웠다. |
| HIS-11 | 구현함 | `governance_engine._after_governance_import`(`:184`)의 `research_preparation` 대기 행동에서 `import_id=import_id`를 지웠다. 읽는 곳이 없으므로 `reason`이나 `event_refs`로 옮겨 적지 않았다. `_ACTION` 스키마의 `import_id`는 `intent_interpretation`이 쓰므로 남겼다. |
| 영역 밖 관찰(설정 재검사) | 구현함 | `configuration.validate_config`가 `host_resources` 검사에서 만든 프로필 판본을 돌려준다(없으면 `None`). `engine.control`의 configure 접수(`engine.py:266`)는 반환값이 `None`일 때만 `build_profiles`를 부른다. `_configure_candidate`에서는 결박 뒤의 두 번째 `validate_config`를 지웠다. 결박은 `host_resources`만 바꾸고, 결박된 호스트 절은 이어지는 `build_profiles`가 검사하기 때문이다. 결박과 서버 해석이 설정을 바꾸지 않았으면 `validate_config`가 만든 판본을 재사용한다. 그래서 같은 설정으로는 한 번만 부른다. `engine.initialize`(`:152-167`)는 설정 변경이 아니라 인스턴스당 한 번 도는 초기화라 고치지 않았다(8절). |

처분별 건수: 구현함 11(TSA-09, HIS-11과 영역 밖 관찰 1건 포함), OPS-02에 흡수 3(OPS-01, OPS-03, HIS-17), 구현하지 않음 0, 조건 불성립 0, 끝내지 못함 0.

## 3. 새 공유 정의와 지운 공개 이름

새 공유 정의는 다음과 같다. 두 행을 모두 `scripts/이음새-정본.md` 6절에 더했다.

- `governance.source_record(text)`(`do_math/governance.py`): 불변 원문 기록 `{text, sha256, bytes}`
- `governance_start(instance=None)`(`scripts/tests/research_fixtures.py`, 시험 도우미): 작은 인스턴스에 `initialize_state`가 모든 인스턴스에 두는 빈 거버넌스 가족 네 개를 더한다.

바뀐 계약은 `configuration.validate_config(config)`의 반환값이다. 전에는 `None`만 돌려주었고, 이제는 host 설정이면 프로필 판본을, 아니면 `None`을 돌려준다.

지운 공개 이름은 다음과 같다.

- `governance.ensure_governance`
- 모듈 `check_coverage` 전체(`validate`, `validate_data`, `validate_observations`, `unproven_errors`, `scope_artifact_errors`, `main` 등)
- 모듈 `test_redesign_EVIDENCE_run` 전체(`manifest`, `RecordedResult`, `main`)
- `test_redesign_EVIDENCE`의 `repository_root`, `ROOT`, `TRACE`, `SOURCE`

옛 이름을 `git grep`으로 찾은 결과 `.claude/skills/do-math`에는 남은 참조가 없다. 생성 사본 `.agents/`와 `docs/`의 과거 산출물에만 남아 있다(4절).

새 상태, 캐시, 수명 규칙, 복구 규칙은 만들지 않았다. OPS-06은 잠금 파일이 남는 상태와 사람이 지우는 복구 규칙을 없앴다.

## 4. 필요한 문서 변경

이 그룹은 아래 문서를 고치지 않았다.

1. **`scripts/tests/시험-지침.md` 2절 통합 확인 문단(현재 41행)**: 두 번째 로컬 자료, 곧 "추적표 검사가 읽는 실행 보관소 … `임시` 폴더로 복사한다"를 지운다. 문단 끝의 "추적표 검사와 실제 Lean 시험이 환경 때문에 실패하며"는 "실제 Lean 시험이 환경 때문에 실패하며"로 고친다. 이 문단에 남는 로컬 자료는 Lean 도구 모음과 `DO_MATH_KNOWLEDGE_TEST_LEAN` 하나다. 이 파일은 시험 단계 그룹의 범위다.
2. **`references/초기화-효율과-정비.md` 91행(OPS-06)**: "기록을 쓰는 모드는 `records/.lock`을 배타적으로 만들어 서로 배제하고 … 잠금 파일이 남아 있으면 `Get-CimInstance Win32_Process`의 `CommandLine`에서 실행 중인 `setup_lean.py`가 없음을 확인한 뒤 사람이 지운다."를 다음 취지로 바꾼다. 기록을 쓰는 모드는 `records/.lock`의 OS 잠금으로 서로 배제한다. 다른 작성자가 잠금을 쥐고 있으면 `OSError`로 끝난다(`status: error`, 종료 코드 2). 잠금은 프로세스가 끝나면 OS가 풀므로 사람이 지울 파일은 없다.
3. **`scripts/이음새-정본.md` 6절의 `DEFAULT_CONFIG`, `validate_config(config)` 행(현재 131행)**: 반환값을 덧붙인다. host 설정이면 만든 프로필 판본을, 아니면 `None`을 돌려주고, 호출자는 이를 재사용해 같은 설정의 `build_profiles`를 다시 부르지 않는다. 파견문이 이 파일에서는 새 행만 허락해 기존 행은 고치지 않았다.
4. **`.agents/diff/_rules.json`의 `verbatim`**: 지운 파일을 가리키는 두 항목 `do-math/scripts/check_coverage.py`와 `do-math/scripts/tests/test_redesign_EVIDENCE_binding.py`가 남아 있다. fnmatch 패턴이라 없는 경로가 오류를 내지는 않는다. 통합자가 `.agents/`를 재생성할 때 함께 지우면 된다.
5. `SKILL.md`, `README.md`, `GLOSSARY.md`, `references/`, `계약/`, `AGENTS.md`에서 `check_coverage`, 추적표, 보관소를 검색했다. 2항의 한 곳 말고는 결과가 없다.

## 5. 실행한 시험

모든 실행에 `DO_MATH_KNOWLEDGE_TEST_LEAN=C:/math/.skill-workspace/do-math-toolchains/lean-4.32.0/lean-4.32.0-windows/bin/lean.exe`를 주었다. 시험 프로세스는 한 번에 하나만 띄웠다.

**기계적 확인.** 바꾼 제품 파일을 `python -m py_compile`로 컴파일했다. `scripts/tests`의 `test_*.py` 132개를 `importlib.import_module`로 적재했고 오류는 0이다. `test_redesign_ENGINE.py`와 `test_review_engine.py`는 그 뒤에 고쳤으며, 아래 run2가 두 모듈을 적재해 실행했다. 옛 이름 grep은 3절에 적었다.

**run1**(인계 확인과 편집 확인). 명령은 다음과 같다.

`python scripts/run_tests.py --output …/ops-work/run1 test_redesign_GOVERNANCE test_governance_engine test_redesign_SURFACE test_redesign_STORAGE test_decision_basis test_state_checks test_redesign_EVIDENCE test_redesign_EVIDENCE_walkthroughs test_environment_validation test_knowledge_import_engine test_observation_audit1 test_test_runner test_initial_intent_connection test_initialization_review_repairs test_walkthrough_repairs test_control_shapes test_redesign_TASKS test_delegation_storage test_walkthrough_followup test_redesign_PROFILES test_storage_validation test_operator_bootstrap test_probe_cli test_initialization_efficiency test_initialization_probe_batch test_engine test_lifecycle_engine test_redesign_ENGINE test_review_engine`

| 조각 | 실행 | 결과 |
|---|---|---|
| foundation | 386 + 격리 6 | 실패 1, 오류 5, 격리 6 통과 |
| host | 5 | 통과 |
| lifecycle | 214 | 오류 3 |
| review | 56 | 오류 8 |

통과하지 못한 17건의 원인은 두 갈래다.

- **이 변경 때문(12건, 모두 `KeyError`)**: OPS-09로 거버넌스 함수가 네 가족을 직접 색인하게 되었다. 그런데 네 가족이 없는 작은 인스턴스를 거버넌스 함수에 넘기는 시험 고정물이 남아 있었다. 원인은 셋이다.
  - `test_review_engine.FakeEngine`의 `self.instance`. `grant_replacement`를 부르는 모든 시험이 걸렸다.
  - `test_redesign_ENGINE.routing_engine`
  - `test_redesign_ENGINE.test_maintenance_archives_complete_run_before_approved_cleanup`의 `current_state(...)`

  세 곳을 `governance_start(...)`로 고쳤다. 대상 시험은 `test_redesign_GOVERNANCE…test_actual_engine_delegation_control_to_independent_judgments_effect_and_receipt`, `test_redesign_ENGINE`(`test_check_cannot_apply_unresolved_proposed_changes`, `test_maintenance_archives_complete_run_before_approved_cleanup`, `test_actual_blind_judgments_apply_the_approved_review_recovery`), `test_walkthrough_followup.test_continue_after_successful_empty_preparation_creates_its_missing_request`, 그리고 `test_review_engine`의 7건이다.
- **변경 전부터 있던 실패(5건)**:
  - `start_review() got an unexpected keyword argument 'owner_activity_id'`(4건). `test_redesign_STORAGE`의 `test_actual_review_cycle_and_identity_producer_round_trip`, `test_staged_review_producer_keeps_transient_candidate_and_real_transition`, `test_verified_identity_and_environment_continuity_round_trip`, 그리고 `test_redesign_EVIDENCE_walkthroughs.test_w12_query_import_metadata_and_next_snapshot_preserve_epistemic_distinctions`가 모두 `test_redesign_STORAGE.py:1216`의 `_reviewed_candidate`에서 실패한다.
  - `test_walkthrough_repairs.test_readiness_document_tables_match_the_condition_grammar`(1건). `references/과제-착수조건.md`의 포인터 표와 `planning.EXPOSED_FIELDS`가 다르다.

  원인 파일(`review_cycle.py`, `planning.py`, `과제-착수조건.md`, `test_walkthrough_repairs.py`, `test_redesign_STORAGE.py:1216` 부근)은 `git diff c-int`에서 이 브랜치의 변경이 없다. 그래서 변경 전부터 있던 실패로 판정했다. 계약 5절이 worktree 생성을 금지하므로 기준 판본을 별도 worktree에서 돌리지는 못했고, 이 판정은 정적 근거다.

**run2**(수리 뒤 확인). 명령은 다음과 같다.

`python scripts/run_tests.py --output …/ops-work/run2 test_redesign_ENGINE test_review_engine test_walkthrough_followup test_redesign_REVIEWS test_redesign_KNOWLEDGE test_review_research test_model_metadata_boundary test_research_reliability test_redesign_GOVERNANCE.AuditRepairTests.test_actual_engine_delegation_control_to_independent_judgments_effect_and_receipt`

foundation 78과 격리 3, lifecycle 93과 격리 1, review 74가 모두 통과했다. 실패와 오류는 0이다. run1의 `KeyError` 12건은 모두 이 실행에 들었다. 고친 고정물(`FakeEngine`, `routing_engine`)을 가져다 쓰는 모듈(`test_redesign_REVIEWS`, `test_redesign_KNOWLEDGE`, `test_review_research`, `test_model_metadata_boundary`, `test_research_reliability`)도 함께 돌렸다.

**돌리지 않은 관련 시험.** 거버넌스 함수나 CE 행을 다른 고정물로 거치는 소비자 모듈이다. `test_six_connections`, `test_connection_repairs`, `test_redesign_LIFECYCLE`, `test_observation_admission`, `test_static_review_repairs`, `test_approved_five_repairs`, `test_initialization_*` 밖의 host 조각 모듈이 여기에 든다. 시험 지침 2절에 따라 소비자 쪽은 통합 확인에 맡겼다. 다만 OPS-09의 직접 색인 때문에, 네 가족이 없는 인스턴스를 거버넌스 함수에 넘기는 고정물이 이 가운데 남았다면 `KeyError`가 날 수 있다. 그런 실패는 고정물을 `governance_start`로 고치는 것이 현행 계약에 맞는 수리다.

## 6. 기능이나 시험 범위가 바뀐 것

- **OPS-02 동결.** 대상은 시험 18개다. `TraceabilityCheckerTests` 12개, `ArchivedEvidenceTests` 5개, `ScopeArtifactTests` 1개이고, 실행기 모듈 하나도 함께 지웠다. 이유는 사용자 결정(계약 2절 2항)이다. 잃는 것은 설계 명세와 구현·시험 사이의 기계적 추적성 검사다. 얻는 것은 셋이다. foundation 조각이 로컬 보관소와 `docs/do-math`에서 독립한다. worktree와 새 체크아웃에서 환경 실패가 사라진다. 보관소 복사 절차가 필요 없어진다. 지운 시험의 단언은 모두 `check_coverage`의 함수나 추적표 파일만 검사했다. 제품의 다른 성질을 검사하던 단언은 없었고, 그래서 옮긴 단언도 없다.
- **TSA-09.** 감사용 부수 출력(환경변수 파일 쓰기, `--evidence`, `print`)만 지웠다. 단언은 바뀌지 않았다.
- **OPS-06.** 시험 단언이 `RuntimeError`와 그 문구에서 `OSError` 형으로 바뀌었다. 잃는 것은 오류 문구의 단언이다. 얻는 것은 두 가지다. 강제 종료 뒤에 남는 잠금 파일이 없어지고, 잠금 구현이 `os_lock` 하나로 모인다.
- **OPS-08.** `_governance_control`은 감싸지 않은 config를 더는 받지 않는다. 그 모양을 쓰던 생산자는 시험뿐이었다.
- **OPS-09.** 거버넌스 함수는 네 가족이 있는 인스턴스를 전제한다. 제품의 인스턴스는 `initialize_state`가 만들고 저장소가 빈 가족도 복원하므로 제품 동작은 바뀌지 않는다. 작은 인스턴스로 부르던 시험 고정물은 `governance_start`로 옮겼다. 단언은 약해지지 않았다.
- **OPS-12.** ID가 내용과 다른 CE 행이 사용 경로에서 조용히 빠지던 동작이 없어졌다. 대신 저장 경계(적재와 게시의 상태 계약 검증)에서 오류가 난다. 이 성질을 단언하는 시험 하나를 더했다(2절 OPS-12 행). 기존 `test_lifecycle_engine.test_capability_evidence_rejects_changed_host_or_forged_record`는 identity 불일치로 여전히 불충족을 단언하며 통과한다.
- **OPS-13.** 없는 묶음을 승인하면 거부 문구가 "import is absent or superseded"에서 "import is absent"로 바뀐다. 대체된 묶음을 승인하면 `apply_import`의 `_current_import`가 같은 문구로 거부한다. 원래 알던 문구와 같다.
- **OPS-14.** 잃는 것은 최상위 `goal`, `policies`, `goal_revision`, `policy_revision`, `academic_requirements`가 메모리 안의 인스턴스에 들어왔을 때의 조기 탐지뿐이다. 게시와 적재 때는 저장 계약이 등록되지 않은 가족을 거부한다(`state_contract.py`의 `unregistered family`).
- **설정 재검사.** 검사의 범위는 그대로다. 줄어든 것은 같은 설정에 대한 반복 호출뿐이다.

## 7. 막힌 지점, 접근을 바꾼 지점, 예상과 달랐던 결과

- OPS-09의 직접 색인이 예상보다 넓은 시험 고정물을 깨뜨렸다. run1에서 12건이다. 원인은 도메인 시험들이 네 가족 없는 작은 인스턴스를 거버넌스 함수에 넘기던 것이었다. 고정물마다 가족 목록을 따로 적지 않도록 시험 도우미 `governance_start` 하나를 두고, 12곳의 고정물을 이 도우미로 고쳤다. 대상은 `test_redesign_GOVERNANCE`, `test_redesign_STORAGE`, `test_redesign_SURFACE`, `test_decision_basis`, `test_governance_engine`, `test_redesign_EVIDENCE`, `test_redesign_ENGINE`(두 곳), `test_review_engine.FakeEngine`이다.
- OPS-15의 원 좌표 가운데 `governance_engine.py`의 `DEFAULT_CONFIG`는 앞 단계에서 이미 사라져 있었다. `resolve_profile`의 중복은 이름이 `match_profile_ref`로 바뀐 채 남아 있었다.
- 설정 재검사를 줄이는 방법으로 `validate_config`가 이미 만든 판본을 돌려주게 했다. `_configure_candidate`에서는 결박 전 설정과 결박·서버 해석 뒤 설정이 같을 때만 재사용한다. 두 설정이 다르면 한 번 더 부르지만, 그때는 설정이 다르므로 같은 설정의 반복이 아니다.
- HIS-17은 `skipUnless` 제안 대신 OPS-02 동결에 흡수되었다. 통합표의 정정, 곧 건너뜀이 다른 오류까지 덮는다는 부작용은 이 결정으로 해당이 없어졌다.

## 8. 다른 그룹 범위에서 발견한 문제

- **REV 또는 STO 영역**: `test_redesign_STORAGE.py:1216`의 `_reviewed_candidate`가 `review_cycle.start_review`에 `owner_activity_id`를 넘긴다. 그러나 `review_cycle.py:108`의 `start_review`에는 그 인자가 없다. 이 때문에 시험 4건이 실패한다(5절). `c-int`에 이미 있는 실패다.
- **`references/과제-착수조건.md`와 `planning.EXPOSED_FIELDS`의 불일치**: `test_walkthrough_repairs.test_readiness_document_tables_match_the_condition_grammar`가 실패한다. 문서의 포인터 표에는 `knowledge` 등이 있고, `EXPOSED_FIELDS`에는 `goal-judgment` 등이 있다. `c-int`에 이미 있는 실패이며, `planning`이나 그 문서를 소유한 그룹의 범위다.
- **ENG 영역(선택)**: `engine.initialize`(`engine.py:152-167`)는 host 설정이 별칭 없이 들어오면 `validate_config` 안과 `build_profiles`에서 같은 설정으로 프로필을 두 번 만든다. 인스턴스당 한 번 도는 초기화라 이번에는 고치지 않았다. 고치려면 `validate_config`의 반환값을 재사용하면 된다. OPS-09의 선택 단계, 곧 엔진이 채우는 실행 프로필·온톨로지·기록 가족을 `initialize_state`로 옮기는 일도 남아 있다.
- **시험 단계 그룹**: `test_redesign_ENGINE.routing_engine`의 인스턴스에 옛 최상위 키 `goal`과 `policies`가 남아 있다. OPS-14 전에는 이 키들이 `validate_governance_state`를 거치면 거부되었을 것이다. 지금 이 고정물을 쓰는 시험은 통과하지만, 고정물이 현행 인스턴스 모양과 다르다.
