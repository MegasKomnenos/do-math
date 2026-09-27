---
id: M-0350
layer: 1
title: do-math 상태 게시의 객체 쓰기를 프로세스 안으로 옮기고 참조 이동만 Git CAS로 남김
convention_version: 27
---

## 맥락

do-math 시험 경량화 작업(공통 계약 `임시/시험-경량화-2026-09-26/계약.md`)에서 W-git 작업자로 `do_math/git_store.py`의 쓰기 경로를 맡았다. 변경 전 `GitStateStore.publish`는 게시 1회마다 `read-tree`·`hash-object`·`update-index`·`write-tree`·`commit-tree`·`update-ref`의 6개 git 프로세스를 띄웠다. 이 기계에서 git 프로세스 1개는 약 0.15~0.2초가 걸렸다. 변경 뒤에는 blob·tree·commit을 프로세스 안에서 느슨한 객체로 쓰고, `update-ref`의 기대값 비교(CAS)만 git으로 남는다. 작업은 worktree `C:/math-worktrees/t-git`, 브랜치 `t-git`에서 했다.

구현의 중심은 네 가지다.
- `_write_object`: 머리말 `"<유형> <크기>\0"`과 내용을 저장소 형식(sha1·sha256)으로 해시한다. zlib 수준 1로 압축해 같은 팬아웃 디렉터리의 `tmp_obj_*` 임시 파일에 쓰고, fsync한 뒤 0444로 바꾸고 이름을 바꾼다. 객체가 이미 있으면 쓰지 않는다. Windows에서 이름 바꾸기가 `FileExistsError`로 지면 같은 객체를 다른 작성자가 먼저 쓴 것으로 본다.
- `_write_tree`: 바뀐 경로의 조상 디렉터리만 경로 복사로 다시 쓴다. 정렬은 하위 트리 이름에 `/`를 붙인 바이트 비교다. 빈 디렉터리는 부모에서 뺀다. 디렉터리 이름과 같은 경로를 삭제하는 변경은 Git 인덱스처럼 아무것도 지우지 않는다.
- `_tree`: 마지막으로 게시한 커밋과 마지막으로 읽은 커밋의 트리 구조를 칸 두 개에 둔다. 칸이 하나이던 변경 전에는 과거 입력 snapshot을 읽으면(`engine._validate_bundle_current`의 `store.view(input_snapshot)`) 방금 게시한 head의 목록이 밀려나, 다음 게시가 `ls-tree`를 다시 띄웠다(시험당 8회).
- `read_snapshot`: writer lock을 쥔 동안 이 저장소 객체의 CAS가 성공했으면 그 head를 프로세스 없이 돌려준다(`_held_head`). CAS 실패와 lock 해제에서 비운다.

## 터득한 것

**설치된 Git for Windows는 느슨한 객체를 기본으로 fsync한다.** upstream `core.fsync`의 플랫폼 기본은 `committed,-loose-object`로, 느슨한 객체를 fsync하지 않는다(설치본 `mingw64/share/doc/git-doc/git-config.html`). 그러나 설치본 `C:/Program Files/Git/ReleaseNotes.html`에 "Git for Windows now sets core.fsyncObjectFiles = true by default"가 있다. trace2 이벤트의 `fsync/hardware-flush` 계수로 실측했다. 조건은 저장소가 git을 띄우는 것과 같이 `GIT_CONFIG_NOSYSTEM=1`, `GIT_CONFIG_GLOBAL=/dev/null`로 두었다. 결과는 다음과 같다.
- 새 객체 1개: 1회
- `-c core.fsyncObjectFiles=false`: 0회
- 여기에 `core.fsync=loose-object`를 더함: 1회
- `core.fsync=none`만 줌: 1회. `fsync_object_files > 0` 분기가 `core.fsync`보다 앞선다.
- 기존 객체와 `update-ref`: 0회

그래서 새 객체마다 fsync하고 디렉터리는 fsync하지 않는 것으로 맞췄다. `core.fsync` 문서만 읽었다면 반대로 판단했을 것이다. `GIT_TRACE2_EVENT`의 `category:"fsync"` counter 이벤트가 설정 조합의 실효를 가르는 수단이었다.

**`read_snapshot` 캐시가 유효한 범위는 lock hold 안뿐이다.** 게시 직후 `engine._reload`가 ref를 다시 읽는 호출(시험당 7회)을 계측으로 찾았다. 그런데 이 호출은 `_run_executor`·`process_controls`가 writer lock을 새로 잡은 직후에 일어났다. 이전 hold가 풀린 사이에 다른 작성자가 ref를 옮겼을 수 있으므로, 이 읽기는 동기화 지점이다. 그래서 없애지 않았다. 캐시는 같은 hold 안에서 자기 CAS가 성공한 뒤로 한정했다(`engine.py` 2210행과 게시 뒤 예외 복구 경로). 두 측정 시험에서 이 경로는 한 번도 일어나지 않았다(`read_snapshot` 16·25회가 변경 전후 같음).

**차등 시험의 생성기 공백은 통과만 보아서는 드러나지 않았다.** 오라클은 git plumbing의 `hash-object`·`update-index --index-info`·`write-tree`를 지속 임시 인덱스에 적용한 것이다. 이 오라클과 트리 OID, `commit-tree` 커밋 OID, `fsck --strict`를 대조하는 시험을 먼저 기존 구현에 돌려 오라클이 맞음을 확인했다. 그다음 생성기가 만든 변경의 종류를 세어 보니 "디렉터리→파일 전환"과 "기존 파일 수정"이 0회였다. 전환 제안 바로 뒤에 같은 디렉터리의 경로 삭제 제안이 덮어쓰고 있었다. 생성기를 고친 뒤 결함 다섯 가지를 심은 돌연변이(정렬의 `/` 규칙, 디렉터리 경로 삭제 보호, 빈 디렉터리 제거, 비워진 디렉터리와 같은 이름의 새 파일 보호, 모드 `040000`)를 돌렸고, sha1·sha256 시험이 모두 실패했다. `git fsck`는 정상 저장소에서도 stderr에 "notice: HEAD points to an unborn branch"를 내므로, 출력이 비었다는 단언은 쓸 수 없다.

**`update-index --index-info`는 파일↔디렉터리 전환을 입력 순서와 무관하게 처리한다.** 파일 `a` 삭제와 `a/b` 추가를 어느 순서로 주어도 성공했다. 새 구현도 같은 결과를 내므로 동작 변화가 아니다.

## 측정

두 대상 시험을 `sitecustomize.py` 계측 장치로 쟀다. 이 장치는 자식 Python까지 모든 git 자식 프로세스를 기록하며 커밋하지 않았다.

| 시험 | git 프로세스 전→후 | 게시 1회당 | 연속 쌍 시간(계측 없음) |
|---|---|---|---|
| `test_engine…test_nonformal_mathematical_goal_is_not_solved` | 573→211 (게시 71회) | 6→1 | 111.2초→65.6초 |
| `test_redesign_ENGINE.PublicGitFlow…next_plan` | 655→233 (게시 83회) | 6→1 | 109.2초→77.4초 |

- 연속 쌍은 `git stash`로 변경 전을 재고, 곧바로 되돌려 변경 후를 잰 것이다.
- 첫 비연속 측정은 149.6→64.9초, 176.5→69.5초였다. 기계 부하에 따라 절대값이 크게 흔들린다.
- 파일 200개 상태에서 파일 3개를 바꾸는 게시의 중앙값은 669·858ms에서 159·169ms로 줄었다.

남은 읽기 호출(두 시험 합)은 `cat-file` read_bytes 108, blob_sizes 90, read_snapshot 41, read_many 20, `ls-tree` 16(과거 snapshot 읽기), `rev-parse` 13이다.

근거 로그(`%TEMP%/t-git-measure/*.log`)와 계측 장치는 저장소 밖 로컬 자료이며 정리로 사라질 수 있다. 수치는 이 노드와 반환 보고가 정본이다.

## 남은 위험과 경계

- 시간대는 `time.localtime().tm_gmtoff`로 계산한다. KST(+0900)에서 `git var GIT_COMMITTER_IDENT`와 일치를 확인했다. DST 지역은 확인하지 못했다.
- 기존 객체의 수정 시각 갱신(freshen)은 하지 않는다. 동시 `git gc --prune`과의 경쟁에서만 차이가 나는데, do-math는 plumbing만 써서 auto-gc가 돌지 않는다.
- 저장소 로컬 설정의 `core.fsync`·`core.looseCompression`·`core.sharedRepository`는 따르지 않는다. 설치본 기본값에 고정했다.
- 팩에만 있는 객체는 느슨한 사본을 한 번 더 쓴다(무해).
- 기존 경로가 `os.environ`에서 넘겨받던 `GIT_AUTHOR_*`·`GIT_COMMITTER_*`는 이제 커밋에 반영되지 않는다. 저장소 안에 이 변수를 설정하는 코드는 없다.
- 379a171에서 이미 실패하는 시험 셋을 확인했다(`test_performance_repairs…test_engine_entry_checks…`의 TypeError, `test_background_processes…console_creation`의 9<14, `test_submission_flow…central_checks`의 verified). fe59ca0 기준 목록에는 없다.
- 이 노드 번호는 병행 작업자 브랜치와 겹칠 수 있다. 통합 때 확인한다.

## 작업 너머 시사점

- dream에서 묶을 후보: [[L-0001]]의 "통과만 본 검증" 항목과 이 노드의 생성기 공백(종류별 계수로 발견, 돌연변이로 검출력 확인)은 무작위 차등 시험의 검증 설계 사례다.
- dream에서 묶을 후보: [[L-0020]]의 비용 항목과 [[M-0348]]·[[M-0349]]의 경량화 흐름에, 제품 비용의 원천(Windows 프로세스 생성)을 계측으로 특정한 이 노드를 잇는다. fsync 기본값처럼 플랫폼별 기본값이 문서와 다를 수 있다는 점은 trace2 실측을 근거로 남긴다.
