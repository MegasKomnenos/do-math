# REV — 제출·검토·계약 영역 정리 검토

검토 기준 시점은 main `9b434f4`의 작업 트리다. 경로는 따로 적지 않으면 `C:/math/.claude/skills/do-math/` 기준 상대 경로다.

## 1. 읽은 범위

전문을 읽은 파일:

- `C:/math/임시/do-math-정리-검토-2026-09-27/기준.md` (238행)
- `AGENTS.md` (11행)
- `C:/math/docs/do-math/검사-경량화-이음새-계약.md` (245행)
- 영역 파일(`scripts/do_math/`): `submission.py` (1710행), `contracts.py` (360행), `task_contracts.py` (321행), `task_scope.py` (488행), `review_cycle.py` (1270행), `review_engine.py` (1249행), `review_policy.py` (120행), `decision_engine.py` (209행), `operational_dispositions.py` (86행), `integration.py` (550행)
- 과거 경량화 자료: `C:/math/임시/경량화-조사-2026-09-26/REV.md` (404행), `결과-C.md` (163행), `결과-이음새.md` (283행)
- 세 커밋이 영역 파일에 준 변경:
  - `git show 9b434f4`: `review_cycle.py`, `review_engine.py`의 변경 전문
  - `git show 379a171`: 영역 파일 10개의 +/- 행 전부
  - `git show 8d2ffd0`: 영역 파일 8개의 +/- 행 전부

일부만 읽은 파일(이음새 판정에 필요한 범위):

- `scripts/do_math/repository.py`: 30-99, 133-180, 232-246, 480-589
- `scripts/do_math/engine.py`: 96-112, 206-218, 238-246, 1060-1065, 2110-2170. `read_artifact` 어댑터와 `_issued_input` 호출부는 grep으로 확인했다.
- `scripts/do_math/record_schemas/schemas.py`: 12, 21-62, 150-189, 320-346(grep), 500-522, 612-631
- `scripts/do_math/record_schemas/__init__.py`: 140-189
- `scripts/do_math/governance.py`: 1048-1062
- `scripts/do_math/governance_engine.py`: 141-146
- `scripts/do_math/knowledge.py`: 85-96
- `scripts/do_math/execution_profiles.py`: 56-62, 264-290
- `scripts/do_math/observations.py`: 181-193
- `scripts/do_math/lifecycle_engine.py`: 905-925
- `scripts/do_math/planning.py`: 280-286, 390-415, 622-635, 676-688
- `scripts/do_math/input_basis.py`: 30-40
- `scripts/tests/research_fixtures.py`: 775-804
- `계약/동일성-검토.md`: 11-20. `계약/후보-준비.md`는 grep으로만 확인했다.
- `C:/math/기억/layer1/M-0349.md` 51-64, `M-0350.md` 45-56. 두 파일은 영역 관련 낱말로 grep한 뒤 해당 행을 읽었다.

파견문이 정했는데 읽지 못한 파일은 없다. 4.1·4.2절의 종류는 모두 검토했다.

## 2. 영역 판정

2라운드가 생산자와 수신자가 공유하는 검사 함수를 `review_cycle`·`submission`·`task_contracts`·`task_scope`에 모았으므로, 이 영역에서 방향성 1·2(이음새 정의 하나, 양쪽 실행)는 대부분 실현되어 있다. 다만 같은 방향이 끝까지 적용되지 않은 자리가 남았다. scope 단계의 생산자 검사가 수신 조건 일부를 빠뜨리고(REV-01), 조사 요청의 `request_digest` 한 필드가 두 규칙으로 정의되며(REV-02), 실행 계보 순회가 세 벌이다(REV-05). 가장 큰 정리 여지의 첫째는 검토 엔진의 수락·준비 경로를 한 번의 확인으로 줄이는 것이다. 여기에는 시험 주입 전용 경로(REV-03)와, 한 호출 안에서 같은 현재성·독립성 확인을 두세 번 되풀이하는 코드(REV-04)를 걷는 일이 포함된다. 둘째는 스키마 빌더가 모듈 전역 노드를 공유하는 방식을 한 규칙으로 정해, 9b434f4가 고친 결함과 같은 형태가 프로세스 전역 규모로 다시 생길 여지를 없애는 것이다(REV-23).

검토했고 없음: 잔재, 비대, 낡음

## 3. 후보

### 검토 1

#### REV-01 scope 단계의 생산자 검사가 수신 조건(`scope_complete`·`questions`)을 실행하지 않는다
- 검토: 1
- 종류: 불일관
- 좌표: `scripts/do_math/submission.py:816-819`, `scripts/do_math/submission.py:1002-1005`, `scripts/do_math/review_cycle.py:858-878`, `scripts/do_math/review_cycle.py:887-901`, `계약/동일성-검토.md:11-17`
- 현상: 생산자 검사와 중앙 봉인은 같은 `_payload_issues`를 실행한다. 그런데 identity_review의 scope 단계만 `validate_visible_output`에서 빠져 있다(1002행의 조건 `action.get("stage") != "scope"`). 이 단계에서는 `validate_scope_assessment` 하나만 부른다(816-819행). 수신 쪽 `accept_result` → `_validate_content`는 scope 결과에 대해 두 조건을 더 요구한다. `scope_complete`가 참이어야 하고 `questions`가 비어 있어야 한다(`review_cycle.py:873-874`). 스키마(`stage_schema('scope')`)는 `scope_complete: boolean`, `questions: array`만 요구하므로 이 조건을 표현하지 않는다. 그래서 `scope_complete=false`이거나 질문이 남은 scope 결과는 생산자 검사와 봉인을 통과한다. 그 뒤 적용 단계에서 ValueError로 반려되고, 미리보기에서는 일반 문구 뒤에 가려진다(`submission.py:1250-1258`). 두 조건은 역할 문서 `계약/동일성-검토.md`의 scope 절(11-17행)에도 적혀 있지 않다.
- 근거: `_validate_content`에 필요한 입력(`proposal_digest`, `review_policy`, `scope_executions_used`)은 `context_for`가 이미 문맥에 넣는다(`review_cycle.py:1250-1255`). `retained_reviewer_slots`는 문맥에 없으므로 그 조건은 `cycle.get(...)`이 거짓이 되어 건너뛰고, 수신에만 남는다(875행). 검색식 `validate_visible_output\(|validate_scope_assessment\(`(`scripts/do_math`)의 일치는 6건이다. 관련은 5건이다(submission 818·1004, review_cycle 124·871, 정의 1). 생산자 쪽 scope 경로는 818행 하나뿐이다.
- 제안: `submission._payload_issues`의 scope 특례(816-819행)를 지운다. 1002행 조건에서 `stage != "scope"`를 빼서 scope도 `review_cycle.validate_visible_output`을 지나게 한다. 이 경로는 `_validate_content`를 거쳐 `validate_scope_assessment`까지 실행한다. 문서 scope 절에는 "`scope_complete`는 참, `questions`는 빈 배열"을 한 문장으로 적는다. 문서 수정은 DOC 영역 몫이다.
- 실익: 적용 단계 반려 경로 하나가 생산자 검사로 앞당겨진다. 생산자·수신 검사의 분기가 하나 사라진다(4행 삭제). scope 단계도 다른 단계와 같은 공유 함수를 쓰게 된다. 이것은 방향성 2의 한 정의·양쪽 실행과 같은 방향이다.
- 비용과 위험: `submission.py` 한 곳과 문서 한 문장만 바뀐다. 새 상태·수명·복구 규칙은 없다. 조사 요청을 함께 낸 scope 결과는 `requesting_research=True`이므로 `validate_provisional`만 실행된다. 이것은 수신의 `defer_for_research`와 같다.
- 기능·커버리지 영향: 있음. 전에는 생산자 검사를 통과하던, 완료되지 않은 scope 결과가 `submission.output` 규칙으로 반려된다. scope 산출을 손으로 만드는 시험 가운데 `scope_complete=false`를 쓰는 것이 있으면 기대가 바뀐다.
- 사용자 결정 관련: 없음
- 확신도: 확인

#### REV-02 조사 요청의 `request_digest` 한 필드가 두 규칙으로 정의되고, 앞 규칙은 운전 경로에서 곧바로 덮어써진다
- 검토: 1
- 종류: 이음새
- 좌표: `scripts/do_math/review_cycle.py:719-727`, `scripts/do_math/review_cycle.py:303-320`, `scripts/do_math/review_cycle.py:619-623`, `scripts/do_math/review_engine.py:1094-1095`, `scripts/do_math/review_engine.py:1114-1119`
- 현상: `defer_for_research`는 조사 기록을 만들면서 `request_digest`를 `json_digest({question, source_refs, proposal_digest})`로 채운다(724행). 호출자 `_defer_review_for_research`는 반환 직후 같은 기록의 `request_digest`를 `research_request_digest(question, proposal_digest, source_records)`로 덮어쓴다(1119행). 이 규칙은 `exact_content_hash`로 계산하고 대상 모양도 다르다. 봉인 재구성(303-320행)은 `source_records`가 있으면 둘째 규칙으로, 없으면 첫째 규칙으로 대조한다.
- 근거: 요청 스키마는 `source_refs`에 `minItems: 1`을 둔다(`review_cycle.py:639`). `validate_research_requests`가 이를 강제한다(644행). 그리고 `_defer_review_for_research`는 참조마다 spec 하나를 만든다(1094행). 따라서 운전 경로의 모든 조사 기록은 `source_records`를 가진다. 첫째 규칙의 값은 게시되지 않으며, 재구성의 `elif` 분기(319-320행)는 엔진을 거치지 않는 순수 함수 호출에서만 닿는다. 이음새 계약 2.1은 상태 저장 값의 식별을 `exact_content_hash`로 정했다. 검색식 `request_digest`(`scripts/do_math`)의 일치는 13건이다. 그중 생산 규칙은 2건(724, 1119행), 대조는 3건(305, 319, 740행)이다.
- 제안: `defer_for_research`가 요청별 `source_records`를 인자로 받게 한다. 그리고 `research_request_digest` 하나로 `request_digest`를 한 번만 계산한다. `_defer_review_for_research`는 이미 만든 spec을 넘기고 덮어쓰기 5행(1114-1119행)을 지운다. 재구성은 기록의 `source_records`를 그대로 넘기고, 둘째 대조 분기(319-320행)와 `generated.update(...)`를 지운다.
- 실익: 한 필드의 두 정의가 하나로 준다. 약 10행이 지워지고, 호출 뒤 기록을 제자리에서 고치는 순서 의존이 사라진다. 첫째 규칙으로만 만든 기록이 두 번째 규칙으로 대조될 여지도 없어진다.
- 비용과 위험: `review_cycle.py`, `review_engine.py`가 바뀐다. 새 상태는 없다. `defer_for_research`를 source 없이 직접 부르는 시험(`tests/test_review_research.py`, `tests/test_redesign_REVIEWS.py`에 호출이 있음)은 spec을 넘기도록 고쳐야 한다.
- 기능·커버리지 영향: 없음. 운전 경로의 저장 값은 같다.
- 사용자 결정 관련: 없음
- 확신도: 확인

#### REV-03 `_start_identity_review`가 저장될 수 없는 지식 필드와 설정 키를 읽는다(시험 주입 전용 경로)
- 검토: 1
- 종류: 미사용
- 좌표: `scripts/do_math/review_engine.py:447`, `scripts/do_math/review_engine.py:453-462`, `scripts/do_math/review_engine.py:262-266`, `scripts/do_math/review_cycle.py:124-127`, `scripts/do_math/review_cycle.py:158`, `scripts/do_math/record_schemas/schemas.py:170-182`, `scripts/do_math/engine.py:210-211`
- 현상: 새 검토를 열 때 엔진이 읽는 값 가운데 저장될 수 없는 것이 넷 있다.
  - `scope_assessment=item.get('scope_assessment', config.get('review_scope_assessment'))`(456행)
  - `owner_activity_id=item.get('owner_activity_id')`(457행)
  - `item.get('producer_execution_ids', [])`(461행)
  - 단계적 검토의 `...get('producer_execution_ids', [])`(263행)

  저장 지식 스키마 `RECORDS["knowledge"]`는 닫혀 있고, 이 세 필드가 없다(`schemas.py:170-182`, `COMMON`은 61-62행). 설정 절도 닫혀 있다. `validate_config`는 `config_schema()`에 없는 키를 거부하는데(`engine.py:210-211`), 그 표에 `review_scope_assessment`가 없다(`record_schemas/__init__.py:167-181`). 따라서 운전 중에는 네 값이 늘 없고, 모든 검토가 scope 단계로 시작한다. 미리 주어진 평가로 scope 단계를 건너뛰는 `start_review`의 분기(124-127·158행)에는 시험이 설정에 주입한 값으로만 닿는다.
- 근거: 검색식 `review_scope_assessment`(스킬 전체)의 일치는 17건이다. 제품 코드는 `review_engine.py:456` 1건이고, 나머지 16건은 시험이다(`tests/test_review_engine.py` 10, `tests/test_redesign_REVIEWS.py` 4, `tests/test_review_research.py` 1 등). 검색식 `producer_execution_ids`(`scripts/do_math`)의 일치는 18건이다. 지식 레코드에 이 필드를 쓰는 생산자는 없다. `knowledge.py:91`은 필드 이름 목록일 뿐이다. 검색식 `scope_assessment`에서 지식 레코드에 값을 쓰는 곳은 0건이다.
- 제안: 456-457행과 461행의 지식·설정 읽기를 지운다. 263행의 `producer_execution_ids` 읽기도 지운다. 이로써 엔진은 항상 scope 단계부터 시작한다. 시험이 싼 시작 상태로 scope 뒤의 검토가 필요하면 제품 설정에 주입하지 않는다. 대신 순수 API(`start_review(..., scope_assessment=...)` 또는 scope 결과의 `accept_result`)로 주기를 구성한다. 그러면 `start_review`의 `scope_assessment` 인자는 순수 API로 남는다.
- 실익: 운전에서 닿지 않는 읽기 4곳이 지워진다. 제품이 시험을 위해 닫힌 설정 밖의 키를 읽는 예외가 사라진다(방향성 4). "지식에 평가를 붙이면 scope를 건너뛴다"는 잘못된 인상도 사라진다.
- 비용과 위험: 제품 쪽은 `review_engine.py` 두 곳만 바뀐다. 시험 쪽에서는 설정에 `review_scope_assessment`를 넣는 시험 3개 모듈의 시작 상태를 고쳐야 한다. 대부분 `config.pop('review_scope_assessment')`로 scope 경로를 여는 시험이므로 영향 폭은 grep 결과 16곳이다.
- 기능·커버리지 영향: 있음. 제품 동작은 같지만, 설정 주입으로 scope 뒤 단계를 직접 시작하던 시험의 시작 상태 구성이 바뀐다.
- 사용자 결정 관련: 없음
- 확신도: 확인(저장 스키마와 설정 스키마가 닫혀 있음, 제품 생산자 0건)

#### REV-04 검토 엔진이 한 수락·준비 호출 안에서 같은 현재성·독립성 확인을 두세 번 되풀이한다
- 검토: 1
- 종류: 비용
- 좌표: `scripts/do_math/review_engine.py:957-981`, `scripts/do_math/review_engine.py:828-837`, `scripts/do_math/review_engine.py:288-299`, `scripts/do_math/review_engine.py:1083-1096`, `scripts/do_math/review_engine.py:587-610`, `scripts/do_math/review_engine.py:650-700`, `scripts/do_math/review_engine.py:547-577`
- 현상: 반복은 세 호출 사슬에서 일어난다.
  - `_accept_identity_review`: `_review_cycle`(961행), `validate_review_independence`(971행), `review_input_basis_changes`(972행)을 차례로 실행한다. 이어서 `_record_review_input`(978행)을 부르는데, 이것이 다시 `_review_cycle`(830행)과 `_admit_review_execution`(835행)을 부른다. `_admit_review_execution`은 다시 `_review_cycle`(296행), `validate_review_independence`(298행), `review_input_basis_changes`(299행)을 실행한다. 여기서는 기존 입장 기록을 확인하기(309-312행) 전에 이 셋을 모두 계산한다. 재심사면 `validate_review_execution`(980행)이 독립성을 세 번째로 검사한다(`review_cycle.py:212`).
  - `_defer_review_for_research`: 1093행과 1096행→298행에서 같은 검사가 되풀이된다.
  - 문맥 준비: `_prepare_review_context`(594행), `_build_review_context`(651행), `_review_schema`(700행→580행)이 `_review_cycle`을 세 번 실행한다.

  `_review_cycle`은 호출될 때마다 `_proposal`(지식 투영과 깊은 복사)과 `_review_publication_premises`(`identity_basis`, 신뢰 환경·거버넌스 깊은 복사, 정책 검증)를 다시 계산해 비교한다(572-576행).
- 근거: 위 행을 직접 따라갔다. 한 사슬 안에서 인스턴스와 runtime은 바뀌지 않는다. `_record_review_input`이 바꾸는 것은 검토 주기의 전사와 바인딩뿐이다. 따라서 되풀이된 계산은 같은 입력에서 같은 결과를 낸다(방향성 6의 "같은 사실의 반복 확인"). 비용은 측정하지 않았다.
- 제안: 수락·보류 경로의 현재성·독립성 확인을 한 곳에 둔다. 예를 들면 `_admit_review_execution`이 이미 입장한 실행을 만나면 검사 전에 `already_admitted`를 돌려주게 한다. 그리고 수락 경로는 971-974행의 한 번만 검사한다. 준비 경로에서는 `_build_review_context`가 받은 cycle로 스키마를 만든다. 즉 `_review_schema`를 cycle 인자형으로 바꾸거나 `stage_schema`에 digest enum을 직접 붙인다. 재심사의 `validate_review_execution` 호출은 결과 바인딩 확인이 목적이다. 그러니 독립성 재검사를 빼는 선택 인자를 두기보다, 수락 직전 검사 한 번과 역할이 겹치는지 먼저 판정한다.
- 실익: 검토 결과 한 건을 수락할 때 `_review_cycle` 계산이 2회, 계보 순회가 1~2회, 입력 기반 비교가 1회 준다. 문맥 준비에서는 `_review_cycle`이 1~2회 준다. 검토 역할은 한 제안에 수십 번 실행되므로 누적된다(추정).
- 비용과 위험: `review_engine.py`만 바뀐다. 새 상태는 없다. 오류 검사 순서가 바뀌므로 오류 문구를 단언하는 시험이 영향을 받을 수 있다. 입장 뒤에 실행 계보가 바뀌는 경로가 있으면 수락 시점 재검사가 필요하다. 그 경우에도 한 번이면 된다.
- 기능·커버리지 영향: 없음(같은 판정을 한 번만 한다)
- 사용자 결정 관련: 없음
- 확신도: 추정. 반복 자체는 원문으로 확인했다. 비용의 크기와 "입장 뒤 계보 불변"은 실행 레코드의 `continuation_of`·`context_origin`이 입장 뒤에 바뀌는 경로가 없는지를 grep으로 확인하면 확정된다.

#### REV-05 실행 계보(`continuation_of`·`context_origin`) 순회가 세 벌로 구현되어 있다
- 검토: 1
- 종류: 이음새
- 좌표: `scripts/do_math/review_cycle.py:180-207`, `scripts/do_math/review_engine.py:87-109`, `scripts/do_math/governance.py:1048-1061`
- 현상: 같은 순회가 세 곳에 따로 있다.
  - `validate_review_independence`: 두 필드를 추이적으로 따라가며, 없는 행이면 거부한다(190-207행).
  - `_qualified_assessment_defect`: 같은 순회를 다시 적었다. 없는 행이면 `None`을 돌려주고, 작성자 집합에서 `previous_reviews`를 뺀다(94-109행).
  - `governance.validate_independent_execution`: `continuation_of` 하나만 따라간다(1052-1057행).

  `validate_review_independence`는 먼저 governance 함수를 부르고(189행) 같은 사슬을 한 번 더 걷는다. 두 경로 모두 "문자열이면 목록으로" 정규화를 두 필드에 똑같이 적용한다. 그런데 저장 스키마에서 `continuation_of`는 ID 하나이고 `context_origin`은 목록이다(`record_schemas/schemas.py:264`).
- 근거: 검색식 `\('continuation_of', 'context_origin'\)`(`scripts/do_math`)의 일치는 2건이고 둘 다 관련이 있다. governance 순회는 1052-1057행을 읽었다. 작성자 집합의 정본 `review_authors`(`review_cycle.py:172-177`)를 `_qualified_assessment_defect`는 쓰지 않는다(94행).
- 제안: 계보 조상을 차례로 내는 순수 함수 하나를 소유 모듈(`governance`, 독립성 정본)에 둔다. 예를 들면 `execution_ancestors(runtime, execution_id, *, missing)`이다. `validate_review_independence`와 `_qualified_assessment_defect`는 이 함수로 조상을 받는다. 없는 행을 거부할지 멈출지는 인자로 가른다. `_qualified_assessment_defect`의 작성자 집합은 `review_authors`로 바꿀지 판단한다. 이것은 재심사 판단 대상이 원 검토의 이전 판본 작성자까지 포함해야 하는가의 문제이므로 사용자 판단이 필요할 수 있다.
- 실익: 순회 구현 두 벌(약 15행)이 하나로 준다. 계보 필드의 형식이 바뀌어도 한 곳만 고치면 된다. `validate_review_independence` 안에서 `continuation_of` 사슬을 두 번 걷는 일도 사라진다.
- 비용과 위험: `review_cycle.py`, `review_engine.py`, `governance.py`(OPS 영역)가 바뀐다. governance 함수는 import 승인 등 다른 소비자도 쓴다(1073행). 그래서 `context_origin`까지 따라가게 바꾸면 그쪽 판정이 엄격해진다. 순회만 공유하고 각 소비자의 판정은 그대로 두어야 한다.
- 기능·커버리지 영향: 없음(판정 보존 시)
- 사용자 결정 관련: 없음
- 확신도: 추정. 중복은 확인했다. `_qualified_assessment_defect`가 `previous_reviews` 작성자를 뺀 것이 의도인지는 재심사 설계 문서나 L-0020에서 확인하면 확정된다.

#### REV-06 `read_artifact` 콜백의 인자 순서가 두 관례로 갈려, 엔진이 순서를 뒤집는 람다를 9번 적는다
- 검토: 1
- 종류: 불일관
- 좌표: `scripts/do_math/submission.py:62`, `scripts/do_math/submission.py:126`, `scripts/do_math/submission.py:1404`, `scripts/do_math/integration.py:191-194`, `scripts/do_math/review_cycle.py:316`, `scripts/do_math/review_cycle.py:593`, `engine.py`(9곳: 1174, 1183, 1372, 1614, 1865, 2171, 2229, 2367, 4482)
- 현상: 콜백 인자 순서가 모듈마다 다르다.
  - `submission`(`read_sealed_submission`, `issued_input`, `summarize_snapshot_checks`)과 이를 넘겨받는 `integration`은 `read_artifact(snapshot, path)`를 부른다.
  - `review_cycle`(`validate_sealed_review`, `validate_resource_disposition`)과 `retention`은 `read_artifact(path, snapshot)`을 부른다. 이것은 `ResearchRepository.read(path, snapshot)`와 같은 순서다.

  그래서 엔진은 submission 계열에 넘길 때마다 `lambda snapshot, path: self.store.read(path, snapshot)`을 적는다. 두 인자가 모두 문자열이라 순서를 바꿔 넘겨도 형 오류가 나지 않는다.
- 근거: 검색식 `lambda snapshot, path: self.store.read\(path, snapshot\)|lambda selected,path: self.store.read\(path,selected\)`(`scripts/do_math`)의 일치는 9건이고 모두 관련이 있다. 검색식 `read_artifact\(`의 호출부는 submission 3건(snapshot 먼저), review_cycle 2건과 retention 2건(path 먼저), context_store 4건(snapshot을 묶은 한 인자)이다.
- 제안: submission과 integration의 `read_artifact`를 저장소와 같은 `(path, snapshot)` 순서로 바꾼다. 엔진은 `self.store.read`를 그대로 넘긴다.
- 실익: 엔진의 어댑터 람다 9개가 지워진다. 콜백 관례가 하나가 되어, 인자를 뒤바꿔 넘길 여지가 사라진다.
- 비용과 위험: `submission.py`(3곳), `integration.py`(전달부), `engine.py`(9곳, ENG 영역)와 이 함수들을 직접 부르는 시험이 바뀐다(예: `tests/test_submission_flow.py:97-99`). 새 상태는 없다.
- 기능·커버리지 영향: 없음
- 사용자 결정 관련: 없음
- 확신도: 확인

#### REV-07 `_prepare_review_context`의 오류 문구 표지 분기에 닿는 예외가 없다
- 검토: 1
- 종류: 미사용
- 좌표: `scripts/do_math/review_engine.py:609-620`
- 현상: `_build_review_context`가 ValueError를 내면 코드가 오류 문구에 표지 여섯 개가 들어 있는지 본다. 표지는 `'transcript restoration'`, `'transcript bytes'`, `'sealed transcript'`, `'review source bytes'`, `'review source hash'`, `'immutable review source'`다. 들어 있으면 복구 사건으로 기록한다(614-620행). 그런데 이 문구를 내는 예외는 모두 `ReviewRestorationError`다. 이 예외는 바로 위의 `except ReviewRestorationError`(611행)가 먼저 잡는다.
- 근거: 검색식 `transcript restoration|transcript bytes|sealed transcript|review source bytes|review source hash|immutable review source`(`scripts` 전체, 시험 포함)의 일치는 9건이다. 616-617행의 표지 목록을 빼면 7건이 남는데, 모두 `ReviewRestorationError(...)` 생성이다(`review_engine.py:679, 683, 690`, `review_cycle.py:1209, 1211, 1216, 1219`). 표지를 담은 일반 ValueError를 내는 곳은 0건이다.
- 제안: 614-620행을 지운다. 표지가 없는 ValueError는 지금처럼 다시 던져진다.
- 실익: 7행이 지워진다. 오류 문구로 실패를 분류하는 코드가 사라진다. 이것은 `submission._issue`의 원칙 "No failure identity depends on human error wording"(411-413행)과 같은 방향이다.
- 비용과 위험: 없음. 새 상태도 없다.
- 기능·커버리지 영향: 없음
- 사용자 결정 관련: 없음
- 확신도: 확인

#### REV-08 `_build_review_context`가 `context_for`가 방금 검증한 전사 바이트를 다시 해시한다
- 검토: 1
- 종류: 비용
- 좌표: `scripts/do_math/review_engine.py:663`, `scripts/do_math/review_engine.py:673-685`, `scripts/do_math/review_cycle.py:1225-1238`, `scripts/do_math/review_cycle.py:1204-1222`
- 현상: `context_for`는 `validate_transcript(cycle, slot)`으로 같은 자리의 모든 메시지를 manifest 행과 대조한다. 대조 항목은 길이 일치, 위치, 압축 JSON의 SHA-256·바이트 수다. 그다음 `source_refs`를 그 manifest 행의 사본으로 만든다(1235행). `_build_review_context`는 그 참조마다 같은 `cycle['turns'][slot][index]`를 다시 꺼낸다(677행). 그리고 `compact_json_bytes`로 직렬화해 SHA-256과 길이를 다시 비교한다(681-685행). 두 호출 사이에 cycle은 바뀌지 않는다(664-666행은 문맥 사본만 고친다).
- 근거: 참조는 `slot = action['slot']`의 메시지에서만 만들어진다(1230-1238행). 그래서 `KeyError`·`IndexError` 분기(678-680행)와 해시 불일치 분기(682-685행)에는 도달하지 않는다.
- 제안: 676-685행을 `raw = compact_json_bytes(cycle['turns'][slot][index])` 한 줄로 줄인다. 직렬화는 파일 쓰기에 필요하다.
- 실익: 약 9행이 지워지고, 문맥 준비 한 번마다 참조 수만큼 해시 계산이 준다. 방향성 6의 반복 확인 제거다.
- 비용과 위험: `review_engine.py` 한 곳이 바뀐다. 이 두 분기가 내던 복구 원인(`missing_record`, `content_mismatch`)은 `validate_transcript`가 같은 원인으로 이미 낸다.
- 기능·커버리지 영향: 없음
- 사용자 결정 관련: 없음
- 확신도: 확인

#### REV-09 검토 주기가 읽는 곳 없는 파생 필드 셋을 저장한다
- 검토: 1
- 종류: 파생상태
- 좌표: `scripts/do_math/review_cycle.py:150-152`, `scripts/do_math/review_cycle.py:157`, `scripts/do_math/review_cycle.py:1006`, `scripts/do_math/review_engine.py:324`, `scripts/do_math/review_engine.py:1101`, `scripts/do_math/record_schemas/schemas.py:509`
- 현상: 검토 주기 레코드에는 읽는 곳 없는 필드가 셋 있다.
  - `reviewers`: `reviewer_slots`의 길이다. scope 수락 때 다시 맞춘다(1006행).
  - `judges`: 상수 3이다.
  - `execution_accounting.reserved_execution_slots`: 입장과 조사 보류 때 매번 계산해 넣는다(324, 1101행).

  저장 스키마도 앞의 둘을 `NAT`로 둔다(`schemas.py:509`). 판정·재구성·문맥은 `reviewer_slots`, `judge_slots`, 호출 시점에 계산한 `reserved_review_slots(...)`를 쓴다.
- 근거: 검색식 `\['reviewers'\]|\["reviewers"\]|\['judges'\]|\["judges"\]|get\('reviewers'|reserved_execution_slots`(`scripts/do_math`, `scripts/tests`)의 일치는 12건이다. 관련은 9건이다(나머지 3건은 설정의 `reviewers`다). 주기의 `reviewers`·`judges`를 읽는 곳은 0건이다. `reserved_execution_slots`를 읽는 곳은 자원 처분 `detail`의 값(`review_cycle.py:585`)과 시험의 입장 결과(`tests/test_review_engine.py:209`)뿐이다. 둘 다 주기 레코드가 아니라 입장 결과 `outcome`의 필드다. 재구성 대조 목록(`review_cycle.py:366-369`)과 입력 기반(`input_basis.py:36-37`)에도 이 필드들은 없다.
- 제안: `start_review`의 `reviewers`, `judges`, `execution_accounting.reserved_execution_slots`와 1006·324·1101행의 대입을 지운다. 저장 스키마의 두 `NAT` 항목도 지운다(STO 영역 파일).
- 실익: 동기화가 필요한 파생 저장값 셋과 대입 4곳이 사라진다. 상태 크기도 조금 준다.
- 비용과 위험: `review_cycle.py`, `review_engine.py`, `record_schemas/schemas.py`가 바뀐다. 저장 계약 manifest의 digest도 바뀐다. 결정 1에 따라 호환 계층은 두지 않는다.
- 기능·커버리지 영향: 없음
- 사용자 결정 관련: 없음
- 확신도: 확인

#### REV-10 완료 판정의 근거 계산이 과제마다 전체 기록 색인을 다시 만든다
- 검토: 1
- 종류: 비용
- 좌표: `scripts/do_math/task_scope.py:212-215`, `scripts/do_math/task_scope.py:292-300`, `scripts/do_math/task_scope.py:322-339`, `scripts/do_math/task_scope.py:397`, `scripts/do_math/task_scope.py:469`, `scripts/do_math/lifecycle_engine.py:916-919`
- 현상: `assessment_basis`는 부를 때마다 `record_index(instance, runtime)`로 모든 기록 가족의 색인을 새로 만든다(215행). 부르는 곳은 다음과 같다.
  - `refresh_task_assessments`: 판정이 있는 과제마다 `assessment_current`(296행)를 부른다. 판정이 낡았으면 같은 과제에 대해 `assessment_basis`를 한 번 더 부른다(333행).
  - `apply_task_assessments`: 397행에서 이미 색인을 만들고도, 과제마다 469행에서 다시 만든다.

  `assessment_current`는 과제마다 `validate_item_dispositions` → `validate_task_contract`로 과제 레코드 전체의 jsonschema 검사도 실행한다(298-302행). `refresh_task_assessments`는 소유 루프의 상태 정리에서 호출된다(`lifecycle_engine.py:916-919`).
- 근거: 원문을 따라가 확인했다. `planning.task_ready`도 의존 과제마다 `assessment_current`를 부른다(`planning.py:630`, `:683`, RES 영역). 호출 빈도와 소요 시간은 측정하지 않았다.
- 제안: `assessment_basis`가 색인을 인자로 받게 한다. `refresh_task_assessments`와 `apply_task_assessments`는 호출 한 번에 색인 하나를 만들어 넘긴다. `assessment_current`의 형태 검사는 저장 관문이 이미 하는 검사(`record_schemas/__init__.py:343`)와 겹친다. 그러니 현재성 판정에 필요한 부분(계약·결과 해시, 근거, 권한)만 남길지를 함께 판단한다.
- 실익: 과제 T개, 기록 R개일 때 갱신 한 번의 색인 구성 비용이 O(T·R)에서 O(R)로 준다. 과제당 jsonschema 검사도 줄일 수 있다.
- 비용과 위험: `task_scope.py`만 바뀐다(`planning`의 호출부는 선택). 새 상태는 없다. 메모리 상태를 읽는 계산이므로 head 키 메모이즈는 쓰지 않는다(이음새 계약 4절). 호출 안에서 색인을 한 번 만드는 것으로 충분하다.
- 기능·커버리지 영향: 없음
- 사용자 결정 관련: 없음
- 확신도: 추정. 구조는 확인했다. 비용의 크기는 소유 루프 한 회차의 `refresh_task_assessments` 소요를 과제 수별로 재면 확정된다.

#### REV-11 scope 평가의 형태가 wire 스키마와 `validate_scope_assessment`의 수기 검사에 두 번 적혀 있다
- 검토: 1
- 종류: 이음새
- 좌표: `scripts/do_math/review_cycle.py:57-65`, `scripts/do_math/review_policy.py:69-120`
- 현상: 2라운드(REV-07)가 scope 평가의 정밀 스키마를 `stage_schema('scope')`로 옮겼다. 하지만 `validate_scope_assessment`는 같은 형태를 손으로 다시 검사한다. 대상은 필드 집합, 문자열·목록 형, 자리 필드 집합, 프로필 참조, 정수 한도다(74-109행). 두 정의는 이미 조금 다르다. 스키마는 비지 않은 텍스트(`\S`)를 요구하는데, 수기 검사는 `not value`만 거부해 공백 문자열을 받는다(92행, `_strings` 17행).
- 근거: 운전 중의 호출자는 둘이다. 하나는 스키마 검사 뒤에 부르는 `_validate_content`(`review_cycle.py:860→871`)와 생산자 검사(`submission.py:818`, 스키마 이슈가 있으면 644-645행에서 먼저 반환)다. 다른 하나는 `start_review`(124행)로, REV-03의 시험 주입 경로와 저장된 정규화 값의 재구성에서만 불린다. 검색식 `validate_scope_assessment\(`의 일치는 4건(정의 제외)이다.
- 제안: scope 평가의 스키마를 계약 소유 모듈 `review_policy`에 하나 두고, `stage_schema`가 가져다 쓴다(`review_policy`는 `review_cycle`을 import하지 않으므로 순환이 없다). `validate_scope_assessment`는 그 스키마로 형태를 한 번 보고 의미 조건만 남긴다. 의미 조건은 정책 일치, 관점 포괄, 최소 자리 수, 독립 자리 ID 충돌, 한도의 상·하한, 넘침 처분 일치다.
- 실익: 형태 정의 두 벌이 하나로 준다(수기 검사 약 15행 삭제). 공백 문자열 판정의 불일치도 사라진다.
- 비용과 위험: `review_cycle.py`, `review_policy.py`가 바뀐다. 오류 문구가 jsonschema 문구로 바뀐다.
- 기능·커버리지 영향: 있음. REV-03의 주입 경로로 공백 텍스트를 넣던 입력이 거부된다. 운전 경로는 같다.
- 사용자 결정 관련: 없음
- 확신도: 확인

#### REV-12 닫힌 객체 스키마 빌더가 영역 안에 네 벌 있다
- 검토: 1
- 종류: 이음새
- 좌표: `scripts/do_math/contracts.py:25-27`, `scripts/do_math/submission.py:156-158`, `scripts/do_math/review_cycle.py:39-40`, `scripts/do_math/integration.py:117-118`
- 현상: `{"type": "object", "properties": P, "required": list(P), "additionalProperties": False}`를 만드는 함수가 네 곳에 따로 있다. `submission._object`만 `required`를 다르게 줄 수 있다. `record_schemas.obj`는 기본 `required=()`로 규칙이 다르므로 다른 개념이다.
- 근거: 검색식 `^def _object|^    def obj|^def _array`(`scripts/do_math`)의 일치 중 관련은 4건이다. `context_store._object_size`는 무관하다.
- 제안: `contracts`(wire 스키마 소유)에 `closed_object(properties, required=None)` 하나를 두고 세 모듈이 가져다 쓴다.
- 실익: 같은 규칙의 정의 4개가 하나로 준다(약 8행).
- 비용과 위험: 파일 4개가 바뀐다. `integration`은 이미 `contracts`를 import하므로 새 순환이 없다. 스키마 digest는 정규 JSON이 키를 정렬하므로 바뀌지 않는다(추정).
- 기능·커버리지 영향: 없음
- 사용자 결정 관련: 없음
- 확신도: 확인

#### REV-13 제안 좌표 `proposal:<경로>` 해석이 두 곳에 남았다
- 검토: 1
- 종류: 이음새
- 좌표: `scripts/do_math/review_cycle.py:672-680`, `scripts/do_math/submission.py:535-544`
- 현상: 2라운드(REV-03)가 조사 원천 허용 규칙을 `classify_research_source`로 모았다. 그러나 `proposal:`, `.`, `/` 경로를 따라 내려가는 같은 루프가 일반 참조 검사 `_validate_reference`에 한 벌 더 있다(539-543행).
- 근거: 검색식 `removeprefix\("proposal:"\)`(`scripts/do_math`)의 일치는 2건이고 둘 다 관련이 있다.
- 제안: `review_cycle`에 `proposal_value(proposal, reference)`를 두고, 두 곳이 모두 이것을 부른다.
- 실익: 약 6행의 좌표 해석 사본이 지워진다. 제안 좌표 문법이 한 곳에서 정의된다.
- 비용과 위험: 두 파일이 바뀐다. 새 상태는 없다.
- 기능·커버리지 영향: 없음
- 사용자 결정 관련: 없음
- 확신도: 확인

#### REV-14 인라인 조사 원천 행의 바이트 규칙을 만드는 곳 하나와 검증하는 곳 둘이 따로 적는다
- 검토: 1
- 종류: 이음새
- 좌표: `scripts/do_math/review_engine.py:1080-1081`, `scripts/do_math/review_engine.py:1169-1171`, `scripts/do_math/review_cycle.py:309-312`
- 현상: 인라인 원천 행은 `raw = compact_json_bytes(value)`, `sha256(raw)`, `len(raw)`로 봉인된다(`_research_source_spec`, 1080-1081행). 같은 규칙의 검증이 두 곳에 따로 있다. 하나는 실시간 자료화(`_materialize_research_sources`, 1169-1171행)이고, 다른 하나는 봉인 재구성(`validate_sealed_review`, 309-312행)이다.
- 근거: 세 곳 원문을 대조했다. 검증 조건(해시와 길이)은 같고 오류 문구는 다르다.
- 제안: `review_cycle`에 `inline_source_row(ref, value)`(행 생성)와 `inline_source_bytes(source)`(검증 뒤 바이트 반환, 불일치면 ValueError)를 두고 세 곳이 쓴다.
- 실익: 한 규칙의 정의 셋이 하나가 된다(약 6행).
- 비용과 위험: 두 파일이 바뀐다. 재구성 쪽의 오류 문구(`supplemental source bytes changed`)는 유지해야 할 수 있다.
- 기능·커버리지 영향: 없음
- 사용자 결정 관련: 없음
- 확신도: 확인

#### REV-15 기계 검사 기록의 필드 목록과 읽기·해석 실패 기록이 여러 곳에 따로 있다
- 검토: 1
- 종류: 이음새
- 좌표: `scripts/do_math/submission.py:1199-1211`, `scripts/do_math/submission.py:1540-1552`, `scripts/do_math/submission.py:1608-1619`, `scripts/do_math/submission.py:1473`, `scripts/do_math/submission.py:1264`
- 현상: 사본은 세 종류다.
  - `check_subject`의 키 튜플이 세 곳에 있다. `check_submission`과 `seal_submission`의 실패 기록은 7개 키(`revision_targets` 포함)이고, `_producer_check`는 6개 키로 덮어쓴다(1551-1552행).
  - 읽기·해석 실패 기록 dict가 `_producer_check`(1540-1549행)와 `seal_submission`(1608-1619행)에 거의 같은 모양으로 두 번 있다. `contract_id`, `not_checked`, `check_order`, `comparison`이 같다.
  - `not_checked` 목록이 다섯 곳에 있다. 이 가운데 설치 계약의 목록(1473행)에는 `check_submission`의 `kind_semantic_approval`이 없다.
- 근거: 원문을 대조했다. `check_subject`는 `_failure_key`(1268-1272행)의 범위 해시에 들어간다. 생산자 사슬과 수신 기록은 서로 비교되지 않으므로, 현재 키 차이가 오판을 만들지는 않는다.
- 제안: `CHECK_SUBJECT_FIELDS`와 `_failed_check(mode, context, raw, error, phase)` 하나를 두고 두 실패 경로가 쓴다. `not_checked` 기본 목록도 상수 하나로 둔다. 설치 계약은 그 상수를 가리킨다.
- 실익: 약 20행의 사본과, 이미 한 번 어긋난 목록(1473행)이 정리된다.
- 비용과 위험: `submission.py`만 바뀐다. 생산자 검사의 `check_subject`에 `revision_targets`가 더해지면 생산자 check ID가 바뀐다. 저장된 과거 check와 비교하는 호환 문제는 없다(결정 1).
- 기능·커버리지 영향: 없음
- 사용자 결정 관련: 없음
- 확신도: 확인

#### REV-16 계획 처분·평가의 형태를 wire 스키마 통과 뒤에 다시 검사한다
- 검토: 1
- 종류: 불일관
- 좌표: `scripts/do_math/task_contracts.py:245-253`, `scripts/do_math/task_contracts.py:261-265`, `scripts/do_math/task_scope.py:392-394`, `scripts/do_math/task_scope.py:399-401`, `scripts/do_math/contracts.py:166-169`, `scripts/do_math/contracts.py:194-198`
- 현상: 같은 형태를 여러 번 검사한다.
  - `validate_plan_dispositions`가 다시 보는 조건: `dispositions` 존재, 행이 `task_id` 문자열을 가진 dict인지, `kind` 열거, `reason`·`next_owner`의 비지 않은 텍스트. `research_plan` wire 스키마의 `PLAN_DISPOSITION`(`TEXT`, `enum`)이 이미 같은 조건을 요구한다.
  - `apply_task_assessments`는 같은 호출 사슬에서 `validate_plan_dispositions`가 이미 확인한 중복 평가와 `decision` 열거를 다시 본다.

  2라운드 REV-11은 같은 이유("봉인된 확장의 형태를 적용 단계가 다시 검사한다")로 `task_scope._withdrawal` 등을 지웠다. 하지만 계획 산출에는 이 원칙이 적용되지 않았다.
- 근거: 호출 경로는 셋이다.
  - 생산자 검사: `submission.py:815`. 스키마 이슈가 있으면 644-645행에서 먼저 반환하므로 이 검사에 닿지 않는다.
  - 수신 적용: `decision_engine.py:143`, `engine.py:4275`. 봉인되어 검사를 통과한 산출이다.
  - 운영 점검: `engine.py:4202`. 스키마가 `task_assessments`를 1개로 묶는다(`engine.py:2143-2146`).

  검색식 `validate_plan_submission\(|apply_task_assessments\(`의 제품 일치는 5건이고 모두 관련이 있다. 스키마가 표현하지 못하는 조건은 이 검사에만 있으므로 남긴다. 대상은 모집단 일치, 선택 시 `expected_research_change` 비지 않음, `revisit` 시각 해석, 병렬 참조다.
- 제안: 위 형태 검사 약 10행을 지우고 의미 검사만 남긴다.
- 실익: 약 10행 삭제. 2라운드 REV-11의 원칙이 계획 산출에도 같게 적용된다.
- 비용과 위험: `task_contracts.py`, `task_scope.py`가 바뀐다. 시험이 손으로 만든 계획으로 이 함수의 형태 거부를 단언하면(`tests/test_redesign_TASKS.py:774-778` 등) 그 시험을 현행 경계에 맞춰 옮겨야 한다.
- 기능·커버리지 영향: 있음(형태 오류의 거부 위치가 스키마 검사로 모인다)
- 사용자 결정 관련: 없음
- 확신도: 확인

#### REV-17 항목 처분 종류의 어휘가 두 곳에 있다
- 검토: 1
- 종류: 이음새
- 좌표: `scripts/do_math/task_contracts.py:14`, `scripts/do_math/contracts.py:158-161`
- 현상: `DISPOSITION_KINDS = {"fulfilled", "open", "waived", "transferred"}`와 wire `ITEM_DISPOSITION`의 종류 튜플이 같은 네 값을 따로 적는다.
- 근거: 검색식 `DISPOSITION_KINDS|"transferred"|'transferred'`에서 관련 정의는 2곳이다. `validate_item_dispositions`는 저장 판정의 형태 검사기이기도 해서 지울 수 없다(`record_schemas/__init__.py:343`). 그러니 합칠 대상은 어휘뿐이다.
- 제안: `contracts.ITEM_DISPOSITION`를 `task_contracts.DISPOSITION_KINDS`로 만들거나, 반대로 `DISPOSITION_KINDS`를 wire 정의에서 파생한다. 이음새 계약 11절에 한 행을 더한다.
- 실익: 상태 어휘의 사본 하나가 사라진다. 방향성 1의 "상태 값" 이음새다.
- 비용과 위험: 두 파일이 바뀐다. 적재 순서(`contracts`↔`task_contracts`)는 지연 import로 풀린다.
- 기능·커버리지 영향: 없음
- 사용자 결정 관련: 없음
- 확신도: 확인

#### REV-18 연구 산출 역할 집합이 영역 안에 이름 붙은 상수 둘과 리터럴로 흩어져 있다
- 검토: 1
- 종류: 이음새
- 좌표: `scripts/do_math/submission.py:135-136`, `scripts/do_math/integration.py:17`, `scripts/do_math/contracts.py:242`, `scripts/do_math/decision_engine.py:65`, `scripts/do_math/task_scope.py:47`, `scripts/do_math/task_scope.py:325`, `scripts/do_math/task_scope.py:411`
- 현상: 두 역할 집합이 여러 곳에 흩어져 있다.
  - `{"research_work", "supplemental_research"}`는 `submission.PRODUCERS`와 `integration.PRODUCERS`에 같은 값으로 두 번 정의되어 있다. 영역 안에 리터럴로 4번 더 적혀 있다.
  - 계획 역할 `{"research_preparation", "research_plan"}`은 `submission.PLANNERS`와 `task_scope.py:47`의 리터럴에 있다.

  2라운드는 역할 집합의 정본을 `execution_profiles`(`WORK_ROLES` 등)와 `governance.TASK_WORK_ROLES`에 두었다. 하지만 이 두 집합은 정본 목록에 없다.
- 근거: 검색식 `^PRODUCERS\s*=|^PLANNERS\s*=|\{"research_work", "supplemental_research"\}|\{'research_work', 'supplemental_research'\}|\{"research_preparation", "research_plan"\}|\{'research_preparation', 'research_plan'\}`(`scripts/do_math`)의 일치는 39건이다. REV 영역은 9건이고 모두 같은 뜻("과제 연구를 산출하는 역할", "계획 역할")이다. 나머지 30건은 engine·scheduler·planning·revision_engine·context_store·model_policy에 있다(5절).
- 제안: `execution_profiles`에 `RESEARCH_PRODUCER_ROLES`와 `PLANNING_ROLES`를 정본으로 둔다. 영역의 상수 둘과 리터럴을 이 이름으로 바꾼다. 다른 영역의 리터럴은 각 소유자가 옮긴다.
- 실익: 같은 집합의 정의가 한 곳으로 모인다. 영역 안에서 상수 사본 1개와 리터럴 5곳이 정리된다.
- 비용과 위험: 영역 안에서는 파일 5개가 바뀐다. 다른 영역의 리터럴 가운데 `not review_cycle_id` 조건과 결합된 곳은 뜻이 "과제 연구 산출"로 좁혀지므로, 옮길 때 조건을 함께 보존해야 한다.
- 기능·커버리지 영향: 없음
- 사용자 결정 관련: 없음
- 확신도: 추정. 영역 안은 확인했다. 영역 밖 30건이 모두 같은 개념인지는 각 호출부를 읽어야 확정된다.

#### REV-19 실행 프로필 참조의 형태가 세 정의로 남아, 과제 계약 저장 규칙이 저장 스키마의 느슨한 판본을 보정한다
- 검토: 1
- 종류: 이음새
- 좌표: `scripts/do_math/contracts.py:140-141`, `scripts/do_math/task_contracts.py:93-104`, `scripts/do_math/record_schemas/schemas.py:59`, `scripts/do_math/execution_profiles.py:264-270`
- 현상: 같은 형태가 세 곳에 따로 정의되어 있다.
  - wire `PROFILE_REF`: revision ≥ 1, sha256 패턴
  - 저장 `PROFILE_REF`: revision `NAT`(≥ 0), `HASH`
  - Python `validate_profile_ref`: revision ≥ 1, `is_sha256`

  저장 스키마가 revision 0을 받으므로, `validate_contract_rules`는 과제의 프로필 참조마다 `validate_profile_ref`를 다시 부른다(99-103행). 저장 관문의 과제 가족 검증기는 이것 때문에 `validate_contract_meaning` 대신 이 함수가 되었다(결과-이음새 1절 2번).
- 근거: 세 정의를 대조했다. 이음새 계약 11절은 `validate_profile_ref`를 "실행 프로필 참조 형태"의 정본으로 든다.
- 제안: 저장 `PROFILE_REF`의 revision을 `minimum: 1`로 맞춘다(STO 영역 파일). 그러면 `validate_contract_rules`의 보정 루프가 필요 없어져 `validate_contract_meaning`만 남는다. wire와 저장 스키마의 노드를 하나로 합칠지(`id`의 `TEXT` 대 `ID`)는 별도로 판단한다.
- 실익: 함수 한 층(`validate_contract_rules`, 약 12행)이 지워진다. 형태 규칙의 셋째 판본이 스키마 안으로 들어간다.
- 비용과 위험: `record_schemas/schemas.py`(STO), `task_contracts.py`, `record_schemas/__init__.py`의 가족 검증기 등록이 바뀐다. 저장 계약 manifest의 digest도 바뀐다.
- 기능·커버리지 영향: 없음(운전 중 revision 0인 프로필은 생기지 않는다고 추정)
- 사용자 결정 관련: 없음
- 확신도: 추정. 프로필 판본이 1부터 시작하는지(`execution_profiles.validate_profile`와 프로필 레코드 스키마의 revision 범위)를 확인하면 확정된다.

#### REV-20 `task_contracts.readiness_for_task`는 `planning.task_ready`에 위임만 한다
- 검토: 1
- 종류: 경계
- 좌표: `scripts/do_math/task_contracts.py:225-228`
- 현상: 이 함수는 인자를 그대로 `planning.task_ready`에 넘긴다.
- 근거: 검색식 `readiness_for_task`(스킬 전체)의 일치는 3건이다. 정의 1건, 제품 호출 `reporting.py:78` 1건, 시험 `tests/test_redesign_TASKS.py:446` 1건이다.
- 제안: 함수를 지우고 두 호출자가 `planning.task_ready`를 직접 부르게 한다.
- 실익: 위임만 하는 층 하나(4행)가 사라진다.
- 비용과 위험: 파일 3개가 바뀐다(`reporting.py`는 OPS 영역).
- 기능·커버리지 영향: 없음
- 사용자 결정 관련: 없음
- 확신도: 확인

#### REV-21 읽기만 하는 프로필 조회 네 곳이 복사판 `resolve_profile`을 쓴다
- 검토: 1
- 종류: 불일관
- 좌표: `scripts/do_math/review_cycle.py:217-219`, `scripts/do_math/review_cycle.py:604-611`, `scripts/do_math/review_engine.py:476-488`, `scripts/do_math/submission.py:751-755`
- 현상: 2라운드는 저장 프로필 조회의 정본을 `match_profile_ref`(재해시·복사 없음)로 두었다. `resolve_profile`은 그 결과를 깊은 복사한다(`execution_profiles.py:287-289`). 영역의 네 호출부는 모두 복사본의 필드를 읽기만 한다. 읽는 필드는 `role`, `actor_kind`, `host_capacity_refs`, 그리고 `observation_settings_errors`의 읽기다(`observations.py:181-193`).
- 근거: 네 곳의 원문과 `observation_settings_errors`를 확인했다. 검색식 `resolve_profile\(|match_profile_ref\(`의 일치는 37건이다. 영역 안의 `resolve_profile` 호출은 이 4건이 전부다.
- 제안: 네 곳을 `match_profile_ref`로 바꾼다.
- 실익: 매 호출의 프로필 깊은 복사가 사라진다. 비용은 작지만, 2라운드가 정한 "읽기 조회는 복사하지 않는다"가 영역 안에서 일관된다.
- 비용과 위험: 파일 3개가 바뀐다. 호출자가 결과를 고치지 않으므로 공유 참조의 위험은 없다.
- 기능·커버리지 영향: 없음
- 사용자 결정 관련: 없음
- 확신도: 확인

#### REV-22 `review_research_limit`의 기본값 3이 설정 기본 표 밖에 세 번 더 적혀 있다
- 검토: 1
- 종류: 이음새
- 좌표: `scripts/do_math/review_cycle.py:338`, `scripts/do_math/review_engine.py:713`, `scripts/do_math/review_engine.py:1104`, `scripts/do_math/engine.py:104`, `references/CLI-실행-계약.md:166`
- 현상: 설정 기본값의 정본은 두 곳이다. 코드는 `engine.DEFAULT_CONFIG`이고, 문서는 `CLI-실행-계약.md`의 설정 목록이다(방향성 7). 그런데 영역 코드는 `config.get('review_research_limit', 3)`으로 같은 기본값을 세 번 더 적는다. `defer_for_research`의 인자 기본값 `limit=3`(`review_cycle.py:697`)도 있다.
- 근거: 검색식 `review_research_limit`(스킬 전체)의 일치는 6건이다. 설정은 `create`와 `validate_config`에서 `DEFAULT_CONFIG`와 합쳐지므로(`engine.py:213`, `:241-243`), 저장 설정에는 이 키가 늘 있다(추정).
- 제안: 세 곳을 `config['review_research_limit']`로 바꾸고, `defer_for_research`의 `limit` 기본값을 없앤다.
- 실익: 수치 사본 넷이 정본 하나를 가리키게 된다.
- 비용과 위험: 파일 2개가 바뀐다. 설정을 손으로 만들며 이 키를 빼는 시험이 있으면 KeyError가 난다. 그러면 그 시험이 현행 설정을 구성하도록 고친다(방향성 4).
- 기능·커버리지 영향: 없음
- 사용자 결정 관련: 없음
- 확신도: 추정. 저장 설정에 키가 빠질 경로(`configure` 제어의 부분 갱신)가 기본값 병합을 거치는지 확인하면 확정된다.

#### REV-26 `contracts.py`의 모듈 설명이 Codex 어댑터 전용으로 적혀 있다
- 검토: 1
- 종류: 문서
- 좌표: `scripts/do_math/contracts.py:1`
- 현상: 모듈 docstring은 "Role prompt and output schemas for the Codex CLI adapter."다. 그러나 역할 응답 스키마는 공급자와 무관하다. `engine._response_schema`(`engine.py:2123-2162`)에는 공급자 분기가 없고, Claude 어댑터도 같은 스키마를 받는다.
- 근거: `_response_schema` 원문에서 공급자 조건이 0건이다.
- 제안: "for the CLI adapters"처럼 공급자 중립으로 고친다.
- 실익: 모듈 책임의 오해 여지 하나가 사라진다.
- 비용과 위험: 없음
- 기능·커버리지 영향: 없음
- 사용자 결정 관련: 없음
- 확신도: 확인

### 검토 2

#### REV-23 스키마 빌더가 모듈 전역 노드를 반환값에 그대로 싣고, 제자리 변경에 대한 방어가 세 방식으로 갈려 있다
- 검토: 2
- 종류: 결함
- 좌표: `scripts/do_math/submission.py:161-234`, `scripts/do_math/contracts.py:172-188`, `scripts/do_math/integration.py:115-136`, `scripts/do_math/review_cycle.py:47-53`, `scripts/do_math/review_cycle.py:626-639`, `scripts/do_math/review_engine.py:579-585`, `scripts/do_math/review_engine.py:1140-1147`, `scripts/do_math/record_schemas/schemas.py:12`, `scripts/do_math/record_schemas/schemas.py:323-336`
- 현상: 9b434f4가 고친 결함은 공유 노드를 제자리에서 바꾼 것이었다. 같은 형태가 세 방식으로 남아 있다.
  1. `extension_schema`, `disposition_schema`, `impact_review_response_schema`는 모듈 전역 객체를 반환 스키마 안에 그대로 넣는다. 대상은 `contracts.TEXT`, `REFS`, `PROFILE_REF`와 `model_policy.ASSESSMENT_SCHEMA["properties"]`의 속성 노드다(`submission.py:203-204`). 2라운드가 비지 않은 텍스트 정의를 `contracts.TEXT` 하나로 모았으므로, 같은 객체가 저장 과제 스키마에도 들어 있다(`schemas.py:12`의 `TEXT as _NONEMPTY_TEXT`, 323-336행). 따라서 누군가 확장 스키마의 텍스트 필드에 `enum`이나 `maxLength`를 제자리에서 넣으면 결과가 둘 난다. wire 스키마 전체가 바뀌고, 이후 생성되는 저장 관문의 과제 스키마도 프로세스가 끝날 때까지 바뀐다. 9b434f4의 결함은 호출 한 번에 국한됐지만, 이 경우는 프로세스 전역이다.
  2. `stage_schema`는 호출마다 `string` 노드 하나를 만들어 모든 문자열 필드가 공유한다(49-53행). 방어는 소비자 `_review_schema`가 새 노드로 다시 묶는 것(584행)뿐이다.
  3. `research_schema`는 필드마다 사본을 만들고(626-634행), 소비자도 새 노드로 다시 묶는다(1144-1146행). 방어가 이중이다.
- 근거: 검색식 `\[['"](enum|description|maxItems|minItems|pattern|const|required|additionalProperties)['"]\]\s*(=|\.append)|\['properties'\]\[[^\]]+\]\s*=`(`scripts/do_math`)의 일치는 29건이다. 영역 빌더의 반환값을 제자리에서 바꾸는 곳은 0건이다. 모두 새 노드 대입이거나, `deepcopy`나 `identify_schema`로 떼어 낸 사본의 변경이다. 따라서 지금 발현된 결함은 없고, 회귀 위험이다.
- 제안: 규칙 하나를 정해 한 곳에 적는다. 예를 들면 `contracts` 모듈 설명에 "스키마 빌더의 반환값은 모듈 전역 노드와 분리한다. 소비자는 필드 노드를 제자리에서 바꾸지 않고 새 노드로 다시 묶는다"라고 쓴다. 코드는 빌더 셋이 끝에서 `copy.deepcopy`로 반환하게 하고, `research_schema`의 필드별 사본 헬퍼를 지워 `stage_schema`와 같은 모양으로 맞춘다. 규칙을 지키는지는 시험 하나로 확인한다. 빌더 반환값의 어떤 노드도 `contracts.TEXT`·`REFS`와 같은 객체(`is`)가 아님을 단언한다.
- 실익: 9b434f4와 같은 형태의 결함이 전역 규모로 다시 생길 여지가 사라진다. 방어 방식이 셋에서 하나로 준다.
- 비용과 위험: 파일 4개가 바뀐다. 확장 스키마는 검사마다 두 번 만들어지므로 깊은 복사 비용이 조금 늘지만, 작은 스키마다.
- 기능·커버리지 영향: 없음
- 사용자 결정 관련: 없음
- 확신도: 확인. 공유 참조는 원문으로 확인했고, 현재 변경자 0건은 검색으로 확인했다.

#### REV-24 고정 입력 메모와 엔진이 저장소 대역을 받아들이려고 제품 규칙을 따로 둔다
- 검토: 2
- 종류: 임시방편
- 좌표: `scripts/do_math/submission.py:112-132`, `scripts/do_math/repository.py:42-51`, `scripts/do_math/review_engine.py:182-184`, `scripts/tests/research_fixtures.py:783-795`
- 현상:
  - `issued_input`의 프로세스 메모는 `git_dir`가 `os.PathLike`일 때만 쓴다(123행). docstring은 "A git_dir that is not a filesystem path (a test double or label) is not cached"라고 이유를 밝힌다. 같은 전제(묶음 불변, `str(git_dir)` 키)를 쓰는 S3 메모 `VERIFIED_ARTIFACTS`는 `None`만 제외하고 문자열 표지도 기억한다(`repository.py:48-51`, `:64-65`). 그래서 저장소 식별의 규칙이 두 메모 사이에서 다르고, 한쪽은 시험 대역을 위한 분기다.
  - `_publish_assessment_reassessment`는 `getattr(self.store, 'read', None)`, `getattr(self.store, "git_dir", None)`으로 저장소 속성의 부재를 허용한다(182-184행, 8d2ffd0). 같은 엔진의 다른 호출부는 `self.store.git_dir`를 직접 읽는다(`engine.py` 10곳 이상).
  - 시험은 이 메모를 포함한 제품 캐시 넷을 내부 이름으로 직접 비운다(`research_fixtures.forget_repository_caches`, 9b434f4).
- 근거: 검색식 `git_dir\s*=|_ISSUED_INPUTS|issued_input`(`scripts`)의 일치 55건 가운데 관련 행을 읽었다. 제품의 `store.git_dir`는 늘 `Path`다(`repository.py:238-241`). 문자열 표지(`'fixture-git'` 등)를 쓰는 곳은 시험뿐이다(`tests/test_approved_five_repairs.py:48`, `tests/test_performance_repairs.py:176`, `:197`, `tests/test_redesign_ENGINE.py:1194`, `:1410`, `tests/test_repair_plan.py:92`).
- 제안: 저장소 식별 규칙을 S3 하나로 맞춘다. `issued_input`은 `git_dir is not None`이면 `artifact_key`와 같은 방식으로 키를 만든다. 시험은 대역마다 고유한 표지(`'git-' + uuid`는 이미 `test_performance_repairs.py:197`의 관례다)나 `None`을 쓴다. `_publish_assessment_reassessment`의 `getattr` 둘은 직접 속성 접근으로 바꾼다. 메모 자체는 유지한다(4절).
- 실익: 제품에서 시험 대역 전용 분기 둘이 사라진다(방향성 4). 한 전제를 쓰는 두 메모의 키 규칙이 하나가 된다.
- 비용과 위험: `submission.py`, `review_engine.py`와 공용 표지를 쓰는 시험 몇 곳이 바뀐다. 공용 표지 `'fixture-git'`을 여러 시험이 같은 묶음 경로로 쓰면 메모가 시험 사이에 새어 나갈 수 있다. 그래서 시험 표지를 고유하게 바꾸는 일이 선행되어야 한다.
- 기능·커버리지 영향: 없음(제품 동작 불변)
- 사용자 결정 관련: 없음
- 확신도: 추정. 제품 분기의 존재는 확인했다. 표지를 공유하는 시험이 같은 `input_bundle` 경로를 재사용하는지 확인하면 필요한 시험 수정 범위가 확정된다.

#### REV-25 모델에 새로 전달한 스키마 키워드를 공급자 CLI가 받아들이는지 아직 확인하지 않았다
- 검토: 2
- 종류: 공백
- 좌표: `scripts/do_math/review_cycle.py:57-65`, `scripts/do_math/contracts.py:163-165`, `scripts/do_math/contracts.py:180-181`, `scripts/do_math/contracts.py:192-193`
- 현상: 2라운드가 모델에 전달하는 스키마에 새 키워드를 넣었다.
  - scope 평가의 `const`, `anyOf`+`null`, `minItems`
  - 계약 검토 항목의 `enum`, `minItems`·`maxItems`
  - repair 대상의 `pattern "^installation:"`
  - 검토 문자열의 `pattern "\S"`

  M-0349 「남은 위험과 진입점」은 "모델에 전달하는 스키마의 새 키워드를 공급자 CLI가 받아들이는지"를 남은 위험으로 적었다(`C:/math/기억/layer1/M-0349.md:53-57`). `결과-C.md` 5.3절은 `preflight._check_schema_pair`가 메타스키마 적합성만 본다고 적었다. M-0350은 시험 검증만 기록했고 실제 공급자 실행은 기록하지 않았다.
- 근거: 세 기록을 읽었다. 이 위험을 닫은 실행 기록은 찾지 못했다.
- 제안: 코드를 바꾸지 않고, 공급자별(Codex, Claude)로 실제 실행 한 번씩을 한다. 대상은 scope 단계의 `identity_review`와 `task_contract_review`다. 스키마 거부가 없는지 확인해 공백을 닫는다. 거부되면 해당 키워드만 스키마에서 빼고 공유 검사 함수에 남긴다.
- 실익: 운전 중 처음 만나는 scope 단계·계약 검토에서 모든 실행이 스키마 거부로 실패할 위험을 미리 닫는다.
- 비용과 위험: 실제 공급자 호출 비용이 든다. 새 상태는 없다.
- 기능·커버리지 영향: 없음
- 사용자 결정 관련: 없음
- 확신도: 추정. 두 공급자에서 위 두 역할을 한 번씩 실행해 스키마 거부 여부를 보면 확정된다.

## 4. 보존 판정

- **`issued_input`의 메모 자체**(`scripts/do_math/submission.py:108-132`). 저장소가 이미 artifact 바이트를 메모한다(`repository.py:536-552`, 9b434f4). 그래서 이 메모는 해석 비용만 아낀다. 한 줄 측정에서 `load_json`(해석과 `canonical_json` 검사)은 같은 값의 `deepcopy`보다 약 2배 느렸다. 명령은 `python -c "...timeit(load_json(raw))...timeit(copy.deepcopy(v))"`이고, 합성 340KB 기준 결과는 0.086초 대 0.041초였다. 그러므로 메모는 실익이 있다. 바꿀 것은 키 규칙뿐이다(REV-24).
- **`_support_archive`의 `lru_cache(maxsize=2)`**(`scripts/do_math/submission.py:1423-1432`). 키가 배포 파일의 상대 경로와 내용 digest 전부이므로, 결과를 정하는 입력이 모두 키에 들어 있다. 무효화는 키 변화로 자동이다(방향성 9 충족).
- **`read_sealed_submission`의 해시·영수증 대조와 check ID 재계산**(`scripts/do_math/submission.py:40-105`). 디스크의 기존 기록이라는 신뢰 경계를 건너는 수신 검사다(2절 12항).
- **`validate_sealed_review`의 전면 재구성**(`scripts/do_math/review_cycle.py:240-375`). 저장 기록만으로 판정을 복원하는 경로다. 과거 조사 보존 판정의 근거가 지금도 맞다.
- **`validate_item_dispositions`의 수기 형태 검사**(`scripts/do_math/task_contracts.py:144-212`). wire `ITEM_DISPOSITION`과 모양이 겹친다. 그러나 저장 스키마에서 과제 `assessment`는 자유 형태이고, 저장 관문이 이 함수로 저장 판정을 검사한다(`record_schemas/__init__.py:343`). 그래서 이것은 저장 형태의 유일한 검사기다. REV-17은 어휘만 합친다.
- **`apply_bundles`의 `except Exception`**(`scripts/do_math/integration.py:501-519`). 원인을 모르는 채 예외를 삼키는 모양이다. 하지만 이것은 설계된 경계다. 적용 콜백의 실패를 단계(`currentness`, `application`, `candidate`, `publication`)와 함께 묶음 반려로 기록하고, 게시 실패면 나머지 묶음을 엔진에 넘긴다. 삼킨 예외는 문구와 단계로 보존된다.
- **리뷰 주기 내부 식별자의 `json_digest`**(`scripts/do_math/review_cycle.py:128`, `:767`, `:797`, `:1197`). `proposal_digest`, 발견 키, `sealed_input_sha256`은 상태에 저장되는 값의 식별이다. 그런데도 `exact_content_hash`가 아니라 `json_digest`를 쓴다. 이음새 계약 2.1은 저장·대조되는 기존 변종의 규칙을 바꾸지 않는다고 정했고, 생산과 대조가 모두 `review_cycle` 안에서 같은 함수를 쓴다. 따라서 규칙을 바꿔도 실익이 없다. REV-02의 `request_digest`는 한 필드가 두 규칙을 쓰는 경우라 다르다.
- **`validate_review_independence`가 governance 함수를 먼저 부르는 것**(`scripts/do_math/review_cycle.py:187-189`). 이 호출은 작성자와 공급자 대화 ID(`provider_session_id`, `conversation_id`)의 공유도 검사한다(`governance.py:1058-1061`). 이 검사는 계보 순회만으로는 대신할 수 없다. REV-05는 순회만 공유하자는 제안이다.
- **`contracts.py` 모듈 적재 시점의 제자리 구성**(`scripts/do_math/contracts.py:132`, `:144-146`, `:156`). `OBLIGATION`·`PROGRESS`에 선택 필드를 넣고 `MANIFEST_SCHEMA`에 설명을 붙인다. 이것은 적재 때 한 번 하는 구성이므로 반환된 스키마를 소비자가 바꾸는 REV-23의 형태와는 다르다.
- **`summarize_snapshot_checks`의 봉인마다 대조**(`scripts/do_math/submission.py:1380-1420`). 2라운드가 S3 커널로 바꿔, 같은 프로세스에서는 처음 한 번만 해시한다. 추가로 줄일 것은 없다.

## 5. 영역 밖 관찰

- `scripts/tests/research_fixtures.py:783-795` (TSB): 시험이 제품 캐시 넷(`VERIFIED_ARTIFACTS`, `_VALIDATED_READS`, `planning._VALID_ARTIFACTS`, `submission._ISSUED_INPUTS`)을 내부 이름으로 직접 비운다. 방향성 11의 "제품 내부 상태를 직접 비우는 시험" 신호다. 네 메모의 무효화 규칙이 한 곳에 없다는 뜻이기도 하다.
- `scripts/do_math/repository.py:133-180` (STO): artifact 바이트 메모(`_ARTIFACT_FACTS`)가 `submission._ISSUED_INPUTS` 아래층에 있다. 두 층이 같은 불변 전제를 쓰므로 이음새 계약 3절에 함께 적을지 판단이 필요하다.
- `scripts/do_math/engine.py` 9곳 (ENG): `read_artifact` 순서를 뒤집는 람다가 있다. REV-06의 수신 쪽이다.
- `scripts/do_math/governance.py:1052-1057` (OPS): `validate_independent_execution`은 `continuation_of`를 ID 하나로 가정한다. 저장 스키마와는 맞다(`schemas.py:264`). REV-05에서 순회를 공유할 때 기준이 된다.
- `scripts/do_math/engine.py`, `scheduler.py`, `planning.py`, `revision_engine.py`, `context_store.py`, `model_policy.py` (ENG/RUN/RES): 연구 산출·계획 역할 집합의 리터럴이 30건 있다(REV-18).
- `scripts/do_math/planning.py:630`, `:683` (RES): 준비 판정이 의존 과제마다 `task_scope.assessment_current`를 불러 전체 색인을 다시 만든다(REV-10).
- `scripts/do_math/record_schemas/schemas.py:59` (STO): 저장 `PROFILE_REF`의 revision이 `NAT`(≥ 0)이어서 `validate_profile_ref`(≥ 1)와 다르다(REV-19).
- `scripts/do_math/model_policy.py:78` 대 `task_scope.py:212`의 `assessment_basis`, `knowledge_records.py:286`·`academic.py:70`·`task_scope.py:292`의 `assessment_current` (RUN/RES): 같은 이름이 서로 다른 개념에 쓰인다. 이름만 겹치고 규칙은 다르므로 합칠 대상은 아니다. 이름으로 구별하는 것이 좋다.
- `scripts/tests/test_lifecycle_engine.py:774`, `:823`, `scripts/tests/test_redesign_ENGINE.py:542` (TSB): `결과-C.md` 4.1절이 "부르지 않는 경로를 막지만 해가 없어 남겼다"고 적은 `_available_inputs` 대역이 아직 남아 있다.
- `scripts/do_math/engine.py:849` (ENG): `getattr(self.store, "git_dir", None)`. REV-24와 같은 저장소 대역 수용이다.

## 6. 작업 기록

- 처음에는 `_ISSUED_INPUTS`를 비대로 보고 삭제 후보로 올리려 했다. 9b434f4가 `repository.read`에 artifact 바이트 메모를 더했으므로 층이 겹친다고 보았고, 합성 자료에서 `deepcopy`가 `json.loads`보다 약 7배 느렸다. 그러나 제품의 `load_json`은 `canonical_json` 검사까지 하므로 다시 쟀다. 결과는 `deepcopy`가 약 2배 빨랐다. 그래서 삭제 후보를 버리고 키 규칙만 후보로 남겼다(REV-24, 4절).
- 9b434f4의 공유 노드 결함과 같은 형태를 찾으면서, 스키마를 제자리에서 바꾸는 코드를 전수 검색했다(29건). 발현된 결함은 없었다. 대신 모듈 전역 노드가 2라운드 뒤 저장 과제 스키마와 공유된다는 점을 확인해, 파급 범위가 전역인 회귀 위험으로 적었다(REV-23).
- `_prepare_review_context`의 오류 문구 표지 분기(REV-07)는 처음에 임시방편으로 보았다. 그런데 검색하니 표지를 담은 일반 ValueError가 0건이었다. 그래서 도달 불가(미사용)로 분류했다.
- `_start_identity_review`의 `config.get('review_scope_assessment')`가 시험 전용이라는 판정(REV-03)은 두 사실을 모두 확인한 뒤에 확정했다. 하나는 닫힌 설정 스키마와 `validate_config`의 키 거부이고, 다른 하나는 지식 저장 스키마에 필드가 없다는 것이다.
- `request_digest`의 두 정의(REV-02)는 8d2ffd0·379a171 변경을 대조하다 발견했다. 두 경량화는 모두 해시 함수 이름만 바꾸었고, 한 필드가 두 규칙을 쓰는 구조는 그대로 두었다.
- REV-26은 검토 2 후보(REV-23~25)에 번호를 붙인 뒤에 더한 검토 1 후보다. 그래서 번호가 절 순서와 어긋난다. 번호는 모두 고유하다.
- graphify는 기준 6절에 따라 쓰지 않았다. 시험은 실행하지 않았다. 저장소를 바꾸지 않는 파이썬 한 줄 측정 두 번만 했고, 명령과 결과는 4절과 이 절에 적었다.
