# 결과 — RES 그룹 (연구 흐름·지식·형식)

## 1. 브랜치, 커밋, 바꾼 파일

- 브랜치: `c-res` (worktree `C:/math-worktrees/c-res`). 시작 커밋은 `d7d1b39`(당시 `c-int`)이다.
- 커밋은 둘이다.
  - `379f7bd` — 담당 ID, 후속 항목, 통합자가 더한 항목 (2)의 구현
  - `c1aa372` — 통합자가 더한 항목 (1). **`c-int`의 REV-10(`task_scope.assessment_current(..., records=)`)이 있어야 동작한다.** 이 커밋만 있는 `c-res` 단독 트리에서는 의존 과제가 있는 `task_ready`가 `TypeError`를 낸다. 그래서 인계 확인은 이 커밋 전의 `379f7bd`에서 돌렸다.
- 마지막 커밋: `c1aa372cafc8c3317e66984b48c92e25ac87b700`
- **`c-int`와 병합하면 충돌한다.** `c-int`에 RUN 그룹(RUN-18)이 병합되면서 내가 고친 함수 일부가 다른 모듈로 옮겨졌다. 충돌 위치와 재적용 방법은 7절에 적는다.

바꾼 파일(경로는 `.claude/skills/do-math/scripts/` 기준):

- 제품: `do_math/academic.py`, `academic_engine.py`, `engine.py`, `formal.py`, `git_store.py`, `knowledge.py`, `lifecycle_engine.py`, `planning.py`, `question_engine.py`, `record_schemas/schemas.py`, `reporting.py`, `repository.py`, `revision_engine.py`, `scheduler.py`, `state_checks.py`, `trust_validation.py`
- 시험: `tests/research_fixtures.py`, `test_academic_engine.py`, `test_environment_validation.py`, `test_formal.py`, `test_knowledge.py`, `test_knowledge_import_engine.py`, `test_lean_preview.py`, `test_lifecycle_engine.py`, `test_model_assessment_flow.py`, `test_performance_repairs.py`, `test_planning.py`, `test_redesign_EVIDENCE_walkthroughs.py`, `test_redesign_LIFECYCLE.py`, `test_redesign_STORAGE.py`, `test_redesign_TASKS.py`
- 문서: `이음새-정본.md`(3절 규칙 한 줄과 6절 표의 새 행 넷)

## 2. ID별 처분

아래 좌표는 `c1aa372`의 파일 기준이다.

- **RES-05 — 구현함.**
  - 새 입력 사건의 ID는 이제 `newinput` 값(입력 요청 ID)과 과제 ID에서 나온다(`planning._event`의 `key`, `planning.py:854`). 같은 입력은 관찰 시각과 무관하게 한 사건이며, 사건에 `request_id`를 싣는다.
  - 기한 사건 수집은 제자리 함수 `planning.record_due_events` 한 경로로 모았다(`planning.py:884`). `apply_event_schedule`(런타임 전체 `deepcopy`)을 지웠다. `schedule_reconsideration`은 더 이상 수집하지 않고, 기록된 사건을 배정만 한다. 제품에서 이 함수를 부르는 곳은 준비 갱신 직후의 한 곳뿐이다.
  - 수명 엔진의 `task_new_input` 중복 필터 약 8행을 지웠다(`lifecycle_engine.py:1038`).
  - 스키마의 `newinput`을 요청 ID(`ID`)로 좁혔다.
  - 소비(`engine._consume_action_events`, `engine.py:2612`)는 이제 과제의 `newinput`이 사건의 `request_id`와 같을 때만 신호를 지운다(`del`). 원래 코드는 무조건 `False`로 덮었다. 그래서 소비 사이에 새 입력 요청이 들어오면 그 신호가 사라졌다. 이 결함은 사건 ID를 요청 ID로 바꾸면서 드러났고 같은 변경으로 막았다.
  - 재현: 새 엔진 시험을 변경 전 코드(`HEAD` 추출본)에서 돌리면 시계를 5초 옮긴 두 번째 갱신 뒤 `task_new_input` 사건이 2개였다(`AssertionError: 2 != 1`).
- **RES-06 — 구현함.**
  - 검사기 동일성은 이제 실행 중 모듈 바이트의 SHA-256으로 판정한다. 이 값은 모듈이 적재될 때 자기 loader로 한 번 읽는다(`formal._RUNNING_CHECKER_SHA256`, `formal.py:22`).
  - `inspect_toolchain`의 기록(`:401`)과 `toolchain_identity_errors`의 대조(`:420`)가 모두 이 값을 쓴다. 경로 비교는 지웠다.
  - 기록된 `verifier_path` 파일과 `verifier_sha256`의 대조는 유지한다.
  - 재현: 변경 전 코드로 zip을 만들어 `formal`을 적재했다. `__file__`은 `...\support.zip\do_math\formal.py`였고, 결과는 `["approved checker is not the running checker"]`였다. 수리 뒤에는 이 재현을 `test_lean_preview.test_preview_checker_loaded_from_the_support_archive_is_the_approved_checker`로 남겼다. 이 시험은 `install_tools`가 만든 실제 `submission-support.zip`에서 `formal`을 적재하고, 그 경로가 zip 안임과 오류 없음을 단언한다.
- **RES-07 — 구현함.** `formal._git`이 `subprocess.run`(stdin DEVNULL, 출력 캡처, 창 없음)을 직접 부른다(`formal.py:25`). 취소는 호출 전후의 `_check_stop`으로 확인한다. 시간 효과는 재지 않았다(5절).
- **RES-09 — 구현함.**
  - `planning.instance_record(instance)`(`planning.py:204`)를 인스턴스 가족의 유일한 기록으로 정했다. 이 기록은 인스턴스 ID, 목표 상태, `governance_revisions`의 두 판본만 담는 정규 투영이다. `record_index`가 인스턴스 가족에 이 기록을 싣는다.
  - 그래서 조건 평가, `capture_task_basis`, 계약 검토 기초, 착수 판정은 호출자가 저장 인스턴스를 주든 `governance_working_view`를 주든 같은 기록을 본다.
  - 승인 헌장이 하나로 정해지기 전에는 판본을 싣지 않는다(`governance_view`의 `ValueError`를 이 뜻으로만 받는다).
  - 비용: `record_index` 1회에 약 50µs가 더 든다. `approved_fixture` 기준으로 `task_ready` 1회는 2.16ms에서 2.23ms가 되었다. 한 번의 `task_ready`가 `record_index`를 2회 부른다.
- **HIS-09 — 구현함(RES-09와 같은 사안).**
  - 판정 입력은 `instance_record` 하나다.
  - 원 인스턴스를 주던 11곳(`engine.py`, `decision_engine.py`, `revision_engine.py`)은 코드 변경 없이 이 투영을 쓰게 되었다.
  - 투영을 주던 곳은 저장 인스턴스를 주도록 바꿨다. 수명 엔진의 준비 갱신(`lifecycle_engine.py:964-1021`: `capture_task_basis`, `review_basis_key`, `contract_review_current`, `task_ready`, 그리고 `required`는 `governance_revisions` 사용)과 `scheduler.py:472`의 `task_ready`가 여기에 든다.
  - 같은 이유로 `scheduler.py:158`의 `schedule_reconsideration`도 저장 인스턴스를 받는다. 이 호출은 통합표의 15곳 밖이지만 `exhaustion_state`를 거쳐 `task_ready`에 닿는다.
- **RES-10 — 구현함(키가 제안과 다르다).**
  - 형식 판정 메모는 이제 `(판정 함수, 경로, sha256) → 참/거짓`의 순수 메모다(`planning.py:37`).
  - 바이트 대조는 평가마다 `sealed_bytes`가 맡는다. 판정이 이미 있으면 `needed=False`로 바이트를 읽지 않고, 길이는 `VERIFIED_ARTIFACTS`의 값을 쓴다.
  - `forget_repository_caches`에서 이 메모를 뺐다.
  - 제안의 `(path, sha256)`에 판정 함수를 더했다. 통합표의 보충 위험, 곧 시험들이 서로 다른 판정자(Mock, 람다)를 넣어 메모가 시험 사이에 섞이는 문제를 이 방법으로 해소했다. 키에 판정자가 있으면 판정은 그 판정자의 순수 함수이므로 격리용 고유 `git_dir`이 필요 없다. 또 "git_dir이 없으면 메모하지 않는다" 규칙도 필요 없어 지웠다.
  - 새 상태는 없다(기존 메모의 키만 바꿨다).
- **RES-11 — 구현함.**
  - `git_store.ARTIFACT_ROOT`(`git_store.py:71`)를 새 공유 상수로 두었다.
  - `artifact_valid` 문법은 이제 이 접두와 성분마다의 `check_path_segment`로 검사한다(`planning.py:340`).
  - 판독기(`engine.py:134`)와 기존 번들 불변 검사(`git_store.py:518`)도 같은 상수를 쓴다.
  - `test_redesign_TASKS`의 `out/proof.txt`는 `runtime/artifacts/BA-1/proof.txt`로 고쳤다.
- **RES-15 — 구현함.**
  - 등록 분기(`lifecycle_engine.py:691`)가 완전한 기록을 한 번에 만든다. 그리고 `environment_errors`를 통과한 뒤에만 인스턴스에 넣는다.
  - `knowledge.register_environment`는 지웠다.
  - 지운 함수만 하던 `allowed_axioms` 중복 거부는 `trust_validation.environment_errors`의 길이 조건으로 옮겨 수신 검사를 유지했다.
  - `test_redesign_LIFECYCLE`의 import를 지웠다.
- **RES-16 — 구현함.** `question_engine`의 inline 분기 세 곳을 지웠다. `engine.py:1842`의 같은 조건과 스키마의 `parent_execution_id`는 통합표대로 두었다(8절).
- **RES-18 — 구현함.** `knowledge.py`의 `capture_sources, sources_current` import와 `revision_engine.py`의 `CurrentnessChanged`, `new_id` import를 지웠다.
- **HIS-19 — 구현함.** `_academic_evidence`가 `missing="omit"`으로 읽는다(`academic_engine.py:52`). 없는 경로는 `None`이 된다.
- **후속: `semantic_content_hash` — 구현함.** 사용처(`engine._record_evidence`, `knowledge._hash`, 시험 1곳)를 `exact_content_hash`로 바꾸고 별칭을 지웠다. 별칭만 검사하던 `test_redesign_STORAGE.test_byte_and_semantic_hashes_are_explicitly_distinct`도 지웠다. `exact_content_hash`의 정의는 `test_digest_characterization`이 검사한다.
- **후속: 상태 점검의 엔진 믹스인 의존 — 구현함.** `current_solution_basis`를 `academic.py:50`으로 옮겼다. `state_checks`, `reporting`, `academic_engine`이 모두 이것을 쓴다. `academic`에서 `governance`와 지식 모듈은 순환을 피하려고 함수 안에서 import한다.
- **후속: `research_reconsider_seconds`의 기본값 사본 — 구현함.** `planning.py:849`는 이제 `instance['config'][...]`를 직접 색인한다. 같은 사본이 `lifecycle_engine._reconsider_interval`에도 있었다(`.get(..., 86400)`와 형 검사). 그래서 그곳도 직접 색인으로 바꿨다. 값의 형과 범위는 설정 스키마가 보장한다.
- **통합자 추가 (1): `task_ready`가 `assessment_current`에 `records=`를 넘김 — 구현함(`c1aa372`, `c-int` 필요).** 두 곳(`planning.py:656`, `:709`)을 바꿨다. 이 커밋은 시험하지 않았다(5절). 확인한 것은 둘이다. 하나는 `c-int`의 `task_scope.py:282`에 `records=None` 인자가 있다는 것이다. 다른 하나는 REV의 `planning.py` 변경이 이 두 줄과 겹치지 않는다는 것이다.
- **통합자 추가 (2): `knowledge._DECISION_BOOKKEEPING`의 스키마 밖 이름 — 구현함.**
  - 지목된 둘(`producer_execution_ids`, `required_reviews`)과 함께 같은 기준에 걸린 넷(`review_history`, `verified_at`, `identity_assessment`, `formal`)도 지웠다.
  - 기준은 이렇다. `content_hash`가 적용되는 가족(`knowledge.BASIS_FAMILIES`와 통합 변경 대상인 지식·과제)의 닫힌 저장 스키마에 그 필드가 없고, 제품의 다른 곳이 그 필드를 기록에 쓰지 않는다.
  - `producer_execution_ids`는 검토 주기 스키마에만 있다. 검토 주기는 `content_hash`의 대상이 아니다.
  - `formal`은 `_IDENTITY_BASIS` 안의 중첩 필드로만 나온다.

집계: 구현함 11(담당 ID) + 후속 3 + 추가 2. 구현하지 않음 0, 조건 불성립 0, 끝내지 못함 0.

## 3. 새 공유 정의와 지운 공개 이름

새 공유 정의(모두 `이음새-정본.md` 6절에 올렸다):

- `git_store.ARTIFACT_ROOT`
- `planning.instance_record(instance)`
- `planning.record_due_events(instance, runtime, now_iso)`
- `academic.current_solution_basis(instance, runtime)`(`academic_engine`에서 옮김)

`이음새-정본.md` 3절의 파생값 메모 규칙도 새 `artifact_valid` 메모에 맞게 고쳤다.

지운 공개 이름:

- `planning.apply_event_schedule`
- `knowledge.register_environment`
- `repository.semantic_content_hash`
- `academic_engine.current_solution_basis`(옮김)

`formal._git`의 정지 문구 `'project inspection stopped'`는 `'verification stopped'`로 바뀌었다.

## 4. 필요한 문서 변경

- `references/초기화-효율과-정비.md`
  - 18행(형식 검사 1건의 대조)과 61행(판본 식별의 검사기 `formal.py`의 "경로·SHA-256")에 한 문장을 더한다. 내용: "실행 중인 검사기는 경로가 아니라 적재한 모듈 바이트의 SHA-256으로 판본 식별의 검사기와 대조한다. 그래서 작업 공간 미리보기처럼 zip에서 적재한 같은 바이트도 같은 검사기다. 기록된 경로의 파일은 그 SHA-256과 계속 대조한다."
- `references/과제-착수조건.md` 18행(`artifact_valid`)
  - 지금 문장("`path`는 `runtime/artifacts/` 아래의 상대 경로다")은 구현과 맞는다.
  - "이 규칙과 경로 성분의 저장 규칙을 어기는 조건은 제출 단계에서 거부된다"를 더하면 거부 시점이 드러난다(선택).
- `references/CLI-실행-계약.md` 573행(`trust register`): 바꿀 것이 없다. `allowed_axioms`의 중복 거부는 기존 동작을 유지한 것이다.

## 5. 실행한 시험

모든 명령은 `.claude/skills/do-math/scripts`에서 `python run_tests.py ...`로 돌렸다. Lean이 필요한 모듈에는 `DO_MATH_KNOWLEDGE_TEST_LEAN`을 주었다.

- **인계 확인(`379f7bd` 트리)**
  - 대상: `test_planning test_formal test_knowledge test_lifecycle_engine test_academic_engine test_academic test_engine test_git_store test_question_flow test_questions test_reporting test_repository test_revision_obligations test_state_checks test_environment_validation test_redesign_STORAGE test_lean_preview test_knowledge_import_engine test_model_assessment_flow test_performance_repairs test_redesign_LIFECYCLE test_redesign_TASKS test_redesign_EVIDENCE_walkthroughs`
  - 결과: **478 통과, 실패 0, 오류 0**(686.9초). 보고서는 `C:\Users\wogud\AppData\Local\Temp\do-math-tests-h7nwno_0\report.json`이다.
- **편집 확인**
  - 편집 확인 중 오류 4건이 났고, 모두 시험 쪽 문제였다.
  - 2건: `test_redesign_TASKS`의 최소 runtime에 `events`가 없었다. 원래는 수집 단계의 `setdefault`가 이 키를 만들었다. 제품 runtime에는 초기화부터 `events`와 `pending_events`가 있으므로 시험 runtime에 두 키를 더했다.
  - 1건: 새 엔진 시험이 과제 dict를 붙잡고 있었는데, 스케줄러가 runtime을 바꿔 끼워 그 dict가 낡았다. 시험에서 과제를 매번 조회하도록 고쳤다.
  - 1건: 시험 ID 오타였다.
- **변경 전 실패 확인**
  - `HEAD` 추출본(임시 폴더, worktree 아님)에 새 시험을 넣고 돌렸다. 네 시험이 모두 실패 또는 오류였다.
    - `test_lifecycle_engine...one_input_request...`: 2 != 1
    - `test_performance_repairs...verdict_belongs_to_its_validator...`: (4, 2, 2) != (4, 1, 1)
    - `test_planning...instance_conditions...`: `evaluation_error` != `ready`
    - `test_planning...artifact_condition_grammar...`: 옛 코드에 상수가 없어 오류
  - RES-06의 재현은 2절에 적었다.
- **소비자 쪽 기계 확인**
  - 바꾼 `.py` 전부 `py_compile`을 통과했다. `tests/test_*.py` 전 모듈을 `importlib`로 적재했고 실패는 0이다.
  - 옛 이름(`apply_event_schedule`, `register_environment`, `semantic_content_hash`, `academic_engine import current_solution_basis`, `inline`, `_VALID_ARTIFACTS`의 시험 사용)을 grep했다. `c-res`에서 남은 참조는 0이다.
  - 바꾼 제품 모듈을 AST로 검사한 결과, 새로 생긴 미사용 import는 없다.
- **돌리지 않은 시험**
  - `c1aa372`: `c-res` 단독으로는 돌 수 없다(1절). 통합 뒤 `test_planning`, `test_redesign_TASKS`, `test_lifecycle_engine`으로 확인해야 한다.
  - RES-07의 시간 효과: 계약 6절 7에 따라 쌍 측정이 따로 필요하다. 이번에는 통과 확인만 했다.
  - 조각과 전체: 계약에 따라 돌리지 않았다.

## 6. 기능이나 시험 범위가 바뀐 것

- **미리보기의 검사기 동일성(RES-06)**
  - 이유: 사용자 판정.
  - 얻는 것: 활성 환경의 미리보기가 컴파일 피드백을 준다.
  - 잃는 것: 같은 바이트의 다른 설치본(미러, zip)도 게시 관문의 "실행 중 검사기" 조건을 통과한다. 경로 동일성은 더 이상 요구하지 않는다.
  - 통합표가 적은 대로, 통합자가 불변 조건 "설치 판본 일관성"의 약화 여부를 판단해야 한다. 설치 파일의 변경은 여전히 `verifier_path` 파일 대조와 설치 판본 검사가 잡는다.
- **git 호출(RES-07)**
  - 잃는 것: git 호출이 멈춘 동안은 정지 요청으로 끊을 수 없다. 호출 전후에만 확인한다.
  - 얻는 것: 호출마다 Job과 worker를 띄우지 않는다.
- **`artifact_valid`(RES-11)**
  - 산출물 밖 경로를 가리키는 조건은 이제 평가 오류를 반복하지 않고 제출 단계에서 거부된다.
- **`newinput`(RES-05)**
  - 스키마가 요청 ID만 받는다. `True`와 `False`는 이제 저장 불가다(저장 계약 `do-math-state/7` 안의 변경).
  - 새 입력 사건은 입력 요청마다 하나다.
  - `schedule_reconsideration`은 기한 사건을 수집하지 않는다. 그래서 직접 부르는 시험 넷은 먼저 `record_due_events`를 부르도록 고쳤다.
- **지운 시험**
  - `test_redesign_STORAGE.test_byte_and_semantic_hashes_are_explicitly_distinct`: 폐기한 별칭만 검사했다.
- **시험 범위가 바뀐 곳**
  - `test_environment_validation`의 "moved" 단언은 새 계약으로 바꿨다. 같은 바이트의 복사본은 통과하고, 다른 바이트면 "not the running checker"다.
  - `test_formal`의 변경 프로젝트 시험은 이제 Job 호출 자체를 금지한다. git이 Job을 쓰지 않기 때문이다.
  - `test_knowledge_import_engine`의 `formal.__file__` 패치 3곳은 의미가 없어져 지웠다.

## 7. 막힌 지점, 접근을 바꾼 지점, 예상과 달랐던 결과

- **`c-int` 병합 충돌.** 작업 중에 `c-int`에 RUN(`5dc45b6`, `45fee5e`, `640e9e3`)과 REV가 병합되었다. `git merge-tree --write-tree c-int c-res`로 확인하니 `lifecycle_engine.py`와 `scheduler.py`가 충돌한다. 계약상 병합하지 않았다. 재적용할 곳은 다음과 같다(좌표는 `c-int` 기준).
  1. `lifecycle_engine.py:16-18` import: `apply_event_schedule`을 `record_due_events`로 바꾸고 `governance_revisions`를 더한다. `c-int`의 import 목록 자체는 유지한다.
  2. `lifecycle_engine.py:24` `_reconsider_interval`: 본문을 `return timedelta(seconds=config['research_reconsider_seconds'])`로 바꾼다.
  3. `lifecycle_engine.py:581` 부근(`_refresh_readiness`): `query_instance = governance_working_view(...)`를 `editions = governance_revisions(self.instance)`로 바꾼다. 이어서 `required`는 `{..., **editions}`로, 네 호출은 `self.instance`로 바꾼다. 656-663행의 `old_pending_inputs`부터 `self.instance, self.runtime = scheduled[...]`까지를 `record_due_events(self.instance, self.runtime, now.isoformat())` 한 줄로 바꾼다.
  4. `formal_engine.py:7`, `:38-44`(`_trust_control`이 이 파일로 옮겨졌다): import에서 `register_environment`를 빼고, 등록 분기를 `c-res`의 `lifecycle_engine.py:691-699`와 같은 코드로 바꾼다. `new_id`와 `deepcopy`는 이미 import되어 있다. 이것을 하지 않으면 병합 뒤 `formal_engine` 적재가 `ImportError`로 실패한다.
  5. `scheduler.py:167`, `:187`(`_schedule_reconsideration`, RUN이 제자리 방식으로 다시 씀): `c-int` 판을 받는다. 호출의 첫 인자를 `self.instance`로 바꾸고 `governance_working_view` import를 지운다.
  6. `scheduler.py:249`(`_dispatchable`): `task_ready`의 인자를 `self.instance`로 바꾸고 바로 위의 import를 지운다.
  7. `lifecycle_engine`의 셋째 충돌 덩어리(`_invalidate_goal_currentness`부터 `_validate_external`까지)는 RUN이 다른 모듈로 옮긴 코드다. `c-int` 쪽을 받고, 위 4만 반영한다.

  나머지 파일은 자동 병합된다. 병합 뒤 옛 이름 grep(`apply_event_schedule`, `register_environment`, `semantic_content_hash`, `academic_engine import current_solution_basis`)이 0건인지 확인하면 된다.
- **RES-10의 키.** 제안의 `(path, sha256)`만으로는 시험이 넣는 판정자가 메모를 오염시킨다(통합표 보충). 그래서 판정자를 키에 넣었다. 이러면 "git_dir 없으면 메모 안 함" 규칙과 시험 쪽 비우기가 모두 필요 없어진다.
- **RES-09의 투영 위치.** HIS-09는 호출부마다 투영 함수를 부르는 안이었다. 대신 투영을 `record_index` 안의 인스턴스 가족 기록으로 두었다. 그래서 11곳의 원 인스턴스 호출부를 고치지 않고도 모두 같은 투영을 쓰며, 새 호출부가 투영을 빠뜨릴 수 없다. 투영을 주던 호출부는 저장 인스턴스를 주도록 바꿔 입력 모양도 하나로 맞췄다.
- **예상과 달랐던 것 셋**
  - RES-05: 사건 ID를 요청 ID로 바꾸자 소비 코드의 무조건 `False` 덮어쓰기가 새 요청의 신호를 지우는 결함이 드러났다. 같은 변경에서 막았다(2절).
  - RES-05 엔진 시험: 같은 시각의 두 갱신에서는 옛 코드도 사건이 하나였다. 시계를 옮겨야 재현되었다.
  - RES-15: 지운 함수가 `allowed_axioms` 중복 거부를 혼자 맡고 있었다. 그래서 그 검사를 `environment_errors`로 옮겼다.

## 8. 다른 그룹 범위에서 발견한 문제

- **ENG·STO — `engine.py:1842`의 `reviewed_execution.get("parent_execution_id")`와 스키마 `executions.parent_execution_id`(`schemas.py:289`).** 생산자가 없다. 통합표 RES-16이 영역 밖으로 남긴 대로 두었다. 시험 2곳(`test_checkpoint_persistence.py:114`, `test_currentness_recovery.py:217`)이 이 값을 설정한다.
- **REV — `review_engine.py:218`.** 지식 기록의 `producer_execution_ids`를 읽는다. 지식 스키마는 닫혀 있고 이 필드가 없으므로 이 읽기는 늘 빈 목록이다.
- **RUN — `lifecycle_engine.py:215`(`c-res` 기준).** `from .initialization import ... INITIAL_ROLES ...`의 `INITIAL_ROLES`가 쓰이지 않는다. 기존부터 그랬다.
- **RUN·PLAN — `scheduler._finish_assessment_preparation`.** `c-int`에서는 `planning_engine.py:175`로 옮겨졌다. 여기서 `contract_basis`의 판본을 `governance_working_view`에서 읽는다. 값은 `governance_revisions`와 같으므로 뜻은 맞지만, 판본 읽기가 두 방식으로 남아 있다. `_assessment_input_version`(`planning_engine.py:35`)도 같다.
- **KNOW — `knowledge._HISTORY_KEYS`(`knowledge.py:117` 부근).** 이 집합에도 스키마 밖 이름 `review_history`가 있다. 통합자 추가 (2)의 대상이 아니라서 두었다.
