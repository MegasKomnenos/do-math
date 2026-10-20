# test_git_store

| 항목 | 값 |
|---|---|
| 조각 | `foundation` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_git_store.py` (575행) |
| 클래스 / 테스트 | 4 / 31 |
| 시험 대상 제품 코드 | `do_math/git_store.py`의 `GitStateStore`(`publish`, `read_snapshot`, `read_bytes`, `read_many`, `tree_paths`, `writer_lock`, `validate_oid`, `validate_candidate_paths`, `_write_object`, `_git`, `_published`·`_read` 트리 캐시, `_repository_boundary`·`_git_boundary`, `git_dir`, `ref`, `object_format`, `oid_length`), `oid_shape`, `PhysicalBoundary`(`open`, `check`), `StateSnapshot`, `GitStateStoreError`, `GitStateStoreConflict` |
| 사용하는 픽스처 모듈 | `research_fixtures`: `git_init` |
| 격리 표지 | 없음 |
| 시작 상태 | 모든 테스트가 실제 Git 저장소를 쓴다(네 단 밖: 실제 Git 저장소). 대부분 `git_init`으로 만든 빈 sha1 저장소 위의 `GitStateStore`에서 시작하고, sha256 저장소는 `git init --object-format=sha256` 자식 프로세스로 만든다. `SnapshotMetadataTests`는 `_git`을 대역으로 바꿔 Git 응답을 흉내 낸다 |

## 목적

모듈 docstring은 "새 저장소에서 하는 불변 Git 객체 상태 저장의 통합 시험"이라고 밝힌다. 제품 `git_store.py`의 docstring은 이 저장소가 "하나의 불변 do-math 인스턴스 상태 사슬을 위한 Git plumbing 저장"이라고 밝힌다. 이 저장소는 바이트와 Git 객체 관계만 발행한다. 레코드 스키마 검증과 인스턴스 활성화 같은 의미 판단은 위층의 몫이다. `publish`의 docstring에 따르면 커밋은 부모가 정확히 하나(초기 커밋은 없음)이다. 객체는 프로세스 안에서 쓰고, 참조(`refs/heads/do-math/<인스턴스>`)는 마지막 `update-ref` 비교-교환(CAS) 하나로만 옮긴다.

이 모듈은 다섯 무리의 계약을 검사한다.

1. 객체 쓰기의 경제성: 객체를 프로세스 안에서 쓴다. 부모 트리를 이 저장소 객체가 이미 알고 있으면 발행의 Git 자식 프로세스는 `update-ref` 하나다. 모르는 부모 트리는 `ls-tree` 한 번으로 읽어 캐시한다(`_tree`). 발행 밖의 Git 호출도 있다. 생성자는 `rev-parse`를, 읽기는 `cat-file`을 자식 프로세스로 돌린다.
2. 발행의 원자성과 충돌: CAS, 동시 작성자, 쓰기 잠금.
3. 경로 규칙: 파일·디렉터리 겹침, 대소문자 충돌, Windows 예약 이름, 유니코드 보존.
4. 물리 경계: 접합과 심볼릭 링크 거부, 열린 핸들의 경계 확인.
5. 저장소 격리: 작업 트리와 기본 색인, 훅.

`InProcessObjectsMatchGitPlumbingTests`는 프로세스 안 작성기를 Git 자신의 plumbing과 차등 비교(differential check)한다. `SnapshotMetadataTests`는 스냅숏 메타데이터를 한 번의 배치 질의로 읽는 규칙을 대역으로 검사한다.

## 모듈 수준 요소

- `SCRIPTS` (행 16): 스킬의 `scripts/` 폴더. 행 17–18에서 `sys.path`에 없으면 맨 앞에 넣는다.
- `git_result(returncode, stdout=b'', stderr=b'')` (행 24–25): `subprocess.CompletedProcess(['git'], ...)`를 만드는 대역 응답. `SnapshotMetadataTests.store`와 그 클래스의 테스트가 쓴다.
- `INSTANCE_ID` (행 28): `"RI-"` 뒤에 0이 26개인 인스턴스 ID. `SnapshotMetadataTests`를 뺀 모든 클래스가 쓴다.
- `git(repository, *arguments, input=None, env=None)` (행 31–40): 실제 `git -C <저장소> ...` 자식 프로세스를 `check=True`로 돌리고 stdout 바이트를 돌려준다. `env`를 주면 현재 환경에 덧씌운다. 시험이 제품을 거치지 않고 Git의 실제 상태를 확인하는 오라클이다. `loose_objects`, 여러 `GitStateStoreTests` 테스트, `GitStateStoreSha256Tests`, `InProcessObjectsMatchGitPlumbingTests`가 쓴다.
- `loose_objects(repository)` (행 43–46): `git rev-parse --git-path objects`로 객체 폴더를 찾아, `??/*` 모양의 느슨한(loose) 객체 파일 가운데 `tmp_obj_`로 시작하지 않는 경로의 집합을 돌려준다. `test_publication_writes_objects_in_process_and_moves_the_ref_only_by_cas`만 쓴다.
- 행 574–575: 직접 실행하면 `unittest.main(verbosity=2)`로 이 모듈의 시험을 돈다.

## GitStateStoreTests (행 49–384)

`unittest.TestCase`를 그대로 상속하고 표지와 클래스 속성이 없다.

- `setUp` (행 50–55): 임시 폴더 아래 `repository` 폴더를 만들어 `git_init`하고, `GitStateStore(self.repository, INSTANCE_ID)`를 `self.store`로 둔다. 생성자는 `git rev-parse` 자식 프로세스로 Git 디렉터리, 객체 형식, 객체 경로를 확인한다.
- `tearDown` (행 57–58): 임시 폴더를 정리한다.
- `initial_changes` (행 60–64): 최소 상태 두 파일. `research/instance.json`(`{"revision": 1}`)과 `runtime/state.json`(`{"state": "initializing"}`)이다. 제품 `publish`는 `research/`와 `runtime/` 두 하위 트리를 모두 요구한다.
- `forget_trees` (행 74–75): 저장소의 트리 캐시 `_published`와 `_read`를 `None`으로 비운다. 다음 트리 조회가 Git의 `ls-tree`를 거치게 하려는 도우미다. 원문에서는 첫 테스트 뒤에 놓여 있다.

### `test_oid_shape_is_separate_from_instance_format` (행 66–72)
- 성질: OID의 모양 판정(`oid_shape`)은 저장소의 객체 형식과 따로이고, 저장소는 자기 형식에 맞는 OID만 받는다.
- 준비: 클래스 절의 `setUp`(sha1 저장소).
- 실행: `oid_shape("a"*64)`, `store.validate_oid("a"*64)`, `oid_shape("A"*40)`.
- 단언: 64자 소문자 16진수는 `"sha256"` 모양이다. sha1 저장소의 `validate_oid`는 그것을 `ValueError`로 거부한다. 대문자 40자는 `oid_shape`가 `ValueError`로 거부한다. 모두 예외 유형만 본다.
- 대역: 없음.

### `test_tree_cache_reuses_only_immutable_oids` (행 77–84)
- 성질: 커밋의 트리 목록은 OID로 캐시되어 같은 커밋을 다시 물을 때 Git을 부르지 않는다.
- 준비: 클래스 절의 `setUp`. `initial_changes`로 발행한 뒤 `forget_trees`로 캐시를 비운다.
- 실행: `_git`을 `wraps`로 감싼 채 `tree_paths(head)`를 두 번 부른다.
- 단언: 두 결과가 같고, `ls-tree` 호출이 1회다.
- 대역: `patch.object(store, '_git', wraps=store._git)`.
- 비고: 이름의 "불변 OID만 재사용"은 캐시 키가 커밋 OID라는 뜻이다. 단언은 재사용 횟수만 본다.

### `test_own_publication_lists_the_new_tree_without_enumerating_it` (행 86–100)
- 성질: 자기가 발행한 트리는 항목별로 알고 있으므로 `ls-tree`로 나열하지 않는다. 옛 스냅숏을 읽어도 방금 발행한 트리 캐시가 밀려나지 않는다.
- 준비: 클래스 절의 `setUp`. `initial_changes`에 `runtime/artifacts/one/a.bin`을 더해 발행한다.
- 실행: `_git`을 감싼 채 파일 삭제(`runtime/state.json: None`), 새 파일, 새 묶음 파일을 한 번에 발행하고 `tree_paths(later)`를 부른다. 옛 머리의 `tree_paths`를 한 번 부른 뒤, 다시 `_git`을 감싼 채 `later` 위에 발행한다. 끝으로 `forget_trees` 뒤 `tree_paths(later)`를 부른다.
- 단언: 첫 구간에서 `ls-tree` 호출이 0회다(행 92 주석: 부모 목록도 자기 발행에서 왔다). 셋째 발행의 Git 호출 목록이 `['update-ref']` 하나다(행 94 주석: 옛 스냅숏 읽기가 방금 발행한 트리를 밀어내지 않는다). 캐시를 비운 뒤 Git이 나열한 목록이 발행 직후의 목록과 같다.
- 대역: `_git` 감싸기.

### `test_publication_writes_objects_in_process_and_moves_the_ref_only_by_cas` (행 102–113)
- 성질: 발행은 객체를 프로세스 안에서 쓰고 새 객체마다 fsync하며, Git 자식 프로세스는 참조를 옮기는 CAS 하나뿐이다.
- 준비: 클래스 절의 `setUp`. 첫 발행 뒤 `loose_objects`로 객체 집합을 떠 둔다.
- 실행: `_git`과 `do_math.git_store.os.fsync`를 감싼 채, 파일 하나를 고치고 깊은 새 경로 `research/new/deep.json`을 더해 발행한다.
- 단언: Git 호출 목록이 `['update-ref']`다. `fsync` 호출 수가 새로 생긴 느슨한 객체 수와 같다. 새 머리에서 `research/new/deep.json`을 읽으면 `b'{}\n'`이다.
- 대역: `_git` 감싸기, `patch('do_math.git_store.os.fsync', wraps=os.fsync)`.
- 비고: 행 110의 주석은 "설치된 Git for Windows는 새 느슨한 객체마다 flush한다(`core.fsyncObjectFiles=true`)"고 밝힌다. 제품 `_write_object` docstring도 같은 근거를 적는다.

### `test_concurrent_writers_of_one_object_all_succeed` (행 115–134)
- 성질: 같은 객체를 동시에 쓰는 작성자들은 모두 성공하고 같은 OID를 얻으며, 임시 파일을 남기지 않는다.
- 준비: 클래스 절의 `setUp`. 스레드 4개와 `threading.Barrier(4)`.
- 실행: 각 스레드가 장벽을 지난 뒤 `_write_object(b"blob", b"same bytes %d\n" % n)`을 `n = 0..19`에 대해 부른다. 스레드는 각각 20초 상한으로 `join`한다.
- 단언: 결과 목록이 4개이고, 네 OID 목록이 모두 같다. 실제 `git cat-file --batch-check`에 첫 목록을 주면 `blob`이 20번 나온다. 객체 폴더에 `tmp_obj_*` 파일이 남아 있지 않다.
- 대역: 없음.
- 비고: 실제 스레드 동시성과 실제 Git 자식 프로세스를 쓴다. 제품 docstring은 "같은 객체의 동시 작성자는 마지막 rename만 진다"고 밝힌다.

### `test_path_that_is_also_a_directory_is_rejected_before_git_drops_it` (행 136–142)
- 성질: 같은 경로가 파일이면서 디렉터리이게 되는 발행은 Git이 한쪽을 버리기 전에 거부된다.
- 준비: 클래스 절의 `setUp`. `research/a`를 파일로 가진 상태를 발행한다.
- 실행: `research/a/b`를 더해 발행한다. `validate_candidate_paths({'research/x', 'research/x/y'})`를 직접 부른다.
- 단언: 두 호출 모두 `ValueError`를 `'both a file and a directory'`로 던진다. 머리가 첫 발행 그대로다.
- 대역: 없음.

### `test_physical_boundary_is_proved_on_open_and_after_git_errors_only` (행 144–154)
- 성질: 저장소와 Git 디렉터리의 물리 경계는 열 때와 Git이 오류를 낸 뒤에만 다시 증명되고, 정상 발행과 읽기에서는 확인하지 않는다.
- 준비: 클래스 절의 `setUp`. 첫 발행.
- 실행: `_repository_boundary.check`와 `_git_boundary.check`가 `ValueError('boundary changed')`를 던지게 한 채, 발행과 `read_many`를 한다. 이어서 없는 경로를 `read_bytes`한다.
- 단언: 발행한 파일을 `read_many`로 읽은 결과가 맞다. 그동안 두 경계 확인의 호출 수가 `(0, 0)`이다. 없는 경로 읽기는 Git 오류를 낸 뒤 경계를 다시 확인하므로 `ValueError`를 `'boundary changed'`로 던진다.
- 대역: 두 `check`에 대한 `patch.object(..., side_effect=changed)`.
- 비고: 제품 클래스 docstring은 이동이나 재마운트가 Git 오류로 드러나고, 경계를 Git 프로세스마다 다시 증명하지 않는다고 밝힌다. 경로를 바꿔치는 경합은 의도적 변조로서 우발적 변경의 위협 모델 밖이다.

### `test_writer_lock_leaves_the_final_cas_as_the_only_ref_comparison` (행 156–176)
- 성질: 쓰기 잠금 아래에서는 자기가 방금 발행한 머리를 다시 읽지 않지만, 잠금 밖 작성자는 여전히 마지막 CAS에서 막힌다. 실패한 CAS는 기억한 머리가 낡았음을 증명하므로 다시 읽힌다.
- 준비: 클래스 절의 `setUp`. 첫 발행.
- 실행: `writer_lock()` 안에서 `_git`을 감싼 채 발행하고, `read_snapshot()`을 부른다. 같은 저장소를 연 둘째 `GitStateStore`가 잠금 없이 발행한 뒤, 첫 저장소가 옛 머리 위에 발행하고 `read_snapshot()`을 부른다. 잠금을 푼 뒤 `_git`을 감싸고 `read_snapshot()`을 한 번 더 부른다.
- 단언: `writer_lock()` 안에서 차례로 확인한다. (1) 발행의 Git 호출은 `['update-ref']`다. (2) `read_snapshot()`은 `StateSnapshot(later.head)`이고 Git 호출이 0회다(행 162–163 주석: 잠금 아래에서는 do-math 작성자가 참조를 옮기지 않으므로 다시 읽지 않는다). (3) 같은 저장소의 둘째 `GitStateStore`가 잠금 없이 `later` 위에 발행해 참조를 `moved`로 옮긴다. 첫 저장소가 `later` 위에 발행하면 `GitStateStoreConflict`를 `'publish compare-and-swap'`으로 던진다. (4) 그 뒤 `read_snapshot().head`가 `moved.head`다(행 172 주석). 잠금을 푼 뒤 `read_snapshot()`은 `moved.head`를 돌려주고 Git 호출이 1회다.
- 대역: `_git` 감싸기.

### `test_unicode_artifact_path_preserves_the_supplied_code_points` (행 178–183)
- 성질: 산출물 경로 이름은 주어진 코드 포인트 그대로 저장되고 정규화되지 않는다.
- 준비: 클래스 절의 `setUp`. 경로 `runtime/artifacts/one/é.txt`(NFD).
- 실행: 발행, `read_bytes`, `tree_paths`.
- 단언: 읽은 바이트가 `b"raw"`이고, 트리 목록에 NFD 경로가 있으며, NFC 경로 `runtime/artifacts/one/é.txt`는 없다.
- 대역: 없음.

### `test_many_blobs_use_no_hash_process_and_preserve_raw_bytes` (행 185–193)
- 성질: 많은 blob의 발행에 해시용 Git 프로세스를 쓰지 않고, 저장소 속성 파일과 상관없이 원시 바이트를 보존한다.
- 준비: 클래스 절의 `setUp`. 작업 트리에 `.gitattributes`(`* text eol=lf`)를 쓴다. `runtime/artifacts/batch/자료 <i>.bin` 38개를 준비한다. 각각 `bytes(range(256)) + b'\r\n\x00' + bytes([i])`다.
- 실행: `_git`을 감싼 채 발행하고, `read_many`로 모든 경로를 읽는다.
- 단언: Git 호출 목록이 `['update-ref']`다. 읽은 결과가 준비한 바이트와 정확히 같다(CRLF와 NUL 포함).
- 대역: `_git` 감싸기.
- 비고: `eol=lf` 속성은 Git의 필터가 끼면 CRLF를 바꿀 조건이다. 한글과 공백이 든 경로 이름도 함께 확인된다.

### `test_batch_read_is_exact_and_missing_blob_is_an_error` (행 195–205)
- 성질: 배치 읽기는 한 번의 Git 호출로 정확한 바이트를 돌려주고, 빈 요청은 빈 결과이며, 없는 blob은 오류다.
- 준비: 클래스 절의 `setUp`. 빈 파일 `빈 파일`과 이진 파일 `바이너리`(`b'\x00\xff\n\r\nblob missing\n'`)를 더해 발행한다.
- 실행: `_git`을 감싼 채 `read_many(head, 모든 경로)`. 빈 목록으로 `read_many`. 있는 경로와 없는 경로 `runtime/absent`를 섞어 `read_many`.
- 단언: 결과가 준비한 바이트와 같고, Git 호출이 1회다. 빈 요청은 `{}`다. 없는 경로가 섞이면 `GitStateStoreError`를 던진다(유형만 본다).
- 대역: `_git` 감싸기.
- 비고: 내용 `blob missing`은 `git cat-file --batch`가 없는 객체에 내는 응답 모양(`<이름> missing`)과 헷갈리지 않는지 보려는 값으로 보인다. 원문에 이유를 밝힌 주석은 없다.

### `test_initial_commit_has_no_parent_and_later_commit_has_one_parent` (행 207–217)
- 성질: 초기 커밋은 부모가 없고, 뒤의 커밋은 기대 머리 하나만 부모로 가진다.
- 준비: 클래스 절의 `setUp`.
- 실행: 두 번 발행하고 실제 `git rev-list --parents -n 1`로 부모를 읽는다.
- 단언: 초기 머리가 있고 길이가 40이며, 부모 목록이 자기 하나뿐이다. 뒤의 커밋은 `[자기, 초기 머리]`다.
- 대역: 없음.

### `test_runtime_only_update_preserves_research_tree_and_old_snapshot_bytes` (행 219–226)
- 성질: runtime만 바꾼 발행은 research 하위 트리 객체를 그대로 두고, 옛 스냅숏의 바이트도 그대로 읽힌다.
- 준비: 클래스 절의 `setUp`.
- 실행: 두 번 발행하고 실제 `git rev-parse <커밋>:research`로 하위 트리 OID를 읽는다.
- 단언: 두 커밋의 research 트리 OID가 같다. 옛 머리의 `runtime/state.json`은 초기 바이트이고, 새 머리의 것은 `running` 바이트다.
- 대역: 없음.

### `test_simultaneous_stale_cas_has_one_winner_and_no_overwrite` (행 228–255)
- 성질: 같은 부모에서 동시에 발행하는 두 작성자 가운데 하나만 이기고, 다른 하나는 충돌로 끝나며 덮어쓰지 않는다.
- 준비: 클래스 절의 `setUp`. 첫 발행. 스레드 둘(`left`, `right`)과 `Barrier(2)`, 결과 목록과 잠금.
- 실행: 각 스레드가 자기 `GitStateStore`를 만들고 장벽을 지난 뒤 `initial.head` 위에 `runtime/state.json`을 자기 이름으로 발행한다. 성공과 `GitStateStoreConflict`를 기록한다. 각각 20초 상한으로 `join`한다.
- 단언: 두 스레드가 끝났다. `published` 1건, `conflict` 1건이다. 현재 머리의 `runtime/state.json`이 `b"left"` 또는 `b"right"`다.
- 대역: 없음.
- 비고: 실제 스레드 경합과 실제 `update-ref` CAS를 쓴다.

### `test_publish_does_not_change_worktree_or_default_index` (행 257–270)
- 성질: 발행은 사용자의 작업 트리 파일과 기본 색인(index)을 바꾸지 않는다.
- 준비: 클래스 절의 `setUp`. 첫 발행. 작업 트리에 `user.txt`를 쓰고 실제 `git add`로 색인에 올린다. `git rev-parse --git-path index`로 색인 파일을 찾아 바이트를 떠 둔다.
- 실행: 발행.
- 단언: `user.txt`의 바이트와 색인 파일의 바이트가 그대로다.
- 대역: 없음.

### `test_publish_does_not_execute_repository_hook` (행 272–283)
- 성질: 발행은 저장소에 설정된 훅을 실행하지 않는다.
- 준비: 클래스 절의 `setUp`. `hostile-hooks/reference-transaction` 훅을 만든다. 이 훅은 실행되면 `hook-ran` 파일을 쓴다. 실행 권한 `0o755`를 주고, 실제 `git config core.hooksPath`로 그 폴더를 가리킨다.
- 실행: 발행.
- 단언: `hook-ran` 파일이 없다.
- 대역: 없음.
- 비고: 제품 `_git`은 모든 Git 호출에 `-c core.hooksPath=<git_dir>/do-math-disabled-hooks`를 붙이고, 시스템·전역 설정을 끈다(`GIT_CONFIG_NOSYSTEM`, `GIT_CONFIG_GLOBAL`).

### `test_writer_lock_is_an_os_lock_without_stale_pid_contents` (행 285–290)
- 성질: 쓰기 잠금은 OS 잠금이고, 잠금 파일에 낡을 수 있는 PID 내용을 남기지 않는다.
- 준비: 클래스 절의 `setUp`.
- 실행: `writer_lock()` 안에서 발행한다.
- 단언: `git_dir/do-math-<INSTANCE_ID>.lock`의 바이트가 `b"\0"` 한 바이트다. 머리가 발행한 커밋이다.
- 대역: 없음.

### `test_existing_artifact_bundle_cannot_be_changed_or_deleted` (행 292–301)
- 성질: 이미 있는 산출물 묶음의 파일은 바꾸거나 지울 수 없다.
- 준비: 클래스 절의 `setUp`. `runtime/artifacts/bundle_01/output.txt`를 가진 상태를 발행한다.
- 실행: 그 파일을 다른 바이트로 바꾸는 발행과, `None`으로 지우는 발행.
- 단언: 둘 다 `ValueError`를 던지고(유형만 본다) 머리가 그대로다.
- 대역: 없음.

### `test_invalid_and_case_colliding_paths_are_rejected` (행 303–319)
- 성질: 탈출, 역슬래시, Windows 예약 이름, 끝의 점·공백, 절대 경로, 대소문자만 다른 파일 이름은 발행에서 거부된다.
- 준비: 클래스 절의 `setUp`. 무효 경로 다섯 개는 `research/../escape.txt`, `research/back\slash.txt`, `research/CON.txt`, `research/trailing. `, `/research/absolute.txt`다.
- 실행: 경로마다 `runtime/state.json`과 함께 초기 발행한다. 이어서 `research/A.txt`와 `research/a.txt`를 함께 발행한다.
- 단언: 모든 경우 `ValueError`를 던진다(유형만 본다).
- 대역: 없음.
- 비고: `subTest(path=...)` 5건. 대소문자 충돌은 `subTest` 밖에서 확인한다.

### `test_case_colliding_directory_segments_are_rejected` (행 321–327)
- 성질: 대소문자만 다른 디렉터리 이름(`Foo`와 `foo`)도 거부된다.
- 준비: 클래스 절의 `setUp`.
- 실행: `research/Foo/a.txt`, `research/foo/b.txt`, `runtime/state.json`을 초기 발행한다.
- 단언: `ValueError`를 던진다(유형만 본다).
- 대역: 없음.

### `test_only_registry_instance_ids_are_accepted_before_ref_use` (행 329–331)
- 성질: 저장소는 등록 형식의 인스턴스 ID(`RI-` 접두 정규 ULID)만 받아, 참조 이름에 쓰기 전에 거른다.
- 준비: 클래스 절의 `setUp`.
- 실행: `GitStateStore(self.repository, "inst_01")`.
- 단언: `ValueError`를 던진다(유형만 본다).
- 대역: 없음.

### `test_repository_junction_is_rejected_before_resolve` (행 333–341)
- 성질: 저장소 경로 자체가 접합이나 심볼릭 링크이면 경로를 해석하기 전에 거부한다.
- 준비: 클래스 절의 `setUp`. Windows에서는 `cmd.exe /d /c mklink /J`로 `repository-link` 접합을 만들고 종료 코드 0을 단언한다. 다른 OS에서는 디렉터리 심볼릭 링크를 만든다.
- 실행: `GitStateStore(link, INSTANCE_ID)`.
- 단언: `ValueError`를 정규식 `"reparse|symlink"`로 던진다.
- 대역: 없음.
- 비고: Windows에서는 실제 `cmd.exe` 자식 프로세스와 실제 NTFS 접합을 쓴다.

### `test_physical_file_boundary_checks_opened_handle` (행 343–355)
- 성질: `PhysicalBoundary.open`은 경계 안의 파일만 열고, 경계 밖 경로와 `..`로 빠져나가는 경로를 거부한다.
- 준비: 클래스 절의 `setUp`. `PhysicalBoundary(self.repository)`.
- 실행: 경계 안 `boundary.bin`을 `xb`로 쓰고 `rb`로 읽는다. 경계 밖 `outside.bin`과 `repository/../outside.bin`을 `xb`로 연다(`__enter__` 호출).
- 단언: 읽은 바이트가 `b"bounded"`다. 두 바깥 경로는 `ValueError`를 던진다(유형만 본다).
- 대역: 없음.
- 비고: 이름의 "열린 핸들을 확인한다"는 제품이 연 핸들의 실제 위치를 확인한다는 뜻이다. 단언은 결과(거부와 정상 읽기)만 본다.

### `test_physical_boundary_refuses_a_reparse_point_below_its_root` (행 357–372)
- 성질: 경계 루트 아래의 재분석 지점을 거쳐 밖의 파일을 열지 못한다.
- 준비: `bounded`와 `elsewhere` 폴더. `elsewhere/file.bin`에 바이트를 쓴다. `bounded/link`를 `elsewhere`로 잇는다. Windows에서는 `mklink /J` 접합을 만들고 종료 코드 0을 단언하며, 다른 OS에서는 심볼릭 링크를 만든다.
- 실행: `PhysicalBoundary(bounded).open(link/"file.bin", "rb").__enter__()`.
- 단언: `ValueError`를 정규식 `"reparse|symlink"`로 던진다.
- 대역: 없음.
- 비고: Windows에서는 실제 `cmd.exe` 자식 프로세스를 쓴다. 클래스 `setUp`의 저장소는 쓰지 않는다.

### `test_non_commit_or_corrupt_existing_ref_is_not_treated_as_absent` (행 374–384)
- 성질: 있는 참조가 커밋이 아닌 객체나 깨진 값을 가리키면, 참조가 없는 것으로 취급하지 않고 오류를 낸다.
- 준비: 클래스 절의 `setUp`. 실제 `git hash-object -w --stdin`으로 blob을 쓰고, 그 OID를 `git_dir/<ref>` 느슨한 참조 파일에 직접 쓴다.
- 실행: `read_snapshot()`. 참조 파일을 `not-an-object-id`로 바꾸고 다시 `read_snapshot()`.
- 단언: 두 경우 모두 `GitStateStoreError`를 던진다(유형만 본다).
- 대역: 없음.

## GitStateStoreSha256Tests (행 387–401)

`unittest.TestCase`를 그대로 상속한다. 표지, 속성, 훅, 도우미가 없다.

### `test_sha256_repository_uses_64_character_oids` (행 388–401)
- 성질: sha256 저장소에서는 64자 OID를 쓰고, 40자 OID는 거부한다.
- 준비: 실제 `git init --object-format=sha256 -q`로 새 저장소를 만든다(`git_init`은 sha1 모델만 복사하므로 여기서는 자식 프로세스를 쓴다).
- 실행: `GitStateStore`를 열어 두 파일을 초기 발행한다. `read_bytes("0"*40, "runtime/state.json")`.
- 단언: `object_format`이 `"sha256"`이고, 머리 길이가 64다. 40자 OID 읽기는 `ValueError`를 던진다(유형만 본다).
- 대역: 없음.

## InProcessObjectsMatchGitPlumbingTests (행 404–512)

`unittest.TestCase`를 그대로 상속하고 표지와 훅이 없다. 클래스 docstring은 "프로세스 안 작성기를 Git 자신의 색인 plumbing과 차등 비교한다"고 밝힌다.

- 클래스 속성 `NAMES` (행 408): `("a", "a.b", "a-b", "a0", "b", "é")`. 행 407의 주석대로, 하위 트리 이름이 정렬될 때 붙는 `/` 위치에서 순서가 뒤집히는 이름들과 비ASCII 이름이다. Git 트리 항목은 하위 트리 이름에 `/`를 붙여 정렬하므로 `a`와 `a.b`, `a-b`, `a0`의 순서가 파일인지 디렉터리인지에 따라 달라진다.
- 클래스 속성 `GIT_DEFAULTS` (행 409): `GIT_CONFIG_NOSYSTEM=1`과 `GIT_CONFIG_GLOBAL=os.devnull`. 오라클 커밋과 `fsck`가 사용자·시스템 설정의 영향을 받지 않게 한다.
- `valid(paths)` (행 412–414, 정적 메서드): 어떤 경로의 상위 디렉터리 접두가 다른 경로와 같지 않은지, 곧 파일·디렉터리 겹침이 없는지 판정한다.
- `random_changes(rng, model)` (행 416–447): 현재 모델(경로→바이트)에 대한 무작위 변경 집합을 만든다. docstring은 다섯 종류를 든다. 추가, 수정, 삭제(디렉터리를 비우는 것 포함), 디렉터리 경로의 삭제(지울 파일이 없음), 파일↔디렉터리 교체다. 제안을 하나씩 덧붙이며 `valid`를 만족할 때만 받아들인다. `*/keep` 파일은 파일 목록에서 빼므로 두 하위 트리가 비지 않는다.
- `oracle_tree(repository, index, changes, width)` (행 449–460): 같은 변경을 Git의 영속 색인에 적용해 Git이 트리를 쓰게 한다. 추가할 바이트를 임시 파일로 쓰고 `git hash-object --no-filters --stdin-paths`로 OID를 얻는다. 삭제는 `0 <0*width>` 행, 추가는 `100644 <oid>` 행으로 `git update-index -z --index-info`에 준다. 색인은 `GIT_INDEX_FILE` 환경으로 따로 둔다. 마지막으로 `git write-tree`의 트리 OID를 돌려준다.
- `check(object_format)` (행 462–506): 차등 비교 본체. 새 저장소를 sha1이면 `git_init`으로, 아니면 `git init --object-format=...`으로 만든다. 시드 `"do-math-" + object_format`의 `random.Random`으로 4회 반복한다. 첫 회에는 `research/keep`과 `runtime/keep`을 더한다. 셋째 회(`round_number == 2`)에는 저장소 객체를 새로 만들어 부모 트리를 `ls-tree`로 읽게 한다(행 480 주석). 매 회 발행한 뒤 모델을 갱신하고 `tree_paths(head) == set(model)`을 단언하며, 오라클 트리를 기록한다. 끝에 네 커밋의 `^{tree}` OID가 오라클 트리 목록과 같은지, `read_many`가 모델 전체를 돌려주는지 단언한다. 첫 커밋과 마지막 커밋은 오라클 커밋과 비교한다. 오라클은 제품 커밋의 committer 시각과 시간대를 읽어, 같은 신원(`do-math <do-math@invalid>`), 같은 메시지(`do-math state\n`), 같은 부모로 `git -c commit.gpgSign=false commit-tree`가 만든 커밋이다. 그 OID가 제품 커밋과 같아야 한다. 마지막으로 `git fsck --strict --no-progress`가 종료 코드 0이고, "HEAD가 태어나지 않은 브랜치를 가리킨다"는 알림 말고는 아무 출력이 없어야 한다(행 503 주석).

### `test_sha1_trees_and_commits_match_git` (행 508–509)
- 성질: sha1 저장소에서 프로세스 안 작성기가 만든 트리와 커밋은 Git plumbing이 같은 변경으로 만든 것과 바이트 단위로 같고, `fsck --strict`를 통과한다.
- 준비: `check("sha1")`이 `git_init`으로 새 저장소를 만든다.
- 실행: `check("sha1")`(클래스 절의 `check` 설명).
- 단언: 매 회 트리 목록이 모델과 같다. 네 트리 OID가 오라클 트리와 같다. 모델 전체의 바이트가 같다. 첫 커밋과 마지막 커밋의 OID가 오라클 `commit-tree`와 같다. `fsck`에 발견이 없다.
- 대역: 없음. 오라클은 실제 Git이다.
- 비고: 실제 Git 자식 프로세스를 여러 번 부른다(`hash-object`, `update-index`, `write-tree`, `rev-parse`, `cat-file`, `commit-tree`, `fsck`). 난수 시드가 고정되어 있어 결정적이다.

### `test_sha256_trees_and_commits_match_git` (행 511–512)
- 성질: sha256 저장소에서도 같은 차등 비교가 성립한다.
- 준비: `check("sha256")`이 `git init --object-format=sha256` 자식 프로세스로 새 저장소를 만든다.
- 실행: `check("sha256")`.
- 단언: sha1 테스트와 같다. 오라클 삭제 행의 OID 폭은 `store.oid_length`(64)를 쓴다.
- 대역: 없음.
- 비고: 시드가 `"do-math-sha256"`이라 sha1 테스트와 다른 변경 순서를 만든다.

## SnapshotMetadataTests (행 515–571)

`unittest.TestCase`를 그대로 상속하고 표지가 없다.

- 클래스 속성 `INSTANCE` (행 516): `'RI-01ARZ3NDEKTSV4RRFFQ69G5FAV'`.
- 클래스 속성 `REF` (행 517): `'refs/heads/do-math/' + INSTANCE`.
- `setUp` (행 519–520): `enterContext`로 연 임시 폴더를 `git_init`해 `self.repository`로 둔다.
- `store(*, length=40, root_type='commit', rows=None, returncode=0, resolved=None)` (행 522–533): 빈 저장소 위의 `GitStateStore`를 만들고, 뒤따르는 Git 호출이 주어진 메타데이터로 답하게 한다(docstring). 생성자는 실제 Git으로 저장소를 확인하고, 그 뒤 `object_format`을 길이에 맞게 덮는다. 기본 응답 행은 `'a'*length + ' ' + root_type`, `'b'*length + ' tree'`, `'c'*length + ' tree'`다. `_git`을 `create_autospec(store._git, side_effect=[배치 응답, resolved])`로 바꾼다. 첫 호출은 `git_result(returncode, 행들)`이고 둘째 호출은 `resolved`다. `resolved`의 기본값은 머리를 출력하는 성공 응답이다. 행 530의 주석대로 배치 질의는 한 번이고, `rev-parse`는 참조 행이 없을 때만 돈다. `(store, head)`를 돌려준다.

### `test_one_batch_reads_the_ref_and_both_subtrees` (행 535–544)
- 성질: 스냅숏 읽기는 참조와 두 하위 트리를 한 번의 `cat-file --batch-check`로 읽는다.
- 준비: 클래스 절의 `store` 도우미로 길이 40과 64 각각의 정상 응답.
- 실행: `read_snapshot()`.
- 단언: 결과가 `StateSnapshot(head)`다. `_git` 호출이 1회다. 그 인자가 `('cat-file', '--batch-check=%(objectname) %(objecttype)')`이고, 입력이 `REF`, `REF:research`, `REF:runtime` 세 줄이다.
- 대역: `store` 도우미의 `_git` 대역.
- 비고: `subTest(length=...)` 2건(sha1, sha256).

### `test_absent_ref_is_none_but_corrupt_ref_is_rejected` (행 546–553)
- 성질: 참조가 없으면 빈 스냅숏이지만, 참조를 해석하다 오류가 나면 없는 것으로 취급하지 않는다.
- 준비: 세 행이 모두 `missing`인 배치 응답. 둘째 응답은 (1) stderr 없는 종료 코드 1, (2) stderr `bad ref`인 종료 코드 1.
- 실행: 두 경우 각각 `read_snapshot()`.
- 단언: (1)은 `StateSnapshot(None)`이고, Git 호출 순서가 `['cat-file', 'rev-parse']`다. (2)는 `GitStateStoreError`를 `'cannot resolve'`로 던진다.
- 대역: `store` 도우미의 `_git` 대역.
- 비고: 제품 `_ref_oid`는 `rev-parse --verify --quiet`의 종료 코드 1과 빈 stderr만 "참조 없음"으로 읽는다.

### `test_wrong_or_incomplete_metadata_never_returns_a_snapshot` (행 555–571)
- 성질: 잘못되었거나 불완전한 메타데이터는 어떤 경우에도 스냅숏을 돌려주지 않는다.
- 준비: 일곱 응답과 기대 메시지. 머리가 `blob`이면 `'commit'`이다. 참조만 `missing`이고 줄이 하나뿐이면 `'unreadable'`이다. 머리 행에 여분 필드가 있으면 `'invalid state commit'`이다. research 하위 트리가 `missing`이면 `'research'`다. research가 `blob`이면 `'tree'`다. 줄이 둘뿐이면 `'incomplete'`이고, 줄이 넷이어도 `'incomplete'`다. 끝으로 배치 질의 자체가 종료 코드 1인 경우.
- 실행: 경우마다 `read_snapshot()`.
- 단언: 일곱 경우는 `GitStateStoreError`를 각 메시지 조각으로 던진다. 종료 코드 1은 `GitStateStoreError`를 던진다(유형만 본다).
- 대역: `store` 도우미의 `_git` 대역.
- 비고: `subTest(rows=...)` 7건.

## 관계

- 이 모듈은 저장의 가장 아래층(Git 객체와 참조)을 본다. 그 위의 `ResearchRepository`(상태 계약 검증, 검증된 읽기 캐시, 질의, 내보내기)는 `test_repository`가 검사한다. `test_repository`의 여러 테스트는 이 층의 `publish`를 직접 불러 손상 커밋을 만든다.
- 물리 경계와 재분석 지점 규칙은 `test_retention`(실행 폴더 정리)과 `test_context_store`(`StableReadTests.test_one_boundary_proves_its_root_once_for_many_reads`, 심볼릭 링크 보고)가 각자의 영역에서 같은 `PhysicalBoundary`·`no_reparse` 장치를 검사한다.
- 레코드 내용의 유니코드 보존은 `test_unicode_flow`가, 경로 이름의 보존은 이 모듈의 `test_unicode_artifact_path_preserves_the_supplied_code_points`가 맡는다.
- 픽스처 의존: `research_fixtures.git_init`(sha1 빈 저장소). sha256 저장소는 `git init` 자식 프로세스를 직접 쓴다.
- 이 모듈에만 있는 도우미: 모듈 함수 `git_result`, `git`, `loose_objects`; 클래스 도우미 `initial_changes`, `forget_trees`, `valid`, `random_changes`, `oracle_tree`, `check`, `store`.
