# 결과 — RUN 그룹 병합

- worktree: `C:/math-worktrees/c-int`, 브랜치 `c-int`
- 병합 커밋: `640e9e340a524cb28e7c27e97cf04eaee10e370a`
  - 부모: `d380cd3`(c-int, STO·REV 병합 뒤)와 `45fee5e`(c-run)
  - 공통 기준점: `78f00bb`
- 메시지: "RUN 그룹 병합: RUN-18의 이동 위치에 STO·REV 변경을 재적용"
- push와 다른 브랜치 조작은 하지 않았다.

아래 경로는 따로 적지 않으면 `.claude/skills/do-math/scripts/` 기준이다.

## 1. 충돌마다 두 쪽의 의도와 푼 방법

### 1.1 `do_math/lifecycle_engine.py` (충돌 2곳)

**HEAD 쪽 의도.** 이 파일에서 기준점 이후 HEAD가 바꾼 것은 STO-11의 두 줄뿐이다. `git diff :1: :2:`로 확인했고, REV는 이 파일을 고치지 않았다. 두 줄의 목적은 외부 작업의 두 생산 경로가 새 저장 규칙을 지키게 하는 것이다.
- `_external_control`의 재시도 준비는 지우는 키에 `handling`을 더한다. 증거 없는 `handling=reconciled`가 남지 않게 하려는 것이다.
- `_run_external_action`의 예외 경로는 `transmitted=sent`를 함께 기록한다. 전송 전 실패가 미전송 `cancelled`로 저장되게 하려는 것이다.

**RUN 쪽 의도.** RUN-18로 두 메서드를 포함한 외부 작업 흐름 전체를 `do_math/external_engine.py`의 `ExternalEngineMixin`으로 옮겼다. 두 충돌 구역은 RUN이 옮기면서 지운 코드 덩어리였다. HEAD 쪽은 그 안의 한 줄씩을 고쳤고, RUN 쪽은 덩어리가 비어 있었다.

**해소.**
- `lifecycle_engine.py`는 c-run 판본을 택했다(`git checkout --theirs`). HEAD 쪽 변경이 두 줄뿐이므로 이 파일에서 다른 HEAD 변경을 잃지 않는다.
- STO의 두 줄은 옮겨진 위치에 다시 적용했다.
  - `external_engine.py:103`: 재시도 준비의 지우는 키에 `'handling'`을 더했다.
  - `external_engine.py:216`: 예외 경로의 `result.update(...)`에 `transmitted=sent`를 더했다.
- 병합 결과의 `git diff c-run -- external_engine.py`는 이 두 줄뿐이다.

### 1.2 `do_math/record_schemas/__init__.py` (`install`)

**HEAD 쪽 의도(STO-02).** `governance_sources`의 `validate_source`와 기록 국소 규칙 `RECORD_RULES`를 가족 검증기로 등록한다.

**RUN 쪽 의도(RUN-05).** `budget._validate_reservation`을 공개 이름 `validate_reservation`으로 바꿨다.

**해소.** 둘을 합쳤다. `from ..budget import validate_reservation`, `from ..governance import validate_source`를 import하고, `validators`에 `"reservations": validate_reservation`, `"governance_sources": validate_source`, `**RECORD_RULES`를 모두 둔다.

### 1.3 `do_math/retention.py` (`cleanup_candidates`)

두 쪽이 같은 `if` 조건의 서로 다른 부분을 지웠다.

**HEAD 쪽 의도(STO-07).** `recovery_pending`·`checkpoint_required` 조건을 지웠다. 제품에 생산자가 없기 때문이다. 남은 `recovery_disposition` 조건은 유지했다.

**RUN 쪽 의도(RUN-06).** `recovery_disposition` 조건을 지웠다. 종료 전이(`execution_lifecycle.py:92`)가 이 값을 지우므로, 이 함수가 받는 종료된 실행에서는 참이 될 수 없기 때문이다. 남은 `recovery_pending`·`checkpoint_required` 조건은 유지했다.

**해소.** 두 의도를 모두 살려 실행 필드에 기댄 조건 전체를 지웠다.
- 근거는 둘이다.
  - 이 함수는 `status != 'ended'`인 실행을 `execution_not_ended`로 막는다.
  - 병합 결과에서 `recovery_disposition`을 쓰는 곳(`engine.py:1501`, `execution_lifecycle.py:207-215`)은 모두 끝나지 않은 실행에 쓰고, 종료 전이가 그 값을 지운다.
- 따라서 이 조건은 종료된 실행에서 참이 될 수 없다.
- RUN의 설명 주석을 두 줄로 늘렸다. 종료된 실행에는 복구 표지가 없고, 끝나지 않은 복구는 아래의 `runtime` 검사(`recoveries`, `waiting_actions`)가 읽는다는 내용이다.

이 해소로 STO가 고친 시험 하나가 성립하지 않게 되었다. 2.2에 적었다.

### 1.4 `do_math/state_checks.py` (`tasks_activities_executions` 영역)

**HEAD 쪽 의도(STO-11).** 실행 `outcome` 점검을 저장 스키마로 옮기고, 점검 문구를 `'task transfers and execution reservation owners'`로 줄였다. `OUTCOMES` 점검 줄과 그 import는 자동 병합에서 이미 지워져 있었다.

**RUN 쪽 의도(RUN-05).** `_outstanding_sum`을 `outstanding_sum`으로 바꿨다.

**해소.** HEAD의 점검 문구와 RUN의 import `from .budget import outstanding_sum`을 함께 둔다. 아래 코드는 이미 `outstanding_sum(reservations.values(), ...)`로 새 서명을 따른다.

## 2. 충돌 표지 밖에서 발견해 고친 것

### 2.1 `tests/test_lifecycle_engine.py:736` — 옛 모듈을 가리키는 `patch`

STO가 STO-11의 전송 전 실패를 검사하려고 새로 쓴 시험 `test_failure_before_any_send_step_is_an_untransmitted_cancellation`이 `patch('do_math.lifecycle_engine.execute_operation', ...)`를 쓴다.

RUN-18 뒤 `execute_operation`은 `external_engine.py`만 import한다(`:5`). 따라서 옛 경로는 `AttributeError`로 실패한다. 설령 속성이 남아 있더라도, 옮겨진 `_run_external_action`에는 효과가 없다.

텍스트 충돌 없이 깨진 의미적 충돌이다. 대상을 `do_math.external_engine.execute_operation`으로 고쳤다.

### 2.2 `tests/test_redesign_SURFACE.py:583` — 없어진 입력을 검사하던 사례

STO-07은 `test_retention_requires_ended_closed_preserved_unrecovered_execution`의 차단 사례를 종료된 실행의 `"recovery_disposition": "retain_for_recheck"`로 바꿨다. 1.3의 해소 뒤 이 조건은 없다. RUN-06은 `retain_for_recheck` 값 자체도 지웠다. 그래서 이 사례는 현행 계약에서 생길 수 없는 입력을 검사하게 된다.

같은 성질("끝나지 않은 복구가 붙은 실행은 `recovery_pending`으로 정리에서 빠진다")을 현행 계약 경로로 다시 단언하게 고쳤다.
- 실행 기록에서 표지 필드를 뺐다.
- `runtime={"recoveries": {"RY-1": {..., "execution_ids": ["EX-1"]}}}`로 끝나지 않은 복구를 준다(`finished_at` 없음).
- 단언(`eligible`이 거짓이고 `recovery_pending`이 사유에 있음)은 그대로다.

### 2.3 대조했으나 고칠 것이 없던 것

- **두 쪽이 모두 바꾼 파일 17개.** 파일마다 "병합 결과와 c-run의 차이"를 "HEAD 쪽이 기준점에서 바꾼 것"과 줄 단위로 대조했다.
  - `context_store.py`, `engine.py`, `file_io.py`, `payloads.py`, `record_schemas/__init__.py`, `record_schemas/schemas.py`, `state_checks.py`, 시험 4개, `이음새-정본.md`는 둘이 정확히 같다. HEAD 변경이 빠짐없이 반영되었다.
  - `lifecycle_engine.py`의 차이는 1.1의 두 줄이다. 이 두 줄은 `external_engine.py`로 옮겨 적용했다.
  - `retention.py`의 차이는 1.3의 의도한 해소다.
  - `review_cycle.py`, `review_engine.py`, `submission.py`의 차이는 `resolve_profile`→`match_profile_ref`다. REV-21과 RUN의 HIS-14가 같은 줄을 똑같이 바꿨으므로, 병합 결과와 c-run 사이에 차이가 없는 것이 옳다.
- **옮긴 메서드의 중복 정의.** RUN-18이 옮긴 메서드 30개와 모듈 함수 `_toolchain_matches`는 각각 새 모듈에 한 번만 정의되어 있다. `ResearchEngine`의 MRO(기반 클래스 14개) 전체에서 같은 이름의 메서드가 두 클래스에 있는 경우는 0건이다.
- **옛 이름.**
  - STO·REV가 지운 이름을 제품·시험 전체에서 grep했다: `StateContract.default`, `installed_checker`, `state_errors`, `_staged_review_candidate`, `readiness_for_task`, `_split_research`, `_prior_rows`, `git_store`의 `no_reparse` import, `review_scope_assessment`, `objection_round_limit` 등.
  - RUN이 지운 이름도 같은 방식으로 grep했다: `_validate_reservation`, `_outstanding_sum`, `SCHEDULE_ACTIONS`, `independent_operator`, `retain_for_recheck`, `git_runtime`, 복구 관찰 어휘, `recover_execution`의 `observation` 인자.
  - 남은 참조는 없다. 걸린 줄은 모두 이름만 같은 다른 것이다. jsonschema의 `check_schema`, `create_execution`의 `owner_activity_id` 인자, 남는 `StateContract.register_family`, 시험 메서드 이름 세 개가 그렇다.
  - `이음새-정본.md`에도 두 쪽이 지운 이름의 행은 없다.
- **정적 해석.** 제품 모듈 83개를 import하고 AST로 두 가지를 확인했다.
  - 모든 상대 import(함수 안의 지연 import 포함)와 `모듈.속성` 참조가 해석된다.
  - 엔진 믹스인 코드의 `self._메서드(` 호출이 `ResearchEngine`의 속성이다. 예외 둘은 `self.lifecycle_monotonic(`이며, `engine.py:447`의 `_init_process_state`가 초기화하는 인스턴스 속성이다.
- **서명이 바뀐 함수.**
  - HEAD 쪽: `defer_for_research`, `_build_review_context`, `_record_review_input`, `issued_input`, `semantic_content_hash`, `assessment_basis` 등. 새 모듈 다섯과 RUN이 고친 제품 파일에서 옛 서명으로 부르는 곳은 없다. `planning_engine.py`의 `assessment_basis(task)`는 `model_policy.assessment_basis`로, 이름만 같은 다른 함수다.
  - RUN 쪽: `recover_execution`, `outstanding_sum`, `validate_reservation`. 호출자는 모두 새 서명을 쓴다. HEAD만 고친 시험이 쓰는 `SessionSlots.acquire`는 RUN이 서명을 바꾸지 않았다.
- **옛 경로의 `patch`.** 시험에서 `do_math.lifecycle_engine.*`, `do_math.scheduler.*`를 `patch`하는 곳을 모두 찾았다.
  - 2.1 외에는 `time` 계열이다. 전역 `time` 모듈의 속성을 바꾸므로 경로와 무관하게 효과가 있다.
  - `do_math.scheduler.ModelCalls`는 `scheduler.py:14`가 여전히 import한다.
- **STO-11과 RUN-06의 교차.** RUN의 새 종료 경로 `end_recovered`의 `outcome`을 추적했다. 호출자는 `provider_engine._settle_recovered_execution` 하나이고, 그 기본값은 `execution_incomplete`이며, 부르는 세 곳(`engine.py:1525`, `:1540`, `scheduler.py:143`)은 값을 따로 넘기지 않는다. 이 값은 STO가 스키마 enum으로 만든 `execution_lifecycle.OUTCOMES` 안에 있다.

## 3. 실행한 확인과 결과

| 확인 | 대상 | 결과 |
|---|---|---|
| 구문 컴파일 | `do_math/**/*.py` 전부, `operator_bootstrap.py`, 고친 시험 2개(86개 파일) | 통과. 내장 `compile()`로 검사해 바이트코드를 남기지 않았다 |
| 제품 import | `do_math` 모듈 83개 | 통과 |
| 시험 import | `tests/test_*.py` 135개, `importlib.import_module` | 135개 모두 통과, 실패 0 |
| 정적 해석·중복·옛 이름 grep | 2.3의 항목 | 남은 참조 0, 중복 정의 0 |
| 대상 시험(프로세스 1개, 백그라운드) | 아래 명령 | 통과 104, 실패 0, 오류 0(39.2초) |

대상 시험 명령은 다음과 같다. `.claude/skills/do-math`에서 실행했고, `DO_MATH_KNOWLEDGE_TEST_LEAN=C:/math/.skill-workspace/do-math-toolchains/lean-4.32.0/lean-4.32.0-windows/bin/lean.exe`를 주었다.

```
python -B scripts/run_tests.py --output C:/Users/wogud/AppData/Local/Temp/merge-run-check-1 \
  test_lifecycle_engine test_external test_state_checks test_storage_validation \
  test_redesign_SURFACE.SurfaceRedesignTests.<cleanup·retention 시험 11개>
```

- `test_lifecycle_engine`과 `test_external`은 1.1(외부 작업의 재시도와 전송 전 실패)과 2.1을 검사한다. 2.1에서 고친 시험은 보고서에서 통과로 확인했다. STO가 더한 재시도 뒤 `handling` 부재 단언이 든 `test_real_loopback_unknown_reconcile_and_retry_share_activity`도 통과했다.
- `test_storage_validation`과 `test_state_checks`는 1.2(가족 검증기 등록)와 1.4(점검 영역과 예산 합)를 검사한다.
- SURFACE의 11개는 `cleanup_candidates`를 부르는 시험 전부다. 1.3과 2.2를 검사한다.
- 보고서: `C:/Users/wogud/AppData/Local/Temp/merge-run-check-1/report.json`

조각 실행과 전체 실행은 하지 않았다. 파견문대로 통합 확인은 통합자에게 맡긴다.

## 4. 남은 위험

- **통합 확인 전이다.** 돌린 것은 충돌 코드를 검사하는 104개뿐이다. 두 그룹의 변경이 만나는 나머지 상호작용은 통합 확인에서 드러난다. 특히 둘이 크다.
  - RUN-01의 판정 주기: 게시해도 head를 옮기지 않는 시험 대역으로 소유 루프를 여러 번 배정까지 모는 시험이다. 결과-RUN 5절과 8절이 이미 경고했다.
  - STO·REV가 고친 시험 가운데 RUN이 바꾼 경로(예약·프로필 선택·복구 처분)를 지나는 것: `test_redesign_STORAGE`, `test_redesign_TASKS`, `test_repair_plan`, `test_review_engine` 등.
- **옮긴 코드의 동작 동등성은 정적으로만 봤다.** STO·REV가 옮겨진 메서드에 가한 변경은 1.1의 두 줄뿐임을 diff로 확인했다. 옮겨진 메서드가 부르는 다른 함수의 동작 변화(예: REV의 검토 흐름, STO의 저장 규칙)는 해석 가능성과 서명만 확인했고, 동작은 통합 확인에 맡긴다.
- **정적 해석의 범위.** `self._메서드(` 검사는 엔진 믹스인 클래스의 코드만 본다. 다른 객체의 속성 호출과 키워드 인자 이름의 일치는 전수로 보지 않았다. 서명이 바뀐 함수의 호출만 골라 보았다.
- **2.2의 시험 입력 변경.** 차단 사유를 끝나지 않은 `recoveries` 행으로 만든다. 같은 사유를 `test_cleanup_uses_current_recovery_completion_and_obligations`도 다른 입력으로 검사하므로, 두 시험이 겹치는 부분이 조금 생겼다. 단언의 강도는 그대로다.
- **문서.** 결과-RUN 4절의 문서 변경(`README.md:458`, `references/CLI-실행-계약.md:230`의 `role_tiers.independent_operator` → `role_tiers.recovery`)은 이 병합의 범위가 아니어서 반영하지 않았다. `.agents/` 사본 재생성도 통합자의 몫이다.
- **커밋 꼬리말.** 병합 커밋 메시지는 파견문의 제목 줄 뒤에 이 세션의 저작 표시 두 줄(`Co-Authored-By`, `Claude-Session`)을 더했다. 앞선 병합 `d380cd3`에는 이 줄이 없으므로 형식이 다르다.
