# TSB 검토: 시험 나머지·기반

기준 시점은 main `9b434f4`의 작업 트리다. 경로는 따로 적지 않으면 `C:/math/.claude/skills/do-math/` 기준의 상대 경로다. 시험은 실행하지 않았다. 시간 수치는 저장소 밖 로컬 자료 `C:/math-worktrees/tools/full1/report.json`에서 가져왔다. 이 보고서는 9b434f4 통합 과정에서 한 프로세스로 조각을 순차 실행한 결과이며, 추적(`operation_trace`) 변경보다 앞선 측정이다. 그래서 절대값이 아니라 상대 크기로만 쓴다.

## 1. 읽은 범위

**전문을 읽은 영역 파일**

- 조각별 시험 모듈 59개. 괄호 안은 행 수다.
  - host(18): test_background_processes(151), test_diagnosed_installation_recovery(144), test_external(111), test_formal(249), test_formal_runtime(138), test_host_resources(492), test_launch_recovery(78), test_lean_preview(73), test_machine_parallel(614), test_operator(308), test_operator_bootstrap(84), test_preflight(106), test_probe_cli(26), test_provider_wait(262), test_schedule_lifetime(56), test_schedule_pythonw(61), test_windows_job(281), test_worker_temporary_outputs(59)
  - lifecycle(23): test_checkpoint_persistence(146), test_cli(543), test_cli_advanced(151), test_connection_repairs(522), test_control_shapes(188), test_controls(125), test_document_followup(96), test_efficiency(351), test_engine(361), test_governance_engine(597), test_initial_intent_connection(190), test_initialization_efficiency(264), test_initialization_probe_batch(120), test_initialization_review_repairs(135), test_input_recovery(282), test_lifecycle_engine(1194), test_observation_admission(127), test_provider_recovery(101), test_redesign_ENGINE(1730), test_research_reliability(573), test_six_connections(500), test_static_review_repairs(759), test_stop_flags(365)
  - research(5): test_currentness_recovery(275), test_purpose_engine(800), test_research_recovery(523), test_run_feedback(145), test_session_scheduler(594)
  - review(8): test_native_final_submission(269), test_question_flow(60), test_review_engine(1063), test_review_research(535), test_submission_boundaries(481), test_submission_flow(458), test_submission_tools(693), test_walkthrough_followup(470)
  - academic(5): test_academic_engine(483), test_academic_preparation(176), test_approved_five_repairs(359), test_lifecycle_currentness(71), test_model_assessment_flow(498)
- 기반 파일: `scripts/tests/research_fixtures.py`(891), `scripts/tests/state_fixtures.py`(121), `scripts/tests/시험-지침.md`(70), `scripts/run_tests.py`(350), `scripts/test_categories.py`(92). `scripts/tests/fixtures/`는 빈 디렉터리다. 파일이 없고 Git도 추적하지 않는다.

**전문을 읽은 공통·과거 자료**

- 공통 자료: `C:/math/임시/do-math-정리-검토-2026-09-27/기준.md`, `AGENTS.md`, `C:/math/docs/do-math/검사-경량화-이음새-계약.md`
- 2라운드 조사: `C:/math/임시/경량화-조사-2026-09-26/TST.md`(577), `결과-K시험.md`(204)
- 시험 경량화: `C:/math/임시/시험-경량화-2026-09-26/계약.md`(62), `분석-G1.md`(592), `분석-G2.md`(534), `분석-G3.md`(647)
- 작업자 노드: `작업자-노드/B1-M-0350.md`, `B2-M-0350.md`, `B3-M-0350.md`, `W-fix-M-0351.md`
- 기억 노드: `C:/math/기억/layer1/M-0350.md`(101)

**이음새를 따라 일부만 읽은 파일**

- `scripts/do_math/repository.py`: 36-200(프로세스 캐시), 206-215(`new_id`), 255-360(`_read_key`, `_read_documents`, `_remember_published`), 488-513(`_validate_artifact_evidence`)
- `scripts/do_math/engine.py`: 70-85(`_CONTROL_READERS`), 885-893(`_controls`), 3186(`input_bundle = new_id("BA")`)
- `scripts/do_math/scheduler.py`: 445-457(`_plan_settle_waits`), 518-536(`_run_parallel` 선두)
- `scripts/do_math/planning.py`: 30-33, 530-550(`_VALID_ARTIFACTS`)
- `scripts/do_math/submission.py`: 105-132(`_ISSUED_INPUTS`, `issued_input`)
- `scripts/do_math/session_slots.py`: 184, 221(`acquire`, `started`의 정의 위치)
- `scripts/do_math/review_engine.py`: 450-458
- `scripts/do_math/record_schemas/__init__.py`: 150-240(`config_schema` 부근)

읽지 못한 파견 지정 파일은 없다. 4.1·4.2절 종류 가운데 검토하지 못한 종류도 없다.

## 2. 영역 판정

이 영역은 세 경량화의 방향을 절반쯤 따른다. 새 시험의 시작 상태는 `restore_template` 하나로 모였고, `research_fixtures`의 공유 도우미가 `git_init`, `run_cli`, `send_control` 같은 규칙을 한 곳에 두었다. 그러나 픽스처 층은 여전히 다른 시험 모듈 45개에 흩어져 있다. 영역 모듈 59개 가운데 44개가 다른 시험 모듈에서 도우미를 빌려 오며, 템플릿 빌드 19개 가운데 17개가 시험 모듈 안에 있다. 모듈은 성질이나 소유 모듈이 아니라 수리 회차·점검 계기별로 나뉘어 있어서, 시험 지침 4.1의 중복 검색이 실제로 작동하지 않았다. 그 결과 같은 성질을 단언하는 시험 쌍이 여럿 남았다(TSB-01·02·04·16). 시간 목표에 대해 말하면, 시험 쪽 수단(중복 제거, 공개 경로 축약, 템플릿 비용 절감)을 모두 써도 줄일 수 있는 양은 full1 합계 약 2440초 가운데 대략 150~250초로 추정된다. 조각당 120초·합계 300초에 닿으려면 M-0350이 남긴 제품 비용, 곧 상태 게시 한 번마다 드는 `update-ref`·fsync를 다뤄야 한다. 가장 큰 구조적 개선 여지는 둘이다. 하나는 픽스처를 픽스처 모듈로 모으고 모듈을 성질별로 재편하는 것이다(TSB-01·02). 다른 하나는 시험 기반이 제품의 사적 캐시 네 개를 이름으로 알고 비우는 결합을 끊는 것이다(TSB-14).

검토했고 없음: 파생상태, 결함, 임시방편

## 3. 후보

#### TSB-01 픽스처 층이 시험 모듈 45개에 흩어져 있다
- 검토: 1
- 종류: 경계
- 좌표: `scripts/tests/state_fixtures.py:30`; `scripts/tests/test_lifecycle_engine.py:174`; `scripts/tests/test_academic_engine.py:98,119`; `scripts/tests/test_purpose_engine.py:404-512`; `scripts/tests/test_input_recovery.py:25-31,89-97`; `scripts/tests/research_fixtures.py:20-37`; `scripts/tests/시험-지침.md:60-62`
- 현상:
  - 픽스처 모듈 `state_fixtures.active_engine`이 시험 모듈 `test_lifecycle_engine`의 `FakeEngine`을 import한다(`state_fixtures.py:30`). 기반이 시험 모듈에 의존하는 방향 역전이다.
  - 템플릿 빌드 함수(`def \w+(root, shared` 형태) 19개 가운데 17개가 시험 모듈 안에 있다. 예로 `test_academic_engine.solved_instance`·`requirement_change_instance`, `test_lifecycle_engine.initialized_instance`, `test_review_research.purpose_state`, `test_session_scheduler.ready_work`가 있다.
  - 하네스(`PurposeHarness`, `ActivatedPurposeHarness`, `PurposeRunner`)와 러너·응답 도우미(`common`, `candidate`, `formal_ok`, `ScriptedRunner`, `context_from`)가 `test_purpose_engine`, `test_engine`, `test_lifecycle_engine` 같은 시험 모듈에 정의되어 있고, 다른 모듈이 그것을 import한다.
  - `FakeEngine`의 메서드를 묶이지 않은 함수처럼 도우미 이름공간으로 부르는 곳이 있다(`test_connection_repairs`의 `FakeEngine.approve(SimpleNamespace(...))`, `FakeEngine.verification(engine, ...)`).
  - `research_fixtures` docstring(20-37)과 `시험-지침.md` 4.3의 2~3단(60-62)은 준비된 빌드를 둘만 안내한다. 나머지 17개는 목록 어디에도 없다.
- 근거:
  - `ast`로 `tests/*.py`의 `from test_X import`·`import test_X`를 전수 집계했다. 명령과 결과는 6절에 있다. 영역 모듈 59개 가운데 44개가 다른 시험 모듈을 import한다. 도우미를 내주는 시험 모듈은 저장소 전체에 45개다. 가장 많이 빌려 주는 모듈과 그 사용 모듈 수는 test_engine 20, test_lifecycle_engine 15, test_purpose_engine 14, test_redesign_TASKS 14, test_redesign_SURFACE 11, test_redesign_GOVERNANCE 9, test_input_recovery 8이다.
  - `git grep -nE "^def \w+\(root, shared" -- tests`의 결과는 19건이다. 전부 템플릿 빌드이며, `research_fixtures`와 `state_fixtures`에 1건씩, 시험 모듈에 17건이 있다.
  - M-0350은 3라운드 통합 결함 하나를 기록한다. `test_academic_preparation`이 다른 작업자의 시험 모듈에서 빌려 온 도우미가 병합 뒤에 없었다. 병렬 작업자가 서로의 시험 모듈을 픽스처로 쓰는 구조가 충돌 면을 넓힌 사례다.
  - 2라운드 TST-06은 같은 문제를 제기했다. 통합자는 "제품 이음새가 아니고 79곳"이라는 판단으로 기각했다(`docs/do-math/경량화-설계-2026-09-26.md` 5절). 사용자 결정은 아니다.
- 제안: 전면 이동이 아니라 빌려 주는 쪽 상위 도우미만 옮긴다. `FakeEngine`과 그 `activate`, `initialized_instance`, `solved_instance`·`requirement_change_instance`·`drive_to`, `PurposeRunner`와 두 하네스, `common`·`candidate`·`formal_ok`·`ScriptedRunner`·`context_from`을 `research_fixtures`나 `state_fixtures`(또는 `engine_fixtures` 하나)로 옮긴다. 시험 모듈은 픽스처 모듈만 import하게 한다. 그리고 `research_fixtures` docstring을 빌드 19개의 목록(이름, 인자, 만드는 상태)으로 고치고, `시험-지침.md` 4.3은 그 목록을 가리키게 한다.
- 실익:
  - 시험 모듈 사이의 import 간선이 대부분 사라진다. 빌려 주는 모듈이 45개에서 한 자릿수로 준다.
  - 시험 하나를 지우거나 옮길 때 다른 모듈이 깨지는 결합이 사라진다. M-0350의 병합 결함과 같은 유형이 재발할 여지가 준다.
  - 새 시험 작성자가 빌드 목록 한 곳에서 기존 시작 상태를 찾을 수 있다. 지침 4.1과 4.3이 실제로 작동하게 된다.
  - 기반→시험 모듈 방향의 역전(`state_fixtures`→`test_lifecycle_engine`)이 없어진다.
- 비용과 위험: 수정 파일이 수십 개다(주로 import 줄). 옮기는 과정에서 모듈 수준 부작용(`sys.path` 조작, `install_adapter_fixture` 패치)의 순서가 바뀔 위험이 있다. 새 상태·수명·복구 규칙은 없다.
- 기능·커버리지 영향: 없음. 정의 위치만 바뀐다.
- 사용자 결정 관련: 없음. TST-06의 기각은 통합자 판단이었다. 이후 새로 드러난 사실은 둘이다. M-0350의 병합 결함, 그리고 템플릿 빌드 17개가 시험 모듈에 새로 쌓였다는 점이다.
- 확신도: 현상은 확인이다. 실익 가운데 "병합 결함 감소"는 추정이다. 옮긴 뒤 빌려 주는 모듈 수를 같은 `ast` 집계로 다시 세면 확정된다.

#### TSB-02 모듈과 시험 이름이 성질이 아니라 계기(수리 회차·점검)로 나뉘어 있다
- 검토: 1
- 종류: 경계
- 좌표:
  - 계기 이름의 모듈: `scripts/tests/test_approved_five_repairs.py`, `test_walkthrough_followup.py`, `test_run_feedback.py`, `test_research_reliability.py`, `test_initialization_review_repairs.py`, `test_connection_repairs.py`, `test_six_connections.py`, `test_static_review_repairs.py`, `test_redesign_ENGINE.py`, `test_efficiency.py`, `test_initialization_efficiency.py`, `test_document_followup.py`, `test_currentness_recovery.py`, `test_lifecycle_currentness.py:1`
  - 계기 이름의 클래스·메서드: `test_lifecycle_engine.py:741`(`Audit2LifecycleTests`), `:951`(`AuditRepairTests`), `:982-1111`(`test_11_*`·`test_12_*`·`test_13_*`), `test_cli.py`의 `def test_audit*` 9건
- 현상:
  - 영역 모듈의 약 4분의 1(14개)이 "승인된 다섯 수리", "2026-09-23 정적 점검 후속", "2026-09-19 주차 실행 피드백", "과거 실패 형태"처럼 시험이 생긴 계기로 이름 붙어 있다.
  - 같은 제품 성질의 시험이 계기 모듈 여러 곳에 흩어져, 중복이 모듈 경계 뒤에 숨는다. TSB-04·16의 중복 쌍이 모두 서로 다른 계기 모듈 사이에 있다: `test_efficiency`↔`test_run_feedback`, `test_purpose_engine`↔`test_run_feedback`, `test_purpose_engine`↔`test_repository`, `test_purpose_engine`↔`test_review_research`.
  - `test_lifecycle_currentness.py:1`의 docstring "Reject unsupported editions unchanged"는 구판 거부 시험이 옮겨 간 뒤 내용과 맞지 않는다.
- 근거:
  - `시험-지침.md` 4.1은 "같은 성질을 검사하는 시험이 이미 있는지 먼저 찾는다"를 요구한다. 그러나 모듈 이름이 성질을 말하지 않으므로 이름으로는 찾을 수 없다. 4.2는 시험 이름이 성질을 문장으로 말하라고 하지만, `test_11_*`, `test_audit*`, `Audit2*`는 점검 회차 번호다.
  - `grep -c "def test_audit" tests/test_cli.py`의 결과는 9다.
  - 기준 4.2절 `낡음`은 "역사적 경위를 따라 붙은 이름과 분류"를 명시한다.
- 제안: 한 번에 재편하지 않는다. TSB-01에서 픽스처를 옮긴 뒤, 계기 모듈의 시험을 그 시험이 단언하는 제품 모듈(소유 영역) 이름의 모듈로 옮기며 합친다. 예를 들면 `test_efficiency`·`test_run_feedback`의 settle·예산 시험은 `test_session_scheduler`로, 회차 번호 이름은 성질 문장으로 바꾼다. 옮기는 도중 같은 성질의 쌍이 드러나면 지침 4.1에 따라 합친다.
- 실익:
  - 계기 모듈 약 14개가 소유 모듈 단위로 흡수된다.
  - 성질별 중복이 한 모듈 안에서 보이게 되어, 이후 중복 누적을 막는다.
  - 인계 확인(`시험-지침.md` 2절)의 `grep -lw` 대상이 소유 모듈로 좁혀진다.
- 비용과 위험:
  - 파일 이동이 크고, `SHARDS` 재배치와 조각 시간 변화가 따른다.
  - 동시 진행 중인 다른 작업과 충돌이 크므로 단독 작업으로 해야 한다.
  - 새 상태·수명 규칙은 없다.
- 기능·커버리지 영향: 이동만 하면 없다. 드러난 쌍을 합칠 때만 있다(각 쌍은 TSB-04·16).
- 사용자 결정 관련: 없음
- 확신도: 확인. 목록과 중복 쌍은 원문으로 확인했다. 흡수할 모듈 수는 배치안을 짜야 확정된다.

#### TSB-03 `GitPurposeTests`가 `solved_instance` 템플릿 빌드와 같은 공개 경로를 한 번 더 돈다
- 검토: 1
- 종류: 비용
- 좌표: `scripts/tests/test_purpose_engine.py:764-786`; `scripts/tests/test_academic_engine.py:98-116`; `scripts/tests/test_redesign_ENGINE.py`(`PublicGitFlow`)
- 현상:
  - `GitPurposeTests`는 docstring대로 "PurposeHarness.make followed by drive"다. 새 저장소에서 공개 초기화와 활성화를 하고, 끝까지 몬다.
  - `test_academic_engine.solved_instance(criteria=None)`도 같은 경로(공개 초기화 → 활성화 → 끝까지 구동)를 템플릿 빌드로 한 번 돈다.
  - 공개 활성화와 작업을 한 엔진에서 잇는 흐름은 `test_redesign_ENGINE.PublicGitFlow`도 덮는다.
- 근거:
  - full1에서 `GitPurposeTests`는 45.7초였다.
  - 같은 프로세스에서 `solved_instance(None)` 템플릿이 academic 조각에서 만들어진다. 따라서 `GitPurposeTests`의 단언(최종 상태의 해결 판정·기록)은 그 템플릿 복원본에서 할 수 있다.
  - 지침 4.3의 4단 판별 질문("활성화 과정에 결함이 있지만 끝난 상태가 정상과 같다면 실패해야 하는가")에 대해, 이 시험의 단언은 최종 상태만 본다.
- 제안: `GitPurposeTests`의 단언을 `restore_template(solved_instance, criteria=None)` 복원본에 대한 시험으로 옮기고 클래스를 지운다. 이 시험의 보고 훅(781-786)은 TSB-09에 따라 함께 지운다.
- 실익: research 조각에서 약 40초 이상 줄어든다(추정). 초기화부터 목표 도달까지의 공개 e2e는 `solved_instance` 빌드와 `PublicGitFlow`에 남는다.
- 비용과 위험: `solved_instance`가 academic 쪽 모듈에 있으므로, TSB-01에 따라 픽스처 모듈로 옮겨야 research 조각이 academic 모듈에 의존하지 않는다. 조각 단독 실행 시 research 조각에 그 빌드 비용이 한 번 생긴다. 새 상태·수명 규칙은 없다.
- 기능·커버리지 영향: 있음, 작다. 공개 경로를 한 번 덜 돈다. 같은 경로는 빌드와 `PublicGitFlow`가 돈다.
- 사용자 결정 관련: 없음. "커버리지는 크게 바꾸지 않는다"와 맞는다.
- 확신도: 추정. 두 경로의 입력(목표, 설정, 러너 시나리오)이 같은지 한 줄씩 대조하고, 옮긴 뒤 research 조각을 단독으로 재면 확정된다.

#### TSB-04 서로 다른 계기 모듈에 같은 성질을 단언하는 시험 세 쌍이 있다
- 검토: 1
- 종류: 비용
- 좌표:
  - (a) `scripts/tests/test_purpose_engine.py:633-647` ↔ `scripts/tests/test_run_feedback.py:109-141`
  - (b) `scripts/tests/test_purpose_engine.py:727-734` ↔ `scripts/tests/test_repository.py:109-131`
  - (c) `scripts/tests/test_efficiency.py:129-155` ↔ `scripts/tests/test_run_feedback.py:80-106`; 판정 규칙 `scripts/do_math/scheduler.py:445-457`
- 현상:
  - (a) `test_work_budget_execution_is_not_bounded_by_operations_call_timeout`(11.9초)와 `RunWithoutDeadlineTests.test_elapsed_legacy_run_limit_does_not_block_the_next_execution`(5.5초)는 둘 다 "작업 실행은 실행 시간 한도에 막히지 않는다"를 단언한다.
  - (b) `test_repository_enforces_snapshot_cas_and_artifact_immutability`(4.6초)는 `test_repository`의 `test_stale_save_conflict_does_not_overwrite`(109)와 `test_new_artifact_bundle_is_saved_with_state_and_existing_bundle_is_immutable`(116)가 foundation에서 이미 단언하는 CAS·번들 불변을, 엔진을 통해 다시 확인한다.
  - (c) `test_plan_settle_waits_only_up_to_limit`(6.1초)는 준비된 과제를 구동한 뒤 settle 한도를 단언한다. `PlanSettleTests.test_the_settle_wait_ends_at_its_configured_limit`(97)도 같은 한도를 단언한다.
- 근거:
  - (c)의 판정 함수 `scheduler._plan_settle_waits`(445-457)는 `requested_by`/`recovery`, 대기 중인 검토, `settle_started_at`만 읽는다. 준비된 과제 구동은 결과에 들어가지 않는다.
  - 시간은 full1 측정값이다.
- 제안: 각 쌍에서 싼 쪽을 남긴다. (a)는 `test_run_feedback` 쪽, (b)는 `test_repository` 쪽, (c)는 `PlanSettleTests` 쪽이다. 비싼 쪽이 추가로 단언하는 값이 있으면 남는 쪽에 한 줄로 옮긴다.
- 실익: 약 22초가 줄고 시험 3개가 사라진다. 지워지는 코드는 약 50행이다.
- 비용과 위험: 파일 3개가 바뀐다. 새 규칙은 없다.
- 기능·커버리지 영향: 없음. 같은 성질이 남는 쪽에서 단언된다.
- 사용자 결정 관련: 없음
- 확신도: 확인. (a)·(b)·(c)의 단언 대상은 원문 대조로 확인했다. 절감 시간은 full1 수치 기준의 추정이다.

#### TSB-05 템플릿 빌드와 복원 비용이 따로 재어지지 않았고, 줄일 수단 둘이 남아 있다
- 검토: 1
- 종류: 비용
- 좌표: `scripts/tests/research_fixtures.py:798-859`(`_Template`, `restore_template`); `research_fixtures.py:706`(`activated_instance`)
- 현상:
  - `restore`는 매 호출마다 `remove_tree` 뒤에 pristine 전체를 `copytree`하고, Git 느슨한 객체를 파일 하나씩 복사한다(`research_fixtures.py:811-817`).
  - 활성화 뒤 상태를 만드는 파생 빌드(`solved_instance`, `purpose_state`, `ready_work`, `plan_ready_instance` 등)는 각자 공개 활성화를 처음부터 다시 돈다.
- 근거:
  - W-fix 작업자 노드의 부하 중 측정값은 공개 템플릿 빌드 44.8초, 복원 1.3~1.5초, 복원 뒤 적재 0.9초다.
  - `activated_instance`를 거치는 빌드는 17개 가운데 여러 개다. 복원 횟수는 템플릿을 쓰는 시험 수만큼이다.
  - 단독 측정값은 없다.
- 제안: 먼저 잰다. 조각 하나를 단독 실행하면서 빌드별 빌드 시간과 복원 횟수·시간을 `report.json`에 남기거나 한 번 로그로 잰다. 그 결과 복원 합계가 크면 (1)을, 파생 빌드 합계가 크면 (2)를 검토한다.
  - (1) pristine의 `.git/objects`를 복사 대신 하드 링크한다. 느슨한 객체는 읽기 전용(0444)이며 Git은 객체를 제자리에서 고치지 않는다.
  - (2) 파생 빌드가 조상 템플릿의 복원본에서 출발하게 한다. 같은 루트이므로 경로 불변 규칙은 유지된다.
- 실익: 추정만 가능하다. (2)는 공개 활성화 한 번(부하 중 약 9초 이상)을 파생 빌드마다 아낀다. (1)은 복원 1회당 복사 시간의 대부분을 아낀다.
- 비용과 위험:
  - (1)은 "pristine과 live가 객체 파일을 공유한다"는 새 규칙을 만든다. `remove_tree`의 `writable` 콜백이 하드 링크의 권한을 바꾸면 pristine 쪽도 바뀐다.
  - (2)는 템플릿 사이의 부모 관계라는 새 수명 규칙을 만든다. 부모 빌드가 실패하면 자식도 실패한다.
  - 기준 2절 8항에 따라 둘 다 비용으로 센다. 측정 없이 채택하면 과설계다.
- 기능·커버리지 영향: 없음
- 사용자 결정 관련: 없음
- 확신도: 추정. 조각 단독 실행에서 빌드·복원 시간을 재면 채택 여부가 확정된다.

#### TSB-06 시작 상태 하네스 셋과 `git init` 자식 프로세스가 지침 4.3·4.6과 다르게 남아 있다
- 검토: 1
- 종류: 불일관
- 좌표: `scripts/tests/test_purpose_engine.py:404-414`(`PurposeHarness.setUp`), `:462-474`(`ActiveStateHarness`), `:477-512`(`ActivatedPurposeHarness`); `scripts/tests/research_fixtures.py:198-209`(`new_instance`), `:726-741`(`git_init`); `scripts/tests/test_document_followup.py:11,14`; `scripts/tests/test_reading_map.py:11,60`
- 현상:
  - `ActiveStateHarness.make`는 시험마다 `state_fixtures.active_engine`으로 합성 활성 상태를 새로 만든다. 같은 상태를 `ActivatedPurposeHarness.make_active`가 템플릿 복원으로 준다. `ActiveStateHarness`의 사용처는 `test_document_followup`과 `test_reading_map`(TSA 영역) 두 모듈뿐이다.
  - `research_fixtures.new_instance`(207)와 `PurposeHarness.setUp`(412)은 지침 4.6("`git init` 자식 프로세스 대신 `git_init(path)`")과 달리 `subprocess.run(['git', ... 'init', '-q'])`을 쓴다. `git_init`은 같은 파일 726행에 있다.
  - 영역 안에서 같은 형태의 호출이 더 있다: `test_initial_intent_connection.py:115`, `test_initialization_efficiency.py:164,191`, `test_preflight.py:20`, `test_provider_wait.py:111`, `test_host_resources.py:141,236`.
- 근거:
  - `git grep -nE "['\"]init['\"]" -- tests` 결과에서 CLI `init`과 스트림 `init` 문자열을 뺀 `git init` 자식 프로세스는 저장소 전체 24건이다. 그중 영역 안은 13건이다.
  - 그 13건 가운데 `test_background_processes.py:27,120`과 `test_formal.py:85,212,225`는 자식 프로세스나 Git 작업 트리 자체가 검사 대상이므로 유지한다(4절). 나머지 8건은 저장소 생성만 한다.
  - `new_instance(` 호출은 10건이다.
- 제안:
  - `ActiveStateHarness`를 지우고, 두 사용 모듈은 `ActivatedPurposeHarness.make_active`를 쓴다. `ActivatedPurposeHarness` docstring의 `ActiveStateHarness.make` 언급도 고친다.
  - `new_instance`, `PurposeHarness.setUp`과 저장소 생성만 하는 8건은 `git_init`으로 바꾼다.
- 실익:
  - 하네스가 둘로 준다.
  - 두 모듈의 시험마다 들던 합성 상태 새 빌드가 약 1초 복원으로 바뀐다.
  - 새 저장소마다 드는 `git init` 프로세스 1개가 사라진다. Windows 프로세스 생성은 호출당 수십 ms다.
  - 지침과 기반의 불일관이 없어진다.
- 비용과 위험: 파일 약 8개가 바뀐다. `make_active`는 복원 루트를 교체하므로, 한 시험에서 인스턴스 둘을 동시에 쓰는 곳이 없는지 확인해야 한다.
- 기능·커버리지 영향: 없음
- 사용자 결정 관련: 없음
- 확신도: 확인. 두 사용 모듈의 시험은 모두 `self.make`를 한 번만 부른다(`test_document_followup.py:17,30,71`, `test_reading_map.py:62,74`). 따라서 인스턴스를 하나만 쓴다. `test_document_followup.py:17`처럼 설정을 바꾸는 호출은 `make_active`에서 템플릿 키 하나를 새로 만든다. 그 빌드 비용은 지금의 새 빌드와 같다.

#### TSB-07 `owner_calls`가 소유자 한 바퀴의 순서를 제품 밖에서 따로 구현한다
- 검토: 1
- 종류: 이음새
- 좌표: `scripts/tests/state_fixtures.py:61-84`; `scripts/do_math/engine.py:885-889`(`_controls`); `scripts/do_math/scheduler.py:521-535`(`_run_parallel`)
- 현상: 픽스처는 `calls.wait` → `calls.pump()` → `engine._transport.pump(engine._publish_control_request)` → `calls.collect()`를 직접 반복한다. 제품의 같은 순서는 `_controls(pump=True)`(885-889)와 `_run_parallel`의 한 바퀴(`_settle_stops` → `_controls` → `_settle_stops` → `collect`)에 있다.
- 근거:
  - 주석 "The owner loop pumps the transport every pass (engine._controls)"(state_fixtures.py:79)가 사본임을 스스로 말한다.
  - M-0350은 이 순서가 어긋나 제출 영수증을 60초 기다린 사례를 기록한다. 픽스처가 transport pump를 빠뜨렸던 사례다.
  - 제품 쪽에 이 순서를 공개하는 함수는 없다(`_controls`는 제어 적용까지 하므로 그대로 부를 수 없다).
- 제안: 제품의 한 바퀴 가운데 "pump와 transport 수신"을 `engine._pump_owner()` 같은 메서드 하나로 뽑는다. `_controls`와 픽스처가 모두 그것을 부르게 한다. 제품 쪽 변경은 ENG 영역과 합의해야 한다.
- 실익: 픽스처 약 6행이 줄고, 소유자 순서의 사본이 없어진다. 제품 순서가 바뀌어도 픽스처가 따라간다. 60초 대기 같은 잠복 불일치의 여지가 사라진다.
- 비용과 위험: `engine.py`에 메서드 하나가 생긴다. 시험을 위한 제품 표면이 아니라, 제품이 두 곳(`_controls`, `_run_parallel`의 전후)에서 쓰는 순서를 이름 붙이는 것이어야 정당하다. 제품 내 재사용이 없으면 채택하지 않는다.
- 기능·커버리지 영향: 없음
- 사용자 결정 관련: 없음
- 확신도: 추정. `_controls`의 pump 부분을 제품 안에서 따로 부를 곳이 있는지를 ENG가 확인하면 확정된다.

#### TSB-08 `in_process` 표지가 한 클래스를 위해 존재한다
- 검토: 1
- 종류: 비대
- 좌표: `scripts/test_categories.py:12-13,65,84-88`; `scripts/tests/test_machine_parallel.py:320-585`
- 현상:
  - `CallManagerTests`는 클래스에 `@test_group('resource')`를 붙이고, 메서드 12개 가운데 8개에 `@test_group('in_process')`를 붙여 격리를 되돌린다(322, 362, 407, 425, 446, 475, 502, 539).
  - `LABELS`의 셋째 값과 `isolation_for`의 되돌림 분기는 이 용도만을 위해 존재한다.
- 근거:
  - `git grep -n "in_process" -- scripts`에서 `test_machine_parallel` 밖의 일치는 8건이다. 표지와 관련된 것은 `test_categories.py:12,65,88`의 정의와 `test_test_runner.py:43,47`의 표지 자기시험(TSA 영역)이다. `run_tests.py:311-313`은 같은 철자의 지역 변수, `test_git_store.py:97`은 시험 이름의 일부라 무관하다.
  - 격리가 필요한 것은 실제 Job·종료를 다루는 메서드들이다(`test_close_sets_every_stop_flag...`(383), `test_failed_start_publication_never_resumes_the_real_job`(572), `test_real_job_cancellation...`(585) 등).
- 제안: 클래스 표지를 지운다. 실제 자원을 쓰는 메서드에만 `@test_group('resource')`를 붙인다. 그리고 `in_process`를 `LABELS`와 `isolation_for`, docstring에서 지운다.
- 실익: 표지 종류가 셋에서 둘로 준다. "메서드 표지가 클래스 표지를 이긴다"는 되돌림 규칙과 그 자기시험이 사라진다. 약 15행이 줄어든다.
- 비용과 위험: 파일 3개(`test_categories.py`, `test_machine_parallel.py`, TSA의 `test_test_runner.py`)가 바뀐다. 메서드 표지 해석(`isolation_for`의 `method` 조회)은 남는다.
- 기능·커버리지 영향: 없음
- 사용자 결정 관련: 없음
- 확신도: 확인

#### TSB-09 생산자 없는 증거 보고 훅 세 개
- 검토: 1
- 종류: 미사용
- 좌표: `scripts/tests/test_purpose_engine.py:415-430`(tearDown 보고), `:781-786`, `:789-800`(`__main__`); `scripts/tests/test_input_recovery.py:185-208`; `scripts/tests/test_host_resources.py:26-31`
- 현상: 세 모듈이 환경변수 `DO_MATH_PURPOSE_TEST_REPORT`, `INPUT_RECOVERY_REPORT`, `DO_MATH_HOST_EVIDENCE_DIR`가 있을 때만 증거 파일을 쓴다.
- 근거: `git grep -n "DO_MATH_PURPOSE_TEST_REPORT\|INPUT_RECOVERY_REPORT\|DO_MATH_HOST_EVIDENCE_DIR"`는 10건을 반환한다. 이 영역의 5건(`test_purpose_engine.py:417,781,791`, `test_input_recovery.py:185`, `test_host_resources.py:27`)과 `C:/math/.agents/skills/do-math/` 아래 같은 파일의 5건이며, 모두 `os.environ.get`으로 읽는 쪽이다. 이 값을 설정하는 스크립트·문서·실행기는 없다. 세 훅은 `7d2597e` 시기에 들어왔다.
- 제안: 세 훅과 `test_purpose_engine`의 `__main__` 보고 블록을 지운다.
- 실익: 약 75행이 줄어든다. 기준 2절 5항의 "생산자 없는 신호"를 없앤다.
- 비용과 위험: 파일 3개가 바뀐다. 외부의 수동 사용이 있었다면 그 기능을 잃는데, 저장소 안에는 흔적이 없다.
- 기능·커버리지 영향: 없음. 단언은 바뀌지 않는다.
- 사용자 결정 관련: 없음
- 확신도: 확인

#### TSB-10 쓰이지 않는 import 30개와 잔여 도우미·출력
- 검토: 1
- 종류: 미사용
- 좌표:
  - `test_academic_engine.py:26`(policy_change), `:161`(`_set_requirements`의 `decision_id` 인자)
  - `test_academic_preparation.py:3,12`
  - `test_control_shapes.py:13`
  - `test_currentness_recovery.py:14,15`
  - `test_efficiency.py:12,14,15,16`
  - `test_engine.py:16,17`(schema_for, control, validate_config)
  - `test_lifecycle_currentness.py:9`
  - `test_model_assessment_flow.py:23,27`
  - `test_native_final_submission.py:9`
  - `test_operator.py:7`
  - `test_provider_recovery.py:10`
  - `test_purpose_engine.py:8,24`, `:38`(`TOOLCHAIN`)
  - `test_question_flow.py:9`
  - `test_run_feedback.py:14`
  - `test_session_scheduler.py:12,13,19,20`
  - `test_submission_boundaries.py:6,22`
  - `research_fixtures.py:127`(uuid)
  - `test_redesign_ENGINE.py:739-741`(디버그 `print`)
  - `test_external.py:46`(`time.sleep(.02)`)
- 현상:
  - 모듈 최상위 import 가운데 파일 안에서 쓰이지 않는 이름이 17개 파일에 30개 있다(`from __future__ import annotations` 제외).
  - `TOOLCHAIN`은 정의만 있고 쓰이지 않는다.
  - `PublicGitFlow`가 매 실행 표준 출력에 디버그 줄을 찍는다.
  - `test_external` setUp은 서버 스레드 시작 뒤 고정 대기를 둔다. `serve_forever` 이전에도 소켓은 이미 listen 상태이므로 대기가 필요 없다.
- 근거:
  - 명령과 결과는 6절에 있다. `ast`로 최상위 import 이름을 모으고, 파일 안의 `Name`·`Attribute` 사용과 문자열 등장을 대조했다. 43건 가운데 `annotations` 13건을 빼면 30건이다.
  - 재수출 여부는 `git grep -nE "from <모듈> import[^#]*\b<이름>\b|<모듈>\.<이름>\b"`로 21개 조합을 확인했다. 모두 0건이고, 여러 줄 import와 `import *`도 해당 없음을 확인했다.
  - `git grep -n TOOLCHAIN tests/test_purpose_engine.py`는 정의 1건뿐이다.
  - 이 import들은 세 경량화 이전부터 있었다(`capture_decision_basis`로 추적 확인).
- 제안: 지운다. `sleep`도 지운다. `HTTPServer` 생성 시점에 bind·listen이 끝난다.
- 실익: 약 45행이 줄고, 독자가 쓰이지 않는 의존을 추적하지 않게 된다.
- 비용과 위험: 파일 약 19개가 바뀐다. 위험은 없다.
- 기능·커버리지 영향: 없음
- 사용자 결정 관련: 없음
- 확신도: 확인. `sleep` 제거만 추정이다. `test_external`을 한 번 돌리면 확정된다.

#### TSB-11 `test_review_engine`의 `FakeEngine` 설정이 닫힌 설정 스키마 밖의 키를 쓰고, 제품이 그 키를 읽는다
- 검토: 1
- 종류: 기타. 기준 2절 4항 "시험을 살리려고 제품에 예외를 넣지 않는다"에 해당하며, 4.1·4.2의 어느 종류에도 딱 맞지 않는다.
- 좌표: `scripts/tests/test_review_engine.py:40-44,164,549-555`; `scripts/tests/test_review_research.py:375`; `scripts/do_math/review_engine.py:456`; `scripts/do_math/record_schemas/__init__.py`(`config_schema`)
- 현상:
  - `FakeEngine`의 설정에 `objection_round_limit`, `review_policy`, `review_scope_assessment`가 있고, 지식 항목에 `required_reviews`가 있다(40-44).
  - 저장 왕복 시험은 이 키들을 떼고서야 저장한다(549-555).
  - 제품 `review_engine.py:456`의 `config.get('review_scope_assessment')` 대체값은 이 시험 대역만 채운다.
- 근거:
  - `git grep -n "review_scope_assessment\|objection_round_limit" -- scripts/do_math`는 `review_engine.py:456` 1건이다. 설정 스키마와 `DEFAULT_CONFIG`에는 없다.
  - 시험 쪽 사용은 `test_review_engine`, `test_review_research:375`, `test_redesign_REVIEWS:185,198,395,474`(TSA)다.
- 제안: 대역 설정을 현행 계약대로 구성한다. 범위 판정은 `item['scope_assessment']`로, 정책은 인스턴스 `review_policy`로 준다. 제품의 대체값은 REV가 지운다.
- 실익: 제품의 시험 전용 분기 하나와, 시험이 계약 밖 키를 떼는 약 5행이 사라진다. 대역과 계약이 어긋나는 이음새가 없어진다.
- 비용과 위험: 시험 파일 3개(TSA 포함)와 제품 한 줄이 바뀐다.
- 기능·커버리지 영향: 없음. 제품의 실제 경로는 `item['scope_assessment']`다.
- 사용자 결정 관련: 없음
- 확신도: 추정. 제품 안에서 `config`에 `review_scope_assessment`를 넣는 경로가 없음을 REV가 확인하면 확정된다. 설정 스키마에는 없다.

#### TSB-12 옛 계약을 가리키는 시험 이름과 단언
- 검토: 1
- 종류: 낡음
- 좌표:
  - `scripts/tests/test_redesign_ENGINE.py:841`(`test_every_call_budget_control_produces_stable_queue_identity`), `:184`(`inspect.signature(...).parameters`에 `owns_response`가 있는지 단언)
  - `scripts/tests/test_run_feedback.py:110`(`..._legacy_run_limit...`)
  - `scripts/tests/test_submission_tools.py:343`(`test_legacy_live_review_...`)
  - `scripts/tests/test_lifecycle_engine.py:413`(`..._legacy_cycle_limit`)
  - `scripts/tests/test_governance_engine.py:52-62,318-319`(`GovernanceEngineMixin` 존재·상속 단언)
  - `scripts/tests/test_operator.py:64`(`parking-unimodality` 부재 단언)
- 현상:
  - 호출 예산은 `9e5e120`에서 없어졌는데, 이름이 여전히 "call budget"을 말한다.
  - `legacy` 이름의 시험 셋은 지금 현행 동작을 단언하지만, 이름이 없어진 옛 한도를 기준으로 삼는다.
  - 시그니처·상속 존재를 단언하는 시험은 행동이 아니라 구현 모양을 검사한다.
  - `parking-unimodality` 부재 단언은 지워진 인자 하나를 영구히 확인한다(L-0020도 이를 깨지기 쉬운 단언으로 적었다).
- 근거: 원문 확인. `git grep -n "call_budget" -- scripts/do_math`는 0건이다.
- 제안:
  - 이름은 현행 성질로 바꾼다. 예: `test_work_executions_have_no_elapsed_run_limit`.
  - 시그니처·상속 단언은 지운다. 행동 단언이 이미 같은 시험이나 이웃 시험에 있다(`test_redesign_ENGINE.py:191`의 `owns_response=False` 호출).
  - `parking-unimodality` 단언은 지운다.
- 실익: 약 15행이 줄고, 실패 메시지가 현행 계약을 말한다.
- 비용과 위험: 파일 6개가 바뀐다. 위험은 없다.
- 기능·커버리지 영향: 없음. 지우는 단언은 구현 모양과 지워진 인자에 대한 것이다.
- 사용자 결정 관련: 없음
- 확신도: 확인

#### TSB-13 `research_fixtures` docstring이 현재 동작과 다르다
- 검토: 1
- 종류: 문서
- 좌표: `scripts/tests/research_fixtures.py:22-23,56-58,783-795`
- 현상:
  - docstring은 "Two builds are ready"(22)라고 하지만 빌드는 19개다(TSB-01).
  - "The product's path-keyed caches are cleared for ``root`` on every restore"(56-58)라고 하지만, `forget_repository_caches`가 비우는 것은 네 개(`VERIFIED_ARTIFACTS`, `_VALIDATED_READS`, `planning._VALID_ARTIFACTS`, `submission._ISSUED_INPUTS`)뿐이다.
  - 경로를 키에 담는 다른 캐시 네 개(`repository._ARTIFACT_FACTS`, `_PUBLISHED_PARENTS`, `_RETAINED_READS`, `engine._CONTROL_READERS`)는 비우지 않는다.
- 근거:
  - `repository.py:111,133-134`와 `engine.py:74`의 정의를 확인했다.
  - `forget_repository_caches`의 대상 튜플(792-793)도 확인했다.
- 제안: TSB-14를 채택하면 캐시 문장은 지운다. 채택하지 않으면 "내용 주소가 아닌 캐시를 비운다"로 사실대로 고친다. 빌드 목록은 TSB-01에 따라 고친다.
- 실익: 시험 작성자가 복원 뒤 캐시 상태를 잘못 믿지 않게 된다.
- 비용과 위험: 파일 1개, 위험은 없다.
- 기능·커버리지 영향: 없음
- 사용자 결정 관련: 없음
- 확신도: 확인

#### TSB-14 시험 기반이 제품의 사적 캐시 네 개를 이름으로 알고 비운다. 그중 셋은 비울 필요가 없다
- 검토: 2
- 종류: 비대
- 좌표: `scripts/tests/research_fixtures.py:783-795,816`; `scripts/tests/test_purpose_engine.py:392-394`; `scripts/do_math/repository.py:39,97,258-259`; `scripts/do_math/planning.py:32,536-548`; `scripts/do_math/submission.py:108,121-130`; `scripts/do_math/engine.py:3186`; `scripts/tests/test_submission_flow.py:341-355`
- 현상:
  - 9b434f4가 더한 `forget_repository_caches`는 복원마다 제품 모듈 세 개의 사적 이름 네 개를 import해서 root 아래 키를 지운다.
  - `test_purpose_engine`의 템플릿 자기시험은 `repository._VALIDATED_READS`가 비었는지 단언한다(394).
- 근거:
  - 네 캐시의 키를 원문에서 확인했다.
    - `VERIFIED_ARTIFACTS`와 `_VALID_ARTIFACTS`의 키는 `(git_dir, path, sha256)`이다(`artifact_key`, planning.py:537-538). 따라서 복원본의 같은 경로에 같은 해시의 바이트가 있으면 결과가 같다.
    - `_VALIDATED_READS`의 키는 `(git_dir, head OID, 계약 키)`다(repository.py:258-259). 커밋 OID가 트리 전체를 담고 계약도 키에 있다. 같은 키의 결과는 같은 내용에 대한 같은 검증이다.
    - 세 캐시는 모두 내용 주소이므로, 이전 복원본의 항목이 남아도 새 복원본에서 틀린 답을 내지 않는다.
  - 남는 하나인 `_ISSUED_INPUTS`의 키는 `(git_dir, 번들 안 경로)`이며 해시가 없다(submission.py:121). 제품은 번들 이름을 `new_id("BA")`(시각+난수 ULID, engine.py:3186)로 만든다. 그래서 제품에서는 같은 경로가 다른 내용을 가리키지 않는다.
  - 다른 내용이 같은 경로를 쓰는 경우는 시험이 고정 번들 이름 `BA-history-input`을 템플릿 복원본(`InputRecoveryPublicTests.setUp`)에 쓰는 `test_submission_flow.py:341-355`뿐이다.
  - `git grep -n "forget_repository_caches\|_VALIDATED_READS\|_ISSUED_INPUTS\|_VALID_ARTIFACTS\|VERIFIED_ARTIFACTS\|_CONTROL_READERS\|_ARTIFACT_FACTS" -- tests`는 10건을 반환한다. 이 후보와 관련된 것은 `research_fixtures.py:783,792,793,816`, `test_purpose_engine.py:394`의 5건이다. 나머지 5건은 특정 캐시를 의도적으로 비우는 단위 시험(4절 보존)이다.
- 제안:
  - `test_submission_flow`의 고정 번들 이름을 `new_id('BA')`로 바꾼다.
  - `forget_repository_caches`와 그 호출, `test_purpose_engine.py:392-394`의 사적 캐시 단언, docstring의 캐시 문장(TSB-13)을 지운다.
- 실익:
  - 시험 기반에서 제품 사적 이름 네 개에 대한 결합이 사라진다. 제품이 캐시를 바꾸거나 더할 때 기반을 함께 고칠 필요가 없어진다(기준 2절 11항의 신호가 해소된다).
  - 약 20행이 줄어든다.
  - 복원 직후 템플릿 헤드가 LRU(한도 4)에 남아 있으면 전체 검증 1회(부하 중 약 0.9초)를 아낀다. 다만 시험 하나가 여러 번 게시하면 그 헤드는 곧 밀려나므로, 이 절감은 작다고 본다.
- 비용과 위험:
  - 시험이 복원본의 artifact 바이트를 일부러 훼손하고 탐지를 기대하는 경우, 이전 복원본에서 남은 `VERIFIED_ARTIFACTS` 항목이 탐지를 건너뛰게 할 수 있다. 제품의 같은 프로세스 안에서도 같은 생략이 일어나므로 D1의 수용 범위다. 그런 시험은 이미 `patch.dict(..., clear=True)`로 스스로 비운다(`test_submission_flow.py:452`, `test_native_final_submission.py:209`).
  - `_VALID_ARTIFACTS`는 형식 검증기(`validate_artifact`)를 키에 담지 않는다. 시험마다 다른 검증기를 주는 곳이 있으면 남은 항목이 결과를 바꿀 수 있다.
  - 새 상태·수명 규칙은 생기지 않고, 오히려 규칙 하나가 사라진다.
- 기능·커버리지 영향: 없음
- 사용자 결정 관련: 없음
- 확신도: 추정. 두 가지를 확인하면 확정된다. 하나는 템플릿 복원본에서 artifact 바이트를 훼손하고 탐지를 기대하는 시험이 위 두 곳 말고는 없는지를 `git grep -n "runtime/artifacts" -- tests` 결과에서 쓰기 호출로 좁혀 보는 것이다. 다른 하나는 `validate_artifact`를 시험마다 다르게 주는 곳이 없는지다. STO의 캐시 키 판정과 대조하면 좋다.

#### TSB-15 9b434f4 병렬 작업이 입력 복구 시작 상태 도우미를 둘로 만들었고, 한쪽 패치는 이제 아무 일도 하지 않는다
- 검토: 2
- 종류: 잔재
- 좌표: `scripts/tests/test_approved_five_repairs.py:17-33,245-249`; `scripts/tests/test_input_recovery.py:24-31,89-97`
- 현상:
  - `INPUT_RECOVERY_CONFIG`(test_approved_five_repairs.py:19)는 `ACTIVE_CONFIG`(test_input_recovery.py:25)와 같은 값의 사본이다.
  - `restore_input_recovery_state`(22-33)는 `InputRecoveryPublicTests.setUp`+`active_repository`(89-97, 28-31)와 같은 일(어댑터 패치, 같은 템플릿 복원, `root`·`repo`·`identifier` 설정)을 한다.
  - 249행은 `patch.object(InputRecoveryPublicTests, 'setUp', restore_input_recovery_state)`로 원본 setUp을 이 사본으로 바꿔 끼운다. 그런데 원본도 이미 같은 템플릿 복원이므로 이 패치는 효과가 없다.
- 근거:
  - `git show 9b434f4 -- scripts/tests/test_input_recovery.py scripts/tests/test_approved_five_repairs.py`로 확인했다. B1 작업자가 원본을 템플릿으로 바꾸고, 병렬의 B3 작업자가 같은 목적의 사본을 따로 만들었다.
  - `git grep -c "restore_input_recovery_state\|INPUT_RECOVERY_CONFIG"`는 `test_approved_five_repairs.py`에만 5건이다.
- 제안: 사본 둘과 249행의 패치를 지우고 `NativeFinalGitTests.setUp(self)`를 직접 부른다.
- 실익: 약 18행이 줄고, 같은 시작 상태 정의의 사본(설정값 포함)이 사라진다.
- 비용과 위험: 파일 1개, 위험은 없다.
- 기능·커버리지 영향: 없음
- 사용자 결정 관련: 없음
- 확신도: 확인

#### TSB-16 G2가 제안한 이의·철회 시험 병합이 구현되지 않았다
- 검토: 2
- 종류: 공백
- 좌표: `scripts/tests/test_purpose_engine.py:527-543`; `scripts/tests/test_review_research.py:175-182`; `C:/math/임시/시험-경량화-2026-09-26/분석-G2.md` 2.2절 (2)항과 7절
- 현상:
  - `test_objection_judgment_answer_and_final_approval_use_real_engine`(full1 79.2초)과 `test_confirmed_withdrawal_closes_before_the_round_cap`(56.9초)은 같은 검토 회차 경로를 공개 엔진으로 두 번 돈다.
  - G2는 이 둘을 합치자고 제안했다. 이의 시험에 `review_rounds=3`과 `round == 2` 단언을 더하고 철회 시험을 지우는 안이다.
  - 9b434f4의 두 파일에는 이 변경이 없다.
- 근거: `git show 9b434f4 -- scripts/tests/test_review_research.py`에서 철회 시험은 그대로다. 이의 시험의 설정에도 `review_rounds`가 없다(527-543).
- 제안: G2의 안대로 합친다. 새 설정값 때문에 템플릿 키가 하나 늘어나 빌드가 한 번 더 생기는지 확인하고, 생기면 그 비용(약 9초)을 절감에서 뺀다.
- 실익: 약 50초(56.9초 − 새 템플릿 키 비용), 시험 1개가 줄어든다.
- 비용과 위험: 파일 2개가 바뀐다. 이의 시험이 두 성질(이의 응답, 회차 상한 전 종결)을 단언하게 되는데, G2가 둘이 같은 경로의 연속 상태임을 근거로 들었다.
- 기능·커버리지 영향: 없음. 두 성질 모두 합친 시험에서 단언된다.
- 사용자 결정 관련: 없음
- 확신도: 확인. 미구현은 원문과 `git show`로 확인했다. 절감량은 full1 기준의 추정이다.

#### TSB-17 조각 단독 시간이 재어진 적이 없고, 지침의 측정 절차는 그것을 낼 수 없다
- 검토: 2
- 종류: 공백
- 좌표: `scripts/tests/시험-지침.md:37`; `scripts/run_tests.py:305-313`; `scripts/tests/research_fixtures.py:821-859`(`_TEMPLATES`)
- 현상:
  - 지침은 통합자가 "통합 확인의 `report.json`에서 조각별 시간"을 보고 120초를 판정하게 한다(37).
  - 그러나 `run_tests.py`는 프로세스 안 조각들을 한 프로세스에서 순서대로 돌리고(305-313), 템플릿 캐시 `_TEMPLATES`는 프로세스 전역이다. 따라서 전체 실행의 조각 시간은 앞 조각이 이미 만든 템플릿을 재사용한 값이다.
  - 예를 들어 `active_instance(CURRENTNESS_CONFIG)`는 lifecycle의 `test_checkpoint_persistence`에서 만들어지고 research에서 재사용된다. 기본 `activated_instance`는 research에서 만들어지고 academic이 재사용한다.
  - 조각을 단독으로 돌리면 그 빌드 비용이 그 조각에 붙는다.
- 근거:
  - M-0350과 W-fix 노드에 남은 최종 확인은 병렬 실행이었다. 추적 변경 이후 조각별 단독 측정은 기록에 없다.
  - full1(추적 변경 전, 한 프로세스 순차)의 조각 시간은 research 828, review 538, lifecycle 411, academic 277, foundation 259, host 128초, 합계 약 2440초다.
- 제안:
  - 지침 37행을 "조각 시간은 `--shard <이름>` 단독 실행으로 잰다"로 고친다.
  - 다음 통합 때 조각 여섯 개를 단독으로 한 번씩 재서 기록한다.
  - 조각 재배치(`SHARDS` 수정)는 그 수치를 본 뒤 판단한다. 템플릿이 조각마다 다시 만들어지므로, 조각을 쪼개면 합계가 오히려 늘 수 있다.
- 실익: 120초 목표의 판정 근거가 생긴다. 편향된 수치로 모듈을 옮기는 일을 막는다.
- 비용과 위험: 문서 1행이 바뀌고, 측정에 1회 실행 비용이 든다.
- 기능·커버리지 영향: 없음
- 사용자 결정 관련: 있음. 시간 목표(조각당 120초·합계 300초)는 "실익 있는 수단을 다 쓴 뒤에도 넘으면 받아들이는 목표"다. 새로 드러난 사실은 두 가지다. 하나는 시험 쪽 수단(TSB-03·04·05·16)을 모두 써도 합계 절감이 약 150~250초로 추정되어, 조각당 수백 초 수준이 남는다는 점이다. 다른 하나는 남는 비용의 주성분이 M-0350이 기록한 게시당 `update-ref` 프로세스(git 시간의 74%)와 객체 fsync라는 점이다. 이것을 줄이는 안(저장 병합·fsync 제거, 안 C)은 사용자가 보류했다. 따라서 목표를 계속 쫓을지, 현재 수준을 받아들일지는 사용자 판단 사항이다.
- 확신도: 확인. 측정 절차의 편향은 원문으로 확인했다. 절감 추정은 full1 기준이다.

## 4. 보존 판정

- `scripts/tests/test_windows_job.py`의 ctypes Job 구조체 재선언: 제품 `windows_job`의 선언과 모양이 같지만, 독립 오라클로서 제품 선언의 오류를 잡는 것이 목적이다. 제품 정의를 import하면 같은 오류를 공유한다.
- `scripts/tests/test_background_processes.py:27,120`과 `test_formal.py:85,212,225`의 `git init`·`git add`·`git commit` 자식 프로세스: 자식 프로세스 생성과 창 플래그, 또는 Lean 프로젝트의 Git 작업 트리 자체가 검사 대상이다(지침 4.6의 예외).
- `run_tests.py`의 전체 발견(discovery): 시험을 돌리지 않는 발견 비용은 1.87초(1862개)다. 모든 모듈의 import 오류를 매 실행 잡으므로, 조각별 발견으로 줄일 실익이 없다.
- `local_job_runner`와 `StopFlag`의 실제 Job 사용, 실제 창 경계를 기다리는 `sleep(1.05)`: 2라운드 TST 보존 1과 같은 근거다. 실제 프로세스 수명과 시각 경계가 검사 대상이다.
- `test_static_review_repairs.py:168`의 문서 예제 pwsh 실행: 문서의 명령이 실제로 도는지가 검사 대상이다.
- `test_submission_flow.py:452`와 `test_native_final_submission.py:209`의 `patch.dict(VERIFIED_ARTIFACTS, clear=True)`: 대조 생략 없이 훼손 탐지를 검사하려고 명시적으로 비운다. TSB-14의 결합과 달리 검사 대상이 그 캐시다.
- `test_input_recovery`의 `InputRecoveryMarkerUnitTests.legacy_pending`: 이름은 옛 표지를 말하지만, 현행 계약이 그 표지를 거부하는지를 단언한다. 기준 2절 4항의 "현행 계약 하나만"을 지키는 시험이다.
- 모듈마다 다른 설정 리터럴(`ACTIVE_CONFIG`, `CURRENTNESS_CONFIG` 등): 2라운드 TST 보존 3과 같다. 각 값은 그 모듈이 단언하는 성질의 입력이다. TSB-15의 사본은 같은 목적의 같은 값이라 예외다.
- `GitPurposeTests`를 뺀 공개 e2e 3개(공개 초기화·활성화 자체가 대상인 시험): 지침 4.3의 4단 판별에 따라 공개 경로를 유지한다.
- `test_diagnosed_installation_recovery.py:31-42`의 `SessionSlots` 대역: 전이 규칙은 제품의 `transition_execution`과 `launch.ticket`을 그대로 부른다. 대역에 남는 것은 "승인 때 starting, 시작 때 running"이라는 호출 순서뿐이며, 이것이 대역이 흉내 내야 할 계약 자체다. 실제 `SessionSlots`(session_slots.py:184,221)로 바꾸면 호스트 자원과 Job이 필요해져 시험이 비싸진다.

## 5. 영역 밖 관찰

- REV: `scripts/do_math/review_engine.py:456`의 `config.get('review_scope_assessment')` 대체값은 설정 스키마에 없는 키를 읽으며, 시험 대역만 채운다(TSB-11).
- STO: `scripts/do_math/submission.py:121`의 `_ISSUED_INPUTS` 키는 `(git_dir, path)`라 내용 해시가 없다. 제품 번들 이름이 ULID라 지금은 안전하지만, 이음새 계약 3절 "저장소가 다르면 같은 경로라도 별개로 다룬다"(`C:/math/docs/do-math/검사-경량화-이음새-계약.md:84`)를 경로 문자열로만 지킨다. 같은 경로에 저장소를 다시 만들면 계약을 어긴다.
- STO: `scripts/do_math/repository.py:111`의 `_RETAINED_READS`는 `git_dir`만 키로 삼는 보존 힌트다. 틀린 답을 내지는 않지만, 지워진 저장소의 항목이 프로세스 끝까지 남는다.
- STO: 게시 1회당 `update-ref` 자식 프로세스(M-0350: git 시간의 74%)를 없애는 안으로 프로세스 안 참조 CAS(Git lockfile 규약 직접 구현)가 있다. 기준 2절 12항의 "update-ref의 기대값 비교로만"을 바꾸므로 사용자 결정 사항이다.
- ENG: `scripts/do_math/engine.py:885-889`의 pump 순서를 이름 붙인 메서드로 뽑을 수 있는지(TSB-07).
- TSA: `scripts/tests/test_test_runner.py`의 `in_process` 표지 자기시험(TSB-08과 함께 바뀐다).
- TSA: `scripts/tests/test_redesign_REVIEWS.py:185,198,395,474`의 `review_scope_assessment`(TSB-11과 함께 바뀐다).
- TSA: `scripts/tests/test_reading_map.py:11,60`의 `ActiveStateHarness` 사용(TSB-06과 함께 바뀐다).
- TSA: `scripts/tests/test_knowledge_import_engine.py:307`의 `DO_MATH_KNOWLEDGE_AUDIT_DIR` 훅도 TSB-09와 같은 생산자 없는 보고 훅인지 확인이 필요하다.
- HIS: `C:/math/.agents/skills/do-math/` 아래에 같은 시험 파일이 보인다(`git grep` 결과에 함께 나온다). 사본인지 연결인지는 확인하지 않았다.

## 6. 작업 기록

- 시험 실행이 금지되어, 조각을 돌려 재려던 계획을 버렸다. 시간 근거는 로컬 `C:/math-worktrees/tools/full1/report.json`(추적 변경 전, 한 프로세스 순차)과 W-fix 노드의 부하 중 측정으로 대신했다. 그래서 시간 절감은 모두 추정으로 적었다.
- 발견 비용 확인에는 저장소를 바꾸지 않는 한 줄 명령 하나를 썼다. scripts 폴더에서 `python -B -c`로 `unittest.defaultTestLoader.discover('tests')`만 부르고, 시험 수와 걸린 시간을 출력하는 형태다. 결과는 시험 1862개, 1.87초였다.
- 시험 모듈 사이의 import 집계에는 `ast`를 쓰는 읽기 전용 파이썬 스크립트를 썼다. 결과는 영역 59개 가운데 빌려 오는 모듈 44개, 빌려 주는 시험 모듈 45개였다.
- 쓰이지 않는 import도 `ast`로 집계했다. 결과는 파일 63개 가운데 24개에서 43건이었고, `annotations` 13건을 빼면 17개 파일에 30건이었다. 재수출은 21개 조합 모두 0건이었다.
- `C:/math` 전체에 대한 Grep 도구 검색이 시간 초과로 멈췄다. 그 뒤로는 `git grep`을 썼다.
- 예상과 달랐던 결과가 넷 있다.
  - `forget_repository_caches`가 비우는 캐시 넷 가운데 셋은 키가 내용 주소였다. 처음에는 "경로 키 캐시가 이음새 계약 3절과 모순된다"는 후보를 세웠으나, 원문의 키를 확인하고 "비울 필요 없는 결합"으로 고쳤다(TSB-14).
  - 쓰이지 않는 import 대부분은 세 경량화 이전부터 있었다.
  - G2의 이의·철회 병합이 구현되지 않은 채 남아 있었다.
  - 요약 단계에서 적어 둔 `SessionSlots` 대역의 행 번호(184-192)는 제품 `session_slots.py`의 것이었다. 시험 쪽 실제 위치는 31-42이며, 대역이 제품 전이 함수를 쓰는 것을 확인해 후보에서 보존으로 옮겼다.
