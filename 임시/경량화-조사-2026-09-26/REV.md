# REV — AI 산출물의 제출과 검토

조사 기준: `C:/math/임시/경량화-조사-2026-09-26/기준.md`. 모든 좌표는 2026-09-26 작업 트리(HEAD `8d2ffd0`) 기준이다. 경로는 따로 적지 않으면 `C:/math/.claude/skills/do-math/scripts/do_math/` 아래 파일이다.

이 영역에서 AI 역할은 생산자, 실행기는 수신자다. 수신 검사는 세 층으로 나뉜다.

1. **제출 검사**(`submission.check_submission`). 생산자의 `input/tools/check_submission.py`와 중앙 수신(`seal_submission`)이 같은 함수를 실행한다.
2. **적용 검사**. 엔진이 봉인된 산출을 적용하는 도메인 함수(`review_cycle.accept_*`, `review_engine._apply_*`, `task_scope.apply_*`, `decision_engine._apply_*`) 안에 있다.
3. **봉인 재구성 검사**(`validate_sealed_review` 등).

적용 단계에서 예외가 나면 `integration.apply_bundles`가 그 묶음을 `integration.application` issue로 생산자에게 돌려보낸다(`integration.py:494-515`, `next_owner: "producer"`). 그 결과 생산자 재실행이 생긴다. 게다가 `--preview`는 적용 단계의 사유 문장을 감추고 "Candidate cannot pass this stage…"라는 일반 문장만 준다(`submission.py:1153-1163`). 따라서 1층에 없고 2층에만 있는 조건은, 생산자가 미리 알 수 없는 반려·재시도 경로가 된다.

공유 검사를 둘 수 있는 위치에는 제약이 있다. 생산자에게 배포되는 검사 코드는 `engine.py`와 `*_engine.py`를 뺀 모듈뿐이다(`submission.py:1343-1345`). 그러므로 생산자와 공유할 검사 함수는 `review_cycle`, `submission`, `task_scope`, `task_contracts` 같은 비엔진 모듈에 두어야 한다. 기억 L-0020의 「생산자가 규범을 지킬 수 있는 경로」도 같은 설계를 기록한다(`기억/layer3/L-0020.md:53`).

## 1. 읽은 범위

전문을 읽은 파일:

- `C:/math/임시/경량화-조사-2026-09-26/기준.md` (120행)
- `C:/math/docs/do-math/검사-경량화-이음새-계약.md` (159행)
- `submission.py` (1609행)
- `contracts.py` (347행)
- `task_contracts.py` (277행)
- `task_scope.py` (480행)
- `review_cycle.py` (1222행)
- `review_engine.py` (1274행)
- `review_policy.py` (120행)
- `decision_engine.py` (208행)
- `C:/math/.claude/skills/do-math/계약/작업-계약-검토.md` (143행)
- `C:/math/.claude/skills/do-math/계약/동일성-검토.md` (107행)
- `C:/math/.claude/skills/do-math/references/과제-착수조건.md` (57행)
- `C:/math/.claude/skills/do-math/scripts/tests/test_review_scope_wire.py` (135행)

일부만 읽은 파일(이음새 판정에 필요한 범위):

- `engine.py`: 680-724, 1206-1217, 1662-1664, 1940-1942, 1955-1984, 2105-2169, 2195-2254, 2290-2489, 3324-3339(grep), 4695-4750
- `integration.py`: 41-58, 205-212, 466-545
- `planning.py`: 180-393
- `context_store.py`: 378-407
- `knowledge.py`: 455-482, 695-719
- `file_io.py`: 146-153
- `repository.py`: 103-114
- `record_schemas/schemas.py`: 112-143
- `계약/후보-준비.md`: 115-184
- `scripts/tests/test_walkthrough_repairs.py`: 225-264
- `기억/색인.md`: layer-3 절
- `기억/layer3/L-0020.md`: grep으로 관련 행만

사용한 전수 검색식(ripgrep, `scripts/do_math` 또는 스킬 전체):

- `_review_schema\(|_review_research_schema\(|install_tools\(|action_schema\(|role_review`
- `action_schema\(|SCOPE_ASSESSMENT|stage_schema\(|research_schema\(` (테스트 포함)
- `_enqueue\(\s*['"]identity_review|role['"]:\s*['"]identity_review['"]`
- `contract_review_decision|validate_plan_submission|validate_withdrawal_scope|validate_scope_assessment|contract_check_errors|validate_visible_output|validate_research_reference|task_candidate_record`
- `contract_checks` (테스트 제외)
- `blocked_actions` (review 모듈 제외)
- `_apply_action_resolutions|_apply_task_plan\(|apply_task_dispositions\(|_apply_review_research\(|_defer_review_for_research\(|_apply_identity_review\(`
- `validate_sealed_review\(|validate_review_independence\(|validate_review_execution\(`
- `read_sealed_submission\(|summarize_snapshot_checks\(|summarize_checks\(|preview_submission\(|seal_submission\(|check_submission\(`
- `_admit_review_execution|_prepare_review_context|_record_review_input\(|scope_executions_used`
- `0123456789abcdef`
- `PROFILE_REF\s*=|def profile_ref\b`
- `validate_task_contract\(`
- `usable_as_k|http_status|stop_phase|…|'record_field_equals'`
- `과제-착수조건|EXPOSED_FIELDS|minimum_scope_executions|U\+2N|CONTRACT_REVIEW_ITEMS` (tests)
- `def json_digest|def canonical_json|def exact_content_hash`

## 2. 후보

#### REV-01: 검토 단계 출력의 수제 스키마 검사기가 jsonschema와 다르게 판정한다
- 유형: 이음새중복
- 위치: `review_cycle.py:85-106`(`_validate`), 호출 `review_cycle.py:629, 637, 676, 799, 827, 890`, 스키마 `review_cycle.py:48-82`(`stage_schema`)·`617-623`(`research_schema`), 생산자·수신 제출 검사 `submission.py:384-395`(`_schema_issues`, jsonschema Draft 2020-12), 보충 조사 생산자 검사 `submission.py:910-922`, 적용 `review_engine.py:1218-1245` → `review_cycle.accept_research_result`
- 현상: 같은 `stage_schema`·`research_schema`를 두 검사기가 따로 해석한다. 제출 검사는 jsonschema로, 적용 검사는 `_validate`로 판정한다. 둘은 문자열 `minLength`를 다르게 본다. jsonschema는 문자 수를 세고, `_validate`는 `value.strip()`의 길이를 센다(`review_cycle.py:103-104`). 읽기 전용 실측 결과는 다음과 같다.
  - 명령: `python -c "…jsonschema.Draft202012Validator(r.research_schema()).iter_errors(o)…; r._validate(o, r.research_schema())"`, `summary=' '`
  - 결과: `jsonschema errors: []`, `_validate: output.summary: empty string`

  동일성 검토 자리는 생산자 검사가 `validate_visible_output`에서 `_validate`를 부르므로 이 차이를 잡는다(`submission.py:904` → `review_cycle.py:833`, `799`). 그러나 검토 보충 조사(`supplemental_research`+`review_cycle_id`)의 생산자 검사는 jsonschema와 `answered` 규칙만 본다(`submission.py:910-922`). 그래서 공백 문자열을 담은 출력이 생산자 검사와 중앙 봉인을 통과한 뒤, `_apply_review_research` → `accept_research_result`의 `_validate`에서 ValueError를 내고 적용 단계 반려로 돌아간다.
- 제안:
  - `review_cycle`의 문자열 스키마(`stage_schema`의 `string`, `research_schema`의 `text`, `defer_for_research`의 요청 spec `review_cycle.py:634-635`)에 `"pattern": r"\S"`를 더한다. `contracts.TEXT`(`contracts.py:120`)나 `submission.TEXT`(`submission.py:32`)와 같은 형태다.
  - `_validate`를 지우고 jsonschema 검사(`jsonschema.Draft202012Validator(schema).validate`를 ValueError로 감싼 한 줄 도우미)로 바꾼다.
  - 정본은 `review_cycle`의 스키마 하나가 되고, 생산자의 jsonschema 검사와 적용 검사가 같은 정의를 쓴다.
- 동작: 변경. 공백만 있는 문자열이 생산자 검사 단계에서 `schema.pattern`으로 반려된다. 모델이 받는 스키마에 `pattern`이 추가된다. `_validate`의 오류 문구(`output.summary: empty string` 등)가 jsonschema 문구로 바뀐다.
- 실익: `_validate` 22행 삭제(측정). 적용 단계 반려 한 경로 제거(보충 조사 공백 문자열). 같은 스키마를 두 해석기로 읽는 일이 없어져, 이후 스키마에 키워드를 추가해도 해석 차이가 생기지 않는다. `_validate`는 `const`·`pattern`·`minItems`·`anyOf`를 지원하지 않는다(`review_cycle.py:85-106`). REV-07의 정밀 scope 스키마를 이 경로에 넣으려면 이 교체가 선행조건이다.
- 위험과 보호: CLI의 스키마 수용성. 기억 L-0020 98행에 Claude CLI가 `$schema`·`x-contract-id`를 거부한 기록이 있고, `pattern`은 `contracts.SCHEMAS`에서 이미 전달되고 있다(`contracts.py:120, 131`). 덮는 테스트는 `test_review_cycle.ReviewCycleTests.test_stage_schema_is_specific`, `test_review_research.*.test_wrong_question_and_partial_answer_are_not_accepted`, `test_review_scope_wire.ScopeWireTests.*`다. 공백 문자열 사례를 직접 덮는 테스트는 없음.
- 확신: 높음 — 판정 차이를 실측으로 재현했고, 보충 조사 경로에 `_validate`가 없음을 원문으로 확인함.
- 다른 영역: `engine.py`(`_response_schema` 2208-2247), `preflight.py:127-129`(`stage_schema`·`research_schema`를 직접 사용)

#### REV-02: 보충 조사의 `answered` 규칙과 검토의 잠정 반환 규칙이 각각 두 벌로 적혀 있다
- 유형: 이음새중복
- 위치:
  - `answered` 규칙: `submission.py:912-913`과 `review_cycle.py:681-682`
  - 잠정 반환 규칙: `review_cycle.py:826-832`(`validate_visible_output`의 `requesting_research` 분기)와 `review_cycle.py:628-632`(`defer_for_research`)
  - 조사 요청 고유성: `submission.py:835-839`와 `review_cycle.py:636-640`
- 현상: 두 조건이 생산자 경로와 적용 경로에 각각 따로 적혀 있다.
  - "answered면 scope_complete·evidence_refs가 있고 questions가 비어 있어야 한다"는 생산자 경로(`submission.py`)와 적용 경로(`accept_research_result`)에 문장까지 비슷하게 따로 있다.
  - "조사를 요청하는 initial/judge 반환은 `unresolved`여야 하고 proposal_digest가 일치해야 한다"도 `validate_visible_output`과 `defer_for_research`에 따로 있다.

  한쪽만 고치면 생산자 검사를 통과한 출력이 적용에서 반려된다.
- 제안: `review_cycle`에 두 순수 함수를 둔다.
  - `research_answer_errors(output)`(또는 raise형): `submission.py:912-913`과 `accept_research_result`가 부른다.
  - `validate_provisional(proposal_digest, action, output)`: `validate_visible_output`의 분기와 `defer_for_research`가 부른다.

  `review_cycle`은 배포 모듈이므로 생산자도 같은 함수를 실행한다.
- 동작: 보존
- 실익: 중복 조건 약 10행. 조건 변경 때 두 곳 동기화가 필요 없다(추정).
- 위험과 보호: `test_review_research.*.test_wrong_question_and_partial_answer_are_not_accepted`, `test_review_research.*.test_producer_and_receiver_reject_an_unassigned_used_source`, `test_review_cycle.*.test_initial_barrier_and_blindness`
- 확신: 높음 — 두 쌍 모두 원문에서 같은 조건임을 확인함.
- 다른 영역: 없음

#### REV-03: 보충 조사 원자료 참조의 허용 규칙이 생산자 검사와 적용 코드에 따로 구현돼 있다
- 유형: 이음새중복
- 위치:
  - 생산자·봉인 쪽: `submission.py:540-552`(`validate_research_reference`)와 `submission.py:497-511`(`_validate_reference`의 `proposal:` 좌표 탐색)
  - 적용 쪽: `review_engine.py:1063-1098`(`_research_source_spec`), 호출 `review_engine.py:1112-1116`
- 현상: 허용 규칙이 두 번 구현돼 있다.
  - `proposal:<경로>` 좌표를 따라 내려가는 코드가 `submission.py:505-511`과 `review_engine.py:1068-1072`에 거의 같은 형태로 두 번 있다.
  - 지식 ID 허용 범위가 다르다. 생산자는 문맥의 `knowledge_catalog` ID를 허용하고(`submission.py:543`), 적용은 `self.instance['knowledge']` 전체를 허용한다(`review_engine.py:1094`).
  - 자기 자리 기록 참조는 생산자가 `role_review.source_refs`로(`submission.py:546`), 적용이 `review_inputs`의 `request.source_refs`와 자리 대조로(`review_engine.py:1078-1082`) 판정한다.

  적용에서 거부되면 `_defer_review_for_research`의 ValueError가 적용 단계 반려로 돌아간다. 동일성 검토 문맥의 `knowledge_catalog`가 인스턴스 지식 전체와 같은지는 미확인이다(`context_store.py:386`이 `role_review`만 직접 키로 두며, 카탈로그 구성은 읽지 않음).
- 제안: `review_cycle`(배포 모듈)에 순수 분류 함수 `classify_research_source(reference, *, proposal, issues, own_source_refs, supplied_sources, knowledge_ids)`를 둔다. 반환값은 `('proposal', path) | ('issue', id) | ('transcript', ref) | ('source', row) | ('knowledge', id)`이고, 허용되지 않으면 ValueError다.
  - `submission.validate_research_reference`는 이 함수로 판정만 한다.
  - `_research_source_spec`은 같은 함수의 분류 결과를 받아 바이트 읽기·봉인만 수행한다.
  - `knowledge_ids`의 정의(카탈로그인지 인스턴스 전체인지)는 이 함수의 인자로 한 곳에서 정한다.
- 동작: 변경. 지식 ID 허용 범위를 하나로 정하면, 지금 두 쪽 판정이 갈리는 참조의 결과가 한쪽으로 바뀐다.
- 실익: 좌표 탐색 중복 6행과 허용 규칙 이원화 제거. 적용 단계 반려 경로 하나 제거(추정).
- 위험과 보호: `test_review_research.*.test_producer_and_receiver_reject_an_unassigned_used_source`, `test_review_research.*.test_all_fixed_questions_return_before_resuming_the_deferred_slot`, `test_review_research.*.test_corrupt_fixed_research_source_is_a_local_diagnostic_on_slot_resume`
- 확신: 중간 — 규칙의 이중 구현은 확실하다. 실제로 갈리는 입력이 운전에서 생기는지는 카탈로그 구성을 확인하지 않아 미확인이다.
- 다른 영역: `context_store.py`(역할 문맥), `input_basis.aliases`

#### REV-04: 검토자 독립성(작성자 계보) 검사가 네 형태로 흩어져 있고, 실시간 수락과 봉인 재구성의 기준이 다르다
- 유형: 이음새중복
- 위치:
  - 실시간 수락: `review_engine.py:966-967, 990-995`(`_accept_identity_review`), `review_cycle.py:904-908, 924-929`(`accept_result`), `review_engine.py:1111`(`_defer_review_for_research`), `review_engine.py:1225-1230`(`_apply_review_research`)
  - 추이 계보 검사: `review_cycle.py:183-205`(`validate_review_independence`)
  - 추이 검사 호출: 재심사일 때만 `review_engine.py:291-293, 975-976`, 봉인 재구성 `review_cycle.py:359`
- 현상: 같은 판정이 여러 형태로 구현돼 있고, 기준이 서로 다르다.
  - 일반 검토의 실시간 수락은 실행의 `continuation_of`·`context_origin` 한 단계만 작성자 집합과 대조한다. 봉인 재구성(`validate_sealed_review` → `validate_review_execution` → `validate_review_independence`)은 계보를 추이적으로 따라간다.
  - 작성자 집합의 출처도 다르다. 엔진은 `cycle['producer_execution_ids']`를 쓰고, `accept_result`는 `cycle['proposal']['producer_execution_ids']`를 쓴다. 그런데 일반 제안의 `proposal`에는 이 필드가 없다(`review_engine.py:24-25`의 `_PROPOSAL_FIELDS`). 그래서 `accept_result`의 작성자 검사는 재심사 제안에서만 실효가 있다(`review_engine.py:149`).
  - 단계적 검토는 실시간 수락 뒤 신뢰 전환 활성화 때 `validate_sealed_review`를 받는다(`knowledge.py:711`). 따라서 두 단계 이상 떨어진 계보로 작성자 문맥을 이어받은 검토자는 실시간으로 수락됐다가, 검토 전체가 끝난 뒤 늦게 거부될 수 있다.
- 제안: `review_cycle`에 `review_authors(cycle)`(cycle과 proposal의 작성자 집합의 합집합)를 두고, 모든 수락 지점이 `validate_review_independence(cycle, runtime, execution_id, action)` 하나를 부르게 한다. 그런 다음 엔진과 `accept_result`의 한 단계 대조 코드를 지운다. 이 검사는 생산자가 고칠 수 없는 배정 사실이므로 수신 전용으로 둔다.
- 동작: 변경. 일반 검토도 실시간 수락에서 추이 계보를 검사한다. 이제까지 수락되던 간접 계승 검토자가 수락 시점에 거부된다.
- 실익: 중복 대조 약 15행 제거. 실시간 수락과 재구성의 판정이 일치해 늦은 거부 경로가 사라진다. 계보 순회 비용은 실행 기록 수에 비례하는 dict 조회라 추가 비용은 작다(추정).
- 위험과 보호: `test_review_cycle.*.test_manifest_peer_and_judge_origin_checks`, `test_review_cycle.*.test_proposal_mutation_and_execution_identity`. 일반 검토의 추이 계승을 덮는 테스트는 없음.
- 확신: 중간 — 기준 차이는 원문으로 확인했다. 실제 운전에서 두 단계 이상의 계승이 생기는지는 미확인이다.
- 다른 영역: `knowledge.py`(재구성 소비), `governance.validate_independent_execution`

#### REV-05: 검토 자리 키 `"stage:round:slot"` 형식을 엔진이 문자열 리터럴로 다시 적는다
- 유형: 이음새중복
- 위치: 정본 `review_cycle.py:480-481`(`_key`). 재작성 `review_engine.py:590, 627, 639, 806`. 복합 키 `review_engine.py:41-42`(`_pending_key`)
- 현상: `cycle['results']`, `blocked_actions`, `replacement_actions`의 키를 `review_cycle._key`가 만든다. 그런데 `review_engine`은 이를 import하지 않고, 같은 형식을 f-string으로 네 번 다시 적는다. 한쪽 형식이 바뀌면 조회가 조용히 빗나간다.
- 제안: `review_cycle._key`를 공개 이름(예: `slot_key`)으로 바꾸고, `review_engine`의 네 곳과 `_pending_key`가 그 함수를 쓴다.
- 동작: 보존
- 실익: 형식 중복 5곳 제거.
- 위험과 보호: `test_review_cycle.*.test_round_three_reuses_slots_without_execution_keys_colliding`, `test_review_research.*` 전반
- 확신: 높음 — 원문 대조.
- 다른 영역: `record_schemas/domains.py:481`(`blocked_actions` 저장 형식), `test_review_scope_wire.py:25`(`'RC-fixture:scope:1:scope'` 리터럴)

#### REV-06: 기록(transcript)의 직렬화와 해시를 쓰는 쪽과 검증하는 쪽이 다른 표현으로 만든다
- 유형: 이음새중복
- 위치:
  - 직렬화 복제: `review_cycle.py:27-28`(`_bytes`), 정본 `file_io.py:146-153`(`json_digest`)
  - 기록할 때 `hashlib.sha256(_bytes(...))`를 쓰는 곳: `review_cycle.py:1046, 1056`(manifest 작성), `review_cycle.py:307-308`, `review_engine.py:676-680, 919, 1097-1098, 1189`
  - 검증할 때 `json_digest(...)`를 쓰는 곳: `review_cycle.py:399, 1170`
  - manifest 행 판정의 이중 구현: `review_cycle.py:395-400`(`_verified_transcript`)와 `review_cycle.py:1165-1170`(`validate_transcript`)
- 현상: `_bytes`의 인자(`ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False`, UTF-8)는 `json_digest`의 직렬화와 같다. 그래서 `sha256(_bytes(x)) == json_digest(x)`이다. 문제는 manifest를 쓰는 쪽은 앞의 식을, 검증하는 쪽은 뒤의 식을 쓴다는 점이다. `json_digest`의 직렬화가 바뀌면, 저장된 기록이 모두 `transcript bytes changed`로 판정된다. 이음새 계약 2.1은 JSON digest 정본을 `file_io`로 정했다. `_bytes`는 digest 도우미가 아니라 직렬화기지만, 실제로는 그 정본을 복제한다.
- 제안:
  - `file_io`에 `json_bytes(value)`(압축 정렬 직렬화)를 두고, `json_digest`를 `sha256(json_bytes(value))`로 정의한다.
  - `review_cycle._bytes`와 `review_engine`의 `_transcript_bytes` 별칭을 `json_bytes`로 바꾸고, 해시 자리는 모두 `json_digest`로 쓴다.
  - manifest 행 일치 판정은 `review_cycle` 안의 한 술어로 합치고 `_verified_transcript`와 `validate_transcript`가 함께 쓴다.
- 동작: 보존. 바이트와 해시 값이 같다.
- 실익: 직렬화 정의 1곳과 manifest 술어 1곳 제거. 쓰는 쪽과 검증하는 쪽이 한 정의를 공유한다.
- 위험과 보호: `test_review_cycle.*.test_transcript_restore_reference_and_integrity`, `test_review_cycle.*.test_incomplete_transcript_manifest_is_a_local_restoration_error`
- 확신: 높음 — 두 직렬화 인자를 원문으로 대조함.
- 다른 영역: `file_io.py`(커널, 이음새 계약 2.1)

#### REV-07: 검토 역할의 출력 스키마를 두 곳에서 만들고, 운영 경로는 정밀한 scope 스키마를 전달하지 않는다
- 유형: 이음새중복
- 위치:
  - `contracts.py:205-224`(`action_schema`의 scope 분기 211-215와 `review_cycle_id` 분기 219-224)
  - `contracts.py:151-156`(`SCOPE_ASSESSMENT`)
  - 운영 경로 `engine.py:2208-2212`(`_response_schema`) → `review_engine.py:574-580`(`_review_schema`), `review_engine.py:1161-1166`(`_review_research_schema`)
  - `review_cycle.py:58-59`(`scope_assessment={"type":"object"}`)
  - 의미 검사 `review_policy.py:69-120`
  - 산문 `계약/동일성-검토.md:13-17`
- 현상: 같은 출력 형태가 여러 곳에 따로 정의돼 있다.
  - 엔진은 `review_cycle_id`가 있는 동일성 검토와 보충 조사를 `_review_schema`·`_review_research_schema`로 보낸다. 그래서 `action_schema`의 두 분기는 운영 경로에서 도달하지 않는다. 전수 검색에서 이 분기를 부르는 곳은 테스트뿐이었다(`test_review_scope_wire.py:52`, `test_redesign_CONTRACTS.py:626`, `test_contracts.py:44`).
  - 모델이 실제로 받는 scope 스키마의 `scope_assessment`는 `{"type":"object"}`뿐이다. 정밀 형태는 산문(동일성-검토.md 13-17)과 `validate_scope_assessment`에만 있다.
  - 테스트가 "installed wire"라 부르는 `SCOPE_ASSESSMENT`는 `selected_profile_ref`를 필수 객체로 요구한다(`contracts.py:154`). 소비자 `validate_scope_assessment`는 `None`을 허용한다(`review_policy.py:102-103`). 테스트가 검증하는 계약과 실제 소비자 계약이 다르다.
- 제안: 검토 출력 스키마의 정본을 `review_cycle.stage_schema`와 `research_schema` 하나로 한다.
  1. `SCOPE_ASSESSMENT`를 `stage_schema('scope')`로 옮기고, `selected_profile_ref`를 `anyOf [null, PROFILE_REF]`로 소비자와 맞춘다.
  2. `_review_schema`는 `stage_schema`에 digest `enum`만 덧붙인다.
  3. `action_schema`의 두 분기와 `SCOPE_ASSESSMENT`를 지운다.
  4. `test_review_scope_wire`가 엔진이 실제로 쓰는 생성기(`_review_schema`)를 검사하게 한다.

  REV-01의 jsonschema 교체가 선행조건이다.
- 동작: 변경. scope 단계의 모델이 정밀한 `scope_assessment` 스키마를 받고, 형태 오류가 제출 검사의 `schema.*` issue로 정확한 좌표와 함께 반환된다.
- 실익: 운영 경로에서 도달하지 않는 분기 약 12행 삭제. 스키마 정의가 셋에서 하나로 준다. scope 단계 반려의 좌표가 정확해진다.
- 위험과 보호: `preflight.py:127`의 스키마 수용 검사가 새 scope 스키마를 받아들이는지, CLI의 `anyOf`·`const` 수용은 미확인이다(L-0020 98행에 CLI의 스키마 거부 전례가 있음). 덮는 테스트는 `test_review_scope_wire.ScopeWireTests.*`, `test_contracts.*.test_profile_references_use_the_sealed_provider_identity`, `test_redesign_CONTRACTS.py:626` 부근 테스트다.
- 확신: 높음(사실) / 중간(정본 위치) — 운영 경로의 스키마 생성 위치는 원문으로 확인했다. CLI 수용성은 확인하지 않았다.
- 다른 영역: `engine.py`, `preflight.py`, 테스트 3개 모듈

#### REV-08: `action_resolutions`의 적용 조건 가운데 고정 입력으로 판정할 수 있는 것을 생산자가 검사하지 못한다
- 유형: 생산자자기확인부재
- 위치: 생산자·봉인 `submission.py:626-633`. 적용 `decision_engine.py:10-32`. 문맥 투영 `engine.py:2116-2119, 2124-2127, 2154-2157`
- 현상: 생산자 검사는 두 가지만 본다. `action_id`가 문맥 `blocked_actions`에 있는지, 증거가 `current`이거나 제공된 ID인지다. 적용은 여기에 세 조건을 더 요구한다.
  1. 대기 종류가 `output_validation`·`execution_failure`일 것(15-16행)
  2. 증거 실행이 같은 판단 범위(role·stage·slot·round·review_cycle_id 등)의 수락된 실행일 것(20-24행)
  3. 필요한 개정 해소가 있을 것(29-32행)

  이 가운데 1은 문맥에 이미 있다. `blocked_actions` 행에 `kind`가 들어 있고, 대기 행동 전체(`formal_stopped`, `review_initialization` 등)가 투영된다(`engine.py:2154-2157`). 그런데도 생산자는 이를 검사하지 않는다. 그 결과 잘못된 종류의 대기를 해소하겠다는 주장이 봉인을 통과하고 적용 단계에서 반려된다. 같은 투영 코드가 엔진에 세 벌 있다.
- 제안:
  - `submission`에 `action_resolution_errors(claim, blocked_row, own_action)`을 두어 종류 조건과, `current` 증거일 때의 role·target 일치를 판정한다. 생산자 검사와 `_apply_action_resolutions`가 함께 부른다.
  - 이미 끝난 다른 실행의 수락 여부·전제 변화 같은 적용 시점 현재성은 수신에 남긴다.
  - 문맥 투영은 한 도우미로 만들고, 판정에 필요한 필드(`stage`, `slot`, `round`, `review_cycle_id`, `revision_targets`)를 담는다.
- 동작: 변경. 잘못된 해소 주장이 적용 단계 대신 생산자 검사와 봉인 단계에서 정확한 좌표로 반려된다.
- 실익: 적용 단계 반려와 재실행 경로 하나 축소. 엔진 투영 중복 2벌 제거.
- 위험과 보호: `test_decision_basis.py`, `test_redesign_ENGINE.py`, `test_research_recovery.py`에 `action_resolutions` 사용 테스트가 있다(grep). 종류 조건의 생산자 검사를 덮는 테스트는 없음.
- 확신: 중간 — 조건 차이와 문맥 필드는 확인했다. 잘못된 종류를 주장하는 사례가 실제로 발생한 기록은 확인하지 않았다.
- 다른 영역: `engine.py`(`_context`의 역할 분기)

#### REV-09: 완료 판정 증거로 허용되는 ID 집합을 생산자와 수신자가 서로 다르게 정의한다
- 유형: 이음새중복
- 위치: 생산자·봉인 `submission.py:530-537`(`assessment_reference_ids`), 사용 `submission.py:613-617`, 원천 `submission.py:442-477`(`_reference_ids`). 적용 `task_scope.py:409, 416-417`(`apply_task_assessments`). 기록 가족 `planning.py:331-341, 369-382`
- 현상: 생산자는 문맥에 나온 ID 전체를 허용한다. 여기에는 `events`, `question_links`, `observation_facts`, `user_inputs`, `self_check_obligations`, `governance_records`, `delegations`, `review_followups`, `external_rejections` 같은 비기록 ID가 들어 있다(`submission.py:461-466`, 457). 수신자는 `planning._records`가 다루는 기록 가족(`RECORD_FAMILIES`, 21종)의 ID와 과제 결과 ID만 허용한다. 따라서 계획 역할이 관찰 사실 ID나 질문 연결 ID를 완료 증거로 인용하면, 생산자 검사는 통과하고 적용 단계에서 `disposition evidence is not in the current input`으로 반려된다.
- 제안: 운영 점검의 `admissible_basis_refs` + `require_basis_refs` 선례(`submission.py:731-732`)를 따른다.
  - 엔진이 계획·운영 점검 문맥에 `admissible_evidence_ids`(현재 기록 ID ∩ 제공된 입력 + 과제 결과 ID)를 넣는다.
  - `task_scope`(배포 모듈)에 `require_evidence_refs(refs, admissible)` 하나를 두고, 생산자 검사와 `apply_task_assessments`가 같은 함수로 판정한다.
- 동작: 변경. 허용 집합이 하나로 정해진다. 생산자는 비기록 ID 인용을 제출 전에 반려받는다.
- 실익: 적용 단계 반려 경로 하나 제거. 허용 규칙의 두 정의가 하나로 준다.
- 위험과 보호: `test_redesign_ENGINE.*.test_operational_task_disposition_uses_authoritative_item_assessment`, `test_connection_repairs.py`(`completion evidence requires` 문구 사용). 비기록 ID 사례를 덮는 테스트는 없음.
- 확신: 중간 — 두 정의의 차이는 원문으로 확인했다. 운전 빈도는 미확인이다.
- 다른 영역: `engine.py`(계획·운영 점검 문맥), `planning.py`

#### REV-10: 완료 판정 적용의 판정자 조건 일부는 고정 입력으로 판정할 수 있는데 수신에만 있다
- 유형: 생산자자기확인부재
- 위치: `task_scope.py:402-403`(계약 작성자 배제), `task_scope.py:412-415`(`fulfilled`의 판정자 또는 전문 판정), `task_scope.py:420-430`(이전 수령 과제 조건). 생산자 쪽 공유 검사 `task_contracts.py:122-168`(`validate_item_dispositions`, 형태만 검사)
- 현상: 계획 역할은 자기 `action.role`과 과제 계약의 `completion_obligations[].judges`를 모두 입력으로 받는다. 그런데 "판정자가 아니면 해당 가족(FR·IA·GJ)의 증거를 인용해야 한다"는 조건은 적용 단계에서만 판정된다. 전문 판정의 현재 유효성(`designated_judgment`)은 인스턴스 상태에 달려 있으므로 수신에 남아야 한다. 역할이 판정자 목록에 없는데 증거에 해당 가족의 ID가 하나도 없다는 사실은 입력만으로 알 수 있다.
- 제안: `task_contracts`에 `judge_coverage_errors(role, task, assessment, cited_families)`를 둔다. 인용 ID의 가족은 문맥 카탈로그로 판정한다. 생산자 검사가 이 함수를 부르고, 수신은 그 뒤에 `designated_judgment`로 현재성을 확인한다.
- 동작: 변경. 명백한 판정자 누락이 생산자 검사 단계에서 반려된다.
- 실익: 적용 단계 반려 경로 일부 축소(추정).
- 위험과 보호: `test_academic_engine.*.test_explicit_requirement_blocks_runtime_completion_until_independent_assessment`, `test_redesign_ENGINE.*.test_operational_task_disposition_uses_authoritative_item_assessment`. 생산자 쪽을 덮는 테스트는 없음.
- 확신: 낮음 — 계획 문맥에 인용 ID의 가족을 판정할 정보가 충분히 있는지 확인하지 않았다.
- 다른 영역: `planning.py`, `engine.py`(계획 문맥)

#### REV-11: 적용 단계가 봉인된 확장의 형태를 다시 검사한다
- 유형: 수신재검사중복
- 위치:
  - `task_scope.py:12-22, 81-83`(`_withdrawal`, 중복 철회): 대응 제출 검사 `submission.py:156`(스키마)과 `submission.py:835-839`(고유성)
  - `review_engine.py:1110, 1114-1115`(`research_requests` 타입): 대응 제출 검사 `submission.py:177`(스키마)
  - `review_engine.py:1231-1232`(보충 조사 확장 금지): 대응 제출 검사 `submission.py:207-208`(`allowed.clear()`)와 `additionalProperties: False`
- 현상: 적용 함수가 받는 확장은 봉인 영수증의 해시로 대조한 바이트다(`submission.py:55-84`, `engine.py:2451-2454`). 그 바이트는 제출 검사의 스키마를 이미 통과했다. 따라서 위 형태 검사는 디스크 왕복을 해시가 덮는 상태에서 같은 조건을 다른 코드로 다시 확인한다. 봉인을 거치지 않은 경로(`engine.py:2455-2486`, `submission_unsealed`)에서도 `check_submission`이 같은 스키마 검사를 수행하고, 실패 issue가 있으면 적용하지 않는다(`integration.py:476-482, 496-497`).
- 제안: 위 세 곳의 형태·금지 가족 검사를 지우고 의미 검사만 남긴다. 예를 들어 `_withdrawal`은 튜플 추출만 남긴다.
- 동작: 보존
- 실익: 약 15행 삭제(측정: `task_scope.py:13-21`, `82-83`, `review_engine.py:1110, 1114-1115, 1231-1232`).
- 위험과 보호: `apply_task_dispositions`를 봉인 없이 직접 부르는 다른 호출자는 `engine.py:3858` 하나(grep)다. 덮는 테스트는 `test_approved_five_repairs.*.test_current_unperformed_withdrawal_preserves_results_and_residual_scope`, `test_approved_five_repairs.*.test_unassessed_new_results_and_protected_scope_are_not_withdrawable`다.
- 확신: 중간 — 봉인 경로는 확인했다. 테스트가 도메인 함수에 형태가 틀린 값을 직접 넣어 오류 문구를 단언하는지는 확인하지 않았다.
- 다른 영역: `engine.py`(적용 순서)

#### REV-12: `accept_result`가 같은 scope 평가를 한 호출 안에서 두 번 검사한다
- 유형: 수신재검사중복
- 위치: `review_cycle.py:810-811`(`_validate_content`), `review_cycle.py:953-954`(`accept_result`)
- 현상: `accept_result`는 950행에서 `_validate_content`를 불러 `validate_scope_assessment`를 실행하고, 953행에서 같은 입력으로 다시 실행한다. 수신 cycle에는 `scope_executions_used` 키가 없어서 두 호출의 `executions_used`가 같다.
- 제안: `_validate_content`가 정규화한 평가를 반환하게 하고, `accept_result`는 그 값을 쓴다.
- 동작: 보존
- 실익: 중복 호출 1회와 3행.
- 위험과 보호: `test_review_scope_wire.ExpandedScopeRevisionTests.test_revision_retains_all_prior_slots_above_the_policy_minimum`, `test_review_cycle.*.test_scope_false_match_rejected_and_incomplete_not_reviewed`
- 확신: 높음 — 원문 대조.
- 다른 영역: 없음

#### REV-13: 실행 프로필 참조 `{id, revision, sha256}`의 형태 규칙이 다섯 곳에 있다
- 유형: 이음새중복
- 위치: `contracts.py:122-123`(wire 스키마), `record_schemas/schemas.py:41`(저장 스키마), `task_contracts.py:89-94`, `review_policy.py:102-108`, `codex_worker.py:61`(grep)
- 현상: 같은 규칙이 스키마 둘과 Python 셋에 따로 적혀 있다. 규칙은 "id는 비어 있지 않은 문자열, revision은 1 이상의 정수, sha256은 소문자 64자리 16진수"다. `task_contracts`와 `review_policy`의 Python 식은 글자까지 거의 같다.
- 제안: 소유 모듈 `execution_profiles`(`profile_ref()`가 있는 곳, `execution_profiles.py:49`)에 `validate_profile_ref(ref)`를 두고 Python 세 곳이 부른다. `codex_worker`가 패키지 없이 적재되는 모듈인지는 미확인이므로 그곳은 제외할 수 있다.
- 동작: 보존
- 실익: 중복 식 약 12행.
- 위험과 보호: `test_contracts.*.test_profile_references_use_the_sealed_provider_identity`, `test_budget.*.test_shared_profile_refs_reserve_atomically_and_separate_work_from_operations`
- 확신: 중간 — `codex_worker`의 적재 방식은 미확인.
- 다른 영역: `execution_profiles.py`, `record_schemas`, `codex_worker.py`

#### REV-14: 과제 계약의 형태와 상태 값이 wire 스키마, 저장 스키마, Python 검사기에 따로 적혀 있다
- 유형: 이음새중복
- 위치: `contracts.py:124-138`(`OBLIGATION`·`PROGRESS`·`TASK_CANDIDATE`), `record_schemas/schemas.py:119-140`(`RECORDS["tasks"]`), `task_contracts.py:44-97`(`validate_task_contract`). 상태 값: `task_contracts.py:13`, `planning.py:344`, `record_schemas/schemas.py:121`
- 현상: 과제 상태 집합 `planned/active/waiting/completed/closed`가 세 곳에 따로 적혀 있다. `scope` 키 집합, 비어 있지 않은 텍스트 목록, 참조 목록의 고유성도 wire 스키마와 `validate_task_contract`에 따로 있다. 조건 일부는 서로 다르다. 저장 스키마의 `OBLIGATION`은 `judges`를 선택으로 두고, `validate_task_contract`는 완료 의무에 `judges`를 요구한다. `task_candidate_record`는 wire 스키마 검사 뒤 `validate_task_contract`를 다시 불러, 생산자 검사 한 번에 같은 형태를 두 번 확인한다(`contracts.py:44, 61`).
- 제안:
  - 상태 집합은 `task_contracts.LIFECYCLE_STATES`를 정본으로 하고, `planning.LIFECYCLE_VALUES['task']`와 저장 스키마가 그것을 참조한다.
  - `validate_task_contract`에는 스키마로 표현할 수 없는 의미 조건(ID 고유성, 완료 의무의 판정자, 프로필 참조 고유성)만 남긴다. 형태는 저장 스키마 검사에 맡긴다.
  - `validate_task_contract`를 부르는 곳이 `state_checks`·`governance`·`academic_engine`·`planning`까지 퍼져 있으므로 저장 영역 조사와 함께 정한다.
- 동작: 보존
- 실익: 상태 집합 2곳과 형태 검사 약 20행(추정).
- 위험과 보호: `test_redesign_CONTRACTS.*.test_structured_task_candidate_has_one_completion_authority`, `state_checks`의 과제 계약 검사(`state_checks.py:310`)
- 확신: 중간 — 중복은 확인했다. 형태 검사를 저장 스키마로 넘겨도 되는지는 저장 검사의 실행 시점을 확인해야 한다.
- 다른 영역: `record_schemas`, `planning.py`, `state_checks.py`, `governance.py`, `academic_engine.py`

#### REV-15: 계약 검토 항목 다섯 개와 승인 조건이 문서, 튜플, 판정 함수에 있고 모델이 받는 스키마에는 없다
- 유형: 이음새중복
- 위치: `계약/작업-계약-검토.md:91-103`, `contracts.py:144-146`(`REVIEW_ITEM.item_id`는 `TEXT`, `CONTRACT_REVIEW_ITEMS`), `contracts.py:242-253`(`contract_review_decision`), 소비 `planning.py:190-195, 233-243`
- 현상: 항목 ID 다섯 개와 "`approved`는 `evidence_refs` 1개 이상·`missing_inputs` 비어 있음, `unresolved`는 `missing_inputs` 1개 이상"이라는 조건은 문서 표·산문과 `contract_review_decision`에 있다. 모델이 받는 스키마는 `item_id`를 임의 텍스트로 허용하고 `minItems: 1`만 요구한다(`contracts.py:176`). 지금 셋의 내용은 일치하지만, 모델은 산문으로만 이 조건을 알고, 위반은 `submission.output.item_reviews` 한 규칙의 의미 오류로 돌아온다.
- 제안: `SCHEMAS['task_contract_review']`에서 다음처럼 바꾼다.
  - `item_id`를 `{"enum": list(CONTRACT_REVIEW_ITEMS)}`로 둔다.
  - `item_reviews`에 `minItems`·`maxItems`를 5로 둔다.
  - 승인·미해결 조건은 `contract_review_decision`에 그대로 두고, 문서는 표의 항목 ID를 스키마의 `enum`으로 가리킨다.

  if/then으로 조건까지 스키마에 넣는 안은 CLI 수용성을 확인하기 전에는 권하지 않는다.
- 동작: 변경. 모델이 받는 스키마에 `enum`이 들어가고, 잘못된 항목 ID가 `schema.enum`으로 정확한 좌표와 함께 반환된다.
- 실익: 항목 ID의 정의가 코드 한 곳에서 스키마로 전달된다. 문서와의 이중 관리는 줄지만 사라지지는 않는다.
- 위험과 보호: `test_contracts.py:69` 부근 테스트, `research_fixtures.py:84`
- 확신: 중간 — 스키마 변경에 따른 CLI 수용성은 미확인.
- 다른 영역: `planning.py`(검토 봉인)

#### REV-16: scope 실행 하한 공식이 문서와 코드에 따로 적혀 있다
- 유형: 이음새중복
- 위치: `계약/동일성-검토.md:15`(U+N+4, U+2N+7), `review_policy.py:64-66`(`minimum_scope_executions`), 기본 정책 상한 `review_policy.py:37-39`, 문맥 값 `review_cycle.py:1207-1210`
- 현상: 문서 공식은 지금 코드와 일치한다. `N+1+3`은 U+N+4이고, `N+1+N+6`은 U+2N+7이다. 그러나 두 곳이 같아야 하는 구조다. 문맥은 정책 최소 자리 수로 계산한 `minimum_scope_execution_limit` 하나만 주므로, 자리를 늘린 생산자는 문서 공식으로 직접 계산한다. 생산자 검사가 같은 `validate_scope_assessment`를 실행하므로(`submission.py:721-724`), 공식이 어긋나도 생산자는 제출 전에 알 수 있다.
- 제안: 코드를 정본으로 두고, 문서 공식 옆에 "로컬 검사가 같은 함수로 확인한다"는 문장을 넣는다. 또는 `test_walkthrough_repairs`처럼 문서 공식과 함수 값을 대조하는 테스트를 하나 둔다.
- 동작: 보존
- 실익: 향후 어긋남 방지. 현재 제거되는 행은 없음.
- 위험과 보호: `test_review_engine.py:187-188`, `test_connection_repairs.py:111`(함수 값만 검사). 문서를 대조하는 테스트는 없음.
- 확신: 중간 — 일치 여부는 수기로 대조함.
- 다른 영역: 없음

#### REV-17: 착수 조건 문서의 가족·포인터·연산 표가 코드 표와 따로 관리되고, 대조 테스트는 예제만 본다
- 유형: 이음새중복
- 위치: `references/과제-착수조건.md:5, 7-18, 20, 24-43`. 코드 `planning.py:268-272`(`CONDITION_FIELDS`), `331-341`(`RECORD_FAMILIES`), `356-366`(`EXPOSED_FIELDS`). 기존 테스트 `scripts/tests/test_walkthrough_repairs.py:235-244`
- 현상: 수기 대조 결과, 연산 11종과 필드, 가족 21종과 space, 포인터 18가족이 지금은 모두 일치한다. 기존 테스트는 문서의 JSON 예제가 문법을 통과하는지만 보고 표는 비교하지 않는다. 생산자는 `validate_condition`을 로컬 검사로 실행하므로 표가 어긋나도 제출 전에 알 수 있다. 그러나 문서를 믿고 저작한 조건이 반려되는 비용은 남는다.
- 제안: 기존 테스트를 확장해 문서의 포인터 표와 가족 목록을 파싱하고, `EXPOSED_FIELDS`·`RECORD_FAMILIES`·`CONDITION_FIELDS`와 같은지 단언한다.
- 동작: 보존
- 실익: 어긋남을 테스트가 잡는다. 현재 제거되는 행은 없음.
- 위험과 보호: 표 서식이 바뀌면 파서도 고쳐야 한다. 덮는 테스트는 `test_walkthrough_repairs.*.test_documented_readiness_examples_match_the_live_grammar`다.
- 확신: 높음 — 표와 코드를 수기로 대조함.
- 다른 영역: `planning.py`

#### REV-18: `contract_checks`의 서로 다른 문제가 한 규칙 ID와 한 issue ID로 합쳐진다
- 유형: 기타(실패 식별의 붕괴)
- 위치:
  - `submission.py:717-718`: `contract_check_errors`의 각 문구를 같은 경로로 발행한다.
  - `submission.py:377-381`: 규칙 ID를 경로에서 만든다.
  - `integration.py:41-44`: issue ID를 `hash(rule_id, integration_id, path)`로 만든다.
  - `submission.py:1173-1193`: 미해결 실패를 이 키로 추적한다.
  - `submission.py:982-984`: 수리 응답이 issue ID 집합을 덮어야 한다.
  - `계약/후보-준비.md:142-150`: 문제 유형별 조치 표
- 현상: 한 후보의 자기점검에서 기호 중복과 결과 갈래 부족이 함께 나와도 두 issue의 `rule_id`(`submission.activity-extensions.json.contract_checks.*`)와 `issue_id`가 같다. 그래서 다음 결과가 생긴다.
  - 수리 응답은 둘을 한 번으로 덮는다.
  - 미해결 추적(`_pending_failures`)은 하나만 남긴다.
  - 규칙별 집계(`summarize_checks`)는 모든 자기점검 실패를 한 규칙으로 센다.
  - 문서 표는 영어 오류 문구를 산문으로 대응시킨다.
- 제안: `contract_check_errors`가 `(rule_id, message)`를 돌려주게 하고, 여섯 규칙에 고정 ID를 준다(예: `contract_check.coverage`, `.symbol_meaning`, `.symbol_absent`, `.outcome_branches`, `.cited_record`, `.sibling_boundary`). 문서 표의 첫 열을 그 ID로 바꾼다.
- 동작: 변경. issue ID와 규칙 ID가 세분되어, 생산자의 수리 응답 단위가 문제별로 바뀐다.
- 실익: 수리 추적의 정확도와 문서 대응의 명확성. 행 수 변화는 작다.
- 위험과 보호: `test_contract_checks.py`의 14개 테스트가 문구나 경로를 단언한다(파일 목록 확인).
- 확신: 중간 — 붕괴는 식으로 확인했다. 실제 수리 품질에 주는 영향은 추정이다.
- 다른 영역: `integration.py`, `계약/후보-준비.md`

#### REV-19: 봉인된 검사 artifact의 재해시 두 곳이 S3 커널을 쓰지 않는다
- 유형: 운영비용
- 위치: `submission.py:1300-1305`(`summarize_snapshot_checks`), 호출 `engine.py:4746-4747`. `integration.py:210`(`read_sealed_submission`을 `git_dir` 없이 호출). `submission.py:73-75`(`git_dir is None` 분기)
- 현상: `summarize_snapshot_checks`는 호출될 때마다 모든 중앙 제출의 check artifact를 git에서 읽어 SHA-256으로 다시 대조한다(`history_window=len(seals)`). `require_bundle_impact_review`도 `git_dir` 없이 `read_sealed_submission`을 불러 매번 해시한다. 나머지 다섯 호출자(`engine.py:1206, 1215, 1662, 1940, 2452`)는 `git_dir`를 넘겨 이음새 계약 3절(S3)의 `artifact_verified`를 쓴다. 이음새 계약 S3의 적용 지점 목록(R4·R8·R25·R29·R30·R44)에는 이 두 곳이 없다.
- 제안: `summarize_snapshot_checks`에 `git_dir` 인자를 더해 `artifact_verified`/`verify_artifact`를 쓰게 한다. `require_bundle_impact_review` 호출에도 `git_dir`를 넘긴다. 모든 호출자가 `git_dir`를 넘기게 되면 `read_sealed_submission`의 `git_dir is None` 분기를 지운다.
- 동작: 보존
- 실익: 보고 한 번에 필요한 git 읽기와 해시가 봉인 수에 비례하던 비용을, 같은 프로세스 안에서는 처음 한 번으로 줄인다(추정, 측정하지 않음). 해시 비교 경로 1곳을 삭제한다.
- 위험과 보호: S3 집합은 프로세스 전역이며 번들 불변에 기댄다(이음새 계약 3절). 덮는 테스트는 미확인이다(`summarize_snapshot_checks`를 직접 검사하는 테스트를 찾지 않음).
- 확신: 중간 — 호출 빈도(`engine.py:4802`의 `repair_iteration` 영역)는 확인하지 않았다.
- 다른 영역: `integration.py`, `engine.py`, `repository.py`(S3 커널)

## 3. 보존 판정

- **`check_submission` 하나를 생산자·수신·미리보기가 공유하는 구조**(`submission.py:1094-1136`, `1436`, `1502`, `1147`). 기준 문서의 원칙이 이미 실현된 곳이다. 같은 도구·입력 해시에서 판정이 다르면 `machine_check.tool_defect`로 표시하는 비교(`1117-1133`)도, 배포 도구 판본 차이를 드러내는 장치이므로 유지한다.
- **`contract_check_errors`의 공유**(`submission.py:341-374`, 호출 `717`). 생산자와 수신이 같은 함수를 쓰고, 선언은 계약 검토 입력에 넣지 않는다(기억 L-0020 57행). REV-18의 식별자 세분만 제안한다.
- **`read_sealed_submission`의 해시 대조와 check ID 재계산**(`submission.py:39-110`, `1244-1249`). 디스크의 기존 기록이라는 신뢰 경계를 건너는 수신 검사이며, 봉인한 바이트와 적용하는 바이트가 같음을 보장한다.
- **미리보기의 사유 비공개**(`submission.py:1153-1163`). 적용 단계 반려의 사유를 감춰 생산자의 자기 수리를 어렵게 하는 것처럼 보인다. 그러나 적용 콜백이 드러낼 수 있는 판정 공간을 막으려는 의도가 주석에 명시돼 있으므로 유지한다. 대신 REV-01·03·08·09·10은 적용 단계에만 있던 조건을 공유 검사로 옮겨 이 비공개가 가리는 범위를 줄인다.
- **검토 배정·독립성·예산의 수신 전용 검사**(`review_cycle.validate_review_execution` 208-234, `review_engine._admit_review_execution` 282-341, `planning.seal_contract_review`의 작성자 배제 236-237). 생산자가 고칠 수 없는 배정 사실이므로, 생산자 자기 확인을 추가할 대상이 아니다.
- **적용 시점 현재성 검사**(`decision_engine._validate_decision_acceptance` 86-137, `task_scope._validate`의 계약 해시·실행 중 확인 29-46, `review_engine._review_cycle` 542-572). 생산 이후 상태가 바뀌었는지를 보는 검사라 생산자 검사로 대신할 수 없다.
- **`validate_sealed_review`의 전면 재구성**(`review_cycle.py:237-374`). 재심사와 단계적 편입이 저장 기록만으로 판정을 복원하는 경로이며, 디스크 기록이라는 신뢰 경계에 해당한다.
- **`task_candidate_record`의 생산자·수신 공유**(`contracts.py:35-71`, 호출 `submission.py:656`, `engine.py:4030`). 같은 함수를 두 쪽이 쓰는 올바른 형태다. REV-14는 이 함수 내부의 형태 이중 검사만 다룬다.
- **`install_tools`가 엔진 모듈을 배포에서 빼는 규칙**(`submission.py:1343-1345`). 상태 적용기를 작업자에게 복제하지 않는 경계다(기억 L-0020 53행). 이 영역의 모든 공유 검사 제안은 이 규칙을 전제로 비엔진 모듈을 정본 위치로 골랐다.

## 4. 후보 없음

전문을 읽었으나 후보가 없었던 부분은 다음과 같다.

- `submission.py`: 생산자 검사 사슬(`producer_check`, `read_producer_checks`, `_validate_producer_sequence`), `capture_eligible`/`captured_check`, `summarize_checks`, `request_control`, `main`, `reference_catalog`
- `contracts.py`: `reading_map`, `prompt_documents`, `render_prompt`, `prompt_metrics`, `identify_schema`/`schema_reference`
- `task_contracts.py`: `repetition_lineages`, `readiness_for_task`, `returned_task_ids`, `validate_plan_dispositions`
- `task_scope.py`: `decision_is_current`, `validate_disposition_authority`, `assessment_basis`, `assessment_current`, `refresh_task_assessments`, `designated_judgment`, `validate_withdrawal_record`
- `review_cycle.py`: 쟁점 상태기계(`_organize`, `_answer`, `_judge`, `_aggregate_judges`, `_finish`), 대체 권한(`replacement_authority`, `authorize_record_replacement`, `_replay_replacement`), `reserved_review_slots`, `validate_resource_disposition`, `context_for`
- `review_engine.py`: 재심사 개시·적용(`_qualified_assessment_defect`, `_start_assessment_reassessment`, `_publish_assessment_reassessment`, `_settle_assessment_reassessments`), 단계적 검토, 자원 처분(`_request_review_resource_disposition`, `_settle_review_resource_dispositions`), 호스트 재조정, 기록 관찰(`_record_review_prompt`, `_record_review_observation`), 복구·대기 해제
- `review_policy.py`: REV-13·REV-16 외 없음
- `decision_engine.py`: `_execution_requirement_changes`, `_decision_references`, `_apply_task_plan`, `_refresh_changed_decision`
- `계약/작업-계약-검토.md`: REV-15 외 없음
- `계약/동일성-검토.md`: REV-07·REV-16 외 없음. 단계별 판정 규칙(13-17, 55-83행)은 `_validate_content`·`_organize`·`_answer`·`_judge`의 조건과 대조해 어긋남이 없었고, 생산자 검사가 같은 함수를 실행한다.
- `references/과제-착수조건.md`: REV-17 외 없음

## 5. 미완료

없음. 맡은 모듈 8개와 문서 3개는 전문을 읽었다. 판정에 필요한 범위 밖의 확인 사항(CLI 스키마 수용성, 역할 문맥의 카탈로그 구성, 개별 테스트 단언 문구)은 각 후보의 `확신`과 `위험과 보호`에 미확인으로 적었다.

## 6. 작업 중 사건

- 설치되는 응답 스키마가 `contracts.action_schema`에서 온다고 예상했다. 그러나 엔진의 `_response_schema`(`engine.py:2208-2247`)가 검토 역할을 `review_engine`의 생성기로 보낸다는 사실을 확인했다. 이 확인에서 REV-07이 나왔다.
- 수제 검사기와 jsonschema의 판정 차이를 원문 독해만으로 단정하지 않고, 파이썬 한 줄 읽기 전용 확인으로 재현했다(REV-01에 명령과 결과를 적음). 저장소는 바꾸지 않았다.
- scope 실행 수의 생산자 값(`scope_executions_used`)과 수신 값이 한 실행만큼 어긋날 수 있다고 처음에 의심했다. `_register_execution`(`engine.py:3324`, 수용 때 실행 ID 추가)이 문맥 구성(`engine.py:3339`)보다 먼저 실행됨을 확인해 이 의심을 기각했다. 후보로 올리지 않았다.
- 작업 기억 색인(`기억/색인.md` layer-3)과 L-0020은 조사 도중에 확인했다. 착수 시점이 아니었으며, 확인한 내용은 보존 판정과 REV-01·07·15의 위험 판단에 반영했다.
- graphify는 사용하지 않았다. 맡은 파일을 전문으로 읽고 grep으로 호출 관계를 확인하는 것으로 충분했다.
