# 결과 — RES 그룹 병합

- worktree: `C:/math-worktrees/c-int`, 브랜치 `c-int`
- 병합 커밋: `c22cb980f8efec5eddbef84b43fdc2b1059aa46e`
  - 부모: `640e9e3`(c-int, RUN 병합 뒤)와 `c1aa372`(c-res)
  - 공통 기준점: `d7d1b39`(STO 커밋)
- 메시지: "RES 그룹 병합: RUN-18 이동 위치에 RES 변경을 재적용"
  - 제목 줄 뒤에 세션 저작 표시 두 줄(`Co-Authored-By`, `Claude-Session`)이 붙어 있다. 이유는 4절 끝에 적었다.
- push와 다른 브랜치 조작은 하지 않았다.

아래 경로는 따로 적지 않으면 `.claude/skills/do-math/scripts/` 기준이다.

공통 기준점이 파견문이 가정한 `d380cd3`이 아니라 `d7d1b39`이다. RES는 STO 뒤, REV 병합 전에 갈라졌다. 그래서 HEAD 쪽 변경은 REV와 RUN을 모두 담는다. RES의 두 번째 커밋 `c1aa372`은 REV-10이 연 `assessment_current(..., records=)` 인자에 기대는데, 병합 결과의 `task_scope.py:282`에 이 인자가 있다.

## 1. 충돌마다 두 쪽의 의도와 푼 방법

충돌한 두 파일(`do_math/lifecycle_engine.py` 3곳, `do_math/scheduler.py` 1곳)은 모두 HEAD 판본(RUN-18 구조)을 택했다. 그다음 RES가 기준점에서 바꾼 hunk를 하나씩 해당 위치에 다시 적용했다. 두 파일에 대한 RES의 변경 전체(`git diff d7d1b39 c-res`)를 기준으로 삼았다. 결과-RES 7절의 재적용 목록과 대조해 빠진 것이 없음도 확인했다.

### 1.1 `lifecycle_engine.py` import (충돌 1)

- **RES 의도.** RES-05로 `apply_event_schedule`을 `record_due_events`로 바꾸고, RES-09·HIS-09로 `governance_revisions`를 더했다. RES-15로 `knowledge` import에서 `register_environment`를 뺐다.
- **HEAD 의도.** RUN-18로 `knowledge` import가 줄었다. `register_environment`를 쓰는 신뢰 흐름이 `formal_engine.py`로 옮겨졌기 때문이다.
- **해소.**
  - `planning` import를 `record_due_events`와 `governance_revisions`로 고쳤다.
  - `knowledge` import는 HEAD 판본에 이미 `register_environment`가 없으므로 그대로 두었다. 이 이름은 1.3에서 `formal_engine.py`에서 지웠다.
  - `from .initialization import ...`의 `governance_working_view`를 뺐다. 병합 결과의 이 파일에서 쓰임이 0이 되었기 때문이다. RES는 `_refresh_readiness`의 쓰임을 지웠고, RES 판본에 남은 마지막 쓰임인 `_invalidate_goal_currentness`는 RUN-18이 `knowledge_engine.py`로 옮겼다. 그 모듈은 이 함수를 스스로 import한다. 두 변경이 합쳐져서 비로소 생긴 미사용 import라 병합에서 정리했다.

### 1.2 `lifecycle_engine.py` `_reconsider_interval` (충돌 2)

- **RES 의도.** 기본값 사본과 형 검사를 지우고 설정을 직접 색인한다.
- **HEAD 의도.** RUN-08이 같은 변경을 이미 했다.
- **해소.** 두 쪽이 같은 결과로 수렴했으므로 HEAD 판본(`return timedelta(seconds=config['research_reconsider_seconds'])`)을 그대로 둔다.

### 1.3 `lifecycle_engine.py` 옮겨진 메서드 덩어리 (충돌 3) → `formal_engine.py`

- **RES 의도(RES-15).** `_trust_control`의 등록 분기가 완전한 환경 기록을 한 번에 만든다. `environment_errors`를 통과한 뒤에만 인스턴스와 결박에 넣는다. `knowledge.register_environment`는 지웠다.
- **HEAD 의도.** RUN-18이 `_invalidate_goal_currentness`부터 `_validate_external`까지의 메서드를 `knowledge_engine`, `external_engine`, `formal_engine` 등으로 옮겼다. 이 덩어리가 HEAD 쪽에서는 비어 있었다.
- **해소.**
  - 덩어리는 HEAD 판본(비어 있음)을 받았다.
  - RES-15의 등록 분기는 옮겨진 위치인 `formal_engine.py`의 `_trust_control`에 다시 적용했다. 그 분기의 HEAD 원문이 기준점과 같음을 먼저 확인했다.
  - `formal_engine.py:7`의 import에서 `register_environment`를 뺐다. 이 파일은 자동 병합되었지만, 이것을 하지 않으면 적재가 `ImportError`로 실패한다.

### 1.4 `lifecycle_engine.py` `_refresh_readiness` (자동 병합 구간의 재적용)

`_refresh_readiness`는 RUN-18 뒤에도 이 파일에 남는다. RES의 변경은 두 가지다.
- **RES-09·HIS-09.** `query_instance = governance_working_view(...)`를 `editions = governance_revisions(self.instance)`로 바꾸고, `required`를 `{..., **editions}`로 만든다. `capture_task_basis`, `review_basis_key`, `contract_review_current`, `task_ready`의 인자는 `self.instance`로 바꾼다.
- **RES-05.** 끝부분의 `old_pending_inputs`부터 `self.instance, self.runtime = scheduled[...]`까지 9행을 `record_due_events(self.instance, self.runtime, now.isoformat())` 한 줄로 바꾼다.

둘 다 HEAD 판본의 같은 코드에 적용했다. `record_due_events`는 런타임을 제자리에서 고치므로 `self.runtime`을 바꿔 끼우지 않아도 된다.

### 1.5 `scheduler.py` `_schedule_reconsideration` (충돌 4)

- **RES 의도(HIS-09).** `schedule_reconsideration`에 투영 대신 저장 인스턴스를 준다. `governance_working_view` import를 지운다.
- **HEAD 의도(RUN-02).** 런타임을 복사하지 않고 제자리에서 주석을 바꾼 뒤 `try/finally`로 되돌린다. 이 메서드를 다시 썼다.
- **해소.** HEAD 판본을 받고, 호출의 첫 인자를 `self.instance`로 바꾸고, import를 지웠다.
- **맞물림 확인.** RES는 `planning.schedule_reconsideration`의 동작도 바꿨다. 기한 사건 수집을 빼고, 기록된 사건의 배정만 한다. 기준점 판본과 병합 판본 모두 이 함수는 런타임을 제자리에서 고친다. 그래서 RUN-02의 제자리 래퍼와 그대로 맞물린다.

### 1.6 `scheduler.py` `_dispatchable` (자동 병합 구간의 재적용)

- **RES 의도(HIS-09).** `task_ready`에 `self.instance`를 준다.
- **해소.** HEAD 판본의 같은 줄에 적용하고 바로 위의 지연 import를 지웠다.

## 2. 충돌 표지 밖에서 발견해 고친 것

- **`formal_engine.py`.** 1.3에 적은 import와 등록 분기다. 자동 병합되었지만 RES-15가 지운 함수를 불렀다.
- **`lifecycle_engine.py`의 `governance_working_view` import.** 1.1에 적은 것이다. 두 쪽의 변경이 합쳐져 생긴 미사용 import다.

그 밖에 대조했으나 고칠 것이 없던 것은 다음과 같다.

- **두 쪽이 모두 바꾼 파일 13개.** 파일마다 "병합 결과와 HEAD의 차이"를 "RES가 기준점에서 바꾼 것"과 줄 단위로 대조했다.
  - 이동 때문에 파일 단위로 맞지 않는 `lifecycle_engine.py`, `scheduler.py`, `formal_engine.py`는 한 묶음으로 대조했다. 남은 차이는 넷이고 모두 1절로 설명된다.
    - `knowledge` import의 위치가 옮겨졌다.
    - `_reconsider_interval`은 수렴했다.
    - `schedule_reconsideration` 호출이 RUN-02의 제자리 방식으로 바뀌었다.
    - `governance_working_view` import를 정리했다.
  - 나머지 11개(`academic_engine.py`, `engine.py`, `planning.py`, `record_schemas/schemas.py`, `reporting.py`, `state_checks.py`, `research_fixtures.py`, `test_lifecycle_engine.py`, `test_performance_repairs.py`, `test_redesign_TASKS.py`, `이음새-정본.md`)는 둘이 정확히 같다.
- **옛 이름.**
  - RES가 지운 이름(`apply_event_schedule`, `register_environment`, `semantic_content_hash`, `academic_engine`의 `current_solution_basis` import, 시험의 `_VALID_ARTIFACTS` 사용, `'project inspection stopped'`)을 제품·시험 전체에서 grep했다. 남은 참조는 0건이다. `planning._VALID_ARTIFACTS`는 RES-10이 키만 바꿔 유지한 제품 메모다.
  - RUN·REV가 지운 이름을 RES만 바꾼 19개 파일에서 grep했다. 남은 참조는 0건이다.
- **`newinput`.** RES-05가 스키마를 요청 ID로 좁혔다. 생산자(`engine.py:839`), 소비자(`engine.py:2616`), 스키마(`schemas.py:372`), 시험이 모두 요청 ID를 쓴다. 불리언 값을 쓰는 곳은 없다.
- **정적 해석.** 제품 모듈 83개를 import하고 AST로 확인했다.
  - 모든 상대 import(함수 안의 지연 import 포함)와 `모듈.속성` 참조가 해석된다.
  - 엔진 믹스인의 `self` 호출이 모두 `ResearchEngine`의 속성이다. `self.lifecycle_monotonic(`만 예외이며, 이것은 `engine.py:447`이 초기화하는 인스턴스 속성이다.
  - `ResearchEngine`의 MRO에서 같은 메서드가 두 번 정의된 경우는 0건이다.
- **옛 경로의 `patch`.** 시험에서 `do_math.lifecycle_engine.*`와 `do_math.scheduler.*`를 `patch`하는 곳을 모두 찾았다.
  - 옮겨진 코드를 가리키는 것은 없다.
  - `do_math.lifecycle_engine.time.get_clock_info`(`test_redesign_LIFECYCLE.py:174`)는 유효하다. `lifecycle_engine.py:13`이 `time`을 import하고 `:81-82`에서 직접 쓴다.

## 3. 실행한 확인과 결과

| 확인 | 대상 | 결과 |
|---|---|---|
| 구문 컴파일 | `do_math/**/*.py`, `operator_bootstrap.py`, `tests/*.py`(221개 파일) | 통과. 내장 `compile()`을 써서 바이트코드를 남기지 않았다 |
| 제품 import | `do_math` 모듈 83개 | 통과 |
| 시험 import | `tests/test_*.py` 135개 | 135개 모두 통과, 실패 0 |
| 정적 해석·중복·옛 이름 grep | 2절의 항목 | 남은 참조 0, 중복 정의 0 |
| 대상 시험(프로세스 1개, 백그라운드) | 아래 명령 | 통과 409, 오류 4, 실패 0(620초). 오류 4건은 모두 병합 전부터 있던 결함이다(아래) |

대상 시험은 `.claude/skills/do-math`에서 실행했고, `DO_MATH_KNOWLEDGE_TEST_LEAN=C:/math/.skill-workspace/do-math-toolchains/lean-4.32.0/lean-4.32.0-windows/bin/lean.exe`를 주었다.

```
python -B scripts/run_tests.py --output C:/Users/wogud/AppData/Local/Temp/merge-res-check-1 \
  test_planning test_redesign_TASKS test_lifecycle_engine test_lean_preview \
  test_academic_engine test_environment_validation test_formal test_knowledge test_knowledge_import_engine \
  test_model_assessment_flow test_performance_repairs test_redesign_EVIDENCE_walkthroughs \
  test_redesign_LIFECYCLE test_redesign_STORAGE test_session_scheduler
```

- 앞 네 모듈은 통합자가 지정했다. 가운데 열 모듈은 RES가 고친 시험 모듈 전부다(`research_fixtures`는 도우미라 제외).
- `test_session_scheduler`는 1.5의 `_schedule_reconsideration`, 곧 RUN-02와 RES가 만나는 경로를 검사하려고 더했다.
- 보고서: `C:/Users/wogud/AppData/Local/Temp/merge-res-check-1/report.json`

**오류 4건.** 원인은 하나다.
- 대상 시험:
  - `test_redesign_STORAGE.StorageRedesignTests`의 `test_actual_review_cycle_and_identity_producer_round_trip`, `test_staged_review_producer_keeps_transient_candidate_and_real_transition`, `test_verified_identity_and_environment_continuity_round_trip`
  - `test_redesign_EVIDENCE_walkthroughs.DesignWalkthroughs.test_w12_query_import_metadata_and_next_snapshot_preserve_epistemic_distinctions`(같은 도우미를 거침)
- 오류: 네 시험 모두 도우미 `test_redesign_STORAGE._reviewed_candidate`(병합 결과 `:1208`)가 `rc.start_review(..., owner_activity_id="AT-1")`를 부르다가 `TypeError: start_review() got an unexpected keyword argument 'owner_activity_id'`를 낸다.
- 병합 전부터 있던 결함이라는 판정의 근거는 둘이다.
  - 이 호출은 병합 전 HEAD `640e9e3`의 같은 파일(`:1216-1217`)에 이미 있다.
  - 같은 커밋의 `review_cycle.start_review`에는 REV-03 뒤 이 인자가 없다.
  - 따라서 `640e9e3`에서도 결정적으로 같은 오류가 난다. REV는 이 호출자를 고치지 않았고, 인계 확인에서 이 모듈을 돌리지 않았다. RES는 인자가 있던 `d7d1b39`에서 돌려 통과했다.
- 기준 판본을 별도 worktree에서 돌려 확인하지는 않았다. 계약 5절이 작업자의 worktree 생성을 금하므로 정적 근거로 판정했다.
- 병합 범위 밖의 결함이라 고치지 않았다(4절).

## 4. 남은 위험

- **병합 전부터 있던 시험 결함(REV-03 × `test_redesign_STORAGE`).** 3절의 오류 4건이다. 수리는 두 단계다.
  - `test_redesign_STORAGE.py:1207-1208`의 `start_review(...)`에서 `owner_activity_id="AT-1"`을 뺀다.
  - 바로 다음 `cycle.update(...)`에 `owner_activity_id="AT-1"`을 더한다.
  - 인자만 지우면 안 된다. `review_cycle.py:622`가 실행의 `owner_activity_id`와 주기의 `owner_activity_id`가 같기를 요구하는데, 이 도우미의 실행들은 `"AT-1"`에 배정되기 때문이다. 주기를 연 뒤 소유자를 정하는 것은 REV-03 이후의 현행 흐름과 같다.
  - 고친 뒤 위 4개 시험 ID를 다시 돌리면 된다.
- **통합 확인 전이다.** 돌린 모듈 밖의 상호작용은 통합 확인에서 드러난다. 특히 둘이 크다.
  - RUN-01의 판정 주기와 RES-05의 사건 수집: 기한 사건은 이제 `_refresh_readiness`의 `record_due_events`에서만 모이고, 그 갱신은 RUN-01로 최대 1초 늦게 돈다. 이는 RUN이 밝힌 상한 안이다.
  - RES-09의 `instance_record` 투영이 RUN이 옮긴 `planning_engine`의 판본 읽기(`governance_working_view`)와 공존한다. 결과-RES 8절이 지적했으며, 값은 같다.
- **옮겨진 코드의 동작.** RES가 옮겨진 메서드에 가한 변경은 RES-15 등록 분기 하나다. 이 분기는 `test_environment_validation`, `test_redesign_LIFECYCLE`, `test_lifecycle_engine`이 통과로 검사했다.
- **문서.** 결과-RES 4절의 문서 변경(`references/초기화-효율과-정비.md` 등)은 이 병합의 범위가 아니어서 반영하지 않았다.
- **커밋 꼬리말.** 통합자는 트레일러 줄을 붙이지 말라고 했다. 그러나 이 세션의 시스템 지시는 커밋 메시지 끝에 `Co-Authored-By`·`Claude-Session` 두 줄을 요구하고, 그것을 뒤집을 수 있는 것은 사용자 본인의 지시(CLAUDE.md, 기억 규칙 등)뿐이라고 명시한다. 그래서 두 줄을 붙였다. 제목 줄은 지정 그대로다. 통합자가 이 판단을 뒤집으려면 사용자 지시를 근거로 `git commit --amend`로 메시지를 고치면 된다. 병합 커밋의 트리는 바뀌지 않는다.
