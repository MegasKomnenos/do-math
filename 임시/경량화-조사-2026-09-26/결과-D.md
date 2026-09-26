# 결과 — 그룹 D: 연구 흐름·지식·질문·개정·형식 증거

이 문서는 do-math 경량화 2라운드 그룹 D의 반환이다. 설계 `docs/do-math/경량화-설계-2026-09-26.md` 6절의 다섯 항목을 차례로 적고, 기존 이음새 계약 10절의 `이음새 요청`과 `추가한 이름`을 덧붙인다. 통합자는 이 문서로 그룹 D를 합칠지 판단하고, 다른 그룹 모듈에서 겹친 줄을 정리한다.

- 브랜치·커밋: worktree `C:/math-worktrees/r2-d`, 브랜치 `r2-d`, 커밋 `2e9078b`(기준 `24682fd`, 커널 병합 뒤)
- 변경 범위: 제품 23개 파일, 시험 13개 파일. 스킬 문서는 고치지 않았다(3절).
- 좌표: 경로는 `C:/math-worktrees/r2-d/.claude/skills/do-math/scripts/` 기준이고, 행 번호는 커밋 `2e9078b`의 것이다.
- 확인: 바꾼 파일 전부가 `python -m py_compile`을 통과했다. 설계 3.3절에 따라 시험은 실행하지 않았다.

## 1. ID별 처분

4.5절 표의 19개 ID를 모두 처리했다. 구현한 항목이 17개다. RES-08은 커널이 이미 구현해 할 일이 없었고, ENG-24는 동등성 조건을 충족하지 않아 바꾸지 않았다.

| ID | 처분 | 내용 |
|---|---|---|
| RES-01 | 구현함 | 가족 표의 정본은 `planning.RECORD_FAMILIES` 하나이고, 색인 함수 `planning.record_index(instance, runtime, *, families=None, source_aliases=False, question_links=False)`(`do_math/planning.py:382`)가 그 공개판이다. 옛 `planning._records`를 대체한다. 호출부는 planning·knowledge_io·delegations·integration·governance(4곳)·scheduler·task_scope(2곳)·engine에서 모두 옮겼다. `knowledge._records`·`_find`·`_impact_records`는 지우고 `knowledge._basis_records`(가족 필터 `BASIS_FAMILIES`, `knowledge.py:30-36`)로 바꿨다. 그래서 `capture_basis`·`validate_basis`는 호출마다 색인을 한 번 만들어 dict로 조회한다. 모집단은 지금 목록과 같다. `knowledge_records.all_records`는 같은 색인에 `RESEARCH_RECORD_FAMILIES` 필터를 건 결과다(`knowledge_records.py:11`, `:31`). `academic._evidence`는 공개 이름 `academic.evidence_record`로 바꿨다. 모집단은 `RECORD_FAMILIES`의 `EVIDENCE_FAMILIES` 다섯 가족이다(`academic.py:155-172`). `question_engine`의 `resolve` 클로저는 지우고 `self._academic_evidence`를 쓴다. 원자료 별칭 해석의 반복(`planning` 2곳, `knowledge_io` 2곳, `governance._import_basis`)은 색인의 `source_aliases` 선택 인자로 옮겼다. `governance._import_basis`의 question_links 덧붙이기는 `question_links` 선택 인자로 옮겼다. `engine._records`는 지우고, 유일한 호출부(`engine.py:2207`)는 `planning.record_index`를 부른다. 이 차이는 5절 1에 적었다. |
| RES-02 | 구현함 | `task_ready` 입구에서 색인을 한 번 만든다. 이 색인은 `user_waits`, `action_read_ids`, `capture_task_basis`, `revision_waits`(자기 행동과 살아 있는 실행 전부), 두 `evaluate_condition` 호출에 `records=` 인자로 넘어간다. 인자가 없으면 각 함수가 지금처럼 만든다. `ready_task_ids`와 `exhaustion_state`는 과제 루프 밖에서 `_shared_index`로 한 번 만든다(`planning.py:418`). 색인 구성이 실패하면 `None`을 넘겨, 과제마다 지금처럼 `evaluation_error`가 되게 한다. `revision_cycles`, `seal_contract_review`, `review_basis_key`도 한 번 만든 색인을 공유한다. `revisions.py`의 버려지는 `_records` 호출은 지웠다(채택된 삭제). |
| RES-03 | 구현함 | `knowledge_records.premise_failures(instance, record)`(`:134`)는 K 판정과 연구 재사용이 공유하는 전제의 실패를 차례로 내는 생성기다. 공유 전제는 기록 active·`kind_use_suspended` 아님, 종류 정의 active, `sources_current` 세 가지다. `record_premises_current(instance, record, visiting=())`(`:146`)는 여기에 의존 기록의 `usable_links`와 관계 기초 검사를 더한다. `usable_links`와 `assessment_current`는 이 함수를 쓴다. 방문 집합의 의미는 두 곳 모두 `{*visiting, record id}`로 같게 보존했다. `assess_research_use`(`knowledge.py:170`)는 `premise_failures`의 결과에 `research_` 접두를 붙여 사유로 쓴다. 자기 조건(`use_suspended`, 해설 lifecycle, 연구 수준 의존 재귀)은 그대로 둔다. `assess_use`의 `kind_use_suspended` 재검사는 지웠다. |
| RES-04 | 구현함 | `formal.py`에 `FORMAL_EVIDENCE_FIELDS`(`:141`), `lean_source_sha256(code)`(`:144`), `forbidden_axioms(axiom_rows, allowed)`(`:149`)를 두었다. `_parse_evidence`, `verify_lean`의 `source_sha256`, `compare_formal_results`, `begin_transition`, `formal_usable`, `validate_formal_evidence`가 이를 참조한다. `activate_transition`의 750-756행(기준 좌표) 재검사는 지우고 `validate_formal_evidence` 한 번으로 판정한다(`knowledge.py:735-738`). 수신 검사 자체는 유지했다. |
| RES-05 | 구현함 | `questions.py`에 세 함수를 두었다. `open_targets(row)`(`:11`), `close(row, *, kind, resolution_ref, affected_ids, status, evidence)`(`:52`), `resolution_error(row, role)`(`:67`)다. 세 닫기 경로는 모두 `close`를 부른다. 사용자 결정은 `resolve_user`, AI 확장은 `_apply_question_resolutions`, 입력 초과 재시도는 `engine._resolve_input_overflow_question`이다. 해소 이력은 `{kind, resolution_ref, affected_ids[, evidence]}` 한 모양이 되었다(저장 모양 통일 채택). AI 해소는 이제 이력을 남기고, 옛 행 필드 `resolution_evidence`·`resolution_reason`은 이력의 `evidence`로 옮겼다. 제출 검사(`validate_extensions`)와 적용은 `resolution_error`를 함께 쓴다. `question_engine`의 스키마 중복 재검사(기준 81-82행)는 지웠다. 대체값 읽기 여섯 곳은 `open_targets`를 쓴다. 구판 호환 대체값은 두지 않았다. 대신 스키마가 `unresolved_target_ids`를 필수로 요구한다(`record_schemas/domains.py`). "열린 사용자 질문" 술어의 사본 두 곳(`revisions.py`의 `record_repetition`, `continue_repetition`)은 `open_links(runtime, 'user')`를 쓴다. |
| RES-06 | 구현함 | `planning.revision_required(task)`(`:30`)를 두었고, `revisions.submission_errors`와 `revision_engine._bind_revision_action`이 부른다. 저장 모양 통일도 채택했다. `engine.py:4043`의 계약 검토 반려는 이제 `{revision, source, reason}`을 쓴다. 이 모양은 `governance`와 `revision_engine`이 쓰는 것과 같다. 그래서 반려 뒤 `task_ready`의 개정 요청 관문이 이 요청을 본다. 상태(`not_ready`)와 대기 목록은 같고, 오류 문구가 "a contract revision was requested by …"로 바뀐다. `item_reviews`를 읽는 소비자는 없었다. 같은 항목은 `task["reviews"]`에 남는다. |
| RES-07 | 구현함 | `revisions.regeneration_time_valid(regenerate_after, observed_at)`(`:9`)를 두었고, 세 곳이 부른다. `submission.py`의 제출 검사, `record_repetition`의 기록 시 예외, `record_execution_outcome`의 수신 후 버림이다. 파서는 커널의 `file_io.parse_utc`를 쓴다. |
| RES-08 | 구현하지 않음(이미 커널이 구현) | K-제품이 `planning._utc`, `delegations._now`, `external._now`를 지우고 `file_io.parse_utc`로 옮겼다(`결과-K제품.md` RES-08 행). 현재 원문 `planning.py:9`, `delegations.py:5`, `external.py:10`이 `parse_utc`를 import하며, 그룹 D 모듈에 `fromisoformat`이나 `_utc`·`_now` 정의가 남아 있지 않다. |
| RES-09 | 구현함 | 참조 필드 정본 표는 `planning.READ_REFERENCE_FIELDS`(엄격·완화 구분, `:63`)와 `READ_REFERENCE_ID_FIELDS`(`:65`)다. `action_read_ids`는 이 표로 시드를 넓힌다. `knowledge._STRICT_REFERENCE_KEYS`·`_REFERENCE_KEYS`(`knowledge.py:115-120`)와 `_impact_refs`의 ID 필드는 같은 표에서 만든다. 그 결과 영향 폐포가 `basis_refs`·`authority_refs`·`profile_refs`로 가리킨 기록을 포함한다(결정 1.5). 세 필드는 완화 필드다. 영향 모집단에 있는 기록 ID만 참조로 세고, 모집단 밖의 grant·프로필 ID는 미해결 참조로 세지 않는다. 읽기 폐포 쪽은 동작이 그대로다. `source_ref`는 읽기 폐포만 따라가는 출처 참조로 남겼다(5절 3). `integration.REFERENCE_KEYS`는 조사 판정대로 합치지 않았다. |
| RES-10 | 구현함 | `validate_relation`은 술어를 만족하는 판정 집합 `establishing`(판정 ID → 형식 결과 ID)을 한 번 계산하고, 두 사유 목록을 이 집합에서 만든다(`knowledge_io.py:351`). 값싼 관계 주장 비교를 `assess_use` 앞에 두어 `assessment_current` 호출을 줄였다. |
| RES-11 | 구현함 | `knowledge_io.candidate_shape_errors(candidate)`(`:209`)는 순수 함수다. 검사하는 것은 본문 필드, `declaration_names`의 구별과 Lean 식별자 문법, `dependencies`의 구별, Lean 원문이 있을 때 선언명 필수다. 제출 검사(`submission.py`의 `output/knowledge` 검사, 생산자 로컬 검사와 중앙 수신이 같은 코드)와 `import_candidate`가 함께 부른다. 선언명 문법 함수는 `formal._ident`를 공개 이름 `formal.is_lean_identifier`(`formal.py:182`)로 바꿨다. `import_candidate`는 재사용 형식 결과로 원문·선언명을 채운 뒤 이 검사를 한다. 이 순서는 원문을 반복하고 선언명을 생략한 재사용 후보가 지금처럼 수락되게 하기 위해서다. 새 제목과 ID로 의존을 가리키는 방식의 차이와 존재 검사는 각 호출자에 남겼다. |
| RES-12 | 구현함 | `create_candidate`는 ID 검사와 인스턴스 사본을 빼고 호출자의 사본에 쓴다(`knowledge_records.py:52`). 유일한 생산 호출자인 `import_candidate`가 검사를 소유한다. `import_candidate`의 `_definition_for`는 한 번만 부른다. `integration.apply_reviewed_knowledge_changes`의 좌표 수 재검사와 교체 ID 구별·존재 재검사는 지우고, 이유를 주석으로 남겼다(`integration.py:238-239`). 좌표 수는 `_reviewed_impact_request`가 다시 부르는 `bundle_impact_request`가 대조하고, 교체 ID는 `import_candidate`가 같은 조건으로 거부한다. |
| RES-13 | 구현함 | 대기 항목의 `delegated_to_task_id` 저장을 없앴다. `pending_revisions`가 `delegated_targets`의 첫 값으로 계산하므로(`planning.py:121-126`) 역할 입력의 같은 이름 필드는 그대로다. 대기 항목의 `revision_targets` 사본도 없애고 `entry["action"]["revision_targets"]` 하나만 둔다. 쓰는 곳은 `revision_engine`, 읽는 곳은 `planning`·`revision_engine`·`reporting`이다. 스키마에서 두 필드를 뺐고, 참조 검사는 `delegated_targets`의 모든 과제 ID가 과제를 가리키는지로 바꿨다(`record_schemas/__init__.py`). |
| RES-14 | 구현함 | 다섯 가지를 지웠다. `planning.task_reference_changes`, `academic.requirements_changed`, `academic_engine.current_solution_basis`의 덮어써지는 `records` 계산, `questions.sync_activity_wait`와 그 `user_questions` 대기 조건, `activities.requeue_recovered_execution`이다. 뒤의 둘은 결정 6이다. 이들만 검사하던 시험도 지웠다(4절). |
| RES-15 | 구현함 | `delegations._check_judgment(runtime, record, execution_id, output, author_ids)`(`:110`)는 기록 때와 사용 때가 공유하는 판정 유효 조건이다. 실행 역할, 입력 해시 결속, 저자 독립, 출력의 `input_sha256`을 확인한다. `record_judgment`는 여기에 판정값·사유 검사를 더하고, `_checked`는 봉인 해시와 `within_scope`를 더한다. 디스크 왕복 뒤의 재검사는 유지했다. |
| RES-16 | 구현함 | `validate_operation`은 `request_binding_current`를 부른다. 재시도 증거 결속은 `external._retry_evidence_bound(operation, evidence)`(`:19`) 하나로 두고, `execute_operation`과 `prepare_retry`가 부른다. 전송 직전 권한 재검사는 유지했다. |
| RES-17 | 구현함 | `integration.derived_bundles(output, extensions, context)`(`:327`)는 protocol 출력과 구성원 값을 한 번에 만든다. `apply_bundles`는 이를 한 번 계산해 `inspect_bundles(..., derived=)`와 `split_bundles(..., derived=)`에 넘긴다. 응답 해시는 미리 계산한 `members["output"]`로 만든다. 두 함수의 `derived` 인자는 선택이다. 인자가 없는 기존 호출(submission 미리보기, 시험)은 지금처럼 동작한다. |
| ENG-24 | 구현하지 않음(동등하지 않음) | 투영(`initialization.governance_working_view`, `initialization.py:93-96`, `{**instance, **governance_view(instance)}`)과 원 인스턴스는 `task_ready` 판정이 같지 않다. 근거는 5절 2에 적었다. 설계 4.5절에 따라 호출을 통일하지 않았고, 메모이즈도 하지 않았다. |

## 2. 필요했지만 커널에 없던 공유 정의

설계 3.2절 정정에 따라, 개념을 소유한 그룹 D 모듈에 하나씩 만들었다. 아래 표에서 "다른 그룹 사용처"가 있는 정의가 그룹 사이의 이음새다. 통합자가 이음새 계약에 옮길지 판단한다.

| 정의 | 위치 | 규칙 | 다른 그룹 사용처 |
|---|---|---|---|
| `record_index(instance, runtime, *, families, source_aliases, question_links)` | `do_math/planning.py:382` | ID → (가족, 기록) 색인. `RECORD_FAMILIES`가 모집단이고, 중복 ID는 `ValueError`다 | engine, governance, scheduler, task_scope, integration |
| `READ_REFERENCE_FIELDS`, `READ_REFERENCE_ID_FIELDS` | `do_math/planning.py:63-66` | 기록 참조 필드 정본(엄격·완화 구분) | 없음(knowledge가 소비) |
| `revision_required(task)` | `do_math/planning.py:30` | 개정 필수 판정 | 없음 |
| `premise_failures`, `record_premises_current` | `do_math/knowledge_records.py:134`, `:146` | 지식 기록의 전제 현재성 | 없음 |
| `FORMAL_EVIDENCE_FIELDS`, `lean_source_sha256`, `forbidden_axioms`, `is_lean_identifier` | `do_math/formal.py:141-189` | 형식 증거 필드, 원문 해시, 금지 공리, 선언명 문법 | 없음(`record_schemas`·`state_checks`는 `validate_formal_evidence`를 거쳐 씀) |
| `candidate_shape_errors(candidate)` | `do_math/knowledge_io.py:209` | 지식 후보의 형태 | submission(그룹 C) |
| `open_targets`, `close`, `resolution_error` | `do_math/questions.py:11`, `:52`, `:67` | 질문의 미해결 대상, 해소 전이, AI 해소 허용 | engine, governance, record_schemas |
| `regeneration_time_valid` | `do_math/revisions.py:9` | 재생성 시각은 관찰 시각보다 뒤 | submission(그룹 C) |
| `derived_bundles` | `do_math/integration.py:327` | 묶음 파생 계산 한 번 | 없음 |
| `evidence_record`, `EVIDENCE_FAMILIES` | `do_math/academic.py:155-172` | 학술 증거 해석 | 없음 |

## 3. 필요한 문서 변경

- `계약/연구-수행.md` 92행: 선언명 검사를 사전 검사만의 일로 서술한다. 이제 제출 검사(생산자 로컬 검사와 중앙 수신)도 같은 선언명 문법(`formal.is_lean_identifier`)을 확인한다. 맞지 않는 이름은 형식 검사를 기다리지 않고 제출 단계에서 반환된다는 문장을 더한다(RES-11).
- `references/CLI-실행-계약.md` 463행: 지식 후보 가져오기 규칙에 선언명 문법 검사를 더한다(RES-11).
- `references/CLI-실행-계약.md` 814행 부근과 `계약/유지보수.md` 76행: "계산된 영향(의존)"의 뜻을 적는 곳이다. 계산된 영향이 따라가는 참조 필드를 적거나 정본을 가리킨다. 필드는 `inputs`, `reuse`, `dependencies`, `basis_refs`, `authority_refs`, `profile_refs`와 증거·출처 필드다. 결과적으로 개정·철회가 `basis_refs`로 그 기록을 인용한 과제까지 다시 판단 대상으로 만든다는 점을 밝힌다(RES-09, 결정 1.5).
- `references/공통-실행.md` 228행, 306행: `impact_set` 선언은 계산된 영향과 대조된다. 과제가 `basis_refs`로 인용한 지식을 개정하면 그 과제도 계산된 영향에 들어간다. 생산자가 이를 선언하지 않으면 지정 독립 검토가 요구된다는 점을 더한다(RES-09).
- 질문 해소 이력의 모양(`{kind, resolution_ref, affected_ids, evidence}`)과 AI 해소가 이력을 남긴다는 점을 서술하는 문서는 찾지 못했다. 문서 단계에서 GLOSSARY나 CLI 계약의 질문 절이 이력 필드를 다룬다면 새 모양으로 맞춘다(RES-05).
- `docs/do-math/검사-경량화-이음새-계약.md`: 2절 표의 행 가운데 다른 그룹이 부르는 것을 이음새로 옮길지 통합자가 판단한다. 대상은 `record_index`, `questions.open_targets`/`close`, `candidate_shape_errors`, `regeneration_time_valid`다.

## 4. 고친 시험 파일과 확인하지 못한 위험

### 고친 시험 파일

- `test_planning.py`: 지운 `task_reference_changes`만 검사하던 시험을 지웠다. 색인 호출 횟수 시험의 patch 대상을 `record_index`로 바꿨다.
- `test_academic.py`: `requirements_changed`의 import와 단언을 지웠다.
- `test_redesign_ACTIVITIES.py`: `requeue_recovered_execution`만 검사하던 시험 셋을 지웠다. `test_pause_and_queued_recovery_…`, `test_queued_recovery_does_not_discard_…`, `test_05_queued_recovery_…`다. `bind_action` 단언은 남은 `test_06_…`이 덮는다.
- `test_redesign_GOVERNANCE.py`: `sync_activity_wait` 시험을 지웠다.
- `test_redesign_EVIDENCE_walkthroughs.py`: w05에서 활동 대기 동기화 줄과 활동 상태 단언을 뺐다. 대기 과제의 의무 보존, 독립 과제의 착수, 질문 해소 뒤 재개 단언은 남겼다. 쓰이지 않게 된 `activities` import도 지웠다.
- `test_formal.py`: `_ident`를 `is_lean_identifier`로 바꿨다.
- `test_redesign_STORAGE.py`, `test_redesign_TASKS.py`, `test_static_review_repairs.py`: 손으로 만든 질문 행에 필수 필드가 된 `unresolved_target_ids`를 더했다. 대상 변경 시험은 `target_ids`와 `unresolved_target_ids`를 함께 바꾼다.
- `test_revision_obligations.py`: 대기 항목의 `revision_targets`를 `entry['action']`에서 읽는다.
- `test_impact_bundle.py`: 중복 교체 ID의 거부 문구 단언을 "globally distinct"에서 "already exists"로 바꿨다. 지금은 `import_candidate`가 거부한다.
- `test_walkthrough_repairs.py`, `test_contract_checks.py`: `revision_requested` 픽스처를 통일한 모양 `{revision, source, reason}`으로 바꿨다.

### 실행하지 않아 확인하지 못한 위험

- **RES-09의 영향 확대.** `knowledge._explicit_refs`는 중첩 구조를 재귀로 읽는다. 그래서 완화 필드가 된 `basis_refs`·`authority_refs`가 실행·활동 기록 안의 중첩 값(예: 저장된 확장의 과제 후보)에 있어도 참조로 센다. 영향 받은 과제를 그렇게 가리키는 실행이 계산된 영향에 들면 생산자의 `impact_set` 선언과 어긋날 수 있다. 그러면 지정 독립 검토가 이전보다 자주 요구된다. 이 동작은 `inputs`·`reuse`에 이미 적용되던 재귀 규칙을 결정대로 세 필드에 넓힌 결과다. 영향 시험(`test_knowledge`, `test_impact_bundle`, `test_redesign_KNOWLEDGE`, 엔진 흐름 시험)의 픽스처는 `basis_refs`·`authority_refs`를 비워 두거나 모집단 밖 ID(`context:goal`, grant)만 쓴다. 그래서 단언이 바뀌지 않는다고 판단했지만 실행으로 확인하지 않았다.
- **RES-05 스키마.** `unresolved_target_ids`를 필수로 바꿨다. 질문 행을 손으로 만드는 시험은 grep으로 찾아 고쳤다. 그러나 픽스처 함수가 간접으로 만드는 행이 있으면 스키마 오류가 날 수 있다.
- **RES-01 중복 ID.** `knowledge._find`는 중복 ID에서 첫 기록을 돌려주었지만, 이제 색인이 `ValueError`를 낸다. `validate_basis`를 부르는 `usable_links` 경로가 중복 상태에서 예외를 낼 수 있다. 저장 계약(`state_contract.py:173-181`)이 전역 유일성을 강제하므로 적재된 상태에서는 일어나지 않는다.
- **RES-07 submission.** `context['observed_at']`이 `None`인 문맥이면 결과가 달라진다. 옛 `governance.timestamp(None)`은 현재 시각으로 비교했지만, 새 함수는 해석 오류로 제출 이슈를 낸다. 엔진은 관찰 시각을 늘 채우지만 생산자 로컬 검사 문맥은 확인하지 않았다.
- **RES-02 공유 색인.** `task_ready`는 상태를 쓰지 않으므로 한 호출 안의 공유는 안전하다. 다만 `authorize`·`assessment_current` 같은 하위 호출은 자기 조회를 따로 하므로, 공유 색인이 그 조회를 대신하지는 않는다.
- **import 순환.** `knowledge`·`knowledge_records`·`knowledge_io`가 `planning`을, `knowledge_records`·`knowledge_io`가 `formal`을 모듈 최상위에서 import한다. 설계가 문법 확인만 허용하므로 import를 실행하지 않았다. 대신 최상위 import를 따라가 확인했다. `planning`의 최상위 import는 `file_io`·`repository`뿐이고, 그 사슬(`events`, `git_store`, `state_contract`, `operation_trace`)과 `formal`의 사슬(`trust_validation`, `file_io`, `windows_job`)은 지식 모듈을 import하지 않는다. 따라서 순환은 없다고 판단한다. 통합 단계의 전 모듈 import 검사로 확인이 필요하다.
- **문구만 바뀐 오류.** 조사의 grep이 놓친 단언을 문구 조각으로 다시 찾았다. 찾은 것은 `test_impact_bundle`의 "globally distinct" 하나였고, 고쳤다. 다른 문구 변경을 단언하는 시험은 찾지 못했다. 바뀐 문구의 출처는 활성화 전이, 질문 해소, 위임 판정, 외부 요청 결속, 지식 후보 형태, `validate_extensions`다. `validate_extensions`는 한 해소 행에 두 오류를 내던 경우 이제 하나만 낸다.

## 5. 전제가 틀렸거나 계획을 바꾼 지점

1. **RES-01 `engine._records`.** 조사는 이 함수를 "조회 CLI용 목록"으로 보고 "색인에 가족 표지를 붙이는 표현 함수로 줄인다"고 제안했다. 원문은 그렇지 않았다. 조회 CLI(`query_records`, 기준 `engine.py:468-486`)는 `store.load_records`와 `_query_record`를 쓰고 이 함수를 부르지 않는다. 유일한 호출자는 `_validate_bundle_candidate`의 게시 전 ID 충돌 검사였고, 반환 목록은 버려졌다. 그 충돌 검사는 바로 뒤의 `store.validate_candidate`가 저장 계약으로 다시 한다. 저장 계약은 등록 가족 전부의 전역 유일성을 강제한다(`state_contract.py:173-181`, `identity=True` 기본). 그래서 목록 함수를 지우고 호출부가 정본 색인 `planning.record_index`를 부르게 했다. 이것이 정본 하나라는 같은 결과를 내는 현재 원문의 방법이다. `question_links`·`integrations` 같은 색인 밖 가족의 충돌은 저장 계약 검사가 계속 잡는다.
2. **ENG-24 동등성.** 코드 독해로 판단했다. 차이는 두 가지다.
   - `EXPOSED_FIELDS['instance']`(`planning.py:376`)는 `/goal_revision`과 `/policy_revision`을 노출한다. 원 인스턴스에는 이 최상위 키가 없다. `governance.validate_governance_state`가 병렬 권한 필드로 금지하기 때문이다(`governance.py:163-164`). 그래서 `record_field_equals` 조건이 인스턴스 가족의 이 포인터를 읽으면 원 인스턴스에서는 `_pointer`가 `KeyError`를 낸다(`planning.py:443`). 결과는 `evaluation_error`다. 투영에서는 값이 있어 `ready` 또는 `not_ready`가 된다.
   - 과제의 읽기 폐포에 인스턴스 ID가 들면 `capture_task_basis`는 인스턴스 dict 전체를 해시한다(`planning.py:229-237`). 조건 대상 ID는 `condition_refs`(`planning.py:101`)로 이 폐포에 들어간다. 투영은 키가 더 많으므로 해시가 다르다. 계약 검토의 `task_basis`를 봉인하는 곳은 원 인스턴스(`engine.py:4036`)와 투영(`lifecycle_engine.py:981`)으로 갈린다. 따라서 `contract_review_current`의 판정도 입력에 따라 달라진다.

   이 차이 때문에 `scheduler.py:493`(투영)과 `engine.py:975`, `:1795`, `:3227`, `decision_engine.py:69`, `:127`, `:148`, `revision_engine.py:69`(원 인스턴스)를 통일하지 않았다. 어느 쪽이 맞는 입력인지는 설계 판단이 필요하다. 인스턴스 가족 조건이 투영에서만 뜻을 가지므로, 통일한다면 투영 쪽이 후보다.
3. **RES-09 `source_ref`.** 읽기 폐포는 `source_ref`를 따라가지만 영향 폐포는 따라가지 않았다. 결정 1.5가 영향 폐포에 더하라고 정한 필드는 `basis_refs`·`authority_refs`·`profile_refs` 셋이다. 그래서 `source_ref`는 정본 표 밖에 두고 `action_read_ids`의 출처 추적으로 남겼다. 결정 밖의 동작 변경을 피하기 위해서다.
4. **RES-01 `academic.evidence_record`.** 조사는 "같은 색인에 가족 필터를 적용해 만든다"고 제안했다. 그러나 이 함수는 증거 참조마다 불린다(`academic.py:191`, `:212`의 기록×참조 루프). 호출마다 색인을 만들면 O(1) 조회가 O(N)이 된다. 그래서 모집단 정의만 정본 `RECORD_FAMILIES`의 `EVIDENCE_FAMILIES` 다섯 가족에서 가져오고, 조회는 가족별 dict 조회로 했다. 모집단이 한 정의라는 결과는 같다.
5. **RES-11 검사 순서.** 조사 제안대로 검사를 `import_candidate` 입구에 두면 동작이 바뀐다. 재사용 형식 결과를 가리키며 원문만 반복하고 선언명을 비운 후보가 지금은 수락되는데, 이것이 거부된다. 그래서 재사용 채움 뒤에 공유 형태 검사를 둔다. 비정상 입력(문자열 아닌 원문 등)의 오류 문구 순서는 바뀐다.
6. **RES-01 `state_checks.py:236-249`.** 조사가 위치로 든 전 가족 ID 중복 검사는 제안의 변경 목록에 없다. 이 검사는 모든 저장 가족(색인 밖 포함)을 도는 `check` 명령의 저장 점검이라 색인과 모집단이 다르므로 두었다.
7. **RES-17 submission 미리보기.** `submission.py:936-943`에도 같은 반복 파생이 있다. 조사 제안의 범위는 `apply_bundles`였고 이 모듈은 그룹 C 소유다. 그래서 선택 인자만 열어 두고 호출부는 바꾸지 않았다. 필요하면 `derived_bundles`를 한 번 계산해 넘기는 두 줄로 옮길 수 있다.
8. **다른 그룹 모듈의 변경.** 호출부를 새 이름으로 바꾸거나 저장 모양 변경에 따른 스키마를 맞추는 최소 변경만 했다. 통합자가 겹침을 정리할 좌표는 다음과 같다.
   - engine(`_records` 삭제와 `:2207` 호출, `:1858` 색인 이름, `:2765` 입력 초과 질문 닫기, `:4043` 반려 모양)
   - governance(`record_index` 4곳, `_import_basis`의 색인 선택 인자, `open_targets` 1곳)
   - scheduler·task_scope(색인 이름)
   - submission(`regeneration_time_valid`, `candidate_shape_errors`)
   - reporting(대기 항목의 `revision_targets`)
   - record_schemas(`question_links` 필수 필드·옛 필드 삭제, `waiting_actions`의 두 필드 삭제와 `delegated_targets` 참조 검사, `open_targets`)

## 이음새 요청

- `planning.record_index`는 그룹 B의 `state_checks`·`retention` 참조 수집, 그룹 C의 `task_scope`·`submission` 참조 해석과 모집단을 공유할 수 있다. 이음새 계약에 "기록 ID 색인의 정본"으로 올릴지 통합자가 판단한다.
- 원자료 별칭 조회의 사본 셋은 그룹 D 밖에 남아 있다(`scheduler.py`의 `_rule_deferral_inputs`, `task_scope.py:163`·`:270`, `review_engine.py:1083`). `scheduler`는 별칭이면 기록 해시가 아니라 원자료 `sha256`을 쓰므로 뜻이 다르다. 나머지를 `record_index(..., families=(), source_aliases=True)`로 옮길지는 소유 그룹이 판단한다.

## 추가한 이름

- 공개 함수·상수: 2절 표의 정의 전부, `knowledge.BASIS_FAMILIES`, `knowledge_records.RESEARCH_RECORD_FAMILIES`
- 내부 함수: `planning._shared_index`, `knowledge._basis_records`, `delegations._check_judgment`, `external._retry_evidence_bound`
- 이름 변경: `planning._records` → `record_index`, `academic._evidence` → `evidence_record`, `formal._ident` → `is_lean_identifier`
- 새 키워드 인자: `action_read_ids`·`revision_waits`·`capture_task_basis`·`evaluate_condition`·`task_ready`·`questions.user_waits`의 `records=`, `inspect_bundles`·`split_bundles`의 `derived=`
- 바뀐 저장 값
  - 질문 행: `unresolved_target_ids` 필수, `resolution_history` 항목 모양 `{kind, resolution_ref, affected_ids[, evidence]}`, `resolution_evidence`·`resolution_reason` 삭제
  - 대기 항목: `revision_targets`·`delegated_to_task_id` 삭제
  - 과제: 계약 검토 반려의 `revision_requested` 모양 `{revision, source, reason}`
- 설정 키, 사건 종류, CLI 인자는 추가하지 않았다.
