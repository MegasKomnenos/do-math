# RES 영역 조사 결과: 연구 흐름, 지식, 형식화

RES 영역의 실익은 같은 판정 규칙이 모듈마다 따로 구현된 곳을 정본 함수 하나로 모으는 데 있다. 중복 구현 수와 그 규칙이 닿는 판정 범위로 볼 때 가장 큰 곳은 넷이다.

- 기록 색인(ID에서 기록을 찾는 표)이 여러 벌 구현되어 있고, 한 번의 평가 안에서도 반복해 구성된다(RES-01, RES-02).
- 지식 기록의 전제가 현재 유효한지를 판정하는 코드가 세 곳에 있다(RES-03).
- 형식 증거 규칙이 세 모듈에 다시 적혀 있다(RES-04).
- 질문을 여닫는 규칙이 흩어져 있다(RES-05).

동작을 바꾸는 후보는 넷이며, 모두 사용자 결정이 필요하다. 영향 폐포와 읽기 폐포의 참조 키 통일(RES-09), 후보 형태 검사 공유와 선언명 수신 검사 앞당김(RES-11), 개정 대기의 파생 필드 제거(RES-13), 생산 호출자 없는 API의 정리(RES-14)다. 이 밖에 동작 보존 후보 셋에 동작을 바꾸는 선택 부분이 있다. 버려지는 색인 호출 `revisions.py:9`의 삭제(RES-02), 질문 해소 이력 모양의 통일(RES-05), 개정 요청 기록 `revision_requested`의 모양 통일(RES-06)이다. 모듈 쌍 분할(`questions`/`question_engine` 등)은 순수 함수와 엔진 믹스인의 경계로서 실익이 있으므로 보존한다(3절).

각 후보의 `동작: 보존`은 저장 상태, 반환 값, 대기·후속 흐름, 역할 입력이 그대로라는 뜻이다. 예외 메시지 문구만 바뀌는 경우도 보존으로 분류하고, 해당 후보에 그 사실과 문구를 단언하는 테스트가 있는지를 적었다.

좌표는 조사 시점(커밋 8d2ffd0, 작업 트리 변경 없음)의 현재 원문 행 번호다. 별도 표기가 없으면 경로는 `C:/math/.claude/skills/do-math/scripts/do_math/` 기준이다.

## 1. 읽은 범위

전문을 읽은 파일(행 수):

- `planning.py` 835, `activities.py` 326, `delegations.py` 181, `integration.py` 560
- `knowledge.py` 847, `knowledge_io.py` 398, `knowledge_records.py` 387, `revisions.py` 405, `revision_engine.py` 257
- `question_engine.py` 107, `questions.py` 114
- `academic.py` 258, `academic_engine.py` 233, `scholarly.py` 91, `external.py` 190
- `formal.py` 570(신뢰 환경 경로는 판정 대상에서 제외), `formal_preview.py` 41
- `C:/math/.claude/skills/do-math/references/지식-저작과-재사용.md` 99, `references/학술자료-활용.md` 49
- `C:/math/.claude/skills/do-math/계약/연구-계획.md` 151, `계약/후보-준비.md` 220, `계약/연구-수행.md` 167, `계약/보충-조사.md` 61
- `C:/math/임시/경량화-조사-2026-09-26/기준.md`, `C:/math/docs/do-math/검사-경량화-이음새-계약.md`

이음새를 따라 일부만 읽은 파일(행 범위):

- `engine.py`: 453-475, 604-612, 1528-1536, 2285-2298, 2325-2342, 2840-2866, 3476-3488, 3940-3960, 4020-4060, 4120-4134
- `governance.py`: 332-338, 625-680, 704-722
- `submission.py`: 190-196, 362-374, 575-640, 748-762
- `task_scope.py`: 440-458
- `scheduler.py`: 294-325
- `state_checks.py`: 236-252
- `record_schemas/schemas.py`: 170-180, `record_schemas/domains.py`: 175-185, `record_schemas/__init__.py`: 574-590
- `repository.py`: 360-380
- 테스트 파일은 테스트 이름과 호출 행만 grep으로 확인했다.

## 2. 후보

#### RES-01: 기록 색인(ID→기록)이 모듈마다 다른 모집단으로 구현되어 있다
- 유형: 이음새중복
- 위치:
  - `planning.py:331-341`(`RECORD_FAMILIES`), `planning.py:369-382`(`_records`, ID 중복 시 예외)
  - `knowledge.py:29-41`(`_records`, 생성기, 중복 검사 없음), `knowledge.py:44-46`(`_find`, 선형 탐색)
  - `knowledge_records.py:27-43`(`all_records`, 연구 공간만)
  - `engine.py:453`(`_records`, 조회 CLI용 목록, `question_links` 포함)
  - `academic.py:159-167`(`_evidence`, 다섯 가족만), `question_engine.py:83-86`(`academic._evidence`를 비공개 이름으로 가져다 씀)
  - `governance.py:708-718`(`planning._records`에 `governance_sources`, 원자료 별칭, `question_links`를 덧붙임)
  - `state_checks.py:236-249`(모든 가족의 ID 중복 검사)
  - 원자료 별칭으로 참조를 푸는 반복: `planning.py:219-222`, `planning.py:571-574`, `knowledge_io.py:216-220`, `knowledge_io.py:289`
- 현상: "이 ID가 가리키는 기록이 무엇인가"라는 한 개념을 일곱 곳이 각자 정의한다. 가족 집합이 서로 다르다.
  - `knowledge._records`에는 grants·decisions·sources·external_operations·review_cycles가 없다.
  - `all_records`에는 런타임 기록이 없다.
  - `planning._records`에는 question_links가 없어 `governance.py:718`이 따로 덧붙인다.
  - 중복 ID 처리도 갈린다. `planning._records`와 `all_records`는 예외를 내고, `knowledge._records`는 첫 항목을 돌려준다.
  - `knowledge._find`는 호출마다 전 기록을 순회하므로, `validate_basis`(`knowledge.py:69-91`)는 기초 행 수 m에 대해 O(m·N)이다.
- 제안: 가족 표의 정본을 `planning.RECORD_FAMILIES` 하나로 두고, 색인 함수 `record_index(instance, runtime, *, families=None)` 하나를 `planning.py`에 둔다(`_records`의 공개판).
  - `knowledge._find`는 색인의 dict 조회로 바꾼다.
  - `knowledge._records`와 `all_records`, `academic._evidence`는 같은 색인에 현재의 가족 필터를 적용해 만든다. 현재 모집단을 그대로 유지하려면 필터를 지금 목록과 같게 둔다.
  - `engine._records`는 색인 결과에 `family` 표지를 붙이는 표현 함수로 줄인다.
  - `question_links`와 원자료 별칭을 색인에 포함할지는 선택 인자로 둔다.
  - `question_engine.py:84-85`의 `resolve` 클로저는 `academic_engine.py:94-95`의 `_academic_evidence`와 같으므로 그 메서드를 재사용한다.
- 동작: 보존. 가족 필터를 현재 목록과 같게 유지하는 경우다. 필터를 넓히면 `capture_basis`가 지금은 거부하는 ID(예: 결정·원자료)를 받아들이게 되므로 변경이 된다.
- 실익:
  - 추정: 모집단 정의 7곳이 1곳으로 줄고, 약 40행이 줄어든다.
  - `_find` 한 번이 O(N)에서 O(1)로 바뀐다.
  - 한 곳의 가족 추가가 다른 곳에서 누락되는 실패 경로가 사라진다.
- 위험과 보호: 가족 필터를 잘못 옮기면 기초 해시 대상이 바뀐다. `tests/test_knowledge.py`(`test_history_is_not_a_current_dependency`, `test_source_currentness_and_reassessment_preserve_judgment`), `tests/test_query_records.py`, `tests/test_delegation_storage.py`(`test_structured_reference_survives_git_and_stales_when_its_record_changes`), `tests/test_academic.py`가 덮는다.
- 확신: 높음 — 일곱 구현과 가족 차이는 원문에서 직접 확인했다. 정본을 `planning.py`에 두는 판단의 확신은 중간이다. `knowledge`가 `planning`을 지연 import하는 곳이 늘어나기 때문이다.
- 다른 영역: `engine.py`, `governance.py`, `state_checks.py`(저장·검사 영역), `question_engine.py`

#### RES-02: 과제 착수 판정 한 번에 기록 색인을 여러 번 새로 만든다
- 유형: 운영비용
- 위치:
  - `planning.py:541`(검사용으로 만들고 버림), `planning.py:568`(다시 만듦)
  - `planning.py:210`(`capture_task_basis`), `planning.py:211`과 `planning.py:66`(`action_read_ids`)
  - `planning.py:127`, `planning.py:139`(`revision_waits`에서 자기 행동과 살아 있는 실행마다 `action_read_ids`)
  - `questions.py:15`(`user_waits`→`action_read_ids`)
  - `revisions.py:9`(`capture_targets`가 결과를 버리는 `_records` 호출, `target_changes`가 대상마다 반복: `revisions.py:31`)
- 현상: `task_ready` 한 번이 색인을 최소 5회, 살아 있는 실행 수를 L이라 하면 5+L회 만든다. `ready_task_ids`(`planning.py:254-256`)와 `exhaustion_state`(`planning.py:680`)는 미종결 과제마다 `task_ready`를 부른다. `revisions.py:9`는 결과를 쓰지 않고 중복 ID 예외만 기대한다.
- 제안:
  - `task_ready` 입구에서 색인을 한 번 만든다.
  - `action_read_ids`, `capture_task_basis`, `revision_waits`, `user_waits`에 `records=` 인자로 넘긴다. 인자가 없으면 지금처럼 만든다.
  - `ready_task_ids`와 `exhaustion_state`는 과제 루프 밖에서 한 번 만들어 넘긴다. 같은 입력 상태 안에서만 공유한다(이음새 계약 4절의 메모리 상태 규칙상 head 키로 메모이즈하지 않는다).
  - `revisions.py:9`는 지운다. 전역 ID 유일성은 게시 전 `engine.py:2293`과 검사 `state_checks.py:236-249`가 맡는다.
- 동작: 색인 재사용은 보존이다. `revisions.py:9` 삭제는 변경이며 선택 사항이다. 삭제하면 `capture_targets`를 부르는 메모리 경로(예: `governance.py:668`)에서 중복 ID 예외가 이 지점에서 나지 않고, 게시 전 검사(`engine.py:2293`)나 상태 검사에서 난다. 그 시점이 필요하면 삭제하지 않고 색인 재사용만 한다.
- 실익:
  - 측정: 기록 9300건(지식 2000·형식 1000·해설 2000·과제 300·실행 3000·활동 1000)의 `planning._records` 1회 구성은 2.92ms다(200회 평균). 기록마다 `id` 필드 하나만 가진 합성 상태이며, `C:/math/.claude/skills/do-math/scripts/`에서 다음 명령으로 측정했다.

    ```
    python -c "import timeit; from do_math import planning; inst={'id':'IN-1','knowledge':{f'KN-{i}':{'id':f'KN-{i}'} for i in range(2000)},'formal_results':{f'FR-{i}':{'id':f'FR-{i}'} for i in range(1000)},'expositions':{f'XP-{i}':{'id':f'XP-{i}'} for i in range(2000)}}; rt={'tasks':{f'TK-{i}':{'id':f'TK-{i}'} for i in range(300)},'executions':{f'EX-{i}':{'id':f'EX-{i}'} for i in range(3000)},'activities':{f'AY-{i}':{'id':f'AY-{i}'} for i in range(1000)}}; print(timeit.timeit(lambda: planning._records(inst,rt), number=200)/200*1000)"
    ```
  - 추정: 과제 300개, L=3이면 `ready_task_ids` 한 번에 300×8×2.92ms ≈ 7초를 색인 구성에 쓴다. 공유하면 3ms가 된다.
  - 규모가 작은 인스턴스에서는 체감 차이가 작다.
- 위험과 보호: 전달한 색인이 평가 도중 바뀐 상태를 반영하지 못할 수 있다. `task_ready`는 상태를 쓰지 않으므로 한 호출 안의 공유는 안전하다. `tests/test_planning.py`, `tests/test_redesign_TASKS.py`, `tests/test_questions.py`(`test_only_the_explicitly_affected_task_waits_and_plan_can_choose_other_tasks`)가 덮는다.
- 확신: 높음 — 호출 사슬과 측정값은 원문과 실행으로 확인했다. 초 단위 수치는 추정이다.
- 다른 영역: `questions.py`(이 영역), `scheduler.py`(착수 판정을 부르는 쪽)

#### RES-03: 지식 기록의 전제 현재성 판정이 세 함수에 따로 있다
- 유형: 이음새중복
- 위치:
  - `knowledge_records.py:144-164`(`usable_links`의 기록 전제)
  - `knowledge_records.py:287-308`(`assessment_current`의 기록 전제)
  - `knowledge.py:177-202`(`assess_research_use`)
  - `knowledge.py:210-213`(`assess_use`의 지식 분기가 `usable_links`가 이미 거른 `kind_use_suspended`를 다시 본다)
  - 지연 import 순환: `knowledge_records.py:162`, `knowledge_records.py:296`
- 현상: 세 함수가 같은 조건 묶음을 각자 적는다. 기록 lifecycle `active`, `kind_use_suspended` 아님, 종류 정의 `active`, `sources_current`, 의존 기록의 재귀 판정, `relation_endpoint_basis` 유효가 그 묶음이다.
  - `usable_links`와 `assessment_current`의 기록 조건은 완전히 같다.
  - `assess_research_use`는 여기에 `use_suspended`와 해설 lifecycle을 더하고, 관계 기초는 보지 않으며, 의존을 연구 수준으로 재귀한다.
  - 한 곳에만 조건을 더하면 K 판정과 동일성 판정 복원(`set_assessment_use`, `knowledge_records.py:317-319`)이 서로 다른 전제를 쓰게 된다.
- 제안: `knowledge_records.record_premises_current(instance, record, *, visiting, dependency_check)` 하나를 둔다.
  - `usable_links`와 `assessment_current`는 `dependency_check=usable_links`로 부른다.
  - `assess_research_use`는 공통 부분을 이 함수로 판정하고 자기 추가 조건(`use_suspended`, 해설, 연구 수준 재귀)만 남긴다. 사유 문자열(`research_record_not_active` 등)을 유지하려면 공통 함수가 실패 사유 목록을 돌려주게 한다.
  - `assess_use`의 `and not record.get("kind_use_suspended")`(`knowledge.py:212`)는 지운다.
- 동작: 보존
- 실익:
  - 추정: 약 20행이 준다.
  - K 판정·판정 복원·연구 재사용의 전제 정의가 한 곳이 된다.
  - 함께 볼 비용: `formal_usable`(`knowledge_records.py:124-134`)은 호출마다 `lean_code`를 해시한다. `plan_impact`(`knowledge.py:259`)는 모든 지식에 `usable_links`를 부른다. 필요하면 이음새 계약 4절대로 `lean_code` 문자열을 키로 캐시한다.
- 위험과 보호: 재귀 방문 집합(`_visiting`)의 의미가 두 함수에서 다르다(`assessment_current`는 `{record['id']}`로 시작). 합칠 때 이 차이를 인자로 보존해야 한다. `tests/test_knowledge.py`, `tests/test_redesign_KNOWLEDGE.py`, `tests/test_knowledge_io.py`(`test_mathematical_relation_requires_match_in_addition_to_active_use`), `tests/test_redesign_TASKS.py`가 덮는다.
- 확신: 높음 — 조건 목록을 행 단위로 대조했다.
- 다른 영역: 없음

#### RES-04: 형식 증거 규칙(금지 공리, 증거 필드 목록, 원문 해시)이 세 모듈에 다시 적혀 있다
- 유형: 이음새중복, 수신재검사중복
- 위치:
  - 금지 공리: `formal.py:556`, `knowledge_records.py:208-211`, `knowledge.py:754-756`
  - 증거 필드 목록: `formal.py:141`(`compare_formal_results`), `knowledge_records.py:202`, `knowledge.py:629-632`(전이 대상에 복사)
  - 원문 해시 `sha256(lean_code.encode())`: `formal.py:436`, `knowledge.py:626`, `knowledge_records.py:133`, `knowledge_records.py:198`
  - 전이 활성화의 재검사: `knowledge.py:750-756` 직후 `knowledge.py:757`(`validate_formal_evidence`)
- 현상:
  - 금지 공리 규칙("`sorryAx`이거나 허용 목록 밖이면 거부")을 생산자(`formal._parse_evidence`)와 수신자 둘이 각자 표현한다.
  - 증거를 이루는 네 필드(`declaration_evidence`, `dependency_closure`, `dependency_evidence`, `axioms`)의 목록도 세 곳에 따로 있다.
  - `activate_transition`은 750-756행에서 원문 해시·툴체인·선언·공리를 검사한 뒤, 757행에서 같은 항목을 `validate_formal_evidence`로 다시 검사한다. 두 검사가 같은 결론을 내는 근거는 다음과 같다.
    - 750행의 `target["source_sha256"]`은 `begin_transition`이 같은 형식 결과의 `lean_code`로 계산한 값이다(`knowledge.py:626`).
    - 747행은 `record_digest(formal)`이 전이 시작 때와 같음을 확인한다. `record_digest`는 `lean_code`를 정확 해시에 포함한다(`knowledge_records.py:12-17`).
    - 따라서 750행과 757행의 원문 검사는 같은 결론을 낸다. 툴체인(750)·선언(752)·공리(754-756)는 757행이 같은 값으로 다시 검사한다.
- 제안:
  - `formal.py`에 `FORMAL_EVIDENCE_FIELDS`, `lean_source_sha256(code)`, `forbidden_axioms(axiom_rows, allowed)`를 둔다. `_parse_evidence`, `validate_formal_evidence`, `compare_formal_results`, `begin_transition`, `formal_usable`이 이를 참조한다.
  - `knowledge.py:750-756`을 지우고 757행 하나로 판정한다.
  - 수신 쪽 검사(`validate_formal_evidence`)는 유지한다. 검증 결과는 하위 프로세스 출력으로 신뢰 경계 밖에서 온다.
- 동작: 보존. 750-756행의 오류 문구(`transition source or environment mismatch` 등)가 757행의 문구로 바뀐다. 이 문구를 단언하는 테스트는 없다(`grep -rn "transition source or environment mismatch\|transition declarations mismatch\|unapproved axioms" tests`, 결과 없음).
- 실익:
  - 추정: 약 10행이 준다.
  - 공리 정책 변경(예: 허용 공리 판정 방식)이 세 곳이 아닌 한 곳의 수정으로 끝난다.
- 위험과 보호: `formal.py`의 import를 늘리면 worker 적재(`_job_run`의 `from do_math.formal import _worker`)에 영향이 없는지 확인해야 한다. 추가 함수는 표준 라이브러리만 쓴다. `tests/test_formal.py`(`test_missing_axiom_output_fails` 등), `tests/test_knowledge.py`(`test_complete_transition_preserves_old_evidence_and_changes_links`), `tests/test_redesign_KNOWLEDGE.py`가 덮는다.
- 확신: 높음 — 동치 근거를 행 단위로 확인했다.
- 다른 영역: 신뢰 환경 전이(`begin_transition`, `activate_transition`)는 직전 라운드의 신뢰 환경 기록과 인접하지만, 이 후보는 그 기록 형태를 바꾸지 않는다.

#### RES-05: 질문의 열림·닫힘 규칙이 다섯 곳에 흩어져 있다
- 유형: 이음새중복
- 위치:
  - 닫기 1(사용자 결정): `questions.py:46-61`(`resolve_user`)
  - 닫기 2(AI 확장): `question_engine.py:67-90`(`_apply_question_resolutions`)
  - 닫기 3(입력 초과 재시도): `engine.py:2851-2863`(`_resolve_input_overflow_question`)
  - 해소 허용 판정의 이중 구현: `questions.py:84-92`(`validate_extensions`, 제출 검사) 대 `question_engine.py:74-80`(적용)
  - 스키마와 겹치는 재검사: `question_engine.py:81-82` 대 `submission.py:193-194`(`disposition` enum, `evidence_refs` minItems 1, `reason` 필수)
  - "열린 사용자 질문" 술어: `questions.py:8`, `questions.py:52`, `questions.py:103`, `revisions.py:225-226`, `revisions.py:322-324`, `question_engine.py:107`
  - `unresolved_target_ids` 대체값 읽기: `questions.py:19`, `questions.py:21`, `questions.py:54`, `questions.py:58`, `governance.py:637`, `record_schemas/__init__.py:585`
- 현상:
  - 세 닫기 경로가 `status`, `resolution_ref`, `unresolved_target_ids`, `resolution_history`를 각자 다른 모양으로 쓴다. 경로 1은 대상별 부분 해소와 이력을 쓰고, 경로 2는 이력을 쓰지 않으며, 경로 3은 다른 모양의 이력(`kind`, `evidence`)을 쓴다.
  - AI 해소의 허용 조건(구별된 ID, 열린 상태, 소유자가 research 또는 operations, operations 질문은 운영 역할만)은 제출 검사와 적용에 서로 다른 코드로 두 번 있다.
  - 질문 링크를 만드는 곳은 `questions.link` 하나이고, 이 함수는 항상 `unresolved_target_ids`를 쓴다(`questions.py:36`). 그런데도 읽는 여섯 곳이 필드 부재에 대비한 대체값을 쓴다.
- 제안: `questions.py`에 세 함수를 둔다.
  - `resolution_error(row, role) -> str | None`: `validate_extensions`와 `_apply_question_resolutions`가 함께 부른다. 적용 시점에도 부르는 이유는 제출과 적용 사이에 다른 실행이 같은 질문을 닫을 수 있기 때문이다.
  - `close(row, *, status, resolution_ref, affected_ids=None, history_entry=None)`: 세 닫기 경로가 부른다. 이력 모양은 인자로 받아 현재 저장 형태를 유지한다.
  - `open_targets(row)`: 대체값 읽기 여섯 곳을 대신한다.
  - `question_engine.py:81-82`는 지운다. 같은 조건을 수신 스키마가 먼저 거부한다.
- 동작: 보존. 이력 모양을 한 가지로 통일하면 저장 기록이 바뀌므로 그때는 변경이며 사용자 결정 대상이다.
- 실익:
  - 추정: 약 25행이 준다.
  - 질문 상태 전이의 정본이 한 모듈이 된다.
  - 해소 허용 조건의 생산자·수신자 불일치 경로가 사라진다.
- 위험과 보호: `open_targets`에서 대체값을 없애려면 `do-math-state/5`로 저장된 기존 질문 링크 가운데 `unresolved_target_ids`가 없는 행이 없어야 한다. 스키마는 이 필드를 필수로 두지 않는다(`record_schemas/schemas.py:175-177`, `record_schemas/domains.py:180`). 기존 저장 상태는 확인하지 않았으므로 대체값은 도우미 안에 남긴다. `tests/test_questions.py`(`test_resolving_one_user_question_preserves_the_other`, `test_an_ai_extension_cannot_resolve_a_user_question`, `test_retry_bypasses_only_the_question_for_its_held_overflow`, `test_scoped_continuation_resolves_only_the_current_hold_question`), `tests/test_redesign_GOVERNANCE.py`, `tests/test_input_recovery.py`가 덮는다.
- 확신: 높음 — 다섯 위치와 경로별 쓰기 차이를 원문에서 확인했다.
- 다른 영역: `engine.py`(입력 초과 재시도), `governance.py`, `submission.py`, `record_schemas`

#### RES-06: 개정 필수(required) 판정이 두 곳에 있고, `revision_requested`의 모양이 세 가지다
- 유형: 이음새중복(선택 부분은 기타: 저장 형태 통일)
- 위치:
  - 판정: `revisions.py:81-82`, `revision_engine.py:93`
  - `revision_requested`를 쓰는 곳: `engine.py:4130`(`{execution_id, item_reviews}`), `governance.py:666`(`{source, revision, reason}`), `revision_engine.py:155`(`{revision, source, reason}`)
  - 읽는 곳: `planning.py:553-555`(`revision` 동등 비교), `scheduler.py:315`, `submission.py:370`
- 현상:
  - 같은 술어("`revision_requested`가 있거나, 현재 판본의 검토 중 승인이 아닌 것이 있다")가 제출 검사와 개정 요청 결속에 따로 있다.
  - `engine.py:4130` 모양에는 `revision`이 없어서 `task_ready`의 개정 요청 관문(`planning.py:554`)이 이 요청을 보지 못한다. 이 경우에는 승인 검토가 없다는 다음 관문(`planning.py:564`)이 같은 `not_ready`를 낸다.
- 제안:
  - `planning.revision_required(task)` 하나를 두고 두 곳이 부른다.
  - 선택: `engine.py:4130`도 `revision`, `source`, `reason`을 담게 해 모양을 하나로 맞춘다.
- 동작: 판정 통합은 보존이다. 선택 부분은 변경이며, 계약 검토 반려 뒤 `task_ready`의 오류 문구가 "current revision lacks approved contract review"에서 "a contract revision was requested by …"로 바뀐다. 상태(`not_ready`)와 대기 목록은 같다.
- 실익:
  - 추정: 약 3행이 준다.
  - 필수 판정 기준이 한 곳이 된다.
- 위험과 보호: `tests/test_contract_checks.py`, `tests/test_redesign_TASKS.py`, `tests/test_walkthrough_repairs.py`가 덮는다.
- 확신: 높음(판정 중복), 중간(모양 통일이 문구 외에 영향을 주지 않는지는 세 읽기 지점만 확인했다)
- 다른 영역: `engine.py`, `governance.py`, `scheduler.py`, `submission.py`

#### RES-07: "재생성 시각은 관찰 시각보다 뒤" 규칙이 세 번, 파서 두 종으로 표현된다
- 유형: 이음새중복
- 위치: `submission.py:591-595`(생산자 자기 확인과 수신 검사, `governance.timestamp`), `revisions.py:384-390`(수신 후 조용히 버림, `governance.timestamp`), `revisions.py:192-194`(기록 시 예외, `planning._utc`)
- 현상: 같은 규칙을 세 곳이 각자 적는다. 기준 시각은 모두 같은 값이다(`engine.py:3483`에서 `execution["observed_at"] = context["observed_at"]`). 문서도 같은 입력 시각 대조를 요구한다(`계약/후보-준비.md:186`).
- 제안: `revisions.regeneration_time_valid(regenerate_after, observed_at) -> bool`을 두고 세 곳이 부른다. 파서는 RES-08의 정본을 쓴다.
- 동작: 보존
- 실익: 추정 약 5행이 준다. 규칙 변경 지점이 하나가 된다.
- 위험과 보호: `tests/test_redesign_TASKS.py`, `tests/test_static_review_repairs.py`, `tests/test_walkthrough_followup.py`가 덮는다.
- 확신: 높음 — 세 위치와 기준 시각의 동일성을 원문에서 확인했다.
- 다른 영역: `submission.py`

#### RES-08: 시간대 필수 ISO 시각 파서 함수가 네 벌 있다
- 유형: 이음새중복
- 위치:
  - 파서 함수, 이 영역: `planning.py:662-666`(`_utc`), `delegations.py:8-13`(`_now`), `external.py:18-23`(`_now`)
  - 파서 함수, 영역 밖: `governance.py:332-338`(`timestamp`)
  - 같은 식을 함수 없이 직접 쓰는 영역 밖 세 곳: `observations.py:243`, `provider_wait.py:15`, `preflight.py:56`
  - 검색식: `grep -rn "fromisoformat" --include=*.py do_math`
- 현상: 네 함수가 모두 `fromisoformat(value.replace("Z", "+00:00"))`에 시간대 필수 검사를 붙인다. 차이는 둘이다. `None`의 뜻이 다르다(`governance.timestamp`·`delegations._now`는 현재 시각, `planning._utc`·`external._now`는 거부). UTC 변환 여부도 다르다(`delegations._now`는 변환하지 않음).
- 제안: 정본 하나(`governance.timestamp`, 또는 worker 적재까지 고려하면 `file_io`에 `utc_timestamp`)를 두고 나머지는 이를 부른다. `None` 처리는 호출자가 `now`를 명시해 넘기게 한다. 이렇게 하면 `planning._utc(None)`의 거부 동작을 유지할 수 있다.
- 동작: 보존. 오류 문구만 달라진다.
- 실익: 추정 약 15행이 준다. 시각 형식 규칙이 한 곳이 된다.
- 위험과 보호: `external`은 `governance`가 import하므로(`governance.py:16`) `external`이 `governance`를 최상위에서 import하면 순환이 생긴다. `file_io`에 두면 이 순환이 없다. `tests/test_external.py`, `tests/test_delegation_storage.py`, `tests/test_planning.py`가 덮는다.
- 확신: 높음 — 네 구현을 직접 비교했다.
- 다른 영역: `governance.py`, `observations.py`, `provider_wait.py`, `preflight.py`, `file_io.py`(공유 커널)

#### RES-09: 영향 폐포와 읽기 폐포가 "참조 필드"를 서로 다르게 정의한다
- 유형: 이음새중복, 문제 발생 여지
- 위치:
  - `knowledge.py:122-127`(`_STRICT_REFERENCE_KEYS`, `_REFERENCE_KEYS`), `knowledge.py:157-174`(`_explicit_refs`)
  - `planning.py:85-88`(`action_read_ids`의 참조 키)
  - `integration.py:35-38`(`REFERENCE_KEYS`, 묶음 안 새 객체 폐포)
- 현상: 지식이 바뀌었을 때 영향받는 기록을 계산하는 `plan_impact`와, 과제가 읽는 기록을 계산하는 `action_read_ids`가 참조 필드 목록을 따로 가진다.
  - `basis_refs`, `authority_refs`, `profile_refs`, `occurrence_condition`은 읽기 참조이지만 영향 참조가 아니다.
  - `_explicit_refs`는 목록에 없는 키의 문자열 배열을 참조로 읽지 않는다.
  - 실행 확인 결과, 지식 KN을 `basis_refs`로만 가리키는 과제는 `plan_impact`의 영향 집합에 들지 않는다. 같은 과제의 `action_read_ids`에는 KN이 든다. 확인 명령은 아래와 같다(`scripts/`에서 실행). TK-2는 `inputs`, TK-1은 `basis_refs`, TK-3은 `authority_refs`로 KN을 참조한다. 첫 출력(영향 집합)은 `['TK-2']`, 둘째 출력(TK-1의 읽기 집합)은 `['KN-0000000000000000000000000A', 'TK-1']`였다.

    ```
    python -c "from do_math import knowledge, planning; K='KN-0000000000000000000000000A'; inst={'id':'IN-1','knowledge':{K:{'id':K,'family':'knowledge','lifecycle':'active'}}}; rt={'tasks':{'TK-1':{'id':'TK-1','basis_refs':[K]},'TK-2':{'id':'TK-2','inputs':[K]},'TK-3':{'id':'TK-3','authority_refs':[K]}}}; print(knowledge.plan_impact(inst,rt,[K],[])['computed_impact']); print(sorted(planning.action_read_ids({'role':'research_work','target':'TK-1'},inst,rt)))"
    ```
  - 이 차이의 결과는 둘이다. 첫째, KN이 개정·철회되어도 TK-1의 `input_current`는 거짓이 되지 않는다. 착수는 계약 검토의 `task_basis`(`planning.py:201-204`)가 막는다. 둘째, 생산자가 TK-1을 `impact_set`에 선언하면 `extra_declarations`가 되어 독립 검토가 강제된다(`knowledge.py:274-276`).
- 제안: 기록 참조 필드의 정본 표 하나(예: `planning.REFERENCE_FIELDS`, 엄격·완화 구분 포함)를 두고 `_explicit_refs`와 `action_read_ids`가 함께 쓴다. `integration.REFERENCE_KEYS`는 같은 응답 안의 새 제목 참조(`task_title`, `target_ids` 등)를 다루는 다른 개념이므로 합치지 않는다.
- 동작: 변경. 개정·철회의 영향 계획이 `basis_refs`·`authority_refs`·`profile_refs`로 참조하는 기록까지 포함하게 된다. 그러면 사용 정지와 재평가 대상이 늘고, 독립 영향 검토 요구 조건이 달라진다. 사용자 결정 대상이다.
- 실익:
  - 추정: 참조 정의가 한 곳이 된다.
  - 영향 선언과 계산의 불일치로 생기는 불필요한 독립 검토 경로가 사라진다.
- 위험과 보호: 영향 집합이 커지면 기존 흐름의 재평가 비용이 늘 수 있다. `tests/test_knowledge.py`(`test_history_is_not_a_current_dependency`), `tests/test_impact_bundle.py`(`test_ordinary_execution_source_dependency_still_propagates`, `test_coupled_changes_use_the_single_reviewed_s0_plan`)가 덮는다.
- 확신: 중간 — 불일치는 실행으로 확인했다. 두 목록의 차이가 의도인지는 계약 문서에서 근거를 찾지 못해 미확인이다.
- 다른 영역: `integration.py`(이 영역)

#### RES-10: `validate_relation`이 같은 동일성 판정 술어로 판정 기록을 두 번 순회한다
- 유형: 복잡성, 운영비용
- 위치: `knowledge_io.py:343-352`(형식 결과 참조마다 순회), `knowledge_io.py:358-369`(판정 참조 검사용 재순회)
- 현상: 두 루프가 같은 술어로 판정 기록을 고른다. 술어는 `formal_result_id` 일치, `decision == "match"`, `assess_use(...)["valid"]`, 관계 주장의 네 필드 일치다. `assess_use`는 판정마다 `assessment_current`를 부르고, 이 함수는 전 지식을 순회한다(`knowledge_records.py:297-307`). `evaluate_condition`의 `relation_exists`(`planning.py:433-457`)는 후보 관계마다 이 함수를 부른다.
- 제안: 술어를 만족하는 판정 집합 `establishing`을 한 번 계산하고, 두 사유 목록을 이 집합에서 만든다.
- 동작: 보존(같은 사유 목록)
- 실익: 추정 약 10행이 준다. 판정당 `assessment_current` 호출이 최대 절반으로 준다.
- 위험과 보호: `tests/test_knowledge_io.py`(`test_mathematical_relation_requires_match_in_addition_to_active_use`, `test_mathematical_relation_requires_exact_formal_identity_and_current_endpoints`)가 덮는다.
- 확신: 높음
- 다른 영역: 없음

#### RES-11: 지식 후보의 형태 검사가 제출 검사와 가져오기에 따로 있고, 선언명 문법은 형식 검사 때에야 검사된다
- 유형: 이음새중복, 생산자자기확인부재
- 위치: `submission.py:748-758`(제출 검사), `knowledge_io.py:233-235`, `knowledge_io.py:249-255`, `knowledge_io.py:268-269`(가져오기), `formal.py:167-171`(`_ident`, 사용처는 `formal.py:438` 하나)
- 현상:
  - 본문 필드 비공백, 선언명 서로 다름, `lean_code`가 있으면 선언명 필수라는 조건을 두 곳이 각자 적는다.
  - 선언명 문법(`_ident`)은 둘 다 검사하지 않는다. 그래서 문법에 맞지 않는 선언명은 후보로 저장된 뒤, 형식 검사 실행이 `invalid declaration`으로 거부한다(`tests/test_formal.py:175` `test_invalid_declaration_rejected`). 비용은 형식 검사 실행 한 회와 그 뒤의 개정 흐름이다.
  - 생산자는 `preview`(`formal_preview.py`)를 실행했을 때만 이 결함을 미리 안다.
  - 문서는 선언명 사전 검사를 설명한다(`계약/연구-수행.md:92`).
- 제안: `knowledge_io.candidate_shape_errors(candidate) -> list[str]`(순수 함수, `formal._ident` 포함) 하나를 둔다. 제출 검사(생산자 로컬 검사와 중앙 수신이 같은 코드)와 `import_candidate`가 함께 부른다. 새 제목으로 의존을 가리키는 제출 형태와 ID로 가리키는 가져오기 형태의 차이는 이 함수 밖에 둔다.
- 동작: 변경. 문법에 맞지 않는 선언명을 가진 제출이 형식 검사 단계가 아니라 수신 단계에서 반환된다. 생산자는 로컬 검사로 미리 알 수 있게 된다.
- 실익:
  - 추정: 약 10행이 준다.
  - 잘못된 선언명마다 형식 검사 실행 1회와 후속 개정 1회가 사라진다.
- 위험과 보호: `_ident`가 허용하는 문법보다 실제 Lean이 넓게 허용하는 이름은 수신 단계에서 거부된다. 이 제한은 지금도 형식 검사가 같은 함수로 거부하므로 결과는 같고 시점만 앞당겨진다. `tests/test_formal.py`(`test_actual_prime_declarations_have_signatures_and_axioms`, `test_invalid_declaration_rejected`), `tests/test_knowledge_io.py`, 제출 검사 테스트가 덮는다.
- 확신: 높음(중복), 중간(제출 검사가 로컬 검사 도구와 같은 코드라는 판단은 `submission.py:575-579`의 공용 함수 구조에 근거하며, 로컬 도구의 호출 경로는 끝까지 추적하지 않았다)
- 다른 영역: `submission.py`

#### RES-12: 지식 가져오기 경로의 같은 검사 반복과 전체 사본 두 벌
- 유형: 수신재검사중복, 운영비용
- 위치:
  - ID 존재 검사: `knowledge_io.py:266`, 곧바로 부르는 `knowledge_records.py:65`
  - 종류 정의 조회 두 번: `knowledge_io.py:237`, `knowledge_io.py:270`
  - 인스턴스 전체 사본 두 벌: `knowledge_io.py:236`(`ensure_ontology`의 deepcopy), `knowledge_records.py:63`(`initialize_families`의 deepcopy)
  - 묶음 적용 경로의 재검사: `integration.py:237-240`(`bundle_impact_request`가 `integration.py:80-82`에서 이미 한 좌표 수 검사), `integration.py:244-250`(교체 ID의 구별·존재 검사. `import_candidate`가 `knowledge_io.py:266`에서 같은 조건으로 거부한다)
- 현상: 같은 프로세스 안에서 값이 바뀌는 경로 없이 같은 조건을 연달아 검사한다. `import_candidate` 한 번에 인스턴스 전체 deepcopy가 두 번 일어난다. `replace_knowledge`(`knowledge.py:519-522`)와 부수 통찰 가져오기(`engine.py:3948`)가 이 경로를 쓴다.
- 제안:
  - `create_candidate`의 ID 검사와 사본을 빼고 호출자가 준 사본에 쓰게 한다. 호출자는 `import_candidate` 하나다.
  - `_definition_for`는 한 번만 부른다.
  - `integration.py:237-240`과 `integration.py:244-250`을 지운다. 교체 ID 검사를 적용 전에 두려는 목적이 있다면 이유를 주석으로 남기고, 없다면 지운다. 모두 메모리 사본 위의 작업이므로 예외 시점이 바뀌어도 결과 상태는 같다.
- 동작: 보존. 오류 문구만 달라진다. 이 문구를 단언하는 테스트는 없다(`grep -rn "knowledge change coordinates differ\|replacement ID already exists\|replacement IDs must be globally distinct" tests`, 결과 없음).
- 실익: 추정 약 12행이 준다. 가져오기 1회당 인스턴스 deepcopy 1회가 준다.
- 위험과 보호: `create_candidate`를 다른 곳에서 직접 부르게 되면 검사가 빠진다. 지금 호출자는 `knowledge_io.py:292` 하나다(`grep -rn "create_candidate" --include=*.py do_math`). `tests/test_knowledge_io.py`(`test_same_id_import_rejected_explicit_revision_preserves_old_authorities`, `test_missing_dependency_is_rejected_without_mutation`), `tests/test_impact_bundle.py`(`test_explicit_replacement_ids_support_forward_sibling_dependencies`)가 덮는다.
- 확신: 높음
- 다른 영역: 없음

#### RES-13: 개정 위임 대기(`revision_dependency`)가 파생값을 따로 저장하고, 한 필드는 실제로 어긋날 수 있다
- 유형: 파생상태
- 위치:
  - `delegated_to_task_id`: 쓰는 곳 `revision_engine.py:128`, `revision_engine.py:246`. 갱신되지 않는 곳 `revision_engine.py:237`. 읽는 곳 `planning.py:116`. 스키마 `record_schemas/domains.py:452`, `record_schemas/__init__.py:593`
  - `revision_targets` 이중 저장(대기 항목과 그 안의 action): `revision_engine.py:52`와 `revision_engine.py:57`, `revision_engine.py:235-236`, `revision_engine.py:243-245`. 읽는 곳 `planning.py:113`, `revision_engine.py:45`(대기 항목 쪽을 우선함)
- 현상:
  - `delegated_to_task_id`는 `delegated_targets`의 첫 값이다. 그런데 `_apply_revision_followup`이 `delegated_targets`를 줄일 때(`revision_engine.py:237`) 이 값을 다시 계산하지 않는다. 그 결과 위임이 빠진 과제를 계속 가리킬 수 있다.
  - 이 값은 `pending_revisions`로 준비·계획 역할의 입력(`engine.py:2122`, `engine.py:2152`, `context_store.py:544-554`)에 들어간다.
  - `revision_targets`는 쓰는 모든 지점이 두 사본을 함께 쓴다. 읽는 곳은 대기 항목 쪽만 본다.
- 제안: `delegated_to_task_id` 저장을 없애고, 역할 입력의 같은 이름 필드는 `pending_revisions`(`planning.py:116`)가 `delegated_targets`의 첫 값으로 계산한다. 대기 항목의 `revision_targets` 사본을 없애고 `entry["action"]["revision_targets"]` 하나만 둔다.
- 동작: 변경. 저장 형태와 스키마가 바뀌므로 기존 `do-math-state/5` 기록의 이행이 필요하다. 역할 입력의 `delegated_to_task_id`는 이름과 위치가 그대로이고, 값은 항상 현재 `delegated_targets`와 일치하게 된다. 문서는 이 필드를 언급하지 않는다(`references/CLI-실행-계약.md:926`, `references/공통-실행.md:61`은 `revision_targets`와 `delegated_targets`만 언급).
- 실익:
  - 추정: 약 8행이 준다.
  - 어긋난 위임 과제 ID가 AI 입력에 들어가는 실패 경로가 사라진다.
- 위험과 보호: 스키마 참조 검사(`record_schemas/__init__.py:593`)를 함께 고쳐야 한다. `revision_dependency`와 `delegated_to_task_id`를 이름으로 찾는 테스트는 없다(`grep -rln "delegated_to_task_id\|revision_dependency" tests`, 결과 없음). 덮는 테스트: 없음.
- 확신: 높음 — 갱신 누락을 원문에서 확인했다.
- 다른 영역: `record_schemas`(저장 계약), `context_store.py`

#### RES-14: 생산 코드에서 부르지 않는 함수와 도달하지 않는 대기 조건
- 유형: 죽은코드
- 위치:
  - `planning.py:39-51`(`task_reference_changes`)
  - `activities.py:198-220`(`requeue_recovered_execution`)
  - `questions.py:96-114`(`sync_activity_wait`와 그 대기 조건 `{"kind": "user_questions"}`)
  - `academic.py:150-151`(`requirements_changed`)
  - `academic_engine.py:20`(다음 대입 `academic_engine.py:40`이 덮어쓰는 `records` 계산)
- 현상: 검색식은 1절에서 전문을 읽은 모듈 17개의 모든 `def` 이름을 `grep -rnw <이름> --include=*.py do_math`로 전수 검사한 것이다. 이름 문자열 전체를 찾으므로 `getattr` 같은 문자열 호출과 CLI 인자 표에 적힌 이름도 결과에 나타난다. 위 네 함수는 생산 코드 호출자가 없고 테스트만 부른다.
  - `task_reference_changes`: `tests/test_planning.py:183-186`
  - `requeue_recovered_execution`: `tests/test_redesign_ACTIVITIES.py:81`, `:92-99`, `:461-462`
  - `sync_activity_wait`: `tests/test_redesign_EVIDENCE_walkthroughs.py:200`, `:210`, `tests/test_redesign_GOVERNANCE.py:271`, `:274`
  - `requirements_changed`: `tests/test_academic.py:24`
  - `user_questions` 대기 조건을 만드는 생산 코드는 없다(`grep -rn "user_questions"`의 생산 결과는 `questions.py`와 무관한 동명 필드뿐이다).
  - 사용자 질문에 따른 대기는 실제로 `user_waits`(`questions.py:11-21`)와 `waiting_actions`가 맡는다. 결과적으로 활동 대기 경로와 행동 대기 경로의 두 설계 가운데 하나만 연결되어 있다.
- 제안:
  - `task_reference_changes`, `requirements_changed`, `academic_engine.py:20`은 지운다.
  - `sync_activity_wait`와 `requeue_recovered_execution`은 결정이 필요하다. 지우거나, 설계 의도대로 엔진에 연결해야 한다. `tests/test_redesign_ACTIVITIES.py:461`은 "queued recovery has no redispatch API"라는 메시지로 API의 존재 자체를 단언하므로, 이 API는 설계 요구로 작성된 흔적이 있다. 엔진의 대기열 실행 복구가 다른 경로로 같은 일을 하는지는 확인하지 않았다(미확인).
- 동작: 앞의 셋은 보존이다. 뒤의 둘은 결정에 따라 변경이다(API 제거 또는 새 연결).
- 실익: 추정이며, 선택에 따라 다르다.
  - 앞의 셋을 지우면 약 15행과 테스트 약 5행이 준다.
  - 뒤의 둘도 지우면 약 45행과 테스트 약 25행이 더 준다. 생산에서 쓰이지 않는 두 번째 대기 설계도 사라진다.
  - 뒤의 둘을 엔진에 연결하면 행 수는 늘고, 설계와 구현의 불일치가 사라진다.
- 위험과 보호: 테스트가 단언하는 설계 요구를 지우는 일이 된다. 위 테스트들이 덮는다.
- 확신: 높음(호출자 부재), 낮음(뒤의 둘을 지울지 연결할지)
- 다른 영역: `engine.py`(복구 경로), `lifecycle_engine.py`

#### RES-15: 위임 판정의 유효 조건이 기록 시와 사용 시에 다른 코드로 두 번 있다
- 유형: 이음새중복
- 위치: `delegations.py:118-131`(`record_judgment`), `delegations.py:135-156`(`_checked`)
- 현상: 실행 역할 `intent_interpretation`, 실행의 입력 해시 일치, 출력의 `input_sha256` 일치, 원 결정 저자와의 독립을 두 함수가 각자 적는다. 사용 시 재검사는 디스크 왕복 뒤이므로 필요하다.
- 제안: `_judgment_errors(record, execution, output, author_ids)`를 두고 두 곳이 부른다. `_checked`는 여기에 `within_scope`와 봉인 해시 검사를 더한다.
- 동작: 보존
- 실익: 추정 약 6행이 준다.
- 위험과 보호: `tests/test_delegation_storage.py`, `tests/test_redesign_GOVERNANCE.py`, `tests/test_review_engine.py`가 덮는다.
- 확신: 높음
- 다른 영역: 없음

#### RES-16: 외부 요청의 결속 검사가 같은 모듈에 두 번 있다
- 유형: 이음새중복
- 위치:
  - 요청 결속: `external.py:14-17`(`request_binding_current`, 호출자 `record_schemas/__init__.py:368-370`, `state_checks.py:395-396`), `external.py:77-78`(`validate_operation`이 같은 조건을 다시 적음)
  - 재시도 증거 결속: `external.py:102`, `external.py:159`
- 현상: 요청 해시와 멱등 키 결속, 재시도 증거와 요청의 결속이 각각 두 곳에 따로 적혀 있다.
- 제안: `validate_operation`이 `request_binding_current`를 부르게 한다. `_retry_evidence_bound(operation, evidence)`를 두고 `execute_operation`과 `prepare_retry`가 부른다. 전송 직전 재검사(`external.py:108`, `external.py:129`)는 권한 철회를 잡으므로 유지한다.
- 동작: 보존(오류 문구만 차이)
- 실익: 추정 약 4행이 준다.
- 위험과 보호: `tests/test_external.py`(`test_tampered_key_and_terminal_persist`, `test_unknown_retry_reconcile_and_scope`, `test_fresh_revocation_before_send_prevents_transport`)가 덮는다.
- 확신: 높음
- 다른 영역: `record_schemas`, `state_checks.py`

#### RES-17: 묶음 적용 한 번에 같은 파생 구조를 반복 계산한다
- 유형: 운영비용
- 위치:
  - `protocol_output`: `integration.py:340`, `integration.py:483`, `integration.py:440`
  - `member_values`: `integration.py:355`, `integration.py:441`, 묶음마다 `integration.py:506`
- 현상: `apply_bundles` 한 번이 `protocol_output`을 세 번, 모든 값을 deepcopy하는 `member_values`를 2+B번 계산한다(B는 응답을 소유하는 수락 묶음 수).
- 제안: `apply_bundles`에서 두 값을 한 번 계산해 `inspect_bundles`와 `split_bundles`에 넘기고, 506행은 미리 계산한 `members["output"]` 해시를 쓴다.
- 동작: 보존
- 실익: 추정 호출당 출력 deepcopy가 2+B회 준다. 출력이 크지 않으면 체감 차이는 작다.
- 위험과 보호: `tests/test_impact_bundle.py`, `tests/test_redesign_CONTRACTS.py`가 덮는다.
- 확신: 높음(반복 사실), 낮음(실익의 크기)
- 다른 영역: `submission.py`(미리보기 경로 `preview_bundles`)

## 3. 보존 판정

| 위치 | 겉보기 문제 | 유지 이유 |
|---|---|---|
| `questions.py`/`question_engine.py`, `revisions.py`/`revision_engine.py`, `academic.py`/`academic_engine.py` | 한 개념이 두 모듈로 나뉘어 있다 | 앞쪽은 상태만 받는 순수 함수로 8~10개 모듈이 import한다(`questions`: decision_engine, engine, governance, planning, reporting, review_cycle, revisions, revision_engine, submission). 뒤쪽은 `self`를 쓰는 엔진 믹스인으로 `engine.py`만 import한다(`engine.py:39`, `:52`, `:53`). 합치면 제출 검사·계획 모듈이 엔진 믹스인을 끌어오거나 순환 import가 생긴다. 한 가지 예외로, 순수 함수 `current_solution_basis`가 `academic_engine.py:9-48`에 있어 `state_checks.py:422`가 믹스인 모듈을 import한다. `academic.py`로 옮길 수 있지만 실익은 import 한 줄이다. |
| `knowledge.py`/`knowledge_io.py`/`knowledge_records.py` | 이름이 분할을 설명하지 못한다. `knowledge_io`에는 입출력이 없고 종류 정의·가져오기·관계를 담는다. `knowledge`↔`knowledge_records`는 지연 import 순환이다(`knowledge.py`에 10곳, `knowledge_records.py:162`, `:296`). | 실제 중복은 분할 경계가 아니라 판정 함수 안에 있다(RES-03, RES-12). 세 파일(합계 1632행)을 합쳐도 그 중복은 줄지 않는다. 이름을 바꾸면 engine·governance·planning·submission·record_schemas의 import가 바뀌지만 판정은 줄지 않는다. |
| `question_engine.py:77-80`(해소 적용 시 열림·소유자 재검사) | 제출 검사와 같은 조건이다 | 제출과 적용 사이에 다른 실행이 같은 질문을 닫을 수 있다. 공유 함수로 합치되(RES-05) 재검사는 유지한다. |
| `delegations.py:135-156`(`_checked`) | 기록 때 검사한 판정을 다시 검사한다 | 판정 기록은 디스크를 왕복한 뒤 쓰이고, 결정·원천의 철회를 이 시점에 봐야 한다. 공유 함수로 합치되(RES-15) 재검사는 유지한다. |
| `external.py:107-108`, `:128-129`(전송 직전 권한 재검사) | 같은 검사를 두 번 한다 | 자격 증명 확보 동안 권한이 철회될 수 있다(`tests/test_external.py` `test_fresh_revocation_before_send_prevents_transport`). |
| `knowledge_records.py:124-134`(`formal_usable`의 원문 해시·툴체인 재대조) | 봉인 때 이미 대조했다 | 디스크의 기존 기록은 신뢰 경계 밖이다(기준.md 검사 원칙). 비용이 문제가 되면 이음새 계약 4절대로 `lean_code` 문자열 키 캐시를 쓴다. |
| `planning.py:686`과 `planning.py:693`의 외부 대기 종류 집합 | 같은 개념의 목록이 둘이고 `assessment_input` 하나가 다르다 | 686행을 693행과 같게 만들면 `returned_work_requires_assessment`(691행)보다 `external_waits`가 먼저 반환되어 판정 순서가 바뀐다. 두 목록은 같은 규칙이 아니다. |
| `planning.py:396-407`(`_pointer`)와 `question_engine.py:8-11`(`_pointer`) | JSON Pointer 구현이 둘이다 | 앞쪽은 노출 필드 제한·`~0`/`~1` 해제·스칼라 제한을 둔 조건 평가 계약이다. 뒤쪽은 질문 원문 좌표를 읽는 무제한 탐색이다. 계약이 다르다. |
| `integration.py:35-38`(`REFERENCE_KEYS`) | 참조 키 목록이 또 하나 있다 | 같은 응답 안의 새 제목·`task_title`·`target_ids` 폐포를 다루는 별개 개념이다(RES-09에서 제외). |
| `planning.py:531-659`(`task_ready`) | 계획·수신·착수 전 판정이 한 함수에 몰려 있다 | 이미 하나의 정본 술어이며(`planning.py:533`), `revision_engine.py:70`의 착수 직전 검사도 이를 재사용한다. 착수 조건의 중복 구현은 찾지 못했다. |

## 4. 후보 없음

- `scholarly.py`: 설정 해석 구현이 하나뿐이고 다른 모듈과 겹치는 규칙이 없다.
- `formal_preview.py`: `verify_lean`을 감싸는 얇은 진입점이며 자체 규칙이 없다.
- `activities.py`: RES-14의 `requeue_recovered_execution` 외에는 활동 상태 전이의 유일한 소유자다. 살아 있는 실행을 거르는 식이 모듈 안에 세 번 있지만(`activities.py:170`, `:236`, `:270`) 한 모듈 안의 한 줄 식이라 실익이 없다.
- `formal.py`의 신뢰 환경 밖 흐름(`verify_lean`, `_parse_evidence`, `_job_run`): RES-04 외의 이음새 중복이 없다.
- 대조 문서 6종과 코드 사이: 코드 상수·기본값·한도를 문서가 따로 적은 곳은 찾지 못했다. 문서가 서술한 규칙(재생성 시각, 관계 제출 필드, 개정 처분)은 코드와 일치했다.

## 5. 미완료

없음. 후보 안에서 확인하지 못한 사실은 각 후보에 미확인으로 적었다(RES-05의 기존 저장 상태, RES-09의 설계 의도, RES-14의 엔진 복구 경로).

## 6. 작업 중 사건

- 기록 색인 구현이 할당 모듈 밖에도 있었다. `engine.py:453`의 조회용 `_records`와 `governance.py:708-718`의 확장, `state_checks.py:236-249`의 중복 검사를 이음새를 따라 찾아 RES-01에 넣었다.
- `sync_activity_wait`와 `requeue_recovered_execution`은 테스트가 설계 요구로 단언하는데 생산 호출자가 없었다. 그래서 단순 삭제 후보가 아니라 결정 대상으로 분류했다(RES-14).
- 영향 폐포와 읽기 폐포의 차이는 코드 읽기만으로는 의도 여부를 판단할 수 없었다. 파이썬 한 줄 실행으로 차이를 확인했다(RES-09).
- `planning._records` 비용은 합성 상태로 한 번 측정했다(RES-02). 실제 인스턴스 상태로는 측정하지 않았다.
