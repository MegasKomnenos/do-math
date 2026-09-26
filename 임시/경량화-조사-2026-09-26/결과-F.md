# 결과-F: 운영 거버넌스·초기화·보고·스크립트

이 문서는 do-math 경량화 2라운드 그룹 F의 반환이다. 설계 `docs/do-math/경량화-설계-2026-09-26.md` 6절의 다섯 항목을 순서대로 적고, 기존 이음새 계약 10절의 `이음새 요청`·`추가한 이름`을 덧붙인다.

- worktree `C:/math-worktrees/r2-f`, 브랜치 `r2-f`, 기준 커밋 `24682fd`(커널 병합)
- 커밋 `daba0fa`(본 변경), `b45e8cf`(OPS-09의 네 번째 사본 교체)
- 좌표는 따로 적지 않으면 `C:/math-worktrees/r2-f/.claude/skills/do-math/scripts/` 기준의 현재(`b45e8cf`) 행 번호다.
- 시험은 실행하지 않았다. 바꾼 Python 파일 20개가 모두 `python -m py_compile`을 통과했다.

## 1. ID별 처분

4.7절의 8개 ID를 모두 구현했다. 조사 제안과 방법이 다른 곳은 비고와 5절에 근거 좌표와 함께 적었다.

| ID | 처분 | 내용 |
|---|---|---|
| OPS-06 | 구현함 | `reporting.timeline`의 `include_operator` 인자와 `operator/runs/*/result.json` 읽기 분기를 지웠다. 이 분기만 쓰던 `hashlib` import도 지웠다. CLI의 `--include-operator` 플래그(`cli.py`)와 전달 인자를 지웠다. 시험 `test_reporting.test_local_operator_evidence_has_its_own_hash_and_count_unit`을 삭제했다. 운영 로그를 보는 경로는 `--include-operations`만 남는다. 문서 변경은 3절에 있다. |
| OPS-08 | 구현함(방법 변형) | 설치 파일 집합을 `file_io.installation_files(root)` 하나로 정의했다(`file_io.py:267`). 규칙은 bootstrap의 기존 규칙이다. `__pycache__`·`.git`·`.lake`·`scripts/tests`·`.pyc`를 빼고 나머지 모든 파일을 넣는다. `repair_execution.installation_sha256`과 `operator_bootstrap._source_paths(root, file_io)`가 이 함수를 쓴다. bootstrap은 자기 스냅숏 표지 두 파일(`MANIFEST`, `MARKS`)만 추가로 빼고, 각 파일에 `_ordinary_path`를 적용한다. 운영 문서 목록은 두 상수로 나눴다(5절). `contracts.OPERATING_DOCUMENTS`(`contracts.py:262`)는 엔진 `_installation_manifest`가 읽는다. `preflight.INSTALLED_DOCUMENTS`(`preflight.py:19`)는 `inspect_bundle`과 `test_preflight`가 읽는다. 동작 변경은 두 가지다. 복구 식별은 이제 시험 파일을 빼고 `examples/*`·`.gitattributes`를 넣는다. `inspect_bundle`은 `scripts/do_math.py`도 검사한다. |
| OPS-09 | 구현함(범위 확장) | `governance.grant_time_reason(grant, now)`(`governance.py:381`)가 유효 구간 `[valid_from, expires_at)`의 유일한 정의다. 사용처는 `_grant_scope_reason`, `expire_grants`, `initialization.grant_current`(`initialization.py:250`)이다. 조사에 없던 네 번째 사본 `external.validate_operation`(기준 커밋 `external.py:50-51`)도 이 함수로 바꿨다(5절). `governance.normalized_grant(spec, *, gid, created_at, source_ref, decision_id)`(`governance.py:388`)는 생산자 `apply_decision`과 수신자 `validate_grant_source`가 함께 쓴다. 목록 필드 다섯 개는 `GRANT_LIST_FIELDS` 상수가 가진다. 조사가 확인하라고 한 `expires_at` 처리는 두 경로 모두 `spec.get("expires_at")`와 같은 값이었다. |
| OPS-10 | 구현함 | 결정 소유 종류 집합 리터럴 5곳을 `DECISION_OWNER_KINDS`(`governance.py:25`)로 바꿨다. 사용처는 `register_import_owner`, `import_consumer_catalog`의 두 줄, `validate_import_units`, `_current_import`다. 해석 검사 판정 어휘는 `INTERPRETATION_DECISIONS`(`governance.py:27`)로 바꿨다. 사용처는 수신 검사 `check_import`, 출력 스키마 `interpretation_schema`(`list(...)`), 그리고 조사에 없던 `prepare_import`의 선행 import 상태 집합(`governance.py:961`)이다. 선행 import의 `status`는 `check_import`가 판정값 또는 `unresolved`로 정하므로 같은 어휘다. `governance_engine.bind_host_configuration`의 식별자는 `exact_content_hash({'host_resources': host})`로 계산한다. 값은 이전과 바이트가 같다. 지역 `import hashlib`은 지웠다. |
| OPS-11 | 구현함 | `engine._governance`의 본문을 `initialization.governance_or_initial_view(instance, runtime)`(`initialization.py:93`)로 옮겼다. `engine._governance`는 이 함수를 부르는 한 줄이다. 호출부 5곳을 그대로 두어 `engine.py`의 변경 줄을 줄였다. `reporting.snapshot_report`는 같은 함수의 `['goal']`을 쓴다. 죽은 분기 `instance.get('goal')`은 지웠다. 동작 변경은 두 가지다. 초기화 중 snapshot의 `status --snapshot`은 이제 최초 입력의 목표를 보인다. 헌장이 없는 비초기화 상태에서는 라이브 `status`처럼 `ValueError("no unique approved charter")`가 난다. 전에는 `goal: None`을 돌려주었다. |
| OPS-12 | 구현함 | `governance_engine._governance_control`의 사전 원문 대조 4행(기준 커밋 `governance_engine.py:227-230`)을 지웠다. 같은 비교는 `apply_import_control` → `_current_import`(`governance.py:999-1000`)가 한다. 실패 문구는 "original source changed before later approval"에서 "original public input changed"로 바뀐다. 이 문구를 단언하는 시험은 없다(`grep -rn "before later approval" tests` 무결과). |
| OPS-15 | 구현함 | `scripts/probe_codex.py`를 삭제했다. `tests/test_probe_codex.py`에서 이 스크립트만 실행하던 `test_missing_cli_preserves_failed_report_and_runs_no_cases`와 그 시험만 쓰던 import 3개를 지웠다. 남은 `probe_cli` 시험의 파일은 대상 이름에 맞게 `tests/test_probe_cli.py`로 옮겼다. |
| OPS-16 | 구현함 | 결정 6에 따라 `scripts/probe_native_isolation.py`를 삭제했다. 이 모듈만 검사하던 `tests/test_native_probe.py`를 삭제하고, `test_categories.UNIT_MODULES`에서 `test_native_probe`를 뺐다. `tests/test_standalone.py`에서 `import probe_native_isolation`과 `test_native_probe_help_does_not_require_repository_ancestors`를 지웠다. |

커널 K-제품이 그룹 F에 넘긴 두 요청의 처분은 다음과 같다.

- `governance.py:99`의 문서 해시 길이 확인을 `is_sha256`으로 바꿨다. 이제 소문자 16진 형태까지 확인한다.
- `governance.WORK_ROLES`의 이름 변경은 하지 않았다. 이 요청은 4.7절 표의 항목이 아니다. 또 유일한 시험 사용처 `tests/test_lifecycle_engine.py:15, 50`이 그룹 A의 결정 4가 고칠 grant 구성과 붙어 있다. 요청은 아래 이음새 요청으로 다시 올린다.

## 2. 필요했지만 커널에 없던 공유 정의

| 정의 | 위치 | 쓰는 곳 | 비고 |
|---|---|---|---|
| `installation_files(root)` | `do_math/file_io.py:267` | `repair_execution.installation_sha256`, `operator_bootstrap._source_paths` | F 소유 모듈이 아니라 `file_io`에 두었다. 이유는 5절 2번이다. 조사 OPS-08 제안이 `file_io`를 위치로 적었다. 통합자가 이음새 계약 2절(S2)에 올리기를 요청한다. |
| `OPERATING_DOCUMENTS` | `do_math/contracts.py:262`(그룹 C 모듈) | `engine._installation_manifest`, `preflight.INSTALLED_DOCUMENTS` | 조사 OPS-08 제안의 위치를 따랐다. 상수 한 줄만 추가했다. |

그룹 F 모듈 안에 만든 정의(`grant_time_reason`, `normalized_grant`, `governance_or_initial_view` 등)는 아래 `추가한 이름`에 적었다. 이 정의들은 다른 그룹의 사본을 대체하지 않는다. 예외는 `external.validate_operation`이 `grant_time_reason`을 부르게 한 호출부 교체 하나다.

## 3. 필요한 문서 변경

| 문서와 위치 | 바꿀 내용 | 근거 |
|---|---|---|
| `README.md:517` | `--include-operator` 문장을 지운다. 문단 끝의 "겹친 실행 시간의 합계를 실제 경과 시간으로 사용하지 않는다"는 `--include-operations`에도 해당하므로, 남길지 문서 단계가 판단한다. | OPS-06 |
| `references/CLI-실행-계약.md:958` | timeline 사용법에서 `[--include-operator]`를 지운다. | OPS-06 |
| `references/CLI-실행-계약.md:917` | `scripts/probe_codex.py` 설명 두 문장("`scripts/probe_codex.py`는 … 검사한다. 이 도구는 `--skill-only`를 제공하지 않는다.")을 지운다. Codex 실호출 검사는 `probe_cli.py --provider codex`가 맡는다. | 결정 6, OPS-15 |
| `계약/독립-운영.md:27`, `:61` 또는 `references/CLI-실행-계약.md:828` | "같은 설치 판본"의 범위를 한 곳에 적는다. 설치 판본은 스킬 트리 전체 파일에서 `scripts/tests`, 바이트코드 캐시, VCS·빌드 산출을 뺀 집합이다. 따라서 회귀 시험만 추가해도 같은 실패의 자동 복구는 다시 열리지 않는다. | OPS-08의 동작 변경 |
| `docs/do-math/검사-경량화-이음새-계약.md` | 2절(S2)에 `file_io.installation_files`를 설치 파일 집합의 정본으로 추가한다. | OPS-08 |
| `.agents/skills/do-math/` 미러 | 삭제한 두 스크립트와 시험 파일 이동을 미러 재생성으로 반영한다. | 결정 6 |

`status --snapshot`의 목표 표시(OPS-11)를 따로 설명한 스킬 문서는 찾지 못했다(`grep -rn "unadopted\|goal: unknown" --include=*.md` 무결과). 그래서 문서 변경은 없다.

## 4. 고친 시험과 확인하지 못한 위험

### 고친 시험 파일

- `tests/test_reporting.py`: 삭제한 경로의 시험 하나를 지웠다(OPS-06).
- `tests/test_cli.py`: `test_audit_public_check_json_discovery_and_fixed_snapshot`에 초기화 중 snapshot의 `goal`이 최초 입력 목표 `'Prove a small theorem'`인지 확인하는 단언을 더했다(OPS-11).
- `tests/test_redesign_SURFACE.py`: `test_json_and_human_status_share_one_snapshot`은 헌장 없는 최소 상태를 저장했다. OPS-11 뒤에는 이런 비초기화 상태에서 `snapshot_report`가 오류를 낸다. 그래서 시험 상태를 같은 파일의 `surface_state()`로 만들고 `goal == "Prove P"`를 단언한다. 저장 방식은 `test_reporting.test_fixed_snapshot_preserves_unknown_times_and_crosses_the_kst_date`와 같다.
- `tests/test_preflight.py`: 운영 문서 목록 사본을 `INSTALLED_DOCUMENTS` import로 바꿨다(OPS-08).
- `tests/test_repair_execution.py`: `InstallationIdentityTests`를 더했다. 시험 파일만 바뀌면 복구 식별이 그대로이고, `examples/*.json`이 바뀌면 식별이 바뀌는지 확인한다(OPS-08).
- `tests/test_probe_codex.py` → `tests/test_probe_cli.py`: `probe_codex` 시험을 삭제하고 파일을 옮겼다(OPS-15).
- `tests/test_native_probe.py` 삭제, `tests/test_standalone.py`·`test_categories.py` 수정(OPS-16).

### 실행하지 않아 확인하지 못한 위험

- `snapshot_report`는 이제 헌장 없는 비초기화 상태에서 오류를 낸다. 호출하는 시험은 `test_cli.py:160`, `test_redesign_SURFACE.py`의 두 곳, `test_reporting.py:87, 93`이다. 네 곳 모두 상태를 읽고 초기화 중이거나 헌장이 있음을 확인했다. CLI를 거쳐 `status --snapshot`을 부르는 다른 시험은 grep으로 찾지 못했다.
- 그룹 B의 OPS-07은 lifecycle 없는 상태를 적재 단계에서 거부한다. `surface_state()`에는 lifecycle이 없으므로, 위의 `test_redesign_SURFACE` 수정은 B의 fixture 수정과 같은 함수·시험에서 만날 수 있다.
- `operator_bootstrap._source_paths`는 재분석 검사를 디렉터리 항목이 아니라 반환된 파일마다 적용한다. `_ordinary_path`는 파일의 모든 조상을 검사하므로, 파일을 담은 재분석 디렉터리는 전과 같이 거부된다. 파일이 없는 재분석 디렉터리는 이제 거부하지 않는다. 이 경우는 사본에 아무것도 넣지 않는다. `test_operator_bootstrap.py`의 네 시험은 실행하지 않았다.
- 복구 식별의 파일 집합이 바뀌어 `.gitattributes`, `examples/claude-codex-sessions.json`, `examples/nat-add-zero.txt`가 들어간다. 식별값을 직접 단언하는 시험은 없다. 시험들은 `installation_sha256`을 patch한다(`test_redesign_PROFILES.py:687`, `test_repair_execution.py:97`).
- `external.validate_operation`은 이제 grant에 시간 경계가 없어도 `parse_utc(now_iso)`를 계산한다. 따라서 형식이 틀린 `now_iso`는 전과 달리 `ValueError`가 된다. 호출자는 엔진 시각 또는 `submission`의 고정값(`basis_time` 또는 `"1970-01-01T00:00:00+00:00"`)을 넘긴다. `governance`는 `external`을 모듈 수준에서 import하므로 순환을 피하려고 함수 안에서 import했다. 제출 도구 환경에서 이 import가 되는지는 실행으로 확인하지 않았다.
- `inspect_bundle`은 이제 `scripts/do_math.py`의 비어 있지 않은 UTF-8도 검사한다. `test_preflight.PreflightTests`는 같은 상수로 임시 설치를 만드므로 함께 맞는다.
- 문법 확인 밖의 실행은 한 번 했다. 제품 트리에서 `installation_files('..')`를 읽기 전용으로 호출해 116개 파일을 확인했다. 이 수는 조사가 bootstrap 사본으로 센 116과 같다. 두 스크립트 삭제 전의 트리다. 시험 실행은 아니다.

## 5. 전제가 틀렸거나 계획을 바꾼 지점

1. **OPS-08 운영 문서 목록은 두 벌이 아니라 서로 다른 두 집합이다.** 기준 커밋 `preflight.py:107-108`은 5개(`README.md`, `references/CLI-실행-계약.md`, `계약/독립-운영.md`, `scripts/operator_schedule.ps1`, `requirements.txt`)를 검사한다. `engine.py:590`은 3개(`계약/독립-운영.md`, `scripts/operator_schedule.ps1`, `scripts/do_math.py`)를 실행 판본에 넣는다. 한 상수로 합치면 엔진 manifest에 `README.md` 등이 들어간다. 그러면 운전자 문서를 고칠 때 실행 중 연구가 정지한다. 조사 자신의 보존 판정(`OPS.md:329`)이 이 확장을 막는다. 그래서 같은 결과, 곧 각 이름을 한 곳에만 적는 상태를 두 상수로 냈다. 엔진의 3개는 `OPERATING_DOCUMENTS` 하나다. preflight는 그 위에 운전자 문서 3개를 더한 `INSTALLED_DOCUMENTS`다. 시험 사본은 사라졌다.
2. **`installation_files`를 F 소유 모듈이 아니라 `file_io`에 두었다.** 개정된 3.2절은 필요한 공유 정의를 자기 그룹 모듈에 두라고 한다. 그러나 F 소유 후보 `repair_execution`은 이 정의의 소비자 bootstrap이 쓸 수 없다. frozen bootstrap은 스냅숏 해시를 확인하기 전에 `do_math.file_io` 하나만 import한다(`operator_bootstrap.py:41-46` `_file_io`, 호출은 `:70`). 그 뒤 manifest의 모든 파일을 대조한다. `repair_execution`은 `activities`·`git_store`·`repository`를 모듈 수준에서 import한다(`repair_execution.py:7-9`). 그래서 bootstrap이 이 모듈을 import하면 확인 전의 스냅숏 코드가 실행된다. 이 보증을 검사하는 시험이 `test_operator_bootstrap.test_changed_frozen_code_is_rejected_before_import`다. 다른 F 모듈인 `operator_bootstrap.py`는 패키지 밖 스크립트라 `repair_execution`이 import할 수 없다. 추가 위치는 `file_io`의 끝이다. 통합자가 위치를 바꾸려면 bootstrap이 확인 전에 import하는 모듈 집합을 함께 정해야 한다.
3. **OPS-09의 규칙 사본은 셋이 아니라 넷이었다.** `external.validate_operation`(기준 커밋 `external.py:50-51`)이 같은 부등호와 같은 오류 문구로 같은 규칙을 적고 있었다. 이 사본은 그룹 D 모듈에 있다. 3.2절이 허용하는 호출부 교체로 두 줄을 `grant_time_reason` 호출 세 줄로 바꿨다. `task_scope.py:156-158`의 비슷한 식은 grant가 아니라 결정 기록의 효력이다. 다른 개념이므로 두었다.
4. **OPS-10의 어휘 사용처는 둘이 아니라 셋이었다.** `prepare_import`(`governance.py:961`)의 선행 import 상태 집합도 같은 어휘라 함께 바꿨다. `contracts.py:144`, `engine.py:2190, 4286`의 같은 세 낱말은 계약 검토 판정이라 개념이 다르다. 이 셋은 두었다.
5. **OPS-11은 오류 동작을 바꾼다.** 조사는 "대체 분기는 항상 `None`"이라고만 적었다. 실제로 `governance_view`는 헌장이 없으면 `ValueError`를 낸다(`governance.py:157`). 그래서 헌장 없는 최소 상태를 쓰던 시험 하나를 현행 상태로 고쳤다(4절).
6. **작문 절차.** `write-for-reader`의 합의·독자 파일과 별도 독해(`writing_flow.py`)는 수행하지 않았다. 설계 6절이 산출 파일 하나를 정했기 때문이다. 스킬의 품질 규칙과 에이전트 반환 규칙만 적용했다.

## 이음새 요청

- `file_io.installation_files`를 이음새 계약 2절에 설치 파일 집합의 정본으로 올린다(2절, 5절 2번).
- 그룹 A의 결정 4가 F 모듈을 고쳐야 한다. `initialization.operations_capacity_available`(`initialization.py:147`)은 `SessionSlots.snapshot()['operations']`을 읽는다. `activation_requirements`가 그 결과로 `operations_capacity`를 누락 항목에 넣는다. `initialization.grant_current`(`initialization.py:245`)는 초기 grant에 `budget_kind == "operations"`를 요구한다. `governance._grant_scope_reason`의 `budget_kind` 대조(`governance.py:408`)도 운영 풀 값에 걸린다. F는 이 줄들을 고치지 않았다. F의 변경 줄(`initialization.py:250`, `governance.py:381-402`)은 이 줄들과 떨어져 있다.
- `governance.WORK_ROLES`는 `formal_check`를 포함해 `execution_profiles.WORK_ROLES`와 뜻이 다른데 이름이 같다(`governance.py:19`). `AUTHORIZED_WORK_ROLES` 같은 이름으로 바꿀지 통합 단계에서 정한다. 바꿀 곳은 `governance.py:19, 325, 572`과 `tests/test_lifecycle_engine.py:15, 50`이다.

## 추가한 이름

- 공개 함수: `governance.grant_time_reason`, `governance.normalized_grant`, `initialization.governance_or_initial_view`, `file_io.installation_files`
- 상수: `governance.DECISION_OWNER_KINDS`, `governance.INTERPRETATION_DECISIONS`, `governance.GRANT_LIST_FIELDS`, `contracts.OPERATING_DOCUMENTS`, `preflight.INSTALLED_DOCUMENTS`
- 서명 변경: `operator_bootstrap._source_paths(root)` → `_source_paths(root, file_io)`
- 제거: CLI 인자 `timeline --include-operator`, `reporting.timeline`의 키워드 `include_operator`, 스크립트 `probe_codex.py`·`probe_native_isolation.py`, 시험 모듈 `test_native_probe`, 시험 모듈 이름 `test_probe_codex`(→ `test_probe_cli`)
- 설정 키, 사건 종류, 상태 필드는 추가하지 않았다.
