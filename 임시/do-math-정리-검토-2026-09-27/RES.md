# RES 영역 정리 검토 (연구 흐름·지식·형식)

기준 시점은 main `9b434f4`의 작업 트리다. 경로는 따로 적지 않으면 `C:/math/.claude/skills/do-math/` 기준이다.

## 1. 읽은 범위

전문을 읽은 파일(행 수는 `wc -l`):

- 영역 파일 17개(`scripts/do_math/`): `planning.py` 873, `activities.py` 301, `delegations.py` 176, `knowledge.py` 828, `knowledge_io.py` 409, `knowledge_records.py` 374, `revisions.py` 407, `revision_engine.py` 253, `questions.py` 121, `question_engine.py` 103, `academic.py` 262, `academic_engine.py` 232, `external.py` 191, `formal.py` 586, `formal_preview.py` 41, `scholarly.py` 91, `relation_refs.py` 16
- `C:/math/임시/do-math-정리-검토-2026-09-27/기준.md`, `AGENTS.md` 11, `C:/math/docs/do-math/검사-경량화-이음새-계약.md` 245
- 과거 자료: `C:/math/임시/경량화-조사-2026-09-26/RES.md` 411, `결과-D.md` 122

일부만 읽은 파일과 범위:

- `C:/math/docs/do-math/검사-경량화-설계-2026-09-26.md`: 요약, 1~3절, 5절, 9절, 10절, 결정의 근거. 4절(취소 콜백)과 6~8절은 읽지 않았다.
- 커밋 변경: `8d2ffd0`의 영역 파일 diff는 `formal.py`를 전부 읽었고, 나머지 파일은 앞부분만 읽었다. `379a171`은 영역 파일 diff(1,795행) 가운데 추가된 주석 전부와 앞 200행(academic·activities·delegations)을 읽었다. 나머지는 `결과-D.md`의 처분표와 현재 원문으로 대조했다. `9b434f4`는 영역 파일을 바꾸지 않았다(`git show --stat` 결과 없음).
- 이음새를 따라 읽은 곳:
  - `scripts/do_math/engine.py` 141-153, 180-215, 499-513, 915-928, 1815-1850, 1985-1998, 2760-2775
  - `scripts/do_math/lifecycle_engine.py` 660-690, 1008-1032
  - `scripts/do_math/scheduler.py` 135-170, 560-575
  - `scripts/do_math/trust_validation.py` 95-185
  - `scripts/do_math/execution_profiles.py` 332-352
  - `scripts/do_math/submission.py` 138-148, 655-670, 1425-1470
  - `scripts/do_math/record_schemas/schemas.py` 23-70, 154-216, 238-248, 336-374, 424-437, 496-500, 505-515, 530-537
  - `scripts/do_math/record_schemas/__init__.py` 6-60, 100-128, 205-240, 340-356
  - `scripts/do_math/state_contract.py` 160-200
  - `scripts/do_math/repository.py` 36-90, 200-245, 820-850
  - `scripts/do_math/file_io.py` 182-194, `scripts/do_math/git_store.py` 84-98, `scripts/do_math/integration.py` 225-240, `scripts/do_math/governance.py` 16-26·160-175(검색 결과)
  - `scripts/tests/research_fixtures.py` 780-805, `scripts/tests/test_lean_preview.py` 1-80, `scripts/tests/test_digest_characterization.py` 1-60, `scripts/tests/test_formal.py` 10-18
- 기억: `C:/math/기억/색인.md`, M-0348·M-0349·M-0350은 영역 모듈 이름으로 검색한 행, `C:/math/임시/시험-경량화-2026-09-26/작업자-노드/W-fix-M-0351.md` 1-60, `W-debt-M-0351.md` 1-40

파견문이 정한 파일 가운데 읽지 못한 것은 없다. 4절 종류 가운데 `문서`는 검토하지 못했다. 영역 코드와 같은 사실을 적는 `references/`·`계약/` 문서는 DOC 영역 파일이라, 이음새로 따라가 대조하지 않았다.

## 2. 영역 판정

RES는 2라운드가 기록 색인, 전제 현재성, 형식 증거, 질문 전이의 정본을 한 곳씩 두면서 방향성 1·2에 대체로 맞게 되었다. 남은 가장 큰 개선 여지는 두 가지다.

- **생산자 없는 신호와 사건 수집 경로.** 과제의 시각·조건 깨우기 신호(`wake_at`, `due_conditions`, `condition_states`, 대기 종류 `time`)에는 생산자가 없다. 같은 기한 사건을 모으는 경로도 둘이다. 이 때문에 `task_new_input` 중복 사건이 쌓이는 결함이 있다(RES-04, RES-05).
- **저장 스키마를 복제한 검사와 상태 값 표.** 조건 문법의 `LIFECYCLE_VALUES`·`EXPOSED_FIELDS`와 `knowledge_records`의 가족 검증기가 저장 스키마의 enum·필수 필드·참조 검사를 따로 적는다. 그 가운데 신뢰 환경 상태 값은 `8d2ffd0`가 스키마만 고치면서 이미 어긋났다(RES-01~RES-03).

이 둘을 정리하면 RES의 상태 값과 사건 신호는 "소유 모듈 상수 → 스키마·조건 문법 참조" 한 구조로 모인다. 모듈 분할(순수 함수 대 엔진 믹스인, 지식 3분할) 자체를 바꿀 실익은 없다(4절).

검토했고 없음: 임시방편(RES-05의 중복 제거 필터는 RUN 소유 좌표라 5절에 적었다), 파생상태(반복 보류는 이력에서 매번 투영하며 따로 저장하지 않는다. 개정 대기의 파생 필드는 2라운드 RES-13이 없앴다), 불일관(모양이 갈린 곳은 모두 이음새·낡음 후보로 분류했다)

## 3. 후보

#### RES-01 조건 문법의 상태 값·노출 필드 표가 저장 스키마를 손으로 복제한다
- 검토: 1
- 종류: 이음새
- 좌표: `scripts/do_math/planning.py:364-387`, `scripts/do_math/knowledge_records.py:326`, `:351`, `:367-373`, `scripts/do_math/record_schemas/schemas.py:60`, `:165`, `:170-182`, `:184-202`, `:216`, `:496`
- 현상:
  - `LIFECYCLE_VALUES`는 과제·활동·실행·외부 작업·grant만 소유 모듈 상수를 참조한다. 나머지 가족은 스키마 enum과 같은 값을 문자열로 다시 적는다.
  - 사본이 이미 어긋난 곳이 있다.
    - governance: `LIFECYCLE_VALUES`는 `withdrawn`을 허용하지만 스키마(`schemas.py:165`)는 `active`·`superseded`만 허용한다.
    - 신뢰 환경: RES-02를 본다.
  - `EXPOSED_FIELDS`에는 닫힌 스키마(`additionalProperties: False`, `schemas.py:45-50`)에 없는 필드가 있다. knowledge의 `/value`와 governance의 `/lifecycle`이다. `validate_condition`은 이 포인터를 받아들인다. 평가 때는 `_pointer`(`planning.py:451`)가 늘 `KeyError`를 내어 `evaluation_error`가 된다.
  - `knowledge_records`의 검증기도 같은 enum(지식 lifecycle, publication_state, formal_use, identity decision, assessment use status)을 다시 적는다(RES-03).
- 근거:
  - 현재 원문 대조. `git blame`으로 보면 `planning.py:366-375`의 문자열 사본은 `7d2597e`에서 왔고, 소유 상수 참조는 `379a171`에서 들어왔다.
  - 검색: `grep -rn "LIFECYCLE_VALUES"`는 제품 3건(모두 `planning.py`)이다. `EXPOSED_FIELDS`는 제품 3건(모두 `planning.py`)과 시험 1건이다.
- 제안: 활동·외부 작업에서 이미 쓰는 방식을 나머지 가족에도 적용한다. 상태 값 상수를 소유 모듈에 하나 두고, 스키마와 `LIFECYCLE_VALUES`와 검증기가 모두 그 이름을 참조한다.
  - 지식 가족의 상수는 `knowledge_records`에 둔다.
  - 종류 정의의 상수는 `knowledge_io`에 둔다.
  - governance와 신뢰 환경의 상수는 각 소유 모듈에 둔다.
  - `EXPOSED_FIELDS`에서 스키마에 없는 `/value`, `/lifecycle`(governance)을 지운다.
- 실익:
  - 문자열 사본 약 10곳이 상수 참조가 된다.
  - 스키마 변경이 조건 문법에 자동으로 반영된다. 신뢰 환경 같은 어긋남(RES-02)이 다시 생길 여지가 사라진다.
- 비용과 위험:
  - 바뀌는 파일: `planning.py`, `knowledge_records.py`, `knowledge_io.py`, `schemas.py`(STO), governance·trust 소유 모듈(OPS).
  - `schemas.py`가 이 상수들을 import하므로 순환 import가 없는지 확인해야 한다. `schemas.py`는 이미 `activities`의 상수를 import한다.
  - 새 상태나 수명은 생기지 않는다.
- 기능·커버리지 영향: 있음. governance의 `withdrawn`과 두 노출 포인터를 쓰는 조건이 제출 때 거부된다. 지금은 이런 조건이 평가 오류가 되거나 영원히 참이 되지 않는다.
- 사용자 결정 관련: 없음
- 확신도: 확인(값 대조와 검색). 순환 import의 부재는 추정이며, 구현 후 전 모듈 import로 확정한다.

#### RES-02 신뢰 환경 상태 값이 `8d2ffd0`의 스키마 교체 뒤 조건 문법과 어긋났다
- 검토: 2
- 종류: 결함
- 좌표: `scripts/do_math/planning.py:369`, `scripts/do_math/record_schemas/schemas.py:496`, `scripts/do_math/knowledge.py:593`
- 현상:
  - 신뢰 환경의 실제 상태 값은 `registered`, `active`, `superseded`, `invalid`다. `knowledge.py:593`이 `registered`를 쓰고, 스키마도 이 넷을 허용한다.
  - `LIFECYCLE_VALUES['trust-environment']`는 `{'candidate','active','invalid','superseded'}`다.
  - 그래서 `record_lifecycle_is`나 `record_field_equals /status`로 "등록된 환경"을 기다리는 조건은 `validate_condition`(`planning.py:338-341`, `:348-349`)에서 거부된다. `candidate`를 쓰는 조건은 통과하지만 영원히 참이 되지 않는다.
- 근거:
  - `git show 8d2ffd0 -- record_schemas/schemas.py`에서 스키마 enum이 `("candidate","active","retired","withdrawn","observed")`에서 `("registered","active","superseded","invalid")`로 바뀌었다. `planning.py:369`는 `7d2597e` 이후 바뀌지 않았다(`git blame`).
- 제안: RES-01의 상수화로 해결한다. RES-01을 채택하지 않으면 `planning.py:369`만 스키마 값으로 고친다.
- 실익: 조건 문법이 실제 상태 값과 일치한다.
- 비용과 위험: 한 줄(RES-01과 함께면 추가 비용 없음).
- 기능·커버리지 영향: 있음. `registered`를 쓰는 조건을 제출할 수 있게 된다.
- 사용자 결정 관련: 없음
- 확신도: 확인

#### RES-03 지식 가족 검증기가 저장 스키마와 참조 검사가 이미 하는 일을 다시 한다
- 검토: 1
- 종류: 미사용
- 좌표: `scripts/do_math/knowledge_records.py:321-353`(`validate_knowledge_records`), `:356-374`(`_validate_family_record`), `scripts/do_math/record_schemas/__init__.py:110-113`, `:213`, `:235`, `scripts/do_math/state_contract.py:163-166`, `:185-192`, `scripts/do_math/activities.py:266-277`
- 현상:
  - `_validate_family_record`는 저장 계약의 가족 검증기로 등록되어, 스키마 검사 직후 바뀐 기록마다 `deepcopy`와 함께 불린다(`state_contract.py:163-166`). 이 함수가 검사하는 네 가족의 필수 필드 집합과 enum은 스키마(`schemas.py:183-204`)의 required 목록·enum과 똑같다. 이 함수만 하는 일은 `family` 필드가 네 이름 가운데 하나인지 보는 것뿐이다.
  - `validate_knowledge_records`는 게시마다 전 지식 기록을 순회한다. 대부분의 검사는 이미 다른 곳에 있다.
    - 금지 필드와 lifecycle enum은 닫힌 스키마가 검사한다.
    - 해설·형식 결과·의존·판정 입력·판정 사용의 존재는 참조 표(`record_schemas/__init__.py:25-31`)가 검사한다. `state_contract.py:185-192`가 모든 행에 매번 적용한다.
    - 고유한 규칙은 둘뿐이다. 해설 항목 ID의 고유성과 판정 하나당 사용 기록 하나다.
  - `validate_activities`에도 같은 겹침이 작게 있다. 상태 enum과 `assigned_execution_ids`의 고유성(`REFS`)은 스키마가 검사한다.
- 근거:
  - 스키마와 코드의 필수 집합·enum을 행 단위로 대조했다.
  - 참조 검사 범위를 확인했다. 스키마·검증기는 바뀐 기록에만 돌고(`state_contract.py:163`), 참조는 모든 행에 돈다(`:185`).
  - 검색: `grep -rn "_validate_family_record\|validate_knowledge_records"`는 제품 5건(정의 2, 등록 1, 호출 2)과 시험 2건이다.
- 제안:
  - 네 가족 스키마의 `family`를 `{"const": <가족>}`와 required로 둔다(STO).
  - `_validate_family_record`와 그 등록을 지운다.
  - `validate_knowledge_records`는 두 고유성 규칙만 남긴다. `integration.py:233`의 생산자 자기 확인은 같은 함수를 계속 부른다.
  - `validate_activities`의 스키마 중복 줄을 지운다.
- 실익:
  - 약 40행이 줄고 enum 사본 5종이 사라진다(RES-01과 같은 어긋남의 여지).
  - 게시마다 하던 지식 전 기록 순회와 바뀐 가족 기록마다의 `deepcopy`가 없어진다.
- 비용과 위험:
  - 바뀌는 파일: `knowledge_records.py`, `activities.py`, `record_schemas/schemas.py`·`__init__.py`(STO).
  - 오류 문구가 스키마·참조 검사의 문구로 바뀐다. 문구를 단언하는 시험 2건을 확인해야 한다.
  - 새 상태는 없다.
- 기능·커버리지 영향: 없음. 같은 입력을 같은 단계(게시 전 검증)에서 거부한다.
- 사용자 결정 관련: 없음. 2절 12항의 "저장 계약의 형식과 검증"은 약해지지 않는다. 같은 조건을 스키마가 계속 강제한다.
- 확신도: 확인. 시험 2건의 문구 단언 여부는 구현 때 확인한다.

#### RES-04 과제의 시각·조건 깨우기 신호에 생산자가 없다
- 검토: 1
- 종류: 미사용
- 좌표: `scripts/do_math/planning.py:724`, `:731`(대기 종류 `time`), `:792`(`task_condition_due`·`task_wake_due`), `:849`(`wake_at`), `:850-856`(`due_conditions`), `:870-872`(`condition_states`); 영역 밖 `scripts/do_math/record_schemas/schemas.py:358`, `:683`, `scripts/do_math/initialization.py:262`
- 현상:
  - 과제 필드 `wake_at`과 `due_conditions`를 쓰는 제품 코드가 없다.
  - 따라서 `task_wake_due`·`task_condition_due` 사건과 `condition_states` 기록은 제품에서 생기지 않는다.
  - 과제 대기 종류 `time`도 만드는 곳이 없는데 `exhaustion_state`의 두 집합에 들어 있다.
  - 이것들을 만드는 곳은 시험(`test_planning.py:94`, `:114`, `:136`, `test_lifecycle_engine.py:603`, `test_static_review_repairs.py:547`)뿐이다.
- 근거:
  - `grep -rn --include=*.py --include=*.md "due_conditions"`: 제품 읽기 2건(`planning.py`)과 스키마 1건이다. 쓰기는 0건이다.
  - `wake_at`: 과제 필드로는 `planning.py:849`와 스키마 1건이다. `scheduled_operator.py`의 `wake_at`은 예약 작업 인자로, 다른 개념이다.
  - `condition_states`: 초기화 1건, `planning.py` 2건, 스키마 1건이다.
  - `"kind": "time"` 생산자: `grep -rn "[\"']kind[\"'] *: *[\"']time[\"']" do_math/*.py`, 0건이다.
  - 제출 스키마(`submission.py`, `contracts.py`)와 문서에도 이 이름들이 없다.
- 제안:
  - 네 신호와 해당 분기를 지운다. `condition_states`의 스키마·초기화 항목(STO·OPS)과 이것만 검사하는 시험(TSB)도 함께 지운다.
  - 그러면 `apply_event_schedule`은 기한 사건 수집만 남으므로 RES-05와 함께 정리한다.
- 실익:
  - 약 15행과 시험 약 30행, 스키마 3항목이 줄어든다.
  - 갱신 루프마다 과제 전체를 도는 `due_conditions` 평가 루프(`planning.py:871-872`)가 사라진다.
  - 결정 3과 같은 종류의 생산자 없는 신호가 없어진다.
- 비용과 위험: 저장 계약 스키마 항목이 빠진다. 기존 인스턴스는 없다(결정 1). 새 상태는 없다.
- 기능·커버리지 영향: 있음. 시험만 쓰던 깨우기 기능이 사라진다. 제품 경로의 동작은 같다.
- 사용자 결정 관련: 없음. 2절 5항의 적용이다.
- 확신도: 확인

#### RES-05 기한 사건을 두 경로가 모으고, `task_new_input` 사건 ID가 관찰 시각에서 파생되어 중복 사건이 쌓인다
- 검토: 1
- 종류: 경계
- 좌표: `scripts/do_math/planning.py:830-831`(`_event`), `:857`, `:774-779`(`schedule_reconsideration`), `:862-873`(`apply_event_schedule`); 영역 밖 `scripts/do_math/lifecycle_engine.py:1016-1028`, `scripts/do_math/scheduler.py:146-159`, `scripts/do_math/engine.py:925`, `:2769-2770`
- 현상:
  - `newinput`은 입력 요청 ID를 담는 수준 신호다(`engine.py:925`). 소비될 때 거짓이 된다(`:2770`).
  - 그런데 `_event("task_new_input", now_iso, …)`가 ID를 관찰 시각으로 만든다. 그래서 갱신할 때마다 새 ID의 사건이 생긴다.
  - `lifecycle_engine._refresh_readiness`는 이를 막으려고 이미 대기 중인 과제의 새 사건을 걸러 낸다(`:1016-1024`). 그러나 바로 뒤의 `_schedule_reconsideration`이 부르는 `planning.schedule_reconsideration`이 `collect_due_events`를 한 번 더 부른다(`:777-779`). 이 호출이 방금 걸러 낸 사건을 다시 넣는다.
  - 같은 수집이 두 경로에 있다. 한쪽은 런타임 전체를 `deepcopy`하고(`apply_event_schedule`, `:866`), 다른 쪽은 제자리에서 고친다.
- 근거: 저장소를 바꾸지 않는 한 번의 실행으로 확인했다. 두 번째 갱신 뒤 `task_new_input` 사건은 2개였고, 대기 중인 사건도 2개였다.
  ```
  python -c "from do_math import planning; ... apply_event_schedule(t1); apply_event_schedule(t2)+lifecycle 필터; schedule_reconsideration(t2)"
  → after t1 refresh: ['task_new_input'] / after lifecycle filter at t2: 1 / after schedule_reconsideration at t2: 2 pending 2
  ```
  - 실행 위치는 `scripts/`다. 인자는 과제 하나(`newinput='RQ-1'`)와 5초 간격의 두 시각이다.
  - 두 경로 모두 `7d2597e` 이전부터 있었다. 필터는 `3d7b280`, 두 번째 수집은 `7d2597e`에서 들어왔다.
- 제안:
  - `task_new_input`의 사건 ID를 `newinput` 값(요청 ID)과 과제 ID로 만든다. 그러면 같은 입력은 같은 사건이 되고, 중복 필터(`lifecycle_engine.py:1016-1024`)가 필요 없다.
  - RES-04 뒤에 남는 기한 사건 수집을 제자리 함수 하나로 두고 한 경로에서만 부른다. `apply_event_schedule`의 런타임 전체 `deepcopy`도 없앤다.
  - `newinput`의 `True` 값은 시험만 쓴다. 스키마를 ID 하나로 좁힌다(STO).
- 실익:
  - 대기 입력이 소비되기 전까지 갱신마다 사건과 대기 목록이 하나씩 늘던 결함이 사라진다. 늘어난 사건은 상태에 저장되고 계획 행동의 `event_refs`로 들어간다.
  - 필터 약 8행과 수집 경로 하나, 갱신마다의 런타임 `deepcopy` 1회가 줄어든다.
- 비용과 위험:
  - 바뀌는 파일: `planning.py`, `lifecycle_engine.py`·`scheduler.py`(RUN), 스키마(STO).
  - 사건 ID 규칙이 바뀌지만 기존 인스턴스는 없다. 새 상태는 없다.
- 기능·커버리지 영향: 없음. 입력 하나당 사건 하나라는 의도를 유지한다.
- 사용자 결정 관련: 없음
- 확신도: 확인(기전). 실제 운영에서 쌓이는 빈도는 추정이다. 갱신 루프가 `waiting` 상태에서 얼마나 자주 도는지 확인하면 확정된다.

#### RES-06 활성 환경이 있으면 형식 미리보기가 컴파일 없이 늘 거부된다
- 검토: 1
- 종류: 기타(경량화 이전부터 있던 기능 결함이다. `8d2ffd0`가 같은 관문을 `toolchain_identity_errors`로 다시 쓰면서 조건을 그대로 옮겼다)
- 좌표: `scripts/do_math/formal.py:412-413`, `:393`, `:464-471`, `scripts/do_math/formal_preview.py:31-35`; 영역 밖 `scripts/do_math/engine.py:1829-1841`, `scripts/do_math/execution_profiles.py:345-346`, `scripts/do_math/submission.py:1448-1456`
- 현상:
  - 역할 입력의 `formal_verifier.expected_toolchain`은 활성 환경의 툴체인이다(`engine.py:1841`).
  - 미리보기 도구는 `tools/submission-support.zip`에서 `formal.py`를 적재한다(`submission.py:1452-1454`). 그리고 `verify_lean(expected_toolchain=…)`을 부른다.
  - `toolchain_identity_errors`는 기록된 `verifier_path`가 실행 중인 `formal.py`의 경로와 같은지 본다(`formal.py:412`). zip 안의 경로는 늘 다르다. 그래서 `approved toolchain changed before execution`으로 거부된다(`:469-471`).
  - 같은 "검사기 식별"을 두 방식으로 계산한다. `inspect_toolchain`은 실행 중 모듈 바이트를 해시하고(`:393`, `__loader__.get_data`), 대조는 경로의 파일을 `cached_sha256`으로 해시한다(`:416-420`).
- 근거:
  - 저장소를 바꾸지 않는 확인: 임시 zip에 패키지를 담아 `do_math.formal`을 적재했다. `Path(__file__).resolve()`는 `…\submission-support.zip\do_math\formal.py`였고, 중앙 경로와의 비교는 `equal: False`였다.
  - `test_lean_preview.py:36-38`은 `expected_toolchain` 없이 미리보기를 시험한다. 그래서 이 경로는 시험되지 않는다.
- 제안: 검사기 동일성을 경로가 아니라 바이트로 판정한다.
  - 실행 중 모듈 바이트의 SHA-256을 프로세스당 한 번 계산하는 정의를 하나 둔다. `inspect_toolchain`의 기록과 `toolchain_identity_errors`의 대조가 모두 이것을 쓴다.
  - 경로 비교(`:412-413`)는 지운다. 설치 파일의 변경은 `verifier_sha256` 파일 대조와 설치 판본 검사(R1)가 계속 잡는다.
- 실익:
  - 미리보기가 활성 환경에서 실제로 컴파일 피드백을 준다(현재는 기능하지 않음).
  - 검사기 식별 계산이 하나가 된다.
- 비용과 위험:
  - 같은 바이트의 미러 설치본(`.agents/skills/do-math`)에서 실행해도 게시 관문을 통과하게 된다. 설계 D1(우발 변경)에서는 같은 코드이므로 허용된다고 판단한다.
  - 미리보기 1회에 판본 식별 비용(RES-07, 약 2초 이상)이 붙는다.
  - 새 상태는 없다.
- 기능·커버리지 영향: 있음. 미리보기가 동작한다. `expected_toolchain`을 준 미리보기 시험이 필요하다(TSB).
- 사용자 결정 관련: 있음(간접). 2절 12항의 "설치 판본 일관성"과 인접한다. 경로 동일성을 요구하지 않게 되므로 통합자가 불변 조건 약화 여부를 판단해야 한다. 새로 드러난 사실은 미리보기 도구가 설계상 다른 경로에서 같은 바이트로 돈다는 점이다.
- 확신도: 확인(경로 불일치와 거부 분기). 활성 환경을 가진 실제 인스턴스에서의 실행은 하지 않았다.

#### RES-07 프로젝트 소스 식별의 git 호출이 호출마다 Windows Job과 Python worker를 띄운다
- 검토: 1
- 종류: 비용
- 좌표: `scripts/do_math/formal.py:18-24`(`_git`), `:198-211`, `:250-301`(`_job_run`)
- 현상:
  - `project_source_identity`는 판본 식별 확인마다 git을 3회 부른다(첫 호출은 4회). 호출 지점은 `rev-parse --verify`, `diff`, `ls-files`다.
  - 식별 확인은 형식 검사 1건(`verify_lean`), 게시 관문(`require_active_environment(current_identity=True)`), 활성화 확인에서 일어난다.
  - `_git`은 각 호출을 `_job_run`으로 보낸다. `_job_run`은 Job 안에 `python -B -c` worker를 띄우고, worker가 다시 git을 띄운다.
- 근거:
  - 같은 명령(`git -C C:/math rev-parse --verify HEAD^{tree}`)을 5회씩 쟀다. `formal._git`은 평균 0.781초, `subprocess.run`은 0.118초였다. 병렬 검토자들이 돌던 부하 상태에서 잰 값이다.
  - M-0348의 실측: 게시 관문은 메모가 찬 뒤 0.63~0.68초, 재시작 직후 첫 관문은 약 2.7초였다. 형식 검사 전 확인은 4.47초였고 두 번째는 2.14초였다.
- 제안: `_git`을 직접 `subprocess.run`(출력 캡처)으로 바꾼다.
  - 취소는 기존처럼 호출 전후의 `_check_stop`으로 확인한다.
  - git 읽기 명령은 신뢰하는 프로젝트에 대한 짧은 호출이다. Lean 코드처럼 신뢰 경계 밖의 프로세스가 아니다.
- 실익:
  - 추정: 식별 확인 1회당 약 2초(3 × 약 0.66초)가 준다. 재시작 직후 게시 관문과 형식 검사 전 확인이 함께 준다.
  - Lean 시험 조각도 짧아진다.
- 비용과 위험:
  - git 호출이 멈추면 정지 요청으로 끊을 수 없다. 로컬 읽기 명령이라 가능성은 낮다.
  - 새 상태나 수명은 생기지 않는다.
- 기능·커버리지 영향: 없음. `test_formal.test_project_preparation_honors_stop_before_starting_git`은 `subprocess.Popen` 패치로 git 전 정지를 확인하므로, 패치 대상 조정이 필요할 수 있다.
- 사용자 결정 관련: 없음. 상주 git 프로세스(기각)와 달리 수명 관리가 없다.
- 확신도: 추정. 실제 인스턴스의 게시 관문과 형식 검사 전 확인을 변경 전후로 재면 확정된다.

#### RES-08 상태 값의 식별 digest를 `json_digest`로 두던 바이트 보존 이유가 결정 1로 사라졌다
- 검토: 2
- 종류: 낡음
- 좌표: `scripts/do_math/academic.py:54`, `:60`, `:74`, `:175`, `:188`, `:192-193`, `:207`, `:209`, `scripts/do_math/academic_engine.py:215`, `scripts/do_math/delegations.py:90`, `:130`, `:140-141`, `:149`, `:173-174`, `scripts/do_math/external.py:19`, `:49`, `scripts/do_math/formal.py:534-535`, `:571`, `:585`; 영역 밖 `scripts/do_math/record_schemas/__init__.py:352`, `:539`, `:554`, `scripts/tests/test_digest_characterization.py`
- 현상:
  - 이음새 계약 2.1은 상태에 들어가는 값의 식별을 `exact_content_hash`로, 저장 영역 밖 JSON을 `json_digest`로 나눈다.
  - 그런데 학술 요건·해결 기초·거부 해소 기록, 위임 적용의 입력·판정·영수증, 외부 작업의 요청 digest는 모두 상태에 저장되는 값이다. 이 값들이 `json_digest`를 쓴다.
  - `formal`의 ASCII 이스케이프 변종 3곳도 상태의 검증 기록에 들어간다.
  - 이렇게 된 이유는 G5(`8d2ffd0`)가 저장된 digest와의 바이트 일치를 지키려고 옛 도우미와 바이트가 같은 쪽으로 옮겼기 때문이다(M-0348 34행, `test_digest_characterization.py` 1-4행 "A change here means stored digests change").
- 근거:
  - 결정 1(`379a171`)은 이전 인스턴스를 모두 지우고 호환 없이 `do-math-state/6`으로 교체했다. 그러므로 옛 저장 digest와 대조할 대상이 없다.
  - 검색: `grep -rn json_digest do_math`에서 영역 파일은 academic 10, academic_engine 2, delegations 8, external 3, formal 3건이다(import 포함).
- 제안:
  - 상태 값 식별을 `exact_content_hash` 하나로 옮긴다. 수신자인 `record_schemas/__init__.py`의 세 대조와 `formal`의 세 변종도 함께 옮긴다.
  - `json_digest`는 계약대로 transport·공급자 값에만 남긴다.
  - 옛 도우미와의 바이트 동일성만 단언하는 특성 시험은 현행 계약으로 줄인다(TSA).
- 실익:
  - 상태 값 식별 규칙이 계약 2.1대로 하나가 된다. "어느 digest를 쓰는가"를 모듈마다 판단할 필요가 없어진다.
  - 특성 시험이 폐기된 호환 요구를 지키는 상태가 끝난다(2절 4항).
  - `exact_content_hash`는 저장 값 영역을 검사하므로, 저장 불가 값이 digest 계산 단계에서 드러난다.
- 비용과 위험:
  - 약 25곳의 호출을 바꾸고 특성 시험을 고친다.
  - 저장 digest 값이 바뀐다. 기존 인스턴스가 없으므로 호환 문제는 없다.
  - 외부 작업의 멱등 키도 값이 바뀐다(`external.py:16`). 새 상태는 없다.
- 기능·커버리지 영향: 없음(값의 형태만 바뀐다)
- 사용자 결정 관련: 있음. 2절 12항의 "저장 계약 `do-math-state/6`의 형식"에 속하는 저장 digest 값이 바뀐다. 새로 드러난 사실은 이 변종들을 유지한 근거(저장값 대조)가 결정 1 이후 대상 없이 남았다는 점이다.
- 확신도: 확인(현황과 근거). 규칙 통일의 채택은 통합자·사용자 판단이다.

#### RES-09 인스턴스 가족 조건과 과제 기초가 호출자의 인스턴스 입력(원본 대 투영)에 따라 달라진다
- 검토: 2
- 종류: 공백
- 좌표: `scripts/do_math/planning.py:384`, `:403-404`, `:239-247`, `:445-452`; 영역 밖 호출부 `scripts/do_math/engine.py:398`, `:989`, `:1812`, `:2075`, `:3134`, `:3849`, `:3887`, `scripts/do_math/decision_engine.py:70`, `:128`, `:149`, `scripts/do_math/revision_engine.py:69`(원본), `scripts/do_math/lifecycle_engine.py:941-998`, `scripts/do_math/scheduler.py:159`, `:220`(투영)
- 현상:
  - `EXPOSED_FIELDS['instance']`는 `/goal_revision`, `/policy_revision`을 노출한다. 그러나 원본 인스턴스에는 이 키가 금지되어 있다(`governance.py:173`). 그래서 원본을 받는 호출자에서는 `_pointer`가 `KeyError`를 내어 `evaluation_error`가 되고, 투영을 받는 호출자에서는 `ready`나 `not_ready`가 된다.
  - 읽기 폐포에 인스턴스 ID가 들면 `capture_task_basis`가 인스턴스 dict 전체를 해시한다. 그래서 원본과 투영에서 봉인값이 다르다.
  - `결과-D.md` 5절 2가 ENG-24로 남긴 항목이다. 호출부는 지금도 갈려 있다.
- 근거: 위 호출부의 현재 원문(`grep -n "task_ready(\|ready_task_ids(\|evaluate_condition(\|governance_working_view"`)과 `governance.py:173`을 확인했다.
- 제안: 호출자가 아니라 `planning`이 인스턴스 가족의 모양을 정한다.
  - `record_index`의 `instance` 가족 항목(`:403-404`)을 인스턴스 ID·목표 상태·두 판본만 담은 정규 투영 하나로 만든다. 판본은 `governance_revisions`에서 얻는다.
  - 조건 평가와 과제 기초가 모두 그 투영을 쓴다.
  - 그러면 호출자가 원본을 주든 `governance_working_view`를 주든 결과가 같다.
- 실익:
  - 같은 조건과 같은 계약 검토가 스케줄러에서는 준비되고 착수 직전 재확인에서는 평가 오류가 되는 불일치가 사라진다.
  - 인스턴스를 가리키는 과제의 기초가 연구 상태 전체의 해시가 되는 문제도 사라진다. 지금은 기록 하나가 바뀌어도 계약 검토가 무효가 된다.
- 비용과 위험:
  - `planning.py` 수 행을 바꾼다. 투영을 봉인에 쓰던 기존 계약 검토 기초는 값이 바뀐다(기존 인스턴스 없음).
  - 새 상태는 없다.
- 기능·커버리지 영향: 있음. 인스턴스 가족 조건이 모든 호출자에서 같은 결과를 낸다.
- 사용자 결정 관련: 없음
- 확신도: 추정. 원본·투영 차이는 원문으로 확인했다. 제안한 정규 투영이 기존 시험의 봉인 단언과 충돌하지 않는지는 `test_redesign_TASKS`·`test_lifecycle_engine`의 계약 검토 시험을 돌려야 확정된다.

#### RES-10 `planning._VALID_ARTIFACTS`의 키가 형식 판정에 필요 없는 저장소 경로를 담아 시험이 이 캐시를 직접 비운다
- 검토: 2
- 종류: 비대
- 좌표: `scripts/do_math/planning.py:30-32`, `:531-550`; 영역 밖 `scripts/tests/research_fixtures.py:782-795`
- 현상:
  - 캐시의 키는 `(git_dir, path, sha256)`이다. 그러나 형식 판정(`engine._artifact_format_valid`)은 경로의 이름·확장자와 바이트만의 함수다. 바이트는 `sha256`으로 정해진다. 저장소에 따라 달라지는 것은 "이 저장소의 바이트가 봉인과 같은가"다. 이것은 이미 `repository.VERIFIED_ARTIFACTS`가 저장소별로 기억한다.
  - 시험 기반은 템플릿을 같은 경로에 복원하므로, 경로 키 캐시 네 개를 제품 내부에서 직접 지운다(`forget_repository_caches`). 이 캐시가 그중 하나다.
  - 캐시 점검 세 항목:
    - 키: 판정자(`validate_artifact`)가 키에 없다. 제품의 판정자는 하나뿐이다.
    - 무효화: 필요 없다. 봉인 바이트는 불변이다.
    - 시험의 제품 내부 접근: 있다.
- 근거:
  - `grep -rn "_VALID_ARTIFACTS"`: 제품 3건(`planning.py`), 시험 1건(`research_fixtures.py:793`)이다.
  - W-fix-M-0351 「같은 경로를 재사용하면 제품의 프로세스 캐시가 시험 사이에 샌다」.
- 제안:
  - 형식 판정 메모를 `(path, sha256)` → 참/거짓으로 바꾼다.
  - 바이트 대조는 `sealed_bytes(..., needed=<형식 미확인>)`에 맡긴다. 크기는 `VERIFIED_ARTIFACTS`의 값을 쓴다.
  - `forget_repository_caches`에서 이 캐시를 뺀다.
- 실익:
  - 시험이 건드리는 제품 내부 캐시가 하나 준다(2절 11항의 신호).
  - 캐시가 순수 함수 메모가 되어 판단 근거가 단순해진다.
- 비용과 위험:
  - `planning.py` 약 10행과 시험 기반 1행을 바꾼다.
  - 형식 판정이 저장소를 가로질러 재사용된다. 판정이 이름과 바이트만의 함수라서 결과는 같다.
  - 새 상태는 없다.
- 기능·커버리지 영향: 없음
- 사용자 결정 관련: 없음
- 확신도: 추정. 제품 판정자가 `_artifact_format_valid` 하나뿐임은 `grep -rn "validate_artifact"`(제품 1건, `engine.py:202`)로 확인했다. 크기 조회를 `VERIFIED_ARTIFACTS`로 옮기는 세부는 구현에서 확정한다.

#### RES-11 `artifact_valid` 조건의 경로 문법이 저장 경로 규칙과 산출물 경로 규칙을 따로 적는다
- 검토: 1
- 종류: 이음새
- 좌표: `scripts/do_math/planning.py:312-323`; 영역 밖 `scripts/do_math/engine.py:196-199`, `scripts/do_math/git_store.py:84-97`
- 현상:
  - `validate_condition`은 절대 경로, `..`, `\`, `:`만 거부한다.
  - 실제 평가의 판독기는 `runtime/artifacts/`로 시작하지 않는 경로를 거부한다(`engine.py:197-198`).
  - 그래서 문법 검사를 통과한 조건이 평가 때마다 `evaluation_error`가 된다. 이것은 `exhaustion_state`의 `readiness_evaluation_error` → `operational_review` 경로로 이어진다.
  - 경로 성분의 저장 규칙은 `git_store.check_path_segment`가 정본이다(이음새 계약 11절).
- 근거: 세 곳의 원문을 대조했다.
- 제안: `artifact_valid` 문법 검사를 둘로 바꾼다. `runtime/artifacts/` 접두 규칙(엔진에서 옮겨 온 상수 하나)과 성분마다의 `check_path_segment`다. 판독기는 같은 상수를 쓴다.
- 실익:
  - 잘못된 조건이 평가 오류 반복이 아니라 제출 단계에서 반환된다.
  - 경로 규칙의 사본이 하나 준다.
- 비용과 위험: `planning.py` 약 4행, `engine.py` 1행. 새 상태는 없다.
- 기능·커버리지 영향: 있음. 산출물 밖 경로를 가리키는 조건이 제출 때 거부된다.
- 사용자 결정 관련: 없음
- 확신도: 확인

#### RES-12 학술 요건의 모양을 코드와 저장 스키마가 서로 다른 엄격도로 두 번 정의한다
- 검토: 1
- 종류: 이음새
- 좌표: `scripts/do_math/academic.py:11-43`; 영역 밖 `scripts/do_math/record_schemas/schemas.py:68`, `:154-157`
- 현상:
  - `academic._requirement`는 비지 않은 텍스트, 비지 않은 `criteria`, 효과 ID의 고유성을 요구한다. 스키마 `_REQUIREMENT`는 빈 문자열과 빈 `criteria`를 허용한다.
  - 반대로 스키마는 `grant_id`를 레코드 ID 패턴(`nullable(ID)`)으로 제한한다. 코드는 비지 않은 문자열이면 받는다. 그래서 ID 형식이 아닌 `grant_id`는 헌장 검사를 통과하고 저장 단계에서 거부된다.
- 근거: 두 정의를 필드별로 대조했다.
  - `requirement_record`의 호출자는 `governance.py:76`(헌장 수신 검사)과 `:168`(`governance_view`)이다.
  - 오류 문구를 단언하는 시험은 없다(`grep -rn "academic requirement\|academic criteria\|academic external effect" tests`, 문구 단언 0건).
- 제안:
  - 스키마 `_REQUIREMENT`를 엄격한 쪽으로 맞춰 유일한 모양 정의로 둔다. 비지 않은 텍스트, `criteria`의 minItems 1, `grant_id`의 ID 패턴이 그 내용이다.
  - `requirement_record`는 그 스키마로 검사하고, 교차 항목 규칙과 정규화만 남긴다. 교차 항목 규칙은 요건 ID·효과 ID의 고유성이고, 정규화는 `grant_id`·`required_inputs`의 기본값이다.
- 실익:
  - 약 15행이 준다.
  - 사용자 입력의 수신 검사와 저장 검사가 같은 정의를 쓴다(2절 2항).
- 비용과 위험: `academic.py`, `schemas.py`(STO)를 바꾼다. 오류 문구가 스키마 문구로 바뀐다. 새 상태는 없다.
- 기능·커버리지 영향: 있음. ID 형식이 아닌 `grant_id`가 헌장 수신 단계에서 거부된다.
- 사용자 결정 관련: 없음
- 확신도: 확인

#### RES-13 위임 자원 한도·요청은 코드가 소수를 허용하지만 저장 스키마는 자연수만 허용한다
- 검토: 1
- 종류: 이음새
- 좌표: `scripts/do_math/delegations.py:42-44`, `:72`; 영역 밖 `scripts/do_math/record_schemas/schemas.py:432-435`, `:583-584`
- 현상: `validate_delegation`과 `_basis`는 `type(v) in (int, float)`를 받는다. 스키마의 `resource_limits`와 `case.resources`는 `mapping(NAT)`이다. 소수 한도는 사용자 결정 수신 검사를 통과한 뒤 게시 단계에서 거부된다.
- 근거: 원문 대조.
- 제안: 두 검사를 음이 아닌 정수(`type(v) is int and v >= 0`)로 좁히거나, 스키마 조각을 참조한다.
- 실익: 값 영역 정의가 하나가 되고, 거부가 수신 단계에서 명확한 문구로 일어난다.
- 비용과 위험: 2행. 새 상태는 없다.
- 기능·커버리지 영향: 있음. 소수 한도가 수신 단계에서 거부된다(지금은 게시 단계에서 거부된다).
- 사용자 결정 관련: 없음
- 확신도: 확인

#### RES-14 질문 소유자 어휘와 운영 역할 쌍이 여러 곳에 문자열로 적혀 있다
- 검토: 1
- 종류: 이음새
- 좌표: `scripts/do_math/questions.py:31`, `:72-74`, `scripts/do_math/question_engine.py:56`; 영역 밖 `scripts/do_math/submission.py:214`
- 현상:
  - 질문 소유자 `{"user","research","operations"}`는 수신자 `questions.link`와 제출 스키마 enum(`submission.py:214`)에 따로 있다. 저장 스키마는 `owner`를 `TEXT`로만 둔다.
  - "운영 질문을 소유하는 역할" `{"operational_review","maintenance"}`는 해소 허용(`questions.py:74`)과 기본 소유자(`question_engine.py:56`)에 따로 있다.
- 근거: `grep -rn "\"research\", \"operations\"\|{\"operational_review\", \"maintenance\"}"`로 찾았다. `submission.py:144`와 `planning.py:145`의 역할 집합은 다른 개념이다(RES 밖 확장 허용 역할, 대기 면제 역할)이라 제외했다.
- 제안: `questions.py`에 `QUESTION_OWNERS`와 `OPERATIONS_ROLES` 두 상수를 두고, 네 곳이 참조한다. 저장 스키마의 `owner`도 같은 enum으로 둔다(STO).
- 실익: 상태 값 사본 3곳이 상수 참조가 된다. 소유자 추가 때 한 곳만 고친다.
- 비용과 위험: 약 5행. 새 상태는 없다.
- 기능·커버리지 영향: 없음
- 사용자 결정 관련: 없음
- 확신도: 확인

#### RES-15 신뢰 환경 기록을 `knowledge.register_environment`가 반쯤 만들고 호출자가 나머지를 채운다
- 검토: 1
- 종류: 경계
- 좌표: `scripts/do_math/knowledge.py:583-594`; 영역 밖 `scripts/do_math/lifecycle_engine.py:673-675`, `scripts/do_math/record_schemas/schemas.py:496-500`
- 현상:
  - `register_environment`는 인스턴스 전체를 `deepcopy`한 뒤 `id`, `toolchain`, `allowed_axioms`, `status`만 가진 기록을 넣는다.
  - 스키마가 요구하는 `source_ref`와 `toolchain_record`는 유일한 제품 호출자(`lifecycle_engine.py:673-675`)가 곧바로 덧붙인다. 신뢰 환경 기록의 모양이 두 모듈에 나뉘어 있다.
  - 지식 모듈이 신뢰 환경의 등록을 맡는 것도 모듈 책임과 맞지 않는다.
- 근거: `grep -rn "register_environment"`: 제품 호출 1건, 시험 1건(`test_knowledge.py:78`)이다.
- 제안: 기록 생성을 호출자의 `trust register` 분기 한 곳으로 옮겨 완전한 기록을 한 번에 만든다. `register_environment`는 지운다.
- 실익: 약 12행이 준다. 신뢰 환경 기록의 모양이 한 곳에 모인다. 등록마다의 인스턴스 전체 `deepcopy` 1회가 준다(드문 사건이라 비용 효과는 작다).
- 비용과 위험: `knowledge.py`, `lifecycle_engine.py`(RUN), 시험 1건. 새 상태는 없다.
- 기능·커버리지 영향: 없음
- 사용자 결정 관련: 없음
- 확신도: 확인

#### RES-16 질문 기록의 "inline" 분기는 생산자 없는 필드와 존재하지 않는 필드를 읽는다
- 검토: 1
- 종류: 미사용
- 좌표: `scripts/do_math/question_engine.py:45`, `:52`, `:61`
- 현상:
  - `inline = bool(execution.get("parent_execution_id"))`가 참일 때만 두 곳이 쓰인다. 하나는 `self.runtime["activities"][execution["activity_id"]]["result_ref"]`이고, 다른 하나는 `"output/"` 접두다.
  - `parent_execution_id`를 쓰는 제품 코드는 없다. 실행 기록에는 `activity_id`가 없고(`engine.py:639`가 지운다), 활동 기록에는 `result_ref`가 없다(`result_refs`다).
- 근거: `grep -rn "parent_execution_id" --include=*.py --include=*.md`: 제품 읽기 2건(`question_engine.py:45`, `engine.py:1993`), 스키마 1건, 시험 2건(값 설정)이다. 쓰기는 0건이다.
- 제안: 세 곳의 inline 분기를 지운다. `engine.py:1993`의 같은 조건과 스키마 필드는 5절에 적었다.
- 실익: 도달하지 않고, 도달하면 `KeyError`가 나는 분기 약 3행이 사라진다.
- 비용과 위험: 없음에 가깝다. 새 상태는 없다.
- 기능·커버리지 영향: 없음
- 사용자 결정 관련: 없음
- 확신도: 확인

#### RES-17 학술 과제만 `feature_version: 5`를 문자열 상수로 싣고, 읽는 곳이 없다
- 검토: 1
- 종류: 미사용
- 좌표: `scripts/do_math/academic_engine.py:136`; 영역 밖 `scripts/do_math/record_schemas/schemas.py:360`
- 현상:
  - 과제의 `feature_version`은 스키마에서 선택 필드(`const STATE_FORMAT_VERSION`)다.
  - 이 필드를 쓰는 제품 생산자는 학술 과제 생성 하나뿐이고, 그것도 상수 대신 `5`를 직접 쓴다.
  - 과제의 이 필드를 읽는 제품 코드는 없다.
- 근거: `grep -rn "feature_version" do_math`에서 과제 관련은 `academic_engine.py:136`과 스키마뿐이다. 나머지는 인스턴스·런타임·프로필·manifest다. 시험 `test_redesign_GOVERNANCE.py:590`이 값을 단언한다.
- 제안: `academic_engine.py:136`의 필드와 과제 스키마의 선택 필드, 시험 단언 1줄을 지운다.
- 실익: 일반 과제와 학술 과제의 모양이 같아진다. `STATE_FORMAT_VERSION`의 사본 하나가 사라진다.
- 비용과 위험: 3행. 새 상태는 없다.
- 기능·커버리지 영향: 없음
- 사용자 결정 관련: 없음
- 확신도: 확인

#### RES-18 쓰지 않는 import가 남아 있다
- 검토: 2
- 종류: 잔재
- 좌표: `scripts/do_math/knowledge.py:13`, `scripts/do_math/revision_engine.py:5-6`
- 현상:
  - `knowledge.py`의 `capture_sources, sources_current` import는 쓰이지 않는다. `sources_current`의 마지막 사용은 `379a171`이 RES-03 처분으로 `knowledge_records.premise_failures`에 옮기면서 사라졌다.
  - `revision_engine.py`의 `CurrentnessChanged`, `new_id`는 경량화 전(`98ac7e5`)부터 쓰이지 않았다.
- 근거:
  - 영역 17개 파일을 AST로 검사해, import한 이름 가운데 본문에서 쓰이지 않는 것을 찾았다. 결과는 이 네 이름뿐이다.
  - `git show 379a171 -- knowledge.py`에서 `sources_current` 사용 삭제를 확인했다.
- 제안: 두 import 줄을 지운다.
- 실익: 잔재 2행이 사라지고, `knowledge`→`input_basis`의 불필요한 최상위 의존이 없어진다.
- 비용과 위험: 없음
- 기능·커버리지 영향: 없음
- 사용자 결정 관련: 없음
- 확신도: 확인

## 4. 보존 판정

- `questions`/`question_engine`, `revisions`/`revision_engine`, `academic`/`academic_engine` 분할: 순수 함수와 엔진 믹스인의 경계다. `경량화-조사-2026-09-26/RES.md` 3절 판정의 근거(순수 쪽을 제출 검사·계획 모듈이 import한다)가 현재 원문에서도 성립한다.
- `knowledge`/`knowledge_io`/`knowledge_records` 3분할과 `knowledge.py`의 신뢰 전이 함수(`begin_transition`~`invalidate_environment`): 전이 대상이 K 기록이라 지식 모듈과 결합되어 있다. 옮겨도 줄어드는 판정이 없다. 등록만 떼어 내는 것은 RES-15로 냈다.
- `formal._GIT_ROOTS`(`formal.py:190`, `:198-199`): 키에 없는 입력은 프로젝트가 git 저장소가 되거나 옮겨지는 사건 하나다. 설계 D1에서 드문 사건이고, 시험이 건드리지 않는다(`grep` 0건).
- `formal._SEARCH_PATHS`(`formal.py:191`, `:359-375`): Lake 검색 경로를 정하는 입력(명령 접두, 판본 식별, Lake 실행 파일 해시)이 모두 키에 있다. 무효화는 키 변경으로 자동이며, 시험이 건드리지 않는다.
- `formal._parse_evidence`의 ASCII 이스케이프 해시 3곳: 현재 계약에서는 보존 대상이다. RES-08을 채택할 때만 함께 바꾼다.
- `delegations.py`·`academic.py`·`external.py`의 내용 기반 ID(`DA-`, `AR-`, 24자리 연산 ID)와 `planning._event`: 서로 다른 기록 가족이다. 서로 대조하지 않으므로 공통 도우미로 묶을 실익이 없다. `_event`의 `task_new_input` 시각 의존만 RES-05에서 다룬다.
- `external._http`의 `_url`·`_body` 재호출(`external.py:88-89`): `validate_operation` 직후라 같은 사실의 반복이다. 다만 시험이 `_http`를 직접 부르며(13건) 전송 계층 검사로 쓴다. 지우면 그 커버리지를 잃는다. 실익은 1행이다.
- `knowledge_records.formal_usable`의 원문 해시 재대조: `경량화-조사-2026-09-26/RES.md` 3절 보존 판정과 같다(디스크의 기존 기록은 신뢰 경계 밖).
- `knowledge_io.import_relation`의 `canonical_json(record)`(`:408`): 생산자가 게시 전에 수신자와 같은 함수로 하는 자기 확인이다(2절 2항).
- `scholarly._from_config`의 두 단계 검사(`:61`, `:66`): 상대 경로를 풀기 전후로 검사 대상이 달라서 반복이 아니다.
- `formal._job_run`의 0.02초 폴링(`:266-274`): 정지 콜백 확인 주기다. `job.wait(0.02)`로 바꿔도 지연 차이는 없다.
- `planning.py:724`와 `:731`의 대기 종류 집합 차이(`assessment_input`): `경량화-조사-2026-09-26/RES.md` 3절 판정대로 판정 순서가 다른 두 규칙이다. 두 집합의 `time`만 RES-04에서 다룬다.

## 5. 영역 밖 관찰

- STO `scripts/do_math/repository.py:829-835`: `semantic_content_hash(value, projection=None)`의 `projection`은 시험만 쓴다(`test_redesign_STORAGE.py:643`). 제품 호출 2곳(`engine.py:423`, `knowledge.py:21`)에서는 `exact_content_hash`의 별칭이다.
- STO `scripts/do_math/record_schemas/schemas.py:275`: 실행의 `parent_execution_id`는 생산자가 없다(RES-16).
- ENG `scripts/do_math/engine.py:1993`: `reviewed_execution.get("parent_execution_id")`는 늘 거짓이다(RES-16).
- RUN `scripts/do_math/lifecycle_engine.py:1016-1024`: `task_new_input` 중복 필터는 RES-05가 원인을 풀면 지울 수 있다. 지금은 두 번째 수집 경로가 이 필터를 무력화한다.
- RUN `scripts/do_math/scheduler.py:146-147`: `_schedule_reconsideration`은 갱신마다 런타임 전체와 모든 사건을 `deepcopy`한다. `_refresh_readiness`의 `apply_event_schedule` 복사와 합치면 갱신당 런타임 전체 복사가 2회다.
- OPS `scripts/do_math/governance.py:164-168`: `governance_view`는 부를 때마다 `requirement_record`(검사와 digest)와 정책 해시를 다시 계산한다. `task_ready`→`contract_review_current`→`governance_revisions` 경로로 과제마다 불린다.
- TSA `scripts/tests/test_digest_characterization.py`: 삭제된 도우미와의 바이트 동일성을 단언한다. 결정 1 뒤로 지킬 저장 digest가 없다(RES-08).
- TSB `scripts/tests/research_fixtures.py:782-795`: 경로 키 캐시 네 개를 제품 내부에서 지운다. 근본 원인은 `artifact_key`(`repository.py:42-44`)가 저장소 경로를 저장소 식별로 쓰는 데 있다(STO). RES-10은 그중 하나만 없앤다.
- ENG·STO `scripts/do_math/engine.py:750`, `:1540`: 런타임 필드 `questions`는 운영 알림 문자열 목록이다(`operational_notices`로 보고됨). 질문 연결(`question_links`)과 이름이 겹친다. `academic_engine.py:71`, `scheduler.py:337`, `:399`도 이 목록에 쓴다.
- REV `scripts/do_math/review_cycle.py`(json_digest 11건), IO·STO `scripts/do_math/input_basis.py:39`, `:46`: 상태 값 식별에 `json_digest`를 쓰는지 RES-08과 같은 기준으로 확인할 필요가 있다.

## 6. 작업 기록

- 한 번의 실행으로 확인한 사항 넷:
  - 미리보기 결함(RES-06)은 원문만으로는 zip 적재 시의 경로를 확신할 수 없었다. 임시 zip으로 적재해 경로 불일치를 확인했다.
  - `task_new_input` 중복(RES-05)은 두 수집 경로가 같은 시각을 쓰므로 필터가 유효하리라 예상했다. 실행해 보니 두 번째 경로가 걸러 낸 사건을 다시 넣었다.
  - `_git` 비용(RES-07)은 M-0348 수치만으로는 git 호출의 몫을 가를 수 없었다. 같은 명령을 Job 경로와 직접 호출로 비교했다. 병렬 검토자들이 돌던 부하 상태의 값이라 절대값은 부풀었을 수 있고, 비율을 근거로 삼았다.
  - 미사용 import(RES-18)는 pyflakes가 없어 AST 스크립트로 전수 검사했다.
- 예상과 달랐던 결과: 신뢰 환경 상태 값의 어긋남(RES-02)은 조건 문법 쪽이 틀린 것으로 보고 이력을 따라갔다. 실제로는 `8d2ffd0` 전에 스키마 쪽이 코드와 달랐고, `8d2ffd0`가 스키마만 고치면서 조건 문법이 남았다.
- 접근을 바꾼 지점: 영역 전 정의의 호출자 전수 검색을 파일 전체 `grep` 반복으로 돌렸더니 2분 제한을 넘었다. 백그라운드로 돌려 완료했다. 결과로 나온 이름은 모두 모듈 안에서 쓰이거나, urllib이 동적으로 부르는 재정의(`_NoRedirect.redirect_request`)였다.
- 작문 절차: CLAUDE.md는 이 산출에 `write-for-reader`의 합의·독자 파일과 별도 독해(`writing_flow.py`)를 요구한다. 그러나 기준 7절이 산출 파일 하나 외의 파일 쓰기를 금지하므로 그 절차는 실행하지 않았다. 참조 문서의 규칙 적용과 자기 점검만 했다.
