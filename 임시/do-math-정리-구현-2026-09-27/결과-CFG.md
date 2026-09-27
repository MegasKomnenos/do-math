# 결과-CFG: 설정 검사의 이중 프로필 생성

## 1. 브랜치와 바꾼 파일

- 브랜치 `c-cfg`(worktree `C:/math-worktrees/c-cfg`), 시작 `975b8ae`, 마지막 커밋 `63dfdeb`
- 제품
  - `.claude/skills/do-math/scripts/do_math/execution_profiles.py`
  - `.claude/skills/do-math/scripts/do_math/configuration.py`
  - `.claude/skills/do-math/scripts/do_math/governance_engine.py`
  - `.claude/skills/do-math/scripts/do_math/engine.py`(configure 접수 두 줄)
- 시험: `.claude/skills/do-math/scripts/tests/test_connection_repairs.py`. `HostConfigurationTests`에 시험 하나를 더했다.
- 문서: `.claude/skills/do-math/scripts/이음새-정본.md` 6절. `DEFAULT_CONFIG`, `validate_config(config)` 행을 고치고 `validate_host_resources(host)` 행을 새로 두었다.

## 2. 처분

| 항목 | 처분 | 내용 |
|---|---|---|
| 설정 검사 이중 프로필 생성 | 구현함 | `validate_config`는 이제 프로필을 만들지 않고 값을 돌려주지 않는다. 호스트 절은 새 공유 함수 `execution_profiles.validate_host_resources`로 검사하고, `config["host_resources"]["constraint"]["host_id"]`를 직접 `platform.node()`와 비교한다. `build_profiles`는 같은 함수를 부른다. 그래서 호스트 절의 검사 사본은 하나뿐이다. OPS가 더한 반환값 계약을 지웠다. 재사용 분기 두 곳도 지웠다. `engine.control`에서는 `if validate_config(candidate) is None:`을 없앴고, `governance_engine._configure_candidate`에서는 `checked`·`checked_editions` 판정을 없앴다. 초기화, configure 접수, configure 적용이 각각 `build_profiles`를 한 번만 부른다. 통합자 제안 2번과 다른 점은 7절에 적는다. |

## 3. 공유 정의와 지운 공개 이름

- 새 공유 정의: `execution_profiles.validate_host_resources(host) -> None`(`execution_profiles.py`, `build_profiles` 바로 앞).
  - 검사 내용은 지금까지 `build_profiles` 안에 있던 호스트 절 검사 전부다. 절 모양 `{"constraint", "demands_by_role"}`, `validate_host_constraint`, 요구량의 `_host_amounts`, 누락된 상한 역할, 상한 없는 역할의 요구량이 여기에 든다. 마지막 검사는 전에는 프로필을 다 만든 뒤에 했지만, 이제 함수 끝에서 한다.
  - 소비자는 `build_profiles`와 `configuration.validate_config` 두 곳이다. 이음새 정본 6절에 행을 두었다.
- 지운 공개 계약: `validate_config`의 반환값. 이제 `-> None`이다. 공개 이름을 지우지는 않았다.

## 4. 필요한 문서 변경

- `scripts/이음새-정본.md` 6절은 이 커밋에서 고쳤다.
- 스킬 문서 가운데 이 반환값을 언급하는 곳은 없다. `SKILL.md`, `README.md`, `GLOSSARY.md`, `references/`를 grep으로 확인했다. 따라서 더 할 문서 변경은 없다.
- `.agents/` 사본은 통합자가 재생성한다.

## 5. 실행한 시험

- 컴파일: 바꾼 제품 네 파일과 시험 한 파일을 `python -m py_compile`로 컴파일했다. 오류는 없다.
- 전체 import: `scripts/tests`의 `test_*.py` 132개 모듈을 `importlib.import_module`로 적재했다. 오류는 없다.
- 옛 이름 grep: `checked_editions`, `is None:  # a host configuration`, `validate_config(...) is None`은 제품, 시험, 스킬 문서 어디에도 남지 않았다.
- 편집 확인: `python -m unittest test_connection_repairs.HostConfigurationTests`(scripts/tests에서)를 돌렸다. 4개 모두 통과했다.
- 새 시험이 옛 코드에서 실패하는지도 확인했다. 방법은 이렇다. 임시 사본에서 제품 네 파일만 `975b8ae` 판본으로 되돌리고, 새 시험 `test_host_configuration_builds_profiles_once_per_step`를 돌렸다. 결과는 `AssertionError: 2 != 1`로 실패였고, 실패 지점은 초기화였다.
- 인계 확인: 한 프로세스로 아래 명령을 돌렸다.

  ```
  python -m unittest test_connection_repairs test_host_resources test_redesign_PROFILES test_current_contract test_governance_engine test_engine test_control_shapes test_session_scheduler
  ```

  148개 시험, 317.7초가 걸렸다. 실패 2, 오류 0, 나머지는 통과했다.
  - 실패 둘은 모두 변경 전부터 있던 것이다.
    - `test_redesign_PROFILES.ProfileTests.test_recovery_never_restarts_with_unknown_local_termination`: `'recovery_waiting' != 'recovery_termination_unknown'`
    - `test_redesign_PROFILES.ProfileTests.test_recovery_requires_current_profile_capability_before_reservation`: 사유가 `'installation maintenance is already active'`로 나왔다.
  - 두 시험을 `git archive 975b8ae`로 뽑은 원본 트리에서 다시 돌려도 똑같이 실패했다.
  - 원인은 8절에 적는다. 이번 변경과는 무관하다. 두 시험은 호스트 절이 없는 `PROFILE_CONFIG`만 쓴다.
- 돌리지 않은 관련 시험은 configure 소비자 모듈이다. `test_cli`, `test_operator`, `test_input_recovery`, `test_repair_plan`, `test_research_recovery`, `test_observation_admission`, `test_model_assessment_flow`, `test_approved_five_repairs`가 여기에 든다. 이유는 시험 지침 2절이다. 소비자 쪽은 컴파일, import, grep으로만 확인하고 통합 확인에 맡긴다.

## 6. 기능이나 시험 범위가 바뀐 것

- 대상: `validate_config`가 호스트 설정일 때 하던 검사.
- 이유: 호스트 절 하나를 확인하려고 모든 역할·층의 프로필을 봉인하던 일을 없앴다.
- 잃는 것: 없다. 호스트 설정이 있을 때에 한해 `build_profiles`가 부수적으로 하던 비호스트 검사는 모두 다른 곳이 이미 덮는다.
  - "tier model has no adopted capacity"는 `model_policy.validate_policy`가 먼저 막는다. 모든 층 모델이 `session_limits.work`에 있어야 한다는 규칙이다.
  - `provider_for`와 `seal_profile`은 예외를 내지 않는다.
  - `_lean_contract`의 `discover_lean`은 예외 없는 환경 탐색이고, 설정 검사가 아니다.
  - 이 비호스트 검사들은 원래 호스트 설정이 없으면 `validate_config`에서 돌지 않았다. 규칙이라기보다 우연한 부수효과였다.
- 얻는 것:
  - 검사 경로에서 프로필 생성이 사라졌다. 적재 검사 `engine.check`와 가져오기 검증 `governance.register_configuration_owner`가 그 경로다.
  - 저장하는 경로는 한 번씩만 만든다.
  - 시험 범위: 호출 횟수를 세는 시험 하나를 더했다. 기존 단언은 바꾸지 않았다.

## 7. 접근을 바꾼 지점과 예상과 다른 결과

- 통합자 제안 2번과 다르게 했다. 제안은 호스트 절의 나머지 검사를 `build_profiles` 쪽에만 두는 것이었다. 그러나 `validate_config`를 부르고 `build_profiles`를 부르지 않는 경로가 둘 있다.
  - `engine.check`의 `validate_config(instance["config"])`(`engine.py:4180` 부근).
  - `governance.register_configuration_owner`의 `validate`(`governance.py:825` 부근). 가져오기 단위를 적용 전에 검증하는 곳이다. 적용은 뒤에 `_configure_candidate`를 거친다.

  이 두 경로에서는 역할별 요구량 누락, 상한 없는 역할의 요구량, 결박 전 별칭 제약의 자기 일관성 검사가 빠졌을 것이다. 별칭 제약의 자기 일관성이란 `id`가 본문 해시와 맞는 봉인 판본인지를 말한다. 저장 관문(`record_schemas/__init__.py`의 `authored_host` 절)은 `validate_host_constraint`와 등록 판본 일치만 보고 역할별 요구량은 보지 않는다. 또 기존 시험 `test_host_demands_accept_only_capped_roles`가 `validate_config`에서 `capped roles only`와 `capped role` 오류를 단언한다.

  그래서 검사를 옮기지 않고 한 함수로 뽑아 두 곳이 같이 부르게 했다. 사본은 여전히 하나이고, 검사 강도는 모든 경로에서 전과 같다. `build_profiles`만 쓰는 경로에서 추가 비용은 제약 해시 한 번이다. 새 상태, 캐시, 반환 계약은 없다.
- 별칭 모양을 확인했다. 결박 전 호스트 절의 제약은 `host_constraint(...)`로 봉인한 완전한 host 제약이며, `authority_refs`에 `configuration:request`가 든다. 시험 픽스처 `test_connection_repairs.HostConfigurationTests.configuration`이 그렇게 만들고, 결박 함수 `governance_engine.bind_host_configuration`도 그 필드들을 읽어 다시 봉인한다.
  - 따라서 `host_id`는 별칭 모양이든 결박 뒤든 `constraint["host_id"]`에 있다. 직접 읽는 데 별도 처리가 필요 없다.
  - `validate_host_resources`는 `validate_host_constraint`로 별칭 제약을 받아들인다. `host_constraint`는 비지 않은 문자열 권한만 요구한다.
  - `validate_config`가 저장 스키마 검사에서 `host_resources`를 빼는 것은 그대로 두었다. 별칭 `configuration:request`가 ID 패턴(`REFS`)에 맞지 않기 때문이다. 이 이유에 맞게 주석을 고쳤다.
- `validate_config`의 모든 호출자와 각 경로의 처리.
  - 제품
    - `engine.initialize`: `validate_config` → 결박 → `build_profiles` 한 번.
    - `engine.control` configure 접수: `validate_config` → `build_profiles` 한 번. 접수 시점의 조기 거부용이다.
    - `_configure_candidate`: `validate_config` → 결박·서버 해석 → `build_profiles` 한 번.
    - `engine.check`: 검사만 한다. 공유 함수가 호스트 절 전체를 검사한다.
    - `governance.register_configuration_owner.validate`: 검사만 한다. 적용은 `_configure_candidate`가 맡는다.
  - 시험: `test_claude_adapter`, `test_connection_repairs`, `test_current_contract`, `test_redesign_ENGINE`, `test_redesign_PROFILES`, `test_session_scheduler`, `test_engine`(import만)이 `validate_config`를 부른다. 반환값을 쓰는 곳은 없었다.
- OPS가 `_configure_candidate`에서 결박 뒤의 두 번째 `validate_config`를 지운 결정은 유지했다. 결박은 `host_resources`의 권한 참조만 바꾸고 `host_id`는 바꾸지 않는다. 결박된 절은 이어지는 `build_profiles`가 공유 함수로 검사한다.

## 8. 다른 그룹 범위에서 발견한 문제

- `test_redesign_PROFILES`의 회복 시험 둘이 통합 브랜치 `975b8ae`에서 실패한다. 5절의 두 시험이다.
  - 원인은 `cdcaffd`에 있다. 이 커밋이 `scheduled_operator.py:487`의 잠금 경로를 `repo._store._git_dir`에서 공개 속성 `repo.git_dir`로 바꿨다. 그런데 시험 쪽 이중체 `test_redesign_PROFILES.repository_double`(18~35행)은 여전히 `repo._store._git_dir = root`만 설정한다.
  - 그래서 autospec 이중체의 `repo.git_dir`로 잠금 파일을 열지 못하고, `os_lock`이 `OSError` 경로로 떨어져 `installation maintenance is already active`를 돌려준다.
  - 이중체가 `repo.git_dir = root`를 설정하면 된다. 이 모듈은 TORG 작업자가 재편하는 중이라 고치지 않았다.
- 관찰 하나(고치지 않음): `engine.control`의 configure 접수는 조기 거부만을 위해 `build_profiles`를 부르고 결과를 버린다. 호스트 설정이 없어도 그렇다. 그 사이에 설정이 바뀌지 않았다면 적용 시점의 `_configure_candidate`가 같은 설정으로 다시 만든다.
  - 이 조기 거부는 OPS 이전부터 있던 동작이다. 호출마다 한 번씩 만든다는 이번 목표도 어기지 않는다.
  - 다만 호스트 절 밖에서 `build_profiles`만 내는 거부는 이제 사실상 없다. 6절의 근거가 그것이다. 그러니 접수 시점에는 `validate_config`만 남기는 단순화를 검토할 수 있다. 결정은 통합자 또는 ENG 영역에 맡긴다.
