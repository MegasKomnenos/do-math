# test_retention

| 항목 | 값 |
|---|---|
| 조각 | `foundation` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_retention.py` (259행) |
| 클래스 / 테스트 | 1 / 13 |
| 시험 대상 제품 코드 | `do_math/retention.py`의 `cleanup_candidates`, `cleanup`, `retention_inputs`, `_run_path`(안에서 `reference_closure`, `_protected_paths`, `_inventory`, `_physical`, `read_stable`, `sealed_bytes`); `do_math/file_io.py`의 `RACY_NS`; `do_math/record_schemas`의 `RECORDS['recoveries']`; `do_math/repository.py`의 `ResearchRepository`(실제 Git 보관본 한 테스트) |
| 사용하는 픽스처 모듈 | `research_fixtures`: `current_state`, `git_init` |
| 격리 표지 | 없음. `test_real_windows_runs_junction_is_not_a_new_trusted_root`는 `os.name == 'nt'`일 때만 돈다 |
| 시작 상태 | 1단(보존 함수에 사전 상태와 읽기 함수를 직접 전달). 실제 임시 폴더에 실행 폴더 `runs/EX-1`을 만든다. 한 테스트는 `git_init` 저장소에 `current_state`를 직접 `initialize`한 실제 Git 보관본을 쓴다(네 단 밖: 저장소 계층 직접 초기화) |

## 목적

모듈 docstring은 "실행 폴더의 보존과 정리: 무엇을 지우고, 보관하고, 남길 수 있는지를 고정된 Git 보관본에 대조해 검사한다"고 밝힌다. 제품 `retention.py`의 docstring은 "명시적으로 승인되고 보관된 실행 공간의 보수적 정리"라고 적는다. 호출자가 인스턴스 쓰기 잠금을 쥐고, 삭제 시점에 현재 상태를 다시 공급한다. 이것은 같은 사용자의 악의적 쓰기에 대한 보안 경계가 아니다.

`cleanup_candidates`는 실행마다 정리 적격(`eligible`)과 거부 사유(`reasons`)를 계산한다. 적격이려면 다음을 모두 만족해야 한다. 실행이 끝났다(`ended`). 로컬 종료가 고정된 스냅숏의 영수증으로 확인된다. 보관 목록(`collection.retention_manifest`)의 모든 행이 보관본 바이트와 맞고, 로컬 파일 목록과 같다. 보호 참조가 없다. 미정산 예약, 대기 행동, 끝나지 않은 복구, 미결 활동 의무가 없다. 승인 범위 안이다. `cleanup`은 삭제 직전에 현재 상태로 적격을 다시 계산하고, 무엇이든 바뀌었으면 지우지 않고 저하(`degraded`)를 보고한다. 연구 상태는 바꾸지 않는다. 이 모듈은 이 규칙들과 그 경계(재분석 지점, Windows 경로 별칭, 참조 폐포)를 검사한다.

## 모듈 수준 요소

- `SCRIPTS` (행 16): 스킬의 `scripts/` 폴더. 행 17에서 존재 확인 없이 `sys.path` 맨 앞에 넣는다.
- `archived_run(root)` (행 25–44): 거의 모든 테스트의 공통 준비. `root/runs/EX-1/output.txt`에 `b'preserved result'`를 쓴다. 종료 영수증 `{'execution_id': 'EX-1', 'local_terminated': True}`의 JSON 바이트를 만들고 스냅숏을 `'a'*40`으로 둔다. `archive` 사전에는 보관 경로 두 개가 있다. `runtime/artifacts/EX-1/output.txt`는 산출물 바이트를, `runtime/artifacts/EX-1/termination.json`은 영수증을 담는다. 실행 `EX-1`은 `status='ended'`이고, `termination`에 로컬 종료, 증거 경로, 스냅숏, 해시, 길이를 가진다. `collection.retention_manifest`에는 `output.txt` 한 행(보관 경로, 스냅숏, 해시, 16바이트)이 있다. `state`는 `executions`, 빈 `protected_references` 집합, `approved_execution_ids={'EX-1'}`, 빈 `runtime`이다. 지역 함수 `read(path, commit)`는 커밋이 그 스냅숏이 아니면 `ValueError('not an archived snapshot')`를 던지고, 맞으면 `archive[path]`를 돌려준다. 반환값은 `(run, state, archive, read)`다. 기본 상태는 적격이다(`test_retention_requires_ended_closed_preserved_unrecovered_execution`가 확인한다). 사용처는 이 모듈의 테스트 10개다.
- 행 258–259: 직접 실행하면 `unittest.main(verbosity=2)`로 이 모듈의 시험을 돈다.

## RetentionTests (행 47–255)

`unittest.TestCase`를 그대로 상속한다. 표지, 속성, 훅, 도우미가 없다. 각 테스트가 임시 폴더를 스스로 열고, 대부분 모듈 함수 `archived_run`으로 준비한다.

### `test_cleanup_uses_current_recovery_completion_and_obligations` (행 48–70)
- 성질: 정리 적격은 현재 runtime의 복구 완료 여부, 대기 행동, 미정산 예약을 본다.
- 준비: `archived_run`. runtime에 끝나지 않은 복구 `RY-1`(`execution_ids=['EX-1']`, `finished_at` 없음)을 넣는다. 복구 레코드는 설치 스키마 `RECORDS['recoveries']`로 먼저 검증한다.
- 실행: `cleanup_candidates(root, **state, read_artifact=reader)`를 네 번 부른다. (1) 끝나지 않은 복구. (2) `finished_at`을 채운 복구(스키마 재검증). (3) 대기 행동 `AC-1`이 `EX-1`을 가리킴. (4) 대기를 비우고 `EX-1`이 소유한 `held` 예약 `RS-1`.
- 단언: (1) 사유에 `recovery_pending`이 있다. (2) 적격이다. (3) 사유에 `recovery_pending`이 있다. (4) 사유에 `unsettled_reservation`이 있고 부적격이다.
- 대역: 없음. 보관본 읽기는 `archived_run`의 사전 읽기 함수다.
- 비고: 이름의 "obligations"(제품 사유 `activity_obligation_pending`)는 단언하지 않는다. 대기 행동이 걸린 실행의 사유도 제품에서 `recovery_pending`으로 합쳐진다. 복구 레코드는 `finished_at`을 채우기 전과 뒤 모두 설치 스키마 `RECORDS['recoveries']`의 `validate`를 예외 없이 통과한다. 원문에 이 검증의 이유를 밝힌 주석은 없다.

### `test_retention_preserves_unpinned_receipt_and_unreadable_inventory` (행 72–89)
- 성질: 고정되지 않은 스냅숏(`HEAD`)의 영수증은 보존을 증명하지 못하고, 목록을 만들 수 없는 실행 폴더는 정리되지 않는다.
- 준비: `archived_run`. (1) 종료 영수증 스냅숏을 `'HEAD'`로 바꾸고, 커밋을 따지지 않는 읽기 함수를 쓴다. (2) 스냅숏을 되돌리고 보관 목록을 비운 뒤, `do_math.retention.os.walk`를 `onerror`에 `PermissionError('cannot list execution directory')`를 넘기고 빈 반복자를 돌려주는 함수로 바꾼다.
- 실행: 두 경우 각각 `cleanup_candidates`.
- 단언: 두 경우 모두 부적격이다. 마지막에 실행 폴더가 그대로 있다.
- 대역: (1) 관대한 읽기 람다. (2) `patch('do_math.retention.os.walk', side_effect=inaccessible)`.
- 비고: 거부 사유는 단언하지 않는다. (1)에서 제품의 `_archive_reference`가 스냅숏 모양을 검사하므로 `HEAD`는 `termination_unverified`로 거부된다. (2)에서 `_inventory`의 `onerror`는 받은 오류를 다시 던지고, `cleanup_candidates`는 그 `PermissionError`를 잡아 메시지를 사유로 적는다. 이때 로컬 목록은 `{}`로 남는다. 보관 목록도 비웠으므로 둘이 같아 `archive_does_not_cover_current_files`는 붙지 않는다. 영수증 스냅숏은 되돌렸고 승인 목록에 `EX-1`이 있으므로 다른 사유도 없다. 그래서 부적격의 유일한 원인은 목록 읽기 실패다. 목록 읽기 실패를 삼켜 빈 목록으로 다루는 구현은 이 경우를 적격으로 판정하므로 이 테스트가 잡는다. 다만 테스트는 사유 문자열을 단언하지 않는다.

### `test_cleanup_archive_failure_is_local_degradation` (행 91–102)
- 성질: 삭제 직전 재확인에서 보관본을 읽지 못하면 정리는 로컬 저하로 끝나고, 상태와 실행 폴더를 건드리지 않는다.
- 준비: `archived_run`으로 적격 후보를 계산하고, 상태의 `deepcopy`를 떠 둔다.
- 실행: `cleanup(root, candidates, current_state=lambda: state, read_artifact=failed_reader)`. `failed_reader`는 항상 `RuntimeError('archive store unavailable')`를 던진다.
- 단언: 결과 `status`가 `degraded`이고, 상태가 사본과 같으며, 실행 폴더가 남아 있다.
- 대역: `failed_reader`.

### `test_descendant_reference_blocks_cleanup` (행 104–108)
- 성질: 실행 폴더 아래 파일을 가리키는 보호 참조는 그 폴더의 정리를 막는다.
- 준비: 빈 임시 폴더. 실행은 `{'id': 'EX-1', 'status': 'ended', 'artifact_bundle': 'bundle'}` 하나이고, 보호 참조는 `{'runs/EX-1/needed.txt'}`다.
- 실행: `cleanup_candidates(Path(d), executions, protected_references=...)`. 읽기 함수, runtime, 승인 목록을 주지 않는다.
- 단언: 부적격이고, 사유에 `protected_reference`가 있다.
- 대역: 없음.
- 비고: 영수증, 보관 목록, runtime, 승인 목록이 모두 없으므로 다른 사유도 여럿 붙는다. 단언은 `protected_reference`의 존재로 사유를 고정한다.

### `test_bundle_name_alone_never_proves_preservation` (행 110–113)
- 성질: 실행 레코드에 산출물 묶음 이름(`artifact_bundle`)만 있으면 보존이 증명되지 않는다.
- 준비: 앞 테스트와 같은 실행 레코드와 빈 보호 참조.
- 실행: `cleanup_candidates`.
- 단언: 부적격이다.
- 대역: 없음.
- 비고: 사유는 단언하지 않는다. 앞 테스트처럼 영수증·보관 목록·runtime·승인 목록이 모두 빠져 있으므로 부적격 사유가 여럿 겹친다. 곧 "묶음 이름이 증명이 되지 못함"을 다른 사유와 떼어 확인하지는 않는다.

### `test_cleanup_hashes_local_files_and_archive_rows_once` (행 115–134)
- 성질: 정리는 로컬 파일을 한 번만 해시하고 이미 맞춘 보관 행을 다시 읽지 않는다. 삭제 직전 재확인은 지문(fingerprint)과 맞춘 보관 행을 재사용한다.
- 준비: `archived_run`. 읽기 함수를 `Mock(side_effect=read)`로 감싸 호출 수를 센다. 무작위 `git_dir` 이름(`'git-'+uuid`)과 빈 `marks`를 둔다.
- 실행: `file_io.RACY_NS`를 0으로 패치하고 `retention.read_stable`을 `wraps`로 감싼 채 `cleanup_candidates(..., git_dir=git_dir, marks=marks)`와 `cleanup(...)`을 부른다.
- 단언: 후보가 적격이다. 후보 계산 뒤 `(read_stable 호출 수, 읽기 호출 수)`가 `(1, 2)`다. 정리 결과 `deleted`가 `['runs/EX-1']`이다. 정리 뒤에도 `read_stable`은 1회이고, 읽기는 3회다.
- 대역: `patch.object(file_io, 'RACY_NS', 0)`, `patch.object(retention, 'read_stable', wraps=...)`, `Mock` 읽기 함수.
- 비고: 행 123의 주석은 이렇게 밝힌다. "새 파일의 생성 시각은 늙힐 수 없으므로 지난 지문을 모두 안정된 것으로 본다." `RACY_NS=0`이 그 장치다. 행 132와 134의 주석은 삭제 전 재확인이 지문과 맞춘 보관 행을 썼고, 다시 파싱한 것은 종료 영수증뿐이라고 밝힌다. 이 증가분 1이 영수증 재읽기다. 보관 행의 재사용은 제품 docstring의 `repository.VERIFIED_ARTIFACTS`(`git_dir`별 기록)에 근거한다.

### `test_retention_requires_ended_closed_preserved_unrecovered_execution` (행 136–149)
- 성질: 끝나고, 닫히고, 보관되고, 복구 중이 아닌 실행만 정리되며, 끝나지 않은 복구가 걸린 실행은 막힌다.
- 준비: `archived_run`의 기본 상태.
- 실행: `cleanup_candidates`, `cleanup`. 이어서 실행 폴더를 다시 만들고, 끝나지 않은 복구 `RY-1`이 걸린 runtime과 `artifact_bundle`만 가진 실행 레코드로 `cleanup_candidates`를 부른다.
- 단언: 기본 상태는 `eligible == True`이고, 정리가 `['runs/EX-1']`을 지우며, 폴더가 사라진다. 복구가 걸린 경우는 부적격이고 사유에 `recovery_pending`이 있다.
- 대역: 없음.
- 비고: 이 테스트가 `archived_run`의 기본 상태가 적격이라는 사실(다른 테스트들의 대조 기준)을 직접 확인한다. 둘째 부분의 실행 레코드에는 영수증과 보관 목록이 없어 다른 사유도 붙는다. 단언은 `recovery_pending`의 존재로 사유를 고정한다.

### `test_cleanup_rechecks_reference_files_and_archive_before_deletion` (행 151–168)
- 성질: 후보 계산 뒤 삭제 전에 참조, 로컬 파일, 보관본, 영수증, 예약, 복구 가운데 무엇이 바뀌어도 정리는 지우지 않고 저하로 끝나며 상태를 바꾸지 않는다.
- 준비: `subTest(mutation=...)`마다 새 임시 폴더에 `archived_run`을 만들고, 적격 후보를 계산해 적격임을 먼저 확인한다. 그 뒤 여섯 변형 가운데 하나를 가한다. `reference`는 보호 참조에 `runs/EX-1/output.txt`를 더한다. `local`은 실행 폴더에 보관되지 않은 `new.txt`를 쓴다. `archive`는 보관 산출물을 `b'corrupt'`로 바꾼다. `termination`은 보관 영수증을 `b'{}'`로 바꾼다. `reservation`은 `EX-1`이 소유한 `held` 예약을 더한다. `recovery`는 끝나지 않은 복구를 더한다.
- 실행: 상태의 `deepcopy`를 떠 둔 뒤 `cleanup(root, candidates, current_state=lambda: state, read_artifact=reader)`.
- 단언: 여섯 경우 모두 `status`가 `degraded`이고, 실행 폴더가 남아 있으며, 상태가 사본과 같다.
- 대역: 없음.
- 비고: `subTest` 6건이다. 거부 사유 문자열은 단언하지 않는다. 제품은 `'cleanup prerequisites changed: ' + 사유`를 실패 행에 적는다.

### `test_retention_resolves_real_git_archive_bytes_at_pinned_commit` (행 170–187)
- 성질: 정리는 고정된 커밋의 실제 Git 보관본 바이트로 보존을 확인하고, 지운 뒤에도 보관본은 그 커밋에서 읽힌다.
- 준비: `git_init`한 폴더에 `new_id('RI')` 인스턴스를 `current_state`(`id`, 빈 `executions`·`activities`)로 `initialize`한다. `archived_run(root/'work')`의 `archive` 사전을 `save_with_state(..., artifacts=archive)`로 실제 발행하고, 그 커밋을 영수증과 보관 목록 행의 `snapshot`에 넣는다.
- 실행: `repository.read(path, snapshot)`를 읽기 함수로 써서 `cleanup_candidates(root/'work', ...)`와 `cleanup(...)`을 부른다.
- 단언: 후보가 적격이고, `deleted`가 `['runs/EX-1']`이며, 그 커밋에서 `runtime/artifacts/EX-1/output.txt`를 읽으면 `b'preserved result'`다.
- 대역: 없음. 실제 Git 저장소와 `ResearchRepository`의 발행·읽기를 쓴다.

### `test_reparse_root_is_rejected_before_resolution` (행 189–204)
- 성질: 작업 공간의 `runs` 폴더가 재분석 지점(reparse point)이면 경로를 해석하기 전에 거부한다.
- 준비: `archived_run`. `Path.lstat`을 바꿔, `root/'runs'`에 대해서만 `st_mode=0`, `st_file_attributes=0x400`(재분석 지점 속성)인 객체를 돌려준다. 다른 경로는 원래 `lstat`을 쓴다.
- 실행: `retention.cleanup_candidates(root, **state, read_artifact=reader)`.
- 단언: 부적격이고, 사유 가운데 `'reparse'`를 포함하는 것이 있다.
- 대역: `patch.object(Path, 'lstat', lstat)`.
- 비고: 실제 재분석 지점을 만들지 않고 속성만 흉내 낸다. 실제 접합(junction)은 `test_real_windows_runs_junction_is_not_a_new_trusted_root`가 다룬다.

### `test_run_path_refuses_an_execution_id_that_windows_stores_as_another_run` (행 206–211)
- 성질: Windows가 다른 실행의 폴더로 저장할 실행 ID(끝의 마침표)는 실행 경로로 받지 않는다.
- 준비: 빈 임시 폴더.
- 실행: `_run_path(Path(d), 'EX-1.')`.
- 단언: `ValueError`를 던진다(유형만 본다).
- 대역: 없음.
- 비고: 행 207의 주석은 "Windows는 끝의 마침표를 버리므로 `EX-1.`의 폴더는 `EX-1`의 폴더가 된다"고 밝힌다. 제품 `_run_path`는 `file_io.check_path_segment`로 이 규칙을 적용한다.

### `test_real_windows_runs_junction_is_not_a_new_trusted_root` (행 214–239)
- 성질: 실제 Windows 접합으로 된 `runs` 폴더는 새 신뢰 루트가 되지 못하고, 접합으로 만든 별칭 경로의 보호 참조도 실제 실행 폴더를 보호한다.
- 준비: 임시 폴더 둘. 바깥 폴더에 `EX-1/important`(`b'keep'`)를 만든다. PowerShell `New-Item -ItemType Junction`으로 `root/runs`를 바깥 폴더에 잇는다.
- 실행: (1) `cleanup_candidates(root, {'EX-1': {'id': 'EX-1', 'status': 'ended'}}, protected_references=set())`. 그 뒤 접합을 `os.rmdir`로 지운다. (2) `archived_run(root)`로 실제 실행 폴더를 만들고, `root/protected-alias`를 그 실행 폴더에 잇는 접합을 만든다. 보호 참조를 `alias/output.txt`의 절대 경로로 두고 `cleanup_candidates`를 부른다. 끝에 별칭 접합을 지운다.
- 단언: (1) 부적격이고 사유에 `'reparse'`가 포함되며, 바깥 폴더의 `important` 파일이 `b'keep'` 그대로다. PowerShell 종료 코드가 0이다(실패하면 stderr를 메시지로 보인다). (2) 별칭 접합 생성의 종료 코드가 0이고, 결과가 부적격이며, 실행 폴더가 남아 있다.
- 대역: 없음.
- 비고: `@unittest.skipUnless(os.name == 'nt', 'Windows junction probe')`로 Windows에서만 돈다. 실제 외부 자원으로 PowerShell 자식 프로세스 두 번과 실제 NTFS 접합을 쓴다. 행 228의 주석은 정리할 때 대상이 아니라 정확히 그 임시 접합만 지운다고 밝힌다. (2)는 거부 사유를 단언하지 않는다. 별칭 경로가 물리 경로로 해석되어 `protected_reference`가 되는지, 해석 실패로 거부되는지는 이 테스트가 가리지 않는다.

### `test_reference_closure_follows_records_and_preserves_unknown_origins` (행 241–255)
- 성질: 보호 참조는 레코드들이 가리키는 참조를 따라 폐포를 이루어 실행 폴더의 파일에 닿으며, 레코드 정보가 없어 풀 수 없는 참조는 사유로 남는다.
- 준비: `archived_run`. 보호 참조를 레코드 ID `{'KN'}`으로 둔다. 저장 행 두 개를 만든다. 지식 `KN`은 `dependencies=['CP']`를 가진다. 형식 결과 `CP`는 `path='runs/EX-1/output.txt'`와 `references=['KN']`을 가진다. 이 행들로 `retention_inputs({}, {}, rows)`를 불러 참조 레코드를 만든다.
- 실행: `cleanup_candidates(..., reference_records=records)`, 그리고 `reference_records` 없이 한 번 더.
- 단언: 첫 호출의 사유에 `protected_reference`가 있다(KN에서 CP를 거쳐 실행 폴더의 파일에 닿음). 둘째 호출의 사유에 `'unresolved_reference: KN'`이 있다.
- 대역: 없음.
- 비고: 행 245의 주석은 "`retention_inputs`는 저장된 레코드마다 그 레코드가 가진 참조를 나열한다"고 밝힌다. `CP`가 다시 `KN`을 가리키는 순환도 폐포 계산이 끝나는지를 함께 보인다(단언은 결과만 본다).

## 관계

- 엔진이 정리를 부르는 경로와 그 실패가 상태 보고에 닿는 경로는 `test_reporting`의 `StatusSnapshotTests.test_engine_cleanup_failure_reaches_snapshot_reporting`이 검사한다. 이 모듈은 `retention` 함수들을 직접 부른다.
- 정리 영역의 점검 결과(중단된 정리 시도, 정리 이력이 저하의 원천이라는 규칙)는 `test_state_checks`의 `CheckAreaTests`가 검사한다.
- 재분석 지점과 물리 경계의 일반 규칙은 `test_git_store`(`test_repository_junction_is_rejected_before_resolve`, `test_physical_boundary_refuses_a_reparse_point_below_its_root`)와 `test_context_store`(`test_outside_symlink_is_reported_when_supported`)가 각자의 영역에서 검사한다.
- 보관 행을 `git_dir`별로 한 번만 읽는 규칙은 `test_repository`의 `SealedArtifactReadTests`와 같은 장치(`sealed_bytes`)를 쓴다.
- 픽스처 의존: `research_fixtures.current_state`, `git_init`(실제 Git 보관본 테스트 한 곳).
- 이 모듈에만 있는 도우미는 `archived_run`이다.
