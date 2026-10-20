# test_repository

| 항목 | 값 |
|---|---|
| 조각 | `foundation` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_repository.py` (515행) |
| 클래스 / 테스트 | 6 / 30 |
| 시험 대상 제품 코드 | `do_math/repository.py`의 `ResearchRepository`(`initialize`, `load`, `view`, `load_records`, `save_with_state`, `validate_candidate`, `read`, `blob_sizes`, `list_files`, `query`, `export`, `published_state`, `_read_documents`, `_validate_artifact_evidence`, `_store`), `retain_reads`, `_VALIDATED_READ_LIMIT`, `_decode_families`, `validate_storage_value`, `canonical_json`, `new_id`, `RepositoryCursorError`; `do_math/git_store.py`의 `GitStateStoreConflict`; `do_math/state_contract.py`의 `StateContract.validate`; `do_math/state_checks.py`의 `inspect_state`; `do_math/engine.py`의 `ResearchEngine._sealed_bytes`(안에서 `repository.sealed_bytes`); 준비용 `initialization.initialize_state`·`original_input_bytes`, `governance.preserve_source` |
| 사용하는 픽스처 모듈 | `research_fixtures`: `bare_engine`, `current_state`, `git_init`, `installed_contract`, `with_validator` |
| 격리 표지 | 없음 |
| 시작 상태 | 대부분 `git_init`으로 만든 실제 Git 저장소에 `current_state` 또는 `initialize_state`의 상태를 직접 `initialize`한 것(네 단 밖: 저장소 계층 직접 초기화). `StorageValueTests`의 둘과 `CandidateCopyTests`는 1단에 가깝다. 후보 검증은 저장소를 건드리지 않는다. `SealedArtifactReadTests`는 `bare_engine`과 저장소 대역을 쓴다 |

## 목적

모듈 docstring은 "새 임시 Git 저장소만 쓰는, 스냅숏을 마주하는 저장소 시험"이라고 밝힌다. `ResearchRepository`는 인스턴스 하나의 연구 상태와 런타임 상태를 Git 커밋(스냅숏)으로 발행하고 읽는 계층이다. 이 모듈은 여섯 무리의 계약을 검사한다.

1. 기본 계약: 초기화·적재·저장, 옛 스냅숏의 정확한 읽기, 낡은 머리(stale head)의 충돌, 산출물 묶음의 불변성, 스냅숏에 묶인 질의 커서, 내보내기(export)의 목적지 제약, ID와 정규 JSON의 모양.
2. 검증된 읽기의 재사용: 같은 사실을 다시 검사하지 않는다. 자기 발행, 공유 머리, 이미 맞춘 바이트가 여기에 해당한다(`ValidatedReadReuseTests` docstring).
3. `save_with_state`의 효율과 안전: 변하지 않은 저장은 효과가 없다. 부모 바이트를 재사용하되 손상은 여전히 거부한다. 새 증거만 다시 읽는다. 낡은 머리는 산출물 모양보다 먼저 거부된다.
4. 후보 복사: 사건 번호 매기기가 호출자의 원본을 건드리지 않는다.
5. 저장 값 영역: 검증과 직렬화가 같은 영역을 쓴다. 부동소수는 부모의 정수와 같아도 거부된다.
6. 봉인된 산출물 읽기: 한 번 맞춘 행은 다시 해시하지 않는다.

## 모듈 수준 요소

- `SCRIPTS` (행 19): 스킬의 `scripts/` 폴더. 행 20–21에서 `sys.path`에 없으면 맨 앞에 넣는다.
- `candidate_repository(test)` (행 35–38): 설치 계약을 쓰는 저장소를 새 빈 Git 저장소 위에 연다. 임시 폴더는 `test.enterContext`로 테스트 끝에 정리되고, 인스턴스 ID는 `RI-01ARZ3NDEKTSV4RRFFQ69G5FAV`다. docstring은 "후보 검증은 이 저장소에 닿지 않는다"고 밝힌다. 곧 `validate_candidate`만 부르는 시험이 저장소 객체를 얻는 가장 싼 방법이다. 사용처는 `CandidateCopyTests`의 두 테스트와 `StorageValueTests.test_inspection_builds_no_json_bytes_and_publication_checks_the_value_domain`이다.
- `INSTANCE_ID` (행 41): `"RI-"` 뒤에 0이 26개인 인스턴스 ID. `ResearchRepositoryTests`와 `SaveWithStateTests`의 `setUp`이 쓴다.
- 행 514–515: 직접 실행하면 `unittest.main(verbosity=2)`로 이 모듈의 시험을 돈다.

## ResearchRepositoryTests (행 44–216)

`unittest.TestCase`를 그대로 상속하고 표지와 클래스 속성이 없다. 원문에서 `setUp`이 테스트 셋 뒤(행 93)에 놓여 있지만 모든 테스트에 적용된다.

- `setUp` (행 93–100): 임시 폴더 아래 `repository` 폴더를 만들어 `git_init`하고, `INSTANCE_ID`로 `ResearchRepository`를 연다. `current_state({"title": "instance"})`로 `initialize`한 커밋을 `self.initial_head`에 둔다. `self.root`는 임시 폴더, `self.repository_path`는 저장소 경로다.
- `tearDown` (행 102–103): 임시 폴더를 정리한다.

### `test_export_reads_bounded_batches_and_preserves_binary_contents` (행 45–55)
- 성질: 내보내기는 Git에서 파일을 하나씩 읽지 않고 64개 이하의 배치로 읽으며, 이진 내용을 그대로 쓴다.
- 준비: 클래스 절의 `setUp`. `runtime/artifacts/BA-export/<i>.bin` 150개를 저장한다. 각 파일은 `bytes([i % 256]) * 1024`다.
- 실행: 저장소 내부 `_store.read_bytes`가 불리면 실패하게 하고 `_store.read_many`를 `wraps`로 감싼 채 `export(self.root/'batched', head, prefixes=('runtime/artifacts/',))`.
- 단언: `read_many`가 3번 불렸고, 매번 경로 목록 길이가 64 이하다. 결과 `files`의 집합이 저장한 경로 집합과 같다. 내보낸 파일마다 바이트가 원본과 같다.
- 대역: `patch.object(_store, 'read_bytes', side_effect=AssertionError('per-file Git read'))`, `patch.object(_store, 'read_many', wraps=...)`.
- 비고: 150개를 64개 단위로 나누면 3번이다. 제품 `export`(행 680)의 배치 상한이 64다.

### `test_published_artifacts_are_not_read_again_at_later_heads_only` (행 57–74)
- 성질: 이 프로세스가 발행한 산출물은 그 커밋과 뒤의 커밋에서 Git에 다시 묻지 않고 읽히지만, 산출물보다 앞선 커밋에서는 Git에 묻는다.
- 준비: 클래스 절의 `setUp`. 적재한 머리를 `before`로 둔다. `runtime/artifacts/BA-known/input.txt`(`b"archived input\n"`)를 저장한 커밋이 `written`이다. 제목을 바꿔 한 번 더 저장한 커밋이 `later`다.
- 실행: `_store.read_bytes`를 실패하게 하고 `_store.blob_sizes`를 감싼 채, 두 커밋에서 `read(path, snapshot)`와 `blob_sizes([path], snapshot)`를 부른다. 이어서 `before`에서 `blob_sizes([path], before, missing="omit")`와 `read(path, before)`를 부른다.
- 단언: 두 커밋에서 바이트와 크기 `{path: len(raw)}`가 맞다. 저장소 계층의 `blob_sizes` 호출이 Git 계층에 넘긴 경로 목록이 두 번 모두 빈 목록 `[]`다. `before`에서는 크기가 `{}`이고, 읽기는 예외를 낸다(`Exception` 전반을 받으므로 유형을 고정하지 않는다).
- 대역: `read_bytes` 실패 패치, `blob_sizes` 감싸기.
- 비고: 행 71의 주석은 "산출물보다 앞선 머리는 여전히 Git에 묻고, Git은 없다고 답한다"고 밝힌다.

### `test_live_input_snapshots_stay_validated_beyond_the_read_bound` (행 76–91)
- 성질: 붙들어 둔(retained) 스냅숏의 검증된 읽기는 캐시 상한을 넘겨도 남고, 붙들기를 풀면 다음 저장에서 밀려난다.
- 준비: 클래스 절의 `setUp`. 현재 머리를 `pinned`로 두고 `retain_reads(git_dir, {pinned})`를 부른다.
- 실행: 제목을 바꿔 `_VALIDATED_READ_LIMIT + 2`번 저장한다(상한 4이므로 6번). `published_state(pinned)`를 본다. `retain_reads(git_dir, set())`로 붙들기를 풀고 한 번 더 저장한 뒤 다시 본다.
- 단언: 붙든 동안에는 `published_state(pinned)`가 `None`이 아니다. 풀고 저장한 뒤에는 `None`이다.
- 대역: 없음.
- 비고: `finally`에서 붙들기를 다시 풀어, 프로세스 전역 캐시 상태가 다른 시험에 새지 않게 한다. 제품 `retain_reads` docstring은 "다음 호출까지 `heads`의 검증된 읽기를 LRU 상한 밖에 둔다"고 밝힌다.

### `test_initialize_load_save_and_exact_old_snapshot_read` (행 105–114)
- 성질: 초기화한 상태가 그대로 적재되고, 저장 뒤에도 옛 스냅숏은 옛 값 그대로 읽힌다.
- 준비: 클래스 절의 `setUp`.
- 실행: `load()`, runtime `status`를 `running`으로 바꾼 `save_with_state`, 옛 머리의 `load`, 새 머리에서 `runtime/_state/metadata.json` 읽기.
- 단언: 적재한 머리가 `initial_head`다. `title`은 `instance`, `object_format`은 `sha1`, runtime `status`는 `initializing`이다. 옛 머리의 runtime `status`는 여전히 `initializing`이다. 새 머리의 메타데이터 파일을 JSON으로 풀면 `record.status`가 `running`이다.
- 대역: 없음.

### `test_stale_save_conflict_does_not_overwrite` (행 116–122)
- 성질: 같은 부모에서 두 번째로 저장하려는 쪽은 충돌로 거부되고, 먼저 저장한 쪽의 결과를 덮어쓰지 않는다.
- 준비: 클래스 절의 `setUp`. 같은 저장소와 인스턴스로 둘째 `ResearchRepository` 객체를 연다.
- 실행: 첫 객체가 `initial_head`에서 `status=running`으로 저장한다. 둘째 객체가 같은 `initial_head`에서 `status=paused`로 저장한다.
- 단언: 둘째 저장이 `GitStateStoreConflict`를 던진다. 현재 머리가 첫 저장의 커밋이고, 그 runtime `status`가 `running`이다.
- 대역: 없음.

### `test_new_artifact_bundle_is_saved_with_state_and_existing_bundle_is_immutable` (행 124–141)
- 성질: 새 산출물 묶음은 상태와 함께 저장되고, 이미 있는 묶음에는 파일을 더할 수 없다.
- 준비: 클래스 절의 `setUp`.
- 실행: `AB-01/output.txt`(`b"sealed"`)와 함께 저장한다. 같은 묶음에 `other.txt`를 더해 저장한다. 새 묶음 `AB-02/output.txt`와 함께 `status=completed`로 저장한다.
- 단언: 둘째 저장이 `ValueError`를 던진다(유형만 본다). 셋째 저장 뒤 `AB-01/output.txt`가 여전히 `b"sealed"`다.
- 대역: 없음.

### `test_query_cursor_is_bound_to_snapshot_and_query_and_has_no_empty_page` (행 143–172)
- 성질: 파일 질의 커서는 자기 스냅숏과 질의 조건에 묶이고, 변조되거나 다른 조건으로 쓰인 커서는 거부되며, 결과가 없는 질의는 빈 쪽 하나를 낸다.
- 준비: 클래스 절의 `setUp`. 내부 `_store.publish`로 `research/a.txt`(`needle alpha`), `b.txt`(`needle beta`), `c.txt`(`not here`)를 발행한다.
- 실행: `query(snapshot=head, prefix="research/", text="needle", limit=1)`로 첫 쪽을 읽고, 커서로 둘째 쪽을 읽는다. 이어서 세 가지 잘못된 커서로 질의한다. 다른 `text="other"`로 쓴 커서, 끝에 `"x"`를 붙인 커서, 위조 커서다. 위조 커서는 `snapshot`·`prefix`·`text`·`last_path="research/aa.txt"`를 `canonical_json`해 URL-safe base64로 만든다. 마지막으로 `text="absent"`로 질의한다.
- 단언: 첫 쪽은 `total=2`, 항목 1개, `truncated=True`, 커서 있음이다. 둘째 쪽은 항목 1개이고, 첫 쪽과 다른 경로이며, `truncated=False`다. 잘못된 세 커서는 모두 `RepositoryCursorError`를 던진다(유형만 본다). 빈 질의는 정확히 `{"snapshot": head, "total": 0, "items": [], "next_cursor": None, "truncated": False}`다.
- 대역: 없음.
- 비고: 제품 커서에는 서명이나 무결성 검사가 없다. 커서는 네 필드를 `canonical_json`해 URL-safe base64로 적은 값일 뿐이다(`repository.py`의 `_encode_cursor`, `_decode_cursor`). 위조 커서는 이 모양을 그대로 갖추므로 복호화와 모양 검사를 통과한다. 거부는 `last_path`인 `research/aa.txt`가 질의 결과에 없기 때문에 난다(`query`의 `"cursor path is not present in this query result"`). 테스트는 예외 유형만 보므로 이 사유를 고정하지 않는다.

### `test_list_files_prefix_and_read_reject_implicit_missing_snapshot` (행 174–179)
- 성질: 파일 목록은 접두사 아래의 실제 저장 파일만 내고, 저장 이름 공간 밖의 접두사는 거부한다.
- 준비: 클래스 절의 `setUp`.
- 실행: `list_files("research/")`, `list_files("runtime/")`, `list_files("../")`.
- 단언: `research/` 목록에 `research/_state/metadata.json`이 있고, 옛 형식 이름 `research/instance.json`은 없다. `runtime/` 목록에 `runtime/_state/metadata.json`이 있다. `"../"`는 `ValueError`를 던진다(유형만 본다).
- 대역: 없음.
- 비고: 이름은 "read가 암묵적인 없는 스냅숏을 거부한다"를 말하지만, 이 테스트는 `read`를 부르지 않고 스냅숏도 지정하지 않는다. 단언은 목록의 내용과 접두사 거부만 확인한다.

### `test_duplicate_json_keys_are_rejected_on_load` (행 181–186)
- 성질: 저장된 JSON에 중복 키가 있으면 적재가 거부한다.
- 준비: 클래스 절의 `setUp`. `_store.publish`로 `research/_state/metadata.json`을 `{"name":"first","name":"second"}`로 덮은 커밋을 만든다.
- 실행: `load(bad_head)`.
- 단언: `ValueError`를 던진다(유형만 본다).
- 대역: 없음.

### `test_export_refuses_nonempty_or_reparse_destination_and_preserves_prefix` (행 188–211)
- 성질: 내보내기는 접두사 경로 구조를 그대로 쓰고, 비어 있지 않은 목적지와 재분석 지점(심볼릭 링크·접합) 목적지를 거부한다.
- 준비: 클래스 절의 `setUp`.
- 실행: `export(self.root/"export", prefixes=("research/",))`, 같은 목적지로 한 번 더. 이어서 `target` 폴더를 만들고 `reparse-export`를 그 폴더로 잇는 디렉터리 심볼릭 링크를 만든다. 권한이 없어 `os.symlink`가 `OSError`를 내면 `cmd.exe /d /c mklink /J`로 접합을 만든다. 그 링크를 목적지로 내보낸다.
- 단언: 첫 내보내기의 `snapshot`이 `initial_head`이고, `files`가 `list_files("research/")`와 같으며, 내보낸 `research/_state/metadata.json` 바이트가 저장소의 바이트와 같다. 같은 목적지로 다시 내보내면 `ValueError`가 난다. 접합 생성이 실패하면 그 종료 코드를 단언하며 stderr를 보인다. 링크 목적지는 `ValueError`로 거부된다.
- 대역: 없음.
- 비고: 심볼릭 링크 권한이 없는 Windows에서는 실제 `cmd.exe` 자식 프로세스로 접합을 만든다.

### `test_new_id_is_canonical_ulid_and_canonical_json_is_stable` (행 213–216)
- 성질: 새 ID는 접두사가 붙은 정규 ULID이고, 정규 JSON은 정해진 바이트 모양을 낸다.
- 준비: 없음(1단).
- 실행: `new_id("RI")`, `canonical_json({"b": 1, "a": [True, None]})`.
- 단언: ID가 `^RI-[0-7][0-9A-HJKMNP-TV-Z]{25}$`에 맞는다(Crockford base32, 첫 글자는 0–7). 직렬화 결과가 키 정렬, 두 칸 들여쓰기, 끝 줄바꿈을 가진 정확한 바이트 `b'{\n  "a": [\n    true,\n    null\n  ],\n  "b": 1\n}\n'`다.
- 대역: 없음.
- 비고: 클래스 `setUp`의 저장소는 쓰지 않는다.

## ValidatedReadReuseTests (행 219–330)

`unittest.TestCase`를 그대로 상속하고 표지와 클래스 속성이 없다. 클래스 docstring은 "같은 사실의 재검사를 읽기에서 뺀다: 자기 머리, 공유 머리, 맞춘 바이트"라고 밝힌다.

- `setUp` (행 222–233): 임시 폴더를 `git_init`하고(정리는 `addCleanup`), `new_id("RI")`로 인스턴스를 연다. 상태는 `initialization.initialize_state`로 만든다. 목표는 `"G"`, 작업 공간은 `root/"work"`, 빈 설정이고, 원 입력 `source_input`은 `"x"*70000`이다. 행 230의 주석대로 큰 원 입력은 봉인된 payload blob으로 저장된다. 이 상태로 `initialize`한 커밋이 `self.head`다.
- `counters` (행 235–243): `ExitStack`에 두 패치를 넣어 `(stack, decode, validate)`를 돌려준다. `repository._decode_families`는 `wraps`로 감싸고, `StateContract.validate`는 `autospec=True, side_effect=StateContract.validate`로 감싸 호출을 센다.
- `outside_head` (행 245–247): 다른 작성자가 발행한 머리를 흉내 낸다. 같은 상태에 `runtime/artifacts/<bundle>/note.bin` 파일 하나를 더해 내부 `_store.publish`로 발행한 커밋이다(docstring: "같은 상태 + 산출물 묶음 하나").

### `test_own_publication_is_not_revalidated_but_an_outside_head_is` (행 249–267)
- 성질: 이 프로세스가 발행한 머리는 적재할 때 다시 풀거나 검증하지 않지만, 바깥에서 발행된 머리는 한 번 푼다. 돌려준 보기(view)는 공유 캐시와 분리되어 있다.
- 준비: 클래스 절의 `setUp`. 적재한 runtime에 `cycles=1`을 둔다.
- 실행: 계수 패치 안에서 `save_with_state`, 새 머리의 `load`, `view(new_head)`. 이어서 반환된 runtime의 `cycles`를 99로 바꾸고 다시 적재한다. `load_records(new_head)`에서 `lifecycle` 가족 행을 센다. `outside_head(new_head, "BA-outside")`를 만들어 새 계수 패치 안에서 적재한다.
- 단언: `view`의 `cycles`가 1이다. 첫 계수는 `(decode, validate) = (0, 1)`이다. 행 257의 주석대로 1은 후보 검사 한 번뿐이다. 적재한 `cycles`가 1이다. 반환된 보기를 바꿔도 다시 적재한 값은 1이다. `lifecycle` 행이 1개다. 바깥 머리의 적재는 `cycles=1`을 내고, 계수는 `(1, 1)`이다.
- 대역: `counters`의 두 감싸기 패치.

### `test_one_head_is_validated_once_across_repository_objects` (행 269–278)
- 성질: 한 머리의 검증된 읽기는 같은 계약을 쓰는 저장소 객체들 사이에서 공유되고, 다른 계약은 따로 검증한다.
- 준비: 클래스 절의 `setUp`. `outside_head(self.head, "BA-shared")`.
- 실행: 계수 패치 안에서 새 `ResearchRepository` 두 개로 바깥 머리를 적재하고, `installed_contract()`를 준 셋째 객체로 한 번 더 적재한다.
- 단언: 두 객체의 적재 뒤 `_decode_families` 호출이 1회다. 다른 계약의 객체가 적재한 뒤에는 2회다(행 278 주석: "다른 계약은 다른 검증").
- 대역: `counters`.

### `test_payload_bytes_are_hashed_once_per_repository` (행 280–289)
- 성질: 봉인된 payload 바이트는 저장소마다 한 번만 해시되고, 뒤의 적재에서 다시 해시되지 않는다.
- 준비: 클래스 절의 `setUp`. `_read_documents(self.head)[3]`에서 `runtime/artifacts/payload-`로 시작하는 파일이 정확히 하나임을 확인하고 그 바이트를 얻는다. `outside_head(self.head, "BA-payload")`.
- 실행: `hashlib.sha256`을 `wraps`로 감싼 채 바깥 머리를 적재한다.
- 단언: 적재한 `lifecycle.immutable_input.text`의 길이가 70000이다. `sha256`이 그 payload 바이트를 첫 인자로 받은 호출이 없다.
- 대역: `patch.object(hashlib, "sha256", wraps=hashlib.sha256)`.
- 비고: 이름은 "저장소마다 한 번"을 말한다. 단언은 첫 해시(초기화 때)를 세지 않고, 바깥 머리의 적재에서 다시 해시하지 않는다는 것만 본다.

### `test_evidence_rows_are_read_once_and_new_rows_are_still_matched` (행 291–304)
- 성질: 이미 맞춘 산출물 증거 행은 다른 머리에서도 다시 읽지 않고, 해시가 다른 행은 여전히 거부된다.
- 준비: 클래스 절의 `setUp`. `runtime/artifacts/BA-evidence/observation.json`을 저장한다. 지역 함수 `rows(digest)`는 체크포인트 `CP-1`의 증거 파일 행 하나를 담은 runtime 조각을 만든다.
- 실행: `_store.read_many`를 감싼 채 `_validate_artifact_evidence(rows(digest), head)`와, 바깥 머리(`BA-evidence-2`)에 대한 같은 호출. 이어서 `rows("0"*64)`로 호출한다.
- 단언: 두 호출에서 `read_many`가 1번만 불렸다. 틀린 해시는 `ValueError`를 `"hash differs"`로 던진다.
- 대역: `read_many` 감싸기.
- 비고: 이름의 "새 행은 여전히 맞춘다"는 해시가 다른 행이 캐시로 통과하지 않음을 뜻한다. 단언은 거부만 본다.

### `test_unchanged_records_skip_record_local_and_immutable_hash_checks` (행 306–330)
- 성질: 부모와 같은 레코드는 레코드 단위 검증기와 불변 원 입력 해시 검사를 건너뛰고, 바뀌거나 새로 생긴 레코드만 검사된다.
- 준비: 클래스 절의 `setUp`. `installed_contract()`의 `governance_sources` 검증기를 `counted`로 감싼다. `counted`는 레코드 ID를 `checked`에 적고 원래 검증기를 부른다. 교체에는 `with_validator`를 쓰고, 그 계약으로 저장소를 연다.
- 실행: (1) `governance.preserve_source`로 `GS-1`을 더해 저장한다. (2) `GS-2`를 더하고 `cycles=1`로 두어, `initialization.original_input_bytes`를 감싼 채 저장한다. (3) `sha256`을 `"0"*64`로 바꾼 `GS-3`을 더해 저장한다.
- 단언: (1) 뒤 `checked`가 `["GS-1"]`이다. (2) 뒤 `["GS-1", "GS-2"]`이고(`GS-1`은 다시 검사되지 않음), `original_input_bytes` 호출이 0회다. (3)은 `ValueError`를 `"immutable source"`로 던진다.
- 대역: `with_validator`로 바꾼 가족 검증기, `original_input_bytes` 감싸기.
- 비고: 제품 `StateContract.validate` docstring은 부모와 같은 레코드가 레코드 단위 검사(스키마와 가족 검증기)를 건너뛴다고 밝힌다.

## SaveWithStateTests (행 333–427)

`unittest.TestCase`를 그대로 상속하고 표지와 클래스 속성이 없다.

- `setUp` (행 334–341): `ResearchRepositoryTests.setUp`과 같다. `repository` 폴더를 `git_init`하고 `INSTANCE_ID`로 열어 `current_state({"title": "instance"})`로 `initialize`한다.
- `tearDown` (행 343–344): 임시 폴더를 정리한다.

### `test_unchanged_state_is_noop_and_returns_normalized_reload_views` (행 346–352)
- 성질: 바뀌지 않은 상태의 저장은 새 커밋을 만들지 않고, 다시 적재한 것과 같은 정규화된 보기를 돌려준다.
- 준비: 클래스 절의 `setUp`.
- 실행: `load()` 뒤 그대로 `save_with_state`, 그 머리의 `load`.
- 단언: 저장이 돌려준 머리가 원래 머리와 같다. 저장의 세 반환값이 다시 적재한 세 값과 같다.
- 대역: 없음.

### `test_changed_state_writes_the_same_canonical_files_and_returns_reload_views` (행 354–362)
- 성질: 바뀐 상태의 저장은 후보 검증이 계산한 정규 파일을 그대로 쓰고, 다시 적재한 것과 같은 보기를 돌려준다.
- 준비: 클래스 절의 `setUp`. runtime `status`를 `running`으로 바꾼 사본.
- 실행: `validate_candidate(instance, changed_runtime, head)`로 기대 파일을 얻고, `save_with_state`한 뒤 `_store.read_many(saved_head, 정렬한 경로)`로 저장된 바이트를 읽는다.
- 단언: 새 머리가 원래 머리와 다르다. 저장된 바이트가 기대 파일과 같다. 저장의 반환값이 새 머리를 적재한 결과와 같다.
- 대역: 없음.

### `test_regular_save_still_rejects_invalid_input` (행 364–369)
- 성질: 일반 저장도 잘못된 입력을 거부하고 머리를 옮기지 않는다.
- 준비: 클래스 절의 `setUp`. runtime `status`를 `float("nan")`으로 둔다.
- 실행: `save_with_state`.
- 단언: `ValueError`를 던지고(유형만 본다) 현재 머리가 그대로다.
- 대역: 없음.

### `test_save_reads_parent_family_bytes_once_and_preserves_reload_equivalence` (행 371–376)
- 성질: 저장은 부모 머리의 가족 바이트를 Git에서 다시 읽지 않고, 반환값은 다시 적재한 값과 같다.
- 준비: 클래스 절의 `setUp`.
- 실행: `_store.read_many`를 감싼 채 `status=running`으로 저장한다.
- 단언: 첫 인자가 부모 `head`인 `read_many` 호출이 0회다. 저장 결과가 새 머리의 적재 결과와 같다.
- 대역: `read_many` 감싸기.
- 비고: 이름은 "한 번 읽는다"를 말하지만 단언은 이 저장 호출 안에서 0회를 요구한다. 부모 머리의 검증된 읽기는 `setUp`의 `initialize`가 `_remember_published`로 캐시에 넣은 것이다. 그래서 앞선 `load`도 Git에서 읽지 않고, 이 테스트 안에서 부모 바이트를 Git에서 읽는 호출은 한 번도 없다. 이름의 "한 번"에 대응하는 읽기는 원문에 없다.

### `test_save_rereads_only_new_artifact_evidence` (행 378–392)
- 성질: 저장은 이미 맞춘 산출물 증거를 다시 읽지 않지만, 증거 행이 바뀌면 거부한다.
- 준비: 클래스 절의 `setUp`. runtime에 체크포인트 `EX-evidence`의 증거 파일 행 하나(`AB-evidence/notes.txt`)를 두고 그 바이트와 함께 저장한 뒤 다시 적재한다.
- 실행: `read_many`를 감싼 채 `status=running`으로 저장한다. 이어서 그 결과의 증거 행 `bytes`를 1 늘려 저장한다.
- 단언: 어떤 `read_many` 호출의 경로 목록에도 그 증거 경로가 없다. 저장 결과가 다시 적재한 값과 같다. 바뀐 증거는 `ValueError`를 `"artifact evidence"`로 던진다.
- 대역: `read_many` 감싸기.

### `test_reused_parent_bytes_still_reject_a_damaged_previous_snapshot` (행 394–401)
- 성질: 부모 바이트를 재사용하더라도 손상된 이전 스냅숏 위에는 저장하지 않는다.
- 준비: 클래스 절의 `setUp`. `_store.publish`로 `runtime/_state/metadata.json`을 `{}\n`로 덮은 손상 커밋을 만든다.
- 실행: `_store.publish`를 감싼 채 손상 커밋을 부모로 `save_with_state`.
- 단언: `ValueError`를 던진다(유형만 본다). `publish`가 불리지 않았다. `_store.read_snapshot().head`가 여전히 손상 커밋이다.
- 대역: `publish` 감싸기.

### `test_stale_head_is_rejected_before_artifact_shape` (행 403–409)
- 성질: 낡은 머리는 산출물 경로 모양 검사보다 먼저 충돌로 거부된다.
- 준비: 클래스 절의 `setUp`. `status=running`으로 한 번 저장해 머리를 전진시킨다.
- 실행: 옛 머리에서, 산출물 이름 공간 밖의 `outside-artifacts.txt`와 함께 저장한다.
- 단언: `GitStateStoreConflict`를 던진다. 산출물 경로 오류(`ValueError`)가 아니라 충돌이 먼저라는 것을 예외 유형으로 고정한다.
- 대역: 없음.

### `test_artifact_bytes_and_namespace_are_checked_by_the_same_save_call` (행 411–427)
- 성질: 산출물 바이트와 산출물 이름 공간은 같은 저장 호출에서 검사되고, 이름 공간 밖의 산출물은 머리를 옮기지 않은 채 거부된다.
- 준비: 클래스 절의 `setUp`.
- 실행: `AB-01/output.txt`(`b"sealed artifact bytes"`)와 함께 저장한다. 다시 적재한 뒤 사본 상태와 `outside-artifacts.txt`로 저장한다.
- 단언: 저장한 산출물의 바이트가 같다. 둘째 저장이 `ValueError`를 던진다(유형만 본다). 현재 머리가 첫 저장의 커밋이다.
- 대역: 없음.

## CandidateCopyTests (행 430–450)

`unittest.TestCase`를 그대로 상속한다. 표지, 속성, 훅, 도우미가 없다.

### `test_candidate_numbers_events_without_a_second_whole_state_copy` (행 431–441)
- 성질: 후보 검증은 각 루트 상태를 한 번씩만 복사하고, 그 분리된 사본에 사건 번호를 매기며, 호출자의 원본은 그대로 둔다.
- 준비: `current_state`에 `title`과 사건 하나(`EV-1`, `created`)를 더한 상태. 비교용 `deepcopy`.
- 실행: `repository.deepcopy`를 `wraps`로 감싼 채 `candidate_repository(self).validate_candidate(instance, runtime)`.
- 단언: `deepcopy`가 받은 첫 인자 목록이 정확히 `[instance, runtime]`이다. 원본이 사본과 같다. 후보 runtime의 첫 사건에 `event_seq=1`이 매겨졌다. 반환된 후보를 바꿔도 원본은 그대로다.
- 대역: `patch.object(repository, 'deepcopy', wraps=deepcopy)`.
- 비고: 행 436의 주석은 "루트마다 사본 하나, 사건 번호 매기기는 그 분리된 사본에서 한다"고 밝힌다.

### `test_late_event_failure_never_numbers_the_callers_original` (행 443–450)
- 성질: 사건 번호 검사가 늦게 실패해도 호출자의 원본에는 번호가 매겨지지 않는다.
- 준비: 사건 두 개. `EV-1`은 번호가 없고, `EV-2`는 `event_seq=99`다.
- 실행: `candidate_repository(self).validate_candidate`.
- 단언: `ValueError`를 `'contiguous'`로 던지고, 원본이 사본과 같다.
- 대역: 없음.

## StorageValueTests (행 453–492)

`unittest.TestCase`를 그대로 상속한다. 표지, 속성, 훅, 도우미가 없다.

### `test_value_validation_and_serialization_keep_the_same_domain` (행 454–470)
- 성질: 저장 값 검증(`validate_storage_value`)과 정규 직렬화(`canonical_json`)는 같은 값 영역을 받아들이고, 같은 메시지로 거부한다.
- 준비: 유효 값 7개와 무효 값 12개. 유효 값은 `None`, `True`, `False`, `0`, `±(2**53−1)`, 그리고 NFD `'é'` 키와 NFC `'é'` 키, 한글, 이모지를 담은 사전이다. 무효 값은 `0.0`, NaN, ±무한대, `2**53`, `-(2**53)`, 짝 없는 서로게이트 `'\ud800'`, 정수 키 사전, 서로게이트 키 사전, `bytes`, 튜플, 중첩 부동소수다.
- 실행: 값마다 두 함수를 부른다.
- 단언: 유효 값은 검증이 `None`을 돌려주고 직렬화가 `bytes`를 낸다. 무효 값은 두 함수가 모두 `ValueError`를 던지고, 두 메시지 문자열이 같다. 끝으로 `True`와 `1`의 직렬화가 다르고, 목록 순서가 다르면 직렬화도 다르다.
- 대역: 없음.
- 비고: `subTest`로 유효 7건, 무효 12건을 나눈다. 정수 경계는 JavaScript 안전 정수 범위(±(2**53−1))다.

### `test_inspection_builds_no_json_bytes_and_publication_checks_the_value_domain` (행 472–480)
- 성질: 상태 점검은 JSON 바이트를 만들지 않고, 저장 값 영역은 적재와 발행(후보 검증)이 검사한다.
- 준비: 원천 없는 instance와 출력 파일 없는 실행 하나의 runtime. 이어서 `current_state`의 runtime에 `provider_wake.measured=NaN`.
- 실행: `repository.canonical_json`이 불리면 실패하게 한 채 `inspect_state(..., requested_areas=['record_storage'])`. 이어서 `candidate_repository(self).validate_candidate`.
- 단언: 점검 `status`가 `healthy`이다(직렬화가 불리지 않음). 후보 검증은 `ValueError`를 `'floating-point'`로 던진다.
- 대역: `patch.object(repository, 'canonical_json', side_effect=AssertionError('unused serialization'))`.
- 비고: 행 476–477의 주석은 "저장 값 영역은 적재와 발행의 몫이다. 후보를 위해 직렬화되는 레코드마다 저장 값 검사를 통과한다"고 밝힌다.

### `test_a_float_equal_to_the_parent_integer_is_still_rejected` (행 482–492)
- 성질: 부모의 정수와 같은 부동소수(`1.0 == 1`)도 저장에서 거부되고 머리는 그대로다.
- 준비: 새 임시 폴더를 `git_init`하고 `new_id('RI')`로 연 저장소에 `provider_wake.measured=1`인 상태를 `initialize`한다. 적재한 뒤 값을 `1.0`으로 바꾼다.
- 실행: `save_with_state`.
- 단언: `ValueError`를 `'floating-point'`로 던지고, 현재 머리가 초기 머리다.
- 대역: 없음.
- 비고: 행 483–484의 주석은 이렇게 밝힌다. "`1.0 == 1`이므로 레코드가 부모와 같아 스키마 검사와 직렬화를 건너뛴다. 후보를 봉인할 때 부동소수를 먼저 거부한다." 제품 `StateContract.validate` docstring의 같은 설명(`payloads.seal_large`가 비교 전에 모든 부동소수를 거부)과 짝을 이룬다.

## SealedArtifactReadTests (행 495–511)

`unittest.TestCase`를 그대로 상속한다. 표지, 속성, 훅, 도우미가 없다.

### `test_a_sealed_row_is_hashed_once_and_matched_rows_are_not_reread` (행 496–511)
- 성질: 봉인된 산출물 행은 해시가 맞을 때 한 번만 해시되어 기억되고, 뒤의 읽기는 다시 해시하지 않으며, 바이트가 필요 없으면 읽지도 않는다. 해시가 다른 행은 거부된다.
- 준비: `bare_engine(head='a'*40, store=create_autospec(ResearchRepository, instance=True))`. 저장소 대역의 `git_dir`은 무작위 이름(`'git-'+uuid`)이고, `read`는 `b'sealed bytes'`를 돌려준다.
- 실행: `engine._sealed_bytes(path, 'b'*64, len(raw))`, 올바른 해시로 한 번, `repository.hashlib.sha256`이 불리면 실패하게 한 채 올바른 해시로 한 번, 읽기 대역을 초기화한 뒤 `needed=False`로 한 번.
- 단언: 틀린 해시는 `ValueError`를 `'differs from its record'`로 던진다. 올바른 해시는 `raw`를 돌려준다. 셋째 호출도 해시 없이 `raw`를 돌려준다. `needed=False`는 `None`을 돌려주고 `read`를 부르지 않는다.
- 대역: `bare_engine`, `create_autospec(ResearchRepository, instance=True)`, `patch.object(repository.hashlib, 'sha256', side_effect=AssertionError('matched row rehashed'))`.
- 비고: 맞춘 행의 기억은 프로세스 전역 사전 `repository.VERIFIED_ARTIFACTS`에 `(git_dir, 경로, sha256)` 키로 남는다(제품 `sealed_bytes` docstring: "프로세스마다 한 번"). 이 테스트는 `git_dir`을 무작위 이름으로 두므로 같은 프로세스의 다른 시험이 남긴 항목과 키가 겹치지 않는다. 원문에 이 선택의 이유를 밝힌 주석은 없다.

## 관계

- Git 객체 층(`GitStateStore`)의 발행, CAS, 경로 규칙, 물리 경계는 `test_git_store`가 검사한다. 이 모듈은 그 위의 `ResearchRepository` 층을 본다. 여러 테스트가 저장소의 `_store.publish`를 직접 불러 손상 커밋이나 바깥 머리를 만든다.
- 상태 계약의 등록과 검증 규칙은 `test_state_contract`가, 적재 뒤 점검은 `test_state_checks`가 검사한다. `ValidatedReadReuseTests`는 그 계약의 "계약 객체별 검증된 읽기 캐시" 규칙을 저장소 층에서 확인한다.
- 질의 커서의 엔진 층 계약은 `test_query_records`가, CLI 층 출처는 `test_cli_surface`가 검사한다.
- 문자열 코드 포인트 보존은 `test_unicode_flow`가, 보관본의 봉인된 행 재사용(`sealed_bytes`, `git_dir`)은 `test_retention`의 `test_cleanup_hashes_local_files_and_archive_rows_once`가 같은 장치로 검사한다.
- 픽스처 의존: `research_fixtures.bare_engine`, `current_state`, `git_init`, `installed_contract`, `with_validator`.
- 이 모듈에만 있는 도우미: 모듈 함수 `candidate_repository`, 클래스 도우미 `counters`, `outside_head`.
