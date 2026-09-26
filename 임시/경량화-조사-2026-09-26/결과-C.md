# 결과 — 그룹 C: 제출·검토·계약·역할 입력

이 문서는 do-math 경량화 2라운드 그룹 C의 반환이다. 설계 `docs/do-math/경량화-설계-2026-09-26.md` 6절의 다섯 항목을 차례로 적는다. 통합자는 이 문서로 그룹 C 브랜치를 합칠지 판단하고, 다른 그룹과 겹치는 공유 정의와 충돌 좌표를 정리하고, 문서 단계에 넘길 변경과 첫 시험 실행에서 먼저 볼 위험을 고른다.

- worktree `C:/math-worktrees/r2-c`, 브랜치 `r2-c`, 커밋 `c918586`(기준: 커널 병합 `24682fd`)
- 좌표는 따로 적지 않으면 `C:/math-worktrees/r2-c/.claude/skills/do-math/scripts/do_math/` 아래 파일이다.
- 시험은 실행하지 않았다(설계 3.3). 바꾼 파일은 모두 `python -m py_compile`을 통과했다. 그 밖에 `operational_dispositions.validate_disposition`의 새 오류 문구를 확인하려고 이 함수를 한 번 직접 호출했다. 시험 러너는 실행하지 않았다.

요약하면, 표의 ID는 모두 조사 제안의 범위대로 구현했다. 생산자 검사와 수신 검사가 같은 함수를 부르게 하려고 공유 정의를 그룹 C 모듈 네 개(review_cycle, submission, task_contracts, task_scope)에 새로 두었고(2절), 이를 위해 다른 그룹 모듈 아홉 개를 좁게 고쳤다(5.1절). 동작이 바뀐 지점은 1절 표의 "동작 변화" 열에 있고, 그 가운데 시험으로 확인하지 못한 위험은 4.2절에 모았다.

## 1. ID별 처분

모든 ID를 구현했다. REV-14는 설계가 정한 변형 범위로 구현했다.

| ID | 처분 | 구현 | 동작 변화 |
|---|---|---|---|
| REV-01 | 구현함 | `review_cycle._validate`(수제 검사기)를 지우고 `_check_schema`(jsonschema Draft 2020-12, 첫 오류를 `ValueError("output/<경로>: <메시지>")`로)로 바꿨다. `stage_schema`·`research_schema`·조사 요청 스키마의 문자열은 `contracts.TEXT`(`minLength 1`, `pattern \S`)다. | 공백만 있는 문자열이 생산자 검사에서 `schema.pattern`으로 반려된다. 적용 단계 오류 문구가 jsonschema 문구로 바뀐다. |
| REV-02 | 구현함 | `review_cycle`에 `validate_research_answer`(answered 규칙), `validate_provisional`(조사 요청 시 잠정 unresolved와 proposal digest), `validate_research_requests`(요청 스키마와 요청 ID 고유), `research_request_schema`를 두었다. 생산자 검사(`submission._payload_issues`)와 적용(`accept_research_result`, `defer_for_research`, `validate_visible_output`)이 같은 함수를 부른다. `extension_schema`의 `research_requests` 항목도 `research_request_schema()`다. | 조사 요청 검사가 identity_review의 모든 단계(scope 포함)에서 실행된다. 전에는 scope 단계에서 생산자가 요청 원천을 검사하지 않았다. |
| REV-03 | 구현함 | `review_cycle.classify_research_source`가 허용 규칙 하나를 정한다(proposal 좌표, 공개 쟁점, 자기 자리 기록, 제공 원천, 지식 ID). `submission.validate_research_reference(reference, context)`는 판정만, `review_engine._research_source_spec`은 분류 결과로 바이트 읽기·봉인만 한다. 지식 ID는 각 호출자가 자기 입력의 ID를 넘긴다(생산자는 `knowledge_catalog`, 수신자는 현재 `instance['knowledge']`). | 엔진 문맥의 `knowledge_catalog`는 인스턴스 지식 전건이다(`engine._context`의 지식 순회). 따라서 두 쪽이 갈리는 경우는 생산자의 고정 입력을 만든 뒤 수신 적용 전에 새로 생긴 지식뿐이다. 다른 자리 기록 참조의 오류 문구가 "another slot transcript is private"에서 일반 허용 거부 문구로 바뀐다. |
| REV-04 | 구현함 | `review_cycle.review_authors(cycle)`(cycle, proposal, previous_reviews 작성자의 합집합)를 두고 `validate_review_independence`가 이를 쓴다. 엔진의 네 수락 지점(`_admit_review_execution`, `_accept_identity_review`, `_defer_review_for_research`, `_apply_review_research`)이 모두 이 함수를 부른다. 한 단계 대조 코드와 `accept_result`의 작성자 검사를 지웠다. 보충 조사 실행은 봉인 재구성과 같은 자리 모양 `{'role','research_request_id'}`으로 검사한다(`review_engine._independence_seat`). | 일반 검토도 배정과 수락에서 추이 계보를 검사한다. 두 단계 이상 떨어진 작성자 문맥 계승, 같은 검토의 다른 자리 문맥 계승, 작성자와 같은 provider 대화 ID가 이제 실시간으로 거부된다. 계보 행이 runtime에 없으면 'review context lineage does not resolve'로 거부된다. |
| REV-05 | 구현함 | `review_cycle._key`를 공개 `slot_key`로 바꾸고 `review_engine`의 f-string 네 곳과 `_pending_key`가 이를 쓴다. | 없음 |
| REV-07 | 구현함 | 옛 `contracts.SCOPE_ASSESSMENT`를 `review_cycle.stage_schema('scope')`로 옮겼다. `selected_profile_ref`는 소비자(`validate_scope_assessment`)와 같게 `anyOf [null, PROFILE_REF]`다. `contracts.action_schema`의 scope 분기와 `review_cycle_id` 분기, `SCOPE_ASSESSMENT`를 지웠다. `engine._review_schema`는 원래대로 `stage_schema`에 digest `enum`만 더한다. `preflight`의 스키마 수용 검사 목록에 `identity_review:scope`를 더했다. `test_review_scope_wire`는 엔진 생성기를 검사하게 바꿨다(4절). | scope 단계 모델이 정밀한 `scope_assessment` 스키마를 받는다. 형태 오류가 `schema.*` issue로 좌표와 함께 반려된다. |
| REV-08 | 구현함 | `submission`에 `RESOLVABLE_WAITS`, `blocked_action_row`(문맥 투영 한 벌), `action_resolution_errors`(대기 종류와 `current` 증거의 판정 범위)를 두었다. 생산자 검사와 `decision_engine._apply_action_resolutions`가 같은 함수를 부른다. 수신은 그 뒤에 수락 여부와 전제 현재성, 개정 해소를 계속 확인한다. 엔진 투영 세 벌은 `blocked_action_row` 하나를 쓴다. | 해소할 수 없는 종류의 대기를 해소하겠다는 주장과, 자기 실행을 증거로 들면서 판정 범위가 다른 주장이 생산자 검사에서 반려된다. |
| REV-09 | 구현함 | 엔진이 research_preparation·research_plan·operational_review 문맥에 `supplied_record_ids`(문맥에 보이는 ID ∩ 현재 기록 ID, `submission.supplied_record_ids`)를 넣는다. `task_scope.require_evidence_refs(refs, admissible)`와 `task_scope.result_ids(task)`를 두었다. 생산자는 `supplied_record_ids` ∪ 해당 과제 결과 ID로, `apply_task_assessments`는 현재 기록 ID ∪ 같은 결과 ID로 같은 함수를 부른다. `submission.assessment_reference_ids`를 지웠다. | 관찰 사실·질문 연결·사건 같은 비기록 ID를 완료 증거로 인용하면 생산자 검사에서 반려된다. 수신 오류 문구가 'disposition evidence is not in the current input'에서 "completion evidence requires a supplied record ID; ..."로 바뀐다. |
| REV-10 | 구현함 | `task_contracts.judge_coverage_errors(role, execution_id, task, assessment, families)`와 `JUDGE_EVIDENCE_FAMILIES`(formal_check→formal-result, identity_review→identity-assessment, goal_audit→goal-judgment, `designated_judgment`와 같은 대응)를 두었다. 생산자는 `submission.judgment_families(context)`(지식 카탈로그의 `formal_result_id`·`identity_assessment_ids`와 `goal_judgments`)로, 수신자는 `planning._records`의 가족으로 부른다. 수신은 이어서 `designated_judgment`로 현재성을 확인한다. | 판정자가 아닌 평가자가 fulfilled를 주장하면서 판정자 가족의 증거를 하나도 인용하지 않으면 생산자 검사(`submission.judge_coverage`)에서 반려된다. 조사가 "확신 낮음"으로 남긴 전제(계획 문맥에 가족 판정 정보가 있는가)는 위 카탈로그 필드로 성립함을 확인했다. |
| REV-11 | 구현함 | `task_scope._withdrawal`과 중복 철회 검사, `review_engine`의 `research_requests` 타입 검사와 요청 모양 검사, 보충 조사의 확장 금지 검사를 지웠다. 봉인 스키마와 제출 검사가 같은 조건을 이미 본다. `apply_task_dispositions`의 유일한 비봉인 호출자는 없다(`engine._apply_extensions`는 실행의 확장, 곧 제출 검사를 통과한 값을 넘긴다). | 없음 |
| REV-12 | 구현함 | `_validate_content`가 scope 평가의 정규화 결과를 돌려주고 `accept_result`는 그 값을 쓴다. `accept_result`의 앞쪽 스키마·digest 검사도 `_validate_content` 한 번으로 줄었다. | 오류 검사 순서가 바뀐다(실행 ID 재사용·manifest 검사가 스키마 검사보다 먼저 난다). |
| REV-14 | 부분 구현(변형) | 설계 4.4절대로 상태 상수는 그룹 B(STO-02) 몫으로 남기고, `validate_task_contract`의 형태 중복만 줄였다. 책임은 셋으로 나뉜다. 첫째, 저장 스키마가 이미 보장하는 형태(상태 enum, 참조 목록 다섯 개의 자료형·고유성, scope·expected의 키 집합과 자료형, id)는 `validate_task_contract`가 더 보지 않는다. 둘째, 저장 스키마가 표현하지 못하는 조건(비지 않은 텍스트·목록, 양수 revision, 완료 의무의 judges, 증거 고유성, 프로필 참조 판본)은 `validate_task_contract`에 남겼다. 셋째, 어떤 스키마도 표현하지 못하는 고유 ID 조건(`progress_criteria`와 `completion_obligations` 각 목록 안의 `id`가 서로 다르고, `profile_refs`의 `id`가 서로 다름)은 `task_contracts.validate_contract_meaning`으로 나누었고, `contracts.task_candidate_record`는 wire 스키마 검사 뒤 이것만 부른다. | 조사 제안의 "형태는 저장 스키마에 맡긴다"를 끝까지 하려면 저장 스키마의 `TEXT`(`{"type":"string"}`, `record_schemas/schemas.py:9`)와 `NAT`(`minimum 0`), 선택 필드인 `judges`를 강화해야 한다. 이는 그룹 B 모듈이라 5절에 넘긴다. 형태가 틀린 dict(예: `scope` 키가 없거나 참조 목록 자리에 문자열이 있는 과제)를 넣으면 이제 ValueError 대신 KeyError·TypeError가 날 수 있다(`planning.task_ready`는 이 예외들을 잡아 `evaluation_error` 상태로 돌려주고, `state_checks.run`은 결함으로 기록한다. 저장 상태는 스키마를 통과하므로 운전 중에는 이 경로에 들어오지 않는다). |
| REV-15 | 구현함 | `REVIEW_ITEM.item_id`를 `{"enum": CONTRACT_REVIEW_ITEMS}`로, `item_reviews`를 `minItems`·`maxItems` 5로 바꿨다. 승인·미해결 조건은 `contract_review_decision`에 그대로 두었다. | 잘못된 항목 ID와 항목 수가 `schema.enum`·`schema.minItems`·`schema.maxItems`로 좌표와 함께 반려된다. |
| REV-16 | 구현함 | `test_walkthrough_repairs.test_scope_execution_minimum_in_the_review_contract_matches_the_policy`를 새로 두었다. `계약/동일성-검토.md`의 "한 회차의 하한은 U+N+4", "두 회차 이상의 하한은 U+2N+7"을 정규식으로 읽어 `review_policy.minimum_scope_executions`와 여러 U·N·회차에서 대조한다. 실행하지 않았다. | 없음 |
| REV-17 | 구현함 | `test_walkthrough_repairs.test_readiness_document_tables_match_the_condition_grammar`를 새로 두었다. `references/과제-착수조건.md`의 연산 표(연산 집합과 각 연산 필드 ⊆ 문서 셀의 역따옴표 토큰), 기록 가족 목록과 runtime·research space 문장, 포인터 표를 `planning.CONDITION_FIELDS`, `RECORD_FAMILIES`, `EXPOSED_FIELDS`와 대조한다. 실행하지 않았다. 지금 문서와 코드를 손으로 대조한 결과 일치한다(연산 11, 가족 21, 포인터 표 18가족). | 없음 |
| REV-18 | 구현함 | `contract_check_errors`가 `(rule_id, message)`를 돌려준다. 규칙 ID: `contract_check.cited_record`, `.symbol_meaning`, `.symbol_absent`, `.outcome_branches`, `.dependency_outcomes`, `.sibling_boundary`, `.sibling_revision`, `.sibling_under_revision`. 후보 전건 덮기 검사는 `contract_check.coverage`다. | 한 후보의 서로 다른 결함이 서로 다른 issue ID로 추적되고, 수리 응답도 결함별로 요구된다. 같은 규칙의 결함 둘(예: 없는 기호 둘)은 여전히 한 issue ID다. |
| ENG-02 | 구현함 | `task_contracts.unsupplied_task_inputs(refs, supplied, *, admit_named_sources)` 하나를 세 곳이 부른다. 허용 집합은 공통-실행.md 43행 문언대로 `available_input_refs` ∪ 제공된 기록(`supplied_record_ids`) ∪ 같은 응답의 새 제목이다. 생산자(`submission`)는 자기 고정 입력으로, 엔진 적용(`engine._apply`)은 그 실행의 고정 입력(`_issued_input`)으로, 착수 판정(`planning.task_ready`)은 현재 파생 입력 참조 ∪ 현재 기록으로 판정한다. `source:` 참조는 후보 단계에서만 미제공을 허용하고 착수 판정이 존재를 기다린다(기존 규칙 유지). | 결정·허가 ID처럼 공급된 기록이면 세 곳 모두 받아들인다. 사건·질문 연결처럼 기록이 아닌 ID는 생산자 검사가 반려한다(전에는 생산자가 받고 적용이 반려했다). 오류 문구가 "task inputs must name available_input_refs, supplied records or titles prepared in this output; unknown: ..."로 바뀐다. |
| ENG-03 | 구현함 | `lifecycle_engine._run_external_action`의 덧붙이기 네 줄((b))을 지웠다. | 없음(다음 회차에 사라지던 값이다). |
| ENG-04 | 구현함 | `instance['available_input_refs']`를 더 저장하지 않는다. 저장 스키마 필드(`record_schemas/domains.py`)도 지웠다(설계 1.2, 호환 선택 필드를 남기지 않음). `task_contracts.available_input_refs(instance, runtime, *, lean_available)`가 정의이고, 호스트 사실(Lean 발견)은 인자다. 엔진 `_available_inputs()`가 역할 문맥에 넣고, `_evaluation_context_for(store, snapshot, *, lean_available)`가 평가 문맥에 `lean_available`을 싣는다. `planning.task_ready`는 그 값으로(없으면 False), `capture_task_basis`는 설정만으로(`lean_available=False`), 질문 대상 검증은 호스트와 무관하게(`lean_available=True`) 계산한다. 엔진 준비 시점·scheduler 소유 루프의 저장 줄을 지웠다. | Lean 설치 변화가 상태 게시를 만들지 않는다. 계약 검토의 `task_basis`에서 `tool:lean`의 `available`은 이제 설정(`lean_command`) 기준이다. 따라서 Lean을 설정하지 않고 발견만 한 호스트에서 전에 봉인한 검토 기반과는 값이 다를 수 있다(설계 1.2에 따라 이전 인스턴스는 모두 삭제되었고 새 인스턴스는 처음부터 새 규칙으로 기반을 봉인하므로, 운전 중인 인스턴스에는 영향이 없다). |
| ENG-08 | 구현함 | `submission.issued_input(execution, snapshot, read_artifact, *, git_dir=None, with_schema=True)`가 입력 묶음의 `context.json`·`schema.json`을 읽는 하나뿐인 판독기다. `git_dir`가 파일 시스템 경로(실제 저장소)이면 `(git_dir, 경로)` 키로 프로세스 안에서 메모하고(상한 32, S3의 묶음 불변 전제) 사본을 돌려준다. 경로가 아닌 `git_dir`(시험 대역, 문자열 표지)는 메모하지 않는다. 준비 적용은 후보가 있을 때만 고정 입력을 읽는다. 엔진 9곳(`engine._issued_input`), `read_sealed_submission`, `integration.require_bundle_impact_review`가 이를 쓴다. context만 필요한 세 곳은 `with_schema=False`다. | 없음(같은 바이트, 같은 해석). |
| ENG-16 | 구현함 | (a) 계획·준비 문맥의 `config` 투영을 지웠다. `context_store`의 `configuration_source` 조건을 역할 집합(research_preparation, research_plan, intent_interpretation)만으로 하고, intent_interpretation 문맥의 `config` 투영(`governance_engine`)도 지웠다. (b) 엔진의 `pending_revisions`는 research_plan에만 계산한다(준비는 `prepare_role_input`이 계산). (c) research_plan의 `ready_task_ids`는 `task_readiness`에서 파생한다. research_preparation은 `task_readiness`를 받지 않으므로(ENG-17 d) `planning.ready_task_ids`로 한 번 계산한다. (d) `_session_resources()` 두 번째 호출을 지웠다. (e) 같은 조건 if 두 쌍을 합쳤다. (f) `_governance_context`의 deepcopy를 지웠다. | 위임 판정 intent_interpretation 입력에도 `configuration_source`가 생긴다(전에는 config가 없어 만들지 않았다). |
| ENG-17 | 구현함 | (a) `repetition_lineages`, `execution_limits`를 문맥에서 뺐다. (b) `blocked_actions`를 문서(공통-실행.md 27행)대로 실패 종류(`RESOLVABLE_WAITS`)로 거른다. 계획·준비·운영 점검에 적용하고, maintenance는 거르지 않은 모든 대기 행동을 같은 행 모양으로 받는다. (c) `ongoing_preparation`을 없애고 그 추가 필드(goal_revision, policy_revision, revision_targets, assessment_targets, observation_rule_targets)를 `ongoing_work`의 research_preparation 실행 행에 싣는다(`context_store`). (d) `task_readiness`는 research_plan·research_work·supplemental_research에만 계산해 준다(`계약/연구-계획.md` 24행, `계약/연구-수행.md` 17행). | 역할 프롬프트의 필드가 줄거나 합쳐진다. 모델이 지운 필드를 실제로 읽었는지는 문서 대조로만 확인했다. |
| RUN-19 | 구현함 | `operational_dispositions.validate_disposition`은 `contracts.disposition_schema()`에서 처분 kind의 변형을 골라 jsonschema로 검사하고 사본을 돌려준다. `_REQUIRED`, `DISPOSITION_KINDS`, 필드별 수동 검사를 지웠다. repair의 `repair_target`에 `pattern "^installation:"`을 넣었다. | 공백만 있는 문자열을 가진 처분이 수신에서 거부된다. 생산자가 `installation:` 조건을 스키마로 미리 안다. 오류 문구가 "operational disposition <kind>/<경로>: <jsonschema 메시지>"로 바뀐다. |
| STO-22 | 구현함 | `submission._intent_import_issues`가 `governance.validate_import_units`를 고정 입력의 보기(instance id, decisions, governance_records, grants, tasks와 `original_source`)로 실행하고, 거버넌스 종류 단위의 `payload.record`에 `validate_governance_record`를 적용한다. 소유자별 현재 상태 검사는 수신에 남기려고 `validate_import_units`에 `owner_kinds` 키워드를 더했다(공개된 `import_consumers` 종류를 알려진 소유자로 보고, 소유자 검사 훅은 부르지 않는다). 옛 재구현(구간 덮기·단위 ID·질문 참조)을 지웠다. | 생산자가 제출 전에 수신과 같은 구간·질문·payload 좌표 결함과 헌장 등 거버넌스 기록 결함을 발견한다. 규칙 ID가 `intent.import_units`(첫 오류 하나), `intent.governance_record`로 바뀐다. 조사가 미확인으로 남긴 "제출 도구에서 governance import 가능 여부"는 `install_tools`가 엔진 모듈(`engine.py`, `*_engine.py`)만 빼므로 `governance.py`가 배포됨을 확인했다. |

## 2. 새로 만든 공유 정의와 위치

설계 정정(필요한 공유 정의가 커널에 없으면 개념을 소유한 자기 그룹 모듈에 하나만 만든다)에 따라 아래를 만들었다. 커널 표의 정본과 겹치는 것은 없다. 통합자는 다른 그룹이 같은 개념을 만들었는지 이 표로 대조한다.

| 이름 | 위치 | 규칙 | 호출자 |
|---|---|---|---|
| `slot_key(action)` | review_cycle | 검토 자리 키 `stage:round:slot` | review_cycle, review_engine |
| `review_authors(cycle)` | review_cycle | 제안 계보의 작성 실행 합집합 | `validate_review_independence` |
| `research_request_schema()`, `validate_research_requests(requests)` | review_cycle | 조사 요청 모양, 요청 ID 고유 | submission(스키마·생산자 검사), `defer_for_research` |
| `validate_provisional(proposal_digest, action, output)` | review_cycle | 조사 요청 시 잠정 반환 | `validate_visible_output`, `defer_for_research` |
| `validate_research_answer(output)` | review_cycle | answered 규칙 | submission, `accept_research_result` |
| `classify_research_source(reference, *, proposal, issues, own_source_refs, sources, knowledge_ids)` | review_cycle | 조사 원천 허용 규칙과 분류 | submission, review_engine |
| `_check_schema(value, schema, label)` | review_cycle(내부) | 검토 스키마의 jsonschema 판정 | review_cycle 내부 |
| `issued_input(execution, snapshot, read_artifact, *, git_dir, with_schema)` | submission | 실행의 고정 입력 판독과 프로세스 메모 | engine 9곳, `read_sealed_submission`, integration |
| `supplied_record_ids(context, record_ids)` | submission | 입력이 공급한 기록 ID | engine `_context` |
| `judgment_families(context)` | submission | 입력 카탈로그의 판정 기록 가족 | 생산자 검사 |
| `RESOLVABLE_WAITS`, `blocked_action_row(action_id, entry)`, `action_resolution_errors(blocked, evidence_action)` | submission | 해소 가능한 대기, 대기 행동 투영, 해소 주장의 입력 판정 | engine `_context`, 생산자 검사, decision_engine |
| `FIXED_INPUT_REFS`, `available_input_refs(instance, runtime, *, lean_available)` | task_contracts | 역할이 과제 입력으로 쓸 수 있는 참조(파생) | engine, planning, record_schemas |
| `unsupplied_task_inputs(refs, supplied, *, admit_named_sources)` | task_contracts | 과제 입력 허용 규칙 | submission, engine, planning |
| `validate_contract_meaning(task)` | task_contracts | 스키마로 표현할 수 없는 과제 계약 조건 | contracts, `validate_task_contract` |
| `JUDGE_EVIDENCE_FAMILIES`, `judge_coverage_errors(...)` | task_contracts | 판정자 밖 fulfilled의 가족 증거 요구 | submission, task_scope |
| `result_ids(task)`, `require_evidence_refs(refs, admissible)` | task_scope | 완료 증거 허용 규칙 | submission, `apply_task_assessments` |

기존 함수의 시그니처 변경은 다음과 같다: `governance.validate_import_units(..., owner_kinds=None)`(그룹 F 모듈), `engine._evaluation_context_for(store, snapshot, *, lean_available)`, `submission.validate_research_reference(reference, context)`(workspace·candidate_files 제거), `contract_check_errors`의 반환형. 새 문맥 키는 `supplied_record_ids`이고, 지운 문맥 키는 `ongoing_preparation`, `repetition_lineages`, `execution_limits`, `config`다. `config`는 research_preparation·research_plan·intent_interpretation 문맥에만 있던 키이고, 세 역할 모두 `configuration_source`로 대체된다. 지운 저장 필드는 `instance.available_input_refs`다.

통합자가 볼 이음새 요청은 하나다. `submission.issued_input`의 메모와 커널 S3의 `VERIFIED_ARTIFACTS`는 같은 전제(묶음 불변, `str(git_dir)` 키)를 쓴다. `docs/do-math/검사-경량화-이음새-계약.md` 3절(S3)에 둘을 함께 적을지 정해야 한다.

## 3. 필요한 문서 변경

| 문서 | 위치 | 바꿀 내용 | 원인 |
|---|---|---|---|
| `references/공통-실행.md` | 27행 | `blocked_actions`는 해소할 수 있는 실패(output_validation, execution_failure)만 담는다고 적는다. | ENG-17(b), REV-08 |
| `references/공통-실행.md` | 29행 | `ongoing_preparation` 문단을 `ongoing_work`의 research_preparation 실행 행(같은 필드)으로 바꾼다. | ENG-17(c) |
| `references/공통-실행.md` | 43행 | "제공된 기록"을 입력의 `supplied_record_ids`로 가리킨다. 과제 입력은 `available_input_refs`, `supplied_record_ids`, 같은 응답의 새 제목에서 고른다. | ENG-02, REV-09 |
| `references/CLI-실행-계약.md` | 876행 | `ongoing_preparation` 설명을 지우고 `ongoing_work` 행으로 옮긴다. | ENG-17(c) |
| `references/CLI-실행-계약.md` | 입력 필드 설명 | `task_readiness`가 research_plan·research_work·supplemental_research에만 있고, `execution_limits`·`repetition_lineages`가 없다는 현재 입력 목록으로 맞춘다. `available_input_refs`는 저장 상태가 아니라 역할 입력에만 있다. | ENG-17(a)(d), ENG-04 |
| `계약/연구-계획.md` | 29행(7번) | `ongoing_preparation`을 `ongoing_work`의 준비 실행 행으로 바꾼다. | ENG-17(c) |
| `계약/연구-계획.md`, `계약/운영-점검.md` | 완료 판정 절 | 완료 증거는 `supplied_record_ids`의 기록이나 과제 결과 ID만 인용한다. 판정자가 아닌 평가자의 fulfilled는 판정자 가족(형식 결과·동일성 판정·목표 판정)의 증거를 인용해야 한다. | REV-09, REV-10 |
| `계약/후보-준비.md` | 142-150행 표 | 첫 열을 규칙 ID(`contract_check.*`)로 바꾼다. 과제 입력 허용 집합을 공통-실행과 같게 적는다. | REV-18, ENG-02 |
| `계약/작업-계약-검토.md` | 91-103행 | 항목 ID 표가 출력 스키마의 `item_id` enum과 같음을 가리킨다. | REV-15 |
| `계약/동일성-검토.md` | 15행 | `selected_profile_ref`는 선택할 프로필이 없으면 `null`일 수 있다(스키마와 소비자가 허용). 문서가 계속 "모두 쓴다"를 요구하려면 스키마를 다시 좁혀야 하므로 문서 단계가 정한다. 하한 공식을 바꾸면 REV-16 시험도 함께 고친다. | REV-07, REV-16 |
| `references/입력-소비자.md` | 9-54행 | "형태는 제출 검사(`governance.validate_import_units`, `validate_governance_record`)가 정본"이라고 가리키고, 코드와 겹치는 필드 나열을 줄인다. | STO-22 |
| `references/과제-착수조건.md` | 표 전체 | 바꾸지 않는다. 표를 바꾸면 REV-17 시험도 함께 고친다. | REV-17 |
| `docs/do-math/검사-경량화-이음새-계약.md` | 2·3절 | 2절 새 공유 정의를 옮기고, 3절(S3)에 `issued_input` 메모를 적을지 정한다. | 2절 |

## 4. 고친 시험 파일과 확인하지 못한 위험

### 4.1 고친 시험 파일

시험 파일은 18개를 고쳤다. 모두 `py_compile`을 통과했고 실행하지 않았다. 경로는 `scripts/tests/` 아래다.

| 파일 | 고친 시험 | 내용 | 항목 |
|---|---|---|---|
| test_walkthrough_repairs.py | 새 시험 둘 | REV-16·17 문서 대조 시험(1절) | REV-16, REV-17 |
| test_walkthrough_repairs.py | `test_question_references_are_stable_ids_at_both_boundaries` | 생산자 검사 문맥에 `original_source`, `instance_id`를 준다 | STO-22 |
| test_walkthrough_repairs.py | `test_engine_preserves_primary_dependency_when_extension_only_sets_condition` | `_available_inputs` 대역을 `_issued_input` 대역으로 바꾼다 | ENG-02 |
| test_review_cycle.py | `test_proposal_mutation_and_execution_identity` | 작성자·계승 거부를 `accept_result` 대신 `validate_review_independence`로 검사한다(작성자, `continuation_of`, `context_origin` 세 경우) | REV-04 |
| test_review_scope_wire.py | `setUp` | 엔진처럼 `stage_schema('scope')`에 digest enum과 봉투를 씌운 스키마를 검사한다 | REV-07 |
| test_contracts.py | `test_profile_references_use_the_sealed_provider_identity` | 두 번째 모양을 scope 스키마의 `selected_profile_ref`로 바꾼다 | REV-07 |
| test_redesign_CONTRACTS.py | `test_intent_source_coverage_is_checked_before_independent_review` | 문맥에 `original_source`를 주고 규칙 ID `intent.import_units`를 기대한다 | STO-22 |
| test_redesign_CONTRACTS.py | `test_scope_planning_schema_reaches_domain_scope_validator` | scope 스키마를 `review_cycle.stage_schema`에서 읽고 `initial_slots` 존재를 확인한다 | REV-07 |
| test_connection_repairs.py | `test_actual_proposal_overflow_ends_preparation_and_reaches_plan_input` | `assessment_reference_ids` 대신 검증 문맥의 `supplied_record_ids`를 확인한다 | REV-09 |
| test_redesign_OBSERVATION.py | `test_dispositions_are_validated_before_engine_application` | 기대 문구를 스키마 오류("Additional properties are not allowed")로 바꾼다 | RUN-19 |
| test_redesign_ENGINE.py | `test_operational_repair_candidate_never_mutates_files_or_publishes` | 기대 문구를 `repair/repair_target`으로 바꾼다 | RUN-19 |
| test_redesign_SURFACE.py | 계획 입력을 손으로 만드는 두 시험 | `ongoing_preparation` 입력을 뺀다 | ENG-17(c) |
| test_purpose_engine.py | `test_fixture_reads_returned_report_from_the_actual_supplied_task_source` | 같음 | ENG-17(c) |
| test_efficiency.py | `test_plan_receives_public_running_preparation_without_private_output` | `prepare_role_input` 뒤 `ongoing_work`의 준비 실행 행(목표·정책 판본 포함)을 확인한다 | ENG-17(c) |
| test_document_followup.py | `test_planning_roles_receive_the_complete_current_settings` | 엔진 문맥에 `config`가 없고, `prepare_role_input`의 `configuration_source` 파일이 현재 설정과 같음을 확인한다 | ENG-16(a) |
| test_document_followup.py, test_redesign_TASKS.py, test_redesign_EVIDENCE_walkthroughs.py | 입력 묶음 없는 가짜 실행으로 준비 `_apply`를 부르는 시험 | `_issued_input` 대역을 둔다(후보에 입력이 없으므로 빈 목록) | ENG-02 |
| test_redesign_EVIDENCE.py | 공유 대역 `InputSnapshot` | 클래스 속성 `git_dir = None`(`_issued_input`이 `store.git_dir`를 읽는다) | ENG-08 |
| test_decision_basis.py | `test_current_resolution_requires_its_validated_bundle_and_same_scope` | 기대 문구를 'same judgment scope'로 바꾼다 | REV-08 |
| test_task_scope.py | `test_rejects_nonwithdraw_and_duplicate_requests_atomically` → `test_submission_rejects_nonwithdraw_and_duplicate_requests` | 철회 모양과 중복 대상 거부를 이제 소유하는 제출 검사(`payload_issues`)에서 확인한다 | REV-11 |
| test_machine_parallel.py | `Host` | 지워진 소유 루프 호출만 받던 `_available_inputs` 대역을 뺀다 | ENG-04 |

나머지 시험 파일은 네 작업자가 바뀐 기호·문구·문맥 키를 기준으로 정적으로 읽었고 고칠 곳을 찾지 못했다. 이것은 실행 결과가 아니다. `test_redesign_ENGINE.py:521`, `test_lifecycle_engine.py:746, 795`의 `_available_inputs` 대역은 이제 부르지 않는 경로를 막지만 해가 없어 남겼다.

### 4.2 실행하지 않아 확인하지 못한 위험

시험을 돌리지 않았으므로 아래는 정적 독해로만 판단한 위험이다. 첫 시험 실행에서 이 순서로 보는 것을 권한다.

1. **검토자 독립성의 실시간 추이 검사(REV-04).** 배정과 수락이 모든 검토에서 `validate_review_independence`를 부른다. 계보 행이 runtime에 없는 실행, 같은 검토의 다른 자리 문맥을 이어받은 실행, 작성자와 provider 대화 ID를 공유하는 실행이 이제 실시간으로 거부된다. 보충 조사의 재개 실행처럼 같은 검토 안의 slot 있는 실행을 이어받는 경우도 거부된다(봉인 재구성과 같은 판정). 검토 엔진 시험(test_review_engine, test_review_research, test_redesign_REVIEWS)에서 먼저 확인한다.
2. **완료 증거와 과제 입력의 허용 집합(REV-09, ENG-02).** 생산자 검사는 문맥의 `supplied_record_ids`에 의존한다. 이 키가 없는 손으로 만든 문맥은 기록 인용을 모두 반려한다. `supplied_record_ids`는 엔진 `_context`가 끝나기 직전의 문맥에서 보이는 ID로 만든다. 그 뒤 `prepare_role_input`이 더하는 항목(`task_catalog` 등)이 새 기록 ID를 보여 주더라도 그 ID는 `supplied_record_ids`에 들어가지 않는다. 지금 `task_catalog`의 ID는 모두 엔진 문맥의 `tasks`에도 있으므로 빠지는 ID는 없다.
3. **판정자 가족 증거(REV-10).** 판정자 목록에 formal_check·identity_review·goal_audit가 아닌 판정자(다른 역할 이름이나 실행 ID)만 있는 의무를 판정자가 아닌 평가자가 fulfilled로 주장하면, 생산자 검사가 반려한다. 수신도 전에 `designated_judgment`로 같은 결과를 냈다.
4. **조치 해소 종류 제한(REV-08, ENG-17 b).** 계획·준비·운영 점검 문맥의 `blocked_actions`에서 실패가 아닌 대기가 빠진다. 계약 문서가 실패 아닌 대기를 이 목록에서 읽으라고 요구하는 곳이 있는지는 문서 단계가 확인한다(`ongoing_work`에는 전건이 있다).
5. **의도 해석 생산자 검사(STO-22).** 생산자 문맥에 `original_source`가 없으면 `validate_source`가 실패해 모든 해석이 반려된다. 엔진의 `_governance_context`는 넣는다(위임 판정 문맥은 interpret 단계가 아니다).
6. **입력 참조의 비저장(ENG-04).** `planning.task_ready`의 `tool:lean` 판정은 평가 문맥의 `lean_available`에 달렸다. 엔진 밖 호출자(`reporting`, `record_schemas`의 파생 가족)는 이 값이 없어 Lean을 설정하지 않은 호스트에서 `tool:lean` 입력을 누락으로 본다. 엔진 `_context`는 역할 입력마다 Lean 발견(초당 한 번)을 호출하므로 `available_input_refs`의 `tool:lean` 포함 여부가 시험 호스트에 따라 달라진다. 이 값을 정확히 비교하는 시험은 찾지 못했다.
7. **고정 입력 판독(ENG-08).** `engine._issued_input`은 `self.store.git_dir`를 직접 읽는다(엔진의 다른 호출과 같다). 이 속성이 없는 저장소 대역은 AttributeError를 낸다. 메모는 `git_dir`가 `os.PathLike`일 때만 쓰므로 시험 대역 사이에 오래된 값이 새지 않는다.
8. **오류 문구와 순서.** REV-01·RUN-19의 jsonschema 문구, REV-12의 검사 순서, REV-03의 다른 자리 기록 문구, REV-10의 수신 선행 문구가 바뀌었다. 정규식으로 옛 문구를 단언하던 시험은 찾아 고쳤지만, 실행으로 확인하지는 않았다. RUN-19의 repair 오류는 이제 "retry with replay_safety" 안내를 문구에 싣지 않고 스키마 `description`에만 싣는다.

## 5. 전제가 틀렸거나 계획을 바꾼 지점

### 5.1 다른 그룹 모듈을 고친 좌표

항목이 요구하는 줄만 바꿨다. 통합자는 아래 좌표에서 해당 그룹 브랜치와의 충돌을 확인한다.

| 모듈(소유 그룹) | 바꾼 곳 | 이유 |
|---|---|---|
| planning(D) | `capture_task_basis`의 비기록 참조 `available` 계산, `task_ready`의 입력 누락 판정 | ENG-04, ENG-02 |
| scheduler(A) | 소유 루프의 `available_input_refs` 저장 한 줄 삭제 | ENG-04 |
| lifecycle_engine(A) | `_run_external_action`의 덧붙이기 네 줄 삭제 | ENG-03 |
| record_schemas/__init__.py(B) | 질문 대상 허용 집합 | ENG-04 |
| record_schemas/domains.py(B) | `RESEARCH_FIELDS["available_input_refs"]` 삭제 | ENG-04 |
| context_store(B) | `_ROLE_DIRECT['research_plan']`, `configuration_source` 조건, `ongoing_work` 준비 실행 필드 | ENG-16(a), ENG-17(c) |
| governance_engine(A) | `_governance_context`의 deepcopy와 intent `config` 투영 삭제 | ENG-16(a)(f) |
| governance(F) | `validate_import_units(..., owner_kinds=None)` | STO-22 |
| preflight(B) | 스키마 수용 검사 목록에 `identity_review:scope` | REV-07 |

integration은 "제출 적용 부분"이 그룹 C 소유이고, `require_bundle_impact_review`의 입력 판독 한 줄만 바꿨다(ENG-08).

### 5.2 조사 파일과 원문이 달랐던 지점

- 좌표 이동: 조사 좌표는 `8d2ffd0` 기준이라 커널 병합 뒤 엔진 좌표가 약 40-50행 이동했다. 예를 들어 ENG-02의 적용 검사는 `engine.py:4082-4090`이 아니라 `_apply`의 준비 분기(병합 기준 4035행)였고, ENG-16·17의 `_context` 좌표도 같은 폭으로 이동했다. 내용은 조사와 같았다.
- ENG-04: 조사 제안은 "스키마 필드는 do-math-state/5 호환을 위해 선택 필드로 남긴다"였으나, 설계 1.2(호환 계층 없음)에 따라 필드를 지웠다. 조사가 적은 소비자 외에 `planning.capture_task_basis`(`{"available": ...}`)도 저장값을 읽고 있었다. 기반 값이 호스트에 따라 흔들리지 않게 설정 기준으로 계산했다.
- ENG-17(b): 두 선택지 가운데 "blocked_actions를 문서대로 실패 종류로 거른다"를 택했다. 이 거름이 REV-08의 종류 조건과 같은 상수(`RESOLVABLE_WAITS`)를 쓰므로 생산자가 해소 불가능한 대기를 보지 않게 된다.
- ENG-16(c): ENG-17(d)로 research_preparation이 `task_readiness`를 받지 않으므로, 준비의 `ready_task_ids`는 파생할 원천이 없다. 준비는 `planning.ready_task_ids`로 한 번 계산한다(전에는 2N회, 지금은 N회).
- REV-04: 보충 조사 실행의 독립성은 봉인 재구성(`validate_sealed_review`)이 쓰는 자리 모양 `{'role','research_request_id'}`로 실시간에도 검사한다. `validate_review_independence`는 같은 검토에 속한 조상 실행의 slot이 검사 대상 자리의 slot과 다르면 거부한다. 이 모양에는 slot이 없으므로, 같은 검토 안에서 slot을 가진 실행의 문맥을 이어받은 보충 조사(예: 보충 조사의 재개 실행)는 항상 slot이 다르다고 판정된다(없는 slot은 `None`으로 비교되므로 slot을 가진 조상과 같을 수 없다). 이런 실행은 전에도 봉인 재구성에서 거부되었고, 이제는 배정 시점에 거부된다.
- STO-22: 조사 제안대로 `validate_import_units`를 직접 부르려면 소유자 검사 훅(지식 후보 검증, `engine.validate_config`)을 생산자 보기에서 실행할 수 없었다. `owner_kinds` 키워드로 소유자 상태 검사만 수신에 남겼다.
- REV-14: 5절의 변형 범위와 남은 저장 스키마 강화는 1절 표에 적었다.

### 5.3 스키마 키워드의 CLI 수용 위험(REV-01·07·15)

모델에 새로 전달하는 키워드는 `pattern`(검토 문자열과 `repair_target`), `const`(`policy_version`), `anyOf`+`{"type":"null"}`(`selected_profile_ref`), `enum`(`item_id`), `minItems`·`maxItems`(`item_reviews`, `initial_slots`, `required_source_refs`)다. 모두 지금도 모델에 전달되는 스키마가 쓰는 키워드다: `contracts.TEXT`의 `pattern`, `ITEM_DISPOSITION`의 `anyOf`와 `const`, `disposition_schema`의 `anyOf`+`null`, preparation의 `candidates.maxItems`. Claude CLI가 거부한 전례는 최상위 `$schema`와 `x-contract-id`였고(L-0020), 이번 변경은 최상위 키를 더하지 않는다. `preflight._check_schema_pair`는 Draft 2020-12와 Draft 7 메타스키마 적합성만 확인하므로 공급자의 실제 수용은 보장하지 않는다. 위험은 둘이다. 하나는 Codex 엄격 모드에서 `anyOf` 안의 `null` 분기가 `required`와 함께 쓰일 때의 동작으로, `disposition_schema`의 `next_review`와 같은 모양이라 이미 운전 중인 형태다. 다른 하나는 정규식 `\S`와 `^installation:`인데, 같은 `\S`가 이미 전달되고 있다. 첫 실제 실행에서 scope 단계와 계약 검토 역할의 스키마 거부 여부를 확인하는 것이 남은 검증이다.
