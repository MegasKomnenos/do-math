# 결과 — 커널 단계 K-제품

이 문서는 do-math 경량화 2라운드 커널 단계 가운데 K-제품의 반환이다. 설계 `docs/do-math/경량화-설계-2026-09-26.md` 6절의 다섯 항목을 순서대로 적고, 기존 이음새 계약 10절의 `이음새 요청`·`추가한 이름`을 덧붙인다. 통합자는 이 문서로 커널을 main에 합칠지 판단하고, 2절 표를 이음새 계약 문서로 옮긴다.

- 브랜치·커밋: worktree `C:/math-worktrees/r2-kprod`, 브랜치 `r2-kprod`, 커밋 `3b0d1d8`(기준 `8d2ffd0`)
- 변경 범위: `scripts/do_math/` 44개 파일, `scripts/operator_bootstrap.py`, 시험 5개 파일. 스킬 문서와 `.agents` 미러는 고치지 않았다(3절).
- 좌표: 경로는 `C:/math-worktrees/r2-kprod/.claude/skills/do-math/scripts/` 기준이다.

## 1. ID별 처분

4.1절 K-제품 행의 16개 ID와 저장 계약 식별자 상향을 모두 처리했다. 완전히 구현한 항목은 14개다. STO-05와 STO-07은 부분 구현이며, 남은 범위와 이유는 각 행에 적었다.

| ID | 처분 | 내용 |
|---|---|---|
| REV-06 | 구현함 | `review_cycle._bytes`와 `review_engine`의 별칭 `_transcript_bytes`를 지우고 `file_io.compact_json_bytes`를 쓴다. manifest 행 판정은 `review_cycle._manifest_fault(message, entry, position)` 하나로 합쳤다. 이 함수는 `None`·`'invalid_manifest'`·`'content_mismatch'`를 돌려주고, `_verified_transcript`와 `validate_transcript`가 함께 쓴다. `validate_transcript`는 두 원인을 지금처럼 다른 `cause_kind`로 구분한다. 값만 해시하는 자리(`event_sha256`)는 `json_digest`를 쓴다. 바이트와 해시가 모두 필요한 자리는 `compact_json_bytes`의 결과를 한 번 해시한다. |
| IO-10 | 구현함 | 다음 네 곳이 `compact_json_bytes`를 쓴다. `control_transport._canonical`은 지웠다. `_atomic_json`은 `write_bytes_atomic(path, compact_json_bytes(value))` 한 줄이 되었다. `codex_worker._write_status`와 `codex_adapter`의 요청 스냅숏도 이 함수를 쓴다. 스냅숏에 NaN이 들어가면 이제 오류가 난다(조사 파일이 예고한 차이). |
| IO-09 | 구현함 | 훅 사본을 모두 지웠다. 대상은 `codex_worker._pairs`, `claude_stream._pairs`·`_constant`, `cli._pairs`, `repository._unique_pairs`·`_reject_constant`다. 넘침 검사까지 하던 `codex_adapter._parse_jsonl`과 `claude_stream.parse_stream`은 `strict_json_loads`를 쓴다. 두 훅을 함께 쓰던 `claude_adapter.validate_final`도 `strict_json_loads`를 쓴다. 넘침 값은 전에도 `canonical_json`에서 `structured_output_invalid`가 되었으므로 결과는 같다. 중복 키 훅만 쓰던 `codex_worker`·`claude_worker`·`cli`는 `unique_pairs`만 쓴다. 두 훅을 쓰던 `repository`·`payloads`·`submission`·`model_runner`·`observations`는 `file_io`에서 직접 가져온다. 조사 제안의 "repository가 재수출"은 AGENTS.md의 별칭 금지에 따라 따르지 않았다. |
| STO-06 | 구현함 | ① `is_sha256`: `state_checks`, `payloads`, `repository`, `context_store`(2곳), 영역 밖의 `planning`·`observations`·`launch`·`formal`(2곳)·`trust_validation`·`codex_worker`가 쓴다. `task_contracts`·`review_policy`는 `validate_profile_ref`를 거쳐 쓴다. ② `git_store._no_reparse`를 `no_reparse`로 공개했다. `repository._assert_no_reparse_ancestor`·`_is_reparse`, `context_store`의 `_physical_root`·`_safe_path` 안 반복문, `retention._physical`이 이를 쓴다. `context_store._is_reparse`는 한 경로 성분만 판정하는 술어로 남긴다. 디렉터리 순회가 예외 대신 참·거짓을 필요로 하기 때문이다. 판정 규칙은 `no_reparse(path, below=path.parent)`에 맡긴다. ③ 스냅숏 OID 형태는 `context_store` 2곳과 `retention._archive_reference`에서 `oid_shape`로 판정한다. `_archive_reference`는 `runtime/artifacts/` 접두 확인만 남긴다(나머지 경로 규칙은 뒤이은 읽기가 한다). 동작 차이: 끊어진 심볼릭 링크를 `repository.export`와 `context_store._safe_path`가 이제 거부한다. 전에는 `exists()`가 링크를 따라가 건너뛰었다. |
| ENG-10 | 구현함 | `file_io.os_lock(path, *, blocking)`을 만들었다. 엔진 `_control_acceptance_lock`을 지우고 호출부(`engine.control`)에서 `os_lock(..., blocking=True)`를 쓴다. 잠금 파일 생성 절차는 임시 파일과 `os.link` 대신 `O_CREAT`로 열고 1바이트를 쓰는 방식이 되었다(git_store와 같음). `_next_control_order`는 `write_bytes_atomic(..., fsync=True)`로 쓴다. 임시 파일 접두·접미는 전과 같다. |
| STO-21 | 구현함 | `git_store.writer_lock`은 `ExitStack`으로 `os_lock(..., blocking=False)`를 잡는다. 잡지 못한 `OSError`는 지금처럼 `GitStateStoreLockError`로 바꾼다. `session_slots._lock`·`_unlock`을 지웠다. 이 두 함수의 유일한 사용처인 `scheduled_operator.recovery`의 설치 정비 잠금은 `ExitStack`과 `os_lock(..., blocking=False)`로 바꿨다. 들여쓰기가 바뀌지 않게 해 그룹 A와의 충돌 면적을 줄였다. |
| OPS-13 | 구현함 | `file_io.parse_utc`를 만들었다. `provider_wait.timestamp`는 `epoch_seconds`로 이름을 바꾸고 문자열 분기를 `parse_utc`에 맡겼다. 호출부 `reporting`·`scheduled_operator`와 시험 2개도 바꿨다. `governance.timestamp`는 이름을 유지한다. 본문은 `None`이면 현재 시각, 아니면 `parse_utc`인 한 줄 변환이다. 호출부가 약 30곳이고 `None`=현재 시각 의미를 쓰므로 이 선택이 가장 작은 변경이었다. 동명이형 혼동은 `provider_wait` 쪽 개명으로 사라졌다. `preflight`의 UTC 오프셋 0 요구는 `parse_utc` 뒤에 값이 `Z` 또는 `+00:00`으로 끝나는지 확인한다. 동작 차이는 `+0000`처럼 다른 표기의 0 오프셋을 이제 거부한다는 점이다. 엔진은 `isoformat()`(`+00:00`)으로 쓰므로 실제 기록은 영향이 없다. |
| RES-08 | 구현함 | `planning._utc`, `delegations._now`, `external._now`를 지우고 `parse_utc`를 쓴다. 조사 파일에 없던 `planning._utc`의 지연 import 사용처 세 곳(`task_contracts`, `task_scope`, `revisions`)도 바꿨다. `delegations`의 `None`=현재 시각 의미는 호출 식에서 명시한다. `observations._utc(value, field)`는 필드 이름이 든 오류 문구를 지키는 감싸개로 남기고, 해석은 `parse_utc`에 맡긴다. |
| STO-05 | 부분 구현 | `repository.sealed_bytes`·`artifact_key`를 만들었다. 이제 `verify_artifact`는 `git_dir is None`이면 표시하지 않고, `artifact_verified(None, ...)`는 거짓이다. 따라서 각 호출자의 `git_dir is None` 분기가 사라졌다. 옮긴 곳은 `context_store` 2곳, `retention` 2곳, `planning`(키 조립은 `artifact_key`), `review_cycle`, `review_engine`, `submission` 2곳(REV-19 포함)이다. `engine._sealed_bytes`는 `sealed_bytes`에 저장소와 head를 묶는 한 줄 어댑터로 남겼다. 엔진 호출부 13곳을 바꾸지 않기 위해서다. 남긴 곳은 `payloads.decode`다. 이 함수는 해시 대조 뒤 정규 JSON 검사까지 통과해야 표시한다. `sealed_bytes`는 해시 대조 직후 표시하므로, 옮기면 비정규 페이로드가 검증된 행으로 남는다. 이 동작 변경을 피해 옮기지 않았다(4번 절의 이음새 요청 참조). |
| REV-19 | 구현함 | `summarize_snapshot_checks`에 키워드 `git_dir`를 더해 `sealed_bytes`를 쓰게 했고, 엔진이 이를 넘긴다. `require_bundle_impact_review`·`apply_reviewed_knowledge_changes`·`_reviewed_impact_request`도 키워드 `git_dir`를 받아 `read_sealed_submission`에 넘기며, 엔진의 두 호출부가 이를 넘긴다. `read_sealed_submission`의 `git_dir is None` 분기는 지웠다. `git_dir`는 키워드 기본값 `None`으로 남긴다. 시험이 저장소 없이 이 함수들을 부르기 때문이며, `None`이면 매번 대조한다. |
| STO-07 | 부분 구현 | `git_store`에 `ULID_ALPHABET`·`ULID_LENGTH`·`ULID_PATTERN`과 `is_new_id(prefix, value)`를 두었다. `repository.new_id`는 이 상수로 인코딩한다. 옮긴 판정은 `git_store`의 `RI` 판정, `knowledge_io`의 `KN`·`RL` 판정, `submission`의 `replacement_id` 스키마 패턴(`"^KN-" + ULID_PATTERN + "$"`)이다. `state_contract.RECORD_ID = r"[A-Za-z0-9][A-Za-z0-9_.-]*"`는 콜론을 제외한다. 계약 검사와 `schemas.ID`가 이 패턴을 쓴다. 외부 등록 가족의 `:` ID는 이제 저장 전에 거부된다. 하지 않은 것은 예약 장치명(`CON` 등) 확인의 재사용이다. 재사용하려면 `git_store._validate_path` 안의 성분 규칙을 모듈 함수로 꺼내야 한다. 이 함수는 2절 표에 없으므로 만들지 않고 이음새 요청으로 올린다. |
| ENG-01 | 구현함 | `scheduler.py`의 `MACHINE_ROLES`·`WORK_ROLES` 사본을 지웠다. `scheduler`는 `execution_profiles`에서 가져오고, 엔진은 `execution_profiles.WORK_ROLES`를 쓴다. 순환 import는 없다(전 모듈 import 확인). `governance.WORK_ROLES`(뜻이 다른 동명 집합)는 그룹 F 소유라 고치지 않았다. |
| RUN-25 | 구현함 | `execution_profiles.LEAN_ROLES = {"formal_check","trust_check"}`와 `UNCAPPED_ROLES = LEAN_ROLES \| {"trust_activate"}`를 두었다. `HOST_ROLES`는 `PROFILE_ROLES - UNCAPPED_ROLES`다. 리터럴 사본은 `execution_profiles` 3곳, `scheduler`, `session_slots`, `launch`, `engine`에서 모두 지웠다. |
| REV-13 | 구현함 | `execution_profiles.validate_profile_ref(ref)`를 만들었다. `task_contracts`·`review_policy`는 지연 import로 이를 부르고, 기존 오류 문구로 감싼다. `review_policy`의 id 조건은 `task_contracts`와 같은 비공백 요구로 약간 엄격해졌다. `codex_worker`는 Job 안에서 패키지 없이 적재되므로 `execution_profiles`를 import하지 않고 `is_sha256`만 쓴다. wire·저장 JSON 스키마(`contracts.py`, `schemas.PROFILE_REF`)는 JSON Schema 선언이라 그대로 두었다. |
| STO-16 | 구현함 | `execution_profiles.match_profile_ref(profiles, reference)`는 형태 확인 뒤 ID·판본·sha256만 비교하고, 재해시와 복사를 하지 않는다. `record_schemas.resolve_profile` 사본을 지우고, `validate_semantics`의 6개 호출이 `match_profile_ref`를 쓴다. `execution_profiles.resolve_profile`은 `deepcopy(match_profile_ref(...))`가 되어 재해시가 빠졌다. 기존 호출자 약 35곳은 복사가 필요할 수 있어 `resolve_profile`을 그대로 부른다. 복사 없는 `match_profile_ref`로 옮기려면 호출자마다 변경 여부를 감사해야 한다. 저장되지 않은 프로필을 조회하는 호출자는 찾지 못했다. 대상 프로필은 모두 저장소 적재나 `seal_profile`을 거친다. 따라서 명시적 재해시를 더한 곳은 없다. |
| OPS-05 | 구현함 | `operator_bootstrap._digest`를 지우고 `file_io.json_digest`를 쓴다. `_source_files(root, file_io)`는 `file_io.sha256_file`을 쓴다. `freeze`와 `verify_snapshot`은 시작할 때 `_file_io()`를 한 번 부른다. `hashlib` import는 사라졌다. `_ordinary_path`(재분석 검사)는 `git_store`를 import하지 않으려고 남겼다. |
| 저장 계약 식별자 | 구현함 | `state_contract.STATE_CONTRACT_ID = "do-math-state/6"`로 바꾸고, `contracts.py`·`engine.py` docstring의 판본도 고쳤다. 이 리터럴을 쓰는 시험은 없었다(`grep -rn "do-math-state" scripts/tests` 무결과). `STATE_FORMAT_VERSION`(기능 판본 5, `feature_version`)은 설계가 요구하지 않았으므로 그대로다. |

## 2. 만든 공유 정의와 위치

| 정본 | 위치 | 규칙 |
|---|---|---|
| `compact_json_bytes(value)` | `do_math/file_io.py` | 압축 정렬 UTF-8 JSON, `allow_nan=False` |
| `json_digest(value)` | `do_math/file_io.py` | `sha256(compact_json_bytes(value))`의 16진 문자열(재정의, 값 불변) |
| `unique_pairs`, `reject_constant`, `strict_json_loads(raw)` | `do_math/file_io.py` | 중복 키 거부, NaN·무한 상수 거부, `strict_json_loads`는 둘에 지수 넘침 거부를 더함 |
| `is_sha256(value)` | `do_math/file_io.py` | 소문자 64자리 16진 문자열 |
| `os_lock(path, *, blocking)` | `do_math/file_io.py` | 0번 바이트의 OS 권고 잠금, 파일이 없으면 생성. `blocking=False`는 즉시 `OSError`. `blocking=True`는 POSIX에서 무한 대기하고, Windows `LK_LOCK`은 1초 간격 10회 재시도 뒤 `OSError`를 낸다(기존 의미 유지). |
| `write_bytes_atomic(path, raw, *, fsync=False)` | `do_math/file_io.py` | 기존 원자 쓰기에 fsync 선택 인자 |
| `parse_utc(value)` | `do_math/file_io.py` | 비지 않은 문자열, `Z` 허용, 시간대 필수, UTC datetime 반환, 실패는 `ValueError` |
| `sealed_bytes(git_dir, path, sha256, size, read, *, raw=None, needed=True, error=None)`, `artifact_key(git_dir, path, sha256)` | `do_math/repository.py` | S3 소비 규칙. `read`는 인자 없는 호출 가능 객체다. `git_dir=None`이면 매번 대조하고 기억하지 않는다. `error`를 주면 불일치를 `ValueError(error)`로 낸다. |
| `ULID_ALPHABET`, `ULID_LENGTH`, `ULID_PATTERN`, `is_new_id(prefix, value)` | `do_math/git_store.py` | ULID 접두 ID(`repository.new_id`가 같은 상수를 씀) |
| `RECORD_ID` | `do_math/state_contract.py` | 레코드 ID 정규식 문자열(앵커 없음, 콜론 제외) |
| `no_reparse(path, *, below=None)` | `do_math/git_store.py` | 재분석 지점·심볼릭 링크 거부(기존 `_no_reparse` 공개) |
| `MACHINE_ROLES`, `WORK_ROLES`, `LEAN_ROLES`, `UNCAPPED_ROLES` | `do_math/execution_profiles.py` | 역할 집합 |
| `validate_profile_ref(ref)`, `match_profile_ref(profiles, reference)` | `do_math/execution_profiles.py` | 프로필 참조 형태, 저장 프로필 조회(재해시·복사 없음) |

설계 2절 표와 이름·위치가 같다. `sealed_bytes`의 인자 순서, `RECORD_ID`의 자료형(정규식 문자열), `ULID_PATTERN` 상수는 표에 적혀 있지 않던 세부다. 이 셋은 조사 파일 STO-05·STO-07 제안을 따라 정했다.

## 3. 필요한 문서 변경

- `.claude/skills/do-math/README.md` 15행, `references/CLI-실행-계약.md` 5행·54행: `do-math-state/5`를 `do-math-state/6`으로 바꾼다.
- `docs/do-math/검사-경량화-이음새-계약.md`
  - 2.1절: 보존 변종 목록에서 `operator_bootstrap` 항목을 지운다(OPS-05). `json_digest` 설명에 `compact_json_bytes` 정본을 더한다.
  - 3절(S3): `sealed_bytes`·`artifact_key`와 `git_dir=None`의 의미(대조만, 표시 안 함)를 더한다. 새 소비자는 `artifact_verified`와 `verify_artifact`를 직접 조합하지 말고 `sealed_bytes`를 쓴다는 규칙을 더한다.
  - 설계 2절 표를 이 문서로 옮긴다(통합자 몫).
- `.agents/skills/do-math/` 미러: 문서 단계의 `build_skill_mirrors.py`로 다시 만든다. 미러의 `scripts/do_math`도 현재 옛 코드다.

## 4. 시험

명령은 모두 `.claude/skills/do-math/scripts`에서 실행했다. lean·resource 그룹은 돌리지 않았다. 결과는 다음 세 묶음이다.

| 묶음 | 명령 | 결과 파일 | 결과 |
|---|---|---|---|
| A | `python run_tests.py --group unit --group integration` + `C:/math-worktrees/reports/kprod-A.args`의 `--match` 24개 | `C:/math-worktrees/reports/kprod-a/report.json` | unit 73 통과. integration 351 통과, 1 건너뜀, 5 실패 |
| B | 같은 명령 + `kprod-B.args`의 `--match` 25개 | `C:/math-worktrees/reports/kprod-b/report.json` | unit 78 통과. integration 322 통과 |
| C | 같은 명령 + `kprod-C.args`의 `--match` 10개 | `C:/math-worktrees/reports/kprod-c/report.json` | unit 40 통과. integration 100 통과, 4 실패 |

- 실패 9건은 모두 M-0348 기준선에 있다. A의 5건은 `test_submission_tools.ReviewFailureTests` 5건이며, 증상도 기준선과 같다(검토 재생성 대기 상태 비교 실패). C의 4건은 `test_redesign_GOVERNANCE` 4건이다. 이 4건은 같은 worktree에서 변경을 stash하고 기준 커밋으로 다시 돌려, 같은 4건이 실패함을 확인했다(`C:/math-worktrees/reports/kprod-base.log`). stash는 복원했다.
- 기준선 대비 새 실패는 0건이다.
- 선택한 모듈은 바뀐 제품 모듈을 직접 검사하거나 고친 시험 파일이다. 목록은 세 `.args` 파일에 있다. 선택 밖 통합 시험(엔진 중심 경로 전체)은 돌리지 않았으므로 통합 단계의 전체 실행이 확인한다.
- 고친 시험 파일 5개는 K-시험의 대형 파일과 겹치지 않는다.
  - `test_control_shapes.py`: 시각 파서 목록을 `governance.timestamp`와 `parse_utc`로 교체
  - `test_diagnosed_installation_recovery.py`: `session_slots._lock` 패치를 `do_math.file_io.os_lock` 패치로 교체
  - `test_provider_wait.py`, `test_six_connections.py`: `timestamp`를 `epoch_seconds`로 교체
  - `test_redesign_PROFILES.py`: 두 곳을 고침. 정비 잠금 해제 확인은 `os_lock`으로 바꿨다. 메모리에서 변조한 프로필의 검출 단언은 `resolve_profile` 대신 `validate_profile`로 옮겼다(STO-16 계약 변경).
- 전 모듈 import 검사를 했다. 정적 검사도 두 가지 했다. 하나는 AST로 모든 `from … import 이름`과 `모듈.속성` 참조의 실재를 확인했다. 다른 하나는 시험의 `patch('do_math.…')` 문자열 대상의 실재를 확인했다. 결과는 결함 없음이다(`record_schemas`의 star import 오탐만 있음). 직접 실행 워커(`codex_worker`, `claude_worker`, `claude_stream`, `control_transport`)의 패키지 없는 import도 확인했다.

## 5. 전제가 틀렸거나 계획을 바꾼 지점

- `planning._utc`에는 조사 파일에 없던 지연 import 사용처가 세 모듈에 있었다. 첫 시험 실행이 `ImportError`로 이를 드러냈다. 실행을 중단하고 세 곳을 고친 뒤 전체를 다시 돌렸다. 4절의 수치는 다시 돌린 결과다.
- `session_slots._lock`·`_unlock`은 `session_slots` 안에서는 쓰이지 않았지만 `scheduled_operator.recovery`가 쓰고 있었다. 그래서 `os_lock`으로 옮겼다.
- IO-09의 "repository 재수출" 제안은 별칭을 남기는 방식이라 따르지 않았다. 사용자가 `file_io`에서 직접 가져온다.
- STO-05의 `payloads.decode`는 동작 보존 조건 때문에 옮기지 않았다(1절).
- STO-16은 조회 함수의 재해시만 뺐다. 호출자를 복사 없는 조회로 옮기는 일은 하지 않았다(1절).
- `engine.py`에서 바꾼 줄은 통합자가 K-시험 브랜치와 합칠 때 확인할 좌표다(기준 커밋 좌표).
  - 3행 docstring
  - import 5줄(`contextmanager`·`tempfile` 삭제, `repository`·`scheduler`·`file_io` import 줄)
  - `_control_acceptance_lock` 삭제(272–306)
  - `_next_control_order`의 쓰기(322–329)
  - `control`의 잠금 한 줄(436)
  - `_sealed_bytes` 본문(1123–1138)
  - 역할 집합 2줄(1738, 1894)
  - `git_dir` 인자 3줄(2256, 2313, 4747)

## 이음새 요청

- `git_store`의 경로 성분 규칙(예약 장치명, 끝 점·공백, 금지 문자)을 모듈 함수로 꺼내 `state_contract`의 레코드 ID 검사가 재사용하게 할지 결정이 필요하다(STO-07 잔여).
- `payloads.decode`의 "대조 + 정규 JSON 검사 뒤 표시" 변종을 `sealed_bytes`로 흡수하려면 표시를 늦추는 선택 인자가 필요하다. 지금은 변종으로 남아 있다.
- 표에 없는 압축 JSON 직렬화 사본이 세 곳 남았다. `budget.canonical_record_bytes`(`allow_nan` 없음), `engine._state_signature`(문자열), `preflight`의 스키마 쌍 검사(문자열)다. 저장 대조 여부를 확인한 뒤 정본으로 옮길지 정해야 한다.
- `governance.WORK_ROLES`는 `formal_check`를 포함해 `execution_profiles.WORK_ROLES`와 뜻이 다른데 이름이 같다. 그룹 F가 `AUTHORIZED_WORK_ROLES` 같은 이름으로 바꿀 것을 제안한다(ENG-01 조사 제안).
- `governance.py:94`는 문서 해시의 길이만 확인한다. `is_sha256`으로 바꾸면 형태까지 확인하게 된다(그룹 F 판단).

## 추가한 이름

- 공개 함수·상수: 2절 표의 정본 전부
- 이름 변경: `provider_wait.timestamp` → `epoch_seconds`, `git_store._no_reparse` → `no_reparse`
- 새 키워드 인자
  - `write_bytes_atomic(fsync=)`
  - `summarize_snapshot_checks(git_dir=)`
  - `integration.require_bundle_impact_review(git_dir=)`, `apply_reviewed_knowledge_changes(git_dir=)`
- 내부 함수: `review_cycle._manifest_fault`
- 설정 키, 사건 종류, 상태 필드, CLI 인자는 추가하지 않았다. 바뀐 저장 값은 계약 식별자 `do-math-state/6` 하나다.
