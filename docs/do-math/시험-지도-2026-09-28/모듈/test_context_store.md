# test_context_store

| 항목 | 값 |
|---|---|
| 조각 | `foundation` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_context_store.py` (599행) |
| 클래스 / 테스트 | 3 / 35 |
| 시험 대상 제품 코드 | `do_math/context_store.py`의 `read_stable`, `stat_fingerprint`(가져온 이름), `_ChangedDuringRead`, `PhysicalBoundary.check`(가져온 이름), `collect_outputs`, `fit_context`, `read_source`, `write_source_catalog`, `materialize_inputs`, `build_role_manifest`, `prepare_role_input`, `validate_role_manifest`, `verify_manifest_artifacts`, `restore_continuation`, `defer_input_overflow`; `do_math/engine.py`의 `ResearchEngine._context`, `_prepare_review_context`; 단언과 준비에 쓰는 `planning.validate_plan_submission`, `submission.contract_check_errors`·`supplied_reference_ids`, `execution_profiles.boundary_prompt`·`seal_profile`·`prepare_prompt`·`build_profiles`, `contracts.schema_for`·`render_prompt`, `knowledge_records.create_candidate`·`set_assessment_use`, `review_cycle.start_review`·`next_actions`·`context_for`, `execution_lifecycle.transition_execution` |
| 사용하는 픽스처 모듈 | `record_fixtures`: `surface_state`, `task_contract`, `task_disposition`, `contract_check`; `research_fixtures`: `governance_start`, `assessment`, `candidate`, `new_instance`; `engine_fixtures`: `context_engine`; `knowledge_fixtures`: `verified_knowledge`; `review_fixtures`: `ReviewFakeEngine` |
| 격리 표지 | 없음. `test_outside_symlink_is_reported_when_supported`는 `os.symlink`가 있을 때만 돌고, 링크 생성이 `OSError`면 건너뛴다 |
| 시작 상태 | 대부분 1단. 임시 작업 공간과 사전 상태(`surface_state` 등)를 문맥 저장 함수에 직접 준다. `context_engine`(엔진 대역)으로 실제 문맥 생산자를 부르는 것 2개, `ReviewFakeEngine`(검토 엔진 대역) 1개가 있다. `test_engine_context_restores_multihop_git_artifact`는 `new_instance`로 공개 `initialize`를 실제로 돈다(4단의 공개 초기화 + 저장소 직접 발행) |

## 목적

모듈 docstring은 없다. 제품 `context_store.py`의 docstring은 "무손실 입력 카탈로그, 크기가 제한된 프롬프트 문맥, 작업 공간 수집"이다. 이 모듈은 AI 역할 실행에 넘길 입력을 준비하고, 실행이 남긴 작업 공간을 거두는 계층을 검사한다. 세 클래스는 층을 나눈다.

- `StableReadTests`: 파일 하나를 한 판본으로 읽는 규칙(`read_stable`)과 물리 경계 확인의 횟수.
- `ContextStoreTests`: 작업 공간 수집(`collect_outputs`), 입력 물질화(`materialize_inputs`), 원천 카탈로그(`write_source_catalog`), 원천 읽기(`read_source`), 크기 맞춤(`fit_context`)의 저수준 계약. 핵심은 무손실이다. 크기 한도 때문에 줄인 값도 카탈로그에서 정확히 되살아나야 하고, 읽지 못한 파일은 사라지지 않고 누락(omission)으로 보고되어야 한다.
- `RoleInputTests`: 역할별 입력 포장(`prepare_role_input`)의 계약. 직접 입력(direct)과 참조(reference)의 구분, 필수 직접 입력의 보존, 제출 검사용 정본 문맥(`input/submission/context.json`), 후보 순서의 봉인과 재현, 연속(continuation) 실행의 이전 산출물 복원, 검토 좌석 범위, 입력 넘침(overflow)의 기록과 대기.

## 모듈 수준 요소

- `SCRIPTS` (행 7): 스킬의 `scripts/` 폴더. 같은 행에서 존재 확인 없이 `sys.path` 맨 앞에 넣는다.
- 행 8: `do_math.context_store`를 `store`라는 이름으로 import한다. `StableReadTests`와 `ContextStoreTests`는 제품 함수를 `store.<이름>`으로 부르고 `patch.object(store, ...)`로 바꾼다.
- 행 599: 직접 실행하면 `unittest.main(verbosity=2)`로 이 모듈의 시험을 돈다.

## StableReadTests (행 13–28)

`unittest.TestCase`를 그대로 상속한다. 표지, 속성, 훅, 도우미가 없다.

### `test_metadata_change_during_one_read_is_not_one_version` (행 14–19)
- 성질: 한 번의 읽기 동안 파일 메타데이터가 바뀌면 그 읽기는 한 판본의 바이트로 인정되지 않는다.
- 준비: 임시 폴더의 파일 `x`(`b'bytes'`).
- 실행: `store.read_stable(path)`를 그대로 한 번 부른다. 이어서 `store.stat_fingerprint`가 `(5,1,1)`과 `(5,2,1)`을 차례로 돌려주게 하고 다시 부른다.
- 단언: 첫 읽기는 `b'bytes'`다. 둘째 읽기는 `store._ChangedDuringRead`를 던진다(유형만 본다).
- 대역: `patch.object(store, 'stat_fingerprint', side_effect=[...])`. 읽기 앞뒤의 지문이 다르게 보이도록 한다.

### `test_one_boundary_proves_its_root_once_for_many_reads` (행 21–28)
- 성질: 작업 공간 수집은 물리 경계를 한 번만 증명하고 여러 파일을 읽는다.
- 준비: 임시 폴더의 `sub/0.txt`, `sub/1.txt`, `sub/2.txt`.
- 실행: `PhysicalBoundary.check`를 `autospec=True, wraps=...`로 감싼 채 `store.collect_outputs(root)`.
- 단언: 거둔 파일이 3개이고, 경계 확인이 1회다.
- 대역: `patch.object(store.PhysicalBoundary, 'check', ...)` 감싸기.

## ContextStoreTests (행 31–136)

`unittest.TestCase`를 그대로 상속한다. 표지, 속성, 훅, 도우미가 없다.

### `test_directory_read_failure_is_an_omission_even_without_required_paths` (행 32–51)
- 성질: 디렉터리를 읽지 못하면, 필수 경로가 없어도 그 디렉터리가 누락으로 보고되고 수집은 불완전하다. 읽을 수 있는 이웃 파일은 보존된다.
- 준비: `subTest(required=...)`로 두 경우를 나눈다. 필수 경로가 없는 경우와 `['blocked/proof.txt']`인 경우다. 각 경우 새 임시 폴더에 `blocked` 폴더와 `visible.txt`(`b'preserved sibling'`)를 만든다. `store.os.walk`를 바꿔, 루트 항목 하나를 내놓은 뒤 `onerror`에 `PermissionError(13, 'Permission denied', blocked)`를 넘기게 한다.
- 실행: `store.collect_outputs(root, required_paths=required)`.
- 단언: `files`가 `{'visible.txt': b'preserved sibling'}`이다. `complete`가 거짓이다. 경로 `blocked`의 누락 행은 `reason='read_error'`, `error_type='PermissionError'`, `required`가 필수 경로 유무와 같은 값, `error`에 `'Permission denied'`를 가진다.
- 대역: `patch.object(store.os, 'walk', side_effect=walk)`.

### `test_large_ongoing_preparation_is_recoverable_without_prompt_overflow` (행 52–58)
- 성질: 진행 중인 준비 목록이 커도 프롬프트 넘침 없이 참조로 옮겨지고 원래 값으로 되살아난다.
- 준비: 임시 작업 공간. `ongoing_preparation` 항목 하나(`reason`이 `'assigned obligation '`의 1000회 반복).
- 실행: `store.fit_context({'goal': 'g', 'ongoing_preparation': entries}, max_bytes=1200, workspace=root, mandatory_keys=['goal'])`, 이어서 `read_source`로 그 참조를 읽는다.
- 단언: `overflow`가 `None`이다. 문맥의 `ongoing_preparation`이 `source_ref`를 가진 참조로 바뀌었고, 그 원천을 풀면 원래 목록과 같다.
- 대역: 없음.

### `test_new_catalog_is_hashed_from_the_bytes_it_wrote` (행 59–73)
- 성질: 새 카탈로그 파일의 해시는 방금 쓴 바이트로 계산하고 다시 읽지 않는다. 이미 있는 카탈로그 파일은 재사용 전에 비교한다.
- 준비: 문맥 `{'goal': 'g', 'tasks': [{'id': 'T-1'}]}`.
- 실행: `store.read_stable`이 불리면 실패하게 한 채 `store.write_source_catalog(context, root)`. 이어서 `input/catalog/goal.json`을 `b'"other"'`로 덮고 다시 부른다.
- 단언: 키마다 `catalog['files']['input/catalog/<키>.json']`이 `canonical_json(value)`와 같다. `entries[<키>].sha256`이 그 바이트의 SHA-256이다. 디스크의 파일 바이트도 같다. 덮어쓴 뒤의 호출은 `FileExistsError`를 던진다.
- 대역: `patch.object(store, 'read_stable', side_effect=AssertionError('a new catalog file is never reread'))`.
- 비고: 행 71의 주석은 "이미 있는 카탈로그 파일은 재사용 전에 여전히 비교한다"고 밝힌다.

### `test_materialize_and_invalid_utf8_round_trip` (행 74–78)
- 성질: 물질화한 입력은 유효하지 않은 UTF-8 바이트도 그대로 쓰이고, 바이트 형식으로 다시 읽힌다.
- 준비: `b'\xff\x00abc'`.
- 실행: `store.materialize_inputs(root, {'sources/raw.bin': data})`, 그 목록의 첫 참조에 `format='bytes'`를 더해 `read_source(root, ref, limit=99)`.
- 단언: 디스크 파일이 같은 바이트다. 읽기 결과가 `status='ok'`이고 바이트가 같으며 `truncated`가 거짓이다.
- 대역: 없음.

### `test_traversal_and_absolute_paths_rejected` (행 79–82)
- 성질: 물질화는 상위 탈출, 절대 경로, 드라이브 경로, 역슬래시 경로를 거부한다.
- 준비: 이름 네 개. `'../x'`, `'/absolute'`, `'C:/absolute'`, `'a\\b'`다.
- 실행: 이름마다 `store.materialize_inputs(Path(d), {name: b'x'})`.
- 단언: 모두 `ValueError`를 던진다(유형만 본다).
- 대역: 없음.

### `test_collect_preserves_outputs_and_excludes_noise` (행 83–87)
- 성질: 작업 공간 수집은 산출물을 보존하고, 입력 폴더와 `.git`, `__pycache__` 같은 잡음을 뺀다.
- 준비: `input/x`, `.git/x`, `__pycache__/x`, `src/main.lean`, `checkpoint.bin`(`b'\xffcp'`)을 만든다.
- 실행: `store.collect_outputs(root, required_paths=['src/main.lean', 'checkpoint.bin'])`.
- 단언: `complete`가 참이다. `checkpoint.bin`의 바이트가 그대로다. 거둔 파일 이름 집합이 `{'src/main.lean', 'checkpoint.bin'}`이다.
- 대역: 없음.

### `test_required_missing_and_limit_are_incomplete` (행 88–91)
- 성질: 필수 경로가 없거나 크기 한도를 넘으면 수집은 불완전하고, 두 사유가 따로 보고된다.
- 준비: 20바이트 파일 `large`.
- 실행: `store.collect_outputs(root, required_paths=['missing', 'large'], max_bytes=5)`.
- 단언: `complete`가 거짓이고, 누락 사유 집합이 `{'required_missing', 'max_bytes_exceeded'}`다.
- 대역: 없음.

### `test_invalid_empty_capture_does_not_disappear` (행 92–95)
- 성질: 잘못된 모양의 포착 목록(빈 리스트)은 조용히 무시되지 않고 거부된다.
- 준비: 빈 임시 폴더.
- 실행: `store.collect_outputs(Path(d), captured_files=[])`.
- 단언: `TypeError`를 정규식 `'captured_files must be'`로 던진다.
- 대역: 없음.

### `test_changed_during_read_is_not_success` (행 96–101)
- 성질: 읽는 동안 바뀐 파일은 성공으로 수집되지 않는다.
- 준비: 파일 `x`.
- 실행: `store.read_stable`이 `store._ChangedDuringRead('moving')`을 던지게 한 채 `collect_outputs(root, required_paths=['x'])`.
- 단언: `complete`가 거짓이고, 첫 누락 행의 `reason`이 `'changed_during_read'`다.
- 대역: `patch.object(store, 'read_stable', side_effect=...)`.

### `test_outside_symlink_is_reported_when_supported` (행 103–108)
- 성질: 작업 공간 밖을 가리키는 심볼릭 링크는 따라가지 않고 누락으로 보고된다.
- 준비: 임시 폴더 둘. 바깥 폴더에 `secret` 파일을 만들고, 작업 공간의 `link`를 그것으로 잇는다.
- 실행: `store.collect_outputs(root, required_paths=['link'])`.
- 단언: `complete`가 거짓이고, 첫 누락 행의 `reason`이 `'outside_symlink'`다.
- 대역: 없음.
- 비고: `@unittest.skipUnless(hasattr(os, 'symlink'), 'symlink unavailable')`. Windows에서 심볼릭 링크 권한이 없어 `symlink_to`가 `OSError`를 내면 `skipTest(str(error))`로 건너뛴다. 곧 권한 없는 Windows에서는 실제로 검사되지 않는다.

### `test_catalog_and_overflow_history_preserve_exact_values` (행 109–114)
- 성질: 크기 맞춤으로 줄인 과제 목록과 최근 이력은 카탈로그에서 원래 값 그대로 되살아난다.
- 준비: 아직 없는 작업 공간 `new-workspace`. 문맥에는 목표, 행동(`role='plan'`), 최근 이력 40항목(각 `'x'*100`), 과제 둘(하나는 `detail`이 `'y'*1000`), 지식 카탈로그 하나(`'z'*2000`)가 있다.
- 실행: `store.fit_context(context, max_bytes=1200, workspace=root, mandatory_keys=['goal', 'action'])`. `tasks` 줄임의 `source_ref`와 목록의 `recent_history` 참조를 `read_source(..., limit=10**7)`로 읽는다.
- 단언: `overflow`가 `None`이다. `actual_bytes`가 1200 이하이고 `reductions`가 비어 있지 않다. 되살린 과제 목록과 최근 이력이 원래 값과 같다.
- 대역: 없음.
- 비고: 작업 공간 폴더가 없어도 카탈로그가 그 아래에 만들어진다.

### `test_packed_sizes_equal_the_canonical_bytes_of_the_packed_context` (행 115–127)
- 성질: 크기 맞춤이 보고하는 바이트 수는 포장된 문맥과 원래 문맥의 정규 JSON 바이트 길이와 정확히 같다.
- 준비: 문맥 셋. (0) 빈 목록·빈 사전·줄바꿈 문자열·중첩 구조(`é`와 U+2028 포함)·숫자 30개. (1) 목표만. (2) 긴 목표(1000자)와 최근 이력, 긴 과제. 한도는 10, 300, 10**6 셋이다.
- 실행: 문맥과 한도의 조합마다 `store.fit_context(..., mandatory_keys=['goal'])`.
- 단언: `actual_bytes`가 `len(canonical_json(got['context']))`와 같다. `original_bytes`가 `len(canonical_json(context))`와 같다. 넘침이 있으면 `overflow.mandatory_bytes`가 `len(canonical_json({'goal': context['goal']}))`와 같다.
- 대역: 없음.
- 비고: `subTest(context=..., limit=...)` 9건이다.

### `test_mandatory_overflow_reports_size_without_reduction` (행 128–130)
- 성질: 필수 문맥만으로 한도를 넘으면, 필수 값을 줄이지 않은 채 넘침을 보고한다.
- 준비: 1000자 목표와 최근 이력.
- 실행: `store.fit_context(context, max_bytes=100, ..., mandatory_keys=['goal'])`.
- 단언: `overflow.reason`이 `'mandatory_context_exceeds_limit'`이고, 문맥의 `goal`이 원래 값 그대로다.
- 대역: 없음.

### `test_read_source_range_missing_and_hash_error` (행 131–136)
- 성질: 원천 읽기는 한도까지 잘라 범위를 밝히고, 없는 원천은 `missing`, 해시가 맞지 않는 원천은 `error`다.
- 준비: `materialize_inputs(root, {'x.bin': b'abcdef'})`의 첫 참조.
- 실행: `read_source(root, ref, limit=2)`. 없는 경로 `input/nope`의 참조로 읽기. 참조의 `sha256`을 `'0'*64`로 바꿔 읽기.
- 단언: 부분 읽기는 `b'ab'`이고, `truncated`가 참이며, `range`가 `{'start': 0, 'end': 2, 'total': 6}`이다. 없는 원천은 `status='missing'`, 해시 불일치는 `status='error'`다.
- 대역: 없음.

## RoleInputTests (행 139–596)

`unittest.TestCase`를 그대로 상속한다. 표지, 속성, 훅, 도우미가 없다. 대부분의 테스트는 `surface_state()`의 인스턴스에서 역할 프로필 하나를 골라 `prepare_role_input`을 임시 작업 공간으로 부른다. 스냅숏은 `'a'*40`, 활동은 `'AC-1'`이다.

### `test_checker_sees_canonical_catalog_beyond_direct_comparison` (행 140–185)
- 성질: 계획·준비 역할의 제출 검사기는 역할에 직접 넘긴 값이 아니라 저장된 정본 과제 목록을 본다. 그래서 직접 문맥에서 빠진 완료 과제의 경계와 결과도 검사에 쓰인다.
- 준비: `surface_state()`의 runtime에 `task_contract()`로 과제 넷을 만든다. `TK-ready`(planned), `TK-completed`(completed, 결과 `EX-old`), `TK-waiting`(waiting), `TK-returned`(waiting)다. `TK-returned`는 결과 `EX-returned`를 가지며, 모든 완료 의무의 증거가 `EX-returned`다. 역할에 넘기는 `readers`는 과제들의 사본이다. 완료 과제의 결과에는 정본에 없는 `local_path`를 덧붙인다.
- 실행: 역할 `research_plan`과 `research_preparation` 각각에 대해 `prepare_role_input`을 부른다. 문맥에는 `readers`와 `ready_task_ids=['TK-ready']`를 넣고 `install_submission_tools=True`를 준다. 이어서 `input/submission/context.json`의 과제 목록으로 제출 검사 함수들을 부른다.
- 단언: 제출 문맥의 과제 사전이 runtime의 정본 과제와 정확히 같다(덧붙인 `local_path`가 없다). 역할 직접 문맥의 과제에는 `TK-completed`가 없다. 계획 제출은 `TK-ready`의 처분(`task_disposition`)과 `TK-returned`의 평가(`assessment`)로 `validate_plan_submission`을 통과한다. 평가를 비우면 `ValueError`다. `contract_check_errors`는 완료 형제 과제의 경계(개정 1)를 인용한 후보에 빈 오류 목록을 내고, 개정을 2로 바꾸면 오류를 낸다. 처분의 `parallel_task_ids`에 `TK-completed`나 `TK-waiting`을 넣으면 `ValueError`다.
- 대역: 없음.
- 비고: `subTest(role=...)` 2건. 예외 단언은 모두 유형만 본다.

### `test_plan_receives_returned_work_separately_from_ready_selection_population` (행 187–208)
- 성질: 계획 역할은 결과가 돌아온 과제를 준비된 선택 후보와 따로 받고, 후보 순서의 씨앗은 역할 문맥이 아니라 목록 증거에 남는다.
- 준비: 결과 하나가 돌아온 `waiting` 과제 `TK-returned` 하나. 준비된 과제는 없다. `research_plan` 프로필.
- 실행: `prepare_role_input(..., ready_task_ids=[], install_submission_tools=True)`.
- 단언: 직접 문맥의 `ready_task_ids`는 `[]`이고 `returned_task_ids`는 `['TK-returned']`다. 목록의 `candidate_order.ids`는 `[]`이고, 직접 문맥에 `candidate_order`가 없다. 직접 문맥의 과제 ID 목록이 `['TK-returned']`이고 `result_count`가 1이다. 제출 문맥의 과제 결과가 정본 결과와 같다.
- 대역: 없음.
- 비고: 행 202의 주석은 "봉인된 순서가 `tasks`를 정렬하고, 그 씨앗은 역할 문맥이 아니라 목록 증거"라고 밝힌다.

### `test_impact_review_evidence_is_required_direct_input` (행 210–231)
- 성질: 영향 검토(impact review) 증거는 필수 직접 입력이라, 한도를 넘어도 참조로 바뀌지 않고 넘침으로 보고된다. 증거가 없으면 준비가 거부된다.
- 준비: `surface_state()`의 설정을 `max_input_bytes=16000`으로 바꾸고 `build_profiles`로 프로필을 다시 만든다. `maintenance` 프로필. 행동은 `stage='impact_review'`이고 생산 실행 `EX-producer`를 가리킨다. 증거는 요청과, 설명이 `'original evidence '`의 6000회 반복인 출력이다.
- 실행: `prepare_role_input({'action': action, 'impact_review_input': evidence}, ..., workspace=root/'oversize')`. 이어서 증거 없이 `workspace=root/'missing'`으로 부른다.
- 단언: 목록의 `required_direct_keys`에 `impact_review_input`이 있다. 문맥의 그 값이 증거와 같다. `overflow`가 있고, 그 `required_direct_keys`에도 `impact_review_input`이 있다. 증거가 없으면 `ValueError`를 `'impact_review_input'`으로 던진다.
- 대역: 없음.

### `test_compaction_preserves_producer_validation_inputs` (행 233–250)
- 성질: 역할 문맥을 압축해도 생산자 제출 검사가 쓰는 결과와 검토 참조는 제출 문맥에 보존된다.
- 준비: 결과(`EX-preserved`)와 검토(`EX-review`)를 가진 `planned` 과제 `TK-1`. `research_preparation` 프로필.
- 실행: `prepare_role_input(..., install_submission_tools=True, max_artifact_bytes=100000)`.
- 단언: 제출 문맥에 대한 `submission.supplied_reference_ids`에 `EX-preserved`와 `EX-review`가 있다. 제출 문맥의 과제 결과가 정본과 같다. 역할 직접 문맥의 과제에는 `results` 키가 없다.
- 대역: 없음.

### `test_engine_context_restores_multihop_git_artifact` (행 252–289)
- 성질: 엔진이 연속 실행의 문맥을 만들 때, 여러 단계 이전의 Git 산출물까지 되살려 최신 파일을 작업 공간에 놓고, 단계마다 결과 원천과 체크포인트를 붙인다.
- 준비: `research_fixtures.new_instance`로 저장소를 만들고 공개 `initialize`를 돈다. 설정은 operator와 scholarly를 끈다. 그 위에 `ResearchEngine`을 연다. `writer_lock` 아래에서 산출물 다섯 개를 `save_with_state`로 발행한다. `EX-a`의 `lemma.txt`(`ancestral evidence`)와 `keep.txt`, `EX-b`의 `lemma.txt`(`latest lemma`), 두 실행의 `result.json`이다. runtime에 끝난 `maintenance` 실행 둘을 넣는다. `EX-a`와, `EX-a`를 이어받는 `EX-b`다. 둘 다 활동 `AT-resume`에 속하고, 결과 참조와 출력 파일 행을 가진다. 두 실행의 체크포인트 `{'partial': <ID>}`도 넣는다.
- 실행: `engine._context({'id': 'AC-c', 'role': 'maintenance', 'continuation_of': 'EX-b'}, root/'resume', execution_id='EX-c')`.
- 단언: `previous_output_files`의 경로 목록이 `['keep.txt', 'lemma.txt']`다. 작업 공간의 `input/previous-output/lemma.txt`는 최신 바이트이고, `keep.txt`는 `EX-a`의 바이트다. `continuation_history`의 실행 순서가 `['EX-a', 'EX-b']`다. 단계마다 `result_source.snapshot`이 엔진 머리이고, `local_path`의 바이트가 그 산출물 바이트이며, `checkpoint`가 runtime의 값과 같다.
- 대역: 없음.
- 비고: 실제 Git 저장소와 공개 초기화 경로를 쓰는 이 클래스의 유일한 시험이다. 같은 복원 규칙을 저장소 없이 검사하는 것은 `test_multihop_restores_latest_file_and_stage_evidence`다.

### `test_candidate_population_is_compact_profile_bound_and_reproducible` (행 291–321)
- 성질: 준비 역할의 후보 과제 목록은 작게 요약되지만 원천으로 되살아나고, 실행 프로필에 묶이며, 봉인된 후보 순서로 같은 프롬프트를 재현한다.
- 준비: `planned` 과제 셋(`TK-z`, `TK-a`, `TK-m`). 각각 `large_detail`이 10만 자다. `research_preparation` 프로필과 그 역할의 문맥.
- 실행: 작업 공간 `first`로 `prepare_role_input`. 결과의 `candidate_order`를 주어 작업 공간 `replay`로 다시 부른다.
- 단언: 프롬프트가 `boundary_prompt(profile)`로 끝난다. 문맥에 `config`가 없고 `profile_selection`이 있으며, `execution_profile`이 프로필과 같다. 과제 ID 집합이 셋과 같다. 첫 과제에 `large_detail`이 없다. 과제마다 `source_ref`를 `read_source`로 읽으면 정본 과제와 같다. `candidate_order.ids`가 문맥 과제 순서와 같다. 재현 결과의 `candidate_order`와 프롬프트가 처음 것과 같다.
- 대역: 없음.

### `test_multihop_restores_latest_file_and_stage_evidence` (행 323–360)
- 성질: 연속 복원은 여러 단계를 거슬러 가장 최신 파일과 단계별 결과·체크포인트를 되살리고, 활동이 다르거나 순환하는 사슬은 거부한다.
- 준비: 사전 보관본 `archive`와 지역 함수 `entry(name, body, generation)`. `entry`는 `runtime/artifacts/<세대>/<이름>`에 바이트를 넣고 출력 파일 행을 만든다. runtime에 끝난 `maintenance` 실행 둘을 넣는다. `EX-a`는 `lemma.txt=old`, `keep.txt=keep`을, `EX-b`는 `EX-a`를 이어받고 `lemma.txt=new`를 가진다. 두 실행에 `result.json` 참조와 체크포인트를 단다.
- 실행: `context_store.restore_continuation(runtime, {'role': 'maintenance', 'continuation_of': 'EX-b'}, Path(directory), snapshot='a'*40, read_artifact=archive.__getitem__ 람다)`. 이어서 `EX-a`의 활동을 `AT-other`로 바꿔 부른다. 활동을 되돌리고 `EX-a`의 행동이 `EX-b`를 이어받게 해 순환을 만들어 부른다.
- 단언: 연속 이력 순서가 `['EX-a', 'EX-b']`다. 단계마다 `local_path` 바이트와 `sha256`이 보관본과 맞고, 체크포인트가 같다. 이전 출력의 `lemma.txt`는 `b'new'`, `keep.txt`는 `b'keep'`이다. 활동이 다르면 `ValueError`를 `'activity'`로, 순환이면 `'cycle'`로 던진다.
- 대역: 사전 조회 읽기 람다.

### `test_required_direct_action_is_never_replaced_by_reference` (행 362–367)
- 성질: 필수 직접 입력인 행동은 한도를 넘어도 참조로 바뀌지 않는다.
- 준비: `reason`이 `'essential '`의 1000회 반복인 행동.
- 실행: `fit_context({'action': action}, max_bytes=500, ..., mandatory_keys=['action'])`.
- 단언: 문맥의 `action`이 원래 값과 같고, `overflow`가 있다.
- 대역: 없음.

### `test_required_input_overflow_is_structured_and_lossless` (행 369–379)
- 성질: 필수 입력 넘침은 역할과 활동을 밝힌 구조화된 기록이고, 필수 값을 잃지 않는다.
- 준비: 1000자 목표와 행동.
- 실행: `fit_context(..., max_bytes=100, mandatory_keys=['goal', 'action'], role='research_work', profile_id='P1', activity_id='ACT-1')`.
- 단언: `overflow.kind`가 `'input_overflow'`, `role`이 `'research_work'`, `activity_id`가 `'ACT-1'`이다. `actual_bytes`가 `limit_bytes`보다 크다. 문맥의 `goal`이 원래 값이다.
- 대역: 없음.

### `test_role_manifest_distinguishes_required_direct_views_from_references` (행 381–391)
- 성질: 역할 목록은 직접 입력과 참조를 나누어 적고, 없는 키를 직접 입력으로 요구하면 거부한다.
- 준비: 목표, 정책, 과제 목록을 담은 문맥.
- 실행: `build_role_manifest(context, workspace=..., role='research_plan', direct_keys=['goal', 'policies'], reference_keys=['tasks'])`. 이어서 `direct_keys=['missing']`으로 부른다.
- 단언: `direct`의 키 순서가 `['goal', 'policies']`다. 첫 참조의 키가 `tasks`이고, 원천 경로가 `input/catalog/tasks.json`이다. 없는 키는 `ValueError`다(유형만 본다).
- 대역: 없음.
- 비고: 둘째 호출은 `with` 블록이 끝나 임시 폴더가 지워진 뒤에 같은 경로로 부른다. 제품 `build_role_manifest`는 작업 공간에 닿기 전에 없는 키를 검사해 `"role manifest keys are missing: ..."`를 던지므로(`context_store.py` 행 270–272), 지금의 거부는 키 검사에서 난다. 폴더가 없더라도 뒤따르는 `write_source_catalog`는 폴더를 만든다(행 225). 테스트는 예외 유형만 보므로 거부 사유를 고정하지 않는다.

### `test_role_input_uses_current_schema_documents_and_private_resume_bytes` (행 393–416)
- 성질: 역할 입력은 현재 출력 계약 스키마를 쓰고, 재개 체크포인트와 이전 실행을 필수 직접 입력으로 보존하며, 목록이 봉인한 바이트가 바뀌면 검증에 실패한다.
- 준비: `research_work` 프로필. 문맥에는 행동, 과제, 이전 실행(`failure='must not disappear'`), 재개 체크포인트(`remaining_work='P'`), 긴 최근 이력이 있다.
- 실행: `context_store.write_source_catalog`를 감싼 채 `prepare_role_input(..., artifact_prefix='runtime/artifacts/EX-1')`. 이어서 목록 검증과 산출물 검증을 부른다.
- 단언: `write_source_catalog`가 1번 불렸다(행 405 주석: 목록이 `fit_context`의 카탈로그를 재사용한다). 문맥의 `resume_checkpoint`가 원래 값이다. `validate_role_manifest(manifest)`가 참이다. `manifest.prompt.sha256`이 프롬프트 UTF-8 바이트의 SHA-256이다. `output_contract.id`가 `contracts.schema_for('research_work')['x-contract-id']`다. `required_direct_keys`에 `previous_execution`이 있다. `direct`에서 `resume_checkpoint`를 뺀 목록은 `validate_role_manifest`에서 `ValueError`다. `verify_manifest_artifacts(manifest, artifacts.__getitem__)`가 `[]`다. 프롬프트 산출물을 `b'changed'`로 바꾸면 `ValueError`다.
- 대역: `patch('do_math.context_store.write_source_catalog', wraps=...)`.
- 비고: 이름의 "private resume bytes"는 재개 체크포인트가 직접 입력으로 남는다는 것으로 확인된다. 예외 단언은 유형만 본다.

### `test_preparation_compares_full_population_and_only_effective_k_summaries` (행 418–445)
- 성질: 준비 역할은 선택 가능한 과제 전체를 비교 대상으로 받고, 지식 카탈로그에는 효력 있는 K(검증된 지식)의 요약만 싣는다. 개정 대상 과제는 후보에 더해진다.
- 준비: `task_contract()` 과제와, 그것을 복사한 `waiting` 과제 `TK-2`. `knowledge_records.create_candidate`로 만든 추측(conjecture) 지식. 요약은 `'Do not call this verified'`다. `research_preparation` 프로필.
- 실행: `engine_fixtures.context_engine(instance, runtime)._context({'role': 'research_preparation'}, Path(d))`로 실제 문맥 생산자의 문맥을 얻어 `prepare_role_input`에 준다. 이어서 대기열에 `TK-2`를 개정 대상(`revision_targets`)으로 가진 준비 행동을 넣고, 스냅숏 `'b'*40`으로 다시 준비한다.
- 단언: 처음 문맥의 과제 목록은 `task_contract`의 과제 하나다. 지식 카탈로그 첫 행이 그 지식이고, `usable_as_k`가 거짓이며, `verified_summaries`가 `[]`다. 목록의 `required_direct_keys`에 `knowledge_catalog`가 있다. 개정 행동 뒤에는 과제 ID 집합이 두 과제이고, 문맥 과제 순서가 `candidate_order.ids`와 같다.
- 대역: `context_engine`(엔진 대역, `engine_fixtures.py` 행 281의 docstring: 실제 문맥 생산자를 두고 관련 없는 호스트 관찰을 바꾼다).

### `test_verified_summary_tracks_identity_use_withdrawal` (행 447–467)
- 성질: 지식 카탈로그의 검증된 요약은 신원 평가의 사용 상태를 따르고, 사용이 철회되면 사라진다.
- 준비: `knowledge_fixtures.verified_knowledge()`의 증거(합성 형식 영수증)를 `surface_state()` 인스턴스에 더한다. 행 453의 주석은 "이 시험은 전파를 보지 Lean을 보지 않는다"고 밝힌다. 지역 함수 `prepare()`는 `context_engine`의 문맥으로 `research_preparation` 입력을 준비한다.
- 실행: `prepare()`. 이어서 `set_assessment_use(instance, assessment, 'withdrawn', 'fixture withdrawal', 'user')` 뒤 다시 `prepare()`.
- 단언: 처음에는 첫 행의 `usable_as_k`가 참이고, 첫 검증 요약의 `text`가 `'Truth'`이며, 그 `basis.assessment_id`가 평가 ID다. 철회 뒤에는 `usable_as_k`가 거짓이고 `verified_summaries`가 `[]`다.
- 대역: `context_engine`.

### `test_review_input_matches_real_seat_view_and_rejects_peer_injection` (행 469–486)
- 성질: 신원 검토 역할의 입력은 실제 검토 좌석의 보기와 맞아야 하고, 다른 좌석의 비공개 값이 끼면 거부된다.
- 준비: `review_cycle.start_review({'revision': 1, 'statement': 'P'}, reviewers=2)`로 주기를 열고 runtime의 `RC-1`로 둔다. `next_actions`의 첫 행동에 ID, 역할, 주기, 권한을 붙인다. `role_review`는 `context_for(cycle, action)`이다. `identity_review` 프로필.
- 실행: `prepare_role_input`. 이어서 `role_review`에 `peer_private`를 더하고 다시 부른다.
- 단언: 목록의 `private_scope.slot`이 행동의 슬롯과 같다. 끼워 넣은 경우는 `ValueError`를 `'seat-scoped'`로 던진다.
- 대역: 없음.

### `test_engine_review_context_reaches_role_input_with_bound_identity_and_policy` (행 488–516)
- 성질: 엔진이 만든 검토 문맥은 신원 기준과 정책 참조를 묶은 채 역할 입력에 닿고, 둘 가운데 하나라도 위조되면 거부된다.
- 준비: `review_fixtures.ReviewFakeEngine(workspace)`. 행 494–495의 주석대로 대역 엔진은 `governance_start`의 가족에서 시작하고, 채택된 헌장은 `surface_state`에서 온다. 그래서 두 인스턴스를 합치되, 설정과 `governance_start()`의 각 가족은 사전 단위로 병합한다. 머리를 `'a'*40`으로 두고 `engine.start('K1')`로 검토를 연다. 대기 행동에 권한을 붙인다. `engine._prepare_review_context(action, workspace)['context']`로 검토 문맥을 얻는다.
- 실행: 지역 함수 `prepare()`로 `identity_review` 입력을 준비한다. 이어서 `identity_basis`와 `policy_ref`를 각각 `'forged'`로 바꿔 다시 준비한다.
- 단언: 문맥의 `role_review.identity_basis`와 `policy_ref`가 엔진 검토 문맥의 값과 같다. 위조한 두 경우는 `ValueError`를 `'authorized seat view'`로 던진다.
- 대역: `ReviewFakeEngine`(docstring: 검증된 형식 증거와 검토 정책을 가진 후보 정리 `K1` 위의 제품 엔진, 저장소 없음, `_save`는 autospec 대역).
- 비고: `subTest(field=...)` 2건.

### `test_submission_context_is_installed_before_single_input_seal` (행 518–532)
- 성질: 제출 검사용 정본 문맥은 입력 봉인 전에 설치되고, 역할 문맥과 같은 형식 검증기·거버넌스 값을 담는다.
- 준비: `research_work` 프로필. 문맥에는 인스턴스 ID, 행동, 과제, 형식 검증기 참조(`tool:lean`)가 있다.
- 실행: `prepare_role_input(..., install_submission_tools=True, max_artifact_bytes=100000, artifact_prefix='runtime/artifacts/EX-1')`.
- 단언: `input/submission/context.json`의 `formal_verifier`와 `governance`가 역할 문맥의 값과 같다. `required_direct_keys`에 `submission_contract`가 있다.
- 대역: 없음.
- 비고: 이름의 "단일 입력 봉인 전"이라는 순서는 결과 파일의 존재와 내용으로만 확인되고, 호출 순서를 직접 단언하지는 않는다.

### `test_role_overflow_keeps_original_sizes_and_waits_on_activity` (행 534–552)
- 성질: 역할 입력 넘침은 원래 크기와 해소 질문을 기록하고, 넘침을 미루면 실행이 끝날 때까지는 작업 중이다가 끝난 뒤 활동이 대기로 바뀐다.
- 준비: `research_work` 프로필 본문의 `input.max_input_bytes`를 200으로 바꿔 `seal_profile`로 다시 봉인한다. 문맥에는 3000자 증거를 가진 과제가 있다.
- 실행: `prepare_role_input`. `defer_input_overflow(runtime, overflow, at=..., question_ref='Q-1')`. `transition_execution`으로 `EX-1`을 `ended`(`cancelled`, 사유 `input overflow`, 처분 `question`)로 옮긴 뒤 다시 `defer_input_overflow`.
- 단언: `overflow.original_bytes`가 3000보다 크고, `resolution_question` 키가 있다. 첫 미룸의 `status`는 `'working'`이고 둘째는 `'waiting'`이다. 활동 `AC-1`의 상태가 `'waiting'`이다.
- 대역: 없음.

### `test_role_overflow_records_the_context_budget_it_compared` (행 554–572)
- 성질: 필수 문맥이 전체 한도보다 작아도 고정 문서·스키마·틀을 뺀 문맥 예산을 넘으면 넘침이고, 기록은 비교한 그 예산을 밝힌다.
- 준비: 지역 함수 `fixed(p)`는 `contracts.render_prompt('research_work', {})`를 `prepare_prompt`로 감싼 프롬프트의 UTF-8 길이다. 프로필의 `max_input_bytes`를 `fixed + 1000`으로 바꿔 다시 봉인한다. 문맥에는 3000자 증거가 있다.
- 실행: `prepare_role_input(...)['overflow']`.
- 단언: `reason`이 `'mandatory_context_exceeds_limit'`이다. `(limit_bytes, context_budget_bytes)`가 `(한도, 한도 − fixed)`다. `context_budget_bytes < mandatory_bytes < limit_bytes`다.
- 대역: 없음.
- 비고: 행 555–556의 주석이 이 성질을 그대로 밝힌다.

### `test_assessment_only_input_contains_waiting_contract_and_review_history` (행 574–596)
- 성질: 평가만 하는 준비 입력에도 대기 중인 과제의 계약과 검토·평가 이력이 원천과 제출 문맥에 그대로 들어간다.
- 준비: 검토(`revision_required`)와 모델 평가 이력을 가진 `waiting` 과제 `TK-rejected`. 행동의 `assessment_targets`가 그 과제의 개정 1을 가리킨다. `research_preparation` 프로필.
- 실행: `prepare_role_input(..., install_submission_tools=True, max_artifact_bytes=100000)`.
- 단언: 문맥 과제 ID 목록이 `['TK-rejected']`다. 그 `source_ref.path` 파일을 풀면 원래 과제와 같다. 제출 문맥의 과제 목록이 `[task]`다.
- 대역: 없음.
- 비고: 함수 안에서 `surface_state`와 `prepare_role_input`을 다시 import한다. 모듈 머리에서 이미 가져온 이름이라 효과는 없다.

## 관계

- 역할 입력 포장의 역할별 규칙(각 역할의 직접 키, 도구 설치, 도달 범위)은 `test_role_input`이 더 넓게 검사한다. 이 모듈은 문맥 저장 계층의 무손실·크기·봉인 규칙과 몇몇 역할 경계를 본다.
- 보관된 역할 입력 바이트를 상태 점검이 비교하는 쪽(`verify_manifest_artifacts`, `prefetch_artifacts`)은 `test_state_checks`의 `BatchedInspectionTests`가 검사한다.
- 원천 카탈로그의 유니코드 바이트 보존은 `test_unicode_flow`의 `test_source_catalog_and_direct_input_hash_exact_bytes`가 맡는다.
- 물리 경계와 재분석 지점 규칙은 `test_git_store`(`PhysicalBoundary`)와 `test_retention`(실행 폴더)이 각자의 영역에서 검사한다.
- 검토 좌석 범위의 본래 규칙은 `test_review_cycle`, `test_review_engine`이 맡는다. 계획 제출 검증은 `test_planning`, 계약 검사는 `test_submission_checks`가 맡는다. 이 모듈은 역할 입력을 통해 그 규칙들이 정본 문맥을 보는지 확인한다.
- 픽스처 의존: `record_fixtures.surface_state`, `task_contract`, `task_disposition`, `contract_check`; `research_fixtures.governance_start`, `assessment`, `candidate`, `new_instance`; `engine_fixtures.context_engine`; `knowledge_fixtures.verified_knowledge`; `review_fixtures.ReviewFakeEngine`.
- 이 모듈에만 있는 도우미는 없다. 테스트 안의 지역 함수로 `walk`, `entry`, `prepare`, `fixed`가 있다.
