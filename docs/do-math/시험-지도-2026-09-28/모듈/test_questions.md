# test_questions

| 항목 | 값 |
|---|---|
| 조각 | `foundation` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_questions.py` (240행) |
| 클래스 / 테스트 | 4 / 14 |
| 시험 대상 제품 코드 | `do_math/questions.py`의 `link`, `user_waits`, `resolve_user`, `validate_extensions`, 간접으로 `resolution_error`, `close`; `do_math/question_engine.py`의 `QuestionEngineMixin._question_view`(모듈 함수 `question_view`), `_record_output_questions`, `_apply_question_resolutions`, `_record_review_questions`, `_user_questions`; `do_math/revisions.py`의 `record_repetition`, `repetition_hold`, `action_repetition_waits`, `continue_repetition`, `action_scope`; `do_math/submission.py`의 `extension_schema`; `do_math/record_schemas.py`의 `RECORDS`; `do_math/governance.py`의 `apply_decision`(`question_answer`), `preserve_source` |
| 사용하는 픽스처 모듈 | `research_fixtures`(`bare_engine`), `record_fixtures`(`domain_governance`) |
| 격리 표지 | 없음 |
| 시작 상태 | 1단(사전 상태에 순수 함수)과, `bare_engine`으로 만든 실제 엔진 객체에 최소 사전 상태를 싣고 질문 믹스인 메서드를 직접 부르는 방식이 섞여 있다. 저장소는 손으로 쓴 대역이나 `create_autospec` 대역이다 |

## 목적

이 모듈에는 docstring이 없다. 시험들이 지키는 계약은 질문 연결(question link)의 규칙이다. 제품은 실행 출력이나 이력에서 나온 질문 하나를 `runtime['question_links']`의 행 하나로 기록한다. 행은 질문 원문을 복사하지 않고, 원천 실행 ID와 원천 필드(JSON 포인터)로 원문을 가리킨다. 행에는 주인(`user`, `research`, `operations`), 영향 대상(`target_ids`), 차단 여부(`blocks`)가 있다. 사용자 질문 가운데 차단하는 것만, 그 대상과 겹치는 작업을 멈춘다(`questions.user_waits`).

이 모듈은 다음을 본다.

- 차단은 명시된 대상에만 걸리고, 연구 계획은 인스턴스 전체를 대상으로 한 질문에만 막힌다.
- 사용자 질문은 사용자 결정으로만 풀리며, 결정이 영향을 준 대상만 풀린다. AI 확장은 사용자 질문을 풀 수 없다.
- 중복 판정은 질문 문장이 아니라 원천의 신원(실행 ID와 필드)으로 한다.
- 질문 원문은 원천 산출물이나 이력의 포인터를 따라 읽힌다.
- 반복 한도 질문은 이력 왕복 뒤에도 읽히고, 범위 있는 계속 결정은 현재 보류 질문만 푼다.
- 제출 확장의 질문 경로(`question_routes`)는 영향 대상의 사용자 대기만 제어한다.

## 모듈 수준 요소

- 행 6: 스킬의 `scripts/` 폴더를 `sys.path` 앞에 넣는 공통 머리.
- 행 239–240: 직접 실행하면 `unittest.main()`.

## QuestionTests (행 12–83)

`unittest.TestCase`를 그대로 상속한다. 클래스 표지, 클래스 속성, 도우미 메서드가 없다.

- `setUp` (행 13–17): 인스턴스 `{"id": "I", "knowledge": {}}`와 과제 `A`, `B`를 가진 런타임을 만든다. `questions.link`로 사용자 차단 질문 둘을 건다. `self.a`는 실행 `E1`의 필드 `output/questions/0`에서 나와 `A`를 막고, `self.b`는 실행 `E2`의 같은 필드에서 나와 `B`를 막는다. 앞의 다섯 시험이 이 상태를 쓴다. 뒤의 두 시험은 이 상태를 쓰지 않고 자기 엔진을 만든다.

### `test_only_the_explicitly_affected_task_waits_and_plan_can_choose_other_tasks` (행 19–25)
- 성질: 차단 질문은 명시된 대상 과제의 작업만 멈추고, 연구 계획은 과제 대상 질문에 막히지 않으며 인스턴스 대상 질문에만 막힌다. 의도 해석은 막히지 않는다.
- 준비: `setUp`의 상태.
- 실행: `user_waits`를 대상 `A`의 작업, 대상 `C`의 작업, 연구 계획에 부른다. 인스턴스 `I`를 대상으로 한 차단 질문을 `E3`에서 더한 뒤 연구 계획과 의도 해석에 다시 부른다.
- 단언: 대상 `A`의 대기가 1개, 대상 `C`는 `[]`, 연구 계획은 `[]`. 인스턴스 질문 뒤 연구 계획의 대기가 참, 의도 해석은 거짓이다.
- 대역: 없음.
- 비고: 제품의 `user_waits`는 연구 계획의 읽기 대상을 비우고 작업 ID·대상·인스턴스 ID만 겹침에 쓰며, `intent_interpretation`, `operational_review`, `maintenance`에는 늘 빈 목록을 돌려준다.

### `test_resolving_one_user_question_preserves_the_other` (행 27–32)
- 성질: 사용자 결정으로 질문 하나를 풀면 다른 질문은 열린 채 남고, 질문의 대상에 영향을 주지 않는 결정은 그 질문을 풀 수 없다.
- 준비: `setUp`의 상태.
- 실행: `questions.resolve_user(runtime, [a의 ID], resolution_ref="D", affected_ids=["A"])`, 이어서 `b`를 `affected_ids=["A"]`로 풀려는 호출.
- 단언: `a`의 `status`가 `"resolved"`, `b`는 `"open"`. 둘째 호출은 `ValueError`(유형만). 제품 메시지는 `"the applied decision does not affect the question target: ..."`다.
- 대역: 없음.

### `test_an_ai_extension_cannot_resolve_a_user_question` (행 34–37)
- 성질: AI 실행의 확장 `question_resolutions`는 사용자 질문을 풀 수 없다.
- 준비: `setUp`의 질문 연결을 담은 연구 계획 문맥. 확장은 `a`를 `resolved`로 처분한다.
- 실행: `questions.validate_extensions({}, extensions, context)`.
- 단언: 오류 목록이 참(비어 있지 않음). 경로나 메시지는 고정하지 않는다. 제품의 `resolution_error`가 `"only distinct open research or operations questions can be resolved by an AI extension"`을 낸다.
- 대역: 없음.

### `test_source_identity_not_equal_text_controls_deduplication` (행 39–43)
- 성질: 같은 원천(실행 ID와 필드)에서 온 질문은 같은 행으로 합쳐지고, 원천이 다르면 다른 행이며, 행은 질문 문장을 담지 않는다.
- 준비: `setUp`의 상태.
- 실행: `a`와 같은 실행·필드·주인·대상·차단으로 `link`를 다시 부른다.
- 단언: 돌려받은 행의 `id`가 `a`와 같다. `a`와 `b`의 ID가 다르다. `a`에 `"text"` 키가 없다.
- 대역: 없음.
- 비고: 이름의 "not equal text"는 `a`와 `b`가 같은 필드 이름(`output/questions/0`)을 쓰지만 실행이 달라 다른 행이 된다는 점과, 행에 문장이 없어 문장으로 합칠 수 없다는 점을 가리킨다. 같은 원천에서 주인이나 대상을 바꾸려 하면 거부되는 경로(`"question source cannot be rerouted silently"`)는 이 모듈에서 단언하지 않는다.

### `test_retry_bypasses_only_the_question_for_its_held_overflow` (행 45–55)
- 성질: 입력 초과 재시도 작업은 자기 초과 보류에 대한 질문 하나만 건너뛰고, 같은 대상의 다른 차단 질문에는 여전히 막힌다. 재시도가 풀리면 두 질문 모두 대기로 돌아온다.
- 준비: `setUp`의 상태에, `A`를 막는 다른 차단 질문 `other`(`E3`)를 더한다. 작업 `AC-1`(`research_work`, 대상 `A`)의 `input_overflow_retry`가 `a`의 ID를 `pending`으로 가리킨다.
- 실행: `user_waits(action, ...)`, 이어서 `input_overflow_retry["state"]`를 `"resolved"`로 바꾸고 다시.
- 단언: 첫 결과의 질문 ID 목록이 `[other의 ID]`, 둘째 결과의 질문 ID 집합이 `{a의 ID, other의 ID}`다.
- 대역: 없음.

### `test_overflow_question_text_follows_its_artifact_pointer` (행 57–70)
- 성질: 원천 산출물을 가리키는 질문 행의 문장은 그 산출물을 읽어 원천 필드 포인터를 따라 얻는다.
- 준비: `read_many`만 가진 내부 클래스 `Store`는 요청된 첫 경로에 `{"resolution_question": {"question": "Choose an authorized larger profile."}}` 바이트를 돌려준다. `bare_engine({"decisions": {}}, head="H", store=Store())`로 엔진을 만들고, 원천 `runtime/artifacts/BA-overflow/input-overflow.json`과 필드 `resolution_question/question`을 가진 열린 사용자 질문 `QU-overflow`를 런타임에 둔다.
- 실행: `reader._question_view()`.
- 단언: 첫 행의 `text`가 `"Choose an authorized larger profile."`이고, `source_status` 키가 없다.
- 대역: 손으로 쓴 저장소 대역 `Store`.
- 비고: 제품의 `question_view`는 원천을 읽지 못하면 `text`를 `None`, `source_status`를 `"unavailable"`로 둔다. 둘째 단언은 그 경로에 빠지지 않았음을 확인한다.

### `test_review_questions_include_pending_research_without_a_result` (행 72–83)
- 성질: 검토 주기의 질문을 기록할 때, 결과가 아직 없는 대기 중 연구 요청의 질문도 포함된다.
- 준비: 주석은 "한 한도 종결은 다른 슬롯의 고정 질문이 아직 대기 중일 때도 출판될 수 있다"고 적는다. `bare_engine(runtime={"question_links": []})`. 검토 주기 `RC-closed`(지식 `KN-reviewed`)의 연구 요청 둘: `EX-a:first`는 `pending`, 질문만 있고 결과 없음. `EX-b:second`는 `unresolved`, 질문과 결과 출력의 질문 하나.
- 실행: `owner._record_review_questions(cycle, "EX-closing")`.
- 단언: 기록된 행의 `origin_field` 목록이 `research/EX-a:first/question`, `research/EX-b:second/question`, `research/EX-b:second/result/output/questions/0` 순서와 같다. 모든 행의 `source_id`가 `"RC-closed"`다.
- 대역: 없음(기본 `StateStore` 대역은 쓰이지 않는다).

## RepetitionQuestionTests (행 86–150)

`unittest.TestCase`를 그대로 상속한다. 클래스 표지, 속성, 설정 훅이 없다.

- `host()` (행 87–103): `bare_engine()`에 인스턴스 `I`(`config={'selection_failure_limit': 1}`, 사용자 원천 `S`, 빈 결정)를 싣는다. 연구 계획 작업 `AC-held`(`repetition_bases={'selection_failure': 'population'}`)를 큐에 두고, 그 작업의 끝난 실행 `EX-first`를 둔다. `revisions.record_repetition`으로 `selection_failure/population` 계열에 `rejected` 반복 하나를 기록한다. 한도가 1이므로 제품이 이력에 `repetition_hold` 행을 더하고, 그 행의 `question` 필드를 가리키는 사용자 질문(원천 종류 `history`)을 건다. `(host, action)`을 돌려준다.

### `test_limit_question_reads_preserved_history_after_roundtrip_and_append` (행 105–121)
- 성질: 반복 한도 질문은 이력 행을 가리키므로, 런타임이 JSON 왕복을 거치고 이력에 무관한 행이 뒤에 붙어도 같은 문장으로 읽힌다. 그 질문 행은 저장 스키마를 만족하고, 보류는 작업을 막는다.
- 준비: `host()`. `revisions.repetition_hold`로 원래 보류 행을 얻는다. 런타임을 `json.dumps`/`json.loads`로 왕복시키고 이력에 `{'kind': 'unrelated_later_event'}`를 붙인다.
- 실행: `host._question_view()`, `host._user_questions()`, `Draft202012Validator(RECORDS['question_links']).validate(...)`, `revisions.action_repetition_waits(...)`.
- 단언: 첫 행의 `text`가 보류 행의 `question`과 같고, `'selection_failure/population'`과 `'1/1'`을 담으며, `source_status` 키가 없다. 사용자 질문 목록이 `[보류 질문]`이다. 스키마 검증이 예외 없이 끝난다. 보류 대기가 참이다.
- 대역: 없음. 원천 산출물이 없으므로 제품의 `question_view`는 저장소를 읽지 않는다.

### `test_scoped_continuation_resolves_only_the_current_hold_question` (행 123–150)
- 성질: 범위 있는 계속 결정은 현재 보류의 질문 하나만 풀고 다른 사용자 질문은 남긴다. 그 뒤 새 거부가 한도에 닿으면 다른 원천 필드의 새 질문이 열린다.
- 준비: `host()`의 첫 질문 `first`. 실행 `EX-other`의 필드 `error`를 원천으로 하는 비차단 사용자 질문을 더하고, 그 실행의 `error`를 `'A separate choice remains.'`로 둔다. 결정 `DC-continue`(사용자, 원천 `S`)는 `repetition_continue` 변경으로 계열·보류 사건 `EX-first`·`allowed_action=revisions.action_scope(action)`을 명시한다.
- 실행: `revisions.continue_repetition(instance, runtime, change, decision)`. 이어서 끝난 실행 `EX-second`를 더하고 같은 계열에 `rejected` 반복을 다시 기록한다.
- 단언: `first`의 `status`가 `'resolved'`, `resolution_ref`가 `'DC-continue'`. 사용자 질문 목록이 `['A separate choice remains.']`. 보류 대기가 거짓. 두 번째 기록 뒤 마지막 질문 행의 `origin_field`가 `first`와 다르고 `status`가 `'open'`, 질문 보기의 마지막 문장에 `'EX-second'`가 들고, 사용자 질문이 2개다.
- 대역: 없음.

## QuestionRouteWireTests (행 153–195)

`unittest.TestCase`를 그대로 상속한다. 표지, 속성, 훅, 도우미가 없다.

### `test_submission_route_controls_only_its_affected_user_wait` (행 154–184)
- 성질: 제출 확장의 질문 경로는 스키마를 통과하고, 기록된 질문은 경로의 `blocks`가 참일 때만 대상의 작업을 막으며, 다른 대상은 막지 않고, 사용자 결정이 대상을 풀면 대기가 사라진다. `blocks`는 불리언이어야 한다.
- 준비: `extension_schema({'role': 'research_work'})`의 `Draft202012Validator`. `blocks`가 없음·거짓·참인 세 경우마다, 질문 0번을 사용자에게 보내고 대상 `A`를 적은 경로를 만든다. 경우마다 `bare_engine({'id': 'I', 'decisions': {}})`에 과제 `A`, `B`와 확장을 가진 실행 `EX-route`를 둔다.
- 실행: 스키마 검증, `questions.validate_extensions(output, extensions, context)`, `owner._record_output_questions({'role': 'research_work', 'target': 'A'}, output, 'EX-route')`, 대상별 `user_waits`, `questions.resolve_user(..., resolution_ref='DC-answer', affected_ids=['A'])` 뒤 다시 `user_waits`. 반복이 끝난 뒤 마지막 경로의 `blocks`를 문자열 `'true'`로 바꾸어 스키마 오류를 모은다.
- 단언: 확장 검증 오류가 `[]`. 기록된 첫 행의 `blocks`가 `blocking is True`와 같다. `A`의 대기 존재 여부가 `blocking is True`와 같고, `B`는 `[]`. 해결 뒤 `A`의 대기가 `[]`. 문자열 `'true'`는 스키마 오류를 하나 이상 낸다.
- 대역: 없음.
- 비고: `subTest(blocking=...)` 세 경우. `blocks`가 없으면 제품의 `_record_output_questions`가 기본값 거짓을 쓴다. 비차단 질문도 사용자 결정으로 풀 수 있음이 세 경우 모두에서 확인된다.

### `test_route_targets_admit_the_records_of_the_record_index` (행 186–195)
- 성질: 질문 경로의 대상은 입력의 `record_index`에 나열된 기록 ID를 받아들이고, 입력이 모르는 ID는 거부한다.
- 준비: 주석은 "과제가 기대는 허가는 역할이 `record_index`로 인용할 수 있는 기록"이라고 적는다. 문맥의 `record_index`는 `{'research/grants': ['GR-1']}`이다. 경로는 대상 `GR-1`의 차단 사용자 질문이다.
- 실행: `validate_extensions`를 두 번. 두 번째는 대상을 `GR-unknown`으로 바꾼다.
- 단언: 첫 번째 오류가 `[]`, 두 번째는 참(비어 있지 않음). 메시지는 고정하지 않는다.
- 대역: 없음.

## GovernanceQuestionTests (행 198–236)

`unittest.TestCase`를 그대로 상속한다. 표지, 속성, 훅, 도우미가 없다.

### `test_question_advice_does_not_block_and_partial_target_answer_does_not_erase_wait` (행 199–205)
- 성질: 비차단 사용자 질문(조언)은 어떤 작업도 막지 않고, 대상 여럿인 차단 질문에 일부 대상만 답하면 질문은 열린 채 나머지 대상만 남는다.
- 준비: 빈 런타임에 인스턴스 `I`를 대상으로 한 비차단 사용자 질문, 이어서 `A`, `B`를 대상으로 한 차단 사용자 질문.
- 실행: 연구 준비 작업에 `user_waits`, 이어서 차단 질문을 `affected_ids=["A"]`로 `resolve_user`.
- 단언: 대기가 `[]`. 차단 질문의 `status`가 `"open"`, `unresolved_target_ids`가 `["B"]`.
- 대역: 없음.

### `test_question_mixin_publishes_advice_without_global_wait_and_resolves_atomically` (행 207–230)
- 성질: 질문 믹스인은 비차단 경로의 질문을 전역 대기 없이 출판하고, AI 확장의 질문 해결은 원자적으로 적용되어 하나라도 틀리면 아무 질문도 풀리지 않는다.
- 준비: `bare_engine()`에 인스턴스 `I`와 연구 계획 실행 `E`(확장에 인스턴스 대상 비차단 사용자 경로)를 둔다.
- 실행:
  1. `h._record_output_questions({"role": "research_plan"}, {"questions": ["Optional priority?"]}, "E")` 뒤 연구 계획의 `user_waits`.
  2. 연구 질문 `one`(주인 `research`, 대상 `I`)을 건다. 실행 `E`의 확장을 `one`의 해결과 없는 ID `"missing"`의 해결 두 행으로 바꾼다. 증거 경로는 `runtime/artifacts/BA-answer/answer.md`다. 저장소를 `create_autospec(ResearchRepository, instance=True)`로 바꾸고, `read_many` 부수 효과가 저장소 계약(주석: `"omit"`은 없는 경로를 빼고, `"raise"`는 묶음 전체를 실패시킨다)에 맞게 그 증거 하나만 돌려주거나 `GitStateStoreError`를 던지게 한다.
  3. `h._apply_question_resolutions("E")`.
- 단언: (1) 대기가 `[]`. (3) `ValueError`이고 메시지가 `"only distinct open research or operations questions"`에 맞는다. 이어서 `one`의 `status`가 `"open"` 그대로다.
- 대역: `ResearchRepository`의 `create_autospec` 대역과 `read_many` 부수 효과 함수.
- 비고: 주석은 "산출물 증거는 런타임 가족이 아니라 엔진 저장소 읽기로 해석된다"고 적는다. 제품은 질문 연결의 깊은 사본에서 해결을 적용하고 모두 성공한 뒤에만 런타임에 쓰므로, 첫 행이 성공해도 둘째 행의 실패로 `one`이 열린 채 남는다.

### `test_actual_answer_preserves_other_affected_targets` (행 232–236)
- 성질: 거버넌스 경로의 실제 사용자 답(`question_answer` 결정)은 답이 다룬 대상만 풀고 다른 영향 대상은 남긴다.
- 준비: `domain_governance()`와 과제 `A`, `B`. `A`, `B`를 막는 사용자 차단 질문 `q`.
- 실행: `gov.apply_decision(i, rt, {"kind": "question_answer", "text": "Answer A", "target_ids": ["A"], "resolves_questions": [q의 ID]}, source_ref="S")`.
- 단언: 갱신된 런타임의 첫 질문 행의 `unresolved_target_ids`가 `["B"]`다.
- 대역: 없음.
- 비고: `test_question_advice_does_not_block_and_partial_target_answer_does_not_erase_wait`가 `resolve_user`를 직접 불러 본 성질을, 이 시험은 거버넌스 결정 경로로 본다.

## 관계

- 같은 제품 기능을 다른 층에서 검사하는 모듈: `user_waits`는 `test_relation_dependencies`(관계의 간접 끝점)와 `test_governance`에서도 불린다. 반복 계열과 보류는 `test_task_contracts`의 `RepetitionLineageTests`가 계열 계산 쪽을 본다. 질문 원문 보기(`_question_view`, `_user_questions`)는 이 모듈 밖에서 `test_question_flow`, `test_review_research`가 쓴다. 원문에 `question_links`가 나오는 시험 모듈은 이 모듈을 포함해 16개다.
- 픽스처 의존: `research_fixtures.bare_engine`, `record_fixtures.domain_governance`.
- 이 모듈에만 있는 도우미: `QuestionTests.setUp`, `RepetitionQuestionTests.host`, 시험 안의 내부 클래스 `Store`와 내부 함수 `read_many`.
- 겹치거나 보완하는 시험: 부분 대상 해결은 `GovernanceQuestionTests`의 첫 시험(직접 호출)과 셋째 시험(거버넌스 결정)이 두 층에서 본다. AI 확장의 해결 금지는 `test_an_ai_extension_cannot_resolve_a_user_question`(제출 검사)과 `test_question_mixin_publishes_advice_without_global_wait_and_resolves_atomically`(적용 단계)가 두 층에서 본다.
