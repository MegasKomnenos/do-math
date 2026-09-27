# TSA: 시험 foundation 조각 정리 검토

이 문서의 경로는 따로 적지 않으면 `C:/math/.claude/skills/do-math/` 기준이다. 검토 기준 시점은 main `9b434f4`의 작업 트리다.

## 1. 읽은 범위

**전문을 읽은 영역 파일.** 대상은 `scripts/test_categories.py`의 `SHARDS['foundation']`에 이름이 있는 76개 모듈이며 합계는 20,377행이다. 모듈별 행 수는 다음과 같다.

| 모듈 | 행 | 모듈 | 행 | 모듈 | 행 |
|---|---|---|---|---|---|
| test_academic | 73 | test_git_store | 513 | test_redesign_OBSERVATION | 249 |
| test_boundary_repairs | 81 | test_impact_bundle | 439 | test_redesign_PROFILES | 1137 |
| test_budget | 143 | test_knowledge | 357 | test_redesign_REVIEWS | 601 |
| test_claude_adapter | 244 | test_knowledge_import_engine | 396 | test_redesign_STORAGE | 1329 |
| test_claude_stream | 138 | test_knowledge_io | 199 | test_redesign_SURFACE | 839 |
| test_codex_adapter | 221 | test_machine_scheduling | 75 | test_redesign_TASKS | 886 |
| test_completion_settlement | 147 | test_model_metadata_boundary | 87 | test_reference_catalog | 86 |
| test_context_store | 132 | test_model_runner | 151 | test_relation_dependencies | 95 |
| test_contract_checks | 167 | test_observation_audit1 | 143 | test_repair_execution | 124 |
| test_contracts | 117 | test_observations | 412 | test_repair_plan | 297 |
| test_control_preview | 70 | test_performance_repairs | 480 | test_reporting | 154 |
| test_control_transport_io | 237 | test_performance_save | 134 | test_repository | 330 |
| test_current_contract | 47 | test_planning | 202 | test_review_cycle | 306 |
| test_decision_basis | 195 | test_preparation_cache | 70 | test_review_scope_wire | 137 |
| test_delegation_storage | 113 | test_provider_final_contract | 88 | test_revision_obligations | 139 |
| test_digest_characterization | 100 | test_query_records | 115 | test_scholarly | 92 |
| test_environment_validation | 341 | test_questions | 187 | test_standalone | 62 |
| test_execution_observation_profile | 106 | test_reading_map | 81 | test_state_checks | 211 |
| test_execution_window | 54 | test_redesign_ACTIVITIES | 492 | test_state_contract_registration | 81 |
| test_file_io | 100 | test_redesign_CONTRACTS | 1089 | test_storage_validation | 41 |
| test_formal_input_manifest | 72 | test_redesign_EVIDENCE | 404 | test_task_scope | 210 |
| | | test_redesign_EVIDENCE_binding | 118 | test_test_runner | 180 |
| | | test_redesign_EVIDENCE_host | 91 | test_trust_continuation | 76 |
| | | test_redesign_EVIDENCE_run | 82 | test_unicode_flow | 113 |
| | | test_redesign_EVIDENCE_scope | 40 | test_walkthrough_contract_repairs | 312 |
| | | test_redesign_EVIDENCE_walkthroughs | 415 | test_walkthrough_repairs | 377 |
| | | test_redesign_GOVERNANCE | 1024 | | |
| | | test_redesign_KNOWLEDGE | 925 | | |
| | | test_redesign_LIFECYCLE | 206 | | |

**판정 기준으로 전문을 읽은 파일.** 이 세 파일의 후보는 TSB 영역이 소유하므로 여기에는 올리지 않았다.

- `scripts/tests/research_fixtures.py`(891행)
- `scripts/tests/state_fixtures.py`(121행)
- `scripts/tests/시험-지침.md`(70행)

**공통 문서와 과거 경량화 자료(전문).**

- `C:/math/임시/do-math-정리-검토-2026-09-27/기준.md`
- `AGENTS.md`
- `C:/math/docs/do-math/검사-경량화-이음새-계약.md`
- `C:/math/임시/경량화-조사-2026-09-26/TST.md`(577행)
- `C:/math/임시/경량화-조사-2026-09-26/결과-K시험.md`(204행)
- `C:/math/임시/시험-경량화-2026-09-26/계약.md`(62행)
- `C:/math/임시/시험-경량화-2026-09-26/진단-B4.md`(93행)
- `C:/math/임시/시험-경량화-2026-09-26/작업자-노드/`의 `B1-M-0350.md`, `B2-M-0350.md`, `B3-M-0350.md`, `B4-M-0350.md`, `B4-M-0351.md`, `W-fix-M-0351.md`

**일부만 읽은 파일.** 이음새 확인과 근거 확보에 필요한 범위만 읽었다.

- `C:/math/docs/do-math/경량화-설계-2026-09-26.md` 60-100, 165-200
- `C:/math/기억/layer1/M-0350.md` 30-70
- `scripts/check_coverage.py` 100-160, 284-313
- `scripts/do_math/repository.py` 226-228
- `scripts/do_math/file_io.py` 182-194
- `scripts/do_math/observations.py` 94-97
- `scripts/do_math/codex_adapter.py` 342
- `scripts/do_math/session_slots.py` 46, 326
- `scripts/do_math/submission.py` 1421-1458
- `scripts/do_math/engine.py` 74-83, 160, 557-574(검색 결과 줄)
- `scripts/tests/test_windows_job.py`(시험 이름과 표시만 검색)
- `C:/math/docs/do-math/implementation-v5/traceability.json`: 파이썬으로 좌표와 관찰만 추출했고, 사람이 전문을 읽지는 않았다.
- `C:/math-worktrees/tools/full1/report.json`과 `foundation-isolated-00*`: 조각별·시험별 시간만 추출했다.

**실행한 읽기 전용 확인.** 시험은 실행하지 않았다.

- 부하가 있는 기계에서 `git init -q` 자식 프로세스와 `research_fixtures.git_init` 복사의 소요 시간을 10회씩 두 번 쟀다. 임시 폴더만 썼다.
- `ast`로 git init을 부르는 setUp을 가진 클래스의 시험 수를 셌다.
- 추적표에서 foundation 시험을 인용한 좌표와, 그 좌표 가운데 보관 실행 관찰을 가진 것을 셌다.

파견문이 정한 파일 가운데 읽지 못한 것은 없다.

## 2. 영역 판정

세 경량화의 방향은 foundation 조각에 부분적으로만 적용되었다. 2라운드가 시험 기반(`bare_engine`, `create_autospec` 대입, `FixtureAdapter`, `review_items`)을 들였지만, 3라운드의 `git_init`·템플릿 전환은 다른 조각의 무거운 모듈에만 적용되었다. 이 조각에는 `git init` 자식 프로세스 약 190회, 손으로 조립한 엔진·저장소 대역, 다른 모듈의 TestCase를 픽스처 보관소로 쓰는 곳 58군데가 그대로 남아 있다. 조직도 문제다. 76개 모듈 가운데 25개(11,851행, 58%)가 성질이 아니라 만들어진 계기(`redesign`, `repairs`, `audit1`, `walkthrough`, `performance`)를 따라 이름이 붙었고, 같은 성질이 여러 모듈에 흩어져 약 20개 시험이 서로 겹친다. 성질별 구조 하나로 정리하는 데에는 제약이 하나 있다. 추적표 293행 가운데 231행이 foundation 시험 좌표 115개를 인용하고, 그중 82개는 보관 실행 관찰에 묶여 있다. 그래서 인용된 시험의 이름이나 위치를 바꾸면 추적표의 실행 요약이 바뀌므로, 전면 재편은 추적표를 계속 유지할지라는 결정에 달려 있다. 그 결정과 무관하게 바로 얻을 수 있는 것은 두 가지다. 하나는 `git_init` 전환으로 조각 시간(full1 실측 259초)을 약 15~65초 줄이는 것이고, 다른 하나는 인용되지 않은 중복·폐기·잔재 시험과 손 조립 픽스처 약 500행(TSA-03·04·07~10의 합)을 정리하는 것이다.

검토했고 없음: 파생상태, 문서, 결함, 임시방편, 비대. 불일관·미사용 성격의 발견은 TSA-01·TSA-06·TSA-09에 합쳐 적었다.

## 3. 후보

#### TSA-01 foundation 조각이 저장소를 `git init` 자식 프로세스로 만들어 조각 시간의 상당 부분을 쓴다
- 검토: 1
- 종류: 비용
- 좌표:
  - setUp에서 부르는 곳(클래스의 시험 수 합계 166개)
    - `scripts/tests/test_redesign_STORAGE.py:596`(80개)
    - `scripts/tests/test_git_store.py:49`(25개)
    - `scripts/tests/test_repository.py:91`(11개)
    - `scripts/tests/test_repository.py:222`(5개)
    - `scripts/tests/test_performance_save.py:33`(9개)
    - `scripts/tests/test_redesign_KNOWLEDGE.py:422`(KnowledgeAudit2 12개와, setUp을 빌리는 KnowledgeRawSource 7개)
    - `scripts/tests/test_unicode_flow.py:31`(6개)
    - `scripts/tests/test_query_records.py:32`(3개)
    - `scripts/tests/test_boundary_repairs.py:30`(3개)
    - `scripts/tests/test_redesign_TASKS.py:212`(3개)
    - `scripts/tests/test_repair_execution.py:46`(2개)
  - 시험 본문에서 부르는 곳 약 26회
    - `scripts/tests/test_execution_observation_profile.py:81`
    - `scripts/tests/test_formal_input_manifest.py:27`
    - `scripts/tests/test_impact_bundle.py:95`(`_seal_review`가 시험 5개에서 불린다)
    - `scripts/tests/test_redesign_ACTIVITIES.py:358`(setUp, 시험 5개)
    - `scripts/tests/test_redesign_CONTRACTS.py:157, 318, 399, 715`
    - `scripts/tests/test_redesign_EVIDENCE_walkthroughs.py:387`
    - `scripts/tests/test_redesign_KNOWLEDGE.py:296`
    - `scripts/tests/test_redesign_PROFILES.py:675`
    - `scripts/tests/test_redesign_SURFACE.py:481, 504, 603`
    - `scripts/tests/test_reporting.py:37, 124`
    - `scripts/tests/test_storage_validation.py:20`
    - `scripts/tests/test_git_store.py:466`
- 현상:
  - 시험 저장소를 매번 `subprocess.run(['git', ..., 'init', '-q'])`로 만든다.
  - `시험-지침.md` 4절 6항은 저장소를 만들 때 `git init` 자식 프로세스 대신 `git_init(path)`를 쓰라고 정한다. 3라운드 시험 경량화는 다른 조각의 모듈 약 25개를 이 방식으로 옮겼지만(`기억/layer1/M-0350.md` 33행), foundation 조각 76개 모듈에는 `git_init` 호출이 하나도 없다.
  - foundation 조각은 full1 통합 확인에서 258.6초가 걸렸다. 조각 목표는 120초다.
- 근거:
  - 검색식 `subprocess\.run\(\[.git.*init|\[.git., .-C., str\([^)]*\), .init.|git\(.*"init"`: 31건, 20개 파일. 모두 관련이 있다.
  - 검색식 `git_init\(`: foundation 모듈에서 0건.
  - 실측(부하 아래, 이 기계, 10회 평균 두 번): 자식 프로세스 `git init`은 0.403초와 0.268초, `git_init` 복사는 0.036초와 0.022초였다. W-fix 노드의 부하 아래 측정은 0.10초에서 0.02초였다(`W-fix-M-0351.md` 측정 절).
  - full1의 foundation 시험 행 합계는 190.1초이고, 그중 `test_redesign_STORAGE`가 80개 35.5초로 가장 크다(`C:/math-worktrees/tools/full1/report.json`).
- 제안:
  - 위 좌표를 `research_fixtures.git_init(path)`로 바꾼다.
  - `--object-format=sha256`가 필요한 세 곳은 자식 프로세스를 유지한다. 해당하는 곳은 `scripts/tests/test_git_store.py:392`, `scripts/tests/test_git_store.py:466`의 sha256 경우, `scripts/tests/test_redesign_STORAGE.py:974`다.
  - `test_unicode_flow.py`의 setUp은 저장소를 쓰는 두 시험만 저장소를 만들게 옮긴다. 나머지 네 시험은 저장소를 쓰지 않는다.
- 실익:
  - 약 187회 × 0.08~0.35초로, 조각 시간이 약 15~65초 준다.
  - 시험 지침과 이 조각이 다르게 움직이던 곳이 사라진다.
  - 바뀌는 줄은 약 30줄이고 삭제되는 줄은 거의 없다.
- 비용과 위험:
  - 20개 파일을 기계적으로 바꾼다. 새 상태·수명·복구 규칙은 없다.
  - `git_init`은 `git init -q`로 만든 빈 `.git`의 복사본이므로 GitStateStore 시험의 전제(새 저장소)가 같다.
  - `test_git_store.py:271-282`의 훅 시험은 init 뒤에 `git config`를 쓰므로 영향이 없다.
- 기능·커버리지 영향: 없음
- 사용자 결정 관련: 없음. 시간 목표(조각 120초)에 가까워지는 방향이다.
- 확신도: 추정. 좌표와 건수는 확인했다. 절감량은 foundation 조각을 변경 전후로 쌍 비교해 재면 확정된다(`시험-지침.md` 3절 7항의 방식).

#### TSA-02 계기 이름 모듈이 서로 무관한 성질을 섞고, 같은 성질을 여러 모듈에 흩어 놓는다
- 검토: 1
- 종류: 경계
- 좌표:
  - 계기 이름 모듈 25개(11,851행): `test_redesign_*` 17개(9,927행), `test_boundary_repairs`, `test_performance_repairs`, `test_performance_save`, `test_repair_plan`, `test_walkthrough_repairs`, `test_walkthrough_contract_repairs`, `test_observation_audit1`, `test_digest_characterization`
  - 계기 이름 클래스 25개: 예로 `scripts/tests/test_redesign_TASKS.py:68, 200, 495`(`AuditWorkflowTests`, `AuditPersistenceTests`, `FollowupRegressions`), `scripts/tests/test_redesign_KNOWLEDGE.py:411`(`KnowledgeAudit2`), `scripts/tests/test_redesign_PROFILES.py:867`(`Audit1Tests`), `scripts/tests/test_repair_plan.py:18, 184, 249`
  - 두 모듈에 같은 이름의 클래스가 있다: `scripts/tests/test_walkthrough_contract_repairs.py:21`, `scripts/tests/test_walkthrough_repairs.py:17`(`WalkthroughRepairs`)
  - 계기 번호 시험: `scripts/tests/test_redesign_ACTIVITIES.py:386, 394, 426, 454, 478`(`test_03`, `04`, `06`, `07`, `11`로, 지운 항목 자리가 비어 있다), `scripts/tests/test_redesign_SURFACE.py:176-340`(`test_audit_*` 8개)
  - 조각 밖 시험 모듈 import 29줄(lifecycle 17, review 6, host 3, academic 2, research 1)
- 현상:
  - 모듈 이름이 담는 성질을 말하지 않는다. 예로 `test_performance_repairs.py`는 상태 검사, 봉인 artifact, 도구 발견, 설치 목록, 후보 복사, 저장 값 영역, 제출 모양, 스냅숏 메타데이터라는 여덟 성질을 한 파일에 둔다(63, 167, 190, 223, 306, 329, 358, 422행).
  - 한 성질은 여러 모듈에 흩어져 있다.
    - 관찰 규칙과 추적기: `test_observations`, `test_redesign_OBSERVATION`, `test_observation_audit1`, `test_execution_observation_profile`, `test_claude_adapter.py:114`
    - 저장 값 영역(`canonical_json`): `test_redesign_STORAGE`, `test_repository`, `test_unicode_flow`, `test_performance_repairs`
    - 지식 환경 전이: `test_knowledge`, `test_redesign_KNOWLEDGE`
    - 재평가: `test_redesign_KNOWLEDGE` KnowledgeAudit2, `test_redesign_REVIEWS` AssessmentReassessmentTests
    - check_coverage: `test_redesign_EVIDENCE`의 TraceabilityCheckerTests, `test_redesign_EVIDENCE_binding`, `test_redesign_EVIDENCE_scope`
  - 그 결과로 TSA-03의 중복이 생겼다. `시험-지침.md` 4절 1항("같은 성질을 검사하는 시험이 이미 있는지 먼저 찾는다")은 이름으로 찾을 수 없는 조직에서 지키기 어렵다.
  - 제약이 하나 있다. 추적표 `docs/do-math/implementation-v5/traceability.json`의 293행 가운데 231행이 foundation 시험 좌표 115개(`파일::클래스.메서드`)를 인용한다. `check_coverage.validate`는 좌표가 현재 파일에 실재하는지 검사한다(`scripts/tests/test_redesign_EVIDENCE.py:300-301`). 115개 가운데 82개는 보관 실행 관찰에 묶여 있고, 좌표 이름이 바뀌면 `validate_observations`가 `observation: cited test outcome is not in the run`으로 거부한다(`scripts/check_coverage.py:141-148`).
- 근거:
  - 검색식 `redesign|repair|audit|walkthrough|characterization|performance`을 모듈 이름에 적용: 26개. `test_repair_execution`은 제품 모듈 이름이라 빼서 25개다.
  - 검색식 `^class \w*(Audit|Followup|Repair|Walkthrough|Redesign|Regression)\w*`: 25건.
  - 추적표 집계(파이썬): 현재 증거 좌표 143개, 그중 foundation 115개. 관찰을 가진 좌표 82개. foundation을 인용하는 행 231개.
  - 인용되지 않은 모듈: `test_performance_repairs`, `test_performance_save`, `test_boundary_repairs`, `test_repair_plan`, `test_walkthrough_repairs`, `test_walkthrough_contract_repairs`, `test_observation_audit1`, `test_execution_observation_profile`, `test_observations`, `test_digest_characterization`, `test_storage_validation`, `test_control_preview`, `test_current_contract` 등이다.
- 제안: 두 단계로 나눈다.
  1. 인용 좌표를 건드리지 않는 재편. 인용되지 않은 모듈을 제품 성질별 모듈로 흡수한다. 예는 다음과 같다.
     - `test_observation_audit1`과 `test_execution_observation_profile`을 `test_observations`로 합친다.
     - `test_performance_repairs`를 성질별로 나눈다: `BatchedInspectionTests`는 `test_state_checks`, `CandidateCopyTests`·`StorageValueTests`·`SealedArtifactTests`는 `test_repository`, `SnapshotMetadataTests`는 `test_git_store`, `SubmissionShapeWorkTests`는 `test_contracts`로 옮긴다.
     - `test_performance_save`와 `test_boundary_repairs`를 `test_repository`로 합친다.
     - `test_storage_validation`을 `test_state_contract_registration`으로 합친다.
     - `test_control_preview`를 `test_control_transport_io`로 합친다.
     - `test_repair_plan`과 두 `test_walkthrough_*_repairs` 모듈은 시험을 성질별 모듈로 나눈다.

     새 모듈을 만들지 않으므로 `SHARDS` 항목만 준다. 인용된 모듈 안의 계기 번호·`test_audit_*` 이름 가운데 인용되지 않은 것은 성질 이름으로 바꾼다.
  2. 인용된 `test_redesign_*` 모듈의 재편. 추적표의 역할을 먼저 정해야 한다(아래 사용자 결정 관련).
- 실익:
  - 1단계만으로 모듈 수가 약 76개에서 약 64개로 준다. 같은 성질을 한 파일에서 찾을 수 있게 되어 중복의 재발 여지가 준다.
  - 삭제 행 수는 TSA-03의 중복 정리와 겹치므로 여기서 따로 세지 않는다.
- 비용과 위험:
  - 1단계는 시험 이동과 이름 변경이므로 제품 변경이 없다. 새 상태·수명·복구 규칙도 없다.
  - `test_categories.SHARDS` 수정이 따른다. 이 파일은 TSB 소유다.
  - 이동한 시험이 다른 모듈의 픽스처를 쓰면 import가 바뀐다(TSA-05).
  - 2단계는 좌표 115개와 관찰 82개에 닿는다.
- 기능·커버리지 영향: 없음(이동과 이름 변경)
- 사용자 결정 관련: 있음. 결정 "시험 커버리지는 크게 바꾸지 않는다"와는 충돌하지 않는다. 다만 2단계의 전제인 추적표 v5(보관 실행과 시험 좌표를 묶은 기록)를 계속 유지할지는 이 영역이 정할 일이 아니다. 새로 드러난 사실은 인용 좌표 115개·관찰 82개의 규모다. 추적표의 소유는 HIS이고, 판단은 사용자에게 올린다.
- 확신도: 확인(현상과 건수). 모듈 수 감소 추정은 1단계 목록대로 옮기면 확정된다.

#### TSA-03 같은 성질을 같은 입력으로 겹쳐 단언하는 시험 약 20개
- 검토: 1
- 종류: 이음새
- 좌표: 아래 표. 앞쪽이 남길 시험이고, 뒤쪽이 지우거나 흡수할 시험이다. 인용 여부는 추적표 현재 증거 좌표 기준이다.

| 성질 | 남길 시험 | 지우거나 흡수할 시험(모두 추적표 미인용, (l)만 예외) |
|---|---|---|
| (a) 저장 값 영역: 소수·NaN·서로게이트·비문자열 키 거부와 유니코드 키 보존 | `scripts/tests/test_performance_repairs.py:330-345`, `scripts/tests/test_unicode_flow.py:36-50`(인용) | `scripts/tests/test_redesign_STORAGE.py:691-694`, `:798-802`, `:195-204`(NFD≠NFC 대조 한 줄만 남길 곳으로 옮긴다), `scripts/tests/test_repository.py:179-181` |
| (b) 초기 원문 입력의 정확한 UTF-8 표현 | `scripts/tests/test_redesign_STORAGE.py:1053-1061` | `scripts/tests/test_unicode_flow.py:100-109` |
| (c) 계획 스키마의 처분 목록 하나와 구 필드 부재 | `scripts/tests/test_contracts.py:108-113` | `scripts/tests/test_redesign_CONTRACTS.py:624-628` |
| (d) 지식 변경의 `independent_confirmation` 거부 | `scripts/tests/test_redesign_CONTRACTS.py:507-521` | `scripts/tests/test_contracts.py:28-33`(같은 시험의 앞 단언은 남긴다) |
| (e) 낡은 부모 head 저장은 CAS 충돌이고 승자가 남는다 | `scripts/tests/test_repository.py:109-114` | `scripts/tests/test_performance_save.py:97-104` |
| (f) 실시간 단조 시계 역행 판정 | `scripts/tests/test_redesign_LIFECYCLE.py:144-152` | `scripts/tests/test_redesign_LIFECYCLE.py:194-202` |
| (g) 학술 반박 해소는 증거 바이트가 그대로일 때만 현재다 | `scripts/tests/test_redesign_GOVERNANCE.py:204-218` | `scripts/tests/test_redesign_GOVERNANCE.py:333-341`(해석기 없는 기록 거부만 흡수) |
| (h) 산문이나 `resolved` 표지는 반박을 해소하지 않는다 | `scripts/tests/test_academic.py:36-44` | `scripts/tests/test_redesign_GOVERNANCE.py:502-518` |
| (i) 환경 무효화는 상수 폐포에 국한된다 | `scripts/tests/test_knowledge.py:264-272` | `scripts/tests/test_redesign_KNOWLEDGE.py:400-408` |
| (j) 환경 복구는 뒤따른 의미 정지를 풀지 않는다 | `scripts/tests/test_knowledge.py:301-308` | `scripts/tests/test_redesign_KNOWLEDGE.py:212-224` |
| (k) 프로필 결속: 위조 출처와 다른 실행 대상 거부 | `scripts/tests/test_execution_observation_profile.py:61-72` | `scripts/tests/test_observation_audit1.py:82-93`, `:98-105`(위조 출처 부분) |
| (l) 관찰 간격 경과 시 계수 부재는 `observation_unavailable`이고 0이 아니다 | `scripts/tests/test_redesign_OBSERVATION.py:176-185` | `scripts/tests/test_execution_observation_profile.py:44-59` |
| (m) 필수 개정 대상은 명시 해소가 있어야 한다 | `scripts/tests/test_decision_basis.py:170-176` | `scripts/tests/test_revision_obligations.py:128-136` |
| (n) 계약 해시는 계약 필드에만 반응한다 | `scripts/tests/test_planning.py:60-65` | `scripts/tests/test_redesign_TASKS.py:651-655` |
| (o) 준비 시작·종료의 종결 결과(start_failed와 cancelled) | `scripts/tests/test_redesign_ACTIVITIES.py:478-488`(인용) | `scripts/tests/test_redesign_ACTIVITIES.py:165-176`(cancelled 분기만 흡수) |
| (p) stdio MCP 제어 서버 자식의 제출·영수증 | `scripts/tests/test_redesign_PROFILES.py:151-264` | `scripts/tests/test_redesign_ACTIVITIES.py:299-323` |

- 현상:
  - 표의 각 쌍은 같은 제품 함수를 같은 종류의 입력으로 지나 같은 결과를 단언한다. 예를 들어 (e)는 두 시험 모두 두 번째 `ResearchRepository`로 같은 부모 head에 저장해 `GitStateStoreConflict`를 받고, 승자의 `status`가 `running`인지 본다. (f)는 두 시험 모두 단조 시계를 0에서 2로, UTC를 1초 움직여 `live_monotonic_regression`을 단언한다.
  - (p)에서 ACTIVITIES 쪽은 initialize, control_submit, pump, control_receipt만 하므로 PROFILES 쪽(tools/list, 제출, 영수증, self_check, 닫힘까지)의 부분집합이다.
  - 이 중복은 TSA-02의 조직에서 생겼다. `시험-지침.md` 4절 1항은 이를 "비용만 두 배"로 규정한다.
- 근거:
  - 각 쌍을 원문에서 줄 단위로 대조했다.
  - 인용 여부: 추적표 현재 증거 좌표 143개와 대조했다. 흡수 대상 가운데 인용된 것은 없다. (o)의 남길 쪽 `test_11_…`, (a)의 남길 쪽 `test_unicode_flow` 두 시험은 인용되어 있어 남기는 쪽으로 골랐다.
- 제안:
  - 오른쪽 시험을 지운다. 남길 시험이 갖지 않은 단언이 있으면 그 단언을 남길 시험으로 옮긴다: (a)의 NFD 대조, (g)의 해석기 없는 기록 거부, (o)의 cancelled 분기, (d)의 스키마 단계 단언.
  - 인용된 시험은 이름과 위치를 바꾸지 않는다.
- 실익: 시험 약 20개와 약 230행이 준다. 같은 규칙이 바뀔 때 고칠 곳이 쌍마다 하나로 준다. 실행 시간은 (p) 약 0.14초 등으로 작다(full1 실측).
- 비용과 위험:
  - 단언을 옮길 때 입력을 잘못 합치면 검사 강도가 바뀔 수 있다. 보호는 남길 시험 자체다.
  - 새 상태·수명·복구 규칙은 없다.
- 기능·커버리지 영향: 없음. 흡수할 단언을 옮기는 조건이다.
- 사용자 결정 관련: 없음. 결정 "커버리지는 크게 바꾸지 않는다"와 맞는다. 단언을 지우지 않고 옮긴다.
- 확신도: 확인(원문 대조와 인용 대조). 각 쌍의 입력 동치성은 읽어서 판정했고 실행하지는 않았다.

#### TSA-04 `test_impact_bundle`이 봉인된 영향 검토 실행 기록을 손으로 조립하고, 같은 거부 성질을 다시 단언한다
- 검토: 1
- 종류: 이음새
- 좌표:
  - `scripts/tests/test_impact_bundle.py:23-33`(`ImpactReviewTests(methodName=...).setUp()` 차용)
  - `scripts/tests/test_impact_bundle.py:44-111`(`_seal_review`)
  - `scripts/tests/test_impact_bundle.py:217-224`, `:252-262`
  - `scripts/tests/test_redesign_CONTRACTS.py:190-208`(`seal_review_fixture`)
  - `scripts/tests/test_redesign_CONTRACTS.py:349-364`(`tampered_output`, `stale` 경우)
- 현상:
  - `_seal_review`는 `submission_intent`와 `submission_receipt.payload.submission_check.artifacts`의 모양, `integrations` 행을 손으로 다시 적는다(68-94행).
  - 같은 목적의 CONTRACTS 픽스처는 제품의 `ResearchEngine._stage_submission_capture`로 봉인 기록을 만든다(203행).
  - 봉인 기록 모양이라는 하나의 지식이 제품 함수 하나와 시험 사본 하나에 있다. 2라운드에서 실행의 `input_sha256`를 지우고 `input_manifest`를 읽게 바꿨을 때 손 대역이 따라가지 못해 시험이 깨진 기전(`진단-B4.md` 2절 2항, `B4-M-0350.md` 터득한 것)과 같은 구조다.
  - `test_review_rejects_changed_sealed_output…`(217-224)은 CONTRACTS의 `tampered_output`(356-359)과, `test_external_premise_change…`(252-262)은 `stale`(354)과 같은 성질이다.
- 근거:
  - 원문 대조.
  - 추적표에 인용된 것은 `test_impact_bundle`의 `test_bundle_level_reviewed_effect_is_applied_once`와 `test_coupled_changes_use_the_single_reviewed_s0_plan` 두 개뿐이다(현재 증거 좌표 집계).
- 제안:
  - `_seal_review`가 봉인 기록을 제품 `_stage_submission_capture`로 만들게 바꾼다. 이 호출은 `bare_engine()` 위에서 한다(TSA-06).
  - 중복 거부 시험 두 개를 지운다.
  - 인용된 두 시험은 제자리에 둔다.
- 실익:
  - 손 조립 약 45행과 시험 2개(약 20행)가 준다.
  - 봉인 기록 모양의 정의가 제품 하나로 모인다.
- 비용과 위험:
  - `_stage_submission_capture`가 요구하는 입력(`sealed`, 수신 영수증)을 만들어야 한다. CONTRACTS 픽스처가 이미 그 경로를 쓰므로 새 상태는 없다.
  - 대상 파일 2개.
- 기능·커버리지 영향: 없음
- 사용자 결정 관련: 없음
- 확신도: 확인

#### TSA-05 같은 픽스처 개념을 모듈마다 따로 만들고, 다른 모듈의 TestCase를 픽스처 보관소로 쓴다
- 검토: 1
- 종류: 이음새
- 좌표:
  - 지식 후보 사전
    - 같은 필드와 값: `scripts/tests/test_knowledge.py:13-18`, `scripts/tests/test_redesign_KNOWLEDGE.py:21-24`
    - 변형: `scripts/tests/test_redesign_EVIDENCE.py:124-126`, `scripts/tests/test_redesign_STORAGE.py:1205-1207`
  - 합성 검증 형식 증거: `scripts/tests/test_knowledge.py:21-28`(`evidence`), `scripts/tests/test_redesign_KNOWLEDGE.py:51-56`, `scripts/tests/test_redesign_EVIDENCE.py:140-144`
  - checkpoint 계수 관찰 규칙: `scripts/tests/test_redesign_OBSERVATION.py:22-29`, `scripts/tests/test_execution_observation_profile.py:16-22`(인자 `execution_id`는 쓰이지 않는다), `scripts/tests/test_redesign_EVIDENCE_walkthroughs.py:78-81`, `scripts/tests/test_redesign_PROFILES.py:438-441`. 공유 픽스처에도 `research_fixtures.supply_observation_rules`가 있다(TSB).
  - 승인된 헌장 하나로 초기화한 거버넌스
    - `scripts/tests/test_redesign_GOVERNANCE.py:26-41`
    - `scripts/tests/test_redesign_SURFACE.py:31-39`
    - `scripts/tests/test_redesign_EVIDENCE.py:64-73`
    - `scripts/tests/test_redesign_STORAGE.py:920-929`
    - `scripts/tests/test_decision_basis.py:85-91`
    - `scripts/tests/test_redesign_GOVERNANCE.py:531-537`
    - 공유 픽스처에도 `research_fixtures.charter_record`가 있다(TSB).
  - TestCase 인스턴스를 픽스처로 쓰는 곳 58군데(18개 파일). 대표 사용처는 다음과 같다.
    - `DomainGovernanceTests().initial()` 7곳
    - `AssessmentApplicationTests().fixture()/apply()` 13곳
    - `KnowledgeRedesign().verified()` 7곳
    - `ReviewCycleTests().output()` 5곳
    - `StorageRedesignTests()`와 `ImpactReviewTests().setUp()` 차용 5곳
    - 조각 밖의 `CentralGovernanceTests().host()`, `InitialIntentConnectionTests().applied()`, `InputRecoveryPublicTests()`, `CompletionBasisTests()`
- 현상:
  - 헌장 모양이 바뀌면 6곳 이상을, 형식 증거 모양이 바뀌면 3곳을 따로 고쳐야 한다.
  - 픽스처가 시험 클래스의 메서드에 있어, 그 클래스를 고치면 다른 모듈이 조용히 바뀐다. 3라운드에서 실제로 두 번 일어났다.
    - B3는 `InputRecoveryPublicTests.setUp`을 바꿨다가 다른 모듈 여덟 곳이 빌려 쓰는 것을 뒤늦게 발견하고 되돌렸다(`작업자-노드/B3-M-0350.md` 터득한 것 첫 문단).
    - B4는 `DomainGovernanceTests.import_fixture`를 바꾸며 호출 19곳을 고쳤다(`작업자-노드/B4-M-0351.md` 터득한 것 넷째 항).
  - foundation 모듈 37개가 다른 시험 모듈을 import하고(107줄), 그중 29줄은 다른 조각의 모듈이다.
- 근거:
  - 검색식 `\b[A-Z]\w*(Tests?|Redesign|Repairs|Audit2|Harness)\((methodName=[^)]*)?\)(\.|$)|\b[A-Z]\w*(Tests?|Audit2)\.(setUp|host|fixture|output|response|verified|initial|import_fixture|checked_import|applied|audit_host)\b`: 58건, 18개 파일. 같은 모듈 안의 사용도 포함하며 모두 관련이 있다.
  - import 집계: 정규식 `^\s*(from\s+(test_\w+)\s+import|import\s+(test_\w+))`로 foundation 모듈을 스캔했다.
- 제안:
  - 조각을 넘어 쓰이는 픽스처(헌장·거버넌스, 지식 후보·형식 증거, 관찰 규칙)는 `research_fixtures`의 모듈 함수 하나씩으로 모은다. `research_fixtures`는 TSB 소유이므로 TSB와 같은 작업으로 한다.
  - 모듈 안에서만 쓰는 TestCase 픽스처 메서드는 그 모듈의 모듈 함수로 옮긴다.
  - 사용처 수 상위 넷(`initial`, `AssessmentApplicationTests`, `verified`, `ReviewCycleTests.output`, 합계 32곳)부터 한다.
  - 이는 2라운드에서 기각된 TST-06의 범위를 줄여 다시 여는 것이다. 기각의 이유는 "제품 이음새가 아니고 79곳을 바꾼다"였다(`docs/do-math/경량화-설계-2026-09-26.md` 5절). 그 뒤 3라운드에서 이 결합이 실제로 두 작업자의 작업을 되돌리거나 늘렸다는 사실이 새로 드러났다.
- 실익:
  - 헌장·증거·규칙 조립 사본 약 12곳(약 80행)이 준다.
  - 픽스처 소유 위치가 명시되어, 한 클래스를 고칠 때 다른 모듈이 조용히 바뀌는 여지가 줄어든다.
  - TSA-02의 모듈 이동이 쉬워진다.
- 비용과 위험:
  - 18개 파일의 사용처를 바꾼다.
  - 픽스처 메서드가 `self.assert*`를 쓰면 함수로 옮길 때 실패 형태가 바뀐다(TST-06의 위험 기술 그대로).
  - 새 상태·수명·복구 규칙은 없다.
- 기능·커버리지 영향: 없음
- 사용자 결정 관련: 없음. TST-06 기각은 통합자 판단이었다(기준 3절의 사용자 결정 목록에 없다).
- 확신도: 확인(사본과 사용처). 사용처별 `self` 의존 정도는 읽은 곳만 확인했다.

#### TSA-06 K-시험이 후속으로 남긴 손 대역과 믹스인 직접 인스턴스가 foundation에 그대로 남아 있다
- 검토: 2
- 종류: 공백
- 좌표:
  - 믹스인 직접 인스턴스: `scripts/tests/test_decision_basis.py:18, 61`(`DecisionEngineMixin()`), `scripts/tests/test_questions.py:59, 73, 91, 166`(`QuestionEngineMixin()`)
  - `SimpleNamespace` 엔진에 제품 메서드를 비결합 호출하는 곳
    - `scripts/tests/test_observations.py:373-390`(`ResearchEngine._observe_running(fake, …)`에 `_controls`·`_check_conversations`·`_save`·`_enqueue` 람다)
    - `scripts/tests/test_machine_scheduling.py:24-27, 36-38, 54-60`(람다 여섯 개로 스케줄러 표면을 복제)
    - `scripts/tests/test_redesign_CONTRACTS.py:202-205`
    - `scripts/tests/test_walkthrough_contract_repairs.py:176-177`
  - 손 저장소 대역
    - `scripts/tests/test_performance_repairs.py:55-60`(`ResearchRepository.__new__`와 수동 속성)
    - `scripts/tests/test_performance_repairs.py:425-438`(`GitStateStore.__new__`와 `ref`·`_held_head`·`object_format`·`_git` 수동 설정)
    - `scripts/tests/test_redesign_EVIDENCE.py:35-52`(`InputSnapshot`)
    - `scripts/tests/test_reporting.py:82-85, 108`
    - `scripts/tests/test_redesign_PROFILES.py:761-765, 803-807`(spec 없는 `Mock()` 저장소)
- 현상:
  - 2라운드는 엔진 대역을 제품 초기화 위에 세우고(TST-01), 협력자 대역에 존재·서명 검사를 강제했다(TST-02). 그런데 위 좌표는 아직 제품 인터페이스를 손으로 복제한다.
  - K-시험은 이 가운데 두 곳을 "후속으로 `bare_engine`으로 바꿀 후보"로 남겼다(`임시/경량화-조사-2026-09-26/결과-K시험.md` 5절 7항).
  - 손 대역이 제품을 따라가야 했던 흔적도 있다. `InputSnapshot`의 `git_dir = None`과 `view`는 2라운드 커밋 `379a171`에서 제품 변경에 맞추려고 더해졌다(`git blame` 37, 43-45행).
- 근거:
  - 원문 대조, `git blame`, `결과-K시험.md` 5절.
  - 보존 판정 80건 가운데 이 영역에 해당하는 "프로세스 경계를 흉내 내는 손 대역"(`test_model_runner`의 `Job`·`Execution`·`Adapter`, `test_codex_adapter`의 `_FakeJob`, `test_test_runner`의 `Job`; `TST.md` 3절 4항)은 위 목록에서 뺐다.
- 제안:
  - 엔진 쪽은 `bare_engine(...)`과 `create_autospec(engine.X, ...)` 대입(K-시험이 정한 표준 형태)으로 바꾼다.
  - 저장소 쪽은 `create_autospec(ResearchRepository, instance=True)`로 바꾼다. `GitStateStore`는 `object.__new__` 대신 실제 생성자 위에서 `_git`만 autospec으로 대체한다.
- 실익:
  - 제품이 메서드나 속성을 바꿀 때 조용히 어긋나는 대역 약 14곳이 즉시 실패하는 대역으로 바뀐다.
  - 2라운드의 "`view`/`git_dir`를 대역마다 손으로 더하기" 유형의 수리가 사라진다.
  - 행 수는 거의 같다.
- 비용과 위험:
  - autospec이 드러내는 잘못된 인자 호출이 있으면 고쳐야 한다. 그것이 목적이다.
  - `GitStateStore` 생성자는 실제 저장소 경로를 요구하므로, 경로 인자를 `git_init`으로 만든 빈 저장소로 준다(TSA-01).
  - 새 상태·수명·복구 규칙은 없다.
- 기능·커버리지 영향: 없음
- 사용자 결정 관련: 없음
- 확신도: 확인

#### TSA-07 폐기된 기능·이름이 없다는 것만 확인하는 시험과 단언
- 검토: 2
- 종류: 낡음
- 좌표:
  - `scripts/tests/test_redesign_PROFILES.py:344-355`(`test_session_slots_has_only_git_authority`)
    - 제품 소스 문자열에 `sqlite3`가 없는지 본다.
    - `SessionSlots`에 넘기지도 않은 임시 폴더가 비어 있는지 단언한다. 이 단언은 실패할 수 없다(`scripts/do_math/session_slots.py:46`의 생성자는 폴더를 받지 않는다).
    - `SessionSlots()`의 `TypeError`와 `isinstance`를 본다.
  - `scripts/tests/test_redesign_STORAGE.py:565-570`(지운 `task_readiness` 가족 거부), `:509-511`(평탄 `goal` 거부). 둘 다 `:696-699`의 미등록 가족 거부와 같은 성질이다.
  - 구 설정 이름 목록으로 닫힌 설정을 검사하는 곳: `scripts/tests/test_current_contract.py:14-24`(구 설정 10종), `scripts/tests/test_redesign_PROFILES.py:116-121`(구 관찰 설정 3종)
  - `scripts/tests/test_redesign_OBSERVATION.py:36-47`: 결정 3으로 지운 출처 `execution_events`와 연산자 `event_recorded`·`active_duration_gte`를 부분 시험으로 거부한다. 미지원 연산자 거부는 40-41행이 이미 본다.
  - `scripts/tests/test_redesign_STORAGE.py:193, 227`, `scripts/tests/test_unicode_flow.py:67`: 구 저장 봉투 인코딩 `utf8_base64`의 부재 단언. `test_unicode_flow`의 두 시험 이름(52행 `…schema_two`, 69행 `…schema_one`)도 구 봉투 판본을 가리킨다.
  - `scripts/tests/test_redesign_CONTRACTS.py:786, 792`: 구 필드 `completion_criteria`·`decision`의 부재 단언
  - `scripts/tests/test_walkthrough_contract_repairs.py:22-36`: 지운 CLI 옵션 `--goal-kind`
  - `scripts/tests/test_planning.py:119-120`: 구 조건 상태 값
  - 구 개념을 가리키는 시험 이름
    - `scripts/tests/test_redesign_ACTIVITIES.py:218`(`…_not_sqlite`)
    - `scripts/tests/test_model_metadata_boundary.py:15`(`…without_a_legacy_projection`)
    - `scripts/tests/test_redesign_GOVERNANCE.py:681`(`…legacy_criteria…`)
- 현상:
  - `AGENTS.md`는 "폐기한 기능만 검사하는 테스트는 제거하고, 유지하는 기능의 검사는 새 계약에 맞춘다"고 정한다.
  - 위 단언은 현재 계약의 성질이 아니라 "옛 이름이 없다"는 것을 본다.
  - 현재 계약은 닫힌 스키마(`additionalProperties: false`, 미등록 가족 거부, `config_schema()`)로 모든 미지의 이름을 거부하고, 그 성질은 일반형 시험이 따로 본다(`test_redesign_STORAGE.py:696-699`, `:774-779`).
  - 옛 이름을 나열한 시험은 새 계약이 바뀔 때 따라 고칠 대상만 늘린다.
- 근거:
  - 검색식 `utf8_base64|sqlite|legacy|retired|obsolete|removed_|_removed|old_state_helper|old_compact|old_rules`: 33건, 13개 파일. 그중 이 후보에 해당한다고 판정한 것은 위 좌표이고, `test_digest_characterization`은 TSA-10으로 뺐다.
  - 추적표 인용: `test_unicode_flow`의 `…schema_two`·`…schema_one`과 `test_redesign_OBSERVATION`의 `test_rules_bind_operator_subject_unit_and_evidence`는 인용되어 있다. 나머지는 인용되지 않았다.
- 제안:
  - `test_session_slots_has_only_git_authority`를 지운다.
  - STORAGE 565-570과 509-511은 지운다. 미등록 가족 성질은 696-699가 본다.
  - 구 설정 목록 두 곳은 발명한 키 하나로 닫힌 설정을 보는 시험 하나로 줄인다.
  - OBSERVATION 42-47의 부분 시험과 36-37의 `execution_events` 행, `utf8_base64` 부재 단언 세 줄, CONTRACTS의 구 필드 부재 두 줄은 지운다. 인용된 시험은 이름과 위치를 그대로 두고 본문만 고친다.
  - `--goal-kind` 시험은 "알 수 없는 옵션은 저장소를 만들기 전에 거부된다"는 현재 성질을 발명한 옵션 이름으로 단언하게 바꾼다.
  - 구 개념 시험 이름 세 개는 성질 이름으로 바꾼다. 셋 다 인용되지 않았다.
- 실익:
  - 시험 약 3개와 약 60행이 준다.
  - 실패할 수 없는 단언 하나가 사라진다.
  - 폐기 경위가 시험 본문과 이름에서 빠진다.
- 비용과 위험:
  - 옛 이름이 다시 들어오는 회귀는 일반형 닫힘 시험이 잡는다. 이 전제는 닫힌 스키마가 유지될 때만 성립한다.
  - 새 상태·수명·복구 규칙은 없다.
- 기능·커버리지 영향: 있음. 옛 이름을 명시적으로 나열한 회귀 검사가 사라진다. 일반형 거부 검사가 같은 입력군을 덮는다.
- 사용자 결정 관련: 없음(`AGENTS.md` 개발 원칙과 결정 1·3·6의 방향)
- 확신도: 확인

#### TSA-08 구현 전 단계의 존재 확인 단언과 그 포장 도우미
- 검토: 2
- 종류: 잔재
- 좌표:
  - 인라인 존재 단언 21곳
    - `scripts/tests/test_claude_adapter.py:207`
    - `scripts/tests/test_git_store.py:196, 344`
    - `scripts/tests/test_redesign_ACTIVITIES.py:410, 428, 480`
    - `scripts/tests/test_redesign_CONTRACTS.py:682, 887, 1024`
    - `scripts/tests/test_redesign_KNOWLEDGE.py:96, 321, 345`
    - `scripts/tests/test_redesign_PROFILES.py:524, 635, 838, 889, 979, 1126`
    - `scripts/tests/test_redesign_TASKS.py:619, 624`
  - 존재를 확인한 뒤 import하는 도우미 3개
    - `scripts/tests/test_redesign_CONTRACTS.py:903-906`(`integration()`, 17회 호출)
    - `scripts/tests/test_redesign_PROFILES.py:382-386`(`profiles()`, 32회 호출)
    - `scripts/tests/test_claude_adapter.py:136-139`(`module()`, 7회 호출)
  - 존재만 확인하는 시험 하나: `scripts/tests/test_redesign_STORAGE.py:722-724`(`test_public_candidate_and_record_evidence_apis_exist`)
- 현상:
  - `assertTrue(hasattr(activities, "bind_action"), "working action loses durable queue binding")`처럼, 기능이 아직 없던 단계의 실패 메시지를 가진 존재 확인이 남아 있다. `"Claude CLI support is missing"`, `"immutable execution profiles are absent"`, `"bundle application must exist, not just response metadata"`도 같은 부류다.
  - 바로 다음 줄이 그 함수를 부르므로, 없으면 어차피 `AttributeError`나 `ImportError`로 실패한다. 존재 단언은 검출력이 없고 역사적 메시지만 남긴다.
- 근거:
  - 검색식 `hasattr\(|find_spec\(|callable\(getattr|inspect\.signature\(`: 26건, 10개 파일. 그중 관련 있는 것은 24건이다. `test_context_store.py:97`의 `skipUnless(hasattr(os,'symlink'))`와 `test_redesign_EVIDENCE.py:135`·`test_redesign_KNOWLEDGE.py:483`의 제어 흐름용 `hasattr`는 뺐다.
  - 도우미 호출 수는 `grep -c`로 셌다(17, 32, 7).
  - STORAGE 722-724는 추적표에 인용되지 않았다.
- 제안:
  - 인라인 존재 단언을 지운다.
  - 세 도우미는 모듈 머리의 일반 import로 바꾸고 호출부를 모듈 참조로 바꾼다. 예: `self.integration()`을 `integration`으로 바꾼다.
  - 존재만 보는 시험 하나는 지운다.
- 실익: 약 30행과 시험 1개가 줄고, 구현 전 단계의 메시지가 사라진다.
- 비용과 위험: 파일 8개를 기계적으로 바꾼다. 인용된 시험의 이름은 바뀌지 않는다. 새 상태·수명·복구 규칙은 없다.
- 기능·커버리지 영향: 없음. 호출 자체가 같은 실패를 낸다.
- 사용자 결정 관련: 없음
- 확신도: 확인

#### TSA-09 쓰이지 않는 두 번째 시험 실행기와 감사용 부수 출력이 시험에 남아 있다
- 검토: 2
- 종류: 잔재
- 좌표:
  - `scripts/tests/test_redesign_EVIDENCE_run.py:1-82`
    - 시험이 하나도 없는 모듈이다.
    - 자체 `manifest()` 해시, `RecordedResult`, `report.json`·`run.log`·`changed_during_run`을 가진 별도 실행기다.
    - `SHARDS['foundation']`에 등록되어 있다(`scripts/test_categories.py:30`).
  - `scripts/tests/test_knowledge_import_engine.py:306-310`: 환경변수 `DO_MATH_KNOWLEDGE_AUDIT_DIR`가 있으면 감사 JSON을 쓴다.
  - `scripts/tests/test_observation_audit1.py:126-143`: `__main__`에 `--evidence` 증거 파일 출력이 있다.
  - `scripts/tests/test_redesign_STORAGE.py:1318`: `print("STORAGE no-op blob writes:", …)`. 3라운드 커밋 `9b434f4`가 이 줄을 고치면서 남겼다(`git show 9b434f4`).
  - 작업 경위를 설명하는 docstring: `scripts/tests/test_state_checks.py:3-4`("These replace the v4 FakeEngine academic end-to-end fixture…")
- 현상:
  - `test_redesign_EVIDENCE_run`은 `run_tests.py`의 역할(시험 선택, 판본 해시, 실행 중 변경 감지, 결과 JSON)을 따로 구현한 두 번째 실행기다.
  - 이 실행기의 출력을 소비할 추적표 `runs`는 비어 있다. 추적표의 보관 실행은 `observed_runs` 형식(`run.json`·`stderr.txt`)을 쓴다(`scripts/check_coverage.py:106-113`).
  - 시험이 없어 plain unittest로 돌리면 종료 코드 5가 난다(`진단-B4.md` 3절 표).
  - 감사 디렉터리 환경변수와 `--evidence` 옵션을 쓰거나 부르는 곳은 없다.
- 근거:
  - 검색식 `test_redesign_EVIDENCE_run|EVIDENCE_run`(저장소 전체, `.git`과 `임시/do-math-*` 보관소 제외): `test_categories.py`와 생성 사본 `.agents/`, graphify 그래프만 나온다.
  - 검색식 `DO_MATH_KNOWLEDGE_AUDIT_DIR`: 이 시험과 그 사본(`.agents/`, `.skill-workspace/`)만 나온다.
  - 검색식 `observation_audit1`: `test_categories.py`와 사본만 나온다.
  - 추적표 `runs` 키는 비어 있다(파이썬 집계).
  - 검색식 `^\s*print\(|[^_]print\("`: 3건 중 실행기 2건을 빼면 STORAGE 1건이 관련이 있다.
- 제안:
  - `test_redesign_EVIDENCE_run.py`를 지우고 `SHARDS`에서 이름을 뺀다(`test_categories.py`는 TSB 소유).
  - 감사 디렉터리 쓰기, `--evidence` 블록, `print` 줄을 지운다.
  - `test_state_checks.py`의 docstring은 현재 성질만 적게 고친다.
- 실익:
  - 약 110행이 준다.
  - 시험 실행기의 정의가 `run_tests.py` 하나로 준다.
  - 시험 없는 모듈을 등록 규칙 때문에 조각에 두는 일이 사라진다.
- 비용과 위험:
  - 추적표 `runs` 형식을 새로 채울 생산자가 없어진다. `check_coverage`의 `runs` 검증(284-313행)이 쓰일 곳도 함께 사라지므로, 그 정리는 OPS와 HIS에서 판단한다(5절).
  - 새 상태·수명·복구 규칙은 없다.
- 기능·커버리지 영향: 없음. 지우는 모듈에는 시험이 없다.
- 사용자 결정 관련: 없음
- 확신도: 확인

#### TSA-10 `test_digest_characterization`이 지운 도우미를 신탁으로 다시 구현해 동어반복을 단언한다
- 검토: 2
- 종류: 잔재
- 좌표: `scripts/tests/test_digest_characterization.py:1-5, 40-63`(지운 도우미 신탁과 그 이름 목록 주석), `:67-76`, `:90-96`
- 현상:
  - 이 모듈은 1라운드(`8d2ffd0`)가 digest 도우미를 두 정본으로 합칠 때 바이트 동일성을 보이려고 만든 특성화 시험이다.
  - 신탁은 이제 정본 본문과 같다.
    - `old_state_helper`는 `hashlib.sha256(canonical_json(value)).hexdigest()`로, `repository.exact_content_hash`의 본문과 같다(`scripts/do_math/repository.py:226-228`).
    - `old_compact_with_nan_guard`는 `file_io.compact_json_bytes`와 `json_digest`의 본문과 같다(`scripts/do_math/file_io.py:182-194`).
  - 그래서 67-76행과 90-96행은 구현을 구현과 비교한다.
  - 주석(41-43, 48-49, 55-56, 62행)은 `execution_profiles._digest`, `initialization.digest`, `academic._hash`처럼 지금은 없는 이름을 나열한다.
  - 저장된 digest의 안정성을 실제로 지키는 것은 고정값 비교(78-83행)와 비유한 값 거부(85-88행)뿐이다.
- 근거: 원문 대조, `git log`(생성 `8d2ffd0`, 수정 `9b434f4`). 추적표에 인용되지 않았다.
- 제안:
  - 신탁 네 개와 신탁 비교 시험 세 개를 지운다.
  - 고정값 비교를 늘려 값 영역을 덮는다. 유니코드 정규형, 중첩, 빈 값, 소수(json_digest), 관찰 규칙 digest(`_raw_json`)의 고정값을 각 하나씩 둔다.
  - 모듈을 `test_file_io`나 `test_repository`로 합친다(TSA-02 1단계).
- 실익: 약 60행이 준다. 지워진 이름을 가리키는 주석이 사라진다. 저장 digest를 지키는 성질은 고정값으로 더 직접 남는다.
- 비용과 위험: 고정값을 새로 계산해 적어야 한다. 새 상태·수명·복구 규칙은 없다.
- 기능·커버리지 영향: 없음. 동어반복 단언만 사라지고, 고정값 단언은 늘어난다.
- 사용자 결정 관련: 없음
- 확신도: 확인

## 4. 보존 판정

- **실제 git init이 필요한 곳.** 좌표는 `scripts/tests/test_git_store.py:392`, `:466`(sha256)과 `scripts/tests/test_redesign_STORAGE.py:974`다. `--object-format=sha256` 저장소는 빈 sha1 `.git`의 복사로 만들 수 없다. `test_git_store.py:404-509`의 Git 배관 신탁 시험도 실제 git이 검사 대상이다.
- **자식 프로세스를 유지하는 시험.** 이 시험들의 검사 대상은 프로세스 시작 그 자체이므로 자식 프로세스를 유지한다.
  - `scripts/tests/test_codex_adapter.py:120-124`: worker의 직접 적재
  - `scripts/tests/test_standalone.py:23-36`: 복사한 스킬의 `probe_cli.py`
  - `scripts/tests/test_redesign_CONTRACTS.py:72-87, 649-679`: 설치된 zip 검사기의 시작과 종료 코드
  - `scripts/tests/test_redesign_PROFILES.py:829-834`: 감독 실행기의 `--help`
  - `scripts/tests/test_control_preview.py:41-70`: preview 종류로 MCP 도구 열거형과 구조 결과를 확인한다. PROFILES 쪽 시험에는 이 부분이 없다.
- **같은 성질을 다른 층에서 보는 시험.** 이 쌍은 TSA-03에 넣지 않았다. 도메인 함수 시험은 규칙을, 엔진 시험은 소비자 배선을 본다.
  - 재평가: `scripts/tests/test_redesign_KNOWLEDGE.py:411-733`(도메인 함수)과 `scripts/tests/test_redesign_REVIEWS.py:390-597`(엔진 소비자)
  - continuation 복원: `scripts/tests/test_redesign_SURFACE.py:249-286`(엔진·실제 Git)과 `:340-377`(순수 함수와 음성 경우)
- **실제 시계 표본.** `scripts/tests/test_redesign_LIFECYCLE.py:156-168`은 200회 `time.sleep(.002)`를 쓴다. Windows 시계 양자화라는 실제 호스트 성질이 대상이므로 고정 대기 금지(`시험-지침.md` 4절 5항)의 대상이 아니다. full1 실측은 0.42초였다.
- **실제 Lean 시험과 그 격리 표시.** `scripts/tests/test_knowledge_import_engine.py:260-393`, `scripts/tests/test_redesign_KNOWLEDGE.py:28-41, 855-861`이다. 실제 컴파일러와 게시 경계가 대상이다.
- **추적표 앵커 이름.** `scripts/tests/test_redesign_EVIDENCE.py:164-236`의 `test_vNN_*`와 `scripts/tests/test_redesign_EVIDENCE_walkthroughs.py:99-412`의 `test_wNN_*`는 설계 벡터·걸음 번호를 가리키며 추적표에 인용되어 있다. 계기 이름이 아니다.
- **문서 예시를 실행하는 시험.** `scripts/tests/test_walkthrough_repairs.py:235-294, 364-373`이다. 2라운드 보존 판정(`TST.md` 3절 2항)을 그대로 따른다.
- **프로세스 경계 손 대역.** `scripts/tests/test_model_runner.py:7-26`, `scripts/tests/test_codex_adapter.py:19-21`, `scripts/tests/test_test_runner.py:99-104, 146-154, 164-170`이다. 2라운드 보존 판정(`TST.md` 3절 4항)을 따르며 TSA-06에서 뺐다.
- **`RACY_NS` 패치.** `scripts/tests/test_file_io.py:64`, `scripts/tests/test_control_transport_io.py:223`, `scripts/tests/test_observations.py:68`, `scripts/tests/test_preparation_cache.py:46`, `scripts/tests/test_performance_repairs.py:243, 263`, `scripts/tests/test_redesign_PROFILES.py:663`, `scripts/tests/test_redesign_SURFACE.py:555`에 있다. 방금 만든 파일은 생성 시각을 과거로 돌릴 수 없어 정착 규칙을 시험에서 끄는 것이다. 각 시험은 정착 뒤의 재사용을 대상으로 하므로 임시방편이 아니다.

## 5. 영역 밖 관찰

- TSB: `scripts/tests/research_fixtures.py:204-207`의 `new_instance`가 `git init` 자식 프로세스를 쓴다. foundation에서 3곳이 쓰고 다른 조각에서도 쓴다. TSA-01과 같은 방식으로 `git_init`을 쓰면 된다.
- TSB: `scripts/test_categories.py:30`의 `test_redesign_EVIDENCE_run` 등록. TSA-09를 채택하면 함께 지운다. TSA-02 1단계의 모듈 이동도 `SHARDS` 수정을 동반한다.
- TSB: 조각 밖 시험 모듈이 foundation의 픽스처 공급처다. 대상은 `test_input_recovery.InputRecoveryPublicTests.setUp`, `test_governance_engine.CentralGovernanceTests.host`, `test_review_engine.FakeEngine`, `test_lifecycle_engine.FakeEngine`(TST-03 부분 구현으로 `_save`·`_controls` 재정의가 남음)이다. TSA-05의 모듈 함수화와 같은 판단이 필요하다.
- OPS: `scripts/check_coverage.py:284-313`의 추적표 `runs` 검증(`log_path`·`report_path`)은 생산자가 `test_redesign_EVIDENCE_run.py` 하나뿐이고, 현재 추적표의 `runs`는 비어 있다.
- HIS: 추적표 `docs/do-math/implementation-v5/traceability.json`이 foundation 시험 좌표 115개와 보관 관찰 82개를 묶는다. 이 결합이 시험 조직 재편의 비용을 정한다(TSA-02). 추적표를 계속 유지할지는 HIS가 올릴 판단이다.
- RUN(추정): `scripts/do_math/session_slots.py:326`의 공급자 상태 `"source": "git_runtime"` 필드를 읽는 곳이 `cli.py:516`, `scheduled_operator.py:322, 423`에서 보이지 않는다. 읽는 곳들은 `providers`만 쓴다. 이 필드를 단언하는 곳은 `scripts/tests/test_redesign_ACTIVITIES.py:243` 하나다. 문서와 JSON 소비자까지 검색하면 확정된다.
- ENG·STO·REV(캐시 점검 재료): 시험이 제품의 프로세스 전역 메모를 직접 비우거나 우회하는 곳이다.
  - `scripts/tests/test_performance_repairs.py:246, 251, 263`: `engine._HASHED_INSTALLATION`, `engine._CONTROL_READERS` 패치
  - `scripts/tests/test_preparation_cache.py:23, 43`: `submission._support_archive.cache_clear()`
  - `scripts/tests/test_file_io.py:97`: `repository.VERIFIED_ARTIFACTS.pop`
  - 메모 키가 `str(git_dir)`이라 가짜 저장소마다 고유 문자열을 만들어야 하는 곳: `scripts/tests/test_performance_repairs.py:197, 216`, `scripts/tests/test_redesign_SURFACE.py:553`
- 측정 단서(HOST·TSB): full1에서 foundation의 격리 묶음 `PortableFormalBoundaryTests`는 worker 82.0초 가운데 시험 행이 15.9초였다(`C:/math-worktrees/tools/full1/foundation-isolated-000/result.json`). setUpClass의 실제 Lean 기준 컴파일이 차가운 파일 캐시에서 돈 결과로 보이지만, 실행 없이 확정하지 못했다.

## 6. 작업 기록

- 위임하지 않고 76개 모듈을 직접 전문으로 읽었다. 모듈 사이의 중복과 픽스처 결합을 판정하려면 모든 모듈을 한 맥락에서 봐야 했기 때문이다.
- 추적표 인용 규모를 처음에는 1,357건으로 셌다. 이 수는 보관 실행의 시험 결과 표까지 포함한 것이어서, 현재 증거 좌표만 다시 세어 143개(foundation 115개)로 바로잡았다. 관찰에 묶인 좌표 82개는 `check_coverage.validate_observations`의 규칙(141-148행)을 읽고 따로 셌다.
- `git init` 시간을 쟀을 때 기계에 다른 파이썬 프로세스 6개가 돌고 있었다. 그래서 값이 0.27~0.40초로 흔들렸고, 절감량을 범위로 적었다.
- 조각 시간은 main 판본의 새 측정이 없어서, 3라운드 통합 확인 full1 보고(`C:/math-worktrees/tools/full1/report.json`, foundation 258.6초)를 썼다. 이 보고는 최종 판본 직전의 것이다.
- 중복 판정은 원문 대조로만 했고 시험을 실행하지 않았다. 일반형 `assertRaises(ValueError)`가 다른 이유로 통과하는 음성 시험(B1이 찾은 유형)은 이 조각에서도 있을 수 있지만, 실행 없이는 전수 확인하지 못했다.
